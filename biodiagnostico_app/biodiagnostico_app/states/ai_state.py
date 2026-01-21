import reflex as rx
from typing import List, Dict, Any, Optional
from .analysis_state import AnalysisState

class AIState(AnalysisState):
    """Estado responsável pela integração com IA (OpenAI, Gemini)"""
    
    # Configuração
    ai_provider: str = "OpenAI"  # OpenAI ou Gemini
    ai_model: str = "gpt-4o"  # Modelo específico selecionado
    openai_api_key: str = ""
    
    # Estado de processamento
    ai_loading_text: str = ""
    is_generating_ai: bool = False
    
    # Resultados
    ai_analysis_data: List[Dict[str, Any]] = []
    ai_analysis_csv: str = ""  # CSV data URI para download
    ai_analysis: str = "" # Texto bruto
    
    def set_api_key(self, key: str):
        self.openai_api_key = key

    def set_ai_provider(self, val: Any):
        self.ai_provider = val
        # Definir defaults ao trocar de provedor
        if val == "OpenAI":
            self.ai_model = "gpt-4o"
        elif val == "Gemini":
            self.ai_model = "gemini-2.5-flash"

    def set_ai_model(self, val: Any):
        self.ai_model = val
        
    async def run_ai_analysis(self):
        """Executa a análise de IA sobre os dados processados"""
        # Placeholder para lógica real de chamada à API
        # A lógica real estava dispersa ou incompleta no state original, 
        # mantenho a estrutura para implementação futura ou migração se existir.
        self.is_generating_ai = True
        self.ai_loading_text = "Conectando ao cérebro digital..."
        yield
        
        try:
            # Simulação ou chamada real iria aqui
            await asyncio.sleep(1)
            self.ai_analysis = "Análise AI Placeholder: Dados analisados com sucesso."
        finally:
            self.is_generating_ai = False
            self.ai_loading_text = ""
