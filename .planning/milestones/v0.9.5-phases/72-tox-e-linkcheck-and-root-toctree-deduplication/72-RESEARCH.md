# Phase 72: `tox -e linkcheck` and Root Toctree Deduplication - Research

**Researched:** 2026-09-13
**Domain:** Sphinx build tooling (tox environment, toctree/HTML-sidebar mechanics, linkcheck builder internals), documentation editing mechanics
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01 — A transient failure is re-run from a clean output directory, never read around.** A
  *transient* status means one of: `timeout`; `ignored` with info `service unavailable` (HTTP 503);
  `rate-limited`; `broken` whose info is a connection-level exception rather than an HTTP status
  (reset, DNS or TLS error). On a transient status the executor removes `docs/_build/linkcheck` and
  runs `tox -e linkcheck` again, stopping after **three runs in total**. Every run is transcribed:
  exit code, the status census from `output.json`, and each non-`working` row verbatim. A run counts
  as the pass only if it meets SC#1 in full on its own. An earlier failed run is never deleted from
  the evidence.
- **D-02 — A timing key is allowed only for a transient failure that recurs on the same URL across
  runs.** If the same URL fails transiently in two or more of D-01's runs, the executor may add
  exactly the key that addresses it to `docs/source/conf.py`: `linkcheck_timeout`,
  `linkcheck_retries` or `linkcheck_rate_limit_timeout`, with a comment naming the URL, status and
  run numbers. Followed by a fresh clean run that meets SC#1. No key is added on a single
  observation or speculatively.
- **D-03 — Anything that is not transient stops the phase and goes to the owner.** Covers: `broken`
  with an HTTP status (404, 410, …); any `redirected` entry; an anchor reported missing; any case
  where passing would require `linkcheck_ignore`, `linkcheck_anchors_ignore`,
  `linkcheck_anchors_ignore_for_url`, `linkcheck_allowed_redirects` or any key that turns a row into
  something other than `working`. The executor does not edit the link and does not add a key; it
  records the URL and its source (editable docs source, or an unfixable autodoc docstring under
  `typsphinx/` per constraint 2) and the owner decides.
- **D-04 [informational] — SC#1 is read literally and is not amended.** "Every `output.json` entry
  has status `working`, and the total equals the `working` count" stays the pass condition. D-02's
  timing keys are compatible; D-03's ignore-style keys are not (Sphinx writes their rows as
  `ignored`). **Note:** this research found and reports a factual correction to one of D-04's
  supporting claims (the exit-code/`timeout` interaction) in `## Premise Check` PC-1 — it does not
  change D-04's pass condition or any required action.
- **D-05 — The new DOC-24 line goes last in each tox block, with a comment saying the environment
  needs the network and is not part of a plain tox run.** Placement: `CLAUDE.md` § Commands after
  `tox -e docs-pdf`; `README.md`'s development block and `contributing.rst`'s "Using Tox" block
  after the `… tox -e docs` line. Uses the neighbouring-line prefix (`tox -e linkcheck` in
  `CLAUDE.md`, `uv run tox -e linkcheck` elsewhere), `#` comment starting in the same column as
  neighbours. Reference wording:
  `# Check external links and anchors (needs network; not run by plain tox)`. Exact text is at
  discretion but must state both the network need and that plain `tox` doesn't run it.
- **D-06 — Nothing else on those surfaces changes.** Every existing line stays byte-identical,
  including `contributing.rst`'s and `CLAUDE.md`'s existing comments (both stay true since
  `linkcheck` is not in `env_list`). No prose paragraph about linkcheck is added anywhere. Every
  other grep hit (including `docs.yml:36` and `CHANGELOG.md:921`) gets a recorded disposition, not
  an edit.
- **D-07 — The 2026-07-22 linkcheck todo stays in `todos/pending/` and gains a status note** appended
  after QUA-13 lands, recording: the `[testenv:linkcheck]` environment now exists (Phase 72,
  QUA-13); the still-open part is the CI job (QUA-08, Future); a future pickup must plan a side PR
  to `main` per ROADMAP constraint 4. Not moved to `completed/`; no new todo filed for QUA-08.
- **D-08 — The 2026-08-16 root-toctree todo is folded into DOC-18 and moves to `todos/completed/`
  in the same commit as the `index.rst` edit.** Its `resolves_phase` is already 72. Its "PDF is not
  affected" section and its `examples/basic` parent-divergence observation feed SC#4 directly (see
  Folded Todos below — **this research's PC-2 widens what that observation must cover**).
- **D-09 — The UI-gate false positive is handled with `--skip-ui` at plan time.** No UI hint line is
  added to the ROADMAP for Phase 72.

### Claude's Discretion

- The exact comment text of the DOC-24 line, within D-05.
- The `description =` text of `[testenv:linkcheck]`. The section's other keys are fixed by SC#1
  (`runner`, `extras`, `changedir`, `commands`). Whether it copies `docs-html`'s other attributes is
  also discretionary, as long as `tox.ini`'s diff only adds lines.
- The plan split and wave shape within the ROADMAP's binding ordering.
- The evidence file names and layout. Evidence is verbatim transcripts in phase markdown, with no
  new committed script and no new test. `72-VERIFICATION.md` is reserved for the verifier and must
  not be authored by a plan.
- How the `PHASE_BASE_SHA` builds are materialised: a second worktree, or `git archive` into
  scratch. **This research recommends `git archive`** for build-only comparisons (see Summary /
  Common Pitfalls Pitfall 1) and reserves `git worktree add --detach` for cases needing a real
  `tox`/`uv sync` run against the snapshot.
- How SC#4's sidebar link count is taken from the markup, as long as it is a count over
  `index.html`'s sidebar navigation and not a reading of prose. **This research provides a working
  `html.parser`-based implementation** (see Code Examples).

### Deferred Ideas (OUT OF SCOPE)

None came up in discussion; it stayed within phase scope. Reviewed-but-not-folded todos: the
2026-07-22 linkcheck-CI-job todo (QUA-08, Future — needs a workflow file, constraint 3 forbids);
`2026-08-14-numref-…` (NUM-01, edits `typsphinx/`); `2026-08-29-hardcoded-delimiter-…` (MSG-06,
edits `typsphinx/`); `2026-09-13-doctest-block-…` (TRN-01, edits `typsphinx/` and changes output).
From `REQUIREMENTS.md`'s Out of Scope table: publishing (tag/PyPI/Release) is merge-only this
milestone; switching RTD's default version to `latest`; any CI job running linkcheck; link-checking
`README.md`/`pyproject.toml`/repo root (lychee already does); link-checking the ja site; fixing the
`examples/basic` HTML-vs-Typst parent divergence beyond re-measuring it after DOC-18 (per PC-2, this
now includes `examples/advanced` too).
</user_constraints>

## Summary

This phase has no unknowns in the "which library" sense — everything it touches is either
Sphinx's own built-in `linkcheck` builder or plain-text editing of `tox.ini`/`CLAUDE.md`/
`README.md`/`docs/source/contributing.rst`/`docs/source/index.rst`. The research value here is
entirely in **measurement**: reproducing every number CONTEXT.md and the ROADMAP cite, confirming
the exact mechanics the plan must drive (how to materialise a `PHASE_BASE_SHA` snapshot so its
`conf.py` still resolves, how furo emits the sidebar twice per page duplication, where the
`multiple toctrees` message and the `build succeeded, N warnings.` line land in stdout vs stderr,
and precisely how Sphinx's `linkcheck` builder decides exit code and `output.json` rows).

All measurements below were taken on today's tree (`5cf396a4`, outside `.planning/` identical to
`main`'s tip per ROADMAP constraint 6) using the main checkout's own `.venv` (Sphinx 9.1.0, Python
3.13.13) — never inside `docs/_build/`, always under a scratch directory that has since been
removed along with two throwaway `git worktree` checkouts used to prove the base/tip build
procedure. Every figure is context, not a threshold (constraint 8); the executing plan re-measures
at its own `PHASE_BASE_SHA`.

**One correction to CONTEXT.md's stated Sphinx internals** and **one widening of what SC#4's
transcription must cover** surfaced during measurement — both are in `## Premise Check` below, both
reported per the orchestrator's instructions (not silently planned around, not re-opened as
decisions).

**Primary recommendation:** Materialise `PHASE_BASE_SHA` and the tip with **`git archive <SHA> |
tar -x -C <scratch>`** (a full tree, not just `docs/source/`, because `conf.py` computes
`pyproject.toml`'s path via `Path(__file__).parent.parent.parent`), then invoke
`(cd <scratch-tree>/docs && LC_ALL=C <main-repo>/.venv/bin/sphinx-build -b html source <out-dir>)`
— this reproduces tox's `[testenv:docs-html]` command line exactly, reuses the **same** already-
provisioned interpreter for both snapshots (satisfying SC#3's "same environment, interpreter
recorded" trivially, since it is literally one binary), and needs no per-snapshot `uv sync` because
the phase never edits `typsphinx/` (constraint 2) so the installed package is identical at both
SHAs.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-------------------|
| QUA-13 | `tox.ini` gains `[testenv:linkcheck]`, shaped like `docs-html`, running `sphinx-build -b linkcheck source _build/linkcheck`; exits 0 with every checked link `working`, measured fresh; any `linkcheck_*` conf.py key carries a comment naming the measured failure that required it | Pattern 1 gives the exact section to add, verified against `docs-html`'s live text; Code Examples gives the working `output.json` census one-liner (95/95 `working` measured today) and the 429/503/anchor-default source citations D-01–D-04 depend on; Common Pitfalls Pitfall 4 covers a rate-limited URL producing two rows in one run |
| DOC-18 | Root `index.rst` toctrees list only `user_guide/index`/`examples/index`; clean HTML build shows 0 `multiple toctrees` messages with unchanged warning count; Typst still includes each page once via its section index, root `index.typ` loses the dead guarded `include()` lines | Pattern 2 gives the exact before/after `index.rst` text (line-range confirmed); Code Examples reproduces the full base→tip build/measure cycle end to end (5→0 messages, 3→3 warnings, dead `include()` lines gone, edge set byte-identical); Premise Check PC-2 widens the parent-divergence transcription to both Examples pages |
| DOC-24 | Every tox-environment-listing surface names `tox -e linkcheck` beside `docs-html`/`docs-pdf`, discovered by grep | Pattern 3 gives exact insertion text, placement and column-aligned padding for all three surfaces, each measured this session; re-ran the discovery grep this session (still 5 hits, same 3 listing surfaces + 2 non-listing hits, dispositions confirmed) |

</phase_requirements>

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| `tox -e linkcheck` environment definition | Build tooling (`tox.ini`) | — | Pure tox/CLI configuration; no application code |
| Link/anchor checking | Sphinx builder (`sphinx.builders.linkcheck`, vendored in `.venv`) | — | Built into Sphinx core; not this project's code |
| Tox-environment discoverability | Documentation / Developer docs (`CLAUDE.md`, `README.md`, `docs/source/contributing.rst`) | — | Prose editing, no runtime component |
| Root toctree structure | Sphinx source (`docs/source/index.rst`, `docs/source/user_guide/index.rst`, `docs/source/examples/index.rst`) | HTML output (furo sidebar) | The `.rst` toctree directives are the single source that both the furo sidebar tree and Sphinx's toctree-relation resolver read |
| Typst include-edge deduplication | `typsphinx/translator.py` (read-only in this phase) | Typst output (`.typ` files) | Constraint 2 forbids editing it; it already deduplicates correctly and this phase only proves that with a build |

This phase touches no Browser/Client, Frontend-Server, API/Backend or Database tier — it is
entirely Build-tooling + Documentation-source + (read-only) output-verification.

## Standard Stack

No new library, package, or runtime dependency is introduced by this phase (constraint 2:
"no new runtime dependencies"). Sphinx's `linkcheck` builder ships inside the `sphinx` package
already pinned by `pyproject.toml` (`sphinx>=9.1,<10` `[VERIFIED: pyproject.toml:27]`
`dependencies = ["sphinx>=9.1,<10", "docutils>=0.21,<0.23", "typst>=0.15.0,<0.16"]`), and the
`docs` extra (`furo`, `sphinx-autodoc-typehints`, `sphinx-intl`, `myst-parser`
`[VERIFIED: pyproject.toml:49-53]`) is unaffected. No `pyproject.toml` edit is expected; if one
turns out to be needed, per constraint 2 it goes to the owner, not into the diff.

### Installed versions (measured, main `.venv`)
| Component | Version | Source |
|-----------|---------|--------|
| Sphinx | 9.1.0 | `[VERIFIED: .venv/bin/python3 -c "import sphinx; print(sphinx.__version__)"]` → `9.1.0` |
| Python | 3.13.13 | `[VERIFIED: .venv/bin/python3 -c "import sys; print(sys.version)"]` → `3.13.13 (main, Apr 7 2026, 18:19:01) [GCC 15.2.0]` |
| Interpreter path | `/home/yuta/Documents/typsphinx/.venv/bin/python3` | `[VERIFIED: sys.executable]` |
| `.venv/pyvenv.cfg` | `home = /nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin`, `version_info = 3.13.13`, `uv = 0.11.25` | `[VERIFIED: .venv/pyvenv.cfg, read this session]` |

**This is the exact "interpreter recorded" evidence SC#3 asks for.** Because both the base and tip
snapshots are built by literally the same `.venv/bin/sphinx-build`, one recording of this table
covers both runs — there is no second interpreter to describe.

### Package Legitimacy Audit

**Not applicable.** This phase installs no new package in any ecosystem — `linkcheck` is a Sphinx
builtin, already available through the pinned `sphinx` dependency. No `npm view` / `pip index
versions` / `cargo search` check is meaningful here, and no legitimacy table is produced. If the
executor discovers during D-02 that a `linkcheck_*` conf.py key requires anything beyond stdlib/
Sphinx (it does not — `linkcheck_timeout`, `linkcheck_retries`, `linkcheck_rate_limit_timeout` are
plain Sphinx config values, confirmed in the installed `sphinx.builders.linkcheck` module, see
`## Code Examples`), this section should be revisited, but no such need was found.

## Architecture Patterns

### System Architecture Diagram (build-time data flow relevant to this phase)

```
docs/source/*.rst  ──(sphinx-build -b html)──►  Sphinx toctree resolver
      │                                                │
      │                                     picks ONE parent per docname
      │                                     when a docname is reachable via
      │                                     >1 toctree ("multiple toctrees"
      │                                     console message, stdout only)
      │                                                │
      ▼                                                ▼
docs/source/*.rst  ──(sphinx-build -b linkcheck)──►  HyperlinkAvailabilityChecker
      │                                                │
      │                                     one JSON-lines row per checked
      │                                     URI written unconditionally to
      │                                     _build/linkcheck/output.json
      │                                     (write_linkstat(), called before
      │                                     any status branching)
      ▼
docs/source/*.rst  ──(sphinx-build -b typst)──►  TypstTranslator (read-only
                                                   in this phase)
                                                        │
                                          derive_master_edge_keys() seeds
                                          #state("typsphinx:include-edges")
                                          with ONE edge per selected parent
                                          (translator.py:343; the resolver's
                                          "selected" parent from the HTML
                                          pass is the same relation Typst's
                                          edge derivation reads)
                                                        │
                                                        ▼
                                          root index.typ's per-child guard
                                          (translator.py:468-507) evaluates
                                          false for any docname whose edge
                                          key does not name index.typ's own
                                          docname as parent → dead include()
                                          line, never fires
```

A reader tracing "why does the PDF never show the defect" follows the right branch: the toctree
resolver's single "selected" parent (same mechanism that emits the `multiple toctrees` message on
the left branch) is exactly what feeds the edge-key set, so a page listed twice in `.rst` still
gets exactly one edge and exactly one firing `include()`.

### Recommended Project Structure

No new files or directories. The three edited surfaces stay exactly where they are:
```
tox.ini                                  # + [testenv:linkcheck] section (QUA-13)
CLAUDE.md                                # § Commands gains one line (DOC-24)
README.md                                # dev commands block gains one line (DOC-24)
docs/source/contributing.rst             # "Using Tox" block gains one line (DOC-24)
docs/source/index.rst                    # 5 lines removed from two toctrees (DOC-18)
docs/source/conf.py                      # optionally, under D-02 only, one linkcheck_* key
```

### Pattern 1: `[testenv:linkcheck]`, shaped like `[testenv:docs-html]`

**What:** A new tox environment, added by pure insertion (no existing line touched).
**When to use:** Whenever a maintainer wants a network-dependent, non-`env_list` check.
**Example (recommended addition, appended after the existing `[testenv:docs]` block so `tox.ini`'s
diff is a pure append):**
```ini
[testenv:linkcheck]
description = Check external links and anchors in the documentation (needs network)
runner = uv-venv-lock-runner
extras = docs
changedir = docs
commands =
    sphinx-build -b linkcheck source _build/linkcheck
```
`[VERIFIED: tox.ini:67-73]` — `[testenv:docs-html]`'s exact keys and shape, quoted verbatim:
```
[testenv:docs-html]
description = Build HTML documentation
runner = uv-venv-lock-runner
extras = docs
changedir = docs
commands =
    sphinx-build -b html source _build/html
```
The `linkcheck` environment differs only in `description`, the builder flag (`-b linkcheck` vs
`-b html`) and the output directory (`_build/linkcheck` vs `_build/html`) — every other key is
identical to what SC#1 requires (`runner = uv-venv-lock-runner`, `extras = docs`,
`changedir = docs`). `[VERIFIED: tox.ini:2]` — `env_list = py312, py313, lint, type, cov, docs`
(unchanged; `linkcheck` correctly stays out of it because it needs the network, matching D-06's
requirement that this line "stays true").

### Pattern 2: Root toctree lists only the section index (DOC-18)

**What:** Remove the flat duplicate entries, leaving each root toctree with exactly one entry.
**When to use:** Always, per the owner's 2026-09-13 decision (conventional hierarchy).
**Exact target state**, `[VERIFIED: docs/source/index.rst:38-53, read this session]`:
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
Current state (to be edited), quoted verbatim, `[VERIFIED: docs/source/index.rst:38-53]`:
```
38	.. toctree::
39	   :maxdepth: 2
40	   :caption: User Guide
41	
42	   user_guide/index
43	   user_guide/configuration
44	   user_guide/builders
45	   user_guide/templates
46	
47	.. toctree::
48	   :maxdepth: 2
49	   :caption: Examples
50	
51	   examples/index
52	   examples/basic
53	   examples/advanced
```
This confirms CONTEXT.md's cited line ranges (`:43-45` and `:52-53`) exactly — those five lines are
the only ones removed; line 42 (`user_guide/index`) and line 51 (`examples/index`) stay.

The section indexes that already own these children, confirmed read-only (must be absent from the
diff), `[VERIFIED: docs/source/user_guide/index.rst:6-12]`:
```
6	.. toctree::
7	   :maxdepth: 2
8	
9	   configuration
10	   builders
11	   templates
12	   output_layout
```
`[VERIFIED: docs/source/examples/index.rst:6-10]`:
```
6	.. toctree::
7	   :maxdepth: 2
8	
9	   basic
10	   advanced
```

### Pattern 3: DOC-24's exact insertion per surface

Every neighbouring line in each block was read this session with `cat -A`-equivalent column
measurement (`str.index('#')`), so the pad width below is exact, not eyeballed.

**`CLAUDE.md`** — `[VERIFIED: CLAUDE.md:31-33, read this session]`:
```
31	# Build the project's own docs (from docs/)
32	tox -e docs-html             # HTML via furo
33	tox -e docs-pdf              # PDF via the typstpdf builder (dogfoods this extension)
```
Both existing lines' `#` starts at 0-indexed column **29** (measured via `line.index('#')`).
`tox -e docs-html` and `tox -e linkcheck` are both 16 characters, so the new line needs the same
13-space pad `tox -e docs-html` uses:
```
tox -e linkcheck             # Check external links and anchors (needs network; not run by plain tox)
```
Placed after line 33 (last in the block), per D-05.

**`README.md`** — `[VERIFIED: README.md:261-263, read this session]`:
```
261	uv run tox -e docs-html     # Build HTML documentation
262	uv run tox -e docs-pdf      # Build PDF documentation
263	uv run tox -e docs          # Build both HTML and PDF docs
```
`#` starts at 0-indexed column **28**. `uv run tox -e docs-html` is 23 characters; `uv run tox -e
linkcheck` is also 23 characters (`docs-html` and `linkcheck` are both 9-character env names), so
the identical 5-space pad reproduces the neighbours' alignment exactly:
```
uv run tox -e linkcheck     # Check external links and anchors (needs network; not run by plain tox)
```
Placed after line 263 (last in the block — the block ends with the `… tox -e docs` line per D-05).

**`docs/source/contributing.rst`** — `[VERIFIED: docs/source/contributing.rst:123-125, read this
session]`:
```
123	   uv run tox -e docs-html     # Build HTML documentation
124	   uv run tox -e docs-pdf      # Build PDF documentation
125	   uv run tox -e docs          # Build both HTML and PDF
```
3-space rST code-block indent, then the identical `uv run tox -e …` shape as README.md; `#` starts
at 0-indexed column **31** (28 + 3). Same 5-space pad after the 3-space indent:
```
   uv run tox -e linkcheck     # Check external links and anchors (needs network; not run by plain tox)
```
Placed after line 125 (last line of the `.. code-block:: bash` block, per D-05). No blank-line or
indentation change is needed around it — it is one more line inside the same `.. code-block::
bash` directive already containing lines 116-125.

**Comment text** (Claude's Discretion per CONTEXT.md, but D-05 fixes its two required clauses):
`# Check external links and anchors (needs network; not run by plain tox)` satisfies both:
names the network requirement, and states plain `tox` does not run it (because `linkcheck` is
absent from `env_list`).

### Anti-Patterns to Avoid

- **Copying `docs/source/` alone into a scratch directory to build a `PHASE_BASE_SHA` snapshot.**
  Measured failure this session: `conf.py` computes
  `pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"` — three levels up from
  `docs/source/conf.py`. A bare `cp -r docs/source/ $SCRATCH/` breaks that path and the build aborts
  with `ConfigError` / `FileNotFoundError`. See `## Premise Check` — no, this is not a premise
  falsification, it is a documented pitfall; see `## Common Pitfalls` Pitfall 1 instead.
- **Running the base/tip builds from the repo's own `docs/` directory into `docs/_build/`.** The
  research constraints (and general project hygiene) require build output to stay in scratch, never
  in the tracked tree. Always redirect `sphinx-build`'s output-dir argument to an absolute scratch
  path, or run from inside a `git worktree`/`git archive` copy's own `docs/` directory.
  `changedir = docs` in `tox.ini` is why `sphinx-build -b html source _build/html` (a **relative**
  output path) is safe when actually run via `tox -e docs-html` — that relative path resolves
  against the tox-managed `changedir`, which for a real (non-scratch) run is the repo's own `docs/`.
  For scratch comparisons, always pass an absolute output-dir path instead.
- **Grepping console output for `multiple toctrees` or `build succeeded` without `LC_ALL=C`.** On
  this machine (`ja_JP.UTF-8` host locale, passed through by the FHS sandbox per `CLAUDE.md` §
  Locale) both strings are localised under the ambient locale, so an un-prefixed grep can return
  zero and look like a false pass. Confirmed this session — see `## Code Examples`.
- **Counting `href="…"` occurrences over the whole `index.html` file, not scoped to the sidebar
  `<div class="sidebar-tree">`.** Measured this session (`## Code Examples` Pitfall 2): raw
  file-wide `grep -c` returns **4**, not the sidebar's real **2**, because the root `index.html`
  page's own body independently renders the same toctree directives inline
  (`<div class="toctree-wrapper compound">`, expanded to `:maxdepth: 2`, including in-page section
  anchors). SC#4 is scoped to "the sidebar navigation," which is the `sidebar-tree` div only.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Link/anchor availability checking | A custom URL-fetching script | Sphinx's built-in `linkcheck` builder | Already handles retries, rate limiting (429), transient-outage detection (503→`ignored`), redirect classification, and per-link JSON output; QUA-13 is explicitly "shaped like `docs-html`" — reusing the builder, not writing one |
| Sidebar link-count verification | A full HTML/DOM diffing library | Python's stdlib `html.parser.HTMLParser`, scoped to the `sidebar-tree` div | This project's convention is verbatim evidence with no new committed script/test (CONTEXT.md § Claude's Discretion); a ~40-line inline `html.parser` subclass, run once via `uv run python -` or a heredoc, is sufficient and was proven working this session (`## Code Examples`) |
| Toctree/edge inspection | Any new tooling | `grep`/direct reading of the emitted `.typ` files and Sphinx's own console `document is referenced in multiple toctrees … selecting: X <- Y` message | Both already exist and were used this session to fully answer SC#3 and SC#4 without any new code path |

**Key insight:** every mechanism this phase needs to observe (toctree parent selection, dead
guarded includes, linkcheck's status classification) is already emitted by Sphinx or by
`typsphinx/translator.py`'s existing (unedited) mechanism. There is nothing to write beyond the
`tox.ini` section and the prose edits — this phase is entirely proof-gathering plus small text
edits.

## Common Pitfalls

### Pitfall 1: A bare directory copy of `docs/source/` cannot build

**What goes wrong:** `sphinx-build` fails with `ConfigError: There is a programmable error in your
configuration file` wrapping a `FileNotFoundError` for `pyproject.toml`.
**Why it happens:** `docs/source/conf.py:22` computes
`pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"` — an absolute,
`__file__`-relative path three directories above `conf.py`. Copying only `docs/source/` elsewhere
puts nothing three levels up. `conf.py` also does `sys.path.insert(0, os.path.abspath("../.."))`
for autodoc (`[VERIFIED: docs/source/conf.py:16]`), which is **CWD**-relative, not
`__file__`-relative — so the working directory when `sphinx-build` runs must also be the snapshot's
own `docs/` directory (exactly what `changedir = docs` gives real tox runs).
**How to avoid:** Materialise a **full** repository tree per SHA — either
`git worktree add --detach <path> <sha>` or `git archive <sha> | tar -x -C <path>` — then `cd` into
that tree's `docs/` before invoking `sphinx-build source <out>` (or point `sphinx-build` at
`<tree>/docs/source` while `cd`'d to `<tree>/docs`, as measured working commands below show). Both
methods were proven this session to produce an identical, buildable tree; `git archive` is lighter
(no `.git` overhead, nothing to `git worktree remove` afterward) and is recommended for build-only
snapshot comparisons. `git worktree add --detach` is only needed if the executor plans to also run
`tox`/`uv sync` against that snapshot (this phase does not need to, since `typsphinx/` never
changes between base and tip).
**Warning signs:** `ConfigError` in `sphinx-build`'s traceback naming `pyproject.toml`, or an
autodoc `ModuleNotFoundError: No module named 'typsphinx'` from the `api/` pages.

### Pitfall 2: File-wide `grep -c` for a target `href` over-counts `index.html`

**What goes wrong:** Counting `grep -c 'href="user_guide/configuration.html"' index.html` returns
**4** on the pre-fix (base) build, not the **2** the sidebar-only defect actually produces — leading
to a wrong SC#4 transcription if used naively.
**Why it happens:** The root `index.rst` page is Sphinx's own "index" (root) document; Sphinx
renders `.. toctree::` directives appearing in a page's own body as inline navigation blocks
(`<div class="toctree-wrapper compound">`) **in addition to** furo's separate left-hand
`<div class="sidebar-tree">`. Both blocks read the same `.. toctree::` source and therefore both
duplicate the same links whenever the source duplicates them — the body's compound-toctree block
even further expands each page down to its own in-page headings (`installation.html#requirements`,
etc.) because of `:maxdepth: 2`, adding still more spurious `href` matches for pages the sidebar
does not touch.
**How to avoid:** Scope the count with a real HTML parser to the `sidebar-tree` div specifically —
measured, working parser in `## Code Examples`.
**Warning signs:** A page-scoped link count that doesn't equal 1 or 2 for anything, or that also
picks up in-page anchor hrefs (`#requirements`-style fragments) alongside whole-page hrefs.

### Pitfall 3: `linkcheck`'s exit code is not purely a `broken`-link signal

See `## Premise Check` — `timed_out_hyperlinks` also sets the nonzero exit code, contrary to
CONTEXT.md D-04's stated claim that "only `broken` does." D-01's procedure is unaffected (it reads
`output.json`'s `status` field directly, never inferring transience from exit code alone), but an
executor who designs a shortcut ("exit 0 implies no timeouts, so I only need to scan for `broken`
rows") would be wrong.

### Pitfall 4: A rate-limited URL can appear more than once in one `output.json`

**What goes wrong:** A single URL that gets HTTP 429 mid-run can produce a `rate-limited` row
*and* a later final-status row (`working`/`broken`) in the **same** `output.json`, because
`write_linkstat()` is called once per **result**, and a re-queued rate-limited check yields two
results for one URL within a single run (`[VERIFIED:
.venv/lib/python3.13/site-packages/sphinx/builders/linkcheck.py:609-613]`, quoted in `## Code
Examples`).
**Why it happens:** `write_linkstat()` (line 124) runs unconditionally before the status-branching
`match` statement, and the checker's own retry loop re-submits the request via `self.wqueue.put(...)`
rather than replacing the earlier result.
**How to avoid:** D-01's "total equals the `working` count" check already handles this correctly —
any surviving non-`working` row (including a stale `rate-limited` one) fails the check regardless of
how many rows exist for that URL. No extra deduplication logic is needed; just do not assume
`len(output.json rows) == len(unique URLs)`.

## Code Examples

Verified patterns from measurement this session (all run against today's tree, `5cf396a4`;
`docs/_build/` never touched — everything under a scratch directory that has been removed):

### Materialising a snapshot and running the exact `docs-html`-shaped build

```bash
# Full-tree snapshot (no .git needed downstream, nothing to clean up):
git archive <SHA> | tar -x -C "$SCRATCH/tree-<SHA>"

# Run tox's own [testenv:docs-html] command line against it, reusing the
# already-provisioned main-checkout interpreter (typsphinx/ is unedited
# between base and tip, so this is a valid "same environment"):
mkdir -p "$SCRATCH/html-<SHA>"
( cd "$SCRATCH/tree-<SHA>/docs" && \
  LC_ALL=C /home/yuta/Documents/typsphinx/.venv/bin/sphinx-build \
    -b html source "$SCRATCH/html-<SHA>" ) \
  > "$SCRATCH/html-<SHA>.stdout.log" 2> "$SCRATCH/html-<SHA>.stderr.log"
echo "EXIT=$?"
```
Measured output on today's tree (`5cf396a4`, used as `PHASE_BASE_SHA` stand-in): `EXIT=0`,
`build succeeded, 3 warnings.` (stdout, line 68 of the log), and:
```
LC_ALL=C grep -c "multiple toctrees" "$SCRATCH/html-<SHA>.stdout.log"   # → 5
LC_ALL=C grep -c "multiple toctrees" "$SCRATCH/html-<SHA>.stderr.log"   # → 0
LC_ALL=C grep -n "build succeeded" "$SCRATCH/html-<SHA>.stdout.log"     # → line 68, stdout
```
**Both the `multiple toctrees` messages and the `build succeeded, N warnings.` line are on
stdout, never stderr.** `-q` is NOT used in the recommended build command above (unlike the
linkcheck example, which the discussion-time precedent ran with `-q`); if `-q` is added, verify it
does not also suppress the `multiple toctrees` lines (a quick check: the discussion-time precedent
used `sphinx-build -q -b linkcheck …`, a different builder, so this has not been checked for `-b
html`; recommend NOT using `-q` for the SC#3 build so both signals stay visible without a second
check).

Full verbatim transcript of the five messages measured on today's tree, `LC_ALL=C`:
```
checking consistency... /…/docs/source/examples/advanced.rst: document is referenced in multiple toctrees: ['examples/index', 'index'], selecting: index <- examples/advanced
/…/docs/source/examples/basic.rst: document is referenced in multiple toctrees: ['examples/index', 'index'], selecting: index <- examples/basic
/…/docs/source/user_guide/builders.rst: document is referenced in multiple toctrees: ['index', 'user_guide/index'], selecting: user_guide/index <- user_guide/builders
/…/docs/source/user_guide/configuration.rst: document is referenced in multiple toctrees: ['index', 'user_guide/index'], selecting: user_guide/index <- user_guide/configuration
/…/docs/source/user_guide/templates.rst: document is referenced in multiple toctrees: ['index', 'user_guide/index'], selecting: user_guide/index <- user_guide/templates
```
(paths shortened here for readability; the actual log lines carry the full scratch-tree absolute
path). Note the asymmetry the folded todo already flagged, now measured to affect **both** Examples
pages — see `## Premise Check`.

### Applying the DOC-18 edit and re-measuring (proves the fix works before it is planned as risky)

```bash
# index.rst edit, applied to a scratch copy of the snapshot (or, at execution
# time, directly to the tip's own docs/source/index.rst):
python3 - <<'EOF'
p = "docs/source/index.rst"
s = open(p).read()
s = s.replace(
    "   user_guide/index\n   user_guide/configuration\n   user_guide/builders\n   user_guide/templates\n",
    "   user_guide/index\n",
)
s = s.replace(
    "   examples/index\n   examples/basic\n   examples/advanced\n",
    "   examples/index\n",
)
open(p, "w").write(s)
EOF
```
Re-running the same build command afterward measured: `EXIT=0`,
`build succeeded, 3 warnings.` (**unchanged** — the 3 warnings are the pre-existing
`visit_toctree` docstring rST errors, constraint 9, untouched by this phase), and
`multiple toctrees` count **0**. This is the exact SC#3 proof shape, reproduced end to end this
session on a throwaway `git worktree` (since removed).

### Sidebar-scoped link count (`html.parser`, stdlib only, no new committed file)

```python
import sys
from html.parser import HTMLParser

TARGETS = [
    "user_guide/configuration.html", "user_guide/builders.html",
    "user_guide/templates.html", "examples/basic.html",
    "examples/advanced.html",
    "user_guide/output_layout.html",  # control: never listed at root
]

class SidebarParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.div_depth = 0
        self.sidebar_div_depth = None
        self.counts = {t: 0 for t in TARGETS}
        self.li_stack = []
        self.parent_map = {}

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "div":
            self.div_depth += 1
            if self.sidebar_div_depth is None and "sidebar-tree" in attrs.get("class", "").split():
                self.sidebar_div_depth = self.div_depth
        if self.sidebar_div_depth is None:
            return
        if tag == "li":
            self.li_stack.append({"classes": attrs.get("class", ""), "href": None})
        if tag == "a" and self.li_stack:
            href = attrs.get("href")
            if href in self.counts:
                self.counts[href] += 1
                parent_href = None
                for frame in reversed(self.li_stack[:-1]):
                    if "has-children" in frame["classes"].split():
                        parent_href = frame["href"]
                        break
                self.parent_map.setdefault(href, []).append(parent_href)
            self.li_stack[-1]["href"] = href

    def handle_endtag(self, tag):
        if tag == "div":
            if self.sidebar_div_depth is not None and self.div_depth == self.sidebar_div_depth:
                self.sidebar_div_depth = None
            self.div_depth -= 1
        if self.sidebar_div_depth is None:
            return
        if tag == "li" and self.li_stack:
            self.li_stack.pop()

with open(sys.argv[1], encoding="utf-8") as f:
    p = SidebarParser()
    p.feed(f.read())
for t in TARGETS:
    print(f"{t}: count={p.counts[t]} parents={p.parent_map.get(t)}")
```
Measured against the **base** build's `index.html`:
```
user_guide/configuration.html: count=2 parents=['user_guide/index.html', None]
user_guide/builders.html: count=2 parents=['user_guide/index.html', None]
user_guide/templates.html: count=2 parents=['user_guide/index.html', None]
examples/basic.html: count=2 parents=['examples/index.html', None]
examples/advanced.html: count=2 parents=['examples/index.html', None]
user_guide/output_layout.html: count=1 parents=['user_guide/index.html']
```
Measured against the **tip** (post-fix) build's `index.html`:
```
user_guide/configuration.html: count=1 parents=['user_guide/index.html']
user_guide/builders.html: count=1 parents=['user_guide/index.html']
user_guide/templates.html: count=1 parents=['user_guide/index.html']
examples/basic.html: count=1 parents=['examples/index.html']
examples/advanced.html: count=1 parents=['examples/index.html']
user_guide/output_layout.html: count=1 parents=['user_guide/index.html']
```
Every count drops from 2 to 1, every parent is the section index, and the control
(`output_layout.html`) stays at 1 throughout — exactly SC#4's HTML half. Recommend running this
inline via `python3 - <<'EOF' … EOF` or `uv run python -c`, per this project's "no new committed
script" convention.

### Typst side: dead `include()` lines disappear, edges stay stable

Base tree, `[VERIFIED: <scratch>/base-typst/index.typ, this session's build]` — 12 `include()`
lines in root `index.typ`, five of them dead-guarded:
```
if "index#0>user_guide/configuration" in state("typsphinx:include-edges", ()).get() { include("user_guide/configuration.typ") }
if "index#0>user_guide/builders" in state("typsphinx:include-edges", ()).get() { include("user_guide/builders.typ") }
if "index#0>user_guide/templates" in state("typsphinx:include-edges", ()).get() { include("user_guide/templates.typ") }
if "index#0>examples/basic" in state("typsphinx:include-edges", ()).get() { include("examples/basic.typ") }
if "index#0>examples/advanced" in state("typsphinx:include-edges", ()).get() { include("examples/advanced.typ") }
```
Tip tree (post-fix), same file: only 7 `include()` lines remain — those five are gone entirely
(not present-but-false; the line itself is not emitted, because the duplicate toctree entry that
would have generated it no longer exists in the source).

The seeded edge set, `[VERIFIED: <scratch>/{base,tip}-typst/typsphinx.typ]`, is **byte-identical**
between base and tip:
```
#state("typsphinx:include-edges", ()).update(("index#0>installation", "index#0>quickstart", "index#0>user_guide/index", "user_guide/index#0>user_guide/configuration", "user_guide/index#0>user_guide/builders", "user_guide/index#0>user_guide/templates", "user_guide/index#0>user_guide/output_layout", "index#0>examples/index", "examples/index#0>examples/basic", "examples/index#0>examples/advanced", "index#0>api/index", "index#0>contributing", "index#0>changelog",))
```
— confirming the DOC-18 edit changes zero bytes of Typst output beyond the dead-line deletion in
`index.typ` itself; `user_guide/index.typ` and `examples/index.typ` (which fire the real,
non-dead includes) are untouched, `[VERIFIED: <scratch>/{base,tip}-typst/user_guide/index.typ:19-22
and examples/index.typ:19-20]`.

The mechanism these guards and this state key come from, read this session (constraint 2 forbids
editing, not reading):
```python
# typsphinx/translator.py:207
INCLUDE_STATE_KEY = "typsphinx:include-edges"

# typsphinx/translator.py:452-465 (render_include_edges_state / similar)
#   "'#state(\"typsphinx:include-edges\", ()).update((\"index#0>child\",))'"

# typsphinx/translator.py:468-507 (render_include_guard)
#   "'if \"index#0>child\" in state(\"typsphinx:include-edges\", ()).get() { include(\"child.typ\") }'"
```

### `output.json` census (linkcheck)

Measured this session, `sphinx-build -q -b linkcheck docs/source $SCRATCH/linkcheck-out`, ~9.5 s
wall clock, exit 0:
```python
import json, collections
rows = [json.loads(l) for l in open("output.json")]
total = len(rows)
by_status = collections.Counter(r["status"] for r in rows)
non_working = [r for r in rows if r["status"] != "working"]
print("total:", total, "by_status:", dict(by_status))
for r in non_working:
    print(r)
```
Output: `total: 95 by_status: {'working': 95}`, `non_working` empty. `output.json` is confirmed
**JSON-lines** (one object per line, 95 lines), never a single JSON array,
`[VERIFIED: .venv/lib/python3.13/site-packages/sphinx/builders/linkcheck.py:209-211]`:
```python
def write_linkstat(self, data: dict[str, str | int | _Status]) -> None:
    self.json_outfile.write(json.dumps(data))
    self.json_outfile.write('\n')
```
This exactly reproduces CONTEXT.md's discussion-time figure (95 `working`, 0 other) — not because
95 is a threshold (constraint 8 forbids that), but because it demonstrates the census script and
the command work end to end, unmodified, right now.

### `linkcheck_anchors` default (confirms D-04's anchor claim)

`[VERIFIED: .venv/lib/python3.13/site-packages/sphinx/builders/linkcheck.py:823]`:
```python
app.add_config_value('linkcheck_anchors', True, '', types=frozenset({bool}))
```
Anchor checking is **on by default** — no `conf.py` key is needed for the 41 `#anchor` URIs
CONTEXT.md counts to actually be checked.

### 429 / 503 handling (confirms D-04's transient-status claims)

`[VERIFIED: .venv/lib/python3.13/site-packages/sphinx/builders/linkcheck.py:608-617]`:
```python
# Rate limiting; back-off if allowed, or report failure otherwise
if status_code == 429:
    if next_check := self.limit_rate(response_url, retry_after):
        self.wqueue.put(CheckRequest(next_check, hyperlink), False)
        return _Status.RATE_LIMITED, '', 0
    return _Status.BROKEN, error_message, 0

# Don't claim success/failure during server-side outages
if status_code == 503:
    return _Status.IGNORED, 'service unavailable', 0
```
Confirms exactly: 429 re-queues as `rate-limited` and only becomes `broken` once retries/timeout
are exhausted; 503 is unconditionally `ignored`/`service unavailable` — no configuration key
changes this. Both match D-04 verbatim.

## State of the Art

Not applicable in the "library evolved" sense — Sphinx's `linkcheck` builder and toctree resolver
are the same mechanisms this project has used since it adopted Sphinx. Nothing here has a newer
recommended approach; the "old approach" is simply "no `tox -e linkcheck` environment exists yet"
and "the root toctree lists both the section index and its children," both closed by this phase.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `-q` on `sphinx-build -b html` would not also suppress the `multiple toctrees` console lines (untested this session; only checked without `-q`) | Code Examples, "Materialising a snapshot…" | Low — the recommendation is to NOT use `-q` for the SC#3 build, so this assumption only matters if a future author adds `-q` for brevity; flagged inline as an open question there |
| A2 | The comment text `# Check external links and anchors (needs network; not run by plain tox)` is accepted style; D-05 only fixes its two required semantic clauses, not its exact wording | Pattern 3 (Code Examples) | None — explicitly Claude's Discretion per CONTEXT.md |

No other claim in this document is `[ASSUMED]`; every load-bearing fact was measured or read from
source this session (`[VERIFIED: …]`) or is drawn directly from ROADMAP/CONTEXT.md's own binding
text.

## Premise Check

Per the orchestrator's instructions: these are measured falsifications of stated facts, reported
here rather than silently planned around or treated as re-opening any locked decision. Neither
changes what D-01 through D-09 require the executor to *do*.

### PC-1: D-04's exit-code claim about `timeout` is incorrect

**CONTEXT.md states (D-04, "informational"):** "Timeouts and redirects: they are written as
`timeout` and `redirected …` but do not make the exit status non-zero. Only `broken` does."

**Reproduction:**
```bash
grep -n "statuscode\|broken_hyperlinks\|timed_out_hyperlinks" \
  /home/yuta/Documents/typsphinx/.venv/lib/python3.13/site-packages/sphinx/builders/linkcheck.py
```
**Output (this session, Sphinx 9.1.0):**
```
90:        self.broken_hyperlinks = 0
91:        self.timed_out_hyperlinks = 0
109:        if self.broken_hyperlinks or self.timed_out_hyperlinks:
110:            self._app.statuscode = 1
155:                self.timed_out_hyperlinks += 1
174:                self.broken_hyperlinks += 1
```
`finish()` (line 109-110) sets the nonzero exit code whenever **either** counter is nonzero.
`timed_out_hyperlinks` is incremented at line 155, inside the `case _Status.TIMEOUT:` branch — so a
`timeout` row **does** make the exit status non-zero, contrary to D-04's claim. Only `redirected`
and `ignored` genuinely leave the exit code untouched.

**Why this does not change the plan:** D-01's procedure never relies on exit code to detect
transience — it reads `output.json`'s `status` field row-by-row, which is the only reliable signal
regardless of this correction. D-01's own three-run/pass-condition logic ("exit 0, and every
`output.json` entry `working`") is unaffected: if a `timeout` row is present, exit is *already*
nonzero (which correctly fails the pass condition either way — this correction makes that failure
mode *more* certain, not less, since a lone `timeout` row now can't slip through on a false exit-0).
No plan action changes; this is purely a documentation correction the planner should not repeat when
writing evidence prose in the executing plan.

### PC-2: SC#4's "examples/basic parent divergence" undercounts — `examples/advanced` diverges identically

**ROADMAP SC#4 states:** "The `examples/basic` parent divergence: it is re-measured, not fixed. The
parent Sphinx HTML selects and the parent the Typst edge map records are both transcribed." This
wording, following the folded todo's own text, names only `examples/basic`.

**Reproduction (today's tree, `5cf396a4`):**
```bash
LC_ALL=C .venv/bin/sphinx-build -b html docs/source $SCRATCH/base-html \
  2> /dev/null | grep "multiple toctrees"
```
**Output:**
```
…examples/advanced.rst: document is referenced in multiple toctrees: ['examples/index', 'index'], selecting: index <- examples/advanced
…examples/basic.rst: document is referenced in multiple toctrees: ['examples/index', 'index'], selecting: index <- examples/basic
…user_guide/builders.rst: … selecting: user_guide/index <- user_guide/builders
…user_guide/configuration.rst: … selecting: user_guide/index <- user_guide/configuration
…user_guide/templates.rst: … selecting: user_guide/index <- user_guide/templates
```
Both `examples/basic` **and** `examples/advanced` have Sphinx's HTML resolver select `index` (the
root) as parent — while the Typst edge map (`[VERIFIED: typsphinx.typ`'s seeded state, this
session]) assigns `examples/index` as parent for **both** pages identically
(`"examples/index#0>examples/basic", "examples/index#0>examples/advanced"`). The three `user_guide`
pages show no such divergence (HTML and Typst agree on `user_guide/index` for all three).

**Why this does not re-open the decision:** SC#4 already says "if they still differ, a todo is
filed and nothing more is done here" — the *disposition* (re-measure, don't fix, file a todo if it
persists) is unchanged. What changes is only the **scope of the transcription**: the executing plan
should transcribe the parent-selection outcome for **both** `examples/basic` and
`examples/advanced`, not `examples/basic` alone, since both now show the identical divergence
pattern. This is consistent with the folded todo's own count history (4 `multiple toctrees` messages
on 2026-08-16 rising to 5 on 2026-09-13, already acknowledged in CONTEXT.md) — the newly-appearing
fifth message is `examples/advanced`'s, and it carries the same "selects `index`" outcome the todo
only documented for `basic`.

## Open Questions

1. **Does `sphinx-build -b html -q` suppress the `multiple toctrees` console lines?**
   - What we know: without `-q`, both the `multiple toctrees` lines and the `build succeeded, N
     warnings.` line print to stdout (confirmed this session).
   - What's unclear: whether adding `-q` (as the discussion-time `linkcheck` precedent did) would
     also silence the `multiple toctrees` lines, which are `logger.info`-level rather than
     `logger.warning`-level output in Sphinx's own toctree-consistency check.
   - Recommendation: don't use `-q` for the SC#3 HTML build in the plan; the un-quieted command was
     measured working end-to-end this session and both signals stay visible without a second
     command.

2. **Will the owner's UAT sidebar screenshot need the DOC-18 fix built with the `docs-pdf`/CI-style
   `extras=docs` provisioning, or is the main `.venv` build sufficient for a visual check?**
   - What we know: the main `.venv` build renders identically to what `tox -e docs-html` would
     produce, since `extras = docs` is a superset already installed there.
   - What's unclear: nothing technical — this is a process question of whether the plan should
     additionally run `tox -e docs-html` itself once (for auditability that the *tox environment*
     specifically was exercised, distinct from the ad hoc `.venv/bin/sphinx-build` invocations used
     for base/tip comparison), given SC#5 already requires the full local gate quartet and a
     dispatched CI run that exercises `tox.ini` on a runner.
   - Recommendation: run `tox -e docs-html` and `tox -e linkcheck` for real (through tox, in the
     provisioned worktree venv) at least once each in the plan's own local-gates wave, in addition
     to the scratch base/tip comparison builds — this exercises the actual tox environment
     definitions the plan adds/uses, not just Sphinx directly.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Sphinx (`linkcheck` builder) | QUA-13 | ✓ | 9.1.0 (`[VERIFIED]`) | — |
| `tox` + `tox-uv` + `uv-venv-lock-runner` | QUA-13, SC#5 | ✓ (main checkout; worktree needs its own `uv sync --extra dev`) | pinned `tox>=4.56,<5`, `tox-uv>=1.35,<2` `[VERIFIED: pyproject.toml:37-38]` | — |
| `furo` theme | DOC-18 (sidebar rendering) | ✓ (installed in main `.venv`) | not version-pinned to a specific release in this research | — |
| `gh` CLI | SC#5 (branch push/CI dispatch/read-only checks) | ✓ (used read-only this session: `gh api …/required_status_checks`, `git ls-remote`) | — | — |
| Network access (to run `linkcheck` for real, and to dispatch/watch CI) | QUA-13, SC#5 | ✓ (95/95 links resolved in ~9.5s this session; `gh api` calls succeeded) | — | — |

**Missing dependencies with no fallback:** none found.
**Missing dependencies with fallback:** none found.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (existing suite; unaffected by this phase — no new test files, `git grep -rln "multiple toctrees\|linkcheck" tests/` returned empty this session, confirming no existing pytest coverage touches either mechanism) |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]` (unedited) |
| Quick run command | `pytest -q` (regression-only; proves this phase broke nothing under `typsphinx/`) |
| Full suite command | `uv run pytest -q -p no:cacheprovider` (per Phase 70's own CI-evidence precedent) |

This phase's actual proof surface is **not** pytest — per CONTEXT.md's Claude's Discretion note,
"evidence is verbatim transcripts in phase markdown, with no new committed script and no new test."
The table below maps each requirement/SC to the shell/Sphinx command that proves it, which is the
real validation architecture for this phase.

### Phase Requirements → Proof Map

| Req / SC | Behavior | Proof command | Failure signal |
|----------|----------|----------------|-----------------|
| QUA-13 / SC#1 | `tox -e linkcheck` exists, shaped like `docs-html`, passes clean | `rm -rf docs/_build/linkcheck && tox -e linkcheck` then census `docs/_build/linkcheck/output.json` (see Code Examples) | nonzero exit, or any `status != "working"` row, or `total != working_count` |
| DOC-24 / SC#2 | Every listing surface names `tox -e linkcheck` | `git grep -n 'tox -e docs-pdf' -- ':!.planning'` re-run, each hit dispositioned | any listing-surface hit (CLAUDE.md/README.md/contributing.rst) without a sibling `tox -e linkcheck`/`uv run tox -e linkcheck` line in the same block |
| DOC-18 / SC#3 | Root toctrees list only section indexes; 0 `multiple toctrees`; warning count unchanged | `rm -rf <out> && LC_ALL=C sphinx-build -b html docs/source <out>`, grep both signals, compare base vs tip (see Code Examples) | `multiple toctrees` count nonzero at tip, or `N warnings.` differs from base's own `N` |
| DOC-18 / SC#4 (HTML) | Each page once in sidebar, nested under section | `html.parser`-based sidebar-scoped count script (Code Examples) over tip's `index.html`, all 5 targets + control | any target count != 1, or a target's parent != its section index, or control count != 1 |
| DOC-18 / SC#4 (Typst) | No dead `include()` in root; one edge per page from section index | `grep -n "include(" index.typ` (tip; expect none of the 5 pages), `grep -n "include-edges" typsphinx.typ` (base vs tip, expect byte-identical) | any of the 5 pages' `include()` line still present in root `index.typ` at tip, or edge set differs from base |
| DOC-18 / SC#4 (parent divergence) | `examples/basic` **and** `examples/advanced` parent transcribed, not fixed | Console `selecting: X <- Y` lines from the SC#3 HTML build, both pages (see Premise Check PC-2) | transcription omits either page, or attempts a fix beyond what's already landed |
| SC#5 | Local gates green, scope clean, branch pushed, CI green | `ruff check .`, `black --check .`, `mypy typsphinx/`, `pytest`; `git diff --stat <BASE>..HEAD -- typsphinx/ .github/workflows/`; `gh api …/required_status_checks`; `gh workflow run CI --ref <branch>` + job census | any gate nonzero exit; non-empty scoped diff; required-checks set differs; any CI job non-`success`, especially the four named OS lanes |

### Sampling Rate
- **Per task commit:** re-run the specific proof command for that task's requirement (e.g. after
  the `index.rst` edit, the SC#3 HTML-build grep; after the `tox.ini` edit, `tox -e linkcheck` once).
- **Per wave merge:** full pytest suite (regression only) + the base/tip comparison pair for DOC-18.
- **Phase gate:** the SC#5 local-gate quartet, then the dispatched CI run, before
  `/gsd-verify-work`.

### Wave 0 Gaps

None — existing test infrastructure (pytest) is unaffected and not the proof mechanism for this
phase's requirements; the proof mechanism is direct Sphinx/tox invocation with verbatim transcript
evidence, already fully demonstrated working in this research session.

## Security Domain

`security_enforcement: true` (`.planning/config.json`), ASVS level 1. This phase's surface area is
minimal: it edits build configuration and prose, and runs Sphinx's own `linkcheck` builder, which
makes outbound HTTP requests to URLs already committed in `docs/source/**.rst` and `CHANGELOG.md`
(not user-supplied input at request time — the URL list is fixed at commit time by whoever writes
the docs).

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-------------------|
| V2 Authentication | No | No auth surface in this phase |
| V3 Session Management | No | No session surface |
| V4 Access Control | No | No access-control surface |
| V5 Input Validation | Marginal | The URLs `linkcheck` fetches come from committed `.rst`/`CHANGELOG.md` sources reviewed via normal PR process, not runtime user input; Sphinx's own builder performs the HTTP fetch (no custom fetch code added) |
| V6 Cryptography | No | No cryptographic operation introduced |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|-----------------------|
| SSRF via a malicious doc-source URL reaching internal infrastructure when `tox -e linkcheck` runs | Information Disclosure / Tampering (low likelihood, local-maintainer-run tool, not exposed as a service) | Out of scope for this phase — `tox -e linkcheck` stays local and manual per ROADMAP constraint 3 (no CI schedule/dispatch runs it); QUA-08 (a future CI job) would be the point to reconsider network-egress controls for an automated, unattended run. No code change needed here. |
| Credential/secret leakage via `output.json`/`output.txt` in `docs/_build/linkcheck/` | Information Disclosure | `docs/_build/` is already gitignored (standard Sphinx output convention); no new logging of secrets is introduced — `output.json` rows are `filename`, `lineno`, `status`, `code`, `uri`, `info`, none of which include request/response bodies or headers |

No further security work is indicated for this phase; it is a documentation/build-tooling change
with no new attack surface.

## Sources

### Primary (HIGH confidence — read/measured this session)
- `docs/source/conf.py`, `docs/source/index.rst`, `docs/source/user_guide/index.rst`,
  `docs/source/examples/index.rst`, `tox.ini`, `CLAUDE.md`, `README.md`,
  `docs/source/contributing.rst`, `pyproject.toml` — all read this session, all quotes verbatim.
- `.venv/lib/python3.13/site-packages/sphinx/builders/linkcheck.py` (installed Sphinx 9.1.0) —
  read this session, lines cited for `write_linkstat`, exit-code logic, 429/503 handling, and
  `linkcheck_anchors` default.
- `typsphinx/translator.py:207, 343, 452-465, 468-507` — read this session (read-only per
  constraint 2), confirms the include-edge-guard mechanism the folded todo describes.
- Live `sphinx-build -b html`, `-b typst`, `-b linkcheck` runs against today's tree (`5cf396a4`),
  via a throwaway `git worktree` and a `git archive` extraction, both removed after use.

### Secondary (MEDIUM confidence)
- `.planning/todos/pending/2026-08-16-root-toctree-duplicates-section-children-in-html-sidebar.md`
  — prior measurement (2026-08-16), partially superseded by this session's fresher measurement (see
  Premise Check PC-2).
- `.planning/milestones/v0.9.4-phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-CI-EVIDENCE.md`
  — evidence-file shape and conventions reused for the Validation Architecture / evidence
  recommendations above.

### Tertiary (LOW confidence)
- None used without corroboration.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new dependency; every version claim verified against the installed
  `.venv` or `pyproject.toml` this session.
- Architecture: HIGH — the include-edge/toctree-resolver interaction was traced end-to-end with
  live builds, not inferred from documentation.
- Pitfalls: HIGH — both major pitfalls (path-relative `conf.py`, sidebar-vs-body double-counting)
  were discovered by hitting them this session, not anticipated speculatively.

**Research date:** 2026-09-13
**Valid until:** Re-measure at `PHASE_BASE_SHA` execution time per constraint 8 — every count in
this document is context, not a pass threshold, and the underlying tree may have moved by then
(dependabot PRs listed in ROADMAP constraint 6 could land on `main` first).
