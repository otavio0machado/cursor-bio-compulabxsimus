"""
Serviço de Histórico de Auditorias
Laboratório Biodiagnóstico
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from .supabase_client import supabase

class AuditService:
    """Operações de banco de dados para Resumos de Auditoria"""
    
    @staticmethod
    async def save_audit_summary(data: Dict[str, Any]) -> Dict[str, Any]:
        """Salva resumo de uma análise no banco de dados"""
        if not supabase:
            return {}
            
        try:
            # Tabela audit_summaries (deve ser criada no Supabase)
            # colunas: created_at, compulab_total, simus_total, missing_exams_count, 
            # divergences_count, missing_patients_count, ai_summary (text)
            
            db_data = {
                "compulab_total": data.get("compulab_total", 0.0),
                "simus_total": data.get("simus_total", 0.0),
                "missing_exams_count": data.get("missing_exams_count", 0),
                "divergences_count": data.get("divergences_count", 0),
                "missing_patients_count": data.get("missing_patients_count", 0),
                "ai_summary": data.get("ai_summary", "")[:500] # Limitar tamanho
            }
            
            response = supabase.table("audit_summaries").insert(db_data).execute()
            return response.data[0] if response.data else {}
        except Exception as e:
            print(f"Erro ao salvar resumo de auditoria: {e}")
            return {}

    @staticmethod
    async def get_latest_audit_summary() -> Optional[Dict[str, Any]]:
        """Busca o resumo da última análise realizada"""
        if not supabase:
            return None
            
        try:
            response = supabase.table("audit_summaries")\
                .select("*")\
                .order("created_at", descending=True)\
                .limit(1)\
                .execute()
                
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Erro ao buscar último resumo: {e}")
            return None
