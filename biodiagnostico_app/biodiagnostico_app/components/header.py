"""
Header component for Biodiagnóstico App
"""
import reflex as rx


def header() -> rx.Component:
    """Renderiza o header do laboratório com design oficial"""
    return rx.box(
        rx.box(
            rx.hstack(
                rx.text("🧬", class_name="text-4xl"),
                rx.hstack(
                    rx.text(
                        "Laboratório ",
                        class_name="text-white font-bold text-2xl md:text-3xl font-['Poppins']"
                    ),
                    rx.text(
                        "Biodiagnóstico",
                        class_name="text-lime-400 font-bold text-2xl md:text-3xl font-['Poppins']"
                    ),
                    spacing="1",
                ),
                align="center",
                spacing="3",
            ),
            rx.text(
                "Sistema de Administração • Camaquã e região",
                class_name="text-white/90 text-sm md:text-base mt-2"
            ),
            rx.box(
                rx.hstack(
                    rx.text("🏆", class_name="text-sm"),
                    rx.text(
                        "Certificação PNCQ Diamante",
                        class_name="text-white text-sm font-medium"
                    ),
                    spacing="2",
                    align="center",
                ),
                class_name="bg-white/15 backdrop-blur-sm px-4 py-2 rounded-full mt-4 inline-flex border border-white/20"
            ),
            class_name="relative z-10"
        ),
        # Padrão de fundo decorativo
        rx.box(
            class_name="absolute inset-0 opacity-10 bg-[radial-gradient(circle_at_20%_80%,rgba(139,195,74,0.3)_0%,transparent_50%),radial-gradient(circle_at_80%_20%,rgba(139,195,74,0.3)_0%,transparent_50%)]"
        ),
        class_name="bg-gradient-to-r from-green-800 to-green-700 p-6 md:p-8 rounded-2xl mb-8 relative overflow-hidden shadow-xl shadow-green-900/30"
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

