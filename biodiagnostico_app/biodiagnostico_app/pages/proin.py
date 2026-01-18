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
from ..styles import Color, Design, Typography
from ..components import ui

def tab_button(label: str, icon: str, tab_id: str) -> rx.Component:
    """Botão de aba do ProIn - Estilo Premium Padronizado"""
    is_active = State.proin_current_tab == tab_id
    
    return rx.button(
        rx.hstack(
            rx.icon(icon, size=18),
            rx.text(label, font_size="0.875rem", font_weight="500"),
            spacing="2",
            align="center",
        ),
        on_click=lambda: State.set_proin_tab(tab_id),
        bg=rx.cond(is_active, Color.PRIMARY_LIGHT, "transparent"),
        color=rx.cond(is_active, Color.DEEP, Color.TEXT_SECONDARY),
        border_radius="9999px",
        padding_x="1.25rem",
        padding_y="0.625rem",
        _hover={
            "bg": rx.cond(is_active, Color.PRIMARY_LIGHT, "#F3F4F6"),
            "color": Color.DEEP,
        },
        class_name="transition-all duration-200 border border-transparent" + 
                   rx.cond(is_active, f" border-{Color.PRIMARY}/20 shadow-sm", "")
    )

def dashboard_tab() -> rx.Component:
    """Aba Dashboard - Visão geral"""
    return rx.vstack(
        # Header
        ui.page_header(
            "Visão Geral do Laboratório",
            "Monitoramento de qualidade e pendências"
        ),
        
        # Grid de KPI Cards
        rx.grid(
            ui.stat_card(
                "Registros Hoje",
                State.dashboard_total_today,
                "clipboard-list",
                "info"
            ),
            ui.stat_card(
                "Registros do Mês",
                State.dashboard_total_month,
                "calendar",
                "success"
            ),
            ui.stat_card(
                "Taxa de Aprovação",
                State.dashboard_approval_rate.to_string() + "%",
                "circle-check",
                "success",
                "CV ≤ 5%"
            ),
            rx.cond(
                State.has_alerts,
                ui.stat_card("Alertas CV > 5%", State.dashboard_alerts_count, "triangle-alert", "error"),
                ui.stat_card("Sem Alertas", "0", "sparkles", "success")
            ),
            columns="4",
            spacing="4",
            width="100%",
            class_name="mb-8"
        ),
        
        # Grid Secundário (Pendências e Alertas)
        rx.grid(
            # Coluna 1: Pendências
            rx.vstack(
                ui.heading("Pendências & Alertas", level=3),
                ui.card(
                    rx.vstack(
                        # Manutenções
                        rx.box(
                            rx.hstack(
                                rx.box(rx.icon("wrench", size=28, color="orange"), class_name="bg-amber-100 p-3 rounded-xl"),
                                rx.vstack(
                                    ui.text("Manutenções Pendentes", size="label"),
                                    ui.text("Equipamentos aguardando revisão", size="small"),
                                    spacing="0",
                                ),
                                rx.spacer(),
                                rx.text(
                                    State.dashboard_pending_maintenances,
                                    font_size="2.5rem",
                                    font_weight="bold",
                                    color=rx.cond(State.has_pending_maintenances, Color.WARNING, Color.SUCCESS)
                                ),
                                width="100%",
                                align="center",
                            ),
                            class_name="p-6 w-full flex-1 flex items-center bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors cursor-pointer"
                        ),
                        # Lotes Vencendo
                        rx.box(
                            rx.hstack(
                                rx.box(rx.icon("clock", size=28, color="red"), class_name="bg-red-100 p-3 rounded-xl"),
                                rx.vstack(
                                    ui.text("Lotes Vencendo", size="label"),
                                    ui.text("Próximos 30 dias", size="small"),
                                    spacing="0",
                                ),
                                rx.spacer(),
                                rx.text(
                                    State.dashboard_expiring_lots,
                                    font_size="2.5rem",
                                    font_weight="bold",
                                    color=rx.cond(State.has_expiring_lots, Color.ERROR, Color.SUCCESS)
                                ),
                                width="100%",
                                align="center",
                            ),
                            class_name="p-6 w-full flex-1 flex items-center bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors cursor-pointer"
                        ),
                        spacing="4",
                        width="100%",
                        height="100%",
                    ),
                    padding="1.5rem",
                    height="100%",
                    min_height="250px"
                ),
                width="100%",
                height="100%",
            ),
            
            # Coluna 2: Últimos Alertas
            rx.vstack(
                ui.heading("Alertas Recentes", level=3),
                ui.card(
                    rx.cond(
                        State.qc_records_with_alerts.length() > 0,
                        rx.vstack(
                            rx.foreach(
                                State.qc_records_with_alerts[:4],
                                lambda r: rx.hstack(
                                    rx.box(class_name="w-2 h-2 rounded-full bg-red-500"),
                                    rx.vstack(
                                        ui.text(r["exam_name"], size="label"),
                                        ui.text(r["date"], size="small"),
                                        spacing="0",
                                    ),
                                    rx.spacer(),
                                    ui.status_badge(
                                        "CV: " + r["cv"].to_string() + "%",
                                        status="error"
                                    ),
                                    width="100%",
                                    align="center",
                                    class_name="p-2 hover:bg-red-50 rounded-lg transition-colors"
                                )
                            ),
                            spacing="1",
                        ),
                            rx.center(
                            rx.vstack(
                                rx.icon("sparkles", size=48, color="lightgray"),
                                ui.text("Tudo certo!", size="body", font_size="1.25rem", color="gray"),
                                spacing="2",
                                align="center",
                            ),
                            height="100%",
                            width="100%",
                            class_name="flex-1 bg-gray-50 rounded-xl"
                        )
                    ),
                    height="100%",
                    min_height="250px",
                    padding="1.5rem",
                    class_name="flex flex-col"
                ),
                width="100%",
            ),
            
            columns="2",
            spacing="6",
            width="100%",
        ),

        # Tabela Recente
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.icon("file-text", size=20, color=Color.TEXT_SECONDARY),
                    ui.heading("Últimos Registros", level=3),
                    spacing="2",
                    align="center",
                    class_name="mb-2"
                ),
                rx.box(
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell("Exame", class_name="text-xs text-gray-500 uppercase"),
                                rx.table.column_header_cell("Data", class_name="text-xs text-gray-500 uppercase"),
                                rx.table.column_header_cell("CV%", class_name="text-xs text-gray-500 uppercase"),
                                rx.table.column_header_cell("Status", class_name="text-xs text-gray-500 uppercase text-right"),
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
                                            r["cv"].to_string() + "%",
                                            class_name=rx.cond(r["status"] == "OK", "text-green-600 font-medium", "text-red-600 font-bold")
                                        )
                                    ),
                                    rx.table.cell(
                                        ui.status_badge(
                                            r["status"],
                                            status=rx.cond(r["status"] == "OK", "success", "error")
                                        ),
                                        align="right"
                                    ),
                                )
                            )
                        ),
                        class_name="w-full"
                    ),
                    class_name="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden"
                ),
            ),
            class_name="w-full mt-6"
        ),
        
        spacing="0",
        width="100%",
    )


def registro_qc_tab() -> rx.Component:
    """Aba de Registro de Controle de Qualidade"""
    return rx.vstack(
        ui.page_header(
            "Registro de CQ",
            "Insira os dados diários para cálculo automático do CV%"
        ),
        
        ui.card(
            rx.vstack(
                ui.text("Dados da Amostra", size="label", color=Color.PRIMARY, class_name="mb-4 uppercase tracking-wider"),
                
                rx.grid(
                    ui.form_field(
                        "Nome do Exame (Obrigatório)",
                        ui.select(
                            State.unique_exam_names,
                            placeholder="Selecione o Exame",
                            value=State.qc_exam_name,
                            on_change=State.set_qc_exam_name,
                        ),
                        required=True
                    ),
                    ui.form_field(
                        "Número do Lote (Opcional)",
                        ui.input(
                            placeholder="LOT...",
                            value=State.qc_lot_number,
                            on_change=State.set_qc_lot_number,
                        )
                    ),
                    ui.form_field(
                        "Data/Hora (Obrigatório)",
                        ui.input(
                            type="datetime-local",
                            value=State.qc_date,
                            on_change=State.set_qc_date,
                        ),
                        required=True
                    ),
                    columns="3",
                    spacing="4",
                    width="100%",
                ),
                
                rx.divider(class_name="my-6 border-gray-100"),
                
                ui.text("Resultados & Metas", size="label", color=Color.PRIMARY, class_name="mb-4 uppercase tracking-wider"),
                
                rx.grid(
                    ui.form_field(
                        "Medição (Obrigatório)",
                        ui.input(
                            placeholder="0.00",
                            value=State.qc_value,
                            on_change=State.set_qc_value,
                        ),
                        required=True
                    ),
                    ui.form_field(
                        "Valor Alvo (Obrigatório)",
                        ui.input(
                            placeholder="0.00",
                            value=State.qc_target_value,
                            on_change=State.set_qc_target_value,
                        ),
                        required=True
                    ),
                    ui.form_field(
                        "Desvio Padrão (Obrigatório)",
                        ui.input(
                            placeholder="0.00",
                            value=State.qc_target_sd,
                            on_change=State.set_qc_target_sd,
                        ),
                        required=True
                    ),
                    ui.form_field(
                        "CV% (Automático)",
                        ui.input(
                            value=State.qc_calculated_cv + "%",
                            read_only=True,
                            class_name="font-bold cursor-not-allowed",
                            style={
                                "color": "#F59E0B !important", 
                                "-webkit-text-fill-color": "#F59E0B !important", 
                                "opacity": "1 !important"
                            },
                            _disabled={
                                "color": "#F59E0B !important", 
                                "-webkit-text-fill-color": "#F59E0B !important",
                                "opacity": "1 !important"
                            },
                            _read_only={
                                "color": "#F59E0B !important", 
                                "-webkit-text-fill-color": "#F59E0B !important",
                                "opacity": "1 !important"
                            }
                        )
                    ),
                    columns="4",
                    spacing="4",
                    width="100%",
                ),
                
                rx.divider(class_name="my-6 border-gray-100"),
                
                rx.grid(
                    ui.form_field(
                        "Equipamento (Opcional)",
                        ui.input(
                            placeholder="Ex: Cobas c111",
                            value=State.qc_equipment,
                            on_change=State.set_qc_equipment,
                        )
                    ),
                    ui.form_field(
                        "Analista Responsável (Opcional)",
                        ui.input(
                            placeholder="Nome do analista",
                            value=State.qc_analyst,
                            on_change=State.set_qc_analyst,
                        )
                    ),
                    columns="2",
                    spacing="4",
                    width="100%",
                ),
                
                rx.box(
                    ui.button(
                        "Salvar Registro",
                        icon="save",
                        is_loading=State.is_saving_qc,
                        on_click=State.save_qc_record,
                        width="100%",
                        class_name="mt-6"
                    ),
                ),
                
                # Feedback Messages
                rx.cond(
                    State.qc_success_message != "",
                    rx.box(
                        rx.hstack(
                            rx.icon("circle-check", size=24, color="green"),
                            ui.text(State.qc_success_message, font_weight="500", color="green"),
                            spacing="3",
                            align="center"
                        ),
                        class_name="mt-4 bg-green-50 text-green-800 p-4 rounded-xl border border-green-100"
                    ),
                ),
                rx.cond(
                    State.qc_error_message != "",
                    rx.box(
                        rx.hstack(
                            rx.icon("circle-x", size=24, color="red"),
                            ui.text(State.qc_error_message, font_weight="500", color="red"),
                            spacing="3",
                            align="center"
                        ),
                        class_name="mt-4 bg-red-50 text-red-800 p-4 rounded-xl border border-red-100"
                    ),
                ),
            ),
            class_name="max-w-4xl mx-auto"
        ),
        
        # Histórico Table Section
        rx.box(
            rx.vstack(
                ui.heading("Histórico Recente", level=3, class_name="mb-2"),
                rx.cond(
                    State.qc_records.length() > 0,
                    rx.box(
                        rx.table.root(
                            rx.table.header(
                                rx.table.row(
                                    rx.table.column_header_cell("Data"),
                                    rx.table.column_header_cell("Exame"),
                                    rx.table.column_header_cell("Valor"),
                                    rx.table.column_header_cell("CV%"),
                                    rx.table.column_header_cell("Status"),
                                    rx.table.column_header_cell(""),
                                )
                            ),
                            rx.table.body(
                                rx.foreach(
                                    State.qc_records,
                                    lambda r: rx.table.row(
                                        rx.table.cell(r["date"][:16], class_name="text-sm text-gray-600"),
                                        rx.table.cell(r["exam_name"], font_weight="500"),
                                        rx.table.cell(r["value"]),
                                        rx.table.cell(
                                            rx.text(
                                                r["cv"].to_string() + "%",
                                                class_name=rx.cond(r["status"] == "OK", "text-green-600 font-bold", "text-red-600 font-bold")
                                            )
                                        ),
                                        rx.table.cell(
                                            ui.status_badge(
                                                r["status"],
                                                status=rx.cond(r["status"] == "OK", "success", "error")
                                            )
                                        ),
                                        rx.table.cell(
                                            rx.button(
                                                rx.icon("trash-2", size=14, color="red"),
                                                on_click=lambda: State.delete_qc_record(r["id"]),
                                                variant="ghost",
                                                color_scheme="red",
                                                size="1"
                                            ),
                                            align="right"
                                        ),
                                    )
                                )
                            ),
                        ),
                        class_name="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden"
                    ),
                    rx.center(
                        ui.text("Nenhum registro encontrado.", size="body", color="gray"),
                        class_name="bg-white rounded-xl border border-gray-100 p-4"
                    )
                ),
                width="100%"
            ),
            class_name="w-full mt-8 max-w-4xl mx-auto"
        ),
        
        width="100%",
        padding_bottom="3rem"
    )

def reagentes_tab() -> rx.Component:
    """Aba de Gestão de Reagentes"""
    return rx.vstack(
        ui.page_header(
            "Gestão de Reagentes",
            "Controle de lotes, validade e fabricantes"
        ),
        
        rx.grid(
            # Coluna Esquerda: Formulário
            ui.card(
                rx.vstack(
                    ui.text("Novo Lote", size="label", color=Color.PRIMARY, class_name="mb-2 uppercase text-xs tracking-wider"),
                    
                    ui.form_field(
                        "Nome do Reagente",
                        ui.input(value=State.reagent_name, on_change=State.set_reagent_name),
                        True
                    ),
                    ui.form_field(
                        "Lote",
                        ui.input(value=State.reagent_lot_number, on_change=State.set_reagent_lot_number),
                        True
                    ),
                    ui.form_field(
                        "Validade",
                        ui.input(type="date", value=State.reagent_expiry_date, on_change=State.set_reagent_expiry_date),
                        True
                    ),
                    rx.grid(
                        ui.form_field("Qtde.", ui.input(value=State.reagent_quantity, on_change=State.set_reagent_quantity)),
                        ui.form_field("Temp.", ui.input(value=State.reagent_storage_temp, on_change=State.set_reagent_storage_temp)),
                        columns="2",
                        spacing="2",
                        width="100%"
                    ),
                    ui.form_field("Fabricante", ui.input(value=State.reagent_manufacturer, on_change=State.set_reagent_manufacturer)),
                    
                    ui.button(
                        "Cadastrar Lote",
                        icon="plus",
                        is_loading=State.is_saving_reagent,
                        on_click=State.save_reagent_lot,
                        width="100%",
                        class_name="mt-4"
                    ),
                    
                    # Mensagens Feedback
                    rx.cond(
                        State.reagent_success_message != "",
                        ui.text(State.reagent_success_message, color="green", size="small")
                    ),
                ),
                class_name="h-fit"
            ),
            
            # Coluna Direita: Listagem e Manutenção
            rx.vstack(
                # Lista de Lotes
                ui.card(
                    rx.vstack(
                        ui.heading("Lotes Ativos", level=3, class_name="mb-2"),
                        rx.cond(
                            State.reagent_lots.length() > 0,
                            rx.vstack(
                                rx.foreach(
                                    State.reagent_lots,
                                    lambda lot: rx.hstack(
                                        rx.box(
                                            rx.icon("package", size=24, color=Color.TEXT_SECONDARY),
                                            class_name="bg-gray-50 p-2 rounded-lg"
                                        ),
                                        rx.vstack(
                                            ui.text(lot["name"], font_weight="500"),
                                            ui.text(lot["lot_number"], size="small"),
                                            spacing="0"
                                        ),
                                        rx.spacer(),
                                        ui.status_badge(lot["expiry_date"], status="warning"),
                                        rx.button("×", on_click=lambda: State.delete_reagent_lot(lot["id"]), size="1", variant="ghost", color_scheme="red"),
                                        width="100%",
                                        align="center",
                                        class_name="p-3 border border-gray-100 rounded-xl hover:bg-gray-50 transition-colors"
                                    )
                                ),
                                spacing="2"
                            ),
                            ui.text("Nenhum lote cadastrado.", size="small", color="gray")
                        ),
                    ),
                    width="100%"
                ),
                
                # Diário de Manutenção
                ui.card(
                    rx.vstack(
                        ui.heading("Diário de Manutenção", level=3, class_name="mb-2"),
                        rx.grid(
                            ui.input(placeholder="Equipamento...", value=State.maintenance_equipment, on_change=State.set_maintenance_equipment),
                            ui.select(["Preventiva", "Corretiva", "Calibração"], value=State.maintenance_type, on_change=State.set_maintenance_type),
                            columns="2",
                            spacing="2",
                            width="100%"
                        ),
                        rx.grid(
                            ui.input(type="date", value=State.maintenance_date, on_change=State.set_maintenance_date),
                            ui.input(type="date", placeholder="Próxima...", value=State.maintenance_next_date, on_change=State.set_maintenance_next_date),
                            columns="2",
                            spacing="2",
                            width="100%"
                        ),
                        ui.text_area(placeholder="Observações...", value=State.maintenance_notes, on_change=State.set_maintenance_notes),
                        ui.button("Registrar Manutenção", "wrench", on_click=State.save_maintenance_record, width="100%", variant="secondary"),
                        
                        rx.cond(State.maintenance_success_message != "", ui.text(State.maintenance_success_message, color="green", size="small")),
                    ),
                    width="100%"
                ),
                spacing="6",
                width="100%"
            ),
            columns="2",
            spacing="6",
            width="100%"
        )
    )

def relatorios_tab() -> rx.Component:
    """Aba de Relatórios - Gráfico Levey-Jennings"""
    return rx.vstack(
        ui.page_header(
            "Análise Levey-Jennings",
            "Visualização de tendências e desvios padrão"
        ),
        
        # Controls
        ui.card(
            rx.hstack(
                rx.box(
                    ui.text("Exame", size="label"),
                    ui.select(
                        State.unique_exam_names,
                        value=State.levey_jennings_exam,
                        on_change=State.set_levey_jennings_exam,
                        placeholder="Selecione...",
                    ),
                ),
                rx.box(
                    ui.text("Período", size="label"),
                    ui.select(
                        ["7", "15", "30", "60", "90"],
                        value=State.levey_jennings_period,
                        on_change=State.set_levey_jennings_period,
                    ),
                ),
                spacing="4",
                align="end",
                justify="center",
                width="100%"
            ),
            class_name="mb-6 max-w-2xl mx-auto"
        ),
        
        # Chart Area
        rx.cond(
            State.levey_jennings_data.length() > 0,
            ui.card(
                rx.vstack(
                    rx.hstack(
                        rx.badge("±1 DP", color_scheme="green", variant="solid"),
                        rx.badge("±2 DP", color_scheme="amber", variant="solid"),
                        rx.badge("±3 DP", color_scheme="red", variant="solid"),
                        spacing="2",
                        justify="end",
                        width="100%"
                    ),
                    
                    # Mock Chart Visualization
                    rx.box(
                        rx.vstack(
                            rx.box(class_name="w-full h-8 bg-red-50 border-b border-red-200"),
                            rx.box(class_name="w-full h-8 bg-amber-50 border-b border-amber-200"),
                            rx.box(class_name="w-full h-8 bg-green-50 border-b border-green-200"),
                            rx.box(class_name="w-full h-2 bg-green-200"), # Target
                            rx.box(class_name="w-full h-8 bg-green-50 border-t border-green-200"),
                            rx.box(class_name="w-full h-8 bg-amber-50 border-t border-amber-200"),
                            rx.box(class_name="w-full h-8 bg-red-50 border-t border-red-200"),
                            
                            rx.hstack(
                                rx.foreach(
                                    State.levey_jennings_data,
                                    lambda d: rx.tooltip(
                                        rx.box(
                                            class_name="w-3 h-3 rounded-full bg-blue-600 border-2 border-white shadow-sm hover:scale-150 transition-transform cursor-pointer"
                                        ),
                                        content=f"{d['date']}: {d['value']}"
                                    )
                                ),
                                justify="center",
                                align="center",
                                class_name="absolute inset-0 w-full h-full"
                            ),
                            position="relative",
                            class_name="w-full border border-gray-200 rounded-lg overflow-hidden mt-4"
                        ),
                        class_name="w-full p-4"
                    ),
                    
                    # Data Table
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell("Data"),
                                rx.table.column_header_cell("Valor"),
                                rx.table.column_header_cell("Target"),
                                rx.table.column_header_cell("CV%"),
                            )
                        ),
                        rx.table.body(
                            rx.foreach(
                                State.levey_jennings_data,
                                lambda d: rx.table.row(
                                    rx.table.cell(d["date"]),
                                    rx.table.cell(d["value"]),
                                    rx.table.cell(d["target"]),
                                    rx.table.cell(d["cv"].to_string() + "%", class_name="font-bold"),
                                )
                            )
                        ),
                        class_name="mt-6 w-full"
                    )
                ),
            ),
            rx.center(
                rx.vstack(
                    rx.text("📊", font_size="3rem"),
                    ui.text("Selecione um exame para visualizar o gráfico", color="gray"),
                    spacing="2",
                    align="center"
                ),
                class_name="bg-gray-50 rounded-2xl border-2 border-dashed border-gray-200 p-12 w-full"
            )
        ),
        
        width="100%"
    )

def importar_tab() -> rx.Component:
    """Aba de Importação de Planilhas"""
    return rx.vstack(
        ui.page_header(
            "Importação Inteligente",
            "Migre dados de planilhas Excel (xlsx/xls) automaticamente"
        ),
        
        ui.card(
            rx.vstack(
                rx.upload(
                    rx.vstack(
                        rx.cond(
                            State.excel_file_name != "",
                            rx.vstack(
                                rx.icon("check", size=48, color="green"),
                                ui.heading("Arquivo Carregado!", level=3, color="green"),
                                ui.text(State.excel_file_name, size="small"),
                                spacing="2",
                                align="center"
                            ),
                            rx.vstack(
                                rx.icon("file-spreadsheet", size=48, class_name="opacity-50"),
                                ui.text("Arraste sua planilha aqui", font_weight="600"),
                                ui.text("Suporta .xlsx e .xls", size="small"),
                                class_name="group-hover:scale-105 transition-transform",
                                spacing="2",
                                align="center"
                            )
                        ),
                        justify="center",
                        align="center",
                        class_name="h-full w-full"
                    ),
                    id="excel_upload",
                    accept={
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"],
                        "application/vnd.ms-excel": [".xls"]
                    },
                    max_files=1,
                    on_drop=State.handle_excel_upload(rx.upload_files(upload_id="excel_upload")),
                    class_name="w-full h-64 border-2 border-dashed border-gray-300 rounded-2xl bg-gray-50 hover:bg-green-50 hover:border-green-300 transition-all cursor-pointer p-8 relative"
                ),
                
                # Action Buttons
                rx.hstack(
                    ui.button(
                        "Analisar Dados",
                        "search",
                        on_click=State.analyze_excel,
                        disabled=~State.has_excel_file | State.is_analyzing_excel,
                        variant="ghost",
                        is_loading=State.is_analyzing_excel
                    ),
                    ui.button(
                        "Importar para o Sistema",
                        "upload",
                        on_click=State.import_excel_to_qc,
                        disabled=~State.excel_analyzed | State.is_analyzing_excel,
                        variant="primary"
                    ),
                    spacing="4",
                    class_name="mt-6 justify-center w-full"
                ),

                # Mensagens Feedback
                rx.cond(
                    State.excel_success_message != "",
                    rx.callout(
                        State.excel_success_message,
                        icon="circle-check",
                        color_scheme="green",
                        class_name="mt-4 max-w-2xl mx-auto"
                    )
                ),
            ),
            class_name="max-w-2xl mx-auto w-full"
        ),
        
        # Preview
        rx.cond(
            State.excel_analyzed,
            ui.card(
                ui.heading("Pré-visualização dos Dados", level=3, class_name="mb-4"),
                rx.scroll_area(
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.foreach(
                                    State.excel_headers,
                                    lambda h: rx.table.column_header_cell(h)
                                )
                            )
                        ),
                        rx.table.body(
                            rx.foreach(
                                State.excel_preview,
                                lambda row: rx.table.row(
                                    rx.foreach(row, lambda cell: rx.table.cell(cell))
                                )
                            )
                        ),
                        width="100%"
                    ),
                    type="always",
                    scrollbars="both",
                    style={"height": 400}
                ),
                class_name="mt-8"
            )
        ),
        
        width="100%",
        align="center",
        padding_bottom="2rem"
    )

def proin_page() -> rx.Component:
    """Página principal do ProIn QC"""
    
    return rx.box(
        rx.vstack(
            # Premium Header
            rx.box(
                ui.animated_heading("Controle de Qualidade", level=1),
                class_name="py-12 w-full flex justify-center"
            ),
            
            # Navigation Tabs
            rx.box(
                rx.hstack(
                    tab_button("Dashboard", "layout-dashboard", "dashboard"),
                    tab_button("Registro CQ", "file-pen-line", "registro"),
                    tab_button("Gestão de Reagentes", "flask-conical", "reagentes"),
                    tab_button("Relatórios", "chart-line", "relatorios"),
                    tab_button("Importar", "upload", "importar"),
                    spacing="2",
                    wrap="wrap",
                    justify="center",
                    class_name="p-1 bg-gray-100/50 rounded-full inline-flex border border-gray-200/50 backdrop-blur-sm"
                ),
                class_name="w-full mb-8 sticky top-0 z-10 py-4 flex justify-center"
            ),
            
            # Main Content Area
            rx.box(
                rx.match(
                    State.proin_current_tab,
                    ("dashboard", dashboard_tab()),
                    ("registro", registro_qc_tab()),
                    ("reagentes", reagentes_tab()),
                    ("relatorios", relatorios_tab()),
                    ("importar", importar_tab()),
                    dashboard_tab(),
                ),
                class_name="w-full min-h-[500px] animate-in fade-in slide-in-from-bottom-4 duration-500"
            ),
            
            width="100%",
            max_width="1280px",
            class_name="mx-auto px-6 pb-12"
        ),
        class_name="flex-1 bg-gray-50/30 w-full"
    )
