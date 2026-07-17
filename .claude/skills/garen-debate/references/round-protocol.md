# Round Protocol

Defines the exact content format defenders must produce each round.

---

## Round 1 (Opening)

Each defender writes a fresh `proposal-{letter}.md`. This is an independent opening statement — defenders do NOT read other proposals.

### Required structure:

```markdown
# Proposal {Letter}: {Name}

## Approach
{1-3 sentence summary of the approach. What is it? What's the core idea?}

## How it works
{Concrete steps. Include example commands, file paths, or config snippets where relevant. Be specific enough that the Judge can evaluate feasibility.}

Step 1: ...
Step 2: ...
Step 3: ...

## Tradeoffs / Honest limitations
{Be self-critical. List real drawbacks. Judge sees through marketing — proposals that only list strengths lose credibility.}

- Limitation 1: ...
- Limitation 2: ...
- Limitation 3: ...
```

Target length: 150-300 words.

---

## Round 2-N (Debate)

Each defender APPENDS to their own `proposal-{letter}.md`. Never overwrite or delete previous rounds.

### Append this exact block:

```markdown
## Round {N} Update

### Defense
{For each attack the other proposals raised against my approach last round, address it concretely. Cite which proposal and which specific attack.}

Example: "Proposal B's R2 counter-attack on operational cost — addressed by [specific evidence or clarification]."

If no attacks targeted me last round, write: "No attacks targeted Proposal {Letter} last round."

### Counter-attack
{Pick 1-2 weaknesses in OTHER proposals. Be specific. Cite the proposal letter and the specific claim you're challenging.}

Example: "Proposal C's claim that [X] scales to 10k users is incorrect because [Y]. See their Step 2 — it assumes a single-writer model."

### Strengthening
{Add 1-2 new supporting points, evidence, or use cases for MY proposal that have NOT been mentioned in any previous round. The Judge checks for repetition — recycled points do not count.}

### Concession (optional)
{If a specific attack against you is genuinely unanswerable, acknowledge it here. Pretending it doesn't exist hurts your credibility with the Judge more than acknowledging it does.}
```

---

## Hard Rules (enforced via defender prompts)

| Rule | Requirement |
|------|------------|
| Defense | ≥1 item addressing an attack OR explicit "no attacks targeted me" |
| Counter-attack | ≥1 item with specific cite (proposal letter + claim) |
| Strengthening | ≥1 item that is genuinely new (not repeated from earlier rounds) |
| Word cap | Round update ≤ 250 words (prevent verbosity bloat across rounds) |
| No overwrite | Only APPEND — never replace previous round content |

---

## Dynamic Stop Signals

A defender MAY end their round update with one of these signals:

- `<NO_NEW_POINTS>` — the defender has nothing genuinely new to add; the debate has exhausted their contribution
- `<CONCEDE>` — the defender explicitly acknowledges another proposal is dominantly better, with a brief explanation why

**Stop signal placement (CRITICAL):** Stop signals (`<NO_NEW_POINTS>` or `<CONCEDE>`) MUST be placed on a line by themselves at the very end of your appended Round update. Do NOT quote these signals in prose — paraphrase ("Proposal B conceded") instead. The stop signal must be on its own line within the last 3 lines of the file. Do not add trailing blank lines after the signal (or limit to max 2 trailing blanks).

**Stop condition:** After each round completes, orchestrator scans all proposal files.
- If ≥2 defenders have signalled `<NO_NEW_POINTS>` or `<CONCEDE>` → stop debate, move to Phase 5
- If round count reached 7 → hard stop, move to Phase 5 regardless of signals

**Important:** Stop signals do not end the current round — they are evaluated AFTER all defenders in that round have finished.

---

## Example Round 2 Update (abbreviated)

```markdown
## Round 2 Update

### Defense
Proposal B's R1 attack on cold-start latency — addressed by lazy initialization: the worker only loads the schema on first request, not at startup. This reduces boot time by ~300ms (benchmarked in our staging env).

### Counter-attack
Proposal A's claim that "Cloudflare D1 handles 10k writes/sec" is misleading — D1 is optimized for reads; their own docs cap writes at 1k/sec per database. See Proposal A Step 3.

### Strengthening
New point: our approach also enables offline-first mobile sync via the same SQLite client — a use case not addressed by any other proposal.
```
