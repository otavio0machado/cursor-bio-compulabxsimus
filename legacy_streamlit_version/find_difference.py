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

def find_total_context(pdf_path, target_total):
    """Encontra o contexto onde o total aparece no PDF"""
    contexts = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text()
            if not text:
                continue
            
            # Procura pelo valor total no texto
            lines = text.split('\n')
            for i, line in enumerate(lines):
                if str(target_total).replace('.', ',') in line or f"R$ {target_total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.') in line:
                    # Pega contexto antes e depois
                    start = max(0, i - 5)
                    end = min(len(lines), i + 5)
                    context = '\n'.join(lines[start:end])
                    contexts.append({
                        'page': page_num + 1,
                        'line': i + 1,
                        'context': context,
                        'full_text': text
                    })
    
    return contexts

def analyze_simus_structure():
    """Analisa a estrutura do SIMUS para encontrar como o total é calculado"""
    print("\n[ANÁLISE ESTRUTURAL DO SIMUS]")
    print("=" * 100)
    
    # Valores conhecidos
    simus_total = Decimal('27644.68')
    compulab_total = Decimal('30872.24')
    difference = compulab_total - simus_total
    
    # Encontrar onde o total aparece
    print("\n1. Procurando onde o total R$ 27.644,68 aparece no SIMUS...")
    simus_contexts = find_total_context('SIMUS.pdf', simus_total)
    
    if simus_contexts:
        print(f"   Encontrado em {len(simus_contexts)} local(is):")
        for ctx in simus_contexts[:3]:  # Mostrar os 3 primeiros
            print(f"\n   Página {ctx['page']}, Linha {ctx['line']}:")
            print("   " + "-" * 96)
            for line in ctx['context'].split('\n'):
                print(f"   {line}")
            print("   " + "-" * 96)
    else:
        print("   Total não encontrado diretamente no texto. Procurando em tabelas...")
    
    # Analisar primeiras páginas do SIMUS (onde geralmente está o resumo)
    print("\n2. Analisando primeiras páginas do SIMUS (resumo/índice)...")
    with pdfplumber.open('SIMUS.pdf') as pdf:
        for page_num in range(min(5, len(pdf.pages))):
            page = pdf.pages[page_num]
            text = page.extract_text()
            if text:
                # Procurar por palavras-chave relacionadas a total, resumo, etc.
                keywords = ['total', 'resumo', 'valor', 'soma', 'geral']
                lines = text.split('\n')
                relevant_lines = []
                for line in lines:
                    line_lower = line.lower()
                    if any(kw in line_lower for kw in keywords):
                        relevant_lines.append(line)
                
                if relevant_lines:
                    print(f"\n   Página {page_num + 1} - Linhas relevantes:")
                    for line in relevant_lines[:10]:
                        print(f"     {line}")
    
    # Analisar tabelas das primeiras páginas
    print("\n3. Analisando tabelas das primeiras páginas do SIMUS...")
    with pdfplumber.open('SIMUS.pdf') as pdf:
        for page_num in range(min(10, len(pdf.pages))):
            page = pdf.pages[page_num]
            tables = page.extract_tables()
            if tables:
                print(f"\n   Página {page_num + 1} - {len(tables)} tabela(s):")
                for table_idx, table in enumerate(tables):
                    # Procurar por linhas que contenham o total
                    for row in table:
                        row_text = ' '.join([str(cell) if cell else '' for cell in row])
                        if str(simus_total).replace('.', ',') in row_text or '27.644' in row_text:
                            print(f"     Tabela {table_idx + 1} - Linha com total encontrada:")
                            for cell in row:
                                if cell:
                                    print(f"       {cell}")
    
    return simus_contexts

def analyze_compulab_structure():
    """Analisa a estrutura do COMPULAB"""
    print("\n[ANÁLISE ESTRUTURAL DO COMPULAB]")
    print("=" * 100)
    
    compulab_total = Decimal('30872.24')
    
    print("\n1. Procurando onde o total R$ 30.872,24 aparece no COMPULAB...")
    compulab_contexts = find_total_context('COMPULAB.pdf', compulab_total)
    
    if compulab_contexts:
        print(f"   Encontrado em {len(compulab_contexts)} local(is):")
        for ctx in compulab_contexts[:3]:
            print(f"\n   Página {ctx['page']}, Linha {ctx['line']}:")
            print("   " + "-" * 96)
            for line in ctx['context'].split('\n'):
                print(f"   {line}")
            print("   " + "-" * 96)
    
    # Extrair todo o texto do COMPULAB
    print("\n2. Extraindo todo o conteúdo do COMPULAB...")
    full_text = ''
    with pdfplumber.open('COMPULAB.pdf') as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text + '\n'
    
    # Procurar por valores que podem compor o total
    all_values = extract_currency_value(full_text)
    unique_values = sorted(set(all_values), reverse=True)
    
    print(f"\n   Todos os valores encontrados no COMPULAB:")
    for val in unique_values[:20]:
        print(f"     R$ {val:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    
    return compulab_contexts, full_text

def find_items_around_difference():
    """Procura por itens no SIMUS que podem explicar a diferença"""
    print("\n[PROCURANDO ITENS QUE EXPLICAM A DIFERENÇA]")
    print("=" * 100)
    
    difference = Decimal('3227.56')
    
    print(f"\nProcurando valores próximos a R$ {difference:,.2f} (a diferença)...".replace(',', 'X').replace('.', ',').replace('X', '.'))
    
    items_near_diff = []
    
    with pdfplumber.open('SIMUS.pdf') as pdf:
        for page_num, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            for table_idx, table in enumerate(tables):
                for row_idx, row in enumerate(table):
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
                    
                    # Verifica se algum valor está próximo da diferença
                    for val in row_values:
                        if abs(val - difference) < Decimal('10'):
                            items_near_diff.append({
                                'page': page_num + 1,
                                'table': table_idx + 1,
                                'row': row_idx + 1,
                                'text': ' | '.join(row_text),
                                'value': val,
                                'diff_from_target': abs(val - difference)
                            })
    
    if items_near_diff:
        print(f"\n   Encontrados {len(items_near_diff)} itens próximos à diferença:")
        # Ordenar por proximidade
        items_near_diff.sort(key=lambda x: x['diff_from_target'])
        for item in items_near_diff[:10]:
            print(f"\n   Página {item['page']}, Tabela {item['table']}, Linha {item['row']}")
            print(f"   Valor: R$ {item['value']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
            print(f"   Diferença do alvo: R$ {item['diff_from_target']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
            print(f"   Texto: {item['text'][:150]}...")
    
    return items_near_diff

def main():
    print("=" * 100)
    print("ANÁLISE COMPARATIVA DETALHADA - COMPULAB vs SIMUS")
    print("=" * 100)
    
    compulab_total = Decimal('30872.24')
    simus_total = Decimal('27644.68')
    difference = compulab_total - simus_total
    
    print(f"\nOBJETIVO: Entender por que há diferença de R$ {difference:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    print(f"COMPULAB: R$ {compulab_total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    print(f"SIMUS:    R$ {simus_total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    
    # Analisar estruturas
    simus_contexts = analyze_simus_structure()
    compulab_contexts, compulab_text = analyze_compulab_structure()
    
    # Procurar itens que explicam a diferença
    items_near_diff = find_items_around_difference()
    
    # Salvar relatório
    print("\n" + "=" * 100)
    print("GERANDO RELATÓRIO DETALHADO...")
    print("=" * 100)
    
    with open('relatorio_diferenca.txt', 'w', encoding='utf-8') as f:
        f.write("RELATÓRIO DE ANÁLISE - DIFERENÇA ENTRE COMPULAB E SIMUS\n")
        f.write("=" * 100 + "\n\n")
        f.write(f"COMPULAB Total: R$ {compulab_total:,.2f}\n".replace(',', 'X').replace('.', ',').replace('X', '.'))
        f.write(f"SIMUS Total:    R$ {simus_total:,.2f}\n".replace(',', 'X').replace('.', ',').replace('X', '.'))
        f.write(f"DIFERENÇA:      R$ {difference:,.2f}\n\n".replace(',', 'X').replace('.', ',').replace('X', '.'))
        
        f.write("\n[CONTEXTO DO TOTAL NO SIMUS]\n")
        f.write("-" * 100 + "\n")
        for ctx in simus_contexts:
            f.write(f"\nPágina {ctx['page']}, Linha {ctx['line']}:\n")
            f.write(ctx['context'] + "\n")
        
        f.write("\n[CONTEXTO DO TOTAL NO COMPULAB]\n")
        f.write("-" * 100 + "\n")
        for ctx in compulab_contexts:
            f.write(f"\nPágina {ctx['page']}, Linha {ctx['line']}:\n")
            f.write(ctx['context'] + "\n")
        
        f.write("\n[ITENS PRÓXIMOS À DIFERENÇA]\n")
        f.write("-" * 100 + "\n")
        for item in items_near_diff[:20]:
            f.write(f"\nPágina {item['page']}, Tabela {item['table']}, Linha {item['row']}\n")
            f.write(f"Valor: R$ {item['value']:,.2f}\n".replace(',', 'X').replace('.', ',').replace('X', '.'))
            f.write(f"Texto: {item['text']}\n")
    
    print("\n   Relatório salvo em: relatorio_diferenca.txt")
    print("\n" + "=" * 100)
    print("Análise concluída!")
    print("=" * 100)

if __name__ == '__main__':
    main()

