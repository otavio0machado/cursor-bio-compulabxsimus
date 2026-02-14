"""Service genérico para CQ de todas as áreas laboratoriais."""
from typing import Optional
from datetime import date
from ..services.supabase_client import supabase


class GenericQCService:
    """Service layer genérico para CQ (Imunologia, Parasitologia, Microbiologia, Uroanálise)."""

    def __init__(self, area_prefix: str, rpc_function: str):
        """
        Inicializa o service com prefixo da área.

        Args:
            area_prefix: Prefixo das tabelas (ex: 'immunology', 'parasitology', 'microbiology', 'urine')
            rpc_function: Nome da função RPC (ex: 'immunology_register_qc_measurement')
        """
        self.area_prefix = area_prefix
        self.rpc_function = rpc_function
        self.params_table = f"{area_prefix}_qc_parameters"
        self.measurements_table = f"{area_prefix}_qc_measurements"

    # ==========================================
    # PARÂMETROS
    # ==========================================

    async def get_all_parameters(self):
        """Retorna todos os parâmetros ativos."""
        try:
            response = (
                supabase.table(self.params_table)
                .select("*")
                .eq("is_active", True)
                .order("created_at", desc=True)
                .execute()
            )
            return response.data or []
        except Exception as e:
            print(f"[{self.area_prefix.upper()}] Erro ao buscar parâmetros:", e)
            return []

    async def create_parameter(
        self,
        analito: str,
        modo: str,
        alvo_valor: float,
        min_valor: Optional[float] = None,
        max_valor: Optional[float] = None,
        tolerancia_percentual: Optional[float] = None,
        equipamento: Optional[str] = None,
        lote_controle: Optional[str] = None,
        nivel_controle: Optional[str] = None,
    ) -> dict:
        """Cria um novo parâmetro de CQ."""
        try:
            data = {
                "analito": analito,
                "modo": modo,
                "alvo_valor": alvo_valor,
                "equipamento": equipamento,
                "lote_controle": lote_controle,
                "nivel_controle": nivel_controle,
                "is_active": True,
            }

            if modo == "INTERVALO":
                data["min_valor"] = min_valor
                data["max_valor"] = max_valor
            else:  # PERCENTUAL
                data["tolerancia_percentual"] = tolerancia_percentual

            response = supabase.table(self.params_table).insert(data).execute()
            return response.data[0] if response.data else {}
        except Exception as e:
            print(f"[{self.area_prefix.upper()}] Erro ao criar parâmetro:", e)
            raise e

    async def update_parameter(self, param_id: str, updates: dict) -> dict:
        """Atualiza um parâmetro existente."""
        try:
            response = (
                supabase.table(self.params_table)
                .update(updates)
                .eq("id", param_id)
                .execute()
            )
            return response.data[0] if response.data else {}
        except Exception as e:
            print(f"[{self.area_prefix.upper()}] Erro ao atualizar parâmetro:", e)
            raise e

    async def delete_parameter(self, param_id: str) -> bool:
        """Soft delete: marca parâmetro como inativo."""
        try:
            await self.update_parameter(param_id, {"is_active": False})
            return True
        except Exception as e:
            print(f"[{self.area_prefix.upper()}] Erro ao deletar parâmetro:", e)
            return False

    # ==========================================
    # MEDIÇÕES
    # ==========================================

    async def get_all_measurements(
        self,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None,
        analito: Optional[str] = None,
    ):
        """Retorna medições com filtros opcionais."""
        try:
            query = supabase.table(self.measurements_table).select("*")

            if data_inicio:
                query = query.gte("data_medicao", data_inicio.isoformat())
            if data_fim:
                query = query.lte("data_medicao", data_fim.isoformat())
            if analito:
                query = query.eq("analito", analito)

            response = query.order("data_medicao", desc=True).execute()
            return response.data or []
        except Exception as e:
            print(f"[{self.area_prefix.upper()}] Erro ao buscar medições:", e)
            return []

    async def register_measurement(
        self,
        data_medicao: date,
        analito: str,
        valor_medido: float,
        equipamento: Optional[str] = None,
        lote_controle: Optional[str] = None,
        nivel_controle: Optional[str] = None,
        observacao: Optional[str] = None,
    ) -> dict:
        """Registra uma nova medição via RPC."""
        try:
            params = {
                "p_data_medicao": data_medicao.isoformat(),
                "p_analito": analito,
                "p_valor_medido": float(valor_medido),
            }

            if equipamento:
                params["p_equipamento"] = equipamento
            if lote_controle:
                params["p_lote_controle"] = lote_controle
            if nivel_controle:
                params["p_nivel_controle"] = nivel_controle
            if observacao:
                params["p_observacao"] = observacao

            response = supabase.rpc(self.rpc_function, params).execute()
            return response.data
        except Exception as e:
            print(f"[{self.area_prefix.upper()}] Erro ao registrar medição:", e)
            raise e


# ==========================================
# INSTÂNCIAS ESPECÍFICAS POR ÁREA
# ==========================================

immunology_service = GenericQCService("immunology", "immunology_register_qc_measurement")
parasitology_service = GenericQCService("parasitology", "parasitology_register_qc_measurement")
microbiology_service = GenericQCService("microbiology", "microbiology_register_qc_measurement")
urine_service = GenericQCService("urine", "urine_register_qc_measurement")


# Mapeamento para facilitar acesso
QC_SERVICES = {
    "imunologia": immunology_service,
    "parasitologia": parasitology_service,
    "microbiologia": microbiology_service,
    "uroanalise": urine_service,
}
