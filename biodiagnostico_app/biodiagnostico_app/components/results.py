"""
Results display components for Biodiagnóstico App
Design Premium SaaS - Clean & Clinical
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
    """Card de métrica individual - Premium Style"""
    return rx.box(
        rx.hstack(
            rx.box(
                rx.text(icon, class_name="text-2xl"),
                class_name="w-12 h-12 rounded-2xl bg-gradient-to-br from-green-50 to-emerald-50 flex items-center justify-center border border-green-100 shadow-inner"
            ),
            rx.vstack(
                rx.text(
                    title,
                    class_name="text-gray-500 text-xs font-bold uppercase tracking-wider"
                ),
                rx.hstack(
                    rx.text(
                        value,
                        class_name="text-gray-900 text-xl font-bold font-['Poppins'] tracking-tight"
                    ),
                    rx.cond(
                        delta is not None,
                        rx.box(
                            rx.hstack(
                                rx.icon(
                                    "trending-up" if delta_positive else "trending-down",
                                    size=12,
                                    class_name="text-white"
                                ),
                                rx.text(
                                    delta,
                                    class_name="text-white text-[10px] font-bold"
                                ),
                                spacing="1",
                                align="center",
                            ),
                            class_name=rx.cond(
                                delta_positive,
                                "bg-green-500 px-2 py-0.5 rounded-full shadow-sm shadow-green-200",
                                "bg-red-500 px-2 py-0.5 rounded-full shadow-sm shadow-red-200"
                            )
                        )
                    ),
                    align="center",
                    spacing="2",
                ),
                rx.cond(
                    help_text != "",
                    rx.text(
                        help_text,
                        class_name="text-gray-400 text-[10px] font-medium"
                    ),
                ),
                spacing="1",
                align="start",
            ),
            spacing="3",
            align="center",
        ),
        class_name="bg-white p-5 rounded-2xl shadow-[0_2px_10px_-3px_rgba(0,0,0,0.05)] border border-gray-100 hover:shadow-lg hover:-translate-y-0.5 transition-all duration-300"
    )


def results_summary() -> rx.Component:
    """Resumo dos resultados da análise"""
    return rx.cond(
        State.has_analysis,
        rx.vstack(
            rx.hstack(
                rx.box(
                    rx.text("📈", class_name="text-xl"),
                    class_name="w-8 h-8 rounded-lg bg-green-50 flex items-center justify-center"
                ),
                rx.text(
                    "Resumo Executivo",
                    class_name="text-[#1B5E20] font-bold text-lg"
                ),
                spacing="3",
                align="center",
            ),
            rx.grid(
                metric_card(
                    title="COMPULAB Total",
                    value=State.formatted_compulab_total,
                    icon="💰",
                    help_text=f"{State.compulab_count} pacientes analisados",
                ),
                metric_card(
                    title="SIMUS Total",
                    value=State.formatted_simus_total,
                    icon="💸",
                    help_text=f"{State.simus_count} pacientes processados",
                ),
                metric_card(
                    title="Diferença Líquida",
                    value=State.formatted_difference,
                    icon="📉",
                    help_text="Variação absoluta",
                    delta=f"{State.difference_percent:.1f}%",
                    delta_positive=State.difference >= 0,
                ),
                metric_card(
                    title="Exames Ausentes",
                    value=f"{State.missing_exams_count}",
                    icon="⚠️",
                    help_text="Não encontrados no SIMUS",
                ),
                columns="1 md:grid-cols-2 lg:grid-cols-4",
                spacing="4",
                width="100%",
            ),
            spacing="4",
            width="100%",
        ),
    )


def breakdown_section() -> rx.Component:
    """Seção de explicação da diferença - Cards elegantes"""
    return rx.cond(
        State.has_analysis,
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.box(
                        rx.text("🧭", class_name="text-xl"),
                        class_name="w-8 h-8 rounded-lg bg-green-50 flex items-center justify-center"
                    ),
                    rx.text(
                        "Análise de Causalidade",
                        class_name="text-[#1B5E20] font-bold text-lg"
                    ),
                    spacing="3",
                    align="center",
                ),
                rx.text(
                    "Decomposição detalhada das origens das divergências financeiras",
                    class_name="text-gray-500 text-sm ml-11"
                ),
                rx.grid(
                    rx.box(
                        rx.vstack(
                            rx.box(rx.text("👤", class_name="text-2xl"), class_name="mb-1"),
                            rx.text("Pacientes", class_name="text-gray-500 text-xs uppercase tracking-wide font-bold"),
                            rx.text(
                                f"R$ {State.missing_patients_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                                class_name="text-gray-800 font-bold text-lg"
                            ),
                            rx.text("Não localizados", class_name="text-xs text-gray-400"),
                            spacing="1",
                            align="center",
                        ),
                        class_name="bg-white p-5 rounded-2xl border border-gray-100 shadow-sm hover:shadow-md transition-shadow"
                    ),
                    rx.box(
                        rx.vstack(
                            rx.box(rx.text("📝", class_name="text-2xl"), class_name="mb-1"),
                            rx.text("Exames", class_name="text-gray-500 text-xs uppercase tracking-wide font-bold"),
                            rx.text(
                                f"R$ {State.missing_exams_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                                class_name="text-gray-800 font-bold text-lg"
                            ),
                            rx.text("Não lançados", class_name="text-xs text-gray-400"),
                            spacing="1",
                            align="center",
                        ),
                        class_name="bg-white p-5 rounded-2xl border border-gray-100 shadow-sm hover:shadow-md transition-shadow"
                    ),
                    rx.box(
                        rx.vstack(
                            rx.box(rx.text("💸", class_name="text-2xl"), class_name="mb-1"),
                            rx.text("Divergências", class_name="text-gray-500 text-xs uppercase tracking-wide font-bold"),
                            rx.text(
                                f"R$ {State.divergences_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                                class_name="text-gray-800 font-bold text-lg"
                            ),
                            rx.text("Diferença de valor", class_name="text-xs text-gray-400"),
                            spacing="1",
                            align="center",
                        ),
                        class_name="bg-white p-5 rounded-2xl border border-gray-100 shadow-sm hover:shadow-md transition-shadow"
                    ),
                    rx.box(
                        rx.vstack(
                            rx.box(rx.text("✅", class_name="text-2xl"), class_name="mb-1"),
                            rx.text("Explicado", class_name="text-green-600 text-xs uppercase tracking-wide font-bold"),
                            rx.text(
                                f"R$ {State.explained_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                                class_name="text-green-700 font-bold text-lg"
                            ),
                            rx.text("Total rastreado", class_name="text-xs text-green-500/70"),
                            spacing="1",
                            align="center",
                        ),
                        class_name="bg-green-50/50 p-5 rounded-2xl border border-green-100 shadow-sm hover:shadow-md transition-shadow"
                    ),
                    rx.box(
                        rx.vstack(
                            rx.box(rx.text("❓", class_name="text-2xl"), class_name="mb-1"),
                            rx.text("Residual", class_name="text-orange-600 text-xs uppercase tracking-wide font-bold"),
                            rx.text(
                                f"R$ {State.residual:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                                class_name="text-orange-700 font-bold text-lg"
                            ),
                            rx.text("Não identificado", class_name="text-xs text-orange-500/70"),
                            spacing="1",
                            align="center",
                        ),
                        class_name="bg-orange-50/50 p-5 rounded-2xl border border-orange-100 shadow-sm hover:shadow-md transition-shadow"
                    ),
                    columns="2 md:grid-cols-3 lg:grid-cols-5",
                    spacing="4",
                    width="100%",
                ),
                spacing="4",
                width="100%",
            ),
            class_name="bg-gray-50/50 p-6 rounded-3xl mt-6 border border-gray-100"
        ),
    )


def missing_exams_table() -> rx.Component:
    """Tabela de exames faltantes - Clean Design"""
    return rx.cond(
        State.missing_exams_count > 0,
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.box(
                        rx.text("⚠️", class_name="text-xl"),
                        class_name="w-8 h-8 rounded-lg bg-orange-50 flex items-center justify-center"
                    ),
                    rx.text(
                        f"Relatório de Exames Faltantes ({State.missing_exams_count})",
                        class_name="text-[#1B5E20] font-bold text-lg"
                    ),
                    spacing="3",
                    align="center",
                ),
                rx.box(
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
                        class_name="w-full text-sm"
                    ),
                    class_name="overflow-hidden rounded-xl border border-gray-200 mt-2"
                ),
                spacing="4",
                width="100%",
            ),
            class_name="bg-white p-6 rounded-3xl shadow-lg shadow-gray-100 border border-gray-100 mt-6"
        ),
    )


def divergences_table() -> rx.Component:
    """Tabela de divergências de valores - Clean Design"""
    return rx.cond(
        State.divergences_count > 0,
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.box(
                        rx.text("💰", class_name="text-xl"),
                        class_name="w-8 h-8 rounded-lg bg-blue-50 flex items-center justify-center"
                    ),
                    rx.text(
                        f"Relatório de Divergências ({State.divergences_count})",
                        class_name="text-[#1B5E20] font-bold text-lg"
                    ),
                    spacing="3",
                    align="center",
                ),
                rx.box(
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
                        class_name="w-full text-sm"
                    ),
                    class_name="overflow-hidden rounded-xl border border-gray-200 mt-2"
                ),
                spacing="4",
                width="100%",
            ),
            class_name="bg-white p-6 rounded-3xl shadow-lg shadow-gray-100 border border-gray-100 mt-6"
        ),
    )


def ai_analysis_section() -> rx.Component:
    """Seção de análise por IA - Premium Design"""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.box(
                    rx.text("🤖", class_name="text-xl"),
                    class_name="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-200"
                ),
                rx.vstack(
                    rx.text(
                        "Análise Inteligente (IA)",
                        class_name="text-[#1B5E20] font-bold text-lg leading-tight"
                    ),
                    rx.text(
                        "Powered by Google Gemini",
                        class_name="text-gray-400 text-[10px] font-bold tracking-wider uppercase"
                    ),
                    spacing="0",
                    align="start",
                ),
                spacing="3",
                align="center",
            ),

            rx.cond(
                State.gemini_api_key == "",
                rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.icon("alert-triangle", size=20, class_name="text-amber-600"),
                            rx.text("Configuração Necessária", class_name="font-bold text-amber-800"),
                            spacing="2",
                            align="center",
                        ),
                        rx.text(
                            "Para utilizar a análise inteligente, é necessário configurar sua chave de API.",
                            class_name="text-amber-700 text-sm"
                        ),
                        rx.button(
                            "Configurar Agora",
                            on_click=State.set_page("api"),
                            class_name="bg-amber-100 text-amber-800 hover:bg-amber-200 px-4 py-2 rounded-lg text-sm font-semibold transition-colors w-full mt-2"
                        ),
                        spacing="2",
                        width="100%",
                    ),
                    class_name="bg-amber-50 border border-amber-200 rounded-2xl p-5 mt-4"
                ),
                rx.vstack(
                    rx.box(
                        rx.button(
                            rx.cond(
                                State.is_generating_ai,
                                rx.hstack(
                                    rx.spinner(size="2", color="white"),
                                    rx.text("Processando dados com IA..."),
                                    spacing="2",
                                ),
                                rx.hstack(
                                    rx.icon("sparkles", size=18),
                                    rx.text("Gerar Relatório Inteligente"),
                                    spacing="2",
                                ),
                            ),
                            on_click=State.generate_ai_analysis,
                            disabled=State.is_generating_ai | ~State.has_analysis,
                            class_name="bg-gradient-to-r from-[#4CAF50] to-[#1B5E20] text-white px-8 py-4 rounded-xl font-semibold shadow-lg shadow-green-900/20 hover:shadow-xl hover:-translate-y-0.5 transition-all w-full md:w-auto"
                        ),
                        class_name="mt-4 flex justify-center w-full"
                    ),
                ),
            ),

            rx.cond(
                State.ai_analysis != "",
                rx.box(
                    rx.box(
                        rx.markdown(State.ai_analysis),
                        class_name="prose prose-sm prose-green max-w-none text-gray-700 leading-relaxed"
                    ),
                    class_name="bg-white rounded-2xl p-8 border border-gray-100 mt-6 shadow-sm relative overflow-hidden"
                ),
            ),
            spacing="4",
            width="100%",
        ),
        class_name="bg-gradient-to-br from-slate-50 to-white p-8 rounded-3xl mt-8 border border-gray-100 shadow-sm"
    )
