# Phase 66: `.github/dependabot.yml` — `pip` → `uv` Ecosystem - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-12
**Phase:** 66-github-dependabot-yml-pip-uv-ecosystem
**Areas discussed:** Delivering the config to `main`, #123/#128 exposure

Findings presented before the first question (measured via `gh api`): dependabot reads
`dependabot.yml` only from the default branch (`about-the-dependabot-yml-file.md:46`); dependabot-core
runs uv 0.12.7 while GitHub's table still says v0.11; #128 is a grouped PR; lockfile-only PRs may
appear under `uv`.

---

## Delivering the config to `main`

| Option | Description | Selected |
|--------|-------------|----------|
| A | Separate `dependabot.yml`-only PR to `main` in Phase 66; constraint 2 gets an AMENDED block | ✓ |
| B | Milestone branch only; real-PR observation (SC#1 tail + Phase 67) after REL-12, roadmap restructured | |
| C | Other (e.g. temporarily switch default branch — not recommended) | |

**User's choice:** A

---

## #123/#128 exposure when the `pip` entry leaves `main`

| Option | Description | Selected |
|--------|-------------|----------|
| H1 | Replace `pip` with `uv` outright; snapshot #123/#128 before/after merge; any auto-close is mechanical | ✓ |
| H2 | Add `uv`, keep `pip` temporarily; protects the PRs but departs from SC#1 wording and keeps failing `pip` PRs | |

**User's choice:** H1

---

## Claude's Discretion

Proposed defaults stated to the owner with no objection: DEP-04 closed by source + real-PR lock
evidence with REQUIREMENTS wording kept literal; no waiting for the Monday schedule (owner clicks
"Check for updates" if needed); DEP-03 carried unchanged with no new keys, behaviour recorded;
byte-identical content on both branches, English terse PR. Also: PR branch name, merge method,
evidence naming, plan split, polling duration.

## Deferred Ideas

- Phase 67 SC#4 / PROJECT.md "neither is grouped" claim is false (#128 is grouped).
- `versioning-strategy` tuning if lockfile-only PR volume crowds the limit.
