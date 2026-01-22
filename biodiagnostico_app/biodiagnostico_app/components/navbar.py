import reflex as rx
from ..state import State
from ..styles import Color, Spacing, Design

def navbar_link(text: str, url: str, icon: str) -> rx.Component:
    """Link de navegação com estados visuais claros e acessíveis"""
    
    # Map internal IDs to routes
    route_map = {
        "dashboard": "/dashboard",
        "conversor": "/conversor",
        "analise": "/analise",
        "proin": "/proin",
        "api": "/settings"
    }
    href = route_map.get(url, "/")
    
    # Use the router path to detect active page (works with direct navigation)
    is_active = rx.State.router.page.path == href

    return rx.link(
        rx.vstack(
            rx.hstack(
                rx.icon(
                    tag=icon,
                    size=20,
                    color=rx.cond(is_active, Color.PRIMARY, Color.TEXT_SECONDARY)
                ),
                rx.text(
                    text,
                    font_weight=rx.cond(is_active, "700", "500"),
                    font_size="1rem",
                    transition="all 0.2s ease",
                ),
                style={"gap": "8px"},
                align="center",
                color=rx.cond(is_active, Color.PRIMARY, Color.TEXT_SECONDARY),
                padding_x=Spacing.MD,
                padding_y=Spacing.SM,
                border_radius=Design.RADIUS_LG,
                transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
                _hover={"bg": Color.PRIMARY_LIGHT, "transform": "translateY(-1px)"},
                min_height="44px",
            ),
            # Active Indicator Line
            rx.cond(
                is_active,
                rx.box(
                    width="40%",
                    height="3px",
                    bg=Color.PRIMARY,
                    border_radius="full",
                    animation="fadeIn 0.3s ease",
                ),
                rx.box(width="0%", height="3px", bg="transparent")
            ),
            spacing="0",
            align="center",
        ),
        href=href,
        text_decoration="none",
        _focus_visible={
            "outline": f"2px solid {Color.PRIMARY}",
            "outline_offset": "2px"
        }
    )

def navbar() -> rx.Component:
    """Barra de navegação principal com estilos aprimorados e responsivos"""
    return rx.box(
        rx.hstack(
            # Logo / Brand
            rx.box(
                rx.image(
                    src="/logo.jpg",
                    height=["35px", "45px", "50px"],
                    width="auto",
                    alt="Logo Biodiagnóstico",
                    object_fit="contain",
                ),
                cursor="pointer",
                on_click=lambda: State.set_page("dashboard"),
                padding=Spacing.XS,
                border_radius=Design.RADIUS_MD,
                transition="all 0.2s ease",
            ),

            rx.spacer(),

            # Desktop Navigation Links
            rx.hstack(
                navbar_link("Dashboard", "dashboard", "layout_dashboard"),
                navbar_link("Conversor PDF", "conversor", "file_text"),
                navbar_link("Análise", "analise", "chart_bar"),
                navbar_link("Proin QC", "proin", "activity"),
                style={"gap": "8px"},
                display=["none", "none", "lg", "flex"],
                padding=Spacing.XS,
                border_radius=Design.RADIUS_XL,
                bg=Color.BACKGROUND,
                border=f"1px solid {Color.BORDER}"
            ),

            rx.spacer(display=["none", "none", "lg", "flex"]),

            # Right Side
            rx.hstack(
                rx.box(
                    rx.icon(tag="bell", size=20, color=Color.TEXT_SECONDARY),
                    padding=Spacing.SM,
                    border_radius="full",
                    cursor="pointer",
                    display=["none", "flex", "flex"],
                    _hover={"bg": Color.PRIMARY_LIGHT, "color": Color.PRIMARY}
                ),
                
                rx.menu.root(
                    rx.menu.trigger(
                        rx.hstack(
                            rx.avatar(fallback="AD", size="2", radius="full", cursor="pointer", bg=Color.PRIMARY, color="white"),
                            rx.vstack(
                                rx.text("Admin", font_size="0.875rem", font_weight="600", color=Color.TEXT_PRIMARY),
                                spacing="0",
                                display=["none", "none", "md", "flex"]
                            ),
                            rx.icon(tag="chevron_down", size=16, color=Color.TEXT_SECONDARY),
                            style={"gap": "8px"},
                            align="center",
                            padding=f"{Spacing.XS} {Spacing.SM}",
                            border_radius="full",
                            cursor="pointer",
                            _hover={"bg": Color.BACKGROUND}
                        ),
                    ),
                    rx.menu.content(
                        rx.menu.item("Configurações", on_select=lambda: State.set_page("api")),
                        rx.menu.separator(),
                        rx.menu.item("Sair", color="red", on_select=State.logout),
                    ),
                ),

                rx.box(
                    mobile_nav_trigger(),
                    display=["flex", "flex", "lg", "none"]
                ),
                
                spacing={"initial": "2", "sm": "4"},
                align="center"
            ),

            width="100%",
            align="center",
            padding_x=[Spacing.MD, Spacing.LG],
            padding_y=Spacing.SM,
            background_color="rgba(255, 255, 255, 0.8)",
            backdrop_filter="blur(16px) saturate(180%)",
            border="1px solid rgba(255, 255, 255, 0.5)",
            border_radius=Design.RADIUS_XL,
            box_shadow="0 10px 30px -10px rgba(0, 0, 0, 0.1)",
        ),
        width="100%",
        position="sticky",
        top=["0.5rem", "1rem"],
        z_index="1000",
        padding_x=[Spacing.SM, Spacing.MD, Spacing.LG],
    )

def mobile_nav_trigger() -> rx.Component:
    """Gatilho para o menu mobile (Hamburger)"""
    return rx.menu.root(
        rx.menu.trigger(
            rx.box(
                rx.icon(tag="menu", size=24, color=Color.TEXT_PRIMARY),
                padding=Spacing.SM,
                border_radius=Design.RADIUS_MD,
                cursor="pointer",
                bg=Color.BACKGROUND,
                _hover={"bg": Color.PRIMARY_LIGHT}
            )
        ),
        rx.menu.content(
            rx.menu.item(rx.hstack(rx.icon(tag="layout_dashboard", size=18), rx.text("Dashboard", font_size="1rem")), on_select=lambda: State.set_page("dashboard"), padding="12px"),
            rx.menu.item(rx.hstack(rx.icon(tag="file_text", size=18), rx.text("Conversor PDF", font_size="1rem")), on_select=lambda: State.set_page("conversor"), padding="12px"),
            rx.menu.item(rx.hstack(rx.icon(tag="chart_bar", size=18), rx.text("Análise", font_size="1rem")), on_select=lambda: State.set_page("analise"), padding="12px"),
            rx.menu.item(rx.hstack(rx.icon(tag="activity", size=18), rx.text("Proin QC", font_size="1rem")), on_select=lambda: State.set_page("proin"), padding="12px"),
            rx.menu.separator(),
            rx.menu.item(rx.hstack(rx.icon(tag="settings", size=18), rx.text("Configurações", font_size="1rem")), on_select=lambda: State.set_page("api"), padding="12px"),
            rx.menu.item(rx.hstack(rx.icon(tag="log_out", size=18), rx.text("Sair", font_size="1rem")), color="red", on_select=State.logout, padding="12px"),
            size="2",
            width="220px",
        )
    )

def mobile_nav() -> rx.Component:
    return rx.fragment()
