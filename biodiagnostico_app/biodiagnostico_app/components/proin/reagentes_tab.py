import reflex as rx
from ...state import State
from ...styles import Color, Design, Typography, Spacing
from ...components import ui
from .helpers import format_cv, qc_status_label, qc_status_kind


def reagentes_tab() -> rx.Component:
    """Aba de Gestão de Reagentes"""
    return rx.vstack(
        rx.hstack(
            rx.vstack(
                ui.heading("Gestão de Reagentes", level=2),
                ui.text("Controle de lotes, validade e fabricantes", size="small", color=Color.TEXT_SECONDARY),
                spacing="1", align_items="start",
            ),
            rx.spacer(),
            rx.button(
                rx.icon(tag="mic", size=16),
                rx.text("Voz", font_size=Typography.SIZE_SM),
                variant="outline",
                color_scheme="green",
                size="2",
                on_click=State.open_voice_modal("reagente"),
            ),
            width="100%", align_items="center", margin_bottom=Spacing.LG,
        ),

        rx.grid(
            # Coluna Esquerda: Formulário
            ui.card(
                rx.vstack(
                    ui.text("Novo Lote", size="label", color=Color.PRIMARY, style={"letter_spacing": "0.05em", "text_transform": "uppercase"}, margin_bottom=Spacing.SM),

                    ui.form_field("Nome do Reagente", ui.input(value=State.reagent_name, on_change=State.set_reagent_name), True),
                    ui.form_field("Lote", ui.input(value=State.reagent_lot_number, on_change=State.set_reagent_lot_number), True),
                    ui.form_field("Validade", ui.input(type="date", value=State.reagent_expiry_date, on_change=State.set_reagent_expiry_date), True),
                    rx.grid(
                        ui.form_field("Estoque Atual", ui.input(placeholder="0", value=State.reagent_initial_stock, on_change=State.set_reagent_initial_stock)),
                        ui.form_field("Consumo p/ Dia", ui.input(placeholder="0", value=State.reagent_daily_consumption, on_change=State.set_reagent_daily_consumption)),
                        columns="2", spacing="2", width="100%"
                    ),
                    ui.form_field("Fabricante", ui.input(value=State.reagent_manufacturer, on_change=State.set_reagent_manufacturer)),

                    ui.button("Cadastrar Lote", icon="plus", is_loading=State.is_saving_reagent, on_click=State.save_reagent_lot, width="100%", margin_top=Spacing.MD),

                    # Mensagens Feedback
                    rx.cond(
                        State.reagent_success_message != "",
                        rx.callout(State.reagent_success_message, icon="circle_check", color_scheme="green", width="100%")
                    ),
                    rx.cond(
                        State.reagent_error_message != "",
                        rx.callout(State.reagent_error_message, icon="triangle_alert", color_scheme="red", width="100%")
                    ),
                ),
            ),

            # Coluna Direita: Lista de Lotes
            ui.card(
                rx.vstack(
                    rx.hstack(
                        ui.heading("Lotes Ativos", level=3),
                        rx.spacer(),
                        rx.badge(State.reagent_lots.length().to_string() + " lotes", color_scheme="blue", variant="soft"),
                        width="100%", align_items="center", margin_bottom=Spacing.MD
                    ),
                    rx.cond(
                        State.reagent_lots.length() > 0,
                        rx.vstack(
                            rx.foreach(
                                State.paginated_reagent_lots,
                                lambda lot: rx.hstack(
                                    rx.box(
                                        rx.icon(tag="package", size=20, color=Color.TEXT_SECONDARY),
                                        bg=rx.cond(lot["days_left"] <= 7, Color.ERROR_BG, rx.cond(lot["days_left"] <= 30, Color.WARNING_BG, Color.PRIMARY_LIGHT)),
                                        p="2", border_radius=Design.RADIUS_SM
                                    ),
                                    rx.vstack(
                                        ui.text(lot["name"], font_weight="500"),
                                        rx.hstack(
                                            ui.text(lot["lot_number"], size="small", color=Color.TEXT_SECONDARY),
                                            rx.text("•", color=Color.TEXT_SECONDARY, font_size=Typography.SIZE_SM_XS),
                                            ui.text(lot["manufacturer"], size="small", color=Color.TEXT_SECONDARY),
                                            spacing="1",
                                        ),
                                        spacing="0"
                                    ),
                                    rx.spacer(),
                                    rx.vstack(
                                        rx.badge(
                                            rx.cond(
                                                lot["days_left"] <= 0, "Vencido",
                                                rx.cond(lot["days_left"] <= 30, lot["days_left"].to_string() + " dias", lot["expiry_date"])
                                            ),
                                            color_scheme=rx.cond(lot["days_left"] <= 7, "red", rx.cond(lot["days_left"] <= 30, "amber", "green")),
                                            variant="solid"
                                        ),
                                        rx.cond(lot["days_left"] <= 30, rx.text(lot["expiry_date"], font_size=Typography.SIZE_2XS, color=Color.TEXT_SECONDARY, text_align="center")),
                                        # Risco de Ruptura
                                        rx.cond(
                                            lot["days_to_rupture"] != None,
                                            rx.badge(
                                                rx.cond(lot["days_to_rupture"] <= 5, "RISCO RUPTURA", f"Estoque: {lot['days_to_rupture']} dias"),
                                                color_scheme=rx.cond(lot["days_to_rupture"] <= 5, "red", "gray"),
                                                variant="outline", margin_top=Spacing.XS
                                            )
                                        ),
                                        spacing="0", align_items="center"
                                    ),
                                    rx.button(
                                        rx.icon(tag="trash_2", size=14),
                                        on_click=lambda: State.delete_reagent_lot(lot["id"]),
                                        size="1", variant="ghost", color_scheme="red",
                                        aria_label="Excluir lote"
                                    ),
                                    width="100%", align_items="center", style={"gap": Spacing.MD},
                                    padding=Spacing.MD, border_radius=Design.RADIUS_LG,
                                    border=rx.cond(lot["days_left"] <= 7, f"1px solid {Color.ERROR}40", rx.cond(lot["days_left"] <= 30, f"1px solid {Color.WARNING}40", f"1px solid {Color.BORDER}")),
                                    bg=rx.cond(lot["days_left"] <= 7, Color.ERROR_BG, rx.cond(lot["days_left"] <= 30, Color.WARNING_BG, Color.SURFACE)),
                                    _hover={"box_shadow": Design.SHADOW_MD, "border_color": Color.PRIMARY}, transition="all 0.2s ease"
                                )
                            ),
                            spacing="2"
                        ),
                        rx.center(
                            rx.vstack(
                                rx.icon(tag="package_open", size=32, color=Color.TEXT_SECONDARY),
                                ui.text("Nenhum lote cadastrado.", size="small", color=Color.TEXT_SECONDARY),
                                spacing="2", align_items="center"
                            ),
                            padding_y=Spacing.XL, width="100%"
                        )
                    ),
                    # Pagination
                    rx.cond(
                        State.total_reagent_pages > 1,
                        rx.hstack(
                            rx.button(
                                rx.icon(tag="chevron_left", size=16),
                                on_click=State.prev_reagent_page,
                                variant="outline", size="1",
                                disabled=State.reagent_page == 0,
                                aria_label="Página anterior",
                            ),
                            rx.text(
                                (State.reagent_page + 1).to_string() + " / " + State.total_reagent_pages.to_string(),
                                font_size=Typography.SIZE_SM, color=Color.TEXT_SECONDARY
                            ),
                            rx.button(
                                rx.icon(tag="chevron_right", size=16),
                                on_click=State.next_reagent_page,
                                variant="outline", size="1",
                                disabled=State.reagent_page >= State.total_reagent_pages - 1,
                                aria_label="Próxima página",
                            ),
                            justify_content="center", align_items="center",
                            style={"gap": Spacing.MD}, width="100%", margin_top=Spacing.MD
                        ),
                    ),
                ),
                width="100%"
            ),
            columns={"initial": "1", "lg": "2"},
            spacing="6", width="100%"
        ),
        width="100%", padding_bottom=Spacing.XXL
    )
