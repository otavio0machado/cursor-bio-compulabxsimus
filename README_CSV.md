# 📊 Exportação e Análise via CSV

## 🎯 Como Usar

### Passo 1: Exportar PDFs para CSV

Execute o script de exportação:

```bash
python export_to_csv.py COMPULAB.pdf SIMUS.pdf
```

Isso irá gerar:
- `compulab_data.csv` - Dados do COMPULAB em formato CSV
- `simus_data.csv` - Dados do SIMUS em formato CSV

### Passo 2: Analisar os CSVs no App

1. Abra o app Streamlit:
   ```bash
   streamlit run app.py
   ```

2. Na barra lateral:
   - Selecione **"CSV"** como tipo de arquivo
   - Faça upload de `compulab_data.csv`
   - Faça upload de `simus_data.csv`
   - Clique em **"Analisar"**

## ✅ Vantagens de Usar CSV

- **⚡ Mais rápido**: Não precisa processar PDFs toda vez
- **💾 Reutilizável**: Use os mesmos CSVs para múltiplas análises
- **📊 Editável**: Você pode corrigir dados manualmente no CSV se necessário
- **🔄 Versionável**: Fácil de comparar diferentes meses

## 📋 Formato do CSV

Os CSVs gerados têm a seguinte estrutura:

```csv
Paciente;Nome_Exame;Codigo_Exame;Valor
JOAO SILVA;VITAMINA B12;0202010708;22,84
JOAO SILVA;TIREOTROFINA TSH;0202060250;13,42
...
```

### Colunas:
- **Paciente**: Nome do paciente (normalizado)
- **Nome_Exame**: Nome do exame (normalizado)
- **Codigo_Exame**: Código do exame (10 dígitos)
- **Valor**: Valor do exame (formato brasileiro: 123,45)

## 🔄 Fluxo Completo

```
PDFs → export_to_csv.py → CSVs → app.py → Análise
```

1. **Primeira vez**: Exporte os PDFs para CSV
2. **Análises seguintes**: Use diretamente os CSVs no app (muito mais rápido!)

## 📝 Notas

- Os nomes são **normalizados** (sem acentos, espaços extras) para facilitar a comparação
- Os valores são mantidos no formato brasileiro (vírgula como decimal)
- O separador do CSV é `;` (ponto e vírgula) para compatibilidade com Excel

---

**Boa análise! 📊**


