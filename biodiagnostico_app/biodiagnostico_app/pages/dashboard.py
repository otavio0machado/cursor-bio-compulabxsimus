"""
Dashboard - Centro de Comando Operacional
Business Intelligence & Gestão por Exceção
"""
import reflex as rx
from ..state import State
from ..styles import Color
from ..components import ui
from ..components.charts import (
    financial_kpi_widget,
    top_offenders_widget,
    loss_funnel_chart,
    critical_alerts_feed,
    sparklines_widget,
    equipment_status_grid,
    reagent_traffic_light,
    maintenance_timeline,
    volume_history_chart,
    quick_actions_widget,
)


def dashboard_header() -> rx.Component:
    """Header do dashboard com informações contextuais"""
    return rx.box(
        rx.vstack(
            # Título principal
            rx.hstack(
                rx.icon("layout-dashboard", size=32, color=Color.DEEP),
                rx.vstack(
                    rx.text(
                        "Centro de Comando Operacional",
                        class_name="text-[#1B5E20] text-4xl font-bold"
                    ),
                    rx.text(
                        "Business Intelligence & Gestão por Exceção",
                        class_name="text-gray-600 text-lg"
                    ),
                    spacing="1",
                    align="start"
                ),
                spacing="4",
                align="center"
            ),

            # Badge de certificação
            rx.hstack(
                rx.text("💎", class_name="text-lg"),
                rx.text(
                    "Certificação PNCQ Diamante",
                    class_name="text-[#1B5E20] text-sm font-medium"
                ),
                spacing="2",
                align="center",
                class_name="bg-white border border-gray-200 px-4 py-2 rounded-full shadow-sm"
            ),

            spacing="4",
            align="start",
            width="100%",
            class_name="py-8"
        ),
        width="100%"
    )


def dashboard_page() -> rx.Component:
    """Página Dashboard Principal - Centro de Comando Operacional"""
    return rx.box(
        rx.vstack(
            # Header
            dashboard_header(),

            # ========================================
            # SECTION 1: FINANCIAL & STRATEGIC WIDGETS
            # ========================================
            rx.box(
                rx.vstack(
                    rx.text(
                        "💰 Financeiro & Estratégia",
                        class_name="text-gray-700 font-bold text-xl mb-4"
                    ),

                    # Grid financeiro - 1 coluna em mobile, 3 em desktop
                    rx.grid(
                        # Widget 1: KPI Financeiro
                        financial_kpi_widget(),

                        # Widget 2: Top 5 Ofensores
                        top_offenders_widget(),

                        # Widget 3: Funil de Perda
                        loss_funnel_chart(),

                        columns=["1", "1", "3"],  # 1 em mobile/tablet, 3 em desktop
                        spacing="6",
                        width="100%",
                        class_name="animate-fade-in-up"
                    ),

                    spacing="4",
                    width="100%"
                ),
                class_name="mb-12"
            ),

            # ========================================
            # SECTION 2: OPERATIONAL & QUALITY CONTROL
            # ========================================
            rx.box(
                rx.vstack(
                    rx.text(
                        "🔬 Qualidade & Operações",
                        class_name="text-gray-700 font-bold text-xl mb-4"
                    ),

                    # Grid de QC - 2 colunas em desktop
                    rx.grid(
                        # Widget 4: Alertas Críticos
                        critical_alerts_feed(),

                        # Widget 5: Sparklines (Tendências)
                        sparklines_widget(),

                        columns=["1", "1", "2"],  # 1 em mobile/tablet, 2 em desktop
                        spacing="6",
                        width="100%",
                        class_name="animate-fade-in-up delay-100"
                    ),

                    # Widget 6: Status Grid dos Equipamentos (full width)
                    rx.box(
                        equipment_status_grid(),
                        width="100%",
                        class_name="mt-6 animate-fade-in-up delay-200"
                    ),

                    spacing="4",
                    width="100%"
                ),
                class_name="mb-12"
            ),

            # ========================================
            # SECTION 3: INVENTORY & LOGISTICS
            # ========================================
            rx.box(
                rx.vstack(
                    rx.text(
                        "📦 Inventário & Logística",
                        class_name="text-gray-700 font-bold text-xl mb-4"
                    ),

                    # Grid de inventário - 2 colunas em desktop
                    rx.grid(
                        # Widget 7: Semáforo de Reagentes
                        reagent_traffic_light(),

                        # Widget 8: Agenda de Manutenções
                        maintenance_timeline(),

                        columns=["1", "1", "2"],  # 1 em mobile/tablet, 2 em desktop
                        spacing="6",
                        width="100%",
                        class_name="animate-fade-in-up delay-100"
                    ),

                    spacing="4",
                    width="100%"
                ),
                class_name="mb-12"
            ),

            # ========================================
            # SECTION 4: MANAGEMENT & UTILITIES
            # ========================================
            rx.box(
                rx.vstack(
                    rx.text(
                        "📊 Gestão & Análises",
                        class_name="text-gray-700 font-bold text-xl mb-4"
                    ),

                    # Grid de gestão - 2 colunas em desktop
                    rx.grid(
                        # Widget 9: Histórico de Volume
                        volume_history_chart(),

                        # Widget 10: Quick Actions
                        quick_actions_widget(),

                        columns=["1", "1", "2"],  # 1 em mobile/tablet, 2 em desktop
                        spacing="6",
                        width="100%",
                        class_name="animate-fade-in-up delay-100"
                    ),

                    spacing="4",
                    width="100%"
                ),
                class_name="mb-12"
            ),

            # ========================================
            # LEGACY SECTION: ACESSO RÁPIDO
            # (Mantido para compatibilidade)
            # ========================================
            rx.divider(class_name="my-12"),

            rx.box(
                rx.vstack(
                    rx.text(
                        "🚀 Acesso Rápido às Ferramentas",
                        class_name="text-gray-700 font-bold text-xl mb-6"
                    ),

                    rx.grid(
                        # Conversor PDF
                        ui.card(
                            rx.vstack(
                                rx.box(
                                    rx.icon("file-text", size=32, color=f"var(--c-blue-600)"),
                                    class_name="text-blue-600 bg-blue-50 p-4 rounded-2xl mb-2"
                                ),
                                ui.heading("Conversor PDF", level=3),
                                ui.text("Extração e padronização de relatórios do Compulab e Simus.", size="body"),
                                align_items="start",
                                spacing="2"
                            ),
                            on_click=lambda: State.set_page("conversor"),
                            class_name="cursor-pointer hover:shadow-lg transition-all duration-300 h-full group border-transparent hover:border-blue-200"
                        ),

                        # Análise Cruzada
                        ui.card(
                            rx.vstack(
                                rx.box(
                                    rx.icon("bar-chart-2", size=32, color=f"var(--c-green-600)"),
                                    class_name="text-green-600 bg-green-50 p-4 rounded-2xl mb-2"
                                ),
                                ui.heading("Análise Cruzada", level=3),
                                ui.text("Identificação de divergências financeiras e exames faltantes.", size="body"),
                                align_items="start",
                                spacing="2"
                            ),
                            on_click=lambda: State.set_page("analise"),
                            class_name="cursor-pointer hover:shadow-lg transition-all duration-300 h-full group border-transparent hover:border-green-200"
                        ),

                        # Gestão da Qualidade
                        ui.card(
                            rx.vstack(
                                rx.box(
                                    rx.icon("microscope", size=32, color=f"var(--c-purple-600)"),
                                    class_name="text-purple-600 bg-purple-50 p-4 rounded-2xl mb-2"
                                ),
                                ui.heading("Gestão da Qualidade", level=3),
                                ui.text("Controle ProIn, gráficos Levey-Jennings e gestão de reagentes.", size="body"),
                                align_items="start",
                                spacing="2"
                            ),
                            on_click=lambda: State.set_page("proin"),
                            class_name="cursor-pointer hover:shadow-lg transition-all duration-300 h-full group border-transparent hover:border-purple-200"
                        ),

                        columns=["1", "2", "3"],  # 1 em mobile, 2 em tablet, 3 em desktop
                        spacing="6",
                        width="100%",
                        class_name="animate-fade-in-up delay-200"
                    ),

                    spacing="4",
                    width="100%"
                ),
                class_name="mb-12"
            ),

            # Footer info
            rx.box(
                rx.text(
                    "📊 Dashboard atualizado em tempo real | Sistema desenvolvido com Reflex Framework",
                    class_name="text-gray-500 text-sm text-center"
                ),
                class_name="py-8"
            ),

            width="100%",
            padding_bottom="4rem"
        ),
        width="100%"
    )
