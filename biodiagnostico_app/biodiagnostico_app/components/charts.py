"""
Chart components for Biodiagnóstico App
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
                    rx.text("📊", class_name="text-2xl"),
                    rx.text(
                        "Visualização de Divergências",
                        class_name="text-green-800 font-bold text-lg"
                    ),
                    spacing="3",
                    align="center",
                ),
                rx.text(
                    "Gráfico interativo das principais divergências",
                    class_name="text-gray-600"
                ),
                # Placeholder para gráfico - pode usar rx.recharts ou plotly
                rx.box(
                    rx.center(
                        rx.vstack(
                            rx.text("📈", class_name="text-6xl text-gray-300"),
                            rx.text(
                                "Gráfico de barras das divergências",
                                class_name="text-gray-400"
                            ),
                            spacing="2",
                        ),
                        class_name="h-64"
                    ),
                    class_name="bg-gray-50 rounded-xl border-2 border-dashed border-gray-200"
                ),
                spacing="4",
                width="100%",
            ),
            class_name="bg-white p-6 rounded-2xl shadow-lg border border-green-100 mt-6"
        ),
    )


def summary_pie_chart() -> rx.Component:
    """Gráfico de pizza do breakdown"""
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
                            rx.text("Pacientes somente COMPULAB", class_name="text-sm text-gray-600 w-40"),
                            rx.box(
                                class_name="h-6 bg-green-500 rounded-r-full transition-all w-1/3",
                            ),
                            rx.text(
                                State.formatted_patients_only_compulab_total,
                                class_name="text-sm text-gray-700 ml-2 w-32"
                            ),
                            align="center",
                            width="100%",
                        ),
                    ),
                    # Exames faltantes
                    rx.box(
                        rx.hstack(
                            rx.text("Exames somente COMPULAB", class_name="text-sm text-gray-600 w-40"),
                            rx.box(
                                class_name="h-6 bg-lime-500 rounded-r-full transition-all w-1/3",
                            ),
                            rx.text(
                                State.formatted_exams_only_compulab_total,
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

