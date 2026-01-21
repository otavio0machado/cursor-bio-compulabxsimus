"""
State management for Biodiagnóstico App
Otimizado para arquivos grandes com processamento assíncrono
"""
import reflex as rx
from decimal import Decimal
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel
import asyncio
from concurrent.futures import ThreadPoolExecutor
import gc
import tempfile
import os
import shutil
from .services import cloudinary_service
from .services.supabase_client import supabase
from .services.qc_service import QCService
from .services.reagent_service import ReagentService
from .services.maintenance_service import MaintenanceService
from .services.audit_service import AuditService
from .config import Config
from .models import AnalysisResult, QCRecord, ReagentLot, MaintenanceRecord, LeveyJenningsPoint, PatientHistoryEntry, PatientModel, TopOffender
from .models import AnalysisResult, QCRecord, ReagentLot, MaintenanceRecord, LeveyJenningsPoint, PatientHistoryEntry, PatientModel, TopOffender
from .utils.westgard import WestgardRules
import pdfplumber
import pandas as pd
import io
from .utils.qc_pdf_report import generate_qc_pdf
import base64
from datetime import timedelta
import calendar


class State(rx.State):
    # Lista restrita de exames permitidos no QC (Solicitação do Usuário)
    ALLOWED_QC_EXAMS: List[str] = [
        "GLICOSE Cal",
        "COLESTEROL",
        "TRIGLICERIDIOS",
        "UREIA",
        "CREATININA P",
        "AC. URICO",
        "TGO",
        "TGP",
        "GGT",
        "FAL DGKC 137 131",
        "AMILASE",
        "CPK Total",
        "P HDL eva 50",
        "COLESTEROL 2 P200"
    ]

    """Estado global da aplicação"""
    
    # Autenticação - Login único
    is_authenticated: bool = False
    login_email: str = ""
    login_password: str = ""
    login_error: str = ""
    
    # Credenciais válidas (login único)
    _valid_email: str = "evandrotorresmachado@gmail.com"
    _valid_password: str = "eva123"
    
    # Navegação
    current_page: str = "dashboard"
    
    # Arquivos
    compulab_file_name: str = ""
    simus_file_name: str = ""
    compulab_file_path: str = ""  # Caminho do arquivo temporário COMPULAB
    simus_file_path: str = ""  # Caminho do arquivo temporário SIMUS
    compulab_file_url: str = "" # URL do arquivo no Cloudinary
    simus_file_url: str = "" # URL do arquivo no Cloudinary
    compulab_file_bytes: bytes = b""  # Mantido para compatibilidade, mas não usado para arquivos grandes
    simus_file_bytes: bytes = b""  # Mantido para compatibilidade, mas não usado para arquivos grandes
    compulab_file_size_bytes: int = 0
    simus_file_size_bytes: int = 0

    is_uploading: bool = False
    
    # Limites de upload
    MAX_FILE_SIZE_MB: int = 50
    
    # Resultados da análise
    compulab_total: float = 0.0
    simus_total: float = 0.0
    compulab_count: int = 0
    simus_count: int = 0
    sigtap_val: float = 0.0
    contratualizado_val: float = 0.0
    
    # Resultados da comparação
    missing_patients: List[PatientModel] = []
    missing_exams: List[AnalysisResult] = []
    value_divergences: List[AnalysisResult] = []
    extra_simus_exams: List[AnalysisResult] = []
    
    # Breakdown da diferença
    missing_patients_total: float = 0.0
    missing_exams_total: float = 0.0
    divergences_total: float = 0.0
    explained_total: float = 0.0
    residual: float = 0.0
    
    # AI Progress State
    ai_loading_progress: int = 0
    ai_loading_text: str = ""
    
    # AI Results Data (Structured)
    ai_analysis_data: List[Dict[str, Any]] = []
    ai_analysis_csv: str = ""  # CSV data URI para download
    ai_analysis_csv: str = ""  # CSV data URI para download
    ai_provider: str = "OpenAI"  # OpenAI ou Gemini
    ai_model: str = "gpt-4o"  # Modelo específico selecionado
    
    # CSVs gerados
    compulab_csv: str = ""
    simus_csv: str = ""
    csv_generated: bool = False
    
    # Resumo persistente da última análise (QA Improvement)
    last_audit_summary: Dict[str, Any] = {}
    
    # Estado de carregamento
    is_loading: bool = False
    is_analyzing: bool = False
    is_generating_csv: bool = False
    is_generating_ai: bool = False
    
    # Divergence Resolution & Patient History
    resolutions: Dict[str, str] = {} # Key: "patient_name|exam_name"
    patient_history_data: List[PatientHistoryEntry] = []
    patient_history_search: str = ""
    selected_patient_name: str = ""
    is_showing_patient_history: bool = False
    resolution_notes: str = ""
    analysis_active_tab: str = "patients_missing"

    def set_analysis_active_tab(self, val: str):
        self.analysis_active_tab = val

    def set_ai_provider(self, val: str):
        self.ai_provider = val
        # Definir defaults ao trocar de provedor
        if val == "OpenAI":
            self.ai_model = "gpt-4o"
        elif val == "Gemini":
            self.ai_model = "gemini-2.5-flash"

    def set_ai_model(self, val: str):
        self.ai_model = val
    
    def set_patient_history_search(self, val: str):
        self.patient_history_search = val
    
    # Financial Forecast & Goals
    
    def calculate_sd(self):
        """Calcula o Desvio Padrão (Diferença Absoluta) automaticamente"""
        try:
            if not self.qc_value or not self.qc_target_value:
                return
            
            # Tratar inputs
            val_str = self.qc_value.replace(",", ".")
            target_str = self.qc_target_value.replace(",", ".")
            
            if not val_str or not target_str:
                return

            value = float(val_str)
            target = float(target_str)
            
            # Desvio Padrão = Diferença Absoluta entre Medição e Alvo
            # Solicitado pelo usuário para representar o 'Desvio' do registro
            sd = abs(value - target)
            self.qc_target_sd = f"{sd:.2f}"
            
        except Exception:
            pass

    def update_qc_value(self, value: str):
        """Atualiza valor da medição e recalcula SD"""
        self.qc_value = value
        self.calculate_sd()
        
    def update_qc_target_value(self, value: str):
        """Atualiza valor alvo e recalcula SD"""
        self.qc_target_value = value
        self.calculate_sd()

    
    # Internal Data (Backend Only)
    _compulab_patients: Dict[str, Any] = {}
    _simus_patients: Dict[str, Any] = {}
    audit_history: List[Dict[str, Any]] = []
    revenue_forecast: float = 0.0
    monthly_goal: float = 50000.0 # Meta padrão
    
    @rx.var
    def goal_progress(self) -> float:
        """Percentual de atingimento da meta"""
        if self.monthly_goal > 0:
            # Usar compulab_total como referência de faturamento realizado
            return min(100.0, (self.compulab_total / self.monthly_goal) * 100)
        return 0.0

    @rx.var
    def selected_patient_exams_count(self) -> int:
        """Quantidade de exames no histórico do paciente selecionado"""
        return len(self.patient_history_data)

    @rx.var
    def selected_patient_total_value(self) -> str:
        """Valor total acumulado dos exames no histórico"""
        total = sum(item.last_value for item in self.patient_history_data)
        return f"{total:,.2f}"

    @rx.var
    def selected_patient_id(self) -> str:
        """Retorna o ID do paciente (baseado no primeiro registro do histórico)"""
        if self.patient_history_data:
            return self.patient_history_data[0].id[:8].upper()
        return "---"

    @rx.var
    def resolution_progress(self) -> int:
        """Percentual de divergências resolvidas na análise atual"""
        total = len(self.missing_exams) + len(self.value_divergences) + len(self.extra_simus_exams)
        if total == 0:
            return 100
            
        resolved_count = 0
        all_items = self.missing_exams + self.value_divergences + self.extra_simus_exams
        
        for item in all_items:
            patient = getattr(item, 'patient', '')
            exam = getattr(item, 'exam_name', '')
            if self.resolutions.get(f"{patient}|{exam}") == "resolvido":
                resolved_count += 1
                
        return int((resolved_count / total) * 100)
    
    # ===== Dashboard Analytics - Chart Data Aggregators =====
    
    def _safe_get_attr(self, item: Any, key: str, default: Any = "") -> Any:
        """Helper to safely extract attribute from dict or object"""
        if isinstance(item, dict):
            return item.get(key, default)
        return getattr(item, key, default)
    
    def _format_currency_br(self, value: float) -> str:
        """Format value as Brazilian currency"""
        return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    @rx.var
    def revenue_distribution_data(self) -> List[Dict[str, Any]]:
        """Data for pie/donut chart showing composition of revenue leakage"""
        data = []
        
        # Cores consistentes com o design system
        if self.missing_patients_total > 0:
            data.append({
                "name": "Pacientes Faltantes", 
                "value": round(self.missing_patients_total, 2), 
                "fill": "#F59E0B"  # Amber
            })
        if self.missing_exams_total > 0:
            data.append({
                "name": "Exames Faltantes", 
                "value": round(self.missing_exams_total, 2), 
                "fill": "#EF4444"  # Red
            })
        if self.divergences_total > 0:
            data.append({
                "name": "Divergências de Valor", 
                "value": round(self.divergences_total, 2), 
                "fill": "#3B82F6"  # Blue
            })
        
        # Calcular valor dos exames fantasma (extras no SIMUS)
        extras_total = sum(
            float(self._safe_get_attr(item, 'simus_value', 0) or self._safe_get_attr(item, 'value', 0))
            for item in self.extra_simus_exams
        )
        if extras_total > 0:
            data.append({
                "name": "Extras no SIMUS",
                "value": round(extras_total, 2),
                "fill": "#6B7280"  # Gray
            })
        
        # Placeholder quando não há divergências
        if not data:
            data.append({
                "name": "✓ Sem Divergências", 
                "value": 1, 
                "fill": "#10B981"  # Green
            })
        
        return data
    
    @rx.var
    def total_revenue_leakage(self) -> float:
        """Total de perda financeira identificada"""
        extras_total = sum(
            float(self._safe_get_attr(item, 'simus_value', 0) or self._safe_get_attr(item, 'value', 0))
            for item in self.extra_simus_exams
        )
        return self.missing_patients_total + self.missing_exams_total + self.divergences_total + extras_total
    
    @rx.var
    def formatted_total_leakage(self) -> str:
        """Total de perda formatado em BRL"""
        return self._format_currency_br(self.total_revenue_leakage)
    
    @rx.var
    def top_exams_discrepancy_data(self) -> List[Dict[str, Any]]:
        """Data for bar chart showing top 7 exams contributing to financial impact"""
        exam_values: Dict[str, float] = {}
        
        # Agregar valores de exames faltantes
        for item in self.missing_exams:
            name = str(self._safe_get_attr(item, 'exam_name', ''))
            value = float(self._safe_get_attr(item, 'value', 0) or 0)
            if name:
                exam_values[name] = exam_values.get(name, 0) + value
        
        # Agregar diferenças absolutas de divergências
        for item in self.value_divergences:
            name = str(self._safe_get_attr(item, 'exam_name', ''))
            diff = float(self._safe_get_attr(item, 'difference', 0) or 0)
            if name:
                exam_values[name] = exam_values.get(name, 0) + abs(diff)
        
        # Agregar valores de exames fantasma
        for item in self.extra_simus_exams:
            name = str(self._safe_get_attr(item, 'exam_name', ''))
            value = float(self._safe_get_attr(item, 'simus_value', 0) or self._safe_get_attr(item, 'value', 0) or 0)
            if name:
                exam_values[name] = exam_values.get(name, 0) + value
        
        # Ordenar por impacto financeiro e limitar a 7
        sorted_exams = sorted(exam_values.items(), key=lambda x: x[1], reverse=True)[:7]
        
        # Truncar nomes longos para melhor visualização
        return [
            {"name": (name[:18] + "…" if len(name) > 18 else name), "value": round(val, 2)} 
            for name, val in sorted_exams
        ]
    
    @rx.var
    def action_center_insights(self) -> List[Dict[str, str]]:
        """Auto-generated insights and recommended actions with smart priority"""
        insights = []
        
        # Calcular impacto para priorização inteligente
        total_leakage = self.total_revenue_leakage
        
        # Insight 1: Pacientes faltantes (alta prioridade se impacto > 30%)
        if self.missing_patients_count > 0:
            impact_pct = (self.missing_patients_total / total_leakage * 100) if total_leakage > 0 else 0
            priority = "high" if impact_pct > 30 or self.missing_patients_total > 1000 else "medium"
            insights.append({
                "icon": "users",
                "title": f"Verificar {self.missing_patients_count} pacientes no SIMUS",
                "description": f"Impacto: {self._format_currency_br(self.missing_patients_total)} ({impact_pct:.1f}% do total)",
                "priority": priority,
                "action_type": "patients_missing"
            })
        
        # Insight 2: Exames faltantes
        if self.missing_exams_count > 0:
            impact_pct = (self.missing_exams_total / total_leakage * 100) if total_leakage > 0 else 0
            priority = "high" if self.missing_exams_count > 10 or impact_pct > 25 else "medium"
            insights.append({
                "icon": "file-warning",
                "title": f"Auditar {self.missing_exams_count} exames não integrados",
                "description": f"Recuperação potencial: {self._format_currency_br(self.missing_exams_total)}",
                "priority": priority,
                "action_type": "missing"
            })
        
        # Insight 3: Top Offender (exame mais problemático)
        if self.top_offenders:
            top = self.top_offenders[0]
            insights.append({
                "icon": "target",
                "title": f"Revisar exame '{top.name[:25]}'",
                "description": f"Aparece {top.count}x nas divergências. Verifique a tabela TUSS/CBHPM.",
                "priority": "medium",
                "action_type": "divergences"
            })
        
        # Insight 4: Exames fantasma
        if self.extra_simus_exams_count > 0:
            insights.append({
                "icon": "ghost",
                "title": f"Investigar {self.extra_simus_exams_count} exames 'fantasma'",
                "description": "Presentes no SIMUS mas não no COMPULAB. Possível duplicidade.",
                "priority": "low",
                "action_type": "extras"
            })
        
        # Estado de sucesso
        if not insights:
            insights.append({
                "icon": "check-circle",
                "title": "Auditoria Perfeita! ✓",
                "description": "Nenhuma divergência significativa identificada entre os sistemas.",
                "priority": "success",
                "action_type": ""
            })
        
        return insights[:4]

    
    # Progresso do processamento (para arquivos grandes)
    processing_progress: int = 0
    processing_total: int = 0
    processing_status: str = ""
    
    # Progresso da conversão CSV
    csv_progress_percentage: int = 0
    csv_stage: str = ""
    
    # Progresso da análise
    analysis_progress_percentage: int = 0
    analysis_stage: str = ""
    
    # Mensagens
    error_message: str = ""
    success_message: str = ""
    
    # Análise por IA
    ai_analysis: str = ""
    
    # PDF da análise
    analysis_pdf: str = ""
    
    # Dados armazenados para análise
    _compulab_patients: Dict = {}
    _simus_patients: Dict = {}
    _excel_dataframe: Any = None
    
    # ===== ProIn - Análise de Planilhas Excel =====
    excel_file_name: str = ""
    excel_file_bytes: bytes = b""
    excel_analyzed: bool = False
    is_analyzing_excel: bool = False
    excel_success_message: str = ""
    excel_error_message: str = ""
    
    # Resultados da análise Excel
    excel_total_rows: int = 0
    excel_total_columns: int = 0
    excel_filled_cells: int = 0
    excel_empty_cells: int = 0
    excel_headers: List[str] = []
    excel_columns_info: List[Dict[str, Any]] = []
    excel_numeric_summary: List[Dict[str, Any]] = []
    excel_preview: List[List[str]] = []
    _excel_dataframe: Any = None
    
    # ===== ProIn QC - Sistema de Controle de Qualidade =====
    proin_current_tab: str = "dashboard"  # dashboard, registro, reagentes, relatorios, importar
    
    # Registros de CQ (Controle de Qualidade)
    qc_records: List[QCRecord] = []  # Lista de registros de CQ
    qc_exam_name: str = ""
    qc_level: str = "Normal"  # Normal, Patológico
    qc_lot_number: str = ""
    qc_value: str = ""  # Valor da medição (single value for simplified form)
    qc_value1: str = ""
    qc_value2: str = ""
    qc_target_value: str = ""
    qc_target_sd: str = ""
    qc_equipment: str = ""
    qc_analyst: str = ""
    qc_date: str = ""
    is_saving_qc: bool = False
    qc_success_message: str = ""
    qc_error_message: str = ""
    
    # Cache and Performance Control
    _last_db_sync: Optional[datetime] = None
    _CACHE_TTL_MINUTES: int = 5
    
    async def load_data_from_db(self, force: bool = False):
        """
        Carrega dados do Supabase para o estado local com sistema de cache de 5 minutos.
        Se 'force' for True, ignora o cache e recarrega.
        """
        if not supabase:
            print("Supabase não configurado. Usando armazenamento em memória.")
            return

        # Sistema de Cache simples
        if not force and self._last_db_sync:
            diff = datetime.now() - self._last_db_sync
            if diff.total_seconds() < (self._CACHE_TTL_MINUTES * 60):
                print(f"DEBUG: Usando cache de dados (última sync há {diff.total_seconds():.0f}s)")
                return

        print("DEBUG: Sincronizando dados com Supabase...")
        try:
            # Carregar QC Records
            qc_data = await QCService.get_qc_records(limit=100)
            self.qc_records = [
                QCRecord(
                    id=str(r.get("id", "")),
                    date=r.get("date", ""),
                    exam_name=r.get("exam_name", ""),
                    level=r.get("level", ""),
                    lot_number=r.get("lot_number", ""),
                    value=float(r.get("value", 0)),
                    target_value=float(r.get("target_value", 0)),
                    target_sd=float(r.get("target_sd", 0)),
                    cv=float(r.get("cv", 0)) if r.get("cv") is not None else 0.0,
                    equipment=r.get("equipment_name", ""),
                    analyst=r.get("analyst_name", ""),
                    status=r.get("status", "")
                ) for r in qc_data if r.get("exam_name") in self.ALLOWED_QC_EXAMS
            ]
            
            # Carregar Reagentes
            reagent_data = await ReagentService.get_active_lots()
            self.reagent_lots = [
                ReagentLot(
                    id=str(r.get("id", "")),
                    name=r.get("name", ""),
                    lot_number=r.get("lot_number", ""),
                    expiry_date=r.get("expiry_date", ""),
                    quantity=r.get("quantity", ""),
                    manufacturer=r.get("manufacturer", ""),
                    storage_temp=r.get("storage_temp", ""),
                    created_at=r.get("created_at", ""),
                    days_left=0, # Calculado na property
                    current_stock=float(r.get("current_stock", 0)) if r.get("current_stock") else 0.0,
                    estimated_consumption=float(r.get("estimated_consumption", 0)) if r.get("estimated_consumption") else 0.0
                ) for r in reagent_data
            ]
            
            # Carregar Manutenções
            maint_data = await MaintenanceService.get_recent_maintenances()
            self.maintenance_records = [
                MaintenanceRecord(
                    id=str(r.get("id", "")),
                    equipment=r.get("equipment_name", ""),
                    type=r.get("type", ""),
                    date=r.get("date", ""),
                    next_date=r.get("next_date", ""),
                    technician=r.get("technician_name", ""),
                    notes=r.get("notes", ""),
                    created_at=r.get("created_at", "")
                ) for r in maint_data
            ]
            
            # Carregar Último Resumo de Auditoria (QA Improvement)
            audit_summary = await AuditService.get_latest_audit_summary()
            if audit_summary:
                self.last_audit_summary = audit_summary
            
            # Carregar Histórico e Calcular Forecast (Novo)
            self.audit_history = await AuditService.get_audit_history(limit=6)
            self.calculate_forecast()

            # Carregar Resoluções (Novo)
            await self.load_resolutions()
            
            # Atualizar marcador de cache
            self._last_db_sync = datetime.now()
            
        except Exception as e:
            print(f"Erro ao carregar dados do Supabase: {e}")
            # Não falhar silenciosamente, talvez setar msg erro global?

    
    # Gestão de Reagentes/Lotes
    reagent_lots: List[ReagentLot] = []
    reagent_name: str = ""
    reagent_lot_number: str = ""
    reagent_expiry_date: str = ""
    reagent_quantity: str = ""
    reagent_manufacturer: str = ""
    reagent_storage_temp: str = ""
    reagent_initial_stock: str = ""
    reagent_daily_consumption: str = ""
    is_saving_reagent: bool = False
    reagent_success_message: str = ""
    reagent_error_message: str = ""
    
    # Equipamentos e Manutenções
    equipment_list: List[str] = []
    maintenance_records: List[MaintenanceRecord] = []
    maintenance_equipment: str = ""
    maintenance_type: str = ""
    maintenance_date: str = ""
    maintenance_next_date: str = ""
    maintenance_technician: str = ""
    maintenance_notes: str = ""
    is_saving_maintenance: bool = False
    maintenance_success_message: str = ""
    maintenance_error_message: str = ""
    
    # Gráfico Levey-Jennings
    levey_jennings_data: List[LeveyJenningsPoint] = []
    levey_jennings_exam: str = ""
    levey_jennings_period: str = "30"  # dias
    
    # Alertas do Dashboard
    qc_alerts: List[QCRecord] = []
    expiring_lots: List[ReagentLot] = []
    
    # Relatórios PDF - QC
    qc_report_type: str = "Mês Atual"  # "Mês Atual", "Mês Específico", "3 Meses", "6 Meses", "Ano Atual", "Ano Específico"
    qc_report_month: str = str(datetime.now().month)
    qc_report_year: str = str(datetime.now().year)
    
    def set_qc_report_type(self, value: str):
        self.qc_report_type = value
        
    def set_qc_report_month(self, value: str):
        self.qc_report_month = value
        
    def set_qc_report_year(self, value: str):
        self.qc_report_year = value

    is_generating_qc_report: bool = False
    
    async def generate_qc_report_pdf(self):
        """Gera PDF das tabelas de QC baseado nos filtros"""
        self.is_generating_qc_report = True
        yield
        
        try:
            # Definir intervalo de datas
            now = datetime.now()
            start_date = None
            end_date = None
            period_desc = ""
            
            if self.qc_report_type == "Mês Atual":
                start_date = now.replace(day=1).date().isoformat()
                end_date = now.date().isoformat()
                period_desc = f"Mês Atual ({now.strftime('%B/%Y')})"
                
            elif self.qc_report_type == "Mês Específico":
                try:
                    month = int(self.qc_report_month)
                    year = int(self.qc_report_year)
                    last_day = calendar.monthrange(year, month)[1]
                    start_date = f"{year}-{month:02d}-01"
                    end_date = f"{year}-{month:02d}-{last_day}"
                    period_desc = f"{month:02d}/{year}"
                except:
                    self.qc_error_message = "Mês/Ano inválidos"
                    self.is_generating_qc_report = False
                    return

            elif self.qc_report_type == "3 Meses":
                start_date = (now - timedelta(days=90)).date().isoformat()
                end_date = now.date().isoformat()
                period_desc = "Últimos 3 Meses"

            elif self.qc_report_type == "6 Meses":
                start_date = (now - timedelta(days=180)).date().isoformat()
                end_date = now.date().isoformat()
                period_desc = "Últimos 6 Meses"
                
            elif self.qc_report_type == "Ano Atual":
                start_date = f"{now.year}-01-01"
                end_date = f"{now.year}-12-31"
                period_desc = f"Ano {now.year}"

            elif self.qc_report_type == "Ano Específico":
                try:
                    year = int(self.qc_report_year)
                    start_date = f"{year}-01-01"
                    end_date = f"{year}-12-31"
                    period_desc = f"Ano {year}"
                except:
                    self.qc_error_message = "Ano inválido"
                    self.is_generating_qc_report = False
                    return

            # Buscar dados (Limitando a 2000 registros para não estourar)
            records = await QCService.get_qc_records(
                limit=5000,
                start_date=start_date,
                end_date=end_date
            )
            
            if not records:
                self.qc_error_message = "Nenhum registro encontrado no período."
                return

            # Gerar PDF
            pdf_bytes = generate_qc_pdf(records, period_desc)
            
            # Download via Javascript (usando rx.download - mas state não supporta direct return aqui fácil, 
            # vamos usar scheme de download via base64 ou salvar em public?
            # Melhor: Retornar rx.download direto no handler event handler, mas aqui é async task.
            # Vamos salvar em temp e retornar rx.download? Nao, rx.download aceita data: url.
            
            b64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
            yield rx.download(
                data=f"data:application/pdf;base64,{b64_pdf}",
                filename=f"QC_Report_{period_desc.replace('/', '_').replace(' ', '_')}.pdf"
            )

        except Exception as e:
            print(f"Erro ao gerar PDF QC: {e}")
            self.qc_error_message = f"Erro na geração do PDF: {str(e)}"
        
        finally:
            self.is_generating_qc_report = False
    
    # Estatísticas do Dashboard
    total_qc_today: int = 0
    total_qc_month: int = 0
    qc_approval_rate: float = 0.0
    pending_maintenances: int = 0
    
    @rx.var
    def has_analysis(self) -> bool:
        """Verifica se há análise disponível"""
        return self.compulab_total > 0 or self.simus_total > 0
    
    @rx.var
    def difference(self) -> float:
        """Diferença entre COMPULAB e SIMUS"""
        return self.compulab_total - self.simus_total
    
    @rx.var
    def formatted_revenue_forecast(self) -> str:
        """Previsão de receita formatada"""
        return f"R$ {self.revenue_forecast:,.2f}"

    @rx.var
    def formatted_monthly_goal(self) -> str:
        """Meta mensal formatada"""
        return f"R$ {self.monthly_goal:,.2f}"
    
    @rx.var
    def difference_percent(self) -> float:
        """Percentual de diferença"""
        if self.simus_total > 0:
            return (self.difference / self.simus_total) * 100
        return 0.0

    def share_on_whatsapp(self, message: str):
        """Abre o WhatsApp com uma mensagem pré-definida"""
        import urllib.parse
        encoded_msg = urllib.parse.quote(message)
        return rx.redirect(f"https://wa.me/?text={encoded_msg}")

    @rx.var
    def extra_simus_exams_count(self) -> int:
        """Quantidade de exames extras no SIMUS (fantasmas)"""
        return len(self.extra_simus_exams)

    @rx.var
    def missing_exams_count(self) -> int:
        """Quantidade de exames faltantes"""
        return len(self.missing_exams)
    
    @rx.var
    def divergences_count(self) -> int:
        """Quantidade de divergências (sessão ou persistente)"""
        count = len(self.value_divergences)
        if count == 0 and self.last_audit_summary:
            count = int(self.last_audit_summary.get("divergences_count", 0))
        return count
    
    @rx.var
    def total_patients_count(self) -> int:
        """Total de pacientes processados"""
        count = self.compulab_count + self.simus_count
        if count == 0 and self.last_audit_summary:
            count = int(self.last_audit_summary.get("missing_patients_count", 0)) # Simplificação (na verdade seria a soma se tivessemos)
            # Na verdade, se o resumo não tem o total de pacientes, usamos o que temos.
        return count
    
    @rx.var
    def missing_patients_count(self) -> int:
        """Quantidade de pacientes faltantes"""
        return len(self.missing_patients)
    
    @rx.var
    def has_files(self) -> bool:
        """Verifica se ambos os arquivos foram carregados"""
        # Verificar se os arquivos existem no disco ou se há bytes (compatibilidade)
        compulab_ok = (self.compulab_file_path and os.path.exists(self.compulab_file_path)) or len(self.compulab_file_bytes) > 0
        simus_ok = (self.simus_file_path and os.path.exists(self.simus_file_path)) or len(self.simus_file_bytes) > 0
        return compulab_ok and simus_ok
    
    @rx.var
    def compulab_file_size(self) -> str:
        """Tamanho do arquivo COMPULAB formatado"""
        if self.compulab_file_size_bytes == 0:
            return ""
        size_kb = self.compulab_file_size_bytes / 1024
        if size_kb < 1024:
            return f"{size_kb:.1f} KB"
        size_mb = size_kb / 1024
        return f"{size_mb:.1f} MB"
    
    @rx.var
    def simus_file_size(self) -> str:
        """Tamanho do arquivo SIMUS formatado"""
        if self.simus_file_size_bytes == 0:
            return ""
        size_kb = self.simus_file_size_bytes / 1024
        if size_kb < 1024:
            return f"{size_kb:.1f} KB"
        size_mb = size_kb / 1024
        return f"{size_mb:.1f} MB"
    
    @rx.var
    def has_excel_file(self) -> bool:
        """Verifica se o arquivo Excel foi carregado"""
        return len(self.excel_file_bytes) > 0
    
    @rx.var
    def formatted_compulab_total(self) -> str:
        """Total COMPULAB formatado"""
        return f"R$ {self.compulab_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    
    
    @rx.var
    def formatted_simus_total(self) -> str:
        """Total SIMUS formatado"""
        return f"R$ {self.simus_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    @rx.var
    def formatted_difference(self) -> str:
        """Diferença formatada"""
        return f"R$ {self.difference:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    @rx.var
    def formatted_missing_patients_total(self) -> str:
        """Total de pacientes faltantes formatado"""
        return f"R$ {self.missing_patients_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    @rx.var
    def formatted_missing_exams_total(self) -> str:
        """Total de exames faltantes formatado"""
        return f"R$ {self.missing_exams_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    @rx.var
    def formatted_divergences_total(self) -> str:
        """Total de divergências formatado"""
        return f"R$ {self.divergences_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    @rx.var
    def processing_progress_text(self) -> str:
        """Texto de progresso do processamento"""
        if self.processing_total == 0:
            return self.processing_status
        pct = int((self.processing_progress / self.processing_total) * 100)
        return f"{self.processing_status} ({pct}% - {self.processing_progress}/{self.processing_total})"
    
    @rx.var
    def is_large_file_processing(self) -> bool:
        """Verifica se está processando um arquivo grande"""
        return self.is_analyzing and self.processing_total > 0
    
    @rx.var
    def qc_calculated_cv(self) -> str:
        """Calcula a Variação Percentual automaticamente em relação ao alvo"""
        try:
            if not self.qc_value or not self.qc_target_value:
                return "0.00"
            
            value = float(self.qc_value.replace(",", "."))
            target = float(self.qc_target_value.replace(",", "."))
            
            if target <= 0:
                return "0.00"
            
            # Variação% = ((Valor - Alvo) / Alvo) * 100
            cv = ((value - target) / target) * 100
            return f"{cv:.2f}"
        except (ValueError, ZeroDivisionError):
            return "0.00"
    
    @rx.var
    def qc_cv_status(self) -> str:
        """Returns status based on |Variação%|: 'ok' (≤5%), 'warning' (5-10%), 'error' (>10%)"""
        try:
            cv_str = self.qc_calculated_cv
            cv = abs(float(cv_str))
            if cv <= 5.0:
                return "ok"
            elif cv <= 10.0:
                return "warning"
            else:
                return "error"
        except (ValueError, TypeError):
            return "ok"
    
    @rx.var
    def unique_exam_names(self) -> List[str]:
        """Retorna lista única de nomes de exames para o dropdown (Restrita conforme solicitação)"""
        return sorted(self.ALLOWED_QC_EXAMS)

    # ===== Dashboard - Financial Scoreboard =====
    financial_target_daily: float = 15000.00
    financial_last_day: float = 12000.00 # Mock value for comparison
    
    @rx.var
    def financial_growth_day(self) -> float:
        """Crescimento diário (comparado com valor mockado anterior)"""
        if self.financial_last_day == 0: return 0.0
        if self.compulab_total == 0: return 0.0
        
        # Usando compulab_total como 'hoje' se houver, senão 0
        current = self.compulab_total
        return ((current - self.financial_last_day) / self.financial_last_day) * 100

    @rx.var
    def financial_performance_color(self) -> str:
        return "success" if self.financial_growth_day >= 0 else "error"
        
    # ===== Dashboard - Top Offenders =====
    @rx.var
    def top_offenders(self) -> List[TopOffender]:
        """Retorna os top 5 exames com problemas (faltantes ou divergentes)"""
        counts = {}
        
        # Contar exames faltantes
        for item in self.missing_exams:
            name = item.get("exam_name", "") if isinstance(item, dict) else getattr(item, "exam_name", "")
            if name:
                counts[name] = counts.get(name, 0) + 1
            
        # Contar divergências
        for item in self.value_divergences:
            name = item.get("exam_name", "") if isinstance(item, dict) else getattr(item, "exam_name", "")
            if name:
                counts[name] = counts.get(name, 0) + 1
            
        # Contar exames extras (fantasmas)
        for item in self.extra_simus_exams:
            name = item.get("exam_name", "") if isinstance(item, dict) else getattr(item, "exam_name", "")
            if name:
                counts[name] = counts.get(name, 0) + 1
            
        # Ordenar e pegar top 5
        sorted_exams = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return [TopOffender(name=str(name), count=int(count)) for name, count in sorted_exams]
    
    def set_login_email(self, email: str):
        """Define o email de login"""
        self.login_email = email
        self.login_error = ""
    
    def set_login_password(self, password: str):
        """Define a senha de login"""
        self.login_password = password
        self.login_error = ""
    
    def attempt_login(self):
        """Tenta realizar o login"""
        email = self.login_email.strip().lower()
        password = self.login_password
        
        if email == self._valid_email and password == self._valid_password:
            self.is_authenticated = True
            self.login_error = ""
            self.login_email = ""
            self.login_password = ""
        else:
            self.login_error = "E-mail ou senha incorretos"
            self.is_authenticated = False
    
    async def logout(self):
        """Realiza logout do sistema"""
        # Delay para fechar Menu e evitar warning 'aria-hidden'
        await asyncio.sleep(0.2)
        self.is_authenticated = False
        self.login_email = ""
        self.login_password = ""
        self.login_error = ""
        self.current_page = "dashboard" # Resetar para home/dashboard por padrão
    
    def set_page(self, page: str):
        """Navega para uma página"""
        self.current_page = page
        self.error_message = ""
        self.success_message = ""
    
    def clear_messages(self):
        """Limpa mensagens de erro e sucesso"""
        self.error_message = ""
        self.success_message = ""
    
    def _validate_file(self, file_name: str, file_bytes: bytes) -> tuple[bool, str]:
        """Valida um arquivo (tipo e tamanho)"""
        # Verificar extensão
        valid_extensions = ['.pdf', '.csv']
        file_ext = file_name.lower()[-4:] if len(file_name) > 4 else ""
        if not any(file_ext.endswith(ext) for ext in valid_extensions):
            return False, f"Tipo de arquivo inválido. Aceitos: PDF, CSV"
        
        # Verificar tamanho
        max_size_bytes = self.MAX_FILE_SIZE_MB * 1024 * 1024
        if len(file_bytes) > max_size_bytes:
            return False, f"Arquivo muito grande. Máximo: {self.MAX_FILE_SIZE_MB}MB"
        
        # Verificar se não está vazio
        if len(file_bytes) == 0:
            return False, "Arquivo está vazio"
        
        return True, ""
    
    async def handle_compulab_upload(self, files: List[rx.UploadFile]):
        """Processa upload do arquivo COMPULAB - Salva em disco para evitar travamento"""
        if not files:
            return
        
        self.is_uploading = True
        self.error_message = ""
        self.success_message = ""
        self.processing_status = "📤 Carregando arquivo COMPULAB..."
        
        # Limpar arquivo anterior se existir
        if self.compulab_file_path and os.path.exists(self.compulab_file_path):
            try:
                os.unlink(self.compulab_file_path)
            except:
                pass
        
        tmp_file_path = None
        
        try:
            file = files[0]
            
            # Criar arquivo temporário
            file_ext = os.path.splitext(file.name)[1] or '.pdf'
            tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_ext)
            tmp_file_path = tmp_file.name
            tmp_file.close()
            
            self.processing_status = "💾 Salvando arquivo em disco..."
            await asyncio.sleep(0.01)  # Yield para UI
            
            # Salvar arquivo em disco em chunks (não carrega tudo na memória)
            chunk_size = 1024 * 1024  # 1MB por chunk
            total_size = 0
            
            with open(tmp_file_path, 'wb') as f:
                while True:
                    chunk = await file.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    total_size += len(chunk)
                    
                    # Yield periodicamente para não travar
                    if total_size % (5 * 1024 * 1024) == 0:  # A cada 5MB
                        await asyncio.sleep(0.01)
                        self.processing_status = f"💾 Salvando... {total_size / (1024*1024):.1f} MB"
            
            # Validar tamanho do arquivo
            if total_size == 0:
                self.error_message = "ERRO: COMPULAB: Arquivo está vazio"
                if tmp_file_path and os.path.exists(tmp_file_path):
                    os.unlink(tmp_file_path)
                return
            
            max_size_bytes = self.MAX_FILE_SIZE_MB * 1024 * 1024
            if total_size > max_size_bytes:
                self.error_message = f"ERRO: COMPULAB: Arquivo muito grande. Máximo: {self.MAX_FILE_SIZE_MB}MB"
                if tmp_file_path and os.path.exists(tmp_file_path):
                    os.unlink(tmp_file_path)
                return
            
            # Validar extensão
            valid_extensions = ['.pdf', '.csv', '.xlsx', '.xls', '.xsl']
            if not any(file.name.lower().endswith(ext) for ext in valid_extensions):
                self.error_message = f"ERRO: COMPULAB: Tipo de arquivo inválido. Aceitos: PDF, CSV, Excel, XSL"

                if tmp_file_path and os.path.exists(tmp_file_path):
                    os.unlink(tmp_file_path)
                return
            
            # Salvar informações (não os bytes!)
            self.compulab_file_name = file.name
            self.compulab_file_path = tmp_file_path
            self.compulab_file_size_bytes = total_size
            self.compulab_file_bytes = b""  # Não armazenar bytes para arquivos grandes
            
            # --- Upload para Cloudinary ---
            self.processing_status = "☁️ Enviando para nuvem (Cloudinary)..."
            await asyncio.sleep(0.01)
            
            # Executar upload em thread separada
            loop = asyncio.get_event_loop()
            file_url = await loop.run_in_executor(
                None, 
                lambda: cloudinary_service.upload_file(tmp_file_path, resource_type="raw")
            )
            
            if file_url:
                self.compulab_file_url = file_url
                print(f"DEBUG: Upload Cloudinary sucesso: {file_url}")
            else:
                print("DEBUG: Erro upload Cloudinary (COMPULAB). Note: Arquivos > 10MB podem falhar no plano gratuito.")
                # Não falhar o processo todo se o Cloudinary falhar, mas avisar?
                # Por enquanto segue, pois temos o arquivo local APENAS SE ESTIVERMOS NA MESMA SESSÃO/CONTAINER
            
            # Mensagem com detalhes
            size_str = self.compulab_file_size
            file_type = "PDF" if file.name.lower().endswith('.pdf') else "CSV"
            cloud_status = " (Salvo na nuvem)" if self.compulab_file_url else " (Local)"
            self.success_message = f"SUCESSO: COMPULAB carregado: {file.name} ({file_type}, {size_str}){cloud_status}"
            self.processing_status = ""
            
        except Exception as e:
            self.error_message = f"ERRO: Erro ao carregar COMPULAB: {str(e)}"
            self.processing_status = ""
            if tmp_file_path and os.path.exists(tmp_file_path):
                try:
                    os.unlink(tmp_file_path)
                except:
                    pass
        finally:
            self.is_uploading = False
    
    async def handle_simus_upload(self, files: List[rx.UploadFile]):
        """Processa upload do arquivo SIMUS - Salva em disco para evitar travamento"""
        print(f"DEBUG: Iniciando upload SIMUS. Files: {len(files) if files else 0}")
        if not files:
            print("DEBUG: Nenhum arquivo recebido")
            return
        
        self.is_uploading = True
        self.error_message = ""
        self.success_message = ""
        self.processing_status = "📤 Carregando arquivo SIMUS..."
        print("DEBUG: Status atualizado para carregando")
        
        # Limpar arquivo anterior se existir
        if self.simus_file_path and os.path.exists(self.simus_file_path):
            try:
                os.unlink(self.simus_file_path)
            except:
                pass
        
        tmp_file_path = None
        
        try:
            file = files[0]
            
            # Criar arquivo temporário
            file_ext = os.path.splitext(file.name)[1] or '.pdf'
            tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_ext)
            tmp_file_path = tmp_file.name
            tmp_file.close()
            
            self.processing_status = "💾 Salvando arquivo em disco..."
            await asyncio.sleep(0.01)  # Yield para UI
            
            # Salvar arquivo em disco em chunks (não carrega tudo na memória)
            chunk_size = 1024 * 1024  # 1MB por chunk
            total_size = 0
            
            with open(tmp_file_path, 'wb') as f:
                while True:
                    chunk = await file.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    total_size += len(chunk)
                    
                    # Yield periodicamente para não travar
                    if total_size % (5 * 1024 * 1024) == 0:  # A cada 5MB
                        await asyncio.sleep(0.01)
                        self.processing_status = f"💾 Salvando... {total_size / (1024*1024):.1f} MB"
            
            # Validar tamanho do arquivo
            if total_size == 0:
                self.error_message = "ERRO: SIMUS: Arquivo está vazio"
                if tmp_file_path and os.path.exists(tmp_file_path):
                    os.unlink(tmp_file_path)
                return
            
            max_size_bytes = self.MAX_FILE_SIZE_MB * 1024 * 1024
            if total_size > max_size_bytes:
                self.error_message = f"ERRO: SIMUS: Arquivo muito grande. Máximo: {self.MAX_FILE_SIZE_MB}MB"
                if tmp_file_path and os.path.exists(tmp_file_path):
                    os.unlink(tmp_file_path)
                return
            
            # Validar extensão
            valid_extensions = ['.pdf', '.csv', '.xlsx', '.xls', '.xsl']
            if not any(file.name.lower().endswith(ext) for ext in valid_extensions):
                self.error_message = f"ERRO: SIMUS: Tipo de arquivo inválido. Aceitos: PDF, CSV, Excel, XSL"

                if tmp_file_path and os.path.exists(tmp_file_path):
                    os.unlink(tmp_file_path)
                return
            
            # Salvar informações (não os bytes!)
            self.simus_file_name = file.name
            self.simus_file_path = tmp_file_path
            self.simus_file_size_bytes = total_size
            self.simus_file_bytes = b""  # Não armazenar bytes para arquivos grandes
            
            # --- Upload para Cloudinary ---
            self.processing_status = "☁️ Enviando para nuvem (Cloudinary)..."
            await asyncio.sleep(0.01)
            
            # Executar upload em thread separada
            loop = asyncio.get_event_loop()
            file_url = await loop.run_in_executor(
                None, 
                lambda: cloudinary_service.upload_file(tmp_file_path, resource_type="raw")
            )
            
            if file_url:
                self.simus_file_url = file_url
                print(f"DEBUG: Upload Cloudinary sucesso: {file_url}")
            else:
                print("DEBUG: Erro upload Cloudinary. Note: Arquivos > 10MB podem falhar no plano gratuito.")
                # O processo continua usando o arquivo local temporário
            
            # Mensagem com detalhes
            size_str = self.simus_file_size
            file_type = "PDF" if file.name.lower().endswith('.pdf') else "CSV"
            cloud_status = " (Salvo na nuvem)" if self.simus_file_url else " (Local)"
            self.success_message = f"SUCESSO: SIMUS carregado: {file.name} ({file_type}, {size_str}){cloud_status}"
            self.processing_status = ""
            
        except Exception as e:
            self.error_message = f"ERRO: Erro ao carregar SIMUS: {str(e)}"
            self.processing_status = ""
            if tmp_file_path and os.path.exists(tmp_file_path):
                try:
                    os.unlink(tmp_file_path)
                except:
                    pass
        finally:
            self.is_uploading = False
    
    def clear_compulab_file(self):
        """Remove o arquivo COMPULAB"""
        # Remover arquivo temporário do disco
        if self.compulab_file_path and os.path.exists(self.compulab_file_path):
            try:
                os.unlink(self.compulab_file_path)
            except:
                pass
        
        self.compulab_file_name = ""
        self.compulab_file_path = ""
        self.compulab_file_url = ""
        self.compulab_file_bytes = b""
        self.compulab_file_size_bytes = 0
        self.success_message = ""
        self.error_message = ""
        # Limpar CSVs gerados
        self.csv_generated = False
        self.compulab_csv = ""
    
    def clear_simus_file(self):
        """Remove o arquivo SIMUS"""
        # Remover arquivo temporário do disco
        if self.simus_file_path and os.path.exists(self.simus_file_path):
            try:
                os.unlink(self.simus_file_path)
            except:
                pass
        
        self.simus_file_name = ""
        self.simus_file_path = ""
        self.simus_file_url = ""
        self.simus_file_bytes = b""
        self.simus_file_size_bytes = 0
        self.success_message = ""
        self.error_message = ""
        # Limpar CSVs gerados
        self.csv_generated = False
        self.simus_csv = ""
    
    def clear_all_files(self):
        """Remove todos os arquivos"""
        self.clear_compulab_file()
        self.clear_simus_file()
        self.clear_analysis()
    
    async def generate_csvs(self):
        """Gera CSVs a partir dos PDFs"""
        if not self.has_files:
            self.error_message = "ERRO: Carregue ambos os arquivos primeiro"
            return
        
        self.is_generating_csv = True
        self.error_message = ""
        self.csv_progress_percentage = 0
        self.csv_stage = "Iniciando conversão..."
        yield
        
        try:
            from .utils.pdf_processor import generate_csvs_from_pdfs
            
            # Variável compartilhada para armazenar progresso (thread-safe)
            progress_state = {"percentage": 0, "stage": ""}
            
            # Callback para atualizar progresso
            def update_progress(percentage: int, stage: str):
                progress_state["percentage"] = percentage
                progress_state["stage"] = stage
            
            # Ler arquivos do disco se existirem, senão usar bytes (compatibilidade)
            compulab_bytes = b""
            simus_bytes = b""
            
            if self.compulab_file_path and os.path.exists(self.compulab_file_path):
                with open(self.compulab_file_path, 'rb') as f:
                    compulab_bytes = f.read()
            else:
                compulab_bytes = self.compulab_file_bytes
            
            if self.simus_file_path and os.path.exists(self.simus_file_path):
                with open(self.simus_file_path, 'rb') as f:
                    simus_bytes = f.read()
            else:
                simus_bytes = self.simus_file_bytes
            
            # Executar conversão em thread separada para não bloquear
            with ThreadPoolExecutor() as executor:
                future = executor.submit(
                    generate_csvs_from_pdfs,
                    compulab_bytes,
                    simus_bytes,
                    update_progress
                )
                
                # Monitorar progresso enquanto executa
                while not future.done():
                    # Atualizar estado do Reflex
                    self.csv_progress_percentage = progress_state["percentage"]
                    self.csv_stage = progress_state["stage"]
                    yield
                    await asyncio.sleep(0.2)  # Verificar progresso a cada 200ms
                
                compulab_csv, simus_csv, success = future.result()
                
                # Atualizar estado final
                self.csv_progress_percentage = progress_state["percentage"]
                self.csv_stage = progress_state["stage"]
                yield
            
            if success:
                self.compulab_csv = compulab_csv
                self.simus_csv = simus_csv
                self.csv_generated = True
                self.csv_progress_percentage = 100
                self.csv_stage = "Concluído"
                self.success_message = "SUCESSO: CSVs gerados com sucesso!"
                yield
            else:
                self.error_message = "ERRO: Erro ao gerar CSVs. Verifique os arquivos."
                yield
        except Exception as e:
            self.error_message = f"ERRO: Erro: {str(e)}"
            yield
        finally:
            self.is_generating_csv = False
    
    def _run_pdf_extraction_sync(self, compulab_path: str, simus_path: str, compulab_is_csv: bool = False, simus_is_csv: bool = False, progress_callback=None) -> dict:
        """
        Executa a extração de PDF, CSV ou Excel de forma síncrona
        """
        from .utils.pdf_processor import extract_compulab_patients, extract_simus_patients, load_from_csv, load_from_excel

        
        try:
            # Estágio 1: Processando COMPULAB (0-45%)
            if progress_callback:
                progress_callback(0, "Processando COMPULAB...")
                
            compulab_filename = compulab_path.lower()
            if compulab_filename.endswith(('.xlsx', '.xls', '.xsl')):
                if progress_callback:
                    progress_callback(5, "Lendo arquivo COMPULAB (Excel)...")
                compulab_patients, compulab_total = load_from_excel(compulab_path)
            elif compulab_is_csv:

                # Ler CSV (rápido, 0-15%)
                if progress_callback:
                    progress_callback(5, "Lendo arquivo COMPULAB (CSV)...")
                with open(compulab_path, 'r', encoding='utf-8-sig') as f:
                    csv_content = f.read()
                if progress_callback:
                    progress_callback(10, "Processando dados COMPULAB...")
                compulab_patients, compulab_total = load_from_csv(csv_content)
                if progress_callback:
                    progress_callback(45, "COMPULAB processado")
            else:
                # Processar PDF (15-45%)
                def compulab_progress(percentage):
                    if progress_callback:
                        progress = 15 + int(percentage * 0.3)
                        progress_callback(progress, f"Processando COMPULAB (PDF)... {percentage}%")
                
                compulab_patients, compulab_total = extract_compulab_patients(
                    compulab_path,
                    progress_callback=compulab_progress if progress_callback else None
                )
                if progress_callback:
                    progress_callback(45, "COMPULAB processado")
            
            if compulab_patients is None:
                return {"error": "Erro ao processar COMPULAB"}
            
            # Liberar memória
            gc.collect()
            
            # Estágio 2: Processando SIMUS (45-90%)
            if progress_callback:
                progress_callback(45, "Processando SIMUS...")
                
            simus_filename = simus_path.lower()
            if simus_filename.endswith(('.xlsx', '.xls', '.xsl')):
                if progress_callback:
                    progress_callback(50, "Lendo arquivo SIMUS (Excel)...")
                simus_patients, simus_total = load_from_excel(simus_path)
                sigtap_val, contrat_val = None, None
            elif simus_is_csv:

                # Ler CSV (rápido, 45-60%)
                if progress_callback:
                    progress_callback(50, "Lendo arquivo SIMUS (CSV)...")
                with open(simus_path, 'r', encoding='utf-8-sig') as f:
                    csv_content = f.read()
                if progress_callback:
                    progress_callback(55, "Processando dados SIMUS...")
                simus_patients, simus_total = load_from_csv(csv_content)
                sigtap_val = None
                contrat_val = None
                if progress_callback:
                    progress_callback(90, "SIMUS processado")
            else:
                # Processar PDF (45-90%)
                def simus_progress(page, total_pages):
                    if total_pages > 0 and progress_callback:
                        percentage = int((page / total_pages) * 100)
                        progress = 45 + int(percentage * 0.45)
                        progress_callback(progress, f"Processando SIMUS (PDF)... Página {page}/{total_pages}")
                
                simus_patients, simus_total, sigtap_val, contrat_val = extract_simus_patients(
                    simus_path,
                    known_patient_names=list(compulab_patients.keys()),
                    progress_callback=simus_progress if progress_callback else None
                )
                if progress_callback:
                    progress_callback(90, "SIMUS processado")
            
            if simus_patients is None:
                return {"error": "Erro ao processar SIMUS"}
            
            # Liberar memória
            gc.collect()
            
            return {
                "compulab_patients": dict(compulab_patients),
                "compulab_total": compulab_total,
                "simus_patients": dict(simus_patients),
                "simus_total": simus_total,
                "sigtap_val": sigtap_val,
                "contrat_val": contrat_val,
            }
            
        except Exception as e:
            return {"error": str(e)}
        finally:
            # Não deletar os arquivos aqui - eles são gerenciados pelo State
            # (ou são temporários criados no run_analysis que serão limpos lá)
            gc.collect()
    
    async def run_analysis(self):
        """
        Executa a análise comparativa
        Otimizado para arquivos grandes usando ThreadPoolExecutor
        """
        if not self.has_files:
            self.error_message = "ERRO: Carregue ambos os arquivos primeiro"
            return
        
        self.is_analyzing = True
        self.error_message = ""
        self.analysis_progress_percentage = 0
        self.analysis_stage = "Iniciando análise..."
        self.processing_progress = 0
        self.processing_total = 0
        # Limpar PDF anterior quando iniciar nova análise
        self.analysis_pdf = ""
        yield
        
        # Rastrear arquivos temporários criados para limpar depois
        created_temp_files = []
        
        try:
            from .utils.comparison import compare_patients, compute_difference_breakdown
            
            # Executar extração em thread separada para não bloquear a UI
            loop = asyncio.get_event_loop()
            
            # Variável compartilhada para armazenar progresso (thread-safe)
            progress_state = {"percentage": 0, "stage": ""}
            
            # Callback para atualizar progresso
            def update_progress(percentage: int, stage: str):
                progress_state["percentage"] = percentage
                progress_state["stage"] = stage
            
            # Detectar tipo de arquivo baseado no nome ou caminho
            compulab_is_csv = False
            if self.compulab_file_name:
                compulab_is_csv = self.compulab_file_name.lower().endswith('.csv')
            elif self.compulab_file_path:
                compulab_is_csv = self.compulab_file_path.lower().endswith('.csv')
            
            simus_is_csv = False
            if self.simus_file_name:
                simus_is_csv = self.simus_file_name.lower().endswith('.csv')
            elif self.simus_file_path:
                simus_is_csv = self.simus_file_path.lower().endswith('.csv')
                
            compulab_is_excel = False
            excel_exts = ('.xlsx', '.xls', '.xsl')
            if self.compulab_file_name:
                compulab_is_excel = self.compulab_file_name.lower().endswith(excel_exts)
            elif self.compulab_file_path:
                compulab_is_excel = self.compulab_file_path.lower().endswith(excel_exts)

            simus_is_excel = False
            if self.simus_file_name:
                simus_is_excel = self.simus_file_name.lower().endswith(excel_exts)
            elif self.simus_file_path:
                simus_is_excel = self.simus_file_path.lower().endswith(excel_exts)

            
            # Obter caminhos dos arquivos (do disco ou criar temporários dos bytes)
            compulab_path = self.compulab_file_path if (self.compulab_file_path and os.path.exists(self.compulab_file_path)) else None
            simus_path = self.simus_file_path if (self.simus_file_path and os.path.exists(self.simus_file_path)) else None
            
            # Rastrear se criamos arquivos temporários para limpar depois
            created_temp_files = []
            
            # Se não houver caminhos, criar arquivos temporários dos bytes (compatibilidade)
            if not compulab_path and len(self.compulab_file_bytes) > 0:
                suffix = '.csv' if compulab_is_csv else ('.xlsx' if compulab_is_excel else '.pdf')
                mode = 'wb' if not compulab_is_csv else 'w'
                encoding = 'utf-8-sig' if compulab_is_csv else None

                with tempfile.NamedTemporaryFile(mode=mode, delete=False, suffix=suffix, encoding=encoding) as tmp_file:
                    if compulab_is_csv:
                        # Para CSV, decodificar bytes para string
                        csv_content = self.compulab_file_bytes.decode('utf-8-sig') if isinstance(self.compulab_file_bytes, bytes) else self.compulab_file_bytes
                        tmp_file.write(csv_content)
                    else:
                        tmp_file.write(self.compulab_file_bytes)
                    compulab_path = tmp_file.name
                created_temp_files.append(compulab_path)
            
            if not simus_path and len(self.simus_file_bytes) > 0:
                suffix = '.csv' if simus_is_csv else ('.xlsx' if simus_is_excel else '.pdf')
                mode = 'wb' if not simus_is_csv else 'w'
                encoding = 'utf-8-sig' if simus_is_csv else None

                with tempfile.NamedTemporaryFile(mode=mode, delete=False, suffix=suffix, encoding=encoding) as tmp_file:
                    if simus_is_csv:
                        # Para CSV, decodificar bytes para string
                        csv_content = self.simus_file_bytes.decode('utf-8-sig') if isinstance(self.simus_file_bytes, bytes) else self.simus_file_bytes
                        tmp_file.write(csv_content)
                    else:
                        tmp_file.write(self.simus_file_bytes)
                    simus_path = tmp_file.name
                created_temp_files.append(simus_path)
            
            if not compulab_path or not simus_path:
                self.error_message = "ERRO: Arquivos não encontrados"
                # Limpar arquivos temporários criados
                for temp_path in created_temp_files:
                    try:
                        if os.path.exists(temp_path):
                            os.unlink(temp_path)
                    except:
                        pass
                return
            
            # Usar ThreadPoolExecutor para processamento pesado
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(
                    self._run_pdf_extraction_sync,
                    compulab_path,
                    simus_path,
                    compulab_is_csv,
                    simus_is_csv,
                    update_progress
                )
                
                # Monitorar progresso enquanto executa
                while not future.done():
                    # Atualizar estado do Reflex
                    self.analysis_progress_percentage = progress_state["percentage"]
                    self.analysis_stage = progress_state["stage"]
                    yield
                    await asyncio.sleep(0.2)  # Verificar progresso a cada 200ms
                
                result = future.result()
                
                # Atualizar estado final da extração
                self.analysis_progress_percentage = progress_state["percentage"]
                self.analysis_stage = progress_state["stage"]
                yield
            
            # Verificar erros
            if "error" in result:
                self.error_message = f"ERRO: {result['error']}"
                yield
                return
            
            # Estágio 3: Comparando dados (90-100%)
            self.analysis_progress_percentage = 90
            self.analysis_stage = "Comparando dados..."
            yield
            
            # Armazenar dados
            compulab_patients = result["compulab_patients"]
            simus_patients = result["simus_patients"]
            compulab_total = result["compulab_total"]
            simus_total = result["simus_total"]
            sigtap_val = result["sigtap_val"]
            contrat_val = result["contrat_val"]
            
            self._compulab_patients = compulab_patients
            self._simus_patients = simus_patients
            
            # Atualizar totais
            self.compulab_total = float(compulab_total)
            self.simus_total = float(simus_total)
            self.compulab_count = len(compulab_patients)
            self.simus_count = len(simus_patients)
            self.sigtap_val = float(sigtap_val) if sigtap_val else 0.0
            self.contratualizado_val = float(contrat_val) if contrat_val else 0.0
            
            # Comparar (90-95%)
            self.analysis_progress_percentage = 92
            self.analysis_stage = "Identificando diferenças..."
            yield
            
            comparison_results = compare_patients(compulab_patients, simus_patients)
            
            # Breakdown (95-98%)
            self.analysis_progress_percentage = 95
            self.analysis_stage = "Calculando breakdown..."
            yield
            
            # Converter para listas serializáveis
            self.missing_patients = [
                PatientModel(
                    name=item['patient'],
                    total_exams=item['exams_count'],
                    total_value=float(item['total_value'])
                )
                for item in comparison_results['missing_patients']
            ]
            
            self.missing_exams = [
                AnalysisResult(
                    patient=item['patient'],
                    exam_name=item['exam_name'],
                    value=float(item['value'])
                )
                for item in comparison_results['missing_exams']
            ]
            
            self.value_divergences = [
                AnalysisResult(
                    patient=item['patient'],
                    exam_name=item['exam_name'],
                    compulab_value=float(item['compulab_value']),
                    simus_value=float(item['simus_value']),
                    difference=float(item['difference']),
                    compulab_count=item.get('compulab_count', 1),
                    simus_count=item.get('simus_count', 1)
                )
                for item in comparison_results['value_divergences']
            ]

            self.extra_simus_exams = [
                AnalysisResult(
                    patient=item['patient'],
                    exam_name=item['exam_name'],
                    value=float(item['value'])
                )
                for item in comparison_results['extra_simus_exams']
            ]
            
            # Breakdown
            breakdown = compute_difference_breakdown(
                Decimal(str(compulab_total)),
                Decimal(str(simus_total)),
                comparison_results
            )
            
            self.missing_patients_total = float(breakdown['missing_patients_total'])
            
            # Finalizando (98-100%)
            self.analysis_progress_percentage = 98
            self.analysis_stage = "Finalizando análise..."
            yield
            self.missing_exams_total = float(breakdown['missing_exams_total'])
            self.divergences_total = float(breakdown['divergences_total'])
            self.explained_total = float(breakdown['explained_total'])
            self.residual = float(breakdown['residual'])
            
            # Concluído (100%)
            self.analysis_progress_percentage = 100
            self.analysis_stage = "Concluído"
            self.success_message = "SUCESSO: Análise concluída com sucesso!"
            self.processing_status = ""
            yield
            
            # Limpar arquivos temporários criados (se houver)
            for temp_path in created_temp_files:
                try:
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)
                except:
                    pass
                
            # Salvar Resumo de Auditoria no Supabase (QA Improvement)
            if not self.error_message:
                summary_data = {
                    "compulab_total": self.compulab_total,
                    "simus_total": self.simus_total,
                    "missing_exams_count": len(self.missing_exams),
                    "divergences_count": len(self.value_divergences),
                    "missing_patients_count": len(self.missing_patients)
                }
                await AuditService.save_audit_summary(summary_data)
                self.last_audit_summary = summary_data
                
                # Carregar resoluções existentes do banco
                await self.load_resolutions()

        except Exception as e:
            self.error_message = f"ERRO: Erro na análise: {str(e)}"
            self.analysis_stage = f"Erro: {str(e)}"
            yield
            # Limpar arquivos temporários em caso de erro também
            for temp_path in created_temp_files:
                try:
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)
                except:
                    pass
        finally:
            self.is_analyzing = False
            self.processing_progress = 0
            self.processing_total = 0
            self.processing_status = ""
            if not self.error_message:
                # Manter 100% se sucesso, senão resetar
                pass
            else:
                self.analysis_progress_percentage = 0
                self.analysis_stage = ""
            gc.collect()
    
    async def generate_ai_analysis(self):
        """Gera análise por IA (Async + Parallel)"""
        # Selecionar chave e provedor
        if self.ai_provider == "Gemini":
            api_key = Config.GEMINI_API_KEY
        else:
            api_key = Config.OPENAI_API_KEY
        
        if not api_key:
            self.error_message = f"ERRO: API Key para {self.ai_provider} não configurada no ambiente (.env)"
            return
        
        if not self.has_analysis:
            self.error_message = "ERRO: Execute a análise primeiro"
            return
        
        self.is_generating_ai = True
        self.ai_loading_progress = 0
        self.ai_loading_text = "Iniciando..."
        self.error_message = ""
        
        try:
            from .utils.ai_analysis import generate_ai_analysis
            
            # Auditoria Híbrida: Filtrar apenas pacientes com problemas detectados
            # Isso economiza 80-90% de tokens e foca a IA no que realmente importa.
            problem_patients = set()
            
            # --- Robustness Check: Ensure lists are populated if totals are > 0 ---
            total_leakage = self.total_revenue_leakage
            has_lists_data = (len(self.missing_patients) > 0 or 
                              len(self.missing_exams) > 0 or 
                              len(self.value_divergences) > 0 or
                              len(self.extra_simus_exams) > 0)
            
            if total_leakage > 0 and not has_lists_data:
                print("DEBUG: State inconsistency detected in generate_ai_analysis (Totals > 0 but lists empty). Regenerating...")
                try:
                    from .utils.comparison import compare_patients
                    comparison_results = compare_patients(self._compulab_patients, self._simus_patients)
                    
                    # Re-populate lists temporarily ensuring they are AnalysisResult/PatientModel
                    # Note: We are not determining breakdown totals again, just the lists for AI context
                    for item in comparison_results['missing_patients']:
                         problem_patients.add(item['patient'])
                    for item in comparison_results['missing_exams']:
                         problem_patients.add(item['patient'])
                    for item in comparison_results['value_divergences']:
                         problem_patients.add(item['patient'])
                    for item in comparison_results['extra_simus_exams']:
                         problem_patients.add(item['patient'])
                except Exception as e:
                     print(f"DEBUG: Failed to regenerate lists: {e}")
            else:
                for p in self.missing_patients: problem_patients.add(p.name)
                for item in self.missing_exams: problem_patients.add(item.patient)
                for item in self.value_divergences: problem_patients.add(item.patient)
                for item in self.extra_simus_exams: problem_patients.add(item.patient)
            
            filtered_compulab = {k: v for k, v in self._compulab_patients.items() if k in problem_patients}
            filtered_simus = {k: v for k, v in self._simus_patients.items() if k in problem_patients}
            
            # Double check: If filtering resulted in empty dicts but we have problem patients,
            # it means keys didn't match. Try fallback with relaxed matching.
            if not filtered_compulab and problem_patients:
                 print("DEBUG: Exact key match failed for AI context. Attempting normalized match.")
                 # Create normalized map of _compulab_patients
                 from .utils.comparison import normalize_patient_name
                 norm_map = {normalize_patient_name(k): v for k, v in self._compulab_patients.items()}
                 
                 for p_name in problem_patients:
                     norm_p = normalize_patient_name(p_name)
                     if norm_p in norm_map:
                         filtered_compulab[p_name] = norm_map[norm_p]
            
            if not problem_patients:
                # Only show 'No Discrepancy' if totals are also zero or negligible
                if self.total_revenue_leakage > 1.0:
                     # Fallback: Send everything if local detection failed but we have leak
                     print("DEBUG: Fallback to full analysis due to empty problem_patients but high leakage.")
                     filtered_compulab = self._compulab_patients
                     filtered_simus = self._simus_patients
                     all_patients = list(filtered_compulab.keys())
                     # Limit to first 50 to avoid token overflow in fallback mode
                     if len(all_patients) > 50:
                         filtered_compulab = {k: filtered_compulab[k] for k in all_patients[:50]}
                         filtered_simus = {k: filtered_simus[k] for k in all_patients[:50] if k in filtered_simus}
                else:
                    self.ai_analysis = "# RELATÓRIO DE AUDITORIA\n\nNenhuma divergência foi encontrada na análise determinística. A auditoria de IA não é necessária."
                    self.is_generating_ai = False
                    self.success_message = "Análise concluída: Sem divergências detectadas."
                    return

            # Consumir o gerador async com throttling de UI
            final_analysis = None
            final_error = None
            last_progress_update = 0
            
            async for progress_update in generate_ai_analysis(
                filtered_compulab,
                filtered_simus,
                api_key,
                provider=self.ai_provider,
                model_name=self.ai_model
            ):
                # O gerador retorna tuplas (progresso, status) OU (resultado, erro) no final
                if isinstance(progress_update, tuple):
                    val1, val2 = progress_update
                    
                    if isinstance(val1, int): # (percentage, message)
                        # Só atualiza a UI se mudou o texto ou a cada 5% para evitar socket flood
                        if val1 != self.ai_loading_progress and (val1 % 5 == 0 or val1 == 100 or val2 != self.ai_loading_text):
                            self.ai_loading_progress = val1
                            self.ai_loading_text = val2
                            yield
                    else: # (analysis, error) - Resultado final
                        final_analysis = val1
                        final_error = val2
            
            if final_error:
                self.error_message = f"ERRO: {final_error}"
                self.success_message = ""
            else:
                self.ai_analysis = final_analysis
                self.success_message = f"SUCESSO: Auditoria IA concluída com {self.ai_provider} ({self.ai_model})!"
                
                # Parsear para tabela na UI (Plain CSV Format - sem code blocks)
                try:
                    import csv
                    from io import StringIO
                    
                    # Encontrar seção de divergências (linhas com ;)
                    lines = final_analysis.split('\n')
                    csv_lines = []
                    for line in lines:
                        line = line.strip()
                        if ';' in line and not line.startswith('#') and not line.startswith('*'):
                            csv_lines.append(line)
                    
                    if csv_lines:
                        # Detectar se tem header
                        first_line = csv_lines[0]
                        if 'Paciente' in first_line and 'Nome_Exame' in first_line:
                            csv_content = '\n'.join(csv_lines)
                        else:
                            # Adicionar header manualmente - deve bater com o prompt do utils/ai_analysis.py
                            header = "Paciente;Nome_Exame;Codigo_Exame;Valor_Compulab;Valor_Simus;Tipo_Divergencia;Sugestao_Causa_Raiz"
                            csv_content = header + '\n' + '\n'.join(csv_lines)
                        
                        f = StringIO(csv_content)
                        reader = csv.DictReader(f, delimiter=';')
                        self.ai_analysis_data = list(reader)
                        
                        # Gerar data URI para download CSV
                        import base64
                        csv_bytes = csv_content.encode('utf-8-sig')
                        csv_base64 = base64.b64encode(csv_bytes).decode('utf-8')
                        self.ai_analysis_csv = f"data:text/csv;charset=utf-8-sig;base64,{csv_base64}"
                        
                except Exception as e:
                    print(f"Erro ao parsear CSV para UI: {e}")
                
        except Exception as e:
            self.error_message = f"ERRO: Erro: {str(e)}"
        finally:
            self.is_generating_ai = False
            self.ai_loading_progress = 0
            self.ai_loading_text = ""
    
    def generate_pdf_report(self):
        """Gera PDF da análise e armazena no state"""
        if not self.has_analysis:
            self.error_message = "ERRO: Execute a análise primeiro"
            self.success_message = ""
            return
        
        self.error_message = ""
        self.success_message = "⏳ Gerando PDF..."
        
        try:
            # Verificar se reportlab está instalado
            try:
                import reportlab
            except ImportError:
                self.error_message = "ERRO: Biblioteca reportlab não está instalada. Execute: pip install reportlab"
                self.success_message = ""
                return
            
            from .utils.pdf_report import generate_analysis_pdf
            import base64
            import traceback
            
            # Gerar PDF
            pdf_bytes = generate_analysis_pdf(
                compulab_total=self.compulab_total,
                simus_total=self.simus_total,
                compulab_count=self.compulab_count,
                simus_count=self.simus_count,
                missing_patients=self.missing_patients,
                missing_exams=self.missing_exams,
                value_divergences=self.value_divergences,
                missing_patients_total=self.missing_patients_total,
                missing_exams_total=self.missing_exams_total,
                divergences_total=self.divergences_total,
                explained_total=self.explained_total,
                residual=self.residual,
                ai_analysis=self.ai_analysis if self.ai_analysis else ""
            )
            
            if not pdf_bytes or len(pdf_bytes) == 0:
                self.error_message = "ERRO: Erro: PDF gerado está vazio"
                self.success_message = ""
                return
            
            # Converter para base64
            pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
            
            # Armazenar data URI para download
            self.analysis_pdf = f"data:application/pdf;base64,{pdf_base64}"
            self.success_message = "SUCESSO: PDF gerado com sucesso! Clique em 'Download PDF' para baixar."
            
        except ImportError as e:
            self.error_message = f"ERRO: Erro ao importar bibliotecas: {str(e)}. Execute: pip install reportlab"
            self.success_message = ""
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            self.error_message = f"ERRO: Erro ao gerar PDF: {str(e)}"
            self.success_message = ""
            # Log do erro completo para debug (pode ser removido em produção)
            print(f"Erro completo ao gerar PDF:\n{error_details}")
    
    def clear_analysis(self):
        """Limpa os resultados da análise"""
        self.compulab_total = 0.0
        self.simus_total = 0.0
        self.compulab_count = 0
        self.simus_count = 0
        self.missing_patients = []
        self.missing_exams = []
        self.value_divergences = []
        self.missing_patients_total = 0.0
        self.missing_exams_total = 0.0
        self.divergences_total = 0.0
        self.explained_total = 0.0
        self.residual = 0.0
        self.ai_analysis = ""
        self.analysis_pdf = ""
        self._compulab_patients = {}
        self._simus_patients = {}
        self.resolutions = {}
        self.is_showing_patient_history = False

    async def load_resolutions(self):
        """Carrega resoluções do banco para o estado"""
        if not supabase: return
        res_data = await AuditService.get_resolutions()
        # Converter dict com chaves tuple para string key compatível com Reflex
        self.resolutions = { f"{k[0]}|{k[1]}": v for k, v in res_data.items() }

    async def toggle_resolution(self, patient: str, exam: str):
        """Alterna o status de uma divergência entre 'pendente' e 'resolvido'"""
        key = f"{patient}|{exam}"
        current_status = self.resolutions.get(key, "pendente")
        new_status = "resolvido" if current_status == "pendente" else "pendente"
        
        # Otimismo na UI
        self.resolutions[key] = new_status
        
        # Persistir
        await AuditService.save_divergence_resolution({
            "patient_name": patient,
            "exam_name": exam,
            "status": new_status,
            "last_value": 0.0 # Opcional
        })

    async def view_patient_history(self, patient: str):
        """Busca e exibe o histórico de um paciente"""
        self.selected_patient_name = patient
        self.is_showing_patient_history = True
        history_raw = await AuditService.get_patient_history(patient)
        self.patient_history_data = [
            PatientHistoryEntry(
                id=str(r.get("id", "")),
                patient_name=r.get("patient_name", ""),
                exam_name=r.get("exam_name", ""),
                status=r.get("status", ""),
                last_value=float(r.get("last_value", 0.0)) if r.get("last_value") else 0.0,
                notes=r.get("notes", ""),
                created_at=str(r.get("created_at", ""))
            ) for r in history_raw
        ]

    def close_patient_history(self):
        """Fecha o modal de histórico"""
        self.is_showing_patient_history = False
        self.patient_history_data = []
        self.patient_history_search = ""

    @rx.var
    def filtered_patient_history(self) -> List[PatientHistoryEntry]:
        """Retorna o histórico filtrado pela busca"""
        if not self.patient_history_search:
            return self.patient_history_data
        search = self.patient_history_search.lower().strip()
        return [
            entry for entry in self.patient_history_data
            if search in entry.exam_name.lower() or search in (entry.notes or "").lower()
        ]

    @rx.var
    def patient_history_total_items(self) -> int:
        """Total de itens no histórico"""
        return len(self.patient_history_data)

    @rx.var
    def patient_history_resolved_items(self) -> int:
        """Total de itens resolvidos"""
        return len([e for e in self.patient_history_data if e.status == "resolvido"])

    @rx.var
    def patient_history_total_value(self) -> float:
        """Valor total auditado"""
        return sum(e.last_value for e in self.patient_history_data)

    @rx.var
    def patient_history_resolved_value(self) -> float:
        """Valor total recuperado"""
        return sum(e.last_value for e in self.patient_history_data if e.status == "resolvido")

    @rx.var
    def patient_history_success_rate(self) -> str:
        """Taxa de sucesso formatada"""
        total = len(self.patient_history_data)
        if total == 0:
            return "0%"
        resolved = len([e for e in self.patient_history_data if e.status == "resolvido"])
        return f"{(resolved / total) * 100:.1f}%"

    @rx.var
    def patient_history_total_value_formatted(self) -> str:
        """Valor total auditado formatado"""
        return f"R$ {self.patient_history_total_value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    @rx.var
    def patient_history_resolved_value_formatted(self) -> str:
        """Valor total recuperado formatado"""
        return f"R$ {self.patient_history_resolved_value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    async def update_patient_history_note(self, entry_id: str, new_note: str):
        """Atualiza a nota de um registro de histórico"""
        for entry in self.patient_history_data:
            if entry.id == entry_id:
                entry.notes = new_note
                # Persistir
                await AuditService.save_divergence_resolution({
                    "patient_name": entry.patient_name,
                    "exam_name": entry.exam_name,
                    "status": entry.status,
                    "notes": new_note,
                    "last_value": entry.last_value
                })
                break
        return rx.toast("Nota atualizada com sucesso!", status="success")

    async def download_patient_history_pdf(self):
        """Gera e baixa o PDF do histórico do paciente"""
        if not self.selected_patient_name or not self.patient_history_data:
            return
        
        try:
            from .utils.patient_pdf_report import generate_patient_history_pdf
            pdf_bytes = generate_patient_history_pdf(self.selected_patient_name, self.patient_history_data)
            
            b64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
            yield rx.download(
                data=f"data:application/pdf;base64,{b64_pdf}",
                filename=f"Historico_{self.selected_patient_name.replace(' ', '_')}.pdf"
            )
        except Exception as e:
            print(f"Erro ao gerar PDF do histórico: {e}")
            yield rx.toast(f"Erro ao gerar PDF: {str(e)}", status="error")

    def calculate_forecast(self):
        """Calcula previsão de faturamento baseada nos últimos meses"""
        if not self.audit_history:
            self.revenue_forecast = 0.0
            return
            
        # Pegar totais do compulab (faturamento real detectado)
        totals = [h.get("compulab_total", 0.0) for h in self.audit_history if h.get("compulab_total")]
        
        if len(totals) < 2:
            self.revenue_forecast = totals[0] if totals else 0.0
            return
            
        # Média simples das variações ou média móvel?
        # Vamos usar média móvel ponderada (meses mais recentes valem mais)
        weights = list(range(1, len(totals) + 1))
        # Reverter para que o mais recente tenha maior peso
        weights.reverse()
        
        weighted_sum = sum(t * w for t, w in zip(totals, weights))
        self.revenue_forecast = weighted_sum / sum(weights)
    
    # ===== ProIn - Métodos para Análise de Planilhas Excel =====
    
    async def handle_import_upload(self, files: List[rx.UploadFile]):
        """Processa upload do arquivo (Excel ou PDF)"""
        if not files:
            return
        
        file = files[0]
        self.excel_file_name = file.name
        self.excel_file_bytes = await file.read()
        
        ext = file.name.lower().split('.')[-1]
        if ext in ['xlsx', 'xls', 'pdf']:
             self.excel_success_message = f"Arquivo carregado: {file.name}"
             self.excel_error_message = ""
        else:
             self.excel_error_message = "Formato não suportado. Use .xlsx, .xls ou .pdf"
             
        self.excel_analyzed = False
    
    async def analyze_import_file(self):

        """Analisa o arquivo carregado (Excel ou PDF) e normaliza os dados"""
        if not self.has_excel_file:
            self.excel_error_message = "Carregue um arquivo primeiro"
            return
            
        self.is_analyzing_excel = True
        self.excel_analyzed = False
        self.excel_error_message = ""
        self.excel_success_message = "Processando arquivo... Aguarde."
        self.qc_import_progress = 0
        yield
        

        
        try:
            filename = self.excel_file_name.lower()
            normalized_data = [] # List of dicts: date, exam_name, value, target, sd, cv, etc.
            
            if filename.endswith(".xlsx") or filename.endswith(".xls") or filename.endswith(".xsl"):
                # --- Análise Excel (Multi-Sheet) ---
                import pandas as pd
                import io
                
                excel_io = io.BytesIO(self.excel_file_bytes)
                all_sheets = pd.read_excel(excel_io, header=None, sheet_name=None)
                
                for sheet_name, df_raw in all_sheets.items():
                    try:
                        if len(df_raw) > 1:
                            # Tentar encontrar a linha de cabeçalho
                            # Em algumas abas pode ser linha 0 ou 1
                            header_row_idx = 1
                            if len(df_raw) > 1 and str(df_raw.iloc[0, 0]).lower().startswith("exame"):
                                header_row_idx = 0
                            elif len(df_raw) > 1 and str(df_raw.iloc[1, 0]).lower().startswith("exame"):
                                header_row_idx = 1
                            else:
                                # Tentar achar "Exame"
                                found = False
                                for r in range(min(5, len(df_raw))):
                                    for c in range(min(5, len(df_raw.columns))):
                                        if str(df_raw.iloc[r, c]).strip().lower().startswith("exame"):
                                            header_row_idx = r
                                            found = True
                                            break
                                    if found: break
                                if not found: header_row_idx = 1

                            header_row = df_raw.iloc[header_row_idx]
                            
                            for idx in range(len(header_row)):
                                val = header_row.iloc[idx]
                                if str(val).strip().lower().startswith("exame"):
                                    # Data está na linha acima ou na mesma coluna se header_row_idx > 0
                                    date_str = datetime.now().strftime("%Y-%m-%d")
                                    if header_row_idx > 0:
                                        date_val = df_raw.iloc[header_row_idx-1, idx]
                                        try:
                                            import re
                                            match = re.search(r'(\d{1,2}/\d{1,2}/\d{2,4})', str(date_val))
                                            if match:
                                                d = match.group(1)
                                                day, month, year = d.split('/')
                                                if len(year) == 2: year = "20" + year
                                                date_str = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                                        except: pass

                                    # Extrair dados
                                    for row_idx in range(header_row_idx + 1, len(df_raw)):
                                        try:
                                            exam = df_raw.iloc[row_idx, idx]
                                            if pd.isna(exam) or str(exam).strip() == "": continue
                                            if idx + 3 >= len(df_raw.columns): break

                                            target = df_raw.iloc[row_idx, idx+1]
                                            value = df_raw.iloc[row_idx, idx+2]
                                            cv_val = df_raw.iloc[row_idx, idx+3]
                                            
                                            def clean_float(x):
                                                if isinstance(x, (int, float)): return float(x)
                                                if isinstance(x, str):
                                                    x = x.replace(',', '.').strip()
                                                    try: return float(x)
                                                    except: return 0.0
                                                return 0.0

                                            val_float = clean_float(value)
                                            target_float = clean_float(target)
                                            cv_float = clean_float(cv_val)
                                            
                                            if val_float != 0:
                                                normalized_data.append({
                                                    "date": date_str,
                                                    "exam_name": str(exam).strip(),
                                                    "value": val_float,
                                                    "target_value": target_float,
                                                    "target_sd": 0.0, 
                                                    "cv": cv_float,
                                                    "lot_number": "", 
                                                    "equipment": "", 
                                                    "analyst": f"Importado ({sheet_name})"
                                                })
                                        except: continue
                    except Exception as e:
                        print(f"Erro processando abas Excel: {e}")

            elif filename.endswith(".pdf"):
                # --- Análise PDF ---
                import pdfplumber
                import io
                with pdfplumber.open(io.BytesIO(self.excel_file_bytes)) as pdf:
                    for page in pdf.pages:
                        tables = page.extract_tables()
                        for table in tables:
                            if not table or len(table) < 3: continue
                            
                            header_cell = table[0][0] or ""
                            date_str = datetime.now().strftime("%Y-%m-%d")
                            
                            import re
                            match = re.search(r'(\d{1,2}/\d{1,2}/\d{2,4})', str(header_cell))
                            if match:
                                d = match.group(1)
                                try:
                                    day, month, year = d.split('/')
                                    if len(year) == 2: year = "20" + year
                                    date_str = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                                except: pass
                            
                            for row in table[2:]:
                                if len(row) < 3: continue
                                exam = row[0]
                                if not exam: continue
                                
                                def clean_pdf_float(x):
                                    if not x: return 0.0
                                    x = str(x).replace(',', '.').replace(" ", "")
                                    try: return float(x)
                                    except: return 0.0
                                
                                target = clean_pdf_float(row[1]) if len(row) > 1 else 0.0
                                value = clean_pdf_float(row[2]) if len(row) > 2 else 0.0
                                cv = clean_pdf_float(row[3]) if len(row) > 3 else 0.0
                                
                                if value != 0:
                                    normalized_data.append({
                                        "date": date_str,
                                        "exam_name": exam,
                                        "value": value,
                                        "target_value": target,
                                        "target_sd": 0.0,
                                        "cv": cv,
                                        "lot_number": "",
                                        "equipment": "",
                                        "analyst": "Importado (PDF)"
                                    })

            # Cria DataFrame normalizado
            if normalized_data:
                import pandas as pd
                df = pd.DataFrame(normalized_data)
                self._excel_dataframe = df
                
                self.excel_total_rows = len(df)
                self.excel_total_columns = len(df.columns)
                self.excel_filled_cells = int(df.count().sum())
                self.excel_headers = ["Data", "Exame", "Valor", "Alvo", "CV%"]
                
                preview_list = []
                for _, row in df.head(50).iterrows():
                    preview_list.append([
                        row["date"], 
                        row["exam_name"], 
                        str(row["value"]), 
                        str(row["target_value"]), 
                        f"{row['cv']}%"
                    ])
                self.excel_preview = preview_list
                self.excel_success_message = f"Análise concluída: {len(df)} registros encontrados!"
                self.excel_analyzed = True
            else:
                self.excel_error_message = "Nenhum dado válido encontrado no arquivo."
                self.excel_analyzed = False
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.excel_error_message = f"Erro na análise: {str(e)}"
            self.excel_analyzed = False
        finally:
            self.is_analyzing_excel = False


            # --- END OF NEW LOGIC ---
            # Dummy return to avoid executing old logic below if not indented properly
            return


    
    def download_excel_report(self):
        """Gera relatório da análise Excel"""
        if not self.excel_analyzed:
            self.excel_error_message = "Execute a análise primeiro"
            return
        
        # O download será tratado via JavaScript/link
        self.excel_success_message = "Relatório gerado!"
    
    def clear_excel_analysis(self):
        """Limpa a análise Excel"""
        self.excel_file_name = ""
        self.excel_file_bytes = b""
        self.excel_analyzed = False
        self.excel_total_rows = 0
        self.excel_total_columns = 0
        self.excel_filled_cells = 0
        self.excel_empty_cells = 0
        self.excel_headers = []
        self.excel_columns_info = []
        self.excel_numeric_summary = []
        self.excel_preview = []
        self._excel_dataframe = None
        self.excel_success_message = ""
        self.excel_error_message = ""

    qc_import_progress: int = 0
    is_importing: bool = False

    async def import_data_to_qc(self):
        """Importa os dados analisados para o sistema em lote"""
        if not self.excel_analyzed or self._excel_dataframe is None:
            self.excel_error_message = "Sem dados para importar. Analise um arquivo primeiro."
            return

        self.is_importing = True
        self.excel_success_message = "Iniciando importação..."
        self.excel_error_message = ""
        self.qc_import_progress = 0
        yield 

        try:
            df = self._excel_dataframe
            records = df.where(pd.notnull(df), None).to_dict('records')
            total_records = len(records)
            
            # Batch size config (Reduced to prevent freezing)
            BATCH_SIZE = 100
            
            batches = [records[i:i + BATCH_SIZE] for i in range(0, total_records, BATCH_SIZE)]
            imported_count = 0
            error_count = 0
            
            for i, batch in enumerate(batches):
                prepared_batch = []
                for record in batch:
                    try:
                        import_date = record.get("date")
                        if not import_date:
                            import_date = datetime.now().strftime("%Y-%m-%d")
                            
                        qc_data = {
                            "date": str(import_date),
                            "exam_name": str(record.get("exam_name", "")),
                            "level": str(record.get("level") if record.get("level") else "Importado"), 
                            "lot_number": str(record.get("lot_number") if record.get("lot_number") else "Importado"),
                            "value": float(record.get("value")) if record.get("value") is not None else 0.0,
                            "target_value": float(record.get("target_value")) if record.get("target_value") is not None else 0.0,
                            "target_sd": float(record.get("target_sd")) if record.get("target_sd") is not None else 0.0,
                            "equipment": str(record.get("equipment") if record.get("equipment") else "Importado"),
                            "analyst": str(record.get("analyst") if record.get("analyst") else "Sistema"),
                            "status": "OK"
                        }
                        
                        if not qc_data["exam_name"]:
                            continue
                            
                        prepared_batch.append(qc_data)
                    except:
                        continue
                
                if prepared_batch:
                    try:
                        await QCService.create_qc_records_batch(prepared_batch)
                        imported_count += len(prepared_batch)
                    except Exception as e:
                        print(f"Erro no lote {i}: {e}")
                        error_count += len(prepared_batch)
                
                # Update progress every batch
                self.qc_import_progress = int((imported_count / total_records) * 100)
                self.excel_success_message = f"Processando: {imported_count} de {total_records} registros..."
                
                # Give UI time to render
                yield
                await asyncio.sleep(0.02)
            
            self.qc_import_progress = 100
            self.excel_success_message = f"Sucesso! {imported_count} registros importados."
            

            
            # Refresh data
            await self.load_data_from_db(force=True)
            
        except Exception as e:
            self.excel_error_message = f"Erro fatal: {str(e)}"
        finally:
            self.is_importing = False
    
    # ===== ProIn QC - Métodos do Sistema de Controle de Qualidade =====
    
    def set_proin_tab(self, tab: str):
        """Muda a aba atual do ProIn QC"""
        self.proin_current_tab = tab
        self.qc_success_message = ""
        self.qc_error_message = ""
        self.reagent_success_message = ""
        self.reagent_error_message = ""
        self.maintenance_success_message = ""
        self.maintenance_error_message = ""
    
    @rx.var
    def qc_records_today(self) -> List[QCRecord]:
        """Registros de CQ do dia atual"""
        today = datetime.now().strftime("%Y-%m-%d")
        return [r for r in self.qc_records if r.date.startswith(today)]
    
    @rx.var
    def qc_records_with_alerts(self) -> List[QCRecord]:
        """Registros de CQ com CV > 5%"""
        return [r for r in self.qc_records if r.cv > 5.0]
    
    @rx.var
    def lots_expiring_soon(self) -> List[ReagentLot]:
        """Lotes que vencem nos próximos 30 dias"""
        from datetime import timedelta
        today = datetime.now()
        limit = today + timedelta(days=30)
        expiring = []
        for lot in self.reagent_lots:
            try:
                exp_date = datetime.strptime(lot.expiry_date, "%Y-%m-%d")
                if exp_date <= limit and exp_date >= today:
                    days_left = (exp_date - today).days
                    new_lot = ReagentLot(
                        id=lot.id,
                        name=lot.name,
                        lot_number=lot.lot_number,
                        expiry_date=lot.expiry_date,
                        quantity=lot.quantity,
                        manufacturer=lot.manufacturer,
                        storage_temp=lot.storage_temp,
                        created_at=lot.created_at,
                        days_left=days_left
                    )
                    expiring.append(new_lot)
            except:
                pass
        return sorted(expiring, key=lambda x: x.days_left)
    
    @rx.var
    def dashboard_total_today(self) -> int:
        """Total de registros de hoje"""
        today = datetime.now().strftime("%Y-%m-%d")
        return len([r for r in self.qc_records if r.date.startswith(today)])
    
    @rx.var
    def dashboard_total_month(self) -> int:
        """Total de registros do mês"""
        month = datetime.now().strftime("%Y-%m")
        return len([r for r in self.qc_records if r.date.startswith(month)])
    
    @rx.var
    def dashboard_approval_rate(self) -> float:
        """Taxa de aprovação (CV <= 5%)"""
        month = datetime.now().strftime("%Y-%m")
        records_month = [r for r in self.qc_records if r.date.startswith(month)]
        approved = len([r for r in records_month if r.cv <= 5.0])
        total = len(records_month)
        return round((approved / total * 100) if total > 0 else 100.0, 1)
    
    @rx.var
    def dashboard_pending_maintenances(self) -> int:
        """Manutenções pendentes"""
        today_dt = datetime.now()
        pending = 0
        for m in self.maintenance_records:
            try:
                next_date = datetime.strptime(m.next_date, "%Y-%m-%d")
                if next_date <= today_dt:
                    pending += 1
            except:
                pass
        return pending
    
    @rx.var
    def dashboard_expiring_lots(self) -> int:
        """Lotes vencendo"""
        return len(self.lots_expiring_soon)
    
    @rx.var
    def dashboard_alerts_count(self) -> int:
        """Quantidade de alertas de CV > 5%"""
        return len(self.qc_records_with_alerts)
    
    @rx.var
    def has_alerts(self) -> bool:
        """Verifica se há alertas de CQ"""
        return len(self.qc_records_with_alerts) > 0
    
    @rx.var
    def has_pending_maintenances(self) -> bool:
        """Verifica se há manutenções pendentes"""
        today_dt = datetime.now()
        for m in self.maintenance_records:
            try:
                next_date = datetime.strptime(m.next_date, "%Y-%m-%d")
                if next_date <= today_dt:
                    return True
            except:
                pass
        return False
    
    @rx.var
    def has_expiring_lots(self) -> bool:
        """Verifica se há lotes vencendo"""
        return len(self.lots_expiring_soon) > 0
    
    def calculate_cv(self, value1: float, value2: float) -> tuple:
        """Calcula CV% a partir de duas medições"""
        if value1 == 0 and value2 == 0:
            return 0.0, 0.0, 0.0
        mean = (value1 + value2) / 2
        variance = ((value1 - mean) ** 2 + (value2 - mean) ** 2) / 2
        sd = variance ** 0.5
        cv = (sd / mean * 100) if mean > 0 else 0.0
        return round(mean, 2), round(sd, 4), round(cv, 2)
    
    def set_qc_exam_name(self, value: str):
        self.qc_exam_name = value
    
    def set_qc_level(self, value: str):
        self.qc_level = value
    
    def set_qc_lot_number(self, value: str):
        self.qc_lot_number = value
    
    def set_qc_value1(self, value: str):
        self.qc_value1 = value
    
    def set_qc_value2(self, value: str):
        self.qc_value2 = value
    
    def set_qc_value(self, value: str):
        """Setter for single measurement value"""
        self.qc_value = value
    
    def set_qc_target_value(self, value: str):
        self.qc_target_value = value
    
    def set_qc_target_sd(self, value: str):
        self.qc_target_sd = value
    
    def set_qc_equipment(self, value: str):
        self.qc_equipment = value
    
    def set_qc_analyst(self, value: str):
        self.qc_analyst = value
    
    def set_qc_date(self, value: str):
        self.qc_date = value
    
    def clear_qc_form(self):
        """Limpa todos os campos do formulário de CQ"""
        self.qc_exam_name = ""
        self.qc_level = ""
        self.qc_lot_number = ""
        self.qc_value = ""
        self.qc_value1 = ""
        self.qc_value2 = ""
        self.qc_target_value = ""
        self.qc_target_sd = ""
        self.qc_equipment = ""
        self.qc_analyst = ""
        self.qc_date = ""
        self.qc_success_message = ""
        self.qc_error_message = ""
    
    async def save_qc_record(self):
        """Salva um novo registro de CQ"""
        self.is_saving_qc = True
        self.qc_error_message = ""
        self.qc_success_message = ""
        
        try:
            # Validações
            if not self.qc_exam_name:
                self.qc_error_message = "Informe o nome do exame"
                return
            if not self.qc_value:
                self.qc_error_message = "Informe o valor da medição"
                return
            if not self.qc_target_value or not self.qc_target_sd:
                self.qc_error_message = "Informe o valor alvo e o desvio padrão"
                return
            if not self.qc_date:
                self.qc_error_message = "Informe a data/hora"
                return
            
            try:
                value = float(self.qc_value.replace(",", "."))
                target = float(self.qc_target_value.replace(",", "."))
                sd = float(self.qc_target_sd.replace(",", "."))
                
                # Validação de valores improváveis ou negativos (QA Improvement)
                if value < 0 or target < 0 or sd < 0:
                    self.qc_error_message = "Valores não podem ser negativos"
                    return
                if target == 0 and value > 0:
                    self.qc_error_message = "Alvo não pode ser zero para uma medição ativa"
                    return
            except:
                self.qc_error_message = "Valores inválidos. Use apenas números e ponto/vírgula."
                return
            
            # Calcular Variação% = ((Valor - Alvo) / Alvo) * 100
            cv = ((value - target) / target) * 100 if target > 0 else 0.0
            
            # --- Lógica de Westgard (Novo) ---
            # Buscar histórico para o mesmo exame e nível
            history_values = [r.value for r in self.qc_records if r.exam_name == self.qc_exam_name and r.level == self.qc_level]
            # Adicionar o valor atual
            history_values.append(value)
            
            # Avaliar regras
            wg_result = WestgardRules.evaluate(history_values, target, sd)
            violations = wg_result["violations"]
            z_score = wg_result["z_score"]
            
            # Status baseado no Westgard (Sobrescreve o simplificado)
            if wg_result["status"] == "rejection":
                status = "REJEITADO (Westgard)"
            elif wg_result["status"] == "warning":
                status = "ALERTA (Westgard)"
            else:
                status = "OK"
            
            # Persistir no banco se disponível
            # Persistir no banco se disponível
            saved_to_db = False
            real_id = str(len(self.qc_records) + 1)
            
            if supabase:
                try:
                    db_data = {
                        "date": self.qc_date,
                        "exam_name": self.qc_exam_name,
                        "level": self.qc_level,
                        "lot_number": self.qc_lot_number,
                        "value": value,
                        "target_value": target,
                        "target_sd": sd,
                        "equipment": self.qc_equipment,
                        "analyst": self.qc_analyst,
                    }
                    await QCService.create_qc_record(db_data)
                    await self.load_data_from_db(force=True)
                    saved_to_db = True
                except Exception as db_error:
                    print(f"Erro ao salvar no Supabase: {db_error}")
            
            if not saved_to_db:
                # Criar registro (Fallback Local)
                record = QCRecord(
                    id=real_id,
                    date=self.qc_date,
                    exam_name=self.qc_exam_name,
                    level=self.qc_level,
                    lot_number=self.qc_lot_number,
                    value=value,
                    value1=value,  # Compatibilidade
                    value2=0.0,
                    mean=value,
                    sd=sd,
                    cv=round(cv, 2),
                    target_value=target,
                    target_sd=sd,
                    equipment=self.qc_equipment,
                    analyst=self.qc_analyst,
                    status=status,
                    westgard_violations=violations,
                    z_score=z_score
                )
                
                self.qc_records = [record] + self.qc_records
            
            # Limpar formulário
            self.qc_exam_name = ""
            self.qc_lot_number = ""
            self.qc_value = ""
            self.qc_value1 = ""
            self.qc_value2 = ""
            self.qc_target_value = ""
            self.qc_target_sd = ""
            self.qc_equipment = ""
            self.qc_analyst = ""
            self.qc_date = ""
            
            self.qc_success_message = f"Registro salvo! CV: {cv:.2f}% - {status}"
            
        except Exception as e:
            self.qc_error_message = f"Erro ao salvar: {str(e)}"
        finally:
            self.is_saving_qc = False

    
    async def delete_qc_record(self, record_id: str):
        """Remove um registro de CQ"""
        self.qc_error_message = ""
        self.qc_success_message = ""
        
        if supabase and record_id and len(str(record_id)) > 10:  # Check for valid UUID length
            success = await QCService.delete_qc_record(str(record_id))
            if success:
                await self.load_data_from_db(force=True)
                self.qc_success_message = "Registro removido com sucesso!"
            else:
                self.qc_error_message = "Falha ao remover registro do banco"
        else:
            # Fallback for local or short IDs
            initial_count = len(self.qc_records)
            self.qc_records = [r for r in self.qc_records if str(r.id) != str(record_id)]
            if len(self.qc_records) < initial_count:
                self.qc_success_message = "Registro removido (local)"
            else:
                self.qc_error_message = f"Registro não encontrado: {record_id}"

    async def clear_all_qc_records(self):
        """Remove todos os registros (CUIDADO!)"""
        if not supabase:
            self.qc_records = []
            self.qc_success_message = "Todos os dados locais foram removidos"
            return

        try:
            # Em um cenário real, poderíamos ter uma confirmação
            # Por enquanto, vamos remover os últimos registros se confirmado ou todos
            # Supabase delete sem filtro costuma ser bloqueado por segurança (RLS)
            # Vamos remover apenas os que estão na lista atual para segurança
            for record in self.qc_records:
                if record.id:
                    await QCService.delete_qc_record(record.id)
            
            await self.load_data_from_db()
            self.qc_success_message = "Histórico limpo com sucesso!"
        except Exception as e:
            self.qc_error_message = f"Erro ao limpar histórico: {str(e)}"
    
    # Gestão de Reagentes
    def set_reagent_name(self, value: str):
        self.reagent_name = value
    
    def set_reagent_lot_number(self, value: str):
        self.reagent_lot_number = value
    
    def set_reagent_expiry_date(self, value: str):
        self.reagent_expiry_date = value
    
    def set_reagent_quantity(self, value: str):
        self.reagent_quantity = value
    
    def set_reagent_manufacturer(self, value: str):
        self.reagent_manufacturer = value
    
    def set_reagent_storage_temp(self, value: str):
        self.reagent_storage_temp = value

    def set_reagent_initial_stock(self, value: str):
        self.reagent_initial_stock = value
        
    def set_reagent_daily_consumption(self, value: str):
        self.reagent_daily_consumption = value
    
    async def save_reagent_lot(self):
        """Salva um novo lote de reagente"""
        self.is_saving_reagent = True
        self.reagent_error_message = ""
        self.reagent_success_message = ""
        
        try:
            if not self.reagent_name:
                self.reagent_error_message = "Informe o nome do reagente"
                return
            if not self.reagent_lot_number:
                self.reagent_error_message = "Informe o número do lote"
                return
            if not self.reagent_expiry_date:
                self.reagent_error_message = "Informe a data de validade"
                return
            
            if supabase:
                lot_data = {
                    "name": self.reagent_name,
                    "lot_number": self.reagent_lot_number,
                    "expiry_date": self.reagent_expiry_date,
                    "quantity": self.reagent_quantity,
                    "manufacturer": self.reagent_manufacturer,
                    "storage_temp": self.reagent_storage_temp,
                    "current_stock": float(self.reagent_initial_stock) if self.reagent_initial_stock else 0.0,
                    "estimated_consumption": float(self.reagent_daily_consumption) if self.reagent_daily_consumption else 0.0
                }
                await ReagentService.create_reagent_lot(lot_data)
                await self.load_data_from_db(force=True)
                self.reagent_success_message = "Lote cadastrado no Supabase!"
            else:
                lot = ReagentLot(
                    id=str(len(self.reagent_lots) + 1),
                    name=self.reagent_name,
                    lot_number=self.reagent_lot_number,
                    expiry_date=self.reagent_expiry_date,
                    quantity=self.reagent_quantity,
                    manufacturer=self.reagent_manufacturer,
                    storage_temp=self.reagent_storage_temp,
                    current_stock=float(self.reagent_initial_stock) if self.reagent_initial_stock else 0.0,
                    estimated_consumption=float(self.reagent_daily_consumption) if self.reagent_daily_consumption else 0.0,
                    created_at=datetime.now().strftime("%Y-%m-%d %H:%M")
                )
                self.reagent_lots = [lot] + self.reagent_lots
                self.reagent_success_message = "Lote cadastrado (local)!"
            
            # Limpar formulário
            self.reagent_name = ""
            self.reagent_lot_number = ""
            self.reagent_expiry_date = ""
            self.reagent_quantity = ""
            self.reagent_manufacturer = ""
            self.reagent_storage_temp = ""
            self.reagent_initial_stock = ""
            self.reagent_daily_consumption = ""
            
        except Exception as e:
            self.reagent_error_message = f"Erro ao salvar: {str(e)}"
        finally:
            self.is_saving_reagent = False
    
    async def delete_reagent_lot(self, lot_id: str):
        """Remove um lote de reagente"""
        if supabase:
            success = await ReagentService.delete_reagent_lot(lot_id)
            if success:
                await self.load_data_from_db(force=True)
                self.reagent_success_message = "Lote removido/inativado"
        else:
            self.reagent_lots = [r for r in self.reagent_lots if r.id != lot_id]
            self.reagent_success_message = "Lote removido"
    
    # Manutenções
    def set_maintenance_equipment(self, value: str):
        self.maintenance_equipment = value
    
    def set_maintenance_type(self, value: str):
        self.maintenance_type = value
    
    def set_maintenance_date(self, value: str):
        self.maintenance_date = value
    
    def set_maintenance_next_date(self, value: str):
        self.maintenance_next_date = value
    
    def set_maintenance_technician(self, value: str):
        self.maintenance_technician = value
    
    def set_maintenance_notes(self, value: str):
        self.maintenance_notes = value
    
    async def save_maintenance_record(self):
        """Salva um novo registro de manutenção"""
        self.is_saving_maintenance = True
        self.maintenance_error_message = ""
        self.maintenance_success_message = ""
        
        try:
            if not self.maintenance_equipment:
                self.maintenance_error_message = "Informe o equipamento"
                return
            if not self.maintenance_type:
                self.maintenance_error_message = "Informe o tipo de manutenção"
                return
            
            if supabase:
                record_data = {
                    "equipment": self.maintenance_equipment,
                    "type": self.maintenance_type,
                    "date": self.maintenance_date or datetime.now().strftime("%Y-%m-%d"),
                    "next_date": self.maintenance_next_date,
                    "technician": self.maintenance_technician,
                    "notes": self.maintenance_notes
                }
                await MaintenanceService.create_maintenance_record(record_data)
                await self.load_data_from_db(force=True)
                self.maintenance_success_message = "Manutenção registrada no Supabase!"
            else:
                record = MaintenanceRecord(
                    id=str(len(self.maintenance_records) + 1),
                    equipment=self.maintenance_equipment,
                    type=self.maintenance_type,
                    date=self.maintenance_date or datetime.now().strftime("%Y-%m-%d"),
                    next_date=self.maintenance_next_date,
                    technician=self.maintenance_technician,
                    notes=self.maintenance_notes,
                    created_at=datetime.now().strftime("%Y-%m-%d %H:%M")
                )
                self.maintenance_records = [record] + self.maintenance_records
                self.maintenance_success_message = "Manutenção registrada (local)!"
            
            # Limpar formulário
            self.maintenance_equipment = ""
            self.maintenance_type = ""
            self.maintenance_date = ""
            self.maintenance_next_date = ""
            self.maintenance_technician = ""
            self.maintenance_notes = ""
            
        except Exception as e:
            self.maintenance_error_message = f"Erro ao salvar: {str(e)}"
        finally:
            self.is_saving_maintenance = False
    
    async def delete_maintenance_record(self, record_id: str):
        """Remove um registro de manutenção"""
        if supabase:
            success = await MaintenanceService.delete_maintenance_record(record_id)
            if success:
                await self.load_data_from_db(force=True)
                self.maintenance_success_message = "Registro removido do banco"
            else:
                self.maintenance_error_message = "Falha ao remover registro"
        else:
            self.maintenance_records = [r for r in self.maintenance_records if r.id != record_id]
            self.maintenance_success_message = "Registro removido"
    
    def set_levey_jennings_exam(self, value: str):
        self.levey_jennings_exam = value
        self.update_levey_jennings_data()
    
    def set_levey_jennings_period(self, value: str):
        self.levey_jennings_period = value
        self.update_levey_jennings_data()
    
    def update_levey_jennings_data(self, args=None):
        """Atualiza os dados para o gráfico Levey-Jennings"""
        if not self.levey_jennings_exam:
            self.levey_jennings_data = []
            return
        
        from datetime import timedelta
        days = int(self.levey_jennings_period) if self.levey_jennings_period else 30
        cutoff_date = datetime.now() - timedelta(days=days)
        
        filtered_records = []
        for r in self.qc_records:
            if r.exam_name == self.levey_jennings_exam:
                try:
                    record_date = datetime.strptime(r.date[:10], "%Y-%m-%d")
                    if record_date >= cutoff_date:
                        filtered_records.append(LeveyJenningsPoint(
                            date=r.date[:10],
                            value=r.mean,
                            target=r.target_value,
                            sd=r.target_sd,
                            cv=r.cv
                        ))
                except:
                    pass
        
        self.levey_jennings_data = sorted(filtered_records, key=lambda x: x.date)
    
    # Levey-Jennings level filter
    levey_jennings_level: str = "Todos"
    
    def set_levey_jennings_level(self, value: str):
        self.levey_jennings_level = value
    
    @rx.var
    def levey_jennings_chart_data(self) -> List[Dict[str, Any]]:
        """Returns chart-ready data for Recharts"""
        return [
            {
                "date": point.date,
                "value": point.value,
                "target": point.target,
                "sd": point.sd,
                "cv": point.cv
            }
            for point in self.levey_jennings_data
        ]
    
    @rx.var
    def lj_mean(self) -> float:
        """Mean of all values in the Levey-Jennings data"""
        if not self.levey_jennings_data:
            return 0.0
        values = [p.value for p in self.levey_jennings_data]
        return round(sum(values) / len(values), 2)
    
    @rx.var
    def lj_sd(self) -> float:
        """Standard deviation of Levey-Jennings data"""
        if len(self.levey_jennings_data) < 2:
            return 0.0
        values = [p.value for p in self.levey_jennings_data]
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return round(variance ** 0.5, 2)
    
    @rx.var
    def lj_cv_mean(self) -> float:
        """Mean CV% from the Levey-Jennings data"""
        if not self.levey_jennings_data:
            return 0.0
        cv_values = [p.cv for p in self.levey_jennings_data]
        return round(sum(cv_values) / len(cv_values), 2)
    
    @rx.var
    def lj_target_plus_1sd(self) -> float:
        """Target + 1 SD for reference line"""
        if not self.levey_jennings_data:
            return 0.0
        avg_target = sum(p.target for p in self.levey_jennings_data) / len(self.levey_jennings_data)
        avg_sd = sum(p.sd for p in self.levey_jennings_data) / len(self.levey_jennings_data)
        return round(avg_target + avg_sd, 2)
    
    @rx.var
    def lj_target_minus_1sd(self) -> float:
        """Target - 1 SD for reference line"""
        if not self.levey_jennings_data:
            return 0.0
        avg_target = sum(p.target for p in self.levey_jennings_data) / len(self.levey_jennings_data)
        avg_sd = sum(p.sd for p in self.levey_jennings_data) / len(self.levey_jennings_data)
        return round(avg_target - avg_sd, 2)
    
    @rx.var
    def lj_target_plus_2sd(self) -> float:
        """Target + 2 SD for reference line"""
        if not self.levey_jennings_data:
            return 0.0
        avg_target = sum(p.target for p in self.levey_jennings_data) / len(self.levey_jennings_data)
        avg_sd = sum(p.sd for p in self.levey_jennings_data) / len(self.levey_jennings_data)
        return round(avg_target + 2 * avg_sd, 2)
    
    @rx.var
    def lj_target_minus_2sd(self) -> float:
        """Target - 2 SD for reference line"""
        if not self.levey_jennings_data:
            return 0.0
        avg_target = sum(p.target for p in self.levey_jennings_data) / len(self.levey_jennings_data)
        avg_sd = sum(p.sd for p in self.levey_jennings_data) / len(self.levey_jennings_data)
        return round(avg_target - 2 * avg_sd, 2)
    
    @rx.var
    def lj_target_plus_3sd(self) -> float:
        """Target + 3 SD for reference line"""
        if not self.levey_jennings_data:
            return 0.0
        avg_target = sum(p.target for p in self.levey_jennings_data) / len(self.levey_jennings_data)
        avg_sd = sum(p.sd for p in self.levey_jennings_data) / len(self.levey_jennings_data)
        return round(avg_target + 3 * avg_sd, 2)
    
    @rx.var
    def lj_target_minus_3sd(self) -> float:
        """Target - 3 SD for reference line"""
        if not self.levey_jennings_data:
            return 0.0
        avg_target = sum(p.target for p in self.levey_jennings_data) / len(self.levey_jennings_data)
        avg_sd = sum(p.sd for p in self.levey_jennings_data) / len(self.levey_jennings_data)
        return round(avg_target - 3 * avg_sd, 2)
    

    
    @rx.var
    def unique_equipment_names(self) -> List[str]:
        """Lista de equipamentos únicos"""
        names = set()
        for r in self.qc_records:
            if r.equipment:
                names.add(r.equipment)
        for m in self.maintenance_records:
            if m.equipment:
                names.add(m.equipment)
        return sorted(list(names))
    
    # ===== Resolution & History Management (V1.1) =====
    
    async def load_resolutions(self):
        """Carrega resoluções salvas (Stub para V1.1)"""
        pass

    def toggle_resolution(self, patient: str, exam: str):
        """Alterna estado de resolução para uma divergência"""
        key = f"{patient}|{exam}"
        if key in self.resolutions:
            del self.resolutions[key]
        else:
            self.resolutions[key] = "resolved"
            
    def view_patient_history(self, patient_name: str):
        """Abre modal de histórico do paciente"""
        self.selected_patient_name = patient_name
        self.is_showing_patient_history = True
        self.patient_history_data = [] # Reset
        
        if not self._compulab_patients:
            self.error_message = "Dados da análise não encontrados. Por favor, execute a análise novamente."
            self.is_showing_patient_history = False
            return

        # Procurar dados do paciente nos dados atuais
        patient_exams = []
        if patient_name in self._compulab_patients:
            patient_exams = self._compulab_patients[patient_name].get('exams', [])
            
        for exam in patient_exams:
             self.patient_history_data.append(
                 PatientHistoryEntry(
                     patient_id="temp",
                     patient_name=patient_name,
                     exam_name=exam.get('exam_name', 'Unknown'),
                     status="resolvido", # Mock
                     last_value=float(exam.get('value', 0)),
                     created_at=datetime.now().strftime("%Y-%m-%d %H:%M")
                 )
             )

    def close_patient_history(self):
        """Fecha modal de histórico"""
        self.is_showing_patient_history = False
        self.selected_patient_name = ""

    async def import_data_to_qc(self):
        """Importa os dados normalizados para o Controle de Qualidade"""
        if not self.has_excel_file or not self.excel_analyzed or self._excel_dataframe is None:
            self.excel_error_message = "Analise um arquivo primeiro"
            return
        
        self.is_analyzing_excel = True
        self.excel_error_message = ""
        
        try:
            df = self._excel_dataframe
            imported_count = 0
            
            for _, row in df.iterrows():
                try:
                    exam_name = str(row["exam_name"])
                    value = float(row["value"])
                    
                    if not exam_name or value == 0: continue
                    
                    date = str(row["date"])
                    target = float(row["target_value"])
                    sd = float(row["target_sd"])
                    cv = float(row["cv"]) if "cv" in row else 0.0
                    
                    # Se CV está zerado mas temos value e target, calcular
                    if cv == 0 and target > 0 and sd > 0:
                        cv = (sd / target) * 100
                    
                    status = "OK"
                    if cv > 10.0: status = "Alerta" # Regra simples para importação
                    
                    # Calcular SD reverso se temos CV e Target?
                    if sd == 0 and target > 0 and cv != 0:
                        sd = (cv * target) / 100

                    record = QCRecord(
                        id=str(len(self.qc_records) + imported_count + 1),
                        date=date,
                        exam_name=exam_name,
                        level="Normal", # Default
                        lot_number=str(row.get("lot_number", "")),
                        value=value,
                        value1=value,
                        value2=0.0,
                        mean=value,
                        sd=sd,
                        cv=round(cv, 2),
                        target_value=target,
                        target_sd=sd,
                        equipment=str(row.get("equipment", "")),
                        analyst=str(row.get("analyst", "Importado")),
                        status=status
                    )
                    self.qc_records = [record] + self.qc_records
                    imported_count += 1
                except:
                    continue
            
            if imported_count > 0:
                self.excel_success_message = f"Sucesso! {imported_count} registros importados."
                # Salvar no banco se disponível
                if supabase:
                    # Aqui apenas carregamos na memória local por enquanto para não spammar o banco
                    # Se quisesse salvar, teria que iterar e chamar create_qc_record
                    pass
            else:
                self.excel_error_message = "Nenhum registro importado. Verifique os dados."
                
        except Exception as e:
            self.excel_error_message = f"Erro na importação: {str(e)}"
        finally:
            self.is_analyzing_excel = False

