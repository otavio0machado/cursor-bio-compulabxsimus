"""
AI Analysis utilities using OpenAI
Laboratório Biodiagnóstico
AI Auditor Implementation (Async Parallel Optimized + Enhanced)
"""
from datetime import datetime
import openai
import csv
import io
import asyncio
import math
import time
from typing import Dict, List, Tuple, Any

def chunk_data(data_dict, chunk_size=50):
    """Agrupa dados em chunks de N pacientes"""
    items = list(data_dict.items())
    for i in range(0, len(items), chunk_size):
        yield dict(items[i:i + chunk_size])

def format_dataset_for_prompt(patients_dict):
    """Formata dataset para o prompt (CSV style) com validação"""
    output = "Paciente;Nome_Exame;Codigo_Exame;Valor\n"

    if not patients_dict:
        return output

    for patient, patient_data in patients_dict.items():
        # Adaptar para a estrutura do pdf_processor: {'exams': [], 'total': ...}
        if isinstance(patient_data, dict) and 'exams' in patient_data:
            exams = patient_data['exams']
        elif isinstance(patient_data, list):
            exams = patient_data
        else:
            exams = [] # Fallback

        for exam in exams:
            # Estrutura esperada: dict com keys 'exam_name', 'value', etc.
            exam_name = exam.get('exam_name', '').upper().replace(';', '').replace(',', '').strip()
            if not exam_name:
                exam_name = "EXAME_NAO_IDENTIFICADO"

            exam_code = exam.get('code', '') # pdf_processor usa 'code'
            if not exam_code:
                exam_code = exam.get('exam_code', '')
            exam_code = str(exam_code).strip()

            try:
                val = f"{float(exam.get('value', 0)):.2f}".replace('.', ',')
            except (ValueError, TypeError):
                val = "0,00"

            output += f"{patient.upper()};{exam_name};{exam_code};{val}\n"

    return output


async def retry_with_backoff(func, max_retries: int = 3, initial_delay: float = 1.0):
    """Retry com exponential backoff para chamadas de API"""
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise

            delay = initial_delay * (2 ** attempt)
            print(f"Tentativa {attempt + 1} falhou: {e}. Retry em {delay}s...")
            await asyncio.sleep(delay)

async def process_batch(client, system_prompt, chunk_patients, compulab_patients, simus_patients, batch_id, total_batches):
    """Processa um único batch (async) com retry logic"""
    async def _api_call():
        # Filtrar dados para este chunk
        chunk_compulab = {k: compulab_patients[k] for k in chunk_patients if k in compulab_patients}
        chunk_simus = {k: simus_patients[k] for k in chunk_patients if k in simus_patients}

        # Formatar CSVs
        csv_compulab = format_dataset_for_prompt(chunk_compulab)
        csv_simus = format_dataset_for_prompt(chunk_simus)

        user_msg = f"""DATASET A (COMPULAB):
\"\"\"
{csv_compulab}
\"\"\"

DATASET B (SIMUS):
\"\"\"
{csv_simus}
\"\"\"

Analise este lote agora e retorne APENAS as divergências no formato CSV especificado."""

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg}
            ],
            temperature=0.0,
            top_p=0.1,
            max_tokens=4000
        )

        return response.choices[0].message.content.strip()

    try:
        # Usar retry com backoff
        content = await retry_with_backoff(_api_call, max_retries=3, initial_delay=1.0)

        # Parse output com validação
        rows = []
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # Skip headers e markdown
            if "Paciente;Nome" in line or "Paciente,Nome" in line:
                continue
            if line.startswith("```") or line.startswith("#"):
                continue
            # Verificar se tem pelo menos 5 campos (formato esperado tem 6)
            if line.count(';') >= 4:
                rows.append(line)

        return rows

    except Exception as e:
        print(f"❌ Erro no batch {batch_id}/{total_batches}: {str(e)}")
        return []

async def generate_ai_analysis(
    compulab_patients: dict,
    simus_patients: dict,
    api_key: str
):
    """
    Executa a auditoria de IA com estratégia de Chunking Paralelo.
    Yields (percentage, status_message) e finally returns (analysis_result, error)
    """
    try:
        yield 0, "Iniciando IA Auditor..."
        await asyncio.sleep(0.1)

        if not api_key:
            yield 100, "Erro de Configuração" # Fim do stream de progresso
            yield "", "API Key não fornecida." # Resultado final
            return
            
        client = openai.AsyncOpenAI(api_key=api_key)
        
        # System Prompt do Auditor (Enhanced)
        system_prompt = """# PAPEL
Você é um Auditor de Dados Médico-Laboratoriais de Alta Precisão especializado em análise comparativa de sistemas de faturamento hospitalar (COMPULAB vs SIMUS).

# OBJETIVO
Identificar e reportar EXCLUSIVAMENTE divergências entre dois datasets de faturamento laboratorial.

# ESTRUTURA DE ENTRADA
Você receberá dados em formato CSV com delimitador ponto-e-vírgula (;) contendo as colunas:
- Paciente: Nome do paciente
- Nome_Exame: Nome do procedimento laboratorial
- Codigo_Exame: Código identificador do exame
- Valor: Valor monetário em formato brasileiro (vírgula decimal)

# REGRAS DE ANÁLISE RIGOROSAS

## 1. NORMALIZAÇÃO DE DADOS
- Todos os nomes de pacientes devem ser tratados em MAIÚSCULAS e sem espaços extras
- Códigos de exame vazios devem usar Nome_Exame como chave alternativa
- Valores decimais: tratar vírgula (,) e ponto (.) como equivalentes

## 2. CHAVE DE COMPARAÇÃO
A chave única para comparação é a COMBINAÇÃO:
```
[Nome_Paciente_Normalizado] + [Codigo_Exame OU Nome_Exame]
```

## 3. TOLERÂNCIA DECIMAL
- Diferenças ≤ R$ 0,01 devem ser IGNORADAS (consideradas iguais)
- Diferenças > R$ 0,01 devem ser reportadas como "Valor Divergente"

## 4. TIPOS DE DIVERGÊNCIA (EXATOS)

### A) Paciente Ausente no SIMUS
- Condição: Paciente existe no COMPULAB mas NÃO existe no SIMUS
- Formato: Listar TODOS os exames deste paciente
- Valor_Simus: deixar vazio ou "0,00"
- Tipo_Divergencia: "Exame Ausente no SIMUS"

### B) Paciente Ausente no COMPULAB
- Condição: Paciente existe no SIMUS mas NÃO existe no COMPULAB
- Formato: Listar TODOS os exames deste paciente
- Valor_Compulab: deixar vazio ou "0,00"
- Tipo_Divergencia: "Exame Ausente no COMPULAB"

### C) Exame Extra no COMPULAB
- Condição: Paciente existe em ambos, mas exame específico só existe no COMPULAB
- Valor_Simus: "0,00"
- Tipo_Divergencia: "Exame Ausente no SIMUS"

### D) Exame Extra no SIMUS
- Condição: Paciente existe em ambos, mas exame específico só existe no SIMUS
- Valor_Compulab: "0,00"
- Tipo_Divergencia: "Exame Ausente no COMPULAB"

### E) Divergência de Valor
- Condição: Paciente e Exame existem em ambos, mas valores divergem > R$ 0,01
- Formato: Mostrar ambos os valores
- Tipo_Divergencia: "Valor Divergente"

# FORMATO DE SAÍDA (ESTRITAMENTE CSV)

## IMPORTANTE:
- NÃO inclua texto explicativo, comentários ou markdown
- NÃO inclua cabeçalho se não houver divergências
- Use delimitador ponto-e-vírgula (;)
- Se valores são iguais (diferença ≤ 0,01), NÃO reportar (silêncio total)

## ESTRUTURA DA LINHA:
```
Paciente;Nome_Exame;Codigo_Exame;Valor_Compulab;Valor_Simus;Tipo_Divergencia
```

## EXEMPLOS VÁLIDOS:
```
JOAO SILVA;HEMOGRAMA COMPLETO;202010689;45,00;0,00;Exame Ausente no SIMUS
MARIA SANTOS;GLICOSE;202020380;12,50;12,80;Valor Divergente
ANA COSTA;UREIA;202030456;0,00;8,90;Exame Ausente no COMPULAB
```

# REGRAS DE ORDENAÇÃO
- Ordenar alfabeticamente por Nome do Paciente
- Em caso de empate, ordenar por Nome do Exame

# VALIDAÇÃO DE QUALIDADE
Antes de retornar, verifique:
✓ Todas as linhas têm exatamente 6 campos separados por ;
✓ Nenhuma linha tem valores idênticos (diferença ≤ 0,01)
✓ Tipo_Divergencia é uma das 3 opções válidas
✓ Valores monetários usam vírgula como decimal (ex: 12,50)
✓ Não há linhas vazias ou com dados faltando

# OUTPUT FINAL
Retorne APENAS as linhas CSV de divergências, uma por linha, sem cabeçalho se não houver dados."""

        all_csv_rows = []
        
        # List of patients from both sets to handle chunking correctly
        all_patients = sorted(list(set(list(compulab_patients.keys()) + list(simus_patients.keys()))))
        
        chunk_size = 20
        total_patients = len(all_patients)
        
        # Criar batches
        batches = []
        for i in range(0, total_patients, chunk_size):
            chunk = all_patients[i:i + chunk_size]
            batches.append(chunk)

        total_batches = len(batches)
        completed_batches = 0
        
        yield 5, f"Preparando {total_batches} lotes de análise..."
        
        # Controlar concorrência
        sem = asyncio.Semaphore(10) # 10 requests simultâneos
        
        async def sem_process_batch(batch_idx, chunk):
            async with sem:
                res = await process_batch(client, system_prompt, chunk, compulab_patients, simus_patients, batch_idx+1, total_batches)
                return res

        # Criar tasks explicitamente
        tasks = [asyncio.create_task(sem_process_batch(i, batch)) for i, batch in enumerate(batches)]
        
        # Executar e monitorar progresso
        pending = list(tasks)
        while pending:
            # Esperar o primeiro completar
            done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)
            
            for task in done:
                res = await task
                all_csv_rows.extend(res)
                completed_batches += 1
                
                # Calcular progresso (5% a 95%)
                progress = 5 + int((completed_batches / total_batches) * 90)
                yield progress, f"Analisando lote {completed_batches}/{total_batches} ({progress}%)"
                
        # Aggregate and analyze results
        yield 98, "Consolidando e analisando resultados..."

        # Sort rows by Patient Name (first column)
        try:
            all_csv_rows.sort(key=lambda x: x.split(';')[0] if ';' in x else x)
        except Exception as e:
            print(f"Erro ao ordenar resultados: {e}")

        # Calcular estatísticas
        total_divergences = len(all_csv_rows)

        stats = {
            "ausente_simus": 0,
            "ausente_compulab": 0,
            "valor_divergente": 0,
            "pacientes_com_divergencia": set(),
            "valor_total_divergencias": 0.0
        }

        for row in all_csv_rows:
            try:
                parts = row.split(';')
                if len(parts) >= 6:
                    paciente = parts[0]
                    val_compulab = parts[3].replace(',', '.')
                    val_simus = parts[4].replace(',', '.')
                    tipo = parts[5]

                    stats["pacientes_com_divergencia"].add(paciente)

                    if "Ausente no SIMUS" in tipo or "Ausente no Simus" in tipo:
                        stats["ausente_simus"] += 1
                    elif "Ausente no COMPULAB" in tipo or "Ausente no Compulab" in tipo:
                        stats["ausente_compulab"] += 1
                    elif "Divergente" in tipo:
                        stats["valor_divergente"] += 1

                    # Calcular diferença monetária
                    try:
                        v_comp = float(val_compulab) if val_compulab else 0.0
                        v_simus = float(val_simus) if val_simus else 0.0
                        diff = abs(v_comp - v_simus)
                        stats["valor_total_divergencias"] += diff
                    except (ValueError, TypeError):
                        pass
            except Exception as e:
                print(f"Erro ao processar linha para estatísticas: {e}")

        pacientes_unicos = len(stats["pacientes_com_divergencia"])

        final_csv = "Paciente;Nome_Exame;Codigo_Exame;Valor_Compulab;Valor_Simus;Tipo_Divergencia\n" + "\n".join(all_csv_rows)

        # Formatar valor total com vírgula brasileira
        valor_formatado = f"R$ {stats['valor_total_divergencias']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

        final_report = f"""# 🔍 RELATÓRIO DE AUDITORIA DE IA - ANÁLISE COMPARATIVA

---

## 📊 INFORMAÇÕES GERAIS

**Data da Análise:** {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}
**Total de Divergências Encontradas:** {total_divergences}
**Pacientes Afetados:** {pacientes_unicos}
**Impacto Financeiro Total:** {valor_formatado}

---

## 📈 ESTATÍSTICAS POR TIPO

| Tipo de Divergência | Quantidade | Percentual |
|---------------------|------------|------------|
| 🔴 Exames Ausentes no SIMUS | {stats['ausente_simus']} | {(stats['ausente_simus']/total_divergences*100) if total_divergences > 0 else 0:.1f}% |
| 🔵 Exames Ausentes no COMPULAB | {stats['ausente_compulab']} | {(stats['ausente_compulab']/total_divergences*100) if total_divergences > 0 else 0:.1f}% |
| 🟡 Divergências de Valor | {stats['valor_divergente']} | {(stats['valor_divergente']/total_divergences*100) if total_divergences > 0 else 0:.1f}% |

---

## 📋 DETALHES DAS DIVERGÊNCIAS (CSV)

```csv
{final_csv}```

---

## ℹ️ INFORMAÇÕES TÉCNICAS

**Modelo de IA:** GPT-4o Mini (OpenAI)
**Método de Análise:** Processamento em lotes paralelos assíncronos
**Total de Lotes Processados:** {total_batches}
**Tolerância Decimal:** ± R$ 0,01

---

*Este relatório foi gerado automaticamente pelo sistema de Auditoria IA do Biodiagnóstico.*
*Para dúvidas ou suporte técnico, contate o administrador do sistema.*
"""

        yield 100, "✅ Análise concluída com sucesso!"
        yield final_report, "" # Retorno final (analysis, error)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        yield 100, "Erro"
        yield "", f"Erro na Auditoria IA: {str(e)}"

def format_ai_report(ai_analysis: str) -> str:
    """Formata o relatório da IA para download"""
    return ai_analysis
