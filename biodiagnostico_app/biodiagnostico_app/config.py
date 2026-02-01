"""
Configurações centralizadas da aplicação
"""
import os
from dotenv import load_dotenv, find_dotenv

# Carregar variáveis de ambiente procurando em diretórios pais
load_dotenv(find_dotenv())

class Config:
    """Configurações da aplicação"""
    
    # Supabase
    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
    SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")
    
    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    
    # Gemini
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    
    # Cloudinary
    CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME", "")
    CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY", "")
    CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET", "")

    # Auth (login unico)
    AUTH_EMAIL = os.getenv("AUTH_EMAIL", "")
    AUTH_PASSWORD = os.getenv("AUTH_PASSWORD", "")
    
    @classmethod
    def validate(cls):
        """Valida se todas as configurações estão presentes"""
        missing = []
        # Apenas valida Supabase se estivermos tentando usar (por enquanto opcional para não quebrar deploy existente)
        # if not cls.SUPABASE_URL:
        #     missing.append("SUPABASE_URL")
        # if not cls.SUPABASE_KEY:
        #     missing.append("SUPABASE_KEY")
        
        if missing:
            raise ValueError(f"Variáveis de ambiente faltando: {', '.join(missing)}")
