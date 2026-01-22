"""
Schema Pydantic para validação de Análises Salvas
Seguindo as diretrizes da skill "O Arquivista" - Validação antes de persistir
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import date, datetime


class SavedAnalysisCreate(BaseModel):
    """Schema para criar uma nova análise salva"""
    
    # Campos obrigatórios (escolhidos pelo usuário)
    analysis_name: str = Field(..., min_length=1, max_length=100, description="Nome da análise ex: 'Janeiro 2026'")
    analysis_date: date = Field(..., description="Data da análise")
    description: Optional[str] = Field(None, max_length=500)
    
    # Arquivos originais
    compulab_file_url: Optional[str] = None
    compulab_file_name: Optional[str] = None
    simus_file_url: Optional[str] = None
    simus_file_name: Optional[str] = None
    
    # Arquivos convertidos
    converted_compulab_url: Optional[str] = None
    converted_simus_url: Optional[str] = None
    
    # Relatório
    analysis_report_url: Optional[str] = None
    
    # Resumo numérico
    compulab_total: float = 0.0
    simus_total: float = 0.0
    missing_patients_count: int = 0
    missing_patients_total: float = 0.0
    missing_exams_count: int = 0
    missing_exams_total: float = 0.0
    divergences_count: int = 0
    divergences_total: float = 0.0
    extra_simus_count: int = 0
    
    # Metadados
    ai_summary: Optional[str] = None
    tags: Optional[List[str]] = None
    status: str = "completed"
    
    @validator('analysis_name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Nome da análise não pode estar vazio')
        return v.strip()
    
    @validator('compulab_total', 'simus_total', 'missing_patients_total', 'missing_exams_total', 'divergences_total')
    def validate_positive(cls, v):
        if v < 0:
            raise ValueError('Valores monetários não podem ser negativos')
        return v


class SavedAnalysisUpdate(BaseModel):
    """Schema para atualizar uma análise existente"""
    
    analysis_name: Optional[str] = None
    analysis_date: Optional[date] = None
    description: Optional[str] = None
    ai_summary: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[str] = None
    
    @validator('analysis_name')
    def validate_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Nome da análise não pode estar vazio')
        return v.strip() if v else v


class SavedAnalysisResponse(BaseModel):
    """Schema de resposta para análise salva"""
    
    id: str
    created_at: datetime
    updated_at: datetime
    analysis_name: str
    analysis_date: date
    description: Optional[str]
    
    compulab_file_url: Optional[str]
    compulab_file_name: Optional[str]
    simus_file_url: Optional[str]
    simus_file_name: Optional[str]
    
    compulab_total: float
    simus_total: float
    difference: float
    missing_patients_count: int
    missing_exams_count: int
    divergences_count: int
    
    status: str
    tags: Optional[List[str]]


class AnalysisItemCreate(BaseModel):
    """Schema para criar item de uma análise"""
    
    analysis_id: str
    item_type: str = Field(..., pattern='^(missing_patient|missing_exam|divergence|extra_simus)$')
    
    patient_name: Optional[str] = None
    exam_name: Optional[str] = None
    compulab_value: Optional[float] = None
    simus_value: Optional[float] = None
    difference: Optional[float] = None
    exams_count: Optional[int] = None
    
    is_resolved: bool = False
    resolution_notes: Optional[str] = None


class AnalysisItemUpdate(BaseModel):
    """Schema para atualizar resolução de item"""
    
    is_resolved: Optional[bool] = None
    resolution_notes: Optional[str] = None


# Helpers para converter dicts em models
def analysis_to_dict(analysis: SavedAnalysisCreate) -> dict:
    """Converte o schema para dict pronto para Supabase"""
    data = analysis.dict(exclude_none=True)
    # Converter date para string ISO
    if 'analysis_date' in data:
        data['analysis_date'] = data['analysis_date'].isoformat()
    return data
