import reflex as rx
from typing import List, Dict, Any
from datetime import datetime
from .auth_state import AuthState


class DashboardState(AuthState):
    """Estado responsável pelas métricas do Dashboard de Controle de Qualidade"""

    # Estatísticas do Dashboard
    total_qc_today: int = 0
    total_qc_month: int = 0
    qc_approval_rate: float = 0.0
    pending_maintenances: int = 0

    @rx.var
    def dashboard_total_today(self) -> str:
        """Total de registros de QC hoje"""
        today = datetime.now().strftime("%Y-%m-%d")
        if not hasattr(self, 'qc_records'):
            return "0"
        return str(len([r for r in self.qc_records if r.date.startswith(today)]))

    @rx.var
    def dashboard_total_month(self) -> str:
        """Total de registros de QC no mês"""
        today = datetime.now()
        month_str = f"{today.year}-{today.month:02d}"
        if not hasattr(self, 'qc_records'):
            return "0"
        return str(len([r for r in self.qc_records if r.date.startswith(month_str)]))

    @rx.var
    def dashboard_approval_rate(self) -> float:
        """Taxa de aprovação (status OK)"""
        if not hasattr(self, 'qc_records') or not self.qc_records:
            return 100.0
        ok_count = len([r for r in self.qc_records if r.status == "OK"])
        return round((ok_count / len(self.qc_records)) * 100, 1)

    @rx.var
    def has_alerts(self) -> bool:
        """Se há alertas ativos (CV acima do threshold)"""
        return len(self.qc_records_with_alerts) > 0

    @rx.var
    def dashboard_alerts_count(self) -> str:
        """Contagem de alertas"""
        return str(len(self.qc_records_with_alerts))

    @rx.var
    def qc_records_with_alerts(self) -> List[Dict[str, Any]]:
        """Registros com alerta (apenas status != OK, definido por regras Westgard/CV no momento do registro)"""
        if not hasattr(self, 'qc_records'):
            return []
        return [r.dict() for r in self.qc_records if r.status != "OK"]

    @rx.var
    def dashboard_pending_maintenances(self) -> str:
        """Manutenções pendentes"""
        if not hasattr(self, 'maintenance_records'):
            return "0"
        return str(len(self.maintenance_records))

    @rx.var
    def has_pending_maintenances(self) -> bool:
        if not hasattr(self, 'maintenance_records'):
            return False
        return len(self.maintenance_records) > 0

    @rx.var
    def dashboard_expiring_lots(self) -> str:
        """Lotes vencendo em 30 dias"""
        if not hasattr(self, 'reagent_lots'):
            return "0"
        return str(len([lot for lot in self.reagent_lots if lot.days_left <= 30]))

    @rx.var
    def has_expiring_lots(self) -> bool:
        return int(self.dashboard_expiring_lots) > 0

    @rx.var
    def westgard_violations_month(self) -> str:
        """Contagem de registros com violações Westgard no mês"""
        if not hasattr(self, 'qc_records'):
            return "0"
        today = datetime.now()
        month_str = f"{today.year}-{today.month:02d}"
        count = len([
            r for r in self.qc_records
            if r.date.startswith(month_str) and r.westgard_violations
        ])
        return str(count)

    @rx.var
    def recent_qc_records(self) -> List[Dict[str, Any]]:
        """Últimos 10 registros QC para tabela do dashboard"""
        if not hasattr(self, 'qc_records'):
            return []
        sorted_records = sorted(self.qc_records, key=lambda r: r.date, reverse=True)[:10]
        return [r.dict() for r in sorted_records]

    @rx.var
    def top_high_cv_exams(self) -> List[Dict[str, Any]]:
        """Top 5 exames com maior CV% médio"""
        if not hasattr(self, 'qc_records') or not self.qc_records:
            return []
        exam_cvs: Dict[str, List[float]] = {}
        for r in self.qc_records:
            if r.exam_name and r.cv > 0:
                if r.exam_name not in exam_cvs:
                    exam_cvs[r.exam_name] = []
                exam_cvs[r.exam_name].append(r.cv)

        exam_avg = [
            {"exam_name": name, "avg_cv": round(sum(cvs) / len(cvs), 2), "count": len(cvs)}
            for name, cvs in exam_cvs.items()
        ]
        exam_avg.sort(key=lambda x: x["avg_cv"], reverse=True)
        return exam_avg[:5]
