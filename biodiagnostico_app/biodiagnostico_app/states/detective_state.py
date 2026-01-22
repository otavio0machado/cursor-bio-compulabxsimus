import reflex as rx
from typing import List, Dict, Any
import json
import os
from ..ai.services.detective_service import DetectiveService
from ..ai.mock_data import get_mock_divergency_data
from .ai_state import AIState

# Flag para usar n8n (se configurado)
USE_N8N = bool(os.getenv("N8N_WEBHOOK_URL"))

class DetectiveState(AIState):
    """
    Estado dedicado ao 'Detetive de Dados' (Chat de Insights).
    Gerencia o histórico de mensagens e a interação com a IA.
    
    Suporta dois backends:
    - n8n AI Agent (se N8N_WEBHOOK_URL estiver configurada)
    - Gemini local (fallback)
    """
    messages: List[Dict[str, str]] = [
        {"role": "ai", "content": "🧬 **Bio IA** ao seu dispor!\n\nEstou analisando as divergências financeiras. Pergunte sobre glosas, convênios ou perdas financeiras."}
    ]
    input_text: str = ""
    is_loading: bool = False
    data_context: str = ""
    using_n8n: bool = USE_N8N
    
    # --- UX Improvements ---
    thinking_steps: List[str] = []
    suggested_actions: List[str] = [
        "Quais são os principais motivos de glosa?",
        "Qual convênio tem maior divergência?",
        "Analisar QC usando as regras de Westgard.",
        "Resuma as perdas financeiras deste mês.",
        "Analisar erros de valor no Compulab vs Simus."
    ]
    
    # Multimodal support
    image_files: List[Dict[str, Any]] = [] # [{ "data": bytes, "mime_type": str, "name": str }]

    def set_input_text(self, value: str):
        self.input_text = value

    def load_context(self):
        """Carrega os dados para o contexto da IA (Real se houver, ou Mock)."""
        # Se houver divergências reais carregadas no AnalysisState
        if self.has_analysis:
            data_list = []
            
            # Adicionar divergências de valor
            for div in self.value_divergences:
                data_list.append({
                    "tipo": "DIVERGENCIA_VALOR",
                    "paciente": div.patient,
                    "exame": div.exam_name,
                    "valor_compulab": div.compulab_value,
                    "valor_simus": div.simus_value,
                    "diferenca": div.difference,
                    "status": "ERRO_VALOR"
                })
            
            # Adicionar exames faltantes
            for missing in self.missing_exams:
                data_list.append({
                    "tipo": "EXAME_FALTANTE_SIMUS",
                    "paciente": missing.patient,
                    "exame": missing.exam_name,
                    "valor": missing.compulab_value,
                    "status": "GLOSADO_PROVAVEL"
                })

            # Adicionar pacientes faltantes (resumido)
            for patient in self.missing_patients:
                data_list.append({
                    "tipo": "PACIENTE_NAO_ENCONTRADO",
                    "paciente": patient.patient,
                    "qtd_exames": patient.exams_count,
                    "valor_total": patient.total_value,
                    "status": "NAO_FATURADO"
                })

            if data_list:
                self.data_context = json.dumps(data_list, indent=2, ensure_ascii=False)
                print(f"DEBUG: DetectiveState loaded REAL data context ({len(data_list)} items).")
            else:
                 self.data_context = "Nenhuma divergência encontrada na análise atual."
        
        # Fallback para Mock se não houver contexto (e não houve análise)
        elif not self.data_context:
            self.data_context = get_mock_divergency_data()
            print("DEBUG: DetectiveState loaded MOCK data context.")

    async def handle_image_upload(self, files: List[rx.UploadFile]):
        """Lê os arquivos de imagem e armazena em memória."""
        self.image_files = []
        for file in files:
            upload_data = await file.read()
            self.image_files.append({
                "data": upload_data,
                "mime_type": file.content_type,
                "name": file.filename
            })
        
        # Feedback visual imediato
        if self.image_files:
            file_names = ", ".join([f["name"] for f in self.image_files])
            self.messages.append({"role": "ai", "content": f"📸 Recebi {len(self.image_files)} imagem(ns): **{file_names}**. O que deseja que eu analise nelas?"})

    def handle_keys(self, key: str):
        """Monitora teclas pressionadas"""
        if key == "Enter":
            return self.send_message()

    async def send_message(self):
        """Envia a mensagem do usuário para o serviço de IA (n8n ou local)."""
        if not self.input_text.strip():
            return
        
        user_msg = self.input_text
        self.messages.append({"role": "user", "content": user_msg})
        # Limpar input
        self.input_text = ""
        # Setar loading
        self.is_loading = True
        yield

        # Garantir contexto
        self.load_context()

        # Chamar serviço (n8n ou local)
        try:
            if self.using_n8n:
                # Usar n8n AI Agent
                self.thinking_steps = ["Conectando ao agente n8n...", "Enviando contexto de dados..."]
                yield
                from ..services.n8n_service import ask_detective_n8n
                # ... (rest of n8n logic)
                result = await ask_detective_n8n(
                    message=user_msg,
                    value_divergences=[{
                        "paciente": div.patient,
                        "exame": div.exam_name,
                        "valor_compulab": div.compulab_value,
                        "valor_simus": div.simus_value,
                        "diferenca": div.difference
                    } for div in self.value_divergences],
                    missing_patients=[{
                        "paciente": p.patient,
                        "qtd_exames": p.exams_count,
                        "valor_total": p.total_value
                    } for p in self.missing_patients],
                    missing_exams=[{
                        "paciente": m.exam_name,
                        "exame": m.exam_name,
                        "valor": m.compulab_value
                    } for m in self.missing_exams]
                )
                
                if result.get("success"):
                    # Processar thinking steps (intermediate steps das ferramentas)
                    steps = result.get("agent_thinking", [])
                    for step in steps:
                        tool = step.get("tool", "ferramenta")
                        tool_input = step.get("toolInput", "")
                        self.thinking_steps.append(f"🔍 Investigando com {tool}...")
                        yield
                        await asyncio.sleep(0.5)
                    
                    self.thinking_steps.append("✨ Análise finalizada!")
                    yield
                    self.messages.append({"role": "ai", "content": result.get("response", "")})
                else:
                    self.messages.append({"role": "ai", "content": result.get("response", "Erro desconhecido.")})
            else:
                # Fallback: usar DetectiveService local
                self.thinking_steps = ["Iniciando Bio IA...", "Analisando contexto de dados..."]
                yield
                await asyncio.sleep(1) # Simular processamento inicial
                
                self.thinking_steps.append("Consultando o Gemini (modelo 2.5-flash)...")
                yield
                
                service = DetectiveService()
                response = await service.ask_detective(
                    user_msg, 
                    self.data_context,
                    images=self.image_files if self.image_files else None
                )
                
                self.thinking_steps.append("Análise concluída!")
                yield
                await asyncio.sleep(0.5)
                
                self.messages.append({"role": "ai", "content": response})
                
                # Limpar imagens após o envio
                self.image_files = []
        except Exception as e:
            self.messages.append({"role": "ai", "content": f"⚠️ Erro ao processar: {str(e)}"})
        finally:
            self.is_loading = False
            self.thinking_steps = []
            
    def select_suggested_action(self, action: str):
        """Preenche o input com a ação sugerida e envia."""
        self.input_text = action
        return self.send_message()
