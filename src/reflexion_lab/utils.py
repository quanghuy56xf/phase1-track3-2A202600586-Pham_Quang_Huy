from __future__ import annotations
import json
import re
from pathlib import Path
from typing import Iterable
from .schemas import QAExample, RunRecord

def normalize_answer(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text

def try_rule_judge(gold: str, predicted: str) -> "JudgeResult | None":
    """Deterministic evaluator: exact/substring match before LLM fallback."""
    from .schemas import JudgeResult

    norm_g = normalize_answer(gold)
    norm_p = normalize_answer(predicted)
    if not norm_p:
        return JudgeResult(score=0, reason="Predicted answer is empty.", spurious_claims=[predicted or ""])
    if norm_g == norm_p:
        return JudgeResult(score=1, reason="Exact match after normalization.")
    if len(norm_g) >= 3 and norm_g in norm_p:
        return JudgeResult(
            score=1,
            reason="Predicted answer contains the gold answer after normalization.",
        )
    if len(norm_p) >= 3 and norm_p in norm_g:
        return JudgeResult(
            score=1,
            reason="Gold answer contains the predicted answer after normalization.",
        )
    yes_answers = {"yes", "yeah", "true"}
    no_answers = {"no", "false"}
    if norm_g in yes_answers and norm_p in yes_answers:
        return JudgeResult(score=1, reason="Both answers are affirmative after normalization.")
    if norm_g in no_answers and norm_p in no_answers:
        return JudgeResult(score=1, reason="Both answers are negative after normalization.")
    return None

def format_reflection_memory(reflection: "ReflectionEntry", wrong_answer: str, attempt_id: int) -> str:
    return (
        f"[Attempt {attempt_id}] Wrong answer: '{wrong_answer}'. "
        f"Failure: {reflection.failure_reason} "
        f"Lesson: {reflection.lesson} "
        f"Strategy: {reflection.next_strategy}"
    )

def load_dataset(path: str | Path) -> list[QAExample]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return [QAExample.model_validate(item) for item in raw]

def save_jsonl(path: str | Path, records: Iterable[RunRecord]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(record.model_dump_json() + "\n")
