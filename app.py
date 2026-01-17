import streamlit as st
import pdfplumber
from decimal import Decimal
import re
from collections import defaultdict
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
import os

# Adicionar utils ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from utils.ui import apply_custom_css, render_header, render_footer, create_sidebar_menu, render_info_box
    from config import LAB_INFO, THEME_COLORS, MODULES
    UI_AVAILABLE = True
except ImportError:
    UI_AVAILABLE = False
    # Fallback se os módulos não estiverem disponíveis
    def apply_custom_css(): pass
    def render_header(): 
        st.title("📊 Análise de Faturamento - COMPULAB vs SIMUS")
    def render_footer(): pass
    def create_sidebar_menu(): return "📊 Análise de Faturamento"
    def render_info_box(title, content, icon="ℹ️", type="info"): 
        st.info(f"{icon} **{title}**: {content}")

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Configuração da página
if UI_AVAILABLE:
    page_title = f"{LAB_INFO['nome']} - Sistema de Administração"
else:
    page_title = "Biodiagnóstico - Sistema de Administração"

st.set_page_config(
    page_title=page_title,
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Aplicar CSS customizado
if UI_AVAILABLE:
    apply_custom_css()
    render_header()
else:
    st.title("📊 Análise de Faturamento - COMPULAB vs SIMUS")

st.markdown("---")

# Funções auxiliares
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
    # Remove espaços extras
    name = ' '.join(name.split())
    # Remove acentos básicos para comparação
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
    # Remove caracteres especiais comuns
    name = re.sub(r'[^\w\s]', '', name)
    return name

# Mapeamento completo de nomes de exames SIMUS para COMPULAB
# Formato: {nome_simus: nome_compulab}
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
    'CONTAGEM DE PLAQUETAS': 'CONTAGEM DE PLAQUETAS',
    
    # Outros
    'DOSAGEM DE CREATINOFOSFOQUINASE (CPK)': 'CREATINOFOSFOQUINASE',
    'DOSAGEM DE CREATINOFOSFOQUINASE CPK': 'CREATINOFOSFOQUINASE',
    'DOSAGEM DE LIPASE': 'LIPASE',
    'DOSAGEM DE AMILASE': 'AMILASE',
    'ANTIBIOGRAMA': 'ANTIBIOGRAMA',
    'PESQUISA LABORATORIAL DE ANTIGENOS DE HIV E/OU ANTICORPOS ANTI-HIV-1 OU ANTI-HIV-2': 'HIV 1/2',
    'PESQUISA LABORATORIAL DE ANTIGENOS DE HIV E OU ANTICORPOS ANTI-HIV-1 OU ANTI-HIV-2': 'HIV 1/2',
    'PESQUISA DE SANGUE OCULTO NAS FEZES': 'SANGUE OCULTO',
}

def map_simus_to_compulab_exam_name(simus_exam_name):
    """Mapeia nome do exame do SIMUS para o nome equivalente no COMPULAB"""
    if not simus_exam_name:
        return simus_exam_name
    
    # Limpar e normalizar o nome de entrada
    simus_clean = str(simus_exam_name).strip().upper()
    
    # Tentar match exato primeiro (com e sem normalização)
    for simus_key, compulab_value in EXAM_NAME_MAPPING.items():
        # Match exato (case-insensitive)
        if simus_key.upper() == simus_clean:
            return compulab_value
        # Match normalizado
        if normalize_exam_name(simus_key) == normalize_exam_name(simus_clean):
            return compulab_value
    
    # Tentar match parcial (contém) - mais flexível
    normalized_simus = normalize_exam_name(simus_clean)
    for simus_key, compulab_value in EXAM_NAME_MAPPING.items():
        normalized_key = normalize_exam_name(simus_key)
        # Verificar se um contém o outro (para pegar variações)
        if normalized_key in normalized_simus or normalized_simus in normalized_key:
            # Verificar se há pelo menos 3 palavras em comum (para evitar matches muito genéricos)
            key_words = set(normalized_key.split())
            simus_words = set(normalized_simus.split())
            common_words = key_words & simus_words
            if len(common_words) >= 2:  # Pelo menos 2 palavras em comum
                return compulab_value
    
    # Se não encontrou mapeamento, retorna o nome original normalizado
    return simus_exam_name

def normalize_exam_name(exam_name):
    """Normaliza nome do exame para comparação"""
    if not exam_name:
        return ""
    exam_name = str(exam_name).strip().upper()
    # Remove espaços extras
    exam_name = ' '.join(exam_name.split())
    # Remove acentos
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
    # Remove parênteses e conteúdo dentro
    exam_name = re.sub(r'\([^)]*\)', '', exam_name)
    # Remove caracteres especiais
    exam_name = re.sub(r'[^\w\s]', ' ', exam_name)
    # Remove espaços extras novamente
    exam_name = ' '.join(exam_name.split())
    return exam_name

def normalize_exam_name_for_comparison(exam_name):
    """Normaliza nome do exame removendo palavras genéricas para comparação inteligente"""
    if not exam_name:
        return ""
    
    # Primeiro normaliza normalmente
    normalized = normalize_exam_name(exam_name)
    
    # Palavras genéricas a remover (no início ou meio da frase)
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
    
    # Remove palavras genéricas
    for word in generic_words:
        # Remove do início
        pattern_start = r'^' + re.escape(word) + r'\s+'
        normalized = re.sub(pattern_start, '', normalized, flags=re.IGNORECASE)
        # Remove do meio (com espaço antes e depois)
        pattern_mid = r'\s+' + re.escape(word) + r'\s+'
        normalized = re.sub(pattern_mid, ' ', normalized, flags=re.IGNORECASE)
        # Remove do final
        pattern_end = r'\s+' + re.escape(word) + r'$'
        normalized = re.sub(pattern_end, '', normalized, flags=re.IGNORECASE)
    
    # Remove espaços extras novamente
    normalized = ' '.join(normalized.split())
    
    return normalized

def extract_key_terms(exam_name):
    """Extrai termos-chave importantes do nome do exame"""
    normalized = normalize_exam_name_for_comparison(exam_name)
    words = normalized.split()
    
    # Remove palavras muito curtas e genéricas
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
    
    # Se normalizados são idênticos
    if norm1 == norm2:
        return True
    
    # Mapeamento de exames equivalentes conhecidos
    exam_synonyms = {
        # Exames de urina
        'URINA': [
            'URINA', 'EAS', 'ELEMENTOS', 'SEDIMENTO', 'CARACTERES', 'FISICOS',
            'QUIMICOS', 'QUALITATIVO', 'QUANTITATIVO'
        ],
        # Exames de sangue
        'HEMOGRAMA': ['HEMOGRAMA', 'HEMATOLOGICO', 'COMPLETO', 'SERIE'],
        'GLICOSE': ['GLICOSE', 'GLICEMIA'],
        'TSH': ['TSH', 'TIREOTROFINA', 'TIREOESTIMULANTE'],
        'T4': ['T4', 'TIROXINA'],
        'T3': ['T3', 'TRIODOTIRONINA'],
    }
    
    # Verifica match por termos-chave importantes
    key_terms1 = extract_key_terms(exam_name1)
    key_terms2 = extract_key_terms(exam_name2)
    
    # Se um contém o outro completamente
    if key_terms1 and key_terms2:
        if key_terms1.issubset(key_terms2) or key_terms2.issubset(key_terms1):
            return True
    
    # Verifica se compartilham termos-chave importantes (especialmente para URINA)
    common_terms = key_terms1 & key_terms2
    
    # Casos especiais: exames de urina
    if 'URINA' in key_terms1 and 'URINA' in key_terms2:
        # Se ambos mencionam URINA e têm pelo menos um termo comum adicional
        if len(common_terms) >= 2:  # URINA + pelo menos 1 outro termo
            return True
        # Ou se ambos têm termos relacionados a urina
        urina_related = {'ELEMENTOS', 'SEDIMENTO', 'CARACTERES', 'FISICOS', 
                        'QUIMICOS', 'QUALITATIVO', 'QUANTITATIVO', 'EAS'}
        if (key_terms1 & urina_related) and (key_terms2 & urina_related):
            return True
    
    # Casos especiais: outros exames com sinônimos conhecidos
    for exam_type, synonyms in exam_synonyms.items():
        if exam_type == 'URINA':  # Já tratado acima
            continue
        if (key_terms1 & set(synonyms)) and (key_terms2 & set(synonyms)):
            # Se ambos têm termos relacionados ao mesmo tipo de exame
            return True
    
    # Se não encontrou match especial, usa lógica de subset original
    if norm1 and norm2:
        words1 = {w for w in norm1.split() if len(w) >= 3}
        words2 = {w for w in norm2.split() if len(w) >= 3}
        
        if not words1 or not words2:
            return False
        
        # Se todas as palavras de um estão no outro (ou vice-versa), é match
        if words1.issubset(words2) or words2.issubset(words1):
            return True
    
    return False

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
    # tenta achar o MAIOR sufixo que corresponde a um exame conhecido
    for i in range(len(tokens)):
        suffix_tokens = tokens[i:]
        exam_name = normalize_exam_name(" ".join(suffix_tokens))
        if exam_name in exam_name_set and i > 0:
            return tokens[:i], suffix_tokens
    # fallback: assume paciente é 3-4 palavras
    split_idx = min(4, max(2, len(tokens) - 1))
    return tokens[:split_idx], tokens[split_idx:]

# Extração de dados do COMPULAB
def extract_compulab_patients(pdf_file):
    """Extrai dados de pacientes do COMPULAB com separação por exame"""
    patients = defaultdict(lambda: {"exams": [], "total": Decimal("0")})
    total_value = Decimal("0")

    try:
        lines_all = _collect_compulab_lines(pdf_file)
        exam_name_set = _build_exam_name_set(lines_all)
        current_patient = None

        for line in lines_all:
            line = line.strip()
            if not line:
                continue
            if any(x in line.upper() for x in ["PAGINA", "SUBTOTAL:", "TOTAL:", "RELACAO DOS", "PERIODO", "SEQ NOME"]):
                continue

            # Linha que contém apenas o paciente (sem exame/código)
            header_match = re.match(r'^(\d+)\s+([A-ZÁÉÍÓÚÂÊÔÇ\s]+)$', line)
            if header_match and not re.search(r'\d{10}', line):
                current_patient = normalize_name(header_match.group(2))
                continue

            code_match = re.search(r'(\d{10})\s+\d+\s+([\d,]+)', line)
            if not code_match:
                # linha sem código não deve quebrar o paciente atual
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

        # tentar total geral
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
        st.error(f"Erro ao processar COMPULAB: {e}")
        import traceback
        st.error(traceback.format_exc())
        return None, None

    return patients, total_value

# Extração de dados do SIMUS
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
    """Coleta todas as linhas do PDF SIMUS"""
    lines_all = []
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            lines_all.extend(text.split("\n"))
    return lines_all

def extract_simus_patients(pdf_file, known_patient_names=None):
    """Extrai dados de pacientes do SIMUS usando tabelas do PDF"""
    patients = defaultdict(lambda: {'exams': [], 'total': Decimal('0')})
    total_value = Decimal('0')
    sigtap_value = None
    contratualizado_value = None
    
    try:
        with pdfplumber.open(pdf_file) as pdf:
            # Primeira página para pegar totais
            first_page = pdf.pages[0]
            first_text = first_page.extract_text()
            if first_text:
                pattern = r'R\$([\d.]+,\d{2})\s*\(SIGTAP\).*?R\$([\d.]+,\d{2})\s*\(Contratualizados\)'
                match = re.search(pattern, first_text, re.DOTALL)
                if match:
                    sigtap_value = parse_currency_value(match.group(1))
                    contratualizado_value = parse_currency_value(match.group(2))
                    total_value = contratualizado_value
            
            # Preparar candidatos de pacientes conhecidos
            candidate_patients = []
            if known_patient_names:
                for name in known_patient_names:
                    tokens = normalize_name(name).split()
                    if tokens:
                        candidate_patients.append(tokens)
                candidate_patients.sort(key=len, reverse=True)
            
            # Tentar extrair usando tabelas primeiro (mais confiável)
            for page in pdf.pages:
                tables = page.extract_tables()
                
                for table in tables:
                    if not table or len(table) < 2:
                        continue
                    
                    # Identificar colunas - procurar cabeçalho
                    header_row = None
                    for i, row in enumerate(table):
                        if row and any(cell and ('PACIENTE' in str(cell).upper() or 'EXAME' in str(cell).upper()) for cell in row if cell):
                            header_row = i
                            break
                    
                    if header_row is None:
                        continue
                    
                    # Identificar índices das colunas
                    header = table[header_row]
                    paciente_col = None
                    exame_col = None
                    valor_pago_col = None
                    codigo_col = None
                    
                    for idx, cell in enumerate(header):
                        if not cell:
                            continue
                        cell_upper = str(cell).upper()
                        if 'PACIENTE' in cell_upper and paciente_col is None:
                            paciente_col = idx
                        elif 'EXAME' in cell_upper and exame_col is None:
                            exame_col = idx
                        elif ('VALOR PAGO' in cell_upper or ('PAGO' in cell_upper and 'SUS' not in cell_upper)) and valor_pago_col is None:
                            valor_pago_col = idx
                        elif 'COD' in cell_upper or 'CÓD' in cell_upper:
                            codigo_col = idx
                    
                    # Processar linhas da tabela
                    for row in table[header_row + 1:]:
                        if not row or len(row) < max(paciente_col or 0, exame_col or 0, valor_pago_col or 0) + 1:
                            continue
                        
                        # Extrair paciente
                        paciente_cell = str(row[paciente_col]).strip() if paciente_col and len(row) > paciente_col and row[paciente_col] else ""
                        if not paciente_cell or paciente_cell.upper() in ['PACIENTE', 'TOTAL', 'TOTAL E FRACOES', '']:
                            continue
                        
                        patient_name = normalize_name(paciente_cell)
                        
                        # Extrair exame
                        exame_cell = str(row[exame_col]).strip() if exame_col and len(row) > exame_col and row[exame_col] else ""
                        
                        # Extrair código do exame (pode estar na coluna CÓD ou no nome do exame)
                        exam_code = ""
                        if codigo_col and len(row) > codigo_col and row[codigo_col]:
                            code_match = re.search(r'\b(\d{10})\b', str(row[codigo_col]))
                            if code_match:
                                exam_code = code_match.group(1)
                        
                        # Se não encontrou código na coluna, procurar no nome do exame
                        if not exam_code and exame_cell:
                            code_match = re.search(r'\b(\d{10})\b', exame_cell)
                            if code_match:
                                exam_code = code_match.group(1)
                        
                        # Extrair valor pago
                        exam_value = None
                        if valor_pago_col and len(row) > valor_pago_col and row[valor_pago_col]:
                            exam_value = parse_currency_value(str(row[valor_pago_col]))
                        
                        # Se não encontrou, procurar valores monetários na linha inteira
                        if not exam_value or exam_value == Decimal('0'):
                            row_text = ' '.join([str(cell) if cell else '' for cell in row])
                            values = re.findall(r'R\$\s*([\d.]+,\d{2})', row_text)
                            if len(values) >= 2:
                                exam_value = parse_currency_value(values[1])  # VALOR PAGO é geralmente o segundo
                            elif len(values) == 1:
                                exam_value = parse_currency_value(values[0])
                        
                        if not exam_value or exam_value == Decimal('0'):
                            continue
                        
                        # Processar nome do exame
                        if exame_cell:
                            # Remover código do nome do exame se estiver lá
                            exam_name_clean = re.sub(r'\b\d{10}\b', '', exame_cell).strip()
                            # Não remover parênteses ainda, pode conter informações importantes (ex: TSH)
                            # exam_name_clean = re.sub(r'\([^)]*\)', '', exam_name_clean).strip()
                        else:
                            exam_name_clean = ""
                        
                        # Aplicar mapeamento SIMUS -> COMPULAB ANTES de normalizar
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
                        
                        # Adicionar exame
                        patients[patient_name]['exams'].append({
                            'exam_name': exam_name,
                            'code': exam_code,
                            'value': exam_value
                        })
                        patients[patient_name]['total'] += exam_value
            
            # Se não extraiu nada das tabelas, usar método de linhas como fallback
            if not patients:
                # Coletar todas as linhas primeiro
                lines_all = _collect_simus_lines(pdf_file)
                
                # Preparar candidatos de pacientes conhecidos
                candidate_patients = []
                if known_patient_names:
                    for name in known_patient_names:
                        tokens = normalize_name(name).split()
                        if tokens:
                            candidate_patients.append(tokens)
                    candidate_patients.sort(key=len, reverse=True)
                
                current_patient = None
                pending_exam_code = None
                
                # Processar cada linha
                for i, line in enumerate(lines_all):
                    line = line.strip()
                    if not line:
                        continue
                    
                    upper = line.upper()
                    if any(x in upper for x in ["SEQ.", "SEQ ", "RELATORIO", "COMPETENCIA", "PRESTADOR", "TOTAL (", "TOTAL E FRACOES", "PAGINA"]):
                        continue
                    
                    # Procurar código de exame (10 dígitos) na linha
                    code_match = re.search(r'\b(\d{10})\b', line)
                    if code_match:
                        pending_exam_code = code_match.group(1)
                    elif re.match(r'^\(?(\d{10})\)?$', line.replace("(", "").replace(")", "")):
                        # Linha só com código entre parênteses
                        pending_exam_code = re.match(r'^\(?(\d{10})\)?$', line.replace("(", "").replace(")", "")).group(1)
                        continue
                    
                    # Procurar valores monetários (indicam linha de exame)
                    values = re.findall(r'R\$\s*([\d.]+,\d{2})', line)
                    if not values:
                        # Se não tem valores mas pode ser linha de exame (sem código ainda)
                        # Pode ser continuação de nome de exame
                        if current_patient and pending_exam_code and re.match(r'^[A-ZÁÉÍÓÚÂÊÔÇ\s]+$', line):
                            continue
                        continue
                    
                    # Extrair valor pago (geralmente segundo valor)
                    if len(values) >= 2:
                        exam_value = parse_currency_value(values[1])
                    elif len(values) == 1:
                        exam_value = parse_currency_value(values[0])
                    else:
                        continue
                    
                    if not exam_value or exam_value == Decimal('0'):
                        continue
                    
                    # Extrair paciente e exame da linha
                    # Remover valores, códigos, datas, status
                    line_clean = line
                    for val in values:
                        line_clean = line_clean.replace(f"R${val}", "")
                    if pending_exam_code:
                        line_clean = re.sub(r'\b' + pending_exam_code + r'\b', '', line_clean)
                    line_clean = re.sub(r'\d{2}/\d{2}/\d{2,4}', '', line_clean)
                    line_clean = re.sub(r'REALIZADO.*?(\d{2}/\d{2}/\d{2,4})?', '', line_clean, flags=re.IGNORECASE)
                    line_clean = re.sub(r'\d+\s+\d+', '', line_clean)  # Remover números de sequência
                    
                    tokens = line_clean.split()
                    
                    # Tentar encontrar paciente conhecido
                    patient_name = None
                    exam_start_idx = 0
                    
                    if candidate_patients:
                        normalized_tokens = [normalize_name(t) for t in tokens]
                        found_patient, start_idx = _find_patient_in_tokens(normalized_tokens, candidate_patients)
                        if found_patient:
                            patient_name = found_patient
                            exam_start_idx = start_idx
                            current_patient = patient_name
                    
                    # Se não encontrou paciente conhecido, tentar extrair manualmente
                    if not patient_name:
                        # Procurar padrão: números de sequência seguidos de nome de paciente
                        # Exemplo: "1 2 REALIZADO 15/01/2025 ADAIR MASSARO SILVA TIREOESTIMULANTE..."
                        seq_match = re.match(r'^\d+\s+\d+\s+REALIZADO', line)
                        if seq_match:
                            # Remover sequência e data
                            rest = re.sub(r'^\d+\s+\d+\s+REALIZADO\s+\d{2}/\d{2}/\d{4}\s*', '', line_clean)
                            rest_tokens = rest.split()
                            
                            # Tentar encontrar paciente conhecido novamente
                            if candidate_patients:
                                normalized_rest = [normalize_name(t) for t in rest_tokens]
                                found_patient, start_idx = _find_patient_in_tokens(normalized_rest, candidate_patients)
                                if found_patient:
                                    patient_name = found_patient
                                    exam_start_idx = start_idx
                                else:
                                    # Fallback: assumir que paciente são 3-4 primeiras palavras
                                    if len(rest_tokens) >= 3:
                                        potential_patient = normalize_name(" ".join(rest_tokens[:4]))
                                        if len(potential_patient.split()) >= 2:
                                            patient_name = potential_patient
                                            exam_start_idx = min(4, len(rest_tokens))
                            else:
                                # Sem candidatos: assumir paciente são 3-4 primeiras palavras
                                if len(rest_tokens) >= 3:
                                    potential_patient = normalize_name(" ".join(rest_tokens[:4]))
                                    if len(potential_patient.split()) >= 2:
                                        patient_name = potential_patient
                                        exam_start_idx = min(4, len(rest_tokens))
                    
                    # Se ainda não encontrou, usar paciente atual (continuação)
                    if not patient_name:
                        if current_patient:
                            patient_name = current_patient
                        else:
                            continue
                    
                    current_patient = patient_name
                    
                    # Extrair nome do exame
                    exam_tokens = tokens[exam_start_idx:] if exam_start_idx < len(tokens) else []
                    exam_name_raw = " ".join(exam_tokens)
                    
                    # Aplicar mapeamento de nomes SIMUS -> COMPULAB ANTES de normalizar
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
                    
                    # Adicionar exame
                    patients[patient_name]['exams'].append({
                        'exam_name': exam_name,
                        'code': pending_exam_code if pending_exam_code else '',
                        'value': exam_value
                    })
                    patients[patient_name]['total'] += exam_value
                    
                    # Reset código pendente
                    pending_exam_code = None
                            
    except Exception as e:
        st.error(f"Erro ao processar SIMUS: {e}")
        import traceback
        st.error(traceback.format_exc())
        return None, None, None, None
    
    return patients, total_value, sigtap_value, contratualizado_value

# Análise comparativa baseada em NOMES
def compare_patients(compulab_patients, simus_patients):
    """Compara pacientes entre COMPULAB e SIMUS usando APENAS NOMES"""
    results = {
        'missing_patients': [],  # Pacientes no COMPULAB mas não no SIMUS
        'missing_exams': [],  # Exames faltantes por paciente
        'value_divergences': []  # Divergências de valores
    }
    
    compulab_names = set(compulab_patients.keys())
    simus_names = set(simus_patients.keys())
    
    # Pacientes faltantes no SIMUS
    missing_in_simus = compulab_names - simus_names
    for patient in missing_in_simus:
        results['missing_patients'].append({
            'patient': patient,
            'exams_count': len(compulab_patients[patient]['exams']),
            'total_value': compulab_patients[patient]['total'],
            'exams': compulab_patients[patient]['exams']
        })
    
    # Comparar pacientes comuns
    common_patients = compulab_names & simus_names
    
    for patient in common_patients:
        compulab_exam_list = compulab_patients[patient]['exams']
        simus_exam_list = simus_patients[patient]['exams']
        
        # Criar cópia mutável da lista do SIMUS para marcar quais já foram usados
        simus_available = simus_exam_list.copy()
        simus_used_indices = set()
        
        # Agrupar exames por nome normalizado para comparação
        compulab_grouped = {}
        for exam in compulab_exam_list:
            norm_key = normalize_exam_name_for_comparison(exam['exam_name'])
            if norm_key not in compulab_grouped:
                compulab_grouped[norm_key] = []
            compulab_grouped[norm_key].append(exam)
        
        # Para cada grupo de exames do COMPULAB, encontrar correspondentes no SIMUS
        for comp_norm_key, comp_exams in compulab_grouped.items():
            simus_matches = []
            
            # Procurar matches no SIMUS
            for i, sim_exam in enumerate(simus_exam_list):
                if i in simus_used_indices:
                    continue
                sim_norm_key = normalize_exam_name_for_comparison(sim_exam['exam_name'])
                if exam_names_match(comp_norm_key, sim_norm_key):
                    simus_matches.append((i, sim_exam))
                    simus_used_indices.add(i)
            
            if not simus_matches:
                # Nenhum match encontrado - exames faltantes
                for exam in comp_exams:
                    results['missing_exams'].append({
                        'patient': patient,
                        'exam_name': exam['exam_name'],
                        'value': exam['value']
                    })
            else:
                # Comparar valores
                compulab_total = sum(ex['value'] for ex in comp_exams)
                simus_total = sum(ex['value'] for i, ex in simus_matches)
                
                if abs(compulab_total - simus_total) > Decimal('0.01'):
                    # Usa o nome mais completo para exibição
                    all_names = [ex['exam_name'] for ex in comp_exams] + [ex['exam_name'] for i, ex in simus_matches]
                    display_name = max(all_names, key=len)
                    results['value_divergences'].append({
                        'patient': patient,
                        'exam_name': display_name,
                        'compulab_value': compulab_total,
                        'simus_value': simus_total,
                        'difference': compulab_total - simus_total,
                        'compulab_count': len(comp_exams),
                        'simus_count': len(simus_matches)
                    })
    
    return results

def compute_difference_breakdown(compulab_total, simus_total, comparison_results):
    """Calcula a explicação da diferença total (COMPULAB - SIMUS)"""
    diff_total = compulab_total - simus_total
    missing_patients_total = sum(item['total_value'] for item in comparison_results['missing_patients'])
    missing_exams_total = sum(item['value'] for item in comparison_results['missing_exams'])
    divergences_total = sum(item['difference'] for item in comparison_results['value_divergences'])
    explained = missing_patients_total + missing_exams_total + divergences_total
    residual = diff_total - explained
    return {
        "diff_total": diff_total,
        "missing_patients_total": missing_patients_total,
        "missing_exams_total": missing_exams_total,
        "divergences_total": divergences_total,
        "explained_total": explained,
        "residual": residual,
    }

# Função para gerar CSV dos PDFs
def generate_csvs_from_pdfs(compulab_pdf_file, simus_pdf_file):
    """Gera CSVs a partir dos PDFs carregados"""
    import tempfile
    import os
    
    tmp_compulab_path = None
    tmp_simus_path = None
    
    try:
        # Salvar PDFs temporariamente
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_compulab:
            tmp_compulab.write(compulab_pdf_file.read())
            tmp_compulab_path = tmp_compulab.name
            compulab_pdf_file.seek(0)  # Reset file pointer
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_simus:
            tmp_simus.write(simus_pdf_file.read())
            tmp_simus_path = tmp_simus.name
            simus_pdf_file.seek(0)  # Reset file pointer
        
        # Extrair dados usando as funções do app
        compulab_patients, compulab_total = extract_compulab_patients(tmp_compulab_path)
        if compulab_patients is None:
            return None, None, False
        
        # Converter para DataFrame
        compulab_rows = []
        for patient_name, data in compulab_patients.items():
            for exam in data['exams']:
                compulab_rows.append({
                    'Paciente': patient_name,
                    'Nome_Exame': exam['exam_name'],
                    'Codigo_Exame': exam.get('code', ''),
                    'Valor': float(exam['value'])
                })
        
        compulab_df = pd.DataFrame(compulab_rows)
        
        # Extrair SIMUS
        simus_patients, simus_total, _, _ = extract_simus_patients(
            tmp_simus_path, 
            known_patient_names=list(compulab_patients.keys())
        )
        
        if simus_patients is None:
            return None, None, False
        
        # Converter para DataFrame - aplicar mapeamento de nomes
        simus_rows = []
        for patient_name, data in simus_patients.items():
            for exam in data['exams']:
                # O nome já deve estar mapeado pela função extract_simus_patients
                # mas garantimos que está normalizado
                exam_name = exam['exam_name']
                simus_rows.append({
                    'Paciente': patient_name,
                    'Nome_Exame': exam_name,  # Já mapeado para formato COMPULAB
                    'Codigo_Exame': exam.get('code', ''),
                    'Valor': float(exam['value'])
                })
        
        simus_df = pd.DataFrame(simus_rows)
        
        # Salvar CSVs em memória
        compulab_csv_bytes = compulab_df.to_csv(
            index=False, sep=';', decimal=',', encoding='utf-8-sig'
        ).encode('utf-8-sig')
        
        simus_csv_bytes = simus_df.to_csv(
            index=False, sep=';', decimal=',', encoding='utf-8-sig'
        ).encode('utf-8-sig')
        
        return compulab_csv_bytes, simus_csv_bytes, True
            
    except Exception as e:
        raise e
    finally:
        # Limpar arquivos temporários
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

# Função para carregar dados de CSV
def load_from_csv(csv_file):
    """Carrega dados de um CSV"""
    try:
        df = pd.read_csv(csv_file, sep=';', decimal=',', encoding='utf-8-sig')
        patients = defaultdict(lambda: {'exams': [], 'total': Decimal('0')})
        total_value = Decimal('0')
        
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
        
        return patients, total_value
    except Exception as e:
        st.error(f"Erro ao ler CSV: {e}")
        return None, None

# ═══════════════════════════════════════════════════════════════════════════════
# INTERFACE STREAMLIT - NAVEGAÇÃO POR ABAS
# ═══════════════════════════════════════════════════════════════════════════════

# Sidebar - Menu de Navegação
if UI_AVAILABLE:
    st.sidebar.markdown(f"### 🧬 {LAB_INFO['nome_curto']}")
    st.sidebar.markdown(f"*{LAB_INFO['sistema']}*")
else:
    st.sidebar.markdown("### 🧬 Biodiagnóstico")
    st.sidebar.markdown("*Sistema de Administração*")

st.sidebar.markdown("---")

# Menu de navegação principal
st.sidebar.markdown("### 📋 Menu Principal")
pagina_selecionada = st.sidebar.radio(
    "Selecione uma função:",
    ["🔄 Conversor PDF → CSV", "📊 Análise COMPULAB x SIMUS"],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")

# ═══════════════════════════════════════════════════════════════════════════════
# PÁGINA 1: CONVERSOR PDF → CSV
# ═══════════════════════════════════════════════════════════════════════════════
if pagina_selecionada == "🔄 Conversor PDF → CSV":
    st.header("🔄 Conversor PDF → CSV")
    st.markdown("**Converta seus PDFs COMPULAB e SIMUS para formato CSV com nomes de exames padronizados!**")
    
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, rgba(139, 195, 74, 0.1) 0%, rgba(27, 94, 32, 0.1) 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #8BC34A;
        margin-bottom: 2rem;
    ">
        <h4 style="margin: 0 0 0.5rem 0; color: #1B5E20;">✨ O que esta ferramenta faz:</h4>
        <ul style="margin: 0; color: #558B2F;">
            <li>✅ Extrai dados dos PDFs de faturamento</li>
            <li>✅ Padroniza nomes de exames (SIMUS → COMPULAB)</li>
            <li>✅ Normaliza nomes de pacientes</li>
            <li>✅ Gera CSVs prontos para análise ou arquivamento</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📄 PDF COMPULAB")
        compulab_pdf_conv = st.file_uploader(
            "Selecione o PDF do COMPULAB",
            type=['pdf'],
            key="compulab_conv_page",
            help="Faça upload do PDF COMPULAB para converter"
        )
        if compulab_pdf_conv:
            st.success(f"✅ {compulab_pdf_conv.name}")
    
    with col2:
        st.subheader("📄 PDF SIMUS")
        simus_pdf_conv = st.file_uploader(
            "Selecione o PDF do SIMUS",
            type=['pdf'],
            key="simus_conv_page",
            help="Faça upload do PDF SIMUS para converter"
        )
        if simus_pdf_conv:
            st.success(f"✅ {simus_pdf_conv.name}")
    
    st.markdown("---")
    
    if compulab_pdf_conv and simus_pdf_conv:
        if st.button("🔄 Converter PDFs para CSV", type="primary", use_container_width=True):
            with st.spinner("🔄 Convertendo PDFs para CSV... Isso pode levar alguns segundos."):
                try:
                    compulab_csv, simus_csv, success = generate_csvs_from_pdfs(compulab_pdf_conv, simus_pdf_conv)
                    
                    if success:
                        st.success("✅ Conversão concluída com sucesso!")
                        
                        st.markdown("""
                        <div style="
                            background: #E8F5E9;
                            padding: 1rem;
                            border-radius: 8px;
                            margin: 1rem 0;
                        ">
                            <p style="margin: 0; color: #2E7D32;">
                                💡 <strong>Os nomes de exames do SIMUS foram padronizados para corresponder ao formato COMPULAB!</strong>
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.download_button(
                                label="📥 Download COMPULAB.csv",
                                data=compulab_csv,
                                file_name="compulab_data.csv",
                                mime="text/csv",
                                use_container_width=True
                            )
                        
                        with col2:
                            st.download_button(
                                label="📥 Download SIMUS.csv",
                                data=simus_csv,
                                file_name="simus_data.csv",
                                mime="text/csv",
                                use_container_width=True
                            )
                        
                        st.info("💡 **Próximo passo:** Vá para a aba '📊 Análise COMPULAB x SIMUS' e use os CSVs gerados para análise mais rápida!")
                    else:
                        st.error("❌ Erro ao converter PDFs. Verifique se os arquivos estão corretos.")
                        
                except Exception as e:
                    st.error(f"❌ Erro ao converter: {str(e)}")
                    import traceback
                    with st.expander("🔍 Detalhes do erro"):
                        st.code(traceback.format_exc())
    else:
        st.info("👆 Faça upload dos dois PDFs acima para começar a conversão.")
    
    # Dicas de uso
    with st.expander("💡 Dicas de Uso"):
        st.markdown("""
        **📋 Formatos Aceitos:**
        - PDFs do sistema COMPULAB (faturamento)
        - PDFs do sistema SIMUS (contratualizado)
        
        **⚡ Benefícios do CSV:**
        - Processamento muito mais rápido na análise
        - Pode ser aberto no Excel para verificação
        - Ideal para arquivamento e backup
        
        **🔄 Mapeamento de Exames:**
        Os nomes de exames do SIMUS são automaticamente convertidos para o padrão COMPULAB.
        Exemplo: "DOSAGEM DE GLICOSE" → "GLICOSE"
        """)

# ═══════════════════════════════════════════════════════════════════════════════
# PÁGINA 2: ANÁLISE COMPULAB x SIMUS
# ═══════════════════════════════════════════════════════════════════════════════
elif pagina_selecionada == "📊 Análise COMPULAB x SIMUS":
    st.header("📊 Análise de Faturamento COMPULAB x SIMUS")
    st.markdown("**Compare os dados de faturamento e identifique divergências**")
    
    # Sidebar para upload de arquivos (específico desta página)
    st.sidebar.markdown("### 📁 Arquivos para Análise")
    
    compulab_file = st.sidebar.file_uploader(
        "COMPULAB (PDF ou CSV)",
        type=['pdf', 'csv'],
        help="Upload do arquivo COMPULAB (PDF ou CSV)",
        key="compulab_analysis"
    )
    
    simus_file = st.sidebar.file_uploader(
        "SIMUS (PDF ou CSV)",
        type=['pdf', 'csv'],
        help="Upload do arquivo SIMUS (PDF ou CSV)",
        key="simus_analysis"
    )
    
    st.sidebar.markdown("---")
    
    # Configuração da API do Gemini
    st.sidebar.markdown("### 🤖 Análise por IA")
    
    # Tentar carregar API key dos secrets do Streamlit Cloud primeiro
    default_api_key = ""
    try:
        default_api_key = st.secrets.get("GEMINI_API_KEY", "")
    except:
        pass
    
    gemini_api_key = st.sidebar.text_input(
        "🔑 Gemini API Key",
        type="password",
        value=default_api_key,
        help="Cole sua chave da API do Google Gemini aqui. Obtenha em: https://makersuite.google.com/app/apikey"
    )
    
    if gemini_api_key:
        st.sidebar.success("✅ API Key configurada!")
        if GEMINI_AVAILABLE:
            try:
                genai.configure(api_key=gemini_api_key)
            except Exception as e:
                st.sidebar.error(f"Erro ao configurar API: {str(e)}")
    else:
        st.sidebar.caption("Configure para usar análise por IA")
    
    if not GEMINI_AVAILABLE:
        st.sidebar.warning("⚠️ google-generativeai não instalada")
    
    st.sidebar.markdown("---")
    
    # Botão de análise
    analyze_button = st.sidebar.button("🔍 Analisar Faturamento", type="primary", use_container_width=True)
    
    # Processar análise quando botão for clicado
    if analyze_button and compulab_file and simus_file:
        with st.spinner("Processando arquivos e extraindo dados dos pacientes..."):
            # Detectar tipo de arquivo COMPULAB
            compulab_is_pdf = compulab_file.type == "application/pdf"
            if compulab_is_pdf:
                compulab_patients, compulab_total = extract_compulab_patients(compulab_file)
            else:
                compulab_patients, compulab_total = load_from_csv(compulab_file)
            
            # Detectar tipo de arquivo SIMUS
            simus_is_pdf = simus_file.type == "application/pdf"
            if simus_is_pdf:
                simus_patients, simus_total, sigtap_val, contratualizado_val = extract_simus_patients(
                    simus_file, known_patient_names=list(compulab_patients.keys()) if compulab_patients else None
                )
            else:
                simus_patients, simus_total = load_from_csv(simus_file)
                sigtap_val = None
                contratualizado_val = None
            
            if compulab_patients is None or simus_patients is None:
                st.error("Erro ao processar os arquivos. Verifique se os arquivos estão corretos.")
            else:
                # Comparar
                comparison_results = compare_patients(compulab_patients, simus_patients)
                breakdown = compute_difference_breakdown(compulab_total, simus_total, comparison_results)
                
                # Armazenar na sessão
                st.session_state['compulab_patients'] = compulab_patients
                st.session_state['compulab_total'] = compulab_total
                st.session_state['compulab_count'] = len(compulab_patients)
                st.session_state['simus_patients'] = simus_patients
                st.session_state['simus_total'] = simus_total
                st.session_state['simus_count'] = len(simus_patients)
                st.session_state['sigtap_val'] = sigtap_val
                st.session_state['contratualizado_val'] = contratualizado_val
                st.session_state['comparison_results'] = comparison_results
                st.session_state['difference_breakdown'] = breakdown
                
                st.success("✅ Análise concluída!")
                st.rerun()
    
    # Exibir resultados (dentro da página de análise)
    if 'comparison_results' in st.session_state:
        st.header("📈 Resumo da Análise")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "COMPULAB Total",
                f"R$ {st.session_state['compulab_total']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
            )
            st.caption(f"{st.session_state.get('compulab_count', 0)} pacientes")
        
        with col2:
            st.metric(
                "SIMUS Contratualizado",
                f"R$ {st.session_state['simus_total']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
            )
            st.caption(f"{st.session_state.get('simus_count', 0)} pacientes")
        
        with col3:
            difference = st.session_state['compulab_total'] - st.session_state['simus_total']
            diff_percent = (difference / st.session_state['simus_total'] * 100) if st.session_state['simus_total'] > 0 else 0
            st.metric(
                "Diferença",
                f"R$ {difference:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
                delta=f"{diff_percent:.2f}%"
            )
        
        with col4:
            missing_exams_count = len(st.session_state['comparison_results']['missing_exams'])
            st.metric(
                "Exames Faltantes",
                missing_exams_count,
                delta="no SIMUS"
            )
        
        if st.session_state.get('sigtap_val') and st.session_state.get('contratualizado_val'):
            st.info(f"📋 SIMUS - SIGTAP: R$ {st.session_state['sigtap_val']:,.2f} | Contratualizado: R$ {st.session_state['contratualizado_val']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))

        # Explicação da diferença total
        st.subheader("🧭 Por que existe essa diferença?")
        breakdown = st.session_state.get('difference_breakdown')
        if breakdown:
            col_a, col_b, col_c, col_d, col_e = st.columns(5)
            with col_a:
                st.metric(
                    "Pacientes faltantes",
                    f"R$ {breakdown['missing_patients_total']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
                )
            with col_b:
                st.metric(
                    "Exames faltantes",
                    f"R$ {breakdown['missing_exams_total']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
                )
            with col_c:
                st.metric(
                    "Divergências",
                    f"R$ {breakdown['divergences_total']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
                )
            with col_d:
                st.metric(
                    "Total explicado",
                    f"R$ {breakdown['explained_total']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
                )
            with col_e:
                st.metric(
                    "Diferença residual",
                    f"R$ {breakdown['residual']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
                )

            st.caption(
                "A diferença total (COMPULAB - SIMUS) é explicada pela soma: "
                "pacientes faltantes + exames faltantes + divergências de valores. "
                "A diferença residual indica itens não classificados (normalização ou extração)."
            )
        
        st.markdown("---")
        
        # Análise detalhada
        st.header("🔍 Análise Detalhada por Paciente")
        
        tab1, tab2, tab3, tab4 = st.tabs([
            "⚠️ Exames Faltantes", 
            "💰 Divergências de Valores",
            "📄 Relatório Completo",
            "🤖 Análise por IA"
        ])
        
        with tab1:
            st.subheader("Exames Faltantes no SIMUS (por Paciente)")
            
            missing_exams = st.session_state['comparison_results']['missing_exams']
            
            if missing_exams:
                st.warning(f"⚠️ **{len(missing_exams)} exame(s) encontrado(s) no COMPULAB mas não cadastrados no SIMUS**")
                
                # Agrupar por paciente
                exams_by_patient = defaultdict(list)
                for item in missing_exams:
                    exams_by_patient[item['patient']].append(item)

                # Agrupar por exame (visão geral)
                exams_by_name = defaultdict(list)
                for item in missing_exams:
                    exams_by_name[item['exam_name']].append(item)
                
                # Tabela resumo
                summary_data = []
                for patient, exams in exams_by_patient.items():
                    total_val = sum(ex['value'] for ex in exams)
                    summary_data.append({
                        'Paciente': patient,
                        'Exames Faltantes': len(exams),
                        'Valor Total': float(total_val)
                    })
                
                df_summary = pd.DataFrame(summary_data)
                df_summary = df_summary.sort_values('Exames Faltantes', ascending=False)
                st.dataframe(df_summary, use_container_width=True, hide_index=True)

                # Resumo por exame
                st.subheader("Resumo por Exame Faltante")
                exam_summary = []
                for exam_name, exams in exams_by_name.items():
                    total_val = sum(ex['value'] for ex in exams)
                    exam_summary.append({
                        'Exame': exam_name,
                        'Ocorrências': len(exams),
                        'Valor Total': float(total_val)
                    })
                df_exam_summary = pd.DataFrame(exam_summary)
                df_exam_summary = df_exam_summary.sort_values('Ocorrências', ascending=False)
                st.dataframe(df_exam_summary, use_container_width=True, hide_index=True)
                
                # Detalhamento
                st.subheader("Detalhamento por Paciente")
                
                for patient, exams in sorted(exams_by_patient.items()):
                    with st.expander(f"👤 {patient} - {len(exams)} exame(s) faltante(s)"):
                        exam_data = []
                        for exam in exams:
                            exam_data.append({
                                'Nome do Exame': exam['exam_name'],
                                'Valor': f"R$ {exam['value']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
                            })
                        df_exams = pd.DataFrame(exam_data)
                        st.dataframe(df_exams, use_container_width=True, hide_index=True)
            else:
                st.success("✅ Todos os exames do COMPULAB estão cadastrados no SIMUS!")

        with tab2:
            st.subheader("Divergências de Valores (por Paciente e Exame)")
            
            divergences = st.session_state['comparison_results']['value_divergences']
            
            if divergences:
                st.warning(f"⚠️ **{len(divergences)} divergência(s) de valor encontrada(s)**")
                
                # Tabela completa
                div_data = []
                total_diff = Decimal('0')
                
                for div in divergences:
                    div_data.append({
                        'Paciente': div['patient'],
                        'Nome do Exame': div['exam_name'],
                        'COMPULAB': f"R$ {div['compulab_value']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
                        'SIMUS': f"R$ {div['simus_value']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
                        'Diferença': f"R$ {div['difference']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
                        'Qtd COMPULAB': div.get('compulab_count', 1),
                        'Qtd SIMUS': div.get('simus_count', 1)
                    })
                    total_diff += div['difference']
                
                df_div = pd.DataFrame(div_data)
                df_div = df_div.sort_values('Paciente')
                st.dataframe(df_div, use_container_width=True, hide_index=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(
                        "Total de Divergências",
                        len(divergences)
                    )
                with col2:
                    st.metric(
                        "Diferença Total",
                        f"R$ {total_diff:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
                    )
                
                # Gráfico
                if len(divergences) > 0:
                    st.subheader("Gráfico de Divergências")
                    div_by_patient = defaultdict(lambda: {'count': 0, 'total_diff': Decimal('0')})
                    for div in divergences:
                        div_by_patient[div['patient']]['count'] += 1
                        div_by_patient[div['patient']]['total_diff'] += div['difference']
                
                    chart_data = pd.DataFrame([
                        {'Paciente': p, 'Divergências': d['count'], 'Diferença Total': float(d['total_diff'])}
                        for p, d in div_by_patient.items()
                    ])
                    chart_data = chart_data.sort_values('Divergências', ascending=False).head(20)
                    
                    fig = px.bar(
                        chart_data,
                        x='Paciente',
                        y='Divergências',
                        title="Top 20 Pacientes com Mais Divergências",
                        labels={'Divergências': 'Quantidade de Divergências'}
                    )
                    fig.update_xaxes(tickangle=45)
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.success("✅ Não há divergências de valores entre COMPULAB e SIMUS!")
        
        with tab3:
            st.subheader("Relatório Completo")
            
            # Gerar relatório
            report = f"""RELATÓRIO DE ANÁLISE - COMPULAB vs SIMUS
Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

═══════════════════════════════════════════════════════════════════════════
RESUMO GERAL
═══════════════════════════════════════════════════════════════════════════
COMPULAB Total: R$ {st.session_state['compulab_total']:,.2f}
SIMUS Contratualizado: R$ {st.session_state['simus_total']:,.2f}
Diferença: R$ {st.session_state['compulab_total'] - st.session_state['simus_total']:,.2f}

Pacientes no COMPULAB: {st.session_state.get('compulab_count', 0)}
Pacientes no SIMUS: {st.session_state.get('simus_count', 0)}
Pacientes faltantes: {len(st.session_state['comparison_results']['missing_patients'])}

═══════════════════════════════════════════════════════════════════════════
EXPLICAÇÃO DA DIFERENÇA TOTAL
═══════════════════════════════════════════════════════════════════════════
Pacientes faltantes (total): R$ {st.session_state['difference_breakdown']['missing_patients_total']:,.2f}
Exames faltantes (total):   R$ {st.session_state['difference_breakdown']['missing_exams_total']:,.2f}
Divergências (total):       R$ {st.session_state['difference_breakdown']['divergences_total']:,.2f}
Total explicado:            R$ {st.session_state['difference_breakdown']['explained_total']:,.2f}
Diferença residual:         R$ {st.session_state['difference_breakdown']['residual']:,.2f}

═══════════════════════════════════════════════════════════════════════════
1. EXAMES FALTANTES NO SIMUS
═══════════════════════════════════════════════════════════════════════════
Total: {len(st.session_state['comparison_results']['missing_exams'])} exame(s)
"""

            report += f"\n═══════════════════════════════════════════════════════════════════════════\n"
            report += f"1. EXAMES FALTANTES NO SIMUS\n"
            report += f"═══════════════════════════════════════════════════════════════════════════\n"
            report += f"Total: {len(st.session_state['comparison_results']['missing_exams'])} exame(s)\n\n"
            
            for item in st.session_state['comparison_results']['missing_exams']:
                report += f"Paciente: {item['patient']}\n"
                report += f"  Exame: {item['exam_name']}\n"
                report += f"  Valor: R$ {item['value']:,.2f}\n\n"
            
            report += f"\n═══════════════════════════════════════════════════════════════════════════\n"
            report += f"2. DIVERGÊNCIAS DE VALORES\n"
            report += f"═══════════════════════════════════════════════════════════════════════════\n"
            report += f"Total: {len(st.session_state['comparison_results']['value_divergences'])} divergência(s)\n\n"
            
            for item in st.session_state['comparison_results']['value_divergences']:
                report += f"Paciente: {item['patient']}\n"
                report += f"  Exame: {item['exam_name']}\n"
                report += f"  COMPULAB: R$ {item['compulab_value']:,.2f} (Qtd: {item.get('compulab_count', 1)})\n"
                report += f"  SIMUS: R$ {item['simus_value']:,.2f} (Qtd: {item.get('simus_count', 1)})\n"
                report += f"  Diferença: R$ {item['difference']:,.2f}\n\n"
            
            st.text_area("Relatório", report, height=400)
            
            # Download
            st.download_button(
                label="📥 Download Relatório (TXT)",
                data=report,
                file_name=f"relatorio_pacientes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
            
            # Exportar para CSV
            if st.session_state['comparison_results']['value_divergences']:
                df_export = pd.DataFrame(st.session_state['comparison_results']['value_divergences'])
                csv = df_export.to_csv(index=False, sep=';', decimal=',')
                st.download_button(
                    label="📥 Download Divergências (CSV)",
                    data=csv,
                    file_name=f"divergencias_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        
        with tab4:
            st.subheader("🤖 Análise Inteligente por IA (Gemini)")
            
            if not GEMINI_AVAILABLE:
                st.error("❌ Biblioteca google-generativeai não está instalada.")
                st.code("pip install google-generativeai")
                st.stop()
            
            if not gemini_api_key:
                st.warning("⚠️ Configure sua API Key do Gemini na barra lateral para usar esta funcionalidade.")
                st.info("""
                **Como obter sua API Key:**
                1. Acesse: https://makersuite.google.com/app/apikey
                2. Faça login com sua conta Google
                3. Clique em "Create API Key"
                4. Copie a chave e cole na barra lateral
                """)
                st.stop()
            
            # Botão para gerar análise por IA
            if st.button("🤖 Gerar Análise por IA", type="primary", use_container_width=True):
                with st.spinner("🤖 Analisando dados com Gemini AI... Isso pode levar alguns segundos."):
                    try:
                        # Preparar dados para a IA
                        compulab_patients = st.session_state.get('compulab_patients', {})
                        simus_patients = st.session_state.get('simus_patients', {})
                        comparison_results = st.session_state.get('comparison_results', {})
                        breakdown = st.session_state.get('difference_breakdown', {})
                        
                        # Criar resumo dos dados
                        summary_data = f"""
RESUMO DA ANÁLISE COMPULAB vs SIMUS:

Totais:
- COMPULAB: R$ {st.session_state.get('compulab_total', 0):,.2f}
- SIMUS: R$ {st.session_state.get('simus_total', 0):,.2f}
- Diferença: R$ {st.session_state.get('compulab_total', 0) - st.session_state.get('simus_total', 0):,.2f}

Pacientes:
- COMPULAB: {st.session_state.get('compulab_count', 0)} pacientes
- SIMUS: {st.session_state.get('simus_count', 0)} pacientes
- Pacientes faltantes no SIMUS: {len(comparison_results.get('missing_patients', []))}

Exames Faltantes: {len(comparison_results.get('missing_exams', []))} exame(s)
Divergências de Valores: {len(comparison_results.get('value_divergences', []))} divergência(s)

Breakdown da Diferença:
- Pacientes faltantes: R$ {breakdown.get('missing_patients_total', 0):,.2f}
- Exames faltantes: R$ {breakdown.get('missing_exams_total', 0):,.2f}
- Divergências: R$ {breakdown.get('divergences_total', 0):,.2f}
- Total explicado: R$ {breakdown.get('explained_total', 0):,.2f}
- Diferença residual: R$ {breakdown.get('residual', 0):,.2f}
"""
                        
                        # Adicionar exemplos de exames faltantes
                        missing_exams = comparison_results.get('missing_exams', [])
                        if missing_exams:
                            summary_data += "\n\nExemplos de Exames Faltantes (primeiros 10):\n"
                            for i, exam in enumerate(missing_exams[:10], 1):
                                summary_data += f"{i}. Paciente: {exam['patient']} | Exame: {exam['exam_name']} | Valor: R$ {exam['value']:,.2f}\n"
                        
                        # Adicionar exemplos de divergências
                        divergences = comparison_results.get('value_divergences', [])
                        if divergences:
                            summary_data += "\n\nExemplos de Divergências de Valores (primeiros 10):\n"
                            for i, div in enumerate(divergences[:10], 1):
                                summary_data += f"{i}. Paciente: {div['patient']} | Exame: {div['exam_name']} | COMPULAB: R$ {div['compulab_value']:,.2f} | SIMUS: R$ {div['simus_value']:,.2f} | Diferença: R$ {div['difference']:,.2f}\n"
                        
                        # Prompt para a IA
                        prompt = f"""Você é um especialista em análise de faturamento médico/laboratorial. 

Analise os seguintes dados de comparação entre COMPULAB (sistema de faturamento) e SIMUS (sistema de pagamento):

{summary_data}

Forneça uma análise detalhada e acionável com:
1. **Resumo Executivo**: Principais pontos que explicam a diferença entre os valores
2. **Principais Causas**: Identifique os 3-5 principais motivos para as divergências
3. **Recomendações**: Sugestões práticas para resolver os problemas identificados
4. **Pontos de Atenção**: Itens que precisam de verificação manual imediata
5. **Impacto Financeiro**: Avaliação do impacto de cada tipo de divergência

Seja específico, prático e use linguagem profissional mas acessível. Responda em português brasileiro."""
                        
                        # Configurar modelo Gemini
                        model = None
                        try:
                            model = genai.GenerativeModel('gemini-1.5-flash')
                        except Exception as e1:
                            try:
                                model = genai.GenerativeModel('gemini-1.5-pro')
                            except Exception as e2:
                                raise Exception(f"Erro ao configurar modelo Gemini: {str(e1)} | {str(e2)}")
                        
                        # Gerar resposta
                        response = model.generate_content(prompt)
                        ai_analysis = response.text
                        
                        # Exibir análise
                        st.markdown("### 📊 Análise Gerada pela IA")
                        st.markdown(ai_analysis)
                        
                        # Botão para download
                        st.download_button(
                            label="📥 Download Análise IA (TXT)",
                            data=f"ANÁLISE POR IA - COMPULAB vs SIMUS\n{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n{'='*80}\n\n{ai_analysis}",
                            file_name=f"analise_ia_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                            mime="text/plain"
                        )
                        
                    except Exception as e:
                        st.error(f"❌ Erro ao gerar análise por IA: {str(e)}")
                        st.info("Verifique se sua API Key está correta e se você tem créditos disponíveis na API do Gemini.")
    
    # Mensagem inicial quando não há análise
    else:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, rgba(139, 195, 74, 0.1) 0%, rgba(27, 94, 32, 0.1) 100%);
            padding: 2rem;
            border-radius: 16px;
            text-align: center;
            margin: 2rem 0;
        ">
            <h3 style="color: #1B5E20; margin-bottom: 1rem;">👋 Bem-vindo à Análise de Faturamento</h3>
            <p style="color: #558B2F; margin-bottom: 1.5rem;">
                Faça upload dos arquivos COMPULAB e SIMUS na barra lateral para começar a análise.
            </p>
            <p style="color: #689F38; font-size: 0.9rem;">
                💡 <strong>Dica:</strong> Use arquivos CSV para análise mais rápida!
            </p>
        </div>
        """, unsafe_allow_html=True)

# Rodapé
if UI_AVAILABLE:
    render_footer()
else:
    st.markdown("---")
    st.markdown("**Análise de Faturamento por Paciente e Exame - Laboratório Biodiagnóstico vs SIMUS**")
