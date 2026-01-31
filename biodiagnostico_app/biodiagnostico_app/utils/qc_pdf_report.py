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
from typing import Optional
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
