"""
Conversor PDF → CSV page
Design moderno com upload aprimorado
"""
import reflex as rx
import base64
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

            # Feature 4: Custom Mapping Editor
            rx.box(
                rx.accordion.root(
                    rx.accordion.item(
                        header=rx.accordion.header(
                            rx.hstack(
                                rx.icon("settings", size=18, color="#1B5E20"),
                                rx.text("⚙️ Configurações Avançadas de Mapeamento", class_name="font-semibold text-[#1B5E20]"),
                                spacing="2",
                            ),
                        ),
                        content=rx.accordion.content(
                            rx.vstack(
                                rx.text(
                                    "Adicione mapeamentos customizados para nomes de exames que não são reconhecidos automaticamente:",
                                    class_name="text-gray-600 text-sm mb-4"
                                ),

                                # Inputs para adicionar mapeamento
                                rx.grid(
                                    rx.vstack(
                                        rx.text("Nome Original (SIMUS)", class_name="text-xs font-medium text-gray-700 mb-1"),
                                        rx.input(
                                            placeholder="Ex: DOSAGEM DE GLICOSE",
                                            value=State.mapping_original_name,
                                            on_change=State.set_mapping_original_name,
                                            class_name="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#1B5E20] focus:border-transparent"
                                        ),
                                        spacing="0",
                                        align="start",
                                    ),
                                    rx.vstack(
                                        rx.text("Nome Correto (COMPULAB)", class_name="text-xs font-medium text-gray-700 mb-1"),
                                        rx.input(
                                            placeholder="Ex: GLICOSE",
                                            value=State.mapping_correct_name,
                                            on_change=State.set_mapping_correct_name,
                                            class_name="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#1B5E20] focus:border-transparent"
                                        ),
                                        spacing="0",
                                        align="start",
                                    ),
                                    columns="2",
                                    spacing="4",
                                    width="100%",
                                ),

                                rx.button(
                                    rx.hstack(
                                        rx.icon("plus", size=16),
                                        rx.text("Adicionar Regra"),
                                        spacing="2",
                                    ),
                                    on_click=State.add_custom_mapping,
                                    class_name="bg-[#1B5E20] text-white px-4 py-2 rounded-lg hover:bg-[#2E7D32] transition-all text-sm mt-3"
                                ),

                                # Mensagens de feedback
                                rx.cond(
                                    State.mapping_success_message != "",
                                    rx.text(State.mapping_success_message, class_name="text-green-600 text-sm mt-2"),
                                ),
                                rx.cond(
                                    State.mapping_error_message != "",
                                    rx.text(State.mapping_error_message, class_name="text-red-600 text-sm mt-2"),
                                ),

                                # Lista de mapeamentos ativos
                                rx.cond(
                                    State.custom_mappings.length() > 0,
                                    rx.vstack(
                                        rx.divider(class_name="my-4"),
                                        rx.text("Mapeamentos Ativos:", class_name="font-semibold text-gray-700 text-sm mb-2"),
                                        rx.foreach(
                                            State.custom_mappings,
                                            lambda key, value: rx.hstack(
                                                rx.box(
                                                    rx.hstack(
                                                        rx.text(key, class_name="text-xs font-mono text-gray-700"),
                                                        rx.icon("arrow-right", size=14, color="gray"),
                                                        rx.text(value, class_name="text-xs font-mono text-[#1B5E20] font-semibold"),
                                                        spacing="2",
                                                    ),
                                                    class_name="flex-1"
                                                ),
                                                rx.button(
                                                    rx.icon("x", size=14),
                                                    on_click=lambda: State.remove_custom_mapping(key),
                                                    class_name="bg-red-50 text-red-600 hover:bg-red-100 p-1 rounded transition-all"
                                                ),
                                                spacing="2",
                                                align="center",
                                                class_name="bg-gray-50 border border-gray-200 rounded-lg p-3 w-full"
                                            )
                                        ),
                                        rx.button(
                                            rx.hstack(
                                                rx.icon("trash-2", size=14),
                                                rx.text("Limpar Todos"),
                                                spacing="2",
                                            ),
                                            on_click=State.clear_all_mappings,
                                            class_name="bg-red-50 text-red-600 hover:bg-red-100 px-3 py-1 rounded text-xs transition-all mt-2"
                                        ),
                                        spacing="2",
                                        width="100%",
                                        align="start",
                                    ),
                                ),

                                spacing="2",
                                width="100%",
                            ),
                        ),
                        value="mapping",
                    ),
                    collapsible=True,
                    variant="soft",
                ),
                class_name="max-w-4xl w-full mt-6"
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
                        rx.icon("circle-check", size=20, color="#15803d"),
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
                        rx.icon("circle-x", size=20, color="#dc2626"),
                        rx.text(State.error_message, class_name="text-red-700"),
                        spacing="2",
                        align="center",
                    ),
                    class_name="bg-red-50 border border-red-200 text-red-700 rounded-xl p-4 mt-4 max-w-4xl w-full"
                ),
            ),
            
            # Downloads dos CSVs e Excel
            rx.cond(
                State.csv_generated,
                rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.text("🎉", class_name="text-2xl"),
                            rx.text(
                                "Arquivos gerados com sucesso!",
                                class_name="text-[#1B5E20] font-bold text-xl"
                            ),
                            spacing="2",
                            align="center",
                        ),
                        rx.text(
                            "Baixe os arquivos ou vá direto para a análise",
                            class_name="text-gray-500 text-sm"
                        ),

                        # Downloads - CSV e Excel lado a lado
                        rx.grid(
                            # COMPULAB
                            rx.vstack(
                                rx.text("COMPULAB", class_name="font-semibold text-[#1B5E20] text-sm mb-2"),
                                rx.hstack(
                                    rx.link(
                                        rx.button(
                                            rx.hstack(
                                                rx.icon("file-text", size=18),
                                                rx.text("CSV", class_name="font-medium"),
                                                spacing="2",
                                            ),
                                            class_name="bg-[#1B5E20] text-white px-5 py-2 rounded-lg hover:bg-[#2E7D32] transition-all text-sm"
                                        ),
                                        download="compulab_data.csv",
                                        href=rx.Var.create(f"data:text/csv;charset=utf-8,{State.compulab_csv}"),
                                    ),
                                    rx.cond(
                                        State.compulab_xlsx != "",
                                        rx.link(
                                            rx.button(
                                                rx.hstack(
                                                    rx.icon("file-spreadsheet", size=18),
                                                    rx.text("XLSX", class_name="font-medium"),
                                                    spacing="2",
                                                ),
                                                class_name="bg-green-600 text-white px-5 py-2 rounded-lg hover:bg-green-700 transition-all text-sm"
                                            ),
                                            download="compulab_data.xlsx",
                                            href=rx.Var.create(f"data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{State.compulab_xlsx}"),
                                        ),
                                    ),
                                    spacing="2",
                                ),
                                spacing="1",
                                align="start",
                            ),
                            # SIMUS
                            rx.vstack(
                                rx.text("SIMUS", class_name="font-semibold text-[#1B5E20] text-sm mb-2"),
                                rx.hstack(
                                    rx.link(
                                        rx.button(
                                            rx.hstack(
                                                rx.icon("file-text", size=18),
                                                rx.text("CSV", class_name="font-medium"),
                                                spacing="2",
                                            ),
                                            class_name="bg-[#1B5E20] text-white px-5 py-2 rounded-lg hover:bg-[#2E7D32] transition-all text-sm"
                                        ),
                                        download="simus_data.csv",
                                        href=rx.Var.create(f"data:text/csv;charset=utf-8,{State.simus_csv}"),
                                    ),
                                    rx.cond(
                                        State.simus_xlsx != "",
                                        rx.link(
                                            rx.button(
                                                rx.hstack(
                                                    rx.icon("file-spreadsheet", size=18),
                                                    rx.text("XLSX", class_name="font-medium"),
                                                    spacing="2",
                                                ),
                                                class_name="bg-green-600 text-white px-5 py-2 rounded-lg hover:bg-green-700 transition-all text-sm"
                                            ),
                                            download="simus_data.xlsx",
                                            href=rx.Var.create(f"data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{State.simus_xlsx}"),
                                        ),
                                    ),
                                    spacing="2",
                                ),
                                spacing="1",
                                align="start",
                            ),
                            columns="2",
                            spacing="6",
                            width="100%",
                        ),

                        # Feature 2: Botão "Analisar Agora"
                        rx.button(
                            rx.hstack(
                                rx.icon("bar-chart-2", size=20),
                                rx.text("Analisar Agora", class_name="font-semibold"),
                                spacing="2",
                            ),
                            on_click=State.send_to_analysis,
                            class_name="bg-[#1B5E20] text-white px-8 py-3 rounded-xl hover:bg-[#2E7D32] hover:shadow-xl transition-all mt-4 font-medium"
                        ),

                        # Botão para limpar e começar novo
                        rx.button(
                            rx.hstack(
                                rx.text("🔄"),
                                rx.text("Nova Conversão"),
                                spacing="2",
                            ),
                            on_click=State.clear_all_files,
                            class_name="bg-transparent border border-gray-300 text-gray-600 px-4 py-2 rounded-lg hover:bg-gray-50 transition-all text-sm mt-2"
                        ),
                        spacing="4",
                        align="center",
                    ),
                    class_name="bg-gradient-to-br from-green-50 to-lime-50 border border-green-200 rounded-2xl p-8 mt-6 max-w-4xl w-full shadow-sm"
                ),
            ),

            # Feature 1: Preview dos Dados com Tabs
            rx.cond(
                State.csv_generated,
                rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.icon("table", size=20, color="#1B5E20"),
                            rx.text(
                                "Prévia dos Dados",
                                class_name="text-[#1B5E20] font-semibold text-lg"
                            ),
                            spacing="2",
                            align="center",
                        ),
                        rx.tabs.root(
                            rx.tabs.list(
                                rx.tabs.trigger("COMPULAB", value="compulab"),
                                rx.tabs.trigger("SIMUS", value="simus"),
                            ),
                            rx.tabs.content(
                                rx.box(
                                    rx.cond(
                                        State.compulab_preview.length() > 0,
                                        rx.data_table(
                                            data=State.compulab_preview,
                                            pagination=True,
                                            search=True,
                                            sort=True,
                                        ),
                                        rx.text("Nenhum dado disponível", class_name="text-gray-500 text-sm text-center py-4")
                                    ),
                                    class_name="mt-4"
                                ),
                                value="compulab",
                            ),
                            rx.tabs.content(
                                rx.box(
                                    rx.cond(
                                        State.simus_preview.length() > 0,
                                        rx.data_table(
                                            data=State.simus_preview,
                                            pagination=True,
                                            search=True,
                                            sort=True,
                                        ),
                                        rx.text("Nenhum dado disponível", class_name="text-gray-500 text-sm text-center py-4")
                                    ),
                                    class_name="mt-4"
                                ),
                                value="simus",
                            ),
                            default_value="compulab",
                        ),
                        spacing="3",
                        width="100%",
                    ),
                    class_name="bg-white border border-gray-200 rounded-2xl p-6 mt-6 max-w-4xl w-full shadow-sm"
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
