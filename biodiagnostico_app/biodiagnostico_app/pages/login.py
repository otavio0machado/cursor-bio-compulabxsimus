import reflex as rx
from ..state import State
from ..styles import Color, Spacing, Design
from ..components import ui

def login_page() -> rx.Component:
    """Página de login - Experiência Premium Simplificada (K.I.S.S)"""
    
    return rx.flex(
        # === LADO ESQUERDO - Hero Visual ===
        rx.box(
            rx.vstack(
                rx.box(
                    rx.icon(tag="flask-conical", size=40, color=Color.WHITE),
                    bg="rgba(255, 255, 255, 0.15)",
                    p="3", border_radius=Design.RADIUS_LG,
                    backdrop_filter="blur(8px)",
                    margin_bottom=Spacing.LG
                ),
                rx.heading("BIODIAGNÓSTICO", size="3", color=Color.WHITE, letter_spacing="0.1em", opacity="0.9"),
                rx.heading("Sistema de Controle de Qualidade Laboratorial", size="7", color=Color.WHITE, font_weight="700", line_height="1.2"),
                rx.text("Precisão e confiabilidade em cada resultado.", size="3", color=Color.WHITE, opacity="0.8"),

                align_items="start",
                justify_content="center",
                height="100%",
                padding=["40px", "60px", "80px"],
                max_width="700px"
            ),
            width=["0%", "0%", "50%"],
            background=f"{Color.GRADIENT_LOGIN_HERO}, url('/login_bg.png')",
            background_size="cover",
            background_position="center",
            display=["none", "none", "flex"],
            align_items="center",
            justify_content="center",
            position="relative"
        ),

        # === LADO DIREITO - Formulário ===
        rx.center(
            rx.vstack(
                rx.box(
                    rx.image(src="/logo_lab.jpg", height="52px", border_radius=Design.RADIUS_SM),
                    margin_bottom=Spacing.LG
                ),

                ui.heading("Bem-vindo", level=2, text_align="center"),
                ui.text("Digite suas credenciais para acessar o painel.", size="body_secondary", text_align="center", margin_bottom=Spacing.LG),

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
                            margin_top=Spacing.SM
                        ),

                        rx.button(
                            "Esqueci minha senha",
                            on_click=State.toggle_forgot_password,
                            variant="ghost", size="1",
                            color=Color.TEXT_SECONDARY,
                            _hover={"color": Color.PRIMARY},
                            width="100%",
                        ),

                        gap=Spacing.MD,
                        width="100%"
                    ),
                    width="100%",
                    max_width="400px",
                    padding=Spacing.XL,
                ),

                # Password Recovery Section
                rx.cond(
                    State.show_forgot_password,
                    ui.card(
                        rx.vstack(
                            ui.heading("Recuperar Senha", level=4),
                            ui.text("Informe seu e-mail para receber o link de recuperação.", size="small", color=Color.TEXT_SECONDARY),
                            ui.form_field(
                                "E-mail",
                                ui.input(
                                    placeholder="seu@biodiagnostico.com",
                                    value=State.forgot_password_email,
                                    on_change=State.set_forgot_password_email,
                                    type="email"
                                )
                            ),
                            rx.cond(
                                State.forgot_password_message != "",
                                rx.callout(State.forgot_password_message, icon="circle_check", color_scheme="green", width="100%")
                            ),
                            rx.cond(
                                State.forgot_password_error != "",
                                rx.callout(State.forgot_password_error, icon="triangle_alert", color_scheme="red", width="100%")
                            ),
                            ui.button("Enviar Link de Recuperação", icon="mail", on_click=State.send_password_reset, width="100%", variant="secondary"),
                            gap=Spacing.MD, width="100%"
                        ),
                        width="100%", max_width="400px", padding=Spacing.LG, margin_top=Spacing.MD
                    )
                ),

                rx.hstack(
                    rx.icon(tag="shield-check", size=14, color=Color.TEXT_SECONDARY),
                    ui.text("Ambiente Seguro e Monitorado", size="caption"),
                    align_items="center",
                    gap=Spacing.XS,
                    margin_top=Spacing.XXL
                ),

                align_items="center",
                width="100%",
                padding=Spacing.LG
            ),
            width=["100%", "100%", "50%"],
            min_height="100vh",
            overflow_y="auto",
            bg=Color.BACKGROUND
        ),
        
        width="100%",
        min_height="100vh",
        display="flex",
        flex_direction=["column", "column", "row"],
        class_name="login-shell"
    )
