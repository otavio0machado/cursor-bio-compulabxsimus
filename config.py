# Configurações do Sistema - Laboratório Biodiagnóstico

# Informações do Laboratório
LAB_INFO = {
    "nome": "Laboratório Biodiagnóstico",
    "nome_curto": "Biodiagnóstico",
    "sistema": "Sistema de Administração",
    "versao": "1.0.0",
    "slogan": "Cuidando da sua saúde há mais de 30 anos",
    "localizacao": "Camaquã e região",
    "certificacao": "Certificação PNCQ Diamante"
}

# Cores do Tema - Paleta oficial do Laboratório Biodiagnóstico
THEME_COLORS = {
    # Cores principais
    "primary": "#1B5E20",       # Verde escuro (cor principal do site)
    "primary_dark": "#0D3D12",  # Verde mais escuro
    "primary_light": "#2E7D32", # Verde médio
    
    # Cores de destaque
    "accent": "#8BC34A",        # Verde limão (destaque do site)
    "accent_light": "#AED581",  # Verde limão claro
    "accent_dark": "#689F38",   # Verde limão escuro
    
    # Cores de fundo
    "background": "#F8FFF8",    # Fundo levemente verde
    "surface": "#FFFFFF",       # Superfície branca
    "card_bg": "#FFFFFF",       # Fundo dos cards
    
    # Cores de texto
    "text_primary": "#1B5E20",  # Texto principal (verde escuro)
    "text_secondary": "#558B2F", # Texto secundário
    "text_light": "#FFFFFF",    # Texto claro (sobre fundo escuro)
    "text_muted": "#81C784",    # Texto suave
    
    # Cores de status
    "success": "#4CAF50",       # Verde sucesso
    "warning": "#FFA726",       # Laranja aviso
    "error": "#EF5350",         # Vermelho erro
    "info": "#66BB6A",          # Verde informação
    
    # Gradientes
    "gradient_start": "#1B5E20", # Início do gradiente
    "gradient_end": "#2E7D32",   # Fim do gradiente
}

# Módulos do Sistema (estrutura para expansão)
MODULES = {
    "analise_faturamento": {
        "nome": "Análise de Faturamento",
        "icone": "📊",
        "descricao": "Análise comparativa COMPULAB vs SIMUS",
        "ativo": True
    },
    "conversor_pdf": {
        "nome": "Conversor PDF → CSV",
        "icone": "🔄",
        "descricao": "Conversão de PDFs para formato CSV",
        "ativo": True
    },
    "relatorios": {
        "nome": "Relatórios",
        "icone": "📄",
        "descricao": "Geração de relatórios detalhados",
        "ativo": False  # Para implementar depois
    },
    "dashboard": {
        "nome": "Dashboard",
        "icone": "📈",
        "descricao": "Visão geral e métricas",
        "ativo": False  # Para implementar depois
    },
    "configuracoes": {
        "nome": "Configurações",
        "icone": "⚙️",
        "descricao": "Configurações do sistema",
        "ativo": False  # Para implementar depois
    }
}


