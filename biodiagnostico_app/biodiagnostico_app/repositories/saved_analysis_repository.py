"""
SavedAnalysisRepository - O Arquivista
Gerencia a persistência de análises salvas no Supabase seguindo o padrão Repository.
"""
from typing import Dict, Any, List, Optional
from datetime import date
from ..services.supabase_client import supabase
from ..schemas.analysis_schemas import SavedAnalysisCreate, AnalysisItemCreate, analysis_to_dict


class SavedAnalysisRepository:
    """Repository para operações de Análises Salvas"""
    
    table_name = "saved_analyses"
    items_table = "analysis_items"

    @staticmethod
    def create(data: SavedAnalysisCreate) -> Optional[Dict[str, Any]]:
        """
        Cria uma nova análise salva.
        Valida dados com Pydantic antes de persistir.
        """
        if not supabase:
            print("ERRO: Cliente Supabase não disponível")
            return None
        
        try:
            # Validar e converter para dict
            db_data = analysis_to_dict(data)
            
            # Calcular diferença
            db_data['difference'] = db_data.get('compulab_total', 0) - db_data.get('simus_total', 0)
            
            response = supabase.table(SavedAnalysisRepository.table_name).insert(db_data).execute()
            
            if response.data:
                print(f"✅ Análise '{data.analysis_name}' salva com sucesso!")
                return response.data[0]
            return None
            
        except Exception as e:
            print(f"❌ Erro ao salvar análise: {e}")
            return None

    @staticmethod
    def get_all(limit: int = 50, order_by: str = "analysis_date") -> List[Dict[str, Any]]:
        """Retorna todas as análises salvas, ordenadas por data."""
        if not supabase:
            return []
        
        try:
            response = supabase.table(SavedAnalysisRepository.table_name)\
                .select("id, analysis_name, analysis_date, compulab_total, simus_total, difference, missing_patients_count, missing_exams_count, divergences_count, status, created_at")\
                .order(order_by, desc=True)\
                .limit(limit)\
                .execute()
            return response.data or []
        except Exception as e:
            print(f"Erro ao buscar análises: {e}")
            return []

    @staticmethod
    def get_by_id(analysis_id: str) -> Optional[Dict[str, Any]]:
        """Retorna uma análise pelo ID com todos os detalhes."""
        if not supabase:
            return None
        
        try:
            response = supabase.table(SavedAnalysisRepository.table_name)\
                .select("*")\
                .eq("id", analysis_id)\
                .single()\
                .execute()
            return response.data
        except Exception as e:
            print(f"Erro ao buscar análise {analysis_id}: {e}")
            return None

    @staticmethod
    def get_by_name_and_date(name: str, analysis_date: date) -> Optional[Dict[str, Any]]:
        """Busca análise por nome e data (único)."""
        if not supabase:
            return None
        
        try:
            response = supabase.table(SavedAnalysisRepository.table_name)\
                .select("*")\
                .eq("analysis_name", name)\
                .eq("analysis_date", analysis_date.isoformat())\
                .execute()
            
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"Erro ao buscar análise '{name}' em {analysis_date}: {e}")
            return None

    @staticmethod
    def search(query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Busca análises por nome (pesquisa parcial)."""
        if not supabase:
            return []
        
        try:
            response = supabase.table(SavedAnalysisRepository.table_name)\
                .select("id, analysis_name, analysis_date, compulab_total, simus_total, status")\
                .ilike("analysis_name", f"%{query}%")\
                .order("analysis_date", desc=True)\
                .limit(limit)\
                .execute()
            return response.data or []
        except Exception as e:
            print(f"Erro na busca: {e}")
            return []

    @staticmethod
    def update(analysis_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Atualiza uma análise existente."""
        if not supabase:
            return None
        
        try:
            # Converter date se presente
            if 'analysis_date' in data and isinstance(data['analysis_date'], date):
                data['analysis_date'] = data['analysis_date'].isoformat()
            
            response = supabase.table(SavedAnalysisRepository.table_name)\
                .update(data)\
                .eq("id", analysis_id)\
                .execute()
            
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"Erro ao atualizar análise {analysis_id}: {e}")
            return None

    @staticmethod
    def delete(analysis_id: str) -> bool:
        """Deleta uma análise e seus itens (cascade)."""
        if not supabase:
            return False
        
        try:
            # Items são deletados automaticamente via ON DELETE CASCADE
            response = supabase.table(SavedAnalysisRepository.table_name)\
                .delete()\
                .eq("id", analysis_id)\
                .execute()
            return bool(response.data)
        except Exception as e:
            print(f"Erro ao deletar análise {analysis_id}: {e}")
            return False

    @staticmethod
    def archive(analysis_id: str) -> bool:
        """Arquiva uma análise (soft delete)."""
        result = SavedAnalysisRepository.update(analysis_id, {"status": "archived"})
        return result is not None

    # ===== Métodos para Items de Análise =====

    @staticmethod
    def add_items(analysis_id: str, items: List[AnalysisItemCreate]) -> int:
        """Adiciona múltiplos itens a uma análise. Retorna quantidade inserida."""
        if not supabase or not items:
            return 0
        
        try:
            data_list = []
            for item in items:
                item_dict = item.dict(exclude_none=True)
                item_dict['analysis_id'] = analysis_id
                data_list.append(item_dict)
            
            response = supabase.table(SavedAnalysisRepository.items_table)\
                .insert(data_list)\
                .execute()
            
            return len(response.data) if response.data else 0
        except Exception as e:
            print(f"Erro ao adicionar itens: {e}")
            return 0

    @staticmethod
    def get_items(analysis_id: str, item_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retorna itens de uma análise, opcionalmente filtrados por tipo."""
        if not supabase:
            return []
        
        try:
            query = supabase.table(SavedAnalysisRepository.items_table)\
                .select("*")\
                .eq("analysis_id", analysis_id)
            
            if item_type:
                query = query.eq("item_type", item_type)
            
            response = query.order("created_at").execute()
            return response.data or []
        except Exception as e:
            print(f"Erro ao buscar itens: {e}")
            return []

    @staticmethod
    def update_item_resolution(item_id: str, is_resolved: bool, notes: str = "") -> bool:
        """Atualiza status de resolução de um item."""
        if not supabase:
            return False
        
        try:
            response = supabase.table(SavedAnalysisRepository.items_table)\
                .update({"is_resolved": is_resolved, "resolution_notes": notes})\
                .eq("id", item_id)\
                .execute()
            return bool(response.data)
        except Exception as e:
            print(f"Erro ao atualizar item {item_id}: {e}")
            return False

    # ===== Métodos de Relatórios =====

    @staticmethod
    def get_monthly_summary(year: int, month: int) -> Optional[Dict[str, Any]]:
        """Retorna resumo das análises de um mês específico."""
        if not supabase:
            return None
        
        try:
            start_date = f"{year}-{month:02d}-01"
            if month == 12:
                end_date = f"{year + 1}-01-01"
            else:
                end_date = f"{year}-{month + 1:02d}-01"
            
            response = supabase.table(SavedAnalysisRepository.table_name)\
                .select("id, analysis_name, analysis_date, compulab_total, simus_total, difference")\
                .gte("analysis_date", start_date)\
                .lt("analysis_date", end_date)\
                .order("analysis_date")\
                .execute()
            
            if not response.data:
                return None
            
            # Calcular totais
            total_compulab = sum(a.get('compulab_total', 0) or 0 for a in response.data)
            total_simus = sum(a.get('simus_total', 0) or 0 for a in response.data)
            
            return {
                "analyses": response.data,
                "count": len(response.data),
                "total_compulab": total_compulab,
                "total_simus": total_simus,
                "total_difference": total_compulab - total_simus
            }
        except Exception as e:
            print(f"Erro ao gerar resumo mensal: {e}")
            return None
