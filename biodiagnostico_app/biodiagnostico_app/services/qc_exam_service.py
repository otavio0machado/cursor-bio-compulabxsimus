"""
Servico de Exames do CQ
Gerencia a lista dinamica de exames disponiveis para Controle de Qualidade
"""
import logging
from typing import List, Dict, Any
from .supabase_client import SupabaseClient
from .exceptions import ServiceError
from .types import QCExamRow

logger = logging.getLogger(__name__)


def get_supabase():
    client = SupabaseClient.get_client()
    if client is None:
        raise Exception("Cliente Supabase nao inicializado.")
    return client


class QCExamService:
    """CRUD para exames de CQ no Supabase"""

    @staticmethod
    async def get_exams(active_only: bool = True) -> List[QCExamRow]:
        """Retorna exames ordenados por display_order"""
        query = get_supabase().table("qc_exams").select("*")
        if active_only:
            query = query.eq("is_active", True)
        query = query.order("display_order", desc=False)
        response = query.execute()
        return response.data if response.data else []

    @staticmethod
    async def get_exam_names(active_only: bool = True) -> List[str]:
        """Retorna apenas os nomes dos exames ordenados"""
        exams = await QCExamService.get_exams(active_only=active_only)
        return [e["name"] for e in exams]

    @staticmethod
    async def create_exam(name: str) -> QCExamRow:
        """Adiciona novo exame com display_order automatico"""
        name = name.strip().upper()
        if not name:
            raise ValueError("Nome do exame nao pode ser vazio")

        # Determinar proximo display_order
        existing = await QCExamService.get_exams(active_only=False)
        max_order = max((e.get("display_order", 0) for e in existing), default=0)

        insert_data = {
            "name": name,
            "display_order": max_order + 1,
            "is_active": True,
        }
        response = get_supabase().table("qc_exams").insert(insert_data).execute()
        if not response.data:
            raise ServiceError("Insert em qc_exams não retornou dados.")
        return response.data[0]

    @staticmethod
    async def delete_exam(exam_id: str) -> bool:
        """Soft delete (desativa exame)"""
        try:
            response = get_supabase().table("qc_exams")\
                .update({"is_active": False})\
                .eq("id", exam_id)\
                .execute()
            return bool(response.data)
        except Exception as e:
            logger.error(f"Erro ao desativar exame {exam_id}: {e}")
            return False
