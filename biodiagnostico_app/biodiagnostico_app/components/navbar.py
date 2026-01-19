import reflex as rx
from ..state import State
from ..styles import Color

def navbar_link(text: str, url: str, icon: str) -> rx.Component:
    """Link de navegação com estados visuais claros e acessíveis"""
    from ..styles import Spacing, Design

    is_active = State.current_page == url
    return rx.link(
        rx.hstack(
            rx.icon(
                icon,
                size=20,  # Ícone maior para melhor visibilidade
                color=rx.cond(is_active, Color.DEEP, Color.TEXT_SECONDARY)
            ),
            rx.text(
                text,
                font_weight=rx.cond(is_active, "600", "500"),  # Negrito quando ativo
                font_size="1rem"  # 16px - texto maior
            ),
            spacing="2",
            align="center",
            color=rx.cond(is_active, Color.DEEP, Color.TEXT_SECONDARY),
            class_name=rx.cond(
                is_active,
                "bg-green-50 border-2 border-green-300 shadow-md",  # Border mais visível quando ativo
                "hover:bg-gray-50 border-2 border-transparent hover:border-gray-200"
            ),
            padding_x=Spacing.MD,  # 16px
            padding_y=Spacing.SM,  # 12px
            border_radius=Design.RADIUS_LG,  # 12px
            transition="all 0.2s ease",
            min_height="44px",  # Área de toque acessível
        ),
        on_click=lambda: State.set_page(url),
        text_decoration="none",
        _focus_visible={  # Acessibilidade por teclado
            "outline": f"2px solid {Color.PRIMARY}",
            "outline_offset": "2px"
        }
    )

def navbar() -> rx.Component:
    """Barra de navegação principal com estilos aprimorados"""
    from ..styles import Spacing, Design

    return rx.box(
        rx.hstack(
            # Logo / Brand com área de toque maior
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
                padding=Spacing.XS,  # 8px - aumenta área de clique
                border_radius=Design.RADIUS_MD,
                transition="all 0.2s ease",
                _hover={
                    "opacity": 0.8,
                    "bg": "#F9FAFB"
                }
            ),

            rx.spacer(),

            # Navigation Links com melhor espaçamento
            rx.hstack(
                navbar_link("Dashboard", "dashboard", "layout-dashboard"),
                navbar_link("Conversor PDF", "conversor", "file-text"),
                navbar_link("Análise", "analise", "bar-chart-2"),
                navbar_link("Proin QC", "proin", "activity"),
                spacing="2",
                display=["none", "flex", "flex"],
                padding=Spacing.XS,  # 8px
                border_radius=Design.RADIUS_XL,
                bg="rgba(249, 250, 251, 0.7)",  # Gray-50 com transparência
                border=f"1px solid {Color.BORDER}"
            ),

            rx.spacer(),

            # User Profile / Logout
            rx.hstack(
                # Notificações
                rx.box(
                    rx.icon("bell", size=20, color=Color.TEXT_SECONDARY),
                    padding=Spacing.SM,  # 12px - área maior
                    border_radius="full",
                    cursor="pointer",
                    transition="all 0.2s ease",
                    _hover={
                        "bg": "#F3F4F6",
                        "color": Color.PRIMARY
                    }
                ),
                # Menu do usuário
                rx.menu.root(
                    rx.menu.trigger(
                        rx.hstack(
                            rx.avatar(fallback="AD", size="2", radius="full", cursor="pointer", bg=Color.PRIMARY, color="white"),
                            rx.vstack(
                                rx.text("Admin User", font_size="0.875rem", font_weight="600", color=Color.TEXT_PRIMARY),
                                rx.text("admin@bio.com", font_size="0.75rem", color=Color.TEXT_SECONDARY),
                                spacing="0",
                                display=["none", "none", "flex"]
                            ),
                            rx.icon("chevron-down", size=16, color=Color.TEXT_SECONDARY),
                            spacing="2",
                            align="center",
                            padding=f"{Spacing.XS} {Spacing.MD}",  # 8px 16px
                            border_radius="full",
                            cursor="pointer",
                            transition="all 0.2s ease",
                            border="1px solid transparent",
                            _hover={
                                "bg": "#F9FAFB",
                                "border_color": Color.BORDER
                            }
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
            padding_x=Spacing.LG,  # 24px
            padding_y=Spacing.MD,  # 16px
            bg="rgba(255, 255, 255, 0.95)",  # Mais opaco para melhor contraste
            backdrop_filter="blur(12px)",
            border=f"1px solid {Color.BORDER}",
            border_radius=Design.RADIUS_XL,  # 16px
            box_shadow=Design.SHADOW_DEFAULT,
        ),
        width="100%",
        position="sticky",
        top="1rem",
        z_index="1000",
        padding_x=[Spacing.MD, Spacing.XL, Spacing.XL],  # Responsivo: 16px -> 32px
    )

def mobile_nav() -> rx.Component:
    """Mobile Navigation (Hamburger menu) com estilos aprimorados"""
    from ..styles import Spacing, Design

    return rx.box(
        rx.menu.root(
            rx.menu.trigger(
                rx.box(
                    rx.icon("menu", size=24, color=Color.TEXT_PRIMARY),
                    padding=Spacing.SM,  # 12px - área de toque maior
                    border_radius=Design.RADIUS_MD,
                    cursor="pointer",
                    transition="all 0.2s ease",
                    _hover={
                        "bg": "#F3F4F6"
                    }
                )
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
        display=["flex", "none", "none"],
        padding=Spacing.MD,  # 16px
        bg=Color.SURFACE,
        border_bottom=f"1px solid {Color.BORDER}",
        box_shadow=Design.SHADOW_SM
    )
