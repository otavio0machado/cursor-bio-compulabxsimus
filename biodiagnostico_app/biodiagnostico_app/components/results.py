import reflex as rx
from ..state import State
from ..styles import Color, Design, Spacing, Typography

def metric_card(
    title: str,
    value: str,
    icon: str,
    help_text: str = "",
    delta: str = None,
    delta_positive: bool = True
) -> rx.Component:
    """Card de métrica individual com design moderno e acessível - usa ícones Lucide"""
    return rx.box(
        rx.hstack(
            # Ícone Lucide em container com fundo (Fase 1: Usando Primary Light)
            rx.box(
                rx.icon(tag=icon, size=32, color=Color.PRIMARY),
                padding=Spacing.MD,
                border_radius=Design.RADIUS_XL,
                bg=Color.PRIMARY_LIGHT,
                display="flex",
                align_items="center",
                justify_content="center"
            ),
            rx.vstack(
                rx.text(
                    title,
                    **Typography.LABEL,
                    text_transform="uppercase",
                    letter_spacing="0.05em",
                    color=Color.TEXT_SECONDARY
                ),
                rx.text(
                    value,
                    font_size=["1.75rem", "2rem", "2.25rem"],
                    font_weight="800",
                    line_height="1.2",
                    color=Color.DEEP
                ),
                rx.cond(
                    delta is not None,
                    rx.text(
                        delta,
                        font_size="0.875rem",
                        font_weight="600",
                        color=rx.cond(
                            delta_positive,
                            Color.SUCCESS,
                            Color.ERROR
                        )
                    ),
                ),
                rx.cond(
                    help_text != "",
                    rx.text(
                        help_text,
                        **Typography.CAPTION,
                        color=Color.TEXT_SECONDARY
                    ),
                ),
                align_items="start",
                style={"gap": "4px"}, # Fase 2: Usando gap para precisão
            ),
            align_items="center",
            style={"gap": Spacing.LG}, # Fase 2: CORREÇÃO DE BUG (gap em vez de spacing)
        ),
        bg=Color.SURFACE,
        padding=Spacing.LG,
        border_radius=Design.RADIUS_XL,
        box_shadow=Design.SHADOW_DEFAULT,
        border=f"1px solid {Color.BORDER}",
        transition="all 0.3s ease",
        _hover={
            "box_shadow": Design.SHADOW_LG,
            "transform": "translateY(-4px)",
            "border_color": Color.PRIMARY
        }
    )

def results_summary() -> rx.Component:
    """Resumo dos resultados da análise"""
    return rx.cond(
        State.has_analysis,
        rx.vstack(
            rx.hstack(
                rx.icon(tag="trending_up", size=28, color=Color.PRIMARY),
                rx.text(
                    "Resumo da Análise",
                    style=Typography.H4, # Fase 1: Removido class_name manual
                    color=Color.DEEP
                ),
                align_items="center",
                style={"gap": "12px"},
            ),
            rx.grid(
                metric_card(
                    title="COMPULAB Total",
                    value=State.formatted_compulab_total,
                    icon="wallet",
                    help_text=f"{State.compulab_count} pacientes",
                ),
                metric_card(
                    title="SIMUS Total",
                    value=State.formatted_simus_total,
                    icon="coins",
                    help_text=f"{State.simus_count} pacientes",
                ),
                metric_card(
                    title="Diferença Total",
                    value=State.formatted_difference,
                    icon="trending_down",
                    help_text="COMPULAB - SIMUS",
                    delta=f"{State.difference_percent:.1f}%",
                    delta_positive=State.difference >= 0,
                ),
                metric_card(
                    title="Exames Faltantes",
                    value=f"{State.missing_exams_count}",
                    icon="triangle_alert", # Fase 2: Nome de ícone correto
                    help_text="no SIMUS",
                ),
                columns={"initial": "1", "sm": "2", "md": "4"}, # Fase 2: Breakpoints dict
                style={"gap": Spacing.LG},
                width="100%",
            ),
            style={"gap": Spacing.LG},
            width="100%",
        ),
    )

def breakdown_section() -> rx.Component:
    """Seção de explicação da diferença"""
    return rx.cond(
        State.has_analysis,
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.text("🧭", font_size="1.5rem"),
                    rx.text(
                        "Por que existe essa diferença?",
                        style=Typography.H4,
                        color=Color.DEEP
                    ),
                    align_items="center",
                    style={"gap": "12px"},
                ),
                # Resumo em cards grid
                rx.grid(
                    rx.box(
                        rx.vstack(
                            rx.text("👤", font_size="1.5rem"),
                            rx.text("Pacientes Faltantes", style=Typography.SMALL, color=Color.TEXT_SECONDARY),
                            rx.text(
                                f"R$ {State.missing_patients_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                                style=Typography.H5,
                                color=Color.DEEP
                            ),
                            align_items="center",
                            style={"gap": "4px"},
                        ),
                        bg=Color.SURFACE,
                        padding=Spacing.MD,
                        border_radius=Design.RADIUS_LG,
                        border=f"1px solid {Color.BORDER}",
                    ),
                    rx.box(
                        rx.vstack(
                            rx.text("📝", font_size="1.5rem"),
                            rx.text("Exames Faltantes", style=Typography.SMALL, color=Color.TEXT_SECONDARY),
                            rx.text(
                                f"R$ {State.missing_exams_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                                style=Typography.H5,
                                color=Color.DEEP
                            ),
                            align_items="center",
                            style={"gap": "4px"},
                        ),
                        bg=Color.SURFACE,
                        padding=Spacing.MD,
                        border_radius=Design.RADIUS_LG,
                        border=f"1px solid {Color.BORDER}",
                    ),
                    rx.box(
                        rx.vstack(
                            rx.text("💸", font_size="1.5rem"),
                            rx.text("Divergências", style=Typography.SMALL, color=Color.TEXT_SECONDARY),
                            rx.text(
                                f"R$ {State.divergences_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                                style=Typography.H5,
                                color=Color.DEEP
                            ),
                            align_items="center",
                            style={"gap": "4px"},
                        ),
                        bg=Color.SURFACE,
                        padding=Spacing.MD,
                        border_radius=Design.RADIUS_LG,
                        border=f"1px solid {Color.BORDER}",
                    ),
                    rx.box(
                        rx.vstack(
                            rx.text("✅", font_size="1.5rem"),
                            rx.text("Total Explicado", style=Typography.SMALL, color=Color.TEXT_SECONDARY),
                            rx.text(
                                f"R$ {State.explained_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                                style=Typography.H5,
                                color=Color.DEEP
                            ),
                            align_items="center",
                            style={"gap": "4px"},
                        ),
                        bg=Color.SURFACE,
                        padding=Spacing.MD,
                        border_radius=Design.RADIUS_LG,
                        border=f"1px solid {Color.BORDER}",
                    ),
                    rx.box(
                        rx.vstack(
                            rx.text("❓", font_size="1.5rem"),
                            rx.text("Diferença Residual", style=Typography.SMALL, color=Color.TEXT_SECONDARY),
                            rx.text(
                                f"R$ {State.residual:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                                style=Typography.H5,
                                color=Color.ERROR
                            ),
                            align_items="center",
                            style={"gap": "4px"},
                        ),
                        bg=Color.SURFACE,
                        padding=Spacing.MD,
                        border_radius=Design.RADIUS_LG,
                        border=f"1px solid {Color.ERROR}40",
                    ),
                    columns={"initial": "1", "sm": "3", "md": "5"},
                    style={"gap": Spacing.MD},
                    width="100%",
                ),
                padding=Spacing.LG,
                border_radius=Design.RADIUS_XL,
                background_image=f"linear-gradient(to br, {Color.BACKGROUND}, {Color.PRIMARY_LIGHT})",
                style={"gap": Spacing.LG},
                width="100%",
            ),
            margin_top=Spacing.XL,
        ),
    )

def missing_exams_table() -> rx.Component:
    """Tabela de exames faltantes"""
    return rx.cond(
        State.missing_exams_count > 0,
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.box(rx.icon(tag="triangle_alert", color=Color.WARNING), padding="8px", bg=Color.WARNING_BG, border_radius="8px"),
                    rx.text(
                        f"Exames Faltantes ({State.missing_exams_count})",
                        style=Typography.H4,
                        color=Color.DEEP
                    ),
                    align_items="center",
                    style={"gap": "12px"},
                ),
                rx.data_table(
                    data=State.missing_exams,
                    columns=[
                        {"name": "patient", "label": "Paciente"},
                        {"name": "exam_name", "label": "Exame"},
                        {"name": "value", "label": "Valor (R$)"},
                    ],
                    pagination=True,
                    search=True,
                    sort=True,
                ),
                style={"gap": Spacing.LG},
                width="100%",
            ),
            padding=Spacing.LG,
            bg=Color.SURFACE,
            border_radius=Design.RADIUS_XL,
            box_shadow=Design.SHADOW_DEFAULT,
            border=f"1px solid {Color.BORDER}",
            margin_top=Spacing.XL,
        ),
    )

def divergences_table() -> rx.Component:
    """Tabela de divergências de valores"""
    return rx.cond(
        State.divergences_count > 0,
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.box(rx.icon(tag="coins", color=Color.PRIMARY), padding="8px", bg=Color.PRIMARY_LIGHT, border_radius="8px"),
                    rx.text(
                        f"Divergências de Valores ({State.divergences_count})",
                        style=Typography.H4,
                        color=Color.DEEP
                    ),
                    align_items="center",
                    style={"gap": "12px"},
                ),
                rx.data_table(
                    data=State.value_divergences,
                    columns=[
                        {"name": "patient", "label": "Paciente"},
                        {"name": "exam_name", "label": "Exame"},
                        {"name": "compulab_value", "label": "COMPULAB (R$)"},
                        {"name": "simus_value", "label": "SIMUS (R$)"},
                        {"name": "difference", "label": "Diferença (R$)"},
                    ],
                    pagination=True,
                    search=True,
                    sort=True,
                ),
                style={"gap": Spacing.LG},
                width="100%",
            ),
            padding=Spacing.LG,
            bg=Color.SURFACE,
            border_radius=Design.RADIUS_XL,
            box_shadow=Design.SHADOW_DEFAULT,
            border=f"1px solid {Color.BORDER}",
            margin_top=Spacing.XL,
        ),
    )

def ai_analysis_section() -> rx.Component:
    """Seção de análise por IA - Design Premium"""
    return rx.box(
        rx.vstack(
            # Header Premium
            rx.box(
                rx.hstack(
                    rx.box(
                        rx.icon(tag="bot", size=24, color="white"),
                        padding="10px",
                        bg="rgba(255,255,255,0.2)",
                        border_radius="12px",
                        backdrop_filter="blur(4px)"
                    ),
                    rx.vstack(
                        rx.text("Auditoria Inteligente", style=Typography.H4, color="white"),
                        rx.text("Análise automatizada por IA OpenAI", style=Typography.SMALL, color="rgba(255,255,255,0.8)"),
                        align_items="start",
                        style={"gap": "0px"},
                    ),
                    align_items="center",
                    style={"gap": Spacing.MD},
                    padding=Spacing.LG,
                ),
                background_image=Color.GRADIENT_PRIMARY,
                border_radius=f"{Design.RADIUS_XL} {Design.RADIUS_XL} 0 0",
                width="100%",
            ),
            
            # Corpo do Card
            rx.box(
                rx.vstack(
                    # Features da IA (Grid Responsivo conforme Guardrail #2)
                    rx.grid(
                        rx.box(
                            rx.vstack(
                                rx.icon(tag="zap", size=20, color=Color.PRIMARY),
                                rx.text("Análise Paralela", style=Typography.SMALL, text_align="center"),
                                align_items="center",
                                style={"gap": "4px"},
                            ),
                            bg=Color.BACKGROUND, padding=Spacing.MD, border_radius=Design.RADIUS_LG,
                        ),
                        rx.box(
                            rx.vstack(
                                rx.icon(tag="target", size=20, color=Color.PRIMARY),
                                rx.text("Precisão 0.02", style=Typography.SMALL, text_align="center"),
                                align_items="center",
                                style={"gap": "4px"},
                            ),
                            bg=Color.BACKGROUND, padding=Spacing.MD, border_radius=Design.RADIUS_LG,
                        ),
                        rx.box(
                            rx.vstack(
                                rx.icon(tag="file_check", size=20, color=Color.PRIMARY),
                                rx.text("CSV + PDF", style=Typography.SMALL, text_align="center"),
                                align_items="center",
                                style={"gap": "4px"},
                            ),
                            bg=Color.BACKGROUND, padding=Spacing.MD, border_radius=Design.RADIUS_LG,
                        ),
                        columns={"initial": "3"},
                        style={"gap": Spacing.MD},
                        width="100%",
                    ),
                    
                    # API Key ou Status
                    rx.cond(
                        State.openai_api_key == "",
                        rx.box(
                            rx.vstack(
                                rx.hstack(
                                    rx.icon(tag="key", size=18, color=Color.WARNING),
                                    rx.text("Configure sua API Key", style=Typography.LABEL, color=Color.DEEP),
                                    align_items="center",
                                    style={"gap": "8px"},
                                ),
                                rx.input(
                                    placeholder="sk-...",
                                    type="password",
                                    on_change=State.set_api_key,
                                    border_radius=Design.RADIUS_MD,
                                    min_height="44px",
                                ),
                                style={"gap": Spacing.MD},
                                width="100%",
                            ),
                            bg=Color.WARNING_BG, padding=Spacing.LG, border_radius=Design.RADIUS_LG, width="100%",
                        ),
                        rx.vstack(
                            rx.hstack(
                                rx.icon(tag="circle_check", size=18, color=Color.SUCCESS),
                                rx.text("API OpenAI conectada", style=Typography.SMALL, color=Color.SUCCESS),
                                align_items="center",
                                style={"gap": "8px"},
                            ),
                            # Botão de Auditoria
                            rx.button(
                                rx.hstack(
                                    rx.cond(State.is_generating_ai, rx.spinner(size="1"), rx.icon(tag="rocket", size=18)),
                                    rx.text("Iniciar Auditoria Inteligente"),
                                    align_items="center",
                                    style={"gap": "8px"},
                                ),
                                on_click=State.generate_ai_analysis,
                                disabled=State.is_generating_ai | ~State.has_analysis,
                                background_image=Color.GRADIENT_PRIMARY,
                                color="white",
                                width="100%",
                                padding="1.5rem",
                                border_radius=Design.RADIUS_LG,
                                _hover={"opacity": 0.9, "transform": "translateY(-2px)"},
                                transition="all 0.2s ease",
                            ),
                            width="100%",
                            style={"gap": Spacing.MD},
                        ),
                    ),
                    style={"gap": Spacing.LG},
                    padding=Spacing.LG,
                ),
                bg=Color.SURFACE,
                border_radius=f"0 0 {Design.RADIUS_XL} {Design.RADIUS_XL}",
                border_x=f"1px solid {Color.BORDER}",
                border_bottom=f"1px solid {Color.BORDER}",
                width="100%",
            ),
            style={"gap": "0px"},
            width="100%",
        ),
        margin_top=Spacing.XL,
        width="100%",
    )
