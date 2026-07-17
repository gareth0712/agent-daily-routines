# Interview Questions

Script for Phase 1: extracting the information needed to set up a well-structured debate.

---

## Pre-extraction: read the user's message first

Before asking anything, extract what you can from the user's initial message:
- What decision are they making? (scenario context)
- Any candidates they already mentioned?
- Any constraints already stated?
- Any success criteria implied?

Only ask about what's still missing. Never ask for information already provided.

---

## What must be extracted

| Item | Why it matters |
|------|---------------|
| Scenario context | Scopes the debate — defenders need to know what they're optimizing for |
| Constraints | Disqualifies candidates and shapes tradeoff dimensions |
| Success criteria | Lets Judge score "fit to constraints" accurately |
| Candidate approaches | The proposals that defenders will champion |
| Out of scope | Prevents defenders from recommending non-starters |

---

## Question bank

Batch up to 4 questions per message. Adapt wording based on context (casual vs. technical user).

### Scenario (ask if unclear)
- What system or feature is this decision for? (1-3 sentences)
- What's the current state — are you building from scratch, or migrating/replacing something existing?

### Constraints (ask for what's unknown)
- What's the budget range? (ballpark is fine — "under $50/mo", "company card, no limit", etc.)
- What's the team's experience level with each candidate? (e.g., "comfortable with Docker, never used K8s")
- What scale are you planning for? (requests/sec, users, data volume — any rough estimate)
- Are there deadline or compliance constraints? (e.g., "must ship in 2 weeks", "HIPAA required")
- Any existing tooling that the solution must integrate with or can't break?

### Success criteria (ask if not clear from context)
- What does "good" look like in 6 months? What's the primary goal — cost, speed, reliability, maintainability?
- What's the deal-breaker? (e.g., "can't have more than 100ms latency", "can't require a DBA")

### Out of scope (ask if needed)
- Anything explicitly off the table? (e.g., "we can't use AWS — company policy", "no vendor lock-in")

---

## Candidate brainstorm

When user provides fewer than 4 candidates (i.e., 0-3), brainstorm to fill the gap to 3-6.

User-provided candidates are usually the obvious choices. Brainstorming 1-2 additional candidates from the 4-axis framework consistently improves debate quality even when user already provided 3.

Present as:
> Beyond what you mentioned, I'd add these candidates:
> - **{Name A}** — {1-sentence description}
> - **{Name B}** — {1-sentence description}
> - **{Name C}** — {1-sentence description}
>
> Reject any you don't want. Add others I missed.

Brainstorm guidelines:
- Include the obvious mainstream option even if you suspect it's not best — it validates the winner's case if it gets eliminated fairly
- Include at least one "unconventional" option if credible — it often forces the mainstream options to articulate their real advantages
- Stay within the user's tech ecosystem (don't suggest AWS if they're a Cloudflare shop)
- Cap at 6 total candidates — debates with 7+ defenders become unwieldy and expensive

## Brainstorm seed framework

When user provides <4 candidates (i.e., 0-3), seed your brainstorm using these 4 axes — try to fill ALL of them before stopping:

1. **Managed / hosted** — vendor service that abstracts infra (e.g., Pusher, Vercel KV, Auth0, Cloudflare D1)
2. **Self-hosted open-source** — runs on user's own infra (e.g., Socket.io, PostgreSQL + Drizzle, Lucia, MeiliSearch)
3. **Simplest possible** — the boring path (e.g., polling, JSON file, cron job, direct DB query)
4. **Least-obvious credible** — alternative the user probably didn't consider but real teams use (e.g., Postgres LISTEN/NOTIFY for pubsub, SQLite for SaaS storage, edge functions instead of containers)

Always include the obvious mainstream choice even if it's probably wrong for this user — gives Judge a baseline to compare against.

If the topic is outside your domain knowledge, ASK the user: "What approaches have you seen others use for this? Even if you've rejected them, name them so I can include them as candidates."

---

## Confirmation before Phase 2

After extracting all required information, confirm with user:

> Here's what I have:
>
> **Topic:** {1-sentence description}
>
> **Candidates ({N} total):**
> A. {Name} — {1-sentence}
> B. {Name} — {1-sentence}
> C. {Name} — {1-sentence}
>
> **Constraints:** {bullet list}
>
> **Success criteria:** {bullet list}
>
> **Out of scope:** {bullet list or "none stated"}
>
> Ready to proceed to Phase 2 (cost estimate + debate setup)?

Wait for confirmation before moving on.

---

## Context summary format

After Phase 1, produce a `CONTEXT_SUMMARY` string for use in defender and judge prompts:

```
Topic: {1 sentence}
Candidates: A={Name}, B={Name}, C={Name}, ...
Constraints: {comma-separated list}
Success criteria: {comma-separated list}
Out of scope: {comma-separated list or "none"}
```

This summary is embedded verbatim in every defender and judge prompt.
