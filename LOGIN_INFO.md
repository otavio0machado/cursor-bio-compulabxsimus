# 🔐 Sistema de Login - Biodiagnóstico

## 📋 Informações de Acesso

O sistema agora possui uma landing page com autenticação. Ao iniciar o aplicativo, você verá uma página de apresentação com um formulário de login.

### 🔑 Credenciais de Acesso

As credenciais sao definidas via variaveis de ambiente:
- AUTH_EMAIL
- AUTH_PASSWORD

Veja `.env.example` para o formato.

## 🎯 Como Funciona

1. **Ao iniciar o app**, você verá a landing page com:
   - Apresentação do sistema
   - Cards explicativos das funcionalidades
   - Formulário de login

2. **Após fazer login**, você terá acesso a:
   - Conversor PDF → CSV
   - Análise COMPULAB x SIMUS
   - Todas as funcionalidades do sistema

3. **Para sair**, clique no botão "🚪 Sair" na barra lateral

## 🔒 Segurança

As credenciais devem ficar fora do codigo e apenas em variaveis de ambiente.

**Para produção, recomenda-se:**
- Usar variáveis de ambiente
- Implementar banco de dados para usuários
- Adicionar hash de senhas
- Implementar sistema de sessões mais robusto

## 📝 Personalização

Para alterar as credenciais, ajuste AUTH_EMAIL e AUTH_PASSWORD no `.env`
(ou nas variaveis do provedor de deploy).

## 🎨 Landing Page

A landing page inclui:
- ✅ Header com logo e certificação
- ✅ Cards explicativos das funcionalidades
- ✅ Formulário de login estilizado
- ✅ Mensagens de erro amigáveis
- ✅ Dicas de acesso seguro

---

**Desenvolvido para o Laboratório Biodiagnóstico** 🧬