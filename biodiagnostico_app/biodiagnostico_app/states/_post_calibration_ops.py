"""
Operações de pós-calibração extraídas do QCState.
Cada função recebe `state` (instância do QCState) como primeiro argumento.
"""
import asyncio
import logging
from datetime import datetime

from ..models import QCRecord, PostCalibrationRecord
from ..services.post_calibration_service import PostCalibrationService
from ..services.qc_service import QCService
from ..utils.numeric import parse_decimal

logger = logging.getLogger(__name__)


def open_post_calibration_modal(state, record_id: str):
    """Abre o modal de pós-calibração para o registro selecionado"""
    record = next((r for r in state.qc_records if r.id == record_id), None)
    if record:
        state.selected_qc_record_for_calibration = {
            "id": record.id,
            "exam_name": record.exam_name,
            "date": record.date,
            "value": record.value,
            "cv": record.cv,
            "target_value": record.target_value,
            "status": record.status
        }
        state.show_post_calibration_modal = True
        state.post_cal_value = ""
        state.post_cal_analyst = ""
        state.post_cal_notes = ""
        state.post_cal_success_message = ""
        state.post_cal_error_message = ""


def close_post_calibration_modal(state):
    """Fecha o modal de pós-calibração"""
    state.show_post_calibration_modal = False
    state.selected_qc_record_for_calibration = None
    state.post_cal_value = ""
    state.post_cal_analyst = ""
    state.post_cal_notes = ""
    state.post_cal_success_message = ""
    state.post_cal_error_message = ""


async def save_post_calibration(state):
    """Salva o registro de medição pós-calibração no Supabase"""
    state.is_saving_post_calibration = True
    state.post_cal_success_message = ""
    state.post_cal_error_message = ""

    try:
        if not state.post_cal_value:
            state.post_cal_error_message = "Informe o valor da medição pós-calibração"
            return

        if not state.selected_qc_record_for_calibration:
            state.post_cal_error_message = "Nenhum registro selecionado"
            return

        val = parse_decimal(state.post_cal_value)
        target = float(state.selected_qc_record_for_calibration.get("target_value", 0))

        post_cv = 0.0
        if target > 0:
            diff = abs(val - target)
            post_cv = round((diff / target) * 100, 2)

        qc_record_id = state.selected_qc_record_for_calibration.get("id", "")

        db_result = await PostCalibrationService.create_record({
            "qc_record_id": qc_record_id,
            "date": datetime.now().isoformat(),
            "exam_name": state.selected_qc_record_for_calibration.get("exam_name", ""),
            "original_value": float(state.selected_qc_record_for_calibration.get("value", 0)),
            "original_cv": float(state.selected_qc_record_for_calibration.get("cv", 0)),
            "post_calibration_value": val,
            "post_calibration_cv": post_cv,
            "target_value": target,
            "analyst": state.post_cal_analyst,
            "notes": state.post_cal_notes,
        })

        new_record = PostCalibrationRecord(
            id=str(db_result.get("id", "")),
            qc_record_id=qc_record_id,
            date=datetime.now().isoformat(),
            exam_name=state.selected_qc_record_for_calibration.get("exam_name", ""),
            original_value=float(state.selected_qc_record_for_calibration.get("value", 0)),
            original_cv=float(state.selected_qc_record_for_calibration.get("cv", 0)),
            post_calibration_value=val,
            post_calibration_cv=post_cv,
            target_value=target,
            analyst=state.post_cal_analyst,
            notes=state.post_cal_notes,
            created_at=datetime.now().isoformat()
        )

        state.post_calibration_records.insert(0, new_record)

        for i, r in enumerate(state.qc_records):
            if r.id == qc_record_id:
                updated_record = QCRecord(
                    id=r.id,
                    date=r.date,
                    exam_name=r.exam_name,
                    level=r.level,
                    lot_number=r.lot_number,
                    value=r.value,
                    value1=r.value1,
                    value2=r.value2,
                    mean=r.mean,
                    sd=r.sd,
                    cv=r.cv,
                    cv_max_threshold=r.cv_max_threshold,
                    target_value=r.target_value,
                    target_sd=r.target_sd,
                    equipment=r.equipment,
                    analyst=r.analyst,
                    status=r.status,
                    westgard_violations=r.westgard_violations,
                    z_score=r.z_score,
                    reference_id=r.reference_id,
                    needs_calibration=False,
                    post_calibration_id=new_record.id
                )
                state.qc_records[i] = updated_record
                await QCService.update_qc_record(qc_record_id, {"needs_calibration": False})
                break

        state.post_cal_success_message = "Medição pós-calibração salva com sucesso!"
        await asyncio.sleep(1.5)
        close_post_calibration_modal(state)

    except ValueError:
        state.post_cal_error_message = "Valor inválido. Use números."
    except Exception as e:
        state.post_cal_error_message = f"Erro ao salvar: {str(e)}"
    finally:
        state.is_saving_post_calibration = False
