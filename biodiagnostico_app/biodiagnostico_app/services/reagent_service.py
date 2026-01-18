"""
Serviço de Gestão de Reagentes
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from .supabase_client import supabase

class ReagentService:
    """Operações de banco de dados para Reagentes"""
    
    @staticmethod
    async def create_reagent_lot(lot_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria novo lote de reagente"""
        data = {
            "name": lot_data.get("name"),
            "lot_number": lot_data.get("lot_number"),
            "expiry_date": lot_data.get("expiry_date"),
            "quantity": lot_data.get("quantity"),
            "manufacturer": lot_data.get("manufacturer"),
            "storage_temp": lot_data.get("storage_temp"),
            "is_active": True
        }
        
        response = supabase.table("reagent_lots").insert(data).execute()
        return response.data[0] if response.data else {}
    
    @staticmethod
    async def get_active_lots() -> List[Dict[str, Any]]:
        """Retorna todos os lotes ativos"""
        response = supabase.table("reagent_lots")\
            .select("*")\
            .eq("is_active", True)\
            .order("expiry_date")\
            .execute()
            
        return response.data
    
    @staticmethod
    async def get_expiring_lots(days: int = 30) -> List[Dict[str, Any]]:
        """Retorna lotes vencendo nos próximos X dias"""
        today = datetime.now().date()
        limit_date = (today + timedelta(days=days)).isoformat()
        today_str = today.isoformat()
        
        response = supabase.table("reagent_lots")\
            .select("*")\
            .eq("is_active", True)\
            .gte("expiry_date", today_str)\
            .lte("expiry_date", limit_date)\
            .order("expiry_date")\
            .execute()
            
        return response.data
    
    @staticmethod
    async def delete_reagent_lot(lot_id: str) -> bool:
        """Marca lote como inativo (soft delete) ou remove"""
        # Soft delete é mais seguro
        response = supabase.table("reagent_lots")\
            .update({"is_active": False})\
            .eq("id", lot_id)\
            .execute()
            
        return len(response.data) > 0
