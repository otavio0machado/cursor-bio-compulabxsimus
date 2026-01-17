# 📊 Biodiagnóstico - Sistema de Administração (Versão Oficial)

**NOVA VERSÃO:** Este projeto agora utiliza **Reflex (React + Tailwind)** para uma interface moderna e responsiva.

A versão antiga (Streamlit) foi descontinuada e movida para `legacy_streamlit_version/`.


Aplicativo web para análise comparativa mensal de faturamento entre o sistema COMPULAB (Laboratório Biodiagnóstico) e o SIMUS.

## 🚀 Funcionalidades

- **Upload de PDFs**: Interface simples para fazer upload dos PDFs do COMPULAB e SIMUS
- **Análise por Paciente**: Extração e comparação de dados por paciente
- **Identificação de Divergências**:
  - ✅ Pacientes faltantes no SIMUS (presentes no COMPULAB mas não no SIMUS)
  - ✅ Exames não cadastrados (por paciente)
  - ✅ Divergências de valores (por paciente e exame)
- **Visualizações**: Gráficos interativos para análise visual
- **Relatórios Detalhados**: Geração de relatórios completos em texto e CSV

## 📋 Requisitos

- Python 3.8 ou superior
- Bibliotecas Python (ver `requirements.txt`)

## 🔧 Instalação

1. Clone ou baixe este repositório

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

## 🎯 Como Usar
 
 1. Inicie o aplicativo:
 ```bash
 ./run_app.bat
 ```
 
 Ou manualmente:
 ```bash
 cd biodiagnostico_app
 reflex run
 ```

2. O aplicativo abrirá automaticamente no seu navegador (geralmente em `http://localhost:8501`)

3. Na barra lateral:
   - Faça upload do arquivo **COMPULAB.pdf**
   - Faça upload do arquivo **SIMUS.pdf**
   - Clique no botão **"Analisar"**

4. Visualize os resultados:
   - **Visão Geral**: Gráficos e estatísticas gerais
   - **Códigos Exclusivos**: Exames presentes apenas no COMPULAB
   - **Comparação de Códigos**: Diferenças de valores para códigos comuns
   - **Relatório**: Relatório completo para download

## 📊 O que o App Analisa

### Análise por Paciente

#### 1. Pacientes Faltantes no SIMUS
- Lista todos os pacientes que estão no COMPULAB mas não aparecem no SIMUS
- Mostra quantos exames cada paciente tem
- Calcula o valor total de cada paciente faltante
- Detalha todos os exames de cada paciente faltante

#### 2. Exames Faltantes
- Identifica exames que estão no COMPULAB mas não foram cadastrados no SIMUS
- Agrupa por paciente para facilitar a identificação
- Mostra o valor de cada exame faltante

#### 3. Divergências de Valores
- Compara valores de exames comuns entre COMPULAB e SIMUS
- Identifica quando o mesmo exame tem valores diferentes
- Mostra a diferença de valor por paciente e exame
- Gera gráficos das maiores divergências

### Valores Totais
- Total do COMPULAB
- Total do SIMUS (Contratualizado)
- Diferença entre os valores
- Quantidade de pacientes em cada sistema

## 📁 Estrutura de Arquivos

```
.
├── app.py                 # Aplicativo principal Streamlit
├── requirements.txt        # Dependências Python
├── README.md              # Este arquivo
├── COMPULAB.pdf           # PDF do COMPULAB (exemplo)
└── SIMUS.pdf              # PDF do SIMUS (exemplo)
```

## 🔍 Exemplo de Análise

O aplicativo identifica:
- **Diferença total** entre COMPULAB e SIMUS
- **Códigos exclusivos** que explicam parte da diferença
- **Diferenças de valores** nos códigos comuns
- **Gráficos visuais** para facilitar a compreensão

## 📝 Notas

- Os PDFs devem estar no formato correto (COMPULAB e SIMUS padrão)
- A análise é feita em tempo real após o upload
- Os relatórios podem ser baixados em formato TXT e CSV

## 🛠️ Tecnologias Utilizadas

- **Streamlit**: Framework para aplicativos web em Python
- **pdfplumber**: Extração de dados de PDFs
- **pandas**: Manipulação de dados
- **plotly**: Gráficos interativos

## 📞 Suporte

Para dúvidas ou problemas, verifique:
1. Se os PDFs estão no formato correto
2. Se todas as dependências foram instaladas
3. Se o Python está na versão 3.8 ou superior

---

**Desenvolvido para análise mensal de faturamento do Laboratório Biodiagnóstico**

