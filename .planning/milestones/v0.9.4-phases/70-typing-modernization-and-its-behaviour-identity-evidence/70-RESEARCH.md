# Phase 70: Typing Modernization and Its Behaviour-Identity Evidence - Research

**Researched:** 2026-09-13
**Domain:** Mechanical Python typing-syntax rewrite + five-legged behaviour-identity evidence (masked-AST hash, pytest counts, `.typ` byte-identity, mypy string-identity, docs-diff classification)
**Confidence:** HIGH — every claim below is either (a) copied from the milestone-level research (`.planning/research/*.md`, already HIGH confidence and not re-litigated) or (b) a command run in this session against a scratch git worktree, with output shown

## Scope note

The milestone-level research (`SUMMARY.md`, `STACK.md`, `ARCHITECTURE.md`, `PITFALLS.md`) already
covers conversion mechanics in full: the exact `ruff --fix` behaviour, the `__init__.py:15`
survivor, the `ast.Dict` trap, and the A–E file-disjoint split. This document does not repeat that
material except where a fresh measurement changed, sharpened, or contradicted it. The effort here
went into the **evidence half** — the five QUA-12 legs, DOC-22's two-commit ordering, and DOC-23's
docs diff — because that is where a phase plan can go wrong even though the rewrite itself is
mechanical.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**DOC-22 — what `CLAUDE.md:75` says after the rewrite**

- **D-01** — The bullet keeps its Python-floor fact and gains one standing instruction about
  annotation style: builtin generics (`dict[str, Any]`, `list[str]`, `set[...]`, `tuple[...]`) and
  `collections.abc` for abstract types such as `Iterator`, not `typing.Dict`/`List`/`Set`/`Tuple`/
  `Iterator`. True on both sides of the ignore flip.
- **D-02** — The rewrite drops every flip-dependent claim and every pointer to the deferral:
  "intentionally ignores", "deliberate deferral", the `todos/pending/` path, "Don't 'modernize'...".
  No history note.
- **D-03** — No standing prohibition on `from __future__ import annotations` or PEP 604 unions is
  added. `typsphinx/` already carries 52 `| None` annotations.
- **D-04** — The edit is confined to the one bullet at line 75.

**QUA-12 (d) — which `.typ` output must be byte-identical**

- **D-05** — The corpus is every Sphinx project under `tests/` with a `conf.py`, enumerated fresh
  at `PHASE_BASE_SHA` (measured at discussion time as 167: 166 under `tests/fixtures/`, 1 under
  `tests/roots/`). Built with `-b typst` on both sides, every emitted `.typ` compared by hash. File
  lists must match too.
- **D-06** — A fixture whose build fails is still part of the corpus; record exit status and
  emitted `.typ`, both must match between sides. Never dropped for failing.
- **D-07** — `examples/` is not in the leg (d) corpus (stays in `ruff check .` scope only).
- **D-08** — Corpus build time is unmeasured up front; pilot a handful, extrapolate, stop and ask
  the owner if prohibitive.

**DOC-23 — what the clean docs build covers**

- **D-09** — Two outputs: the HTML build and the `.typ` the typstpdf build emits. Both built clean
  (`rm -rf docs/_build` first) on base and post-flip, each with a base-vs-base control build. Tox
  commands `docs-html` / `docs-pdf`. The PDF binary itself is not compared; the `.typ` it compiles
  from is.
- **D-10** — The docs `.typ` belongs to DOC-23, never to leg (d) (leg (d) is `tests/`-only and
  requires byte identity; the docs `.typ` is expected to differ).
- **D-11** — Every differing hunk of both docs diffs is classified. Each must sit in an
  API-reference page (`api/…`) and be explained by a `Dict`/`List`/`Set`/`Tuple` →
  `dict`/`list`/`set`/`tuple` rename in an autodoc'd signature or field, including any link
  target/title change. Any hunk that does not trace this way goes to the owner. Never written off
  as nondeterminism — the control build is what separates that.

### Claude's Discretion

- The exact wording of the rewritten `CLAUDE.md:75` bullet, within D-01..D-03.
- The plan split (research's A–E is the expected shape, not a mandate).
- Evidence file names/layout — verbatim transcripts in phase markdown, no new committed script, no
  new test (a new test would also break leg (b)'s collected-count identity).
- Which file pilots the masked-AST normalization, and how the base side is materialised (second
  worktree at `PHASE_BASE_SHA`, or `git archive` into scratch).
- Raw-HTML vs extracted-text for the docs diff, as long as D-11's classification is complete.

### Deferred Ideas (OUT OF SCOPE)

None came up in discussion. Reviewed-but-not-folded todos: MSG-06 (hardcoded delimiter in
`translator.py` debug logs — constraint 12 forbids absorbing it even though `translator.py` is
edited here), TRN-01/NUM-01/DOC-18 (all change emitted output, forbidden), QUA-08 (needs a workflow
edit, forbidden).
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| QUA-09 | Zero `UP006`/`UP035` repo-wide, ignores removed, count measured fresh | § Conversion Mechanics (re-verified fresh this session: 113/93/20, 10 files, identical breakdown to milestone research) |
| QUA-11 | Builtin generics + `collections.abc.Iterator`, no PEP 604 sweep, no `__future__`, no API change, `@preview` lines untouched | § Conversion Mechanics; confirmed every changed line in the scratch conversion names a typing symbol, zero non-typing lines touched |
| QUA-12 | Five-legged behaviour-identity evidence (a)-(e) | § Evidence Architecture — masked-AST harness (a) with working code and non-vacuity proof, pytest mechanics (b), `git diff` framing (c), `.typ` corpus mechanics + path-independence proof (d), mypy string-identity mechanics (e) |
| DOC-22 | `CLAUDE.md:75` rewrite lands first, todo moves with the flip | § SC#1 Mechanics — exact `git merge-base --is-ancestor` and `git grep` commands, both re-verified fresh |
| DOC-23 | Clean docs build diff confined to API-reference type text | § Docs Build Findings — HTML/PDF diffs measured, control build proves zero nondeterminism, one **contradiction with D-11** flagged (viewcode pages) |
</phase_requirements>

## Summary

This phase has two halves of very different character. The **conversion half** (QUA-09/QUA-11) is
exactly as mechanical as the milestone research found: `ruff check . --fix` (with the two ignores
removed) resolves 111 of 113 findings in one pass, black is a byte-for-byte no-op afterward, and the
one survivor (`typsphinx/__init__.py:15`'s `Dict`) needs the one documented hand edit. This session
re-verified all of that fresh in a scratch git worktree and found nothing new to add.

The **evidence half** (QUA-12, DOC-22, DOC-23) is where this research spent its effort, and it
surfaced several concrete, previously-unmeasured facts a plan needs:

1. **The masked-AST mask from CONTEXT's Specific Ideas needs one refinement beyond the prose
   description: the `ImportFrom` node must be deleted from its parent's body, not merely emptied in
   place.** A first implementation that emptied the node in place (kept it as a stub) produced
   false `DIFFER` results on the three files where a `from typing import` line is either deleted
   entirely or reordered by ruff's import sort — because AST node *position* in the body list still
   participated in the hash even with the node's contents blanked. Deleting the node outright fixes
   this; all 10 files then hash equal, and a non-vacuity control (renaming a class) still changes
   the hash.
2. **`.typ` byte-identity does not depend on build location.** Building the same fixture at two
   different absolute paths (and rebuilding at the same path) produced byte-identical `.typ` files
   every time; only Sphinx's own `.doctrees/*.pickle` cache differed. The corpus comparison can
   simply exclude `.doctrees/` rather than requiring both sides to build at an identical absolute
   path (building at the same path is still fine as belt-and-braces, just not load-bearing).
3. **The pytest collected-count line is `=`-decorated, confirmed live** (`==== 1548 tests collected
   in 0.35s ====`) — an anchored `^[0-9]` extraction returns empty; use the unanchored
   `grep -oE '[0-9]+ tests? collected'` form.
4. **The CHANGELOG page gate's skip count is provisioning-dependent, and this matters for leg
   (b)'s "identical passed/collected count" claim.** In a `--extra dev`-only worktree,
   `test_changelog_page_gate.py` reports `2 passed, 4 skipped`; with `--extra dev --extra docs` it
   reports `6 passed, 0 skipped`. Both sides of every QUA-12 leg must provision with the **same**
   extras set (recommend `--extra dev --extra docs` throughout Phase 70, matching Phase 71's
   established practice) or the pass/skip counts will differ for a reason that has nothing to do
   with the typing rewrite.
5. **`uv run mypy`'s sync/rebuild chatter goes to stderr, not stdout** — `mypy typsphinx/`'s own
   output (`Success: no issues found in 9 source files`) is clean and string-comparable on stdout
   alone, confirmed identical before and after conversion, and stable across `--no-incremental` and
   a warm `.mypy_cache`.
6. **A fresh worktree's default interpreter (uv-managed CPython 3.14.4) differs from the main
   checkout's (nixpkgs 3.13.13), but `uv sync --python 3.13.13` resolves to the exact same nixpkgs
   interpreter path** — this is the concrete mechanism for constraint 6's "same interpreter on both
   sides" requirement.
7. **A genuine contradiction with locked decision D-11**, found by actually building both docs
   sides and diffing: the clean-build HTML diff touches not just `api/index.html` but also four
   `sphinx.ext.viewcode` pages under `_modules/typsphinx/*.html` (the syntax-highlighted mirror of
   the source itself, which of course differs wherever the source text differs). D-11 requires
   every differing hunk to "sit in an API-reference page (`api/…`)"; these four pages are outside
   that prefix. See **Contradictions With Locked Decisions** below — this is reported, not
   re-decided.
8. A second, more subtle docs-rendering effect worth knowing before reading a diff: `Set[str] |
   None` in source renders as `Optional[Set[str]]` in the API reference, but `set[str] | None`
   (the exact same annotation, converted) renders as `set[str] | None` textually — because
   `typing.Set[str] | None` and `set[str] | None` are different runtime objects
   (`typing.Union` vs. `types.UnionType`) that Sphinx's own `stringify_annotation` formats
   differently. This still traces to a converted annotation (satisfies D-11's substance), but a
   plan should not assume every diff hunk is a literal word-for-word `Dict`→`dict` swap.

**Primary recommendation:** keep the wave shape the ROADMAP already binds (CLAUDE.md rewrite +
baseline first, file-disjoint conversions under the still-present ignores, the `pyproject.toml`
flip last, after-side evidence in its own wave); use the refined node-deleting mask for leg (a);
provision every worktree with `--extra dev --extra docs`; compare `.typ` corpora with `.doctrees/`
excluded; and put the viewcode-page finding to the owner as an amendment to D-11 rather than
silently satisfying or silently failing it.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Typing-syntax rewrite (`typsphinx/`, `tests/`) | Library source (Python package) | — | Pure static annotation/import rewrite, zero runtime-behaviour surface |
| Lint-gate flip (`pyproject.toml`) | Build/CI config | — | Config-only; governs what `ruff check .` accepts |
| Contributor-facing instruction (`CLAUDE.md`) | Documentation | — | Read by every executor as ambient instruction, not code |
| Masked-AST equality proof | Verification tooling (throwaway script, not committed) | — | A pure-Python `ast`-module script run inside the verify block, per this project's evidence convention (no new committed script/test) |
| `.typ` corpus byte-identity | Build output (Sphinx `typst` builder) | Test fixtures (`tests/fixtures/`, `tests/roots/`) | The builder emits `.typ`; the fixture corpus is what's compared |
| Docs diff (HTML + PDF `.typ`) | Documentation build (`docs/source`) | Sphinx extension surfaces (`autodoc`, `sphinx_autodoc_typehints`, `viewcode`) | The rendering path (not `typsphinx/` itself) is what changes visibly |
| CI dispatch / branch push | CI/CD (`.github/workflows/ci.yml`) | — | Milestone invariant #5; no code-tier involvement |

This is a single-tier (library-source) milestone with a documentation and CI/CD side-effect surface
— there is no browser/frontend/API-boundary tier to misassign work to, and `ui.plan-gate` is
correctly expected to false-positive on "docs-html"/"render"/"page" wording (per project memory);
`**UI hint**: no` is correct.

## Standard Stack

No new stack. This confirms the milestone-level `STACK.md` finding by direct re-measurement in a
fresh scratch worktree this session (not by re-reading STACK.md's own numbers):

| Tool | Version (this session, fresh worktree) | Confirmed behaviour |
|------|------------------------------------------|----------------------|
| ruff | 0.16.6 `[VERIFIED: uv run ruff --version, this session]` | `--fix` resolves 113→2 in one pass; second pass no-op |
| black | (worktree's pinned version, `uv.lock`) `[VERIFIED: uv run black --check --diff ., this session]` | Zero reformatting after the rewrite: `All done! ... 355 files would be left unchanged.` |
| mypy | 2.3.1 in the fresh worktree (`uv.lock`-pinned) vs. 2.1.0 in the main checkout's stale `.venv` `[VERIFIED: uv run mypy --version, both trees, this session]` | `Success: no issues found in 9 source files`, byte-identical before/after |
| Python | main checkout nixpkgs 3.13.13; fresh worktree default uv-managed 3.14.4; `uv sync --python 3.13.13` pins the nixpkgs 3.13.13 path exactly `[VERIFIED: .venv/pyvenv.cfg, both trees, this session]` | See § Same-Interpreter Mechanism |

No new dependency, no version bump recommended or needed.

## Package Legitimacy Audit

Not applicable — this phase installs no new package. `Package Legitimacy Gate` is skipped.

## Architecture Patterns

### Wave shape (binding, from ROADMAP constraint 1 / research ARCHITECTURE.md — reconfirmed fresh)

```
Phase 70
├── Wave 0: CLAUDE.md:75 rewrite (lint-neutral) + pre-conversion baseline capture
│           (PHASE_BASE_SHA, fresh ruff count+version, QUA-12 (b)/(d)/(e) "before" sides,
│           DOC-23 "before" clean docs build)
├── Wave 1 (parallel, file-disjoint, ignores still present so every merge stays lint-green):
│   ├── Plan A: typsphinx/translator.py                              (42 findings)
│   ├── Plan B: typsphinx/builder.py                                 (30 findings)
│   ├── Plan C: typsphinx/template_engine.py + template_registry.py  (12+4=16)
│   ├── Plan D: typsphinx/writer.py + typsphinx/__init__.py          (2+2=4, incl. hand edit)
│   └── Plan E: tests/{conftest,test_bundle_layout_sweep_gate,
│               test_include_edge_derivation_unit,
│               test_include_ledger_removal_gate}.py                 (2+6+4+9=21, incl. Iterator move)
├── Wave 2: the flip plan (sole owner of pyproject.toml/CLAUDE.md/the todo move) —
│           removes both ignores + comments, moves the todo, re-measures repo-wide
│           (expect zero), runs the gate quartet
└── Wave 3: after-side evidence (QUA-12 (b)/(d)/(e) "after", DOC-23 "after" + control),
            CI dispatch, branch push
```

Re-verified fresh this session (`uv run ruff check . --select UP006,UP035 --output-format=concise`
on a clean scratch worktree at the current `HEAD`, `cbd448bf`): **113 findings (93 UP006 + 20
UP035) across exactly the same 10 files and the same per-file counts** the milestone research and
ROADMAP recorded (`translator.py` 42, `builder.py` 30, `template_engine.py` 12,
`test_include_ledger_removal_gate.py` 9, `test_bundle_layout_sweep_gate.py` 6,
`template_registry.py` 4, `test_include_edge_derivation_unit.py` 4, `writer.py` 2, `__init__.py` 2,
`conftest.py` 2). The A–E groups are file-disjoint from each other and from Plan F's
`pyproject.toml`/`CLAUDE.md`/todo-move surface — no plan touches a file another plan touches.
`[VERIFIED: uv run ruff check . --select UP006,UP035, this session, ruff 0.16.6]`

**Note for whoever picks `PHASE_BASE_SHA` at execution time:** this session's fresh count was taken
at commit `cbd448bf` (current `HEAD` of `gsd/v0.9.4-typing-modernization` as of this research). By
execution time `HEAD` will have advanced (this very research commit, at minimum). Re-run the count
at the actual execution-time `HEAD` — do not copy `113`/`cbd448bf` from this document as the
recorded baseline; constraint 3 requires it fresh.

### Evidence Architecture

#### Leg (a) — masked-AST hash, working implementation

The prior-art harness (v0.9.3 Phase 68, `68-02-PLAN.md:253`,`:305`) masks docstrings and assert
messages. This phase's mask target is different — annotation subtrees and the `typing`/
`collections.abc` import lines — and CONTEXT's Specific Ideas section already describes the target
precisely. This session implemented and tested it; the one addition beyond the prose spec is
**delete** the masked `ImportFrom` node from the AST (via `ast.NodeTransformer` returning `None`),
not merely blank its `names`/`module` fields in place:

```python
# Source: this session's scratch harness, tested against the real tree
# (typsphinx/translator.py, typsphinx/__init__.py, tests/test_include_ledger_removal_gate.py,
# typsphinx/template_engine.py, typsphinx/builder.py, typsphinx/template_registry.py,
# typsphinx/writer.py, tests/conftest.py, tests/test_bundle_layout_sweep_gate.py,
# tests/test_include_edge_derivation_unit.py — all 10 files hash EQUAL, base vs. converted)
import ast, hashlib

class Mask(ast.NodeTransformer):
    def visit_ImportFrom(self, node):
        if node.module in ("typing", "collections.abc"):
            return None  # DELETE the node -- do not just empty node.names in place.
        return node       # An import line may move (I001 sort), split (Dict/Iterator/Set ->
                          # two imports), or vanish entirely (no typing import left at all);
                          # keeping an emptied stub node at its old body position produced a
                          # false hash mismatch for the 3 files where this happens.

    def visit_FunctionDef(self, node):
        return self._mask_func(node)

    def visit_AsyncFunctionDef(self, node):
        return self._mask_func(node)

    def _mask_func(self, node):
        self.generic_visit(node)
        node.returns = None
        a = node.args
        for arg in (a.posonlyargs + a.args + a.kwonlyargs):
            arg.annotation = None
        if a.vararg:
            a.vararg.annotation = None
        if a.kwarg:
            a.kwarg.annotation = None
        return node

    def visit_AnnAssign(self, node):
        self.generic_visit(node)
        node.annotation = ast.Constant(value=None)
        return node

def sk(source: str) -> str:
    t = ast.parse(source)
    t = Mask().visit(t)
    ast.fix_missing_locations(t)
    return hashlib.sha256(
        ast.dump(t, annotate_fields=True, include_attributes=False).encode()
    ).hexdigest()
```

**Measured this session** (`git show <base>:<path> | sk()` vs. `sk()` on the fully-converted
working tree, all 10 files):

```
typsphinx/translator.py                          EQUAL
typsphinx/__init__.py                            EQUAL
tests/test_include_ledger_removal_gate.py        EQUAL   (the Iterator import-split file)
typsphinx/template_engine.py                     EQUAL
typsphinx/builder.py                             EQUAL
typsphinx/template_registry.py                   EQUAL
typsphinx/writer.py                              EQUAL
tests/conftest.py                                EQUAL
tests/test_bundle_layout_sweep_gate.py           EQUAL   (import line vanishes entirely)
tests/test_include_edge_derivation_unit.py       EQUAL   (import line vanishes entirely)
```
`[VERIFIED: this session, scratch git worktree at cbd448bf + ruff --fix + one hand edit]`

**Non-vacuity control, measured this session:** renaming `class TypstTranslator` to
`class TypstTranslatorZZZ` in a scratch copy of `translator.py` changed the hash
(`8c766e23...` → `5c954eac...`) — the mask does not trivially hash everything to the same value.
`[VERIFIED: this session]`

**What this leg proves, and what it does not (write this into the plan, not just the code):**
Because the entire `ImportFrom` node is deleted before hashing, this leg proves the **non-import,
non-annotation** code is structurally unchanged — no statement, expression, call, or control-flow
node moved, was added, or was removed. It does **not** independently prove that the import list
itself is *correct* (e.g., that a converted file didn't accidentally also drop a legitimately-used
`Any` import) — because any annotation referencing `Any` is *also* nulled by the annotation mask,
regardless of whether `Any` stayed imported. That gap is closed by the other two legs that touch
these files: **leg (e)** (`mypy typsphinx/`) would flag an undefined `Any`/`NamedTuple` name, and
**leg (b)** (pytest collection) would fail to import a `tests/` module with a broken import. Treat
the five legs as a set, not leg (a) alone, when writing the plan's "done" criteria.

**Enumeration of typing usages outside the masked positions (module-level type aliases, `cast(...)`,
`TypeVar`, quoted/forward-ref annotations)** — re-verified fresh this session, zero hits for all
four, on the pristine base tree:

```
$ grep -rnE '^\s*[A-Za-z_][A-Za-z0-9_]*\s*=\s*(Dict|List|Set|Tuple)\[' typsphinx/ tests/
none found
$ grep -rn "cast(" typsphinx/ tests/
none found
$ grep -rn "TypeVar(" typsphinx/ tests/
none found
$ grep -rnE '"(Dict|List|Set|Tuple)\[|'"'"'(Dict|List|Set|Tuple)\[' typsphinx/ tests/
none found
```
`[VERIFIED: this session, grep against pristine base tree]`

Class-level `NamedTuple` field annotations (e.g. `translator.py:126`'s
`xref: tuple[str, str] | None` inside `class _ReferenceAnchorDecision(NamedTuple):`) and
function-local variable annotations (e.g. `template_registry.py:469`'s
`registry: Dict[str, TemplateRegistryEntry] = {}`) **are** `AnnAssign` nodes regardless of scope,
and the mask's `visit_AnnAssign` fires on them via `ast.NodeTransformer`'s default recursive
traversal into `ClassDef`/`FunctionDef` bodies — confirmed empirically above (both files hash
EQUAL).

#### Leg (b) — pytest collected/passed counts

**The summary line is `=`-decorated; an anchored extraction returns empty, confirmed live:**

```
$ uv run pytest --collect-only -q 2>&1 | tail -1
======================== 1548 tests collected in 0.35s =========================
$ echo "$LINE" | grep -oE '^[0-9]+ tests? collected'
(empty)
$ echo "$LINE" | grep -oE '[0-9]+ tests? collected'
1548 tests collected
```
`[VERIFIED: this session]` — use the unanchored form, exactly as this project's own memory already
records for a different gate (`gsd-decision-coverage-bullet-format`-adjacent pytest-summary
pitfall).

**Full-suite run, converted tree, `--extra dev --extra docs` worktree:**

```
$ LC_ALL=C uv run pytest -q -p no:cacheprovider
================= 1547 passed, 1 skipped in 124.95s (0:02:04) ==================
```
`[VERIFIED: this session, full suite, converted working tree]` (1547+1=1548, matching the collect
count). ~125s wall clock for the full suite — budget for it being run at least twice per side
(before/after) across the phase's legs, ideally sharing runs where possible (e.g., the same "after"
run can serve leg (b) and the final gate-quartet check).

**Provisioning hazard, measured live — both sides of every leg must use the same extras:**

```
# --extra dev only:
tests/test_changelog_page_gate.py: 2 passed, 4 skipped in 0.03s
#   (4 skips read "...ra only (D-01), so a dev-only CI lane skips this class")

# --extra dev --extra docs:
tests/test_changelog_page_gate.py: 6 passed, 0 skipped in 4.33s
```
`[VERIFIED: this session, two independently-provisioned scratch trees]`. Provision **every**
worktree used for QUA-12 measurements (base and post-flip alike) with
`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs --python 3.13.13`,
not `--extra dev` alone — otherwise leg (b)'s "identical passed/collected counts" claim can fail
for a provisioning reason unrelated to the typing rewrite, and worse, could silently "match" at a
lower, skip-inflated count on both sides if both happen to use `--extra dev` only, hiding real
coverage.

#### Leg (c) — zero pre-existing test-assertion edits

Re-verified fresh this session on the scratch conversion: every changed line under
`typsphinx/` and `tests/` mentions a typing name (`Dict`/`List`/`Set`/`Tuple`/`typing`/
`collections.abc`):

```
$ git diff -- typsphinx/translator.py | grep -E '^[+-]' | grep -v '^[+-][+-][+-]' \
    | grep -viE '(Dict|List|Set|Tuple|dict|list|set|tuple|typing)'
(empty)
```
`[VERIFIED: this session]`, and confirmed for `typsphinx/__init__.py`,
`tests/test_include_ledger_removal_gate.py`, `typsphinx/template_engine.py`,
`typsphinx/builder.py`, `typsphinx/template_registry.py`, `typsphinx/writer.py`,
`tests/conftest.py` by inspection of each file's diff. The recommended verification form for the
plan: `git diff --stat` scoped to the plan's own files, plus a grep of the diff's added/removed
lines for the negation above.

`tests/test_authors_pipeline_stage_gate.py:515` — read directly this session:
```python
        if isinstance(node, ast.Return) and isinstance(node.value, ast.Dict):
```
(surrounding context, same file, line 513: `literal_keys: set[str] = set()` — already lowercase,
unrelated). Confirmed **zero** UP006/UP035 findings on this file
(`uv run ruff check tests/test_authors_pipeline_stage_gate.py --select UP006,UP035` produces no
diagnostic output), so no conversion plan touches it, and its `ast.Dict` stays byte-identical by
construction, not by discipline. `[VERIFIED: tests/test_authors_pipeline_stage_gate.py:513-515, read this session]`

#### Leg (d) — byte-identical `.typ` corpus

**Corpus count, re-enumerated fresh this session:**
```
$ find tests/fixtures -name conf.py | wc -l
166
$ find tests/roots -name conf.py | wc -l
1
```
`[VERIFIED: this session]` — matches D-05's 167 exactly.

**Pilot timing (5 fixtures, bare `sphinx-build -b typst`):**
```
abbr_pep_separator_render_gate:        exit=0  time=0.28s  typ_files=3
citation_render_gate:                  exit=0  time=0.24s  typ_files=4
derived_template_collision_gate:       exit=2  time=0.23s  typ_files=0
external_link_style_render_gate:       exit=0  time=0.24s  typ_files=3
manpage_render_gate:                   exit=0  time=0.23s  typ_files=3
TOTAL for 5 = 1.22s, avg=0.24s/project, extrapolated 167 ≈ 41s
```
`[VERIFIED: this session]`. **Not prohibitive** — a single-side full-corpus build is on the order
of 40 seconds, not minutes. D-08's "stop and ask the owner if prohibitive" branch does not fire;
the plan can run the full 167-project corpus on both sides without a time-budget escalation.

**`derived_template_collision_gate` is a live example of D-06's "fixture exists to exercise error
paths"**: it raises `sphinx.errors.ExtensionError: typst: 1 output path collision(s):
'_template/index.typ'...` (a WR-01/CR-01-family collision guard), exits 2, and emits zero `.typ`
files. `[VERIFIED: this session]` Both exit status (2) and the empty file set are what the plan
must reproduce identically on both sides — not a build the plan should "fix" or exclude.

**Path-independence, measured directly — this removes the need for same-absolute-path building as
a hard requirement:**
```
$ sphinx-build -b typst citation_render_gate/ /path/A     # first path
$ sphinx-build -b typst citation_render_gate/ /path/B     # second, different path
$ sphinx-build -b typst citation_render_gate/ /longer/nested/path/C  # different path length
$ diff -rq A B; diff -rq A C; sphinx-build again into A   # rebuild in place
```
Result in every comparison: **only `.doctrees/environment.pickle` differs.** Every `.typ` file
(`index.typ`, `master.typ`, `second.typ`, `_template/typst/base.typ`) hashes identical across all
three builds, regardless of output path or rebuild. `[VERIFIED: this session, sha256sum per file]`
**Recommendation:** the leg (d) comparison should hash only `*.typ` files (or explicitly exclude
`.doctrees/`), not the whole output tree — `.doctrees/*.pickle` is Sphinx's internal incremental
cache and is expected to differ by path/timing on both sides regardless of the typing change, and
including it in the byte-identity check would produce a false failure unrelated to QUA-12.

**How the test suite normally builds these fixtures, vs. the bare CLI build D-05 specifies:** zero
hits for `confoverrides=` across `tests/*.py` — the suite drives fixtures through
`sphinx.testing.util.SphinxTestApp` / the `pytest.mark.sphinx` plugin, with no per-test config
override for any of these 167 conf.py projects. `[VERIFIED: this session, grep]` This means a bare
`sphinx-build -b typst <fixture-dir> <outdir>` (D-05's own build command) reproduces exactly what
each fixture's own `conf.py` declares — there is no config drift between "how tests normally build
it" and "how leg (d) builds it" to reconcile.

#### Leg (e) — mypy string-identity

```
$ uv run mypy typsphinx/ 2>&1
Success: no issues found in 9 source files
```
Confirmed **identical on stdout** before conversion (pristine base via `git stash`) and after
(converted working tree), and stable across a warm `.mypy_cache` and `--no-incremental`.
`[VERIFIED: this session, both trees]`

**Capture hazard, measured directly:** `uv run`'s own package-rebuild chatter
(`Building typsphinx @ file://...`, `Uninstalled 1 package...`, `Installed 1 package...`) goes to
**stderr**, not stdout:
```
$ uv run mypy typsphinx/ >stdout.txt 2>stderr.txt
stdout.txt: "Success: no issues found in 9 source files"
stderr.txt: "   Building typsphinx @ file://...\n      Built typsphinx @ ...\nUninstalled...\nInstalled..."
```
`[VERIFIED: this session]` The plan's string-identity comparison should capture and compare
**stdout only** (`uv run mypy typsphinx/ 2>/dev/null`, or redirect stderr to a separate file it
does not compare) — otherwise a spurious "output differs" would fire purely from uv's own
sync-noise timing/package-count text, which has nothing to do with mypy or the typing rewrite.

### Same-Interpreter Mechanism (constraint 6)

```
Main checkout .venv/pyvenv.cfg:      home = /nix/store/.../python3-3.13.13/bin, version_info = 3.13.13
Fresh worktree (uv sync --extra dev --extra docs, no --python): version_info = 3.14  (Python 3.14.4)
Fresh worktree (uv sync --extra dev --extra docs --python 3.13): version_info = 3.13.13
                home = /nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin
                (identical path to the main checkout's interpreter)
```
`[VERIFIED: this session, .venv/pyvenv.cfg read directly in three trees]` — `uv python list` shows
this exact nixpkgs `cpython-3.13.13` registered as a discoverable interpreter, and `uv sync
--python 3.13` (or `3.13.13` for full precision) resolves to it rather than downloading or
preferring the newer cached `3.14.4`. **Recommendation:** every worktree in this phase — the
pre-conversion base worktree and the conversion/post-flip worktree alike — should run
`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs --python 3.13.13`,
which both (a) satisfies constraint 6's "same interpreter on both sides" by construction (both sides
pin the identical version string) and (b) happens to match the main checkout, so a `.venv/pyvenv.cfg`
comparison against the main checkout is also a valid sanity check.

mypy: since neither the conversion plans nor the flip plan touch `pyproject.toml`'s dependency
specifiers or `uv.lock` (only the `[tool.ruff.lint] ignore` array), a fresh sync on both sides from
the *same* `uv.lock` resolves the *same* mypy (`2.3.1`) automatically — the main checkout's stale
`2.1.0` is out of scope (already so per REQUIREMENTS.md's Out of Scope table) and does not need
reconciling for this phase's own gates, only avoided as the tool doing the actual measurement.

**The 2026-09-12 libz/Pillow sandbox hazard is resolved, re-confirmed fresh this session:**
```
$ uv run python -c "import PIL._imaging; print('PIL._imaging OK')"
PIL._imaging OK
```
`[VERIFIED: this session, fresh worktree, uv-managed CPython 3.14.4, inside the FHS sandbox]` — the
fix recorded at `.planning/milestones/v0.9.3-phases/64-fhs-wrapper-and-command-shims-in-flake-nix/
64-LIBZ-FIX-EVIDENCE.md` holds; this is not a live risk for Phase 70's docs/pytest gates.

### Base-side materialisation (Claude's Discretion item)

Both options work, provided each side gets its **own** `uv sync`:

- **`git worktree add --detach <scratch> <PHASE_BASE_SHA>`** — git-native, supports `git diff`/
  `git show` directly against the base tree, matches this project's existing worktree-isolated
  execution convention (`CLAUDE.md` § Worktree-isolated execution). **Recommended** for this
  reason alone (no functional advantage measured either way beyond convention-fit).
- **`git archive <PHASE_BASE_SHA> | tar -x -C <scratch>`** — also works, confirmed this session:
  a plain (non-git) directory, `uv sync --extra dev` inside it, and the resulting editable finder's
  `MAPPING` dict points at the archived directory itself, not the main checkout. `pyproject.toml`'s
  `version = "0.9.2"` is a static field (no `setuptools_scm`), so the absence of `.git` metadata
  does not block the build. `[VERIFIED: this session]`

**The hazard this discretion point exists to avoid, demonstrated directly:** the main checkout's
own editable finder hardcodes an absolute path:
```
$ grep MAPPING .venv/lib/python3.13/site-packages/__editable___typsphinx_0_9_2_finder.py
MAPPING: dict[str, str] = {'typsphinx': '/home/yuta/Documents/typsphinx/typsphinx'}
```
`[VERIFIED: /home/yuta/Documents/typsphinx/.venv/lib/python3.13/site-packages/__editable___typsphinx_0_9_2_finder.py:9, read this session]`
If a base-side measurement ever runs `import typsphinx` using the **main checkout's** interpreter/
site-packages (rather than a `uv sync`'d copy of its own), it silently resolves to the main
checkout's live files — not the archived/worktree base snapshot, and not necessarily even the
pristine base commit if the main checkout has local edits. Always `uv sync` (or worktree-provision)
independently on the base side; never reuse another tree's `.venv`/site-packages for a "base"
measurement.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Detecting remaining `Dict`/`List`/`Set`/`Tuple`/`Iterator` usages | A custom grep/regex sweep | `ruff check . --select UP006,UP035` | AST-aware; correctly ignores `ast.Dict`, docstring prose ("List of directories"), and any other non-typing occurrence a regex would false-positive or false-negative on |
| Rewriting the 94 mechanical usages | Hand-editing each annotation | `ruff check . --fix` | Deterministic, already the tool this project trusts for every other lint fix; confirmed to leave exactly the one documented `__init__.py` survivor |
| Proving "nothing else changed" | A committed diff-review checklist or a new pytest test asserting AST shape | The masked-AST `sk()` one-liner run inline inside the plan's verify block (per this project's evidence convention: verbatim transcripts, no new committed script/test) | A new test would itself change the pytest collected count, breaking leg (b) |

**Key insight:** every tool this phase needs (`ruff`, `black`, `mypy`, `pytest`, `sphinx-build`) is
already pinned and already the project's standard gate. There is no library gap here — the risk is
entirely in evidence bookkeeping (provisioning consistency, stdout/stderr separation, path handling
in the corpus comparison), not in missing tooling.

## Common Pitfalls

The milestone-level `PITFALLS.md` already covers Pitfalls 1–5 (the `__init__.py` survivor,
`CLAUDE.md`'s self-contradiction, the multi-location sync hazard, the stale todo file list, and the
dependabot ruff-bump risk) in full and does not need restating. This session found four additional,
narrower pitfalls specific to the evidence half:

### Pitfall 6: an in-place-emptied `ImportFrom` node in the mask produces a false hash mismatch
**What goes wrong:** masking an import line by setting `node.names = []` / `node.module =
"<MASKED>"` while leaving the (now-empty) node at its original position in the module body still
participates in `ast.dump()`'s output via its position relative to sibling statements. Three of the
ten files change an import line's *position or existence* (not just its content): the `Iterator`
import moves earlier (alphabetical resort after splitting `typing`/`collections.abc`), and two files
lose the import line entirely (no typing import needed after conversion). All three produced a
`DIFFER` with an in-place mask, before switching to node deletion.
**Why it happens:** `ast.NodeTransformer.visit_ImportFrom` returning a mutated (but still-present)
node keeps that node in the body list; only returning `None` removes it.
**How to avoid:** `return None` from `visit_ImportFrom` when the module matches, confirmed to
produce `EQUAL` on all 10 files this session.
**Warning signs:** exactly the files whose typing-import line moves or vanishes (not the files where
it merely shrinks in place, e.g. `Any, Dict` → `Any`) show a spurious `DIFFER`.
**Phase to address:** Phase 70, when the plan implements the leg (a) verify block — pilot on
`translator.py` (a shrink-in-place case, would pass even with the buggy mask) **and** on
`tests/test_include_ledger_removal_gate.py` or `tests/test_bundle_layout_sweep_gate.py` (a
move/vanish case, which the buggy mask fails) before trusting the harness.

### Pitfall 7: `uv run`'s sync/rebuild noise lands on stderr and looks like a diff if captured on the wrong stream, and can also silently touch the main checkout
**What goes wrong:** `uv run <tool>` in a tree whose source changed since the last sync triggers an
automatic editable-package rebuild, printing `Building typsphinx @ file://...` /
`Uninstalled/Installed N package(s)` — on stderr for `mypy`, confirmed this session. If a plan
naively pipes `2>&1` into its string-identity comparison, that chatter becomes part of the compared
string and produces a false "output differs." Separately, running `uv run <tool>` even for a
read-only check (e.g. `ruff --version`) inside the **main checkout** can trigger this same
rebuild/reinstall cycle; this session observed it and confirmed it did not modify `pyproject.toml`/
`uv.lock` (`git status --short` clean afterward), but a plan should not assume that's always benign
— avoid running `uv run` for read-only checks in the main checkout at all, and prefer worktrees.
**Why it happens:** `uv run` implicitly re-syncs a stale environment before invoking the tool;
uv writes its own progress messages to stderr.
**How to avoid:** capture and compare stdout only for the mypy leg; avoid `uv run` in the main
checkout except through the project's own documented worktree-isolated flow.
**Warning signs:** a "mypy output differs" failure whose diff consists entirely of `Building`/
`Uninstalled`/`Installed` lines rather than any mypy diagnostic.
**Phase to address:** Phase 70's leg (e) verify block (stream separation); general executor
discipline for the rest of the phase (avoid ad hoc `uv run` in the main checkout).

### Pitfall 8: the docs clean-build diff is not confined to `api/…` pages — `sphinx.ext.viewcode` pages differ too
**What goes wrong:** DOC-23/D-11 expects every differing hunk of the clean HTML build to sit under
`api/…`. A real base-vs-converted clean build (`rm -rf docs/_build` both sides) instead shows **five**
differing files: `api/index.html` plus four `_modules/typsphinx/{builder,template_engine,
translator,writer}.html` pages — `sphinx.ext.viewcode`'s syntax-highlighted mirror of the source
itself, which naturally differs wherever the source text differs (confirmed: the diff is exactly the
`Tuple`→`tuple` / `from typing import Any, Tuple`→`from typing import Any` text, syntax-highlighted).
**Why it happens:** `docs/source/conf.py:38` enables `sphinx.ext.viewcode`, which this milestone's
scope discussion did not have in view when D-11 was worded.
**How to avoid:** see **Contradictions With Locked Decisions** — this is reported to the owner as an
amendment candidate for D-11's wording, not silently resolved either way by the planner.
**Warning signs:** a plan's D-11 classification script that hard-codes an `api/` path prefix filter
will either wrongly ignore these four files (under-classifying) or wrongly fail the phase on them
(over-strict) depending on which way it's written.
**Phase to address:** Phase 70's DOC-23 evidence write-up; needs an owner decision before the
DOC-23 acceptance check is finalized (see Open Questions).

### Pitfall 9: not every docs-diff hunk is a literal `Dict`→`dict` word substitution
**What goes wrong:** a converted `Set[str] | None` renders, before conversion, as `Optional[Set[str]]`
in the API reference (a different **textual shape**, not just a different word) and after
conversion as `set[str] | None` (matching the source spelling). A D-11 classification check that
looks for a literal substring match (e.g. `s/Dict\[/dict[/`) between the two diff sides would fail
to explain this hunk even though it is entirely explained by the `Set`→`set` rename.
**Why it happens:** `typing.Set[str] | None` evaluates, at runtime, to a `typing.Union` object
(because `typing._GenericAlias.__or__` returns `typing.Union[...]`), which Sphinx's
`stringify_annotation` renders as `Optional[X]`; `set[str] | None` evaluates to a native
`types.UnionType` object, rendered as `X | None`. Same logical type, different runtime object,
different formatter branch.
**How to avoid:** D-11's classification step should be done by a human/owner reading each hunk
against "does this trace to one of the ten converted files' annotations," not by an automated
literal-substring matcher — the CONTEXT already frames D-11 this way ("Each differing hunk...must
trace...Any hunk that does not trace this way goes to the owner"), so this finding just confirms
that framing is necessary, not decorative.
**Warning signs:** a hunk whose before/after text share no common substring at all (unlike the
simple `Dict[`→`dict[` cases) but both sides name the same parameter/field.
**Phase to address:** Phase 70's DOC-23 write-up — flag this specific shape in the evidence file so
whoever reads the diff isn't surprised by it.

## Runtime State Inventory

Not applicable — this is not a rename/refactor/migration phase in the "runtime state" sense (no
datastore keys, no live service config, no OS-registered state, no secret/env-var renames, no
build-artifact rename). It is a pure source-code syntax rewrite. The one build-artifact-adjacent
fact worth recording: the editable-install finder (`__editable___typsphinx_0_9_2_finder.py`)
regenerates itself on every `uv sync`/rebuild and needs no manual attention across this phase — its
`MAPPING` always points at whichever tree it was last synced in, confirmed this session for both
the main checkout and a fresh worktree/archive.

## Code Examples

### Full conversion command sequence, re-verified this session end to end

```bash
# 1. Remove the two ignore lines + comments from pyproject.toml (Wave 2 plan only).
# 2. One fix pass:
uv run ruff check . --fix --statistics
#   Observed this session: "Found 115 errors (113 fixed, 2 remaining)."
#   The 2 remaining are always both on typsphinx/__init__.py:15 (1 UP035 + 1 F401).
# 3. Hand edit (the one and only manual line edit):
#    typsphinx/__init__.py:15  "from typing import Any, Dict"  ->  "from typing import Any"
# 4. Confirm zero remaining, matching CI exactly:
uv run ruff check .
#   Observed this session: "All checks passed!"
# 5. Confirm no reformatting follows:
uv run black --check --diff .
#   Observed this session: "All done! ... 355 files would be left unchanged."
```

### Masked-AST leg (a) verify-block shape (adapt the `sk()` function above)

```bash
# Inside an automated <verify> block, per this project's Phase 68 idiom:
sk() { uv run python -c '<the Mask class + sk() from above, reading stdin>'; }
[ "$(sk < typsphinx/translator.py)" = "$(git show "$B:typsphinx/translator.py" | sk)" ] && ...
```

### Safe pytest-collect-count extraction

```bash
uv run pytest --collect-only -q 2>&1 | grep -oE '[0-9]+ tests? collected' | grep -oE '^[0-9]+'
```

### mypy string-identity capture (stdout only)

```bash
BEFORE=$(uv run mypy typsphinx/ 2>/dev/null)
# ... conversion happens ...
AFTER=$(uv run mypy typsphinx/ 2>/dev/null)
[ "$BEFORE" = "$AFTER" ]
```

## State of the Art

Not applicable in the usual "old library vs. new library" sense. The one relevant "old vs. new"
axis is annotation syntax itself:

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|---------------|--------|
| `typing.Dict`/`List`/`Set`/`Tuple` generic aliases | PEP 585 builtin generics (`dict`/`list`/`set`/`tuple`) | Python 3.9 (PEP 585); this codebase's floor has been 3.12+ since v0.5.0 | No runtime behaviour difference for any pattern used in this codebase (confirmed: no `isinstance`/`get_type_hints`/`__annotations__` introspection anywhere); the only observable difference is the rendered API-reference type text and, subtly, whether a following `| None` renders as `Optional[X]` or `X | None` (Pitfall 9 above) |
| `typing.Iterator` | `collections.abc.Iterator` | Also available since 3.9+; `typsphinx/builder.py:11` already uses the new form | Same import-source change; zero behaviour difference |

**Deprecated/outdated:** `typing.Dict`/`List`/`Set`/`Tuple`/`Iterator` themselves are not removed
from Python — they remain available and functionally aliased — this milestone is a lint-driven
style modernization, not a compatibility fix.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The pre-existing `derived_template_collision_gate` fixture's `exit=2` / zero-`.typ` shape is representative of every other error-path fixture in the 167-project corpus (i.e., no fixture produces a *partial* `.typ` write before failing). | Leg (d) | If a different fixture emits some `.typ` files and then fails, D-06's "record exit status and whatever `.typ` it emitted" framing already covers that case — no plan change needed, just don't assume every failing fixture emits zero files |
| A2 | `--extra dev --extra docs` is sufficient to reach zero test skips project-wide (only spot-checked on `test_changelog_page_gate.py`, not every skip in the 1548-test suite). | Leg (b) provisioning | A different, unrelated skip elsewhere could still legitimately differ by platform (e.g. a Windows-only test) — that would not be a typing-rewrite regression; the plan should read *why* any skip-count mismatch occurs before treating it as a QUA-12(b) failure |
| A3 | A cold `@preview` package cache (network fetch) was not exercised this session — the local cache at `~/.cache/typst/packages/preview` was already warm, so the docs-pdf build's network dependency (or lack thereof) in a fresh CI-like environment is unmeasured here. | Docs Build Findings | If the executing environment's cache is cold, the first `docs-pdf` build could need network access; this is a pre-existing, cross-milestone gap (v0.9.3 WR-01), not new to this phase |

## Open Questions

1. **Does D-11's "must sit in an API-reference page (`api/…`)" wording need amending to admit the
   four `_modules/typsphinx/*.html` viewcode pages, or should the plan instead exclude viewcode
   pages from the docs-diff comparison entirely (build with `viewcode_enable_epub`/disable
   `sphinx.ext.viewcode` for the comparison only)?**
   - What we know: the four pages differ by exactly the same text the source itself changed
     (syntax-highlighted), so they trivially satisfy D-11's *substance* ("explained by a
     Dict/List/Set/Tuple rename") but not its literal *location* requirement.
   - What's unclear: whether the owner considers `_modules/` pages part of "the API reference" in
     spirit (they are reached from the API reference via "view source" links) or wants them
     excluded from DOC-23's scope entirely, the way `examples/` is excluded from leg (d) by D-07.
   - Recommendation: put this to the owner as a two-option choice — (a) amend D-11 to also admit
     `_modules/…` pages when their content is explained by the same annotation renames, or (b)
     scope DOC-23's HTML diff to exclude `_modules/` (documenting why) and keep D-11 exactly as
     worded for `api/…` alone. See **Contradictions With Locked Decisions** below; this is not
     re-decided here.

2. **Should the leg (d) corpus comparison exclude `.doctrees/` by convention, or should the
   executing plan build outside `docs/_build`-style paths that never generate a `.doctrees/`
   directory in the compared tree at all (e.g., a `-d <separate-doctree-dir>` flag)?**
   - What we know: `sphinx-build`'s `-d` option lets the doctree cache be written outside the
     output directory entirely, which would make "hash everything under the output dir" trivially
     correct without an explicit exclude rule.
   - What's unclear: whether the corpus comparison plan wants that extra flag or prefers the
     simpler "hash only `*.typ` files" filter this research already validated.
   - Recommendation: either works; the `*.typ`-only filter needs no build-command change, so it is
     the lower-risk default unless the plan author prefers keeping the `-d` separation for other
     reasons (e.g., simpler `diff -rq` invocations).

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| ruff | QUA-09/QUA-11 conversion + gate | ✓ `[VERIFIED]` | 0.16.6 (`uv.lock`-pinned) | — |
| black | Gate quartet | ✓ `[VERIFIED]` | `uv.lock`-pinned, no reformatting triggered | — |
| mypy | QUA-12 (e) | ✓ `[VERIFIED]` | 2.3.1 (`uv.lock`); main checkout's stale `.venv` reports 2.1.0, out of scope, avoid using it as the measuring tool | Fresh `uv sync` in each worktree resolves the lock's 2.3.1 |
| pytest | QUA-12 (b) | ✓ `[VERIFIED]` | pytest 9.1.1 (this session's worktree) | — |
| sphinx-build (`typst`/`typstpdf` builders) | QUA-12 (d), DOC-23 | ✓ `[VERIFIED]` | Sphinx 9.1.0, this project's own extension | — |
| `~/.cache/typst/packages/preview` (warm cache) | DOC-23's `docs-pdf` build | ✓ `[VERIFIED]` this session (cold-cache path unmeasured) | 9 packages cached incl. `codly`, `mitex`, `gentle-clues` | If cold: network fetch on first build (pre-existing cross-milestone gap, v0.9.3 WR-01) |
| `gh` CLi / GitHub API | SC#5's CI dispatch and job-conclusion reading | ✓ `[VERIFIED]` (`gh run view`, `gh workflow list`, `gh pr list` all functioned this session) | — | — |
| NixOS FHS shims (`typsphinx-fhs-run`) | every `uv`/`ruff`/`black`/`mypy`/`pytest`/`sphinx-build` invocation on this machine | ✓ `[VERIFIED]` (`grep -q typsphinx-fhs-run "$(command -v uv)"` passed) | — | — |

**Missing dependencies with no fallback:** none identified.
**Missing dependencies with fallback:** cold `@preview` cache (falls back to network fetch; not
observed this session).

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 9.1.1 (`uv.lock`-pinned), config in `pyproject.toml` |
| Config file | `pyproject.toml` (`[tool.pytest.ini_options]`, not separately re-read this session — unchanged by this milestone) |
| Quick run command | `uv run pytest tests/<one_file>.py -q` |
| Full suite command | `uv run pytest -q` (this session: 1547 passed, 1 skipped, ~125s) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| QUA-09 | Zero UP006/UP035 repo-wide | lint | `uv run ruff check . --select UP006,UP035` (expect empty) then `uv run ruff check .` (expect `All checks passed!`) | ✅ (tool-native, no fixture needed) |
| QUA-11 | Builtin generics/`collections.abc.Iterator`; no PEP 604 sweep; no `__future__`; `@preview` lines untouched | grep/diff | `grep -rn "from typing import.*\(Dict\|List\|Set\|Tuple\|Iterator\)" typsphinx/ tests/` (expect empty); `git diff --stat` restricted to `@preview`-bearing lines in `writer.py`/`template_engine.py`/`templates/base.typ` (expect empty) | ✅ |
| QUA-12 (a) | Masked-AST hash equality per converted file | unit (inline script, not a committed test) | the `sk()` verify-block shown in § Code Examples | ✅ (harness proven this session) |
| QUA-12 (b) | pytest collected+passed counts identical | integration | `uv run pytest --collect-only -q` + `uv run pytest -q`, both sides, same extras | ✅ |
| QUA-12 (c) | Zero pre-existing test-assertion edits | diff review | `git diff --stat -- tests/` restricted to the plan's own files; grep the diff for non-typing-named changed lines (expect empty) | ✅ |
| QUA-12 (d) | Byte-identical `.typ` corpus | integration (167-project bare `sphinx-build -b typst`) | for each of 167 `conf.py` dirs: `sphinx-build -b typst <dir> <out>`; hash every `*.typ` under `<out>`, compare exit code + file list + hashes both sides | ✅ (pilot proven this session, ~41s extrapolated full corpus per side) |
| QUA-12 (e) | mypy output string-identical | unit | `uv run mypy typsphinx/ 2>/dev/null`, compare stdout string both sides | ✅ |
| DOC-22 | `CLAUDE.md:75` ancestor-of-every-conversion-commit; no `todos/pending/` reference after the flip commit | git history | `git merge-base --is-ancestor <claude_md_commit> <each_conversion_commit>`; `git grep -n "todos/pending/2026-07-22-modernize" -- . ':!.planning'` (expect empty after the flip commit) | ✅ (both commands proven functional this session) |
| DOC-23 | Clean docs diff confined to API-reference type text | manual/diff review | `rm -rf docs/_build && sphinx-build -b html docs/source docs/_build/html-<label>` + `sphinx-build -b typstpdf ...`, diff both sides + a base-vs-base control | ✅ (base-vs-base control proven zero-diff outside `.doctrees/` this session) |

### Sampling Rate

- **Per task/plan commit (Wave 1, A–E):** `uv run ruff check .`, `uv run black --check .`, the
  plan's own leg-(a)/(c) checks for its files, full `uv run pytest -q` in the plan's worktree.
- **Per wave merge:** re-run the full gate quartet on the merged tree.
- **Phase gate (Wave 3):** all five QUA-12 legs, DOC-22's ancestor/grep checks, DOC-23's docs diffs
  with control builds, then the CI dispatch (SC#5) before `/gsd-verify-work`.

### Wave 0 Gaps

None — every command in the Phase Requirements → Test Map above is tool-native (`ruff`/`black`/
`mypy`/`pytest`/`sphinx-build`/`git`) and was proven functional this session against the real repo.
No new test file, fixture, or framework install is needed. (This is also load-bearing for QUA-12
(b): a new test file would itself change the collected count.)

## Security Domain

`security_enforcement` is enabled project-wide (`.planning/config.json`), so this section is
included per policy, but this phase has essentially no security surface to evaluate:

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-------------------|
| V2 Authentication | No | N/A — no auth surface touched |
| V3 Session Management | No | N/A |
| V4 Access Control | No | N/A |
| V5 Input Validation | No | Annotation-only change; no new input path, no new parsing |
| V6 Cryptography | No | N/A — no crypto touched |

### Known Threat Patterns for this stack

None applicable. Confirmed this session (re-verifying the milestone research's own "Headline
finding"): zero `isinstance()` checks against `typing.Dict`/`List`/`Set`/`Tuple`, zero
`get_type_hints`/`__annotations__` introspection, zero `cast(...)`, zero `TypeVar`, zero new
dependency, zero new config surface, zero new attack surface. The `app.add_config_value(...)` sites
in `typsphinx/__init__.py` already use lowercase builtin *runtime values* (`[list]`, `[dict]`) in
Sphinx's config-validation API — unrelated to `typing` annotations and untouched by this rewrite.

## Contradictions With Locked Decisions

> Per the reporting rules: these are reported, not re-decided. The orchestrator puts them to the
> owner.

### C1 — D-11's "must sit in an API-reference page (`api/…`)" is contradicted by a measured clean-build diff

**D-11 (CONTEXT.md) states:** "Each differing hunk of both docs diffs is classified. Each
differing hunk must sit in an API-reference page (`api/…`) and be explained by a
`Dict`/`List`/`Set`/`Tuple` → `dict`/`list`/`set`/`tuple` rename... Any hunk that does not trace
this way goes to the owner as a finding."

**Measured this session:** a real clean HTML build (`rm -rf docs/_build`, `sphinx-build -b html
docs/source <out>`) on the pristine base and on the fully-converted tree, diffed with
`diff -rq --exclude=.doctrees`, shows **five** differing files, not files confined to `api/…`:

```
html-run1/_modules/typsphinx/builder.html   vs  html-after/...   DIFFERS
html-run1/_modules/typsphinx/template_engine.html vs ...          DIFFERS
html-run1/_modules/typsphinx/translator.html vs ...               DIFFERS
html-run1/_modules/typsphinx/writer.html vs ...                   DIFFERS
html-run1/api/index.html vs ...                                   DIFFERS
```
`[VERIFIED: this session, base-vs-converted clean HTML build]`

Each of the four `_modules/` diffs is content-identical in *character* to the source diff itself
(e.g. `writer.html`'s diff is exactly `from typing import Any, Tuple` → `from typing import Any`
and `Tuple[str, ...]` → `tuple[str, ...]`, syntax-highlighted) — so the **substance** of D-11 (every
hunk explained by a converted-annotation rename) holds. Only the **literal path prefix** ("must sit
in `api/…`") does not, because `sphinx.ext.viewcode` (`docs/source/conf.py:38`) publishes these four
pages under `_modules/typsphinx/*.html`, a location D-11's wording did not anticipate.

**This is not re-decided here.** Two live options for the owner (see Open Questions #1): amend
D-11's location language to admit `_modules/…` pages when explained the same way, or scope DOC-23's
HTML diff to exclude `_modules/` and keep D-11 exactly as worded.

## Sources

### Primary (HIGH confidence — this session's own tool use)
- `uv run ruff check . --select UP006,UP035 --statistics/--output-format=concise/--fix`, `uv run
  black --check --diff .`, `uv run mypy typsphinx/ --no-incremental`, `uv run pytest
  --collect-only -q` / `-q`, all run in a scratch `git worktree add --detach` at `cbd448bf`
  (`gsd/v0.9.4-typing-modernization`'s tip at research time).
- The masked-AST `sk()` harness (this session's own Python), run against all 10 converted files,
  both the base (`git show HEAD:<path>`) and the scratch-converted working tree.
- `sphinx-build -b typst`/`-b html`/`-b typstpdf`, run on 5 piloted `tests/fixtures/*` projects and
  on `docs/source`, at three different absolute output paths and via rebuild-in-place, diffed with
  `diff -rq`/`sha256sum`.
- `git merge-base --is-ancestor`, `git grep -n "todos/pending/2026-07-22-modernize..."`,
  `git worktree add/remove/prune`, `git stash`, all run this session.
- `gh run view 34730969392 --json jobs`, `gh workflow list`, `gh pr list --state open/all` — live
  GitHub API reads this session.
- `.venv/pyvenv.cfg` read directly in three trees (main checkout, fresh worktree default, fresh
  worktree pinned to `--python 3.13.13`); `__editable___typsphinx_0_9_2_finder.py:9` read directly.
- `tests/test_authors_pipeline_stage_gate.py:513-515`, `typsphinx/template_registry.py:469`,
  `typsphinx/translator.py:126`, `typsphinx/builder.py:11`, `.github/workflows/ci.yml`,
  `tox.ini`, `docs/source/conf.py`, `pyproject.toml` — all read directly this session.

### Secondary (MEDIUM confidence)
- `.planning/research/SUMMARY.md`, `STACK.md`, `ARCHITECTURE.md`, `PITFALLS.md` — milestone-level
  research, HIGH confidence on its own terms, cited here rather than re-verified line-by-line
  except where this session's fresh measurement is what's reported.
- `.planning/ROADMAP.md` § "🚧 v0.9.4 — Typing Modernization (ACTIVE)" — binding constraints,
  read directly this session for the wave shape and SC wording.
- `.planning/milestones/v0.9.3-phases/68-documentation-follow-through-claude-md-tox-ini-flake-nix/
  68-TOX-EVIDENCE.md:248-326`, `68-02-PLAN.md:220-322` — prior-art harness shape, read directly.

### Tertiary (LOW confidence)
- None — every claim in this document is either tagged `[VERIFIED: ...]` against a command run
  this session, `[CITED: ...]` against a file read this session, or explicitly logged in the
  Assumptions table above.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new stack; every version/behaviour claim re-measured fresh this session
- Architecture (wave shape, evidence harness): HIGH — file-disjointness and the masked-AST harness
  both re-verified fresh, including a genuine bug found and fixed in the initial mask design
- Docs-diff findings (DOC-23/D-11): HIGH confidence in the *measurements*, but surfaces one
  **open contradiction with a locked decision** that needs an owner call before DOC-23's acceptance
  check can be written precisely (see Contradictions)
- Pitfalls: HIGH — every pitfall in this document is backed by a command run and its output shown

**Research date:** 2026-09-13
**Valid until:** ~7 days (fast-moving axis: dependabot can bump `ruff`/`mypy` mid-milestone per
ROADMAP constraint 4/PITFALLS.md Pitfall 5; re-run the fresh counts and version reads at execution
time regardless of this document's numbers)
