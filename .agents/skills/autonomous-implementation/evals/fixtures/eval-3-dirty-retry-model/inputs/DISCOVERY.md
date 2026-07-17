# Discovery

discovery_revision: eval3-discovery-r1
repository_revision: eval3-repository-baseline-r1
freshness_evidence: named configuration behavior and repository surfaces remain current; first-attempt code is an Implementation-owned change
Planning readiness: READY

## Framing

- User: an operator configuring local notification delivery.
- Outcome: textual configuration values `true` and `false` are interpreted safely and predictably.
- In scope: exact boolean and case-insensitive trimmed string forms.
- Out of scope: arbitrary truthy values, remote configuration, UI, persistence, delivery providers, deployment, and secret changes.
- Acceptance intent: false-like strings never enable notifications accidentally; unsupported values fail closed.
- Hard constraints: preserve the exported API and user draft; no external effects or dependencies.
- Residual unknowns: none required before Implementation.
