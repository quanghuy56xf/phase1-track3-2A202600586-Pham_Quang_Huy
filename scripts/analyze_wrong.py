import json
from pathlib import Path

out = Path("outputs/hotpot_run")
reflex = {r["qid"]: r for r in map(json.loads, (out / "reflexion_runs.jsonl").read_text(encoding="utf-8").splitlines())}
react = {r["qid"]: r for r in map(json.loads, (out / "react_runs.jsonl").read_text(encoding="utf-8").splitlines())}

fixed = [qid for qid in react if not react[qid]["is_correct"] and reflex[qid]["is_correct"]]
wrong = [qid for qid in reflex if not reflex[qid]["is_correct"]]

print(f"Reflexion still wrong: {len(wrong)}")
print(f"ReAct wrong -> Reflexion fixed: {len(fixed)}")

for qid in wrong:
    r = reflex[qid]
    print("=" * 80)
    print("QID:", qid)
    print("Q:", r["question"])
    print("Gold:", r["gold_answer"])
    print("Final pred:", r["predicted_answer"])
    print("Failure:", r["failure_mode"])
    print("ReAct pred:", react[qid]["predicted_answer"])
    for t in r["traces"]:
        print(f"  Attempt {t['attempt_id']}: {t['answer']!r} (score={t['score']})")
        print(f"    reason: {t['reason'][:120]}")
        if t.get("reflection"):
            print(f"    next_strategy: {t['reflection']['next_strategy'][:150]}")
