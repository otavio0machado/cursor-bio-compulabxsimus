"""
Utilitários de Interface - Laboratório Biodiagnóstico
Funções para melhorar a UI do Streamlit
Design baseado na identidade visual oficial do laboratório
"""
import streamlit as st
from config import LAB_INFO, THEME_COLORS

def apply_custom_css():
    """Aplica CSS customizado ao app - Tema Biodiagnóstico"""
    css = f"""
    <style>
        /* Importar fontes do Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;500;600;700&display=swap');
        
        /* ===== CONFIGURAÇÕES GERAIS ===== */
        .main {{
            font-family: 'Open Sans', sans-serif;
            background-color: {THEME_COLORS['background']};
        }}
        
        h1, h2, h3, h4, h5, h6 {{
            font-family: 'Poppins', sans-serif !important;
            color: {THEME_COLORS['primary']} !important;
        }}
        
        /* ===== HEADER BIODIAGNÓSTICO ===== */
        .lab-header {{
            background: linear-gradient(135deg, {THEME_COLORS['gradient_start']} 0%, {THEME_COLORS['gradient_end']} 100%);
            padding: 2rem 2.5rem;
            border-radius: 16px;
            margin-bottom: 2rem;
            color: white;
            box-shadow: 0 8px 32px rgba(27, 94, 32, 0.3);
            position: relative;
            overflow: hidden;
        }}
        
        /* Padrão de fundo (similar ao site) */
        .lab-header::before {{
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-image: 
                radial-gradient(circle at 20% 80%, rgba(139, 195, 74, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(139, 195, 74, 0.1) 0%, transparent 50%);
            pointer-events: none;
        }}
        
        .lab-header-content {{
            position: relative;
            z-index: 1;
        }}
        
        .lab-header .lab-title {{
            color: white !important;
            margin: 0;
            font-weight: 700;
            font-size: 2rem;
            font-family: 'Poppins', sans-serif;
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        
        .lab-header .lab-title .accent {{
            color: {THEME_COLORS['accent']} !important;
        }}
        
        .lab-header .lab-subtitle {{
            color: rgba(255, 255, 255, 0.95);
            margin: 0.5rem 0 0 0;
            font-size: 1rem;
            font-weight: 400;
        }}
        
        .lab-header .certification-badge {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(10px);
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.85rem;
            margin-top: 1rem;
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}
        
        /* ===== CARDS ===== */
        .custom-card {{
            background: {THEME_COLORS['surface']};
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(27, 94, 32, 0.08);
            margin-bottom: 1rem;
            border: 1px solid rgba(27, 94, 32, 0.05);
            transition: all 0.3s ease;
        }}
        
        .custom-card:hover {{
            box-shadow: 0 8px 30px rgba(27, 94, 32, 0.12);
            transform: translateY(-2px);
        }}
        
        /* ===== BOTÕES ===== */
        .stButton > button {{
            border-radius: 25px !important;
            font-weight: 600 !important;
            font-family: 'Poppins', sans-serif !important;
            transition: all 0.3s ease !important;
            border: none !important;
            padding: 0.6rem 1.5rem !important;
        }}
        
        .stButton > button[kind="primary"] {{
            background: linear-gradient(135deg, {THEME_COLORS['accent']} 0%, {THEME_COLORS['accent_dark']} 100%) !important;
            color: white !important;
        }}
        
        .stButton > button:hover {{
            transform: translateY(-3px) !important;
            box-shadow: 0 6px 20px rgba(139, 195, 74, 0.4) !important;
        }}
        
        /* ===== SIDEBAR ===== */
        [data-testid="stSidebar"] {{
            background: {THEME_COLORS['primary']} !important;
            min-width: 256px !important;
        }}
        
        [data-testid="stSidebar"] * {{
            color: white !important;
        }}
        
        [data-testid="stSidebar"] .stMarkdown p,
        [data-testid="stSidebar"] .stMarkdown h1,
        [data-testid="stSidebar"] .stMarkdown h2,
        [data-testid="stSidebar"] .stMarkdown h3 {{
            color: white !important;
        }}
        
        [data-testid="stSidebar"] hr {{
            border-color: rgba(255, 255, 255, 0.2) !important;
            margin: 1rem 0 !important;
        }}
        
        [data-testid="stSidebar"] .stButton > button {{
            background: {THEME_COLORS['accent']} !important;
            color: white !important;
            border: none !important;
        }}
        
        [data-testid="stSidebar"] .stButton > button:hover {{
            background: {THEME_COLORS['accent_light']} !important;
        }}
        
        /* Logo do sidebar */
        .sidebar-logo {{
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 1.5rem 1rem;
            margin-bottom: 0.5rem;
        }}
        
        .sidebar-logo-icon {{
            width: 45px;
            height: 52px;
        }}
        
        .sidebar-logo-text {{
            display: flex;
            flex-direction: column;
        }}
        
        .sidebar-logo-text .lab-name {{
            font-size: 10px;
            letter-spacing: 0.2em;
            text-transform: uppercase;
            opacity: 0.9;
            font-weight: 500;
        }}
        
        .sidebar-logo-text .lab-brand {{
            font-size: 18px;
            font-weight: bold;
            letter-spacing: 0.05em;
        }}
        
        /* Menu sections */
        .sidebar-section-title {{
            font-size: 10px;
            letter-spacing: 0.15em;
            text-transform: uppercase;
            opacity: 0.5;
            font-weight: 600;
            padding: 1rem 1rem 0.5rem 1rem;
            margin: 0;
        }}
        
        /* Menu items */
        .sidebar-menu-item {{
            padding: 0.75rem 1rem;
            margin: 0.25rem 0.5rem;
            border-radius: 0.5rem;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        
        .sidebar-menu-item:hover {{
            background: rgba(255, 255, 255, 0.1) !important;
        }}
        
        .sidebar-menu-item.active {{
            background: {THEME_COLORS['accent']} !important;
        }}
        
        .sidebar-menu-item-icon {{
            font-size: 18px;
        }}
        
        .sidebar-menu-item-text {{
            font-size: 14px;
            font-weight: 500;
        }}
        
        /* Sair button */
        .sidebar-logout {{
            background: rgba(220, 38, 38, 0.6) !important;
            padding: 0.75rem 1rem;
            margin: 0.5rem;
            border-radius: 0.5rem;
            cursor: pointer;
            transition: all 0.2s;
        }}
        
        .sidebar-logout:hover {{
            background: rgba(220, 38, 38, 0.8) !important;
        }}
        
        /* Footer sidebar */
        .sidebar-footer {{
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            padding: 1rem;
            text-align: center;
            margin-top: auto;
            font-size: 12px;
            opacity: 0.5;
        }}
        
        /* ===== MÉTRICAS ===== */
        [data-testid="stMetricValue"] {{
            font-size: 2rem !important;
            font-weight: 700 !important;
            font-family: 'Poppins', sans-serif !important;
            color: {THEME_COLORS['primary']} !important;
        }}
        
        [data-testid="stMetricLabel"] {{
            font-weight: 500 !important;
            color: {THEME_COLORS['text_secondary']} !important;
        }}
        
        [data-testid="stMetricDelta"] svg {{
            display: none;
        }}
        
        /* ===== TABS ===== */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 4px;
            background: {THEME_COLORS['background']};
            padding: 4px;
            border-radius: 12px;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            border-radius: 10px !important;
            padding: 12px 24px !important;
            font-family: 'Poppins', sans-serif !important;
            font-weight: 500 !important;
            background: transparent !important;
            color: {THEME_COLORS['text_secondary']} !important;
        }}
        
        .stTabs [aria-selected="true"] {{
            background: {THEME_COLORS['primary']} !important;
            color: white !important;
        }}
        
        /* ===== EXPANDERS ===== */
        .streamlit-expanderHeader {{
            font-family: 'Poppins', sans-serif !important;
            font-weight: 500 !important;
            color: {THEME_COLORS['primary']} !important;
            background: {THEME_COLORS['background']} !important;
            border-radius: 10px !important;
        }}
        
        /* ===== DATA FRAMES ===== */
        .stDataFrame {{
            border-radius: 12px !important;
            overflow: hidden !important;
        }}
        
        /* ===== FILE UPLOADER ===== */
        [data-testid="stFileUploader"] {{
            background: transparent !important;
            border: none !important;
            border-radius: 16px !important;
            padding: 0 !important;
            margin-top: 0.5rem !important;
        }}
        
        [data-testid="stFileUploader"] > div {{
            background: transparent !important;
            border: none !important;
        }}
        
        [data-testid="stFileUploader"] button {{
            background: {THEME_COLORS['accent']} !important;
            color: white !important;
            border: none !important;
            border-radius: 10px !important;
            padding: 0.6rem 1.2rem !important;
            font-weight: 600 !important;
            font-size: 0.9rem !important;
            transition: all 0.3s ease !important;
        }}
        
        [data-testid="stFileUploader"] button:hover {{
            background: {THEME_COLORS['accent_dark']} !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 12px rgba(139, 195, 74, 0.4) !important;
        }}
        
        /* Cards de upload customizados */
        .upload-card-container {{
            position: relative;
            border: 2px dashed {THEME_COLORS['accent']};
            border-radius: 20px;
            padding: 2.5rem 2rem;
            text-align: center;
            background: linear-gradient(135deg, rgba(139, 195, 74, 0.03) 0%, rgba(76, 175, 80, 0.05) 100%);
            transition: all 0.3s ease;
            min-height: 320px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            gap: 1.5rem;
        }}
        
        .upload-card-container:hover {{
            border-color: {THEME_COLORS['primary']};
            background: linear-gradient(135deg, rgba(139, 195, 74, 0.08) 0%, rgba(76, 175, 80, 0.1) 100%);
            transform: translateY(-4px);
            box-shadow: 0 8px 24px rgba(27, 94, 32, 0.15);
        }}
        
        .upload-card-container.has-file {{
            border-style: solid;
            border-color: {THEME_COLORS['success']};
            background: linear-gradient(135deg, rgba(76, 175, 80, 0.1) 0%, rgba(139, 195, 74, 0.05) 100%);
        }}
        
        .upload-card-icon {{
            filter: drop-shadow(0 4px 8px rgba(0,0,0,0.1));
            transition: transform 0.3s ease;
        }}
        
        .upload-card-container:hover .upload-card-icon {{
            transform: scale(1.05);
        }}
        
        .upload-card-title {{
            color: {THEME_COLORS['primary']};
            font-weight: 700;
            font-size: 1.25rem;
            margin: 0.5rem 0 0.25rem 0;
            font-family: 'Poppins', sans-serif;
        }}
        
        .upload-card-subtitle {{
            color: #666;
            font-size: 0.95rem;
            margin: 0;
        }}
        
        .upload-card-badge {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            margin-top: 1rem;
        }}
        
        .upload-card-badge .file-type {{
            background: #EF5350;
            color: white;
            padding: 0.35rem 0.9rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.5px;
        }}
        
        .upload-card-badge .file-size {{
            color: #666;
            font-size: 0.8rem;
        }}
        
        /* Feature cards melhorados */
        .feature-card {{
            background: white;
            border: 1px solid rgba(139, 195, 74, 0.2);
            border-radius: 16px;
            padding: 1.5rem;
            text-align: center;
            transition: all 0.3s ease;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            gap: 0.75rem;
        }}
        
        .feature-card:hover {{
            border-color: {THEME_COLORS['accent']};
            box-shadow: 0 8px 24px rgba(139, 195, 74, 0.15);
            transform: translateY(-4px);
        }}
        
        .feature-card-icon {{
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, {THEME_COLORS['accent']}15 0%, {THEME_COLORS['accent']}25 100%);
            border-radius: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }}
        
        .feature-card-title {{
            color: {THEME_COLORS['primary']};
            font-weight: 700;
            font-size: 1rem;
            margin: 0;
            font-family: 'Poppins', sans-serif;
        }}
        
        .feature-card-desc {{
            color: #666;
            font-size: 0.85rem;
            margin: 0;
            line-height: 1.4;
        }}
        
        /* Page header melhorado */
        .page-header {{
            margin-bottom: 2rem;
        }}
        
        .page-header-cert-badge {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            background: white;
            border: 1px solid rgba(0,0,0,0.1);
            padding: 0.6rem 1.2rem;
            border-radius: 25px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            margin-bottom: 1.5rem;
        }}
        
        .page-header-title {{
            color: {THEME_COLORS['primary']} !important;
            font-size: 2.75rem !important;
            font-weight: 800 !important;
            margin: 0.5rem 0 !important;
            font-family: 'Poppins', sans-serif !important;
            line-height: 1.2 !important;
        }}
        
        .page-header-subtitle {{
            color: #666 !important;
            font-size: 1.125rem !important;
            margin: 0.5rem 0 2rem 0 !important;
            font-weight: 400 !important;
        }}
        
        /* Radio buttons do sidebar melhorados */
        [data-testid="stRadio"] {{
            background: transparent !important;
        }}
        
        [data-testid="stRadio"] > div {{
            gap: 0.5rem !important;
        }}
        
        [data-testid="stRadio"] label {{
            padding: 0.75rem 1rem !important;
            border-radius: 10px !important;
            transition: all 0.2s ease !important;
            font-weight: 500 !important;
        }}
        
        [data-testid="stRadio"] label:hover {{
            background: rgba(255, 255, 255, 0.1) !important;
        }}
        
        [data-testid="stRadio"] input:checked + label {{
            background: {THEME_COLORS['accent']} !important;
            color: white !important;
        }}
        
        /* Melhorias gerais */
        .main .block-container {{
            padding-top: 3rem !important;
            padding-bottom: 3rem !important;
        }}
        
        /* Métricas melhoradas */
        [data-testid="stMetricValue"] {{
            font-family: 'Poppins', sans-serif !important;
        }}
        
        /* Tabelas melhoradas */
        .stDataFrame {{
            border: 1px solid rgba(139, 195, 74, 0.2) !important;
        }}
        
        /* ===== INFO BOXES ===== */
        .stAlert {{
            border-radius: 12px !important;
            border: none !important;
        }}
        
        /* ===== FOOTER ===== */
        .lab-footer {{
            text-align: center;
            padding: 2rem;
            background: linear-gradient(135deg, {THEME_COLORS['gradient_start']} 0%, {THEME_COLORS['gradient_end']} 100%);
            border-radius: 16px;
            color: white;
            margin-top: 3rem;
        }}
        
        .lab-footer p {{
            margin: 0.3rem 0;
            color: rgba(255, 255, 255, 0.9);
        }}
        
        .lab-footer .footer-brand {{
            font-family: 'Poppins', sans-serif;
            font-weight: 600;
            font-size: 1.1rem;
            color: white;
        }}
        
        /* ===== BADGES ===== */
        .badge {{
            display: inline-block;
            padding: 0.3rem 0.9rem;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            font-family: 'Poppins', sans-serif;
            background: linear-gradient(135deg, {THEME_COLORS['accent']} 0%, {THEME_COLORS['accent_dark']} 100%);
            color: white;
        }}
        
        .badge-outline {{
            background: transparent;
            border: 2px solid {THEME_COLORS['accent']};
            color: {THEME_COLORS['accent']};
        }}
        
        /* ===== ANIMAÇÕES ===== */
        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        @keyframes pulse {{
            0%, 100% {{
                opacity: 1;
            }}
            50% {{
                opacity: 0.7;
            }}
        }}
        
        .fade-in {{
            animation: fadeInUp 0.6s ease-out;
        }}
        
        .pulse {{
            animation: pulse 2s ease-in-out infinite;
        }}
        
        /* ===== SCROLLBAR PERSONALIZADA ===== */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: {THEME_COLORS['background']};
            border-radius: 4px;
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: {THEME_COLORS['accent']};
            border-radius: 4px;
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: {THEME_COLORS['accent_dark']};
        }}
        
        /* ===== SPINNER/LOADING ===== */
        .stSpinner > div {{
            border-top-color: {THEME_COLORS['accent']} !important;
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def render_header():
    """Renderiza o header do laboratório com design oficial moderno"""
    header_html = f"""
    <div class="lab-header fade-in">
        <div class="lab-header-content">
            <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 10px;">
                <div style="font-size: 2.5rem;">🧬</div>
                <div>
                    <h1 class="lab-title" style="margin: 0; display: flex; align-items: baseline; gap: 5px;">
                        <span>Laboratório</span> 
                        <span class="accent" style="color: {THEME_COLORS['accent']} !important;">Biodiagnóstico</span>
                    </h1>
                </div>
            </div>
            <p class="lab-subtitle">{LAB_INFO['sistema']} • {LAB_INFO['localizacao']}</p>
            <div class="certification-badge" style="margin-top: 1rem;">
                <span>🏆</span>
                <span>{LAB_INFO['certificacao']}</span>
            </div>
        </div>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)

def render_footer():
    """Renderiza o footer do laboratório"""
    footer_html = f"""
    <div class="lab-footer fade-in">
        <p class="footer-brand">🧬 {LAB_INFO['nome']}</p>
        <p>{LAB_INFO['slogan']}</p>
        <p style="font-size: 0.85rem; margin-top: 1rem;">
            © 2025 {LAB_INFO['nome']} - Todos os direitos reservados
        </p>
        <p style="font-size: 0.8rem; opacity: 0.8;">
            Sistema de Administração v{LAB_INFO['versao']}
        </p>
    </div>
    """
    st.markdown(footer_html, unsafe_allow_html=True)

def render_module_card(module_key, module_info):
    """Renderiza um card de módulo"""
    if not module_info.get('ativo', False):
        return
    
    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown(f"### {module_info['icone']}")
    with col2:
        st.markdown(f"**{module_info['nome']}**")
        st.caption(module_info['descricao'])
    
    st.markdown("---")

def create_sidebar_menu():
    """Cria o menu lateral"""
    st.sidebar.markdown(f"## 🏥 {LAB_INFO['nome_curto']}")
    st.sidebar.markdown("---")
    
    # Menu de navegação
    st.sidebar.markdown("### 📋 Menu")
    
    # Páginas disponíveis
    page = st.sidebar.radio(
        "Selecione uma seção:",
        ["📊 Análise de Faturamento", "🔄 Conversor PDF", "📈 Dashboard", "⚙️ Configurações"],
        label_visibility="collapsed"
    )
    
    return page

def render_info_box(title, content, icon="ℹ️", type="info"):
    """Renderiza uma caixa de informação com estilo Biodiagnóstico"""
    colors = {
        "info": THEME_COLORS['accent'],
        "success": THEME_COLORS['success'],
        "warning": THEME_COLORS['warning'],
        "error": THEME_COLORS['error']
    }
    
    bg_colors = {
        "info": "rgba(139, 195, 74, 0.1)",
        "success": "rgba(76, 175, 80, 0.1)",
        "warning": "rgba(255, 167, 38, 0.1)",
        "error": "rgba(239, 83, 80, 0.1)"
    }
    
    box_html = f"""
    <div style="
        background: {bg_colors.get(type, bg_colors['info'])};
        border-left: 4px solid {colors.get(type, THEME_COLORS['accent'])};
        padding: 1rem 1.25rem;
        border-radius: 0 12px 12px 0;
        margin: 1rem 0;
        font-family: 'Open Sans', sans-serif;
    ">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.5rem;">
            <span style="font-size: 1.2rem;">{icon}</span>
            <strong style="color: {THEME_COLORS['primary']}; font-family: 'Poppins', sans-serif;">{title}</strong>
        </div>
        <p style="margin: 0; color: {THEME_COLORS['text_secondary']}; font-size: 0.95rem; line-height: 1.5;">{content}</p>
    </div>
    """
    st.markdown(box_html, unsafe_allow_html=True)

def render_metric_card(title, value, delta=None, icon="📊", color=None):
    """Renderiza um card de métrica customizado com estilo Biodiagnóstico"""
    delta_html = ""
    if delta:
        delta_color = THEME_COLORS['success'] if delta >= 0 else THEME_COLORS['error']
        delta_icon = "↑" if delta >= 0 else "↓"
        delta_html = f'<span style="color: {delta_color}; font-size: 0.9rem; font-weight: 600;">{delta_icon} {abs(delta):.2f}%</span>'
    
    main_color = color if color else THEME_COLORS['primary']
    
    card_html = f"""
    <div class="custom-card" style="
        background: linear-gradient(135deg, {THEME_COLORS['surface']} 0%, {THEME_COLORS['background']} 100%);
        border-top: 4px solid {main_color};
    ">
        <div style="display: flex; align-items: center; gap: 1rem;">
            <div style="
                font-size: 2.5rem;
                background: {main_color}15;
                padding: 0.75rem;
                border-radius: 12px;
            ">{icon}</div>
            <div style="flex: 1;">
                <p style="margin: 0; color: {THEME_COLORS['text_secondary']}; font-size: 0.85rem; font-family: 'Poppins', sans-serif; text-transform: uppercase; letter-spacing: 0.5px;">{title}</p>
                <p style="margin: 0.25rem 0 0 0; font-size: 1.75rem; font-weight: 700; color: {main_color}; font-family: 'Poppins', sans-serif;">{value}</p>
                {delta_html}
            </div>
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

def render_stats_row(stats):
    """Renderiza uma linha de estatísticas com estilo Biodiagnóstico
    
    Args:
        stats: lista de dicionários com keys: title, value, icon, color (opcional)
    """
    cols = st.columns(len(stats))
    for i, stat in enumerate(stats):
        with cols[i]:
            render_metric_card(
                title=stat.get('title', ''),
                value=stat.get('value', ''),
                icon=stat.get('icon', '📊'),
                color=stat.get('color', THEME_COLORS['primary'])
            )

def render_section_header(title, subtitle=None, icon="📋"):
    """Renderiza um cabeçalho de seção estilizado"""
    subtitle_html = f'<p style="margin: 0.5rem 0 0 0; color: {THEME_COLORS["text_secondary"]}; font-size: 0.95rem;">{subtitle}</p>' if subtitle else ''
    
    header_html = f"""
    <div style="
        margin: 2rem 0 1.5rem 0;
        padding-bottom: 1rem;
        border-bottom: 2px solid {THEME_COLORS['accent']}30;
    ">
        <div style="display: flex; align-items: center; gap: 12px;">
            <span style="
                font-size: 1.5rem;
                background: {THEME_COLORS['accent']}20;
                padding: 0.5rem;
                border-radius: 10px;
            ">{icon}</span>
            <div>
                <h2 style="margin: 0; color: {THEME_COLORS['primary']}; font-family: 'Poppins', sans-serif; font-size: 1.5rem;">{title}</h2>
                {subtitle_html}
            </div>
        </div>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)

def render_status_badge(text, status="info"):
    """Renderiza um badge de status"""
    colors = {
        "info": THEME_COLORS['accent'],
        "success": THEME_COLORS['success'],
        "warning": THEME_COLORS['warning'],
        "error": THEME_COLORS['error'],
        "primary": THEME_COLORS['primary']
    }
    
    badge_html = f"""
    <span style="
        display: inline-block;
        padding: 0.3rem 0.9rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        font-family: 'Poppins', sans-serif;
        background: {colors.get(status, THEME_COLORS['accent'])};
        color: white;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    ">{text}</span>
    """
    return badge_html

def render_welcome_message():
    """Renderiza mensagem de boas-vindas"""
    welcome_html = f"""
    <div style="
        background: linear-gradient(135deg, {THEME_COLORS['primary']}10 0%, {THEME_COLORS['accent']}10 100%);
        padding: 1.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        border: 1px solid {THEME_COLORS['accent']}30;
    ">
        <h3 style="margin: 0 0 0.5rem 0; color: {THEME_COLORS['primary']}; font-family: 'Poppins', sans-serif;">
            👋 Bem-vindo ao Sistema de Administração
        </h3>
        <p style="margin: 0; color: {THEME_COLORS['text_secondary']}; line-height: 1.6;">
            Utilize o menu lateral para navegar pelas funcionalidades. 
            Faça upload dos arquivos PDF ou CSV para começar a análise de faturamento.
        </p>
    </div>
    """
    st.markdown(welcome_html, unsafe_allow_html=True)

def render_sidebar_logo():
    """Renderiza o logo do sidebar com ícone de tubos de ensaio"""
    logo_html = """
    <div style="
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 1.5rem 1rem;
        margin-bottom: 0.5rem;
    ">
        <svg viewBox="0 0 60 70" width="45" height="52">
            <path d="M20 5 L40 5 L40 25 L55 60 Q57 65 52 68 L8 68 Q3 65 5 60 L20 25 Z" 
                  fill="#4CAF50" stroke="#8BC34A" stroke-width="2"/>
            <rect x="18" y="2" width="24" height="6" rx="2" fill="#4CAF50" stroke="#8BC34A" stroke-width="1"/>
            <circle cx="25" cy="45" r="3" fill="#FFD54F"/>
            <circle cx="35" cy="50" r="2.5" fill="#FFD54F"/>
            <circle cx="30" cy="55" r="2" fill="#FFD54F"/>
            <circle cx="22" cy="52" r="1.5" fill="#FFD54F"/>
        </svg>
        <div style="display: flex; flex-direction: column;">
            <span style="color: rgba(255,255,255,0.9); font-size: 10px; letter-spacing: 0.2em; text-transform: uppercase; font-weight: 500; line-height: 1;">LABORATÓRIO</span>
            <span style="color: white; font-size: 18px; font-weight: bold; letter-spacing: 0.05em; line-height: 1.2;">BIODIAGNÓSTICO</span>
        </div>
    </div>
    """
    st.sidebar.markdown(logo_html, unsafe_allow_html=True)

def render_upload_card(title, subtitle, icon_svg, file_uploader_key, file_obj):
    """Renderiza um card de upload estilizado com SVG"""
    has_file = file_obj is not None
    border_style = "solid" if has_file else "dashed"
    bg_style = "rgba(76, 175, 80, 0.1)" if has_file else "transparent"
    
    card_html = f"""
    <div style="
        border: 2px {border_style} {THEME_COLORS['accent']};
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        background: {bg_style};
        transition: all 0.3s;
        min-height: 250px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        gap: 1rem;
    ">
        {icon_svg}
        <div>
            <h4 style="margin: 0.5rem 0 0.25rem 0; color: {THEME_COLORS['primary']}; font-weight: bold; font-size: 1.1rem;">
                {title}
            </h4>
            <p style="margin: 0; color: #666; font-size: 0.9rem;">
                {subtitle}
            </p>
        </div>
        <div style="display: flex; gap: 0.5rem; align-items: center; margin-top: 0.5rem;">
            <span style="background: #EF5350; color: white; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.75rem; font-weight: 600;">
                PDF
            </span>
            <span style="color: #666; font-size: 0.75rem;">
                Máx. 50MB
            </span>
        </div>
    </div>
    """
    return card_html

def get_erlenmeyer_svg():
    """SVG do Erlenmeyer (COMPULAB) - ID único para evitar conflitos"""
    import uuid
    grad_id = f"liquidGrad_{uuid.uuid4().hex[:8]}"
    return f"""
    <svg viewBox="0 0 80 100" width="70" height="88" style="filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1)); display: block; margin: 0 auto;">
        <defs>
            <linearGradient id="{grad_id}" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" style="stop-color:#81C784;stop-opacity:0.3" />
                <stop offset="100%" style="stop-color:#4CAF50;stop-opacity:0.5" />
            </linearGradient>
        </defs>
        <path d="M28 10 L52 10 L52 35 L70 85 Q72 92 65 95 L15 95 Q8 92 10 85 L28 35 Z" 
              fill="url(#{grad_id})" stroke="#1B5E20" stroke-width="2.5"/>
        <rect x="26" y="5" width="28" height="8" rx="3" fill="none" stroke="#1B5E20" stroke-width="2.5"/>
        <ellipse cx="40" cy="75" rx="20" ry="8" fill="#4CAF50" opacity="0.2"/>
        <circle cx="48" cy="60" r="4" fill="#4CAF50" opacity="0.6">
            <animate attributeName="cy" values="60;55;60" dur="2s" repeatCount="indefinite"/>
        </circle>
        <circle cx="35" cy="68" r="3" fill="#4CAF50" opacity="0.4">
            <animate attributeName="cy" values="68;62;68" dur="1.5s" repeatCount="indefinite"/>
        </circle>
    </svg>
    """

def get_tubes_svg():
    """SVG dos Tubos de ensaio (SIMUS) - ID único para evitar conflitos"""
    import uuid
    grad_id = f"tubeGrad_{uuid.uuid4().hex[:8]}"
    return f"""
    <svg viewBox="0 0 100 100" width="70" height="88" style="filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1)); display: block; margin: 0 auto;">
        <defs>
            <linearGradient id="{grad_id}" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" style="stop-color:#81C784;stop-opacity:0.2" />
                <stop offset="100%" style="stop-color:#4CAF50;stop-opacity:0.5" />
            </linearGradient>
        </defs>
        <!-- Tubo 1 -->
        <rect x="18" y="15" width="15" height="68" rx="7" fill="none" stroke="#1B5E20" stroke-width="2.5"/>
        <rect x="18" y="52" width="15" height="31" rx="7" fill="url(#{grad_id})"/>
        <!-- Tubo 2 -->
        <rect x="42" y="15" width="15" height="68" rx="7" fill="none" stroke="#1B5E20" stroke-width="2.5"/>
        <rect x="42" y="42" width="15" height="41" rx="7" fill="url(#{grad_id})"/>
        <!-- Tubo 3 -->
        <rect x="66" y="15" width="15" height="68" rx="7" fill="none" stroke="#1B5E20" stroke-width="2.5"/>
        <rect x="66" y="58" width="15" height="25" rx="7" fill="url(#{grad_id})"/>
        <!-- Upload badge -->
        <circle cx="81" cy="75" r="10" fill="#4CAF50">
            <animate attributeName="r" values="10;11;10" dur="1.5s" repeatCount="indefinite"/>
        </circle>
        <path d="M81 72 L81 78 M78 75 L81 72 L84 75" stroke="white" stroke-width="2" fill="none" stroke-linecap="round"/>
    </svg>
    """
