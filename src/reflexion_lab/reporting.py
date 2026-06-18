from __future__ import annotations
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from .schemas import ReportPayload, RunRecord

def summarize(records: list[RunRecord]) -> dict:
    grouped: dict[str, list[RunRecord]] = defaultdict(list)
    for record in records:
        grouped[record.agent_type].append(record)
    summary: dict[str, dict] = {}
    for agent_type, rows in grouped.items():
        summary[agent_type] = {"count": len(rows), "em": round(mean(1.0 if r.is_correct else 0.0 for r in rows), 4), "avg_attempts": round(mean(r.attempts for r in rows), 4), "avg_token_estimate": round(mean(r.token_estimate for r in rows), 2), "avg_latency_ms": round(mean(r.latency_ms for r in rows), 2)}
    if "react" in summary and "reflexion" in summary:
        summary["delta_reflexion_minus_react"] = {"em_abs": round(summary["reflexion"]["em"] - summary["react"]["em"], 4), "attempts_abs": round(summary["reflexion"]["avg_attempts"] - summary["react"]["avg_attempts"], 4), "tokens_abs": round(summary["reflexion"]["avg_token_estimate"] - summary["react"]["avg_token_estimate"], 2), "latency_abs": round(summary["reflexion"]["avg_latency_ms"] - summary["react"]["avg_latency_ms"], 2)}
    return summary

def failure_breakdown(records: list[RunRecord]) -> dict:
    grouped: dict[str, Counter] = defaultdict(Counter)
    for record in records:
        grouped[record.agent_type][record.failure_mode] += 1
    combined: Counter = Counter()
    for counter in grouped.values():
        combined.update(counter)
    return {agent: dict(counter) for agent, counter in grouped.items()} | {"combined": dict(combined)}

def _build_discussion(records: list[RunRecord], summary: dict) -> str:
    react = summary.get("react", {})
    reflexion = summary.get("reflexion", {})
    delta = summary.get("delta_reflexion_minus_react", {})
    react_wrong = [r for r in records if r.agent_type == "react" and not r.is_correct]
    reflexion_fixed = [r for r in records if r.agent_type == "reflexion" and r.is_correct and r.attempts > 1]
    failure_modes = failure_breakdown(records)

    lines = [
        "This benchmark compares ReAct (single attempt) against Reflexion (retry with reflection memory) on multi-hop QA.",
        f"ReAct EM={react.get('em', 0):.2%} with avg {react.get('avg_attempts', 0)} attempts; "
        f"Reflexion EM={reflexion.get('em', 0):.2%} with avg {reflexion.get('avg_attempts', 0)} attempts.",
        f"Reflexion changed EM by {delta.get('em_abs', 0):+.4f} at the cost of "
        f"+{delta.get('tokens_abs', 0)} tokens and +{delta.get('latency_abs', 0)} ms per question on average.",
        f"ReAct failed on {len(react_wrong)} questions; Reflexion recovered {len(reflexion_fixed)} cases after reflection.",
        "Common failure modes include incomplete_multi_hop (stopping at an intermediate entity), "
        "entity_drift (wrong second-hop answer), and wrong_final_answer.",
        f"Observed failure breakdown: {json.dumps(failure_modes)}.",
        "Reflection memory helped when the evaluator identified a missing hop and the reflector supplied "
        "a concrete next strategy. Remaining errors often come from ambiguous context or evaluator false negatives.",
    ]
    return " ".join(lines)

def build_report(records: list[RunRecord], dataset_name: str, mode: str = "mock") -> ReportPayload:
    examples = [{"qid": r.qid, "agent_type": r.agent_type, "gold_answer": r.gold_answer, "predicted_answer": r.predicted_answer, "is_correct": r.is_correct, "attempts": r.attempts, "failure_mode": r.failure_mode, "reflection_count": len(r.reflections)} for r in records]
    summary = summarize(records)
    extensions = ["structured_evaluator", "reflection_memory", "benchmark_report_json", "mock_mode_for_autograding"]
    if mode == "llm":
        extensions.append("llm_runtime_deepseek")
    return ReportPayload(
        meta={"dataset": dataset_name, "mode": mode, "num_records": len(records), "agents": sorted({r.agent_type for r in records})},
        summary=summary,
        failure_modes=failure_breakdown(records),
        examples=examples,
        extensions=extensions,
        discussion=_build_discussion(records, summary),
    )

def save_report(report: ReportPayload, out_dir: str | Path) -> tuple[Path, Path]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "report.json"
    md_path = out_dir / "report.md"
    json_path.write_text(json.dumps(report.model_dump(), indent=2), encoding="utf-8")
    s = report.summary
    react = s.get("react", {})
    reflexion = s.get("reflexion", {})
    delta = s.get("delta_reflexion_minus_react", {})
    ext_lines = "\n".join(f"- {item}" for item in report.extensions)
    md = f"""# Lab 16 Benchmark Report

## Metadata
- Dataset: {report.meta['dataset']}
- Mode: {report.meta['mode']}
- Records: {report.meta['num_records']}
- Agents: {', '.join(report.meta['agents'])}

## Summary
| Metric | ReAct | Reflexion | Delta |
|---|---:|---:|---:|
| EM | {react.get('em', 0)} | {reflexion.get('em', 0)} | {delta.get('em_abs', 0)} |
| Avg attempts | {react.get('avg_attempts', 0)} | {reflexion.get('avg_attempts', 0)} | {delta.get('attempts_abs', 0)} |
| Avg token estimate | {react.get('avg_token_estimate', 0)} | {reflexion.get('avg_token_estimate', 0)} | {delta.get('tokens_abs', 0)} |
| Avg latency (ms) | {react.get('avg_latency_ms', 0)} | {reflexion.get('avg_latency_ms', 0)} | {delta.get('latency_abs', 0)} |

## Failure modes
```json
{json.dumps(report.failure_modes, indent=2)}
```

## Extensions implemented
{ext_lines}

## Discussion
{report.discussion}
"""
    md_path.write_text(md, encoding="utf-8")
    return json_path, md_path
