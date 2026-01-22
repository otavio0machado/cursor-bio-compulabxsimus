"""
Análise COMPULAB x SIMUS page
Design moderno com upload aprimorado e visualização de dados premium
"""
import reflex as rx
from typing import Any
from ..state import State
from ..components.file_upload import compact_upload_card, upload_progress_indicator
from ..components.save_analysis_modal import save_analysis_modal, saved_analyses_list
from ..components.analysis.widgets import metric_card_premium, insight_card, patient_history_modal, action_table
from ..components import ui
from ..styles import Color, Design, Spacing

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
        # Background Decor
        rx.box(
            position="fixed", top="0", left="0", width="100%", height="100%", z_index="-1",
            background=f"radial-gradient(circle at 10% 20%, {Color.PRIMARY_LIGHT}40 0%, transparent 40%), radial-gradient(circle at 90% 80%, {Color.PRIMARY_LIGHT}40 0%, transparent 40%)",
            pointer_events="none"
        ),
        
        rx.center(
            rx.vstack(
                # === HERO SECTION REMASTERED ===
                rx.vstack(
                    rx.badge("CENTRAL DE AUDITORIA", color_scheme="green", variant="soft", size="3", radius="full"),
                    ui.animated_heading("Painel de Controle Financeiro", level=1, color=Color.DEEP, font_size="3.5rem", letter_spacing="-2px"),
                    rx.text(
                        "Sincronização em tempo real entre COMPULAB e SIMUS. Detecte divergências com precisão cirúrgica.",
                        color=Color.TEXT_SECONDARY,
                        text_align="center",
                        font_size="1.1rem",
                        max_width="600px",
                        line_height="1.6"
                    ),
                    spacing="4", align_items="center", margin_bottom="48px"
                ),

                # === SAVED ANALYSES (Floating Glass) ===
                rx.box(
                    rx.accordion.root(
                        rx.accordion.item(
                            header=rx.text("📂 Histórico de Arquivos", weight="bold", color=Color.PRIMARY),
                            content=saved_analyses_list(),
                        ),
                        collapsible=True, variant="ghost"
                    ),
                    bg="rgba(255,255,255,0.5)", backdrop_filter="blur(10px)",
                    padding="16px", border_radius="20px", border=f"1px solid {Color.BORDER}",
                    width="100%", max_width="900px", margin_bottom="48px"
                ),

                # === UPLOAD AREA (Glassmorphism) ===
                rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.icon("cloud-upload", color=Color.PRIMARY, size=24),
                            rx.text("Upload de Relatórios", weight="bold", color=Color.DEEP, size="4"),
                            spacing="3", align_items="center", width="100%", justify_content="center", margin_bottom="24px"
                        ),
                        rx.grid(
                            compact_upload_card("COMPULAB", erlenmeyer_small, "compulab_anl", State.compulab_file_name, State.compulab_file_size, State.handle_compulab_upload, State.clear_compulab_file, "COMPLETO"),
                            compact_upload_card("SIMUS", tubes_small, "simus_anl", State.simus_file_name, State.simus_file_size, State.handle_simus_upload, State.clear_simus_file, "COMPLETO"),
                            columns="2", spacing="6", width="100%"
                        ),
                        upload_progress_indicator(State.is_uploading),
                        
                        rx.cond(
                            ~State.is_analyzing,
                            ui.button("Iniciar Auditoria Cruzada", icon="zap", on_click=State.run_analysis, disabled=~State.has_files, width="100%", variant="primary", size="4", margin_top="32px", padding="24px"),
                            ui.button("Processando Inteligência de Dados...", icon="loader-circle", is_loading=True, width="100%", variant="primary", margin_top="32px", padding="24px")
                        ),
                        
                        padding="48px",
                    ),
                    bg="rgba(255, 255, 255, 0.8)",
                    backdrop_filter="blur(20px)",
                    border_radius="32px", border=f"1px solid white",
                    box_shadow="0 25px 50px -12px rgba(0, 0, 0, 0.1)", 
                    width="100%", max_width="1000px", margin_bottom="64px",
                    animation="fadeInUp 0.6s ease-out"
                ),
                
                # === RESULTS SECTION ===
                rx.cond(
                    State.has_analysis,
                    rx.flex(
                        # === LEFT PANEL ===
                        rx.vstack(
                            # KPI Grid
                            rx.grid(
                                metric_card_premium("Faturamento Compulab", State.formatted_compulab_total, "building-2", color_scheme="blue", delay="0.1s"),
                                metric_card_premium("Faturamento Simus", State.formatted_simus_total, "database", color_scheme="green", delay="0.2s"),
                                metric_card_premium("Divergência Total", State.formatted_difference, "git-compare", "Alerta", "orange", delay="0.3s"),
                                metric_card_premium("Itens Pendentes", State.missing_exams_count.to_string(), "list-x", "Ação Necessária", "red", delay="0.4s"),
                                columns={"initial": "1", "md": "2", "xl": "2"},
                                spacing="5", width="100%", margin_bottom="48px"
                            ),
                            
                            # Charts & Insights
                            rx.grid(
                                # Chart Card
                                rx.vstack(
                                    rx.text("Distribuição de Perdas", weight="bold", color=Color.DEEP, margin_bottom="12px"),
                                    rx.recharts.pie_chart(
                                        rx.recharts.pie(
                                            data=State.revenue_distribution_data,
                                            data_key="value", name_key="name",
                                            cx="50%", cy="50%", inner_radius=70, outer_radius=90,
                                            padding_angle=2, stroke="none", label=True
                                        ),
                                        rx.recharts.legend(),
                                        height=300, width="100%"
                                    ),
                                    bg="rgba(255,255,255,0.7)", p="8", border_radius="24px", border=f"1px solid {Color.BORDER}", width="100%"
                                 ),
                                # Insights List
                                rx.vstack(
                                    rx.hstack(
                                        rx.icon("lightbulb", color=Color.WARNING, size=20),
                                        rx.text("Insights & Ações", weight="bold", color=Color.DEEP),
                                        align_items="center", spacing="3", margin_bottom="16px"
                                    ),
                                    rx.vstack(
                                        rx.foreach(
                                            State.action_center_insights,
                                            lambda x: insight_card(x["icon"], x["title"], x["description"], "warning")
                                        ),
                                        spacing="4", width="100%"
                                    ),
                                    bg="rgba(255,255,255,0.7)", p="8", border_radius="24px", border=f"1px solid {Color.BORDER}", width="100%"
                                ),
                                columns={"initial": "1", "xl": "2"},
                                spacing="6", width="100%", margin_bottom="48px"
                            ),
                            
                            # Data Controls
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
                                margin_bottom="32px", width="100%"
                            ),
                            
                            # Tab Content
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
                                rx.cond(
                                    State.analysis_active_tab == "ai",
                                    # ... AI Content (Already Premium enough, keeping logic) ...
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
                                                    width="150px", color="white"
                                                ),
                                                spacing="1"
                                            ),
                                            rx.vstack(
                                                rx.text("Modelo", size="2", color="white", opacity=0.7),
                                                rx.select(
                                                    State.available_model_ids,
                                                    value=State.ai_model,
                                                    on_change=State.set_ai_model,
                                                    width="200px", color="white"
                                                ),
                                                spacing="1"
                                            ),
                                            spacing="4",
                                            margin_bottom="16px",
                                            flex_wrap="wrap"
                                        ),
                                        rx.cond(
                                            State.ai_loading_text != "",
                                            rx.hstack(
                                                rx.spinner(size="1", color="white"),
                                                rx.text(State.ai_loading_text, color="white", opacity=0.9, size="2"),
                                                spacing="2", margin_bottom="12px"
                                            )
                                        ),
                                        ui.button("Gerar Relatório Inteligente", icon="sparkles", on_click=State.generate_ai_analysis, is_loading=State.is_generating_ai, variant="secondary", width="100%"),
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
                            
                            flex="1", min_width="0",
                            animation="fadeInUp 0.8s ease-out 0.2s both",
                            padding_right={"initial": "0", "lg": Spacing.LG},
                            margin_bottom={"initial": "32px", "lg": "0"},
                        ),

                        # === RIGHT PANEL (Floating Preview) ===
                        rx.cond(
                            State.pdf_preview_b64 != "",
                            rx.box(
                                rx.vstack(
                                    rx.hstack(
                                        rx.icon("file-check", color=Color.PRIMARY, size=24),
                                        rx.text("Preview do Relatório", weight="bold", color=Color.DEEP, size="4"),
                                        rx.spacer(),
                                        save_analysis_modal(),
                                        rx.button(rx.icon("refresh-cw", size=16), on_click=State.generate_pdf_report, variant="ghost", size="1"),
                                        align_items="center", width="100%", padding_bottom="16px", border_bottom=f"1px solid {Color.BORDER}"
                                    ),
                                    rx.box(
                                        rx.html(f'<iframe src="data:application/pdf;base64,' + State.pdf_preview_b64 + '" width="100%" height="100%" style="border: none; border-radius: 12px;"></iframe>'),
                                        width="100%", height="calc(100vh - 250px)", min_height="600px"
                                    ),
                                    height="100%", width="100%", spacing="4"
                                ),
                                width={"initial": "100%", "lg": "500px"}, 
                                min_width={"initial": "100%", "lg": "400px"},
                                flex_shrink="0",
                                bg=Color.SURFACE,
                                border=f"1px solid {Color.BORDER}",
                                border_radius=Design.RADIUS_XL,
                                padding=Spacing.LG,
                                height="fit-content",
                                position={"initial": "relative", "lg": "sticky"}, 
                                top="40px",
                                box_shadow=Design.SHADOW_LG
                            ),
                            rx.box() 
                        ),
                        
                        width="100%",
                        justify_content="start",
                        direction={"initial": "column", "lg": "row"},
                        align_items="start", gap="32px"
                    ),
                ),
            
                patient_history_modal(),
                width="100%", max_width="1400px", padding_x=[Spacing.MD, Spacing.LG], padding_bottom="100px"
            ),
            width="100%"
        ),
        width="100%",
        min_height="100vh",
        background_color="#F8FAFC" # Base color under gradient
    )
