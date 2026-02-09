import reflex as rx
from ...state import State
from ...styles import Color, Design, Typography, Spacing
from ...components import ui
from .helpers import format_cv, qc_status_label, qc_status_kind


def registro_qc_tab() -> rx.Component:
    """Aba de Registro de Controle de Qualidade (Purificada)"""
    return rx.vstack(
        rx.hstack(
            rx.vstack(
                ui.heading("Registro de CQ", level=2),
                ui.text("Insira os dados diários para cálculo automático da Variação %", size="small", color=Color.TEXT_SECONDARY),
                spacing="1", align_items="start",
            ),
            rx.spacer(),
            rx.button(
                rx.icon(tag="mic", size=16),
                rx.text("Voz", font_size=Typography.SIZE_SM),
                variant="outline",
                color_scheme="green",
                size="2",
                on_click=State.open_voice_modal("registro"),
            ),
            width="100%", align_items="center", margin_bottom=Spacing.LG,
        ),

        ui.card(
            rx.vstack(
                ui.text("Dados da Amostra", size="label", color=Color.PRIMARY, style={"letter_spacing": "0.05em", "text_transform": "uppercase"}, margin_bottom=Spacing.MD),

                rx.grid(
                    ui.form_field(
                        "Nome do Exame (Obrigatório)",
                        ui.select(
                            State.unique_exam_names,
                            placeholder="Selecione o Exame",
                            value=State.qc_exam_name,
                            on_change=State.on_exam_selected,
                        ),
                        required=True
                    ),
                    ui.form_field(
                        "Data (Automatico)",
                        ui.input(type="date", value=State.qc_date, read_only=True),
                    ),
                    columns={"initial": "1", "sm": "2"},
                    spacing="4", width="100%",
                ),

                # Indicador de Referencia Ativa
                rx.cond(
                    State.has_active_reference,
                    rx.callout(
                        rx.hstack(
                            rx.icon(tag="circle-check", size=16),
                            rx.text("Referencia ativa: ", font_weight="600"),
                            rx.text(State.current_exam_reference["name"]),
                            rx.spacer(),
                            rx.text("CV% Max: <=" + format_cv(State.current_cv_max_threshold) + "%", font_size=Typography.SIZE_SM),
                            width="100%", align_items="center", flex_wrap="wrap", gap="2"
                        ),
                        icon="info", color_scheme="green", width="100%", margin_y=Spacing.SM
                    ),
                    rx.cond(
                        State.qc_exam_name != "",
                        rx.callout(
                            "Nenhuma referencia cadastrada para este exame. Usando limite padrao (10%).",
                            icon="info", color_scheme="yellow", width="100%", margin_y=Spacing.SM
                        )
                    )
                ),

                rx.divider(margin_y=Spacing.LG, opacity=0.3),

                ui.text("Resultados & Metas", size="label", color=Color.PRIMARY, style={"letter_spacing": "0.05em", "text_transform": "uppercase"}, margin_bottom=Spacing.MD),

                rx.grid(
                    ui.form_field("Medição (Obrigatório)", ui.input(placeholder="0.00", value=State.qc_value, on_change=State.update_qc_value), required=True),
                    ui.form_field("Valor Alvo (Obrigatório)", ui.input(placeholder="0.00", value=State.qc_target_value, on_change=State.update_qc_target_value), required=True),
                    ui.form_field("Desvio Padrão (Automático)", ui.input(placeholder="0.00", value=State.qc_target_sd, on_change=State.set_qc_target_sd, read_only=True)),
                    # CV% with dynamic color indicator
                    ui.form_field(
                        "Variação % (Automático)",
                        rx.box(
                            rx.hstack(
                                rx.text(
                                    format_cv(State.qc_calculated_cv) + "%",
                                    font_size=Typography.H3["font_size"], font_weight="bold",
                                    color=rx.cond(State.qc_cv_status == "OK", Color.SUCCESS, Color.ERROR)
                                ),
                                rx.icon(
                                    tag=rx.cond(State.qc_cv_status == "OK", "circle_check", "circle_x"),
                                    size=18,
                                    color=rx.cond(State.qc_cv_status == "OK", Color.SUCCESS, Color.ERROR)
                                ),
                                align_items="center", style={"gap": Spacing.SM}, height="100%",
                            ),
                            width="100%", height="44px", display="flex", align_items="center", padding_x=Spacing.MD, bg=Color.SURFACE, border_radius=Design.RADIUS_LG,
                            border=rx.cond(State.qc_cv_status == "OK", f"1px solid {Color.SUCCESS}40", f"1px solid {Color.ERROR}40")
                        ),
                    ),
                    columns={"initial": "1", "sm": "2", "md": "4"},
                    spacing="4", width="100%",
                ),

                rx.divider(margin_y=Spacing.LG, opacity=0.3),

                rx.grid(
                    ui.form_field("Equipamento (Automatico)", ui.input(placeholder="Ex: Cobas c111", value=State.qc_equipment, on_change=State.set_qc_equipment)),
                    ui.form_field("Analista Responsável (Opcional)", ui.input(placeholder="Nome do analista", value=State.qc_analyst, on_change=State.set_qc_analyst)),
                    columns={"initial": "1", "sm": "2"},
                    spacing="4", width="100%",
                ),

                rx.grid(
                    ui.button("Limpar", icon="eraser", on_click=State.clear_qc_form, variant="secondary", width="100%"),
                    ui.button("Salvar Registro", icon="save", is_loading=State.is_saving_qc, on_click=State.save_qc_record, width="100%"),
                    columns={"initial": "1", "sm": "2"},
                    spacing="4", width="100%", margin_top=Spacing.LG
                ),

                # Feedback Messages
                rx.cond(
                    State.qc_success_message != "",
                    rx.callout(State.qc_success_message, icon="circle_check", color_scheme="green", width="100%", margin_top=Spacing.MD),
                ),
                rx.cond(
                    State.qc_warning_message != "",
                    rx.callout(State.qc_warning_message, icon="triangle_alert", color_scheme="yellow", width="100%", margin_top=Spacing.MD),
                ),
                rx.cond(
                    State.qc_error_message != "",
                    rx.callout(State.qc_error_message, icon="triangle_alert", color_scheme="red", width="100%", margin_top=Spacing.MD),
                ),
                width="100%"
            ),
            width="100%"
        ),

        # Histórico Table Section
        rx.box(
            rx.vstack(
                rx.hstack(
                    ui.heading("Histórico Recente", level=3),
                    rx.spacer(),
                    rx.cond(
                        State.qc_records.length() > 0,
                        rx.button(
                            "Limpar Histórico", rx.icon(tag="trash_2", size=14),
                            on_click=State.open_clear_all_modal, variant="ghost", color_scheme="red", size="1", opacity="0.7", _hover={"opacity": "1"}
                        ),
                    ),
                    width="100%", align_items="center", margin_bottom=Spacing.MD
                ),
                rx.cond(
                    State.qc_records.length() > 0,
                    rx.box(
                        rx.table.root(
                            rx.table.header(
                                rx.table.row(
                                    rx.table.column_header_cell(rx.text("DATA", style=Typography.CAPTION, color=Color.TEXT_SECONDARY)),
                                    rx.table.column_header_cell(rx.text("EXAME", style=Typography.CAPTION, color=Color.TEXT_SECONDARY)),
                                    rx.table.column_header_cell(rx.text("VALOR", style=Typography.CAPTION, color=Color.TEXT_SECONDARY)),
                                    rx.table.column_header_cell(rx.text("CV%", style=Typography.CAPTION, color=Color.TEXT_SECONDARY)),
                                    rx.table.column_header_cell(rx.text("STATUS", style=Typography.CAPTION, color=Color.TEXT_SECONDARY)),
                                    rx.table.column_header_cell(rx.text("CALIBRAR?", style=Typography.CAPTION, color=Color.TEXT_SECONDARY)),
                                    rx.table.column_header_cell(rx.text("REF.", style=Typography.CAPTION, color=Color.TEXT_SECONDARY)),
                                    rx.table.column_header_cell(""),
                                )
                            ),
                            rx.table.body(
                                rx.foreach(
                                    State.paginated_qc_records,
                                    lambda r: rx.table.row(
                                        rx.table.cell(rx.text(r.date[:16], color=Color.TEXT_SECONDARY, font_size=Typography.H5["font_size"])),
                                        rx.table.cell(rx.text(r.exam_name, font_weight="600")),
                                        rx.table.cell(r.value.to_string()),
                                        rx.table.cell(rx.text(format_cv(r.cv) + "%", font_weight="600", color=rx.cond(r.cv <= r.cv_max_threshold, Color.SUCCESS, Color.ERROR))),
                                        rx.table.cell(
                                            ui.status_badge(
                                                qc_status_label(r.status, r.cv, r.cv_max_threshold),
                                                status=qc_status_kind(r.status, r.cv, r.cv_max_threshold)
                                            )
                                        ),
                                        rx.table.cell(
                                            rx.cond(
                                                r.needs_calibration,
                                                rx.cond(
                                                    r.post_calibration_id != "",
                                                    # Já tem pós-calibração registrada
                                                    rx.tooltip(
                                                        rx.badge("FEITO", color_scheme="blue", size="1", cursor="default"),
                                                        content="Pós-calibração já registrada"
                                                    ),
                                                    # Precisa registrar pós-calibração - botão clicável
                                                    rx.tooltip(
                                                        rx.badge(
                                                            "SIM",
                                                            color_scheme="red",
                                                            size="1",
                                                            cursor="pointer",
                                                            _hover={"opacity": "0.8", "transform": "scale(1.05)"},
                                                            on_click=lambda: State.open_post_calibration_modal(r.id)
                                                        ),
                                                        content="Clique para registrar medição pós-calibração"
                                                    )
                                                ),
                                                rx.badge("NAO", color_scheme="green", variant="outline", size="1")
                                            )
                                        ),
                                        rx.table.cell(
                                            rx.cond(
                                                r.reference_id != "",
                                                rx.tooltip(
                                                    rx.icon(tag="link", size=14, color=Color.PRIMARY),
                                                    content="Referencia vinculada"
                                                ),
                                                rx.text("-", color=Color.TEXT_SECONDARY, font_size=Typography.SIZE_SM_XS)
                                            )
                                        ),
                                        rx.table.cell(
                                            rx.tooltip(
                                                rx.button(
                                                    rx.icon(tag="trash_2", size=14, color=Color.ERROR),
                                                    on_click=lambda: State.open_delete_qc_record_modal(r.id, r.exam_name),
                                                    variant="ghost", color_scheme="red", size="1",
                                                    aria_label="Excluir registro"
                                                ),
                                                content="Excluir permanentemente"
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
                    rx.center(
                        rx.vstack(
                            rx.icon(tag="database", size=32, color=Color.TEXT_SECONDARY, opacity=0.3),
                            ui.text("Nenhum registro encontrado.", size="small", color=Color.TEXT_SECONDARY),
                            spacing="2", align_items="center"
                        ),
                        bg=Color.SURFACE, border=f"1px solid {Color.BORDER}", border_radius=Design.RADIUS_XL, padding=Spacing.XL, width="100%"
                    )
                ),
                # Pagination Controls
                rx.cond(
                    State.total_qc_pages > 1,
                    rx.hstack(
                        rx.button(
                            rx.icon(tag="chevron_left", size=16),
                            on_click=State.prev_qc_page,
                            variant="outline", size="1",
                            disabled=State.qc_page == 0,
                            aria_label="Página anterior",
                        ),
                        rx.text(
                            (State.qc_page + 1).to_string() + " / " + State.total_qc_pages.to_string(),
                            font_size=Typography.SIZE_SM, color=Color.TEXT_SECONDARY
                        ),
                        rx.button(
                            rx.icon(tag="chevron_right", size=16),
                            on_click=State.next_qc_page,
                            variant="outline", size="1",
                            disabled=State.qc_page >= State.total_qc_pages - 1,
                            aria_label="Próxima página",
                        ),
                        justify_content="center", align_items="center",
                        style={"gap": Spacing.MD}, width="100%", margin_top=Spacing.MD
                    ),
                ),
                width="100%"
            ),
            width="100%", margin_top=Spacing.XL
        ),

        width="100%", padding_bottom=Spacing.XXL
    )
