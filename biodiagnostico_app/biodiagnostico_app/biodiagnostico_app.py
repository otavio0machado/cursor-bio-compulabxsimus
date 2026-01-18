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



def login_page() -> rx.Component:
    """Página de login com design moderno"""
    return rx.box(
        rx.hstack(
            # Lado esquerdo - Formulário de Login
            rx.box(
                rx.vstack(
                    # Logo
                    rx.hstack(
                        rx.box(
                            rx.icon("flask-conical", size=32, color="white"),
                            class_name="bg-gradient-to-br from-[#4CAF50] to-[#66BB6A] p-3 rounded-xl"
                        ),
                        rx.vstack(
                            rx.text("Laboratório", class_name="text-2xl font-bold text-gray-800 leading-tight"),
                            rx.text("Biodiagnóstico", class_name="text-2xl font-bold text-gray-800 leading-tight"),
                            spacing="0",
                            align="start",
                        ),
                        spacing="4",
                        align="center",
                    ),
                    
                    # Formulário
                    rx.box(
                        rx.vstack(
                            # E-mail
                            rx.box(
                                rx.text("E-mail", class_name="text-sm font-semibold text-gray-700 mb-2"),
                                rx.input(
                                    placeholder="seu@email.com",
                                    value=State.login_email,
                                    on_change=State.set_login_email,
                                    type="email",
                                    class_name="w-full px-4 py-3 rounded-lg border border-gray-200 bg-gray-50 focus:bg-white focus:border-[#4CAF50] focus:ring-2 focus:ring-green-200 transition-all"
                                ),
                                width="100%",
                            ),
                            
                            # Senha
                            rx.box(
                                rx.text("Senha", class_name="text-sm font-semibold text-gray-700 mb-2"),
                                rx.input(
                                    placeholder="Digite sua senha",
                                    value=State.login_password,
                                    on_change=State.set_login_password,
                                    type="password",
                                    class_name="w-full px-4 py-3 rounded-lg border border-gray-200 bg-gray-50 focus:bg-white focus:border-[#4CAF50] focus:ring-2 focus:ring-green-200 transition-all"
                                ),
                                width="100%",
                            ),
                            
                            # Mensagem de erro
                            rx.cond(
                                State.login_error != "",
                                rx.box(
                                    rx.text(State.login_error, class_name="text-red-700 text-sm"),
                                    class_name="bg-red-50 border border-red-200 rounded-lg p-3 w-full"
                                ),
                            ),
                            
                            # Botão de Login
                            rx.button(
                                "Login",
                                on_click=State.attempt_login,
                                class_name="w-full bg-[#4CAF50] hover:bg-[#43A047] text-white font-semibold py-3.5 px-6 rounded-lg transition-all duration-200 shadow-md hover:shadow-lg mt-4"
                            ),
                            
                            spacing="5",
                            width="100%",
                        ),
                        class_name="mt-12 w-full max-w-md"
                    ),
                    
                    spacing="0",
                    align="start",
                    width="100%",
                    class_name="max-w-md mx-auto"
                ),
                class_name="w-1/2 bg-white flex flex-col justify-center px-16 py-12"
            ),
            
            # Lado direito - Seção de boas-vindas
            rx.box(
                rx.vstack(
                    rx.box(height="100px"),  # Spacer
                    
                    # Badge de certificação
                    rx.hstack(
                        rx.box(
                            rx.icon("gem", size=24, color="#FCD34D"),
                            class_name="w-16 h-16 bg-blue-500 rounded-lg flex items-center justify-center"
                        ),
                        rx.vstack(
                            rx.text("PNCQ CERTIFICATION DIAMOND", class_name="text-sm font-semibold uppercase tracking-wide opacity-90"),
                            rx.text("QUALIDADE APROVADA", class_name="text-xs opacity-75 mt-1"),
                            spacing="0",
                            align="start",
                        ),
                        spacing="4",
                        align="center",
                    ),
                    
                    # Texto de boas-vindas
                    rx.text("Bem-vindo ao", class_name="text-4xl font-bold leading-tight mt-8"),
                    rx.text("Portal Administrativo", class_name="text-4xl font-bold leading-tight"),
                    
                    rx.box(flex="1"),  # Spacer
                    
                    # Informações de contato
                    rx.hstack(
                        rx.hstack(
                            rx.icon("phone", size=16),
                            rx.text("Contato: (11) 5555-1234"),
                            spacing="2",
                        ),
                        rx.text("|", class_name="mx-2"),
                        rx.text("suporte@biodiagnostico.com.br"),
                        spacing="2",
                        class_name="text-sm"
                    ),
                    
                    spacing="0",
                    align="start",
                    height="100%",
                    class_name="py-12"
                ),
                class_name="w-1/2 bg-gradient-to-br from-[#1B5E20] to-[#2E7D32] text-white flex flex-col px-16"
            ),
            
            spacing="0",
            width="100%",
            height="100vh",
        ),
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
    """Página principal - acesso direto ao conteúdo (sem login)"""
    return authenticated_layout()


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

app.add_page(index, route="/", title="Biodiagnóstico - Sistema de Administração")
