import reflex as rx
from ..state import State
from ..styles import Color
from ..components import ui

def quick_access_card(title: str, description: str, icon: str, page: str, color: str) -> rx.Component:
    """Card de acesso rápido padronizado"""
    return ui.card(
        rx.vstack(
            rx.box(
                rx.icon(icon, size=32, color=f"var(--c-{color}-600)"),
                class_name=f"text-{color}-600 bg-{color}-50 p-4 rounded-2xl mb-2"
            ),
            ui.heading(title, level=3),
            ui.text(description, size="body"),
            align_items="start",
            spacing="2"
        ),
        on_click=lambda: State.set_page(page),
        class_name="cursor-pointer hover:shadow-lg transition-all duration-300 h-full group border-transparent hover:border-green-200"
    )

def dashboard_page() -> rx.Component:
    """Página Dashboard Principal - Refatorada com UI Kit"""
    return rx.box(
        rx.vstack(
            # Welcome Banner
            rx.box(
                ui.animated_heading("Bem-vindo de volta", level=1),
                class_name="py-8 w-full flex justify-center"
            ),
            
            # === NOVA SECTION: Scoreboard & Top Offenders ===
            rx.grid(
                # Coluna 1: Financial & Stats combinados
                rx.vstack(
                    # Financial Card (Destaque)
                    rx.box(
                        rx.hstack(
                            rx.vstack(
                                rx.text("Faturamento Processado (Estimado)", class_name="text-sm font-medium text-gray-500"),
                                rx.heading(State.formatted_compulab_total, size={"initial": "6", "sm": "8"}, class_name="text-gray-900"),
                                rx.hstack(
                                    rx.cond(
                                        State.financial_growth_day >= 0,
                                        rx.icon("trending-up", size=16, class_name="text-green-600"),
                                        rx.icon("trending-down", size=16, class_name="text-red-600")
                                    ),
                                    rx.text(
                                        f"{State.financial_growth_day:.1f}% vs dia anterior", 
                                        class_name=rx.cond(State.financial_growth_day >= 0, "text-green-600 text-sm font-medium", "text-red-600 text-sm font-medium")
                                    ),
                                    align="center",
                                    spacing="2"
                                ),
                                align="start",
                                spacing="1"
                            ),
                            rx.spacer(),
                            rx.box(
                                rx.icon("dollar-sign", size=32, class_name="text-green-700"),
                                class_name="bg-green-100 p-3 rounded-xl"
                            ),
                            width="100%",
                            align="center"
                        ),
                        class_name="bg-white p-4 md:p-6 rounded-2xl shadow-sm border border-gray-100 w-full hover:shadow-md transition-shadow"
                    ),
                    
                    # Mini Stats Grid
                    rx.grid(
                        ui.stat_card(
                            "Aprovação CQ", 
                            f"{State.dashboard_approval_rate}%", 
                            "circle-check", 
                            "success", 
                            "Média mensal"
                        ),
                        ui.stat_card(
                            "Manutenções", 
                            f"{State.dashboard_pending_maintenances}", 
                            "wrench", 
                            "warning", 
                            "Pendentes"
                        ),
                        ui.stat_card(
                            "Pacientes", 
                            f"{State.total_patients_count}", 
                            "users", 
                            "brand", 
                            "Processados"
                        ),
                        ui.stat_card(
                            "Divergências", 
                            f"{State.divergences_count}", 
                            "triangle-alert", 
                            "error", 
                            "Detectadas"
                        ),
                        columns={"initial": "1", "sm": "2"},
                        spacing="4",
                        width="100%"
                    ),
                    width="100%",
                    spacing="4"
                ),
                
                # Coluna 2: Top Offenders (Lista de problemas recorrentes)
                rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.icon("octagon-alert", size=20, class_name="text-red-500"),
                            ui.heading("Top Ofensores", level=3, font_size="1.1rem"),
                            rx.spacer(),
                            rx.badge("Divergências", color_scheme="red", variant="soft"),
                            align="center",
                            width="100%",
                            class_name="mb-4"
                        ),
                        rx.cond(
                            State.top_offenders.length() > 0,
                            rx.vstack(
                                rx.foreach(
                                    State.top_offenders,
                                    lambda item: rx.hstack(
                                        rx.box(
                                            rx.text(item["name"], class_name="font-medium text-gray-700 text-sm truncate"),
                                            class_name="flex-1"
                                        ),
                                        rx.text(f"{item['count']}x", class_name="text-xs font-bold bg-red-100 text-red-700 px-2 py-1 rounded-md"),
                                        width="100%",
                                        align="center",
                                        class_name="p-3 bg-gray-50 rounded-lg border border-transparent hover:border-gray-200 transition-colors"
                                    )
                                ),
                                spacing="2",
                                width="100%"
                            ),
                            rx.center(
                                rx.vstack(
                                    rx.icon("circle-check", size=40, class_name="text-green-300"),
                                    rx.text("Nenhum ofensor detectado", class_name="text-gray-400 text-sm"),
                                    align="center",
                                    spacing="2"
                                ),
                                class_name="h-40 w-full bg-gray-50 rounded-xl border-2 border-dashed border-gray-100"
                            )
                        ),
                        width="100%",
                        height="100%"
                    ),
                    class_name="bg-white p-4 md:p-6 rounded-2xl shadow-sm border border-gray-100 h-full"
                ),
                
                columns={"initial": "1", "md": "2"},
                spacing="6",
                width="100%",
                class_name="mb-10 max-w-6xl mx-auto w-full"
            ),
            
            rx.divider(class_name="mb-10 max-w-6xl mx-auto"),
            
            # Quick Access Section
            ui.heading("Acesso Rápido", level=2, class_name="mb-6 max-w-6xl mx-auto w-full text-center"),
            rx.grid(
                quick_access_card(
                    "Conversor PDF",
                    "Extração e padronização de relatórios do Compulab e Simus.",
                    "file-text",
                    "conversor",
                    "blue"
                ),
                quick_access_card(
                    "Análise Cruzada",
                    "Identificação de divergências financeiras e exames faltantes.",
                    "chart-bar",
                    "analise",
                    "green"
                ),
                quick_access_card(
                    "Gestão da Qualidade",
                    "Controle ProIn, gráficos Levey-Jennings e gestão de reagentes.",
                    "microscope",
                    "proin",
                    "purple"
                ),
                columns={"initial": "1", "md": "3"},
                spacing="6",
                width="100%",
                class_name="mb-12 animate-fade-in-up delay-100 max-w-6xl mx-auto w-full"
            ),

            width="100%",
            align="center",
            padding_bottom="4rem"
        ),
        width="100%"
    )
