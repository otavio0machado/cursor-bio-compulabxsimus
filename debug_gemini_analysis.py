
import sys
import os
print("SCRIPT STARTED", flush=True)

# Add the parent directory of the outer biodiagnostico_app folder to sys.path if needed
# But better: Add the outer folder itself
sys.path.append(os.path.join(os.getcwd(), 'biodiagnostico_app'))

from dotenv import load_dotenv
import google.genai as genai
import asyncio

try:
    from biodiagnostico_app.utils.ai_analysis import generate_ai_analysis, pre_filter_data
    print("IMPORTS SUCCESS", flush=True)
except ImportError as e:
    print(f"IMPORT ERROR: {e}", flush=True)
    # Fallback/Debug: List directories
    print(f"SYS PATH: {sys.path}", flush=True)
    sys.exit(1)

# Carregar variaveis
load_dotenv()

# Mock Data
def create_mock_data(count=100):
    compulab = {}
    simus = {}
    
    for i in range(count):
        p_id = f"PACIENTE_{i}"
        
        # Caso 1: Match Perfeito (deve ser filtrado pelo Sieve)
        if i < count * 0.8: 
            compulab[p_id] = {'exams': [{'exam_name': 'HEMOGRAMA', 'code': '123', 'value': 10.0}]}
            simus[p_id] = {'exams': [{'exam_name': 'HEMOGRAMA', 'code': '123', 'value': 10.0}]}
            
        # Caso 2: Divergencia de Valor
        elif i < count * 0.9:
            compulab[p_id] = {'exams': [{'exam_name': 'GLICOSE', 'code': '456', 'value': 50.0}]}
            simus[p_id] = {'exams': [{'exam_name': 'GLICOSE', 'code': '456', 'value': 25.0}]}
            
        # Caso 3: Paciente Ausente no SIMUS
        else:
            compulab[p_id] = {'exams': [{'exam_name': 'COLESTEROL', 'code': '789', 'value': 15.0}]}
            # Ausente no simus
            
    return compulab, simus

async def run_test():
    print("=== INICIANDO TESTE DE STRESS GEMINI 2.5 FLASH ===")
    
    # Criar 200 pacientes (para gerar uns 2-3 batches após filtro)
    print("Gerando dados mockados...")
    compulab, simus = create_mock_data(250)
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERRO: API KEY NAO ENCONTRADA")
        return

    print(f"Iniciando análise com modelo: gemini-2.5-flash")
    
    start_time = asyncio.get_event_loop().time()
    
    try:
        async for progress, msg in generate_ai_analysis(
            compulab, 
            simus, 
            api_key, 
            provider="Gemini", 
            model_name="gemini-2.5-flash"
        ):
            print(f"[{progress}%] {msg}")
            
    except Exception as e:
        print(f"\nCRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        
    end_time = asyncio.get_event_loop().time()
    print(f"\n=== TESTE FINALIZADO EM {end_time - start_time:.2f} SEGUNDOS ===")

if __name__ == "__main__":
    asyncio.run(run_test())
