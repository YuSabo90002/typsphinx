# Phase 8: API & Test Compatibility (Sphinx 9 / docutils 0.22) - Research

**Researched:** 2026-07-11
**Domain:** docutils/Sphinx soft-deprecation modernization + pytest deprecation-guard hardening
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01: Thorough audit — modernize ALL soft-deprecated docutils/Sphinx API, not just the one known
  `traverse()`.** The user explicitly chose the exhaustive stance over "fix only what breaks" and
  "light grep". Proactively find and replace every soft-deprecated docutils/Sphinx call the
  extension uses (e.g. `traverse()`→`findall()` everywhere, deprecated `nodes`/`addnodes` attribute
  access, deprecated logging/util API, deprecated builder/translator hooks).
- **D-02: Install a PERMANENT deprecation guard.** Add `filterwarnings = error::DeprecationWarning`
  (scoped appropriately) to `pyproject.toml` `[tool.pytest.ini_options]` so any future
  `DeprecationWarning` fails the suite. Third-party escape hatch: deprecation warnings from
  dependencies (Sphinx, docutils, typst-py, pytest plugins) that typsphinx cannot fix must be
  excluded via targeted `ignore::DeprecationWarning:<module>` entries — not by weakening the global
  `error` default. Interaction with D-01: the failure list from enabling the guard IS the D-01
  work-list; land the sweep first (or same wave) so the guard leaves the suite green.
- **API-01 is mechanical & locked:** replace the deprecated `doctree.traverse(addnodes.toctree)` at
  `typsphinx/template_engine.py:239` with `doctree.findall(...)` (consistent with
  `builder.py:151`'s existing `findall` usage). No `traverse()` deprecation warning may remain.
- **Latest-only forward-port:** raise-forward to Sphinx 9.1 / docutils 0.22; no Sphinx-8/docutils-0.21
  compatibility range or version-conditional branching.
- **Branch strategy:** all work stays on `release/v0.5.0`; `main` stays green throughout; merge to
  main only at milestone completion via GitHub PR.
- **Done-ness gate = full suite green + clean tree.** SC3 (~400 tests incl. PDF integration pass) +
  SC4 (`black`/`ruff`/`mypy` clean) are the blocking gates.
- **NOT this phase:** CI-matrix green observation + `typst compile` smoke test + drift/Dependabot
  ceiling bumps (Phase 9); `__version__`→0.5.0 fix + PyPI release (Phase 10); the admonition
  rendering bug (deferred, Phase 8.1).

### Claude's Discretion

- **Test-failure fix bias (default locked here):** When a test goes red on the new stack, prefer
  fixing the source to preserve the existing `.typ` output over rewriting test expectations —
  UNLESS the red is caused by a genuine, intended docutils/Sphinx output/structure change (e.g. the
  docutils 0.22 definition-list node shape), in which case adapt the translator to the new node
  shape and update the fixture to the new *correct* output. Document any fixture change with a
  one-line why.
- **docutils 0.22 multi-`<term>` definition-list edge case:** implementation-level; planner/
  researcher handle it. Verify against the resolved docutils 0.22 and fix if the node shape changed.
- **Sweep mechanics / grep patterns / findall signature:** planner decides how to enumerate
  deprecated calls and the exact `findall` replacement form.

### Deferred Ideas (OUT OF SCOPE)

- **Admonition rendering bug** (`translator.py::_visit_admonition` markup/code-mode mismatch,
  `.. note::` renders literal `par({text(...)})` instead of typeset prose) — explicitly NOT in Phase
  8. Routed to a dedicated follow-up phase (Phase 8.1, already inserted per STATE.md Roadmap
  Evolution). Not a Sphinx-9/docutils-0.22 API break.
- CFG-01 (user-configurable `@preview` versions) and XOS-01 (cross-OS docs-PDF CI) — not in this
  milestone.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| API-01 | The deprecated `doctree.traverse()` call at `template_engine.py:239` is replaced with `doctree.findall()` (consistent with `builder.py`) | Confirmed exact call site, confirmed `builder.py:151` reference pattern, empirically verified the swap resolves 21/28 of the guard's failures with zero behavior change (monkeypatch-tested end-to-end build). See "Code Examples" and "Common Pitfalls". |
| API-02 | The translator / writer / builder / config registration are confirmed compatible with Sphinx 9.1 + docutils 0.22 (any deprecation-removal breakage fixed), and the full pytest suite passes | Ran the full 402-test suite and a live `Sphinx()` app + full `typst` build against the resolved 9.1.0/0.22.4/0.15.0 stack under `-W error::DeprecationWarning -W error::PendingDeprecationWarning`. Found and enumerated the exact, complete 5-site work-list (see "Standard Stack" is N/A here — see "Common Pitfalls" and "Validation Architecture" §Phase Requirements → Test Map). No `AttributeError`/`TypeError` surfaced anywhere. |
</phase_requirements>

## Summary

The resolved environment is confirmed **Sphinx 9.1.0 + docutils 0.22.4 + typst 0.15.0** (verified via
`uv pip show` and `uv.lock`, not assumed from training data). Against this exact stack, I ran the
translator/writer/builder/config-registration pipeline end-to-end (a live `Sphinx()` app + a full
`typst`-builder build of a fixture project exercising headings, toctree, a definition list, an
admonition, and a code block) and the **full 402-test pytest suite**, both under
`-W error::DeprecationWarning -W error::PendingDeprecationWarning` to force every soft-deprecation to
surface as a hard failure. Zero `AttributeError`/`TypeError`/removed-API breakage occurred anywhere —
this confirms CONTEXT.md's own changelog-audit finding empirically, closing the "Blockers/Concerns"
landmine in STATE.md. The only failures were deprecation warnings, and I traced every single one to
its exact source line. There are exactly **5 fix sites**, all inside typsphinx's own source/tests —
**zero third-party (Sphinx/docutils/typst-py/pytest-plugin) deprecation warnings were observed**, so
D-02's "third-party escape hatch" ignore-list is very likely empty for this stack (see Open Questions
for the one caveat: subprocess-isolated integration tests were not exercisable in this research
sandbox — see "Environment Availability").

One fix (`template_engine.py:239`, API-01) is source code; it alone resolves 21 of the 28
guard-triggered failures (all `test_config_template_mapping.py`/`test_config_toctree_defaults.py`/
`test_template_assets.py`/`test_template_engine.py` failures reach `traverse()` indirectly through
`TemplateEngine.render()` → `extract_toctree_options()`). The remaining 7 are in **test files**, not
`typsphinx/` source: 3× `docutils.frontend.OptionParser(...).get_default_values()` in
`test_translator.py` (deprecated in favor of `frontend.get_default_settings(...)`), 2× `builder.app`
property access in `test_builder.py`/`test_pdf_generation.py` (Sphinx 9 deprecated all public `.app`
attributes, `RemovedInSphinx11Warning`, tracked upstream as sphinx-doc/sphinx#13627), and 2×
`publish_string(..., writer_name="html")` in `test_documentation_configuration.py`/
`test_documentation_usage.py` (docutils 0.22 deprecated the `writer_name`/`reader_name`/`parser_name`
string arguments in favor of `writer`/`reader`/`parser` instance arguments). All 5 sites, their exact
line numbers, and their exact modern replacement forms are documented below and were independently
re-verified by re-running the guard after applying each fix (via monkeypatch/dry-run, not by editing
the working tree, since this is a research pass).

I also resolved CONTEXT.md's open "docutils 0.22 multi-`<term>` definition-list edge case" concern
definitively: the docutils 0.22 **document-tree DTD** was indeed changed to permit multiple `<term>`
children per `definition_list_item` (`"Allow multiple <term> elements... third-party writers may
need adaption"`, Docutils 0.22rc1 release notes) — CONTEXT.md's concern was well-founded at the
schema level. However, empirically **no reStructuredText syntax in the installed docutils 0.22.4
`rst` parser currently produces this shape**: I tested both the classifier syntax (`term : classifier`,
produces 1 `<term>` + N `<classifier>` siblings, unchanged from prior docutils) and stacked
consecutive term lines (produces a parse `ERROR`, not a multi-term node — the concrete rST syntax for
this DTD feature is still an open docutils ticket, patches#95, not yet implemented in the parser).
**Net effect: `visit_term`/`depart_term`'s single-term buffer is not exercised by any construct the
installed rST parser can produce, so it does not cause today's SC2/SC3 breakage** — but it is now a
confirmed, documented latent risk (the schema allows it; the parser doesn't emit it *yet*). See
"Common Pitfalls" for the recommended low-cost defensive hardening.

**Primary recommendation:** Fix the 5 concrete deprecation-warning sites (1 source file, 4 test
files) exactly as enumerated below, add `filterwarnings = ["error::DeprecationWarning",
"error::PendingDeprecationWarning"]` to `pyproject.toml` (see "Open Questions" — the literal CONTEXT.md
text only names `DeprecationWarning`; escalating `PendingDeprecationWarning` too is required to
actually catch Sphinx's own `RemovedInSphinxNNWarning` family, which subclasses
`PendingDeprecationWarning`, not `DeprecationWarning`), and (optionally, low-risk, D-01-aligned)
harden `visit_term`/`depart_term` to append rather than overwrite. No other source-code changes are
needed for API-02.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| doctree→Typst translation (node visiting) | Translator (`translator.py`) | — | `TypstTranslator` owns all `visit_*`/`depart_*` node handling; the definition-list multi-term concern lives here. |
| toctree option extraction / template param mapping | Template Engine (`template_engine.py`) | — | `TemplateEngine.extract_toctree_options()` walks the doctree for `addnodes.toctree`; this is the API-01 `traverse()`→`findall()` site. |
| Sphinx build-loop orchestration (write_doc, image collection, PDF compile trigger) | Builder (`builder.py`) | Translator/TemplateEngine (consumes their output) | `TypstBuilder`/`TypstPDFBuilder` drive the per-doc write loop and own the reference `findall()` usage (`builder.py:151`) that API-01 must mirror. |
| Extension/config registration | `__init__.py` (`setup()`) | — | Registers builders + all `typst_*` config values; verified clean against Sphinx 9.1 with zero deprecation warnings (empirically re-created a live `Sphinx()` app). |
| Deprecation-guard enforcement | pytest config (`pyproject.toml`) | Test suite (`tests/*.py`) | `filterwarnings` is declared once in `pyproject.toml` but enforced across every test file; 4 of the 5 fix sites are in test files, not the extension's runtime source. |
| PDF compilation | `pdf.py` (`typst-py` wrapper) | Builder | Not implicated — no deprecated API found in `pdf.py`; `typst==0.15.0` compile path is orthogonal to the docutils/Sphinx sweep (Phase 7's domain). |

## Standard Stack

### Core (already pinned — this phase does not change dependency versions)

| Library | Resolved Version | Purpose | Verification |
|---------|-------------------|---------|---------------|
| `sphinx` | `9.1.0` | Host framework; builder/translator/config registration API | `[VERIFIED: uv pip show / uv.lock, this repo's environment]` |
| `docutils` | `0.22.4` | Doctree model, rST parser, `nodes`/`frontend`/`core` API | `[VERIFIED: uv pip show / uv.lock, this repo's environment]` |
| `typst` | `0.15.0` | PDF compilation backend (unaffected by this phase's scope) | `[VERIFIED: uv pip show / uv.lock, this repo's environment]` |
| `types-docutils` | `0.22.3.20260518` | mypy stubs, matches resolved docutils 0.22.4 | `[VERIFIED: uv pip show, this repo's environment]` — mypy already runs clean, no stub gap. |
| `pytest` | `9.1.1` | Test runner; `filterwarnings` guard target | `[VERIFIED: uv pip show, this repo's environment]` |

No new packages are needed for this phase — API-01/API-02 are pure modernization of existing calls,
not new dependencies. **Package Legitimacy Audit is not applicable** (no new external packages
installed this phase).

## Architecture Patterns

### System Architecture Diagram

```
   .rst source                    Sphinx 9.1 core
        │                          (App, Environment,
        ▼                           doctree cache)
  ┌─────────────┐   env.get_doctree()  ┌──────────────────┐
  │  docutils    │ ───────────────────▶│  TypstBuilder /   │
  │  0.22 parser │                     │  TypstPDFBuilder  │
  │  → doctree   │                     │  (builder.py)     │
  └─────────────┘                     └─────────┬──────────┘
                                                 │ write_doc(docname, doctree)
                                                 ▼
                                     ┌───────────────────────┐
                                     │   TypstWriter          │
                                     │   .translate()          │
                                     │   (writer.py)           │
                                     └──────────┬──────────────┘
                    doctree.findall(image)      │  runs translator over doctree
                    (builder.py:151, existing)  ▼
                                     ┌───────────────────────┐
                                     │  TypstTranslator        │
                                     │  ~140 visit_*/depart_*  │
                                     │  (translator.py)        │
                                     │  ← visit_term/depart_term│
                                     │    single-term-buffer   │
                                     │    (latent multi-term    │
                                     │    risk, not yet         │
                                     │    triggered)            │
                                     └──────────┬──────────────┘
                                                 │ body string
                     master doc? ───────────────┼──────────────── included doc?
                          │                                            │
                          ▼                                            ▼
              ┌────────────────────────┐                  ┌──────────────────────┐
              │  TemplateEngine.render() │                  │ minimal @preview      │
              │  (template_engine.py)    │                  │ imports only, no      │
              │  extract_toctree_options │                  │ template (writer.py)  │
              │  doctree.traverse(...)   │                  └──────────────────────┘
              │  ← API-01 FIX SITE:       │
              │    traverse()→findall()  │
              │    (line 239)             │
              └──────────┬───────────────┘
                          ▼
                    .typ file(s)
                          │
                          ▼ (typstpdf builder only)
                    typst 0.15 compile (pdf.py) → PDF
```

### Recommended Project Structure

No structural changes — this phase edits existing files in place:

```
typsphinx/
├── __init__.py          # verified clean — no changes needed
├── builder.py            # verified clean — reference findall() pattern, no changes needed
├── template_engine.py     # API-01 FIX: traverse() → findall() at line 239
├── translator.py          # optional hardening: visit_term/depart_term multi-term defense
├── writer.py               # verified clean — no changes needed
└── pdf.py                  # verified clean — no changes needed
tests/
├── test_translator.py      # FIX: OptionParser(...).get_default_values() → frontend.get_default_settings(...) (3 sites: ~1647, ~1725, ~1845)
├── test_builder.py          # FIX: builder.app → builder._app or refactor assertion (~line 64)
├── test_pdf_generation.py    # FIX: builder.app → builder._app or refactor assertion (~line 80)
├── test_documentation_configuration.py  # FIX: publish_string(writer_name=...) → publish_string(writer=...) (~line 104)
└── test_documentation_usage.py           # FIX: publish_string(writer_name=...) → publish_string(writer=...) (~line 101)
pyproject.toml              # D-02: add filterwarnings guard to [tool.pytest.ini_options]
```

### Pattern 1: `traverse()` → `findall()` (API-01, locked)

**What:** Replace the deprecated `Node.traverse()` iterator with `Node.findall()`, matching the
existing `builder.py:151` usage exactly.
**When to use:** Any doctree node-type search. This is the *only* `traverse()` call in `typsphinx/`.
**Verified fix (empirically tested via monkeypatch against the resolved stack — full build ran clean
under `-W error::DeprecationWarning -W error::PendingDeprecationWarning` afterward):**

```python
# typsphinx/template_engine.py:239 — BEFORE (deprecated):
toctree_nodes = list(doctree.traverse(addnodes.toctree))

# AFTER (matches builder.py:151's doctree.findall(image) pattern):
toctree_nodes = list(doctree.findall(addnodes.toctree))
```

`findall()` has the same signature and return semantics as `traverse()` (a generator over matching
nodes in document order) for this use case — the `list(...)` wrapper and downstream
`toctree_nodes[0]` indexing require no other changes. `[VERIFIED: empirical monkeypatch test against
sphinx==9.1.0/docutils==0.22.4, this repo's environment]`

### Pattern 2: `frontend.OptionParser` → `frontend.get_default_settings()`

**What:** docutils 0.22 deprecates `frontend.OptionParser`/`frontend.Option`/`frontend.Values`/
`frontend.store_multiple()`/`frontend.read_config_file()` ahead of an argparse-based rewrite in
docutils 2.0. `[CITED: docutils.sourceforge.io/0.22/RELEASE-NOTES.html]`
**When to use:** Anywhere test code needs default runtime settings for a parser/component to build a
`new_document(...)`.
**Fix (all 3 occurrences are in `tests/test_translator.py`, ~lines 1647, 1725, 1845):**

```python
# BEFORE (triggers DeprecationWarning: "will be replaced by a subclass of
# argparse.ArgumentParser in Docutils 2.0 or later. To get default settings,
# use frontend.get_default_settings()."):
from docutils.frontend import OptionParser
settings = OptionParser(components=(RstParser,)).get_default_values()

# AFTER — verified zero-warning under -W error::DeprecationWarning:
from docutils import frontend
settings = frontend.get_default_settings(RstParser)
```

`[VERIFIED: empirical test — python -W error::DeprecationWarning against installed docutils==0.22.4]`

### Pattern 3: `builder.app` → avoid the deprecated property

**What:** Sphinx 9 deprecated all remaining public `.app` attributes across the codebase —
`builder.app`, `env.app`, `events.app`, `SphinxTransform.app` — tracked upstream as
sphinx-doc/sphinx#13627, raising `RemovedInSphinx11Warning` (scheduled removal in Sphinx 11).
`[CITED: sphinx-doc.org changelog / GitHub issue #13627, cross-referenced via WebSearch]`
**Note:** `typsphinx/builder.py` itself never accesses `self.app` (`grep` confirms zero occurrences
in `typsphinx/*.py`) — both occurrences are test-only assertions comparing the builder's app
reference to the fixture's `app`/`temp_sphinx_app` object.
**Fix (`tests/test_builder.py:64`, `tests/test_pdf_generation.py:80`):**

```python
# BEFORE (triggers RemovedInSphinx11Warning, a PendingDeprecationWarning subclass):
assert builder.app == app

# AFTER — use the non-deprecated private attribute the property itself returns:
assert builder._app == app
```

`RemovedInSphinx11Warning` subclasses `PendingDeprecationWarning`, **not** `DeprecationWarning`
(`[VERIFIED: empirical class-hierarchy inspection, RemovedInSphinx11Warning.__mro__]`) — this matters
for the `filterwarnings` guard scoping, see "Open Questions".

### Pattern 4: `publish_string(writer_name=...)` → `publish_string(writer=...)`

**What:** docutils 0.22 deprecates the `reader_name`/`parser_name`/`writer_name` *string* arguments
of `core.Publisher.__init__()` and the `core.publish_*()` convenience functions in favor of
`reader`/`parser`/`writer` arguments that accept either a name string or a component instance.
`[CITED: docutils.sourceforge.io/0.22/RELEASE-NOTES.html, cross-referenced via WebSearch]`
**Fix (`tests/test_documentation_configuration.py:104`, `tests/test_documentation_usage.py:101`):**

```python
# BEFORE (triggers PendingDeprecationWarning: 'Argument "writer_name" will be
# removed in Docutils 2.0. Specify writer name in the "writer" argument.'):
publish_string(source=content, writer_name="html", settings_overrides={"report_level": 2})

# AFTER — verified zero-warning under -W error::PendingDeprecationWarning:
from docutils.writers import get_writer_class
publish_string(
    source=content,
    writer=get_writer_class("html")(),
    settings_overrides={"report_level": 2},
)
```

`[VERIFIED: empirical test — python -W error::PendingDeprecationWarning against installed
docutils==0.22.4]`

### Anti-Patterns to Avoid

- **Do not weaken `filterwarnings` to a blanket `ignore` or `default` to make the suite green.**
  D-02 explicitly forbids this; every warning found in this research has a concrete, minimal fix.
- **Do not "modernize" `typing.Dict`/`typing.List`** in `template_engine.py`/`__init__.py`/
  `translator.py` even though the sweep touches those files — `UP006`/`UP035` stay ruff-ignored per
  CLAUDE.md, and this is explicitly out of scope per CONTEXT.md's "Sweep mechanics" note.
- **Do not treat the `-U`-flag `.venv/bin/uv`/`.venv/bin/ruff` NixOS binary-launch failures as
  Sphinx-9/docutils-0.22 regressions.** See "Environment Availability" — these are pre-existing
  environment artifacts unrelated to API-01/API-02.
- **Do not expand into the admonition rendering bug** even though it will be visible in any manual
  `docs-pdf` glance during this phase's verification — it is explicitly Phase 8.1's scope.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|--------------|-----|
| Default docutils runtime settings for a test-only parse | A hand-rolled `Values` object or reimplementing `OptionParser` defaults | `docutils.frontend.get_default_settings(*components)` | It's docutils' own blessed replacement, already installed, already covers the exact same defaults `OptionParser(...).get_default_values()` produced. |
| Deprecation-warning enforcement | A custom warnings-capturing pytest fixture/hook | pytest's built-in `filterwarnings` ini option | pytest has first-class, well-documented `error::`/`ignore::<category>:<module>` syntax; no custom infra needed — this is exactly what D-02 asks for. |

**Key insight:** every fix in this phase is a 1-2 line substitution using an API the dependency
itself already exposes as the documented replacement — there is no design work here, only faithful
mechanical substitution per D-01's "modernize, don't redesign" framing.

## Common Pitfalls

### Pitfall 1: Fixing only `template_engine.py:239` leaves the D-02 guard red

**What goes wrong:** If the guard (`filterwarnings = error::DeprecationWarning`) is added before the
4 test-file fixes land, 7 of the 28 originally-observed failures remain (`test_translator.py` ×3
under plain `DeprecationWarning`; `test_builder.py`/`test_pdf_generation.py`/
`test_documentation_configuration.py`/`test_documentation_usage.py` ×4 only surface if
`PendingDeprecationWarning` is also escalated — see Pitfall 2).
**Why it happens:** API-01 is the only *locked* requirement; D-01's "thorough sweep" language is easy
to under-scope to "just template_engine.py" if the sweep is done by changelog-reading alone instead
of actually running the suite under the guard.
**How to avoid:** Land all 5 fix sites (1 source + 4 test) in the same wave as the guard, exactly as
enumerated in "Architecture Patterns" above — this list is empirically complete (verified by running
the guard both before and after the equivalent fixes).
**Warning signs:** `pytest -W error::DeprecationWarning -W error::PendingDeprecationWarning` still
shows `FAILED` entries after applying only the `template_engine.py` change.

### Pitfall 2: `error::DeprecationWarning` alone does not catch Sphinx's own deprecations

**What goes wrong:** Sphinx's `RemovedInSphinxNNWarning` family (the mechanism behind the `builder.app`
warning) subclasses `PendingDeprecationWarning`, not `DeprecationWarning`
(`RemovedInSphinx11Warning.__mro__` confirmed empirically). A guard written literally as
`filterwarnings = ["error::DeprecationWarning"]` (the literal text in CONTEXT.md D-02) will silently
let future Sphinx-specific deprecations through — defeating D-02's stated purpose ("prevents silent
re-accumulation of deprecated API").
**Why it happens:** Sphinx deliberately uses `PendingDeprecationWarning` as the base so that
deprecations don't immediately break user code under Python's default warning filters (which hide
`PendingDeprecationWarning` by default but not `DeprecationWarning` raised from `__main__`).
**How to avoid:** Escalate both classes: `filterwarnings = ["error::DeprecationWarning",
"error::PendingDeprecationWarning"]`. This is a deviation-with-rationale from CONTEXT.md's literal
wording, not from its intent — flagged explicitly in "Open Questions" for the planner/user to confirm.
**Warning signs:** A future Sphinx 10 deprecation warning appears in CI output as a warning, not a
test failure.

### Pitfall 3: Attributing NixOS subprocess-launch failures to API-02

**What goes wrong:** In this research environment, 45 of 402 tests fail with `Could not start
dynamically linked executable: uv` / the same for a directly-invoked `.venv/bin/ruff`. All 45 use the
pattern `subprocess.run(["uv", "run", "sphinx-build", ...])` (integration/example tests). This is
**not** a Sphinx 9/docutils 0.22 regression.
**Why it happens:** `tox-uv` pulls in the PyPI `uv` wheel (a generic-manylinux compiled binary) as a
transitive dependency, installed into `.venv/bin/uv`. `uv run <anything>` prepends `.venv/bin` to
`PATH`, so any subprocess call to bare `uv` inside a test resolves to this non-NixOS-compatible binary
instead of the system/flake-provided `uv` (confirmed via `file .venv/bin/uv` → generic ELF requiring
`/lib64/ld-linux-x86-64.so.2`, which doesn't exist on NixOS without `nix-ld`). The same root cause
breaks a directly-invoked `.venv/bin/ruff` (also a compiled wheel) — `ruff check .` only succeeds via
`nix-shell -p ruff --run "ruff check ."`, bypassing the venv copy entirely. `black`/`mypy` are
unaffected (pure-Python/py-interpreter-hosted, so the venv's own patched Python runs them fine).
**How to avoid:** This is a pre-existing artifact of running in this sandboxed NixOS tool-execution
context, not something Phase 8 introduces or must fix — STATE.md records the full 402-test suite as
already green as of Phase 7, meaning the user's normal (non-sandboxed) interactive shell does not hit
this (likely has `nix-ld` configured system-wide, unlike this tool sandbox). **Do not attempt to "fix"
this as part of API-01/API-02** — it is orthogonal. If the phase executor hits the same 45 failures,
treat it as an environment note to surface to the user, not a code regression, and verify pass/fail
status for the other 357 tests + the 1 source-level `traverse()` fix independently of these 45.
**Warning signs:** Failure messages containing `"Could not start dynamically linked executable"` or
`"NixOS cannot run dynamically linked executables"`.

### Pitfall 4: Conflating the docutils 0.22 DTD change with an actual parser-level regression

**What goes wrong:** Assuming the docutils 0.22 "allow multiple `<term>` elements" DTD change (real,
cited) means the installed rST parser now actually emits multi-term `definition_list_item` nodes from
ordinary `.rst` input, and therefore `visit_term`/`depart_term` is actively dropping terms today.
**Why it happens:** The DTD/schema and the parser are two different layers; docutils 0.22's release
notes describe a document-tree capability change, and a search-engine summary can blur this together
with "this now happens when you write reST."
**How to avoid:** Empirically verified (`docutils.parsers.rst.Parser`, docutils 0.22.4, both the
classifier syntax and stacked-consecutive-term-lines syntax): the classifier syntax still produces
exactly 1 `<term>` + N `<classifier>` siblings (unchanged); stacked term lines produce a parse
`ERROR`, not a multi-term node. The concrete rST syntax for the new DTD capability is still an open
docutils ticket (patches#95) — not implemented in the installed parser version. **No fixture or test
currently exercises a multi-term doctree**, and none can be constructed from standard `.rst` input on
this stack, so this does not block SC2/SC3 today. Recommended defensive hardening (optional, low
cost, aligned with D-01's "reduce future forward-port debt" framing) — change the single-value
overwrite to an append-then-join so a future parser version (or a hand-built doctree from another
input format) degrades gracefully instead of silently dropping terms:

```python
# translator.py — current (translator.py:1047-1122), simplified:
# visit_term: self.current_term_buffer = []  (buffer)
# depart_term: self.current_term_buffer = term_content   # OVERWRITES if called twice

# Recommended defensive shape (only matters if/when the parser emits >1 <term>):
def visit_definition_list_item(self, node):
    self._term_strings = []   # new: accumulate across possibly-multiple <term> siblings
    ...

def depart_term(self, node):
    term_content = "".join(self.current_term_buffer).strip()
    self._term_strings.append(term_content)   # APPEND, don't overwrite
    ...

def depart_definition(self, node):
    ...
    joined_term = ", ".join(self._term_strings)  # or another Typst-appropriate join
    self.definition_list_items.append((joined_term, definition_content))
    self._term_strings = []
```

This is **Claude's Discretion per CONTEXT.md**, not a blocking fix — no test currently requires it.
Flag it to the planner as an optional low-risk hardening task, not a required one.
**Warning signs:** N/A today (nothing currently triggers it) — future-proofing only.

## Code Examples

See "Architecture Patterns" Patterns 1-4 above for all 5 verified fix sites with before/after code.

### Verifying the guard is complete (recommended verification command)

```bash
# Run with both warning classes escalated to confirm zero deprecation warnings remain
# (this exact invocation reproduced all 28 findings in this research):
uv run pytest -q -m "not slow" \
  -W "error::DeprecationWarning" -W "error::PendingDeprecationWarning" --tb=short
```

`[VERIFIED: this exact command was used to derive every fix site in this document, against
sphinx==9.1.0/docutils==0.22.4/pytest==9.1.1, this repo's environment]`

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|---------------|--------|
| `doctree.traverse(NodeClass)` | `doctree.findall(NodeClass)` | docutils (long-deprecated, now hard-erroring under strict warning filters in this stack) | Same generator semantics; drop-in replacement. |
| `OptionParser(components=...).get_default_values()` | `frontend.get_default_settings(*components)` | docutils 0.22 (`frontend.OptionParser` etc. deprecated ahead of argparse rewrite in docutils 2.0) | Same `Values` object shape returned; drop-in for this use case. |
| `builder.app` / `env.app` / `events.app` / `SphinxTransform.app` | Access the object you already have in scope (e.g. the `app` fixture) instead of round-tripping through the builder | Sphinx 9 (sphinx-doc/sphinx#13627), `RemovedInSphinx11Warning` | Public `.app` surface fully deprecated across Sphinx; typsphinx's own source never used it, so this is test-only. |
| `publish_string(..., writer_name="html")` | `publish_string(..., writer=get_writer_class("html")())` | docutils 0.22 (component *_name string args deprecated, removal targeted for docutils 2.0) | Requires importing `get_writer_class`; otherwise identical output. |

**Deprecated/outdated:**
- `docutils.frontend.OptionParser`/`Option`/`Values`/`store_multiple()`/`read_config_file()`: being
  replaced by an `argparse.ArgumentParser` subclass in docutils 2.0; not yet removed in 0.22.4, but
  emits `DeprecationWarning` on use.
- Sphinx `Builder.app`/`BuildEnvironment.app`/`EventManager.app`/`SphinxTransform.app`: all four
  scheduled for removal in Sphinx 11; typsphinx source does not use any of them (test-only fix needed).

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|----------------|
| A1 | The `.venv/bin/uv`/`.venv/bin/ruff` NixOS binary-launch failures are a research-sandbox-specific artifact and do not reproduce in the actual Phase 8 execution/CI environment | Common Pitfalls #3 | If wrong, 45 of 402 tests would falsely appear to block SC3 during real execution too, requiring a PATH-ordering or `nix-ld` fix that is currently out of this phase's identified scope. Low risk: STATE.md already records these 402 tests green as of Phase 7 in the real execution environment; GitHub Actions CI runners are Ubuntu (not NixOS) and are unaffected regardless. |
| A2 | Escalating `PendingDeprecationWarning` (not just `DeprecationWarning`) in the `filterwarnings` guard is necessary to catch Sphinx's `RemovedInSphinxNNWarning` family and does not conflict with D-02's intent, even though it goes beyond D-02's literal wording | Open Questions / Pitfall 2 | If the user/planner prefers the literal `error::DeprecationWarning`-only text, the guard would not catch future Sphinx-specific deprecations (like `builder.app` would have gone undetected) — a scope decision, not a technical risk, since I verified both configurations empirically. |

**If this table is empty:** N/A — see the two entries above; both are HIGH-confidence findings with a
narrow, well-understood risk surface, not unverified guesses.

## Open Questions

1. **Should the `filterwarnings` guard escalate `PendingDeprecationWarning` in addition to
   `DeprecationWarning`?**
   - What we know: CONTEXT.md D-02 literally specifies `filterwarnings = error::DeprecationWarning`.
     Empirically, `RemovedInSphinx11Warning` (the `builder.app` warning) and docutils' `writer_name`
     warning are both `PendingDeprecationWarning` subclasses, not `DeprecationWarning`. An
     `error::DeprecationWarning`-only guard would leave those 4 sites' *future* regressions
     undetected (even though this research already found and will fix today's instances).
   - What's unclear: Whether the user intended `DeprecationWarning` literally (accepting that
     Sphinx-specific pending-deprecations pass through un-gated) or as shorthand for "any deprecation
     warning" (the D-02 prose says "any future `DeprecationWarning`" but also frames the goal as
     "prevents silent re-accumulation of deprecated API" broadly).
   - Recommendation: Add both `error::DeprecationWarning` and `error::PendingDeprecationWarning` to
     `filterwarnings`. This is the only configuration that empirically achieves D-02's stated goal
     against this specific dependency stack. Document the deviation from the literal locked text with
     a one-line comment in `pyproject.toml` citing this research finding.

2. **Should the `visit_term`/`depart_term` multi-term defensive hardening (Pitfall 4) be included in
   this phase or deferred?**
   - What we know: No current test or reST syntax triggers the bug; SC2/SC3 do not require it.
   - What's unclear: Whether "thorough audit... reducing future forward-port debt" (D-01's own
     framing) extends to this kind of forward-looking, currently-untriggered hardening, or whether it
     should stay strictly to *currently observable* deprecation warnings (which this item is not — it's
     a doctree-shape risk, not a deprecation warning).
   - Recommendation: Treat as optional/low-priority. Include only if the planner has spare wave
     capacity; do not let it block the SC3 gate. If included, add exactly one new regression test that
     directly constructs a multi-term `definition_list_item` doctree (bypassing the rST parser, since
     the parser cannot produce one) to prove the append-not-overwrite behavior, and note in the test
     docstring that this is forward-looking (docutils parser does not yet emit this shape).

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|--------------|-----------|---------|----------|
| Nix-provided `uv` (system/flake) | Running `uv sync`, `uv run pytest` at the top level | ✓ | 0.11.25/0.11.26 | — |
| `.venv/bin/uv` (pip-wheel, transitive via `tox-uv`) | Subprocess-based integration/example tests (`subprocess.run(["uv","run",...])`) | ✗ (this sandbox) | 0.11.26 (installed, but non-launchable — generic-manylinux ELF, NixOS lacks the FHS dynamic linker without `nix-ld`) | None found in this sandbox; `nix-shell -p nix-ld` alone was insufficient (needs system-level `programs.nix-ld.enable` + a real `/lib64/ld-linux-x86-64.so.2` symlink, both out of reach from a sandboxed tool call) |
| `.venv/bin/ruff` (pip-wheel) | `ruff check .` when invoked directly (not via a Nix-provided `ruff`) | ✗ (this sandbox) | 0.15.20 (installed, non-launchable, same root cause) | `nix-shell -p ruff --run "ruff check ."` — confirmed working, "All checks passed!" |
| `black` (pip-wheel, pure-Python entrypoint) | `black --check .` | ✓ | (installed via `uv sync --extra dev`) | — (pure Python, unaffected by the ELF-launch issue) |
| `mypy` (pip-wheel) | `mypy typsphinx/` | ✓ | (installed via `uv sync --extra dev`) | — (Python-hosted; ran clean, "Success: no issues found in 6 source files") |

**Missing dependencies with no fallback:**
- None that block the *code-level* verification of API-01/API-02 (the `traverse()`→`findall()` fix
  and the 4 test-file fixes were all independently verified without needing the subprocess-based
  integration tests).

**Missing dependencies with fallback:**
- `ruff check .` — use `nix-shell -p ruff --run "ruff check ."` if the sandboxed `.venv/bin/ruff`
  fails to launch with the NixOS ELF error.
- Subprocess-based `uv run sphinx-build` integration tests (45 of 402) — no fallback found from
  within this sandbox; treat as environment noise per Common Pitfalls #3, and cross-check against the
  357 non-subprocess tests + the direct empirical build verification already performed in this
  research (both passed clean).

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 9.1.1 |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]` |
| Quick run command | `uv run pytest -q -m "not slow" -W "error::DeprecationWarning" -W "error::PendingDeprecationWarning"` (≈2s, 402 tests, no `-m slow` tests exist in this suite — `-m slow` selects 0) |
| Full suite command | `uv run pytest` (402 tests; includes the subprocess-based integration/example tests — see Environment Availability for the known sandbox caveat) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|---------------------|--------------|
| API-01 | `template_engine.py:239` uses `findall()`, no `traverse()` warning | unit + guard | `pytest tests/test_template_engine.py::TestToctreeOutlineIntegration -W error::DeprecationWarning -x` | ✅ (existing `test_template_engine.py`) |
| API-01 | No `traverse()` deprecation warning anywhere in the suite | guard (whole-suite) | `pytest -q -W error::DeprecationWarning -W error::PendingDeprecationWarning` (must show 0 failed from `traverse`) | ✅ (whole existing suite is the test) |
| API-02 | Translator/writer/builder/config registration run without `AttributeError`/`TypeError` against Sphinx 9.1/docutils 0.22 | integration (empirical, already reproduced in this research) | `python -m sphinx -b typst <fixture-src> <out>` under `-W error` flags | ✅ (existing `tests/fixtures/*`; also independently reproducible via the ad-hoc fixture used in this research) |
| API-02 | docutils 0.22 definition-list term/classifier handling unchanged for supported syntax | unit | `pytest tests/test_translator.py -k definition_list` | ✅ (existing `test_definition_list_conversion`, `test_definition_list_with_multiple_definitions`) |
| API-02 | Full pytest suite (~402 tests) passes, `filterwarnings` guard active | full suite | `pytest` (with the new `filterwarnings` ini option in place) | ✅ (existing suite; new: `pyproject.toml` `filterwarnings` entries) |
| API-02 | `black`/`ruff`/`mypy` clean after any reformatting | lint/type | `black --check .`, `ruff check .`, `mypy typsphinx/` | ✅ (all three already run clean against the pre-fix tree in this research — no reformatting expected from the 5 small fixes, but re-run is the verification step) |

### Sampling Rate

- **Per task commit:** `uv run pytest -q -m "not slow" -W "error::DeprecationWarning" -W "error::PendingDeprecationWarning" tests/<affected_file>.py` — fast, targeted, catches regressions in the specific fix site.
- **Per wave merge:** `uv run pytest -q -m "not slow"` plus `black --check . && mypy typsphinx/` (skip subprocess-based integration tests locally if the NixOS `uv`/`ruff` launch issue reproduces; run `ruff check .` via `nix-shell -p ruff --run "ruff check ."` as a fallback).
- **Phase gate:** Full `pytest` (all 402, including subprocess-based integration tests) green + `black --check .` + `ruff check .` + `mypy typsphinx/` all clean, before `/gsd-verify-work`. If the 45 subprocess-based tests fail with the exact NixOS launch error signature from Common Pitfalls #3, treat as a pre-existing environment issue to surface, not a phase blocker to silently ignore — the planner/executor should explicitly confirm this signature (not a Sphinx-9-shaped stack trace) before treating those 45 as non-blocking.

### Wave 0 Gaps

- None — existing test infrastructure (402 tests, `pyproject.toml` pytest config, `tox.ini` lint/type/docs envs) covers all Phase 8 requirements. The only new artifact is the `filterwarnings` ini-option addition to `pyproject.toml`, which is a config change, not a new test file.
- Optional (only if Open Question #2's hardening is adopted): one new unit test in `tests/test_translator.py` that hand-constructs a multi-term `definition_list_item` doctree node (bypassing the rST parser) to exercise the append-not-overwrite path.

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|----------------|---------|--------------------|
| V2 Authentication | No | This is a build-time Sphinx extension; no auth surface. |
| V3 Session Management | No | N/A — no sessions. |
| V4 Access Control | No | N/A — no access-control surface. |
| V5 Input Validation | Partial (pre-existing, unmodified by this phase) | `app.add_config_value(..., [type, ...])` type-list validation already in place in `__init__.py` for all `typst_*` config values; verified clean against Sphinx 9.1, no change needed. |
| V6 Cryptography | No | N/A — no cryptography in this extension. |
| V12 Files and Resources | Partial (pre-existing, unmodified by this phase) | Image/asset copying (`builder.py`, `_write_template_file`, template-asset copy) uses `path`/`ensuredir` from `sphinx.util.osutil`; this phase does not touch file-path handling and introduces no new file I/O. |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|-----------------------|
| Untrusted `.rst`/config content triggering arbitrary code via `eval`/`exec`-like constructs | Tampering | Not applicable — this phase makes no changes to how document content or config values are parsed/evaluated; `frontend.get_default_settings()` and `get_writer_class()` are both docutils' own trusted, non-eval-based APIs. |

This phase is a pure API-modernization change with no new input surface, no new file I/O, and no new
external package installs — the security domain is effectively unaffected. No new controls are
required.

## Sources

### Primary (HIGH confidence — empirical, verified in this repo's own environment)

- `uv pip show sphinx docutils typst types-docutils pytest` + `uv.lock` — resolved dependency versions.
- Live `Sphinx()` app construction + full `typst`-builder build of a fixture project (headings,
  toctree, definition list, admonition, code block) under `-W error::DeprecationWarning -W
  error::PendingDeprecationWarning` — zero `AttributeError`/`TypeError`, one `traverse()`
  `DeprecationWarning` (resolved via monkeypatch re-test).
- Full 402-test pytest suite run under the same strict-warning flags, twice (once with
  `error::DeprecationWarning` only → 24 failures; once adding `error::PendingDeprecationWarning` → 28
  failures) — every failure traced to its exact source line.
- Direct docutils parser tests (`docutils.parsers.rst.Parser`, docutils 0.22.4) for the classifier
  syntax and the stacked-consecutive-term-lines syntax, confirming the actual (non-)shape of
  `definition_list_item` doctrees this stack's parser produces.
- `black --check .`, `mypy typsphinx/`, and `ruff check .` (via `nix-shell -p ruff` workaround) — all
  clean against the current tree.

### Secondary (MEDIUM confidence — official docs, cross-referenced via WebSearch)

- [Docutils 0.22 Release Notes](https://docutils.sourceforge.io/0.22/RELEASE-NOTES.html) — confirms
  `frontend.OptionParser`/`Option`/`Values` deprecation ahead of docutils 2.0's argparse rewrite;
  confirms `reader_name`/`parser_name`/`writer_name` string-argument deprecation in favor of
  `reader`/`parser`/`writer`; confirms the definition_list_item DTD change ("Allow multiple `<term>`
  elements in a `<definition_list_item>` (third-party writers may need adaption)").
- Sphinx changelog / sphinx-doc/sphinx#13627 (via WebSearch) — confirms Sphinx 9's deprecation of all
  remaining public `.app` attributes (`builder.app`, `env.app`, `events.app`, `SphinxTransform.app`),
  raising `RemovedInSphinx11Warning`.
- SourceForge docutils feature-requests#60 (via WebSearch) — confirms the concrete rST syntax for
  multi-term definition lists is still an open ticket (patches#95), not yet implemented in the parser.

### Tertiary (LOW confidence)

- None used — every claim in this document is either empirically verified against this repo's exact
  resolved environment or cited from official docutils/Sphinx sources.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — versions read directly from `uv.lock`/`uv pip show`, not inferred.
- Architecture / fix-site enumeration: HIGH — every fix site was empirically triggered, isolated, and
  independently re-verified fixed (via monkeypatch/dry-run) against the exact resolved dependency
  stack, not inferred from changelogs alone.
- Multi-`<term>` edge case: HIGH — resolved definitively via a combination of official docs citation
  (DTD change confirmed) and direct parser-level empirical testing (confirmed not yet reachable via
  standard rST syntax on this docutils version).
- Pitfalls (NixOS subprocess launch issue): HIGH confidence that the *symptom* is an environment
  artifact (reproduced and root-caused precisely); MEDIUM confidence on whether it reproduces in the
  actual Phase 8 execution environment (see Assumption A1).

**Research date:** 2026-07-11
**Valid until:** 30 days (stable dependency stack already resolved/locked in `uv.lock`; re-verify if
`uv.lock` is regenerated against newer Sphinx/docutils patch releases before Phase 8 executes).
