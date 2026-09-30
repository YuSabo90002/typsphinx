# Feature Research

**Domain:** Python typing modernization on a mature, single-maintainer PyPI library with a strict
"evidence, not assertion" project culture (typsphinx v0.9.4, QUA-09)
**Researched:** 2026-09-13
**Confidence:** HIGH (scope items and counts are locally measured, not inferred; evidence-mechanism
costs are estimated from this project's own prior art, not benchmarked)

This is not a product feature landscape — this milestone ships no user-facing feature. "Feature" is
read here as "scope item a `/gsd-new-milestone` requirements pass could plausibly pull in", scored
the same way: table stakes (must be in scope or the milestone doesn't count as done), differentiators
(the evidence work that makes "behaviour unchanged" a checked fact instead of a claim), and
anti-features (adjacent typing/formatting work to explicitly refuse).

## Feature Landscape

### Table Stakes (Must Be In Scope For This To Count As Done)

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Remove `UP035` and `UP006` from `pyproject.toml`'s `[tool.ruff.lint] ignore`, including both deferral comments | This is the milestone's own stated goal (PROJECT.md) and the todo's own Solution step 1; leaving either ignore in place means the ignore that motivated the whole milestone still exists | LOW | Two-line delete at `pyproject.toml:128-129`. The comments reference this todo's filename and the pending 3.10-compat wording — both must go, not just the rule IDs, or a future reader re-derives a false "still 3.10-constrained" story |
| Resolve all 113 measured violations (93 UP006 + 20 UP035) to zero, re-measured with the ignore already removed | "Zero violations" is the only way `ruff check .` — CI's actual lint gate — passes once the ignore is gone; a partial rewrite that still trips the rule fails CI, not just the milestone's own bar | LOW–MEDIUM | Confirmed 2026-09-13 by direct measurement in this research session: `ruff check . --select UP006,UP035` reports exactly 113 errors, 94 autofixable, matching PROJECT.md. `ruff check --fix` handles the bulk (`Dict`→`dict`, `List`→`list`, `Set`→`set`, `Tuple`→`tuple` at both import and annotation sites); the remaining ~19 are import-line residue that autofix cannot safely drop until usages are gone (F401 will flag the leftover `from typing import Dict` etc. once the last usage is rewritten) |
| Move `typing.Iterator` to `collections.abc.Iterator` | Named explicitly by PROJECT.md and the todo as the one non-container rewrite in scope; `Iterator` is not part of the `Dict/List/Set/Tuple` autofix family ruff's UP006/UP035 handle, so it needs its own import-line edit | LOW | One occurrence per PROJECT.md's count. `ruff --fix` does not move this on its own for all cases — confirm post-fix with `grep -rn 'from typing import.*Iterator\|typing.Iterator' typsphinx/ tests/` before declaring done |
| `tests/` in scope, not just `typsphinx/` (4 files / 21 violations: `conftest.py` + three gate modules) | CI runs `ruff check .` over the whole repo, so `tests/` is in scope by construction regardless of what the stale todo's file list says; PROJECT.md's "Key context" explicitly flags the todo's list as stale on this exact point | LOW | The todo (2026-07-22) names zero `tests/` files — confirmed by reading it directly. Discovery must be by `ruff check . --select UP006,UP035`, not by the todo's file list, or these 21 are silently missed and CI still fails after "typsphinx/ done" |
| `mypy typsphinx/` stays green under the rewritten annotations | The todo's own Solution step 3 requires it; mypy is a separate CI job (`tox -e type`) from ruff/black, so a typing rewrite that ruff accepts could still regress mypy independently (e.g. a `Tuple[int, ...]` variadic form rewritten incorrectly to `tuple[int]`) | LOW | `[tool.mypy]` config (`pyproject.toml:136-149`) already disables several error codes for `typsphinx.*` (`var-annotated`, `arg-type`, `override`, `misc`, `union-attr`, `attr-defined`, `list-item`) — the pre-existing `list-item` suppression is worth a second look post-rewrite in case it was papering over a `List`-vs-`list` mismatch that this milestone now resolves for real, in which case tightening (not just re-running) mypy is in scope as evidence, not as new work |
| Full pytest suite green, black clean, ruff clean (whole gate quartet, not just the two rules touched) | Standing project convention for every milestone (v0.9.1, v0.9.2, v0.9.3 all closed on the full quartet); a rewrite this mechanical is exactly the kind of change likely to trip an unrelated `E501` line-length wrap or an F401 leftover import that narrow `--select UP006,UP035` re-checks would miss | LOW | `black --check .`, `ruff check .` (unrestricted, not `--select`), `mypy typsphinx/`, full `pytest` — the same four gates CI runs (`.github/workflows/ci.yml`: lint/type/py312/py313/cov jobs) |
| `CLAUDE.md:75`'s "Don't modernize typing imports until that todo lands" prohibition rewritten to reflect completion | PROJECT.md states this explicitly as a target feature; leaving the prohibition in place after landing the work leaves the repo's own contributor doc contradicting its own state, exactly the kind of drift this project's culture treats as a defect (cf. Phase 68's whole purpose was fixing three docs describing a mechanism that no longer matched reality) | LOW | Locate via `grep -n "modernize.*typing\|UP006\|UP035" CLAUDE.md` (line 75 per PROJECT.md's citation is not itself verified in this research pass — confirm at plan time, since CLAUDE.md is a live file this milestone's own prior turns may have already touched). Rewrite to state completion, not delete outright — the file's own convention (see the `@preview` version-sync and toolchain-pin-sync subsections) is to record *why* a constraint existed and *that* it resolved, not to erase the history |
| Move the todo file to `todos/completed/` | Todo lifecycle convention already established elsewhere in this project (referenced by name throughout PROJECT.md's Shipped Milestone sections, e.g. v0.9.3's DEP items closing #123/#128); the todo itself is the authoritative record of *why* the ignore existed (an accidental Phase-6 floor-raise leftover, not a real constraint) and should be preserved, not deleted | LOW | `git mv .planning/todos/pending/2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md .planning/todos/completed/`. The todo file itself warns (line 51-52) that "Plan 03 (Phase 22.4)" references this exact filename from `CLAUDE.md`/`pyproject.toml` comments — confirm no live comment still points at the `pending/` path after the move, or the comment being rewritten (table-stakes item above) needs to drop the path reference entirely rather than repoint it |
| CHANGELOG bullet under the existing `## [Unreleased]` heading, contributor-tooling register | This milestone is close-prep-only and unpublished (owner decision, same shape as v0.9.3) — no `## [0.9.4]` heading, no version bump in `pyproject.toml` (stays `0.9.2`) | LOW | Read `CHANGELOG.md`'s current `## [Unreleased]` section directly (confirmed in this research pass): three existing bullets (TOX-01..04, DEP-01..05, NIX-01..08+DOC-19..21) each open with a **bold one-line summary naming the requirement IDs**, then 2-4 sentences ending in an explicit **"This has no effect on installing or using typsphinx"** disclaimer for contributor-only changes. QUA-09's bullet should match that register exactly: bold summary + requirement ID, then the one genuinely user-visible fact (the rendered API reference now shows `dict[str, Any]` instead of `Dict[str, Any]`) stated plainly rather than buried, then the same "no effect on installing or using typsphinx" framing for everything else, since runtime behavior is otherwise unchanged |
| The one user-visible side effect (rendered API reference typehints) is acknowledged, not hidden | PROJECT.md's own "Key context" flags this as "One visible side effect" — `docs/source/api/index.rst` autodocs five modules with `sphinx_autodoc_typehints` + `autodoc_typehints = "description"`, so HTML and PDF on RTD will render `dict[str, Any]` where they rendered `Dict[str, Any]` | LOW | This is not a defect to fix — it is a fact to state in the CHANGELOG bullet (see above) and to confirm via an actual docs build diff (see differentiators) rather than assume from reading the config |

### Differentiators (Evidence That Behaviour Is Actually Unchanged)

PROJECT.md defers the *mechanism* to research/planning ("AST-level comparison, byte-identical `.typ`
output, zero pre-existing test-assertion edits, or a combination"). Ranked here cheapest-to-most-
convincing, with concrete named mechanisms so each can become a success criterion directly.

| Feature (evidence mechanism) | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Zero pre-existing test-assertion edits, measured by `git diff --name-status` / `git diff` over `tests/`** | Cheapest and most convincing single proof for this specific change class: a pure `Dict`→`dict` rewrite touches only annotations, never assertion bodies, so if any *existing* test's assertion logic needed to change to stay green, that is itself evidence something behavioural moved. This is this project's own standing culture (named explicitly in memory: "zero pre-existing test edits" measured with `git diff --name-status", used across v0.9.1, v0.9.2, v0.9.3) | LOW | Run once on a clean pre-change branch tip, once post-change; the only files touched under `tests/` should be the 4 files with `UP006/UP035` hits themselves (`conftest.py` + 3 gate modules) being rewritten *in that same class of change* (their own type-hint lines), not new assertion edits. Depends on: existing full pytest suite already gating merges (already true) |
| **Full pytest suite green with the *collected test count* and pass/skip counts unchanged before vs. after** | Cheap, mechanical, and this project's own precedent for "nothing executable moved": Phase 68 (v0.9.3) used exactly this pairing — masked-AST-hash equality *plus* "the two-file pass/skip summary and the suite collected count are identical before and after" — as its closing proof for a claimed no-op change | LOW | `pytest --collect-only -q | tail -1` and the final `N passed / M skipped` line, captured before and after, string-compared. Depends on: no test in the suite currently asserts on `repr(SomeType)`-shaped output that would differ between `typing.Dict` and `dict` reprs (worth a targeted grep before claiming this is sufficient alone) |
| **AST comparison modulo annotation nodes** (not modulo docstrings/strings, as Phase 68 used — that project's own "masked AST hash" masked *string* nodes, because Phase 68's edits were prose-only; this milestone's edits are annotation-only, so the mask target is different) | Directly answers "did anything except type annotations change?" for a mechanical rewrite where the diff itself is large (113 sites) and hard to visually audit end to end. Adapts, rather than reuses verbatim, the exact technique this project already trusts (v0.9.3 Phase 68, `68-02-PLAN.md`/`68-TOX-EVIDENCE.md`) | MEDIUM | Concretely: `ast.parse()` each changed file before and after, walk the tree, and before hashing, blank/normalize every `ast.AnnAssign.annotation`, `ast.arg.annotation`, and `ast.FunctionDef`/`ast.AsyncFunctionDef.returns` field (and the subscript targets they contain — `Dict[str, Any]` and `dict[str, Any]` are structurally different `Subscript` shapes, so the mask must strip the whole annotation subtree, not just rename a `Name` node) — then compare hashes of what remains. A one-off script for this milestone, not existing tooling; budget it as new, small (~30-40 line) code written for evidence, never committed to `typsphinx/` itself. Depends on: nothing existing — this is new verification code, distinct from Phase 68's docstring-masking helper, which cannot be reused unmodified because it masks the wrong node class |
| **Byte-identical `.typ` output over the existing fixture/golden corpus** (`tests/roots/`, any committed golden `.typ` files, and — if budget allows — a full real `-b typstpdf` compile over Sphinx's own `doc/` tree per the v0.6.0/v0.6.1 corpus precedent) | The single most convincing proof available for "runtime behaviour and emitted Typst output unchanged" as PROJECT.md phrases the goal, because it measures the actual deliverable (the `.typ`/PDF a user gets) rather than a proxy for it. This project's own precedent (v0.9.1: "POSIX output was proven byte-identical the way v0.9.0 proved it") treats this as the standard bar for a behaviour-neutral claim | LOW (mechanically — hash/diff the output tree before and after over the existing test corpus; no new fixtures needed since none of the 113 sites touch translator logic, only its type declarations) | This is close to free here specifically *because* the change class is type-annotation-only and never touches a runtime branch, default value, or control-flow expression — unlike Phase 68's doc-only change (which had no `.typ` output to compare at all), this milestone's changes live inside the same files (`translator.py`, `builder.py`, etc.) that produce `.typ` output, so re-running the existing integration/render-gate tests (`test_pdf_render_gate.py`, the various `*_render_gate.py` files, `test_pdf_generation.py`) already exercises this if their own assertions are untouched. Depends on: the existing render-gate test suite already existing and passing (it does) |
| **`git diff` over `typsphinx/` and `tests/` classified line-by-line as annotation-only** (a manual/scripted audit that every changed line matches one of a small number of known-safe patterns: import line, `Dict[`→`dict[`, bare `Dict`→`dict`, etc.) | Cheap sanity check that complements rather than replaces the AST-modulo-annotations proof — catches the case where `ruff --fix` or a manual edit accidentally reflowed a nearby line (autofix sometimes reformats the containing statement, which black would then re-touch) | LOW | `git diff --unified=0 typsphinx/ tests/` piped through a small classifier; overlaps with black's own `--check` gate for "did formatting move" but is more legible for a human reviewer scanning 113 sites across 11 files |
| **mypy diff-free**: same error set (empty, given current green baseline) before and after, not just "still green" | Slightly stronger than "green" alone — proves mypy's own view of the types is unchanged, not merely that no *new* category of error appeared that mypy's already-generous `disable_error_code` list happens to suppress | LOW | `mypy typsphinx/` output string-compared before/after (both expected empty/success); cheap since it reuses the existing gate, just captures output rather than only the exit code |
| **Clean docs build (`rm -rf docs/_build` first) with the diff confined to type text in the API reference pages** | Directly targets PROJECT.md's named "one visible side effect" — proves the *only* rendered change anywhere in the built docs (HTML and the `docs-pdf` output) is `Dict[str, Any]` → `dict[str, Any]`-shaped text in the five autodoc'd modules, with the warning count from a clean build unchanged from baseline | MEDIUM | Depends on the standing project memory that **incremental docs rebuilds under-report warnings** — a clean `rm -rf docs/_build` is required before comparing, per this project's own established practice, or the "no new warnings" claim is unfalsifiable. Diff mechanism: build HTML before/after, diff the API reference pages' rendered text, confirm every changed line is inside a type annotation. Depends on: existing `tox -e docs-html` / `tox -e docs-pdf` environments (already present) and a pre-change warning-count baseline (must be taken fresh, not reused from a stale prior run) |

### Anti-Features (Scope Creep To Refuse)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|------------------|-------------|
| PEP 604 `X \| None` sweep (rewriting `Optional[X]` to `X \| None`, or `Union[A, B]` to `A \| B`) across the codebase | Feels like "the same modernization, one PEP later" — an executor mid-rewrite will see adjacent `Optional`/`Union` usages sitting right next to the `Dict`/`List` ones being touched and be tempted to fold them in for free | Not forced by any active ruff rule in this milestone's scope (UP006/UP035 govern container generics, not `Optional`/`Union` — that is UP007/UP045, which stay in `ignore` and are out of scope). Pulling it in silently doubles the diff surface, doubles the evidence burden (every new site needs the same behaviour-neutrality proof), and reopens exactly the kind of undisclosed scope-widening this project's memory explicitly warns against ("requirement reframings live in prior-phase CONTEXT" — scope expansion needs an explicit owner decision, not executor initiative) | Leave `Optional`/`Union` exactly as-is. If it's worth doing, it is a separate todo filed the same way the current one was (2026-07-22 precedent), scoped and dated, for a future milestone to pick up deliberately |
| `from __future__ import annotations` (postponed evaluation of annotations) added to touched files | Looks like a natural companion to a typing-generics upgrade, and would make some rewrites cosmetically shorter | Changes runtime semantics of `typing.get_type_hints()` and any string-based introspection Sphinx's own autodoc/`sphinx_autodoc_typehints` machinery performs on these exact modules — this is precisely the kind of change that could alter the "one visible side effect" from a pure text change (`Dict`→`dict`) into a *different* rendering entirely, or break autodoc's type resolution. Direct contradiction of the milestone's own explicit constraint ("runtime behaviour and emitted Typst output unchanged") | Do not add it. Python 3.12's floor already makes builtin generics subscriptable at runtime without it — the entire premise of this milestone is that `from __future__ import annotations` was never necessary here |
| Public API or function-signature changes (renaming parameters, adding/removing them, changing default values, changing overload structure while "improving" types) | An executor auditing 113 sites across `translator.py`'s ~140 `visit_*`/`depart_*` methods will inevitably notice adjacent signature quirks worth "fixing while I'm in there" | Directly violates the milestone's own scope statement and this project's general convention of not bundling unrelated fixes into a mechanical-rewrite phase (cf. the `@preview` version-sync and toolchain-pin-sync hazards this project explicitly documents as "things that must move together" — the inverse discipline, keeping unrelated things apart, is the same value applied here) | File any genuine signature defect found along the way as a new dated todo, exactly like the source todo this milestone closes. Do not fix it in this milestone's diff |
| Touching the four `@preview` package versions (`codly`, `codly-languages`, `mitex`, `gentle-clues`) or their three-file lockstep declarations | None of the 113 violation sites are anywhere near these declarations, but `builder.py`/`writer.py`/`template_engine.py` are three of the seven files this milestone touches, and those are exactly the three-plus-one files (`templates/base.typ`) that carry the version-sync hazard CLAUDE.md documents | Any incidental edit to a line near a `@preview` version string risks a diff-review false flag or an actual accidental version drift, which has its own dedicated CI gate (`tests/test_preview_version_sync.py`) that is unrelated to this milestone's own gates and would confuse a failure's root cause | Confirm at plan time that the specific lines touched in `builder.py`/`writer.py`/`template_engine.py` are annotation-only and nowhere near the version-string declarations; if a UP006/UP035 site happens to sit on the same line as a version string (unlikely but not measured false), split the edit rather than risk conflating the two diff classes |
| Reformatting unrelated code while `black`/`ruff --fix` is running (accepting `black`'s reflow of *any* line the autofix touches, beyond what the annotation rewrite itself requires, or running `black`/`ruff --fix` repo-wide instead of scoped to the 11 changed files) | `ruff --fix` and `black` are whole-file/whole-repo tools by default, and running them without care can reformat lines that have nothing to do with UP006/UP035 (e.g. a coincidentally-adjacent line that was already imperfectly wrapped) | Inflates the diff, defeats the "AST comparison modulo annotation nodes" and "`git diff` classified line-by-line" evidence mechanisms above (a reflowed-but-behaviourally-identical line still shows up as a changed line, forcing every reviewer to re-derive that it's cosmetic), and risks masking a real accidental behaviour change inside noise | Run `ruff check . --select UP006,UP035 --fix` scoped to exactly the 11 files named in PROJECT.md's counts, not `ruff check . --fix` unscoped; run `black --check .` to confirm no *other* file needed reformatting, and treat any black-reformatted line outside the 11 files as a signal to investigate, not to accept |
| Expanding the todo's own file list correction into a full audit of *all* stale file-list references project-wide | The todo file itself is already known-stale (PROJECT.md: "The todo's own file list is stale"), which could tempt an executor into a broader "let's fix all stale references while we're here" pass | Out of scope for a milestone whose own goal statement is narrowly "drop the ignores and rewrite the usages" — broader documentation-hygiene sweeps are their own kind of work (cf. v0.9.3 Phase 68, which was a dedicated documentation-follow-through phase, not folded into the toolchain-fix phases that preceded it) | If other stale references are noticed, file them as todos; do not fix them inside this milestone's diff |

## Feature Dependencies

```
[Remove UP006/UP035 from ruff ignore]
    └──requires──> [All 113 violations resolved to zero]
                       └──requires──> [ruff --fix autofix pass, scoped to the 11 named files]
                       └──requires──> [Manual Iterator → collections.abc rewrite (not autofixable by this rule pair)]
                       └──requires──> [tests/ 4 files included, not just typsphinx/ 7 files]

[All 113 violations resolved to zero]
    └──requires──> [mypy typsphinx/ still green]
    └──requires──> [Full pytest suite still green]
    └──requires──> [black --check . still clean]

[Behaviour-neutrality evidence: zero pre-existing test-assertion edits]
    └──enhances──> [AST comparison modulo annotation nodes]
        (both needed together: assertion-edit-diff catches logic changes in tests themselves;
         AST-modulo-annotations catches logic changes in typsphinx/ source)

[Byte-identical .typ output over existing corpus]
    └──requires──> [Existing render-gate test suite already passing before this milestone starts]
    (this evidence is available near-for-free specifically because no other Phase Detail
     restructures translator.py/builder.py control flow in the same milestone)

[Clean docs build diff confined to type text]
    └──requires──> [Fresh clean-build warning baseline, taken in this milestone, not reused stale]
    (standing project memory: incremental docs rebuilds under-report warnings)

[CLAUDE.md prohibition rewritten to reflect completion]
    └──requires──> [Todo moved to todos/completed/]
        (rewrite should describe the todo's new location/status, not the pending/ path)

[CHANGELOG bullet under ## [Unreleased]]
    └──requires──> [The one visible side effect (rendered API typehints) is explicitly named]
    └──conflicts with──> [Any pyproject.toml version bump] (owner decision: stays 0.9.2, unpublished)

[PEP 604 sweep] ──conflicts──> [Minimal-diff evidence mechanisms above]
[from __future__ import annotations] ──conflicts──> [Runtime-behaviour-unchanged constraint]
[Public API/signature changes] ──conflicts──> [Milestone's own scope statement]
```

### Dependency Notes

- **Zero-violations requires the tests/ scope correction:** the pending todo (2026-07-22) lists only
  4 `typsphinx/` files and misses `template_registry.py`, `writer.py`'s `Tuple`, and all of `tests/`.
  PROJECT.md's own measurement (113 total, `tests/` 4 files / 21) is the authoritative discovery
  source; a plan built from the todo's file list alone under-covers by roughly 20% of the violations
  and 4 whole files, and CI's un-scoped `ruff check .` would still fail after "done."
- **Behaviour-neutrality evidence mechanisms are complementary, not substitutable:** the
  zero-pre-existing-test-edits check only sees `tests/`; the AST-modulo-annotations check only sees
  what's inside the compared files' function/module bodies outside annotations; the byte-identical
  `.typ`-corpus check only sees the deliverable, not the source. Table-stakes "full pytest green"
  is necessary but not sufficient alone — a broken annotation that mypy's generous suppression list
  hides could still pass pytest if no test happens to exercise that exact code path, which is why the
  AST-modulo-annotations and mypy-diff-free checks matter as independent signals.
- **CHANGELOG bullet depends on the docs-side evidence being run, not skipped:** the bullet must name
  the rendered-API-reference change as a concrete fact ("shows `dict[str, Any]` where it showed
  `Dict[str, Any]`"), which is only honestly stated if the clean-docs-build diff was actually
  performed in this milestone rather than assumed from the config value alone.
- **The `@preview` anti-feature and the file-touch list overlap by construction:** `builder.py`,
  `writer.py`, and `template_engine.py` all appear in both PROJECT.md's violation-count table and
  CLAUDE.md's `@preview` version-sync hazard list. This is a proximity risk, not a design conflict —
  worth a specific plan-time check that no changed line sits near a version-string declaration.

## MVP Definition

This milestone has no incremental-value ladder in the product sense — it is a single, atomic,
close-prep-shaped unit of contributor-tooling work. "MVP" here means the irreducible set that makes
the milestone count as done at all, versus evidence work that strengthens confidence but could in
principle be descoped without invalidating the result (though this project's own culture, evidenced
across every prior milestone read for this research, treats the evidence layer as non-optional in
practice).

### Launch With (v1 — table stakes, all required)

- [ ] Ruff ignore removed (both `UP035`/`UP006` lines and their deferral comments) — the milestone's
      literal goal
- [ ] All 113 violations resolved to zero, `tests/` included, discovered by
      `ruff check . --select UP006,UP035` not by the stale todo list
- [ ] `Iterator` moved to `collections.abc` (the one non-autofixable, non-container rewrite)
- [ ] Full gate quartet green: `black --check .`, `ruff check .` (unrestricted), `mypy typsphinx/`,
      full `pytest`
- [ ] `CLAUDE.md:75`'s prohibition rewritten to reflect completion
- [ ] Todo moved `pending/` → `completed/`
- [ ] CHANGELOG bullet under `## [Unreleased]`, contributor-tooling register, naming the one visible
      side effect
- [ ] Close-prep-only final phase: no version bump, no tag, no PyPI upload, no GitHub Release
      (owner decision, already locked)

### Add After Validation (evidence layer — strongly expected given project culture, but logically separable from "done")

- [ ] Zero pre-existing test-assertion edits, measured by `git diff --name-status`/`git diff` over
      `tests/`
- [ ] Full pytest collected-count and pass/skip-count identity before vs. after
- [ ] AST comparison modulo annotation nodes over the 11 changed files
- [ ] Byte-identical `.typ` output over the existing fixture/golden corpus (and ideally the real
      `-b typstpdf` compile of Sphinx's own `doc/` tree, per the v0.6.0/v0.6.1 precedent, if budget
      allows)
- [ ] mypy output string-identical (not just exit-code-green) before vs. after
- [ ] Clean docs build (`rm -rf docs/_build` first) with diff confined to type text in the API
      reference pages, fresh warning-count baseline

### Future Consideration (explicitly out of scope, not deferred-with-intent)

- [ ] PEP 604 `X | None` sweep — files its own todo if ever wanted, not part of this milestone
- [ ] `from __future__ import annotations` — never appropriate here; not a "later" item, a "no" item
- [ ] Any signature/public-API change surfaced incidentally — files its own todo

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|----------------------|----------|
| Remove ignore lines + resolve 113 violations | N/A (contributor-only) — HIGH for project hygiene | LOW | P1 |
| `tests/` scope correction (vs. stale todo list) | HIGH (silent CI failure otherwise) | LOW | P1 |
| `Iterator` → `collections.abc` | LOW individually, but named explicitly in scope | LOW | P1 |
| Full gate quartet re-run | HIGH (standing project bar) | LOW | P1 |
| CLAUDE.md + todo lifecycle housekeeping | MEDIUM (repo self-consistency) | LOW | P1 |
| CHANGELOG bullet | MEDIUM (contributor/user transparency on the one visible effect) | LOW | P1 |
| Zero pre-existing test-assertion edits check | HIGH (cheapest strong proof) | LOW | P1 |
| Full pytest count identity | MEDIUM (redundant with quartet but near-free) | LOW | P1 |
| AST comparison modulo annotation nodes | HIGH (most targeted proof for this exact change class) | MEDIUM (new small script) | P1 |
| Byte-identical `.typ` corpus check | HIGH (measures the actual deliverable) | LOW (reuses existing suite) | P1 |
| mypy output string-diff | LOW–MEDIUM (marginal over green) | LOW | P2 |
| Clean docs-build diff | MEDIUM (only real proof of the one visible side effect) | MEDIUM (full clean rebuild + diff) | P1 |
| PEP 604 sweep | none in this milestone | MEDIUM–HIGH if attempted | Refuse |
| `from __future__ import annotations` | none in this milestone | LOW to add, HIGH in downstream risk | Refuse |

**Priority key:**
- P1: Must have for this milestone to count as done, per the quality gate's own "every proposed
  evidence mechanism named concretely enough to become a success criterion" bar
- P2: Should have, cheap enough that skipping it needs a stated reason
- Refuse: Explicitly out of scope; would need its own future milestone/todo

## Sources

- `.planning/PROJECT.md` lines 1-90 (What This Is, Core Value, Current Milestone: v0.9.4) — HIGH
  confidence, primary project record
- `.planning/todos/pending/2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md` — HIGH
  confidence, primary source for why the ignore existed and the original (now stale) file list
- `CHANGELOG.md` `## [Unreleased]` section — HIGH confidence, direct read of the bullet register this
  milestone's own CHANGELOG entry must match
- `.planning/milestones/v0.9.3-ROADMAP.md` (Phase 68, Phase 69, constraints 13/14/15, Roadmap
  Evolution) — HIGH confidence, direct read; source of the "masked-AST-hash" precedent, adapted (not
  reused verbatim) above because that technique masked string/docstring nodes for a prose-only
  change, whereas this milestone's changes are annotation-only and need annotation-node masking
  instead
- `.planning/MILESTONES.md`, `.planning/RETROSPECTIVE.md` — HIGH confidence, corroborate the
  masked-AST-hash precedent and the "zero pre-existing test edits" / "byte-identical output" standing
  culture across v0.9.0-v0.9.3
- `pyproject.toml` (`[tool.ruff.lint] ignore`, `[tool.mypy]`), `docs/source/conf.py`
  (`sphinx_autodoc_typehints`, `autodoc_typehints = "description"`), `.github/workflows/ci.yml`
  (lint/type/py312/py313/cov/docs jobs), `tox.ini` (`docs-html`, `docs-pdf` envs) — HIGH confidence,
  direct reads in this research session
- Direct measurement in this research session: `ruff check . --select UP006,UP035` on the current
  tree returns exactly 113 errors, 94 fixable — confirms PROJECT.md's count rather than merely citing
  it
