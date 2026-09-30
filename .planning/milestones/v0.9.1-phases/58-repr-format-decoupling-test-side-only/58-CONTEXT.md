# Phase 58: `repr()`-Format Decoupling (test-side only) - Context

**Gathered:** 2026-08-27
**Status:** Ready for planning

<domain>
## Phase Boundary

Rewrite the two existing tests that hard-code `repr()`'s output format as their pass criterion so
they assert the *meaning* — that the offending path is **named** in the message — under a predicate
that holds whether the message site quotes with `!r`, with a hardcoded `'{value}'`, or with the
delimiter-aware helper MSG-02 introduces. Record and classify the `repr(...)` / `!r` census in
`tests/`. Prove the rewrite is neither a regression nor a tautology. Push the milestone branch to
`origin`. Requirement: **MSG-01**.

**In scope:**

- `tests/test_out02_escape_target_gate.py:134` — `assert repr(target) in combined_output`, in
  `test_escape_shape_refused_with_containment_proof`, parametrized over
  `shape ∈ {traversal, absolute, drive}` and running **unconditionally on every platform**.
- `tests/test_builder.py:598` — `assert repr(abs_uri) in message`, in
  `test_post_process_images_rehome_escape_relocates_with_warning`.
- One shared, format-agnostic naming predicate (D-02) and its own meta-tests (D-05).
- A recorded, real falsification of both rewritten assertions (D-06), plus the recorded
  pre-rewrite / post-rewrite green runs SC#2 demands.
- The full `repr(` / `!r` census of `tests/`, classified and written down (D-07), plus an
  AST-based guard test that keeps the path-valued pass-criterion count at zero (D-08).
- `git push -u origin gsd/v0.9.1-windows-path-correctness` (SC#5).

**Out of scope:**

- **Any change under `typsphinx/`.** SC#4 proves this by `git diff --stat` over the phase's own
  range. The temporary product edit D-06 requires is made, measured, and reverted inside a single
  plan; it must not survive into a commit.
- **Any of the other seven `assert repr(...)` sites** — measured this session, all seven are
  identifier / list / bytes / int-valued and correctly stay untouched (D-07's table names each).
- **`TestWindowsPathEscapingRegressionGuard`** (`tests/test_templates_path_collision_gate.py:411+`).
  Its `_assert_no_doubled_separator` asserts on quoting *format* on purpose, in the inverse
  direction, and MSG-02's own gate depends on it. It is classified, not rewritten (D-07).
- **Message-site rewiring** — `builder.py:697` and `builder.py:1767` keep `!r` in this phase. They
  move in Phase 60 (MSG-03).
- Widening the predicate to cover quoting forms this project does not use (D-01 rejects the
  four-form enumeration in favour of the two-form minimal-complete one).

</domain>

<decisions>
## Implementation Decisions

Every measured value below was taken **this session (2026-08-27)** against the live tree at
`72896623`, not from recall. The owner delegated all four gray areas ("おすすめで進める"); the
recommendations below are locked as decisions.

### The replacement assertion predicate

- **D-01: The naming predicate is `value in text or repr(value) in text` — two forms, not four.**
  A four-form enumeration (raw / `repr()` / `'{value}'` / `"{value}"`) was considered and
  **rejected as redundant**: if `'C:\escape.typ'` is a substring of the message then the raw
  `C:\escape.typ` already is, so the two delimiter forms are strictly subsumed by the raw check.
  The only rendering the raw check does **not** subsume is `repr()`'s backslash-doubled form, which
  is why exactly one extra disjunct is needed. This is what makes the predicate hold across all
  three quoting regimes the milestone will pass through: `!r` today, MSG-02's delimiter-aware
  helper after Phase 60, and 57-11's hardcoded `'{value}'` in between.
  — **Reversibility:** reversible.

- **D-02: The predicate is applied to the extracted warning LINE, not to the whole captured output.**
  `tests/test_out02_escape_target_gate.py` asserts against `result.stdout + result.stderr` from a
  real `sphinx-build` subprocess. Asserting the raw form against the whole capture is unsound for
  SC#2: a raw path that leaks into the build output from *any* other source (a config echo, a
  traceback, a path Sphinx prints) would keep the test green after the path is removed from the
  warning, making the recorded falsification a false negative. The rewritten test therefore first
  selects the line(s) containing `ESCAPE_WARNING_SUBSTRING`
  (`"a path is not supported in a typst_documents target name"`, already a module constant at
  `tests/test_out02_escape_target_gate.py:36`), asserts exactly one such line exists, and applies
  the predicate to that line only. `tests/test_builder.py` already works on a single
  `caplog` record's `getMessage()` and needs no equivalent narrowing.
  — **Reversibility:** reversible.

- **D-03: The predicate takes the FULL path value, never its basename.**
  This is the trap SC#2 is aimed at. Measured: `builder.py:697` interpolates **two** path-valued fields,
  `{target!r}` *and* `{fallback!r}`, and for the `drive` shape they share a basename
  (`target = "C:\escape.typ"`, `fallback = "escape.typ"`). A "the basename appears in the message"
  predicate is therefore satisfied by `fallback` alone and stays GREEN with `target` fully
  removed — precisely the tautology SC#2 forbids. Verified for all three shapes that the
  full-value predicate goes RED under removal: `../escape.typ`, `/tmp/escape.typ` (POSIX) /
  `\\escape.typ` (nt), and `C:\escape.typ` are none of them substrings of the surviving
  `'escape.typ'` fallback text.
  — **Reversibility:** reversible.

### Where the shared predicate lives

- **D-04: A new leaf test-helper module `tests/_path_naming.py`.**
  Imported as `from _path_naming import path_named_in`. Measured this session by a live probe: `tests/` has
  **no `__init__.py`** and `pyproject.toml` sets `testpaths = ["tests"]` with the default
  `prepend` import mode, so pytest inserts `tests/` on `sys.path` and a bare
  `from _path_naming import ...` resolves — probe test collected and passed, then removed.
  Rejected: **`tests/conftest.py`** (it holds only fixtures today — `rootdir`, `sample_doctree`,
  `temp_sphinx_app`, `sphinx_config`, `mock_builder` — and `from conftest import ...` is a
  well-known pytest anti-pattern), and **inline duplication in both test modules** (two copies of
  a predicate that Phases 59 and 60 depend on is exactly the drift surface this phase exists to
  remove). The module carries **zero** `typsphinx` imports, mirroring MSG-02's leaf-module
  discipline on the product side.
  — **Reversibility:** reversible.

### Proving the rewrite is neither regression nor tautology (SC#2)

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
  — **Reversibility:** reversible.

- **D-06: The temporary product edit for (b) is made, measured and reverted inside ONE plan.**
  SC#4's `git diff --stat` runs at phase close as the proof it did not survive. The plan records
  `git status --porcelain typsphinx/` as empty immediately after the revert, in the same evidence
  file, before its commit. A dirty `typsphinx/` at commit time is a halt, not a deviation.
  — **Reversibility:** reversible.

- **D-07: Evidence file name is `58-DECOUPLING-EVIDENCE.md` — NOT `58-VERIFICATION.md`.**
  `{padded_phase}-VERIFICATION.md` is a name `gsd-verifier` reserves and overwrites wholesale; a
  plan that accumulates evidence under that name has it deleted at verify time. Follows the
  `57-MESSAGE-FIX-EVIDENCE.md` / `57-WINDOWS-FIX-EVIDENCE.md` precedent.
  — **Reversibility:** reversible.

### The census (SC#3)

- **D-08: The census is derived from a whole-tree sweep of `tests/`, classified on two axes.**
  It is never derived from the two known sites. Deriving the enumeration set from the two sites MSG-01
  names would inherit the very blind spot the census exists to close (this project has paid for
  that framing error before). Axes:
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
  — **Reversibility:** reversible.

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
  — **Reversibility:** reversible — one file, deletable if the planner judges it exceeds the
  test-side budget; but it is the only mechanism that carries SC#3's value into Phases 59 and 60.

### Branch push (SC#5)

- **D-10: `git push -u origin gsd/v0.9.1-windows-path-correctness` lands in this phase.**
  Verified by a post-push `git branch -vv` showing tracking. Measured this session: the branch is at
  `72896623` with **no upstream**, and `git ls-remote --heads origin` matches nothing containing
  `0.9.1`. Note the decoy-pair hazard this project sees every milestone — sibling branches
  `gsd/v0.7.0-milestone`, `gsd/v0.7.1-milestone`, `gsd/v0.9.0-milestone` all exist locally from the
  commit helper. The canonical branch is the config-slug one, `gsd/v0.9.1-windows-path-correctness`,
  and **no `gsd/v0.9.1-milestone` decoy exists locally at all** this round — nothing to disambiguate,
  but do not create one.
  — **Reversibility:** reversible.

### Claude's Discretion

The owner selected "おすすめで進める" for all four gray areas, so every D-NN above is Claude's
recommendation locked as a decision. The planner retains discretion on:
- Plan decomposition (D-05's two routes may be one plan or two; the census + guard may be one or two).
- The exact signature/naming of `path_named_in` and whether it returns `bool` or raises.
- Whether the `58-REPR-CENSUS.md` table is generated by the same script that backs D-09's guard.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone-binding documents
- `.planning/ROADMAP.md` § "🚧 v0.9.1 — Windows path correctness (ACTIVE)" — the 14 binding
  constraints. Constraints **2** (MSG-01 comes first, alone, test-side only), **4** (a plan that
  changes an emitted string and a plan that asserts on it must not share a wave), **9** (zero test
  edits in Phases 59/60), **10** (CI is not first discovery) and **11** (worktree isolation is
  standing) all bear directly on this phase.
- `.planning/ROADMAP.md` § "Phase 58" — the five success criteria this CONTEXT.md is scoped to.
- `.planning/REQUIREMENTS.md` **MSG-01** (lines 76-89) — the requirement text, including the
  owner-decision rationale for why it is its own requirement.
- `.planning/REQUIREMENTS.md` **MSG-02 / MSG-03** (lines 91-113) — read for *awareness only*:
  they define the quoting regimes D-01's predicate must survive. Do not implement them here.

### Research (written 2026-08-27, before MSG-01 existed)
- `.planning/research/SUMMARY.md` — **superseded on one point.** Its Key Finding #2 ("the zero test
  edits discipline cannot hold … these two test edits must land in the same wave as the source
  fixes") is exactly what MSG-01 and this phase overturn. ROADMAP constraint 2 says so explicitly
  and forbids re-litigating it during planning. Everything else in the file stands.
- `.planning/research/ARCHITECTURE.md` — leaf-module rationale (product side); D-04 mirrors its
  discipline on the test side.

### Test-side precedent this phase must match or preserve
- `tests/test_templates_path_collision_gate.py:411-470` — `TestWindowsPathEscapingRegressionGuard`,
  the proven POSIX-runnable Windows-shaped-string pattern (constraint 10 names it), and the
  format-asserting site D-08 classifies into the third bucket.
- `.planning/milestones/v0.9.0-phases/57-v0-9-0-release-prep-prep-only/57-MESSAGE-FIX-EVIDENCE.md`
  — the evidence-file shape D-07 follows, and the record of 57-11's revert-turns-RED technique
  that D-05(b) reuses.
- `.planning/milestones/v0.9.0-phases/57-v0-9-0-release-prep-prep-only/57-REVIEW.md` — IN-01, the
  single-quote-in-path sibling case; noted so Phase 60 inherits it, not addressed here.

### Project standing rules
- `CLAUDE.md` § "Worktree-isolated execution" — mandatory per-worktree
  `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` + `uv run` for every executor.
- `pyproject.toml` `[tool.pytest.ini_options]` — `testpaths`, `addopts = "-v --strict-markers"`,
  and the `filterwarnings` `error::DeprecationWarning` / `error::PendingDeprecationWarning` pair a
  new test module must not trip.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `tests/test_out02_escape_target_gate.py:36` `ESCAPE_WARNING_SUBSTRING` — already a module
  constant; D-02's line selection uses it rather than re-pasting the format string.
- `tests/test_out02_escape_target_gate.py:80-92` `_target_for_shape()` — already the single source
  of the target string, with the `os.name` branch (`absolute` → `"\\\\escape.typ"` on nt,
  `"/tmp/escape.typ"` on POSIX). The rewritten assertion feeds its return value to the predicate;
  it does not re-derive the shape.
- `tests/conftest.py` — `temp_sphinx_app` (used by `tests/test_builder.py`'s target test),
  `mock_builder`, `sample_doctree`. Fixtures only; no plain helper functions (D-04's rejection
  rationale).
- `ast` (stdlib) — D-09's guard needs nothing beyond it. **Zero new dependencies**, consistent with
  the milestone's standing invariant.

### Established Patterns
- **Call the real product function, never a re-pasted f-string.**
  `TestWindowsPathEscapingRegressionGuard`'s docstring states this explicitly ("A re-pasted format
  string would keep passing even if the product regressed back to `!r`"). Both tests in scope
  already satisfy it — one runs a real `sphinx-build`, the other calls
  `builder.post_process_images()` — and the rewrite must not weaken that.
- **Windows shapes are tested as hand-built string literals on every lane**, never gated on
  `os.name`. `test_escape_shape_refused_with_containment_proof`'s own docstring records this as
  D-05's platform-independence principle. `tests/test_builder.py:555-561` is the exception that
  proves it: it *does* branch on `os.name` to build `abs_root` — deliberate, because that test
  targets an absolute-path branch, and the rewrite leaves that branch alone.
- **`repr()` in a failure message is fine and stays.** 332 of the 341 occurrences are diagnostic
  f-strings (e.g. `f"unknown escape shape: {shape!r}"` at line 92 of the same file being edited).
  D-08's role axis exists so nobody mistakes those for census targets.

### Integration Points
- `typsphinx/builder.py:695-698` — the `!r`-formatted docname/target warning; the message
  `tests/test_out02_escape_target_gate.py` observes and D-05(b) temporarily falsifies. **Read-only
  in this phase.** MSG-03 rewires it in Phase 60.
- `typsphinx/builder.py:1766-1769` — the image-rehome warning
  (`f"could not rehome image URI {resolved_uri!r} … relocated to {key!r}"`); the message
  `tests/test_builder.py:598` observes. **Read-only in this phase.** Note it interpolates `key`,
  the value IMG-04/IMG-06 change in Phase 59 — ROADMAP constraint 4's collision site, and another
  reason nothing here may drift into product code.
- `tests/` root on `sys.path` (no `__init__.py`, pytest `prepend` mode) — the mechanism D-04
  depends on. Verified live this session.

</code_context>

<specifics>
## Specific Ideas

1. **The `fallback` trap is the concrete thing to design against.** `builder.py:697` names two
   path-valued fields and, for the `drive` shape, `fallback`'s value *is* `target`'s basename.
   Any predicate weaker than full-value matching is green under falsification. If a planner or
   executor proposes a basename/component-based assertion, that is the failure mode to point at.

2. **`repr()` doubles backslashes; it does not add them.** The `drive` target `"C:\escape.typ"`
   contains one backslash and `repr()` renders `'C:\\escape.typ'`. That is why the raw form is
   *absent* today under `!r` and *present* under both other regimes — and why exactly two disjuncts
   (raw, `repr`) cover all three regimes with no gap.

3. **The AST walk was prototyped this session and returned 9 sites**, all `repr()` calls, zero
   `!r` conversions in criterion position. The planner can treat that count as a measured baseline
   rather than re-deriving it, but the guard test must re-derive it at runtime (a hardcoded 9 would
   be the same snapshot problem D-09 exists to fix).

4. **Both tests must be recorded green on the pre-rewrite tree too**, not only post-rewrite —
   SC#2 names both runs. `tests/test_out02_escape_target_gate.py` is `skipif`-gated on
   `TYPST_AVAILABLE`; confirm typst-py is present in the worktree venv before claiming a green,
   or a skip will be misread as a pass.

</specifics>

<deferred>
## Deferred Ideas

- **`57-REVIEW.md` IN-01 — a path containing a literal single quote.** Belongs to MSG-02's gate in
  Phase 60, which names it explicitly. This phase's predicate happens to tolerate it (the raw
  disjunct matches regardless of delimiter), but no test for it is added here.
- **Routing `builder.py:697` / `:1767` off `!r`.** Phase 60, MSG-03. This phase deliberately leaves
  both message sites byte-identical — that is what makes "zero test edits in 59/60" a meaningful
  claim rather than a circular one.
- **Extending the AST guard to `typsphinx/` (product-side `!r` census).** MSG-03's own scope in
  Phase 60 already enumerates the product sites; duplicating it as a guard here would pre-empt that
  phase's decisions.

### Reviewed Todos (not folded)

`todo.match-phase 58` returned four matches. **None folded** — three carry an explicit
`resolves_phase` tag pointing elsewhere, and folding them would break the milestone's
phase-separation constraints:

- `2026-08-16-escapes-outdir-isabs-not-backslash-normalized.md` (score 0.90) — `resolves_phase: 59`
  (PATH-01). Product code; folding it would violate SC#4.
- `2026-08-16-track-image-escape-branch-basename-not-normalized.md` (score 0.90) —
  `resolves_phase: 59` (IMG-04). Same.
- `2026-08-17-repr-escaped-paths-in-remaining-user-facing-messages.md` — `resolves_phase: 60`
  (MSG-02..MSG-05). This is the todo Phase 58 *enables*, not the one it closes.
- `2026-08-04-release-create-job-missing-uv-verify-end-to-end.md` (score 0.60) —
  `resolves_phase: 46`, a release-pipeline concern with no bearing on a test-side phase.

</deferred>

---

*Phase: 58-repr-format-decoupling-test-side-only*
*Context gathered: 2026-08-27*
