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

def generate_qc_pdf(qc_records: list, period_description: str) -> bytes:
    """
    Gera PDF com tabelas de Controle de Qualidade
    
    Args:
        qc_records: Lista de dicionários ou objetos QCRecord
        period_description: Descrição do período (ex: "Janeiro 2024")
        
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
        textColor=colors.HexColor('#1B5E20'),
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
    
    # Cabeçalho
    story.append(Paragraph("Relatório de Controle de Qualidade (QC)", title_style))
    story.append(Paragraph(f"Período: {period_description}", subtitle_style))
    story.append(Spacer(1, 0.5*cm))
    
    if not qc_records:
        story.append(Paragraph("Nenhum registro encontrado para o período selecionado.", styles['Normal']))
    else:
        # Tabela
        # Headers: Data, Exame, Nível, Lote, Valor, Alvo, DP, CV%, Status, Analista
        table_data = [['Data', 'Exame', 'Nível', 'Lote', 'Valor', 'Alvo', 'CV%', 'Status']]
        
        for record in qc_records:
            # Normalizar acesso aos dados (dict ou objeto)
            if isinstance(record, dict):
                date = record.get('date', '')[:16].replace('T', ' ')
                exam = record.get('exam_name', '')
                level = record.get('level', '')
                lot = record.get('lot_number', '')
                value = str(record.get('value', ''))
                target = str(record.get('target_value', ''))
                cv = f"{record.get('cv', 0):.2f}%"
                status = record.get('status', '')
            else:
                date = getattr(record, 'date', '')[:16].replace('T', ' ')
                exam = getattr(record, 'exam_name', '')
                level = getattr(record, 'level', '')
                lot = getattr(record, 'lot_number', '')
                value = str(getattr(record, 'value', ''))
                target = str(getattr(record, 'target_value', ''))
                cv = f"{getattr(record, 'cv', 0):.2f}%"
                status = getattr(record, 'status', '')
                
            table_data.append([date, exam, level, lot, value, target, cv, status])
            
        # Largura das colunas (Total ~27.7cm em landscape A4 com margens)
        col_widths = [3.5*cm, 6.0*cm, 2.0*cm, 3.0*cm, 2.5*cm, 2.5*cm, 2.5*cm, 3.0*cm]
        
        table = Table(table_data, colWidths=col_widths, repeatRows=1)
        
        # Estilo da Tabela
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E7D32')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (4, 1), (6, -1), 'RIGHT'), # Alinhar números à direita
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
        ]))
        
        story.append(table)
        
        # Rodapé com total
        story.append(Spacer(1, 1*cm))
        story.append(Paragraph(f"Total de registros: {len(qc_records)}", styles['Normal']))
        story.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Italic']))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
