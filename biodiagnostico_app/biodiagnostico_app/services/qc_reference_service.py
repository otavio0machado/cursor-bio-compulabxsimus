"""
Servico de Valores Referenciais do CQ
Gerencia cadastro de valores-alvo e tolerancias de CV% por exame
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from .supabase_client import SupabaseClient


def get_supabase():
    """Obtém cliente Supabase de forma lazy"""
    client = SupabaseClient.get_client()
    if client is None:
        raise Exception("Cliente Supabase não inicializado. Verifique SUPABASE_URL e SUPABASE_KEY.")
    return client


class QCReferenceService:
    """Operacoes CRUD para Valores Referenciais de CQ"""

    @staticmethod
    async def create_reference(data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria novo registro de referencia"""
        insert_data = {
            "name": data.get("name"),
            "exam_name": data.get("exam_name"),
            "valid_from": data.get("valid_from"),
            "valid_until": data.get("valid_until") or None,
            "target_value": float(data.get("target_value", 0)),
            "cv_max_threshold": float(data.get("cv_max_threshold", 10.0)),
            "lot_number": data.get("lot_number") or None,
            "manufacturer": data.get("manufacturer") or None,
            "level": data.get("level", "Normal"),
            "notes": data.get("notes") or None,
            "is_active": data.get("is_active", True),
        }

        response = get_supabase().table("qc_reference_values").insert(insert_data).execute()
        return response.data[0] if response.data else {}

    @staticmethod
    async def get_references(
        exam_name: Optional[str] = None,
        active_only: bool = True,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Busca registros de referencia com filtros"""
        query = get_supabase().table("qc_reference_values").select("*")

        if exam_name:
            query = query.eq("exam_name", exam_name)
        if active_only:
            query = query.eq("is_active", True)

        query = query.order("valid_from", desc=True).limit(limit)
        response = query.execute()

        return response.data if response.data else []

    @staticmethod
    async def get_references_by_ids(ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """Busca referencias por uma lista de IDs"""
        unique_ids = list({i for i in ids if i})
        if not unique_ids:
            return {}

        response = get_supabase().table("qc_reference_values")\
            .select("*")\
            .in_("id", unique_ids)\
            .execute()

        if not response.data:
            return {}

        return {r.get("id"): r for r in response.data if r.get("id")}

    @staticmethod
    async def get_active_reference_for_exam(
        exam_name: str,
        level: str = "Normal",
        reference_date: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Busca a referencia ativa mais recente para um exame.

        Logica: valid_from <= reference_date AND (valid_until IS NULL OR valid_until >= reference_date)
        Ordenado por valid_from DESC (mais recente primeiro).

        Args:
            exam_name: Nome canonico do exame
            level: Nivel do controle (Normal, N1, N2, N3)
            reference_date: Data de referencia (se None, usa data atual)

        Returns:
            Dict com dados da referencia ativa ou None se nao encontrada
        """
        if reference_date is None:
            reference_date = datetime.now().date().isoformat()

        # Busca referencias ativas para o exame/nivel onde valid_from <= data
        query = get_supabase().table("qc_reference_values")\
            .select("*")\
            .eq("exam_name", exam_name)\
            .eq("level", level)\
            .eq("is_active", True)\
            .lte("valid_from", reference_date)\
            .order("valid_from", desc=True)\
            .limit(1)

        response = query.execute()

        if not response.data:
            return None

        ref = response.data[0]

        # Verifica se valid_until permite (NULL ou >= reference_date)
        valid_until = ref.get("valid_until")
        if valid_until and valid_until < reference_date:
            return None

        return ref

    @staticmethod
    async def get_all_exams_with_references() -> Dict[str, Dict[str, Any]]:
        """
        Retorna um mapa {exam_name: {target_value, cv_ok_threshold, cv_alert_threshold, ...}}
        para todos os exames com referencia ativa atual.

        Util para carregar todas as referencias de uma vez.
        """
        today = datetime.now().date().isoformat()

        response = get_supabase().table("qc_reference_values")\
            .select("*")\
            .eq("is_active", True)\
            .lte("valid_from", today)\
            .order("valid_from", desc=True)\
            .execute()

        if not response.data:
            return {}

        # Agrupa por exam_name + level, mantendo apenas o mais recente
        exam_map: Dict[str, Dict[str, Any]] = {}
        for ref in response.data:
            key = f"{ref['exam_name']}|{ref.get('level', 'Normal')}"
            if key not in exam_map:
                # Verifica valid_until
                valid_until = ref.get("valid_until")
                if valid_until is None or valid_until >= today:
                    exam_map[key] = ref

        return exam_map

    @staticmethod
    async def update_reference(id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Atualiza registro de referencia existente"""
        update_data = {}

        # Apenas atualiza campos fornecidos
        if "name" in data:
            update_data["name"] = data["name"]
        if "exam_name" in data:
            update_data["exam_name"] = data["exam_name"]
        if "valid_from" in data:
            update_data["valid_from"] = data["valid_from"]
        if "valid_until" in data:
            update_data["valid_until"] = data["valid_until"] or None
        if "target_value" in data:
            update_data["target_value"] = float(data["target_value"])
        if "cv_max_threshold" in data:
            update_data["cv_max_threshold"] = float(data["cv_max_threshold"])
        if "lot_number" in data:
            update_data["lot_number"] = data["lot_number"] or None
        if "manufacturer" in data:
            update_data["manufacturer"] = data["manufacturer"] or None
        if "level" in data:
            update_data["level"] = data["level"]
        if "notes" in data:
            update_data["notes"] = data["notes"] or None
        if "is_active" in data:
            update_data["is_active"] = data["is_active"]

        if not update_data:
            return {}

        response = get_supabase().table("qc_reference_values")\
            .update(update_data)\
            .eq("id", id)\
            .execute()

        return response.data[0] if response.data else {}

    @staticmethod
    async def deactivate_reference(id: str) -> bool:
        """Desativa (soft delete) um registro de referencia"""
        try:
            response = get_supabase().table("qc_reference_values")\
                .update({"is_active": False})\
                .eq("id", id)\
                .execute()

            return len(response.data) > 0 if response.data else False
        except Exception as e:
            print(f"Erro ao desativar referencia {id}: {e}")
            return False

    @staticmethod
    async def delete_reference(id: str) -> bool:
        """Remove permanentemente um registro de referencia"""
        try:
            print(f"DEBUG: Tentando deletar referência: {id}")

            # Primeiro verifica se o registro existe
            check = get_supabase().table("qc_reference_values").select("id").eq("id", id).execute()
            if not check.data or len(check.data) == 0:
                print(f"DEBUG: Referência {id} não encontrada no banco.")
                return False

            # Deleta o registro
            get_supabase().table("qc_reference_values")\
                .delete()\
                .eq("id", id)\
                .execute()

            # Verifica se foi realmente deletado
            verify = get_supabase().table("qc_reference_values").select("id").eq("id", id).execute()
            if not verify.data or len(verify.data) == 0:
                print(f"DEBUG: Referência {id} deletada com sucesso (verificado).")
                return True

            print(f"DEBUG: Delete falhou - referência ainda existe.")
            return False
        except Exception as e:
            print(f"Erro ao deletar referencia {id}: {e}")
            return False

    @staticmethod
    async def get_reference_by_id(id: str) -> Optional[Dict[str, Any]]:
        """Busca uma referencia pelo ID"""
        response = get_supabase().table("qc_reference_values")\
            .select("*")\
            .eq("id", id)\
            .limit(1)\
            .execute()

        return response.data[0] if response.data else None
