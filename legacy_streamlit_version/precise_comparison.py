import pdfplumber
from decimal import Decimal
import re
from collections import defaultdict

def parse_compulab_line(line):
    """Extrai código e valor de uma linha do COMPULAB"""
    # Padrão: código de 10 dígitos seguido de números (CH) e valor
    # Exemplo: "VITAMINA B12 0202010708 23 22,84"
    pattern = r'(\d{10})\s+\d+\s+([\d,]+)'
    match = re.search(pattern, line)
    if match:
        code = match.group(1)
        value_str = match.group(2).replace(',', '.')
        try:
            return code, Decimal(value_str)
        except:
            pass
    return None, None

def extract_compulab_data():
    """Extrai todos os códigos e valores do COMPULAB"""
    codes_values = defaultdict(list)
    
    with pdfplumber.open('COMPULAB.pdf') as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            
            lines = text.split('\n')
            for line in lines:
                code, value = parse_compulab_line(line)
                if code and value:
                    codes_values[code].append(value)
    
    return codes_values

def parse_simus_table_row(row):
    """Extrai código e valor de uma linha de tabela do SIMUS"""
    if not row or len(row) < 8:
        return None, None
    
    row_text = ' '.join([str(cell) if cell else '' for cell in row])
    
    # Procurar código de 10 dígitos
    code_match = re.search(r'\b(\d{10})\b', row_text)
    if not code_match:
        return None, None
    
    code = code_match.group(1)
    
    # Procurar VALOR PAGO (geralmente o segundo valor monetário)
    values = []
    for cell in row:
        if not cell:
            continue
        cell_str = str(cell).strip()
        # Procurar por padrão R$ X.XXX,XX
        val_match = re.search(r'R\$\s*([\d.]+,\d{2})', cell_str)
        if val_match:
            value_str = val_match.group(1).replace('.', '').replace(',', '.')
            try:
                values.append(Decimal(value_str))
            except:
                pass
    
    # VALOR PAGO geralmente é o segundo valor (índice 1)
    if len(values) >= 2:
        return code, values[1]  # VALOR PAGO
    elif len(values) == 1:
        return code, values[0]
    
    return None, None

def extract_simus_data():
    """Extrai todos os códigos e valores do SIMUS"""
    codes_values = defaultdict(list)
    
    with pdfplumber.open('SIMUS.pdf') as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    code, value = parse_simus_table_row(row)
                    if code and value:
                        codes_values[code].append(value)
    
    return codes_values

def calculate_total_by_code(codes_values):
    """Calcula o total por código (soma de todas as ocorrências)"""
    totals = {}
    for code, values in codes_values.items():
        totals[code] = sum(values)
    return totals

def main():
    print("=" * 100)
    print("COMPARAÇÃO PRECISA ENTRE COMPULAB E SIMUS")
    print("=" * 100)
    
    # Extrair dados
    print("\n[1] Extraindo dados do COMPULAB...")
    compulab_data = extract_compulab_data()
    print(f"   {len(compulab_data)} códigos únicos encontrados")
    
    print("\n[2] Extraindo dados do SIMUS...")
    simus_data = extract_simus_data()
    print(f"   {len(simus_data)} códigos únicos encontrados")
    
    # Calcular totais
    print("\n[3] Calculando totais por código...")
    compulab_totals = calculate_total_by_code(compulab_data)
    simus_totals = calculate_total_by_code(simus_data)
    
    # Comparar
    print("\n[4] Comparando valores...")
    compulab_total = sum(compulab_totals.values())
    simus_total = sum(simus_totals.values())
    
    print(f"\n   Total COMPULAB (soma de todos os códigos): R$ {compulab_total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    print(f"   Total SIMUS (soma de todos os códigos):    R$ {simus_total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    
    # Valores esperados
    compulab_expected = Decimal('30872.24')
    simus_expected = Decimal('27644.68')
    difference_expected = compulab_expected - simus_expected
    
    print(f"\n   Total esperado COMPULAB: R$ {compulab_expected:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    print(f"   Total esperado SIMUS:    R$ {simus_expected:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    print(f"   Diferença esperada:      R$ {difference_expected:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    
    # Encontrar códigos exclusivos
    compulab_codes = set(compulab_data.keys())
    simus_codes = set(simus_data.keys())
    
    only_compulab = compulab_codes - simus_codes
    only_simus = simus_codes - compulab_codes
    common_codes = compulab_codes & simus_codes
    
    print(f"\n[5] Códigos exclusivos:")
    print(f"   Apenas no COMPULAB: {len(only_compulab)}")
    print(f"   Apenas no SIMUS: {len(only_simus)}")
    print(f"   Em comum: {len(common_codes)}")
    
    # Calcular valor dos códigos exclusivos do COMPULAB
    exclusive_compulab_total = Decimal('0')
    exclusive_details = []
    
    for code in only_compulab:
        code_total = compulab_totals[code]
        exclusive_compulab_total += code_total
        exclusive_details.append({
            'code': code,
            'total': code_total,
            'count': len(compulab_data[code])
        })
    
    print(f"\n[6] Valor dos códigos exclusivos do COMPULAB:")
    print(f"   Total: R$ {exclusive_compulab_total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    
    if abs(exclusive_compulab_total - difference_expected) < Decimal('50'):
        print(f"   ✓ Este valor está próximo da diferença esperada!")
    else:
        print(f"   ⚠ Diferença: R$ {abs(exclusive_compulab_total - difference_expected):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    
    # Comparar valores para códigos comuns
    print(f"\n[7] Comparando valores para códigos comuns...")
    value_differences = []
    
    for code in common_codes:
        compulab_val = compulab_totals[code]
        simus_val = simus_totals[code]
        diff = compulab_val - simus_val
        
        if abs(diff) > Decimal('0.01'):
            value_differences.append({
                'code': code,
                'compulab': compulab_val,
                'simus': simus_val,
                'difference': diff
            })
    
    if value_differences:
        print(f"   Encontradas diferenças para {len(value_differences)} códigos:")
        value_differences.sort(key=lambda x: abs(x['difference']), reverse=True)
        total_diff_common = sum([d['difference'] for d in value_differences])
        print(f"   Diferença total nos códigos comuns: R$ {total_diff_common:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        
        print(f"\n   Top 10 diferenças:")
        for item in value_differences[:10]:
            print(f"     Código {item['code']}:")
            print(f"       COMPULAB: R$ {item['compulab']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
            print(f"       SIMUS:    R$ {item['simus']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
            print(f"       Diferença: R$ {item['difference']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    
    # Gerar relatório
    print("\n" + "=" * 100)
    print("GERANDO RELATÓRIO...")
    print("=" * 100)
    
    with open('comparacao_precisa.txt', 'w', encoding='utf-8') as f:
        f.write("COMPARAÇÃO PRECISA ENTRE COMPULAB E SIMUS\n")
        f.write("=" * 100 + "\n\n")
        
        f.write("RESUMO:\n")
        f.write(f"  COMPULAB Total calculado: R$ {compulab_total:,.2f}\n".replace(',', 'X').replace('.', ',').replace('X', '.'))
        f.write(f"  COMPULAB Total esperado:  R$ {compulab_expected:,.2f}\n".replace(',', 'X').replace('.', ',').replace('X', '.'))
        f.write(f"  SIMUS Total calculado:    R$ {simus_total:,.2f}\n".replace(',', 'X').replace('.', ',').replace('X', '.'))
        f.write(f"  SIMUS Total esperado:     R$ {simus_expected:,.2f}\n".replace(',', 'X').replace('.', ',').replace('X', '.'))
        f.write(f"  DIFERENÇA:               R$ {difference_expected:,.2f}\n\n".replace(',', 'X').replace('.', ',').replace('X', '.'))
        
        f.write("\nCÓDIGOS EXCLUSIVOS DO COMPULAB:\n")
        f.write("-" * 100 + "\n")
        exclusive_details.sort(key=lambda x: x['total'], reverse=True)
        for detail in exclusive_details:
            f.write(f"Código {detail['code']}: R$ {detail['total']:,.2f} ({detail['count']} ocorrência(s))\n".replace(',', 'X').replace('.', ',').replace('X', '.'))
        
        f.write(f"\nTotal dos códigos exclusivos: R$ {exclusive_compulab_total:,.2f}\n\n".replace(',', 'X').replace('.', ',').replace('X', '.'))
        
        if value_differences:
            f.write("\nDIFERENÇAS NOS CÓDIGOS COMUNS:\n")
            f.write("-" * 100 + "\n")
            for item in value_differences[:20]:
                f.write(f"Código {item['code']}:\n")
                f.write(f"  COMPULAB: R$ {item['compulab']:,.2f}\n".replace(',', 'X').replace('.', ',').replace('X', '.'))
                f.write(f"  SIMUS:    R$ {item['simus']:,.2f}\n".replace(',', 'X').replace('.', ',').replace('X', '.'))
                f.write(f"  Diferença: R$ {item['difference']:,.2f}\n\n".replace(',', 'X').replace('.', ',').replace('X', '.'))
    
    print("\n   Relatório salvo em: comparacao_precisa.txt")
    print("\n" + "=" * 100)
    print("Análise concluída!")
    print("=" * 100)

if __name__ == '__main__':
    main()

