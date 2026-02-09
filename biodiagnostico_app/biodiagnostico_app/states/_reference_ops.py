"""
Operações de valores de referência extraídas do QCState.
Cada função recebe `state` (instância do QCState) como primeiro argumento.
"""
import logging

from ..models import QCReferenceValue
from ..services.qc_reference_service import QCReferenceService
from ..utils.numeric import parse_decimal

logger = logging.getLogger(__name__)


async def load_qc_references(state):
    """Carrega todos os valores de referência ativos"""
    try:
        refs = await QCReferenceService.get_references(active_only=True)
        state.qc_reference_values = [
            QCReferenceValue(
                id=r.get("id") or "",
                name=r.get("name") or "",
                exam_name=r.get("exam_name") or "",
                valid_from=r.get("valid_from") or "",
                valid_until=r.get("valid_until") or "",
                target_value=float(r.get("target_value") or 0),
                cv_max_threshold=float(r.get("cv_max_threshold") or 10.0),
                lot_number=r.get("lot_number") or "",
                manufacturer=r.get("manufacturer") or "",
                level=r.get("level") or "Normal",
                notes=r.get("notes") or "",
                is_active=r.get("is_active", True),
                created_at=r.get("created_at") or "",
                updated_at=r.get("updated_at") or ""
            )
            for r in refs
        ]
        logger.info(f"Referências carregadas: {len(state.qc_reference_values)}")
    except Exception as e:
        logger.error(f"Erro ao carregar referências: {e}")
        state.qc_reference_values = []


async def save_qc_reference(state):
    """Salva novo registro de valor referencial"""
    state.is_saving_reference = True
    state.ref_success_message = ""
    state.ref_error_message = ""

    try:
        if not state.ref_name:
            state.ref_error_message = "Nome do registro é obrigatório"
            return
        if not state.ref_exam_name:
            state.ref_error_message = "Exame é obrigatório"
            return
        if not state.ref_valid_from:
            state.ref_error_message = "Data de início é obrigatória"
            return
        if not state.ref_target_value:
            state.ref_error_message = "Valor-alvo é obrigatório"
            return

        cv_max = parse_decimal(state.ref_cv_max_threshold or "10.0", default=10.0)
        if cv_max <= 0:
            state.ref_error_message = "Limite máximo de CV% deve ser maior que zero"
            return

        target_val = parse_decimal(state.ref_target_value)
        if target_val <= 0:
            state.ref_error_message = "Valor-alvo deve ser maior que zero"
            return

        data = {
            "name": state.ref_name,
            "exam_name": state.ref_exam_name,
            "valid_from": state.ref_valid_from,
            "valid_until": state.ref_valid_until or None,
            "target_value": target_val,
            "cv_max_threshold": cv_max,
            "lot_number": state.ref_lot_number,
            "manufacturer": state.ref_manufacturer,
            "level": state.ref_level,
            "notes": state.ref_notes,
            "is_active": True
        }

        result = await QCReferenceService.create_reference(data)

        if result:
            state.ref_success_message = "Referência salva com sucesso!"
            state.ref_name = ""
            state.ref_exam_name = ""
            state.ref_valid_from = ""
            state.ref_valid_until = ""
            state.ref_target_value = ""
            state.ref_cv_max_threshold = "10.0"
            state.ref_lot_number = ""
            state.ref_manufacturer = ""
            state.ref_level = "Normal"
            state.ref_notes = ""
            await load_qc_references(state)
        else:
            state.ref_error_message = "Erro ao salvar referência"

    except ValueError as ve:
        state.ref_error_message = f"Valor inválido: {ve}"
    except Exception as e:
        state.ref_error_message = f"Erro: {e}"
    finally:
        state.is_saving_reference = False


async def deactivate_qc_reference(state, ref_id: str):
    """Desativa uma referência"""
    try:
        success = await QCReferenceService.deactivate_reference(ref_id)
        if success:
            await load_qc_references(state)
    except Exception as e:
        logger.error(f"Erro ao desativar referência: {e}")


def open_delete_reference_modal(state, ref_id: str, ref_name: str):
    """Abre modal de confirmação para excluir referência"""
    state.delete_reference_id = ref_id
    state.delete_reference_name = ref_name
    state.show_delete_reference_modal = True


def close_delete_reference_modal(state):
    """Fecha modal de confirmação de exclusão de referência"""
    state.show_delete_reference_modal = False
    state.delete_reference_id = ""
    state.delete_reference_name = ""


async def confirm_delete_reference(state):
    """Confirma e executa exclusão permanente da referência"""
    if not state.delete_reference_id:
        return

    try:
        success = await QCReferenceService.delete_reference(state.delete_reference_id)
        if success:
            state.ref_success_message = "Referência excluída permanentemente!"
            await load_qc_references(state)
        else:
            state.ref_error_message = "Erro ao excluir referência do banco de dados"
    except Exception as e:
        state.ref_error_message = f"Erro ao excluir: {e}"
    finally:
        close_delete_reference_modal(state)
