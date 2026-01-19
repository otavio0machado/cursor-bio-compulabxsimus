# 🚀 Deployment SEM Docker

## ✅ DOCKER FOI REMOVIDO!

Este projeto agora faz deployment **diretamente** sem usar Docker.

---

## 📦 Plataformas Suportadas

### 1️⃣ **Railway** (Recomendado)
```bash
# Railway detecta automaticamente o nixpacks.toml e railway.toml
railway up
```

**Configurações Automáticas:**
- Builder: NIXPACKS (configurado via `nixpacks.toml`)
- Python: 3.11
- Node.js: 18.x
- Build: Automático via `reflex init`
- Start: `reflex run --env prod --loglevel info`
- Port: 3000 (porta padrão do Reflex)

**⚠️ IMPORTANTE:**
- O Railway usa `nixpacks.toml` para as instruções de build
- NÃO precisa configurar nada manualmente no dashboard
- Apenas faça push e o Railway faz tudo automaticamente

**Variáveis de Ambiente Necessárias:**
```
GEMINI_API_KEY=your_key_here
SUPABASE_URL=your_url_here
SUPABASE_KEY=your_key_here
CLOUDINARY_URL=cloudinary://...
```

---

### 2️⃣ **Render**
```yaml
# render.yaml (criar na raiz)
services:
  - type: web
    name: biodiagnostico
    env: python
    buildCommand: cd biodiagnostico_app && pip install -r requirements.txt && reflex init
    startCommand: cd biodiagnostico_app && reflex run --env prod --loglevel info
    envVars:
      - key: PYTHON_VERSION
        value: 3.11
```

---

### 3️⃣ **Heroku**
```bash
# Heroku usa o Procfile automaticamente
heroku create seu-app
git push heroku main
```

O arquivo `Procfile` já está configurado:
```
web: cd biodiagnostico_app && reflex run --env prod --loglevel info
```

---

## 🔧 Desenvolvimento Local

```bash
cd biodiagnostico_app
pip install -r requirements.txt
reflex init
reflex run
```

---

## 📁 Arquivos Docker (Desabilitados)

Os seguintes arquivos foram **desabilitados** mas mantidos para referência:
- `Dockerfile.disabled`
- `nginx-docker.conf.disabled`
- `start-docker.sh.disabled`

Se precisar reativar o Docker no futuro, basta renomear removendo `.disabled`.

---

## ⚙️ Comandos Úteis

### Build do Frontend
```bash
cd biodiagnostico_app
reflex export --frontend-only
```

### Rodar em Produção
```bash
cd biodiagnostico_app
reflex run --env prod --loglevel info
```

### Rodar com Backend Only
```bash
cd biodiagnostico_app
reflex run --env prod --backend-only --backend-port 8000
```

---

## 🐛 Troubleshooting

### Erro: "Module not found"
```bash
cd biodiagnostico_app
pip install -r requirements.txt
```

### Erro: "reflex command not found"
```bash
pip install reflex>=0.8.0
```

### Port já em uso
```bash
# Especifique uma porta diferente
reflex run --port 8080
```

---

## 📊 Status do Projeto

✅ **Docker Removido**
✅ **Deployment Direto Configurado**
✅ **Railway/Render/Heroku Suportados**
✅ **Procfile Criado**
✅ **railway.toml Atualizado**

---

## 🎯 Próximos Passos

1. Merge o PR: https://github.com/otavio0machado/cursor-bio-compulabxsimus/pull/new/claude/remove-docker-z1dgy
2. Railway vai automaticamente re-deployar sem Docker
3. Deployment deve funcionar sem erros! 🎉
