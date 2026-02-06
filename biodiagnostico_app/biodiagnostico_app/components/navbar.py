import reflex as rx
from ..state import State
from ..styles import Color, Spacing, Design, Typography, GLASS_STYLE

def navbar_link(text: str, url: str, icon: str) -> rx.Component:
    """Link de navegação com estados visuais claros e acessíveis"""

    route_map = {
        "dashboard": "/dashboard",
        "proin": "/proin",
    }
    href = route_map.get(url, "/")

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
                    font_size=Typography.SIZE_MD,
                    transition="all 0.2s ease",
                ),
                style={"gap": Spacing.SM},
                align="center",
                color=rx.cond(is_active, Color.DEEP, Color.TEXT_SECONDARY),
                padding_x=Spacing.MD,
                padding_y=Spacing.SM,
                border_radius=Design.RADIUS_MD,
                bg=rx.cond(is_active, Color.PRIMARY_LIGHT, "transparent"),
                border=rx.cond(is_active, f"1px solid {Color.PRIMARY}25", "1px solid transparent"),
                transition="all 0.15s ease",
                _hover={"bg": Color.SURFACE_ALT},
                min_height="40px",
            ),
            rx.cond(
                is_active,
                rx.box(
                    width="50%",
                    height="2px",
                    bg=Color.PRIMARY,
                    border_radius=Design.RADIUS_FULL,
                    animation="fadeIn 0.2s ease",
                ),
                rx.box(width="0%", height="2px", bg="transparent")
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
    """Barra de navegação principal"""
    return rx.box(
        rx.hstack(
            # Logo / Brand
            rx.box(
                rx.image(
                    src="/logo.jpg",
                    height=["32px", "40px", "44px"],
                    width="auto",
                    alt="Logo Biodiagnóstico",
                    object_fit="contain",
                ),
                cursor="pointer",
                on_click=lambda: State.set_page("dashboard"),
                padding=Spacing.XS,
                border_radius=Design.RADIUS_SM,
                transition="all 0.15s ease",
            ),

            rx.spacer(),

            # Desktop Navigation Links
            rx.hstack(
                navbar_link("Dashboard", "dashboard", "layout_dashboard"),
                navbar_link("Controle de Qualidade", "proin", "activity"),
                style={"gap": Spacing.XS},
                display=["none", "none", "lg", "flex"],
                padding=Spacing.XS,
                border_radius=Design.RADIUS_LG,
                bg=Color.SURFACE_ALT,
                border=f"1px solid {Color.BORDER}"
            ),

            rx.spacer(display=["none", "none", "lg", "flex"]),

            # Right Side
            rx.hstack(
                rx.menu.root(
                    rx.menu.trigger(
                        rx.hstack(
                            rx.avatar(fallback="AD", size="2", radius="full", cursor="pointer", bg=Color.PRIMARY, color=Color.WHITE),
                            rx.vstack(
                                rx.text("Admin", font_size=Typography.SMALL["font_size"], font_weight="600", color=Color.TEXT_PRIMARY),
                                spacing="0",
                                display=["none", "none", "md", "flex"]
                            ),
                            rx.icon(tag="chevron_down", size=14, color=Color.TEXT_SECONDARY),
                            style={"gap": Spacing.SM},
                            align="center",
                            padding=f"{Spacing.XS} {Spacing.SM}",
                            border_radius=Design.RADIUS_FULL,
                            cursor="pointer",
                            _hover={"bg": Color.SURFACE_ALT}
                        ),
                    ),
                    rx.menu.content(
                        rx.menu.separator(),
                        rx.menu.item("Sair", color=Color.ERROR, on_select=State.logout),
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
            **GLASS_STYLE,
            border_radius=Design.RADIUS_LG,
            box_shadow=Design.SHADOW_SM,
        ),
        width="100%",
        position="sticky",
        top=["0.5rem", "0.75rem"],
        z_index=Design.Z_INDEX_NAVBAR,
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
                bg=Color.SURFACE_ALT,
                _hover={"bg": Color.BORDER}
            )
        ),
        rx.menu.content(
            rx.menu.item(rx.hstack(rx.icon(tag="layout_dashboard", size=18), rx.text("Dashboard", font_size=Typography.H4["font_size"])), on_select=lambda: State.set_page("dashboard"), padding=Spacing.SM_MD),
            rx.menu.item(rx.hstack(rx.icon(tag="activity", size=18), rx.text("Controle de Qualidade", font_size=Typography.H4["font_size"])), on_select=lambda: State.set_page("proin"), padding=Spacing.SM_MD),
            rx.menu.separator(),
            rx.menu.item(rx.hstack(rx.icon(tag="log_out", size=18), rx.text("Sair", font_size=Typography.H4["font_size"])), color=Color.ERROR, on_select=State.logout, padding=Spacing.SM_MD),
            size="2",
            width="260px",
        )
    )

def mobile_nav() -> rx.Component:
    return rx.fragment()
