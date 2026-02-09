"""
Servico de Nomes de Registro do CQ
Gerencia nomes reutilizaveis para registros de referencia
"""
import logging
from typing import List, Dict, Any
from .supabase_client import SupabaseClient
from .exceptions import ServiceError
from .types import QCRegistryNameRow

logger = logging.getLogger(__name__)


def get_supabase():
    client = SupabaseClient.get_client()
    if client is None:
        raise Exception("Cliente Supabase nao inicializado.")
    return client


class QCRegistryNameService:
    """CRUD para nomes de registro de CQ"""

    @staticmethod
    async def get_names(active_only: bool = True) -> List[str]:
        """Retorna lista de nomes ordenados por criacao"""
        query = get_supabase().table("qc_registry_names").select("name")
        if active_only:
            query = query.eq("is_active", True)
        query = query.order("created_at", desc=False)
        response = query.execute()
        return [r["name"] for r in response.data] if response.data else []

    @staticmethod
    async def create_name(name: str) -> QCRegistryNameRow:
        """Adiciona novo nome de registro"""
        name = name.strip()
        if not name:
            raise ValueError("Nome nao pode ser vazio")
        response = get_supabase().table("qc_registry_names").insert({
            "name": name,
            "is_active": True,
        }).execute()
        if not response.data:
            raise ServiceError("Insert em qc_registry_names não retornou dados.")
        return response.data[0]

    @staticmethod
    async def delete_name(name_id: str) -> bool:
        """Soft delete"""
        try:
            response = get_supabase().table("qc_registry_names")\
                .update({"is_active": False})\
                .eq("id", name_id)\
                .execute()
            return bool(response.data)
        except Exception as e:
            logger.error(f"Erro ao desativar nome {name_id}: {e}")
            return False
