import reflex as rx
from ...state import State
from ...styles import Color, Design, Typography, Spacing
from ...components import ui
from .helpers import format_cv, qc_status_label, qc_status_kind


def dashboard_tab() -> rx.Component:
    """Aba Dashboard - Vis\u00e3o geral (Purificada)"""
    return rx.vstack(
        # Header with Refresh Button
        rx.hstack(
            rx.vstack(
                ui.heading("Vis\u00e3o Geral", level=2),
                ui.text("Monitoramento de qualidade e pend\u00eancias", size="small", color=Color.TEXT_SECONDARY),
                spacing="1", align_items="start",
            ),
            rx.spacer(),
            rx.button(
                rx.hstack(
                    rx.icon(tag="refresh_cw", size=18),
                    rx.text("Atualizar", display=["none", "none", "block"]),
                    style={"gap": Spacing.SM},
                ),
                on_click=State.load_data_from_db(True),
                variant="ghost", size="2", color=Color.TEXT_SECONDARY,
                _hover={"bg": Color.PRIMARY_LIGHT, "color": Color.DEEP},
                border_radius=Design.RADIUS_LG,
                aria_label="Atualizar dados"
            ),
            width="100%", align_items="center", margin_bottom=Spacing.LG, max_width="6xl", margin_x="auto"
        ),

        # Grid de KPI Cards - Responsivo
        rx.box(
            rx.grid(
                ui.stat_card("Registros Hoje", State.dashboard_total_today, "clipboard-list", "info"),
                ui.stat_card("Registros do M\u00eas", State.dashboard_total_month, "calendar", "success"),
                ui.stat_card("Taxa de Aprova\u00e7\u00e3o", State.dashboard_approval_rate.to_string() + "%", "circle-check", "success", "CV \u2264 5%"),
                rx.cond(
                    State.has_alerts,
                    ui.stat_card("Alertas CV > 5%", State.dashboard_alerts_count, "triangle-alert", "error"),
                    ui.stat_card("Sem Alertas", "0", "sparkles", "success")
                ),
                columns={"initial": "1", "sm": "2", "md": "2", "lg": "4"},
                spacing="4", width="100%",
            ),
            margin_bottom=Spacing.LG, max_width="6xl", margin_x="auto", width="100%"
        ),

        # Grid Secund\u00e1rio (Pend\u00eancias e Alertas)
        rx.box(
            rx.grid(
                # Coluna 1-2: Pend\u00eancias
                rx.box(
                    rx.vstack(
                        ui.heading("Pend\u00eancias & Alertas", level=3),
                        ui.card(
                            rx.vstack(
                                # Manuten\u00e7\u00f5es
                                rx.box(
                                    rx.hstack(
                                        rx.box(
                                            rx.icon(tag="wrench", size=24, color=Color.WARNING),
                                            bg=Color.WARNING_BG, p="3", border_radius=Design.RADIUS_MD,
                                            display="flex", align_items="center", justify_content="center"
                                        ),
                                        rx.vstack(
                                            rx.text("Manuten\u00e7\u00f5es Pendentes", style=Typography.LABEL, color=Color.TEXT_SECONDARY),
                                            ui.text("Equipamentos aguardando revis\u00e3o", size="small"),
                                            spacing="0", align_items="start"
                                        ),
                                        rx.spacer(),
                                        rx.text(
                                            State.dashboard_pending_maintenances,
                                            font_size=Typography.DISPLAY["font_size"], font_weight="800",
                                            color=rx.cond(State.has_pending_maintenances, Color.WARNING, Color.SUCCESS),
                                            line_height="1"
                                        ),
                                        width="100%", align_items="center",
                                    ),
                                    padding=Spacing.MD, width="100%", bg=Color.SURFACE, border=f"1px solid {Color.BORDER}", border_radius=Design.RADIUS_XL,
                                    _hover={"border_color": Color.WARNING, "box_shadow": Design.SHADOW_MD}, transition="all 0.2s ease", cursor="pointer"
                                ),
                                # Lotes Vencendo
                                rx.box(
                                    rx.hstack(
                                        rx.box(
                                            rx.icon(tag="clock", size=24, color=Color.ERROR),
                                            bg=Color.ERROR_BG, p="3", border_radius=Design.RADIUS_MD,
                                            display="flex", align_items="center", justify_content="center"
                                        ),
                                        rx.vstack(
                                            rx.text("Lotes Vencendo", style=Typography.LABEL, color=Color.TEXT_SECONDARY),
                                            ui.text("Pr\u00f3ximos 30 dias", size="small"),
                                            spacing="0", align_items="start"
                                        ),
                                        rx.spacer(),
                                        rx.text(
                                            State.dashboard_expiring_lots,
                                            font_size=Typography.DISPLAY["font_size"], font_weight="800",
                                            color=rx.cond(State.has_expiring_lots, Color.ERROR, Color.SUCCESS),
                                            line_height="1"
                                        ),
                                        width="100%", align_items="center",
                                    ),
                                    padding=Spacing.MD, width="100%", bg=Color.SURFACE, border=f"1px solid {Color.BORDER}", border_radius=Design.RADIUS_XL,
                                    _hover={"border_color": Color.ERROR, "box_shadow": Design.SHADOW_MD}, transition="all 0.2s ease", cursor="pointer"
                                ),
                                spacing="4", width="100%", height="100%",
                            ),
                            padding=Spacing.LG, height="100%", min_height="250px"
                        ),
                        width="100%", height="100%",
                    ),
                    grid_column={"initial": "span 1", "md": "span 2"},
                ),

                # Coluna 3-4: \u00daltimos Alertas
                rx.box(
                    rx.vstack(
                        ui.heading("Alertas Recentes", level=3),
                        ui.card(
                            rx.cond(
                                State.qc_records_with_alerts.length() > 0,
                                rx.vstack(
                                    rx.foreach(
                                        State.qc_records_with_alerts[:4],
                                        lambda r: rx.hstack(
                                            rx.box(width="8px", height="8px", border_radius=Design.RADIUS_FULL, bg=Color.ERROR),
                                            rx.vstack(
                                                ui.text(r["exam_name"], size="label"),
                                                ui.text(r["date"], size="small"),
                                                spacing="0", align_items="start"
                                            ),
                                            rx.spacer(),
                                            ui.status_badge("CV: " + format_cv(r["cv"]) + "%", status="error"),
                                            width="100%", align_items="center",
                                            padding=Spacing.XS, border_radius=Design.RADIUS_MD, _hover={"bg": Color.ERROR_BG}
                                        )
                                    ),
                                    style={"gap": Spacing.SM},
                                ),
                                rx.center(
                                    rx.vstack(
                                        rx.icon(tag="sparkles", size=48, color=Color.TEXT_SECONDARY),
                                        ui.text("Tudo certo!", size="body_large", color=Color.TEXT_SECONDARY),
                                        style={"gap": Spacing.SM}, align_items="center",
                                    ),
                                    height="100%", width="100%", bg=Color.BACKGROUND, border_radius=Design.RADIUS_LG, padding=Spacing.XL
                                )
                            ),
                            height="100%", min_height="250px", padding=Spacing.LG,
                        ),
                        width="100%",
                    ),
                    grid_column={"initial": "span 1", "md": "span 2"},
                ),

                columns={"initial": "1", "sm": "2", "md": "2", "lg": "4"},
                spacing="4", width="100%",
            ),
            max_width="6xl", margin_x="auto", width="100%"
        ),

        # Tabela Recente
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.icon(tag="file_text", size=20, color=Color.TEXT_SECONDARY),
                    ui.heading("\u00daltimos Registros", level=3),
                    spacing="2", align_items="center", margin_bottom=Spacing.SM
                ),
                rx.box(
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell(rx.text("EXAME", style=Typography.CAPTION, color=Color.TEXT_SECONDARY)),
                                rx.table.column_header_cell(rx.text("DATA", style=Typography.CAPTION, color=Color.TEXT_SECONDARY)),
                                rx.table.column_header_cell(rx.text("CV%", style=Typography.CAPTION, color=Color.TEXT_SECONDARY)),
                                rx.table.column_header_cell(rx.text("STATUS", style=Typography.CAPTION, color=Color.TEXT_SECONDARY), text_align="right"),
                            )
                        ),
                        rx.table.body(
                            rx.foreach(
                                State.qc_records[:5],
                                lambda r: rx.table.row(
                                    rx.table.cell(ui.text(r["exam_name"], size="body", font_weight="500")),
                                    rx.table.cell(ui.text(r["date"], size="small")),
                                    rx.table.cell(
                                        rx.text(
                                            format_cv(r["cv"]) + "%",
                                            font_weight="700",
                                            color=rx.cond(r["cv"] <= r["cv_max_threshold"], Color.SUCCESS, Color.ERROR)
                                        )
                                    ),
                                    rx.table.cell(
                                        ui.status_badge(
                                            qc_status_label(r["status"], r["cv"], r["cv_max_threshold"]),
                                            status=qc_status_kind(r["status"], r["cv"], r["cv_max_threshold"])
                                        ),
                                        text_align="right"
                                    ),
                                )
                            )
                        ),
                        width="100%"
                    ),
                    bg=Color.SURFACE, border=f"1px solid {Color.BORDER}", border_radius=Design.RADIUS_XL, box_shadow=Design.SHADOW_SM, overflow="hidden",
                    width="100%", overflow_x="auto"
                ),
                width="100%", margin_top=Spacing.LG, max_width="6xl", margin_x="auto"
            ),
            width="100%"
        ),

        spacing="0", width="100%",
    )
