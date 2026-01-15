# 🚀 Guia Rápido - Análise de Faturamento

## Início Rápido

### 1. Instalar Dependências

**Windows (recomendado):**
```bash
py -m pip install -r requirements.txt
```

**Ou:**
```bash
python -m pip install -r requirements.txt
```

### 2. Iniciar o Aplicativo

**Windows (mais fácil):**
- Clique duas vezes no arquivo `run_app.bat`

**Ou via linha de comando:**
```bash
py -m streamlit run app.py
```

**Se não funcionar, tente:**
```bash
python -m streamlit run app.py
```

**Linux/Mac:**
```bash
chmod +x run_app.sh
./run_app.sh
```

### 3. Usar o Aplicativo

1. O navegador abrirá automaticamente em `http://localhost:8501`
2. Na barra lateral esquerda:
   - Clique em "Browse files" no campo **COMPULAB.pdf**
   - Selecione o arquivo PDF do COMPULAB
   - Clique em "Browse files" no campo **SIMUS.pdf**
   - Selecione o arquivo PDF do SIMUS
   - Clique no botão **"🔍 Analisar"**

3. Aguarde o processamento (alguns segundos)

4. Visualize os resultados nas abas:
   - **📊 Visão Geral**: Gráficos e estatísticas
   - **🔴 Códigos Exclusivos**: Exames só no COMPULAB
   - **⚖️ Comparação de Códigos**: Diferenças de valores
   - **📄 Relatório**: Relatório completo para download

## 📊 Entendendo os Resultados

### Resumo
- **COMPULAB Total**: Valor total extraído do PDF do COMPULAB
- **SIMUS Contratualizado**: Valor total do SIMUS (usado para comparação)
- **Diferença**: Quanto o COMPULAB tem a mais que o SIMUS

### Códigos Exclusivos
Mostra os códigos de exames que estão no COMPULAB mas não no SIMUS, com seus valores totais.

### Comparação de Códigos
Mostra os códigos que aparecem em ambos os sistemas, mas com valores diferentes. Isso ajuda a identificar onde estão as diferenças.

## 💡 Dicas

- Use os gráficos interativos para explorar os dados
- Baixe os relatórios para análise posterior
- Compare mensalmente para identificar tendências
- Os dados são processados apenas na sua máquina (privacidade garantida)

## ❓ Problemas Comuns

**Erro ao processar PDFs:**
- Verifique se os PDFs estão no formato correto
- Certifique-se de que são os PDFs do COMPULAB e SIMUS

**App não inicia:**
- Verifique se todas as dependências foram instaladas: `py -m pip install -r requirements.txt`
- Certifique-se de que o Python está na versão 3.8 ou superior
- Use `py -m streamlit` ao invés de apenas `streamlit`
- Execute primeiro `testar_instalacao.bat` para verificar se tudo está OK

**Gráficos não aparecem:**
- Aguarde alguns segundos para o processamento
- Recarregue a página se necessário

---

**Boa análise! 📊**

