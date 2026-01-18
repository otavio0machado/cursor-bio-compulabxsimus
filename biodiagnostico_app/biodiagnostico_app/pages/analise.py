"""
Análise COMPULAB x SIMUS page
Design Premium SaaS - Clean & Clinical
"""
import reflex as rx
from ..state import State
from ..components.file_upload import compact_upload_card, upload_progress_indicator
from ..components.results import metric_card, results_summary, breakdown_section, missing_exams_table, divergences_table, ai_analysis_section
from ..components.charts import summary_pie_chart, divergences_chart


def analise_page() -> rx.Component:
    """Página de análise comparativa - Design Premium"""
    
    # SVG compacto do Erlenmeyer
    erlenmeyer_small = """
        <svg viewBox="0 0 50 60" width="36" height="44">
            <path d="M18 8 L32 8 L32 22 L42 50 Q43 54 39 56 L11 56 Q7 54 8 50 L18 22 Z" 
                  fill="none" stroke="#1B5E20" stroke-width="2"/>
            <circle cx="25" cy="42" r="6" fill="#4CAF50" opacity="0.3"/>
        </svg>
    """
    
    # SVG compacto dos Tubos
    tubes_small = """
        <svg viewBox="0 0 60 60" width="36" height="44">
            <rect x="12" y="10" width="10" height="40" rx="5" fill="none" stroke="#1B5E20" stroke-width="2"/>
            <rect x="25" y="10" width="10" height="40" rx="5" fill="none" stroke="#1B5E20" stroke-width="2"/>
            <rect x="38" y="10" width="10" height="40" rx="5" fill="none" stroke="#1B5E20" stroke-width="2"/>
            <rect x="12" y="28" width="10" height="22" rx="5" fill="#4CAF50" opacity="0.3"/>
            <rect x="25" y="24" width="10" height="26" rx="5" fill="#4CAF50" opacity="0.3"/>
            <rect x="38" y="32" width="10" height="18" rx="5" fill="#4CAF50" opacity="0.3"/>
        </svg>
    """
    
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
            rx.vstack(
                rx.text(
                    "Análise Financeira Comparativa",
                    class_name="text-[#1B5E20] text-3xl md:text-5xl font-bold tracking-tight text-center"
                ),
                rx.text(
                    "Auditoria cruzada entre sistemas laboratoriais para detecção de divergências",
                    class_name="text-gray-500 text-lg mt-2 font-medium text-center"
                ),
                spacing="0",
                align="center",
                class_name="mb-8"
            ),
            
            # Upload section
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.box(
                            rx.text("📁", class_name="text-xl"),
                            class_name="w-10 h-10 rounded-xl bg-green-50 flex items-center justify-center"
                        ),
                        rx.text(
                            "Fontes de Dados",
                            class_name="text-[#1B5E20] font-bold text-lg"
                        ),
                        spacing="3",
                        align="center",
                        class_name="mb-2"
                    ),
                    rx.text(
                        "Carregue os relatórios em PDF ou os arquivos CSV padronizados",
                        class_name="text-gray-500 text-sm mb-4 ml-1"
                    ),

                    rx.grid(
                        compact_upload_card(
                            title="COMPULAB",
                            icon_svg=erlenmeyer_small,
                            upload_id="compulab_analysis",
                            file_name=State.compulab_file_name,
                            file_size=State.compulab_file_size,
                            on_upload=State.handle_compulab_upload,
                            on_remove=State.clear_compulab_file,
                            accepted_types="PDF/CSV",
                        ),
                        compact_upload_card(
                            title="SIMUS",
                            icon_svg=tubes_small,
                            upload_id="simus_analysis",
                            file_name=State.simus_file_name,
                            file_size=State.simus_file_size,
                            on_upload=State.handle_simus_upload,
                            on_remove=State.clear_simus_file,
                            accepted_types="PDF/CSV",
                        ),
                        columns="1 md:grid-cols-2",
                        spacing="4",
                        width="100%",
                    ),

                    upload_progress_indicator(State.is_uploading, "Validando estrutura dos arquivos..."),
                    spacing="2",
                    width="100%",
                ),
                class_name="bg-white border border-gray-100 rounded-3xl p-6 mt-4 max-w-4xl w-full shadow-lg shadow-gray-100"
            ),
            
            # Botão de análise
            rx.box(
                rx.button(
                    rx.cond(
                        State.is_analyzing,
                        rx.hstack(
                            rx.spinner(size="2", color="white"),
                            rx.text("Executando Auditoria..."),
                            spacing="3",
                            align="center",
                        ),
                        rx.hstack(
                            rx.icon("search", size=20),
                            rx.text("Executar Análise de Conformidade"),
                            spacing="2",
                            align="center",
                        ),
                    ),
                    on_click=State.run_analysis,
                    disabled=~State.has_files | State.is_analyzing,
                    class_name="bg-gradient-to-r from-[#1B5E20] to-[#2E7D32] text-white px-10 py-4 rounded-xl font-bold text-lg shadow-lg shadow-green-900/20 hover:shadow-xl hover:-translate-y-1 transition-all disabled:opacity-50 disabled:cursor-not-allowed mt-8"
                ),
            ),
            
            # Indicador de progresso
            rx.cond(
                State.is_analyzing,
                rx.box(
                    rx.vstack(
                        rx.text(
                            State.analysis_progress_percentage.to_string() + "%",
                            class_name="text-[#1B5E20] text-4xl font-bold font-['Poppins'] text-center"
                        ),
                        rx.text(
                            State.analysis_stage,
                            class_name="text-gray-500 text-sm font-medium text-center mt-1"
                        ),
                        # Barra de progresso
                        rx.box(
                            rx.box(
                                class_name="h-full bg-gradient-to-r from-[#4CAF50] to-[#1B5E20] rounded-full transition-all duration-300 relative overflow-hidden",
                                width=rx.cond(
                                    State.analysis_progress_percentage > 0,
                                    State.analysis_progress_percentage.to_string() + "%",
                                    "0%"
                                ),
                                children=[
                                    rx.box(class_name="absolute inset-0 bg-white/20 animate-[shimmer_2s_infinite]")
                                ]
                            ),
                            class_name="w-full h-3 bg-gray-100 rounded-full overflow-hidden mt-4 shadow-inner",
                        ),
                        spacing="2",
                        align="center",
                    ),
                    class_name="bg-white border border-gray-100 rounded-2xl p-8 mt-6 max-w-2xl w-full shadow-lg"
                ),
            ),
            
            # Mensagens
            rx.cond(
                State.success_message != "",
                rx.box(
                    rx.hstack(
                        rx.icon("check-circle-2", size=20, class_name="text-green-600"),
                        rx.text(State.success_message, class_name="text-green-800 font-medium"),
                        spacing="3",
                    ),
                    class_name="bg-green-50 border border-green-200 rounded-xl p-4 mt-6 max-w-2xl w-full animate-fade-in"
                ),
            ),
            rx.cond(
                State.error_message != "",
                rx.box(
                    rx.hstack(
                        rx.icon("alert-triangle", size=20, class_name="text-red-600"),
                        rx.text(State.error_message, class_name="text-red-800 font-medium"),
                        spacing="3",
                    ),
                    class_name="bg-red-50 border border-red-200 rounded-xl p-4 mt-6 max-w-2xl w-full animate-shake"
                ),
            ),
            
            # Resultados
            rx.cond(
                State.has_analysis,
                rx.vstack(
                    # Métricas principais
                    rx.box(
                        results_summary(),
                        class_name="w-full mt-8"
                    ),
                    
                    # Breakdown da diferença
                    rx.box(
                        breakdown_section(),
                        class_name="w-full mt-4"
                    ),
                    
                    # Gráficos
                    rx.grid(
                        summary_pie_chart(),
                        divergences_chart(),
                        columns="1 lg:grid-cols-2",
                        spacing="6",
                        width="100%",
                        class_name="mt-4"
                    ),

                    # Tabs de detalhes - Modern Design
                    rx.tabs.root(
                        rx.tabs.list(
                            rx.tabs.trigger(
                                rx.hstack(
                                    rx.icon("alert-circle", size=16),
                                    rx.text(f"Exames Faltantes ({State.missing_exams_count})"),
                                    spacing="2",
                                ),
                                value="missing",
                                class_name="data-[state=active]:bg-white data-[state=active]:text-[#1B5E20] data-[state=active]:shadow-sm data-[state=active]:border-gray-200 px-6 py-3 rounded-xl transition-all text-sm font-semibold text-gray-500 border border-transparent"
                            ),
                            rx.tabs.trigger(
                                rx.hstack(
                                    rx.icon("banknote", size=16),
                                    rx.text(f"Divergências ({State.divergences_count})"),
                                    spacing="2",
                                ),
                                value="divergences",
                                class_name="data-[state=active]:bg-white data-[state=active]:text-[#1B5E20] data-[state=active]:shadow-sm data-[state=active]:border-gray-200 px-6 py-3 rounded-xl transition-all text-sm font-semibold text-gray-500 border border-transparent"
                            ),
                            rx.tabs.trigger(
                                rx.hstack(
                                    rx.icon("sparkles", size=16),
                                    rx.text("Análise IA"),
                                    spacing="2",
                                ),
                                value="ai",
                                class_name="data-[state=active]:bg-gradient-to-r data-[state=active]:from-[#4CAF50] data-[state=active]:to-[#1B5E20] data-[state=active]:text-white data-[state=active]:shadow-md px-6 py-3 rounded-xl transition-all text-sm font-semibold text-gray-500 border border-transparent"
                            ),
                            class_name="bg-gray-100/80 p-1.5 rounded-2xl flex gap-2 w-full md:w-auto"
                        ),

                        rx.tabs.content(
                            rx.cond(
                                State.missing_exams_count > 0,
                                missing_exams_table(),
                                rx.box(
                                    rx.vstack(
                                        rx.icon("check-circle-2", size=48, class_name="text-green-500"),
                                        rx.text("Conformidade Total", class_name="text-xl font-bold text-green-800"),
                                        rx.text("Todos os exames do COMPULAB estão devidamente registrados no SIMUS.", class_name="text-gray-500"),
                                        align="center",
                                        spacing="2",
                                    ),
                                    class_name="bg-white border border-green-100 rounded-3xl p-12 mt-6 text-center shadow-sm"
                                ),
                            ),
                            value="missing",
                        ),

                        rx.tabs.content(
                            rx.cond(
                                State.divergences_count > 0,
                                divergences_table(),
                                rx.box(
                                    rx.vstack(
                                        rx.icon("check-circle-2", size=48, class_name="text-green-500"),
                                        rx.text("Valores Consistentes", class_name="text-xl font-bold text-green-800"),
                                        rx.text("Não foram encontradas divergências de valores entre os sistemas.", class_name="text-gray-500"),
                                        align="center",
                                        spacing="2",
                                    ),
                                    class_name="bg-white border border-green-100 rounded-3xl p-12 mt-6 text-center shadow-sm"
                                ),
                            ),
                            value="divergences",
                        ),

                        rx.tabs.content(
                            ai_analysis_section(),
                            value="ai",
                        ),
                        default_value="missing",
                        class_name="mt-8 w-full"
                    ),
                    
                    # Botões de ação e exportação
                    rx.box(
                        rx.hstack(
                            # Botão de Download PDF (só aparece se PDF foi gerado)
                            rx.cond(
                                State.analysis_pdf != "",
                                rx.link(
                                    rx.button(
                                        rx.hstack(
                                            rx.icon("download", size=18),
                                            rx.text("Baixar Relatório PDF"),
                                            spacing="2",
                                        ),
                                        class_name="bg-[#1B5E20] text-white px-6 py-3 rounded-xl hover:bg-[#2E7D32] hover:shadow-lg transition-all text-sm font-semibold"
                                    ),
                                    download="analise_compulab_simus.pdf",
                                    href=State.analysis_pdf,
                                    is_external=False,
                                ),
                            ),
                            # Botão de Gerar PDF (sempre disponível)
                            rx.button(
                                rx.cond(
                                    State.analysis_pdf != "",
                                    rx.hstack(
                                        rx.icon("file-text", size=18),
                                        rx.text("Gerar Novo PDF"),
                                        spacing="2",
                                    ),
                                    rx.hstack(
                                        rx.icon("file-text", size=18),
                                        rx.text("Gerar Relatório Oficial"),
                                        spacing="2",
                                    ),
                                ),
                                on_click=State.generate_pdf_report,
                                class_name="bg-white border border-[#1B5E20] text-[#1B5E20] px-6 py-3 rounded-xl hover:bg-green-50 transition-all text-sm font-semibold"
                            ),
                            rx.button(
                                rx.hstack(
                                    rx.icon("rotate-ccw", size=18),
                                    rx.text("Nova Análise"),
                                    spacing="2",
                                ),
                                on_click=State.clear_all_files,
                                class_name="bg-transparent text-gray-500 hover:text-gray-700 px-6 py-3 rounded-xl hover:bg-gray-100 transition-all text-sm font-medium"
                            ),
                            spacing="3",
                            justify="center",
                            wrap="wrap",
                            width="100%",
                        ),
                        class_name="mt-12 bg-gray-50 p-6 rounded-3xl border border-gray-100 w-full"
                    ),
                    
                    width="100%",
                    max_width="7xl",
                ),
            ),
            
            spacing="0",
            align="center",
            width="100%",
            class_name="py-8 px-4"
        ),
        width="100%",
    )
