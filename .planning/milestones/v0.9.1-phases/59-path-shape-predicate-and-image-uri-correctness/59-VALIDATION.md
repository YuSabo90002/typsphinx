---
phase: 59
slug: path-shape-predicate-and-image-uri-correctness
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-29
---

# Phase 59 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
>
> Seeded by plan-phase from `59-RESEARCH.md` § "Validation Architecture". This is a **product-side
> phase gated RED-first**: every one of the five requirements ships with a gate that is recorded
> failing against the unfixed tree before the fix lands (ROADMAP constraint 1). A green run that was
> never first recorded RED is evidence of nothing here.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.1 (`pyproject.toml:35` pins `>=8.4,<10`) |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]` (`pyproject.toml:79-99`) — `testpaths = ["tests"]`, `addopts = "-v --strict-markers"`, `filterwarnings` escalates `DeprecationWarning`/`PendingDeprecationWarning` to `error` |
| **Quick run command** | `uv run pytest tests/test_path_shape_predicate_gate.py tests/test_track_image_key_construction.py -q` *(planner-named files; substitute the actual names once chosen — naming is Claude's Discretion per CONTEXT.md)* |
| **Full suite command** | `uv run pytest` |
| **Estimated runtime** | quick ~15s · full suite ~3–5 min (carried from Phase 58's recorded figure for this same suite; this phase adds 4 new modules, two of which run `sphinx-build` subprocesses) |

**Worktree note (CLAUDE.md § "Worktree-isolated execution", mandatory):** every command above runs
only after `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` in the executor's own
worktree, and every command is prefixed `uv run`. `typst` is a **core** dependency
(`pyproject.toml:29`), so a correctly-provisioned worktree venv has `TYPST_AVAILABLE` true — a
`skipped` line on the IMG-07 compile gate means the venv is wrong, **not** a pass (CONTEXT.md
§ Specific Ideas #4; Phase 58 recorded the same trap).

---

## Sampling Rate

- **After every task commit:** the specific requirement's quick command below, scoped to the file(s)
  that task touched.
- **After every plan wave:** `uv run pytest` (full suite). This phase edits `builder.py` and
  `translator.py` within the same milestone, and ROADMAP constraint 4 forbids a plan changing an
  emitted string from sharing a wave with a plan asserting on it; a full-suite run at each merge
  boundary is the cheapest way to confirm no cross-wave collision.
- **Before `/gsd-verify-work`:** full suite green, `uv run black --check .` clean, and
  `uv run mypy typsphinx/` clean (both product files are in scope). `ruff check .` is **deferred to
  CI** — it is not runnable on this NixOS dev machine, and CI is the lint authority.
- **Phase gate ordering (binding constraint 10):** local RED→green must be complete **before** the
  first `windows-latest` CI dispatch. CI is final confirmation, never first discovery.
- **Max feedback latency:** ~15 seconds (quick run).

---

## Per-Task Verification Map

Task IDs are assigned by the planner; the rows below are the requirement→verification contract each
task must map onto.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD | TBD | 1 | PATH-01 | T-59-01 (V12 outdir containment) | `_escapes_outdir()` called **directly** returns `True` for `\manuals\guide` and `\\srv\share\g`; pre-fix `False` recorded RED first (D-09, ROADMAP constraint 8 — never through a call site) | unit | `uv run pytest tests/test_path_shape_predicate_gate.py -k escapes_outdir_direct -x` | ❌ W0 — new file | ⬜ pending |
| TBD | TBD | 1 | PATH-01 | T-59-01 | Both production call sites (`_resolve_target_stem()`, `_track_image()`) classify every tested shape byte-identically before and after — the characterization pin runs **through** the call sites (D-10, the opposite of the gate above) | unit (parametrized) | `uv run pytest tests/test_path_shape_predicate_gate.py -k characterization -x` | ❌ W0 — new file | ⬜ pending |
| TBD | TBD | 1 | IMG-04 | T-59-03 (Typst literal validity) | `_track_image()`'s escape-branch key contains no raw `\` for a Windows-shaped `resolved_uri`; RED-first against the unfixed `path.basename()` call | unit | `uv run pytest tests/test_track_image_key_construction.py -k no_backslash -x` | ❌ W0 — new file | ⬜ pending |
| TBD | TBD | 1 | IMG-06 | T-59-02 (ENAMETOOLONG DoS) | Relocation-key final component ≤ 255 UTF-8 bytes, `{sha1[:8]}-` digest intact, extension preserved, truncation on a UTF-8 boundary, stem never empty; collision re-proven for two long URIs sharing a basename (D-06/D-07/D-08(a), pure-string, all lanes) | unit | `uv run pytest tests/test_track_image_key_construction.py -k length_bound -x` | ❌ W0 — new file | ⬜ pending |
| TBD | TBD | 1 | IMG-06 | T-59-02 | Pre-fix `Failed to copy image …: [Errno 36] File name too long` captured with **`caplog`** (a `logging` call, not `warnings.warn()` — RESEARCH Pitfall 4) **and** the absent destination file; both gone post-fix (D-08(b)) | integration | `uv run pytest tests/test_copy_image_files_name_too_long.py -x` | ❌ W0 — new file | ⬜ pending |
| TBD | TBD | 1 | IMG-05 | T-59-03 | `visit_image()`'s emitted `image("...")` literal carries no raw backslash and shows `"` in escaped form for a Windows-shaped absolute URI, via a `-b typst` build — D-04's all-lane sibling, so `windows-latest` is not left uncovered by D-03's skip | integration (`sphinx-build -b typst`) | `uv run pytest tests/test_windows_image_uri_render_gate.py -k string_shape -x` | ❌ W0 — new file | ⬜ pending |
| TBD | TBD | 2 | IMG-07 | T-59-03 | A real `typst.compile()` succeeds for D-01's four-combination fixture (raw basename `sub\we"ird.png`, normalized `we"ird.png`); RED pre-fix with `path must not contain a backslash` quoted **verbatim**; skips via D-03's runtime `tmp_path` probe inside the test body, never `os.name` and never a collection-time `skipif` (RESEARCH Pitfall 1) | integration (`sphinx-build -b typstpdf`, `TYPST_AVAILABLE`-guarded) | `uv run pytest tests/test_windows_image_uri_render_gate.py -k compile -x` | ❌ W0 — new file | ⬜ pending |
| TBD | TBD | final | SC#5 | — | Zero existing test assertions modified over the phase diff (measured against `58-REPR-CENSUS.md`, not claimed) **and** a fresh 3-OS CI dispatch green on this phase's own post-fix tip | CLI + CI | `git diff --stat <phase-base>..HEAD -- tests/` shows additions only; then a fresh `gh workflow run` on the post-fix tip | ✅ tooling exists; the dispatch is a one-time recorded action | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_path_shape_predicate_gate.py` — PATH-01's direct-call RED gate (D-09) + the
      through-call-site characterization pin (D-10)
- [ ] `tests/test_track_image_key_construction.py` — IMG-04's no-backslash gate + IMG-06(a)'s
      pure-string length-bound gate (neither needs a filesystem)
- [ ] `tests/test_windows_image_uri_render_gate.py` — IMG-05/D-04's POSIX string-shape sibling +
      IMG-07/D-01..D-03's real-compile gate
- [ ] `tests/fixtures/<name>/` — the new fixture project for the compile gate, modelled on
      `tests/fixtures/absolute_image_render_gate/`; its `conf.py` post-transform rewrites
      `node["uri"]` to a **genuinely existing** file whose raw basename is `sub\we"ird.png`
      (CONTEXT.md § Specific Ideas #3 — a missing source makes a red indistinguishable from a
      fixture bug)
- [ ] `tests/test_copy_image_files_name_too_long.py` — IMG-06(b)'s integration gate for the
      swallowed `OSError`
- [ ] `59-WINDOWS-URI-EVIDENCE.md` — the recorded two-tree PATH-01 measurement (D-09's "before and
      after" half) and IMG-07's verbatim `TypstError` RED quote. **Not** `59-VERIFICATION.md`, which
      `gsd-verifier` reserves and overwrites wholesale (D-11)
- [ ] No framework install needed — `pytest`, `hashlib`, `posixpath`, `ntpath`, `os` are all
      already present; `typst`/`typst-py` is a core pin and was confirmed importable this session

*File names above are the RESEARCH.md seeds; final naming is Claude's Discretion per CONTEXT.md.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| The two-tree PATH-01 "byte-identical before and after" comparison (D-09) | PATH-01 / SC#1 | A test in the suite can only ever pin the tree it runs on. "Identical before **and** after" is inherently a two-tree comparison and cannot be a permanent automated assertion. | Run the full shape table through both production call sites against the **pre-fix** tree, record the output verbatim in `59-WINDOWS-URI-EVIDENCE.md`; apply the fix; re-run; record the second output; show the two byte-identical. Same shape as `57-11` and Phase 58 D-05(b). |
| Every RED-first recording (ROADMAP constraint 1) | PATH-01, IMG-04, IMG-05, IMG-06, IMG-07 | The RED must be captured against the unfixed tree, so it cannot be re-derived after the fix lands. | Before applying each product change, run that requirement's gate command and paste the verbatim failure into `59-WINDOWS-URI-EVIDENCE.md`. For IMG-07 the evidence must quote Typst's own `path must not contain a backslash` text, not a paraphrase (SC#2). For IMG-06(b) it must quote the `[Errno 36] File name too long` warning line. Confirm zero `skipped` — a skip is not a RED and not a green. |
| Fresh 3-OS CI dispatch on the post-fix tip (SC#5) | — | A remote-state side effect; not observable from the local suite. Constraint 10 forbids inferring it from a prior run. | After local RED→green is complete and pushed, dispatch CI fresh against this phase's own tip and record the run URL plus the `windows-latest` job result in `59-WINDOWS-URI-EVIDENCE.md`. |
| Zero-test-edit proof (SC#5) | — | The claim is about a diff, not a runtime behavior; it is measured against `58-REPR-CENSUS.md`, not asserted by a test. | `git diff --stat <phase-base>..HEAD -- tests/` must show new files only, with no modified-line count on any pre-existing test module. A plan finding it *must* edit a test is a signal the census was incomplete — halt, do not edit (ROADMAP constraint 9). |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
