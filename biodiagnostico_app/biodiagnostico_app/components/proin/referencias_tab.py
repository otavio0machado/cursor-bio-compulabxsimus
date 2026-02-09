import reflex as rx
from ...state import State
from ...styles import Color, Design, Typography, Spacing
from ...components import ui
from .helpers import format_cv, qc_status_label, qc_status_kind


def reference_card(ref) -> rx.Component:
    """Card individual de referencia cadastrada"""
    return rx.box(
        rx.hstack(
            rx.vstack(
                rx.text(ref.name, font_weight="600", font_size=Typography.SIZE_MD),
                rx.hstack(
                    rx.badge(ref.exam_name, color_scheme="blue", size="1"),
                    rx.badge(ref.level, variant="outline", size="1"),
                    spacing="1"
                ),
                rx.text(
                    "Alvo: " + ref.target_value.to_string() + " | CV% Max: <=" + format_cv(ref.cv_max_threshold) + "%",
                    font_size=Typography.SIZE_SM_XS, color=Color.TEXT_SECONDARY
                ),
                rx.text(
                    f"Valido a partir de: {ref.valid_from}",
                    font_size=Typography.SIZE_XS, color=Color.TEXT_SECONDARY
                ),
                spacing="1", align_items="start"
            ),
            rx.spacer(),
            rx.vstack(
                rx.badge(
                    rx.cond(ref.is_active, "Ativo", "Inativo"),
                    color_scheme=rx.cond(ref.is_active, "green", "gray"),
                    size="1"
                ),
                rx.tooltip(
                    rx.button(
                        rx.icon(tag="trash_2", size=14),
                        on_click=lambda: State.open_delete_reference_modal(ref.id, ref.name),
                        variant="ghost", color_scheme="red", size="1",
                        aria_label="Excluir referência"
                    ),
                    content="Excluir permanentemente"
                ),
                spacing="2", align_items="end"
            ),
            width="100%", align_items="center"
        ),
        padding=Spacing.MD, width="100%",
        bg=Color.SURFACE, border=f"1px solid {Color.BORDER}", border_radius=Design.RADIUS_LG,
        _hover={"border_color": Color.PRIMARY, "box_shadow": Design.SHADOW_DEFAULT},
        transition="all 0.2s ease"
    )


def referencias_tab() -> rx.Component:
    """Aba de Cadastro de Valores Referenciais do CQ"""
    return rx.vstack(
        rx.hstack(
            rx.vstack(
                ui.heading("Valores Referenciais do CQ", level=2),
                ui.text("Configure valores-alvo e tolerancias de CV% por exame e periodo", size="small", color=Color.TEXT_SECONDARY),
                spacing="1", align_items="start",
            ),
            rx.spacer(),
            rx.button(
                rx.icon(tag="mic", size=16),
                rx.text("Voz", font_size=Typography.SIZE_SM),
                variant="outline",
                color_scheme="green",
                size="2",
                on_click=State.open_voice_modal("referencia"),
            ),
            width="100%", align_items="center", margin_bottom=Spacing.LG,
        ),

        rx.grid(
            # Coluna Esquerda: Formulario
            ui.card(
                rx.vstack(
                    ui.text("Nova Referencia", size="label", color=Color.PRIMARY, style={"letter_spacing": "0.05em", "text_transform": "uppercase"}, margin_bottom=Spacing.MD),

                    # Nome do Registro (dropdown dinamico + botao adicionar)
                    ui.form_field(
                        "Nome do Registro",
                        rx.vstack(
                            ui.select(
                                State.qc_registry_names,
                                placeholder="Selecione o Nome",
                                value=State.ref_name,
                                on_change=State.set_ref_name,
                            ),
                            rx.button(
                                rx.icon(tag="plus", size=14),
                                rx.text("Adicionar Nome", font_size=Typography.SIZE_SM_XS),
                                on_click=State.open_add_name_modal,
                                variant="ghost", color_scheme="blue", size="1",
                                width="100%",
                            ),
                            spacing="1", width="100%"
                        ),
                        required=True
                    ),

                    # Exame e Nivel
                    rx.grid(
                        ui.form_field(
                            "Exame",
                            rx.vstack(
                                ui.select(
                                    State.unique_exam_names,
                                    placeholder="Selecione o Exame",
                                    value=State.ref_exam_name,
                                    on_change=State.set_ref_exam_name
                                ),
                                rx.button(
                                    rx.icon(tag="plus", size=14),
                                    rx.text("Adicionar Exame", font_size=Typography.SIZE_SM_XS),
                                    on_click=State.open_add_exam_modal,
                                    variant="ghost", color_scheme="blue", size="1",
                                    width="100%",
                                ),
                                spacing="1", width="100%"
                            ),
                            required=True
                        ),
                        ui.form_field(
                            "Nivel",
                            ui.select(
                                ["Normal", "N1", "N2", "N3"],
                                value=State.ref_level,
                                on_change=State.set_ref_level
                            )
                        ),
                        columns="2", spacing="4", width="100%"
                    ),

                    # Datas de Validade
                    rx.grid(
                        ui.form_field(
                            "Valido a partir de (Automatico)",
                            ui.input(type="date", value=State.ref_valid_from, on_change=State.set_ref_valid_from),
                            required=True
                        ),
                        ui.form_field(
                            "Valido ate (opcional)",
                            ui.input(type="date", value=State.ref_valid_until, on_change=State.set_ref_valid_until)
                        ),
                        columns="2", spacing="4", width="100%"
                    ),

                    rx.divider(margin_y=Spacing.MD, opacity=0.3),

                    # Valor Alvo
                    ui.form_field(
                        "Valor-Alvo (Media de Controle)",
                        ui.input(placeholder="0.00", value=State.ref_target_value, on_change=State.set_ref_target_value),
                        required=True
                    ),

                    # Limite de CV%
                    ui.form_field(
                        "CV% Maximo Aceito (acima = calibrar)",
                        ui.input(placeholder="10.0", value=State.ref_cv_max_threshold, on_change=State.set_ref_cv_max_threshold),
                        required=True
                    ),

                    rx.divider(margin_y=Spacing.MD, opacity=0.3),

                    # Informacoes do Material
                    rx.grid(
                        ui.form_field(
                            "Lote do Controle",
                            ui.input(placeholder="LOT...", value=State.ref_lot_number, on_change=State.set_ref_lot_number)
                        ),
                        ui.form_field(
                            "Fabricante",
                            ui.input(placeholder="Ex: ControlLab", value=State.ref_manufacturer, on_change=State.set_ref_manufacturer)
                        ),
                        columns="2", spacing="4", width="100%"
                    ),

                    ui.form_field(
                        "Observacoes",
                        rx.text_area(
                            placeholder="Notas adicionais...",
                            value=State.ref_notes,
                            on_change=State.set_ref_notes,
                            width="100%", min_height="80px"
                        )
                    ),

                    # Botao Salvar
                    ui.button(
                        "Salvar Referencia", icon="save",
                        is_loading=State.is_saving_reference,
                        on_click=State.save_qc_reference,
                        width="100%", margin_top=Spacing.MD
                    ),

                    # Mensagens
                    rx.cond(
                        State.ref_success_message != "",
                        rx.callout(State.ref_success_message, icon="circle_check", color_scheme="green", width="100%", margin_top=Spacing.MD)
                    ),
                    rx.cond(
                        State.ref_error_message != "",
                        rx.callout(State.ref_error_message, icon="triangle_alert", color_scheme="red", width="100%", margin_top=Spacing.MD)
                    ),

                    spacing="3", width="100%"
                ),
                padding=Spacing.LG
            ),

            # Coluna Direita: Lista de Referencias
            rx.vstack(
                ui.heading("Referencias Cadastradas", level=3),
                ui.card(
                    rx.vstack(
                        rx.cond(
                            State.qc_reference_values.length() > 0,
                            rx.vstack(
                                rx.foreach(State.qc_reference_values, reference_card),
                                spacing="2", width="100%"
                            ),
                            rx.center(
                                rx.vstack(
                                    rx.icon(tag="settings", size=32, color=Color.TEXT_SECONDARY),
                                    ui.text("Nenhuma referencia cadastrada", size="small", color=Color.TEXT_SECONDARY),
                                    ui.text("Cadastre valores de referencia para cada exame", size="small", color=Color.TEXT_SECONDARY),
                                    spacing="2", align_items="center"
                                ),
                                padding=Spacing.XL, width="100%"
                            )
                        ),
                        spacing="2", width="100%"
                    ),
                    padding=Spacing.MD, max_height="500px", overflow_y="auto"
                ),
                # Botao para recarregar
                ui.button(
                    "Atualizar Lista", icon="refresh_cw",
                    on_click=State.load_qc_references,
                    variant="secondary", width="100%", margin_top=Spacing.SM
                ),
                width="100%", spacing="3"
            ),

            columns={"initial": "1", "lg": "2"},
            spacing="6", width="100%"
        ),
        width="100%"
    )
