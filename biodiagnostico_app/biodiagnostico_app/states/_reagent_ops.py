"""
Operações de reagentes extraídas do QCState.
Cada função recebe `state` (instância do QCState) como primeiro argumento.
"""
import logging
from datetime import datetime

from ..models import ReagentLot
from ..services.reagent_service import ReagentService

logger = logging.getLogger(__name__)


async def save_reagent_lot(state):
    """Salva um novo lote de reagente no Supabase"""
    state.is_saving_reagent = True
    state.reagent_error_message = ""
    state.reagent_success_message = ""
    try:
        if not state.reagent_name.strip():
            state.reagent_error_message = "Nome do reagente é obrigatório."
            return
        if not state.reagent_lot_number.strip():
            state.reagent_error_message = "Número do lote é obrigatório."
            return
        if not state.reagent_expiry_date:
            state.reagent_error_message = "Data de validade é obrigatória."
            return

        db_result = await ReagentService.create_lot({
            "name": state.reagent_name,
            "lot_number": state.reagent_lot_number,
            "expiry_date": state.reagent_expiry_date,
            "quantity": state.reagent_quantity,
            "manufacturer": state.reagent_manufacturer,
            "storage_temp": state.reagent_storage_temp,
            "current_stock": float(state.reagent_initial_stock or 0),
            "estimated_consumption": float(state.reagent_daily_consumption or 0),
        })

        days_left = 0
        if state.reagent_expiry_date:
            try:
                expiry_dt = datetime.strptime(state.reagent_expiry_date, "%Y-%m-%d").date()
                days_left = (expiry_dt - datetime.now().date()).days
            except ValueError:
                pass

        new_lot = ReagentLot(
            id=str(db_result.get("id", "")),
            name=state.reagent_name,
            lot_number=state.reagent_lot_number,
            expiry_date=state.reagent_expiry_date,
            quantity=state.reagent_quantity,
            manufacturer=state.reagent_manufacturer,
            storage_temp=state.reagent_storage_temp,
            current_stock=float(state.reagent_initial_stock or 0),
            estimated_consumption=float(state.reagent_daily_consumption or 0),
            created_at=datetime.now().isoformat(),
            days_left=days_left,
        )
        state.reagent_lots.insert(0, new_lot)
        state.reagent_success_message = "Lote salvo com sucesso!"
        state.reagent_name = ""
        state.reagent_lot_number = ""
    except Exception as e:
        state.reagent_error_message = f"Erro ao salvar: {str(e)}"
    finally:
        state.is_saving_reagent = False


async def delete_reagent_lot(state, lot_id: str):
    """Deleta lote de reagente do Supabase"""
    try:
        await ReagentService.delete_lot(lot_id)
    except Exception as e:
        logger.error(f"Erro ao deletar lote: {e}")
    state.reagent_lots = [lot for lot in state.reagent_lots if lot.id != lot_id]
