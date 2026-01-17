# Como Iniciar a Versão Oficial (React + Tailwind)

Esta é a versão oficial da aplicação Biodiagnóstico, construída com **Reflex**, que compila Python para uma aplicação web moderna usando React e Tailwind CSS.

## 🚀 Início Rápido

Para iniciar a aplicação, basta executar o arquivo:

`run_app.bat`

(Dê um duplo clique neste arquivo na pasta raiz)

Ou via terminal:

```bash
.\run_app.bat
```

## 🛠️ Detalhes Técnicos

A aplicação está localizada na pasta `biodiagnostico_app/`.

Para rodar manualmente via terminal:

1. Acesse a pasta do app:
   ```bash
   cd biodiagnostico_app
   ```

2. Execute o comando do Reflex:
   ```bash
   py -m reflex run
   ```

O site estará disponível em: http://localhost:3000

## 🔄 Como Desenvolver (Visualização em Tempo Real)

O Reflex possui um recurso poderoso chamado **Hot Reload**.

1. **Mantenha o app rodando** (`.\run_app.bat` ou `reflex run`).
2. **Faça uma alteração** no código (ex: mude um texto ou cor).
3. **Salve o arquivo** (Ctrl+S).
4. O navegador (http://localhost:3000) atualizará **automaticamente** e quase instantaneamente!

> **Diferença Importante**:
> - **Local (`reflex run`)**: Atualiza automaticamente ao salvar. Use para criar e testar.
> - **Online (`reflex deploy`)**: **NÃO** atualiza ao salvar. Você precisa rodar o comando `deploy` novamente sempre que quiser enviar atualizações para o público.

## 📂 Onde está o Código?

Os arquivos principais que você vai editar estão aqui:

`biodiagnostico_app/`
  └── `biodiagnostico_app/`
       ├── `biodiagnostico_app.py`  (📄 Onde tudo começa: menu e links)
       ├── `state.py`               (🧠 O "cérebro" do app: lógica e variáveis)
       ├── `pages/`                 (📑 As páginas do site: Conversor, Análise, etc)
       └── `components/`            (🧩 Peças reutilizáveis: Sidebar, botões, etc)

**Dica de Aprendizado:** Comece editando o arquivo `biodiagnostico_app.py` para ver mudar o texto da página inicial!

## 📦 Versão Antiga (Streamlit)

A versão antiga (Streamlit) foi movida para a pasta `legacy_streamlit_version/` para evitar conflitos e confusão.
