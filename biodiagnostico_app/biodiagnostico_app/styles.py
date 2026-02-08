import reflex as rx

# =============================================================================
# DESIGN SYSTEM - Laboratório Biodiagnóstico
# =============================================================================
# Clean, clinical, light-themed design for medical/laboratory software.
# Primary green from logo + neutral slate palette for professional readability.
# =============================================================================

class Color:
    # --- Primary Brand (Verde Floresta - Logo Biodiagnóstico) ---
    PRIMARY = "#166534"
    PRIMARY_HOVER = "#14532D"
    PRIMARY_LIGHT = "#DCFCE7"
    SECONDARY = "#22C55E"
    ACCENT = "#15803D"
    ACCENT_LIGHT = "#F0FDF4"

    # --- Text & Headers (Neutral Slate - No Green Tint) ---
    DEEP = "#0F172A"

    # --- Neutrals (Clean Clinical Slate) ---
    BACKGROUND = "#F8FAFC"
    SURFACE = "#FFFFFF"
    SURFACE_ALT = "#F1F5F9"
    TEXT_PRIMARY = "#1E293B"
    TEXT_SECONDARY = "#64748B"
    BORDER = "#E2E8F0"
    BORDER_HOVER = "#CBD5E1"
    WHITE = "#FFFFFF"

    # --- Focus ---
    FOCUS_RING = "rgba(22, 101, 52, 0.12)"

    # --- Status (Semantic) ---
    ERROR = "#EF4444"
    ERROR_BG = "#FEF2F2"
    SUCCESS = "#10B981"
    SUCCESS_BG = "#ECFDF5"
    WARNING = "#F59E0B"
    WARNING_BG = "#FFFBEB"

    # --- Gradients ---
    GRADIENT_PRIMARY = "linear-gradient(135deg, #166534 0%, #14532D 100%)"
    GRADIENT_SURFACE = "linear-gradient(160deg, rgba(255,255,255,0.98) 0%, rgba(241,245,249,0.95) 100%)"
    GRADIENT_GLASS = "linear-gradient(180deg, rgba(255,255,255,0.9) 0%, rgba(255,255,255,0.7) 100%)"
    GRADIENT_LOGIN_HERO = "linear-gradient(135deg, rgba(22, 101, 52, 0.92) 0%, rgba(5, 46, 22, 0.96) 100%)"

class Design:
    RADIUS_SM = "8px"
    RADIUS_MD = "12px"
    RADIUS_LG = "16px"
    RADIUS_XL = "20px"
    RADIUS_XXL = "24px"
    RADIUS_FULL = "9999px"

    SHADOW_SM = "0 1px 3px rgba(15, 23, 42, 0.06), 0 1px 2px rgba(15, 23, 42, 0.04)"
    SHADOW_DEFAULT = "0 4px 12px rgba(15, 23, 42, 0.08)"
    SHADOW_MD = "0 8px 24px rgba(15, 23, 42, 0.1)"
    SHADOW_LG = "0 16px 40px rgba(15, 23, 42, 0.12)"

    HEIGHT_MD = "44px"
    HEIGHT_LG = "52px"

    MODAL_WIDTH_SM = "450px"
    MODAL_WIDTH_MD = "500px"

    MAX_WIDTH_APP = "1400px"

    Z_INDEX_NAVBAR = "1000"
    Z_INDEX_TOAST = "9999"

class Typography:
    H1 = {"font_size": "1.875rem", "font_weight": "700", "line_height": "1.2", "color": Color.DEEP, "font_family": "var(--font-display)"}
    H2 = {"font_size": "1.5rem", "font_weight": "700", "line_height": "1.25", "color": Color.DEEP, "font_family": "var(--font-display)"}
    H3 = {"font_size": "1.125rem", "font_weight": "600", "line_height": "1.35", "color": Color.DEEP, "font_family": "var(--font-display)"}
    H4 = {"font_size": "1rem", "font_weight": "600", "color": Color.TEXT_PRIMARY, "font_family": "var(--font-display)"}
    H5 = {"font_size": "0.875rem", "font_weight": "600", "color": Color.TEXT_PRIMARY, "font_family": "var(--font-display)"}

    BODY = {"font_size": "0.9375rem", "font_weight": "400", "line_height": "1.6", "color": Color.TEXT_PRIMARY, "font_family": "var(--font-body)"}
    BODY_LARGE = {"font_size": "1.0625rem", "font_weight": "400", "color": Color.TEXT_PRIMARY, "font_family": "var(--font-body)"}
    BODY_SECONDARY = {"font_size": "0.9375rem", "color": Color.TEXT_SECONDARY, "font_family": "var(--font-body)"}
    SMALL = {"font_size": "0.8125rem", "color": Color.TEXT_SECONDARY, "font_family": "var(--font-body)"}
    CAPTION = {"font_size": "0.6875rem", "font_weight": "500", "color": Color.TEXT_SECONDARY, "text_transform": "uppercase", "letter_spacing": "0.05em", "font_family": "var(--font-body)"}

    LABEL = {"font_size": "0.8125rem", "font_weight": "500", "color": Color.TEXT_PRIMARY, "margin_bottom": "4px", "font_family": "var(--font-body)"}
    LABEL_LARGE = {"font_size": "0.9375rem", "font_weight": "500", "color": Color.TEXT_PRIMARY, "font_family": "var(--font-body)"}

    DISPLAY = {"font_size": "2rem", "font_weight": "800", "line_height": "1.1", "color": Color.DEEP, "font_family": "var(--font-display)"}

    # --- Size constants for direct use (replace hardcoded font_size values) ---
    SIZE_2XS = "0.65rem"
    SIZE_XS = "0.7rem"
    SIZE_SM_XS = "0.75rem"
    SIZE_SM = "0.8rem"
    SIZE_MD_SM = "0.9rem"
    SIZE_MD = "0.95rem"
    SIZE_LG = "1.1rem"
    SIZE_XL = "1.25rem"

class Spacing:
    XXS = "2px"
    XS = "4px"
    SM = "8px"
    SM_MD = "12px"
    MD = "16px"
    LG = "24px"
    XL = "32px"
    XXL = "48px"

STYLES = {
    "font_family": "var(--font-body)",
    "background_color": Color.BACKGROUND,
    "@keyframes fadeIn": {
        "from": {"opacity": "0"},
        "to": {"opacity": "1"},
    },
    "@keyframes slideUp": {
        "from": {"opacity": "0", "transform": "translateY(10px)"},
        "to": {"opacity": "1", "transform": "translateY(0)"},
    },
    "@keyframes voicePulse": {
        "0%": {"box_shadow": "0 0 0 0 rgba(239, 68, 68, 0.4)"},
        "70%": {"box_shadow": "0 0 0 20px rgba(239, 68, 68, 0)"},
        "100%": {"box_shadow": "0 0 0 0 rgba(239, 68, 68, 0)"},
    },
    ".animate-fade-in": {"animation": "fadeIn 0.4s ease-out"},
    ".animate-slide-up": {"animation": "slideUp 0.5s cubic-bezier(0.2, 0.8, 0.2, 1)"},
}

# =============================================================================
# COMPONENT STYLES
# =============================================================================

INPUT_STYLE = {
    "border": f"1px solid {Color.BORDER}",
    "border_radius": Design.RADIUS_MD,
    "padding": f"{Spacing.SM} {Spacing.MD}",
    "min_height": Design.HEIGHT_MD,
    "bg": Color.SURFACE,
    "color": Color.TEXT_PRIMARY,
    "placeholder_color": Color.TEXT_SECONDARY,
    "font_size": "0.9375rem",
    "transition": "all 0.15s ease",
    "_focus": {
        "border_color": Color.PRIMARY,
        "box_shadow": f"0 0 0 3px {Color.FOCUS_RING}",
        "outline": "none"
    },
    "_hover": {"border_color": Color.BORDER_HOVER}
}

INPUT_XL_STYLE = {
    "border": f"1px solid {Color.BORDER}",
    "border_radius": Design.RADIUS_MD,
    "padding": f"{Spacing.SM_MD} {Spacing.MD}",
    "min_height": Design.HEIGHT_LG,
    "width": "100%",
    "bg": Color.SURFACE,
    "color": Color.TEXT_PRIMARY,
    "placeholder_color": Color.TEXT_SECONDARY,
    "font_size": "0.9375rem",
    "transition": "all 0.15s ease",
    "_focus": {
        "border_color": Color.PRIMARY,
        "box_shadow": f"0 0 0 3px {Color.FOCUS_RING}",
        "outline": "none"
    },
    "_hover": {"border_color": Color.BORDER_HOVER}
}

BUTTON_PRIMARY_STYLE = {
    "bg": Color.PRIMARY,
    "color": Color.WHITE,
    "border": "1px solid transparent",
    "padding_x": Spacing.LG,
    "min_height": Design.HEIGHT_MD,
    "border_radius": Design.RADIUS_MD,
    "font_weight": "600",
    "font_size": "0.875rem",
    "transition": "all 0.15s ease",
    "box_shadow": Design.SHADOW_SM,
    "_hover": {
        "bg": Color.PRIMARY_HOVER,
        "box_shadow": Design.SHADOW_DEFAULT,
    },
    "_active": {
        "transform": "scale(0.98)",
    }
}

BUTTON_XL_STYLE = {
    "bg": Color.PRIMARY,
    "color": Color.WHITE,
    "border": "1px solid transparent",
    "padding_x": Spacing.XL,
    "min_height": Design.HEIGHT_LG,
    "width": "100%",
    "border_radius": Design.RADIUS_MD,
    "font_weight": "600",
    "font_size": "0.9375rem",
    "transition": "all 0.15s ease",
    "box_shadow": Design.SHADOW_SM,
    "_hover": {
        "bg": Color.PRIMARY_HOVER,
        "box_shadow": Design.SHADOW_DEFAULT,
    },
    "_active": {
        "transform": "scale(0.98)",
    }
}

CARD_STYLE = {
    "bg": Color.SURFACE,
    "border": f"1px solid {Color.BORDER}",
    "border_radius": Design.RADIUS_XL,
    "padding": Spacing.LG,
    "box_shadow": Design.SHADOW_SM,
    "transition": "all 0.2s ease",
    "width": "100%",
    "_hover": {
        "box_shadow": Design.SHADOW_DEFAULT,
    }
}

BUTTON_SECONDARY_STYLE = {
    "bg": Color.SURFACE,
    "color": Color.TEXT_PRIMARY,
    "border": f"1px solid {Color.BORDER}",
    "padding_y": Spacing.SM,
    "padding_x": Spacing.LG,
    "min_height": Design.HEIGHT_MD,
    "border_radius": Design.RADIUS_MD,
    "font_weight": "600",
    "font_size": "0.875rem",
    "cursor": "pointer",
    "transition": "all 0.15s ease",
    "_hover": {
        "bg": Color.SURFACE_ALT,
        "border_color": Color.BORDER_HOVER,
    },
    "_active": {"transform": "scale(0.98)"},
    "_disabled": {
        "opacity": 0.5,
        "cursor": "not-allowed",
    }
}

GLASS_STYLE = {
    "background_color": "rgba(255, 255, 255, 0.85)",
    "backdrop_filter": "blur(12px) saturate(150%)",
    "-webkit-backdrop-filter": "blur(12px) saturate(150%)",
    "border": f"1px solid {Color.BORDER}",
}
