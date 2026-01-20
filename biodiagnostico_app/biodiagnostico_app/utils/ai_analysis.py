"""
AI Analysis utilities using OpenAI
Laboratório Biodiagnóstico
AI Auditor Implementation (Async Parallel Optimized with Robust Parsing)
"""
from datetime import datetime
import openai
import csv
import io
import asyncio
import math
import re
from typing import Optional, Tuple, Dict, List, Any, Callable

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

async def process_batch(client, system_prompt, chunk_patients, compulab_patients, simus_patients, batch_id, total_batches, retries=2):
    """Processa um único batch (async) com retry"""
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
                timeout=45.0 # Timeout de 45s por batch
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse robusto
            rows = []
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if not line: continue
                # Ignorar cabeçalhos comuns ou blocos de código
                if any(x in line.lower() for x in ["paciente;", "tipo_divergencia", "```"]):
                    continue
                
                # Garantir que a linha tenha pelo menos alguns separadores ;
                if line.count(';') >= 4:
                    rows.append(line)
                elif line.count(',') >= 4 and ';' not in line:
                    # IA usou vírgula por engano? Vamos converter
                    line = line.replace(',', ';')
                    rows.append(line)
                    
            return rows
            
        except Exception as e:
            if attempt < retries:
                print(f"Aviso batch {batch_id} (tentativa {attempt+1}): {e}. Tentando novamente...")
                await asyncio.sleep(2 * (attempt + 1))
            else:
                print(f"Erro fatal no batch {batch_id} após {retries} retentativas: {e}")
                return []
    return []

async def generate_ai_analysis(
    compulab_patients: dict,
    simus_patients: dict,
    api_key: str
):
    """
    Executa a auditoria de IA com estratégia de Chunking Paralelo e Parsing Robusto.
    Yields (percentage, status_message) e finally returns (analysis_result, error)
    """
    try:
        yield 0, "Iniciando IA Auditor..."
        await asyncio.sleep(0.1)

        if not api_key:
            yield 100, "Erro de Configuração"
            yield "", "API Key não fornecida."
            return
            
        client = openai.AsyncOpenAI(api_key=api_key)
        
        # System Prompt do Auditor (OTIMIZADO)
        system_prompt = """
# ROLE
You are a Senior Medical Audit Algorithm. Compare Dataset A (COMPULAB) and Dataset B (SIMUS).

# LOGIC RULES
1. Match by PATIENT + CODE.
2. Ignore differences <= 0.05.
3. Output ONLY the discrepancies. 

# OUTPUT FORMAT (STRICT CSV)
- Separator: Semicolon (;)
- Format: Paciente;Nome_Exame;Codigo_Exame;Valor_Compulab;Valor_Simus;Tipo_Divergencia
- Type terms: "Paciente Ausente no SIMUS", "Paciente Ausente no COMPULAB", "Exame Ausente no SIMUS", "Exame Ausente no COMPULAB", "Valor Divergente"
- NO Header, NO Markdown, NO conversational text. Just lines of data.
"""

        all_csv_rows = []
        all_patients = sorted(list(set(list(compulab_patients.keys()) + list(simus_patients.keys()))))
        
        chunk_size = 25
        total_patients = len(all_patients)
        batches = [all_patients[i:i + chunk_size] for i in range(0, total_patients, chunk_size)]
        total_batches = len(batches)
        completed_batches = 0
        
        yield 5, f"Auditando {total_batches} lotes..."
        
        # Semáforo para não estourar rate limit
        sem = asyncio.Semaphore(5)
        
        async def sem_process_batch(batch_idx, chunk):
            async with sem:
                return await process_batch(client, system_prompt, chunk, compulab_patients, simus_patients, batch_idx+1, total_batches)

        tasks = [asyncio.create_task(sem_process_batch(i, batch)) for i, batch in enumerate(batches)]
        
        pending = list(tasks)
        while pending:
            done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)
            for task in done:
                res = await task
                all_csv_rows.extend(res)
                completed_batches += 1
                progress = 5 + int((completed_batches / total_batches) * 90)
                yield progress, f"Processado lote {completed_batches}/{total_batches}..."
                
        yield 98, "Consolidando relatório..."
        
        try:
             all_csv_rows.sort(key=lambda x: x.split(';')[0] if ';' in x else x)
        except:
             pass

        final_csv = "Paciente;Nome_Exame;Codigo_Exame;Valor_Compulab;Valor_Simus;Tipo_Divergencia\n" + "\n".join(all_csv_rows)
        total_divergences = len(all_csv_rows)
        
        final_report = f"""# RELATÓRIO DE AUDITORIA DE IA - BIODIAGNÓSTICO
**Data:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
**Total de Divergências Encontradas:** {total_divergences}

## Detalhes das Divergências (CSV)
{final_csv}

---
*Este relatório foi gerado automaticamente por IA Audit Engine v2 (gpt-4o).*
"""
        
        yield 100, "Concluído"
        yield final_report, ""
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        yield 100, "Erro"
        yield "", f"Erro na Auditoria IA: {str(e)}"

def format_ai_report(ai_analysis: str) -> str:
    return ai_analysis
