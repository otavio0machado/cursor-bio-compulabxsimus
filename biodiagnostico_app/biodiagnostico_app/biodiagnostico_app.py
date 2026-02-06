"""
Biodiagnóstico Lab - Sistema de Controle de Qualidade
"""
import reflex as rx
from .state import State
from .components.navbar import navbar, mobile_nav
from .pages.login import login_page
from .pages.proin import proin_page
from .pages.dashboard import dashboard_page
from .styles import Color, Design, Spacing


def main_content() -> rx.Component:
    """Conteúdo principal baseado na página atual"""
    return rx.match(
        State.current_page,
        ("dashboard", dashboard_page()),
        ("proin", proin_page()),
        dashboard_page(),  # default
    )


def authenticated_layout(content: rx.Component = None) -> rx.Component:
    """Layout com navbar no topo"""
    return rx.box(
        rx.vstack(
            navbar(),
            rx.box(
                content if content else main_content(),
                width="100%",
                max_width=Design.MAX_WIDTH_APP,
                margin_x="auto",
                padding_x=[Spacing.SM_MD, Spacing.LG, Spacing.XXL],
                padding_y=[Spacing.MD, Spacing.XL],
            ),
            spacing="0",
            width="100%",
            min_height="100vh",
            bg="transparent",
            position="relative",
            z_index="1",
        ),
        class_name="app-shell"
    )


def index() -> rx.Component:
    """Página principal - Login obrigatório"""
    return rx.cond(
        State.is_authenticated,
        authenticated_layout(),
        login_page()
    )


def index_dashboard() -> rx.Component:
    """Rota Dashboard"""
    return rx.cond(
        State.is_authenticated,
        authenticated_layout(dashboard_page()),
        login_page()
    )


def route_proin() -> rx.Component:
    """Rota Controle de Qualidade"""
    return rx.cond(
        State.is_authenticated,
        authenticated_layout(proin_page()),
        login_page()
    )


# Configurar aplicação
app = rx.App(
    theme=rx.theme(
        accent_color="green",
        gray_color="slate",
        radius="large",
    ),
    head_components=[
        rx.el.link(rel="manifest", href="/manifest.json"),
        rx.el.meta(name="theme-color", content=Color.PRIMARY),
        rx.el.meta(name="apple-mobile-web-app-capable", content="yes"),
        rx.el.meta(name="mobile-web-app-capable", content="yes"),
        rx.el.meta(name="apple-mobile-web-app-status-bar-style", content="black-translucent"),
    ],
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=DM+Sans:wght@400;500;600;700&display=swap",
        "/custom.css",
    ],
)

# Rotas
app.add_page(index, route="/", title="QC Lab - Login", on_load=[State.restore_session, State.load_data_from_db])
app.add_page(index_dashboard, route="/dashboard", title="QC Lab - Dashboard", on_load=[State.restore_session, State.load_data_from_db])
app.add_page(route_proin, route="/proin", title="QC Lab - Controle de Qualidade", on_load=[State.restore_session, State.load_data_from_db])
