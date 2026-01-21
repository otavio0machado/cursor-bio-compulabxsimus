import reflex as rx
from ..state import State
from ..styles import Color, INPUT_STYLE, BUTTON_PRIMARY_STYLE, Design, Typography, Spacing

def login_page() -> rx.Component:
    """Página de login - Experiência Premium com Glassmorphism"""
    
    # Custom CSS para animações
    login_animation = """
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @keyframes shimmer {
            0% { background-position: -200% 0; }
            100% { background-position: 200% 0; }
        }
        @keyframes pulse-ring {
            0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(76, 175, 80, 0.4); }
            70% { transform: scale(1); box-shadow: 0 0 0 15px rgba(76, 175, 80, 0); }
            100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(76, 175, 80, 0); }
        }
    """
    
    return rx.fragment(
        rx.script(f"const style = document.createElement('style'); style.textContent = `{login_animation}`; document.head.appendChild(style);"),
        rx.flex(
            # === LADO ESQUERDO - Hero Visual ===
            rx.box(
                # Overlay gradiente premium
                rx.box(
                    position="absolute",
                    top="0", left="0", right="0", bottom="0",
                    background="linear-gradient(135deg, rgba(27, 94, 32, 0.85) 0%, rgba(46, 125, 50, 0.7) 50%, rgba(76, 175, 80, 0.5) 100%)",
                    z_index="1"
                ),
                # Content overlay
                rx.vstack(
                    rx.box(flex="1"),
                    rx.vstack(
                        # Glassmorphism card para título
                        rx.box(
                            rx.vstack(
                                rx.hstack(
                                    rx.box(
                                        rx.icon(tag="flask-conical", size=32, color="white"),
                                        bg="rgba(255, 255, 255, 0.2)",
                                        p="3", border_radius="16px",
                                        backdrop_filter="blur(10px)"
                                    ),
                                    rx.text("BIODIAGNÓSTICO", font_size="0.875rem", font_weight="700", color="white", letter_spacing="0.2em"),
                                    align_items="center",
                                    style={"gap": "12px"}
                                ),
                                rx.text("Sistema de Auditoria", font_size=["2.5rem", "3rem", "3.5rem"], font_weight="800", color="white", line_height="1.1", margin_top=Spacing.MD),
                                rx.text("& Inteligência Laboratorial", font_size=["1.5rem", "1.75rem", "2rem"], font_weight="300", color="white", opacity="0.9", line_height="1.2"),
                                align_items="start",
                                style={"gap": "0"}
                            ),
                            bg="rgba(255, 255, 255, 0.1)",
                            backdrop_filter="blur(16px)",
                            border="1px solid rgba(255, 255, 255, 0.2)",
                            border_radius="24px",
                            padding=Spacing.XL,
                            margin_x=Spacing.XL,
                            animation="fadeInUp 0.8s ease-out"
                        ),
                        align_items="start",
                        width="100%",
                    ),
                    rx.box(flex="1"),
                    # Footer seguro
                    rx.hstack(
                        rx.icon(tag="shield-check", size=18, color="white"),
                        rx.text("Conexão 100% Segura • Dados Criptografados", font_size="0.8rem", color="white", font_weight="500"),
                        style={"gap": "10px"},
                        padding=Spacing.XL,
                        opacity="0.8"
                    ),
                    align_items="start",
                    justify_content="space-between",
                    height="100%",
                    z_index="2", position="relative"
                ),
                width=["0%", "0%", "55%"],
                background_image="url('/login_bg.png')",
                background_size="cover",
                background_position="center",
                display=["none", "none", "flex"],
                position="relative",
                overflow="hidden"
            ),

            # === LADO DIREITO - Formulário Premium ===
            rx.center(
                rx.vstack(
                    # Logo animada
                    rx.box(
                        rx.image(src="/logo_lab.jpg", height="90px", border_radius="20px", box_shadow=Design.SHADOW_MD),
                        animation="fadeInUp 0.6s ease-out",
                        margin_bottom=Spacing.LG
                    ),
                    
                    # Título com shimmer effect
                    rx.vstack(
                        rx.text("Bem-vindo de volta", style=Typography.H2, color=Color.DEEP, text_align="center"),
                        rx.text("Entre com suas credenciais para acessar", style=Typography.SMALL, color=Color.TEXT_SECONDARY, text_align="center"),
                        align_items="center",
                        style={"gap": Spacing.XS},
                        margin_bottom=Spacing.XL,
                        animation="fadeInUp 0.7s ease-out"
                    ),
                    
                    # Formulário
                    rx.box(
                        rx.vstack(
                            # Email field
                            rx.box(
                                rx.hstack(
                                    rx.icon(tag="mail", size=16, color=Color.TEXT_SECONDARY),
                                    rx.text("E-mail", style=Typography.LABEL, color=Color.TEXT_PRIMARY),
                                    align_items="center",
                                    style={"gap": "6px"},
                                    margin_bottom="8px"
                                ),
                                rx.input(
                                    placeholder="exemplo@biodiagnostico.com",
                                    value=State.login_email,
                                    on_change=State.set_login_email,
                                    type="email",
                                    **INPUT_STYLE
                                ),
                                width="100%",
                            ),
                            
                            # Password field
                            rx.box(
                                rx.hstack(
                                    rx.icon(tag="lock", size=16, color=Color.TEXT_SECONDARY),
                                    rx.text("Senha", style=Typography.LABEL, color=Color.TEXT_PRIMARY),
                                    align_items="center",
                                    style={"gap": "6px"},
                                    margin_bottom="8px"
                                ),
                                rx.input(
                                    placeholder="••••••••",
                                    value=State.login_password,
                                    on_change=State.set_login_password,
                                    type="password",
                                    **INPUT_STYLE
                                ),
                                width="100%",
                            ),
                            
                            # Error message
                            rx.cond(
                                State.login_error != "",
                                rx.box(
                                    rx.hstack(
                                        rx.icon(tag="circle-x", size=18, color=Color.ERROR),
                                        rx.text(State.login_error, color=Color.ERROR, font_weight="500", font_size="0.875rem"),
                                        align_items="center",
                                        style={"gap": "8px"}
                                    ),
                                    bg=Color.ERROR_BG,
                                    border=f"1px solid {Color.ERROR}40",
                                    padding=Spacing.MD,
                                    border_radius=Design.RADIUS_LG,
                                    width="100%"
                                ),
                            ),
                            
                            # Login Button Premium
                            rx.button(
                                rx.hstack(
                                    rx.text("Acessar Sistema", font_weight="600"),
                                    rx.icon(tag="arrow-right", size=18),
                                    align_items="center",
                                    style={"gap": "8px"}
                                ),
                                on_click=State.attempt_login,
                                width="100%",
                                height="52px",
                                bg=Color.GRADIENT_PRIMARY,
                                color="white",
                                border="none",
                                border_radius=Design.RADIUS_LG,
                                font_size="1rem",
                                cursor="pointer",
                                transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
                                _hover={"transform": "translateY(-2px)", "box_shadow": Design.SHADOW_LG},
                                _active={"transform": "translateY(0)"},
                                margin_top=Spacing.MD
                            ),
                            
                            style={"gap": Spacing.LG},
                            width="100%",
                        ),
                        width="100%",
                        max_width="400px",
                        bg=Color.SURFACE,
                        padding=Spacing.XL,
                        border_radius="20px",
                        border=f"1px solid {Color.BORDER}",
                        box_shadow=Design.SHADOW_MD,
                        animation="fadeInUp 0.8s ease-out"
                    ),
                    
                    # Footer
                    rx.text(
                        "© 2024 Biodiagnóstico App • Todos os direitos reservados",
                        font_size="0.75rem", color=Color.TEXT_LIGHT, margin_top=Spacing.XL, text_align="center"
                    ),
                    
                    align_items="center",
                    width="100%",
                    padding=Spacing.XL,
                ),
                width=["100%", "100%", "45%"],
                bg=Color.BACKGROUND,
                height="100vh",
            ),
            width="100%",
            min_height="100vh",
        )
    )
