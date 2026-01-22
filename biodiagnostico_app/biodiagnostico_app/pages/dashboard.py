import reflex as rx
from ..state import State
from ..styles import Color, Design, Typography, Spacing
from ..components import ui

def quick_access_card(title: str, description: str, icon: str, page: str, delay: str = "0s") -> rx.Component:
    """Card de acesso rápido padronizado com animação de entrada"""
    return rx.box(
        ui.card(
            rx.vstack(
                rx.box(
                    rx.icon(icon, size=32, color=Color.PRIMARY),
                    bg=Color.PRIMARY_LIGHT, p="4", border_radius=Design.RADIUS_LG, margin_bottom=Spacing.XS,
                    transition="transform 0.3s ease",
                    _group_hover={"transform": "scale(1.1) rotate(5deg)"}
                ),
                ui.heading(title, level=3),
                ui.text(description, size="small", color=Color.TEXT_SECONDARY),
                align_items="start",
                spacing="2"
            ),
            on_click=lambda: State.set_page(page),
            cursor="pointer",
            transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
            _hover={
                "box_shadow": Design.SHADOW_LG,
                "transform": "translateY(-6px)",
                "border_color": Color.PRIMARY
            }
        ),
        animation=f"fadeInUp 0.6s ease-out {delay} both",
        class_name="group"
    )

def hero_metric_card() -> rx.Component:
    """Card de faturamento destaque com design premium"""
    return rx.box(
        rx.flex(
            # Coluna de texto
            rx.vstack(
                rx.hstack(
                    rx.icon(tag="activity", size=14, color=Color.PRIMARY),
                    rx.text("FATURAMENTO PROCESSADO", font_size="0.7rem", font_weight="700", color=Color.TEXT_SECONDARY, letter_spacing="0.15em"),
                    align_items="center",
                    style={"gap": "6px"}
                ),
                rx.text(State.formatted_compulab_total, font_size=["2rem", "2.5rem", "3rem"], font_weight="800", color=Color.DEEP, line_height="1.1"),
                rx.hstack(
                    rx.box(
                        rx.icon(
                            tag=rx.cond(State.financial_growth_day >= 0, "trending-up", "trending-down"),
                            size=14, color="white"
                        ),
                        bg=rx.cond(State.financial_growth_day >= 0, Color.SUCCESS, Color.ERROR),
                        p="1", border_radius="6px"
                    ),
                    rx.text(
                        f"{State.financial_growth_day.to_string()}% vs ontem",
                        font_size="0.875rem", font_weight="600",
                        color=rx.cond(State.financial_growth_day >= 0, Color.SUCCESS, Color.ERROR)
                    ),
                    align_items="center",
                    style={"gap": "8px"}
                ),
                align_items="start",
                style={"gap": "8px"},
                width="100%"
            ),
            rx.spacer(),
            # Ícone destaque
            rx.box(
                rx.icon(tag="banknote", size=40, color="white"),
                bg=Color.GRADIENT_PRIMARY,
                p="4", border_radius="20px",
                display={"initial": "none", "md": "block"}, # Esconde em mobile/tablet vertical, mostra em desktop
                box_shadow=f"0 8px 24px -4px {Color.PRIMARY}60"
            ),
            width="100%",
            align_items="center",
            direction={"initial": "column", "md": "row"}, # Stack vert em mobile
            gap="4"
        ),
        bg=Color.SURFACE,
        border=f"1px solid {Color.BORDER}",
        border_radius="20px",
        padding=[Spacing.MD, Spacing.LG, Spacing.XL], # Padding responsivo
        box_shadow=Design.SHADOW_MD,
        transition="all 0.3s ease",
        _hover={"box_shadow": Design.SHADOW_LG, "border_color": Color.PRIMARY},
        animation="fadeInUp 0.5s ease-out both",
        width="100%"
    )

def progress_card() -> rx.Component:
    """Card de progresso da meta com animação"""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.hstack(
                    rx.icon(tag="target", size=16, color=Color.PRIMARY),
                    rx.text("META MENSAL", font_size="0.7rem", font_weight="700", color=Color.TEXT_SECONDARY, letter_spacing="0.1em"),
                    align_items="center",
                    style={"gap": "6px"}
                ),
                rx.spacer(),
                rx.box(
                    rx.text(f"{State.goal_progress.to_string()}%", font_weight="800", color=Color.DEEP),
                    bg=Color.PRIMARY_LIGHT,
                    px="3", py="1",
                    border_radius="full"
                ),
                width="100%",
                align_items="center"
            ),
            # Barra de progresso animada
            rx.box(
                rx.box(
                    bg=Color.GRADIENT_PRIMARY,
                    border_radius="full",
                    transition="width 1.5s cubic-bezier(0.4, 0, 0.2, 1)",
                    width=State.goal_progress.to_string() + "%",
                    height="100%",
                    position="relative",
                    overflow="hidden",
                    _after={
                        "content": '""',
                        "position": "absolute",
                        "top": "0", "left": "-100%",
                        "width": "100%", "height": "100%",
                        "background": "linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent)",
                        "animation": "shimmer 2s infinite"
                    }
                ),
                width="100%", h="12px", bg=Color.BACKGROUND, border_radius="full", overflow="hidden", margin_y=Spacing.SM
            ),
            rx.hstack(
                rx.text(State.formatted_compulab_total, font_size="0.8rem", color=Color.TEXT_LIGHT, font_weight="500"),
                rx.spacer(),
                rx.text(f"Meta: {State.formatted_monthly_goal}", font_size="0.8rem", color=Color.TEXT_LIGHT, font_weight="500"),
                width="100%"
            ),
            width="100%",
            style={"gap": "4px"}
        ),
        bg=Color.SURFACE,
        border=f"1px solid {Color.BORDER}",
        border_radius="16px",
        padding=Spacing.LG,
        animation="fadeInUp 0.6s ease-out 0.1s both",
        width="100%"
    )

def dashboard_page() -> rx.Component:
    """Dashboard Premium - Fase 4 UI/UX Refinement"""
    
    # CSS Animations injection
    animations_css = """
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @keyframes shimmer {
            0% { left: -100%; }
            100% { left: 100%; }
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }
    """
    
    return rx.fragment(
        rx.script(f"if(!document.getElementById('dash-anim')){{ const s=document.createElement('style'); s.id='dash-anim'; s.textContent=`{animations_css}`; document.head.appendChild(s); }}"),
        rx.box(
            rx.vstack(
                # Welcome Banner com animação
                rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.text("👋", font_size="2rem"),
                            rx.text("Bem-vindo de volta", style=Typography.H1, color=Color.DEEP),
                            align_items="center",
                            style={"gap": "12px"}
                        ),
                        rx.text("Aqui está o resumo de hoje", style=Typography.BODY_SECONDARY, color=Color.TEXT_SECONDARY),
                        align_items="center",
                        style={"gap": "4px"}
                    ),
                    width="100%", display="flex", justify_content="center",
                    animation="fadeInUp 0.4s ease-out both",
                    padding_y=[Spacing.MD, Spacing.LG, Spacing.XL],
                    padding_x=[Spacing.MD, Spacing.LG]
                ),
                
                # Main Grid - Scoreboard
                rx.grid(
                    # Coluna Esquerda - Métricas Financeiras
                    rx.vstack(
                        hero_metric_card(),
                        progress_card(),
                        
                        # Forecast Card
                        rx.box(
                            rx.hstack(
                                rx.vstack(
                                    rx.hstack(
                                        rx.icon(tag="sparkles", size=14, color=Color.PRIMARY),
                                        rx.text("PREVISÃO DE RECEITA", font_size="0.65rem", font_weight="700", color=Color.PRIMARY, letter_spacing="0.15em"),
                                        align_items="center",
                                        style={"gap": "6px"}
                                    ),
                                    rx.text(State.formatted_revenue_forecast, font_size="1.75rem", font_weight="800", color=Color.DEEP),
                                    rx.text("Baseado nos últimos 6 meses", font_size="0.75rem", color=Color.TEXT_LIGHT),
                                    align_items="start",
                                    style={"gap": "2px"}
                                ),
                                rx.spacer(),
                                rx.box(
                                    rx.icon(tag="chart-line", size=24, color=Color.PRIMARY),
                                    bg=Color.PRIMARY_LIGHT, p="3", border_radius="12px"
                                ),
                                width="100%",
                                align_items="center"
                            ),
                            bg=f"linear-gradient(135deg, {Color.PRIMARY_LIGHT} 0%, white 100%)",
                            border=f"1px solid {Color.PRIMARY}30",
                            border_radius="16px",
                            padding=Spacing.LG,
                            animation="fadeInUp 0.7s ease-out 0.2s both",
                            width="100%"
                        ),
                        
                        # Mini Stats Grid
                        rx.grid(
                            ui.stat_card("Aprovação CQ", rx.cond(State.dashboard_approval_rate > 0, State.dashboard_approval_rate.to_string() + "%", "100%"), "circle-check", "success", "Média mensal"),
                            ui.stat_card("Manutenções", State.dashboard_pending_maintenances.to_string(), "wrench", "warning", "Pendentes"),
                            ui.stat_card("Pacientes", State.total_patients_count.to_string(), "users", "primary", "Processados"),
                            ui.stat_card("Divergências", State.divergences_count.to_string(), "triangle-alert", "error", "Detectadas"),
                            columns={"initial": "1", "sm": "2"},
                            spacing="4",
                            width="100%"
                        ),
                        width="100%",
                        spacing="4"
                    ),
                    
                    # Coluna Direita - Top Ofensores
                    rx.box(
                        rx.vstack(
                            rx.hstack(
                                rx.box(
                                    rx.icon(tag="octagon-alert", size=18, color="white"),
                                    bg=Color.ERROR, p="2", border_radius="10px"
                                ),
                                rx.text("Top Ofensores", font_weight="700", color=Color.DEEP, font_size="1.1rem"),
                                rx.spacer(),
                                ui.status_badge("Divergências", status="error"),
                                align_items="center",
                                width="100%",
                                style={"gap": "10px"}
                            ),
                            rx.divider(opacity=0.2, margin_y=Spacing.SM),
                            rx.cond(
                                State.top_offenders.length() > 0,
                                rx.vstack(
                                    rx.foreach(
                                        State.top_offenders,
                                        lambda item, i: rx.hstack(
                                            rx.box(
                                                rx.text(f"#{(i + 1).to_string()}", font_size="0.7rem", font_weight="800", color=Color.TEXT_LIGHT),
                                                width="24px"
                                            ),
                                            rx.box(
                                                rx.text(item.name, font_size="0.9rem", font_weight="500", color=Color.TEXT_PRIMARY,
                                                       style={"max_width": "180px", "overflow": "hidden", "text_overflow": "ellipsis", "white_space": "nowrap"}),
                                                flex="1"
                                            ),
                                            rx.box(
                                                rx.text(f"{item.count.to_string()}×", font_size="0.8rem", font_weight="700", color=Color.ERROR),
                                                bg=Color.ERROR_BG, px="3", py="1", border_radius="full"
                                            ),
                                            width="100%",
                                            align_items="center",
                                            padding=Spacing.MD, bg=Color.BACKGROUND, border_radius=Design.RADIUS_LG,
                                            border=f"1px solid transparent",
                                            _hover={"border_color": Color.ERROR, "bg": Color.ERROR_BG},
                                            transition="all 0.2s ease"
                                        )
                                    ),
                                    spacing="2",
                                    width="100%"
                                ),
                                rx.center(
                                    rx.vstack(
                                        rx.box(
                                            rx.icon(tag="party-popper", size=36, color=Color.SUCCESS),
                                            bg=Color.SUCCESS_BG, p="4", border_radius="full"
                                        ),
                                        rx.text("Tudo em ordem!", font_weight="600", color=Color.SUCCESS),
                                        rx.text("Nenhum ofensor detectado", font_size="0.8rem", color=Color.TEXT_LIGHT),
                                        align_items="center",
                                        spacing="2"
                                    ),
                                    height="200px", width="100%"
                                )
                            ),
                            width="100%",
                            height="100%"
                        ),
                        bg=Color.SURFACE,
                        border=f"1px solid {Color.BORDER}",
                        border_radius="20px",
                        padding=Spacing.LG,
                        height="100%",
                        animation="fadeInUp 0.6s ease-out 0.15s both"
                    ),
                    
                    columns={"initial": "1", "md": "2"},
                    spacing="6",
                    width="100%",
                    max_width="6xl", margin_x="auto", margin_bottom=Spacing.XL
                ),
                
                rx.divider(max_width="6xl", margin_x="auto", margin_bottom=Spacing.XL, opacity=0.2),
                
                # Quick Access Section
                rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.icon(tag="layout-grid", size=20, color=Color.PRIMARY),
                            rx.text("Acesso Rápido", style=Typography.H2, color=Color.DEEP),
                            align_items="center",
                            style={"gap": "10px"}
                        ),
                        rx.text("Atalhos para as principais funções do sistema", font_size="0.9rem", color=Color.TEXT_SECONDARY),
                        align_items="center",
                        style={"gap": "4px"},
                        margin_bottom=Spacing.LG
                    ),
                    animation="fadeInUp 0.8s ease-out 0.3s both"
                ),
                rx.grid(
                    quick_access_card(
                        "Conversor PDF",
                        "Extração e padronização de relatórios do Compulab e Simus.",
                        "file-text",
                        "conversor",
                        "0.35s"
                    ),
                    quick_access_card(
                        "Análise Cruzada",
                        "Identificação de divergências financeiras e exames faltantes.",
                        "chart-bar",
                        "analise",
                        "0.45s"
                    ),
                    quick_access_card(
                        "Gestão da Qualidade",
                        "Controle ProIn, gráficos Levey-Jennings e gestão de reagentes.",
                        "beaker",
                        "proin",
                        "0.55s"
                    ),
                    columns={"initial": "1", "md": "3"},
                    spacing="6",
                    width="100%",
                    max_width="6xl", margin_x="auto", margin_bottom="4rem"
                ),

                width="100%",
                align_items="center",
                padding_bottom="4rem"
            ),
            width="100%"
        )
    )
