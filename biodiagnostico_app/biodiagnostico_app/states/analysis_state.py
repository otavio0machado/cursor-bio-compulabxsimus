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
from ..utils.analysis_pdf_report import generate_analysis_pdf
from .qc_state import QCState
from ..styles import Color

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
    pdf_preview_b64: str = "" # Base64 for Split View Preview
    
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
    def has_analysis(self) -> bool:
        """Verifica se há análise disponível (REATIVO - usa acesso direto)"""
        result = self.compulab_total > 0 or self.simus_total > 0
        print(f"DEBUG has_analysis (AnalysisState): compulab={self.compulab_total}, simus={self.simus_total}, result={result}")
        return result

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
            float(getattr(item, 'simus_value', 0) or getattr(item, 'value', 0)) 
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
    def formatted_total_leakage(self) -> str:
        """Total de perda financeira identificada"""
        total = self.missing_patients_total + self.missing_exams_total + self.divergences_total
        return f"R$ {total:,.2f}"

    @rx.var
    def revenue_distribution_data(self) -> List[Dict[str, Any]]:
        """Dados para o gráfico de pizza de distribuição de receita/perda"""
        return [
            {"name": "Pacientes Faltantes", "value": float(self.missing_patients_total), "fill": Color.WARNING},
            {"name": "Exames Faltantes", "value": float(self.missing_exams_total), "fill": Color.ERROR},
            {"name": "Divergência Valores", "value": float(self.divergences_total), "fill": Color.PRIMARY},
        ]
        
    @rx.var
    def top_exams_discrepancy_data(self) -> List[Dict[str, Any]]:
        """Dados para o gráfico de barras dos top exames com problemas"""
        # Convert TopOffender objects to dict for Recharts
        return [
            {"name": item.name, "value": item.count} 
            for item in self.top_offenders
        ]

    @rx.var
    def action_center_insights(self) -> List[Dict[str, str]]:
        """Gera insights acionáveis baseados nos dados"""
        insights = []
        
        # Insight 1: Maior ofensor
        if self.missing_patients_total > self.missing_exams_total and self.missing_patients_total > self.divergences_total:
            insights.append({
                "icon": "users", "title": "Foco em Recepção", 
                "description": f"Pacientes não lançados representam a maior perda (R$ {self.missing_patients_total:,.2f}). Verifique processos de cadastro."
            })
        elif self.missing_exams_total > 0:
            insights.append({
                 "icon": "file-warning", "title": "Auditoria de Lançamento",
                 "description": f"Exames esquecidos somam R$ {self.missing_exams_total:,.2f}. Treinamento de equipe sugerido."
            })
            
        # Insight 2: Divergencias
        if self.divergences_count > 5:
             insights.append({
                 "icon": "git-compare", "title": "Revisão de Tabela de Preços",
                 "description": f"Detectadas {self.divergences_count} divergências de valor. Possível inconsistência cadastral entre sistemas."
             })
             
        # Insight 3: Default se vazio
        if not insights:
            insights.append({
                "icon": "circle-check", "title": "Tudo parece em ordem", 
                "description": "Nenhuma anomalia grave detectada na análise preliminar."
            })
            
        return insights

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
        """Mock: Carrega histórico do paciente com dados formatados corretamente"""
        self.selected_patient_name = patient_name
        self.is_showing_patient_history = True
        
        # Simular busca no banco com os campos corretos do model PatientHistoryEntry
        self.patient_history_data = [
            PatientHistoryEntry(
                id="PAT-10892", 
                patient_name=patient_name,
                exam_name="HEMOGRAMA COMPLETO", 
                status="Divergente",
                last_value=45.90, 
                notes="Diferença de arredondamento em glóbulos brancos",
                created_at="21/01/2026"
            ),
            PatientHistoryEntry(
                id="PAT-10850", 
                patient_name=patient_name,
                exam_name="GLICEMIA EM JEJUM", 
                status="Normal",
                last_value=22.40, 
                notes="",
                created_at="15/01/2026"
            ),
            PatientHistoryEntry(
                id="PAT-10700", 
                patient_name=patient_name,
                exam_name="CREATININA", 
                status="Normal",
                last_value=12.00, 
                notes="",
                created_at="10/12/2025"
            )
        ]

    async def toggle_resolution(self, patient: str, exam: str):
        """Marca/Desmarca item como resolvido e atualiza PDF"""
        key = f"{patient}|{exam}"
        current = self.resolutions.get(key, "")
        self.resolutions[key] = "resolvido" if current != "resolvido" else ""
        yield
        # Regenerar PDF para refletir mudanças
        await self.generate_pdf_report()
    
    async def run_analysis(self):
        """Executa a análise comparativa REAL baseada nos arquivos carregados"""
        print("DEBUG: run_analysis STARTED - REAL ANALYSIS")
        self.is_analyzing = True
        self.analysis_stage = "Iniciando análise..."
        self.error_message = ""
        yield
        
        try:
            # Importar funções de processamento
            from ..utils.pdf_processor import load_from_excel, exam_names_match
            from decimal import Decimal
            import requests
            import io
            
            # Verificar se os arquivos estão disponíveis (via URL ou path)
            compulab_data = None
            simus_data = None
            
            self.analysis_stage = "Carregando arquivo COMPULAB..."
            self.analysis_progress_percentage = 10
            yield
            
            # Carregar COMPULAB
            if self.compulab_file_path and os.path.exists(self.compulab_file_path):
                print(f"DEBUG: Carregando COMPULAB de arquivo local: {self.compulab_file_path}")
                compulab_patients, compulab_total_val = load_from_excel(self.compulab_file_path)
            elif self.compulab_file_url:
                print(f"DEBUG: Carregando COMPULAB de URL: {self.compulab_file_url}")
                response = requests.get(self.compulab_file_url)
                if response.status_code == 200:
                    compulab_patients, compulab_total_val = load_from_excel(response.content)
                else:
                    raise Exception(f"Erro ao baixar COMPULAB: HTTP {response.status_code}")
            else:
                raise Exception("Arquivo COMPULAB não disponível")
            
            if compulab_patients is None:
                raise Exception("Falha ao processar arquivo COMPULAB")
            
            self.analysis_stage = "Carregando arquivo SIMUS..."
            self.analysis_progress_percentage = 30
            yield
            
            # Carregar SIMUS
            if self.simus_file_path and os.path.exists(self.simus_file_path):
                print(f"DEBUG: Carregando SIMUS de arquivo local: {self.simus_file_path}")
                simus_patients, simus_total_val = load_from_excel(self.simus_file_path)
            elif self.simus_file_url:
                print(f"DEBUG: Carregando SIMUS de URL: {self.simus_file_url}")
                response = requests.get(self.simus_file_url)
                if response.status_code == 200:
                    simus_patients, simus_total_val = load_from_excel(response.content)
                else:
                    raise Exception(f"Erro ao baixar SIMUS: HTTP {response.status_code}")
            else:
                raise Exception("Arquivo SIMUS não disponível")
            
            if simus_patients is None:
                raise Exception("Falha ao processar arquivo SIMUS")
            
            print(f"DEBUG: COMPULAB: {len(compulab_patients)} pacientes, Total: {compulab_total_val}")
            print(f"DEBUG: SIMUS: {len(simus_patients)} pacientes, Total: {simus_total_val}")
            
            self.analysis_stage = "Comparando dados..."
            self.analysis_progress_percentage = 50
            yield
            
            # Atualizar totais
            self.compulab_total = float(compulab_total_val or 0)
            self.simus_total = float(simus_total_val or 0)
            
            # Armazenar dados internos para comparação
            self._compulab_patients = dict(compulab_patients)
            self._simus_patients = dict(simus_patients)
            
            # Listas de resultados
            missing_patients_list = []
            missing_exams_list = []
            value_divergences_list = []
            extra_simus_list = []
            
            # ANÁLISE 1: Pacientes no COMPULAB que não estão no SIMUS
            compulab_patient_names = set(compulab_patients.keys())
            simus_patient_names = set(simus_patients.keys())
            
            patients_only_in_compulab = compulab_patient_names - simus_patient_names
            for patient_name in patients_only_in_compulab:
                patient_data = compulab_patients[patient_name]
                total_val = float(patient_data['total'])
                exams_count = len(patient_data['exams'])
                missing_patients_list.append(AnalysisResult(
                    patient=patient_name,
                    exam_name=f"{exams_count} exame(s)",
                    value=total_val,
                    exams_count=exams_count,
                    total_value=total_val
                ))
            
            self.analysis_stage = "Analisando exames..."
            self.analysis_progress_percentage = 70
            yield
            
            # ANÁLISE 2: Para cada paciente comum, verificar exames faltantes e divergências
            common_patients = compulab_patient_names & simus_patient_names
            for patient_name in common_patients:
                compulab_exams = compulab_patients[patient_name]['exams']
                simus_exams = simus_patients[patient_name]['exams']
                
                # Indexar exames SIMUS por nome normalizado
                simus_exam_map = {}
                for exam in simus_exams:
                    exam_key = exam['exam_name'].upper().strip()
                    if exam_key not in simus_exam_map:
                        simus_exam_map[exam_key] = []
                    simus_exam_map[exam_key].append(exam)
                
                # Verificar cada exame COMPULAB
                for comp_exam in compulab_exams:
                    comp_name = comp_exam['exam_name'].upper().strip()
                    comp_value = float(comp_exam['value'])
                    
                    # Procurar exame correspondente no SIMUS
                    found_match = False
                    matched_simus_exam = None
                    
                    for simus_key, simus_exam_list in simus_exam_map.items():
                        if exam_names_match(comp_name, simus_key):
                            for simus_exam in simus_exam_list:
                                if not simus_exam.get('_matched'):
                                    matched_simus_exam = simus_exam
                                    found_match = True
                                    simus_exam['_matched'] = True
                                    break
                            if found_match:
                                break
                    
                    if not found_match:
                        # Exame faltante no SIMUS
                        missing_exams_list.append(AnalysisResult(
                            patient=patient_name,
                            exam_name=comp_exam['exam_name'],
                            value=comp_value,
                            compulab_value=comp_value
                        ))
                    elif matched_simus_exam:
                        # Verificar divergência de valor
                        simus_value = float(matched_simus_exam['value'])
                        diff = abs(comp_value - simus_value)
                        if diff > 0.01:  # Tolerância de 1 centavo
                            value_divergences_list.append(AnalysisResult(
                                patient=patient_name,
                                exam_name=comp_exam['exam_name'],
                                compulab_value=comp_value,
                                simus_value=simus_value,
                                difference=comp_value - simus_value
                            ))
            
            # ANÁLISE 3: Exames no SIMUS que não estão no COMPULAB (exames "fantasma")
            for patient_name in common_patients:
                simus_exams = simus_patients[patient_name]['exams']
                for simus_exam in simus_exams:
                    if not simus_exam.get('_matched'):
                        extra_simus_list.append(AnalysisResult(
                            patient=patient_name,
                            exam_name=simus_exam['exam_name'],
                            simus_value=float(simus_exam['value'])
                        ))
            
            # Também verificar pacientes somente no SIMUS
            patients_only_in_simus = simus_patient_names - compulab_patient_names
            for patient_name in patients_only_in_simus:
                patient_data = simus_patients[patient_name]
                for exam in patient_data['exams']:
                    extra_simus_list.append(AnalysisResult(
                        patient=patient_name,
                        exam_name=exam['exam_name'],
                        simus_value=float(exam['value'])
                    ))
            
            # Atualizar estados com resultados
            self.missing_patients = missing_patients_list
            self.missing_exams = missing_exams_list
            self.value_divergences = value_divergences_list
            self.extra_simus_exams = extra_simus_list
            
            # Calcular totais
            self.missing_patients_count = len(missing_patients_list)
            self.missing_patients_total = sum(r.value for r in missing_patients_list)
            self.missing_exams_count = len(missing_exams_list)
            self.missing_exams_total = sum(r.compulab_value for r in missing_exams_list)
            self.divergences_count = len(value_divergences_list)
            self.divergences_total = sum(abs(r.difference) for r in value_divergences_list)
            self.extra_simus_exams_count = len(extra_simus_list)
            
            self.analysis_progress_percentage = 100
            self.analysis_stage = "Concluído"
            
            print(f"DEBUG: Análise concluída!")
            print(f"  - Pacientes faltantes: {self.missing_patients_count}")
            print(f"  - Exames faltantes: {self.missing_exams_count}")
            print(f"  - Divergências: {self.divergences_count}")
            print(f"  - Exames fantasma: {self.extra_simus_exams_count}")
            
            yield  # Propagate state to frontend
            
            yield  # Propagate state to frontend
            
        except Exception as e:
            print(f"DEBUG: run_analysis EXCEPTION: {e}")
            import traceback
            traceback.print_exc()
            self.error_message = f"Erro na análise: {str(e)}"
            self.analysis_stage = "Erro"
            yield
        finally:
            self.is_analyzing = False
            print("DEBUG: run_analysis FINISHED")
            yield
            # Gerar preview do PDF automaticamente após análise
            if not self.error_message:
                await self.generate_pdf_report()
            
    # generate_ai_analysis foi movido para AIState
            
    async def generate_pdf_report(self):
        """Gera relatório PDF da análise para preview e download"""
        if not self.has_analysis:
            return
            
        try:
             # Filtrar itens resolvidos para o relatório
            def is_resolved(item):
                p = getattr(item, 'patient', '') or item.get('patient', '')
                e = getattr(item, 'exam_name', '') or item.get('exam_name', '')
                return self.resolutions.get(f"{p}|{e}") == "resolvido"

            filtered_missing = [x for x in self.missing_exams if not is_resolved(x)]
            filtered_divergences = [x for x in self.value_divergences if not is_resolved(x)]
            filtered_extras = [x for x in self.extra_simus_exams if not is_resolved(x)]
            
             # Executar em thread pool para não bloquear
            loop = asyncio.get_event_loop()
            pdf_bytes = await loop.run_in_executor(
                None,
                lambda: generate_analysis_pdf(
                    self.compulab_total,
                    self.simus_total,
                    self.missing_patients, # Pacientes faltantes não têm resolução individual por exame aqui
                    filtered_missing,
                    filtered_divergences,
                    filtered_extras,
                    self.top_offenders
                )
            )
            
            self.pdf_preview_b64 = base64.b64encode(pdf_bytes).decode('utf-8')
            # self.analysis_pdf = ... (Upload logic if needed later)
            print("DEBUG: PDF Preview Generated")
            
        except Exception as e:
            print(f"Erro ao gerar PDF: {e}")
            self.error_message = f"Erro ao gerar PDF: {str(e)}"

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
            from ..utils.pdf_processor import generate_excel_from_pdfs
            
            # Variável compartilhada para armazenar progresso (thread-safe)
            progress_state = {"percentage": 0, "stage": ""}
            
            # Callback para atualizar progresso
            def update_progress(percentage: int, stage: str):
                progress_state["percentage"] = percentage
                progress_state["stage"] = stage
            
            # Ler arquivos do disco se existirem, senão usar bytes (compatibilidade)
            compulab_bytes = b""
            simus_bytes = b""
            
            # DEBUG: Log para diagnóstico
            print(f"DEBUG generate_csvs: compulab_file_path='{self.compulab_file_path}'")
            print(f"DEBUG generate_csvs: simus_file_path='{self.simus_file_path}'")
            print(f"DEBUG generate_csvs: compulab_file_path exists={os.path.exists(self.compulab_file_path) if self.compulab_file_path else 'N/A'}")
            print(f"DEBUG generate_csvs: simus_file_path exists={os.path.exists(self.simus_file_path) if self.simus_file_path else 'N/A'}")
            
            if self.compulab_file_path and os.path.exists(self.compulab_file_path):
                with open(self.compulab_file_path, 'rb') as f:
                    compulab_bytes = f.read()
                print(f"DEBUG generate_csvs: compulab_bytes lidos do disco, tamanho={len(compulab_bytes)} bytes")
            else:
                compulab_bytes = self.compulab_file_bytes
                print(f"DEBUG generate_csvs: usando compulab_file_bytes em memória, tamanho={len(compulab_bytes)} bytes")
            
            if self.simus_file_path and os.path.exists(self.simus_file_path):
                with open(self.simus_file_path, 'rb') as f:
                    simus_bytes = f.read()
                print(f"DEBUG generate_csvs: simus_bytes lidos do disco, tamanho={len(simus_bytes)} bytes")
            else:
                simus_bytes = self.simus_file_bytes
                print(f"DEBUG generate_csvs: usando simus_file_bytes em memória, tamanho={len(simus_bytes)} bytes")
            
            # Validar se os bytes foram lidos
            if len(compulab_bytes) == 0:
                self.error_message = "ERRO: Arquivo COMPULAB está vazio ou não foi carregado. Tente fazer upload novamente."
                print("DEBUG generate_csvs: ERRO - compulab_bytes está vazio!")
                yield
                return
                
            if len(simus_bytes) == 0:
                self.error_message = "ERRO: Arquivo SIMUS está vazio ou não foi carregado. Tente fazer upload novamente."
                print("DEBUG generate_csvs: ERRO - simus_bytes está vazio!")
                yield
                return
            
            print(f"DEBUG generate_csvs: Iniciando processamento com ThreadPoolExecutor...")
            
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
                print(f"DEBUG generate_csvs: SUCESSO! compulab_csv={len(compulab_csv) if compulab_csv else 0} chars, simus_csv={len(simus_csv) if simus_csv else 0} chars")
                yield
            else:
                self.error_message = "ERRO: Erro ao gerar CSVs. Verifique os arquivos."
                print("DEBUG generate_csvs: Falha - success=False retornado por generate_excel_from_pdfs")
                yield
        except Exception as e:
            import traceback
            print(f"DEBUG generate_csvs: EXCEÇÃO: {e}")
            traceback.print_exc()
            self.error_message = f"ERRO: Erro: {str(e)}"
            yield
        finally:
            self.is_generating_csv = False

