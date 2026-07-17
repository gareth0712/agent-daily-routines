# Verdict Template

The Judge must produce `verdict.md` following this exact structure. Do not add sections. Do not omit sections.

---

## Template

```markdown
# Verdict — {Topic}

## Winner
**Proposal {Letter}: {Name}** — {1-sentence rationale explaining why this proposal won}

## Why this proposal won

1. **Evolution:** {How the proposal strengthened across rounds — what was weak in R1 that was resolved by the final round?}
2. **Attacks survived:** {Which counter-attacks from other proposals did this proposal neutralize, and how convincingly?}
3. **Counter-attacks landed:** {Which other proposals did this proposal successfully weaken, and on what claims?}
4. **Fit to constraints:** {How well does it match the user's stated constraints and success criteria?}

## Full Tradeoff Table

| Dimension | Proposal A | Proposal B | Proposal C | {additional columns as needed} |
|-----------|-----------|-----------|-----------|-------------------------------|
| Setup cost | ... | ... | ... | ... |
| Operational complexity | ... | ... | ... | ... |
| Cost ($/month est.) | ... | ... | ... | ... |
| Scalability ceiling | ... | ... | ... | ... |
| Team skill requirement | ... | ... | ... | ... |
| {Dimension discovered during debate} | ... | ... | ... | ... |

Add rows for any dimensions that surfaced during the debate. Remove rows that don't apply to this topic.

## Actionable Next Steps

1. {Concrete step 1 — include file paths, commands, or service names where applicable}
2. {Concrete step 2}
3. {Concrete step 3}

## What's worth borrowing from losing proposals

- **From Proposal {X}: {Name}** — {1-2 specific ideas, patterns, or constraints from this proposal that could enhance or de-risk the winning approach}
- **From Proposal {Y}: {Name}** — {same}

(Omit proposals that contributed nothing worth borrowing.)

## All Agent Points (Reference)

### Proposal A — {Name}

- **Round 1 (Opening):** {1-line summary of opening position}
- **Round 2 Defense:** {what was defended} | **Counter:** {what was attacked} | **Strengthening:** {new point added}
- **Round 3 Defense:** ... | **Counter:** ... | **Strengthening:** ...
- {continue for all rounds this proposal participated in}
- **Final status:** {Won / Conceded / Dominated / Hybridized}
- **Stop signal (if any):** {<NO_NEW_POINTS> / <CONCEDE> / none}

### Proposal B — {Name}

{same structure as Proposal A}

### Proposal C — {Name}

{same structure as Proposal A}

{add sections for all proposals}

## Honest Limitations of This Verdict

- **Not covered:** {What the debate didn't address — e.g., specific integration scenarios, regulatory requirements, org-specific constraints}
- **Where winner could fail:** {Specific conditions or scale points where the winning proposal might break down}
- **When to reconsider:** {Concrete triggers that should prompt re-evaluation — e.g., "if team size doubles", "if latency SLA drops below 50ms", "if budget halves"}
```

---

## Judge Evaluation Criteria

When picking the winner, weight these factors in order:

1. **Fewest unaddressed weaknesses** — which proposal had the most attacks successfully neutralized?
2. **Landed counter-attacks** — which proposal most effectively weakened its opponents?
3. **Round evolution** — which proposal materially strengthened from R1 to final round?
4. **Constraint fit** — which proposal best matches the user's stated constraints and success criteria?

**Hybrid winners are allowed** — if the best outcome is "Proposal A's architecture + Proposal B's caching strategy", say so explicitly and specify exactly what to take from each.

**Be decisive.** A verdict that says "it depends" without a clear winner is not useful. Make the call, then qualify it in "Honest Limitations".

## All Agent Points — completeness requirement

The "All Agent Points" section must include:
- One entry per proposal (no skipping)
- One line per round per proposal (no skipping rounds)
- The final status for every proposal

This section is the primary audit trail — users refer back to it to understand why specific arguments were or were not credited.
