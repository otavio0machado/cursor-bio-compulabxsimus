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
from ..styles import Color


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
        textColor=colors.HexColor(Color.DEEP),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor(Color.DEEP),
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
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(Color.PRIMARY)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor(Color.BACKGROUND)]),
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
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(Color.WARNING)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor(Color.BACKGROUND)),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    story.append(breakdown_table)
    story.append(PageBreak())
    
    # Pacientes Faltantes
    if missing_patients:
        story.append(Paragraph(f"Pacientes Faltantes no SIMUS ({len(missing_patients)} registros)", heading_style))
        
        # Criar tabela com Todos os pacientes - sem limite
        patients_data = [['Paciente', 'Qtd. Exames', 'Valor Total (R$)']]
        
        # Processar Todos os pacientes faltantes
        for idx, item in enumerate(missing_patients):
            # Handle both dicts and objects (PatientModel)
            if isinstance(item, dict):
                patient_name = str(item.get('patient', item.get('name', '')))
                exams_count = str(item.get('exams_count', item.get('total_exams', 0)))
                total_val = item.get('total_value', 0)
            else:
                patient_name = getattr(item, 'patient', getattr(item, 'name', ''))
                exams_count = str(getattr(item, 'exams_count', getattr(item, 'total_exams', 0)))
                total_val = getattr(item, 'total_value', 0)

            patients_data.append([
                patient_name,
                exams_count,
                format_currency(total_val)
            ])
        
        # Criar tabela com todos os dados
        patients_table = Table(patients_data, colWidths=[8*cm, 4*cm, 4*cm], repeatRows=1)
        patients_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(Color.WARNING)),
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
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor(Color.BACKGROUND)]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(patients_table)
        story.append(PageBreak())
    
    # Exames Faltantes
    if missing_exams:
        story.append(Paragraph(f"Exames Faltantes no SIMUS ({len(missing_exams)} registros)", heading_style))
        
        # Criar tabela com Todos os registros - sem limite
        exam_data = [['Paciente', 'Exame', 'Valor (R$)']]
        
        # Processar Todos os exames faltantes
        total_exams = len(missing_exams)
        for idx, item in enumerate(missing_exams):
            # Handle both dicts and objects (AnalysisResult)
            if isinstance(item, dict):
                patient_name = str(item.get('patient', ''))
                exam_name = str(item.get('exam_name', ''))
                val = item.get('value', 0)
            else:
                patient_name = getattr(item, 'patient', '')
                exam_name = getattr(item, 'exam_name', '')
                val = getattr(item, 'value', 0)

            exam_data.append([
                patient_name,
                exam_name,
                format_currency(val)
            ])
        
        # Criar tabela com todos os dados
        exam_table = Table(exam_data, colWidths=[6*cm, 7*cm, 3*cm], repeatRows=1)
        exam_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(Color.ERROR)),
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
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor(Color.BACKGROUND)]),
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
            # Handle both dicts and objects (AnalysisResult)
            if isinstance(item, dict):
                patient_name = str(item.get('patient', ''))
                exam_name = str(item.get('exam_name', ''))
                val_c = item.get('compulab_value', 0)
                val_s = item.get('simus_value', 0)
                diff = item.get('difference', 0)
            else:
                patient_name = getattr(item, 'patient', '')
                exam_name = getattr(item, 'exam_name', '')
                val_c = getattr(item, 'compulab_value', 0)
                val_s = getattr(item, 'simus_value', 0)
                diff = getattr(item, 'difference', 0)

            div_data.append([
                patient_name,
                exam_name,
                format_currency(val_c),
                format_currency(val_s),
                format_currency(diff)
            ])
        
        # Criar tabela com todos os dados
        div_table = Table(div_data, colWidths=[4*cm, 5*cm, 2.5*cm, 2.5*cm, 2.5*cm], repeatRows=1)
        div_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(Color.PRIMARY)),
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
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor(Color.BACKGROUND)]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(div_table)
        story.append(PageBreak())
    
    # Análise por IA
    if ai_analysis:
        story.append(Paragraph("Análise por Inteligência Artificial", heading_style))
            
        # Tentar extrair CSV da resposta (Plain CSV Format - sem code blocks)
        try:
            import csv
            from io import StringIO
            
            # Encontrar linhas com ; (formato CSV)
            lines = ai_analysis.split('\n')
            csv_lines = []
            text_intro = []
            in_csv_section = False
            
            for line in lines:
                stripped = line.strip()
                if ';' in stripped and not stripped.startswith('#') and not stripped.startswith('*'):
                    in_csv_section = True
                    csv_lines.append(stripped)
                elif not in_csv_section:
                    text_intro.append(stripped)
            
            # Se tem texto introdutório, adicionar
            intro_text = ' '.join(text_intro).replace('#', '').replace('*', '').strip()
            if intro_text and len(intro_text) > 10:
                story.append(Paragraph(intro_text[:500], styles['Normal']))  # Limitar tamanho
                story.append(Spacer(1, 0.5*cm))
                
            if csv_lines:
                # Detectar se tem header
                first_line = csv_lines[0]
                if 'Paciente' in first_line and 'Nome_Exame' in first_line:
                    csv_content = '\n'.join(csv_lines)
                else:
                    # Adicionar header manualmente - deve bater com o prompt do utils/ai_analysis.py
                    header = "Paciente;Nome_Exame;Codigo_Exame;Valor_Compulab;Valor_Simus;Tipo_Divergencia;Sugestao_Causa_Raiz"
                    csv_content = header + '\n' + '\n'.join(csv_lines)
                
                # Parsear CSV
                f = StringIO(csv_content)
                reader = csv.reader(f, delimiter=';')
                csv_data = list(reader)
                
                if csv_data:
                    # Formatar cabeçalho
                    header = csv_data[0]
                    # Ajustar larguras para acomodar a nova coluna (A4 largura total aprox 20cm util)
                    col_widths = [3.5*cm, 3.5*cm, 1.8*cm, 2.0*cm, 2.0*cm, 2.5*cm, 4.0*cm]
                    
                    ai_table = Table(csv_data, colWidths=col_widths, repeatRows=1)
                    ai_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(Color.SECONDARY)),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 9),
                        ('FONTSIZE', (0, 1), (-1, -1), 8),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('TOPPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor(Color.BACKGROUND)]),
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

