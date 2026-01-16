# 🔑 Configuração da API do Gemini

## Como Obter sua API Key do Google Gemini

### Passo 1: Acessar o Google AI Studio
1. Acesse: **https://makersuite.google.com/app/apikey**
2. Ou vá em: **https://aistudio.google.com/apikey**

### Passo 2: Fazer Login
- Faça login com sua conta Google
- (Se necessário, crie uma conta Google gratuita)

### Passo 3: Criar API Key
1. Clique no botão **"Create API Key"** (Criar Chave de API)
2. Escolha um projeto Google Cloud (ou crie um novo)
3. Sua chave será gerada automaticamente

### Passo 4: Copiar a Chave
- Copie a chave gerada (algo como: `AIzaSy...`)
- **⚠️ IMPORTANTE**: Mantenha sua chave secreta! Não compartilhe publicamente.

### Passo 5: Usar no App
1. No app Streamlit, vá para a barra lateral
2. Na seção **"🤖 Análise por IA (Gemini)"**
3. Cole sua API Key no campo **"🔑 Gemini API Key"**
4. A chave será armazenada apenas na sessão do navegador

## 📋 Características

- ✅ **Gratuita**: A API do Gemini tem um nível gratuito generoso
- ✅ **Segura**: A chave só existe na sua sessão do navegador
- ✅ **Não compartilhada**: Sua chave não é enviada ao servidor (exceto para a API do Google)

## 🔒 Segurança

- Nunca compartilhe sua API Key publicamente
- Não commite a chave no Git
- A chave é usada apenas para fazer requisições à API do Gemini

## 💡 Uso no App

Após configurar a API Key:
1. Faça upload dos PDFs/CSVs
2. Clique em "Analisar"
3. Vá para a aba **"🤖 Análise por IA"**
4. Clique em **"🤖 Gerar Análise por IA"**
5. A IA analisará os dados e fornecerá insights detalhados!

## ❓ Problemas Comuns

**Erro: "Invalid API Key"**
- Verifique se copiou a chave corretamente
- Certifique-se de que não há espaços extras

**Erro: "Quota exceeded"**
- Você pode ter excedido o limite gratuito
- Aguarde ou atualize para um plano pago

**Biblioteca não encontrada**
```bash
pip install google-generativeai
```

---

**Pronto para usar!** 🚀


