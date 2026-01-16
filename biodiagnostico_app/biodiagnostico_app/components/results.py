"""
Results display components for Biodiagnóstico App
"""
import reflex as rx
from ..state import State


def metric_card(
    title: str,
    value: str,
    icon: str,
    help_text: str = "",
    delta: str = None,
    delta_positive: bool = True
) -> rx.Component:
    """Card de métrica individual"""
    return rx.box(
        rx.hstack(
            rx.box(
                rx.text(icon, class_name="text-4xl"),
                class_name="text-lime-500"
            ),
            rx.vstack(
                rx.text(
                    title,
                    class_name="text-gray-500 text-sm uppercase tracking-wide font-medium"
                ),
                rx.text(
                    value,
                    class_name="text-green-800 text-2xl font-bold font-['Poppins']"
                ),
                rx.cond(
                    delta is not None,
                    rx.text(
                        delta,
                        class_name=rx.cond(
                            delta_positive,
                            "text-green-600 text-sm font-medium",
                            "text-red-600 text-sm font-medium"
                        )
                    ),
                ),
                rx.cond(
                    help_text != "",
                    rx.text(
                        help_text,
                        class_name="text-gray-400 text-xs"
                    ),
                ),
                spacing="1",
                align="start",
            ),
            spacing="4",
            align="center",
        ),
        class_name="bg-white p-5 rounded-2xl shadow-lg shadow-green-900/5 border border-green-100 hover:shadow-xl hover:-translate-y-1 transition-all duration-300"
    )


def results_summary() -> rx.Component:
    """Resumo dos resultados da análise"""
    return rx.cond(
        State.has_analysis,
        rx.vstack(
            rx.hstack(
                rx.text("📈", class_name="text-2xl"),
                rx.text(
                    "Resumo da Análise",
                    class_name="text-green-800 font-bold text-xl"
                ),
                spacing="3",
                align="center",
            ),
            rx.grid(
                metric_card(
                    title="COMPULAB Total",
                    value=State.formatted_compulab_total,
                    icon="💰",
                    help_text=f"{State.compulab_count} pacientes",
                ),
                metric_card(
                    title="SIMUS Total",
                    value=State.formatted_simus_total,
                    icon="💸",
                    help_text=f"{State.simus_count} pacientes",
                ),
                metric_card(
                    title="Diferença Total",
                    value=State.formatted_difference,
                    icon="📉",
                    help_text="COMPULAB - SIMUS",
                    delta=f"{State.difference_percent:.1f}%",
                    delta_positive=State.difference >= 0,
                ),
                metric_card(
                    title="Exames Faltantes",
                    value=f"{State.missing_exams_count}",
                    icon="⚠️",
                    help_text="no SIMUS",
                ),
                columns="4",
                spacing="4",
                width="100%",
            ),
            spacing="4",
            width="100%",
        ),
    )


def breakdown_section() -> rx.Component:
    """Seção de explicação da diferença"""
    return rx.cond(
        State.has_analysis,
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.text("🧭", class_name="text-2xl"),
                    rx.text(
                        "Por que existe essa diferença?",
                        class_name="text-green-800 font-bold text-xl"
                    ),
                    spacing="3",
                    align="center",
                ),
                rx.text(
                    "Detalhes sobre a composição da diferença total",
                    class_name="text-gray-600"
                ),
                rx.grid(
                    rx.box(
                        rx.vstack(
                            rx.text("👤", class_name="text-2xl"),
                            rx.text("Pacientes Faltantes", class_name="text-gray-600 text-sm"),
                            rx.text(
                                f"R$ {State.missing_patients_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                                class_name="text-green-800 font-bold text-lg"
                            ),
                            spacing="1",
                            align="center",
                        ),
                        class_name="bg-white p-4 rounded-xl border border-green-100"
                    ),
                    rx.box(
                        rx.vstack(
                            rx.text("📝", class_name="text-2xl"),
                            rx.text("Exames Faltantes", class_name="text-gray-600 text-sm"),
                            rx.text(
                                f"R$ {State.missing_exams_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                                class_name="text-green-800 font-bold text-lg"
                            ),
                            spacing="1",
                            align="center",
                        ),
                        class_name="bg-white p-4 rounded-xl border border-green-100"
                    ),
                    rx.box(
                        rx.vstack(
                            rx.text("💸", class_name="text-2xl"),
                            rx.text("Divergências", class_name="text-gray-600 text-sm"),
                            rx.text(
                                f"R$ {State.divergences_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                                class_name="text-green-800 font-bold text-lg"
                            ),
                            spacing="1",
                            align="center",
                        ),
                        class_name="bg-white p-4 rounded-xl border border-green-100"
                    ),
                    rx.box(
                        rx.vstack(
                            rx.text("✅", class_name="text-2xl"),
                            rx.text("Total Explicado", class_name="text-gray-600 text-sm"),
                            rx.text(
                                f"R$ {State.explained_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                                class_name="text-green-800 font-bold text-lg"
                            ),
                            spacing="1",
                            align="center",
                        ),
                        class_name="bg-white p-4 rounded-xl border border-green-100"
                    ),
                    rx.box(
                        rx.vstack(
                            rx.text("❓", class_name="text-2xl"),
                            rx.text("Diferença Residual", class_name="text-gray-600 text-sm"),
                            rx.text(
                                f"R$ {State.residual:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                                class_name="text-orange-600 font-bold text-lg"
                            ),
                            spacing="1",
                            align="center",
                        ),
                        class_name="bg-white p-4 rounded-xl border border-orange-100"
                    ),
                    columns="5",
                    spacing="3",
                    width="100%",
                ),
                rx.text(
                    "A diferença total é explicada pela soma: pacientes faltantes + exames faltantes + divergências de valores.",
                    class_name="text-gray-500 text-sm italic mt-2"
                ),
                spacing="4",
                width="100%",
            ),
            class_name="bg-gradient-to-br from-green-50 to-lime-50 p-6 rounded-2xl mt-6"
        ),
    )


def missing_exams_table() -> rx.Component:
    """Tabela de exames faltantes"""
    return rx.cond(
        State.missing_exams_count > 0,
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.text("⚠️", class_name="text-2xl"),
                    rx.text(
                        f"Exames Faltantes ({State.missing_exams_count})",
                        class_name="text-green-800 font-bold text-lg"
                    ),
                    spacing="3",
                    align="center",
                ),
                rx.data_table(
                    data=State.missing_exams,
                    columns=[
                        {"name": "patient", "label": "Paciente"},
                        {"name": "exam_name", "label": "Exame"},
                        {"name": "value", "label": "Valor (R$)"},
                    ],
                    pagination=True,
                    search=True,
                    sort=True,
                ),
                spacing="4",
                width="100%",
            ),
            class_name="bg-white p-6 rounded-2xl shadow-lg border border-orange-100 mt-6"
        ),
    )


def divergences_table() -> rx.Component:
    """Tabela de divergências de valores"""
    return rx.cond(
        State.divergences_count > 0,
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.text("💰", class_name="text-2xl"),
                    rx.text(
                        f"Divergências de Valores ({State.divergences_count})",
                        class_name="text-green-800 font-bold text-lg"
                    ),
                    spacing="3",
                    align="center",
                ),
                rx.data_table(
                    data=State.value_divergences,
                    columns=[
                        {"name": "patient", "label": "Paciente"},
                        {"name": "exam_name", "label": "Exame"},
                        {"name": "compulab_value", "label": "COMPULAB (R$)"},
                        {"name": "simus_value", "label": "SIMUS (R$)"},
                        {"name": "difference", "label": "Diferença (R$)"},
                    ],
                    pagination=True,
                    search=True,
                    sort=True,
                ),
                spacing="4",
                width="100%",
            ),
            class_name="bg-white p-6 rounded-2xl shadow-lg border border-yellow-100 mt-6"
        ),
    )


def ai_analysis_section() -> rx.Component:
    """Seção de análise por IA"""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.text("🤖", class_name="text-2xl"),
                rx.text(
                    "Análise por Inteligência Artificial",
                    class_name="text-green-800 font-bold text-lg"
                ),
                spacing="3",
                align="center",
            ),
            rx.cond(
                State.gemini_api_key == "",
                rx.box(
                    rx.vstack(
                        rx.text(
                            "Configure sua API Key do Gemini para usar esta funcionalidade",
                            class_name="text-gray-600"
                        ),
                        rx.input(
                            placeholder="Cole sua API Key do Gemini aqui...",
                            type="password",
                            on_change=State.set_api_key,
                            class_name="w-full"
                        ),
                        rx.link(
                            rx.text("🔑 Obter API Key", class_name="text-lime-600 hover:underline"),
                            href="https://makersuite.google.com/app/apikey",
                            is_external=True,
                        ),
                        spacing="3",
                        width="100%",
                    ),
                    class_name="bg-yellow-50 border border-yellow-200 rounded-lg p-4"
                ),
                rx.vstack(
                    rx.text("✅ API Key configurada!", class_name="text-green-600"),
                    rx.button(
                        rx.cond(
                            State.is_generating_ai,
                            rx.hstack(
                                rx.spinner(size="1"),
                                rx.text("Gerando análise..."),
                                spacing="2",
                            ),
                            rx.hstack(
                                rx.text("🤖"),
                                rx.text("Gerar Análise por IA"),
                                spacing="2",
                            ),
                        ),
                        on_click=State.generate_ai_analysis,
                        disabled=State.is_generating_ai | ~State.has_analysis,
                        class_name="bg-gradient-to-r from-lime-500 to-green-600 text-white px-6 py-3 rounded-xl font-semibold hover:shadow-lg transition-all"
                    ),
                    spacing="3",
                ),
            ),
            rx.cond(
                State.ai_analysis != "",
                rx.box(
                    rx.markdown(State.ai_analysis),
                    class_name="bg-white rounded-xl p-6 border border-green-100 mt-4 prose prose-green max-w-none"
                ),
            ),
            spacing="4",
            width="100%",
        ),
        class_name="bg-gradient-to-br from-blue-50 to-indigo-50 p-6 rounded-2xl mt-6"
    )

