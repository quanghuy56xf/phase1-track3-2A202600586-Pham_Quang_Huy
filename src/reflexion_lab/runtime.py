from __future__ import annotations
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .schemas import JudgeResult, QAExample, ReflectionEntry

def _mode() -> str:
    return os.getenv("REFLEXION_RUNTIME", "llm").lower()

def _impl():
    if _mode() == "mock":
        from . import mock_runtime as runtime
    else:
        from . import llm_runtime as runtime
    return runtime

def actor_answer(example: QAExample, attempt_id: int, agent_type: str, reflection_memory: list[str]) -> str:
    return _impl().actor_answer(example, attempt_id, agent_type, reflection_memory)

def evaluator(example: QAExample, answer: str) -> JudgeResult:
    return _impl().evaluator(example, answer)

def reflector(example: QAExample, attempt_id: int, judge: JudgeResult, answer: str = "") -> ReflectionEntry:
    return _impl().reflector(example, attempt_id, judge, answer)

def get_failure_mode(example: QAExample, judge: JudgeResult, final_score: int) -> str:
    return _impl().get_failure_mode(example, judge, final_score)

__all__ = ["actor_answer", "evaluator", "reflector", "get_failure_mode"]
