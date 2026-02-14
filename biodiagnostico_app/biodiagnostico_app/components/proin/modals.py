import reflex as rx
from ...state import State
from ...styles import Color, Design, Typography, Spacing
from ...components import ui
from .helpers import format_cv


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

                # Layout lado a lado: formulário + histórico de calibrações
                rx.grid(
                    # Coluna esquerda: formulário de pós-calibração
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

                    # Coluna direita: histórico de calibrações do exame
                    rx.vstack(
                        rx.hstack(
                            rx.icon(tag="history", size=16, color=Color.PRIMARY),
                            rx.text("Histórico de Calibrações", font_weight="600", font_size=Typography.SIZE_SM, color=Color.DEEP),
                            spacing="2", align_items="center",
                        ),
                        rx.cond(
                            State.calibration_history_for_selected.length() > 0,
                            rx.box(
                                rx.table.root(
                                    rx.table.header(
                                        rx.table.row(
                                            rx.table.column_header_cell(rx.text("DATA", style=Typography.CAPTION, color=Color.TEXT_SECONDARY)),
                                            rx.table.column_header_cell(rx.text("VALOR", style=Typography.CAPTION, color=Color.TEXT_SECONDARY)),
                                            rx.table.column_header_cell(rx.text("CV%", style=Typography.CAPTION, color=Color.TEXT_SECONDARY)),
                                            rx.table.column_header_cell(rx.text("ANALISTA", style=Typography.CAPTION, color=Color.TEXT_SECONDARY)),
                                        ),
                                    ),
                                    rx.table.body(
                                        rx.foreach(
                                            State.calibration_history_for_selected,
                                            lambda pc: rx.table.row(
                                                rx.table.cell(rx.text(pc.date[:10], font_size=Typography.SIZE_SM_XS, color=Color.TEXT_SECONDARY)),
                                                rx.table.cell(rx.text(pc.post_calibration_value.to_string(), font_size=Typography.SIZE_SM, font_weight="600")),
                                                rx.table.cell(
                                                    rx.text(
                                                        format_cv(pc.post_calibration_cv) + "%",
                                                        font_size=Typography.SIZE_SM, font_weight="600",
                                                        color=rx.cond(pc.post_calibration_cv <= 10.0, Color.SUCCESS, Color.ERROR),
                                                    )
                                                ),
                                                rx.table.cell(rx.text(pc.analyst, font_size=Typography.SIZE_SM_XS, color=Color.TEXT_SECONDARY)),
                                            ),
                                        ),
                                    ),
                                    width="100%",
                                ),
                                bg=Color.SURFACE,
                                border=f"1px solid {Color.BORDER}",
                                border_radius=Design.RADIUS_LG,
                                overflow="hidden",
                                overflow_x="auto",
                                width="100%",
                                max_height="260px",
                                overflow_y="auto",
                            ),
                            rx.center(
                                rx.vstack(
                                    rx.icon(tag="clipboard_list", size=24, color=Color.TEXT_SECONDARY, opacity=0.3),
                                    rx.text("Nenhuma calibração anterior.", font_size=Typography.SIZE_SM_XS, color=Color.TEXT_SECONDARY),
                                    spacing="1", align_items="center",
                                ),
                                bg=Color.SURFACE,
                                border=f"1px solid {Color.BORDER}",
                                border_radius=Design.RADIUS_LG,
                                padding=Spacing.MD,
                                width="100%",
                            ),
                        ),
                        spacing="2", width="100%",
                    ),

                    columns={"initial": "1", "md": "2"},
                    spacing="4",
                    width="100%",
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

            style={"max_width": "800px"}
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


def levey_jennings_chart_modal() -> rx.Component:
    """Modal para exibir gráfico Levey-Jennings de um exame específico"""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.hstack(
                    rx.icon(tag="chart_line", size=24, color=Color.PRIMARY),
                    rx.text("Gráfico Levey-Jennings", font_weight="700", font_size=Typography.SIZE_XL),
                    spacing="2", align_items="center"
                )
            ),
            rx.dialog.description(
                rx.hstack(
                    rx.text("Exame: ", color=Color.TEXT_SECONDARY, font_size=Typography.H5["font_size"]),
                    rx.text(State.chart_modal_exam_name, font_weight="600", font_size=Typography.H5["font_size"], color=Color.DEEP),
                    rx.spacer(),
                    rx.badge(State.levey_jennings_data.length().to_string() + " pontos", color_scheme="blue", variant="soft"),
                    spacing="2", align_items="center", width="100%"
                )
            ),

            rx.vstack(
                # Controles de período
                rx.hstack(
                    rx.box(
                        ui.text("Período (dias)", size="label", margin_bottom=Spacing.XS),
                        ui.select(["7", "15", "30", "60", "90"], value=State.chart_modal_period, on_change=State.set_chart_modal_period),
                        width="150px"
                    ),
                    ui.button("Atualizar", icon="refresh-cw", on_click=State.update_chart_modal_data, size="2"),
                    spacing="3", align_items="end", width="100%"
                ),

                # Legenda
                rx.hstack(
                    rx.hstack(rx.box(width="12px", height="12px", border_radius=Design.RADIUS_FULL, bg=Color.SUCCESS), rx.text("±1 DP", style=Typography.CAPTION), style={"gap": Spacing.XS}),
                    rx.hstack(rx.box(width="12px", height="12px", border_radius=Design.RADIUS_FULL, bg=Color.WARNING), rx.text("±2 DP", style=Typography.CAPTION), style={"gap": Spacing.XS}),
                    rx.hstack(rx.box(width="12px", height="12px", border_radius=Design.RADIUS_FULL, bg=Color.ERROR), rx.text("±3 DP", style=Typography.CAPTION), style={"gap": Spacing.XS}),
                    style={"gap": Spacing.LG}, justify_content="center", width="100%", margin_top=Spacing.MD
                ),

                # Gráfico
                rx.cond(
                    State.levey_jennings_data.length() > 0,
                    rx.box(
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
                            data=State.levey_jennings_chart_data, width="100%", height=350,
                        ),
                        bg=Color.SURFACE, border=f"1px solid {Color.BORDER}", border_radius=Design.RADIUS_LG, padding=Spacing.MD,
                        margin_top=Spacing.MD, width="100%"
                    ),
                    rx.center(
                        rx.vstack(
                            rx.icon(tag="chart_bar", size=48, color=Color.TEXT_SECONDARY, opacity=0.3),
                            ui.text("Nenhum dado encontrado para o período selecionado", color=Color.TEXT_SECONDARY),
                            spacing="2", align_items="center"
                        ),
                        bg=Color.BACKGROUND, border=f"2px dashed {Color.BORDER}", border_radius=Design.RADIUS_XL,
                        padding=Spacing.XL, width="100%", margin_top=Spacing.MD, height="350px"
                    )
                ),

                # Estatísticas
                rx.cond(
                    State.levey_jennings_data.length() > 0,
                    rx.grid(
                        ui.stat_card("Média", State.lj_mean, "target", "primary"),
                        ui.stat_card("Desvio Padrão", State.lj_sd, "variable", "primary"),
                        ui.stat_card("CV% Médio", format_cv(State.lj_cv_mean) + "%", "percent", "primary"),
                        ui.stat_card("Pontos", State.levey_jennings_data.length(), "list", "primary"),
                        columns={"initial": "2", "sm": "4"},
                        spacing="3", width="100%", margin_top=Spacing.MD
                    )
                ),

                # Botão fechar
                rx.hstack(
                    ui.button("Fechar", icon="x", variant="secondary", on_click=State.close_chart_modal),
                    justify_content="flex-end", width="100%", margin_top=Spacing.MD
                ),

                spacing="3", width="100%", padding_top=Spacing.MD
            ),

            style={"max_width": "900px", "max_height": "90vh"},
            overflow_y="auto"
        ),
        open=State.show_chart_modal
    )
