"""
Testes unitários para WestgardService e cálculos de CV%
"""
import pytest
from biodiagnostico_app.models import QCRecord
from biodiagnostico_app.services.westgard_service import WestgardService


def make_record(value: float, target: float, sd: float, **kwargs) -> QCRecord:
    """Helper para criar QCRecord de teste"""
    return QCRecord(
        id=kwargs.get("id", "test"),
        date=kwargs.get("date", "2025-01-01T10:00:00"),
        exam_name=kwargs.get("exam_name", "GLICOSE"),
        level="Normal",
        value=value,
        target_value=target,
        target_sd=sd,
        cv=abs(value - target) / target * 100 if target > 0 else 0.0,
        status="OK",
    )


# === Testes de CV% ===

class TestCVCalculation:
    """Testes para cálculo de Coeficiente de Variação"""

    def test_cv_zero_when_value_equals_target(self):
        r = make_record(value=100.0, target=100.0, sd=5.0)
        assert r.cv == 0.0

    def test_cv_positive_when_value_above_target(self):
        r = make_record(value=105.0, target=100.0, sd=5.0)
        assert r.cv == pytest.approx(5.0)

    def test_cv_positive_when_value_below_target(self):
        r = make_record(value=95.0, target=100.0, sd=5.0)
        assert r.cv == pytest.approx(5.0)

    def test_cv_large_deviation(self):
        r = make_record(value=120.0, target=100.0, sd=5.0)
        assert r.cv == pytest.approx(20.0)

    def test_cv_zero_target_returns_zero(self):
        r = make_record(value=100.0, target=0.0, sd=5.0)
        assert r.cv == 0.0

    def test_cv_small_values(self):
        r = make_record(value=0.52, target=0.50, sd=0.02)
        assert r.cv == pytest.approx(4.0)


# === Testes de Westgard ===

class TestWestgardNoViolation:
    """Testes onde nenhuma regra é violada"""

    def test_normal_value_no_violations(self):
        current = make_record(value=101.0, target=100.0, sd=5.0)
        violations = WestgardService.check_rules(current, [])
        assert len(violations) == 0

    def test_value_within_1sd_no_violations(self):
        current = make_record(value=104.0, target=100.0, sd=5.0)
        violations = WestgardService.check_rules(current, [])
        assert len(violations) == 0

    def test_sd_zero_returns_empty(self):
        current = make_record(value=105.0, target=100.0, sd=0.0)
        violations = WestgardService.check_rules(current, [])
        assert len(violations) == 0


class TestWestgard1_2s:
    """Testes para regra 1-2s (alerta)"""

    def test_value_above_2sd_triggers_warning(self):
        current = make_record(value=111.0, target=100.0, sd=5.0)  # z=2.2
        violations = WestgardService.check_rules(current, [])
        rules = [v["rule"] for v in violations]
        assert "1-2s" in rules
        assert all(v["severity"] in ("warning", "rejection") for v in violations if v["rule"] == "1-2s")

    def test_value_below_minus_2sd_triggers_warning(self):
        current = make_record(value=89.0, target=100.0, sd=5.0)  # z=-2.2
        violations = WestgardService.check_rules(current, [])
        rules = [v["rule"] for v in violations]
        assert "1-2s" in rules


class TestWestgard1_3s:
    """Testes para regra 1-3s (rejeição)"""

    def test_value_above_3sd_triggers_rejection(self):
        current = make_record(value=116.0, target=100.0, sd=5.0)  # z=3.2
        violations = WestgardService.check_rules(current, [])
        rules = [v["rule"] for v in violations]
        assert "1-3s" in rules
        rejection = next(v for v in violations if v["rule"] == "1-3s")
        assert rejection["severity"] == "rejection"

    def test_value_below_minus_3sd_triggers_rejection(self):
        current = make_record(value=84.0, target=100.0, sd=5.0)  # z=-3.2
        violations = WestgardService.check_rules(current, [])
        rules = [v["rule"] for v in violations]
        assert "1-3s" in rules


class TestWestgard2_2s:
    """Testes para regra 2-2s (rejeição por erro sistemático)"""

    def test_two_consecutive_above_2sd(self):
        prev = make_record(value=111.0, target=100.0, sd=5.0)  # z=2.2
        current = make_record(value=112.0, target=100.0, sd=5.0)  # z=2.4
        violations = WestgardService.check_rules(current, [prev])
        rules = [v["rule"] for v in violations]
        assert "2-2s" in rules

    def test_two_consecutive_below_minus_2sd(self):
        prev = make_record(value=89.0, target=100.0, sd=5.0)  # z=-2.2
        current = make_record(value=88.0, target=100.0, sd=5.0)  # z=-2.4
        violations = WestgardService.check_rules(current, [prev])
        rules = [v["rule"] for v in violations]
        assert "2-2s" in rules

    def test_opposite_sides_no_2_2s(self):
        prev = make_record(value=111.0, target=100.0, sd=5.0)  # z=+2.2
        current = make_record(value=89.0, target=100.0, sd=5.0)  # z=-2.2
        violations = WestgardService.check_rules(current, [prev])
        rules = [v["rule"] for v in violations]
        assert "2-2s" not in rules


class TestWestgardR4s:
    """Testes para regra R-4s (rejeição por erro aleatório)"""

    def test_range_exceeds_4sd(self):
        prev = make_record(value=111.0, target=100.0, sd=5.0)  # z=+2.2
        current = make_record(value=89.0, target=100.0, sd=5.0)  # z=-2.2, diff=4.4
        violations = WestgardService.check_rules(current, [prev])
        rules = [v["rule"] for v in violations]
        assert "R-4s" in rules

    def test_range_below_4sd_no_violation(self):
        prev = make_record(value=108.0, target=100.0, sd=5.0)  # z=+1.6
        current = make_record(value=111.0, target=100.0, sd=5.0)  # z=+2.2, diff=0.6
        violations = WestgardService.check_rules(current, [prev])
        rules = [v["rule"] for v in violations]
        assert "R-4s" not in rules


class TestWestgard4_1s:
    """Testes para regra 4-1s (rejeição por erro sistemático)"""

    def test_four_consecutive_above_1sd(self):
        history = [
            make_record(value=106.0, target=100.0, sd=5.0),  # z=1.2
            make_record(value=107.0, target=100.0, sd=5.0),  # z=1.4
            make_record(value=108.0, target=100.0, sd=5.0),  # z=1.6
        ]
        current = make_record(value=106.0, target=100.0, sd=5.0)  # z=1.2
        violations = WestgardService.check_rules(current, history)
        rules = [v["rule"] for v in violations]
        assert "4-1s" in rules

    def test_three_consecutive_not_enough(self):
        history = [
            make_record(value=106.0, target=100.0, sd=5.0),  # z=1.2
            make_record(value=107.0, target=100.0, sd=5.0),  # z=1.4
        ]
        current = make_record(value=106.0, target=100.0, sd=5.0)  # z=1.2
        violations = WestgardService.check_rules(current, history)
        rules = [v["rule"] for v in violations]
        assert "4-1s" not in rules


class TestWestgard10x:
    """Testes para regra 10x (erro sistemático - tendência)"""

    def test_ten_consecutive_same_side(self):
        # All values above target (positive side)
        history = [
            make_record(value=101.0, target=100.0, sd=5.0)
            for _ in range(9)
        ]
        current = make_record(value=101.0, target=100.0, sd=5.0)
        violations = WestgardService.check_rules(current, history)
        rules = [v["rule"] for v in violations]
        assert "10x" in rules

    def test_nine_consecutive_not_enough(self):
        history = [
            make_record(value=101.0, target=100.0, sd=5.0)
            for _ in range(8)
        ]
        current = make_record(value=101.0, target=100.0, sd=5.0)
        violations = WestgardService.check_rules(current, history)
        rules = [v["rule"] for v in violations]
        assert "10x" not in rules

    def test_mixed_sides_no_violation(self):
        history = []
        for i in range(9):
            if i % 2 == 0:
                history.append(make_record(value=101.0, target=100.0, sd=5.0))
            else:
                history.append(make_record(value=99.0, target=100.0, sd=5.0))
        current = make_record(value=101.0, target=100.0, sd=5.0)
        violations = WestgardService.check_rules(current, history)
        rules = [v["rule"] for v in violations]
        assert "10x" not in rules


class TestWestgardMultipleViolations:
    """Testes para cenários com múltiplas violações simultâneas"""

    def test_extreme_value_triggers_multiple_rules(self):
        """Um valor muito extremo deve disparar 1-2s, 1-3s ao mesmo tempo"""
        current = make_record(value=120.0, target=100.0, sd=5.0)  # z=4.0
        violations = WestgardService.check_rules(current, [])
        rules = [v["rule"] for v in violations]
        assert "1-2s" in rules
        assert "1-3s" in rules

    def test_severity_classification(self):
        """Verifica classificação correta de severidades"""
        current = make_record(value=116.0, target=100.0, sd=5.0)  # z=3.2
        violations = WestgardService.check_rules(current, [])

        warning_rules = [v for v in violations if v["severity"] == "warning"]
        rejection_rules = [v for v in violations if v["severity"] == "rejection"]

        assert len(warning_rules) > 0  # 1-2s
        assert len(rejection_rules) > 0  # 1-3s
