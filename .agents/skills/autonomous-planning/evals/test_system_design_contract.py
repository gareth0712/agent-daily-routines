from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def require(path: Path, *needles: str) -> None:
    text = path.read_text(encoding="utf-8")
    missing = [needle for needle in needles if needle not in text]
    assert not missing, f"{path.relative_to(ROOT)} missing: {missing}"


def section(path: Path, heading: str) -> str:
    text = path.read_text(encoding="utf-8")
    match = re.search(
        rf"(?ms)^## {re.escape(heading)}\n(.*?)(?=^## |\Z)",
        text,
    )
    assert match, f"{path.relative_to(ROOT)} missing section: {heading}"
    return match.group(1)


def between(path: Path, start: str, end: str) -> str:
    text = path.read_text(encoding="utf-8")
    assert text.count(start) == 1, f"{path.relative_to(ROOT)} start mismatch: {start}"
    assert text.count(end) == 1, f"{path.relative_to(ROOT)} end mismatch: {end}"
    return text.split(start, 1)[1].split(end, 1)[0]


require(
    ROOT / "SKILL.md",
    "System design scenario matrix",
    "Small / Baseline",
    "Medium / Growth and HA",
    "Enterprise / High-scale or mission-critical",
    "user count alone",
    "correctness, security, privacy, and safety requirements remain identical",
    "current execution request explicitly authorizes named future-profile work",
    "must not block completion of the remaining Planning-owned contracts",
)
require(
    ROOT / "references" / "planning-method.md",
    "workload/risk envelope",
    "not_applicable",
    "deferred",
    "backpressure",
    "RTO/RPO",
    "no universal numeric threshold",
    "correctness, security, privacy, and safety requirements remain identical",
    "current execution request explicitly authorizes named future-profile work",
)
require(
    ROOT / "references" / "state-templates.md",
    "## System design scenario matrix",
    "recommended_current_profile",
    "upgrade_trigger",
    "validation_action",
    "decision_deadline",
    "Shared correctness/security/privacy/safety invariants",
    "Current execution request for future-profile work",
)
require(
    ROOT / "references" / "launcher-template.md",
    "Architecture scenario policy",
    "do not invent precise",
    "current Discovery/equivalent evidence for this scope contains one named material system-design trigger",
)

method_matrix = section(
    ROOT / "references" / "planning-method.md",
    "Conditional system-design scenario matrix",
)
for needle in (
    "Otherwise omit the matrix",
    "do not invent precise",
    "does not automatically mean microservices",
    "current execution request explicitly authorizes named future-profile work",
):
    assert needle in method_matrix, f"matrix relationship missing: {needle}"

for needle in (
    "`required`, evidenced `not_applicable`, or `deferred`",
    "owner, validation action, measurable upgrade trigger, and decision deadline",
):
    assert needle in method_matrix, f"disposition relationship missing: {needle}"

skill_review = between(
    ROOT / "SKILL.md",
    "### 8. Run independent final plan review",
    "### 9. Apply the Implementation readiness gate",
)
for needle in (
    "all three profiles",
    "evidence-driven recommendation",
    "`required` / evidenced `not_applicable` / owned-and-triggered `deferred`",
    "resilience/recovery/operations/security/cost coverage",
    "identical correctness/security/privacy/safety requirements",
    "current execution request contains the exact future-profile authorization evidence",
):
    assert needle in skill_review, f"workflow reviewer duty missing: {needle}"

method_review = section(
    ROOT / "references" / "planning-method.md",
    "Independent plan review",
)
for needle in (
    "all three profiles",
    "workload/risk evidence",
    "separate upgrade triggers/deadlines",
    "identical correctness/security/privacy/safety requirements",
    "current execution request explicitly authorizes named future-profile work",
):
    assert needle in method_review, f"method reviewer duty missing: {needle}"

template_matrix = section(
    ROOT / "references" / "state-templates.md",
    "System design scenario matrix",
)
assert "| `upgrade_trigger` | `decision_deadline` |" in template_matrix
assert "Current execution request for future-profile work" in template_matrix
for needle in (
    "explicit_request: current request path/revision, current-scope mapping, requested dimension, material_trigger: none_not_required",
    "discovery_trigger: current Discovery/equivalent path/revision, current-scope mapping, one named material trigger",
):
    assert needle in template_matrix, f"activation alternative missing: {needle}"

for path in (
    ROOT / "SKILL.md",
    ROOT / "references" / "planning-method.md",
    ROOT / "references" / "state-templates.md",
):
    text = path.read_text(encoding="utf-8")
    assert not re.search(r"(?:fewer than|through|more than) 10?,?000 users", text)

evals = json.loads((ROOT / "evals" / "evals.json").read_text(encoding="utf-8"))
qualifying = next(item for item in evals["evals"] if item["id"] == 1)
joined = "\n".join(qualifying["expectations"])
for needle in (
    "System design scenario matrix",
    "Small / Baseline",
    "Medium / Growth and HA",
    "Enterprise / High-scale or mission-critical",
):
    assert needle in joined, f"eval 1 missing: {needle}"

for needle in (
    "not fixed user-count bands",
    "current execution request explicitly authorizes named future-profile work",
    "correctness, security, privacy, and safety",
):
    assert needle in joined, f"eval 1 relationship missing: {needle}"

assert "planning_approval_state: not_requested" in joined
assert "planning_approval_evidence path/revision/authority all none" in joined
assert "delegated_execution_authority" not in joined

activation = json.loads(
    (ROOT / "evals" / "activation-evals.json").read_text(encoding="utf-8")
)
narrow = next(item for item in activation["cases"] if item["id"] == 6)
assert narrow["should_trigger_autonomous_planning"] is False
assert narrow["first_stage"] == "Ordinary scoped implementation"
assert narrow["competing_owner"] == "ordinary scoped workflow"

print("system design contract tests: PASS")
