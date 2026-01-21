---
name: Código Limpo e Refinamento (Aspirador)
description: Skill focada em identificar e corrigir dívidas técnicas, inconsistências de design e problemas de performance no ecossistema Biodiagnóstico.
---

# Skill: Código Limpo e Refinamento (Aspirador)

Esta skill define o protocolo "Aspirador", cujo objetivo é purificar o código-fonte, eliminando redundâncias, corrigindo bugs silenciosos e garantindo que cada linha de código seja eficiente e elegante.

## 🧹 Princípios do Aspirador

1. **Modularização Extrema**: Arquivos com mais de 800 linhas (ex: `state.py`) são considerados "caixas pretas" perigosas. Devem ser fatiados em estados menores e especializados (ex: `StateAnalise`, `StateQC`, `StateFaturamento`).
2. **Design System Purista**: Qualquer estilo CSS declarado fora de `styles.py` ou sem o uso de tokens (`Color`, `Design`, `Spacing`) deve ser "aspirado" e substituído pelas constantes oficiais.
3. **Eliminação de Código Morto**: Funções que não são chamadas ou variáveis globais obsoletas devem ser removidas.
4. **UX de Alinhamento**: Tabelas e grids devem seguir o mesmo padrão de respiro e hover em todas as páginas. Se uma página "parece diferente", ela está quebrada.

## 🛠️ O Protocolo de Refinamento (Passo-a-passo)

1. **Scan de Inconsistências**: Rodar o script `validate_reflex.py` para erros técnicos básicos.
2. **Auditoria de Estilos**: Buscar por strings hex (#...) e substituí-las.
3. **Refatoração de Estado**: Identificar lógica de backend misturada com UI e mover para camadas de `services/` ou `utils/`.
4. **Validar Performance**: Verificar se há carregamentos desnecessários em tabs inativas (usar `rx.cond` para renderização preguiçosa).

## 🚨 Checklist do Aspirador (Antes de entregar)
- O código está mais curto do que antes?
- A performance melhorou ou a legibilidade aumentou?
- O `Reflex Technical Guardrails` foi aplicado em 100% dos arquivos tocados?
- Existe algum comentário "TODO" ou código comentado que poderia ser deletado?
