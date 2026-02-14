"""Componente genérico de CQ reutilizável para todas as áreas."""
import reflex as rx
from ...styles import Color, Design, Typography, Spacing
from ...components import ui


# Analitos padrão por área (podem ser customizados via State)
AREA_ANALITOS = {
    "imunologia": ["IgG", "IgM", "IgA", "IgE", "C3", "C4", "PCR", "ASO", "FR"],
    "parasitologia": ["EPF", "Giardia", "Entamoeba", "Cryptosporidium", "Isospora"],
    "microbiologia": ["Cultura", "Antibiograma", "TSA", "Gram", "BK"],
    "uroanalise": ["pH", "Densidade", "Proteínas", "Glicose", "Hemoglobina", "Leucócitos", "Nitrito", "Cetonas"],
}


def generic_qc_tab(
    area_id: str,
    area_label: str,
    # State vars
    state_module,
    # Params form
    param_analito_var,
    param_modo_var,
    param_alvo_var,
    param_min_var,
    param_max_var,
    param_tolerancia_var,
    param_equipamento_var,
    param_lote_var,
    param_nivel_var,
    # Measurement form
    meas_data_var,
    meas_analito_var,
    meas_valor_var,
    meas_observacao_var,
    # Tables data
    params_list_var,
    measurements_list_var,
    # Handlers
    load_params_handler,
    save_param_handler,
    load_measurements_handler,
    register_measurement_handler,
) -> rx.Component:
    """
    Tab genérica de CQ que pode ser usada para qualquer área.

    Parâmetros:
        area_id: ID da área (ex: 'imunologia')
        area_label: Label da área (ex: 'Imunologia')
        state_module: Módulo State que contém as variáveis
        param_*: Variáveis de estado para formulário de parâmetros
        meas_*: Variáveis de estado para formulário de medições
        *_list_var: Listas de dados para tabelas
        *_handler: Funções handlers para ações
    """
    analitos = AREA_ANALITOS.get(area_id, [])

    return rx.vstack(
        # Header
        rx.hstack(
            rx.icon(tag="flask", size=24, color=Color.PRIMARY),
            rx.text(
                f"Controle de Qualidade - {area_label}",
                font_size=Typography.H3["font_size"],
                font_weight="700",
                color=Color.DEEP,
            ),
            spacing="3",
            align_items="center",
        ),

        # Grid: Parâmetros | Medições
        rx.grid(
            # COLUNA 1: PARÂMETROS
            ui.card(
                rx.vstack(
                    # Header Parâmetros
                    rx.hstack(
                        rx.icon(tag="settings", size=18, color=Color.PRIMARY),
                        rx.text(
                            "Parâmetros de CQ",
                            font_size=Typography.H4["font_size"],
                            font_weight="600",
                            color=Color.DEEP,
                        ),
                        spacing="2",
                        align_items="center",
                    ),

                    # Form Parâmetros
                    rx.grid(
                        ui.form_field(
                            "Analito",
                            ui.select(
                                analitos,
                                placeholder="Selecione",
                                value=param_analito_var,
                                on_change=state_module.set_param_analito,
                            ),
                            required=True,
                        ),
                        ui.form_field(
                            "Modo",
                            ui.select(
                                ["INTERVALO", "PERCENTUAL"],
                                value=param_modo_var,
                                on_change=state_module.set_param_modo,
                            ),
                            required=True,
                        ),
                        ui.form_field(
                            "Alvo",
                            ui.input(
                                placeholder="Ex: 100",
                                value=param_alvo_var,
                                on_change=state_module.set_param_alvo,
                            ),
                            required=True,
                        ),
                        columns={"initial": "1", "sm": "3"},
                        spacing="3",
                        width="100%",
                    ),

                    # Condicional: Intervalo ou Percentual
                    rx.cond(
                        param_modo_var == "INTERVALO",
                        rx.grid(
                            ui.form_field(
                                "Mínimo",
                                ui.input(
                                    placeholder="Ex: 90",
                                    value=param_min_var,
                                    on_change=state_module.set_param_min,
                                ),
                            ),
                            ui.form_field(
                                "Máximo",
                                ui.input(
                                    placeholder="Ex: 110",
                                    value=param_max_var,
                                    on_change=state_module.set_param_max,
                                ),
                            ),
                            columns="2",
                            spacing="3",
                            width="100%",
                        ),
                        ui.form_field(
                            "Tolerância (%)",
                            ui.input(
                                placeholder="Ex: 5",
                                value=param_tolerancia_var,
                                on_change=state_module.set_param_tolerancia,
                            ),
                            max_width="200px",
                        ),
                    ),

                    # Botão Salvar Parâmetro
                    ui.button(
                        "Salvar Parâmetro",
                        icon="save",
                        on_click=save_param_handler,
                        variant="primary",
                        width="100%",
                    ),

                    spacing="4",
                    width="100%",
                ),
            ),

            # COLUNA 2: MEDIÇÕES
            ui.card(
                rx.vstack(
                    # Header Medições
                    rx.hstack(
                        rx.icon(tag="activity", size=18, color=Color.PRIMARY),
                        rx.text(
                            "Registrar Medição",
                            font_size=Typography.H4["font_size"],
                            font_weight="600",
                            color=Color.DEEP,
                        ),
                        spacing="2",
                        align_items="center",
                    ),

                    # Form Medições
                    rx.grid(
                        ui.form_field(
                            "Data",
                            rx.input(
                                type="date",
                                value=meas_data_var,
                                on_change=state_module.set_meas_data,
                            ),
                            required=True,
                        ),
                        ui.form_field(
                            "Analito",
                            ui.select(
                                analitos,
                                placeholder="Selecione",
                                value=meas_analito_var,
                                on_change=state_module.set_meas_analito,
                            ),
                            required=True,
                        ),
                        ui.form_field(
                            "Valor Medido",
                            ui.input(
                                placeholder="Ex: 105",
                                value=meas_valor_var,
                                on_change=state_module.set_meas_valor,
                            ),
                            required=True,
                        ),
                        columns={"initial": "1", "sm": "3"},
                        spacing="3",
                        width="100%",
                    ),

                    ui.form_field(
                        "Observação",
                        rx.text_area(
                            placeholder="Observações adicionais (opcional)",
                            value=meas_observacao_var,
                            on_change=state_module.set_meas_observacao,
                            rows="2",
                        ),
                    ),

                    # Botão Registrar
                    ui.button(
                        "Registrar Medição",
                        icon="check_circle",
                        on_click=register_measurement_handler,
                        variant="primary",
                        width="100%",
                    ),

                    spacing="4",
                    width="100%",
                ),
            ),

            columns={"initial": "1", "lg": "2"},
            spacing="4",
            width="100%",
        ),

        # Tabela de Medições Recentes
        ui.card(
            rx.vstack(
                rx.hstack(
                    rx.icon(tag="table", size=18, color=Color.PRIMARY),
                    rx.text(
                        "Medições Recentes",
                        font_size=Typography.H4["font_size"],
                        font_weight="600",
                        color=Color.DEEP,
                    ),
                    spacing="2",
                    align_items="center",
                ),

                rx.cond(
                    measurements_list_var.length() > 0,
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell("Data"),
                                rx.table.column_header_cell("Analito"),
                                rx.table.column_header_cell("Valor"),
                                rx.table.column_header_cell("Min"),
                                rx.table.column_header_cell("Max"),
                                rx.table.column_header_cell("Status"),
                            ),
                        ),
                        rx.table.body(
                            rx.foreach(
                                measurements_list_var,
                                lambda m: rx.table.row(
                                    rx.table.cell(m["data_medicao"]),
                                    rx.table.cell(m["analito"]),
                                    rx.table.cell(m["valor_medido"]),
                                    rx.table.cell(m["min_aplicado"]),
                                    rx.table.cell(m["max_aplicado"]),
                                    rx.table.cell(
                                        rx.badge(
                                            m["status"],
                                            color_scheme=rx.cond(
                                                m["status"] == "APROVADO",
                                                "green",
                                                "red"
                                            ),
                                        )
                                    ),
                                ),
                            ),
                        ),
                        width="100%",
                        variant="surface",
                    ),
                    ui.empty_state(
                        icon="inbox",
                        title="Nenhuma medição registrada",
                        description=f"Registre a primeira medição de {area_label}",
                    ),
                ),

                spacing="4",
                width="100%",
            ),
        ),

        spacing="5",
        width="100%",
    )
