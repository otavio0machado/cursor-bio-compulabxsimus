"""
File upload components for Biodiagnóstico App
Enhanced with drag-and-drop animations, validation, and better UX
(PURIFICADA)
"""
import reflex as rx
from ..state import State
from ..styles import Color, Design, Typography, Spacing
from . import ui

def file_type_badge(file_type: str) -> rx.Component:
    """Badge que mostra o tipo de arquivo aceito (Purificada)"""
    colors = {
        "PDF": Color.ERROR,
        "CSV": Color.PRIMARY,
        "EXCEL": Color.SUCCESS,
        "PDF/CSV": Color.PRIMARY, # Optimized to use PRIMARY green
        "COMPLETO": Color.DEEP,
    }
    fg = colors.get(file_type, Color.TEXT_SECONDARY)
    return rx.badge(
        file_type,
        color_scheme="gray", # Default base
        style={
            "color": fg,
            "background_color": f"{fg}15",
            "border": f"1px solid {fg}30",
            "font_size": "0.75rem",
            "font_weight": "700",
            "padding_x": "8px",
            "border_radius": "9999px"
        }
    )


def file_upload_enhanced(
    title: str,
    subtitle: str,
    icon_svg: str,
    upload_id: str,
    file_name: str,
    file_size: str,
    on_upload,
    on_remove,
    accepted_types: str = "PDF",
    accept_dict: dict = None,
    max_size_mb: int = 50,
) -> rx.Component:
    """Componente de upload aprimorado (Purificada)"""
    if accept_dict is None:
        accept_dict = {
            "application/pdf": [".pdf"],
            "text/csv": [".csv"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"],
            "application/vnd.ms-excel": [".xls", ".xsl"]
        }

    # Ícone de arquivo carregado (Purificado)
    file_loaded_icon = f"""
        <svg viewBox="0 0 60 60" width="48" height="48">
            <circle cx="30" cy="30" r="28" fill="{Color.SUCCESS_BG}" stroke="{Color.SUCCESS}" stroke-width="2"/>
            <path d="M20 30 L27 37 L40 24" stroke="{Color.SUCCESS}" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
    """
    
    is_loaded = file_name != ""

    return rx.box(
        rx.upload(
            rx.vstack(
                rx.cond(
                    is_loaded,
                    # ===== Estado: Arquivo Carregado =====
                    rx.vstack(
                        rx.html(file_loaded_icon),
                        ui.heading(title, level=3, color=Color.DEEP),
                        rx.box(
                            rx.hstack(
                                rx.text("📄", font_size="0.875rem"),
                                ui.text(file_name, size="small", color=Color.SUCCESS, font_weight="500", style={"max_width": "180px", "overflow": "hidden", "text_overflow": "ellipsis", "white_space": "nowrap"}),
                                spacing="2", align_items="center",
                            ),
                            bg=Color.SUCCESS_BG, border=f"1px solid {Color.SUCCESS}30", px="3", py="1.5", border_radius=Design.RADIUS_MD
                        ),
                        rx.cond(file_size != "", ui.text(file_size, size="caption", color=Color.TEXT_SECONDARY)),
                        ui.button("Remover", icon="x", on_click=on_remove, variant="ghost", color_scheme="red", margin_top=Spacing.SM),
                        spacing="2", align_items="center",
                    ),
                    # ===== Estado: Aguardando Upload =====
                    rx.vstack(
                        rx.html(icon_svg),
                        ui.heading(title, level=3, color=Color.DEEP, margin_top=Spacing.SM),
                        ui.text(subtitle, size="small", color=Color.TEXT_SECONDARY),
                        rx.hstack(
                            file_type_badge(accepted_types),
                            ui.text(f"Máx. {max_size_mb}MB", size="caption", color=Color.TEXT_SECONDARY),
                            spacing="2", align_items="center",
                        ),
                        spacing="2", align_items="center",
                    ),
                ),
                justify_content="center", align_items="center", width="100%", height="100%", min_height="200px", padding_y=Spacing.LG
            ),
            id=upload_id,
            accept=accept_dict,
            max_files=1,
            on_drop=on_upload(rx.upload_files(upload_id=upload_id)),
            width="100%", height="100%", cursor="pointer"
        ),
        bg=rx.cond(is_loaded, f"{Color.SUCCESS}05", f"{Color.PRIMARY}05"),
        border=rx.cond(is_loaded, f"2px solid {Color.SUCCESS}", f"2px dashed {Color.PRIMARY}"),
        border_radius=Design.RADIUS_XL,
        transition="all 0.3s ease",
        _hover={
            "border_color": Color.DEEP,
            "bg": Color.PRIMARY_LIGHT,
            "box_shadow": Design.SHADOW_MD,
            "transform": "translateY(-2px)"
        },
        width="100%"
    )


def compact_upload_card(
    title: str,
    icon_svg: str,
    upload_id: str,
    file_name: str,
    file_size: str,
    on_upload,
    on_remove,
    accepted_types: str = "PDF/CSV",
    accept_dict: dict = None,
) -> rx.Component:
    """Card de upload compacto (Purificada)"""
    if accept_dict is None:
        accept_dict = {
            "application/pdf": [".pdf"], 
            "text/csv": [".csv"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"],
            "application/vnd.ms-excel": [".xls", ".xsl"]
        }

    is_loaded = file_name != ""
    
    return rx.box(
        rx.upload(
            rx.vstack(
                rx.cond(
                    is_loaded,
                    # Arquivo carregado
                    rx.vstack(
                        rx.hstack(
                            rx.box(rx.icon(tag="circle_check", size=24, color=Color.SUCCESS), bg=Color.SUCCESS_BG, p="1", border_radius="full"),
                            rx.vstack(
                                ui.text(title, size="label", color=Color.DEEP, font_weight="700"),
                                ui.text(file_name, size="caption", color=Color.SUCCESS, style={"max_width": "140px", "overflow": "hidden", "text_overflow": "ellipsis", "white_space": "nowrap"}),
                                rx.cond(file_size != "", ui.text(file_size, size="caption", color=Color.TEXT_SECONDARY)),
                                spacing="0", align_items="start",
                            ),
                            spacing="2", align_items="center",
                        ),
                        ui.button("Remover", icon="x", on_click=on_remove, variant="ghost", color_scheme="red", size="1"),
                        spacing="1", align_items="center",
                    ),
                    # Aguardando upload
                    rx.vstack(
                        rx.html(icon_svg),
                        ui.text(title, size="label", color=Color.DEEP, font_weight="700", margin_top=Spacing.XS),
                        file_type_badge(accepted_types),
                        spacing="1", align_items="center",
                    ),
                ),
                justify_content="center", align_items="center", width="100%", height="100%", min_height="130px", padding_y=Spacing.MD
            ),
            id=upload_id,
            accept=accept_dict,
            max_files=1,
            on_drop=on_upload(rx.upload_files(upload_id=upload_id)),
            width="100%", height="100%", cursor="pointer"
        ),
        bg=rx.cond(is_loaded, f"{Color.SUCCESS}05", Color.SURFACE),
        border=rx.cond(is_loaded, f"2px solid {Color.SUCCESS}", f"2px dashed {Color.BORDER}"),
        border_radius=Design.RADIUS_LG,
        transition="all 0.2s ease",
        _hover={"border_color": Color.PRIMARY, "bg": Color.PRIMARY_LIGHT},
        width="100%"
    )


def upload_progress_indicator(is_loading: bool, message: str = "Processando...") -> rx.Component:
    """Indicador de progresso purificado"""
    return rx.cond(
        is_loading,
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.spinner(size="1", color=Color.PRIMARY),
                    ui.text(message, size="small", color=Color.DEEP, font_weight="500", class_name="animate-pulse"),
                    spacing="2", align_items="center",
                ),
                rx.cond(
                    State.processing_status != "",
                    rx.box(
                        ui.text(State.processing_status, size="caption", color=Color.WARNING, font_weight="500"),
                        bg=Color.WARNING_BG, border=f"1px solid {Color.WARNING}30", border_radius=Design.RADIUS_MD, px="3", py="1.5", margin_top=Spacing.SM
                    ),
                ),
                spacing="1", align_items="center",
            ),
            bg=Color.PRIMARY_LIGHT, border=f"1px solid {Color.PRIMARY}30", border_radius=Design.RADIUS_XL, px="4", py="2"
        ),
    )


def large_file_progress_indicator() -> rx.Component:
    """Indicador de progresso para arquivos grandes purificado"""
    return rx.cond(
        State.is_large_file_processing,
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.spinner(size="2", color=Color.SUCCESS),
                    ui.heading(State.processing_progress_text, level=4, color=Color.DEEP),
                    spacing="3", align_items="center",
                ),
                rx.box(
                    ui.text("💡 Arquivos grandes podem levar alguns minutos. Por favor, não feche a página.", size="small", color=Color.WARNING),
                    bg=Color.WARNING_BG, border=f"1px solid {Color.WARNING}30", border_radius=Design.RADIUS_MD, px="3", py="2", margin_top=Spacing.SM
                ),
                spacing="2", align_items="center",
            ),
            bg=Color.SUCCESS_BG, border=f"2px solid {Color.SUCCESS}30", border_radius=Design.RADIUS_XL, p="4", class_name="animate-pulse"
        ),
    )


def file_upload_section() -> rx.Component:
    """Seção completa de upload de arquivos purificada"""
    
    # SVG do Erlenmeyer (COMPULAB)
    erlenmeyer_svg = f"""
        <svg viewBox="0 0 80 100" width="60" height="75">
            <path d="M28 10 L52 10 L52 35 L70 85 Q72 92 65 95 L15 95 Q8 92 10 85 L28 35 Z" 
                  fill="none" stroke="{Color.DEEP}" stroke-width="2.5"/>
            <rect x="26" y="5" width="28" height="8" rx="3" fill="none" stroke="{Color.DEEP}" stroke-width="2.5"/>
            <circle cx="40" cy="72" r="10" fill="{Color.SUCCESS}" opacity="0.2"/>
            <circle cx="52" cy="58" r="6" fill="{Color.SUCCESS}" opacity="0.4"/>
        </svg>
    """
    
    # SVG dos Tubos de ensaio (SIMUS)
    tubes_svg = f"""
        <svg viewBox="0 0 100 100" width="60" height="75">
            <rect x="20" y="15" width="14" height="65" rx="7" fill="none" stroke="{Color.DEEP}" stroke-width="2.5"/>
            <rect x="20" y="50" width="14" height="30" rx="7" fill="{Color.SUCCESS}" opacity="0.2"/>
            <rect x="43" y="15" width="14" height="65" rx="7" fill="none" stroke="{Color.DEEP}" stroke-width="2.5"/>
            <rect x="43" y="40" width="14" height="40" rx="7" fill="{Color.SUCCESS}" opacity="0.3"/>
            <rect x="66" y="15" width="14" height="65" rx="7" fill="none" stroke="{Color.DEEP}" stroke-width="2.5"/>
            <rect x="66" y="55" width="14" height="25" rx="7" fill="{Color.SUCCESS}" opacity="0.2"/>
        </svg>
    """
    
    return rx.box(
        rx.vstack(
            # Cabeçalho
            rx.hstack(
                rx.icon(tag="upload_cloud", size=24, color=Color.PRIMARY),
                ui.heading("Upload de Arquivos", level=2, color=Color.DEEP),
                spacing="3", align_items="center",
            ),
            ui.text("Arraste ou clique para carregar os arquivos PDF, CSV ou Excel/XSL", size="small", color=Color.TEXT_SECONDARY),
            
            # Grid de uploads
            rx.grid(
                file_upload_enhanced(
                    title="COMPULAB",
                    subtitle="Arraste ou clique para enviar",
                    icon_svg=erlenmeyer_svg,
                    upload_id="compulab_upload",
                    file_name=State.compulab_file_name,
                    file_size=State.compulab_file_size,
                    on_upload=State.handle_compulab_upload,
                    on_remove=State.clear_compulab_file,
                    accepted_types="COMPLETO",
                ),

                file_upload_enhanced(
                    title="SIMUS",
                    subtitle="Arraste ou clique para enviar",
                    icon_svg=tubes_svg,
                    upload_id="simus_upload",
                    file_name=State.simus_file_name,
                    file_size=State.simus_file_size,
                    on_upload=State.handle_simus_upload,
                    on_remove=State.clear_simus_file,
                    accepted_types="COMPLETO",
                ),

                columns={"initial": "1", "md": "2"},
                spacing="6", width="100%",
            ),
            
            upload_progress_indicator(State.is_uploading, "Carregando arquivo..."),
            large_file_progress_indicator(),
            
            # Mensagens de status (Purificadas)
            rx.cond(
                State.success_message != "",
                rx.callout(State.success_message, icon="circle_check", color_scheme="green", width="100%")
            ),
            rx.cond(
                State.error_message != "",
                rx.callout(State.error_message, icon="triangle_alert", color_scheme="red", width="100%", class_name="animate-shake")
            ),
            
            # Dica
            rx.box(
                rx.hstack(
                    rx.icon(tag="info", size=16, color=Color.TEXT_SECONDARY),
                    ui.text("Você pode arrastar os arquivos diretamente do seu computador.", size="caption", color=Color.TEXT_SECONDARY),
                    spacing="2", align_items="center",
                ),
                bg=Color.BACKGROUND, border=f"1px solid {Color.BORDER}", border_radius=Design.RADIUS_MD, px="3", py="2", margin_top=Spacing.SM
            ),
            
            spacing="4", width="100%",
        ),
        bg=Color.SURFACE, p="6", border_radius=Design.RADIUS_XXL if hasattr(Design, 'RADIUS_XXL') else Design.RADIUS_XL, border=f"1px solid {Color.BORDER}", box_shadow=Design.SHADOW_SM
    )
