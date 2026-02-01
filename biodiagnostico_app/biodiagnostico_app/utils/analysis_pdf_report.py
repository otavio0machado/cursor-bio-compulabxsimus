"""
Gerador de Relatório PDF para Análise de Diferenças
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
    patients_only_compulab: list,
    patients_only_simus: list,
    exams_only_compulab: list,
    divergences: list,
    exams_only_simus: list,
    top_offenders: list,
    annotations: dict = None,
) -> bytes:
    """
    Gera PDF com o relatório completo da análise de auditoria.
    """
    annotations = annotations or {}
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
            Paragraph("Diferença Total", metric_label_style)
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
    
    # === SEÇÃO 1: DETALHAMENTO DE DIFERENÇAS ===
    story.append(Paragraph("Detalhamento de Diferenças Identificadas", h2_style))
    
    loss_data = [['Categoria', 'Qtd. Ocorrências', 'Impacto Financeiro']]
    
    # Helper para somar valores de AnalysisResult objects ou dicts
    def get_val(item, attr):
        return getattr(item, attr, 0) if not isinstance(item, dict) else item.get(attr, 0)

    def annotation_label(patient: str, exam: str = "") -> str:
        value = annotations.get(f"{patient}|{exam}", "") if annotations else ""
        if not value:
            return "-"
        return value.replace("_", " ")

    # Pacientes somente COMPULAB
    poc_total = sum(get_val(x, 'total_value') or get_val(x, 'value') for x in patients_only_compulab)
    loss_data.append(['Pacientes somente COMPULAB', str(len(patients_only_compulab)), f"R$ {poc_total:,.2f}"])

    # Pacientes somente SIMUS
    pos_total = sum(get_val(x, 'total_value') or get_val(x, 'value') for x in patients_only_simus)
    loss_data.append(['Pacientes somente SIMUS', str(len(patients_only_simus)), f"R$ {pos_total:,.2f}"])
    
    # Exames somente COMPULAB
    eoc_total = sum(get_val(x, 'compulab_value') or get_val(x, 'value') for x in exams_only_compulab)
    loss_data.append(['Exames somente COMPULAB', str(len(exams_only_compulab)), f"R$ {eoc_total:,.2f}"])
    
    # Divergences
    div_total = sum(abs(get_val(x, 'difference')) for x in divergences)
    loss_data.append(['Diferença de Valores', str(len(divergences)), f"R$ {div_total:,.2f}"])
    
    # Exames somente SIMUS
    eos_total = sum(get_val(x, 'simus_value') for x in exams_only_simus)
    loss_data.append(['Exames somente SIMUS', str(len(exams_only_simus)), f"R$ {eos_total:,.2f}"])
    
    # Total Leakage (COMPULAB)
    total_leakage = poc_total + eoc_total + div_total
    loss_data.append(['TOTAL DE PERDAS MENSURÁVEIS (COMPULAB)', '', f"R$ {total_leakage:,.2f}"])

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
    
    # Pacientes somente COMPULAB
    if patients_only_compulab:
        story.append(PageBreak())
        story.append(Paragraph("Detalhamento: Pacientes somente COMPULAB", h2_style))
        p_data = [['Paciente', 'Qtd Exames', 'Valor Total', 'Anotação']]
        for p in patients_only_compulab[:50]: # Limit
            patient_name = get_val(p, 'patient')
            p_data.append([
                patient_name,
                str(get_val(p, 'exams_count')),
                f"R$ {get_val(p, 'total_value'):,.2f}",
                annotation_label(patient_name),
            ])
        
        p_table = Table(p_data, colWidths=[7*cm, 3*cm, 4*cm, 4*cm])
        p_table.setStyle(TableStyle([
             ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
             ('GRID', (0,0), (-1,-1), 0.2, colors.grey),
             ('FONTSIZE', (0,0), (-1,-1), 8),
        ]))
        story.append(p_table)
        if len(patients_only_compulab) > 50:
             story.append(Paragraph(f"... e mais {len(patients_only_compulab)-50} pacientes.", styles['Italic']))

    # Pacientes somente SIMUS
    if patients_only_simus:
        story.append(PageBreak())
        story.append(Paragraph("Detalhamento: Pacientes somente SIMUS", h2_style))
        p_data = [['Paciente', 'Qtd Exames', 'Valor Total', 'Anotação']]
        for p in patients_only_simus[:50]:
            patient_name = get_val(p, 'patient')
            p_data.append([
                patient_name,
                str(get_val(p, 'exams_count')),
                f"R$ {get_val(p, 'total_value'):,.2f}",
                annotation_label(patient_name),
            ])
        
        p_table = Table(p_data, colWidths=[7*cm, 3*cm, 4*cm, 4*cm])
        p_table.setStyle(TableStyle([
             ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
             ('GRID', (0,0), (-1,-1), 0.2, colors.grey),
             ('FONTSIZE', (0,0), (-1,-1), 8),
        ]))
        story.append(p_table)
        if len(patients_only_simus) > 50:
             story.append(Paragraph(f"... e mais {len(patients_only_simus)-50} pacientes.", styles['Italic']))

    # Exames somente COMPULAB
    if exams_only_compulab:
        story.append(PageBreak())
        story.append(Paragraph("Detalhamento: Exames somente COMPULAB", h2_style))
        e_data = [['Paciente', 'Exame', 'Valor Compulab', 'Anotação']]
        for e in exams_only_compulab[:50]:
            patient_name = get_val(e, 'patient')
            exam_name = get_val(e, 'exam_name')
            e_data.append([
                patient_name[:20],
                exam_name[:35],
                f"R$ {get_val(e, 'compulab_value'):,.2f}",
                annotation_label(patient_name, exam_name),
            ])
            
        e_table = Table(e_data, colWidths=[5*cm, 7*cm, 3*cm, 3*cm])
        e_table.setStyle(TableStyle([
             ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
             ('GRID', (0,0), (-1,-1), 0.2, colors.grey),
             ('FONTSIZE', (0,0), (-1,-1), 8),
        ]))
        story.append(e_table)

    # Diferença de Valores
    if divergences:
        story.append(PageBreak())
        story.append(Paragraph("Detalhamento: Diferença de Valores", h2_style))
        d_data = [['Paciente', 'Exame', 'Compulab', 'Simus', 'Dif.', 'Anotação']]
        for d in divergences[:50]:
            patient_name = get_val(d, 'patient')
            exam_name = get_val(d, 'exam_name')
            d_data.append([
                patient_name[:15],
                exam_name[:22],
                f"{get_val(d, 'compulab_value'):,.2f}",
                f"{get_val(d, 'simus_value'):,.2f}",
                f"{get_val(d, 'difference'):,.2f}",
                annotation_label(patient_name, exam_name),
            ])
            
        d_table = Table(d_data, colWidths=[3.5*cm, 5.5*cm, 2.2*cm, 2.2*cm, 2.1*cm, 2.5*cm])
        d_table.setStyle(TableStyle([
             ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
             ('GRID', (0,0), (-1,-1), 0.2, colors.grey),
             ('FONTSIZE', (0,0), (-1,-1), 8),
             ('TEXTCOLOR', (4,1), (4,-1), colors.red),
        ]))
        story.append(d_table)

    # Exames somente SIMUS
    if exams_only_simus:
        story.append(PageBreak())
        story.append(Paragraph("Detalhamento: Exames somente SIMUS", h2_style))
        e_data = [['Paciente', 'Exame', 'Valor Simus', 'Anotação']]
        for e in exams_only_simus[:50]:
            patient_name = get_val(e, 'patient')
            exam_name = get_val(e, 'exam_name')
            e_data.append([
                patient_name[:20],
                exam_name[:35],
                f"R$ {get_val(e, 'simus_value'):,.2f}",
                annotation_label(patient_name, exam_name),
            ])
            
        e_table = Table(e_data, colWidths=[5*cm, 7*cm, 3*cm, 3*cm])
        e_table.setStyle(TableStyle([
             ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
             ('GRID', (0,0), (-1,-1), 0.2, colors.grey),
             ('FONTSIZE', (0,0), (-1,-1), 8),
        ]))
        story.append(e_table)

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
