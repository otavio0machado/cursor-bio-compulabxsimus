"""
SavedAnalysisService - O Arquivista
Serviço de alto nível para salvar, recuperar e gerenciar análises completas.
Coordena Repository, Cloudinary e validação.
"""
from typing import Dict, Any, List, Optional
from datetime import date, datetime
import asyncio
import base64

from ..repositories.saved_analysis_repository import SavedAnalysisRepository
from ..schemas.analysis_schemas import SavedAnalysisCreate, AnalysisItemCreate
from .cloudinary_service import CloudinaryService


class SavedAnalysisService:
    """Serviço para operações completas de salvamento de análises"""
    
    def __init__(self):
        self.repository = SavedAnalysisRepository
        self.cloudinary = CloudinaryService()

    async def save_complete_analysis(
        self,
        name: str,
        analysis_date: date,
        description: str = "",
        # Arquivos
        compulab_file_url: str = "",
        compulab_file_name: str = "",
        simus_file_url: str = "",
        simus_file_name: str = "",
        # Convertidos
        converted_compulab_url: str = "",
        converted_simus_url: str = "",
        # Relatório
        analysis_report_url: str = "",
        pdf_bytes: bytes = None,
        # Resultados numéricos
        compulab_total: float = 0.0,
        simus_total: float = 0.0,
        missing_patients_count: int = 0,
        missing_patients_total: float = 0.0,
        missing_exams_count: int = 0,
        missing_exams_total: float = 0.0,
        divergences_count: int = 0,
        divergences_total: float = 0.0,
        extra_simus_count: int = 0,
        # Listas de itens
        missing_patients: List[Any] = None,
        missing_exams: List[Any] = None,
        value_divergences: List[Any] = None,
        extra_simus_exams: List[Any] = None,
        # AI
        ai_summary: str = "",
        tags: List[str] = None
    ) -> Dict[str, Any]:
        """
        Salva uma análise completa com todos os detalhes.
        
        Returns:
            dict com 'success', 'analysis_id' e 'message'
        """
        try:
            # 1. Upload do PDF se fornecido em bytes
            report_url = analysis_report_url
            if pdf_bytes and not report_url:
                print("📤 Fazendo upload do relatório PDF...")
                # Criar arquivo temp para upload
                import tempfile
                import os
                
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                    tmp.write(pdf_bytes)
                    tmp_path = tmp.name
                
                loop = asyncio.get_event_loop()
                report_url = await loop.run_in_executor(
                    None,
                    lambda: self.cloudinary.upload_file(tmp_path, resource_type="raw")
                )
                
                # Limpar temp
                try:
                    os.unlink(tmp_path)
                except:
                    pass
            
            # 2. Criar schema validado
            analysis_data = SavedAnalysisCreate(
                analysis_name=name,
                analysis_date=analysis_date,
                description=description,
                compulab_file_url=compulab_file_url or None,
                compulab_file_name=compulab_file_name or None,
                simus_file_url=simus_file_url or None,
                simus_file_name=simus_file_name or None,
                converted_compulab_url=converted_compulab_url or None,
                converted_simus_url=converted_simus_url or None,
                analysis_report_url=report_url or None,
                compulab_total=compulab_total,
                simus_total=simus_total,
                missing_patients_count=missing_patients_count,
                missing_patients_total=missing_patients_total,
                missing_exams_count=missing_exams_count,
                missing_exams_total=missing_exams_total,
                divergences_count=divergences_count,
                divergences_total=divergences_total,
                extra_simus_count=extra_simus_count,
                ai_summary=ai_summary[:500] if ai_summary else None,
                tags=tags,
                status="completed"
            )
            
            # 3. Salvar análise principal
            saved = self.repository.create(analysis_data)
            if not saved:
                return {"success": False, "message": "Erro ao salvar análise no banco de dados"}
            
            analysis_id = saved['id']
            
            # 4. Salvar itens detalhados
            items_count = 0
            
            if missing_patients:
                items = [
                    AnalysisItemCreate(
                        analysis_id=analysis_id,
                        item_type="missing_patient",
                        patient_name=self._get_attr(item, 'patient'),
                        exam_name=self._get_attr(item, 'exam_name'),
                        compulab_value=self._get_float(item, 'value') or self._get_float(item, 'total_value'),
                        exams_count=self._get_int(item, 'exams_count')
                    )
                    for item in missing_patients
                ]
                items_count += self.repository.add_items(analysis_id, items)
            
            if missing_exams:
                items = [
                    AnalysisItemCreate(
                        analysis_id=analysis_id,
                        item_type="missing_exam",
                        patient_name=self._get_attr(item, 'patient'),
                        exam_name=self._get_attr(item, 'exam_name'),
                        compulab_value=self._get_float(item, 'compulab_value') or self._get_float(item, 'value')
                    )
                    for item in missing_exams
                ]
                items_count += self.repository.add_items(analysis_id, items)
            
            if value_divergences:
                items = [
                    AnalysisItemCreate(
                        analysis_id=analysis_id,
                        item_type="divergence",
                        patient_name=self._get_attr(item, 'patient'),
                        exam_name=self._get_attr(item, 'exam_name'),
                        compulab_value=self._get_float(item, 'compulab_value'),
                        simus_value=self._get_float(item, 'simus_value'),
                        difference=self._get_float(item, 'difference')
                    )
                    for item in value_divergences
                ]
                items_count += self.repository.add_items(analysis_id, items)
            
            if extra_simus_exams:
                items = [
                    AnalysisItemCreate(
                        analysis_id=analysis_id,
                        item_type="extra_simus",
                        patient_name=self._get_attr(item, 'patient'),
                        exam_name=self._get_attr(item, 'exam_name'),
                        simus_value=self._get_float(item, 'simus_value') or self._get_float(item, 'value')
                    )
                    for item in extra_simus_exams
                ]
                items_count += self.repository.add_items(analysis_id, items)
            
            print(f"✅ Análise salva: {name} ({analysis_date}) - {items_count} itens")
            
            return {
                "success": True,
                "analysis_id": analysis_id,
                "items_saved": items_count,
                "message": f"Análise '{name}' salva com sucesso!"
            }
            
        except ValueError as e:
            return {"success": False, "message": f"Dados inválidos: {str(e)}"}
        except Exception as e:
            print(f"❌ Erro ao salvar análise: {e}")
            return {"success": False, "message": f"Erro: {str(e)}"}

    def get_saved_analyses(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retorna lista de análises salvas para exibição."""
        analyses = self.repository.get_all(limit=limit)
        
        # Formatar para exibição
        for analysis in analyses:
            if analysis.get('analysis_date'):
                try:
                    dt = datetime.fromisoformat(analysis['analysis_date'].replace('Z', '+00:00'))
                    analysis['formatted_date'] = dt.strftime('%d/%m/%Y')
                except:
                    analysis['formatted_date'] = analysis['analysis_date']
            
            # Formatar valores
            analysis['formatted_compulab'] = f"R$ {analysis.get('compulab_total', 0):,.2f}"
            analysis['formatted_simus'] = f"R$ {analysis.get('simus_total', 0):,.2f}"
            analysis['formatted_difference'] = f"R$ {analysis.get('difference', 0):,.2f}"
        
        return analyses

    def load_analysis(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Carrega uma análise completa com todos os itens."""
        analysis = self.repository.get_by_id(analysis_id)
        if not analysis:
            return None
        
        # Carregar itens por tipo
        analysis['missing_patients'] = self.repository.get_items(analysis_id, "missing_patient")
        analysis['missing_exams'] = self.repository.get_items(analysis_id, "missing_exam")
        analysis['divergences'] = self.repository.get_items(analysis_id, "divergence")
        analysis['extra_simus'] = self.repository.get_items(analysis_id, "extra_simus")
        
        return analysis

    def search_analyses(self, query: str) -> List[Dict[str, Any]]:
        """Busca análises por nome."""
        return self.repository.search(query)

    def delete_analysis(self, analysis_id: str) -> bool:
        """Deleta uma análise permanentemente."""
        return self.repository.delete(analysis_id)

    def archive_analysis(self, analysis_id: str) -> bool:
        """Arquiva uma análise (soft delete)."""
        return self.repository.archive(analysis_id)

    def get_monthly_report(self, year: int, month: int) -> Optional[Dict[str, Any]]:
        """Gera relatório mensal consolidado."""
        return self.repository.get_monthly_summary(year, month)

    # ===== Helpers =====
    
    def _get_attr(self, item: Any, attr: str, default: str = "") -> str:
        """Extrai atributo de dict ou objeto."""
        if isinstance(item, dict):
            return item.get(attr, default)
        return getattr(item, attr, default)

    def _get_float(self, item: Any, attr: str, default: float = 0.0) -> float:
        """Extrai atributo float de dict ou objeto."""
        val = self._get_attr(item, attr, None)
        if val is None:
            return default
        try:
            return float(val)
        except:
            return default

    def _get_int(self, item: Any, attr: str, default: int = 0) -> int:
        """Extrai atributo int de dict ou objeto."""
        val = self._get_attr(item, attr, None)
        if val is None:
            return default
        try:
            return int(val)
        except:
            return default


# Instância singleton do serviço
saved_analysis_service = SavedAnalysisService()
