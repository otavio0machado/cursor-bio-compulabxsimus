"""
Componentes de UI para Análise Profunda (Deep Analysis)
"""
import reflex as rx


def analysis_status_banner(status: rx.Var, executive_summary: rx.Var) -> rx.Component:
    """Banner de status da análise"""
    
    return rx.cond(
        status == "critical",
        rx.box(
            rx.hstack(
                rx.icon("circle-alert", color="#DC2626", size=24),
                rx.text(
                    "⚠️ Atenção: Diferenças Significativas Detectadas",
                    font_weight="700",
                    color="#991B1B",
                    font_size="1rem"
                ),
                spacing="4",
                align_items="center",
                width="100%"
            ),
            bg="#FEF2F2",
            border="1px solid #FCA5A5",
            border_radius="16px",
            padding="16px",
            margin_bottom="24px",
            width="100%"
        ),
        rx.cond(
            status == "warning",
            rx.box(
                rx.hstack(
                    rx.icon("triangle-alert", color="#D97706", size=24),
                    rx.text(
                        "⚡ Alerta: Revisão Recomendada",
                        font_weight="700",
                        color="#92400E",
                        font_size="1rem"
                    ),
                    spacing="4",
                    align_items="center",
                    width="100%"
                ),
                bg="#FFFBEB",
                border="1px solid #FCD34D",
                border_radius="16px",
                padding="16px",
                margin_bottom="24px",
                width="100%"
            ),
            rx.cond(
                status == "ok",
                rx.box(
                    rx.hstack(
                        rx.icon("circle-check", color="#16A34A", size=24),
                        rx.text(
                            "✅ Análise Concluída: Diferenças Explicadas",
                            font_weight="700",
                            color="#166534",
                            font_size="1rem"
                        ),
                        spacing="4",
                        align_items="center",
                        width="100%"
                    ),
                    bg="#F0FDF4",
                    border="1px solid #86EFAC",
                    border_radius="16px",
                    padding="16px",
                    margin_bottom="24px",
                    width="100%"
                ),
                rx.box()
            )
        )
    )


def extra_patients_badge(count: rx.Var, value: rx.Var) -> rx.Component:
    """Badge indicando pacientes extras encontrados no COMPULAB"""
    
    return rx.cond(
        count > 0,
        rx.box(
            rx.hstack(
                rx.icon("users", color="#2563EB", size=20),
                rx.vstack(
                    rx.hstack(
                        rx.text(count, font_weight="700", color="#1E40AF", font_size="1rem"),
                        rx.text("Paciente(s) Extras no COMPULAB", font_weight="600", color="#1E40AF", font_size="0.95rem"),
                        spacing="2",
                        align_items="center"
                    ),
                    rx.hstack(
                        rx.text("Valor total:", font_size="0.875rem", color="#3B82F6"),
                        rx.text(value, font_size="0.875rem", color="#3B82F6", font_weight="600"),
                        spacing="1",
                        align_items="center"
                    ),
                    spacing="0",
                    align_items="start"
                ),
                spacing="3",
                align_items="center"
            ),
            bg="#EFF6FF",
            border="1px solid #BFDBFE",
            border_radius="16px",
            padding="16px",
            width="100%"
        ),
        rx.box()
    )


def repeated_exams_alert(count: rx.Var, value: rx.Var) -> rx.Component:
    """Alerta destacando exames repetidos encontrados"""
    
    return rx.cond(
        count > 0,
        rx.box(
            rx.hstack(
                rx.icon("copy-x", color="#DC2626", size=20),
                rx.vstack(
                    rx.hstack(
                        rx.hstack(
                            rx.text(count, font_weight="700", color="#991B1B", font_size="1rem"),
                            rx.text("Exame(s) Repetido(s)", font_weight="600", color="#991B1B", font_size="0.95rem"),
                            spacing="2",
                            align_items="center"
                        ),
                        rx.badge("REVISAR", color_scheme="red", size="1", variant="soft"),
                        spacing="2",
                        align_items="center"
                    ),
                    rx.hstack(
                        rx.text("Possível duplicidade:", font_size="0.875rem", color="#DC2626"),
                        rx.text(value, font_size="0.875rem", color="#DC2626", font_weight="600"),
                        spacing="1",
                        align_items="center"
                    ),
                    spacing="0",
                    align_items="start"
                ),
                spacing="3",
                align_items="center"
            ),
            bg="#FEF2F2",
            border="1px solid #FECACA",
            border_radius="16px",
            padding="16px",
            width="100%"
        ),
        rx.box(
            rx.hstack(
                rx.icon("circle-check", color="#16A34A", size=20),
                rx.text("Nenhum exame repetido detectado", font_weight="500", color="#166534", font_size="0.95rem"),
                spacing="3",
                align_items="center"
            ),
            bg="#F0FDF4",
            border="1px solid #86EFAC",
            border_radius="16px",
            padding="16px",
            width="100%"
        )
    )


def executive_summary_card(summary: rx.Var) -> rx.Component:
    """Card de resumo executivo com métricas principais"""
    
    return rx.cond(
        summary != None,
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.icon("file-text", color="#10B981", size=22),
                    rx.text("Resumo Executivo", font_weight="700", color="#064E3B", font_size="1.1rem"),
                    rx.spacer(),
                    rx.badge("Análise Completa", color_scheme="green", size="2"),
                    width="100%",
                    spacing="3",
                    align_items="center",
                    padding_bottom="12px",
                    border_bottom="1px solid #E2E8F0"
                ),
                rx.text(
                    "Análise comparativa entre COMPULAB e SIMUS concluída. "
                    "Verifique os detalhes abaixo para identificar divergências.",
                    font_size="0.9rem",
                    color="#64748B"
                ),
                spacing="4",
                width="100%",
                align_items="start"
            ),
            bg="white",
            border="1px solid #E2E8F0",
            border_radius="24px",
            padding="24px",
            margin_bottom="32px",
            width="100%",
            box_shadow="0 4px 6px -1px rgba(0, 0, 0, 0.05)"
        ),
        rx.box()
    )


def difference_breakdown_panel(
    breakdown: rx.Var,
    extra_patients_formatted: rx.Var,
    repeated_exams_formatted: rx.Var,
    residual_formatted: rx.Var
) -> rx.Component:
    """Painel mostrando a explicação passo a passo da diferença"""
    
    return rx.cond(
        breakdown != None,
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.icon("calculator", color="#10B981", size=22),
                    rx.text("Explicação da Diferença", font_weight="700", color="#064E3B", font_size="1.1rem"),
                    rx.spacer(),
                    rx.badge("Detalhado", color_scheme="blue", size="2"),
                    width="100%",
                    spacing="3",
                    align_items="center",
                    padding_bottom="12px",
                    border_bottom="1px solid #E2E8F0"
                ),
                
                rx.grid(
                    rx.box(
                        rx.vstack(
                            rx.text("Pacientes Extras", font_size="0.8rem", color="#64748B"),
                            rx.text(extra_patients_formatted, font_size="1rem", font_weight="600", color="#1E40AF"),
                            spacing="1",
                            align_items="start"
                        ),
                        padding="16px",
                        bg="#EFF6FF",
                        border="1px solid #BFDBFE",
                        border_radius="16px",
                        width="100%"
                    ),
                    rx.box(
                        rx.vstack(
                            rx.text("Exames Repetidos", font_size="0.8rem", color="#64748B"),
                            rx.text(repeated_exams_formatted, font_size="1rem", font_weight="600", color="#991B1B"),
                            spacing="1",
                            align_items="start"
                        ),
                        padding="16px",
                        bg="#FEF2F2",
                        border="1px solid #FECACA",
                        border_radius="16px",
                        width="100%"
                    ),
                    rx.box(
                        rx.vstack(
                            rx.text("Diferença Não Explicada", font_size="0.8rem", color="#64748B"),
                            rx.text(residual_formatted, font_size="1rem", font_weight="600", color="#F59E0B"),
                            spacing="1",
                            align_items="start"
                        ),
                        padding="16px",
                        bg="#FFFBEB",
                        border="1px solid #FCD34D",
                        border_radius="16px",
                        width="100%"
                    ),
                    columns={"initial": "1", "md": "3"},
                    spacing="4",
                    width="100%"
                ),
                
                rx.box(
                    rx.hstack(
                        rx.icon("info", color="#10B981", size=16),
                        rx.text(
                            "A análise considera pacientes extras no COMPULAB, "
                            "exames repetidos e divergências de valores.",
                            font_size="0.85rem",
                            color="#0F172A",
                            font_style="italic"
                        ),
                        spacing="2",
                        align_items="start"
                    ),
                    padding="12px",
                    bg="#EFF6FF",
                    border_radius="16px",
                    border="1px solid #BFDBFE",
                    width="100%"
                ),
                
                spacing="4",
                width="100%",
                align_items="start"
            ),
            bg="white",
            border="1px solid #E2E8F0",
            border_radius="24px",
            padding="24px",
            margin_bottom="32px",
            width="100%",
            box_shadow="0 4px 6px -1px rgba(0, 0, 0, 0.05)"
        ),
        rx.box()
    )
