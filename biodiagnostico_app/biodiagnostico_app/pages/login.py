import reflex as rx
from ..state import State
from ..styles import Color, Design, Typography, Spacing, GLASS_STYLE
from ..components import ui

def login_page() -> rx.Component:
    """Página de login - Experiência Premium com Glassmorphism"""
    
    # Custom CSS para animações (Mantendo as específicas desta página)
    login_animation = """
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
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
                                    gap="12px"
                                ),
                                rx.text("Sistema de Auditoria", font_size=["2.5rem", "3rem", "3.5rem"], font_weight="800", color="white", line_height="1.1", margin_top=Spacing.MD),
                                rx.text("& Inteligência Laboratorial", font_size=["1.5rem", "1.75rem", "2rem"], font_weight="300", color="white", opacity="0.9", line_height="1.2"),
                                align_items="start",
                                gap="0"
                            ),
                            # Aplicando GLASS_STYLE mas adaptado para fundo escuro (texto branco)
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
                        gap="10px",
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
                        ui.heading("Bem-vindo de volta", level=2, color=Color.DEEP, text_align="center"),
                        ui.text("Entre com suas credenciais para acessar", size="small", text_align="center"),
                        align_items="center",
                        gap=Spacing.XS,
                        margin_bottom=Spacing.XL,
                        animation="fadeInUp 0.7s ease-out"
                    ),
                    
                    # Formulário dentro do Card Glass/Surface
                    ui.card(
                        rx.vstack(
                            ui.form_field(
                                "E-mail",
                                ui.input(
                                    placeholder="exemplo@biodiagnostico.com",
                                    value=State.login_email,
                                    on_change=State.set_login_email,
                                    type="email",
                                )
                            ),
                            
                            ui.form_field(
                                "Senha",
                                ui.input(
                                    placeholder="••••••••",
                                    value=State.login_password,
                                    on_change=State.set_login_password,
                                    type="password",
                                )
                            ),
                            
                            # Error message
                            rx.cond(
                                State.login_error != "",
                                ui.status_badge(State.login_error, status="error")
                            ),
                            
                            # Login Button Premium
                            ui.button(
                                "Acessar Sistema",
                                icon="arrow-right",
                                on_click=State.attempt_login,
                                width="100%",
                                margin_top=Spacing.MD,
                                # Custom gradient override via props if needed, but primary is standard
                                bg=Color.GRADIENT_PRIMARY, 
                                _hover={"filter": "brightness(1.1)", "transform": "translateY(-2px)", "box_shadow": Design.SHADOW_LG}
                            ),
                            
                            gap=Spacing.LG,
                            width="100%",
                        ),
                        width="100%",
                        max_width="400px",
                        animation="fadeInUp 0.8s ease-out"
                    ),
                    
                    # Footer
                    rx.text(
                        "© 2024 Biodiagnóstico App • Todos os direitos reservados",
                        font_size="0.75rem", color=Color.TEXT_SECONDARY, margin_top=Spacing.XL, text_align="center"
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
