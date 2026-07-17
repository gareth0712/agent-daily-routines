# Fixture provenance

- Upstream: `https://github.com/nextjs/saas-starter`
- Upstream revision: `6e33e58b1e553a41fe22e6b941a7229a002de361`
- Retrieved: 2026-07-14 with a read-only shallow Git clone
- License: MIT; the upstream `LICENSE` file is copied verbatim
- Nature: selected real source/document copies for an isolated Discovery eval, not a runnable fork and not synthetic product stubs

## Copied evidence surfaces

- `README.md` and `package.json`
- `lib/db/schema.ts`, `lib/db/queries.ts`, and the initial SQL migration
- `lib/payments/stripe.ts` and `lib/payments/actions.ts`
- Stripe checkout and webhook route handlers
- team API route, pricing page, and activity page

The selected slice is intentionally incomplete. Discovery must distinguish inspected facts from missing repository areas, and must not claim the fixture proves behavior outside these copied paths.
