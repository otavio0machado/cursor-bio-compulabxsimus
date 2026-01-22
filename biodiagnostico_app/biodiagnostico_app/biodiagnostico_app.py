"""
Biodiagnóstico Lab - Sistema de Administração
Design oficial baseado na identidade visual do laboratório
"""
import reflex as rx
from .state import State
from .components.navbar import navbar, mobile_nav
from .pages.login import login_page
from .pages.conversor import conversor_page
from .pages.analise import analise_page
from .pages.proin import proin_page
from .pages.dashboard import dashboard_page
from .styles import Color


from .pages.insight_chat import insight_chat_page

def main_content() -> rx.Component:
    """Conteúdo principal baseado na página atual"""
    return rx.match(
        State.current_page,
        ("dashboard", dashboard_page()),
        ("conversor", conversor_page()),
        ("analise", analise_page()),
        ("proin", proin_page()),
        ("detetive", insight_chat_page()), # New page match
        dashboard_page(),  # default
    )


def authenticated_layout(content: rx.Component = None) -> rx.Component:
    """Layout com navbar no topo - Design Moderno"""
    return rx.box(
        rx.vstack(
            # Navbar no topo (Contém logo e menu mobile/desktop)
            navbar(),
            
            # Conteúdo principal
            rx.box(
                content if content else main_content(), # Usa o conteúdo passado ou o padrão dinâmico
                width="100%",
                max_width="1400px",
                margin_x="auto",
                padding_x=["0.75rem", "1.5rem", "3rem"], # Menos padding no mobile para aproveitar espaço
                padding_y=["1rem", "2rem"], # Menos padding vertical no mobile
            ),
            
            spacing="0",
            width="100%",
            min_height="100vh",
            bg=Color.BACKGROUND,
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


def index_dashboard() -> rx.Component:
    """Rota Dashboard"""
    return authenticated_layout(dashboard_page())

def route_conversor() -> rx.Component:
    """Rota Conversor"""
    return authenticated_layout(conversor_page())

def route_analise() -> rx.Component:
    """Rota Análise"""
    return authenticated_layout(analise_page())

def route_proin() -> rx.Component:
    """Rota ProIn QC"""
    return authenticated_layout(proin_page())

def route_insights() -> rx.Component:
    """Rota Detetive de Dados"""
    return authenticated_layout(insight_chat_page())

# Configurar aplicação
app = rx.App(
    theme=rx.theme(
        accent_color="jade",
        gray_color="slate",
        radius="large",
    ),
    head_components=[
        rx.el.link(rel="manifest", href="/manifest.json"),
        rx.el.meta(name="theme-color", content=Color.DEEP),
        rx.el.meta(name="apple-mobile-web-app-capable", content="yes"),
        rx.el.meta(name="mobile-web-app-capable", content="yes"),
        rx.el.meta(name="apple-mobile-web-app-status-bar-style", content="black-translucent"),
    ],
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap",
        "/custom.css",
    ],
)

# Adicionar rotas explícitas - Isso resolve os erros 404 e permite refresh
app.add_page(index, route="/", title="Biodiagnóstico - Login", on_load=State.load_data_from_db)
app.add_page(index_dashboard, route="/dashboard", title="Biodiagnóstico - Dashboard", on_load=State.load_data_from_db)
app.add_page(route_conversor, route="/conversor", title="Biodiagnóstico - Conversor PDF")
app.add_page(route_analise, route="/analise", title="Biodiagnóstico - Análise", on_load=State.load_saved_analyses)
app.add_page(route_proin, route="/proin", title="Biodiagnóstico - ProIn QC", on_load=State.load_data_from_db)
app.add_page(route_insights, route="/detetive", title="Biodiagnóstico - Bio IA")
