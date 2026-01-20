import reflex as rx
from ..state import State
from ..styles import Color, INPUT_STYLE, BUTTON_PRIMARY_STYLE

def login_page() -> rx.Component:
    """Página de login com design moderno e padronizado"""
    return rx.flex(
        # Lado esquerdo - Formulário de Login
        rx.box(
            rx.vstack(
                # Logo
                rx.image(
                    src="/logo_lab.jpg",
                    width="auto",
                    height="100px",
                    object_fit="contain",
                    margin_bottom="1rem"
                ),
                
                # Formulário
                rx.box(
                    rx.vstack(
                        # E-mail
                        rx.box(
                            rx.text("E-mail", font_size="0.875rem", font_weight="600", color=Color.TEXT_PRIMARY, margin_bottom="0.5rem"),
                            rx.input(
                                placeholder="seu@email.com",
                                value=State.login_email,
                                on_change=State.set_login_email,
                                type="email",
                                **INPUT_STYLE
                            ),
                            width="100%",
                        ),
                        
                        # Senha
                        rx.box(
                            rx.text("Senha", font_size="0.875rem", font_weight="600", color=Color.TEXT_PRIMARY, margin_bottom="0.5rem"),
                            rx.input(
                                placeholder="Digite sua senha",
                                value=State.login_password,
                                on_change=State.set_login_password,
                                type="password",
                                **INPUT_STYLE
                            ),
                            width="100%",
                        ),
                        
                        # Mensagem de erro
                        rx.cond(
                            State.login_error != "",
                            rx.box(
                                rx.text(State.login_error, color=Color.ERROR, font_size="0.875rem"),
                                bg=Color.ERROR_BG,
                                border=f"1px solid {Color.ERROR}40",
                                border_radius="8px",
                                padding="0.75rem",
                                width="100%"
                            ),
                        ),
                        
                        # Botão de Login
                        rx.button(
                            "Login",
                            on_click=State.attempt_login,
                            width="100%",
                            margin_top="1rem",
                            **BUTTON_PRIMARY_STYLE
                        ),
                        
                        spacing="5",
                        width="100%",
                    ),
                    class_name="mt-8 w-full max-w-md"
                ),
                
                spacing="0",
                align="center",
                width="100%",
                class_name="max-w-md mx-auto"
            ),
            width=["100%", "100%", "50%"],
            bg="white",
            display="flex",
            flex_direction="column",
            justify_content="center",
            padding_x=["2rem", "4rem"],
            padding_y="3rem",
            min_height=["auto", "auto", "100vh"]
        ),
        
        # Lado direito - Seção de boas-vindas
        rx.box(
            rx.vstack(
                rx.box(flex="1"), # Spacer top
                
                # Texto de boas-vindas
                rx.text("Bem-vindo ao", font_size=["2rem", "3rem"], font_weight="bold", line_height="1.2"),
                rx.text("Portal Administrativo", font_size=["2rem", "3rem"], font_weight="bold", line_height="1.2"),
                
                rx.box(flex="1"),  # Spacer bottom
                
                # Informações de contato
                rx.hstack(
                    rx.hstack(
                        rx.icon("phone", size=16),
                        rx.text("Contato: (11) 5555-1234"),
                        spacing="2",
                    ),
                    rx.text("|", margin_x="0.5rem"),
                    rx.text("suporte@biodiagnostico.com.br"),
                    spacing="2",
                    font_size="0.875rem",
                    opacity="0.9"
                ),
                
                spacing="0",
                align="center",
                height="100%",
                padding_y="3rem"
            ),
            width=["100%", "100%", "50%"],
            bg="linear-gradient(135deg, #1B5E20 0%, #2E7D32 100%)",
            color="white",
            display=["none", "none", "flex"], # Escondido em mobile muito pequeno se desejar
            flex_direction="column",
            padding_x=["2rem", "4rem"],
            min_height="100vh"
        ),
        
        width="100%",
        min_height="100vh",
        flex_direction=["column", "column", "row"], # Stack em mobile, row em desktop
        class_name="font-sans"
    )
