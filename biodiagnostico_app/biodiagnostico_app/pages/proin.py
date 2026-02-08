"""
ProIn QC - Sistema de Controle de Qualidade Laboratorial
Funcionalidades:
- Dashboard com estatísticas e alertas
- Registro de CQ simplificado com cálculo automático de CV%
- Gestão de Reagentes/Lotes com controle de validade
- Gráfico Levey-Jennings para auditorias
- Importação de planilhas Excel
"""
import reflex as rx
from ..state import State
from ..styles import Color, Design, Typography, Spacing
from ..components import ui


def format_cv(value) -> rx.Var:
    """Format CV with two decimal places and comma separator."""
    value_var = rx.Var.create(value).to(float)
    return rx.Var.create(f"{value_var:.2f}").replace(".", ",")


def qc_status_label(status, cv, cv_max) -> rx.Var:
    """Status exibido baseado APENAS no status salvo no banco (Westgard + CV ja avaliados ao salvar)."""
    status_var = rx.Var.create(status)
    return status_var


def qc_status_kind(status, cv, cv_max) -> rx.Var:
    """Tipo visual do status baseado APENAS no status salvo no banco."""
    status_var = rx.Var.create(status)
    return rx.cond(
        status_var == "OK",
        "success",
        rx.cond(status_var.contains("ALERTA"), "warning", "error")
    )


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


def dashboard_tab() -> rx.Component:
    """Aba Dashboard - Visão geral (Purificada)"""
    return rx.vstack(
        # Header with Refresh Button
        rx.hstack(
            rx.vstack(
                ui.heading("Visão Geral", level=2),
                ui.text("Monitoramento de qualidade e pendências", size="small", color=Color.TEXT_SECONDARY),
                spacing="1", align_items="start",
            ),
            rx.spacer(),
            rx.button(
                rx.hstack(
                    rx.icon(tag="refresh_cw", size=18),
                    rx.text("Atualizar", display=["none", "none", "block"]),
                    style={"gap": Spacing.SM},
                ),
                on_click=State.load_data_from_db(True),
                variant="ghost", size="2", color=Color.TEXT_SECONDARY,
                _hover={"bg": Color.PRIMARY_LIGHT, "color": Color.DEEP},
                border_radius=Design.RADIUS_LG,
                aria_label="Atualizar dados"
            ),
            width="100%", align_items="center", margin_bottom=Spacing.LG, max_width="6xl", margin_x="auto"
        ),
        
        # Grid de KPI Cards - Responsivo
        rx.box(
            rx.grid(
                ui.stat_card("Registros Hoje", State.dashboard_total_today, "clipboard-list", "info"),
                ui.stat_card("Registros do Mês", State.dashboard_total_month, "calendar", "success"),
                ui.stat_card("Taxa de Aprovação", State.dashboard_approval_rate.to_string() + "%", "circle-check", "success", "CV ≤ 5%"),
                rx.cond(
                    State.has_alerts,
                    ui.stat_card("Alertas CV > 5%", State.dashboard_alerts_count, "triangle-alert", "error"),
                    ui.stat_card("Sem Alertas", "0", "sparkles", "success")
                ),
                columns={"initial": "1", "sm": "2", "md": "2", "lg": "4"},
                spacing="4", width="100%",
            ),
            margin_bottom=Spacing.LG, max_width="6xl", margin_x="auto", width="100%"
        ),
        
        # Grid Secundário (Pendências e Alertas) - Alinhado com grid 4 colunas acima
        rx.box(
            rx.grid(
                # Coluna 1-2: Pendências
                rx.box(
                    rx.vstack(
                        ui.heading("Pendências & Alertas", level=3),
                        ui.card(
                            rx.vstack(
                                # Manutenções
                                rx.box(
                                    rx.hstack(
                                        rx.box(
                                            rx.icon(tag="wrench", size=24, color=Color.WARNING), 
                                            bg=Color.WARNING_BG, p="3", border_radius=Design.RADIUS_MD,
                                            display="flex", align_items="center", justify_content="center"
                                        ),
                                        rx.vstack(
                                            rx.text("Manutenções Pendentes", style=Typography.LABEL, color=Color.TEXT_SECONDARY),
                                            ui.text("Equipamentos aguardando revisão", size="small"),
                                            spacing="0", align_items="start"
                                        ),
                                        rx.spacer(),
                                        rx.text(
                                            State.dashboard_pending_maintenances,
                                            font_size=Typography.DISPLAY["font_size"], font_weight="800",
                                            color=rx.cond(State.has_pending_maintenances, Color.WARNING, Color.SUCCESS),
                                            line_height="1"
                                        ),
                                        width="100%", align_items="center",
                                    ),
                                    padding=Spacing.MD, width="100%", bg=Color.SURFACE, border=f"1px solid {Color.BORDER}", border_radius=Design.RADIUS_XL,
                                    _hover={"border_color": Color.WARNING, "box_shadow": Design.SHADOW_MD}, transition="all 0.2s ease", cursor="pointer"
                                ),
                                # Lotes Vencendo
                                rx.box(
                                    rx.hstack(
                                        rx.box(
                                            rx.icon(tag="clock", size=24, color=Color.ERROR),
                                            bg=Color.ERROR_BG, p="3", border_radius=Design.RADIUS_MD,
                                            display="flex", align_items="center", justify_content="center"
                                        ),
                                        rx.vstack(
                                            rx.text("Lotes Vencendo", style=Typography.LABEL, color=Color.TEXT_SECONDARY),
                                            ui.text("Próximos 30 dias", size="small"),
                                            spacing="0", align_items="start"
                                        ),
                                        rx.spacer(),
                                        rx.text(
                                            State.dashboard_expiring_lots,
                                            font_size=Typography.DISPLAY["font_size"], font_weight="800",
                                            color=rx.cond(State.has_expiring_lots, Color.ERROR, Color.SUCCESS),
                                            line_height="1"
                                        ),
                                        width="100%", align_items="center",
                                    ),
                                    padding=Spacing.MD, width="100%", bg=Color.SURFACE, border=f"1px solid {Color.BORDER}", border_radius=Design.RADIUS_XL,
                                    _hover={"border_color": Color.ERROR, "box_shadow": Design.SHADOW_MD}, transition="all 0.2s ease", cursor="pointer"
                                ),
                                spacing="4", width="100%", height="100%",
                            ),
                            padding=Spacing.LG, height="100%", min_height="250px"
                        ),
                        width="100%", height="100%",
                    ),
                    grid_column={"initial": "span 1", "md": "span 2"},
                ),
                
                # Coluna 3-4: Últimos Alertas
                rx.box(
                    rx.vstack(
                        ui.heading("Alertas Recentes", level=3),
                        ui.card(
                            rx.cond(
                                State.qc_records_with_alerts.length() > 0,
                                rx.vstack(
                                    rx.foreach(
                                        State.qc_records_with_alerts[:4],
                                        lambda r: rx.hstack(
                                            rx.box(width="8px", height="8px", border_radius=Design.RADIUS_FULL, bg=Color.ERROR),
                                            rx.vstack(
                                                ui.text(r["exam_name"], size="label"),
                                                ui.text(r["date"], size="small"),
                                                spacing="0", align_items="start"
                                            ),
                                            rx.spacer(),
                                            ui.status_badge("CV: " + format_cv(r["cv"]) + "%", status="error"),
                                            width="100%", align_items="center",
                                            padding=Spacing.XS, border_radius=Design.RADIUS_MD, _hover={"bg": Color.ERROR_BG}
                                        )
                                    ),
                                    style={"gap": Spacing.SM},
                                ),
                                rx.center(
                                    rx.vstack(
                                        rx.icon(tag="sparkles", size=48, color=Color.TEXT_SECONDARY),
                                        ui.text("Tudo certo!", size="body_large", color=Color.TEXT_SECONDARY),
                                        style={"gap": Spacing.SM}, align_items="center",
                                    ),
                                    height="100%", width="100%", bg=Color.BACKGROUND, border_radius=Design.RADIUS_LG, padding=Spacing.XL
                                )
                            ),
                            height="100%", min_height="250px", padding=Spacing.LG,
                        ),
                        width="100%",
                    ),
                    grid_column={"initial": "span 1", "md": "span 2"},
                ),
                
                columns={"initial": "1", "sm": "2", "md": "2", "lg": "4"},
                spacing="4", width="100%",
            ),
            max_width="6xl", margin_x="auto", width="100%"
        ),

        # Tabela Recente
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.icon(tag="file_text", size=20, color=Color.TEXT_SECONDARY),
                    ui.heading("Últimos Registros", level=3),
                    spacing="2", align_items="center", margin_bottom=Spacing.SM
                ),
                rx.box(
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell(rx.text("EXAME", style=Typography.CAPTION, color=Color.TEXT_SECONDARY)),
                                rx.table.column_header_cell(rx.text("DATA", style=Typography.CAPTION, color=Color.TEXT_SECONDARY)),
                                rx.table.column_header_cell(rx.text("CV%", style=Typography.CAPTION, color=Color.TEXT_SECONDARY)),
                                rx.table.column_header_cell(rx.text("STATUS", style=Typography.CAPTION, color=Color.TEXT_SECONDARY), text_align="right"),
                            )
                        ),
                        rx.table.body(
                            rx.foreach(
                                State.qc_records[:5],
                                lambda r: rx.table.row(
                                    rx.table.cell(ui.text(r["exam_name"], size="body", font_weight="500")),
                                    rx.table.cell(ui.text(r["date"], size="small")),
                                    rx.table.cell(
                                        rx.text(
                                            format_cv(r["cv"]) + "%",
                                            font_weight="700",
                                            color=rx.cond(r["cv"] <= r["cv_max_threshold"], Color.SUCCESS, Color.ERROR)
                                        )
                                    ),
                                    rx.table.cell(
                                        ui.status_badge(
                                            qc_status_label(r["status"], r["cv"], r["cv_max_threshold"]),
                                            status=qc_status_kind(r["status"], r["cv"], r["cv_max_threshold"])
                                        ),
                                        text_align="right"
                                    ),
                                )
                            )
                        ),
                        width="100%"
                    ),
                    bg=Color.SURFACE, border=f"1px solid {Color.BORDER}", border_radius=Design.RADIUS_XL, box_shadow=Design.SHADOW_SM, overflow="hidden",
                    width="100%", overflow_x="auto"
                ),
                width="100%", margin_top=Spacing.LG, max_width="6xl", margin_x="auto"
            ),
            width="100%"
        ),

        spacing="0", width="100%",
    )


def registro_qc_tab() -> rx.Component:
    """Aba de Registro de Controle de Qualidade (Purificada)"""
    return rx.vstack(
        rx.hstack(
            rx.vstack(
                ui.heading("Registro de CQ", level=2),
                ui.text("Insira os dados diários para cálculo automático da Variação %", size="small", color=Color.TEXT_SECONDARY),
                spacing="1", align_items="start",
            ),
            rx.spacer(),
            rx.tooltip(
                ui.button("Voz", icon="mic", variant="ghost", on_click=State.open_voice_modal("registro")),
                content="Preencher por voz com IA",
            ),
            width="100%", align_items="center", margin_bottom=Spacing.LG,
        ),
        
        ui.card(
            rx.vstack(
                ui.text("Dados da Amostra", size="label", color=Color.PRIMARY, style={"letter_spacing": "0.05em", "text_transform": "uppercase"}, margin_bottom=Spacing.MD),
                
                rx.grid(
                    ui.form_field(
                        "Nome do Exame (Obrigatório)",
                        ui.select(
                            State.unique_exam_names,
                            placeholder="Selecione o Exame",
                            value=State.qc_exam_name,
                            on_change=State.on_exam_selected,
                        ),
                        required=True
                    ),
                    ui.form_field(
                        "Data (Automatico)",
                        ui.input(type="date", value=State.qc_date, read_only=True),
                    ),
                    columns={"initial": "1", "sm": "2"},
                    spacing="4", width="100%",
                ),

                # Indicador de Referencia Ativa
                rx.cond(
                    State.has_active_reference,
                    rx.callout(
                        rx.hstack(
                            rx.icon(tag="circle-check", size=16),
                            rx.text("Referencia ativa: ", font_weight="600"),
                            rx.text(State.current_exam_reference["name"]),
                            rx.spacer(),
                            rx.text("CV% Max: <=" + format_cv(State.current_cv_max_threshold) + "%", font_size=Typography.SIZE_SM),
                            width="100%", align_items="center", flex_wrap="wrap", gap="2"
                        ),
                        icon="info", color_scheme="green", width="100%", margin_y=Spacing.SM
                    ),
                    rx.cond(
                        State.qc_exam_name != "",
                        rx.callout(
                            "Nenhuma referencia cadastrada para este exame. Usando limite padrao (10%).",
                            icon="info", color_scheme="yellow", width="100%", margin_y=Spacing.SM
                        )
                    )
                ),
                
                rx.divider(margin_y=Spacing.LG, opacity=0.3),
                
                ui.text("Resultados & Metas", size="label", color=Color.PRIMARY, style={"letter_spacing": "0.05em", "text_transform": "uppercase"}, margin_bottom=Spacing.MD),
                
                rx.grid(
                    ui.form_field("Medição (Obrigatório)", ui.input(placeholder="0.00", value=State.qc_value, on_change=State.update_qc_value), required=True),
                    ui.form_field("Valor Alvo (Obrigatório)", ui.input(placeholder="0.00", value=State.qc_target_value, on_change=State.update_qc_target_value), required=True),
                    ui.form_field("Desvio Padrão (Automático)", ui.input(placeholder="0.00", value=State.qc_target_sd, on_change=State.set_qc_target_sd, read_only=True)),
                    # CV% with dynamic color indicator
                    ui.form_field(
                        "Variação % (Automático)",
                        rx.box(
                            rx.hstack(
                                rx.text(
                                    format_cv(State.qc_calculated_cv) + "%",
                                    font_size=Typography.H3["font_size"], font_weight="bold",
                                    color=rx.cond(State.qc_cv_status == "OK", Color.SUCCESS, Color.ERROR)
                                ),
                                rx.icon(
                                    tag=rx.cond(State.qc_cv_status == "OK", "circle_check", "circle_x"),
                                    size=18,
                                    color=rx.cond(State.qc_cv_status == "OK", Color.SUCCESS, Color.ERROR)
                                ),
                                align_items="center", style={"gap": Spacing.SM}, height="100%",
                            ),
                            width="100%", height="44px", display="flex", align_items="center", padding_x=Spacing.MD, bg=Color.SURFACE, border_radius=Design.RADIUS_LG,
                            border=rx.cond(State.qc_cv_status == "OK", f"1px solid {Color.SUCCESS}40", f"1px solid {Color.ERROR}40")
                        ),
                    ),
                    columns={"initial": "1", "sm": "2", "md": "4"},
                    spacing="4", width="100%",
                ),
                
                rx.divider(margin_y=Spacing.LG, opacity=0.3),
                
                rx.grid(
                    ui.form_field("Equipamento (Automatico)", ui.input(placeholder="Ex: Cobas c111", value=State.qc_equipment, on_change=State.set_qc_equipment)),
                    ui.form_field("Analista Responsável (Opcional)", ui.input(placeholder="Nome do analista", value=State.qc_analyst, on_change=State.set_qc_analyst)),
                    columns={"initial": "1", "sm": "2"},
                    spacing="4", width="100%",
                ),
                
                rx.grid(
                    ui.button("Limpar", icon="eraser", on_click=State.clear_qc_form, variant="secondary", width="100%"),
                    ui.button("Salvar Registro", icon="save", is_loading=State.is_saving_qc, on_click=State.save_qc_record, width="100%"),
                    columns={"initial": "1", "sm": "2"},
                    spacing="4", width="100%", margin_top=Spacing.LG
                ),
                
                # Feedback Messages
                rx.cond(
                    State.qc_success_message != "",
                    rx.callout(State.qc_success_message, icon="circle_check", color_scheme="green", width="100%", margin_top=Spacing.MD),
                ),
                rx.cond(
                    State.qc_warning_message != "",
                    rx.callout(State.qc_warning_message, icon="triangle_alert", color_scheme="yellow", width="100%", margin_top=Spacing.MD),
                ),
                rx.cond(
                    State.qc_error_message != "",
                    rx.callout(State.qc_error_message, icon="triangle_alert", color_scheme="red", width="100%", margin_top=Spacing.MD),
                ),
                width="100%"
            ),
            width="100%"
        ),

        # Histórico Table Section
        rx.box(
            rx.vstack(
                rx.hstack(
                    ui.heading("Histórico Recente", level=3),
                    rx.spacer(),
                    rx.cond(
                        State.qc_records.length() > 0,
                        rx.button(
                            "Limpar Histórico", rx.icon(tag="trash_2", size=14),
                            on_click=State.open_clear_all_modal, variant="ghost", color_scheme="red", size="1", opacity="0.7", _hover={"opacity": "1"}
                        ),
                    ),
                    width="100%", align_items="center", margin_bottom=Spacing.MD
                ),
                rx.cond(
                    State.qc_records.length() > 0,
                    rx.box(
                        rx.table.root(
                            rx.table.header(
                                rx.table.row(
                                    rx.table.column_header_cell(rx.text("DATA", style=Typography.CAPTION, color=Color.TEXT_SECONDARY)),
                                    rx.table.column_header_cell(rx.text("EXAME", style=Typography.CAPTION, color=Color.TEXT_SECONDARY)),
                                    rx.table.column_header_cell(rx.text("VALOR", style=Typography.CAPTION, color=Color.TEXT_SECONDARY)),
                                    rx.table.column_header_cell(rx.text("CV%", style=Typography.CAPTION, color=Color.TEXT_SECONDARY)),
                                    rx.table.column_header_cell(rx.text("STATUS", style=Typography.CAPTION, color=Color.TEXT_SECONDARY)),
                                    rx.table.column_header_cell(rx.text("CALIBRAR?", style=Typography.CAPTION, color=Color.TEXT_SECONDARY)),
                                    rx.table.column_header_cell(rx.text("REF.", style=Typography.CAPTION, color=Color.TEXT_SECONDARY)),
                                    rx.table.column_header_cell(""),
                                )
                            ),
                            rx.table.body(
                                rx.foreach(
                                    State.paginated_qc_records,
                                    lambda r: rx.table.row(
                                        rx.table.cell(rx.text(r.date[:16], color=Color.TEXT_SECONDARY, font_size=Typography.H5["font_size"])),
                                        rx.table.cell(rx.text(r.exam_name, font_weight="600")),
                                        rx.table.cell(r.value.to_string()),
                                        rx.table.cell(rx.text(format_cv(r.cv) + "%", font_weight="600", color=rx.cond(r.cv <= r.cv_max_threshold, Color.SUCCESS, Color.ERROR))),
                                        rx.table.cell(
                                            ui.status_badge(
                                                qc_status_label(r.status, r.cv, r.cv_max_threshold),
                                                status=qc_status_kind(r.status, r.cv, r.cv_max_threshold)
                                            )
                                        ),
                                        rx.table.cell(
                                            rx.cond(
                                                r.needs_calibration,
                                                rx.cond(
                                                    r.post_calibration_id != "",
                                                    # Já tem pós-calibração registrada
                                                    rx.tooltip(
                                                        rx.badge("FEITO", color_scheme="blue", size="1", cursor="default"),
                                                        content="Pós-calibração já registrada"
                                                    ),
                                                    # Precisa registrar pós-calibração - botão clicável
                                                    rx.tooltip(
                                                        rx.badge(
                                                            "SIM",
                                                            color_scheme="red",
                                                            size="1",
                                                            cursor="pointer",
                                                            _hover={"opacity": "0.8", "transform": "scale(1.05)"},
                                                            on_click=lambda: State.open_post_calibration_modal(r.id)
                                                        ),
                                                        content="Clique para registrar medição pós-calibração"
                                                    )
                                                ),
                                                rx.badge("NAO", color_scheme="green", variant="outline", size="1")
                                            )
                                        ),
                                        rx.table.cell(
                                            rx.cond(
                                                r.reference_id != "",
                                                rx.tooltip(
                                                    rx.icon(tag="link", size=14, color=Color.PRIMARY),
                                                    content="Referencia vinculada"
                                                ),
                                                rx.text("-", color=Color.TEXT_SECONDARY, font_size=Typography.SIZE_SM_XS)
                                            )
                                        ),
                                        rx.table.cell(
                                            rx.tooltip(
                                                rx.button(
                                                    rx.icon(tag="trash_2", size=14, color=Color.ERROR),
                                                    on_click=lambda: State.open_delete_qc_record_modal(r.id, r.exam_name),
                                                    variant="ghost", color_scheme="red", size="1",
                                                    aria_label="Excluir registro"
                                                ),
                                                content="Excluir permanentemente"
                                            ),
                                            text_align="right"
                                        ),
                                    )
                                )
                            ),
                            width="100%"
                        ),
                        bg=Color.SURFACE, border=f"1px solid {Color.BORDER}", border_radius=Design.RADIUS_XL, box_shadow=Design.SHADOW_SM, overflow="hidden",
                        width="100%", overflow_x="auto"
                    ),
                    rx.center(
                        rx.vstack(
                            rx.icon(tag="database", size=32, color=Color.TEXT_SECONDARY, opacity=0.3),
                            ui.text("Nenhum registro encontrado.", size="small", color=Color.TEXT_SECONDARY),
                            spacing="2", align_items="center"
                        ),
                        bg=Color.SURFACE, border=f"1px solid {Color.BORDER}", border_radius=Design.RADIUS_XL, padding=Spacing.XL, width="100%"
                    )
                ),
                # Pagination Controls
                rx.cond(
                    State.total_qc_pages > 1,
                    rx.hstack(
                        rx.button(
                            rx.icon(tag="chevron_left", size=16),
                            on_click=State.prev_qc_page,
                            variant="outline", size="1",
                            disabled=State.qc_page == 0,
                            aria_label="Página anterior",
                        ),
                        rx.text(
                            (State.qc_page + 1).to_string() + " / " + State.total_qc_pages.to_string(),
                            font_size=Typography.SIZE_SM, color=Color.TEXT_SECONDARY
                        ),
                        rx.button(
                            rx.icon(tag="chevron_right", size=16),
                            on_click=State.next_qc_page,
                            variant="outline", size="1",
                            disabled=State.qc_page >= State.total_qc_pages - 1,
                            aria_label="Próxima página",
                        ),
                        justify_content="center", align_items="center",
                        style={"gap": Spacing.MD}, width="100%", margin_top=Spacing.MD
                    ),
                ),
                width="100%"
            ),
            width="100%", margin_top=Spacing.XL
        ),
        
        width="100%", padding_bottom=Spacing.XXL
    )

def reagentes_tab() -> rx.Component:
    """Aba de Gestão de Reagentes (Purificada)"""
    return rx.vstack(
        rx.hstack(
            rx.vstack(
                ui.heading("Gestão de Reagentes", level=2),
                ui.text("Controle de lotes, validade e fabricantes", size="small", color=Color.TEXT_SECONDARY),
                spacing="1", align_items="start",
            ),
            rx.spacer(),
            rx.tooltip(
                ui.button("Voz", icon="mic", variant="ghost", on_click=State.open_voice_modal("reagente")),
                content="Preencher por voz com IA",
            ),
            width="100%", align_items="center", margin_bottom=Spacing.LG,
        ),
        
        rx.grid(
            # Coluna Esquerda: Formulário
            ui.card(
                rx.vstack(
                    ui.text("Novo Lote", size="label", color=Color.PRIMARY, style={"letter_spacing": "0.05em", "text_transform": "uppercase"}, margin_bottom=Spacing.SM),
                    
                    ui.form_field("Nome do Reagente", ui.input(value=State.reagent_name, on_change=State.set_reagent_name), True),
                    ui.form_field("Lote", ui.input(value=State.reagent_lot_number, on_change=State.set_reagent_lot_number), True),
                    ui.form_field("Validade", ui.input(type="date", value=State.reagent_expiry_date, on_change=State.set_reagent_expiry_date), True),
                    rx.grid(
                        ui.form_field("Estoque Atual", ui.input(placeholder="0", value=State.reagent_initial_stock, on_change=State.set_reagent_initial_stock)),
                        ui.form_field("Consumo p/ Dia", ui.input(placeholder="0", value=State.reagent_daily_consumption, on_change=State.set_reagent_daily_consumption)),
                        columns="2", spacing="2", width="100%"
                    ),
                    ui.form_field("Fabricante", ui.input(value=State.reagent_manufacturer, on_change=State.set_reagent_manufacturer)),
                    
                    ui.button("Cadastrar Lote", icon="plus", is_loading=State.is_saving_reagent, on_click=State.save_reagent_lot, width="100%", margin_top=Spacing.MD),
                    
                    # Mensagens Feedback
                    rx.cond(
                        State.reagent_success_message != "",
                        rx.callout(State.reagent_success_message, icon="circle_check", color_scheme="green", width="100%")
                    ),
                    rx.cond(
                        State.reagent_error_message != "",
                        rx.callout(State.reagent_error_message, icon="triangle_alert", color_scheme="red", width="100%")
                    ),
                ),
            ),
            
            # Coluna Direita: Listagem e Manutenção
            rx.vstack(
                # Lista de Lotes
                ui.card(
                    rx.vstack(
                        rx.hstack(
                            ui.heading("Lotes Ativos", level=3),
                            rx.spacer(),
                            rx.badge(State.reagent_lots.length().to_string() + " lotes", color_scheme="blue", variant="soft"),
                            width="100%", align_items="center", margin_bottom=Spacing.MD
                        ),
                        rx.cond(
                            State.reagent_lots.length() > 0,
                            rx.vstack(
                                rx.foreach(
                                    State.reagent_lots,
                                    lambda lot: rx.hstack(
                                        rx.box(
                                            rx.icon(tag="package", size=20, color=Color.TEXT_SECONDARY),
                                            bg=rx.cond(lot["days_left"] <= 7, Color.ERROR_BG, rx.cond(lot["days_left"] <= 30, Color.WARNING_BG, Color.PRIMARY_LIGHT)),
                                            p="2", border_radius=Design.RADIUS_SM
                                        ),
                                        rx.vstack(
                                            ui.text(lot["name"], font_weight="500"),
                                            rx.hstack(
                                                ui.text(lot["lot_number"], size="small", color=Color.TEXT_SECONDARY),
                                                rx.text("•", color=Color.TEXT_SECONDARY, font_size=Typography.SIZE_SM_XS),
                                                ui.text(lot["manufacturer"], size="small", color=Color.TEXT_SECONDARY),
                                                spacing="1",
                                            ),
                                            spacing="0"
                                        ),
                                        rx.spacer(),
                                        rx.vstack(
                                            rx.badge(
                                                rx.cond(
                                                    lot["days_left"] <= 0, "Vencido",
                                                    rx.cond(lot["days_left"] <= 30, lot["days_left"].to_string() + " dias", lot["expiry_date"])
                                                ),
                                                color_scheme=rx.cond(lot["days_left"] <= 7, "red", rx.cond(lot["days_left"] <= 30, "amber", "green")),
                                                variant="solid"
                                            ),
                                            rx.cond(lot["days_left"] <= 30, rx.text(lot["expiry_date"], font_size=Typography.SIZE_2XS, color=Color.TEXT_SECONDARY, text_align="center")),
                                            # Risco de Ruptura
                                            rx.cond(
                                                lot["days_to_rupture"] != None,
                                                rx.badge(
                                                    rx.cond(lot["days_to_rupture"] <= 5, "RISCO RUPTURA", f"Estoque: {lot['days_to_rupture']} dias"),
                                                    color_scheme=rx.cond(lot["days_to_rupture"] <= 5, "red", "gray"),
                                                    variant="outline", margin_top=Spacing.XS
                                                )
                                            ),
                                            spacing="0", align_items="center"
                                        ),
                                        rx.button(
                                            rx.icon(tag="trash_2", size=14),
                                            on_click=lambda: State.delete_reagent_lot(lot["id"]),
                                            size="1", variant="ghost", color_scheme="red",
                                            aria_label="Excluir lote"
                                        ),
                                        width="100%", align_items="center", style={"gap": Spacing.MD},
                                        padding=Spacing.MD, border_radius=Design.RADIUS_LG,
                                        border=rx.cond(lot["days_left"] <= 7, f"1px solid {Color.ERROR}40", rx.cond(lot["days_left"] <= 30, f"1px solid {Color.WARNING}40", f"1px solid {Color.BORDER}")),
                                        bg=rx.cond(lot["days_left"] <= 7, Color.ERROR_BG, rx.cond(lot["days_left"] <= 30, Color.WARNING_BG, Color.SURFACE)),
                                        _hover={"box_shadow": Design.SHADOW_MD, "border_color": Color.PRIMARY}, transition="all 0.2s ease"
                                    )
                                ),
                                spacing="2"
                            ),
                            rx.center(
                                rx.vstack(
                                    rx.icon(tag="package_open", size=32, color=Color.TEXT_SECONDARY),
                                    ui.text("Nenhum lote cadastrado.", size="small", color=Color.TEXT_SECONDARY),
                                    spacing="2", align_items="center"
                                ),
                                padding_y=Spacing.XL, width="100%"
                            )
                        ),
                    ),
                    width="100%"
                ),
                
                # Diário de Manutenção
                ui.card(
                    rx.vstack(
                        rx.hstack(
                            ui.heading("Diário de Manutenção", level=3),
                            rx.spacer(),
                            rx.tooltip(
                                ui.button("Voz", icon="mic", variant="ghost", on_click=State.open_voice_modal("manutencao")),
                                content="Preencher por voz com IA",
                            ),
                            width="100%", align_items="center",
                        ),
                        rx.grid(
                            ui.input(placeholder="Equipamento...", value=State.maintenance_equipment, on_change=State.set_maintenance_equipment),
                            ui.select(["Preventiva", "Corretiva", "Calibração"], value=State.maintenance_type, on_change=State.set_maintenance_type),
                            columns={"initial": "1", "sm": "2"}, spacing="2", width="100%"
                        ),
                        rx.grid(
                            ui.input(type="date", value=State.maintenance_date, on_change=State.set_maintenance_date),
                            ui.input(type="date", placeholder="Próxima...", value=State.maintenance_next_date, on_change=State.set_maintenance_next_date),
                            columns={"initial": "1", "sm": "2"}, spacing="2", width="100%"
                        ),
                        ui.text_area(placeholder="Observações...", value=State.maintenance_notes, on_change=State.set_maintenance_notes),
                        ui.button("Registrar Manutenção", icon="wrench", on_click=State.save_maintenance_record, width="100%", variant="secondary"),
                        
                        rx.cond(State.maintenance_success_message != "", rx.callout(State.maintenance_success_message, icon="circle_check", color_scheme="green", width="100%")),
                        rx.cond(State.maintenance_error_message != "", rx.callout(State.maintenance_error_message, icon="triangle_alert", color_scheme="red", width="100%")),
                    ),
                    width="100%"
                ),

                # Histórico de Manutenções
                ui.card(
                    rx.vstack(
                        rx.hstack(
                            ui.heading("Histórico de Manutenções", level=3),
                            rx.spacer(),
                            rx.badge(State.maintenance_records.length().to_string() + " registros", color_scheme="blue", variant="soft"),
                            width="100%", align_items="center", margin_bottom=Spacing.MD
                        ),
                        rx.cond(
                            State.maintenance_records.length() > 0,
                            rx.vstack(
                                rx.foreach(
                                    State.maintenance_records,
                                    lambda m: rx.hstack(
                                        rx.box(
                                            rx.icon(tag="wrench", size=20, color=Color.TEXT_SECONDARY),
                                            bg=Color.PRIMARY_LIGHT, p="2", border_radius=Design.RADIUS_SM
                                        ),
                                        rx.vstack(
                                            ui.text(m.equipment, font_weight="500"),
                                            rx.hstack(
                                                rx.badge(m.type, color_scheme="blue", size="1"),
                                                ui.text(m.date, size="small", color=Color.TEXT_SECONDARY),
                                                spacing="1",
                                            ),
                                            spacing="0"
                                        ),
                                        rx.spacer(),
                                        rx.cond(
                                            m.next_date != "",
                                            rx.badge("Próx: " + m.next_date, color_scheme="amber", variant="outline", size="1"),
                                        ),
                                        rx.button(
                                            rx.icon(tag="trash_2", size=14),
                                            on_click=lambda: State.delete_maintenance_record(m.id),
                                            size="1", variant="ghost", color_scheme="red",
                                            aria_label="Excluir manutenção"
                                        ),
                                        width="100%", align_items="center", style={"gap": Spacing.MD},
                                        padding=Spacing.SM, border_radius=Design.RADIUS_LG,
                                        border=f"1px solid {Color.BORDER}",
                                        _hover={"bg": Color.BACKGROUND}, transition="all 0.2s ease"
                                    )
                                ),
                                spacing="2"
                            ),
                            rx.center(
                                rx.vstack(
                                    rx.icon(tag="wrench", size=32, color=Color.TEXT_SECONDARY),
                                    ui.text("Nenhuma manutenção registrada.", size="small", color=Color.TEXT_SECONDARY),
                                    spacing="2", align_items="center"
                                ),
                                padding_y=Spacing.XL, width="100%"
                            )
                        ),
                    ),
                    width="100%", max_height="400px", overflow_y="auto"
                ),
                spacing="6", width="100%"
            ),
            columns={"initial": "1", "lg": "2"},
            spacing="6", width="100%"
        )
    )

def relatorios_tab() -> rx.Component:
    """Aba de Relatórios - Gráfico Levey-Jennings (Purificada)"""
    return rx.vstack(
        rx.vstack(
            ui.heading("Relatórios & Auditoria", level=2),
            ui.text("Visualize gráficos ou exporte tabelas completas para auditoria", size="small", color=Color.TEXT_SECONDARY),
            spacing="1", align_items="start", margin_bottom=Spacing.LG, width="100%"
        ),
        
        # Section: Exportação PDF (Split View)
        ui.card(
            rx.vstack(
                rx.hstack(
                    rx.box(rx.icon(tag="file_text", size=20, color=Color.PRIMARY), bg=Color.PRIMARY_LIGHT, p="2", border_radius=Design.RADIUS_SM),
                    ui.heading("Exportar Tabela QC (PDF)", level=3),
                    rx.spacer(),
                    rx.cond(
                        State.qc_pdf_preview != "",
                        rx.badge("Preview Ativo", color_scheme="green", variant="soft")
                    ),
                    style={"gap": Spacing.SM}, align_items="center", margin_bottom=Spacing.MD, width="100%"
                ),
                
                rx.hstack(
                    # Controls Column
                    rx.vstack(
                        rx.grid(
                            rx.box(
                                ui.text("Período", size="label", margin_bottom=Spacing.XS),
                                ui.select(["Mês Atual", "Mês Específico", "3 Meses", "6 Meses", "Ano Atual", "Ano Específico"], value=State.qc_report_type, on_change=State.set_qc_report_type)
                            ),
                            rx.cond(
                                State.qc_report_type == "Mês Específico",
                                rx.box(
                                    ui.text("Mês", size="label", margin_bottom=Spacing.XS),
                                    ui.select(["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"], value=State.qc_report_month, on_change=State.set_qc_report_month, placeholder="Mês")
                                )
                            ),
                            rx.cond(
                                (State.qc_report_type == "Mês Específico") | (State.qc_report_type == "Ano Específico"),
                                rx.box(
                                    ui.text("Ano", size="label", margin_bottom=Spacing.XS),
                                    ui.input(value=State.qc_report_year, on_change=State.set_qc_report_year, placeholder="Ano (ex: 2024)")
                                )
                            ),
                            columns={"initial": "1", "sm": "2"}, style={"gap": Spacing.MD}, width="100%"
                        ),
                        rx.box(
                             rx.grid(
                                 ui.button("Baixar PDF", icon="download", on_click=State.generate_qc_report_pdf, is_loading=State.is_generating_qc_report, variant="primary", width="100%"),
                                 ui.button("Exportar CSV", icon="file-spreadsheet", on_click=State.export_qc_csv, variant="secondary", width="100%"),
                                 columns="2", spacing="3", width="100%",
                             ),
                             margin_top=Spacing.LG,
                        ),
                        rx.cond(
                            State.qc_error_message != "",
                            rx.callout(State.qc_error_message, icon="triangle_alert", color_scheme="red", width="100%", margin_top=Spacing.MD)
                        ),
                        width=rx.cond(State.qc_pdf_preview != "", "40%", "100%"), transition="width 0.3s ease"
                    ),
                    
                    # Preview Column
                    rx.cond(
                        State.qc_pdf_preview != "",
                        rx.box(
                            rx.html(
                                f'<iframe src="data:application/pdf;base64,' + State.qc_pdf_preview + '" width="100%" height="400px" style="border: none; border-radius: 8px; background: white;"></iframe>'
                            ),
                            width="60%", height="400px", bg=Color.BACKGROUND, border_radius=Design.RADIUS_MD, border=f"1px solid {Color.BORDER}"
                        )
                    ),
                    width="100%", spacing="6", align_items="start"
                )
            ),
            border_left=f"4px solid {Color.PRIMARY}", margin_bottom=Spacing.LG,
        ),
        rx.divider(margin_bottom=Spacing.LG, opacity=0.3),

        rx.vstack(
            ui.heading("Análise Levey-Jennings", level=2),
            ui.text("Visualização gráfica de tendências", size="small", color=Color.TEXT_SECONDARY),
            spacing="1", align_items="start", margin_bottom=Spacing.LG, width="100%"
        ),
        
        # Controls
        ui.card(
            rx.vstack(
                rx.grid(
                    rx.box(ui.text("Exame", size="label", margin_bottom=Spacing.XS), ui.select(State.unique_exam_names, value=State.levey_jennings_exam, on_change=State.set_levey_jennings_exam, placeholder="Selecione o exame...")),
                    rx.box(ui.text("Nível", size="label", margin_bottom=Spacing.XS), ui.select(["Todos", "N1", "N2", "N3"], value=State.levey_jennings_level, on_change=State.set_levey_jennings_level, placeholder="Selecione...")),
                    rx.box(ui.text("Período (dias)", size="label", margin_bottom=Spacing.XS), ui.select(["7", "15", "30", "60", "90"], value=State.levey_jennings_period, on_change=State.set_levey_jennings_period)),
                    columns="3", spacing="4", width="100%"
                ),
                ui.button("Gerar Gráfico", icon="chart_line", on_click=State.update_levey_jennings_data, margin_top=Spacing.MD),
            ),
            width="100%"
        ),
        
        # Chart Area
        rx.cond(
            State.levey_jennings_data.length() > 0,
            rx.vstack(
                # Legend (Purified)
                rx.hstack(
                    rx.hstack(rx.box(width="12px", height="12px", border_radius=Design.RADIUS_FULL, bg=Color.SUCCESS), rx.text("±1 DP", style=Typography.CAPTION), style={"gap": Spacing.XS}),
                    rx.hstack(rx.box(width="12px", height="12px", border_radius=Design.RADIUS_FULL, bg=Color.WARNING), rx.text("±2 DP", style=Typography.CAPTION), style={"gap": Spacing.XS}),
                    rx.hstack(rx.box(width="12px", height="12px", border_radius=Design.RADIUS_FULL, bg=Color.ERROR), rx.text("±3 DP", style=Typography.CAPTION), style={"gap": Spacing.XS}),
                    style={"gap": Spacing.LG}, justify_content="center", width="100%", margin_bottom=Spacing.MD
                ),
                
                # Recharts Line Chart
                ui.card(
                    rx.recharts.line_chart(
                        rx.recharts.line(data_key="value", stroke=Color.PRIMARY, stroke_width=2, dot=True, name="Valor"),
                        rx.recharts.line(data_key="target", stroke=Color.SUCCESS, stroke_width=1, stroke_dash_array="5 5", dot=False, name="Alvo"),
                        rx.recharts.x_axis(data_key="date"),
                        rx.recharts.y_axis(domain=[State.lj_min_domain, State.lj_max_domain]),
                        # Westgard Zones (Background)
                        rx.recharts.reference_area(y1=State.lj_target_minus_1sd.to_string(), y2=State.lj_target_plus_1sd.to_string(), fill=Color.SUCCESS, fill_opacity=0.1),
                        rx.recharts.reference_area(y1=State.lj_target_plus_1sd.to_string(), y2=State.lj_target_plus_2sd.to_string(), fill=Color.WARNING, fill_opacity=0.15),
                        rx.recharts.reference_area(y1=State.lj_target_minus_2sd.to_string(), y2=State.lj_target_minus_1sd.to_string(), fill=Color.WARNING, fill_opacity=0.15),
                        rx.recharts.reference_area(y1=State.lj_target_plus_2sd.to_string(), y2=State.lj_max_domain.to_string(), fill=Color.ERROR, fill_opacity=0.1),
                        rx.recharts.reference_area(y1=State.lj_min_domain.to_string(), y2=State.lj_target_minus_2sd.to_string(), fill=Color.ERROR, fill_opacity=0.1),
                        rx.recharts.cartesian_grid(stroke_dasharray="3 3", opacity=0.4),
                        rx.recharts.graphing_tooltip(),
                        rx.recharts.legend(),
                        rx.recharts.reference_line(y=State.lj_target_plus_1sd.to_string(), stroke=Color.SUCCESS, stroke_width=1, stroke_dasharray="3 3", label="+1s"),
                        rx.recharts.reference_line(y=State.lj_target_minus_1sd.to_string(), stroke=Color.SUCCESS, stroke_width=1, stroke_dasharray="3 3", label="-1s"),
                        rx.recharts.reference_line(y=State.lj_target_plus_2sd.to_string(), stroke=Color.WARNING, stroke_width=1, stroke_dasharray="3 3", label="+2s"),
                        rx.recharts.reference_line(y=State.lj_target_minus_2sd.to_string(), stroke=Color.WARNING, stroke_width=1, stroke_dasharray="3 3", label="-2s"),
                        rx.recharts.reference_line(y=State.lj_target_plus_3sd.to_string(), stroke=Color.ERROR, stroke_width=1, stroke_dasharray="3 3", label="+3s"),
                        rx.recharts.reference_line(y=State.lj_target_minus_3sd.to_string(), stroke=Color.ERROR, stroke_width=1, stroke_dasharray="3 3", label="-3s"),
                        data=State.levey_jennings_chart_data, width="100%", height=400,
                    ),
                    width="100%", padding=Spacing.MD
                ),
                
                # Statistics Summary
                rx.grid(
                    ui.stat_card("Média", State.lj_mean, "target", "primary"),
                    ui.stat_card("Desvio Padrão", State.lj_sd, "variable", "primary"),
                    ui.stat_card("CV% Médio", format_cv(State.lj_cv_mean) + "%", "percent", "primary"),
                    ui.stat_card("Pontos", State.levey_jennings_data.length(), "list", "primary"),
                    columns={"initial": "1", "sm": "2", "md": "2", "lg": "4"},
                    spacing="4", width="100%", margin_top=Spacing.LG
                ),
                
                # Data Table
                rx.box(
                    rx.vstack(
                        rx.hstack(ui.heading("Dados do Período", level=3), rx.spacer(), rx.badge(State.levey_jennings_data.length().to_string() + " registros", color_scheme="blue", variant="soft"), width="100%", align_items="center", margin_bottom=Spacing.MD),
                        rx.scroll_area(
                            rx.table.root(
                                rx.table.header(
                                    rx.table.row(
                                        rx.table.column_header_cell(rx.text("DATA", style=Typography.CAPTION)),
                                        rx.table.column_header_cell(rx.text("VALOR", style=Typography.CAPTION)),
                                        rx.table.column_header_cell(rx.text("ALVO", style=Typography.CAPTION)),
                                        rx.table.column_header_cell(rx.text("DP", style=Typography.CAPTION)),
                                        rx.table.column_header_cell(rx.text("CV%", style=Typography.CAPTION)),
                                        rx.table.column_header_cell(rx.text("STATUS", style=Typography.CAPTION)),
                                    )
                                ),
                                rx.table.body(
                                    rx.foreach(
                                        State.levey_jennings_data,
                                        lambda d: rx.table.row(
                                            rx.table.cell(rx.text(d.date, font_size=Typography.H5["font_size"])),
                                            rx.table.cell(rx.text(d.value.to_string(), font_weight="600")),
                                            rx.table.cell(d.target.to_string()),
                                            rx.table.cell(d.sd.to_string()),
                                            rx.table.cell(rx.text(format_cv(d.cv) + "%", font_weight="700", color=rx.cond(d.cv <= State.current_cv_max_threshold, Color.SUCCESS, rx.cond(d.cv <= State.current_cv_max_threshold * 1.5, Color.WARNING, Color.ERROR)))),
                                            rx.table.cell(ui.status_badge(rx.cond(d.cv <= State.current_cv_max_threshold, "OK", "ALERTA"), status=rx.cond(d.cv <= State.current_cv_max_threshold, "success", "error"))),
                                        )
                                    )
                                ), width="100%"
                            ),
                            style={"max_height": "300px"}
                        ),
                    ),
                    bg=Color.SURFACE, border=f"1px solid {Color.BORDER}", border_radius=Design.RADIUS_XL, padding=Spacing.LG, margin_top=Spacing.LG, width="100%", box_shadow=Design.SHADOW_SM
                ),
                width="100%"
            ),
            rx.center(
                rx.vstack(rx.icon(tag="chart_bar", size=48, color=Color.TEXT_SECONDARY, opacity=0.3), ui.text("Selecione um exame e gere o gráfico", color=Color.TEXT_SECONDARY), spacing="2", align_items="center"),
                bg=Color.BACKGROUND, border=f"2px dashed {Color.BORDER}", border_radius=Design.RADIUS_XL, padding=Spacing.XL, width="100%"
            )
        ),
        width="100%"
    )

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


def post_calibration_modal() -> rx.Component:
    """Modal para registrar medição pós-calibração"""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.hstack(
                    rx.icon(tag="settings_2", size=24, color=Color.PRIMARY),
                    rx.text("Medição Pós-Calibração", font_weight="700", font_size=Typography.SIZE_XL),
                    spacing="2", align_items="center"
                )
            ),
            rx.dialog.description(
                rx.text("Registre o novo valor após a calibração do equipamento", color=Color.TEXT_SECONDARY, font_size=Typography.H5["font_size"])
            ),

            rx.vstack(
                # Informações do registro original
                rx.cond(
                    State.selected_qc_record_for_calibration != None,
                    rx.box(
                        rx.vstack(
                            rx.text("Registro Original", font_weight="600", color=Color.TEXT_SECONDARY, font_size=Typography.SIZE_SM_XS, style={"text_transform": "uppercase", "letter_spacing": "0.05em"}),
                            rx.grid(
                                rx.vstack(
                                    rx.text("Exame", font_size=Typography.SIZE_SM_XS, color=Color.TEXT_SECONDARY),
                                    rx.text(State.selected_qc_record_for_calibration["exam_name"], font_weight="600"),
                                    spacing="0", align_items="start"
                                ),
                                rx.vstack(
                                    rx.text("Valor Original", font_size=Typography.SIZE_SM_XS, color=Color.TEXT_SECONDARY),
                                    rx.text(State.selected_qc_record_for_calibration["value"].to_string(), font_weight="600", color=Color.ERROR),
                                    spacing="0", align_items="start"
                                ),
                                rx.vstack(
                                    rx.text("CV% Original", font_size=Typography.SIZE_SM_XS, color=Color.TEXT_SECONDARY),
                                    rx.text(format_cv(State.selected_qc_record_for_calibration["cv"]) + "%", font_weight="600", color=Color.ERROR),
                                    spacing="0", align_items="start"
                                ),
                                rx.vstack(
                                    rx.text("Valor Alvo", font_size=Typography.SIZE_SM_XS, color=Color.TEXT_SECONDARY),
                                    rx.text(State.selected_qc_record_for_calibration["target_value"].to_string(), font_weight="600"),
                                    spacing="0", align_items="start"
                                ),
                                columns="4", spacing="4", width="100%"
                            ),
                            spacing="2", width="100%"
                        ),
                        bg=Color.ERROR_BG, padding=Spacing.MD, border_radius=Design.RADIUS_LG, width="100%", margin_bottom=Spacing.MD
                    )
                ),

                rx.divider(margin_y=Spacing.SM, opacity=0.3),

                # Formulário de pós-calibração
                rx.vstack(
                    ui.form_field(
                        "Nova Medição (Pós-Calibração)",
                        ui.input(
                            placeholder="Digite o novo valor...",
                            value=State.post_cal_value,
                            on_change=State.set_post_cal_value,
                        ),
                        required=True
                    ),

                    # Exibição do CV% calculado em tempo real
                    rx.cond(
                        State.post_cal_value != "",
                        rx.box(
                            rx.hstack(
                                rx.text("CV% Pós-Calibração: ", font_size=Typography.H5["font_size"]),
                                rx.text(
                                    format_cv(State.post_cal_calculated_cv) + "%",
                                    font_weight="700",
                                    color=rx.cond(State.post_cal_calculated_cv <= 10.0, Color.SUCCESS, Color.WARNING)
                                ),
                                rx.cond(
                                    State.post_cal_calculated_cv <= 10.0,
                                    rx.icon(tag="circle_check", size=16, color=Color.SUCCESS),
                                    rx.icon(tag="circle_alert", size=16, color=Color.WARNING)
                                ),
                                spacing="2", align_items="center"
                            ),
                            bg=rx.cond(State.post_cal_calculated_cv <= 10.0, Color.SUCCESS + "15", Color.WARNING + "15"),
                            padding=Spacing.SM, border_radius=Design.RADIUS_MD, width="100%"
                        )
                    ),

                    ui.form_field(
                        "Analista Responsável",
                        ui.input(
                            placeholder="Nome do analista...",
                            value=State.post_cal_analyst,
                            on_change=State.set_post_cal_analyst
                        )
                    ),

                    ui.form_field(
                        "Observações",
                        rx.text_area(
                            placeholder="Descreva as ações tomadas na calibração...",
                            value=State.post_cal_notes,
                            on_change=State.set_post_cal_notes,
                            width="100%", min_height="80px"
                        )
                    ),

                    spacing="3", width="100%"
                ),

                # Mensagens de feedback
                rx.cond(
                    State.post_cal_success_message != "",
                    rx.callout(State.post_cal_success_message, icon="circle_check", color_scheme="green", width="100%")
                ),
                rx.cond(
                    State.post_cal_error_message != "",
                    rx.callout(State.post_cal_error_message, icon="triangle_alert", color_scheme="red", width="100%")
                ),

                # Botões de ação
                rx.hstack(
                    ui.button("Cancelar", icon="x", variant="secondary", on_click=State.close_post_calibration_modal),
                    ui.button(
                        "Salvar Medição", icon="save",
                        is_loading=State.is_saving_post_calibration,
                        on_click=State.save_post_calibration
                    ),
                    spacing="3", width="100%", justify_content="flex-end", margin_top=Spacing.MD
                ),

                spacing="3", width="100%", padding_top=Spacing.MD
            ),

            style={"max_width": Design.MODAL_WIDTH_MD}
        ),
        open=State.show_post_calibration_modal
    )


def delete_qc_record_modal() -> rx.Component:
    """Modal de confirmação para exclusão permanente de registro CQ"""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.hstack(
                    rx.icon(tag="triangle-alert", size=24, color=Color.ERROR),
                    rx.text("Confirmar Exclusão", font_weight="700", font_size=Typography.SIZE_XL),
                    spacing="2", align_items="center"
                )
            ),
            rx.dialog.description(
                rx.text("Esta ação não pode ser desfeita!", color=Color.ERROR, font_size=Typography.H5["font_size"])
            ),

            rx.vstack(
                rx.box(
                    rx.vstack(
                        rx.text("Você está prestes a excluir permanentemente o registro:", font_size=Typography.SIZE_MD_SM),
                        rx.text(State.delete_qc_record_name, font_weight="700", font_size=Typography.SIZE_LG, color=Color.PRIMARY),
                        rx.text("Este registro será removido do banco de dados e não poderá ser recuperado.", font_size=Typography.SIZE_SM, color=Color.TEXT_SECONDARY),
                        spacing="2", align_items="center", width="100%"
                    ),
                    bg=Color.ERROR_BG, padding=Spacing.MD, border_radius=Design.RADIUS_LG, width="100%", margin_y=Spacing.MD
                ),

                rx.hstack(
                    ui.button("Cancelar", icon="x", variant="secondary", on_click=State.close_delete_qc_record_modal),
                    ui.button(
                        "Excluir Permanentemente", icon="trash-2",
                        variant="danger",
                        on_click=State.confirm_delete_qc_record
                    ),
                    spacing="3", width="100%", justify_content="flex-end", margin_top=Spacing.MD
                ),

                spacing="3", width="100%", padding_top=Spacing.MD
            ),

            style={"max_width": Design.MODAL_WIDTH_SM}
        ),
        open=State.show_delete_qc_record_modal
    )


def clear_all_qc_modal() -> rx.Component:
    """Modal de confirmação para limpar todo o histórico de CQ"""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.hstack(
                    rx.icon(tag="triangle-alert", size=24, color=Color.ERROR),
                    rx.text("Limpar Todo o Histórico", font_weight="700", font_size=Typography.SIZE_XL),
                    spacing="2", align_items="center"
                )
            ),
            rx.dialog.description(
                rx.text("Esta ação não pode ser desfeita!", color=Color.ERROR, font_size=Typography.H5["font_size"])
            ),

            rx.vstack(
                rx.box(
                    rx.vstack(
                        rx.text("Todos os registros de controle de qualidade serão excluídos permanentemente.", font_size=Typography.SIZE_MD_SM),
                        rx.text("Esta operação removerá todos os dados do banco e não poderá ser revertida.", font_size=Typography.SIZE_SM, color=Color.TEXT_SECONDARY),
                        spacing="2", align_items="center", width="100%"
                    ),
                    bg=Color.ERROR_BG, padding=Spacing.MD, border_radius=Design.RADIUS_LG, width="100%", margin_y=Spacing.MD
                ),

                rx.hstack(
                    ui.button("Cancelar", icon="x", variant="secondary", on_click=State.close_clear_all_modal),
                    ui.button(
                        "Excluir Tudo", icon="trash-2",
                        variant="danger",
                        on_click=State.confirm_clear_all_qc_records
                    ),
                    spacing="3", width="100%", justify_content="flex-end", margin_top=Spacing.MD
                ),

                spacing="3", width="100%", padding_top=Spacing.MD
            ),

            style={"max_width": Design.MODAL_WIDTH_SM}
        ),
        open=State.show_clear_all_modal
    )


def delete_reference_modal() -> rx.Component:
    """Modal de confirmação para exclusão permanente de referência"""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.hstack(
                    rx.icon(tag="triangle-alert", size=24, color=Color.ERROR),
                    rx.text("Confirmar Exclusão", font_weight="700", font_size=Typography.SIZE_XL),
                    spacing="2", align_items="center"
                )
            ),
            rx.dialog.description(
                rx.text("Esta ação não pode ser desfeita!", color=Color.ERROR, font_size=Typography.H5["font_size"])
            ),

            rx.vstack(
                rx.box(
                    rx.vstack(
                        rx.text("Você está prestes a excluir permanentemente a referência:", font_size=Typography.SIZE_MD_SM),
                        rx.text(State.delete_reference_name, font_weight="700", font_size=Typography.SIZE_LG, color=Color.PRIMARY),
                        rx.text("Esta referência será removida do banco de dados e não poderá ser recuperada.", font_size=Typography.SIZE_SM, color=Color.TEXT_SECONDARY),
                        spacing="2", align_items="center", width="100%"
                    ),
                    bg=Color.ERROR_BG, padding=Spacing.MD, border_radius=Design.RADIUS_LG, width="100%", margin_y=Spacing.MD
                ),

                rx.hstack(
                    ui.button("Cancelar", icon="x", variant="secondary", on_click=State.close_delete_reference_modal),
                    ui.button(
                        "Excluir Permanentemente", icon="trash-2",
                        variant="danger",
                        on_click=State.confirm_delete_reference
                    ),
                    spacing="3", width="100%", justify_content="flex-end", margin_top=Spacing.MD
                ),

                spacing="3", width="100%", padding_top=Spacing.MD
            ),

            style={"max_width": Design.MODAL_WIDTH_SM}
        ),
        open=State.show_delete_reference_modal
    )


def reference_card(ref) -> rx.Component:
    """Card individual de referencia cadastrada"""
    return rx.box(
        rx.hstack(
            rx.vstack(
                rx.text(ref.name, font_weight="600", font_size=Typography.SIZE_MD),
                rx.hstack(
                    rx.badge(ref.exam_name, color_scheme="blue", size="1"),
                    rx.badge(ref.level, variant="outline", size="1"),
                    spacing="1"
                ),
                rx.text(
                    "Alvo: " + ref.target_value.to_string() + " | CV% Max: <=" + format_cv(ref.cv_max_threshold) + "%",
                    font_size=Typography.SIZE_SM_XS, color=Color.TEXT_SECONDARY
                ),
                rx.text(
                    f"Valido a partir de: {ref.valid_from}",
                    font_size=Typography.SIZE_XS, color=Color.TEXT_SECONDARY
                ),
                spacing="1", align_items="start"
            ),
            rx.spacer(),
            rx.vstack(
                rx.badge(
                    rx.cond(ref.is_active, "Ativo", "Inativo"),
                    color_scheme=rx.cond(ref.is_active, "green", "gray"),
                    size="1"
                ),
                rx.tooltip(
                    rx.button(
                        rx.icon(tag="trash_2", size=14),
                        on_click=lambda: State.open_delete_reference_modal(ref.id, ref.name),
                        variant="ghost", color_scheme="red", size="1",
                        aria_label="Excluir referência"
                    ),
                    content="Excluir permanentemente"
                ),
                spacing="2", align_items="end"
            ),
            width="100%", align_items="center"
        ),
        padding=Spacing.MD, width="100%",
        bg=Color.SURFACE, border=f"1px solid {Color.BORDER}", border_radius=Design.RADIUS_LG,
        _hover={"border_color": Color.PRIMARY, "box_shadow": Design.SHADOW_DEFAULT},
        transition="all 0.2s ease"
    )


def referencias_tab() -> rx.Component:
    """Aba de Cadastro de Valores Referenciais do CQ"""
    return rx.vstack(
        rx.hstack(
            rx.vstack(
                ui.heading("Valores Referenciais do CQ", level=2),
                ui.text("Configure valores-alvo e tolerancias de CV% por exame e periodo", size="small", color=Color.TEXT_SECONDARY),
                spacing="1", align_items="start",
            ),
            rx.spacer(),
            rx.tooltip(
                ui.button("Voz", icon="mic", variant="ghost", on_click=State.open_voice_modal("referencia")),
                content="Preencher por voz com IA",
            ),
            width="100%", align_items="center", margin_bottom=Spacing.LG,
        ),

        rx.grid(
            # Coluna Esquerda: Formulario
            ui.card(
                rx.vstack(
                    ui.text("Nova Referencia", size="label", color=Color.PRIMARY, style={"letter_spacing": "0.05em", "text_transform": "uppercase"}, margin_bottom=Spacing.MD),

                    # Nome do Registro (dropdown dinamico + botao adicionar)
                    ui.form_field(
                        "Nome do Registro",
                        rx.vstack(
                            ui.select(
                                State.qc_registry_names,
                                placeholder="Selecione o Nome",
                                value=State.ref_name,
                                on_change=State.set_ref_name,
                            ),
                            rx.button(
                                rx.icon(tag="plus", size=14),
                                rx.text("Adicionar Nome", font_size=Typography.SIZE_SM_XS),
                                on_click=State.open_add_name_modal,
                                variant="ghost", color_scheme="blue", size="1",
                                width="100%",
                            ),
                            spacing="1", width="100%"
                        ),
                        required=True
                    ),

                    # Exame e Nivel
                    rx.grid(
                        ui.form_field(
                            "Exame",
                            rx.vstack(
                                ui.select(
                                    State.unique_exam_names,
                                    placeholder="Selecione o Exame",
                                    value=State.ref_exam_name,
                                    on_change=State.set_ref_exam_name
                                ),
                                rx.button(
                                    rx.icon(tag="plus", size=14),
                                    rx.text("Adicionar Exame", font_size=Typography.SIZE_SM_XS),
                                    on_click=State.open_add_exam_modal,
                                    variant="ghost", color_scheme="blue", size="1",
                                    width="100%",
                                ),
                                spacing="1", width="100%"
                            ),
                            required=True
                        ),
                        ui.form_field(
                            "Nivel",
                            ui.select(
                                ["Normal", "N1", "N2", "N3"],
                                value=State.ref_level,
                                on_change=State.set_ref_level
                            )
                        ),
                        columns="2", spacing="4", width="100%"
                    ),

                    # Datas de Validade
                    rx.grid(
                        ui.form_field(
                            "Valido a partir de (Automatico)",
                            ui.input(type="date", value=State.ref_valid_from, on_change=State.set_ref_valid_from),
                            required=True
                        ),
                        ui.form_field(
                            "Valido ate (opcional)",
                            ui.input(type="date", value=State.ref_valid_until, on_change=State.set_ref_valid_until)
                        ),
                        columns="2", spacing="4", width="100%"
                    ),

                    rx.divider(margin_y=Spacing.MD, opacity=0.3),

                    # Valor Alvo
                    ui.form_field(
                        "Valor-Alvo (Media de Controle)",
                        ui.input(placeholder="0.00", value=State.ref_target_value, on_change=State.set_ref_target_value),
                        required=True
                    ),

                    # Limite de CV%
                    ui.form_field(
                        "CV% Maximo Aceito (acima = calibrar)",
                        ui.input(placeholder="10.0", value=State.ref_cv_max_threshold, on_change=State.set_ref_cv_max_threshold),
                        required=True
                    ),

                    rx.divider(margin_y=Spacing.MD, opacity=0.3),

                    # Informacoes do Material
                    rx.grid(
                        ui.form_field(
                            "Lote do Controle",
                            ui.input(placeholder="LOT...", value=State.ref_lot_number, on_change=State.set_ref_lot_number)
                        ),
                        ui.form_field(
                            "Fabricante",
                            ui.input(placeholder="Ex: ControlLab", value=State.ref_manufacturer, on_change=State.set_ref_manufacturer)
                        ),
                        columns="2", spacing="4", width="100%"
                    ),

                    ui.form_field(
                        "Observacoes",
                        rx.text_area(
                            placeholder="Notas adicionais...",
                            value=State.ref_notes,
                            on_change=State.set_ref_notes,
                            width="100%", min_height="80px"
                        )
                    ),

                    # Botao Salvar
                    ui.button(
                        "Salvar Referencia", icon="save",
                        is_loading=State.is_saving_reference,
                        on_click=State.save_qc_reference,
                        width="100%", margin_top=Spacing.MD
                    ),

                    # Mensagens
                    rx.cond(
                        State.ref_success_message != "",
                        rx.callout(State.ref_success_message, icon="circle_check", color_scheme="green", width="100%", margin_top=Spacing.MD)
                    ),
                    rx.cond(
                        State.ref_error_message != "",
                        rx.callout(State.ref_error_message, icon="triangle_alert", color_scheme="red", width="100%", margin_top=Spacing.MD)
                    ),

                    spacing="3", width="100%"
                ),
                padding=Spacing.LG
            ),

            # Coluna Direita: Lista de Referencias
            rx.vstack(
                ui.heading("Referencias Cadastradas", level=3),
                ui.card(
                    rx.vstack(
                        rx.cond(
                            State.qc_reference_values.length() > 0,
                            rx.vstack(
                                rx.foreach(State.qc_reference_values, reference_card),
                                spacing="2", width="100%"
                            ),
                            rx.center(
                                rx.vstack(
                                    rx.icon(tag="settings", size=32, color=Color.TEXT_SECONDARY),
                                    ui.text("Nenhuma referencia cadastrada", size="small", color=Color.TEXT_SECONDARY),
                                    ui.text("Cadastre valores de referencia para cada exame", size="small", color=Color.TEXT_SECONDARY),
                                    spacing="2", align_items="center"
                                ),
                                padding=Spacing.XL, width="100%"
                            )
                        ),
                        spacing="2", width="100%"
                    ),
                    padding=Spacing.MD, max_height="500px", overflow_y="auto"
                ),
                # Botao para recarregar
                ui.button(
                    "Atualizar Lista", icon="refresh_cw",
                    on_click=State.load_qc_references,
                    variant="secondary", width="100%", margin_top=Spacing.SM
                ),
                width="100%", spacing="3"
            ),

            columns={"initial": "1", "lg": "2"},
            spacing="6", width="100%"
        ),
        width="100%"
    )


def add_exam_modal() -> rx.Component:
    """Modal para adicionar novo exame a lista"""
    return rx.alert_dialog.root(
        rx.alert_dialog.content(
            rx.alert_dialog.title("Adicionar Novo Exame"),
            rx.alert_dialog.description(
                rx.vstack(
                    ui.text("O novo exame ficara disponivel nas abas Registro CQ e Referencias CQ.", size="small", color=Color.TEXT_SECONDARY),
                    ui.form_field(
                        "Nome do Exame",
                        ui.input(
                            placeholder="Ex: HEMOGLOBINA GLICADA",
                            value=State.new_exam_name,
                            on_change=State.set_new_exam_name,
                        ),
                        required=True
                    ),
                    rx.cond(
                        State.add_exam_error != "",
                        rx.callout(State.add_exam_error, icon="triangle_alert", color_scheme="red", width="100%")
                    ),
                    spacing="3", width="100%"
                )
            ),
            rx.hstack(
                rx.alert_dialog.cancel(
                    rx.button("Cancelar", variant="outline", on_click=State.close_add_exam_modal)
                ),
                rx.button("Salvar Exame", on_click=State.add_new_exam, color_scheme="blue"),
                spacing="3", justify="end", width="100%", margin_top=Spacing.MD
            ),
            max_width="450px"
        ),
        open=State.show_add_exam_modal
    )


def add_name_modal() -> rx.Component:
    """Modal para adicionar novo nome de registro"""
    return rx.alert_dialog.root(
        rx.alert_dialog.content(
            rx.alert_dialog.title("Adicionar Nome de Registro"),
            rx.alert_dialog.description(
                rx.vstack(
                    ui.text("Este nome ficara disponivel no dropdown da aba Referencias CQ.", size="small", color=Color.TEXT_SECONDARY),
                    ui.form_field(
                        "Nome do Registro",
                        ui.input(
                            placeholder="Ex: Kit ControlLab Jan/2026",
                            value=State.new_registry_name,
                            on_change=State.set_new_registry_name,
                        ),
                        required=True
                    ),
                    rx.cond(
                        State.add_name_error != "",
                        rx.callout(State.add_name_error, icon="triangle_alert", color_scheme="red", width="100%")
                    ),
                    spacing="3", width="100%"
                )
            ),
            rx.hstack(
                rx.alert_dialog.cancel(
                    rx.button("Cancelar", variant="outline", on_click=State.close_add_name_modal)
                ),
                rx.button("Salvar Nome", on_click=State.add_registry_name, color_scheme="blue"),
                spacing="3", justify="end", width="100%", margin_top=Spacing.MD
            ),
            max_width="450px"
        ),
        open=State.show_add_name_modal
    )


def voice_recording_modal() -> rx.Component:
    """Modal de gravacao de voz para preenchimento de formulario via IA"""
    js_start = """
(async () => {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        window._voiceStream = stream;
        const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
            ? 'audio/webm;codecs=opus' : 'audio/mp4';
        window._voiceRecorder = new MediaRecorder(stream, { mimeType });
        window._voiceChunks = [];
        window._voiceRecorder.ondataavailable = (e) => {
            if (e.data.size > 0) window._voiceChunks.push(e.data);
        };
        window._voiceRecorder.start();
        return "ok";
    } catch(err) {
        return "error:" + err.message;
    }
})()
"""
    js_stop = """
new Promise((resolve) => {
    if (window._voiceRecorder && window._voiceRecorder.state === 'recording') {
        window._voiceRecorder.onstop = async () => {
            const blob = new Blob(window._voiceChunks, { type: window._voiceRecorder.mimeType });
            const reader = new FileReader();
            reader.onloadend = () => resolve(reader.result.split(',')[1]);
            reader.readAsDataURL(blob);
            if (window._voiceStream) {
                window._voiceStream.getTracks().forEach(t => t.stop());
            }
        };
        window._voiceRecorder.stop();
    } else {
        resolve("");
    }
})
"""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.hstack(
                    rx.icon(tag="mic", size=24, color=Color.PRIMARY),
                    rx.text("Preencher por Voz", font_weight="700", font_size=Typography.SIZE_XL),
                    spacing="2", align_items="center",
                )
            ),
            rx.dialog.description(
                rx.text(
                    "Fale os dados do formulario e a IA preenchera automaticamente",
                    color=Color.TEXT_SECONDARY, font_size=Typography.H5["font_size"],
                )
            ),
            rx.vstack(
                # Area central com botao de gravacao
                rx.center(
                    rx.cond(
                        State.voice_is_recording,
                        # Estado: Gravando (vermelho pulsando)
                        rx.vstack(
                            rx.box(
                                rx.icon(tag="mic", size=48, color=Color.WHITE),
                                width="100px", height="100px",
                                bg=Color.ERROR,
                                border_radius=Design.RADIUS_FULL,
                                display="flex", align_items="center", justify_content="center",
                                animation="voicePulse 1.5s ease-in-out infinite",
                                cursor="pointer",
                                on_click=[
                                    State.set_voice_recording(False),
                                    rx.call_script(js_stop, callback=State.receive_voice_audio),
                                ],
                                _hover={"opacity": "0.8"},
                            ),
                            rx.text("Toque para parar", color=Color.ERROR, font_weight="600",
                                    font_size=Typography.SIZE_SM, margin_top=Spacing.SM),
                            align_items="center",
                        ),
                        rx.cond(
                            State.voice_is_processing,
                            # Estado: Processando (spinner)
                            rx.vstack(
                                rx.spinner(size="3", color=Color.PRIMARY),
                                rx.text("Analisando audio com IA...", color=Color.PRIMARY,
                                        font_weight="600", font_size=Typography.SIZE_MD),
                                align_items="center", spacing="3",
                            ),
                            # Estado: Idle (pronto para gravar)
                            rx.vstack(
                                rx.box(
                                    rx.icon(tag="mic", size=48, color=Color.WHITE),
                                    width="100px", height="100px",
                                    bg=Color.PRIMARY,
                                    border_radius=Design.RADIUS_FULL,
                                    display="flex", align_items="center", justify_content="center",
                                    cursor="pointer",
                                    on_click=[
                                        State.set_voice_recording(True),
                                        rx.call_script(js_start),
                                    ],
                                    _hover={"bg": Color.PRIMARY_HOVER, "transform": "scale(1.05)"},
                                    transition="all 0.2s ease",
                                    box_shadow=Design.SHADOW_MD,
                                ),
                                rx.text("Toque para gravar", color=Color.TEXT_SECONDARY,
                                        font_weight="500", font_size=Typography.SIZE_SM,
                                        margin_top=Spacing.SM),
                                align_items="center",
                            ),
                        ),
                    ),
                    width="100%", padding_y=Spacing.XL,
                ),
                # Mensagem de status
                rx.cond(
                    State.voice_status_message != "",
                    rx.callout(
                        State.voice_status_message,
                        icon="info",
                        color_scheme=rx.cond(
                            State.voice_status_message.contains("sucesso"),
                            "green", "blue",
                        ),
                        width="100%",
                    ),
                ),
                # Mensagem de erro
                rx.cond(
                    State.voice_error_message != "",
                    rx.callout(
                        State.voice_error_message,
                        icon="triangle_alert",
                        color_scheme="red",
                        width="100%",
                    ),
                ),
                # Botao fechar
                rx.hstack(
                    ui.button(
                        "Fechar", icon="x",
                        variant="secondary",
                        on_click=State.close_voice_modal,
                    ),
                    justify_content="flex-end", width="100%", margin_top=Spacing.MD,
                ),
                spacing="3", width="100%", padding_top=Spacing.MD,
            ),
            style={"max_width": Design.MODAL_WIDTH_MD},
        ),
        open=State.show_voice_modal,
    )


def proin_page() -> rx.Component:
    """Página principal do ProIn QC (Purificada)"""
    return rx.box(
        # Loading overlay
        rx.cond(
            State.is_loading_data,
            rx.center(
                rx.vstack(
                    rx.spinner(size="3", color=Color.PRIMARY),
                    ui.text("Carregando dados...", size="small", color=Color.TEXT_SECONDARY),
                    spacing="3", align_items="center"
                ),
                width="100%", padding_y=Spacing.XXL
            ),
        ),
        rx.vstack(
            rx.box(
                ui.animated_heading("ProIn QC - Gestão de Qualidade", level=1),
                padding_y=Spacing.XL, width="100%", display="flex", justify_content="center"
            ),

            # Navegação de Abas
            rx.box(
                rx.hstack(
                    tab_button("Dashboard", "layout_dashboard", "dashboard"),
                    tab_button("Registro CQ", "clipboard_list", "registro"),
                    tab_button("Referencias CQ", "settings", "referencias"),
                    tab_button("Reagentes / Manutenção", "beaker", "reagentes"),
                    tab_button("Relatórios", "bar_chart_3", "relatorios"),
                    tab_button("Importar", "upload", "importar"),
                    spacing="2", justify_content="center", width="100%", flex_wrap="wrap"
                ),
                margin_bottom=Spacing.XL, width="100%"
            ),

            # Conteúdo da Aba Ativa
            rx.box(
                rx.cond(State.proin_current_tab == "dashboard", dashboard_tab()),
                rx.cond(State.proin_current_tab == "registro", registro_qc_tab()),
                rx.cond(State.proin_current_tab == "referencias", referencias_tab()),
                rx.cond(State.proin_current_tab == "reagentes", reagentes_tab()),
                rx.cond(State.proin_current_tab == "relatorios", relatorios_tab()),
                rx.cond(State.proin_current_tab == "importar", importar_tab()),
                width="100%", max_width="6xl", margin_x="auto"
            ),

            spacing="0", align_items="center", width="100%", padding_y=Spacing.XL, padding_x=Spacing.MD
        ),
        # Modal de Pós-Calibração
        post_calibration_modal(),
        # Modais de Confirmação de Exclusão
        delete_qc_record_modal(),
        delete_reference_modal(),
        clear_all_qc_modal(),
        # Modal de Adicionar Exame
        add_exam_modal(),
        # Modal de Adicionar Nome de Registro
        add_name_modal(),
        # Modal de Gravacao de Voz (IA)
        voice_recording_modal(),
        width="100%",
    )
