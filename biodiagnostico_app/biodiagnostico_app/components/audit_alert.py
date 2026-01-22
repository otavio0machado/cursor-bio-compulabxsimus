import reflex as rx
from ..state import State
from ..styles import Color, Design, Spacing

def audit_alert() -> rx.Component:
    """
    Componente de alerta de auditoria com Motion System e Glassmorphism.
    Aparece de baixo para cima com suavidade.
    """
    return rx.cond(
        State.is_audit_alert_visible,
        rx.box(
            rx.hstack(
                rx.icon(
                    "shield-check", 
                    size=20, 
                    color=rx.cond(
                        State.audit_warning_level == "critical", 
                        Color.ERROR, 
                        rx.cond(
                            State.audit_warning_level == "high",
                            Color.WARNING,
                            Color.PRIMARY
                        )
                    )
                ),
                rx.text(
                    State.audit_alert_message,
                    font_size="0.875rem",
                    font_weight="500",
                    color=Color.TEXT_PRIMARY,
                ),
                rx.spacer(),
                rx.icon(
                    "x", 
                    size=16, 
                    cursor="pointer", 
                    on_click=lambda: State.set_is_audit_alert_visible(False)
                ),
                spacing="3",
                align="center",
            ),
            position="fixed",
            bottom="24px",
            right="24px",
            width=["calc(100% - 48px)", "400px"],
            padding=Spacing.MD,
            background_color="rgba(255, 255, 255, 0.8)",
            backdrop_filter="blur(12px)",
            border=f"1px solid {Color.BORDER}",
            border_radius=Design.RADIUS_LG,
            box_shadow=Design.SHADOW_LG,
            z_index="1000",
            # Motion System: Entrada suave fadeIn + slideUp (300ms)
            transition="all 300ms ease-in-out",
            opacity="1",
            transform="translateY(0)",
            custom_attrs={"aria-live": "polite"},
        ),
        rx.box(
            opacity="0",
            transform="translateY(20px)",
            transition="all 300ms ease-in-out",
        )
    )
