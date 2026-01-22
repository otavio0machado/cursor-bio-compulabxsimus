"""
AuditRepository - O Arquivista
Gerencia a persistência de logs de auditoria no Supabase seguindo o padrão Repository.
"""
from typing import Dict, Any, List
from ..services.supabase_client import supabase

class AuditRepository:
    table_name = "data_audits"

    @staticmethod
    def create_log(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cria um novo log de auditoria.
        Campos esperados: record_id, table_name, old_value, new_value, user_id, action, consistency_result
        """
        if not supabase:
            return {}
        
        try:
            response = supabase.table(AuditRepository.table_name).insert(data).execute()
            return response.data[0] if response.data else {}
        except Exception as e:
            print(f"Error creating audit log: {e}")
            return {}

    @staticmethod
    def get_logs_by_record(record_id: str) -> List[Dict[str, Any]]:
        """Busca histórico de alterações de um registro específico."""
        if not supabase:
            return []
        
        try:
            response = supabase.table(AuditRepository.table_name)\
                .select("*")\
                .eq("record_id", record_id)\
                .order("created_at", desc=True)\
                .execute()
            return response.data
        except Exception as e:
            print(f"Error fetching logs: {e}")
            return []
