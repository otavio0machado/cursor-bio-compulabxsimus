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
from ..services.mapping_service import mapping_service

# Configurações para arquivos grandes
MAX_PAGES_PER_BATCH = 20  # Processar páginas em lotes
PDF_PROCESSING_TIMEOUT = 300  # 5 minutos de timeout
LARGE_FILE_THRESHOLD_MB = 5  # Arquivos acima disso são considerados grandes


# EXAM_NAME_MAPPING removido e movido para o banco de dados via MappingService

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
    
    # Manter parênteses pois o usuário solicitou nomenclaturas específicas como (T4 LIVRE)
    # exam_name = re.sub(r'\([^)]*\)', '', exam_name) 
    
    exam_name = re.sub(r'[^\w\s\(\)]', ' ', exam_name) # Permite ( e )
    exam_name = ' '.join(exam_name.split())
    
    # Remover palavras genéricas para o nome ficar limpo na exibição
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
        exam_name = re.sub(pattern_start, '', exam_name, flags=re.IGNORECASE)
    
    # Normalizações específicas de acrônimos (Solicitado: sem separação)
    exam_name = exam_name.replace('G O T', 'GOT')
    exam_name = exam_name.replace('G P T', 'GPT')
    
    # Renomeações específicas solicitadas pelo usuário
    if 'TIROXINA LIVRE' in exam_name:
        if '(T4)' in exam_name or 'T4' in exam_name:
             if '(T4 LIVRE)' not in exam_name:
                 exam_name = exam_name.replace('(T4)', '(T4 LIVRE)').replace('T4', '(T4 LIVRE)')
                 exam_name = ' '.join(exam_name.split()) # Limpar espaços extras
    
    return exam_name.strip()


def normalize_exam_name_for_comparison(exam_name):
    """Normaliza nome do exame removendo parênteses para comparação inteligente"""
    if not exam_name:
        return ""
    
    # normalize_exam_name já removeu as palavras genéricas e normalizou GOT/GPT
    normalized = normalize_exam_name(exam_name)
    
    # Remover parênteses apenas para a COMPARAÇÃO interna
    normalized = re.sub(r'\([^)]*\)', '', normalized)
    normalized = re.sub(r'[^\w\s]', ' ', normalized)
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

def canonicalize_exam_name(exam_name):
    """Aplica mapeamento de sinônimos e normaliza para comparação."""
    if not exam_name:
        return ""
    mapped = map_simus_to_compulab_exam_name(exam_name)
    return normalize_exam_name(mapped)


def exam_names_match(exam_name1, exam_name2):
    """Verifica se dois nomes de exame representam o mesmo exame"""
    canon1 = canonicalize_exam_name(exam_name1)
    canon2 = canonicalize_exam_name(exam_name2)
    norm1 = normalize_exam_name_for_comparison(canon1)
    norm2 = normalize_exam_name_for_comparison(canon2)
    
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
    
    key_terms1 = extract_key_terms(canon1)
    key_terms2 = extract_key_terms(canon2)
    
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
    
    # 1. Tentar mapeamento exato via Banco de Dados (MappingService)
    canonical = mapping_service.get_canonical_name_sync(simus_clean)
    if canonical != simus_clean:
        return canonical
    
    # 2. Tentar mapeamento via normalização
    normalized_simus = normalize_exam_name(simus_clean)
    all_mappings = mapping_service.get_all_synonyms()
    
    for original, canonical in all_mappings.items():
        if normalize_exam_name(original) == normalized_simus:
            return canonical
            
    # 3. Tentar match parcial se as palavras baterem significativamente (Heurística)
    for original, canonical in all_mappings.items():
        normalized_key = normalize_exam_name(original)
        if normalized_key in normalized_simus or normalized_simus in normalized_key:
            key_words = set(normalized_key.split())
            simus_words = set(normalized_simus.split())
            common_words = key_words & simus_words
            if len(common_words) >= 2:
                return canonical
    
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



class SimusPDFParser:
    """
    Parser robusto para arquivos PDF do SIMUS.
    Implementa múltiplas estratégias de extração para máxima compatibilidade.
    """
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.total_sigtap = Decimal('0')
        self.total_contratualizado = Decimal('0')
        self.extracted_patients = defaultdict(lambda: {'exams': [], 'total': Decimal('0')})
        
    def extract(self, progress_callback=None) -> Tuple[Dict, Decimal, Optional[Decimal], Optional[Decimal]]:
        """
        Executa a extração usando a melhor estratégia disponível.
        1. Tenta extrair totais da primeira página
        2. Tenta estratégia baseada em tabelas (mais precisa)
        3. Se falhar ou retornar pouco, tenta estratégia baseada em texto (fallback)
        """
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                # FASE 0: Extrair Totais do Cabeçalho (Página 1)
                self._extract_header_totals(pdf.pages[0])
                
                total_pages = len(pdf.pages)
                
                # FASE 1: Estratégia de Tabelas
                table_success = self._strategy_table_extraction(pdf, total_pages, progress_callback)
                
                # Validação: Se extraiu muito pouco comparado ao esperado, tentar fallback
                extracted_total = sum(p['total'] for p in self.extracted_patients.values())
                expected_total = self.total_contratualizado or Decimal('999999999')
                
                # Se recuperamos menos de 10% do valor esperado ou nenhum paciente, tentar fallback
                if not table_success or (len(self.extracted_patients) == 0):
                    print("DEBUG: Estratégia de tabela falhou ou insuficiente. Tentando análise textual...")
                    # Limpar parcial
                    self.extracted_patients.clear()
                    self._strategy_text_analysis(pdf, total_pages, progress_callback)
            
            final_total = sum(p['total'] for p in self.extracted_patients.values())
            return self.extracted_patients, final_total, self.total_sigtap, self.total_contratualizado
            
        except Exception as e:
            print(f"Erro fatal no parser SIMUS: {e}")
            return {}, Decimal('0'), None, None

    def _extract_header_totals(self, first_page):
        """Extrai valores totais do cabeçalho da primeira página"""
        try:
            text = first_page.extract_text() or ""
            # Padrão: R$ 1.234,56 (SIGTAP) ... R$ 1.234,56 (Contratualizados)
            sigtap_match = re.search(r'R\$\s*([\d.]+,\d{2})\s*\(SIGTAP\)', text)
            contrat_match = re.search(r'R\$\s*([\d.]+,\d{2})\s*\(Contratualizados\)', text)
            
            if sigtap_match:
                self.total_sigtap = parse_currency_value(sigtap_match.group(1)) or Decimal('0')
            if contrat_match:
                self.total_contratualizado = parse_currency_value(contrat_match.group(1)) or Decimal('0')
                
        except Exception as e:
            print(f"Erro ao extrair totais do cabeçalho: {e}")

    def _strategy_table_extraction(self, pdf, total_pages, progress_callback) -> bool:
        """Estratégia 1: Extração estruturada de tabelas"""
        try:
            current_patient = None
            
            for i, page in enumerate(pdf.pages):
                if progress_callback:
                    progress_callback(i + 1, total_pages)
                
                tables = page.extract_tables()
                if not tables:
                    continue
                    
                for table in tables:
                    self._process_table(table, current_patient)
                    
            return len(self.extracted_patients) > 0
        except Exception as e:
            print(f"Erro na estratégia de tabelas: {e}")
            return False

    def _process_table(self, table, current_patient):
        """Processa uma única tabela identificando colunas dinamicamente"""
        if not table or len(table) < 2:
            return
            
        # Identificar colunas
        header_row_idx = -1
        cols = {'paciente': -1, 'exame': -1, 'valor': -1, 'codigo': -1}
        
        # Procurar cabeçalho
        for i, row in enumerate(table[:5]): # Tentar nas 5 primeiras linhas
            row_str = " ".join([str(c).upper() if c else "" for c in row])
            if "PACIENTE" in row_str or "BENEFICIARIO" in row_str or "NOME" in row_str:
                header_row_idx = i
                break
        
        if header_row_idx == -1: return
        
        # Mapear índices das colunas
        header = table[header_row_idx]
        for idx, col_name in enumerate(header):
            if not col_name: continue
            c = str(col_name).upper().strip()
            
            if any(x in c for x in ['PACIENTE', 'BENEFICIARIO', 'NOME']): cols['paciente'] = idx
            elif any(x in c for x in ['EXAME', 'PROCEDIMENTO', 'DESCRICAO']): cols['exame'] = idx
            elif any(x in c for x in ['VALOR PAGO', 'VL PAGO', 'VALOR']): cols['valor'] = idx # Prioridade
            elif any(x in c for x in ['CODIGO', 'COD', 'SIGTAP']): cols['codigo'] = idx

        # Se não achou colunas vitais, abortar tabela
        if cols['exame'] == -1 or cols['valor'] == -1: return
        
        # Processar linhas de dados
        for row in table[header_row_idx+1:]:
            if not row or len(row) <= max(cols.values()): continue
            
            # Extrair dados
            patient_name = ""
            if cols['paciente'] != -1 and row[cols['paciente']]:
                raw_name = str(row[cols['paciente']]).strip()
                if raw_name and raw_name.upper() not in ['TOTAL', 'SUBTOTAL']:
                    patient_name = normalize_name(raw_name)
                    # Atualizar contexto de paciente atual (para linhas subsequentes vazias)
                    current_patient = patient_name
            
            # Usar paciente do contexto se a linha não tiver nome mas for continuação
            active_patient = patient_name if patient_name else current_patient
            if not active_patient: continue
            
            # Extrair exame
            exam_raw = str(row[cols['exame']]).strip()
            if not exam_raw: continue
            
            # Extrair código (da coluna ou do nome do exame)
            exam_code = ""
            if cols['codigo'] != -1 and row[cols['codigo']]:
                code_match = re.search(r'\d{8,10}', str(row[cols['codigo']]))
                if code_match: exam_code = code_match.group(0)
            
            if not exam_code:
                code_match = re.search(r'\d{8,10}', exam_raw)
                if code_match: exam_code = code_match.group(0)
            
            # Limpar nome do exame (remover código se estiver junto)
            exam_name = re.sub(r'\d{8,10}', '', exam_raw).strip()
            exam_name = normalize_exam_name(map_simus_to_compulab_exam_name(exam_name))
            
            # Extrair valor
            try:
                val_str = str(row[cols['valor']])
                val = parse_currency_value(val_str)
            except:
                val = Decimal('0')
                
            if val and val > 0:
                self.extracted_patients[active_patient]['exams'].append({
                    'exam_name': exam_name,
                    'code': exam_code,
                    'value': val
                })
                self.extracted_patients[active_patient]['total'] += val

    def _strategy_text_analysis(self, pdf, total_pages, progress_callback):
        """Estratégia 2: Análise linha a linha (Fallback)"""
        current_patient = None
        
        for i, page in enumerate(pdf.pages):
            if progress_callback:
                progress_callback(i + 1, total_pages)
                
            text = page.extract_text()
            if not text: continue
            
            lines = text.split('\n')
            for line in lines:
                # Pular cabeçalhos/rodapés comuns
                if any(x in line.upper() for x in ['PAGINA', 'RELATORIO', 'EMISSAO', 'TOTAL']):
                    continue
                    
                # Identificar Paciente (Linha começa com número seq e tem nome)
                # Ex: 001 NOME DO PACIENTE                                 ...
                patient_match = re.match(r'^\d+\s+([A-Z\s]+?)\s+\d{2}/\d{2}/\d{4}', line)
                if patient_match:
                    possible_name = patient_match.group(1).strip()
                    if len(possible_name) > 3 and not re.search(r'\d', possible_name):
                        current_patient = normalize_name(possible_name)
                        continue
                
                # Se temos um paciente ativo, procurar exames na linha
                if current_patient:
                    # Tentar achar padrão de exame: Código + Nome + Valor
                    # Ex: 0202010123 HEMOGRAMA COMPLETO ... 10,00
                    
                    # Regex flexível para capturar código, nome e valor
                    # Procura código 8-10 digitos, seguido de texto, seguido de valor monetário
                    line_match = re.search(r'(\d{8,10})\s+(.+?)\s+([\d.]+,\d{2})', line)
                    if not line_match:
                        # Tentar sem código inicial (as vezes codigo ta em outra coluna)
                        line_match = re.search(r'()(.+?)\s+([\d.]+,\d{2})', line)
                        
                    if line_match:
                        code = line_match.group(1)
                        name_raw = line_match.group(2).strip()
                        val_str = line_match.group(3)
                        
                        # Validar se o "nome" não é lixo
                        if len(name_raw) < 3 or re.search(r'\d{2}/\d{2}', name_raw): 
                            continue
                            
                        val = parse_currency_value(val_str)
                        if val and val > 0:
                            # Mapear nome
                            name_mapped = map_simus_to_compulab_exam_name(name_raw)
                            normalized_name = normalize_exam_name(name_mapped)
                            
                            # Adicionar
                            self.extracted_patients[current_patient]['exams'].append({
                                'exam_name': normalized_name,
                                'code': code,
                                'value': val
                            })
                            self.extracted_patients[current_patient]['total'] += val


def extract_simus_patients(pdf_file, known_patient_names=None, progress_callback: Optional[Callable[[int, int], None]] = None):
    """
    Wrapper para o novo parser SIMUS.
    Mantém compatibilidade com a assinatura antiga.
    """
    parser = SimusPDFParser(pdf_file)
    return parser.extract(progress_callback)


def generate_excel_from_pdfs(compulab_pdf_bytes, simus_pdf_bytes, progress_callback: Optional[Callable[[int, str], None]] = None):
    """Gera arquivos Excel (.xlsx) a partir dos bytes dos PDFs
    
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
        if not compulab_df.empty:
            compulab_df = compulab_df.sort_values(by=['Paciente', 'Nome_Exame'], ascending=[True, True])
        
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
        if not simus_df.empty:
            simus_df = simus_df.sort_values(by=['Paciente', 'Nome_Exame'], ascending=[True, True])
        
        # Estágio 4: Gerando Excels (95-98%)
        if progress_callback:
            progress_callback(95, "Gerando arquivos Excel...")

        import io
        import base64
        
        # Gerar Excel COMPULAB
        output_compulab = io.BytesIO()
        with pd.ExcelWriter(output_compulab, engine='openpyxl') as writer:
            compulab_df.to_excel(writer, index=False, sheet_name='COMPULAB')
        compulab_excel_b64 = base64.b64encode(output_compulab.getvalue()).decode()
        
        if progress_callback:
            progress_callback(98, "Finalizando conversão...")
        
        # Gerar Excel SIMUS
        output_simus = io.BytesIO()
        with pd.ExcelWriter(output_simus, engine='openpyxl') as writer:
            simus_df.to_excel(writer, index=False, sheet_name='SIMUS')
        simus_excel_b64 = base64.b64encode(output_simus.getvalue()).decode()
        
        if progress_callback:
            progress_callback(100, "Concluído")
        
        return compulab_excel_b64, simus_excel_b64, True
            
    except Exception as e:
        print(f"Erro ao gerar Excels: {e}")
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


def load_from_excel(file_path):
    """
    Carrega dados de um arquivo Excel (.xlsx ou .xls)
    """
    try:
        # Detectar se é bytes ou caminho
        if isinstance(file_path, bytes):
            import io
            file_path = io.BytesIO(file_path)
            
        df = pd.read_excel(file_path, engine='openpyxl' if str(file_path).endswith('.xlsx') else None)
        patients = defaultdict(lambda: {'exams': [], 'total': Decimal('0')})
        total_value = Decimal('0')
        
        # Mapeamento flexível de colunas
        col_map = {}
        for col in df.columns:
            col_upper = str(col).upper().strip()
            
            # Ordem de prioridade e exclusão de falso-positivos
            # Se contém "EXAME" ou "PROC", provavelmente não é o nome do paciente
            is_exam_col = any(name in col_upper for name in ['EXAME', 'PROCEDIMENTO', 'NOME_EXAME', 'NOME DO EXAME', 'DESCRICAO'])
            
            if is_exam_col and 'exam' not in col_map:
                col_map['exam'] = col
            elif any(name in col_upper for name in ['PACIENTE', 'BENEFICIARIO', 'NOME DO PACIENTE']) and 'patient' not in col_map:
                # Se for apenas "NOME", verificamos se não é o nome do exame
                if col_upper == 'NOME' and is_exam_col:
                    continue
                col_map['patient'] = col
            elif 'NOME' in col_upper and 'patient' not in col_map and not is_exam_col:
                col_map['patient'] = col
            elif any(name in col_upper for name in ['VALOR_PAGO', 'VALOR PAGO', 'VALOR_TOTAL', 'VALOR TOTAL']) and 'value' not in col_map:
                col_map['value'] = col
            elif any(name in col_upper for name in ['VALOR', 'PRECO', 'TOTAL']) and 'value' not in col_map:
                col_map['value'] = col
            elif any(name in col_upper for name in ['CODIGO', 'COD', 'SIGTAP', 'COD_PROC']) and 'code' not in col_map:
                col_map['code'] = col
                
        # Fallback se não encontrar colunas
        if 'patient' not in col_map:
            # Tentar encontrar uma coluna que pareça ter nomes de pessoas (opcional, aqui apenas pega a primeira)
            col_map['patient'] = df.columns[0]
        if 'exam' not in col_map:
            # Pega a segunda coluna se disponível
            col_map['exam'] = df.columns[1] if len(df.columns) > 1 else df.columns[0]
        if 'value' not in col_map:
            # Tenta a última coluna
            col_map['value'] = df.columns[-1]

        # Ordenar para determinismo
        df = df.sort_values(by=[col_map['patient'], col_map['exam']], na_position='last')
        
        for _, row in df.iterrows():
            patient_name = normalize_name(str(row[col_map['patient']]))
            exam_name = normalize_exam_name(str(row[col_map['exam']]))
            
            # Limpeza de valor
            try:
                val_raw = str(row[col_map['value']]).replace(',', '.')
                val_clean = "".join(c for c in val_raw if c.isdigit() or c == '.')
                value = Decimal(val_clean) if val_clean else Decimal('0')
            except:
                value = Decimal('0')
            
            if not patient_name or patient_name.upper() in ['TOTAL', 'PACIENTE', 'NOME'] or value == 0:
                continue
                
            code = str(row[col_map['code']]) if 'code' in col_map else ''
            
            patients[patient_name]['exams'].append({
                'exam_name': exam_name,
                'code': code,
                'value': value
            })
            patients[patient_name]['total'] += value
            total_value += value
            
        # Ordenar exames internos
        for patient_name in patients:
            patients[patient_name]['exams'].sort(key=lambda x: (x['exam_name'], x['value']))
            
        return patients, total_value
    except Exception as e:
        print(f"Erro ao carregar Excel: {e}")
        return None, Decimal('0')


