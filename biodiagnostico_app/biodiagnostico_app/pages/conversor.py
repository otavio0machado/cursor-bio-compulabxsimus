"""
Conversor PDF → CSV page
Design moderno com upload aprimorado
"""
import reflex as rx
from ..state import State
from ..components.file_upload import file_upload_enhanced, upload_progress_indicator, file_type_badge
from ..components import ui
from ..styles import Color, Design, Typography, Spacing


def feature_card(icon: str, title: str, description: str) -> rx.Component:
    """Card de funcionalidade (Purificado)"""
    return ui.card(
        rx.hstack(
            rx.box(
                rx.icon(icon, size=24, color=Color.PRIMARY),
                bg=Color.PRIMARY_LIGHT, p="3", border_radius=Design.RADIUS_LG
            ),
            rx.vstack(
                ui.text(title, size="label", color=Color.DEEP),
                ui.text(description, size="small", color=Color.TEXT_SECONDARY),
                spacing="0", align_items="start",
            ),
            spacing="3", align_items="center",
        ),
    )


def conversor_page() -> rx.Component:
    """Página do conversor PDF para Excel - Design oficial aprimorado (Purificada)"""
    
    # SVG do Erlenmeyer (COMPULAB) - Design refinado
    erlenmeyer_svg = f"""
        <svg viewBox="0 0 80 100" width="70" height="88">
            <defs>
                <linearGradient id="liquidGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" style="stop-color:{Color.SUPPORTIVE_MEDIUM};stop-opacity:0.3" />
                    <stop offset="100%" style="stop-color:{Color.PRIMARY};stop-opacity:0.5" />
                </linearGradient>
            </defs>
            <path d="M28 10 L52 10 L52 35 L70 85 Q72 92 65 95 L15 95 Q8 92 10 85 L28 35 Z" 
                  fill="url(#liquidGrad)" stroke="{Color.DEEP}" stroke-width="2.5"/>
            <rect x="26" y="5" width="28" height="8" rx="3" fill="none" stroke="{Color.DEEP}" stroke-width="2.5"/>
            <ellipse cx="40" cy="75" rx="20" ry="8" fill="{Color.PRIMARY}" opacity="0.2"/>
        </svg>
    """
    
    # SVG dos Tubos de ensaio (SIMUS) - Design refinado
    tubes_svg = f"""
        <svg viewBox="0 0 100 100" width="70" height="88">
            <defs>
                <linearGradient id="tubeGrad1" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" style="stop-color:{Color.SUPPORTIVE_MEDIUM};stop-opacity:0.2" />
                    <stop offset="100%" style="stop-color:{Color.PRIMARY};stop-opacity:0.5" />
                </linearGradient>
            </defs>
            <rect x="18" y="15" width="15" height="68" rx="7" fill="none" stroke="{Color.DEEP}" stroke-width="2.5"/>
            <rect x="18" y="52" width="15" height="31" rx="7" fill="url(#tubeGrad1)"/>
            <rect x="42" y="15" width="15" height="68" rx="7" fill="none" stroke="{Color.DEEP}" stroke-width="2.5"/>
            <rect x="42" y="42" width="15" height="41" rx="7" fill="url(#tubeGrad1)"/>
            <rect x="66" y="15" width="15" height="68" rx="7" fill="none" stroke="{Color.DEEP}" stroke-width="2.5"/>
            <rect x="66" y="58" width="15" height="25" rx="7" fill="url(#tubeGrad1)"/>
        </svg>
    """
    
    return rx.box(
        rx.vstack(
            # Animated Header
            rx.box(
                ui.animated_heading("Conversor PDF → Excel", level=1),
                padding_y=Spacing.XL, width="100%", display="flex", justify_content="center"
            ),

            
            # Cards de funcionalidades
            rx.grid(
                feature_card("file_text", "Extração Inteligente", "Extrai dados automaticamente dos PDFs"),
                feature_card("refresh_cw", "Padronização", "Normaliza nomes de exames e pacientes"),
                feature_card("chart_bar", "Excel Estruturado", "Gera arquivos prontos para análise"),

                feature_card("zap", "Processamento Rápido", "Conversão em segundos"),
                columns={"initial": "1", "sm": "2", "lg": "4"},
                spacing="4", width="100%", max_width="6xl", margin_x="auto"
            ),

            
            # Container principal de upload
            ui.card(
                rx.vstack(
                    rx.hstack(
                        rx.icon(tag="upload", size=24, color=Color.PRIMARY),
                        ui.heading("Upload de Arquivos", level=3),
                        spacing="3", align_items="center",
                    ),
                    ui.text(
                        "Arraste seus arquivos ou clique para selecionar",
                        size="body_secondary",
                        margin_bottom=Spacing.MD
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
                        columns={"initial": "1", "sm": "2"},
                        spacing="6", width="100%",
                    ),
                    
                    # Progresso de upload
                    upload_progress_indicator(State.is_uploading, "Carregando arquivo..."),
                    
                    spacing="2", width="100%",
                ),
                width="100%", max_width="5xl", margin_top=Spacing.LG, margin_x="auto"
            ),
            
            # Botão de conversão
            ui.button(
                "Converter para Excel",
                icon="refresh_cw",
                on_click=State.generate_csvs,
                is_loading=State.is_generating_csv,

                loading_text="Convertendo arquivos...",
                disabled=~State.has_files,
                margin_top=Spacing.LG,
                width="100%", max_width="24rem",
            ),
            
            # Indicador de progresso
            rx.cond(
                State.is_generating_csv,
                rx.box(
                    rx.vstack(
                        ui.text(State.csv_progress_percentage.to_string() + "%", size="body_large", color=Color.DEEP, font_weight="800"),
                        ui.text(State.csv_stage, size="small", color=Color.TEXT_SECONDARY),
                        # Barra de progresso
                        rx.box(
                            rx.box(
                                bg=Color.PRIMARY, border_radius="full", transition="all 0.3s ease",
                                width=rx.cond(State.csv_progress_percentage > 0, State.csv_progress_percentage.to_string() + "%", "0%"),
                                height="100%"
                            ),
                            width="100%", height="12px", bg=Color.BACKGROUND, border_radius="full", overflow="hidden", margin_top=Spacing.MD
                        ),
                        spacing="2", align_items="center",
                    ),
                    bg=Color.SURFACE, border=f"1px solid {Color.BORDER}", border_radius=Design.RADIUS_XL, padding=Spacing.LG, mt="4", max_width="4xl", width="100%", box_shadow=Design.SHADOW_SM
                ),
            ),
            
            # Mensagens de status
            rx.cond(
                State.success_message != "",
                rx.callout(State.success_message, icon="circle_check", color_scheme="green", width="100%", max_width="4xl", margin_top=Spacing.MD)
            ),
            rx.cond(
                State.error_message != "",
                rx.callout(State.error_message, icon="triangle_alert", color_scheme="red", width="100%", max_width="4xl", margin_top=Spacing.MD)
            ),
            

            # Downloads dos CSVs
            rx.cond(
                State.csv_generated,
                ui.card(
                    rx.vstack(
                        rx.hstack(
                            rx.text("🎉", font_size="1.5rem"),
                            ui.heading("Planilhas Excel geradas com sucesso!", level=3, color=Color.DEEP),
                            spacing="3", align_items="center",
                        ),

                        ui.text(
                            "Clique nos botões abaixo para baixar os arquivos",
                            size="body_secondary",
                            margin_bottom=Spacing.MD
                        ),
                        rx.grid(
                            rx.link(
                                ui.button("COMPULAB.xlsx", icon="download", variant="primary", width="100%"),
                                download="compulab_data.xlsx",
                                href=rx.Var.create(f"data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{State.compulab_csv}"),
                            ),

                            rx.link(
                                ui.button("SIMUS.xlsx", icon="download", variant="primary", width="100%"),
                                download="simus_data.xlsx",
                                href=rx.Var.create(f"data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{State.simus_csv}"),
                            ),

                            columns={"initial": "1", "sm": "2"},
                            spacing="4", width="100%",
                        ),
                        # Botão para limpar e começar novo
                        ui.button("Nova Conversão", icon="refresh_cw", on_click=State.clear_all_files, variant="ghost", margin_top=Spacing.MD),
                        spacing="4", align_items="center",
                    ),
                    bg=f"linear-gradient(135deg, {Color.SUCCESS_BG} 0%, {Color.SURFACE} 100%)",
                    border=f"1px solid {Color.SUCCESS}40",
                    width="100%", max_width="5xl", margin_top=Spacing.LG, margin_x="auto"
                ),
            ),
            
            # Dica
            rx.cond(
                ~State.csv_generated,
                ui.card(
                    rx.hstack(
                        rx.icon(tag="lightbulb", size=24, color=Color.WARNING),
                        rx.vstack(
                            ui.text("Os arquivos gerados terão os nomes de exames padronizados.", size="label", color=Color.DEEP),
                            ui.text("Isso facilita a comparação entre COMPULAB e SIMUS na Análise Cruzada.", size="caption"),
                            spacing="0", align_items="start",
                        ),
                        spacing="3", align_items="start",
                    ),
                    bg=Color.WARNING_BG, border=f"1px solid {Color.WARNING}30", width="100%", max_width="5xl", margin_top=Spacing.LG
                ),
            ),
            
            spacing="0", align_items="center", width="100%", padding_y=Spacing.XL, padding_x=Spacing.MD
        ),
        width="100%",
    )
