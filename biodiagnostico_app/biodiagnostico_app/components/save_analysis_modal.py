"""
Componente Modal para Salvar Análise
Seguindo skill UI/UX Reflex Premium
"""
import reflex as rx
from ..styles import Color


def save_analysis_modal() -> rx.Component:
    """
    Modal premium para salvar análise com nome e data.
    Usa tokens de design da skill UI/UX.
    """
    from ..state import State
    
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                rx.icon(tag="save", size=18),
                "Salvar Análise",
                variant="soft",
                color_scheme="green",
                cursor="pointer",
                on_click=State.open_save_modal,
            )
        ),
        rx.dialog.content(
            rx.dialog.title(
                rx.hstack(
                    rx.icon(tag="archive", size=24, color=Color.PRIMARY),
                    "Salvar Análise",
                    spacing="2",
                    align="center"
                ),
            ),
            rx.dialog.description(
                "Salve esta análise para consultar depois. Escolha um nome e data para organização.",
                size="2",
                color_scheme="gray"
            ),
            
            rx.vstack(
                # Campo: Nome da Análise
                rx.box(
                    rx.text("Nome da Análise *", size="2", weight="medium", color=Color.TEXT_SECONDARY),
                    rx.input(
                        placeholder="Ex: Janeiro 2026, Conferência Mensal...",
                        value=State.save_analysis_name,
                        on_change=State.set_save_analysis_name,
                        size="3",
                        width="100%",
                    ),
                    width="100%",
                ),
                
                # Campo: Data
                rx.box(
                    rx.text("Data da Análise *", size="2", weight="medium", color=Color.TEXT_SECONDARY),
                    rx.input(
                        type="date",
                        value=State.save_analysis_date,
                        on_change=State.set_save_analysis_date,
                        size="3",
                        width="100%",
                    ),
                    width="100%",
                ),
                
                # Campo: Descrição (opcional)
                rx.box(
                    rx.text("Descrição (opcional)", size="2", weight="medium", color=Color.TEXT_SECONDARY),
                    rx.text_area(
                        placeholder="Observações sobre esta análise...",
                        value=State.save_analysis_description,
                        on_change=State.set_save_analysis_description,
                        rows="3",
                        width="100%",
                    ),
                    width="100%",
                ),
                
                # Resumo do que será salvo
                rx.card(
                    rx.vstack(
                        rx.text("📊 Resumo", size="2", weight="bold", color=Color.TEXT_PRIMARY),
                        rx.hstack(
                            rx.text("COMPULAB:", size="1", color=Color.TEXT_SECONDARY),
                            rx.text(State.formatted_compulab_total, size="1", weight="medium"),
                            spacing="1",
                        ),
                        rx.hstack(
                            rx.text("SIMUS:", size="1", color=Color.TEXT_SECONDARY),
                            rx.text(State.formatted_simus_total, size="1", weight="medium"),
                            spacing="1",
                        ),
                        rx.hstack(
                            rx.text("Divergências:", size="1", color=Color.TEXT_SECONDARY),
                            rx.text(f"{State.divergences_count}", size="1", weight="medium"),
                            spacing="1",
                        ),
                        spacing="1",
                        align_items="start",
                    ),
                    variant="surface",
                    size="1",
                    width="100%",
                ),
                
                # Mensagem de feedback
                rx.cond(
                    State.save_analysis_message != "",
                    rx.callout(
                        State.save_analysis_message,
                        icon="info",
                        size="1",
                        width="100%",
                    ),
                    rx.fragment(),
                ),
                
                spacing="4",
                width="100%",
                padding_y="4",
            ),
            
            # Botões de ação
            rx.flex(
                rx.dialog.close(
                    rx.button(
                        "Cancelar",
                        variant="soft",
                        color_scheme="gray",
                        on_click=State.close_save_modal,
                    ),
                ),
                rx.button(
                    rx.cond(
                        State.is_saving_analysis,
                        rx.hstack(
                            rx.spinner(size="1"),
                            "Salvando...",
                            spacing="2",
                        ),
                        rx.hstack(
                            rx.icon(tag="check", size=16),
                            "Salvar",
                            spacing="2",
                        ),
                    ),
                    on_click=State.save_current_analysis,
                    disabled=State.is_saving_analysis,
                    color_scheme="green",
                    cursor="pointer",
                ),
                spacing="3",
                justify="end",
                margin_top="4",
            ),
            
            style={
                "max_width": "450px",
                "background": Color.BACKGROUND_CARD,
            },
        ),
        open=State.is_save_modal_open,
    )


def saved_analyses_list() -> rx.Component:
    """
    Lista de análises salvas anteriormente.
    Permite carregar ou deletar.
    """
    from ..state import State
    
    def analysis_card(analysis: dict) -> rx.Component:
        """Card individual para cada análise salva"""
        return rx.card(
            rx.hstack(
                # Info principal
                rx.vstack(
                    rx.hstack(
                        rx.icon(tag="file-text", size=16, color=Color.PRIMARY),
                        rx.text(
                            analysis["analysis_name"],
                            size="2",
                            weight="bold",
                            color=Color.TEXT_PRIMARY,
                        ),
                        spacing="2",
                        align="center",
                    ),
                    rx.hstack(
                        rx.text(
                            analysis["formatted_date"],
                            size="1",
                            color=Color.TEXT_LIGHT,
                        ),
                        rx.text("•", color=Color.TEXT_LIGHT),
                        rx.text(
                            analysis["formatted_difference"],
                            size="1",
                            weight="medium",
                            color=rx.cond(
                                analysis["difference"].to(float) > 0,
                                Color.SUCCESS,
                                Color.ERROR,
                            ),
                        ),
                        spacing="2",
                    ),
                    align_items="start",
                    spacing="1",
                ),
                
                # Ações
                rx.hstack(
                    rx.icon_button(
                        rx.icon(tag="download", size=14),
                        size="1",
                        variant="ghost",
                        color_scheme="blue",
                        on_click=lambda: State.load_saved_analysis(analysis["id"]),
                        title="Carregar análise",
                    ),
                    rx.icon_button(
                        rx.icon(tag="trash-2", size=14),
                        size="1",
                        variant="ghost",
                        color_scheme="red",
                        on_click=lambda: State.delete_saved_analysis(analysis["id"]),
                        title="Deletar análise",
                    ),
                    spacing="1",
                ),
                
                justify="between",
                align="center",
                width="100%",
            ),
            variant="surface",
            size="1",
        )
    
    return rx.box(
        rx.vstack(
            # Header
            rx.hstack(
                rx.icon(tag="history", size=20, color=Color.PRIMARY),
                rx.text("Análises Salvas", size="3", weight="bold", color=Color.TEXT_PRIMARY),
                rx.spacer(),
                rx.icon_button(
                    rx.icon(tag="refresh-cw", size=14),
                    size="1",
                    variant="ghost",
                    on_click=State.load_saved_analyses,
                    loading=State.is_loading_saved_analyses,
                ),
                spacing="2",
                align="center",
                width="100%",
            ),
            
            # Lista ou placeholder
            rx.cond(
                State.saved_analyses_list.length() > 0,
                rx.vstack(
                    rx.foreach(State.saved_analyses_list, analysis_card),
                    spacing="2",
                    width="100%",
                ),
                rx.center(
                    rx.vstack(
                        rx.icon(tag="inbox", size=32, color=Color.TEXT_LIGHT),
                        rx.text(
                            "Nenhuma análise salva",
                            size="2",
                            color=Color.TEXT_LIGHT,
                        ),
                        rx.text(
                            "Execute uma análise e clique em 'Salvar'",
                            size="1",
                            color=Color.TEXT_LIGHT,
                        ),
                        align="center",
                        spacing="1",
                    ),
                    padding="6",
                ),
            ),
            
            spacing="3",
            width="100%",
        ),
        padding="4",
        border_radius="var(--radius-3)",
        background=Color.BACKGROUND_CARD,
        width="100%",
    )


def save_analysis_button() -> rx.Component:
    """Botão compacto para salvar análise (para usar em toolbars)"""
    from ..state import State
    
    return rx.tooltip(
        rx.icon_button(
            rx.icon(tag="save", size=18),
            size="2",
            variant="soft",
            color_scheme="green",
            on_click=State.open_save_modal,
            disabled=~State.has_analysis,
        ),
        content="Salvar esta análise",
    )
