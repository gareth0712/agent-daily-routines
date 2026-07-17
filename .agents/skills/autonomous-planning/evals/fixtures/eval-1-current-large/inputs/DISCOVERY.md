# Discovery Brief: Billing Administration

artifact_revision: discovery-billing-v1
repository_source: inputs/repository
repository_revision: 6e33e58b1e553a41fe22e6b941a7229a002de361
discovery_readiness: ready

## Problem and users

Small SaaS operators need reliable self-service subscription state, entitlement visibility, billing activity, and administrative diagnosis without inspecting Stripe manually. End users need clear checkout and subscription status. Support/admin staff need safe read-only diagnosis and bounded recovery actions.

## Outcomes and journeys

- An authenticated team owner can start checkout and later see current subscription and entitlement state.
- Stripe webhook delivery is idempotent and observable; duplicate or delayed events do not corrupt state.
- An admin can inspect billing events and subscription status without seeing secrets or cross-tenant data.
- Operators can detect and recover from delayed webhook processing.

## Scope

- Subscription/entitlement data model and lifecycle.
- Checkout/webhook contracts and idempotency.
- Team-owner billing UI and admin observability UI.
- Migration/backfill, tests, staged rollout, rollback, and operational signals.

## Non-goals

- Multiple payment processors.
- Usage-based billing.
- Tax calculation or invoice customization.
- Automated refunds or destructive admin actions.

## Hard constraints

- Preserve current Next.js SaaS conventions and existing Stripe integration where evidence supports them.
- Server-side authorization and tenant isolation are mandatory.
- Migrations must be additive/reversible; no production data mutation during Planning.
- Planning may propose architecture within this scope but may not change product framing or product files.

## Acceptance intent

The execution plan must map each journey and failure mode to exact implementation Task Contracts, tests, representative flows, migration/rollout evidence, and rollback points. UI stages require later human UAT after automatic verification.

## Residual unknowns and authority

- Planning owns exact interface, schema, idempotency, sequencing, migration, observability, and verification design.
- Implementation may decide only local reversible details explicitly delegated in a Task Contract.
- Any new pricing, refund, tax, retention, or customer-communication policy is a product decision and routes back to Discovery/human approval.

## Freshness evidence

The fixture `SOURCE.md` pins the upstream revision. Planning must inspect that file first, then relevant copied schema, payment, webhook, team, activity, and pricing paths. Treat any unavailable upstream surface as unavailable rather than invented.
