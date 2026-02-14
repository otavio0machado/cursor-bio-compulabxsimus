"""State management para outras áreas laboratoriais (Imunologia, Parasitologia, Microbiologia, Uroanálise)."""
import reflex as rx
from typing import List, Dict, Any
from datetime import datetime
from ..services.generic_qc_service import QC_SERVICES


class OutrasAreasQCMixin:
    """Mixin para adicionar funcionalidades de CQ das outras áreas ao QCState."""

    # ==========================================
    # IMUNOLOGIA
    # ==========================================

    # Parâmetros
    imuno_param_analito: str = ""
    imuno_param_modo: str = "INTERVALO"
    imuno_param_alvo: str = ""
    imuno_param_min: str = ""
    imuno_param_max: str = ""
    imuno_param_tolerancia: str = ""
    imuno_param_equipamento: str = ""
    imuno_param_lote: str = ""
    imuno_param_nivel: str = ""

    # Medições
    imuno_meas_data: str = ""
    imuno_meas_analito: str = ""
    imuno_meas_valor: str = ""
    imuno_meas_observacao: str = ""

    # Listas
    imuno_params_list: List[Dict[str, Any]] = []
    imuno_measurements_list: List[Dict[str, Any]] = []

    # ==========================================
    # PARASITOLOGIA
    # ==========================================

    # Parâmetros
    para_param_analito: str = ""
    para_param_modo: str = "INTERVALO"
    para_param_alvo: str = ""
    para_param_min: str = ""
    para_param_max: str = ""
    para_param_tolerancia: str = ""
    para_param_equipamento: str = ""
    para_param_lote: str = ""
    para_param_nivel: str = ""

    # Medições
    para_meas_data: str = ""
    para_meas_analito: str = ""
    para_meas_valor: str = ""
    para_meas_observacao: str = ""

    # Listas
    para_params_list: List[Dict[str, Any]] = []
    para_measurements_list: List[Dict[str, Any]] = []

    # ==========================================
    # MICROBIOLOGIA
    # ==========================================

    # Parâmetros
    micro_param_analito: str = ""
    micro_param_modo: str = "INTERVALO"
    micro_param_alvo: str = ""
    micro_param_min: str = ""
    micro_param_max: str = ""
    micro_param_tolerancia: str = ""
    micro_param_equipamento: str = ""
    micro_param_lote: str = ""
    micro_param_nivel: str = ""

    # Medições
    micro_meas_data: str = ""
    micro_meas_analito: str = ""
    micro_meas_valor: str = ""
    micro_meas_observacao: str = ""

    # Listas
    micro_params_list: List[Dict[str, Any]] = []
    micro_measurements_list: List[Dict[str, Any]] = []

    # ==========================================
    # UROANÁLISE
    # ==========================================

    # Parâmetros
    urine_param_analito: str = ""
    urine_param_modo: str = "INTERVALO"
    urine_param_alvo: str = ""
    urine_param_min: str = ""
    urine_param_max: str = ""
    urine_param_tolerancia: str = ""
    urine_param_equipamento: str = ""
    urine_param_lote: str = ""
    urine_param_nivel: str = ""

    # Medições
    urine_meas_data: str = ""
    urine_meas_analito: str = ""
    urine_meas_valor: str = ""
    urine_meas_observacao: str = ""

    # Listas
    urine_params_list: List[Dict[str, Any]] = []
    urine_measurements_list: List[Dict[str, Any]] = []

    # ==========================================
    # MÉTODOS GENÉRICOS (TODAS AS ÁREAS)
    # ==========================================

    async def load_area_data(self, area_id: str):
        """Carrega parâmetros e medições de uma área específica."""
        service = QC_SERVICES.get(area_id)
        if not service:
            return

        prefix = self._get_area_prefix(area_id)

        # Carregar parâmetros
        params = await service.get_all_parameters()
        setattr(self, f"{prefix}_params_list", params)

        # Carregar medições
        measurements = await service.get_all_measurements()
        setattr(self, f"{prefix}_measurements_list", measurements)

        # Inicializar data se vazio
        if not getattr(self, f"{prefix}_meas_data"):
            setattr(self, f"{prefix}_meas_data", datetime.now().strftime("%Y-%m-%d"))

    async def save_area_param(self, area_id: str):
        """Salva um parâmetro de CQ para uma área."""
        service = QC_SERVICES.get(area_id)
        if not service:
            return rx.window_alert("Área não encontrada")

        prefix = self._get_area_prefix(area_id)

        try:
            # Validações
            analito = getattr(self, f"{prefix}_param_analito")
            modo = getattr(self, f"{prefix}_param_modo")
            alvo = getattr(self, f"{prefix}_param_alvo")

            if not analito or not alvo:
                return rx.window_alert("Preencha Analito e Alvo")

            alvo_float = float(alvo.replace(",", "."))

            kwargs = {
                "analito": analito,
                "modo": modo,
                "alvo_valor": alvo_float,
                "equipamento": getattr(self, f"{prefix}_param_equipamento") or None,
                "lote_controle": getattr(self, f"{prefix}_param_lote") or None,
                "nivel_controle": getattr(self, f"{prefix}_param_nivel") or None,
            }

            if modo == "INTERVALO":
                min_val = getattr(self, f"{prefix}_param_min")
                max_val = getattr(self, f"{prefix}_param_max")
                if not min_val or not max_val:
                    return rx.window_alert("Preencha Mínimo e Máximo para modo INTERVALO")
                kwargs["min_valor"] = float(min_val.replace(",", "."))
                kwargs["max_valor"] = float(max_val.replace(",", "."))
            else:  # PERCENTUAL
                tolerancia = getattr(self, f"{prefix}_param_tolerancia")
                if not tolerancia:
                    return rx.window_alert("Preencha Tolerância para modo PERCENTUAL")
                kwargs["tolerancia_percentual"] = float(tolerancia.replace(",", "."))

            await service.create_parameter(**kwargs)

            # Limpar formulário
            self._clear_area_param_form(prefix)

            # Recarregar dados
            await self.load_area_data(area_id)

            return rx.toast.success(f"Parâmetro salvo com sucesso!")

        except ValueError as e:
            return rx.window_alert(f"Erro nos valores numéricos: {e}")
        except Exception as e:
            return rx.window_alert(f"Erro ao salvar parâmetro: {e}")

    async def register_area_measurement(self, area_id: str):
        """Registra uma medição para uma área."""
        service = QC_SERVICES.get(area_id)
        if not service:
            return rx.window_alert("Área não encontrada")

        prefix = self._get_area_prefix(area_id)

        try:
            # Validações
            data = getattr(self, f"{prefix}_meas_data")
            analito = getattr(self, f"{prefix}_meas_analito")
            valor = getattr(self, f"{prefix}_meas_valor")

            if not data or not analito or not valor:
                return rx.window_alert("Preencha Data, Analito e Valor")

            valor_float = float(valor.replace(",", "."))
            data_obj = datetime.strptime(data, "%Y-%m-%d").date()

            result = await service.register_measurement(
                data_medicao=data_obj,
                analito=analito,
                valor_medido=valor_float,
                observacao=getattr(self, f"{prefix}_meas_observacao") or None,
            )

            # Limpar formulário
            self._clear_area_meas_form(prefix)

            # Recarregar medições
            await self.load_area_data(area_id)

            status = result.get("status", "")
            if status == "APROVADO":
                return rx.toast.success(f"✅ Medição registrada: APROVADO")
            else:
                return rx.toast.error(f"❌ Medição registrada: REPROVADO")

        except ValueError as e:
            return rx.window_alert(f"Erro nos valores numéricos: {e}")
        except Exception as e:
            error_msg = str(e)
            if "Nenhum parâmetro ativo" in error_msg:
                return rx.window_alert(f"Cadastre um parâmetro para o analito '{analito}' antes de registrar medições.")
            return rx.window_alert(f"Erro ao registrar medição: {e}")

    # ==========================================
    # HELPERS PRIVADOS
    # ==========================================

    def _get_area_prefix(self, area_id: str) -> str:
        """Retorna o prefixo das variáveis de estado para cada área."""
        mapping = {
            "imunologia": "imuno",
            "parasitologia": "para",
            "microbiologia": "micro",
            "uroanalise": "urine",
        }
        return mapping.get(area_id, area_id)

    def _clear_area_param_form(self, prefix: str):
        """Limpa o formulário de parâmetros."""
        setattr(self, f"{prefix}_param_analito", "")
        setattr(self, f"{prefix}_param_modo", "INTERVALO")
        setattr(self, f"{prefix}_param_alvo", "")
        setattr(self, f"{prefix}_param_min", "")
        setattr(self, f"{prefix}_param_max", "")
        setattr(self, f"{prefix}_param_tolerancia", "")
        setattr(self, f"{prefix}_param_equipamento", "")
        setattr(self, f"{prefix}_param_lote", "")
        setattr(self, f"{prefix}_param_nivel", "")

    def _clear_area_meas_form(self, prefix: str):
        """Limpa o formulário de medições."""
        setattr(self, f"{prefix}_meas_analito", "")
        setattr(self, f"{prefix}_meas_valor", "")
        setattr(self, f"{prefix}_meas_observacao", "")
        # Manter data preenchida com hoje
        setattr(self, f"{prefix}_meas_data", datetime.now().strftime("%Y-%m-%d"))
