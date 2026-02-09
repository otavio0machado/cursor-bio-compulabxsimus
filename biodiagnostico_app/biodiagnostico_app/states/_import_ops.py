"""
Operações de importação de planilha extraídas do QCState.
Cada função recebe `state` (instância do QCState) como primeiro argumento.
"""
import io
import logging
from datetime import datetime

import pandas as pd

from ..services.qc_service import QCService

logger = logging.getLogger(__name__)

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
MAX_ROWS = 10_000
ALLOWED_EXTENSIONS = (".xlsx", ".xls")


async def handle_proin_upload(state, files):
    """Handle upload of ProIn Excel file"""
    state.is_importing = True
    state.upload_progress = 10

    try:
        for file in files:
            filename = getattr(file, "filename", "") or getattr(file, "name", "") or ""
            if not filename.lower().endswith(ALLOWED_EXTENSIONS):
                state.qc_error_message = (
                    f"Formato inválido: '{filename}'. Aceitos: .xlsx, .xls"
                )
                return

            upload_data = await file.read()

            if len(upload_data) > MAX_FILE_SIZE_BYTES:
                size_mb = round(len(upload_data) / (1024 * 1024), 1)
                state.qc_error_message = (
                    f"Arquivo muito grande ({size_mb} MB). Limite: 10 MB."
                )
                return

            df = pd.read_excel(io.BytesIO(upload_data))

            if len(df) > MAX_ROWS:
                state.qc_error_message = (
                    f"Planilha com {len(df)} linhas excede o limite de {MAX_ROWS}."
                )
                return

            state.proin_import_headers = list(df.columns)
            state.proin_import_preview = df.head(5).values.tolist()
            state.proin_import_data = df.to_dict('records')
            state.upload_progress = 100
    except Exception as e:
        state.qc_error_message = f"Erro ao processar arquivo: {str(e)}"
    finally:
        state.is_importing = False


async def process_proin_import(state):
    """Process the imported data and save to DB"""
    try:
        if not state.proin_import_data:
            state.qc_error_message = "Nenhum dado para importar."
            return

        records_to_save = []
        for row in state.proin_import_data:
            record_data = {
                "date": str(row.get("date", row.get("data", row.get("DATA", datetime.now().isoformat())))),
                "exam_name": str(row.get("exam_name", row.get("exame", row.get("EXAME", "")))),
                "level": str(row.get("level", row.get("nivel", row.get("NIVEL", "Normal")))),
                "lot_number": str(row.get("lot_number", row.get("lote", row.get("LOTE", "")))),
                "value": float(row.get("value", row.get("valor", row.get("VALOR", 0)))),
                "target_value": float(row.get("target_value", row.get("alvo", row.get("ALVO", 0)))),
                "target_sd": float(row.get("target_sd", row.get("dp", row.get("DP", 0)))),
                "equipment": str(row.get("equipment", row.get("equipamento", row.get("EQUIPAMENTO", "")))),
                "analyst": str(row.get("analyst", row.get("analista", row.get("ANALISTA", "")))),
            }
            val = record_data["value"]
            target = record_data["target_value"]
            if target > 0:
                record_data["cv"] = round((abs(val - target) / target) * 100, 2)
            else:
                record_data["cv"] = 0.0
            record_data["status"] = "OK"
            record_data["needs_calibration"] = False
            records_to_save.append(record_data)

        result = await QCService.create_qc_records_batch(records_to_save)
        count = len(records_to_save)

        if result:
            state.qc_success_message = f"{count} registros importados com sucesso!"
            await state.load_data_from_db(force=True)
        else:
            state.qc_error_message = "Erro ao salvar registros importados no banco."

        clear_proin_import(state)
    except Exception as e:
        state.qc_error_message = f"Erro na importação: {str(e)}"


def clear_proin_import(state):
    """Clear import state"""
    state.proin_import_preview = []
    state.proin_import_headers = []
    state.proin_import_data = []
    state.upload_progress = 0
