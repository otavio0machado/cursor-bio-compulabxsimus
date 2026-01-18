"""
File upload components for Biodiagnóstico App
Enhanced with drag-and-drop animations, validation, and better UX - Premium Style
"""
import reflex as rx
from ..state import State


def file_type_badge(file_type: str) -> rx.Component:
    """Badge que mostra o tipo de arquivo aceito"""
    colors = {
        "PDF": ("bg-red-50", "text-red-600", "border-red-100"),
        "CSV": ("bg-blue-50", "text-blue-600", "border-blue-100"),
        "PDF/CSV": ("bg-purple-50", "text-purple-600", "border-purple-100"),
    }
    bg, text, border = colors.get(file_type, ("bg-gray-50", "text-gray-600", "border-gray-100"))
    
    return rx.box(
        rx.text(file_type, class_name=f"{text} text-[10px] font-bold tracking-wider"),
        class_name=f"{bg} {border} border px-2 py-1 rounded-md"
    )


def file_upload_enhanced(
    title: str,
    subtitle: str,
    icon_svg: str,
    upload_id: str,
    file_name,
    file_size,
    on_upload,
    on_remove,
    accepted_types: str = "PDF",
    accept_dict: dict = None,
    max_size_mb: int = 50,
) -> rx.Component:
    """
    Componente de upload aprimorado com design Premium SaaS
    """
    if accept_dict is None:
        accept_dict = {"application/pdf": [".pdf"]}
    
    # Ícone de arquivo carregado
    file_loaded_icon = """
        <svg viewBox="0 0 60 60" width="48" height="48" class="animate-bounce-once">
            <circle cx="30" cy="30" r="28" fill="#E8F5E9" stroke="#4CAF50" stroke-width="2"/>
            <path d="M20 30 L27 37 L40 24" stroke="#4CAF50" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
    """
    
    return rx.box(
        rx.upload(
            rx.vstack(
                rx.cond(
                    file_name != "",
                    # ===== Estado: Arquivo Carregado =====
                    rx.vstack(
                        rx.html(file_loaded_icon),
                        rx.text(
                            title,
                            class_name="text-[#1B5E20] font-bold text-lg mt-2"
                        ),
                        rx.box(
                            rx.hstack(
                                rx.icon("file-text", size=16, class_name="text-green-600"),
                                rx.text(
                                    file_name,
                                    class_name="text-green-800 text-sm font-medium truncate max-w-[180px]"
                                ),
                                spacing="2",
                                align="center",
                            ),
                            class_name="bg-green-50 border border-green-200 px-4 py-2 rounded-xl"
                        ),
                        rx.cond(
                            file_size != "",
                            rx.text(
                                file_size,
                                class_name="text-gray-400 text-xs font-medium"
                            ),
                        ),
                        rx.button(
                            rx.hstack(
                                rx.icon("trash-2", size=14),
                                rx.text("Remover arquivo", class_name="text-xs font-medium"),
                                spacing="2",
                                align="center",
                            ),
                            on_click=on_remove,
                            class_name="bg-white border border-red-100 text-red-500 px-4 py-2 rounded-lg hover:bg-red-50 hover:text-red-600 hover:border-red-200 transition-all mt-2 shadow-sm",
                            type="button",
                        ),
                        spacing="2",
                        align="center",
                    ),
                    # ===== Estado: Aguardando Upload =====
                    rx.vstack(
                        rx.box(
                            rx.html(icon_svg),
                            class_name="p-4 bg-gray-50 rounded-full mb-2 group-hover:scale-110 transition-transform duration-300"
                        ),
                        rx.text(
                            title,
                            class_name="text-[#1B5E20] font-bold text-lg"
                        ),
                        rx.text(
                            subtitle,
                            class_name="text-gray-500 text-sm text-center px-4"
                        ),
                        rx.box(
                            rx.hstack(
                                file_type_badge(accepted_types),
                                rx.text(
                                    f"Máx. {max_size_mb}MB",
                                    class_name="text-gray-400 text-xs"
                                ),
                                spacing="3",
                                align="center",
                            ),
                            class_name="mt-2"
                        ),
                        spacing="1",
                        align="center",
                    ),
                ),
                justify="center",
                align="center",
                class_name="w-full h-full min-h-[240px] py-8 group"
            ),
            id=upload_id,
            accept=accept_dict,
            max_files=1,
            on_drop=on_upload(rx.upload_files(upload_id=upload_id)),
            class_name="w-full h-full cursor-pointer outline-none"
        ),
        class_name=rx.cond(
            file_name != "",
            "border-2 border-solid border-[#4CAF50] rounded-3xl bg-white shadow-lg shadow-green-900/5 transition-all duration-300",
            "border-2 border-dashed border-gray-300 rounded-3xl bg-white hover:border-[#4CAF50] hover:bg-green-50/10 hover:shadow-xl hover:shadow-green-900/5 transition-all duration-300"
        ),
    )


def compact_upload_card(
    title: str,
    icon_svg: str,
    upload_id: str,
    file_name,
    file_size,
    on_upload,
    on_remove,
    accepted_types: str = "PDF/CSV",
    accept_dict: dict = None,
) -> rx.Component:
    """Card de upload compacto para análise - Design Premium"""
    if accept_dict is None:
        accept_dict = {"application/pdf": [".pdf"], "text/csv": [".csv"]}
    
    return rx.box(
        rx.upload(
            rx.vstack(
                rx.cond(
                    file_name != "",
                    # Arquivo carregado
                    rx.vstack(
                        rx.box(
                            rx.hstack(
                                rx.icon("check-circle-2", size=24, class_name="text-[#4CAF50]"),
                                rx.vstack(
                                    rx.text(title, class_name="text-[#1B5E20] font-bold text-sm"),
                                    rx.text(
                                        file_name,
                                        class_name="text-gray-600 text-xs truncate max-w-[140px]"
                                    ),
                                    rx.cond(
                                        file_size != "",
                                        rx.text(file_size, class_name="text-gray-400 text-[10px]"),
                                    ),
                                    spacing="0",
                                    align="start",
                                ),
                                spacing="3",
                                align="center",
                            ),
                        ),
                        rx.button(
                            rx.text("Remover", class_name="text-xs"),
                            on_click=on_remove,
                            class_name="bg-transparent text-red-400 hover:text-red-600 px-2 py-1 transition-all",
                            type="button",
                        ),
                        spacing="1",
                        align="center",
                    ),
                    # Aguardando upload
                    rx.vstack(
                        rx.html(icon_svg),
                        rx.text(title, class_name="text-[#1B5E20] font-bold text-sm mt-1"),
                        rx.hstack(
                            file_type_badge(accepted_types),
                            spacing="1",
                        ),
                        spacing="1",
                        align="center",
                    ),
                ),
                justify="center",
                align="center",
                class_name="w-full h-full min-h-[140px] py-4"
            ),
            id=upload_id,
            accept=accept_dict,
            max_files=1,
            on_drop=on_upload(rx.upload_files(upload_id=upload_id)),
            class_name="w-full h-full cursor-pointer outline-none"
        ),
        class_name=rx.cond(
            file_name != "",
            "border border-solid border-[#4CAF50] rounded-2xl bg-green-50/20 transition-all duration-300",
            "border border-dashed border-gray-300 rounded-2xl bg-gray-50/50 hover:bg-white hover:border-[#4CAF50] hover:shadow-md transition-all duration-200"
        ),
    )


def upload_progress_indicator(is_loading: bool, message: str = "Processando...") -> rx.Component:
    """Indicador de progresso durante o upload"""
    return rx.cond(
        is_loading,
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.spinner(size="2", color="green"),
                    rx.text(message, class_name="text-[#1B5E20] text-sm font-semibold animate-pulse"),
                    spacing="3",
                    align="center",
                ),
                rx.cond(
                    State.processing_status != "",
                    rx.box(
                        rx.text(
                            State.processing_status,
                            class_name="text-amber-700 text-xs font-medium"
                        ),
                        class_name="bg-amber-50 border border-amber-100 rounded-lg px-3 py-1.5 mt-2"
                    ),
                ),
                spacing="1",
                align="center",
            ),
            class_name="bg-white border border-green-100 rounded-2xl p-4 shadow-sm w-full max-w-md mx-auto"
        ),
    )


def large_file_progress_indicator() -> rx.Component:
    """Indicador de progresso para arquivos grandes"""
    return rx.cond(
        State.is_large_file_processing,
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.spinner(size="3", color="green"),
                    rx.vstack(
                        rx.text(
                            State.processing_progress_text,
                            class_name="text-[#1B5E20] font-bold"
                        ),
                        rx.text(
                            "Isso pode levar alguns minutos...",
                            class_name="text-gray-500 text-xs"
                        ),
                        spacing="0",
                    ),
                    spacing="4",
                    align="center",
                ),
                rx.progress(value=None, class_name="w-full h-1 mt-3"), # Indeterminate progress
                rx.box(
                    rx.hstack(
                        rx.icon("info", size=14, class_name="text-amber-600"),
                        rx.text(
                            "Por favor, não feche esta página enquanto processamos seus dados.",
                            class_name="text-amber-700 text-xs font-medium"
                        ),
                        spacing="2",
                        align="center",
                    ),
                    class_name="bg-amber-50 border border-amber-100 rounded-lg px-3 py-2 mt-2 w-full"
                ),
                spacing="2",
                align="center",
            ),
            class_name="bg-white border border-green-200 rounded-2xl p-6 shadow-lg w-full max-w-md mx-auto mt-4"
        ),
    )
