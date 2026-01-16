# 🔒 Segurança da API Key

## ⚠️ IMPORTANTE: Sua chave API foi compartilhada publicamente!

Se você compartilhou sua chave API em um chat, repositório público, ou qualquer lugar acessível, **REVOQUE-A IMEDIATAMENTE** e crie uma nova.

## 🛡️ Como Revogar e Criar Nova Chave

1. Acesse: https://makersuite.google.com/app/apikey
2. Encontre sua chave atual
3. Clique em **"Delete"** ou **"Revoke"**
4. Crie uma nova chave
5. **NÃO compartilhe a nova chave publicamente**

## ✅ Boas Práticas

### ✅ FAÇA:
- ✅ Cole a chave apenas no campo do app Streamlit
- ✅ Use variáveis de ambiente em produção
- ✅ Revogue chaves comprometidas imediatamente
- ✅ Use chaves diferentes para desenvolvimento e produção

### ❌ NÃO FAÇA:
- ❌ Não commite chaves no Git
- ❌ Não compartilhe chaves em chats públicos
- ❌ Não hardcode chaves no código
- ❌ Não compartilhe chaves em repositórios públicos

## 🔐 Uso Seguro no App

A chave deve ser inserida **apenas** no campo da interface do Streamlit:
- A chave fica apenas na sua sessão do navegador
- Não é salva permanentemente
- Não é enviada para o servidor (exceto para a API do Google)

## 📝 Para Produção

Se for fazer deploy público, considere:
1. Usar variáveis de ambiente do Streamlit Cloud
2. Ou criar um sistema de autenticação para usuários
3. Nunca hardcodar chaves no código

---

**Lembre-se**: Chaves API são como senhas. Mantenha-as secretas! 🔐


