# Phase 52 Plan 03 — Goal-Claim Evidence

**Provisioning note:** all commands below were run inside this plan's isolated git worktree
(`.claude/worktrees/agent-a1caa5c8e9c2fe049`), after
`uv sync --extra dev` with `VIRTUAL_ENV`/`UV_PROJECT_ENVIRONMENT` unset, per this project's
`CLAUDE.md` § "Worktree-isolated execution". Every command below was invoked through `uv run`.

## SC#3 — the goal-claim half

`.planning/REQUIREMENTS.md`'s milestone goal sentence, quoted verbatim:

> A `typst_documents` configuration declaring more than one master produces a complete PDF for
> each of them — no silently dropped content, no compile failure — by moving composition from
> "one `.typ` shared by every master, with the include decision baked in at write time" to
> "per-master wrapper files that publish their include edge set as Typst `state`, plus
> template-less docname-named content files that emit state-guarded includes at the toctree's
> own position".

ROADMAP Phase 52 SC#3 requires this discharged on generated evidence: "a real
`sphinx-build -b typstpdf` over a **multi-master project with ≥2 masters and ≥1 shared child**,
its PDFs opened via `pypdf`, with specific text/page assertions proving each master's full
content is present — not 'the code looks correct' and not 'one representative fixture
compiles'."

The fixture that discharges it is `tests/fixtures/state_guard_three_master_gate/`: **three**
masters (`m1`, `m2`, `m3`) and **two** shared children (`common_a`, `common_b`), plus one
mid-level intermediate document (`mid`) that carries a heading but no marker — exceeding SC#3's
"≥2 masters and ≥1 shared child" minimum on both axes. Per-master include sets, derived from the
fixture's own toctree membership (`m1` lists `[mid, common_a]`; `m2` lists
`[common_a, common_b]`; `m3` lists `[common_b, mid]`; `mid` lists `[common_b]`):

- `m1` → `{m1, mid, common_b, common_a}`
- `m2` → `{m2, common_a, common_b}`
- `m3` → `{m3, common_b, mid}`

`common_a` is reachable from `m1`/`m2` only (not `m3`); `common_b` is reachable from all three,
each time through a different immediate parent (`mid` for `m1`, `m2` itself, `m3` itself) — no
cross-master coordination is possible in the algorithm being proven correct.

## The gate

`tests/test_state_guard_shapes_gate.py::TestThreeMasterGate` now carries two methods over this
one fixture, built once per module run:

- `test_three_masters_each_render_shared_children_once` (pre-existing, unmodified) — covers the
  shared-child occurrence counts (`COMMON-A-MARKER`/`COMMON-B-MARKER` appear exactly once per
  master's PDF that reaches them) and the resolved heading levels (`typst.query()` against the
  compiled wrapper, proving `common_b` resolves at level 3 under `m1`, level 2 under `m2`, level
  2 under `m3`).
- `test_three_masters_each_carry_their_full_include_set_in_pdf` (new, this plan) — covers the
  completeness and isolation halves: every document in a master's own include set contributes
  content to that master's PDF (including the non-marker-bearing `mid` document), a document
  outside that set contributes nothing, and no master's own body leaks into another master's
  PDF — asserted at both full-text and page level via the new `_Build.pdf_page_texts()` helper.

Full `-v` pytest transcript, both methods PASSED:

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a1caa5c8e9c2fe049/.venv/bin/python
cachedir: .pytest_cache
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a1caa5c8e9c2fe049
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 2 items

tests/test_state_guard_shapes_gate.py::TestThreeMasterGate::test_three_masters_each_render_shared_children_once PASSED [ 50%]
tests/test_state_guard_shapes_gate.py::TestThreeMasterGate::test_three_masters_each_carry_their_full_include_set_in_pdf PASSED [100%]

============================== 2 passed in 4.07s ===============================
```

JUnit `testsuite` attribute line from the same run:

```
testsuite name="pytest" errors="0" failures="0" skipped="0" tests="2" time="4.070" timestamp="2026-08-15T09:55:16.858231+09:00" hostname="Yuta-PC"
```

## What the assertions prove

| Assertion family | Concrete strings / counts asserted |
|---|---|
| Presence — full include set, per master | `manual1.pdf`: `"Mid" in text`, `COMMON-A-MARKER` count `== 1`, `COMMON-B-MARKER` count `== 1`. `manual2.pdf`: `COMMON-A-MARKER` count `== 1`, `COMMON-B-MARKER` count `== 1`. `manual3.pdf`: `"Mid" in text`, `COMMON-B-MARKER` count `== 1`. |
| Absence — outside the include set | `manual3.pdf`: `COMMON-A-MARKER` count `== 0` (`common_a` unreachable from `m3`). `manual2.pdf`: `"Mid" not in text` (`m2` never toctrees `mid`). |
| Cross-master isolation | `manual1.pdf` excludes `"M2"` and `"M3"`; `manual2.pdf` excludes `"M1"` and `"M3"`; `manual3.pdf` excludes `"M1"` and `"M2"` — the cross-master absence form, deliberately not a same-master presence check (the fixture's own title, e.g. `"Three Master Gate — M1"`, would satisfy a same-master token check via the title page alone and prove nothing about the body). |
| Page-level occurrence | Each PDF has `len(pages) >= 1`. `COMMON-A-MARKER`/`COMMON-B-MARKER` occur on exactly one page where present (`manual1.pdf`: both, page 2 of 3; `manual2.pdf`: both, page 2 of 3; `manual3.pdf`: `COMMON-B-MARKER`, page 2 of 3), and on zero pages where absent (`manual3.pdf`: `COMMON-A-MARKER`, 0 pages). |

Measured page shape (all three PDFs, `uv run python` probe against the compiled output, read
before any assertion was written per the plan's Step 2): each PDF has exactly 3 pages — page 0
is the title page (`Three Master Gate — M<n>` / author / release / page number), page 1 is the
generated table of contents (heading titles, no marker strings), page 2 is the body (headings
plus marker strings). This is why the page-level marker assertions above target page 2
specifically for the markers, while the "Mid" full-text presence/absence assertions use
`pdf_text()` rather than a page-indexed assertion — "Mid" is a heading title, so it legitimately
appears on both the TOC page (page 1) and the body page (page 2) wherever it's reachable, unlike
the markers, which appear only in body content.

## Non-vacuity — the detector fires

The absence assertion inverted was the **page-level** form —
`assert len(_pages_with(m3_pages, "COMMON-A-MARKER")) == 0` (the marker that must occur on zero
pages of `manual3.pdf`) — changed in a scratch, never-committed edit to
`assert len(_pages_with(m3_pages, "COMMON-A-MARKER")) >= 1`, run, and shown to FAIL:

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a1caa5c8e9c2fe049/.venv/bin/python
cachedir: .pytest_cache
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a1caa5c8e9c2fe049
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 1 item

tests/test_state_guard_shapes_gate.py::TestThreeMasterGate::test_three_masters_each_carry_their_full_include_set_in_pdf FAILED [100%]

=================================== FAILURES ===================================
_ TestThreeMasterGate.test_three_masters_each_carry_their_full_include_set_in_pdf _

>       assert len(_pages_with(m3_pages, "COMMON-A-MARKER")) >= 1  # SCRATCH: inverted for non-vacuity proof, DO NOT COMMIT
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       AssertionError: assert 0 >= 1
E        +  where 0 = len([])
E        +    where [] = <function TestThreeMasterGate.test_three_masters_each_carry_their_full_include_set_in_pdf.<locals>._pages_with at 0x7516c9b96980>([...], 'COMMON-A-MARKER')

tests/test_state_guard_shapes_gate.py:581: AssertionError
=========================== short test summary info ============================
FAILED tests/test_state_guard_shapes_gate.py::TestThreeMasterGate::test_three_masters_each_carry_their_full_include_set_in_pdf - AssertionError: assert 0 >= 1
============================== 1 failed in 3.86s ===============================
```

This is the proof the page-scan detector fires on a real violation rather than merely passing
on a clean tree. The inverted variant was **never committed** — it existed only as an in-place
edit to the already-modified, not-yet-committed working copy of
`tests/test_state_guard_shapes_gate.py`, made after Task 1's real assertions were written and
verified green, and reverted before any commit touched the file. The committed file was then
re-run and confirmed green again:

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a1caa5c8e9c2fe049/.venv/bin/python
cachedir: .pytest_cache
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a1caa5c8e9c2fe049
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 2 items

tests/test_state_guard_shapes_gate.py::TestThreeMasterGate::test_three_masters_each_render_shared_children_once PASSED [ 50%]
tests/test_state_guard_shapes_gate.py::TestThreeMasterGate::test_three_masters_each_carry_their_full_include_set_in_pdf PASSED [100%]

============================== 2 passed in 4.07s ===============================
```

`git status --porcelain tests/` after this sequence produced no output — no stray scratch
file or uncommitted diff was left behind.

## Why there is no pre-fix RED

This gate is additive over behaviour Phases 47 and 49 already shipped — the per-master
state-guarded include mechanism it proves was implemented and gated (with its own recorded-RED
fixtures) in those two prior phases, not in this one. The milestone's standing GATE-01 bar (a
recorded-RED fixture for every node-handler change) governs changes to `typsphinx/`'s node
handlers, and this phase changes none — `git diff --name-only -- typsphinx/` produces no output
(confirmed above and re-confirmed in the Executed-versus-skipped section). There is therefore no
pre-fix RED transcript to manufacture here. The non-vacuity observation in the section above is
what stands in for it: it proves the new assertions are load-bearing (capable of failing on a
real violation) without requiring the production code itself to have ever been broken during
this plan.

## Executed versus skipped

`typst` and `pypdf` were both importable in this worktree's provisioned environment (`uv sync
--extra dev` installed `typst==0.15.0` and `pypdf==6.14.2`, confirmed by the sync transcript and
by the module's `pytestmark = pytest.mark.skipif(not (TYPST_AVAILABLE and PYPDF_AVAILABLE), ...)`
guard being inactive — both test methods collected and ran, `skipped="0"` in the JUnit XML).
The gate **RAN**, it did not skip. Both `-b typst` and `-b typstpdf` subprocess builds
(`build.pdf_result.returncode == 0`, asserted in the new method and confirmed by the earlier
manual probe build) completed successfully against real `sys.executable -m sphinx` invocations,
and every assertion above was evaluated against real `pypdf.PdfReader`-extracted text, not a
skipped or mocked path.

Prep/publish fence check, re-confirmed at the end of this plan:

```
$ git tag -l v0.8.0
```
(no output)

```
$ git ls-remote --tags origin v0.8.0
```
(no output)
