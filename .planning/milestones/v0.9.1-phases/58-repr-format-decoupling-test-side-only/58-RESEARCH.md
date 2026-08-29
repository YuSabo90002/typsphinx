# Phase 58: `repr()`-Format Decoupling (test-side only) - Research

**Researched:** 2026-08-27
**Domain:** Test-suite refactoring (pytest, `ast`-based static analysis) — no production code
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01: The naming predicate is `value in text or repr(value) in text` — two forms, not four.**
  A four-form enumeration (raw / `repr()` / `'{value}'` / `"{value}"`) was considered and
  **rejected as redundant**: if `'C:\escape.typ'` is a substring of the message then the raw
  `C:\escape.typ` already is, so the two delimiter forms are strictly subsumed by the raw check.
  The only rendering the raw check does **not** subsume is `repr()`'s backslash-doubled form, which
  is why exactly one extra disjunct is needed. This is what makes the predicate hold across all
  three quoting regimes the milestone will pass through: `!r` today, MSG-02's delimiter-aware
  helper after Phase 60, and 57-11's hardcoded `'{value}'` in between.
  — Reversibility: reversible.

- **D-02: The predicate is applied to the extracted warning LINE, not to the whole captured output.**
  `tests/test_out02_escape_target_gate.py` asserts against `result.stdout + result.stderr` from a
  real `sphinx-build` subprocess. Asserting the raw form against the whole capture is unsound for
  SC#2: a raw path that leaks into the build output from *any* other source (a config echo, a
  traceback, a path Sphinx prints) would keep the test green after the path is removed from the
  warning, making the recorded falsification a false negative. The rewritten test therefore first
  selects the line(s) containing `ESCAPE_WARNING_SUBSTRING`
  (`"a path is not supported in a typst_documents target name"`, already a module constant at
  `tests/test_out02_escape_target_gate.py:36`), asserts exactly one such line exists, and applies
  the predicate to that line only. `tests/test_builder.py` already works on a single `caplog`
  record's `getMessage()` and needs no equivalent narrowing.
  — Reversibility: reversible.

- **D-03: The predicate takes the FULL path value, never its basename.**
  This is the trap SC#2 is aimed at. Measured: `builder.py:697` interpolates **two** path-valued
  fields, `{target!r}` *and* `{fallback!r}`, and for the `drive` shape they share a basename
  (`target = "C:\escape.typ"`, `fallback = "escape.typ"`). A "the basename appears in the message"
  predicate is therefore satisfied by `fallback` alone and stays GREEN with `target` fully
  removed — precisely the tautology SC#2 forbids. Verified for all three shapes that the
  full-value predicate goes RED under removal: `../escape.typ`, `/tmp/escape.typ` (POSIX) /
  `\\escape.typ` (nt), and `C:\escape.typ` are none of them substrings of the surviving
  `'escape.typ'` fallback text.
  — Reversibility: reversible.

- **D-04: A new leaf test-helper module `tests/_path_naming.py`.**
  Imported as `from _path_naming import path_named_in`. Measured this session by a live probe:
  `tests/` has **no `__init__.py`** and `pyproject.toml` sets `testpaths = ["tests"]` with the
  default `prepend` import mode, so pytest inserts `tests/` on `sys.path` and a bare
  `from _path_naming import ...` resolves — probe test collected and passed, then removed.
  Rejected: **`tests/conftest.py`** (it holds only fixtures today — `rootdir`, `sample_doctree`,
  `temp_sphinx_app`, `sphinx_config`, `mock_builder` — and `from conftest import ...` is a
  well-known pytest anti-pattern), and **inline duplication in both test modules** (two copies of
  a predicate that Phases 59 and 60 depend on is exactly the drift surface this phase exists to
  remove). The module carries **zero** `typsphinx` imports, mirroring MSG-02's leaf-module
  discipline on the product side.
  — Reversibility: reversible.

- **D-05: BOTH falsification routes are required, not either.**
  (a) A **permanent meta-test** for `path_named_in` in a new `tests/test_path_naming_predicate.py`:
  a message naming the value → `True`; a message with the value removed but a same-basename
  sibling still quoted (the D-03 trap, verbatim) → `False`; and the three-regime table (`!r`,
  `'{value}'`, delimiter-aware) → `True` for each. This is durable and turns RED if a future edit
  weakens the predicate.
  (b) A **recorded real falsification** against the live wiring: temporarily edit `builder.py:697`
  and `builder.py:1767` to drop the path field from the message, run each rewritten test, record
  the RED verbatim, `git checkout` the file. (a) alone proves the predicate is sound but not that
  the tests are wired to a message that actually carries the path; (b) alone proves nothing
  durable. SC#2's wording ("real runs, not asserted") is satisfied only by (b); its intent is
  satisfied only by both.
  — Reversibility: reversible.

- **D-06: The temporary product edit for (b) is made, measured and reverted inside ONE plan.**
  SC#4's `git diff --stat` runs at phase close as the proof it did not survive. The plan records
  `git status --porcelain typsphinx/` as empty immediately after the revert, in the same evidence
  file, before its commit. A dirty `typsphinx/` at commit time is a halt, not a deviation.
  — Reversibility: reversible.

- **D-07: Evidence file name is `58-DECOUPLING-EVIDENCE.md` — NOT `58-VERIFICATION.md`.**
  `{padded_phase}-VERIFICATION.md` is a name `gsd-verifier` reserves and overwrites wholesale; a
  plan that accumulates evidence under that name has it deleted at verify time. Follows the
  `57-MESSAGE-FIX-EVIDENCE.md` / `57-WINDOWS-FIX-EVIDENCE.md` precedent.
  — Reversibility: reversible.

- **D-08: The census is derived from a whole-tree sweep of `tests/`, classified on two axes.**
  It is never derived from the two known sites. Deriving the enumeration set from the two sites
  MSG-01 names would inherit the very blind spot the census exists to close (this project has paid
  for that framing error before). Axes:
  1. **Role** — *pass-criterion* (the `repr(...)`/`!r` sits inside the `assert` **test**
     expression, i.e. it decides GREEN/RED) vs *diagnostic-only* (it sits inside a failure-message
     f-string, a `pytest.fail`, an `ids=`, or a docstring — it cannot decide the verdict).
  2. **Value type** — path / identifier / list / bytes / int / other.

  Measured baseline this session (AST walk over `ast.Assert(...).test` across `tests/**/*.py`):
  **341** raw `repr(`/`!r` textual occurrences, of which exactly **9** are pass-criterion, all of
  them `repr()` calls and **zero** of them `!r` conversions:

  | Site | Value | Class | Disposition |
  |---|---|---|---|
  | `tests/test_out02_escape_target_gate.py:134` | `target` (`"C:\escape.typ"` etc.) | **path** | rewritten (MSG-01) |
  | `tests/test_builder.py:598` | `abs_uri` | **path** | rewritten (MSG-01) |
  | `tests/test_registry_container_shape_gate.py:142` | `["a", "b"]` | list | untouched |
  | `tests/test_registry_prewrite_validation_gate.py:278` | `"first-bad"` | identifier | untouched |
  | `tests/test_registry_prewrite_validation_gate.py:279` | `"second-bad"` (negative) | identifier | untouched |
  | `tests/test_template_engine.py:1317` | `malformed` (lang code) | identifier | untouched |
  | `tests/test_template_registry.py:832` | `["a", "b"]` | list | untouched |
  | `tests/test_template_registry.py:847` | `b"base.typ"` | bytes | untouched |
  | `tests/test_template_registry.py:1001` | `bad_value` (`None`/`123`/tuple) | other | untouched |

  A **third bucket** is recorded explicitly rather than dropped: *path-valued but format-asserting
  by design* — `TestWindowsPathEscapingRegressionGuard._assert_no_doubled_separator`
  (`tests/test_templates_path_collision_gate.py:445-455`) asserts the **absence** of `repr()`'s
  doubled-backslash form. It is the inverse of MSG-01's target and MSG-02's own gate depends on it.
  It must not be rewritten, and the census must say so in writing so Phase 60 does not re-litigate.

  Written to `58-REPR-CENSUS.md` in the phase directory (the file Phases 59 and 60 check their
  zero-test-edit claim against).
  — Reversibility: reversible.

- **D-09: The census is backed by an AST-based guard test, not left as a snapshot.** A new test
  parses every `tests/**/*.py` with `ast`, walks each `ast.Assert` node's **`.test`** expression
  only (never its `.msg`, which is why the 341 diagnostic occurrences do not pollute the result),
  collects `Call(func=Name('repr'))` and `FormattedValue(conversion=114)` hits, and asserts the hit
  set equals a recorded allowlist of the **seven** non-path sites above. Rationale: milestone
  constraint 9 says a plan in Phase 59/60 finding it must edit a test is "a signal the census was
  incomplete" — a guard is what makes incompleteness *detectable* instead of hypothetical, and the
  AST route is exact rather than grep-brittle. The AST walk is ~25 lines and was prototyped and run
  this session (result: 9 sites, matching the table). The guard test **must exclude its own file**
  from the sweep (its allowlist literals contain `repr(` in source form).
  — Reversibility: reversible — one file, deletable if the planner judges it exceeds the
  test-side budget; but it is the only mechanism that carries SC#3's value into Phases 59 and 60.

- **D-10: `git push -u origin gsd/v0.9.1-windows-path-correctness` lands in this phase.**
  Verified by a post-push `git branch -vv` showing tracking. Measured this session: the branch is at
  `72896623` with **no upstream**, and `git ls-remote --heads origin` matches nothing containing
  `0.9.1`. Note the decoy-pair hazard this project sees every milestone — sibling branches
  `gsd/v0.7.0-milestone`, `gsd/v0.7.1-milestone`, `gsd/v0.9.0-milestone` all exist locally from the
  commit helper. The canonical branch is the config-slug one, `gsd/v0.9.1-windows-path-correctness`,
  and **no `gsd/v0.9.1-milestone` decoy exists locally at all** this round — nothing to disambiguate,
  but do not create one.
  — Reversibility: reversible.

### Claude's Discretion

The owner selected "おすすめで進める" for all four gray areas, so every D-NN above is Claude's
recommendation locked as a decision. The planner retains discretion on:
- Plan decomposition (D-05's two routes may be one plan or two; the census + guard may be one or two).
- The exact signature/naming of `path_named_in` and whether it returns `bool` or raises.
- Whether the `58-REPR-CENSUS.md` table is generated by the same script that backs D-09's guard.

### Deferred Ideas (OUT OF SCOPE)

- **`57-REVIEW.md` IN-01 — a path containing a literal single quote.** Belongs to MSG-02's gate in
  Phase 60, which names it explicitly. This phase's predicate happens to tolerate it (the raw
  disjunct matches regardless of delimiter), but no test for it is added here.
- **Routing `builder.py:697` / `:1767` off `!r`.** Phase 60, MSG-03. This phase deliberately leaves
  both message sites byte-identical — that is what makes "zero test edits in 59/60" a meaningful
  claim rather than a circular one.
- **Extending the AST guard to `typsphinx/` (product-side `!r` census).** MSG-03's own scope in
  Phase 60 already enumerates the product sites; duplicating it as a guard here would pre-empt that
  phase's decisions.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| MSG-01 | The two existing tests that hard-code `repr()`'s output format as their pass criterion are rewritten to assert the *meaning* (the path is named in the message), before any message site is rewired. Both must stay green before and after. | Predicate design verified against live `builder.py:696-697` and `builder.py:1766-1768` message construction (Architecture Patterns, Code Examples). AST-guard mechanism independently reproduced this session (Code Examples §3), confirming D-08's 9-site table byte-for-byte. Validation Architecture section below defines the falsifiability sampling plan SC#2 requires. |
</phase_requirements>

## Summary

This is a test-side-only phase: zero lines under `typsphinx/` may survive into a commit (SC#4).
Everything measured this session against the live tree (commit `3b6c5c2e`, no drift from the
`72896623` tree CONTEXT.md measured against — `git diff --stat 72896623 HEAD -- typsphinx/ tests/
pyproject.toml` is empty) confirms every claim CONTEXT.md's D-01..D-10 locked. The two target
assertions (`tests/test_out02_escape_target_gate.py:134`, `tests/test_builder.py:598`) are exactly
where CONTEXT.md says, both currently pass on this POSIX host (`typst` is a core, not dev-only,
dependency — `pyproject.toml:29` — so any correctly `uv sync --extra dev`-provisioned worktree
venv has it, and a live run this session produced `4 passed` with zero skips), and the two message
sites (`builder.py:697`, `builder.py:1767`) are read-only in this phase.

The highest-value thing this research adds beyond CONTEXT.md is **independent reproduction of
D-09's AST guard**: the exact ~20-line script below (walking `ast.Assert(...).test` only, matching
`Call(func=Name('repr'))` and `FormattedValue(conversion=114)`) was run against the live tree this
session and returned **exactly the same 9 sites, in the same order**, as CONTEXT.md's table — this
is now a verified, copy-pasteable starting point for the planner rather than a description to
re-derive. One softer finding: a naive text-count of `repr(`/`!r}` occurrences across `tests/**/*.py`
this session returned 352, not CONTEXT.md's cited 341 — the discrepancy is almost certainly a
counting-methodology difference (what counts as "one occurrence" in an f-string with multiple `!r`
conversions, whether `tests/fixtures/`/`tests/roots/` are included) rather than a tree drift (the
`git diff --stat` above is empty). This is not load-bearing: D-09's guard is exact and re-derives
both the pass-criterion set and (if the planner chooses) the total count at test-run time, so
`58-REPR-CENSUS.md`'s narrative text should not assert a specific total-occurrence number as a test
target — only the **9 pass-criterion sites** are safety-critical, and those are locked.

`git push -u origin gsd/v0.9.1-windows-path-correctness` (D-10/SC#5) is unblocked: the branch
carries 7 commits ahead of `main` (up from the 3 CONTEXT.md measured at roadmap time — 2 doc-only
commits landed during context-gathering, 1 during earlier roadmap correction), has no upstream, and
no `gsd/v0.9.1-*` ref exists on `origin` to collide with. `.github/workflows/ci.yml`'s
`push`/`pull_request` triggers are scoped to `main`/`develop` only (confirmed by direct read), so
the push alone dispatches no CI — consistent with the precedent phases (53, 47) that also had to
`gh workflow run CI --ref <branch>` separately if CI confirmation was wanted; SC#5's own wording
here does not require a CI run, only the push+tracking, so the planner is not obligated to add one.

**Primary recommendation:** One plan (or two, per Claude's Discretion) builds `tests/_path_naming.py`
+ its meta-tests (D-05a) + a temporary-edit-and-revert falsification pass (D-05b) recorded to
`58-DECOUPLING-EVIDENCE.md`, another builds the AST-based census guard (D-08/D-09) using the
verified script below, and a small close-out step pushes the branch (D-10). Rewrite both target
assertions to call `path_named_in(...)` against the D-02-narrowed text; do not touch
`builder.py:697`/`:1767` except transiently and revertedly for D-05(b).

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Naming predicate (`path_named_in`) | Test / Test-support | — | Pure function, zero I/O, zero `typsphinx` imports (D-04) — lives in a leaf test-helper module, not in `typsphinx/` (this phase is test-side only). |
| Rewritten assertions in the two target tests | Test | — | Both already drive real product code (`sphinx-build` subprocess / `builder.post_process_images()`) — only the pass-criterion *expression* changes, not the exercised code path. |
| Meta-tests for the predicate (D-05a) | Test | — | Durable regression guard on the predicate itself, independent of any product wiring. |
| Real falsification (D-05b) | Test harness / temporary product edit | `typsphinx/builder.py` (transient, reverted) | The ONLY point in this phase that touches `typsphinx/`, and it must not survive to a commit (SC#4). |
| `repr()`/`!r` census (D-08) + AST guard (D-09) | Test / static analysis | — | Operates on `tests/**/*.py` source text via the stdlib `ast` module; no runtime coupling to `typsphinx/`. |
| Milestone branch push (D-10) | Git / CI infra | — | Repository-level, unrelated to any application tier. |

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `ast` (stdlib) | bundled with Python 3.13.13 (project floor 3.12) | Parse `tests/**/*.py`, walk `Assert.test` nodes, detect `repr()` calls / `!r` conversions | Exact, non-brittle (vs. grep/regex); zero new dependency, matching the milestone's stdlib-only standing invariant `[VERIFIED: /home/yuta/Documents/typsphinx/CLAUDE.md, .planning/REQUIREMENTS.md "Out of Scope" table]` |
| `pytest` | `>=8.4,<10` (installed: `9.1.1`) `[VERIFIED: pyproject.toml:35, live venv]` | Test framework already in use | Already the project's sole test runner |
| `pathlib` (stdlib) | bundled | Filesystem sweep (`Path("tests").rglob("*.py")`) for the census/guard | Already used throughout the test suite (`tests/test_out02_escape_target_gate.py:33-34`) |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `re` (stdlib) | bundled | Only if the planner wants a supplementary textual count for `58-REPR-CENSUS.md`'s narrative (non-authoritative) | Never for the pass-criterion detection itself — that must be the AST route (D-09); a regex-based census undercounts/overcounts by construction (this session's own regex recount landed at 352 vs. CONTEXT's 341 — see Common Pitfalls) |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Raw `ast.walk` + `isinstance` checks | `ast.NodeVisitor` subclass | `NodeVisitor` is the textbook-idiomatic approach for larger walks, but for a single-purpose "collect Assert.test hits" pass, plain `ast.walk()` + `isinstance` is fewer lines and was what was actually prototyped and verified this session; either is fine, `NodeVisitor` is not required. |
| `tests/_path_naming.py` as a bare module | A `tests/support/` sub-package with `__init__.py` | Rejected by D-04: introducing `__init__.py` anywhere under `tests/` changes pytest's import mode assumptions project-wide and is out of scope for a decoupling-only phase. |

**Installation:** None. Zero new dependencies — this phase is stdlib-only by design (`ast`,
`pathlib`, `re` are all part of Python 3.12+, the project's floor `[VERIFIED: pyproject.toml:10]`).

**Version verification:** `python3 --version` → `Python 3.13.13` in this environment
`[VERIFIED: live `python3 --version` this session]`; project floor `requires-python = ">=3.12"`
`[VERIFIED: pyproject.toml:10]`. `pytest>=8.4,<10` pinned in `pyproject.toml:35`, resolved to
`9.1.1` in the live `.venv` `[VERIFIED: live pytest session-start banner this session]`.

## Package Legitimacy Audit

No external packages are installed or newly depended upon in this phase — it is stdlib-only
(`ast`, `pathlib`, optionally `re`) plus the project's existing `pytest` dependency. The Package
Legitimacy Gate does not apply.

**Packages removed due to [SLOP] verdict:** none — no packages proposed.
**Packages flagged as suspicious [SUS]:** none.

## Architecture Patterns

### System Architecture Diagram

```
 sphinx-build subprocess              caplog capture (in-process)
 (test_out02_escape_target_gate.py)   (test_builder.py)
        |                                      |
        v                                      v
 result.stdout + result.stderr        warning_records[0].getMessage()
        |                                      |
        v                                      |
 [D-02] select line(s) containing              |
 ESCAPE_WARNING_SUBSTRING                       |
 (exactly-one assertion)                        |
        |                                      |
        +------------------+-------------------+
                           v
              tests/_path_naming.py
              path_named_in(value: str | PathLike,
                             text: str) -> bool
              # value in text or repr(value) in text  (D-01)
                           |
                +----------+----------+
                v                     v
        assert True              assert False
        (test PASSES)             (test FAILS,
                                    predicate/wiring broken)

 Separately, at census/guard time:

 tests/**/*.py source ---> ast.parse() ---> ast.walk(tree)
        |
        v
 for each ast.Assert node:
     walk ONLY node.test (never node.msg)   [D-09; verified this
        |                                    session -- see Code
        v                                    Examples #3]
     collect Call(func=Name('repr')) and
     FormattedValue(conversion==114) hits
        |
        v
 hit-set == recorded allowlist (7 non-path sites)?
    yes -> guard PASSES        no -> guard FAILS (census incomplete)
```

### Recommended Project Structure

```
tests/
├── _path_naming.py                    # NEW (D-04): path_named_in() -- zero typsphinx imports
├── test_path_naming_predicate.py      # NEW (D-05a): meta-tests for path_named_in
├── test_repr_census_guard.py          # NEW (D-08/D-09): AST-walk guard over tests/**/*.py
├── test_out02_escape_target_gate.py   # MODIFIED: line 134 rewritten to use path_named_in
├── test_builder.py                    # MODIFIED: line 598 rewritten to use path_named_in
└── conftest.py                        # UNCHANGED (fixtures only -- D-04 explicitly rejects adding helpers here)
```

### Pattern 1: Two-form naming predicate (D-01)

**What:** `value in text or repr(value) in text` — exactly two disjuncts.
**When to use:** Any assertion that a path (or other value) is *named* in a message, independent
of which quoting convention produced the message.
**Example:**
```python
# tests/_path_naming.py -- new leaf module, zero typsphinx imports (D-04)
import os


def path_named_in(value: str | os.PathLike, text: str) -> bool:
    """True if `value` is named in `text`, regardless of whether the
    message quotes it with `!r` (repr()'s backslash-doubling form), a
    hardcoded `'{value}'`, or a future delimiter-aware helper. D-01: two
    disjuncts, not four -- the delimiter forms are strictly subsumed by
    the raw-value check; only repr()'s doubled-backslash rendering is
    NOT subsumed, hence exactly one extra disjunct.
    """
    value_str = os.fspath(value)
    return value_str in text or repr(value_str) in text
```
Source: derived directly from D-01/D-03's locked rationale and the live `builder.py:696-697`
message construction verified this session — not from an external doc (no third-party API here).

### Pattern 2: Line-narrowing before predicate application (D-02)

**What:** Extract only the line(s) containing a known warning-substring before applying the
predicate, rather than searching the whole captured output.
**When to use:** Any assertion against a multi-line subprocess capture (`stdout + stderr`) where a
raw value could coincidentally appear elsewhere (a traceback, a config echo) and mask a real
regression.
**Example:**
```python
# Inside test_escape_shape_refused_with_containment_proof, replacing the
# single `assert repr(target) in combined_output` line:
warning_lines = [
    line for line in combined_output.splitlines()
    if ESCAPE_WARNING_SUBSTRING in line
]
assert len(warning_lines) == 1, (
    f"Expected exactly one warning line naming the refused target:\n"
    f"{combined_output}"
)
assert path_named_in(target, warning_lines[0]), (
    f"Expected the warning to name the offending target {target!r} "
    f"(raw or repr()'d):\n{warning_lines[0]}"
)
```
`tests/test_builder.py:598`'s equivalent needs no line-narrowing — it already operates on a single
`caplog` record's `getMessage()` (verified: `warning_records = [... 1 record ...]`,
`message = warning_records[0].getMessage()` at `tests/test_builder.py:585-587`), so the rewrite
there is a direct one-line substitution: `assert path_named_in(abs_uri, message)`.

### Anti-Patterns to Avoid

- **Basename-only matching:** `assert path.basename(value) in text` — satisfied by `fallback`
  alone in the `drive` shape (D-03's trap: `fallback = "escape.typ"` is a substring-equal basename
  of `target = "C:\escape.typ"`), so it stays GREEN when the actual `target` value is removed from
  the message. This is the exact tautology SC#2 forbids.
- **Whole-capture matching without line-narrowing:** loses the "recorded falsification actually
  falsifies" property (D-02) — a raw path leaking from any unrelated source keeps the test green.
- **Re-pasting the product's f-string into the test:** `TestWindowsPathEscapingRegressionGuard`'s
  own docstring states the rule this phase must also follow — call the real product function/path,
  never a copy of its format string, or a regression that reverts the product code silently passes.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Detecting `repr()`/`!r` usage inside assertions | A regex/grep-based scanner over source text | `ast.walk()` over `ast.Assert(...).test` matching `Call(func=Name('repr'))` and `FormattedValue(conversion=114)` | Exact — a regex cannot distinguish an assertion's `.test` from its `.msg`, a docstring, or a comment without false positives/negatives (this session's own textual regex recount landed at 352 vs. the AST walk's exact 9 pass-criterion sites — the two numbers measure different things and neither substitutes for the other). |
| Running `sphinx-build` for the escape-shape test | A hand-rolled subprocess wrapper | The existing `_run_sphinx_build()` helper (`tests/test_out02_escape_target_gate.py:38-56`) | Already exists, already invoked as `sys.executable -m sphinx` (never a resolved `sphinx-build` binary), matching the interpreter-fidelity requirement this suite already established. |
| A shared predicate module | Duplicating the predicate inline in both test files | `tests/_path_naming.py` (D-04) | Two copies of a predicate that Phases 59/60 depend on is exactly the drift surface D-04 exists to remove. |

**Key insight:** every piece of new test infrastructure this phase needs (AST walking, subprocess
invocation, line extraction) already exists either in the stdlib or in this test suite's own
established patterns — there is no library gap to fill.

## Common Pitfalls

### Pitfall 1: A `SKIP` verdict misread as a green run
**What goes wrong:** `test_escape_shape_refused_with_containment_proof` is
`@pytest.mark.skipif(not TYPST_AVAILABLE, ...)` (verified: `tests/test_out02_escape_target_gate.py:96-99`).
If the plan's worktree venv lacks `typst-py`, the test SKIPs rather than passes, and a `pytest`
exit code of `0` can mask that in casual evidence-gathering.
**Why it happens:** `typst` is listed as a core dependency (`pyproject.toml:29`,
`"typst>=0.15.0,<0.16"`), so it should always install via `uv sync --extra dev` — but a
misconfigured or stale venv could still lack it.
**How to avoid:** the evidence file (D-07/`58-DECOUPLING-EVIDENCE.md`) must record the actual
pytest summary line (`"N passed"` with the target test named, not `"N passed, M skipped"` covering
it) for both the before and after runs SC#2 requires — not just the process exit code. Verified
this session on the current tree: `pytest tests/test_out02_escape_target_gate.py::test_escape_shape_refused_with_containment_proof tests/test_builder.py::test_post_process_images_rehome_escape_relocates_with_warning -q` → `4 passed in 0.86s`, zero skips.
**Warning signs:** an evidence file that quotes only `echo $?` / `returncode == 0` without the
literal pytest summary line naming the tests as `passed`.

### Pitfall 2: The D-03 fallback trap
**What goes wrong:** A predicate weaker than full-value matching (e.g. basename-only, or "any
substring of the value") stays GREEN after the real `target` is removed from the message, because
`builder.py:697`'s `fallback` field is `target`'s basename for the `drive` shape.
**Why it happens:** `posixpath.basename(fallback_source)` (verified: `typsphinx/builder.py:680`)
computes `fallback` from the same stem `target` was derived from; for `"C:\escape.typ"` (no `/`),
the basename equals the whole trailing segment, i.e. `"escape.typ"` — a true substring of
`repr("C:\escape.typ")` too, so a naive "any known-value substring appears" predicate can't tell
`target` was removed if `fallback` is still present.
**How to avoid:** D-05(a)'s meta-test table must include this exact case (message with `fallback`
quoted, `target` absent) asserting `path_named_in(target, message) is False`.
**Warning signs:** a meta-test suite that only tests the positive case (value present → `True`)
without a same-basename-sibling negative case.

### Pitfall 3: Census total count is a soft, method-dependent number
**What goes wrong:** Treating "341" (CONTEXT.md D-08's cited total textual `repr(`/`!r`
occurrence count) as a fixed target to reproduce exactly.
**Why it happens:** Verified this session: an AST walk restricted to `Assert.test` nodes
(the sound, load-bearing count) reproduces **exactly 9** sites, byte-for-byte matching CONTEXT.md's
table — that count is solid. But a separate textual regex recount of ALL `repr(`/`!r}` occurrences
across `tests/**/*.py` (diagnostic + pass-criterion combined) returned **352** this session, not
341, most likely due to a difference in what one method counts as "one occurrence" (e.g. an
f-string with two `!r` conversions on one line) rather than any tree drift — `git diff --stat
72896623 HEAD -- tests/` is empty, confirming the tree hasn't changed.
**How to avoid:** `58-REPR-CENSUS.md` should present its own script's own count as authoritative
narrative text (not asserted against a hardcoded prior number), and D-09's guard test must assert
only the **pass-criterion allowlist** (the 9 sites / their locations), never a total occurrence
count.
**Warning signs:** a test that asserts `total_occurrences == 341` (or `== 352`) — either constant
is fragile to counting-methodology drift and neither is the safety-critical number.

### Pitfall 4: `mypy` does not gate `tests/`, but `black`/`ruff` do
**What goes wrong:** Assuming the new test modules need to satisfy `mypy typsphinx/`'s strictness,
or conversely assuming lint doesn't apply to `tests/` at all.
**Why it happens:** Verified this session: `tox.ini`'s `type` environment runs `mypy typsphinx/`
only (`tox.ini:52`) — `tests/` is out of mypy's scope entirely. But the `lint` environment runs
`black --check .` and `ruff check .` (`tox.ini:44-45`) — both apply repo-wide, including `tests/`.
**How to avoid:** new modules (`tests/_path_naming.py`, `tests/test_path_naming_predicate.py`,
the AST guard test) must be `black`-formatted and `ruff`-clean (the project's existing
`[tool.ruff.lint]` ignore list at `pyproject.toml:118-134` already covers common test-file
patterns like `F841`/`B017`), but do not need type annotations beyond what's idiomatic — `mypy`
will never check them in CI.
**Warning signs:** running only `mypy typsphinx/` and believing the whole tree is clean; running
`black`/`ruff` scoped to `typsphinx/` only and missing new `tests/` files.

### Pitfall 5: Evidence file name collision with the verifier's reserved name
**What goes wrong:** Naming the accumulated evidence file `58-VERIFICATION.md`.
**Why it happens:** `gsd-verifier` reserves and overwrites `{padded_phase}-VERIFICATION.md`
wholesale at verify time (project-wide learned hazard, `gsd-verifier-clobbers-verification-md`) —
a plan that writes its falsification records there loses them.
**How to avoid:** D-07 locks the name `58-DECOUPLING-EVIDENCE.md`, following the
`57-MESSAGE-FIX-EVIDENCE.md` / `57-WINDOWS-FIX-EVIDENCE.md` precedent (verified: both files exist
under `.planning/milestones/v0.9.0-phases/57-v0-9-0-release-prep-prep-only/`).
**Warning signs:** any plan task that writes to a path literally named `*-VERIFICATION.md`.

### Pitfall 6: Worktree isolation and the D-06 revert
**What goes wrong:** D-05(b)'s temporary edit to `builder.py:697`/`:1767` is made in a worktree
that was never freshly provisioned, so `uv run pytest` imports the MAIN tree's unchanged
`typsphinx` package instead of the worktree's edited copy — the "RED" observed is not actually
proof of anything, and later the "clean revert" check passes trivially because nothing was ever
really exercised.
**Why it happens:** `CLAUDE.md`'s "Worktree-isolated execution" section documents exactly this
failure mode (verified live: this session's shell is the MAIN tree — `test -f .git` → false,
`.git` is a directory — so an executor spawned for this phase must run its own
`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` before anything, per the
standing mandatory rule).
**How to avoid:** the plan must invoke the per-worktree provisioning block verbatim before D-05(b)
runs, and record `git status --porcelain typsphinx/` as empty **inside the evidence file, in the
same worktree**, immediately after `git checkout` reverts the temporary edit — before that
worktree's commit.
**Warning signs:** an evidence file whose RED output doesn't match the exact message text the
temporary edit would produce, or a revert-check run from a different shell/worktree than the edit.

## Code Examples

### 1. The naming predicate module (D-01, D-03, D-04)

```python
# tests/_path_naming.py
"""
Format-agnostic predicate for asserting that a path value is NAMED in a
message, independent of the quoting convention the message site uses.

D-01: exactly two disjuncts. If a delimiter form (`'{value}'`,
`"{value}"`, or a future delimiter-aware helper's output) wraps `value`,
the raw `value` is already a substring of the message -- the delimiter
characters add nothing the raw check doesn't already catch. The ONE
rendering the raw check misses is repr()'s backslash-doubling: `repr()`
does not add delimiters this predicate cares about, it mutates the VALUE
itself (each `\\` becomes `\\\\`). Hence one extra disjunct, not three.

Zero typsphinx imports (mirrors MSG-02's leaf-module discipline).
"""

import os


def path_named_in(value: str | os.PathLike, text: str) -> bool:
    value_str = os.fspath(value)
    return value_str in text or repr(value_str) in text
```

### 2. Meta-test table skeleton (D-05a)

```python
# tests/test_path_naming_predicate.py
from _path_naming import path_named_in


def test_raw_value_present_is_named():
    assert path_named_in("C:\\escape.typ", "target: C:\\escape.typ") is True


def test_repr_quoted_value_is_named():
    # !r's actual rendering: repr() doubles every backslash.
    message = f"target: {'C:\\escape.typ'!r}"
    assert path_named_in("C:\\escape.typ", message) is True


def test_hardcoded_single_quoted_value_is_named():
    # 57-11's interim quoting form: '{value}' with no repr() escaping.
    message = "target: 'C:\\escape.typ'"
    assert path_named_in("C:\\escape.typ", message) is True


def test_d03_fallback_trap_is_not_a_false_positive():
    # The value under test ("C:\escape.typ") is ABSENT; only its
    # same-basename sibling ("escape.typ") is quoted. This is the exact
    # shape builder.py:697 produces for the drive-qualified escape shape.
    message = "using 'escape.typ' instead"
    assert path_named_in("C:\\escape.typ", message) is False


def test_delimiter_aware_helper_form_is_named():
    # Placeholder for MSG-02's eventual output shape -- Phase 60 will
    # confirm the exact delimiter; any delimiter wrapping the raw value
    # satisfies the raw-value disjunct regardless of which character.
    message = "target: |C:\\escape.typ|"
    assert path_named_in("C:\\escape.typ", message) is True
```

### 3. AST-based pass-criterion detector — reproduced and verified this session

```python
# Verified this session (2026-08-27) against the live tree at 3b6c5c2e
# (identical to the 72896623 tree CONTEXT.md measured -- git diff --stat
# over typsphinx/ tests/ pyproject.toml is empty between the two).
# Output: exactly 9 hits, in this exact order, matching D-08's table:
#   tests/test_out02_escape_target_gate.py:134
#   tests/test_builder.py:598
#   tests/test_registry_container_shape_gate.py:142
#   tests/test_registry_prewrite_validation_gate.py:278
#   tests/test_registry_prewrite_validation_gate.py:279
#   tests/test_template_engine.py:1317
#   tests/test_template_registry.py:832
#   tests/test_template_registry.py:847
#   tests/test_template_registry.py:1001
import ast
import pathlib

root = pathlib.Path("tests")
hits = []
for f in root.rglob("*.py"):
    if "__pycache__" in f.parts:
        continue
    # D-09: the guard's OWN file must be excluded from the sweep --
    # its allowlist literals contain "repr(" in source form.
    if f.name == "test_repr_census_guard.py":
        continue
    tree = ast.parse(f.read_text(), filename=str(f))
    for node in ast.walk(tree):
        if isinstance(node, ast.Assert):
            # D-09: walk ONLY node.test, never node.msg -- .msg is where
            # the 300+ diagnostic-only occurrences live and must not
            # pollute the pass-criterion result. `ast.Assert(test, msg)`
            # per docs.python.org/3/library/ast.html [CITED].
            for sub in ast.walk(node.test):
                if (
                    isinstance(sub, ast.Call)
                    and isinstance(sub.func, ast.Name)
                    and sub.func.id == "repr"
                ):
                    hits.append((str(f), sub.lineno))
                # FormattedValue.conversion == 114 (ord('r')) means !r
                # formatting; -1 no formatting, 115 == !s. Per
                # docs.python.org/3/library/ast.html [CITED].
                if isinstance(sub, ast.FormattedValue) and sub.conversion == 114:
                    hits.append((str(f), sub.lineno))
```

`ast.Assert` field shape (`test`, `msg`) and `FormattedValue.conversion`'s integer encoding
(`114 == !r`) are both `[CITED: docs.python.org/3/library/ast.html]`.

## State of the Art

Not applicable in the usual sense — this phase does not touch a fast-moving library. The one
relevant "current practice" note: `tests/` having no `__init__.py` and relying on pytest's default
`prepend` import mode to expose bare top-level test-support modules is the project's existing,
already-probed convention (D-04) — `[CITED: docs.pytest.org/en/stable/explanation/pythonpath.html]`
confirms this is standard, documented pytest behavior, not a project-specific hack: "pytest will
find `foo/bar/tests/test_foo.py` and realize it is NOT part of a package given that there's no
`__init__.py` file in the same directory. It will then add `root/foo/bar/tests` to `sys.path`."
The pytest community independently flags `from conftest import helper` as fragile
(`[CITED: github.com/pytest-dev/pytest/discussions/11274]`), reinforcing D-04's rejection of that
route in favor of the dedicated `tests/_path_naming.py` leaf module.

**Deprecated/outdated:** nothing in this phase's scope.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `58-REPR-CENSUS.md`'s narrative total-occurrence count should be generated fresh by whichever script the planner writes, rather than asserted to equal either 341 (CONTEXT.md) or 352 (this session's independent regex recount) | Common Pitfalls #3, Summary | Low — neither number is safety-critical (only the 9-site pass-criterion allowlist is), but a plan that hardcodes either total as a test assertion would be needlessly brittle to future test-file additions that add diagnostic-only `repr()`/`!r` usage. |
| A2 | `git push -u origin gsd/v0.9.1-windows-path-correctness` alone (no `gh workflow run CI --ref`) satisfies SC#5 as literally worded | Summary | Low-Medium — if the phase's actual reviewer expects a completed CI run as evidence (as Phase 53's SC#2 explicitly required), a bare push would be judged insufficient; re-read SC#5's exact wording at plan time and add a CI dispatch step if in doubt, following the `gh workflow run CI --ref <branch>` precedent from Phase 53. |

**If this table is empty:** N/A — see above; both entries are low-risk clarifications, not
compliance/security/retention-policy assumptions.

## Open Questions

1. **Does the planner want the census table (`58-REPR-CENSUS.md`) and the AST guard
   (`tests/test_repr_census_guard.py`) generated from one shared script, or written independently?**
   - What we know: CONTEXT.md's "Claude's Discretion" section explicitly leaves this open. The
     verified script in Code Examples #3 is a complete, working basis for both — the census table
     is just this script's output rendered as markdown, and the guard is the same script's hit-set
     compared against a recorded allowlist.
   - What's unclear: whether one Python module should serve both purposes (imported by the guard
     test AND run standalone to regenerate the markdown table) or whether that coupling is
     over-engineering for a one-time census.
   - Recommendation: a single small module (e.g. `tests/_repr_census.py`, mirroring the
     `_path_naming.py` leaf-module pattern) exposing a `find_pass_criterion_repr_sites() -> list[tuple[str,int]]`
     function, imported by both the guard test and an optional one-off script/task that renders
     `58-REPR-CENSUS.md` — avoids duplicating the ~20-line AST walk.

2. **Exact plan decomposition — one plan or two for D-05's two falsification routes, and one plan
   or two for census+guard?**
   - What we know: CONTEXT.md defers this explicitly to the planner.
   - What's unclear: whether wave-parallelism benefits from splitting (e.g. the predicate module +
     meta-tests as one plan, the two target-test rewrites as a second, the census+guard as a
     third, the branch push as a fourth) versus a smaller number of larger plans.
   - Recommendation: given this is a small, single-file-family (`tests/`) phase with no
     cross-file collision hazard analogous to ROADMAP constraint 4 (that constraint concerns
     `builder.py`, which this phase does not durably touch), 2-3 plans is likely sufficient; the
     planner should weigh plan-count against the worktree-isolation overhead documented in
     `CLAUDE.md`.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `typst` (typst-py) | `test_escape_shape_refused_with_containment_proof`'s `skipif` gate | ✓ | `>=0.15.0,<0.16` pinned; live venv has it (core dependency, not dev-only) | If genuinely absent in a worktree venv, the test SKIPs rather than fails — see Common Pitfalls #1; re-run `uv sync --extra dev` in that worktree. |
| `pytest` | Test framework | ✓ | `9.1.1` in live `.venv` (`pyproject.toml:35` pins `>=8.4,<10`) | — |
| `ast` (stdlib) | D-09's guard | ✓ | bundled with Python 3.13.13 | — |
| `black` / `ruff` | Lint gate over `tests/` (new modules included) | ✓ | project-pinned in `pyproject.toml` dev extras | — |
| `mypy` | Type gate | ✓ (but scoped to `typsphinx/` only — does not check `tests/`, verified `tox.ini:52`) | — | Not applicable to this phase's new files. |
| GitHub CI (`ci.yml`) | SC#5 (optional, see A2) | N/A on bare push | — | `push`/`pull_request` triggers scoped to `main`/`develop` only — the milestone-branch push alone dispatches nothing; `workflow_dispatch` is present (`ci.yml:8`) if the planner wants `gh workflow run CI --ref <branch>` as additional SC#5 evidence. |

**Missing dependencies with no fallback:** none.

**Missing dependencies with fallback:** typst-py absence (fallback: re-provision the worktree venv).

## Validation Architecture

This is a **test-side phase whose deliverable IS test code** — there is no separate "product"
layer to add coverage on top of. The validation question is not "what tests exist for the
feature" but "how do we prove the new/rewritten tests are themselves falsifiable, sound, and not
tautological." SC#1-SC#3 are exactly this: the rewrite must (1) stop asserting format, (2) be
proven neither a regression nor a tautology via a REAL recorded RED, and (3) have its enumeration
recorded and guarded so it can't silently rot.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 9.1.1 (`pyproject.toml:35` pins `>=8.4,<10`) |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]` (`testpaths = ["tests"]`, `addopts = "-v --strict-markers"`, `filterwarnings` escalates `DeprecationWarning`/`PendingDeprecationWarning` to errors) |
| Quick run command | `uv run pytest tests/test_out02_escape_target_gate.py::test_escape_shape_refused_with_containment_proof tests/test_builder.py::test_post_process_images_rehome_escape_relocates_with_warning -q` |
| Full suite command | `uv run pytest` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| MSG-01 | `path_named_in` correctly distinguishes "value named" from "value absent, sibling present" (D-01/D-03) | unit (meta-test) | `uv run pytest tests/test_path_naming_predicate.py -x` | ❌ Wave 0 — new file |
| MSG-01 | The escape-target-gate test still passes pre-rewrite and post-rewrite, real `sphinx-build` subprocess (D-02, D-05a-real-wiring-half) | integration | `uv run pytest tests/test_out02_escape_target_gate.py::test_escape_shape_refused_with_containment_proof -q` | ✅ exists, rewritten in place |
| MSG-01 | The image-rehome warning test still passes pre-rewrite and post-rewrite, real `builder.post_process_images()` call | integration | `uv run pytest tests/test_builder.py::test_post_process_images_rehome_escape_relocates_with_warning -q` | ✅ exists, rewritten in place |
| MSG-01 | A real, recorded falsification (temporary `builder.py` edit dropping the path field) turns both rewritten tests RED (D-05b) | manual-only, recorded | Run the two commands above against the temporarily-edited `builder.py`; record RED verbatim in `58-DECOUPLING-EVIDENCE.md`; `git checkout typsphinx/builder.py` to revert | ❌ Wave 0 — this is a one-time recorded procedure, not a permanent automated test (by construction: the falsifying edit must not survive) |
| MSG-01 | The `repr()`/`!r` census's pass-criterion set stays at exactly the recorded allowlist (D-08/D-09) | unit (static analysis) | `uv run pytest tests/test_repr_census_guard.py -x` | ❌ Wave 0 — new file |

### Sampling Rate

- **Per task commit:** the quick run command above (both target tests + any new predicate/guard
  test file touched by that task).
- **Per wave merge:** `uv run pytest` (full suite) — this phase touches shared test infrastructure
  (`tests/_path_naming.py` is importable from anywhere `tests/` is on `sys.path`), so a full-suite
  run at each wave boundary catches any accidental collision with an unrelated test module.
- **Phase gate:** full suite green, `black --check .` and `ruff check .` clean (both apply to the
  new `tests/` files — see Common Pitfalls #4), before `/gsd-verify-work`. `mypy typsphinx/` is
  unaffected by this phase (no `typsphinx/` file changes survive to commit) and should show a
  byte-identical result to the pre-phase baseline.

### Wave 0 Gaps

- [ ] `tests/_path_naming.py` — the predicate itself (D-04)
- [ ] `tests/test_path_naming_predicate.py` — meta-tests (D-05a)
- [ ] `tests/test_repr_census_guard.py` (or the planner's chosen name) — AST-based guard (D-08/D-09)
- [ ] `58-DECOUPLING-EVIDENCE.md` — the recorded real-falsification procedure and its output (D-05b, D-06)
- [ ] `58-REPR-CENSUS.md` — the written census table (D-08)
- [ ] No framework install needed — `pytest`, `ast`, `pathlib` all already present.

## Security Domain

`security_enforcement` is `true` in `.planning/config.json` (`security_asvs_level: 1`,
`security_block_on: "high"`), so this section is required even though this phase touches no
production code, no user input surface, no authentication, and no cryptography — it modifies only
`tests/` and pushes a git branch.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | N/A — no auth surface in this phase |
| V3 Session Management | no | N/A |
| V4 Access Control | no | N/A |
| V5 Input Validation | no | This phase does not add input handling; `path_named_in()`'s only "input" is trusted test-authored literal strings and the product's own log/output text, never external/untrusted input |
| V6 Cryptography | no | N/A — `hashlib.sha1` usage elsewhere in the suite is pre-existing and untouched by this phase |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Temporary product-code edit (D-05b) accidentally surviving into a commit, silently reintroducing a defect | Tampering (of the codebase's own trusted state, not an external actor) | SC#4's `git diff --stat` check over the phase's own commit range, PLUS the plan-level `git status --porcelain typsphinx/` empty-check immediately after revert (D-06) — a dirty `typsphinx/` at commit time is a hard halt, not a warning. |
| A weakened/tautological test assertion silently passing forever (the class SC#2 exists to prevent) | Repudiation-adjacent (a false claim of correctness that can't later be disproven) | D-05's two independently-required falsification routes (durable meta-test + one-time recorded real RED) — this IS the mitigation, not an add-on. |

No injection, auth, session, or crypto surface is introduced or modified by this phase.

## Sources

### Primary (HIGH confidence)

- Live repository reads this session, all `[VERIFIED]`: `typsphinx/builder.py:660-700,1760-1772`
  (message construction sites), `tests/test_out02_escape_target_gate.py:1-150` (target assertion
  and its surrounding fixture), `tests/test_builder.py:540-610` (target assertion),
  `tests/test_templates_path_collision_gate.py:400-470` (`TestWindowsPathEscapingRegressionGuard`
  precedent), `tests/conftest.py:1-80` (existing fixtures, confirming D-04's "no plain helpers"
  claim), `pyproject.toml:1-152` (`testpaths`, `filterwarnings`, `[tool.ruff]`, `[tool.mypy]`,
  core/dev dependency split), `tox.ini` (`mypy typsphinx/` scope, `black`/`ruff` whole-tree scope),
  `.github/workflows/ci.yml:1-8` (push/PR trigger scope, `workflow_dispatch` presence).
- Live commands this session: `git diff --stat 72896623 HEAD -- typsphinx/ tests/ pyproject.toml`
  (empty — tree unchanged from CONTEXT.md's measurement point), `git ls-remote --heads origin`,
  `git branch -a`, `git log --oneline main..gsd/v0.9.1-windows-path-correctness` (7 commits),
  `python3 -c "import ast; ..."` prototype reproducing the exact 9-site D-08/D-09 table, a live
  `pytest -q` run of both target tests (`4 passed`, zero skipped).

### Secondary (MEDIUM confidence)

- `[CITED: docs.python.org/3/library/ast.html]` — `ast.Assert(test, msg)` field shape;
  `ast.FormattedValue.conversion` encoding (`114` = `!r`/repr, `115` = `!s`, `-1` = none).
- `[CITED: docs.pytest.org/en/stable/explanation/pythonpath.html]` — pytest's default `prepend`
  import mode inserting a `__init__.py`-less test directory directly onto `sys.path`.
- `[CITED: github.com/pytest-dev/pytest/discussions/11274]` — community confirmation that
  `from conftest import helper` is a known-fragile pattern, reinforcing D-04's module choice.

### Tertiary (LOW confidence)

None used — every claim in this document is either directly verified against the live repository
this session or cited to an official doc page returned by search this session.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — stdlib-only, versions read live from the venv and `pyproject.toml`.
- Architecture: HIGH — the predicate and AST-guard designs are locked decisions from CONTEXT.md,
  independently re-verified against the live tree and (for the AST guard) actually re-executed
  this session with matching output.
- Pitfalls: HIGH — all six pitfalls are grounded in a live measurement this session (message-site
  reads, `tox.ini`/`pyproject.toml` reads, or an executed script), not recalled from training data.

**Research date:** 2026-08-27
**Valid until:** 30 days (stable domain — stdlib `ast`/pytest behavior, no fast-moving dependency)
