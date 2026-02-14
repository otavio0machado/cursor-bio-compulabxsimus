import os
import reflex as rx
import asyncio
import base64
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

CACHE_TTL_SECONDS = int(os.environ.get("CACHE_TTL_SECONDS", "30"))
from ..models import QCRecord, ReagentLot, MaintenanceRecord, LeveyJenningsPoint, QCReferenceValue, PostCalibrationRecord, ImunologiaRecord, HematologyQCParameter, HematologyQCMeasurement, HematologyBioRecord
from ..services.qc_service import QCService
from ..services.hematology_qc_service import HematologyQCService
from ..services.qc_reference_service import QCReferenceService
from ..services.westgard_service import WestgardService
from ..services.reagent_service import ReagentService
from ..services.maintenance_service import MaintenanceService
from ..services.post_calibration_service import PostCalibrationService
from ..services.qc_exam_service import QCExamService
from ..services.qc_registry_name_service import QCRegistryNameService
from ..utils.numeric import parse_decimal
from . import (
    _voice_ops, _report_ops, _reagent_ops, _maintenance_ops,
    _reference_ops, _post_calibration_ops, _import_ops,
)
from .dashboard_state import DashboardState
from ._outras_areas_qc import OutrasAreasQCMixin

class QCState(OutrasAreasQCMixin, DashboardState):
    """Estado responsável pelo Controle de Qualidade (ProIn), Reagentes e Manutenções"""
    
    # ===== ProIn QC - Sistema de Controle de Qualidade =====
    proin_current_tab: str = "dashboard"  # dashboard, registro, reagentes, relatorios, importar, outros_registros
    outros_registros_area: str = "hematologia"  # hematologia, imunologia, parasitologia, microbiologia, uroanalise
    
    # Registros de CQ (Controle de Qualidade)
    qc_records: List[QCRecord] = []
    qc_exam_name: str = ""
    qc_level: str = "Normal"
    qc_lot_number: str = ""
    qc_value: str = ""
    qc_value1: str = ""
    qc_value2: str = ""
    qc_target_value: str = ""
    qc_target_sd: str = ""
    qc_equipment: str = ""
    qc_analyst: str = ""
    qc_date: str = ""
    is_saving_qc: bool = False
    qc_success_message: str = ""
    qc_warning_message: str = ""
    qc_error_message: str = ""

    # Lista dinamica de exames (carregada do banco)
    qc_exams_list: List[str] = []
    show_add_exam_modal: bool = False
    new_exam_name: str = ""
    add_exam_error: str = ""

    # ProIn Import State
    is_importing: bool = False
    proin_import_preview: List[List[str]] = []
    proin_import_headers: List[str] = []
    proin_import_data: List[Dict[str, Any]] = []
    upload_progress: int = 0
    
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
    maintenance_new_equipment_mode: bool = False  # True = digitar novo, False = selecionar
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
    levey_jennings_level: str = "Todos"
    levey_jennings_period: str = "30"

    # Alertas do Dashboard (QC related)
    qc_alerts: List[QCRecord] = []
    expiring_lots: List[ReagentLot] = []
    
    # Relatórios PDF - QC
    qc_report_type: str = "Mês Atual"
    qc_report_month: str = str(datetime.now().month)
    qc_report_year: str = str(datetime.now().year)
    qc_pdf_preview: str = "" # Base64 preview

    # === Valores de Referência do CQ ===
    qc_reference_values: List[QCReferenceValue] = []  # Cache local de referências
    current_exam_reference: Optional[Dict[str, Any]] = None  # Referência ativa do exame selecionado

    # Formulário de Cadastro de Referência
    ref_name: str = ""
    ref_exam_name: str = ""
    ref_valid_from: str = ""
    ref_valid_until: str = ""
    ref_target_value: str = ""
    ref_cv_max_threshold: str = "10.0"
    ref_lot_number: str = ""
    ref_manufacturer: str = ""
    ref_level: str = "Normal"
    ref_notes: str = ""
    is_saving_reference: bool = False
    ref_success_message: str = ""
    ref_error_message: str = ""

    # Lista dinamica de nomes de registro (carregada do banco)
    qc_registry_names: List[str] = []
    show_add_name_modal: bool = False
    new_registry_name: str = ""
    add_name_error: str = ""

    # === Pop-up Medição Pós-Calibração ===
    post_calibration_records: List[PostCalibrationRecord] = []  # Histórico de pós-calibrações
    show_post_calibration_modal: bool = False
    selected_qc_record_for_calibration: Optional[Dict[str, Any]] = None
    post_cal_value: str = ""
    post_cal_analyst: str = ""
    post_cal_notes: str = ""
    is_saving_post_calibration: bool = False
    post_cal_success_message: str = ""
    post_cal_error_message: str = ""

    # === Modais de Confirmação de Exclusão ===
    show_delete_qc_record_modal: bool = False
    delete_qc_record_id: str = ""
    delete_qc_record_name: str = ""

    # Soft-delete: registro recém-excluído disponível para restauração
    last_deleted_qc_record: Optional[Dict[str, Any]] = None

    show_delete_reference_modal: bool = False
    delete_reference_id: str = ""
    delete_reference_name: str = ""

    # Modal de confirmação para limpar todos os registros
    show_clear_all_modal: bool = False

    # === Voice-to-Form (Voz para Formulario) ===
    show_voice_modal: bool = False
    voice_form_target: str = ""       # "registro", "referencia", "reagente", "manutencao"
    voice_is_recording: bool = False
    voice_is_processing: bool = False
    voice_audio_base64: str = ""
    voice_status_message: str = ""
    voice_error_message: str = ""

    # === Hematologia (Outros Registros) ===
    hemato_bio_hemacias: str = ""
    hemato_bio_hematocrito: str = ""
    hemato_bio_hemoglobina: str = ""
    hemato_bio_leucocitos: str = ""
    hemato_bio_plaquetas: str = ""
    hemato_bio_rdw: str = ""
    hemato_bio_vpm: str = ""
    hemato_bio_registro: str = ""
    hemato_bio_data: str = ""
    hemato_pad_hemacias: str = ""
    hemato_pad_hematocrito: str = ""
    hemato_pad_hemoglobina: str = ""
    hemato_pad_leucocitos: str = ""
    hemato_pad_plaquetas: str = ""
    hemato_pad_rdw: str = ""
    hemato_pad_vpm: str = ""
    hemato_pad_registro: str = ""
    hemato_pad_data: str = ""
    hemato_success_message: str = ""
    hemato_error_message: str = ""
    is_saving_hemato: bool = False
    # Controle Interno - modo de comparação e campos adicionais
    hemato_ci_mode: str = "bio"  # "bio" | "intervalo" | "porcentagem"
    hemato_ci_min_hemacias: str = ""
    hemato_ci_max_hemacias: str = ""
    hemato_ci_min_hematocrito: str = ""
    hemato_ci_max_hematocrito: str = ""
    hemato_ci_min_hemoglobina: str = ""
    hemato_ci_max_hemoglobina: str = ""
    hemato_ci_min_leucocitos: str = ""
    hemato_ci_max_leucocitos: str = ""
    hemato_ci_min_plaquetas: str = ""
    hemato_ci_max_plaquetas: str = ""
    hemato_ci_min_rdw: str = ""
    hemato_ci_max_rdw: str = ""
    hemato_ci_min_vpm: str = ""
    hemato_ci_max_vpm: str = ""
    hemato_ci_pct_hemacias: str = ""
    hemato_ci_pct_hematocrito: str = ""
    hemato_ci_pct_hemoglobina: str = ""
    hemato_ci_pct_leucocitos: str = ""
    hemato_ci_pct_plaquetas: str = ""
    hemato_ci_pct_rdw: str = ""
    hemato_ci_pct_vpm: str = ""

    # === Histórico Bio x CI (Hematologia) ===
    hemato_bio_records: List[HematologyBioRecord] = []
    show_hemato_bio_detail: bool = False
    selected_hemato_bio_record: HematologyBioRecord = HematologyBioRecord()

    # === Imunologia (Outros Registros) ===
    imuno_controle: str = ""
    imuno_fabricante: str = ""
    imuno_lote: str = ""
    imuno_data: str = ""
    imuno_resultado: str = ""
    imuno_records: List[ImunologiaRecord] = []
    imuno_success_message: str = ""
    imuno_error_message: str = ""
    is_saving_imuno: bool = False
    imuno_search_term: str = ""
    imuno_history_date: str = ""

    # === Hematologia CQ por Intervalo/% ===
    hemato_qc_sub_tab: str = "tabela"   # "tabela" (original) | "cq_intervalo"
    # Parâmetros (regras)
    hqc_parameters: List[HematologyQCParameter] = []
    hqc_show_inactive: bool = False
    hqc_param_analito: str = ""
    hqc_param_modo: str = "INTERVALO"
    hqc_param_alvo: str = ""
    hqc_param_min: str = ""
    hqc_param_max: str = ""
    hqc_param_tolerancia: str = ""
    hqc_param_equipamento: str = ""
    hqc_param_lote: str = ""
    hqc_param_nivel: str = ""
    hqc_param_edit_id: str = ""         # Se preenchido, edita ao invés de criar
    is_saving_hqc_param: bool = False
    hqc_param_success: str = ""
    hqc_param_error: str = ""
    # Medição (lançamento)
    hqc_meas_data: str = ""
    hqc_meas_analito: str = ""
    hqc_meas_valor: str = ""
    hqc_meas_equipamento: str = ""
    hqc_meas_lote: str = ""
    hqc_meas_nivel: str = ""
    hqc_meas_observacao: str = ""
    is_saving_hqc_meas: bool = False
    hqc_meas_success: str = ""
    hqc_meas_error: str = ""
    hqc_last_result: Optional[Dict[str, Any]] = None  # Último resultado da RPC
    # Histórico de medições
    hqc_measurements: List[HematologyQCMeasurement] = []
    hqc_meas_filter_analito: str = ""
    hqc_meas_filter_status: str = "Todos"
    hqc_meas_search: str = ""

    # Loading state for initial data load
    is_loading_data: bool = False

    # Busca e filtros da tabela QC
    qc_search_term: str = ""
    qc_status_filter: str = "Todos"

    # Navegação por dia no histórico
    qc_history_date: str = ""

    # Pagination (reagentes e manutenções)
    qc_page: int = 0
    qc_page_size: int = 50
    reagent_page: int = 0
    reagent_page_size: int = 20
    maintenance_page: int = 0
    maintenance_page_size: int = 20

    # Data cache timestamp
    _last_loaded: str = ""

    def set_qc_report_type(self, value: str):
        """Define o tipo de relatório (Mês Atual, Específico, etc)"""
        self.qc_report_type = value
        return self.update_qc_preview()
    def set_qc_report_month(self, value: str):
        """Define o mês para o relatório específico"""
        self.qc_report_month = value
        return self.update_qc_preview()
    def set_qc_exam_name(self, value: str):
        """Define o nome do exame selecionado"""
        self.qc_exam_name = value

    def set_qc_lot_number(self, value: str):
        """Define o número do lote"""
        self.qc_lot_number = value

    def set_maintenance_notes(self, value: str):
        """Define as notas de manutenção"""
        self.maintenance_notes = value

    def set_qc_date(self, value: str):
        self.qc_date = value

    def set_qc_search_term(self, value: str):
        self.qc_search_term = value
        self.qc_page = 0  # Reset paginação ao buscar

    def set_qc_status_filter(self, value: str):
        self.qc_status_filter = value
        self.qc_page = 0

    def set_maintenance_type(self, value: str):
        self.maintenance_type = value

    def set_qc_target_sd(self, value: str):
        self.qc_target_sd = value

    def set_qc_equipment(self, value: str):
        self.qc_equipment = value

    def set_qc_analyst(self, value: str):
        self.qc_analyst = value

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

    # Setters for Maintenance (Explicitly defined to avoid DeprecationWarning)
    def set_maintenance_equipment(self, value: str):
        self.maintenance_equipment = value

    def set_maintenance_new_equipment_mode(self, value: bool):
        self.maintenance_new_equipment_mode = value
        if value:
            self.maintenance_equipment = ""

    def set_maintenance_date(self, value: str):
        self.maintenance_date = value

    def set_maintenance_next_date(self, value: str):
        self.maintenance_next_date = value

    def set_maintenance_technician(self, value: str):
        self.maintenance_technician = value

    def set_qc_level(self, value: str):
        self.qc_level = value

    # Computed CV & Status
    @rx.var
    def qc_calculated_cv(self) -> float:
        """Calcula CV = (SD/Média)*100"""
        try:
            val = float(self.qc_value or 0)
            target = float(self.qc_target_value or 0)
            if target == 0: return 0.0
            diff = abs(val - target)
            return (diff / target) * 100
        except (ValueError, TypeError):
            return 0.0

    @rx.var
    def filtered_qc_records(self) -> List[QCRecord]:
        """Registros filtrados por busca e status"""
        records = self.qc_records
        # Filtro por nome do exame
        search = (self.qc_search_term or "").strip().upper()
        if search:
            records = [r for r in records if search in (r.exam_name or "").upper()]
        # Filtro por status (baseado em CV% vs threshold)
        status_filter = self.qc_status_filter or "Todos"
        if status_filter == "OK":
            records = [r for r in records if r.cv <= r.cv_max_threshold]
        elif status_filter == "ALERTA":
            records = [r for r in records if r.cv > r.cv_max_threshold]
        elif status_filter == "ERRO":
            records = [r for r in records if r.cv > r.cv_max_threshold]
        return records

    @rx.var
    def paginated_qc_records(self) -> List[QCRecord]:
        """Retorna registros filtrados pelo dia selecionado"""
        records = self.filtered_qc_records
        target_date = (self.qc_history_date or "").strip()
        if target_date:
            records = [r for r in records if (r.date or "")[:10] == target_date]
        return records

    @rx.var
    def qc_history_date_display(self) -> str:
        """Formata a data do histórico para exibição (DD/MM/AAAA)"""
        d = (self.qc_history_date or "").strip()
        if len(d) >= 10:
            try:
                parts = d[:10].split("-")
                return f"{parts[2]}/{parts[1]}/{parts[0]}"
            except (IndexError, ValueError):
                return d
        return d

    def set_qc_history_date(self, value: str):
        """Define a data do histórico"""
        self.qc_history_date = value

    def next_qc_day(self):
        """Avança um dia no histórico"""
        try:
            current = datetime.strptime(self.qc_history_date, "%Y-%m-%d")
            self.qc_history_date = (current + timedelta(days=1)).strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            self.qc_history_date = datetime.now().strftime("%Y-%m-%d")

    def prev_qc_day(self):
        """Retrocede um dia no histórico"""
        try:
            current = datetime.strptime(self.qc_history_date, "%Y-%m-%d")
            self.qc_history_date = (current - timedelta(days=1)).strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            self.qc_history_date = datetime.now().strftime("%Y-%m-%d")

    # ── Reagent pagination ──
    @rx.var
    def paginated_reagent_lots(self) -> List[ReagentLot]:
        start = self.reagent_page * self.reagent_page_size
        return self.reagent_lots[start:start + self.reagent_page_size]

    @rx.var
    def total_reagent_pages(self) -> int:
        total = len(self.reagent_lots)
        if total == 0:
            return 1
        return (total + self.reagent_page_size - 1) // self.reagent_page_size

    def next_reagent_page(self):
        if self.reagent_page < self.total_reagent_pages - 1:
            self.reagent_page += 1

    def prev_reagent_page(self):
        if self.reagent_page > 0:
            self.reagent_page -= 1

    # ── Equipment options from maintenance history ──
    @rx.var
    def unique_equipment_names(self) -> List[str]:
        """Lista de nomes únicos de equipamentos já cadastrados em manutenções"""
        seen = set()
        result = []
        for r in self.maintenance_records:
            name = (r.equipment or "").strip()
            if name and name not in seen:
                seen.add(name)
                result.append(name)
        return sorted(result)

    # ── Maintenance pagination ──
    @rx.var
    def paginated_maintenance_records(self) -> List[MaintenanceRecord]:
        start = self.maintenance_page * self.maintenance_page_size
        return self.maintenance_records[start:start + self.maintenance_page_size]

    @rx.var
    def total_maintenance_pages(self) -> int:
        total = len(self.maintenance_records)
        if total == 0:
            return 1
        return (total + self.maintenance_page_size - 1) // self.maintenance_page_size

    def next_maintenance_page(self):
        if self.maintenance_page < self.total_maintenance_pages - 1:
            self.maintenance_page += 1

    def prev_maintenance_page(self):
        if self.maintenance_page > 0:
            self.maintenance_page -= 1

    @rx.var
    def qc_cv_status(self) -> str:
        """Status do CV baseado no limite máximo parametrizado"""
        cv = self.qc_calculated_cv

        # Buscar limite máximo da referência atual (se houver)
        max_threshold = 10.0  # Default

        if self.current_exam_reference:
            max_threshold = float(self.current_exam_reference.get("cv_max_threshold", 10.0))

        if cv <= max_threshold:
            return "OK"
        return "ERRO"

    @rx.var
    def current_cv_max_threshold(self) -> float:
        """Retorna o limite máximo atual (para exibição na UI)"""
        if self.current_exam_reference:
            return float(self.current_exam_reference.get("cv_max_threshold", 10.0))
        return 10.0

    @rx.var
    def has_undo_delete(self) -> bool:
        """Há registro recém-excluído disponível para restauração"""
        return self.last_deleted_qc_record is not None

    @rx.var
    def has_active_reference(self) -> bool:
        """Verifica se há referência ativa para o exame selecionado"""
        return self.current_exam_reference is not None
        
    # Levey-Jennings Stats (Legacy props for older chart components)
    @rx.var
    def lj_mean(self) -> float:
        if not self.levey_jennings_data: return 0.0
        return sum(p.value for p in self.levey_jennings_data) / len(self.levey_jennings_data)
        
    @rx.var
    def lj_sd(self) -> float:
        # Simplificação para evitar numpy
        if not self.levey_jennings_data: return 0.0
        mean = self.lj_mean
        variance = sum((p.value - mean) ** 2 for p in self.levey_jennings_data) / len(self.levey_jennings_data)
        return variance ** 0.5
        
    @rx.var
    def lj_cv_mean(self) -> float:
        if not self.levey_jennings_data: return 0.0
        return sum(p.cv for p in self.levey_jennings_data) / len(self.levey_jennings_data)

    # Levey-Jennings Bounds (Mock or Calculated based on target)
    @rx.var 
    def lj_target_val(self) -> float:
        if self.levey_jennings_data: return self.levey_jennings_data[-1].target
        return 0.0
        
    @rx.var
    def lj_target_sd_val(self) -> float:
         if self.levey_jennings_data: return self.levey_jennings_data[-1].sd
         return 0.0

    @rx.var
    def lj_target_plus_1sd(self) -> float: return self.lj_target_val + self.lj_target_sd_val
    @rx.var
    def lj_target_minus_1sd(self) -> float: return self.lj_target_val - self.lj_target_sd_val
    @rx.var
    def lj_target_plus_2sd(self) -> float: return self.lj_target_val + (2 * self.lj_target_sd_val)
    @rx.var
    def lj_target_minus_2sd(self) -> float: return self.lj_target_val - (2 * self.lj_target_sd_val)
    @rx.var
    def lj_target_plus_3sd(self) -> float: return self.lj_target_val + (3 * self.lj_target_sd_val)
    @rx.var
    def lj_target_minus_3sd(self) -> float: return self.lj_target_val - (3 * self.lj_target_sd_val)
    
    @rx.var
    def lj_min_domain(self) -> float:
        """Limite inferior do gráfico — quando SD=0, calcula a partir dos dados reais"""
        if self.lj_target_sd_val > 0:
            return self.lj_target_val - (4 * self.lj_target_sd_val)
        # SD=0: calcular domínio a partir dos valores e target reais
        if not self.levey_jennings_data:
            return 0.0
        all_vals = [p.value for p in self.levey_jennings_data]
        target = self.lj_target_val
        min_val = min(min(all_vals), target) if all_vals else target
        spread = max(abs(max(all_vals) - target), abs(target - min(all_vals)), target * 0.1) if all_vals else target * 0.1
        return min_val - spread * 0.5

    @rx.var
    def lj_max_domain(self) -> float:
        """Limite superior do gráfico — quando SD=0, calcula a partir dos dados reais"""
        if self.lj_target_sd_val > 0:
            return self.lj_target_val + (4 * self.lj_target_sd_val)
        # SD=0: calcular domínio a partir dos valores e target reais
        if not self.levey_jennings_data:
            return 100.0
        all_vals = [p.value for p in self.levey_jennings_data]
        target = self.lj_target_val
        max_val = max(max(all_vals), target) if all_vals else target
        spread = max(abs(max(all_vals) - target), abs(target - min(all_vals)), target * 0.1) if all_vals else target * 0.1
        return max_val + spread * 0.5

    # Fallback hardcoded (usado apenas se banco estiver indisponivel)
    _FALLBACK_EXAMS: List[str] = [
        "GLICOSE", "COLESTEROL TOTAL", "TRIGLICERIDEOS", "UREIA",
        "CREATININA", "ACIDO URICO", "GOT", "GPT", "GAMA GT",
        "FOSFATASE ALCALINA", "AMILASE", "CREATINOFOSFOQUINASE",
        "COLESTEROL HDL", "COLESTEROL LDL"
    ]

    @rx.var
    def unique_exam_names(self) -> List[str]:
        """Lista de exames para dropdown (do banco, na ordem de cadastro)"""
        if self.qc_exams_list:
            return list(self.qc_exams_list)
        return list(self._FALLBACK_EXAMS)

    async def load_qc_exams(self):
        """Carrega lista de exames do banco"""
        try:
            names = await QCExamService.get_exam_names(active_only=True)
            if names:
                self.qc_exams_list = names
            elif not self.qc_exams_list:
                self.qc_exams_list = list(self._FALLBACK_EXAMS)
        except Exception as e:
            logger.error(f"Erro ao carregar exames: {e}")
            if not self.qc_exams_list:
                self.qc_exams_list = list(self._FALLBACK_EXAMS)

    async def add_new_exam(self):
        """Adiciona novo exame ao banco e recarrega lista"""
        name = (self.new_exam_name or "").strip().upper()
        if not name:
            self.add_exam_error = "Nome do exame nao pode ser vazio"
            return
        if name in self.qc_exams_list:
            self.add_exam_error = f"Exame '{name}' ja existe"
            return
        try:
            await QCExamService.create_exam(name)
            await self.load_qc_exams()
            self.new_exam_name = ""
            self.add_exam_error = ""
            self.show_add_exam_modal = False
        except Exception as e:
            logger.error(f"Erro ao criar exame: {e}")
            self.add_exam_error = f"Erro ao salvar: {e}"

    def open_add_exam_modal(self):
        self.new_exam_name = ""
        self.add_exam_error = ""
        self.show_add_exam_modal = True

    def close_add_exam_modal(self):
        self.show_add_exam_modal = False
        self.add_exam_error = ""

    # === Handlers para Nomes de Registro ===

    async def load_registry_names(self):
        """Carrega lista de nomes de registro do banco"""
        try:
            names = await QCRegistryNameService.get_names(active_only=True)
            self.qc_registry_names = names
        except Exception as e:
            logger.error(f"Erro ao carregar nomes de registro: {e}")

    async def add_registry_name(self):
        """Adiciona novo nome de registro ao banco e recarrega lista"""
        name = (self.new_registry_name or "").strip()
        if not name:
            self.add_name_error = "Nome nao pode ser vazio"
            return
        if name in self.qc_registry_names:
            self.add_name_error = f"Nome '{name}' ja existe"
            return
        try:
            await QCRegistryNameService.create_name(name)
            await self.load_registry_names()
            self.new_registry_name = ""
            self.add_name_error = ""
            self.show_add_name_modal = False
            # Selecionar o nome recem-adicionado
            self.ref_name = name
        except Exception as e:
            logger.error(f"Erro ao criar nome de registro: {e}")
            self.add_name_error = f"Erro ao salvar: {e}"

    def open_add_name_modal(self):
        self.new_registry_name = ""
        self.add_name_error = ""
        self.show_add_name_modal = True

    def close_add_name_modal(self):
        self.show_add_name_modal = False
        self.add_name_error = ""

    def set_qc_report_year(self, value: str):
        """Define o ano para o relatório"""
        self.qc_report_year = value
        return self.update_qc_preview()
    is_generating_qc_report: bool = False

    async def set_proin_tab(self, tab: str):
        """Alterna a tab ativa do ProIn e carrega dados necessários"""
        self.proin_current_tab = tab
        # Carregar exames do banco em qualquer aba
        await self.load_qc_exams()
        # Carregar dados automaticamente ao abrir certas abas
        if tab == "referencias":
            await self.load_qc_references()
            await self.load_registry_names()
            # Sprint 5: Auto-preencher data "Valido a partir de" com hoje
            if not self.ref_valid_from:
                self.ref_valid_from = datetime.now().strftime("%Y-%m-%d")
        elif tab in ["dashboard", "registro", "relatorios"]:
            await self.load_data_from_db()
        # Auto-preencher data e equipamento ao abrir aba de registro
        if tab == "registro":
            self.qc_date = datetime.now().strftime("%Y-%m-%d")
            if not self.qc_history_date:
                self.qc_history_date = datetime.now().strftime("%Y-%m-%d")
        # Auto-preencher data da Imunologia + carregar dados CQ Hematologia
        if tab == "outros_registros":
            if not self.imuno_data:
                self.imuno_data = datetime.now().strftime("%Y-%m-%d")
            if not self.imuno_history_date:
                self.imuno_history_date = datetime.now().strftime("%Y-%m-%d")
            # Carregar dados de CQ Hematologia
            await self.load_hqc_data()
            # Auto-preencher equipamento do ultimo registro de manutencao
            if not self.qc_equipment and self.maintenance_records:
                self.qc_equipment = self.maintenance_records[0].equipment

    async def load_data_from_db(self, force: bool = False):
        """Carrega registros de QC, reagentes, manutenções e pós-calibrações do banco"""
        # Skip reload if data was recently loaded (within 30s) unless forced
        now_str = datetime.now().isoformat()
        if not force and self._last_loaded and self.qc_records:
            try:
                last = datetime.fromisoformat(self._last_loaded)
                if (datetime.now() - last).total_seconds() < CACHE_TTL_SECONDS:
                    return
            except (ValueError, TypeError):
                pass

        self.is_loading_data = True
        try:
            # Carregar exames dinamicos
            await self.load_qc_exams()

            # Carregar registros de QC
            db_records = await QCService.get_qc_records(limit=10000)

            if db_records:
                refs_by_id = {}
                ref_ids = [r.get("reference_id") for r in db_records if r.get("reference_id")]
                if ref_ids:
                    try:
                        refs_by_id = await QCReferenceService.get_references_by_ids(ref_ids)
                    except Exception as e:
                        logger.error(f"Erro ao buscar referências por ID: {e}")
                records: List[QCRecord] = []
                for r in db_records:
                    reference_id = r.get("reference_id", "") or ""
                    ref = refs_by_id.get(reference_id, {}) or {}
                    cv = float(r.get("cv", 0)) if r.get("cv") else 0.0
                    cv_max_threshold = float(ref.get("cv_max_threshold") or 10.0)
                    status = r.get("status", "OK") or "OK"
                    needs_calibration = bool(r.get("needs_calibration", False))

                    records.append(
                        QCRecord(
                            id=str(r.get("id") or ""),
                            date=r.get("date") or "",
                            exam_name=r.get("exam_name") or "",
                            level=r.get("level") or "Normal",
                            lot_number=r.get("lot_number") or "",
                            value=float(r.get("value") or 0),
                            target_value=float(r.get("target_value") or 0),
                            target_sd=float(r.get("target_sd") or 0),
                            cv=cv,
                            cv_max_threshold=cv_max_threshold,
                            status=status,
                            equipment=r.get("equipment_name") or "",
                            analyst=r.get("analyst_name") or "",
                            westgard_violations=[],
                            reference_id=reference_id,
                            needs_calibration=needs_calibration,
                            post_calibration_id=r.get("post_calibration_id") or ""
                        )
                    )

                self.qc_records = records
                self.qc_records = sorted(self.qc_records, key=lambda x: x.date, reverse=True)
                logger.info(f"Carregados {len(self.qc_records)} registros de QC do banco")

            # Carregar lotes de reagentes
            try:
                db_lots = await ReagentService.get_lots()
                today = datetime.now().date()
                lots = []
                for r in db_lots:
                    expiry_str = r.get("expiry_date") or ""
                    days_left = 0
                    if expiry_str:
                        try:
                            expiry_dt = datetime.strptime(expiry_str, "%Y-%m-%d").date()
                            days_left = (expiry_dt - today).days
                        except ValueError:
                            pass
                    lots.append(ReagentLot(
                        id=str(r.get("id") or ""),
                        name=r.get("name") or "",
                        lot_number=r.get("lot_number") or "",
                        expiry_date=expiry_str,
                        quantity=r.get("quantity") or "",
                        manufacturer=r.get("manufacturer") or "",
                        storage_temp=r.get("storage_temp") or "",
                        current_stock=float(r.get("current_stock") or 0),
                        estimated_consumption=float(r.get("estimated_consumption") or 0),
                        created_at=str(r.get("created_at") or ""),
                        days_left=days_left,
                    ))
                self.reagent_lots = lots
                logger.info(f"Carregados {len(self.reagent_lots)} lotes de reagentes")
            except Exception as e:
                logger.error(f"Erro ao carregar reagentes: {e}")

            # Carregar registros de manutenção
            try:
                db_maint = await MaintenanceService.get_records()
                self.maintenance_records = [
                    MaintenanceRecord(
                        id=str(r.get("id") or ""),
                        equipment=r.get("equipment") or "",
                        type=r.get("type") or "",
                        date=r.get("date") or "",
                        next_date=r.get("next_date") or "",
                        technician=r.get("technician") or "",
                        notes=r.get("notes") or "",
                        created_at=str(r.get("created_at") or "")
                    )
                    for r in db_maint
                ]
                logger.info(f"Carregados {len(self.maintenance_records)} registros de manutenção")
            except Exception as e:
                logger.error(f"Erro ao carregar manutenções: {e}")

            # Carregar registros de pós-calibração
            try:
                db_postcal = await PostCalibrationService.get_records()
                self.post_calibration_records = [
                    PostCalibrationRecord(
                        id=str(r.get("id") or ""),
                        qc_record_id=str(r.get("qc_record_id") or ""),
                        date=r.get("date") or "",
                        exam_name=r.get("exam_name") or "",
                        original_value=float(r.get("original_value") or 0),
                        original_cv=float(r.get("original_cv") or 0),
                        post_calibration_value=float(r.get("post_calibration_value") or 0),
                        post_calibration_cv=float(r.get("post_calibration_cv") or 0),
                        target_value=float(r.get("target_value") or 0),
                        analyst=r.get("analyst") or "",
                        notes=r.get("notes") or "",
                        created_at=str(r.get("created_at") or "")
                    )
                    for r in db_postcal
                ]
                logger.info(f"Carregados {len(self.post_calibration_records)} registros de pós-calibração")
            except Exception as e:
                logger.error(f"Erro ao carregar pós-calibrações: {e}")

            self._last_loaded = datetime.now().isoformat()

        except Exception as e:
            logger.error(f"Erro ao carregar dados do banco: {e}")
        finally:
            self.is_loading_data = False

    async def handle_proin_upload(self, files: List[rx.UploadFile]):
        """Handle upload of ProIn Excel file"""
        await _import_ops.handle_proin_upload(self, files)

    async def process_proin_import(self):
        """Process the imported data and save to DB"""
        await _import_ops.process_proin_import(self)

    def clear_proin_import(self):
        """Clear import state"""
        _import_ops.clear_proin_import(self)

    async def save_reagent_lot(self):
        """Salva um novo lote de reagente no Supabase"""
        await _reagent_ops.save_reagent_lot(self)

    async def delete_reagent_lot(self, id: str):
        """Deleta lote de reagente do Supabase"""
        await _reagent_ops.delete_reagent_lot(self, id)

    async def save_maintenance_record(self):
        """Registra manutenção no Supabase"""
        await _maintenance_ops.save_maintenance_record(self)

    # Lógica de cálculo SD/CV para formulário
    def calculate_sd(self):
        """Calcula o Desvio Padrão (Diferença Absoluta) automaticamente"""
        try:
            if not self.qc_value or not self.qc_target_value:
                return
            
            value = parse_decimal(self.qc_value)
            target = parse_decimal(self.qc_target_value)

            if value == 0 and not self.qc_value.strip():
                return
            if target == 0 and not self.qc_target_value.strip():
                return
            
            sd = abs(value - target)
            self.qc_target_sd = f"{sd:.2f}"
            
        except Exception:
            pass

    def update_qc_value(self, value: str):
        """Atualiza valor da medição e recalcula SD automaticamente"""
        self.qc_value = value
        self.calculate_sd()  # Calcula SD automaticamente
        
    def update_qc_target_value(self, value: str):
        """Atualiza valor alvo e recalcula SD automaticamente"""
        self.qc_target_value = value
        self.calculate_sd()  # Calcula SD automaticamente

    # Levey-Jennings Utils
    @rx.var
    def levey_jennings_chart_data(self) -> List[Dict[str, Any]]:
         # Se levey_jennings_data já forem dicts, retornar direto
         # Compatibility wrapper for existing charts components expecting dicts
         if self.levey_jennings_data and not isinstance(self.levey_jennings_data[0], dict):
             return [
                {
                    "date": point.date,
                    "value": point.value,
                    "target": point.target,
                    "sd": point.sd,
                    "cv": point.cv 
                } for point in self.levey_jennings_data
             ]
         return self.levey_jennings_data

    def set_levey_jennings_exam(self, val): self.levey_jennings_exam = val
    def set_levey_jennings_level(self, val): self.levey_jennings_level = val
    def set_levey_jennings_period(self, val): self.levey_jennings_period = val
    
    async def update_levey_jennings_data(self):
        """Atualiza dados do gráfico LJ com filtro de período"""
        if not self.levey_jennings_exam: return

        filtered = [r for r in self.qc_records if r.exam_name == self.levey_jennings_exam]

        # Aplicar filtro de nível
        if self.levey_jennings_level and self.levey_jennings_level != "Todos":
            filtered = [r for r in filtered if r.level == self.levey_jennings_level]

        # Aplicar filtro de período (dias)
        try:
            period_days = int(self.levey_jennings_period or 30)
            cutoff_date = (datetime.now() - timedelta(days=period_days)).isoformat()
            filtered = [r for r in filtered if r.date >= cutoff_date]
        except (ValueError, TypeError):
            pass

        # Ordenar por data crescente (mais antigo primeiro) para o gráfico mostrar progressão temporal
        filtered = sorted(filtered, key=lambda x: x.date, reverse=False)

        self.levey_jennings_data = [
            LeveyJenningsPoint(
                date=r.date[:10],
                value=r.value,
                target=r.target_value,
                sd=r.target_sd,
                cv=r.cv
            ) for r in filtered
        ]

    # QC CRUD Actions
    async def save_qc_record(self):
        self.is_saving_qc = True
        self.reset_qc_messages()
        try:
             # === Validação de campos obrigatórios ===
             if not (self.qc_exam_name or "").strip():
                 self.qc_error_message = "Selecione um exame."
                 self.is_saving_qc = False
                 return

             if not (self.qc_value or "").strip():
                 self.qc_error_message = "Informe o valor da medição."
                 self.is_saving_qc = False
                 return

             if not (self.qc_target_value or "").strip():
                 self.qc_error_message = "Informe o valor alvo."
                 self.is_saving_qc = False
                 return

             # Validação numérica
             try:
                 float(self.qc_value.strip().replace(",", "."))
             except (ValueError, TypeError):
                 self.qc_error_message = "Medição deve ser um valor numérico válido."
                 self.is_saving_qc = False
                 return

             try:
                 float(self.qc_target_value.strip().replace(",", "."))
             except (ValueError, TypeError):
                 self.qc_error_message = "Valor alvo deve ser um valor numérico válido."
                 self.is_saving_qc = False
                 return

             # Normalizar nome do exame antes de salvar
             canonical_name = self.qc_exam_name.strip()
             
             # Prepare history for Westgard check (Filter by same exam)
             # Assuming self.qc_records is sorted by date descending
             history = [r for r in self.qc_records if r.exam_name == canonical_name]
             
             # Valores Numéricos
             val = float(self.qc_value or 0)
             target = float(self.qc_target_value or 0)
             sd_target = float(self.qc_target_sd or 0)
             
             # Calcular CV
             cv = 0.0
             if target > 0:
                 diff = abs(val - target)
                 cv = (diff / target) * 100

             # Obter ID da referência se houver
             reference_id = ""
             if self.current_exam_reference:
                 reference_id = self.current_exam_reference.get("id", "")
                 cv_max_threshold = float(self.current_exam_reference.get("cv_max_threshold", 10.0))
             else:
                 cv_max_threshold = 10.0

             new_record = QCRecord(
                 id=str(len(self.qc_records) + 1),
                 date=self.qc_date or datetime.now().strftime("%Y-%m-%d"),
                 exam_name=canonical_name,
                 level=self.qc_level,
                 lot_number=self.qc_lot_number,
                 value=val,
                 target_value=target,
                 target_sd=sd_target,
                 cv=cv,
                 cv_max_threshold=cv_max_threshold,
                 status="OK",
                 westgard_violations=[],
                 reference_id=reference_id,
                 needs_calibration=False,
                 post_calibration_id=""
             )
             
             # Validação Westgard
             violations = WestgardService.check_rules(new_record, history)
             
             _toast_msg = ""
             _toast_level = "success"

             if violations:
                 new_record.westgard_violations = violations
                 # Determine status severity
                 rejections = [v for v in violations if v["severity"] == "rejection"]
                 warnings = [v for v in violations if v["severity"] == "warning"]

                 if rejections:
                     rule = rejections[0]['rule']
                     new_record.status = f"ERRO ({rule})"
                     new_record.needs_calibration = True
                     self.qc_error_message = f"Regra {rule} violada: {rejections[0]['description']}"
                     self.qc_success_message = ""
                     _toast_msg = f"⚠ Regra {rule} violada!"
                     _toast_level = "error"
                 elif warnings:
                     rule = warnings[0]['rule']
                     new_record.status = f"ALERTA ({rule})"
                     self.qc_warning_message = f"Salvo com Alerta ({rule}): {warnings[0]['description']}"
                     self.qc_success_message = ""
                     _toast_msg = f"Salvo com alerta ({rule})"
                     _toast_level = "warning"
                 else:
                     new_record.status = "OK"
             else:
                 self.qc_success_message = "Registro salvo! Sem violações de regras."
                 self.qc_error_message = ""
                 self.qc_warning_message = ""
                 _toast_msg = "Registro salvo com sucesso!"
                 _toast_level = "success"

             # Aplicar regra de CV% para calibração e status
             cv_out = cv > cv_max_threshold
             if cv_out:
                 new_record.needs_calibration = True
                 if new_record.status == "OK":
                     new_record.status = "ALERTA (CV)"
                 if not self.qc_error_message and not self.qc_warning_message:
                     self.qc_warning_message = "CV acima do limite. Calibração necessária."
                     self.qc_success_message = ""
                     _toast_msg = "CV acima do limite. Calibração necessária."
                     _toast_level = "warning"

             # Persistir no banco de dados
             db_saved = False
             try:
                 db_record = await QCService.create_qc_record({
                     "date": new_record.date,
                     "exam_name": new_record.exam_name,
                     "level": new_record.level,
                     "lot_number": new_record.lot_number,
                     "value": new_record.value,
                     "target_value": new_record.target_value,
                     "target_sd": new_record.target_sd,
                     "equipment": self.qc_equipment,
                     "analyst": self.qc_analyst,
                     "cv": new_record.cv,
                     "status": new_record.status,
                     "reference_id": new_record.reference_id,
                     "needs_calibration": new_record.needs_calibration
                 })
                 # Atualizar ID com o ID do banco
                 if db_record and db_record.get("id"):
                     new_record = QCRecord(
                         id=str(db_record.get("id")),
                         date=new_record.date,
                         exam_name=new_record.exam_name,
                         level=new_record.level,
                         lot_number=new_record.lot_number,
                         value=new_record.value,
                         target_value=new_record.target_value,
                         target_sd=new_record.target_sd,
                         cv=new_record.cv,
                         cv_max_threshold=new_record.cv_max_threshold,
                         status=new_record.status,
                         westgard_violations=new_record.westgard_violations,
                         reference_id=new_record.reference_id,
                         needs_calibration=new_record.needs_calibration,
                         post_calibration_id=""
                     )
                     db_saved = True
             except Exception as db_error:
                 logger.error(f"Erro ao salvar no banco: {db_error}")
                 self.qc_error_message = f"Erro ao salvar no banco: {db_error}"

             # Only append to local state if DB save succeeded
             if db_saved:
                 self.qc_records.append(new_record)
                 self.qc_records = sorted(self.qc_records, key=lambda x: x.date, reverse=True)

             self.qc_value = ""
             self.is_saving_qc = False

             # Toast notification
             if _toast_level == "success":
                 yield rx.toast.success(_toast_msg, duration=4000, position="bottom-right")
             elif _toast_level == "warning":
                 yield rx.toast.warning(_toast_msg, duration=6000, position="bottom-right")
             elif _toast_level == "error":
                 yield rx.toast.error(_toast_msg, duration=8000, position="bottom-right")
             return

        except Exception as e:
            self.qc_error_message = f"Erro: {e}"
            self.is_saving_qc = False
            yield rx.toast.error(f"Erro ao salvar: {e}", duration=8000, position="bottom-right")

    async def delete_qc_record(self, id: str):
        # Deletar do banco de dados
        try:
            await QCService.delete_qc_record(id)
        except Exception as e:
            logger.error(f"Erro ao deletar do banco: {e}")
        # Remover da lista local
        self.qc_records = [r for r in self.qc_records if r.id != id]

    def open_clear_all_modal(self):
        """Abre modal de confirmação para limpar todos os registros"""
        self.show_clear_all_modal = True

    def close_clear_all_modal(self):
        """Fecha modal de confirmação"""
        self.show_clear_all_modal = False

    async def confirm_clear_all_qc_records(self):
        """Confirma e executa limpeza de todos os registros"""
        self.show_clear_all_modal = False
        errors = 0
        for record in self.qc_records:
            try:
                await QCService.delete_qc_record(record.id)
            except Exception as e:
                logger.error(f"Erro ao deletar registro {record.id}: {e}")
                errors += 1
        self.qc_records = []
        if errors > 0:
            self.qc_warning_message = f"Histórico limpo, mas {errors} registros falharam ao ser removidos do banco."
        else:
            self.qc_success_message = "Todos os registros foram removidos."

    def clear_qc_form(self):
        """Limpa o formulário de registro de CQ"""
        self.qc_value = ""
        self.qc_date = datetime.now().strftime("%Y-%m-%d")
        self.reset_qc_messages()
        
    def reset_qc_messages(self):
        self.qc_success_message = ""
        self.qc_warning_message = ""
        self.qc_error_message = ""

    # === Handlers para Valores de Referência ===

    async def on_exam_selected(self, exam_name: str):
        """
        Ao selecionar um exame, busca automaticamente a referência ativa
        e preenche o valor-alvo no formulário.
        """
        self.qc_exam_name = exam_name

        # Buscar referência ativa para este exame
        try:
            ref = await QCReferenceService.get_active_reference_for_exam(
                exam_name=exam_name,
                level=self.qc_level
            )

            if ref:
                self.current_exam_reference = ref
                self.qc_target_value = str(ref.get("target_value", ""))
            else:
                self.current_exam_reference = None
        except Exception as e:
            logger.error(f"Erro ao buscar referência: {e}")
            self.current_exam_reference = None

    async def load_qc_references(self):
        """Carrega todos os valores de referência ativos"""
        await _reference_ops.load_qc_references(self)

    async def save_qc_reference(self):
        """Salva novo registro de valor referencial"""
        await _reference_ops.save_qc_reference(self)

    async def deactivate_qc_reference(self, id: str):
        """Desativa uma referência"""
        await _reference_ops.deactivate_qc_reference(self, id)

    # === Métodos de Exclusão Permanente com Confirmação ===

    def open_delete_qc_record_modal(self, record_id: str, exam_name: str):
        """Abre modal de confirmação para excluir registro de CQ"""
        self.delete_qc_record_id = record_id
        self.delete_qc_record_name = exam_name
        self.show_delete_qc_record_modal = True

    def close_delete_qc_record_modal(self):
        """Fecha modal de confirmação de exclusão de registro CQ"""
        self.show_delete_qc_record_modal = False
        self.delete_qc_record_id = ""
        self.delete_qc_record_name = ""

    async def confirm_delete_qc_record(self):
        """Exclui registro de CQ com opção de restaurar"""
        if not self.delete_qc_record_id:
            return

        # Guardar registro para possível restauração
        deleted_record = next((r for r in self.qc_records if r.id == self.delete_qc_record_id), None)
        if deleted_record:
            self.last_deleted_qc_record = deleted_record.dict()

        try:
            success = await QCService.delete_qc_record(self.delete_qc_record_id)
            if success:
                self.qc_records = [r for r in self.qc_records if r.id != self.delete_qc_record_id]
                self.close_delete_qc_record_modal()
                yield rx.toast.info("Registro excluído. Use 'Desfazer' para restaurar.", duration=8000, position="bottom-right")
                return
            else:
                self.qc_error_message = "Erro ao excluir registro do banco de dados"
                self.last_deleted_qc_record = None
        except Exception as e:
            self.qc_error_message = f"Erro ao excluir: {e}"
            self.last_deleted_qc_record = None
        self.close_delete_qc_record_modal()

    async def restore_last_deleted_qc_record(self):
        """Restaura o último registro excluído re-inserindo no banco"""
        if not self.last_deleted_qc_record:
            return
        try:
            record_data = self.last_deleted_qc_record
            db_record = await QCService.create_qc_record({
                "date": record_data.get("date", ""),
                "exam_name": record_data.get("exam_name", ""),
                "level": record_data.get("level", "Normal"),
                "lot_number": record_data.get("lot_number", ""),
                "value": record_data.get("value", 0),
                "target_value": record_data.get("target_value", 0),
                "target_sd": record_data.get("target_sd", 0),
                "equipment": record_data.get("equipment", ""),
                "analyst": record_data.get("analyst", ""),
                "cv": record_data.get("cv", 0),
                "status": record_data.get("status", "OK"),
                "reference_id": record_data.get("reference_id", ""),
                "needs_calibration": record_data.get("needs_calibration", False),
            })
            if db_record and db_record.get("id"):
                restored = QCRecord(
                    id=str(db_record.get("id")),
                    date=record_data.get("date", ""),
                    exam_name=record_data.get("exam_name", ""),
                    level=record_data.get("level", "Normal"),
                    lot_number=record_data.get("lot_number", ""),
                    value=float(record_data.get("value", 0)),
                    target_value=float(record_data.get("target_value", 0)),
                    target_sd=float(record_data.get("target_sd", 0)),
                    cv=float(record_data.get("cv", 0)),
                    cv_max_threshold=float(record_data.get("cv_max_threshold", 10.0)),
                    status=record_data.get("status", "OK"),
                    westgard_violations=[],
                    reference_id=record_data.get("reference_id", ""),
                    needs_calibration=record_data.get("needs_calibration", False),
                    post_calibration_id=record_data.get("post_calibration_id", ""),
                )
                self.qc_records.append(restored)
                self.qc_records = sorted(self.qc_records, key=lambda x: x.date, reverse=True)
            self.last_deleted_qc_record = None
            yield rx.toast.success("Registro restaurado!", duration=3000, position="bottom-right")
        except Exception as e:
            logger.error(f"Erro ao restaurar registro: {e}")
            self.last_deleted_qc_record = None
            yield rx.toast.error(f"Erro ao restaurar: {e}", duration=5000, position="bottom-right")

    def dismiss_undo_delete(self):
        """Descarta a opção de desfazer exclusão"""
        self.last_deleted_qc_record = None

    def open_delete_reference_modal(self, ref_id: str, ref_name: str):
        """Abre modal de confirmação para excluir referência"""
        _reference_ops.open_delete_reference_modal(self, ref_id, ref_name)

    def close_delete_reference_modal(self):
        """Fecha modal de confirmação de exclusão de referência"""
        _reference_ops.close_delete_reference_modal(self)

    async def confirm_delete_reference(self):
        """Confirma e executa exclusão permanente da referência"""
        await _reference_ops.confirm_delete_reference(self)

    # Setters para formulário de referência
    def set_ref_name(self, value: str):
        self.ref_name = value

    def set_ref_exam_name(self, value: str):
        self.ref_exam_name = value

    def set_ref_valid_from(self, value: str):
        self.ref_valid_from = value

    def set_ref_valid_until(self, value: str):
        self.ref_valid_until = value

    def set_ref_target_value(self, value: str):
        self.ref_target_value = value

    def set_ref_cv_max_threshold(self, value: str):
        self.ref_cv_max_threshold = value

    def set_ref_lot_number(self, value: str):
        self.ref_lot_number = value

    def set_ref_manufacturer(self, value: str):
        self.ref_manufacturer = value

    def set_ref_level(self, value: str):
        self.ref_level = value

    def set_ref_notes(self, value: str):
        self.ref_notes = value

    # === Handlers Pós-Calibração ===

    def open_post_calibration_modal(self, record_id: str):
        """Abre o modal de pós-calibração para o registro selecionado"""
        _post_calibration_ops.open_post_calibration_modal(self, record_id)

    def close_post_calibration_modal(self):
        """Fecha o modal de pós-calibração"""
        _post_calibration_ops.close_post_calibration_modal(self)

    def set_post_cal_value(self, value: str):
        self.post_cal_value = value

    def set_post_cal_analyst(self, value: str):
        self.post_cal_analyst = value

    def set_post_cal_notes(self, value: str):
        self.post_cal_notes = value

    @rx.var
    def post_cal_calculated_cv(self) -> float:
        """Calcula CV% da medição pós-calibração"""
        try:
            if not self.selected_qc_record_for_calibration:
                return 0.0
            val = float(self.post_cal_value or 0)
            target = float(self.selected_qc_record_for_calibration.get("target_value", 0))
            if target == 0:
                return 0.0
            diff = abs(val - target)
            return round((diff / target) * 100, 2)
        except (ValueError, TypeError):
            return 0.0

    async def save_post_calibration(self):
        """Salva o registro de medição pós-calibração no Supabase"""
        await _post_calibration_ops.save_post_calibration(self)

    @rx.var
    def has_post_calibration_records(self) -> bool:
        """Verifica se há registros de pós-calibração"""
        return len(self.post_calibration_records) > 0

    @rx.var
    def calibration_history_for_selected(self) -> List[PostCalibrationRecord]:
        """Histórico de pós-calibrações do exame selecionado no modal"""
        if not self.selected_qc_record_for_calibration:
            return []
        exam = self.selected_qc_record_for_calibration.get("exam_name", "")
        if not exam:
            return []
        return [r for r in self.post_calibration_records if r.exam_name == exam]

    def get_post_calibration_for_record(self, qc_record_id: str) -> Optional[PostCalibrationRecord]:
        """Retorna o registro de pós-calibração para um QC record específico"""
        return next((r for r in self.post_calibration_records if r.qc_record_id == qc_record_id), None)

    async def update_qc_preview(self):
        """Gera o preview do PDF QC sem baixar"""
        self.is_generating_qc_report = True
        yield
        try:
            pdf_bytes, filename = await self._generate_pdf_bytes()
            if pdf_bytes:
                self.qc_pdf_preview = base64.b64encode(pdf_bytes).decode('utf-8')
                self.qc_error_message = ""
        except Exception as e:
            self.qc_error_message = f"Erro ao gerar preview: {str(e)}"
        finally:
            self.is_generating_qc_report = False

    async def _generate_pdf_bytes(self):
        """Helper para gerar bytes do PDF"""
        return await _report_ops.generate_pdf_bytes(self)

    async def regenerate_qc_report_pdf(self):
        """Recarrega dados do banco e gera novo PDF"""
        self.is_generating_qc_report = True
        self.qc_error_message = ""
        yield

        try:
            await self.load_data_from_db(force=True)
            pdf_bytes, filename = await self._generate_pdf_bytes()

            if pdf_bytes:
                logger.info(f"PDF regenerado: {len(pdf_bytes)} bytes, filename={filename}")
                b64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
                self.qc_pdf_preview = b64_pdf
                self.is_generating_qc_report = False

                yield rx.download(data=pdf_bytes, filename=filename)
            else:
                logger.warning("PDF regeneration retornou bytes vazios")
                self.qc_error_message = "Erro: PDF não foi gerado"
                self.is_generating_qc_report = False

        except Exception as e:
            logger.error(f"Erro ao regenerar PDF QC: {e}", exc_info=True)
            self.qc_error_message = f"Erro na geração do PDF: {str(e)}"
            self.is_generating_qc_report = False

    async def generate_qc_report_pdf(self):
        """Gera PDF das tabelas de QC e inicia download"""
        self.is_generating_qc_report = True
        yield

        try:
            pdf_bytes, filename = await self._generate_pdf_bytes()

            if pdf_bytes:
                logger.info(f"PDF gerado: {len(pdf_bytes)} bytes, filename={filename}")
                b64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
                self.qc_pdf_preview = b64_pdf
                self.is_generating_qc_report = False

                # Usar bytes diretamente ao invés de data URI
                yield rx.download(data=pdf_bytes, filename=filename)
            else:
                logger.warning("PDF generation retornou bytes vazios")
                self.qc_error_message = "Erro: PDF não foi gerado"
                self.is_generating_qc_report = False

        except Exception as e:
            logger.error(f"Erro ao gerar PDF QC: {e}", exc_info=True)
            self.qc_error_message = f"Erro na geração do PDF: {str(e)}"
            self.is_generating_qc_report = False

    async def generate_area_report_pdf(self, area: str):
        """Gera PDF de relatório para uma área laboratorial específica"""
        try:
            from ..utils.qc_pdf_report import generate_area_pdf
            area_name_map = {
                "hematologia": "Hematologia",
                "imunologia": "Imunologia",
                "parasitologia": "Parasitologia",
                "microbiologia": "Microbiologia",
                "uroanalise": "Uroanálise",
            }
            area_label = area_name_map.get(area, area.capitalize())
            records = []
            bio_records = []
            if area == "imunologia":
                records = [r.dict() for r in self.imuno_records]
            elif area == "hematologia":
                records = [m.dict() for m in self.hqc_measurements]
                bio_records = [r.dict() for r in self.hemato_bio_records]

            loop = asyncio.get_event_loop()
            pdf_bytes = await loop.run_in_executor(
                None,
                lambda: generate_area_pdf(area, area_label, records, bio_records=bio_records)
            )
            filename = f"Relatorio_{area_label}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
            yield rx.download(data=pdf_bytes, filename=filename)
        except Exception as e:
            logger.error(f"Erro ao gerar PDF da área {area}: {e}", exc_info=True)
            yield rx.toast.error(f"Erro ao gerar PDF: {e}", duration=6000, position="bottom-right")

    async def export_qc_csv(self):
        """Exporta registros de QC como CSV para download"""
        if not self.qc_records:
            self.qc_error_message = "Nenhum registro para exportar."
            return
        csv_content = _report_ops.build_csv_content(self)
        csv_bytes = csv_content.encode("utf-8-sig")
        filename = f"QC_Export_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
        yield rx.download(data=csv_bytes, filename=filename)

    async def delete_maintenance_record(self, record_id: str):
        """Deleta registro de manutenção do Supabase"""
        await _maintenance_ops.delete_maintenance_record(self, record_id)

    # ===== Voice-to-Form Handlers =====

    def open_voice_modal(self, form_type: str):
        """Abre modal de gravacao de voz para o formulario especificado"""
        _voice_ops.open_voice_modal(self, form_type)

    def close_voice_modal(self):
        """Fecha modal de voz e limpa estado"""
        _voice_ops.close_voice_modal(self)

    def set_voice_recording(self, is_recording: bool):
        """Chamado pelo JS callback quando gravacao inicia/para"""
        _voice_ops.set_voice_recording(self, is_recording)

    def receive_voice_audio(self, audio_base64: str):
        """Recebe audio base64 do JS MediaRecorder callback"""
        _voice_ops.receive_voice_audio(self, audio_base64)
        return QCState.process_voice_audio

    async def process_voice_audio(self):
        """Envia audio ao Gemini e preenche campos do formulario"""
        if not self.voice_audio_base64:
            self.voice_error_message = "Nenhum audio capturado. Tente novamente."
            return
        self.voice_is_processing = True
        self.voice_status_message = "Analisando audio com IA..."
        self.voice_error_message = ""
        yield
        success = await _voice_ops.process_voice_audio(self)
        if success:
            yield
            await asyncio.sleep(1.2)
            _voice_ops.close_voice_modal(self)

    def _apply_voice_data(self, data: Dict[str, Any]):
        """Aplica dados extraidos pelo Gemini nos campos do formulario correto"""
        _voice_ops.apply_voice_data(self, data)

    # === Hematologia Handlers ===

    def clear_hemato_form(self):
        """Limpa o formulário de Hematologia"""
        self.hemato_bio_hemacias = ""
        self.hemato_bio_hematocrito = ""
        self.hemato_bio_hemoglobina = ""
        self.hemato_bio_leucocitos = ""
        self.hemato_bio_plaquetas = ""
        self.hemato_bio_rdw = ""
        self.hemato_bio_vpm = ""
        self.hemato_bio_registro = ""
        self.hemato_bio_data = ""
        self.hemato_pad_hemacias = ""
        self.hemato_pad_hematocrito = ""
        self.hemato_pad_hemoglobina = ""
        self.hemato_pad_leucocitos = ""
        self.hemato_pad_plaquetas = ""
        self.hemato_pad_rdw = ""
        self.hemato_pad_vpm = ""
        self.hemato_pad_registro = ""
        self.hemato_pad_data = ""
        self.hemato_ci_mode = "bio"
        self.hemato_ci_min_hemacias = ""
        self.hemato_ci_max_hemacias = ""
        self.hemato_ci_min_hematocrito = ""
        self.hemato_ci_max_hematocrito = ""
        self.hemato_ci_min_hemoglobina = ""
        self.hemato_ci_max_hemoglobina = ""
        self.hemato_ci_min_leucocitos = ""
        self.hemato_ci_max_leucocitos = ""
        self.hemato_ci_min_plaquetas = ""
        self.hemato_ci_max_plaquetas = ""
        self.hemato_ci_min_rdw = ""
        self.hemato_ci_max_rdw = ""
        self.hemato_ci_min_vpm = ""
        self.hemato_ci_max_vpm = ""
        self.hemato_ci_pct_hemacias = ""
        self.hemato_ci_pct_hematocrito = ""
        self.hemato_ci_pct_hemoglobina = ""
        self.hemato_ci_pct_leucocitos = ""
        self.hemato_ci_pct_plaquetas = ""
        self.hemato_ci_pct_rdw = ""
        self.hemato_ci_pct_vpm = ""
        self.hemato_success_message = ""
        self.hemato_error_message = ""

    async def save_hemato_record(self):
        """Salva registro de Hematologia no banco de dados"""
        # Validação mínima: ao menos um campo preenchido
        has_bio = any([
            self.hemato_bio_hemacias, self.hemato_bio_hematocrito,
            self.hemato_bio_hemoglobina, self.hemato_bio_leucocitos,
            self.hemato_bio_plaquetas, self.hemato_bio_rdw, self.hemato_bio_vpm,
        ])
        has_pad = any([
            self.hemato_pad_hemacias, self.hemato_pad_hematocrito,
            self.hemato_pad_hemoglobina, self.hemato_pad_leucocitos,
            self.hemato_pad_plaquetas, self.hemato_pad_rdw, self.hemato_pad_vpm,
        ])
        has_ci = any([
            self.hemato_ci_min_hemacias, self.hemato_ci_max_hemacias,
            self.hemato_ci_min_hematocrito, self.hemato_ci_max_hematocrito,
            self.hemato_ci_min_hemoglobina, self.hemato_ci_max_hemoglobina,
            self.hemato_ci_min_leucocitos, self.hemato_ci_max_leucocitos,
            self.hemato_ci_min_plaquetas, self.hemato_ci_max_plaquetas,
            self.hemato_ci_min_rdw, self.hemato_ci_max_rdw,
            self.hemato_ci_min_vpm, self.hemato_ci_max_vpm,
            self.hemato_ci_pct_hemacias, self.hemato_ci_pct_hematocrito,
            self.hemato_ci_pct_hemoglobina, self.hemato_ci_pct_leucocitos,
            self.hemato_ci_pct_plaquetas, self.hemato_ci_pct_rdw,
            self.hemato_ci_pct_vpm,
        ])
        if not has_bio and not has_pad and not has_ci:
            self.hemato_error_message = "Preencha ao menos um valor antes de salvar."
            self.hemato_success_message = ""
            yield rx.toast.error("Preencha ao menos um valor.", duration=4000, position="bottom-right")
            return

        self.is_saving_hemato = True
        self.hemato_error_message = ""
        self.hemato_success_message = ""

        def _safe_float(val: str) -> Optional[float]:
            try:
                v = float(val.replace(",", ".")) if val.strip() else None
                return v
            except (ValueError, TypeError, AttributeError):
                return None

        try:
            data_bio = self.hemato_bio_data or datetime.now().strftime("%Y-%m-%d")
            data = {
                "data_bio": data_bio,
                "data_pad": self.hemato_pad_data or None,
                "registro_bio": self.hemato_bio_registro.strip() or None,
                "registro_pad": self.hemato_pad_registro.strip() or None,
                "modo_ci": self.hemato_ci_mode,
                "bio_hemacias": _safe_float(self.hemato_bio_hemacias),
                "bio_hematocrito": _safe_float(self.hemato_bio_hematocrito),
                "bio_hemoglobina": _safe_float(self.hemato_bio_hemoglobina),
                "bio_leucocitos": _safe_float(self.hemato_bio_leucocitos),
                "bio_plaquetas": _safe_float(self.hemato_bio_plaquetas),
                "bio_rdw": _safe_float(self.hemato_bio_rdw),
                "bio_vpm": _safe_float(self.hemato_bio_vpm),
            }

            # Campos CI dependendo do modo
            if self.hemato_ci_mode == "bio":
                data.update({
                    "pad_hemacias": _safe_float(self.hemato_pad_hemacias),
                    "pad_hematocrito": _safe_float(self.hemato_pad_hematocrito),
                    "pad_hemoglobina": _safe_float(self.hemato_pad_hemoglobina),
                    "pad_leucocitos": _safe_float(self.hemato_pad_leucocitos),
                    "pad_plaquetas": _safe_float(self.hemato_pad_plaquetas),
                    "pad_rdw": _safe_float(self.hemato_pad_rdw),
                    "pad_vpm": _safe_float(self.hemato_pad_vpm),
                })
            elif self.hemato_ci_mode == "intervalo":
                data.update({
                    "ci_min_hemacias": _safe_float(self.hemato_ci_min_hemacias),
                    "ci_max_hemacias": _safe_float(self.hemato_ci_max_hemacias),
                    "ci_min_hematocrito": _safe_float(self.hemato_ci_min_hematocrito),
                    "ci_max_hematocrito": _safe_float(self.hemato_ci_max_hematocrito),
                    "ci_min_hemoglobina": _safe_float(self.hemato_ci_min_hemoglobina),
                    "ci_max_hemoglobina": _safe_float(self.hemato_ci_max_hemoglobina),
                    "ci_min_leucocitos": _safe_float(self.hemato_ci_min_leucocitos),
                    "ci_max_leucocitos": _safe_float(self.hemato_ci_max_leucocitos),
                    "ci_min_plaquetas": _safe_float(self.hemato_ci_min_plaquetas),
                    "ci_max_plaquetas": _safe_float(self.hemato_ci_max_plaquetas),
                    "ci_min_rdw": _safe_float(self.hemato_ci_min_rdw),
                    "ci_max_rdw": _safe_float(self.hemato_ci_max_rdw),
                    "ci_min_vpm": _safe_float(self.hemato_ci_min_vpm),
                    "ci_max_vpm": _safe_float(self.hemato_ci_max_vpm),
                })
            else:  # porcentagem
                data.update({
                    "ci_pct_hemacias": _safe_float(self.hemato_ci_pct_hemacias),
                    "ci_pct_hematocrito": _safe_float(self.hemato_ci_pct_hematocrito),
                    "ci_pct_hemoglobina": _safe_float(self.hemato_ci_pct_hemoglobina),
                    "ci_pct_leucocitos": _safe_float(self.hemato_ci_pct_leucocitos),
                    "ci_pct_plaquetas": _safe_float(self.hemato_ci_pct_plaquetas),
                    "ci_pct_rdw": _safe_float(self.hemato_ci_pct_rdw),
                    "ci_pct_vpm": _safe_float(self.hemato_ci_pct_vpm),
                })

            # Remover chaves com valor None
            data = {k: v for k, v in data.items() if v is not None}

            await HematologyQCService.save_bio_record(data)
            await self.load_hemato_bio_records()

            self.hemato_success_message = "Registro de Hematologia salvo com sucesso!"
            yield rx.toast.success("Registro de Hematologia salvo!", duration=4000, position="bottom-right")

        except Exception as e:
            logger.error(f"Erro ao salvar registro de hematologia: {e}")
            self.hemato_error_message = f"Erro ao salvar: {e}"
            yield rx.toast.error(f"Erro ao salvar: {e}", duration=6000, position="bottom-right")
        finally:
            self.is_saving_hemato = False

    async def load_hemato_bio_records(self):
        """Carrega registros Bio x CI do banco"""
        try:
            rows = await HematologyQCService.get_bio_records(limit=200)
            self.hemato_bio_records = [
                HematologyBioRecord(
                    id=str(r.get("id", "")),
                    data_bio=r.get("data_bio", "") or "",
                    data_pad=r.get("data_pad", "") or "",
                    registro_bio=r.get("registro_bio", "") or "",
                    registro_pad=r.get("registro_pad", "") or "",
                    modo_ci=r.get("modo_ci", "bio") or "bio",
                    bio_hemacias=float(r.get("bio_hemacias") or 0),
                    bio_hematocrito=float(r.get("bio_hematocrito") or 0),
                    bio_hemoglobina=float(r.get("bio_hemoglobina") or 0),
                    bio_leucocitos=float(r.get("bio_leucocitos") or 0),
                    bio_plaquetas=float(r.get("bio_plaquetas") or 0),
                    bio_rdw=float(r.get("bio_rdw") or 0),
                    bio_vpm=float(r.get("bio_vpm") or 0),
                    pad_hemacias=float(r.get("pad_hemacias") or 0),
                    pad_hematocrito=float(r.get("pad_hematocrito") or 0),
                    pad_hemoglobina=float(r.get("pad_hemoglobina") or 0),
                    pad_leucocitos=float(r.get("pad_leucocitos") or 0),
                    pad_plaquetas=float(r.get("pad_plaquetas") or 0),
                    pad_rdw=float(r.get("pad_rdw") or 0),
                    pad_vpm=float(r.get("pad_vpm") or 0),
                    ci_min_hemacias=float(r.get("ci_min_hemacias") or 0),
                    ci_max_hemacias=float(r.get("ci_max_hemacias") or 0),
                    ci_min_hematocrito=float(r.get("ci_min_hematocrito") or 0),
                    ci_max_hematocrito=float(r.get("ci_max_hematocrito") or 0),
                    ci_min_hemoglobina=float(r.get("ci_min_hemoglobina") or 0),
                    ci_max_hemoglobina=float(r.get("ci_max_hemoglobina") or 0),
                    ci_min_leucocitos=float(r.get("ci_min_leucocitos") or 0),
                    ci_max_leucocitos=float(r.get("ci_max_leucocitos") or 0),
                    ci_min_plaquetas=float(r.get("ci_min_plaquetas") or 0),
                    ci_max_plaquetas=float(r.get("ci_max_plaquetas") or 0),
                    ci_min_rdw=float(r.get("ci_min_rdw") or 0),
                    ci_max_rdw=float(r.get("ci_max_rdw") or 0),
                    ci_min_vpm=float(r.get("ci_min_vpm") or 0),
                    ci_max_vpm=float(r.get("ci_max_vpm") or 0),
                    ci_pct_hemacias=float(r.get("ci_pct_hemacias") or 0),
                    ci_pct_hematocrito=float(r.get("ci_pct_hematocrito") or 0),
                    ci_pct_hemoglobina=float(r.get("ci_pct_hemoglobina") or 0),
                    ci_pct_leucocitos=float(r.get("ci_pct_leucocitos") or 0),
                    ci_pct_plaquetas=float(r.get("ci_pct_plaquetas") or 0),
                    ci_pct_rdw=float(r.get("ci_pct_rdw") or 0),
                    ci_pct_vpm=float(r.get("ci_pct_vpm") or 0),
                    created_at=str(r.get("created_at", "")),
                ) for r in rows
            ]
            logger.info(f"Carregados {len(self.hemato_bio_records)} registros Bio x CI")
        except Exception as e:
            logger.error(f"Erro ao carregar registros Bio x CI: {e}")

    async def delete_hemato_bio_record(self, record_id: str):
        """Exclui registro Bio x CI"""
        try:
            await HematologyQCService.delete_bio_record(record_id)
            await self.load_hemato_bio_records()
            yield rx.toast.info("Registro removido.", duration=3000, position="bottom-right")
        except Exception as e:
            logger.error(f"Erro ao excluir registro Bio x CI: {e}")
            yield rx.toast.error(f"Erro ao excluir: {e}", duration=4000, position="bottom-right")

    def open_hemato_bio_detail(self, record_id: str):
        """Abre modal de detalhes de um registro Bio x CI"""
        for rec in self.hemato_bio_records:
            if rec.id == record_id:
                self.selected_hemato_bio_record = rec
                self.show_hemato_bio_detail = True
                return
        self.show_hemato_bio_detail = False

    def close_hemato_bio_detail(self):
        """Fecha modal de detalhes"""
        self.show_hemato_bio_detail = False

    # === Imunologia Handlers ===

    def set_imuno_controle(self, value: str):
        self.imuno_controle = value

    def set_imuno_fabricante(self, value: str):
        self.imuno_fabricante = value

    def set_imuno_lote(self, value: str):
        self.imuno_lote = value

    def set_imuno_data(self, value: str):
        self.imuno_data = value

    def set_imuno_resultado(self, value: str):
        self.imuno_resultado = value

    def set_imuno_search_term(self, value: str):
        self.imuno_search_term = value

    def set_imuno_history_date(self, value: str):
        self.imuno_history_date = value

    @rx.var
    def filtered_imuno_records(self) -> List[ImunologiaRecord]:
        """Registros de imunologia filtrados por busca e data"""
        records = self.imuno_records
        search = (self.imuno_search_term or "").strip().upper()
        if search:
            records = [r for r in records if search in (r.controle or "").upper() or search in (r.fabricante or "").upper()]
        target_date = (self.imuno_history_date or "").strip()
        if target_date:
            records = [r for r in records if (r.data or "")[:10] == target_date]
        return records

    def next_imuno_day(self):
        """Avança um dia no histórico de imunologia"""
        try:
            current = datetime.strptime(self.imuno_history_date, "%Y-%m-%d")
            self.imuno_history_date = (current + timedelta(days=1)).strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            self.imuno_history_date = datetime.now().strftime("%Y-%m-%d")

    def prev_imuno_day(self):
        """Retrocede um dia no histórico de imunologia"""
        try:
            current = datetime.strptime(self.imuno_history_date, "%Y-%m-%d")
            self.imuno_history_date = (current - timedelta(days=1)).strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            self.imuno_history_date = datetime.now().strftime("%Y-%m-%d")

    def clear_imuno_form(self):
        """Limpa o formulário de Imunologia"""
        self.imuno_controle = ""
        self.imuno_fabricante = ""
        self.imuno_lote = ""
        self.imuno_data = datetime.now().strftime("%Y-%m-%d")
        self.imuno_resultado = ""
        self.imuno_success_message = ""
        self.imuno_error_message = ""

    def save_imuno_record(self):
        """Salva registro de Imunologia (local) e exibe toast"""
        if not (self.imuno_controle or "").strip():
            self.imuno_error_message = "Informe o Controle."
            self.imuno_success_message = ""
            return rx.toast.error("Informe o Controle.", duration=4000, position="bottom-right")

        if not (self.imuno_resultado or "").strip():
            self.imuno_error_message = "Informe o Resultado."
            self.imuno_success_message = ""
            return rx.toast.error("Informe o Resultado.", duration=4000, position="bottom-right")

        record = ImunologiaRecord(
            id=str(len(self.imuno_records) + 1),
            controle=self.imuno_controle.strip(),
            fabricante=self.imuno_fabricante.strip(),
            lote=self.imuno_lote.strip(),
            data=self.imuno_data or datetime.now().strftime("%Y-%m-%d"),
            resultado=self.imuno_resultado.strip(),
            created_at=datetime.now().isoformat(),
        )
        self.imuno_records.append(record)
        self.imuno_records = sorted(self.imuno_records, key=lambda x: x.data, reverse=True)

        self.imuno_error_message = ""
        self.imuno_success_message = "Registro de Imunologia salvo com sucesso!"
        # Limpar campos do formulário (manter data)
        self.imuno_controle = ""
        self.imuno_fabricante = ""
        self.imuno_lote = ""
        self.imuno_resultado = ""
        return rx.toast.success("Registro de Imunologia salvo!", duration=4000, position="bottom-right")

    def delete_imuno_record(self, record_id: str):
        """Remove um registro de imunologia"""
        self.imuno_records = [r for r in self.imuno_records if r.id != record_id]
        return rx.toast.info("Registro removido.", duration=3000, position="bottom-right")

    # =====================================================================
    # === Hematologia CQ por Intervalo/% — Handlers ===
    # =====================================================================

    def set_hemato_qc_sub_tab(self, value: str):
        self.hemato_qc_sub_tab = value

    # ── Setters de parâmetro ──

    def set_hqc_param_analito(self, value: str):
        self.hqc_param_analito = value

    def set_hqc_param_modo(self, value: str):
        self.hqc_param_modo = value

    def set_hqc_param_alvo(self, value: str):
        self.hqc_param_alvo = value

    def set_hqc_param_min(self, value: str):
        self.hqc_param_min = value

    def set_hqc_param_max(self, value: str):
        self.hqc_param_max = value

    def set_hqc_param_tolerancia(self, value: str):
        self.hqc_param_tolerancia = value

    def set_hqc_param_equipamento(self, value: str):
        self.hqc_param_equipamento = value

    def set_hqc_param_lote(self, value: str):
        self.hqc_param_lote = value

    def set_hqc_param_nivel(self, value: str):
        self.hqc_param_nivel = value

    def set_hqc_show_inactive(self, value: bool):
        self.hqc_show_inactive = value

    # ── Setters de medição ──

    def set_hqc_meas_data(self, value: str):
        self.hqc_meas_data = value

    def set_hqc_meas_analito(self, value: str):
        self.hqc_meas_analito = value

    def set_hqc_meas_valor(self, value: str):
        self.hqc_meas_valor = value

    def set_hqc_meas_equipamento(self, value: str):
        self.hqc_meas_equipamento = value

    def set_hqc_meas_lote(self, value: str):
        self.hqc_meas_lote = value

    def set_hqc_meas_nivel(self, value: str):
        self.hqc_meas_nivel = value

    def set_hqc_meas_observacao(self, value: str):
        self.hqc_meas_observacao = value

    def set_hqc_meas_filter_analito(self, value: str):
        self.hqc_meas_filter_analito = value

    def set_hqc_meas_filter_status(self, value: str):
        self.hqc_meas_filter_status = value

    def set_hqc_meas_search(self, value: str):
        self.hqc_meas_search = value

    # ── Computed vars ──

    @rx.var
    def hqc_param_min_calc(self) -> str:
        """Preview do intervalo min calculado"""
        try:
            alvo = float(self.hqc_param_alvo or 0)
            if alvo <= 0:
                return ""
            if self.hqc_param_modo == "INTERVALO":
                return self.hqc_param_min
            tol = float(self.hqc_param_tolerancia or 0)
            if tol <= 0:
                return ""
            return f"{alvo * (1 - tol / 100):.4f}"
        except (ValueError, TypeError):
            return ""

    @rx.var
    def hqc_param_max_calc(self) -> str:
        """Preview do intervalo max calculado"""
        try:
            alvo = float(self.hqc_param_alvo or 0)
            if alvo <= 0:
                return ""
            if self.hqc_param_modo == "INTERVALO":
                return self.hqc_param_max
            tol = float(self.hqc_param_tolerancia or 0)
            if tol <= 0:
                return ""
            return f"{alvo * (1 + tol / 100):.4f}"
        except (ValueError, TypeError):
            return ""

    @rx.var
    def hqc_param_pct_calc(self) -> str:
        """Preview do percentual equivalente"""
        try:
            if self.hqc_param_modo == "PERCENTUAL":
                return self.hqc_param_tolerancia
            alvo = float(self.hqc_param_alvo or 0)
            vmin = float(self.hqc_param_min or 0)
            vmax = float(self.hqc_param_max or 0)
            if alvo <= 0:
                return ""
            pct = max(abs(vmax - alvo), abs(alvo - vmin)) / alvo * 100
            return f"{pct:.2f}"
        except (ValueError, TypeError):
            return ""

    @rx.var
    def hqc_active_parameters(self) -> List[HematologyQCParameter]:
        """Parâmetros filtrados por is_active ou todos"""
        if self.hqc_show_inactive:
            return self.hqc_parameters
        return [p for p in self.hqc_parameters if p.is_active]

    @rx.var
    def hqc_analitos_disponiveis(self) -> List[str]:
        """Lista de analitos únicos dos parâmetros ativos"""
        seen = set()
        result = []
        for p in self.hqc_parameters:
            if p.is_active and p.analito not in seen:
                seen.add(p.analito)
                result.append(p.analito)
        return sorted(result)

    @rx.var
    def hqc_analitos_filter_options(self) -> List[str]:
        """Lista de analitos com opção vazia para filtro 'Todos'"""
        return [""] + self.hqc_analitos_disponiveis

    @rx.var
    def hqc_filtered_measurements(self) -> List[HematologyQCMeasurement]:
        """Medições filtradas por analito, status e busca"""
        records = self.hqc_measurements
        if self.hqc_meas_filter_analito:
            records = [r for r in records if r.analito == self.hqc_meas_filter_analito]
        if self.hqc_meas_filter_status and self.hqc_meas_filter_status != "Todos":
            records = [r for r in records if r.status == self.hqc_meas_filter_status]
        search = (self.hqc_meas_search or "").strip().upper()
        if search:
            records = [r for r in records if search in (r.analito or "").upper() or search in (r.observacao or "").upper()]
        return records

    # ── CRUD Parâmetros ──

    async def load_hqc_parameters(self):
        """Carrega parâmetros do banco via VIEW resolvida"""
        try:
            rows = await HematologyQCService.get_parameters(active_only=False)
            self.hqc_parameters = [
                HematologyQCParameter(
                    id=str(r.get("id", "")),
                    analito=r.get("analito", ""),
                    equipamento=r.get("equipamento", "") or "",
                    lote_controle=r.get("lote_controle", "") or "",
                    nivel_controle=r.get("nivel_controle", "") or "",
                    modo=r.get("modo", "INTERVALO"),
                    alvo_valor=float(r.get("alvo_valor", 0)),
                    min_valor=float(r.get("min_valor") or 0),
                    max_valor=float(r.get("max_valor") or 0),
                    tolerancia_percentual=float(r.get("tolerancia_percentual") or 0),
                    is_active=bool(r.get("is_active", True)),
                    min_calc=float(r.get("min_calc") or 0),
                    max_calc=float(r.get("max_calc") or 0),
                    percentual_equivalente=float(r.get("percentual_equivalente") or 0),
                    created_at=str(r.get("created_at", "")),
                    updated_at=str(r.get("updated_at", "")),
                ) for r in rows
            ]
            logger.info(f"Carregados {len(self.hqc_parameters)} parâmetros de CQ Hematologia")
        except Exception as e:
            logger.error(f"Erro ao carregar parâmetros HQC: {e}")

    def clear_hqc_param_form(self):
        """Limpa formulário de parâmetros"""
        self.hqc_param_analito = ""
        self.hqc_param_modo = "INTERVALO"
        self.hqc_param_alvo = ""
        self.hqc_param_min = ""
        self.hqc_param_max = ""
        self.hqc_param_tolerancia = ""
        self.hqc_param_equipamento = ""
        self.hqc_param_lote = ""
        self.hqc_param_nivel = ""
        self.hqc_param_edit_id = ""
        self.hqc_param_success = ""
        self.hqc_param_error = ""

    def edit_hqc_parameter(self, param_id: str):
        """Carrega um parâmetro no formulário para edição"""
        param = next((p for p in self.hqc_parameters if p.id == param_id), None)
        if not param:
            return
        self.hqc_param_edit_id = param.id
        self.hqc_param_analito = param.analito
        self.hqc_param_modo = param.modo
        self.hqc_param_alvo = str(param.alvo_valor)
        self.hqc_param_min = str(param.min_valor) if param.min_valor else ""
        self.hqc_param_max = str(param.max_valor) if param.max_valor else ""
        self.hqc_param_tolerancia = str(param.tolerancia_percentual) if param.tolerancia_percentual else ""
        self.hqc_param_equipamento = param.equipamento
        self.hqc_param_lote = param.lote_controle
        self.hqc_param_nivel = param.nivel_controle
        self.hqc_param_success = ""
        self.hqc_param_error = ""

    async def save_hqc_parameter(self):
        """Salva (cria ou atualiza) parâmetro de CQ no Supabase"""
        self.is_saving_hqc_param = True
        self.hqc_param_success = ""
        self.hqc_param_error = ""
        try:
            # Validações
            analito = (self.hqc_param_analito or "").strip().upper()
            if not analito:
                self.hqc_param_error = "Informe o analito."
                self.is_saving_hqc_param = False
                return

            try:
                alvo = float(self.hqc_param_alvo)
                if alvo <= 0:
                    raise ValueError
            except (ValueError, TypeError):
                self.hqc_param_error = "Alvo deve ser numérico e maior que zero."
                self.is_saving_hqc_param = False
                return

            data = {
                "analito": analito,
                "modo": self.hqc_param_modo,
                "alvo_valor": alvo,
                "equipamento": self.hqc_param_equipamento.strip() or None,
                "lote_controle": self.hqc_param_lote.strip() or None,
                "nivel_controle": self.hqc_param_nivel.strip() or None,
            }

            if self.hqc_param_modo == "INTERVALO":
                try:
                    vmin = float(self.hqc_param_min)
                    vmax = float(self.hqc_param_max)
                    if vmin > vmax:
                        self.hqc_param_error = "Mín deve ser <= Máx."
                        self.is_saving_hqc_param = False
                        return
                except (ValueError, TypeError):
                    self.hqc_param_error = "Min e Max devem ser numéricos."
                    self.is_saving_hqc_param = False
                    return
                data["min_valor"] = vmin
                data["max_valor"] = vmax
                data["tolerancia_percentual"] = None
            else:
                try:
                    tol = float(self.hqc_param_tolerancia)
                    if tol <= 0 or tol > 100:
                        raise ValueError
                except (ValueError, TypeError):
                    self.hqc_param_error = "Tolerância deve ser entre 0 e 100%."
                    self.is_saving_hqc_param = False
                    return
                data["tolerancia_percentual"] = tol
                data["min_valor"] = None
                data["max_valor"] = None

            if self.hqc_param_edit_id:
                # Atualizar existente
                success = await HematologyQCService.update_parameter(self.hqc_param_edit_id, data)
                if success:
                    self.hqc_param_success = "Parâmetro atualizado!"
                    yield rx.toast.success("Parâmetro atualizado!", duration=4000, position="bottom-right")
                else:
                    self.hqc_param_error = "Erro ao atualizar parâmetro."
                    yield rx.toast.error("Erro ao atualizar.", duration=4000, position="bottom-right")
            else:
                # Criar novo — user_id precisa ser preenchido
                await HematologyQCService.create_parameter(data)
                self.hqc_param_success = "Parâmetro criado!"
                yield rx.toast.success("Parâmetro criado!", duration=4000, position="bottom-right")

            await self.load_hqc_parameters()
            self.clear_hqc_param_form()

        except Exception as e:
            self.hqc_param_error = f"Erro: {e}"
            logger.error(f"Erro ao salvar parâmetro HQC: {e}")
            yield rx.toast.error(f"Erro: {e}", duration=6000, position="bottom-right")
        finally:
            self.is_saving_hqc_param = False

    async def toggle_hqc_param_active(self, param_id: str):
        """Ativa/Inativa parâmetro"""
        param = next((p for p in self.hqc_parameters if p.id == param_id), None)
        if not param:
            return
        new_status = not param.is_active
        success = await HematologyQCService.toggle_parameter_active(param_id, new_status)
        if success:
            await self.load_hqc_parameters()
            label = "ativado" if new_status else "inativado"
            yield rx.toast.info(f"Parâmetro {label}.", duration=3000, position="bottom-right")

    async def delete_hqc_parameter(self, param_id: str):
        """Exclui parâmetro permanentemente"""
        success = await HematologyQCService.delete_parameter(param_id)
        if success:
            await self.load_hqc_parameters()
            yield rx.toast.info("Parâmetro excluído.", duration=3000, position="bottom-right")

    # ── Medições ──

    async def load_hqc_measurements(self):
        """Carrega medições do banco"""
        try:
            rows = await HematologyQCService.get_measurements(limit=500)
            self.hqc_measurements = [
                HematologyQCMeasurement(
                    id=str(r.get("id", "")),
                    data_medicao=str(r.get("data_medicao", "")),
                    analito=r.get("analito", ""),
                    valor_medido=float(r.get("valor_medido", 0)),
                    parameter_id=str(r.get("parameter_id", "")),
                    modo_usado=r.get("modo_usado", ""),
                    min_aplicado=float(r.get("min_aplicado", 0)),
                    max_aplicado=float(r.get("max_aplicado", 0)),
                    status=r.get("status", ""),
                    observacao=r.get("observacao", "") or "",
                    created_at=str(r.get("created_at", "")),
                ) for r in rows
            ]
            logger.info(f"Carregadas {len(self.hqc_measurements)} medições de CQ Hematologia")
        except Exception as e:
            logger.error(f"Erro ao carregar medições HQC: {e}")

    def clear_hqc_meas_form(self):
        """Limpa formulário de medição"""
        self.hqc_meas_valor = ""
        self.hqc_meas_observacao = ""
        self.hqc_meas_success = ""
        self.hqc_meas_error = ""
        self.hqc_last_result = None

    async def save_hqc_measurement(self):
        """Registra medição via RPC do banco"""
        self.is_saving_hqc_meas = True
        self.hqc_meas_success = ""
        self.hqc_meas_error = ""
        self.hqc_last_result = None
        try:
            analito = (self.hqc_meas_analito or "").strip().upper()
            if not analito:
                self.hqc_meas_error = "Selecione o analito."
                self.is_saving_hqc_meas = False
                return

            try:
                valor = float(self.hqc_meas_valor)
            except (ValueError, TypeError):
                self.hqc_meas_error = "Valor medido deve ser numérico."
                self.is_saving_hqc_meas = False
                return

            data = {
                "data_medicao": self.hqc_meas_data or datetime.now().strftime("%Y-%m-%d"),
                "analito": analito,
                "valor_medido": valor,
                "equipamento": self.hqc_meas_equipamento.strip() or None,
                "lote_controle": self.hqc_meas_lote.strip() or None,
                "nivel_controle": self.hqc_meas_nivel.strip() or None,
                "observacao": self.hqc_meas_observacao.strip() or None,
            }

            result = await HematologyQCService.register_measurement(data)
            self.hqc_last_result = result if isinstance(result, dict) else result

            status = result.get("status", "") if isinstance(result, dict) else "?"
            if status == "APROVADO":
                self.hqc_meas_success = f"APROVADO — Valor dentro do intervalo."
                yield rx.toast.success("APROVADO!", duration=5000, position="bottom-right")
            else:
                self.hqc_meas_error = f"REPROVADO — Valor fora do intervalo."
                yield rx.toast.error("REPROVADO!", duration=5000, position="bottom-right")

            await self.load_hqc_measurements()
            self.hqc_meas_valor = ""
            self.hqc_meas_observacao = ""

        except Exception as e:
            error_msg = str(e)
            if "Nenhum parâmetro ativo" in error_msg:
                self.hqc_meas_error = "Nenhum parâmetro ativo para este analito. Cadastre um parâmetro primeiro."
            else:
                self.hqc_meas_error = f"Erro: {error_msg}"
            logger.error(f"Erro ao registrar medição HQC: {e}")
            yield rx.toast.error(self.hqc_meas_error, duration=6000, position="bottom-right")
        finally:
            self.is_saving_hqc_meas = False

    async def delete_hqc_measurement(self, meas_id: str):
        """Exclui medição"""
        success = await HematologyQCService.delete_measurement(meas_id)
        if success:
            await self.load_hqc_measurements()
            yield rx.toast.info("Medição excluída.", duration=3000, position="bottom-right")

    @rx.var
    def filtered_hemato_bio_records(self) -> List[HematologyBioRecord]:
        """Registros Bio x CI (todos, ordenados por data)"""
        return self.hemato_bio_records

    @rx.var
    def hemato_bio_detail_rows(self) -> List[List[str]]:
        """Linhas formatadas para o modal de detalhes do registro Bio x CI.
        Cada linha: [analito, valor_bio, valor_ci, status]
        """
        rec = self.selected_hemato_bio_record
        if not rec or not rec.id:
            return []

        _LABELS = ["Hemácias", "Hematócrito", "Hemoglobina", "Leucócitos", "Plaquetas", "RDW", "VPM"]
        _KEYS = ["hemacias", "hematocrito", "hemoglobina", "leucocitos", "plaquetas", "rdw", "vpm"]

        rows: List[List[str]] = []
        modo = rec.modo_ci

        for label, key in zip(_LABELS, _KEYS):
            bio_val = getattr(rec, f"bio_{key}", 0.0) or 0.0
            bio_str = f"{bio_val:g}" if bio_val else "—"

            if modo == "bio":
                pad_val = getattr(rec, f"pad_{key}", 0.0) or 0.0
                ci_str = f"{pad_val:g}" if pad_val else "—"
                status = "—"
            elif modo == "intervalo":
                ci_min = getattr(rec, f"ci_min_{key}", 0.0) or 0.0
                ci_max = getattr(rec, f"ci_max_{key}", 0.0) or 0.0
                if ci_min or ci_max:
                    ci_str = f"{ci_min:g} — {ci_max:g}"
                    if bio_val and ci_min <= bio_val <= ci_max:
                        status = "OK"
                    elif bio_val:
                        status = "FORA"
                    else:
                        status = "—"
                else:
                    ci_str = "—"
                    status = "—"
            else:  # porcentagem
                pad_val = getattr(rec, f"pad_{key}", 0.0) or 0.0
                ci_pct = getattr(rec, f"ci_pct_{key}", 0.0) or 0.0
                if pad_val and ci_pct:
                    r_min = pad_val * (1 - ci_pct / 100)
                    r_max = pad_val * (1 + ci_pct / 100)
                    ci_str = f"{pad_val:g} ±{ci_pct:g}%  ({r_min:.2f} — {r_max:.2f})"
                    if bio_val and r_min <= bio_val <= r_max:
                        status = "OK"
                    elif bio_val:
                        status = "FORA"
                    else:
                        status = "—"
                elif pad_val:
                    ci_str = f"{pad_val:g}"
                    status = "—"
                else:
                    ci_str = "—"
                    status = "—"

            rows.append([label, bio_str, ci_str, status])

        return rows

    # ── Computed vars: status interativo da tabela Bio x CI ──

    _HEMATO_KEYS: List[str] = [
        "hemacias", "hematocrito", "hemoglobina",
        "leucocitos", "plaquetas", "rdw", "vpm",
    ]

    def _parse_hemato(self, val: str) -> Optional[float]:
        try:
            v = val.strip().replace(",", ".") if val else ""
            return float(v) if v else None
        except (ValueError, TypeError):
            return None

    @rx.var
    def hemato_ci_status_list(self) -> List[str]:
        """Status (OK/FORA/vazio) para cada analito na ordem padrão, conforme modo CI."""
        results: List[str] = []
        for key in self._HEMATO_KEYS:
            bio = self._parse_hemato(getattr(self, f"hemato_bio_{key}", ""))
            if bio is None:
                results.append("")
                continue

            if self.hemato_ci_mode == "intervalo":
                vmin = self._parse_hemato(getattr(self, f"hemato_ci_min_{key}", ""))
                vmax = self._parse_hemato(getattr(self, f"hemato_ci_max_{key}", ""))
                if vmin is not None and vmax is not None:
                    results.append("OK" if vmin <= bio <= vmax else "FORA")
                else:
                    results.append("")

            elif self.hemato_ci_mode == "porcentagem":
                pad = self._parse_hemato(getattr(self, f"hemato_pad_{key}", ""))
                pct = self._parse_hemato(getattr(self, f"hemato_ci_pct_{key}", ""))
                if pad is not None and pct is not None and pad > 0 and pct > 0:
                    calc_min = pad * (1 - pct / 100)
                    calc_max = pad * (1 + pct / 100)
                    results.append("OK" if calc_min <= bio <= calc_max else "FORA")
                else:
                    results.append("")
            else:
                results.append("")
        return results

    @rx.var
    def hemato_ci_range_list(self) -> List[str]:
        """Intervalo calculado (min — max) para modo porcentagem, por analito."""
        results: List[str] = []
        for key in self._HEMATO_KEYS:
            if self.hemato_ci_mode != "porcentagem":
                results.append("")
                continue
            pad = self._parse_hemato(getattr(self, f"hemato_pad_{key}", ""))
            pct = self._parse_hemato(getattr(self, f"hemato_ci_pct_{key}", ""))
            if pad is not None and pct is not None and pad > 0 and pct > 0:
                calc_min = pad * (1 - pct / 100)
                calc_max = pad * (1 + pct / 100)
                results.append(f"{calc_min:.2f} — {calc_max:.2f}")
            else:
                results.append("")
        return results

    async def load_hqc_data(self):
        """Carrega parâmetros, medições e registros Bio x CI"""
        await self.load_hqc_parameters()
        await self.load_hqc_measurements()
        await self.load_hemato_bio_records()
        if not self.hqc_meas_data:
            self.hqc_meas_data = datetime.now().strftime("%Y-%m-%d")
        if not self.hemato_bio_data:
            self.hemato_bio_data = datetime.now().strftime("%Y-%m-%d")
