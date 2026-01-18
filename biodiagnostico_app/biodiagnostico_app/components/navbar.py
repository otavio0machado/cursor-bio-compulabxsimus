import reflex as rx
from ..state import State
from ..styles import Color

def navbar_link(text: str, url: str, icon: str) -> rx.Component:
    is_active = State.current_page == url
    return rx.link(
        rx.hstack(
            rx.icon(icon, size=18, color=rx.cond(is_active, Color.DEEP, Color.TEXT_SECONDARY)),
            rx.text(text, font_weight="500", font_size="0.9rem"),
            spacing="2",
            align="center",
            color=rx.cond(
                is_active,
                Color.DEEP,
                Color.TEXT_SECONDARY
            ),
            class_name=rx.cond(
                is_active,
                "bg-green-50 border border-green-200 shadow-sm",
                "hover:bg-gray-50 border border-transparent"
            ),
            padding_x="1rem",
            padding_y="0.5rem",
            border_radius="10px",
            transition="all 0.2s ease"
        ),
        on_click=lambda: State.set_page(url),
        text_decoration="none"
    )

def navbar() -> rx.Component:
    return rx.box(
        rx.hstack(
            # Logo / Brand
            # Logo / Brand
            rx.box(
                rx.image(
                    src="/logo.jpg",
                    height="50px",
                    width="auto",
                    alt="Logo Biodiagnóstico",
                    object_fit="contain",
                ),
                cursor="pointer",
                on_click=lambda: State.set_page("dashboard"),
                class_name="hover:opacity-80 transition-opacity"
            ),
            
            rx.spacer(),
            
            # Navigation Links
            rx.hstack(
                navbar_link("Dashboard", "dashboard", "layout-dashboard"),
                navbar_link("Conversor PDF", "conversor", "file-text"),
                navbar_link("Análise", "analise", "bar-chart-2"),
                navbar_link("Proin QC", "proin", "activity"),
                spacing="2",
                display=["none", "flex", "flex"],
                class_name="bg-gray-50/50 p-1 rounded-xl border border-gray-100"
            ),
            
            rx.spacer(),
            
            # User Profile / Logout
            rx.hstack(
                rx.box(
                    rx.icon("bell", size=18, color=Color.TEXT_SECONDARY),
                    class_name="p-2 hover:bg-gray-100 rounded-full cursor-pointer transition-colors"
                ),
                rx.menu.root(
                    rx.menu.trigger(
                        rx.hstack(
                            rx.avatar(fallback="AD", size="2", radius="full", cursor="pointer", bg=Color.PRIMARY, color="white"),
                            rx.vstack(
                                rx.text("Admin User", font_size="0.85rem", font_weight="600", color=Color.TEXT_PRIMARY),
                                rx.text("admin@bio.com", font_size="0.7rem", color=Color.TEXT_SECONDARY),
                                spacing="0",
                                display=["none", "none", "flex"]
                            ),
                            rx.icon("chevron-down", size=16, color=Color.TEXT_SECONDARY),
                            spacing="2",
                            align="center",
                            class_name="cursor-pointer hover:bg-gray-50 p-1.5 pr-3 rounded-full transition-colors border border-transparent hover:border-gray-200"
                        ),
                    ),
                    rx.menu.content(
                        rx.menu.item("Configurações", on_select=lambda: State.set_page("api")),
                        rx.menu.separator(),
                        rx.menu.item("Sair", color="red", on_select=State.logout),
                    ),
                ),
                spacing="4",
                align="center"
            ),
            
            width="100%",
            align="center",
            padding_x="1.5rem",
            padding_y="0.75rem",
            bg="rgba(255, 255, 255, 0.9)",
            backdrop_filter="blur(10px)",
            border=f"1px solid {Color.BORDER}",
            border_radius="16px",
            box_shadow="0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03)",
        ),
        width="100%",
        position="sticky",
        top="1rem",
        z_index="1000",
        padding_x=["1rem", "2rem", "2rem"],
    )

def mobile_nav() -> rx.Component:
    """Mobile Navigation (Hamburger menu)"""
    return rx.box(
        rx.menu.root(
            rx.menu.trigger(
                rx.icon("menu", size=24, color=Color.TEXT_PRIMARY)
            ),
            rx.menu.content(
                rx.menu.item("Dashboard", on_select=lambda: State.set_page("dashboard")),
                rx.menu.item("Conversor PDF", on_select=lambda: State.set_page("conversor")),
                rx.menu.item("Análise", on_select=lambda: State.set_page("analise")),
                rx.menu.item("Proin QC", on_select=lambda: State.set_page("proin")),
                rx.menu.separator(),
                rx.menu.item("Configurações", on_select=lambda: State.set_page("api")),
                rx.menu.item("Sair", color="red", on_select=State.logout),
            )
        ),
        display=["block", "none", "none"],
        padding="1rem",
        bg="white",
        border_bottom=f"1px solid {Color.BORDER}"
    )
