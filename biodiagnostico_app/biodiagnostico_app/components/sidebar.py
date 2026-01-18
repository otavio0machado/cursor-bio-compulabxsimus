"""
Sidebar navigation component for Biodiagnóstico App
Design baseado na identidade visual oficial - Premium SaaS Style
"""
import reflex as rx
from ..state import State


def nav_item(label: str, icon: str, page: str) -> rx.Component:
    """Item de navegação do sidebar com estilo premium"""
    active_bg = "bg-[#4CAF50] shadow-md shadow-green-900/20"
    active_text = "text-white font-semibold"
    inactive_bg = "hover:bg-white/10"
    inactive_text = "text-green-50/80 hover:text-white font-medium"

    return rx.box(
        rx.hstack(
            rx.box(
                rx.text(icon, class_name="text-lg"),
                class_name="w-6 flex justify-center"
            ),
            rx.text(label, class_name="text-sm transition-all duration-200"),
            spacing="3",
            align="center",
            width="100%",
        ),
        on_click=lambda: State.set_page(page),
        class_name=rx.cond(
            State.current_page == page,
            f"w-full px-4 py-3.5 rounded-xl cursor-pointer transition-all duration-300 {active_bg} {active_text} transform scale-[1.02]",
            f"w-full px-4 py-3.5 rounded-xl cursor-pointer transition-all duration-200 {inactive_bg} {inactive_text}"
        ),
    )


def sidebar() -> rx.Component:
    """Sidebar de navegação principal - Design Flutuante Premium"""
    return rx.box(
        rx.vstack(
            # Logo área
            rx.box(
                rx.hstack(
                    # Ícone Erlenmeyer com animação sutil
                    rx.box(
                        rx.html("""
                            <svg viewBox="0 0 60 70" width="45" height="52">
                                <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                                    <feGaussianBlur stdDeviation="2" result="blur"/>
                                    <feComposite in="SourceGraphic" in2="blur" operator="over"/>
                                </filter>
                                <path d="M20 5 L40 5 L40 25 L55 60 Q57 65 52 68 L8 68 Q3 65 5 60 L20 25 Z" 
                                      fill="#4CAF50" stroke="#8BC34A" stroke-width="2"/>
                                <rect x="18" y="2" width="24" height="6" rx="2" fill="#4CAF50" stroke="#8BC34A" stroke-width="1"/>
                                <circle cx="25" cy="45" r="3" fill="#FFD54F"/>
                                <circle cx="35" cy="50" r="2.5" fill="#FFD54F"/>
                                <circle cx="30" cy="55" r="2" fill="#FFD54F"/>
                                <circle cx="22" cy="52" r="1.5" fill="#FFD54F"/>
                            </svg>
                        """),
                        class_name="filter drop-shadow-lg"
                    ),
                    rx.vstack(
                        rx.text(
                            "LABORATÓRIO",
                            class_name="text-green-300/90 text-[10px] font-bold tracking-[0.25em] leading-none uppercase"
                        ),
                        rx.text(
                            "BIODIAGNÓSTICO",
                            class_name="text-white text-lg font-bold tracking-wide leading-tight"
                        ),
                        spacing="1",
                        align="start",
                    ),
                    spacing="3",
                    align="center",
                ),
                class_name="px-6 py-8"
            ),
            
            # Separador sutil
            rx.divider(class_name="border-white/10 mx-6 mb-2"),
            
            # Container de rolagem para os itens
            rx.vstack(
                # Menu Principal
                rx.vstack(
                    rx.text(
                        "MENU PRINCIPAL",
                        class_name="text-green-200/50 text-[10px] font-bold tracking-[0.15em] px-6 py-4"
                    ),
                    rx.box(
                        nav_item("Conversor PDF → CSV", "⇄", "conversor"),
                        nav_item("Análise COMPULAB × SIMUS", "📊", "analise"),
                        class_name="px-3 space-y-1"
                    ),
                    spacing="0",
                    width="100%",
                ),

                # Ferramentas (ProIn QC)
                rx.vstack(
                    rx.text(
                        "CONTROLE QUALIDADE",
                        class_name="text-green-200/50 text-[10px] font-bold tracking-[0.15em] px-6 py-4"
                    ),
                    rx.box(
                        nav_item("ProIn QC", "🔬", "proin"),
                        class_name="px-3"
                    ),
                    spacing="0",
                    width="100%",
                ),

                # Configurações
                rx.vstack(
                    rx.text(
                        "CONFIGURAÇÕES",
                        class_name="text-green-200/50 text-[10px] font-bold tracking-[0.15em] px-6 py-4"
                    ),
                    rx.box(
                        nav_item("API Gemini", "🤖", "api"),
                        class_name="px-3"
                    ),
                    spacing="0",
                    width="100%",
                ),

                class_name="flex-1 w-full overflow-y-auto custom-scrollbar"
            ),
            
            # Spacer
            rx.spacer(),
            
            # Botão de Logout e Perfil
            rx.box(
                rx.vstack(
                    rx.divider(class_name="border-white/10 mb-4"),
                    rx.box(
                        rx.hstack(
                            rx.avatar(fallback="AD", size="3", class_name="bg-green-700 text-white border-2 border-[#4CAF50]"),
                            rx.vstack(
                                rx.text("Administrador", class_name="text-sm font-semibold text-white"),
                                rx.text("admin@bio.com", class_name="text-xs text-green-200/70"),
                                spacing="0",
                                align="start",
                            ),
                            rx.spacer(),
                            rx.icon("log-out", size=18, class_name="text-red-400 hover:text-red-300 cursor-pointer transition-colors", on_click=lambda: State.logout()),
                            spacing="3",
                            align="center",
                            width="100%",
                        ),
                        class_name="bg-black/20 p-3 rounded-xl backdrop-blur-sm"
                    ),
                    rx.hstack(
                        rx.text("v1.1.0", class_name="text-white/30 text-[10px]"),
                        rx.spacer(),
                        rx.text("© 2025", class_name="text-white/30 text-[10px]"),
                        width="100%",
                        class_name="mt-2"
                    ),
                    width="100%",
                ),
                class_name="px-4 pb-6 w-full"
            ),
            
            height="100%",
            width="100%",
        ),
        # Estilo "Floating" Card
        class_name="w-64 bg-[#1B5E20] fixed left-4 top-4 bottom-4 rounded-3xl shadow-2xl z-50 flex flex-col overflow-hidden border border-white/5"
    )


def mobile_nav() -> rx.Component:
    """Navegação mobile simplificada e elegante"""
    return rx.box(
        rx.hstack(
            rx.button(
                rx.hstack(
                    rx.text("⇄"),
                    rx.text("Conversor", class_name="hidden sm:inline text-xs font-medium"),
                    spacing="2",
                ),
                on_click=lambda: State.set_page("conversor"),
                class_name=rx.cond(
                    State.current_page == "conversor",
                    "bg-[#4CAF50] text-white px-4 py-2.5 rounded-xl shadow-md",
                    "bg-white/5 text-white/70 px-4 py-2.5 rounded-xl hover:bg-white/10"
                ),
                variant="ghost",
            ),
            rx.button(
                rx.hstack(
                    rx.text("📊"),
                    rx.text("Análise", class_name="hidden sm:inline text-xs font-medium"),
                    spacing="2",
                ),
                on_click=lambda: State.set_page("analise"),
                class_name=rx.cond(
                    State.current_page == "analise",
                    "bg-[#4CAF50] text-white px-4 py-2.5 rounded-xl shadow-md",
                    "bg-white/5 text-white/70 px-4 py-2.5 rounded-xl hover:bg-white/10"
                ),
                variant="ghost",
            ),
            rx.button(
                rx.hstack(
                    rx.text("🔬"),
                    rx.text("CQ", class_name="hidden sm:inline text-xs font-medium"),
                    spacing="2",
                ),
                on_click=lambda: State.set_page("proin"),
                class_name=rx.cond(
                    State.current_page == "proin",
                    "bg-[#4CAF50] text-white px-4 py-2.5 rounded-xl shadow-md",
                    "bg-white/5 text-white/70 px-4 py-2.5 rounded-xl hover:bg-white/10"
                ),
                variant="ghost",
            ),
            rx.spacer(),
            rx.button(
                rx.icon("log-out", size=18),
                on_click=lambda: State.logout(),
                class_name="bg-red-500/20 text-red-200 p-2.5 rounded-xl hover:bg-red-500/30 transition-all",
            ),
            spacing="2",
            justify="start",
            width="100%",
            align="center",
        ),
        class_name="md:hidden bg-[#1B5E20] p-3 rounded-2xl mb-6 shadow-lg border border-white/5"
    )
