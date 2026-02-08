import reflex as rx
import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import calendar
import pandas as pd
import io
import base64

logger = logging.getLogger(__name__)
from ..models import QCRecord, ReagentLot, MaintenanceRecord, LeveyJenningsPoint, QCReferenceValue, PostCalibrationRecord
from ..utils.qc_pdf_report import generate_qc_pdf
from ..services.qc_service import QCService
from ..services.qc_reference_service import QCReferenceService
from ..services.westgard_service import WestgardService
from ..services.reagent_service import ReagentService
from ..services.maintenance_service import MaintenanceService
from ..services.post_calibration_service import PostCalibrationService
from ..services.qc_exam_service import QCExamService
from ..services.qc_registry_name_service import QCRegistryNameService
from .dashboard_state import DashboardState

class QCState(DashboardState):
    """Estado responsável pelo Controle de Qualidade (ProIn), Reagentes e Manutenções"""
    
    # ===== ProIn QC - Sistema de Controle de Qualidade =====
    proin_current_tab: str = "dashboard"  # dashboard, registro, reagentes, relatorios, importar
    
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

    # Loading state for initial data load
    is_loading_data: bool = False

    # Pagination
    qc_page: int = 0
    qc_page_size: int = 50

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
    def paginated_qc_records(self) -> List[QCRecord]:
        """Retorna registros paginados"""
        start = self.qc_page * self.qc_page_size
        end = start + self.qc_page_size
        return self.qc_records[start:end]

    @rx.var
    def total_qc_pages(self) -> int:
        """Total de páginas"""
        total = len(self.qc_records)
        if total == 0:
            return 1
        return (total + self.qc_page_size - 1) // self.qc_page_size

    def next_qc_page(self):
        if self.qc_page < self.total_qc_pages - 1:
            self.qc_page += 1

    def prev_qc_page(self):
        if self.qc_page > 0:
            self.qc_page -= 1

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
        """Limite inferior fixo do gráfico (Target - 4 SD)"""
        if self.lj_target_sd_val == 0: return 0.0 # Auto
        return self.lj_target_val - (4 * self.lj_target_sd_val)

    @rx.var
    def lj_max_domain(self) -> float:
        """Limite superior fixo do gráfico (Target + 4 SD)"""
        if self.lj_target_sd_val == 0: return 100.0 # Auto fallback
        return self.lj_target_val + (4 * self.lj_target_sd_val)

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
                if (datetime.now() - last).total_seconds() < 30:
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
                            id=str(r.get("id", "")),
                            date=r.get("date", ""),
                            exam_name=r.get("exam_name", ""),
                            level=r.get("level", "Normal"),
                            lot_number=r.get("lot_number", ""),
                            value=float(r.get("value", 0)),
                            target_value=float(r.get("target_value", 0)),
                            target_sd=float(r.get("target_sd", 0)),
                            cv=cv,
                            cv_max_threshold=cv_max_threshold,
                            status=status,
                            equipment=r.get("equipment_name", ""),
                            analyst=r.get("analyst_name", ""),
                            westgard_violations=[],
                            reference_id=reference_id,
                            needs_calibration=needs_calibration,
                            post_calibration_id=r.get("post_calibration_id", "") or ""
                        )
                    )

                self.qc_records = records
                self.qc_records = sorted(self.qc_records, key=lambda x: x.date, reverse=True)
                logger.info(f"Carregados {len(self.qc_records)} registros de QC do banco")

            # Carregar lotes de reagentes
            try:
                db_lots = await ReagentService.get_lots()
                self.reagent_lots = [
                    ReagentLot(
                        id=str(r.get("id", "")),
                        name=r.get("name", ""),
                        lot_number=r.get("lot_number", ""),
                        expiry_date=r.get("expiry_date", ""),
                        quantity=r.get("quantity", ""),
                        manufacturer=r.get("manufacturer", ""),
                        storage_temp=r.get("storage_temp", ""),
                        current_stock=float(r.get("current_stock", 0)),
                        estimated_consumption=float(r.get("estimated_consumption", 0)),
                        created_at=str(r.get("created_at", ""))
                    )
                    for r in db_lots
                ]
                logger.info(f"Carregados {len(self.reagent_lots)} lotes de reagentes")
            except Exception as e:
                logger.error(f"Erro ao carregar reagentes: {e}")

            # Carregar registros de manutenção
            try:
                db_maint = await MaintenanceService.get_records()
                self.maintenance_records = [
                    MaintenanceRecord(
                        id=str(r.get("id", "")),
                        equipment=r.get("equipment", ""),
                        type=r.get("type", ""),
                        date=r.get("date", ""),
                        next_date=r.get("next_date", ""),
                        technician=r.get("technician", ""),
                        notes=r.get("notes", ""),
                        created_at=str(r.get("created_at", ""))
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
                        id=str(r.get("id", "")),
                        qc_record_id=str(r.get("qc_record_id", "")),
                        date=r.get("date", ""),
                        exam_name=r.get("exam_name", ""),
                        original_value=float(r.get("original_value", 0)),
                        original_cv=float(r.get("original_cv", 0)),
                        post_calibration_value=float(r.get("post_calibration_value", 0)),
                        post_calibration_cv=float(r.get("post_calibration_cv", 0)),
                        target_value=float(r.get("target_value", 0)),
                        analyst=r.get("analyst", ""),
                        notes=r.get("notes", ""),
                        created_at=str(r.get("created_at", ""))
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
        self.is_importing = True
        self.upload_progress = 10
        
        try:
            for file in files:
                upload_data = await file.read()
                df = pd.read_excel(io.BytesIO(upload_data))
                self.proin_import_headers = list(df.columns)
                self.proin_import_preview = df.head(5).values.tolist()
                self.proin_import_data = df.to_dict('records')
                self.upload_progress = 100
        except Exception as e:
            self.qc_error_message = f"Erro ao processar arquivo: {str(e)}"
        finally:
            self.is_importing = False

    async def process_proin_import(self):
        """Process the imported data and save to DB"""
        try:
            if not self.proin_import_data:
                self.qc_error_message = "Nenhum dado para importar."
                return

            # Map imported columns to DB fields
            records_to_save = []
            for row in self.proin_import_data:
                record_data = {
                    "date": str(row.get("date", row.get("data", row.get("DATA", datetime.now().isoformat())))),
                    "exam_name": str(row.get("exam_name", row.get("exame", row.get("EXAME", "")))),
                    "level": str(row.get("level", row.get("nivel", row.get("NIVEL", "Normal")))),
                    "lot_number": str(row.get("lot_number", row.get("lote", row.get("LOTE", "")))),
                    "value": float(row.get("value", row.get("valor", row.get("VALOR", 0)))),
                    "target_value": float(row.get("target_value", row.get("alvo", row.get("ALVO", 0)))),
                    "target_sd": float(row.get("target_sd", row.get("dp", row.get("DP", 0)))),
                    "equipment": str(row.get("equipment", row.get("equipamento", row.get("EQUIPAMENTO", "")))),
                    "analyst": str(row.get("analyst", row.get("analista", row.get("ANALISTA", "")))),
                }
                # Calculate CV if not provided
                val = record_data["value"]
                target = record_data["target_value"]
                if target > 0:
                    record_data["cv"] = round((abs(val - target) / target) * 100, 2)
                else:
                    record_data["cv"] = 0.0
                record_data["status"] = "OK"
                record_data["needs_calibration"] = False
                records_to_save.append(record_data)

            # Batch insert to database
            result = await QCService.create_qc_records_batch(records_to_save)
            count = len(records_to_save)

            if result:
                self.qc_success_message = f"{count} registros importados com sucesso!"
                # Reload data from DB to sync state
                await self.load_data_from_db(force=True)
            else:
                self.qc_error_message = "Erro ao salvar registros importados no banco."

            self.clear_proin_import()
        except Exception as e:
            self.qc_error_message = f"Erro na importação: {str(e)}"

    def clear_proin_import(self):
        """Clear import state"""
        self.proin_import_preview = []
        self.proin_import_headers = []
        self.proin_import_data = []
        self.upload_progress = 0

    async def save_reagent_lot(self):
        """Salva um novo lote de reagente no Supabase"""
        self.is_saving_reagent = True
        self.reagent_error_message = ""
        self.reagent_success_message = ""
        try:
             # Validação de campos obrigatórios
             if not self.reagent_name.strip():
                 self.reagent_error_message = "Nome do reagente é obrigatório."
                 return
             if not self.reagent_lot_number.strip():
                 self.reagent_error_message = "Número do lote é obrigatório."
                 return
             if not self.reagent_expiry_date:
                 self.reagent_error_message = "Data de validade é obrigatória."
                 return
             db_result = await ReagentService.create_lot({
                 "name": self.reagent_name,
                 "lot_number": self.reagent_lot_number,
                 "expiry_date": self.reagent_expiry_date,
                 "quantity": self.reagent_quantity,
                 "manufacturer": self.reagent_manufacturer,
                 "storage_temp": self.reagent_storage_temp,
                 "current_stock": float(self.reagent_initial_stock or 0),
                 "estimated_consumption": float(self.reagent_daily_consumption or 0),
             })
             new_lot = ReagentLot(
                 id=str(db_result.get("id", "")),
                 name=self.reagent_name,
                 lot_number=self.reagent_lot_number,
                 expiry_date=self.reagent_expiry_date,
                 quantity=self.reagent_quantity,
                 manufacturer=self.reagent_manufacturer,
                 storage_temp=self.reagent_storage_temp,
                 current_stock=float(self.reagent_initial_stock or 0),
                 estimated_consumption=float(self.reagent_daily_consumption or 0),
                 created_at=datetime.now().isoformat()
             )
             self.reagent_lots.insert(0, new_lot)
             self.reagent_success_message = "Lote salvo com sucesso!"
             self.reagent_name = ""
             self.reagent_lot_number = ""
        except Exception as e:
            self.reagent_error_message = f"Erro ao salvar: {str(e)}"
        finally:
            self.is_saving_reagent = False

    async def delete_reagent_lot(self, id: str):
        """Deleta lote de reagente do Supabase"""
        try:
            await ReagentService.delete_lot(id)
        except Exception as e:
            logger.error(f"Erro ao deletar lote: {e}")
        self.reagent_lots = [lot for lot in self.reagent_lots if lot.id != id]

    async def save_maintenance_record(self):
        """Registra manutenção no Supabase"""
        self.is_saving_maintenance = True
        self.maintenance_error_message = ""
        self.maintenance_success_message = ""
        try:
            # Validação de campos obrigatórios
            if not self.maintenance_equipment.strip():
                self.maintenance_error_message = "Equipamento é obrigatório."
                return
            if not self.maintenance_type:
                self.maintenance_error_message = "Tipo de manutenção é obrigatório."
                return
            if not self.maintenance_date:
                self.maintenance_error_message = "Data é obrigatória."
                return
            db_result = await MaintenanceService.create_record({
                "equipment": self.maintenance_equipment,
                "type": self.maintenance_type,
                "date": self.maintenance_date,
                "next_date": self.maintenance_next_date,
                "technician": self.maintenance_technician,
                "notes": self.maintenance_notes,
            })
            new_record = MaintenanceRecord(
                id=str(db_result.get("id", "")),
                equipment=self.maintenance_equipment,
                type=self.maintenance_type,
                date=self.maintenance_date,
                next_date=self.maintenance_next_date,
                technician=self.maintenance_technician,
                notes=self.maintenance_notes,
                created_at=datetime.now().isoformat()
            )
            self.maintenance_records.insert(0, new_record)
            self.maintenance_success_message = "Manutenção registrada!"
            self.maintenance_equipment = ""
            self.maintenance_notes = ""
        except Exception as e:
            self.maintenance_error_message = f"Erro ao salvar: {str(e)}"
        finally:
            self.is_saving_maintenance = False

    # Lógica de cálculo SD/CV para formulário
    def calculate_sd(self):
        """Calcula o Desvio Padrão (Diferença Absoluta) automaticamente"""
        try:
            if not self.qc_value or not self.qc_target_value:
                return
            
            val_str = self.qc_value.replace(",", ".")
            target_str = self.qc_target_value.replace(",", ".")
            
            if not val_str or not target_str:
                return

            value = float(val_str)
            target = float(target_str)
            
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
             
             if violations:
                 new_record.westgard_violations = violations
                 # Determine status severity
                 rejections = [v for v in violations if v["severity"] == "rejection"]
                 warnings = [v for v in violations if v["severity"] == "warning"]

                 if rejections:
                     rule = rejections[0]['rule']
                     new_record.status = f"ERRO ({rule})"
                     new_record.needs_calibration = True  # Rejeição exige calibração
                     self.qc_error_message = f"Regra {rule} violada: {rejections[0]['description']}"
                     self.qc_success_message = "" # Limpa sucesso se houve erro crítico
                 elif warnings:
                     rule = warnings[0]['rule']
                     new_record.status = f"ALERTA ({rule})"
                     self.qc_warning_message = f"Salvo com Alerta ({rule}): {warnings[0]['description']}"
                     self.qc_success_message = ""
                 else:
                     new_record.status = "OK"
             else:
                 self.qc_success_message = "Registro salvo! Sem violações de regras."
                 self.qc_error_message = ""
                 self.qc_warning_message = ""

             # Aplicar regra de CV% para calibração e status
             cv_out = cv > cv_max_threshold
             if cv_out:
                 new_record.needs_calibration = True
                 # Definir status de CV no registro se nao houve violacao Westgard mais grave
                 if new_record.status == "OK":
                     new_record.status = "ALERTA (CV)"
                 if not self.qc_error_message and not self.qc_warning_message:
                     self.qc_warning_message = "CV acima do limite. Calibração necessária."
                     self.qc_success_message = ""

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
                 self.qc_error_message = "Erro ao salvar no banco de dados. Tente novamente."

             # Only append to local state if DB save succeeded
             if db_saved:
                 self.qc_records.append(new_record)
                 # Reordenar por data decrescente (mais recente primeiro)
                 self.qc_records = sorted(self.qc_records, key=lambda x: x.date, reverse=True)

             # Se houve erro, não limpa o form imediatamente para permitir ajuste se foi digitação errada?
             # Por enquanto limpa para seguir fluxo normal, mas mantém msg
             self.qc_value = ""
             
        except Exception as e:
            self.qc_error_message = f"Erro: {e}"
        finally:
            self.is_saving_qc = False

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
        try:
            refs = await QCReferenceService.get_references(active_only=True)
            self.qc_reference_values = [
                QCReferenceValue(
                    id=r.get("id") or "",
                    name=r.get("name") or "",
                    exam_name=r.get("exam_name") or "",
                    valid_from=r.get("valid_from") or "",
                    valid_until=r.get("valid_until") or "",
                    target_value=float(r.get("target_value") or 0),
                    cv_max_threshold=float(r.get("cv_max_threshold") or 10.0),
                    lot_number=r.get("lot_number") or "",
                    manufacturer=r.get("manufacturer") or "",
                    level=r.get("level") or "Normal",
                    notes=r.get("notes") or "",
                    is_active=r.get("is_active", True),
                    created_at=r.get("created_at") or "",
                    updated_at=r.get("updated_at") or ""
                )
                for r in refs
            ]
            logger.info(f"Referências carregadas: {len(self.qc_reference_values)}")
        except Exception as e:
            logger.error(f"Erro ao carregar referências: {e}")
            self.qc_reference_values = []

    async def save_qc_reference(self):
        """Salva novo registro de valor referencial"""
        self.is_saving_reference = True
        self.ref_success_message = ""
        self.ref_error_message = ""

        try:
            # Validações
            if not self.ref_name:
                self.ref_error_message = "Nome do registro é obrigatório"
                return
            if not self.ref_exam_name:
                self.ref_error_message = "Exame é obrigatório"
                return
            if not self.ref_valid_from:
                self.ref_error_message = "Data de início é obrigatória"
                return
            if not self.ref_target_value:
                self.ref_error_message = "Valor-alvo é obrigatório"
                return

            cv_max_str = (self.ref_cv_max_threshold or "10.0").replace(",", ".")
            cv_max = float(cv_max_str)

            if cv_max <= 0:
                self.ref_error_message = "Limite máximo de CV% deve ser maior que zero"
                return

            target_val = float(self.ref_target_value.replace(",", "."))
            if target_val <= 0:
                self.ref_error_message = "Valor-alvo deve ser maior que zero"
                return

            # Criar registro
            data = {
                "name": self.ref_name,
                "exam_name": self.ref_exam_name,
                "valid_from": self.ref_valid_from,
                "valid_until": self.ref_valid_until or None,
                "target_value": target_val,
                "cv_max_threshold": cv_max,
                "lot_number": self.ref_lot_number,
                "manufacturer": self.ref_manufacturer,
                "level": self.ref_level,
                "notes": self.ref_notes,
                "is_active": True
            }

            result = await QCReferenceService.create_reference(data)

            if result:
                self.ref_success_message = "Referência salva com sucesso!"
                # Limpar formulário
                self.ref_name = ""
                self.ref_exam_name = ""
                self.ref_valid_from = ""
                self.ref_valid_until = ""
                self.ref_target_value = ""
                self.ref_cv_max_threshold = "10.0"
                self.ref_lot_number = ""
                self.ref_manufacturer = ""
                self.ref_level = "Normal"
                self.ref_notes = ""
                # Recarregar lista
                await self.load_qc_references()
            else:
                self.ref_error_message = "Erro ao salvar referência"

        except ValueError as ve:
            self.ref_error_message = f"Valor inválido: {ve}"
        except Exception as e:
            self.ref_error_message = f"Erro: {e}"
        finally:
            self.is_saving_reference = False

    async def deactivate_qc_reference(self, id: str):
        """Desativa uma referência"""
        try:
            success = await QCReferenceService.deactivate_reference(id)
            if success:
                await self.load_qc_references()
        except Exception as e:
            logger.error(f"Erro ao desativar referência: {e}")

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
        """Confirma e executa exclusão permanente do registro de CQ"""
        if not self.delete_qc_record_id:
            return

        try:
            success = await QCService.delete_qc_record(self.delete_qc_record_id)
            if success:
                self.qc_records = [r for r in self.qc_records if r.id != self.delete_qc_record_id]
                self.qc_success_message = "Registro excluído permanentemente!"
            else:
                self.qc_error_message = "Erro ao excluir registro do banco de dados"
        except Exception as e:
            self.qc_error_message = f"Erro ao excluir: {e}"
        finally:
            self.close_delete_qc_record_modal()

    def open_delete_reference_modal(self, ref_id: str, ref_name: str):
        """Abre modal de confirmação para excluir referência"""
        self.delete_reference_id = ref_id
        self.delete_reference_name = ref_name
        self.show_delete_reference_modal = True

    def close_delete_reference_modal(self):
        """Fecha modal de confirmação de exclusão de referência"""
        self.show_delete_reference_modal = False
        self.delete_reference_id = ""
        self.delete_reference_name = ""

    async def confirm_delete_reference(self):
        """Confirma e executa exclusão permanente da referência"""
        if not self.delete_reference_id:
            return

        try:
            success = await QCReferenceService.delete_reference(self.delete_reference_id)
            if success:
                self.ref_success_message = "Referência excluída permanentemente!"
                await self.load_qc_references()
            else:
                self.ref_error_message = "Erro ao excluir referência do banco de dados"
        except Exception as e:
            self.ref_error_message = f"Erro ao excluir: {e}"
        finally:
            self.close_delete_reference_modal()

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
        # Buscar o registro pelo ID
        record = next((r for r in self.qc_records if r.id == record_id), None)
        if record:
            self.selected_qc_record_for_calibration = {
                "id": record.id,
                "exam_name": record.exam_name,
                "date": record.date,
                "value": record.value,
                "cv": record.cv,
                "target_value": record.target_value,
                "status": record.status
            }
            self.show_post_calibration_modal = True
            self.post_cal_value = ""
            self.post_cal_analyst = ""
            self.post_cal_notes = ""
            self.post_cal_success_message = ""
            self.post_cal_error_message = ""

    def close_post_calibration_modal(self):
        """Fecha o modal de pós-calibração"""
        self.show_post_calibration_modal = False
        self.selected_qc_record_for_calibration = None
        self.post_cal_value = ""
        self.post_cal_analyst = ""
        self.post_cal_notes = ""
        self.post_cal_success_message = ""
        self.post_cal_error_message = ""

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
        self.is_saving_post_calibration = True
        self.post_cal_success_message = ""
        self.post_cal_error_message = ""

        try:
            if not self.post_cal_value:
                self.post_cal_error_message = "Informe o valor da medição pós-calibração"
                return

            if not self.selected_qc_record_for_calibration:
                self.post_cal_error_message = "Nenhum registro selecionado"
                return

            val = float(self.post_cal_value.replace(",", "."))
            target = float(self.selected_qc_record_for_calibration.get("target_value", 0))

            # Calcular CV pós calibração
            post_cv = 0.0
            if target > 0:
                diff = abs(val - target)
                post_cv = round((diff / target) * 100, 2)

            qc_record_id = self.selected_qc_record_for_calibration.get("id", "")

            # Persistir no Supabase
            db_result = await PostCalibrationService.create_record({
                "qc_record_id": qc_record_id,
                "date": datetime.now().isoformat(),
                "exam_name": self.selected_qc_record_for_calibration.get("exam_name", ""),
                "original_value": float(self.selected_qc_record_for_calibration.get("value", 0)),
                "original_cv": float(self.selected_qc_record_for_calibration.get("cv", 0)),
                "post_calibration_value": val,
                "post_calibration_cv": post_cv,
                "target_value": target,
                "analyst": self.post_cal_analyst,
                "notes": self.post_cal_notes,
            })

            new_record = PostCalibrationRecord(
                id=str(db_result.get("id", "")),
                qc_record_id=qc_record_id,
                date=datetime.now().isoformat(),
                exam_name=self.selected_qc_record_for_calibration.get("exam_name", ""),
                original_value=float(self.selected_qc_record_for_calibration.get("value", 0)),
                original_cv=float(self.selected_qc_record_for_calibration.get("cv", 0)),
                post_calibration_value=val,
                post_calibration_cv=post_cv,
                target_value=target,
                analyst=self.post_cal_analyst,
                notes=self.post_cal_notes,
                created_at=datetime.now().isoformat()
            )

            # Adicionar ao histórico local
            self.post_calibration_records.insert(0, new_record)

            # Atualizar o registro QC original para indicar que tem pós-calibração
            for i, r in enumerate(self.qc_records):
                if r.id == qc_record_id:
                    updated_record = QCRecord(
                        id=r.id,
                        date=r.date,
                        exam_name=r.exam_name,
                        level=r.level,
                        lot_number=r.lot_number,
                        value=r.value,
                        value1=r.value1,
                        value2=r.value2,
                        mean=r.mean,
                        sd=r.sd,
                        cv=r.cv,
                        cv_max_threshold=r.cv_max_threshold,
                        target_value=r.target_value,
                        target_sd=r.target_sd,
                        equipment=r.equipment,
                        analyst=r.analyst,
                        status=r.status,
                        westgard_violations=r.westgard_violations,
                        z_score=r.z_score,
                        reference_id=r.reference_id,
                        needs_calibration=r.needs_calibration,
                        post_calibration_id=new_record.id
                    )
                    self.qc_records[i] = updated_record
                    break

            self.post_cal_success_message = "Medição pós-calibração salva com sucesso!"

            # Fechar modal após pequeno delay para mostrar mensagem de sucesso
            await asyncio.sleep(1.5)
            self.close_post_calibration_modal()

        except ValueError:
            self.post_cal_error_message = "Valor inválido. Use números."
        except Exception as e:
            self.post_cal_error_message = f"Erro ao salvar: {str(e)}"
        finally:
            self.is_saving_post_calibration = False

    @rx.var
    def has_post_calibration_records(self) -> bool:
        """Verifica se há registros de pós-calibração"""
        return len(self.post_calibration_records) > 0

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
        try:
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
                except (ValueError, TypeError):
                    self.qc_error_message = "Mês/Ano inválidos"
                    return None, None

            elif self.qc_report_type == "3 Meses":
                start_date = (now - timedelta(days=90)).date().isoformat()
                end_date = now.date().isoformat()
                period_desc = "Últimos 3 Meses"
            
            # Year specific
            elif self.qc_report_type == "Ano Atual":
                start_date = now.replace(month=1, day=1).date().isoformat()
                end_date = now.replace(month=12, day=31).date().isoformat()
                period_desc = f"Ano {now.year}"
                
            elif self.qc_report_type == "Ano Específico":
                 try:
                    year = int(self.qc_report_year)
                    start_date = f"{year}-01-01"
                    end_date = f"{year}-12-31"
                    period_desc = f"Ano {year}"
                 except (ValueError, TypeError):
                    self.qc_error_message = "Ano inválido"
                    return None, None

            # Buscar dados (Mock via Service)
            # records = await QCService.get_qc_records(limit=2000)
            records = self.qc_records # Use local state records
            
            filtered_records = []
            if start_date and end_date:
                for r in records:
                    # r.date format iso string
                    if r.date >= start_date and r.date <= (end_date + "T23:59:59"):
                        filtered_records.append(r)
            else:
                filtered_records = records
            
            # Sort by date
            filtered_records.sort(key=lambda x: x.date, reverse=True)
            
            if not filtered_records:
                self.qc_error_message = "Nenhum registro encontrado no período."
                # Allow generating empty report or return None
                # return None, None
            
            # Executar em thread pool
            loop = asyncio.get_event_loop()
            pdf_bytes = await loop.run_in_executor(
                None,
                lambda: generate_qc_pdf(filtered_records, period_desc, self.post_calibration_records)
            )
            
            filename = f"QC_Report_{period_desc.replace('/', '_').replace(' ', '_')}.pdf"
            return pdf_bytes, filename

        except Exception as e:
            logger.error(f"Erro interno PDF Generation: {e}")
            raise

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

    async def export_qc_csv(self):
        """Exporta registros de QC como CSV para download"""
        if not self.qc_records:
            self.qc_error_message = "Nenhum registro para exportar."
            return

        header = "Data,Exame,Nível,Lote,Valor,Alvo,DP,CV%,Status,Equipamento,Analista\n"
        rows = []
        for r in self.qc_records:
            row = f"{r.date},{r.exam_name},{r.level},{r.lot_number},{r.value},{r.target_value},{r.target_sd},{r.cv:.2f},{r.status},{r.equipment},{r.analyst}"
            rows.append(row)

        csv_content = header + "\n".join(rows)
        csv_bytes = csv_content.encode("utf-8-sig")
        filename = f"QC_Export_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
        yield rx.download(data=csv_bytes, filename=filename)

    async def delete_maintenance_record(self, record_id: str):
        """Deleta registro de manutenção do Supabase"""
        try:
            await MaintenanceService.delete_record(record_id)
        except Exception as e:
            logger.error(f"Erro ao deletar manutenção: {e}")
        self.maintenance_records = [r for r in self.maintenance_records if r.id != record_id]

    # ===== Voice-to-Form Handlers =====

    def open_voice_modal(self, form_type: str):
        """Abre modal de gravacao de voz para o formulario especificado"""
        self.show_voice_modal = True
        self.voice_form_target = form_type
        self.voice_is_recording = False
        self.voice_is_processing = False
        self.voice_audio_base64 = ""
        self.voice_status_message = "Toque no microfone para iniciar"
        self.voice_error_message = ""

    def close_voice_modal(self):
        """Fecha modal de voz e limpa estado"""
        self.show_voice_modal = False
        self.voice_form_target = ""
        self.voice_is_recording = False
        self.voice_is_processing = False
        self.voice_audio_base64 = ""
        self.voice_status_message = ""
        self.voice_error_message = ""

    def set_voice_recording(self, is_recording: bool):
        """Chamado pelo JS callback quando gravacao inicia/para"""
        self.voice_is_recording = is_recording
        if is_recording:
            self.voice_status_message = "Gravando... Fale os dados do formulario"
            self.voice_error_message = ""
        else:
            self.voice_status_message = "Gravacao finalizada"

    def receive_voice_audio(self, audio_base64: str):
        """Recebe audio base64 do JS MediaRecorder callback"""
        self.voice_audio_base64 = audio_base64
        self.voice_is_recording = False
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

        try:
            from ..services.voice_ai_service import VoiceAIService
            result = await VoiceAIService.process_audio(
                audio_base64=self.voice_audio_base64,
                form_type=self.voice_form_target,
            )

            if "error" in result:
                self.voice_error_message = result["error"]
                self.voice_status_message = ""
                return

            self._apply_voice_data(result)
            self.voice_status_message = "Campos preenchidos com sucesso!"
            self.voice_error_message = ""
            yield

            await asyncio.sleep(1.2)
            self.close_voice_modal()

        except Exception as e:
            logger.error(f"Voice processing error: {e}")
            self.voice_error_message = f"Erro: {str(e)}"
            self.voice_status_message = ""
        finally:
            self.voice_is_processing = False

    def _apply_voice_data(self, data: Dict[str, Any]):
        """Aplica dados extraidos pelo Gemini nos campos do formulario correto"""
        target = self.voice_form_target

        if target == "registro":
            if data.get("exam_name"):
                self.qc_exam_name = data["exam_name"]
            if data.get("value") is not None:
                self.qc_value = str(data["value"])
            if data.get("target_value") is not None:
                self.qc_target_value = str(data["target_value"])
                self.calculate_sd()
            if data.get("equipment"):
                self.qc_equipment = data["equipment"]
            if data.get("analyst"):
                self.qc_analyst = data["analyst"]

        elif target == "referencia":
            if data.get("name"):
                self.ref_name = data["name"]
            if data.get("exam_name"):
                self.ref_exam_name = data["exam_name"]
            if data.get("level"):
                self.ref_level = data["level"]
            if data.get("valid_from"):
                self.ref_valid_from = data["valid_from"]
            if data.get("valid_until"):
                self.ref_valid_until = data["valid_until"]
            if data.get("target_value") is not None:
                self.ref_target_value = str(data["target_value"])
            if data.get("cv_max") is not None:
                self.ref_cv_max_threshold = str(data["cv_max"])
            if data.get("lot_number"):
                self.ref_lot_number = data["lot_number"]
            if data.get("manufacturer"):
                self.ref_manufacturer = data["manufacturer"]
            if data.get("notes"):
                self.ref_notes = data["notes"]

        elif target == "reagente":
            if data.get("name"):
                self.reagent_name = data["name"]
            if data.get("lot_number"):
                self.reagent_lot_number = data["lot_number"]
            if data.get("expiry_date"):
                self.reagent_expiry_date = data["expiry_date"]
            if data.get("initial_stock") is not None:
                self.reagent_initial_stock = str(data["initial_stock"])
            if data.get("daily_consumption") is not None:
                self.reagent_daily_consumption = str(data["daily_consumption"])
            if data.get("manufacturer"):
                self.reagent_manufacturer = data["manufacturer"]

        elif target == "manutencao":
            if data.get("equipment"):
                self.maintenance_equipment = data["equipment"]
            if data.get("type"):
                self.maintenance_type = data["type"]
            if data.get("date"):
                self.maintenance_date = data["date"]
            if data.get("next_date"):
                self.maintenance_next_date = data["next_date"]
            if data.get("notes"):
                self.maintenance_notes = data["notes"]
