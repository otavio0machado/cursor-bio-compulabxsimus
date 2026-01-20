"""
Serviço de Manutenção de Equipamentos
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from .supabase_client import supabase

class MaintenanceService:
    """Operações de banco de dados para Manutenções"""
    
    @staticmethod
    async def create_maintenance_record(record_data: Dict[str, Any]) -> Dict[str, Any]:
        """Registra nova manutenção"""
        data = {
            "equipment_name": record_data.get("equipment"),
            "type": record_data.get("type"),
            "date": record_data.get("date"),
            "next_date": record_data.get("next_date"),
            "technician_name": record_data.get("technician"),
            "notes": record_data.get("notes"),
            "status": "completed" # Default status
        }
        
        response = supabase.table("maintenance_records").insert(data).execute()
        return response.data[0] if response.data else {}
    
    @staticmethod
    async def get_recent_maintenances(limit: int = 20) -> List[Dict[str, Any]]:
        """Retorna manutenções recentes"""
        response = supabase.table("maintenance_records")\
            .select("*")\
            .order("date", desc=True)\
            .limit(limit)\
            .execute()
            
        return response.data
    
    @staticmethod
    async def get_pending_maintenances_count() -> int:
        """Conta manutenções preventivas pendentes (baseado em next_date vencendo hoje ou antes e não realizadas)"""
        # Esta lógica depende de como "pendente" é definido. 
        # Se for apenas registros agendados que ainda não foram feitos:
        # Mas aqui estamos simplificando: maintenance_records guarda historico.
        # Poderíamos ter uma tabela de "agendamentos". 
        # Por enquanto vamos retornar 0 ou implementar lógica futura.
    @staticmethod
    async def delete_maintenance_record(record_id: str) -> bool:
        """Remove registro de manutenção"""
        try:
            supabase.table("maintenance_records")\
                .delete()\
                .eq("id", record_id)\
                .execute()
            return True
        except Exception as e:
            print(f"Erro ao deletar registro de manutenção {record_id}: {e}")
            return False
