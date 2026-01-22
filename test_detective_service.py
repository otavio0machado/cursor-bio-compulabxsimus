"""
Teste do Servico DetectiveService (Detetive de Dados)
Verifica se a conexao com a API Gemini esta funcionando corretamente.
"""
import asyncio
import os
import sys

# Adicionar o path do app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'biodiagnostico_app'))

from dotenv import load_dotenv
load_dotenv()

async def test_detective():
    from biodiagnostico_app.ai.services.detective_service import DetectiveService
    from biodiagnostico_app.ai.mock_data import get_mock_divergency_data
    
    print("=" * 60)
    print("[DETETIVE] TESTE: DetectiveService (Detetive de Dados)")
    print("=" * 60)
    
    # Verificar API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("[ERRO] GEMINI_API_KEY nao encontrada!")
        return
    print(f"[OK] API Key encontrada: {api_key[:10]}...")
    
    # Instanciar servico
    service = DetectiveService()
    print(f"[OK] Servico instanciado. Modelo: {service.model}")
    
    if not service.client:
        print("[ERRO] Cliente Gemini nao foi inicializado!")
        return
    print("[OK] Cliente Gemini inicializado.")
    
    # Carregar dados mock
    mock_data = get_mock_divergency_data()
    print(f"[OK] Dados mock carregados: {len(mock_data)} caracteres")
    
    # Testar pergunta simples
    question = "Qual o convenio com mais glosas?"
    print(f"\n[PERGUNTA] {question}")
    print("-" * 60)
    
    try:
        response = await service.ask_detective(question, mock_data)
        print("[RESPOSTA DA IA]:")
        print(response)
        print("-" * 60)
        print("[SUCESSO] A IA respondeu com sucesso!")
    except Exception as e:
        print(f"[ERRO] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_detective())
