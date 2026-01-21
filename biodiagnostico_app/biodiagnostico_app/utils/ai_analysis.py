"""
AI Analysis utilities using OpenAI
Laboratório Biodiagnóstico
FORENSIC AUDIT ENGINE v3.0 - Structured Report Generation
"""
from datetime import datetime
import openai
import csv
import io
import asyncio
import math
import re
from typing import Optional, Tuple, Dict, List, Any, Callable


def normalize_patient_name(name: str) -> str:
    """Normaliza nome do paciente para matching"""
    import unicodedata
    if not name:
        return ""
    # Remove acentos
    name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('ASCII')
    # Uppercase e remove espaços extras
    name = ' '.join(name.upper().strip().split())
    return name


def calculate_local_totals(patients_dict: dict) -> Tuple[float, int, int]:
    """Calcula totais localmente para validação"""
    total_value = 0.0
    total_exams = 0
    total_patients = len(patients_dict)
    
    for patient, patient_data in patients_dict.items():
        if isinstance(patient_data, dict) and 'exams' in patient_data:
            exams = patient_data['exams']
        elif isinstance(patient_data, list):
            exams = patient_data
        else:
            exams = []
        
        for exam in exams:
            try:
                val = float(exam.get('value', 0) or 0)
                total_value += val
                total_exams += 1
            except (ValueError, TypeError):
                pass
    
    return total_value, total_exams, total_patients



def identify_discrepancies_locally(compulab_patients: dict, simus_patients: dict) -> Dict[str, Any]:
    """
    Identifica discrepâncias usando o motor robusto de comparação (comparison.py).
    Garante consistência total com o Dashboard.
    """
    from .comparison import run_complete_analysis
    
    # Executar análise robusta
    report = run_complete_analysis(compulab_patients, simus_patients)
    
    # Converter para o formato esperado pelo relatório de IA
    result = {
        "pacientes_ausentes_simus": [
            {"nome": p.name, "valor_total": p.total_value, "qtd_exames": p.total_exams}
            for p in report.missing_patients
        ],
        "pacientes_ausentes_compulab": [
             # Pacientes extras no SIMUS (que geraram exames extras)
             # ExtraSimusExam já captura isso, mas aqui a estrutura antiga pedia lista de pacientes
             # Vamos reconstruir simplificado ou deixar vazio se não for crítico, 
             # mas o relatório usa isso.
             # O report v2 tem extra_simus_exams, mas não lista de pacientes extras isolada.
             # Vamos extrair dos extra_simus_exams agrupando.
        ],
        "exames_ausentes_simus": [
            {"paciente": e.patient, "exame": e.exam_name, "valor": e.value}
            for e in report.missing_exams
        ],
        "exames_ausentes_compulab": [
            {"paciente": e.patient, "exame": e.exam_name, "valor": e.simus_value}
            for e in report.extra_simus_exams
        ],
        "divergencias_valor": [
            {
                "paciente": v.patient, 
                "exame": v.exam_name, 
                "valor_compulab": v.compulab_value, 
                "valor_simus": v.simus_value, 
                "diferenca": v.difference
            }
            for v in report.value_divergences
        ],
        "totais": {
            "compulab_total": report.compulab_total,
            "simus_total": report.simus_total,
            "impacto_pacientes": report.impact_missing_patients,
            "impacto_exames": report.impact_missing_exams,
            "impacto_divergencias": report.impact_value_divergences,
        }
    }
    
    # Reconstruir lista de pacientes extras no SIMUS (apenas para manter compatibilidade)
    # Agrupar report.extra_simus_exams por paciente
    extra_patients = {}
    for extra in report.extra_simus_exams:
        if extra.patient not in extra_patients:
            extra_patients[extra.patient] = {"nome": extra.patient, "valor_total": 0.0, "qtd_exames": 0}
        extra_patients[extra.patient]["valor_total"] += extra.simus_value
        extra_patients[extra.patient]["qtd_exames"] += 1
        
    result["pacientes_ausentes_compulab"] = list(extra_patients.values())
    
    return result


def chunk_data(data_dict, chunk_size=50):
    """Agrupa dados em chunks de N pacientes"""
    items = list(data_dict.items())
    for i in range(0, len(items), chunk_size):
        yield dict(items[i:i + chunk_size])


def format_dataset_for_prompt(patients_dict):
    """Formata dataset para o prompt (CSV style)"""
    output = "Paciente,Nome_Exame,Codigo_Exame,Valor\n"
    for patient, patient_data in patients_dict.items():
        if isinstance(patient_data, dict) and 'exams' in patient_data:
            exams = patient_data['exams']
        elif isinstance(patient_data, list):
            exams = patient_data
        else:
            exams = []

        for exam in exams:
            exam_name = str(exam.get('exam_name', '')).upper().replace(',', '').strip()
            exam_code = str(exam.get('code', '')).strip()
            if not exam_code:
                 exam_code = str(exam.get('exam_code', exam_name)).strip()
            
            try:
                val = float(exam.get('value', 0))
                val_str = f"{val:.2f}".replace('.', ',')
            except:
                val_str = "0,00"
            
            output += f"{patient.upper()},{exam_name},{exam_code},{val_str}\n"
    return output


def format_currency_br(value: float) -> str:
    """Formata valor como moeda brasileira"""
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


async def process_batch(client, system_prompt, chunk_patients, compulab_patients, simus_patients, batch_id, total_batches, progress_callback=None, retries=3):
    """Processa um único batch (async) com retry e backoff exponencial"""
    for attempt in range(retries + 1):
        try:
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

Analyze this batch now and output ONLY the CSV lines."""

            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_msg}
                ],
                temperature=0.0,
                timeout=60.0
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse robusto
            rows = []
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if not line or line.startswith('---'): continue
                if "```" in line: continue
                if "tipo_divergencia" in line.lower() or "causa_raiz" in line.lower():
                    continue
                
                if line.count(';') >= 5:
                    rows.append(line)
                elif line.count(',') >= 5 and ';' not in line:
                    line = line.replace(',', ';')
                    rows.append(line)
                    
            return rows, None
            
        except Exception as e:
            error_msg = str(e)
            is_rate_limit = "rate_limit" in error_msg.lower() or "429" in error_msg
            
            if attempt < retries:
                wait_time = (2 ** attempt) * 5 + 5
                if is_rate_limit:
                    wait_time += 15
                
                if progress_callback:
                    await progress_callback(f"Lote {batch_id} falhou ({attempt+1}/{retries}). Tentando em {wait_time}s...")
                
                await asyncio.sleep(wait_time)
            else:
                return [], f"Batch {batch_id} falhou após {retries} tentativas: {error_msg}"
    
    return [], "Erro desconhecido"


async def generate_ai_analysis(
    compulab_patients: dict,
    simus_patients: dict,
    api_key: str
):
    """
    Executa a auditoria de IA com estratégia de Chunking Paralelo e Parsing Robusto.
    Gera relatório no formato FORENSE ESTRUTURADO.
    Yields (percentage, status_message) e finally returns (analysis_result, error)
    """
    try:
        yield 0, "Iniciando Auditoria Forense Digital..."
        await asyncio.sleep(0.1)

        if not api_key:
            yield 100, "Erro de Configuração"
            yield "", "API Key não fornecida."
            return
        
        # ===== FASE 1: CÁLCULO LOCAL (Validação) =====
        yield 2, "Calculando totais locais para validação..."
        
        local_discrepancies = identify_discrepancies_locally(compulab_patients, simus_patients)
        totais = local_discrepancies["totais"]
        
        compulab_total = totais["compulab_total"]
        simus_total = totais["simus_total"]
        gap_financeiro = compulab_total - simus_total
        
        yield 5, f"Gap identificado: {format_currency_br(gap_financeiro)}"
        
        client = openai.AsyncOpenAI(api_key=api_key)
        
        # ===== FASE 2: AUDITORIA IA PROFUNDA =====
        # System Prompt FORENSE (v3.0)
        system_prompt = """
# ROLE
Você é um Engenheiro de Dados Sênior e Auditor Forense Digital, especialista em sistemas de saúde e conciliação financeira para fins judiciais.

# CONTEXTO
Estamos auditando o Laboratório Biodiagnóstico. O sistema interno (COMPULAB) registra valores a receber superiores aos pagos pelo SUS (SIMUS). Precisamos provar a origem dessa diferença para uso em processo judicial.

# LÓGICA DE PROCESSAMENTO
1. NORMALIZAÇÃO: Padronize nomes de pacientes (ignore acentos, maiúsculas) e códigos de exames.
2. MATCHING: Cruze por NOME DO PACIENTE + NOME/CÓDIGO DO EXAME.
3. PRECISÃO: Ignore diferenças < R$ 0,10.

# CATEGORIAS DE DISCREPÂNCIA (USE EXATAMENTE)
- "Paciente Ausente": Paciente no COMPULAB mas não existe no SIMUS.
- "Exame Ausente": Paciente existe em ambos, mas exame específico só está no COMPULAB.
- "Divergência de Valor": Paciente e exame existem em ambos, mas valor COMPULAB > SIMUS.
- "Exame Fantasma": Exame no SIMUS mas não no COMPULAB (possível fraude).

# OUTPUT FORMAT (STRICT CSV)
- Separator: Semicolon (;)
- Columns: Paciente;Nome_Exame;Codigo_Exame;Valor_Compulab;Valor_Simus;Categoria;Causa_Raiz
- NO Header, NO Markdown, NO conversational text, NO code blocks. 
- Output ONLY the data lines.
- 'Causa_Raiz' deve ser técnica e judicial: ex: "Falha de integração SIMUS", "Tabela SIGTAP desatualizada", "Erro de digitação", "Duplicidade suspeita".
"""

        all_csv_rows = []
        all_patients = sorted(list(set(list(compulab_patients.keys()) + list(simus_patients.keys()))))
        
        chunk_size = 15
        total_patients = len(all_patients)
        batches = [all_patients[i:i + chunk_size] for i in range(0, total_patients, chunk_size)]
        total_batches = len(batches)
        completed_batches = 0
        
        yield 8, f"Processando {total_batches} lotes de análise IA..."
        
        sem = asyncio.Semaphore(2)
        batch_errors = []
        
        async def sem_process_batch(batch_idx, chunk):
            async with sem:
                res, error = await process_batch(
                    client, system_prompt, chunk, compulab_patients, simus_patients, 
                    batch_idx+1, total_batches, progress_callback=None
                )
                if error:
                    batch_errors.append(error)
                return res

        tasks = [asyncio.create_task(sem_process_batch(i, batch)) for i, batch in enumerate(batches)]
        
        pending = list(tasks)
        while pending:
            done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)
            for task in done:
                res = await task
                all_csv_rows.extend(res)
                completed_batches += 1
                progress = 8 + int((completed_batches / total_batches) * 85)
                
                status_msg = f"Lote {completed_batches}/{total_batches} concluído"
                if batch_errors:
                    status_msg += f" ({len(batch_errors)} erros)"
                
                yield progress, status_msg
                
        yield 95, "Consolidando Relatório Forense..."
        
        if len(batch_errors) == total_batches:
             yield 100, "Erro"
             yield "", f"Todos os lotes de auditoria falharam: {batch_errors[0]}"
             return
             
        try:
             all_csv_rows.sort(key=lambda x: x.split(';')[0] if ';' in x else x)
        except:
             pass

        # ===== FASE 3: GERAR RELATÓRIO ESTRUTURADO =====
        
        # Contagens por categoria
        cat_paciente_ausente = [r for r in all_csv_rows if "Paciente Ausente" in r]
        cat_exame_ausente = [r for r in all_csv_rows if "Exame Ausente" in r]
        cat_divergencia = [r for r in all_csv_rows if "Divergência de Valor" in r]
        cat_fantasma = [r for r in all_csv_rows if "Exame Fantasma" in r or "Fantasma" in r]
        
        # Gerar listas formatadas
        def format_list(items, max_items=10):
            if not items:
                return "Nenhum caso identificado."
            output = ""
            for i, item in enumerate(items[:max_items]):
                parts = item.split(';')
                if len(parts) >= 5:
                    paciente = parts[0]
                    exame = parts[1]
                    val_c = parts[3]
                    val_s = parts[4]
                    output += f"   - {paciente} | {exame} | COMPULAB: R$ {val_c} | SIMUS: R$ {val_s}\n"
            if len(items) > max_items:
                output += f"   ... e mais {len(items) - max_items} casos.\n"
            return output if output else "Nenhum caso identificado."
        
        lista_pacientes_ausentes = format_list(cat_paciente_ausente)
        lista_exames_ausentes = format_list(cat_exame_ausente)
        lista_divergencias = format_list(cat_divergencia)
        lista_fantasmas = format_list(cat_fantasma)
        
        # Impactos calculados localmente (mais confiável)
        impacto_pacientes = totais["impacto_pacientes"]
        impacto_exames = totais["impacto_exames"]
        impacto_divergencias = totais["impacto_divergencias"]
        
        csv_header = "Paciente;Nome_Exame;Codigo_Exame;Valor_Compulab;Valor_Simus;Categoria;Causa_Raiz"
        csv_content = "\n".join(all_csv_rows) if all_csv_rows else "Nenhuma divergência encontrada."
        
        error_notice = ""
        if batch_errors:
            error_notice = f"\n> ⚠️ **Atenção:** {len(batch_errors)} lotes falharam durante o processamento. Os resultados podem estar incompletos.\n"
        
        final_report = f"""# RELATÓRIO DE AUDITORIA FORENSE - BIODIAGNÓSTICO
**Gerado em:** {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}
**Versão do Engine:** Forensic Audit v3.0
{error_notice}
---

## 1. ANÁLISE RESUMIDA

Foi realizada uma auditoria completa comparando os registros do sistema interno COMPULAB (exames realizados) com o sistema de faturamento SUS SIMUS (exames cobrados). A análise identificou um gap financeiro de **{format_currency_br(gap_financeiro)}**, distribuído entre pacientes não faturados, exames omitidos e divergências de tabela de preços.

---

## 2. RESUMO EXECUTIVO (DASHBOARD FINANCEIRO)

| Métrica | Valor |
|---------|-------|
| **Valor Total COMPULAB** | {format_currency_br(compulab_total)} |
| **Valor Total SIMUS** | {format_currency_br(simus_total)} |
| **Diferença (Gap Financeiro)** | **{format_currency_br(gap_financeiro)}** |
| Pacientes Analisados (COMPULAB) | {len(compulab_patients)} |
| Pacientes Analisados (SIMUS) | {len(simus_patients)} |
| Total de Divergências Identificadas | {len(all_csv_rows)} |

---

## 3. DIAGNÓSTICO DA DIFERENÇA (CAUSA RAIZ)

### 3.1. Impacto por PACIENTES AUSENTES no SIMUS
**Quantidade:** {len(local_discrepancies['pacientes_ausentes_simus'])} pacientes
**Impacto Financeiro:** {format_currency_br(impacto_pacientes)}

{lista_pacientes_ausentes}

### 3.2. Impacto por EXAMES NÃO COMPUTADOS no SIMUS
**Quantidade:** {len(local_discrepancies['exames_ausentes_simus'])} exames
**Impacto Financeiro:** {format_currency_br(impacto_exames)}

{lista_exames_ausentes}

### 3.3. Impacto por DIVERGÊNCIA DE TABELA/VALOR
**Quantidade:** {len(local_discrepancies['divergencias_valor'])} casos
**Impacto Financeiro:** {format_currency_br(impacto_divergencias)}

{lista_divergencias}

### 3.4. EXAMES FANTASMA (Alerta de Risco)
**Quantidade:** {len(local_discrepancies['exames_ausentes_compulab'])} exames no SIMUS sem correspondência no COMPULAB

{lista_fantasmas}

---

## 4. DADOS DETALHADOS (CSV)

```csv
{csv_header}
{csv_content}
```

---

## 5. CONCLUSÃO TÉCNICA

Com base nos dados analisados, a diferença de **{format_currency_br(gap_financeiro)}** entre COMPULAB e SIMUS pode ser explicada por:

1. **Falha de Integração:** Exames realizados não foram transmitidos ao sistema de faturamento.
2. **Tabela Desatualizada:** O SIMUS utiliza valores inferiores aos praticados pelo laboratório.
3. **Erro Operacional:** Pacientes ou exames não foram cadastrados corretamente no SIMUS.

**Recomendação:** Revisar o processo de integração COMPULAB→SIMUS e atualizar a tabela de preços SIGTAP/CBHPM.

---

*Este relatório foi gerado automaticamente pelo Forensic Audit Engine v3.0 - Biodiagnóstico.*
*Para uso em processos judiciais, os dados originais devem ser preservados como prova digital.*
"""
        
        yield 100, "Auditoria Forense Concluída"
        yield final_report, ""
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        yield 100, "Erro"
        yield "", f"Erro na Auditoria IA: {str(e)}"


def format_ai_report(ai_analysis: str) -> str:
    return ai_analysis

