# 🚀 Deploy no Streamlit Cloud - Guia Rápido

## ✅ Seu Repositório GitHub
**URL**: https://github.com/otavio0machado/cursor-bio-compulabxsimus

---

## 📋 Passo a Passo para Deploy

### 1️⃣ Acesse o Streamlit Cloud
👉 **https://share.streamlit.io/**

### 2️⃣ Faça Login
- Use sua conta GitHub (mesma do repositório)

### 3️⃣ Clique em "New app"

### 4️⃣ Configure o Deploy

Preencha os campos assim:

| Campo | Valor |
|-------|-------|
| **Repository** | `otavio0machado/cursor-bio-compulabxsimus` |
| **Branch** | `main` |
| **Main file path** | `app.py` |

### 5️⃣ Clique em **"Deploy!"**

---

## ⏱️ Tempo de Deploy

O deploy leva **2-5 minutos** na primeira vez.

---

## 🔑 Configurar API do Gemini (Opcional)

Depois do deploy:

1. Clique no **ícone de menu** (⋮) do seu app
2. Vá em **"Settings"**
3. Clique em **"Secrets"**
4. Adicione:

```toml
GEMINI_API_KEY = "sua_api_key_aqui"
```

5. Clique em **"Save"**

---

## ✅ Checklist

- [x] Repositório no GitHub criado
- [x] `app.py` na raiz
- [x] `requirements.txt` configurado
- [x] `.streamlit/config.toml` configurado
- [x] Código atualizado e commitado
- [ ] Deploy realizado no Streamlit Cloud
- [ ] (Opcional) API Key configurada

---

## 🌐 Sua URL do App

Após o deploy, sua aplicação estará em:
```
https://otavio0machado-cursor-bio-compulabxsimus-app-xxxxx.streamlit.app
```

---

## 🔄 Atualizações Automáticas

Cada `git push` para `main` atualiza o app automaticamente!

```bash
git add .
git commit -m "Nova atualização"
git push origin main
```

---

## 🐛 Problemas Comuns

### App não carrega
- Verifique os logs: Menu → Manage app → Logs
- Certifique-se que `app.py` está na raiz

### Erro de módulo não encontrado
- Verifique se todas as dependências estão no `requirements.txt`
- Verifique se `utils/__init__.py` existe

### Visual não está correto
- Limpe o cache: Menu → Settings → Clear cache
- Recarregue a página

---

**🧬 Laboratório Biodiagnóstico** - Pronto para Deploy!

