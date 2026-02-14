from typing import List, Optional, Any, Dict
from pydantic import BaseModel


class QCReferenceValue(BaseModel):
    """Registro de Valores Referenciais do CQ - Define valor-alvo e tolerância por exame"""
    id: str = ""
    name: str = ""
    exam_name: str = ""
    valid_from: str = ""
    valid_until: str = ""
    target_value: float = 0.0
    cv_max_threshold: float = 10.0
    lot_number: str = ""
    manufacturer: str = ""
    level: str = "Normal"
    notes: str = ""
    is_active: bool = True
    created_at: str = ""
    updated_at: str = ""


class QCRecord(BaseModel):
    """Registro de Controle de Qualidade"""
    id: str = ""
    date: str = ""
    exam_name: str = ""
    level: str = ""
    lot_number: str = ""
    value: float = 0.0
    value1: float = 0.0  # DEPRECATED: campo reservado para duplicatas, não populado atualmente
    value2: float = 0.0  # DEPRECATED: campo reservado para duplicatas, não populado atualmente
    mean: float = 0.0  # DEPRECATED: média calculada não utilizada — cv é calculado direto de value/target
    sd: float = 0.0  # DEPRECATED: desvio padrão local não utilizado — usa target_sd da referência
    cv: float = 0.0
    cv_max_threshold: float = 10.0
    target_value: float = 0.0
    target_sd: float = 0.0
    equipment: str = ""
    analyst: str = ""
    status: str = ""
    westgard_violations: List[Dict[str, Any]] = []
    z_score: float = 0.0  # DEPRECATED: calculado mas não exibido na UI
    reference_id: str = ""
    needs_calibration: bool = False
    post_calibration_id: str = ""


class PostCalibrationRecord(BaseModel):
    """Registro de Medição Pós-Calibração"""
    id: str = ""
    qc_record_id: str = ""
    date: str = ""
    exam_name: str = ""
    original_value: float = 0.0
    original_cv: float = 0.0
    post_calibration_value: float = 0.0
    post_calibration_cv: float = 0.0
    target_value: float = 0.0
    analyst: str = ""
    notes: str = ""
    created_at: str = ""


class ReagentLot(BaseModel):
    """Lote de Reagente"""
    id: str = ""
    name: str = ""
    lot_number: str = ""
    expiry_date: str = ""
    quantity: str = ""
    manufacturer: str = ""
    storage_temp: str = ""
    created_at: str = ""
    days_left: int = 0
    current_stock: float = 0.0
    estimated_consumption: float = 0.0

    @property
    def days_to_rupture(self) -> Optional[int]:
        if self.estimated_consumption > 0:
            return int(self.current_stock / self.estimated_consumption)
        return None


class MaintenanceRecord(BaseModel):
    """Registro de Manutenção"""
    id: str = ""
    equipment: str = ""
    type: str = ""
    date: str = ""
    next_date: str = ""
    technician: str = ""
    notes: str = ""
    created_at: str = ""


class ImunologiaRecord(BaseModel):
    """Registro de Controle de Qualidade - Imunologia"""
    id: str = ""
    controle: str = ""
    fabricante: str = ""
    lote: str = ""
    data: str = ""
    resultado: str = ""
    created_at: str = ""


class HematologyQCParameter(BaseModel):
    """Parâmetro (regra) de CQ Hematologia — Intervalo ou Percentual"""
    id: str = ""
    analito: str = ""
    equipamento: str = ""
    lote_controle: str = ""
    nivel_controle: str = ""
    modo: str = "INTERVALO"     # 'INTERVALO' | 'PERCENTUAL'
    alvo_valor: float = 0.0
    min_valor: float = 0.0
    max_valor: float = 0.0
    tolerancia_percentual: float = 0.0
    is_active: bool = True
    # Campos calculados da VIEW
    min_calc: float = 0.0
    max_calc: float = 0.0
    percentual_equivalente: float = 0.0
    created_at: str = ""
    updated_at: str = ""


class HematologyQCMeasurement(BaseModel):
    """Medição (lançamento) de CQ Hematologia"""
    id: str = ""
    data_medicao: str = ""
    analito: str = ""
    valor_medido: float = 0.0
    parameter_id: str = ""
    modo_usado: str = ""        # 'INTERVALO' | 'PERCENTUAL'
    min_aplicado: float = 0.0
    max_aplicado: float = 0.0
    status: str = ""            # 'APROVADO' | 'REPROVADO'
    observacao: str = ""
    created_at: str = ""


class HematologyBioRecord(BaseModel):
    """Registro da Tabela Bio x Controle Interno (Hematologia)"""
    id: str = ""
    data_bio: str = ""
    data_pad: str = ""
    registro_bio: str = ""
    registro_pad: str = ""
    modo_ci: str = "bio"  # 'bio' | 'intervalo' | 'porcentagem'
    bio_hemacias: float = 0.0
    bio_hematocrito: float = 0.0
    bio_hemoglobina: float = 0.0
    bio_leucocitos: float = 0.0
    bio_plaquetas: float = 0.0
    bio_rdw: float = 0.0
    bio_vpm: float = 0.0
    pad_hemacias: float = 0.0
    pad_hematocrito: float = 0.0
    pad_hemoglobina: float = 0.0
    pad_leucocitos: float = 0.0
    pad_plaquetas: float = 0.0
    pad_rdw: float = 0.0
    pad_vpm: float = 0.0
    ci_min_hemacias: float = 0.0
    ci_max_hemacias: float = 0.0
    ci_min_hematocrito: float = 0.0
    ci_max_hematocrito: float = 0.0
    ci_min_hemoglobina: float = 0.0
    ci_max_hemoglobina: float = 0.0
    ci_min_leucocitos: float = 0.0
    ci_max_leucocitos: float = 0.0
    ci_min_plaquetas: float = 0.0
    ci_max_plaquetas: float = 0.0
    ci_min_rdw: float = 0.0
    ci_max_rdw: float = 0.0
    ci_min_vpm: float = 0.0
    ci_max_vpm: float = 0.0
    ci_pct_hemacias: float = 0.0
    ci_pct_hematocrito: float = 0.0
    ci_pct_hemoglobina: float = 0.0
    ci_pct_leucocitos: float = 0.0
    ci_pct_plaquetas: float = 0.0
    ci_pct_rdw: float = 0.0
    ci_pct_vpm: float = 0.0
    created_at: str = ""


class LeveyJenningsPoint(BaseModel):
    """Ponto do gráfico Levey-Jennings"""
    date: str = ""
    value: float = 0.0
    target: float = 0.0
    sd: float = 0.0
    cv: float = 0.0
