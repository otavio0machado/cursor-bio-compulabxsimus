"""
Serviço de CQ Hematologia — Parâmetros (Intervalo/Percentual) e Medições.
"""
import logging
from typing import List, Optional, Dict, Any
from .supabase_client import SupabaseClient
from .exceptions import ServiceError
from .types import HematologyQCParameterRow, HematologyQCMeasurementRow, HematologyBioRecordRow

logger = logging.getLogger(__name__)


def get_supabase():
    """Cliente admin (service_role) — ignora RLS para tabelas de hematologia."""
    client = SupabaseClient.get_admin_client()
    if client is None:
        raise Exception("Cliente Supabase não inicializado.")
    return client


class HematologyQCService:
    """CRUD para parâmetros e medições de CQ Hematologia no Supabase"""

    # ── Parâmetros (regras) ──

    @staticmethod
    async def get_parameters(active_only: bool = True, limit: int = 200) -> List[HematologyQCParameterRow]:
        """Busca parâmetros da VIEW resolvida (com min_calc, max_calc, percentual_equivalente)"""
        query = get_supabase().table("v_hematology_qc_parameters_resolved").select("*")
        if active_only:
            query = query.eq("is_active", True)
        query = query.order("analito").order("created_at", desc=True).limit(limit)
        response = query.execute()
        return response.data if response.data else []

    @staticmethod
    async def create_parameter(data: Dict[str, Any]) -> HematologyQCParameterRow:
        """Cria novo parâmetro de CQ"""
        insert_data = {
            "analito": data["analito"],
            "modo": data["modo"],
            "alvo_valor": float(data["alvo_valor"]),
        }
        # Campos opcionais
        for field in ("equipamento", "lote_controle", "nivel_controle"):
            val = data.get(field)
            if val and str(val).strip():
                insert_data[field] = str(val).strip()

        # Campos condicionais por modo
        if data["modo"] == "INTERVALO":
            insert_data["min_valor"] = float(data["min_valor"])
            insert_data["max_valor"] = float(data["max_valor"])
        else:  # PERCENTUAL
            insert_data["tolerancia_percentual"] = float(data["tolerancia_percentual"])

        response = get_supabase().table("hematology_qc_parameters").insert(insert_data).execute()
        if not response.data:
            raise ServiceError("Insert em hematology_qc_parameters não retornou dados.")
        return response.data[0]

    @staticmethod
    async def update_parameter(param_id: str, data: Dict[str, Any]) -> bool:
        """Atualiza parâmetro existente"""
        try:
            if not param_id:
                return False
            update_data = {k: v for k, v in data.items() if v is not None}
            if not update_data:
                return False
            response = get_supabase().table("hematology_qc_parameters")\
                .update(update_data).eq("id", param_id).execute()
            return bool(response.data)
        except Exception as e:
            logger.error(f"Erro ao atualizar parâmetro {param_id}: {e}")
            return False

    @staticmethod
    async def toggle_parameter_active(param_id: str, is_active: bool) -> bool:
        """Ativa ou inativa um parâmetro"""
        return await HematologyQCService.update_parameter(param_id, {"is_active": is_active})

    @staticmethod
    async def delete_parameter(param_id: str) -> bool:
        """Exclui parâmetro permanentemente"""
        try:
            get_supabase().table("hematology_qc_parameters").delete().eq("id", param_id).execute()
            verify = get_supabase().table("hematology_qc_parameters").select("id").eq("id", param_id).execute()
            return not verify.data
        except Exception as e:
            logger.error(f"Erro ao deletar parâmetro {param_id}: {e}")
            return False

    # ── Medições ──

    @staticmethod
    async def get_measurements(
        limit: int = 200,
        analito: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[HematologyQCMeasurementRow]:
        """Busca medições com filtros opcionais"""
        query = get_supabase().table("hematology_qc_measurements").select("*")
        if analito:
            query = query.eq("analito", analito)
        if status:
            query = query.eq("status", status)
        if start_date:
            query = query.gte("data_medicao", start_date)
        if end_date:
            query = query.lte("data_medicao", end_date)
        query = query.order("data_medicao", desc=True).order("created_at", desc=True).limit(limit)
        response = query.execute()
        return response.data if response.data else []

    @staticmethod
    async def register_measurement(data: Dict[str, Any]) -> Dict[str, Any]:
        """Registra medição usando a RPC do banco (hematology_register_qc_measurement)"""
        params = {
            "p_data_medicao": data["data_medicao"],
            "p_analito": data["analito"],
            "p_valor_medido": float(data["valor_medido"]),
        }
        for field, key in [
            ("p_equipamento", "equipamento"),
            ("p_lote_controle", "lote_controle"),
            ("p_nivel_controle", "nivel_controle"),
            ("p_observacao", "observacao"),
        ]:
            val = data.get(key)
            if val and str(val).strip():
                params[field] = str(val).strip()

        response = get_supabase().rpc("hematology_register_qc_measurement", params).execute()
        if not response.data:
            raise ServiceError("RPC hematology_register_qc_measurement não retornou dados.")
        return response.data

    @staticmethod
    async def delete_measurement(meas_id: str) -> bool:
        """Exclui medição permanentemente"""
        try:
            get_supabase().table("hematology_qc_measurements").delete().eq("id", meas_id).execute()
            verify = get_supabase().table("hematology_qc_measurements").select("id").eq("id", meas_id).execute()
            return not verify.data
        except Exception as e:
            logger.error(f"Erro ao deletar medição {meas_id}: {e}")
            return False

    # ── Registros Bio x Controle Interno ──

    @staticmethod
    async def get_bio_records(limit: int = 200) -> List[HematologyBioRecordRow]:
        """Busca registros da tabela Bio x CI"""
        query = get_supabase().table("hematology_bio_records").select("*")
        query = query.order("data_bio", desc=True).order("created_at", desc=True).limit(limit)
        response = query.execute()
        return response.data if response.data else []

    @staticmethod
    async def save_bio_record(data: Dict[str, Any]) -> HematologyBioRecordRow:
        """Salva registro Bio x CI no banco"""
        response = get_supabase().table("hematology_bio_records").insert(data).execute()
        if not response.data:
            raise ServiceError("Insert em hematology_bio_records não retornou dados.")
        return response.data[0]

    @staticmethod
    async def delete_bio_record(record_id: str) -> bool:
        """Exclui registro Bio x CI"""
        try:
            get_supabase().table("hematology_bio_records").delete().eq("id", record_id).execute()
            verify = get_supabase().table("hematology_bio_records").select("id").eq("id", record_id).execute()
            return not verify.data
        except Exception as e:
            logger.error(f"Erro ao deletar registro bio {record_id}: {e}")
            return False
