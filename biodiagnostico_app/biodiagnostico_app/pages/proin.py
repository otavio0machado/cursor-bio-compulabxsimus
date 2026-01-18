"""
ProIn QC - Sistema de Controle de Qualidade Laboratorial
Funcionalidades:
- Dashboard com estatísticas e alertas
- Registro de CQ simplificado com cálculo automático de CV%
- Gestão de Reagentes/Lotes com controle de validade
- Gráfico Levey-Jennings para auditorias
- Importação de planilhas Excel

Design Premium SaaS - Clean & Clinical
"""
import reflex as rx
from ..state import State


def tab_button(label: str, icon: str, tab_id: str) -> rx.Component:
    """Botão de aba do ProIn - Premium Style"""
    return rx.box(
        rx.hstack(
            rx.text(icon, class_name="text-lg"),
            rx.text(label, class_name="text-sm font-medium hidden lg:inline"),
            spacing="2",
            align="center",
        ),
        on_click=lambda: State.set_proin_tab(tab_id),
        class_name=rx.cond(
            State.proin_current_tab == tab_id,
            "px-5 py-3 bg-[#1B5E20] text-white rounded-xl cursor-pointer transition-all shadow-md shadow-green-900/10 transform scale-[1.02]",
            "px-5 py-3 bg-white text-gray-600 border border-gray-100 rounded-xl cursor-pointer hover:bg-gray-50 hover:text-[#1B5E20] transition-all"
        ),
    )


def alert_card_static(icon: str, title: str, value, color: str, subtitle: str = "") -> rx.Component:
    """Card de alerta/estatística com design premium"""
    # Color mappings for semantic consistency
    colors = {
        "green": ("bg-emerald-50/50", "text-emerald-700", "border-emerald-100", "bg-emerald-100"),
        "red": ("bg-rose-50/50", "text-rose-700", "border-rose-100", "bg-rose-100"),
        "amber": ("bg-amber-50/50", "text-amber-700", "border-amber-100", "bg-amber-100"),
        "blue": ("bg-blue-50/50", "text-blue-700", "border-blue-100", "bg-blue-100")
    }
    
    bg, text_color, border, icon_bg = colors.get(color, colors["blue"])

    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.box(
                    rx.text(icon, class_name="text-xl"),
                    class_name=f"w-10 h-10 rounded-lg {icon_bg} flex items-center justify-center"
                ),
                rx.spacer(),
                rx.cond(
                    subtitle != "",
                    rx.badge(subtitle, variant="soft", color_scheme=color if color != "amber" else "orange"),
                ),
                width="100%",
                align="center",
            ),
            rx.text(value, class_name=f"text-3xl font-bold {text_color} mt-2 font-['Poppins']"),
            rx.text(title, class_name="text-sm font-medium text-gray-500"),
            spacing="1",
            align="start",
            width="100%"
        ),
        class_name=f"p-5 rounded-2xl border {border} {bg} hover:shadow-lg transition-all duration-300 flex-1 min-w-[200px]"
    )


def alert_card_dynamic(icon: str, title: str, value, condition, color_true: str, color_false: str, subtitle: str = "") -> rx.Component:
    """Card de alerta/estatística com cor dinâmica baseada em condição"""
    return rx.cond(
        condition,
        alert_card_static(icon, title, value, color_true, subtitle),
        alert_card_static(icon, title, value, color_false, subtitle)
    )


def dashboard_tab() -> rx.Component:
    """Aba Dashboard - Visão geral Premium"""
    return rx.vstack(
        # Header do Dashboard
        rx.hstack(
            rx.box(
                rx.text("📊", class_name="text-2xl"),
                class_name="w-12 h-12 rounded-xl bg-green-50 flex items-center justify-center"
            ),
            rx.vstack(
                rx.text("Visão Geral do Laboratório", class_name="text-2xl font-bold text-[#1B5E20]"),
                rx.text("Monitoramento em tempo real dos indicadores de qualidade", class_name="text-gray-500 text-sm"),
                spacing="0",
                align="start",
            ),
            spacing="3",
            align="center",
            class_name="mb-6 w-full"
        ),
        
        # Grid de KPI Cards
        rx.grid(
            alert_card_static(
                "📋",
                "Registros Hoje",
                State.dashboard_total_today,
                "blue"
            ),
            alert_card_static(
                "📆",
                "Registros do Mês",
                State.dashboard_total_month,
                "green"
            ),
            alert_card_static(
                "✅",
                "Taxa de Aprovação",
                State.dashboard_approval_rate.to_string() + "%",
                "green",
                "CV ≤ 5%"
            ),
            alert_card_dynamic(
                "⚠️",
                "Alertas CV > 5%",
                State.dashboard_alerts_count,
                State.has_alerts,
                "red",
                "green"
            ),
            columns="1 md:grid-cols-2 lg:grid-cols-4",
            spacing="4",
            width="100%",
            class_name="mb-6"
        ),
        
        # Grid Secundário
        rx.grid(
            alert_card_dynamic(
                "🔧",
                "Manutenções Pendentes",
                State.dashboard_pending_maintenances,
                State.has_pending_maintenances,
                "amber",
                "green"
            ),
            alert_card_dynamic(
                "⏰",
                "Lotes Vencendo",
                State.dashboard_expiring_lots,
                State.has_expiring_lots,
                "red",
                "green",
                "Próximos 30 dias"
            ),
            columns="1 md:grid-cols-2",
            spacing="4",
            width="100%",
        ),
        
        # Alertas Ativos
        rx.cond(
            State.qc_records_with_alerts.length() > 0,
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.icon("siren", class_name="text-red-600"),
                        rx.text("Alertas Críticos de Controle de Qualidade", class_name="font-bold text-red-800"),
                        spacing="2",
                        align="center",
                        class_name="mb-2"
                    ),
                    rx.foreach(
                        State.qc_records_with_alerts[:5],
                        lambda r: rx.box(
                            rx.hstack(
                                rx.vstack(
                                    rx.text(r["exam_name"], class_name="font-bold text-gray-800"),
                                    rx.text(r["date"], class_name="text-xs text-gray-500"),
                                    spacing="0",
                                ),
                                rx.spacer(),
                                rx.badge(
                                    "CV: " + r["cv"].to_string() + "%",
                                    class_name="bg-red-100 text-red-700 px-3 py-1 text-sm font-bold"
                                ),
                                width="100%",
                                align="center",
                            ),
                            class_name="bg-white p-3 rounded-lg border-l-4 border-red-500 shadow-sm"
                        )
                    ),
                    spacing="2",
                    width="100%",
                ),
                class_name="bg-red-50 border border-red-100 rounded-2xl p-5 w-full mt-4"
            ),
        ),
        
        # Últimos registros
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.icon("clipboard-list", size=20, class_name="text-[#1B5E20]"),
                    rx.text("Últimos Registros de CQ", class_name="font-bold text-[#1B5E20] text-lg"),
                    rx.spacer(),
                    rx.button("Ver Todos", variant="ghost", size="1", class_name="text-green-600"),
                    width="100%",
                    align="center",
                    class_name="mb-2"
                ),
                rx.cond(
                    State.qc_records.length() > 0,
                    rx.box(
                        rx.foreach(
                            State.qc_records[:5],
                            lambda r: rx.box(
                                rx.hstack(
                                    rx.vstack(
                                        rx.text(r["exam_name"], class_name="font-semibold text-gray-800"),
                                        rx.text(r["date"], class_name="text-xs text-gray-400"),
                                        spacing="0",
                                        align="start",
                                    ),
                                    rx.spacer(),
                                    rx.vstack(
                                        rx.text(
                                            "CV: " + r["cv"].to_string() + "%",
                                            class_name="font-bold text-sm"
                                        ),
                                        rx.badge(
                                            r["status"],
                                            class_name=rx.cond(
                                                r["status"] == "OK",
                                                "bg-green-100 text-green-700",
                                                "bg-red-100 text-red-700"
                                            )
                                        ),
                                        spacing="1",
                                        align="end",
                                    ),
                                    width="100%",
                                ),
                                class_name="p-4 border-b border-gray-50 hover:bg-gray-50 transition-colors last:border-0"
                            )
                        ),
                        class_name="w-full bg-white rounded-xl divide-y divide-gray-50"
                    ),
                    rx.text("Nenhum registro encontrado", class_name="text-gray-400 py-8 text-center bg-white rounded-xl")
                ),
                spacing="3",
                width="100%",
            ),
            class_name="bg-white border border-gray-100 rounded-2xl p-6 w-full shadow-sm mt-4"
        ),
        
        spacing="0",
        width="100%",
    )


def registro_qc_tab() -> rx.Component:
    """Aba de Registro de Controle de Qualidade - Form Style"""
    return rx.vstack(
        # Header
        rx.hstack(
            rx.box(
                rx.text("📝", class_name="text-2xl"),
                class_name="w-12 h-12 rounded-xl bg-green-50 flex items-center justify-center"
            ),
            rx.vstack(
                rx.text("Novo Registro de CQ", class_name="text-2xl font-bold text-[#1B5E20]"),
                rx.text("Preencha os dados das medições para cálculo automático do CV%", class_name="text-gray-500 text-sm"),
                spacing="0",
                align="start",
            ),
            spacing="3",
            align="center",
            class_name="mb-6 w-full"
        ),
        
        # Formulário
        rx.box(
            rx.vstack(
                rx.text("Dados do Exame e Amostra", class_name="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2"),
                rx.grid(
                    # Exame
                    rx.box(
                        rx.vstack(
                            rx.text("Nome do Exame *", class_name="text-sm font-medium text-gray-700"),
                            rx.input(
                                placeholder="Ex: Glicose, Hemoglobina...",
                                value=State.qc_exam_name,
                                on_change=State.set_qc_exam_name,
                                class_name="w-full rounded-xl bg-gray-50 border-gray-200 focus:bg-white transition-all"
                            ),
                            spacing="1",
                            width="100%",
                        )
                    ),
                    # Nível
                    rx.box(
                        rx.vstack(
                            rx.text("Nível de Controle", class_name="text-sm font-medium text-gray-700"),
                            rx.select(
                                ["Normal", "Patológico"],
                                value=State.qc_level,
                                on_change=State.set_qc_level,
                                class_name="w-full rounded-xl bg-gray-50 border-gray-200 focus:bg-white transition-all"
                            ),
                            spacing="1",
                            width="100%",
                        )
                    ),
                    # Lote
                    rx.box(
                        rx.vstack(
                            rx.text("Número do Lote", class_name="text-sm font-medium text-gray-700"),
                            rx.input(
                                placeholder="Ex: LOT123456",
                                value=State.qc_lot_number,
                                on_change=State.set_qc_lot_number,
                                class_name="w-full rounded-xl bg-gray-50 border-gray-200 focus:bg-white transition-all"
                            ),
                            spacing="1",
                            width="100%",
                        )
                    ),
                    # Data
                    rx.box(
                        rx.vstack(
                            rx.text("Data/Hora", class_name="text-sm font-medium text-gray-700"),
                            rx.input(
                                type="datetime-local",
                                value=State.qc_date,
                                on_change=State.set_qc_date,
                                class_name="w-full rounded-xl bg-gray-50 border-gray-200 focus:bg-white transition-all"
                            ),
                            spacing="1",
                            width="100%",
                        )
                    ),
                    columns="1 md:grid-cols-2",
                    spacing="4",
                    width="100%",
                ),
                
                rx.divider(class_name="my-6 border-gray-100"),
                
                rx.text("Valores de Medição e Referência", class_name="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2"),
                rx.grid(
                    # Valor 1
                    rx.box(
                        rx.vstack(
                            rx.text("Medição 1 *", class_name="text-sm font-medium text-gray-700"),
                            rx.input(
                                placeholder="0.00",
                                value=State.qc_value1,
                                on_change=State.set_qc_value1,
                                class_name="w-full rounded-xl bg-gray-50 border-gray-200 focus:bg-white transition-all text-lg font-mono"
                            ),
                            spacing="1",
                            width="100%",
                        )
                    ),
                    # Valor 2
                    rx.box(
                        rx.vstack(
                            rx.text("Medição 2 *", class_name="text-sm font-medium text-gray-700"),
                            rx.input(
                                placeholder="0.00",
                                value=State.qc_value2,
                                on_change=State.set_qc_value2,
                                class_name="w-full rounded-xl bg-gray-50 border-gray-200 focus:bg-white transition-all text-lg font-mono"
                            ),
                            spacing="1",
                            width="100%",
                        )
                    ),
                    # Valor Alvo
                    rx.box(
                        rx.vstack(
                            rx.text("Valor Alvo (Bula)", class_name="text-sm font-medium text-gray-700"),
                            rx.input(
                                placeholder="0.00",
                                value=State.qc_target_value,
                                on_change=State.set_qc_target_value,
                                class_name="w-full rounded-xl bg-gray-50 border-gray-200 focus:bg-white transition-all text-lg font-mono"
                            ),
                            spacing="1",
                            width="100%",
                        )
                    ),
                    # DP Alvo
                    rx.box(
                        rx.vstack(
                            rx.text("DP Alvo (Bula)", class_name="text-sm font-medium text-gray-700"),
                            rx.input(
                                placeholder="0.00",
                                value=State.qc_target_sd,
                                on_change=State.set_qc_target_sd,
                                class_name="w-full rounded-xl bg-gray-50 border-gray-200 focus:bg-white transition-all text-lg font-mono"
                            ),
                            spacing="1",
                            width="100%",
                        )
                    ),
                    columns="2 md:grid-cols-4",
                    spacing="4",
                    width="100%",
                ),
                
                rx.divider(class_name="my-6 border-gray-100"),

                rx.grid(
                    # Equipamento
                    rx.box(
                        rx.vstack(
                            rx.text("Equipamento", class_name="text-sm font-medium text-gray-700"),
                            rx.input(
                                placeholder="Ex: Analisador Bioquímico",
                                value=State.qc_equipment,
                                on_change=State.set_qc_equipment,
                                class_name="w-full rounded-xl bg-gray-50 border-gray-200 focus:bg-white transition-all"
                            ),
                            spacing="1",
                            width="100%",
                        )
                    ),
                    # Analista
                    rx.box(
                        rx.vstack(
                            rx.text("Analista Responsável", class_name="text-sm font-medium text-gray-700"),
                            rx.input(
                                placeholder="Seu nome",
                                value=State.qc_analyst,
                                on_change=State.set_qc_analyst,
                                class_name="w-full rounded-xl bg-gray-50 border-gray-200 focus:bg-white transition-all"
                            ),
                            spacing="1",
                            width="100%",
                        )
                    ),
                    columns="1 md:grid-cols-2",
                    spacing="4",
                    width="100%",
                ),
                
                # Botão salvar
                rx.button(
                    rx.cond(
                        State.is_saving_qc,
                        rx.hstack(rx.spinner(size="2", color="white"), rx.text("Processando..."), spacing="2"),
                        rx.hstack(rx.icon("save", size=18), rx.text("Salvar Registro de CQ"), spacing="2"),
                    ),
                    on_click=State.save_qc_record,
                    disabled=State.is_saving_qc,
                    class_name="bg-[#1B5E20] text-white px-8 py-3.5 rounded-xl font-semibold hover:bg-[#2E7D32] shadow-lg shadow-green-900/10 hover:shadow-xl hover:-translate-y-0.5 transition-all w-full mt-6"
                ),
                
                # Mensagens
                rx.cond(
                    State.qc_success_message != "",
                    rx.box(
                        rx.hstack(
                            rx.icon("check-circle-2", class_name="text-green-600"),
                            rx.text(State.qc_success_message, class_name="text-green-700 font-medium"),
                            spacing="2",
                            align="center"
                        ),
                        class_name="bg-green-50 border border-green-200 rounded-xl p-4 w-full mt-4"
                    ),
                ),
                rx.cond(
                    State.qc_error_message != "",
                    rx.box(
                        rx.hstack(
                            rx.icon("alert-circle", class_name="text-red-600"),
                            rx.text(State.qc_error_message, class_name="text-red-700 font-medium"),
                            spacing="2",
                            align="center"
                        ),
                        class_name="bg-red-50 border border-red-200 rounded-xl p-4 w-full mt-4"
                    ),
                ),
                
                spacing="4",
                width="100%",
            ),
            class_name="bg-white border border-gray-100 rounded-3xl p-8 w-full shadow-sm"
        ),
        
        # Histórico de registros
        rx.box(
            rx.vstack(
                rx.text("Histórico Recente", class_name="font-bold text-[#1B5E20] text-lg"),
                rx.cond(
                    State.qc_records.length() > 0,
                    rx.box(
                        rx.table.root(
                            rx.table.header(
                                rx.table.row(
                                    rx.table.column_header_cell("Data", class_name="bg-gray-50 text-gray-600 font-semibold py-3"),
                                    rx.table.column_header_cell("Exame", class_name="bg-gray-50 text-gray-600 font-semibold py-3"),
                                    rx.table.column_header_cell("Média", class_name="bg-gray-50 text-gray-600 font-semibold py-3"),
                                    rx.table.column_header_cell("CV%", class_name="bg-gray-50 text-gray-600 font-semibold py-3"),
                                    rx.table.column_header_cell("Status", class_name="bg-gray-50 text-gray-600 font-semibold py-3"),
                                    rx.table.column_header_cell("Ações", class_name="bg-gray-50 text-gray-600 font-semibold py-3"),
                                )
                            ),
                            rx.table.body(
                                rx.foreach(
                                    State.qc_records,
                                    lambda r: rx.table.row(
                                        rx.table.cell(r["date"][:16], class_name="text-sm"),
                                        rx.table.cell(r["exam_name"], class_name="font-medium text-gray-900"),
                                        rx.table.cell(r["mean"], class_name="font-mono text-xs"),
                                        rx.table.cell(
                                            rx.text(
                                                r["cv"].to_string() + "%",
                                                class_name=rx.cond(
                                                    r["status"] == "OK",
                                                    "text-green-600 font-bold text-xs",
                                                    "text-red-600 font-bold text-xs"
                                                )
                                            )
                                        ),
                                        rx.table.cell(
                                            rx.badge(
                                                r["status"],
                                                variant="soft",
                                                color_scheme=rx.cond(r["status"] == "OK", "green", "red")
                                            )
                                        ),
                                        rx.table.cell(
                                            rx.button(
                                                rx.icon("trash-2", size=14),
                                                on_click=lambda rid=r["id"]: State.delete_qc_record(rid),
                                                class_name="bg-red-50 text-red-600 p-2 rounded-lg hover:bg-red-100 transition-colors",
                                                size="1",
                                                variant="ghost"
                                            )
                                        ),
                                    )
                                )
                            ),
                            width="100%",
                        ),
                        class_name="w-full overflow-x-auto rounded-xl border border-gray-100"
                    ),
                    rx.text("Nenhum registro cadastrado", class_name="text-gray-400 py-8 text-center italic")
                ),
                spacing="3",
                width="100%",
            ),
            class_name="bg-white border border-gray-100 rounded-3xl p-6 w-full shadow-sm mt-6"
        ),
        
        spacing="4",
        width="100%",
    )


def reagentes_tab() -> rx.Component:
    """Aba de Gestão de Reagentes - Clean Design"""
    return rx.vstack(
        rx.hstack(
            rx.box(
                rx.text("🧪", class_name="text-2xl"),
                class_name="w-12 h-12 rounded-xl bg-purple-50 flex items-center justify-center"
            ),
            rx.vstack(
                rx.text("Gestão de Insumos", class_name="text-2xl font-bold text-[#1B5E20]"),
                rx.text("Controle de validade e estoque de reagentes e lotes", class_name="text-gray-500 text-sm"),
                spacing="0",
                align="start",
            ),
            spacing="3",
            align="center",
            class_name="mb-6 w-full"
        ),
        
        # Formulário de cadastro
        rx.box(
            rx.vstack(
                rx.text("Cadastrar Novo Lote", class_name="font-bold text-[#1B5E20] text-lg mb-2"),
                rx.grid(
                    rx.box(
                        rx.vstack(
                            rx.text("Nome do Reagente *", class_name="text-sm font-medium text-gray-700"),
                            rx.input(
                                placeholder="Ex: Controle Glicose Nível I",
                                value=State.reagent_name,
                                on_change=State.set_reagent_name,
                                class_name="w-full rounded-xl bg-gray-50 border-gray-200 focus:bg-white"
                            ),
                            spacing="1",
                            width="100%",
                        )
                    ),
                    rx.box(
                        rx.vstack(
                            rx.text("Número do Lote *", class_name="text-sm font-medium text-gray-700"),
                            rx.input(
                                placeholder="Ex: LOT2024001",
                                value=State.reagent_lot_number,
                                on_change=State.set_reagent_lot_number,
                                class_name="w-full rounded-xl bg-gray-50 border-gray-200 focus:bg-white"
                            ),
                            spacing="1",
                            width="100%",
                        )
                    ),
                    rx.box(
                        rx.vstack(
                            rx.text("Data de Validade *", class_name="text-sm font-medium text-gray-700"),
                            rx.input(
                                type="date",
                                value=State.reagent_expiry_date,
                                on_change=State.set_reagent_expiry_date,
                                class_name="w-full rounded-xl bg-gray-50 border-gray-200 focus:bg-white"
                            ),
                            spacing="1",
                            width="100%",
                        )
                    ),
                    rx.box(
                        rx.vstack(
                            rx.text("Quantidade", class_name="text-sm font-medium text-gray-700"),
                            rx.input(
                                placeholder="Ex: 10 frascos",
                                value=State.reagent_quantity,
                                on_change=State.set_reagent_quantity,
                                class_name="w-full rounded-xl bg-gray-50 border-gray-200 focus:bg-white"
                            ),
                            spacing="1",
                            width="100%",
                        )
                    ),
                    rx.box(
                        rx.vstack(
                            rx.text("Fabricante", class_name="text-sm font-medium text-gray-700"),
                            rx.input(
                                placeholder="Ex: Labtest",
                                value=State.reagent_manufacturer,
                                on_change=State.set_reagent_manufacturer,
                                class_name="w-full rounded-xl bg-gray-50 border-gray-200 focus:bg-white"
                            ),
                            spacing="1",
                            width="100%",
                        )
                    ),
                    rx.box(
                        rx.vstack(
                            rx.text("Temp. Armazenamento", class_name="text-sm font-medium text-gray-700"),
                            rx.input(
                                placeholder="Ex: 2-8°C",
                                value=State.reagent_storage_temp,
                                on_change=State.set_reagent_storage_temp,
                                class_name="w-full rounded-xl bg-gray-50 border-gray-200 focus:bg-white"
                            ),
                            spacing="1",
                            width="100%",
                        )
                    ),
                    columns="1 md:grid-cols-2 lg:grid-cols-3",
                    spacing="4",
                    width="100%",
                ),
                rx.button(
                    rx.cond(
                        State.is_saving_reagent,
                        rx.hstack(rx.spinner(size="2", color="white"), rx.text("Salvando..."), spacing="2"),
                        rx.hstack(rx.icon("save", size=18), rx.text("Cadastrar Lote"), spacing="2"),
                    ),
                    on_click=State.save_reagent_lot,
                    disabled=State.is_saving_reagent,
                    class_name="bg-[#1B5E20] text-white px-8 py-3 rounded-xl font-semibold hover:bg-[#2E7D32] transition-all mt-4 w-full md:w-auto"
                ),
                rx.cond(
                    State.reagent_success_message != "",
                    rx.box(
                        rx.text(f"✅ {State.reagent_success_message}", class_name="text-green-700 font-medium"),
                        class_name="bg-green-50 border border-green-200 rounded-xl p-3 w-full"
                    ),
                ),
                rx.cond(
                    State.reagent_error_message != "",
                    rx.box(
                        rx.text(f"❌ {State.reagent_error_message}", class_name="text-red-700 font-medium"),
                        class_name="bg-red-50 border border-red-200 rounded-xl p-3 w-full"
                    ),
                ),
                spacing="3",
                width="100%",
            ),
            class_name="bg-white border border-gray-100 rounded-3xl p-8 w-full shadow-sm"
        ),
        
        # Lista de lotes - Cards
        rx.box(
            rx.vstack(
                rx.text("📦 Lotes em Estoque", class_name="font-bold text-[#1B5E20] text-lg"),
                rx.cond(
                    State.reagent_lots.length() > 0,
                    rx.grid(
                        rx.foreach(
                            State.reagent_lots,
                            lambda lot: rx.box(
                                rx.vstack(
                                    rx.hstack(
                                        rx.box(rx.text("🧪", class_name="text-xl"), class_name="w-8 h-8 rounded bg-gray-100 flex items-center justify-center"),
                                        rx.vstack(
                                            rx.text(lot["name"], class_name="font-bold text-gray-800 text-sm line-clamp-1"),
                                            rx.text(lot["manufacturer"], class_name="text-xs text-gray-500"),
                                            spacing="0",
                                            align="start",
                                            width="100%"
                                        ),
                                        width="100%",
                                        align="start"
                                    ),
                                    rx.divider(class_name="my-2 border-gray-100"),
                                    rx.hstack(
                                        rx.vstack(
                                            rx.text("LOTE", class_name="text-[10px] font-bold text-gray-400"),
                                            rx.text(lot["lot_number"], class_name="text-xs font-mono font-medium"),
                                            spacing="0"
                                        ),
                                        rx.spacer(),
                                        rx.vstack(
                                            rx.text("VALIDADE", class_name="text-[10px] font-bold text-gray-400"),
                                            rx.text(lot["expiry_date"], class_name="text-xs font-mono font-medium"),
                                            spacing="0",
                                            align="end"
                                        ),
                                        width="100%"
                                    ),
                                    rx.button(
                                        "Remover",
                                        on_click=lambda lid=lot["id"]: State.delete_reagent_lot(lid),
                                        class_name="w-full mt-2 bg-red-50 text-red-600 hover:bg-red-100 text-xs py-2 rounded-lg transition-colors",
                                    )
                                ),
                                class_name="bg-white border border-gray-100 rounded-xl p-4 hover:shadow-md transition-all"
                            )
                        ),
                        columns="1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4",
                        spacing="4",
                        width="100%"
                    ),
                    rx.text("Nenhum lote cadastrado", class_name="text-gray-400 py-8 text-center w-full bg-white rounded-xl")
                ),
                spacing="3",
                width="100%",
            ),
            class_name="w-full mt-4"
        ),
        
        # Manutenções de Equipamentos
        rx.box(
            rx.vstack(
                rx.text("🔧 Diário de Manutenções", class_name="font-bold text-[#1B5E20] text-lg"),
                rx.text("Registro de intervenções técnicas nos equipamentos", class_name="text-gray-500 text-sm mb-4"),

                rx.grid(
                    rx.box(
                        rx.vstack(
                            rx.text("Equipamento *", class_name="text-sm font-medium text-gray-700"),
                            rx.input(
                                placeholder="Ex: Analisador XYZ",
                                value=State.maintenance_equipment,
                                on_change=State.set_maintenance_equipment,
                                class_name="w-full rounded-xl"
                            ),
                            spacing="1",
                        )
                    ),
                    rx.box(
                        rx.vstack(
                            rx.text("Tipo *", class_name="text-sm font-medium text-gray-700"),
                            rx.select(
                                ["Preventiva", "Corretiva", "Calibração", "Limpeza", "Verificação"],
                                value=State.maintenance_type,
                                on_change=State.set_maintenance_type,
                                class_name="w-full rounded-xl"
                            ),
                            spacing="1",
                        )
                    ),
                    rx.box(
                        rx.vstack(
                            rx.text("Data", class_name="text-sm font-medium text-gray-700"),
                            rx.input(
                                type="date",
                                value=State.maintenance_date,
                                on_change=State.set_maintenance_date,
                                class_name="w-full rounded-xl"
                            ),
                            spacing="1",
                        )
                    ),
                    rx.box(
                        rx.vstack(
                            rx.text("Próxima Manutenção", class_name="text-sm font-medium text-gray-700"),
                            rx.input(
                                type="date",
                                value=State.maintenance_next_date,
                                on_change=State.set_maintenance_next_date,
                                class_name="w-full rounded-xl"
                            ),
                            spacing="1",
                        )
                    ),
                    columns="1 md:grid-cols-4",
                    spacing="4",
                    width="100%",
                ),

                rx.button(
                    rx.cond(
                        State.is_saving_maintenance,
                        rx.hstack(rx.spinner(size="2", color="white"), rx.text("Salvando..."), spacing="2"),
                        rx.hstack(rx.icon("tool", size=18), rx.text("Registrar Manutenção"), spacing="2"),
                    ),
                    on_click=State.save_maintenance_record,
                    disabled=State.is_saving_maintenance,
                    class_name="bg-[#1B5E20] text-white px-6 py-3 rounded-xl font-semibold hover:bg-[#2E7D32] transition-all mt-4 w-full md:w-auto"
                ),

                # Lista de manutenções
                rx.cond(
                    State.maintenance_records.length() > 0,
                    rx.box(
                        rx.table.root(
                            rx.table.header(
                                rx.table.row(
                                    rx.table.column_header_cell("Equipamento", class_name="py-3"),
                                    rx.table.column_header_cell("Tipo", class_name="py-3"),
                                    rx.table.column_header_cell("Data", class_name="py-3"),
                                    rx.table.column_header_cell("Próxima", class_name="py-3"),
                                    rx.table.column_header_cell("Ação", class_name="py-3"),
                                )
                            ),
                            rx.table.body(
                                rx.foreach(
                                    State.maintenance_records,
                                    lambda m: rx.table.row(
                                        rx.table.cell(m["equipment"], class_name="font-medium"),
                                        rx.table.cell(rx.badge(m["type"], variant="soft")),
                                        rx.table.cell(m["date"]),
                                        rx.table.cell(m["next_date"], class_name="text-amber-600 font-medium"),
                                        rx.table.cell(
                                            rx.button(
                                                rx.icon("trash-2", size=14),
                                                on_click=lambda mid=m["id"]: State.delete_maintenance_record(mid),
                                                class_name="bg-red-50 text-red-600 p-2 rounded-lg hover:bg-red-100",
                                                variant="ghost"
                                            )
                                        ),
                                    )
                                )
                            ),
                            width="100%",
                        ),
                        class_name="w-full mt-6 overflow-x-auto rounded-xl border border-gray-100"
                    ),
                ),
                spacing="3",
                width="100%",
            ),
            class_name="bg-white border border-gray-100 rounded-3xl p-8 w-full shadow-sm mt-6"
        ),
        
        spacing="4",
        width="100%",
    )


def relatorios_tab() -> rx.Component:
    """Aba de Relatórios - Gráfico Levey-Jennings Premium"""
    return rx.vstack(
        rx.hstack(
            rx.box(
                rx.text("📈", class_name="text-2xl"),
                class_name="w-12 h-12 rounded-xl bg-blue-50 flex items-center justify-center"
            ),
            rx.vstack(
                rx.text("Gráfico Levey-Jennings", class_name="text-2xl font-bold text-[#1B5E20]"),
                rx.text("Ferramenta padrão ouro para auditoria de controle interno de qualidade", class_name="text-gray-500 text-sm"),
                spacing="0",
                align="start",
            ),
            spacing="3",
            align="center",
            class_name="mb-6 w-full"
        ),
        
        # Filtros
        rx.box(
            rx.hstack(
                rx.box(
                    rx.vstack(
                        rx.text("Selecione o Exame", class_name="text-sm font-medium text-gray-700"),
                        rx.select(
                            State.unique_exam_names,
                            value=State.levey_jennings_exam,
                            on_change=State.set_levey_jennings_exam,
                            placeholder="Escolha um exame...",
                            class_name="w-full min-w-[250px] rounded-xl bg-gray-50 border-gray-200"
                        ),
                        spacing="1",
                        width="100%"
                    ),
                    class_name="flex-1"
                ),
                rx.box(
                    rx.vstack(
                        rx.text("Período (dias)", class_name="text-sm font-medium text-gray-700"),
                        rx.select(
                            ["7", "15", "30", "60", "90"],
                            value=State.levey_jennings_period,
                            on_change=State.set_levey_jennings_period,
                            class_name="w-full rounded-xl bg-gray-50 border-gray-200"
                        ),
                        spacing="1",
                        width="150px"
                    )
                ),
                spacing="4",
                width="100%",
                wrap="wrap",
                align="end"
            ),
            class_name="bg-white border border-gray-100 rounded-2xl p-6 w-full shadow-sm"
        ),
        
        # Gráfico (representação visual)
        rx.cond(
            State.levey_jennings_data.length() > 0,
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.text("Controle de Qualidade Diário", class_name="font-bold text-gray-800"),
                        rx.spacer(),
                        # Legenda
                        rx.hstack(
                            rx.hstack(rx.box(class_name="w-2 h-2 bg-green-500 rounded-full"), rx.text("±1 DP", class_name="text-xs text-gray-500")),
                            rx.hstack(rx.box(class_name="w-2 h-2 bg-amber-500 rounded-full"), rx.text("±2 DP", class_name="text-xs text-gray-500")),
                            rx.hstack(rx.box(class_name="w-2 h-2 bg-red-500 rounded-full"), rx.text("±3 DP", class_name="text-xs text-gray-500")),
                            spacing="4",
                        ),
                        width="100%",
                        align="center"
                    ),
                    
                    # Área do gráfico representativa
                    rx.box(
                        rx.vstack(
                            # Zonas coloridas para representar desvios
                            rx.box(
                                class_name="relative w-full h-[300px] border border-gray-100 rounded-xl bg-white p-4",
                                children=[
                                    # Linhas de grade
                                    rx.box(class_name="absolute top-[10%] left-0 right-0 h-[1px] bg-red-200 border-dashed border-t border-red-300"), # +3SD
                                    rx.box(class_name="absolute top-[23%] left-0 right-0 h-[1px] bg-amber-200 border-dashed border-t border-amber-300"), # +2SD
                                    rx.box(class_name="absolute top-[36%] left-0 right-0 h-[1px] bg-green-200 border-dashed border-t border-green-300"), # +1SD
                                    rx.box(class_name="absolute top-[50%] left-0 right-0 h-[2px] bg-gray-800"), # MEAN
                                    rx.box(class_name="absolute top-[63%] left-0 right-0 h-[1px] bg-green-200 border-dashed border-t border-green-300"), # -1SD
                                    rx.box(class_name="absolute top-[76%] left-0 right-0 h-[1px] bg-amber-200 border-dashed border-t border-amber-300"), # -2SD
                                    rx.box(class_name="absolute top-[90%] left-0 right-0 h-[1px] bg-red-200 border-dashed border-t border-red-300"), # -3SD

                                    # Labels
                                    rx.text("+3SD", class_name="absolute top-[8%] right-2 text-[10px] text-red-400 font-bold"),
                                    rx.text("+2SD", class_name="absolute top-[21%] right-2 text-[10px] text-amber-400 font-bold"),
                                    rx.text("Média", class_name="absolute top-[48%] right-2 text-[10px] text-gray-400 font-bold"),
                                    rx.text("-2SD", class_name="absolute top-[74%] right-2 text-[10px] text-amber-400 font-bold"),
                                    rx.text("-3SD", class_name="absolute top-[88%] right-2 text-[10px] text-red-400 font-bold"),

                                    # Pontos (simulados visualmente distribuídos)
                                    rx.hstack(
                                        rx.foreach(
                                            State.levey_jennings_data,
                                            lambda d: rx.tooltip(
                                                rx.box(
                                                    class_name="w-2.5 h-2.5 bg-blue-600 rounded-full border-2 border-white shadow-sm hover:scale-150 transition-transform cursor-pointer"
                                                ),
                                                content=d["date"].to_string() + ": " + d["value"].to_string()
                                            )
                                        ),
                                        spacing="4",
                                        justify="center",
                                        align="center",
                                        class_name="absolute inset-0 flex items-center px-8"
                                    ),
                                ]
                            ),
                        ),
                        class_name="w-full mt-4"
                    ),
                    
                    # Tabela de dados detalhada
                    rx.box(
                        rx.table.root(
                            rx.table.header(
                                rx.table.row(
                                    rx.table.column_header_cell("Data", class_name="bg-gray-50"),
                                    rx.table.column_header_cell("Valor", class_name="bg-gray-50"),
                                    rx.table.column_header_cell("Alvo", class_name="bg-gray-50"),
                                    rx.table.column_header_cell("Desvio", class_name="bg-gray-50"),
                                )
                            ),
                            rx.table.body(
                                rx.foreach(
                                    State.levey_jennings_data,
                                    lambda d: rx.table.row(
                                        rx.table.cell(d["date"]),
                                        rx.table.cell(d["value"], class_name="font-mono"),
                                        rx.table.cell(d["target"], class_name="text-gray-500"),
                                        rx.table.cell(
                                            rx.badge(
                                                d["cv"].to_string() + "%",
                                                variant="outline"
                                            )
                                        ),
                                    )
                                )
                            ),
                            width="100%",
                        ),
                        class_name="w-full overflow-x-auto mt-6 rounded-xl border border-gray-100"
                    ),
                    
                    spacing="3",
                    width="100%",
                ),
                class_name="bg-white border border-gray-100 rounded-3xl p-8 w-full shadow-sm mt-4"
            ),
            rx.box(
                rx.vstack(
                    rx.icon("line-chart", size=48, class_name="text-gray-200"),
                    rx.text("Selecione um exame para visualizar o gráfico", class_name="text-gray-400 font-medium"),
                    align="center",
                    spacing="2"
                ),
                class_name="bg-white border border-gray-100 rounded-3xl p-12 w-full text-center mt-4"
            )
        ),
        
        spacing="4",
        width="100%",
    )


def importar_tab() -> rx.Component:
    """Aba de Importação de Planilhas - Premium"""
    excel_svg = """
        <svg viewBox="0 0 80 100" width="80" height="100">
            <rect x="10" y="5" width="60" height="85" rx="4" fill="#FFFFFF" stroke="#1B5E20" stroke-width="2"/>
            <path d="M55 5 L55 20 L70 20" fill="#E8F5E9" stroke="#1B5E20" stroke-width="2"/>
            <rect x="20" y="35" width="40" height="30" rx="3" fill="#1B5E20"/>
            <text x="28" y="56" fill="white" font-size="16" font-weight="bold">XLS</text>
            <line x1="25" y1="75" x2="55" y2="75" stroke="#4CAF50" stroke-width="2"/>
            <line x1="25" y1="82" x2="45" y2="82" stroke="#4CAF50" stroke-width="2"/>
        </svg>
    """
    
    return rx.vstack(
        rx.hstack(
            rx.box(
                rx.text("📥", class_name="text-2xl"),
                class_name="w-12 h-12 rounded-xl bg-gray-100 flex items-center justify-center"
            ),
            rx.vstack(
                rx.text("Migração de Dados Legados", class_name="text-2xl font-bold text-[#1B5E20]"),
                rx.text("Importe planilhas Excel existentes para popular o sistema", class_name="text-gray-500 text-sm"),
                spacing="0",
                align="start",
            ),
            spacing="3",
            align="center",
            class_name="mb-6 w-full"
        ),
        
        # Upload area
        rx.box(
            rx.upload(
                rx.vstack(
                    rx.cond(
                        State.excel_file_name != "",
                        rx.vstack(
                            rx.icon("file-spreadsheet", size=48, class_name="text-green-600"),
                            rx.text("Arquivo Pronto", class_name="text-[#1B5E20] font-bold text-lg"),
                            rx.text(State.excel_file_name, class_name="bg-green-50 text-green-700 px-3 py-1 rounded-full text-sm font-medium"),
                            spacing="2",
                            align="center",
                        ),
                        rx.vstack(
                            rx.html(excel_svg),
                            rx.text("Arraste sua planilha aqui", class_name="text-[#1B5E20] font-bold text-lg mt-4"),
                            rx.text("Suporte para .xlsx e .xls", class_name="text-gray-400 text-sm"),
                            spacing="1",
                            align="center",
                        ),
                    ),
                    justify="center",
                    align="center",
                    class_name="w-full h-full min-h-[250px] py-8"
                ),
                id="excel_upload",
                accept={
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"],
                    "application/vnd.ms-excel": [".xls"]
                },
                max_files=1,
                on_drop=State.handle_excel_upload(rx.upload_files(upload_id="excel_upload")),
                class_name="w-full h-full cursor-pointer outline-none"
            ),
            class_name="border-2 border-dashed border-gray-300 rounded-3xl hover:border-[#4CAF50] hover:bg-green-50/10 transition-all max-w-2xl mx-auto bg-white"
        ),
        
        # Botões de ação
        rx.hstack(
            rx.button(
                rx.cond(
                    State.is_analyzing_excel,
                    rx.hstack(rx.spinner(size="2", color="white"), rx.text("Analisando Estrutura..."), spacing="2"),
                    rx.hstack(rx.icon("search", size=18), rx.text("Analisar Planilha"), spacing="2"),
                ),
                on_click=State.analyze_excel,
                disabled=~State.has_excel_file | State.is_analyzing_excel,
                class_name="bg-white border border-[#1B5E20] text-[#1B5E20] px-6 py-3 rounded-xl font-semibold hover:bg-green-50 transition-all disabled:opacity-50"
            ),
            rx.button(
                rx.hstack(rx.icon("download", size=18), rx.text("Importar Dados"), spacing="2"),
                on_click=State.import_excel_to_qc,
                disabled=~State.excel_analyzed | State.is_analyzing_excel,
                class_name="bg-[#1B5E20] text-white px-6 py-3 rounded-xl font-semibold hover:bg-[#2E7D32] transition-all disabled:opacity-50"
            ),
            spacing="4",
            justify="center",
            class_name="mt-4"
        ),
        
        # Preview dos dados
        rx.cond(
            State.excel_analyzed,
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.icon("table", size=20, class_name="text-gray-500"),
                        rx.text("Pré-visualização dos Dados", class_name="font-bold text-gray-800"),
                        rx.spacer(),
                        rx.badge(f"{State.excel_total_rows} linhas", variant="outline"),
                        width="100%",
                        align="center"
                    ),
                    rx.cond(
                        State.excel_preview.length() > 0,
                        rx.box(
                            rx.table.root(
                                rx.table.header(
                                    rx.table.row(
                                        rx.foreach(
                                            State.excel_headers,
                                            lambda header: rx.table.column_header_cell(
                                                header,
                                                class_name="bg-gray-50 text-xs font-bold uppercase tracking-wider py-3"
                                            )
                                        )
                                    )
                                ),
                                rx.table.body(
                                    rx.foreach(
                                        State.excel_preview,
                                        lambda row: rx.table.row(
                                            rx.foreach(
                                                row,
                                                lambda cell: rx.table.cell(
                                                    cell,
                                                    class_name="text-xs py-2 border-b border-gray-50"
                                                )
                                            )
                                        )
                                    )
                                ),
                                width="100%",
                            ),
                            class_name="w-full overflow-x-auto rounded-xl border border-gray-100 mt-4"
                        ),
                        rx.text("Nenhum dado disponível para visualização", class_name="text-gray-400 py-4")
                    ),
                    spacing="3",
                    width="100%",
                ),
                class_name="bg-white border border-gray-100 rounded-3xl p-6 w-full mt-6 shadow-sm"
            ),
        ),
        
        spacing="4",
        width="100%",
        align="center",
    )


def proin_page() -> rx.Component:
    """Página principal do ProIn QC - Layout Premium"""
    
    return rx.box(
        rx.vstack(
            # Badge de certificação
            rx.box(
                rx.hstack(
                    rx.text("💎", class_name="text-sm"),
                    rx.text(
                        "Certificação PNCQ Diamante",
                        class_name="text-[#1B5E20] text-xs font-bold tracking-wide uppercase"
                    ),
                    spacing="2",
                    align="center",
                ),
                class_name="bg-white border border-green-100 px-4 py-1.5 rounded-full shadow-sm mb-6"
            ),
            
            # Título
            rx.text(
                "Controle Interno de Qualidade",
                class_name="text-[#1B5E20] text-4xl font-bold tracking-tight text-center"
            ),
            
            rx.text(
                "Gestão completa de conformidade e excelência laboratorial (ProIn)",
                class_name="text-gray-500 text-lg mt-2 text-center"
            ),
            
            # Abas de navegação
            rx.box(
                rx.hstack(
                    tab_button("Dashboard", "📊", "dashboard"),
                    tab_button("Novo Registro", "📝", "registro"),
                    tab_button("Insumos", "🧪", "reagentes"),
                    tab_button("Relatórios", "📈", "relatorios"),
                    tab_button("Importar", "📥", "importar"),
                    spacing="2",
                    wrap="wrap",
                    justify="center",
                ),
                class_name="w-full mt-8 mb-6"
            ),
            
            # Conteúdo da aba atual
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
                class_name="w-full max-w-7xl animate-fade-in"
            ),
            
            spacing="0",
            align="center",
            width="100%",
            class_name="py-8 px-4"
        ),
        width="100%",
    )
