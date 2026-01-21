import reflex as rx
from ..state import State
from ..styles import Color

def navbar_link(text: str, url: str, icon: str) -> rx.Component:
    """Link de navegação com estados visuais claros e acessíveis"""
    from ..styles import Spacing, Design

    is_active = State.current_page == url
    return rx.link(
        rx.vstack(
            rx.hstack(
                rx.icon(
                    icon,
                    size=20,
                    color=rx.cond(is_active, Color.PRIMARY, Color.TEXT_SECONDARY)
                ),
                rx.text(
                    text,
                    font_weight=rx.cond(is_active, "700", "500"),
                    font_size="1rem",
                    transition="all 0.2s ease",
                ),
                spacing="2",
                align="center",
                color=rx.cond(is_active, Color.PRIMARY, Color.TEXT_SECONDARY),
                padding_x=Spacing.MD,
                padding_y=Spacing.SM,
                border_radius=Design.RADIUS_LG,
                transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
                _hover={"bg": "rgba(0, 0, 0, 0.04)", "transform": "translateY(-1px)"},
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
        on_click=lambda: State.set_page(url),
        text_decoration="none",
        _focus_visible={
            "outline": f"2px solid {Color.PRIMARY}",
            "outline_offset": "2px"
        }
    )

def navbar() -> rx.Component:
    """Barra de navegação principal com estilos aprimorados e responsivos"""
    from ..styles import Spacing, Design

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

            # Desktop Navigation Links (Hidden on mobile)
            rx.hstack(
                navbar_link("Dashboard", "dashboard", "layout_dashboard"),
                navbar_link("Conversor PDF", "conversor", "file_text"),
                navbar_link("Análise", "analise", "chart_bar"),
                navbar_link("Proin QC", "proin", "activity"),
                spacing="2",
                display=["none", "none", "lg", "flex"], # Hide on mobile and tablet
                padding=Spacing.XS,
                border_radius=Design.RADIUS_XL,
                bg="rgba(249, 250, 251, 0.7)",
                border=f"1px solid {Color.BORDER}"
            ),

            rx.spacer(display=["none", "none", "lg", "flex"]),

            # Right Side: Notifications, User & Mobile Menu
            rx.hstack(
                # Notificações (Hidden on very small screens)
                rx.box(
                    rx.icon("bell", size=20, color=Color.TEXT_SECONDARY),
                    padding=Spacing.SM,
                    border_radius="full",
                    cursor="pointer",
                    display=["none", "flex", "flex"],
                    _hover={"bg": "#F3F4F6", "color": Color.PRIMARY}
                ),
                
                # User Menu
                rx.menu.root(
                    rx.menu.trigger(
                        rx.hstack(
                            rx.avatar(fallback="AD", size="2", radius="full", cursor="pointer", bg=Color.PRIMARY, color="white"),
                            rx.vstack(
                                rx.text("Admin", font_size="0.875rem", font_weight="600", color=Color.TEXT_PRIMARY),
                                spacing="0",
                                display=["none", "none", "md", "flex"]
                            ),
                            rx.icon("chevron_down", size=16, color=Color.TEXT_SECONDARY),
                            spacing="2",
                            align="center",
                            padding=f"{Spacing.XS} {Spacing.SM}",
                            border_radius="full",
                            cursor="pointer",
                            _hover={"bg": "#F9FAFB"}
                        ),
                    ),
                    rx.menu.content(
                        rx.menu.item("Configurações", on_select=lambda: State.set_page("api")),
                        rx.menu.separator(),
                        rx.menu.item("Sair", color="red", on_select=State.logout),
                    ),
                ),

                # Mobile Menu Trigger (Visible only on mobile/tablet)
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
            border=f"1px solid rgba(255, 255, 255, 0.5)",
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
    from ..styles import Spacing, Design
    
    return rx.menu.root(
        rx.menu.trigger(
            rx.box(
                rx.icon("menu", size=24, color=Color.TEXT_PRIMARY),
                padding=Spacing.SM,
                border_radius=Design.RADIUS_MD,
                cursor="pointer",
                bg="#F3F4F6",
                _hover={"bg": "#E5E7EB"}
            )
        ),
        rx.menu.content(
            rx.menu.item(rx.hstack(rx.icon("layout-dashboard", size=18), rx.text("Dashboard", font_size="1rem")), on_select=lambda: State.set_page("dashboard"), padding="12px"),
            rx.menu.item(rx.hstack(rx.icon("file-text", size=18), rx.text("Conversor PDF", font_size="1rem")), on_select=lambda: State.set_page("conversor"), padding="12px"),
            rx.menu.item(rx.hstack(rx.icon("chart-bar", size=18), rx.text("Análise", font_size="1rem")), on_select=lambda: State.set_page("analise"), padding="12px"),
            rx.menu.item(rx.hstack(rx.icon("activity", size=18), rx.text("Proin QC", font_size="1rem")), on_select=lambda: State.set_page("proin"), padding="12px"),
            rx.menu.separator(),
            rx.menu.item(rx.hstack(rx.icon("settings", size=18), rx.text("Configurações", font_size="1rem")), on_select=lambda: State.set_page("api"), padding="12px"),
            rx.menu.item(rx.hstack(rx.icon("log-out", size=18), rx.text("Sair", font_size="1rem")), color="red", on_select=State.logout, padding="12px"),
            size="2",
            width="220px",
        )
    )

def mobile_nav() -> rx.Component:
    """Mantido por retrocompatibilidade, mas agora vazio pois o menu está no navbar"""
    return rx.fragment()

