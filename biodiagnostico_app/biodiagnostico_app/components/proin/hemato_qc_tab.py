"""Sub-aba CQ por Intervalo/% dentro de Hematologia."""
import reflex as rx
from ...state import State
from ...styles import Color, Design, Typography, Spacing
from ...components import ui


# ── Analitos padrão de hematologia ──
_HEMATO_ANALITOS = ["RBC", "HGB", "HCT", "WBC", "PLT", "RDW", "MPV"]


def _param_form() -> rx.Component:
    """BLOCO A — Formulário de cadastro/edição de parâmetro de CQ."""
    return ui.card(
        rx.vstack(
            rx.hstack(
                rx.icon(tag="settings", size=18, color=Color.PRIMARY),
                rx.text(
                    rx.cond(State.hqc_param_edit_id != "", "Editar Parâmetro", "Novo Parâmetro"),
                    font_size=Typography.H4["font_size"],
                    font_weight="600",
                    color=Color.DEEP,
                ),
                spacing="2",
                align_items="center",
            ),

            # Linha 1: Analito, Modo, Alvo
            rx.grid(
                ui.form_field(
                    "Analito",
                    ui.select(
                        _HEMATO_ANALITOS,
                        placeholder="Selecione",
                        value=State.hqc_param_analito,
                        on_change=State.set_hqc_param_analito,
                    ),
                    required=True,
                ),
                ui.form_field(
                    "Modo",
                    ui.select(
                        ["INTERVALO", "PERCENTUAL"],
                        value=State.hqc_param_modo,
                        on_change=State.set_hqc_param_modo,
                    ),
                    required=True,
                ),
                ui.form_field(
                    "Alvo (valor de referência)",
                    ui.input(
                        placeholder="Ex: 4.50",
                        value=State.hqc_param_alvo,
                        on_change=State.set_hqc_param_alvo,
                    ),
                    required=True,
                ),
                columns={"initial": "1", "sm": "3"},
                spacing="3",
                width="100%",
            ),

            # Linha 2 condicional: INTERVALO => min/max, PERCENTUAL => tolerância
            rx.cond(
                State.hqc_param_modo == "INTERVALO",
                rx.grid(
                    ui.form_field(
                        "Mínimo",
                        ui.input(placeholder="Ex: 4.00", value=State.hqc_param_min, on_change=State.set_hqc_param_min),
                        required=True,
                    ),
                    ui.form_field(
                        "Máximo",
                        ui.input(placeholder="Ex: 5.50", value=State.hqc_param_max, on_change=State.set_hqc_param_max),
                        required=True,
                    ),
                    columns={"initial": "1", "sm": "2"},
                    spacing="3",
                    width="100%",
                ),
                rx.grid(
                    ui.form_field(
                        "Tolerância (%)",
                        ui.input(placeholder="Ex: 5", value=State.hqc_param_tolerancia, on_change=State.set_hqc_param_tolerancia),
                        required=True,
                    ),
                    columns="1",
                    spacing="3",
                    width="100%",
                    max_width="300px",
                ),
            ),

            # Linha 3: campos opcionais
            rx.grid(
                ui.form_field("Equipamento", ui.input(placeholder="Opcional", value=State.hqc_param_equipamento, on_change=State.set_hqc_param_equipamento)),
                ui.form_field("Lote Controle", ui.input(placeholder="Opcional", value=State.hqc_param_lote, on_change=State.set_hqc_param_lote)),
                ui.form_field("Nível Controle", ui.input(placeholder="Opcional", value=State.hqc_param_nivel, on_change=State.set_hqc_param_nivel)),
                columns={"initial": "1", "sm": "3"},
                spacing="3",
                width="100%",
            ),

            # Preview: Intervalo calculado + % equivalente
            rx.cond(
                State.hqc_param_alvo != "",
                rx.hstack(
                    rx.hstack(
                        rx.icon(tag="ruler", size=14, color=Color.PRIMARY),
                        rx.text("Intervalo: ", font_weight="600", font_size=Typography.SIZE_SM, color=Color.TEXT_SECONDARY),
                        rx.text(State.hqc_param_min_calc, font_size=Typography.SIZE_SM, font_weight="bold"),
                        rx.text(" — ", font_size=Typography.SIZE_SM, color=Color.TEXT_SECONDARY),
                        rx.text(State.hqc_param_max_calc, font_size=Typography.SIZE_SM, font_weight="bold"),
                        align_items="center",
                        gap="1",
                    ),
                    rx.hstack(
                        rx.icon(tag="percent", size=14, color=Color.WARNING),
                        rx.text("Tolerância: ", font_weight="600", font_size=Typography.SIZE_SM, color=Color.TEXT_SECONDARY),
                        rx.text(State.hqc_param_pct_calc + "%", font_size=Typography.SIZE_SM, font_weight="bold"),
                        align_items="center",
                        gap="1",
                    ),
                    gap="6",
                    flex_wrap="wrap",
                    padding=Spacing.SM,
                    bg=Color.SURFACE_ALT,
                    border_radius=Design.RADIUS_MD,
                    width="100%",
                ),
            ),

            # Feedback
            rx.cond(
                State.hqc_param_error != "",
                rx.callout(State.hqc_param_error, icon="triangle_alert", color_scheme="red", width="100%"),
            ),
            rx.cond(
                State.hqc_param_success != "",
                rx.callout(State.hqc_param_success, icon="circle_check", color_scheme="green", width="100%"),
            ),

            # Botões
            rx.hstack(
                ui.button("Limpar", icon="eraser", on_click=State.clear_hqc_param_form, variant="secondary"),
                ui.button(
                    rx.cond(State.hqc_param_edit_id != "", "Atualizar", "Salvar Parâmetro"),
                    icon="save",
                    is_loading=State.is_saving_hqc_param,
                    on_click=State.save_hqc_parameter,
                ),
                spacing="3",
                width="100%",
                justify_content="flex-end",
            ),

            width="100%",
            spacing="3",
        ),
        width="100%",
        padding=Spacing.MD,
    )


def _param_table() -> rx.Component:
    """Tabela de parâmetros cadastrados."""
    return rx.vstack(
        rx.hstack(
            rx.text("Parâmetros Cadastrados", font_size=Typography.H4["font_size"], font_weight="600", color=Color.DEEP),
            rx.spacer(),
            rx.hstack(
                rx.switch(
                    checked=State.hqc_show_inactive,
                    on_change=State.set_hqc_show_inactive,
                    size="1",
                ),
                rx.text("Mostrar inativos", font_size=Typography.SIZE_SM, color=Color.TEXT_SECONDARY),
                align_items="center",
                gap="2",
            ),
            width="100%",
            align_items="center",
        ),
        rx.cond(
            State.hqc_active_parameters.length() > 0,
            rx.box(
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell(rx.text("ANALITO", style=Typography.CAPTION, color=Color.TEXT_SECONDARY)),
                            rx.table.column_header_cell(rx.text("MODO", style=Typography.CAPTION, color=Color.TEXT_SECONDARY)),
                            rx.table.column_header_cell(rx.text("ALVO", style=Typography.CAPTION, color=Color.TEXT_SECONDARY)),
                            rx.table.column_header_cell(rx.text("INTERVALO", style=Typography.CAPTION, color=Color.TEXT_SECONDARY)),
                            rx.table.column_header_cell(rx.text("%", style=Typography.CAPTION, color=Color.TEXT_SECONDARY)),
                            rx.table.column_header_cell(rx.text("STATUS", style=Typography.CAPTION, color=Color.TEXT_SECONDARY)),
                            rx.table.column_header_cell(""),
                        ),
                    ),
                    rx.table.body(
                        rx.foreach(
                            State.hqc_active_parameters,
                            lambda p: rx.table.row(
                                rx.table.cell(rx.text(p.analito, font_weight="600")),
                                rx.table.cell(
                                    rx.badge(
                                        p.modo,
                                        color_scheme=rx.cond(p.modo == "INTERVALO", "blue", "purple"),
                                        size="1",
                                    )
                                ),
                                rx.table.cell(rx.text(p.alvo_valor.to_string())),
                                rx.table.cell(
                                    rx.text(
                                        p.min_calc.to_string() + " — " + p.max_calc.to_string(),
                                        font_size=Typography.SIZE_SM,
                                    )
                                ),
                                rx.table.cell(
                                    rx.text(
                                        p.percentual_equivalente.to_string() + "%",
                                        font_size=Typography.SIZE_SM,
                                        font_weight="600",
                                    )
                                ),
                                rx.table.cell(
                                    rx.cond(
                                        p.is_active,
                                        rx.badge("Ativo", color_scheme="green", size="1"),
                                        rx.badge("Inativo", color_scheme="gray", size="1"),
                                    )
                                ),
                                rx.table.cell(
                                    rx.hstack(
                                        rx.tooltip(
                                            rx.button(
                                                rx.icon(tag="pencil", size=14),
                                                on_click=lambda: State.edit_hqc_parameter(p.id),
                                                variant="ghost",
                                                size="1",
                                            ),
                                            content="Editar",
                                        ),
                                        rx.tooltip(
                                            rx.button(
                                                rx.icon(
                                                    tag=rx.cond(p.is_active, "eye_off", "eye"),
                                                    size=14,
                                                ),
                                                on_click=lambda: State.toggle_hqc_param_active(p.id),
                                                variant="ghost",
                                                size="1",
                                            ),
                                            content=rx.cond(p.is_active, "Inativar", "Ativar"),
                                        ),
                                        rx.tooltip(
                                            rx.button(
                                                rx.icon(tag="trash_2", size=14, color=Color.ERROR),
                                                on_click=lambda: State.delete_hqc_parameter(p.id),
                                                variant="ghost",
                                                color_scheme="red",
                                                size="1",
                                            ),
                                            content="Excluir",
                                        ),
                                        gap="1",
                                    ),
                                ),
                            ),
                        ),
                    ),
                    width="100%",
                ),
                bg=Color.SURFACE,
                border=f"1px solid {Color.BORDER}",
                border_radius=Design.RADIUS_XL,
                box_shadow=Design.SHADOW_SM,
                overflow="hidden",
                width="100%",
                overflow_x="auto",
            ),
            rx.center(
                rx.vstack(
                    rx.icon(tag="settings", size=32, color=Color.TEXT_SECONDARY, opacity=0.3),
                    ui.text("Nenhum parâmetro cadastrado.", size="small", color=Color.TEXT_SECONDARY),
                    spacing="2",
                    align_items="center",
                ),
                bg=Color.SURFACE,
                border=f"1px solid {Color.BORDER}",
                border_radius=Design.RADIUS_XL,
                padding=Spacing.XL,
                width="100%",
            ),
        ),
        width="100%",
        spacing="3",
    )


def _measurement_form() -> rx.Component:
    """BLOCO B — Formulário de registro de medição."""
    return ui.card(
        rx.vstack(
            rx.hstack(
                rx.icon(tag="clipboard_check", size=18, color=Color.SUCCESS),
                rx.text("Registrar Medição do CQ", font_size=Typography.H4["font_size"], font_weight="600", color=Color.DEEP),
                spacing="2",
                align_items="center",
            ),

            rx.grid(
                ui.form_field(
                    "Data da Medição",
                    ui.input(type="date", value=State.hqc_meas_data, on_change=State.set_hqc_meas_data),
                ),
                ui.form_field(
                    "Analito",
                    ui.select(
                        State.hqc_analitos_disponiveis,
                        placeholder="Selecione",
                        value=State.hqc_meas_analito,
                        on_change=State.set_hqc_meas_analito,
                    ),
                    required=True,
                ),
                ui.form_field(
                    "Valor Medido",
                    ui.input(placeholder="Ex: 4.85", value=State.hqc_meas_valor, on_change=State.set_hqc_meas_valor),
                    required=True,
                ),
                columns={"initial": "1", "sm": "3"},
                spacing="3",
                width="100%",
            ),

            rx.grid(
                ui.form_field("Equipamento", ui.input(placeholder="Opcional", value=State.hqc_meas_equipamento, on_change=State.set_hqc_meas_equipamento)),
                ui.form_field("Lote Controle", ui.input(placeholder="Opcional", value=State.hqc_meas_lote, on_change=State.set_hqc_meas_lote)),
                ui.form_field("Nível Controle", ui.input(placeholder="Opcional", value=State.hqc_meas_nivel, on_change=State.set_hqc_meas_nivel)),
                columns={"initial": "1", "sm": "3"},
                spacing="3",
                width="100%",
            ),

            ui.form_field(
                "Observação",
                ui.input(placeholder="Opcional", value=State.hqc_meas_observacao, on_change=State.set_hqc_meas_observacao),
            ),

            # Resultado imediato da última medição
            rx.cond(
                State.hqc_last_result.is_not_none(),  # type: ignore
                rx.box(
                    rx.hstack(
                        rx.icon(
                            tag=rx.cond(
                                State.hqc_meas_success != "",
                                "circle_check",
                                "circle_x",
                            ),
                            size=20,
                            color=rx.cond(State.hqc_meas_success != "", Color.SUCCESS, Color.ERROR),
                        ),
                        rx.text(
                            rx.cond(State.hqc_meas_success != "", State.hqc_meas_success, State.hqc_meas_error),
                            font_weight="700",
                            font_size=Typography.H4["font_size"],
                            color=rx.cond(State.hqc_meas_success != "", Color.SUCCESS, Color.ERROR),
                        ),
                        align_items="center",
                        gap="2",
                    ),
                    padding=Spacing.MD,
                    bg=rx.cond(State.hqc_meas_success != "", Color.SUCCESS_BG, Color.ERROR_BG),
                    border=rx.cond(
                        State.hqc_meas_success != "",
                        f"1px solid {Color.SUCCESS}40",
                        f"1px solid {Color.ERROR}40",
                    ),
                    border_radius=Design.RADIUS_MD,
                    width="100%",
                ),
            ),

            # Feedback de erro (quando não é resultado de medição)
            rx.cond(
                (State.hqc_meas_error != "") & (State.hqc_last_result.is_none()),  # type: ignore
                rx.callout(State.hqc_meas_error, icon="triangle_alert", color_scheme="red", width="100%"),
            ),

            # Botões
            rx.hstack(
                ui.button("Limpar", icon="eraser", on_click=State.clear_hqc_meas_form, variant="secondary"),
                ui.button("Registrar Medição", icon="check", is_loading=State.is_saving_hqc_meas, on_click=State.save_hqc_measurement),
                spacing="3",
                width="100%",
                justify_content="flex-end",
            ),

            width="100%",
            spacing="3",
        ),
        width="100%",
        padding=Spacing.MD,
    )


def _measurement_history() -> rx.Component:
    """BLOCO C — Histórico de medições com filtros."""
    return rx.vstack(
        rx.hstack(
            rx.text("Histórico de Medições", font_size=Typography.H4["font_size"], font_weight="600", color=Color.DEEP),
            rx.spacer(),
            rx.text(
                State.hqc_filtered_measurements.length().to_string() + " registros",
                font_size=Typography.SIZE_SM,
                color=Color.TEXT_SECONDARY,
            ),
            width="100%",
            align_items="center",
        ),

        # Filtros
        rx.hstack(
            rx.box(
                rx.input(
                    placeholder="Buscar...",
                    value=State.hqc_meas_search,
                    on_change=State.set_hqc_meas_search,
                    size="2",
                    width="100%",
                    max_width="220px",
                ),
                rx.icon(
                    tag="search",
                    size=16,
                    color=Color.TEXT_SECONDARY,
                    position="absolute",
                    right="10px",
                    top="50%",
                    transform="translateY(-50%)",
                    pointer_events="none",
                ),
                position="relative",
                flex="1",
                max_width="220px",
            ),
            rx.select(
                ["Todos", "APROVADO", "REPROVADO"],
                value=State.hqc_meas_filter_status,
                on_change=State.set_hqc_meas_filter_status,
                size="2",
                width="150px",
            ),
            rx.cond(
                State.hqc_analitos_disponiveis.length() > 0,
                rx.select(
                    State.hqc_analitos_filter_options,
                    placeholder="Analito",
                    value=State.hqc_meas_filter_analito,
                    on_change=State.set_hqc_meas_filter_analito,
                    size="2",
                    width="130px",
                ),
            ),
            width="100%",
            align_items="center",
            gap="3",
            flex_wrap="wrap",
            margin_bottom=Spacing.SM,
        ),

        # Tabela
        rx.cond(
            State.hqc_measurements.length() > 0,
            rx.box(
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell(rx.text("DATA", style=Typography.CAPTION, color=Color.TEXT_SECONDARY)),
                            rx.table.column_header_cell(rx.text("ANALITO", style=Typography.CAPTION, color=Color.TEXT_SECONDARY)),
                            rx.table.column_header_cell(rx.text("VALOR", style=Typography.CAPTION, color=Color.TEXT_SECONDARY)),
                            rx.table.column_header_cell(rx.text("MIN", style=Typography.CAPTION, color=Color.TEXT_SECONDARY)),
                            rx.table.column_header_cell(rx.text("MAX", style=Typography.CAPTION, color=Color.TEXT_SECONDARY)),
                            rx.table.column_header_cell(rx.text("MODO", style=Typography.CAPTION, color=Color.TEXT_SECONDARY)),
                            rx.table.column_header_cell(rx.text("STATUS", style=Typography.CAPTION, color=Color.TEXT_SECONDARY)),
                            rx.table.column_header_cell(""),
                        ),
                    ),
                    rx.table.body(
                        rx.foreach(
                            State.hqc_filtered_measurements,
                            lambda m: rx.table.row(
                                rx.table.cell(rx.text(m.data_medicao, color=Color.TEXT_SECONDARY, font_size=Typography.H5["font_size"])),
                                rx.table.cell(rx.text(m.analito, font_weight="600")),
                                rx.table.cell(
                                    rx.text(
                                        m.valor_medido.to_string(),
                                        font_weight="700",
                                        color=rx.cond(m.status == "APROVADO", Color.SUCCESS, Color.ERROR),
                                    )
                                ),
                                rx.table.cell(rx.text(m.min_aplicado.to_string(), font_size=Typography.SIZE_SM)),
                                rx.table.cell(rx.text(m.max_aplicado.to_string(), font_size=Typography.SIZE_SM)),
                                rx.table.cell(
                                    rx.badge(
                                        m.modo_usado,
                                        color_scheme=rx.cond(m.modo_usado == "INTERVALO", "blue", "purple"),
                                        size="1",
                                    )
                                ),
                                rx.table.cell(
                                    rx.badge(
                                        m.status,
                                        color_scheme=rx.cond(m.status == "APROVADO", "green", "red"),
                                        size="1",
                                    )
                                ),
                                rx.table.cell(
                                    rx.tooltip(
                                        rx.button(
                                            rx.icon(tag="trash_2", size=14, color=Color.ERROR),
                                            on_click=lambda: State.delete_hqc_measurement(m.id),
                                            variant="ghost",
                                            color_scheme="red",
                                            size="1",
                                        ),
                                        content="Excluir",
                                    ),
                                ),
                            ),
                        ),
                    ),
                    width="100%",
                ),
                bg=Color.SURFACE,
                border=f"1px solid {Color.BORDER}",
                border_radius=Design.RADIUS_XL,
                box_shadow=Design.SHADOW_SM,
                overflow="hidden",
                width="100%",
                overflow_x="auto",
            ),
            rx.center(
                rx.vstack(
                    rx.icon(tag="database", size=32, color=Color.TEXT_SECONDARY, opacity=0.3),
                    ui.text("Nenhuma medição encontrada.", size="small", color=Color.TEXT_SECONDARY),
                    spacing="2",
                    align_items="center",
                ),
                bg=Color.SURFACE,
                border=f"1px solid {Color.BORDER}",
                border_radius=Design.RADIUS_XL,
                padding=Spacing.XL,
                width="100%",
            ),
        ),

        width="100%",
        spacing="3",
    )


def hemato_qc_intervalo_tab() -> rx.Component:
    """Conteúdo completo da sub-aba CQ por Intervalo/% dentro de Hematologia."""
    return rx.vstack(
        # BLOCO A — Parâmetros
        _param_form(),
        _param_table(),

        # Separador visual
        rx.separator(margin_y=Spacing.MD, color=Color.BORDER),

        # BLOCO B — Registrar Medição
        _measurement_form(),

        # Separador visual
        rx.separator(margin_y=Spacing.MD, color=Color.BORDER),

        # BLOCO C — Histórico
        _measurement_history(),

        width="100%",
        spacing="4",
    )
