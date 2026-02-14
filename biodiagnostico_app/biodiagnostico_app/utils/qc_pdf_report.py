"""
Função para gerar PDF das tabelas de QC
"""
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from datetime import datetime
from io import BytesIO
from typing import Optional, List, Dict, Any
from ..styles import Color

def generate_qc_pdf(qc_records: list, period_description: str, post_calibration_records: Optional[list] = None) -> bytes:
    """
    Gera PDF com tabelas de Controle de Qualidade
    
    Args:
        qc_records: Lista de dicionários ou objetos QCRecord
        period_description: Descrição do período (ex: "Janeiro 2024")
        post_calibration_records: Lista de registros de pos-calibracao (opcional)
        
    Returns:
        bytes: Conteúdo do PDF em bytes
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=landscape(A4), 
        topMargin=1.5*cm, 
        bottomMargin=1.5*cm,
        leftMargin=1.5*cm,
        rightMargin=1.5*cm
    )
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor(Color.DEEP),
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.gray,
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # Conteúdo
    story = []

    def record_get(record, key, default=""):
        if isinstance(record, dict):
            return record.get(key, default)
        return getattr(record, key, default)

    post_by_id = {}
    post_by_qc_record_id = {}
    if post_calibration_records:
        for post_record in post_calibration_records:
            post_id = record_get(post_record, "id", "")
            qc_record_id = record_get(post_record, "qc_record_id", "")
            if post_id != "":
                post_by_id[post_id] = post_record
            if qc_record_id != "":
                post_by_qc_record_id[qc_record_id] = post_record
    
    # Cabeçalho
    story.append(Paragraph("Relatório de Controle de Qualidade (QC)", title_style))
    story.append(Paragraph(f"Período: {period_description}", subtitle_style))
    story.append(Spacer(1, 0.5*cm))
    
    if not qc_records:
        story.append(Paragraph("Nenhum registro encontrado para o período selecionado.", styles['Normal']))
    else:
        # Tabela
        # Headers: Data, Exame, Nível, Lote, Valor, Alvo, Variação %, Status, Passou CQ?, Nova Medição
        table_data = [['Data', 'Exame', 'Nível', 'Lote', 'Valor', 'Alvo', 'Variação %', 'Status', 'Passou CQ?', 'Nova Medição']]
        
        for record in qc_records:
            date = record_get(record, 'date', '')[:16].replace('T', ' ')
            exam = record_get(record, 'exam_name', '')
            level = record_get(record, 'level', '')
            lot = record_get(record, 'lot_number', '')
            value = str(record_get(record, 'value', ''))
            target = str(record_get(record, 'target_value', ''))
            cv = f"{record_get(record, 'cv', 0):.2f}%"
            status = record_get(record, 'status', '')
            needs_calibration = record_get(record, 'needs_calibration', None)
            if needs_calibration is None:
                needs_calibration = "ERRO" in str(status).upper()
            passed_cq = "NAO" if needs_calibration else "SIM"

            post_value = record_get(record, "post_calibration_value", None)
            if post_value in [None, ""]:
                post_id = record_get(record, "post_calibration_id", "")
                if post_id and post_id in post_by_id:
                    post_value = record_get(post_by_id[post_id], "post_calibration_value", None)

            if post_value in [None, ""]:
                qc_record_id = record_get(record, "id", "")
                if qc_record_id and qc_record_id in post_by_qc_record_id:
                    post_value = record_get(post_by_qc_record_id[qc_record_id], "post_calibration_value", None)

            if needs_calibration:
                if post_value in [None, ""]:
                    post_value_display = "PENDENTE"
                else:
                    post_value_display = str(post_value)
            else:
                post_value_display = "-"

            table_data.append([date, exam, level, lot, value, target, cv, status, passed_cq, post_value_display])

        # Largura das colunas (Total ~26.7cm em landscape A4 com margens)
        col_widths = [
            3.0*cm,  # Data
            5.0*cm,  # Exame
            1.8*cm,  # Nível
            2.5*cm,  # Lote
            2.3*cm,  # Valor
            2.3*cm,  # Alvo
            2.3*cm,  # Variação %
            2.8*cm,  # Status
            2.0*cm,  # Passou CQ?
            2.7*cm   # Nova Medição
        ]
        
        table = Table(table_data, colWidths=col_widths, repeatRows=1)
        
        # Estilo da Tabela
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(Color.SECONDARY)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (4, 1), (6, -1), 'RIGHT'), # Alinhar números à direita
            ('ALIGN', (9, 1), (9, -1), 'RIGHT'), # Nova medição a direita
            ('ALIGN', (8, 1), (8, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor(Color.BACKGROUND)]),
        ]))
        
        story.append(table)
        
        # Rodapé com total
        story.append(Spacer(1, 1*cm))
        story.append(Paragraph(f"Total de registros: {len(qc_records)}", styles['Normal']))
        story.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Italic']))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


_HEMATO_ANALITOS = [
    ("hemacias", "Hemácias"),
    ("hematocrito", "Hematócrito"),
    ("hemoglobina", "Hemoglobina"),
    ("leucocitos", "Leucócitos"),
    ("plaquetas", "Plaquetas"),
    ("rdw", "RDW"),
    ("vpm", "VPM"),
]


def _fmt(val: Any) -> str:
    """Formata valor numérico para exibição no PDF."""
    if val is None or val == "" or val == 0 or val == 0.0:
        return "—"
    try:
        f = float(val)
        return f"{f:g}"
    except (ValueError, TypeError):
        return str(val)


def _build_bio_rows(bio_records: List[Dict[str, Any]]) -> List[List[str]]:
    """Converte registros Bio x CI em linhas planas (1 linha por analito)."""
    rows: List[List[str]] = []
    for rec in bio_records:
        data_bio = rec.get("data_bio", "") or ""
        lote_bio = rec.get("registro_bio", "") or ""
        modo = rec.get("modo_ci", "bio") or "bio"

        for key, label in _HEMATO_ANALITOS:
            bio_val = rec.get(f"bio_{key}") or 0
            bio_str = _fmt(bio_val)

            if modo == "bio":
                ci_str = _fmt(rec.get(f"pad_{key}"))
                status = "—"
            elif modo == "intervalo":
                ci_min = float(rec.get(f"ci_min_{key}") or 0)
                ci_max = float(rec.get(f"ci_max_{key}") or 0)
                ci_str = f"{_fmt(ci_min)} — {_fmt(ci_max)}" if (ci_min or ci_max) else "—"
                try:
                    bv = float(bio_val)
                    status = "OK" if (ci_min <= bv <= ci_max and bv) else ("FORA" if bv else "—")
                except (ValueError, TypeError):
                    status = "—"
            else:  # porcentagem
                pad_val = float(rec.get(f"pad_{key}") or 0)
                ci_pct = float(rec.get(f"ci_pct_{key}") or 0)
                if pad_val and ci_pct:
                    r_min = pad_val * (1 - ci_pct / 100)
                    r_max = pad_val * (1 + ci_pct / 100)
                    ci_str = f"{_fmt(pad_val)} ±{_fmt(ci_pct)}%"
                    try:
                        bv = float(bio_val)
                        status = "OK" if (r_min <= bv <= r_max and bv) else ("FORA" if bv else "—")
                    except (ValueError, TypeError):
                        status = "—"
                else:
                    ci_str = _fmt(pad_val) if pad_val else "—"
                    status = "—"

            rows.append([data_bio, lote_bio, label, bio_str, ci_str, modo.capitalize(), status])
    return rows


def generate_area_pdf(
    area: str,
    area_label: str,
    records: List[Dict[str, Any]],
    bio_records: Optional[List[Dict[str, Any]]] = None,
) -> bytes:
    """
    Gera PDF de relatório para uma área laboratorial específica.

    Args:
        area: ID da área (hematologia, imunologia, etc.)
        area_label: Nome de exibição da área
        records: Lista de dicts com os registros da área
        bio_records: Lista de dicts com registros Bio x CI (hematologia)
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "AreaTitle",
        parent=styles["Heading1"],
        fontSize=18,
        textColor=colors.HexColor(Color.DEEP),
        spaceAfter=20,
        alignment=TA_CENTER,
    )
    subtitle_style = ParagraphStyle(
        "AreaSubtitle",
        parent=styles["Normal"],
        fontSize=12,
        textColor=colors.gray,
        spaceAfter=30,
        alignment=TA_CENTER,
    )
    section_style = ParagraphStyle(
        "SectionTitle",
        parent=styles["Heading2"],
        fontSize=13,
        textColor=colors.HexColor(Color.DEEP),
        spaceBefore=15,
        spaceAfter=10,
    )

    _table_style = TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(Color.SECONDARY)),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("FONTSIZE", (0, 1), (-1, -1), 9),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("TOPPADDING", (0, 0), (-1, 0), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor(Color.BACKGROUND)]),
        ]
    )

    story = []
    story.append(Paragraph(f"Relatório de Controle de Qualidade — {area_label}", title_style))
    story.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", subtitle_style))
    story.append(Spacer(1, 0.5 * cm))

    has_content = False

    # ── Seção Bio x CI (hematologia) ──
    if area == "hematologia" and bio_records:
        has_content = True
        story.append(Paragraph("Tabela Bio x Controle Interno", section_style))

        bio_headers = ["Data", "Lote", "Analito", "Bio", "Controle Interno", "Modo", "Status"]
        bio_col_widths = [3 * cm, 3.5 * cm, 3.5 * cm, 3 * cm, 5 * cm, 3 * cm, 3 * cm]

        bio_table_data = [bio_headers] + _build_bio_rows(bio_records)
        table = Table(bio_table_data, colWidths=bio_col_widths, repeatRows=1)
        table.setStyle(_table_style)
        story.append(table)
        story.append(Spacer(1, 0.3 * cm))
        story.append(Paragraph(f"Total: {len(bio_records)} registro(s) — {len(bio_table_data) - 1} linhas", styles["Normal"]))
        story.append(Spacer(1, 1 * cm))

    # ── Seção principal (medições CQ / imunologia / etc.) ──
    if records:
        has_content = True
        if area == "imunologia":
            headers = ["Data", "Controle", "Fabricante", "Lote", "Resultado"]
            keys = ["data", "controle", "fabricante", "lote", "resultado"]
            col_widths = [3.5 * cm, 6 * cm, 5 * cm, 4 * cm, 6 * cm]
        elif area == "hematologia":
            story.append(Paragraph("Medições CQ Intervalo / %", section_style))
            headers = ["Data", "Analito", "Valor", "Mín", "Máx", "Modo", "Status"]
            keys = ["data_medicao", "analito", "valor_medido", "min_aplicado", "max_aplicado", "modo_usado", "status"]
            col_widths = [3 * cm, 4 * cm, 3.5 * cm, 3.5 * cm, 3.5 * cm, 3.5 * cm, 3.5 * cm]
        else:
            headers = ["Info"]
            keys = ["info"]
            col_widths = [25 * cm]
            records = [{"info": f"Área {area_label} — registros em implementação."}]

        table_data = [headers]
        for rec in records:
            row = []
            for k in keys:
                val = rec.get(k, "")
                if val is None:
                    val = ""
                row.append(str(val))
            table_data.append(row)

        table = Table(table_data, colWidths=col_widths, repeatRows=1)
        table.setStyle(_table_style)
        story.append(table)
        story.append(Spacer(1, 0.3 * cm))
        story.append(Paragraph(f"Total de registros: {len(records)}", styles["Normal"]))

    if not has_content:
        story.append(Paragraph("Nenhum registro encontrado para esta área.", styles["Normal"]))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
