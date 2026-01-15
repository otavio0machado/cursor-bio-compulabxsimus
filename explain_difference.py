import pdfplumber
from decimal import Decimal
import re
from collections import defaultdict

def extract_currency_value(text):
    """Extrai valores em formato brasileiro (R$ X.XXX,XX)"""
    pattern = r'R\$\s*([\d.]+,\d{2})'
    matches = re.findall(pattern, text)
    values = []
    for match in matches:
        value_str = match.replace('.', '').replace(',', '.')
        try:
            values.append(Decimal(value_str))
        except:
            pass
    return values

def parse_table_value(cell):
    """Converte célula de tabela para valor decimal"""
    if not cell:
        return None
    cell_str = str(cell).strip()
    cell_str = re.sub(r'R\$\s*', '', cell_str)
    cell_str = cell_str.replace('.', '').replace(',', '.')
    try:
        return Decimal(cell_str)
    except:
        return None

def extract_exam_codes_and_values_compulab():
    """Extrai códigos de exames e seus valores do COMPULAB"""
    codes_values = defaultdict(list)
    
    with pdfplumber.open('COMPULAB.pdf') as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            
            # Procurar por padrão: código seguido de valores
            # Padrão comum: código de 10 dígitos seguido de valores
            lines = text.split('\n')
            for line in lines:
                # Procurar códigos de 10 dígitos
                codes = re.findall(r'\b(\d{10})\b', line)
                if codes:
                    # Procurar valores na mesma linha
                    values = extract_currency_value(line)
                    for code in codes:
                        if values:
                            codes_values[code].extend(values)
    
    return codes_values

def extract_exam_codes_and_values_simus():
    """Extrai códigos de exames e seus valores do SIMUS"""
    codes_values = defaultdict(list)
    
    with pdfplumber.open('SIMUS.pdf') as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    if not row:
                        continue
                    
                    row_text = ' | '.join([str(cell) if cell else '' for cell in row])
                    
                    # Procurar códigos de 10 dígitos
                    codes = re.findall(r'\b(\d{10})\b', row_text)
                    if codes:
                        # Procurar valores na linha (VALOR PAGO)
                        values = []
                        for cell in row:
                            val = parse_table_value(cell)
                            if val:
                                values.append(val)
                        
                        # Geralmente o VALOR PAGO é o segundo valor monetário
                        for code in codes:
                            if len(values) >= 2:
                                # VALOR PAGO geralmente é o segundo
                                codes_values[code].append(values[1] if len(values) > 1 else values[0])
    
    return codes_values

def calculate_exclusive_codes_value():
    """Calcula o valor dos códigos que estão apenas no COMPULAB"""
    print("=" * 100)
    print("CÁLCULO DO VALOR DOS CÓDIGOS EXCLUSIVOS DO COMPULAB")
    print("=" * 100)
    
    # Extrair códigos e valores
    print("\n[1] Extraindo códigos e valores do COMPULAB...")
    compulab_codes_values = extract_exam_codes_and_values_compulab()
    print(f"   {len(compulab_codes_values)} códigos encontrados no COMPULAB")
    
    print("\n[2] Extraindo códigos e valores do SIMUS...")
    simus_codes_values = extract_exam_codes_and_values_simus()
    print(f"   {len(simus_codes_values)} códigos encontrados no SIMUS")
    
    # Encontrar códigos exclusivos do COMPULAB
    compulab_codes = set(compulab_codes_values.keys())
    simus_codes = set(simus_codes_values.keys())
    
    only_compulab = compulab_codes - simus_codes
    only_simus = simus_codes - compulab_codes
    
    print(f"\n[3] Códigos exclusivos:")
    print(f"   Apenas no COMPULAB: {len(only_compulab)}")
    print(f"   Apenas no SIMUS: {len(only_simus)}")
    
    # Calcular valor total dos códigos exclusivos do COMPULAB
    print(f"\n[4] Calculando valor dos códigos exclusivos do COMPULAB...")
    exclusive_total = Decimal('0')
    exclusive_details = []
    
    for code in only_compulab:
        values = compulab_codes_values[code]
        if values:
            # Usar o maior valor ou média (dependendo do caso)
            code_value = max(values) if values else Decimal('0')
            exclusive_total += code_value
            exclusive_details.append({
                'code': code,
                'value': code_value,
                'count': len(values)
            })
    
    print(f"\n   Valor total dos códigos exclusivos: R$ {exclusive_total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    
    # Comparar com a diferença
    difference = Decimal('3227.56')
    print(f"\n   Diferença entre COMPULAB e SIMUS: R$ {difference:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    
    if abs(exclusive_total - difference) < Decimal('100'):
        print(f"\n   ✓ O valor dos códigos exclusivos ({exclusive_total:,.2f}) está próximo da diferença ({difference:,.2f})!".replace(',', 'X').replace('.', ',').replace('X', '.'))
    else:
        print(f"\n   ⚠ O valor dos códigos exclusivos não explica totalmente a diferença.")
        print(f"      Diferença restante: R$ {abs(exclusive_total - difference):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    
    # Mostrar detalhes dos códigos exclusivos
    print(f"\n[5] Detalhes dos códigos exclusivos do COMPULAB:")
    exclusive_details.sort(key=lambda x: x['value'], reverse=True)
    for detail in exclusive_details:
        print(f"   Código {detail['code']}: R$ {detail['value']:,.2f} (aparece {detail['count']} vez(es))".replace(',', 'X').replace('.', ',').replace('X', '.'))
    
    return exclusive_total, exclusive_details

def analyze_value_differences():
    """Analisa diferenças de valores para códigos comuns"""
    print("\n" + "=" * 100)
    print("ANÁLISE DE DIFERENÇAS DE VALORES PARA CÓDIGOS COMUNS")
    print("=" * 100)
    
    compulab_codes_values = extract_exam_codes_and_values_compulab()
    simus_codes_values = extract_exam_codes_and_values_simus()
    
    common_codes = set(compulab_codes_values.keys()) & set(simus_codes_values.keys())
    
    print(f"\nAnalisando {len(common_codes)} códigos comuns...")
    
    value_differences = []
    for code in common_codes:
        compulab_vals = compulab_codes_values[code]
        simus_vals = simus_codes_values[code]
        
        if compulab_vals and simus_vals:
            compulab_avg = sum(compulab_vals) / len(compulab_vals)
            simus_avg = sum(simus_vals) / len(simus_vals)
            diff = compulab_avg - simus_avg
            
            if abs(diff) > Decimal('0.01'):  # Apenas diferenças significativas
                value_differences.append({
                    'code': code,
                    'compulab_avg': compulab_avg,
                    'simus_avg': simus_avg,
                    'difference': diff
                })
    
    if value_differences:
        print(f"\nEncontradas diferenças de valor para {len(value_differences)} códigos:")
        value_differences.sort(key=lambda x: abs(x['difference']), reverse=True)
        for item in value_differences[:10]:
            print(f"\n   Código {item['code']}:")
            print(f"     COMPULAB média: R$ {item['compulab_avg']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
            print(f"     SIMUS média:    R$ {item['simus_avg']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
            print(f"     Diferença:     R$ {item['difference']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    
    return value_differences

def main():
    print("=" * 100)
    print("EXPLICAÇÃO FINAL DA DIFERENÇA ENTRE COMPULAB E SIMUS")
    print("=" * 100)
    
    compulab_total = Decimal('30872.24')
    simus_total = Decimal('27644.68')
    difference = compulab_total - simus_total
    
    print(f"\nRESUMO:")
    print(f"  COMPULAB Total:        R$ {compulab_total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    print(f"  SIMUS Contratualizado: R$ {simus_total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    print(f"  DIFERENÇA:            R$ {difference:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    
    # Calcular valor dos códigos exclusivos
    exclusive_total, exclusive_details = calculate_exclusive_codes_value()
    
    # Analisar diferenças de valores
    value_differences = analyze_value_differences()
    
    # Gerar relatório final
    print("\n" + "=" * 100)
    print("GERANDO RELATÓRIO FINAL...")
    print("=" * 100)
    
    with open('explicacao_diferenca.txt', 'w', encoding='utf-8') as f:
        f.write("EXPLICAÇÃO DA DIFERENÇA ENTRE COMPULAB E SIMUS\n")
        f.write("=" * 100 + "\n\n")
        
        f.write("RESUMO:\n")
        f.write(f"  COMPULAB Total:        R$ {compulab_total:,.2f}\n".replace(',', 'X').replace('.', ',').replace('X', '.'))
        f.write(f"  SIMUS Contratualizado: R$ {simus_total:,.2f}\n".replace(',', 'X').replace('.', ',').replace('X', '.'))
        f.write(f"  DIFERENÇA:            R$ {difference:,.2f}\n\n".replace(',', 'X').replace('.', ',').replace('X', '.'))
        
        f.write("\nCAUSA PROVÁVEL DA DIFERENÇA:\n")
        f.write("-" * 100 + "\n")
        f.write(f"O COMPULAB contém {len(exclusive_details)} códigos de exames que NÃO estão no SIMUS.\n")
        f.write(f"O valor total desses códigos exclusivos é: R$ {exclusive_total:,.2f}\n\n".replace(',', 'X').replace('.', ',').replace('X', '.'))
        
        if abs(exclusive_total - difference) < Decimal('100'):
            f.write("✓ CONCLUSÃO: A diferença de R$ {:.2f} é explicada principalmente pelos exames\n".format(difference))
            f.write("  que estão no COMPULAB mas não foram incluídos no cálculo do SIMUS Contratualizado.\n\n")
        else:
            f.write("⚠ A diferença não é totalmente explicada pelos códigos exclusivos.\n")
            f.write(f"  Diferença restante: R$ {abs(exclusive_total - difference):,.2f}\n\n".replace(',', 'X').replace('.', ',').replace('X', '.'))
        
        f.write("\nCÓDIGOS EXCLUSIVOS DO COMPULAB:\n")
        f.write("-" * 100 + "\n")
        for detail in exclusive_details:
            f.write(f"Código {detail['code']}: R$ {detail['value']:,.2f} (aparece {detail['count']} vez(es))\n".replace(',', 'X').replace('.', ',').replace('X', '.'))
    
    print("\n   Relatório salvo em: explicacao_diferenca.txt")
    print("\n" + "=" * 100)
    print("Análise concluída!")
    print("=" * 100)

if __name__ == '__main__':
    main()

