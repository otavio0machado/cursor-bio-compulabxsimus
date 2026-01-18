"""
Biodiagnóstico Lab - Sistema de Administração
Design oficial baseado na identidade visual do laboratório - Premium SaaS Edition
"""
import reflex as rx
from .state import State
from .components.sidebar import sidebar, mobile_nav
from .pages.conversor import conversor_page
from .pages.analise import analise_page
from .pages.proin import proin_page


def login_page() -> rx.Component:
    """Página de login com design moderno e premium"""
    return rx.box(
        rx.hstack(
            # Lado esquerdo - Formulário de Login
            rx.box(
                rx.vstack(
                    # Logo
                    rx.hstack(
                        rx.box(
                            rx.icon("flask-conical", size=32, color="white"),
                            class_name="bg-gradient-to-br from-[#4CAF50] to-[#1B5E20] p-3.5 rounded-2xl shadow-lg shadow-green-900/20"
                        ),
                        rx.vstack(
                            rx.text("LABORATÓRIO", class_name="text-xs font-bold text-gray-400 tracking-[0.2em] leading-none"),
                            rx.text("BIODIAGNÓSTICO", class_name="text-2xl font-bold text-[#1B5E20] leading-tight"),
                            spacing="1",
                            align="start",
                        ),
                        spacing="4",
                        align="center",
                    ),
                    
                    rx.text(
                        "Bem-vindo de volta",
                        class_name="text-4xl font-bold text-gray-900 mt-12 mb-2"
                    ),
                    rx.text(
                        "Acesse o portal administrativo para gerenciar suas análises.",
                        class_name="text-gray-500 mb-8"
                    ),

                    # Formulário
                    rx.box(
                        rx.vstack(
                            # E-mail
                            rx.box(
                                rx.text("E-mail Corporativo", class_name="text-sm font-semibold text-gray-700 mb-2 ml-1"),
                                rx.input(
                                    placeholder="seu@biodiagnostico.com.br",
                                    value=State.login_email,
                                    on_change=State.set_login_email,
                                    type="email",
                                    class_name="w-full px-5 py-4 rounded-xl border border-gray-200 bg-gray-50/50 focus:bg-white focus:border-[#4CAF50] focus:ring-4 focus:ring-green-500/10 transition-all text-sm font-medium shadow-sm outline-none"
                                ),
                                width="100%",
                            ),
                            
                            # Senha
                            rx.box(
                                rx.hstack(
                                    rx.text("Senha", class_name="text-sm font-semibold text-gray-700 ml-1"),
                                    rx.spacer(),
                                    rx.text("Esqueceu a senha?", class_name="text-xs font-medium text-[#4CAF50] hover:text-[#1B5E20] cursor-pointer"),
                                    width="100%",
                                    class_name="mb-2"
                                ),
                                rx.input(
                                    placeholder="••••••••",
                                    value=State.login_password,
                                    on_change=State.set_login_password,
                                    type="password",
                                    class_name="w-full px-5 py-4 rounded-xl border border-gray-200 bg-gray-50/50 focus:bg-white focus:border-[#4CAF50] focus:ring-4 focus:ring-green-500/10 transition-all text-sm font-medium shadow-sm outline-none"
                                ),
                                width="100%",
                            ),
                            
                            # Mensagem de erro
                            rx.cond(
                                State.login_error != "",
                                rx.box(
                                    rx.hstack(
                                        rx.icon("alert-circle", size=16, class_name="text-red-600"),
                                        rx.text(State.login_error, class_name="text-red-700 text-sm font-medium"),
                                        spacing="2",
                                        align="center",
                                    ),
                                    class_name="bg-red-50 border border-red-100 rounded-xl p-3 w-full animate-shake"
                                ),
                            ),
                            
                            # Botão de Login
                            rx.button(
                                "Acessar Portal",
                                on_click=State.attempt_login,
                                class_name="w-full bg-[#1B5E20] hover:bg-[#2E7D32] text-white font-semibold py-4 rounded-xl transition-all duration-300 shadow-lg shadow-green-900/20 hover:shadow-xl hover:translate-y-[-1px] mt-2 text-sm tracking-wide"
                            ),
                            
                            spacing="5",
                            width="100%",
                        ),
                        class_name="w-full max-w-md"
                    ),
                    
                    spacing="0",
                    align="start",
                    width="100%",
                    class_name="max-w-md mx-auto"
                ),
                class_name="w-full lg:w-1/2 bg-white flex flex-col justify-center px-8 lg:px-24 py-12 relative z-10"
            ),
            
            # Lado direito - Seção de boas-vindas / Visual
            rx.box(
                rx.box(
                    class_name="absolute inset-0 bg-[#1B5E20] opacity-95 z-0"
                ),
                rx.box(
                    class_name="absolute inset-0 bg-[url('https://source.unsplash.com/random/1920x1080/?laboratory,science')] bg-cover bg-center mix-blend-overlay opacity-30 z-0"
                ),
                rx.box(
                    class_name="absolute inset-0 bg-gradient-to-t from-[#0e3310] via-transparent to-transparent z-0 opacity-80"
                ),

                rx.vstack(
                    rx.box(flex="1"),  # Spacer top
                    
                    # Conteúdo flutuante
                    rx.box(
                        rx.vstack(
                            rx.box(
                                rx.icon("microscope", size=48, class_name="text-[#4CAF50]"),
                                class_name="bg-white/10 backdrop-blur-md p-4 rounded-2xl border border-white/10 mb-6 inline-block"
                            ),
                            rx.text("Tecnologia de Ponta", class_name="text-[#4CAF50] font-bold text-sm tracking-widest uppercase mb-2"),
                            rx.text("Precisão e Excelência em Diagnósticos", class_name="text-5xl font-bold text-white leading-tight mb-6"),
                            rx.text("Sistema integrado de gestão laboratorial com certificação PNCQ Diamante. Garantia de qualidade e segurança em cada análise.", class_name="text-green-100/80 text-lg max-w-xl leading-relaxed"),

                            # Badge de certificação
                            rx.hstack(
                                rx.box(
                                    rx.text("💎", class_name="text-2xl"),
                                    class_name="w-12 h-12 bg-white/10 rounded-full flex items-center justify-center border border-white/20"
                                ),
                                rx.vstack(
                                    rx.text("PNCQ DIAMANTE", class_name="text-white font-bold text-sm tracking-wide"),
                                    rx.text("Certificação de Excelência", class_name="text-green-200/70 text-xs"),
                                    spacing="0",
                                ),
                                spacing="3",
                                align="center",
                                class_name="mt-12 bg-black/20 backdrop-blur-sm p-3 pr-6 rounded-full border border-white/5"
                            ),
                        ),
                        class_name="relative z-10"
                    ),
                    
                    rx.box(flex="1"),  # Spacer bottom
                    
                    # Footer infos
                    rx.hstack(
                        rx.text("© 2025 Biodiagnóstico", class_name="text-white/40 text-xs"),
                        rx.spacer(),
                        rx.hstack(
                            rx.text("Privacidade", class_name="text-white/40 text-xs hover:text-white cursor-pointer transition-colors"),
                            rx.text("Termos", class_name="text-white/40 text-xs hover:text-white cursor-pointer transition-colors"),
                            spacing="4",
                        ),
                        width="100%",
                        class_name="relative z-10 pt-8 border-t border-white/10"
                    ),
                    
                    spacing="0",
                    align="start",
                    height="100%",
                    class_name="p-16 lg:p-24"
                ),
                class_name="hidden lg:flex w-1/2 relative flex-col overflow-hidden"
            ),
            
            spacing="0",
            width="100%",
            height="100vh",
        ),
        class_name="font-sans"
    )


def api_config_page() -> rx.Component:
    """Página de configuração da API - Design Premium"""
    return rx.box(
        rx.vstack(
            # Badge de certificação
            rx.box(
                rx.hstack(
                    rx.text("💎", class_name="text-sm"),
                    rx.text(
                        "Certificação PNCQ Diamante",
                        class_name="text-[#1B5E20] text-xs font-bold tracking-wide uppercase"
                    ),
                    spacing="2",
                    align="center",
                ),
                class_name="bg-white border border-green-100 px-4 py-1.5 rounded-full shadow-sm mb-6"
            ),
            
            # Título
            rx.text(
                "Configuração API Gemini",
                class_name="text-[#1B5E20] text-4xl font-bold tracking-tight"
            ),
            
            rx.text(
                "Configure sua chave de API para habilitar a análise inteligente por IA",
                class_name="text-gray-500 text-lg mt-2 font-medium"
            ),
            
            # Card de configuração
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.box(
                            rx.text("🔑", class_name="text-2xl"),
                            class_name="w-12 h-12 bg-green-50 rounded-xl flex items-center justify-center"
                        ),
                        rx.vstack(
                            rx.text(
                                "API Key do Google Gemini",
                                class_name="text-[#1B5E20] font-bold text-lg"
                            ),
                            rx.text(
                                "Necessário para processamento de linguagem natural",
                                class_name="text-gray-500 text-xs"
                            ),
                            spacing="0",
                        ),
                        spacing="3",
                        align="center",
                        class_name="mb-4 w-full"
                    ),

                    rx.input(
                        placeholder="Cole sua API Key aqui (ex: AIzaSy...)",
                        type="password",
                        value=State.gemini_api_key,
                        on_change=State.set_api_key,
                        class_name="w-full px-5 py-4 rounded-xl border border-gray-200 bg-gray-50 focus:bg-white focus:border-[#4CAF50] focus:ring-4 focus:ring-green-100 transition-all text-sm font-medium outline-none"
                    ),

                    rx.cond(
                        State.gemini_api_key != "",
                        rx.box(
                            rx.hstack(
                                rx.icon("check-circle-2", size=18),
                                rx.text("API Key configurada e pronta para uso", class_name="font-medium"),
                                spacing="2",
                                align="center",
                            ),
                            class_name="bg-green-50 border border-green-200 text-green-700 rounded-xl p-3 w-full text-sm mt-2"
                        ),
                    ),
                    spacing="2",
                    width="100%",
                ),
                class_name="bg-white border border-gray-100 rounded-3xl p-8 mt-8 max-w-2xl w-full shadow-xl shadow-green-900/5"
            ),
            
            # Instruções
            rx.box(
                rx.vstack(
                    rx.text(
                        "Como obter sua chave de acesso",
                        class_name="text-[#1B5E20] font-bold text-lg mb-4"
                    ),
                    rx.vstack(
                        rx.hstack(
                            rx.box(rx.text("1", class_name="text-white font-bold text-xs"), class_name="w-6 h-6 bg-[#4CAF50] rounded-full flex items-center justify-center shrink-0"),
                            rx.hstack(rx.text("Acesse o", class_name="text-gray-600"), rx.link("Google AI Studio", href="https://makersuite.google.com/app/apikey", is_external=True, class_name="text-[#4CAF50] font-semibold hover:underline"), spacing="1"),
                            align="center",
                        ),
                        rx.hstack(
                            rx.box(rx.text("2", class_name="text-white font-bold text-xs"), class_name="w-6 h-6 bg-[#4CAF50] rounded-full flex items-center justify-center shrink-0"),
                            rx.text("Faça login com sua conta Google", class_name="text-gray-600"),
                            align="center",
                        ),
                        rx.hstack(
                            rx.box(rx.text("3", class_name="text-white font-bold text-xs"), class_name="w-6 h-6 bg-[#4CAF50] rounded-full flex items-center justify-center shrink-0"),
                            rx.text("Clique no botão 'Create API Key'", class_name="text-gray-600"),
                            align="center",
                        ),
                        rx.hstack(
                            rx.box(rx.text("4", class_name="text-white font-bold text-xs"), class_name="w-6 h-6 bg-[#4CAF50] rounded-full flex items-center justify-center shrink-0"),
                            rx.text("Copie a chave gerada e cole no campo acima", class_name="text-gray-600"),
                            align="center",
                        ),
                        spacing="3",
                        align="start",
                    ),
                    spacing="0",
                    width="100%",
                    align="start",
                ),
                class_name="bg-gray-50/50 border border-gray-200 rounded-3xl p-8 mt-6 max-w-2xl w-full"
            ),
            
            spacing="0",
            align="center",
            width="100%",
            class_name="py-12 px-4"
        ),
        width="100%",
    )


def main_content() -> rx.Component:
    """Conteúdo principal baseado na página atual"""
    return rx.match(
        State.current_page,
        ("conversor", conversor_page()),
        ("analise", analise_page()),
        ("api", api_config_page()),
        ("proin", proin_page()),
        conversor_page(),  # default
    )


def authenticated_layout() -> rx.Component:
    """Layout quando autenticado - Suporte a Sidebar Flutuante"""
    return rx.box(
        # Sidebar (desktop) - Componente flutuante
        rx.box(
            sidebar(),
            class_name="hidden md:block"
        ),
        
        # Conteúdo principal
        rx.box(
            rx.vstack(
                # Navegação mobile
                mobile_nav(),
                
                # Conteúdo da página
                main_content(),
                
                spacing="0",
                width="100%",
                # Padding extra no bottom para scroll
                class_name="pb-12"
            ),
            # Ajuste de margem esquerda para acomodar sidebar flutuante (64 + 4 + 4)
            # A sidebar tem w-64 (16rem) e left-4 (1rem). Total 17rem. Vamos dar 18rem ou 19rem de margem.
            # md:ml-[19rem] garante espaço.
            class_name="md:ml-[19rem] min-h-screen bg-[#F8FAFC] px-6 py-6 transition-all duration-300"
        ),
        
        class_name="font-sans bg-[#F8FAFC]"
    )


def index() -> rx.Component:
    """Página principal"""
    return authenticated_layout()


# Configurar aplicação
app = rx.App(
    theme=rx.theme(
        accent_color="green",
        gray_color="slate",
        radius="large",
    ),
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Poppins:wght@400;500;600;700&display=swap",
    ],
    style={
        "font_family": "Inter, sans-serif",
        "::selection": {
            "background_color": "#4CAF50",
            "color": "white",
        },
    }
)

app.add_page(index, route="/", title="Biodiagnóstico - Sistema de Administração")
