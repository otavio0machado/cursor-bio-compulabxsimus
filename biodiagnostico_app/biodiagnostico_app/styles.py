import reflex as rx

# =============================================================================
# GLOBAL VIBE CODING - DESIGN SYSTEM (THE ARCHITECT APPROVED)
# =============================================================================
# Principles:
# 1. Aesthetics First: Modern Fintech/Health Vibe (Emerald/Teal + Glass)
# 2. KISS: Flatter structures, less nested dictionaries
# 3. YAGNI: Only what we use. No "Future Proofing".
# =============================================================================

class Color:
    # --- Primary Brand (Verde Floresta - Logo Biodiagnóstico) ---
    PRIMARY = "#166534"          # Verde escuro (logo)
    PRIMARY_HOVER = "#14532D"
    PRIMARY_LIGHT = "#DCFCE7"
    SECONDARY = "#22C55E"        # Verde vibrante (frasco da logo)
    ACCENT = "#15803D"           # Verde médio
    ACCENT_LIGHT = "#F0FDF4"

    # --- Deep & Contrast (Text & Headers) ---
    DEEP = "#052E16"

    # --- Neutrals (Clean Slate) ---
    BACKGROUND = "#F7F4EE"
    SURFACE = "#FFFFFF"
    SURFACE_ALT = "#F2EFE9"
    TEXT_PRIMARY = "#14532D"
    TEXT_SECONDARY = "#5F6F68"
    BORDER = "#D1E5D8"

    # --- Status (Semantic) ---
    ERROR = "#EF4444"
    ERROR_BG = "#FEF2F2"
    SUCCESS = "#10B981"
    SUCCESS_BG = "#E7FBF4"
    WARNING = "#F59E0B"
    WARNING_BG = "#FFF7ED"

    # --- Vibe Gradients ---
    GRADIENT_PRIMARY = "linear-gradient(135deg, #166534 0%, #14532D 100%)"
    GRADIENT_SURFACE = "linear-gradient(160deg, rgba(255,255,255,0.96) 0%, rgba(242,239,233,0.9) 100%)"
    GRADIENT_GLASS = "linear-gradient(180deg, rgba(255,255,255,0.85) 0%, rgba(255,255,255,0.65) 100%)"

class Design:
    # --- Radius (Curvier = Friendlier) ---
    RADIUS_MD = "12px"
    RADIUS_LG = "18px"
    RADIUS_XL = "26px"
    RADIUS_XXL = "32px"
    
    # --- Shadows (Soft & floating) ---
    SHADOW_SM = "0 2px 8px rgba(10, 20, 16, 0.06)"
    SHADOW_DEFAULT = "0 10px 24px -18px rgba(10, 20, 16, 0.35)"
    SHADOW_MD = "0 18px 32px -22px rgba(10, 20, 16, 0.4)"
    SHADOW_LG = "0 28px 50px -26px rgba(10, 20, 16, 0.45)"

class Typography:
    # --- Headings ---
    H1 = {"font_size": "2.7rem", "font_weight": "700", "line_height": "1.1", "color": Color.DEEP, "font_family": "var(--font-display)"}
    H2 = {"font_size": "2.1rem", "font_weight": "700", "line_height": "1.2", "color": Color.DEEP, "font_family": "var(--font-display)"}
    H3 = {"font_size": "1.55rem", "font_weight": "600", "line_height": "1.3", "color": Color.DEEP, "font_family": "var(--font-display)"}
    H4 = {"font_size": "1.2rem", "font_weight": "600", "color": Color.TEXT_PRIMARY, "font_family": "var(--font-display)"}
    H5 = {"font_size": "1rem", "font_weight": "600", "color": Color.TEXT_PRIMARY, "font_family": "var(--font-display)"}
    
    # --- Body ---
    BODY = {"font_size": "1rem", "font_weight": "400", "line_height": "1.6", "color": Color.TEXT_PRIMARY, "font_family": "var(--font-body)"}
    BODY_LARGE = {"font_size": "1.1rem", "font_weight": "400", "color": Color.TEXT_PRIMARY, "font_family": "var(--font-body)"}
    BODY_SECONDARY = {"font_size": "1rem", "color": Color.TEXT_SECONDARY, "font_family": "var(--font-body)"}
    SMALL = {"font_size": "0.875rem", "color": Color.TEXT_SECONDARY, "font_family": "var(--font-body)"}
    CAPTION = {"font_size": "0.75rem", "color": Color.TEXT_SECONDARY, "font_family": "var(--font-body)"}
    
    # --- UI Elements ---
    LABEL = {"font_size": "0.875rem", "font_weight": "500", "color": Color.TEXT_PRIMARY, "margin_bottom": "4px", "font_family": "var(--font-body)"}
    LABEL_LARGE = {"font_size": "1rem", "font_weight": "500", "color": Color.TEXT_PRIMARY, "font_family": "var(--font-body)"}

class Spacing:
    # --- Consistent Rhythm (4px base) ---
    XS = "4px"
    SM = "8px"
    MD = "16px"
    LG = "24px"
    XL = "32px"
    XXL = "48px"

class Animation:
    FADE_IN_UP = {
        "0%": {"opacity": "0", "transform": "translateY(20px)"},
        "100%": {"opacity": "1", "transform": "translateY(0)"},
    }

# =============================================================================
# TYPOGRAPHY (KISS: Default to Reflex Text props, define only specifics)
# =============================================================================
# We use standard Reflex rx.text(size="...") but provide helpers here if needed.
# For now, we trust the defaults + font variables.

# =============================================================================
# ANIMATIONS (Vibe Motion)
# =============================================================================
STYLES = {
    "font_family": "var(--font-body)",
    "background_color": Color.BACKGROUND,
    
    # Keyframes
    "@keyframes fadeIn": {
        "from": {"opacity": "0"},
        "to": {"opacity": "1"},
    },
    "@keyframes slideUp": {
        "from": {"opacity": "0", "transform": "translateY(10px)"},
        "to": {"opacity": "1", "transform": "translateY(0)"},
    },
    
    # Global Classes
    ".animate-fade-in": {"animation": "fadeIn 0.4s ease-out"},
    ".animate-slide-up": {"animation": "slideUp 0.5s cubic-bezier(0.2, 0.8, 0.2, 1)"},
}

# =============================================================================
# COMPONENT STYLES (Refactored for Reusability)
# =============================================================================

# --- Input Fields ---
INPUT_STYLE = {
    "border": f"1px solid {Color.BORDER}",
    "border_radius": Design.RADIUS_LG,
    "padding": f"{Spacing.SM} {Spacing.MD}",
    "min_height": "48px", # Touch target accessible
    "bg": Color.SURFACE,
    "color": Color.TEXT_PRIMARY,
    "placeholder_color": Color.TEXT_SECONDARY,
    "transition": "all 0.2s cubic-bezier(0.4, 0, 0.2, 1)",
    "_focus": {
        "border_color": Color.PRIMARY,
        "box_shadow": "0 0 0 4px rgba(22, 101, 52, 0.18)",
        "outline": "none"
    },
    "_hover": {"border_color": Color.PRIMARY}
}

# --- Large Input (Matching Button XL) ---
INPUT_XL_STYLE = {
    "border": f"1px solid {Color.BORDER}",
    "border_radius": Design.RADIUS_LG,
    "padding": f"{Spacing.MD} {Spacing.XL}", # More breathing room
    "height": "56px", # Matching Button XL
    "width": "100%",  # Explicit Full Width
    "bg": Color.SURFACE,
    "color": Color.TEXT_PRIMARY,
    "placeholder_color": Color.TEXT_SECONDARY,
    "font_size": "1rem",
    "transition": "all 0.2s cubic-bezier(0.4, 0, 0.2, 1)",
    "_focus": {
        "border_color": Color.PRIMARY,
        "box_shadow": "0 0 0 4px rgba(22, 101, 52, 0.18)",
        "outline": "none"
    },
    "_hover": {"border_color": Color.PRIMARY}
}

# --- Primary Button ---
BUTTON_PRIMARY_STYLE = {
    "bg": Color.GRADIENT_PRIMARY,
    "color": "white",
    "border": f"1px solid {Color.PRIMARY_HOVER}",
    "padding_x": Spacing.LG,
    "min_height": "48px",
    "border_radius": Design.RADIUS_LG,
    "font_weight": "600",
    "letter_spacing": "0.01em",
    "transition": "all 0.2s cubic-bezier(0.4, 0, 0.2, 1)",
    "box_shadow": Design.SHADOW_DEFAULT,
    "_hover": {
        "bg": "linear-gradient(135deg, rgba(22, 101, 52, 0.95) 0%, rgba(20, 83, 45, 0.95) 100%)",
        "transform": "translateY(-2px)",
        "box_shadow": Design.SHADOW_MD,
    },
    "_active": {
        "transform": "scale(0.98)",
        "box_shadow": "none",
    }
}

# --- Large/XL Button (Impact) ---
BUTTON_XL_STYLE = {
    "bg": Color.GRADIENT_PRIMARY,
    "color": "white",
    "border": f"1px solid {Color.PRIMARY_HOVER}",
    "padding_x": Spacing.XL,
    "height": "56px", # Taller for impact
    "width": "100%",  # Usually full width
    "border_radius": Design.RADIUS_LG,
    "font_weight": "700", # Bolder
    "font_size": "1.125rem", # Larger Frame
    "transition": "all 0.2s cubic-bezier(0.4, 0, 0.2, 1)",
    "box_shadow": Design.SHADOW_MD,
    "_hover": {
        "bg": "linear-gradient(135deg, rgba(22, 101, 52, 0.95) 0%, rgba(20, 83, 45, 0.95) 100%)",
        "transform": "translateY(-2px)",
        "box_shadow": Design.SHADOW_LG,
    },
    "_active": {
        "transform": "scale(0.99)",
        "box_shadow": "none",
    }
}

# --- Glass Card ( The Crown Jewel) ---
CARD_STYLE = {
    "bg": Color.GRADIENT_SURFACE,
    "border": f"1px solid {Color.BORDER}",
    "border_radius": Design.RADIUS_XL,
    "padding": Spacing.LG,
    "box_shadow": Design.SHADOW_DEFAULT,
    "transition": "all 0.3s ease",
    "_hover": {
        "box_shadow": Design.SHADOW_MD,
        "border_color": Color.PRIMARY_LIGHT, # Subtle glow
    }
}

# Botão Secundário / Outline
BUTTON_SECONDARY_STYLE = {
    "bg": Color.SURFACE,
    "color": Color.DEEP,
    "border": f"1px solid {Color.BORDER}",
    "padding_y": Spacing.SM,
    "padding_x": Spacing.LG,
    "min_height": "48px",
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
    "_active": { "transform": "translateY(0)" },
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
    "background_color": "rgba(255, 255, 255, 0.75)",
    "backdrop_filter": "blur(14px) saturate(170%)",
    "-webkit-backdrop-filter": "blur(14px) saturate(170%)",
    "border": "1px solid rgba(255, 255, 255, 0.35)",
}

# Estilo para Tabelas
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
    "padding": f"{Spacing.MD} {Spacing.MD}",
    "text_align": "left",
    "border_bottom": f"2px solid {Color.PRIMARY}",
}

TABLE_CELL_STYLE = {
    "padding": f"{Spacing.SM} {Spacing.MD}",  
    "border_bottom": f"1px solid {Color.BORDER}",
    "color": Color.TEXT_PRIMARY,
    "font_size": "0.875rem",
}

TABLE_ROW_STYLE = {
    "transition": "background-color 0.15s ease",
    "_hover": {"bg": Color.PRIMARY_LIGHT + "40"}
}

TABLE_ROW_EVEN_STYLE = {
    "bg": Color.SURFACE_ALT,
}
