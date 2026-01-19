"""
Função para gerar PDF da análise COMPULAB x SIMUS
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
from decimal import Decimal
from io import BytesIO


def format_currency(value):
    """Formata valor como moeda brasileira"""
    if isinstance(value, (int, float)):
        return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    elif isinstance(value, Decimal):
        return f"R$ {float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return str(value)


def generate_analysis_pdf(
    compulab_total: float,
    simus_total: float,
    compulab_count: int,
    simus_count: int,
    missing_patients: list,
    missing_exams: list,
    value_divergences: list,
    missing_patients_total: float,
    missing_exams_total: float,
    divergences_total: float,
    explained_total: float,
    residual: float,
    ai_analysis: str = ""
) -> bytes:
    """
    Gera PDF da análise COMPULAB x SIMUS
    
    Returns:
        bytes: Conteúdo do PDF em bytes
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#1B5E20'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1B5E20'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    # Conteúdo
    story = []
    
    # Título
    story.append(Paragraph("Análise de Faturamento", title_style))
    story.append(Paragraph("COMPULAB x SIMUS", title_style))
    story.append(Spacer(1, 0.5*cm))
    
    # Data e hora
    date_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    story.append(Paragraph(f"<b>Data da Análise:</b> {date_str}", styles['Normal']))
    story.append(Spacer(1, 1*cm))
    
    # Resumo Geral
    story.append(Paragraph("Resumo Geral", heading_style))
    
    summary_data = [
        ['Métrica', 'Valor'],
        ['Total COMPULAB', format_currency(compulab_total)],
        ['Total SIMUS', format_currency(simus_total)],
        ['Diferença', format_currency(compulab_total - simus_total)],
        ['Pacientes COMPULAB', str(compulab_count)],
        ['Pacientes SIMUS', str(simus_count)],
    ]
    
    summary_table = Table(summary_data, colWidths=[8*cm, 8*cm])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4CAF50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    
    story.append(summary_table)
    story.append(Spacer(1, 1*cm))
    
    # Breakdown da Diferença
    story.append(Paragraph("Breakdown da Diferença", heading_style))
    
    breakdown_data = [
        ['Componente', 'Valor (R$)'],
        ['Pacientes Faltantes', format_currency(missing_patients_total)],
        ['Exames Faltantes', format_currency(missing_exams_total)],
        ['Divergências de Valor', format_currency(divergences_total)],
        ['Total Explicado', format_currency(explained_total)],
        ['Residual', format_currency(residual)],
    ]
    
    breakdown_table = Table(breakdown_data, colWidths=[8*cm, 8*cm])
    breakdown_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF9800')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    story.append(breakdown_table)
    story.append(PageBreak())
    
    # Pacientes Faltantes
    if missing_patients:
        story.append(Paragraph(f"Pacientes Faltantes no SIMUS ({len(missing_patients)} registros)", heading_style))
        
        # Criar tabela com TODOS os pacientes - sem limite
        patients_data = [['Paciente', 'Qtd. Exames', 'Valor Total (R$)']]
        
        # Processar TODOS os pacientes faltantes
        for idx, item in enumerate(missing_patients):
            patient_name = str(item.get('patient', ''))
            patients_data.append([
                patient_name,
                str(item.get('exams_count', 0)),
                format_currency(item.get('total_value', 0))
            ])
        
        # Criar tabela com todos os dados
        patients_table = Table(patients_data, colWidths=[8*cm, 4*cm, 4*cm], repeatRows=1)
        patients_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF9800')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
            ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(patients_table)
        story.append(PageBreak())
    
    # Exames Faltantes
    if missing_exams:
        story.append(Paragraph(f"Exames Faltantes no SIMUS ({len(missing_exams)} registros)", heading_style))
        
        # Criar tabela com TODOS os registros - sem limite
        exam_data = [['Paciente', 'Exame', 'Valor (R$)']]
        
        # Processar TODOS os exames faltantes
        total_exams = len(missing_exams)
        for idx, item in enumerate(missing_exams):
            patient_name = str(item.get('patient', ''))
            exam_name = str(item.get('exam_name', ''))
            exam_data.append([
                patient_name,
                exam_name,
                format_currency(item.get('value', 0))
            ])
        
        # Criar tabela com todos os dados
        exam_table = Table(exam_data, colWidths=[6*cm, 7*cm, 3*cm], repeatRows=1)
        exam_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F44336')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(exam_table)
        story.append(PageBreak())
    
    # Divergências de Valor
    if value_divergences:
        story.append(Paragraph(f"Divergências de Valor ({len(value_divergences)} registros)", heading_style))
        
        # Criar tabela com TODAS as divergências - sem limite
        div_data = [['Paciente', 'Exame', 'COMPULAB', 'SIMUS', 'Diferença']]
        
        # Processar TODAS as divergências
        for idx, item in enumerate(value_divergences):
            patient_name = str(item.get('patient', ''))
            exam_name = str(item.get('exam_name', ''))
            div_data.append([
                patient_name,
                exam_name,
                format_currency(item.get('compulab_value', 0)),
                format_currency(item.get('simus_value', 0)),
                format_currency(item.get('difference', 0))
            ])
        
        # Criar tabela com todos os dados
        div_table = Table(div_data, colWidths=[4*cm, 5*cm, 2.5*cm, 2.5*cm, 2.5*cm], repeatRows=1)
        div_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2196F3')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(div_table)
        story.append(PageBreak())
    
    # Análise por IA
    if ai_analysis:
        story.append(Paragraph("Análise por Inteligência Artificial", heading_style))
        
        # Tentar extrair CSV da resposta MD
        try:
            import re
            import csv
            from io import StringIO
            
            # Encontrar bloco de codigo csv
            # Procura por ```csv ... ``` ou apenas o conteúdo se não tiver blocos
            csv_pattern = r"```csv\s*(.*?)\s*```"
            match = re.search(csv_pattern, ai_analysis, re.DOTALL)
            
            csv_content = ""
            text_before = ai_analysis
            
            if match:
                csv_content = match.group(1)
                # Texto antes do CSV (intro)
                text_before = ai_analysis.split("```csv")[0].strip()
            
            # Se tem texto introdutório, adicionar
            if text_before:
                # Limpar markdown básico
                clean_text = text_before.replace('#', '').replace('*', '')
                story.append(Paragraph(clean_text, styles['Normal']))
                story.append(Spacer(1, 0.5*cm))
                
            if csv_content:
                # Parsear CSV
                f = StringIO(csv_content)
                reader = csv.reader(f, delimiter=';')
                csv_data = list(reader)
                
                if csv_data:
                    # Formatar cabeçalho
                    header = csv_data[0]
                    # Ajustar larguras baseado no conteúdo (estimativa)
                    # Paciente;Nome_Exame;Codigo_Exame;Valor_Compulab;Valor_Simus;Tipo_Divergencia
                    col_widths = [5*cm, 5*cm, 2*cm, 2.5*cm, 2.5*cm, 3*cm]
                    
                    ai_table = Table(csv_data, colWidths=col_widths, repeatRows=1)
                    ai_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#673AB7')), # Deep Purple
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 9),
                        ('FONTSIZE', (0, 1), (-1, -1), 8),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('TOPPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lavender]),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ]))
                    
                    story.append(ai_table)
                    story.append(Spacer(1, 1*cm))
                    
                    # Adicionar contagem
                    story.append(Paragraph(f"Total de itens na auditoria: {len(csv_data)-1}", styles['Normal']))
            else:
                 # Fallback se não achar CSV mas tiver conteúdo
                 clean_text = str(ai_analysis).replace('#', '').replace('*', '').replace('\n', '<br/>')
                 story.append(Paragraph(clean_text, styles['Normal']))

        except Exception as e:
            # Fallback em caso de erro no parse
            story.append(Paragraph(f"Erro ao formatar tabela IA: {str(e)}", styles['Normal']))
            clean_text = str(ai_analysis).replace('\n', '<br/>')
            story.append(Paragraph(clean_text, styles['Normal']))
            
        story.append(Spacer(1, 1*cm))
    
    # Rodapé
    story.append(Spacer(1, 2*cm))
    story.append(Paragraph(
        f"<i>Relatório gerado em {date_str} - Laboratório Biodiagnóstico</i>",
        styles['Normal']
    ))
    
    # Construir PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

