"""
Chart components for Biodiagnóstico App - Centro de Comando Operacional
Widgets estratégicos para Business Intelligence e Gestão por Exceção
"""
import reflex as rx
from ..state import State
from ..styles import Color, Design, CARD_STYLE


# ========================================
# WIDGET 1: KPI FINANCEIRO - Total Loss Value
# ========================================

def financial_kpi_widget() -> rx.Component:
    """Card de destaque com o valor total de perdas financeiras"""
    return rx.cond(
        State.has_analysis,
        rx.box(
            rx.vstack(
                # Header
                rx.hstack(
                    rx.icon("alert-triangle", size=24, color=Color.TEXT_SECONDARY),
                    rx.text(
                        "Divergência Total Detectada",
                        class_name="text-gray-600 font-semibold text-sm uppercase tracking-wide"
                    ),
                    spacing="2",
                    align="center",
                    width="100%"
                ),

                # Valor principal
                rx.text(
                    State.formatted_total_loss_value,
                    class_name=rx.match(
                        State.loss_value_color,
                        ("green", "text-green-600 text-5xl font-bold"),
                        ("yellow", "text-yellow-600 text-5xl font-bold"),
                        ("red", "text-red-600 text-5xl font-bold"),
                        "text-gray-600 text-5xl font-bold"
                    ),
                ),

                # Status badge
                rx.box(
                    rx.text(
                        State.loss_value_status,
                        class_name=rx.match(
                            State.loss_value_color,
                            ("green", "text-green-700 text-sm font-medium"),
                            ("yellow", "text-yellow-700 text-sm font-medium"),
                            ("red", "text-red-700 text-sm font-medium"),
                            "text-gray-700 text-sm font-medium"
                        ),
                    ),
                    class_name=rx.match(
                        State.loss_value_color,
                        ("green", "bg-green-100 px-4 py-2 rounded-full"),
                        ("yellow", "bg-yellow-100 px-4 py-2 rounded-full"),
                        ("red", "bg-red-100 px-4 py-2 rounded-full"),
                        "bg-gray-100 px-4 py-2 rounded-full"
                    ),
                ),

                spacing="4",
                align="center",
                width="100%",
                class_name="py-6"
            ),
            class_name="bg-white rounded-2xl shadow-lg border border-gray-200 p-6 hover:shadow-xl transition-all"
        ),
    )


# ========================================
# WIDGET 2: TOP 5 OFENSORES
# ========================================

def top_offenders_widget() -> rx.Component:
    """Tabela dos top 5 exames com mais divergências"""
    return rx.cond(
        State.has_analysis & (State.top_divergence_exams.length() > 0),
        rx.box(
            rx.vstack(
                # Header
                rx.hstack(
                    rx.icon("trending-down", size=20, color=Color.ERROR),
                    rx.text(
                        "Top 5 Exames com Divergências",
                        class_name="text-gray-800 font-bold text-lg"
                    ),
                    spacing="2",
                    width="100%"
                ),

                # Tabela minimalista
                rx.box(
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell("Exame"),
                                rx.table.column_header_cell("Total Divergente", class_name="text-right"),
                            ),
                        ),
                        rx.table.body(
                            rx.foreach(
                                State.top_divergence_exams,
                                lambda item: rx.table.row(
                                    rx.table.cell(
                                        rx.text(item["exam"], class_name="font-medium text-gray-700")
                                    ),
                                    rx.table.cell(
                                        rx.text(item["total"], class_name="text-red-600 font-semibold text-right")
                                    ),
                                    class_name="hover:bg-gray-50"
                                )
                            )
                        ),
                        variant="surface",
                        class_name="w-full"
                    ),
                    class_name="w-full"
                ),

                spacing="4",
                width="100%"
            ),
            class_name="bg-white rounded-2xl shadow-md border border-gray-200 p-6"
        ),
    )


# ========================================
# WIDGET 3: GRÁFICO FUNIL DE PERDA
# ========================================

def loss_funnel_chart() -> rx.Component:
    """Gráfico de barras mostrando o funil de perdas"""
    return rx.cond(
        State.has_analysis,
        rx.box(
            rx.vstack(
                # Header
                rx.hstack(
                    rx.icon("filter", size=20, color=Color.PRIMARY),
                    rx.text(
                        "Funil de Perda Financeira",
                        class_name="text-gray-800 font-bold text-lg"
                    ),
                    spacing="2",
                    width="100%"
                ),

                # Gráfico usando recharts
                rx.recharts.bar_chart(
                    rx.recharts.bar(
                        data_key="value",
                        fill="#4CAF50",
                    ),
                    rx.recharts.x_axis(data_key="stage", class_name="text-xs"),
                    rx.recharts.y_axis(),
                    rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
                    rx.recharts.graphing_tooltip(),
                    data=State.loss_funnel_data,
                    width="100%",
                    height=300,
                ),

                spacing="4",
                width="100%"
            ),
            class_name="bg-white rounded-2xl shadow-md border border-gray-200 p-6"
        ),
    )


# ========================================
# WIDGET 4: ALERTAS CRÍTICOS (Feed)
# ========================================

def critical_alerts_feed() -> rx.Component:
    """Feed de alertas críticos de QC que exigem ação imediata"""
    return rx.cond(
        State.critical_alerts.length() > 0,
        rx.box(
            rx.vstack(
                # Header
                rx.hstack(
                    rx.icon("bell", size=20, color=Color.ERROR),
                    rx.text(
                        "Alertas Críticos - QC",
                        class_name="text-gray-800 font-bold text-lg"
                    ),
                    rx.badge(
                        State.critical_alerts.length(),
                        color_scheme="red",
                        size="2"
                    ),
                    spacing="2",
                    width="100%",
                    justify="between"
                ),

                # Lista de alertas
                rx.box(
                    rx.foreach(
                        State.critical_alerts,
                        lambda alert: rx.box(
                            rx.hstack(
                                rx.cond(
                                    alert["severity"] == "high",
                                    rx.icon("triangle-alert", size=20, color=Color.ERROR),
                                    rx.icon("alert-circle", size=20, color=Color.WARNING)
                                ),
                                rx.vstack(
                                    rx.text(
                                        alert["exam"],
                                        class_name="font-semibold text-gray-800 text-sm"
                                    ),
                                    rx.text(
                                        alert["message"],
                                        class_name="text-gray-600 text-xs"
                                    ),
                                    spacing="1",
                                    align="start",
                                    flex="1"
                                ),
                                spacing="3",
                                align="start",
                                width="100%"
                            ),
                            class_name=rx.cond(
                                alert["severity"] == "high",
                                "bg-red-50 border-l-4 border-red-500 p-3 rounded",
                                "bg-yellow-50 border-l-4 border-yellow-500 p-3 rounded"
                            ),
                        )
                    ),
                    class_name="space-y-2 max-h-96 overflow-y-auto"
                ),

                spacing="4",
                width="100%"
            ),
            class_name="bg-white rounded-2xl shadow-md border border-gray-200 p-6"
        ),
        # Placeholder quando não há alertas
        rx.box(
            rx.vstack(
                rx.icon("check-circle", size=48, color=Color.SUCCESS),
                rx.text(
                    "Nenhum alerta crítico",
                    class_name="text-gray-600 font-medium"
                ),
                spacing="3",
                align="center",
                class_name="py-8"
            ),
            class_name="bg-white rounded-2xl shadow-md border border-green-200 p-6"
        )
    )


# ========================================
# WIDGET 5: MINI-GRÁFICOS DE TENDÊNCIA (Sparklines)
# ========================================

def sparklines_widget() -> rx.Component:
    """Mini-gráficos de tendência para os 3 analitos mais críticos"""
    return rx.cond(
        State.top_critical_analytes.length() > 0,
        rx.box(
            rx.vstack(
                # Header
                rx.hstack(
                    rx.icon("activity", size=20, color=Color.PRIMARY),
                    rx.text(
                        "Tendência - Analitos Críticos (7 dias)",
                        class_name="text-gray-800 font-bold text-lg"
                    ),
                    spacing="2",
                    width="100%"
                ),

                # Cards de sparklines
                rx.foreach(
                    State.top_critical_analytes,
                    lambda exam: rx.box(
                        rx.vstack(
                            rx.text(exam, class_name="font-semibold text-gray-700 text-sm"),
                            rx.recharts.line_chart(
                                rx.recharts.line(
                                    data_key="value",
                                    stroke=Color.PRIMARY,
                                    stroke_width=2,
                                    dot=False,
                                ),
                                data=State.sparkline_data[exam],
                                width="100%",
                                height=60,
                                margin={"top": 5, "right": 5, "left": 5, "bottom": 5}
                            ),
                            spacing="2",
                            width="100%"
                        ),
                        class_name="bg-gray-50 p-4 rounded-xl"
                    )
                ),

                spacing="3",
                width="100%"
            ),
            class_name="bg-white rounded-2xl shadow-md border border-gray-200 p-6"
        ),
    )


# ========================================
# WIDGET 6: GRID DE STATUS DOS EQUIPAMENTOS
# ========================================

def equipment_status_grid() -> rx.Component:
    """Grid visual mostrando status de cada equipamento"""
    return rx.cond(
        State.equipment_status_grid.length() > 0,
        rx.box(
            rx.vstack(
                # Header
                rx.hstack(
                    rx.icon("cpu", size=20, color=Color.PRIMARY),
                    rx.text(
                        "Status dos Equipamentos",
                        class_name="text-gray-800 font-bold text-lg"
                    ),
                    spacing="2",
                    width="100%"
                ),

                # Grid de equipamentos
                rx.grid(
                    rx.foreach(
                        State.equipment_status_grid,
                        lambda eq: rx.box(
                            rx.vstack(
                                rx.text(
                                    eq["name"],
                                    class_name="font-medium text-gray-700 text-sm text-center"
                                ),
                                rx.box(
                                    class_name=rx.match(
                                        eq["overall_status"],
                                        ("green", "w-12 h-12 rounded-full bg-green-500 border-4 border-green-200"),
                                        ("yellow", "w-12 h-12 rounded-full bg-yellow-500 border-4 border-yellow-200"),
                                        ("red", "w-12 h-12 rounded-full bg-red-500 border-4 border-red-200"),
                                        "w-12 h-12 rounded-full bg-gray-500 border-4 border-gray-200"
                                    ),
                                ),
                                spacing="2",
                                align="center"
                            ),
                            class_name="bg-gray-50 p-4 rounded-xl hover:bg-gray-100 transition-all"
                        )
                    ),
                    columns=["2", "3", "4"],  # 2 em mobile, 3 em tablet, 4 em desktop
                    spacing="4",
                    width="100%"
                ),

                # Legenda
                rx.hstack(
                    rx.hstack(
                        rx.box(class_name="w-3 h-3 rounded-full bg-green-500"),
                        rx.text("OK", class_name="text-xs text-gray-600"),
                        spacing="1"
                    ),
                    rx.hstack(
                        rx.box(class_name="w-3 h-3 rounded-full bg-yellow-500"),
                        rx.text("Atenção", class_name="text-xs text-gray-600"),
                        spacing="1"
                    ),
                    rx.hstack(
                        rx.box(class_name="w-3 h-3 rounded-full bg-red-500"),
                        rx.text("Crítico", class_name="text-xs text-gray-600"),
                        spacing="1"
                    ),
                    spacing="4",
                    justify="center",
                    width="100%",
                    class_name="pt-2"
                ),

                spacing="4",
                width="100%"
            ),
            class_name="bg-white rounded-2xl shadow-md border border-gray-200 p-6"
        ),
    )


# ========================================
# WIDGET 7: SEMÁFORO DE REAGENTES
# ========================================

def reagent_traffic_light() -> rx.Component:
    """Lista de reagentes com status de validade em formato de semáforo"""
    return rx.cond(
        State.lots_expiring_soon.length() > 0,
        rx.box(
            rx.vstack(
                # Header
                rx.hstack(
                    rx.icon("flask-conical", size=20, color=Color.PRIMARY),
                    rx.text(
                        "Reagentes - Controle de Validade",
                        class_name="text-gray-800 font-bold text-lg"
                    ),
                    spacing="2",
                    width="100%"
                ),

                # Lista de reagentes
                rx.box(
                    rx.foreach(
                        State.lots_expiring_soon,
                        lambda lot: rx.hstack(
                            rx.text(lot["badge"], class_name="text-2xl"),
                            rx.vstack(
                                rx.text(
                                    lot["name"],
                                    class_name="font-semibold text-gray-800 text-sm"
                                ),
                                rx.text(
                                    f"Lote: {lot['lot_number']} | Vence: {lot['expiry_date']} ({lot['days_left']} dias)",
                                    class_name="text-gray-600 text-xs"
                                ),
                                spacing="1",
                                align="start",
                                flex="1"
                            ),
                            spacing="3",
                            align="center",
                            width="100%",
                            class_name="p-3 rounded-lg hover:bg-gray-50"
                        )
                    ),
                    class_name="space-y-1 max-h-80 overflow-y-auto"
                ),

                spacing="4",
                width="100%"
            ),
            class_name="bg-white rounded-2xl shadow-md border border-gray-200 p-6"
        ),
        # Placeholder
        rx.box(
            rx.vstack(
                rx.icon("check-circle", size=48, color=Color.SUCCESS),
                rx.text(
                    "Todos os reagentes com validade OK",
                    class_name="text-gray-600 font-medium"
                ),
                spacing="3",
                align="center",
                class_name="py-8"
            ),
            class_name="bg-white rounded-2xl shadow-md border border-green-200 p-6"
        )
    )


# ========================================
# WIDGET 8: AGENDA DE MANUTENÇÕES
# ========================================

def maintenance_timeline() -> rx.Component:
    """Timeline das manutenções previstas para os próximos 7 dias"""
    return rx.cond(
        State.upcoming_maintenances.length() > 0,
        rx.box(
            rx.vstack(
                # Header
                rx.hstack(
                    rx.icon("wrench", size=20, color=Color.PRIMARY),
                    rx.text(
                        "Manutenções - Próximos 7 Dias",
                        class_name="text-gray-800 font-bold text-lg"
                    ),
                    spacing="2",
                    width="100%"
                ),

                # Lista de manutenções
                rx.box(
                    rx.foreach(
                        State.upcoming_maintenances,
                        lambda maint: rx.hstack(
                            rx.box(
                                rx.text(
                                    maint["days_until"],
                                    class_name="text-white font-bold text-sm"
                                ),
                                class_name=rx.cond(
                                    maint["days_until"] == 0,
                                    "bg-red-500 w-12 h-12 rounded-full flex items-center justify-center",
                                    "bg-blue-500 w-12 h-12 rounded-full flex items-center justify-center"
                                )
                            ),
                            rx.vstack(
                                rx.text(
                                    maint["equipment"],
                                    class_name="font-semibold text-gray-800 text-sm"
                                ),
                                rx.text(
                                    f"{maint['type']} - {maint['date']}",
                                    class_name="text-gray-600 text-xs"
                                ),
                                spacing="1",
                                align="start",
                                flex="1"
                            ),
                            spacing="3",
                            align="center",
                            width="100%",
                            class_name="p-3 rounded-lg hover:bg-gray-50"
                        )
                    ),
                    class_name="space-y-2"
                ),

                spacing="4",
                width="100%"
            ),
            class_name="bg-white rounded-2xl shadow-md border border-gray-200 p-6"
        ),
        # Placeholder
        rx.box(
            rx.vstack(
                rx.icon("calendar-check", size=48, color=Color.SUCCESS),
                rx.text(
                    "Nenhuma manutenção prevista nos próximos 7 dias",
                    class_name="text-gray-600 font-medium text-center"
                ),
                spacing="3",
                align="center",
                class_name="py-8"
            ),
            class_name="bg-white rounded-2xl shadow-md border border-green-200 p-6"
        )
    )


# ========================================
# WIDGET 9: HISTÓRICO DE VOLUME
# ========================================

def volume_history_chart() -> rx.Component:
    """Gráfico de barras mostrando volume de pacientes nos últimos 6 meses"""
    return rx.box(
        rx.vstack(
            # Header
            rx.hstack(
                rx.icon("bar-chart-3", size=20, color=Color.PRIMARY),
                rx.text(
                    "Volume de Pacientes - 6 Meses",
                    class_name="text-gray-800 font-bold text-lg"
                ),
                spacing="2",
                width="100%"
            ),

            # Gráfico
            rx.recharts.bar_chart(
                rx.recharts.bar(
                    data_key="volume",
                    fill=Color.PRIMARY,
                    radius=[8, 8, 0, 0],
                ),
                rx.recharts.x_axis(data_key="month", class_name="text-xs"),
                rx.recharts.y_axis(),
                rx.recharts.cartesian_grid(stroke_dasharray="3 3", opacity=0.3),
                rx.recharts.graphing_tooltip(),
                data=State.volume_history_6months,
                width="100%",
                height=250,
            ),

            spacing="4",
            width="100%"
        ),
        class_name="bg-white rounded-2xl shadow-md border border-gray-200 p-6"
    )


# ========================================
# WIDGET 10: QUICK ACTIONS
# ========================================

def quick_actions_widget() -> rx.Component:
    """Botões de atalho para ações rotineiras"""
    return rx.box(
        rx.vstack(
            # Header
            rx.hstack(
                rx.icon("zap", size=20, color=Color.PRIMARY),
                rx.text(
                    "Ações Rápidas",
                    class_name="text-gray-800 font-bold text-lg"
                ),
                spacing="2",
                width="100%"
            ),

            # Botões
            rx.vstack(
                rx.button(
                    rx.icon("printer", size=18),
                    "Relatório QC Hoje",
                    on_click=lambda: State.set_page("proin"),
                    class_name="w-full bg-green-500 hover:bg-green-600 text-white font-semibold py-3 px-4 rounded-xl flex items-center justify-start gap-3 transition-all"
                ),
                rx.button(
                    rx.icon("download", size=18),
                    "Exportar XML",
                    on_click=lambda: State.set_page("conversor"),
                    class_name="w-full bg-blue-500 hover:bg-blue-600 text-white font-semibold py-3 px-4 rounded-xl flex items-center justify-start gap-3 transition-all"
                ),
                rx.button(
                    rx.icon("wrench", size=18),
                    "Registrar Manutenção",
                    on_click=lambda: State.set_page("proin"),
                    class_name="w-full bg-purple-500 hover:bg-purple-600 text-white font-semibold py-3 px-4 rounded-xl flex items-center justify-start gap-3 transition-all"
                ),
                spacing="3",
                width="100%"
            ),

            spacing="4",
            width="100%"
        ),
        class_name="bg-white rounded-2xl shadow-md border border-gray-200 p-6"
    )


# ========================================
# COMPONENTES LEGADOS (mantidos para compatibilidade)
# ========================================

def divergences_chart() -> rx.Component:
    """Gráfico de divergências (legado)"""
    return loss_funnel_chart()


def summary_pie_chart() -> rx.Component:
    """Gráfico de pizza do breakdown (legado)"""
    return rx.cond(
        State.has_analysis,
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.text("🥧", class_name="text-2xl"),
                    rx.text(
                        "Composição da Diferença",
                        class_name="text-green-800 font-bold text-lg"
                    ),
                    spacing="3",
                    align="center",
                ),
                # Barras horizontais simples como alternativa
                rx.vstack(
                    # Pacientes faltantes
                    rx.box(
                        rx.hstack(
                            rx.text("Pacientes Faltantes", class_name="text-sm text-gray-600 w-40"),
                            rx.box(
                                class_name="h-6 bg-green-500 rounded-r-full transition-all w-1/3",
                            ),
                            rx.text(
                                State.formatted_missing_patients_total,
                                class_name="text-sm text-gray-700 ml-2 w-32"
                            ),
                            align="center",
                            width="100%",
                        ),
                    ),
                    # Exames faltantes
                    rx.box(
                        rx.hstack(
                            rx.text("Exames Faltantes", class_name="text-sm text-gray-600 w-40"),
                            rx.box(
                                class_name="h-6 bg-lime-500 rounded-r-full transition-all w-1/3",
                            ),
                            rx.text(
                                State.formatted_missing_exams_total,
                                class_name="text-sm text-gray-700 ml-2 w-32"
                            ),
                            align="center",
                            width="100%",
                        ),
                    ),
                    # Divergências
                    rx.box(
                        rx.hstack(
                            rx.text("Divergências", class_name="text-sm text-gray-600 w-40"),
                            rx.box(
                                class_name="h-6 bg-yellow-500 rounded-r-full transition-all w-1/3",
                            ),
                            rx.text(
                                State.formatted_divergences_total,
                                class_name="text-sm text-gray-700 ml-2 w-32"
                            ),
                            align="center",
                            width="100%",
                        ),
                    ),
                    spacing="3",
                    width="100%",
                    class_name="bg-gray-50 p-4 rounded-xl"
                ),
                spacing="4",
                width="100%",
            ),
            class_name="bg-white p-6 rounded-2xl shadow-lg border border-green-100 mt-6"
        ),
    )
