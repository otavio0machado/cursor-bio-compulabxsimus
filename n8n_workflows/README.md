# 🕵️ Detetive de Dados - n8n AI Agent

## 📦 Versões Disponíveis

| Arquivo | Modelo | Descrição |
|---------|--------|-----------|
| `detetive_dados_agent_v7_http_tools.json` | Gemini 2.0 Flash | **RECOMENDADO** - Usa `toolHttpRequest` para ferramentas com parâmetros. Máxima compatibilidade. |
| `detetive_dados_agent_v6_fixed.json` | Gemini 2.0 Flash | Usa `inputSchema` para definir parâmetros. Pode não funcionar em n8n antigos. |
| `detetive_dados_agent_v5_skills.json` | Gemini 1.5 Flash | Versão anterior com todas as ferramentas. |
| `detetive_dados_agent.json` | Gemini 2.0 Flash | Versão básica com 4 ferramentas. |

---

## 🚀 Quick Start (v7 Recomendada)

### 1. Importe o Workflow

1. Acesse seu n8n (Cloud ou Self-hosted)
2. Menu **Workflows** → **Import from File**
3. Escolha `detetive_dados_agent_v7_http_tools.json`

### 2. Configure as Credenciais

#### Google Gemini API
1. Clique no node **"Google Gemini Chat Model"**
2. **Create New Credential** → Cole sua API Key do [Google AI Studio](https://aistudio.google.com/)
3. Save

### 3. Configure a URL Base do App

As ferramentas `interpretador_westgard`, `gerar_contestacao` e `comparar_tabelas` fazem chamadas HTTP para o seu app.

**No n8n:**
1. Clique em cada um desses nodes
2. Altere a URL de base:
   ```
   https://seu-app.railway.app
   ```
   Para a URL real do seu deploy (Railway, Vercel, etc.)

**OU passe `app_base_url` no payload:**
```json
{
  "message": "Valide o QC: value=150, target=145, sd=3",
  "context": "{}",
  "app_base_url": "https://seu-app.railway.app"
}
```

### 4. Ative o Workflow

1. Toggle **"Active"** no canto superior direito
2. Copie a **Production URL** do webhook
3. Adicione no seu `.env`:
   ```
   N8N_WEBHOOK_URL=https://seu-n8n.com/webhook/detetive-dados
   ```

---

## 🛠️ Ferramentas Disponíveis

### Ferramentas sem Parâmetros (toolCode)
Essas ferramentas usam os dados de contexto automaticamente:

| Ferramenta | Descrição |
|------------|-----------|
| `calcular_perda` | Calcula prejuízo total das divergências |
| `top_offenders` | Ranking de convênios/exames problemáticos |
| `analisar_tendencia` | Verifica se está melhorando ou piorando |
| `projecao_perda` | Estima perda até o fim do mês |
| `resumo_executivo` | Briefing diário com KPIs |
| `detectar_anomalias` | Identifica outliers nos dados |

### Ferramentas com Parâmetros (toolHttpRequest)
Essas ferramentas fazem chamadas HTTP para endpoints do seu app:

| Ferramenta | Endpoint | Parâmetros |
|------------|----------|------------|
| `interpretador_westgard` | `/api/n8n-tools/westgard` | `value`, `target_value`, `target_sd` |
| `gerar_contestacao` | `/api/n8n-tools/contestacao` | `convenio`, `exame`, `valor_cobrado`, `valor_pago`, `motivo`, `paciente` |
| `comparar_tabelas` | `/api/n8n-tools/comparar-tabelas` | `exame` |

---

## 🧪 API Endpoints (Backend)

O app Biodiagnóstico expõe os seguintes endpoints para as tools:

### POST `/api/n8n-tools/westgard`
Valida resultados de QC usando regras de Westgard.

```json
{
  "value": 150,
  "target_value": 145,
  "target_sd": 3
}
```

**Resposta:**
```json
{
  "sucesso": true,
  "dados_entrada": { "valor_medido": 150, "media_esperada": 145, "desvio_padrao": 3 },
  "resultado": {
    "z_score": "1.667",
    "status": "OK ✅",
    "severity": "none",
    "cor_indicador": "green"
  },
  "violations": [],
  "interpretacao": "Aceitável: Entre 1-2 SD (zona amarela)",
  "recomendacao": "✅ Resultado dentro dos limites. Liberar análise normalmente."
}
```

### POST `/api/n8n-tools/contestacao`
Gera carta de contestação de glosa.

```json
{
  "convenio": "Unimed",
  "exame": "Hemograma",
  "valor_cobrado": 35.00,
  "valor_pago": 28.00,
  "motivo": "valor acima da tabela",
  "paciente": "João Silva"
}
```

### POST `/api/n8n-tools/comparar-tabelas`
Compara preços entre lab e convênios.

```json
{
  "exame": "HEMOGRAMA"
}
```

### GET `/api/n8n-tools/health`
Verifica se a API está funcionando.

---

## 📋 Testando a Integração

### Via cURL
```bash
curl -X POST "SUA_URL_WEBHOOK" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Qual o total de perdas financeiras?",
    "context": "{\"value_divergences\": [{\"convenio\": \"Unimed\", \"valor_simus\": 100, \"valor_convenio\": 80}]}",
    "app_base_url": "https://seu-app.railway.app"
  }'
```

### Teste de QC Westgard
```bash
curl -X POST "SUA_URL_WEBHOOK" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Valide este resultado de QC: valor medido 155, média 145, desvio padrão 3",
    "context": "{}",
    "app_base_url": "https://seu-app.railway.app"
  }'
```

---

## 🐛 Troubleshooting

### Erro: `key cannot be empty`
**Causa:** O Gemini 2.0 rejeita tools com `properties: {}` vazias.
**Solução:** Use o workflow v7 que usa `toolHttpRequest` para ferramentas com parâmetros.

### Erro: Tools não são chamadas
**Causa:** O AI Agent pode não estar reconhecendo o formato dos parâmetros.
**Solução:** Verifique se você está passando `app_base_url` no payload ou configurou a URL hardcoded nos nodes.

### Erro: Conexão recusada nas HTTP tools
**Causa:** O app backend não está rodando ou a URL está incorreta.
**Solução:** 
1. Verifique se o app está online
2. Teste o endpoint diretamente: `curl https://seu-app/api/n8n-tools/health`
3. Confirme que o router foi registrado no app

### Erro: Timeout
**Causa:** O processamento está demorando muito.
**Solução:** O serviço n8n tem timeout de 60s. Para análises muito grandes, considere paginar os dados.

---

## 📁 Arquivos Relacionados

- `biodiagnostico_app/api_n8n_tools.py` - Endpoints FastAPI para as tools
- `biodiagnostico_app/services/n8n_tools_service.py` - Lógica das ferramentas
- `biodiagnostico_app/services/n8n_service.py` - Cliente para chamar o n8n

---

## ✅ Checklist de Configuração

- [ ] Importar workflow v7 no n8n
- [ ] Configurar credencial Google Gemini API
- [ ] Configurar URL base do app nas HTTP tools
- [ ] Ativar workflow
- [ ] Copiar URL do webhook para `.env`
- [ ] Testar endpoint health: `/api/n8n-tools/health`
- [ ] Testar pergunta simples no app
