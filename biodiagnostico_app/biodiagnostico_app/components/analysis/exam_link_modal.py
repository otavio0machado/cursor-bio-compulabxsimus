"""
Modal para vincular exames SIMUS -> COMPULAB
Permite cadastrar sinônimos e reprocessar a análise
"""
import reflex as rx
from ...state import State
from ...styles import Color, Design


def exam_link_modal() -> rx.Component:
    """Modal premium para vincular exames entre sistemas"""
    def render_mapping_row(item: dict) -> rx.Component:
        return rx.hstack(
            rx.text(item.get("original_name", ""), size="1", color=Color.TEXT_PRIMARY, flex="1"),
            rx.icon("arrow-right", size=14, color=Color.TEXT_SECONDARY),
            rx.text(item.get("canonical_name", ""), size="1", weight="medium", color=Color.DEEP, flex="1"),
            spacing="2",
            width="100%",
        )

    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                rx.icon(tag="link-2", size=18),
                "Linkar Exames",
                variant="soft",
                color_scheme="blue",
                cursor="pointer",
                on_click=State.open_link_modal,
            )
        ),
        rx.dialog.content(
            rx.dialog.title(
                rx.hstack(
                    rx.icon(tag="link-2", size=22, color=Color.PRIMARY),
                    "Linkar Exames (SIMUS -> COMPULAB)",
                    spacing="2",
                    align="center",
                ),
            ),
            rx.dialog.description(
                "Defina equival\u00eancias entre nomes dos exames para reduzir pend\u00eancias e alinhar os sistemas.",
                size="2",
                color_scheme="gray",
            ),
            rx.vstack(
                rx.grid(
                    rx.vstack(
                        rx.text("Exame no SIMUS", size="2", weight="medium", color=Color.TEXT_SECONDARY),
                        rx.input(
                            placeholder="Ex: G.O.T., TGO, TRANSAMINASE...",
                            value=State.link_simus_exam,
                            on_change=State.set_link_simus_exam,
                            size="3",
                            width="100%",
                        ),
                        rx.cond(
                            State.simus_exam_names.length() > 0,
                            rx.select(
                                State.simus_exam_names,
                                placeholder="Selecionar do SIMUS (opcional)",
                                value=State.link_simus_exam,
                                on_change=State.set_link_simus_exam,
                                width="100%",
                            ),
                            rx.fragment(),
                        ),
                        spacing="2",
                        width="100%",
                    ),
                    rx.vstack(
                        rx.text("Exame no COMPULAB", size="2", weight="medium", color=Color.TEXT_SECONDARY),
                        rx.input(
                            placeholder="Ex: GOT, HEMOGRAMA...",
                            value=State.link_compulab_exam,
                            on_change=State.set_link_compulab_exam,
                            size="3",
                            width="100%",
                        ),
                        rx.cond(
                            State.compulab_exam_names.length() > 0,
                            rx.select(
                                State.compulab_exam_names,
                                placeholder="Selecionar do COMPULAB (opcional)",
                                value=State.link_compulab_exam,
                                on_change=State.set_link_compulab_exam,
                                width="100%",
                            ),
                            rx.fragment(),
                        ),
                        spacing="2",
                        width="100%",
                    ),
                    columns={"initial": "1", "md": "2"},
                    spacing="5",
                    width="100%",
                ),
                rx.cond(
                    State.link_message != "",
                    rx.callout(
                        State.link_message,
                        icon="info",
                        size="1",
                        width="100%",
                    ),
                    rx.fragment(),
                ),
                rx.box(
                    rx.hstack(
                        rx.text("Mapeamentos Atuais", weight="bold", color=Color.DEEP, size="2"),
                        rx.spacer(),
                        rx.input(
                            placeholder="Buscar...",
                            value=State.mapping_search,
                            on_change=State.set_mapping_search,
                            size="2",
                            width="200px",
                        ),
                        align_items="center",
                        width="100%",
                    ),
                    rx.cond(
                        State.is_loading_mappings,
                        rx.hstack(
                            rx.spinner(size="1"),
                            rx.text("Carregando mapeamentos...", size="1", color=Color.TEXT_SECONDARY),
                            spacing="2",
                        ),
                        rx.cond(
                            State.mapping_rows.length() > 0,
                            rx.scroll_area(
                                rx.vstack(
                                    rx.foreach(State.mapping_rows, render_mapping_row),
                                    spacing="2",
                                    width="100%",
                                ),
                                type="auto",
                                scrollbars="vertical",
                                style={"max_height": "220px"},
                            ),
                            rx.box(
                                rx.text("Nenhum mapeamento cadastrado ainda.", size="1", color=Color.TEXT_SECONDARY),
                                padding="12px",
                            ),
                        ),
                    ),
                    margin_top="8px",
                    padding="12px",
                    bg="rgba(255,255,255,0.6)",
                    border=f"1px solid {Color.BORDER}",
                    border_radius=Design.RADIUS_LG,
                    width="100%",
                ),
                rx.hstack(
                    rx.button(
                        rx.hstack(rx.icon(tag="download", size=16), "Exportar JSON", spacing="2"),
                        on_click=State.export_mappings,
                        variant="soft",
                        color_scheme="blue",
                        cursor="pointer",
                    ),
                    rx.upload(
                        rx.button(
                            rx.cond(
                                State.is_importing_mappings,
                                rx.hstack(rx.spinner(size="1"), "Importando...", spacing="2"),
                                rx.hstack(rx.icon(tag="cloud-upload", size=16), "Importar JSON", spacing="2"),
                            ),
                            variant="soft",
                            color_scheme="gray",
                            cursor="pointer",
                        ),
                        id="mapping_import",
                        multiple=False,
                        accept={"application/json": [".json"]},
                        max_files=1,
                        on_drop=State.import_mappings(rx.upload_files(upload_id="mapping_import")),
                        border="none",
                        padding="0",
                    ),
                    spacing="3",
                    width="100%",
                ),
                spacing="4",
                width="100%",
                padding_y="2",
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button(
                        "Fechar",
                        variant="soft",
                        color_scheme="gray",
                        on_click=State.close_link_modal,
                    ),
                ),
                rx.button(
                    rx.cond(
                        State.is_linking,
                        rx.hstack(rx.spinner(size="1"), "Salvando...", spacing="2"),
                        rx.hstack(rx.icon(tag="link-2", size=16), "Salvar Link", spacing="2"),
                    ),
                    on_click=State.create_exam_link,
                    disabled=State.is_linking,
                    color_scheme="blue",
                    cursor="pointer",
                ),
                rx.button(
                    rx.hstack(rx.icon(tag="link-2", size=16), "Salvar e Reprocessar", spacing="2"),
                    on_click=State.create_exam_link_and_reprocess,
                    disabled=State.is_linking,
                    variant="soft",
                    color_scheme="green",
                    cursor="pointer",
                ),
                rx.button(
                    rx.hstack(rx.icon(tag="refresh-cw", size=16), "Reprocessar An\u00e1lise", spacing="2"),
                    on_click=State.run_analysis,
                    disabled=~State.has_files | State.is_analyzing,
                    variant="soft",
                    color_scheme="green",
                ),
                spacing="3",
                justify="end",
                margin_top="4",
            ),
            style={
                "max_width": "720px",
                "background": Color.SURFACE,
            },
        ),
        open=State.is_link_modal_open,
    )
