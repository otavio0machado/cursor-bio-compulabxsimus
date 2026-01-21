import reflex as rx
from typing import List, Dict, Any, Optional
import asyncio

# Import Modular States
from .states import AIState

class State(AIState):
    """Estado global da aplicação (Modularizado)"""
    
    # Lista restrita de exames permitidos no QC (Solicitação do Usuário)
    ALLOWED_QC_EXAMS: List[str] = [
        "GLICOSE Cal",
        "COLESTEROL",
        "TRIGLICERIDIOS",
        "UREIA",
        "CREATININA P",
        "AC. URICO",
        "TGO",
        "TGP",
        "GGT",
        "FAL DGKC 137 131",
        "AMILASE",
        "CPK Total",
        "P HDL eva 50",
        "COLESTEROL 2 P200"
    ]

    # Navegação e UI Global
    current_page: str = "dashboard"
    is_mobile_menu_open: bool = False
    
    def set_page(self, page: str):
        """Define a página atual"""
        self.current_page = page
        # Fechar menu mobile ao navegar
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

    # Método genérico para resetar estados se necessário
    def reset_state(self):
        pass
