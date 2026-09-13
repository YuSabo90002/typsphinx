# Stack Research

**Domain:** Python typing-syntax modernization via linter-driven autofix (ruff UP006/UP035 → PEP 585 builtin generics)
**Researched:** 2026-09-13
**Confidence:** HIGH — every claim below is backed by an observed command run in a scratch copy of the real tree (`typsphinx/`, `tests/`, `pyproject.toml`), not by ruff/mypy documentation alone. Commands and outputs are reproduced under "Sources."

## Recommended Stack

No new technology is being introduced. This milestone (QUA-09) is a **behavior-preserving syntax rewrite executed entirely with tools already pinned in `uv.lock`** — ruff's own autofixer does 94 of the 113 rewrites; the remaining 19 (import lines) and 1 special case are mechanical text edits. The "stack" here is the toolchain versions that participate and what each one actually does.

### Core Technologies (as pinned in `uv.lock`, verified 2026-09-13)

| Technology | Version (uv.lock resolved) | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| ruff | 0.16.6 | Detects and autofixes UP006 (`non-pep585-annotation`) and UP035 (`deprecated-import`) | Already the project's sole linter; `pyproject.toml`'s `ruff>=0.15,<0.17` dev-extra spec already resolves to 0.16.6 today. No version change needed to do this work. |
| black | 26.5.1 | Reformats any lines ruff's fixer touches | Confirmed no-op on this change (see Sources) — builtin-generic annotations are exactly as short as `Dict`/`List`, so no line ever crosses the 88-column limit differently than before. |
| mypy | installed `.venv` build reports 2.1.0; `uv.lock` resolves `mypy==2.3.1` for a clean sync (see note below) | Confirms the rewrite changes no type-checking result | `dict[str, Any]` and `typing.Dict[str, Any]` are the same type to mypy under `python_version = "3.12"` — PEP 585 builtin generic aliases have been treated as fully equivalent to their `typing` counterparts by mypy since Python 3.9 support was added. Verified empirically (see Sources): `mypy typsphinx/` reports `Success: no issues found in 9 source files` on both the current tree and the fully-rewritten scratch copy, byte-for-byte the same message. |
| Python | 3.12 (target), tested 3.12–3.13 | Runtime the rewritten annotations execute under | `requires-python = ">=3.12"` already; PEP 585 (builtin generics as generic aliases) landed in 3.9, so no floor change is needed or implied by this milestone. |
| sphinx-autodoc-typehints | 3.0.1 (docs extra) | Renders the changed annotations in the published API reference | This is the one **visible, intentional** side effect: it prints whatever the live `__annotations__` object is, not source text — see "Version Compatibility" below for the exact before/after string. |

**Note on the mypy version discrepancy:** the currently-synced `.venv` in the main checkout reports `mypy 2.1.0`, while `uv.lock` resolves `mypy==2.3.1` for a fresh `dev`-extra sync. This is a pre-existing drift between the synced venv and the lockfile, unrelated to this milestone (environment rules for this research task forbid running `uv sync`, so it was not corrected here). Either version treats `Dict[str, Any]` and `dict[str, Any]` identically for the reason given above; do not treat this drift as something QUA-09 needs to fix.

### Supporting Libraries

None. QUA-09 adds zero runtime or dev dependencies. `collections.abc.Iterator` (stdlib) replaces `typing.Iterator` (also stdlib) for the one `Iterator` occurrence — this is an import-source change, not a new dependency.

### Development Tools — the exact ruff behavior this milestone depends on

| Tool behavior | Purpose | Notes (observed, not assumed) |
|------|---------|-------|
| `ruff check . --select UP006,UP035 --statistics` | Confirms scope before touching the ignore list | Reproduced the orchestrator's exact count: `93 UP006 [*]` (autofixable) + `20 UP035 [-]` (fix "sometimes available") = 113, "94 fixable with the `--fix` option." One of the 20 UP035 hits (the `Iterator` one in `tests/test_include_ledger_removal_gate.py`) is itself marked `[*]` — it's the one UP035 hit ruff can fix unassisted, because `Iterator` has a direct `collections.abc` replacement import; the other 19 UP035 hits are the `Dict`/`List`/`Set`/`Tuple` import-line residue, which UP035 cannot fix by itself (there is no "import statement" form of `dict`/`list`/`set`/`tuple` — they're builtins) until UP006 has first rewritten every *usage* of the name, at which point the import becomes simply unused and F401 (not UP035) is what actually removes it. |
| Single `ruff check . --fix` pass | Applies the 94 safe fixes and re-evaluates to a fixed point *within one invocation* | Observed: pass 1 goes from 113 → 2 remaining (`1 UP035` + `1 F401`, both on the same line, `typsphinx/__init__.py:15`). Pass 2 (`ruff check . --fix` again) makes **zero further progress** — same 2 remain. This is not an "orphaned import needs a second pass" situation in general (isort/F401 for ordinary files resolve within pass 1, confirmed against a synthetic file with identical import shape placed anywhere else in the tree) — it is a **single, `__init__.py`-specific carve-out**, documented in ruff's own rule text: *"Fixes to remove unused imports are safe, except in `__init__.py` files. Applying fixes to `__init__.py` files is currently in preview."* Without `--preview`, ruff reports the diagnostic but offers **no fix at all** (no `[*]` marker) for the leftover `Dict` in `typsphinx/__init__.py`'s `from typing import Any, Dict` — confirmed this holds even with `--unsafe-fixes` added, and only yields a fix when `--preview` is also added (verified: `ruff check typsphinx/__init__.py --select F401 --preview --unsafe-fixes --diff` produces the removal; without `--preview` it produces nothing, exit 0, "no errors" reported for `--diff` mode even though `check` mode still lists it as an unfixed error). **Do not turn on `--preview`** for this (see "What NOT to Use") — hand-edit that one line instead. |
| `ruff check .` (respecting `pyproject.toml`'s configured `select`/`ignore`, i.e. simulating the ignore-lines-removed state) after the manual `__init__.py` edit | Confirms no other rule category starts firing | Observed: `All checks passed!` — zero I001 (import-sort) violations, zero UP007/UP045 (`Optional`/`Union` → `X \| None`) violations. The latter is because the codebase has **zero** `typing.Optional`/`typing.Union` usages anywhere (`grep -rn "Optional\[\|Union\[" typsphinx/ tests/` returns nothing) and UP007/UP045 were already enabled (`UP` is selected as a whole category, not per-code) and already clean before this change — there is no UP007/UP045 "interplay" to guard against because the triggering pattern doesn't exist in this codebase. |
| `black --check --diff .` on the fully-rewritten scratch tree | Confirms no reformatting follows the rewrite | Observed: `All done! ✨ 🍰 ✨ 348 files would be left unchanged.` — zero diffs. |
| `mypy typsphinx/` on original vs. rewritten scratch tree | Confirms zero type-checking behavior change | Observed: identical `Success: no issues found in 9 source files` on both trees. |
| `pytest` on the rewritten scratch tree | Sanity check for runtime behavior (not a substitute for the real worktree run) | Ran 1,377+168 tests passing across the touched modules (`test_translator.py`, `test_builder.py`, `test_template_engine.py`, `test_bundle_layout_sweep_gate.py`, `test_include_edge_derivation_unit.py`, `test_include_ledger_removal_gate.py`, `conftest.py`) plus the full non-slow suite; the ~72 failures observed were 100% attributable to the scratch copy intentionally omitting `docs/`, `examples/`, `README.md`, `.readthedocs.yaml`, and `.planning/` (this experiment copied only `typsphinx/ tests/ pyproject.toml` per the environment rules) — every failure is a `FileNotFoundError`/content-mismatch against a repo-root file this scratch never had, not a typing-rewrite regression. Execute-phase must still run the full suite inside a real worktree (per `CLAUDE.md`'s worktree-isolated execution rules) as the actual gate; this scratch run is corroborating evidence, not a replacement.

## Installation

No installation step. Nothing to add to `dependencies`, `dev`, or `docs` extras. The two ruff ignore lines are deletions, not additions:

```toml
# pyproject.toml [tool.ruff.lint] ignore — DELETE these two lines and their comments:
    "UP035",  # typing.Dict/List/Set deprecation; modernization deferred (see .planning/todos/pending/2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md)
    "UP006",  # Use dict instead of Dict; same deferral as UP035 above
```

### Recommended conversion command sequence

```bash
# 1. Edit pyproject.toml: remove the two ignore lines above (and their comments).

# 2. Let ruff do the 94 safe, mechanical rewrites in one pass.
ruff check . --fix

# 3. Confirm what's left (expected: exactly 2 diagnostics, both on
#    typsphinx/__init__.py:15 — one UP035, one F401 unused-import, both for
#    the now-dead `Dict` name in `from typing import Any, Dict`).
ruff check . --statistics

# 4. Hand-edit typsphinx/__init__.py:15 to drop the dead name
#    (ruff will not auto-fix this without --preview; do not enable --preview —
#    see "What NOT to Use"):
#    from typing import Any, Dict   ->   from typing import Any

# 5. Confirm zero remaining violations under the project's real configured
#    select/ignore list (not just --select UP006,UP035).
ruff check .

# 6. Confirm no reformatting follows (expected: no-op).
black --check .

# 7. Confirm no type-checking behavior changed (expected: identical to
#    pre-change output).
mypy typsphinx/

# 8. Full suite, in the real worktree (per CLAUDE.md's worktree-isolated
#    execution — do NOT run this from a bare scratch copy as the gate):
uv run pytest

# 9. Update CLAUDE.md:75's "Don't modernize typing imports..." prohibition
#    to reflect completion, and move the todo file to todos/completed/.
```

Everything through step 7 was executed in a scratch copy for this research and produced exactly the outputs quoted above — steps 8-9 are execution-phase work, not research.

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| `ruff check . --fix` (stable mode) then one manual line edit | `ruff check . --fix --preview --unsafe-fixes` (lets ruff auto-remove the `__init__.py` import too) | Never for this milestone. `--preview` turns on ruff's entire preview rule set project-wide for that invocation, not just the `__init__.py` F401 carve-out — it is not a scoped flag. Using it risks surfacing or silently applying unrelated preview-only fixes elsewhere in the tree, which is scope creep this milestone explicitly should avoid. A one-line hand edit is strictly safer and just as fast. |
| Two-pass `ruff check --fix` (run it, then run it again to converge) | Trusting a single pass to be complete | Run the second pass anyway as a matter of hygiene (it's free and confirms the fixed point) — but expect it to be a no-op here. Do not treat "second pass found something new" as expected/normal in general; here it's specifically the `__init__.py` exemption, not a general two-pass requirement. |
| Manual `from typing import Any` edit in `__init__.py` | Adding a `# noqa: F401` or import alias (`Dict as Dict`) to silence the warning | Never — that would preserve the dead `typing.Dict` import as a permanent lint suppression instead of deleting it, defeating the purpose of the milestone (the goal is zero `typing.Dict/List/Set/Tuple` usages left in the tree, not zero lint noise about them). |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| `ruff check --fix --preview` project-wide | Turns on ruff's full preview rule set, not just the `__init__.py` F401 fix; introduces risk of unrelated new violations/fixes outside this milestone's scope | The one-line hand edit shown above |
| `from __future__ import annotations` sweep | Not requested by REQUIREMENTS/PROJECT.md; would change annotation evaluation semantics (turns all annotations into forward-reference strings) — a much bigger behavioral surface than a syntax swap, and unnecessary since `requires-python >=3.12` already supports PEP 585 generics natively at runtime with zero import needed | Nothing — builtin generics (`dict`, `list`, `set`, `tuple`) require no `__future__` import on 3.12+; this is precisely why the ignores were only ever a maintenance leftover (per the 2026-07-22 todo's own diagnosis) and not a technical constraint |
| PEP 604 (`X \| None` / `X \| Y`) scope creep | Confirmed via `grep -rn "Optional\[\|Union\[" typsphinx/ tests/` — zero occurrences exist in this codebase, and UP007 (`non-pep604-annotation-union`)/UP045 (`non-pep604-annotation-optional`) are already enabled and already clean (`ruff check . --select UP007,UP045` → 0 hits) before this milestone even starts. There is nothing here to convert, and there is no rule interplay to guard against | N/A — leave `Optional`/`Union` handling untouched because it does not exist |
| Bumping `ruff`'s pin ahead of what dependabot proposes, or merging an in-flight dependabot ruff PR mid-milestone for convenience | `pyproject.toml`'s `ruff>=0.15,<0.17` spec is already wide enough to have silently absorbed 0.15.20 → 0.16.6 via dependabot's uv-ecosystem PRs (proven on PR #138, merged 2026-09-12 — see "Version Compatibility"/Sources), and that merge itself widened the *pyproject.toml* specifier (`<0.16` → `<0.17`), not just `uv.lock`. Because this project's ruff `select` list names whole categories (`"UP"`, not individual `UP0xx` codes), a *future* dependabot bump to `ruff>=0.17` could add brand-new `UP` (or other) rule IDs that fire for the first time, producing violations unrelated to UP006/UP035 and muddying the "113 violations, closed" evidence trail for this milestone | Do the UP006/UP035 conversion against the currently-pinned 0.16.6 first; if a dependabot ruff PR lands during the milestone, treat merging it as a separate, later decision (owner-approved, per this project's established process — see D-03 in the v0.9.3 shipped section) and re-run `ruff check . --statistics` afterward to confirm zero new violations before considering it a non-event |
| Treating this milestone's autodoc rendering change as a bug to "fix" | `docs/source/api/index.rst` will render `dict[str, Any]` where it rendered `Dict[str, Any]` before — this is the correct, intended, and only visible side effect (already called out in `PROJECT.md`'s Current Milestone section) | Let it happen; do not add config to force the old `Dict`-style rendering back |

## Stack Patterns by Variant

**If a future dependabot PR bumps `ruff` past `<0.17` mid-milestone:**
- Re-run `ruff check . --statistics` against the *already-completed* rewrite before merging that PR, to establish whether the new ruff version introduces unrelated violations.
- Keep that decision (merge now vs. defer) separate from QUA-09's own commit — do not let a version-bump-triggered violation get silently folded into "the 113 UP006/UP035 fixes," since that would misrepresent what this milestone actually closed.

**If mypy's synced venv version (2.1.0) and `uv.lock`'s resolved version (2.3.1) ever need reconciling:**
- That is a separate, pre-existing drift (unrelated to typing/UP006/UP035) and out of scope for QUA-09; do not fix it as a side effect of this milestone's commits.

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| ruff 0.16.6 | Python 3.12 target (`target-version = "py312"`) | UP006 is active by default for `target-version` py39+; no config change needed beyond removing the two ignore lines. Verified: `ruff rule UP006` / `ruff rule UP035` both confirm "Fix is sometimes available," and this research reproduced exactly which occurrences are/aren't auto-fixable (see Development Tools table). |
| mypy 2.1.0 / 2.3.1 | `dict[str, Any]` vs `typing.Dict[str, Any]` | No difference in type-checking result — PEP 585 generic aliases and their `typing` counterparts are the same type to mypy. Verified empirically: identical `Success: no issues found in 9 source files` before and after the full rewrite. |
| black 26.5.1 | Rewritten annotation lines | No reformatting triggered — verified `black --check --diff .` is a no-op (348 files unchanged) on the fully-rewritten scratch tree. |
| sphinx-autodoc-typehints 3.0.1 + Sphinx's `stringify_annotation` | `autodoc_typehints = "description"` (as configured in `docs/source/conf.py`, no `autodoc_typehints_format` override, so default "short"/`fully-qualified-except-typing`-equivalent formatting applies) | Verified directly via `sphinx.util.typing.stringify_annotation`: `typing.Dict[str, Any]` renders as `Dict[str, Any]` (cross-referenced to `typing.Dict`); `dict[str, Any]` renders as `dict[str, Any]` (builtin, lowercase, not cross-referenced as a typing member — only `Any` inside it still cross-references `typing.Any`). This is the exact, sole, and already-anticipated visible change to the published API reference (HTML and PDF, both built from the same `docs/source/api/index.rst` automodule directives) named in `PROJECT.md`'s Current Milestone section — no further action needed beyond letting the rewrite happen. |
| Dependabot (uv ecosystem, since v0.9.3/PR #137) | ruff's `>=0.15,<0.17` spec in `pyproject.toml` | Confirmed via git history (`cf3305ce`, PR #138, merged 2026-09-12): dependabot's uv-ecosystem support edits **both** `pyproject.toml`'s specifier (there: `<0.16` → `<0.17`) **and** `uv.lock`'s resolved version in the same commit, and only lands via an owner-approved merge (not automatically) — so it is a discrete, visible event this milestone can watch for, not a silent background risk. |

## Sources

- Live scratch-copy experiment (this session): `pyproject.toml`, `typsphinx/`, `tests/` copied to `/tmp/.../scratchpad/stack-probe`, `.venv` symlinked from the real checkout, both ignore lines removed, then `ruff check . --statistics` (113 before fix), `ruff check . --fix --statistics` (113→2, pass 2 no-op), `ruff rule F401`/`ruff rule UP035`/`ruff rule UP006` (rule text, fix-safety notes), targeted `ruff check typsphinx/__init__.py --select F401 [--unsafe-fixes|--preview] --diff` isolating the `__init__.py`-only F401 carve-out, `black --check --diff .` (no-op), `mypy typsphinx/` (identical clean result before/after), `pytest` (1,377+168 relevant tests green; all failures traced to repo-root files the scratch intentionally omitted).
- `uv.lock` (this checkout, read directly, not from memory): `ruff==0.16.6`, `black==26.5.1`, `mypy==2.3.1` (resolved; installed `.venv` currently reports 2.1.0), `sphinx-autodoc-typehints==3.0.1`.
- `git show`/`git diff` on `cf3305ce` (PR #138 merge commit) and `72162d19` (its adoption into main): confirms dependabot's uv-ecosystem PR changed both `pyproject.toml`'s ruff specifier and `uv.lock` together, and required an owner-approved merge (D-03), consistent with `PROJECT.md`'s v0.9.3 shipped-milestone summary.
- Direct Python invocation of `sphinx.util.typing.stringify_annotation` (Sphinx's own formatter, the one `sphinx-autodoc-typehints` calls) against `typing.Dict[str, Any]` and `dict[str, Any]` — confirms the exact before/after rendered string for the API reference docs.
- `.planning/PROJECT.md` (Current Milestone section, lines 33-70) and `.planning/todos/pending/2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md` — milestone scope and the todo's own admission that the ignore was a maintenance leftover from the Python-3.10-floor era, not a technical constraint.
- `pyproject.toml` (this checkout) — current `[tool.ruff.lint]` select/ignore list, `[tool.mypy]` config, `[tool.black]` config, dev/docs extras.

---
*Stack research for: typsphinx v0.9.4 Typing Modernization (QUA-09)*
*Researched: 2026-09-13*
