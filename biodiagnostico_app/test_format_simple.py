"""
Teste simples da função format_divergences_to_json
Demonstra conversão de dados delimitados para JSON estruturado
"""
import json
import sys
sys.path.insert(0, '/home/user/cursor-bio-compulabxsimus/biodiagnostico_app')

# Importar diretamente o módulo
from biodiagnostico_app.utils.comparison import format_divergences_to_json


def test_with_semicolon():
    """Teste com dados delimitados por ponto-e-vírgula"""
    data = """Paciente;Nome_Exame;Codigo_Exame;Valor_Compulab;Valor_Simus;Tipo_Divergencia
ANA SILVA;HEMOGRAMA;202020380;6,15;6,16;Valor Divergente
ANA SILVA;UREIA;202010694;2,77;0,00;Exame Ausente no SIMUS
JOAO SANTOS;GLICOSE;202030456;12,50;12,50;Valor Correto
MARIA OLIVEIRA;COLESTEROL;202040567;8,90;9,00;Valor Divergente"""

    result = format_divergences_to_json(data)
    print("=== TESTE COM PONTO-E-VÍRGULA ===")
    print(result)
    print()
    return result


def test_with_comma():
    """Teste com dados delimitados por vírgula (ajustando valores)"""
    data = """Paciente,Nome_Exame,Codigo_Exame,Valor_Compulab,Valor_Simus,Tipo_Divergencia
PEDRO COSTA,CREATININA,202050678,3.45,3.45,Valor Correto
LUCIA MARTINS,TRIGLICERIDES,202060789,15.20,0.00,Exame Ausente no SIMUS"""

    result = format_divergences_to_json(data)
    print("=== TESTE COM VÍRGULA ===")
    print(result)
    print()
    return result


def test_without_header():
    """Teste com dados sem cabeçalho explícito"""
    data = """CARLOS PEREIRA;HEMOGLOBINA;202070890;14,5;14,6;Valor Divergente
FERNANDA LIMA;LEUCOCITOS;202080901;7,2;7,2;Valor Correto"""

    result = format_divergences_to_json(data)
    print("=== TESTE SEM CABEÇALHO ===")
    print(result)
    print()
    return result


def test_multiple_blocks():
    """Teste com múltiplos blocos de dados"""
    data = """Paciente;Nome_Exame;Codigo_Exame;Valor_Compulab;Valor_Simus;Tipo_Divergencia
RAFAEL SOUZA;TSH;202091012;2,5;2,5;Valor Correto
TATIANA ROCHA;T4 LIVRE;202102123;1,2;0,0;Exame Ausente no SIMUS

ANDRE ALVES;PSA;202113234;0,8;0,9;Valor Divergente
BEATRIZ NUNES;CA 125;202124345;18,5;18,5;Valor Correto"""

    result = format_divergences_to_json(data)
    print("=== TESTE COM MÚLTIPLOS BLOCOS ===")
    print(result)
    print()
    return result


def test_empty_fields():
    """Teste com campos vazios"""
    data = """Paciente;Nome_Exame;Codigo_Exame;Valor_Compulab;Valor_Simus;Tipo_Divergencia
GABRIEL PIRES;;202135456;5,0;5,0;Valor Correto
;VITAMINA D;202146567;25,0;0,0;Exame Ausente no SIMUS"""

    result = format_divergences_to_json(data)
    print("=== TESTE COM CAMPOS VAZIOS ===")
    print(result)
    print()
    return result


if __name__ == "__main__":
    print("TESTES DA FUNÇÃO format_divergences_to_json\n")
    print("=" * 60)
    print()

    results = []
    results.append(test_with_semicolon())
    results.append(test_with_comma())
    results.append(test_without_header())
    results.append(test_multiple_blocks())
    results.append(test_empty_fields())

    print("=" * 60)
    print("TESTES CONCLUÍDOS")
    print()
    print("Verificando integridade dos resultados...")
    for i, result in enumerate(results, 1):
        parsed = json.loads(result)
        print(f"Teste {i}: {len(parsed)} registros convertidos com sucesso ✓")
