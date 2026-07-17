# Cold-Start Retest Report — garen-debate skill (v2)

**Test prompt:** /garen-debate Need to choose a background job queue for my Cloudflare Workers SaaS app — torn between Cloudflare Queues, Durable Objects as a queue, and Upstash QStash

## Verdict
- **Could a fresh Claude run this skill end-to-end?** YES
- **Estimated quality of debate this would produce:** HIGH
- **Previous gaps regressed:** 0
- **NEW gaps discovered:** 3 (minor)

---

## Fix verification table

| # | Previous gap | Status | Note |
|---|--------------|--------|------|
| 1 | Brainstorm seed framework missing | FIXED | Seed framework (4 axes) now in `references/interview-questions.md`. Tested below — genuinely useful. |
| 2 | EOF-anchored stop signals ambiguous | FIXED | `round-protocol.md` now has explicit "standalone final line" requirement + "do NOT quote in prose" rule. `SKILL.md` has a grep/tail command. |
| 3 | Snapshot isolation unexplained | FIXED | SKILL.md Phase 4 now has explicit anti-pattern example with concrete DO/DON'T phrasing. |
| 4 | Windows path for `{CLAUDE_HOME}` undefined | FIXED | SKILL.md Phase 2 now lists platform-specific resolution with forward-slash note for subagent prompts. Both agent prompt Variable Reference tables show a full Windows example path. |
| 5 | `{LETTER}` vs `{letter}` confusion | FIXED | defender-prompt.md Variable Reference table now explicitly distinguishes uppercase (spoken identity) from lowercase (file paths). |
| 6 | `{ROUND_COUNT}` source undefined | FIXED | judge-prompt.md Variable Reference now says "Actual number of rounds completed before stop" with example `3`. SKILL.md Phase 5 says "fill in {ROUND_COUNT} — actual final round number". Clear enough. |
| 7 | "Synthesize from verdict" reporting unclear | FIXED | SKILL.md Reporting Back step 2 now says explicitly "Do NOT copy verdict sections verbatim — synthesize." |
| 8 | Cost script path platform-specific | FIXED | SKILL.md Phase 2 shows the bash invocation using `S:\git\...\estimate-cost.sh` — matches Windows workspace. |
| 9 | No confirmation step for candidate list | FIXED | `interview-questions.md` has a full confirmation block template. SKILL.md Phase 1 step 4 says "Confirm all candidates with user before proceeding to Phase 2." |
| 10 | Brainstorm cap of 6 buried | FIXED | `interview-questions.md` candidate brainstorm section explicitly says "Cap at 6 total candidates". |
| 11 | No model spec for judge | FIXED | judge-prompt.md Orchestrator notes specifies "Judge is Sonnet model". |

---

## Phase-by-phase walkthrough

### Phase 1: Interview — PASS
User provided 3 candidates (Cloudflare Queues, Durable Objects as queue, Upstash QStash). That is exactly 3 — the minimum. The skill says "brainstorm to fill gap to 3-6 total." Three candidates are within range (3-6), so brainstorming is optional but encouraged. The instructions are slightly ambiguous here: the rule says "user provides 0-N; brainstorm to fill gap to **3-6 total**." With exactly 3, a cold-start agent might skip brainstorm (3 is already ≥3). See **NEW GAP #1** below.

Batching questions: the user's initial message gives scenario context and 3 candidates but not constraints. A proper first response would ask (batched ≤4 questions): budget, scale, team experience, and deal-breaker. The question bank in `interview-questions.md` is well-organized and clear.

### Phase 2: Setup + Cost Guard — PASS
Path generation traced below. Cost script invocation is clear. User confirmation message template is present.

### Phase 3: Round 1 — PASS
Defender prompt Round 1 template is complete. All variables are defined. File path uses `{letter}` (lowercase) for `proposal-{letter}.md`. `{LETTER}` uppercase appears only in "Defender {LETTER}" spoken identity and "Proposal {Letter}" headings. Distinction is clear in the Variable Reference table.

### Phase 4: Debate Rounds — PASS
Stop signal grep command reads:
```bash
for f in {WORKSPACE_PATH}/proposal-*.md; do
  tail -1 "$f" | grep -qE "^(<NO_NEW_POINTS>|<CONCEDE>)$" && echo "$f"
done | wc -l
```
This correctly anchors to final line (via `tail -1`) and requires the signal to be the entire line (`^...$`). False-positive analysis: if a defender writes "Proposal B's <NO_NEW_POINTS> argument" in prose mid-file, `tail -1` only checks the last line, so this is not a false positive. If a defender mistakenly writes `<CONCEDE>` followed by a blank line, `tail -1` returns an empty line and the grep fails — signal is missed. See **NEW GAP #2** below.

Snapshot isolation anti-pattern is explicit and uses a concrete bad example. Clear to cold-start agent.

### Phase 5: Judge Verdict — PASS
Judge prompt is complete. `{ROUND_COUNT}` is tracked by orchestrator as a simple counter incremented after each round. The judge prompt Orchestrator notes explicitly call out the low-round edge case.

### Reporting Back — PASS
Three-step process is explicit. "Do NOT copy verdict sections verbatim — synthesize" is clearly stated.

---

## NEW gaps discovered

### NEW GAP #1 — Brainstorm trigger ambiguity when user provides exactly 3 candidates
**File:** `SKILL.md` Phase 1, step 4 / `references/interview-questions.md` Candidate brainstorm section

**Problem:** The skill says "brainstorm to fill gap to 3-6 total" and "when user provides fewer than 3 candidates." The user in this test has exactly 3 candidates. A fresh agent reading these rules literally will NOT brainstorm (3 is not fewer than 3), even though a 3-person debate is the minimum and adding 1-2 more candidates often makes the debate richer and surfaces less-obvious options.

The brainstorm seed framework in `interview-questions.md` says "when user provides <3 candidates, seed your brainstorm using these 4 axes." With 3 candidates, the agent skips the framework entirely — but the seed framework is genuinely useful even at 3+ candidates.

**Suggested fix:** Change condition in both files from `fewer than 3` / `<3` to `fewer than 4` (or `3 or fewer`), OR add a nudge: "With exactly 3 candidates, consider whether a 4th from the 'least-obvious credible' axis would strengthen the debate." The seed framework is valuable enough to use at 3 candidates; locking it behind `<3` wastes it.

---

### NEW GAP #2 — Stop signal missed if defender appends trailing blank line
**File:** `references/round-protocol.md` Dynamic Stop Signals section / `SKILL.md` Phase 4 stop-check bash command

**Problem:** The bash stop-check uses `tail -1 "$f"` to read the final line. If a defender subagent appends `<NO_NEW_POINTS>` followed by a trailing newline (which most text editors and LLM completions do by default), `tail -1` returns an empty string and the grep fails. The signal is silently missed, the orchestrator runs an unnecessary extra round.

The defender prompt says "append `<NO_NEW_POINTS>` on its own line as the LAST line of your file." A trailing newline is invisible to the LLM — it will produce one naturally. `tail -1` on a file ending in `\n<NO_NEW_POINTS>\n` returns `<NO_NEW_POINTS>` (POSIX: `tail -1` gives the last non-empty line if the last line is a newline). Actually this behavior is shell-dependent. Verify: on bash, `echo -e "foo\n<NO_NEW_POINTS>\n" | tail -1` returns empty string. On some systems it returns `<NO_NEW_POINTS>`.

**Suggested fix:** Change the grep command to scan the last 3 lines instead of just the final line:
```bash
for f in {WORKSPACE_PATH}/proposal-*.md; do
  tail -3 "$f" | grep -qE "^(<NO_NEW_POINTS>|<CONCEDE>)$" && echo "$f"
done | wc -l
```
This tolerates 1-2 trailing blank lines without introducing false positives from earlier prose (since stop signals must come at the very end, not buried mid-file). Also add a note in the defender prompt: "Do not add any blank lines after the stop signal."

---

### NEW GAP #3 — `{ROUND_N}` vs `{ROUND_COUNT}` naming inconsistency creates confusion
**File:** `agents/defender-prompt.md` (uses `{ROUND_N}`) vs `agents/judge-prompt.md` and `SKILL.md` Phase 5 (use `{ROUND_COUNT}`)

**Problem:** Defender prompt uses `{ROUND_N}` for the current round number (runtime variable per spawn). Judge prompt uses `{ROUND_COUNT}` for the total rounds completed (post-debate summary). These are different values serving different purposes, and the naming is confusingly similar. A cold-start orchestrator writing prompts could accidentally mix them up, especially when copy-pasting template snippets.

`{ROUND_N}` = current round being executed (e.g., `2` when spawning Round 2 defenders).
`{ROUND_COUNT}` = total rounds that ran (e.g., `3` when debate ended after 3 rounds).

**Suggested fix:** Rename one to reduce collision:
- Keep `{ROUND_N}` as-is in defender prompt (it's clear in context: "This is Round {ROUND_N} of the debate").
- Rename `{ROUND_COUNT}` to `{TOTAL_ROUNDS}` in the judge prompt and SKILL.md Phase 5. "Total rounds" is unambiguous; "round count" sounds like it could be a counter variable.

Update both the judge prompt variable reference table and SKILL.md Phase 5 fill-in instruction.

---

## Phase-by-phase walkthrough (continued): Windows path resolution trace

**Scenario:** User is on Windows as `garet`. Skill triggered at `2026-05-31 14:30:22`.

1. `{CLAUDE_HOME}` = `C:\Users\garet\.claude` → in subagent prompts, forward slashes: `C:/Users/garet/.claude`
2. Topic slug from "background job queue for Cloudflare Workers SaaS app":
   - Lowercase: "background job queue for cloudflare workers saas app"
   - Strip stopwords (for): "background job queue cloudflare workers saas app"
   - Hyphenate: "background-job-queue-cloudflare-workers-saas-app"
   - 43 chars — exceeds 40-char max. Truncate at word boundary before char 40: "background-job-queue-cloudflare-workers" (39 chars) ✓
3. Full workspace path: `C:/Users/garet/.claude/debates/20260531-143022-background-job-queue-cloudflare-workers/`

This traces cleanly. The skill's slugification rules (lowercase, hyphenate, strip stopwords, max 40 chars at word boundary) are sufficient to produce a deterministic slug.

---

## Brainstorm test — 4th-5th candidates

User provided 3 candidates. Applying the 4-axis seed framework from `interview-questions.md`:

| Axis | Candidate |
|------|-----------|
| Managed/hosted | ✅ Already covered: Cloudflare Queues (managed), Upstash QStash (managed) |
| Self-hosted open-source | ❌ Not covered — **Inngest** (self-hostable, open-core) or **BullMQ on Redis** (Redis-backed queue) |
| Simplest possible | ❌ Not covered — **Cloudflare D1 + cron trigger** (dead simple: store jobs in D1, Worker cron picks them up) |
| Least-obvious credible | ❌ Not covered — **Cloudflare R2 + Workers polling** (store job payloads as R2 objects, Workers poll via scheduled trigger — no external queue needed, pure Cloudflare native) OR **Temporal Cloud** (overkill for SaaS but worth including as a baseline for the Judge) |

The seed framework genuinely helped surface candidates I would not have reached by just listing "popular queue solutions." Specifically:
- "Simplest possible" axis forced me to think about native Cloudflare primitives (D1+cron) instead of dedicated queue products.
- "Least-obvious credible" prompted the R2-as-queue idea which is a real pattern used by Cloudflare-native teams.

Without the seed framework, I would have listed BullMQ and Inngest (both "self-hosted" variations) and missed the Cloudflare-native simplest path. The framework's value is highest for the "simplest" and "least-obvious" axes — the managed/self-hosted split is intuitive even without prompting.

**Proposed 4th + 5th candidates for this debate:**
- D. **D1 + Scheduled Worker (cron)** — Store job records in Cloudflare D1, scheduled Worker polls and processes. No external dependency, fits Cloudflare ecosystem, boring and predictable.
- E. **BullMQ on Upstash Redis** — Redis-backed queue via Upstash Redis (not QStash), gives full BullMQ API (retries, priorities, delayed jobs) without self-hosted infra.

---

## Overall recommendation

**SHIP IT** — with optional pre-ship fixes for GAP #2 (trailing newline) and GAP #3 (naming rename). GAP #1 is a judgment call; the current behavior is technically correct but leaves value on the table.

Priority order:
1. **GAP #2** (stop signal missed on trailing newline) — highest impact, trivial fix: `tail -3` instead of `tail -1` + one note in defender prompt
2. **GAP #3** (`{ROUND_N}` vs `{ROUND_COUNT}` rename) — low effort, prevents orchestrator confusion
3. **GAP #1** (brainstorm threshold at exactly 3) — low urgency; only matters when user provides exactly 3 candidates, and even then the debate will run fine
