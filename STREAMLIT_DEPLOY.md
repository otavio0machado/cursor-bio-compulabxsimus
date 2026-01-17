# 🚀 Deploy no Streamlit Cloud

## Guia Completo para Deploy do Biodiagnóstico

Este guia explica como fazer o deploy da aplicação no Streamlit Cloud de forma gratuita.

---

## 📋 Pré-requisitos

1. **Conta no GitHub** - [Criar conta](https://github.com/signup)
2. **Conta no Streamlit Cloud** - [Criar conta](https://share.streamlit.io/) (use sua conta GitHub)
3. **Repositório Git** com o código da aplicação

---

## 📁 Estrutura de Arquivos Necessária

```
seu-repositorio/
├── app.py                    # Arquivo principal do Streamlit
├── requirements.txt          # Dependências Python
├── config.py                 # Configurações do laboratório
├── utils/
│   ├── __init__.py
│   └── ui.py                 # Utilitários de interface
├── .streamlit/
│   └── config.toml           # Configurações do tema
└── .gitignore                # Arquivos a ignorar
```

---

## 🔧 Passo a Passo

### 1. Criar Repositório no GitHub

```bash
# Inicializar repositório (se ainda não tiver)
git init

# Adicionar arquivos
git add .

# Commit inicial
git commit -m "Versão inicial para deploy Streamlit"

# Criar repositório no GitHub e conectar
git remote add origin https://github.com/SEU_USUARIO/biodiagnostico-app.git
git branch -M main
git push -u origin main
```

### 2. Acessar Streamlit Cloud

1. Acesse [share.streamlit.io](https://share.streamlit.io/)
2. Faça login com sua conta GitHub
3. Clique em **"New app"**

### 3. Configurar o Deploy

Preencha os campos:

| Campo | Valor |
|-------|-------|
| **Repository** | `seu-usuario/biodiagnostico-app` |
| **Branch** | `main` |
| **Main file path** | `app.py` |

### 4. Configurar Secrets (API Keys)

⚠️ **IMPORTANTE**: Nunca coloque API keys no código!

1. No Streamlit Cloud, vá em **Settings** → **Secrets**
2. Adicione suas chaves no formato TOML:

```toml
GEMINI_API_KEY = "sua_api_key_do_gemini_aqui"
```

3. No código, acesse via:
```python
import streamlit as st
api_key = st.secrets.get("GEMINI_API_KEY", "")
```

### 5. Deploy!

Clique em **"Deploy!"** e aguarde alguns minutos.

---

## 🔑 Configurando a API do Gemini

### Opção 1: Via Secrets (Recomendado para produção)

1. Obtenha sua API key em: [makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
2. Adicione no Streamlit Cloud Secrets (passo 4 acima)

### Opção 2: Via Interface (Para usuários)

Os usuários podem inserir sua própria API key na barra lateral da aplicação.

---

## 🎨 Personalização do Tema

O arquivo `.streamlit/config.toml` define o tema visual:

```toml
[theme]
primaryColor = "#8BC34A"          # Verde limão (botões)
backgroundColor = "#F8FFF8"       # Fundo claro
secondaryBackgroundColor = "#E8F5E9"  # Sidebar
textColor = "#1B5E20"             # Texto verde escuro
```

---

## 📊 Limites do Plano Gratuito

| Recurso | Limite |
|---------|--------|
| Apps públicos | Ilimitados |
| Apps privados | 1 |
| RAM | 1 GB |
| Upload de arquivos | 200 MB |
| Tempo de inatividade | 7 dias (depois hiberna) |

---

## 🔧 Solução de Problemas

### Erro: "ModuleNotFoundError"
- Verifique se todas as dependências estão no `requirements.txt`
- Certifique-se de que as versões são compatíveis

### Erro: "No module named 'config'"
- Verifique se o `config.py` está na raiz do repositório
- Confirme que o `__init__.py` existe na pasta `utils/`

### App não carrega
- Verifique os logs no Streamlit Cloud (ícone de menu → "Manage app" → "Logs")
- Teste localmente primeiro: `streamlit run app.py`

### Arquivos PDF não processam
- Limite de upload é 200MB no plano gratuito
- Verifique se `pdfplumber` está no `requirements.txt`

---

## 🔄 Atualizações

Cada push para o branch `main` dispara um novo deploy automaticamente!

```bash
# Fazer alterações
git add .
git commit -m "Atualização: nova funcionalidade"
git push origin main
```

---

## 🌐 URL da Aplicação

Após o deploy, sua aplicação estará disponível em:

```
https://seu-usuario-biodiagnostico-app-app-xxxxx.streamlit.app
```

Você pode personalizar a URL nas configurações do app.

---

## 📱 Recursos Adicionais

- [Documentação Streamlit](https://docs.streamlit.io/)
- [Streamlit Cloud Docs](https://docs.streamlit.io/streamlit-community-cloud)
- [Fórum da Comunidade](https://discuss.streamlit.io/)

---

## ✅ Checklist Final

- [ ] Repositório no GitHub criado
- [ ] `requirements.txt` com todas as dependências
- [ ] `.streamlit/config.toml` configurado
- [ ] `.gitignore` incluindo secrets
- [ ] API keys configuradas nos Secrets
- [ ] Teste local funcionando
- [ ] Deploy realizado com sucesso

---

**🧬 Laboratório Biodiagnóstico** - Sistema de Administração  
*Desenvolvido para análise de faturamento COMPULAB vs SIMUS*

