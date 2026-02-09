import reflex as rx

from .states.qc_state import QCState

class State(QCState):
    """Estado global da aplicação - Controle de Qualidade"""

    # Navegação e UI Global
    current_page: str = "dashboard"
    is_mobile_menu_open: bool = False

    def set_page(self, page: str):
        """Define a página atual"""
        self.current_page = page
        self.is_mobile_menu_open = False

    def toggle_mobile_menu(self):
        """Alterna visibilidade do menu mobile"""
        self.is_mobile_menu_open = not self.is_mobile_menu_open

    def navigate_to(self, page: str):
        """Navega para uma página específica"""
        self.set_page(page)
        if page == "dashboard":
            return rx.redirect("/")
        return rx.redirect(f"/{page}")

    def reset_state(self):
        """Reseta todos os campos para defaults (delegado para self.reset do Reflex)"""
        self.reset()
