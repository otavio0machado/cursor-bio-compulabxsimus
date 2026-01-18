import reflex as rx
from ..state import State
from ..styles import Color
from ..components import ui

def quick_access_card(title: str, description: str, icon: str, page: str, color: str) -> rx.Component:
    """Card de acesso rápido padronizado"""
    return ui.card(
        rx.vstack(
            rx.box(
                rx.icon(icon, size=32, color=f"var(--c-{color}-600)"),
                class_name=f"text-{color}-600 bg-{color}-50 p-4 rounded-2xl mb-2"
            ),
            ui.heading(title, level=3),
            ui.text(description, size="body"),
            align_items="start",
            spacing="2"
        ),
        on_click=lambda: State.set_page(page),
        class_name="cursor-pointer hover:shadow-lg transition-all duration-300 h-full group border-transparent hover:border-green-200"
    )

def dashboard_page() -> rx.Component:
    """Página Dashboard Principal - Refatorada com UI Kit"""
    return rx.box(
        rx.vstack(
            # Welcome Banner
            rx.box(
                ui.animated_heading("Bem-vindo de volta", level=1),
                class_name="py-12 w-full flex justify-center"
            ),
            
            # Stats Grid
            rx.grid(
                ui.stat_card(
                    "Controle de Qualidade", 
                    f"{State.total_qc_today}", 
                    "activity", 
                    "success", 
                    "Registros hoje"
                ),
                ui.stat_card(
                    "Taxa de Aprovação", 
                    f"{State.qc_approval_rate}%", 
                    "circle-check", 
                    "info", 
                    "Média mensal"
                ),
                ui.stat_card(
                    "Manutenções", 
                    f"{State.pending_maintenances}", 
                    "wrench", 
                    "warning", 
                    "Pendentes"
                ),
                ui.stat_card(
                    "Pacientes", 
                    f"{State.compulab_count + State.simus_count}", 
                    "users", 
                    "brand", 
                    "Processados"
                ),
                columns="4",
                spacing="6",
                width="100%",
                class_name="mb-10 animate-fade-in-up"
            ),
            
            rx.divider(class_name="mb-10"),
            
            # Quick Access Section
            ui.heading("Acesso Rápido", level=2, class_name="mb-6"),
            rx.grid(
                quick_access_card(
                    "Conversor PDF",
                    "Extração e padronização de relatórios do Compulab e Simus.",
                    "file-text",
                    "conversor",
                    "blue"
                ),
                quick_access_card(
                    "Análise Cruzada",
                    "Identificação de divergências financeiras e exames faltantes.",
                    "bar-chart-2",
                    "analise",
                    "green"
                ),
                quick_access_card(
                    "Gestão da Qualidade",
                    "Controle ProIn, gráficos Levey-Jennings e gestão de reagentes.",
                    "microscope",
                    "proin",
                    "purple"
                ),
                columns="3",
                spacing="6",
                width="100%",
                class_name="mb-12 animate-fade-in-up delay-100"
            ),

            width="100%",
            padding_bottom="4rem"
        ),
        width="100%"
    )
