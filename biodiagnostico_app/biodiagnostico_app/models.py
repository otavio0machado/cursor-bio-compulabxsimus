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


class LeveyJenningsPoint(BaseModel):
    """Ponto do gráfico Levey-Jennings"""
    date: str = ""
    value: float = 0.0
    target: float = 0.0
    sd: float = 0.0
    cv: float = 0.0
