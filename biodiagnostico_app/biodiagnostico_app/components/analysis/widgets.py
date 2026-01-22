import reflex as rx
from typing import Any
from ...state import State
from ...components import ui
from ...styles import Color, Design, Spacing, Typography, GLASS_STYLE, CARD_STYLE

# === ANALYSIS PAGE COMPONENTS (REMASTERED PREMIUM) ===

def metric_card_premium(title: str, value: str, icon: str, subtitle: str = "", color_scheme: str = "green", delay: str = "0s"):
    """Card de métrica com design glassmorphism e animação de entrada (REMASTERED)"""
    colors = {
        "green": (Color.SUCCESS, Color.SUCCESS_BG, "circle-check"),
        "blue": (Color.PRIMARY, Color.PRIMARY_LIGHT, "bar-chart-2"),
        "orange": (Color.WARNING, Color.WARNING_BG, "alert-triangle"),
        "red": (Color.ERROR, Color.ERROR_BG, "x-circle"),
    }
    fg, bg, default_icon = colors.get(color_scheme, colors["green"])
    
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.box(
                    rx.icon(tag=icon, size=24, color=fg),
                    bg="rgba(255,255,255,0.8)", # Glass white
                    padding="12px", 
                    border_radius="14px",
                    box_shadow=f"0 8px 16px -4px {bg}",
                    backdrop_filter="blur(4px)"
                ),
                rx.spacer(),
                rx.cond(
                    subtitle != "",
                    rx.box(
                        rx.text(subtitle, size="1", weight="bold", color=fg),
                        padding_x="8px", padding_y="4px",
                        bg=bg, border_radius="full",
                        border=f"1px solid {fg}20"
                    )
                ),
                width="100%", align_items="center"
            ),
            rx.vstack(
                rx.text(value, font_size="2rem", font_weight="800", color=Color.DEEP, letter_spacing="-1px", line_height="1.1"),
                rx.text(title, font_size="0.75rem", font_weight="600", color=Color.TEXT_SECONDARY, text_transform="uppercase", letter_spacing="1px"),
                spacing="2", align_items="start"
            ),
            spacing="5", align_items="start", width="100%"
        ),
        # Glassmorphism Container
        bg="rgba(255, 255, 255, 0.6)",
        backdrop_filter="blur(16px) saturate(180%)",
        padding=Spacing.LG,
        border_radius=Design.RADIUS_XL,
        border=f"1px solid rgba(255,255,255,0.6)",
        box_shadow="0 10px 30px -10px rgba(0,0,0,0.05)",
        transition="all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275)",
        _hover={
            "transform": "translateY(-5px) scale(1.01)",
            "box_shadow": f"0 20px 40px -12px {bg}",
            "bg": "rgba(255, 255, 255, 0.8)",
            "border_color": fg
        },
        animation=f"fadeInUp 0.6s ease-out {delay} both",
        overflow="hidden",
        position="relative",
        # Decorative gradient blob
        _before={
            "content": "''",
            "position": "absolute",
            "top": "-50%",
            "right": "-50%",
            "width": "100%",
            "height": "100%",
            "background": f"radial-gradient(circle, {bg} 0%, transparent 70%)",
            "opacity": "0.5",
            "z_index": "-1"
        }
    )

def insight_card(icon: str, title: str, description: str, type: str = "warning"):
    """Card de insight para o Action Center (REMASTERED)"""
    color_map = {
        "warning": (Color.WARNING, Color.WARNING_BG),
        "error": (Color.ERROR, Color.ERROR_BG),
        "info": (Color.PRIMARY, Color.PRIMARY_LIGHT),
        "success": (Color.SUCCESS, Color.SUCCESS_BG)
    }
    fg, bg = color_map.get(type, (Color.PRIMARY, Color.PRIMARY_LIGHT))
    
    return rx.box(
        rx.hstack(
            rx.center(
                rx.icon(tag=icon, size=20, color="white"),
                bg=fg, 
                width="40px", height="40px",
                border_radius="12px",
                box_shadow=f"0 4px 10px {fg}40",
                flex_shrink="0"
            ),
            rx.vstack(
                rx.text(title, font_weight="bold", color=Color.DEEP, font_size="0.95rem"),
                rx.text(description, font_size="0.85rem", color=Color.TEXT_SECONDARY, line_height="1.4"),
                spacing="1", align_items="start", width="100%"
            ),
            spacing="4", align_items="start", width="100%"
        ),
        padding="16px",
        bg="rgba(255,255,255,0.6)",
        border_radius=Design.RADIUS_LG,
        border=f"1px solid {Color.BORDER}",
        transition="all 0.2s ease",
        _hover={
            "transform": "translateX(4px)",
            "bg": "white",
            "border_left": f"4px solid {fg}",
            "box_shadow": Design.SHADOW_SM
        },
        cursor="default"
    )

def patient_history_modal() -> rx.Component:
    """Modal de histórico REMASTERED"""
    return rx.dialog.root(
        rx.dialog.content(
            # Header Premium
            rx.box(
                rx.hstack(
                    rx.center(
                        rx.icon(tag="user", size=24, color="white"),
                        bg=Color.GRADIENT_PRIMARY,
                        width="48px", height="48px",
                        border_radius="16px",
                        box_shadow=f"0 6px 16px {Color.PRIMARY}40"
                    ),
                    rx.vstack(
                        rx.text(State.selected_patient_name, size="5", weight="bold", color=Color.DEEP),
                        rx.hstack(
                            rx.badge("PACIENTE PRIORITÁRIO", color_scheme="blue", variant="solid", radius="full"),
                            rx.text(f"#{State.selected_patient_id}", size="2", color=Color.TEXT_SECONDARY),
                            spacing="3", align_items="center"
                        ),
                        spacing="1",
                    ),
                    rx.spacer(),
                    rx.dialog.close(
                        rx.button(
                            rx.icon("x", size=24), 
                            variant="ghost", 
                            color=Color.TEXT_SECONDARY, 
                            border_radius="full",
                            padding="8px",
                            _hover={"bg": Color.ERROR_BG, "color": Color.ERROR}
                        )
                    ),
                    width="100%", align_items="center"
                ),
                padding="24px",
                border_bottom=f"1px solid {Color.BORDER}",
                background="linear-gradient(to bottom, #ffffff, #fcfcfc)"
            ),
            
            # Corpo
            rx.box(
                rx.grid(
                    rx.vstack(
                        rx.text("Registros Auditados", style=Typography.LABEL_LARGE, color=Color.TEXT_SECONDARY),
                        rx.text(State.patient_history_data.length().to_string(), size="6", weight="bold", color=Color.DEEP),
                        spacing="1", bg=Color.BACKGROUND, padding="16px", border_radius="12px"
                    ),
                    rx.vstack(
                        rx.text("Status da Ficha", style=Typography.LABEL_LARGE, color=Color.TEXT_SECONDARY),
                        rx.badge("EM ANÁLISE", color_scheme="amber", variant="soft", size="3"),
                        spacing="1", bg=Color.BACKGROUND, padding="16px", border_radius="12px"
                    ),
                    columns="2", spacing="4", width="100%", margin_bottom="24px"
                ),
                
                rx.text("Linha do Tempo", weight="bold", color=Color.DEEP, margin_bottom="16px"),
                
                # Scroll Area da Timeline
                rx.scroll_area(
                    rx.vstack(
                        rx.foreach(
                            State.patient_history_data,
                            lambda exam: rx.box(
                                rx.hstack(
                                    # Linha e Bolinha (Visual)
                                    rx.vstack(
                                        rx.box(width="2px", height="100%", bg=Color.BORDER, opacity=0.5, position="relative", z_index="0"),
                                        align_items="center", height="100%", width="24px", position="relative"
                                    ),
                                    # Indicador
                                    rx.box(
                                        width="12px", height="12px", border_radius="full",
                                        bg=rx.cond(exam.status == "Divergente", Color.ERROR, Color.SUCCESS),
                                        position="absolute", left="6px", top="24px", z_index="1",
                                        box_shadow=f"0 0 0 4px white"
                                    ),
                                    # Card de Conteúdo
                                    rx.box(
                                        rx.flex(
                                            rx.vstack(
                                                rx.text(exam.exam_name, weight="bold", color=Color.TEXT_PRIMARY),
                                                rx.text(exam.created_at, size="1", color=Color.TEXT_SECONDARY),
                                                spacing="1"
                                            ),
                                            rx.spacer(),
                                            rx.vstack(
                                                rx.text(f"R$ {exam.last_value}", weight="bold", color=Color.PRIMARY, text_align="right"),
                                                rx.badge(exam.status, color_scheme=rx.cond(exam.status == "Divergente", "red", "green"), variant="outline"),
                                                spacing="1", align_items="end"
                                            ),
                                            width="100%"
                                        ),
                                        rx.cond(
                                            exam.notes != "",
                                            rx.text(exam.notes, size="2", color=Color.TEXT_SECONDARY, margin_top="8px", font_style="italic")
                                        ),
                                        bg=Color.SURFACE,
                                        padding="16px",
                                        border_radius="16px",
                                        box_shadow=Design.SHADOW_SM,
                                        border=f"1px solid {Color.BORDER}",
                                        width="100%",
                                        _hover={"border_color": Color.PRIMARY, "box_shadow": Design.SHADOW_MD}
                                    ),
                                    padding_bottom="16px",
                                    position="relative", width="100%"
                                )
                            )
                        ),
                        spacing="0", width="100%"
                    ),
                    type="auto", scrollbars="vertical", style={"max_height": "400px"}
                ),
                padding="24px"
            ),
            
            background_color="#F8FAFC",
            max_width="600px",
            border_radius="24px",
            box_shadow="0 50px 100px -20px rgba(0,0,0,0.3)",
            padding="0",
            overflow="hidden"
        ),
        open=State.is_showing_patient_history,
        on_open_change=State.set_is_showing_patient_history,
    )

def action_table(headers: list[str], data: list, columns_keys: list[str], patient_key: str = "patient", is_divergence: bool = False) -> rx.Component:
    """Tabela de dados REMASTERED"""
    
    def render_row(item: Any, i: rx.Var[int]):
        # Row styling
        cells = [
            rx.table.cell(
                rx.text(getattr(item, key), font_size="0.9rem", color=Color.TEXT_PRIMARY, font_weight="500"),
                padding="16px 20px"
            ) for key in columns_keys
        ]
        
        # Actions
        actions = [
            ui.button("", icon="history", on_click=lambda: State.view_patient_history(getattr(item, patient_key)), variant="ghost", size="2", padding="6px", color="gray")
        ]
        
        if "exam_name" in columns_keys:
            res_key = getattr(item, patient_key) + "|" + getattr(item, "exam_name")
            is_resolved = State.resolutions[res_key] == "resolvido"
            actions.append(
                ui.button(
                    "",
                    icon=rx.cond(is_resolved, "check-circle", "circle"),
                    on_click=lambda: State.toggle_resolution(getattr(item, patient_key), getattr(item, "exam_name")),
                    variant="ghost", 
                    color=rx.cond(is_resolved, Color.SUCCESS, "gray"),
                    size="2", padding="6px"
                )
            )

        cells.append(
            rx.table.cell(
                rx.hstack(*actions, spacing="2", justify="end"),
                padding="12px 16px"
            )
        )
        
        return rx.table.row(
            *cells,
            bg=rx.cond(i % 2 == 0, "rgba(255,255,255,0.4)", "rgba(255,255,255,0.1)"),
            border_bottom=f"1px solid {Color.BORDER}",
            _hover={"bg": "white", "box_shadow": Design.SHADOW_SM, "transform": "scale(1.002)"},
            transition="all 0.2s ease"
        )
    
    return rx.box(
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    *[rx.table.column_header_cell(
                        rx.text(h, size="1", weight="bold", color=Color.TEXT_SECONDARY, text_transform="uppercase", letter_spacing="1px"),
                        padding="16px 20px", bg="rgba(248, 250, 252, 0.8)", border_bottom=f"2px solid {Color.BORDER}"
                    ) for h in headers],
                    rx.table.column_header_cell(
                        rx.text("AÇÕES", size="1", weight="bold", color=Color.TEXT_SECONDARY, text_align="right", text_transform="uppercase"),
                        padding="16px 20px", bg="rgba(248, 250, 252, 0.8)", border_bottom=f"2px solid {Color.BORDER}"
                    )
                )
            ),
            rx.table.body(rx.foreach(data, render_row)),
            variant="ghost",
            width="100%",
        ),
        bg="rgba(255, 255, 255, 0.6)",
        backdrop_filter="blur(10px)",
        border=f"1px solid {Color.BORDER}",
        border_radius=Design.RADIUS_XL,
        overflow="hidden",
        box_shadow=Design.SHADOW_DEFAULT,
        width="100%"
    )
