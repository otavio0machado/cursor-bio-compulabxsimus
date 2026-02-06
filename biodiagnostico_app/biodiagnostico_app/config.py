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
    SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")

    # Auth (login unico)
    AUTH_EMAIL = os.getenv("AUTH_EMAIL", "")
    AUTH_PASSWORD = os.getenv("AUTH_PASSWORD", "")

    @classmethod
    def validate(cls):
        """Valida se todas as configurações estão presentes"""
        missing = []
        if missing:
            raise ValueError(f"Variáveis de ambiente faltando: {', '.join(missing)}")
