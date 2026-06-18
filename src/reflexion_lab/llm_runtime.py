from __future__ import annotations
from .llm_client import chat_completion, chat_json
from .prompts import ACTOR_SYSTEM, EVALUATOR_SYSTEM, REFLECTOR_SYSTEM
from .schemas import JudgeResult, QAExample, ReflectionEntry

def _format_context(example: QAExample) -> str:
    blocks = [f"[{chunk.title}]\n{chunk.text}" for chunk in example.context]
    return "\n\n".join(blocks)

def actor_answer(example: QAExample, attempt_id: int, agent_type: str, reflection_memory: list[str]) -> str:
    memory_block = ""
    if reflection_memory:
        strategies = "\n".join(f"- {item}" for item in reflection_memory)
        memory_block = f"\n\nPrevious reflection strategies:\n{strategies}"

    user = (
        f"Context:\n{_format_context(example)}\n\n"
        f"Question: {example.question}\n"
        f"Attempt: {attempt_id} ({agent_type})"
        f"{memory_block}\n\n"
        "Return only the final short answer."
    )
    return chat_completion(ACTOR_SYSTEM, user)

def evaluator(example: QAExample, answer: str) -> JudgeResult:
    user = (
        f"Question: {example.question}\n"
        f"Gold answer: {example.gold_answer}\n"
        f"Predicted answer: {answer}\n\n"
        "Return JSON only."
    )
    payload = chat_json(EVALUATOR_SYSTEM, user)
    return JudgeResult.model_validate(payload)

def reflector(example: QAExample, attempt_id: int, judge: JudgeResult, answer: str) -> ReflectionEntry:
    user = (
        f"Question: {example.question}\n"
        f"Attempt ID: {attempt_id}\n"
        f"Wrong answer: {answer}\n"
        f"Evaluator reason: {judge.reason}\n"
        f"Missing evidence: {judge.missing_evidence}\n"
        f"Spurious claims: {judge.spurious_claims}\n\n"
        "Return JSON only."
    )
    payload = chat_json(REFLECTOR_SYSTEM, user)
    payload["attempt_id"] = attempt_id
    return ReflectionEntry.model_validate(payload)

def get_failure_mode(example: QAExample, judge: JudgeResult, final_score: int) -> str:
    if final_score == 1:
        return "none"
    reason = judge.reason.lower()
    if any(term in reason for term in ("hop", "intermediate", "partial", "incomplete")):
        return "incomplete_multi_hop"
    if judge.spurious_claims:
        return "entity_drift"
    return "wrong_final_answer"
