"""
Análise COMPULAB x SIMUS page
Design moderno com upload aprimorado
"""
import reflex as rx
from ..state import State
from ..components.file_upload import compact_upload_card, upload_progress_indicator, large_file_progress_indicator
from ..components import ui
from ..styles import Color, Design

# Card de métrica com design premium e animação
def metric_card(title: str, value: str, icon: str, subtitle: str = "", color: str = "green"):
    color_map = {
        "green": (Color.SUCCESS, Color.SUCCESS_BG),
        "blue": ("#3B82F6", "#EFF6FF"),
        "orange": (Color.WARNING, Color.WARNING_BG),
        "red": (Color.ERROR, Color.ERROR_BG),
    }
    
    fg, bg = color_map.get(color, color_map["green"])
    
    return ui.card(
        rx.vstack(
            rx.hstack(
                rx.box(
                    rx.icon(icon, size=24, color=fg),
                    padding="12px",
                    border_radius="16px",
                    background_color=bg,
                    class_name="flex items-center justify-center",
                ),
                rx.spacer(),
                rx.badge(
                    "ATIVO", 
                    variant="soft", 
                    color_scheme=color,
                    size="1",
                    class_name="rounded-full px-2"
                ),
                width="100%",
                align="center",
            ),
            rx.vstack(
                rx.text(
                    value, 
                    font_size=["1.5rem", "1.75rem", "2rem"], 
                    font_weight="800", 
                    color=Color.DEEP, 
                    line_height="1.2",
                    letter_spacing="-0.02em"
                ),
                rx.text(
                    title, 
                    font_size="0.75rem", 
                    font_weight="700", 
                    color=Color.TEXT_SECONDARY,
                    text_transform="uppercase",
                    letter_spacing="0.05em"
                ),
                rx.text(subtitle, font_size="10px", color="gray", font_weight="500"),
                spacing="1",
                align="start",
            ),
            spacing="4",
            align="start",
        ),
        _hover={
            "transform": "translateY(-4px)",
            "box_shadow": Design.SHADOW_LG,
            "border_color": f"{fg}40"
        }
    )

# Item de breakdown da diferença com design minimalista
def breakdown_item(icon: str, label: str, value: str, color: str = "gray"):
    color_map = {
        "green": "text-green-600",
        "blue": "text-blue-600",
        "orange": "text-orange-600",
        "red": "text-red-600",
        "gray": "text-gray-600",
    }
    fg_color = color_map.get(color, "text-gray-600")
    
    return rx.box(
        rx.hstack(
            rx.box(
                rx.icon(icon, size=18, color=fg_color),
                class_name="bg-gray-50 p-2 rounded-xl"
            ),
            rx.vstack(
                rx.text(label, class_name="text-gray-400 text-[10px] font-bold uppercase tracking-widest"),
                rx.text(value, class_name=f"text-sm font-bold {fg_color}"),
                spacing="0",
                align="start"
            ),
            spacing="3",
            align="center",
        ),
        class_name="bg-white/50 border border-gray-100 p-3 rounded-2xl hover:bg-white transition-colors flex-1"
    )


# Modal para exibir o histórico do paciente com design de Timeline e Funcionalidades Avançadas
def patient_history_modal() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.hstack(
                    rx.box(
                        rx.icon("user", size=24, color="#1B5E20"),
                        class_name="bg-green-50 p-2 rounded-xl"
                    ),
                    rx.vstack(
                        rx.text(
                            State.selected_patient_name, 
                            class_name="text-gray-900 font-black text-xl tracking-tight"
                        ),
                        rx.hstack(
                            rx.badge("PACIENTE", variant="surface", color_scheme="green"),
                            rx.text(
                                "ID: " + State.selected_patient_id, 
                                class_name="text-gray-400 text-xs font-mono"
                            ),
                            spacing="2",
                            align="center"
                        ),
                        spacing="0",
                        align="start"
                    ),
                    rx.spacer(),
                    rx.dialog.close(
                        rx.button(
                            rx.icon("x", size=20),
                            class_name="p-2 hover:bg-gray-100 rounded-full transition-colors text-gray-400"
                        ),
                    ),
                    width="100%",
                    align="center",
                    class_name="pb-4 border-b border-gray-100"
                )
            ),
            
            rx.box(
                rx.vstack(
                    # Stats Row
                    rx.grid(
                        rx.box(
                            rx.vstack(
                                rx.text("Total Auditoria", class_name="text-[10px] font-bold text-gray-400 uppercase"),
                                rx.text("R$ " + State.selected_patient_total_value, class_name="text-lg font-black text-emerald-600"),
                                spacing="0", align="start"
                            ),
                            class_name="bg-emerald-50/50 p-3 rounded-2xl border border-emerald-100"
                        ),
                        rx.box(
                            rx.vstack(
                                rx.text("Exames", class_name="text-[10px] font-bold text-gray-400 uppercase"),
                                rx.text(State.selected_patient_exams_count, class_name="text-lg font-black text-blue-600"),
                                spacing="0", align="start"
                            ),
                            class_name="bg-blue-50/50 p-3 rounded-2xl border border-blue-100"
                        ),
                        rx.box(
                            rx.vstack(
                                rx.text("Status", class_name="text-[10px] font-bold text-gray-400 uppercase"),
                                rx.badge("Em Analise", color_scheme="orange", variant="soft"),
                                spacing="0", align="start"
                            ),
                            class_name="bg-orange-50/50 p-3 rounded-2xl border border-orange-100"
                        ),
                        columns="3",
                        spacing="3",
                        width="100%",
                        class_name="mb-6"
                    ),

                    # Timeline Section
                    rx.text("Timeline de Exames", class_name="text-sm font-bold text-gray-700 mb-2 px-1"),
                    
                    rx.scroll_area(
                        rx.vstack(
                            rx.foreach(
                                State.patient_history_data,
                                lambda exam, i: rx.box(
                                    rx.hstack(
                                        # Indicador Lateral
                                        rx.box(
                                            class_name=rx.cond(
                                                exam.status == "Divergente",
                                                "w-1 bg-red-500 h-full rounded-full",
                                                "w-1 bg-emerald-500 h-full rounded-full"
                                            )
                                        ),
                                        rx.vstack(
                                            rx.hstack(
                                                rx.text(exam.exam_name, class_name="text-sm font-bold text-gray-900"),
                                                rx.spacer(),
                                                rx.text("R$ " + exam.last_value.to_string(), class_name="text-sm font-mono font-bold text-gray-700"),
                                                width="100%",
                                            ),
                                            rx.hstack(
                                                rx.hstack(
                                                    rx.icon("calendar", size=12, color="#9CA3AF"),
                                                    rx.text(exam.created_at, class_name="text-[11px] text-gray-500"),
                                                    spacing="1",
                                                    align="center"
                                                ),
                                                rx.hstack(
                                                    rx.icon("hash", size=12, color="#9CA3AF"),
                                                    rx.text(exam.id, class_name="text-[11px] text-gray-400 font-mono"),
                                                    spacing="1",
                                                    align="center"
                                                ),
                                                rx.badge(
                                                    exam.status, 
                                                    color_scheme=rx.cond(exam.status == "Divergente", "red", "green"),
                                                    size="1"
                                                ),
                                                spacing="3",
                                                align="center"
                                            ),
                                            
                                            # Notas se houver
                                            rx.cond(
                                                exam.notes != "",
                                                rx.box(
                                                    rx.text("Nota: " + exam.notes, class_name="text-[10px] text-gray-500 italic"),
                                                    class_name="bg-gray-50 p-2 rounded-lg mt-2",
                                                    width="100%"
                                                )
                                            ),
                                            spacing="1",
                                            width="100%",
                                            align="start",
                                            class_name="pl-3"
                                        ),
                                        width="100%",
                                        align="stretch",
                                        class_name="py-3 px-2 border-b border-gray-50 last:border-0 hover:bg-gray-50/50 transition-colors"
                                    ),
                                    width="100%"
                                )
                            ),
                            width="100%",
                            spacing="0",
                        ),
                        style={"maxHeight": "400px"},
                        type="always",
                        class_name="pr-4"
                    ),
                    
                    width="100%",
                ),
                class_name="py-4"
            ),
            
            class_name="max-w-xl rounded-[32px] p-8 bg-white/95 backdrop-blur-xl border border-white/20 shadow-2xl",
        ),
    )

# Tabela com ações (Ver Histórico / Resolver) - Design Refinado
def action_table(headers: list[str], data: list, columns_keys: list[str], patient_key: str = "patient", is_divergence: bool = False) -> rx.Component:
    return rx.box(
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    *[rx.table.column_header_cell(
                        rx.text(header, class_name="text-gray-500 font-bold text-[11px] uppercase tracking-wider"),
                        class_name="bg-gray-50/80 px-4 py-3 border-b border-gray-100"
                    ) for header in headers],
                    rx.table.column_header_cell(
                        rx.text("AÇÕES", class_name="text-gray-500 font-bold text-[11px] uppercase tracking-wider"),
                        class_name="bg-gray-50/80 px-4 py-3 border-b border-gray-100 text-right"
                    )
                )
            ),
            rx.table.body(
                rx.foreach(
                    data,
                    lambda item, i: rx.table.row(
                        *[rx.table.cell(
                            rx.text(item[key], class_name="text-gray-700 text-sm font-medium"),
                            class_name="px-4 py-3"
                        ) for key in columns_keys],
                        rx.table.cell(
                            rx.hstack(
                                rx.button(
                                    rx.icon("history", size=14, color="#1B5E20"),
                                    on_click=lambda: State.view_patient_history(item[patient_key]),
                                    class_name="bg-green-50 p-2 rounded-lg hover:bg-green-100 transition-colors"
                                ),
                                rx.button(
                                    rx.icon("circle-check", size=14, color="#6B7280"),
                                    class_name="bg-gray-50 p-2 rounded-lg hover:bg-gray-200 transition-colors"
                                ),
                                spacing="2",
                                justify="end"
                            ),
                            class_name="px-4 py-3"
                        ),
                        class_name=rx.cond(i % 2 == 0, "bg-white", "bg-gray-50/30")
                    )
                )
            ),
            variant="surface",
            class_name="w-full border-none overflow-hidden rounded-2xl"
        ),
        class_name="bg-white border border-gray-100 rounded-2xl shadow-sm overflow-hidden"
    )


def analise_page() -> rx.Component:
    """Página de análise comparativa - Design oficial aprimorado"""
    
    # SVG compacto do Erlenmeyer
    erlenmeyer_small = """
        <svg viewBox="0 0 50 60" width="36" height="44">
            <path d="M18 8 L32 8 L32 22 L42 50 Q43 54 39 56 L11 56 Q7 54 8 50 L18 22 Z" 
                  fill="none" stroke="#1B5E20" stroke-width="2"/>
            <circle cx="25" cy="42" r="6" fill="#4CAF50" opacity="0.3"/>
        </svg>
    """
    
    # SVG compacto dos Tubos
    tubes_small = """
        <svg viewBox="0 0 60 60" width="36" height="44">
            <rect x="12" y="10" width="10" height="40" rx="5" fill="none" stroke="#1B5E20" stroke-width="2"/>
            <rect x="25" y="10" width="10" height="40" rx="5" fill="none" stroke="#1B5E20" stroke-width="2"/>
            <rect x="38" y="10" width="10" height="40" rx="5" fill="none" stroke="#1B5E20" stroke-width="2"/>
            <rect x="12" y="28" width="10" height="22" rx="5" fill="#4CAF50" opacity="0.3"/>
            <rect x="25" y="24" width="10" height="26" rx="5" fill="#4CAF50" opacity="0.3"/>
            <rect x="38" y="32" width="10" height="18" rx="5" fill="#4CAF50" opacity="0.3"/>
        </svg>
    """
    
    return rx.box(
        rx.vstack(
            # Animated Header
            rx.box(
                ui.animated_heading("Análise COMPULAB × SIMUS", level=1),
                class_name="py-12 w-full flex justify-center"
            ),
            
            # Upload section
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.text("📁", class_name="text-lg"),
                        rx.text(
                            "Upload de Arquivos",
                            class_name="text-[#1B5E20] font-semibold"
                        ),
                        spacing="2",
                        align="center",
                    ),
                    rx.text(
                        "Aceita arquivos PDF, CSV ou Excel/XSL",
                        class_name="text-gray-500 text-xs mb-3"
                    ),
                    rx.grid(
                        compact_upload_card(
                            title="COMPULAB",
                            icon_svg=erlenmeyer_small,
                            upload_id="compulab_analysis",
                            file_name=State.compulab_file_name,
                            file_size=State.compulab_file_size,
                            on_upload=State.handle_compulab_upload,
                            on_remove=State.clear_compulab_file,
                            accepted_types="COMPLETO",
                        ),
                        compact_upload_card(
                            title="SIMUS",
                            icon_svg=tubes_small,
                            upload_id="simus_analysis",
                            file_name=State.simus_file_name,
                            file_size=State.simus_file_size,
                            on_upload=State.handle_simus_upload,
                            on_remove=State.clear_simus_file,
                            accepted_types="COMPLETO",
                        ),
                        columns={"initial": "1", "sm": "2"},
                        spacing="4",
                        width="100%",
                    ),
                    upload_progress_indicator(State.is_uploading, "Carregando arquivo..."),
                    spacing="2",
                    width="100%",
                ),
                class_name="bg-white border border-gray-200 rounded-2xl p-5 mt-8 max-w-xl w-full shadow-sm"
            ),
            
            # Botão de análise
            rx.button(
                rx.cond(
                    State.is_analyzing,
                    rx.hstack(
                        rx.spinner(size="1", color="white"),
                        rx.text("Analisando dados..."),
                        spacing="2",
                        align="center",
                    ),
                    rx.hstack(
                        rx.icon("search", size=18),
                        rx.text("Analisar Faturamento"),
                        spacing="2",
                        align="center",
                    ),
                ),
                on_click=State.run_analysis,
                disabled=~State.has_files | State.is_analyzing,
                class_name="bg-[#1B5E20] text-white px-8 py-3 rounded-xl font-semibold hover:bg-[#2E7D32] hover:shadow-lg transition-all mt-6 disabled:opacity-50 disabled:cursor-not-allowed"
            ),
            
            # Indicador de progresso
            rx.cond(
                State.is_analyzing,
                rx.box(
                    rx.vstack(
                        rx.text(
                            State.analysis_progress_percentage.to_string() + "%",
                            class_name="text-[#1B5E20] text-3xl font-bold text-center"
                        ),
                        rx.text(
                            State.analysis_stage,
                            class_name="text-gray-600 text-sm text-center mt-1"
                        ),
                        # Barra de progresso
                        rx.box(
                            rx.box(
                                class_name="h-full bg-[#4CAF50] rounded-full transition-all duration-300",
                                width=rx.cond(
                                    State.analysis_progress_percentage > 0,
                                    State.analysis_progress_percentage.to_string() + "%",
                                    "0%"
                                ),
                            ),
                            class_name="w-full h-3 bg-gray-200 rounded-full overflow-hidden mt-4",
                        ),
                        spacing="2",
                        align="center",
                    ),
                    class_name="bg-white border border-gray-200 rounded-xl p-6 mt-4 max-w-4xl w-full shadow-sm"
                ),
            ),
            
            # Mensagens
            rx.cond(
                State.success_message != "",
                rx.box(
                    rx.hstack(
                        rx.icon("circle-check", size=20, color="#15803d"),
                        rx.text(State.success_message, class_name="text-green-700"),
                        spacing="2",
                    ),
                    class_name="bg-green-50 border border-green-200 rounded-xl p-4 mt-4 max-w-xl w-full"
                ),
            ),
            rx.cond(
                State.error_message != "",
                rx.box(
                    rx.hstack(
                        rx.icon("circle-x", size=20, color="#dc2626"),
                        rx.text(State.error_message, class_name="text-red-700"),
                        spacing="2",
                    ),
                    class_name="bg-red-50 border border-red-200 rounded-xl p-4 mt-4 max-w-xl w-full"
                ),
            ),
            
            # Resultados
            rx.cond(
                State.has_analysis,
                rx.vstack(
                    # Métricas principais
                    rx.box(
                        rx.vstack(
                            rx.hstack(
                                rx.box(
                                    rx.icon("bar-chart-3", size=24, color=Color.DEEP),
                                    class_name="p-2 bg-green-50 rounded-xl"
                                ),
                                rx.vstack(
                                    rx.text(
                                        "Resumo Executivo da Análise",
                                        class_name="text-gray-900 font-bold text-xl tracking-tight"
                                    ),
                                    rx.text(
                                        "Consolidação financeira dos sistemas integrados",
                                        class_name="text-gray-400 text-xs font-medium"
                                    ),
                                    spacing="0",
                                    align="start",
                                ),
                                rx.spacer(),
                                rx.badge(
                                    "CONCLUÍDO",
                                    color_scheme="green",
                                    variant="surface",
                                    size="2",
                                    class_name="rounded-full px-4"
                                ),
                                spacing="3",
                                align="center",
                                width="100%",
                                class_name="mb-6"
                            ),
                            
                            rx.grid(
                                metric_card("COMPULAB Total", State.formatted_compulab_total, "landmark", State.compulab_count.to_string() + " pacientes", "green"),
                                metric_card("SIMUS Total", State.formatted_simus_total, "database", State.simus_count.to_string() + " pacientes", "blue"),
                                metric_card("Diferença Bruta", State.formatted_difference, "git-compare", "COMPULAB - SIMUS", "orange"),
                                metric_card("Alertas de Exame", State.missing_exams_count.to_string(), "circle-alert", "itens faltantes", "red"),
                                columns={"initial": "1", "sm": "2", "lg": "4"},
                                spacing="4",
                                width="100%",
                            ),
                            
                            # Barra de Progresso da Auditoria
                            rx.box(
                                rx.vstack(
                                    rx.hstack(
                                        rx.vstack(
                                            rx.text("Status da Auditoria Local", class_name="text-sm font-bold text-gray-700"),
                                            rx.text("Divergências tratadas nesta sessão", class_name="text-[10px] text-gray-400 font-medium"),
                                            spacing="0",
                                            align="start",
                                        ),
                                        rx.spacer(),
                                        rx.box(
                                            rx.text(State.resolution_progress.to_string() + "%", class_name="text-lg font-black text-emerald-600"),
                                            class_name="bg-emerald-50 px-3 py-1 rounded-lg border border-emerald-100"
                                        ),
                                        width="100%",
                                        align="center",
                                    ),
                                    rx.box(
                                        rx.box(
                                            class_name="h-full bg-gradient-to-r from-emerald-400 to-emerald-600 rounded-full transition-all duration-1000 ease-in-out",
                                            width=State.resolution_progress.to_string() + "%",
                                        ),
                                        class_name="w-full h-3 bg-gray-100 rounded-full overflow-hidden shadow-inner border border-gray-50",
                                    ),
                                    spacing="3",
                                    width="100%",
                                ),
                                class_name="mt-8 p-6 bg-gray-50/50 border border-gray-100 rounded-3xl w-full"
                            ),
                            width="100%",
                        ),
                        class_name="bg-white border border-gray-100 rounded-[32px] p-8 mt-12 w-full shadow-sm"
                    ),
                    
                    # === DASHBOARD ANALÍTICO REFINADO ===
                    rx.box(
                        rx.vstack(
                            # Header com Total de Perda
                            rx.hstack(
                                rx.vstack(
                                    rx.hstack(
                                        rx.icon("layout-dashboard", size=22, color=Color.DEEP),
                                        rx.text("Dashboard de Inteligência", class_name="text-gray-900 font-black text-xl tracking-tight"),
                                        spacing="2",
                                        align="center",
                                    ),
                                    rx.text("Visualização analítica das divergências identificadas", class_name="text-gray-400 text-xs"),
                                    spacing="0",
                                    align="start",
                                ),
                                rx.spacer(),
                                # Card de Perda Total
                                rx.box(
                                    rx.vstack(
                                        rx.text("PERDA TOTAL IDENTIFICADA", class_name="text-[9px] font-bold text-red-400 uppercase tracking-widest"),
                                        rx.text(State.formatted_total_leakage, class_name="text-2xl font-black text-red-600"),
                                        spacing="0",
                                        align="end",
                                    ),
                                    class_name="bg-red-50/80 border border-red-100 px-4 py-2 rounded-2xl"
                                ),
                                width="100%",
                                align="center",
                                class_name="mb-6"
                            ),
                            
                            # Grid com Gráficos Refinados
                            rx.grid(
                                # Pie Chart - Composição da Perda
                                rx.box(
                                    rx.vstack(
                                        rx.hstack(
                                            rx.icon("pie-chart", size=16, color="#6B7280"),
                                            rx.text("Composição da Perda", class_name="text-sm font-bold text-gray-700"),
                                            spacing="2",
                                            align="center",
                                        ),
                                        rx.recharts.pie_chart(
                                            rx.recharts.pie(
                                                data=State.revenue_distribution_data,
                                                data_key="value",
                                                name_key="name",
                                                cx="50%",
                                                cy="50%",
                                                inner_radius=45,
                                                outer_radius=75,
                                                padding_angle=3,
                                                stroke="#fff",
                                                label=True,
                                            ),
                                            rx.recharts.graphing_tooltip(),
                                            rx.recharts.legend(
                                                icon_type="circle",
                                                icon_size=8,
                                                vertical_align="bottom",
                                            ),
                                            width="100%",
                                            height=250,
                                        ),
                                        width="100%",
                                        spacing="3",
                                    ),
                                    class_name="bg-white border border-gray-100 rounded-3xl p-5 shadow-sm hover:shadow-md transition-shadow"
                                ),
                                
                                # Bar Chart - Top Exames
                                rx.box(
                                    rx.vstack(
                                        rx.hstack(
                                            rx.icon("bar-chart-2", size=16, color="#3B82F6"),
                                            rx.text("Top Exames Problemáticos", class_name="text-sm font-bold text-gray-700"),
                                            spacing="2",
                                            align="center",
                                        ),
                                        rx.recharts.bar_chart(
                                            rx.recharts.bar(
                                                data_key="value",
                                                fill="#3B82F6",
                                                radius=[6, 6, 0, 0],
                                            ),
                                            rx.recharts.x_axis(
                                                data_key="name", 
                                                tick_size=6,
                                                angle=-20,
                                                text_anchor="end",
                                            ),
                                            rx.recharts.y_axis(width=55),
                                            rx.recharts.graphing_tooltip(),
                                            rx.recharts.cartesian_grid(stroke_dasharray="3 3", opacity=0.3),
                                            data=State.top_exams_discrepancy_data,
                                            width="100%",
                                            height=250,
                                        ),
                                        width="100%",
                                        spacing="3",
                                    ),
                                    class_name="bg-white border border-gray-100 rounded-3xl p-5 shadow-sm hover:shadow-md transition-shadow"
                                ),
                                columns={"initial": "1", "lg": "2"},
                                spacing="4",
                                width="100%",
                            ),
                            
                            # === CENTRAL DE AÇÕES (SIMPLIFICADA) ===
                            rx.box(
                                rx.vstack(
                                    rx.hstack(
                                        rx.box(
                                            rx.icon("lightbulb", size=18, color="white"),
                                            class_name="bg-gradient-to-r from-amber-400 to-orange-500 p-2 rounded-lg shadow-sm"
                                        ),
                                        rx.vstack(
                                            rx.text("Central de Ações Recomendadas", class_name="text-gray-900 font-bold text-base"),
                                            rx.text("Sugestões ordenadas por impacto financeiro", class_name="text-gray-400 text-[10px]"),
                                            spacing="0",
                                            align="start",
                                        ),
                                        rx.spacer(),
                                        spacing="3",
                                        align="center",
                                        width="100%",
                                    ),
                                    rx.divider(class_name="my-4 opacity-50"),
                                    rx.foreach(
                                        State.action_center_insights,
                                        lambda insight: rx.box(
                                            rx.hstack(
                                                # Ícone
                                                rx.box(
                                                    rx.icon(insight["icon"], size=18, color="#F59E0B"),
                                                    class_name="bg-amber-50 p-2.5 rounded-xl"
                                                ),
                                                # Texto
                                                rx.vstack(
                                                    rx.text(insight["title"], class_name="text-sm font-bold text-gray-800"),
                                                    rx.text(insight["description"], class_name="text-[11px] text-gray-500 leading-relaxed"),
                                                    spacing="1",
                                                    align="start",
                                                    class_name="flex-1"
                                                ),
                                                spacing="3",
                                                align="center",
                                                width="100%",
                                            ),
                                            class_name="p-4 bg-white border border-gray-100 rounded-2xl hover:border-amber-200 hover:shadow-sm transition-all mb-3"
                                        )
                                    ),
                                    width="100%",
                                ),
                                class_name="bg-gradient-to-br from-amber-50/50 to-orange-50/30 border border-amber-100/50 rounded-3xl p-5 mt-6"
                            ),

                            
                            # Breakdown numérico secundário
                            rx.box(
                                rx.hstack(
                                    rx.icon("calculator", size=16, color="#6B7280"),
                                    rx.text("Resumo Numérico", class_name="text-sm font-bold text-gray-600"),
                                    spacing="2",
                                    align="center",
                                    class_name="mb-3"
                                ),
                                rx.grid(
                                    breakdown_item("users", "Pacientes Faltantes", State.formatted_missing_patients_total, "orange"),
                                    breakdown_item("file-warning", "Exames Faltantes", State.formatted_missing_exams_total, "red"),
                                    breakdown_item("coins", "Divergências Valor", State.formatted_divergences_total, "blue"),
                                    breakdown_item("circle-plus", "Extras no SIMUS", State.extra_simus_exams_count.to_string() + " exames", "gray"),
                                    columns={"initial": "2", "lg": "4"},
                                    spacing="3",
                                    width="100%",
                                ),
                                class_name="mt-6"
                            ),
                            

                            width="100%",
                        ),
                        class_name="bg-gradient-to-br from-slate-50 to-white border border-gray-100 rounded-[32px] p-6 mt-8 w-full shadow-sm"
                    ),


                    # Tabs de detalhes usando Segmented Control
                    ui.segmented_control(
                        [
                            {"label": f"Pct Faltantes ({State.missing_patients_count})", "value": "patients_missing"},
                            {"label": f"Exames Faltantes ({State.missing_exams_count})", "value": "missing"},
                            {"label": f"Divergências ({State.divergences_count})", "value": "divergences"},
                            {"label": f"Extras Simus ({State.extra_simus_exams_count})", "value": "extras"},
                            {"label": "Análise IA", "value": "ai"},
                        ],
                        State.analysis_active_tab,
                        State.set_analysis_active_tab
                    ),

                    rx.box(
                        rx.cond(
                            State.analysis_active_tab == "patients_missing",
                            rx.cond(
                                State.missing_patients_count > 0,
                                action_table(headers=["Paciente", "Exames", "Valor Total (R$)"], data=State.missing_patients, columns_keys=["name", "total_exams", "total_value"], patient_key="name"),
                                rx.box(rx.hstack(rx.icon("circle-check", size=20, color="#10B981"), rx.text("Todos os pacientes do COMPULAB estão no SIMUS!", class_name="text-green-700"), spacing="2", align="center"), class_name="bg-green-50 border border-green-200 rounded-xl p-6 mt-4")
                            )
                        ),
                        rx.cond(
                            State.analysis_active_tab == "missing",
                            rx.cond(
                                State.missing_exams_count > 0,
                                action_table(headers=["Paciente", "Exame", "Valor (R$)"], data=State.missing_exams, columns_keys=["patient", "exam_name", "value"]),
                                rx.box(rx.hstack(rx.icon("circle-check", size=20, color="#10B981"), rx.text("Todos os exames do COMPULAB estão no SIMUS!", class_name="text-green-700"), spacing="2", align="center"), class_name="bg-green-50 border border-green-200 rounded-xl p-6 mt-4")
                            )
                        ),
                        rx.cond(
                            State.analysis_active_tab == "divergences",
                            rx.cond(
                                State.divergences_count > 0,
                                action_table(headers=["Paciente", "Exame", "COMPULAB", "SIMUS", "Diferença"], data=State.value_divergences, columns_keys=["patient", "exam_name", "compulab_value", "simus_value", "difference"], is_divergence=True),
                                rx.box(rx.hstack(rx.icon("circle-check", size=20, color="#10B981"), rx.text("Não há divergências de valor!", class_name="text-green-700"), spacing="2", align="center"), class_name="bg-green-50 border border-green-200 rounded-xl p-6 mt-4")
                            )
                        ),
                        rx.cond(
                            State.analysis_active_tab == "extras",
                            rx.cond(
                                State.extra_simus_exams_count > 0,
                                action_table(headers=["Paciente", "Exame", "Valor SIMUS"], data=State.extra_simus_exams, columns_keys=["patient", "exam_name", "simus_value"]),
                                rx.box(rx.hstack(rx.icon("check-check", size=20, color="#10B981"), rx.text("Nenhum exame extra ('fantasma') encontrado no SIMUS.", class_name="text-green-700"), spacing="2", align="center"), class_name="bg-green-50 border border-green-200 rounded-xl p-6 mt-4")
                            )
                        ),
                        rx.cond(
                            State.analysis_active_tab == "ai",
                            rx.box(
                                rx.vstack(
                                    # Header Premium
                                    rx.box(
                                        rx.hstack(
                                            rx.box(rx.icon("bot", size=24, color="white"), class_name="bg-white/20 p-2 rounded-xl"),
                                            rx.vstack(
                                                rx.text("Auditoria Inteligente (Beta)", class_name="text-white font-bold text-lg tracking-tight"),
                                                rx.text("Análise profunda de padrões via GPT-4 Turbo", class_name="text-white/80 text-[10px] uppercase font-medium tracking-widest"),
                                                spacing="0", align="start"
                                            ),
                                            rx.spacer(),
                                            rx.badge("IA ATIVA", variant="soft", color_scheme="green", size="1"),
                                            spacing="3", align="center"
                                        ),
                                        class_name="bg-gradient-to-r from-emerald-600 to-teal-700 p-6 rounded-2xl mb-6 shadow-md"
                                    ),
                                    
                                    rx.cond(
                                        State.is_generating_ai,
                                        rx.box(
                                            rx.vstack(
                                                rx.hstack(
                                                    rx.spinner(size="1", color="green"),
                                                    rx.text(State.ai_loading_text, class_name="text-sm font-medium text-gray-700"),
                                                    spacing="2",
                                                ),
                                                rx.progress(value=State.ai_loading_progress, max=100, class_name="w-full h-2 rounded-full", color_scheme="green"),
                                                spacing="2", width="100%"
                                            ),
                                            class_name="bg-green-50 p-4 rounded-xl w-full mb-4 border border-green-100"
                                        ),
                                    ),

                                    # Seletor de Modelo e Provedor
                                    rx.box(
                                        rx.vstack(
                                            rx.text("Modelo de IA", class_name="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2"),
                                            
                                            # Seletor de Provedor (Macro)
                                            ui.segmented_control(
                                                [
                                                    {"label": "OpenAI", "value": "OpenAI"},
                                                    {"label": "Google Gemini", "value": "Gemini"},
                                                ],
                                                State.ai_provider,
                                                State.set_ai_provider
                                            ),

                                            # Seletor de Modelo (Específico)
                                            rx.cond(
                                                State.ai_provider == "OpenAI",
                                                rx.select(
                                                    ["gpt-4o", "gpt-4-turbo"],
                                                    value=State.ai_model,
                                                    on_change=State.set_ai_model,
                                                    class_name="w-full mt-2 p-2 border border-gray-200 rounded-xl bg-white text-sm"
                                                ),
                                                rx.select(
                                                    ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro", "gemini-3-pro-preview", "gemini-3-flash-preview"],
                                                    value=State.ai_model,
                                                    on_change=State.set_ai_model,
                                                    class_name="w-full mt-2 p-2 border border-gray-200 rounded-xl bg-white text-sm"
                                                )
                                            ),
                                            
                                            width="100%",
                                            align="start"
                                        ),
                                        class_name="mb-6 w-full"
                                    ),

                                    rx.button(
                                        rx.hstack(
                                            rx.cond(State.is_generating_ai, rx.spinner(size="1", color="white"), rx.icon("rocket", size=18, color="white")),
                                            rx.text("Iniciar Auditoria Inteligente"),
                                            spacing="2"
                                        ),
                                        on_click=State.generate_ai_analysis,
                                        disabled=State.is_generating_ai,
                                        class_name="bg-gradient-to-r from-emerald-500 to-green-600 text-white px-6 py-3 rounded-xl font-bold hover:shadow-lg transition-all w-full disabled:opacity-50"
                                    ),

                                    rx.cond(
                                        State.ai_analysis != "",
                                        rx.vstack(
                                            rx.box(
                                                rx.scroll_area(
                                                    rx.markdown(State.ai_analysis),
                                                    type="hover"
                                                ),
                                                style={"maxHeight": "500px"},
                                                class_name="bg-white rounded-xl p-6 border border-gray-100 mt-6 prose prose-sm max-w-none shadow-sm"
                                            ),
                                            rx.hstack(
                                                rx.cond(
                                                    State.ai_analysis_csv != "",
                                                    rx.link(
                                                        rx.button(rx.hstack(rx.icon("table", size=14), rx.text("CSV"), spacing="1"), class_name="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-blue-700"),
                                                        href=State.ai_analysis_csv, download="Auditoria_IA.csv"
                                                    ),
                                                ),
                                                rx.button(rx.hstack(rx.icon("rotate-ccw", size=14), rx.text("Refazer"), spacing="1"), on_click=State.generate_ai_analysis, class_name="border-2 border-orange-500 text-orange-600 px-4 py-2 rounded-lg text-sm font-semibold hover:bg-orange-50"),
                                                spacing="2", class_name="mt-4"
                                            ),
                                            width="100%"
                                        ),
                                    ),
                                    width="100%", class_name="mt-2"
                                ),
                                width="100%"
                            )
                        ),
                        width="100%",
                        padding_top="1rem"
                    ),
                    
                    # Ações do Relatório Final
                    rx.hstack(
                        rx.cond(
                            State.analysis_pdf != "",
                            rx.link(
                                rx.button(rx.hstack(rx.icon("download", size=16), rx.text("Download PDF"), spacing="2"), class_name="bg-[#1B5E20] text-white px-6 py-2 rounded-lg hover:shadow-lg transition-all font-semibold"),
                                download="analise_faturamento.pdf",
                                href=State.analysis_pdf
                            ),
                        ),
                        rx.button(rx.hstack(rx.icon("file-text", size=16), rx.text("Gerar PDF"), spacing="2"), on_click=State.generate_pdf_report, class_name="bg-[#1B5E20] text-white px-6 py-2 rounded-lg hover:shadow-lg transition-all font-semibold"),
                        rx.button(rx.hstack(rx.icon("refresh-cw", size=16), rx.text("Nova Análise"), spacing="2"), on_click=State.clear_all_files, class_name="bg-white border border-gray-300 text-gray-600 px-4 py-2 rounded-lg hover:bg-gray-50 transition-all font-medium"),
                        spacing="3",
                        justify="center",
                        class_name="mt-10"
                    ),
                    width="100%",
                    max_width="5xl",
                ),
            ),
            
            patient_history_modal(),
            spacing="0",
            align="center",
            width="100%",
            class_name="py-8 px-4"
        ),
        width="100%",
    )
