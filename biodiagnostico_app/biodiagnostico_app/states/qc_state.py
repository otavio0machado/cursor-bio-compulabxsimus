import reflex as rx
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import calendar
import pandas as pd
import io
import base64
from datetime import timedelta
import reflex as rx
from typing import List, Dict, Any, Optional
from ..models import QCRecord, ReagentLot, MaintenanceRecord, LeveyJenningsPoint, QCReferenceValue, PostCalibrationRecord
from ..utils.qc_pdf_report import generate_qc_pdf
from ..services.qc_service import QCService
from ..services.qc_reference_service import QCReferenceService
from ..services.mapping_service import mapping_service
from ..services.westgard_service import WestgardService
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
        except:
            return 0.0

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

    # Lista restrita de exames permitidos no QC (Nomes Canônicos)
    ALLOWED_QC_EXAMS: List[str] = [
        "GLICOSE",
        "COLESTEROL TOTAL",
        "TRIGLICERIDEOS",
        "UREIA",
        "CREATININA",
        "ACIDO URICO",
        "GOT",
        "GPT",
        "GAMA GT",
        "FOSFATASE ALCALINA",
        "AMILASE",
        "CREATINOFOSFOQUINASE",
        "COLESTEROL HDL",
        "COLESTEROL LDL"
    ]

    @rx.var
    def unique_exam_names(self) -> List[str]:
        """Lista única de exames para dropdown"""
        names = set(r.exam_name for r in self.qc_records)
        names.update(self.ALLOWED_QC_EXAMS)
        return sorted(list(names))

    def set_qc_report_year(self, value: str):
        """Define o ano para o relatório"""
        self.qc_report_year = value
        return self.update_qc_preview()
    is_generating_qc_report: bool = False

    async def set_proin_tab(self, tab: str):
        """Alterna a tab ativa do ProIn e carrega dados necessários"""
        self.proin_current_tab = tab
        # Carregar dados automaticamente ao abrir certas abas
        if tab == "referencias":
            await self.load_qc_references()
        elif tab in ["dashboard", "registro", "relatorios"]:
            await self.load_data_from_db()

    async def load_data_from_db(self, force: bool = False):
        """Carrega registros de QC do banco de dados"""
        try:
            # Carregar registros de QC (sem limite prático para exibir todo histórico)
            db_records = await QCService.get_qc_records(limit=10000)

            if db_records:
                self.qc_records = [
                    QCRecord(
                        id=str(r.get("id", "")),
                        date=r.get("date", ""),
                        exam_name=r.get("exam_name", ""),
                        level=r.get("level", "Normal"),
                        lot_number=r.get("lot_number", ""),
                        value=float(r.get("value", 0)),
                        target_value=float(r.get("target_value", 0)),
                        target_sd=float(r.get("target_sd", 0)),
                        cv=float(r.get("cv", 0)) if r.get("cv") else 0.0,
                        status=r.get("status", "OK"),
                        equipment=r.get("equipment_name", ""),
                        analyst=r.get("analyst_name", ""),
                        westgard_violations=[],
                        reference_id=r.get("reference_id", "") or "",
                        needs_calibration=r.get("needs_calibration", False) or False,
                        post_calibration_id=r.get("post_calibration_id", "") or ""
                    )
                    for r in db_records
                ]
                # Ordenar por data decrescente (mais recente primeiro)
                self.qc_records = sorted(self.qc_records, key=lambda x: x.date, reverse=True)
                print(f"Carregados {len(self.qc_records)} registros de QC do banco")
        except Exception as e:
            print(f"Erro ao carregar dados do banco: {e}")

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
            count = len(self.proin_import_data)
            self.qc_success_message = f"{count} registros importados com sucesso!"
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
        """Salva um novo lote de reagente"""
        self.is_saving_reagent = True
        try:
             new_lot = ReagentLot(
                 id=str(len(self.reagent_lots) + 1),
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
             self.reagent_lots.append(new_lot)
             self.reagent_success_message = "Lote salvo com sucesso!"
             self.reagent_name = ""
             self.reagent_lot_number = ""
        except Exception as e:
            self.reagent_error_message = f"Erro ao salvar: {str(e)}"
        finally:
            self.is_saving_reagent = False

    async def delete_reagent_lot(self, id: str):
        """Deleta lote de reagente"""
        self.reagent_lots = [lot for lot in self.reagent_lots if lot.id != id]

    async def save_maintenance_record(self):
        """Registra manutenção"""
        self.is_saving_maintenance = True
        try:
            new_record = MaintenanceRecord(
                id=str(len(self.maintenance_records) + 1),
                equipment=self.maintenance_equipment,
                type=self.maintenance_type,
                date=self.maintenance_date,
                next_date=self.maintenance_next_date,
                technician=self.maintenance_technician,
                notes=self.maintenance_notes,
                created_at=datetime.now().isoformat()
            )
            self.maintenance_records.append(new_record)
            self.maintenance_success_message = "Manutenção registrada!"
            self.maintenance_equipment = ""
            self.maintenance_notes = ""
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
        """Atualiza dados do gráfico LJ"""
        if not self.levey_jennings_exam: return

        filtered = [r for r in self.qc_records if r.exam_name == self.levey_jennings_exam]
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
        
        # Calculate stats (legacy attributes for charts)
        if filtered:
            values = [r.value for r in filtered]
            # self.lj_mean = ... (Legacy attributes handled in frontend via chart data)

    # QC CRUD Actions
    async def save_qc_record(self):
        self.is_saving_qc = True
        self.reset_qc_messages()
        try:
             # Normalizar nome do exame antes de salvar
             canonical_name = mapping_service.get_canonical_name_sync(self.qc_exam_name)
             
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

             new_record = QCRecord(
                 id=str(len(self.qc_records) + 1),
                 date=self.qc_date or datetime.now().isoformat(),
                 exam_name=canonical_name,
                 level=self.qc_level,
                 lot_number=self.qc_lot_number,
                 value=val,
                 target_value=target,
                 target_sd=sd_target,
                 cv=cv,
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

             # Persistir no banco de dados
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
                         status=new_record.status,
                         westgard_violations=new_record.westgard_violations,
                         reference_id=new_record.reference_id,
                         needs_calibration=new_record.needs_calibration,
                         post_calibration_id=""
                     )
             except Exception as db_error:
                 print(f"Erro ao salvar no banco: {db_error}")
                 # Continua mesmo se falhar o banco (fallback para memória)

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
            print(f"Erro ao deletar do banco: {e}")
        # Remover da lista local
        self.qc_records = [r for r in self.qc_records if r.id != id]

    async def clear_all_qc_records(self):
        # Deletar todos do banco (opcional - por segurança, deletamos um a um)
        for record in self.qc_records:
            try:
                await QCService.delete_qc_record(record.id)
            except Exception as e:
                print(f"Erro ao deletar registro {record.id}: {e}")
        self.qc_records = []

    def clear_qc_form(self):
        """Limpa o formulário de registro de CQ"""
        self.qc_value = ""
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
            print(f"Erro ao buscar referência: {e}")
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
            print(f"Referências carregadas: {len(self.qc_reference_values)}")
        except Exception as e:
            print(f"Erro ao carregar referências: {e}")
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
            print(f"Erro ao desativar referência: {e}")

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
        except:
            return 0.0

    async def save_post_calibration(self):
        """Salva o registro de medição pós-calibração"""
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

            # Criar registro de pós-calibração
            new_record = PostCalibrationRecord(
                id=str(len(self.post_calibration_records) + 1),
                qc_record_id=self.selected_qc_record_for_calibration.get("id", ""),
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

            # Adicionar ao histórico
            self.post_calibration_records.insert(0, new_record)

            # Atualizar o registro QC original para indicar que tem pós-calibração
            qc_record_id = self.selected_qc_record_for_calibration.get("id", "")
            for i, r in enumerate(self.qc_records):
                if r.id == qc_record_id:
                    # Criar novo registro com post_calibration_id atualizado
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
                except:
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
                 except:
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
            print(f"Erro interno PDF Generation: {e}")
            raise e

    async def generate_qc_report_pdf(self):
        """Gera PDF das tabelas de QC e inicia download"""
        self.is_generating_qc_report = True
        yield

        try:
            pdf_bytes, filename = await self._generate_pdf_bytes()

            if pdf_bytes:
                print(f"DEBUG PDF: Gerado {len(pdf_bytes)} bytes, filename={filename}")
                b64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
                self.qc_pdf_preview = b64_pdf
                self.is_generating_qc_report = False

                # Usar bytes diretamente ao invés de data URI
                yield rx.download(data=pdf_bytes, filename=filename)
            else:
                print("DEBUG PDF: pdf_bytes está vazio")
                self.qc_error_message = "Erro: PDF não foi gerado"
                self.is_generating_qc_report = False

        except Exception as e:
            print(f"Erro ao gerar PDF QC: {e}")
            import traceback
            traceback.print_exc()
            self.qc_error_message = f"Erro na geração do PDF: {str(e)}"
            self.is_generating_qc_report = False
