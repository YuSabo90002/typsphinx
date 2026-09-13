# Phase 72: `tox -e linkcheck` and Root Toctree Deduplication - Pattern Map

**Mapped:** 2026-09-13
**Files analyzed:** 8 (6 edited source/config files + 1 todo move + N evidence markdown files)
**Analogs found:** 8 / 8

All analog paths below were confirmed git-TRACKED (`git ls-files`) before being named — none is a
`.gsd/`-mirrored or otherwise gitignored copy.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|--------------------|------|-----------|-----------------|----------------|
| `tox.ini` (add `[testenv:linkcheck]`) | config | batch (build invocation) | `tox.ini:67-73` `[testenv:docs-html]` | exact (same file, adjacent section) |
| `docs/source/index.rst` (remove 5 toctree lines) | config/content | transform (doctree structure) | `docs/source/user_guide/index.rst:6-12`, `docs/source/examples/index.rst:6-10` (the toctrees that already own the children) | exact (same document family, target shape) |
| `CLAUDE.md` § Commands (add one line) | config/docs | transform (prose line insertion) | `CLAUDE.md:32-33` (`tox -e docs-html` / `tox -e docs-pdf` lines) | exact (same block, same file) |
| `README.md` dev block (add one line) | config/docs | transform | `README.md:261-263` (`uv run tox -e docs-html/docs-pdf/docs`) | exact (same block, same file) |
| `docs/source/contributing.rst` "Using Tox" block (add one line) | config/docs | transform | `docs/source/contributing.rst:123-125` (same three lines, rST code-block) | exact (same block, same file) |
| `docs/source/conf.py` (conditional `linkcheck_*` key, D-02 only) | config | request-response (HTTP timing knobs) | No existing `linkcheck_*` key in `conf.py` today (measured: none) — analog is Sphinx's own `add_config_value` calls in the installed `sphinx.builders.linkcheck` module, not project code | no analog (see below) |
| `.planning/todos/pending/2026-07-22-add-sphinx-linkcheck-ci-job.md` (append status note) | doc/config | transform (frontmatter-adjacent status note) | Same file's own `audit_acknowledged:` frontmatter block (already shows the "note appended after the fact" shape) | role-match |
| `.planning/todos/pending/2026-08-16-root-toctree-duplicates-section-children-in-html-sidebar.md` → `git mv` to `todos/completed/` | doc/config | event-driven (lifecycle transition) | No renamed-move commit found via `git log --diff-filter=R` for `.planning/todos/completed/`; use the destination directory's existing file shape as the target format, and `tox.ini`-style pure `git mv` (no content edit required beyond what D-08 asks) | no analog commit found — treat as a plain `git mv`, content unchanged except D-08's requirement |
| Phase evidence markdown (linkcheck census, toctree base/tip diff, CI dispatch, etc.) | test/evidence | transform (verbatim transcript) | `.planning/milestones/v0.9.4-phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-BASELINE-EVIDENCE.md`, `70-CI-EVIDENCE.md`; `.../71-v0-9-4-close-prep-prep-only-unpublished/71-PREFLIGHT-EVIDENCE.md` | exact |

## Pattern Assignments

### `tox.ini` — add `[testenv:linkcheck]`

**Analog:** `tox.ini:67-73`, `[testenv:docs-html]` (verified this session, verbatim):

```ini
[testenv:docs-html]
description = Build HTML documentation
runner = uv-venv-lock-runner
extras = docs
changedir = docs
commands =
    sphinx-build -b html source _build/html
```

**Core pattern to copy:** same four keys (`runner`, `extras`, `changedir`, `commands`), changing
only `description`, the `-b` flag and the output directory:

```ini
[testenv:linkcheck]
description = Check external links and anchors in the documentation (needs network)
runner = uv-venv-lock-runner
extras = docs
changedir = docs
commands =
    sphinx-build -b linkcheck source _build/linkcheck
```

**Placement:** pure insertion — append after the existing `[testenv:docs]` block (end of file) so
the diff is add-only. `env_list = py312, py313, lint, type, cov, docs` (`tox.ini:2`) stays
byte-identical — `linkcheck` must NOT be added to it (D-06: needs network, not part of a plain
`tox` run).

**No error-handling / validation pattern applies** — this is declarative INI, no logic.

---

### `docs/source/index.rst` — remove 5 duplicate toctree lines (DOC-18)

**Analog (target shape already exists two levels down):** `docs/source/user_guide/index.rst:6-12`
and `docs/source/examples/index.rst:6-10` — both already show "one toctree, children only, no
duplication," which is exactly the shape the root document should converge toward for its own two
`.. toctree::` blocks:

```rst
.. toctree::
   :maxdepth: 2

   configuration
   builders
   templates
   output_layout
```

**Current root state to edit** (`docs/source/index.rst:38-53`, verified verbatim):

```rst
.. toctree::
   :maxdepth: 2
   :caption: User Guide

   user_guide/index
   user_guide/configuration
   user_guide/builders
   user_guide/templates

.. toctree::
   :maxdepth: 2
   :caption: Examples

   examples/index
   examples/basic
   examples/advanced
```

**Target state** (only lines 43-45 and 52-53 removed; lines 42/51 — `user_guide/index` /
`examples/index` — stay):

```rst
.. toctree::
   :maxdepth: 2
   :caption: User Guide

   user_guide/index

.. toctree::
   :maxdepth: 2
   :caption: Examples

   examples/index
```

**Files to leave untouched (must be absent from the diff):**
`docs/source/user_guide/index.rst`, `docs/source/examples/index.rst`,
`typsphinx/translator.py` (constraint 2; read-only, proves the Typst side already dedupes via the
`typsphinx:include-edges` state guard at `translator.py:207,343,452-465,468-507`).

---

### `CLAUDE.md`, `README.md`, `docs/source/contributing.rst` — DOC-24 line insertion

**Analog:** each file's own immediately preceding `tox -e docs-*` lines (same file, same block —
this is a "match the neighboring line's shape" pattern, not a cross-file analog).

**`CLAUDE.md`** (`CLAUDE.md:31-33`, verbatim):
```
# Build the project's own docs (from docs/)
tox -e docs-html             # HTML via furo
tox -e docs-pdf              # PDF via the typstpdf builder (dogfoods this extension)
```
`#` starts at 0-indexed column 29. Insert last in the block:
```
tox -e linkcheck             # Check external links and anchors (needs network; not run by plain tox)
```

**`README.md`** (`README.md:261-263`, verbatim):
```
uv run tox -e docs-html     # Build HTML documentation
uv run tox -e docs-pdf      # Build PDF documentation
uv run tox -e docs          # Build both HTML and PDF docs
```
`#` starts at 0-indexed column 28. Insert last in the block:
```
uv run tox -e linkcheck     # Check external links and anchors (needs network; not run by plain tox)
```

**`docs/source/contributing.rst`** (`docs/source/contributing.rst:123-125`, verbatim, 3-space
rST code-block indent):
```
   uv run tox -e docs-html     # Build HTML documentation
   uv run tox -e docs-pdf      # Build PDF documentation
   uv run tox -e docs          # Build both HTML and PDF
```
`#` starts at 0-indexed column 31 (28 + 3-space indent). Insert last in the block:
```
   uv run tox -e linkcheck     # Check external links and anchors (needs network; not run by plain tox)
```

**Byte-identical constraint (D-06):** every existing line in each of the three blocks — including
`CLAUDE.md`'s `tox  # env_list: py312, py313, lint, type, cov, docs` line and
`contributing.rst`'s `# Run all tox environments (tests, lint, type check, docs)` comment — is left
untouched. Only one new line is added per block, at the position shown.

**Comment text (discretionary but D-05-constrained):**
`# Check external links and anchors (needs network; not run by plain tox)` — states both required
clauses (network need; not run by plain `tox`).

**Non-listing grep hits needing only a recorded disposition, not an edit:**
`.github/workflows/docs.yml:36` and `CHANGELOG.md:921` (both cite `tox -e docs-pdf` but are not
"tox environment listing surfaces" — record their disposition in evidence, do not edit them).

---

### `docs/source/conf.py` — conditional `linkcheck_*` key (D-02 only, may not be needed)

**No project analog exists** — `conf.py` currently has zero `linkcheck_*` keys (measured this
session). If D-02's condition fires (same URL transiently fails across ≥2 of the three D-01 runs),
add exactly one of `linkcheck_timeout`, `linkcheck_retries`, `linkcheck_rate_limit_timeout`, with a
comment naming the URL, status and run numbers. The **shape** to imitate is Sphinx's own config
registration (read-only reference, not something to copy into `conf.py`):

`[VERIFIED: .venv/lib/python3.13/site-packages/sphinx/builders/linkcheck.py:823]`:
```python
app.add_config_value('linkcheck_anchors', True, '', types=frozenset({bool}))
```
This confirms `linkcheck_anchors` defaults to `True` (no key needed for the 41 `#anchor` URIs to be
checked) and that these are plain Sphinx config values, nothing exotic. Follow existing `conf.py`
style for any config-value assignment (a bare `key = value` line, per the file's own convention) —
read `docs/source/conf.py` directly at execution time for the exact surrounding style before
inserting, since no `linkcheck_*` precedent exists to quote.

---

### Todos — D-07 status note and D-08 fold-and-move

**`2026-07-22-add-sphinx-linkcheck-ci-job.md`** — append a status note after QUA-13 lands. The
existing frontmatter's `audit_acknowledged:` block (`created`, `area`, `files`, then
`audit_acknowledged: { milestone, at }`) is the file's own precedent for "append dated
metadata/notes without disturbing the original Problem/Solution prose" — follow that shape for the
new status note (append as a new section or frontmatter-adjacent note, not an in-place edit of
existing sentences). Content required by D-07: environment now exists (Phase 72, QUA-13); CI job
(QUA-08, Future) still open; future pickup needs a side PR to `main` per ROADMAP constraint 4.

**`2026-08-16-root-toctree-duplicates-section-children-in-html-sidebar.md`** — `git mv` to
`.planning/todos/completed/` in the same commit as the `index.rst` edit. No prior renamed-move
commit was found via `git log --diff-filter=R -- '.planning/todos/completed/'` to quote as a literal
analog; treat this as a plain `git mv <pending-path> <completed-path>` with no content rewrite
beyond what the todo already states (its `resolves_phase: 72` frontmatter key already points here).
Destination directory convention (`.planning/todos/completed/*.md`, e.g.
`2026-08-29-inline-image-in-paragraph-emits-unseparated-expression.md`) confirms completed todos
keep their original filename and frontmatter shape — only the directory changes.

---

### Evidence markdown files (phase proof artifacts)

**Analogs:** `.../70-typing-modernization-and-its-behaviour-identity-evidence/70-BASELINE-EVIDENCE.md`,
`70-CI-EVIDENCE.md`, `70-CORPUS-DOCS-BASE-EVIDENCE.md`, `70-DOCS-DIFF-EVIDENCE.md`; and
`.../71-v0-9-4-close-prep-prep-only-unpublished/71-PREFLIGHT-EVIDENCE.md`,
`71-GREEN-TREE-EVIDENCE.md`, `71-CI-EVIDENCE.md`, `COVERAGE.md`.

**Header/`KEY = value` shape** (from `70-BASELINE-EVIDENCE.md`, verbatim):
```
# Phase 70 — Pre-conversion Baseline

BASE_70_02 = 697a113221a8a267d7e8c6dd1f2b95672f9454d2
PHASE_BASE_SHA = 697a113221a8a267d7e8c6dd1f2b95672f9454d2
SCRATCH_70_02 = /tmp/tmp.gV17Fsgks8

## Head check

Fresh measurements at the start of this plan's execution, in this worktree.

$ date -u +%FT%TZ
2026-09-13T04:25:04Z
$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-aaedef104ece8dc10
$ test -f .git; echo "exit:$?"
exit:0
$ grep -c typsphinx-fhs-run "$(command -v uv)"
2
$ git diff --name-only main HEAD -- . ':(exclude).planning'
(empty)
```

**Provisioning transcript shape** (`70-CI-EVIDENCE.md`, verbatim):
```
Provisioning command:
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs --python 3.13.13
Ran to completion; final resolved lines included `typsphinx==0.9.2 (from file:///...)`,
`ruff==0.16.6`, `uv==0.12.13`. Exit 0.
```

**Non-committing evidence disclaimer shape** (`71-PREFLIGHT-EVIDENCE.md`, verbatim, useful for any
Phase 72 evidence file that transcribes throwaway scratch builds):
```
# Phase 71 — REL-13 Update-Step Pre-Flight (D-05, non-committing)

Nothing in this file is committed to the branch except the file itself, and no merge is performed.
Every command below was re-run live from this worktree during this plan's execution — no value is
copied from `71-CONTEXT.md` or `71-RESEARCH.md`.
```
Reuse this framing for Phase 72's `PHASE_BASE_SHA`/base-tip comparison evidence, since it also
uses throwaway scratch builds (`git archive`/`git worktree`) that are not part of the tracked diff.

**Verify-command pattern reading a `KEY = value` out of an evidence file** (`71-01-PLAN.md:256`,
verbatim structure, condensed — shows the idiom to reuse for reading e.g. `LINKCHECK_TOTAL_72` or
`MULTIPLE_TOCTREES_COUNT_72` out of a Phase 72 evidence file):
```bash
k() { sed -n "s/^$1 = //p" "$F" | head -n 1; }
B="$(k BASE_71_01)"
[ "${#B}" = 40 ] && git merge-base --is-ancestor "$B" HEAD
```
And the corresponding `<fails_when>` shape (`71-01-PLAN.md:257-269`, condensed): enumerate every
distinct failure mode as its own bullet — missing/wrong worktree provisioning, a key missing or not
an ancestor SHA, a required section header absent (`missing section: <name>`), a `KEY = value` line
carrying a stray parenthesis, or a `## HALT` heading present. The `for s in '## Head check…' …; do
grep -qxF "$s" "$F" || { echo "missing section: $s"; exit 1; }; done` idiom (from the same plan) is
the reusable pattern for asserting an evidence file's required section headings exist verbatim.

**Note:** `72-VERIFICATION.md` is a reserved filename for `/gsd-verify-work` — no plan may author a
file with that exact name (per the orchestrator's constraint and this project's convention, confirmed
by `70-VERIFICATION.md`/`71-VERIFICATION.md` both being verifier-authored, never listed among their
phases' own `*-PLAN.md` action/evidence file lists).

## Shared Patterns

### Evidence-file header/footer convention
**Source:** `70-BASELINE-EVIDENCE.md`, `71-PREFLIGHT-EVIDENCE.md`
**Apply to:** every new Phase 72 evidence markdown file (linkcheck census, DOC-18 base/tip
comparison, DOC-24 grep disposition table, SC#5 CI-dispatch roll-up).
Pattern: `# Phase 72 — <short title>` heading; a `KEY = value` block for every SHA/path/count that a
later `<verify>` block or a later plan will read back; a `## Head check` section transcribing
`date -u +%FT%TZ`, `pwd -P`, `test -f .git; echo "exit:$?"`, and the `typsphinx-fhs-run` shim check;
provisioning transcript when a fresh `.venv` is needed (`env -u VIRTUAL_ENV -u
UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs --python 3.13.13`); every subsequent command
transcribed verbatim with its own `$ command` / output pairing; no value copied from CONTEXT.md or
RESEARCH.md without being re-measured live.

### Worktree isolation preamble
**Source:** CLAUDE.md § "Worktree-isolated execution"; reproduced in every Phase 70/71 evidence
file's `## Head check` section.
**Apply to:** every Phase 72 plan and evidence file.
```bash
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs
uv run tox -e linkcheck   # or: uv run pytest / uv run <tool> — everything via `uv run`
```

### `LC_ALL=C` for any grep of Sphinx console output
**Source:** CLAUDE.md § Locale; RESEARCH.md Common Pitfalls (Pitfall 3, un-prefixed grep).
**Apply to:** DOC-18's `multiple toctrees` count and `build succeeded, N warnings.` grep, and
QUA-13's `output.json`/exit-code checks.

### Verify-command `KEY = value` extraction idiom
**Source:** `71-01-PLAN.md:256` (quoted above).
**Apply to:** any Phase 72 `<verify><automated>` block that must read a prior task's recorded SHA,
count, or census value out of an evidence markdown file rather than re-deriving it.

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `docs/source/conf.py` (D-02 conditional `linkcheck_*` key) | config | request-response | No `linkcheck_*` key exists anywhere in this project's `conf.py` today; only Sphinx's own `add_config_value` registration (`sphinx/builders/linkcheck.py:823`) is available as a reference, and it documents the default rather than a project usage pattern to copy |
| `git mv` of the 2026-08-16 todo to `todos/completed/` | doc | event-driven | No prior renamed-move commit for `.planning/todos/completed/` was found via `git log --diff-filter=R`; use a plain `git mv` with unchanged content, per D-08 |

## Metadata

**Analog search scope:** `tox.ini`, `CLAUDE.md`, `README.md`, `docs/source/*.rst`,
`docs/source/conf.py`, `.planning/todos/{pending,completed}/`,
`.planning/milestones/v0.9.4-phases/{70,71}-*/`.
**Files scanned:** 8 target files/moves + ~12 evidence-file analogs across Phases 70–71.
**Pattern extraction date:** 2026-09-13
</content>
