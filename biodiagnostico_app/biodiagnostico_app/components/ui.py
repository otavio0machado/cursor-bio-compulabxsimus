import reflex as rx
from ..styles import Color, Design, Typography, Spacing, CARD_STYLE, BUTTON_PRIMARY_STYLE, BUTTON_SECONDARY_STYLE, BUTTON_XL_STYLE, INPUT_STYLE, INPUT_XL_STYLE

# =============================================================================
# BIODIAGNÓSTICO VIBE UI
# Centralized Component Library - Protocol K.I.S.S
# =============================================================================

# --- Typography Helpers ---

def heading(text: str, level: int = 1, color: str = None, **props) -> rx.Component:
    """Standardized Heading (H1-H5)"""
    map_level = {
        1: Typography.H1, 2: Typography.H2, 3: Typography.H3,
        4: Typography.H4, 5: Typography.H5
    }
    style = map_level.get(level, Typography.H1).copy()
    if color: style["color"] = color
    style.update(props)
    return rx.text(text, **style)

def animated_heading(text: str, level: int = 1, animation: str = "fade-in-up", **props) -> rx.Component:
    """Heading with entrance animation"""
    map_anim = {
        "fade-in": "animate-fade-in",
        "fade-in-up": "animate-fade-in-up",
        "slide-up": "animate-slide-up"
    }
    return heading(text, level=level, class_name=map_anim.get(animation, "animate-fade-in-up"), **props)

def text(content: str, size: str = "body", **props) -> rx.Component:
    """Standardized Text Component"""
    map_size = {
        "body": Typography.BODY,
        "body_large": Typography.BODY_LARGE,
        "body_secondary": Typography.BODY_SECONDARY,
        "small": Typography.SMALL,
        "caption": Typography.CAPTION,
        "label": Typography.LABEL,
        "label_large": Typography.LABEL_LARGE,
        "display": Typography.DISPLAY,
    }
    style = map_size.get(size, Typography.BODY).copy()
    style.update(props)
    return rx.text(content, **style)

# --- Containers & Cards ---

def card(*children, **props) -> rx.Component:
    """Premium Glass/Surface Card"""
    style = CARD_STYLE.copy()
    style.update(props)
    return rx.box(*children, **style)

def empty_state(icon: str, title: str, description: str, action_label: str = "", on_action=None) -> rx.Component:
    """Clean Empty State Placeholder"""
    return card(
        rx.vstack(
            rx.icon(tag=icon, size=48, color=Color.TEXT_SECONDARY),
            heading(title, level=3, color=Color.DEEP),
            text(description, size="body_secondary", text_align="center", max_width="400px"),
            rx.cond(action_label != "", button(action_label, on_click=on_action)),
            padding=Spacing.XXL, align_items="center", gap=Spacing.LG
        ),
        text_align="center"
    )

# --- Actions & Inputs ---

def button(label: str, icon: str = None, variant: str = "primary", size: str = "default", is_loading: bool = False, **props) -> rx.Component:
    """Unified Vibe Button"""
    # Variants configuration
    variants = {
        "primary": BUTTON_PRIMARY_STYLE,
        "secondary": BUTTON_SECONDARY_STYLE,
        "ghost": {
            "bg": "transparent",
            "color": Color.DEEP,
            "padding_x": "0.75rem",
            "border": "1px solid transparent",
            "_hover": {"bg": Color.PRIMARY_LIGHT, "color": Color.DEEP, "border_color": Color.PRIMARY}
        },
        "danger": {
            "bg": Color.ERROR_BG, "color": Color.ERROR, "border": f"1px solid {Color.ERROR}40",
            "_hover": {"bg": Color.ERROR, "color": Color.WHITE, "border_color": Color.ERROR}
        }
    }

    # Select Base Style
    base_style = variants.get(variant, BUTTON_PRIMARY_STYLE).copy()

    # Apply Size Overrides
    if size == "large" and variant == "primary":
        base_style.update(BUTTON_XL_STYLE)

    style = base_style
    user_disabled = props.pop("disabled", False)
    style.update(props)

    # Internal Loading State
    content = rx.cond(
        is_loading,
        rx.hstack(rx.spinner(size="1"), rx.text("Carregando..."), align="center", gap=Spacing.SM),
        rx.hstack(
            rx.cond(icon is not None, rx.icon(tag=icon, size=18)),
            rx.text(label),
            align="center", gap=Spacing.SM
        )
    )

    return rx.button(content, disabled=is_loading | user_disabled, **style)

def input(placeholder: str = "", size: str = "default", **props) -> rx.Component:
    """Standard Input"""
    style = INPUT_STYLE.copy()
    if size == "large":
        style = INPUT_XL_STYLE.copy()

    style["placeholder"] = placeholder
    style.update(props)
    return rx.input(**style)

def select(items: list, placeholder: str = "Selecione...", **props) -> rx.Component:
    """Standard Select"""
    style = INPUT_STYLE.copy() # Reuse Input style base
    style.update(props)
    return rx.select(items, placeholder=placeholder, **style)

def form_field(label: str, control: rx.Component, required: bool = False, error: str = "") -> rx.Component:
    """Label + Control + Error Message Wrapper"""
    return rx.vstack(
        rx.hstack(
            rx.text(label, **Typography.LABEL),
            rx.cond(required, rx.text("*", color=Color.ERROR, font_size=Typography.H5["font_size"])),
            gap=Spacing.XS
        ),
        control,
        rx.cond(error != "", rx.text(error, color=Color.ERROR, font_size=Typography.SIZE_SM_XS)),
        width="100%", gap=Spacing.XS, align_items="start"
    )

# --- Data Display ---

def status_badge(text: str, status: str = "default") -> rx.Component:
    """Semantic Status Badge"""
    config = {
        "success": (Color.SUCCESS, Color.SUCCESS_BG, "circle-check"),
        "warning": (Color.WARNING, Color.WARNING_BG, "triangle-alert"),
        "error": (Color.ERROR, Color.ERROR_BG, "circle-x"),
        "info": (Color.PRIMARY, Color.PRIMARY_LIGHT, "info"),
        "neutral": (Color.TEXT_SECONDARY, Color.BACKGROUND, "circle-help"),
    }
    color, bg, icon = config.get(status, config["neutral"])

    return rx.badge(
        rx.hstack(rx.icon(tag=icon, size=14), rx.text(text), gap=Spacing.XS, align_items="center"),
        bg=bg, color=color, variant="soft", radius="full", padding_x=Spacing.MD, padding_y=Spacing.XXS
    )

def stat_card(title: str, value: str, icon: str, trend: str = "neutral", subtext: str = "") -> rx.Component:
    """Dashboard Statistic Card"""
    return card(
        rx.vstack(
            rx.hstack(
                rx.box(
                    rx.icon(tag=icon, size=20, color=Color.PRIMARY),
                    padding=Spacing.SM_MD, border_radius=Design.RADIUS_MD, bg=Color.PRIMARY_LIGHT,
                ),
                rx.spacer(),
                rx.cond(subtext != "", status_badge(subtext, status=trend)),
                width="100%", align_items="center"
            ),
            rx.vstack(
                rx.text(value, font_size=Typography.H2["font_size"], font_weight="700", color=Color.DEEP, line_height="1.2"),
                rx.text(title, style=Typography.CAPTION, color=Color.TEXT_SECONDARY),
                gap=Spacing.XXS, align_items="start"
            ),
            gap=Spacing.MD
        )
    )

def toast(message: str, status: str = "info") -> rx.Component:
    """Floating Toast Notification"""
    colors = {
        "success": (Color.SUCCESS, Color.SUCCESS_BG, "circle-check"),
        "error": (Color.ERROR, Color.ERROR_BG, "circle-x"),
        "info": (Color.PRIMARY, Color.PRIMARY_LIGHT, "info"),
    }
    color, bg, icon = colors.get(status, colors["info"])

    return rx.box(
        rx.hstack(
            rx.icon(tag=icon, size=20, color=color),
            rx.text(message, style=Typography.LABEL, color=Color.DEEP),
            align_items="center", gap=Spacing.MD
        ),
        bg=bg, border=f"1px solid {color}40", border_radius=Design.RADIUS_LG,
        padding=Spacing.MD, box_shadow=Design.SHADOW_MD,
        position="fixed", bottom="2rem", right="2rem", z_index=Design.Z_INDEX_TOAST
    )

def loading_spinner(text: str = "Carregando...") -> rx.Component:
    """Full width loading state"""
    return rx.center(
        rx.vstack(
            rx.spinner(size="3", color=Color.PRIMARY),
            rx.text(text, color=Color.TEXT_SECONDARY),
            gap=Spacing.SM_MD, align_items="center"
        ),
        width="100%", padding=Spacing.XL
    )

def text_area(placeholder: str = "", **props) -> rx.Component:
    """Standard TextArea"""
    style = INPUT_STYLE.copy()
    style.update({
        "min_height": "100px",
        "resize": "vertical",
        "padding": Spacing.MD
    })
    style["placeholder"] = placeholder
    style.update(props)
    return rx.text_area(**style)

def segmented_control(items: list[dict], value: str, on_change) -> rx.Component:
    """Standard Segmented Control"""
    return rx.segmented_control.root(
        *[rx.segmented_control.item(item["label"], value=item["value"]) for item in items],
        value=value,
        on_change=on_change,
        variant="surface",
        size="2",
        radius="large",
        width="100%",
    )
