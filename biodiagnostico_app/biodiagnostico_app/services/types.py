"""
TypedDicts para retornos dos services Supabase.
Cada TypedDict espelha as colunas da respectiva tabela no banco.
"""
from typing import TypedDict, Optional


class QCRecordRow(TypedDict, total=False):
    id: str
    date: str
    exam_name: str
    level: str
    lot_number: str
    value: float
    target_value: float
    target_sd: float
    equipment_name: str
    analyst_name: str
    cv: float
    status: str
    reference_id: str
    needs_calibration: bool
    post_calibration_id: str
    created_at: str


class ReagentLotRow(TypedDict, total=False):
    id: str
    name: str
    lot_number: str
    expiry_date: str
    quantity: str
    manufacturer: str
    storage_temp: str
    current_stock: float
    estimated_consumption: float
    created_at: str


class MaintenanceRecordRow(TypedDict, total=False):
    id: str
    equipment: str
    type: str
    date: str
    next_date: str
    technician: str
    notes: str
    created_at: str


class PostCalibrationRow(TypedDict, total=False):
    id: str
    qc_record_id: str
    date: str
    exam_name: str
    original_value: float
    original_cv: float
    post_calibration_value: float
    post_calibration_cv: float
    target_value: float
    analyst: str
    notes: str
    created_at: str


class QCReferenceRow(TypedDict, total=False):
    id: str
    name: str
    exam_name: str
    valid_from: str
    valid_until: str
    target_value: float
    cv_max_threshold: float
    lot_number: str
    manufacturer: str
    level: str
    notes: str
    is_active: bool
    created_at: str
    updated_at: str


class QCExamRow(TypedDict, total=False):
    id: str
    name: str
    display_order: int
    is_active: bool
    created_at: str


class QCRegistryNameRow(TypedDict, total=False):
    id: str
    name: str
    is_active: bool
    created_at: str


class HematologyQCParameterRow(TypedDict, total=False):
    id: str
    created_at: str
    updated_at: str
    analito: str
    equipamento: str
    lote_controle: str
    nivel_controle: str
    modo: str
    alvo_valor: float
    min_valor: float
    max_valor: float
    tolerancia_percentual: float
    is_active: bool
    user_id: str
    min_calc: float
    max_calc: float
    percentual_equivalente: float


class HematologyQCMeasurementRow(TypedDict, total=False):
    id: str
    created_at: str
    data_medicao: str
    analito: str
    valor_medido: float
    parameter_id: str
    modo_usado: str
    min_aplicado: float
    max_aplicado: float
    status: str
    observacao: str
    user_id: str


class HematologyBioRecordRow(TypedDict, total=False):
    id: str
    created_at: str
    data_bio: str
    data_pad: str
    registro_bio: str
    registro_pad: str
    modo_ci: str
    bio_hemacias: float
    bio_hematocrito: float
    bio_hemoglobina: float
    bio_leucocitos: float
    bio_plaquetas: float
    bio_rdw: float
    bio_vpm: float
    pad_hemacias: float
    pad_hematocrito: float
    pad_hemoglobina: float
    pad_leucocitos: float
    pad_plaquetas: float
    pad_rdw: float
    pad_vpm: float
    ci_min_hemacias: float
    ci_max_hemacias: float
    ci_min_hematocrito: float
    ci_max_hematocrito: float
    ci_min_hemoglobina: float
    ci_max_hemoglobina: float
    ci_min_leucocitos: float
    ci_max_leucocitos: float
    ci_min_plaquetas: float
    ci_max_plaquetas: float
    ci_min_rdw: float
    ci_max_rdw: float
    ci_min_vpm: float
    ci_max_vpm: float
    ci_pct_hemacias: float
    ci_pct_hematocrito: float
    ci_pct_hemoglobina: float
    ci_pct_leucocitos: float
    ci_pct_plaquetas: float
    ci_pct_rdw: float
    ci_pct_vpm: float
    user_id: str
