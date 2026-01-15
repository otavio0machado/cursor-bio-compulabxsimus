import streamlit as st
import pdfplumber
from decimal import Decimal
import re
from collections import defaultdict
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Análise de Faturamento - COMPULAB vs SIMUS",
    page_icon="📊",
    layout="wide"
)

# Título principal
st.title("📊 Análise de Faturamento - COMPULAB vs SIMUS")
st.markdown("**Análise por Paciente e Exame - Identificação de Divergências**")
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

def extract_simus_patients(pdf_file, known_patient_names=None):
    """Extrai dados de pacientes do SIMUS a partir das linhas do PDF"""
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
                match = re.search(pattern, first_text)
                if match:
                    sigtap_value = parse_currency_value(match.group(1))
                    contratualizado_value = parse_currency_value(match.group(2))
                    total_value = contratualizado_value
            
            # Preparar candidatos de pacientes
            candidate_patients = []
            if known_patient_names:
                for name in known_patient_names:
                    tokens = normalize_name(name).split()
                    if tokens:
                        candidate_patients.append(tokens)
                candidate_patients.sort(key=len, reverse=True)

            pending_exam_prefix = ""
            pending_code = None

            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue
                lines = text.split("\n")
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue

                    upper = line.upper()
                    if any(x in upper for x in ["SEQ.", "SEQ ", "RELATORIO", "COMPETENCIA", "PRESTADOR", "TOTAL (", "TOTAL E FRACOES"]):
                        continue

                    # Linha apenas com código entre parênteses
                    paren_code = re.match(r'^\(?(\d{10})\)?$', line.replace("(", "").replace(")", ""))
                    if paren_code:
                        pending_code = paren_code.group(1)
                        continue

                    # Capturar prefixo de exame (linhas como "DOSAGEM DE ...")
                    if "R$" not in line and not re.match(r'^\d+\s+\d+\s+REALIZADO', line):
                        if len(line) > 3 and re.match(r'^[A-ZÁÉÍÓÚÂÊÔÇ\s]+$', line):
                            pending_exam_prefix = (pending_exam_prefix + " " + line).strip()
                        continue

                    seq_match = re.match(r'^\d+\s+\d+\s+REALIZADO', line)
                    if not seq_match:
                        continue

                    # Extrair valores
                    values = re.findall(r'R\$\s*[\d.]+,\d{2}', line)
                    value_pago = None
                    if len(values) >= 2:
                        value_pago = parse_currency_value(values[1])
                    elif len(values) == 1:
                        value_pago = parse_currency_value(values[0])
                    if not value_pago:
                        continue

                    # Cortar linha antes dos valores
                    left = line.split("R$")[0].strip()
                    tokens = left.split()

                    patient_name = None
                    exam_tokens = []

                    if candidate_patients:
                        normalized_tokens = [normalize_name(t) for t in tokens]
                        patient_name, exam_start_idx = _find_patient_in_tokens(normalized_tokens, candidate_patients)
                        if patient_name:
                            # reconstruir tokens originais do exame
                            exam_tokens = tokens[exam_start_idx:]
                            patient_name = normalize_name(patient_name)

                    if not patient_name:
                        # fallback: após código de origem numérico
                        numeric_idx = None
                        for i, token in enumerate(tokens):
                            if token.isdigit() and len(token) >= 5:
                                numeric_idx = i
                                break
                        if numeric_idx is not None and numeric_idx + 2 < len(tokens):
                            patient_tokens = tokens[numeric_idx + 1 : numeric_idx + 5]
                            patient_name = normalize_name(" ".join(patient_tokens))
                            exam_tokens = tokens[numeric_idx + 5 :]

                    if not patient_name:
                        continue

                    exam_name = normalize_exam_name(" ".join(exam_tokens))
                    if pending_exam_prefix:
                        exam_name = normalize_exam_name(pending_exam_prefix + " " + exam_name)
                        pending_exam_prefix = ""
                    if pending_code and pending_code not in exam_name:
                        # ajuda a diferenciar exames iguais com código no SIMUS
                        exam_name = normalize_exam_name(f"{exam_name} {pending_code}")
                        pending_code = None

                    if not exam_name or len(exam_name) < 3:
                        exam_name = "EXAME"

                    patients[patient_name]["exams"].append(
                        {"exam_name": exam_name, "value": value_pago}
                    )
                    patients[patient_name]["total"] += value_pago
                            
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
        # Criar dicionários de exames por NOME (não código!)
        compulab_exams = {}
        for exam in compulab_patients[patient]['exams']:
            exam_name = exam['exam_name']
            if exam_name not in compulab_exams:
                compulab_exams[exam_name] = []
            compulab_exams[exam_name].append(exam)
        
        simus_exams = {}
        for exam in simus_patients[patient]['exams']:
            exam_name = exam['exam_name']
            if exam_name not in simus_exams:
                simus_exams[exam_name] = []
            simus_exams[exam_name].append(exam)
        
        compulab_exam_names = set(compulab_exams.keys())
        simus_exam_names = set(simus_exams.keys())
        
        # Exames faltantes no SIMUS (comparando por NOME)
        missing_exam_names = compulab_exam_names - simus_exam_names
        for exam_name in missing_exam_names:
            for exam in compulab_exams[exam_name]:
                results['missing_exams'].append({
                    'patient': patient,
                    'exam_name': exam_name,
                    'value': exam['value']
                })
        
        # Comparar valores de exames comuns (comparando por NOME)
        common_exam_names = compulab_exam_names & simus_exam_names
        for exam_name in common_exam_names:
            # Soma todos os valores do mesmo nome de exame
            compulab_total = sum(ex['value'] for ex in compulab_exams[exam_name])
            simus_total = sum(ex['value'] for ex in simus_exams[exam_name])
            
            if abs(compulab_total - simus_total) > Decimal('0.01'):
                results['value_divergences'].append({
                    'patient': patient,
                    'exam_name': exam_name,
                    'compulab_value': compulab_total,
                    'simus_value': simus_total,
                    'difference': compulab_total - simus_total,
                    'compulab_count': len(compulab_exams[exam_name]),
                    'simus_count': len(simus_exams[exam_name])
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

# Interface Streamlit
st.sidebar.header("📁 Upload de Arquivos")
st.sidebar.markdown("Faça upload dos PDFs para análise mensal")

compulab_file = st.sidebar.file_uploader(
    "COMPULAB.pdf",
    type=['pdf'],
    help="Upload do PDF do COMPULAB"
)

simus_file = st.sidebar.file_uploader(
    "SIMUS.pdf",
    type=['pdf'],
    help="Upload do PDF do SIMUS"
)

analyze_button = st.sidebar.button("🔍 Analisar", type="primary", use_container_width=True)

if analyze_button and compulab_file and simus_file:
    with st.spinner("Processando PDFs e extraindo dados dos pacientes..."):
        # Extrair dados
        compulab_patients, compulab_total = extract_compulab_patients(compulab_file)
        simus_patients, simus_total, sigtap_val, contratualizado_val = extract_simus_patients(
            simus_file, known_patient_names=list(compulab_patients.keys()) if compulab_patients else None
        )
        
        if compulab_patients is None or simus_patients is None:
            st.error("Erro ao processar os PDFs. Verifique se os arquivos estão corretos.")
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

# Exibir resultados
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
    
    tab1, tab2, tab3 = st.tabs([
        "⚠️ Exames Faltantes", 
        "💰 Divergências de Valores",
        "📄 Relatório Completo"
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

else:
    st.info("👆 Faça upload dos PDFs na barra lateral e clique em 'Analisar' para começar.")

# Rodapé
st.markdown("---")
st.markdown("**Análise de Faturamento por Paciente e Exame - Laboratório Biodiagnóstico vs SIMUS**")
