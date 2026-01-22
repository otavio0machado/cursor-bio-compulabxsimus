import reflex as rx
from typing import List, Dict, Any, Optional
import asyncio

# Import Modular States
# Import Modular States
from .states.detective_state import DetectiveState
from .services.mapping_service import mapping_service
from .services.ai_service import ai_service
from .repositories.audit_repository import AuditRepository

class State(DetectiveState):
    """Estado global da aplicação (Modularizado)"""
    


    def get_canonical_name(self, name: str) -> str:
        """Helper para obter nome canônico de forma síncrona"""
        return mapping_service.get_canonical_name_sync(name)

    # Navegação e UI Global
    current_page: str = "dashboard"
    is_mobile_menu_open: bool = False
    
    # Auditoria e Alertas
    audit_alert_message: str = ""
    is_audit_alert_visible: bool = False
    audit_warning_level: str = "low" # low, medium, high, critical
    
    async def trigger_audit(self, record_id: str, old_data: Dict[str, Any], new_data: Dict[str, Any]):
        """Dispara o processo de auditoria."""
        # Calcular variação
        old_val = float(old_data.get("value", 0))
        new_val = float(new_data.get("value", 0))
        pct_change = ((new_val - old_val) / old_val * 100) if old_val != 0 else 0
        
        # 1. O Oráculo analisa consistência clínica
        ai_result = await ai_service.analyze_clinical_consistency({
            "exam_name": new_data.get("exam_name"),
            "lot_number": new_data.get("lot_number"),
            "level": new_data.get("level"),
            "old_value": old_val,
            "new_value": new_val,
            "percentage_change": pct_change
        })
        
        # 2. O Arquivista salva o log
        AuditRepository.create_log({
            "record_id": record_id,
            "table_name": "qc_records",
            "old_value": str(old_data),
            "new_value": str(new_data),
            "action": "update",
            "consistency_result": ai_result.model_dump_json() if hasattr(ai_result, 'model_dump_json') else str(ai_result)
        })
        
        # 3. UI/UX: Notificar com Motion System
        self.audit_alert_message = f"Auditoria: {ai_result.reason}"
        self.audit_warning_level = ai_result.warning_level
        self.is_audit_alert_visible = True
        
        # Auto-hide após 6 segundos
        yield
        await asyncio.sleep(6)
        self.is_audit_alert_visible = False
    
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
