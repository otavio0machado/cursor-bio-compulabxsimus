"""
Análise COMPULAB x SIMUS page
Design moderno com upload aprimorado
"""
import reflex as rx
from typing import Any
from ..state import State
from ..components.file_upload import compact_upload_card, upload_progress_indicator, large_file_progress_indicator
from ..components import ui
from ..styles import Color, Design, Typography, Spacing

# Card de métrica com design premium e animação (Purificado)
def metric_card(title: str, value: str, icon: str, subtitle: str = "", color_scheme: str = "green"):
    colors = {
        "green": (Color.SUCCESS, Color.SUCCESS_BG),
        "blue": (Color.PRIMARY, Color.PRIMARY_LIGHT),
        "orange": (Color.WARNING, Color.WARNING_BG),
        "red": (Color.ERROR, Color.ERROR_BG),
    }
    fg, bg = colors.get(color_scheme, colors["green"])
    
    return ui.card(
        rx.vstack(
            rx.hstack(
                rx.box(
                    rx.icon(tag=icon, size=24, color=fg),
                    padding="12px",
                    border_radius="16px",
                    background_color=bg,
                    display="flex", align_items="center", justify_content="center"
                ),
                rx.spacer(),
                ui.status_badge("ATIVO", status=color_scheme),
                width="100%",
                align_items="center",
            ),
            rx.vstack(
                rx.text(value, font_size=["1.5rem", "1.75rem", "2rem"], font_weight="800", color=Color.DEEP, line_height="1.1"),
                rx.text(title, style=Typography.SMALL, color=Color.TEXT_SECONDARY, text_transform="uppercase"),
                rx.cond(subtitle != "", rx.text(subtitle, font_size="10px", color=Color.TEXT_SECONDARY, font_weight="500")),
                align_items="start",
                style={"gap": "2px"},
            ),
            style={"gap": Spacing.MD},
        ),
    )

# Item de breakdown da diferença com design minimalista (Purificado)
def breakdown_item(icon: str, label: str, value: str, status: str = "default"):
    status_map = {
        "green": Color.SUCCESS,
        "blue": Color.PRIMARY,
        "orange": Color.WARNING,
        "red": Color.ERROR,
        "default": Color.TEXT_SECONDARY,
    }
    fg_color = status_map.get(status, Color.TEXT_SECONDARY)
    
    return rx.box(
        rx.hstack(
            rx.box(
                rx.icon(tag=icon, size=18, color=fg_color),
                bg=Color.BACKGROUND, padding="8px", border_radius="10px"
            ),
            rx.vstack(
                rx.text(label, style=Typography.CAPTION, font_weight="700", text_transform="uppercase", letter_spacing="0.1em"),
                rx.text(value, font_weight="700", color=fg_color, font_size="0.875rem"),
                align_items="start",
                style={"gap": "0px"}
            ),
            align_items="center",
            style={"gap": Spacing.MD},
        ),
        bg=Color.SURFACE,
        border=f"1px solid {Color.BORDER}",
        padding=Spacing.MD,
        border_radius=Design.RADIUS_LG,
        _hover={"bg": Color.PRIMARY_LIGHT, "border_color": Color.PRIMARY},
        transition="all 0.2s ease",
        flex="1",
    )


# Modal para exibir o histórico do paciente com design de Timeline (Purificado)
def patient_history_modal() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.hstack(
                    rx.box(rx.icon(tag="user", size=24, color=Color.PRIMARY), bg=Color.PRIMARY_LIGHT, p="2", border_radius="12px"),
                    rx.vstack(
                        rx.text(State.selected_patient_name, style=Typography.H4, color=Color.DEEP),
                        rx.hstack(
                            ui.status_badge("PACIENTE", status="success"),
                            rx.text("ID: " + State.selected_patient_id, style=Typography.CAPTION),
                            style={"gap": "8px"}, align_items="center",
                        ),
                        spacing="0", align_items="start"
                    ),
                    rx.spacer(),
                    rx.dialog.close(rx.button(rx.icon(tag="x", size=20), variant="ghost", color_scheme="gray", radius="full")),
                    width="100%", align_items="center", padding_bottom=Spacing.MD, border_bottom=f"1px solid {Color.BORDER}"
                )
            ),
            
            rx.box(
                rx.vstack(
                    # Stats Row
                    rx.grid(
                        rx.box(rx.vstack(rx.text("Total Auditoria", style=Typography.CAPTION, font_weight="700"), rx.text("R$ " + State.selected_patient_total_value, font_size="1.25rem", font_weight="800", color=Color.SUCCESS), spacing="0", align_items="start"), bg=Color.PRIMARY_LIGHT, padding=Spacing.MD, border_radius=Design.RADIUS_LG, border=f"1px solid {Color.SUCCESS}40"),
                        rx.box(rx.vstack(rx.text("Exames", style=Typography.CAPTION, font_weight="700"), rx.text(State.selected_patient_exams_count, font_size="1.25rem", font_weight="800", color=Color.PRIMARY), spacing="0", align_items="start"), bg=Color.BACKGROUND, padding=Spacing.MD, border_radius=Design.RADIUS_LG, border=f"1px solid {Color.BORDER}"),
                        rx.box(rx.vstack(rx.text("Status", style=Typography.CAPTION, font_weight="700"), ui.status_badge("Em Analise", status="warning"), spacing="0", align_items="start"), bg=Color.WARNING_BG, padding=Spacing.MD, border_radius=Design.RADIUS_LG, border=f"1px solid {Color.WARNING}40"),
                        columns="3", style={"gap": Spacing.MD}, width="100%", margin_bottom=Spacing.LG,
                    ),

                    rx.text("Timeline de Exames", style=Typography.LABEL, color=Color.DEEP, margin_bottom=Spacing.SM),
                    
                    rx.scroll_area(
                        rx.vstack(
                            rx.foreach(
                                State.patient_history_data,
                                lambda exam, i: rx.box(
                                    rx.hstack(
                                        rx.box(bg=rx.cond(exam.status == "Divergente", Color.ERROR, Color.SUCCESS), width="4px", height="auto", border_radius="full"),
                                        rx.vstack(
                                            rx.hstack(rx.text(exam.exam_name, style=Typography.BODY, font_weight="700", color=Color.DEEP), rx.spacer(), rx.text("R$ " + exam.last_value.to_string(), style=Typography.BODY, font_weight="800", color=Color.TEXT_PRIMARY), width="100%"),
                                            rx.hstack(
                                                rx.hstack(rx.icon(tag="calendar", size=12, color=Color.TEXT_SECONDARY), rx.text(exam.created_at, style=Typography.CAPTION), spacing="1", align_items="center"),
                                                rx.hstack(rx.icon(tag="hash", size=12, color=Color.TEXT_SECONDARY), rx.text(exam.id, style=Typography.CAPTION, color=Color.TEXT_LIGHT), spacing="1", align_items="center"),
                                                rx.badge(exam.status, color_scheme=rx.cond(exam.status == "Divergente", "red", "green"), size="1"),
                                                spacing="3", align_items="center"
                                            ),
                                            rx.cond(exam.notes != "", rx.box(rx.text("Nota: " + exam.notes, style=Typography.CAPTION, font_style="italic"), bg=Color.BACKGROUND, p="2", border_radius="8px", margin_top="4px", width="100%")),
                                            spacing="1", width="100%", align_items="start", padding_left=Spacing.SM
                                        ),
                                        width="100%", align_items="stretch", padding_y=Spacing.SM, padding_x=Spacing.XS, border_bottom=f"1px solid {Color.BORDER}", _hover={"bg": Color.BACKGROUND}
                                    ),
                                    width="100%"
                                )
                            ),
                            width="100%", spacing="0",
                        ),
                        style={"maxHeight": "400px"}, width="100%"
                    ),
                    width="100%",
                ),
                padding_y=Spacing.MD
            ),
            max_width="xl", border_radius=Design.RADIUS_XL, padding=Spacing.XL, bg=Color.SURFACE, border=f"1px solid {Color.BORDER}", box_shadow=Design.SHADOW_LG
        ),
        open=State.is_showing_patient_history,
        on_open_change=State.set_is_showing_patient_history,
    )

# Tabela com ações (Ver Histórico / Resolver) - Design Purificado
def action_table(headers: list[str], data: list, columns_keys: list[str], patient_key: str = "patient", is_divergence: bool = False) -> rx.Component:
    def render_row(item: Any, i: rx.Var[int]):
        # Células de dados
        cells = [
            rx.table.cell(
                rx.text(getattr(item, key), color=Color.TEXT_PRIMARY, font_size="0.875rem", font_weight="500"),
                padding_x=Spacing.MD, padding_y=Spacing.SM
            ) for key in columns_keys
        ]
        
        # Botões de ação
        actions = [
            ui.button(
                "",
                icon="history",
                on_click=lambda: State.view_patient_history(getattr(item, patient_key)),
                variant="ghost",
                padding="8px",
            )
        ]
        
        # Adicionar botão de resolução apenas se exam_name estiver presente
        if "exam_name" in columns_keys:
            # Construct resolution key safely using getattr
            res_key = getattr(item, patient_key) + "|" + getattr(item, "exam_name")
            is_resolved = State.resolutions[res_key] == "resolvido"
            
            actions.append(
                ui.button(
                    "",
                    icon=rx.cond(is_resolved, "circle_check", "circle"),
                    on_click=lambda: State.toggle_resolution(getattr(item, patient_key), getattr(item, "exam_name")),
                    variant="ghost",
                    color=rx.cond(is_resolved, Color.SUCCESS, Color.TEXT_SECONDARY),
                    padding="8px",
                )
            )
            
        # Adicionar coluna de ações
        cells.append(
            rx.table.cell(
                rx.hstack(
                    *actions,
                    style={"gap": Spacing.SM},
                    justify="end"
                ),
                padding_x=Spacing.MD, padding_y=Spacing.SM
            )
        )
        
        return rx.table.row(
            *cells,
            bg=rx.cond(i % 2 == 0, Color.SURFACE, Color.BACKGROUND)
        )

    return rx.box(
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    *[rx.table.column_header_cell(
                        rx.text(header, style=Typography.CAPTION, font_weight="700", text_transform="uppercase", letter_spacing="0.05em", color=Color.TEXT_SECONDARY),
                        bg=Color.BACKGROUND, padding_x=Spacing.MD, padding_y=Spacing.SM, border_bottom=f"1px solid {Color.BORDER}"
                    ) for header in headers],
                    rx.table.column_header_cell(
                        rx.text("AÇÕES", style=Typography.CAPTION, font_weight="700", text_transform="uppercase", letter_spacing="0.05em", color=Color.TEXT_SECONDARY),
                        bg=Color.BACKGROUND, padding_x=Spacing.MD, padding_y=Spacing.SM, border_bottom=f"1px solid {Color.BORDER}", text_align="right"
                    )
                )
            ),
            rx.table.body(
                rx.foreach(
                    data,
                    render_row
                )
            ),
            variant="surface",
            width="100%", border="none", border_radius=Design.RADIUS_LG, overflow="hidden"
        ),
        bg=Color.SURFACE, border=f"1px solid {Color.BORDER}", border_radius=Design.RADIUS_LG, box_shadow=Design.SHADOW_SM, overflow="hidden"
    )


def analise_page() -> rx.Component:
    """Página de análise comparativa - Design oficial aprimorado"""
    
    # SVG compacto do Erlenmeyer (Purificado)
    erlenmeyer_small = f"""
        <svg viewBox="0 0 50 60" width="36" height="44">
            <path d="M18 8 L32 8 L32 22 L42 50 Q43 54 39 56 L11 56 Q7 54 8 50 L18 22 Z" 
                  fill="none" stroke="{Color.DEEP}" stroke-width="2"/>
            <circle cx="25" cy="42" r="6" fill="{Color.SUCCESS}" opacity="0.3"/>
        </svg>
    """
    
    # SVG compacto dos Tubos (Purificado)
    tubes_small = f"""
        <svg viewBox="0 0 60 60" width="36" height="44">
            <rect x="12" y="10" width="10" height="40" rx="5" fill="none" stroke="{Color.DEEP}" stroke-width="2"/>
            <rect x="25" y="10" width="10" height="40" rx="5" fill="none" stroke="{Color.DEEP}" stroke-width="2"/>
            <rect x="38" y="10" width="10" height="40" rx="5" fill="none" stroke="{Color.DEEP}" stroke-width="2"/>
            <rect x="12" y="28" width="10" height="22" rx="5" fill="{Color.SUCCESS}" opacity="0.3"/>
            <rect x="25" y="24" width="10" height="26" rx="5" fill="{Color.SUCCESS}" opacity="0.3"/>
            <rect x="38" y="32" width="10" height="18" rx="5" fill="{Color.SUCCESS}" opacity="0.3"/>
        </svg>
    """
    
    return rx.box(
        rx.vstack(
            # Animated Header
            rx.box(
                ui.animated_heading("Análise COMPULAB × SIMUS", level=1),
                padding_y=Spacing.XL, width="100%", display="flex", justify_content="center"
            ),
            
            # Upload section
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.text("📁", font_size="1.25rem"),
                        rx.text("Upload de Arquivos", color=Color.PRIMARY, font_weight="700"),
                        spacing="2", align_items="center",
                    ),
                    rx.text("Aceita arquivos PDF, CSV ou Excel/XSL", style=Typography.CAPTION, color=Color.TEXT_SECONDARY, margin_bottom=Spacing.MD),
                    rx.grid(
                        compact_upload_card(title="COMPULAB", icon_svg=erlenmeyer_small, upload_id="compulab_analysis", file_name=State.compulab_file_name, file_size=State.compulab_file_size, on_upload=State.handle_compulab_upload, on_remove=State.clear_compulab_file, accepted_types="COMPLETO"),
                        compact_upload_card(title="SIMUS", icon_svg=tubes_small, upload_id="simus_analysis", file_name=State.simus_file_name, file_size=State.simus_file_size, on_upload=State.handle_simus_upload, on_remove=State.clear_simus_file, accepted_types="COMPLETO"),
                        columns={"initial": "1", "sm": "2"}, spacing="4", width="100%",
                    ),
                    upload_progress_indicator(State.is_uploading, "Carregando arquivo..."),
                    spacing="2", width="100%",
                ),
                bg=Color.SURFACE, border=f"1px solid {Color.BORDER}", border_radius=Design.RADIUS_XL, padding=Spacing.LG, margin_top=Spacing.LG, max_width="xl", width="100%", box_shadow=Design.SHADOW_SM
            ),
            
            # Botão de análise (Purificado)
            ui.button("Analisar Faturamento", icon="search", on_click=State.run_analysis, is_loading=State.is_analyzing, loading_text="Analisando dados...", disabled=~State.has_files, variant="primary", padding="1.5rem 3rem", margin_top=Spacing.LG),
            
            # Indicador de progresso
            rx.cond(
                State.is_analyzing,
                rx.box(
                    rx.vstack(
                        rx.text(State.analysis_progress_percentage.to_string() + "%", color=Color.PRIMARY, font_size="2rem", font_weight="800", text_align="center"),
                        rx.text(State.analysis_stage, style=Typography.SMALL, color=Color.TEXT_SECONDARY, text_align="center", margin_top="4px"),
                        rx.box(
                            rx.box(bg=Color.GRADIENT_PRIMARY, border_radius="full", transition="width 0.3s ease", width=rx.cond(State.analysis_progress_percentage > 0, State.analysis_progress_percentage.to_string() + "%", "0%"), height="100%"),
                            width="100%", height="12px", bg=Color.BACKGROUND, border_radius="full", overflow="hidden", margin_top=Spacing.MD
                        ),
                        spacing="0", align_items="center",
                    ),
                    bg=Color.SURFACE, border=f"1px solid {Color.BORDER}", border_radius=Design.RADIUS_LG, padding=Spacing.LG, margin_top=Spacing.MD, max_width="4xl", width="100%", box_shadow=Design.SHADOW_SM
                ),
            ),
            
            # Mensagens
            rx.cond(
                State.success_message != "",
                rx.callout(State.success_message, icon="circle_check", color_scheme="green", width="100%", max_width="xl", margin_top=Spacing.MD),
            ),
            rx.cond(
                State.error_message != "",
                rx.callout(State.error_message, icon="triangle_alert", color_scheme="red", width="100%", max_width="xl", margin_top=Spacing.MD),
            ),
            
            # Resultados
            rx.cond(
                State.has_analysis,
                rx.vstack(
                    # Métricas principais
                    rx.box(
                        rx.vstack(
                             rx.hstack(
                                rx.box(rx.icon(tag="bar-chart-3", size=24, color=Color.PRIMARY), bg=Color.PRIMARY_LIGHT, p="2", border_radius="12px"),
                                rx.vstack(
                                    rx.text("Resumo Executivo da Análise", style=Typography.H4, color=Color.DEEP),
                                    rx.text("Consolidação financeira dos sistemas integrados", style=Typography.SMALL, color=Color.TEXT_SECONDARY),
                                    spacing="0", align_items="start",
                                ),
                                rx.spacer(),
                                ui.status_badge("CONCLUÍDO", status="success"),
                                style={"gap": Spacing.MD}, width="100%", margin_bottom=Spacing.LG
                            ),
                            
                            rx.grid(
                                metric_card("COMPULAB Total", State.formatted_compulab_total, "landmark", State.compulab_count.to_string() + " pacientes", "green"),
                                metric_card("SIMUS Total", State.formatted_simus_total, "database", State.simus_count.to_string() + " pacientes", "blue"),
                                metric_card("Diferença Bruta", State.formatted_difference, "git-compare", "COMPULAB - SIMUS", "orange"),
                                metric_card("Alertas de Exame", State.missing_exams_count.to_string(), "circle-alert", "itens faltantes", "red"),
                                columns={"initial": "1", "sm": "2", "lg": "4"},
                                style={"gap": Spacing.MD},
                                width="100%",
                            ),
                            
                            # Barra de Progresso da Auditoria
                            rx.box(
                                rx.vstack(
                                    rx.hstack(
                                        rx.vstack(
                                            rx.text("Status da Auditoria Local", style=Typography.LABEL, color=Color.DEEP),
                                            rx.text("Divergências tratadas nesta sessão", style=Typography.CAPTION, color=Color.TEXT_SECONDARY),
                                            spacing="0", align_items="start",
                                        ),
                                        rx.spacer(),
                                        rx.box(
                                            rx.text(State.resolution_progress.to_string() + "%", style=Typography.H4, color=Color.SUCCESS),
                                            bg=Color.SUCCESS_LIGHT, px="3", py="1", border_radius="8px", border=f"1px solid {Color.SUCCESS}40"
                                        ),
                                        width="100%", align_items="center",
                                    ),
                                    rx.box(
                                        rx.box(
                                            bg=Color.GRADIENT_PRIMARY, border_radius="full", transition="all 1s ease-in-out",
                                            width=State.resolution_progress.to_string() + "%", height="100%"
                                        ),
                                        width="100%", height="12px", bg=Color.BACKGROUND, border_radius="full", overflow="hidden", border=f"1px solid {Color.BORDER}"
                                    ),
                                    style={"gap": Spacing.MD}, width="100%",
                                ),
                                margin_top=Spacing.XL, padding=Spacing.LG, bg=Color.SURFACE, border=f"1px solid {Color.BORDER}", border_radius=Design.RADIUS_XL, width="100%"
                            ),
                            width="100%",
                        ),
                        bg=Color.SURFACE, border=f"1px solid {Color.BORDER}", border_radius=Design.RADIUS_XL, padding=Spacing.XL, margin_top=Spacing.XL, width="100%", box_shadow=Design.SHADOW_SM
                    ),
                    
                    # === DASHBOARD ANALÍTICO REFINADO ===
                    rx.box(
                        rx.vstack(
                            # Header com Total de Perda
                     rx.hstack(
                                rx.vstack(
                                    rx.hstack(
                                        rx.icon(tag="layout-dashboard", size=22, color=Color.PRIMARY),
                                        rx.text("Dashboard de Inteligência", style=Typography.H4, color=Color.DEEP),
                                        align_items="center",
                                        style={"gap": "8px"},
                                    ),
                                    rx.text("Visualização analítica das divergências identificadas", style=Typography.SMALL, color=Color.TEXT_SECONDARY),
                                    spacing="0", align_items="start",
                                ),
                                rx.spacer(),
                                # Card de Perda Total
                                rx.box(
                                    rx.vstack(
                                        rx.text("PERDA TOTAL IDENTIFICADA", style=Typography.CAPTION, font_weight="700", color=Color.ERROR),
                                        rx.text(State.formatted_total_leakage, font_size="1.5rem", font_weight="800", color=Color.ERROR),
                                        spacing="0", align_items="end",
                                    ),
                                    bg=Color.ERROR_BG, border=f"1px solid {Color.ERROR}40", px="4", py="2", border_radius="16px"
                                ),
                                width="100%", align_items="center", margin_bottom=Spacing.LG
                            ),
                            
                            # Grid com Gráficos Refinados
                            rx.grid(
                                # Pie Chart - Composição da Perda
                                rx.box(
                                    rx.vstack(
                                        rx.hstack(
                                            rx.icon(tag="pie-chart", size=16, color=Color.TEXT_SECONDARY),
                                            rx.text("Composição da Perda", style=Typography.LABEL, color=Color.DEEP),
                                            style={"gap": Spacing.SM}, align_items="center",
                                        ),
                                        rx.recharts.pie_chart(
                                            rx.recharts.pie(
                                                data=State.revenue_distribution_data,
                                                data_key="value",
                                                name_key="name",
                                                cx="50%",
                                                cy="50%",
                                                inner_radius=45,
                                                outer_radius=75,
                                                padding_angle=3,
                                                stroke="white",
                                                label=True,
                                            ),
                                            rx.recharts.graphing_tooltip(),
                                            rx.recharts.legend(
                                                icon_type="circle",
                                                icon_size=8,
                                                vertical_align="bottom",
                                            ),
                                            width="100%",
                                            height=250,
                                        ),
                                        width="100%", style={"gap": Spacing.MD},
                                    ),
                                    bg=Color.SURFACE, border=f"1px solid {Color.BORDER}", border_radius=Design.RADIUS_XL, padding=Spacing.MD, box_shadow=Design.SHADOW_SM,
                                    _hover={"box_shadow": Design.SHADOW_MD}, transition="all 0.2s ease"
                                ),
                                
                                # Bar Chart - Top Exames
                                rx.box(
                                    rx.vstack(
                                        rx.hstack(
                                            rx.icon(tag="bar-chart-2", size=16, color=Color.PRIMARY),
                                            rx.text("Top Exames Problemáticos", style=Typography.LABEL, color=Color.DEEP),
                                            style={"gap": Spacing.SM}, align_items="center",
                                        ),
                                        rx.recharts.bar_chart(
                                            rx.recharts.bar(
                                                data_key="value",
                                                fill=Color.PRIMARY,
                                                radius=[6, 6, 0, 0],
                                            ),
                                            rx.recharts.x_axis(
                                                data_key="name", 
                                                tick_size=6,
                                                angle=-20,
                                                text_anchor="end",
                                            ),
                                            rx.recharts.y_axis(width=55),
                                            rx.recharts.graphing_tooltip(),
                                            rx.recharts.cartesian_grid(stroke_dasharray="3 3", opacity=0.3),
                                            data=State.top_exams_discrepancy_data,
                                            width="100%",
                                            height=250,
                                        ),
                                        width="100%", style={"gap": Spacing.MD},
                                    ),
                                    bg=Color.SURFACE, border=f"1px solid {Color.BORDER}", border_radius=Design.RADIUS_XL, padding=Spacing.MD, box_shadow=Design.SHADOW_SM,
                                    _hover={"box_shadow": Design.SHADOW_MD}, transition="all 0.2s ease"
                                ),
                                columns={"initial": "1", "lg": "2"},
                                spacing="4",
                                width="100%",
                            ),
                            
                            # === CENTRAL DE AÇÕES (SIMPLIFICADA) ===
                             rx.box(
                                rx.vstack(
                                    rx.hstack(
                                        rx.box(
                                            rx.icon(tag="lightbulb", size=18, color="white"),
                                            bg=Color.WARNING, p="2", border_radius="8px"
                                        ),
                                        rx.vstack(
                                            rx.text("Central de Ações Recomendadas", style=Typography.LABEL, color=Color.DEEP),
                                            rx.text("Sugestões ordenadas por impacto financeiro", style=Typography.CAPTION, color=Color.TEXT_SECONDARY),
                                            spacing="0", align_items="start",
                                        ),
                                        rx.spacer(),
                                        style={"gap": Spacing.MD},
                                        width="100%",
                                        align_items="center",
                                    ),
                                    rx.divider(margin_y=Spacing.MD, opacity=0.3),
                                    rx.foreach(
                                        State.action_center_insights,
                                        lambda insight: rx.box(
                                            rx.hstack(
                                                rx.box(
                                                    rx.icon(tag=insight["icon"], size=18, color=Color.WARNING),
                                                    bg=Color.WARNING_BG, p="2.5", border_radius="12px"
                                                ),
                                                rx.vstack(
                                                    rx.text(insight["title"], style=Typography.SMALL, font_weight="700", color=Color.DEEP),
                                                    rx.text(insight["description"], style=Typography.CAPTION, color=Color.TEXT_SECONDARY),
                                                    spacing="1", align_items="start", flex="1"
                                                ),
                                                style={"gap": Spacing.MD}, align_items="center", width="100%",
                                            ),
                                            bg=Color.SURFACE, border=f"1px solid {Color.BORDER}", padding=Spacing.MD, border_radius=Design.RADIUS_LG,
                                            _hover={"border_color": Color.WARNING, "bg": Color.WARNING_BG},
                                            margin_bottom=Spacing.SM, transition="all 0.2s ease"
                                        )
                                    ),
                                    width="100%",
                                ),
                                bg=Color.BACKGROUND, border=f"1px solid {Color.BORDER}", padding=Spacing.LG, border_radius=Design.RADIUS_XL, margin_top=Spacing.LG
                            ),

                            
                            # Breakdown numérico secundário
                             rx.box(
                                rx.hstack(
                                    rx.icon(tag="calculator", size=16, color=Color.TEXT_SECONDARY),
                                    rx.text("Resumo Numérico", style=Typography.SMALL, font_weight="700", color=Color.TEXT_SECONDARY),
                                    align_items="center",
                                    style={"gap": "8px"},
                                    margin_bottom=Spacing.MD
                                ),
                                rx.grid(
                                    breakdown_item("users", "Pacientes Faltantes", State.formatted_missing_patients_total, "orange"),
                                    breakdown_item("file_warning", "Exames Faltantes", State.formatted_missing_exams_total, "red"),
                                    breakdown_item("coins", "Divergências Valor", State.formatted_divergences_total, "blue"),
                                    breakdown_item("circle_plus", "Extras no SIMUS", State.extra_simus_exams_count.to_string() + " exames", "default"),
                                    columns={"initial": "2", "lg": "4"},
                                    style={"gap": Spacing.MD},
                                    width="100%",
                                ),
                                margin_top=Spacing.LG
                            ),
                            

                            width="100%",
                        ),
                        bg=Color.BACKGROUND, border=f"1px solid {Color.BORDER}", border_radius=Design.RADIUS_XL, padding=Spacing.XL, margin_top=Spacing.LG, box_shadow=Design.SHADOW_SM
                    ),


                    # Tabs de detalhes usando Segmented Control
                    ui.segmented_control(
                        [
                            {"label": f"Pct Faltantes ({State.missing_patients_count})", "value": "patients_missing"},
                            {"label": f"Exames Faltantes ({State.missing_exams_count})", "value": "missing"},
                            {"label": f"Divergências ({State.divergences_count})", "value": "divergences"},
                            {"label": f"Extras Simus ({State.extra_simus_exams_count})", "value": "extras"},
                            {"label": "Análise IA", "value": "ai"},
                        ],
                        State.analysis_active_tab,
                        State.set_analysis_active_tab
                    ),

                    rx.box(
                        rx.cond(
                            State.analysis_active_tab == "patients_missing",
                            rx.cond(
                                State.missing_patients_count > 0,
                                action_table(headers=["Paciente", "Exames", "Valor Total (R$)"], data=State.missing_patients, columns_keys=["patient", "exams_count", "total_value"], patient_key="patient"),
                                rx.box(rx.hstack(rx.icon(tag="circle_check", size=20, color=Color.SUCCESS), rx.text("Todos os pacientes do COMPULAB estão no SIMUS!", color=Color.SUCCESS, font_weight="500"), spacing="2", align_items="center"), bg=Color.SUCCESS_BG, border=f"1px solid {Color.SUCCESS}40", border_radius=Design.RADIUS_LG, padding=Spacing.LG, margin_top=Spacing.MD)
                            )
                        ),
                        rx.cond(
                            State.analysis_active_tab == "missing",
                            rx.cond(
                                State.missing_exams_count > 0,
                                action_table(headers=["Paciente", "Exame", "Valor (R$)"], data=State.missing_exams, columns_keys=["patient", "exam_name", "value"]),
                                rx.box(rx.hstack(rx.icon(tag="circle_check", size=20, color=Color.SUCCESS), rx.text("Todos os exames do COMPULAB estão no SIMUS!", color=Color.SUCCESS, font_weight="500"), spacing="2", align_items="center"), bg=Color.SUCCESS_BG, border=f"1px solid {Color.SUCCESS}40", border_radius=Design.RADIUS_LG, padding=Spacing.LG, margin_top=Spacing.MD)
                            )
                        ),
                        rx.cond(
                            State.analysis_active_tab == "divergences",
                            rx.cond(
                                State.divergences_count > 0,
                                action_table(headers=["Paciente", "Exame", "COMPULAB", "SIMUS", "Diferença"], data=State.value_divergences, columns_keys=["patient", "exam_name", "compulab_value", "simus_value", "difference"], is_divergence=True),
                                rx.box(rx.hstack(rx.icon(tag="circle_check", size=20, color=Color.SUCCESS), rx.text("Não há divergências de valor!", color=Color.SUCCESS, font_weight="500"), spacing="2", align_items="center"), bg=Color.SUCCESS_BG, border=f"1px solid {Color.SUCCESS}40", border_radius=Design.RADIUS_LG, padding=Spacing.LG, margin_top=Spacing.MD)
                            )
                        ),
                        rx.cond(
                            State.analysis_active_tab == "extras",
                            rx.cond(
                                State.extra_simus_exams_count > 0,
                                action_table(headers=["Paciente", "Exame", "Valor SIMUS"], data=State.extra_simus_exams, columns_keys=["patient", "exam_name", "simus_value"]),
                                rx.box(rx.hstack(rx.icon(tag="check_check", size=20, color=Color.SUCCESS), rx.text("Nenhum exame extra ('fantasma') encontrado no SIMUS.", color=Color.SUCCESS, font_weight="500"), spacing="2", align_items="center"), bg=Color.SUCCESS_BG, border=f"1px solid {Color.SUCCESS}40", border_radius=Design.RADIUS_LG, padding=Spacing.LG, margin_top=Spacing.MD)
                            )
                        ),
                        rx.cond(
                            State.analysis_active_tab == "ai",
                            rx.box(
                                rx.vstack(
                                    # Header Premium
                                    rx.box(
                                        rx.hstack(
                                            rx.box(rx.icon(tag="bot", size=24, color="white"), bg="rgba(255,255,255,0.1)", p="2", border_radius="12px"),
                                            rx.vstack(
                                                rx.text("Auditoria Inteligente (Beta)", style=Typography.H4, color="white"),
                                                rx.text("Análise profunda de padrões via GPT-4 Turbo", style=Typography.CAPTION, color="white", opacity=0.8, letter_spacing="0.1em", text_transform="uppercase"),
                                                spacing="0", align_items="start"
                                            ),
                                            rx.spacer(),
                                            rx.badge("IA ATIVA", variant="soft", color_scheme="green", size="1"),
                                            style={"gap": Spacing.MD}, align_items="center"
                                        ),
                                        bg=Color.GRADIENT_PRIMARY, padding=Spacing.LG, border_radius=Design.RADIUS_LG, margin_bottom=Spacing.LG, box_shadow=Design.SHADOW_MD
                                    ),
                                    
                                    rx.cond(
                                        State.is_generating_ai,
                                        rx.box(
                                            rx.vstack(
                                                rx.hstack(
                                                    rx.spinner(size="1", color=Color.SUCCESS),
                                                    rx.text(State.ai_loading_text, style=Typography.BODY, color=Color.TEXT_PRIMARY),
                                                    spacing="2",
                                                ),
                                                rx.progress(value=State.ai_loading_progress, max=100, color_scheme="green", width="100%", height="8px", border_radius="full"),
                                                spacing="2", width="100%"
                                            ),
                                            bg=Color.SUCCESS_BG, padding=Spacing.MD, border_radius=Design.RADIUS_LG, margin_bottom=Spacing.MD, border=f"1px solid {Color.SUCCESS}40"
                                        ),
                                    ),

                                    # Seletor de Modelo e Provedor
                                    rx.box(
                                        rx.vstack(
                                            rx.text("Modelo de IA", style=Typography.CAPTION, font_weight="700", color=Color.TEXT_SECONDARY, text_transform="uppercase", margin_bottom=Spacing.SM),
                                            
                                            # Seletor de Provedor (Macro)
                                            ui.segmented_control(
                                                [
                                                    {"label": "OpenAI", "value": "OpenAI"},
                                                    {"label": "Google Gemini", "value": "Gemini"},
                                                ],
                                                State.ai_provider,
                                                State.set_ai_provider
                                            ),

                                            # Seletor de Modelo (Específico)
                                            rx.cond(
                                                State.ai_provider == "OpenAI",
                                                rx.select(
                                                    ["gpt-4o", "gpt-4-turbo"],
                                                    value=State.ai_model,
                                                    on_change=State.set_ai_model,
                                                    width="100%", margin_top=Spacing.SM
                                                ),
                                                rx.select(
                                                    ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro", "gemini-3-pro-preview", "gemini-3-flash-preview"],
                                                    value=State.ai_model,
                                                    on_change=State.set_ai_model,
                                                    width="100%", margin_top=Spacing.SM
                                                )
                                            ),
                                            
                                            width="100%", align_items="start"
                                        ),
                                        margin_bottom=Spacing.LG, width="100%"
                                    ),

                                    ui.button("Iniciar Auditoria Inteligente", icon="rocket", on_click=State.generate_ai_analysis, is_loading=State.is_generating_ai, variant="primary", width="100%"),

                                    rx.cond(
                                        State.ai_analysis != "",
                                        rx.vstack(
                                            rx.box(
                                                rx.scroll_area(
                                                    rx.markdown(State.ai_analysis),
                                                    type="hover"
                                                ),
                                                style={"maxHeight": "500px"},
                                                bg=Color.SURFACE, border=f"1px solid {Color.BORDER}", border_radius=Design.RADIUS_LG, padding=Spacing.LG, margin_top=Spacing.LG, box_shadow=Design.SHADOW_SM, width="100%"
                                            ),
                                            rx.hstack(
                                                rx.cond(
                                                    State.ai_analysis_csv != "",
                                                    ui.button("Download CSV", icon="table", on_click=lambda: rx.download(url=State.ai_analysis_csv), variant="secondary"),
                                                ),
                                                ui.button("Refazer Auditoria", icon="rotate-ccw", on_click=State.generate_ai_analysis, variant="ghost"),
                                                spacing="2", margin_top=Spacing.MD
                                            ),
                                            width="100%"
                                        ),
                                    ),
                                    width="100%", margin_top=Spacing.SM
                                ),
                                width="100%"
                            )
                        ),
                        width="100%",
                        padding_top=Spacing.MD
                    ),
                    
                    # Ações do Relatório Final (Aspirado)
                    rx.hstack(
                        rx.cond(
                            State.analysis_pdf != "",
                            ui.button("Download PDF", icon="download", on_click=lambda: rx.download(url=State.analysis_pdf), variant="primary"),
                        ),
                        ui.button("Gerar PDF", icon="file-text", on_click=State.generate_pdf_report, variant="secondary"),
                        ui.button("Nova Análise", icon="refresh-cw", on_click=State.clear_all_files, variant="secondary"),
                        style={"gap": Spacing.MD},
                        justify_content="center",
                        margin_top=Spacing.XL,
                    ),
                    width="100%",
                    max_width="5xl",
                ),
            ),
            
            patient_history_modal(),
            spacing="0",
            align_items="center",
            width="100%",
            padding_y=Spacing.XL, padding_x=Spacing.MD
        ),
        width="100%",
    )
