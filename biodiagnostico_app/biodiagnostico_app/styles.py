import reflex as rx

# Cores do Sistema Baseadas no Figma - Biodiagnóstico 2.0
class Color:
    # Primary Brand Colors
    PRIMARY = "#4CAF50"      # Verde principal (Botões, Destaques) - Brand Green
    PRIMARY_HOVER = "#43A047" # Verde hover
    PRIMARY_LIGHT = "#E8F5E9" # Verde muito claro (Backgrounds sutis, Badges)
    
    # Deep & Contrast Colors
    DEEP = "#1B5E20"    # Verde Floresta Escuro (Headers, Textos de alto contraste)
    SECONDARY = "#2E7D32" # Verde intermediário
    
    # Supportive Colors
    SUPPORTIVE_LIGHT = "#F1F8E9"
    SUPPORTIVE_MEDIUM = "#A5D6A7"
    
    # Neutrals
    BACKGROUND = "#F8F9FA"   # Fundo geral da aplicação (Clean Slate)
    SURFACE = "#FFFFFF"      # Fundo de cards e containers
    TEXT_PRIMARY = "#111827" # Gray 900 - Quase preto para leitura
    TEXT_SECONDARY = "#4B5563" # Gray 600 - Texto de apoio
    TEXT_LIGHT = "#9CA3AF"     # Gray 400 - Legendas e textos desativados
    BORDER = "#E5E7EB"       # Gray 200 - Bordas sutis
    BACKGROUND_CARD = "#FFFFFF" # Fundo de cards (Alias para SURFACE)
    
    # Status Colors
    ERROR = "#EF4444"        # Vermelho erro
    ERROR_BG = "#FEF2F2"     # Fundo erro
    ERROR_LIGHT = "#FEF2F2"  # Alias para compatibilidade
    SUCCESS = "#10B981"      # Verde sucesso
    SUCCESS_BG = "#ECFDF5"   # Fundo sucesso
    SUCCESS_LIGHT = "#ECFDF5" # Alias para compatibilidade
    WARNING = "#F59E0B"      # Amarelo alerta
    WARNING_BG = "#FFFBEB"   # Fundo alerta
    WARNING_LIGHT = "#FFFBEB" # Alias para compatibilidade

    # Gradients
    GRADIENT_PRIMARY = "linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%)"
    GRADIENT_SURFACE = "linear-gradient(180deg, rgba(255, 255, 255, 0.8) 0%, rgba(255, 255, 255, 0.4) 100%)"
    GRADIENT_SHINE = "linear-gradient(45deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.2) 50%, rgba(255,255,255,0) 100%)"

# Configurações de Design System
class Design:
    RADIUS_MD = "8px"
    RADIUS_LG = "12px"
    RADIUS_XL = "16px"
    
    SHADOW_SM = "0 1px 2px 0 rgba(0, 0, 0, 0.05)"
    SHADOW_DEFAULT = "0 2px 8px -2px rgba(0, 0, 0, 0.05), 0 1px 2px 0 rgba(0, 0, 0, 0.02)"
    SHADOW_MD = "0 8px 24px -4px rgba(0, 0, 0, 0.08), 0 4px 12px -2px rgba(0, 0, 0, 0.04)"
    SHADOW_LG = "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)"

class Typography:
    # Headings - Hierarquia visual clara e responsiva
    H1 = {
        "font_size": ["2rem", "2.25rem", "2.5rem"],  # Mobile: 32px, Tablet: 36px, Desktop: 40px
        "font_weight": "800",
        "line_height": "1.2",
        "letter_spacing": "-0.02em",
        "color": Color.DEEP,
        "margin_bottom": "1rem"
    }
    H2 = {
        "font_size": ["1.5rem", "1.75rem", "2rem"],  # Mobile: 24px, Tablet: 28px, Desktop: 32px
        "font_weight": "700",
        "line_height": "1.3",
        "letter_spacing": "-0.01em",
        "color": Color.DEEP,
        "margin_bottom": "0.875rem"
    }
    H3 = {
        "font_size": ["1.25rem", "1.375rem", "1.5rem"],  # Mobile: 20px, Tablet: 22px, Desktop: 24px
        "font_weight": "600",
        "line_height": "1.4",
        "color": Color.DEEP,
        "margin_bottom": "0.75rem"
    }
    H4 = {
        "font_size": ["1.125rem", "1.25rem"],  # Mobile: 18px, Tablet+: 20px
        "font_weight": "600",
        "line_height": "1.4",
        "color": Color.TEXT_PRIMARY,
        "margin_bottom": "0.625rem"
    }
    H5 = {
        "font_size": "1rem",  # 16px
        "font_weight": "600",
        "line_height": "1.5",
        "color": Color.TEXT_PRIMARY,
        "margin_bottom": "0.5rem"
    }

    # Body text - Mínimo de 16px para legibilidade
    BODY = {
        "font_size": "1rem",  # 16px - tamanho mínimo recomendado
        "font_weight": "400",
        "line_height": "1.6",  # 1.5x+ para conforto de leitura
        "color": Color.TEXT_PRIMARY,  # Texto principal mais escuro
        "margin_bottom": "1rem"  # Espaçamento entre parágrafos
    }
    BODY_LARGE = {
        "font_size": "1.125rem",  # 18px - para destaque
        "font_weight": "400",
        "line_height": "1.7",
        "color": Color.TEXT_PRIMARY,
        "margin_bottom": "1rem"
    }
    BODY_SECONDARY = {
        "font_size": "1rem",  # 16px
        "font_weight": "400",
        "line_height": "1.6",
        "color": Color.TEXT_SECONDARY,
        "margin_bottom": "1rem"
    }
    SMALL = {
        "font_size": "0.875rem",  # 14px - tamanho mínimo para texto secundário
        "font_weight": "400",
        "line_height": "1.5",
        "color": Color.TEXT_SECONDARY,
        "margin_bottom": "0.5rem"
    }
    CAPTION = {
        "font_size": "0.75rem",  # 12px - apenas para legendas e metadados
        "font_weight": "400",
        "line_height": "1.4",
        "color": Color.TEXT_SECONDARY
    }

    # Labels e formulários
    LABEL = {
        "font_size": "0.875rem",  # 14px
        "font_weight": "500",
        "color": Color.TEXT_PRIMARY,
        "margin_bottom": "0.375rem",
        "line_height": "1.4"
    }
    LABEL_LARGE = {
        "font_size": "1rem",  # 16px - para formulários importantes
        "font_weight": "500",
        "color": Color.TEXT_PRIMARY,
        "margin_bottom": "0.5rem",
        "line_height": "1.5"
    }

# Sistema de Espaçamento Consistente (baseado em múltiplos de 4px)
class Spacing:
    # Espaçamentos internos (padding)
    XS = "0.5rem"   # 8px
    SM = "0.75rem"  # 12px
    MD = "1rem"     # 16px
    LG = "1.5rem"   # 24px
    XL = "2rem"     # 32px
    XXL = "3rem"    # 48px
    XXXL = "4rem"   # 64px

    # Espaçamentos entre seções
    SECTION_SM = "1.5rem"   # 24px
    SECTION_MD = "2rem"     # 32px
    SECTION_LG = "3rem"     # 48px
    SECTION_XL = "4rem"     # 64px

    # Espaçamentos entre componentes
    COMPONENT_XS = "0.5rem"   # 8px
    COMPONENT_SM = "0.75rem"  # 12px
    COMPONENT_MD = "1rem"     # 16px
    COMPONENT_LG = "1.5rem"   # 24px

class Animation:
    FADE_IN_UP = {
        "0%": {"opacity": "0", "transform": "translateY(20px)"},
        "100%": {"opacity": "1", "transform": "translateY(0)"},
    }

# Configurações de Estilo Global
STYLES = {
    "font_family": "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
    "background_color": Color.BACKGROUND,
    "@keyframes fadeInUp": {
        "0%": {"opacity": "0", "transform": "translateY(20px)"},
        "100%": {"opacity": "1", "transform": "translateY(0)"},
    },
    "@keyframes fadeIn": {
        "0%": {"opacity": "0"},
        "100%": {"opacity": "1"},
    },
    ".animate-fade-in": {
        "animation": "fadeIn 0.5s ease-out forwards"
    },
    ".animate-fade-in-up": {
        "animation": "fadeInUp 0.5s ease-out forwards"
    },
    ".animate-slide-up": {
        "animation": "fadeInUp 0.6s ease-out forwards"
    },
    "@keyframes shake": {
        "10%, 90%": {"transform": "translate3d(-1px, 0, 0)"},
        "20%, 80%": {"transform": "translate3d(2px, 0, 0)"},
        "30%, 50%, 70%": {"transform": "translate3d(-4px, 0, 0)"},
        "40%, 60%": {"transform": "translate3d(4px, 0, 0)"},
    },
    ".animate-shake": {
        "animation": "shake 0.82s cubic-bezier(.36,.07,.19,.97) both"
    },
    "@keyframes pulse-subtle": {
        "0%, 100%": {"opacity": "1"},
        "50%": {"opacity": "0.7"},
    },
    ".animate-pulse-subtle": {
        "animation": "pulse-subtle 2s ease-in-out infinite"
    },
    "@keyframes shine": {
        "0%": {"background-position": "-200% 0"},
        "100%": {"background-position": "200% 0"},
    }
}

# Estilos de Componentes Reutilizáveis

# Input Premium - Altura mínima 44px para acessibilidade
INPUT_STYLE = {
    "border": f"1px solid {Color.BORDER}",
    "border_radius": Design.RADIUS_LG,
    "padding": f"{Spacing.SM} {Spacing.MD}",  # 12px 16px
    "width": "100%",
    "color": Color.TEXT_PRIMARY,
    "min_height": "44px",  # Mínimo para acessibilidade (touch target)
    "font_size": "1rem",   # 16px - evita zoom no iOS
    "bg": Color.SURFACE,
    "transition": "all 0.2s ease-in-out",
    "_placeholder": {
        "color": Color.TEXT_SECONDARY,
        "opacity": 0.7
    },
    "_focus": {
        "border_color": f"{Color.TEXT_SECONDARY} !important",
        "outline": "none !important",
        "box_shadow": "none !important",
    },
    "_focus_visible": {
        "border_color": f"{Color.TEXT_SECONDARY} !important",
        "outline": "none !important",
        "box_shadow": "none !important",
    },
    "_hover": {
        "border_color": Color.SECONDARY,
    },
    "_disabled": {
        "opacity": 0.5,
        "cursor": "not-allowed",
        "bg": "#F9FAFB"
    }
}

# Botão Primário Premium - Altura mínima 44px, largura mínima 120px
BUTTON_PRIMARY_STYLE = {
    "background_image": Color.GRADIENT_PRIMARY,
    "color": "white",
    "padding_y": Spacing.SM,    # 12px
    "padding_x": Spacing.LG,    # 24px
    "min_height": "44px",       # Área de toque acessível
    "min_width": "120px",       # Largura mínima para texto legível
    "border_radius": Design.RADIUS_LG,
    "font_weight": "600",
    "font_size": "1rem",        # 16px
    "box_shadow": Design.SHADOW_MD,
    "transition": "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
    "cursor": "pointer",
    "border": "none",
    "position": "relative",
    "overflow": "hidden",
    "_hover": {
        "filter": "brightness(1.1)",
        "box_shadow": Design.SHADOW_LG,
        "transform": "translateY(-2px)",
    },
    "_active": {
        "transform": "translateY(0) scale(0.98)",
        "box_shadow": Design.SHADOW_SM,
    },
    "_focus": {
        "outline": f"2px solid {Color.PRIMARY}",
        "outline_offset": "2px",
    },
    "_disabled": {
        "opacity": 0.5,
        "cursor": "not-allowed",
        "transform": "none",
        "box_shadow": "none",
        "filter": "grayscale(0.5)",
    }
}

# Botão Secundário / Outline
BUTTON_SECONDARY_STYLE = {
    "bg": "transparent",
    "color": Color.DEEP,
    "border": f"2px solid {Color.BORDER}",  # Border mais visível
    "padding_y": Spacing.SM,    # 12px
    "padding_x": Spacing.LG,    # 24px
    "min_height": "44px",
    "min_width": "120px",
    "border_radius": Design.RADIUS_LG,
    "font_weight": "600",
    "font_size": "1rem",
    "cursor": "pointer",
    "transition": "all 0.2s ease",
    "_hover": {
        "bg": Color.PRIMARY_LIGHT,
        "border_color": Color.PRIMARY,
        "transform": "translateY(-1px)",
        "box_shadow": Design.SHADOW_SM,
    },
    "_active": {
        "transform": "translateY(0)",
    },
    "_focus": {
        "outline": f"2px solid {Color.PRIMARY}",
        "outline_offset": "2px",
    },
    "_disabled": {
        "opacity": 0.5,
        "cursor": "not-allowed",
        "transform": "none",
    }
}

# Glassmorphism Style
GLASS_STYLE = {
    "background_color": "rgba(255, 255, 255, 0.7)",
    "backdrop_filter": "blur(12px) saturate(180%)",
    "-webkit-backdrop-filter": "blur(12px) saturate(180%)",
    "border": "1px solid rgba(255, 255, 255, 0.3)",
}

# Card Premium (Floating) - Padding mínimo 20px
CARD_STYLE = {
    "bg": Color.SURFACE,
    "border": f"1px solid {Color.BORDER}",
    "border_radius": Design.RADIUS_XL,
    "padding": Spacing.LG,  # 24px - respiro visual adequado
    "box_shadow": Design.SHADOW_DEFAULT,
    "transition": "all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275)",
    "position": "relative",
    "overflow": "hidden",
}

# Estilo para Tabelas - Alternância de linhas e espaçamento confortável
TABLE_STYLE = {
    "width": "100%",
    "border_collapse": "separate",
    "border_spacing": "0",
    "border": f"1px solid {Color.BORDER}",
    "border_radius": Design.RADIUS_LG,
    "overflow": "hidden",
}

TABLE_HEADER_STYLE = {
    "bg": Color.PRIMARY_LIGHT,
    "color": Color.DEEP,
    "font_weight": "600",
    "font_size": "0.875rem",
    "text_transform": "uppercase",
    "letter_spacing": "0.05em",
    "padding": f"{Spacing.MD} {Spacing.MD}",  # 16px
    "text_align": "left",
    "border_bottom": f"2px solid {Color.PRIMARY}",
}

TABLE_CELL_STYLE = {
    "padding": f"{Spacing.SM} {Spacing.MD}",  # 12px 16px
    "border_bottom": f"1px solid {Color.BORDER}",
    "color": Color.TEXT_PRIMARY,
    "font_size": "0.875rem",
}

TABLE_ROW_STYLE = {
    "transition": "background-color 0.15s ease",
    "_hover": {
        "bg": Color.PRIMARY_LIGHT + "40",  # 25% opacity
    }
}

TABLE_ROW_EVEN_STYLE = {
    "bg": "#F9FAFB",  # Leve alternância de cor
}
