"""
Serviço de Controle de Qualidade (QC)
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
# Importação circular evitada: importamos apenas para validação de tipo se necessário, 
# mas os dados virão como dicts ou objetos do State
# from ..state import QCRecord 
from .supabase_client import supabase

class QCService:
    """Operações de banco de dados para QC"""
    
    @staticmethod
    async def create_qc_record(record_data: Dict[str, Any]) -> Dict[str, Any]:
        """Insere novo registro de CQ"""
        # Prepara os dados para inserção (remove campos que não são colunas ou trata tipos)
        data = {
            "date": record_data.get("date"),
            "exam_name": record_data.get("exam_name"),
            "level": record_data.get("level"),
            "lot_number": record_data.get("lot_number"),
            "value": float(record_data.get("value", 0)),
            "target_value": float(record_data.get("target_value", 0)),
            "target_sd": float(record_data.get("target_sd", 0)),
            "equipment_name": record_data.get("equipment"),
            "analyst_name": record_data.get("analyst"),
            "status": record_data.get("status", "OK")
        }
        
        response = supabase.table("qc_records").insert(data).execute()
        return response.data[0] if response.data else {}

    @staticmethod
    async def create_qc_records_batch(records_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Insere múltiplos registros de CQ em lote"""
        data_list = []
        for record_data in records_data:
            data_list.append({
                "date": record_data.get("date"),
                "exam_name": record_data.get("exam_name"),
                "level": record_data.get("level"),
                "lot_number": record_data.get("lot_number"),
                "value": float(record_data.get("value", 0)),
                "target_value": float(record_data.get("target_value", 0)),
                "target_sd": float(record_data.get("target_sd", 0)),
                "equipment_name": record_data.get("equipment"),
                "analyst_name": record_data.get("analyst"),
                "status": record_data.get("status", "OK")
            })
        
        response = supabase.table("qc_records").insert(data_list).execute()
        return response.data if response.data else []
    
    @staticmethod
    async def get_qc_records(
        limit: int = 100,
        exam_name: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Busca registros de CQ com filtros"""
        query = supabase.table("qc_records").select("*")
        
        if exam_name:
            query = query.eq("exam_name", exam_name)
        if start_date:
            query = query.gte("date", start_date)
        if end_date:
            query = query.lte("date", end_date)
        
        query = query.order("date", desc=True).limit(limit)
        response = query.execute()
        
        return response.data
    
    @staticmethod
    async def get_qc_statistics_today() -> Dict[str, int]:
        """Retorna estatísticas de hoje"""
        today = datetime.now().date().isoformat()
        
        # Total de registros hoje
        total = supabase.table("qc_records")\
            .select("id", count="exact")\
            .gte("date", today)\
            .execute()
        
        # Registros com alerta (Status != OK) - Ajuste conforme lógica do banco
        # Supondo que o banco calcule o status ou que a aplicação filtre
        # Aqui vamos filtrar pelo status gerado se possível, ou calcular na query se não
        alerts = supabase.table("qc_records")\
            .select("id", count="exact")\
            .gte("date", today)\
            .neq("status", "OK")\
            .execute()
        
        return {
            "total_today": total.count,
            "alerts_today": alerts.count
        }
    
    @staticmethod
    async def get_qc_statistics_month() -> int:
        """Retorna total de registros do mês atual"""
        today = datetime.now()
        first_day = today.replace(day=1).date().isoformat()
        
        total = supabase.table("qc_records")\
            .select("id", count="exact")\
            .gte("date", first_day)\
            .execute()
            
        return total.count

    @staticmethod
    async def get_approval_rate_month() -> float:
        """Calcula taxa de aprovação do mês"""
        today = datetime.now()
        first_day = today.replace(day=1).date().isoformat()
        
        # Total do mês
        total_response = supabase.table("qc_records")\
            .select("id", count="exact")\
            .gte("date", first_day)\
            .execute()
            
        total = total_response.count
        
        if total == 0:
            return 0.0
            
        # Total aprovado (OK)
        ok_response = supabase.table("qc_records")\
            .select("id", count="exact")\
            .gte("date", first_day)\
            .eq("status", "OK")\
            .execute()
            
        return (ok_response.count / total) * 100.0
    
    @staticmethod
    async def get_levey_jennings_data(
        exam_name: str,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Retorna dados para gráfico Levey-Jennings"""
        start_date = (datetime.now() - timedelta(days=days)).date().isoformat()
        
        response = supabase.table("qc_records")\
            .select("date, value, target_value, target_sd, cv")\
            .eq("exam_name", exam_name)\
            .gte("date", start_date)\
            .order("date")\
            .execute()
        
        return response.data
    
    @staticmethod
    async def delete_qc_record(record_id: str) -> bool:
        """Remove registro de CQ"""
        try:
            print(f"DEBUG: Tentando deletar QC record: {record_id}")
            # Tenta deletar o registro - Por padrão retorna os dados deletados
            response = supabase.table("qc_records")\
                .delete()\
                .eq("id", record_id)\
                .execute()
            
            # Verifica se deletou algo (retornou dados)
            if response.data and len(response.data) > 0:
                print(f"DEBUG: Registro {record_id} deletado com sucesso.")
                return True
            
            # Se não tem data, verifica count se disponível (fallback)
            if hasattr(response, 'count') and response.count is not None and response.count > 0:
                print(f"DEBUG: Registro {record_id} deletado (count > 0).")
                return True
                
            # Se response.data está vazio, significa que o ID não foi encontrado ou não deletado
            print(f"DEBUG: Delete falhou ou registro não encontrado. Response data: {response.data}")
            return False
            
        except Exception as e:
            print(f"Erro ao deletar registro QC {record_id}: {e}")
            return False
