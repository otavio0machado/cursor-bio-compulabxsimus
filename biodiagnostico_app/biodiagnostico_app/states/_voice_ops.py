"""
Operações de Voice-to-Form extraídas do QCState.
Cada função recebe `state` (instância do QCState) como primeiro argumento.
"""
import asyncio
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


def open_voice_modal(state, form_type: str):
    state.show_voice_modal = True
    state.voice_form_target = form_type
    state.voice_is_recording = False
    state.voice_is_processing = False
    state.voice_audio_base64 = ""
    state.voice_status_message = "Toque no microfone para iniciar"
    state.voice_error_message = ""


def close_voice_modal(state):
    state.show_voice_modal = False
    state.voice_form_target = ""
    state.voice_is_recording = False
    state.voice_is_processing = False
    state.voice_audio_base64 = ""
    state.voice_status_message = ""
    state.voice_error_message = ""


def set_voice_recording(state, is_recording: bool):
    state.voice_is_recording = is_recording
    if is_recording:
        state.voice_status_message = "Gravando... Fale os dados do formulario"
        state.voice_error_message = ""
    else:
        state.voice_status_message = "Gravacao finalizada"


def receive_voice_audio(state, audio_base64: str):
    state.voice_audio_base64 = audio_base64
    state.voice_is_recording = False


async def process_voice_audio(state):
    if not state.voice_audio_base64:
        state.voice_error_message = "Nenhum audio capturado. Tente novamente."
        return

    state.voice_is_processing = True
    state.voice_status_message = "Analisando audio com IA..."
    state.voice_error_message = ""

    try:
        from ..services.voice_ai_service import VoiceAIService
        result = await VoiceAIService.process_audio(
            audio_base64=state.voice_audio_base64,
            form_type=state.voice_form_target,
        )

        if "error" in result:
            state.voice_error_message = result["error"]
            state.voice_status_message = ""
            return

        apply_voice_data(state, result)
        state.voice_status_message = "Campos preenchidos com sucesso!"
        state.voice_error_message = ""
        return True  # signals caller to yield + close modal

    except Exception as e:
        logger.error(f"Voice processing error: {e}")
        state.voice_error_message = f"Erro: {str(e)}"
        state.voice_status_message = ""
        return False
    finally:
        state.voice_is_processing = False


def apply_voice_data(state, data: Dict[str, Any]):
    target = state.voice_form_target

    if target == "registro":
        if data.get("exam_name"):
            state.qc_exam_name = data["exam_name"]
        if data.get("value") is not None:
            state.qc_value = str(data["value"])
        if data.get("target_value") is not None:
            state.qc_target_value = str(data["target_value"])
            state.calculate_sd()
        if data.get("equipment"):
            state.qc_equipment = data["equipment"]
        if data.get("analyst"):
            state.qc_analyst = data["analyst"]

    elif target == "referencia":
        if data.get("name"):
            state.ref_name = data["name"]
        if data.get("exam_name"):
            state.ref_exam_name = data["exam_name"]
        if data.get("level"):
            state.ref_level = data["level"]
        if data.get("valid_from"):
            state.ref_valid_from = data["valid_from"]
        if data.get("valid_until"):
            state.ref_valid_until = data["valid_until"]
        if data.get("target_value") is not None:
            state.ref_target_value = str(data["target_value"])
        if data.get("cv_max") is not None:
            state.ref_cv_max_threshold = str(data["cv_max"])
        if data.get("lot_number"):
            state.ref_lot_number = data["lot_number"]
        if data.get("manufacturer"):
            state.ref_manufacturer = data["manufacturer"]
        if data.get("notes"):
            state.ref_notes = data["notes"]

    elif target == "reagente":
        if data.get("name"):
            state.reagent_name = data["name"]
        if data.get("lot_number"):
            state.reagent_lot_number = data["lot_number"]
        if data.get("expiry_date"):
            state.reagent_expiry_date = data["expiry_date"]
        if data.get("initial_stock") is not None:
            state.reagent_initial_stock = str(data["initial_stock"])
        if data.get("daily_consumption") is not None:
            state.reagent_daily_consumption = str(data["daily_consumption"])
        if data.get("manufacturer"):
            state.reagent_manufacturer = data["manufacturer"]

    elif target == "manutencao":
        if data.get("equipment"):
            state.maintenance_equipment = data["equipment"]
        if data.get("type"):
            state.maintenance_type = data["type"]
        if data.get("date"):
            state.maintenance_date = data["date"]
        if data.get("next_date"):
            state.maintenance_next_date = data["next_date"]
        if data.get("notes"):
            state.maintenance_notes = data["notes"]
