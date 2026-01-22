# 📊 Biodiagnóstico - Sistema de Gestão Inteligente

> **Sistema avançado de auditoria financeira e controle de qualidade laboratorial.**
> *Desenvolvido com Reflex, Python e IA Generativa (Google Gemini).*

![Status](https://img.shields.io/badge/Status-Active-success)
![Framework](https://img.shields.io/badge/Framework-Reflex-blue)
![AI](https://img.shields.io/badge/AI-Gemini%20Flash-orange)
![Database](https://img.shields.io/badge/DB-Supabase-green)

O **Biodiagnóstico x SIMUS** é uma plataforma integrada para modernizar a gestão do Laboratório Biodiagnóstico. O sistema evoluiu de um simples script de comparação de PDFs para uma aplicação web robusta que integra auditoria financeira, controle de qualidade (CQ) em tempo real e análise de dados assistida por Inteligência Artificial.

## 🚀 Funcionalidades Principais

### 🔍 1. Auditoria Financeira (Compulab vs SIMUS)
Automatiza a conferência mensal de faturamento, identificando divergências que causam prejuízos.
- **Comparação de PDFs Automática**: Upload de relatórios Compulab e SIMUS.
- **Detecção de Divergências**:
  - ✅ Pacientes faltantes (realizados mas não faturados).
  - ✅ Exames não cadastrados ou com códigos errados.
  - ✅ Divergências de valores (R$) por exame.
- **Relatórios**: Geração de planilhas Excel e relatórios detalhados.

### 🧪 2. Controle de Qualidade (QC)
Módulo completo para gestão da qualidade analítica.
- **Regras de Westgard**: Validação automática (1-2s, 1-3s, 2-2s, R-4s, etc.).
- **Gráficos de Levey-Jennings**: Visualização interativa da variabilidade.
- **Gestão de Exames**: Cadastro e monitoramento de métricas (Média, DP).

### 🤖 3. Detetive de Dados (IA)
Assistente inteligente integrado ao sistema.
- **Análise Conversacional**: Pergunte sobre os dados financeiro ou de qualidade.
- **Insights Automáticos**: A IA analisa tendências e sugere correções baseado nos dados processados.
- **Separação de Contexto**: Prompts otimizados para evitar alucinações.

### 🛠️ 4. Ferramentas Utilitárias
- **Conversor PDF -> Excel**: Transformação rápida de relatórios técnicos.
- **Dashboard Executivo**: KPIs em tempo real para tomada de decisão.

---

## 💻 Tech Stack

O projeto utiliza uma arquitetura moderna e escalável:

| Componente | Tecnologia | Descrição |
|------------|------------|-----------|
| **Frontend/Backend** | [Reflex](https://reflex.dev) | Framework Full-stack em Python puro. |
| **Banco de Dados** | Supabase (PostgreSQL) | Armazenamento persistente para QC e auditorias. |
| **Inteligência Artificial** | Google Gemini 1.5 Flash | Cérebro do "Detetive de Dados". |
| **Automação** | n8n | Orquestração de fluxos complexos de IA. |
| **Processamento** | Pandas & PDFPlumber | Engenharia de dados e extração de PDFs. |
| **Deploy** | Railway / Docker | Infraestrutura de produção. |

---

## 📂 Estrutura do Projeto

```
/
├── .agent/                 # 🧠 Agente IA: Skills, Prompts e Workflows
│   ├── skills/             # Habilidades especializadas (Arquivista, Guardião, etc.)
│   └── workflows/          # Fluxos de trabalho automatizados
├── biodiagnostico_app/     # 📱 Aplicação Principal (Reflex)
│   ├── assets/             # Imagens, CSS customizado
│   └── biodiagnostico_app/ # Código fonte Python
│       ├── ai/             # Integração com Gemini
│       ├── components/     # Componentes UI Reutilizáveis
│       ├── pages/          # Rotas e páginas (Dashboard, QC, Upload)
│       ├── services/       # Lógica de negócio (Westgard, PDF, etc.)
│       ├── state.py        # Gerenciamento de estado (Backend Reflex)
│       └── styles.py       # Design System centralizado
└── n8n_workflows/          # 🔄 Fluxos de automação exportados
```

---

## 🏃 Como Iniciar

### Pré-requisitos
- Python 3.9+
- Acesso à internet (para carregar assets do Reflex)
- Chave de API do Google Gemini (configurada no `.env`)

### Instalação

1. **Clone o repositório**
2. **Crie um ambiente virtual e instale as dependências:**
   ```bash
   cd biodiagnostico_app
   pip install -r requirements.txt
   ```
3. **Configure as variáveis de ambiente:**
   Crie um arquivo `.env` na raiz com sua `GEMINI_API_KEY` e URLs do Supabase.

4. **Execute a aplicação:**
   ```bash
   reflex run
   ```
   O app estará disponível em `http://localhost:3000`.

---

## 📚 Documentação Adicional

Para detalhes específicos, consulte os guias na raiz do projeto:

- `COMO_INICIAR.md`: Guia passo-a-passo para iniciantes.
- `DEPLOY.md`: Instruções para colocar em produção.
- `ESTRUTURA_MODULAR.md`: Explicação da arquitetura de código.
- `GUIA_ANALISE_PACIENTES.md`: Manual de uso para a auditoria financeira.

---

**Desenvolvido por Otávio Machado** | *Laboratório Biodiagnóstico*
