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


def tab_button(label: str, icon: str, tab_id: str) -> rx.Component:
    """Botão de aba do ProIn"""
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
            "px-4 py-2.5 bg-[#1B5E20] text-white rounded-lg cursor-pointer transition-all shadow-md",
            "px-4 py-2.5 bg-white text-[#1B5E20] border border-gray-200 rounded-lg cursor-pointer hover:bg-green-50 transition-all"
        ),
    )


def alert_card_static(icon: str, title: str, value, color: str, subtitle: str = "") -> rx.Component:
    """Card de alerta/estatística com cor estática"""
    bg_colors = {
        "green": "bg-green-50 border-green-200",
        "red": "bg-red-50 border-red-200",
        "amber": "bg-amber-50 border-amber-200",
        "blue": "bg-blue-50 border-blue-200"
    }
    text_colors = {
        "green": "text-green-700",
        "red": "text-red-700",
        "amber": "text-amber-700",
        "blue": "text-blue-700"
    }
    
    return rx.box(
        rx.vstack(
            rx.text(icon, class_name="text-3xl"),
            rx.text(value, class_name=f"text-3xl font-bold {text_colors.get(color, 'text-gray-700')}"),
            rx.text(title, class_name="text-sm font-medium text-gray-600"),
            rx.cond(
                subtitle != "",
                rx.text(subtitle, class_name="text-xs text-gray-400"),
            ),
            spacing="1",
            align="center",
        ),
        class_name=f"p-4 rounded-xl border {bg_colors.get(color, 'bg-gray-50 border-gray-200')} flex-1 min-w-[140px]"
    )


def alert_card_dynamic(icon: str, title: str, value, condition, color_true: str, color_false: str, subtitle: str = "") -> rx.Component:
    """Card de alerta/estatística com cor dinâmica baseada em condição"""
    bg_classes = {
        "green": "bg-green-50 border-green-200",
        "red": "bg-red-50 border-red-200",
        "amber": "bg-amber-50 border-amber-200",
        "blue": "bg-blue-50 border-blue-200"
    }
    text_classes = {
        "green": "text-green-700",
        "red": "text-red-700",
        "amber": "text-amber-700",
        "blue": "text-blue-700"
    }
    
    return rx.box(
        rx.vstack(
            rx.text(icon, class_name="text-3xl"),
            rx.text(
                value, 
                class_name=rx.cond(
                    condition,
                    f"text-3xl font-bold {text_classes.get(color_true, 'text-gray-700')}",
                    f"text-3xl font-bold {text_classes.get(color_false, 'text-gray-700')}"
                )
            ),
            rx.text(title, class_name="text-sm font-medium text-gray-600"),
            rx.cond(
                subtitle != "",
                rx.text(subtitle, class_name="text-xs text-gray-400"),
            ),
            spacing="1",
            align="center",
        ),
        class_name=rx.cond(
            condition,
            f"p-4 rounded-xl border {bg_classes.get(color_true, 'bg-gray-50 border-gray-200')} flex-1 min-w-[140px]",
            f"p-4 rounded-xl border {bg_classes.get(color_false, 'bg-gray-50 border-gray-200')} flex-1 min-w-[140px]"
        )
    )


def dashboard_tab() -> rx.Component:
    """Aba Dashboard - Visão geral"""
    return rx.vstack(
        # Título
        rx.hstack(
            rx.text("📊", class_name="text-2xl"),
            rx.text("Dashboard - Visão Geral", class_name="text-xl font-bold text-[#1B5E20]"),
            spacing="2",
            align="center",
        ),
        
        # Cards de estatísticas
        rx.box(
            rx.hstack(
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
                spacing="4",
                wrap="wrap",
                width="100%",
            ),
            class_name="w-full"
        ),
        
        # Segunda linha de cards
        rx.box(
            rx.hstack(
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
                spacing="4",
                wrap="wrap",
                width="100%",
            ),
            class_name="w-full"
        ),
        
        # Alertas Ativos
        rx.cond(
            State.qc_records_with_alerts.length() > 0,
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.text("🚨", class_name="text-xl"),
                        rx.text("Alertas de Controle de Qualidade", class_name="font-bold text-red-700"),
                        spacing="2",
                    ),
                    rx.foreach(
                        State.qc_records_with_alerts[:5],
                        lambda r: rx.box(
                            rx.hstack(
                                rx.text(r["exam_name"], class_name="font-medium flex-1"),
                                rx.badge(
                                    "CV: " + r["cv"].to_string() + "%",
                                    class_name="bg-red-100 text-red-700"
                                ),
                                rx.text(r["date"], class_name="text-gray-500 text-sm"),
                                justify="between",
                                width="100%",
                            ),
                            class_name="py-2 border-b border-red-100"
                        )
                    ),
                    spacing="2",
                    width="100%",
                ),
                class_name="bg-red-50 border border-red-200 rounded-xl p-4 w-full"
            ),
        ),
        
        # Lotes Vencendo
        rx.cond(
            State.lots_expiring_soon.length() > 0,
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.text("⏰", class_name="text-xl"),
                        rx.text("Lotes Próximos da Validade", class_name="font-bold text-amber-700"),
                        spacing="2",
                    ),
                    rx.foreach(
                        State.lots_expiring_soon[:5],
                        lambda lot: rx.box(
                            rx.hstack(
                                rx.text(lot["name"], class_name="font-medium flex-1"),
                                rx.text(lot["lot_number"], class_name="text-gray-500 text-sm"),
                                rx.badge(
                                    lot["days_left"].to_string() + " dias",
                                    class_name="bg-amber-100 text-amber-700"
                                ),
                                justify="between",
                                width="100%",
                            ),
                            class_name="py-2 border-b border-amber-100"
                        )
                    ),
                    spacing="2",
                    width="100%",
                ),
                class_name="bg-amber-50 border border-amber-200 rounded-xl p-4 w-full"
            ),
        ),
        
        # Últimos registros
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.text("📝", class_name="text-xl"),
                    rx.text("Últimos Registros de CQ", class_name="font-bold text-[#1B5E20]"),
                    spacing="2",
                ),
                rx.cond(
                    State.qc_records.length() > 0,
                    rx.box(
                        rx.foreach(
                            State.qc_records[:5],
                            lambda r: rx.box(
                                rx.hstack(
                                    rx.vstack(
                                        rx.text(r["exam_name"], class_name="font-medium"),
                                        rx.text(r["date"], class_name="text-xs text-gray-400"),
                                        spacing="0",
                                        align="start",
                                    ),
                                    rx.spacer(),
                                    rx.vstack(
                                        rx.text(
                                            "CV: " + r["cv"].to_string() + "%",
                                            class_name="font-bold"
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
                                class_name="py-3 border-b border-gray-100 last:border-0"
                            )
                        ),
                        class_name="w-full"
                    ),
                    rx.text("Nenhum registro encontrado", class_name="text-gray-400 py-4 text-center")
                ),
                spacing="3",
                width="100%",
            ),
            class_name="bg-white border border-gray-200 rounded-xl p-4 w-full"
        ),
        
        spacing="4",
        width="100%",
    )


def registro_qc_tab() -> rx.Component:
    """Aba de Registro de Controle de Qualidade"""
    return rx.vstack(
        # Título
        rx.hstack(
            rx.text("📝", class_name="text-2xl"),
            rx.text("Registro de Controle de Qualidade", class_name="text-xl font-bold text-[#1B5E20]"),
            spacing="2",
            align="center",
        ),
        
        rx.text(
            "Registre os dados diários de CQ. O sistema calcula automaticamente o CV%.",
            class_name="text-gray-500 text-sm"
        ),
        
        # Formulário
        rx.box(
            rx.vstack(
                rx.grid(
                    # Exame
                    rx.box(
                        rx.vstack(
                            rx.text("Nome do Exame *", class_name="text-sm font-medium text-gray-700"),
                            rx.input(
                                placeholder="Ex: Glicose, Hemoglobina...",
                                value=State.qc_exam_name,
                                on_change=State.set_qc_exam_name,
                                class_name="w-full"
                            ),
                            spacing="1",
                            width="100%",
                        )
                    ),
                    # Nível
                    rx.box(
                        rx.vstack(
                            rx.text("Nível", class_name="text-sm font-medium text-gray-700"),
                            rx.select(
                                ["Normal", "Patológico"],
                                value=State.qc_level,
                                on_change=State.set_qc_level,
                                class_name="w-full"
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
                                class_name="w-full"
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
                                class_name="w-full"
                            ),
                            spacing="1",
                            width="100%",
                        )
                    ),
                    columns="2",
                    spacing="4",
                    width="100%",
                ),
                
                rx.divider(class_name="my-2"),
                
                rx.grid(
                    # Valor 1
                    rx.box(
                        rx.vstack(
                            rx.text("Medição 1 *", class_name="text-sm font-medium text-gray-700"),
                            rx.input(
                                placeholder="Ex: 98.5",
                                value=State.qc_value1,
                                on_change=State.set_qc_value1,
                                class_name="w-full"
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
                                placeholder="Ex: 99.2",
                                value=State.qc_value2,
                                on_change=State.set_qc_value2,
                                class_name="w-full"
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
                                placeholder="Ex: 100",
                                value=State.qc_target_value,
                                on_change=State.set_qc_target_value,
                                class_name="w-full"
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
                                placeholder="Ex: 5",
                                value=State.qc_target_sd,
                                on_change=State.set_qc_target_sd,
                                class_name="w-full"
                            ),
                            spacing="1",
                            width="100%",
                        )
                    ),
                    columns="4",
                    spacing="4",
                    width="100%",
                ),
                
                rx.grid(
                    # Equipamento
                    rx.box(
                        rx.vstack(
                            rx.text("Equipamento", class_name="text-sm font-medium text-gray-700"),
                            rx.input(
                                placeholder="Ex: Analisador Bioquímico",
                                value=State.qc_equipment,
                                on_change=State.set_qc_equipment,
                                class_name="w-full"
                            ),
                            spacing="1",
                            width="100%",
                        )
                    ),
                    # Analista
                    rx.box(
                        rx.vstack(
                            rx.text("Analista", class_name="text-sm font-medium text-gray-700"),
                            rx.input(
                                placeholder="Seu nome",
                                value=State.qc_analyst,
                                on_change=State.set_qc_analyst,
                                class_name="w-full"
                            ),
                            spacing="1",
                            width="100%",
                        )
                    ),
                    columns="2",
                    spacing="4",
                    width="100%",
                ),
                
                # Botão salvar
                rx.button(
                    rx.cond(
                        State.is_saving_qc,
                        rx.hstack(rx.spinner(size="1"), rx.text("Salvando..."), spacing="2"),
                        rx.hstack(rx.text("💾"), rx.text("Salvar Registro"), spacing="2"),
                    ),
                    on_click=State.save_qc_record,
                    disabled=State.is_saving_qc,
                    class_name="bg-[#1B5E20] text-white px-6 py-2.5 rounded-lg font-semibold hover:bg-[#2E7D32] transition-all w-full mt-4"
                ),
                
                # Mensagens
                rx.cond(
                    State.qc_success_message != "",
                    rx.box(
                        rx.text(f"✅ {State.qc_success_message}", class_name="text-green-700"),
                        class_name="bg-green-50 border border-green-200 rounded-lg p-3 w-full"
                    ),
                ),
                rx.cond(
                    State.qc_error_message != "",
                    rx.box(
                        rx.text(f"❌ {State.qc_error_message}", class_name="text-red-700"),
                        class_name="bg-red-50 border border-red-200 rounded-lg p-3 w-full"
                    ),
                ),
                
                spacing="4",
                width="100%",
            ),
            class_name="bg-white border border-gray-200 rounded-xl p-6 w-full"
        ),
        
        # Histórico de registros
        rx.box(
            rx.vstack(
                rx.text("📋 Histórico de Registros", class_name="font-bold text-[#1B5E20]"),
                rx.cond(
                    State.qc_records.length() > 0,
                    rx.box(
                        rx.table.root(
                            rx.table.header(
                                rx.table.row(
                                    rx.table.column_header_cell("Data", class_name="bg-[#1B5E20] text-white"),
                                    rx.table.column_header_cell("Exame", class_name="bg-[#1B5E20] text-white"),
                                    rx.table.column_header_cell("Média", class_name="bg-[#1B5E20] text-white"),
                                    rx.table.column_header_cell("CV%", class_name="bg-[#1B5E20] text-white"),
                                    rx.table.column_header_cell("Status", class_name="bg-[#1B5E20] text-white"),
                                    rx.table.column_header_cell("Ações", class_name="bg-[#1B5E20] text-white"),
                                )
                            ),
                            rx.table.body(
                                rx.foreach(
                                    State.qc_records,
                                    lambda r: rx.table.row(
                                        rx.table.cell(r["date"][:16]),
                                        rx.table.cell(r["exam_name"]),
                                        rx.table.cell(r["mean"]),
                                        rx.table.cell(
                                            rx.text(
                                                r["cv"].to_string() + "%",
                                                class_name=rx.cond(
                                                    r["status"] == "OK",
                                                    "text-green-600 font-bold",
                                                    "text-red-600 font-bold"
                                                )
                                            )
                                        ),
                                        rx.table.cell(
                                            rx.badge(
                                                r["status"],
                                                class_name=rx.cond(
                                                    r["status"] == "OK",
                                                    "bg-green-100 text-green-700",
                                                    "bg-red-100 text-red-700"
                                                )
                                            )
                                        ),
                                        rx.table.cell(
                                            rx.button(
                                                "🗑️",
                                                on_click=lambda rid=r["id"]: State.delete_qc_record(rid),
                                                class_name="bg-red-50 text-red-600 px-2 py-1 rounded hover:bg-red-100",
                                                size="1"
                                            )
                                        ),
                                    )
                                )
                            ),
                            width="100%",
                        ),
                        class_name="w-full overflow-x-auto"
                    ),
                    rx.text("Nenhum registro cadastrado", class_name="text-gray-400 py-4")
                ),
                spacing="3",
                width="100%",
            ),
            class_name="bg-white border border-gray-200 rounded-xl p-4 w-full"
        ),
        
        spacing="4",
        width="100%",
    )


def reagentes_tab() -> rx.Component:
    """Aba de Gestão de Reagentes"""
    return rx.vstack(
        # Título
        rx.hstack(
            rx.text("🧪", class_name="text-2xl"),
            rx.text("Gestão de Reagentes e Lotes", class_name="text-xl font-bold text-[#1B5E20]"),
            spacing="2",
            align="center",
        ),
        
        # Formulário de cadastro
        rx.box(
            rx.vstack(
                rx.text("Cadastrar Novo Lote", class_name="font-semibold text-[#1B5E20]"),
                rx.grid(
                    rx.box(
                        rx.vstack(
                            rx.text("Nome do Reagente *", class_name="text-sm font-medium text-gray-700"),
                            rx.input(
                                placeholder="Ex: Controle Glicose Nível I",
                                value=State.reagent_name,
                                on_change=State.set_reagent_name,
                                class_name="w-full"
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
                                class_name="w-full"
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
                                class_name="w-full"
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
                                class_name="w-full"
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
                                class_name="w-full"
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
                                class_name="w-full"
                            ),
                            spacing="1",
                            width="100%",
                        )
                    ),
                    columns="3",
                    spacing="4",
                    width="100%",
                ),
                rx.button(
                    rx.cond(
                        State.is_saving_reagent,
                        rx.hstack(rx.spinner(size="1"), rx.text("Salvando..."), spacing="2"),
                        rx.hstack(rx.text("💾"), rx.text("Cadastrar Lote"), spacing="2"),
                    ),
                    on_click=State.save_reagent_lot,
                    disabled=State.is_saving_reagent,
                    class_name="bg-[#1B5E20] text-white px-6 py-2.5 rounded-lg font-semibold hover:bg-[#2E7D32] transition-all mt-4"
                ),
                rx.cond(
                    State.reagent_success_message != "",
                    rx.box(
                        rx.text(f"✅ {State.reagent_success_message}", class_name="text-green-700"),
                        class_name="bg-green-50 border border-green-200 rounded-lg p-3 w-full"
                    ),
                ),
                rx.cond(
                    State.reagent_error_message != "",
                    rx.box(
                        rx.text(f"❌ {State.reagent_error_message}", class_name="text-red-700"),
                        class_name="bg-red-50 border border-red-200 rounded-lg p-3 w-full"
                    ),
                ),
                spacing="3",
                width="100%",
            ),
            class_name="bg-white border border-gray-200 rounded-xl p-6 w-full"
        ),
        
        # Lista de lotes
        rx.box(
            rx.vstack(
                rx.text("📦 Lotes Cadastrados", class_name="font-bold text-[#1B5E20]"),
                rx.cond(
                    State.reagent_lots.length() > 0,
                    rx.box(
                        rx.foreach(
                            State.reagent_lots,
                            lambda lot: rx.box(
                                rx.hstack(
                                    rx.vstack(
                                        rx.text(lot["name"], class_name="font-medium"),
                                        rx.text("Lote: " + lot["lot_number"].to_string(), class_name="text-sm text-gray-500"),
                                        spacing="0",
                                        align="start",
                                    ),
                                    rx.spacer(),
                                    rx.vstack(
                                        rx.text("Validade: " + lot["expiry_date"].to_string(), class_name="text-sm"),
                                        rx.text(lot["manufacturer"], class_name="text-xs text-gray-400"),
                                        spacing="0",
                                        align="end",
                                    ),
                                    rx.button(
                                        "🗑️",
                                        on_click=lambda lid=lot["id"]: State.delete_reagent_lot(lid),
                                        class_name="bg-red-50 text-red-600 px-2 py-1 rounded hover:bg-red-100 ml-2",
                                        size="1"
                                    ),
                                    width="100%",
                                ),
                                class_name="py-3 border-b border-gray-100 last:border-0"
                            )
                        ),
                        class_name="w-full"
                    ),
                    rx.text("Nenhum lote cadastrado", class_name="text-gray-400 py-4")
                ),
                spacing="3",
                width="100%",
            ),
            class_name="bg-white border border-gray-200 rounded-xl p-4 w-full"
        ),
        
        # Manutenções de Equipamentos
        rx.box(
            rx.vstack(
                rx.text("🔧 Diário de Manutenções", class_name="font-bold text-[#1B5E20]"),
                rx.grid(
                    rx.box(
                        rx.vstack(
                            rx.text("Equipamento *", class_name="text-sm font-medium text-gray-700"),
                            rx.input(
                                placeholder="Ex: Analisador XYZ",
                                value=State.maintenance_equipment,
                                on_change=State.set_maintenance_equipment,
                                class_name="w-full"
                            ),
                            spacing="1",
                            width="100%",
                        )
                    ),
                    rx.box(
                        rx.vstack(
                            rx.text("Tipo de Manutenção *", class_name="text-sm font-medium text-gray-700"),
                            rx.select(
                                ["Preventiva", "Corretiva", "Calibração", "Limpeza", "Verificação"],
                                value=State.maintenance_type,
                                on_change=State.set_maintenance_type,
                                class_name="w-full"
                            ),
                            spacing="1",
                            width="100%",
                        )
                    ),
                    rx.box(
                        rx.vstack(
                            rx.text("Data", class_name="text-sm font-medium text-gray-700"),
                            rx.input(
                                type="date",
                                value=State.maintenance_date,
                                on_change=State.set_maintenance_date,
                                class_name="w-full"
                            ),
                            spacing="1",
                            width="100%",
                        )
                    ),
                    rx.box(
                        rx.vstack(
                            rx.text("Próxima Manutenção", class_name="text-sm font-medium text-gray-700"),
                            rx.input(
                                type="date",
                                value=State.maintenance_next_date,
                                on_change=State.set_maintenance_next_date,
                                class_name="w-full"
                            ),
                            spacing="1",
                            width="100%",
                        )
                    ),
                    columns="4",
                    spacing="4",
                    width="100%",
                ),
                rx.grid(
                    rx.box(
                        rx.vstack(
                            rx.text("Técnico Responsável", class_name="text-sm font-medium text-gray-700"),
                            rx.input(
                                placeholder="Nome do técnico",
                                value=State.maintenance_technician,
                                on_change=State.set_maintenance_technician,
                                class_name="w-full"
                            ),
                            spacing="1",
                            width="100%",
                        )
                    ),
                    rx.box(
                        rx.vstack(
                            rx.text("Observações", class_name="text-sm font-medium text-gray-700"),
                            rx.input(
                                placeholder="Notas sobre a manutenção...",
                                value=State.maintenance_notes,
                                on_change=State.set_maintenance_notes,
                                class_name="w-full"
                            ),
                            spacing="1",
                            width="100%",
                        )
                    ),
                    columns="2",
                    spacing="4",
                    width="100%",
                ),
                rx.button(
                    rx.cond(
                        State.is_saving_maintenance,
                        rx.hstack(rx.spinner(size="1"), rx.text("Salvando..."), spacing="2"),
                        rx.hstack(rx.text("💾"), rx.text("Registrar Manutenção"), spacing="2"),
                    ),
                    on_click=State.save_maintenance_record,
                    disabled=State.is_saving_maintenance,
                    class_name="bg-[#1B5E20] text-white px-6 py-2.5 rounded-lg font-semibold hover:bg-[#2E7D32] transition-all mt-4"
                ),
                rx.cond(
                    State.maintenance_success_message != "",
                    rx.box(
                        rx.text(f"✅ {State.maintenance_success_message}", class_name="text-green-700"),
                        class_name="bg-green-50 border border-green-200 rounded-lg p-3 w-full"
                    ),
                ),
                # Lista de manutenções
                rx.cond(
                    State.maintenance_records.length() > 0,
                    rx.box(
                        rx.foreach(
                            State.maintenance_records,
                            lambda m: rx.box(
                                rx.hstack(
                                    rx.vstack(
                                        rx.text(m["equipment"], class_name="font-medium"),
                                        rx.badge(m["type"], class_name="bg-blue-100 text-blue-700"),
                                        spacing="1",
                                        align="start",
                                    ),
                                    rx.spacer(),
                                    rx.vstack(
                                        rx.text("Data: " + m["date"].to_string(), class_name="text-sm"),
                                        rx.text("Próxima: " + m["next_date"].to_string(), class_name="text-xs text-amber-600"),
                                        spacing="0",
                                        align="end",
                                    ),
                                    rx.button(
                                        "🗑️",
                                        on_click=lambda mid=m["id"]: State.delete_maintenance_record(mid),
                                        class_name="bg-red-50 text-red-600 px-2 py-1 rounded hover:bg-red-100 ml-2",
                                        size="1"
                                    ),
                                    width="100%",
                                ),
                                class_name="py-3 border-b border-gray-100 last:border-0"
                            )
                        ),
                        class_name="w-full mt-4"
                    ),
                ),
                spacing="3",
                width="100%",
            ),
            class_name="bg-white border border-gray-200 rounded-xl p-6 w-full"
        ),
        
        spacing="4",
        width="100%",
    )


def relatorios_tab() -> rx.Component:
    """Aba de Relatórios - Gráfico Levey-Jennings"""
    return rx.vstack(
        # Título
        rx.hstack(
            rx.text("📈", class_name="text-2xl"),
            rx.text("Relatórios Técnicos - Gráfico Levey-Jennings", class_name="text-xl font-bold text-[#1B5E20]"),
            spacing="2",
            align="center",
        ),
        
        rx.text(
            "O gráfico Levey-Jennings é essencial para auditorias, mostrando a variação dos resultados em relação aos Desvios Padrão.",
            class_name="text-gray-500 text-sm"
        ),
        
        # Seletores
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
                            class_name="w-full min-w-[200px]"
                        ),
                        spacing="1",
                    )
                ),
                rx.box(
                    rx.vstack(
                        rx.text("Período (dias)", class_name="text-sm font-medium text-gray-700"),
                        rx.select(
                            ["7", "15", "30", "60", "90"],
                            value=State.levey_jennings_period,
                            on_change=State.set_levey_jennings_period,
                            class_name="w-full"
                        ),
                        spacing="1",
                    )
                ),
                spacing="4",
            ),
            class_name="bg-white border border-gray-200 rounded-xl p-4 w-full"
        ),
        
        # Gráfico (representação visual simplificada)
        rx.cond(
            State.levey_jennings_data.length() > 0,
            rx.box(
                rx.vstack(
                    rx.text("📊 Gráfico de Controle", class_name="font-bold text-[#1B5E20]"),
                    
                    # Legenda
                    rx.hstack(
                        rx.hstack(
                            rx.box(class_name="w-3 h-3 bg-green-500 rounded"),
                            rx.text("±1 DP", class_name="text-xs"),
                            spacing="1",
                        ),
                        rx.hstack(
                            rx.box(class_name="w-3 h-3 bg-amber-500 rounded"),
                            rx.text("±2 DP", class_name="text-xs"),
                            spacing="1",
                        ),
                        rx.hstack(
                            rx.box(class_name="w-3 h-3 bg-red-500 rounded"),
                            rx.text("±3 DP", class_name="text-xs"),
                            spacing="1",
                        ),
                        spacing="4",
                    ),
                    
                    # Área do gráfico representativa
                    rx.box(
                        rx.vstack(
                            # Limites superiores
                            rx.box(class_name="w-full h-[1px] bg-red-300"),
                            rx.box(class_name="w-full h-[1px] bg-amber-300 mt-4"),
                            rx.box(class_name="w-full h-[1px] bg-green-300 mt-4"),
                            # Linha média
                            rx.box(class_name="w-full h-[2px] bg-[#1B5E20] mt-4"),
                            # Limites inferiores
                            rx.box(class_name="w-full h-[1px] bg-green-300 mt-4"),
                            rx.box(class_name="w-full h-[1px] bg-amber-300 mt-4"),
                            rx.box(class_name="w-full h-[1px] bg-red-300 mt-4"),
                            
                            # Pontos de dados
                            rx.hstack(
                                rx.foreach(
                                    State.levey_jennings_data,
                                    lambda d: rx.tooltip(
                                        rx.box(
                                            class_name="w-2 h-2 bg-blue-500 rounded-full"
                                        ),
                                        content=d["date"].to_string() + ": " + d["value"].to_string()
                                    )
                                ),
                                spacing="2",
                                justify="center",
                                class_name="absolute inset-x-0 top-1/2 transform -translate-y-1/2"
                            ),
                            
                            position="relative",
                            class_name="h-[200px]"
                        ),
                        class_name="bg-gray-50 rounded-lg p-4 w-full"
                    ),
                    
                    # Tabela de dados
                    rx.box(
                        rx.table.root(
                            rx.table.header(
                                rx.table.row(
                                    rx.table.column_header_cell("Data", class_name="bg-[#1B5E20] text-white"),
                                    rx.table.column_header_cell("Valor", class_name="bg-[#1B5E20] text-white"),
                                    rx.table.column_header_cell("Alvo", class_name="bg-[#1B5E20] text-white"),
                                    rx.table.column_header_cell("CV%", class_name="bg-[#1B5E20] text-white"),
                                )
                            ),
                            rx.table.body(
                                rx.foreach(
                                    State.levey_jennings_data,
                                    lambda d: rx.table.row(
                                        rx.table.cell(d["date"]),
                                        rx.table.cell(d["value"]),
                                        rx.table.cell(d["target"]),
                                        rx.table.cell(
                                            rx.text(
                                                d["cv"].to_string() + "%",
                                                class_name="text-gray-700 font-bold"
                                            )
                                        ),
                                    )
                                )
                            ),
                            width="100%",
                        ),
                        class_name="w-full overflow-x-auto mt-4"
                    ),
                    
                    spacing="3",
                    width="100%",
                ),
                class_name="bg-white border border-gray-200 rounded-xl p-6 w-full"
            ),
            rx.box(
                rx.text("Selecione um exame para visualizar o gráfico Levey-Jennings", class_name="text-gray-400 text-center py-8"),
                class_name="bg-white border border-gray-200 rounded-xl p-6 w-full"
            )
        ),
        
        spacing="4",
        width="100%",
    )


def importar_tab() -> rx.Component:
    """Aba de Importação de Planilhas"""
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
        # Título
        rx.hstack(
            rx.text("📥", class_name="text-2xl"),
            rx.text("Importação Inteligente de Planilhas", class_name="text-xl font-bold text-[#1B5E20]"),
            spacing="2",
            align="center",
        ),
        
        rx.text(
            "Importe sua planilha antiga (como 'pro in 5 otavio.xlsx') e traga os dados para o sistema automaticamente.",
            class_name="text-gray-500 text-sm"
        ),
        
        # Upload area
        rx.box(
            rx.upload(
                rx.vstack(
                    rx.cond(
                        State.excel_file_name != "",
                        rx.vstack(
                            rx.text("✅", class_name="text-4xl text-green-600"),
                            rx.text("Planilha Carregada", class_name="text-[#1B5E20] font-bold text-lg"),
                            rx.text(State.excel_file_name, class_name="text-green-600 text-sm truncate max-w-[200px]"),
                            spacing="2",
                            align="center",
                        ),
                        rx.vstack(
                            rx.html(excel_svg),
                            rx.text("Planilha Excel", class_name="text-[#1B5E20] font-bold text-lg mt-2"),
                            rx.text("Arraste ou clique para enviar .xlsx/.xls", class_name="text-gray-500 text-sm"),
                            spacing="1",
                            align="center",
                        ),
                    ),
                    justify="center",
                    align="center",
                    class_name="w-full h-full min-h-[200px] py-8"
                ),
                id="excel_upload",
                accept={
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"],
                    "application/vnd.ms-excel": [".xls"]
                },
                max_files=1,
                on_drop=State.handle_excel_upload(rx.upload_files(upload_id="excel_upload")),
                class_name="w-full h-full cursor-pointer"
            ),
            class_name="border-2 border-dashed border-[#4CAF50] rounded-2xl hover:border-[#1B5E20] hover:bg-green-50/30 transition-all max-w-xl mx-auto"
        ),
        
        # Botões de ação
        rx.hstack(
            rx.button(
                rx.cond(
                    State.is_analyzing_excel,
                    rx.hstack(rx.spinner(size="1"), rx.text("Analisando..."), spacing="2"),
                    rx.hstack(rx.text("🔍"), rx.text("Analisar Planilha"), spacing="2"),
                ),
                on_click=State.analyze_excel,
                disabled=~State.has_excel_file | State.is_analyzing_excel,
                class_name="bg-white border-2 border-[#1B5E20] text-[#1B5E20] px-6 py-2.5 rounded-lg font-semibold hover:bg-green-50 transition-all disabled:opacity-50"
            ),
            rx.button(
                rx.hstack(rx.text("📥"), rx.text("Importar para CQ"), spacing="2"),
                on_click=State.import_excel_to_qc,
                disabled=~State.excel_analyzed | State.is_analyzing_excel,
                class_name="bg-[#1B5E20] text-white px-6 py-2.5 rounded-lg font-semibold hover:bg-[#2E7D32] transition-all disabled:opacity-50"
            ),
            spacing="4",
            justify="center",
        ),
        
        # Mensagens
        rx.cond(
            State.excel_success_message != "",
            rx.box(
                rx.text(f"✅ {State.excel_success_message}", class_name="text-green-700"),
                class_name="bg-green-50 border border-green-200 rounded-lg p-3 w-full max-w-xl mx-auto"
            ),
        ),
        rx.cond(
            State.excel_error_message != "",
            rx.box(
                rx.text(f"❌ {State.excel_error_message}", class_name="text-red-700"),
                class_name="bg-red-50 border border-red-200 rounded-lg p-3 w-full max-w-xl mx-auto"
            ),
        ),
        
        # Preview dos dados
        rx.cond(
            State.excel_analyzed,
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.text("👁️", class_name="text-xl"),
                        rx.text("Preview da Planilha", class_name="font-bold text-[#1B5E20]"),
                        rx.spacer(),
                        rx.text(f"{State.excel_total_rows} linhas × {State.excel_total_columns} colunas", class_name="text-gray-500 text-sm"),
                        width="100%",
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
                                                class_name="bg-[#1B5E20] text-white font-semibold px-3 py-2 text-xs"
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
                                                    class_name="px-3 py-2 border-b border-gray-100 text-xs"
                                                )
                                            )
                                        )
                                    )
                                ),
                                width="100%",
                            ),
                            class_name="w-full overflow-x-auto"
                        ),
                        rx.text("Nenhum dado disponível", class_name="text-gray-400 py-4")
                    ),
                    spacing="3",
                    width="100%",
                ),
                class_name="bg-white border border-gray-200 rounded-xl p-4 w-full"
            ),
        ),
        
        spacing="4",
        width="100%",
        align="center",
    )


def proin_page() -> rx.Component:
    """Página principal do ProIn QC"""
    
    return rx.box(
        rx.vstack(
            # Header
            rx.box(
                rx.hstack(
                    rx.text("🔬", class_name="text-sm"),
                    rx.text(
                        "ProIn QC - Sistema de Controle de Qualidade",
                        class_name="text-[#1B5E20] text-sm font-medium"
                    ),
                    spacing="2",
                    align="center",
                ),
                class_name="bg-white border border-gray-200 px-4 py-2 rounded-full shadow-sm"
            ),
            
            # Título
            rx.text(
                "Controle de Qualidade",
                class_name="text-[#1B5E20] text-4xl font-bold mt-4"
            ),
            
            rx.text(
                "Sistema completo para gestão de qualidade laboratorial",
                class_name="text-gray-600 text-lg"
            ),
            
            # Abas de navegação
            rx.box(
                rx.hstack(
                    tab_button("Dashboard", "📊", "dashboard"),
                    tab_button("Registro CQ", "📝", "registro"),
                    tab_button("Reagentes", "🧪", "reagentes"),
                    tab_button("Relatórios", "📈", "relatorios"),
                    tab_button("Importar", "📥", "importar"),
                    spacing="2",
                    wrap="wrap",
                    justify="center",
                ),
                class_name="w-full mt-6"
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
                class_name="w-full mt-6"
            ),
            
            spacing="0",
            align="center",
            width="100%",
            class_name="py-6"
        ),
        width="100%",
    )
