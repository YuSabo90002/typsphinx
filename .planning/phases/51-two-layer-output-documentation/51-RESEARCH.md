# Phase 51: Two-Layer Output Documentation - Research

**Researched:** 2026-08-14
**Domain:** Documentation accuracy for a shipped behaviour change (no code changes in this phase)
**Confidence:** HIGH

## Summary

This is a measurement job, not a technology-selection job. Every claim published in this phase is a
claim about code that shipped in Phases 47-50. All findings below were measured this session against
the working tree at HEAD: the relevant `builder.py`/`writer.py`/`translator.py` functions were read in
full, five real `sphinx-build -b typst` runs were executed against scratch fixtures (bare target,
explicit-path target, and three refusal shapes: `..`, absolute, drive-qualified) plus the repository's
own `docs/source` tree and the existing three-master gate fixture, and a repo-wide grep swept
`docs/source/**`, `README.md`, and `examples/**/README.md` for every claim shape the phase description
named.

**Primary recommendation:** the planner can treat Part A's sweep table below as the closed, re-derived
falsified-claim list (superseding CONTEXT.md's "starting set, not the closed list") and Part B's
function-level model as the exact vocabulary the new `output_layout.rst` page must use. Part C's
measured file sets and warning text are ready to drop into the page's worked examples and the new
gate's fixtures verbatim. `:numref:` appears nowhere below, per D-07 — this research does not
re-import it.

**Environment note (measured this session):** `typst-py` *imports* successfully in this sandbox
(`import typst` succeeds, version 0.15.0) but a real `typst.compile()` call fails with
`FileNotFoundError: No such file or directory (os error 2)` — the underlying native binary cannot run
under NixOS's dynamic linker. This means `-b typst` (markup-only) builds work perfectly here (used for
all measurements below), `-b typstpdf` / `tox -e docs-pdf` do not, and D-12's "-b typst only, must never
skip" gate design is the only shape that runs reliably in this environment — confirming the CONTEXT.md
constraint rather than merely asserting it.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Two-layer wrapper/content explanation (new page) | Documentation (docs/source) | — | Pure prose; the code it describes is frozen |
| Target-as-path worked examples | Documentation (docs/source) | Test fixtures (tests/) | The gate (D-10/D-11/D-12) is the machine-checked half of the same claim |
| Migration guide ("what changed from v0.7.x") | Documentation (docs/source/changelog.rst) | — | Existing `Migration Guides` section owns this per D-02 |
| README correction | Documentation (README.md, PyPI front page) | — | D-03 scopes this to false-claim fixes only, no new explanation |
| Falsified-claim sweep fixes | Documentation (docs/source/**, README.md, examples/**/README.md) | — | D-04 repo-wide scope |
| SC#3 verification gate | Test infrastructure (tests/) | — | D-10/D-11/D-12; asserts `.typ` file sets against real builds, never `typst-py` |

This phase touches **zero** lines under `typsphinx/` — every row above is documentation or test
infrastructure. No behaviour-tier capability is being (re)assigned; this map exists only so the planner
does not accidentally scope a task to touch `typsphinx/builder.py` etc.

## Standard Stack

Not applicable — this phase adds no runtime dependency and no new library. The new SC#3 gate reuses
`pytest` (already a `dev` extra) and `sphinx.util.osutil.make_filename_from_project` (already imported
by `typsphinx/builder.py:19` and by the existing `tests/test_quickstart_docs_gate.py:30`). No
`## Package Legitimacy Audit` is required — no external package is installed by this phase.

## Part A — Repo-Wide Falsified-Claim Sweep (Re-Derived, D-04)

Scope searched: `docs/source/**`, `README.md`, `examples/**/README.md`. Excluded: `.planning/`,
`tests/`, `typsphinx/`. Search covered every claim shape the phase description named: `index.typ`
mentions, `typst compile …`/`cat …` commands naming a `.typ` file, "filename stem"/"basename" language,
"path component is not supported" language, one-file-per-entry counting claims, `#include()`
walkthroughs, and directory/build-output listings.

### CONTEXT.md's starting-set sites — confirmed / status

| CONTEXT.md site | Confirmed this session | Line drift |
|---|---|---|
| `docs/source/user_guide/configuration.rst:46-52` | Yes, still present, still false | none — exact lines |
| `docs/source/user_guide/builders.rst:114-121` | Yes, still present, still false | none |
| `docs/source/user_guide/builders.rst:61`, `:170` | Yes, both present | none |
| `docs/source/user_guide/templates.rst:458-462` | Present at `:453-462` (block starts 3 lines earlier than cited; the `cat` line itself is still at `:462`) | minor (block header, not the claim line) |
| `README.md:82-85`, `README.md:228` | Yes, both present, still false | none |
| `examples/advanced/README.md:60-64` | Confirmed at `:59-65` (one line wider than cited) | minor |

None of CONTEXT.md's named sites has already been fixed or moved substantially.

### Full sweep table (re-derived, all hits)

| # | Path:Line | Verbatim claim | Verdict | Why (code citation) |
|---|---|---|---|---|
| 1 | `docs/source/user_guide/builders.rst:39` | `- One file per document defined in ` + backtick + `typst_documents` + backtick | **FALSE** | Every `typst_documents` entry now produces TWO files (wrapper `_wrapper_output_relpath()` + content `_content_output_path()`, `typsphinx/builder.py:967-1010`), and every docname — not only ones in `typst_documents` — gets an unconditional content file (`builder.py:573-577`). |
| 2 | `docs/source/user_guide/builders.rst:61` | `typst compile build/typst/index.typ output.pdf` | **FALSE** | No `typst_documents` is set in this walkthrough's implicit context, so under the default derivation (`_default_typst_documents()`, `builder.py:169-188`) the wrapper is `<project>.typ` and `index.typ` is the CONTENT file. Compiling it directly succeeds but yields an empty `state` and zero children (D-08, measured Phase 49). |
| 3 | `docs/source/user_guide/builders.rst:108-121` | `` The second tuple element is the output filename stem, and it governs both the emitted ``.typ`` file and the compiled ``.pdf`` `` … `` the builders therefore emit ``main.typ`` / ``main.pdf`` and ``api-ref.typ`` / ``api-ref.pdf`` `` | **FALSE / INCOMPLETE** | Element 2 (`_resolve_target_stem()`, `builder.py:296-420`) governs only the WRAPPER's name. With this exact config the build ALSO writes `index.typ` and `api.typ` (docname-derived content files, unconditional) that this paragraph never mentions. |
| 4 | `docs/source/user_guide/builders.rst:156` | `open build/pdf/index.pdf` | **FALSE (pre-existing, orthogonal to the split)** | No `typst_documents` is set in this "Common Workflow → Development" walkthrough either; under the default derivation the PDF is named `<project>.pdf`, never `index.pdf`, since v0.7.1's CONF-08 (Phase 44). Not caused by the two-layer split — flagging for visibility since it fits the sweep's claim shapes, but the planner should decide whether DOC-14's mandate covers a pre-existing CONF-08-era staleness or only split-caused claims. |
| 5 | `docs/source/user_guide/builders.rst:170` | `typst compile build/typst/index.typ output.pdf` | **FALSE** | Same defect as #2 (this is the "Production → Option 2" walkthrough, no `typst_documents` set). |
| 6 | `docs/source/user_guide/configuration.rst:46-52` | `` A path component is not supported: a path-bearing value produces a build warning and the file is written under its basename next to the source document. `` | **FALSE** | OUT-01 (Phase 47) is a deliberate reversal: `_escapes_outdir()` (`builder.py:71-112`) only refuses `..`, absolute, and drive-qualified targets. A plain path-bearing target (e.g. `"manuals/guide.typ"`) is now accepted AS-IS relative to outdir (`_resolve_target_stem()`, `builder.py:325-334`). This is the exact claim `47-08-SUMMARY.md:212` and `47-SECURITY.md` R-47-01 handed forward to DOC-14. |
| 7 | `docs/source/user_guide/templates.rst:453-462` | `` 3. **Use typst builder**: Generate ``.typ`` files to inspect output `` … `` cat build/typst/index.typ `` under the heading "Check the generated template usage" | **FALSE** | Content files carry NO template application at all (`writer.py:222-224`, `TypstWriter.translate()`'s docstring: "template application now belongs exclusively to `render_wrapper()`"). Measured: `index.typ`'s first 15 lines contain only `@preview` imports + raw body, no `#show: project.with(...)`; that call lives in the wrapper (`manual.typ` / `<project>.typ`). |
| 8 | `docs/source/changelog.rst:184` (historical `0.2.0` "Old way (still works)" entry) | `typst compile build/typst/index.typ output.pdf` | **BORDERLINE / historical** | This is a `## [0.2.0]` release-note example labelled "Old way (still works)", not a current-usage instruction. The command still runs without error, but its semantic result silently changed (Phase 49: the compiled content-only file now includes zero children instead of the whole document it once was). Flagging for the planner's own scope call — a historical changelog entry describing 0.1.x-era behaviour is arguably out of DOC-14's "published documentation" mandate, but the literal command would now mislead anyone who runs it today. |
| 9 | `README.md:82-85` | `` Each entry is a tuple `(source, target, title, author, documentclass)`, and each entry produces one emitted `.typ` file and, under the `typstpdf` builder, one compiled `.pdf`. `` | **FALSE** | Named explicitly in CONTEXT.md D-04's starting set. Each entry now produces the WRAPPER `.typ` (+ `.pdf` under `typstpdf`) but its docname ALSO unconditionally gets a content `.typ` file — "one emitted `.typ` file" per entry is false; it is two, plus every non-entry docname gets one too. |
| 10 | `README.md:228` | `` `typst_documents`: Master documents to build, as `[(source, target, title, author, documentclass), ...]` — optional; when unset, typsphinx derives a single master from `root_doc`/`project`/`author` (target `<project>.typ`), and an explicit value always overrides that derived default `` | **STALE (companion to #9)** | Not independently false, but this summary bullet is the second occurrence of the same undocumented two-layer split — README's Quick Start prose (lines 80-103) needs the split explained once and this bullet kept consistent with it. Grouped with #9 in CONTEXT.md's starting set for the same fix pass. |
| 11 | `examples/basic/README.md:36` | `` This will create `_build/typst/basic-example.typ` with the Typst markup. `` | **FALSE (by omission)** | Measured: `examples/basic/conf.py:30-35` sets `typst_documents = [("index", "basic-example.typ", …)]`. The build ALSO creates `_build/typst/index.typ` (the content file, unmentioned), and "with the Typst markup" implies `basic-example.typ` is the whole document — it is now a thin wrapper (`#show: project.with(...)` + state publication + one `#include("index.typ")`). |
| 12 | `examples/advanced/README.md:59-65` | `` This will generate: - `_build/typst/advanced-example.typ` - Master document - `_build/typst/chapter1.typ` - Chapter 1 - `_build/typst/chapter2.typ` - Chapter 2. The master document (`advanced-example.typ`) uses `#include()` directives to combine all chapters into a single document structure. `` | **FALSE** | Already named in CONTEXT.md D-04. Measured: the actual set (docname `index`, target `advanced-example.typ`) is `advanced-example.typ` (wrapper), `index.typ` (content — missing from this list entirely), `chapter1.typ`, `chapter2.typ`. The `#include()` calls for `chapter1`/`chapter2` live in `index.typ` (state-guarded, `translator.py:5309-5340`), not in `advanced-example.typ`, which contains exactly one `#include("index.typ")` (`writer.py:262-319`). |
| 13 | `examples/advanced/README.md:113-125` | Code block: `` { #set heading(offset: 1) #include("chapter1.typ") } `` (and the same for `chapter2.typ`) | **FALSE, twice over** | (a) Split-caused: the real emission is a per-child STATIC compile-time guard, `` if "index#0>chapter1" in state("typsphinx:include-edges", ()).get() { include("chapter1.typ") } `` (verbatim shape, `translator.py:338-377`, `INCLUDE_STATE_KEY = "typsphinx:include-edges"` at `translator.py:192`), not an unconditional `#include()`. (b) Pre-existing (v0.7.1 Phase 44.1, unrelated to Phase 51 but in the same block being rewritten): the offset line is `` context { set heading(offset: heading.offset + 1) } `` (a relative increment, `translator.py:5303-5310`), not the absolute `` #set heading(offset: 1) `` shown. |

### Sites checked and found STILL TRUE (no fix needed — listed so the sweep is auditable)

| Path:Line | Claim | Why it survives |
|---|---|---|
| `docs/source/quickstart.rst:74-77,92-105` | `Find your PDF in build/pdf/myproject.pdf` … `typst_documents = [("index", "myproject", …)]` | Only the WRAPPER is ever compiled to PDF — the two-layer split changes the `.typ` file SET but not which file becomes the `.pdf` (measured: `bare` scratch build wrote only `manual.typ`→`manual.pdf`-equivalent target set, never `index.pdf`). This example's bare target ("myproject") is itself a valid worked-example shape. |
| `examples/basic/README.md:57` | `typst compile _build/typst/basic-example.typ output.pdf` | `basic-example.typ` IS the wrapper (target from `examples/basic/conf.py:30-35`) — this is the CORRECT file to compile; the instruction survives even though line 36 (just above it) needs fixing. |
| `examples/charged-ieee/README.md:107,116` | `typst compile paper.typ output.pdf` | `examples/charged-ieee/{approach1,approach2}/conf.py` set `typst_documents = [("index", "paper", …)]`; `paper.typ` is the wrapper. Correct as written. |
| `README.md:100-103` | `` A document reached only through a toctree is not a separate PDF — it is emitted as its own `.typ` file and pulled into its master through Typst's `#include()`. `` | Still true in outcome (a toctree child gets its own content file and is transitively included), though it does not explain the wrapper/content mechanics. D-03 explicitly scopes README to false-claim correction only, not a full explanation, so no fix is mandated here — note for the planner in case a tighter read is wanted. |
| `docs/source/user_guide/index.rst`, `docs/source/user_guide/builders.rst:98-101` general prose | (no specific filename claims) | Not evaluated as false; generic. |

**Total actionable falsified/stale claims: 13** (items 1-13 above), of which item 4 is flagged as
possibly out-of-scope (pre-existing CONF-08 staleness) and item 8 is flagged as borderline (historical
record). 11 are unambiguous split-caused falsifications the plan must fix.

## Part B — Measured Behaviour Contract

All of the following were read from `typsphinx/builder.py`/`writer.py`/`translator.py` at HEAD this
session (not inferred from CONTEXT.md's summary — CONTEXT.md's summary is a **correct** compression of
all of it; no divergence was found).

### `_resolve_target_stem(docname, target)` — `builder.py:296-420`

Decision tree, in order:

1. **Non-`str` target** → `stem = ""`, falls through to step 5's degenerate-target branch.
2. **`.typ` suffix stripping** — literal trailing `".typ"` only (`stem = target[:-4] if target.endswith(".typ") else target`); a stem containing an embedded period (`"v1.2-manual"`) is untouched.
3. **Backslash normalization** — `stem = stem.replace("\\", "/")`, unconditional, before the escape check.
4. **OUT-02 escape guard** (`_escapes_outdir(stem)` — true if `..` is a path segment, or `posixpath.isabs(stem)`, or `_is_drive_qualified(stem)`):
   - If escaping: `fallback = posixpath.basename(fallback_source)` (drive prefix stripped first if drive-qualified). If that fallback is itself empty/whitespace (e.g. trailing separator, bare root, bare drive prefix), emits the **degenerate-target warning** and returns `docname`. Otherwise emits the **path-rejected warning** and continues with `stem = fallback`.
   - Else if `"/" in stem` and `posixpath.basename(stem)` is empty (a non-escaping path ending in a separator, e.g. `"sub/manual.typ/"`): emits the degenerate-target warning and returns `docname` directly.
5. **Final degenerate check** — if target was non-`str` OR `stem.strip()` is empty: emits the degenerate-target warning and returns `docname`.
6. **No Unicode normalization/case folding** on the surviving stem — a non-ASCII stem such as `"マニュアル"` survives byte-for-byte.

**Verbatim warning strings (must be quoted, not paraphrased, in the new page):**

- Path-rejected (measured live, scratch build stderr, all three refusal shapes):
  ```
  a path is not supported in a typst_documents target name: '../escape' -- using 'escape' instead
  a path is not supported in a typst_documents target name: '/abs/manual' -- using 'manual' instead
  a path is not supported in a typst_documents target name: 'C:manual' -- using 'manual' instead
  ```
  (source template, `builder.py:383-386`: `f"a path is not supported in a typst_documents target name: {target!r} -- using {fallback!r} instead"`)
- Degenerate-target / empty-after-guard (`builder.py:377-381` and `:398-401` and `:411-414`, three call sites, same message shape): `f"empty typst_documents target name for docname {docname!r} -- falling back to {docname!r}"` (the escaping-fallback-is-itself-empty variant adds `" after removing an unsupported path"` before `"-- falling back to"`).

### `_is_drive_qualified(stem)` / `_escapes_outdir(stem)` — `builder.py:36-112`

- `_is_drive_qualified`: `len(stem) >= 2 and stem[0].isalpha() and stem[1] == ":"` — a pure string-shape test, platform-independent (a Windows-shaped target is refused identically on POSIX CI).
- `_escapes_outdir`: `".." in segments or posixpath.isabs(stem) or _is_drive_qualified(stem)`, where `segments = stem.replace("\\", "/").split("/")`. Deliberately does **not** treat a bare separator as escaping — `"manuals/guide"` is legitimate; only `..`, absolute (`posixpath.isabs`, not `os.path.isabs`), or drive-qualified trips it.

### `_validate_output_path_collisions()` — `builder.py:502-613`

Runs exactly once per `write()` call, before `prepare_writing()` and before `_template.typ` is written,
so a collision leaves **zero** `.typ` files on disk. Builds one `dict` keyed by `_collision_key()`
(case-folded, separator-normalized, `posixpath.normpath()`-collapsed) from three claimant kinds, in this
order:

1. The reserved `_template.typ` infrastructure file.
2. Every docname in `self.env.found_docs`, mapped to its content path (`docname + ".typ"`) —
   unconditional, regardless of `typst_documents` membership.
3. Every `typst_documents` entry's wrapper path (`_wrapper_output_relpath(entry) + ".typ"`), resolved
   per-entry (so two entries naming the same docname with different targets never collide with each
   other).

An unusable entry (`_is_usable_typst_documents_entry()` fails) is skipped with a `logger.warning`, never
added to the collision map.

**Verbatim `ExtensionError` message shape** (`builder.py:607-613`):
```
typst: {N} output path collision(s): {relpath!r}: {existing} and {description} both resolve to the same output path {relpath!r}; …
```
joined with `"; "` for multiple failures. Example (D-05's canonical illustration): configuring
`typst_documents = [("index", "index.typ", …)]` collides the wrapper against `index`'s own content
file — this exact configuration built successfully in v0.7.x and now raises this error.

### `_content_output_path(docname)` / `_wrapper_output_relpath(entry)` — `builder.py:967-1010`

- `_content_output_path(docname) -> path.normpath(path.join(self.outdir, docname + ".typ"))` — a pure
  function of the docname alone; every docname gets exactly one, unconditionally.
- `_wrapper_output_relpath(entry) -> self._resolve_target_stem(entry[0], entry[1])` — resolves the
  entry's OWN target directly (no docname-based search), so `.typ` must be appended by the caller.

**Function-level model — given `(docname, target)`, what two paths land on disk:**

| docname | target | content path | wrapper path |
|---|---|---|---|
| `"index"` | `"manual"` | `index.typ` | `manual.typ` (outdir root) |
| `"guide/index"` | `"manuals/guide.typ"` | `guide/index.typ` | `manuals/guide.typ` |
| `"index"` | *(unset — default derivation)* | `index.typ` | `<make_filename_from_project(project)>.typ` |

### `_default_typst_documents(config)` — `builder.py:169-188`

Returns `[(config.root_doc, make_filename_from_project(config.project) + ".typ", config.project,
config.author, "typst")]`, only invoked when the user has NOT set `typst_documents` at all (an explicit
`[]` always wins). This is the v0.7.1 `index.typ` → `<project>.typ` rename PROJECT.md and D-02 require
staying visually distinct from the v0.8.0 wrapper/content rename — verified this session by building
this project's own `docs/source/conf.py:72-74` (`typst_documents = [("index", "typsphinx", project,
author, "typst")]`, an EXPLICIT bare target, not the derived-default path, but it demonstrates the same
target-resolution machinery): emitted `typsphinx.typ` (wrapper) + `index.typ` (content).

### The wrapper-report message — `builder.py:767-770` (confirmed at these exact lines)

```python
logger.info(
    f"typst: wrote {len(wrapper_relpaths)} wrapper file(s) -- "
    f"compile these: {', '.join(wrapper_relpaths)}"
)
```
Measured live output for the `explicit` scratch build: `typst: wrote 1 wrapper file(s) -- compile
these: manuals/guide.typ`. This is the "wrapper" vocabulary CONTEXT.md's Claude's Discretion section
says should stay — it is already user-visible and matches the planning vocabulary exactly.

### No divergence found

CONTEXT.md's summary of every one of the above functions matches the code read this session exactly —
no correction is owed to the planner on this axis.

## Part C — Worked Examples, Actually Built

All five builds below ran via `uv run python -m sphinx -b typst <source> <build>` this session (project
main tree, `.venv` already provisioned — no worktree isolation needed for this research session). Every
build exited 0 (`build succeeded`, with warnings on the three refusal shapes as expected).

### 1. Bare target (`"manual"`)

`conf.py`: `typst_documents = [("index", "manual", "Title", "Author", "typst")]`

```
$ find build -name '*.typ' | sort
build/_template.typ
build/index.typ
build/manual.typ
```
Log line: `typst: wrote 1 wrapper file(s) -- compile these: manual.typ`. No warnings.

### 2. Explicit path target (`"manuals/guide.typ"`)

`conf.py`: `typst_documents = [("index", "manuals/guide.typ", "Title", "Author", "typst")]`

```
$ find build -name '*.typ' | sort
build/_template.typ
build/index.typ
build/manuals/guide.typ
```
Log line: `typst: wrote 1 wrapper file(s) -- compile these: manuals/guide.typ`. No warnings. `index.typ`
stays at the outdir root (docname-derived), independent of where the wrapper landed.

### 3a. Refused target — parent traversal (`"../escape"`)

```
WARNING: a path is not supported in a typst_documents target name: '../escape' -- using 'escape' instead
$ find build -name '*.typ' | sort
build/_template.typ
build/escape.typ
build/index.typ
```
Log line: `typst: wrote 1 wrapper file(s) -- compile these: escape.typ`. 3 warnings total (the
resolution warning is emitted at write-doc time AND at the final wrapper-report derivation — measured,
not assumed: the same warning string appears three times in stderr for one build).

### 3b. Refused target — absolute (`"/abs/manual"`)

```
WARNING: a path is not supported in a typst_documents target name: '/abs/manual' -- using 'manual' instead
$ find build -name '*.typ' | sort
build/_template.typ
build/index.typ
build/manual.typ
```

### 3c. Refused target — drive-qualified (`"C:manual"`)

```
WARNING: a path is not supported in a typst_documents target name: 'C:manual' -- using 'manual' instead
$ find build -name '*.typ' | sort
build/_template.typ
build/index.typ
build/manual.typ
```

**All three refusal shapes land on the same fallback pattern**: basename extraction, then written at
the outdir root exactly like a bare target — 3a/3b/3c's file sets are structurally identical to
example 1's, differing only in the wrapper's stem.

### 4. Shared-child multi-master shape (existing fixture, not invented for this research)

Built `tests/fixtures/state_guard_three_master_gate` (3 masters `m1`/`m2`/`m3`, shared children
`common_a`/`common_b`, mid-level `mid`) with `-b typst`:

```
$ find build -name '*.typ' | sort
build/_template.typ
build/common_a.typ
build/common_b.typ
build/m1.typ
build/m2.typ
build/m3.typ
build/manual1.typ
build/manual2.typ
build/manual3.typ
build/mid.typ
```
Log line: `typst: wrote 3 wrapper file(s) -- compile these: manual1.typ, manual2.typ, manual3.typ`. 6
content files (one per docname: `common_a`, `common_b`, `m1`, `m2`, `m3`, `mid`) + 3 wrappers +
`_template.typ` = 10 `.typ` files. This is the measured file-set control for the "accepted composition
consequence" SC#3 requires — the compiled-PDF-level marker/heading-level proof (`COMMON-B-MARKER` count
= 1 in all three masters; resolved heading levels `[3]` in m1, `[2]` in m2 and m3) is Phase 49's own
measurement (`49-EVIDENCE.md` §"Degenerate-shape closure", quoted verbatim below) — it could not be
re-run live here because `typst.compile()` does not work in this sandbox (see Environment Availability).

### 5. Cross-check — this project's own docs build

`docs/source/conf.py:72-74`: `typst_documents = [("index", "typsphinx", project, author, "typst")]`.
Built `docs/source` with `-b typst` (required `uv sync --extra dev --extra docs` first — `myst_parser`
is a `docs`-extra dependency the base `dev` sync does not install):

```
$ find build -maxdepth 1 -name '*.typ' | sort
build/_template.typ
build/changelog.typ
build/contributing.typ
build/index.typ
build/installation.typ
build/quickstart.typ
build/typsphinx.typ
```
(plus nested `examples/*.typ`, `user_guide/*.typ`.) Log line: `typst: wrote 1 wrapper file(s) --
compile these: typsphinx.typ`. Confirms the exact prediction: wrapper `typsphinx.typ`, content
`index.typ`. Verified the wrapper's first lines contain `#show: project.with(title: ..., authors: ...,
date: ...)` and the content's first lines do not — the template/no-template split is real and matches
`writer.py`'s docstrings.

### Standalone-content-compile behaviour — could not be re-measured live; Phase 49's real transcript is the evidence

`typst.compile()` in this sandbox raises `FileNotFoundError` for even a trivial document (measured this
session — see Environment Availability), so the standalone-compile claim SC#1/D-08 requires cannot be
re-proven with a fresh compile here. Phase 49 already measured it directly against a real compile in an
environment where `typst-py` worked (`49-EVIDENCE.md` §"Handoff to Phase 51 and Phase 52", item 1),
quoted verbatim:

> `$ typst.compile("<build-dir>/shared.typ", output="shared_standalone.pdf", root="<build-dir>")`
> `standalone compile of shared.typ (no wrapper) succeeded`
> `$ pypdf-extracted text of the standalone compile:`
> `'Shared\nSHARED-CHAPTER-MARKER'`
> `SHARED-CHAPTER-MARKER in text: True`
> `NESTED-DOCNAME-BODY-MARKER in text: False`

"The compile SUCCEEDS and produces only that document's OWN body ... its state-guarded child ... is
ABSENT, because with no wrapper ever calling `.update(...)`, `state("typsphinx:include-edges",
()).get()` returns its declared default `()`, so every guard ... is false." This is the exact sentence
SC#1 requires the new page to publish as "documented as intended, well-defined behaviour."

## Part D — The SC#3 Gate's Shape (D-10/D-11/D-12)

### `tests/test_quickstart_docs_gate.py` — the D-10/D-11 precedent, read in full

**Two-class structure:**

- `TestQuickstartFirstPdfGate` — `@pytest.mark.skipif(not TYPST_AVAILABLE, ...)` where
  `TYPST_AVAILABLE` is set by `try: import typst` at module top. Runs a real `sys.executable -m sphinx
  -b typstpdf` subprocess against `tests/fixtures/quickstart_docs_gate/` and asserts the emitted
  `<stem>.typ`/`<stem>.pdf` filenames, where `<stem> = make_filename_from_project(_FIXTURE_PROJECT)`
  (`_FIXTURE_PROJECT = "My Project"`, computed once at module level, never hardcoded as a string
  literal). **Important for D-12:** this class's skip check is an IMPORT check, not a real-compile
  check — measured this session, `import typst` succeeds in this sandbox even though `typst.compile()`
  itself fails with `FileNotFoundError`. A gate that copies this class's skip pattern verbatim would
  therefore run (not skip) in this sandbox and then fail on the `-b typstpdf` subprocess's own PDF
  compile. D-12's "must never skip" requirement for the NEW Phase 51 gate is satisfied by NOT using
  this class's shape at all — using `-b typst` only, which needs no `typst-py` compile step (only
  markup generation), sidesteps the whole skip/import-vs-compile distinction.
- `TestPublishedQuickstartTextMatchesBuild` — no skip, no `typst-py` import, no `sphinx-build`
  subprocess. Reads `README.md` and `docs/source/quickstart.rst` with `Path(...).read_text()` and
  asserts literal substrings (e.g. `f"build/pdf/{_EXPECTED_STEM}.pdf"` must appear in
  `quickstart.rst`'s text) computed from the same `make_filename_from_project` helper the first class's
  fixture exercises. This is the pattern D-11's "derive expected values from the same helpers the
  builder uses" and "reads the published `.rst`/`.md` text from disk with `Path`" describe.

**`_run_sphinx_build()` helper (both this file and every other gate module copy it independently, per
this file's own docstring — "every gate module in this suite carries its own copy of this helper"):**
```python
subprocess.run(
    [sys.executable, "-m", "sphinx", "-b", builder, str(source_dir), str(build_dir)],
    capture_output=True, text=True,
)
```
Never `uv run sphinx-build`, never a resolved `sphinx-build` binary — `sys.executable` reuses the exact
interpreter/venv running pytest, sidestepping the NixOS PATH-shadowing hazard `CLAUDE.md` documents.

**Helper functions the new gate must import** (not re-derive): `sphinx.util.osutil.
make_filename_from_project` (for the default-derivation worked example) and, for the target-as-path
worked examples, no helper is needed beyond reading the real emitted file set off disk — the gate
should assert against `Path(build_dir / "<name>.typ").exists()` for the exact filenames Part C measured
above, not re-implement `_resolve_target_stem()`'s logic in the test.

### `tests/fixtures/` layout convention (confirmed, `quickstart_docs_gate/` inspected)

One directory per fixture, each containing exactly `conf.py` + one or more `.rst` source files (no
`_build/` checked in). `quickstart_docs_gate/conf.py`'s own header comment states its ONE job precisely
("mirrors docs/source/quickstart.rst's 'Your First PDF' flow verbatim ... Do not merge them and do not
modify the existing fixture") — the new gate's fixtures should follow the same one-fixture-one-job
discipline, likely one fixture per worked-example shape (bare/explicit-path/refused), matching Part C's
three scratch builds above almost exactly (those can become the actual fixture `conf.py` contents,
copied in rather than reinvented).

### `tests/test_docs_contract_claims_gate.py` — the D-J fence (read in full, do not extend across it)

This module's subject is **prose-vs-code agreement on `lang`/template-parameter route-scope claims**
(`TemplateEngine.uses_bundled_default_template()` against `docs/source/**/*.rst` prose) — a narrow,
named axis. Its own docstring states explicitly: "D-A/D-J ... declined a lockstep sync test over the
contract's parameter-NAME declaration surfaces ... This guard checks a different axis entirely ... do
not extend it across that fence." The new Phase 51 gate is a DIFFERENT subject (emitted `.typ` file
SETS against `typst_documents` configs, not template-parameter route-scope claims) and must be its own
new test module, not a method added to this class.

### `test_typst_documents_collision_gate.py` / `test_builder_output_stem.py` — existing assertions the new docs must not contradict

`test_builder_output_stem.py` already asserts, unit-level (via `temp_sphinx_app` fixture, calling
`_resolve_target_stem` directly): trailing-`.typ` stripping, period-preservation, path-bearing targets
resolving AS-IS (`test_resolve_target_stem_resolves_posix_path_bearing_target`), backslash
normalization, the three escape-guard shapes, and multiple degenerate-target fallback cases.
`test_typst_documents_collision_gate.py`'s `TestTypstDocumentsCollisionGate` class covers the
`ExtensionError` collision behaviour. Neither needs modification by this phase — they are the code-side
proof the new prose must agree with, already green.

### D-12's "no `typst-py` dependency" confirmed structurally achievable

A `-b typst`-only gate needs no `import typst` guard at all — `TestPublishedQuickstartTextMatchesBuild`
above already demonstrates the "zero optional-dependency, never skips" shape for the prose half; the
`-b typst` subprocess half needs nothing beyond `sphinx` itself (already a hard dependency, not
optional). This is a stronger guarantee than the existing precedent's PDF-compiling class, which DOES
carry an (import-only) `typst-py` conditional.

## Part E — Docs-Surface Integration Points

### `docs/source/user_guide/index.rst` — toctree and Main Topics (exact current content)

```rst
.. toctree::
   :maxdepth: 2

   configuration
   builders
   templates
```
```rst
Main Topics
-----------

:doc:`configuration`
   Learn about all configuration options available in ``conf.py``

:doc:`builders`
   Understand the difference between typst and typstpdf builders

:doc:`templates`
   Customize output using Typst templates
```
The new `output_layout.rst` page (D-01) needs a THIRD `toctree` entry AND a THIRD `:doc:`.../description
pair in Main Topics — CONTEXT.md's warning that the second list is easy to miss is confirmed: it is a
separate, hand-written definition list, not generated from the toctree, and nothing enforces the two
staying in sync.

### `docs/source/changelog.rst` — Migration Guides section and the D-02 format template

Section header confirmed at lines 4-8 (`Migration Guides` / `Migrating from 0.7.0 to 0.7.1`). The
0.7.0→0.7.1 subsection's exact shape (D-02's template): one intro sentence naming the count of breaking
changes, then per-change: a `- **Breaking:**` (or plain `-`) bullet explaining WHY, followed by two
adjacent `.. code-block:: python` blocks headed `# Old way -- X is gone in 0.7.1` / `# New way -- ...`.
The new `Migrating from 0.7.x to 0.8.0` subsection (per D-02, placed as a new subsection following this
same pattern) should reuse this exact shape: intro sentence, bullet(s) for (a) the output-shape change
and (b) the target-as-path reversal, each with before/after code blocks showing the concrete file-set
change (per SC#2's "concrete config and its concrete before/after file set" requirement) — Part C's
"bare target" measurement (`manual.typ` was-whole-document → is-now-wrapper, `index.typ` appears) is the
ready-made concrete illustration.

### Build command surface

- `tox -e docs-html` → `sphinx-build -b html source _build/html` (extras: `docs`). **Confirmed working
  in this sandbox** — ran the equivalent command directly this session (`myst_parser` etc. all resolve
  once `--extra docs` is synced); `build succeeded, 3 warnings`.
- `tox -e docs-pdf` → `sphinx-build -b typstpdf source _build/pdf`. **Confirmed NOT working in this
  sandbox** — `typst.compile()` raises `FileNotFoundError` (measured this session, see Environment
  Availability). Any verification step this phase adds must not require `docs-pdf` to pass locally;
  CI (non-NixOS runners) is where a real PDF-level check would need to run, and this phase does not add
  one (D-12 deliberately keeps the new gate at `-b typst` only, PDF-level verification explicitly out of
  scope).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Deriving the default wrapper filename for a worked example | A hardcoded string like `"myproject.typ"` | `sphinx.util.osutil.make_filename_from_project(project)`, same as `builder.py:19,183` and the existing gate's `_EXPECTED_STEM` | Keeps the doc's claim and the gate's assertion both tied to the ONE function that actually computes the value — a hardcoded string drifts silently if the helper's behaviour ever changes |
| Re-deriving `_resolve_target_stem()`'s escape/fallback logic inside the new gate | A parallel Python reimplementation of the decision tree in Part B | Assert against the REAL emitted file set from a real `-b typst` subprocess build (as Part C did) | This is exactly D-11's "derive expected values from the same helpers the builder uses" — asserting file EXISTENCE after a real build is testing the actual behaviour, not a second copy of it that can drift from the first |

**Key insight:** every worked example on the new page and every fixture in the new gate should be a
literal copy of one of Part C's five measured configurations (or a close variant) — inventing a sixth,
unmeasured configuration reintroduces exactly the "written from the design, not verified against the
build" failure mode SC#3 exists to close.

## Common Pitfalls

### Pitfall 1: Treating "the docs mention `#include()`" as sufficient without checking WHERE it lives now

**What goes wrong:** A rewritten example still shows `#include()` calls inside the wrapper/master file
(the pre-Phase-49 shape), when the real emission site moved into the CONTENT file as a state-guarded
conditional.
**Why it happens:** The wrapper DOES still contain exactly one `#include(...)` call (of its own content
file) — so a superficial check ("does the wrapper have an include") passes even when the deeper claim
(what the child-inclusion mechanism looks like) is wrong.
**How to avoid:** Any `#include()` code-block example must be checked against `translator.py:338-377`'s
`render_include_guard()` output shape (the `if "<edge_key>" in state(...).get() { include(...) }`
one-liner) and located in a CONTENT file's own emission, not attributed to the wrapper.
**Warning signs:** An example showing a bare `#include("chapter1.typ")` with no `if`/`state(...)` guard
around it, or attributing the include to the entry's own target filename.

### Pitfall 2: Assuming every unset-`typst_documents` code walkthrough resolves to `index.typ`/`index.pdf`

**What goes wrong:** Several existing pages (builders.rst:61,156,170; templates.rst:462) assume the
"master" file is named after the docname (`index`). Since v0.7.1's CONF-08, an unset `typst_documents`
resolves the WRAPPER name via `make_filename_from_project(project)`, never `index`.
**Why it happens:** `index.typ` used to be both the docname's file AND (pre-Phase-47) the whole
document; post-split, `index.typ` is unconditionally the CONTENT-ONLY file regardless of what triggered
its creation, so a stale example that "still runs" now silently compiles a child-less document instead
of erroring.
**How to avoid:** Every `typst compile`/`cat` example must be checked against a real `_resolve_target_stem`
walkthrough for its own implied config (per D-06) — either name the wrapper explicitly (a concrete
`typst_documents` line) or point at the runtime `typst: wrote N wrapper file(s) -- compile these: ...`
signal instead of a hardcoded filename.
**Warning signs:** Any `.typ`/`.pdf` filename literal in the docs that is not traceable to an explicit
`typst_documents` entry shown on the same page.

### Pitfall 3: Re-measuring `typst.compile()`-dependent claims in this sandbox and getting a false negative

**What goes wrong:** Attempting to verify the standalone-content-compile claim (D-08) with a fresh
`typst.compile()` call in this environment raises `FileNotFoundError`, which could be misread as "the
behaviour changed" rather than "the sandbox cannot run the native binary."
**Why it happens:** `import typst` succeeds (the Python wheel installs fine), but the underlying Rust
binary the wheel wraps cannot execute under NixOS's dynamic linker — an environment limitation, not a
code regression.
**How to avoid:** Cite Phase 49's own real-compile transcript (`49-EVIDENCE.md` §"Handoff to Phase 51
and Phase 52", quoted verbatim in Part C above) for any claim that requires an actual Typst compile;
use `-b typst` (markup generation only, no native binary invocation) for everything this phase can
verify directly.
**Warning signs:** Any executor attempting `typst.compile(...)` locally and treating a
`FileNotFoundError` as evidence of a behaviour change.

## Code Examples

### The wrapper's own body shape (verbatim, from `writer.py:308-319` template + measured output)

```typst
#state("typsphinx:include-edges", ()).update(("index#0>chapter1", "index#0>chapter2",))
#include("index.typ")
```
(the state line's array literal is `()` when the master has no toctree children at all — measured for
the `bare`/`explicit` scratch builds above, which have no toctree.)

### One content file's state-guarded toctree emission (verbatim shape, `translator.py:5309-5340` + `render_include_guard()`)

```typst
context {
  set heading(offset: heading.offset + 1)
  if "index#0>chapter1" in state("typsphinx:include-edges", ()).get() { include("chapter1.typ") }
  if "index#0>chapter2" in state("typsphinx:include-edges", ()).get() { include("chapter2.typ") }
}
```

### The wrapper-report log line (verbatim, `builder.py:767-770`, measured live for the `explicit` build)

```
typst: wrote 1 wrapper file(s) -- compile these: manuals/guide.typ
```

## State of the Art

| Old Approach (pre-Phase-47, v0.7.x) | Current Approach (v0.8.0, this phase documents) | When Changed | Impact |
|---|---|---|---|
| One `.typ` file per `typst_documents` entry, containing the whole document (template + body) | Two files per entry: a WRAPPER (template + state publication + one `#include()`) and a docname-named CONTENT file (no template, state-guarded child includes) | Phase 47 (split) + Phase 49 (state-guarded includes complete the mechanism) | Every existing `typst_documents` config now emits roughly twice as many `.typ` files; a tool that expected the target filename to BE the whole document finds a thin wrapper |
| A path component in a target (element 2) is rejected, truncated to its basename, with a warning | A path component is ACCEPTED as-is, relative to outdir; only `..`/absolute/drive-qualified are refused | Phase 47, OUT-01 (deliberate reversal of v0.7.1 Phase 44's D-05/D-06/D-07) | `"manuals/guide.typ"` now writes to `outdir/manuals/guide.typ` instead of `outdir/guide.typ` |
| Unconditional `#include()` for every toctree child, decided at WRITE time via a build-scoped dedup ledger | Static compile-time guard (`if "<edge_key>" in state(...).get() { include(...) }`) per child, decided at COMPILE time from each wrapper's own published edge set | Phase 49 (COMP-05/COMP-06) | A document shared by multiple masters now renders once in EACH master's own PDF, at that master's own position/heading level, instead of being claimed by only the first master that named it |

**Deprecated/outdated:** the pre-Phase-47 mental model "the target filename IS the document" no longer
holds for any `typst_documents` configuration; the pre-Phase-49 mental model "an included document is
claimed by exactly one master, globally" no longer holds either.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|---|---|---|
| A1 | Item 4 (`builders.rst:156`, `open build/pdf/index.pdf`) and item 8 (`changelog.rst:184`, historical 0.2.0 entry) are in-scope for DOC-14's repo-wide sweep even though neither is caused by the two-layer split | Part A sweep table | If out of scope, the plan should skip fixing them and note the deliberate exclusion; if in scope, they are two more cheap fixes. Low risk either way — flagged for an explicit owner/planner call, not asserted as a fact. |

No other claim in this research required non-authoritative inference — every functional claim above was
either read directly from `typsphinx/` source at HEAD, measured via a real `sphinx-build` subprocess run
this session, or quoted verbatim from a prior phase's own recorded real-compile transcript
(`49-EVIDENCE.md`).

## Open Questions

None outstanding for planning purposes. The `:numref:` divergence — the only item CONTEXT.md's own
`<deferred>` section names as unresolved for this milestone — is explicitly OUT of scope by D-07 (owner
override) and is not an open question this research needs to carry forward; it is tracked separately in
`.planning/todos/pending/2026-08-14-numref-number-diverges-per-master-and-vanishes-for-non-root-only-figures.md`
with `resolves_phase: null`.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|---|---|---|---|---|
| `typst` Python package (import only) | `-b typstpdf`, the existing gate's `TYPST_AVAILABLE` check | Partial — imports successfully | 0.15.0 | N/A (see next row) |
| `typst.compile()` (real native compile) | `-b typstpdf`, `tox -e docs-pdf`, any live PDF-level assertion | **No** — `FileNotFoundError: No such file or directory (os error 2)` measured live this session against a trivial 2-line document | — | Use `-b typst` (markup generation only) for every verification this phase can run locally; PDF-level proof relies on Phase 49's already-recorded real-compile transcripts, quoted verbatim in Part C |
| `myst_parser` (docs extra) | `docs/source/changelog.rst`'s `.. include:: ../../CHANGELOG.md` directive, `tox -e docs-html` | Not present in the base `dev` sync — required `uv sync --extra dev --extra docs` this session | 5.1.0 (resolved) | None needed — this is a normal, already-declared `docs` extra (`pyproject.toml:49-53`); any executor building `docs/source` must `uv sync --extra docs` (or `--extra dev --extra docs`) first, same as `tox -e docs-html`/`tox -e docs-pdf` already do via their own `extras = docs` tox declaration |

**Missing dependencies with no fallback:** none — every verification this phase's plan can require
(the new SC#3 gate, all worked-example builds) uses `-b typst` only, which needs no native Typst binary.

**Missing dependencies with fallback:** `typst.compile()` — fallback is citing Phase 49's already-
recorded real-compile evidence rather than re-measuring locally (documented above).

## Validation Architecture

This is a documentation phase with one net-new test module (the SC#3 gate, D-10/D-11/D-12); there is no
application code under test. The four validation dimensions the phase description names:

### 1. Prose-vs-code claim gate (D-10/D-11/D-12)

| Property | Value |
|---|---|
| Framework | `pytest` (existing `dev` extra, already the project's sole test framework) |
| Precedent module | `tests/test_quickstart_docs_gate.py` (two-class shape: real-build class + never-skip prose-match class) |
| New module (planner names it) | `tests/test_output_layout_docs_gate.py` (suggested name — matches D-01's working page name `output_layout.rst`) |
| Config file | none — pytest config lives in `pyproject.toml` (existing) |
| Quick run command | `pytest tests/test_output_layout_docs_gate.py -q` |
| Full suite command | `pytest -m "not slow"` |
| Signal | Real `-b typst` subprocess build of each worked-example fixture (Part C's five configs, or a representative subset) asserting the exact `.typ` file set on disk, PLUS a prose-match class reading `output_layout.rst` from disk and asserting it names those exact filenames |
| Sampling rate | Per task commit: the new module alone (`pytest tests/test_output_layout_docs_gate.py -q`, seconds). Per wave merge / phase gate: full `pytest -m "not slow"` (this module carries no `typst-py` dependency so it always runs, never skipped) |

### 2. Real-build file-set assertion

Already demonstrated as feasible and cheap this session — five real `-b typst` builds (Part C) each
completed in well under a second. The new gate should reuse this exact mechanism: `subprocess.run([sys.
executable, "-m", "sphinx", "-b", "typst", source, build], ...)` then `assert (build /
"<name>.typ").exists()` for each expected file, mirroring `_run_sphinx_build()`'s existing shape.

### 3. Repo-wide sweep completeness check

Part A's sweep is itself the "completeness" proof for THIS research pass, but it is a one-time grep, not
a standing gate — D-04 does not mandate a permanent regression test against future staleness (only
D-10/11/12 mandate a permanent gate, and its scope is the NEW page's own claims, not a sweep over the
whole doc set). The planner should treat Part A's table as the closed task list for THIS phase; no new
automated "no stale `.typ` filename anywhere in docs/" gate is in scope unless the planner chooses to
add one (not required by any locked decision).

### 4. `:numref:` absence check

No dedicated gate is required — D-07 forbids PUBLISHING `:numref:`, not testing for it. The cheapest
verification is a literal `grep -rn ':numref:' docs/source/ README.md CHANGELOG.md` returning empty
before the phase closes (a one-line manual/CI check, not a pytest module) — consistent with how the
existing `test_no_stale_github_io_links.py`-style literal-absence checks are already done elsewhere in
this suite (concatenated-fragment technique to avoid the check module itself matching its own grep, if
a permanent test is added — see `test_quickstart_docs_gate.py:181-187`'s `_MANDATORY_CLAUSE` pattern for
the exact idiom, useful if the planner decides a standing `:numref:`-absence pytest module is worth
adding).

## Security Domain

`security_enforcement` is on project-wide, but this phase changes zero lines under `typsphinx/` — no
new input-handling, authentication, session, or cryptography surface is introduced. The only "input" is
prose the phase's own authors write and a new test module that shells out to `sphinx-build` on
project-controlled fixture directories (the same subprocess pattern every existing gate module already
uses, e.g. `test_quickstart_docs_gate.py:53-78`). No ASVS category applies materially beyond what the
existing gate precedent already satisfies (fixed, repo-controlled fixture paths passed to
`subprocess.run` with a list argument, never `shell=True`, never user-controlled input).

| ASVS Category | Applies | Standard Control |
|---|---|---|
| V2 Authentication | No | N/A — no auth surface |
| V3 Session Management | No | N/A |
| V4 Access Control | No | N/A |
| V5 Input Validation | No (new code) | The new gate reuses the existing `subprocess.run([...], ...)` list-argument pattern (no shell injection surface); no user input is parsed |
| V6 Cryptography | No | N/A |

No new threat patterns identified for this phase's own new code (the SC#3 gate module).

## Sources

### Primary (HIGH confidence — read from source or measured live this session)

- `typsphinx/builder.py:1-1010` (full read of the cited ranges: 36-188, 296-420, 502-613, 700-800,
  960-1010) — every function cited in Part B
- `typsphinx/writer.py:1-320` — `compute_content_include_path()`, `translate()`, `render_wrapper()`
- `typsphinx/translator.py:192,330-378,5260-5350` — `INCLUDE_STATE_KEY`, `render_include_edge_state()`,
  `render_include_guard()`, the toctree state-guard emission site
- `tests/test_quickstart_docs_gate.py` (full read) — the D-10/D-11 precedent
- `tests/test_docs_contract_claims_gate.py:1-80` — the D-J fence
- `tests/fixtures/quickstart_docs_gate/conf.py`, `tests/fixtures/state_guard_three_master_gate/conf.py`
  (full read)
- Five live `sphinx-build -b typst` runs (bare/explicit/3× refused targets), one live
  `state_guard_three_master_gate` build, one live `docs/source` build, one live `docs/source` HTML
  build, one live `typst.compile()` failure probe — all executed and captured this session
- `docs/source/user_guide/{configuration,builders,templates,index}.rst`, `docs/source/quickstart.rst`,
  `docs/source/changelog.rst` (relevant sections, full read)
- `README.md:70-310` (full read), `examples/basic/README.md` (full read), `examples/advanced/README.md`
  (full read), `examples/charged-ieee/README.md:85-125`, `examples/{basic,advanced,charged-ieee/
  approach{1,2}}/conf.py` (`typst_documents` lines)

### Secondary (MEDIUM confidence — quoted from a prior phase's own recorded measurement, not re-verified live this session)

- `.planning/phases/49-per-master-include-graph-with-state-guarded-includes/49-EVIDENCE.md`
  §"Handoff to Phase 51 and Phase 52" and §"Degenerate-shape closure" — the standalone-compile
  transcript and the three-master marker/heading-level PDF-level measurement, both quoted verbatim
  above because this session's own `typst.compile()` does not work

### Tertiary (LOW confidence)

None — every finding in this document is either a direct source read, a live measurement, or a verbatim
quote from another phase's own recorded live measurement.

## Metadata

**Confidence breakdown:**
- Falsified-claim sweep (Part A): HIGH — repo-wide grep executed this session across the exact scope
  D-04 specifies, cross-checked against every named `conf.py`
- Behaviour contract (Part B): HIGH — every function read at HEAD this session, no reliance on
  CONTEXT.md's summary alone
- Worked examples (Part C): HIGH for `.typ`-level claims (five live builds); MEDIUM for the standalone-
  compile / PDF-marker claims (cited from Phase 49's own real-compile transcript, not re-run live here
  due to the sandbox's `typst.compile()` limitation)
- Gate shape (Part D): HIGH — both precedent modules read in full
- Docs-surface integration points (Part E): HIGH — exact current content quoted from disk

**Research date:** 2026-08-14
**Valid until:** Effectively permanent for the code-behaviour claims (frozen at HEAD, Phases 47-50 are
complete and this phase makes no code changes) — but re-verify the sweep table (Part A) if any doc file
is touched by an unrelated commit before this phase executes.
