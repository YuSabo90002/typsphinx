# Phase 60 — Path-Quoting Evidence (Consolidated by Reference)

**No file in this phase is named `60-VERIFICATION.md`** — that name is reserved and overwritten
wholesale by `gsd-verifier` (per `60-CONTEXT.md` D-10, inheriting 59 D-11 / 58 D-07).

This document consolidates the phase's five plans' evidence **by REFERENCE ONLY**, per D-10.
`60-01-EVIDENCE.md` through `60-04-EVIDENCE.md` are read-only inputs to this file — nothing here
copies a transcript, rewrites a section, or appends to any of them. Each row below names the
requirement, the plan that closed it, the per-plan evidence file, the section heading holding its
recorded RED and green, and a one-line statement of what that RED actually was, in the shape D-12
assigned that site.

## Requirement-by-requirement reference table

| Requirement | Closing plan | Evidence file | RED section | GREEN section | What the RED actually was (D-12 shape) |
|---|---|---|---|---|---|
| MSG-02 | 60-01 | `60-01-EVIDENCE.md` | `## MSG-02 RED` | `## MSG-02 GREEN` | The legitimate wave-1 tracer-slice RED: `ModuleNotFoundError: No module named 'typsphinx.pathfmt'` (exit code 2) — the leaf module did not exist yet, so nothing could be quoted at all. |
| MSG-03 | 60-02 | `60-02-EVIDENCE.md` | `## RED — three 57-11 builders (single-quote half)`, `## RED — _resolve_target_stem`, `## RED — _track_image rehome warning`, `## RED — _validate_output_path_collisions`, `## RED — _copy_bundle_directory` | `## GREEN` | Two distinct shapes per D-12: (a) the **single-quote** case at the three 57-11 message builders (`_conf17_violation_message`, `_templates_path_collision_message`, `_bundle_destination_collision_message`) — their backslash half was already green since Phase 57, so only the hardcoded-apostrophe-delimiter defect (closing early on an embedded `'`) remained to gate; (b) the **doubled backslash**, still on a bare `!r` conversion, at the five other message families (`_resolve_target_stem`'s path-refusal warning, `_track_image`'s image-rehome warning, both `_validate_output_path_collisions()` branches, `_copy_bundle_directory`'s never-copied `ExtensionError`). |
| MSG-04 | 60-03 | `60-03-EVIDENCE.md` | `## RED — wrapper-render debug log` | `## GREEN` | The **`caplog` DEBUG read** — `writer.py`'s wrapper-render site is a `logger.debug()` call, so its RED was captured via `caplog.at_level("DEBUG")` rather than an exception or a warning: `AssertionError: Expected every backslash run to be a single unescaped separator`, with the doubled backslash present in `wrapper_relative_dir` and `include_path`. |
| MSG-05 | 60-04 | `60-04-EVIDENCE.md` | `## RED shape 1 — doubled backslash (str template)`, `## RED shape 2 — leaked class-name wrapper (Path template)` | `## GREEN` | **Two independent RED shapes**, as D-12 predicts for a site whose value may be a `pathlib.Path`: (1) the **doubled backslash** for a `str`-typed `template` value (`re.findall(r"\\\\+", ...)` finding 3 and 6 doubled runs at the CONF-17 and existence-check messages respectively); (2) the **leaked class-name wrapper** for a `pathlib.Path`-typed `template` value — pre-fix `{template!r}` renders `PosixPath('/some/path/...')`, leaking Python's internal class name into a user-facing `conf.py` error, caught via `pytest.raises(ExtensionError)` + `str(excinfo.value)`. |

## This plan's own acceptance measurements (SC#2, SC#3, SC#5)

Referenced by section, not copied — see `60-05-EVIDENCE.md`:

- **SC#2 — repo-wide discovery grep and its classification table**: `60-05-EVIDENCE.md`
  § "SC#2 repo-wide discovery grep". Zero path-valued interpolations remain unrouted in
  `typsphinx/builder.py`, `typsphinx/writer.py` or `typsphinx/template_registry.py`. A genuinely
  path-valued hardcoded-delimiter site was found in a fourth module
  (`typsphinx/translator.py:5047`/`:5152`) and filed as a new todo rather than fixed — see that
  section's "Fourth-module hits" subsection and the filed record at
  `.planning/todos/pending/2026-08-29-hardcoded-delimiter-path-fragments-in-translator-relative-path-debug-logs.md`.
- **SC#3 — over-reach measurement**: `60-05-EVIDENCE.md` § "SC#3 over-reach measurement".
  Every surviving identifier-valued class (registry keys, docnames, the whole-tuple config
  `entry`, the config `doc_tuple`, sorted key lists) is measured by command and output, and
  `template_registry.py`'s deliberately-excluded type-check message (line 420, one surviving
  `template!r` conversion) is confirmed still `!r`-quoted with its two falsification-gate
  assertions green and unmodified.
- **SC#5 — zero-test-edit measurement and final local gate**: `60-05-EVIDENCE.md`
  § "SC#5 zero test edits (measured)" and § "Final local gate". The phase's whole `tests/` diff
  against `PHASE_BASE_SHA` is only-`A` plus one pure-addition `M` for
  `tests/test_templates_path_collision_gate.py`, cross-checked against every module
  `58-REPR-CENSUS.md` enumerates (none modified), with the AST census guard green and unmodified.
  The final local gate (`uv run pytest -q`, `uv run black --check .`, `uv run mypy typsphinx/`)
  is green with a `0 skipped` census across all four new gate modules.
- **RED-first ledger (phase-wide)**: `60-05-EVIDENCE.md` § "RED-first ledger (phase-wide)" — the
  same requirement-by-requirement table this document's own reference table above restates in
  D-12's shape language.
- **SC#5 3-OS CI dispatch**: `60-05-EVIDENCE.md` § "SC#5 3-OS CI dispatch". That section was
  recorded as `PENDING — owner dispatch required` by 60-05 (a worktree cannot dispatch against a
  tip that does not exist yet) and was resolved by the orchestrator after the final merge; it now
  carries both dispatches, the failing one included.

## Post-plan gate findings and their fixes (orchestrator, after wave 3)

Recorded here because three defects were found *after* every plan reported complete and every local
suite was green — the phase's own closing evidence would misrepresent how it closed without them.
None of the five per-plan evidence files is modified by this section; it references commits.

| # | Found by | Defect | Fix | Reachable locally? |
|---|---|---|---|---|
| 1 | CI dispatch 1, `Lint and Format Check` | `ruff F401` — unused module-scope `importlib.util` in `tests/test_pathfmt.py:28` (the name is used only inside a docstring and inside the string literal executed as a subprocess, which carries its own import) | `78c85fe4` | **No** — `ruff`'s PyPI generic-linux wheel cannot exec in this dev sandbox (QUA-06); CI holds lint authority |
| 2 | CI dispatch 1, both `windows-latest` test jobs | `test_conf17_violation_message_has_no_doubled_separator` asserted a POSIX-only branch outcome unguarded on all three OSes | `130f614e` — branch asserted per platform; MSG-05's real invariants asserted on both | **No** — POSIX-only dev host; production code was already correct on Windows |
| 3 | `60-REVIEW.md` CR-01 (code-review gate) | `quote_path()`'s both-quotes branch produced a run of two backslashes when the value's own `\` sat immediately before an apostrophe — falsifying D-01a, which the module docstring stated as settled fact | `e3399825` — SQL-style apostrophe doubling; D-01 AMENDED in `60-CONTEXT.md` | Yes in principle, but **no fixture placed the backslash in that adjacency**, so the suite stayed green over a false invariant |

**SC#5 re-measured after all three fixes** (the fixes touch `tests/`, so the zero-test-edit claim
must be re-established, not assumed):

- `git diff --name-status <PHASE_BASE_SHA>..HEAD -- tests/` is still **only `A` plus one `M`** —
  the four new gate modules added, and `tests/test_templates_path_collision_gate.py` modified.
- That one `M` is still a **pure addition**: `git diff --numstat` reports `50  0` (50 added, 0
  removed).
- `tests/test_repr_census_guard.py`, `tests/test_out02_escape_target_gate.py` and
  `tests/test_builder.py` are **untouched** across the whole phase.
- Both edited test files (`tests/test_pathfmt.py`,
  `tests/test_template_registry_path_quoting_gate.py`) are themselves `A` in this diff — files this
  phase created. No pre-existing test was edited, so SC#5 holds as stated.

**Cross-phase regression gate** (not a plan obligation; run by the orchestrator before
verification): Phase 58 + 59 test files, 83 tests, all passed on the final tip.
