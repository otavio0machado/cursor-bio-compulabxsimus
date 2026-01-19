"""
Análise COMPULAB x SIMUS page
Design moderno com upload aprimorado
"""
import reflex as rx
from ..state import State
from ..components.file_upload import compact_upload_card, upload_progress_indicator, large_file_progress_indicator
from ..components import ui
from ..styles import Color


def metric_card(title: str, value: str, icon: str, subtitle: str = "", color: str = "green") -> rx.Component:
    """Card de métrica com design aprimorado"""
    bg_colors = {
        "green": "from-green-50 to-lime-50",
        "blue": "from-blue-50 to-cyan-50",
        "orange": "from-orange-50 to-amber-50",
        "red": "from-red-50 to-pink-50",
    }
    border_colors = {
        "green": "border-green-200",
        "blue": "border-blue-200",
        "orange": "border-orange-200",
        "red": "border-red-200",
    }
    
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.box(
                    rx.icon(icon, size=20, color=Color.DEEP),
                    class_name="w-10 h-10 flex items-center justify-center bg-white rounded-lg shadow-sm"
                ),
                rx.text(title, class_name="text-gray-500 text-sm font-medium"),
                spacing="2",
                align="center",
            ),
            rx.text(value, class_name="text-[#1B5E20] text-2xl font-bold"),
            rx.cond(
                subtitle != "",
                rx.text(subtitle, class_name="text-gray-400 text-xs"),
            ),
            spacing="1",
            align="start",
            width="100%",
        ),
        class_name=f"bg-gradient-to-br {bg_colors.get(color, bg_colors['green'])} border {border_colors.get(color, border_colors['green'])} rounded-xl p-4 hover:shadow-md transition-all"
    )


def breakdown_item(icon: str, label: str, value: str, color: str = "gray") -> rx.Component:
    """Item de breakdown da diferença"""
    text_colors = {
        "green": "text-green-600",
        "blue": "text-blue-600",
        "orange": "text-orange-600",
        "red": "text-red-600",
        "gray": "text-gray-600",
    }
    
    return rx.box(
        rx.vstack(
            rx.icon(icon, size=28, color=Color.DEEP),
            rx.text(label, class_name="text-gray-500 text-xs font-medium text-center"),
            rx.text(value, class_name=f"{text_colors.get(color, 'text-gray-600')} font-bold text-sm"),
            spacing="1",
            align="center",
        ),
        class_name="bg-white border border-gray-100 rounded-xl p-4 hover:shadow-md transition-all flex-1"
    )


def analise_page() -> rx.Component:
    """Página de análise comparativa - Design oficial aprimorado"""
    
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
            # Animated Header
            rx.box(
                ui.animated_heading("Análise COMPULAB × SIMUS", level=1),
                class_name="py-12 w-full flex justify-center"
            ),
            
            # Upload section
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.text("📁", class_name="text-lg"),
                        rx.text(
                            "Upload de Arquivos",
                            class_name="text-[#1B5E20] font-semibold"
                        ),
                        spacing="2",
                        align="center",
                    ),
                    rx.text(
                        "Aceita arquivos PDF ou CSV",
                        class_name="text-gray-500 text-xs mb-3"
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
                        columns="2",
                        spacing="4",
                        width="100%",
                    ),
                    upload_progress_indicator(State.is_uploading, "Carregando arquivo..."),
                    spacing="2",
                    width="100%",
                ),
                class_name="bg-white border border-gray-200 rounded-2xl p-5 mt-8 max-w-xl w-full shadow-sm"
            ),
            
            # Botão de análise
            rx.button(
                rx.cond(
                    State.is_analyzing,
                    rx.hstack(
                        rx.spinner(size="1", color="white"),
                        rx.text("Analisando dados..."),
                        spacing="2",
                        align="center",
                    ),
                    rx.hstack(
                        rx.text("🔍"),
                        rx.text("Analisar Faturamento"),
                        spacing="2",
                        align="center",
                    ),
                ),
                on_click=State.run_analysis,
                disabled=~State.has_files | State.is_analyzing,
                class_name="bg-[#1B5E20] text-white px-8 py-3 rounded-xl font-semibold hover:bg-[#2E7D32] hover:shadow-lg transition-all mt-6 disabled:opacity-50 disabled:cursor-not-allowed"
            ),
            
            # Indicador de progresso
            rx.cond(
                State.is_analyzing,
                rx.box(
                    rx.vstack(
                        rx.text(
                            State.analysis_progress_percentage.to_string() + "%",
                            class_name="text-[#1B5E20] text-3xl font-bold text-center"
                        ),
                        rx.text(
                            State.analysis_stage,
                            class_name="text-gray-600 text-sm text-center mt-1"
                        ),
                        # Barra de progresso
                        rx.box(
                            rx.box(
                                class_name="h-full bg-[#4CAF50] rounded-full transition-all duration-300",
                                width=rx.cond(
                                    State.analysis_progress_percentage > 0,
                                    State.analysis_progress_percentage.to_string() + "%",
                                    "0%"
                                ),
                            ),
                            class_name="w-full h-3 bg-gray-200 rounded-full overflow-hidden mt-4",
                        ),
                        spacing="2",
                        align="center",
                    ),
                    class_name="bg-white border border-gray-200 rounded-xl p-6 mt-4 max-w-4xl w-full shadow-sm"
                ),
            ),
            
            # Mensagens
            rx.cond(
                State.success_message != "",
                rx.box(
                    rx.hstack(
                        rx.text("✅"),
                        rx.text(State.success_message, class_name="text-green-700"),
                        spacing="2",
                    ),
                    class_name="bg-green-50 border border-green-200 rounded-xl p-4 mt-4 max-w-xl w-full"
                ),
            ),
            rx.cond(
                State.error_message != "",
                rx.box(
                    rx.hstack(
                        rx.text("❌"),
                        rx.text(State.error_message, class_name="text-red-700"),
                        spacing="2",
                    ),
                    class_name="bg-red-50 border border-red-200 rounded-xl p-4 mt-4 max-w-xl w-full"
                ),
            ),
            
            # Resultados
            rx.cond(
                State.has_analysis,
                rx.vstack(
                    # Métricas principais
                    rx.box(
                        rx.vstack(
                            rx.hstack(
                                rx.icon("bar-chart-2", size=20, color=Color.DEEP),
                                rx.text(
                                    "Resumo da Análise",
                                    class_name="text-[#1B5E20] font-semibold text-lg"
                                ),
                                spacing="2",
                                align="center",
                            ),
                            rx.grid(
                                metric_card("COMPULAB Total", State.formatted_compulab_total, "dollar-sign", f"{State.compulab_count} pacientes", "green"),
                                metric_card("SIMUS Total", State.formatted_simus_total, "wallet", f"{State.simus_count} pacientes", "blue"),
                                metric_card("Diferença", State.formatted_difference, "trending-down", "COMPULAB - SIMUS", "orange"),
                                metric_card("Exames Faltantes", f"{State.missing_exams_count}", "triangle-alert", "no SIMUS", "red"),
                                columns="4",
                                spacing="4",
                                width="100%",
                                class_name="mt-4"
                            ),
                            width="100%",
                        ),
                        class_name="bg-white border border-gray-200 rounded-2xl p-6 mt-8 w-full shadow-sm"
                    ),
                    
                    # Breakdown da diferença
                    rx.box(
                        rx.vstack(
                            rx.hstack(
                                rx.icon("compass", size=20, color=Color.DEEP),
                                rx.text(
                                    "Por que existe essa diferença?",
                                    class_name="text-[#1B5E20] font-semibold text-lg"
                                ),
                                spacing="2",
                                align="center",
                            ),
                            rx.hstack(
                                breakdown_item("user-x", "Pacientes Faltantes", State.formatted_missing_patients_total, "orange"),
                                breakdown_item("file-x", "Exames Faltantes", State.formatted_missing_exams_total, "red"),
                                breakdown_item("diff", "Divergências de Valor", State.formatted_divergences_total, "blue"),
                                spacing="4",
                                width="100%",
                                class_name="mt-4"
                            ),
                            width="100%",
                        ),
                        class_name="bg-gradient-to-br from-gray-50 to-white border border-gray-200 rounded-2xl p-6 mt-4 w-full shadow-sm"
                    ),
                    
                    # Tabs de detalhes
                    rx.tabs.root(
                        rx.tabs.list(
                            rx.tabs.trigger(
                                rx.hstack(
                                    rx.icon("triangle-alert", size=16),
                                    rx.text(f"Exames Faltantes ({State.missing_exams_count})"),
                                    spacing="2",
                                ),
                                value="missing",
                                class_name="data-[state=active]:bg-[#1B5E20] data-[state=active]:text-white px-4 py-2 rounded-lg transition-all text-sm font-medium"
                            ),
                            rx.tabs.trigger(
                                rx.hstack(
                                    rx.icon("dollar-sign", size=16),
                                    rx.text(f"Divergências ({State.divergences_count})"),
                                    spacing="2",
                                ),
                                value="divergences",
                                class_name="data-[state=active]:bg-[#1B5E20] data-[state=active]:text-white px-4 py-2 rounded-lg transition-all text-sm font-medium"
                            ),
                            rx.tabs.trigger(
                                rx.hstack(
                                    rx.icon("bot", size=16),
                                    rx.text("Análise IA"),
                                    spacing="2",
                                ),
                                value="ai",
                                class_name="data-[state=active]:bg-[#1B5E20] data-[state=active]:text-white px-4 py-2 rounded-lg transition-all text-sm font-medium"
                            ),
                            class_name="bg-white border border-gray-200 p-1 rounded-xl flex gap-1 shadow-sm justify-center"
                        ),
                        rx.tabs.content(
                            rx.cond(
                                State.missing_exams_count > 0,
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
                                    ),
                                    class_name="bg-white rounded-xl p-4 mt-4 border border-gray-100"
                                ),
                                rx.box(
                                    rx.hstack(
                                        rx.icon("circle-check", size=20, color="#10B981"),
                                        rx.text("Todos os exames estão registrados no SIMUS!", class_name="text-green-700"),
                                        spacing="2",
                                        align="center",
                                    ),
                                    class_name="bg-green-50 border border-green-200 rounded-xl p-6 mt-4"
                                ),
                            ),
                            value="missing",
                        ),
                        rx.tabs.content(
                            rx.cond(
                                State.divergences_count > 0,
                                rx.box(
                                    rx.data_table(
                                        data=State.value_divergences,
                                        columns=[
                                            {"name": "patient", "label": "Paciente"},
                                            {"name": "exam_name", "label": "Exame"},
                                            {"name": "compulab_value", "label": "COMPULAB"},
                                            {"name": "simus_value", "label": "SIMUS"},
                                            {"name": "difference", "label": "Diferença"},
                                        ],
                                        pagination=True,
                                        search=True,
                                        sort=True,
                                    ),
                                    class_name="bg-white rounded-xl p-4 mt-4 border border-gray-100"
                                ),
                                rx.box(
                                    rx.hstack(
                                        rx.icon("circle-check", size=20, color="#10B981"),
                                        rx.text("Não há divergências de valores entre os sistemas!", class_name="text-green-700"),
                                        spacing="2",
                                        align="center",
                                    ),
                                    class_name="bg-green-50 border border-green-200 rounded-xl p-6 mt-4"
                                ),
                            ),
                            value="divergences",
                        ),
                        rx.tabs.content(
                            rx.vstack(
                                # Header Premium
                                rx.box(
                                    rx.hstack(
                                        rx.box(
                                            rx.text("🤖", class_name="text-2xl"),
                                            class_name="bg-white/20 p-2 rounded-lg"
                                        ),
                                        rx.vstack(
                                            rx.text(
                                                "Auditoria Inteligente",
                                                class_name="text-white font-bold text-lg"
                                            ),
                                            rx.text(
                                                "Análise automatizada por OpenAI GPT-4",
                                                class_name="text-white/80 text-xs"
                                            ),
                                            spacing="0",
                                            align="start",
                                        ),
                                        spacing="3",
                                        align="center",
                                    ),
                                    class_name="bg-gradient-to-r from-emerald-600 via-green-600 to-teal-600 p-4 rounded-xl mb-4"
                                ),
                                
                                # Features Row
                                rx.hstack(
                                    rx.box(
                                        rx.vstack(
                                            rx.text("⚡", class_name="text-xl"),
                                            rx.text("Paralelo", class_name="text-xs font-medium text-gray-600"),
                                            spacing="0",
                                            align="center",
                                        ),
                                        class_name="bg-gray-50 p-2 rounded-lg flex-1 text-center"
                                    ),
                                    rx.box(
                                        rx.vstack(
                                            rx.text("🎯", class_name="text-xl"),
                                            rx.text("0.02 Precisão", class_name="text-xs font-medium text-gray-600"),
                                            spacing="0",
                                            align="center",
                                        ),
                                        class_name="bg-gray-50 p-2 rounded-lg flex-1 text-center"
                                    ),
                                    rx.box(
                                        rx.vstack(
                                            rx.text("📊", class_name="text-xl"),
                                            rx.text("CSV + PDF", class_name="text-xs font-medium text-gray-600"),
                                            spacing="0",
                                            align="center",
                                        ),
                                        class_name="bg-gray-50 p-2 rounded-lg flex-1 text-center"
                                    ),
                                    spacing="2",
                                    width="100%",
                                    class_name="mb-4"
                                ),
                                
                                # API Key / Action Area
                                rx.cond(
                                    State.openai_api_key == "",
                                    rx.box(
                                        rx.vstack(
                                            rx.hstack(
                                                rx.icon("key", size=18, color="#D97706"),
                                                rx.text("Configure sua API Key", class_name="text-amber-800 font-semibold"),
                                                spacing="2",
                                            ),
                                            rx.input(
                                                placeholder="sk-... (Cole sua API Key da OpenAI)",
                                                type="password",
                                                on_change=State.set_api_key,
                                                class_name="w-full bg-white border-amber-300 rounded-lg"
                                            ),
                                            rx.link(
                                                rx.text("🔑 Obter API Key grátis", class_name="text-sm text-amber-700 hover:text-amber-900"),
                                                href="https://platform.openai.com/api-keys",
                                                is_external=True,
                                            ),
                                            spacing="3",
                                            width="100%",
                                        ),
                                        class_name="bg-gradient-to-r from-amber-50 to-yellow-50 border border-amber-200 rounded-xl p-4"
                                    ),
                                    rx.vstack(
                                        # Status + Progress
                                        rx.hstack(
                                            rx.box(class_name="w-3 h-3 bg-green-500 rounded-full animate-pulse"),
                                            rx.text("API Conectada", class_name="text-green-700 text-sm font-medium"),
                                            spacing="2",
                                        ),
                                        
                                        rx.cond(
                                            State.is_generating_ai,
                                            rx.box(
                                                rx.vstack(
                                                    rx.hstack(
                                                        rx.spinner(size="1", color="green"),
                                                        rx.text(State.ai_loading_text, class_name="text-sm font-medium text-gray-700"),
                                                        spacing="2",
                                                    ),
                                                    rx.progress(
                                                        value=State.ai_loading_progress,
                                                        max=100,
                                                        class_name="w-full h-2 rounded-full",
                                                        color_scheme="green"
                                                    ),
                                                    spacing="2",
                                                    width="100%"
                                                ),
                                                class_name="bg-green-50 p-3 rounded-lg w-full"
                                            ),
                                        ),
                                        
                                        # Main Button
                                        rx.button(
                                            rx.hstack(
                                                rx.cond(
                                                    State.is_generating_ai,
                                                    rx.spinner(size="1", color="white"),
                                                    rx.text("🚀", class_name=""),
                                                ),
                                                rx.text("Iniciar Auditoria Inteligente"),
                                                spacing="2",
                                            ),
                                            on_click=State.generate_ai_analysis,
                                            disabled=State.is_generating_ai,
                                            class_name="bg-gradient-to-r from-emerald-500 to-green-600 text-white px-6 py-3 rounded-xl font-bold hover:from-emerald-600 hover:to-green-700 hover:shadow-lg transition-all w-full disabled:opacity-50"
                                        ),
                                        
                                        # Results Area
                                        rx.cond(
                                            State.ai_analysis != "",
                                            rx.vstack(
                                                # Header do resultado
                                                rx.hstack(
                                                    rx.text("📊", class_name="text-xl"),
                                                    rx.text(
                                                        "Divergências Encontradas",
                                                        class_name="text-green-800 font-bold"
                                                    ),
                                                    spacing="2",
                                                    align="center",
                                                ),
                                                # Resultado em Markdown (evita erro de hook)
                                                rx.box(
                                                    rx.scroll_area(
                                                        rx.markdown(State.ai_analysis),
                                                        type="hover",
                                                        scrollbars="vertical",
                                                        style={"maxHeight": "400px"},
                                                    ),
                                                    class_name="bg-white rounded-xl p-4 border border-gray-100 mt-4 prose prose-sm max-w-none"
                                                ),
                                                # Download Buttons
                                                rx.hstack(
                                                    rx.cond(
                                                        State.ai_analysis_csv != "",
                                                        rx.link(
                                                            rx.button(
                                                                rx.hstack(
                                                                    rx.icon("table", size=14, color="white"),
                                                                    rx.text("CSV"),
                                                                    spacing="1",
                                                                ),
                                                                class_name="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-blue-700"
                                                            ),
                                                            href=State.ai_analysis_csv,
                                                            download="Auditoria_IA.csv",
                                                        ),
                                                    ),
                                                    rx.cond(
                                                        State.analysis_pdf != "",
                                                        rx.link(
                                                            rx.button(
                                                                rx.hstack(
                                                                    rx.icon("file-text", size=14, color="white"),
                                                                    rx.text("PDF"),
                                                                    spacing="1",
                                                                ),
                                                                class_name="bg-green-600 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-green-700"
                                                            ),
                                                            href=State.analysis_pdf,
                                                            download="Relatorio_IA.pdf",
                                                        ),
                                                        rx.button(
                                                            rx.hstack(
                                                                rx.icon("file-plus", size=14),
                                                                rx.text("Gerar PDF"),
                                                                spacing="1",
                                                            ),
                                                            on_click=State.generate_pdf_report,
                                                            class_name="border-2 border-green-600 text-green-700 px-4 py-2 rounded-lg text-sm font-semibold hover:bg-green-50"
                                                        ),
                                                    ),
                                                    # Botão Refazer Auditoria
                                                    rx.button(
                                                        rx.hstack(
                                                            rx.icon("rotate-ccw", size=14),
                                                            rx.text("Refazer"),
                                                            spacing="1",
                                                        ),
                                                        on_click=State.generate_ai_analysis,
                                                        class_name="border-2 border-orange-500 text-orange-600 px-4 py-2 rounded-lg text-sm font-semibold hover:bg-orange-50"
                                                    ),
                                                    spacing="2",
                                                    class_name="mt-3"
                                                ),
                                                spacing="3",
                                                width="100%",
                                            ),
                                        ),
                                        spacing="4",
                                        width="100%",
                                    ),
                                ),
                                spacing="2",
                                width="100%",
                                class_name="mt-4"
                            ),
                            value="ai",
                        ),
                        default_value="missing",
                        class_name="mt-6 w-full bg-white border border-gray-200 rounded-2xl p-4 shadow-sm"
                    ),
                    
                    # Botões de ação
                    rx.hstack(
                        # Botão de Download PDF (só aparece se PDF foi gerado)
                        rx.cond(
                            State.analysis_pdf != "",
                            rx.link(
                                rx.button(
                                    rx.hstack(
                                        rx.icon("download", size=16, color="white"),
                                        rx.text("Download PDF"),
                                        spacing="2",
                                    ),
                                    class_name="bg-[#1B5E20] text-white px-6 py-2 rounded-lg hover:bg-[#2E7D32] hover:shadow-lg transition-all text-sm font-semibold"
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
                                    rx.icon("file-text", size=16, color="white"),
                                    rx.text("Gerar Novo PDF"),
                                    spacing="2",
                                ),
                                rx.hstack(
                                    rx.icon("file-text", size=16, color="white"),
                                    rx.text("Gerar PDF"),
                                    spacing="2",
                                ),
                            ),
                            on_click=State.generate_pdf_report,
                            class_name="bg-[#1B5E20] text-white px-6 py-2 rounded-lg hover:bg-[#2E7D32] hover:shadow-lg transition-all text-sm font-semibold"
                        ),
                        rx.button(
                            rx.hstack(
                                rx.icon("refresh-cw", size=16),
                                rx.text("Nova Análise"),
                                spacing="2",
                            ),
                            on_click=State.clear_all_files,
                            class_name="bg-transparent border border-gray-300 text-gray-600 px-4 py-2 rounded-lg hover:bg-gray-50 transition-all text-sm"
                        ),
                        spacing="3",
                        justify="center",
                        class_name="mt-6"
                    ),
                    
                    width="100%",
                    max_width="5xl",
                ),
            ),
            
            spacing="0",
            align="center",
            width="100%",
            class_name="py-8 px-4"
        ),
        width="100%",
    )
