# Pitfalls Research

**Domain:** Mechanical typing-annotation modernization (`typing.Dict/List/Set/Tuple` →
builtin generics) in a mature, gate-heavy Sphinx-extension codebase (typsphinx v0.9.4,
QUA-09, close-prep-only milestone)
**Researched:** 2026-09-13
**Confidence:** HIGH — every claim below is backed by a command run against this exact repo
(ruff 0.16.6, the same version pinned in `uv.lock`) or a file:line read, not by generic
UP006/UP035 advice. Scratch experiments ran in
`/tmp/claude-1000/-home-yuta-Documents-typsphinx/36f41dc4-a02c-4bd1-863a-edef50bd4bfd/scratchpad/pitfalls-probe/`
per the environment rules; no repository file was modified.

## Headline finding

This codebase has **none** of the runtime-hazard shapes the question asked me to hunt for.
Confirmed by grep across `typsphinx/*.py` and `tests/*.py`:

- `isinstance(x, Dict|List|Set|Tuple)` — **zero** real hits. The only match,
  `tests/test_authors_pipeline_stage_gate.py:515` (`isinstance(node.value, ast.Dict)`), is the
  **`ast` module's** `ast.Dict` node class (this test parses `template_engine.py`'s AST to prove a
  return-literal's key set), unrelated to `typing.Dict`. Ruff's AST-aware selector will not flag it
  and `--fix` will not touch it — but a *manual* text-grep audit (as opposed to `ruff check .
  --select UP006,UP035`) will surface it as false-positive noise. See Pitfall 4.
- `cast(...)` — **zero** hits anywhere in `typsphinx/` or `tests/`.
- Module-level type aliases (`Foo = Dict[str, Any]`) — **zero** hits.
- `TypeVar` — **zero** hits.
- `get_type_hints` / `__annotations__` introspection — **zero** hits.
- Quoted/forward-ref annotations spelling `"Dict[...]"` etc. — **zero** hits.
- `NamedTuple` field annotations **do** use `Tuple`/`List` (`translator.py:126`
  `xref: Tuple[str, str] | None` inside `class _ReferenceAnchorDecision(NamedTuple):`,
  `translator.py` `_LabelGuardStrings`) — these class-body annotations are evaluated eagerly at
  class-definition time (no `from __future__ import annotations` anywhere in the repo, confirmed by
  grep), but `ruff check typsphinx/translator.py --select UP006 --diff` rewrites
  `xref: Tuple[str, str] | None` → `xref: tuple[str, str] | None` cleanly with no other change
  needed — `tuple[str, str] | None` is legal PEP 604 syntax on 3.12+ and behaves identically. Not a
  hazard, but confirm it stays a straight `--fix` in execution rather than being hand-edited into
  something narrower.
- `app.add_config_value(...)` sites in `typsphinx/__init__.py:45-62` already use the **builtin**
  lowercase `list`/`dict`/`str`/`bool`/`type(None)` as runtime values in the `types=[...]` tuple
  (e.g. `app.add_config_value("typst_documents", _default_typst_documents, "html", [list])`,
  line 45). These are not typing annotations at all — Sphinx's config-validation API takes actual
  classes — so UP006/UP035 has zero interaction with them, and there is no plausible way a
  `ruff --fix` AST-based rewrite confuses them with `typing.List`/`typing.Dict` (case differs, and
  they are positional-argument values, not annotations). The only way to break this is a
  **careless manual regex substitution** (`s/List/list/`-style) instead of trusting `ruff --fix`
  — see Pitfall 6.

So the "runtime-hazard" half of this research question comes back clean. The actual risk in this
milestone is concentrated in five narrower, very concrete places below — each independently
verified.

---

## Critical Pitfalls

### Pitfall 1: `typsphinx/__init__.py`'s `Dict` import survives *every* form of `ruff --fix`, including `--unsafe-fixes`

**What goes wrong:**
`typsphinx/__init__.py:15` is `from typing import Any, Dict`, used only at
`typsphinx/__init__.py:29` as `def setup(app: Sphinx) -> Dict[str, Any]:`. Running
`ruff check . --select UP006,UP035 --fix` (or a bare `ruff check . --fix` with the two ignores
removed) rewrites the annotation to `-> dict[str, Any]:` correctly, which makes `Dict` unused —
but the import is **left in place**, and `ruff check .` afterward still reports it as **two**
separate, unresolved errors:
```
UP035 `typing.Dict` is deprecated, use `dict` instead   --> typsphinx/__init__.py:15:1
F401 `typing.Dict` imported but unused                  --> typsphinx/__init__.py:15:25
```
I verified this is not a one-off: I re-ran `ruff check . --fix` a second time (no change),
then `ruff check typsphinx/__init__.py --select F401 --unsafe-fixes --diff` (no diff produced —
not even offered as an unsafe fix), and only with **both** `--unsafe-fixes` **and** `--preview`
together does ruff produce the removal diff. Standard project tooling
(`ruff check .`, `tox -e lint` → `ruff check .`, CI's `lint` job) never passes `--preview`, so this
file's leftover import will **not** self-heal under any command this project actually runs.

**Why it happens:**
Per `ruff rule F401`'s own documentation: *"Fixes to remove unused imports are safe, except in
`__init__.py` files... Ruff will suggest an unsafe fix to remove third-party and standard library
imports... Applying fixes to `__init__.py` files is currently in preview."* Ruff treats any import
in a package `__init__.py` as a probable intentional re-export by default, and that whole code
path is gated behind `--preview`. `typsphinx/__init__.py` is exactly this shape (the package root),
so it is the **one file in the whole repo** where the standard fix workflow leaves a straggler.
Measured: of the 11 files with UP006/UP035 violations, this is the only one where a full
`ruff check . --fix` run does not converge to zero remaining errors.

**How to avoid:**
Do not treat "94/113 autofixable" as "run `--fix` once and you're done." After the autofix pass,
run a bare `ruff check .` (no `--select` filter, matching CI exactly) and require it to report
`All checks passed!` before moving on. For `typsphinx/__init__.py` specifically, plan for a
**one-line manual edit** — `from typing import Any, Dict` → `from typing import Any` — as an
explicit task, not an assumed side effect of the automated pass. Do not reach for
`--unsafe-fixes --preview` project-wide to "solve" this generically: that combination changes fix
behavior for every rule in the ruleset, not just this one import, and is not what CI or `tox -e
lint` will ever run, so a plan built around it would be unverifiable against the actual gate.

**Warning signs:**
`ruff check .` (bare, matching `tox -e lint` / CI's `lint` job) reports any remaining error after
the "bulk fix" step — especially anything mentioning `typsphinx/__init__.py:15`. `git diff
typsphinx/__init__.py` after the autofix step still shows `Dict` on the import line.

**Phase to address:**
The implementation phase (Phase 70) doing the actual rewrite — as its own explicit task/checklist
item, verified by a clean `ruff check .` run, not folded silently into "ran `ruff --fix`."

---

### Pitfall 2: `CLAUDE.md:75` tells every executor, verbatim, not to do the thing this milestone exists to do

**What goes wrong:**
`CLAUDE.md` is loaded into every agent's context automatically (as literally demonstrated by this
very research session — it arrived as a system-reminder before any task-specific instruction).
Line 75 currently reads: *"Python 3.12+ is required. ruff intentionally ignores `UP006`/`UP035`
(the `Dict`/`List` → `dict`/`list` upgrades) — this is a deliberate deferral, not a compatibility
constraint... **Don't "modernize" typing imports until that todo lands.**"* An executor agent
dispatched to the implementation phase will read this framed, in the harness's own words, as an
instruction that "OVERRIDE[s] any default behavior" and "MUST [be] follow[ed]... exactly as
written" — while its actual task is to edit exactly the files this line warns against touching.
This is a genuine self-contradiction baked into the project's own steering document, not a
hypothetical: the todo it points to (`.planning/todos/pending/2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md`)
is this milestone's entire content.

**Why it happens:**
CLAUDE.md was correctly written as a standing guard against *premature, un-planned* typing
modernization back when the deferral was still active (Phase 6, v0.5.0 floor bump). It was never
designed to be read mid-milestone by the very phase that lands the todo it references — the
document has no "unless you are the phase this todo authorizes" escape clause.

**How to avoid:**
The phase (or a preceding phase) doing the rewrite must update `CLAUDE.md:75` to drop the
prohibition **before or as its first task**, not last — sequence it ahead of the `Dict`→`dict`
edits so that by the time an executor is mid-rewrite, the file no longer contradicts the work. The
phase's own CONTEXT/PLAN should say explicitly, up front: "CLAUDE.md:75's prohibition is what this
milestone exists to retire; updating that line is in scope, not a violation of instructions." Don't
rely on an executor inferring this from PROJECT.md's Current Milestone section alone — CLAUDE.md is
the higher-authority document by the harness's own framing, so it must be the one that changes, and
the plan must say so explicitly rather than assuming the contradiction resolves itself.

**Warning signs:**
An executor pausing, asking for clarification, or refusing to touch `typing.Dict` usages citing
CLAUDE.md; or an executor editing the four originally-named files but skipping
`template_registry.py`/`writer.py`/`tests/` because CLAUDE.md's cross-reference to the (stale) todo
implicitly scoped it that way.

**Phase to address:**
Implementation phase (Phase 70), as an explicit early task, not the close-prep phase — the
contradiction is live for the entire duration the rewrite is in progress, not just at the end.

---

### Pitfall 3: this is the same "multi-location sync hazard" shape the project has already been burned by twice — a *fourth* location this time

**What goes wrong:**
CLAUDE.md documents two existing standing hazards of this exact shape: the `@preview` package
version triad (`writer.py` / `template_engine.py` / `templates/base.typ`) and the `tox-uv` pin
rationale (`pyproject.toml` / `tox.ini` / `flake.nix` / `CLAUDE.md` ×2 / a test docstring) — the
latter "drifted out of sync once already (Phase 65 → Phase 68)" per CLAUDE.md's own text. This
milestone creates a smaller but structurally identical hazard: the UP035/UP006 deferral rationale
is currently spelled out in **three** places that must move together —
`pyproject.toml:128-129`'s two `ignore` list comments, `CLAUDE.md:75`'s prose, and the todo file
itself (which must move from `todos/pending/` to `todos/completed/`). A partial edit (e.g.
removing the `pyproject.toml` ignore lines and their comments but forgetting `CLAUDE.md:75`, or
moving the todo without updating either) reproduces the drift.

**Why it happens:**
The reasoning for a deferred decision tends to get restated in every place someone might read it
in isolation (a linter config, a steering doc, a todo file) — which is good for discoverability but
means closing the deferral is a coordinated, multi-file edit, not a single-file diff. This project
has already measured that partial coordination fails (Phase 65 → 68 drift on the tox-uv rationale).

**How to avoid:**
Land the `pyproject.toml` ignore removal, the `CLAUDE.md:75` rewrite, and the todo's move to
`todos/completed/` in the **same commit** (mirroring how the `@preview` and `tox-uv` hazards are
each enforced by a same-commit discipline). The todo's own frontmatter already carries an
`audit_acknowledged: {milestone: v0.9.1, at: 2026-08-29}` block from when it was first surfaced —
closing it should also reflect that lineage rather than a bare file move.

**Warning signs:**
`pyproject.toml`'s ignore list loses `UP035`/`UP006` but `CLAUDE.md:75` still contains the
"Don't modernize" sentence in a later `git diff`/`git log` review; the todo file still exists under
`todos/pending/` after the phase claims completion.

**Phase to address:**
Implementation phase (Phase 70) — same phase as Pitfall 2's CLAUDE.md edit, same commit as the
`pyproject.toml` ignore removal.

---

### Pitfall 4: the todo's own file list is stale, and discovery-by-named-file silently under-scopes the change

**What goes wrong:**
The todo (`2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md`) names exactly four
`typsphinx/` files (`__init__.py`, `template_engine.py`, `builder.py`, `translator.py`) and zero
`tests/` files, with a note that `writer.py` "probably" doesn't need changes. Measured against
`ruff check . --select UP006,UP035 --statistics` (ruff 0.16.6, matching `uv.lock`) right now:

```
93  UP006  non-pep585-annotation      [*] fixable
20  UP035  deprecated-import          [-] not all fixable
Found 113 errors.
```

Per-file breakdown (`ruff check . --select UP006,UP035 --output-format=concise`):

| File | Count |
|------|-------|
| `typsphinx/translator.py` | 42 |
| `typsphinx/builder.py` | 30 |
| `typsphinx/template_engine.py` | 12 |
| `tests/test_include_ledger_removal_gate.py` | 9 |
| `tests/test_bundle_layout_sweep_gate.py` | 6 |
| `typsphinx/template_registry.py` | 4 |
| `tests/test_include_edge_derivation_unit.py` | 4 |
| `typsphinx/writer.py` | 2 |
| `typsphinx/__init__.py` | 2 |
| `tests/conftest.py` | 2 |

`template_registry.py` (4 violations, e.g. `template_registry.py:215`
`-> Dict[str, TemplateRegistryEntry]:`) postdates the todo's writing entirely — it didn't exist in
this form on 2026-07-22. `writer.py:284` (`edge_keys: Tuple[str, ...] = ()`) is a real usage the
todo explicitly hedged as "probably not applicable" and got wrong. Zero `tests/` files are named,
yet CI runs `ruff check .` over the whole repo (confirmed: no `[tool.ruff]` `exclude`/
`extend-exclude` entry carves out `tests/`), so `tests/` was always in scope by construction — 21
of the 113 violations (conftest.py + three gate test modules) live there. This exactly matches this
project's own standing lesson (see memory: "anywhere" success criteria must be checked by
repo-wide discovery grep, not by named files) — already the case here even before writing this
report, but worth re-grounding since the todo is the literal artifact this milestone closes.

I also confirmed the converse: `examples/`, `docs/`, and `scripts/` **do** fall inside
`ruff check .`'s scope (no exclude for them either; `ruff check examples/ docs/ scripts/` runs
clean with zero findings of any kind, not just UP006/UP035) and contain **zero**
`Dict`/`List`/`Set`/`Tuple` typing usages — so there is genuinely nothing to change there, but this
should be *measured* per-run, not assumed from this snapshot, since it's one more place a future
contributor could add a `typing.List` without anyone noticing.

**Why it happens:**
The todo was written against the codebase as it existed 2026-07-22; `template_registry.py` and the
now-affected test files were added or grew in the ~7 weeks since. Todos are point-in-time
artifacts; roadmaps/success-criteria that cite them by file list inherit that staleness.

**How to avoid:**
Success criteria and phase scoping must say "resolve every violation `ruff check . --select
UP006,UP035` reports at execution time" — never "resolve the violations in files X, Y, Z." Re-run
the statistics command as the first task of the implementation phase and treat its output, not the
todo's prose, as the worklist. This is already how PROJECT.md's Key Context frames it
("Discovery is by `ruff check . --select UP006,UP035`, not by the todo's list") — this pitfall
entry exists to carry that framing into the roadmap's literal success-criteria wording, since a
success criterion that lists files can silently regress to the todo's stale list if copied loosely.

**Warning signs:**
A plan or success criterion enumerates specific file paths for "files to modify" instead of "run
`ruff check . --select UP006,UP035`, expect zero output." A phase closes with `ruff check .`
still non-clean because `tests/` or `template_registry.py` were never re-discovered.

**Phase to address:**
Roadmap/success-criteria authoring, then re-verified at the start of the implementation phase
(Phase 70) by literally re-running the discovery command rather than trusting this document's
numbers as of 2026-09-13.

---

### Pitfall 5: dependabot is now on the `uv` ecosystem and *can* land a ruff bump mid-milestone, silently changing the measured violation count

**What goes wrong:**
v0.9.3 (Phase 66-67) moved dependabot from `pip` to `uv`, proven working on PR #138 which bumped
`ruff` to exactly `0.16.6` and updated `pyproject.toml` + `uv.lock` together in one commit that ran
full CI. Dependabot reads its config only from the default branch (`main`), so its PRs land against
`main`, not this milestone's branch directly — but v0.9.3's own history shows the milestone branch
merging `origin/main` in with `--no-ff` before its own close (`main`'s `cf3305ce` merged into the
milestone branch). If the same pattern repeats and a dependabot ruff-bump PR merges to `main`
mid-v0.9.4 and then gets pulled into the milestone branch, a newer ruff minor could add UP-rule
behavior changes (new detected shapes, or fixed false negatives) that make the "113 violations"
figure measured 2026-09-13 stale by the time a phase executes against it. CI's `lint`/`type`/`test`
jobs all run `uv sync --extra dev --locked` (confirmed in `.github/workflows/ci.yml`), which
enforces exactly what `uv.lock` pins — so the measured count is stable *as long as* `uv.lock` isn't
advanced underneath the phase.

**Why it happens:**
This is a direct, structural consequence of v0.9.3's own delivered feature (DEP-01..DEP-05) working
correctly — dependabot PRs against `main` are no longer dead on arrival, so they are more likely to
actually land during the lifetime of a subsequent milestone than they were before v0.9.3.

**How to avoid:**
Record the ruff version the "113" figure was measured against (0.16.6, `uv.lock`-pinned) explicitly
in the phase's own context, and re-run `ruff check . --select UP006,UP035 --statistics` immediately
before starting the rewrite work if any `main`-merge happened since. Do not hard-code "113" or the
per-file counts above as a literal pass/fail target in a success criterion — use "zero
UP006/UP035 findings" as the target, which is invariant to the exact count. If a dependabot PR does
bump ruff mid-milestone, treat a changed count as a signal to re-measure, not as evidence of a
mistake in earlier work.

**Warning signs:**
`uv.lock`'s pinned `ruff` version differs from `0.16.6` when a phase begins; `ruff check .
--select UP006,UP035 --statistics` reports a number other than 113/93/20 without any typing edits
having been made yet.

**Phase to address:**
Roadmap success-criteria wording (avoid hard-coded counts) plus a re-measurement step at the start
of the implementation phase (Phase 70).

---

## Technical Debt Patterns

Shortcuts that seem reasonable but create long-term problems in this specific change.

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|-----------------|------------------|
| Trusting the todo's named file list instead of re-running `ruff check . --select UP006,UP035` | Saves one command | Misses `template_registry.py` (4), `writer.py`'s real `Tuple` usage (2), and all 21 `tests/` violations — exactly the gap this milestone's own PROJECT.md already flags | Never |
| Running `ruff check . --fix` once and declaring the pass done | Fast | Leaves `typsphinx/__init__.py`'s `Dict` import (2 errors: UP035 + F401) permanently, since no default-mode re-run fixes it (Pitfall 1) | Never — always re-run bare `ruff check .` after fixing |
| Manual regex search/replace (`s/\bDict\b/dict/`) instead of `ruff --fix` | Feels more "controllable" | Risks touching prose (docstrings say "Dictionary of...", "List of...", "Tuple of author names" — see `template_engine.py:274,475,487,612,819`) that ruff correctly leaves alone, and offers no protection against missing a usage ruff would have caught via AST | Never for the annotation rewrite itself; fine only for the `CLAUDE.md`/`pyproject.toml` prose edits, which are not ruff's job anyway |
| Hard-coding "113 violations" as the literal success-criterion number | Sounds precise | Breaks silently if dependabot advances `ruff` mid-milestone (Pitfall 5) before the count is re-measured | Only as a *measured-on-date* citation, never as the pass/fail target itself |

## Integration Gotchas (tooling, not external services)

| Tool/Integration | Common Mistake | Correct Approach |
|-------------------|-----------------|-------------------|
| `ruff --fix` on `__init__.py` | Assuming `--fix` (or even `--fix --unsafe-fixes`) converges to zero errors everywhere | It doesn't for package `__init__.py` files without `--preview` (Pitfall 1) — plan a manual one-line fix for `typsphinx/__init__.py` specifically |
| NixOS `ruff`/`tox`/`mypy` shims (this machine only) | Invoking a tool binary directly, or expecting a scratch/experiment directory outside the checkout (no `.venv`) to resolve the shim | The shim walks up from CWD looking for `.venv/bin/<tool>`, stopping at the first `.git` it meets; a directory with neither fails loudly with exit 127 and a `typsphinx-shim:` message — reproduced directly during this research when probing a scratch copy with no `.venv` |
| `mypy typsphinx/` (tox `type` env, CI `type-check` job) | Assuming mypy provides a safety net for the `tests/` rewrite too | `tox.ini`'s `[testenv:type]` runs `mypy typsphinx/` only — `tests/conftest.py` and the three gate modules being rewritten have **no mypy coverage at all**; their correctness rests entirely on `ruff check .` being clean plus `pytest` passing |
| Dependabot on `uv` ecosystem | Assuming `uv sync --extra dev --locked` (CI's own install step) is immune to upstream ruff bumps | It's immune only until `uv.lock` itself changes; a dependabot PR updates both files together and CI runs on it (proven on #138) — see Pitfall 5 |

## Performance Traps

Not applicable — this is a pure static-annotation rewrite with zero runtime code-path changes.
No new hot loop, no new I/O, no new dependency. The project's own large-suite runtime concern
(`.planning/codebase/CONCERNS.md`'s "Large Test Suite Runtime") is unaffected by this milestone.

## Security Mistakes

Not applicable — no user input, no new dependency, no config-surface change. `app.add_config_value`
sites are untouched (Pitfall — see Headline finding). Confirmed no new attack surface: the diff
this milestone produces is limited to `typing` import lines and annotation subscripts.

## UX Pitfalls

Not applicable — PROJECT.md's own milestone goal states "runtime behaviour and emitted Typst output
unchanged"; there is no end-user-visible surface for this milestone except the one already named
below (rendered API docs typehint text).

## "Looks Done But Isn't" Checklist

- [ ] **`ruff check .` reports zero errors:** don't stop at "94/113 auto-fixed" — re-run the bare
      command (matching `tox -e lint` / CI exactly) and confirm `All checks passed!`, specifically
      checking `typsphinx/__init__.py` (Pitfall 1).
- [ ] **`mypy typsphinx/` green:** this does **not** validate the `tests/` half of the rewrite —
      mypy's target is `typsphinx/` only (`tox.ini` `[testenv:type]`). Verify the `tests/` rewrite
      by `pytest` passing, not by mypy.
- [ ] **"Behaviour unchanged" claimed:** PROJECT.md explicitly defers the *mechanism* for proving
      this to planning ("AST-level comparison, byte-identical `.typ` output, zero pre-existing
      test-assertion edits, or a combination") — verify a phase actually picked and executed one of
      these, not that tests merely "still pass" (passing tests alone don's prove the emitted
      `.typ`/PDF bytes are unchanged, only that assertions already in place still hold).
- [ ] **`CLAUDE.md:75` "modernization complete":** confirm the literal sentence "Don't 'modernize'
      typing imports until that todo lands" is gone, not merely appended-to or contradicted by a
      newer sentence nearby (Pitfall 2/3).
- [ ] **Todo moved to `todos/completed/`:** confirm the file actually moved (not copied, leaving a
      stale duplicate in `todos/pending/`), and that its `audit_acknowledged` (v0.9.1) provenance is
      preserved or referenced, not dropped.
- [ ] **`pyproject.toml`'s `ignore` list:** confirm **both** `"UP035"` and `"UP006"` lines (with
      their comments) are gone, not just one — they're separate list entries at
      `pyproject.toml:128-129`.
- [ ] **`typsphinx/__init__.py`'s import line specifically:** confirm `Dict` was removed from
      `from typing import Any, Dict`, not left as unused dead weight because "the linter didn't
      flag it after the last fix pass I ran" (it will still flag it — Pitfall 1 — unless separately
      hand-fixed).
- [ ] **Version/publish fields untouched:** `pyproject.toml`'s `version = "0.9.2"` must stay put;
      the CHANGELOG bullet goes under the existing `## [Unreleased]` — verify with `git diff
      pyproject.toml` that only the `ruff` ignore lines changed there, nothing version-related.

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|----------------|-----------------|
| `__init__.py` leftover `Dict` import (Pitfall 1) | LOW | One-line manual edit of the import statement; re-run `ruff check .` to confirm zero errors |
| CLAUDE.md contradiction stalls an executor (Pitfall 2) | LOW | Point the executor at PROJECT.md's Current Milestone section and this PITFALLS.md entry; resume with the CLAUDE.md edit sequenced first |
| Partial multi-location sync (Pitfall 3) | LOW–MEDIUM | `grep -rn "UP006\|UP035\|modernize.*typing" pyproject.toml CLAUDE.md .planning/todos/` to find the straggler location; fix in a follow-up commit, same phase |
| Under-scoped fix (missed `template_registry.py`/`writer.py`/`tests/`) (Pitfall 4) | LOW | Re-run `ruff check . --select UP006,UP035`; any nonzero output names the exact remaining files/lines to fix |
| Ruff bumped mid-milestone, count drifted (Pitfall 5) | LOW | Re-run the statistics command; treat the new count as authoritative, adjust nothing else — the fix mechanism (annotation rewrite) is identical regardless of count |
| `phase.complete` auto-flips a close-prep checkbox (see below) | LOW | `git diff` the requirements/CONTEXT files before committing the close; revert any auto-flip that contradicts a recorded CONTEXT decision, exactly as done 8 times previously in this project's history |

## Additional pitfalls (informational — not novel discoveries, but must not be dropped from this milestone's radar)

### `phase.complete` auto-flipping close-prep checkboxes against recorded decisions

This project has hit this **repeatedly and specifically at release/close-prep phases**: v0.9.3's
own MILESTONES.md entry documents `phase.complete` flipping REL-12 "for the eighth time" at that
milestone's close, requiring a manual revert and a SHA-256 re-match before the box could be
correctly checked. v0.9.4's close-prep phase carries the equivalent risk for whatever checkbox(es)
encode "no tag / no PyPI upload / no GitHub Release / `pyproject.toml` stays `0.9.2`" — decisions
this milestone has already locked (PROJECT.md: "Final phase is close prep only, unpublished...
same shape as v0.9.3"). Prevention: before committing the close, `git diff` the requirements file
and manually verify no auto-flip contradicted the CONTEXT decision, exactly as v0.9.3's close did.
**Phase to address:** the close-prep phase (likely Phase 71).

### ja translation `.po` catalog drift lands at the *next publish*, not during this milestone

`docs/source/api/index.rst` autodocs five modules (`typsphinx.builder`, `.pdf`, `.writer`,
`.translator`, `.template_engine`) via `sphinx_autodoc_typehints` with
`autodoc_typehints = "description"` (`docs/source/conf.py:114`) — confirmed no other docs-content
gate in this repo asserts on rendered typehint text (`grep` across `tests/*.py` for
`autodoc_typehints`/`Dict\[str, Any\]`/`api/index` found only unrelated fixture data, not a
docs-rendering assertion). After this milestone, the rendered signatures read `dict[str, Any]`
where they previously read `Dict[str, Any]`. This repo has **no local `locale/`/`.po` files** —
Japanese translation lives entirely in the separate `typsphinx-doc-translations` repository (no
git submodule checked out locally to inspect directly), synced only by that repo's own
`update-pin.yml`, which itself is dispatched only at a *published release* (per every prior
MILESTONES.md entry: "resyncs the ja catalogs" happens as part of the release-time pin-advance, not
mid-milestone). Since v0.9.4 publishes nothing (no tag), the msgid drift for these five modules'
autodoc-derived strings will not surface until whichever release eventually publishes this work —
this milestone should **not** attempt to touch the translations repo itself (out of scope, separate
repo, separate milestone history shows it's always handled by dispatching `update-pin.yml`, not a
hand-edit). Precedent for how prior milestones scoped a similar prose-changing docs edit: v0.6.3
Phase 27/28 paired a `lang` config-value addition with "a scope-limited ja gettext regeneration
that keeps all 12 pre-existing obsolete catalog blocks intact" — i.e., regenerate only what the
change touched, never a blanket resync that could touch unrelated already-fuzzy content. If this
milestone is ever amended to include a translations-repo touch, that is the pattern to follow, not
a wholesale resync. **Phase to address:** none in this milestone — flag as a known, deferred,
future-release consequence in the CHANGELOG bullet or close-prep notes, so the next publishing
milestone isn't surprised by it.

### Worktree-isolated execution: fresh venv may resolve a different CPython minor than the main checkout

Verified live on this machine: the main checkout's `.venv/pyvenv.cfg` reports
`version_info = 3.13.13` (nixpkgs-provided interpreter), while `uv python list` shows a
**locally cached** `cpython-3.14.4` already present at
`~/.local/share/uv/python/cpython-3.14-linux-x86_64-gnu/bin/python3.14`, and no `.python-version`
file exists anywhere in this repo to pin a worktree's fresh `uv sync --extra dev` to 3.13. Because
`requires-python = ">=3.12"` has no upper bound, a fresh worktree's `uv sync` is free to select
3.14 over 3.13 (uv prefers the newest satisfying interpreter it can find, and 3.14 is already
cached locally, making it cheaper to select than downloading 3.13). This is the same "fresh
worktree uses a different Python than the main checkout" hazard already logged in project memory,
now confirmed applicable to this exact repo state. `mypy`'s `python_version = "3.12"` config pin
(pyproject.toml:137) neutralizes the type-checking-target risk regardless of which interpreter runs
mypy — but `pytest`'s `filterwarnings = ["error::DeprecationWarning", "error::PendingDeprecationWarning"]`
(pyproject.toml:89-95) means a stdlib/dependency deprecation warning newly introduced under 3.14
(untested territory — CI's matrix is `['3.12', '3.13']` only) could turn into a hard test failure
that has nothing to do with the typing rewrite. This is unlikely to interact with the typing
rewrite itself (annotation-only change, no version-conditional code), but a worktree executor
seeing an unexpected RED must first compare `.venv/pyvenv.cfg`'s `version_info` between the main
checkout and the worktree before attributing the failure to the typing change (per the existing
CLAUDE.md "Interpreters may differ" guidance). Also confirmed: `ruff` itself is pinned to exactly
`0.16.6` by `uv.lock` regardless of interpreter, so ruff's own behavior does not vary across this
axis — only pytest/mypy's Python-version-sensitive paths could.

### CI-only defect classes: nothing new for this milestone, but the standing gate still applies

The project's own memory records three CI-only defect classes (locale-dependent test text, lint
authority in CI, Windows-only behaviour). This milestone's change (annotation rewrites only) has no
plausible interaction with locale text or Windows-specific paths — but the standing CI gate
(`.github/workflows/ci.yml`: `test` job matrix is `os: [ubuntu-latest, windows-latest,
macos-latest]` × `python-version: ['3.12', '3.13']`, plus separate `lint`/`type-check`/`coverage`
jobs) is still the actual authority. A locally-clean `ruff check .` + `mypy typsphinx/` +
`pytest` run under the maintainer's NixOS shell does not by itself prove the change is
Windows/macOS-safe; per this project's own established practice (every prior milestone's close
cites "15/15 checks green including both `windows-latest` and both `macos-latest` lanes" as
evidence, not local runs alone), the close-prep phase should still wait for and cite the actual CI
run rather than asserting cross-platform safety from a purely local pass.

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|-------------------|----------------|
| `__init__.py` residue survives `--fix` (Pitfall 1) | Implementation phase (Phase 70) | Bare `ruff check .` reports `All checks passed!` after the rewrite, specifically re-checked against `typsphinx/__init__.py` |
| CLAUDE.md:75 contradicts the milestone (Pitfall 2) | Implementation phase (Phase 70), sequenced first | `grep -c "modernize.*typing imports" CLAUDE.md` returns 0 (or the sentence is gone) before the annotation edits are made |
| Multi-location sync (`pyproject.toml`/`CLAUDE.md`/todo) (Pitfall 3) | Implementation phase (Phase 70), same commit | All three locations changed in one commit; todo file physically present under `todos/completed/`, absent from `todos/pending/` |
| Stale todo file list / under-scoped discovery (Pitfall 4) | Roadmap authoring + re-verified at Phase 70 start | `ruff check . --select UP006,UP035` returns zero output at phase close, run fresh (not cached from this report) |
| Dependabot ruff-version drift mid-milestone (Pitfall 5) | Roadmap wording (no hard-coded counts) + Phase 70 start | `uv.lock`'s `ruff` version recorded at phase start; violation count re-measured if it changed |
| `phase.complete` checkbox auto-flip | Close-prep phase (Phase 71) | `git diff` on requirements/state files before commit, reverting any flip contradicting the "unpublished" CONTEXT decision |
| ja `.po` drift (deferred, informational) | None in this milestone; noted for the next publishing milestone | CHANGELOG/close-prep notes mention the autodoc-typehint text change as a future translation-sync item |
| Worktree Python-minor drift | Any phase using worktree-isolated execution (standing mode, all phases) | Compare `.venv/pyvenv.cfg` `version_info` between main checkout and worktree before attributing an unexpected test failure to the typing change |
| CI-only defect classes | Close-prep phase (Phase 71) | Cite the actual CI run (all matrix lanes green), not a local-only pass |

## Sources

- Direct command output against this repo (ruff 0.16.6, pinned in `uv.lock`): `ruff check .
  --select UP006,UP035 --statistics`, `--output-format=concise`, `--diff`, `--fix`,
  `--fix --unsafe-fixes`, `--fix --unsafe-fixes --preview`, run both in the real checkout and in a
  scratch copy under this session's scratchpad directory.
- `ruff rule F401` (built-in rule documentation, ruff 0.16.6) for the `__init__.py` fix-safety
  explanation underlying Pitfall 1.
- `/home/yuta/Documents/typsphinx/CLAUDE.md` (verbatim lines 75, 91, 93, 97-115).
- `/home/yuta/Documents/typsphinx/pyproject.toml` (lines 118-134, 136-149).
- `/home/yuta/Documents/typsphinx/.planning/PROJECT.md` (lines 1-90, Current Milestone section).
- `/home/yuta/Documents/typsphinx/.planning/todos/pending/2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md`.
- `/home/yuta/Documents/typsphinx/.planning/MILESTONES.md` (v0.9.3 entry: REL-12 auto-flip history,
  dependabot-on-uv proof via PR #138; v0.6.3/v0.6.4 entries: ja gettext regeneration precedent).
- `/home/yuta/Documents/typsphinx/.planning/codebase/CONCERNS.md`.
- `.github/workflows/ci.yml`, `tox.ini` (job/env definitions cited above).
- `uv python list`, `.venv/pyvenv.cfg` (live measurement of interpreter availability/drift).

---
*Pitfalls research for: typsphinx v0.9.4 Typing Modernization (QUA-09)*
*Researched: 2026-09-13*
