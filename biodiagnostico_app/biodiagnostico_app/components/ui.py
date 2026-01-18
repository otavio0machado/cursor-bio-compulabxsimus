import reflex as rx
from ..styles import Color, Design, Typography, Animation

"""
Biblioteca de Componentes Centralizada
Use estes componentes para garantir consistência visual em toda a aplicação.
"""

def heading(text: str, level: int = 1, color: str = None, **props) -> rx.Component:
    """Cabeçalho padronizado (H1-H4)"""
    styles = {
        1: Typography.H1,
        2: Typography.H2,
        3: Typography.H3,
        4: Typography.H4,
    }
    style = styles.get(level, Typography.H1).copy()
    if color:
        style["color"] = color
        
    style.update(props)
    return rx.text(text, **style)

def animated_heading(text: str, level: int = 1, color: str = None, delay: int = 100, **props) -> rx.Component:
    """Cabeçalho com animação palavra por palavra (Frame Motion like)"""
    words = text.split(" ")
    
    # Reuse heading styles logic
    styles = {
        1: Typography.H1,
        2: Typography.H2,
        3: Typography.H3,
        4: Typography.H4,
    }
    style = styles.get(level, Typography.H1).copy()
    if color:
        style["color"] = color
    style.update(props)
    
    return rx.hstack(
        *[
            rx.text(
                word,
                **style,
                opacity="0",
                animation_name="fadeInUp",
                animation_duration="0.6s",
                animation_fill_mode="forwards",
                animation_timing_function="ease-out",
                style={"animationDelay": f"{i * delay}ms"}
            ) for i, word in enumerate(words)
        ],
        spacing="3",
        justify="center",
        wrap="wrap",
        width="100%"
    )

def text(content: str, size: str = "body", color: str = None, **props) -> rx.Component:
    """Texto de corpo padronizado"""
    styles = {
        "body": Typography.BODY,
        "small": Typography.SMALL,
        "label": Typography.LABEL,
    }
    style = styles.get(size, Typography.BODY).copy()
    if color:
        style["color"] = color
        
    style.update(props)
    return rx.text(content, **style)

def card(*children, **props) -> rx.Component:
    """Container card padrão com sombra e bordas arredondadas"""
    base_style = {
        "bg": Color.SURFACE,
        "border": f"1px solid {Color.BORDER}",
        "border_radius": Design.RADIUS_XL,
        "padding": "1.5rem",
        "box_shadow": Design.SHADOW_DEFAULT,
        "transition": "all 0.3s ease",
        "_hover": {"box_shadow": Design.SHADOW_MD, "transform": "translateY(-2px)"},
    }

    # Merge styles handling duplicates carefully (props take precedence)
    final_style = base_style.copy()
    final_style.update(props)
    
    return rx.box(*children, **final_style)

def button(
    label: str, 
    icon: str = None, 
    variant: str = "primary",  # primary, secondary, ghost, danger
    on_click = None,
    is_loading: bool = False,
    loading_text: str = "Carregando...",
    **props
) -> rx.Component:
    """Botão unificado com variantes"""
    
    # Base styles
    base_style = {
        "padding_y": "0.75rem",
        "padding_x": "1.5rem",
        "border_radius": Design.RADIUS_LG,
        "font_weight": "600",
        "cursor": "pointer",
        "display": "flex",
        "align_items": "center",
        "justify_content": "center",
        "transition": "all 0.2s ease",
        "gap": "0.5rem",
    }

    # Variant styles
    variants = {
        "primary": {
            "bg": Color.PRIMARY,
            "color": "white",
            "border": "1px solid transparent",
            "box_shadow": Design.SHADOW_SM,
            "_hover": {"bg": Color.PRIMARY_HOVER, "box_shadow": Design.SHADOW_MD, "transform": "translateY(-1px)"},
        },
        "secondary": {
            "bg": "transparent",
            "color": Color.DEEP,
            "border": f"1px solid {Color.BORDER}",
            "_hover": {"bg": Color.PRIMARY_LIGHT, "border_color": Color.PRIMARY},
        },
        "ghost": {
            "bg": "transparent",
            "color": Color.TEXT_SECONDARY,
            "padding_x": "0.75rem",
            "_hover": {"bg": "#F3F4F6", "color": Color.DEEP},
        },
        "danger": {
            "bg": "#FEF2F2",
            "color": "#DC2626",
            "border": "1px solid #FECACA",
            "_hover": {"bg": "#FEE2E2", "border_color": "#FCA5A5"},
        }
    }
    
    current_variant = variants.get(variant, variants["primary"])
    
    # Content construction
    loading_content = rx.hstack(
        rx.spinner(size="1", color="current"),
        rx.text(loading_text),
        align="center",
        spacing="2"
    )

    normal_content = rx.hstack(
        rx.cond(icon is not None, rx.icon(icon or "help-circle", size=18)),
        rx.text(label),
        align="center",
        spacing="2"
    )
        
    # Merge disabled state
    user_disabled = props.pop("disabled", False)
    should_disable = is_loading | user_disabled

    # Merge styles
    final_style = base_style.copy()
    final_style.update(current_variant)
    final_style.update(props)

    return rx.button(
        rx.cond(is_loading, loading_content, normal_content),
        on_click=on_click,
        disabled=should_disable,
        **final_style
    )

def form_field(label: str, control: rx.Component, required: bool = False, error: str = "") -> rx.Component:
    """Campo de formulário com label e tratamento de erro"""
    return rx.vstack(
        rx.hstack(
            rx.text(label, **Typography.LABEL),
            rx.cond(required, rx.text("*", color=Color.ERROR, font_size="0.875rem")),
            spacing="1",
        ),
        control,
        rx.cond(
            error != "",
            rx.text(error, color=Color.ERROR, font_size="0.75rem"),
        ),
        spacing="1",
        width="100%",
        align_items="start",
    )

def input(placeholder: str = "", **props) -> rx.Component:
    """Input text padronizado"""
    base_style = {
        "placeholder": placeholder,
        "color": Color.TEXT_PRIMARY,
        "height": "3rem",
        "border": f"1px solid {Color.BORDER}",
        "border_radius": Design.RADIUS_LG,
        "padding": "0.75rem 1rem",
        "bg": Color.SURFACE,
        "width": "100%",
        "_placeholder": {"color": Color.TEXT_PRIMARY, "opacity": 1},
        "_focus": {
            "border_color": Color.PRIMARY,
            "outline": "none",
            "box_shadow": f"0 0 0 3px {Color.PRIMARY}20",
        },
    }
    base_style.update(props)
    
    return rx.input(**base_style)

def select(items, placeholder: str = "Selecione...", value=None, on_change=None, **props) -> rx.Component:
    """Select padronizado - suporta listas dinâmicas"""
    # Estilo base
    trigger_style = {
        "border": f"1px solid {Color.BORDER}",
        "border_radius": Design.RADIUS_LG,
        "height": "3rem",
        "width": "100%",
        "bg": Color.SURFACE,
    }
    
    # Mesclar props de estilo
    trigger_style.update({k: v for k, v in props.items() if k not in ['on_change', 'value']})
    
    return rx.select.root(
        rx.select.trigger(
            placeholder=placeholder,
            **trigger_style
        ),
        rx.select.content(
            rx.foreach(
                items,
                lambda item: rx.select.item(item, value=item)
            ),
        ),
        value=value,
        on_change=on_change,
    )

def text_area(placeholder: str = "", **props) -> rx.Component:
    """TextArea padronizado"""
    base_style = {
        "placeholder": placeholder,
        "border": f"1px solid {Color.BORDER}",
        "border_radius": Design.RADIUS_LG,
        "padding": "0.75rem 1rem",
        "bg": Color.SURFACE,
        "width": "100%",
        "min_height": "100px",
        "color": Color.TEXT_PRIMARY,
        "_placeholder": {"color": Color.TEXT_PRIMARY, "opacity": 1},
        "_focus": {
            "border_color": Color.PRIMARY,
            "outline": "none",
            "box_shadow": f"0 0 0 3px {Color.PRIMARY}20",
        },
    }
    base_style.update(props)
    
    return rx.text_area(**base_style)

def status_badge(text: str, status: str = "default") -> rx.Component:
    """Badge de status (success, error, warning, info)"""
    colors = {
        "success": {"bg": Color.SUCCESS_BG, "color": Color.SUCCESS},
        "error": {"bg": Color.ERROR_BG, "color": Color.ERROR},
        "warning": {"bg": Color.WARNING_BG, "color": Color.WARNING},
        "info": {"bg": "#EFF6FF", "color": "#1D4ED8"}, # Blue
        "brand": {"bg": "#F3E8FF", "color": "#7E22CE"}, # Purple
        "default": {"bg": "#F3F4F6", "color": Color.TEXT_SECONDARY},
    }
    style = colors.get(status, colors["default"])
    
    return rx.badge(
        text,
        bg=style["bg"],
        color=style["color"],
        padding_x="0.75rem",
        padding_y="0.25rem",
        border_radius="full",
        variant="soft",
        font_weight="500",
    )

def stat_card(title: str, value: str, icon: str, trend: str = "neutral", subtext: str = "") -> rx.Component:
    """Card de estatística para dashboards"""
    return card(
        rx.vstack(
            rx.hstack(
                rx.box(
                    rx.icon(icon, size=24, color=Color.DEEP),
                    class_name="p-3 rounded-xl bg-gray-50",
                ),
                rx.spacer(),
                rx.cond(
                    subtext != "",
                    status_badge(subtext, status=trend),
                ),
                width="100%",
                align="center",
            ),
            rx.vstack(
                rx.text(value, font_size="2rem", font_weight="700", color=Color.DEEP, line_height="1"),
                rx.text(title, font_size="0.875rem", font_weight="500", color=Color.TEXT_SECONDARY),
                spacing="1", 
                align="start"
            ),
            spacing="4",
        )
    )

def page_header(title: str, subtitle: str) -> rx.Component:
    """Cabeçalho de página padrão centralizado"""
    return rx.box(
        rx.vstack(
            heading(title, level=2, font_size="1.5rem", text_align="center"),
            text(subtitle, size="body", text_align="center"),
            spacing="1",
            align="center",
        ),
        class_name="mb-8 flex justify-center w-full"
    )
