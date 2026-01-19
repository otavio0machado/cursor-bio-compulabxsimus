"""
Componentes de visualização para Auditoria IA
Laboratório Biodiagnóstico
"""
import reflex as rx
from ..styles import Color


def ai_stats_card(
    icon: str,
    title: str,
    value: str,
    subtitle: str = "",
    color: str = "blue",
    trend: str = None
) -> rx.Component:
    """Card de estatística da análise IA com design aprimorado"""
    bg_colors = {
        "blue": "from-blue-50 to-indigo-50",
        "green": "from-green-50 to-emerald-50",
        "orange": "from-orange-50 to-amber-50",
        "red": "from-red-50 to-rose-50",
        "purple": "from-purple-50 to-pink-50",
    }

    icon_colors = {
        "blue": "#3B82F6",
        "green": "#10B981",
        "orange": "#F97316",
        "red": "#EF4444",
        "purple": "#A855F7",
    }

    return rx.box(
        rx.vstack(
            # Header com ícone
            rx.hstack(
                rx.box(
                    rx.icon(
                        icon,
                        size=24,
                        color=icon_colors.get(color, icon_colors["blue"])
                    ),
                    class_name="w-12 h-12 flex items-center justify-center bg-white rounded-xl shadow-sm"
                ),
                rx.text(
                    title,
                    class_name="text-gray-600 text-sm font-medium"
                ),
                spacing="3",
                align="center",
                width="100%",
            ),

            # Valor principal
            rx.hstack(
                rx.text(
                    value,
                    class_name=f"text-3xl font-bold text-{color}-600"
                ),
                rx.cond(
                    trend != None,
                    rx.box(
                        rx.text(
                            trend,
                            class_name="text-xs font-semibold text-gray-500"
                        ),
                        class_name="bg-gray-100 px-2 py-1 rounded-md"
                    ),
                ),
                spacing="2",
                align="end",
            ),

            # Subtítulo
            rx.cond(
                subtitle != "",
                rx.text(
                    subtitle,
                    class_name="text-gray-500 text-xs"
                ),
            ),

            spacing="3",
            align="start",
            width="100%",
        ),
        class_name=f"bg-gradient-to-br {bg_colors.get(color, bg_colors['blue'])} border border-{color}-200 rounded-2xl p-6 hover:shadow-xl transition-all duration-300 h-full"
    )


def ai_progress_display(
    progress_percentage,
    progress_text,
    is_active: bool = True
) -> rx.Component:
    """Display de progresso avançado para análise IA"""
    return rx.cond(
        is_active,
        rx.box(
            rx.vstack(
                # Título
                rx.hstack(
                    rx.icon("bot", size=24, color=Color.DEEP),
                    rx.text(
                        "Análise por Inteligência Artificial",
                        class_name="text-[#1B5E20] font-bold text-lg"
                    ),
                    spacing="3",
                    align="center",
                ),

                # Progresso
                rx.vstack(
                    # Percentual grande
                    rx.text(
                        progress_percentage.to_string() + "%",
                        class_name="text-5xl font-bold text-[#1B5E20] text-center"
                    ),

                    # Status
                    rx.hstack(
                        rx.spinner(size="2", color=Color.DEEP),
                        rx.text(
                            progress_text,
                            class_name="text-gray-600 text-sm font-medium"
                        ),
                        spacing="2",
                        align="center",
                        justify="center",
                    ),

                    # Barra de progresso animada
                    rx.box(
                        rx.box(
                            class_name="h-full bg-gradient-to-r from-[#1B5E20] to-[#4CAF50] rounded-full transition-all duration-500 shadow-lg",
                            width=rx.cond(
                                progress_percentage > 0,
                                progress_percentage.to_string() + "%",
                                "0%"
                            ),
                        ),
                        class_name="w-full h-4 bg-gray-200 rounded-full overflow-hidden shadow-inner",
                    ),

                    # Dica
                    rx.box(
                        rx.hstack(
                            rx.icon("info", size=14, color="#6B7280"),
                            rx.text(
                                "Este processo pode levar alguns minutos dependendo da quantidade de dados",
                                class_name="text-gray-500 text-xs"
                            ),
                            spacing="2",
                            align="center",
                        ),
                        class_name="bg-gray-50 border border-gray-200 rounded-lg p-3 mt-2"
                    ),

                    spacing="4",
                    align="center",
                    width="100%",
                ),

                spacing="6",
                align="center",
                width="100%",
            ),
            class_name="bg-white border-2 border-[#1B5E20] rounded-2xl p-8 shadow-xl max-w-2xl w-full"
        ),
    )


def ai_divergence_type_badge(divergence_type: str) -> rx.Component:
    """Badge colorido para tipo de divergência"""
    return rx.match(
        divergence_type,
        ("Exame Ausente no SIMUS", rx.badge("Ausente SIMUS", color_scheme="red", size="2")),
        ("Exame Ausente no COMPULAB", rx.badge("Ausente COMPULAB", color_scheme="blue", size="2")),
        ("Valor Divergente", rx.badge("Valor Divergente", color_scheme="orange", size="2")),
        rx.badge(divergence_type, color_scheme="gray", size="2"),  # default
    )


def ai_analysis_summary_panel(
    total_divergences: int,
    pacientes_afetados: int,
    ausentes_simus: int,
    ausentes_compulab: int,
    valores_divergentes: int,
    impacto_financeiro: str
) -> rx.Component:
    """Painel resumo da análise IA"""
    return rx.box(
        rx.vstack(
            # Header
            rx.hstack(
                rx.icon("bar-chart-3", size=24, color=Color.DEEP),
                rx.text(
                    "Resumo Executivo da Auditoria",
                    class_name="text-[#1B5E20] font-bold text-xl"
                ),
                spacing="3",
                align="center",
            ),

            # Métricas principais em grid
            rx.grid(
                ai_stats_card(
                    "alert-triangle",
                    "Total de Divergências",
                    str(total_divergences),
                    "Itens que requerem atenção",
                    "red"
                ),
                ai_stats_card(
                    "users",
                    "Pacientes Afetados",
                    str(pacientes_afetados),
                    "Pacientes com divergências",
                    "orange"
                ),
                ai_stats_card(
                    "dollar-sign",
                    "Impacto Financeiro",
                    impacto_financeiro,
                    "Diferença monetária total",
                    "purple"
                ),
                columns="3",
                spacing="4",
                width="100%",
                class_name="mt-6"
            ),

            # Breakdown por tipo
            rx.box(
                rx.vstack(
                    rx.text(
                        "Distribuição por Tipo de Divergência",
                        class_name="text-gray-700 font-semibold text-sm mb-4"
                    ),
                    rx.grid(
                        rx.box(
                            rx.vstack(
                                rx.hstack(
                                    rx.icon("x-circle", size=20, color="#EF4444"),
                                    rx.text("Ausentes SIMUS", class_name="text-gray-600 text-sm"),
                                    spacing="2",
                                    align="center",
                                ),
                                rx.text(
                                    str(ausentes_simus),
                                    class_name="text-2xl font-bold text-red-600"
                                ),
                                spacing="2",
                                align="start",
                            ),
                            class_name="bg-red-50 border border-red-200 rounded-xl p-4"
                        ),
                        rx.box(
                            rx.vstack(
                                rx.hstack(
                                    rx.icon("x-circle", size=20, color="#3B82F6"),
                                    rx.text("Ausentes COMPULAB", class_name="text-gray-600 text-sm"),
                                    spacing="2",
                                    align="center",
                                ),
                                rx.text(
                                    str(ausentes_compulab),
                                    class_name="text-2xl font-bold text-blue-600"
                                ),
                                spacing="2",
                                align="start",
                            ),
                            class_name="bg-blue-50 border border-blue-200 rounded-xl p-4"
                        ),
                        rx.box(
                            rx.vstack(
                                rx.hstack(
                                    rx.icon("trending-up", size=20, color="#F97316"),
                                    rx.text("Valores Divergentes", class_name="text-gray-600 text-sm"),
                                    spacing="2",
                                    align="center",
                                ),
                                rx.text(
                                    str(valores_divergentes),
                                    class_name="text-2xl font-bold text-orange-600"
                                ),
                                spacing="2",
                                align="start",
                            ),
                            class_name="bg-orange-50 border border-orange-200 rounded-xl p-4"
                        ),
                        columns="3",
                        spacing="4",
                        width="100%",
                    ),
                    spacing="3",
                ),
                class_name="bg-gradient-to-br from-gray-50 to-white border border-gray-200 rounded-xl p-6 mt-6"
            ),

            spacing="6",
            align="start",
            width="100%",
        ),
        class_name="bg-white border border-gray-200 rounded-2xl p-8 shadow-lg"
    )


def ai_analysis_empty_state() -> rx.Component:
    """Estado vazio quando não há análise IA ainda"""
    return rx.box(
        rx.vstack(
            rx.box(
                rx.icon("bot", size=48, color="#9CA3AF"),
                class_name="w-24 h-24 flex items-center justify-center bg-gray-100 rounded-full"
            ),
            rx.text(
                "Análise por IA não gerada",
                class_name="text-gray-700 font-semibold text-lg"
            ),
            rx.text(
                "Clique no botão abaixo para gerar uma análise detalhada usando Inteligência Artificial",
                class_name="text-gray-500 text-sm text-center max-w-md"
            ),
            spacing="4",
            align="center",
        ),
        class_name="bg-gray-50 border-2 border-dashed border-gray-300 rounded-2xl p-12 text-center"
    )


def ai_error_display(error_message: str) -> rx.Component:
    """Display de erro para análise IA"""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.icon("alert-circle", size=24, color="#EF4444"),
                rx.text(
                    "Erro na Análise por IA",
                    class_name="text-red-700 font-bold text-lg"
                ),
                spacing="3",
                align="center",
            ),
            rx.text(
                error_message,
                class_name="text-red-600 text-sm"
            ),
            rx.box(
                rx.vstack(
                    rx.text(
                        "Possíveis causas:",
                        class_name="text-gray-700 font-semibold text-sm"
                    ),
                    rx.vstack(
                        rx.hstack(
                            rx.text("•", class_name="text-gray-500"),
                            rx.text("API Key inválida ou expirada", class_name="text-gray-600 text-sm"),
                            spacing="2",
                            align="start",
                        ),
                        rx.hstack(
                            rx.text("•", class_name="text-gray-500"),
                            rx.text("Limite de requisições excedido", class_name="text-gray-600 text-sm"),
                            spacing="2",
                            align="start",
                        ),
                        rx.hstack(
                            rx.text("•", class_name="text-gray-500"),
                            rx.text("Problemas de conexão com a API", class_name="text-gray-600 text-sm"),
                            spacing="2",
                            align="start",
                        ),
                        spacing="2",
                        align="start",
                    ),
                    spacing="2",
                    align="start",
                ),
                class_name="bg-gray-50 border border-gray-200 rounded-lg p-4 mt-3"
            ),
            spacing="4",
            align="start",
        ),
        class_name="bg-red-50 border border-red-200 rounded-xl p-6"
    )
