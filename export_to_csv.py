import pdfplumber
from decimal import Decimal
import re
from collections import defaultdict
import pandas as pd
import sys

# Funções auxiliares (mesmas do app.py)
def parse_currency_value(value_str):
    """Converte string de valor brasileiro para Decimal"""
    if not value_str:
        return None
    value_str = str(value_str).strip()
    value_str = re.sub(r'R\$\s*', '', value_str)
    value_str = value_str.replace('.', '').replace(',', '.')
    try:
        return Decimal(value_str)
    except:
        return None

def normalize_name(name):
    """Normaliza nome para comparação"""
    if not name:
        return ""
    name = str(name).strip().upper()
    name = ' '.join(name.split())
    replacements = {
        'Á': 'A', 'À': 'A', 'Â': 'A', 'Ã': 'A',
        'É': 'E', 'Ê': 'E',
        'Í': 'I',
        'Ó': 'O', 'Ô': 'O', 'Õ': 'O',
        'Ú': 'U', 'Û': 'U',
        'Ç': 'C'
    }
    for old, new in replacements.items():
        name = name.replace(old, new)
    name = re.sub(r'[^\w\s]', '', name)
    return name

def normalize_exam_name(exam_name):
    """Normaliza nome do exame para comparação"""
    if not exam_name:
        return ""
    exam_name = str(exam_name).strip().upper()
    exam_name = ' '.join(exam_name.split())
    replacements = {
        'Á': 'A', 'À': 'A', 'Â': 'A', 'Ã': 'A',
        'É': 'E', 'Ê': 'E',
        'Í': 'I',
        'Ó': 'O', 'Ô': 'O', 'Õ': 'O',
        'Ú': 'U', 'Û': 'U',
        'Ç': 'C'
    }
    for old, new in replacements.items():
        exam_name = exam_name.replace(old, new)
    exam_name = re.sub(r'\([^)]*\)', '', exam_name)
    exam_name = re.sub(r'[^\w\s]', ' ', exam_name)
    exam_name = ' '.join(exam_name.split())
    return exam_name

def _collect_compulab_lines(pdf_file):
    lines_all = []
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            lines_all.extend(text.split("\n"))
    return lines_all

def _build_exam_vocab(lines):
    vocab = set()
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if re.match(r'^\d+\s+', line):
            continue
        match = re.search(r'(\d{10})\s+\d+\s+([\d,]+)', line)
        if not match:
            continue
        exam_left = line.split(match.group(1))[0].strip()
        exam_name = normalize_exam_name(exam_left)
        if exam_name:
            for token in exam_name.split():
                vocab.add(token)
    return vocab

def _split_patient_exam(tokens, exam_vocab):
    if not tokens:
        return [], []
    split_idx = None
    for i, token in enumerate(tokens):
        if any(ch.isdigit() for ch in token):
            split_idx = i
            break
        if token in exam_vocab:
            split_idx = i
            break
    if split_idx is None or split_idx == 0:
        split_idx = min(4, max(2, len(tokens) - 1))
    patient_tokens = tokens[:split_idx]
    exam_tokens = tokens[split_idx:]
    return patient_tokens, exam_tokens

def extract_compulab_to_csv(pdf_file, output_csv):
    """Extrai dados do COMPULAB e salva em CSV"""
    print("Processando COMPULAB.pdf...")
    
    lines_all = _collect_compulab_lines(pdf_file)
    exam_vocab = _build_exam_vocab(lines_all)
    current_patient = None
    
    rows = []
    
    for line in lines_all:
        line = line.strip()
        if not line:
            continue
        if any(x in line.upper() for x in ["PAGINA", "SUBTOTAL:", "TOTAL:", "RELACAO DOS", "PERIODO", "SEQ NOME"]):
            continue
        
        code_match = re.search(r'(\d{10})\s+\d+\s+([\d,]+)', line)
        if not code_match:
            # Verificar se é linha só com nome de paciente
            if re.match(r'^\d+\s+[A-ZÁÉÍÓÚÂÊÔÇ\s]{10,}', line):
                parts = line.split()
                if len(parts) >= 2:
                    patient_parts = parts[1:]
                    patient_name = normalize_name(" ".join(patient_parts))
                    if patient_name:
                        current_patient = patient_name
            continue
        
        exam_code = code_match.group(1)
        exam_value = parse_currency_value(code_match.group(2))
        if not exam_value:
            continue
        
        left = line.split(exam_code)[0].strip()
        tokens = left.split()
        
        if re.match(r'^\d+$', tokens[0]):
            tokens = tokens[1:]
            patient_tokens, exam_tokens = _split_patient_exam(tokens, exam_vocab)
            patient_name = normalize_name(" ".join(patient_tokens))
            exam_name = normalize_exam_name(" ".join(exam_tokens))
            if not patient_name:
                continue
            current_patient = patient_name
        elif current_patient:
            exam_name = normalize_exam_name(" ".join(tokens))
            patient_name = current_patient
        else:
            continue
        
        if not exam_name or len(exam_name) < 3:
            exam_name = f"EXAME {exam_code}"
        
        rows.append({
            'Paciente': patient_name,
            'Nome_Exame': exam_name,
            'Codigo_Exame': exam_code,
            'Valor': float(exam_value)
        })
    
    df = pd.DataFrame(rows)
    df.to_csv(output_csv, index=False, sep=';', decimal=',', encoding='utf-8-sig')
    print(f"✅ COMPULAB exportado: {len(rows)} exames de {df['Paciente'].nunique()} pacientes")
    print(f"   Salvo em: {output_csv}")
    return df

def extract_simus_to_csv(pdf_file, output_csv, compulab_patients=None):
    """Extrai dados do SIMUS e salva em CSV"""
    print("Processando SIMUS.pdf...")
    
    rows = []
    total_value = Decimal('0')
    sigtap_value = None
    contratualizado_value = None
    
    if compulab_patients:
        candidate_patients = []
        for patient in compulab_patients:
            tokens = patient.split()
            candidate_patients.append(tokens)
    else:
        candidate_patients = None
    
    try:
        with pdfplumber.open(pdf_file) as pdf:
            first_page = pdf.pages[0]
            first_text = first_page.extract_text()
            if first_text:
                pattern = r'R\$([\d.]+,\d{2})\s*\(SIGTAP\).*?R\$([\d.]+,\d{2})\s*\(Contratualizados\)'
                match = re.search(pattern, first_text)
                if match:
                    sigtap_value = parse_currency_value(match.group(1))
                    contratualizado_value = parse_currency_value(match.group(2))
                    total_value = contratualizado_value
            
            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue
                
                lines = text.split("\n")
                for i, line in enumerate(lines):
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Procurar código de exame
                    code_match = re.search(r'\b(\d{10})\b', line)
                    if not code_match:
                        continue
                    
                    exam_code = code_match.group(1)
                    
                    # Extrair valores monetários
                    values = []
                    for val_match in re.finditer(r'R\$\s*([\d.]+,\d{2})', line):
                        val = parse_currency_value(val_match.group(1))
                        if val and val > Decimal('0'):
                            values.append(val)
                    
                    if len(values) >= 2:
                        exam_value = values[1]
                    elif len(values) == 1:
                        exam_value = values[0]
                    else:
                        continue
                    
                    # Extrair paciente e exame
                    tokens = line.split()
                    patient_name = None
                    exam_name = ""
                    
                    if candidate_patients:
                        patient_name, start_idx = _find_patient_in_tokens(tokens, candidate_patients)
                        if patient_name and start_idx is not None:
                            remaining = tokens[start_idx:]
                            exam_name = normalize_exam_name(" ".join(remaining))
                    
                    if not patient_name:
                        # Tentar pegar da coluna PACIENTE se for tabela
                        if len(tokens) > 4:
                            potential_patient = normalize_name(" ".join(tokens[4:7]))
                            if potential_patient and len(potential_patient.split()) >= 2:
                                patient_name = potential_patient
                    
                    if not patient_name:
                        continue
                    
                    if not exam_name:
                        # Remover paciente, códigos, valores, datas
                        exam_text = line
                        exam_text = re.sub(r'\b\d{10}\b', '', exam_text)
                        exam_text = re.sub(r'R\$\s*[\d.,]+', '', exam_text)
                        exam_text = re.sub(r'\d{2}/\d{2}/\d{2,4}', '', exam_text)
                        exam_text = exam_text.replace(patient_name, '').strip()
                        exam_name = normalize_exam_name(exam_text)
                    
                    if not exam_name or len(exam_name) < 3:
                        exam_name = f"EXAME {exam_code}"
                    
                    rows.append({
                        'Paciente': patient_name,
                        'Nome_Exame': exam_name,
                        'Codigo_Exame': exam_code,
                        'Valor': float(exam_value)
                    })
    
    except Exception as e:
        print(f"Erro ao processar SIMUS: {e}")
        return None
    
    df = pd.DataFrame(rows)
    df.to_csv(output_csv, index=False, sep=';', decimal=',', encoding='utf-8-sig')
    print(f"✅ SIMUS exportado: {len(rows)} exames de {df['Paciente'].nunique()} pacientes")
    print(f"   Salvo em: {output_csv}")
    if sigtap_value:
        print(f"   SIGTAP: R$ {sigtap_value:,.2f}, Contratualizado: R$ {contratualizado_value:,.2f}")
    return df

def main():
    if len(sys.argv) < 3:
        print("Uso: python export_to_csv.py COMPULAB.pdf SIMUS.pdf")
        print("Ou: python export_to_csv.py (usa COMPULAB.pdf e SIMUS.pdf na pasta atual)")
        sys.exit(1)
    
    compulab_pdf = sys.argv[1] if len(sys.argv) > 1 else "COMPULAB.pdf"
    simus_pdf = sys.argv[2] if len(sys.argv) > 2 else "SIMUS.pdf"
    
    try:
        # Exportar COMPULAB
        compulab_df = extract_compulab_to_csv(compulab_pdf, "compulab_data.csv")
        
        # Exportar SIMUS (usando pacientes do COMPULAB para melhor matching)
        compulab_patients = compulab_df['Paciente'].unique().tolist() if compulab_df is not None else None
        simus_df = extract_simus_to_csv(simus_pdf, "simus_data.csv", compulab_patients)
        
        print("\n✅ Exportação concluída!")
        print("\nArquivos gerados:")
        print("  - compulab_data.csv")
        print("  - simus_data.csv")
        print("\nAgora você pode usar o app para analisar os CSVs!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

