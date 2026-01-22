import reflex as rx
from typing import List, Dict, Any, Optional
from datetime import datetime
from ..styles import Color
from .auth_state import AuthState

class DashboardState(AuthState):
    """Estado responsável pelas métricas e dados do Dashboard"""
    
    # Estatísticas do Dashboard
    total_qc_today: int = 0
    total_qc_month: int = 0
    qc_approval_rate: float = 0.0
    pending_maintenances: int = 0
    
    # Growth Indicators
    financial_growth_day: float = 2.4
    
    @rx.var
    def goal_progress(self) -> float:
        """Percentual de atingimento da meta (Mock ou baseado em Analysis)"""
        if hasattr(self, 'monthly_goal') and self.monthly_goal > 0:
            current = getattr(self, 'compulab_total', 0)
            return min(100.0, (current / self.monthly_goal) * 100)
        return 0.0

    @rx.var
    def total_patients_count(self) -> int:
        """Total de pacientes analisados (Compulab + Simus distintos ou soma simples)"""
        c = getattr(self, 'compulab_count', 0)
        s = getattr(self, 'simus_count', 0)
        return c + s
    
    @rx.var
    def dashboard_total_today(self) -> str:
        """Total de registros de QC hoje"""
        today = datetime.now().strftime("%Y-%m-%d")
        if not hasattr(self, 'qc_records'): return "0"
        return str(len([r for r in self.qc_records if r.date.startswith(today)]))

    @rx.var
    def dashboard_total_month(self) -> str:
        """Total de registros de QC no mês"""
        today = datetime.now()
        month_str = f"{today.year}-{today.month:02d}"
        if not hasattr(self, 'qc_records'): return "0"
        return str(len([r for r in self.qc_records if r.date.startswith(month_str)]))

    @rx.var
    def dashboard_approval_rate(self) -> float:
        """Taxa de aprovação (CV <= 5%)"""
        if not hasattr(self, 'qc_records') or not self.qc_records: 
            return 100.0
        # Consideramos 'aprovado' se o status for OK
        ok_count = len([r for r in self.qc_records if r.status == "OK"])
        return round((ok_count / len(self.qc_records)) * 100, 1)

    @rx.var
    def has_alerts(self) -> bool:
        """Se há alertas ativos (CV > 5%)"""
        return hasattr(self, 'qc_records_with_alerts') and len(self.qc_records_with_alerts) > 0

    @rx.var
    def dashboard_alerts_count(self) -> str:
        """Contagem de alertas"""
        if not hasattr(self, 'qc_records_with_alerts'): return "0"
        return str(len(self.qc_records_with_alerts))
    
    @rx.var
    def qc_records_with_alerts(self) -> List[Dict[str, Any]]:
        """Retorna registros com alerta para o dashboard"""
        if not hasattr(self, 'qc_records'): return []
        # Retorna dict representation para frontend
        return [r.dict() for r in self.qc_records if r.status != "OK"] 

    @rx.var
    def dashboard_pending_maintenances(self) -> str:
        """Manutenções pendentes"""
        if not hasattr(self, 'maintenance_records'): return "0"
        return str(len(self.maintenance_records))
    
    @rx.var
    def has_pending_maintenances(self) -> bool:
        if not hasattr(self, 'maintenance_records'): return False
        return len(self.maintenance_records) > 0

    @rx.var
    def dashboard_expiring_lots(self) -> str:
        """Lotes vencendo em 30 dias"""
        if not hasattr(self, 'reagent_lots'): return "0"
        return str(len([l for l in self.reagent_lots if l.days_left <= 30]))

    @rx.var
    def has_expiring_lots(self) -> bool:
        return int(self.dashboard_expiring_lots) > 0


    
    @rx.var
    def difference(self) -> float:
        """Diferença entre COMPULAB e SIMUS"""
        compulab = getattr(self, 'compulab_total', 0)
        simus = getattr(self, 'simus_total', 0)
        return compulab - simus
    
    @rx.var
    def formatted_revenue_forecast(self) -> str:
        """Previsão de receita formatada"""
        forecast = getattr(self, 'revenue_forecast', 0)
        return f"R$ {forecast:,.2f}"

    @rx.var
    def formatted_monthly_goal(self) -> str:
        """Meta mensal formatada"""
        goal = getattr(self, 'monthly_goal', 0)
        return f"R$ {goal:,.2f}"
    
    @rx.var
    def difference_percent(self) -> float:
        """Percentual de diferença"""
        simus = getattr(self, 'simus_total', 0)
        if simus > 0:
            return (self.difference / simus) * 100
        return 0.0

    # ===== Dashboard Analytics - Chart Data Aggregators =====
    
    def _safe_get_attr(self, item: Any, key: str, default: Any = "") -> Any:
        """Helper to safely extract attribute from dict or object"""
        if isinstance(item, dict):
            return item.get(key, default)
        return getattr(item, key, default)
    
    def _format_currency_br(self, value: float) -> str:
        """Format value as Brazilian currency"""
        return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    @rx.var
    def revenue_distribution_data(self) -> List[Dict[str, Any]]:
        """Data for pie/donut chart showing composition of revenue leakage"""
        data = []
        
        # Access attributes safely from AnalysisState (via self)
        missing_patients_total = getattr(self, 'missing_patients_total', 0)
        missing_exams_total = getattr(self, 'missing_exams_total', 0)
        divergences_total = getattr(self, 'divergences_total', 0)
        extra_simus_exams = getattr(self, 'extra_simus_exams', [])
        
        # Cores consistentes com o design system (Aspirado)
        if missing_patients_total > 0:
            data.append({
                "name": "Pacientes Faltantes", 
                "value": round(missing_patients_total, 2), 
                "fill": Color.WARNING
            })
        if missing_exams_total > 0:
            data.append({
                "name": "Exames Faltantes", 
                "value": round(missing_exams_total, 2), 
                "fill": Color.ERROR
            })
        if divergences_total > 0:
            data.append({
                "name": "Divergências de Valor", 
                "value": round(divergences_total, 2), 
                "fill": Color.PRIMARY
            })
        
        # Calcular valor dos exames fantasma (extras no SIMUS)
        extras_total = sum(
            float(self._safe_get_attr(item, 'simus_value', 0) or self._safe_get_attr(item, 'value', 0))
            for item in extra_simus_exams
        )
        if extras_total > 0:
            data.append({
                "name": "Extras no SIMUS",
                "value": round(extras_total, 2),
                "fill": Color.TEXT_SECONDARY
            })
        
        # Placeholder quando não há divergências
        if not data:
            data.append({
                "name": "✓ Sem Divergências", 
                "value": 1, 
                "fill": Color.SUCCESS
            })
        
        return data
    
    @rx.var
    def total_revenue_leakage(self) -> float:
        """Total de perda financeira identificada"""
        missing_patients_total = getattr(self, 'missing_patients_total', 0)
        missing_exams_total = getattr(self, 'missing_exams_total', 0)
        divergences_total = getattr(self, 'divergences_total', 0)
        extra_simus_exams = getattr(self, 'extra_simus_exams', [])
        
        extras_total = sum(
            float(self._safe_get_attr(item, 'simus_value', 0) or self._safe_get_attr(item, 'value', 0))
            for item in extra_simus_exams
        )
        return missing_patients_total + missing_exams_total + divergences_total + extras_total
    
    @rx.var
    def formatted_total_leakage(self) -> str:
        """Total de perda formatado em BRL"""
        return self._format_currency_br(self.total_revenue_leakage)
    
    @rx.var
    def top_exams_discrepancy_data(self) -> List[Dict[str, Any]]:
        """Data for bar chart showing top 7 exams contributing to financial impact"""
        exam_values: Dict[str, float] = {}
        
        missing_exams = getattr(self, 'missing_exams', [])
        value_divergences = getattr(self, 'value_divergences', [])
        extra_simus_exams = getattr(self, 'extra_simus_exams', [])
        
        # Agregar valores de exames faltantes
        for item in missing_exams:
            name = str(self._safe_get_attr(item, 'exam_name', ''))
            value = float(self._safe_get_attr(item, 'value', 0) or 0)
            if name:
                exam_values[name] = exam_values.get(name, 0) + value
        
        # Agregar diferenças absolutas de divergências
        for item in value_divergences:
            name = str(self._safe_get_attr(item, 'exam_name', ''))
            diff = float(self._safe_get_attr(item, 'difference', 0) or 0)
            if name:
                exam_values[name] = exam_values.get(name, 0) + abs(diff)
        
        # Agregar valores de exames fantasma
        for item in extra_simus_exams:
            name = str(self._safe_get_attr(item, 'exam_name', ''))
            value = float(self._safe_get_attr(item, 'simus_value', 0) or self._safe_get_attr(item, 'value', 0) or 0)
            if name:
                exam_values[name] = exam_values.get(name, 0) + value
        
        # Ordenar por impacto financeiro e limitar a 7
        sorted_exams = sorted(exam_values.items(), key=lambda x: x[1], reverse=True)[:7]
        
        # Truncar nomes longos para melhor visualização
        return [
            {"name": (name[:18] + "…" if len(name) > 18 else name), "value": round(val, 2)} 
            for name, val in sorted_exams
        ]
    
    @rx.var
    def action_center_insights(self) -> List[Dict[str, str]]:
        """Auto-generated insights and recommended actions with smart priority"""
        insights = []
        
        # Calcular impacto para priorização inteligente
        total_leakage = self.total_revenue_leakage
        
        missing_patients_count = getattr(self, 'missing_patients_count', 0)
        missing_patients_total = getattr(self, 'missing_patients_total', 0)
        missing_exams_count = getattr(self, 'missing_exams_count', 0)
        missing_exams_total = getattr(self, 'missing_exams_total', 0)
        top_offenders = getattr(self, 'top_offenders', [])
        extra_simus_exams_count = getattr(self, 'extra_simus_exams_count', 0)
        
        # Insight 1: Pacientes faltantes (alta prioridade se impacto > 30%)
        if missing_patients_count > 0:
            impact_pct = (missing_patients_total / total_leakage * 100) if total_leakage > 0 else 0
            priority = "high" if impact_pct > 30 or missing_patients_total > 1000 else "medium"
            insights.append({
                "icon": "users",
                "title": f"Verificar {missing_patients_count} pacientes no SIMUS",
                "description": f"Impacto: {self._format_currency_br(missing_patients_total)} ({impact_pct:.1f}% do total)",
                "priority": priority,
                "action_type": "patients_missing"
            })
        
        # Insight 2: Exames faltantes
        if missing_exams_count > 0:
            impact_pct = (missing_exams_total / total_leakage * 100) if total_leakage > 0 else 0
            priority = "high" if missing_exams_count > 10 or impact_pct > 25 else "medium"
            insights.append({
                "icon": "file-warning",
                "title": f"Auditar {missing_exams_count} exames não integrados",
                "description": f"Recuperação potencial: {self._format_currency_br(missing_exams_total)}",
                "priority": priority,
                "action_type": "missing"
            })
        
        # Insight 3: Top Offender (exame mais problemático)
        if top_offenders:
            top = top_offenders[0]
            insights.append({
                "icon": "target",
                "title": f"Revisar exame '{top.name[:25]}'",
                "description": f"Aparece {top.count}x nas divergências. Verifique a tabela TUSS/CBHPM.",
                "priority": "medium",
                "action_type": "divergences"
            })
        
        # Insight 4: Exames fantasma
        if extra_simus_exams_count > 0:
            insights.append({
                "icon": "ghost",
                "title": f"Investigar {extra_simus_exams_count} exames 'fantasma'",
                "description": "Presentes no SIMUS mas não no COMPULAB. Possível duplicidade.",
                "priority": "low",
                "action_type": "extras"
            })
        
        # Estado de sucesso
        if not insights:
            insights.append({
                "icon": "circle-check",
                "title": "Auditoria Perfeita! ✓",
                "description": "Nenhuma divergência significativa identificada entre os sistemas.",
                "priority": "success",
                "action_type": ""
            })
        
        return insights[:4]
