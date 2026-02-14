"""
Cliente Supabase Singleton - inicialização lazy para não falhar em build time.
"""
from supabase import create_client, Client
from ..config import Config


class SupabaseClient:
    _instance: Client = None
    _admin_instance: Client = None

    @classmethod
    def get_client(cls) -> Client:
        """Retorna instância única do cliente Supabase (anon key — respeita RLS)"""
        if cls._instance is None:
            Config.validate()
            if Config.SUPABASE_URL and Config.SUPABASE_KEY:
                cls._instance = create_client(
                    Config.SUPABASE_URL,
                    Config.SUPABASE_KEY,
                )
        return cls._instance

    @classmethod
    def get_admin_client(cls) -> Client:
        """Retorna cliente Supabase com service_role key (ignora RLS).
        Se service_role key não estiver configurada, retorna o client normal."""
        if cls._admin_instance is None:
            Config.validate()
            key = Config.SUPABASE_SERVICE_ROLE_KEY or Config.SUPABASE_KEY
            if Config.SUPABASE_URL and key:
                cls._admin_instance = create_client(
                    Config.SUPABASE_URL,
                    key,
                )
        return cls._admin_instance


class _LazySupabase:
    """Proxy que só inicializa o cliente Supabase no primeiro acesso real."""

    def __getattr__(self, name):
        client = SupabaseClient.get_client()
        if client is None:
            raise RuntimeError(
                "Supabase não configurado. Defina SUPABASE_URL e SUPABASE_KEY."
            )
        return getattr(client, name)


class _LazyAdminSupabase:
    """Proxy para o cliente admin (service_role) do Supabase."""

    def __getattr__(self, name):
        client = SupabaseClient.get_admin_client()
        if client is None:
            raise RuntimeError(
                "Supabase não configurado. Defina SUPABASE_URL e SUPABASE_KEY."
            )
        return getattr(client, name)


# Atalho — lazy: não executa nada no import, só no primeiro uso real
supabase = _LazySupabase()
supabase_admin = _LazyAdminSupabase()
