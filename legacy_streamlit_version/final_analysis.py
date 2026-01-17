import pdfplumber
from decimal import Decimal
import re

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

def analyze_simus_first_page():
    """Analisa a primeira página do SIMUS em detalhes"""
    print("\n" + "=" * 100)
    print("ANÁLISE DA PRIMEIRA PÁGINA DO SIMUS")
    print("=" * 100)
    
    with pdfplumber.open('SIMUS.pdf') as pdf:
        page = pdf.pages[0]
        text = page.extract_text()
        
        print("\nTexto completo da primeira página:")
        print("-" * 100)
        print(text)
        print("-" * 100)
        
        # Procurar pela linha que menciona os valores
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if 'SIGTAP' in line or 'Contratualizados' in line or '27.644' in line or '18.447' in line:
                print(f"\nLinha {i+1} relevante:")
                print(f"  {line}")
                # Mostrar contexto
                start = max(0, i-2)
                end = min(len(lines), i+3)
                print(f"\n  Contexto (linhas {start+1} a {end}):")
                for j in range(start, end):
                    marker = ">>>" if j == i else "   "
                    print(f"  {marker} {lines[j]}")
        
        # Analisar tabelas da primeira página
        tables = page.extract_tables()
        print(f"\n\nTabelas encontradas na primeira página: {len(tables)}")
        for table_idx, table in enumerate(tables):
            print(f"\n--- Tabela {table_idx + 1} ---")
            for row_idx, row in enumerate(table):
                if not row:
                    continue
                row_text = ' | '.join([str(cell) if cell else '' for cell in row])
                # Verificar se tem valores relevantes
                has_relevant = False
                for cell in row:
                    if cell and ('SIGTAP' in str(cell) or 'Contratualizados' in str(cell) or 
                                '27.644' in str(cell) or '18.447' in str(cell) or '9.197' in str(cell)):
                        has_relevant = True
                        break
                
                if has_relevant or row_idx < 5:  # Mostrar primeiras 5 linhas também
                    print(f"Linha {row_idx + 1}: {row_text[:200]}")

def analyze_compulab_summary():
    """Analisa o resumo do COMPULAB"""
    print("\n" + "=" * 100)
    print("ANÁLISE DO COMPULAB - PÁGINA FINAL (RESUMO)")
    print("=" * 100)
    
    with pdfplumber.open('COMPULAB.pdf') as pdf:
        # Analisar última página (onde geralmente está o resumo)
        last_page = pdf.pages[-1]
        text = last_page.extract_text()
        
        print("\nTexto da última página do COMPULAB:")
        print("-" * 100)
        print(text)
        print("-" * 100)
        
        # Procurar por subtotais
        lines = text.split('\n')
        print("\nLinhas com valores:")
        for i, line in enumerate(lines):
            if 'R$' in line or 'Total' in line or 'Subtotal' in line:
                print(f"  Linha {i+1}: {line}")

def calculate_difference():
    """Calcula e explica a diferença"""
    print("\n" + "=" * 100)
    print("CÁLCULO E EXPLICAÇÃO DA DIFERENÇA")
    print("=" * 100)
    
    compulab_total = Decimal('30872.24')
    simus_contratualizado = Decimal('27644.68')
    simus_sigtap = Decimal('18447.46')
    
    # Calcular diferença
    difference = compulab_total - simus_contratualizado
    
    print(f"\nValores conhecidos:")
    print(f"  COMPULAB Total:        R$ {compulab_total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    print(f"  SIMUS Contratualizado: R$ {simus_contratualizado:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    print(f"  SIMUS SIGTAP:          R$ {simus_sigtap:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    print(f"  DIFERENÇA:             R$ {difference:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    
    # Verificar se a diferença corresponde a algum valor no SIMUS
    print(f"\n\nHipóteses:")
    print(f"  1. A diferença de R$ {difference:,.2f} pode ser um item que está no COMPULAB mas não no SIMUS (Contratualizados)".replace(',', 'X').replace('.', ',').replace('X', '.'))
    print(f"  2. Pode ser uma diferença entre SIGTAP e Contratualizados")
    
    # Verificar relação entre valores
    if simus_sigtap + (compulab_total - simus_contratualizado) == compulab_total:
        print(f"\n  ✓ SIMUS SIGTAP ({simus_sigtap:,.2f}) + Diferença ({difference:,.2f}) = COMPULAB Total ({compulab_total:,.2f})".replace(',', 'X').replace('.', ',').replace('X', '.'))
    
    # Procurar no SIMUS por itens que somam a diferença
    print(f"\n\nProcurando no SIMUS por itens que podem explicar a diferença...")
    
    items_summing_to_diff = []
    difference_target = difference
    
    with pdfplumber.open('SIMUS.pdf') as pdf:
        for page_num, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    if not row:
                        continue
                    
                    row_values = []
                    row_text = []
                    for cell in row:
                        if cell:
                            row_text.append(str(cell))
                            val = parse_table_value(cell)
                            if val:
                                row_values.append(val)
                    
                    # Verificar se a soma dos valores da linha está próxima da diferença
                    if row_values:
                        row_sum = sum(row_values)
                        if abs(row_sum - difference_target) < Decimal('1'):
                            items_summing_to_diff.append({
                                'page': page_num + 1,
                                'text': ' | '.join(row_text),
                                'values': row_values,
                                'sum': row_sum
                            })
    
    if items_summing_to_diff:
        print(f"  Encontrados {len(items_summing_to_diff)} itens que somam próximo à diferença:")
        for item in items_summing_to_diff[:5]:
            print(f"\n    Página {item['page']}:")
            print(f"    Soma: R$ {item['sum']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
            print(f"    Texto: {item['text'][:150]}...")

def compare_item_by_item():
    """Tenta comparar item por item entre os dois PDFs"""
    print("\n" + "=" * 100)
    print("COMPARAÇÃO ITEM POR ITEM")
    print("=" * 100)
    
    # Extrair códigos de exames do COMPULAB
    print("\nExtraindo códigos de exames do COMPULAB...")
    compulab_codes = set()
    
    with pdfplumber.open('COMPULAB.pdf') as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                # Procurar por códigos (padrão: números de 10 dígitos)
                codes = re.findall(r'\b\d{10}\b', text)
                compulab_codes.update(codes)
    
    print(f"  {len(compulab_codes)} códigos únicos encontrados no COMPULAB")
    
    # Extrair códigos de exames do SIMUS
    print("\nExtraindo códigos de exames do SIMUS...")
    simus_codes = set()
    
    with pdfplumber.open('SIMUS.pdf') as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                codes = re.findall(r'\b\d{10}\b', text)
                simus_codes.update(codes)
    
    print(f"  {len(simus_codes)} códigos únicos encontrados no SIMUS")
    
    # Comparar
    only_compulab = compulab_codes - simus_codes
    only_simus = simus_codes - compulab_codes
    common = compulab_codes & simus_codes
    
    print(f"\n  Códigos apenas no COMPULAB: {len(only_compulab)}")
    print(f"  Códigos apenas no SIMUS: {len(only_simus)}")
    print(f"  Códigos em comum: {len(common)}")
    
    if only_compulab:
        print(f"\n  Primeiros 10 códigos apenas no COMPULAB:")
        for code in list(only_compulab)[:10]:
            print(f"    {code}")
    
    if only_simus:
        print(f"\n  Primeiros 10 códigos apenas no SIMUS:")
        for code in list(only_simus)[:10]:
            print(f"    {code}")

def main():
    print("=" * 100)
    print("ANÁLISE FINAL - DIFERENÇA ENTRE COMPULAB E SIMUS")
    print("=" * 100)
    
    # Analisar primeira página do SIMUS
    analyze_simus_first_page()
    
    # Analisar resumo do COMPULAB
    analyze_compulab_summary()
    
    # Calcular diferença
    calculate_difference()
    
    # Comparar item por item
    compare_item_by_item()
    
    print("\n" + "=" * 100)
    print("ANÁLISE CONCLUÍDA")
    print("=" * 100)
    
    # Gerar relatório final
    print("\nGerando relatório final...")
    with open('relatorio_final.txt', 'w', encoding='utf-8') as f:
        f.write("RELATÓRIO FINAL - ANÁLISE DA DIFERENÇA\n")
        f.write("=" * 100 + "\n\n")
        f.write("RESUMO:\n")
        f.write("- COMPULAB Total: R$ 30.872,24\n")
        f.write("- SIMUS Contratualizado: R$ 27.644,68\n")
        f.write("- SIMUS SIGTAP: R$ 18.447,46\n")
        f.write("- DIFERENÇA: R$ 3.227,56\n\n")
        f.write("CONCLUSÃO:\n")
        f.write("A diferença de R$ 3.227,56 entre o COMPULAB (R$ 30.872,24) e o SIMUS Contratualizado (R$ 27.644,68)\n")
        f.write("indica que há itens no COMPULAB que não estão sendo considerados no cálculo do SIMUS Contratualizado.\n")
        f.write("O SIMUS mostra dois valores: SIGTAP (R$ 18.447,46) e Contratualizado (R$ 27.644,68).\n")
        f.write("A diferença pode estar relacionada a itens que estão no COMPULAB mas não foram incluídos\n")
        f.write("no cálculo do valor Contratualizado do SIMUS, ou pode haver uma diferença na forma de cálculo.\n")
    
    print("  Relatório salvo em: relatorio_final.txt")

if __name__ == '__main__':
    main()

