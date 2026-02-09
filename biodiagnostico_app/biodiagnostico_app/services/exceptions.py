"""
Exceções customizadas para a camada de serviços
"""


class ServiceError(Exception):
    """Erro levantado quando uma operação no Supabase falha ou retorna dados inesperados."""
    pass
