"""
Teste standalone da função format_divergences_to_json
Demonstra conversão de dados delimitados para JSON estruturado
"""
import json


def format_divergences_to_json(delimited_data: str) -> str:
    """
    Converte dados delimitados de divergências laboratoriais em JSON estruturado.

    Entrada esperada (delimitado por ; ou ,):
    Paciente;Nome_Exame;Codigo_Exame;Valor_Compulab;Valor_Simus;Tipo_Divergencia
    ANA SILVA;HEMOGRAMA;202020380;6,15;6,16;Valor Divergente

    Saída: JSON array com objetos estruturados
    """
    if not delimited_data or not delimited_data.strip():
        return "[]"

    lines = delimited_data.strip().split('\n')
    if not lines:
        return "[]"

    # Detectar delimitador (ponto-e-vírgula ou vírgula)
    first_line = lines[0]
    delimiter = ';' if ';' in first_line else ','

    result = []
    header_found = False
    expected_fields = ["Paciente", "Nome_Exame", "Codigo_Exame", "Valor_Compulab", "Valor_Simus", "Tipo_Divergencia"]

    for line in lines:
        line = line.strip()
        if not line:
            continue

        parts = [p.strip() for p in line.split(delimiter)]

        # Verificar se é cabeçalho
        if not header_found and any(field in line for field in expected_fields):
            header_found = True
            continue

        # Processar linha de dados
        if len(parts) >= 6:
            obj = {
                "Paciente": parts[0] if len(parts) > 0 else "",
                "Nome_Exame": parts[1] if len(parts) > 1 else "",
                "Codigo_Exame": parts[2] if len(parts) > 2 else "",
                "Valor_Compulab": parts[3] if len(parts) > 3 else "",
                "Valor_Simus": parts[4] if len(parts) > 4 else "",
                "Tipo_Divergencia": parts[5] if len(parts) > 5 else ""
            }
            result.append(obj)

    return json.dumps(result, ensure_ascii=False, indent=2)


def test_with_semicolon():
    """Teste com dados delimitados por ponto-e-vírgula"""
    data = """Paciente;Nome_Exame;Codigo_Exame;Valor_Compulab;Valor_Simus;Tipo_Divergencia
ANA SILVA;HEMOGRAMA;202020380;6,15;6,16;Valor Divergente
ANA SILVA;UREIA;202010694;2,77;0,00;Exame Ausente no SIMUS
JOAO SANTOS;GLICOSE;202030456;12,50;12,50;Valor Correto
MARIA OLIVEIRA;COLESTEROL;202040567;8,90;9,00;Valor Divergente"""

    result = format_divergences_to_json(data)
    print("=== TESTE 1: PONTO-E-VÍRGULA ===")
    print(result)
    print()
    return result


def test_with_comma():
    """Teste com dados delimitados por vírgula"""
    data = """Paciente,Nome_Exame,Codigo_Exame,Valor_Compulab,Valor_Simus,Tipo_Divergencia
PEDRO COSTA,CREATININA,202050678,3.45,3.45,Valor Correto
LUCIA MARTINS,TRIGLICERIDES,202060789,15.20,0.00,Exame Ausente no SIMUS"""

    result = format_divergences_to_json(data)
    print("=== TESTE 2: VÍRGULA ===")
    print(result)
    print()
    return result


def test_without_header():
    """Teste com dados sem cabeçalho explícito"""
    data = """CARLOS PEREIRA;HEMOGLOBINA;202070890;14,5;14,6;Valor Divergente
FERNANDA LIMA;LEUCOCITOS;202080901;7,2;7,2;Valor Correto"""

    result = format_divergences_to_json(data)
    print("=== TESTE 3: SEM CABEÇALHO ===")
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
    print("=== TESTE 4: MÚLTIPLOS BLOCOS ===")
    print(result)
    print()
    return result


def test_empty_fields():
    """Teste com campos vazios"""
    data = """Paciente;Nome_Exame;Codigo_Exame;Valor_Compulab;Valor_Simus;Tipo_Divergencia
GABRIEL PIRES;;202135456;5,0;5,0;Valor Correto
;VITAMINA D;202146567;25,0;0,0;Exame Ausente no SIMUS"""

    result = format_divergences_to_json(data)
    print("=== TESTE 5: CAMPOS VAZIOS ===")
    print(result)
    print()
    return result


if __name__ == "__main__":
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 15 + "TESTES DA FUNÇÃO format_divergences_to_json" + " " * 20 + "║")
    print("╚" + "=" * 78 + "╝")
    print()

    results = []
    results.append(test_with_semicolon())
    results.append(test_with_comma())
    results.append(test_without_header())
    results.append(test_multiple_blocks())
    results.append(test_empty_fields())

    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 30 + "RESUMO DOS TESTES" + " " * 31 + "║")
    print("╚" + "=" * 78 + "╝")
    print()

    for i, result in enumerate(results, 1):
        parsed = json.loads(result)
        print(f"✓ Teste {i}: {len(parsed)} registros convertidos com sucesso")

    print()
    print("Todos os testes foram executados com sucesso! ✓")
