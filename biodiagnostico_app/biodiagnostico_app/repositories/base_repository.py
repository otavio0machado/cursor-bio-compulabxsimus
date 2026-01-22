from typing import Generic, TypeVar, List, Optional, Dict, Any
from ..services.supabase_client import supabase

T = TypeVar("T")

class BaseRepository(Generic[T]):
    """
    Classe base para repositórios Supabase.
    Centraliza operações de banco de dados conforme skill 'O Arquivista'.
    Implementa o padrão Singleton reutilizando o cliente existente.
    """
    def __init__(self, table_name: str):
        self.table_name = table_name

    @property
    def client(self):
        """Retorna o cliente Supabase Singleton"""
        return supabase

    def get_all(self) -> List[Dict[str, Any]]:
        """Retorna todos os registros da tabela."""
        try:
            response = self.client.table(self.table_name).select("*").execute()
            return response.data
        except Exception as e:
            print(f"Erro ao buscar dados em {self.table_name}: {e}")
            return []

    def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """Retorna um registro pelo ID."""
        try:
            response = self.client.table(self.table_name).select("*").eq("id", id).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"Erro ao buscar ID {id} em {self.table_name}: {e}")
            return None

    def create(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Cria um novo registro."""
        try:
            response = self.client.table(self.table_name).insert(data).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"Erro ao criar registro em {self.table_name}: {e}")
            return None

    def update(self, id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Atualiza um registro existente."""
        try:
            response = self.client.table(self.table_name).update(data).eq("id", id).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"Erro ao atualizar ID {id} em {self.table_name}: {e}")
            return None

    def delete(self, id: str) -> bool:
        """Deleta um registro pelo ID."""
        try:
            # Em alguns casos queremos soft delete, mas o base repository faz delete real.
            # Classes filhas devem sobrescrever se quiserem soft delete.
            self.client.table(self.table_name).delete().eq("id", id).execute()
            return True
        except Exception as e:
            print(f"Erro ao deletar ID {id} em {self.table_name}: {e}")
            return False
