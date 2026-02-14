"""Helpers compartilhados pelos componentes ProIn."""
import reflex as rx
from ...state import State
from ...styles import Color, Design, Typography, Spacing


def format_cv(value) -> rx.Var:
    """Format CV with two decimal places and comma separator."""
    value_var = rx.Var.create(value).to(float)
    return rx.Var.create(f"{value_var:.2f}").replace(".", ",")


def qc_status_label(status, cv, cv_max) -> rx.Var:
    """Status exibido SOMENTE baseado em CV% vs threshold configurado.
    Alerta aparece apenas quando CV% ultrapassa o limite determinado."""
    cv_var = rx.Var.create(cv).to(float)
    cv_max_var = rx.Var.create(cv_max).to(float)
    return rx.cond(cv_var <= cv_max_var, "OK", "ALERTA (CV)")


def qc_status_kind(status, cv, cv_max) -> rx.Var:
    """Tipo visual SOMENTE baseado em CV% vs threshold configurado."""
    cv_var = rx.Var.create(cv).to(float)
    cv_max_var = rx.Var.create(cv_max).to(float)
    return rx.cond(cv_var <= cv_max_var, "success", "warning")


def tab_button(label: str, icon: str, tab_id: str) -> rx.Component:
    """Botão de aba do ProIn"""
    is_active = State.proin_current_tab == tab_id

    return rx.button(
        rx.hstack(
            rx.icon(tag=icon, size=16),
            rx.text(label, font_size=Typography.SMALL["font_size"], font_weight="500"),
            style={"gap": Spacing.XS},
            align_items="center",
        ),
        on_click=lambda: State.set_proin_tab(tab_id),
        bg=rx.cond(is_active, Color.PRIMARY_LIGHT, "transparent"),
        color=rx.cond(is_active, Color.PRIMARY, Color.TEXT_SECONDARY),
        border_radius=Design.RADIUS_MD,
        padding_x=Spacing.MD,
        padding_y=Spacing.SM,
        border=rx.cond(is_active, f"1px solid {Color.PRIMARY}30", "1px solid transparent"),
        _hover={
            "bg": Color.SURFACE_ALT,
            "color": Color.TEXT_PRIMARY,
        },
        transition="all 0.15s ease"
    )
