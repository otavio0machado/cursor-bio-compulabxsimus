import re
import pdfplumber
from decimal import Decimal
from collections import defaultdict

def extract_currency_value(text):
    """Extrai valores em formato brasileiro (R$ X.XXX,XX)"""
    # Padrão para valores em reais: R$ seguido de números, pontos e vírgula
    pattern = r'R\$\s*([\d.]+,\d{2})'
    matches = re.findall(pattern, text)
    values = []
    for match in matches:
        # Remove pontos e substitui vírgula por ponto para converter
        value_str = match.replace('.', '').replace(',', '.')
        try:
            values.append(Decimal(value_str))
        except:
            pass
    return values

def extract_all_data_from_pdf(pdf_path):
    """Extrai todo o texto e valores de um PDF"""
    data = {
        'text': '',
        'currency_values': [],
        'lines': []
    }
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    data['text'] += text + '\n'
                    data['lines'].extend(text.split('\n'))
                    # Extrai valores de moeda desta página
                    currency_vals = extract_currency_value(text)
                    data['currency_values'].extend(currency_vals)
    except Exception as e:
        print(f"Erro ao processar {pdf_path}: {e}")
    
    return data

def find_total_value(text, lines):
    """Tenta encontrar o valor total no texto"""
    # Procurar por padrões comuns de "total"
    patterns = [
        r'(?i)total[:\s]*R\$\s*([\d.]+,\d{2})',
        r'(?i)valor\s+total[:\s]*R\$\s*([\d.]+,\d{2})',
        r'(?i)total\s+geral[:\s]*R\$\s*([\d.]+,\d{2})',
        r'R\$\s*([\d.]+,\d{2})',  # Todos os valores
    ]
    
    totals = []
    for pattern in patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            value_str = match.group(1) if match.groups() else match.group(0).replace('R$', '').strip()
            value_str = value_str.replace('.', '').replace(',', '.')
            try:
                totals.append(Decimal(value_str))
            except:
                pass
    
    return totals

def extract_table_data(pdf_path):
    """Tenta extrair dados de tabelas do PDF"""
    tables_data = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                tables = page.extract_tables()
                if tables:
                    for table in tables:
                        tables_data.append({
                            'page': page_num + 1,
                            'table': table
                        })
    except Exception as e:
        print(f"Erro ao extrair tabelas de {pdf_path}: {e}")
    
    return tables_data

def main():
    print("=" * 80)
    print("ANÁLISE DE DIFERENÇA ENTRE PDFs COMPULAB E SIMUS")
    print("=" * 80)
    
    # Valores conhecidos
    compulab_total = Decimal('30872.24')
    simus_total = Decimal('27644.68')
    difference = compulab_total - simus_total
    
    print(f"\nValores conhecidos:")
    print(f"COMPULAB: R$ {compulab_total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    print(f"SIMUS: R$ {simus_total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    print(f"Diferença: R$ {difference:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    print("\n" + "=" * 80)
    
    # Extrair dados dos PDFs
    print("\nExtraindo dados do COMPULAB.pdf...")
    compulab_data = extract_all_data_from_pdf('COMPULAB.pdf')
    
    print("\nExtraindo dados do SIMUS.pdf...")
    simus_data = extract_all_data_from_pdf('SIMUS.pdf')
    
    # Encontrar valores totais
    print("\n" + "=" * 80)
    print("VALORES ENCONTRADOS NOS PDFs:")
    print("=" * 80)
    
    compulab_totals = find_total_value(compulab_data['text'], compulab_data['lines'])
    simus_totals = find_total_value(simus_data['text'], simus_data['lines'])
    
    print(f"\nCOMPULAB - Todos os valores encontrados:")
    unique_compulab = sorted(set(compulab_data['currency_values']), reverse=True)
    for val in unique_compulab[:20]:  # Mostrar os 20 maiores
        print(f"  R$ {val:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    
    print(f"\nSIMUS - Todos os valores encontrados:")
    unique_simus = sorted(set(simus_data['currency_values']), reverse=True)
    for val in unique_simus[:20]:  # Mostrar os 20 maiores
        print(f"  R$ {val:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    
    # Extrair tabelas
    print("\n" + "=" * 80)
    print("EXTRAINDO DADOS DE TABELAS:")
    print("=" * 80)
    
    compulab_tables = extract_table_data('COMPULAB.pdf')
    simus_tables = extract_table_data('SIMUS.pdf')
    
    print(f"\nCOMPULAB: {len(compulab_tables)} tabela(s) encontrada(s)")
    print(f"SIMUS: {len(simus_tables)} tabela(s) encontrada(s)")
    
    # Salvar dados extraídos para análise detalhada
    print("\n" + "=" * 80)
    print("SALVANDO DADOS EXTRAÍDOS PARA ANÁLISE:")
    print("=" * 80)
    
    with open('compulab_extracted.txt', 'w', encoding='utf-8') as f:
        f.write("=== TEXTO COMPLETO COMPULAB ===\n\n")
        f.write(compulab_data['text'])
        f.write("\n\n=== VALORES ENCONTRADOS ===\n")
        for val in sorted(set(compulab_data['currency_values']), reverse=True):
            f.write(f"R$ {val:,.2f}\n".replace(',', 'X').replace('.', ',').replace('X', '.'))
    
    with open('simus_extracted.txt', 'w', encoding='utf-8') as f:
        f.write("=== TEXTO COMPLETO SIMUS ===\n\n")
        f.write(simus_data['text'])
        f.write("\n\n=== VALORES ENCONTRADOS ===\n")
        for val in sorted(set(simus_data['currency_values']), reverse=True):
            f.write(f"R$ {val:,.2f}\n".replace(',', 'X').replace('.', ',').replace('X', '.'))
    
    print("\nArquivos salvos:")
    print("  - compulab_extracted.txt")
    print("  - simus_extracted.txt")
    
    # Análise comparativa
    print("\n" + "=" * 80)
    print("ANÁLISE COMPARATIVA:")
    print("=" * 80)
    
    # Procurar valores que estão em um mas não no outro
    compulab_set = set(compulab_data['currency_values'])
    simus_set = set(simus_data['currency_values'])
    
    only_compulab = compulab_set - simus_set
    only_simus = simus_set - compulab_set
    
    print(f"\nValores APENAS no COMPULAB:")
    for val in sorted(only_compulab, reverse=True)[:10]:
        print(f"  R$ {val:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    
    print(f"\nValores APENAS no SIMUS:")
    for val in sorted(only_simus, reverse=True)[:10]:
        print(f"  R$ {val:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    
    print("\n" + "=" * 80)
    print("Análise concluída! Verifique os arquivos de texto para mais detalhes.")
    print("=" * 80)

if __name__ == '__main__':
    main()

