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
| TBD | TBD | 1 | DOC-19 | — | N/A | grep-gate | `git grep -n tox-uv-bare -- CLAUDE.md` prints nothing; provisioning line byte-identical | ✅ | ⬜ pending |
| TBD | TBD | 1 | DOC-20 | — | N/A | grep-gate + structural | `git grep -n tox-uv-bare -- tox.ini` prints nothing; `tox config -e py312 --core -k requires` prints `tox-uv~=1.35` | ✅ | ⬜ pending |
| TBD | TBD | 1 | DOC-21 | — | N/A | derivation-identity + grep | four `nix eval --raw .#devShells.{system}.default.drvPath` byte-identical before/after; `grep -n 'D-[0-9]' flake.nix` prints nothing | ✅ | ⬜ pending |
| TBD | TBD | 2 | DOC-19, DOC-20, DOC-21 | — | N/A | evidence-assertion | repository-wide D-15 grep on the merged tree with zero "rationale presented as current" rows; collected count unchanged | ❌ W0 → `68-*-EVIDENCE.md` | ⬜ pending |

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
