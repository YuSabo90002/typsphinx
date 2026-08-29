# Roadmap: typsphinx

## Milestones

- ✅ **v0.4.4 — CI-repair + modernize** — Phases 1–5 (shipped 2026-07-05) → [archive](milestones/v0.4.4-ROADMAP.md)
- ✅ **v0.5.0 — forward-ecosystem** — Phases 6–10 + 8.1 (shipped 2026-07-11) → [archive](milestones/v0.5.0-ROADMAP.md)
- ✅ **v0.6.0 — real-world robustness** — Phases 11–15 (shipped 2026-07-13) → [archive](milestones/v0.6.0-ROADMAP.md)
- ✅ **v0.6.1 — rendering fidelity** — Phases 16–18 (shipped 2026-07-19) → [archive](milestones/v0.6.1-ROADMAP.md)
- ✅ **v0.6.2 — rendering fidelity round 2** — Phases 19–23 (+22.1–22.4) (shipped 2026-07-23) → [archive](milestones/v0.6.2-ROADMAP.md)
- ✅ **v0.6.3 — config & docs measured fidelity + captioned tables** — Phases 24–28 (+27.1) (shipped 2026-07-25) → [archive](milestones/v0.6.3-ROADMAP.md)
- ✅ **v0.6.4 — Read the Docs migration** — Phases 29–33 (+30.1) (shipped 2026-07-28) → [archive](milestones/v0.6.4-ROADMAP.md)
- ✅ **v0.6.5 — inline-math separator hotfix** — Phases 34–35 (shipped 2026-07-29) → [archive](milestones/v0.6.5-ROADMAP.md)
- ✅ **v0.7.0 — API rendering design overhaul** — Phases 36–42 (+40.1) (shipped 2026-08-04) → [archive](milestones/v0.7.0-ROADMAP.md)
- ✅ **v0.7.1 — bug-fix round** — Phases 43–46 (+44.1, 44.2, 45.1, 45.2) (shipped 2026-08-11) → [archive](milestones/v0.7.1-ROADMAP.md)
- ✅ **v0.8.0 — multi-master composition** — Phases 47–52 (shipped 2026-08-15) → [archive](milestones/v0.8.0-ROADMAP.md)
- ✅ **v0.9.0 — per-document templates** — Phases 53–57 (+54.1) (shipped 2026-08-22) → [archive](milestones/v0.9.0-ROADMAP.md)
- 🚧 **v0.9.1 — Windows path correctness** — Phases 58–61 (active, started 2026-08-27)

**Active milestone: v0.9.1 — Windows path correctness.** Four phases (58–61): decouple the two tests
that hard-code `repr()`'s output format so every later phase can change a message with zero test
edits; normalize the path-shape predicate and make a Windows-shaped absolute image URI survive the
whole pipeline into an `image("...")` Typst actually compiles; route every path-valued message
through one delimiter-aware quoting helper living in a new leaf module; then prep-only release.

Phase numbering is **continuous across milestones** — v0.9.0 ran Phases 53–57 (+54.1), so v0.9.1
starts at **Phase 58**.

## Phases

**Phase Numbering:**

- Integer phases (58, 59, …): Planned milestone work
- Decimal phases (58.1, 58.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order. Numbering is
**continuous across milestones** — each milestone continues from the prior one's last phase
(never resets to 1). v0.9.0 ran Phases 53–57, so v0.9.1 starts at **Phase 58**.

<details>
<summary>✅ v0.9.0 per-document templates (Phases 53–57, +54.1) — SHIPPED 2026-08-22</summary>

- [x] Phase 53: Template Registry Foundation (10/10 plans) — completed 2026-08-15
- [x] Phase 54: One Bundle Rule — `_template/<key>/`, Per-Document Selection, Four Deletions (7/7 plans) — completed 2026-08-16
- [x] Phase 54.1: Bundle Directory Safety — `templates_path` Collision Refusal and Pre-Write Path Validation (INSERTED) (5/5 plans) — completed 2026-08-16
- [x] Phase 55: v0.8.0-Derived Defects (4/4 plans) — completed 2026-08-16
- [x] Phase 56: Per-Document Template Documentation (5/5 plans) — completed 2026-08-16
- [x] Phase 57: v0.9.0 Release Prep (prep-only) (11/11 plans) — completed 2026-08-22

Full phase detail, success criteria, and decisions: [milestones/v0.9.0-ROADMAP.md](milestones/v0.9.0-ROADMAP.md)

</details>

<details>
<summary>✅ v0.4.4 – v0.8.0 (Phases 1–52) — SHIPPED 2026-07-05 → 2026-08-15</summary>

Each milestone's phase detail lives in its own archive, linked from the **Milestones** list above.

</details>

## 🚧 v0.9.1 — Windows path correctness (ACTIVE)

**Milestone Goal:** a path this extension writes, emits, or quotes back to the user is correct on
every supported platform, not only on the one the maintainer develops on. This is a bug-fix round —
no new user-facing capability, no new runtime dependency, no new `typst_*` config value. Its scope is
the Windows path defects Phase 57's prep-only fence held back, closed together with their whole
sibling family: the path-shape predicate that decides on the raw stem, the image URI that carries a
backslash into an `image()` Typst refuses to compile, the relocation key with no length bound, and
the twelve-odd user-facing messages that quote a path with `!r` or a hardcoded `'...'`.

**Everything this roadmap is built on was re-measured at HEAD** (2026-08-27) before being written.
Where a research finding contradicted the milestone's own initial framing, the finding won — see
PATH-01's reachability note and MSG-01's existence, both in `REQUIREMENTS.md`.

**Binding constraints this roadmap is built on** (settled decisions and measured facts, not open
questions):

1. **All three defect families are latent, so "CI green" is evidence of nothing.** No test covers any
   of them today; the `windows-latest` lane is green at HEAD and would stay green if nothing were
   fixed. The acceptance bar is only meaningful in its RED-first form: every gate must FAIL against
   the unfixed tree, recorded, before its fix lands.

2. **MSG-01 comes first, alone, and is test-side only.** Two existing tests hard-code `repr()`'s
   backslash-doubling as their pass criterion:
   `tests/test_out02_escape_target_gate.py:134` (`assert repr(target) in combined_output` for
   `target = "C:\\escape.typ"`, parametrized to run **unconditionally on every platform**) and
   `tests/test_builder.py:598` (`assert repr(abs_uri) in message`, green on POSIX by coincidence and
   breaking only on `windows-latest`). The first goes RED **on POSIX** the instant MSG-03 rewires
   `builder.py:697`. Decoupling them in their own phase, before any message string changes, is what
   makes the "zero test edits proves POSIX-identical output" discipline 57-11 established survive
   this milestone. This **supersedes** `research/SUMMARY.md`'s finding #4 ("the zero-test-edits
   discipline cannot hold; the two edits must land in the same wave as the source fixes") — that
   finding was written before MSG-01 existed and must not be re-litigated during planning.

3. **Three requirements share one ~30-line region of `builder.py`.** `_escapes_outdir()`
   (`builder.py:197-238`, PATH-01) is called from *inside* `_track_image()` at line 1727, thirteen
   lines above IMG-04's and IMG-06's key construction at ~1761-1772. They are one phase, and inside
   it one sequential plan — or strictly sequential sub-plans in one wave ordinal, never parallel
   worktrees against the same file.

4. **A plan that changes an emitted string and a plan that asserts on that string must not share a
   wave.** `builder.py:1767`'s image-rehome warning interpolates the exact `key` value IMG-04 and
   IMG-06 change *and* is one of the sites MSG-03 re-quotes. This is why Phase 59 (the value) and
   Phase 60 (the quoting) are separate phases rather than two waves of one — this project has
   already paid for that collision once.

5. **IMG-04 and IMG-05 are coupled by a measured Typst property.** Typst refuses a backslash in an
   `image()` path **BY VALUE, not by syntax** — escaping the backslash in the source so it decodes to
   one `\` still produces `TypstError: path must not contain a backslash`. Neither fix alone closes
   the compile failure, so IMG-07's real `typst.compile()` gate can only be green once **both** have
   landed, and belongs in the wave after them. This is also why the defect survived Phase 55's suite,
   whose tests stop at `node["uri"]` and never render.

6. **The quoting helper must be a NEW LEAF MODULE with zero `typsphinx`-internal imports.**
   `builder.py` imports `writer.py` at module scope, and `template_registry.py` avoids a cycle with
   `builder.py` only via a lazy function-scoped import. Putting the helper in any of those three
   files creates an unconditional two-file import cycle the moment the other two import it back.
   Placement is forced, not stylistic.

7. **IMG-06's bound is a hardcoded 255, not a probe** (owner decision 2026-08-27):
   `os.pathconf()`/`os.statvfs()` are documented `Availability: Unix` and unusable on the
   `windows-latest` lane. And IMG-06 has **no compile-visible symptom** — it surfaces as an
   `ENAMETOOLONG` `OSError` at `copy_image_files()` time — so it needs a gate of its own; the
   milestone's compile gate will not force it out.

8. **PATH-01's gate must call `_escapes_outdir()` directly.** Measured: the gap is not reachable from
   either production call site — `_resolve_target_stem()` normalizes at `builder.py:662` before
   calling, and `_track_image()` passes a `relpath()` result that always carries a `..` segment. An
   integration test routed through either call site is tautologically green before and after the fix
   and proves nothing. PATH-01 is scoped in as hardening of the function's own contract, deliberately.

9. **Zero test edits in the product-code phases (59 and 60).** MSG-01 exists to make this achievable.
   If a plan finds it must edit a test, that is a signal the census was incomplete, not a licence to
   edit.

10. **CI is not first discovery.** Phase 57 burned two matrix runs on this exact defect family. Each
    product-code phase confirms RED, then green, locally — on POSIX-runnable string-shape assertions,
    the proven `TestWindowsPathEscapingRegressionGuard` pattern — and only then dispatches the 3-OS
    lane. The acceptance bar is that lane, `windows-latest` included, green on the phase's own
    **post-fix tip**, dispatched fresh rather than inferred from a prior run.

11. **Worktree isolation is the standing execution mode** (owner decision, `CLAUDE.md`). Every
    executor provisions its own venv with
    `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` and runs everything via
    `uv run`. Do **not** degrade to sequential main-tree execution merely because a phase has low
    parallelism benefit.

12. **Push the milestone branch to `origin` from the FIRST phase** (milestone invariant #5, adopted
    v0.7.1, paid four times over in v0.8.0). Measured 2026-08-27: the branch actually carrying this
    milestone's commits is **`gsd/v0.9.1-windows-path-correctness`** — see the CORRECTED note in Roadmap
    Evolution below. No upstream
    configured, and nothing matching `0.9.1` on `origin`. Unlike v0.9.0's identically-shaped decoy
    (`gsd/v0.9.0-milestone`, which sat at the merge-base with zero milestone commits), this one *is*
    the milestone branch. Phase 58 carries it as SC#5; every later phase inherits it.

13. **The final phase (61) is prep-only and takes zero irreversible action.** Version bump, curated
    CHANGELOG entry, evidence gathering, handoff checklist. No tag, no publish, no GitHub Release, no
    PR. **REL-09 closes at `/gsd-complete-milestone`, not in the phase** — and the `phase.complete`
    auto-flip has fired against the release-prep requirement at **five consecutive** closes, so Phase
    61 records a `REQUIREMENTS.md` checksum at phase head to catch and revert it.

14. **Standing invariants carried forward:** zero new runtime dependencies (every fix is stdlib-only
    by construction, verified against the research — no candidate solution required one); no new
    `typst_*` config value (the configuration surface is unchanged this round); the `@preview` package
    count stays at **four** with no new version-lockstep site (`writer.py` / `template_engine.py` /
    `templates/base.typ`); typing-import modernization is forbidden (`CLAUDE.md` independently
    instructs it); every phase closes green on the full pytest suite plus `black` / `ruff` / `mypy`;
    and "anywhere under X" success criteria are checked by a repo-wide grep at discovery time, never
    against the files a requirement happens to name (milestone invariant #4).

**`research/SUMMARY.md`'s suggested A–F structure is adopted in sequence, not in count.** Its six
"phases" are plan-sized units, and it was written before two owner decisions landed: MSG-01's
existence (constraint 2) and the Phase-59-before-Phase-60 ordering that constraint 4 forces. Its
Wave-1/Wave-2 decomposition survives intact *inside* Phases 59 and 60 and should be read as planning
input there.

**Not a frontend UI milestone** (standing project note): every phase below is builder, writer,
translator and release work. `ui.plan-gate` false-positives on words this milestone cannot avoid —
"image", "render", "template", "page". Each phase detail therefore carries an explicit
`**UI hint**: no` line, the authoritative override `ui-safety-gate.cjs` reads, rather than relying on
a per-run `--skip-ui`.

- [x] **Phase 58: `repr()`-Format Decoupling (test-side only)** - The two tests that hard-code `repr()`'s backslash-doubling as their pass criterion assert the *meaning* instead, so every later phase in this milestone can change a message string with genuinely zero test edits (completed 2026-08-28)
- [x] **Phase 59: Path-Shape Predicate and Image-URI Correctness** - A Windows-shaped absolute image URI survives the whole pipeline: classified correctly by a predicate that normalizes before it decides, relocated under a key carrying no separator and bounded to a portable filesystem limit, and emitted into an `image("...")` a real `typst.compile()` accepts (completed 2026-08-29)
- [x] **Phase 60: One Delimiter-Aware Path-Quoting Helper, Routed Everywhere** - Every path-valued interpolation in `builder.py`, `writer.py` and `template_registry.py` quotes through one helper in a new leaf module that never doubles a backslash and never closes its quote early, while identifier-valued `!r` stays untouched (completed 2026-08-29)
- [ ] **Phase 61: v0.9.1 Release Prep (prep-only)** - The v0.9.1 tree is bumped, its CHANGELOG curated around the three defect families, proven green on a fresh 3-OS run, and handed off with no irreversible action taken

## Phase Details

### Phase 58: `repr()`-Format Decoupling (test-side only)

**Goal**: The two existing tests that hard-code `repr()`'s output format as their pass criterion
assert the *meaning* — that the offending path is named in the message — instead. After this phase,
a message site can move off `!r` without a single test edit, which is the whole mechanism by which
Phases 59 and 60 prove POSIX output stayed identical.

This phase ships **no product change**. It is first because
`tests/test_out02_escape_target_gate.py:134` runs unconditionally on every platform and goes RED
**on POSIX** the instant MSG-03 rewires `builder.py:697` — before any Windows lane is even consulted.
Its sibling `tests/test_builder.py:598` is green on POSIX by coincidence (`repr()` of a
backslash-free path is the `!r` form the message already contains) and breaks only on
`windows-latest`, which is exactly the shape that cost Phase 57 two matrix runs.

**Depends on**: Nothing (first phase of the milestone)
**Requirements**: MSG-01
**Success Criteria** (what must be TRUE):

  1. **Neither test asserts on `repr()`'s output format for a path value any more.** The drive-shape
     escape gate and the image-rehome warning test each assert that the offending path is *named* in
     the message, by a property that holds whether the message quotes with `repr()`, with a
     hardcoded `'...'`, or with a delimiter-aware helper.

  2. **The rewrite is proven neither a regression nor a tautology.** Both tests are recorded green on
     the pre-rewrite tree and on the post-rewrite tree (real runs, not asserted), *and* a recorded
     falsification — the path removed from the message — turns each one RED. A rewritten assertion
     that would pass against a message naming no path at all does not satisfy this.

  3. **The `repr(...)` / `!r` census in `tests/` is recorded and classified.** Every remaining
     occurrence is labelled path-valued or identifier/list/bytes/int-valued, the path-valued count is
     zero, and the list is written down — so Phases 59 and 60 can check their zero-test-edit claim
     against an enumeration rather than against a belief.

  4. **No file under `typsphinx/` changes in this phase**, proven by `git diff --stat` over the
     phase's own range. This is a test-side decoupling; a product change here would confound the
     next two phases' evidence.

  5. **The milestone branch is on `origin`.** `gsd/v0.9.1-windows-path-correctness` (see the
     CORRECTED 2026-08-27 note in Roadmap Evolution — the roadmapper named
     `gsd/v0.9.1-milestone`, which the commit helper then superseded) — measured at roadmap time as
     three commits ahead of `main` with no upstream and nothing matching `0.9.1` on the remote — is
     pushed and tracking, from this first phase rather than at the release PR (milestone invariant
     #5).

**Plans**: 3/3 plans executed in 3 waves

Plans:
**Wave 1**

- [x] 58-01-PLAN.md — Tracer: the `tests/_path_naming.py` predicate, the escape-target gate rewritten onto it with D-02 line narrowing, SC#2's pre-rewrite baseline for both target tests, the recorded RED under a reverted `builder.py:697` falsification, and D-05(a)'s durable meta-tests

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 58-02-PLAN.md — The second call site: `tests/test_builder.py`'s image-rehome assertion rewritten onto the predicate, plus the recorded RED under a reverted `builder.py:1767` falsification; brings the pass-criterion count to 7 with zero path-valued sites

**Wave 3** *(blocked on Wave 2 completion)*

- [x] 58-03-PLAN.md — The AST-backed census guard, the two-axis classified `58-REPR-CENSUS.md`, the phase gate, SC#4 proven at phase scope, and the milestone branch pushed to `origin` and tracking

**UI hint**: no

### Phase 59: Path-Shape Predicate and Image-URI Correctness

**Goal**: A Windows-shaped absolute image URI survives the whole pipeline. `_escapes_outdir()`
decides on the normalized string like its sibling `_is_absolute_image_uri()` already does; the
relocation key `_track_image()` builds carries no backslash and cannot exceed a portable filesystem
component limit; and the URI `visit_image()` interpolates is escaped last, after every path-shape
transform, so what reaches Typst is a string it accepts.

The three `builder.py` changes are **one sequential plan** by constraint 3 — `_escapes_outdir()` is
called from inside the very method whose key construction IMG-04 and IMG-06 rewrite. `translator.py`
is a disjoint file and parallel-safe alongside it. IMG-07's real `typst.compile()` gate is coupled to
**both** halves by a measured Typst property (constraint 5), so it belongs in the wave after them,
not beside them.

**Depends on**: Phase 58
**Requirements**: PATH-01, IMG-04, IMG-05, IMG-06, IMG-07
**Success Criteria** (what must be TRUE):

  1. **`_escapes_outdir()` is a correct standalone predicate.** Called **directly** — never through
     either production call site — it returns `True` for a driveless-absolute stem (`\manuals\guide`)
     and a UNC stem (`\\srv\share\g`), with the pre-fix `False` recorded as RED first. Both existing
     call sites are separately measured to classify every tested shape byte-identically before and
     after, so the hardening is proven to have changed no live behaviour.

  2. **A real `typst.compile()` accepts a document whose image URI was a Windows-shaped absolute
     path.** The gate is recorded RED against the unfixed tree with Typst's own
     `path must not contain a backslash` refusal in the evidence, and green after — proving both
     coupled halves (relocation-key normalization and literal escaping at the emission point) are
     present, and that neither alone would have closed it.

     **AMENDED 2026-08-29 (owner-approved, after measurement).** The error string named above was
     inherited from `59-CONTEXT.md` D-01's prediction, which measurement falsified for the *unfixed*
     row only. Measured, the unfixed tree is refused with `unclosed delimiter`;
     `path must not contain a backslash` is real but fires on the **escaping-only** row. Cause: the
     unfixed pipeline emits a literal carrying BOTH a raw backslash and a raw unescaped `"`, and the
     `"` terminates the Typst string at parse time, so the semantic backslash check never runs —
     D-01's four probe runs each carried only ONE defect, so none of them exercised that literal. The
     substantive claim of this criterion is unchanged and **is met**: all three of unfixed,
     key-normalization-only and escaping-only fail to compile, and only the tree carrying both halves
     compiles, so neither alone would have closed it. Evidence:
     `59-WINDOWS-URI-EVIDENCE.md` § "IMG-07 four-combination table"; decision record:
     `59-CONTEXT.md` § D-01a; both readings judged separately in `59-VERIFICATION.md`.

  3. **The relocation key is separator-free and length-bounded, with the collision anchor intact.**
     No backslash from the original URI survives into the key for any Windows-shaped input; the
     basename is bounded to 255 UTF-8 bytes with the `{sha1[:8]}-` digest kept whole, truncation
     landing on a UTF-8 character boundary, the extension preserved, and never an empty basename. The
     collision property IMG-03 closed is re-proven for two long URIs sharing a basename.

  4. **The length bound has its own gate, not a compile gate.** It fails against the unfixed tree
     with the `ENAMETOOLONG` `OSError` raised at `copy_image_files()` time and passes after — because
     this defect has no compile-visible symptom and criterion 2's gate cannot see it.

  5. **Zero test edits, and the matrix is green on this phase's own tip.** No existing test
     assertion anywhere under `tests/` is modified over this phase's diff (measured against Phase
     58's census, not claimed), and the 3-OS CI lane — `windows-latest` included — is green on the
     post-fix tip, dispatched fresh after a local RED-then-green run rather than inferred from a
     prior run.

**Plans**: 5/5 plans executed (strictly sequential — 5 waves; see the plan-ordering note below)

Plans:

**Wave 1**

- [x] 59-01-PLAN.md — PATH-01: `_escapes_outdir()` normalize-then-decide, its direct-call RED gate, the two-call-site characterization pin, and the phase evidence spine

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 59-02-PLAN.md — IMG-04 + IMG-06: normalized, 255-byte-bounded relocation key via two new builder helpers, with a pure-string gate and an ENAMETOOLONG integration gate

**Wave 3** *(blocked on Wave 2 completion)*

- [x] 59-03-PLAN.md — IMG-05: `visit_image()` routes the adjusted URI through `escape_typst_string()` once, gated by a relative-URI escaping gate independent of the builder half

**Wave 4** *(blocked on Wave 3 completion)*

- [x] 59-04-PLAN.md — IMG-07: the two-mode Windows-shaped fixture project, the all-lane `-b typst` string-shape gate, and the real `typst.compile()` gate with a runtime probe-skip

**Wave 5** *(blocked on Wave 4 completion)*

- [x] 59-05-PLAN.md — Acceptance: D-01's four-combination two-tree table (SC#2), the measured zero-test-edit proof (SC#5), and the fresh 3-OS CI dispatch

**Plan ordering note.** Constraint 3 forbids parallel worktrees against `builder.py`, and constraint
4 forbids a plan that changes an emitted string from sharing a wave with a plan that asserts on it.
Independently, every plan appends its RED/GREEN transcript to the single D-11-named
`59-WINDOWS-URI-EVIDENCE.md`, so any two plans in one wave would collide there at merge even with
disjoint code files. The five plans therefore run one per wave; `translator.py`'s parallel-safety
(noted above) is a permission this decomposition declines to use.

**UI hint**: no

### Phase 60: One Delimiter-Aware Path-Quoting Helper, Routed Everywhere

**Goal**: Every user-facing message that names a path quotes it unambiguously and without
backslash-doubling, through one helper that lives where nothing can import-cycle on it. This restores
the half of `repr()` that 57-11's hardcoded `'{value}'` dropped — automatic delimiter selection —
while keeping the half it correctly removed.

The helper is created first (a new leaf module, new tests, no existing file touched), then wired into
three disjoint modules. It runs **after** Phase 59 by constraint 4: `builder.py:1767` interpolates
the very `key` value Phase 59 changes, so quoting it — and asserting on the quoted result — must
follow the value settling, never accompany it.

**Depends on**: Phase 59
**Requirements**: MSG-02, MSG-03, MSG-04, MSG-05
**Success Criteria** (what must be TRUE):

  1. **The helper exists in a new leaf module and behaves on both halves.** Its import block names no
     `typsphinx` module (read from the source, and proven by importing it standalone); it accepts
     `str` **and** `os.PathLike`, because `template` values are deliberately allowed to be
     `pathlib.Path`; it never doubles a backslash; and it selects a delimiter that cannot appear
     unescaped in the value, so a path containing a literal single quote comes back unambiguously
     delimited — the sibling case `57-REVIEW.md` IN-01 named as missing.

  2. **Every path-valued interpolation in the census routes through it.** `builder.py`'s three
     message builders (~329-402) plus lines 697, 942, 964, 965, 999, 1007, 1008, 1015, 1767, 2056 and
     2066; `writer.py`'s wrapper-render debug log (511-513); and `template_registry.py`'s CONF-17
     violation (422) and existence check (433). A repo-wide grep run at execution time — not the
     line list above — is the discovery authority, and it shows no path-valued `!r` left in those
     three modules.

  3. **The rollout is proven not to have over-reached.** Identifier-valued interpolations — registry
     keys, docnames, config tuples — still render with `!r`, and `template_registry.py:410` is
     measurably still `!r`, because it is reached precisely when the value is a `list`, `bytes` or
     another non-path type and quoting it as a path would be actively wrong.

  4. **Both gate halves are green, each RED-recorded first.** The existing no-doubled-separator
     property (`TestWindowsPathEscapingRegressionGuard`) is extended to the newly-routed sites, and
     the single-quote-in-path case is asserted — with `writer.py`'s and `template_registry.py`'s
     coverage living in their own test modules rather than all three files' plans extending one
     shared class in one wave.

  5. **Zero test edits, and the matrix is green on this phase's own tip.** No existing test assertion
     is modified — Phase 58 removed the only two that would have forced it — and the 3-OS CI lane,
     `windows-latest` included, is green on the post-fix tip, dispatched fresh.

**Plans**: 5/5 plans executed in 3 waves (D-09: helper → three parallel wiring plans → acceptance)

Plans:

**Wave 1**

- [x] 60-01-PLAN.md — MSG-02: the `typsphinx/pathfmt.py` leaf module and `quote_path()`, its own
  RED-first gate module, the two-form leaf-import proof, and the phase evidence spine

**Wave 2** *(blocked on Wave 1; the three plans run IN PARALLEL — disjoint modules, disjoint test
modules, per-plan evidence files)*

- [x] 60-02-PLAN.md — MSG-03: all 23 path-valued interpolations in `typsphinx/builder.py` routed,
  five message families RED-recorded first, plus the three added single-quote methods on
  `TestWindowsPathEscapingRegressionGuard` (a one-plan privilege, D-11)
- [x] 60-03-PLAN.md — MSG-04: `typsphinx/writer.py`'s wrapper-render debug log routed, gated via
  `caplog` at DEBUG, with a two-tree byte-identity pin for the package-alone `None` path
- [x] 60-04-PLAN.md — MSG-05: `typsphinx/template_registry.py`'s CONF-17 and existence messages
  routed, both of D-12's RED shapes recorded, and the type-check message measurably left excluded

**Wave 3** *(blocked on Wave 2 completion — the audit runs one wave later than what it audits)*

- [x] 60-05-PLAN.md — acceptance: SC#2's repo-wide discovery grep, SC#3's over-reach measurement,
  SC#5's zero-test-edit proof against `58-REPR-CENSUS.md`, the read-only consolidation into
  `60-PATH-QUOTING-EVIDENCE.md`, and a fresh 3-OS CI dispatch on the post-fix tip

**UI hint**: no

### Phase 61: v0.9.1 Release Prep (prep-only)

**Goal**: The v0.9.1 tree is bumped, its CHANGELOG curated, its claims re-proven on live runs against
the bumped tree, and handed off — with **zero irreversible action**. No tag, local or remote; no
publish; no GitHub Release; no PR. This is the standing pattern held for seven consecutive milestones
(Phases 10, 41, 46, 52, 57) under `branching_strategy: milestone`. **REL-09 closes at
`/gsd-complete-milestone`, not in this phase** — it is held at `[ ]` through every plan.

v0.9.1 is a **patch release with no breaking change**: no new capability, no new runtime dependency,
no new `typst_*` config value. The CHANGELOG entry describes three defect families as user-visible
fixes — a Windows-shaped `typst_documents` target now refused by a predicate that normalizes first, a
Windows-shaped absolute image URI that now compiles, and path-naming diagnostics that no longer
double separators or close their quote early.

**Depends on**: Phase 60
**Requirements**: REL-09
**Success Criteria** (what must be TRUE):

  1. **The version moves atomically to 0.9.1.** `pyproject.toml` (the sole literal), `uv.lock` and
     `README.md`'s Status line move in lockstep, the editable-install metadata is regenerated so
     `typsphinx.__version__` reports `0.9.1`, and every version-sync guard test stays green.

  2. **The CHANGELOG entry is curated, not generated.** A `## [0.9.1]` section names the three defect
     families, states plainly that nothing breaks and no configuration changed, and the tail
     link-reference block is rolled over in this same phase (the `[Unreleased]` compare link advanced
     and a `0.9.1` release/tag link added) — release-prep work, not a version-bump side effect. The
     GitHub Release body's source, `scripts/extract_changelog_section.py 0.9.1`, reproduces that
     section byte-for-byte.

  3. **The bumped tree is proven green on live runs, not on the preceding phases' word.** Full pytest
     suite, `black` / `ruff` / `mypy`, both docs tox environments against their measured warning
     baselines, and a fresh 3-OS CI run dispatched on the **bumped** tip with both `windows-latest`
     lanes green — the milestone's acceptance bar, observed here rather than inherited.

  4. **The fence is proven held.** No local or remote `v0.9.1` tag exists and no release or publish
     has occurred — probed and recorded twice at separated times, as at every previous close.
     `git diff` over the phase shows **no unintended change under `typsphinx/`**, and a checksum of
     `REQUIREMENTS.md` recorded at phase head catches the known `phase.complete` auto-flip of the
     release requirement — which has fired at **five consecutive** release-prep closes — so it is
     reverted rather than shipped.

  5. **The handoff checklist is standalone and complete.** A `61-HANDOFF.md` enumerates every step
     `/gsd-complete-milestone` must execute, including the standing second-repository tag
     (`typsphinx-doc-translations`, advanced by dispatching that repository's own `update-pin.yml`
     rather than by a hand-made clone-edit-push), the Read the Docs `stable` measurement for both
     projects, and the GitHub Release body being byte-identical to
     `scripts/extract_changelog_section.py 0.9.1`'s stdout.

**Plans**: TBD
**UI hint**: no

## Progress

**Execution Order:**
Active milestone phases execute in numeric order (decimal insertions between their surrounding
integers), with the prep-only Release phase last so its CHANGELOG entry describes work already proven
by the preceding phases' gates. v0.9.1 executes **58 → 59 → 60 → 61**, and every one of those three
arrows is a measured constraint rather than a convention:

- **58 before 59 and 60** because `tests/test_out02_escape_target_gate.py:134` runs on every platform
  and goes RED on POSIX the moment a message site moves off `!r`. Decoupling it first is what makes
  the later phases' zero-test-edit claim mean something.
- **59 before 60** because `builder.py:1767` interpolates the exact `key` value Phase 59 changes and
  Phase 60 re-quotes. Landing the value first means Phase 60's assertions are written against a
  settled string; landing them together is the same-wave string/assertion collision this project has
  already paid for once.
- **60 before 61** only in the ordinary sense that release prep describes finished work.

Phases 1–57 shipped across v0.4.4 → v0.9.0; their per-phase plan counts, statuses and completion
dates are preserved in each milestone's archived roadmap under `milestones/`. The table below tracks
the active milestone only.

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 58. `repr()`-Format Decoupling (test-side only) | v0.9.1 | 3/3 | Complete | 2026-08-28 |
| 59. Path-Shape Predicate and Image-URI Correctness | v0.9.1 | 5/5 | Complete | 2026-08-29 |
| 60. One Delimiter-Aware Path-Quoting Helper, Routed Everywhere | v0.9.1 | 5/5 | Complete | 2026-08-29 |
| 61. v0.9.1 Release Prep (prep-only) | v0.9.1 | 0/TBD | Not started | - |

## Roadmap Evolution

- **2026-08-27** — v0.9.1 roadmap created: **Phases 58–61**, 11/11 v1 requirements mapped, zero
  orphans, continuing numbering from v0.9.0's Phase 57. Four phases at `granularity: standard`.
  Three decisions are baked into the structure and should not be re-derived during planning:

  - **MSG-01 is its own phase and comes first** (Phase 58), superseding `research/SUMMARY.md`'s
    finding #4 that the two `repr()`-dependent test edits "must land in the same wave as the source
    fixes". That finding predates MSG-01's owner decision (2026-08-27). Landing the edits in their
    own test-only phase preserves the zero-test-edits discipline for the phases that change product
    code, which is the only reason the discipline is evidence of anything.

  - **PATH-01, IMG-04 and IMG-06 are one phase, not three** (Phase 59), because `_escapes_outdir()`
    is called from inside `_track_image()` and all three land in the same ~30-line region of
    `builder.py`. `research/SUMMARY.md`'s A–F suggestion splits them across two of its units; the
    split survives as *plan* structure inside Phase 59, not as phase structure.

  - **IMG-07 is mapped to Phase 59**, the phase that actually writes the real `typst.compile()`
    gate, rather than being carried as a cross-cutting milestone-level obligation. Typst's
    value-level backslash refusal couples IMG-04 and IMG-05, so the gate is only green once both
    have landed — which is possible in exactly one phase.

- **2026-08-27** — Milestone invariant #5 (push the branch from the first phase) encoded as Phase
  58's SC#5. The milestone branch was **measured, not assumed**: `gsd/v0.9.1-windows-path-correctness`

    **CORRECTED 2026-08-27, after the roadmap commit.** The roadmapper measured
    `gsd/v0.9.1-milestone` as the live milestone branch, and that was true when it measured. The
    very next `commit` call then derived the canonical name from `config.json`'s
    `git.milestone_branch_template` (`gsd/{milestone}-{slug}`), created
    `gsd/v0.9.1-windows-path-correctness`, and switched to it -- so the roadmap commit `e257e70d`
    landed there while the three earlier commits' branch pointer stayed behind at `441266a4`.
    Measured immediately after: the two were strictly linear (merge-base `441266a4`, 1 commit ahead,
    0 behind), so nothing diverged and nothing was lost. `gsd/v0.9.1-milestone` was deleted as a
    zero-unique-commit ancestor, precisely so it could not become the mid-milestone decoy v0.9.0
    had to correct. **The canonical branch is `gsd/v0.9.1-windows-path-correctness`** -- the name
    the tooling will keep re-deriving on every commit, so it is the one Phase 58's SC#5 pushes.
    Restore the deleted pointer with `git branch gsd/v0.9.1-milestone 441266a4` if ever needed.

  At roadmap time `gsd/v0.9.1-milestone` was three
  commits ahead of `main`, has no upstream configured, and nothing matching `0.9.1` exists on
  `origin`. v0.9.0's roadmap had to correct an identically-named decoy mid-milestone; this one is the
  real branch, checked before it was written down.

- **2026-08-27** — The 3-OS matrix run was deliberately **not** given a REQ-ID (`REQUIREMENTS.md`
  Out of Scope). It remains the milestone's acceptance bar and is carried in the success criteria of
  each phase that changes product code (59, 60) and re-run on the bumped tree in 61.

## Backlog

Candidate work not yet scoped into a milestone. Promote items with `/gsd-review-backlog`, or
pull a whole cluster into the next milestone via `/gsd-new-milestone`.
Numbered 999.x so milestone reorganization never renumbers or drops them.

New items land here as `999.x` entries. **No item is open** — the backlog has been empty since
2026-08-04. Item **999.1** (inline math after text: missing separator before `#mi()` causes a Typst
error) was promoted into v0.6.5 as Phase 34 / requirement MATH-01 and shipped 2026-07-29. Item
**999.2** (a captioned table drops the id of an immediately preceding standalone target) was promoted
into v0.7.0 as **Phase 42 / requirement TBL-03** and shipped in v0.7.0. Numbering does not reuse
retired numbers, so the next item filed here is **999.3**.

**Todos and seeds promoted into v0.8.0** (2026-08-11) — the three-defect `typst_documents`-modelling
cluster the v0.7.1 close named first among next-milestone candidates, plus the two image defects that
shipped in v0.7.1 unfixed by owner decision D-27:

- `shared-document-silently-dropped-from-all-but-first-master` → Phase 49 (defect A: COMP-07, and the
  whole COMP-05..COMP-12 include-graph set that closes it)

- `a-master-that-is-also-a-toctree-child-is-unrepresentable` → Phase 47 (B-1: COMP-03)
- `duplicate-typst-documents-target-silently-drops-a-master` → Phase 47 (BLD-02) — re-measured live in
  Phase 46 and still reachable, because Phase 44's guard compares only against `env.found_docs` and
  the reserved `_template`, never against already-resolved targets

- `rehomed-converted-image-collides-with-srcdir-images-dir` → Phase 50 (IMG-01, major — a regression
  in failure mode: the same project used to abort loudly)

- `track-image-rehome-escapes-outdir-for-non-doctreedir-abs-uri` → Phase 50 (IMG-02, minor)

Each todo record stays **pending** until its phase executes; the todo is the detail record, the phase
entry above is the sequencing record.

**Still open and deferred, not in v0.8.0 scope:**

- `modernize-typing-imports-drop-up006-up035-ignore` — deferred *doubly deliberately*, since
  `CLAUDE.md` independently instructs "don't modernize typing imports until that todo lands", and
  binding constraint #9 forbids it this milestone.

- `add-sphinx-linkcheck-ci-job` — tracked as Future requirement LNK-01; `links.yml`'s repo-wide
  lychee check already covers the links each release adds.

- `ruff-generic-linux-elf-unrunnable-on-nixos` — a `flake.nix`-side toolchain repair in the same
  family as QUA-04 (Future requirement QUA-06); CI holds lint authority, so it blocks nothing.

- Dormant seeds: `SEED-001-readme-quickstart-typst-documents-pdf` (substantially discharged by v0.7.1's
  CONF-08 + DOC-11) and `SEED-003-tox-dependency-groups-per-env` (Future requirement QUA-07).

**Todos and seeds promoted into v0.9.0** (2026-08-15) — the five v0.8.0-derived defects that shipped
unfixed by decision D-01 or with only a test-side fix, all closed on the product side by Phase 55:

- `label-collision-false-negative-in-compile-time-xref-guard` → Phase 55 (XREF-05)
- `include-edge-key-separators-unescaped-two-edges-can-collide` → Phase 55 (BLD-07)
- `unbounded-recursion-in-derive-master-edge-keys` → Phase 55 (BLD-08)
- `escape-branch-relocation-key-uses-basename-only-two-escaping-images-can-collide` → Phase 55 (IMG-03)
- `track-image-isabs-not-drive-aware-on-py313-windows` → Phase 55 (BLD-09)

**Todos promoted into v0.9.1** (2026-08-27) — the three path-handling records Phase 57's prep-only
fence held back, each now carrying a REQ-ID and a phase:

- `2026-08-16-escapes-outdir-isabs-not-backslash-normalized` → Phase 59 (**PATH-01**). Re-measured at
  roadmap time: **not reachable from either production call site**, because both pre-normalize. Kept
  in scope deliberately as hardening of the function's own contract — a future third call site would
  inherit the gap silently — with the standing instruction that its gate call `_escapes_outdir()`
  directly, since an integration test through either call site is tautologically green.

- `2026-08-16-track-image-escape-branch-basename-not-normalized` → Phase 59 (**IMG-04**), together
  with its two never-filed siblings scoped in alongside it: the unescaped `image("...")` emission
  (**IMG-05**) and the unbounded key length (**IMG-06**). IMG-04 and IMG-05 are coupled by Typst's
  value-level backslash refusal, so the real-compile gate (**IMG-07**) closes both at once.

- `2026-08-17-repr-escaped-paths-in-remaining-user-facing-messages` → Phase 60 (**MSG-02** through
  **MSG-05**), with its test-side prerequisite split out as **MSG-01** in Phase 58. This record
  carries **both** halves of the defect — the `!r` backslash-doubling at the sites 57-11 left alone,
  and 57-REVIEW WR-01's fixed-`'...'` delimiter that closes early on a path containing a single
  quote — and one delimiter-aware helper closes both.

Each todo record stays **pending** until its phase executes; the todo is the detail record, the phase
entry above is the sequencing record.

**Still open and deferred after the v0.9.0 close** (2026-08-22), and **not** in v0.9.1 scope — full
dispositions in
`.planning/milestones/v0.9.0-phases/57-v0-9-0-release-prep-prep-only/57-HANDOFF.md`
§ "Deferrals carried forward", and one row each in STATE.md's Deferred Items ledger:

- `2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos` — **kept open with a live 2026-08-22
  recurrence annotated**, which falsified v0.9.0's own 2026-08-16 "ruff works here" measurement. The
  main tree's stale binary masks it; only a freshly-provisioned venv reproduces it. Tracked as Future
  requirement QUA-06. CI holds lint authority, so it blocks nothing — including this milestone's
  worktree-isolated executors.
- `2026-08-16-dependabot-prs-die-on-uv-lock-locked-mismatch` — `severity: major`; its `--locked`
  census is what made v0.9.0's D-13 sequencing constraint concrete. Tracked as a Future CI requirement.
- `2026-08-16-root-toctree-duplicates-section-children-in-html-sidebar` — an HTML sidebar defect in
  this project's own docs.
- `2026-08-14-numref-number-diverges-per-master-and-vanishes-for-non-root-only-figures` — still
  excluded from every published surface by owner override D-07.
- `2026-08-04-release-create-job-missing-uv-verify-end-to-end` — REL-04's own record, whose acceptance
  criteria were met at the v0.7.1 publish and again at v0.8.0 and v0.9.0. Raised for the third close
  with the settling measurement attached; the disposition is the owner's.
- `2026-07-22-add-sphinx-linkcheck-ci-job` (Future LNK-01) and
  `2026-07-22-modernize-typing-imports-drop-up006-up035-ignore` (forbidden by `CLAUDE.md` until the
  todo itself lands) — both deferred again.
- Dormant seeds: `SEED-001-readme-quickstart-typst-documents-pdf`,
  `SEED-003-tox-dependency-groups-per-env` (Future QUA-07), and **`SEED-004-typst-py-maintenance-risk-vendored-compile-path`**
  — `typst-py` upstream maintenance is slowing and typsphinx may eventually need to carry an
  equivalent compile path. The largest structural risk on the horizon; never scoped into a milestone,
  and explicitly not scoped into this bug-fix round either.

**Known limitations shipped in v0.9.0**, deferred by owner decision with no published surface:
WR-02 (`templates_path` resolved against `srcdir`, not `confdir`, so `-c`/confdir projects keep the
republication hole — shipped *silent*, making the CHANGELOG's validation sentence read
unconditional) and the tripled "Custom template not found" warning; both are carried forward as v2
requirements and are **not** in v0.9.1 scope. The third — the fixed-`'...'`-delimiter path quoting —
**is** closed this milestone, by MSG-02's delimiter-aware helper.

---
*Roadmap created: 2026-07-04 · Reorganized at each milestone close: v0.4.4 (2026-07-05), v0.5.0 (2026-07-11), v0.6.0 (2026-07-13), v0.6.1 (2026-07-19), v0.6.2 (2026-07-23), v0.6.3 (2026-07-25), v0.6.4 (2026-07-28), v0.6.5 (2026-07-29), v0.7.0 (2026-08-04), v0.7.1 (2026-08-11), v0.8.0 (2026-08-15), v0.9.0 (2026-08-22) · Active milestone section added: v0.9.1 (2026-08-27). Per-milestone phase detail, success criteria, and decisions for shipped milestones live in `milestones/vX.Y-ROADMAP.md`.*
