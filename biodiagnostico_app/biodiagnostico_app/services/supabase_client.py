"""
Cliente Supabase Singleton
"""
from supabase import create_client, Client
from ..config import Config

class SupabaseClient:
    _instance: Client = None
    
    @classmethod
    def get_client(cls) -> Client:
        """Retorna instância única do cliente Supabase"""
        if cls._instance is None:
            # Config.validate()
            if Config.SUPABASE_URL and Config.SUPABASE_KEY:
                cls._instance = create_client(
                    Config.SUPABASE_URL,
                    Config.SUPABASE_KEY
                )
        return cls._instance

# Atalho
supabase = SupabaseClient.get_client()
