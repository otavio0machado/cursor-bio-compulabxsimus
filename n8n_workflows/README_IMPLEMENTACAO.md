# Guia de Implementação - Workflows Proativos do Detetive de Dados

Este documento descreve todos os workflows proativos criados para o ecossistema n8n do Biodiagnóstico.

---

## 📥 Arquivos Criados

| Arquivo | Função | Frequência |
|---------|--------|------------|
| `detetive_dados_agent_v5_skills.json` | Agente Principal com 10 ferramentas | Sob demanda |
| `proativo_resumo_matinal.json` | Briefing diário para o gestor | 08:00 (Seg-Sex) |
| `proativo_alerta_perda_critica.json` | Alerta imediato de perdas > R$ 500 | Webhook |
| `proativo_lembrete_qc.json` | Lembrete se não houver QC cadastrado | 14:00 (Seg-Sex) |
| `proativo_relatorio_semanal.json` | Relatório completo da semana | Sexta 17:00 |
| `proativo_monitoramento_continuo.json` | Monitoramento em tempo real | A cada 15 minutos |
| `middleware_sanitizacao_lgpd.json` | Mascarar dados pessoais (LGPD) | Middleware |

---

## 🔧 Configuração Necessária

### 1. Variáveis de Ambiente (n8n)
Configure estas variáveis no n8n (Settings → Variables):

```
SUPABASE_URL=https://sxytwmsjfmxhlcfnuiqm.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
TELEGRAM_CHAT_ID=-1001234567890
N8N_WEBHOOK_URL=https://machadootavio.app.n8n.cloud/webhook/detetive-dados
```

### 2. Credenciais Necessárias

| Credencial | Tipo | Onde Usar |
|------------|------|-----------|
| Google Gemini API | API Key | Agente Principal |
| Telegram Bot API | Bot Token | Todos os alertas |
| HTTP Header Auth | Supabase Key | Workflows proativos |

### 3. Telegram Bot (Opcional mas Recomendado)
1. Fale com @BotFather no Telegram
2. Crie um bot: `/newbot`
3. Copie o Token gerado
4. Adicione o bot ao grupo/canal desejado
5. Pegue o Chat ID do grupo

---

## 📋 Ordem de Importação no n8n

1. **Primeiro**: `detetive_dados_agent_v5_skills.json` (Agente Principal)
2. **Segundo**: `middleware_sanitizacao_lgpd.json` (Middleware LGPD)
3. **Terceiro**: Workflows proativos na ordem desejada

---

## 🎯 O que cada Workflow faz

### 1. Resumo Matinal (08:00)
- Busca divergências das últimas 24h
- Calcula perda total
- Identifica pior convênio
- Envia resumo formatado no Telegram

### 2. Alerta de Perda Crítica
- Recebe webhook quando nova divergência é cadastrada
- Verifica se valor > limite configurado (padrão R$ 500)
- Dispara alerta instantâneo se crítico

### 3. Lembrete de QC (14:00)
- Verifica se há registros de QC do dia
- Se não houver, envia lembrete
- Evita que o laboratório fique sem controle de qualidade

### 4. Relatório Semanal (Sexta 17:00)
- Consolida todos os dados da semana
- Ranking de convênios problemáticos
- Evolução diária
- Envia ao final do expediente

### 5. Monitoramento Contínuo (15 min)
- Verifica novas divergências em tempo real
- Alerta apenas divergências > R$ 200
- Evita "spam" de alertas pequenos

### 6. Sanitização LGPD
- Middleware para mascarar dados pessoais
- Transforma "João da Silva" → "J** d* S****"
- Protege CPF, telefone, email
- Usar antes de enviar dados para Gemini

---

## 🚀 Próximos Passos

1. [ ] Importar todos os workflows no n8n
2. [ ] Configurar credenciais (Gemini, Telegram, Supabase)
3. [ ] Ativar workflows proativos (toggle Active)
4. [ ] Testar com dados de exemplo
5. [ ] Ajustar horários conforme necessidade do laboratório

---

## 📞 Suporte

Dúvidas sobre a implementação? Consulte a documentação das skills:
- `.agent/skills/integracao-ai-oraculo/SKILL.md`
- `.agent/skills/engenharia-prompts-estrategista/SKILL.md`
