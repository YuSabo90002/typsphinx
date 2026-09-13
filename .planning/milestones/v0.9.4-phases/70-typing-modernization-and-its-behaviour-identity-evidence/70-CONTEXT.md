# Phase 70: Typing Modernization and Its Behaviour-Identity Evidence - Context

**Gathered:** 2026-09-13
**Status:** Ready for planning

<domain>
## Phase Boundary

Move every `typing.Dict`/`List`/`Set`/`Tuple` use in `typsphinx/` and `tests/` onto builtin generics
and `typing.Iterator` onto `collections.abc`. Remove the `UP006`/`UP035` ruff ignores so `ruff check .`
enforces the new shape, and rewrite `CLAUDE.md:75` so it no longer forbids the work. Then show, by
measurement, that nothing changed except API-reference type text (QUA-09, QUA-11, QUA-12, DOC-22,
DOC-23).

The ROADMAP already binds almost everything about this phase: the three orderings (constraint 1),
the todo-move-with-flip commit (constraint 2), the fresh repo-wide count (constraint 3), no dependabot
ruff bump mid-flight (constraint 4), `ruff --fix` plus the one `__init__.py:15` hand edit with no
`sed` and no `--preview` (constraint 5), the five QUA-12 legs and their same-lock/same-interpreter
rule (constraint 6), the clean docs build with a control (constraint 7), the CI dispatch (constraint
8), the branch census (constraint 9), worktree isolation (constraint 11) and the standing invariants
(constraint 12). None of it is re-decided here. This discussion settled only the three things the
ROADMAP left open: the `CLAUDE.md` wording, the leg (d) corpus, and what DOC-23's docs build covers.
The owner accepted the recommended option for all three.

**Measured at discussion time (2026-09-13, main checkout, ruff 0.16.6):**
`ruff check . --select UP006,UP035` reports 113 findings (93 UP006, 20 UP035) across 10 files:
`translator.py` 42, `builder.py` 30, `template_engine.py` 12, `template_registry.py` 4, `writer.py`
2, `__init__.py` 2, `tests/test_include_ledger_removal_gate.py` 9,
`tests/test_bundle_layout_sweep_gate.py` 6, `tests/test_include_edge_derivation_unit.py` 4,
`tests/conftest.py` 2. That matches the ROADMAP and research figures. It is recorded here as
context only. Constraint 3 still requires the executing plan to re-measure fresh.

</domain>

<decisions>
## Implementation Decisions

### DOC-22 — what `CLAUDE.md:75` says after the rewrite

- **D-01 — The bullet keeps its Python-floor fact and gains one standing instruction about annotation style.** The rewritten bullet
  states that Python 3.12+ is required, and that annotations use builtin generics (`dict[str, Any]`,
  `list[str]`, `set[...]`, `tuple[...]`) and `collections.abc` for abstract types such as `Iterator`,
  not `typing.Dict`/`List`/`Set`/`Tuple`/`Iterator`. This is an instruction about how to write code,
  so it reads true on both sides of the ignore flip. Before the flip it is exactly what authorises
  the conversion plans. After the flip ruff enforces it.

- **D-02 — The rewrite drops every flip-dependent claim and every pointer to the deferral.** Removed: the claim that ruff
  "intentionally ignores" `UP006`/`UP035`, "this is a deliberate deferral", the `todos/pending/` path,
  and "Don't modernize typing imports until that todo lands". No replacement sentence says whether
  ruff enforces or ignores those rules. There is no history note ("was deferred until v0.9.4"),
  because `CLAUDE.md` carries operational facts only (v0.9.3 Phase 68 D-07).

- **D-03 — No standing prohibition on `from __future__ import annotations` or on PEP 604 unions is added.** Option (c) was
  rejected. Both refusals are fences on this milestone's scope (ROADMAP constraint 5 and the REQUIREMENTS
  Out of Scope table), and those already bind every plan in this phase. As standing rules in
  `CLAUDE.md` they would also misdescribe the code. `typsphinx/` already carries 52 `| None`
  annotations (measured: translator 27, template_engine 13, pdf 4, template_registry 4, builder 2,
  pathfmt 1, writer 1), so a "no PEP 604" instruction would contradict what is there.

- **D-04 — The edit is confined to the one CLAUDE.md bullet at line 75.** Measured: line 75 is the only line in `CLAUDE.md`
  that mentions `UP006`, `UP035` or "modernize". No test reads `CLAUDE.md`; the three test-file hits for
  "CLAUDE" are prose in docstrings and assertion messages, and none quotes line 75. So the rewrite is
  lint-neutral and test-neutral and can land first, as constraint 1(i) requires.

### QUA-12 (d) — which `.typ` output must be byte-identical

- **D-05 — The corpus is every Sphinx project under `tests/` that has a `conf.py`, enumerated fresh at `PHASE_BASE_SHA`.** Measured at
  discussion time as 167 (166 under `tests/fixtures/`, 1 under `tests/roots/`). Each is built with
  `-b typst` on the base side and on the post-flip side, and every emitted `.typ` is compared by
  hash. The file-list sets must be equal too, so no emitted file may appear or vanish. The 12
  committed goldens alone (option (a)) were rejected: the tests already assert them, so that leg
  would only repeat leg (b).

- **D-06 — A fixture whose build fails is still part of the corpus.** Some fixtures exist to exercise error paths. For each
  project, record the build's exit status and whatever `.typ` it emitted. Both must match between the
  base and post-flip sides. A project is never dropped from the list because it fails. A difference
  in exit status is a finding, not noise.

- **D-07 — `examples/` is not in the leg (d) corpus.** Option (c) was rejected. QUA-12 (d) names "the existing golden /
  render-gate fixture corpus", and `examples/` holds user-facing samples, not test fixtures. The four
  `examples/*/conf.py` projects stay in `ruff check .` scope as before.

- **D-08 — The corpus build time is unmeasured, so the plan pilots it before committing to the full run.** Build a handful
  of projects on both sides, record wall-clock time, then extrapolate. If the full run is
  prohibitive, stop and put it to the owner. The corpus is never silently narrowed to fit a time
  budget.

### DOC-23 — what the clean docs build covers

- **D-09 — DOC-23 covers two outputs of `docs/source`, the HTML build and the `.typ` files the typstpdf build emits.** Measured:
  `docs/source/index.rst:59` includes `api/index`, and `typst_documents` has a single root `index`
  (`docs/source/conf.py:72-74`). The dogfood PDF therefore contains the API reference, and its `.typ`
  changes in type text as well. Both outputs are built clean (`rm -rf docs/_build` first) on the base
  and post-flip sides, each with a base-vs-base control build. The two builds are the tox
  `docs-html` and `docs-pdf` commands (`sphinx-build -b html source _build/html` and
  `sphinx-build -b typstpdf source _build/pdf`). The PDF binary is not compared; the `.typ` it
  compiles from is. Option (a), HTML only, was rejected because it leaves the docs `.typ` covered by
  neither DOC-23 nor leg (d).

- **D-10 — The docs `.typ` belongs to DOC-23 and never to leg (d).** Leg (d) asserts byte identity. The docs `.typ` is
  expected to differ, so putting it in leg (d) would make that leg fail by design. D-05's corpus is
  `tests/` only, which keeps the two sets disjoint.

- **D-11 — Every hunk of both docs diffs is classified, and each one must trace to a converted annotation.** "Confined to
  API-reference type text" is a checked claim. Each differing hunk must sit in an API-reference page
  (`api/…`) and be explained by a `Dict`/`List`/`Set`/`Tuple` → `dict`/`list`/`set`/`tuple` rename in
  an autodoc'd signature or field. In the HTML that includes any link target or title attached to
  the renamed type, since intersphinx may link `typing.Dict` and builtin `dict` to different
  targets. Any hunk that does not trace this way goes to the owner as a finding. It is never recorded
  as nondeterminism, because the control build is what separates nondeterminism.

  *AMENDED 2026-09-13 (plan-phase; owner chose option (a) on 70-RESEARCH.md § Contradictions C1).*
  The location rule also admits the `sphinx.ext.viewcode` source pages under
  `_modules/typsphinx/…` (viewcode is enabled at `docs/source/conf.py:38`), because each one mirrors
  a source file this phase converts. Research measured four of them differing: `builder`,
  `template_engine`, `translator` and `writer`. That list is research-time evidence; the executing
  plan enumerates the differing pages itself. A hunk on such a page is classified the same way as
  one under `api/…`: it must be the same annotation rename, or the same `typing` /
  `collections.abc` import-line change, as the converted source it mirrors. `_modules/` is not
  dropped from the HTML comparison. A hunk whose text shape changes because of the rename, such as
  `Optional[Set[str]]` → `set[str] | None` (70-RESEARCH.md Pitfall 9), still traces to a converted
  annotation and is classified, not escalated. Any other hunk still goes to the owner.

### Claude's Discretion

- The exact wording of the rewritten `CLAUDE.md:75` bullet, within D-01..D-03.
- The plan split. The research A–E conversion split in the ROADMAP is the expected shape, not a
  mandate.
- Evidence file names and layout. By this project's convention (v0.9.3 Phase 64 D-05), evidence is
  verbatim transcripts in phase markdown, with no new committed script and no new test. A new test
  would also break leg (b)'s collected-count identity.
- Which file pilots the masked-AST normalization, and how the base side is materialised: a second
  worktree at `PHASE_BASE_SHA`, or `git archive` into the scratch area.
- Whether the docs diff is taken on raw HTML or on extracted text, as long as D-11's classification
  is complete.

### Folded Todos

- **`2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md`** — this phase's own todo
  (`resolves_phase: 70`). It asks for the ignores to be dropped, the typing imports rewritten, the
  gates run and `CLAUDE.md` updated. Folded in full. Its file list is stale (constraint 3), and it
  moves to `todos/completed/` in the flip commit (constraint 2).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase contract
- `.planning/ROADMAP.md` § "🚧 v0.9.4 — Typing Modernization (ACTIVE)" — binding constraints 1–13, and
  § "Phase 70" goal, expected wave shape and SC#1..SC#5
- `.planning/REQUIREMENTS.md` — QUA-09, QUA-11, QUA-12 (a)–(e), DOC-22, DOC-23; the Out of Scope table
- `.planning/PROJECT.md` § "Current Milestone: v0.9.4 Typing Modernization"

### Research
- `.planning/research/SUMMARY.md` — conversion mechanics, the `__init__.py:15` survivor, the A–F split, and the `ast.Dict` trap
- `.planning/research/PITFALLS.md` — Pitfalls 1–5 (the CLAUDE.md self-contradiction, the multi-location sync, the stale todo list, the dependabot ruff bump)
- `.planning/research/ARCHITECTURE.md` — the file-disjoint wave derivation
- `.planning/research/STACK.md` — ruff, black and mypy behaviour measured on a scratch tree

### Prior art — masked-AST hash harness
- `.planning/milestones/v0.9.3-phases/68-documentation-follow-through-claude-md-tox-ini-flake-nix/68-TOX-EVIDENCE.md` lines 248-326 — evidence shape (hash for base and for now, equal)
- `.planning/milestones/v0.9.3-phases/68-documentation-follow-through-claude-md-tox-ini-flake-nix/68-02-PLAN.md` lines 253 and 305 — the `sk()` helper in an automated verify block. It masks docstrings and assert messages; this phase masks annotations and imports instead (see Specific Ideas)

### Files edited or measured
- `CLAUDE.md:75` — the bullet D-01..D-04 rewrite
- `pyproject.toml:128-129` — the two ignore lines and their comments (flip plan only)
- `.planning/todos/pending/2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md` — the folded todo
- `typsphinx/{translator,builder,template_engine,template_registry,writer,__init__}.py`, `tests/{conftest,test_bundle_layout_sweep_gate,test_include_edge_derivation_unit,test_include_ledger_removal_gate}.py` — the 10 files that carry findings at discussion time
- `tests/test_authors_pipeline_stage_gate.py:515` — `ast.Dict`, which must stay untouched
- `docs/source/conf.py:40`, `:72-74`, `:114`; `docs/source/index.rst:59`; `docs/source/api/index.rst` — why the API reference and the dogfood `.typ` change
- `tox.ini:67-90` — the `docs-html` and `docs-pdf` commands D-09 builds with
- `.github/workflows/ci.yml:52`, `:69` — `Lint and Format Check` / `Run lint with tox`

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- The Phase 68 `sk()` one-liner (an `ast.parse`, a mutation, then `hashlib.sha256(ast.dump(t))`) is
  the harness shape to reuse. Only the mask changes.
- `typsphinx/builder.py:11` already imports `Iterator` from `collections.abc`. That is the target form
  for `tests/test_include_ledger_removal_gate.py:47`.

### Established Patterns
- `typing` stays imported after conversion in several files (measured `from typing import` lines:
  `translator.py:9` keeps `Any` and `NamedTuple`, `builder.py:13` / `template_engine.py:13` /
  `template_registry.py:29` / `writer.py:10` / `tests/conftest.py:6` keep `Any`). The import line
  changes; it does not disappear.
- Docstring prose such as "List of directories" (`template_engine.py:274`), "Tuple of author names"
  (`:819`), "Iterator of document names" (`builder.py:1601`) and "Set of document names" (`:1649`)
  uses English words, not type names. These are out of scope and must stay byte-identical. Leg (a)
  does not mask docstrings, so it would catch an edit here.
- `translator.py:773` is `str | List[str] | None`. Only the inner `List` converts, and the `|` count
  is unchanged (SC#2's base-count check).
- `docs/source`, `README`, `CHANGELOG.md` and `examples/` carry zero `Dict[`/`List[`/`Set[`/`Tuple[`
  in prose (measured). No test string literal contains them either, so no test assertion can depend
  on the old spelling.

### Integration Points
- The main checkout's `.venv` is nixpkgs CPython 3.13.13 (`.venv/pyvenv.cfg`). A fresh worktree venv
  may be uv-managed 3.14.x. Constraint 6 applies to both D-05's corpus builds and D-09's docs builds:
  both sides use the same interpreter version.

</code_context>

<specifics>
## Specific Ideas

- **The leg (a) import mask must cover `collections.abc` as well as `typing`.** Measured:
  `tests/test_include_ledger_removal_gate.py` gains a new `from collections.abc import Iterator`
  node, because its `from typing import Dict, Iterator, Set` line splits in two. A mask covering only
  the `typing` import line would give unequal hashes on a correct conversion. So the normalization
  masks or drops every `ImportFrom` whose module is `typing` or `collections.abc`, together with
  annotation subtrees (`arg.annotation` including vararg, kwarg and kwonly, `FunctionDef.returns` /
  `AsyncFunctionDef.returns`, `AnnAssign.annotation`). Nothing else is masked. A `cast(List[...], …)`
  call argument, for instance, stays in the hash and would surface. Research found none, and a
  surviving one would be a finding. Pilot on one file first, then show the mask is not vacuous: an
  intentional non-annotation edit in a scratch copy must change the hash.
- **The rewritten `CLAUDE.md` bullet is read at two commits.** It must be true at the last pre-flip
  commit and at the post-flip tip (SC#1), so the check is a reading against D-01..D-03, not a grep for
  one phrase.

</specifics>

<deferred>
## Deferred Ideas

None came up in discussion; it stayed within the phase scope.

### Reviewed Todos (not folded)
- `2026-08-29-hardcoded-delimiter-path-fragments-in-translator-relative-path-debug-logs.md` — MSG-06. ROADMAP constraint 12 forbids absorbing it even though `translator.py` is edited here.
- `2026-09-13-doctest-block-unhandled-collapses-examples-to-one-line.md` — TRN-01, a Future Requirement. It changes emitted output, which this phase must not do.
- `2026-08-14-numref-number-diverges-per-master-and-vanishes-for-non-root-only-figures.md` — NUM-01, a Future Requirement. It changes output.
- `2026-08-16-root-toctree-duplicates-section-children-in-html-sidebar.md` — DOC-18, a Future Requirement. It would move the DOC-23 docs diff outside type text.
- `2026-07-22-add-sphinx-linkcheck-ci-job.md` — QUA-08, a Future Requirement. It needs a workflow edit, which constraint 12 forbids.

</deferred>

---

*Phase: 70-typing-modernization-and-its-behaviour-identity-evidence*
*Context gathered: 2026-09-13*
