"""
Servico de Lotes de Reagentes
"""
import logging
from typing import List, Dict, Any
from .supabase_client import SupabaseClient

logger = logging.getLogger(__name__)


def get_supabase():
    client = SupabaseClient.get_client()
    if client is None:
        raise Exception("Cliente Supabase não inicializado.")
    return client


class ReagentService:
    """CRUD para lotes de reagentes no Supabase"""

    @staticmethod
    async def create_lot(data: Dict[str, Any]) -> Dict[str, Any]:
        insert_data = {
            "name": data.get("name"),
            "lot_number": data.get("lot_number"),
            "expiry_date": data.get("expiry_date"),
            "quantity": data.get("quantity"),
            "manufacturer": data.get("manufacturer"),
            "storage_temp": data.get("storage_temp"),
            "current_stock": float(data.get("current_stock", 0)),
            "estimated_consumption": float(data.get("estimated_consumption", 0)),
        }
        insert_data = {k: v for k, v in insert_data.items() if v is not None}
        response = get_supabase().table("reagent_lots").insert(insert_data).execute()
        return response.data[0] if response.data else {}

    @staticmethod
    async def get_lots(limit: int = 200) -> List[Dict[str, Any]]:
        response = get_supabase().table("reagent_lots")\
            .select("*")\
            .order("created_at", desc=True)\
            .limit(limit)\
            .execute()
        return response.data if response.data else []

    @staticmethod
    async def delete_lot(lot_id: str) -> bool:
        try:
            get_supabase().table("reagent_lots").delete().eq("id", lot_id).execute()
            verify = get_supabase().table("reagent_lots").select("id").eq("id", lot_id).execute()
            return not verify.data
        except Exception as e:
            logger.error(f"Erro ao deletar reagent lot {lot_id}: {e}")
            return False

    @staticmethod
    async def update_lot(lot_id: str, data: Dict[str, Any]) -> bool:
        try:
            update_data = {k: v for k, v in data.items() if v is not None}
            if not update_data:
                return False
            response = get_supabase().table("reagent_lots").update(update_data).eq("id", lot_id).execute()
            return bool(response.data)
        except Exception as e:
            logger.error(f"Erro ao atualizar reagent lot {lot_id}: {e}")
            return False
