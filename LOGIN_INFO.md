# 🔐 Sistema de Login - Biodiagnóstico

## 📋 Informações de Acesso

O sistema agora possui uma landing page com autenticação. Ao iniciar o aplicativo, você verá uma página de apresentação com um formulário de login.

### 🔑 Credenciais de Acesso

**Usuários Disponíveis:**

1. **Administrador**
   - Usuário: `admin`
   - Senha: `biodiagnostico2024`

2. **Usuário Padrão**
   - Usuário: `usuario`
   - Senha: `lab2024`

3. **Demo/Teste**
   - Usuário: `demo`
   - Senha: `demo123`

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

⚠️ **IMPORTANTE**: As credenciais estão hardcoded no código para desenvolvimento. 

**Para produção, recomenda-se:**
- Usar variáveis de ambiente
- Implementar banco de dados para usuários
- Adicionar hash de senhas
- Implementar sistema de sessões mais robusto

## 📝 Personalização

Para alterar as credenciais, edite o dicionário `LOGIN_CREDENTIALS` no arquivo `app.py`:

```python
LOGIN_CREDENTIALS = {
    "admin": "sua_senha_aqui",
    "usuario": "outra_senha",
    "demo": "senha_demo"
}
```

## 🎨 Landing Page

A landing page inclui:
- ✅ Header com logo e certificação
- ✅ Cards explicativos das funcionalidades
- ✅ Formulário de login estilizado
- ✅ Mensagens de erro amigáveis
- ✅ Dicas de credenciais de teste

---

**Desenvolvido para o Laboratório Biodiagnóstico** 🧬

