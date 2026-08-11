# Phase 44: `typst_documents` Default Derivation + Builder Input Hardening - Research

**Researched:** 2026-08-04
**Domain:** Sphinx `Config` callable-default mechanics; `TypstPDFBuilder.finish()` input hardening
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01: A degenerate `project` name keeps Sphinx's `'sphinx'` sentinel verbatim.** No typsphinx-side
  fallback, no extra warning, no branch. Measured 2026-08-04 (Sphinx 9.1.0):
  `make_filename_from_project()` (1) removes a trailing `' Documentation'`, (2) deletes every
  character matching `[^a-zA-Z0-9_-]` (`_no_fn_re`), (3) lowercases, (4) returns `'sphinx'` if the
  result is empty. So `project='日本語 プロジェクト'` → `'sphinx'`, `project='Проект'` → `'sphinx'`,
  `project=''` → `'sphinx'`, `project='ドキュメント v1'` → `'v1'`, `project='MyApp Documentation'`
  → `'myapp'`, `project='My Cool Project'` → `'mycoolproject'`. A project with a non-ASCII name gets
  `sphinx.typ` / `sphinx.pdf` — exactly as it already gets `sphinx.tex` from `-b latex` today. Users
  who want another name set `typst_documents` explicitly, which always wins (SC#2).
  — Reversibility: reversible — adding a fallback branch later is local to the derivation function.

- **D-02: The derived entry is a 5-tuple in LaTeX's shape, and the wiring of explicit `[2]`/`[3]` is
  deferred to a todo.** Derived value:
  `[(config.root_doc, make_filename_from_project(config.project) + ".typ", config.project, config.author, "typst")]`.
  The trailing `.typ` is included because `default_latex_documents` includes `.tex`;
  `_resolve_output_stem` strips a literal trailing `.typ` already (builder.py:180), so both forms
  work and LaTeX-consistency decides it. typsphinx reads **only** `entry[0]` and `entry[1]` — Sphinx's
  LaTeX builder reads `entry[:5]` (title/author DO reach the rendered document there). This phase
  emits `[2]`/`[3]`/`[4]` for shape-consistency only; wiring their consumption is out of scope.
  — Reversibility: reversible — the arity is one literal in one function; the deferral is a todo file.

### Opt-out semantics

- **D-03: An explicit `typst_documents = []` stays an opt-out — the `WARNING` is kept at `WARNING`
  severity and only its wording is corrected.** Once the derived default lands, unset can never be
  empty (verified: with a callable default, `config.typst_documents` returns the derived list when
  unset and `[]` when the user wrote `[]`), so the existing message at `builder.py:907-909` —
  `"No documents defined in typst_documents. Nothing to compile."` — is only reachable via an
  explicit empty list, where it reads as if the setting were absent. New wording must say the setting
  is present and empty, and that removing it restores the derived default. Severity stays `WARNING`
  so `-W` builds keep failing, matching Sphinx's LaTeX builder's equivalent situation.
  — Reversibility: reversible — message text and log level.

- **D-04: The default is registered as a Sphinx callable default, exactly as `latex_documents` is.**
  `app.add_config_value("typst_documents", <derivation callable>, "html", [list])` in
  `typsphinx/__init__.py:44`. Verified live 2026-08-04 with that exact signature: type validation
  accepts a callable default, an unset project yields the derived list, and an explicit `[]` yields
  `[]`. Every existing reader then sees the same resolved value with no further change —
  `writer.py:55` `_is_master_document`, `builder.py:117` `_compute_master_included_docnames`,
  `builder.py:160` `_resolve_output_stem`, `builder.py:904` `finish`. Rejected: a `config-inited`
  handler that materializes the value, and a builder-local helper (both diverge from LaTeX or leave
  `config.typst_documents` desynchronized from what `finish()` looks up).
  — Reversibility: reversible pre-release — one registration line.

### The user-visible-change record (SC#4)

- **D-05: The before/after record covers the filename AND the content change.** Measured 2026-08-04
  on a real build of a minimal project with `project = 'My Cool Project'` and no `typst_documents`:
  `sphinx-build -b typstpdf` exits 0, emits exactly one `WARNING`, writes **zero PDFs**, and writes
  `out/index.typ` at **373 bytes** — `@preview` imports plus body only, with **no template applied**,
  because `_is_master_document('index')` is False. After the change the same project emits
  `mycoolproject.typ` + `mycoolproject.pdf` **with the full template applied**, because the derived
  entry makes `index` a master. Both facts (rename AND structure change) go into the SC#4 evidence and
  the source text handed to Phase 46.
  — Reversibility: reversible — it widens what the evidence file records, nothing else.

### Claude's Discretion

- **BLD-01's error shape and validation width.** Open: (a) collect into the existing `failures` list
  and report through the single end-of-loop `ExtensionError` (consistent with the WR-01 aggregate
  design, other masters still compile) versus raise immediately; (b) validate only "docname is not
  `str`" (the todo's exact scope) versus broader `typst_documents` entry-shape validation — the latter
  plus a `difflib` "did you mean" suggestion were both explicitly deferred in Phase 22.3's
  `<deferred>` and should not be widened into by accident.
- **Which existing tests are updated and how** (SC#5 requires each change be traceable to this
  requirement rather than absorbed silently). Measured starting point: **all 103** `conf.py` files in
  the repo that mention `typst_documents` already set it. `tests/test_config.py:6-19` asserts only
  that the config value exists and is a `list` — both still hold under a callable default. A new
  fixture is needed to exercise the unset path at all.
- **Where the SC#4 evidence file lives and what it is named** (a `44-GATE-EVIDENCE-*.md` in the phase
  directory is the established shape).
- **Whether `-b typst` alone should warn on an explicit empty list.** D-03 decided the message for the
  `typstpdf` path only.

### Deferred Ideas (OUT OF SCOPE)

- Wiring `typst_documents` entry `[2]` (title) / `[3]` (author) into the rendered output — filed as
  `.planning/todos/pending/2026-08-04-typst-documents-title-author-elements-ignored.md`.
- Giving the 5th tuple element (`"Document class (usually 'typst')"`) an actual meaning.
- Exhaustive `typst_documents` shape validation and a `difflib`-based "did you mean" suggestion for an
  unknown docname — both deferred in Phase 22.3 and still deferred. Do not widen BLD-01 into these.
- A `-b typst`-side warning for an explicit empty list — D-03 only settled the `typstpdf` path.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| CONF-08 | With `typst_documents` unset, `sphinx-build -b typstpdf` produces a PDF — the default is derived from `root_doc`/`project`/`author` in LaTeX's own shape (`<project>.typ`); an explicit setting always wins. | See "Standard Stack", "Architecture Patterns" (callable-default mechanics verified against the installed Sphinx 9.1.0 `Config.__getattr__`), "Code Examples" (derivation function + registration), "Common Pitfalls" (no-caching pitfall, fixture-blast-radius audit). |
| BLD-01 | A non-`str` docname reaching `TypstPDFBuilder.finish()` fails with an actionable typsphinx-level error rather than a raw `TypeError`. | See "Architecture Patterns" (exact crash-site trace, re-confirmed against current `builder.py` line numbers), "Code Examples" (guard clause, in the `failures`-list style), "Don't Hand-Roll" (reuse the existing aggregate-error mechanism). |
</phase_requirements>

## Summary

Both requirements touch exactly one method, `TypstPDFBuilder.finish()` (`typsphinx/builder.py:875-967`),
which is why the phase groups them. CONF-08 is a **one-line registration change plus one new pure
function**: replace `app.add_config_value("typst_documents", [], "html", [list])` with a callable
default, mirroring Sphinx's own `latex_documents` / `default_latex_documents()` mechanism byte-for-byte
(verified this session by reading the installed `sphinx==9.1.0` package directly, not from memory).
Sphinx's `Config.__getattr__` (verified, `sphinx/config.py:446-470`) already does the right thing for a
callable default with **zero other changes required**: every one of typsphinx's four read sites
(`writer.py:55`, `builder.py:117`, `builder.py:160`, `builder.py:904`) calls `getattr(config,
"typst_documents", ...)`, which transparently receives the same resolved list whether it came from a
literal default, a callable default, or the user's `conf.py`. An explicit `typst_documents` (including
an explicit `[]`) always wins because `Config.__getattr__` checks `self._raw_config` (what the user's
`conf.py` set) strictly before falling back to `self._options[name].default`.

BLD-01 is a four-line input guard. The crash trace was re-verified this session against the CURRENT
`builder.py` (not just the archived todo): `finish()` extracts `docname = doc_tuple[0]` at line 928,
calls `_resolve_output_stem(docname)` at 929 (tolerates any type — only does `==` comparisons), then
`_directory_preserving_relpath(docname, stem)` at 930, which calls `posixpath.dirname(docname)` at
line 270 — a raw `TypeError: expected str, bytes or os.PathLike object, not int` for a non-`str`
docname, raised **before** the `try:` block at line 946 that aggregates into `failures`. The fix is to
validate `isinstance(docname, str)` immediately after line 928, append to `failures` and `continue`
(matching the existing `if not doc_tuple:` malformed-entry guard three lines above it verbatim in
style), rather than let the crash escape.

**Primary recommendation:** Add a pure `_default_typst_documents(config) -> list` function (co-located
with `TypstBuilder` in `builder.py`, imported by `__init__.py`) that mirrors
`default_latex_documents()`'s exact shape, register it as the callable default in `__init__.py:44`, and
add a 4-line `isinstance(docname, str)` guard in `finish()`'s loop that appends to the existing
`failures` list — no new exception class, no new validation surface, no widening beyond the todo's
exact scope.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| `typst_documents` default derivation | Config / Build orchestration (Sphinx `Config` object, `typsphinx/__init__.py` registration) | — | A pure function of `config.root_doc`/`config.project`/`config.author`; no I/O, no builder state. |
| Master-vs-included routing (`_is_master_document`) | Writer (`typsphinx/writer.py`) | — | Unchanged code; its *result* changes because the config value it reads changes (D-05's content half). |
| Output filename resolution (`_resolve_output_stem`, `_directory_preserving_relpath`) | Builder (`typsphinx/builder.py`) | — | Filesystem-path derivation; already the single normalization site for every `typst_documents` entry, explicit or derived. |
| Non-`str` docname validation (BLD-01) | Builder (`TypstPDFBuilder.finish()`) | — | The PDF-compile aggregation loop is the only place a `typst_documents` entry's docname is dereferenced as a path component without going through `_resolve_output_stem`'s own type-tolerant guards first. |
| PDF compilation | Builder → `typsphinx/pdf.py` (`typst-py`) | — | Unaffected by this phase; only reached for the entries that pass validation. |

## Standard Stack

No new runtime dependency is introduced (milestone invariant #1: zero new runtime dependencies). This
phase reuses functions Sphinx already ships and typsphinx already imports transitively.

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `sphinx` | `>=9.1,<10` (installed: **9.1.0**, verified live via `import sphinx; sphinx.__version__`) | `sphinx.util.osutil.make_filename_from_project`, `Config.__getattr__`'s callable-default protocol | Already a direct dependency (`pyproject.toml`); no version bump needed — both symbols exist unchanged in 9.1.0. |

### Supporting

None — no new packages. `sphinx.util.osutil.make_filename_from_project` and
`sphinx.errors.ExtensionError` (already imported in `builder.py`) are the only external symbols this
phase touches, and both are already used elsewhere in the codebase.

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| A Sphinx callable default (D-04) | A `config-inited` event handler that materializes the value into `config.typst_documents` | Rejected in CONTEXT.md D-04: adds a handler + priority to manage, diverges from the LaTeX-parity precedent this phase is built on. |
| A Sphinx callable default | A builder-local helper (e.g. a `TypstBuilder` method called at `write()`/`finish()` time) | Rejected in CONTEXT.md D-04: leaves `config.typst_documents` itself empty/`[]`, so any ONE of the four read sites that isn't updated silently desyncs (e.g. the writer's `_is_master_document` check disagreeing with `finish()`'s lookup). |
| `isinstance(docname, str)` guard reusing `failures` | Raising `TypeError`/`ExtensionError` immediately at the crash site | The immediate-raise path aborts the WHOLE build the instant one malformed entry is hit, even if other configured masters would compile fine — inconsistent with the WR-01 "attempt every master, then raise once" contract already governing every other kind of malformed entry in this same loop. |

**Installation:** none — no `pip`/`uv` command needed for this phase.

**Version verification:** `sphinx==9.1.0` confirmed installed in the project's own `.venv`
(`source .venv/bin/activate && python3 -c "import sphinx; print(sphinx.__version__)"` → `9.1.0`),
matching the `pyproject.toml` constraint `sphinx>=9.1,<10`. No package version changes as part of this
phase.

## Package Legitimacy Audit

**Not applicable — this phase installs no external packages.** Zero new runtime dependencies (milestone
invariant #1); every symbol used (`make_filename_from_project`, `Config.__getattr__`'s callable-default
protocol, `ExtensionError`) is already inside the existing `sphinx>=9.1,<10` dependency. No
`package-legitimacy check` run was needed.

## Architecture Patterns

### System Architecture Diagram

```
conf.py (user's project)
    │
    │  (may or may not set `typst_documents = [...]`)
    ▼
Sphinx Config object  ── app.add_config_value("typst_documents", <callable>, "html", [list])
    │                      registered in typsphinx/__init__.py:setup()  [THIS PHASE changes the
    │                      2nd positional arg from `[]` to a derivation function]
    │
    │  config.typst_documents  (attribute access, EVERY time — see Pitfall below)
    ▼
Config.__getattr__ (sphinx/config.py:446, UNCHANGED by this phase, verified installed source)
    │
    ├─ name in self._overrides?           → command-line -D override wins
    ├─ name in self._raw_config?          → EXPLICIT conf.py setting wins (SC#2 — even `[]`)
    └─ else: default = self._options[name].default
             if callable(default): return default(self)   ◄── THIS is where the new
                                                               derivation function runs,
                                                               RE-INVOKED on every access
                                                               (no caching for callables)
    │
    ▼
[ derived list, or user's explicit list, or [] ]
    │
    ├──► writer.py:55  _is_master_document(docname)   — decides template-vs-included per doc
    ├──► builder.py:117 _compute_master_included_docnames() — toctree closure for xref degrade
    ├──► builder.py:160 _resolve_output_stem(docname)  — filename normalization (D-06/D-07 guards)
    └──► builder.py:904 TypstPDFBuilder.finish()        — PDF-compile loop
              │
              │  for doc_tuple in typst_documents:
              │      if not doc_tuple: → failures.append(...); continue   (existing guard)
              │      docname = doc_tuple[0]
              │      ██ THIS PHASE INSERTS: if not isinstance(docname, str):
              │      ██                          failures.append(...); continue   (BLD-01)
              │      stem = _resolve_output_stem(docname)             (tolerates any type)
              │      relative_path = _directory_preserving_relpath(docname, stem)
              │                          └─ posixpath.dirname(docname)  ◄── CRASH SITE
              │                             (TypeError for non-str, pre-fix)
              │      [compile via typst-py] → pdf_bytes / exception → failures
              │
              ▼
          failures: list  →  if any: raise ExtensionError(aggregate message)  (unchanged)
```

### Pattern 1: Sphinx callable config default (D-04)

**What:** `app.add_config_value(name, <function>, rebuild_trigger, types)` where the 2nd argument is a
function `(config) -> value` instead of a literal. Sphinx's `Config.__getattr__` detects `callable(default)`
and invokes it with the `Config` instance, on every attribute access that reaches the default branch
(i.e., every time the user has NOT set the value and no override applies).

**When to use:** When a config value's default depends on OTHER config values (here: `root_doc`,
`project`, `author`) that are resolved later than `add_config_value()`'s own call time — exactly
`latex_documents`'s situation.

**Example (verified this session by reading the installed package, not from training memory):**

```python
# Source: .venv/lib/python3.13/site-packages/sphinx/builders/latex/__init__.py:575-587
# (installed sphinx==9.1.0; verified via `inspect.getsource`)
def default_latex_documents(config: Config) -> list[tuple[str, str, str, str, str]]:
    """Better default latex_documents settings."""
    project = texescape.escape(config.project, config.latex_engine)
    author = texescape.escape(config.author, config.latex_engine)
    return [
        (
            config.root_doc,
            make_filename_from_project(config.project) + '.tex',
            texescape.escape_abbr(project),
            texescape.escape_abbr(author),
            config.latex_theme,
        )
    ]

# ... registered at (same file, line 604-606):
app.add_config_value(
    'latex_documents', default_latex_documents, '', types=frozenset({list, tuple})
)
```

```python
# Source: .venv/lib/python3.13/site-packages/sphinx/config.py:446-470
# (installed sphinx==9.1.0; verified via Read tool this session)
def __getattr__(self, name: str) -> Any:
    if name in self._options:
        if name in self._overrides:
            ...  # -D override path
        if name in self._raw_config:
            value = self._raw_config[name]
            self.__setattr__(name, value)
            return value
        # finally, fall back to the default value
        default = self._options[name].default
        if callable(default):
            return default(self)          # <-- re-invoked EVERY access, never cached
        self.__dict__[name] = default     # <-- non-callable defaults ARE cached; callables are NOT
        return default
```

**typsphinx's derivation function (this phase, new — matches D-02's exact literal):**

```python
# typsphinx/builder.py — co-located with TypstBuilder, module-level function
def _default_typst_documents(config: "Config") -> list:
    """Sphinx-native default for ``typst_documents``, mirroring
    ``sphinx.builders.latex.default_latex_documents`` (CONF-08).

    Derives a single master entry from ``root_doc``/``project``/``author``,
    with the target name in LaTeX's own shape (``make_filename_from_project``).
    Only invoked when the user has NOT set ``typst_documents`` in conf.py --
    an explicit setting (including an explicit ``[]``) always wins, because
    Sphinx's ``Config.__getattr__`` checks ``_raw_config`` before falling
    back to this callable default.
    """
    return [
        (
            config.root_doc,
            make_filename_from_project(config.project) + ".typ",
            config.project,
            config.author,
            "typst",
        )
    ]
```

```python
# typsphinx/__init__.py:44 -- the ONE line D-04 changes
app.add_config_value("typst_documents", _default_typst_documents, "html", [list])
```

Note: typsphinx does NOT need LaTeX's `texescape.escape(...)` calls — that escaping is specific to
LaTeX's `\title{}`/`\author{}` macro syntax, and typsphinx does not consume `entry[2]`/`entry[3]` at all
(D-02); Typst's own metadata plumbing (`template_engine.py`, driven by `config.project`/`config.author`
directly, not by the tuple) has no equivalent escaping need.

### Pattern 2: Aggregate-then-raise error handling (existing, BLD-01 joins it)

**What:** `TypstPDFBuilder.finish()` never raises immediately on a per-entry problem; it appends
`(identifier, message)` to a `failures: list[tuple[str, str]]` and `continue`s the loop, then raises a
single `ExtensionError` after every configured master has been attempted.

**When to use:** Any new per-entry validation added to this loop (BLD-01's case).

**Example — the existing malformed-entry guard BLD-01's fix sits three lines below, in the same style
(verified against the CURRENT file this session, `typsphinx/builder.py:924-928`):**

```python
# Source: typsphinx/builder.py:916-931 (current, verified via Read this session)
for doc_tuple in typst_documents:
    if not doc_tuple:
        logger.warning(f"Malformed typst_documents entry: {doc_tuple!r}")
        failures.append((repr(doc_tuple), "malformed typst_documents entry"))
        continue
    docname = doc_tuple[0]
    # <-- BLD-01's guard belongs HERE, before _resolve_output_stem/
    #     _directory_preserving_relpath are ever called with `docname`.
    stem = self._resolve_output_stem(docname)
    relative_path = self._directory_preserving_relpath(docname, stem)
    typ_file = path.normpath(path.join(self.outdir, relative_path + ".typ"))
```

**BLD-01's guard, in the same style (this phase, new):**

```python
    docname = doc_tuple[0]
    if not isinstance(docname, str):
        message = f"typst_documents entry has a non-str docname: {docname!r}"
        logger.warning(message)
        failures.append((repr(docname), message))
        continue
    stem = self._resolve_output_stem(docname)
    ...
```

This mirrors the `if not doc_tuple:` guard immediately above it verbatim in shape (warn, append to
`failures`, `continue`), so the loop's existing "attempt every master, then raise once" contract
(D-02 of the WR-01 design, `typsphinx/builder.py:885-894`'s own docstring) extends to this new failure
kind with zero new mechanism.

### Recommended Project Structure

No new files/directories for CONF-08 or BLD-01's production code — both changes land inside the two
existing files already named in `<canonical_refs>`:

```
typsphinx/
├── __init__.py         # D-04: one line changed (add_config_value's 2nd arg)
└── builder.py           # + _default_typst_documents() (module-level, new)
                          # + BLD-01 guard inside TypstPDFBuilder.finish() (4 lines, new)
                          # D-03: warning message text changed at the existing early-return
tests/
├── test_config.py                              # unaffected (asserts only hasattr + isinstance list)
├── test_builder_output_stem.py                 # unaffected (sets typst_documents explicitly)
├── test_pdf_generation.py                      # unaffected (sets typst_documents explicitly)
├── fixtures/
│   └── <new fixture omitting typst_documents>/  # NEW — the only way to exercise the unset path
│       ├── conf.py                              #   (no `typst_documents =` line at all)
│       └── index.rst
└── test_<new>_default_derivation_gate.py        # NEW — real sphinx-build -b typstpdf assertion
└── test_<new>_non_str_docname_gate.py           # NEW — mirrors test_missing_and_malformed_master_gate.py
```

### Anti-Patterns to Avoid

- **Caching the derived value on the builder instance.** The callable default is invoked fresh on
  every `config.typst_documents` access (verified: `Config.__getattr__`'s callable branch has no
  `self.__dict__[name] = value` line, unlike the non-callable branch). Do not add builder-side memoization
  "for performance" — the function is a few string operations, already as cheap as every other config
  read in this codebase, and memoizing would risk staleness if `config.project` were ever mutated
  mid-build (it is not, today, but the anti-pattern is still worth avoiding).
- **Widening BLD-01 into full entry-shape validation.** Phase 22.3 and this phase's own CONTEXT.md
  Discretion note explicitly reserve that for later (with a `difflib` suggestion for unknown docnames).
  Adding it here would be an undiscussed second behavior change riding along with the two locked ones.
- **Raising immediately instead of joining `failures`.** Breaks the attempt-all-then-raise contract
  that BLD-01's own sibling guard (`if not doc_tuple:`) already establishes three lines above.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Deriving a safe filename stem from an arbitrary `project` string | A custom slugify/transliteration routine | `sphinx.util.osutil.make_filename_from_project` (already a transitive dependency, already used identically by LaTeX) | Sphinx already solved the degenerate-input space (non-ASCII, empty, whitespace-only) via `_no_fn_re` + the `'sphinx'` sentinel fallback (D-01) — re-implementing it risks a shape that disagrees with `-b latex`'s own output for the same `conf.py`, which is the exact inconsistency CONF-08 exists to avoid. |
| Making an unset config value resolve to a real value before the writer/builder ever read it | A `config-inited` handler, a builder `init()`-time materialization | Sphinx's built-in callable-default protocol (`Config.__getattr__`) | Explicitly the mechanism `latex_documents` already uses; a hand-rolled materialization step is an entirely new code path with its own priority-ordering and staleness risks that D-04 rejected for exactly this reason. |
| Reporting a per-entry validation failure without aborting other masters | A new exception class, a per-entry try/except with its own message format | The existing `failures: list[tuple[str, str]]` + terminal `ExtensionError` in `finish()` | One aggregation mechanism already exists and is exercised end-to-end by `tests/test_missing_and_malformed_master_gate.py`; a second, differently-shaped error path for BLD-01 alone would fragment the "attempt every master" contract into two behaviors. |

**Key insight:** Every piece of this phase already has a working, tested precedent inside the same
process — Sphinx's LaTeX builder for the derivation, and typsphinx's own `finish()` loop for the
error-aggregation shape. The task is transcription with typsphinx-specific substitutions (`.typ`
instead of `.tex`, no `texescape`), not design.

## Common Pitfalls

### Pitfall 1: The callable default is invoked repeatedly, not once

**What goes wrong:** A future maintainer (or an executor mid-phase) might assume `config.typst_documents`
is resolved once and cached, and add a stateful or expensive operation inside the derivation function.

**Why it happens:** The NON-callable default branch in `Config.__getattr__` DOES cache
(`self.__dict__[name] = default`); the callable branch conspicuously does not
(`return default(self)` with no assignment). This asymmetry is easy to miss on a skim.

**How to avoid:** Keep `_default_typst_documents` a pure function of its `config` argument (string ops
only, as D-02's literal already is) — exactly what LaTeX's own `default_latex_documents` does.

**Warning signs:** Any `global`/module-level mutable state referenced inside the derivation function,
or a comment claiming "computed once at config-inited."

### Pitfall 2: `temp_sphinx_app`'s `conf.py` never sets `typst_documents` — used by ~250 test call sites

**What goes wrong:** `tests/conftest.py:59-65`'s `temp_sphinx_app` fixture writes a `conf.py` containing
only `extensions`, `project`, `author` — no `typst_documents` line at all. This fixture is referenced
across 9 test files and roughly 250 individual test-function parameters (`test_admonitions.py` (54),
`test_builder.py` (34), `test_config.py` (10), `test_builder_output_stem.py` (48),
`test_line_blocks.py` (9), `test_topics.py` (15), `test_extension.py` (3), `test_footnotes.py` (13),
`test_inline_references.py` (42), `test_pdf_generation.py` (27) — counted via grep this session). After
D-04 lands, `app.config.typst_documents` on EVERY one of these apps resolves to a derived
`[('index', 'testproject.typ', 'Test Project', 'Test Author', 'typst')]` instead of `[]`.

**Why it doesn't actually break anything (verified this session, not assumed):** Grepping all nine
files for `.translate()`, `.write(`, `app.build(`, `writer.translate`, and `_is_master_document` found
**zero matches** — none of them drive a full `write()`/`translate()` pass through `temp_sphinx_app`;
they build hand-crafted doctrees and feed them directly to `TypstTranslator`, or (in
`test_pdf_generation.py`'s case) construct a `TypstPDFBuilder` and set `builder.config.typst_documents`
explicitly BEFORE calling `finish()` (confirmed at `test_pdf_generation.py:94`, `:126`, `:271`, `:299`,
`:333`, `:371`, `:404`, `:437`, `:543` — every `finish()`-exercising test overrides the config value
directly). `test_config.py:6-19`'s two `temp_sphinx_app`-based assertions
(`test_default_typst_documents_config`, `test_typst_documents_config_structure`) only check
`hasattr(...)` and `isinstance(..., list)` — both still hold for the derived list.

**How to avoid:** Do not assume this pitfall is closed just because it wasn't caught by the grep above —
re-run the FULL suite (not just these nine files) after landing D-04, since a full-suite run is the
only actual proof. This grep result narrows the search space; it is not a substitute for SC#5's real
green-suite requirement.

**Warning signs:** Any NEW test added elsewhere in this phase that uses `temp_sphinx_app` AND calls
`builder.write(...)`/`writer.translate()` without first setting `typst_documents` explicitly will now
render 'index' as a MASTER (full template applied) rather than an included document — a behavior
change relative to every pre-existing test's assumption, should any such test exist outside the nine
audited above.

### Pitfall 3: `_resolve_output_stem` tolerates a non-`str` docname; `_directory_preserving_relpath` does not

**What goes wrong:** A narrow fix that validates `docname` type only where `_directory_preserving_relpath`
is called (rather than immediately after `docname = doc_tuple[0]`) works, but wastes a full
`_resolve_output_stem` call first and separates the "read the bad value" and "reject the bad value"
steps by one line for no benefit.

**Why it happens:** `_resolve_output_stem`'s only operations on `docname` are `==` comparisons
(`entry[0] == docname`), which never raise for any type — so it silently "succeeds" on a malformed
input, producing a normal-looking `stem` string before the REAL crash site three lines later.

**How to avoid:** Place the `isinstance(docname, str)` guard immediately after
`docname = doc_tuple[0]` (line 928 in the current file), before either helper is called — this is also
where `_resolve_output_stem`'s own equivalent guard for a too-short tuple happens (compare
`if not doc_tuple:` two lines above), keeping every per-entry validation grouped together at the top of
the loop body.

**Warning signs:** A fix that validates INSIDE `_directory_preserving_relpath` itself rather than in
`finish()`'s loop — that method is a generic path-combination helper with other callers
(`write_doc`/`TypstPDFBuilder.write_doc`, both of which only ever receive real string docnames from
`env.found_docs`); pushing the guard down into it would validate a case those callers can never
actually hit, and would report the error using whatever exception shape that low-level method chooses,
diverging from `finish()`'s established `failures`-list convention.

### Pitfall 4: A five-element derived tuple looks richer than it is

**What goes wrong:** Seeing `config.project`/`config.author` land in `entry[2]`/`entry[3]` of the
derived tuple might suggest they now flow through to the rendered title/author — they do not.

**Why it happens:** typsphinx's title/author in the rendered document come from
`sphinx_metadata = {"project": config.project, "author": config.author, ...}` in `writer.py:207-211`,
built independently of `typst_documents` entirely (verified this session, `writer.py:203-211`). The
derived tuple's `[2]`/`[3]` are dead weight for typsphinx today — present only because D-02 chose to
match LaTeX's 5-tuple *shape*, not because anything reads them.

**How to avoid:** Do not add code in this phase that reads `entry[2]`/`entry[3]` "since they're right
there now" — that is exactly the deferred todo
(`2026-08-04-typst-documents-title-author-elements-ignored.md`) this phase must not fold in.

## Code Examples

### Full derivation function + registration change

```python
# typsphinx/builder.py -- add near the top of the module, after imports,
# or immediately above class TypstBuilder (either placement keeps it close
# to _resolve_output_stem, its downstream consumer).
from sphinx.config import Config
from sphinx.util.osutil import make_filename_from_project


def _default_typst_documents(config: Config) -> list:
    """CONF-08: Sphinx-native default for ``typst_documents``.

    Mirrors ``sphinx.builders.latex.default_latex_documents`` (verified
    against the installed sphinx==9.1.0 source this session). Returns a
    single master entry derived from ``root_doc``/``project``/``author``,
    target name in LaTeX's own shape via ``make_filename_from_project``.
    Only invoked by Sphinx's ``Config.__getattr__`` when the user has NOT
    set ``typst_documents`` -- an explicit setting (including an explicit
    ``[]``) always wins (SC#2).
    """
    return [
        (
            config.root_doc,
            make_filename_from_project(config.project) + ".typ",
            config.project,
            config.author,
            "typst",
        )
    ]
```

```python
# typsphinx/__init__.py:44 -- the only registration-site change
app.add_config_value("typst_documents", _default_typst_documents, "html", [list])
```

### BLD-01 guard, in place

```python
# typsphinx/builder.py, inside TypstPDFBuilder.finish()'s loop
for doc_tuple in typst_documents:
    if not doc_tuple:
        logger.warning(f"Malformed typst_documents entry: {doc_tuple!r}")
        failures.append((repr(doc_tuple), "malformed typst_documents entry"))
        continue
    docname = doc_tuple[0]
    if not isinstance(docname, str):
        message = (
            f"typst_documents entry has a non-str docname: {docname!r} "
            "-- expected a str"
        )
        logger.warning(message)
        failures.append((repr(docname), message))
        continue
    stem = self._resolve_output_stem(docname)
    relative_path = self._directory_preserving_relpath(docname, stem)
    typ_file = path.normpath(path.join(self.outdir, relative_path + ".typ"))
    ...
```

### D-03's corrected warning wording (early-return branch)

```python
# typsphinx/builder.py:906-910 -- wording only, severity unchanged (WARNING)
if not typst_documents:
    logger.warning(
        "typst_documents is explicitly set to an empty list -- nothing will "
        "be compiled. Remove the setting entirely to use the derived "
        "default (root_doc/project/author)."
    )
    return
```

### Test fixture that omits `typst_documents` entirely (the only way to exercise the unset path)

```python
# tests/fixtures/<new_fixture_name>/conf.py -- deliberately has NO
# `typst_documents = ...` line, unlike every one of the 103 existing
# conf.py files in the repo that mention it.
project = "Quickstart Default Gate"
author = "Test Author"
release = "1.0.0"

extensions = ["typsphinx"]

# typst_documents intentionally left unset -- CONF-08's derivation must
# resolve it to [('index', 'quickstartdefaultgate.typ', ...)].
```

### Non-str-docname fixture (mirrors `missing_and_malformed_master_gate`'s established pattern)

```python
# tests/fixtures/<new_fixture_name>/conf.py -- one valid master (still
# compiles, per the attempt-all-then-raise contract) plus one entry with a
# non-str docname (BLD-01's exact trigger).
project = "Non-Str Docname Gate"
author = "Test Author"
release = "1.0.0"

extensions = ["typsphinx"]

typst_documents = [
    ("index", "index", "Valid Master", "Test Author"),
    (123, "manual.typ", "Bad Docname", "Test Author"),
]
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|---------------|--------|
| `typst_documents` default `[]`, literal | `typst_documents` default is a callable derived from `root_doc`/`project`/`author` | This phase (CONF-08) | `sphinx-build -b typstpdf` with unset config now produces a PDF instead of exiting 0 with zero output. Renames the pre-existing `-b typst` unset-config output (`index.typ` → `<project-slug>.typ`), an accepted, CHANGELOG-documented cost. |
| A non-`str` docname in `typst_documents` crashes `finish()` with a raw `TypeError` | Reported through the existing `failures`-list + aggregate `ExtensionError`, other masters still compile | This phase (BLD-01) | The build still fails (non-zero exit is correct and unchanged — a malformed config IS an error), but the diagnostic is typsphinx-authored and actionable, and it no longer aborts compilation of OTHER valid masters in the same build. |

**Deprecated/outdated:** None — no typsphinx API is deprecated by this phase; both changes are additive
hardening of existing internal surfaces.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The `_default_typst_documents` function's placement (module-level in `builder.py`, imported by `__init__.py`) is the best location — a genuinely free implementation choice, not verified against any authority since none exists for it. | Code Examples / Recommended Project Structure | Low — purely organizational; any consistent placement (e.g. a new small module) satisfies CONF-08 equally. The planner may choose differently without contradicting any measured fact. |
| A2 | The suggested new-fixture and new-test-file naming (`test_<new>_default_derivation_gate.py`, `test_<new>_non_str_docname_gate.py`) is illustrative, not a locked filename. | Code Examples / Recommended Project Structure | Low — SC#5 requires traceability, not a specific filename; the planner should pick one consistent with the existing `*_render_gate.py` / `*_gate.py` naming convention already used throughout `tests/`. |

**If this table is empty:** N/A — two low-risk organizational items are logged above; every factual/
behavioral claim elsewhere in this document was verified this session by reading the installed
`sphinx==9.1.0` source, the current `typsphinx` source, or an existing test file, or is copied verbatim
from `44-CONTEXT.md`'s own already-measured findings per the research brief's instruction not to
re-derive those.

## Open Questions

1. **Exact new-fixture/new-test naming and file count for BLD-01 and CONF-08.**
   - What we know: the established sibling pattern is `tests/fixtures/missing_and_malformed_master_gate/`
     + `tests/test_missing_and_malformed_master_gate.py` (a real `sphinx-build -b typstpdf` subprocess
     gate asserting `returncode != 0`, the aggregate message fragment, and that the valid master's
     `.typ`/`.pdf` still get written) — directly reusable as the template for BLD-01's new gate.
   - What's unclear: whether BLD-01's non-str-docname case should get its OWN new fixture+test module
     (cleaner traceability per SC#5) or be added as a THIRD bad-entry kind inside the existing
     `missing_and_malformed_master_gate` fixture (less new-file surface, but muddies "which requirement
     does this fixture prove" for a future reader).
   - Recommendation: a dedicated new fixture + test module, matching CONTEXT.md's Discretion note (b)'s
     emphasis that "each change [be] traceable to this requirement rather than absorbed silently" — the
     same reasoning applies to a NEW test as to an edited existing one.

2. **Whether CONF-08's unset-default gate needs its own fixture or can reuse `tests/roots/test-basic`.**
   - What we know: `tests/roots/test-basic` is used by `test_target_name_render_gate.py` and DOES set
     `typst_documents` explicitly (confirmed via the grep census: it is one of the 103 conf.py files
     that mention it).
   - What's unclear: whether to add a second `test-basic`-like root without `typst_documents`, or a
     small purpose-built fixture (2-3 files) dedicated to CONF-08 alone.
   - Recommendation: a small purpose-built fixture — `tests/roots/test-basic` is shared across several
     unrelated gates already, and CONF-08 wants a MINIMAL project (mirroring the Quick Start exactly,
     per SC#1's own wording "A Sphinx project whose `conf.py` never mentions `typst_documents`").

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `sphinx` | CONF-08 (`make_filename_from_project`, `Config` callable-default protocol), BLD-01 | ✓ | 9.1.0 (installed, verified live) | — |
| `typst` (typst-py) | The PDF-compile half of both requirements' gate tests | ✓ (verified importable in `.venv` per `TYPST_AVAILABLE` guards already present in sibling test modules) | pinned `>=0.15.0,<0.16` | Gate tests already `@pytest.mark.skipif(not TYPST_AVAILABLE, ...)` — no new fallback needed, matches existing convention. |
| `uv` / per-worktree provisioning | Any executor running this phase (CLAUDE.md standing instruction) | ✓ (project-standard) | — | N/A — mandatory per CLAUDE.md, not a research finding. |

**Missing dependencies with no fallback:** none.
**Missing dependencies with fallback:** none — both real dependencies are already present and already
have an established skip-guard convention in this codebase.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 8.4+ (installed via `dev` extra), `sphinx.testing.fixtures` plugin |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]` (`testpaths = ["tests"]`, `--strict-markers`) |
| Quick run command | `uv run pytest tests/test_config.py tests/test_pdf_generation.py tests/test_missing_and_malformed_master_gate.py -v` (existing + new sibling modules, fast) |
| Full suite command | `uv run pytest` (matches `tox.ini`'s `[testenv]` `commands = pytest {posargs:tests/}`; no `-m "not slow"` filter is applied anywhere in this repo's CI, so the full run INCLUDES `tests/test_corpus_gate.py`'s real corpus-compile gate) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| CONF-08 | Unset `typst_documents`, `-b typstpdf` produces a PDF named from `make_filename_from_project` | integration (real subprocess `sphinx-build`) | `uv run pytest tests/test_<new>_default_derivation_gate.py -v` | ❌ Wave 0 — new fixture + new test module |
| CONF-08 | Explicit `typst_documents` always wins (SC#2) | unit + existing coverage | `uv run pytest tests/test_config.py::test_custom_typst_documents_config -v` | ✅ already exists, unaffected |
| CONF-08 | `-b typst`-only build's D-05 content-shape change (template applied to former "index" master) | covered implicitly by the same new integration test above, or a dedicated `-b typst` assertion | `uv run pytest tests/test_<new>_default_derivation_gate.py -v` | ❌ Wave 0 |
| BLD-01 | Non-`str` docname fails via the aggregate `ExtensionError`, other masters still compile | integration (real subprocess `sphinx-build`, mirrors `test_missing_and_malformed_master_gate.py`) | `uv run pytest tests/test_<new>_non_str_docname_gate.py -v` | ❌ Wave 0 — new fixture + new test module |
| SC#5 | Full suite + `black`/`ruff`/`mypy` + full-corpus `-b typstpdf` gate all green | full-suite / lint / type / slow-integration | `uv run pytest` (includes `tests/test_corpus_gate.py`, not `-m`-filtered in this repo), `uv run black --check .`, `uv run ruff check .`, `uv run mypy typsphinx/` | ✅ all commands already exist; no new tooling needed |

### Sampling Rate

- **Per task commit:** `uv run pytest tests/test_config.py tests/test_builder_output_stem.py tests/test_pdf_generation.py tests/test_missing_and_malformed_master_gate.py tests/test_<new>_*.py -v`
- **Per wave merge:** `uv run pytest` (full suite — no `-m` filter exists in this repo, so this already includes the slow corpus gate; budget time accordingly, it clones Sphinx's own `doc/` tree on first run)
- **Phase gate:** Full suite green (`uv run pytest`) + `black --check .` + `ruff check .` + `mypy typsphinx/` before `/gsd-verify-work`, per SC#5's exact wording.

### Wave 0 Gaps

- [ ] A new fixture directory under `tests/fixtures/` that omits `typst_documents` entirely — none of
      the 103 existing `conf.py` files in the repo can be reused for this (all set it).
- [ ] A new integration test module asserting CONF-08's SC#1 (PDF exists, named via
      `make_filename_from_project`) and SC#2 (explicit setting wins) via real `sphinx-build` subprocess
      calls, following `tests/test_missing_and_malformed_master_gate.py`'s
      `sys.executable -m sphinx` subprocess pattern (sidesteps the NixOS PATH-shadowing hazard already
      documented in that file's own docstring).
- [ ] A new fixture + test module for BLD-01's non-str-docname case, following the SAME subprocess
      pattern and the SAME "one valid master survives" assertion shape as
      `tests/test_missing_and_malformed_master_gate.py`.
- [ ] `tests/test_config.py` needs no NEW test to keep passing (its two `temp_sphinx_app`-based
      assertions already tolerate the derived default per Pitfall 2's grep-verified finding), but SC#5
      requires the planner to STATE that explicitly as a deliberate "no change needed, verified" line
      item rather than silently skip auditing this file.

*(Framework and lint/type tooling are already fully in place; no framework install step is needed.)*

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | No | Not a network-facing or multi-user surface; `conf.py` is trusted, site-owner-authored Python. |
| V3 Session Management | No | N/A — build-time CLI tool. |
| V4 Access Control | No | N/A. |
| V5 Input Validation | Yes | BLD-01 IS this category: a config-supplied value (`typst_documents` entry's docname) reaching a filesystem-path-construction function (`posixpath.dirname`) must be type-checked before use. The existing `_resolve_output_stem` path-traversal guard (D-06/D-07, `builder.py:188-220` — rejecting `/`, `\`, `..`, absolute paths, drive-qualified paths in the TARGET NAME) is the precedent this hardening extends; BLD-01 adds the analogous check for the DOCNAME position, narrowly scoped to type (not shape) per the Discretion note. |
| V6 Cryptography | No | N/A. |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Type confusion in a config-supplied tuple element reaching a raw stdlib path function (`posixpath.dirname`) | Denial of Service (an uncaught `TypeError` crashes the whole `sphinx-build` process with a raw traceback rather than a scoped, reported failure) | BLD-01's `isinstance(docname, str)` guard, feeding the existing `failures`-list aggregation — already the established mitigation shape in this exact loop for the sibling "malformed (empty) entry" case. |
| Path traversal via a `typst_documents` target name (`../../etc/passwd`-shaped) | Tampering (writing outside `outdir`) | Already mitigated, unaffected by this phase — `_resolve_output_stem`'s D-06/D-07 guard (`builder.py:182-220`) rejects any `/`, `\`, `..` segment, absolute path, or drive-qualified path in the TARGET NAME before it ever reaches `path.join(self.outdir, ...)`. Confirmed still active and untouched by this phase's changes (the derivation function's OWN output, `make_filename_from_project(project) + ".typ"`, can never contain a path separator — `_no_fn_re` strips both `/` and `\` along with everything else outside `[a-zA-Z0-9_-]`, so the new default can never even trigger this guard). |

Note: `conf.py` is executed as trusted Python by the site owner who runs `sphinx-build`; a malicious
`typst_documents` entry is a self-inflicted misconfiguration risk (crash/DoS against one's own build),
not a remote-attacker input-validation gap in the ASVS sense. V5 is included here because the ASVS
control (type-check before use) is the right engineering practice regardless of trust boundary, and
because BLD-01 is explicitly framed as diagnostic-quality hardening, not an actual vulnerability fix.

## Sources

### Primary (HIGH confidence — verified this session by reading installed/repo source directly)

- `.venv/lib/python3.13/site-packages/sphinx/builders/latex/__init__.py:575-606` (installed
  `sphinx==9.1.0`) — `default_latex_documents()` body and its `add_config_value('latex_documents', ...)`
  registration, read via the `Read` tool this session.
- `.venv/lib/python3.13/site-packages/sphinx/builders/latex/__init__.py:151-173` — `init_document_data()`,
  the `WARNING` D-03 mirrors, and the `entry[2]` title consumption D-02 explicitly does NOT replicate.
- `.venv/lib/python3.13/site-packages/sphinx/config.py:446-470` — `Config.__getattr__`, the callable-default
  invocation and non-caching behavior (Pitfall 1), read via the `Read` tool this session.
- `.venv/lib/python3.13/site-packages/sphinx/config.py:239-240` — `master_doc`/`root_doc` default is
  `'index'`, confirmed via grep + read this session.
- `sphinx.util.osutil.make_filename_from_project` / `make_filename` — source read live via
  `inspect.getsource()` in the project's own `.venv` this session (matches CONTEXT.md's D-01 table
  verbatim — not re-derived, cross-checked).
- `typsphinx/builder.py` (current, full file read this session) — exact current line numbers for
  `finish()`'s loop (916-931), the crash-site call chain (`_resolve_output_stem` 133-238,
  `_directory_preserving_relpath` 240-273), and the existing malformed-entry guard style.
- `typsphinx/writer.py` (current, full file read this session) — `_is_master_document` (41-71),
  `sphinx_metadata` construction (203-211) proving `entry[2]`/`entry[3]` are dead weight (Pitfall 4).
- `typsphinx/__init__.py` (current, full file read this session) — the exact registration line CONF-08
  changes.
- `tests/conftest.py` (full file read this session) — `temp_sphinx_app`'s conf.py content, confirming
  it omits `typst_documents` (Pitfall 2's premise).
- `tests/test_config.py`, `tests/test_builder_output_stem.py`, `tests/test_pdf_generation.py`,
  `tests/test_extension.py` (read this session) — confirming which existing tests are/aren't affected
  by the default change (SC#5's discretion item (b)).
- `tests/test_corpus_gate.py`, `tests/test_missing_and_malformed_master_gate.py` (read this session) —
  the established gate-test patterns this phase's new tests should follow, and identification of the
  "full-corpus `-b typstpdf` gate" as `TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error`.
- `tox.ini`, `pyproject.toml` `[tool.pytest.ini_options]`, `.github/workflows/ci.yml` (read this
  session) — confirming CI runs plain `pytest tests/` with no `-m "not slow"` filter, so the corpus
  gate IS part of the routine CI/full-suite run.
- `docs/source/user_guide/configuration.rst:26-44` (read this session) — the published 5-tuple contract
  wording, confirming D-02's shape matches the documented contract.
- `.planning/milestones/v0.7.0-phases/42-captioned-table-drops-preceding-target-label/42-GATE-EVIDENCE-05.md`
  (read this session) — the two-build worktree-isolation method template for SC#4's evidence file.

### Secondary (MEDIUM confidence)

None used — every claim in this document traces to a direct source read or to `44-CONTEXT.md`'s own
already-measured findings (which this research treats as given per the research brief).

### Tertiary (LOW confidence)

None.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — zero new dependencies; both symbols used were read directly from the installed
  package this session.
- Architecture: HIGH — the callable-default mechanism, the crash-site call chain, and the four config
  read-sites were all verified by reading the current source, not recalled from training data.
- Pitfalls: HIGH — the `temp_sphinx_app` blast-radius audit (Pitfall 2) was a real grep across all nine
  affected test files this session, not an assumption.

**Research date:** 2026-08-04
**Valid until:** 30 days (stable domain — Sphinx's `Config` callable-default protocol and
`make_filename_from_project` are long-standing, low-churn internals; re-verify if `sphinx` is bumped
past `<10` before this phase executes).
