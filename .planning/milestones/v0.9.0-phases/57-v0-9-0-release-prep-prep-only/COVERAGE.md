# Phase 57 — External API Coverage Declaration

No external API integration: this phase edits release-surface files only — the version literal in
`pyproject.toml`/`uv.lock`/`README.md`, the `## [0.9.0]` entry and tail link block in `CHANGELOG.md`,
one data constant and its adjacent comment in an existing test module, one new prose section in
`docs/source/changelog.rst`, and planning artifacts — and reads its own repository's GitHub Actions
run status, git remote refs and (for the handoff's checklist only) a sibling repository's workflow
run list through the already-authenticated `gh` and `git` clients. No third-party API client, SDK or
HTTP integration is introduced, no `typsphinx/` source file is touched (the prep-only fence holds),
and the only first-party script exercised (`scripts/extract_changelog_section.py`) is run as a local
subprocess against a local file.

**Why this declaration exists.** `.planning/STATE.md` records a standing note that
`api-coverage.verify-pre` false-positives on prose describing compile/render/API-read evidence. The
detector was run twice at plan time: over the phase scope before any PLAN existed it returned
`{"detected":false,"signals":[]}`; re-run over the finished PLAN bodies it returned `detected: true`
on a single signal, the words "API integration" inside this very declaration's own `must_haves`
citation in `57-01-PLAN.md`. That is a self-referential match, not an integration — and it is the
same shape the three recorded v0.6.4 overrides describe. This phase's PLAN bodies are additionally
dense with `gh run view`, `gh workflow run`, `git ls-remote` and `release.yml` prose, which is
exactly the false-positive surface. This file is the reasoned declaration for the seal-time re-run.

**No capability matrix is supplied** because there is no external API being integrated — a reasoned
declaration with no rows is the correct form here, not an invented table. Fabricating rows for
capabilities that do not exist would put unverifiable claims into the phase record; an `OPT-OUT`
without a real capability behind it is not a decision, it is noise.
