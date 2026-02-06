import reflex as rx
from ..state import State
from ..styles import Color, Design, Typography, Spacing
from ..components import ui


def quick_access_card(title: str, description: str, icon: str, page: str, delay: str = "0s") -> rx.Component:
    """Card de acesso rápido com animação de entrada"""
    return rx.box(
        ui.card(
            rx.vstack(
                rx.box(
                    rx.icon(icon, size=32, color=Color.PRIMARY),
                    bg=Color.PRIMARY_LIGHT, p="4", border_radius=Design.RADIUS_LG, margin_bottom=Spacing.XS,
                    transition="transform 0.3s ease",
                    _group_hover={"transform": "scale(1.1) rotate(5deg)"}
                ),
                ui.heading(title, level=3),
                ui.text(description, size="small", color=Color.TEXT_SECONDARY),
                align_items="start",
                spacing="2"
            ),
            on_click=lambda: State.set_page(page),
            cursor="pointer",
            transition="all 0.2s ease",
            _hover={
                "box_shadow": Design.SHADOW_MD,
                "transform": "translateY(-2px)",
                "border_color": Color.PRIMARY
            }
        ),
        animation=f"fadeInUp 0.6s ease-out {delay} both",
        class_name="group"
    )


def qc_hero_card() -> rx.Component:
    """Card destaque de taxa de aprovação QC"""
    return rx.box(
        rx.flex(
            rx.vstack(
                rx.hstack(
                    rx.icon(tag="shield-check", size=14, color=Color.PRIMARY),
                    rx.text("TAXA DE APROVAÇÃO QC", font_size=Typography.SIZE_XS, font_weight="700", color=Color.TEXT_SECONDARY, letter_spacing="0.15em"),
                    align_items="center",
                    style={"gap": Spacing.XS}
                ),
                rx.text(
                    State.dashboard_approval_rate.to_string() + "%",
                    font_size=["2rem", "2.5rem", "3rem"], font_weight="800", color=Color.DEEP, line_height="1.1"
                ),
                rx.hstack(
                    rx.box(
                        rx.icon(
                            tag=rx.cond(State.dashboard_approval_rate >= 95.0, "trending-up", "trending-down"),
                            size=14, color=Color.WHITE
                        ),
                        bg=rx.cond(State.dashboard_approval_rate >= 95.0, Color.SUCCESS, Color.WARNING),
                        p="1", border_radius=Design.RADIUS_SM
                    ),
                    rx.text(
                        rx.cond(
                            State.dashboard_approval_rate >= 95.0,
                            "Excelente",
                            rx.cond(State.dashboard_approval_rate >= 85.0, "Atenção necessária", "Crítico")
                        ),
                        font_size=Typography.H5["font_size"], font_weight="600",
                        color=rx.cond(State.dashboard_approval_rate >= 95.0, Color.SUCCESS, Color.WARNING)
                    ),
                    align_items="center",
                    style={"gap": Spacing.SM}
                ),
                align_items="start",
                style={"gap": Spacing.SM},
                width="100%"
            ),
            rx.spacer(),
            rx.box(
                rx.icon(tag="activity", size=40, color=Color.WHITE),
                bg=Color.GRADIENT_PRIMARY,
                p="4", border_radius=Design.RADIUS_XL,
                display={"initial": "none", "md": "block"},
                box_shadow=Design.SHADOW_MD
            ),
            width="100%",
            align_items="center",
            direction={"initial": "column", "md": "row"},
            gap="4"
        ),
        bg=Color.SURFACE,
        border=f"1px solid {Color.BORDER}",
        border_radius=Design.RADIUS_XL,
        padding=[Spacing.MD, Spacing.LG, Spacing.XL],
        box_shadow=Design.SHADOW_SM,
        transition="all 0.2s ease",
        _hover={"box_shadow": Design.SHADOW_DEFAULT},
        animation="fadeInUp 0.4s ease-out both",
        width="100%"
    )


def alerts_panel() -> rx.Component:
    """Painel de alertas QC"""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.box(
                    rx.icon(tag="bell-ring", size=18, color=Color.WHITE),
                    bg=Color.WARNING, p="2", border_radius=Design.RADIUS_SM
                ),
                rx.text("Alertas", font_weight="700", color=Color.DEEP, font_size=Typography.SIZE_LG),
                rx.spacer(),
                ui.status_badge(State.dashboard_alerts_count.to_string() + " alertas", status="warning"),
                align_items="center",
                width="100%",
                style={"gap": Spacing.SM_MD}
            ),
            rx.divider(opacity=0.2, margin_y=Spacing.SM),

            # Reagentes vencendo
            rx.cond(
                State.has_expiring_lots,
                rx.hstack(
                    rx.icon(tag="flask-round", size=18, color=Color.WARNING),
                    rx.vstack(
                        rx.text("Reagentes vencendo", font_size=Typography.SIZE_MD_SM, font_weight="600", color=Color.TEXT_PRIMARY),
                        rx.text(State.dashboard_expiring_lots.to_string() + " lotes vencendo em 30 dias", font_size=Typography.SIZE_SM, color=Color.TEXT_SECONDARY),
                        spacing="0",
                    ),
                    width="100%", align_items="center", style={"gap": Spacing.SM_MD},
                    padding=Spacing.MD, bg=Color.WARNING_BG, border_radius=Design.RADIUS_LG,
                ),
            ),

            # Manutenções pendentes
            rx.cond(
                State.has_pending_maintenances,
                rx.hstack(
                    rx.icon(tag="wrench", size=18, color=Color.PRIMARY),
                    rx.vstack(
                        rx.text("Manutenções pendentes", font_size=Typography.SIZE_MD_SM, font_weight="600", color=Color.TEXT_PRIMARY),
                        rx.text(State.dashboard_pending_maintenances.to_string() + " equipamentos", font_size=Typography.SIZE_SM, color=Color.TEXT_SECONDARY),
                        spacing="0",
                    ),
                    width="100%", align_items="center", style={"gap": Spacing.SM_MD},
                    padding=Spacing.MD, bg=Color.PRIMARY_LIGHT, border_radius=Design.RADIUS_LG,
                ),
            ),

            # Violações Westgard
            rx.cond(
                State.westgard_violations_month != "0",
                rx.hstack(
                    rx.icon(tag="triangle-alert", size=18, color=Color.ERROR),
                    rx.vstack(
                        rx.text("Violações Westgard", font_size=Typography.SIZE_MD_SM, font_weight="600", color=Color.TEXT_PRIMARY),
                        rx.text(State.westgard_violations_month.to_string() + " este mês", font_size=Typography.SIZE_SM, color=Color.TEXT_SECONDARY),
                        spacing="0",
                    ),
                    width="100%", align_items="center", style={"gap": Spacing.SM_MD},
                    padding=Spacing.MD, bg=Color.ERROR_BG, border_radius=Design.RADIUS_LG,
                ),
            ),

            # Estado sem alertas
            rx.cond(
                ~State.has_alerts & ~State.has_expiring_lots & ~State.has_pending_maintenances,
                rx.center(
                    rx.vstack(
                        rx.box(
                            rx.icon(tag="circle-check", size=36, color=Color.SUCCESS),
                            bg=Color.SUCCESS_BG, p="4", border_radius=Design.RADIUS_FULL
                        ),
                        rx.text("Tudo em ordem!", font_weight="600", color=Color.SUCCESS),
                        rx.text("Nenhum alerta ativo", font_size=Typography.SIZE_SM, color=Color.TEXT_SECONDARY),
                        align_items="center",
                        spacing="2"
                    ),
                    height="120px", width="100%"
                ),
            ),

            width="100%",
            height="100%",
            spacing="3",
        ),
        bg=Color.SURFACE,
        border=f"1px solid {Color.BORDER}",
        border_radius=Design.RADIUS_XL,
        padding=Spacing.LG,
        height="100%",
        animation="fadeInUp 0.6s ease-out 0.15s both"
    )


def recent_records_table() -> rx.Component:
    """Tabela de registros QC recentes"""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.icon(tag="table", size=20, color=Color.PRIMARY),
                rx.text("Registros Recentes", style=Typography.H3, color=Color.DEEP),
                rx.spacer(),
                ui.button("Ver todos", icon="arrow-right", variant="ghost", on_click=lambda: State.set_page("proin")),
                align_items="center",
                width="100%",
                style={"gap": Spacing.SM_MD}
            ),
            rx.divider(opacity=0.2),
            rx.cond(
                State.recent_qc_records.length() > 0,
                rx.box(
                    rx.foreach(
                        State.recent_qc_records,
                        lambda record: rx.hstack(
                            rx.vstack(
                                rx.text(record["exam_name"], font_size=Typography.SIZE_MD_SM, font_weight="600", color=Color.TEXT_PRIMARY),
                                rx.text(record["date"], font_size=Typography.SIZE_SM_XS, color=Color.TEXT_SECONDARY),
                                spacing="0",
                                align_items="start",
                                flex="1",
                            ),
                            rx.vstack(
                                rx.text("Nível", font_size=Typography.SIZE_2XS, color=Color.TEXT_SECONDARY),
                                rx.text(record["level"], font_size=Typography.SIZE_SM, font_weight="500"),
                                spacing="0", align_items="center",
                            ),
                            rx.vstack(
                                rx.text("CV%", font_size=Typography.SIZE_2XS, color=Color.TEXT_SECONDARY),
                                rx.text(
                                    record["cv"].to(str),
                                    font_size=Typography.SIZE_SM, font_weight="600",
                                    color=rx.cond(record["status"] == "OK", Color.SUCCESS, Color.ERROR)
                                ),
                                spacing="0", align_items="center",
                            ),
                            rx.box(
                                rx.text(
                                    record["status"],
                                    font_size=Typography.SIZE_SM_XS, font_weight="700",
                                    color=rx.cond(record["status"] == "OK", Color.SUCCESS, Color.ERROR)
                                ),
                                bg=rx.cond(record["status"] == "OK", Color.SUCCESS_BG, Color.ERROR_BG),
                                px="3", py="1", border_radius=Design.RADIUS_FULL
                            ),
                            width="100%", align_items="center",
                            padding=Spacing.SM, border_radius=Design.RADIUS_LG,
                            border=f"1px solid {Color.BORDER}",
                            _hover={"bg": Color.BACKGROUND},
                            transition="all 0.2s ease",
                        )
                    ),
                    width="100%",
                    display="flex", flex_direction="column", gap=Spacing.XS,
                ),
                rx.center(
                    rx.vstack(
                        rx.icon(tag="clipboard", size=36, color=Color.TEXT_SECONDARY),
                        rx.text("Nenhum registro ainda", font_weight="500", color=Color.TEXT_SECONDARY),
                        align_items="center", spacing="2"
                    ),
                    height="120px", width="100%"
                ),
            ),
            width="100%",
            spacing="3",
        ),
        bg=Color.SURFACE,
        border=f"1px solid {Color.BORDER}",
        border_radius=Design.RADIUS_XL,
        padding=Spacing.LG,
        animation="fadeInUp 0.7s ease-out 0.2s both",
        width="100%"
    )


def dashboard_page() -> rx.Component:
    """Dashboard de Controle de Qualidade"""

    return rx.fragment(
        rx.box(
            rx.vstack(
                # Welcome Banner
                rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.text("🔬", font_size=Typography.DISPLAY["font_size"]),
                            rx.text("Controle de Qualidade", style=Typography.H1, color=Color.DEEP),
                            align_items="center",
                            style={"gap": Spacing.SM_MD}
                        ),
                        rx.text("Painel de monitoramento e indicadores", style=Typography.BODY_SECONDARY, color=Color.TEXT_SECONDARY),
                        align_items="center",
                        style={"gap": Spacing.XS}
                    ),
                    width="100%", display="flex", justify_content="center",
                    animation="fadeInUp 0.4s ease-out both",
                    padding_y=[Spacing.MD, Spacing.LG, Spacing.XL],
                    padding_x=[Spacing.MD, Spacing.LG]
                ),

                # Main Grid
                rx.grid(
                    # Coluna Esquerda - Métricas QC
                    rx.vstack(
                        qc_hero_card(),

                        # KPI Cards
                        rx.grid(
                            ui.stat_card("QC Hoje", State.dashboard_total_today.to_string(), "clipboard-check", "primary", "Registros"),
                            ui.stat_card("QC Mês", State.dashboard_total_month.to_string(), "calendar-check", "primary", "Registros"),
                            ui.stat_card("Westgard", State.westgard_violations_month.to_string(), "triangle-alert", "error", "Violações"),
                            ui.stat_card("Reagentes", State.dashboard_expiring_lots.to_string(), "flask-round", "warning", "Vencendo"),
                            columns={"initial": "2", "sm": "2"},
                            spacing="4",
                            width="100%"
                        ),
                        width="100%",
                        spacing="4"
                    ),

                    # Coluna Direita - Alertas
                    alerts_panel(),

                    columns={"initial": "1", "md": "2"},
                    spacing="6",
                    width="100%",
                    max_width="6xl", margin_x="auto", margin_bottom=Spacing.XL
                ),

                # Tabela de registros recentes
                rx.box(
                    recent_records_table(),
                    width="100%",
                    max_width="6xl", margin_x="auto", margin_bottom=Spacing.XL
                ),

                rx.divider(max_width="6xl", margin_x="auto", margin_bottom=Spacing.XL, opacity=0.2),

                # Quick Access
                rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.icon(tag="layout-grid", size=20, color=Color.PRIMARY),
                            rx.text("Acesso Rápido", style=Typography.H2, color=Color.DEEP),
                            align_items="center",
                            style={"gap": Spacing.SM_MD}
                        ),
                        rx.text("Atalhos para as principais funções", font_size=Typography.SIZE_MD_SM, color=Color.TEXT_SECONDARY),
                        align_items="center",
                        style={"gap": Spacing.XS},
                        margin_bottom=Spacing.LG
                    ),
                    animation="fadeInUp 0.8s ease-out 0.3s both"
                ),
                rx.grid(
                    quick_access_card(
                        "Registrar QC",
                        "Registre novos controles de qualidade com validação Westgard automática.",
                        "clipboard-plus",
                        "proin",
                        "0.35s"
                    ),
                    quick_access_card(
                        "Reagentes e Lotes",
                        "Gerencie estoque de reagentes, datas de validade e consumo.",
                        "flask-round",
                        "proin",
                        "0.45s"
                    ),
                    quick_access_card(
                        "Relatórios QC",
                        "Gere relatórios em PDF por período para auditoria e controle.",
                        "file-bar-chart",
                        "proin",
                        "0.55s"
                    ),
                    columns={"initial": "1", "md": "3"},
                    spacing="6",
                    width="100%",
                    max_width="6xl", margin_x="auto", margin_bottom=Spacing.XXL
                ),

                width="100%",
                align_items="center",
                padding_bottom=Spacing.XXL
            ),
            width="100%"
        )
    )
