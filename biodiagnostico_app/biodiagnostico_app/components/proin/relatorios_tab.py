import reflex as rx
from ...state import State
from ...styles import Color, Design, Typography, Spacing
from ...components import ui
from .helpers import format_cv, qc_status_label, qc_status_kind


def relatorios_tab() -> rx.Component:
    """Aba de Relatórios - Gráfico Levey-Jennings (Purificada)"""
    return rx.vstack(
        rx.vstack(
            ui.heading("Relatórios & Auditoria", level=2),
            ui.text("Visualize gráficos ou exporte tabelas completas para auditoria", size="small", color=Color.TEXT_SECONDARY),
            spacing="1", align_items="start", margin_bottom=Spacing.LG, width="100%"
        ),

        # Section: Exportação PDF (Split View)
        ui.card(
            rx.vstack(
                rx.hstack(
                    rx.box(rx.icon(tag="file_text", size=20, color=Color.PRIMARY), bg=Color.PRIMARY_LIGHT, p="2", border_radius=Design.RADIUS_SM),
                    ui.heading("Exportar Tabela QC (PDF)", level=3),
                    rx.spacer(),
                    rx.cond(
                        State.qc_pdf_preview != "",
                        rx.badge("Preview Ativo", color_scheme="green", variant="soft")
                    ),
                    style={"gap": Spacing.SM}, align_items="center", margin_bottom=Spacing.MD, width="100%"
                ),

                rx.hstack(
                    # Controls Column
                    rx.vstack(
                        rx.grid(
                            rx.box(
                                ui.text("Período", size="label", margin_bottom=Spacing.XS),
                                ui.select(["Mês Atual", "Mês Específico", "3 Meses", "6 Meses", "Ano Atual", "Ano Específico"], value=State.qc_report_type, on_change=State.set_qc_report_type)
                            ),
                            rx.cond(
                                State.qc_report_type == "Mês Específico",
                                rx.box(
                                    ui.text("Mês", size="label", margin_bottom=Spacing.XS),
                                    ui.select(["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"], value=State.qc_report_month, on_change=State.set_qc_report_month, placeholder="Mês")
                                )
                            ),
                            rx.cond(
                                (State.qc_report_type == "Mês Específico") | (State.qc_report_type == "Ano Específico"),
                                rx.box(
                                    ui.text("Ano", size="label", margin_bottom=Spacing.XS),
                                    ui.input(value=State.qc_report_year, on_change=State.set_qc_report_year, placeholder="Ano (ex: 2024)")
                                )
                            ),
                            columns={"initial": "1", "sm": "2"}, style={"gap": Spacing.MD}, width="100%"
                        ),
                        rx.box(
                             rx.grid(
                                 ui.button("Baixar PDF", icon="download", on_click=State.generate_qc_report_pdf, is_loading=State.is_generating_qc_report, variant="primary", width="100%"),
                                 ui.button("Regenerar PDF", icon="refresh-cw", on_click=State.regenerate_qc_report_pdf, is_loading=State.is_generating_qc_report, variant="secondary", width="100%"),
                                 ui.button("Exportar CSV", icon="file-spreadsheet", on_click=State.export_qc_csv, variant="secondary", width="100%"),
                                 columns="3", spacing="3", width="100%",
                             ),
                             margin_top=Spacing.LG,
                        ),
                        rx.cond(
                            State.qc_error_message != "",
                            rx.callout(State.qc_error_message, icon="triangle_alert", color_scheme="red", width="100%", margin_top=Spacing.MD)
                        ),
                        width=rx.cond(State.qc_pdf_preview != "", "40%", "100%"), transition="width 0.3s ease"
                    ),

                    # Preview Column
                    rx.cond(
                        State.qc_pdf_preview != "",
                        rx.box(
                            rx.html(
                                f'<iframe src="data:application/pdf;base64,' + State.qc_pdf_preview + '" width="100%" height="400px" style="border: none; border-radius: 8px; background: white;"></iframe>'
                            ),
                            width="60%", height="400px", bg=Color.BACKGROUND, border_radius=Design.RADIUS_MD, border=f"1px solid {Color.BORDER}"
                        )
                    ),
                    width="100%", spacing="6", align_items="start"
                )
            ),
            border_left=f"4px solid {Color.PRIMARY}", margin_bottom=Spacing.LG,
        ),
        rx.divider(margin_bottom=Spacing.LG, opacity=0.3),

        rx.vstack(
            ui.heading("Análise Levey-Jennings", level=2),
            ui.text("Visualização gráfica de tendências", size="small", color=Color.TEXT_SECONDARY),
            spacing="1", align_items="start", margin_bottom=Spacing.LG, width="100%"
        ),

        # Controls
        ui.card(
            rx.vstack(
                rx.grid(
                    rx.box(ui.text("Exame", size="label", margin_bottom=Spacing.XS), ui.select(State.unique_exam_names, value=State.levey_jennings_exam, on_change=State.set_levey_jennings_exam, placeholder="Selecione o exame...")),
                    rx.box(ui.text("Nível", size="label", margin_bottom=Spacing.XS), ui.select(["Todos", "N1", "N2", "N3"], value=State.levey_jennings_level, on_change=State.set_levey_jennings_level, placeholder="Selecione...")),
                    rx.box(ui.text("Período (dias)", size="label", margin_bottom=Spacing.XS), ui.select(["7", "15", "30", "60", "90"], value=State.levey_jennings_period, on_change=State.set_levey_jennings_period)),
                    columns="3", spacing="4", width="100%"
                ),
                ui.button("Gerar Gráfico", icon="chart_line", on_click=State.update_levey_jennings_data, margin_top=Spacing.MD),
            ),
            width="100%"
        ),

        # Chart Area
        rx.cond(
            State.levey_jennings_data.length() > 0,
            rx.vstack(
                # Legend (Purified)
                rx.hstack(
                    rx.hstack(rx.box(width="12px", height="12px", border_radius=Design.RADIUS_FULL, bg=Color.SUCCESS), rx.text("±1 DP", style=Typography.CAPTION), style={"gap": Spacing.XS}),
                    rx.hstack(rx.box(width="12px", height="12px", border_radius=Design.RADIUS_FULL, bg=Color.WARNING), rx.text("±2 DP", style=Typography.CAPTION), style={"gap": Spacing.XS}),
                    rx.hstack(rx.box(width="12px", height="12px", border_radius=Design.RADIUS_FULL, bg=Color.ERROR), rx.text("±3 DP", style=Typography.CAPTION), style={"gap": Spacing.XS}),
                    style={"gap": Spacing.LG}, justify_content="center", width="100%", margin_bottom=Spacing.MD
                ),

                # Recharts Line Chart
                ui.card(
                    rx.recharts.line_chart(
                        rx.recharts.line(data_key="value", stroke=Color.PRIMARY, stroke_width=2, dot=True, name="Valor"),
                        rx.recharts.line(data_key="target", stroke=Color.SUCCESS, stroke_width=1, stroke_dash_array="5 5", dot=False, name="Alvo"),
                        rx.recharts.x_axis(data_key="date"),
                        rx.recharts.y_axis(domain=[State.lj_min_domain, State.lj_max_domain]),
                        # Westgard Zones (Background)
                        rx.recharts.reference_area(y1=State.lj_target_minus_1sd.to_string(), y2=State.lj_target_plus_1sd.to_string(), fill=Color.SUCCESS, fill_opacity=0.1),
                        rx.recharts.reference_area(y1=State.lj_target_plus_1sd.to_string(), y2=State.lj_target_plus_2sd.to_string(), fill=Color.WARNING, fill_opacity=0.15),
                        rx.recharts.reference_area(y1=State.lj_target_minus_2sd.to_string(), y2=State.lj_target_minus_1sd.to_string(), fill=Color.WARNING, fill_opacity=0.15),
                        rx.recharts.reference_area(y1=State.lj_target_plus_2sd.to_string(), y2=State.lj_max_domain.to_string(), fill=Color.ERROR, fill_opacity=0.1),
                        rx.recharts.reference_area(y1=State.lj_min_domain.to_string(), y2=State.lj_target_minus_2sd.to_string(), fill=Color.ERROR, fill_opacity=0.1),
                        rx.recharts.cartesian_grid(stroke_dasharray="3 3", opacity=0.4),
                        rx.recharts.graphing_tooltip(),
                        rx.recharts.legend(),
                        rx.recharts.reference_line(y=State.lj_target_plus_1sd.to_string(), stroke=Color.SUCCESS, stroke_width=1, stroke_dasharray="3 3", label="+1s"),
                        rx.recharts.reference_line(y=State.lj_target_minus_1sd.to_string(), stroke=Color.SUCCESS, stroke_width=1, stroke_dasharray="3 3", label="-1s"),
                        rx.recharts.reference_line(y=State.lj_target_plus_2sd.to_string(), stroke=Color.WARNING, stroke_width=1, stroke_dasharray="3 3", label="+2s"),
                        rx.recharts.reference_line(y=State.lj_target_minus_2sd.to_string(), stroke=Color.WARNING, stroke_width=1, stroke_dasharray="3 3", label="-2s"),
                        rx.recharts.reference_line(y=State.lj_target_plus_3sd.to_string(), stroke=Color.ERROR, stroke_width=1, stroke_dasharray="3 3", label="+3s"),
                        rx.recharts.reference_line(y=State.lj_target_minus_3sd.to_string(), stroke=Color.ERROR, stroke_width=1, stroke_dasharray="3 3", label="-3s"),
                        data=State.levey_jennings_chart_data, width="100%", height=400,
                    ),
                    width="100%", padding=Spacing.MD
                ),

                # Statistics Summary
                rx.grid(
                    ui.stat_card("Média", State.lj_mean, "target", "primary"),
                    ui.stat_card("Desvio Padrão", State.lj_sd, "variable", "primary"),
                    ui.stat_card("CV% Médio", format_cv(State.lj_cv_mean) + "%", "percent", "primary"),
                    ui.stat_card("Pontos", State.levey_jennings_data.length(), "list", "primary"),
                    columns={"initial": "1", "sm": "2", "md": "2", "lg": "4"},
                    spacing="4", width="100%", margin_top=Spacing.LG
                ),

                # Data Table
                rx.box(
                    rx.vstack(
                        rx.hstack(ui.heading("Dados do Período", level=3), rx.spacer(), rx.badge(State.levey_jennings_data.length().to_string() + " registros", color_scheme="blue", variant="soft"), width="100%", align_items="center", margin_bottom=Spacing.MD),
                        rx.scroll_area(
                            rx.table.root(
                                rx.table.header(
                                    rx.table.row(
                                        rx.table.column_header_cell(rx.text("DATA", style=Typography.CAPTION)),
                                        rx.table.column_header_cell(rx.text("VALOR", style=Typography.CAPTION)),
                                        rx.table.column_header_cell(rx.text("ALVO", style=Typography.CAPTION)),
                                        rx.table.column_header_cell(rx.text("DP", style=Typography.CAPTION)),
                                        rx.table.column_header_cell(rx.text("CV%", style=Typography.CAPTION)),
                                        rx.table.column_header_cell(rx.text("STATUS", style=Typography.CAPTION)),
                                    )
                                ),
                                rx.table.body(
                                    rx.foreach(
                                        State.levey_jennings_data,
                                        lambda d: rx.table.row(
                                            rx.table.cell(rx.text(d.date, font_size=Typography.H5["font_size"])),
                                            rx.table.cell(rx.text(d.value.to_string(), font_weight="600")),
                                            rx.table.cell(d.target.to_string()),
                                            rx.table.cell(d.sd.to_string()),
                                            rx.table.cell(rx.text(format_cv(d.cv) + "%", font_weight="700", color=rx.cond(d.cv <= State.current_cv_max_threshold, Color.SUCCESS, rx.cond(d.cv <= State.current_cv_max_threshold * 1.5, Color.WARNING, Color.ERROR)))),
                                            rx.table.cell(ui.status_badge(rx.cond(d.cv <= State.current_cv_max_threshold, "OK", "ALERTA"), status=rx.cond(d.cv <= State.current_cv_max_threshold, "success", "error"))),
                                        )
                                    )
                                ), width="100%"
                            ),
                            style={"max_height": "300px"}
                        ),
                    ),
                    bg=Color.SURFACE, border=f"1px solid {Color.BORDER}", border_radius=Design.RADIUS_XL, padding=Spacing.LG, margin_top=Spacing.LG, width="100%", box_shadow=Design.SHADOW_SM
                ),
                width="100%"
            ),
            rx.center(
                rx.vstack(rx.icon(tag="chart_bar", size=48, color=Color.TEXT_SECONDARY, opacity=0.3), ui.text("Selecione um exame e gere o gráfico", color=Color.TEXT_SECONDARY), spacing="2", align_items="center"),
                bg=Color.BACKGROUND, border=f"2px dashed {Color.BORDER}", border_radius=Design.RADIUS_XL, padding=Spacing.XL, width="100%"
            )
        ),
        width="100%"
    )
