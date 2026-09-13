---
phase: 70-typing-modernization-and-its-behaviour-identity-evidence
verified: 2026-09-13T00:00:00Z
status: human_needed
score: 5/5 must-haves verified
covered_files:
  - ".planning/REQUIREMENTS.md"
  - ".planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-01-PLAN.md"
  - ".planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-01-SUMMARY.md"
  - ".planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-02-PLAN.md"
  - ".planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-02-SUMMARY.md"
  - ".planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-03-PLAN.md"
  - ".planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-03-SUMMARY.md"
  - ".planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-04-PLAN.md"
  - ".planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-04-SUMMARY.md"
  - ".planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-05-PLAN.md"
  - ".planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-05-SUMMARY.md"
  - ".planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-06-PLAN.md"
  - ".planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-06-SUMMARY.md"
  - ".planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-07-PLAN.md"
  - ".planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-07-SUMMARY.md"
  - ".planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-08-PLAN.md"
  - ".planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-08-SUMMARY.md"
  - ".planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-09-PLAN.md"
  - ".planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-09-SUMMARY.md"
  - ".planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-10-PLAN.md"
  - ".planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-10-SUMMARY.md"
  - ".planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-11-PLAN.md"
  - ".planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-11-SUMMARY.md"
  - ".planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-12-PLAN.md"
  - ".planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-12-SUMMARY.md"
  - ".planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-13-PLAN.md"
  - ".planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-13-SUMMARY.md"
  - ".planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-AFTER-RUNTIME-EVIDENCE.md"
  - ".planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-AFTER-STATIC-EVIDENCE.md"
  - ".planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-BASELINE-EVIDENCE.md"
  - ".planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-CI-EVIDENCE.md"
  - ".planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-CONTEXT.md"
  - ".planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-CONV-BUILDER-EVIDENCE.md"
  - ".planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-CONV-TEMPLATE-EVIDENCE.md"
  - ".planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-CONV-TESTS-EVIDENCE.md"
  - ".planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-CONV-WRITER-INIT-EVIDENCE.md"
  - ".planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-CORPUS-DOCS-BASE-EVIDENCE.md"
  - ".planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-DOC22-EVIDENCE.md"
  - ".planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-DOCS-DIFF-EVIDENCE.md"
  - ".planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-FLIP-EVIDENCE.md"
  - ".planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-MASK-PILOT-EVIDENCE.md"
  - ".planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-REVIEW.md"
  - ".planning/todos/completed/2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md"
  - "CLAUDE.md"
  - "pyproject.toml"
  - "tests/conftest.py"
  - "tests/test_bundle_layout_sweep_gate.py"
  - "tests/test_include_edge_derivation_unit.py"
  - "tests/test_include_ledger_removal_gate.py"
  - "typsphinx/__init__.py"
  - "typsphinx/builder.py"
  - "typsphinx/template_engine.py"
  - "typsphinx/template_registry.py"
  - "typsphinx/translator.py"
  - "typsphinx/writer.py"
covered_digest: "v1:sha256:0de6aedc5fe9cb6ccd42cc996b87c380dc4393e5d3c2c1fd4a00be0b55507f11"
behavior_unverified: 0
overrides_applied: 0
human_verification:
  - test: "Read `## D-11 classification` in 70-DOCS-DIFF-EVIDENCE.md (83 rows, H-001..H-083) and confirm each TRACED row's 'traces to' column genuinely names a converted annotation or typing-import line, not a coincidental match."
    expected: "Every row is TRACED to a real Dict/List/Set/Tuple -> dict/list/set/tuple rename or typing/collections.abc import-line change in the source file the page mirrors; UNTRACED_HUNKS stays 0."
    why_human: "This is the exact deferred check 70-12-PLAN.md Task 2 declares via <human-check> (owner reads the classification table at end of phase). The verifier independently confirmed the table's structure, the TRACED_HUNKS=83/UNTRACED_HUNKS=0 tally, the DOCS_HTML_CONTROL=EQUAL / DOCS_TYP_CONTROL=EQUAL base-vs-base controls, and spot-checked a sample of rows (H-048..H-083) against the converted source lines they cite — all held up. But a full owner read of all 83 rows' judgment calls (e.g. the two-part Optional[Set[str]] -> set[str] | None hunk splits) was explicitly deferred to end-of-phase per the plan's own verify contract, and a subjective classification judgment over an evidence table is not something grep can certify as complete."
---

# Phase 70: Typing Modernization and Its Behaviour-Identity Evidence Verification Report

**Phase Goal:** a contributor opening any module under `typsphinx/` or `tests/` finds builtin generics (`dict[str, Any]`, `list[str]`, `set[...]`, `tuple[...]`) and `collections.abc.Iterator`. `ruff check .` enforces that shape instead of suppressing it, and `CLAUDE.md` no longer tells an executor not to write it. A reader of the API reference sees `dict[str, Any]` where they saw `Dict[str, Any]`, and nothing else changes: no byte of emitted Typst, no test count, no line of mypy output.

**Verified:** 2026-09-13
**Status:** human_needed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 (SC#1) | `CLAUDE.md` rewrite commit is an ancestor of every conversion commit and of the flip commit; the todo left `pending/` in the same commit that removed the ignores; no residual `pending/` path reference outside `.planning/` | ✓ VERIFIED | `git merge-base --is-ancestor 3c5e281c <c>` returned 0 for all 5 real conversion commits + flip commit `0224b5ea` (independently re-run). `git show --name-status -M --format= 0224b5ea` shows exactly `R100 pending/... -> completed/...` + `M pyproject.toml` in one commit. `.planning/todos/pending/` has no modernize-typing file; `.planning/todos/completed/` does. `git grep -n "todos/pending/2026-07-22-modernize" -- . ':!.planning'` returns empty (exit 1), independently re-run. |
| 2 (SC#2) | Zero `UP006`/`UP035` fresh repo-wide; ignores and deferral comments gone from `pyproject.toml`; bare `ruff check .` clean, no `--preview`; no `from typing import` naming `Dict/List/Set/Tuple/Iterator` under `typsphinx/`/`tests/`; `__init__.py:15` reads `from typing import Any`; `__future__`/`Optional[`/`Union[`/`\| None` counts unchanged from base; `tests/test_authors_pipeline_stage_gate.py` untouched with `ast.Dict` intact at :515 | ✓ VERIFIED | Independently re-ran `ruff check . --select UP006,UP035` → "All checks passed!"; `ruff check .` → "All checks passed!". `grep -n "UP006\|UP035" pyproject.toml` → empty. Word-boundary grep for banned typing imports → empty (0 hits) in both `typsphinx/` and `tests/`. `sed -n 15p typsphinx/__init__.py` → `from typing import Any`. Counts re-measured: `FUTURE_ANNOTATIONS=0`, `Optional[`=0, `Union[`=0, `\| None`=82 — matches `70-AFTER-STATIC-EVIDENCE.md`'s `_BASE` keys exactly (independently re-run, same numbers). `git diff 697a1132..HEAD -- tests/test_authors_pipeline_stage_gate.py` empty; `sed -n 515p` still shows `ast.Dict`. |
| 3 (SC#3 / QUA-12 a,c,e) | Masked-AST hash equal per converted file (leg a); every changed `tests/` line is an import/annotation line, no assert line touched (leg c); `mypy typsphinx/` stdout string-identical before/after, same interpreter/lockfile (leg e) | ✓ VERIFIED | `70-AFTER-STATIC-EVIDENCE.md` records all 10 converted files EQUAL under the masked-AST harness (`MASK_HARNESS_SHA256` reproducibility chain shown), `LEG_C_NON_TYPING_LINES=0`, `LEG_C_ASSERT_LINES=0`. Independently re-ran `mypy typsphinx/` in this checkout (different mypy binary: nixpkgs 2.1.0 vs. the evidence's uv-managed 2.3.1) and got byte-identical stdout `Success: no issues found in 9 source files`, hashing to the same `46984ca2...` recorded as both `MYPY_STDOUT_SHA256_BEFORE` and `_AFTER`. |
| 4 (SC#4 / QUA-12 b,d + DOC-23) | Pytest collected/passed counts identical before/after; `.typ` output byte-identical over the 167-project corpus; clean docs build differs from base only in API-reference type text (incl. `_modules/` viewcode pages per the D-11 AMENDED rule), with a base-vs-base control showing zero diff | ✓ VERIFIED | `70-AFTER-RUNTIME-EVIDENCE.md`: `PYTEST_RESULT_AFTER = 1547 passed 1 skipped` = `PYTEST_RESULT_BEFORE`; leg (d) corpus manifest hash `4c87a31d...` equal on both sides over all 167 entries (21 non-zero-exit fixtures match too). `70-DOCS-DIFF-EVIDENCE.md`: `DOCS_HTML_CONTROL = EQUAL`, `DOCS_TYP_CONTROL = EQUAL` (base-vs-base control), differing pages confined to `api/index.{html,typ}` + the 4 `_modules/typsphinx/{builder,template_engine,translator,writer}.html` pages the AMENDED D-11 rule admits; all 83 hunks classified TRACED, `UNTRACED_HUNKS=0`, `DOC23_VERDICT=MET`. Spot-checked a sample of the H-048..H-083 rows against the cited source lines (e.g. H-051 `toctree_includes: Dict[str, List[str]]` → `translator.py:344`) — correct. |
| 5 (SC#5) | Gate quartet green on the post-flip tip; branch census clean (no decoy); branch pushed with tracking; CI dispatched on the pushed tip completed with all 12 jobs success, both `windows-latest` and both `macos-latest` lanes named individually, `Lint and Format Check` green | ✓ VERIFIED | Independently queried GitHub live (not just the evidence file): `gh run view 34742047126` → `status: completed, conclusion: success, headSha: e70e31fb...`; all 12 jobs listed success including `Lint and Format Check`, `Test Python 3.12/3.13 on windows-latest`, `Test Python 3.12/3.13 on macos-latest`. `git ls-remote origin gsd/v0.9.4-typing-modernization` → `e70e31fb...`, matching the CI-verified tip. `git ls-remote origin 'refs/heads/gsd/v0.9.4-*'` shows only the one canonical branch — no decoy. `git diff --name-only e70e31fb..HEAD` shows only `.planning/` docs changed post-push — no code drift after the verified CI tip. |

**Score:** 5/5 truths verified (0 present, behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `CLAUDE.md:75` | Rewritten annotation-style instruction, no flip-dependent claim | ✓ VERIFIED | Confirmed on disk: "Annotations use builtin generics (`dict[str, Any]`, `list[str]`, `set[str]`, `tuple[str, ...]`) and take abstract types such as `Iterator` from `collections.abc`, not `typing.Dict`/`List`/`Set`/`Tuple`/`Iterator`." No mention of UP006/UP035/deferral/pending path. |
| `pyproject.toml` `[tool.ruff.lint] ignore` | No `UP006`/`UP035` | ✓ VERIFIED | Confirmed absent by direct grep. |
| `typsphinx/{translator,builder,template_engine,template_registry,writer,__init__}.py` | Builtin generics, no `Dict/List/Set/Tuple` typing imports | ✓ VERIFIED | Word-boundary grep for banned imports returns zero across all files; masked-AST hashes equal to base. |
| `tests/{conftest,test_bundle_layout_sweep_gate,test_include_edge_derivation_unit,test_include_ledger_removal_gate}.py` | Same conversion, `Iterator` from `collections.abc` | ✓ VERIFIED | Same grep result; masked-AST hashes equal; leg (c) confirms only import/annotation lines changed. |
| `.planning/todos/completed/2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md` | Moved from `pending/` | ✓ VERIFIED | File present in `completed/`, absent from `pending/`. |
| `70-*-EVIDENCE.md` (13 files) | Verbatim measurement transcripts for each SC/leg | ✓ VERIFIED | Read all; cross-checked verdict keys (`SC1..SC5_VERDICT`, `LEG_A..LEG_E_VERDICT`, `DOC23_VERDICT`) all `MET`, and independently reproduced a sample of the underlying measurements (ruff, mypy, git ancestry, CI, branch state). |

### Key Link Verification

Not applicable in the conventional component→API sense — this phase's "wiring" is the evidence chain linking each Success Criterion to a measurement. Verified above per-truth: SC#1→ancestry (re-run), SC#2→static counts (re-run), SC#3→masked-AST/leg-c/mypy (re-run mypy independently, cross-checked leg-a/leg-c tables), SC#4→pytest/corpus/docs-diff (cross-checked tables, control builds), SC#5→CI/branch (re-queried GitHub live).

### Anti-Patterns Found

None. Scanned all 10 converted files (`translator.py`, `builder.py`, `template_engine.py`, `template_registry.py`, `writer.py`, `__init__.py`, and the four `tests/` files) for `TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER` — zero hits. Code review (`70-REVIEW.md`) is `status: clean`, `critical: 0, warning: 0, info: 1` — the one Info (`IN-01`, `template_engine.py:665` `str = None`) is pre-existing at the phase base (confirmed same line pattern exists at `697a1132`) and out of this phase's scope, per the orchestrator's note and independently spot-checked.

### Requirements Coverage

| Requirement | Source Plan(s) | Description | Status | Evidence |
|---|---|---|---|---|
| QUA-09 | 70-02, 70-09, 70-10, 70-13 | Ignores removed, zero fresh UP006/UP035 | ✓ SATISFIED | SC#1/SC#2 truths above |
| QUA-11 | 70-04..70-08, 70-10 | All typing.Dict/List/Set/Tuple → builtins, Iterator → collections.abc, no PEP 604/`__future__`/API changes | ✓ SATISFIED | SC#2 truth, leg (a)/(c) |
| QUA-12 | 70-02..70-04, 70-05..70-08, 70-11 | 5-leg behaviour-identity evidence (a-e) | ✓ SATISFIED | SC#3/SC#4 truths, all leg verdicts MET |
| DOC-22 | 70-01, 70-09, 70-10 | CLAUDE.md:75 rewritten pre-conversion, todo moved with flip | ✓ SATISFIED | SC#1 truth |
| DOC-23 | 70-03, 70-12 | Clean docs diff confined to API-reference type text, recorded as evidence | ✓ SATISFIED (pending human read of classification table) | SC#4 truth, `70-DOCS-DIFF-EVIDENCE.md` |

No orphaned requirements: `.planning/REQUIREMENTS.md`'s Phase 70 mapping table lists exactly QUA-09, QUA-11, QUA-12, DOC-22, DOC-23, and every plan's `requirements:` frontmatter field sums to that same set with no extras. REL-13 correctly stays scoped to Phase 71 and its checkbox remains `[ ]` (not touched by this phase's plans).

### Human Verification Required

1. **Owner reads `## D-11 classification` in `70-DOCS-DIFF-EVIDENCE.md`**

**Test:** Read all 83 rows (H-001..H-083) of the classification table and confirm each TRACED row's cited source line genuinely explains the diff hunk, including the two-part `Optional[Set[str]]` → `set[str] | None` shape-change splits (Pitfall 9).
**Expected:** Every row holds up under a full read; `UNTRACED_HUNKS` stays `0`; no hunk should have been dismissed as "nondeterminism."
**Why human:** This is the exact `<human-check>` 70-12-PLAN.md Task 2 declares as deferred to end-of-phase (D-11's classification is inherently a judgment call about whether prose/HTML text differences trace to a rename, not a pure grep-checkable fact). The verifier confirmed the table's mechanics (tally, control builds, hunk count derivation) and spot-checked a sample of rows against the cited source, all of which held — but a full 83-row judgment read was explicitly scoped to the owner, not the automated verify block.

### Gaps Summary

No gaps found. All five roadmap Success Criteria are independently verified against the live codebase and, where feasible, re-measured directly (ruff, mypy, git ancestry, GitHub CI/branch state) rather than taken solely from the plan-produced evidence files. The sole open item is the owner's own read of the DOC-23 hunk-classification table, which the phase's own plan explicitly deferred to this point rather than a defect found during verification.

Two items noted from the orchestrator's notes were checked and found non-blocking:
- The 70-12 Task 1 automated-verify oracle defect (localized `diff -rq` output breaking the English-text `grep` checks) is a plan-authoring bug in the verify script, not a defect in the underlying evidence; the substantive DOC-23 diff/classification stands on its own merits as reviewed above.
- `CONVERSION_COMMIT_COUNT = 8` includes 3 wave-3 merge commits alongside 5 real conversion commits; all 8 are between the CLAUDE.md rewrite and the flip commit as required by SC#1's ordering, so the wording imprecision ("conversion commit" for a merge) doesn't affect the ordering guarantee.

---

*Verified: 2026-09-13*
*Verifier: Claude (gsd-verifier)*
