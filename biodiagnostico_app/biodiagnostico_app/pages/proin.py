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


def tab_button(label: str, icon: str, tab_id: str) -> rx.Component:
    """Botão de aba do ProIn - Purificado"""
    is_active = State.proin_current_tab == tab_id
    
    return rx.button(
        rx.hstack(
            rx.icon(tag=icon, size=18),
            rx.text(label, font_size="0.875rem", font_weight="500"),
            style={"gap": "8px"},
            align_items="center",
        ),
        on_click=lambda: State.set_proin_tab(tab_id),
        bg=rx.cond(is_active, Color.PRIMARY_LIGHT, "transparent"),
        color=rx.cond(is_active, Color.PRIMARY, Color.TEXT_SECONDARY),
        border_radius=Design.RADIUS_LG,
        padding_x="1.5rem",
        padding_y="0.75rem",
        border=rx.cond(is_active, f"1px solid {Color.PRIMARY}40", "1px solid transparent"),
        _hover={
            "bg": Color.PRIMARY_LIGHT,
            "color": Color.PRIMARY,
        },
        transition="all 0.2s cubic-bezier(0.4, 0, 0.2, 1)"
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
                    style={"gap": "8px"},
                ),
                on_click=State.load_data_from_db(True),
                variant="ghost", size="2", color=Color.TEXT_SECONDARY,
                _hover={"bg": Color.PRIMARY_LIGHT, "color": Color.DEEP},
                border_radius=Design.RADIUS_LG
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
                                            bg=Color.WARNING_BG, p="3", border_radius="12px",
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
                                            font_size="2rem", font_weight="800",
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
                                            bg=Color.ERROR_BG, p="3", border_radius="12px",
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
                                            font_size="2rem", font_weight="800",
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
                                            rx.box(width="8px", height="8px", border_radius="full", bg=Color.ERROR),
                                            rx.vstack(
                                                ui.text(r["exam_name"], size="label"),
                                                ui.text(r["date"], size="small"),
                                                spacing="0", align_items="start"
                                            ),
                                            rx.spacer(),
                                            ui.status_badge("CV: " + r["cv"].to_string() + "%", status="error"),
                                            width="100%", align_items="center",
                                            padding=Spacing.XS, border_radius=Design.RADIUS_MD, _hover={"bg": Color.ERROR_BG}
                                        )
                                    ),
                                    style={"gap": "8px"},
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
                                            r["cv"].to_string() + "%",
                                            font_weight="700",
                                            color=rx.cond(r["status"] == "OK", Color.SUCCESS, Color.ERROR)
                                        )
                                    ),
                                    rx.table.cell(ui.status_badge(r["status"], status=rx.cond(r["status"] == "OK", "success", rx.cond(r["status"].contains("ALERTA"), "warning", "error"))), text_align="right"),
                                )
                            )
                        ),
                        width="100%"
                    ),
                    bg=Color.SURFACE, border=f"1px solid {Color.BORDER}", border_radius=Design.RADIUS_XL, box_shadow=Design.SHADOW_SM, overflow="hidden"
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
        rx.vstack(
            ui.heading("Registro de CQ", level=2),
            ui.text("Insira os dados diários para cálculo automático da Variação %", size="small", color=Color.TEXT_SECONDARY),
            spacing="1", align_items="start", margin_bottom=Spacing.LG
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
                            on_change=State.set_qc_exam_name,
                        ),
                        required=True
                    ),
                    ui.form_field(
                        "Número do Lote (Opcional)",
                        ui.input(placeholder="LOT...", value=State.qc_lot_number, on_change=State.set_qc_lot_number)
                    ),
                    ui.form_field(
                        "Data/Hora (Obrigatório)",
                        ui.input(type="datetime-local", value=State.qc_date, on_change=State.set_qc_date),
                        required=True
                    ),
                    columns={"initial": "1", "sm": "1", "md": "3"},
                    spacing="4", width="100%",
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
                                    State.qc_calculated_cv.to_string() + "%",
                                    font_size="1.125rem", font_weight="bold",
                                    color=rx.cond(State.qc_cv_status == "ok", Color.SUCCESS, rx.cond(State.qc_cv_status == "warning", Color.WARNING, Color.ERROR))
                                ),
                                rx.icon(
                                    tag=rx.cond(State.qc_cv_status == "ok", "circle_check", rx.cond(State.qc_cv_status == "warning", "triangle_alert", "circle_x")),
                                    size=18,
                                    color=rx.cond(State.qc_cv_status == "ok", Color.SUCCESS, rx.cond(State.qc_cv_status == "warning", Color.WARNING, Color.ERROR))
                                ),
                                align_items="center", style={"gap": "8px"}, height="100%",
                            ),
                            width="100%", height="44px", display="flex", align_items="center", padding_x=Spacing.MD, bg=Color.SURFACE, border_radius=Design.RADIUS_LG,
                            border=rx.cond(State.qc_cv_status == "ok", f"1px solid {Color.SUCCESS}40", rx.cond(State.qc_cv_status == "warning", f"1px solid {Color.WARNING}40", f"1px solid {Color.ERROR}40"))
                        ),
                    ),
                    columns={"initial": "1", "sm": "2", "md": "4"},
                    spacing="4", width="100%",
                ),
                
                rx.divider(margin_y=Spacing.LG, opacity=0.3),
                
                rx.grid(
                    ui.form_field("Equipamento (Opcional)", ui.input(placeholder="Ex: Cobas c111", value=State.qc_equipment, on_change=State.set_qc_equipment)),
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
            max_width="4xl", margin_x="auto", width="100%"
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
                            on_click=State.clear_all_qc_records, variant="ghost", color_scheme="red", size="1", opacity="0.7", _hover={"opacity": "1"}
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
                                    rx.table.column_header_cell(""),
                                )
                            ),
                            rx.table.body(
                                rx.foreach(
                                    State.qc_records,
                                    lambda r: rx.table.row(
                                        rx.table.cell(rx.text(r.date[:16], color=Color.TEXT_SECONDARY, font_size="0.875rem")),
                                        rx.table.cell(rx.text(r.exam_name, font_weight="600")),
                                        rx.table.cell(r.value.to_string()),
                                        rx.table.cell(rx.text(r.cv.to_string() + "%", font_weight="600", color=rx.cond(r.status == "OK", Color.SUCCESS, Color.ERROR))),
                                        rx.table.cell(ui.status_badge(r.status, status=rx.cond(r.status == "OK", "success", rx.cond(r.status.contains("ALERTA"), "warning", "error")))),
                                        rx.table.cell(
                                            rx.button(
                                                rx.icon(tag="trash_2", size=14, color=Color.ERROR),
                                                on_click=lambda: State.delete_qc_record(r.id),
                                                variant="ghost", color_scheme="red", size="1"
                                            ),
                                            text_align="right"
                                        ),
                                    )
                                )
                            ),
                            width="100%"
                        ),
                        bg=Color.SURFACE, border=f"1px solid {Color.BORDER}", border_radius=Design.RADIUS_XL, box_shadow=Design.SHADOW_SM, overflow="hidden"
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
                width="100%"
            ),
            width="100%", margin_top=Spacing.XL, max_width="4xl", margin_x="auto"
        ),
        
        width="100%", padding_bottom="3rem"
    )

def reagentes_tab() -> rx.Component:
    """Aba de Gestão de Reagentes (Purificada)"""
    return rx.vstack(
        rx.vstack(
            ui.heading("Gestão de Reagentes", level=2),
            ui.text("Controle de lotes, validade e fabricantes", size="small", color=Color.TEXT_SECONDARY),
            spacing="1", align_items="start", margin_bottom=Spacing.LG, width="100%"
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
                        ui.text(State.reagent_success_message, color=Color.SUCCESS, size="small")
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
                                            p="2", border_radius="10px"
                                        ),
                                        rx.vstack(
                                            ui.text(lot["name"], font_weight="500"),
                                            rx.hstack(
                                                ui.text(lot["lot_number"], size="small", color=Color.TEXT_SECONDARY),
                                                rx.text("•", color=Color.TEXT_SECONDARY, font_size="0.75rem"),
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
                                            rx.cond(lot["days_left"] <= 30, rx.text(lot["expiry_date"], font_size="0.65rem", color=Color.TEXT_SECONDARY, text_align="center")),
                                            # Risco de Ruptura
                                            rx.cond(
                                                lot["days_to_rupture"] != None,
                                                rx.badge(
                                                    rx.cond(lot["days_to_rupture"] <= 5, "RISCO RUPTURA", f"Estoque: {lot['days_to_rupture']} dias"),
                                                    color_scheme=rx.cond(lot["days_to_rupture"] <= 5, "red", "gray"),
                                                    variant="outline", margin_top="4px"
                                                )
                                            ),
                                            spacing="0", align_items="center"
                                        ),
                                        rx.button(
                                            rx.icon(tag="trash_2", size=14),
                                            on_click=lambda: State.delete_reagent_lot(lot["id"]),
                                            size="1", variant="ghost", color_scheme="red"
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
                        ui.heading("Diário de Manutenção", level=3),
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
                        
                        rx.cond(State.maintenance_success_message != "", ui.text(State.maintenance_success_message, color=Color.SUCCESS, size="small")),
                    ),
                    width="100%"
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
                    rx.box(rx.icon(tag="file_text", size=20, color=Color.PRIMARY), bg=Color.PRIMARY_LIGHT, p="2", border_radius="8px"),
                    ui.heading("Exportar Tabela QC (PDF)", level=3),
                    rx.spacer(),
                    rx.cond(
                        State.qc_pdf_preview != "",
                        rx.badge("Preview Ativo", color_scheme="green", variant="soft")
                    ),
                    style={"gap": "8px"}, align_items="center", margin_bottom=Spacing.MD, width="100%"
                ),
                
                rx.hstack(
                    # Controls Column
                    rx.vstack(
                        rx.grid(
                            rx.box(
                                ui.text("Período", size="label", margin_bottom="4px"),
                                ui.select(["Mês Atual", "Mês Específico", "3 Meses", "6 Meses", "Ano Atual", "Ano Específico"], value=State.qc_report_type, on_change=State.set_qc_report_type)
                            ),
                            rx.cond(
                                State.qc_report_type == "Mês Específico",
                                rx.box(
                                    ui.text("Mês", size="label", margin_bottom="4px"),
                                    ui.select(["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"], value=State.qc_report_month, on_change=State.set_qc_report_month, placeholder="Mês")
                                )
                            ),
                            rx.cond(
                                (State.qc_report_type == "Mês Específico") | (State.qc_report_type == "Ano Específico"),
                                rx.box(
                                    ui.text("Ano", size="label", margin_bottom="4px"),
                                    ui.input(value=State.qc_report_year, on_change=State.set_qc_report_year, placeholder="Ano (ex: 2024)")
                                )
                            ),
                            columns={"initial": "1", "sm": "2"}, style={"gap": Spacing.MD}, width="100%"
                        ),
                        rx.box(
                             ui.button("Baixar PDF", icon="download", on_click=State.generate_qc_report_pdf, is_loading=State.is_generating_qc_report, variant="primary", width="100%", margin_top="24px"),
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
                            width="60%", height="400px", bg=Color.BACKGROUND, border_radius="12px", border=f"1px solid {Color.BORDER}"
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
            max_width="3xl", margin_x="auto", width="100%"
        ),
        
        # Chart Area
        rx.cond(
            State.levey_jennings_data.length() > 0,
            rx.vstack(
                # Legend (Purified)
                rx.hstack(
                    rx.hstack(rx.box(width="12px", height="12px", border_radius="full", bg=Color.SUCCESS), rx.text("±1 DP", style=Typography.CAPTION), style={"gap": "4px"}),
                    rx.hstack(rx.box(width="12px", height="12px", border_radius="full", bg=Color.WARNING), rx.text("±2 DP", style=Typography.CAPTION), style={"gap": "4px"}),
                    rx.hstack(rx.box(width="12px", height="12px", border_radius="full", bg=Color.ERROR), rx.text("±3 DP", style=Typography.CAPTION), style={"gap": "4px"}),
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
                    ui.stat_card("CV% Médio", State.lj_cv_mean.to_string() + "%", "percent", "primary"),
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
                                            rx.table.cell(rx.text(d.date, font_size="0.875rem")),
                                            rx.table.cell(rx.text(d.value.to_string(), font_weight="600")),
                                            rx.table.cell(d.target.to_string()),
                                            rx.table.cell(d.sd.to_string()),
                                            rx.table.cell(rx.text(d.cv.to_string() + "%", font_weight="700", color=rx.cond(d.cv <= 5.0, Color.SUCCESS, rx.cond(d.cv <= 10.0, Color.WARNING, Color.ERROR)))),
                                            rx.table.cell(ui.status_badge(rx.cond(d.cv <= 5.0, "OK", "ALERTA"), status=rx.cond(d.cv <= 5.0, "success", "error"))),
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
                max_width="2xl", margin_x="auto", width="100%"
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
                                        rx.foreach(row, lambda cell: rx.table.cell(rx.text(cell, font_size="0.875rem")))
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

def proin_page() -> rx.Component:
    """Página principal do ProIn QC (Purificada)"""
    return rx.box(
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
                    tab_button("Reagentes / Manutenção", "beaker", "reagentes"),
                    tab_button("Relatórios", "bar_chart_3", "relatorios"),
                    tab_button("Importar", "upload", "importar"),
                    spacing="2", justify_content="center", width="100%"
                ),
                margin_bottom=Spacing.XL, width="100%"
            ),
            
            # Conteúdo da Aba Ativa
            rx.box(
                rx.cond(State.proin_current_tab == "dashboard", dashboard_tab()),
                rx.cond(State.proin_current_tab == "registro", registro_qc_tab()),
                rx.cond(State.proin_current_tab == "reagentes", reagentes_tab()),
                rx.cond(State.proin_current_tab == "relatorios", relatorios_tab()),
                rx.cond(State.proin_current_tab == "importar", importar_tab()),
                width="100%", max_width="6xl", margin_x="auto"
            ),
            
            spacing="0", align_items="center", width="100%", padding_y=Spacing.XL, padding_x=Spacing.MD
        ),
        width="100%",
    )
