"""
Serviço de integração com n8n AI Agent.

Este serviço substitui o DetectiveService local, delegando
as análises para o AI Agent configurado no n8n.
"""
import os
import httpx
import asyncio
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class N8NAgentService:
    """Serviço para comunicação com o AI Agent no n8n."""
    
    def __init__(self):
        self.webhook_url = os.getenv("N8N_WEBHOOK_URL")
        self.timeout = 60.0  # 60 segundos para respostas de AI
        self.max_retries = 3
        
        if not self.webhook_url:
            raise ValueError(
                "N8N_WEBHOOK_URL não configurada no .env\n"
                "Configure com a URL do webhook do n8n após importar o workflow."
            )
    
    async def ask_agent(
        self, 
        message: str, 
        context: dict,
        supabase_url: Optional[str] = None
    ) -> dict:
        """
        Envia uma pergunta para o AI Agent no n8n.
        
        Args:
            message: Pergunta do usuário
            context: Dados de contexto (divergências, pacientes, etc)
            supabase_url: URL do Supabase para a tool de histórico
            
        Returns:
            dict com 'success', 'response' e 'agent_thinking'
        """
        import json
        
        payload = {
            "message": message,
            "context": json.dumps(context, ensure_ascii=False),
            "supabase_url": supabase_url or os.getenv("SUPABASE_URL", "")
        }
        
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        self.webhook_url,
                        json=payload,
                        headers={"Content-Type": "application/json"}
                    )
                    
                    print(f"DEBUG n8n: Status={response.status_code}, Content-Type={response.headers.get('content-type', 'unknown')}")
                    print(f"DEBUG n8n: Response preview: {response.text[:300] if response.text else 'EMPTY'}")
                    
                    if response.status_code == 200:
                        if not response.text or response.text.strip() == "":
                            return {
                                "success": False,
                                "response": "⚠️ n8n retornou resposta vazia. Verifique os Logs no n8n para ver o erro.",
                                "agent_thinking": []
                            }
                        
                        try:
                            data = response.json()
                            # O n8n pode retornar em diferentes formatos
                            if isinstance(data, dict):
                                if "success" in data:
                                    return data
                                elif "output" in data:
                                    return {"success": True, "response": data["output"], "agent_thinking": []}
                                elif "text" in data:
                                    return {"success": True, "response": data["text"], "agent_thinking": []}
                                else:
                                    # Retornar o JSON como string
                                    return {"success": True, "response": str(data), "agent_thinking": []}
                            elif isinstance(data, str):
                                return {"success": True, "response": data, "agent_thinking": []}
                            else:
                                return {"success": True, "response": str(data), "agent_thinking": []}
                        except Exception as json_err:
                            # n8n retornou algo que não é JSON - pode ser text puro
                            print(f"DEBUG n8n: JSON error: {json_err}")
                            if response.text:
                                return {"success": True, "response": response.text, "agent_thinking": []}
                            return {
                                "success": False,
                                "response": "⚠️ n8n retornou resposta inválida.",
                                "agent_thinking": []
                            }
                    else:
                        print(f"DEBUG n8n: Error status {response.status_code}")
                        return {
                            "success": False,
                            "response": f"Erro do n8n: {response.status_code} - {response.text[:100] if response.text else 'sem detalhes'}",
                            "agent_thinking": []
                        }
                        
            except httpx.TimeoutException:
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    continue
                return {
                    "success": False,
                    "response": "⏱️ Tempo limite excedido. O agente está demorando muito para responder.",
                    "agent_thinking": []
                }
                
            except httpx.RequestError as e:
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                return {
                    "success": False,
                    "response": f"❌ Erro de conexão com n8n: {str(e)}",
                    "agent_thinking": []
                }
        
        return {
            "success": False,
            "response": "❌ Falha após múltiplas tentativas.",
            "agent_thinking": []
        }
    
    def format_context_for_agent(
        self,
        value_divergences: list = None,
        missing_patients: list = None,
        missing_exams: list = None,
        extra_simus_exams: list = None
    ) -> dict:
        """
        Formata os dados de divergência para envio ao agente.
        
        Args:
            value_divergences: Lista de divergências de valores
            missing_patients: Lista de pacientes ausentes
            missing_exams: Lista de exames ausentes
            extra_simus_exams: Lista de exames extras no SIMUS
            
        Returns:
            Dicionário formatado para o agente
        """
        return {
            "value_divergences": value_divergences or [],
            "missing_patients": missing_patients or [],
            "missing_exams": missing_exams or [],
            "extra_simus_exams": extra_simus_exams or [],
            "resumo": {
                "total_divergencias_valor": len(value_divergences or []),
                "total_pacientes_ausentes": len(missing_patients or []),
                "total_exames_ausentes": len(missing_exams or []),
                "total_exames_extras": len(extra_simus_exams or [])
            }
        }


# Instância global do serviço
_n8n_service: Optional[N8NAgentService] = None


def get_n8n_service() -> N8NAgentService:
    """Retorna instância singleton do serviço n8n."""
    global _n8n_service
    if _n8n_service is None:
        _n8n_service = N8NAgentService()
    return _n8n_service


async def ask_detective_n8n(
    message: str,
    value_divergences: list = None,
    missing_patients: list = None,
    missing_exams: list = None,
    extra_simus_exams: list = None
) -> dict:
    """
    Função de conveniência para perguntar ao Detetive de Dados via n8n.
    
    Args:
        message: Pergunta do usuário
        value_divergences: Divergências de valores
        missing_patients: Pacientes ausentes
        missing_exams: Exames ausentes
        extra_simus_exams: Exames extras no SIMUS
        
    Returns:
        Dicionário com 'success', 'response' e 'agent_thinking'
    """
    try:
        service = get_n8n_service()
        context = service.format_context_for_agent(
            value_divergences=value_divergences,
            missing_patients=missing_patients,
            missing_exams=missing_exams,
            extra_simus_exams=extra_simus_exams
        )
        
        return await service.ask_agent(message, context)
            
    except ValueError as e:
        return {"success": False, "response": f"⚠️ Configuração necessária: {str(e)}", "agent_thinking": []}
    except Exception as e:
        return {"success": False, "response": f"❌ Erro inesperado: {str(e)}", "agent_thinking": []}
