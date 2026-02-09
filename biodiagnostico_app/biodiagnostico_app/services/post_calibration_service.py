"""
Servico de Registros Pos-Calibracao
"""
import logging
from typing import List, Optional, Dict, Any
from .supabase_client import SupabaseClient
from .exceptions import ServiceError
from .types import PostCalibrationRow

logger = logging.getLogger(__name__)


def get_supabase():
    client = SupabaseClient.get_client()
    if client is None:
        raise Exception("Cliente Supabase não inicializado.")
    return client


class PostCalibrationService:
    """CRUD para registros de pós-calibração no Supabase"""

    @staticmethod
    async def create_record(data: Dict[str, Any]) -> PostCalibrationRow:
        insert_data = {
            "qc_record_id": data.get("qc_record_id"),
            "date": data.get("date"),
            "exam_name": data.get("exam_name"),
            "original_value": float(data.get("original_value", 0)),
            "original_cv": float(data.get("original_cv", 0)),
            "post_calibration_value": float(data.get("post_calibration_value", 0)),
            "post_calibration_cv": float(data.get("post_calibration_cv", 0)),
            "target_value": float(data.get("target_value", 0)),
            "analyst": data.get("analyst"),
            "notes": data.get("notes"),
        }
        insert_data = {k: v for k, v in insert_data.items() if v is not None}
        response = get_supabase().table("post_calibration_records").insert(insert_data).execute()
        if not response.data:
            raise ServiceError("Insert em post_calibration_records não retornou dados.")
        return response.data[0]

    @staticmethod
    async def get_records(limit: int = 200) -> List[PostCalibrationRow]:
        response = get_supabase().table("post_calibration_records")\
            .select("*")\
            .order("created_at", desc=True)\
            .limit(limit)\
            .execute()
        return response.data if response.data else []

    @staticmethod
    async def get_by_qc_record_id(qc_record_id: str) -> Optional[PostCalibrationRow]:
        response = get_supabase().table("post_calibration_records")\
            .select("*")\
            .eq("qc_record_id", qc_record_id)\
            .order("created_at", desc=True)\
            .limit(1)\
            .execute()
        return response.data[0] if response.data else None

    @staticmethod
    async def delete_record(record_id: str) -> bool:
        try:
            get_supabase().table("post_calibration_records").delete().eq("id", record_id).execute()
            verify = get_supabase().table("post_calibration_records").select("id").eq("id", record_id).execute()
            return not verify.data
        except Exception as e:
            logger.error(f"Erro ao deletar post_calibration record {record_id}: {e}")
            return False
