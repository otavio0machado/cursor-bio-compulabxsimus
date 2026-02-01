import os
import time
from contextlib import contextmanager
from typing import Dict, Iterable, Tuple


def timing_enabled() -> bool:
    value = os.getenv("ANALYSIS_TIMING", "")
    return value.strip().lower() in {"1", "true", "yes", "on"}


class TimingCollector:
    def __init__(self, enabled: bool | None = None) -> None:
        self.enabled = timing_enabled() if enabled is None else bool(enabled)
        self.steps: Dict[str, float] = {}
        self.started_at = time.perf_counter() if self.enabled else 0.0

    @contextmanager
    def step(self, name: str) -> Iterable[None]:
        if not self.enabled:
            yield
            return
        start = time.perf_counter()
        try:
            yield
        finally:
            self.add(name, time.perf_counter() - start)

    def add(self, name: str, duration: float) -> None:
        if not self.enabled:
            return
        self.steps[name] = self.steps.get(name, 0.0) + duration

    def total(self) -> float:
        if not self.enabled:
            return 0.0
        return time.perf_counter() - self.started_at

    def summary(self) -> Iterable[Tuple[str, float]]:
        if not self.enabled:
            return []
        return sorted(self.steps.items(), key=lambda item: (-item[1], item[0]))

    def log(self, label: str) -> None:
        if not self.enabled:
            return
        total = self.total()
        print(f"TIMING: {label} total={total:.3f}s")
        for name, duration in self.summary():
            print(f"  - {name}: {duration:.3f}s")
