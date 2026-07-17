# Cold-Start Test Report — garen-debate skill

**Test prompt:** /garen-debate I'm building a real-time notification system for a Next.js SaaS app and not sure on architecture

---

## Verdict

- **Could a fresh Claude run this skill end-to-end?** PARTIALLY
- **Estimated quality of debate this would produce:** MEDIUM
- **Gaps blocking adoption:** 4 major, 7 minor

---

## Phase-by-phase analysis

### Phase 1: Interview

**What I would do:**

Extract from the user's initial message:
- Decision: notification architecture for a Next.js SaaS app
- Candidates mentioned: 0
- Constraints stated: none
- Stack: Next.js (inferred)

Send one batched message (up to 4 questions):

> 幾個問題幫我了解背景：
>
> 1. **Scenario** — 這是新功能還是要替換現有方案？通知是 server → client 單向 push，還是需要雙向？
> 2. **Scale** — 預計同時上線用戶數？（粗估即可，例如 < 1k、1k–50k、50k+）
> 3. **Constraints** — 有預算上限、部署平台限制（Vercel/Cloudflare/AWS）、或現有 infra 必須整合的嗎？
> 4. **Deal-breaker** — 最在乎什麼？（latency < 100ms、不想維護 WebSocket server、成本、某 vendor 不能用？）

After user answers, brainstorm candidates (since user provided 0):

> 以下是這個場景的主要候選方案：
> - **A. SSE (Server-Sent Events)** — HTTP long-lived stream，Next.js Route Handler 原生支援，server → client 單向
> - **B. WebSocket (自架，e.g. Socket.io / ws)** — 雙向全雙工，需獨立 server 或 adapter
> - **C. Polling (Long / Short)** — 最簡單，periodic fetch，無 persistent connection
> - **D. Managed Push Service (Pusher / Ably)** — 零 infra，per-message 計費
> - **E. Supabase Realtime** — Postgres CDC-based，若已用 Supabase 極低摩擦
>
> Reject 任何不適合的。補充我漏掉的。

Confirm full summary, then wait for user OK before Phase 2.

**What was clear in the skill:**

- `references/interview-questions.md` gives a concrete question bank organized by category (Scenario, Constraints, Success criteria, Out of scope). The batching rule (≤4 per message) is explicit.
- The brainstorm template ("Beyond what you mentioned…") is word-for-word in `interview-questions.md` lines 61-65.
- The confirmation block format (lines 79-94) is a complete template — no guessing needed.
- `CONTEXT_SUMMARY` output format (lines 102-112) is explicitly defined.

**Ambiguity / had to guess:**

1. **Brainstorm seed list not provided.** The skill says "brainstorm to fill gap to 3-6" but gives zero domain examples for the notification space. I had to generate SSE / WebSocket / Polling / Pusher / Ably / Supabase from general knowledge. If the topic were unusual (e.g., "embedded firmware OTA update strategy"), a cold-start agent with weaker domain knowledge would produce weak or irrelevant candidates. **GAP: skill has no seed list, no examples, no guidance on how to brainstorm.**
2. **"Stay within user's tech ecosystem"** (interview-questions.md line 71) — user only said "Next.js SaaS". I don't know if they're on Vercel, have a DB, use Supabase, etc. I'd have to ask. The skill doesn't tell me how to handle the case where ecosystem is completely unknown.
3. **Number of candidates to target.** Skill says "3-6 total." I brainstormed 5. Acceptable. But if user rejects 3 of them, am I supposed to brainstorm replacements? Skill is silent on iteration.

---

### Phase 2: Setup + Cost Guard

**What I would do:**

1. Slugify topic: "real-time-notification-architecture-nextjs"
2. Generate workspace path:
   ```
   ~/.claude/debates/20260531-143022-real-time-notification-architecture-nextjs/
   ```
3. Create the directory.
4. Run cost estimate (mentally, or via Bash):
   ```bash
   bash S:\git\15-skills\garen-agent-skills\skills\garen-debate\scripts\estimate-cost.sh 4 5
   ```
   Output: 4 defenders × 5 rounds + 1 judge = 21 calls, ~$1.13–$1.70 USD

5. Show to user:
   > 預計 spawn 4 agents × ~5 rounds = 21 calls，~$1.13–$1.70 美元（Sonnet pricing）。確認繼續？

Wait for explicit yes/no.

**What was clear in the skill:**

- Workspace path template (`~/.claude/debates/{YYYYMMDD-HHMMSS}-{topic-slug}/`) is explicit in SKILL.md line 55.
- The cost confirmation message template is word-for-word in SKILL.md line 66.
- Script path is given. Arguments are documented.
- "Wait for explicit confirmation" and "offer to reduce defenders or rounds" on decline are explicit.

**Ambiguity / had to guess:**

4. **Slugification rules not defined.** "real-time notification system for a Next.js SaaS app" needs to become a slug. The skill says `{topic-slug}` but never defines: lowercase? hyphens? max length? Strip "for a"? I guessed `real-time-notification-architecture-nextjs`. A different agent would produce a different slug. Minor inconsistency but annoying for reproducibility.
5. **Timestamp collision.** The skill says nothing about what to do if `~/.claude/debates/20260531-143022-<slug>/` already exists. If the user runs the same debate twice within the same second (or if the system clock hasn't changed), the directory exists. `mkdir` will silently succeed (directory already exists) but old files might contaminate the new debate. **GAP: no collision-handling instruction.**
6. **Windows path vs `~` expansion.** On Windows, `~/.claude/debates/` may expand to `C:\Users\garet\.claude\debates\`. The defender/judge prompts embed `{WORKSPACE_PATH}` — if this is a Unix `~` path on a Windows machine, the subagent may fail to create/read files. **MAJOR GAP: no platform path handling guidance.**
7. **Script uses `bc`.** The script has a fallback for missing `bc`, but on Windows PowerShell / Git Bash the fallback integer math may underflow to 0 for small costs (e.g., `COST_LOW_INT=1` → `$1`). Not critical but the displayed estimate can be misleading.

---

### Phase 3: Round 1 — Opening Proposals

**What I would do:**

Assume 4 candidates confirmed: A=SSE, B=WebSocket+Socket.io, C=Managed Push (Pusher/Ably), D=Supabase Realtime.

Spawn 4 defender subagents in PARALLEL. Prompt for Defender A:

```
You are Defender A, championing the approach **SSE (Server-Sent Events)** in a structured multi-agent debate.

Topic: Choose the real-time notification architecture for a Next.js SaaS app
Context:
  Topic: Choose the real-time notification architecture for a Next.js SaaS app
  Candidates: A=SSE, B=WebSocket+Socket.io, C=Managed Push (Pusher/Ably), D=Supabase Realtime
  Constraints: Vercel deployment, team comfortable with Next.js, budget <$50/mo, scale ~5k concurrent users
  Success criteria: Low operational complexity, notifications delivered <500ms, no dedicated infra to maintain
  Out of scope: none stated

Your task:
Write your opening proposal to: C:/Users/garet/.claude/debates/20260531-143022-real-time-notification-nextjs/proposal-a.md

Follow the Round 1 format exactly as specified in:
S:\git\15-skills\garen-agent-skills\skills\garen-debate\references\round-protocol.md
(Read the "Round 1 (Opening)" section.)

You believe in this approach — make the strongest honest case for it.
Acknowledge real tradeoffs. Judges see through marketing. Proposals that omit limitations lose credibility.

Target length: 150-300 words.
Do NOT read other proposal files — they don't exist yet, and even if they did, this round is independent.
```

**What was clear in the skill:**

- `agents/defender-prompt.md` contains the complete Round 1 template. All `{VARIABLE}` slots are defined with examples in the Variable Reference table.
- The instruction "Defenders do NOT read other proposals this round" is in both SKILL.md and `round-protocol.md`.
- The "PARALLEL" dispatch requirement is explicit.

**Ambiguity / had to guess:**

8. **`{LETTER}` is uppercase in the variable reference ("A, B, C") but `proposal-{letter}.md` uses lowercase ("proposal-a.md") in SKILL.md line 83 and the round-protocol.** This is a direct contradiction. The defender prompt says `Write your opening proposal to: {WORKSPACE_PATH}/proposal-{LETTER}.md` — if LETTER="A" then the file is `proposal-A.md`, but the grep command in Phase 4 uses `proposal-*.md` which would still match. However the judge prompt also says `proposal-*.md`. Inconsistent casing between variable definition and usage. **MINOR GAP but can cause file not found if grep or the judge looks for lowercase.**
9. **Model not specified in defender prompt template.** The skill says "spawn subagents" but never tells the orchestrator what model to use for defenders. SKILL.md Phase 5 says "Sonnet judge agent" explicitly. Nothing says Sonnet vs Haiku for defenders. Given CLAUDE.md rules (Haiku for mechanical, Sonnet for reasoning), I'd guess Sonnet — but I'm guessing. **GAP: model not specified for defenders.**
10. **No `subagent_type` specified.** The skill doesn't say whether to use `subagent_type: agent`, a Task tool call, etc. In Claude Code's actual dispatch mechanism the orchestrator needs to know how to spawn. Skill is silent on this. A cold-start agent reading only these files would not know the dispatch mechanism.

---

### Phase 4: Round 2-N — Debate Rounds

**What I would do:**

After Round 1 proposals exist:

Round 2 — spawn all 4 defenders in PARALLEL. Prompt for Defender A:

```
You are Defender A, championing **SSE (Server-Sent Events)**. This is Round 2 of the debate.

Topic: Choose the real-time notification architecture for a Next.js SaaS app
Context: [CONTEXT_SUMMARY as above]

Your task — execute in this order:

1. Read ALL proposal files in: C:/Users/garet/.claude/debates/20260531-143022-.../proposal-*.md
2. Read the Round 2-N format in:
   S:\git\15-skills\garen-agent-skills\skills\garen-debate\references\round-protocol.md
3. APPEND a `## Round 2 Update` section to: .../proposal-a.md
   DO NOT overwrite or delete any previous content. Only append.

[hard requirements, optional concession, stop signals as per template]
```

After all 4 finish, scan for stop signals:
```bash
grep -l "<NO_NEW_POINTS>\|<CONCEDE>" C:/Users/garet/.claude/debates/20260531-143022-.../proposal-*.md | wc -l
```
If count ≥ 2, stop. Otherwise proceed to Round 3.

**What was clear in the skill:**

- Round 2-N prompt template is complete in `agents/defender-prompt.md`.
- The grep command is given verbatim in SKILL.md line 104.
- "Never overwrite previous rounds" is repeated in both SKILL.md and round-protocol.md.
- Hard rules table in `round-protocol.md` (≥1 Defense, ≥1 Counter-attack, ≥1 Strengthening, ≤250 words) is explicit.

**Ambiguity / had to guess:**

11. **False-positive stop signal detection.** The grep pattern `<NO_NEW_POINTS>\|<CONCEDE>` will match ANY occurrence in the file — including a defender saying "Proposal B's use of `<NO_NEW_POINTS>` after Round 2 was premature because...". A defender might quote an opponent's stop signal as part of their counter-attack. The grep counts file matches (`-l`), not line matches, but a file with a quoted signal still counts. **MAJOR GAP: grep pattern can produce false positives; skill should specify line-anchored matching or require signals on their own line at EOF.**
12. **Snapshot race condition.** Phase 4 says "snapshot at round start — do not re-read mid-round." But SKILL.md gives no mechanism to enforce this. All defenders are spawned in parallel; Defender B starts reading files at the same time Defender A starts writing. If Defender A is fast, Defender B's read of `proposal-a.md` might include A's Round 2 update before the round officially ends. This creates inconsistent snapshots within the same round. **MAJOR GAP: no read-before-write ordering or snapshot isolation mechanism described.**
13. **`wc -l` on Windows.** The grep command uses `wc -l`. On Windows Git Bash this works, but in PowerShell it does not. Skill uses bash syntax throughout but target OS is Windows. **MINOR GAP: no OS note.**
14. **`{ROUND_N}` variable not incremented by skill explicitly.** The skill says the orchestrator runs rounds sequentially but never says "increment `{ROUND_N}` counter and track current round number in orchestrator state." Obvious to a human but a cold-start agent needs to track this somewhere — skill doesn't say where or how. Minor but a fresh agent might forget to update the round number in the prompt.

---

### Phase 5: Judge Verdict

**What I would do:**

Spawn single Sonnet judge agent using judge-prompt.md:

```
You are the Judge in a multi-agent debate on: **Choose the real-time notification architecture for a Next.js SaaS app**

Context: [CONTEXT_SUMMARY]

Your task — execute in this order:
1. Read ALL proposal files in: C:/Users/garet/.claude/debates/20260531-.../proposal-*.md
2. Read the verdict template from:
   S:\git\15-skills\garen-agent-skills\skills\garen-debate\references\verdict-template.md
3. Write your verdict to: C:/Users/garet/.claude/debates/20260531-.../verdict.md

[evaluation criteria, hybrid note, "be decisive", All Agent Points requirements as per template]
```

**What was clear in the skill:**

- Judge prompt template in `agents/judge-prompt.md` is complete.
- Evaluation criteria order (4 weighted factors) is explicit in both `judge-prompt.md` and `verdict-template.md` — no ambiguity.
- "Spawn exactly ONE judge agent" is called out in orchestrator notes.
- Verdict template structure is fully specified with no optional sections.

**Ambiguity / had to guess:**

15. **Judge has no round count passed.** The judge prompt does NOT include `{ROUND_COUNT}` or "the debate ran N rounds." The judge must infer the round count by reading how many `## Round N Update` sections exist in each file. This works, but if a proposal file is malformed or a defender skipped a round numbering, the judge may miscount. A `{TOTAL_ROUNDS}` variable would make this explicit. **MINOR GAP.**
16. **No model specified for judge either.** `judge-prompt.md` orchestrator notes say "Judge is Sonnet model" — this is stated. But the defender orchestrator notes do not. Consistency gap.

---

### Reporting Back to User

**What I would do:**

After verdict.md is confirmed written:

> 辯論結束。
>
> **Verdict 位置：** `C:/Users/garet/.claude/debates/20260531-143022-real-time-notification-nextjs/verdict.md`
>
> **Summary:** [1-paragraph I generate by reading the "Winner" and "Why this proposal won" sections of verdict.md]
>
> 完整辯論記錄在 `C:/Users/garet/.claude/debates/20260531-143022-real-time-notification-nextjs/` — 每個 proposal-*.md 都有 round-by-round 的演進過程。

**What was clear in the skill:**

- The three reporting steps (path, summary, reminder) are explicit in SKILL.md lines 127-131.
- "1-paragraph summary: winner, key reason, top alternative to borrow from" gives clear content requirements.

**Ambiguity / had to guess:**

17. **"Generate that yourself or extract from verdict.md?"** SKILL.md says "Print a 1-paragraph summary: winner, key reason, top alternative to borrow from." verdict.md has a `## Winner` section and a `## What's worth borrowing from losing proposals` section. The skill does NOT say whether to copy from those sections or synthesize fresh prose. I would read verdict.md and synthesize from those two sections — but a cold-start agent that takes "print a summary" literally might print the raw Winner section verbatim, which is only 1 sentence, not a paragraph. **MINOR GAP: clarify "synthesize from verdict sections" vs "copy."**

---

## Stress-test results

| # | Concern | Result | Note |
|---|---------|--------|------|
| 1 | Trigger match | PASS | "not sure on architecture" is explicitly listed in skill description and trigger list. No ambiguity. |
| 2 | Phase 1 interview — minimum question set | PARTIAL | Skill gives a full question bank and batching rule. But does not tell you which 4 to prioritize when user gave near-zero context. A cold-start agent must decide which 4 to pick first. |
| 3 | Phase 1 brainstorm — seeding candidates from scratch | FAIL | Skill says brainstorm to 3-6 but gives zero domain examples, no seed list, no guidance on how to find candidates for the topic. Cold-start agent relies purely on internal knowledge. Low-domain topics will get weak candidates. |
| 4 | Phase 2 cost guard — exact number and confirmation prompt | PASS | Script math is deterministic. N=4, max=5 → 21 calls → $1.13–$1.70. Confirmation template is word-for-word. |
| 5 | Phase 3 workspace — exact path and timestamp collision | PARTIAL | Path template is explicit. Slugification rules are undefined. Collision handling is absent. |
| 6 | Phase 3 defender spawning — exact prompt assembly | PASS | Prompt template and variable reference are complete. A defender prompt can be assembled mechanically. |
| 7 | Phase 4 dynamic stop — grep pattern, false positives | FAIL | Grep is given but will false-positive on quoted signals in counter-attack prose. No line-anchoring or EOF requirement specified. |
| 8 | Phase 4 snapshot race — parallel defenders reading in-progress writes | FAIL | Skill says "snapshot at round start" but gives no enforcement mechanism. Parallel spawning can cause Defender B to read Defender A's in-progress writes. |
| 9 | Phase 5 judge — round count passed? | PARTIAL | Round count is NOT passed to judge. Judge infers from file content. Works in happy path; fragile on malformed files. |
| 10 | Report back — summarize from verdict.md or generate fresh? | PARTIAL | Skill says "print a 1-paragraph summary" but does not specify whether to copy verdict sections or synthesize. Ambiguous enough that different agents would behave differently. |

---

## Concrete gap list

1. **SKILL.md / Phase 1 — No brainstorm seed list.** Skill says "brainstorm to fill gap to 3-6" with zero examples or domain guidance. A cold-start agent for an unfamiliar topic will produce low-quality candidates. **Fix:** Add a 1-paragraph note in `interview-questions.md`: "Seed your brainstorm by listing: (a) managed/hosted option, (b) self-hosted open-source, (c) simplest possible option, (d) least-obvious credible option. Always include the obvious mainstream choice even if it's probably wrong."

2. **SKILL.md line 104 — Grep false-positive on quoted stop signals.** `grep -l "<NO_NEW_POINTS>\|<CONCEDE>"` matches files where the signal appears in prose (e.g., a defender quoting an opponent's signal in their counter-attack). **Fix:** Require signals on their own line at the end of the file and add `grep -c "^<NO_NEW_POINTS>\|^<CONCEDE>"` or anchor-match: `grep -P "^<(NO_NEW_POINTS|CONCEDE)>"`.

3. **SKILL.md Phase 4 / defender-prompt.md orchestrator notes — No snapshot isolation mechanism.** "Snapshot at round start" is stated but not enforced. Parallel defenders can read files being concurrently written. **Fix:** Add explicit orchestrator step: "Wait for all Round N-1 writes to complete before spawning Round N defenders. Because subagents are spawned sequentially in the orchestrator loop, this is satisfied automatically as long as you confirm all N-1 defenders have finished before dispatching Round N."

4. **SKILL.md Phase 3 and defender-prompt.md Variable Reference — `{LETTER}` case inconsistency.** Variable Reference says "A, B, C" (uppercase) but the proposal file is `proposal-{letter}.md` (lowercase in SKILL.md body text). The prompt template says `proposal-{LETTER}.md`. **Fix:** Standardize to lowercase throughout. Change variable reference example to `a`, `b`, `c` and prompt template to `proposal-{letter}.md`.

5. **SKILL.md Phase 2 — No slugification rules.** `{topic-slug}` is undefined: max length, allowed chars, how to strip stopwords. **Fix:** Add one line: "Slugify by lowercasing, replacing spaces and special chars with hyphens, stripping leading articles (a/an/the), max 40 chars."

6. **SKILL.md Phase 2 — No timestamp collision handling.** If the directory already exists, old proposal files contaminate the new debate. **Fix:** Add: "If directory already exists, append `-2`, `-3`, etc. to the slug until the path is unique."

7. **SKILL.md / All phases — Windows path: `~/.claude/debates/` is not valid on Windows.** The workspace path uses Unix `~` notation. On Windows, `~` expands differently in PowerShell vs Bash. Subagents running on Windows may fail to resolve the path. **Fix:** Add a platform note: "On Windows, expand `~` to `$env:USERPROFILE` (PowerShell) or `$HOME` (Git Bash). Use forward slashes in all paths passed to subagents." And mention that the estimate-cost.sh script must be run via Git Bash, not PowerShell.

8. **agents/defender-prompt.md — No model specified for defenders.** Judge prompt orchestrator notes say "Judge is Sonnet model" but defender notes say nothing. **Fix:** Add one line to orchestrator notes: "Spawn defenders as Sonnet model — they need reasoning, not just retrieval."

9. **SKILL.md Phase 5 — Judge has no `{ROUND_COUNT}` context.** Judge must infer round count from file content. **Fix:** Pass `{ROUND_COUNT}` as an additional variable and add to judge prompt: "The debate ran {ROUND_COUNT} rounds." Low-cost fix, eliminates one inference step.

10. **SKILL.md Reporting Back — "print a 1-paragraph summary" is ambiguous.** Does not say whether to extract from verdict.md or synthesize fresh. **Fix:** Change to: "Read `verdict.md` and synthesize a 1-paragraph summary covering: (1) which proposal won and the single most decisive reason, (2) one specific idea worth borrowing from a losing proposal."

11. **estimate-cost.sh line 29 — Pricing hardcoded to Sonnet 4.5 at $3/$15 per million tokens.** Sonnet pricing has changed across versions (claude-sonnet-4-6, claude-sonnet-4-7). The script will silently produce stale estimates. **Fix:** Add a comment warning: "# PRICING: Update INPUT_PRICE/OUTPUT_PRICE when switching models. Current: Sonnet 4.5. Check https://anthropic.com/pricing before running with a new model."

---

## Things the skill got right

- **Round protocol is production-quality.** The `round-protocol.md` format — Defense / Counter-attack / Strengthening / Concession, with explicit cite requirements, word cap, and no-overwrite rule — is exactly what prevents defender agents from writing marketing fluff. The Judge evaluation criteria matching the protocol sections means the debate output directly feeds the verdict. This is well-designed end-to-end.

- **Cost guard is genuinely useful and mechanically complete.** The script, the exact confirmation message template, and the "offer to reduce if declined" fallback are all there. A user running this for the first time gets a real USD estimate before spending tokens. Most skills skip this entirely.

- **Verdict template closes the loop.** The "Honest Limitations" and "What's worth borrowing" sections prevent the Judge from pretending the winner is perfect. The "All Agent Points" audit trail requirement means the verdict is traceable. These sections were clearly designed by someone who had read bad AI verdicts before.
