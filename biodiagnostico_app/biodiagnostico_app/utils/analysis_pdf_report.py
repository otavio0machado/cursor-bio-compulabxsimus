"""
Gerador de Relatório PDF para Análise de Divergências
Laboratório Biodiagnóstico
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from datetime import datetime
from io import BytesIO
from ..styles import Color

def generate_analysis_pdf(
    compulab_total: float,
    simus_total: float,
    missing_patients: list,
    missing_exams: list,
    divergences: list,
    extra_simus: list,
    top_offenders: list
) -> bytes:
    """
    Gera PDF com o relatório completo da análise de auditoria.
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
    
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Heading1'],
        fontSize=22,
        textColor=colors.HexColor(Color.DEEP),
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    h2_style = ParagraphStyle(
        'ReportH2',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor(Color.PRIMARY),
        spaceBefore=15,
        spaceAfter=10,
        borderPadding=5,
        borderColor=colors.HexColor(Color.BORDER),
        borderWidth=0,
        borderBottomWidth=1
    )

    metric_label_style = ParagraphStyle(
        'MetricLabel',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.grey,
        alignment=TA_CENTER
    )

    metric_value_style = ParagraphStyle(
        'MetricValue',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor(Color.DEEP),
        alignment=TA_CENTER
    )
    
    story = []
    
    # === HEADER ===
    story.append(Paragraph("Relatório de Auditoria Financeira", title_style))
    story.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}", 
                          ParagraphStyle('Date', parent=styles['Normal'], alignment=TA_CENTER, textColor=colors.grey)))
    story.append(Spacer(1, 1*cm))
    
    # === RESUMO EXECUTIVO (Cards Layout in Table) ===
    diff = compulab_total - simus_total
    
    summary_data = [
        [
            Paragraph("Faturamento COMPULAB", metric_label_style),
            Paragraph("Faturamento SIMUS", metric_label_style),
            Paragraph("Divergência Total", metric_label_style)
        ],
        [
            Paragraph(f"R$ {compulab_total:,.2f}", metric_value_style),
            Paragraph(f"R$ {simus_total:,.2f}", metric_value_style),
            Paragraph(f"R$ {diff:,.2f}", ParagraphStyle('Diff', parent=metric_value_style, textColor=colors.red if diff != 0 else colors.green))
        ]
    ]
    
    summary_table = Table(summary_data, colWidths=[6*cm, 6*cm, 6*cm])
    summary_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor(Color.BORDER)),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor(Color.BORDER)),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor(Color.BACKGROUND)),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('TOPPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 1*cm))
    
    # === SEÇÃO 1: DETALHAMENTO DE PERDAS ===
    story.append(Paragraph("Detalhamento de Perdas Identificadas", h2_style))
    
    loss_data = [['Categoria', 'Qtd. Ocorrências', 'Impacto Financeiro']]
    
    # Helper para somar valores de AnalysisResult objects ou dicts
    def get_val(item, attr):
        return getattr(item, attr, 0) if not isinstance(item, dict) else item.get(attr, 0)

    # Missing Patients
    mp_total = sum(get_val(x, 'total_value') or get_val(x, 'value') for x in missing_patients)
    loss_data.append(['Pacientes Faltantes (Compulab > Simus)', str(len(missing_patients)), f"R$ {mp_total:,.2f}"])
    
    # Missing Exams
    me_total = sum(get_val(x, 'compulab_value') or get_val(x, 'value') for x in missing_exams)
    loss_data.append(['Exames Não Lançados', str(len(missing_exams)), f"R$ {me_total:,.2f}"])
    
    # Divergences
    div_total = sum(abs(get_val(x, 'difference')) for x in divergences)
    loss_data.append(['Divergência de Valores', str(len(divergences)), f"R$ {div_total:,.2f}"])
    
    # Extra Simus
    extra_total = sum(get_val(x, 'simus_value') for x in extra_simus)
    loss_data.append(['Extras no Simus (Não Faturados?)', str(len(extra_simus)), f"R$ {extra_total:,.2f}"])
    
    # Total Leakage
    total_leakage = mp_total + me_total + div_total
    loss_data.append(['TOTAL DE PERDAS MENSURÁVEIS', '', f"R$ {total_leakage:,.2f}"])

    loss_table = Table(loss_data, colWidths=[9*cm, 4*cm, 5*cm])
    loss_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor(Color.PRIMARY_LIGHT)),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor(Color.DEEP)),
        ('ALIGN', (0,0), (0,-1), 'LEFT'),
        ('ALIGN', (1,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'), # Total row bold
        ('LINEBELOW', (0,0), (-1,0), 1, colors.HexColor(Color.PRIMARY)),
        ('GRID', (0,0), (-1,-2), 0.5, colors.grey),
        ('BOX', (0,-1), (-1,-1), 1, colors.HexColor(Color.DEEP)), # Total box
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor(Color.BACKGROUND)),
    ]))
    story.append(loss_table)
    story.append(Spacer(1, 0.5*cm))
    
    # === SEÇÃO 2: TOP OFFENSORES ===
    if top_offenders:
        story.append(Paragraph("Top 5 Exames Problemáticos", h2_style))
        offender_data = [['Exame', 'Ocorrências']]
        for off in top_offenders:
            offender_data.append([off.name, str(off.count)])
            
        off_table = Table(offender_data, colWidths=[13*cm, 5*cm])
        off_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor(Color.SECONDARY)),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
            ('ALIGN', (1,0), (1,-1), 'CENTER'),
        ]))
        story.append(off_table)
        story.append(Spacer(1, 1*cm))

    # === SEÇÃO 3: LISTAS DETALHADAS (Limitado a 50 itens para não quebrar preview) ===
    
    # Pacientes Faltantes
    if missing_patients:
        story.append(PageBreak())
        story.append(Paragraph("Detalhamento: Pacientes Faltantes", h2_style))
        p_data = [['Paciente', 'Qtd Exames', 'Valor Total']]
        for p in missing_patients[:50]: # Limit
            p_data.append([
                get_val(p, 'patient'),
                str(get_val(p, 'exams_count')),
                f"R$ {get_val(p, 'total_value'):,.2f}"
            ])
        
        p_table = Table(p_data, colWidths=[10*cm, 3*cm, 5*cm])
        p_table.setStyle(TableStyle([
             ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
             ('GRID', (0,0), (-1,-1), 0.2, colors.grey),
             ('FONTSIZE', (0,0), (-1,-1), 9),
        ]))
        story.append(p_table)
        if len(missing_patients) > 50:
             story.append(Paragraph(f"... e mais {len(missing_patients)-50} pacientes.", styles['Italic']))

    # Exames Faltantes
    if missing_exams:
        story.append(PageBreak())
        story.append(Paragraph("Detalhamento: Exames Faltantes", h2_style))
        e_data = [['Paciente', 'Exame', 'Valor Compulab']]
        for e in missing_exams[:50]:
            e_data.append([
                get_val(e, 'patient')[:20], # Truncate patient name
                get_val(e, 'exam_name')[:35], # Truncate exam name
                f"R$ {get_val(e, 'compulab_value'):,.2f}"
            ])
            
        e_table = Table(e_data, colWidths=[6*cm, 8*cm, 4*cm])
        e_table.setStyle(TableStyle([
             ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
             ('GRID', (0,0), (-1,-1), 0.2, colors.grey),
             ('FONTSIZE', (0,0), (-1,-1), 8),
        ]))
        story.append(e_table)

    # Divergências
    if divergences:
        story.append(PageBreak())
        story.append(Paragraph("Detalhamento: Divergências de Valores", h2_style))
        d_data = [['Paciente', 'Exame', 'Compulab', 'Simus', 'Dif.']]
        for d in divergences[:50]:
            d_data.append([
                get_val(d, 'patient')[:15],
                get_val(d, 'exam_name')[:25],
                f"{get_val(d, 'compulab_value'):,.2f}",
                f"{get_val(d, 'simus_value'):,.2f}",
                f"{get_val(d, 'difference'):,.2f}"
            ])
            
        d_table = Table(d_data, colWidths=[4*cm, 6*cm, 2.5*cm, 2.5*cm, 2.5*cm])
        d_table.setStyle(TableStyle([
             ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
             ('GRID', (0,0), (-1,-1), 0.2, colors.grey),
             ('FONTSIZE', (0,0), (-1,-1), 8),
             ('TEXTCOLOR', (4,1), (4,-1), colors.red),
        ]))
        story.append(d_table)

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
