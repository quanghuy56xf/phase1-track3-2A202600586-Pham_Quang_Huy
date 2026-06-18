"""Quick smoke test for DeepSeek LLM runtime (Step 3)."""
from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()
os.environ["REFLEXION_RUNTIME"] = "llm"

from src.reflexion_lab.agents import ReActAgent, ReflexionAgent
from src.reflexion_lab.utils import load_dataset


def main() -> None:
    example = load_dataset("data/hotpot_mini.json")[1]  # hp2 multi-hop
    react = ReActAgent().run(example)
    reflexion = ReflexionAgent(max_attempts=3).run(example)

    print("=== ReAct ===")
    print(f"answer={react.predicted_answer!r} correct={react.is_correct} tokens={react.token_estimate}")
    print("=== Reflexion ===")
    print(f"answer={reflexion.predicted_answer!r} correct={reflexion.is_correct} attempts={reflexion.attempts}")
    print(f"reflections={len(reflexion.reflections)} tokens={reflexion.token_estimate}")


if __name__ == "__main__":
    main()
