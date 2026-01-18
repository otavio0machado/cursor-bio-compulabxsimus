"""
Biodiagnóstico Lab - Sistema de Administração
Design oficial baseado na identidade visual do laboratório
"""
import reflex as rx
from .state import State
from .components.navbar import navbar, mobile_nav
from .pages.conversor import conversor_page
from .pages.analise import analise_page
from .pages.proin import proin_page
from .pages.dashboard import dashboard_page
from .styles import Color, INPUT_STYLE, BUTTON_PRIMARY_STYLE



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
            display=["none", "none", "flex"], # Escondido em mobile muito pequeno se desejar, ou manter. O usuário pediu width responsivo.
            flex_direction="column",
            padding_x=["2rem", "4rem"],
            min_height="100vh"
        ),
        
        width="100%",
        min_height="100vh",
        flex_direction=["column", "column", "row"], # Stack em mobile, row em desktop
        class_name="font-sans"
    )


def api_config_page() -> rx.Component:
    """Página de configuração da API"""
    return rx.box(
        rx.vstack(
            # Badge de certificação
            rx.box(
                rx.hstack(
                    rx.text("💎", class_name="text-sm"),
                    rx.text(
                        "Certificação PNCQ Diamante",
                        class_name="text-[#1B5E20] text-sm font-medium"
                    ),
                    spacing="2",
                    align="center",
                ),
                class_name="bg-white border border-gray-200 px-4 py-2 rounded-full shadow-sm"
            ),
            
            # Título
            rx.text(
                "Configuração API Gemini",
                class_name="text-[#1B5E20] text-5xl font-bold mt-6"
            ),
            
            rx.text(
                "Configure sua chave de API para análise por Inteligência Artificial",
                class_name="text-gray-600 text-lg mt-2"
            ),
            
            # Card de configuração
            rx.box(
                rx.vstack(
                    rx.text(
                        "🔑 API Key do Google Gemini",
                        class_name="text-[#1B5E20] font-semibold text-lg"
                    ),
                    rx.input(
                        placeholder="Cole sua API Key aqui...",
                        type="password",
                        value=State.gemini_api_key,
                        on_change=State.set_api_key,
                        class_name="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-[#4CAF50] focus:ring-2 focus:ring-green-200 transition-all text-lg"
                    ),
                    rx.cond(
                        State.gemini_api_key != "",
                        rx.box(
                            rx.hstack(
                                rx.text("✅"),
                                rx.text("API Key configurada!"),
                                spacing="2",
                            ),
                            class_name="bg-green-50 border border-green-200 text-green-700 rounded-lg p-3 w-full"
                        ),
                    ),
                    spacing="4",
                    width="100%",
                ),
                class_name="bg-white border border-gray-200 rounded-2xl p-6 mt-8 max-w-xl w-full shadow-sm"
            ),
            
            # Instruções
            rx.box(
                rx.vstack(
                    rx.text(
                        "📋 Como obter sua API Key:",
                        class_name="text-[#1B5E20] font-semibold text-lg"
                    ),
                    rx.ordered_list(
                        rx.list_item(
                            rx.hstack(
                                rx.text("1. Acesse"),
                                rx.link(
                                    "Google AI Studio",
                                    href="https://makersuite.google.com/app/apikey",
                                    is_external=True,
                                    class_name="text-[#4CAF50] hover:underline font-medium"
                                ),
                                spacing="1",
                            )
                        ),
                        rx.list_item("2. Faça login com sua conta Google"),
                        rx.list_item("3. Clique em 'Create API Key'"),
                        rx.list_item("4. Copie a chave gerada e cole acima"),
                        class_name="text-gray-700 space-y-2 ml-4 list-decimal"
                    ),
                    spacing="3",
                    width="100%",
                    align="start",
                ),
                class_name="bg-gray-50 border border-gray-200 rounded-2xl p-6 mt-6 max-w-xl w-full"
            ),
            
            spacing="0",
            align="center",
            width="100%",
            class_name="py-8"
        ),
        width="100%",
    )


def main_content() -> rx.Component:
    """Conteúdo principal baseado na página atual"""
    return rx.match(
        State.current_page,
        ("dashboard", dashboard_page()),
        ("conversor", conversor_page()),
        ("analise", analise_page()),
        ("api", api_config_page()),
        ("proin", proin_page()),
        dashboard_page(),  # default
    )


def authenticated_layout() -> rx.Component:
    """Layout com navbar no topo - Design Moderno"""
    return rx.box(
        rx.vstack(
            # Navbar no topo
            navbar(),
            
            # Mobile nav (hamburger menu para telas pequenas)
            mobile_nav(),
            
            # Conteúdo principal
            rx.box(
                main_content(),
                width="100%",
                max_width="1400px",
                margin_x="auto",
                padding_x=["1rem", "2rem", "3rem"],
                padding_y="2rem",
            ),
            
            spacing="0",
            width="100%",
            min_height="100vh",
            bg="#F8FAFC",
        ),
        class_name="font-sans"
    )



def index() -> rx.Component:
    """Página principal - Login obrigatório para acesso interno"""
    return rx.cond(
        State.is_authenticated,
        authenticated_layout(),
        login_page()
    )


# Configurar aplicação
app = rx.App(
    theme=rx.theme(
        accent_color="green",
        gray_color="slate",
        radius="large",
    ),
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap",
        "/custom.css",
    ],
)

app.add_page(index, route="/", title="Biodiagnóstico - Sistema de Administração", on_load=State.load_data_from_db)
