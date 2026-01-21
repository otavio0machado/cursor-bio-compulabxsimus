"""
Função para gerar PDF do histórico do paciente
Laboratório Biodiagnóstico
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from datetime import datetime
from io import BytesIO

def generate_patient_history_pdf(patient_name: str, history: list) -> bytes:
    """
    Gera um relatório PDF com o histórico de auditoria de um paciente específico.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4, 
        rightMargin=1.5*cm, 
        leftMargin=1.5*cm, 
        topMargin=1.5*cm, 
        bottomMargin=1.5*cm
    )
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'MainTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#1B5E20'),
        alignment=TA_CENTER,
        spaceAfter=10
    )
    
    header_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2E7D32'),
        spaceBefore=15,
        spaceAfter=10
    )
    
    normal_style = styles['Normal']
    
    story = []
    
    # Cabeçalho do Relatório
    story.append(Paragraph("Relatório de Histórico de Auditoria", title_style))
    story.append(Paragraph(f"<b>Paciente:</b> {patient_name}", styles['Normal']))
    story.append(Paragraph(f"<b>Data de Emissão:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
    story.append(Spacer(1, 0.5*cm))
    
    # Resumo Estatístico do Paciente
    resolved_count = len([e for e in history if e.status == "resolvido"])
    total_val = sum(e.last_value for e in history)
    
    story.append(Paragraph("Resumo do Histórico", header_style))
    
    summary_data = [
        ["Total de Registros", "Exames Resolvidos", "Valor Total Auditado"],
        [str(len(history)), str(resolved_count), f"R$ {total_val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")]
    ]
    
    summary_table = Table(summary_data, colWidths=[6*cm, 6*cm, 6*cm])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E8F5E9')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1B5E20')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica-Bold'),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 0.8*cm))
    
    # Tabela de Histórico Detalhado
    story.append(Paragraph("Detalhamento de Exames e Resoluções", header_style))
    
    data = [['Data/Hora', 'Exame', 'Status', 'Valor', 'Notas']]
    for e in history:
        # Formatar data simplificada
        date_str = e.created_at[:16].replace("T", " ")
        data.append([
            date_str,
            e.exam_name[:30] + ('...' if len(e.exam_name) > 30 else ''),
            e.status.capitalize(),
            f"R$ {e.last_value:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            Paragraph(e.notes or "", styles['Normal'])
        ])
    
    # Calcular larguras de colunas
    col_widths = [3.5*cm, 4.5*cm, 2.5*cm, 2.5*cm, 5*cm]
    
    hist_table = Table(data, colWidths=col_widths, repeatRows=1)
    hist_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1B5E20')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 0.2, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FAFB')]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    story.append(hist_table)
    
    # Rodapé
    story.append(Spacer(1, 2*cm))
    story.append(Paragraph(
        f"<i>Este documento é um registro interno do sistema de auditoria Biodiagnóstico. Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}.</i>",
        styles['Italic']
    ))
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
