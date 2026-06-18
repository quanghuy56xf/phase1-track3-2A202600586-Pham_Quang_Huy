# Lab 16 Benchmark Report

## Metadata
- Dataset: hotpot_golden.json
- Mode: llm
- Records: 40
- Agents: react, reflexion

## Summary
| Metric | ReAct | Reflexion | Delta |
|---|---:|---:|---:|
| EM | 1.0 | 1.0 | 0.0 |
| Avg attempts | 1 | 1.05 | 0.05 |
| Avg token estimate | 223.9 | 281.45 | 57.55 |
| Avg latency (ms) | 844.7 | 1140.6 | 295.9 |

## Failure modes
```json
{
  "react": {
    "none": 20
  },
  "reflexion": {
    "none": 20
  },
  "combined": {
    "none": 40
  }
}
```

## Extensions implemented
- structured_evaluator
- reflection_memory
- adaptive_max_attempts
- benchmark_report_json
- mock_mode_for_autograding
- llm_runtime_deepseek

## Discussion
This benchmark compares ReAct (single attempt) against Reflexion (retry with reflection memory) on multi-hop QA. ReAct EM=100.00% with avg 1 attempts; Reflexion EM=100.00% with avg 1.05 attempts. Reflexion changed EM by +0.0000 at the cost of +57.55 tokens and +295.9 ms per question on average. ReAct failed on 0 questions; Reflexion recovered 1 cases after reflection. Common failure modes include incomplete_multi_hop (stopping at an intermediate entity), entity_drift (wrong second-hop answer), and wrong_final_answer. Observed failure breakdown: {"react": {"none": 20}, "reflexion": {"none": 20}, "combined": {"none": 40}}. Reflection memory helped when the evaluator identified a missing hop and the reflector supplied a concrete next strategy. Remaining errors often come from ambiguous context or evaluator false negatives.
