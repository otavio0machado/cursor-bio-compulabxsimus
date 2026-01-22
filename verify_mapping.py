"""
Script de Verificação do Mapeamento de Exames
"""
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'biodiagnostico_app')))

from biodiagnostico_app.services.mapping_service import MappingService

def test_mapping_logic():
    print("Iniciando testes de mapeamento...")
    
    # Mock do cache (simulando carregamento do banco)
    MappingService._cache = {
        "HEMOGRAMA COMPLETO": "HEMOGRAMA",
        "DOSAGEM DE GLICOSE": "GLICOSE",
        "G O T": "GOT",
        "G P T": "GPT"
    }
    MappingService._is_loaded = True
    
    test_cases = [
        ("HEMOGRAMA COMPLETO", "HEMOGRAMA"),
        ("HEMOGRAMA COMPLETO ", "HEMOGRAMA"),
        ("hemograma completo", "HEMOGRAMA"),
        ("G O T", "GOT"),
        ("EXAME INEXISTENTE", "EXAME INEXISTENTE")
    ]
    
    success = True
    for original, expected in test_cases:
        result = MappingService.get_canonical_name_sync(original)
        if result == expected:
            print(f"[OK]: '{original}' -> '{result}'")
        else:
            print(f"[FAIL]: '{original}' -> esperado '{expected}', obteve '{result}'")
            success = False
            
    if success:
        print("\nTodos os testes de lógica de mapeamento passaram!")
    else:
        print("\nHouve falhas nos testes.")
        sys.exit(1)

if __name__ == "__main__":
    test_mapping_logic()
