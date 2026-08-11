# Phase 46 — External API Coverage Declaration

No external API integration: this phase edits release-surface files only — the version literal in
`pyproject.toml`/`uv.lock`/`README.md`, the `## [0.7.1]` entry in `CHANGELOG.md`, a migration section
in `docs/source/changelog.rst`, and two data constants in existing test modules — and reads its own
repository's GitHub Actions run status through the already-installed `gh` CLI. No third-party API
client, SDK, or HTTP integration is introduced, no `typsphinx/` source file is touched, and the only
first-party script exercised (`scripts/extract_changelog_section.py`) is run as a local subprocess
against a local file.

**Why this declaration exists.** `.planning/STATE.md` records a standing note that
`api-coverage.verify-pre` false-positives on prose describing compile/render/API-read evidence (three
recorded overrides in v0.6.4). This phase's PLAN bodies are dense with `gh run view`,
`git ls-remote`, and `release.yml` prose, which is exactly that false-positive shape. The detector was
run over the phase scope at plan time and returned `{"detected":false,"signals":[]}`; this file is the
reasoned declaration for the seal-time re-run over the PLAN bodies.

**No capability matrix is supplied** because there is no external API being integrated — a reasoned
declaration with no rows is the correct form here, not an invented table.
