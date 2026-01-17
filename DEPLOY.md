# 🚀 Guia de Deploy - Reflex (React + Tailwind)

Como sua aplicação agora é construída com **Reflex**, o processo de deploy é diferente do Streamlit. Uma aplicação Reflex consiste em duas partes:
1. **Frontend**: Arquivos estáticos (HTML/CSS/JS) compilados (React).
2. **Backend**: Servidor Python (FastAPI).

Existem duas formas principais de fazer o deploy:

## Opção 1: Reflex Cloud (Recomendado - Mais Fácil)

O Reflex possui seu próprio serviço de hospedagem otimizado.

1. **Instale o CLI do Reflex** (você já tem):
   ```bash
   pip install reflex
   ```

2. **Faça Login na Reflex Cloud**:
   ```bash
   py -m reflex login
   ```

3. **Faça o Deploy**:
   Dentro da pasta `biodiagnostico_app/`:
   ```bash
   py -m reflex deploy
   ```
   Siga as instruções interativas no terminal.

## Opção 2: Self-Hosting (Docker / Railway / Render)

Se preferir hospedar em sua própria infraestrutura ou serviços como Railway/Render:

### Usando Docker (Padrão de Ouro)

1. **Crie um Dockerfile** na raiz de `biodiagnostico_app/`.
   (Eu posso criar isso para você se desejar).

2. **Construa e Rode**:
   ```bash
   docker build -t biodiagnostico .
   docker run -p 3000:3000 -p 8000:8000 biodiagnostico
   ```

### Usando Railway (Excelente Custo-Benefício)

1. Crie um repositório no GitHub com o conteúdo da pasta `biodiagnostico_app`.
2. Conecte sua conta do Railway ao GitHub.
3. O Railway detectará o projeto Python/Nixpacks.
4. Configure as variáveis de ambiente necessárias.
5. Comando de start: `reflex run --env prod`

## 🛠️ Gerando a Build de Produção Localmente

Antes de fazer deploy, é uma boa prática testar a build de produção localmente para garantir que não há erros de compilação.

1. **Vá para a pasta do app**:
   ```bash
   cd biodiagnostico_app
   ```

2. **Exporte o projeto**:
   ```bash
   reflex export
   ```
   Isso criará uma pasta `.zip` (ou pasta de build) contendo o frontend compilado e o backend, pronto para ser enviado para um servidor.

---

**Precisa de ajuda com o Dockerfile ou configuração do Railway?** Basta pedir!
