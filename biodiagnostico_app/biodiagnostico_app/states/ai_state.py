import reflex as rx
import asyncio
from typing import List, Dict, Any, Optional
from .analysis_state import AnalysisState
from ..services.ai_service import ai_service, AVAILABLE_MODELS

class AIState(AnalysisState):
    """Estado responsável pela integração com IA (OpenAI, Gemini)"""
    
    # Configuração
    ai_provider: str = "Gemini"  # OpenAI ou Gemini
    ai_model: str = "gemini-2.5-flash"  # Modelo específico selecionado
    
    # Estado de processamento
    ai_loading_text: str = ""
    is_generating_ai: bool = False
    ai_error: str = ""
    
    # Resultados
    ai_analysis_data: List[Dict[str, Any]] = []
    ai_analysis_csv: str = ""  # CSV data URI para download
    ai_analysis: str = ""  # Texto bruto do relatório
    
    @rx.var
    def available_providers(self) -> List[str]:
        """Lista de provedores disponíveis"""
        return ["OpenAI", "Gemini"]
    
    @rx.var
    def available_models(self) -> List[Dict[str, str]]:
        """Lista de modelos disponíveis para o provedor atual"""
        return AVAILABLE_MODELS.get(self.ai_provider, [])
    
    @rx.var
    def available_model_ids(self) -> List[str]:
        """IDs dos modelos disponíveis"""
        return [m["id"] for m in self.available_models]
    
    @rx.var
    def current_model_name(self) -> str:
        """Nome do modelo atual"""
        for model in self.available_models:
            if model["id"] == self.ai_model:
                return model["name"]
        return self.ai_model
    
    def set_ai_provider(self, val: str):
        """Define o provedor e ajusta o modelo padrão"""
        self.ai_provider = val
        self.ai_error = ""
        # Definir modelo padrão ao trocar de provedor
        if val == "OpenAI":
            self.ai_model = "gpt-4o-mini"  # Econômico por padrão
        elif val == "Gemini":
            self.ai_model = "gemini-2.5-flash"  # Rápido por padrão

    def set_ai_model(self, val: str):
        """Define o modelo selecionado"""
        self.ai_model = val
        self.ai_error = ""

    # OpenAI specific (used in some components)
    openai_api_key: str = ""

    def set_api_key(self, key: str):
        """Define a chave de API da OpenAI"""
        self.openai_api_key = key
        
    async def run_ai_analysis(self):
        """Executa a análise de IA usando o provedor e modelo selecionados"""
        print(f"DEBUG: run_ai_analysis STARTED - provider={self.ai_provider}, model={self.ai_model}")
        self.is_generating_ai = True
        self.ai_error = ""
        self.ai_loading_text = f"Conectando ao {self.ai_provider}..."
        yield
        
        try:
            self.ai_loading_text = f"Analisando com {self.current_model_name}..."
            yield
            
            # Preparar dados para análise
            analysis_data = {
                "compulab_total": self.compulab_total,
                "simus_total": self.simus_total,
                "missing_patients_count": self.missing_patients_count,
                "missing_patients_total": self.missing_patients_total,
                "missing_exams_count": self.missing_exams_count,
                "missing_exams_total": self.missing_exams_total,
                "divergences_count": self.divergences_count,
                "divergences_total": self.divergences_total,
                "extra_simus_exams_count": self.extra_simus_exams_count,
                "top_exams": [
                    {"name": getattr(t, 'name', ''), "count": getattr(t, 'count', 0)} 
                    for t in self.top_offenders[:5]
                ] if self.top_offenders else []
            }
            
            # Chamar serviço de IA
            self.ai_loading_text = "Gerando relatório inteligente..."
            yield
            
            result = await ai_service.run_analysis(
                provider=self.ai_provider,
                model=self.ai_model,
                analysis_data=analysis_data
            )
            
            # Escapar cifrões para evitar que o Markdown interprete como Math Mode (KaTeX)
            # Isso resolve o problema de texto "bugado" e com espaços anormais
            self.ai_analysis = result.replace("$", "\\$")
            self.ai_loading_text = "Relatório gerado com sucesso!"
            print(f"DEBUG: run_ai_analysis SUCCESS - {len(result)} caracteres")
            yield
            
            # Pequena pausa para usuário ver mensagem de sucesso
            await asyncio.sleep(0.5)
            
        except ImportError as e:
            error_msg = str(e)
            print(f"DEBUG: run_ai_analysis IMPORT ERROR: {e}")
            self.ai_error = f"Pacote não instalado: {error_msg}"
            self.ai_analysis = f"❌ **Erro de Dependência**\n\n{error_msg}\n\nInstale o pacote necessário e tente novamente."
            yield
            
        except ValueError as e:
            error_msg = str(e)
            print(f"DEBUG: run_ai_analysis CONFIG ERROR: {e}")
            self.ai_error = error_msg
            self.ai_analysis = f"❌ **Erro de Configuração**\n\n{error_msg}\n\nVerifique o arquivo `.env`."
            yield
            
        except Exception as e:
            error_msg = str(e)
            print(f"DEBUG: run_ai_analysis ERROR: {e}")
            import traceback
            traceback.print_exc()
            self.ai_error = error_msg
            self.ai_analysis = f"❌ **Erro na Análise**\n\n{error_msg}\n\nTente novamente ou selecione outro modelo."
            yield
            
        finally:
            self.is_generating_ai = False
            self.ai_loading_text = ""
            print("DEBUG: run_ai_analysis FINISHED")
            yield

    async def generate_ai_analysis(self):
        """Wrapper público para gerar análise de IA"""
        print("DEBUG: generate_ai_analysis CALLED in AIState")
        async for _ in self.run_ai_analysis():
            yield
