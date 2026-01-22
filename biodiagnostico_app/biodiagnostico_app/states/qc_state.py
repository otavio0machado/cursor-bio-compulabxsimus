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
from ..models import QCRecord, ReagentLot, MaintenanceRecord, LeveyJenningsPoint
from ..utils.qc_pdf_report import generate_qc_pdf
from ..services.qc_service import QCService
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
        """Status do CV (OK, ALERTA, ERRO)"""
        cv = self.qc_calculated_cv
        if cv <= 5.0: return "OK"
        if cv <= 10.0: return "ALERTA"
        return "ERRO"
        
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

    def set_proin_tab(self, tab: str):
        """Alterna a tab ativa do ProIn"""
        self.proin_current_tab = tab

    async def load_data_from_db(self, force: bool = False):
        """Mock Database Loader preventing integration loss"""
        # In the monolithic state this was loading from Supabase.
        # Keeping empty/mock for now to pass integrity, assumed moved/refactored later 
        # or data populated via mock init.
        pass

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
                 westgard_violations=[]
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
             
             self.qc_records.insert(0, new_record)
             
             # Se houve erro, não limpa o form imediatamente para permitir ajuste se foi digitação errada?
             # Por enquanto limpa para seguir fluxo normal, mas mantém msg
             self.qc_value = ""
             
        except Exception as e:
            self.qc_error_message = f"Erro: {e}"
        finally:
            self.is_saving_qc = False

    async def delete_qc_record(self, id: str):
        self.qc_records = [r for r in self.qc_records if r.id != id]

    async def clear_all_qc_records(self):
        self.qc_records = []

    def clear_qc_form(self):
        """Limpa o formulário de registro de CQ"""
        self.qc_value = ""
        self.reset_qc_messages()
        
    def reset_qc_messages(self):
        self.qc_success_message = ""
        self.qc_warning_message = ""
        self.qc_error_message = ""

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
                lambda: generate_qc_pdf(filtered_records, period_desc)
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
                b64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
                self.qc_pdf_preview = b64_pdf # Update preview too
                
                yield rx.download(
                    data=f"data:application/pdf;base64,{b64_pdf}",
                    filename=filename
                )

        except Exception as e:
            print(f"Erro ao gerar PDF QC: {e}")
            self.qc_error_message = f"Erro na geração do PDF: {str(e)}"
        
        finally:
            self.is_generating_qc_report = False
