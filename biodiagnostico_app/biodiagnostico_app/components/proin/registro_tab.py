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
                # Linha 1: Exame, Data, Medição, Valor Alvo
                rx.grid(
                    ui.form_field(
                        "Exame",
                        ui.select(
                            State.unique_exam_names,
                            placeholder="Selecione o Exame",
                            value=State.qc_exam_name,
                            on_change=State.on_exam_selected,
                        ),
                        required=True
                    ),
                    ui.form_field(
                        "Data",
                        ui.input(type="date", value=State.qc_date, on_change=State.set_qc_date),
                    ),
                    ui.form_field("Medição", ui.input(placeholder="0.00", value=State.qc_value, on_change=State.update_qc_value), required=True),
                    ui.form_field("Valor Alvo", ui.input(placeholder="0.00", value=State.qc_target_value, on_change=State.update_qc_target_value), required=True),
                    columns={"initial": "1", "sm": "2", "md": "4"},
                    spacing="3", width="100%",
                ),

                # Linha 2: SD, CV%, Equipamento, Analista
                rx.grid(
                    ui.form_field("Desvio Padrão", ui.input(placeholder="0.00", value=State.qc_target_sd, on_change=State.set_qc_target_sd, read_only=True)),
                    ui.form_field(
                        "Variação %",
                        rx.box(
                            rx.hstack(
                                rx.text(
                                    format_cv(State.qc_calculated_cv) + "%",
                                    font_size=Typography.H4["font_size"], font_weight="bold",
                                    color=rx.cond(State.qc_cv_status == "OK", Color.SUCCESS, Color.ERROR)
                                ),
                                rx.icon(
                                    tag=rx.cond(State.qc_cv_status == "OK", "circle_check", "circle_x"),
                                    size=16,
                                    color=rx.cond(State.qc_cv_status == "OK", Color.SUCCESS, Color.ERROR)
                                ),
                                align_items="center", style={"gap": Spacing.XS}, height="100%",
                            ),
                            width="100%", height="40px", display="flex", align_items="center", padding_x=Spacing.SM, bg=Color.SURFACE, border_radius=Design.RADIUS_LG,
                            border=rx.cond(State.qc_cv_status == "OK", f"1px solid {Color.SUCCESS}40", f"1px solid {Color.ERROR}40")
                        ),
                    ),
                    ui.form_field("Equipamento", ui.input(placeholder="Ex: Cobas c111", value=State.qc_equipment, on_change=State.set_qc_equipment)),
                    ui.form_field("Analista", ui.input(placeholder="Nome do analista", value=State.qc_analyst, on_change=State.set_qc_analyst)),
                    columns={"initial": "1", "sm": "2", "md": "4"},
                    spacing="3", width="100%",
                ),

                # Indicador de Referência (compacto)
                rx.cond(
                    State.has_active_reference,
                    rx.hstack(
                        rx.icon(tag="circle-check", size=14, color=Color.SUCCESS),
                        rx.text("Ref: ", font_weight="600", font_size=Typography.SIZE_SM, color=Color.TEXT_SECONDARY),
                        rx.text(State.current_exam_reference["name"], font_size=Typography.SIZE_SM),
                        rx.text(" | CV% Max: ≤" + format_cv(State.current_cv_max_threshold) + "%", font_size=Typography.SIZE_SM, color=Color.TEXT_SECONDARY),
                        align_items="center", gap="1", flex_wrap="wrap",
                        padding_x=Spacing.SM, padding_y=Spacing.XS,
                        bg=Color.SUCCESS_BG, border_radius=Design.RADIUS_MD, width="100%",
                    ),
                    rx.cond(
                        State.qc_exam_name != "",
                        rx.hstack(
                            rx.icon(tag="info", size=14, color=Color.WARNING),
                            rx.text("Sem referência cadastrada. Limite padrão: 10%", font_size=Typography.SIZE_SM, color=Color.TEXT_SECONDARY),
                            align_items="center", gap="1",
                            padding_x=Spacing.SM, padding_y=Spacing.XS,
                            bg=Color.WARNING_BG, border_radius=Design.RADIUS_MD, width="100%",
                        )
                    )
                ),

                # Botões de ação
                rx.hstack(
                    ui.button("Limpar", icon="eraser", on_click=State.clear_qc_form, variant="secondary"),
                    ui.button("Salvar Registro", icon="save", is_loading=State.is_saving_qc, on_click=State.save_qc_record),
                    spacing="3", width="100%", justify_content="flex-end",
                ),

                # Feedback Messages
                rx.cond(
                    State.qc_success_message != "",
                    rx.callout(State.qc_success_message, icon="circle_check", color_scheme="green", width="100%"),
                ),
                rx.cond(
                    State.qc_warning_message != "",
                    rx.callout(State.qc_warning_message, icon="triangle_alert", color_scheme="yellow", width="100%"),
                ),
                rx.cond(
                    State.qc_error_message != "",
                    rx.callout(State.qc_error_message, icon="triangle_alert", color_scheme="red", width="100%"),
                ),
                width="100%", spacing="3",
            ),
            width="100%", padding=Spacing.MD,
        ),

        # Histórico Table Section
        rx.box(
            rx.vstack(
                rx.hstack(
                    ui.heading("Histórico", level=3),
                    rx.spacer(),
                    rx.cond(
                        State.qc_records.length() > 0,
                        rx.button(
                            "Limpar Histórico", rx.icon(tag="trash_2", size=14),
                            on_click=State.open_clear_all_modal, variant="ghost", color_scheme="red", size="1", opacity="0.7", _hover={"opacity": "1"}
                        ),
                    ),
                    width="100%", align_items="center",
                ),
                # Banner de desfazer exclusão
                rx.cond(
                    State.has_undo_delete,
                    rx.hstack(
                        rx.icon(tag="undo-2", size=16, color=Color.PRIMARY),
                        rx.text("Registro excluído.", font_size=Typography.SIZE_SM, color=Color.TEXT_PRIMARY),
                        rx.button(
                            "Desfazer", size="1", variant="solid", color_scheme="green",
                            on_click=State.restore_last_deleted_qc_record,
                        ),
                        rx.button(
                            rx.icon(tag="x", size=14), size="1", variant="ghost",
                            on_click=State.dismiss_undo_delete, aria_label="Fechar",
                        ),
                        align_items="center", gap="3", width="100%",
                        padding=Spacing.SM, bg=Color.WARNING_BG,
                        border=f"1px solid {Color.WARNING}40",
                        border_radius=Design.RADIUS_MD,
                        margin_bottom=Spacing.SM,
                    ),
                ),
                # Barra de busca e filtros
                rx.hstack(
                    rx.box(
                        rx.input(
                            placeholder="Buscar exame...",
                            value=State.qc_search_term,
                            on_change=State.set_qc_search_term,
                            size="2",
                            width="100%",
                            max_width="280px",
                        ),
                        rx.icon(tag="search", size=16, color=Color.TEXT_SECONDARY,
                                position="absolute", right="10px", top="50%",
                                transform="translateY(-50%)", pointer_events="none"),
                        position="relative", flex="1", max_width="280px",
                    ),
                    rx.select(
                        ["Todos", "OK", "ALERTA", "ERRO"],
                        value=State.qc_status_filter,
                        on_change=State.set_qc_status_filter,
                        size="2", width="130px",
                    ),
                    rx.text(
                        State.paginated_qc_records.length().to_string() + " registros no dia",
                        font_size=Typography.SIZE_SM, color=Color.TEXT_SECONDARY,
                    ),
                    width="100%", align_items="center", gap="3", flex_wrap="wrap",
                    margin_bottom=Spacing.SM,
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
                                                r.cv > r.cv_max_threshold,
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
                # Navegação por dia
                rx.hstack(
                    rx.button(
                        rx.icon(tag="chevron_left", size=16),
                        on_click=State.prev_qc_day,
                        variant="outline", size="1",
                        aria_label="Dia anterior",
                    ),
                    rx.input(
                        type="date",
                        value=State.qc_history_date,
                        on_change=State.set_qc_history_date,
                        size="2",
                        width="160px",
                    ),
                    rx.button(
                        rx.icon(tag="chevron_right", size=16),
                        on_click=State.next_qc_day,
                        variant="outline", size="1",
                        aria_label="Próximo dia",
                    ),
                    justify_content="center", align_items="center",
                    style={"gap": Spacing.SM}, width="100%", margin_top=Spacing.MD
                ),
                width="100%"
            ),
            width="100%", margin_top=Spacing.XL
        ),

        width="100%", padding_bottom=Spacing.XXL
    )
