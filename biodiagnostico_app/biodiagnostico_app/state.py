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
from .config import Config

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


class State(rx.State):
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
    missing_patients: List[Dict[str, Any]] = []
    missing_exams: List[Dict[str, Any]] = []
    value_divergences: List[Dict[str, Any]] = []
    
    # Breakdown da diferença
    missing_patients_total: float = 0.0
    missing_exams_total: float = 0.0
    divergences_total: float = 0.0
    explained_total: float = 0.0
    residual: float = 0.0
    
    # CSVs gerados
    compulab_csv: str = ""
    simus_csv: str = ""
    csv_generated: bool = False
    
    # Estado de carregamento
    is_loading: bool = False
    is_analyzing: bool = False
    is_generating_csv: bool = False
    is_generating_ai: bool = False
    
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
    openai_api_key: str = Config.OPENAI_API_KEY
    ai_analysis: str = ""
    
    # PDF da análise
    analysis_pdf: str = ""
    
    # Dados armazenados para análise
    _compulab_patients: Dict = {}
    _simus_patients: Dict = {}
    
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
    
    async def load_data_from_db(self):
        """Carrega dados do Supabase para o estado local"""
        if not supabase:
            print("Supabase não configurado. Usando armazenamento em memória.")
            return

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
                ) for r in qc_data
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
                    days_left=0 # Calculado na property
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
    def difference_percent(self) -> float:
        """Percentual de diferença"""
        if self.simus_total > 0:
            return (self.difference / self.simus_total) * 100
        return 0.0
    
    @rx.var
    def missing_exams_count(self) -> int:
        """Quantidade de exames faltantes"""
        return len(self.missing_exams)
    
    @rx.var
    def divergences_count(self) -> int:
        """Quantidade de divergências"""
        return len(self.value_divergences)
    
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
        """Calcula o CV% automaticamente baseado no valor, alvo e desvio padrão"""
        try:
            if not self.qc_value or not self.qc_target_value or not self.qc_target_sd:
                return "0.00"
            
            value = float(self.qc_value.replace(",", "."))
            target = float(self.qc_target_value.replace(",", "."))
            sd = float(self.qc_target_sd.replace(",", "."))
            
            if sd <= 0 or target <= 0:
                return "0.00"
            
            # CV% = (SD / Target) * 100
            cv = (sd / target) * 100
            return f"{cv:.2f}"
        except (ValueError, ZeroDivisionError):
            return "0.00"
    
    @rx.var
    def unique_exam_names(self) -> List[str]:
        """Retorna lista única de nomes de exames para o dropdown"""
        # Lista de exames comuns em laboratório (padronizada)
        return ["DEBUG_TEST_ITEM"]
        
        # Lista de exames comuns em laboratório (padronizada)
        common_exams = [
            "GLICOSE",
            "HEMOGRAMA",
            "CREATININA",
            "UREIA",
            "ACIDO URICO",
            "COLESTEROL TOTAL",
            "COLESTEROL HDL",
            "COLESTEROL LDL",
            "TRIGLICERIDEOS",
            "HEMOGLOBINA GLICOSILADA A1C",
            "TIREOTROFINA (TSH)",
            "TIROXINA LIVRE (T4 LIVRE)",
            "VITAMINA D25",
            "VITAMINA B12",
            "FERRITINA",
            "FERRO SERICO",
            "SODIO",
            "POTASSIO",
            "CALCIO",
            "MAGNESIO",
            "GOT",
            "GPT",
            "GAMA GT",
            "FOSFATASE ALCALINA",
            "BILIRRUBINAS",
            "PROTEINA C REATIVA",
            "V. S. G.",
            "TEMPO DE PROTROMBINA",
            "EXAME QUALITATIVO DE URINA",
            "UROCULTURA",
            "INSULINA",
            "CORTISOL",
            "PROLACTINA",
            "ESTRADIOL",
            "PROGESTERONA",
            "TESTOSTERONA TOTAL",
            "HORMONIO FOLICULO ESTIMULANTE FSH",
            "HORMONIO LUTEINIZANTE LH",
            "ANTIGENO PROSTATICO ESPECIFICO",
        ]
        
        # Combinar e ordenar
        try:
            # Adicionar exames dos registros existentes
            recorded_exams = set()
            if self.qc_records:
                for record in self.qc_records:
                    if record and hasattr(record, "exam_name") and record.exam_name:
                        recorded_exams.add(record.exam_name)
            
            # Adicionar exames dos PDFs analisados (Compulab)
            if self._compulab_patients:
                for patient_data in self._compulab_patients.values():
                    for exam in patient_data.get("exams", []):
                        if exam.get("exam_name"):
                            recorded_exams.add(exam["exam_name"])
                            
            # Adicionar exames dos PDFs analisados (Simus)
            if self._simus_patients:
                for patient_data in self._simus_patients.values():
                    for exam in patient_data.get("exams", []):
                        if exam.get("exam_name"):
                            recorded_exams.add(exam["exam_name"])
                            
            all_exams = set(common_exams) | recorded_exams
            return sorted(list(all_exams))
            
        except Exception as e:
            # Log error for debugging
            try:
                import traceback
                with open("debug_exam_list.txt", "a") as f:
                    f.write(f"Error in unique_exam_names: {str(e)}\n")
                    f.write(traceback.format_exc())
            except:
                pass
            return sorted(common_exams)
    
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
                self.error_message = "❌ COMPULAB: Arquivo está vazio"
                if tmp_file_path and os.path.exists(tmp_file_path):
                    os.unlink(tmp_file_path)
                return
            
            max_size_bytes = self.MAX_FILE_SIZE_MB * 1024 * 1024
            if total_size > max_size_bytes:
                self.error_message = f"❌ COMPULAB: Arquivo muito grande. Máximo: {self.MAX_FILE_SIZE_MB}MB"
                if tmp_file_path and os.path.exists(tmp_file_path):
                    os.unlink(tmp_file_path)
                return
            
            # Validar extensão
            valid_extensions = ['.pdf', '.csv']
            if not any(file.name.lower().endswith(ext) for ext in valid_extensions):
                self.error_message = f"❌ COMPULAB: Tipo de arquivo inválido. Aceitos: PDF, CSV"
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
                print("DEBUG: Erro upload Cloudinary")
                # Não falhar o processo todo se o Cloudinary falhar, mas avisar?
                # Por enquanto segue, pois temos o arquivo local APENAS SE ESTIVERMOS NA MESMA SESSÃO/CONTAINER
            
            # Mensagem com detalhes
            size_str = self.compulab_file_size
            file_type = "PDF" if file.name.lower().endswith('.pdf') else "CSV"
            cloud_status = " (Salvo na nuvem)" if self.compulab_file_url else " (Local)"
            self.success_message = f"✅ COMPULAB carregado: {file.name} ({file_type}, {size_str}){cloud_status}"
            self.processing_status = ""
            
        except Exception as e:
            self.error_message = f"❌ Erro ao carregar COMPULAB: {str(e)}"
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
                self.error_message = "❌ SIMUS: Arquivo está vazio"
                if tmp_file_path and os.path.exists(tmp_file_path):
                    os.unlink(tmp_file_path)
                return
            
            max_size_bytes = self.MAX_FILE_SIZE_MB * 1024 * 1024
            if total_size > max_size_bytes:
                self.error_message = f"❌ SIMUS: Arquivo muito grande. Máximo: {self.MAX_FILE_SIZE_MB}MB"
                if tmp_file_path and os.path.exists(tmp_file_path):
                    os.unlink(tmp_file_path)
                return
            
            # Validar extensão
            valid_extensions = ['.pdf', '.csv']
            if not any(file.name.lower().endswith(ext) for ext in valid_extensions):
                self.error_message = f"❌ SIMUS: Tipo de arquivo inválido. Aceitos: PDF, CSV"
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
                print("DEBUG: Erro upload Cloudinary")
            
            # Mensagem com detalhes
            size_str = self.simus_file_size
            file_type = "PDF" if file.name.lower().endswith('.pdf') else "CSV"
            cloud_status = " (Salvo na nuvem)" if self.simus_file_url else " (Local)"
            self.success_message = f"✅ SIMUS carregado: {file.name} ({file_type}, {size_str}){cloud_status}"
            self.processing_status = ""
            
        except Exception as e:
            self.error_message = f"❌ Erro ao carregar SIMUS: {str(e)}"
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
            self.error_message = "❌ Carregue ambos os arquivos primeiro"
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
                self.success_message = "✅ CSVs gerados com sucesso!"
                yield
            else:
                self.error_message = "❌ Erro ao gerar CSVs. Verifique os arquivos."
                yield
        except Exception as e:
            self.error_message = f"❌ Erro: {str(e)}"
            yield
        finally:
            self.is_generating_csv = False
    
    def _run_pdf_extraction_sync(self, compulab_path: str, simus_path: str, compulab_is_csv: bool = False, simus_is_csv: bool = False, progress_callback=None) -> dict:
        """
        Executa a extração de PDF ou CSV de forma síncrona (chamado em thread separada)
        Usa caminhos de arquivos em vez de bytes para evitar problemas de memória
        Retorna um dict com os resultados ou erro
        
        Args:
            compulab_path: Caminho do arquivo COMPULAB
            simus_path: Caminho do arquivo SIMUS
            compulab_is_csv: True se COMPULAB é CSV
            simus_is_csv: True se SIMUS é CSV
            progress_callback: Função callback(percentage: int, stage: str) para reportar progresso
        """
        from .utils.pdf_processor import extract_compulab_patients, extract_simus_patients, load_from_csv
        
        try:
            # Estágio 1: Processando COMPULAB (0-45%)
            if progress_callback:
                progress_callback(0, "Processando COMPULAB...")
            
            # Processar COMPULAB
            if compulab_is_csv:
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
            
            # Processar SIMUS
            if simus_is_csv:
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
            self.error_message = "❌ Carregue ambos os arquivos primeiro"
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
            
            # Obter caminhos dos arquivos (do disco ou criar temporários dos bytes)
            compulab_path = self.compulab_file_path if (self.compulab_file_path and os.path.exists(self.compulab_file_path)) else None
            simus_path = self.simus_file_path if (self.simus_file_path and os.path.exists(self.simus_file_path)) else None
            
            # Rastrear se criamos arquivos temporários para limpar depois
            created_temp_files = []
            
            # Se não houver caminhos, criar arquivos temporários dos bytes (compatibilidade)
            if not compulab_path and len(self.compulab_file_bytes) > 0:
                suffix = '.csv' if compulab_is_csv else '.pdf'
                mode = 'w' if compulab_is_csv else 'wb'
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
                suffix = '.csv' if simus_is_csv else '.pdf'
                mode = 'w' if simus_is_csv else 'wb'
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
                self.error_message = "❌ Arquivos não encontrados"
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
                self.error_message = f"❌ {result['error']}"
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
                {
                    'patient': item['patient'],
                    'exams_count': item['exams_count'],
                    'total_value': float(item['total_value'])
                }
                for item in comparison_results['missing_patients']
            ]
            
            self.missing_exams = [
                {
                    'patient': item['patient'],
                    'exam_name': item['exam_name'],
                    'value': float(item['value'])
                }
                for item in comparison_results['missing_exams']
            ]
            
            self.value_divergences = [
                {
                    'patient': item['patient'],
                    'exam_name': item['exam_name'],
                    'compulab_value': float(item['compulab_value']),
                    'simus_value': float(item['simus_value']),
                    'difference': float(item['difference']),
                    'compulab_count': item.get('compulab_count', 1),
                    'simus_count': item.get('simus_count', 1)
                }
                for item in comparison_results['value_divergences']
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
            self.success_message = "✅ Análise concluída com sucesso!"
            self.processing_status = ""
            yield
            
            # Limpar arquivos temporários criados (se houver)
            for temp_path in created_temp_files:
                try:
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)
                except:
                    pass
                    
        except Exception as e:
            self.error_message = f"❌ Erro na análise: {str(e)}"
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
    
    def set_api_key(self, key: str):
        """Define a API key do Gemini"""
        self.gemini_api_key = key
    
    async def generate_ai_analysis(self):
        """Gera análise por IA"""
        if not self.gemini_api_key:
            self.error_message = "❌ Configure sua API Key do Gemini primeiro"
            return
        
        if not self.has_analysis:
            self.error_message = "❌ Execute a análise primeiro"
            return
        
        self.is_generating_ai = True
        self.error_message = ""
        
        try:
            from .utils.ai_analysis import generate_ai_analysis
            
            comparison_results = {
                'missing_patients': self.missing_patients,
                'missing_exams': self.missing_exams,
                'value_divergences': self.value_divergences
            }
            
            breakdown = {
                'missing_patients_total': self.missing_patients_total,
                'missing_exams_total': self.missing_exams_total,
                'divergences_total': self.divergences_total,
                'explained_total': self.explained_total,
                'residual': self.residual
            }
            
            analysis, error = generate_ai_analysis(
                Decimal(str(self.compulab_total)),
                Decimal(str(self.simus_total)),
                self.compulab_count,
                self.simus_count,
                comparison_results,
                breakdown,
                self.gemini_api_key
            )
            
            if error:
                self.error_message = f"❌ {error}"
            else:
                self.ai_analysis = analysis
                self.success_message = "✅ Análise por IA gerada!"
                
        except Exception as e:
            self.error_message = f"❌ Erro: {str(e)}"
        finally:
            self.is_generating_ai = False
    
    def generate_pdf_report(self):
        """Gera PDF da análise e armazena no state"""
        if not self.has_analysis:
            self.error_message = "❌ Execute a análise primeiro"
            self.success_message = ""
            return
        
        self.error_message = ""
        self.success_message = "⏳ Gerando PDF..."
        
        try:
            # Verificar se reportlab está instalado
            try:
                import reportlab
            except ImportError:
                self.error_message = "❌ Biblioteca reportlab não está instalada. Execute: pip install reportlab"
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
                self.error_message = "❌ Erro: PDF gerado está vazio"
                self.success_message = ""
                return
            
            # Converter para base64
            pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
            
            # Armazenar data URI para download
            self.analysis_pdf = f"data:application/pdf;base64,{pdf_base64}"
            self.success_message = "✅ PDF gerado com sucesso! Clique em 'Download PDF' para baixar."
            
        except ImportError as e:
            self.error_message = f"❌ Erro ao importar bibliotecas: {str(e)}. Execute: pip install reportlab"
            self.success_message = ""
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            self.error_message = f"❌ Erro ao gerar PDF: {str(e)}"
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
    
    # ===== ProIn - Métodos para Análise de Planilhas Excel =====
    
    async def handle_excel_upload(self, files: List[rx.UploadFile]):
        """Processa upload do arquivo Excel"""
        if not files:
            return
        
        file = files[0]
        self.excel_file_name = file.name
        self.excel_file_bytes = await file.read()
        self.excel_success_message = f"Arquivo carregado: {file.name}"
        self.excel_error_message = ""
        self.excel_analyzed = False
    
    async def analyze_excel(self):
        """Analisa o arquivo Excel carregado"""
        if not self.has_excel_file:
            self.excel_error_message = "Carregue um arquivo Excel primeiro"
            return
        
        self.is_analyzing_excel = True
        self.excel_error_message = ""
        self.excel_success_message = ""
        
        try:
            import pandas as pd
            import io
            
            # Ler o arquivo Excel
            excel_io = io.BytesIO(self.excel_file_bytes)
            df = pd.read_excel(excel_io)
            self._excel_dataframe = df
            
            # Estatísticas básicas
            self.excel_total_rows = len(df)
            self.excel_total_columns = len(df.columns)
            total_cells = self.excel_total_rows * self.excel_total_columns
            self.excel_filled_cells = int(df.count().sum())
            self.excel_empty_cells = total_cells - self.excel_filled_cells
            
            # Headers
            self.excel_headers = [str(col) for col in df.columns.tolist()]
            
            # Análise por coluna
            columns_info = []
            for col in df.columns:
                col_data = df[col]
                fill_rate = round((col_data.count() / len(df)) * 100, 1)
                
                # Determinar tipo
                if pd.api.types.is_numeric_dtype(col_data):
                    col_type = "Numérico"
                elif pd.api.types.is_datetime64_any_dtype(col_data):
                    col_type = "Data"
                else:
                    col_type = "Texto"
                
                columns_info.append({
                    "name": str(col),
                    "type": col_type,
                    "fill_rate": str(fill_rate)
                })
            
            self.excel_columns_info = columns_info
            
            # Resumo numérico
            numeric_summary = []
            numeric_cols = df.select_dtypes(include=['number']).columns
            for col in numeric_cols:
                col_data = df[col].dropna()
                if len(col_data) > 0:
                    numeric_summary.append({
                        "column": str(col),
                        "sum": f"{col_data.sum():,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                        "mean": f"{col_data.mean():,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                        "min": f"{col_data.min():,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                        "max": f"{col_data.max():,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    })
            
            self.excel_numeric_summary = numeric_summary
            
            # Preview (primeiras 10 linhas)
            preview_df = df.head(10)
            preview_data = []
            for _, row in preview_df.iterrows():
                row_data = [str(val) if pd.notna(val) else "" for val in row.tolist()]
                preview_data.append(row_data)
            
            self.excel_preview = preview_data
            
            self.excel_analyzed = True
            self.excel_success_message = f"Análise concluída! {self.excel_total_rows} linhas e {self.excel_total_columns} colunas encontradas."
            
        except Exception as e:
            self.excel_error_message = f"Erro ao analisar arquivo: {str(e)}"
        finally:
            self.is_analyzing_excel = False
    
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
    def qc_records_today(self) -> List[Dict[str, Any]]:
        """Registros de CQ do dia atual"""
        today = datetime.now().strftime("%Y-%m-%d")
        return [r for r in self.qc_records if r.get("date", "").startswith(today)]
    
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
            except:
                self.qc_error_message = "Valores inválidos"
                return
            
            # Calcular CV% = (SD / Target) * 100
            cv = (sd / target) * 100 if target > 0 else 0.0
            
            # Status baseado no CV
            status = "OK" if cv <= 5.0 else "Atenção"
            
            # Criar registro
            record = QCRecord(
                id=str(len(self.qc_records) + 1),
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
                status=status
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
        if supabase:
            success = await QCService.delete_qc_record(record_id)
            if success:
                await self.load_data_from_db()
                self.qc_success_message = "Registro removido do banco"
            else:
                self.qc_error_message = "Falha ao remover registro"
        else:
            self.qc_records = [r for r in self.qc_records if r.id != record_id]
            self.qc_success_message = "Registro removido"
    
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
                    "storage_temp": self.reagent_storage_temp
                }
                await ReagentService.create_reagent_lot(lot_data)
                await self.load_data_from_db()
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
            
        except Exception as e:
            self.reagent_error_message = f"Erro ao salvar: {str(e)}"
        finally:
            self.is_saving_reagent = False
    
    async def delete_reagent_lot(self, lot_id: str):
        """Remove um lote de reagente"""
        if supabase:
            success = await ReagentService.delete_reagent_lot(lot_id)
            if success:
                await self.load_data_from_db()
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
                await self.load_data_from_db()
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
                await self.load_data_from_db()
                self.maintenance_success_message = "Registro removido do banco"
            else:
                self.maintenance_error_message = "Falha ao remover registro"
        else:
            self.maintenance_records = [r for r in self.maintenance_records if r.id != record_id]
            self.maintenance_success_message = "Registro removido"
    
    def set_levey_jennings_exam(self, value: str):
        self.levey_jennings_exam = value
        self._update_levey_jennings_data()
    
    def set_levey_jennings_period(self, value: str):
        self.levey_jennings_period = value
        self._update_levey_jennings_data()
    
    def _update_levey_jennings_data(self):
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
    
    @rx.var
    def unique_exam_names(self) -> List[str]:
        """Lista de nomes de exames únicos nos registros"""
        names = set()
        for r in self.qc_records:
            if r.exam_name:
                names.add(r.exam_name)
        return sorted(list(names))
    
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
    
    async def import_excel_to_qc(self):
        """Importa dados do Excel para registros de CQ"""
        if not self.has_excel_file or not self.excel_analyzed:
            self.excel_error_message = "Analise um arquivo Excel primeiro"
            return
        
        self.is_analyzing_excel = True
        self.excel_error_message = ""
        
        try:
            import pandas as pd
            import io
            
            excel_io = io.BytesIO(self.excel_file_bytes)
            df = pd.read_excel(excel_io)
            
            imported_count = 0
            
            # Tentar identificar colunas relevantes
            cols_lower = {str(c).lower(): c for c in df.columns}
            
            # Mapear possíveis nomes de colunas
            exam_col = None
            value_col = None
            date_col = None
            
            for key, col in cols_lower.items():
                if any(x in key for x in ["exame", "exam", "analito", "teste"]):
                    exam_col = col
                elif any(x in key for x in ["valor", "value", "resultado", "result"]):
                    value_col = col
                elif any(x in key for x in ["data", "date", "dia"]):
                    date_col = col
            
            if exam_col and value_col:
                for _, row in df.iterrows():
                    try:
                        exam_name = str(row[exam_col]) if pd.notna(row[exam_col]) else ""
                        value = float(row[value_col]) if pd.notna(row[value_col]) else 0
                        date = str(row[date_col])[:10] if date_col and pd.notna(row.get(date_col)) else datetime.now().strftime("%Y-%m-%d")
                        
                        if exam_name and value > 0:
                            record = QCRecord(
                                id=str(len(self.qc_records) + imported_count + 1),
                                date=date,
                                exam_name=exam_name,
                                level="Normal",
                                lot_number="",
                                value1=value,
                                value2=value,
                                mean=value,
                                sd=0,
                                cv=0,
                                target_value=0,
                                target_sd=0,
                                equipment="",
                                analyst="Importado",
                                status="Importado"
                            )
                            self.qc_records = self.qc_records + [record]
                            imported_count += 1
                    except:
                        continue
                
                self.excel_success_message = f"Importados {imported_count} registros para o CQ!"
            else:
                self.excel_error_message = "Não foi possível identificar colunas de exame e valor na planilha"
                
        except Exception as e:
            self.excel_error_message = f"Erro na importação: {str(e)}"
        finally:
            self.is_analyzing_excel = False

