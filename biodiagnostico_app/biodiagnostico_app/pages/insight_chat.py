import reflex as rx
from ..state import State
from ..styles import Color, Spacing, Design

def chat_bubble(message: dict) -> rx.Component:
    """Renderiza uma bolha de chat individual.
    
    Usa rx.cond com a sintaxe reativa para evitar erro de ordem de hooks.
    O operador == com rx.Var retorna um rx.Var[bool] que é reativo.
    """
    # Usar o operador == diretamente gera um rx.Var[bool] reativo
    is_user = message["role"] == "user"
    
    return rx.box(
        rx.markdown(
            message["content"],
            # If user, white text. If AI, dark text.
            style={
                "color": rx.cond(is_user, "white", Color.TEXT_PRIMARY),
                "& p": {"margin": 0}, # Remove default p margin
            }
        ),
        bg=rx.cond(is_user, Color.SECONDARY, "#F3F4F6"), # Using SECONDARY/Gray
        padding=Spacing.MD,
        border_radius=Design.RADIUS_LG,
        # visual touches
        box_shadow=Design.SHADOW_SM,
        max_width=["100%", "85%", "75%"],
        margin_left=rx.cond(is_user, "auto", "0"),
        margin_right=rx.cond(is_user, "0", "auto"),
        align_self=rx.cond(is_user, "flex-end", "flex-start"),
    )

def input_area() -> rx.Component:
    return rx.hstack(
        rx.input(
            value=State.input_text,
            on_change=State.set_input_text,
            placeholder="Pergunte à Bio IA (ex: 'Qual o maior motivo de glosa?')",
            border_radius="full",
            padding_x=Spacing.LG,
            height="3.5rem",
            width="100%",
            box_shadow=Design.SHADOW_SM,
            border="1px solid " + Color.BORDER,
            _focus={"border_color": Color.PRIMARY, "box_shadow": Design.SHADOW_MD, "outline": "none"},
            bg=Color.SURFACE,
            on_key_down=State.handle_keys,
            disabled=State.is_loading,
        ),
        rx.button(
            rx.cond(
                State.is_loading,
                rx.spinner(color="white", size="2"),
                rx.icon("send", size=20)
            ),
            on_click=State.send_message,
            bg=Color.GRADIENT_PRIMARY,
            color="white",
            border_radius="full",
            width="3.5rem",
            height="3.5rem",
            box_shadow=Design.SHADOW_MD,
            _hover={"transform": "scale(1.05)", "box_shadow": Design.SHADOW_LG},
            cursor="pointer",
            disabled=State.is_loading,
        ),
        width="100%",
        padding_top=Spacing.MD,
        align_items="center",
        spacing="3"
    )

def insight_chat_page() -> rx.Component:
    """Página principal da Bio IA"""
    return rx.box(
        rx.vstack(
            # Header
            rx.box(
                rx.heading("🧬 Bio IA", size="8", color=Color.DEEP, margin_bottom="0.5rem"),
                rx.text(
                    "Inteligência Artificial para análise de faturamento e glosas.",
                    color=Color.TEXT_SECONDARY,
                    font_size="1.1rem"
                ),
                width="100%",
                padding_y=Spacing.XL,
                text_align="center",
            ),
            
            # Content Area - Chat centralizado
            rx.box(
                rx.heading("💬 Chat de Insights", size="4", margin_bottom=Spacing.MD, color=Color.DEEP),
                rx.vstack(
                    # Chat History Container
                    rx.scroll_area(
                        rx.vstack(
                            rx.foreach(
                                State.messages,
                                chat_bubble
                            ),
                            width="100%",
                            spacing="4",
                        ),
                        height="500px",
                        type="always",
                        scrollbars="vertical",
                        style={"paddingRight": "1rem"}
                    ),
                    
                    rx.spacer(),
                    
                    # Input
                    input_area(),
                    
                    bg=Color.SURFACE,
                    padding=Spacing.LG,
                    border_radius=Design.RADIUS_XL,
                    box_shadow=Design.SHADOW_DEFAULT,
                    border="1px solid " + Color.BORDER,
                    width="100%",
                    height="620px",
                    justify="between",
                ),
                width="100%",
                max_width="800px",
                margin_x="auto",
            ),
            
            width="100%",
            max_width="1400px",
            margin_x="auto",
            padding_x=Spacing.MD,
        ),
        on_mount=State.load_context,
        bg=Color.BACKGROUND,
        min_height="100vh",
    )
