"""
Serviço de Mapeamento de Exames
Laboratório Biodiagnóstico
"""
from typing import Dict, List, Optional
from .supabase_client import supabase

class MappingService:
    """Gerencia sinônimos e nomes canônicos de exames"""
    
    _cache: Dict[str, str] = {}
    _is_loaded: bool = False

    @classmethod
    async def load_mappings(cls, force: bool = False):
        """Carrega todos os mapeamentos do banco para o cache"""
        if cls._is_loaded and not force:
            return
            
        try:
            response = supabase.table("exam_mappings").select("original_name, canonical_name").execute()
            if response.data:
                cls._cache = {
                    item["original_name"].upper().strip(): item["canonical_name"].strip()
                    for item in response.data
                }
                cls._is_loaded = True
                print(f"DEBUG: MappingService carregou {len(cls._cache)} mapeamentos.")
        except Exception as e:
            print(f"Erro ao carregar mapeamentos de exames: {e}")
            # Se falhar o banco, mantemos o cache vazio (ou poderíamos ter um fallback hardcoded)

    @classmethod
    async def get_canonical_name(cls, original_name: str) -> str:
        """Retorna o nome canônico para um nome original (garante carregamento)"""
        await cls.load_mappings()
        return cls.get_canonical_name_sync(original_name)

    @classmethod
    def get_canonical_name_sync(cls, original_name: str) -> str:
        """Versão síncrona (usa cache). Retorna original se não estiver no cache."""
        if not original_name:
            return ""
        name_upper = original_name.upper().strip()
        return cls._cache.get(name_upper, original_name)

    @classmethod
    async def add_mapping(cls, original_name: str, canonical_name: str):
        """Adiciona um novo mapeamento ao banco e ao cache"""
        try:
            data = {
                "original_name": original_name.upper().strip(),
                "canonical_name": canonical_name.strip()
            }
            supabase.table("exam_mappings").upsert(data, on_conflict="original_name").execute()
            
            # Atualizar cache
            cls._cache[data["original_name"]] = data["canonical_name"]
        except Exception as e:
            print(f"Erro ao adicionar mapeamento: {e}")

    @classmethod
    def get_all_synonyms(cls) -> Dict[str, str]:
        """Retorna todos os sinônimos (para uso em prompts de IA)"""
        return cls._cache

# Singleton para uso simplificado
mapping_service = MappingService()
