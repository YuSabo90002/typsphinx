# Phase 67: Proof on a Real Dependabot PR, Then Disposal of #123 and #128 - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-12
**Phase:** 67-proof-on-a-real-dependabot-pr-then-disposal-of-123-and-128
**Areas discussed:** DEP-02 evidence source, ruff disposal (#123/#138), docutils disposal (#128), SC#4 premise correction

Before the questions, the owner asked what DEP-02 actually requires; it was explained against
DEP-01 (PR contents, closed in Phase 66) vs DEP-02 (the PR's CI outcome), with #138's step-level
results shown. The owner then chose to discuss all four areas.

---

## DEP-02 evidence source

| Option | Description | Selected |
|--------|-------------|----------|
| Read existing run | #138's own run 34689041575 (dependabot-triggered in Phase 66); step logs already show Install dependencies and Run lint/type/tests success; zero external action | ✓ |
| Rerun on same head | `gh run rerun 34689041575` → attempt 2 on head 8808807; initiator becomes the owner | |
| Have dependabot recreate | `@dependabot rebase`/`recreate` on #138 → new head; behaviour with unchanged `main` unmeasured; differs from Phase 66's SC1_SHA | |

**User's choice:** Read existing run

---

## ruff disposal (#123/#138)

| Option | Description | Selected |
|--------|-------------|----------|
| Merge #138, close #123 | dev-only tool; no new violations under 0.16.6; REL-12 conflict-free; NIX-01's 0.15.20 stays as a measurement record | ✓ |
| Close both, stay on 0.15 | keep the toolchain NIX-01 measured; revisit ruff 0.16 next milestone | |
| Close #123 only, leave #138 open | SC#3 would have to be read as satisfied via #123 alone | |

**User's choice:** Merge #138, close #123

| Option | Description | Selected |
|--------|-------------|----------|
| Leave to REL-12 | no main→milestone merge now; measured: ruff 0.16.6 `ruff check .` passes on milestone tip in FHS; merge-tree clean | ✓ |
| Merge main into milestone right after | milestone and local .venv move to 0.16.6 mid-milestone; main-checkout sync needs docs extra restored | |

**User's choice:** Leave to REL-12

---

## docutils disposal (#128)

| Option | Description | Selected |
|--------|-------------|----------|
| Close with reason comment | terse English comment citing Sphinx 9.1.0's docutils<0.23 cap and the uv resolution failure; owner approves text | ✓ |
| Close without comment | reason recorded only in .planning evidence | |
| Leave open | would require amending SC#3 ("merged or closed with reason") | |

**User's choice:** Close with reason comment

---

## SC#4 premise correction

| Option | Description | Selected |
|--------|-------------|----------|
| AMENDED blocks in ROADMAP/PROJECT | append owner-approved AMENDED blocks after SC#4 and PROJECT.md:124; original text kept; REQUIREMENTS.md DEP-05 untouched | ✓ |
| Correct only in Phase 67 records | leave ROADMAP/PROJECT literal; verifier reports literal and actual | |

**User's choice:** AMENDED blocks in ROADMAP/PROJECT

---

## Claude's Discretion

- Merge method for #138; merge-then-close order; a terse "Superseded by #138." comment on #123;
  transcribing every job's conclusion; evidence file naming and plan split.

## Deferred Ideas

- Lockfile-only uv PRs #139–#142 (outside DEP-05's text).
- docutils 0.23 adoption once Sphinx relaxes its cap.
- `versioning-strategy` tuning (carried from Phase 66).
- PROJECT.md's "will need closing so uv opens fresh ones" claim, superseded by measurement — for the milestone-close PROJECT.md update.
