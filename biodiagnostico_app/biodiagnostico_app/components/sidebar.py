"""
Sidebar navigation component for Biodiagnóstico App
Design baseado na identidade visual oficial
"""
import reflex as rx
from ..state import State


def nav_item(label: str, icon: str, page: str) -> rx.Component:
    """Item de navegação do sidebar"""
    return rx.box(
        rx.hstack(
            rx.text(icon, class_name="text-lg"),
            rx.text(label, class_name="text-sm font-medium"),
            spacing="3",
            align="center",
            width="100%",
        ),
        on_click=lambda: State.set_page(page),
        class_name=rx.cond(
            State.current_page == page,
            "w-full px-4 py-3 rounded-lg bg-[#4CAF50] text-white cursor-pointer transition-all",
            "w-full px-4 py-3 rounded-lg text-white/90 hover:bg-white/10 cursor-pointer transition-all"
        ),
    )


def sidebar() -> rx.Component:
    """Sidebar de navegação principal - Design oficial Biodiagnóstico"""
    return rx.box(
        rx.vstack(
            # Logo área
            rx.box(
                rx.hstack(
                    # Ícone Erlenmeyer
                    rx.box(
                        rx.html("""
                            <svg viewBox="0 0 60 70" width="45" height="52">
                                <path d="M20 5 L40 5 L40 25 L55 60 Q57 65 52 68 L8 68 Q3 65 5 60 L20 25 Z" 
                                      fill="#4CAF50" stroke="#8BC34A" stroke-width="2"/>
                                <rect x="18" y="2" width="24" height="6" rx="2" fill="#4CAF50" stroke="#8BC34A" stroke-width="1"/>
                                <circle cx="25" cy="45" r="3" fill="#FFD54F"/>
                                <circle cx="35" cy="50" r="2.5" fill="#FFD54F"/>
                                <circle cx="30" cy="55" r="2" fill="#FFD54F"/>
                                <circle cx="22" cy="52" r="1.5" fill="#FFD54F"/>
                            </svg>
                        """),
                    ),
                    rx.vstack(
                        rx.text(
                            "LABORATÓRIO",
                            class_name="text-white/90 text-[10px] font-medium tracking-[0.2em] leading-none"
                        ),
                        rx.text(
                            "BIODIAGNÓSTICO",
                            class_name="text-white text-lg font-bold tracking-wide leading-tight"
                        ),
                        spacing="0",
                        align="start",
                    ),
                    spacing="3",
                    align="center",
                ),
                class_name="px-4 py-6"
            ),
            
            # Separador
            rx.divider(class_name="border-white/20 mx-4"),
            
            # Menu Principal
            rx.vstack(
                rx.text(
                    "MENU PRINCIPAL",
                    class_name="text-white/50 text-[10px] font-semibold tracking-[0.15em] px-4 pt-4 pb-2"
                ),
                rx.box(
                    nav_item("Conversor PDF → CSV", "⇄", "conversor"),
                    nav_item("Análise COMPULAB × SIMUS", "📊", "analise"),
                    class_name="px-2 space-y-1"
                ),
                spacing="0",
                width="100%",
            ),
            
            # Separador
            rx.divider(class_name="border-white/20 mx-4 my-4"),
            
            # Ferramentas (ProIn QC)
            rx.vstack(
                rx.text(
                    "CONTROLE QUALIDADE",
                    class_name="text-white/50 text-[10px] font-semibold tracking-[0.15em] px-4 pb-2"
                ),
                rx.box(
                    nav_item("ProIn QC", "🔬", "proin"),
                    class_name="px-2"
                ),
                spacing="0",
                width="100%",
            ),
            
            # Separador
            rx.divider(class_name="border-white/20 mx-4 my-4"),
            
            # Configurações
            rx.vstack(
                rx.text(
                    "CONFIGURAÇÕES",
                    class_name="text-white/50 text-[10px] font-semibold tracking-[0.15em] px-4 pb-2"
                ),
                rx.box(
                    nav_item("API Gemini", "🤖", "api"),
                    class_name="px-2"
                ),
                spacing="0",
                width="100%",
            ),
            
            # Spacer
            rx.spacer(),
            
            # Botão de Logout
            rx.box(
                rx.box(
                    rx.hstack(
                        rx.text("🚪", class_name="text-lg"),
                        rx.text("Sair", class_name="text-sm font-medium"),
                        spacing="3",
                        align="center",
                        width="100%",
                    ),
                    on_click=lambda: State.logout(),
                    class_name="w-full px-4 py-3 rounded-lg text-white bg-red-600/60 hover:bg-red-600 cursor-pointer transition-all"
                ),
                class_name="px-2 pb-4"
            ),
            
            # Footer
            rx.box(
                rx.vstack(
                    rx.text(
                        "v1.1.0",
                        class_name="text-white/50 text-xs"
                    ),
                    rx.text(
                        "© 2025 Biodiagnóstico",
                        class_name="text-white/50 text-xs"
                    ),
                    spacing="1",
                    align="center",
                ),
                class_name="py-4 border-t border-white/10"
            ),
            
            height="100%",
            width="100%",
        ),
        class_name="w-64 bg-[#1B5E20] min-h-screen fixed left-0 top-0"
    )


def mobile_nav() -> rx.Component:
    """Navegação mobile simplificada"""
    return rx.box(
        rx.hstack(
            rx.button(
                rx.hstack(
                    rx.text("⇄"),
                    rx.text("Conversor", class_name="hidden sm:inline text-sm"),
                    spacing="2",
                ),
                on_click=lambda: State.set_page("conversor"),
                class_name=rx.cond(
                    State.current_page == "conversor",
                    "bg-[#4CAF50] text-white px-4 py-2 rounded-lg",
                    "bg-white/10 text-white/80 px-4 py-2 rounded-lg"
                ),
                variant="ghost",
            ),
            rx.button(
                rx.hstack(
                    rx.text("📊"),
                    rx.text("Análise", class_name="hidden sm:inline text-sm"),
                    spacing="2",
                ),
                on_click=lambda: State.set_page("analise"),
                class_name=rx.cond(
                    State.current_page == "analise",
                    "bg-[#4CAF50] text-white px-4 py-2 rounded-lg",
                    "bg-white/10 text-white/80 px-4 py-2 rounded-lg"
                ),
                variant="ghost",
            ),
            rx.button(
                rx.hstack(
                    rx.text("🔬"),
                    rx.text("CQ", class_name="hidden sm:inline text-sm"),
                    spacing="2",
                ),
                on_click=lambda: State.set_page("proin"),
                class_name=rx.cond(
                    State.current_page == "proin",
                    "bg-[#4CAF50] text-white px-4 py-2 rounded-lg",
                    "bg-white/10 text-white/80 px-4 py-2 rounded-lg"
                ),
                variant="ghost",
            ),
            rx.box(
                rx.hstack(
                    rx.text("🚪"),
                    rx.text("Sair", class_name="hidden sm:inline text-sm"),
                    spacing="2",
                ),
                on_click=lambda: State.logout(),
                class_name="bg-red-600/60 hover:bg-red-600 text-white px-4 py-2 rounded-lg cursor-pointer transition-all",
            ),
            spacing="2",
            justify="center",
            width="100%",
        ),
        class_name="md:hidden bg-[#1B5E20] p-3 rounded-xl mb-4"
    )
