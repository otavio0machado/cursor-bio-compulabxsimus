# 📋 Guia de Análise por Paciente

## 🎯 Objetivo

Este aplicativo foi desenvolvido para fazer análise mensal de faturamento comparando os dados do **COMPULAB** (Laboratório Biodiagnóstico) com o **SIMUS**, identificando:

1. **Pacientes faltantes** no SIMUS
2. **Exames não cadastrados** no SIMUS
3. **Divergências de valores** entre os sistemas

---

## 📊 Como Funciona a Análise

### 1. Extração de Dados

O aplicativo extrai automaticamente:
- **Nomes dos pacientes** de ambos os PDFs
- **Códigos dos exames** realizados por cada paciente
- **Valores** de cada exame
- **Totais** por paciente e geral

### 2. Comparação

O sistema compara:
- ✅ Quais pacientes do COMPULAB estão no SIMUS
- ✅ Quais exames de cada paciente estão cadastrados no SIMUS
- ✅ Se os valores dos exames são iguais em ambos os sistemas

### 3. Identificação de Problemas

O aplicativo identifica automaticamente:

#### 🔴 Pacientes Faltantes
- Pacientes que aparecem no COMPULAB mas não no SIMUS
- Lista todos os exames desses pacientes
- Calcula o valor total que está faltando

#### ⚠️ Exames Faltantes
- Exames que estão no COMPULAB mas não foram cadastrados no SIMUS
- Agrupados por paciente para facilitar a correção
- Mostra o valor de cada exame faltante

#### 💰 Divergências de Valores
- Quando o mesmo exame tem valores diferentes nos dois sistemas
- Mostra o valor em cada sistema e a diferença
- Identifica em qual paciente ocorreu a divergência

---

## 📈 Interpretando os Resultados

### Resumo da Análise

No topo da página, você verá:
- **COMPULAB Total**: Valor total do faturamento no COMPULAB
- **SIMUS Contratualizado**: Valor total no SIMUS
- **Diferença**: Quanto está faltando ou sobrando
- **Pacientes Faltantes**: Quantos pacientes não estão no SIMUS

### Aba: Pacientes Faltantes

Mostra:
- Lista de pacientes que estão no COMPULAB mas não no SIMUS
- Quantidade de exames de cada paciente
- Valor total de cada paciente
- Detalhamento completo de todos os exames

**Ação necessária**: Verificar por que esses pacientes não foram cadastrados no SIMUS

### Aba: Exames Faltantes

Mostra:
- Exames que estão no COMPULAB mas não no SIMUS
- Agrupados por paciente
- Valor de cada exame faltante

**Ação necessária**: Cadastrar os exames faltantes no SIMUS para os pacientes indicados

### Aba: Divergências de Valores

Mostra:
- Exames que têm valores diferentes entre os sistemas
- Valor no COMPULAB vs valor no SIMUS
- Diferença calculada
- Gráfico das maiores divergências

**Ação necessária**: Verificar e corrigir os valores divergentes no SIMUS

### Aba: Relatório Completo

Contém:
- Resumo geral da análise
- Lista completa de pacientes faltantes
- Lista completa de exames faltantes
- Lista completa de divergências de valores
- Opção de download em TXT e CSV

---

## 💡 Dicas de Uso

### Para Análise Mensal

1. **Faça upload dos PDFs** do mês que deseja analisar
2. **Clique em "Analisar"** e aguarde o processamento
3. **Revise cada aba** para identificar problemas
4. **Baixe o relatório** para documentação
5. **Corrija os problemas** identificados no SIMUS

### Interpretando os Valores

- **Diferença positiva**: COMPULAB tem mais que SIMUS (valores faltando no SIMUS)
- **Diferença negativa**: SIMUS tem mais que COMPULAB (valores extras no SIMUS)
- **Pacientes faltantes**: Precisam ser cadastrados no SIMUS
- **Exames faltantes**: Precisam ser adicionados aos pacientes no SIMUS
- **Divergências**: Valores precisam ser corrigidos no SIMUS

### Exportando Dados

- Use o **relatório TXT** para documentação
- Use o **CSV de divergências** para análise em Excel
- Os dados podem ser filtrados e ordenados nas tabelas

---

## ❓ Perguntas Frequentes

### Por que alguns pacientes não aparecem no SIMUS?

Pode ser que:
- O paciente não foi cadastrado no SIMUS
- O nome está escrito diferente (com acentos, espaços, etc.)
- O paciente foi cadastrado em outro período

### Por que alguns exames não aparecem?

Pode ser que:
- O exame não foi cadastrado no SIMUS
- O código do exame está diferente
- O exame foi cadastrado com outro código

### Por que há divergências de valores?

Pode ser que:
- O valor foi digitado errado no SIMUS
- Há diferença na forma de cálculo
- O exame foi cobrado com valor diferente

### Como corrigir os problemas?

1. Identifique os problemas nas abas
2. Acesse o SIMUS
3. Cadastre pacientes faltantes
4. Adicione exames faltantes
5. Corrija valores divergentes
6. Refaça a análise para verificar

---

## 🔍 Exemplo de Análise

**Cenário**: Análise de dezembro/2025

**Resultados**:
- 3 pacientes faltantes no SIMUS
- 15 exames não cadastrados
- 8 divergências de valores

**Ações**:
1. Cadastrar os 3 pacientes no SIMUS
2. Adicionar os 15 exames faltantes
3. Corrigir os 8 valores divergentes
4. Reanalisar para confirmar correções

---

**Boa análise! 📊**

