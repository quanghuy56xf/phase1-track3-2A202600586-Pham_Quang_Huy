from __future__ import annotations
from dataclasses import dataclass

@dataclass
class CallMetrics:
    tokens: int = 0
    latency_ms: int = 0

_metrics = CallMetrics()

def reset_call_metrics() -> None:
    global _metrics
    _metrics = CallMetrics()

def record_call_metrics(tokens: int, latency_ms: int) -> None:
    global _metrics
    _metrics.tokens += tokens
    _metrics.latency_ms += latency_ms

def consume_call_metrics() -> CallMetrics:
    global _metrics
    current = _metrics
    _metrics = CallMetrics()
    return current
