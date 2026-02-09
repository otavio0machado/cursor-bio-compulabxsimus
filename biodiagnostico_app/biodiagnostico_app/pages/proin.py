"""
ProIn QC - Sistema de Controle de Qualidade Laboratorial
Funcionalidades:
- Dashboard com estatísticas e alertas
- Registro de CQ simplificado com cálculo automático de CV%
- Gestão de Reagentes/Lotes com controle de validade
- Gráfico Levey-Jennings para auditorias
- Importação de planilhas Excel
"""
import reflex as rx
from ..state import State
from ..styles import Color, Spacing
from ..components import ui
from ..components.proin import (
    tab_button,
    dashboard_tab,
    registro_qc_tab,
    reagentes_tab,
    manutencao_tab,
    relatorios_tab,
    importar_tab,
    referencias_tab,
    post_calibration_modal,
    delete_qc_record_modal,
    clear_all_qc_modal,
    delete_reference_modal,
    add_exam_modal,
    add_name_modal,
    voice_recording_modal,
)


def proin_page() -> rx.Component:
    """Página principal do ProIn QC (Purificada)"""
    return rx.box(
        # Loading overlay
        rx.cond(
            State.is_loading_data,
            rx.center(
                rx.vstack(
                    rx.spinner(size="3", color=Color.PRIMARY),
                    ui.text("Carregando dados...", size="small", color=Color.TEXT_SECONDARY),
                    spacing="3", align_items="center"
                ),
                width="100%", padding_y=Spacing.XXL
            ),
        ),
        rx.vstack(
            rx.box(
                ui.animated_heading("ProIn QC - Gestão de Qualidade", level=1),
                padding_y=Spacing.XL, width="100%", display="flex", justify_content="center"
            ),

            # Navegação de Abas
            rx.box(
                rx.hstack(
                    tab_button("Dashboard", "layout_dashboard", "dashboard"),
                    tab_button("Registro CQ", "clipboard_list", "registro"),
                    tab_button("Referencias CQ", "settings", "referencias"),
                    tab_button("Reagentes", "beaker", "reagentes"),
                    tab_button("Manutenção", "wrench", "manutencao"),
                    tab_button("Relatórios", "bar_chart_3", "relatorios"),
                    tab_button("Importar", "upload", "importar"),
                    spacing="2", justify_content="center", width="100%", flex_wrap="wrap"
                ),
                margin_bottom=Spacing.XL, width="100%"
            ),

            # Conteúdo da Aba Ativa
            rx.box(
                rx.cond(State.proin_current_tab == "dashboard", dashboard_tab()),
                rx.cond(State.proin_current_tab == "registro", registro_qc_tab()),
                rx.cond(State.proin_current_tab == "referencias", referencias_tab()),
                rx.cond(State.proin_current_tab == "reagentes", reagentes_tab()),
                rx.cond(State.proin_current_tab == "manutencao", manutencao_tab()),
                rx.cond(State.proin_current_tab == "relatorios", relatorios_tab()),
                rx.cond(State.proin_current_tab == "importar", importar_tab()),
                width="100%", max_width="6xl", margin_x="auto"
            ),

            spacing="0", align_items="center", width="100%", padding_y=Spacing.XL, padding_x=Spacing.MD
        ),
        # Modal de Pós-Calibração
        post_calibration_modal(),
        # Modais de Confirmação de Exclusão
        delete_qc_record_modal(),
        delete_reference_modal(),
        clear_all_qc_modal(),
        # Modal de Adicionar Exame
        add_exam_modal(),
        # Modal de Adicionar Nome de Registro
        add_name_modal(),
        # Modal de Gravacao de Voz (IA)
        voice_recording_modal(),
        width="100%",
    )
