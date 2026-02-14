"""Aba Outros Registros - Controle de Qualidade por área laboratorial."""
import reflex as rx
from ...state import State
from ...styles import Color, Design, Typography, Spacing
from ...components import ui
from .hemato_qc_tab import hemato_qc_intervalo_tab


AREAS = [
    ("hematologia", "Hematologia", "droplets"),
    ("imunologia", "Imunologia", "shield"),
    ("parasitologia", "Parasitologia", "bug"),
    ("microbiologia", "Microbiologia", "microscope"),
    ("uroanalise", "Uroanálise", "test_tube"),
]

# Parâmetros da tabela de Hematologia
_HEMATO_PARAMS = [
    "Hemácias",
    "Hematócrito",
    "Hemoglobina",
    "Leucócitos",
    "Plaquetas",
    "Rdw",
    "Vpm",
]

# Mapeamento parâmetro -> (bio, pad, ci_min, ci_max, ci_pct)
_HEMATO_FIELDS = {
    "Hemácias":     ("hemato_bio_hemacias",     "hemato_pad_hemacias",     "hemato_ci_min_hemacias",     "hemato_ci_max_hemacias",     "hemato_ci_pct_hemacias"),
    "Hematócrito":  ("hemato_bio_hematocrito",   "hemato_pad_hematocrito",   "hemato_ci_min_hematocrito",   "hemato_ci_max_hematocrito",   "hemato_ci_pct_hematocrito"),
    "Hemoglobina":  ("hemato_bio_hemoglobina",   "hemato_pad_hemoglobina",   "hemato_ci_min_hemoglobina",   "hemato_ci_max_hemoglobina",   "hemato_ci_pct_hemoglobina"),
    "Leucócitos":   ("hemato_bio_leucocitos",    "hemato_pad_leucocitos",    "hemato_ci_min_leucocitos",    "hemato_ci_max_leucocitos",    "hemato_ci_pct_leucocitos"),
    "Plaquetas":    ("hemato_bio_plaquetas",     "hemato_pad_plaquetas",     "hemato_ci_min_plaquetas",     "hemato_ci_max_plaquetas",     "hemato_ci_pct_plaquetas"),
    "Rdw":          ("hemato_bio_rdw",           "hemato_pad_rdw",           "hemato_ci_min_rdw",           "hemato_ci_max_rdw",           "hemato_ci_pct_rdw"),
    "Vpm":          ("hemato_bio_vpm",           "hemato_pad_vpm",           "hemato_ci_min_vpm",           "hemato_ci_max_vpm",           "hemato_ci_pct_vpm"),
}


def _area_button(label: str, icon: str, area_id: str) -> rx.Component:
    """Botão de seleção de área laboratorial."""
    is_active = State.outros_registros_area == area_id

    return rx.button(
        rx.hstack(
            rx.icon(tag=icon, size=18),
            rx.text(label, font_size=Typography.SMALL["font_size"], font_weight="500"),
            style={"gap": Spacing.XS},
            align_items="center",
        ),
        on_click=State.set_outros_registros_area(area_id),
        bg=rx.cond(is_active, Color.PRIMARY, "transparent"),
        color=rx.cond(is_active, Color.WHITE, Color.TEXT_SECONDARY),
        border_radius=Design.RADIUS_MD,
        padding_x=Spacing.MD,
        padding_y=Spacing.SM,
        border=rx.cond(is_active, f"1px solid {Color.PRIMARY}", f"1px solid {Color.BORDER}"),
        _hover={
            "bg": rx.cond(is_active, Color.PRIMARY_HOVER, Color.SURFACE_ALT),
            "color": rx.cond(is_active, Color.WHITE, Color.TEXT_PRIMARY),
        },
        transition="all 0.15s ease",
    )


def _area_content(area_id: str, label: str) -> rx.Component:
    """Conteúdo placeholder de cada área (exceto hematologia)."""
    return rx.cond(
        State.outros_registros_area == area_id,
        rx.box(
            rx.vstack(
                rx.center(
                    rx.vstack(
                        rx.icon(tag="clipboard_list", size=48, color=Color.TEXT_SECONDARY, opacity="0.4"),
                        rx.text(
                            f"Registros de {label}",
                            font_size=Typography.H3["font_size"],
                            font_weight="600",
                            color=Color.TEXT_PRIMARY,
                        ),
                        rx.text(
                            "Em breve: registros de controle de qualidade desta área.",
                            font_size=Typography.SMALL["font_size"],
                            color=Color.TEXT_SECONDARY,
                        ),
                        spacing="3",
                        align_items="center",
                        padding_y=Spacing.XXL,
                    ),
                ),
                width="100%",
            ),
            width="100%",
            bg=Color.SURFACE,
            border=f"1px solid {Color.BORDER}",
            border_radius=Design.RADIUS_XL,
            padding=Spacing.LG,
        ),
    )


# ---------------------------------------------------------------------------
# Hematologia - Tabela de entrada (Biodiagnostico x Padrão)
# ---------------------------------------------------------------------------

_CELL_INPUT_STYLE = {
    "border": f"1px solid {Color.BORDER}",
    "border_radius": Design.RADIUS_SM,
    "padding": f"{Spacing.XS} {Spacing.SM}",
    "min_height": "36px",
    "bg": Color.SURFACE,
    "color": Color.TEXT_PRIMARY,
    "font_size": Typography.SMALL["font_size"],
    "width": "100%",
    "_focus": {
        "border_color": Color.PRIMARY,
        "box_shadow": f"0 0 0 2px {Color.FOCUS_RING}",
        "outline": "none",
    },
}

_HEADER_CELL_STYLE = {
    "font_size": Typography.H5["font_size"],
    "font_weight": "700",
    "color": Color.DEEP,
    "text_align": "center",
    "padding": f"{Spacing.SM} {Spacing.MD}",
}

_LABEL_CELL_STYLE = {
    "font_size": Typography.SMALL["font_size"],
    "font_weight": "600",
    "color": Color.TEXT_PRIMARY,
    "padding": f"{Spacing.XS} {Spacing.SM}",
    "white_space": "nowrap",
}


def _hemato_input(state_var, setter_name: str, placeholder: str = "") -> rx.Component:
    """Input compacto para célula da tabela."""
    return rx.input(
        value=state_var,
        on_change=getattr(State, f"set_{setter_name}"),
        placeholder=placeholder,
        **_CELL_INPUT_STYLE,
    )


def _status_badge(status_var) -> rx.Component:
    """Badge de status interativo (OK/FORA) baseado em uma var de string."""
    return rx.cond(
        status_var != "",
        rx.badge(
            status_var,
            color_scheme=rx.cond(status_var == "OK", "green", "red"),
            size="1",
            variant="solid",
        ),
    )


def _hemato_param_row(param: str, idx: int) -> rx.Component:
    """Linha da tabela para um parâmetro de hematologia com status interativo."""
    bio_field, pad_field, ci_min_field, ci_max_field, ci_pct_field = _HEMATO_FIELDS[param]
    status = State.hemato_ci_status_list[idx]
    calc_range = State.hemato_ci_range_list[idx]

    return rx.table.row(
        rx.table.cell(
            rx.text(param, **_LABEL_CELL_STYLE),
        ),
        rx.table.cell(
            _hemato_input(getattr(State, bio_field), bio_field, "—"),
        ),
        rx.table.cell(
            rx.text(param, **_LABEL_CELL_STYLE),
        ),
        rx.table.cell(
            rx.cond(
                State.hemato_ci_mode == "bio",
                _hemato_input(getattr(State, pad_field), pad_field, "—"),
                rx.cond(
                    State.hemato_ci_mode == "intervalo",
                    # Intervalo: Min + Max + Status
                    rx.hstack(
                        _hemato_input(getattr(State, ci_min_field), ci_min_field, "Mín"),
                        _hemato_input(getattr(State, ci_max_field), ci_max_field, "Máx"),
                        _status_badge(status),
                        spacing="1", width="100%", align_items="center",
                    ),
                    # Porcentagem: Alvo (pad) + ±% + Status + Range calculado
                    rx.vstack(
                        rx.hstack(
                            rx.box(
                                _hemato_input(getattr(State, pad_field), pad_field, "Alvo"),
                                flex="1",
                                min_width="80px",
                            ),
                            rx.hstack(
                                rx.text("±", font_size=Typography.SMALL["font_size"], color=Color.TEXT_SECONDARY, flex_shrink="0"),
                                rx.box(
                                    _hemato_input(getattr(State, ci_pct_field), ci_pct_field, "%"),
                                    min_width="60px",
                                    width="70px",
                                ),
                                rx.text("%", font_size=Typography.SMALL["font_size"], color=Color.TEXT_SECONDARY, flex_shrink="0"),
                                spacing="1", align_items="center", flex_shrink="0",
                            ),
                            _status_badge(status),
                            spacing="2", width="100%", align_items="center",
                        ),
                        rx.cond(
                            calc_range != "",
                            rx.text(
                                calc_range,
                                font_size="11px",
                                color=Color.TEXT_SECONDARY,
                                font_style="italic",
                            ),
                        ),
                        spacing="1", width="100%",
                    ),
                ),
            ),
        ),
        _hover={"bg": Color.SURFACE_ALT},
    )


def _ci_mode_button(label: str, icon: str, mode_id: str) -> rx.Component:
    """Botão de seleção de modo de comparação do Controle Interno."""
    is_active = State.hemato_ci_mode == mode_id
    return rx.button(
        rx.hstack(
            rx.icon(tag=icon, size=14),
            rx.text(label, font_size=Typography.SIZE_SM_XS, font_weight="500"),
            style={"gap": Spacing.XS},
            align_items="center",
        ),
        on_click=State.set_hemato_ci_mode(mode_id),
        bg=rx.cond(is_active, Color.PRIMARY_LIGHT, "transparent"),
        color=rx.cond(is_active, Color.PRIMARY, Color.TEXT_SECONDARY),
        border_radius=Design.RADIUS_SM,
        padding_x=Spacing.SM,
        padding_y=Spacing.XS,
        border=rx.cond(is_active, f"1px solid {Color.PRIMARY}30", "1px solid transparent"),
        _hover={"bg": Color.SURFACE_ALT, "color": Color.TEXT_PRIMARY},
        transition="all 0.15s ease",
        size="1",
    )


def _hemato_tabela_original() -> rx.Component:
    """Conteúdo da tabela Biodiagnostico x Controle Interno."""
    return rx.vstack(
        # Mensagens de feedback
        rx.cond(
            State.hemato_error_message != "",
            rx.box(
                rx.text(State.hemato_error_message, color=Color.ERROR, font_size=Typography.SMALL["font_size"]),
                bg=Color.ERROR_BG, padding=Spacing.SM, border_radius=Design.RADIUS_SM, width="100%",
            ),
        ),
        rx.cond(
            State.hemato_success_message != "",
            rx.box(
                rx.text(State.hemato_success_message, color=Color.SUCCESS, font_size=Typography.SMALL["font_size"]),
                bg=Color.SUCCESS_BG, padding=Spacing.SM, border_radius=Design.RADIUS_SM, width="100%",
            ),
        ),

        # Seletor de modo de comparação do Controle Interno
        rx.box(
            rx.hstack(
                rx.text("Modo do Controle Interno:", font_size=Typography.SMALL["font_size"], font_weight="600", color=Color.TEXT_SECONDARY),
                _ci_mode_button("Bio (dia anterior)", "git_compare_arrows", "bio"),
                _ci_mode_button("Intervalo de valor", "ruler", "intervalo"),
                _ci_mode_button("Porcentagem", "percent", "porcentagem"),
                spacing="2", align_items="center", flex_wrap="wrap",
            ),
            padding=Spacing.SM,
            bg=Color.SURFACE_ALT,
            border_radius=Design.RADIUS_MD,
            margin_bottom=Spacing.SM,
            width="100%",
        ),

        # Tabela principal
        rx.box(
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell(rx.text("Biodiagnostico", **_HEADER_CELL_STYLE), col_span=2),
                        rx.table.column_header_cell(rx.text("Controle Interno", **_HEADER_CELL_STYLE), col_span=2),
                        bg=Color.SURFACE_ALT,
                    ),
                ),
                rx.table.body(
                    *[_hemato_param_row(p, i) for i, p in enumerate(_HEMATO_PARAMS)],
                    rx.table.row(
                        rx.table.cell(rx.text("Lote:", **_LABEL_CELL_STYLE)),
                        rx.table.cell(_hemato_input(State.hemato_bio_registro, "hemato_bio_registro", "—")),
                        rx.table.cell(rx.text("Lote:", **_LABEL_CELL_STYLE)),
                        rx.table.cell(_hemato_input(State.hemato_pad_registro, "hemato_pad_registro", "—")),
                        _hover={"bg": Color.SURFACE_ALT},
                    ),
                    rx.table.row(
                        rx.table.cell(rx.text("Data:", **_LABEL_CELL_STYLE)),
                        rx.table.cell(rx.input(type="date", value=State.hemato_bio_data, on_change=State.set_hemato_bio_data, **_CELL_INPUT_STYLE)),
                        rx.table.cell(rx.text("Data:", **_LABEL_CELL_STYLE)),
                        rx.table.cell(rx.input(type="date", value=State.hemato_pad_data, on_change=State.set_hemato_pad_data, **_CELL_INPUT_STYLE)),
                        _hover={"bg": Color.SURFACE_ALT},
                    ),
                ),
                width="100%", variant="surface",
            ),
            width="100%", overflow_x="auto",
        ),

        # Botões de ação
        rx.hstack(
            rx.button(
                rx.hstack(rx.icon(tag="save", size=16), rx.text("Salvar", font_size=Typography.SMALL["font_size"], font_weight="600"), spacing="2", align_items="center"),
                on_click=State.save_hemato_record, bg=Color.PRIMARY, color=Color.WHITE,
                border_radius=Design.RADIUS_MD, padding_x=Spacing.LG, padding_y=Spacing.SM,
                _hover={"bg": Color.PRIMARY_HOVER}, loading=State.is_saving_hemato,
            ),
            rx.button(
                rx.hstack(rx.icon(tag="eraser", size=16), rx.text("Limpar", font_size=Typography.SMALL["font_size"], font_weight="600"), spacing="2", align_items="center"),
                on_click=State.clear_hemato_form, bg="transparent", color=Color.TEXT_SECONDARY,
                border=f"1px solid {Color.BORDER}", border_radius=Design.RADIUS_MD,
                padding_x=Spacing.LG, padding_y=Spacing.SM,
                _hover={"bg": Color.SURFACE_ALT, "color": Color.TEXT_PRIMARY},
            ),
            spacing="3", justify_content="flex-end", width="100%", padding_top=Spacing.MD,
        ),

        width="100%", spacing="4",
    )


def _hemato_sub_tab_button(label: str, icon: str, tab_id: str) -> rx.Component:
    """Botão de sub-aba dentro de Hematologia."""
    is_active = State.hemato_qc_sub_tab == tab_id
    return rx.button(
        rx.hstack(
            rx.icon(tag=icon, size=16),
            rx.text(label, font_size=Typography.SMALL["font_size"], font_weight="600"),
            style={"gap": Spacing.XS},
            align_items="center",
        ),
        on_click=State.set_hemato_qc_sub_tab(tab_id),
        bg=rx.cond(is_active, Color.PRIMARY_LIGHT, "transparent"),
        color=rx.cond(is_active, Color.PRIMARY, Color.TEXT_SECONDARY),
        border_radius=Design.RADIUS_MD,
        padding_x=Spacing.MD,
        padding_y=Spacing.SM,
        border=rx.cond(is_active, f"1px solid {Color.PRIMARY}40", f"1px solid {Color.BORDER}"),
        _hover={"bg": Color.SURFACE_ALT, "color": Color.TEXT_PRIMARY},
        transition="all 0.15s ease",
    )


def _hemato_bio_history() -> rx.Component:
    """Seção de histórico dos registros Bio x CI salvos."""
    return rx.vstack(
        rx.hstack(
            ui.heading("Histórico", level=3),
            rx.spacer(),
            rx.text(
                State.filtered_hemato_bio_records.length().to_string() + " registros",
                font_size=Typography.SIZE_SM,
                color=Color.TEXT_SECONDARY,
            ),
            width="100%",
            align_items="center",
        ),
        rx.cond(
            State.hemato_bio_records.length() > 0,
            rx.box(
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell(rx.text("DATA BIO", style=Typography.CAPTION, color=Color.TEXT_SECONDARY)),
                            rx.table.column_header_cell(rx.text("LOTE BIO", style=Typography.CAPTION, color=Color.TEXT_SECONDARY)),
                            rx.table.column_header_cell(rx.text("DATA CI", style=Typography.CAPTION, color=Color.TEXT_SECONDARY)),
                            rx.table.column_header_cell(rx.text("LOTE CI", style=Typography.CAPTION, color=Color.TEXT_SECONDARY)),
                            rx.table.column_header_cell(rx.text("MODO", style=Typography.CAPTION, color=Color.TEXT_SECONDARY)),
                            rx.table.column_header_cell(""),
                        ),
                    ),
                    rx.table.body(
                        rx.foreach(
                            State.filtered_hemato_bio_records,
                            lambda r: rx.table.row(
                                rx.table.cell(rx.text(r.data_bio, color=Color.TEXT_SECONDARY, font_size=Typography.H5["font_size"])),
                                rx.table.cell(rx.text(r.registro_bio, font_weight="600")),
                                rx.table.cell(rx.text(r.data_pad, color=Color.TEXT_SECONDARY, font_size=Typography.H5["font_size"])),
                                rx.table.cell(rx.text(r.registro_pad, font_weight="600")),
                                rx.table.cell(
                                    rx.badge(
                                        r.modo_ci,
                                        color_scheme=rx.cond(
                                            r.modo_ci == "bio", "blue",
                                            rx.cond(r.modo_ci == "intervalo", "purple", "orange"),
                                        ),
                                        size="1",
                                    ),
                                ),
                                rx.table.cell(
                                    rx.hstack(
                                        rx.tooltip(
                                            rx.button(
                                                rx.icon(tag="eye", size=14, color=Color.PRIMARY),
                                                on_click=lambda: State.open_hemato_bio_detail(r.id),
                                                variant="ghost", color_scheme="blue", size="1",
                                            ),
                                            content="Ver detalhes",
                                        ),
                                        rx.tooltip(
                                            rx.button(
                                                rx.icon(tag="trash_2", size=14, color=Color.ERROR),
                                                on_click=lambda: State.delete_hemato_bio_record(r.id),
                                                variant="ghost", color_scheme="red", size="1",
                                            ),
                                            content="Excluir",
                                        ),
                                        spacing="3",
                                    ),
                                ),
                            ),
                        ),
                    ),
                    width="100%",
                ),
                bg=Color.SURFACE,
                border=f"1px solid {Color.BORDER}",
                border_radius=Design.RADIUS_XL,
                box_shadow=Design.SHADOW_SM,
                overflow="hidden",
                width="100%",
                overflow_x="auto",
            ),
            rx.center(
                rx.vstack(
                    rx.icon(tag="database", size=32, color=Color.TEXT_SECONDARY, opacity=0.3),
                    ui.text("Nenhum registro salvo.", size="small", color=Color.TEXT_SECONDARY),
                    spacing="2",
                    align_items="center",
                ),
                bg=Color.SURFACE,
                border=f"1px solid {Color.BORDER}",
                border_radius=Design.RADIUS_XL,
                padding=Spacing.XL,
                width="100%",
            ),
        ),
        width="100%",
        spacing="3",
        margin_top=Spacing.XL,
    )


def _hemato_bio_detail_modal() -> rx.Component:
    """Modal para visualizar detalhes completos de um registro Bio x CI."""
    rec = State.selected_hemato_bio_record
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.hstack(
                    rx.icon(tag="file_text", size=22, color=Color.PRIMARY),
                    rx.text("Detalhes do Registro", font_weight="700", font_size=Typography.SIZE_XL),
                    spacing="2",
                    align_items="center",
                ),
            ),
            # Cabeçalho com informações gerais
            rx.box(
                rx.grid(
                    rx.vstack(
                        rx.text("Data Bio", font_size="11px", color=Color.TEXT_SECONDARY, font_weight="600"),
                        rx.text(rec.data_bio, font_weight="600", font_size=Typography.SMALL["font_size"]),
                        spacing="1",
                    ),
                    rx.vstack(
                        rx.text("Lote Bio", font_size="11px", color=Color.TEXT_SECONDARY, font_weight="600"),
                        rx.text(rec.registro_bio, font_weight="600", font_size=Typography.SMALL["font_size"]),
                        spacing="1",
                    ),
                    rx.vstack(
                        rx.text("Data CI", font_size="11px", color=Color.TEXT_SECONDARY, font_weight="600"),
                        rx.text(rec.data_pad, font_weight="600", font_size=Typography.SMALL["font_size"]),
                        spacing="1",
                    ),
                    rx.vstack(
                        rx.text("Lote CI", font_size="11px", color=Color.TEXT_SECONDARY, font_weight="600"),
                        rx.text(rec.registro_pad, font_weight="600", font_size=Typography.SMALL["font_size"]),
                        spacing="1",
                    ),
                    rx.vstack(
                        rx.text("Modo", font_size="11px", color=Color.TEXT_SECONDARY, font_weight="600"),
                        rx.badge(
                            rec.modo_ci,
                            color_scheme=rx.cond(
                                rec.modo_ci == "bio", "blue",
                                rx.cond(rec.modo_ci == "intervalo", "purple", "orange"),
                            ),
                            size="1",
                        ),
                        spacing="1",
                    ),
                    columns={"initial": "2", "sm": "3", "md": "5"},
                    spacing="3",
                    width="100%",
                ),
                bg=Color.BACKGROUND,
                border=f"1px solid {Color.BORDER}",
                border_radius=Design.RADIUS_MD,
                padding=Spacing.MD,
                margin_bottom=Spacing.MD,
            ),
            # Tabela de analitos
            rx.box(
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell(rx.text("ANALITO", style=Typography.CAPTION, color=Color.TEXT_SECONDARY)),
                            rx.table.column_header_cell(rx.text("BIO", style=Typography.CAPTION, color=Color.TEXT_SECONDARY)),
                            rx.table.column_header_cell(rx.text("CONTROLE INTERNO", style=Typography.CAPTION, color=Color.TEXT_SECONDARY)),
                            rx.table.column_header_cell(rx.text("STATUS", style=Typography.CAPTION, color=Color.TEXT_SECONDARY)),
                            bg=Color.SURFACE_ALT,
                        ),
                    ),
                    rx.table.body(
                        rx.foreach(
                            State.hemato_bio_detail_rows,
                            lambda row: rx.table.row(
                                rx.table.cell(
                                    rx.text(row[0], font_weight="600", font_size=Typography.SMALL["font_size"]),
                                ),
                                rx.table.cell(
                                    rx.text(row[1], font_size=Typography.SMALL["font_size"]),
                                ),
                                rx.table.cell(
                                    rx.text(row[2], font_size=Typography.SMALL["font_size"], color=Color.TEXT_SECONDARY),
                                ),
                                rx.table.cell(
                                    rx.cond(
                                        row[3] == "OK",
                                        rx.badge("OK", color_scheme="green", size="1", variant="solid"),
                                        rx.cond(
                                            row[3] == "FORA",
                                            rx.badge("FORA", color_scheme="red", size="1", variant="solid"),
                                            rx.text("—", color=Color.TEXT_SECONDARY, font_size=Typography.SMALL["font_size"]),
                                        ),
                                    ),
                                ),
                                _hover={"bg": Color.SURFACE_ALT},
                            ),
                        ),
                    ),
                    width="100%",
                    variant="surface",
                ),
                overflow_x="auto",
                width="100%",
            ),
            # Botão fechar
            rx.hstack(
                rx.dialog.close(
                    rx.button(
                        "Fechar",
                        variant="outline",
                        color_scheme="gray",
                    ),
                ),
                justify_content="flex-end",
                width="100%",
                margin_top=Spacing.MD,
            ),
            style={"max_width": "700px"},
        ),
        open=State.show_hemato_bio_detail,
        on_open_change=lambda _open: State.close_hemato_bio_detail(),
    )


def _hematologia_content() -> rx.Component:
    """Conteúdo da aba Hematologia com sub-abas: Tabela Bio x CI e CQ Intervalo/%."""
    return rx.cond(
        State.outros_registros_area == "hematologia",
        rx.box(
            rx.vstack(
                # Título
                rx.hstack(
                    rx.icon(tag="droplets", size=22, color=Color.PRIMARY),
                    rx.text("Hematologia", font_size=Typography.H3["font_size"], font_weight="600", color=Color.DEEP),
                    spacing="2",
                    align_items="center",
                ),

                # Sub-abas
                rx.box(
                    rx.hstack(
                        _hemato_sub_tab_button("Tabela Bio x CI", "table", "tabela"),
                        _hemato_sub_tab_button("CQ Intervalo / %", "settings", "cq_intervalo"),
                        spacing="2",
                        align_items="center",
                        flex_wrap="wrap",
                    ),
                    padding=Spacing.SM,
                    bg=Color.SURFACE_ALT,
                    border_radius=Design.RADIUS_MD,
                    width="100%",
                ),

                # Conteúdo condicional
                rx.cond(
                    State.hemato_qc_sub_tab == "tabela",
                    rx.vstack(
                        _hemato_tabela_original(),
                        _hemato_bio_history(),
                        width="100%",
                        spacing="2",
                    ),
                    hemato_qc_intervalo_tab(),
                ),

                # Modal de detalhes do registro
                _hemato_bio_detail_modal(),

                width="100%",
                spacing="4",
            ),
            width="100%",
            bg=Color.SURFACE,
            border=f"1px solid {Color.BORDER}",
            border_radius=Design.RADIUS_XL,
            padding=Spacing.LG,
        ),
    )


# ---------------------------------------------------------------------------
# Imunologia - Formulário + Histórico
# ---------------------------------------------------------------------------

def _imunologia_content() -> rx.Component:
    """Conteúdo da aba Imunologia com formulário e tabela de histórico."""
    return rx.cond(
        State.outros_registros_area == "imunologia",
        rx.box(
            rx.vstack(
                # Título
                rx.hstack(
                    rx.icon(tag="shield", size=22, color=Color.PRIMARY),
                    rx.text(
                        "Imunologia",
                        font_size=Typography.H3["font_size"],
                        font_weight="600",
                        color=Color.DEEP,
                    ),
                    spacing="2",
                    align_items="center",
                ),

                # Mensagens de feedback
                rx.cond(
                    State.imuno_error_message != "",
                    rx.callout(State.imuno_error_message, icon="triangle_alert", color_scheme="red", width="100%"),
                ),
                rx.cond(
                    State.imuno_success_message != "",
                    rx.callout(State.imuno_success_message, icon="circle_check", color_scheme="green", width="100%"),
                ),

                # Formulário
                ui.card(
                    rx.vstack(
                        rx.grid(
                            ui.form_field(
                                "Controle",
                                ui.input(
                                    placeholder="Ex: HBSAG 00942025",
                                    value=State.imuno_controle,
                                    on_change=State.set_imuno_controle,
                                ),
                                required=True,
                            ),
                            ui.form_field(
                                "Fabricante",
                                ui.input(
                                    placeholder="Ex: InVitro",
                                    value=State.imuno_fabricante,
                                    on_change=State.set_imuno_fabricante,
                                ),
                            ),
                            ui.form_field(
                                "Lote",
                                ui.input(
                                    placeholder="Ex: 7010/24",
                                    value=State.imuno_lote,
                                    on_change=State.set_imuno_lote,
                                ),
                            ),
                            ui.form_field(
                                "Data",
                                ui.input(
                                    type="date",
                                    value=State.imuno_data,
                                    on_change=State.set_imuno_data,
                                ),
                            ),
                            columns={"initial": "1", "sm": "2", "md": "4"},
                            spacing="3",
                            width="100%",
                        ),
                        ui.form_field(
                            "Resultado",
                            ui.input(
                                placeholder="Informe o resultado",
                                value=State.imuno_resultado,
                                on_change=State.set_imuno_resultado,
                            ),
                            required=True,
                        ),
                        # Botões de ação
                        rx.hstack(
                            ui.button("Limpar", icon="eraser", on_click=State.clear_imuno_form, variant="secondary"),
                            ui.button("Salvar Registro", icon="save", is_loading=State.is_saving_imuno, on_click=State.save_imuno_record),
                            spacing="3",
                            width="100%",
                            justify_content="flex-end",
                        ),
                        width="100%",
                        spacing="3",
                    ),
                    width="100%",
                    padding=Spacing.MD,
                ),

                # ── Histórico ──
                rx.box(
                    rx.vstack(
                        rx.hstack(
                            ui.heading("Histórico", level=3),
                            rx.spacer(),
                            rx.text(
                                State.filtered_imuno_records.length().to_string() + " registros",
                                font_size=Typography.SIZE_SM,
                                color=Color.TEXT_SECONDARY,
                            ),
                            width="100%",
                            align_items="center",
                        ),
                        # Barra de busca
                        rx.hstack(
                            rx.box(
                                rx.input(
                                    placeholder="Buscar controle...",
                                    value=State.imuno_search_term,
                                    on_change=State.set_imuno_search_term,
                                    size="2",
                                    width="100%",
                                    max_width="280px",
                                ),
                                rx.icon(
                                    tag="search", size=16, color=Color.TEXT_SECONDARY,
                                    position="absolute", right="10px", top="50%",
                                    transform="translateY(-50%)", pointer_events="none",
                                ),
                                position="relative", flex="1", max_width="280px",
                            ),
                            width="100%", align_items="center", gap="3", flex_wrap="wrap",
                            margin_bottom=Spacing.SM,
                        ),
                        # Tabela
                        rx.cond(
                            State.imuno_records.length() > 0,
                            rx.box(
                                rx.table.root(
                                    rx.table.header(
                                        rx.table.row(
                                            rx.table.column_header_cell(rx.text("DATA", style=Typography.CAPTION, color=Color.TEXT_SECONDARY)),
                                            rx.table.column_header_cell(rx.text("CONTROLE", style=Typography.CAPTION, color=Color.TEXT_SECONDARY)),
                                            rx.table.column_header_cell(rx.text("FABRICANTE", style=Typography.CAPTION, color=Color.TEXT_SECONDARY)),
                                            rx.table.column_header_cell(rx.text("LOTE", style=Typography.CAPTION, color=Color.TEXT_SECONDARY)),
                                            rx.table.column_header_cell(rx.text("RESULTADO", style=Typography.CAPTION, color=Color.TEXT_SECONDARY)),
                                            rx.table.column_header_cell(""),
                                        ),
                                    ),
                                    rx.table.body(
                                        rx.foreach(
                                            State.filtered_imuno_records,
                                            lambda r: rx.table.row(
                                                rx.table.cell(rx.text(r.data, color=Color.TEXT_SECONDARY, font_size=Typography.H5["font_size"])),
                                                rx.table.cell(rx.text(r.controle, font_weight="600")),
                                                rx.table.cell(rx.text(r.fabricante)),
                                                rx.table.cell(rx.text(r.lote)),
                                                rx.table.cell(rx.text(r.resultado, font_weight="600")),
                                                rx.table.cell(
                                                    rx.tooltip(
                                                        rx.button(
                                                            rx.icon(tag="trash_2", size=14, color=Color.ERROR),
                                                            on_click=lambda: State.delete_imuno_record(r.id),
                                                            variant="ghost", color_scheme="red", size="1",
                                                            aria_label="Excluir registro",
                                                        ),
                                                        content="Excluir",
                                                    ),
                                                    text_align="right",
                                                ),
                                            ),
                                        ),
                                    ),
                                    width="100%",
                                ),
                                bg=Color.SURFACE,
                                border=f"1px solid {Color.BORDER}",
                                border_radius=Design.RADIUS_XL,
                                box_shadow=Design.SHADOW_SM,
                                overflow="hidden",
                                width="100%",
                                overflow_x="auto",
                            ),
                            rx.center(
                                rx.vstack(
                                    rx.icon(tag="database", size=32, color=Color.TEXT_SECONDARY, opacity=0.3),
                                    ui.text("Nenhum registro encontrado.", size="small", color=Color.TEXT_SECONDARY),
                                    spacing="2",
                                    align_items="center",
                                ),
                                bg=Color.SURFACE,
                                border=f"1px solid {Color.BORDER}",
                                border_radius=Design.RADIUS_XL,
                                padding=Spacing.XL,
                                width="100%",
                            ),
                        ),
                        # Navegação por dia
                        rx.hstack(
                            rx.button(
                                rx.icon(tag="chevron_left", size=16),
                                on_click=State.prev_imuno_day,
                                variant="outline", size="1",
                                aria_label="Dia anterior",
                            ),
                            rx.input(
                                type="date",
                                value=State.imuno_history_date,
                                on_change=State.set_imuno_history_date,
                                size="2",
                                width="160px",
                            ),
                            rx.button(
                                rx.icon(tag="chevron_right", size=16),
                                on_click=State.next_imuno_day,
                                variant="outline", size="1",
                                aria_label="Próximo dia",
                            ),
                            justify_content="center",
                            align_items="center",
                            style={"gap": Spacing.SM},
                            width="100%",
                            margin_top=Spacing.MD,
                        ),
                        width="100%",
                    ),
                    width="100%",
                    margin_top=Spacing.XL,
                ),

                width="100%",
                spacing="4",
            ),
            width="100%",
            bg=Color.SURFACE,
            border=f"1px solid {Color.BORDER}",
            border_radius=Design.RADIUS_XL,
            padding=Spacing.LG,
        ),
    )


def outros_registros_tab() -> rx.Component:
    """Aba Outros Registros com sub-menu por área laboratorial."""
    return rx.vstack(
        # Header
        rx.vstack(
            rx.text(
                "Outros Registros",
                font_size=Typography.H2["font_size"],
                font_weight="700",
                color=Color.DEEP,
            ),
            rx.text(
                "Controle de qualidade por área laboratorial",
                font_size=Typography.BODY_SECONDARY["font_size"],
                color=Color.TEXT_SECONDARY,
            ),
            spacing="1",
            align_items="center",
            width="100%",
        ),

        # Menu de áreas
        rx.box(
            rx.hstack(
                *[_area_button(label, icon, area_id) for area_id, label, icon in AREAS],
                spacing="2",
                justify_content="center",
                width="100%",
                flex_wrap="wrap",
            ),
            width="100%",
            padding_y=Spacing.MD,
        ),

        # Conteúdo da área ativa
        _hematologia_content(),
        _imunologia_content(),
        *[_area_content(area_id, label) for area_id, label, _ in AREAS if area_id not in ("hematologia", "imunologia")],

        width="100%",
        spacing="4",
        padding_bottom=Spacing.XXL,
    )
