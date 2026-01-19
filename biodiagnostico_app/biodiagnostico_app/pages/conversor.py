"""
Conversor PDF → CSV page
Design moderno com upload aprimorado
"""
import reflex as rx
from ..state import State
from ..components.file_upload import file_upload_enhanced, upload_progress_indicator, file_type_badge
from ..components import ui
from ..styles import Color


def feature_card(icon: str, title: str, description: str) -> rx.Component:
    """Card de funcionalidade"""
    return ui.card(
        rx.hstack(
            rx.box(
                rx.icon(icon, size=24, color=Color.PRIMARY),
                class_name="p-3 rounded-xl bg-green-50"
            ),
            rx.vstack(
                ui.text(title, size="label", color=Color.DEEP),
                ui.text(description, size="small"),
                spacing="0",
                align="start",
            ),
            spacing="3",
            align="center",
        ),
    )


def conversor_page() -> rx.Component:
    """Página do conversor PDF para CSV - Design oficial aprimorado"""
    
    # SVG do Erlenmeyer (COMPULAB) - Design refinado
    erlenmeyer_svg = """
        <svg viewBox="0 0 80 100" width="70" height="88" class="drop-shadow-sm">
            <defs>
                <linearGradient id="liquidGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" style="stop-color:#81C784;stop-opacity:0.3" />
                    <stop offset="100%" style="stop-color:#4CAF50;stop-opacity:0.5" />
                </linearGradient>
            </defs>
            <path d="M28 10 L52 10 L52 35 L70 85 Q72 92 65 95 L15 95 Q8 92 10 85 L28 35 Z" 
                  fill="url(#liquidGrad)" stroke="#1B5E20" stroke-width="2.5"/>
            <rect x="26" y="5" width="28" height="8" rx="3" fill="none" stroke="#1B5E20" stroke-width="2.5"/>
            <ellipse cx="40" cy="75" rx="20" ry="8" fill="#4CAF50" opacity="0.2"/>
            <circle cx="48" cy="60" r="4" fill="#4CAF50" opacity="0.6">
                <animate attributeName="cy" values="60;55;60" dur="2s" repeatCount="indefinite"/>
            </circle>
            <circle cx="35" cy="68" r="3" fill="#4CAF50" opacity="0.4">
                <animate attributeName="cy" values="68;62;68" dur="1.5s" repeatCount="indefinite"/>
            </circle>
        </svg>
    """
    
    # SVG dos Tubos de ensaio (SIMUS) - Design refinado
    tubes_svg = """
        <svg viewBox="0 0 100 100" width="70" height="88" class="drop-shadow-sm">
            <defs>
                <linearGradient id="tubeGrad1" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" style="stop-color:#81C784;stop-opacity:0.2" />
                    <stop offset="100%" style="stop-color:#4CAF50;stop-opacity:0.5" />
                </linearGradient>
            </defs>
            <!-- Tubo 1 -->
            <rect x="18" y="15" width="15" height="68" rx="7" fill="none" stroke="#1B5E20" stroke-width="2.5"/>
            <rect x="18" y="52" width="15" height="31" rx="7" fill="url(#tubeGrad1)"/>
            <!-- Tubo 2 -->
            <rect x="42" y="15" width="15" height="68" rx="7" fill="none" stroke="#1B5E20" stroke-width="2.5"/>
            <rect x="42" y="42" width="15" height="41" rx="7" fill="url(#tubeGrad1)"/>
            <!-- Tubo 3 -->
            <rect x="66" y="15" width="15" height="68" rx="7" fill="none" stroke="#1B5E20" stroke-width="2.5"/>
            <rect x="66" y="58" width="15" height="25" rx="7" fill="url(#tubeGrad1)"/>
            <!-- Upload badge -->
            <circle cx="81" cy="75" r="10" fill="#4CAF50">
                <animate attributeName="r" values="10;11;10" dur="1.5s" repeatCount="indefinite"/>
            </circle>
            <path d="M81 72 L81 78 M78 75 L81 72 L84 75" stroke="white" stroke-width="2" fill="none" stroke-linecap="round"/>
        </svg>
    """
    
    return rx.box(
        rx.vstack(
            # Animated Header
            rx.box(
                ui.animated_heading("Conversor PDF → CSV", level=1),
                class_name="py-12 w-full flex justify-center"
            ),
            
            # Cards de funcionalidades
            rx.grid(
                feature_card("file-text", "Extração Inteligente", "Extrai dados automaticamente dos PDFs"),
                feature_card("refresh-cw", "Padronização", "Normaliza nomes de exames e pacientes"),
                feature_card("bar-chart-2", "CSV Estruturado", "Gera arquivos prontos para análise"),
                feature_card("zap", "Processamento Rápido", "Conversão em segundos"),
                columns="4",
                spacing="4",
                width="100%",
                class_name="max-w-4xl hidden md:grid"
            ),

            
            # Container principal de upload
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.text("📁", class_name="text-xl"),
                        rx.text(
                            "Upload de Arquivos",
                            class_name="text-[#1B5E20] font-semibold text-lg"
                        ),
                        spacing="2",
                        align="center",
                    ),
                    rx.text(
                        "Arraste seus arquivos ou clique para selecionar",
                        class_name="text-gray-500 text-sm mb-4"
                    ),
                    
                    # Grid de uploads
                    rx.grid(
                        file_upload_enhanced(
                            title="COMPULAB",
                            subtitle="Relatório de faturamento COMPULAB",
                            icon_svg=erlenmeyer_svg,
                            upload_id="compulab_conv",
                            file_name=State.compulab_file_name,
                            file_size=State.compulab_file_size,
                            on_upload=State.handle_compulab_upload,
                            on_remove=State.clear_compulab_file,
                            accepted_types="PDF",
                            accept_dict={"application/pdf": [".pdf"]},
                        ),
                        file_upload_enhanced(
                            title="SIMUS",
                            subtitle="Relatório de faturamento SIMUS",
                            icon_svg=tubes_svg,
                            upload_id="simus_conv",
                            file_name=State.simus_file_name,
                            file_size=State.simus_file_size,
                            on_upload=State.handle_simus_upload,
                            on_remove=State.clear_simus_file,
                            accepted_types="PDF",
                            accept_dict={"application/pdf": [".pdf"]},
                        ),
                        columns="2",
                        spacing="6",
                        width="100%",
                    ),
                    
                    # Progresso de upload
                    upload_progress_indicator(State.is_uploading, "Carregando arquivo..."),
                    
                    spacing="2",
                    width="100%",
                ),
                class_name="bg-white border border-gray-200 rounded-2xl p-6 mt-8 max-w-4xl w-full shadow-sm"
            ),
            
            # Botão de conversão
            rx.button(
                rx.cond(
                    State.is_generating_csv,
                    rx.hstack(
                        rx.spinner(size="1", color="white"),
                        rx.text("Convertendo arquivos..."),
                        spacing="2",
                        align="center",
                    ),
                    rx.hstack(
                        rx.text("🔄"),
                        rx.text("Converter para CSV"),
                        spacing="2",
                        align="center",
                    ),
                ),
                on_click=State.generate_csvs,
                disabled=~State.has_files | State.is_generating_csv,
                class_name="bg-[#1B5E20] text-white px-8 py-3 rounded-xl font-semibold hover:bg-[#2E7D32] hover:shadow-lg transition-all mt-6 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:shadow-none"
            ),
            
            # Indicador de progresso
            rx.cond(
                State.is_generating_csv,
                rx.box(
                    rx.vstack(
                        rx.text(
                            State.csv_progress_percentage.to_string() + "%",
                            class_name="text-[#1B5E20] text-3xl font-bold text-center"
                        ),
                        rx.text(
                            State.csv_stage,
                            class_name="text-gray-600 text-sm text-center mt-1"
                        ),
                        # Barra de progresso
                        rx.box(
                            rx.box(
                                class_name="h-full bg-[#4CAF50] rounded-full transition-all duration-300",
                                width=rx.cond(
                                    State.csv_progress_percentage > 0,
                                    State.csv_progress_percentage.to_string() + "%",
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
            
            # Mensagens de status
            rx.cond(
                State.success_message != "",
                rx.box(
                    rx.hstack(
                        rx.icon("check-circle", size=20, color="#15803d"),
                        rx.text(State.success_message, class_name="text-green-700"),
                        spacing="2",
                        align="center",
                    ),
                    class_name="bg-green-50 border border-green-200 text-green-700 rounded-xl p-4 mt-4 max-w-4xl w-full"
                ),
            ),
            rx.cond(
                State.error_message != "",
                rx.box(
                    rx.hstack(
                        rx.icon("x-circle", size=20, color="#dc2626"),
                        rx.text(State.error_message, class_name="text-red-700"),
                        spacing="2",
                        align="center",
                    ),
                    class_name="bg-red-50 border border-red-200 text-red-700 rounded-xl p-4 mt-4 max-w-4xl w-full"
                ),
            ),
            
            # Downloads dos CSVs
            rx.cond(
                State.csv_generated,
                rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.text("🎉", class_name="text-2xl"),
                            rx.text(
                                "CSVs gerados com sucesso!",
                                class_name="text-[#1B5E20] font-bold text-xl"
                            ),
                            spacing="2",
                            align="center",
                        ),
                        rx.text(
                            "Clique nos botões abaixo para baixar os arquivos",
                            class_name="text-gray-500 text-sm"
                        ),
                        rx.hstack(
                            rx.link(
                                rx.button(
                                    rx.hstack(
                                        rx.text("📥", class_name="text-lg"),
                                        rx.vstack(
                                            rx.text("COMPULAB.csv", class_name="font-semibold"),
                                            rx.text("Dados padronizados", class_name="text-xs opacity-80"),
                                            spacing="0",
                                            align="start",
                                        ),
                                        spacing="3",
                                        align="center",
                                    ),
                                    class_name="bg-[#1B5E20] text-white px-6 py-3 rounded-xl font-medium hover:bg-[#2E7D32] hover:shadow-lg transition-all"
                                ),
                                download="compulab_data.csv",
                                href=rx.Var.create(f"data:text/csv;charset=utf-8,{State.compulab_csv}"),
                            ),
                            rx.link(
                                rx.button(
                                    rx.hstack(
                                        rx.text("📥", class_name="text-lg"),
                                        rx.vstack(
                                            rx.text("SIMUS.csv", class_name="font-semibold"),
                                            rx.text("Dados padronizados", class_name="text-xs opacity-80"),
                                            spacing="0",
                                            align="start",
                                        ),
                                        spacing="3",
                                        align="center",
                                    ),
                                    class_name="bg-[#1B5E20] text-white px-6 py-3 rounded-xl font-medium hover:bg-[#2E7D32] hover:shadow-lg transition-all"
                                ),
                                download="simus_data.csv",
                                href=rx.Var.create(f"data:text/csv;charset=utf-8,{State.simus_csv}"),
                            ),
                            spacing="4",
                            justify="center",
                        ),
                        # Botão para limpar e começar novo
                        rx.button(
                            rx.hstack(
                                rx.text("🔄"),
                                rx.text("Nova Conversão"),
                                spacing="2",
                            ),
                            on_click=State.clear_all_files,
                            class_name="bg-transparent border border-gray-300 text-gray-600 px-4 py-2 rounded-lg hover:bg-gray-50 transition-all text-sm mt-4"
                        ),
                        spacing="4",
                        align="center",
                    ),
                    class_name="bg-gradient-to-br from-green-50 to-lime-50 border border-green-200 rounded-2xl p-8 mt-6 max-w-4xl w-full shadow-sm"
                ),
            ),
            
            # Dica
            rx.cond(
                ~State.csv_generated,
                rx.box(
                    rx.hstack(
                        rx.text("💡", class_name="text-lg"),
                        rx.vstack(
                            rx.text(
                                "Dica: Os arquivos gerados terão os nomes de exames padronizados",
                                class_name="text-gray-600 text-sm font-medium"
                            ),
                            rx.text(
                                "Isso facilita a comparação entre COMPULAB e SIMUS",
                                class_name="text-gray-500 text-xs"
                            ),
                            spacing="0",
                            align="start",
                        ),
                        spacing="3",
                        align="start",
                    ),
                    class_name="bg-amber-50 border border-amber-200 rounded-xl p-4 mt-6 max-w-4xl w-full"
                ),
            ),
            
            spacing="0",
            align="center",
            width="100%",
            class_name="py-8 px-4"
        ),
        width="100%",
    )
