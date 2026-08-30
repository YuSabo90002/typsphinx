---
phase: 63
slug: v0-9-2-release-prep-prep-only
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-30
---

# Phase 63 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
>
> Seeded by plan-phase from `63-RESEARCH.md` § "Validation Architecture". This is a **prep-only
> release phase**: it changes no `typsphinx/` behaviour, so there is no product-side RED-first gate.
> What it validates instead is (a) that the version-literal lockstep holds across four files, (b)
> that the release body the extractor actually emits is *read*, not reasoned about, (c) that the
> bumped tree is green on runs executed **in this phase**, and (d) that the phase took **zero
> irreversible action** and REL-09's checkbox never moved.
>
> **The unit of proof here is a recorded observation, not a passing assertion.** Several rows below
> are audits whose evidence is a transcript in an evidence file, not a test exit code. A row that
> cannot be run is never recorded as a pass — see § "Skipped is not passed".

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (config in `pyproject.toml` `[tool.pytest.ini_options]`), orchestrated via `tox` (`env_list = py312, py313, lint, type, cov, docs`) |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]`; `tox.ini` |
| **Quick run command** | `uv run pytest -m "not slow"` |
| **Full suite command** | `uv run pytest` (matches CI; includes the `@pytest.mark.slow` corpus/docs-build gates) |
| **Estimated runtime** | full suite several minutes · one CI dispatch ≈ 7 min wall clock (Phase 61's run `33260111745`) |

**Worktree note (CLAUDE.md § "Worktree-isolated execution", STANDING):** every executor first runs
`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` in its own worktree, then runs
every command via `uv run`. This is mandatory, not conditional on parallelism.

**The `docs` extra is required for two specific proofs.** `myst_parser` lives in the `docs` extra
only (`pyproject.toml:49-54`), and `tests/test_changelog_page_gate.py` guards on
`import myst_parser`. A worktree provisioned with `--extra dev` alone therefore **silently skips**
both content-coverage classes — the exact two classes that enforce D-11's `RELEASE_VERSIONS`
addition. Wherever D-11's proof or the docs-warning baseline runs, sync `--extra dev --extra docs`.

### Baselines carried in (to be re-measured, never inherited)

| Baseline | Value | Source | Obligation |
|----------|-------|--------|------------|
| Full pytest suite | **1543 passed, 5 skipped** | `62-VERIFICATION.md` line 66, Phase 62's close, 2026-08-30 | Re-run fresh on the **bumped** tree; record this phase's own count. Expect 1543/5 exactly — none of D-01..D-21 adds a test case. |
| Skips, itemised | 4× myst-parser docs-extra gap · 1× env-gated corpus report | same | All 5 pre-existing and unrelated. A **sixth** skip is a finding, not noise. |
| `tox -e docs-html` warnings | **3** | Phase 61's close, 2026-08-29 | Re-measure from a **clean** build (`rm -rf docs/_build` first) per D-21. |
| `tox -e docs-pdf` warnings | **5** | Phase 61's close, 2026-08-29 | Same. An incremental rebuild under-reports and manufactures a false "baseline match" — a repeat finding in this project, not a theoretical hazard. |

---

## Sampling Rate

- **After every task commit:** no product-behaviour code changes, so there is no per-commit product
  gate beyond the task's own evidence artifact being written and readable.
- **After every plan wave:** `uv run pytest` (full suite) plus `uv run black --check .` and
  `uv run mypy typsphinx/`. `ruff` is **deferred to CI** (D-18 AMENDED / QUA-10) — it is an
  unrunnable generic-linux ELF in a freshly `uv sync`-provisioned worktree venv on this host.
- **After the CHANGELOG edit and after the `RELEASE_VERSIONS` edit specifically:**
  `rm -rf docs/_build && uv run tox -e docs-html`, same for `docs-pdf`, warning counts compared
  against the 3 / 5 baseline; and `uv run --extra dev --extra docs pytest
  tests/test_changelog_page_gate.py -v` for D-11's own proof (all tests PASSED, **none SKIPPED**).
- **Phase gate:** one fresh 3-OS CI dispatch on the phase's final tip, **after** the bump commit
  (D-18), all 12 jobs green, both `windows-latest` lanes named individually.
- **Max feedback latency:** local suite minutes; CI dispatch ≈ 7 min wall clock.

**Gap-closure wave (waves 4–5, added 2026-08-30).** The **CHANGELOG-edit clause fires a second
time**: `63-05-T3` runs `rm -rf docs/_build && uv run tox -e docs-html`, then the same for
`docs-pdf`, with warning counts compared against the 3 / 5 baseline, and runs
`uv run --extra dev --extra docs pytest tests/test_changelog_page_gate.py` with the **skipped count
read rather than the exit code**. That clause's `RELEASE_VERSIONS` half does **not** fire — D-24
keeps `tests/test_changelog_page_gate.py` unedited, and `63-05-T3` gates on that file being
unmodified. The **phase gate deliberately does not fire a second time**, and the reason is a
measurement `63-05-T3` records rather than an assumption: every `ci.yml` job installs the `dev` extra
and none installs `docs`, every tox environment `ci.yml` invokes declares `extras = dev`, and
`tests/test_changelog_page_gate.py` guards both content-coverage classes on importing `myst_parser` —
so **no CI lane reads CHANGELOG content** and a dispatch would exercise nothing in a prose-only diff
at a cost of twelve jobs. `ruff`'s verdict continues to come from the already-recorded run
`33309565005`'s `Lint and Format Check` job. The "after every plan wave" clause's `black --check .`
and `mypy typsphinx/` halves are **not re-run and are not claimed**: neither tool reads Markdown and
the closure changes no `.py` file, which `63-05-T3` and `63-06-T1` both assert by gating on
`git status --porcelain typsphinx/` being empty.

---

## Per-Task Verification Map

Task IDs are assigned at plan time (`63-{plan}-T{task}`) and are **filled in below**. Every row's
command is runnable today — there is no Wave 0 gap. Four rows were split rather than dropped, because
the decomposition spread their surface across two tasks: REL-10's extractor surface (the run in
`63-01-T1`, the verbatim transcription and byte-identity proof in `63-01-T3`) and SC#4's local
green-tree surface (the full suite in `63-03-T1`, the format/type/version-sync gates in `63-03-T2`).
Two rows were added for surfaces the seed did not carry: D-06's `### Verified` milestone-invariant
sweep, and the external-API coverage declaration.

**The last six rows (`63-05-T1`..`63-06-T3`) were appended by the gap-closure planning run**
(2026-08-30), after `63-VERIFICATION.md` returned `gaps_found` (4/5) on **SC#2**: the extracted
release body's structural inspection passed, but a false, trivially-checkable file-confinement claim
survived it (`63-REVIEW.md` CR-01). Those six rows cover the SC#2 closure only — the correction
itself, its re-run proof, the green-tree re-proof on the corrected tree, and the three phase-close
observations re-taken against the post-correction tip. Every Automated Command below is transcribed
from the task's own `<automated>` block in `63-05-PLAN.md` / `63-06-PLAN.md`, not predicted. Rows
`63-01-T*` through `63-04-T*` describe executed work and are unchanged.

| Task ID | Plan | Wave | Requirement | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------------|-----------|-------------------|-------------|--------|
| `63-02-T1` (closeout guard, phase head) | 63-02 | 1 | REL-11 / D-16 / SC#3 — closeout guard, **phase head** | the `phase.complete` REL-09 auto-flip is detected rather than shipped | audit (checksum) | `sha256sum .planning/REQUIREMENTS.md` · `wc -l .planning/REQUIREMENTS.md` · `git rev-parse HEAD` (PHASE_BASE_SHA) · `grep -n 'REL-09' .planning/REQUIREMENTS.md` — all four recorded verbatim into `63-CLOSEOUT-GUARD.md`; gate re-compares the recorded digest and line count against live values, and asserts the guarded lines are classified state-bearing vs informational-only per Pitfall 6 | ✅ N/A — created by the task | ⬜ pending |
| `63-02-T2` (fence probe, observation 1 of 2) | 63-02 | 1 | SC#5 / D-16 — fence probe, **observation 1 of 2** | no irreversible action has occurred, and the probe provably reached its source | audit | `git tag -l 'v0.9.2'` empty · **unfiltered** `git ls-remote --tags origin` with ≥1 `v0.9.0` reference as the positive control and **0** `v0.9.2` references · `gh release list` with a `Latest` marker (positive control) and no `v0.9.2` row · `gh run list --workflow=release.yml` showing no v0.9.2 run. Precondition halts on a failed `gh auth status` or unreachable `git ls-remote --heads origin` | ✅ N/A — created by the task (`63-SC5-INVARIANTS.md`) | ⬜ pending |
| `63-02-T3` (external-API coverage declaration) | 63-02 | 1 | — (seal-time gate hygiene) | a false-positive detector run over gh-dense plan prose meets a reasoned declaration, not a fabricated capability matrix | audit | `COVERAGE.md` exists, ≥20 lines, records the plan-time detector result verbatim, names `release.yml` as recorded-but-never-triggered, and states the zero-packages fact from `63-RESEARCH.md` § "Package Legitimacy Audit" | ✅ N/A — created by the task | ⬜ pending |
| `63-01-T1` (tracer: version literal → lockfile → README → 4-step CHANGELOG → extractor stdout) | 63-01 | 1 | REL-09 (coverage only) / SC#1 — version-literal lockstep | a partial bump (the shape killing every dependabot PR) cannot reach a commit | unit + lock | `uv run pytest tests/test_extension.py::test_version_matches_pyproject_toml tests/test_readme_version_sync.py tests/test_preview_version_sync.py -v` · `uv lock --check` · `uv sync --extra dev --locked` (exit 0) · `uv run python -c` import round-trip printing `0.9.2` · `git show --name-only` on the bump commit listing `pyproject.toml`, `uv.lock`, `README.md`, `CHANGELOG.md` together (asserted in `63-01-T3`, `LC_ALL=C sort`ed) | ✅ exists | ⬜ pending |
| `63-01-T1` (same tracer, extractor half) | 63-01 | 1 | REL-10 / D-20 — extractor **executed** and its three named greps read | the published GitHub Release body cannot silently carry the scratch block | subprocess/integration | `uv run python scripts/extract_changelog_section.py 0.9.2` (exit 0, non-empty stdout) · stdout piped through `grep -c 'Planned for Future Releases'` → **0** · `grep -c '^## \[0\.9\.1\]' CHANGELOG.md` → **0** · `grep -c '^\[0\.9\.1\]:' CHANGELOG.md` → **0** · plus the structural gates that prove the relocation preceded the rename: heading count 22→23, exactly one placeholder heading, it is the FIRST `^## [` heading, the 0.9.2 heading is second, `## [0.9.0] - 2026-08-17` is third | ✅ exists (`tests/test_changelog_extraction.py` exercises the script) | ⬜ pending |
| `63-01-T2` (milestone-invariant sweep → `### Verified`) | 63-01 | 1 | REL-10 / D-06 — three `### Verified` bullets, each backed by a run | an unmeasured claim cannot enter the published release notes | audit (anchored diff) | `git rev-list --count v0.9.0..HEAD` > 0 and `git diff --stat v0.9.0..HEAD -- typsphinx/` NON-empty (the anchor's positive control) · `git diff v0.9.0..HEAD -- pyproject.toml` = exactly one added and one removed `version` line · `git diff v0.9.0..HEAD -- typsphinx/writer.py typsphinx/template_engine.py typsphinx/templates/base.typ examples/ \| grep -c '@preview'` → **0** · the 0.9.2 section carries exactly 3 `### Verified` bullets, zero `full-corpus` occurrences, ≥1 `TEST-05` | ✅ exists | ⬜ pending |
| `63-01-T3` (byte-identity + evidence consolidation) | 63-01 | 1 | REL-10 / D-20 — extractor stdout **transcribed verbatim** and proven byte-identical | a summarised or paraphrased release body is not evidence | subprocess/integration | `diff` between `scripts/extract_changelog_section.py 0.9.2` stdout and the `awk`-sliced, blank-line-trimmed 0.9.2 section body → empty, exit 0 · the **identical** pipeline against the pre-existing `## [0.6.5]` section as the POSITIVE CONTROL → also empty, exit 0 (measured exit 0 / 1299 bytes each side while planning) | ✅ exists | ⬜ pending |
| `63-01-T3` (same task, tuple half) | 63-01 | 1 | REL-10 / D-11 — `RELEASE_VERSIONS` gains `"0.9.2"` | a version string missing from the rendered page cannot pass as covered | docs build (slow, **docs-extra-gated**) | `uv run --extra dev --extra docs pytest tests/test_changelog_page_gate.py -v` — ≥6 tests **PASSED**, **zero SKIPPED** (a `--extra dev`-only run silently skips both content classes; see § "Skipped is not passed") · tuple holds 16 entries · the preceding comment reads "16 releases … 0.4.4 through 0.9.2" | ✅ exists | ⬜ pending |
| `63-03-T1` (tree identity + full pytest) | 63-03 | 2 | SC#4 — green-tree proof, executed **in this phase** | a green inherited from Phase 62's word is never recorded as this phase's, and no gate is measured against the main checkout | full-suite + import check | `uv run python -c` asserting `typsphinx.__file__` resolves inside this worktree · `uv run pytest -q` (full suite, **1543 passed / 5 skipped**, each skip's node id and reason recorded; a sixth is a finding) · PHASE_BASE_SHA read back out of `63-CLOSEOUT-GUARD.md`, `git cat-file -e`, product-tree delta = exactly the five touched files, `typsphinx/`-scoped delta empty | ✅ exists | ⬜ pending |
| `63-03-T2` (format, type and version-sync gates) | 63-03 | 2 | SC#4 — lint/type half, with the authority split recorded honestly | a skipped or unexecutable gate is never recorded as a pass | lint/type + targeted tests | `uv run black --check .` · `uv run mypy typsphinx/` · the version-sync guard trio · a local `ruff` attempt recorded additively with its literal failure, plus a `Division of authority` section naming `63-CI-EVIDENCE.md` as the `ruff` source | ✅ exists | ⬜ pending |
| `63-03-T2` (same task, docs half) | 63-03 | 2 | SC#4 / D-21 — docs builds on a **clean** baseline | an incremental rebuild cannot manufacture a false "baseline match" | docs build | `rm -rf docs/_build && uv run tox -e docs-html` (warnings vs **3**) · `rm -rf docs/_build && uv run tox -e docs-pdf` (warnings vs **5**) — the `rm -rf` is part of the command, not a preamble, and the live build output is piped through the match rather than a recorded number being read | ✅ exists | ⬜ pending |
| `63-03-T3` (3-OS CI dispatch) | 63-03 | 2 | SC#4 / D-17 / D-18 AMENDED — one 3-OS CI dispatch on the **bumped** tip | the green is observed here, never inherited; and `ruff`'s verdict comes from CI, never this host | CI | `uv sync --extra dev --locked` (pre-dispatch, D-17) → `gh workflow run ci.yml --ref <branch>` → `gh run list --workflow=ci.yml --branch <branch> --limit 1` → `gh run watch <id> --exit-status` → `gh run view <id> --json jobs`. Gate asserts `status=completed`, `conclusion=success`, `workflowName=CI`, ≥12 jobs with zero non-success, exactly 2 `windows-latest` and 2 `macos-latest` jobs, and `Lint and Format Check` = success. **`ruff`'s verdict = that job's conclusion, step `Run lint with tox` (`ci.yml:69`); see § "The lint-step name".** Plus a `<human-check>` on run recency and head-SHA identity | ✅ `.github/workflows/ci.yml` | ⬜ pending |
| `63-04-T1` (fence probe, observation 2 of 2) | 63-04 | 3 | SC#5 / D-16 — fence probe, **observation 2 of 2** | the fence held for the *whole* phase, not just at its head | audit | the same four probes with the same positive controls at a later timestamp, in a **later wave** — observation 1 in wave 1, this one in wave 3, with the bump (wave 1) and the green-tree proof and CI dispatch (wave 2) named as the intervening work · `git diff <PHASE_BASE_SHA>..HEAD -- typsphinx/` **empty**, paired with the same-anchor widened diff whose expected NON-empty result is exactly the five touched files · ≥2 distinct UTC timestamps and ≥6 `positive control` occurrences in the file | ✅ N/A — created by 63-02, extended here | ⬜ pending |
| `63-04-T2` (closeout guard re-verification) | 63-04 | 3 | REL-11 / D-16 / SC#3 — closeout guard, **phase close** | a detected flip is reverted by hand and reported, never committed | audit (checksum) | live `sha256sum` / `wc -l` / `grep -n 'REL-09'` compared line-for-line to the recorded Baseline, with the compared values shown side by side · `git diff --name-only -- .planning/REQUIREMENTS.md` empty · exactly 1 unchecked and 0 checked REL-09 bullets, 1 `Pending` Traceability row, 3 total `REL-09` occurrences · on divergence: `git checkout -- .planning/REQUIREMENTS.md` and report | ✅ N/A — created by 63-02, extended here | ⬜ pending |
| _(operator, outside any plan)_ | — | post-phase | REL-11 / D-16 / SC#3 — **third observation, after `phase.complete`-family tooling** | the flip that historically lands *after* the last plan is caught | audit (checksum) | the same three commands re-run once more after `phase.complete` has run — recorded in `63-CLOSEOUT-GUARD.md`'s "For the operator running phase.complete" section, authored by `63-02-T1`, confirmed reachable by `63-04-T2` and pointed at by name from `63-HANDOFF.md` (`63-04-T3`). **This is the observation that actually catches the flip, because it runs outside any plan's reach.** | ✅ N/A — created by `63-02-T1` | ⬜ pending |
| `63-04-T3` (handoff) | 63-04 | 3 | SC#5 / D-13 / D-14 / D-15 — the standalone handoff | the handoff cannot be read as authorising a publish, and cannot omit a step | audit | `63-HANDOFF.md` opens by stating the POSITIVE (this milestone **does** publish) · the `v0.9.2` tag push, the `pypi` Environment approval named as an **expected** gate at a LOWER line number than the tag-push command, the Release body's byte-identity to the extractor's stdout, the `update-pin.yml` **manual dispatch** plus that repository's own separate tag, and the RTD `en`/`ja` (`typsphinx-ja`) `stable` checks all present · D-14's four REL-04 items present including the todo filename · REL-09 quoted verbatim as an unchecked blockquote · plus a `<human-check>` reading it cold against SC#5's five steps for polarity and standalone-ness | ✅ N/A — created by the task | ⬜ pending |
| `63-05-T1` (tracer: two CHANGELOG edits → measured scope proof → extractor stdout read) | 63-05 | 4 | REL-09 / REL-10 / SC#2 / CR-01 / D-23 — the false blanket claim deleted, a measured narrower one re-scoped into the IMG-08 bullet | a checkable false claim about a release's blast radius cannot reach the published GitHub Release body or the RTD changelog page | subprocess/integration + anchored diff | newline-normalised whole-file `grep -c 'The runtime changes are confined to'` → **0**, with the **pre-edit count of 1 recorded as its own control** (a zero-count gate whose pre-state was never measured proves nothing) · intro-region `awk` slice `grep -c 'confined to'` → **0** · IMG-08 bullet-region slice `grep -c 'confined to \`typsphinx/translator.py\`'` → **1** · section still carries `0.9.0 users should upgrade to this release` (1) and `Windows-exclusive fix` (1) · **9** em dashes · no line > 99 columns · `grep -c '^## \['` → **23** · all three `0.9.1` greps → **0** · `git diff --name-only e3399825..dd385436 -- typsphinx/` = exactly `typsphinx/translator.py` · `uv run python scripts/extract_changelog_section.py 0.9.2` non-empty, `grep -c 'Planned for Future Releases'` → **0** · `diff` vs the `awk`-sliced section → empty, with the **identical `## [0.6.5]` pipeline as the POSITIVE CONTROL** · `tail -1` = the `v0.9.2...HEAD` compare link · `git status --porcelain typsphinx/ .planning/REQUIREMENTS.md` empty. Precondition halts unless `e3399825`, `dd385436` and `v0.9.0` all resolve — a shallow clone would make every diff vacuously empty | ✅ exists (`CHANGELOG.md`; `tests/test_changelog_extraction.py` exercises the extractor) | ⬜ pending |
| `63-05-T2` (post-correction evidence, contradiction annotated resolved) | 63-05 | 4 | REL-10 / D-20 / SC#2 — the corrected body transcribed verbatim and the file's own contradiction closed | the record of what was inspected, when, and what it missed survives the correction — append-only, never rewritten | audit | all four pre-existing sections still present (`Milestone-invariant sweep`, `Byte-for-byte identity`, `The extracted body, verbatim`) · a new `Post-correction` section with ≥1 UTC timestamp · the replacement claim's proof transcribed: `e3399825`, `dd385436`, `8430ca62`, `1adad07f`, and `756b9fad` (the commit explaining why the milestone-wide `translator.py` figure exceeds the phase-62 one) all cited · size labelled in `bytes` · the extractor **re-run at gate time** and its live byte count required to appear in the file (so no pre-correction figure can be carried forward) · `63-01-PLAN.md`..`63-04-PLAN.md` untouched by the commit · no near-miss reserved-name file | ✅ N/A — extends `63-CHANGELOG-EVIDENCE.md`, created by `63-01-T3` | ⬜ pending |
| `63-05-T3` (green-tree re-proof, CI-dispatch decision, D-24 declination) | 63-05 | 4 | SC#4 / D-21 / D-18 AMENDED / D-24 — the corrected tree proven green on runs executed **in this closure** | a docs-extra skip cannot pass as a proof, and a CI dispatch is neither taken reflexively nor skipped silently | full-suite + docs build + audit | `63-GAP-CLOSURE-EVIDENCE.md` exists with ≥1 UTC timestamp · records an `extra docs` invocation and a `SKIPPED`/`skipped` count (read, not inferred from exit code) · `rm -rf docs/_build` appears **≥2** times, once before each of `docs-html` and `docs-pdf`, warnings compared to the **3 / 5** baseline · `Lint and Format Check` named and `grep -c 'Run linters'` → **0** · CI run `33309565005` cited as the standing lint authority · `IN-01`, `COVERAGE.md` and `myst_parser` all recorded · `tests/test_changelog_page_gate.py` unmodified (D-24) and its milestone-wide change count still 1 · plus a live `uv run --extra dev --extra docs pytest` over the changelog page gate, the extractor contract tests and the version-sync guard trio | ✅ N/A — creates `63-GAP-CLOSURE-EVIDENCE.md`; all test/build infrastructure already exists | ⬜ pending |
| `63-06-T1` (fence probe, **observation 3**, post-correction) | 63-06 | 5 | SC#5 / D-16 — fence probe, **third observation, after the correction commit** | the zero-irreversible-action claim is re-observed against the tree that now exists, never inherited from observations that pre-date it | audit | PHASE_BASE_SHA read back out of `63-CLOSEOUT-GUARD.md` and `git cat-file -e`-resolved · `typsphinx/`-scoped diff **empty**, paired with the same-anchor widened diff whose NON-empty result must still be exactly the five touched files (no sixth) · local tag probe empty with the `v0.9.0` list as control · **one** unfiltered `git ls-remote --tags origin` fetch yielding ≥1 control reference and **0** release-tag references · **one** `gh release list` fetch yielding ≥1 `Latest` marker and **0** release rows · **0** open PRs and **0** `release.yml` runs on this milestone branch · file carries all three observation headings with observation 3 strictly **after** observation 2, ≥3 distinct UTC timestamps, ≥9 `positive control` occurrences · `superseded` recorded with a cross-reference to `63-GAP-CLOSURE-EVIDENCE.md` and to run `33309565005` | ✅ N/A — extends `63-SC5-INVARIANTS.md`, created by `63-02-T2` | ⬜ pending |
| `63-06-T2` (closeout guard re-verification, **after gap closure**) | 63-06 | 5 | REL-11 / D-16 / SC#3 — closeout guard, re-run **after the gap-closure commits move HEAD** | a fence verified before the new commits says nothing about the tree after them, and moving HEAD is exactly when the flip has historically landed | audit (checksum) | live `sha256sum .planning/REQUIREMENTS.md` = the **first** 64-hex Baseline digest in the guard file · live `wc -l` present in the file · `git diff --name-only` and `git status --porcelain` over `.planning/REQUIREMENTS.md` both empty · exactly **1** unchecked and **0** checked REL-09 bullets, **1** `Pending` Traceability row, **3** total `REL-09` occurrences · both `Re-verification at phase close` and `Re-verification after gap closure` present, the new one strictly **after** the old · ≥3 distinct UTC timestamps · **the first 64-hex match still occurs above the new section**, proving no hexadecimal value was inserted above the Baseline and silently re-pointing every gate · on divergence: `git checkout -- .planning/REQUIREMENTS.md` and report | ✅ N/A — extends `63-CLOSEOUT-GUARD.md`, created by `63-02-T1` | ⬜ pending |
| `63-06-T3` (handoff brought back into accuracy) | 63-06 | 5 | SC#5 / D-13 / D-14 / D-15 — the standalone handoff, post-correction | a stale extractor size would make a correct publish look like a failure or hide a real body mismatch, and an update must not quietly drop a publish step | audit | the extractor **re-run at gate time** and its live byte count required to appear in `63-HANDOFF.md`, with the pre-correction figure required absent unless the two coincide · `63-05` and an `observation 3` citation present · every pre-existing element still present: ≥4 `REL-04` mentions, `update-pin.yml`, ≥3 `create-release`, the operator-facing guard pointer, `typsphinx-ja`, and `manual approval` at a **lower line number** than the tag-push command · **0** occurrences of the release-workflow-only lint step name · REL-09 still unchecked, no `v0.9.2` tag, `typsphinx/` and `tests/test_changelog_page_gate.py` clean | ✅ N/A — updates `63-HANDOFF.md`, created by `63-04-T3` | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

**Every plan's `SUMMARY.md` frontmatter declares `requirements-completed: []` for REL-09** (D-16).
REL-09 is cited as a coverage ID only; no plan closes it and no plan touches its checkbox.

---

## Wave 0 Requirements

**None. Existing infrastructure covers every phase requirement.** The full pytest suite, the `tox`
lint/type/docs environments, `ci.yml`'s 3-OS matrix, `scripts/extract_changelog_section.py` with its
pytest coverage (`tests/test_changelog_extraction.py`), and `tests/test_changelog_page_gate.py` are
all already in place and were exercised as recently as CI run `33302087913` (Phase 62's close) and
the local suite recorded in `62-VERIFICATION.md`.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| The `## [0.9.2]` lead paragraph reads as prose a user reads, names the 0.9.0 upgrade urgency in one sentence, and **never names 0.9.1** | REL-10 / D-01, D-02, D-08 | Prose quality and the absence of a version name are judgements, not assertions; the greps below catch only the mechanical half | `grep -c '0\.9\.1' CHANGELOG.md` → 0 inside the new section; then read the paragraph against `## [0.6.5]` (`CHANGELOG.md:381-403`), the measured structural analog |
| The three promoted `### Unreleased` bullets are **verbatim**, with the MSG bullet's apostrophe-path clause intact | REL-10 / D-04 | "Verbatim except a clause the lead paragraph makes literally redundant" is a judgement about redundancy | `git diff` the promoted region against `CHANGELOG.md:10-36` at `PHASE_BASE_SHA`; confirm the POSIX-apostrophe clause survives (the release is **not** Windows-exclusive) |
| Each `### Verified` bullet is backed by a run recorded in **this** phase's or Phase 62's evidence | REL-10 / D-06 | Provenance of a claim cannot be asserted by a test | For each of the three bullets, name the evidence file and line it rests on. **Do not copy prior entries' "full-corpus `-b typstpdf` re-run remains fatal-free" sentence** — this phase does not run that corpus (D-06's explicit warning) |
| `63-HANDOFF.md` is standalone — an operator who reads only it can execute `/gsd-complete-milestone` | SC#5 / D-13 | Standalone-ness is a reading test | Read it cold against SC#5's five enumerated steps; every one present, in the operator's own execution order |

---

## Skipped is not passed

Two failure modes in this phase record a **skip** as if it were a pass:

1. **`tests/test_changelog_page_gate.py` under a `--extra dev`-only sync.** `myst_parser` is in the
   `docs` extra only; both content-coverage classes are guarded on importing it, so they SKIP
   silently. A green worktree `pytest` **does not prove D-11**. The proof must come from a
   `--extra dev --extra docs` run, or from the dispatched CI run, and the plan must say which. Assert
   on **`PASSED` counts with zero `SKIPPED`**, not on exit code.
2. **`ruff` on this host.** It is an unrunnable generic-linux ELF in a freshly provisioned worktree
   venv. A `black`+`mypy` green is **not** "lint clean". `ruff`'s verdict comes from CI (below) —
   never from a local attempt, and never from silence.

The 5-skip full-suite baseline is itemised above precisely so that a *sixth* skip is visible as a
finding rather than absorbed into "5 skipped, as expected".

---

## The lint-step name (D-18 AMENDED)

`ci.yml` carries **no** step named `Run linters`. Measured 2026-08-30 with
`grep -rn 'Run linters' .github/`: exactly one hit, `.github/workflows/release.yml:84` — the
workflow this prep-only phase must **never** trigger. `ci.yml`'s `lint` job (`ci.yml:51-70`, display
name **`Lint and Format Check`**) has one substantive step, **`Run lint with tox`** (`ci.yml:69`),
running `uv run tox -e lint` → `tox.ini`'s `[testenv:lint]` → `black --check .` then `ruff check .`.

Read `ruff`'s verdict as the `Lint and Format Check` job's conclusion in
`gh run view <id> --json jobs`, and quote the `Run lint with tox` step's own `ruff check .` output
verbatim in `63-CI-EVIDENCE.md`. See `63-CONTEXT.md` § Amendments item 1 — this is the third
recurrence of the wrong name and the first fixed at the source.

---

## Evidence-file naming constraint (D-19)

`{padded_phase}-VERIFICATION.md` is `gsd-verifier`'s **reserved output name**; a plan-authored file
there is clobbered at verify time. **No plan may write `63-VERIFICATION.md`.** The permitted set,
mirroring Phase 61's: `63-CLOSEOUT-GUARD.md`, `63-CHANGELOG-EVIDENCE.md`,
`63-GREEN-TREE-EVIDENCE.md`, `63-CI-EVIDENCE.md`, `63-SC5-INVARIANTS.md`, `63-HANDOFF.md`.

**Gap-closure addition (2026-08-30).** The set above is the *plan-authored* evidence set as of the
phase's original close. The gap closure adds one more permitted file,
**`63-GAP-CLOSURE-EVIDENCE.md`**, following the same `{padded_phase}-{TOPIC}-EVIDENCE.md`
convention; the ban on the reserved name is unchanged and unweakened. Note also that `gsd-verifier`
has since **legitimately written `63-VERIFICATION.md`** for this phase — which is exactly why the two
gap-closure plans gate on the absence of the near-miss name `63-VERIFICATION-GAP.md` rather than
reusing `63-02`/`63-04`'s now-unsatisfiable `[ ! -f … 63-VERIFICATION.md ]` assertion.

---

## `uv lock` sequencing constraint (D-17)

`uv lock` runs and is **committed before** the CI dispatch. Every CI job begins with
`uv sync --extra dev --locked`; `uv.lock:1467` currently reads `version = "0.9.0"` for the
self-package, independently of `pyproject.toml:7`. Dispatching before regenerating reproduces the
exact refusal already killing every dependabot PR, and it fails at the *install* step — before any
test, lint or type signal exists. `uv.lock` is regenerated with `uv lock` and **never hand-edited**.

---

## Validation Sign-Off

Checked items are properties of the **six** authored plans, verified at plan time against
`63-01-PLAN.md` through `63-06-PLAN.md` — the four original plans plus the two gap-closure plans
(`63-05`, `63-06`) added after `63-VERIFICATION.md` returned `gaps_found` (4/5) on SC#2. The
unchecked item is `/gsd-validate-phase`'s to set.

- [x] All tasks have `<automated>` verify or a recorded-observation audit with a stated positive control — **18/18** tasks across the six plans carry `<automated>`; the four audit tasks that pair every negative probe with a control derived from the same fetch are `63-02-T2`, `63-04-T1`, `63-04-T3` and `63-06-T1`, and `63-05-T1` carries two controls of its own — the `## [0.6.5]` byte-identity pipeline, and the **pre-edit count of 1** recorded for its own zero-count gate so a post-edit 0 cannot be a vacuous match
- [x] Sampling continuity: no 3 consecutive tasks without automated verify — every task has one
- [x] Wave 0 covers all MISSING references — *(none; existing infrastructure suffices)*
- [x] No watch-mode flags — `gh run watch --exit-status` is a one-shot wait-for-completion, not a watch loop
- [x] Feedback latency < 10 min (local suite minutes; CI dispatch ≈ 7 min)
- [x] D-11's proof recorded from a `--extra docs` run or from CI — never from a `--extra dev`-only skip — `63-01-T3` runs `uv run --extra dev --extra docs pytest tests/test_changelog_page_gate.py -v` and gates on **zero** skipped; `63-05-T3` re-runs the same gate under the same extra on the corrected tree and records the skipped count rather than reading the exit code
- [x] `ruff` verdict recorded from `ci.yml`'s `Lint and Format Check` job, not from this host — `63-03-T3` gates on that job's conclusion; `63-03-T2` records the local attempt additively under a `Division of authority` heading; `63-05-T3` re-reads the verdict from that same recorded run and gates on **zero** occurrences of the release-workflow-only step name; the release workflow's own differently-named lint step appears in no plan body
- [x] The SC#5 fence observations sit in **different waves** — `63-02-T2` in wave 1, `63-04-T1` in wave 3, and `63-06-T1` in wave 5, separated by wave 2's green-tree proof and CI dispatch and by wave 4's correction commit. The third was added by the gap closure because observations 1 and 2 **both pre-date that commit** and therefore say nothing about the tree that now exists; SC#5's two-observation minimum was already met by the first pair, so this is an addition, not a renumbering
- [x] No plan writes `63-VERIFICATION.md` — all **six** plans forbid it by name. Two of the original four (`63-02`, `63-04`) additionally gated on the file's absence with `[ ! -f … ]`; that assertion is **no longer available**, because `gsd-verifier` has since legitimately written `63-VERIFICATION.md` for this phase. The two gap-closure plans therefore gate on the absence of the **near-miss name** `63-VERIFICATION-GAP.md` and route their own evidence to `63-GAP-CLOSURE-EVIDENCE.md`
- [x] Every plan declares `requirements-completed: []` for REL-09 — all **six** plans, in plan frontmatter and again as an instruction in each plan's `<output>` block for the generated `SUMMARY.md`
- [ ] `nyquist_compliant: true` set in frontmatter — set by `/gsd-validate-phase`, not at plan time

**Approval:** pending (`status: draft` until `/gsd-validate-phase` runs)
