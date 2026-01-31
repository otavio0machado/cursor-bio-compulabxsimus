"""
Servico de Mapeamento de Exames
Laboratorio Biodiagnostico
"""
import json
import os
from typing import Dict
from .supabase_client import supabase


class MappingService:
    """Gerencia sinonimos e nomes canonicos de exames."""

    _cache: Dict[str, str] = {}
    _is_loaded: bool = False

    @classmethod
    def _local_file_path(cls) -> str:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        return os.path.join(base_dir, "data", "exam_mappings.json")

    @classmethod
    def _load_local_mappings(cls) -> Dict[str, str]:
        path = cls._local_file_path()
        if not os.path.exists(path):
            return {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            if isinstance(raw, dict):
                return {k.upper().strip(): str(v).strip() for k, v in raw.items() if k}
            if isinstance(raw, list):
                result: Dict[str, str] = {}
                for item in raw:
                    if not isinstance(item, dict):
                        continue
                    original = str(item.get("original_name", "")).upper().strip()
                    canonical = str(item.get("canonical_name", "")).strip()
                    if original and canonical:
                        result[original] = canonical
                return result
        except Exception as e:
            print(f"Erro ao carregar mapeamentos locais: {e}")
        return {}

    @classmethod
    def _save_local_mappings(cls, mappings: Dict[str, str]) -> None:
        path = cls._local_file_path()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        payload = {k: v for k, v in mappings.items()}
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=True)
        except Exception as e:
            print(f"Erro ao salvar mapeamentos locais: {e}")

    @classmethod
    async def load_mappings(cls, force: bool = False):
        """Carrega todos os mapeamentos (Supabase ou fallback local)."""
        if cls._is_loaded and not force:
            return

        loaded = False
        if supabase is not None:
            try:
                response = supabase.table("exam_mappings").select("original_name, canonical_name").execute()
                if response.data is not None:
                    cls._cache = {
                        item["original_name"].upper().strip(): item["canonical_name"].strip()
                        for item in response.data
                        if item.get("original_name") and item.get("canonical_name")
                    }
                    loaded = True
                    print(f"DEBUG: MappingService carregou {len(cls._cache)} mapeamentos.")
            except Exception as e:
                msg = str(e)
                if "exam_mappings" in msg:
                    print("DEBUG: Tabela exam_mappings indisponivel no Supabase. Usando fallback local.")
                else:
                    print(f"Erro ao carregar mapeamentos de exames: {e}")

        if not loaded:
            local = cls._load_local_mappings()
            cls._cache = local
            loaded = True
            if local:
                print(f"DEBUG: MappingService carregou {len(cls._cache)} mapeamentos locais.")
            else:
                print("DEBUG: MappingService sem mapeamentos (local e remoto vazios).")

        cls._is_loaded = loaded

    @classmethod
    async def get_canonical_name(cls, original_name: str) -> str:
        """Retorna o nome canonico para um nome original (garante carregamento)."""
        await cls.load_mappings()
        return cls.get_canonical_name_sync(original_name)

    @classmethod
    def get_canonical_name_sync(cls, original_name: str) -> str:
        """Versao sincrona (usa cache). Retorna original se nao estiver no cache."""
        if not original_name:
            return ""
        name_upper = original_name.upper().strip()
        return cls._cache.get(name_upper, original_name)

    @classmethod
    async def add_mapping(cls, original_name: str, canonical_name: str):
        """Adiciona um novo mapeamento ao banco e ao cache."""
        data = {
            "original_name": original_name.upper().strip(),
            "canonical_name": canonical_name.strip(),
        }
        success = False
        if supabase is not None:
            try:
                supabase.table("exam_mappings").upsert(data, on_conflict="original_name").execute()
                success = True
            except Exception as e:
                msg = str(e)
                if "exam_mappings" in msg:
                    print("DEBUG: Supabase sem exam_mappings. Salvando mapeamento localmente.")
                else:
                    print(f"Erro ao adicionar mapeamento: {e}")

        cls._cache[data["original_name"]] = data["canonical_name"]
        cls._save_local_mappings(cls._cache)
        if not success:
            print("DEBUG: Mapeamento salvo localmente (fallback).")

    @classmethod
    def get_all_synonyms(cls) -> Dict[str, str]:
        """Retorna todos os sinonimos (para uso em prompts de IA)."""
        return cls._cache


# Singleton para uso simplificado
mapping_service = MappingService()
