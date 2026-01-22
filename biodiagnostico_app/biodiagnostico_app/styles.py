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
    # --- Primary Brand (Modern Emerald) ---
    PRIMARY = "#10B981"          # Emerald 500 - Vivid, Friendly
    PRIMARY_HOVER = "#059669"    # Emerald 600 - Deep Interaction
    PRIMARY_LIGHT = "#ECFDF5"    # Emerald 50 - Backgrounds, Badges
    
    # --- Deep & Contrast (Text & Headers) ---
    DEEP = "#064E3B"             # Emerald 900 - Almost Black, but richer
    SECONDARY = "#34D399"        # Emerald 400 - Accents
    
    # --- Neutrals (Clean Slate) ---
    BACKGROUND = "#F8FAFC"       # Slate 50 - Cool Gray Background
    SURFACE = "#FFFFFF"          # Pure White
    TEXT_PRIMARY = "#0F172A"     # Slate 900 - Sharper text
    TEXT_SECONDARY = "#64748B"   # Slate 500 - Soft text
    BORDER = "#E2E8F0"           # Slate 200 - Subtle borders
    
    # --- Status (Semantic) ---
    ERROR = "#EF4444"            # Red 500
    ERROR_BG = "#FEF2F2"         # Red 50
    SUCCESS = "#10B981"          # Emerald 500
    SUCCESS_BG = "#ECFDF5"       # Emerald 50
    WARNING = "#F59E0B"          # Amber 500
    WARNING_BG = "#FFFBEB"       # Amber 50

    # --- Vibe Gradients ---
    GRADIENT_PRIMARY = "linear-gradient(135deg, #10B981 0%, #059669 100%)"
    GRADIENT_SURFACE = "radial-gradient(circle at top left, #F8FAFC 0%, #E2E8F0 100%)"
    GRADIENT_GLASS = "linear-gradient(180deg, rgba(255,255,255,0.9) 0%, rgba(255,255,255,0.7) 100%)"

class Design:
    # --- Radius (Curvier = Friendlier) ---
    RADIUS_MD = "10px"
    RADIUS_LG = "16px"
    RADIUS_XL = "24px" 
    
    # --- Shadows (Soft & floating) ---
    SHADOW_SM = "0 1px 2px 0 rgba(0, 0, 0, 0.05)"
    SHADOW_DEFAULT = "0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03)"
    SHADOW_MD = "0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.025)"
    SHADOW_LG = "0 20px 25px -5px rgba(0, 0, 0, 0.05), 0 10px 10px -5px rgba(0, 0, 0, 0.02)"

class Typography:
    # --- Headings ---
    H1 = {"font_size": "2.5rem", "font_weight": "800", "line_height": "1.2", "color": Color.DEEP}
    H2 = {"font_size": "2rem", "font_weight": "700", "line_height": "1.3", "color": Color.DEEP}
    H3 = {"font_size": "1.5rem", "font_weight": "600", "line_height": "1.4", "color": Color.DEEP}
    H4 = {"font_size": "1.25rem", "font_weight": "600", "color": Color.TEXT_PRIMARY}
    H5 = {"font_size": "1rem", "font_weight": "600", "color": Color.TEXT_PRIMARY}
    
    # --- Body ---
    BODY = {"font_size": "1rem", "font_weight": "400", "line_height": "1.6", "color": Color.TEXT_PRIMARY}
    BODY_LARGE = {"font_size": "1.125rem", "font_weight": "400", "color": Color.TEXT_PRIMARY}
    BODY_SECONDARY = {"font_size": "1rem", "color": Color.TEXT_SECONDARY}
    SMALL = {"font_size": "0.875rem", "color": Color.TEXT_SECONDARY}
    CAPTION = {"font_size": "0.75rem", "color": Color.TEXT_SECONDARY}
    
    # --- UI Elements ---
    LABEL = {"font_size": "0.875rem", "font_weight": "500", "color": Color.TEXT_PRIMARY, "margin_bottom": "4px"}
    LABEL_LARGE = {"font_size": "1rem", "font_weight": "500", "color": Color.TEXT_PRIMARY}

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
# For now, we trust the defaults + Inter font.

# =============================================================================
# ANIMATIONS (Vibe Motion)
# =============================================================================
STYLES = {
    "font_family": "'Inter', 'Outfit', sans-serif",
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
    "transition": "all 0.2s cubic-bezier(0.4, 0, 0.2, 1)",
    "_focus": {
        "border_color": Color.PRIMARY,
        "box_shadow": f"0 0 0 4px {Color.PRIMARY_LIGHT}",
        "outline": "none"
    },
    "_hover": {"border_color": Color.SECONDARY}
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
    "font_size": "1rem",
    "transition": "all 0.2s cubic-bezier(0.4, 0, 0.2, 1)",
    "_focus": {
        "border_color": Color.PRIMARY,
        "box_shadow": f"0 0 0 4px {Color.PRIMARY_LIGHT}",
        "outline": "none"
    },
    "_hover": {"border_color": Color.SECONDARY}
}

# --- Primary Button ---
BUTTON_PRIMARY_STYLE = {
    "bg": Color.PRIMARY,
    "color": "white",
    "padding_x": Spacing.LG,
    "min_height": "48px",
    "border_radius": Design.RADIUS_LG,
    "font_weight": "600",
    "transition": "all 0.2s cubic-bezier(0.4, 0, 0.2, 1)",
    "box_shadow": Design.SHADOW_DEFAULT,
    "_hover": {
        "bg": Color.PRIMARY_HOVER,
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
    "bg": Color.PRIMARY,
    "color": "white",
    "padding_x": Spacing.XL,
    "height": "56px", # Taller for impact
    "width": "100%",  # Usually full width
    "border_radius": Design.RADIUS_LG,
    "font_weight": "700", # Bolder
    "font_size": "1.125rem", # Larger Frame
    "transition": "all 0.2s cubic-bezier(0.4, 0, 0.2, 1)",
    "box_shadow": Design.SHADOW_MD,
    "_hover": {
        "bg": Color.PRIMARY_HOVER,
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
    "bg": Color.SURFACE,
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
    "bg": "transparent",
    "color": Color.DEEP,
    "border": f"2px solid {Color.BORDER}",
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
    "background_color": "rgba(255, 255, 255, 0.7)",
    "backdrop_filter": "blur(12px) saturate(180%)",
    "-webkit-backdrop-filter": "blur(12px) saturate(180%)",
    "border": "1px solid rgba(255, 255, 255, 0.3)",
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
    "bg": "#F9FAFB",
}
