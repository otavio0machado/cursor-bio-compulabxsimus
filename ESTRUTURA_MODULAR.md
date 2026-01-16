# 🏗️ Estrutura Modular do Sistema

## 📁 Estrutura de Arquivos

```
.
├── app.py                 # Aplicativo principal Streamlit
├── config.py              # Configurações do sistema (cores, módulos, etc)
├── utils/
│   ├── __init__.py        # Inicialização do pacote utils
│   └── ui.py              # Funções de interface (CSS, componentes)
├── requirements.txt        # Dependências Python
└── ESTRUTURA_MODULAR.md   # Este arquivo
```

## 🎨 Sistema de Design

### Cores do Tema
As cores estão definidas em `config.py` no dicionário `THEME_COLORS`:
- **Primary**: Azul principal (#1E88E5)
- **Secondary**: Verde secundário (#43A047)
- **Accent**: Laranja de destaque (#FF6F00)
- **Background**: Fundo claro (#F5F5F5)
- **Surface**: Superfície branca (#FFFFFF)

### Componentes de UI
Os componentes estão em `utils/ui.py`:
- `apply_custom_css()`: Aplica CSS customizado
- `render_header()`: Renderiza header do laboratório
- `render_footer()`: Renderiza footer
- `render_info_box()`: Caixa de informação customizada
- `render_metric_card()`: Card de métrica customizado

## 🔌 Como Adicionar Novos Módulos

### 1. Definir o Módulo em `config.py`

```python
MODULES = {
    # ... módulos existentes ...
    "novo_modulo": {
        "nome": "Nome do Módulo",
        "icone": "🔧",
        "descricao": "Descrição do módulo",
        "ativo": True  # ou False se ainda não implementado
    }
}
```

### 2. Criar Função do Módulo

No `app.py`, adicione uma função para renderizar o módulo:

```python
def render_novo_modulo():
    """Renderiza o novo módulo"""
    st.header("🔧 Nome do Módulo")
    st.markdown("Conteúdo do módulo aqui...")
    # Sua lógica aqui
```

### 3. Adicionar ao Menu de Navegação

Na sidebar, adicione a opção:

```python
page = st.sidebar.radio(
    "Selecione uma seção:",
    [
        "📊 Análise de Faturamento",
        "🔄 Conversor PDF",
        "🔧 Novo Módulo",  # Adicione aqui
        "📈 Dashboard",
        "⚙️ Configurações"
    ],
    label_visibility="collapsed"
)
```

### 4. Adicionar Roteamento

No código principal, adicione o roteamento:

```python
if page == "🔧 Novo Módulo":
    render_novo_modulo()
```

## 🎯 Módulos Planejados

### ✅ Implementados
- **Análise de Faturamento**: Comparação COMPULAB vs SIMUS
- **Conversor PDF**: Conversão de PDFs para CSV

### 🚧 Para Implementar
- **Dashboard**: Visão geral e métricas
- **Relatórios**: Geração de relatórios detalhados
- **Configurações**: Configurações do sistema

## 🎨 Personalização

### Alterar Cores
Edite `config.py`:

```python
THEME_COLORS = {
    "primary": "#SUA_COR_AQUI",
    # ...
}
```

### Alterar Logo/Header
Edite `utils/ui.py`, função `render_header()`:

```python
def render_header():
    header_html = f"""
    <div class="lab-header fade-in">
        <h1>🏥 {LAB_INFO['nome']}</h1>
        <!-- Adicione sua logo aqui -->
        <img src="caminho/para/logo.png" alt="Logo" style="max-width: 200px;">
        <p>{LAB_INFO['sistema']} - Versão {LAB_INFO['versao']}</p>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)
```

## 📝 Boas Práticas

1. **Modularidade**: Mantenha cada módulo em sua própria função
2. **Reutilização**: Use os componentes de UI de `utils/ui.py`
3. **Configuração**: Centralize configurações em `config.py`
4. **Documentação**: Documente novos módulos neste arquivo

## 🚀 Próximos Passos

1. Adicionar logo do laboratório no header
2. Implementar módulo de Dashboard
3. Implementar módulo de Relatórios
4. Adicionar sistema de autenticação (se necessário)
5. Adicionar mais componentes de UI reutilizáveis

---

**Desenvolvido para o Laboratório Biodiagnóstico**


