import reflex as rx
from ..styles import Color, Design, Typography, Animation, Spacing

"""
Biblioteca de Componentes Centralizada - Biodiagnóstico 2.0
Use estes componentes para garantir consistência visual em toda a aplicação.

Inclui:
- Tipografia responsiva com hierarquia clara
- Componentes de formulário acessíveis (mínimo 44px de altura)
- Sistema de espaçamento consistente
- Tabelas modernas com alternância de cores
- Sistema de notificações toast
- Estados vazios e spinners de carregamento
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
    """
    Texto de corpo padronizado com múltiplas opções de tamanho

    Args:
        content: Conteúdo do texto
        size: Tamanho do texto (body, body_large, body_secondary, small, caption, label, label_large)
        color: Cor personalizada (opcional)
    """
    styles = {
        "body": Typography.BODY,
        "body_large": Typography.BODY_LARGE,
        "body_secondary": Typography.BODY_SECONDARY,
        "small": Typography.SMALL,
        "caption": Typography.CAPTION,
        "label": Typography.LABEL,
        "label_large": Typography.LABEL_LARGE,
    }
    style = styles.get(size, Typography.BODY).copy()
    if color:
        style["color"] = color

    style.update(props)
    return rx.text(content, **style)

def card(*children, **props) -> rx.Component:
    """Container card padrão com sombra e bordas arredondadas"""
    from ..styles import CARD_STYLE

    base_style = CARD_STYLE.copy()
    base_style["_hover"] = {"box_shadow": Design.SHADOW_MD, "transform": "translateY(-2px)"}

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
    from ..styles import BUTTON_PRIMARY_STYLE, BUTTON_SECONDARY_STYLE

    # Base styles with display and gap
    base_style = {
        "display": "flex",
        "align_items": "center",
        "justify_content": "center",
        "gap": "0.5rem",
    }

    # Variant styles using new style constants
    variants = {
        "primary": {**BUTTON_PRIMARY_STYLE},
        "secondary": {**BUTTON_SECONDARY_STYLE},
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
    """Input text padronizado com estilos acessíveis (min 44px)"""
    from ..styles import INPUT_STYLE

    base_style = INPUT_STYLE.copy()
    base_style["placeholder"] = placeholder
    base_style.update(props)

    return rx.input(**base_style)

def select(items, placeholder: str = "Selecione...", value=None, on_change=None, **props) -> rx.Component:
    """Select padronizado com estilos acessíveis (min 44px)"""
    # Estilo base usando os novos padrões
    base_style = {
        "border": f"1px solid {Color.BORDER}",
        "border_radius": Design.RADIUS_LG,
        "min_height": "44px",  # Acessibilidade WCAG
        "bg": Color.SURFACE,
        "padding": f"{Spacing.SM} {Spacing.MD}",  # 12px 16px
        "width": "100%",
        "cursor": "pointer",
        "color": Color.TEXT_PRIMARY,
        "font_size": "1rem",  # 16px - evita zoom no iOS
        "transition": "all 0.2s ease-in-out",
        "_focus": {
            "border_color": Color.PRIMARY,
            "outline": "none",
            "box_shadow": f"0 0 0 3px {Color.PRIMARY}20",
        },
        "_hover": {
            "border_color": Color.SECONDARY,
        },
    }

    # Mesclar props de estilo
    style_props = base_style.copy()
    style_props.update(props)
    
    return rx.select(
        items,
        placeholder=placeholder,
        value=value,
        on_change=on_change,
        **style_props
    )

def text_area(placeholder: str = "", **props) -> rx.Component:
    """TextArea padronizado com estilos acessíveis"""
    base_style = {
        "placeholder": placeholder,
        "border": f"1px solid {Color.BORDER}",
        "border_radius": Design.RADIUS_LG,
        "padding": f"{Spacing.SM} {Spacing.MD}",  # 12px 16px
        "bg": Color.SURFACE,
        "width": "100%",
        "min_height": "100px",
        "color": Color.TEXT_PRIMARY,
        "font_size": "1rem",  # 16px - evita zoom no iOS
        "transition": "all 0.2s ease-in-out",
        "_placeholder": {"color": Color.TEXT_SECONDARY, "opacity": 0.7},
        "_focus": {
            "border_color": Color.PRIMARY,
            "outline": "none",
            "box_shadow": f"0 0 0 3px {Color.PRIMARY}20",
            "transform": "scale(1.01)",
        },
        "_hover": {
            "border_color": Color.SECONDARY,
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

def data_table(
    headers: list[str],
    rows: list[list],
    sortable: bool = False,
    striped: bool = True,
    hover: bool = True,
    **props
) -> rx.Component:
    """
    Tabela de dados profissional com formatação moderna

    Args:
        headers: Lista de cabeçalhos das colunas
        rows: Lista de listas com os dados (cada lista interna é uma linha)
        sortable: Se True, permite ordenação por clique nos cabeçalhos
        striped: Se True, alterna cores das linhas
        hover: Se True, destaca linha ao passar o mouse
    """
    from ..styles import TABLE_STYLE, TABLE_HEADER_STYLE, TABLE_CELL_STYLE, TABLE_ROW_STYLE, TABLE_ROW_EVEN_STYLE, Spacing

    # Cabeçalhos da tabela
    header_row = rx.table.header(
        rx.table.row(
            *[
                rx.table.column_header_cell(
                    rx.hstack(
                        rx.text(header, **{"font_weight": "600"}),
                        rx.cond(
                            sortable,
                            rx.icon("arrow-up-down", size=14, color=Color.TEXT_SECONDARY)
                        ),
                        spacing="2",
                        align="center"
                    ),
                    padding=f"{Spacing.MD} {Spacing.MD}",
                    bg=Color.PRIMARY_LIGHT,
                    color=Color.DEEP,
                    font_weight="600",
                    font_size="0.875rem",
                    text_transform="uppercase",
                    letter_spacing="0.05em",
                )
                for header in headers
            ]
        )
    )

    # Linhas de dados
    def create_row(row_data, index):
        row_bg = rx.cond(
            (striped & (index % 2 == 1)),
            "#F9FAFB",
            Color.SURFACE
        )

        return rx.table.row(
            *[
                rx.table.cell(
                    str(cell),
                    padding=f"{Spacing.SM} {Spacing.MD}",
                    color=Color.TEXT_PRIMARY,
                    font_size="0.875rem",
                )
                for cell in row_data
            ],
            bg=row_bg,
            class_name=rx.cond(hover, "hover:bg-green-50 transition-colors", ""),
        )

    body = rx.table.body(
        *[create_row(row, i) for i, row in enumerate(rows)]
    )

    return card(
        rx.table.root(
            header_row,
            body,
            width="100%",
            variant="surface",
        ),
        padding=Spacing.MD,
        **props
    )

def toast(
    message: str,
    status: str = "info",  # success, error, warning, info
    duration: int = 3000,
    icon: str = None,
) -> rx.Component:
    """
    Notificação toast flutuante

    Args:
        message: Mensagem a ser exibida
        status: Tipo de notificação (success, error, warning, info)
        duration: Duração em milissegundos
        icon: Ícone personalizado (opcional)
    """
    from ..styles import Spacing

    # Mapeamento de status para cores e ícones
    status_config = {
        "success": {"bg": Color.SUCCESS_BG, "color": Color.SUCCESS, "icon": "circle-check"},
        "error": {"bg": Color.ERROR_BG, "color": Color.ERROR, "icon": "circle-x"},
        "warning": {"bg": Color.WARNING_BG, "color": Color.WARNING, "icon": "triangle-alert"},
        "info": {"bg": "#EFF6FF", "color": "#1D4ED8", "icon": "info"},
    }

    config = status_config.get(status, status_config["info"])
    toast_icon = icon or config["icon"]

    return rx.box(
        rx.hstack(
            rx.icon(toast_icon, size=20, color=config["color"]),
            rx.text(
                message,
                font_size="0.875rem",
                font_weight="500",
                color=Color.TEXT_PRIMARY,
            ),
            spacing="3",
            align="center",
        ),
        bg=config["bg"],
        border=f"1px solid {config['color']}40",
        border_radius=Design.RADIUS_LG,
        padding=f"{Spacing.SM} {Spacing.MD}",
        box_shadow=Design.SHADOW_MD,
        class_name="animate-slide-up",
        position="fixed",
        bottom="2rem",
        right="2rem",
        z_index="9999",
        min_width="300px",
        max_width="500px",
    )

def loading_spinner(size: str = "md", text: str = "") -> rx.Component:
    """
    Spinner de carregamento com texto opcional

    Args:
        size: Tamanho do spinner (sm, md, lg)
        text: Texto a ser exibido abaixo do spinner
    """
    size_map = {"sm": "1", "md": "2", "lg": "3"}
    spinner_size = size_map.get(size, "2")

    return rx.vstack(
        rx.spinner(size=spinner_size, color=Color.PRIMARY),
        rx.cond(
            text != "",
            rx.text(
                text,
                font_size="0.875rem",
                color=Color.TEXT_SECONDARY,
                font_weight="500",
            )
        ),
        spacing="3",
        align="center",
        justify="center",
    )

def empty_state(
    icon: str,
    title: str,
    description: str,
    action_label: str = "",
    on_action = None,
) -> rx.Component:
    """
    Estado vazio para quando não há dados a exibir

    Args:
        icon: Ícone a ser exibido
        title: Título do estado vazio
        description: Descrição do que fazer
        action_label: Texto do botão de ação (opcional)
        on_action: Callback para o botão de ação
    """
    from ..styles import Spacing

    return card(
        rx.vstack(
            rx.box(
                rx.icon(icon, size=48, color=Color.TEXT_SECONDARY),
                class_name="p-6 rounded-full bg-gray-50",
            ),
            heading(title, level=3, color=Color.TEXT_PRIMARY),
            text(description, size="body", text_align="center", max_width="400px"),
            rx.cond(
                action_label != "",
                button(
                    action_label,
                    variant="primary",
                    on_click=on_action,
                ),
            ),
            spacing="4",
            align="center",
            justify="center",
            padding=f"{Spacing.XXL} {Spacing.XL}",
        ),
        text_align="center",
    )
