"""
Operações de relatórios/PDF extraídas do QCState.
Cada função recebe `state` (instância do QCState) como primeiro argumento.
"""
import asyncio
import base64
import calendar
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


async def generate_pdf_bytes(state):
    """Helper para gerar bytes do PDF"""
    from ..utils.qc_pdf_report import generate_qc_pdf

    now = datetime.now()
    start_date = None
    end_date = None
    period_desc = ""

    if state.qc_report_type == "Mês Atual":
        start_date = now.replace(day=1).date().isoformat()
        end_date = now.date().isoformat()
        period_desc = f"Mês Atual ({now.strftime('%B/%Y')})"

    elif state.qc_report_type == "Mês Específico":
        try:
            month = int(state.qc_report_month)
            year = int(state.qc_report_year)
            last_day = calendar.monthrange(year, month)[1]
            start_date = f"{year}-{month:02d}-01"
            end_date = f"{year}-{month:02d}-{last_day}"
            period_desc = f"{month:02d}/{year}"
        except (ValueError, TypeError):
            state.qc_error_message = "Mês/Ano inválidos"
            return None, None

    elif state.qc_report_type == "3 Meses":
        start_date = (now - timedelta(days=90)).date().isoformat()
        end_date = now.date().isoformat()
        period_desc = "Últimos 3 Meses"

    elif state.qc_report_type == "Ano Atual":
        start_date = now.replace(month=1, day=1).date().isoformat()
        end_date = now.replace(month=12, day=31).date().isoformat()
        period_desc = f"Ano {now.year}"

    elif state.qc_report_type == "Ano Específico":
        try:
            year = int(state.qc_report_year)
            start_date = f"{year}-01-01"
            end_date = f"{year}-12-31"
            period_desc = f"Ano {year}"
        except (ValueError, TypeError):
            state.qc_error_message = "Ano inválido"
            return None, None

    records = state.qc_records

    filtered_records = []
    if start_date and end_date:
        for r in records:
            if r.date >= start_date and r.date <= (end_date + "T23:59:59"):
                filtered_records.append(r)
    else:
        filtered_records = records

    filtered_records.sort(key=lambda x: x.date, reverse=True)

    if not filtered_records:
        state.qc_error_message = "Nenhum registro encontrado no período."

    loop = asyncio.get_event_loop()
    pdf_bytes = await loop.run_in_executor(
        None,
        lambda: generate_qc_pdf(filtered_records, period_desc, state.post_calibration_records)
    )

    filename = f"QC_Report_{period_desc.replace('/', '_').replace(' ', '_')}.pdf"
    return pdf_bytes, filename


def build_csv_content(state):
    """Gera conteúdo CSV dos registros de QC"""
    header = "Data,Exame,Nível,Lote,Valor,Alvo,DP,CV%,Status,Equipamento,Analista\n"
    rows = []
    for r in state.qc_records:
        row = f"{r.date},{r.exam_name},{r.level},{r.lot_number},{r.value},{r.target_value},{r.target_sd},{r.cv:.2f},{r.status},{r.equipment},{r.analyst}"
        rows.append(row)
    return header + "\n".join(rows)
