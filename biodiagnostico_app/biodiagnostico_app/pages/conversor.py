import reflex as rx
from ..state import State
from ..components.file_upload import file_upload_enhanced
from ..components import ui
from ..styles import Color, Design, Typography, Spacing

def feature_card(icon: str, title: str, description: str, delay: str = "0s") -> rx.Component:
    """Card de funcionalidade premium com animação"""
    return rx.box(
        ui.card(
            rx.hstack(
                rx.box(
                    rx.icon(icon, size=24, color=Color.PRIMARY),
                    bg=Color.PRIMARY_LIGHT, p="3", border_radius=Design.RADIUS_LG,
                    transition="transform 0.3s ease",
                    _group_hover={"transform": "scale(1.1) rotate(5deg)"}
                ),
                rx.vstack(
                    ui.text(title, size="label", color=Color.DEEP),
                    ui.text(description, size="small", color=Color.TEXT_SECONDARY),
                    spacing="1", align_items="start",
                ),
                spacing="3", align_items="center",
            ),
            _hover={"transform": "translateY(-4px)", "box_shadow": Design.SHADOW_MD},
            transition="all 0.3s ease",
            class_name="group"
        ),
        animation=f"fadeInUp 0.6s ease-out {delay} both"
    )

def step_indicator(number: str, title: str, is_active: bool = False, is_completed: bool = False) -> rx.Component:
    """Indicador de etapa do processo"""
    
    return rx.vstack(
        rx.box(
            rx.cond(
                is_completed,
                rx.icon(tag="check", size=16, color="white"),
                rx.text(number, font_weight="700", color=rx.cond(is_active | is_completed, "white", Color.TEXT_SECONDARY), font_size="0.9rem")
            ),
            width="32px", height="32px", border_radius="full",
            bg=rx.cond(is_completed, Color.SUCCESS, rx.cond(is_active, Color.PRIMARY, "transparent")),
            border=rx.cond(
                is_completed, 
                f"2px solid {Color.SUCCESS}", 
                rx.cond(
                    is_active, 
                    f"2px solid {Color.PRIMARY}", 
                    f"2px solid {Color.TEXT_LIGHT}"
                )
            ),
            display="flex", align_items="center", justify_content="center",
            transition="all 0.3s ease"
        ),
        rx.text(title, font_size="0.75rem", font_weight="600", color=rx.cond(is_active, Color.DEEP, Color.TEXT_SECONDARY)),
        align_items="center",
        spacing="2"
    )

def conversor_page() -> rx.Component:
    """Página do conversor PDF para Excel - Design Premium"""
    
    # SVG do Erlenmeyer (COMPULAB)
    erlenmeyer_svg = f"""
        <svg viewBox="0 0 80 100" width="60" height="75">
            <defs>
                <linearGradient id="liquidGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" style="stop-color:{Color.SUPPORTIVE_MEDIUM};stop-opacity:0.4" />
                    <stop offset="100%" style="stop-color:{Color.PRIMARY};stop-opacity:0.6" />
                </linearGradient>
            </defs>
            <path d="M28 10 L52 10 L52 35 L70 85 Q72 92 65 95 L15 95 Q8 92 10 85 L28 35 Z" 
                  fill="url(#liquidGrad)" stroke="{Color.DEEP}" stroke-width="2"/>
            <rect x="26" y="5" width="28" height="8" rx="3" fill="none" stroke="{Color.DEEP}" stroke-width="2"/>
            <ellipse cx="40" cy="75" rx="20" ry="8" fill="{Color.PRIMARY}" opacity="0.2">
                <animate attributeName="opacity" values="0.2;0.5;0.2" dur="3s" repeatCount="indefinite" />
            </ellipse>
        </svg>
    """
    
    # SVG dos Tubos (SIMUS)
    tubes_svg = f"""
        <svg viewBox="0 0 100 100" width="60" height="75">
            <defs>
                <linearGradient id="tubeGrad1" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" style="stop-color:{Color.SUPPORTIVE_MEDIUM};stop-opacity:0.3" />
                    <stop offset="100%" style="stop-color:{Color.PRIMARY};stop-opacity:0.6" />
                </linearGradient>
            </defs>
            <rect x="18" y="15" width="15" height="68" rx="7" fill="none" stroke="{Color.DEEP}" stroke-width="2"/>
            <rect x="18" y="52" width="15" height="31" rx="7" fill="url(#tubeGrad1)">
                <animate attributeName="height" values="31;45;31" dur="4s" repeatCount="indefinite" />
                <animate attributeName="y" values="52;38;52" dur="4s" repeatCount="indefinite" />
            </rect>
            <rect x="42" y="15" width="15" height="68" rx="7" fill="none" stroke="{Color.DEEP}" stroke-width="2"/>
            <rect x="42" y="42" width="15" height="41" rx="7" fill="url(#tubeGrad1)">
                <animate attributeName="height" values="41;25;41" dur="5s" repeatCount="indefinite" />
                <animate attributeName="y" values="42;58;42" dur="5s" repeatCount="indefinite" />
            </rect>
            <rect x="66" y="15" width="15" height="68" rx="7" fill="none" stroke="{Color.DEEP}" stroke-width="2"/>
            <rect x="66" y="58" width="15" height="25" rx="7" fill="url(#tubeGrad1)"/>
        </svg>
    """
    
    return rx.box(
        rx.vstack(
            # Header com Stepper
            rx.box(
                rx.vstack(
                    ui.animated_heading("Conversor Inteligente", level=1),
                    rx.text("Transforme relatórios laboratoriais em dados estruturados", 
                           color=Color.TEXT_SECONDARY, 
                           text_align="center",
                           font_size=["0.875rem", "1rem"]),
                    
                    # Stepper
                    rx.hstack(
                        step_indicator("1", "Upload", is_active=True, is_completed=State.has_files),
                        rx.box(width=["20px", "40px"], height="2px", bg=Color.BORDER),
                        step_indicator("2", "Conversão", is_active=State.is_generating_csv, is_completed=State.csv_generated),
                        rx.box(width=["20px", "40px"], height="2px", bg=Color.BORDER),
                        step_indicator("3", "Excel", is_active=State.csv_generated, is_completed=False),
                        spacing="0", margin_top=Spacing.LG, align_items="center",
                        gap=["2", "4"] # Gap responsivo
                    ),
                    align_items="center",
                    spacing="2",
                    width="100%"
                ),
                padding_y=[Spacing.MD, Spacing.LG, Spacing.XL],
                padding_x=[Spacing.MD, Spacing.LG],
                width="100%", display="flex", justify_content="center"
            ),
            
            # Cards de funcionalidades
            rx.grid(
                feature_card("file-text", "Extração Automática", "Reconhecimento de PDF Compulab/Simus", "0.1s"),
                feature_card("refresh-cw", "Padronização", "Normaliza nomes de exames e valores", "0.2s"),
                feature_card("table", "Excel Estruturado", "Gera planilhas prontas para análise", "0.3s"),
                feature_card("zap", "Alta Performance", "Processamento local seguro e rápido", "0.4s"),
                columns={"initial": "1", "sm": "2", "lg": "4"},
                spacing="4", width="100%", max_width="6xl", margin_x="auto"
            ),
            
            # Área Principal de Upload
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.icon(tag="cloud-upload", size=24, color=Color.PRIMARY),
                        ui.heading("Área de Upload", level=3),
                        spacing="3", align_items="center",
                        margin_bottom=Spacing.MD
                    ),
                    
                    # Grid de uploads com estilo visual superior
                    rx.grid(
                        file_upload_enhanced(
                            title="COMPULAB",
                            subtitle="Relatório de faturamento (PDF)",
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
                            subtitle="Relatório de faturamento (PDF)",
                            icon_svg=tubes_svg,
                            upload_id="simus_conv",
                            file_name=State.simus_file_name,
                            file_size=State.simus_file_size,
                            on_upload=State.handle_simus_upload,
                            on_remove=State.clear_simus_file,
                            accepted_types="PDF",
                            accept_dict={"application/pdf": [".pdf"]},
                        ),
                        columns={"initial": "1", "md": "2"},
                        spacing="6", width="100%",
                    ),
                    
                    # Barra de progresso do processamento
                    rx.cond(
                        State.is_generating_csv,
                        rx.box(
                            rx.vstack(
                                rx.hstack(
                                    rx.spinner(size="2", color=Color.PRIMARY),
                                    rx.text(State.csv_stage, font_weight="600", color=Color.DEEP),
                                    rx.spacer(),
                                    rx.text(f"{State.csv_progress_percentage.to_string()}%", font_weight="700", color=Color.PRIMARY),
                                    width="100%", align_items="center"
                                ),
                                rx.box(
                                    rx.box(
                                        bg=Color.GRADIENT_PRIMARY, border_radius="full", transition="width 0.3s ease",
                                        width=rx.cond(State.csv_progress_percentage > 0, State.csv_progress_percentage.to_string() + "%", "0%"),
                                        height="100%",
                                        position="relative", overflow="hidden",
                                        _after={
                                            "content": '""', "position": "absolute", "top": "0", "left": "0", "right": "0", "bottom": "0",
                                            "background": "linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent)",
                                            "animation": "shimmer 1.5s infinite"
                                        }
                                    ),
                                    width="100%", height="8px", bg=Color.BACKGROUND, border_radius="full", overflow="hidden"
                                ),
                                spacing="2", width="100%", align_items="center"
                            ),
                            bg=Color.PRIMARY_LIGHT, border=f"1px solid {Color.PRIMARY}30", border_radius=Design.RADIUS_LG, padding=Spacing.MD, margin_top=Spacing.LG,
                            animation="fadeInUp 0.3s ease-out",
                            width="100%", max_width="600px", margin_x="auto"
                        )
                    ),

                    # Botão de Ação Principal
                    rx.cond(
                        ~State.csv_generated & ~State.is_generating_csv,
                        ui.button(
                            "Iniciar Conversão Inteligente",
                            icon="wand-sparkles",
                            on_click=State.generate_csvs,
                            disabled=~State.has_files,
                            width="100%", margin_top=Spacing.LG, height="50px", variant="primary",
                            box_shadow=Design.SHADOW_MD
                        )
                    ),
                    
                    padding=[Spacing.MD, Spacing.LG, Spacing.XL],
                    width="100%"
                ),
                bg=Color.SURFACE,
                border_radius="24px",
                width="100%", max_width="5xl", margin_top=Spacing.LG, margin_x="auto",
                box_shadow=Design.SHADOW_DEFAULT,
                animation="fadeInUp 0.6s ease-out 0.2s both"
            ),
            
            # Área de Download (Sucesso)
            rx.cond(
                State.csv_generated,
                rx.box(
                    rx.vstack(
                        rx.icon(tag="circle-check", size=48, color=Color.SUCCESS),
                        ui.heading("Conversão Concluída!", level=2, color=Color.DEEP),
                        ui.text("Seus arquivos foram padronizados e estão prontos para download.", color=Color.TEXT_SECONDARY),
                        
                        rx.grid(
                            rx.link(
                                ui.button("Baixar COMPULAB (.xlsx)", icon="download", variant="primary", width="100%", height="48px"),
                                download="compulab_data.xlsx",
                                href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64," + State.compulab_csv,
                            ),
                            rx.link(
                                ui.button("Baixar SIMUS (.xlsx)", icon="download", variant="primary", width="100%", height="48px"),
                                download="simus_data.xlsx",
                                href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64," + State.simus_csv,
                            ),
                            columns={"initial": "1", "sm": "2"},
                            spacing="4", width="100%", margin_top=Spacing.MD
                        ),
                        
                        ui.button("Realizar Nova Conversão", icon="rotate-ccw", on_click=State.clear_all_files, variant="ghost", margin_top=Spacing.MD),
                        align_items="center", spacing="3"
                    ),
                    bg=Color.SUCCESS_BG,
                    border=f"1px solid {Color.SUCCESS}40",
                    border_radius="24px",
                    padding=Spacing.XL,
                    width="100%", max_width="5xl", margin_x="auto", margin_top=Spacing.LG,
                    animation="fadeInUp 0.5s ease-out"
                )
            ),
            
            # Informational Tip
            rx.cond(
                ~State.csv_generated,
                rx.box(
                    rx.hstack(
                        rx.icon(tag="info", size=20, color=Color.PRIMARY),
                        rx.text("Dica Pro: Os arquivos são processados localmente e nunca deixam seu computador.", font_size="0.85rem", color=Color.TEXT_SECONDARY),
                        align_items="center", spacing="3"
                    ),
                    bg=Color.BACKGROUND, border_radius="full", padding="8px 20px", margin_top=Spacing.XL,
                    border=f"1px solid {Color.BORDER}"
                )
            ),
            
            spacing="0", align_items="center", width="100%", padding_y=Spacing.XL, padding_x=Spacing.MD
        ),
        width="100%"
    )
