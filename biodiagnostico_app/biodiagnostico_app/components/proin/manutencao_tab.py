import reflex as rx
from ...state import State
from ...styles import Color, Design, Typography, Spacing
from ...components import ui
from .helpers import format_cv, qc_status_label, qc_status_kind


def manutencao_tab() -> rx.Component:
    """Aba de Manutenção de Equipamentos"""
    return rx.vstack(
        rx.hstack(
            rx.vstack(
                ui.heading("Manutenção de Equipamentos", level=2),
                ui.text("Registre e acompanhe manutenções preventivas, corretivas e calibrações", size="small", color=Color.TEXT_SECONDARY),
                spacing="1", align_items="start",
            ),
            rx.spacer(),
            rx.button(
                rx.icon(tag="mic", size=16),
                rx.text("Voz", font_size=Typography.SIZE_SM),
                variant="outline",
                color_scheme="green",
                size="2",
                on_click=State.open_voice_modal("manutencao"),
            ),
            width="100%", align_items="center", margin_bottom=Spacing.LG,
        ),

        rx.grid(
            # Coluna Esquerda: Formulário
            ui.card(
                rx.vstack(
                    ui.text("Novo Registro", size="label", color=Color.PRIMARY, style={"letter_spacing": "0.05em", "text_transform": "uppercase"}, margin_bottom=Spacing.SM),
                    ui.form_field("Equipamento", ui.input(placeholder="Nome do equipamento...", value=State.maintenance_equipment, on_change=State.set_maintenance_equipment), True),
                    ui.form_field("Tipo", ui.select(["Preventiva", "Corretiva", "Calibração"], value=State.maintenance_type, on_change=State.set_maintenance_type), True),
                    rx.grid(
                        ui.form_field("Data", ui.input(type="date", value=State.maintenance_date, on_change=State.set_maintenance_date)),
                        ui.form_field("Próxima Manutenção", ui.input(type="date", value=State.maintenance_next_date, on_change=State.set_maintenance_next_date)),
                        columns="2", spacing="2", width="100%"
                    ),
                    ui.form_field("Observações", ui.text_area(placeholder="Descreva o que foi feito...", value=State.maintenance_notes, on_change=State.set_maintenance_notes)),
                    ui.button("Registrar Manutenção", icon="wrench", on_click=State.save_maintenance_record, width="100%", variant="secondary", margin_top=Spacing.MD),

                    rx.cond(State.maintenance_success_message != "", rx.callout(State.maintenance_success_message, icon="circle_check", color_scheme="green", width="100%")),
                    rx.cond(State.maintenance_error_message != "", rx.callout(State.maintenance_error_message, icon="triangle_alert", color_scheme="red", width="100%")),
                ),
            ),

            # Coluna Direita: Histórico
            ui.card(
                rx.vstack(
                    rx.hstack(
                        ui.heading("Histórico de Manutenções", level=3),
                        rx.spacer(),
                        rx.badge(State.maintenance_records.length().to_string() + " registros", color_scheme="blue", variant="soft"),
                        width="100%", align_items="center", margin_bottom=Spacing.MD
                    ),
                    rx.cond(
                        State.maintenance_records.length() > 0,
                        rx.vstack(
                            rx.foreach(
                                State.paginated_maintenance_records,
                                lambda m: rx.hstack(
                                    rx.box(
                                        rx.icon(tag="wrench", size=20, color=Color.TEXT_SECONDARY),
                                        bg=Color.PRIMARY_LIGHT, p="2", border_radius=Design.RADIUS_SM
                                    ),
                                    rx.vstack(
                                        ui.text(m.equipment, font_weight="500"),
                                        rx.hstack(
                                            rx.badge(m.type, color_scheme="blue", size="1"),
                                            ui.text(m.date, size="small", color=Color.TEXT_SECONDARY),
                                            spacing="1",
                                        ),
                                        spacing="0"
                                    ),
                                    rx.spacer(),
                                    rx.cond(
                                        m.next_date != "",
                                        rx.badge("Próx: " + m.next_date, color_scheme="amber", variant="outline", size="1"),
                                    ),
                                    rx.button(
                                        rx.icon(tag="trash_2", size=14),
                                        on_click=lambda: State.delete_maintenance_record(m.id),
                                        size="1", variant="ghost", color_scheme="red",
                                        aria_label="Excluir manutenção"
                                    ),
                                    width="100%", align_items="center", style={"gap": Spacing.MD},
                                    padding=Spacing.SM, border_radius=Design.RADIUS_LG,
                                    border=f"1px solid {Color.BORDER}",
                                    _hover={"bg": Color.BACKGROUND}, transition="all 0.2s ease"
                                )
                            ),
                            spacing="2"
                        ),
                        rx.center(
                            rx.vstack(
                                rx.icon(tag="wrench", size=32, color=Color.TEXT_SECONDARY),
                                ui.text("Nenhuma manutenção registrada.", size="small", color=Color.TEXT_SECONDARY),
                                spacing="2", align_items="center"
                            ),
                            padding_y=Spacing.XL, width="100%"
                        )
                    ),
                    # Pagination
                    rx.cond(
                        State.total_maintenance_pages > 1,
                        rx.hstack(
                            rx.button(
                                rx.icon(tag="chevron_left", size=16),
                                on_click=State.prev_maintenance_page,
                                variant="outline", size="1",
                                disabled=State.maintenance_page == 0,
                                aria_label="Página anterior",
                            ),
                            rx.text(
                                (State.maintenance_page + 1).to_string() + " / " + State.total_maintenance_pages.to_string(),
                                font_size=Typography.SIZE_SM, color=Color.TEXT_SECONDARY
                            ),
                            rx.button(
                                rx.icon(tag="chevron_right", size=16),
                                on_click=State.next_maintenance_page,
                                variant="outline", size="1",
                                disabled=State.maintenance_page >= State.total_maintenance_pages - 1,
                                aria_label="Próxima página",
                            ),
                            justify_content="center", align_items="center",
                            style={"gap": Spacing.MD}, width="100%", margin_top=Spacing.MD
                        ),
                    ),
                ),
                width="100%",
            ),
            columns={"initial": "1", "lg": "2"},
            spacing="6", width="100%"
        ),
        width="100%", padding_bottom=Spacing.XXL
    )
