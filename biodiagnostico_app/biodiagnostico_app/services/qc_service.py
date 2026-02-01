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
        # Prepara os dados para inserção
        # NOTA: 'cv' e 'status' são colunas geradas no banco, não devem ser inseridas
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
            "reference_id": record_data.get("reference_id"),
            "needs_calibration": record_data.get("needs_calibration", False),
        }

        # Remove campos None para evitar erros no Supabase
        data = {k: v for k, v in data.items() if v is not None}

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
                # status is a generated column
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
    async def update_qc_record(record_id: str, data: Dict[str, Any]) -> bool:
        """Atualiza campos de um registro de CQ"""
        try:
            if not record_id:
                return False
            update_data = {k: v for k, v in data.items() if v is not None}
            if not update_data:
                return False
            response = supabase.table("qc_records").update(update_data).eq("id", record_id).execute()
            return bool(response.data)
        except Exception as e:
            print(f"Erro ao atualizar QC record {record_id}: {e}")
            return False

    @staticmethod
    async def update_qc_records(records: List[Dict[str, Any]]) -> int:
        """Atualiza múltiplos registros de CQ (lote simples em loop)"""
        updated = 0
        for record in records:
            record_id = record.get("id")
            data = {k: v for k, v in record.items() if k != "id"}
            if await QCService.update_qc_record(record_id, data):
                updated += 1
        return updated
    
    @staticmethod
    async def delete_qc_record(record_id: str) -> bool:
        """Remove registro de CQ"""
        try:
            print(f"DEBUG: Tentando deletar QC record: {record_id}")

            # Primeiro verifica se o registro existe
            check = supabase.table("qc_records").select("id").eq("id", record_id).execute()
            if not check.data or len(check.data) == 0:
                print(f"DEBUG: Registro {record_id} não encontrado no banco.")
                return False

            # Deleta o registro
            response = supabase.table("qc_records")\
                .delete()\
                .eq("id", record_id)\
                .execute()

            # DELETE no Supabase pode retornar lista vazia mesmo quando bem-sucedido
            # Verifica novamente se o registro ainda existe
            verify = supabase.table("qc_records").select("id").eq("id", record_id).execute()
            if not verify.data or len(verify.data) == 0:
                print(f"DEBUG: Registro {record_id} deletado com sucesso (verificado).")
                return True

            print(f"DEBUG: Delete falhou - registro ainda existe.")
            return False

        except Exception as e:
            print(f"Erro ao deletar registro QC {record_id}: {e}")
            return False
