"""
Operações de manutenção extraídas do QCState.
Cada função recebe `state` (instância do QCState) como primeiro argumento.
"""
import logging
from datetime import datetime

from ..models import MaintenanceRecord
from ..services.maintenance_service import MaintenanceService

logger = logging.getLogger(__name__)


async def save_maintenance_record(state):
    """Registra manutenção no Supabase"""
    state.is_saving_maintenance = True
    state.maintenance_error_message = ""
    state.maintenance_success_message = ""
    try:
        if not state.maintenance_equipment.strip():
            state.maintenance_error_message = "Equipamento é obrigatório."
            return
        if not state.maintenance_type:
            state.maintenance_error_message = "Tipo de manutenção é obrigatório."
            return
        if not state.maintenance_date:
            state.maintenance_error_message = "Data é obrigatória."
            return

        db_result = await MaintenanceService.create_record({
            "equipment": state.maintenance_equipment,
            "type": state.maintenance_type,
            "date": state.maintenance_date,
            "next_date": state.maintenance_next_date,
            "technician": state.maintenance_technician,
            "notes": state.maintenance_notes,
        })

        new_record = MaintenanceRecord(
            id=str(db_result.get("id", "")),
            equipment=state.maintenance_equipment,
            type=state.maintenance_type,
            date=state.maintenance_date,
            next_date=state.maintenance_next_date,
            technician=state.maintenance_technician,
            notes=state.maintenance_notes,
            created_at=datetime.now().isoformat()
        )
        state.maintenance_records.insert(0, new_record)
        state.maintenance_success_message = "Manutenção registrada!"
        state.maintenance_equipment = ""
        state.maintenance_notes = ""
    except Exception as e:
        state.maintenance_error_message = f"Erro ao salvar: {str(e)}"
    finally:
        state.is_saving_maintenance = False


async def delete_maintenance_record(state, record_id: str):
    """Deleta registro de manutenção do Supabase"""
    try:
        await MaintenanceService.delete_record(record_id)
    except Exception as e:
        logger.error(f"Erro ao deletar manutenção: {e}")
    state.maintenance_records = [r for r in state.maintenance_records if r.id != record_id]
