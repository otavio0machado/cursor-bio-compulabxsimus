"""
PDF Processing utilities for COMPULAB and SIMUS files
Laboratório Biodiagnóstico

Otimizado para arquivos grandes (12MB+):
- Processamento em chunks
- Extração seletiva de tabelas
- Limite de páginas por iteração
"""
import pdfplumber
from decimal import Decimal
import re
from collections import defaultdict
import pandas as pd
import tempfile
import os
import gc
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from typing import Optional, Tuple, Dict, List, Any, Callable

# Configurações para arquivos grandes
MAX_PAGES_PER_BATCH = 20  # Processar páginas em lotes
PDF_PROCESSING_TIMEOUT = 300  # 5 minutos de timeout
LARGE_FILE_THRESHOLD_MB = 5  # Arquivos acima disso são considerados grandes

# Mapeamento completo de nomes de exames SIMUS para COMPULAB
EXAM_NAME_MAPPING = {
    # Urina
    'ANÁLISE DE CARACTERES FÍSICOS, ELEMENTOS E SEDIMENTO DA URINA': 'EXAME QUALITATIVO DE URINA',
    'ANALISE DE CARACTERES FISICOS, ELEMENTOS E SEDIMENTO DA URINA': 'EXAME QUALITATIVO DE URINA',
    'ANALISE DE CARACTERES FISICOS ELEMENTOS E SEDIMENTO DA URINA': 'EXAME QUALITATIVO DE URINA',
    
    # Hemograma
    'HEMOGRAMA COMPLETO': 'HEMOGRAMA',
    
    # Vitaminas
    'DOSAGEM DE 25 HIDROXIVITAMINA D': 'VITAMINA D25',
    'DOSAGEM DE VITAMINA B12': 'VITAMINA B12',
    
    # Hormônios Tireoide
    'DOSAGEM DE HORMONIO TIREOESTIMULANTE (TSH)': 'TIREOTROFINA (TSH)',
    'DOSAGEM DE HORMONIO TIREOESTIMULANTE TSH': 'TIREOTROFINA (TSH)',
    'DOSAGEM DE TIROXINA LIVRE (T4 LIVRE)': 'TIROXINA LIVRE (T4 LIVRE)',
    'DOSAGEM DE TIROXINA LIVRE T4 LIVRE': 'TIROXINA LIVRE (T4 LIVRE)',
    'DOSAGEM DE TIROXINA (T4)': 'TIROXINA (T4)',
    
    # Glicose e Lipídios
    'DOSAGEM DE GLICOSE': 'GLICOSE',
    'DOSAGEM DE COLESTEROL TOTAL': 'COLESTEROL TOTAL',
    'DOSAGEM DE COLESTEROL HDL': 'COLESTEROL HDL',
    'DOSAGEM DE COLESTEROL LDL': 'COLESTEROL LDL',
    'DOSAGEM DE TRIGLICERIDEOS': 'TRIGLICERIDEOS',
    'DOSAGEM DE HEMOGLOBINA GLICOSILADA': 'HEMOGLOBINA GLICOSILADA A1C',
    
    # Função Renal
    'DOSAGEM DE CREATININA': 'CREATININA',
    'DOSAGEM DE ACIDO URICO': 'ACIDO URICO',
    'DOSAGEM DE UREIA': 'UREIA',
    'DOSAGEM DE MICROALBUMINA NA URINA': 'MICROALBUMINURIA',
    
    # Eletrólitos
    'DOSAGEM DE POTASSIO': 'POTASSIO',
    'DOSAGEM DE SODIO': 'SODIO',
    'DOSAGEM DE CALCIO': 'CALCIO',
    'DOSAGEM DE MAGNESIO': 'MAGNESIO',
    
    # Marcadores Tumorais
    'DOSAGEM DE ANTIGENO PROSTATICO ESPECIFICO (PSA)': 'ANTIGENO PROSTATICO ESPECIFICO',
    'DOSAGEM DE ANTIGENO PROSTATICO ESPECIFICO PSA': 'ANTIGENO PROSTATICO ESPECIFICO',
    'DOSAGEM DE FRACAO PROSTATICA DA FOSFATASE ACIDA': 'FOSFATASE ACIDA PROSTATICA',
    
    # Urocultura
    'CULTURA DE BACTERIAS P/ IDENTIFICACAO': 'UROCULTURA',
    'CULTURA DE BACTERIAS P IDENTIFICACAO': 'UROCULTURA',
    
    # Enzimas Hepáticas
    'DOSAGEM DE TRANSAMINASE GLUTAMICO-OXALACETICA (TGO)': 'GOT',
    'DOSAGEM DE TRANSAMINASE GLUTAMICO-OXALACETICA TGO': 'GOT',
    'DOSAGEM DE TRANSAMINASE GLUTAMICO-PIRUVICA (TGP)': 'GPT',
    'DOSAGEM DE TRANSAMINASE GLUTAMICO-PIRUVICA TGP': 'GPT',
    'DOSAGEM DE GAMA-GLUTAMIL-TRANSFERASE (GAMA GT)': 'GAMA GT',
    'DOSAGEM DE GAMA-GLUTAMIL-TRANSFERASE GAMA GT': 'GAMA GT',
    'DOSAGEM DE FOSFATASE ALCALINA': 'FOSFATASE ALCALINA',
    'DOSAGEM DE BILIRRUBINA TOTAL E FRACOES': 'BILIRRUBINAS',
    
    # Ferro e Ferritina
    'DOSAGEM DE FERRITINA': 'FERRITINA',
    'DOSAGEM DE FERRO SERICO': 'FERRO SERICO',
    'DOSAGEM DE TRANSFERRINA': 'TRANSFERRINA',
    
    # Hormônios
    'DOSAGEM DE INSULINA': 'INSULINA',
    'DOSAGEM DE ESTRADIOL': 'ESTRADIOL',
    'DOSAGEM DE CORTISOL': 'CORTISOL',
    'DOSAGEM DE PROLACTINA': 'PROLACTINA',
    'DOSAGEM DE PROGESTERONA': 'PROGESTERONA',
    'DOSAGEM DE TESTOSTERONA LIVRE': 'TESTOSTERONA LIVRE',
    'DOSAGEM DE TESTOSTERONA': 'TESTOSTERONA TOTAL',
    'DOSAGEM DE HORMONIO FOLICULO-ESTIMULANTE (FSH)': 'HORMONIO FOLICULO ESTIMULANTE FSH',
    'DOSAGEM DE HORMONIO FOLICULO-ESTIMULANTE FSH': 'HORMONIO FOLICULO ESTIMULANTE FSH',
    'DOSAGEM DE HORMONIO LUTEINIZANTE (LH)': 'HORMONIO LUTEINIZANTE LH',
    'DOSAGEM DE HORMONIO LUTEINIZANTE LH': 'HORMONIO LUTEINIZANTE LH',
    'DOSAGEM DE GONADOTROFINA CORIONICA HUMANA (HCG, BETA HCG)': 'B-HCG',
    'DOSAGEM DE GONADOTROFINA CORIONICA HUMANA HCG BETA HCG': 'B-HCG',
    'DOSAGEM DE ANDROSTENEDIONA': 'ANDROSTENEDIONA',
    
    # Proteínas
    'DOSAGEM DE PROTEINA C REATIVA': 'PROTEINA C REATIVA',
    'DOSAGEM DE PROTEINAS TOTAIS E FRACOES': 'PROTEÍNAS TOTAIS E FRAÇÕES',
    
    # Coagulação
    'DETERMINAÇÃO DE VELOCIDADE DE HEMOSSEDIMENTAÇÃO (VHS)': 'V. S. G.',
    'DETERMINACAO DE VELOCIDADE DE HEMOSSEDIMENTACAO VHS': 'V. S. G.',
    'DETERMINAÇÃO DE TEMPO E ATIVIDADE DA PROTROMBINA (TAP)': 'TEMPO DE PROTROMBINA',
    'DETERMINACAO DE TEMPO E ATIVIDADE DA PROTROMBINA TAP': 'TEMPO DE PROTROMBINA',
    'DETERMINAÇÃO DE TEMPO DE TROMBOPLASTINA PARCIAL ATIVADA (TTP ATIVADA)': 'TEMPO DE TROMBOPLASTINA ATIVADO (TTPA)',
    'DETERMINACAO DE TEMPO DE TROMBOPLASTINA PARCIAL ATIVADA TTP ATIVADA': 'TEMPO DE TROMBOPLASTINA ATIVADO (TTPA)',
    
    # Autoanticorpos
    'PESQUISA DE ANTICORPOS ANTINUCLEO': 'FATOR ANTI NUCLEAR (FAN)',
    'PESQUISA DE ANTICORPOS ANTIMICROSSOMAS': 'ANTI-TIREOPEROXIDASE (ANTI-TPO)',
    
    # Sorologias
    'PESQUISA DE ANTICORPOS IGG ANTITOXOPLASMA': 'TOXOPLASMOSE (IFI-IgG)',
    'PESQUISA DE ANTICORPOS IGM ANTITOXOPLASMA': 'TOXOPLASMOSE (IFI-IgM)',
    'PESQUISA DE ANTICORPOS IGG ANTICITOMEGALOVIRUS': 'CITOMEGALOVIRUS IgG',
    'PESQUISA DE ANTICORPOS IGM ANTICITOMEGALOVIRUS': 'CITOMEGALOVIRUS IgM',
    'PESQUISA DE ANTICORPOS IGG CONTRA O VIRUS EPSTEIN-BARR': 'EPSTEIN-BAAR IgG',
    'PESQUISA DE ANTICORPOS IGM CONTRA O VIRUS EPSTEIN-BARR': 'EPSTEIN-BAAR IgM',
    
    # Sífilis e Hepatites
    'TESTE NÃO TREPONEMICO P/ DETECÇÃO DE SIFILIS': 'VDRL QUANTITATIVO',
    'TESTE NAO TREPONEMICO P DETECCAO DE SIFILIS': 'VDRL QUANTITATIVO',
    'PESQUISA DE ANTICORPOS CONTRA ANTIGENO DE SUPERFICIE DO VIRUS DA HEPATITE B (ANTI-HBS)': 'ANTI-HBS',
    'PESQUISA DE ANTICORPOS CONTRA ANTIGENO DE SUPERFICIE DO VIRUS DA HEPATITE B ANTI-HBS': 'ANTI-HBS',
    'PESQUISA LABORATORIAL DE ANTIGENO DE SUPERFÍCIE DO VÍRUS DA HEPATITE B (HBSAG)': 'ABsAg (ANTIGENO AUSTRALIA)',
    'PESQUISA LABORATORIAL DE ANTIGENO DE SUPERFICIE DO VIRUS DA HEPATITE B HBSAG': 'ABsAg (ANTIGENO AUSTRALIA)',
    
    # Sangue
    'DETERMINACAO DIRETA E REVERSA DE GRUPO ABO': 'GRUPO SANGUINEO',
    'PESQUISA DE FATOR RH (INCLUI D FRACO)': 'FATOR Rh',
    'TESTE INDIRETO DE ANTIGLOBULINA HUMANA (TIA)': 'COOMBS INDIRETO',
    
    # Outros
    'DOSAGEM DE CREATINOFOSFOQUINASE (CPK)': 'CREATINOFOSFOQUINASE',
    'DOSAGEM DE CREATINOFOSFOQUINASE CPK': 'CREATINOFOSFOQUINASE',
    'DOSAGEM DE LIPASE': 'LIPASE',
    'DOSAGEM DE AMILASE': 'AMILASE',
    'ANTIBIOGRAMA': 'ANTIBIOGRAMA',
    'PESQUISA LABORATORIAL DE ANTIGENOS DE HIV E/OU ANTICORPOS ANTI-HIV-1 OU ANTI-HIV-2': 'HIV 1/2',
    'PESQUISA LABORATORIAL DE ANTIGENOS DE HIV E OU ANTICORPOS ANTI-HIV-1 OU ANTI-HIV-2': 'HIV 1/2',
    'PESQUISA DE SANGUE OCULTO NAS FEZES': 'SANGUE OCULTO',
    
    # Novos Sinônimos (Solicitados pelo Usuário)
    'CLEARANCE DE CREATININA': 'DEPURACAO DA CREATININA ENDOGENA',
    'CONTAGEM DE PLAQUETAS': 'PLAQUETAS',
    'DETERMINACAO DE CAPACIDADE DE FIXACAO DO FERRO': 'CAPACIDADE FERROPEXICA',
    'DETERMINACAO DE CURVA GLICEMICA CLASSICA': 'GLICOSE 1 E 2 HORAS',
    'DOSAGEM DE 17 ALFA HIDROXIPROGESTERONA': '17 HIDROXIPROGESTERONA',
    'DOSAGEM DE ALFA 1 GLICOPROTEINA ACIDA': 'ALFA 1 GLICOPROTEINA ACIDA',
    'DOSAGEM DE FOLATO': 'ACIDO FOLICO',
    'DOSAGEM DE FOSFORO': 'FOSFORO',
    'DOSAGEM DE IMUNOGLOBULINA A': 'IMUNOGLOBULINA A',
    'DOSAGEM DE LITIO': 'LITIO',
    'DOSAGEM DE PARATORMONIO': 'PARATORMONIO',
    'DOSAGEM DE TIREOGLOBULINA': 'TIREOGLOBULINA',
    'DOSAGEM DE TRIIODOTIRONINA': 'TRIIODOTIRONINA T3 RIE',
    'DOSAGEM DE ZINCO': 'ZINCO',
    'PESQUISA DE ANTICORPOS ANTIESTREPTOLISINA O': 'ANTIESTREPTOLISINA O',
    'PESQUISA DE ANTICORPOS ANTIINSULINA': 'ANTICORPOS ANTI INSULINA',
    'PESQUISA DE ANTIGENO CARCINOEMBRIONARIO': 'ANTIGENO CARCINO EMBRIONICO',
    'PESQUISA DE OVOS E CISTOS DE PARASITAS 1ª AMOSTRA': 'EXAME PARASITOLOGICO DE FEZES 1 O',
    'PESQUISA LABORATORIAL DE ANTICORPOS ANTI HTLV 1 HTLV 2 PARA POPULACAO GERAL': 'HTLV I II',
    'PESQUISA LABORATORIAL DE ANTICORPOS CONTRA O VIRUS DA HEPATITE C (PARA POPULACAO GERAL/EM GESTANTE)': 'ANTI HCV',
    'SANGUE OCULTO': 'PESQUISA DE SANGUE OCULTO FEZES',
    'TIROXINA': 'TIROXINA T4 RIE',
}


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
    """Normaliza nome para comparação (remove acentos, espaços extras, etc)"""
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


def normalize_exam_name_for_comparison(exam_name):
    """Normaliza nome do exame removendo palavras genéricas para comparação inteligente"""
    if not exam_name:
        return ""
    
    normalized = normalize_exam_name(exam_name)
    
    generic_words = [
        'DOSAGEM DE', 'DOSAGEM', 'DETERMINACAO DE', 'DETERMINACAO',
        'ANALISE DE', 'ANALISE', 'AVALIACAO DE', 'AVALIACAO',
        'MEDICAO DE', 'MEDICAO', 'MEDIDA DE', 'MEDIDA',
        'TESTE DE', 'TESTE', 'EXAME DE', 'EXAME',
        'QUANTIFICACAO DE', 'QUANTIFICACAO', 'DETECCAO DE', 'DETECCAO',
        'PESQUISA DE', 'PESQUISA', 'TRIAGEM DE', 'TRIAGEM',
        'SOROLOGIA DE', 'SOROLOGIA', 'IMUNOLOGIA DE', 'IMUNOLOGIA',
        'QUALITATIVO DE', 'QUALITATIVO', 'QUANTITATIVO DE', 'QUANTITATIVO'
    ]
    
    for word in generic_words:
        pattern_start = r'^' + re.escape(word) + r'\s+'
        normalized = re.sub(pattern_start, '', normalized, flags=re.IGNORECASE)
        pattern_mid = r'\s+' + re.escape(word) + r'\s+'
        normalized = re.sub(pattern_mid, ' ', normalized, flags=re.IGNORECASE)
        pattern_end = r'\s+' + re.escape(word) + r'$'
        normalized = re.sub(pattern_end, '', normalized, flags=re.IGNORECASE)
    
    normalized = ' '.join(normalized.split())
    return normalized


def extract_key_terms(exam_name):
    """Extrai termos-chave importantes do nome do exame"""
    normalized = normalize_exam_name_for_comparison(exam_name)
    words = normalized.split()
    
    key_terms = []
    stop_words = {'DE', 'DA', 'DO', 'DAS', 'DOS', 'E', 'OU', 'COM', 'SEM', 'POR', 'PARA'}
    
    for word in words:
        if len(word) >= 3 and word not in stop_words:
            key_terms.append(word)
    
    return set(key_terms)


def exam_names_match(exam_name1, exam_name2):
    """Verifica se dois nomes de exame representam o mesmo exame"""
    norm1 = normalize_exam_name_for_comparison(exam_name1)
    norm2 = normalize_exam_name_for_comparison(exam_name2)
    
    if norm1 == norm2:
        return True
    
    exam_synonyms = {
        'URINA': [
            'URINA', 'EAS', 'ELEMENTOS', 'SEDIMENTO', 'CARACTERES', 'FISICOS',
            'QUIMICOS', 'QUALITATIVO', 'QUANTITATIVO'
        ],
        'HEMOGRAMA': ['HEMOGRAMA', 'HEMATOLOGICO', 'COMPLETO', 'SERIE'],
        'GLICOSE': ['GLICOSE', 'GLICEMIA'],
        'TSH': ['TSH', 'TIREOTROFINA', 'TIREOESTIMULANTE'],
        'T4': ['T4', 'TIROXINA'],
        'T3': ['T3', 'TRIODOTIRONINA'],
    }
    
    key_terms1 = extract_key_terms(exam_name1)
    key_terms2 = extract_key_terms(exam_name2)
    
    if key_terms1 and key_terms2:
        if key_terms1.issubset(key_terms2) or key_terms2.issubset(key_terms1):
            return True
    
    common_terms = key_terms1 & key_terms2
    
    if 'URINA' in key_terms1 and 'URINA' in key_terms2:
        if len(common_terms) >= 2:
            return True
        urina_related = {'ELEMENTOS', 'SEDIMENTO', 'CARACTERES', 'FISICOS', 
                        'QUIMICOS', 'QUALITATIVO', 'QUANTITATIVO', 'EAS'}
        if (key_terms1 & urina_related) and (key_terms2 & urina_related):
            return True
    
    for exam_type, synonyms in exam_synonyms.items():
        if exam_type == 'URINA':
            continue
        if (key_terms1 & set(synonyms)) and (key_terms2 & set(synonyms)):
            return True
    
    if norm1 and norm2:
        words1 = {w for w in norm1.split() if len(w) >= 3}
        words2 = {w for w in norm2.split() if len(w) >= 3}
        
        if not words1 or not words2:
            return False
        
        if words1.issubset(words2) or words2.issubset(words1):
            return True
    
    return False


def map_simus_to_compulab_exam_name(simus_exam_name):
    """Mapeia nome do exame do SIMUS para o nome equivalente no COMPULAB"""
    if not simus_exam_name:
        return simus_exam_name
    
    simus_clean = str(simus_exam_name).strip().upper()
    
    for simus_key, compulab_value in EXAM_NAME_MAPPING.items():
        if simus_key.upper() == simus_clean:
            return compulab_value
        if normalize_exam_name(simus_key) == normalize_exam_name(simus_clean):
            return compulab_value
    
    normalized_simus = normalize_exam_name(simus_clean)
    for simus_key, compulab_value in EXAM_NAME_MAPPING.items():
        normalized_key = normalize_exam_name(simus_key)
        if normalized_key in normalized_simus or normalized_simus in normalized_key:
            key_words = set(normalized_key.split())
            simus_words = set(normalized_simus.split())
            common_words = key_words & simus_words
            if len(common_words) >= 2:
                return compulab_value
    
    return simus_exam_name


def _collect_compulab_lines(pdf_file):
    lines_all = []
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            lines_all.extend(text.split("\n"))
    return lines_all


def _build_exam_name_set(lines):
    exam_names = set()
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
            exam_names.add(exam_name)
    return exam_names


def _split_patient_exam(tokens, exam_name_set):
    if not tokens:
        return [], []
    for i in range(len(tokens)):
        suffix_tokens = tokens[i:]
        exam_name = normalize_exam_name(" ".join(suffix_tokens))
        if exam_name in exam_name_set and i > 0:
            return tokens[:i], suffix_tokens
    split_idx = min(4, max(2, len(tokens) - 1))
    return tokens[:split_idx], tokens[split_idx:]


def extract_compulab_patients(pdf_file, progress_callback: Optional[Callable[[int], None]] = None):
    """Extrai dados de pacientes do COMPULAB com separação por exame
    
    Args:
        pdf_file: Caminho para o arquivo PDF
        progress_callback: Função callback(percentage: int) para reportar progresso (0-100)
    """
    patients = defaultdict(lambda: {"exams": [], "total": Decimal("0")})
    total_value = Decimal("0")

    try:
        lines_all = _collect_compulab_lines(pdf_file)
        total_lines = len(lines_all)
        exam_name_set = _build_exam_name_set(lines_all)
        current_patient = None

        for idx, line in enumerate(lines_all):
            # Reportar progresso a cada 100 linhas ou no início
            if progress_callback and (idx % 100 == 0 or idx == 0):
                if total_lines > 0:
                    percentage = int((idx / total_lines) * 100)
                    progress_callback(percentage)
            line = line.strip()
            if not line:
                continue
            if any(x in line.upper() for x in ["PAGINA", "SUBTOTAL:", "TOTAL:", "RELACAO DOS", "PERIODO", "SEQ NOME"]):
                continue

            header_match = re.match(r'^(\d+)\s+([A-ZÁÉÍÓÚÂÊÔÇ\s]+)$', line)
            if header_match and not re.search(r'\d{10}', line):
                current_patient = normalize_name(header_match.group(2))
                continue

            code_match = re.search(r'(\d{10})\s+\d+\s+([\d,]+)', line)
            if not code_match:
                continue

            exam_code = code_match.group(1)
            exam_value = parse_currency_value(code_match.group(2))
            if not exam_value:
                continue

            left = line.split(exam_code)[0].strip()
            tokens = left.split()

            if re.match(r'^\d+$', tokens[0]):
                tokens = tokens[1:]
                patient_tokens, exam_tokens = _split_patient_exam(tokens, exam_name_set)
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

            patients[patient_name]["exams"].append(
                {"exam_name": exam_name, "code": exam_code, "value": exam_value}
            )
            patients[patient_name]["total"] += exam_value
            total_value += exam_value

        # Reportar progresso final do processamento de linhas
        if progress_callback:
            progress_callback(100)

        for line in reversed(lines_all):
            if "TOTAL" in line.upper() and "R$" in line:
                currency_values = re.findall(r'R\$\s*([\d.]+,\d{2})', line)
                for val in currency_values:
                    parsed = parse_currency_value(val)
                    if parsed and parsed > Decimal("1000"):
                        total_value = parsed
                        break
                if total_value > Decimal("1000"):
                    break
    except Exception as e:
        print(f"Erro ao processar COMPULAB: {e}")
        return None, None

    return patients, total_value


def _find_patient_in_tokens(tokens, candidate_patients):
    if not candidate_patients:
        return None, None
    for patient_tokens in candidate_patients:
        size = len(patient_tokens)
        if size == 0 or size > len(tokens):
            continue
        for i in range(0, len(tokens) - size + 1):
            if tokens[i : i + size] == patient_tokens:
                return " ".join(tokens[i : i + size]), i + size
    return None, None


def _collect_simus_lines(pdf_file):
    """Coleta todas as linhas do PDF SIMUS - otimizado para arquivos grandes"""
    lines_all = []
    try:
        with pdfplumber.open(pdf_file) as pdf:
            total_pages = len(pdf.pages)
            
            # Processar em batches para arquivos grandes
            for batch_start in range(0, total_pages, MAX_PAGES_PER_BATCH):
                batch_end = min(batch_start + MAX_PAGES_PER_BATCH, total_pages)
                
                for page_idx in range(batch_start, batch_end):
                    page = pdf.pages[page_idx]
                    text = page.extract_text()
                    if not text:
                        continue
                    lines_all.extend(text.split("\n"))
                
                # Liberar memória entre batches
                gc.collect()
                
    except Exception as e:
        print(f"Erro ao coletar linhas SIMUS: {e}")
    
    return lines_all


def extract_simus_patients(pdf_file, known_patient_names=None, progress_callback: Optional[Callable[[int, int], None]] = None):
    """
    Extrai dados de pacientes do SIMUS usando tabelas do PDF
    
    Otimizado para arquivos grandes:
    - Processa páginas em batches
    - Libera memória entre iterações
    - Suporta callback de progresso
    
    Args:
        pdf_file: Caminho para o arquivo PDF
        known_patient_names: Lista opcional de nomes de pacientes conhecidos
        progress_callback: Função callback(pagina_atual, total_paginas) para reportar progresso
    """
    patients = defaultdict(lambda: {'exams': [], 'total': Decimal('0')})
    total_value = Decimal('0')
    sigtap_value = None
    contratualizado_value = None
    
    try:
        with pdfplumber.open(pdf_file) as pdf:
            total_pages = len(pdf.pages)
            
            # Processar primeira página para extrair totais
            first_page = pdf.pages[0]
            first_text = first_page.extract_text()
            if first_text:
                pattern = r'R\$([\d.]+,\d{2})\s*\(SIGTAP\).*?R\$([\d.]+,\d{2})\s*\(Contratualizados\)'
                match = re.search(pattern, first_text, re.DOTALL)
                if match:
                    sigtap_value = parse_currency_value(match.group(1))
                    contratualizado_value = parse_currency_value(match.group(2))
                    total_value = contratualizado_value
            
            candidate_patients = []
            if known_patient_names:
                for name in known_patient_names:
                    tokens = normalize_name(name).split()
                    if tokens:
                        candidate_patients.append(tokens)
                candidate_patients.sort(key=len, reverse=True)
            
            # Processar páginas em batches para arquivos grandes
            for batch_start in range(0, total_pages, MAX_PAGES_PER_BATCH):
                batch_end = min(batch_start + MAX_PAGES_PER_BATCH, total_pages)
                
                for page_idx in range(batch_start, batch_end):
                    page = pdf.pages[page_idx]
                    
                    # Reportar progresso se callback foi fornecido
                    if progress_callback:
                        progress_callback(page_idx + 1, total_pages)
                    
                    # Tentar extrair tabelas (método mais confiável)
                    try:
                        tables = page.extract_tables()
                    except Exception:
                        tables = []
                    
                    for table in tables:
                        if not table or len(table) < 2:
                            continue
                        
                        # Busca mais flexível do cabeçalho
                        header_row = None
                        header_keywords = ['PACIENTE', 'EXAME', 'PROCEDIMENTO', 'NOME', 'CÓDIGO', 'VALOR']
                        for i, row in enumerate(table):
                            if not row:
                                continue
                            row_text = ' '.join([str(c).upper() if c else '' for c in row])
                            if any(kw in row_text for kw in header_keywords):
                                header_row = i
                                break
                        
                        if header_row is None:
                            # Tentar usar primeira linha como cabeçalho se tiver pelo menos 3 colunas
                            if table[0] and len([c for c in table[0] if c]) >= 3:
                                header_row = 0
                            else:
                                continue
                        
                        header = table[header_row]
                        paciente_col = None
                        exame_col = None
                        valor_pago_col = None
                        codigo_col = None
                        valor_sus_col = None
                        
                        for idx, cell in enumerate(header):
                            if not cell:
                                continue
                            cell_upper = str(cell).upper().strip()
                            
                            # Detectar coluna de paciente
                            if any(kw in cell_upper for kw in ['PACIENTE', 'BENEFICIÁRIO', 'BENEFICIARIO', 'NOME']) and paciente_col is None:
                                paciente_col = idx
                            # Detectar coluna de exame
                            elif any(kw in cell_upper for kw in ['EXAME', 'PROCEDIMENTO', 'DESCRIÇÃO', 'DESCRICAO']) and exame_col is None:
                                exame_col = idx
                            # Detectar coluna de valor pago (prioridade)
                            elif ('VALOR PAGO' in cell_upper or ('PAGO' in cell_upper and 'SUS' not in cell_upper) or 'VL PAGO' in cell_upper) and valor_pago_col is None:
                                valor_pago_col = idx
                            # Detectar coluna de código
                            elif any(kw in cell_upper for kw in ['COD', 'CÓD', 'CÓDIGO', 'CODIGO', 'SIGTAP']) and codigo_col is None:
                                codigo_col = idx
                            # Detectar valor SUS como fallback
                            elif 'SUS' in cell_upper and 'VL' in cell_upper and valor_sus_col is None:
                                valor_sus_col = idx
                        
                        # Se não encontrou valor pago, usar valor SUS
                        if valor_pago_col is None and valor_sus_col is not None:
                            valor_pago_col = valor_sus_col
                        
                        for row in table[header_row + 1:]:
                            if not row or len(row) < max(paciente_col or 0, exame_col or 0, valor_pago_col or 0) + 1:
                                continue
                            
                            paciente_cell = str(row[paciente_col]).strip() if paciente_col is not None and len(row) > paciente_col and row[paciente_col] else ""
                            if not paciente_cell or paciente_cell.upper() in ['PACIENTE', 'TOTAL', 'TOTAL E FRACOES', '', 'SUBTOTAL']:
                                continue
                            
                            patient_name = normalize_name(paciente_cell)
                            
                            exame_cell = str(row[exame_col]).strip() if exame_col is not None and len(row) > exame_col and row[exame_col] else ""
                            
                            # Buscar código de exame (8 a 10 dígitos são comuns)
                            exam_code = ""
                            if codigo_col is not None and len(row) > codigo_col and row[codigo_col]:
                                # Primeiro tenta 10 dígitos
                                code_match = re.search(r'\b(\d{10})\b', str(row[codigo_col]))
                                if code_match:
                                    exam_code = code_match.group(1)
                                else:
                                    # Fallback para 8 dígitos
                                    code_match = re.search(r'\b(\d{8})\b', str(row[codigo_col]))
                                    if code_match:
                                        exam_code = code_match.group(1)
                            
                            # Tentar extrair código do campo de exame se não encontrou
                            if not exam_code and exame_cell:
                                code_match = re.search(r'\b(\d{10})\b', exame_cell)
                                if code_match:
                                    exam_code = code_match.group(1)
                                else:
                                    code_match = re.search(r'\b(\d{8})\b', exame_cell)
                                    if code_match:
                                        exam_code = code_match.group(1)

                            
                            exam_value = None
                            if valor_pago_col and len(row) > valor_pago_col and row[valor_pago_col]:
                                exam_value = parse_currency_value(str(row[valor_pago_col]))
                            
                            if not exam_value or exam_value == Decimal('0'):
                                row_text = ' '.join([str(cell) if cell else '' for cell in row])
                                values = re.findall(r'R\$\s*([\d.]+,\d{2})', row_text)
                                if len(values) >= 2:
                                    exam_value = parse_currency_value(values[1])
                                elif len(values) == 1:
                                    exam_value = parse_currency_value(values[0])
                            
                            if not exam_value or exam_value == Decimal('0'):
                                continue
                            
                            if exame_cell:
                                exam_name_clean = re.sub(r'\b\d{10}\b', '', exame_cell).strip()
                            else:
                                exam_name_clean = ""
                            
                            exam_name_mapped = map_simus_to_compulab_exam_name(exam_name_clean)
                            if exam_name_mapped != exam_name_clean:
                                exam_name = normalize_exam_name(exam_name_mapped)
                            else:
                                exam_name = normalize_exam_name(exam_name_clean)
                            
                            if not exam_name or len(exam_name) < 3:
                                if exam_code:
                                    exam_name = f"EXAME {exam_code}"
                                else:
                                    exam_name = "EXAME"
                            
                            patients[patient_name]['exams'].append({
                                'exam_name': exam_name,
                                'code': exam_code,
                                'value': exam_value
                            })
                            patients[patient_name]['total'] += exam_value
                
                # Liberar memória após cada batch
                gc.collect()
            
            if not patients:
                lines_all = _collect_simus_lines(pdf_file)
                
                candidate_patients = []
                if known_patient_names:
                    for name in known_patient_names:
                        tokens = normalize_name(name).split()
                        if tokens:
                            candidate_patients.append(tokens)
                    candidate_patients.sort(key=len, reverse=True)
                
                current_patient = None
                pending_exam_code = None
                
                for i, line in enumerate(lines_all):
                    line = line.strip()
                    if not line:
                        continue
                    
                    upper = line.upper()
                    if any(x in upper for x in ["SEQ.", "SEQ ", "RELATORIO", "COMPETENCIA", "PRESTADOR", "TOTAL (", "TOTAL E FRACOES", "PAGINA"]):
                        continue
                    
                    code_match = re.search(r'\b(\d{10})\b', line)
                    if code_match:
                        pending_exam_code = code_match.group(1)
                    elif re.match(r'^\(?(\d{10})\)?$', line.replace("(", "").replace(")", "")):
                        pending_exam_code = re.match(r'^\(?(\d{10})\)?$', line.replace("(", "").replace(")", "")).group(1)
                        continue
                    
                    values = re.findall(r'R\$\s*([\d.]+,\d{2})', line)
                    if not values:
                        if current_patient and pending_exam_code and re.match(r'^[A-ZÁÉÍÓÚÂÊÔÇ\s]+$', line):
                            continue
                        continue
                    
                    if len(values) >= 2:
                        exam_value = parse_currency_value(values[1])
                    elif len(values) == 1:
                        exam_value = parse_currency_value(values[0])
                    else:
                        continue
                    
                    if not exam_value or exam_value == Decimal('0'):
                        continue
                    
                    line_clean = line
                    for val in values:
                        line_clean = line_clean.replace(f"R${val}", "")
                    if pending_exam_code:
                        line_clean = re.sub(r'\b' + pending_exam_code + r'\b', '', line_clean)
                    line_clean = re.sub(r'\d{2}/\d{2}/\d{2,4}', '', line_clean)
                    line_clean = re.sub(r'REALIZADO.*?(\d{2}/\d{2}/\d{2,4})?', '', line_clean, flags=re.IGNORECASE)
                    line_clean = re.sub(r'\d+\s+\d+', '', line_clean)
                    
                    tokens = line_clean.split()
                    
                    patient_name = None
                    exam_start_idx = 0
                    
                    if candidate_patients:
                        normalized_tokens = [normalize_name(t) for t in tokens]
                        found_patient, start_idx = _find_patient_in_tokens(normalized_tokens, candidate_patients)
                        if found_patient:
                            patient_name = found_patient
                            exam_start_idx = start_idx
                            current_patient = patient_name
                    
                    if not patient_name:
                        seq_match = re.match(r'^\d+\s+\d+\s+REALIZADO', line)
                        if seq_match:
                            rest = re.sub(r'^\d+\s+\d+\s+REALIZADO\s+\d{2}/\d{2}/\d{4}\s*', '', line_clean)
                            rest_tokens = rest.split()
                            
                            if candidate_patients:
                                normalized_rest = [normalize_name(t) for t in rest_tokens]
                                found_patient, start_idx = _find_patient_in_tokens(normalized_rest, candidate_patients)
                                if found_patient:
                                    patient_name = found_patient
                                    exam_start_idx = start_idx
                                else:
                                    if len(rest_tokens) >= 3:
                                        potential_patient = normalize_name(" ".join(rest_tokens[:4]))
                                        if len(potential_patient.split()) >= 2:
                                            patient_name = potential_patient
                                            exam_start_idx = min(4, len(rest_tokens))
                            else:
                                if len(rest_tokens) >= 3:
                                    potential_patient = normalize_name(" ".join(rest_tokens[:4]))
                                    if len(potential_patient.split()) >= 2:
                                        patient_name = potential_patient
                                        exam_start_idx = min(4, len(rest_tokens))
                    
                    if not patient_name:
                        if current_patient:
                            patient_name = current_patient
                        else:
                            continue
                    
                    current_patient = patient_name
                    
                    exam_tokens = tokens[exam_start_idx:] if exam_start_idx < len(tokens) else []
                    exam_name_raw = " ".join(exam_tokens)
                    
                    exam_name_mapped = map_simus_to_compulab_exam_name(exam_name_raw)
                    if exam_name_mapped != exam_name_raw:
                        exam_name = normalize_exam_name(exam_name_mapped)
                    else:
                        exam_name = normalize_exam_name(exam_name_raw)
                    
                    if not exam_name or len(exam_name) < 3:
                        if pending_exam_code:
                            exam_name = f"EXAME {pending_exam_code}"
                        else:
                            exam_name = "EXAME"
                    
                    patients[patient_name]['exams'].append({
                        'exam_name': exam_name,
                        'code': pending_exam_code if pending_exam_code else '',
                        'value': exam_value
                    })
                    patients[patient_name]['total'] += exam_value
                    
                    pending_exam_code = None
                            
    except Exception as e:
        print(f"Erro ao processar SIMUS: {e}")
        return None, None, None, None
    
    return patients, total_value, sigtap_value, contratualizado_value


def generate_csvs_from_pdfs(compulab_pdf_bytes, simus_pdf_bytes, progress_callback: Optional[Callable[[int, str], None]] = None):
    """Gera CSVs a partir dos bytes dos PDFs
    
    Args:
        compulab_pdf_bytes: Bytes do PDF COMPULAB
        simus_pdf_bytes: Bytes do PDF SIMUS
        progress_callback: Função callback(percentage: int, stage: str) para reportar progresso
    """
    tmp_compulab_path = None
    tmp_simus_path = None
    
    try:
        # Estágio 1: Preparação (0-5%)
        if progress_callback:
            progress_callback(0, "Preparando arquivos...")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_compulab:
            tmp_compulab.write(compulab_pdf_bytes)
            tmp_compulab_path = tmp_compulab.name
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_simus:
            tmp_simus.write(simus_pdf_bytes)
            tmp_simus_path = tmp_simus.name
        
        # Estágio 2: Processando COMPULAB (5-45%)
        if progress_callback:
            progress_callback(5, "Processando COMPULAB...")
        
        def compulab_progress(percentage):
            # 5% a 45% para COMPULAB
            if progress_callback:
                progress = 5 + int(percentage * 0.4)
                progress_callback(progress, f"Processando COMPULAB... {percentage}%")
        
        compulab_patients, compulab_total = extract_compulab_patients(
            tmp_compulab_path, 
            progress_callback=compulab_progress if progress_callback else None
        )
        if compulab_patients is None:
            return None, None, False
        
        if progress_callback:
            progress_callback(45, "Organizando dados COMPULAB...")
        
        compulab_rows = []
        total_exams = sum(len(data['exams']) for data in compulab_patients.values())
        processed_exams = 0
        
        for patient_name, data in compulab_patients.items():
            for exam in data['exams']:
                compulab_rows.append({
                    'Paciente': patient_name,
                    'Nome_Exame': exam['exam_name'],
                    'Codigo_Exame': exam.get('code', ''),
                    'Valor': float(exam['value'])
                })
                processed_exams += 1
                if progress_callback and total_exams > 0:
                    exam_progress = int((processed_exams / total_exams) * 10)
                    progress_callback(45 + exam_progress, f"Organizando dados COMPULAB... {processed_exams}/{total_exams} exames")
        
        compulab_df = pd.DataFrame(compulab_rows)
        
        # Estágio 3: Processando SIMUS (55-90%)
        if progress_callback:
            progress_callback(55, "Processando SIMUS...")
        
        def simus_progress(page, total_pages):
            if total_pages > 0:
                percentage = int((page / total_pages) * 100)
                # 55% a 90% para SIMUS
                progress = 55 + int(percentage * 0.35)
                if progress_callback:
                    progress_callback(progress, f"Processando SIMUS... Página {page}/{total_pages}")
        
        simus_patients, simus_total, _, _ = extract_simus_patients(
            tmp_simus_path, 
            known_patient_names=list(compulab_patients.keys()),
            progress_callback=simus_progress if progress_callback else None
        )
        
        if simus_patients is None:
            return None, None, False
        
        if progress_callback:
            progress_callback(90, "Organizando dados SIMUS...")
        
        simus_rows = []
        total_simus_exams = sum(len(data['exams']) for data in simus_patients.values())
        processed_simus_exams = 0
        
        for patient_name, data in simus_patients.items():
            for exam in data['exams']:
                exam_name = exam['exam_name']
                simus_rows.append({
                    'Paciente': patient_name,
                    'Nome_Exame': exam_name,
                    'Codigo_Exame': exam.get('code', ''),
                    'Valor': float(exam['value'])
                })
                processed_simus_exams += 1
                if progress_callback and total_simus_exams > 0:
                    exam_progress = int((processed_simus_exams / total_simus_exams) * 5)
                    progress_callback(90 + exam_progress, f"Organizando dados SIMUS... {processed_simus_exams}/{total_simus_exams} exames")
        
        simus_df = pd.DataFrame(simus_rows)
        
        # Estágio 4: Gerando CSVs (95-98%)
        if progress_callback:
            progress_callback(95, "Gerando arquivos CSV...")
        
        compulab_csv = compulab_df.to_csv(
            index=False, sep=';', decimal=',', encoding='utf-8-sig'
        )
        
        if progress_callback:
            progress_callback(98, "Finalizando conversão...")
        
        simus_csv = simus_df.to_csv(
            index=False, sep=';', decimal=',', encoding='utf-8-sig'
        )
        
        if progress_callback:
            progress_callback(100, "Concluído")
        
        return compulab_csv, simus_csv, True
            
    except Exception as e:
        print(f"Erro ao gerar CSVs: {e}")
        if progress_callback:
            progress_callback(0, f"Erro: {str(e)}")
        return None, None, False
    finally:
        if tmp_compulab_path and os.path.exists(tmp_compulab_path):
            try:
                os.unlink(tmp_compulab_path)
            except:
                pass
        if tmp_simus_path and os.path.exists(tmp_simus_path):
            try:
                os.unlink(tmp_simus_path)
            except:
                pass


def load_from_csv(csv_content):
    """
    Carrega dados de um CSV de forma determinística
    Garante que os exames sejam ordenados consistentemente
    """
    try:
        import io
        df = pd.read_csv(io.StringIO(csv_content), sep=';', decimal=',', encoding='utf-8-sig')
        patients = defaultdict(lambda: {'exams': [], 'total': Decimal('0')})
        total_value = Decimal('0')
        
        # ORDENAR DataFrame antes de iterar para garantir ordem consistente
        # Ordenar por Paciente, Nome_Exame e Valor para garantir ordem determinística
        df = df.sort_values(by=['Paciente', 'Nome_Exame', 'Valor'], na_position='last')
        
        for _, row in df.iterrows():
            patient_name = normalize_name(str(row['Paciente']))
            exam_name = normalize_exam_name(str(row['Nome_Exame']))
            value = Decimal(str(row['Valor']))
            
            patients[patient_name]['exams'].append({
                'exam_name': exam_name,
                'code': str(row.get('Codigo_Exame', '')),
                'value': value
            })
            patients[patient_name]['total'] += value
            total_value += value
        
        # ORDENAR exames dentro de cada paciente para garantir consistência
        # Converter para dict ordenado (OrderedDict) ou garantir ordenação
        for patient_name in patients:
            patients[patient_name]['exams'].sort(key=lambda x: (x['exam_name'], x['value'], x['code']))
        
        return patients, total_value
    except Exception as e:
        print(f"Erro ao ler CSV: {e}")
        return None, None

