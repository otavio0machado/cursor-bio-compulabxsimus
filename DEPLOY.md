# Deploy no Railway com Cloudinary

Este guia descreve como fazer o deploy da aplicação Biodiagnóstico no Railway.app, utilizando Nginx para proxy reverso e Cloudinary para armazenamento de arquivos.

## 1. Pré-requisitos

1.  Conta no [GitHub](https://github.com/) com o código do projeto.
2.  Conta no [Railway](https://railway.app/).
3.  Conta no [Cloudinary](https://cloudinary.com/) (Gratuita).

## 2. Configuração do Cloudinary

Para que os uploads funcionem em produção, precisamos de uma conta no Cloudinary para armazenar os arquivos.

1.  Crie uma conta gratuita em [cloudinary.com](https://cloudinary.com).
2.  No Dashboard, copie as seguintes credenciais:
    *   **Cloud Name**
    *   **API Key**
    *   **API Secret**

## 3. Configuração no Railway

1.  Crie um **New Project** → **Deploy from GitHub repo**.
2.  Selecione o repositório `cursor-bio-compulabxsimus`.
3.  Vá em **Settings**:
    *   **Root Directory**: `biodiagnostico_app` (IMPORTANTE!)
4.  Vá em **Variables** e adicione:

| Variável | Valor |
|----------|-------|
| `API_URL` | `https://[SEU-DOMINIO-RAILWAY].up.railway.app` (sem barra no final) |
| `CORS_ALLOWED_ORIGINS` | Origem(ens) permitidas do frontend (ex: https://app.seudominio.com) |
| `AUTH_EMAIL` | Email de login (ambiente) |
| `AUTH_PASSWORD` | Senha de login (ambiente) |
| `SUPABASE_URL` | URL do projeto Supabase (Settings > API) |
| `SUPABASE_KEY` | Chave `anon public` do Supabase |
| `GEMINI_API_KEY` | (Opcional) Chave API do Google Gemini para IA |
| `CLOUDINARY_CLOUD_NAME` | *(Seu Cloud Name)* |
| `CLOUDINARY_API_KEY` | *(Sua API Key)* |
| `CLOUDINARY_API_SECRET` | *(Seu API Secret)* |

> **Nota:** A URL do Railway pode ser encontrada/gerada na aba **Settings** → **Networking** → **Public Networking**.

## 4. Testando o Deploy

1.  Aguarde o deploy finalizar (aba **Deployments**).
2.  Acesse a URL pública (ex: `https://biodiagnostico-prod.up.railway.app`).
3.  Faca login com as credenciais definidas em AUTH_EMAIL/AUTH_PASSWORD.
4.  Vá em **Conversor** e tente fazer upload do **SIMUS.pdf**.
5.  Se funcionar, você verá a mensagem "✅ SIMUS carregado... (Salvo na nuvem)".

## 5. Solução de Problemas

*   **Erro "WebSocket error" ou Tela Branca**: Verifique se a URL está com `https://` e se o `API_URL` está correto.
*   **Erro no Upload**: Verifique se as credenciais do Cloudinary estão corretas nas variáveis de ambiente.
*   **Healthcheck Failing**: O Nginx demora um pouco para subir, o Railway pode tentar reiniciar. Aumente o *Healthcheck Timeout* no `railway.json` ou `railway.toml` se necessário (já configurado para 300s).