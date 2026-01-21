import reflex as rx
from ..styles import Color, Design, Typography, Animation, Spacing

"""
Biblioteca de Componentes Centralizada - Biodiagnóstico 2.0 (PURIFICADA)
Versão 2.1 - Protocolo Aspirador ativado.
"""

def heading(text: str, level: int = 1, color: str = None, **props) -> rx.Component:
    """Cabeçalho padronizado (H1-H5) usando tokens oficiais"""
    styles = {
        1: Typography.H1,
        2: Typography.H2,
        3: Typography.H3,
        4: Typography.H4,
        5: Typography.H5,
    }
    style = styles.get(level, Typography.H1).copy()
    if color:
        style["color"] = color
    style.update(props)
    return rx.text(text, **style)

def animated_heading(text: str, level: int = 1, color: str = None, animation: str = "fade-in-up", **props) -> rx.Component:
    """Cabeçalho com animação integrada do Design System"""
    anim_classes = {
        "fade-in": "animate-fade-in",
        "fade-in-up": "animate-fade-in-up",
        "slide-up": "animate-slide-up",
        "pulse": "animate-pulse-subtle",
    }
    class_name = anim_classes.get(animation, "animate-fade-in-up")
    return heading(text, level=level, color=color, class_name=class_name, **props)

def text(content: str, size: str = "body", **props) -> rx.Component:
    """Texto padronizado usando o Design System"""
    sizes = {
        "body": Typography.BODY,
        "body_large": Typography.BODY_LARGE,
        "body_secondary": Typography.BODY_SECONDARY,
        "small": Typography.SMALL,
        "caption": Typography.CAPTION,
        "label": Typography.LABEL,
        "label_large": Typography.LABEL_LARGE,
    }
    style = sizes.get(size, Typography.BODY).copy()
    style.update(props)
    return rx.text(content, **style)

def card(*children, **props) -> rx.Component:
    """Container card premium com sombras e bordas do design system"""
    from ..styles import CARD_STYLE
    base_style = CARD_STYLE.copy()
    # Adicionando interatividade premium da Skill de UI
    base_style.update({
        "transition": "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
        "_hover": {
            "box_shadow": Design.SHADOW_MD, 
            "transform": "translateY(-4px)",
            "border_color": Color.PRIMARY
        }
    })
    base_style.update(props)
    return rx.box(*children, **base_style)

def button(
    label: str,
    icon: str = None,
    variant: str = "primary",  
    on_click = None,
    is_loading: bool = False,
    loading_text: str = "Carregando...",
    **props
) -> rx.Component:
    """Botão unificado com variantes purificadas"""
    from ..styles import BUTTON_PRIMARY_STYLE, BUTTON_SECONDARY_STYLE

    variants = {
        "primary": {**BUTTON_PRIMARY_STYLE},
        "secondary": {**BUTTON_SECONDARY_STYLE},
        "ghost": {
            "bg": "transparent",
            "color": Color.TEXT_SECONDARY,
            "padding_x": "0.75rem",
            "_hover": {"bg": Color.PRIMARY_LIGHT, "color": Color.DEEP},
        },
        "danger": {
            "bg": Color.ERROR_BG,
            "color": Color.ERROR,
            "border": f"1px solid {Color.ERROR}40",
            "_hover": {"bg": Color.ERROR, "color": "white", "border_color": Color.ERROR},
        }
    }
    
    current_variant = variants.get(variant, variants["primary"])
    
    user_disabled = props.pop("disabled", False)
    should_disable = is_loading | user_disabled

    final_style = current_variant.copy()
    final_style.update(props)

    return rx.button(
        rx.cond(
            is_loading,
            rx.hstack(
                rx.spinner(size="1"),
                rx.text(loading_text),
                align="center",
                style={"gap": "8px"}
            ),
            rx.hstack(
                rx.cond(icon != None, rx.icon(tag=icon, size=18)),
                rx.text(label),
                align="center",
                style={"gap": "8px"}
            )
        ),
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
            style={"gap": "4px"},
        ),
        control,
        rx.cond(
            error != "",
            rx.text(error, color=Color.ERROR, font_size="0.75rem"),
        ),
        style={"gap": "4px"},
        width="100%",
        align_items="start",
    )

def input(placeholder: str = "", **props) -> rx.Component:
    """Input text padronizado com estilos acessíveis (min 44px)"""
    from ..styles import INPUT_STYLE
    base_style = INPUT_STYLE.copy()
    base_style["placeholder"] = placeholder
    base_style.update(props)
    return rx.input(**base_style)

def select(items, placeholder: str = "Selecione...", value=None, on_change=None, **props) -> rx.Component:
    """Select padronizado com estilos acessíveis (min 44px)"""
    base_style = {
        "border": f"1px solid {Color.BORDER}",
        "border_radius": Design.RADIUS_LG,
        "min_height": "44px",
        "bg": Color.SURFACE,
        "padding": f"{Spacing.SM} {Spacing.MD}",
        "width": "100%",
        "color": Color.TEXT_PRIMARY,
        "font_size": "1rem",
        "transition": "all 0.2s ease-in-out",
        "_hover": {"border_color": Color.PRIMARY},
        "_focus": {"border_color": Color.PRIMARY, "box_shadow": f"0 0 0 2px {Color.PRIMARY}20"},
    }
    base_style.update(props)
    return rx.select(items, placeholder=placeholder, value=value, on_change=on_change, **base_style)

def text_area(placeholder: str = "", **props) -> rx.Component:
    """TextArea padronizado com estilos consistentes"""
    from ..styles import INPUT_STYLE
    base_style = INPUT_STYLE.copy()
    base_style.update({
        "min_height": "100px",
        "padding": Spacing.MD,
        "resize": "vertical"
    })
    base_style["placeholder"] = placeholder
    base_style.update(props)
    return rx.text_area(**base_style)

def status_badge(text: str, status: str = "default") -> rx.Component:
    """Badge de status (success, error, warning, info) usando Design System"""
    colors = {
        "success": {"bg": Color.SUCCESS_BG, "color": Color.SUCCESS},
        "error": {"bg": Color.ERROR_BG, "color": Color.ERROR},
        "warning": {"bg": Color.WARNING_BG, "color": Color.WARNING},
        "info": {"bg": Color.PRIMARY_LIGHT, "color": Color.PRIMARY},
        "primary": {"bg": Color.PRIMARY_LIGHT, "color": Color.PRIMARY},
        "default": {"bg": Color.BACKGROUND, "color": Color.TEXT_SECONDARY},
    }
    style = colors.get(status, colors["default"])
    return rx.badge(
        text,
        bg=style["bg"],
        color=style["color"],
        variant="soft",
        radius="full",
        padding_x=Spacing.MD,
        padding_y="2px",
    )

def stat_card(title: str, value: str, icon: str, trend: str = "neutral", subtext: str = "") -> rx.Component:
    """Card de estatística premium para dashboards"""
    return card(
        rx.vstack(
            rx.hstack(
                rx.box(
                    rx.icon(tag=icon, size=24, color=Color.PRIMARY),
                    padding="12px",
                    border_radius="12px",
                    bg=Color.PRIMARY_LIGHT,
                    display="flex", align_items="center", justify_content="center"
                ),
                rx.spacer(),
                rx.cond(subtext != "", status_badge(subtext, status=trend)),
                width="100%",
                align_items="center",
            ),
            rx.vstack(
                rx.text(value, font_size="2rem", font_weight="800", color=Color.DEEP, line_height="1.1"),
                rx.text(title, style=Typography.SMALL, color=Color.TEXT_SECONDARY, text_transform="uppercase"),
                align_items="start",
                style={"gap": "2px"},
            ),
            style={"gap": Spacing.LG},
        ),
    )

def data_table(headers: list[str], rows: list[list], striped: bool = True, **props) -> rx.Component:
    """Tabela de dados profissional purificada"""
    return card(
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    *[rx.table.column_header_cell(
                        rx.text(header, color=Color.DEEP, font_weight="700", font_size="0.875rem"),
                        padding=Spacing.MD, bg=Color.PRIMARY_LIGHT
                    ) for header in headers]
                )
            ),
            rx.table.body(
                *[rx.table.row(
                    *[rx.table.cell(str(cell), padding=Spacing.MD) for cell in row],
                    bg=rx.cond(striped & (i % 2 == 1), Color.BACKGROUND, Color.SURFACE),
                    _hover={"bg": Color.PRIMARY_LIGHT} if props.get("hover", True) else {}
                ) for i, row in enumerate(rows)]
            ),
            width="100%",
            variant="surface",
        ),
        padding="0",
        overflow="hidden",
        **props
    )

def toast(message: str, status: str = "info") -> rx.Component:
    """Notificação toast (Aspirada: Removido hexadecimais)"""
    config = {
        "success": {"bg": Color.SUCCESS_BG, "color": Color.SUCCESS, "icon": "check-circle"},
        "error": {"bg": Color.ERROR_BG, "color": Color.ERROR, "icon": "circle-x"},
        "warning": {"bg": Color.WARNING_BG, "color": Color.WARNING, "icon": "triangle-alert"},
        "info": {"bg": Color.PRIMARY_LIGHT, "color": Color.PRIMARY, "icon": "info"},
    }.get(status, {"bg": Color.PRIMARY_LIGHT, "color": Color.PRIMARY, "icon": "info"})

    return rx.box(
        rx.hstack(
            rx.icon(tag=config["icon"], size=20, color=config["color"]),
            rx.text(message, style=Typography.LABEL, color=Color.DEEP),
            align_items="center",
            style={"gap": Spacing.MD},
        ),
        bg=config["bg"],
        border=f"1px solid {config['color']}40",
        border_radius=Design.RADIUS_LG,
        padding=Spacing.MD,
        box_shadow=Design.SHADOW_MD,
        position="fixed", bottom="2rem", right="2rem", z_index="9999",
    )

def loading_spinner(text: str = "") -> rx.Component:
    """Spinner padronizado"""
    return rx.vstack(
        rx.spinner(size="3", color=Color.PRIMARY),
        rx.cond(text != "", rx.text(text, style=Typography.BODY_SECONDARY)),
        align_items="center",
        justify_content="center",
        style={"gap": Spacing.MD},
    )

def empty_state(icon: str, title: str, description: str, action_label: str = "", on_action=None) -> rx.Component:
    """Estado vazio purificado"""
    return card(
        rx.vstack(
            rx.box(
                rx.icon(tag=icon, size=48, color=Color.TEXT_SECONDARY),
                padding=Spacing.XL, border_radius="full", bg=Color.BACKGROUND,
            ),
            heading(title, level=3, color=Color.DEEP),
            text(description, size="body_secondary", text_align="center", max_width="400px"),
            rx.cond(action_label != "", button(action_label, on_click=on_action)),
            padding=Spacing.XXL,
            align_items="center",
            style={"gap": Spacing.LG},
        ),
        text_align="center",
    )

def segmented_control(items: list[dict], value: str, on_change) -> rx.Component:
    """Controle segmentado padronizado (Alternativa melhor ao tabs)"""
    return rx.segmented_control.root(
        *[rx.segmented_control.item(item["label"], value=item["value"]) for item in items],
        value=value,
        on_change=on_change,
        variant="surface",
        size="2",
        radius="large",
        width="100%",
    )
