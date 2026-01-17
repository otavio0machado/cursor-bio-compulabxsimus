# 🚀 Guia de Deploy - Biodiagnóstico App

## ⚠️ Importante: Upload de Arquivos Grandes

Esta aplicação processa arquivos PDF de até **50MB** (ex: SIMUS.pdf ~12MB). 
O **Reflex Cloud** tem limite de ~5MB para uploads, por isso recomendamos **Railway**.

---

## ✅ Opção Recomendada: Railway (Suporta uploads grandes)

O Railway permite configuração customizada do Nginx para uploads de até 100MB.

### Passo 1: Criar conta no Railway
1. Acesse [railway.app](https://railway.app)
2. Crie uma conta (pode usar GitHub)

### Passo 2: Conectar repositório
1. No Railway, clique em **"New Project"**
2. Selecione **"Deploy from GitHub repo"**
3. Escolha o repositório `cursor-bio-compulabxsimus`
4. **Root Directory**: Configure para `biodiagnostico_app`

### Passo 3: Configurar variáveis de ambiente
No painel do Railway, adicione:
```
API_URL=https://sua-app.railway.app
```

### Passo 4: Deploy automático
O Railway detectará o `Dockerfile` e fará o deploy automaticamente.
Após ~5 minutos, sua aplicação estará disponível em uma URL `.railway.app`.

---

## 🐳 Alternativa: Docker Local

Para testar localmente com a mesma configuração de produção:

```bash
cd biodiagnostico_app
docker build -t biodiagnostico .
docker run -p 3000:3000 -p 8000:8000 biodiagnostico
```

Acesse: http://localhost:3000

---

## ⚡ Reflex Cloud (Apenas para arquivos pequenos)

> **Limitação**: Uploads máximo de ~5MB

Se seus arquivos forem pequenos:

```bash
cd biodiagnostico_app
py -m reflex login
py -m reflex deploy
```

---

## 📁 Arquivos de Configuração

| Arquivo | Descrição |
|---------|-----------|
| `Dockerfile` | Container com Nginx + Reflex |
| `nginx.conf` | Limite de upload de 100MB |
| `start.sh` | Script de inicialização |
| `railway.json` | Configuração do Railway |
