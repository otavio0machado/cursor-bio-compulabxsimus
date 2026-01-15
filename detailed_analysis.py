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
    # Remove R$ e espaços, depois converte
    cell_str = re.sub(r'R\$\s*', '', cell_str)
    cell_str = cell_str.replace('.', '').replace(',', '.')
    try:
        return Decimal(cell_str)
    except:
        return None

def analyze_simus_tables():
    """Analisa todas as tabelas do SIMUS para encontrar itens e valores"""
    items = []
    totals = []
    
    with pdfplumber.open('SIMUS.pdf') as pdf:
        for page_num, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            for table_idx, table in enumerate(tables):
                # Procura por valores nas tabelas
                for row_idx, row in enumerate(table):
                    if not row:
                        continue
                    row_values = []
                    row_text = []
                    for cell in row:
                        if cell:
                            row_text.append(str(cell).strip())
                            val = parse_table_value(cell)
                            if val:
                                row_values.append(val)
                    
                    # Se a linha tem valores, adiciona aos itens
                    if row_values:
                        items.append({
                            'page': page_num + 1,
                            'table': table_idx + 1,
                            'row': row_idx + 1,
                            'text': ' | '.join(row_text),
                            'values': row_values,
                            'sum': sum(row_values)
                        })
    
    return items

def analyze_compulab():
    """Analisa o PDF COMPULAB para extrair informações"""
    text = ''
    values = []
    
    with pdfplumber.open('COMPULAB.pdf') as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + '\n'
                vals = extract_currency_value(page_text)
                values.extend(vals)
    
    return {
        'text': text,
        'values': values,
        'total': max(values) if values else None
    }

def main():
    print("=" * 100)
    print("ANÁLISE DETALHADA - COMPULAB vs SIMUS")
    print("=" * 100)
    
    # Analisar COMPULAB
    print("\n[1] Analisando COMPULAB.pdf...")
    compulab = analyze_compulab()
    compulab_total = Decimal('30872.24')
    print(f"   Total encontrado: R$ {compulab_total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    
    # Analisar SIMUS
    print("\n[2] Analisando tabelas do SIMUS.pdf...")
    simus_items = analyze_simus_tables()
    print(f"   {len(simus_items)} linhas com valores encontradas")
    
    # Agrupar valores do SIMUS
    print("\n[3] Agrupando valores do SIMUS...")
    simus_values = []
    for item in simus_items:
        simus_values.extend(item['values'])
    
    unique_simus_values = sorted(set(simus_values), reverse=True)
    print(f"\n   Maiores valores únicos no SIMUS:")
    for val in unique_simus_values[:15]:
        print(f"     R$ {val:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    
    # Procurar o total do SIMUS
    simus_total = Decimal('27644.68')
    print(f"\n   Total esperado SIMUS: R$ {simus_total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    
    # Tentar somar valores do SIMUS
    print("\n[4] Tentando identificar a composição do total SIMUS...")
    
    # Estratégia 1: Somar todos os valores únicos maiores que um threshold
    large_values = [v for v in unique_simus_values if v > Decimal('100')]
    sum_large = sum(large_values)
    print(f"\n   Soma dos valores > R$ 100,00: R$ {sum_large:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    
    # Estratégia 2: Procurar por padrões de soma nas tabelas
    print("\n[5] Procurando linhas que somam próximo ao total...")
    target_total = simus_total
    tolerance = Decimal('0.50')
    
    # Encontrar combinações de valores que somam próximo ao total
    candidates = []
    for item in simus_items:
        if abs(item['sum'] - target_total) < tolerance:
            candidates.append(item)
    
    if candidates:
        print(f"   Encontradas {len(candidates)} linhas que somam próximo ao total:")
        for cand in candidates[:5]:
            print(f"     Página {cand['page']}, Tabela {cand['table']}, Linha {cand['row']}")
            print(f"     Texto: {cand['text'][:100]}...")
            print(f"     Soma: R$ {cand['sum']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    
    # Calcular diferença
    difference = compulab_total - simus_total
    print("\n" + "=" * 100)
    print("RESUMO DA DIFERENÇA:")
    print("=" * 100)
    print(f"COMPULAB Total: R$ {compulab_total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    print(f"SIMUS Total:    R$ {simus_total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    print(f"DIFERENÇA:      R$ {difference:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    print(f"Percentual:     {(difference/simus_total*100):.2f}%")
    
    # Salvar itens do SIMUS para análise manual
    print("\n[6] Salvando detalhes das tabelas SIMUS...")
    with open('simus_detailed_items.txt', 'w', encoding='utf-8') as f:
        f.write("ITENS DETALHADOS DO SIMUS\n")
        f.write("=" * 100 + "\n\n")
        for item in simus_items:
            f.write(f"Página {item['page']}, Tabela {item['table']}, Linha {item['row']}\n")
            f.write(f"Texto: {item['text']}\n")
            f.write(f"Valores: {[str(v) for v in item['values']]}\n")
            f.write(f"Soma: R$ {item['sum']:,.2f}\n".replace(',', 'X').replace('.', ',').replace('X', '.'))
            f.write("-" * 100 + "\n")
    
    print("   Arquivo salvo: simus_detailed_items.txt")
    
    # Procurar valores que podem explicar a diferença
    print("\n[7] Procurando valores que podem explicar a diferença...")
    diff_value = difference
    print(f"   Procurando valores próximos a R$ {diff_value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    
    close_to_diff = []
    for val in unique_simus_values:
        if abs(val - diff_value) < Decimal('100'):
            close_to_diff.append(val)
    
    if close_to_diff:
        print(f"   Valores próximos à diferença encontrados:")
        for val in close_to_diff:
            print(f"     R$ {val:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    
    # Verificar se há valores no COMPULAB que não estão no SIMUS
    print("\n[8] Verificando valores exclusivos...")
    compulab_values_set = set(compulab['values'])
    simus_values_set = set(simus_values)
    
    only_compulab = compulab_values_set - simus_values_set
    only_simus = simus_values_set - compulab_values_set
    
    print(f"   Valores APENAS no COMPULAB: {len(only_compulab)}")
    for val in sorted(only_compulab, reverse=True):
        print(f"     R$ {val:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    
    print(f"\n   Valores APENAS no SIMUS (maiores): {len([v for v in only_simus if v > Decimal('1000')])}")
    for val in sorted([v for v in only_simus if v > Decimal('1000')], reverse=True)[:10]:
        print(f"     R$ {val:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    
    print("\n" + "=" * 100)
    print("Análise detalhada concluída!")
    print("=" * 100)

if __name__ == '__main__':
    main()

