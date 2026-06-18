from __future__ import annotations
from dataclasses import dataclass
from typing import Literal
from .call_metrics import consume_call_metrics, reset_call_metrics
from .runtime import actor_answer, evaluator, get_failure_mode, reflector
from .schemas import AttemptTrace, QAExample, ReflectionEntry, RunRecord

@dataclass
class BaseAgent:
    agent_type: Literal["react", "reflexion"]
    max_attempts: int = 1
    def run(self, example: QAExample) -> RunRecord:
        reflection_memory: list[str] = []
        reflections: list[ReflectionEntry] = []
        traces: list[AttemptTrace] = []
        final_answer = ""
        final_score = 0
        for attempt_id in range(1, self.max_attempts + 1):
            reset_call_metrics()
            answer = actor_answer(example, attempt_id, self.agent_type, reflection_memory)
            actor_metrics = consume_call_metrics()

            reset_call_metrics()
            judge = evaluator(example, answer)
            eval_metrics = consume_call_metrics()

            token_estimate = actor_metrics.tokens + eval_metrics.tokens
            latency_ms = actor_metrics.latency_ms + eval_metrics.latency_ms

            trace = AttemptTrace(attempt_id=attempt_id, answer=answer, score=judge.score, reason=judge.reason, token_estimate=token_estimate, latency_ms=latency_ms)
            final_answer = answer
            final_score = judge.score
            if judge.score == 1:
                traces.append(trace)
                break

            if self.agent_type == "reflexion" and attempt_id < self.max_attempts:
                reset_call_metrics()
                reflection = reflector(example, attempt_id, judge, answer)
                ref_metrics = consume_call_metrics()
                token_estimate += ref_metrics.tokens
                latency_ms += ref_metrics.latency_ms
                trace.token_estimate = token_estimate
                trace.latency_ms = latency_ms
                reflections.append(reflection)
                reflection_memory.append(reflection.next_strategy)
                trace.reflection = reflection
            traces.append(trace)
        total_tokens = sum(t.token_estimate for t in traces)
        total_latency = sum(t.latency_ms for t in traces)
        failure_mode = get_failure_mode(example, judge, final_score)
        return RunRecord(qid=example.qid, question=example.question, gold_answer=example.gold_answer, agent_type=self.agent_type, predicted_answer=final_answer, is_correct=bool(final_score), attempts=len(traces), token_estimate=total_tokens, latency_ms=total_latency, failure_mode=failure_mode, reflections=reflections, traces=traces)

class ReActAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(agent_type="react", max_attempts=1)

class ReflexionAgent(BaseAgent):
    def __init__(self, max_attempts: int = 3) -> None:
        super().__init__(agent_type="reflexion", max_attempts=max_attempts)
