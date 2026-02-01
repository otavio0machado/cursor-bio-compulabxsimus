"""
Componentes de Análise - Módulo de UI para COMPULAB x SIMUS
"""

from .widgets import (
    metric_card_premium,
    insight_card,
    patient_history_modal,
    action_table
)

from .deep_analysis import (
    executive_summary_card,
    difference_breakdown_panel,
    repeated_exams_alert,
    extra_patients_badge,
    analysis_status_banner
)

from .exam_link_modal import exam_link_modal

__all__ = [
    "metric_card_premium",
    "insight_card",
    "patient_history_modal",
    "action_table",
    "executive_summary_card",
    "difference_breakdown_panel",
    "repeated_exams_alert",
    "extra_patients_badge",
    "analysis_status_banner",
    "exam_link_modal",
]
