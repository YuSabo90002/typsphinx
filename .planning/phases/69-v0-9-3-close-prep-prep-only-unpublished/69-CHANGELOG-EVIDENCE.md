# Phase 69 Plan 01 — CHANGELOG Evidence

Measured shape: executor worktree, Phase 64 shims inherited from the session PATH; no `nix
develop`, no `direnv exec`, never the main checkout.

## Head check and provisioning

```
$ date -u +%FT%TZ
2026-09-12T22:32:19Z

$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-ab4c25ec1378d6a2a

$ test -f .git; echo "exit:$?"
exit:0

$ command -v uv
/nix/store/3vpzk25whpm7s8zq5flpk8gbpkggj9np-uv/bin/uv

$ grep -c typsphinx-fhs-run "$(command -v uv)"
2
```

Provisioning:

```
$ env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs
Using CPython 3.14.4
Creating virtual environment at: .venv
Resolved 91 packages in 0.58ms
   Building typsphinx @ file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-ab4c25ec1378d6a2a
      Built typsphinx @ file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-ab4c25ec1378d6a2a
Prepared 1 package in 456ms
Installed 90 packages in 53ms
 ... (90 packages, including tox-uv==1.36.0, tox-uv-bare==1.36.0, uv==0.12.13, myst-parser==5.1.0,
      furo==2025.12.19, sphinx-intl==2.3.2, sphinx-autodoc-typehints==3.0.1)
```

Both extras synced without error.

```
BASE_69_01 = 2db4e803d36d5f7a5db0a92b08cac4988fa88957

$ cat .venv/pyvenv.cfg
home = /home/yuta/.local/share/uv/python/cpython-3.14-linux-x86_64-gnu/bin
implementation = CPython
uv = 0.11.25
version_info = 3.14
include-system-site-packages = false
prompt = typsphinx
```

PYVENV_HOME_69_01 = /home/yuta/.local/share/uv/python/cpython-3.14-linux-x86_64-gnu/bin
PYVENV_VERSION_69_01 = 3.14

## Pre-edit measurements

Taken before touching `CHANGELOG.md`.

```
$ grep -cE '^## \[' CHANGELOG.md
23
```
HEADINGS_BEFORE = 23

```
$ grep -cE '^\[[^]]+\]: https' CHANGELOG.md
23
```
LINKREFS_BEFORE = 23

```
$ awk '/^## \[0\.9\.2\]/{exit} f; /^## \[Unreleased\]/{f=1}' CHANGELOG.md | grep -cE '^- \*\*'
0
```
UNRELEASED_BOLD_BEFORE = 0

```
$ grep -c '0\.9\.3' CHANGELOG.md
0
```
V093_BEFORE = 0

```
$ awk '/^### Planned for Future Releases$/{f=1} /^## \[0\.9\.2\]/{exit} f' CHANGELOG.md | sha256sum
a3436143cc65050f0aa709bbdc02b8fa31ab6d8f58c2c4aa198cbc10e0911f02  -
```
PLANNED_SHA_BEFORE = a3436143cc65050f0aa709bbdc02b8fa31ab6d8f58c2c4aa198cbc10e0911f02

Verbatim final line:
```
[Unreleased]: https://github.com/YuSabo90002/typsphinx/compare/v0.9.2...HEAD
```

All five pre-edit measurements match the planning-time census in `69-01-PLAN.md`'s planning-time
table (23 release headings, 23 link-reference lines, 0 real change bullets under
`## [Unreleased]`, 0 hits for `0.9.3`, and the tail line ending `v0.9.2...HEAD`) — confirming
D-03's premise that this is authoring from scratch, not promotion.

## What this file is NOT

`scripts/extract_changelog_section.py` is deliberately NOT invoked in this phase. There is no
versioned `## [0.9.3]` (or any other new) section for it to extract — SC#2 and D-03 keep this
milestone's bullets under `## [Unreleased]`, unpromoted. D-11 records that the next release-prep
phase runs the extractor and promotes these bullets into a versioned section when it closes,
exactly as Phase 61's `## [Unreleased]` bullets were promoted by Phase 63.

## Docs baseline — pre-edit, clean builds

Both baselines were taken BEFORE touching `CHANGELOG.md`, each preceded by `rm -rf docs/_build`
so the count reflects a full rebuild, not an incremental one.

Command:
```
$ rm -rf docs/_build && uv run tox -e docs-html
```

Verbatim tail:
```
build succeeded, 3 warnings.

HTMLページは_build/htmlにあります。
  docs-html: OK (3.46=setup[0.10]+cmd[3.37] seconds)
  congratulations :) (3.49 seconds)
```

`WARNING` lines (all four are the pre-existing `visit_toctree` docstring rendering, unrelated to
`CHANGELOG.md`):
```
22::21: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
44::21: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
418::6: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
445:/home/yuta/Documents/typsphinx/.claude/worktrees/agent-ab4c25ec1378d6a2a/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:6: WARNING: Block quote ends without a blank line; unexpected unindent. [docutils]
```

DOCS_HTML_WARN_BASE = 3

Command:
```
$ rm -rf docs/_build && uv run tox -e docs-pdf
```

Verbatim tail:
```
typst: wrote 1 wrapper file(s) -- compile these: typsphinx.typ
Compiling 1 master document(s) to PDF...
Generated PDF: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-ab4c25ec1378d6a2a/docs/_build/pdf/typsphinx.pdf
build succeeded, 5 warnings.
  docs-pdf: OK (3.82=setup[0.10]+cmd[3.72] seconds)
  congratulations :) (3.84 seconds)
```

`WARNING` lines (the same four docstring warnings, plus two `doctest_block` unknown-node-type
warnings pre-existing in the PDF builder path):
```
22::21: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
44::21: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
418::6: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
445:/home/yuta/Documents/typsphinx/.claude/worktrees/agent-ab4c25ec1378d6a2a/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:6: WARNING: Block quote ends without a blank line; unexpected unindent. [docutils]
456:WARNING: unknown node type: <doctest_block classes="doctest" xml:space="preserve">>>> compute_content_include_path("", "index.typ")
462:WARNING: unknown node type: <doctest_block classes="doctest" xml:space="preserve">>>> compute_template_import_path("typst", "base.typ")
```

DOCS_PDF_WARN_BASE = 5

```
$ head -c 5 docs/_build/pdf/typsphinx.pdf
%PDF-
```

Both counts (3 / 5) match the historical cross-check cited in the plan's planning-time census
(Phase 61 and Phase 63 closes). An incremental rebuild under-reports warnings, which is why both
counted builds start from an empty `docs/_build`.

## The TOX bullet (tracer slice)

Inserted immediately below `## [Unreleased]`, one blank line on each side of the new `### Changed`
heading, above the existing `### Planned for Future Releases` (left untouched):

```markdown
### Changed

- **Contributor tooling returns to `tox-uv` from `tox-uv-bare` (TOX-01, TOX-02, TOX-03, TOX-04).**
  The `dev` extra and `tox.ini`'s `requires` line once again name `tox-uv`, with `uv.lock`
  regenerated in the same change. This has no effect on installing or using typsphinx. A CI run
  dispatched against the branch carrying this change was green across the Linux, Windows and
  macOS test lanes.
```

No lead paragraph and no `### Verified` subsection were written (D-04). `tox-uv-bare` is named
only as the previous state — this bullet is a dated record, not one of the toolchain-pin sync
points `CLAUDE.md` lists, so no other file changes with it.

## Accuracy basis

| Claim in the TOX bullet | Evidence file / section |
|---|---|
| `dev` extra and `tox.ini`'s `requires` line name `tox-uv` again, in place of `tox-uv-bare` | `65-REVERT-EVIDENCE.md` § "TOX-01 lock regeneration" (the one-token pin swap in both files) |
| `uv.lock` regenerated in the same change | `65-REVERT-EVIDENCE.md` § "TOX-01 lock regeneration" (`uv lock` output: `Added tox-uv v1.36.0` / `Updated tox-uv-bare v1.35.2 -> v1.36.0` / `Added uv v0.12.13`) and § "Revert commit" (all four files — `pyproject.toml`, `tox.ini`, `uv.lock`, `tests/test_toolchain_config_gate.py` — landed in one commit) |
| No effect on installing or using typsphinx | This is a `dev`-extra / tox-runner change only; `typsphinx`'s own runtime dependencies are untouched by either file (`65-REVERT-EVIDENCE.md`'s diff touches only the `dev` extra line and the tox requires line) |
| CI run dispatched against the branch was green across Linux, Windows and macOS | `65-CI-EVIDENCE.md` § "Job census" (all twelve jobs `success`), § "windows-latest lanes" and § "macos-latest lanes" (both OS's two Python lanes each `success`), run `34681968010`, conclusion `success` |

## Docs render — tracer slice

Command:
```
$ rm -rf docs/_build && uv run tox -e docs-html
```

Verbatim tail:
```
build succeeded, 3 warnings.

HTMLページは_build/htmlにあります。
  docs-html: OK (2.41=setup[0.01]+cmd[2.40] seconds)
  congratulations :) (2.43 seconds)
```

`WARNING` lines (identical set to the baseline, only the docstring line-numbers within the
CHANGELOG-including `changelog` page's own upstream file shifted by the 8-line insertion — no new
warning, no warning naming the `changelog` page):
```
21::21: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
43::21: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
417::6: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
444:/home/yuta/Documents/typsphinx/.claude/worktrees/agent-ab4c25ec1378d6a2a/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:6: WARNING: Block quote ends without a blank line; unexpected unindent. [docutils]
```

DOCS_HTML_WARN_TRACER = 3

`DOCS_HTML_WARN_TRACER` (3) equals `DOCS_HTML_WARN_BASE` (3), and the set of `WARNING` lines is
the same four pre-existing `visit_toctree` docstring warnings — none names the `changelog` page.
The TOX bullet's MyST renders through `docs/source/changelog.rst`'s
`.. include:: ../../CHANGELOG.md` with `:parser: myst_parser.sphinx_` without introducing any new
warning.

## Pure-addition check (Task 1 slice)

```
$ git diff BASE_69_01 -- CHANGELOG.md
```

Verbatim output:
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 5d8266cd..02661407 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -7,6 +7,14 @@ and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0
 
 ## [Unreleased]
 
+### Changed
+
+- **Contributor tooling returns to `tox-uv` from `tox-uv-bare` (TOX-01, TOX-02, TOX-03, TOX-04).**
+  The `dev` extra and `tox.ini`'s `requires` line once again name `tox-uv`, with `uv.lock`
+  regenerated in the same change. This has no effect on installing or using typsphinx. A CI run
+  dispatched against the branch carrying this change was green across the Linux, Windows and
+  macOS test lanes.
+
 ### Planned for Future Releases
 - BibTeX/bibliography support
 - Glossary generation
```

Zero lines in this diff begin with a single `-` followed by a non-`-` character — no source line
was removed. `### Planned for Future Releases` and every historical release section survive
byte-identical, and the tail link-reference block is untouched (confirmed above:
`PLANNED_SHA_BEFORE` recorded before this edit; re-confirmed equal in Task 2's evidence after the
remaining two bullets land).

This evidence file continues in Task 2 with the DEP and NIX bullets, the full pure-addition proof
over both tasks' combined diff, the fence assertions, and both docs environments rebuilt clean a
final time against this baseline.

## The DEP and NIX bullets

Re-ran the head check and `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra
docs` at the start of Task 2 — `Resolved 91 packages`, `Checked 90 packages` (no drift from Task 1's
sync).

Inserted after the TOX bullet, before `### Planned for Future Releases`:

```markdown
- **Dependabot's Python dependency updates now use the `uv` ecosystem instead of `pip` (DEP-01,
  DEP-02, DEP-03, DEP-04, DEP-05).** Each dependency pull request now updates `pyproject.toml` and
  `uv.lock` in the same commit, so CI's `uv sync --locked` step succeeds and the test, lint and
  type jobs actually run against it; before the switch, every such pull request stopped at that
  step before any test ran. The grouping, labels and pull-request limit carry over unchanged. This
  was proven on the pull request that also carried a routine `ruff` version bump. This has no
  effect on installing or using typsphinx.

- **A NixOS development shell (NIX-01, NIX-02, NIX-03, NIX-04, NIX-05, NIX-06, NIX-07, NIX-08,
  DOC-19, DOC-20, DOC-21).** `flake.nix` now puts command shims for `uv`, `tox`, `ruff`, `black`,
  `mypy`, `pytest` and `sphinx-build` on `PATH`; each one runs the checkout's own `.venv` tools
  inside an FHS sandbox, so the versions `uv.lock` pins run on NixOS without any manual step. This
  applies only to contributors who enter that shell on NixOS; CI and every other platform are
  unchanged, and this has no effect on installing or using typsphinx. The `darwin` systems evaluate
  under this shell but remain unverified. `CLAUDE.md`'s contributor notes, the `tox.ini` comment
  and the `flake.nix` header now describe the mechanism.
```

The DEP bullet does not claim an observed `sphinx-typst-stack` grouped update under `uv` (that
coverage gap is recorded, not closed, per `67-CLOSURE-EVIDENCE.md`'s `UV_GROUP_PR_COUNT = 0`), and
it does not call the ruff-carrying pull request the first — it is named only as the one on which
the mechanism was proven. The NIX bullet does not claim CI coverage of `flake.nix` and does not
use either of the two manual-step words Phase 68 confined to `CLAUDE.md`.

## Accuracy basis

| Claim in the TOX bullet | Evidence file / section |
|---|---|
| `dev` extra and `tox.ini`'s `requires` line name `tox-uv` again, in place of `tox-uv-bare` | `65-REVERT-EVIDENCE.md` § "TOX-01 lock regeneration" (the one-token pin swap in both files) |
| `uv.lock` regenerated in the same change | `65-REVERT-EVIDENCE.md` § "TOX-01 lock regeneration" (`uv lock` output: `Added tox-uv v1.36.0` / `Updated tox-uv-bare v1.35.2 -> v1.36.0` / `Added uv v0.12.13`) and § "Revert commit" (all four files landed in one commit) |
| No effect on installing or using typsphinx | This is a `dev`-extra / tox-runner change only; `typsphinx`'s own runtime dependencies are untouched by either file |
| CI run dispatched against the branch was green across Linux, Windows and macOS | `65-CI-EVIDENCE.md` § "Job census" (all twelve jobs `success`), § "windows-latest lanes" and § "macos-latest lanes" (both OS's two Python lanes each `success`), run `34681968010`, conclusion `success` |

| Claim in the DEP bullet | Evidence file / section |
|---|---|
| Dependabot's Python updates use the `uv` ecosystem instead of `pip` | `66-DEPENDABOT-EVIDENCE.md` § "Requirement closure" row DEP-01 MET (`.github/dependabot.yml`'s uv line) |
| Each pull request updates `pyproject.toml` and `uv.lock` in the same commit, so CI's `uv sync --locked` step succeeds and test/lint/type jobs run | `67-PROOF-EVIDENCE.md` § "Per-step reads" — all eight D-01 jobs' `Install dependencies` step `success`; `uv sync --locked` succeeds and the jobs run to completion |
| Before the switch, every such pull request stopped at that step before any test ran | `66-RESEARCH.md`'s own framing that `pip`-ecosystem PRs never regenerate `uv.lock` and always fail `--locked` (the reason DEP-02 could not be proven on a `pip` PR) |
| Grouping, labels and pull-request limit carry over unchanged | `66-DEPENDABOT-EVIDENCE.md` § "Requirement closure" row DEP-03 MET (§ D-06 observations: grouping, exclusions, labels, `open-pull-requests-limit`, lockfile-only PRs, `ruff` range) |
| Proven on the pull request that also carried a routine `ruff` version bump | `67-CLOSURE-EVIDENCE.md` § "Requirement closure" row DEP-02 MET, citing `67-PROOF-EVIDENCE.md`'s `DEP02_VERDICT = MET` on PR #138 (the same PR STATE.md records as carrying the `ruff` 0.15.20 → 0.16.6 bump) |
| No effect on installing or using typsphinx | This changes only the Dependabot configuration ecosystem identifier; no runtime dependency of `typsphinx` is affected |
| No observed grouped update under `uv` (not claimed) | `67-CLOSURE-EVIDENCE.md` line `UV_GROUP_PR_COUNT = 0` — the coverage gap this bullet deliberately does not claim closed |

| Claim in the NIX bullet | Evidence file / section |
|---|---|
| `flake.nix` puts command shims for `uv`, `tox`, `ruff`, `black`, `mypy`, `pytest` and `sphinx-build` on PATH | `68-CLOSURE-EVIDENCE.md` § "SC#3 reading" (`flake.nix` header block: "Exactly the seven bare commands `CLAUDE.md` documents are shimmed: `uv`, plus the six names in `venvShimNames`") |
| They run the checkout's own `.venv` tools inside an FHS sandbox, so the pinned versions run on NixOS without a manual step | `64-VERIFICATION.md` § "Requirements Coverage" rows NIX-01..NIX-05 SATISFIED (`ruff check .` reports the `uv.lock`-pinned version; fresh-worktree provisioning needs no manual step) |
| Applies only to contributors on NixOS; CI and every other platform are unchanged | `68-CLOSURE-EVIDENCE.md` § "SC#3 reading" flake.nix header ("only when the host platform is Linux"); no workflow under `.github/workflows/` references `nix` or `flake` (ROADMAP constraint 8, restated in `69-CONTEXT.md`'s domain section) |
| The darwin systems evaluate but are unverified | `68-CLOSURE-EVIDENCE.md` § "SC#3 reading" flake.nix header comment ("the darwin shell itself has never been built or entered ... unverified by construction") |
| `CLAUDE.md`, `tox.ini` and `flake.nix` now carry the contributor notes | `68-CLOSURE-EVIDENCE.md` § "Requirement closure" rows DOC-19/DOC-20/DOC-21 all MET |
| No effect on installing or using typsphinx | The shim mechanism only wraps contributor-invoked commands on the maintainer's NixOS machine; it changes no installed or published artifact |

## Discretion exercised

- The `ruff`-carrying pull request (#138) is named as the one on which the DEP mechanism was
  proven, per D-05's explicit discretion. It is not called the first such pull request — the
  bullet makes no ordinal claim at all.
- No `### Verified` subsection is authored this phase (D-04). The next release-prep phase writes
  it against its own whole diff when these bullets are promoted into a versioned section, exactly
  as Phase 63 did for Phase 61's bullets.
- Bullet order follows D-01's literal ordering: TOX, then DEP, then NIX.

## Pure-addition proof

Command:
```
$ git diff 2db4e803d36d5f7a5db0a92b08cac4988fa88957 -- CHANGELOG.md
```

Verbatim output:
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 5d8266cd..73a8428e 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -7,6 +7,31 @@ and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0
 
 ## [Unreleased]
 
+### Changed
+
+- **Contributor tooling returns to `tox-uv` from `tox-uv-bare` (TOX-01, TOX-02, TOX-03, TOX-04).**
+  The `dev` extra and `tox.ini`'s `requires` line once again name `tox-uv`, with `uv.lock`
+  regenerated in the same change. This has no effect on installing or using typsphinx. A CI run
+  dispatched against the branch carrying this change was green across the Linux, Windows and
+  macOS test lanes.
+
+- **Dependabot's Python dependency updates now use the `uv` ecosystem instead of `pip` (DEP-01,
+  DEP-02, DEP-03, DEP-04, DEP-05).** Each dependency pull request now updates `pyproject.toml` and
+  `uv.lock` in the same commit, so CI's `uv sync --locked` step succeeds and the test, lint and
+  type jobs actually run against it; before the switch, every such pull request stopped at that
+  step before any test ran. The grouping, labels and pull-request limit carry over unchanged. This
+  was proven on the pull request that also carried a routine `ruff` version bump. This has no
+  effect on installing or using typsphinx.
+
+- **A NixOS development shell (NIX-01, NIX-02, NIX-03, NIX-04, NIX-05, NIX-06, NIX-07, NIX-08,
+  DOC-19, DOC-20, DOC-21).** `flake.nix` now puts command shims for `uv`, `tox`, `ruff`, `black`,
+  `mypy`, `pytest` and `sphinx-build` on `PATH`; each one runs the checkout's own `.venv` tools
+  inside an FHS sandbox, so the versions `uv.lock` pins run on NixOS without any manual step. This
+  applies only to contributors who enter that shell on NixOS; CI and every other platform are
+  unchanged, and this has no effect on installing or using typsphinx. The `darwin` systems evaluate
+  under this shell but remain unverified. `CLAUDE.md`'s contributor notes, the `tox.ini` comment
+  and the `flake.nix` header now describe the mechanism.
+
 ### Planned for Future Releases
 - BibTeX/bibliography support
 - Glossary generation
```

Zero lines in this diff begin with a single `-` followed by a non-`-` character:
```
$ git diff 2db4e803d36d5f7a5db0a92b08cac4988fa88957 -- CHANGELOG.md | grep -cE '^-[^-]'
0
```

REMOVED_LINE_COUNT = 0

## Fence assertions

```
$ grep -cE '^## \[' CHANGELOG.md
23
```
HEADINGS_AFTER = 23 (equal to HEADINGS_BEFORE)

```
$ grep -cE '^\[[^]]+\]: https' CHANGELOG.md
23
```
LINKREFS_AFTER = 23 (equal to LINKREFS_BEFORE)

```
$ awk '/^## \[0\.9\.2\]/{exit} f; /^## \[Unreleased\]/{f=1}' CHANGELOG.md | grep -E '^- \*\*' | wc -l
3
```
UNRELEASED_BOLD_AFTER = 3

```
$ awk '/^## \[0\.9\.2\]/{exit} f; /^## \[Unreleased\]/{f=1}' CHANGELOG.md | grep -oE '(TOX-0[1-4]|DEP-0[1-5]|NIX-0[1-8]|DOC-(19|20|21))' | sort -u | wc -l
20
```
UNRELEASED_IDS_AFTER = 20

```
$ R="$(awk '/^## \[0\.9\.2\]/{exit} f; /^## \[Unreleased\]/{f=1}' CHANGELOG.md)"
$ J="$(printf '%s\n' "$R" | tr '\n' ' ' | tr -s ' ')"
$ printf '%s\n' "$J" | grep -oi 'no effect on installing or using typsphinx' | wc -l
3
```
NO_EFFECT_PHRASES = 3

```
$ grep -c '0\.9\.3' CHANGELOG.md
0
```
V093_AFTER = 0

```
$ awk '/^### Planned for Future Releases$/{f=1} /^## \[0\.9\.2\]/{exit} f' CHANGELOG.md | sha256sum
a3436143cc65050f0aa709bbdc02b8fa31ab6d8f58c2c4aa198cbc10e0911f02  -
```
PLANNED_SHA_AFTER = a3436143cc65050f0aa709bbdc02b8fa31ab6d8f58c2c4aa198cbc10e0911f02 (equal to
PLANNED_SHA_BEFORE)

```
$ grep -cE 'patchelf|ln -sf' CHANGELOG.md
0
```
MANUAL_STEP_WORDS = 0

Also recorded:

Verbatim final line, identical to the base's:
```
$ tail -n 1 CHANGELOG.md
[Unreleased]: https://github.com/YuSabo90002/typsphinx/compare/v0.9.2...HEAD
```

```
$ sed -n 7p pyproject.toml
version = "0.9.2"
```

The region's `###` heading list:
```
$ awk '/^## \[0\.9\.2\]/{exit} f; /^## \[Unreleased\]/{f=1}' CHANGELOG.md | grep -E '^### '
### Changed
### Planned for Future Releases
```

Empty lead-paragraph check:
```
$ awk '/^### Changed$/{exit} f; /^## \[Unreleased\]/{f=1}' CHANGELOG.md | grep -c .
0
```

```
$ git status --porcelain typsphinx/ tests/ docs/ pyproject.toml uv.lock
(empty)
```

Manual-step word confinement, over the whole tree outside `.planning/`:
```
$ git grep -lE 'patchelf|ln -sf' -- . ':(exclude).planning'
CLAUDE.md
```

Exactly one file (`CLAUDE.md`), matching the planning-time census — neither word leaked into
`CHANGELOG.md` or any other tracked file.

## Docs render — post-edit, clean builds

Command:
```
$ rm -rf docs/_build && uv run tox -e docs-html
```

Verbatim tail:
```
build succeeded, 3 warnings.

HTMLページは_build/htmlにあります。
  docs-html: OK (2.40=setup[0.01]+cmd[2.39] seconds)
  congratulations :) (2.42 seconds)
```

`WARNING` lines (identical set to the baseline — the four pre-existing `visit_toctree` docstring
warnings, no warning naming the `changelog` page):
```
21::21: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
43::21: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
417::6: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
445:/home/yuta/Documents/typsphinx/.claude/worktrees/agent-ab4c25ec1378d6a2a/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:6: WARNING: Block quote ends without a blank line; unexpected unindent. [docutils]
```

DOCS_HTML_WARN_POST = 3 (equal to DOCS_HTML_WARN_BASE)

Command:
```
$ rm -rf docs/_build && uv run tox -e docs-pdf
```

Verbatim tail:
```
typst: wrote 1 wrapper file(s) -- compile these: typsphinx.typ
Compiling 1 master document(s) to PDF...
Generated PDF: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-ab4c25ec1378d6a2a/docs/_build/pdf/typsphinx.pdf
build succeeded, 5 warnings.
  docs-pdf: OK (2.95=setup[0.01]+cmd[2.94] seconds)
  congratulations :) (2.97 seconds)
```

`WARNING` lines (identical set to the baseline — the four docstring warnings plus the two
pre-existing `doctest_block` unknown-node-type warnings):
```
21::21: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
43::21: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
417::6: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
444:/home/yuta/Documents/typsphinx/.claude/worktrees/agent-ab4c25ec1378d6a2a/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:6: WARNING: Block quote ends without a blank line; unexpected unindent. [docutils]
455:WARNING: unknown node type: <doctest_block classes="doctest" xml:space="preserve">>>> compute_content_include_path("", "index.typ")
461:WARNING: unknown node type: <doctest_block classes="doctest" xml:space="preserve">>>> compute_template_import_path("typst", "base.typ")
```

DOCS_PDF_WARN_POST = 5 (equal to DOCS_PDF_WARN_BASE)

```
$ head -c 5 docs/_build/pdf/typsphinx.pdf
%PDF-
```

Both counts (3 / 5) equal their clean pre-edit baselines, with the same warning sets in each case,
and the PDF starts `%PDF-`. `scripts/extract_changelog_section.py` was not run (see § "What this
file is NOT"); only `CHANGELOG.md` and this evidence file changed across both tasks of this plan.

## Requirement closure (coverage only)

| Requirement | Status | Deciding section |
|---|---|---|
| REL-12 | FENCED, not closed | This plan does not touch REL-12's checkbox; its SUMMARY declares `requirements-completed: []`. REL-12 closes only at `/gsd-complete-milestone`. |

TOX-01..04, DEP-01..05, NIX-01..08 and DOC-19..21 are cited here for the CHANGELOG bullets' accuracy
basis only — their own closure already happened in Phases 64-68 and is not re-decided by this plan.
