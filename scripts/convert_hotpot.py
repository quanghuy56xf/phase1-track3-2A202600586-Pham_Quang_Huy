"""Convert HotpotQA distractor JSON to QAExample format (README Lab 16)."""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Literal

from pydantic import ValidationError

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = Path(r"D:\HocAI\Day17\hotpot_dev_distractor_v1.json\hotpot_dev_distractor_v1.json")
DEFAULT_OUTPUT = ROOT / "data" / "my_test_set.json"


def _difficulty(item: dict) -> Literal["easy", "medium", "hard"]:
    qtype = item.get("type", "bridge")
    if qtype == "comparison":
        return "hard"
    if qtype == "bridge":
        return "medium"
    return "hard"


def convert_item(item: dict) -> dict:
    context = []
    for title, sentences in item["context"]:
        text = " ".join(s.strip() for s in sentences if s and s.strip())
        context.append({"title": title, "text": text})
    return {
        "qid": item["_id"],
        "difficulty": _difficulty(item),
        "question": item["question"],
        "gold_answer": item["answer"],
        "context": context,
    }


def sample_items(items: list[dict], limit: int, seed: int) -> list[dict]:
    if limit >= len(items):
        return items
    rng = random.Random(seed)
    by_type: dict[str, list[dict]] = {}
    for item in items:
        by_type.setdefault(item.get("type", "bridge"), []).append(item)

    picked: list[dict] = []
    types = sorted(by_type)
    per_type = max(1, limit // len(types))
    for qtype in types:
        pool = by_type[qtype][:]
        rng.shuffle(pool)
        picked.extend(pool[:per_type])

    if len(picked) < limit:
        remaining = [item for item in items if item not in picked]
        rng.shuffle(remaining)
        picked.extend(remaining[: limit - len(picked)])
    return picked[:limit]


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert HotpotQA to QAExample JSON")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--limit", type=int, default=50, help="Number of examples (min 50 for autograde)")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--no-shuffle", action="store_true", help="Take first N items instead of stratified sample")
    args = parser.parse_args()

    if not args.input.exists():
        raise SystemExit(f"Input not found: {args.input}")
    if args.limit < 50:
        raise SystemExit("README requires at least 50 examples for full experiment score.")

    raw = json.loads(args.input.read_text(encoding="utf-8"))
    subset = raw[: args.limit] if args.no_shuffle else sample_items(raw, args.limit, args.seed)
    converted = [convert_item(item) for item in subset]

    # Validate against project schema
    import sys
    sys.path.insert(0, str(ROOT))
    from src.reflexion_lab.schemas import QAExample

    for example in converted:
        try:
            QAExample.model_validate(example)
        except ValidationError as exc:
            raise SystemExit(f"Invalid example {example.get('qid')}: {exc}") from exc

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(converted, indent=2, ensure_ascii=False), encoding="utf-8")

    bridge = sum(1 for item in subset if item.get("type") == "bridge")
    comparison = sum(1 for item in subset if item.get("type") == "comparison")
    print(f"Wrote {len(converted)} examples to {args.output}")
    print(f"  bridge={bridge}, comparison={comparison}")
    print(f"  avg context paragraphs: {sum(len(x['context']) for x in converted) / len(converted):.1f}")


if __name__ == "__main__":
    main()
