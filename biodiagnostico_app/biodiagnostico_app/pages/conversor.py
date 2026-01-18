"""
Conversor PDF → CSV page
Design Premium SaaS - Clean & Clinical
"""
import reflex as rx
from ..state import State
from ..components.file_upload import file_upload_enhanced, upload_progress_indicator
from ..components.header import mini_header


def feature_card(icon: str, title: str, description: str) -> rx.Component:
    """Card de funcionalidade - Premium Style"""
    return rx.box(
        rx.vstack(
            rx.box(
                rx.text(icon, class_name="text-2xl"),
                class_name="w-12 h-12 flex items-center justify-center bg-green-50 rounded-2xl mb-2 group-hover:scale-110 transition-transform duration-300"
            ),
            rx.text(title, class_name="text-[#1B5E20] font-bold text-sm"),
            rx.text(description, class_name="text-gray-500 text-xs text-center"),
            spacing="1",
            align="center",
            width="100%",
        ),
        class_name="bg-white border border-gray-100 rounded-2xl p-6 hover:shadow-lg hover:shadow-green-900/5 transition-all duration-300 group cursor-default"
    )


def conversor_page() -> rx.Component:
    """Página do conversor PDF para CSV - Design oficial Premium"""
    
    # SVG do Erlenmeyer (COMPULAB) - Design refinado
    erlenmeyer_svg = """
        <svg viewBox="0 0 80 100" width="70" height="88" class="drop-shadow-md">
            <defs>
                <linearGradient id="liquidGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" style="stop-color:#81C784;stop-opacity:0.3" />
                    <stop offset="100%" style="stop-color:#4CAF50;stop-opacity:0.6" />
                </linearGradient>
            </defs>
            <path d="M28 10 L52 10 L52 35 L70 85 Q72 92 65 95 L15 95 Q8 92 10 85 L28 35 Z" 
                  fill="url(#liquidGrad)" stroke="#1B5E20" stroke-width="2"/>
            <rect x="26" y="5" width="28" height="8" rx="3" fill="none" stroke="#1B5E20" stroke-width="2"/>
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
        <svg viewBox="0 0 100 100" width="70" height="88" class="drop-shadow-md">
            <defs>
                <linearGradient id="tubeGrad1" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" style="stop-color:#81C784;stop-opacity:0.2" />
                    <stop offset="100%" style="stop-color:#4CAF50;stop-opacity:0.6" />
                </linearGradient>
            </defs>
            <!-- Tubo 1 -->
            <rect x="18" y="15" width="15" height="68" rx="7" fill="none" stroke="#1B5E20" stroke-width="2"/>
            <rect x="18" y="52" width="15" height="31" rx="7" fill="url(#tubeGrad1)"/>
            <!-- Tubo 2 -->
            <rect x="42" y="15" width="15" height="68" rx="7" fill="none" stroke="#1B5E20" stroke-width="2"/>
            <rect x="42" y="42" width="15" height="41" rx="7" fill="url(#tubeGrad1)"/>
            <!-- Tubo 3 -->
            <rect x="66" y="15" width="15" height="68" rx="7" fill="none" stroke="#1B5E20" stroke-width="2"/>
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
            
            # Título principal e subtítulo com melhor hierarquia
            rx.vstack(
                rx.text(
                    "Conversor PDF → CSV",
                    class_name="text-[#1B5E20] text-4xl md:text-5xl font-bold tracking-tight text-center"
                ),
                rx.text(
                    "Transforme seus relatórios clínicos em dados estruturados com precisão",
                    class_name="text-gray-500 text-lg mt-2 font-medium text-center max-w-2xl"
                ),
                spacing="0",
                align="center",
                class_name="mb-8"
            ),
            
            # Cards de funcionalidades - Grid mais limpo
            rx.grid(
                feature_card("📄", "Extração Inteligente", "Algoritmos avançados de parsing de PDF"),
                feature_card("🔄", "Padronização", "Normalização automática de nomenclatura"),
                feature_card("📊", "CSV Estruturado", "Output formatado para análise imediata"),
                feature_card("⚡", "Alta Performance", "Processamento otimizado em segundos"),
                columns="1 md:grid-cols-2 lg:grid-cols-4",
                spacing="4",
                width="100%",
                class_name="mb-12 max-w-5xl"
            ),
            
            # Container principal de upload - Card Flutuante
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.box(
                            rx.text("📁", class_name="text-xl"),
                            class_name="w-10 h-10 rounded-xl bg-green-50 flex items-center justify-center"
                        ),
                        rx.text(
                            "Área de Processamento",
                            class_name="text-[#1B5E20] font-bold text-lg"
                        ),
                        spacing="3",
                        align="center",
                        class_name="mb-4"
                    ),
                    
                    # Grid de uploads
                    rx.grid(
                        file_upload_enhanced(
                            title="COMPULAB",
                            subtitle="Relatório de faturamento PDF",
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
                            subtitle="Relatório de faturamento PDF",
                            icon_svg=tubes_svg,
                            upload_id="simus_conv",
                            file_name=State.simus_file_name,
                            file_size=State.simus_file_size,
                            on_upload=State.handle_simus_upload,
                            on_remove=State.clear_simus_file,
                            accepted_types="PDF",
                            accept_dict={"application/pdf": [".pdf"]},
                        ),
                        columns="1 md:grid-cols-2",
                        spacing="6",
                        width="100%",
                    ),
                    
                    # Progresso de upload
                    rx.box(
                        upload_progress_indicator(State.is_uploading, "Enviando arquivos para o servidor seguro..."),
                        class_name="w-full mt-4"
                    ),
                    
                    spacing="2",
                    width="100%",
                ),
                class_name="bg-white border border-gray-100 rounded-3xl p-8 max-w-5xl w-full shadow-xl shadow-gray-100"
            ),
            
            # Botão de conversão - Design destacado
            rx.box(
                rx.button(
                    rx.cond(
                        State.is_generating_csv,
                        rx.hstack(
                            rx.spinner(size="2", color="white"),
                            rx.text("Processando Conversão..."),
                            spacing="3",
                            align="center",
                        ),
                        rx.hstack(
                            rx.icon("refresh-cw", size=20),
                            rx.text("Iniciar Conversão"),
                            spacing="2",
                            align="center",
                        ),
                    ),
                    on_click=State.generate_csvs,
                    disabled=~State.has_files | State.is_generating_csv,
                    class_name="bg-gradient-to-r from-[#4CAF50] to-[#1B5E20] text-white px-10 py-4 rounded-xl font-bold text-lg shadow-lg shadow-green-900/20 hover:shadow-xl hover:-translate-y-1 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:shadow-none disabled:hover:translate-y-0"
                ),
                class_name="mt-8"
            ),
            
            # Indicador de progresso detalhado
            rx.cond(
                State.is_generating_csv,
                rx.box(
                    rx.vstack(
                        rx.text(
                            State.csv_progress_percentage.to_string() + "%",
                            class_name="text-[#1B5E20] text-4xl font-bold font-['Poppins'] text-center"
                        ),
                        rx.text(
                            State.csv_stage,
                            class_name="text-gray-500 text-sm font-medium text-center mt-1"
                        ),
                        # Barra de progresso
                        rx.box(
                            rx.box(
                                class_name="h-full bg-gradient-to-r from-[#4CAF50] to-[#1B5E20] rounded-full transition-all duration-300 relative overflow-hidden",
                                width=rx.cond(
                                    State.csv_progress_percentage > 0,
                                    State.csv_progress_percentage.to_string() + "%",
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
            
            # Mensagens de status
            rx.cond(
                State.success_message != "",
                rx.box(
                    rx.hstack(
                        rx.icon("check-circle-2", size=24, class_name="text-green-600"),
                        rx.text(State.success_message, class_name="text-green-800 font-medium"),
                        spacing="3",
                        align="center",
                    ),
                    class_name="bg-green-50 border border-green-200 rounded-xl p-4 mt-6 max-w-3xl w-full animate-fade-in"
                ),
            ),
            rx.cond(
                State.error_message != "",
                rx.box(
                    rx.hstack(
                        rx.icon("alert-triangle", size=24, class_name="text-red-600"),
                        rx.text(State.error_message, class_name="text-red-800 font-medium"),
                        spacing="3",
                        align="center",
                    ),
                    class_name="bg-red-50 border border-red-200 rounded-xl p-4 mt-6 max-w-3xl w-full animate-shake"
                ),
            ),
            
            # Área de Download
            rx.cond(
                State.csv_generated,
                rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.icon("party-popper", size=28, class_name="text-[#4CAF50]"),
                            rx.text(
                                "Conversão Concluída",
                                class_name="text-[#1B5E20] font-bold text-2xl"
                            ),
                            spacing="3",
                            align="center",
                        ),
                        rx.text(
                            "Seus arquivos foram padronizados e estão prontos para download",
                            class_name="text-gray-500 text-sm mb-4"
                        ),

                        rx.flex(
                            rx.link(
                                rx.button(
                                    rx.hstack(
                                        rx.icon("download", size=20),
                                        rx.vstack(
                                            rx.text("COMPULAB.csv", class_name="font-bold text-sm"),
                                            rx.text("Dados padronizados", class_name="text-[10px] opacity-80 font-normal"),
                                            spacing="0",
                                            align="start",
                                        ),
                                        spacing="3",
                                        align="center",
                                    ),
                                    class_name="bg-[#1B5E20] text-white pl-6 pr-8 py-4 rounded-xl hover:bg-[#2E7D32] hover:shadow-lg transition-all w-full sm:w-auto"
                                ),
                                download="compulab_data.csv",
                                href=rx.Var.create(f"data:text/csv;charset=utf-8,{State.compulab_csv}"),
                            ),
                            rx.link(
                                rx.button(
                                    rx.hstack(
                                        rx.icon("download", size=20),
                                        rx.vstack(
                                            rx.text("SIMUS.csv", class_name="font-bold text-sm"),
                                            rx.text("Dados padronizados", class_name="text-[10px] opacity-80 font-normal"),
                                            spacing="0",
                                            align="start",
                                        ),
                                        spacing="3",
                                        align="center",
                                    ),
                                    class_name="bg-[#1B5E20] text-white pl-6 pr-8 py-4 rounded-xl hover:bg-[#2E7D32] hover:shadow-lg transition-all w-full sm:w-auto"
                                ),
                                download="simus_data.csv",
                                href=rx.Var.create(f"data:text/csv;charset=utf-8,{State.simus_csv}"),
                            ),
                            spacing="4",
                            wrap="wrap",
                            justify="center",
                            width="100%",
                        ),

                        rx.divider(class_name="my-6 border-gray-200"),

                        # Botão para limpar e começar novo
                        rx.button(
                            rx.hstack(
                                rx.icon("rotate-ccw", size=16),
                                rx.text("Iniciar Nova Conversão"),
                                spacing="2",
                            ),
                            on_click=State.clear_all_files,
                            class_name="bg-white border border-gray-300 text-gray-600 px-6 py-2.5 rounded-lg hover:bg-gray-50 hover:text-gray-900 transition-all text-sm font-medium"
                        ),
                        spacing="4",
                        align="center",
                    ),
                    class_name="bg-gradient-to-br from-green-50/50 to-lime-50/50 border border-green-200 rounded-3xl p-8 mt-8 max-w-4xl w-full shadow-lg relative overflow-hidden"
                ),
            ),
            
            # Dica Informativa
            rx.cond(
                ~State.csv_generated,
                rx.box(
                    rx.hstack(
                        rx.icon("lightbulb", size=20, class_name="text-amber-500"),
                        rx.vstack(
                            rx.text(
                                "Padronização Automática",
                                class_name="text-gray-800 text-sm font-bold"
                            ),
                            rx.text(
                                "O sistema normaliza automaticamente nomes de exames para garantir compatibilidade total entre COMPULAB e SIMUS.",
                                class_name="text-gray-600 text-xs leading-relaxed"
                            ),
                            spacing="1",
                            align="start",
                        ),
                        spacing="3",
                        align="start",
                    ),
                    class_name="bg-amber-50/50 border border-amber-100 rounded-2xl p-5 mt-8 max-w-3xl w-full"
                ),
            ),
            
            spacing="0",
            align="center",
            width="100%",
            class_name="py-8 px-4"
        ),
        width="100%",
    )
