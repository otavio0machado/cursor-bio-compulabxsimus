"""
Cliente Supabase Singleton - inicialização lazy para não falhar em build time.
"""
from supabase import create_client, Client
from ..config import Config


class SupabaseClient:
    _instance: Client = None

    @classmethod
    def get_client(cls) -> Client:
        """Retorna instância única do cliente Supabase"""
        if cls._instance is None:
            Config.validate()
            if Config.SUPABASE_URL and Config.SUPABASE_KEY:
                cls._instance = create_client(
                    Config.SUPABASE_URL,
                    Config.SUPABASE_KEY,
                )
        return cls._instance


class _LazySupabase:
    """Proxy que só inicializa o cliente Supabase no primeiro acesso real."""

    def __getattr__(self, name):
        client = SupabaseClient.get_client()
        if client is None:
            raise RuntimeError(
                "Supabase não configurado. Defina SUPABASE_URL e SUPABASE_KEY."
            )
        return getattr(client, name)


# Atalho — lazy: não executa nada no import, só no primeiro uso real
supabase = _LazySupabase()
