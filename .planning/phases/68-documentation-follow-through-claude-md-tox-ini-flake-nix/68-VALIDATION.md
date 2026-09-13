---
phase: "68"
slug: "documentation-follow-through-claude-md-tox-ini-flake-nix"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-09-12"
---

# Phase 68 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Source: `68-RESEARCH.md` § Validation Architecture. This phase changes prose only — `CLAUDE.md`,
> the `tox.ini` `requires` comment block, `flake.nix` `#` comments, and docstring / assertion-message
> text in two test files — and adds no test file (Phase 64–67 convention). Prose *quality* has no
> automated oracle; what is mechanically checkable is (a) the stale-string regression (`git grep`),
> (b) the `requires` value staying structurally unchanged (`tox config`), (c) the devShell derivation
> staying byte-identical across a comment-only `flake.nix` edit (`nix eval` drvPath ×4), and (d) the
> test suite's collected count and the two edited test files' pass counts staying identical.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.1 (`uv.lock`-pinned), plus `git grep`, `tox config`, `nix eval` as evidence probes |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]` (unedited by this phase) |
| **Quick run command** | `uv run pytest tests/test_toolchain_config_gate.py tests/test_pdf_render_gate.py -q` |
| **Full suite command** | `uv run pytest --collect-only -q` (count gate, same worktree before/after) and `uv run pytest -q` |
| **Estimated runtime** | quick ~10 s; `nix eval` ×4 ~1.6 s; full suite several minutes |

---

## Sampling Rate

- **After every task commit:** the plan-scoped probe for the file(s) that plan owns — `git grep -n tox-uv-bare` scoped to that file; `tox config -e py312 --core -k requires` for the `tox.ini` plan; the four-system drvPath equality for the `flake.nix` plan; the quick run command for the test-file plan
- **After every plan wave:** wave 2 re-runs `git grep -n tox-uv-bare -- ':!.planning' ':!uv.lock'` against the merged tree and classifies every hit (D-15), plus the green-tree gate
- **Before `/gsd-verify-work`:** the wave-2 evidence file is complete and every row in its "rationale presented as current" class is absent
- **Max feedback latency:** ~10 seconds for every per-task probe

---

## Per-Task Verification Map

Seeded from `68-RESEARCH.md` § Phase Requirements → Test Map. Task IDs are filled in when plans are
created. Comparisons of pytest counts are same-worktree before/after only (D-06: a worktree's
`.venv` may run a different interpreter than the main checkout).

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 68-01-01 | 01 | 1 | DOC-19 | T-68-01, T-68-02 | recipe tail byte-identical; only old lines 11 and 77 removed | grep-gate + byte fence | line 11 exact; one `tox-uv~=1.35` Conventions bullet carrying its tokens; recipe-tail `sha256sum` equal to `BASE_68_01`; D-02 `git log -S` ×2 and `git grep` at base all 0 (68-01 Task 1 `<automated>`) | ✅ | ⬜ pending |
| 68-01-02 | 01 | 1 | DOC-19 | T-68-01 | NixOS subsection and boundary paragraph additive; recipe unchanged | region tokens + byte fence | heading order Conventions → CI bullet → `### NixOS development shell` → `### Worktree-isolated execution`; subsection and boundary token sets; no digit-dot-digit in the subsection; recipe-tail hash; collected count equal to before (68-01 Task 2) | ✅ | ⬜ pending |
| 68-02-01 | 02 | 1 | DOC-20 | T-68-04, T-68-06 | `requires` value unchanged | structural + byte fence | `uv run tox config -e py312 --core -k requires` prints `tox-uv~=1.35`; `requires`-to-EOF and lines 1-3 hash equal to base; block all `#` lines with its tokens; `SPECIFIER_EQUIV = True` (68-02 Task 1) | ✅ | ⬜ pending |
| 68-02-02 | 02 | 1 | DOC-20, DOC-19 | T-68-05 | assertion logic unchanged | masked-AST hash + pytest | AST hash with docstrings/assert messages masked equal to base; stale self-references absent from the function's strings; two-file result equal to `TWO_FILE_RESULT_BEFORE`; black/ruff (68-02 Task 2) | ✅ | ⬜ pending |
| 68-02-03 | 02 | 1 | DOC-20 | T-68-05 | assertion logic unchanged | masked-AST hash + docstring order + pytest | masked-AST hash for both test files; QUA-04 sentence → revert/FHS sentence → "kept regardless" order; two-file result and collected count equal to before; black/ruff (68-02 Task 3) | ✅ | ⬜ pending |
| 68-03-01 | 03 | 1 | DOC-21 | T-68-07, T-68-09 | derivation unchanged | derivation-identity | four `nix eval --raw .#devShells.<sys>.default.drvPath` equal to `DRV_BEFORE_*`; comment-stripped hash equal to base; comment-only diff; uvShim note tokens, no version/ID (68-03 Task 1) | ✅ | ⬜ pending |
| 68-03-02 | 03 | 1 | DOC-21 | T-68-07, T-68-08 | derivation unchanged; darwin stated unverified | derivation-identity + grep | drvPaths ×4 and `nix flake check --all-systems --no-build`; `grep -nE 'D-[0-9]' flake.nix` empty; archive-stable citations; header and per-element tokens; collected count equal (68-03 Task 2) | ✅ | ⬜ pending |
| 68-04-01 | 04 | 2 | DOC-20 | T-68-10, T-68-11 | classification measured, not copied | evidence-assertion | live D-15 grep with one table row per hit and `C3_ROWS = 0`; file-scoped stale-sentence negatives; `tox config` read-back (68-04 Task 1) | ✅ | ⬜ pending |
| 68-04-02 | 04 | 2 | DOC-19, DOC-21 | T-68-10 | SC#1 literal and amended readings kept separate | evidence-assertion + derivation-identity | recipe tail vs `PHASE_BASE`; `ln -sf`/`patchelf` only inside the NixOS subsection; merged-tree drvPaths ×4 equal to `DRV_BEFORE_*`; the seven shim names begin CLAUDE.md § Commands lines (68-04 Task 2) | ✅ | ⬜ pending |
| 68-04-03 | 04 | 2 | DOC-19, DOC-20, DOC-21 | T-68-11, T-68-12 | no out-of-scope change | full suite + lint + scope fence | `FULL_FAILED = 0`; `uv run black --check .`; `uv run ruff check .`; `git diff --quiet PHASE_BASE HEAD -- typsphinx .github pyproject.toml uv.lock CHANGELOG.md`; exactly the five edit targets changed outside `.planning/` (68-04 Task 3) | ✅ | ⬜ pending |

**Correction to the seeded rows (planner, 2026-09-13).** The seeded DOC-19/DOC-20 rows gated on
"`git grep -n tox-uv-bare -- <file>` prints nothing". That can never hold: D-08 and D-16 require
`CLAUDE.md` and `tox.ini` to keep `tox-uv-bare` as one sentence of history. The per-file gate is
therefore the absence of the six specific sentences RESEARCH classed as "rationale presented as
current", plus the byte fences above; 68-04's D-15 classification is where every surviving hit is
judged.

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements. No new test file or fixture is needed; the
only new files are phase evidence markdown (`68-*-EVIDENCE.md`, never `68-VERIFICATION.md`).

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| New CLAUDE.md / `tox.ini` / `flake.nix` prose states each mandated fact (D-01..D-16) accurately | DOC-19, DOC-20, DOC-21 | No automated oracle for prose content | Verifier reads each edited block against the decision list and the Phase 64/65 evidence quoted in `68-RESEARCH.md` § Measured Facts; SC#1 literal and amended readings reported separately |
| Darwin behaviour of the per-system guard | DOC-21 | No darwin machine and no CI lane evaluates `flake.nix` (constraint 8) | Not verifiable — the note's job is to say so; only `nix eval` on a Linux evaluator is checked |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s for per-task probes
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
