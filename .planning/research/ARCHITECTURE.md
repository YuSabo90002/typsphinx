# Architecture Research: v0.9.4 Typing Modernization (QUA-09)

**Domain:** mechanical typing-syntax refactor of an existing Sphinx-extension codebase (not a new system)
**Researched:** 2026-09-13
**Confidence:** HIGH (all claims below are measured against the working tree with `ruff`, `grep`, and file reads — not inferred from the todo's stale file list)

This is not a "system architecture" in the usual sense — there is no new component, no new data flow, no new external integration. The relevant "architecture" question is entirely about **build/phase decomposition and the ruff-config dependency graph**, because the change flips a repo-wide lint gate from green-with-ignore to green-without-ignore, and CI (`ruff check .`) has zero tolerance for a partial state. Sections below answer the five numbered questions directly, then give a build order.

## Measured Ground Truth (2026-09-13, ruff 0.16.6)

```
$ uv run ruff check . --select UP006,UP035 --output-format=json | <count by file>
42  typsphinx/translator.py
30  typsphinx/builder.py
12  typsphinx/template_engine.py
 9  tests/test_include_ledger_removal_gate.py
 6  tests/test_bundle_layout_sweep_gate.py
 4  tests/test_include_edge_derivation_unit.py
 4  typsphinx/template_registry.py
 2  tests/conftest.py
 2  typsphinx/__init__.py
 2  typsphinx/writer.py
--- total 113 (93 UP006 + 20 UP035, ruff's own --statistics agrees) ---
```

This exactly matches the milestone context's numbers and confirms the 2026-07-22 todo's file list is stale in two ways the milestone context already flagged: it omits `template_registry.py` (created after the todo was filed) and undercounts `writer.py` (the todo guessed writer.py "likely has none"; it has 2, both `Tuple`, at `typsphinx/writer.py:10` and `:284`).

**Import lines per source file** (the anchor edit site in each):

| File | Import line | Symbols imported |
|---|---|---|
| `typsphinx/__init__.py:15` | `from typing import Any, Dict` | `Dict` |
| `typsphinx/builder.py:13` | `from typing import Any, Dict, List, Set, Tuple` | all four |
| `typsphinx/template_engine.py:13` | `from typing import Any, Dict, List` | `Dict`, `List` |
| `typsphinx/template_registry.py:29` | `from typing import Any, Dict` | `Dict` |
| `typsphinx/translator.py:9` | `from typing import Any, Dict, List, NamedTuple, Tuple` | `Dict`, `List`, `Tuple` (leave `NamedTuple`, `Any`) |
| `typsphinx/writer.py:10` | `from typing import Any, Tuple` | `Tuple` |
| `tests/conftest.py:6` | `from typing import Any, Dict` | `Dict` |
| `tests/test_bundle_layout_sweep_gate.py:42` | `from typing import Dict, List` | both |
| `tests/test_include_edge_derivation_unit.py:25` | `from typing import Dict, List` | both |
| `tests/test_include_ledger_removal_gate.py:47` | `from typing import Dict, Iterator, Set` | all three — this is **the one `Iterator` migration** (→ `collections.abc.Iterator`, mirroring the pattern `typsphinx/builder.py:11` already uses: `from collections.abc import Iterator`, used at `builder.py:1594` `get_outdated_docs(self) -> Iterator[str]`) |

`typsphinx/builder.py` already imports `Iterator` correctly from `collections.abc` (line 11) alongside its stale `typing` import (line 13) — the two imports coexist today, which is itself proof that mixing both import styles compiles and runs fine; the "flip" changes nothing about how Python resolves these at runtime, only which name a given annotation binds to.

`pyproject.toml` ignore lines: `128` (`"UP035"`) and `129` (`"UP006"`), each with an inline comment pointing at the todo path.

---

## 1. Phase/plan decomposition

**One code phase, split into parallel per-file conversion plans, plus one small "flip" plan inside the same phase that must run last and touch no source file — followed by the existing close-prep-only phase.** Do not spread the conversion across multiple *phases*; spread it across *plans within one phase*, because the dependency is plan-to-plan, not phase-to-phase, and phases in this project's model are the unit the roadmap reasons about at a coarser grain than is needed here.

**Why "convert first under the ignore, flip last" and not "flip first, convert everywhere"**: with `UP006`/`UP035` still ignored, every intermediate merged state — after 1 file converted, after 5, after 9 — is lint-green by construction, because ruff simply never checks for the old spelling. `ruff check .` only starts caring about `Dict`/`List`/`Set`/`Tuple`/`typing.Iterator` the moment the two ignore lines are gone. So:

- **Ordering A (safe, recommended): convert-under-ignore, flip-last.** Waves 1..N rewrite `typsphinx/*.py` and `tests/*.py` files one-by-one or in small independent groups, with the ignore lines still in `pyproject.toml`. Every wave's merged state is green: the already-converted files pass because they use builtin generics (which `UP006`/`UP035` never flagged as *wrong* — the ignore only suppresses the migration *suggestion*, it does not forbid the modern spelling), and the not-yet-converted files pass because the ignore still suppresses the old-spelling warning. The final plan removes the two `pyproject.toml` ignore lines, re-runs `ruff check .` over the whole repo as its own gate, and requires zero `UP006`/`UP035` hits — if any file was missed, this plan fails loudly instead of merging a red CI.
- **Ordering B (also safe, more coupled): flip + convert atomically in one plan.** A single plan removes the ignore lines and rewrites every one of the 10 files in one commit. This is simpler to reason about (no interstitial state at all) but forecloses parallelism entirely — one plan, one wave, ~113 edits reviewed as one diff. Given the file list is disjoint and mechanical (see §2), this discards free parallelism for no correctness benefit.
- **Ordering C (unsafe, do not use): flip first, convert in later waves.** The instant the ignore lines are removed, `ruff check .` goes red for every unconverted file. If wave 1 only flips the ignore and wave 2+ do the conversions, the merged state between those waves is lint-red — and per the milestone's own worktree-merge model (`CLAUDE.md` § Worktree-isolated execution), each wave's merge is a real commit on the integration branch that CI matrices run against. A red intermediate state is exactly the failure mode the question asks to avoid.

**Recommended decomposition inside the one code phase** (mirrors the measured per-file split, which is already file-disjoint and requires no cross-file coordination):

| Plan | Wave | Files | Violations | Notes |
|---|---|---|---|---|
| Plan A | 1 | `typsphinx/translator.py` | 42 | Largest file (~2700 lines); independent of the rest |
| Plan B | 1 | `typsphinx/builder.py` | 30 | Also touches nothing else; note the existing `collections.abc.Iterator` import at line 11 stays untouched — only the `typing` import at line 13 changes |
| Plan C | 1 | `typsphinx/template_engine.py` + `typsphinx/template_registry.py` | 12 + 4 = 16 | Small enough to combine; both are template-layer files with no cross-import of the typing symbols in question |
| Plan D | 1 | `typsphinx/writer.py` + `typsphinx/__init__.py` | 2 + 2 = 4 | Trivial, combine to avoid a near-empty plan |
| Plan E | 1 | `tests/conftest.py` + `tests/test_bundle_layout_sweep_gate.py` + `tests/test_include_edge_derivation_unit.py` + `tests/test_include_ledger_removal_gate.py` | 2 + 6 + 4 + 9 = 21 | All four are test-only, independent of the `typsphinx/` plans and of each other; combine into one plan (or split further — each file is disjoint) since none is individually large |
| Plan F (flip) | 2, depends on A–E | `pyproject.toml`, `CLAUDE.md`, todo file move | 0 (verification-only) | Removes the two ignore lines, runs `ruff check . --select UP006,UP035` repo-wide expecting zero hits, rewrites `CLAUDE.md:75`, moves the todo `pending/` → `completed/` |

Plans A–E are wave 1 (fully parallel, zero file overlap — see §2). Plan F is wave 2, gated on all of A–E landing, and is the only plan permitted to touch `pyproject.toml`/`CLAUDE.md`/the todo file. This keeps the "ruff-config-flip dependency" as a single explicit edge in the plan DAG rather than an implicit ordering assumption.

The existing **final close-prep-only phase** (per `PROJECT.md` § Current Milestone: "Final phase is close prep only, unpublished") stays a separate phase after this one, unchanged in shape from v0.9.3's Phase 69 precedent — it does not touch `typsphinx/` or `tests/` at all, only CHANGELOG/version bookkeeping.

---

## 2. Parallel-worktree conflict analysis

**Two categories of file, cleanly separated:**

**Category 1 — per-file conversions (Plans A–E, wave 1).** These are disjoint by construction: `translator.py`, `builder.py`, `template_engine.py`, `template_registry.py`, `writer.py`, `__init__.py`, and the four `tests/*.py` files each appear in exactly one plan's `files_modified`. No two plans in wave 1 touch the same file, so ordinary GSD worktree-merge (each plan branches from the same base, edits its own files, merges back) produces no textual conflicts. The only shared *resource* is the ruff/mypy/pytest run each worktree performs locally per `CLAUDE.md` § Worktree-isolated execution (`uv sync --extra dev` + `uv run pytest`/`ruff`/`mypy`) — each worktree runs these against its own copy of the tree at its own branch point, so this is not a file conflict, just N independent CI-equivalent runs.

**Category 2 — the flip (Plan F, wave 2).** `pyproject.toml` and `CLAUDE.md` are each touched by **exactly one plan** in this proposed decomposition (Plan F), not two — so there is no direct two-plan collision on those files *if* the flip is isolated into its own single plan as recommended in §1. The risk the question is flagging materializes only under a different (worse) decomposition where, e.g., two different plans each try to edit `pyproject.toml`'s ignore list (one plan per ignore line) or where a conversion plan is also handed the CLAUDE.md rewrite "since it's touching typing-adjacent files anyway." Concretely, avoid:

- **Two plans both editing `pyproject.toml` `[tool.ruff.lint] ignore`** (e.g., one plan removing `"UP035"` at line 128 and another removing `"UP006"` at line 129) — this is the classic "disjoint lines, same file, same wave" merge hazard (per the project's own recorded lesson `disjoint-files-still-collide-at-merge.md`: even non-overlapping line edits to a shared list can produce a semantically-correct-looking merge that leaves one ignore line back in, or a comma/list-syntax break, if both plans regenerate the surrounding array). Removing both lines is a two-line, single-intent edit — keep it in one plan.
- **Two plans both editing `CLAUDE.md`** — one doing the QUA-09 line-75 rewrite and, independently, some unrelated plan touching the same "Conventions & gotchas" section (unlikely within this milestone, since only QUA-09 concerns typing, but the Phase 68 precedent shows CLAUDE.md edits are routinely bundled per-topic into single plans for exactly this reason — see `68-01-PLAN.md`'s `files_modified: [CLAUDE.md, ...]` pattern, one plan per prose-rewrite topic).
- **A conversion plan also moving the todo file** — keep `todos/pending/2026-07-22-...md` → `todos/completed/2026-07-22-...md` in Plan F only; it is a single-intent bureaucratic step tied to "the deferral is closed," which is only true once the flip has actually landed, not once any one file is converted.

No plan touches `tests/conftest.py` and any `typsphinx/*.py` file simultaneously except by cross-plan dependency (none needed — conftest fixtures don't import from `typsphinx/` typing symbols). No test file imports another test file's typing symbols. The only cross-file *semantic* link is `typsphinx/builder.py:11`'s existing `collections.abc.Iterator` import, which Plan E's rewrite of `tests/test_include_ledger_removal_gate.py:47` should mirror in spelling (`from collections.abc import Iterator`) for consistency, but there is no import-level coupling between the two files.

**Net conflict surface: zero file-level collisions if Plan F is the sole owner of `pyproject.toml`, `CLAUDE.md`, and the todo move, and Plans A–E are the sole owners of one `typsphinx/`/`tests/` file (or small disjoint group) each.**

---

## 3. Evidence architecture for "behaviour unchanged"

> **ORCHESTRATOR CORRECTION (2026-09-13, verified by grep after this file was written):** the
> paragraph below is wrong on its central fact. Phase 68 plan 02 **did** use a Python masked-AST
> hash: `68-TOX-EVIDENCE.md:248-326` records `masked AST hash (docstrings + assert messages masked)`
> for `tests/test_toolchain_config_gate.py` and `tests/test_pdf_render_gate.py`, current tree vs
> `git show BASE_68_02:…`, equal on both files; the automated verify blocks carrying the
> `ast.parse`/`ast.dump` code are at `68-02-PLAN.md:253` and `:305`. So there **is** prior art to
> reuse — its mask target (string constants / docstrings / assert messages) differs from this
> milestone's (annotation subtrees + the `typing` import line), but the harness shape (hash current
> tree vs `git show <base>:<path>`, require equality per file) is directly reusable. The
> normalization sketch later in this section remains a valid design; treat the "no pre-existing
> script" claim as retracted.

**What v0.9.3 Phase 68 actually did (correcting the milestone context's premise):** Phase 68 is a documentation-only phase (`CLAUDE.md`/`tox.ini`/`flake.nix` prose rewrites) — it contains no `ast.dump` or Python-AST hashing anywhere (`grep -rl "ast\." .planning/milestones/v0.9.3-phases/68-*` returns nothing). There is **no pre-existing "masked-AST-hash" script to reuse verbatim.** What Phase 68 *does* establish, and what generalizes directly, is a **masked-hash pattern** used to prove a file with both a real edit and untouched surroundings changed only where intended:

```
$ grep -vE '^[[:space:]]*(#|$)' flake.nix | sha256sum
```
(`68-FLAKE-EVIDENCE.md`) — strip comments and blank lines (the part expected to change: DOC-21 was a comment-only edit), hash the rest, and require the hash to match the pre-edit hash. This proves "every non-comment (behavior-relevant) line is byte-identical" without needing a semantic diff. `68-CLAUDEMD-EVIDENCE.md` uses the sibling pattern for prose: `awk` to isolate an untouched tail section, then `sha256sum` both sides.

**The QUA-09-shaped generalization of that pattern, for Python source:** mask out exactly the nodes expected to change (the annotation subtrees carrying `Dict`/`List`/`Set`/`Tuple`/`typing.Iterator`), normalize them to their builtin-generic equivalents, and hash what remains. Concretely, per converted file:

```python
import ast, hashlib

class AnnotationNormalizer(ast.NodeTransformer):
    """Rewrite typing.Dict/List/Set/Tuple subscripts and bare names to their
    builtin-generic equivalents, in place, on a parsed AST — so a pre-change
    and post-change parse of the "same" file collapse to one canonical form."""
    _MAP = {"Dict": "dict", "List": "list", "Set": "set", "Tuple": "tuple"}

    def visit_Name(self, node):
        if node.id in self._MAP:
            node.id = self._MAP[node.id]
        return node

    def visit_Attribute(self, node):
        # typing.Dict[...] form, if any survive as typing.Dict rather than a
        # bare imported name
        self.generic_visit(node)
        if isinstance(node.value, ast.Name) and node.value.id == "typing" and node.attr in self._MAP:
            return ast.copy_location(ast.Name(id=self._MAP[node.attr], ctx=node.ctx), node)
        return node

def normalized_dump(source: str) -> str:
    tree = ast.parse(source)
    AnnotationNormalizer().visit(tree)
    ast.fix_missing_locations(tree)
    return ast.dump(tree, annotate_fields=True, include_attributes=False)

def normalized_hash(path: str) -> str:
    return hashlib.sha256(normalized_dump(open(path).read()).encode()).hexdigest()
```

Run `normalized_hash()` on each of the 10 files at the pre-conversion commit (via `git show <base>:<path>`) and again on the post-conversion working tree; require equality per file. Additionally strip the now-dead `from typing import ...` line itself before parsing (or accept that the `Import`/`ImportFrom` node changes and exclude those node types from the dump, since the import statement is expected to change and isn't part of the "behavior" claim). This is a direct AST-level descendant of the same masking idea Phase 68 used at the text level — "mask the part that's supposed to change, hash the rest, require equality" — just moved from a line-based comment mask to a node-type/name-based annotation mask.

**What this proves:**
- The two ASTs are structurally identical everywhere except the deliberately-normalized annotation names and the import line — i.e., no logic, control flow, string literal, call, or non-annotation expression moved, was added, or was deleted.
- Combined with `ruff --fix`'s own determinism (94 of 113 hits are `[*]` autofixable — `ruff check --fix` already performs exactly this class of mechanical, single-name substitution, so preferring the autofixer over hand-editing wherever possible is itself part of the evidence story: autofix output is what the tool's own test suite already trusts, reducing "trust the executor's manual edit" to "trust `ruff --fix`'s well-known transform" for 83% of the hits), this closes almost the entire diff to a mechanical class the tool vendor already verifies.

**What this cannot prove, and what closes the remaining gap:**
- **Runtime object identity of the annotation itself.** `typing.Dict[str, Any]` and `dict[str, Any]` are *not* the same runtime object — the former is a `typing._GenericAlias`, the latter a `types.GenericAlias` (PEP 585). Nothing under `typsphinx/` or `tests/` evaluates `__annotations__`, calls `typing.get_type_hints()`, or does `isinstance()`/equality checks against these generic-alias objects (confirmed by grep — see §4), and none of the 10 files use `from __future__ import annotations` (confirmed by grep — meaning annotations *are* eagerly evaluated at class/def time in all 10 files today, both before and after the change, so this is not a laziness/order-of-evaluation shift either way). Because nothing inspects the alias objects, the AST-normalization proof plus this negative grep together are sufficient — the AST proof shows the code shape is unchanged, the grep shows the one semantically-different runtime artifact (the alias object) is never observed by anything that would notice the difference.
- **`sphinx_autodoc_typehints` rendering.** The milestone context itself already names this as "one visible side effect" (not a defect): `docs/source/api/index.rst`'s rendered API reference will show `dict[str, Any]` instead of `Dict[str, Any]`. The AST-hash proof does not — and should not — claim this doesn't change; it is an intentional, disclosed, cosmetic doc-rendering change, evidenced separately by a docs build diff if the plan wants to show it (not required by QUA-09's "runtime behaviour and emitted Typst output unchanged" framing, since docs rendering is neither runtime behavior nor Typst output).
- **Emitted `.typ` output identity.** The AST proof says nothing about `.typ` files; that needs its own evidence leg.

**Second evidence leg — emitted `.typ` output, reusing existing golden-fixture infrastructure.** `tests/` already contains dozens of `test_*_render_gate.py` modules (per `TESTING.md` § Test Types, "50+ gate tests") that assert exact Typst-syntax substrings or full-body output from `TypstTranslator.astext()`, plus real-`typst.compile()` acceptance gates (per `PROJECT.md` v0.6.0/v0.9.2 history) and committed byte-identical goldens (the same technique v0.9.1/v0.9.2 used — "POSIX output was proven byte-identical the way v0.9.0 proved it — by zero pre-existing test edits, measured rather than asserted"). For QUA-09 the correct instance of that pattern is: **run the full existing test suite unmodified** (per-file conversion plans must not edit any existing test assertion — a `git diff` restricted to `git diff --stat -- tests/` for the `typsphinx/`-only plans A–D must show zero hits, and for plan E, the diff to each converted test file must touch only the `typing` import line and the type-annotation occurrences, never an assertion string) and require the whole suite green, file-count and pass-count unchanged, mirroring the `COLLECT_BEFORE`/`COLLECT_AFTER` pytest-collection-count invariant Phase 68 used (`68-CLAUDEMD-EVIDENCE.md`'s `COLLECT_BEFORE_68_01`/`COLLECT_AFTER_68_01` = 1548 both times). Because annotations are never asserted on by any existing test (§4), an unmodified, fully-green suite at an unchanged collection count is direct behavioral proof, not just an absence-of-regression signal.

**Recommended combined evidence package per conversion plan:**
1. `git diff --stat` restricted to the plan's owned file(s), showing only import-line and annotation-token changes (no other line touched).
2. The AST-normalized-hash equality (pre vs. post) for each owned file, as a machine-checked gate.
3. `pytest --collect-only -q` count unchanged before/after (catches accidental syntax breakage or an accidentally-deleted test).
4. Full `uv run pytest` green, zero new failures, zero test-assertion edits (`git diff` on `tests/*.py` files outside the plan's own list must be empty).
5. `ruff check . --select UP006,UP035` count strictly decreasing by exactly the plan's file's violation count (e.g., Plan A: 113 → 71 after `translator.py`'s 42 are gone) — this is the direct, cheap, tool-native signal that the mechanical rewrite is complete for that file, checkable without waiting for the flip.
6. For Plan F only: `ruff check . --select UP006,UP035` returns zero hits repo-wide, then `ruff check .` (full, unrestricted) is green, `black --check .` is green, `mypy typsphinx/` is green.

---

## 4. Tests that could break for reasons other than typing

Grepped `tests/` for: reading typsphinx source text, asserting on annotation strings, `typing.get_type_hints`, `__annotations__`, and `Dict[`/`List[`/`from typing import` occurrences.

**No hits for the dangerous categories** — the searches for `get_type_hints`, `__annotations__`, and any `isinstance()` check against `typing.Dict`/`List`/`Tuple` all returned nothing in the entire repository (not just `tests/`). Nothing in this codebase introspects type annotations at runtime, so there is no test whose *pass/fail* depends on which spelling an annotation uses.

**Hits that are self-referential, not risk (the file's own type hints on functions inside the test/gate module — converting these is literally the milestone's own scope, and does not change what the gate function checks):**

| File:line | What it is | Risk to flag |
|---|---|---|
| `tests/conftest.py:6` (`from typing import Any, Dict`) and `:84` (`def sphinx_config() -> Dict[str, Any]:`) | conftest's own fixture return-type hint | None — fixture body unaffected; this file is in-scope for Plan E |
| `tests/test_bundle_layout_sweep_gate.py:42,87,105,112,153` | the sweep gate's own helper-function type hints (`EXCLUDED_SWEEP_PATHS: Dict[str, str]`, `_discover_policed_files() -> List[Path]`, etc.) | None — this gate sweeps `docs/source/`, `README.md`, `examples/` for `_template.typ`/`_write_template_file()` text (per its own docstring, "Policed scope... exactly docs/source/, README.md, and examples/... tests/ is deliberately NOT policed"); its search patterns have nothing to do with typing syntax, so rewriting its own hints changes nothing it checks |
| `tests/test_include_edge_derivation_unit.py:25,296` | `from typing import Dict, List`; `def _linear_chain(n: int) -> Dict[str, List[str]]:` | None — local test-helper hint, unrelated to what the test asserts about include-edge derivation |
| `tests/test_include_ledger_removal_gate.py:47,354,361,374,379,400,412` | `from typing import Dict, Iterator, Set`; several `ast.Dict`-**adjacent** but distinct usages | **Read carefully, do not confuse `typing.Dict` with `ast.Dict`.** This file also does `isinstance(node, ast.Return) and isinstance(node.value, ast.Dict)`-shaped AST inspection **in a different test file**, `tests/test_authors_pipeline_stage_gate.py:515` — that `ast.Dict` is the docutils/stdlib `ast` module's dict-literal AST node type, completely unrelated to `typing.Dict`, and **must not be touched** by any find-and-replace across the codebase. A naive `sed 's/Dict/dict/g'` sweep would corrupt `ast.Dict` into `ast.dict` (which does not exist) and silently break `test_authors_pipeline_stage_gate.py`. This is the single sharpest "breaks for a reason other than typing" trap in the whole conversion — flag it explicitly in Plan E's/any-plan's read-first and prohibit blind `sed`/global-replace; use `ruff check --fix` (which is AST-aware and only touches `typing`-imported names, not `ast.Dict`) or careful manual review of each hit. |

**Second-order risk — `pyproject.toml`/`CLAUDE.md` text-shape gates unrelated to typing but adjacent to the files Plan F touches:** `tests/test_toolchain_config_gate.py` parses `pyproject.toml` via `tomllib` and asserts on the `[project]`, `[project.optional-dependencies]`, and `[project.optional-dependencies].dev` tables (lines 318, 322, 326, 409, 413) and on `CLAUDE.md`'s `## Conventions & gotchas` heading text existing (line 164, cited as `"CLAUDE.md 'Conventions & gotchas'"` — this is a prose citation inside a docstring/message, **not** a mechanical `grep`/`sed` assertion on CLAUDE.md's line numbers). No test in the repo hardcodes a `pyproject.toml` line number or the ignore-list's length/contents, and no test hardcodes `CLAUDE.md:75`'s line number — confirmed by grep (`UP035|UP006|tool.ruff.lint.*ignore` → zero hits in `tests/*.py`). So Plan F's edits to `pyproject.toml`'s ignore list and `CLAUDE.md`'s prose are safe against `test_toolchain_config_gate.py` as long as the `[project]`/`[project.optional-dependencies]` tables and the `## Conventions & gotchas` heading text survive verbatim — which they do, since Plan F only touches the `[tool.ruff.lint] ignore` array and a different `CLAUDE.md` sentence.

**Conclusion:** the conversion is exceptionally low-risk for test breakage *except* for the one `ast.Dict` vs `typing.Dict` name collision in `tests/test_include_ledger_removal_gate.py`/`tests/test_authors_pipeline_stage_gate.py`, which must be handled by AST-aware tooling (`ruff --fix`) or manual review, never blind text substitution across the whole tree.

---

## 5. Where CLAUDE.md and pyproject.toml comments must change, and in which plan

**All of these land in Plan F (the flip plan), not in any per-file conversion plan**, because each is a *consequence* of the ignore lines being gone, not a precondition for any individual file's rewrite — and because executors read `CLAUDE.md` (and, implicitly, `pyproject.toml`'s comments) before acting, so leaving the old prohibition in place while conversion plans are still running is actually *useful*: it correctly describes the state of the tree in every wave-1 worktree except that each wave-1 executor's own plan overrides the general prohibition for its one file.

**Sites, verbatim, in this working tree today:**

1. `CLAUDE.md:75` — "**Python 3.12+ is required.** ruff intentionally ignores `UP006`/`UP035` (the `Dict`/`List` → `dict`/`list` upgrades) — this is a deliberate deferral, not a compatibility constraint; the modernization pass is filed at `.planning/todos/pending/2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md`. Don't 'modernize' typing imports until that todo lands." — this line **currently instructs any executor who reads it not to do the very thing this milestone asks for.** Any wave-1 plan (A–E) that has an executor read the whole of `CLAUDE.md` as ambient context (which `execute-plan.md`'s standard context-loading does) will see this sentence and, absent an explicit phase/plan-level override, could second-guess or halt. **Mitigation, concrete:** each conversion plan's own `<objective>`/`<context>` must explicitly state that this specific `CLAUDE.md:75` sentence is superseded for this plan's scope by the QUA-09 milestone goal (the way `68-01-PLAN.md` explicitly named which `CLAUDE.md` lines it was allowed to touch and why) — do not silently contradict CLAUDE.md; name the contradiction and its authority (the milestone's own `PROJECT.md` § Current Milestone) in the plan text. The line itself is rewritten only in Plan F, once the todo has actually landed.
2. `pyproject.toml:128-129` — the two ignore lines and their inline comments, each pointing at `.planning/todos/pending/2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md`. Removed together, in Plan F, only after every conversion plan (A–E) has merged — removing them earlier is exactly Ordering C from §1 and goes CI-red.
3. `.planning/todos/pending/2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md` → `.planning/todos/completed/2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md` — the move itself, in Plan F. Note the todo's own frontmatter (`file_path` list) is stale (missing `template_registry.py`, undercounting `writer.py`, naming no `tests/` files) — Plan F's rewrite of `CLAUDE.md:75` should not simply restate the todo's now-obsolete file inventory; it should describe completion in terms of the measured 113-violation/10-file inventory this research (and the milestone context) established, or simply state the deferral is closed without re-enumerating files (safest — avoids baking a second stale list into `CLAUDE.md`).
4. **No other file needs a comment update.** `tox.ini`, `flake.nix`, and `.github/workflows/ci.yml` do not mention `UP006`/`UP035` or typing modernization anywhere (confirmed: `grep -rn "UP035\|UP006"` across the repo returns only `pyproject.toml:128-129`) — this change has none of Phase 68's multi-file "toolchain-pin sync hazard" shape (that hazard is explicitly named in `CLAUDE.md`'s own "Toolchain-pin sync hazard" bullet for the *different* `tox-uv` pin, not for typing). QUA-09's sync surface is exactly two files: `pyproject.toml` and `CLAUDE.md`, both owned by Plan F alone.

**Executor-ordering consequence:** because `CLAUDE.md:75` is not rewritten until Plan F (wave 2), every wave-1 executor operates with the *old* prohibition still on disk, so plans A–E must carry their own explicit written authorization to proceed despite it (see item 1's mitigation) — this is a documentation lag the roadmapper should surface as a stated wave-1 plan requirement, not leave implicit.

---

## Suggested Build Order

```
Phase 70 (code phase — QUA-09 typing modernization)
├── Wave 1 (parallel, 5 plans, each names its own explicit CLAUDE.md:75 override,
│           none touches pyproject.toml/CLAUDE.md/the todo file):
│   ├── Plan A: typsphinx/translator.py            (42 violations → 0)
│   ├── Plan B: typsphinx/builder.py               (30 violations → 0; Iterator import at
│   │            line 11 stays as-is, only the typing import at line 13 changes)
│   ├── Plan C: typsphinx/template_engine.py +
│   │           typsphinx/template_registry.py     (12 + 4 = 16 violations → 0)
│   ├── Plan D: typsphinx/writer.py + __init__.py  (2 + 2 = 4 violations → 0)
│   └── Plan E: tests/conftest.py + the 3 gate
│               test modules                       (2 + 6 + 4 + 9 = 21 violations → 0;
│               explicit ast.Dict-vs-typing.Dict caution in read-first;
│               Iterator → collections.abc.Iterator in test_include_ledger_removal_gate.py)
│   Each plan's evidence: AST-normalized-hash equality (§3), unchanged pytest collection
│   count, zero test-assertion diffs outside its own files, per-file ruff UP006/UP035
│   count → 0, full green `uv run pytest`/`ruff check .`/`mypy typsphinx/` in its worktree.
│
└── Wave 2 (single plan, depends on A–E all merged):
    └── Plan F: pyproject.toml (remove lines 128-129), CLAUDE.md (rewrite line 75),
               todos/pending/... → todos/completed/...
               Gate: `ruff check . --select UP006,UP035` = 0 hits repo-wide (the
               decisive proof no file was missed), then full `ruff check .`,
               `black --check .`, `mypy typsphinx/`, `uv run pytest` all green.

Phase 71 (existing "close prep only, unpublished" phase — unchanged shape from
          v0.9.3 Phase 69: CHANGELOG bullet under ## [Unreleased], no version bump,
          no tag, no PyPI upload, no GitHub Release; touches no typsphinx/ or tests/ file)
```

This keeps every merged state lint-green (Ordering A from §1), makes the ruff-config flip a single explicit wave-2 dependency edge rather than an implicit assumption, isolates the only two shared-file edits (`pyproject.toml`, `CLAUDE.md`) into the one plan that owns them, and gives the roadmapper a ready-made wave/plan table rather than an undifferentiated "convert everything" phase.

---

## Sources

- Measured directly in this working tree: `uv run ruff check . --select UP006,UP035 --output-format=json` (2026-09-13, ruff 0.16.6) — per-file counts, HIGH confidence (primary/first-party measurement).
- `grep -rn` across `typsphinx/*.py` and `tests/*.py` for `from typing import`, `Iterator`, `get_type_hints`, `__annotations__`, `from __future__ import annotations`, `isinstance(...Dict...)` — HIGH confidence (exhaustive grep, not sampled).
- `.planning/milestones/v0.9.3-phases/68-documentation-follow-through-claude-md-tox-ini-flake-nix/68-FLAKE-EVIDENCE.md`, `68-CLAUDEMD-EVIDENCE.md`, `68-01-PLAN.md` — read directly; the "masked-hash" pattern generalized in §3 is this project's own precedent, HIGH confidence.
- `.planning/todos/pending/2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md` — read directly; used to identify its own staleness (its file list predates `template_registry.py` and undercounts `writer.py`), HIGH confidence.
- `CLAUDE.md`, `pyproject.toml` (this repo, current) — read directly for line numbers and exact text, HIGH confidence.
- `.planning/PROJECT.md` lines 33-71 (§ Current Milestone: v0.9.4 Typing Modernization) — HIGH confidence, primary source for scope/goal framing.
