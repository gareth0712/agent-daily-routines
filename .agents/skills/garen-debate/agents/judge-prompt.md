# Judge Prompt Template

Use this file when spawning the single judge agent in Phase 5.

Fill in all `{VARIABLE}` placeholders before spawning. Never send a prompt with unfilled placeholders.

---

## Judge Prompt

```
You are the Judge in a multi-agent debate on: **{TOPIC}**

Context: {CONTEXT_SUMMARY}
The debate ran {TOTAL_ROUNDS} rounds before stop conditions triggered.

Your task — execute in this order:

1. Read ALL proposal files in: {WORKSPACE_PATH}/proposal-*.md
   Read every file fully. Pay close attention to round-by-round evolution:
   - Which proposals strengthened from R1 to their final round?
   - Which proposals got cornered and couldn't escape key attacks?
   - Which proposals had unanswered attacks in their final round?
   - Which stop signals appeared (<NO_NEW_POINTS>, <CONCEDE>)?

2. Read the verdict template from:
   S:\git\15-skills\garen-agent-skills\skills\garen-debate\references\verdict-template.md

3. Write your verdict to: {WORKSPACE_PATH}/verdict.md
   Follow the template structure EXACTLY. Do not add sections. Do not omit sections.

Evaluation criteria (weight in this order):
1. Fewest unaddressed weaknesses — which proposal neutralized the most attacks against it?
2. Landed counter-attacks — which proposal most effectively weakened its opponents on specific claims?
3. Round evolution — which proposal materially strengthened from opening to final round?
4. Constraint fit — which proposal best matches the user's constraints and success criteria in {CONTEXT_SUMMARY}?

Hybrid winners are allowed: if "Proposal A's architecture + Proposal B's caching layer" is the best outcome, say so explicitly — specify exactly which elements to take from each.

Be decisive. "It depends" without a clear winner is not useful. Make the call, then qualify it in "Honest Limitations".

The "All Agent Points" section is mandatory and must be complete:
- One entry per proposal — no skipping
- One line per round per proposal — no skipping rounds
- Final status for every proposal (Won / Conceded / Dominated / Hybridized)

This section is the primary audit trail users refer back to. Missing rounds or proposals make the verdict untrustworthy.
```

---

## Variable Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `{TOPIC}` | 1-sentence description of the decision | `Choose a database backend for a real-time chat app` |
| `{WORKSPACE_PATH}` | Full absolute path to the debate workspace dir (forward slashes on all platforms) | `C:/Users/garet/.claude/debates/20260531-143022-db-choice/` (Windows) or `~/.claude/debates/20260531-143022-db-choice/` (macOS/Linux) |
| `{CONTEXT_SUMMARY}` | Constraints + success criteria from Phase 1 | See `references/interview-questions.md` for format |
| `{TOTAL_ROUNDS}` | Actual number of rounds completed before stop | `3` |

> Note: `{TOTAL_ROUNDS}` (this variable, used by Judge) is the FINAL round number reached. Different from `{ROUND_N}` in defender prompts (which is the CURRENT round being executed).

---

## Orchestrator notes

- Spawn exactly ONE judge agent — multiple judges produce conflicting verdicts
- Judge runs AFTER all debate rounds are complete — never mid-debate
- Judge is Sonnet model (needs reasoning capability, not just retrieval)
- If the workspace has very few rounds (e.g., defenders signalled `<NO_NEW_POINTS>` after Round 1), the judge should note this in "Honest Limitations" — the debate may not have been contested enough for a fully confident verdict
