import reflex as rx
from ..state import State
from ..styles import Color, Spacing, Design
from ..components import ui

def login_page() -> rx.Component:
    """Página de login - Experiência Premium Simplificada (K.I.S.S)"""
    
    return rx.flex(
        # === LADO ESQUERDO - Hero Visual (Glassmorphism Subtle) ===
        rx.box(
            rx.vstack(
                rx.box(
                    rx.icon(tag="flask-conical", size=48, color="white"),
                    bg="rgba(255, 255, 255, 0.2)",
                    p="4", border_radius="20px",
                    backdrop_filter="blur(10px)",
                    margin_bottom=Spacing.LG
                ),
                rx.heading("BIODIAGNÓSTICO", size="3", color="white", letter_spacing="0.1em"),
                rx.heading("Sistema de Controle de Qualidade Laboratorial", size="8", color="white", font_weight="800", line_height="1.2"),
                rx.text("Precisão e confiabilidade em cada resultado.", size="4", color="white", opacity="0.9"),
                
                align_items="start",
                justify_content="center",
                height="100%",
                padding="80px",
                max_width="800px"
            ),
            width=["0%", "0%", "50%"],
            background="linear-gradient(135deg, rgba(15, 118, 110, 0.92) 0%, rgba(8, 53, 48, 0.96) 100%), url('/login_bg.png')",
            background_size="cover",
            background_position="center",
            display=["none", "none", "flex"],
            align_items="center",
            justify_content="center",
            position="relative"
        ),

        # === LADO DIREITO - Formulário Clean ===
        rx.center(
            rx.vstack(
                # Header
                rx.box(
                    rx.image(src="/logo_lab.jpg", height="60px", border_radius="12px"),
                    margin_bottom=Spacing.XL
                ),
                
                ui.heading("Bem-vindo", level=2, text_align="center"),
                ui.text("Digite suas credenciais para acessar o painel.", size="body_secondary", text_align="center", margin_bottom=Spacing.LG),
                
                # Card Wrapper
                ui.card(
                    rx.vstack(
                        ui.form_field(
                            "E-mail Corporativo",
                            ui.input(
                                placeholder="seu@biodiagnostico.com",
                                value=State.login_email,
                                on_change=State.set_login_email,
                                type="email",
                                size="large"
                            )
                        ),
                        ui.form_field(
                            "Senha",
                            ui.input(
                                placeholder="••••••••",
                                value=State.login_password,
                                on_change=State.set_login_password,
                                type="password",
                                size="large"
                            )
                        ),
                        
                        rx.cond(
                            State.login_error != "",
                            ui.status_badge(State.login_error, status="error")
                        ),
                        
                        ui.button(
                            "Acessar Plataforma", 
                            icon="arrow-right", 
                            on_click=State.attempt_login, 
                            width="100%",
                            size="large",
                            margin_top=Spacing.MD
                        ),
                        
                        gap=Spacing.LG,
                        width="100%"
                    ),
                    width="100%",
                    max_width="420px",
                    padding=Spacing.XL,
                    box_shadow=Design.SHADOW_LG
                ),
                
                # Footer
                rx.hstack(
                    rx.icon(tag="shield-check", size=14, color=Color.TEXT_SECONDARY),
                    ui.text("Ambiente Seguro e Monitorado", size="caption"),
                    align_items="center",
                    gap="6px",
                    margin_top=Spacing.XXL
                ),
                
                align_items="center",
                width="100%",
                padding=Spacing.LG
            ),
            width=["100%", "100%", "50%"],
            height="100vh",
            bg=Color.BACKGROUND
        ),
        
        width="100%",
        min_height="100vh",
        display="flex",
        flex_direction=["column", "column", "row"],
        class_name="login-shell"
    )
