# Discovery

discovery_revision: eval2-discovery-r1
repository_revision: eval2-repository-r1
freshness_evidence: repository/SOURCE.md and named source/test/UI surfaces at eval2-repository-r1
Planning readiness: READY

## Framing

- User: a support operator reviewing unread workspace activity.
- Outcome: see the most recent unread events in the existing dashboard and later mark one read.
- Primary journey: open dashboard, scan unread events in newest-first order, confirm exact labels/timestamps, then acknowledge an item after the reviewed UI is accepted.
- In scope: local activity data, existing dashboard panel, and local read-state command.
- Out of scope: authentication, remote API, persistence service, notifications, deployment, analytics, and broad redesign.
- Acceptance intent: accessible semantic list, honest empty state, deterministic order, human visual acceptance before dependent read-state work.
- Hard constraints: existing editorial layout and no third-party packages.
- Residual unknowns: visual preference is owned by the scheduled UAT gate; no pre-Implementation product decision remains.
