import reflex as rx
from typing import List, Optional, Any, Dict
from pydantic import BaseModel

class AnalysisResult(BaseModel):
    """Resultado de uma análise individual"""
    patient: str = ""
    exam_name: str = ""
    value: float = 0.0
    compulab_value: float = 0.0
    simus_value: float = 0.0
    difference: float = 0.0
    compulab_count: int = 0
    simus_count: int = 0
    exams_count: int = 0
    total_value: float = 0.0


class QCRecord(BaseModel):
    """Registro de Controle de Qualidade"""
    id: str = ""
    date: str = ""
    exam_name: str = ""
    level: str = ""
    lot_number: str = ""
    value: float = 0.0  # Single value for simplified form
    value1: float = 0.0
    value2: float = 0.0
    mean: float = 0.0
    sd: float = 0.0
    cv: float = 0.0
    target_value: float = 0.0
    target_sd: float = 0.0
    equipment: str = ""
    analyst: str = ""
    status: str = ""
    westgard_violations: List[Dict[str, Any]] = []
    z_score: float = 0.0


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
    estimated_consumption: float = 0.0 # por dia
    
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


class PatientHistoryEntry(BaseModel):
    """Entrada de histórico do paciente"""
    id: str = ""
    patient_name: str = ""
    exam_name: str = ""
    status: str = ""
    last_value: float = 0.0
    notes: str = ""
    created_at: str = ""


class PatientModel(BaseModel):
    """Modelo simplificado de paciente"""
    name: str = ""
    total_exams: int = 0
    total_value: float = 0.0


class TopOffender(BaseModel):
    """Modelo de ofensor (exame/problema recorrente)"""
    name: str = ""
    count: int = 0
