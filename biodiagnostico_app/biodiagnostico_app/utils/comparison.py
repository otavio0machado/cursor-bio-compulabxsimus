"""
Comparison Engine for COMPULAB vs SIMUS Analysis
Laboratório Biodiagnóstico
v2.0 - Robust, Deterministic Results for Judicial Use
"""
import json
import re
import unicodedata
from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Tuple


def normalize_patient_name(name: str) -> str:
    """
    Normaliza nome do paciente para matching robusto.
    - Remove acentos
    - Converte para maiúsculas
    - Remove espaços extras
    - Remove caracteres especiais
    """
    if not name:
        return ""
    # Remove acentos
    name = unicodedata.normalize('NFKD', str(name)).encode('ASCII', 'ignore').decode('ASCII')
    # Uppercase
    name = name.upper()
    # Remove caracteres não alfanuméricos exceto espaço
    name = re.sub(r'[^A-Z0-9\s]', '', name)
    # Remove espaços extras
    name = ' '.join(name.split())
    return name.strip()


def normalize_exam_name(name: str) -> str:
    """
    Normaliza nome do exame para matching.
    """
    if not name:
        return ""
    name = unicodedata.normalize('NFKD', str(name)).encode('ASCII', 'ignore').decode('ASCII')
    name = name.upper()
    name = re.sub(r'[^A-Z0-9\s]', '', name)
    name = ' '.join(name.split())
    return name.strip()


def safe_decimal(value: Any, default: Decimal = Decimal('0')) -> Decimal:
    """Converte valor para Decimal de forma segura."""
    if value is None:
        return default
    try:
        if isinstance(value, Decimal):
            return value
        if isinstance(value, str):
            # Handle Brazilian format (1.234,56)
            value = value.replace('.', '').replace(',', '.')
        return Decimal(str(value))
    except:
        return default


def format_currency_br(value: Decimal) -> str:
    """Formata valor como moeda brasileira."""
    val = float(value)
    return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


@dataclass
class PatientMissing:
    """Paciente presente no COMPULAB mas ausente no SIMUS"""
    name: str
    total_exams: int
    total_value: float
    exams: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ExamMissing:
    """Exame presente no COMPULAB mas ausente no SIMUS para um paciente comum"""
    patient: str
    exam_name: str
    code: str
    value: float


@dataclass
class ValueDivergence:
    """Divergência de valor entre COMPULAB e SIMUS para o mesmo exame"""
    patient: str
    exam_name: str
    code: str
    compulab_value: float
    simus_value: float
    difference: float


@dataclass
class ExtraSimusExam:
    """Exame presente no SIMUS mas não no COMPULAB (alerta de risco)"""
    patient: str
    exam_name: str
    code: str
    simus_value: float


@dataclass
class AnalysisReport:
    """Relatório completo da análise COMPULAB vs SIMUS"""
    # Totais agregados
    compulab_total: float = 0.0
    simus_total: float = 0.0
    difference: float = 0.0
    
    # Contagens
    compulab_patients_count: int = 0
    simus_patients_count: int = 0
    compulab_exams_count: int = 0
    simus_exams_count: int = 0
    
    # Listas de discrepâncias
    missing_patients: List[PatientMissing] = field(default_factory=list)
    missing_exams: List[ExamMissing] = field(default_factory=list)
    value_divergences: List[ValueDivergence] = field(default_factory=list)
    extra_simus_exams: List[ExtraSimusExam] = field(default_factory=list)
    
    # Impactos financeiros por categoria
    impact_missing_patients: float = 0.0
    impact_missing_exams: float = 0.0
    impact_value_divergences: float = 0.0
    impact_extra_simus: float = 0.0
    
    # Explicação da diferença
    explained_difference: float = 0.0
    unexplained_residual: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário para serialização"""
        return {
            "compulab_total": self.compulab_total,
            "simus_total": self.simus_total,
            "difference": self.difference,
            "compulab_patients_count": self.compulab_patients_count,
            "simus_patients_count": self.simus_patients_count,
            "compulab_exams_count": self.compulab_exams_count,
            "simus_exams_count": self.simus_exams_count,
            "missing_patients": [asdict(p) for p in self.missing_patients],
            "missing_exams": [asdict(e) for e in self.missing_exams],
            "value_divergences": [asdict(v) for v in self.value_divergences],
            "extra_simus_exams": [asdict(e) for e in self.extra_simus_exams],
            "impact_missing_patients": self.impact_missing_patients,
            "impact_missing_exams": self.impact_missing_exams,
            "impact_value_divergences": self.impact_value_divergences,
            "impact_extra_simus": self.impact_extra_simus,
            "explained_difference": self.explained_difference,
            "unexplained_residual": self.unexplained_residual,
        }


def run_complete_analysis(compulab_patients: Dict, simus_patients: Dict) -> AnalysisReport:
    """
    Executa análise completa e determinística entre COMPULAB e SIMUS.
    
    LÓGICA:
    1. Normaliza todos os nomes de pacientes para matching
    2. Identifica pacientes ausentes em cada sistema
    3. Para pacientes comuns, compara exames por nome/código normalizado
    4. Calcula impacto financeiro de cada categoria
    5. Explica a diferença total
    
    Returns:
        AnalysisReport com todos os dados estruturados
    """
    report = AnalysisReport()
    
    # ===== FASE 1: Calcular totais e contagens =====
    compulab_total = Decimal('0')
    simus_total = Decimal('0')
    compulab_exams_count = 0
    simus_exams_count = 0
    
    # Criar mapeamento normalizado -> (nome_original, dados)
    norm_to_compulab: Dict[str, Tuple[str, Dict]] = {}
    norm_to_simus: Dict[str, Tuple[str, Dict]] = {}
    
    for patient_name, patient_data in compulab_patients.items():
        norm_name = normalize_patient_name(patient_name)
        if not norm_name:
            continue
        
        exams = []
        if isinstance(patient_data, dict):
            exams = patient_data.get('exams', [])
        elif isinstance(patient_data, list):
            exams = patient_data
        
        patient_total = Decimal('0')
        for exam in exams:
            val = safe_decimal(exam.get('value', 0))
            patient_total += val
            compulab_exams_count += 1
        
        compulab_total += patient_total
        norm_to_compulab[norm_name] = (patient_name, {
            'exams': exams,
            'total': float(patient_total)
        })
    
    for patient_name, patient_data in simus_patients.items():
        norm_name = normalize_patient_name(patient_name)
        if not norm_name:
            continue
        
        exams = []
        if isinstance(patient_data, dict):
            exams = patient_data.get('exams', [])
        elif isinstance(patient_data, list):
            exams = patient_data
        
        patient_total = Decimal('0')
        for exam in exams:
            val = safe_decimal(exam.get('value', 0))
            patient_total += val
            simus_exams_count += 1
        
        simus_total += patient_total
        norm_to_simus[norm_name] = (patient_name, {
            'exams': exams,
            'total': float(patient_total)
        })
    
    report.compulab_total = float(compulab_total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
    report.simus_total = float(simus_total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
    report.difference = float((compulab_total - simus_total).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
    report.compulab_patients_count = len(norm_to_compulab)
    report.simus_patients_count = len(norm_to_simus)
    report.compulab_exams_count = compulab_exams_count
    report.simus_exams_count = simus_exams_count
    
    # ===== FASE 2: Identificar pacientes ausentes =====
    compulab_norm_names = set(norm_to_compulab.keys())
    simus_norm_names = set(norm_to_simus.keys())
    
    # Pacientes no COMPULAB mas não no SIMUS
    missing_in_simus = sorted(compulab_norm_names - simus_norm_names)
    impact_missing_patients = Decimal('0')
    
    for norm_name in missing_in_simus:
        orig_name, data = norm_to_compulab[norm_name]
        patient_total = safe_decimal(data['total'])
        impact_missing_patients += patient_total
        
        report.missing_patients.append(PatientMissing(
            name=orig_name,
            total_exams=len(data['exams']),
            total_value=float(patient_total),
            exams=data['exams']
        ))
    
    report.impact_missing_patients = float(impact_missing_patients.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
    
    # Pacientes no SIMUS mas não no COMPULAB (para referência, não impacta a diferença positiva)
    extra_patients_simus = sorted(simus_norm_names - compulab_norm_names)
    # Esses vão para extra_simus_exams se necessário
    
    # ===== FASE 3: Comparar exames para pacientes comuns =====
    common_patients = sorted(compulab_norm_names & simus_norm_names)
    impact_missing_exams = Decimal('0')
    impact_divergences = Decimal('0')
    impact_extra_simus = Decimal('0')
    
    for norm_name in common_patients:
        orig_compulab, data_compulab = norm_to_compulab[norm_name]
        orig_simus, data_simus = norm_to_simus[norm_name]
        
        compulab_exams = data_compulab['exams']
        simus_exams = data_simus['exams']
        
        # Criar índice de exames SIMUS por nome normalizado
        simus_exam_index: Dict[str, List[Tuple[int, Dict]]] = {}
        for i, exam in enumerate(simus_exams):
            norm_exam = normalize_exam_name(exam.get('exam_name', ''))
            if norm_exam:
                if norm_exam not in simus_exam_index:
                    simus_exam_index[norm_exam] = []
                simus_exam_index[norm_exam].append((i, exam))
        
        simus_used_indices = set()
        
        # Para cada exame do COMPULAB
        for c_exam in compulab_exams:
            c_exam_name = c_exam.get('exam_name', '')
            c_norm_name = normalize_exam_name(c_exam_name)
            c_value = safe_decimal(c_exam.get('value', 0))
            c_code = str(c_exam.get('code', '')).strip()
            
            if not c_norm_name:
                continue
            
            # Procurar match no SIMUS
            match_found = False
            if c_norm_name in simus_exam_index:
                for idx, s_exam in simus_exam_index[c_norm_name]:
                    if idx in simus_used_indices:
                        continue
                    
                    s_value = safe_decimal(s_exam.get('value', 0))
                    s_code = str(s_exam.get('code', '')).strip()
                    
                    # Match encontrado
                    simus_used_indices.add(idx)
                    match_found = True
                    
                    # Verificar divergência de valor
                    diff = c_value - s_value
                    if abs(diff) >= Decimal('0.10'):  # Diferença >= 10 centavos
                        impact_divergences += diff
                        report.value_divergences.append(ValueDivergence(
                            patient=orig_compulab,
                            exam_name=c_exam_name,
                            code=c_code or s_code,
                            compulab_value=float(c_value),
                            simus_value=float(s_value),
                            difference=float(diff)
                        ))
                    break
            
            if not match_found:
                # Exame faltante no SIMUS
                impact_missing_exams += c_value
                report.missing_exams.append(ExamMissing(
                    patient=orig_compulab,
                    exam_name=c_exam_name,
                    code=c_code,
                    value=float(c_value)
                ))
        
        # Identificar exames extras no SIMUS (não usados)
        for i, s_exam in enumerate(simus_exams):
            if i not in simus_used_indices:
                s_value = safe_decimal(s_exam.get('value', 0))
                impact_extra_simus += s_value
                report.extra_simus_exams.append(ExtraSimusExam(
                    patient=orig_simus,
                    exam_name=s_exam.get('exam_name', ''),
                    code=str(s_exam.get('code', '')).strip(),
                    simus_value=float(s_value)
                ))
    
    # Adicionar exames de pacientes extras no SIMUS
    for norm_name in extra_patients_simus:
        orig_name, data = norm_to_simus[norm_name]
        for exam in data['exams']:
            s_value = safe_decimal(exam.get('value', 0))
            impact_extra_simus += s_value
            report.extra_simus_exams.append(ExtraSimusExam(
                patient=orig_name,
                exam_name=exam.get('exam_name', ''),
                code=str(exam.get('code', '')).strip(),
                simus_value=float(s_value)
            ))
    
    # Finalizar impactos
    report.impact_missing_exams = float(impact_missing_exams.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
    report.impact_value_divergences = float(impact_divergences.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
    report.impact_extra_simus = float(impact_extra_simus.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
    
    # ===== FASE 4: Explicar a diferença =====
    explained = impact_missing_patients + impact_missing_exams + impact_divergences
    report.explained_difference = float(explained.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
    report.unexplained_residual = float((Decimal(str(report.difference)) - explained).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
    
    # ===== FASE 5: Ordenar resultados para determinismo =====
    report.missing_patients.sort(key=lambda x: (-x.total_value, x.name))
    report.missing_exams.sort(key=lambda x: (-x.value, x.patient, x.exam_name))
    report.value_divergences.sort(key=lambda x: (-abs(x.difference), x.patient, x.exam_name))
    report.extra_simus_exams.sort(key=lambda x: (-x.simus_value, x.patient, x.exam_name))
    
    return report


def compare_patients(compulab_patients, simus_patients):
    """
    Wrapper de compatibilidade com a interface antiga.
    Retorna dicionário no formato esperado pelo State.
    """
    report = run_complete_analysis(compulab_patients, simus_patients)
    
    return {
        'missing_patients': [
            {
                'patient': p.name,
                'name': p.name,
                'exams_count': p.total_exams,
                'total_exams': p.total_exams,
                'total_value': round(float(p.total_value), 2),
                'exams': p.exams
            }
            for p in report.missing_patients
        ],

        'missing_exams': [
            {
                'patient': e.patient,
                'exam_name': e.exam_name,
                'value': round(float(e.value), 2),
                'code': e.code
            }
            for e in report.missing_exams
        ],
        'value_divergences': [
            {
                'patient': v.patient,
                'exam_name': v.exam_name,
                'code': v.code,
                'compulab_value': round(float(v.compulab_value), 2),
                'simus_value': round(float(v.simus_value), 2),
                'difference': round(float(v.difference), 2)
            }
            for v in report.value_divergences
        ],
        'extra_simus_exams': [
            {
                'patient': e.patient,
                'exam_name': e.exam_name,
                'simus_value': round(float(e.simus_value), 2),
                'value': round(float(e.simus_value), 2),
                'code': e.code
            }
            for e in report.extra_simus_exams
        ]
    }



def compute_difference_breakdown(compulab_total, simus_total, comparison_results):
    """Calcula a explicação da diferença total (COMPULAB - SIMUS) - Compatibilidade"""
    compulab_total = Decimal(str(compulab_total))
    simus_total = Decimal(str(simus_total))
    
    diff_total = compulab_total - simus_total
    
    # Calcular totais das listas de resultados
    missing_patients_total = Decimal('0')
    for item in comparison_results.get('missing_patients', []):
        val = item.get('total_value', 0)
        if isinstance(val, str):
            val = val.replace(',', '.')
        missing_patients_total += safe_decimal(val)
    
    missing_exams_total = Decimal('0')
    for item in comparison_results.get('missing_exams', []):
        val = item.get('value', 0)
        if isinstance(val, str):
            val = val.replace(',', '.')
        missing_exams_total += safe_decimal(val)
    
    divergences_total = Decimal('0')
    for item in comparison_results.get('value_divergences', []):
        val = item.get('difference', 0)
        if isinstance(val, str):
            val = val.replace(',', '.')
        divergences_total += safe_decimal(val)
    
    explained = missing_patients_total + missing_exams_total + divergences_total
    residual = diff_total - explained
    
    return {
        "diff_total": float(diff_total),
        "missing_patients_total": float(missing_patients_total),
        "missing_exams_total": float(missing_exams_total),
        "divergences_total": float(divergences_total),
        "explained_total": float(explained),
        "residual": float(residual),
    }


def generate_analysis_summary(report: AnalysisReport) -> str:
    """
    Gera um resumo textual da análise para exibição.
    """
    lines = []
    
    lines.append("## RESUMO EXECUTIVO DA ANÁLISE")
    lines.append("")
    lines.append(f"**Valor Total COMPULAB:** {format_currency_br(Decimal(str(report.compulab_total)))}")
    lines.append(f"**Valor Total SIMUS:** {format_currency_br(Decimal(str(report.simus_total)))}")
    lines.append(f"**Diferença (Gap):** {format_currency_br(Decimal(str(report.difference)))}")
    lines.append("")
    lines.append(f"Pacientes COMPULAB: {report.compulab_patients_count} | Pacientes SIMUS: {report.simus_patients_count}")
    lines.append(f"Exames COMPULAB: {report.compulab_exams_count} | Exames SIMUS: {report.simus_exams_count}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## EXPLICAÇÃO DA DIFERENÇA")
    lines.append("")
    
    if report.impact_missing_patients > 0:
        lines.append(f"**1. Pacientes Ausentes no SIMUS:** {format_currency_br(Decimal(str(report.impact_missing_patients)))}")
        lines.append(f"   - {len(report.missing_patients)} pacientes do COMPULAB não foram encontrados no SIMUS")
    
    if report.impact_missing_exams > 0:
        lines.append(f"**2. Exames Ausentes no SIMUS:** {format_currency_br(Decimal(str(report.impact_missing_exams)))}")
        lines.append(f"   - {len(report.missing_exams)} exames do COMPULAB não foram faturados no SIMUS")
    
    if report.impact_value_divergences != 0:
        lines.append(f"**3. Divergências de Valor:** {format_currency_br(Decimal(str(report.impact_value_divergences)))}")
        lines.append(f"   - {len(report.value_divergences)} exames com valores diferentes entre os sistemas")
    
    if report.impact_extra_simus > 0:
        lines.append(f"**4. Exames Extras no SIMUS (Alerta):** {format_currency_br(Decimal(str(report.impact_extra_simus)))}")
        lines.append(f"   - {len(report.extra_simus_exams)} exames no SIMUS sem correspondência no COMPULAB")
    
    lines.append("")
    lines.append(f"**Diferença Explicada:** {format_currency_br(Decimal(str(report.explained_difference)))}")
    
    if abs(report.unexplained_residual) >= 0.01:
        lines.append(f"**Resíduo Não Explicado:** {format_currency_br(Decimal(str(report.unexplained_residual)))}")
    
    return "\n".join(lines)


# Compatibilidade com imports antigos
def format_divergences_to_json(delimited_data: str) -> str:
    """Converte dados delimitados em JSON estruturado (legado)."""
    if not delimited_data or not delimited_data.strip():
        return "[]"
    
    lines = delimited_data.strip().split('\n')
    if not lines:
        return "[]"
    
    delimiter = ';' if ';' in lines[0] else ','
    result = []
    
    for line in lines[1:]:  # Skip header
        parts = [p.strip() for p in line.split(delimiter)]
        if len(parts) >= 6:
            result.append({
                "Paciente": parts[0],
                "Nome_Exame": parts[1],
                "Codigo_Exame": parts[2],
                "Valor_Compulab": parts[3],
                "Valor_Simus": parts[4],
                "Tipo_Divergencia": parts[5]
            })
    
    return json.dumps(result, ensure_ascii=False, indent=2)


