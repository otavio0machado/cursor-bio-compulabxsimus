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
        rx.vstack(
            rx.markdown(
                message["content"],
                # If user, white text. If AI, dark text.
                style={
                    "color": rx.cond(is_user, "white", Color.TEXT_PRIMARY),
                    "& p": {"margin": 0}, # Remove default p margin
                }
            ),
            # Action Area for AI messages
            rx.cond(
                ~is_user,
                rx.flex(
                    rx.cond(
                        message["content"].contains("divergência") | message["content"].contains("R$"),
                        rx.button(
                            rx.hstack(rx.icon("chart-bar", size=16), rx.text("Ver Detalhes")),
                            size="1",
                            variant="soft",
                            color_scheme="green",
                            on_click=State.navigate_to("analise"),
                        ),
                    ),
                    rx.cond(
                        message["content"].contains("glosa"),
                        rx.button(
                            rx.hstack(rx.icon("file-text", size=16), rx.text("Ver Relatório")),
                            size="1",
                            variant="soft",
                            color_scheme="blue",
                            on_click=State.navigate_to("conversor"),
                        ),
                    ),
                    spacing="2",
                    padding_top=Spacing.SM,
                )
            ),
            spacing="2",
            align_items="start",
        ),
        bg=rx.cond(is_user, Color.SECONDARY, Color.BACKGROUND), # Using SECONDARY/Gray
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
        rx.upload(
            rx.button(
                rx.cond(
                    State.image_files.length() > 0,
                    rx.icon("image-plus", size=20, color=Color.PRIMARY),
                    rx.icon("paperclip", size=20)
                ),
                bg="transparent",
                color=rx.cond(State.image_files.length() > 0, Color.PRIMARY, Color.TEXT_SECONDARY),
                _hover={"color": Color.PRIMARY, "bg": "rgba(76, 175, 80, 0.1)"},
                cursor="pointer",
                border="none",
                box_shadow="none",
                padding="0",
                width="2.5rem",
            ),
            id="ai_image_upload",
            multiple=True,
            accept={"image/*": [".png", ".jpg", ".jpeg"]},
            max_files=5,
            on_drop=State.handle_image_upload(rx.upload_files(upload_id="ai_image_upload")),
            border="none",
            padding="0",
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

def suggested_chips() -> rx.Component:
    return rx.flex(
        rx.foreach(
            State.suggested_actions,
            lambda action: rx.badge(
                action,
                variant="outline",
                color_scheme="green",
                padding_x="12px",
                padding_y="6px",
                border_radius="full",
                cursor="pointer",
                _hover={
                    "bg": Color.PRIMARY,
                    "color": "white",
                    "transform": "translateY(-2px)",
                    "box_shadow": Design.SHADOW_SM,
                },
                on_click=State.select_suggested_action(action),
                style={"transition": "all 0.2s ease"},
            )
        ),
        spacing="2",
        flex_wrap="wrap",
        padding_y=Spacing.SM,
        width="100%",
    )

def thinking_trace() -> rx.Component:
    return rx.cond(
        State.is_loading,
        rx.box(
            rx.vstack(
                rx.foreach(
                    State.thinking_steps,
                    lambda step: rx.hstack(
                        rx.icon("circle-check", size=14, color=Color.PRIMARY),
                        rx.text(step, font_size="0.85rem", color=Color.TEXT_SECONDARY),
                        spacing="2",
                        align_items="center",
                    )
                ),
                rx.hstack(
                    rx.spinner(size="1", color=Color.PRIMARY),
                    rx.text("Processando...", font_size="0.85rem", font_style="italic", color=Color.PRIMARY),
                    spacing="2",
                    align_items="center",
                ),
                spacing="1",
                align_items="start",
            ),
            padding=Spacing.MD,
            margin_bottom=Spacing.MD,
            bg="rgba(76, 175, 80, 0.05)",
            border_left=f"3px solid {Color.PRIMARY}",
            border_radius=Design.RADIUS_MD,
            width="100%",
            animation="fadeIn 0.5s ease-in-out",
        )
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
                    
                    # Thinking Trace
                    thinking_trace(),

                    rx.spacer(),
                    
                    # Suggestions
                    suggested_chips(),

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
