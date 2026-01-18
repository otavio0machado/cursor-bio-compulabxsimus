"""
Chart components for Biodiagnóstico App
Design Premium SaaS
"""
import reflex as rx
from ..state import State


def divergences_chart() -> rx.Component:
    """Gráfico de divergências (placeholder - usar plotly ou recharts)"""
    return rx.cond(
        State.divergences_count > 0,
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.box(
                        rx.text("📊", class_name="text-xl"),
                        class_name="w-8 h-8 rounded-lg bg-green-50 flex items-center justify-center"
                    ),
                    rx.text(
                        "Visualização de Divergências",
                        class_name="text-[#1B5E20] font-bold text-lg"
                    ),
                    spacing="3",
                    align="center",
                ),
                rx.text(
                    "Distribuição das divergências encontradas na análise",
                    class_name="text-gray-500 text-sm ml-11"
                ),
                # Placeholder para gráfico
                rx.box(
                    rx.center(
                        rx.vstack(
                            rx.icon("bar-chart-2", size=48, class_name="text-gray-300"),
                            rx.text(
                                "Gráfico Interativo",
                                class_name="text-gray-400 font-medium"
                            ),
                            spacing="2",
                        ),
                        class_name="h-64"
                    ),
                    class_name="bg-gray-50 rounded-2xl border border-dashed border-gray-200 mt-4"
                ),
                spacing="2",
                width="100%",
            ),
            class_name="bg-white p-6 rounded-3xl shadow-lg shadow-gray-100 border border-gray-100 mt-6"
        ),
    )


def summary_pie_chart() -> rx.Component:
    """Gráfico de pizza do breakdown"""
    return rx.cond(
        State.has_analysis,
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.box(
                        rx.text("🥧", class_name="text-xl"),
                        class_name="w-8 h-8 rounded-lg bg-green-50 flex items-center justify-center"
                    ),
                    rx.text(
                        "Composição da Diferença",
                        class_name="text-[#1B5E20] font-bold text-lg"
                    ),
                    spacing="3",
                    align="center",
                ),

                # Visualização em barras modernas
                rx.vstack(
                    # Pacientes faltantes
                    rx.box(
                        rx.vstack(
                            rx.hstack(
                                rx.text("Pacientes Faltantes", class_name="text-xs font-medium text-gray-500 uppercase tracking-wide"),
                                rx.spacer(),
                                rx.text(State.formatted_missing_patients_total, class_name="text-sm font-bold text-gray-700"),
                                width="100%",
                            ),
                            rx.box(
                                class_name="h-2 bg-gray-100 rounded-full w-full overflow-hidden",
                                children=[
                                    rx.box(class_name="h-full bg-orange-400 rounded-full w-1/3") # Placeholder width
                                ]
                            ),
                            spacing="1",
                            width="100%",
                        ),
                    ),
                    # Exames faltantes
                    rx.box(
                        rx.vstack(
                            rx.hstack(
                                rx.text("Exames Faltantes", class_name="text-xs font-medium text-gray-500 uppercase tracking-wide"),
                                rx.spacer(),
                                rx.text(State.formatted_missing_exams_total, class_name="text-sm font-bold text-gray-700"),
                                width="100%",
                            ),
                            rx.box(
                                class_name="h-2 bg-gray-100 rounded-full w-full overflow-hidden",
                                children=[
                                    rx.box(class_name="h-full bg-red-400 rounded-full w-1/3") # Placeholder width
                                ]
                            ),
                            spacing="1",
                            width="100%",
                        ),
                    ),
                    # Divergências
                    rx.box(
                        rx.vstack(
                            rx.hstack(
                                rx.text("Divergências de Valor", class_name="text-xs font-medium text-gray-500 uppercase tracking-wide"),
                                rx.spacer(),
                                rx.text(State.formatted_divergences_total, class_name="text-sm font-bold text-gray-700"),
                                width="100%",
                            ),
                            rx.box(
                                class_name="h-2 bg-gray-100 rounded-full w-full overflow-hidden",
                                children=[
                                    rx.box(class_name="h-full bg-blue-400 rounded-full w-1/3") # Placeholder width
                                ]
                            ),
                            spacing="1",
                            width="100%",
                        ),
                    ),
                    spacing="6",
                    width="100%",
                    class_name="bg-gray-50/50 p-6 rounded-2xl mt-4 border border-gray-100"
                ),
                spacing="2",
                width="100%",
            ),
            class_name="bg-white p-6 rounded-3xl shadow-lg shadow-gray-100 border border-gray-100 mt-6"
        ),
    )
