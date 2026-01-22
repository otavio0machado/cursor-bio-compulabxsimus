# 🕵️ Detetive de Dados - n8n AI Agent

## Como Importar o Workflow no n8n

### 1. Acesse seu n8n
- **n8n Cloud**: https://app.n8n.cloud
- **Self-hosted**: Seu endereço local (ex: http://localhost:5678)

### 2. Importe o Workflow
1. No menu lateral, clique em **"Workflows"**
2. Clique no botão **"⋮"** (três pontos) ou **"+"**
3. Selecione **"Import from File"**
4. Escolha o arquivo `detetive_dados_agent.json`
5. Clique em **"Import"**

### 3. Configure as Credenciais

#### Google Gemini API
1. Clique no node **"Google Gemini Chat Model"**
2. Em "Credential", clique **"+ Create New Credential"**
3. Cole sua API Key do Google AI Studio:
   ```
   AIzaSyDGTEcm3CIIZbAiO6PQLvEpWr77jPCTZm8
   ```
4. Clique **"Save"**

#### Supabase API (para Tool: Buscar Histórico)
1. Clique no node **"Tool: Buscar Histórico"**
2. Em "Credential", clique **"+ Create New Credential"**
3. Configure:
   - **Host**: `https://sxytwmsjfmxhlcfnuiqm.supabase.co`
   - **Service Role Key**: Sua service key do Supabase
4. Clique **"Save"**

### 4. Ative o Workflow
1. No canto superior direito, clique no toggle **"Active"**
2. O workflow agora está rodando!

### 5. Copie a URL do Webhook
1. Clique no node **"Webhook Detetive"**
2. Copie a **"Production URL"** (ex: `https://your-instance.n8n.cloud/webhook/detetive-dados`)
3. Adicione no seu `.env`:
   ```
   N8N_WEBHOOK_URL=https://your-instance.n8n.cloud/webhook/detetive-dados
   ```

---

## Estrutura do Workflow

```
[Webhook] → [AI Agent + Gemini] → [Resposta]
                   ↑
            [4 Tools disponíveis]
            ├── Analisar Divergências
            ├── Calcular Perda Financeira
            ├── Buscar Histórico (Supabase)
            └── Top Offenders
```

## Como Testar

1. Com o workflow ativo, faça um POST para o webhook:
```bash
curl -X POST "SUA_URL_WEBHOOK" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Qual o total de perdas financeiras?",
    "context": "{\"value_divergences\": [{\"convenio\": \"Unimed\", \"valor_simus\": 100, \"valor_convenio\": 80}]}"
  }'
```

2. Você receberá uma resposta JSON com a análise do AI Agent!

---

## Próximos Passos

1. ✅ Importar workflow no n8n
2. ✅ Configurar credenciais
3. ✅ Ativar workflow
4. 🔄 Atualizar `.env` com a URL do webhook
5. 🔄 Testar a integração no app Biodiagnóstico
