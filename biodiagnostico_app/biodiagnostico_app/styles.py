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
    BORDER = "#E5E7EB"       # Gray 200 - Bordas sutis
    
    # Status Colors
    ERROR = "#EF4444"        # Vermelho erro
    ERROR_BG = "#FEF2F2"     # Fundo erro
    SUCCESS = "#10B981"      # Verde sucesso
    SUCCESS_BG = "#ECFDF5"   # Fundo sucesso
    WARNING = "#F59E0B"      # Amarelo alerta
    WARNING_BG = "#FFFBEB"   # Fundo alerta

# Configurações de Design System
class Design:
    RADIUS_MD = "8px"
    RADIUS_LG = "12px"
    RADIUS_XL = "16px"
    
    SHADOW_SM = "0 1px 2px 0 rgba(0, 0, 0, 0.05)"
    SHADOW_DEFAULT = "0 2px 8px -2px rgba(0, 0, 0, 0.05), 0 1px 2px 0 rgba(0, 0, 0, 0.02)"
    SHADOW_MD = "0 8px 24px -4px rgba(0, 0, 0, 0.08), 0 4px 12px -2px rgba(0, 0, 0, 0.04)"
    SHADOW_MD = "0 8px 24px -4px rgba(0, 0, 0, 0.08), 0 4px 12px -2px rgba(0, 0, 0, 0.04)"
    SHADOW_LG = "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)"

class Typography:
    H1 = {"font_size": ["2rem", "2.25rem"], "font_weight": "800", "line_height": "1.2", "letter_spacing": "-0.02em", "color": Color.DEEP}
    H2 = {"font_size": ["1.5rem", "1.75rem"], "font_weight": "700", "line_height": "1.3", "letter_spacing": "-0.01em", "color": Color.DEEP}
    H3 = {"font_size": "1.25rem", "font_weight": "600", "line_height": "1.4", "color": Color.DEEP}
    H4 = {"font_size": "1.125rem", "font_weight": "600", "line_height": "1.4", "color": Color.TEXT_PRIMARY}
    
    BODY = {"font_size": "1rem", "font_weight": "400", "line_height": "1.6", "color": Color.TEXT_SECONDARY}
    SMALL = {"font_size": "0.875rem", "font_weight": "400", "line_height": "1.5", "color": Color.TEXT_SECONDARY}
    LABEL = {"font_size": "0.875rem", "font_weight": "500", "color": Color.TEXT_PRIMARY, "margin_bottom": "0.375rem"}

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
    }
}

# Estilos de Componentes Reutilizáveis

# Input Premium
INPUT_STYLE = {
    "border": f"1px solid {Color.BORDER}",
    "border_radius": Design.RADIUS_LG,
    "padding": "0.75rem 1rem",
    "width": "100%",
    "color": Color.TEXT_PRIMARY,
    "height": "3rem",
    "bg": Color.SURFACE,
    "transition": "all 0.2s ease-in-out",
    "_placeholder": {"color": Color.TEXT_PRIMARY, "opacity": 1},
    "_focus": {
        "border_color": Color.PRIMARY,
        "box_shadow": f"0 0 0 3px {Color.PRIMARY}20", # 20 hex = ~12% opacity
        "outline": "none",
    },
    "_hover": {
        "border_color": Color.SECONDARY,
    }
}

# Botão Primário Premium
BUTTON_PRIMARY_STYLE = {
    "bg": Color.PRIMARY,
    "color": "white",
    "padding_y": "0.75rem",
    "padding_x": "1.5rem",
    "border_radius": Design.RADIUS_LG,
    "font_weight": "600",
    "box_shadow": Design.SHADOW_MD,
    "transition": "all 0.2s ease",
    "_hover": {
        "bg": Color.PRIMARY_HOVER,
        "box_shadow": Design.SHADOW_LG,
        "transform": "translateY(-1px)",
    },
    "_active": {
        "transform": "translateY(0)",
    }
}

# Botão Secundário / Outline
BUTTON_SECONDARY_STYLE = {
    "bg": "transparent",
    "color": Color.DEEP,
    "border": f"1px solid {Color.BORDER}",
    "padding_y": "0.75rem",
    "padding_x": "1.5rem",
    "border_radius": Design.RADIUS_LG,
    "font_weight": "500",
    "transition": "all 0.2s ease",
    "_hover": {
        "bg": Color.PRIMARY_LIGHT,
        "border_color": Color.PRIMARY,
    }
}

# Card Premium (Floating)
CARD_STYLE = {
    "bg": Color.SURFACE,
    "border": f"1px solid {Color.BORDER}",
    "border_radius": Design.RADIUS_XL,
    "padding": "1.5rem",
    "box_shadow": Design.SHADOW_DEFAULT,
}
