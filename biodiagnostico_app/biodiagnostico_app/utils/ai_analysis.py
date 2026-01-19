"""
AI Analysis utilities using OpenAI
Laboratório Biodiagnóstico
AI Auditor Implementation (Async Parallel Optimized)
"""
from datetime import datetime
import openai
import csv
import io
import asyncio
import math

def chunk_data(data_dict, chunk_size=50):
    """Agrupa dados em chunks de N pacientes"""
    items = list(data_dict.items())
    for i in range(0, len(items), chunk_size):
        yield dict(items[i:i + chunk_size])

def format_dataset_for_prompt(patients_dict):
    """Formata dataset para o prompt (CSV style)"""
    output = "Paciente,Nome_Exame,Codigo_Exame,Valor\n"
    for patient, patient_data in patients_dict.items():
        # Adaptar para a estrutura do pdf_processor: {'exams': [], 'total': ...}
        if isinstance(patient_data, dict) and 'exams' in patient_data:
            exams = patient_data['exams']
        elif isinstance(patient_data, list):
            exams = patient_data
        else:
            exams = [] # Fallback

        for exam in exams:
            # Assumindo estrutura dos exames. Ajustar conforme necessário baseando-se no objeto real
            # Estrutura esperada: dict com keys 'exam_name', 'value', etc.
            # Se 'exam_code' não existir, usar 'exam_name' como código também ou vazio
            exam_name = exam.get('exam_name', '').upper().replace(',', '')
            exam_code = exam.get('code', '') # pdf_processor usa 'code'
            if not exam_code:
                 exam_code = exam.get('exam_code', exam_name)
            
            val = f"{float(exam.get('value', 0)):.2f}".replace('.', ',')
            
            output += f"{patient.upper()},{exam_name},{exam_code},{val}\n"
    return output

async def process_batch(client, system_prompt, chunk_patients, compulab_patients, simus_patients, batch_id, total_batches):
    """Processa um único batch (async)"""
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

Analyze this batch now."""

        response = await client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg}
            ],
            temperature=0.0,
            top_p=0.1
        )
        
        content = response.choices[0].message.content.strip()
        
        # Parse output
        rows = []
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line: continue
            if "Paciente;Nome" in line: continue # Skip header
            if line.startswith("```"): continue # Skip markdown code blocks
            rows.append(line)
            
        return rows
        
    except Exception as e:
        print(f"Erro no batch {batch_id}: {e}")
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
        
        # System Prompt do Auditor (OTIMIZADO)
        system_prompt = """
# ROLE
You are a Senior Medical Audit Algorithm. Your task is to compare two datasets: 
- **Dataset A (COMPULAB - Provider)**
- **Dataset B (SIMUS - Payer)**

# OBJECTIVE
Identify FINANCIAL DISCREPANCIES where the Provider (Compulab) is billing differently from what the Payer (Simus) recorded.

# INPUT FORMAT
You receive data as: "PATIENT,EXAM_NAME,CODE,VALUE"

# LOGIC RULES
1. **Match Key:** Match items by `PATIENT` (Case insensitive) + `CODE` (or `EXAM_NAME` if code is generic).
2. **Value Parsing:** Treat "1.234,56" and "1234.56" as identical numbers.
3. **Tolerance:** Ignore differences <= 0.02 (cents).
4. **Validation:** - If a patient exists in A but not B -> Missing in Simus.
   - If a specific exam code exists in A but not B (for the same patient) -> Exam Missing in Simus.
   - If values differ > 0.02 -> Value Divergence.

# OUTPUT FORMAT (STRICT CSV)
- **Separator:** Semicolon (;) 
- **Decimal Separator:** Comma (,) for display (e.g. 24,50).
- **Columns:** Paciente;Nome_Exame;Codigo_Exame;Valor_Compulab;Valor_Simus;Tipo_Divergencia
- **No Markdown:** Do not use code blocks (```). Just raw text lines.
- **Header:** Do NOT output the header row.

# DISCREPANCY TYPES (Use EXACTLY these terms)
- "Paciente Ausente no SIMUS"
- "Paciente Ausente no COMPULAB"
- "Exame Ausente no SIMUS"
- "Exame Ausente no COMPULAB"
- "Valor Divergente"

# EXAMPLE OUTPUT ROW
SILVA JOAO;HEMOGRAMA;02020101;25,00;0,00;Exame Ausente no SIMUS
MARIA JOSE;GLICOSE;02020104;10,50;9,50;Valor Divergente

# INSTRUCTIONS
Analyze the provided batch and output ONLY the discrepancies found using the format above. If no discrepancies, output nothing.
"""

        all_csv_rows = []
        
        # List of patients from both sets to handle chunking correctly
        all_patients = sorted(list(set(list(compulab_patients.keys()) + list(simus_patients.keys()))))
        
        # DEBUG: Contar total de dados
        total_compulab_exams = sum(len(p.get('exams', [])) if isinstance(p, dict) else len(p) for p in compulab_patients.values())
        total_simus_exams = sum(len(p.get('exams', [])) if isinstance(p, dict) else len(p) for p in simus_patients.values())
        print(f"DEBUG AI: {len(compulab_patients)} pacientes COMPULAB ({total_compulab_exams} exames)")
        print(f"DEBUG AI: {len(simus_patients)} pacientes SIMUS ({total_simus_exams} exames)")
        print(f"DEBUG AI: Total combinado: {len(all_patients)} pacientes únicos")
        
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
                
        # Aggregate results
        yield 98, "Consolidando resultados..."
        
        # Sort rows by Patient Name (first column)
        # Assuming format "Paciente;..."
        try:
             all_csv_rows.sort(key=lambda x: x.split(';')[0] if ';' in x else x)
        except:
             pass

        final_csv = "Paciente;Nome_Exame;Codigo_Exame;Valor_Compulab;Valor_Simus;Tipo_Divergencia\n" + "\n".join(all_csv_rows)
        
        total_divergences = len(all_csv_rows)
        
        # Report sem markdown code blocks para facilitar parsing
        final_report = f"""# RELATÓRIO DE AUDITORIA DE IA

**Data:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
**Total de Divergências Encontradas:** {total_divergences}

## Detalhes das Divergências

{final_csv}

*Este relatório foi gerado automaticamente por IA Audit (Modo Turbo).*
"""
        
        yield 100, "Concluído"
        yield final_report, "" # Retorno final (analysis, error)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        yield 100, "Erro"
        yield "", f"Erro na Auditoria IA: {str(e)}"

def format_ai_report(ai_analysis: str) -> str:
    """Formata o relatório da IA para download"""
    return ai_analysis
