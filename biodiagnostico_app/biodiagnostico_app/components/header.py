"""
Header component for Biodiagnóstico App
Design Premium SaaS - Clean & Clinical
"""
import reflex as rx


def header() -> rx.Component:
    """Renderiza o header do laboratório com design oficial premium"""
    return rx.box(
        rx.box(
            rx.hstack(
                rx.box(
                    rx.text("🧬", class_name="text-3xl"),
                    class_name="bg-white/10 p-2 rounded-xl backdrop-blur-sm"
                ),
                rx.vstack(
                    rx.hstack(
                        rx.text(
                            "LABORATÓRIO",
                            class_name="text-green-100 font-bold text-xs tracking-[0.2em]"
                        ),
                        rx.box(class_name="w-1 h-1 bg-green-400 rounded-full"),
                        rx.text(
                            "CAMAQUÃ",
                            class_name="text-green-100 font-bold text-xs tracking-[0.2em]"
                        ),
                        align="center",
                        spacing="2"
                    ),
                    rx.hstack(
                        rx.text(
                            "Biodiagnóstico",
                            class_name="text-white font-bold text-2xl md:text-3xl font-['Poppins'] leading-none"
                        ),
                        rx.badge(
                            "ADMIN",
                            variant="solid",
                            color_scheme="green",
                            class_name="bg-green-400/20 text-green-100 border border-green-400/30 backdrop-blur-md"
                        ),
                        align="center",
                        spacing="3",
                    ),
                    spacing="1",
                    align="start",
                ),
                rx.spacer(),
                # Certification Badge - Premium Style
                rx.box(
                    rx.hstack(
                        rx.box(
                            rx.text("💎", class_name="text-xl"),
                            class_name="w-10 h-10 bg-gradient-to-br from-blue-400 to-blue-600 rounded-lg flex items-center justify-center shadow-lg shadow-blue-900/20"
                        ),
                        rx.vstack(
                            rx.text(
                                "PNCQ DIAMANTE",
                                class_name="text-white font-bold text-xs tracking-wide"
                            ),
                            rx.text(
                                "Excelência Garantida",
                                class_name="text-blue-100 text-[10px] opacity-80"
                            ),
                            spacing="0",
                            align="start",
                        ),
                        spacing="3",
                        align="center",
                    ),
                    class_name="bg-white/10 backdrop-blur-md px-4 py-2 rounded-xl border border-white/10 hidden md:flex"
                ),
                align="center",
                spacing="4",
                width="100%",
            ),
            class_name="relative z-10"
        ),
        # Padrão de fundo decorativo - Clinical Abstract
        rx.box(
            class_name="absolute inset-0 opacity-10 bg-[radial-gradient(circle_at_20%_80%,rgba(139,195,74,0.4)_0%,transparent_50%),radial-gradient(circle_at_80%_20%,rgba(255,255,255,0.1)_0%,transparent_50%)]"
        ),
        rx.box(
            class_name="absolute right-0 top-0 w-64 h-full bg-gradient-to-l from-white/5 to-transparent"
        ),
        class_name="bg-gradient-to-r from-[#1B5E20] to-[#2E7D32] p-6 md:p-8 rounded-3xl mb-8 relative overflow-hidden shadow-xl shadow-green-900/10 border border-white/5"
    )


def mini_header() -> rx.Component:
    """Header compacto para páginas internas"""
    return rx.hstack(
        rx.text("🧬", class_name="text-2xl"),
        rx.hstack(
            rx.text(
                "Laboratório ",
                class_name="text-white font-semibold text-lg font-['Poppins']"
            ),
            rx.text(
                "Biodiagnóstico",
                class_name="text-lime-400 font-semibold text-lg font-['Poppins']"
            ),
            spacing="1",
        ),
        align="center",
        spacing="2",
        class_name="p-4"
    )
