"""
Configurações centralizadas da aplicação
"""
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

class Config:
    """Configurações da aplicação"""

    # Supabase
    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

    # Gemini AI (Voice-to-Form)
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    @classmethod
    def validate(cls):
        """Valida se todas as configurações obrigatórias estão presentes"""
        missing = []
        if not cls.SUPABASE_URL:
            missing.append("SUPABASE_URL")
        if not cls.SUPABASE_KEY:
            missing.append("SUPABASE_KEY")
        if missing:
            import logging
            logging.getLogger(__name__).warning(
                f"Variáveis de ambiente faltando: {', '.join(missing)}"
            )
