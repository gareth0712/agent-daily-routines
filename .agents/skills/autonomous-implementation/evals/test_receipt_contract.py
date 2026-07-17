from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def require(text: str, needle: str, source: str) -> None:
    if needle not in text:
        raise AssertionError(f"{source}: missing {needle!r}")


def main() -> None:
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    method = (ROOT / "references" / "implementation-method.md").read_text(
        encoding="utf-8"
    )
    templates = (ROOT / "references" / "state-templates.md").read_text(
        encoding="utf-8"
    )
    evals = json.loads((ROOT / "evals" / "evals.json").read_text(encoding="utf-8"))

    for source, text in (("SKILL.md", skill), ("implementation-method.md", method)):
        for needle in (
            "readiness, implementation, repair, or integration",
            "host_return_observed_at",
            "return_observed",
            "final disposition",
        ):
            require(text, needle, source)

    for needle in (
        "canonical-utf8-base64-v1",
        "return_base64",
        "line_count: {integer 0..10}",
        "host_return_observed_at <= receipt_created_at <= worker_return_observed event time",
        "final_disposition_event: pending_at_receipt_creation",
    ):
        require(templates, needle, "state-templates.md")

    expectations = {
        item["id"]: "\n".join(item["expectations"]) for item in evals["evals"]
    }
    for eval_id in (1, 2, 3):
        require(expectations[eval_id], "readiness", f"eval {eval_id}")
        require(expectations[eval_id], "immutable receipt", f"eval {eval_id}")
        require(expectations[eval_id], "terminal subtree", f"eval {eval_id}")
        require(expectations[eval_id], "later acceptance disposition", f"eval {eval_id}")

    print("receipt contract tests: PASS")


if __name__ == "__main__":
    main()
