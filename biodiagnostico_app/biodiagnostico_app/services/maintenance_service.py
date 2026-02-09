"""
Servico de Registros de Manutencao
"""
import logging
from typing import List, Dict, Any
from .supabase_client import SupabaseClient
from .exceptions import ServiceError
from .types import MaintenanceRecordRow

logger = logging.getLogger(__name__)


def get_supabase():
    client = SupabaseClient.get_client()
    if client is None:
        raise Exception("Cliente Supabase não inicializado.")
    return client


class MaintenanceService:
    """CRUD para registros de manutenção no Supabase"""

    @staticmethod
    async def create_record(data: Dict[str, Any]) -> MaintenanceRecordRow:
        insert_data = {
            "equipment": data.get("equipment"),
            "type": data.get("type"),
            "date": data.get("date"),
            "next_date": data.get("next_date"),
            "technician": data.get("technician"),
            "notes": data.get("notes"),
        }
        insert_data = {k: v for k, v in insert_data.items() if v is not None}
        response = get_supabase().table("maintenance_records").insert(insert_data).execute()
        if not response.data:
            raise ServiceError("Insert em maintenance_records não retornou dados.")
        return response.data[0]

    @staticmethod
    async def get_records(limit: int = 200) -> List[MaintenanceRecordRow]:
        response = get_supabase().table("maintenance_records")\
            .select("*")\
            .order("created_at", desc=True)\
            .limit(limit)\
            .execute()
        return response.data if response.data else []

    @staticmethod
    async def delete_record(record_id: str) -> bool:
        try:
            get_supabase().table("maintenance_records").delete().eq("id", record_id).execute()
            verify = get_supabase().table("maintenance_records").select("id").eq("id", record_id).execute()
            return not verify.data
        except Exception as e:
            logger.error(f"Erro ao deletar maintenance record {record_id}: {e}")
            return False

    @staticmethod
    async def update_record(record_id: str, data: Dict[str, Any]) -> bool:
        try:
            update_data = {k: v for k, v in data.items() if v is not None}
            if not update_data:
                return False
            response = get_supabase().table("maintenance_records").update(update_data).eq("id", record_id).execute()
            return bool(response.data)
        except Exception as e:
            logger.error(f"Erro ao atualizar maintenance record {record_id}: {e}")
            return False
