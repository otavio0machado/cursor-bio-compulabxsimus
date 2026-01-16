# 🚀 Guia de Deploy - Streamlit Community Cloud

Este guia mostra como fazer deploy do app no **Streamlit Community Cloud** (gratuito e fácil).

## 📋 Pré-requisitos

1. Conta no **GitHub** (gratuita) - [Criar conta](https://github.com/signup)
2. Conta no **Streamlit Community Cloud** (gratuita) - [Criar conta](https://share.streamlit.io/)

## 🔧 Passo a Passo

### 1. Preparar o Repositório GitHub

#### Opção A: Se já tem um repositório GitHub

```bash
# No diretório do projeto
git add .
git commit -m "Preparar para deploy"
git push origin main
```

#### Opção B: Criar novo repositório no GitHub

1. Acesse [GitHub](https://github.com) e faça login
2. Clique em **"+"** → **"New repository"**
3. Nome do repositório: `compulab-simus-analyzer` (ou outro nome)
4. **NÃO** marque "Initialize with README"
5. Clique em **"Create repository"**

6. No terminal, execute:

```bash
# Se ainda não inicializou git
git init
git add .
git commit -m "Primeiro commit - app de análise COMPULAB vs SIMUS"

# Adicionar repositório remoto (substitua SEU_USUARIO pelo seu username)
git remote add origin https://github.com/SEU_USUARIO/compulab-simus-analyzer.git

# Renomear branch para main (se necessário)
git branch -M main

# Fazer push
git push -u origin main
```

### 2. Criar Arquivo de Configuração (Opcional)

Crie um arquivo `.streamlit/config.toml` para configurações personalizadas:

```bash
# Criar diretório .streamlit (se não existir)
mkdir -p .streamlit
```

Crie o arquivo `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
headless = true
port = 8501
```

### 3. Deploy no Streamlit Community Cloud

1. **Acesse**: [share.streamlit.io](https://share.streamlit.io/)
2. **Faça login** com sua conta GitHub
3. **Clique em**: **"New app"**
4. **Preencha**:
   - **Repository**: Seu repositório GitHub (ex: `seu-usuario/compulab-simus-analyzer`)
   - **Branch**: `main` (ou `master`)
   - **Main file path**: `app.py`
   - **App URL** (opcional): Escolha uma URL personalizada
5. **Clique em**: **"Deploy!"**

### 4. Aguardar o Deploy

O Streamlit irá:
- Instalar as dependências do `requirements.txt`
- Iniciar o app
- Gerar uma URL pública (ex: `https://seu-app.streamlit.app`)

⏱️ **Tempo**: 2-5 minutos na primeira vez

## ✅ Verificação

Após o deploy, verifique:

1. ✅ O app carrega sem erros
2. ✅ Pode fazer upload de PDFs
3. ✅ A análise funciona corretamente
4. ✅ Os gráficos são exibidos

## 🔄 Atualizar o App

Para atualizar o app depois de fazer mudanças:

```bash
git add .
git commit -m "Descrição das mudanças"
git push origin main
```

O Streamlit **atualiza automaticamente** em alguns segundos!

## 🐛 Troubleshooting

### Erro: "ModuleNotFoundError"

**Solução**: Verifique se todas as dependências estão no `requirements.txt`:

```bash
pip freeze > requirements.txt
# Depois revise e remova dependências desnecessárias
```

### Erro: "FileNotFoundError"

**Solução**: Não use arquivos locais. O app deve funcionar apenas com uploads.

### Erro no Deploy

**Solução**: 
1. Verifique os logs no Streamlit Cloud
2. Certifique-se que `app.py` está na raiz do repositório
3. Verifique se `requirements.txt` está correto

## 📝 Estrutura Final do Repositório

```
seu-repositorio/
├── app.py                    # ← Arquivo principal
├── requirements.txt          # ← Dependências
├── README.md                # ← Documentação
├── .gitignore              # ← Arquivos ignorados
└── .streamlit/             # ← Configurações (opcional)
    └── config.toml
```

## 🔒 Privacidade

- **Apps gratuitos** são públicos por padrão
- Para apps privados, considere usar Streamlit Cloud for Teams (pago)

## 🌐 URLs e Compartilhamento

Após o deploy, você terá:
- **URL pública**: `https://seu-app.streamlit.app`
- Pode compartilhar com qualquer pessoa
- Sem necessidade de instalação para usuários

---

**Pronto!** Seu app estará online e acessível! 🎉


