import reflex as rx
from typing import List, Dict, Any, Optional
import asyncio
import os
import tempfile
import base64
import gc
from concurrent.futures import ThreadPoolExecutor
from ..services.cloudinary_service import CloudinaryService
from ..services.audit_service import AuditService
from ..models import AnalysisResult, PatientHistoryEntry, PatientModel, TopOffender
from ..utils import pdf_processor # Import module to access functions dynamically
from .qc_state import QCState

# Cloudinary Service Instance
cloudinary_service = CloudinaryService()

class AnalysisState(QCState):
    """Estado responsável pela análise comparativa e upload de arquivos"""
    
    # Internal Data (Backend Only)
    _compulab_patients: Dict[str, Any] = {}
    _simus_patients: Dict[str, Any] = {}
    audit_history: List[Dict[str, Any]] = []
    
    # Upload State
    compulab_file_name: str = ""
    compulab_file_path: str = ""
    compulab_file_url: str = ""
    compulab_file_bytes: bytes = b""
    compulab_file_size_bytes: int = 0
    
    simus_file_name: str = ""
    simus_file_path: str = ""
    simus_file_url: str = ""
    simus_file_bytes: bytes = b""
    simus_file_size_bytes: int = 0
    
    is_uploading: bool = False
    processing_status: str = ""
    MAX_FILE_SIZE_MB: int = 50
    
    # Progresso do processamento (para arquivos grandes)
    processing_progress: int = 0
    processing_total: int = 0
    is_large_file_processing: bool = False
    processing_progress_text: str = ""
    ai_loading_progress: int = 0
    
    # Progresso da conversão CSV
    csv_progress_percentage: int = 0
    csv_stage: str = ""
    is_generating_csv: bool = False
    
    # Progresso da análise
    analysis_progress_percentage: int = 0
    analysis_stage: str = ""
    is_analyzing: bool = False
    
    # Mensagens
    error_message: str = ""
    success_message: str = ""
    
    # Analysis Results (Objects)
    missing_patients: List[AnalysisResult] = []
    missing_exams: List[AnalysisResult] = []
    value_divergences: List[AnalysisResult] = []
    extra_simus_exams: List[AnalysisResult] = []
    
    # Analysis Stats - Attributes with Defaults
    missing_patients_count: int = 0
    missing_patients_total: float = 0.0
    missing_exams_count: int = 0
    missing_exams_total: float = 0.0
    divergences_count: int = 0
    divergences_total: float = 0.0
    extra_simus_exams_count: int = 0
    compulab_total: float = 0.0
    simus_total: float = 0.0
    
    # CSVs gerados
    compulab_csv: str = ""
    simus_csv: str = ""
    csv_generated: bool = False
    
    # PDF da análise
    analysis_pdf: str = ""
    
    # Divergence Resolution & Patient History
    resolutions: Dict[str, str] = {} # Key: "patient_name|exam_name"
    patient_history_data: List[PatientHistoryEntry] = []
    patient_history_search: str = ""
    selected_patient_name: str = ""
    is_showing_patient_history: bool = False
    resolution_notes: str = ""
    analysis_active_tab: str = "patients_missing"

    def set_analysis_active_tab(self, val: Any):
        self.analysis_active_tab = val

    def set_is_showing_patient_history(self, val: bool):
        self.is_showing_patient_history = val
        
    def set_patient_history_search(self, val: str):
        self.patient_history_search = val

    # Computed Properties
    # Computed Properties needed for UI
    @rx.var
    def has_files(self) -> bool:
        """Verifica se ambos os arquivos foram carregados"""
        return bool(self.compulab_file_path and self.simus_file_path)

    @rx.var
    def compulab_file_size(self) -> str:
        """Tamanho formatado do arquivo Compulab"""
        if self.compulab_file_size_bytes == 0: return ""
        mb = self.compulab_file_size_bytes / (1024 * 1024)
        if mb < 1:
            kb = self.compulab_file_size_bytes / 1024
            return f"{kb:.1f} KB"
        return f"{mb:.1f} MB"
        
    @rx.var
    def simus_file_size(self) -> str:
        """Tamanho formatado do arquivo Simus"""
        if self.simus_file_size_bytes == 0: return ""
        mb = self.simus_file_size_bytes / (1024 * 1024)
        if mb < 1:
            kb = self.simus_file_size_bytes / 1024
            return f"{kb:.1f} KB"
        return f"{mb:.1f} MB"

    @rx.var
    def compulab_count(self) -> int:
        return len(self._compulab_patients)

    @rx.var
    def simus_count(self) -> int:
        return len(self._simus_patients)

    @rx.var
    def formatted_compulab_total(self) -> str:
        return f"R$ {self.compulab_total:,.2f}"

    @rx.var
    def formatted_simus_total(self) -> str:
        return f"R$ {self.simus_total:,.2f}"

    @rx.var
    def formatted_difference(self) -> str:
        diff = self.compulab_total - self.simus_total
        return f"R$ {diff:,.2f}"

    @rx.var
    def formatted_missing_patients_total(self) -> str:
        return f"R$ {self.missing_patients_total:,.2f}"

    @rx.var
    def formatted_missing_exams_total(self) -> str:
        return f"R$ {self.missing_exams_total:,.2f}"

    @rx.var
    def formatted_divergences_total(self) -> str:
        return f"R$ {self.divergences_total:,.2f}"
    
    @rx.var
    def explained_total(self) -> float:
        """Total explicado pelas divergências encontradas"""
        extras = sum(
            float(item.get('simus_value', 0) or item.get('value', 0)) 
            for item in self.extra_simus_exams
        ) if isinstance(self.extra_simus_exams, list) else 0
        return self.missing_patients_total + self.missing_exams_total + self.divergences_total + extras

    @rx.var
    def residual(self) -> float:
        """Diferença não explicada"""
        real_diff = self.compulab_total - self.simus_total
        return real_diff - self.explained_total

    @rx.var
    def top_offenders(self) -> List[TopOffender]:
        """Retorna os top 5 exames com mais problemas (usado no Dashboard)"""
        counts = {}
        # Contar ocorrências em missing_exams e value_divergences
        for item in self.missing_exams:
            name = item.get("exam_name", "") if isinstance(item, dict) else getattr(item, "exam_name", "")
            if name:
                counts[name] = counts.get(name, 0) + 1
                
        for item in self.value_divergences:
            name = item.get("exam_name", "") if isinstance(item, dict) else getattr(item, "exam_name", "")
            if name:
                counts[name] = counts.get(name, 0) + 1
                
        sorted_exams = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:5]
        return [TopOffender(name=str(name), count=int(count)) for name, count in sorted_exams]

    # Patient History & Actions
    @rx.var
    def selected_patient_id(self) -> str:
        if self.patient_history_data:
            return self.patient_history_data[0].id[:8].upper()
        return "---"

    @rx.var
    def selected_patient_total_value(self) -> str:
        total = sum(item.last_value for item in self.patient_history_data)
        return f"{total:,.2f}"

    @rx.var
    def selected_patient_exams_count(self) -> int:
        return len(self.patient_history_data)
        
    @rx.var
    def resolution_progress(self) -> int:
        """Percentual de divergências resolvidas na análise atual"""
        total = len(self.missing_exams) + len(self.value_divergences) + len(self.extra_simus_exams)
        if total == 0: return 100
        resolved_count = 0
        all_items = self.missing_exams + self.value_divergences + self.extra_simus_exams
        for item in all_items:
            # Handle both dict and object (pydantic)
            patient = item.get('patient', '') if isinstance(item, dict) else getattr(item, 'patient', '')
            exam = item.get('exam_name', '') if isinstance(item, dict) else getattr(item, 'exam_name', '')
            if self.resolutions.get(f"{patient}|{exam}") == "resolvido":
                resolved_count += 1
        return int((resolved_count / total) * 100)

    def view_patient_history(self, patient_name: str):
        """Mock: Carrega histórico do paciente"""
        self.selected_patient_name = patient_name
        self.is_showing_patient_history = True
        # Em produção, buscaria no banco real
        self.patient_history_data = [
            PatientHistoryEntry(id="123", date="2024-01-01", exam="HEMOGRAMA", last_value=0.0, trend="stable")
        ]

    def toggle_resolution(self, key: str):
        """Marca/Desmarca item como resolvido"""
        current = self.resolutions.get(key, "")
        self.resolutions[key] = "resolvido" if current != "resolvido" else ""
    
    async def run_analysis(self):
        """Executa a análise comparativa"""
        self.is_analyzing = True
        self.analysis_stage = "Iniciando análise..."
        yield
        try:
            # Mock analysis logic from original state
            # Ensure attributes are set so UI doesn't crash
            self.missing_patients_count = 5
            self.missing_patients_total = 1500.00
            self.missing_exams_count = 12
            self.missing_exams_total = 450.00
            self.divergences_count = 3
            self.divergences_total = 120.50
            self.compulab_total = 50000.00
            self.simus_total = 48000.00
            
            # Populate lists with dummy data if empty to prevent UI glitches
            if not self.missing_patients:
                self.missing_patients = [
                    AnalysisResult(patient="Paciente Teste", exam_name="Checkup", value=300.0)
                ]
            
            self.analysis_progress_percentage = 100
            self.analysis_stage = "Concluído"
        finally:
            self.is_analyzing = False
            
    async def generate_ai_analysis(self):
        """Gera análise via AIState (Delegation)"""
        # Como AIState é um mixin irmão, podemos chamar seus métodos se herdados juntos
        # Mas aqui self é AnalysisState. Em runtime, self será State(AnalysisState, AIState)
        if hasattr(self, 'run_ai_analysis'):
            await self.run_ai_analysis()
            
    async def generate_pdf_report(self):
        """Gera relatório PDF da análise"""
        # Placeholder
        pass

    # ===== UPLOAD HANDLERS =====

    async def handle_compulab_upload(self, files: List[rx.UploadFile]):
        """Processa upload do arquivo COMPULAB - Salva em disco para evitar travamento"""
        print(f"DEBUG: Iniciando upload COMPULAB. Files: {len(files) if files else 0}")
        if not files:
            print("DEBUG: Nenhum arquivo recebido")
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
        self.csv_generated = False
        self.compulab_csv = ""
    
    def clear_simus_file(self):
        """Remove o arquivo SIMUS"""
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
        self.csv_generated = False
        self.simus_csv = ""
    
    def clear_all_files(self):
        """Remove todos os arquivos"""
        self.clear_compulab_file()
        self.clear_simus_file()
        self.clear_analysis() # Assume this exists inside a generic cleanup in AnalysisState

    def clear_analysis(self):
        """Limpa resultados da análise"""
        self.missing_patients = []
        self.missing_exams = []
        self.value_divergences = []
        self.extra_simus_exams = []
        self.missing_patients_count = 0
        self.missing_exams_count = 0
        self.divergences_count = 0
        self.extra_simus_exams_count = 0
        self.analysis_progress_percentage = 0
        self.analysis_stage = ""
        self.is_analyzing = False

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
            from .utils.pdf_processor import generate_excel_from_pdfs
            
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
            
            with ThreadPoolExecutor() as executor:
                future = executor.submit(
                    generate_excel_from_pdfs,
                    compulab_bytes,
                    simus_bytes,
                    update_progress
                )
                
                while not future.done():
                    self.csv_progress_percentage = progress_state["percentage"]
                    self.csv_stage = progress_state["stage"]
                    yield
                    await asyncio.sleep(0.2)
                
                compulab_csv, simus_csv, success = future.result()
                
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
