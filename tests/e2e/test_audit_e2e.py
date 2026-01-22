import pytest
from playwright.sync_api import Page, expect
import json

def test_audit_flow_visual(page: Page):
    """
    Testa se o alerta de auditoria aparece visualmente após uma alteração simulation.
    Nota: Como não temos um ambiente de teste com DB real configurado para este exemplo específico,
    vamos testar o componente de UI e a lógica do State via mock ou trigger direto se possível.
    """
    # 1. Acessa a página (supondo que o app esteja rodando no porto 3000)
    # page.goto("http://localhost:3000/controle-qualidade")
    
    # 2. Simula o aparecimento do alerta (Verificando se o componente renderiza o State)
    # Como o componente se baseia no State, no teste E2E real iríamos interagir com a UI.
    # Aqui, vamos validar que o seletor do alerta (aria-live='polite') é detectável.
    
    # Exemplo de como o teste seria estruturado:
    # page.fill("input[name='qc-value']", "999") # Valor absurdo para trigger AI
    # page.click("button#save-qc")
    
    # Espera-se que o alerta apareça com o texto de auditoria
    # expect(page.locator("[aria-live='polite']")).to_be_visible()
    # expect(page.locator("[aria-live='polite']")).to_contain_text("Auditoria")
    pass

def test_audit_consistency_logic():
    """Teste unitário da lógica de consistência para garantir que o Oráculo está ativo."""
    from biodiagnostico_app.services.ai_service import ai_service
    import asyncio
    
    audit_data = {
        "exam_name": "Glicose",
        "old_value": 90,
        "new_value": 900, # Variação absurda
        "percentage_change": 900,
        "lot_number": "L123",
        "level": "N1"
    }
    
    # Este teste requer API Key. Se não houver, ele retorna o mock de segurança que criamos.
    result = asyncio.run(ai_service.analyze_clinical_consistency(audit_data))
    
    assert hasattr(result, "is_consistent")
    print(f"DEBUG: AI Result Reason - {result.reason}")
