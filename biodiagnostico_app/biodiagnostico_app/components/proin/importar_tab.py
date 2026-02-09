import reflex as rx
from ...state import State
from ...styles import Color, Design, Typography, Spacing
from ...components import ui
from .helpers import format_cv, qc_status_label, qc_status_kind


def importar_tab() -> rx.Component:
    """Aba de Importação de planilha Excel (Purificada)"""
    return rx.vstack(
        rx.vstack(
            ui.heading("Importação de Dados", level=2),
            ui.text("Importe registros em massa via planilha Excel (.xlsx)", size="small", color=Color.TEXT_SECONDARY),
            spacing="1", align_items="start", margin_bottom=Spacing.LG, width="100%"
        ),

        ui.card(
            rx.vstack(
                rx.cond(
                    State.is_importing,
                    rx.vstack(
                        rx.spinner(size="3", color=Color.PRIMARY),
                        ui.text("Processando arquivo...", size="small"),
                        rx.progress(value=State.upload_progress, max=100, width="100%", height="8px", color_scheme="blue", margin_top=Spacing.SM),
                        spacing="2", align_items="center", width="100%"
                    ),
                    rx.vstack(
                        rx.upload(
                            rx.vstack(
                                rx.icon(tag="upload", size=32, color=Color.PRIMARY),
                                ui.text("Arraste o arquivo .xlsx aqui ou clique para selecionar", size="body"),
                                ui.text("Formatos aceitos: .xlsx, .xls", size="small", color=Color.TEXT_SECONDARY),
                                spacing="2", align_items="center"
                            ),
                            id="proin_upload",
                            multiple=False,
                            accept={
                                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"],
                                "application/vnd.ms-excel": [".xls"]
                            },
                            on_drop=State.handle_proin_upload(rx.upload_files(upload_id="proin_upload")),
                            border=f"2px dashed {Color.BORDER}",
                            padding=Spacing.XL,
                            border_radius=Design.RADIUS_XL,
                            _hover={"bg": Color.PRIMARY_LIGHT, "border_color": Color.PRIMARY},
                            width="100%"
                        ),
                        ui.button("Processar Seleção", icon="file_spreadsheet", on_click=State.handle_proin_upload(rx.upload_files(upload_id="proin_upload")), variant="secondary", margin_top=Spacing.MD),
                        spacing="2", align_items="center", width="100%"
                    )
                ),
                max_width="3xl", margin_x="auto", width="100%"
            )
        ),

        # Feedback e Preview
        rx.cond(
            State.proin_import_preview.length() > 0,
            rx.vstack(
                rx.hstack(
                    ui.heading("Prévia da Importação", level=3),
                    rx.spacer(),
                    ui.button("Importar Todos", icon="check_check", on_click=State.process_proin_import, variant="primary"),
                    ui.button("Cancelar", icon="x", on_click=State.clear_proin_import, variant="ghost", color_scheme="red"),
                    width="100%", align_items="center", margin_bottom=Spacing.MD
                ),
                rx.box(
                    rx.scroll_area(
                        rx.table.root(
                            rx.table.header(
                                rx.table.row(
                                    rx.foreach(State.proin_import_headers, lambda h: rx.table.column_header_cell(rx.text(h, style=Typography.CAPTION, color=Color.TEXT_SECONDARY), bg=Color.BACKGROUND)),
                                )
                            ),
                            rx.table.body(
                                rx.foreach(
                                    State.proin_import_preview,
                                    lambda row: rx.table.row(
                                        rx.foreach(row, lambda cell: rx.table.cell(rx.text(cell, font_size=Typography.H5["font_size"])))
                                    )
                                )
                            ), width="100%"
                        ),
                        style={"max_height": "400px"}
                    ),
                    bg=Color.SURFACE, border=f"1px solid {Color.BORDER}", border_radius=Design.RADIUS_XL, box_shadow=Design.SHADOW_SM, overflow="hidden", width="100%"
                ),
                width="100%", margin_top=Spacing.LG
            )
        ),
        width="100%", padding_bottom=Spacing.XL
    )
