---
created: 2026-08-04
title: "REL-04 is unproven end to end: `release.yml`'s `create-release` job failed on the v0.7.0 tag push with `uv: command not found`"
area: ci, release
resolves_phase: 46
severity: warning
source: v0.7.0 milestone close (/gsd-complete-milestone) — release run 30848860064
files:

  - .github/workflows/release.yml (the `create-release` job)

audit_acknowledged:
  milestone: v0.9.1
  at: 2026-08-29
---

## Problem

REL-04 requires the GitHub Release body to be the curated `## [X.Y.Z]` CHANGELOG section rather than
a `git log --pretty` commit dump. Phase 41 (plan 41-01) delivered the mechanism — a stdlib-only,
positional extractor at `scripts/extract_changelog_section.py`, pytest-covered, wired into
`release.yml` — and removed the commit dump rather than fencing it.

Its **first real tag push failed**. Release run `30848860064` for `v0.7.0`:

```
validate       ✓ 2m41s
build          ✓ 13s
publish-pypi   ✓ 17s   (PyPI typsphinx 0.7.0 published)
create-release ✗ 10s   Generate release notes → uv: command not found (exit 127)
```

Root cause: the `create-release` job runs

```yaml
run: uv run python scripts/extract_changelog_section.py "${TAG#v}" > release_notes.md
```

but that job has **no `astral-sh/setup-uv` step**. `validate` and `build` both install uv;
`create-release` never needed it before REL-04 wired the extractor into it. `41-HANDOFF.md` item 1
had explicitly flagged this tag push as "the first moment that check exercises in anger" — it was,
and it broke.

Consequence at the time: PyPI published fine, but the GitHub Release was left as the empty-bodied,
`typsphinx.pdf`-only entry `docs.yml` creates — no curated notes, no wheel, no sdist.

## What was already done at the v0.7.0 close

- `release.yml`'s `create-release` job gained the missing `Install uv` + `Set up Python` steps on
  `main` (owner decision: match the other jobs rather than drop `uv run`).

- The `v0.7.0` GitHub Release was repaired **by hand**: renamed to `Release v0.7.0`, body set to the
  extractor's output for `0.7.0` + the Installation block + GitHub's auto-generated notes, and the
  wheel (122,514 B) and sdist (477,342 B) uploaded alongside the existing `typsphinx.pdf`.

- REL-04 was reverted to `[ ]` / Pending in `milestones/v0.7.0-REQUIREMENTS.md` and recorded as
  v0.7.0's one Known Gap, because the *automation* has still never produced the body — only a human
  has.

## What is still owed

REL-04 closes when a **real tag push** runs `create-release` to completion and the resulting release
body is the curated CHANGELOG section with no hand editing. That cannot be manufactured; it happens
at the next release.

## Acceptance

- The next `v*` tag push produces a green `create-release` job in its release run.
- The resulting GitHub Release body begins with the curated `## [X.Y.Z]` CHANGELOG section (not a
  `git log` dump, not empty), and its assets include the wheel and the sdist.

- No hand editing of that release is performed before the check.
- REL-04 is then marked Complete in the milestone that observes it.

## Worth considering alongside

A rehearsal path for `create-release` — e.g. a `workflow_dispatch` variant that renders
`release_notes.md` and uploads it as an artifact without creating a release — would let this job be
exercised without an irreversible tag. Its absence is why a job-level defect survived a phase that
hand-ran the script, pytest-covered it, and statically read the YAML.
