"""
Análise COMPULAB x SIMUS page
Design moderno com upload aprimorado e visualização de dados premium
"""
import reflex as rx
from typing import Any
from ..state import State
from ..components.file_upload import compact_upload_card, upload_progress_indicator
from ..components import ui
from ..styles import Color, Design, Typography, Spacing

# === COMPONENTES LOCAIS ===

def metric_card_premium(title: str, value: str, icon: str, subtitle: str = "", color_scheme: str = "green", delay: str = "0s"):
    """Card de métrica com design glassmorphism e animação de entrada"""
    colors = {
        "green": (Color.SUCCESS, Color.SUCCESS_BG, "circle-check"),
        "blue": (Color.PRIMARY, Color.PRIMARY_LIGHT, "bar-chart-2"),
        "orange": (Color.WARNING, Color.WARNING_BG, "alert-triangle"),
        "red": (Color.ERROR, Color.ERROR_BG, "x-circle"),
    }
    fg, bg, default_icon = colors.get(color_scheme, colors["green"])
    
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.box(
                    rx.icon(tag=icon, size=20, color=fg),
                    bg=bg, padding="10px", border_radius="12px",
                    box_shadow=f"0 4px 12px {bg}40"
                ),
                rx.spacer(),
                rx.cond(
                    subtitle != "",
                    rx.badge(subtitle, color_scheme=color_scheme, variant="soft", size="1")
                ),
                width="100%", align_items="start"
            ),
            rx.vstack(
                rx.text(value, font_size="1.5rem", font_weight="800", color=Color.DEEP, letter_spacing="-0.02em"),
                rx.text(title, font_size="0.75rem", font_weight="600", color=Color.TEXT_SECONDARY, text_transform="uppercase", letter_spacing="0.05em"),
                spacing="1", align_items="start"
            ),
            spacing="4", align_items="start"
        ),
        bg=Color.SURFACE,
        padding=Spacing.LG,
        border_radius=Design.RADIUS_LG,
        border=f"1px solid {Color.BORDER}",
        box_shadow=Design.SHADOW_SM,
        transition="all 0.3s ease",
        _hover={
            "transform": "translateY(-4px)",
            "box_shadow": Design.SHADOW_MD,
            "border_color": fg
        },
        animation=f"fadeInUp 0.5s ease-out {delay} both"
    )

def insight_card(icon: str, title: str, description: str, type: str = "warning"):
    """Card de insight para o Action Center"""
    color_map = {
        "warning": (Color.WARNING, Color.WARNING_BG),
        "error": (Color.ERROR, Color.ERROR_BG),
        "info": (Color.PRIMARY, Color.PRIMARY_LIGHT),
        "success": (Color.SUCCESS, Color.SUCCESS_BG)
    }
    fg, bg = color_map.get(type, (Color.PRIMARY, Color.PRIMARY_LIGHT))
    
    return rx.box(
        rx.hstack(
            rx.box(
                rx.icon(tag=icon, size=20, color=fg),
                bg=bg, padding="10px", border_radius="12px",
                display="flex", align_items="center", justify_content="center"
            ),
            rx.vstack(
                rx.text(title, font_weight="700", color=Color.DEEP, font_size="0.9rem"),
                rx.text(description, font_size="0.8rem", color=Color.TEXT_SECONDARY, line_height="1.4"),
                spacing="1", align_items="start"
            ),
            spacing="3", align_items="start"
        ),
        padding=Spacing.MD,
        bg=Color.SURFACE,
        border_left=f"4px solid {fg}",
        border_radius=Design.RADIUS_MD,
        box_shadow=Design.SHADOW_SM,
        transition="transform 0.2s ease",
        _hover={"transform": "translateX(4px)"}
    )

def patient_history_modal() -> rx.Component:
    """Modal de histórico do paciente com estilo Timeline"""
    return rx.dialog.root(
        rx.dialog.content(
            # Header
            rx.hstack(
                rx.box(rx.icon(tag="user", size=24, color=Color.PRIMARY), bg=Color.PRIMARY_LIGHT, p="2", border_radius="12px"),
                rx.vstack(
                    rx.text(State.selected_patient_name, size="4", weight="bold", color=Color.DEEP),
                    rx.hstack(
                        rx.badge("PACIENTE", color_scheme="blue", variant="solid", size="1"),
                        rx.text(f"ID: {State.selected_patient_id}", size="1", color=Color.TEXT_LIGHT),
                        spacing="2", align_items="center"
                    ),
                    spacing="1"
                ),
                rx.spacer(),
                rx.dialog.close(
                    rx.button(rx.icon("x", size=18), variant="ghost", color_scheme="gray", radius="full")
                ),
                width="100%", align_items="center", margin_bottom="20px", border_bottom=f"1px solid {Color.BORDER}", padding_bottom="16px"
            ),
            
            # Corpo
            rx.scroll_area(
                rx.vstack(
                    rx.foreach(
                        State.patient_history_data,
                        lambda exam: rx.box(
                            rx.hstack(
                                # Linha do tempo visual
                                rx.vstack(
                                    rx.box(width="2px", height="100%", bg=Color.BORDER, position="absolute", left="7px", top="24px"),
                                    rx.box(width="14px", height="14px", border_radius="full", bg=rx.cond(exam.status == "Divergente", Color.ERROR, Color.SUCCESS), z_index="1"),
                                    position="relative", height="100%", min_height="60px", margin_right="12px"
                                ),
                                # Conteúdo
                                rx.vstack(
                                    rx.hstack(
                                        rx.text(exam.exam_name, weight="bold", color=Color.DEEP),
                                        rx.spacer(),
                                        rx.text(f"R$ {exam.last_value.to_string()}", weight="bold", color=Color.TEXT_PRIMARY),
                                        width="100%"
                                    ),
                                    rx.hstack(
                                        rx.icon("calendar", size=12, color=Color.TEXT_LIGHT),
                                        rx.text(exam.created_at, size="1", color=Color.TEXT_LIGHT),
                                        rx.spacer(),
                                        rx.badge(exam.status, color_scheme=rx.cond(exam.status == "Divergente", "red", "green"), variant="soft", size="1"),
                                        width="100%", align_items="center"
                                    ),
                                    rx.cond(
                                        exam.notes != "",
                                        rx.box(
                                            rx.text(f"Nota: {exam.notes}", size="1", font_style="italic"),
                                            bg=Color.BACKGROUND, p="2", border_radius="md", width="100%", margin_top="4px"
                                        )
                                    ),
                                    width="100%", spacing="1",
                                    padding_bottom="20px"
                                ),
                                align_items="start", width="100%"
                            )
                        )
                    ),
                    width="100%"
                ),
                max_height="400px"
            ),
            max_width="500px",
            border_radius="16px",
            padding="24px",
            box_shadow="0 10px 30px -10px rgba(0,0,0,0.2)"
        ),
        open=State.is_showing_patient_history,
        on_open_change=State.set_is_showing_patient_history,
    )

def action_table(headers: list[str], data: list, columns_keys: list[str], patient_key: str = "patient", is_divergence: bool = False) -> rx.Component:
    """Tabela de dados refinada com ações"""
    
    def render_row(item: Any, i: rx.Var[int]):
        bg_hover = Color.PRIMARY_LIGHT
        
        cells = [
            rx.table.cell(
                rx.text(getattr(item, key), font_size="0.85rem", color=Color.TEXT_PRIMARY),
                padding="12px 16px"
            ) for key in columns_keys
        ]
        
        # Actions
        actions = [
            ui.button("", icon="history", on_click=lambda: State.view_patient_history(getattr(item, patient_key)), variant="ghost", size="1", padding="4px")
        ]
        
        if "exam_name" in columns_keys:
            res_key = getattr(item, patient_key) + "|" + getattr(item, "exam_name")
            is_resolved = State.resolutions[res_key] == "resolvido"
            actions.append(
                ui.button(
                    "",
                    icon=rx.cond(is_resolved, "circle-check", "circle"),
                    on_click=lambda: State.toggle_resolution(getattr(item, patient_key), getattr(item, "exam_name")),
                    variant="ghost", 
                    color=rx.cond(is_resolved, Color.SUCCESS, Color.TEXT_LIGHT),
                    size="1", padding="4px"
                )
            )

        cells.append(
            rx.table.cell(
                rx.hstack(*actions, spacing="2", justify="end"),
                padding="12px 16px"
            )
        )
        
        return rx.table.row(
            *cells,
            bg=rx.cond(i % 2 == 0, "transparent", f"{Color.BACKGROUND}80"),
            _hover={"bg": f"{Color.PRIMARY}08"},
            transition="background-color 0.2s"
        )

    return rx.box(
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    *[rx.table.column_header_cell(
                        rx.text(h, size="1", weight="bold", color=Color.TEXT_SECONDARY, letter_spacing="0.05em"),
                        padding="12px 16px", bg=Color.BACKGROUND
                    ) for h in headers],
                    rx.table.column_header_cell(
                        rx.text("AÇÕES", size="1", weight="bold", color=Color.TEXT_SECONDARY, text_align="right"),
                        padding="12px 16px", bg=Color.BACKGROUND
                    )
                )
            ),
            rx.table.body(rx.foreach(data, render_row)),
            variant="surface",
            width="100%"
        ),
        border=f"1px solid {Color.BORDER}",
        border_radius=Design.RADIUS_LG,
        overflow="hidden",
        box_shadow=Design.SHADOW_SM,
        bg=Color.SURFACE
    )

def analise_page() -> rx.Component:
    """Página de Análise Premium"""
    
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
            # === HERO SECTION ===
            rx.box(
                rx.vstack(
                    ui.animated_heading("Central de Auditoria", level=1),
                    ui.text("Analise divergências financeiras entre COMPULAB e SIMUS com precisão.", color=Color.TEXT_SECONDARY),
                    align_items="center", spacing="2"
                ),
                padding_y=Spacing.XL, width="100%", display="flex", justify_content="center"
            ),

            # === UPLOAD AREA ===
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.icon("cloud-upload", color=Color.PRIMARY, size=20),
                        rx.text("Importação de Dados", weight="bold", color=Color.DEEP),
                        spacing="2", align_items="center", width="100%"
                    ),
                    rx.grid(
                        compact_upload_card("COMPULAB", erlenmeyer_small, "compulab_anl", State.compulab_file_name, State.compulab_file_size, State.handle_compulab_upload, State.clear_compulab_file, "COMPLETO"),
                        compact_upload_card("SIMUS", tubes_small, "simus_anl", State.simus_file_name, State.simus_file_size, State.handle_simus_upload, State.clear_simus_file, "COMPLETO"),
                        columns="2", spacing="4", width="100%"
                    ),
                    upload_progress_indicator(State.is_uploading),
                    
                    # Botão Analisar
                    rx.cond(
                        ~State.is_analyzing,
                        ui.button("Processar Análise Cruzada", icon="zap", on_click=State.run_analysis, disabled=~State.has_files, width="100%", variant="primary", margin_top="16px"),
                        ui.button("Analisando...", icon="loader-circle", is_loading=True, width="100%", variant="primary", margin_top="16px")
                    ),
                    
                    bg=Color.SURFACE, padding="24px", border_radius="24px", border=f"1px solid {Color.BORDER}",
                    box_shadow=Design.SHADOW_DEFAULT, max_width="800px", width="100%", margin_bottom="32px",
                    animation="fadeInUp 0.6s ease-out"
                )
            ),
            
            # === RESULTS SECTION ===
            rx.cond(
                State.has_analysis,
                rx.vstack(
                    # KPIs
                    rx.grid(
                        metric_card_premium("Faturamento Compulab", State.formatted_compulab_total, "building-2", color_scheme="blue", delay="0.1s"),
                        metric_card_premium("Faturamento Simus", State.formatted_simus_total, "database", color_scheme="green", delay="0.2s"),
                        metric_card_premium("Divergência Total", State.formatted_difference, "git-compare", "Alerta", "orange", delay="0.3s"),
                        metric_card_premium("Itens Pendentes", State.missing_exams_count.to_string(), "list-x", "Ação Necessária", "red", delay="0.4s"),
                        columns={"initial": "1", "md": "2", "lg": "4"},
                        spacing="4", width="100%", margin_bottom="32px"
                    ),
                    
                    # DASHBOARD COMPLEXO
                    rx.grid(
                        # Coluna Esquerda: Gráficos
                        rx.vstack(
                             rx.box(
                                rx.text("Distribuição de Perdas", weight="bold", color=Color.DEEP, margin_bottom="12px"),
                                rx.recharts.pie_chart(
                                    rx.recharts.pie(
                                        data=State.revenue_distribution_data,
                                        data_key="value", name_key="name",
                                        cx="50%", cy="50%", inner_radius=60, outer_radius=80,
                                        padding_angle=2, stroke="none",
                                        label=True
                                    ),
                                    rx.recharts.legend(),
                                    height=250, width="100%"
                                ),
                                bg=Color.SURFACE, p="6", border_radius="20px", border=f"1px solid {Color.BORDER}", width="100%", height="100%"
                             ),
                        ),
                        # Coluna Direita: Top Offensores e Ações
                        rx.vstack(
                             rx.box(
                                rx.hstack(
                                    rx.icon("lightbulb", color=Color.WARNING, size=18),
                                    rx.text("Insights & Ações", weight="bold", color=Color.DEEP),
                                    align_items="center", spacing="2", margin_bottom="16px"
                                ),
                                rx.vstack(
                                    rx.foreach(
                                        State.action_center_insights,
                                        lambda x: insight_card(x["icon"], x["title"], x["description"], "warning")
                                    ),
                                    spacing="3", width="100%"
                                ),
                                bg=Color.SURFACE, p="6", border_radius="20px", border=f"1px solid {Color.BORDER}", width="100%"
                             )
                        ),
                        columns={"initial": "1", "lg": "2"},
                        spacing="6", width="100%", margin_bottom="32px"
                    ),
                    
                    # TABELA DETALHADA
                    rx.box(
                        ui.segmented_control(
                            [
                                {"label": "Pacientes Faltantes", "value": "patients_missing"},
                                {"label": "Exames Faltantes", "value": "missing"},
                                {"label": "Divergência Valores", "value": "divergences"},
                                {"label": "Extras Simus", "value": "extras"},
                                {"label": "Análise IA", "value": "ai"},
                            ],
                            State.analysis_active_tab,
                            State.set_analysis_active_tab
                        ),
                        margin_bottom="20px", width="100%"
                    ),
                    
                    rx.box(
                        rx.cond(
                            State.analysis_active_tab == "patients_missing",
                            action_table(["Paciente", "Qtd Exames", "Valor Total"], State.missing_patients, ["patient", "exams_count", "total_value"], "patient")
                        ),
                        rx.cond(
                            State.analysis_active_tab == "missing",
                            action_table(["Paciente", "Exame", "Valor"], State.missing_exams, ["patient", "exam_name", "value"])
                        ),
                        rx.cond(
                            State.analysis_active_tab == "divergences",
                            action_table(["Paciente", "Exame", "Compulab", "Simus", "Diferença"], State.value_divergences, ["patient", "exam_name", "compulab_value", "simus_value", "difference"], is_divergence=True)
                        ),
                        rx.cond(
                            State.analysis_active_tab == "extras",
                            action_table(["Paciente", "Exame", "Valor Simus"], State.extra_simus_exams, ["patient", "exam_name", "simus_value"])
                        ),
                        # AI TAB
                        rx.cond(
                            State.analysis_active_tab == "ai",
                            rx.box(
                                rx.hstack(
                                    rx.icon("bot", size=32, color="white"),
                                    rx.vstack(
                                        rx.text("Auditor Virtual IA", size="5", weight="bold", color="white"),
                                        rx.text("Análise semântica e financeira avançada", color="white", opacity=0.8, size="2"),
                                    ),
                                    spacing="4", align_items="center", margin_bottom="24px"
                                ),
                                # Provider and Model Selection
                                rx.hstack(
                                    rx.vstack(
                                        rx.text("Provedor", size="2", color="white", opacity=0.7),
                                        rx.select(
                                            State.available_providers,
                                            value=State.ai_provider,
                                            on_change=State.set_ai_provider,
                                            width="150px",
                                        ),
                                        spacing="1"
                                    ),
                                    rx.vstack(
                                        rx.text("Modelo", size="2", color="white", opacity=0.7),
                                        rx.select(
                                            State.available_model_ids,
                                            value=State.ai_model,
                                            on_change=State.set_ai_model,
                                            width="200px",
                                        ),
                                        spacing="1"
                                    ),
                                    spacing="4",
                                    margin_bottom="16px",
                                    flex_wrap="wrap"
                                ),
                                # Loading status
                                rx.cond(
                                    State.ai_loading_text != "",
                                    rx.hstack(
                                        rx.spinner(size="1"),
                                        rx.text(State.ai_loading_text, color="white", opacity=0.9, size="2"),
                                        spacing="2",
                                        margin_bottom="12px"
                                    )
                                ),
                                # Generate button
                                ui.button("Gerar Relatório Inteligente", icon="sparkles", on_click=State.generate_ai_analysis, is_loading=State.is_generating_ai, variant="secondary", width="100%"),
                                # Report output
                                rx.cond(
                                    State.ai_analysis != "",
                                    rx.box(
                                        rx.markdown(State.ai_analysis, color="white"),
                                        margin_top="24px", padding="20px", bg="rgba(0,0,0,0.2)", border_radius="12px"
                                    )
                                ),
                                bg=Color.GRADIENT_PRIMARY, padding="32px", border_radius="24px", width="100%", box_shadow=Design.SHADOW_MD
                            )
                        ),
                        width="100%"
                    ),
                    
                    width="100%", animation="fadeInUp 0.8s ease-out 0.2s both"
                ),
            ),
            
            patient_history_modal(),
            
            width="100%", padding_x=Spacing.MD, padding_bottom="100px", align_items="center"
        ),
        width="100%"
    )
