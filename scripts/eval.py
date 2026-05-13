"""
Eval harness — runs a test set of Q&A pairs against the RAG pipeline
and prints accuracy metrics.

This is the thing that separates "ChatGPT wrapper" from "production system"
in client conversations. SHOW THIS IN YOUR LOOM.

Run: python scripts/eval.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.rag import get_pipeline

# Each item: a question, and a list of keywords that MUST appear in a correct answer.
# This is a simple but effective eval — better than nothing, much better than vibes.
# For a real client you'd build LLM-as-judge evals too, but this proves the concept.
TEST_SET = [
    {
        "question": "What is JDG in Poland?",
        "must_contain": ["sole", "proprietorship"],  # or Polish equivalent
        "must_contain_any": ["JDG", "jednoosobowa", "sole proprietor"],
    },
    {
        "question": "What is the VAT registration threshold?",
        "must_contain_any": ["200,000", "200 000", "PLN", "threshold"],
    },
    {
        "question": "Who can register a JDG in Poland?",
        "must_contain_any": ["EU", "citizen", "resident", "permit"],
    },
    # Add 10-20 more for a real eval. Aim for diverse difficulty.
]


def keyword_score(answer: str, must_contain: list[str], must_contain_any: list[str]) -> tuple[float, str]:
    """Score 0.0–1.0 based on keyword presence. Returns (score, explanation)."""
    answer_lower = answer.lower()
    notes = []

    all_present = all(kw.lower() in answer_lower for kw in (must_contain or []))
    any_present = (
        not must_contain_any
        or any(kw.lower() in answer_lower for kw in must_contain_any)
    )

    if must_contain and not all_present:
        missing = [kw for kw in must_contain if kw.lower() not in answer_lower]
        notes.append(f"missing required: {missing}")
    if must_contain_any and not any_present:
        notes.append(f"missing any-of: {must_contain_any}")

    score = 1.0 if (all_present and any_present) else 0.0
    return score, "; ".join(notes) if notes else "ok"


def main():
    print("Running RAG eval...\n")
    pipe = get_pipeline()

    results = []
    for i, case in enumerate(TEST_SET, 1):
        q = case["question"]
        print(f"[{i}/{len(TEST_SET)}] {q}")
        resp = pipe.query(q)
        score, note = keyword_score(
            resp.answer,
            case.get("must_contain", []),
            case.get("must_contain_any", []),
        )
        results.append({
            "question": q,
            "score": score,
            "note": note,
            "latency_ms": resp.latency_ms,
            "answer_preview": resp.answer[:120] + "..." if len(resp.answer) > 120 else resp.answer,
        })
        status = "✓" if score == 1.0 else "✗"
        print(f"  {status} {note} ({resp.latency_ms}ms)")
        print(f"    {results[-1]['answer_preview']}\n")

    # Summary
    avg_score = sum(r["score"] for r in results) / len(results)
    avg_latency = sum(r["latency_ms"] for r in results) / len(results)
    print(f"\n=== Summary ===")
    print(f"Accuracy: {avg_score:.0%} ({sum(r['score'] for r in results):.0f}/{len(results)})")
    print(f"Avg latency: {avg_latency:.0f}ms")


if __name__ == "__main__":
    main()
