"""
API Endpoints para integração com n8n AI Agent Tools.

Estes endpoints são chamados pelo n8n quando o AI Agent precisa
executar ferramentas que requerem processamento no backend.

Seguindo SKILL "O Oráculo" - Integração AI e Prompts
"""

import reflex as rx
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .services.n8n_tools_service import n8n_tools_service


# ============================================================
# Modelos Pydantic para validação de entrada
# ============================================================

class WestgardInput(BaseModel):
    """Entrada para a ferramenta interpretador_westgard."""
    value: float
    target_value: float
    target_sd: float


class ContestacaoInput(BaseModel):
    """Entrada para a ferramenta gerar_contestacao."""
    convenio: Optional[str] = "[Nome do Convênio]"
    exame: Optional[str] = "[Nome do Exame]"
    valor_cobrado: Optional[float] = 0
    valor_pago: Optional[float] = 0
    motivo: Optional[str] = "divergência de valores"
    paciente: Optional[str] = "[Nome do Paciente]"


class CompararTabelasInput(BaseModel):
    """Entrada para a ferramenta comparar_tabelas."""
    exame: Optional[str] = "HEMOGRAMA"


# ============================================================
# Router FastAPI para endpoints de Tools
# ============================================================

n8n_tools_router = APIRouter(prefix="/api/n8n-tools", tags=["n8n-tools"])


@n8n_tools_router.post("/westgard")
async def tool_westgard(data: WestgardInput):
    """
    Endpoint para a ferramenta interpretador_westgard.
    
    Valida resultados de Controle de Qualidade usando as regras de Westgard.
    
    Chamado pelo n8n via toolHttpRequest.
    """
    try:
        result = n8n_tools_service.interpretador_westgard(
            value=data.value,
            target_value=data.target_value,
            target_sd=data.target_sd
        )
        return result
    except Exception as e:
        return {"sucesso": False, "erro": str(e)}


@n8n_tools_router.post("/contestacao")
async def tool_contestacao(data: ContestacaoInput):
    """
    Endpoint para a ferramenta gerar_contestacao.
    
    Gera uma carta profissional para contestar uma glosa de convênio.
    
    Chamado pelo n8n via toolHttpRequest.
    """
    try:
        result = n8n_tools_service.gerar_contestacao(
            convenio=data.convenio,
            exame=data.exame,
            valor_cobrado=data.valor_cobrado,
            valor_pago=data.valor_pago,
            motivo=data.motivo,
            paciente=data.paciente
        )
        return result
    except Exception as e:
        return {"sucesso": False, "erro": str(e)}


@n8n_tools_router.post("/comparar-tabelas")
async def tool_comparar_tabelas(data: CompararTabelasInput):
    """
    Endpoint para a ferramenta comparar_tabelas.
    
    Compara valores entre a tabela do laboratório e as tabelas dos convênios.
    
    Chamado pelo n8n via toolHttpRequest.
    """
    try:
        result = n8n_tools_service.comparar_tabelas(exame=data.exame)
        return result
    except Exception as e:
        return {"sucesso": False, "erro": str(e)}


@n8n_tools_router.get("/health")
async def health_check():
    """Endpoint de verificação de saúde da API."""
    return {"status": "ok", "service": "n8n-tools"}


# ============================================================
# Função para registrar o router no app Reflex
# ============================================================

def register_n8n_tools_api(app: rx.App):
    """
    Registra os endpoints de tools do n8n no app Reflex/FastAPI.
    
    Deve ser chamado após a criação do app.
    
    Exemplo:
        app = rx.App(...)
        register_n8n_tools_api(app)
    """
    # Reflex expõe uma instância FastAPI que podemos estender
    # Isso será feito no arquivo principal ou em um hook de inicialização
    pass
