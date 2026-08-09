# Phase 45 — API Coverage Declaration

No external API integration: this phase edits published documentation prose, adds a build-time
Sphinx parser plugin (`myst-parser`) to the `docs` extra, consolidates one `logger.warning` call
site inside `typsphinx/template_engine.py`, and verifies HTML-comment balance in a planning record —
no REST/GraphQL/gRPC endpoint, SDK, OAuth flow, webhook or MCP server is called, wrapped or consumed
at any point.

Detector result at plan time: `api-coverage.cjs --json` over the ROADMAP Phase 45 scope returned
`{"detected": false, "signals": []}`. This declaration is recorded pre-emptively because the
seal-time gate re-scans the PLAN bodies, which contain ordinary English uses of "integration",
"wiring" and "consume" describing Sphinx build plumbing rather than an external service — the same
false-positive class STATE.md already records three accepted overrides for in v0.6.4.

The one new external artifact this phase pulls in is a PyPI package, not an API: `myst-parser>=5.0`,
gated by a blocking human package-legitimacy checkpoint in `45-01-PLAN.md` and audited in
`45-RESEARCH.md` § Package Legitimacy Audit.
