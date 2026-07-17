# Agent State

protocol_version: autonomous-artifacts-v2
workflow_type: planning
run_id: old-online-plan
repository_revision: abc123
discovery_artifact_path: DISCOVERY.md
discovery_revision: discovery-online-v1
planning_artifact_path: MASTER-PLAN.md
planning_revision: plan-online-v1
planning_readiness: ready
implementation_readiness: ready
next_stage: STOP
completed_weight: 2
session_budget: 6

| packet | status | report |
|---|---|---|
| P-001 | verified | reports/P-001-report.md |

The referenced report, evidence directory, event stream, and freshness evidence are absent. This state is intentionally unsupported.
