---
name: UI/UX Reflex Premium
description: Diretrizes de design system, tokens e componentes visuais premium para o ecossistema Biodiagnóstico utilizando Reflex.
---

# Skill: UI/UX Reflex Premium

Esta skill define a identidade visual "Biodiagnóstico 2.0". Ela deve ser utilizada para garantir consistência estética, usabilidade (acessibilidade) e o "feeling" premium em todas as telas da aplicação.

## 🎨 Princípios de Design
1. **Glassmorphism**: Uso de transparências e blur em modais e overlays para profundidade.
2. **Respiro Visual**: Espaçamentos generosos baseados em múltiplos de 4 (utilizando a classe `Spacing`).
3. **Micro-interações**: Botões e elementos clicáveis devem reagir suavemente ao hover e clique (escalonamento, brilho).
4. **Legibilidade**: Contraste alto usando `Color.DEEP` para títulos e `Color.TEXT_PRIMARY` para o corpo.

## 🛠️ Ferramentas e Tokens
Os tokens estão definidos no arquivo `biodiagnostico_app/biodiagnostico_app/styles.py`.

- **Cores**: `Color.PRIMARY` (#4CAF50), `Color.DEEP` (#1B5E20), `Color.BACKGROUND` (#F8F9FA).
- **Sombras**: `Design.SHADOW_MD` para cards padrão, `Design.SHADOW_LG` para elementos flutuantes.
- **Raio de Borda**: `Design.RADIUS_LG` (12px) é o padrão para inputs e botões.

## 📝 Como Implementar Componentes
Sempre verifique a pasta `examples/` nesta skill para snippets prontos de:
- `glass_card.py`: Cards com efeito de vidro.
- `premium_button.py`: Botões com gradiente e animação.
- `data_table.py`: Tabelas formatadas para leitura de dados médicos.

## 🚨 Regras Inegociáveis
1. **Acessibilidade**: Todo input deve ter `min_height="44px"`.
2. **Consistência**: Nunca use cores hexadecimais soltas; use sempre a classe `Color`.
3. **Animação**: Toda página deve carregar com uma animação de `fadeInUp`.
4. **Layout Oficial**: Novas páginas devem, por padrão, ser integradas ao `authenticated_layout()` ou conter a `navbar()` e o fundo `Color.BACKGROUND` para evitar o aspecto de "página solta".
5. **Harmonia**: O uso de `GLASS_STYLE` deve ser moderado (modais/overlays). Cards de dashboard devem preferir `Color.SURFACE` sólido com `_hover` para profundidade.

## 👁️ Check de Referência Visual
Antes de entregar, compare o código com as imagens de referência do projeto (Dashboard e Controle de Qualidade):
- O cabeçalho está alinhado?
- A cor de fundo é a correta (#F8F9FA)?
- O respiro (`padding`) condiz com o site real?
