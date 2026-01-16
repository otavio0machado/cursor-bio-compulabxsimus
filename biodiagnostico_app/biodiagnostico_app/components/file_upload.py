"""
File upload components for Biodiagnóstico App
Enhanced with drag-and-drop animations, validation, and better UX
"""
import reflex as rx
from ..state import State


def file_type_badge(file_type: str) -> rx.Component:
    """Badge que mostra o tipo de arquivo aceito"""
    colors = {
        "PDF": ("bg-red-100", "text-red-700", "border-red-200"),
        "CSV": ("bg-blue-100", "text-blue-700", "border-blue-200"),
        "PDF/CSV": ("bg-purple-100", "text-purple-700", "border-purple-200"),
    }
    bg, text, border = colors.get(file_type, ("bg-gray-100", "text-gray-700", "border-gray-200"))
    
    return rx.box(
        rx.text(file_type, class_name=f"{text} text-xs font-semibold"),
        class_name=f"{bg} {border} border px-2 py-0.5 rounded-full"
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
    Componente de upload aprimorado com:
    - Animações de drag-and-drop
    - Validação visual
    - Botão de remover arquivo
    - Indicador de tamanho
    - Feedback visual melhorado
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
                            class_name="text-[#1B5E20] font-bold text-lg"
                        ),
                        rx.box(
                            rx.hstack(
                                rx.text("📄", class_name="text-sm"),
                                rx.text(
                                    file_name,
                                    class_name="text-green-700 text-sm font-medium truncate max-w-[180px]"
                                ),
                                spacing="1",
                                align="center",
                            ),
                            class_name="bg-green-50 border border-green-200 px-3 py-1.5 rounded-lg"
                        ),
                        rx.cond(
                            file_size != "",
                            rx.text(
                                file_size,
                                class_name="text-gray-500 text-xs"
                            ),
                        ),
                        rx.button(
                            rx.hstack(
                                rx.text("✕", class_name="text-xs"),
                                rx.text("Remover", class_name="text-xs"),
                                spacing="1",
                                align="center",
                            ),
                            on_click=on_remove,
                            class_name="bg-transparent border border-red-300 text-red-600 px-3 py-1 rounded-lg hover:bg-red-50 transition-all text-xs mt-2",
                            type="button",
                        ),
                        spacing="2",
                        align="center",
                    ),
                    # ===== Estado: Aguardando Upload =====
                    rx.vstack(
                        rx.html(icon_svg),
                        rx.text(
                            title,
                            class_name="text-[#1B5E20] font-bold text-lg mt-2"
                        ),
                        rx.text(
                            subtitle,
                            class_name="text-gray-500 text-sm"
                        ),
                        rx.hstack(
                            file_type_badge(accepted_types),
                            rx.text(
                                f"Máx. {max_size_mb}MB",
                                class_name="text-gray-400 text-xs"
                            ),
                            spacing="2",
                            align="center",
                        ),
                        spacing="2",
                        align="center",
                    ),
                ),
                justify="center",
                align="center",
                class_name="w-full h-full min-h-[200px] py-6"
            ),
            id=upload_id,
            accept=accept_dict,
            max_files=1,
            on_drop=on_upload(rx.upload_files(upload_id=upload_id)),
            class_name="w-full h-full cursor-pointer"
        ),
        class_name=rx.cond(
            file_name != "",
            "border-2 border-solid border-[#4CAF50] rounded-2xl bg-green-50/30 transition-all duration-300",
            "border-2 border-dashed border-[#4CAF50] rounded-2xl hover:border-[#1B5E20] hover:bg-green-50/50 hover:shadow-lg hover:scale-[1.02] transition-all duration-300 active:scale-[0.98]"
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
    """Card de upload compacto para análise"""
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
                                rx.text("✅", class_name="text-xl"),
                                rx.vstack(
                                    rx.text(title, class_name="text-[#1B5E20] font-bold text-sm"),
                                    rx.text(
                                        file_name,
                                        class_name="text-green-600 text-xs truncate max-w-[140px]"
                                    ),
                                    rx.cond(
                                        file_size != "",
                                        rx.text(file_size, class_name="text-gray-400 text-xs"),
                                    ),
                                    spacing="0",
                                    align="start",
                                ),
                                spacing="2",
                                align="center",
                            ),
                        ),
                        rx.button(
                            rx.text("✕ Remover", class_name="text-xs"),
                            on_click=on_remove,
                            class_name="bg-transparent text-red-500 hover:text-red-700 px-2 py-1 transition-all",
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
                class_name="w-full h-full min-h-[130px] py-3"
            ),
            id=upload_id,
            accept=accept_dict,
            max_files=1,
            on_drop=on_upload(rx.upload_files(upload_id=upload_id)),
            class_name="w-full h-full cursor-pointer"
        ),
        class_name=rx.cond(
            file_name != "",
            "border-2 border-solid border-[#4CAF50] rounded-xl bg-green-50/30 transition-all duration-300",
            "border-2 border-dashed border-[#4CAF50] rounded-xl hover:border-[#1B5E20] hover:bg-green-50/30 transition-all duration-200"
        ),
    )


def upload_progress_indicator(is_loading: bool, message: str = "Processando...") -> rx.Component:
    """Indicador de progresso durante o upload - Melhorado para arquivos grandes"""
    return rx.cond(
        is_loading,
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.spinner(size="1", color="green"),
                    rx.text(message, class_name="text-[#1B5E20] text-sm font-medium animate-pulse"),
                    spacing="2",
                    align="center",
                ),
                rx.cond(
                    State.processing_status != "",
                    rx.box(
                        rx.text(
                            State.processing_status,
                            class_name="text-amber-700 text-xs mt-2 font-medium"
                        ),
                        class_name="bg-amber-50 border border-amber-200 rounded-lg px-3 py-1.5 mt-2"
                    ),
                ),
                spacing="1",
                align="center",
            ),
            class_name="bg-green-50 border border-green-200 rounded-xl px-4 py-2"
        ),
    )


def large_file_progress_indicator() -> rx.Component:
    """Indicador de progresso para arquivos grandes"""
    return rx.cond(
        State.is_large_file_processing,
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.spinner(size="2", color="green"),
                    rx.text(
                        State.processing_progress_text,
                        class_name="text-[#1B5E20] font-semibold"
                    ),
                    spacing="3",
                    align="center",
                ),
                rx.box(
                    rx.text(
                        "💡 Arquivos grandes podem levar alguns minutos. Por favor, não feche a página.",
                        class_name="text-amber-600 text-sm"
                    ),
                    class_name="bg-amber-50 border border-amber-200 rounded-lg px-3 py-2 mt-2"
                ),
                spacing="2",
                align="center",
            ),
            class_name="bg-green-50 border-2 border-green-300 rounded-xl p-4 animate-pulse"
        ),
    )


def file_upload_section() -> rx.Component:
    """Seção completa de upload de arquivos - Design atualizado"""
    
    # SVG do Erlenmeyer (COMPULAB)
    erlenmeyer_svg = """
        <svg viewBox="0 0 80 100" width="60" height="75">
            <path d="M28 10 L52 10 L52 35 L70 85 Q72 92 65 95 L15 95 Q8 92 10 85 L28 35 Z" 
                  fill="none" stroke="#1B5E20" stroke-width="2.5"/>
            <rect x="26" y="5" width="28" height="8" rx="3" fill="none" stroke="#1B5E20" stroke-width="2.5"/>
            <circle cx="40" cy="72" r="10" fill="#4CAF50" opacity="0.2"/>
            <circle cx="52" cy="58" r="6" fill="#4CAF50" opacity="0.4"/>
        </svg>
    """
    
    # SVG dos Tubos de ensaio (SIMUS)
    tubes_svg = """
        <svg viewBox="0 0 100 100" width="60" height="75">
            <rect x="20" y="15" width="14" height="65" rx="7" fill="none" stroke="#1B5E20" stroke-width="2.5"/>
            <rect x="20" y="50" width="14" height="30" rx="7" fill="#4CAF50" opacity="0.2"/>
            <rect x="43" y="15" width="14" height="65" rx="7" fill="none" stroke="#1B5E20" stroke-width="2.5"/>
            <rect x="43" y="40" width="14" height="40" rx="7" fill="#4CAF50" opacity="0.3"/>
            <rect x="66" y="15" width="14" height="65" rx="7" fill="none" stroke="#1B5E20" stroke-width="2.5"/>
            <rect x="66" y="55" width="14" height="25" rx="7" fill="#4CAF50" opacity="0.2"/>
        </svg>
    """
    
    return rx.box(
        rx.vstack(
            # Cabeçalho
            rx.hstack(
                rx.text("📁", class_name="text-2xl"),
                rx.text(
                    "Upload de Arquivos",
                    class_name="text-[#1B5E20] font-bold text-xl"
                ),
                spacing="3",
                align="center",
            ),
            rx.text(
                "Arraste ou clique para carregar os arquivos PDF ou CSV",
                class_name="text-gray-600 text-sm"
            ),
            
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
                    accepted_types="PDF/CSV",
                    accept_dict={"application/pdf": [".pdf"], "text/csv": [".csv"]},
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
                    accepted_types="PDF/CSV",
                    accept_dict={"application/pdf": [".pdf"], "text/csv": [".csv"]},
                ),
                columns="2",
                spacing="6",
                width="100%",
            ),
            
            # Indicador de progresso para upload
            upload_progress_indicator(State.is_uploading, "Carregando arquivo..."),
            
            # Indicador de progresso para processamento de arquivos grandes
            large_file_progress_indicator(),
            
            # Mensagens de status
            rx.cond(
                State.success_message != "",
                rx.box(
                    rx.hstack(
                        rx.text("✅"),
                        rx.text(State.success_message, class_name="text-green-700"),
                        spacing="2",
                    ),
                    class_name="bg-green-50 border border-green-200 rounded-xl p-3 w-full animate-fade-in"
                ),
            ),
            rx.cond(
                State.error_message != "",
                rx.box(
                    rx.hstack(
                        rx.text("❌"),
                        rx.text(State.error_message, class_name="text-red-700"),
                        spacing="2",
                    ),
                    class_name="bg-red-50 border border-red-200 rounded-xl p-3 w-full animate-shake"
                ),
            ),
            
            # Dica
            rx.box(
                rx.hstack(
                    rx.text("💡", class_name="text-sm"),
                    rx.text(
                        "Dica: Você pode arrastar os arquivos diretamente do seu computador para as áreas de upload",
                        class_name="text-gray-500 text-xs"
                    ),
                    spacing="2",
                    align="center",
                ),
                class_name="bg-gray-50 border border-gray-200 rounded-lg px-3 py-2 mt-2"
            ),
            
            spacing="4",
            width="100%",
        ),
        class_name="bg-gradient-to-br from-lime-50/50 to-green-50/50 p-6 rounded-2xl border border-green-100"
    )
