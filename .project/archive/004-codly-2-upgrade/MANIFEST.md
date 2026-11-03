# Archive — 004-codly-2-upgrade

Milestone: codly-2-upgrade
Shipped: 2026-11-03
Final verdict: all criteria met; project verify passed
Waves: 1  Tasks: 3 done / 3 total  Review cycles used: 1
Carried forward: none

## Success criteria at ship

| Criterion | Verdict | Evidence |
|-----------|---------|----------|
| Package pin: `typsphinx/typst_deps.py` `DEFAULT_PACKAGES` names `@preview/codly:2.0.0`, and a `typst` build of `tests/roots/test-basic` writes `<outdir>/_typsphinx/deps.typ` whose codly import line is `@preview/codly:2.0.0` and whose `typsphinx-init` contains no 1.3-only call (`codly-init`, a state-setting `codly(` call) and no `show raw` rule that converts raw blocks to codly (E9: user-written raw blocks are left to Typst's ordinary rendering); `tests/test_preview_version_sync.py` passes with the spec literal appearing only in `typst_deps.py`. | met | typsphinx/typst_deps.py:93; .project/build/verify-ledger.jsonl (commit ae1565f2); .project/review/final-gap-1.md |
| Code-mode emission (surface: generated content .typ files): in the content `.typ` files produced by `typst` builds of `tests/roots/test-basic`, `examples/basic`, `examples/advanced` and `docs/source`, every Sphinx code block (literal_block and doctest_block, including blocks inside captioned figures, list items, admonitions and table cells) is one `codly.new(raw(...), ...)` expression. Absence check over those same output files: `grep -rn '```'` and `grep -rnE '(^\|[^.a-z-])codly\('` both return no match. | met | tests/test_codly2_output_gate.py; tests/test_codly2_render_gate.py; .project/intent/INTENT.md C5; .project/review/wave-1.cycle1.md (T002/AC1-AC3, AC7, AC8) |
| Options reflected (surface: typstpdf PDF output): in the PDF built by `typstpdf` from a fixture covering each option, a block without `:linenos:` shows no line numbers; a block with `:linenos:` shows line numbers starting at 1; `:lineno-start: N` makes the first displayed number N; `:emphasize-lines:` highlights exactly the named lines (including when combined with `:lineno-start:`); and a block with a language shows codly 2.0's language badge. Visual styling (colors, radius, badge look) is codly 2.0's default, not a recreation of 1.3's look. | met | tests/fixtures/codly2_render_gate/index.rst; tests/test_codly2_render_gate.py; .project/review/wave-1.cycle1.md (T002/AC4, AC5, AC9-AC11) |
| Captioned code blocks: a `code-block` with `:caption:` and `:name:` still renders as a numbered listing-kind figure with its caption (numbered in the listing sequence, separate from image figures), and a `:ref:`/`:numref:` to its name resolves in the PDF. | met | tests/test_codly2_render_gate.py; .project/review/wave-1.cycle1.md (T002/AC6) |
| Builds compile: `typstpdf` builds of `examples/basic`, `examples/advanced`, both `examples/charged-ieee` approaches, and the project docs (`tox -e docs-pdf`) complete without error. | met | .project/tasks/T003-*.md Log; .project/review/wave-1.cycle1.md (T003/AC1); .project/build/verify-ledger.jsonl (ae1565f2) |
| Contract docs (surface: docs user guide templates page): `docs/source/user_guide/templates.rst` lists the names `/_typsphinx/deps.typ` exports for codly 2.0 and describes what `typsphinx-init` now sets up; `CHANGELOG.md` `## [Unreleased]` records the codly 2.0.0 upgrade as a breaking change with a migration note for templates that imported `codly`/`codly-init` from deps.typ, and states that raw blocks written by users (custom templates, `.. raw:: typst`) are no longer rendered through codly by `typsphinx-init` (E9). | met | docs/source/user_guide/templates.rst:150-198; CHANGELOG.md `## [Unreleased]` (Breaking codly entry); .project/review/wave-1.cycle1.md (T001/AC6) |
| charged-ieee fix-code: the PDF built from `examples/charged-ieee` approach1 has the project title (not "Paper Title") as its paper title, so the README's identical-output claim holds. | met | examples/charged-ieee/approach1/conf.py:67; tests/test_examples_charged_ieee_gate.py |
| advanced README fix-doc: `examples/advanced/README.md` states that seealso renders through `#tip` and shows the inline-math form the translator actually emits. | met | examples/advanced/README.md:138,207; tests/test_examples_typstpdf_gate.py |
| On the final HEAD, `LC_ALL=C uv run pytest tests/` (with `--extra dev --extra docs` installed) reports 0 failed, and `black --check .`, `ruff check .`, `mypy typsphinx/` are clean. | met | .project/build/verify-ledger.jsonl (commit ae1565f28a43b152c7599f7aed92d661b428e59f); .project/review/final-gap-1.md (Gap verdict: pass) |

## Contents

- build/evidence.json
- build/verify-ledger.jsonl
- intent/INTENT.md
- plan/PLAN.md
- research/DOCS-AUDIT.md
- research/RESEARCH.md
- research/SYNTHESIS.md
- research/evidence-codebase.md
- research/evidence-pitfalls.md
- research/evidence-stack.md
- review/FINAL.md
- review/final-gap-1.md
- review/wave-1.cycle1.md
- tasks/T001-codly2-deps-and-code-mode-emission.md
- tasks/T002-codly2-surface-gates.md
- tasks/T003-examples-pdf-builds-and-audit-rulings.md

## Notes

- none
