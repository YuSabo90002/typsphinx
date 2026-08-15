---
phase: 53
slug: template-registry-foundation
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-15
---

# Phase 53 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Seeded by `/gsd-plan-phase` from `53-RESEARCH.md` § Validation Architecture.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (config in `pyproject.toml` `[tool.pytest.ini_options]`), `tox` (with `tox-uv-bare`) as task runner |
| **Config file** | `pyproject.toml`, `tox.ini` |
| **Quick run command** | `uv run pytest tests/test_template_registry.py tests/test_template_engine.py -v` (registry module name is the planner's choice — CONTEXT § Claude's Discretion) |
| **Full suite command** | `uv run pytest tests/ -v` (local spot-check) — the **matrix / lint / type authority is the dispatched CI run**, not the local suite |
| **Estimated runtime** | quick ~5–10s; full local suite ~3–5 min |

**Worktree note (CLAUDE.md, mandatory):** every executor runs
`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` first, then invokes **all** commands
through `uv run`. Without this, pytest imports the unchanged main-tree package and gates stay RED after a
correct fix.

**Lint caveat:** `ruff` cannot execute on this machine (generic-linux ELF, NixOS —
`todos/pending/2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos.md`). Lint evidence comes from the
dispatched CI run only; never report a local suite pass as lint coverage.

---

## Sampling Rate

- **After every task commit:** the new registry-module test file alone (seconds).
- **After every plan wave:** `uv run pytest tests/ -v` locally, confirming the **32** files that assert
  the root `_template.typ` stay green **unmodified** (`grep -rl "_template\.typ" tests/ | wc -l` → 32,
  measured 2026-08-15; re-run the grep rather than hardcoding the number). A spot-check only — not
  authoritative for lint/type/matrix.
- **Before `/gsd-verify-work`:** dispatched CI run (`gh workflow run CI --ref
  gsd/v0.9.0-per-document-templates`) all-green across all 6 matrix legs, **including `windows-latest`
  and `macos-latest`** (SC#5's own requirement). `53-RED-EVIDENCE.md` must also be complete and
  committed — it is evidence, not a gate, but SC#2 has no other acceptance mechanism (D-12).
- **Max feedback latency:** ~10s for the registry test subset.

---

## Phase Requirements → Test Map

| Req ID | SC | Behavior | Test Type | Automated Command | File Exists |
|--------|----|----------|-----------|-------------------|-------------|
| TPL-01 | SC#1 | Named definitions accepted; `template` **xor** `package`; optional `template_function` in both its `str` and `{"name","params"}` forms | unit | new `tests/test_template_registry.py` | ❌ Wave 0 |
| TPL-05 | SC#1 | Two `typst_documents` entries naming the **same** key resolve to the one definition; `params`-exclusivity rule intact, no new predicate | unit | new `tests/test_template_registry.py::test_shared_key_resolves_once` | ❌ Wave 0 |
| TPL-03 | SC#2 | `"typst"` key synthesizes the existing global config; byte-identical output | e2e / evidence | `53-RED-EVIDENCE.md` procedure (RESEARCH Q6) — a one-off measurement, **not** a pytest gate (D-12); also covered structurally by the existing 32-file regression net staying green unmodified | ✅ existing net; ❌ evidence artifact |
| TPL-04 | SC#2 | Four-element `typst_documents` tuple produces output byte-identical to the same tuple with a fifth element of `"typst"` | unit + e2e | new unit test + RESEARCH Q6's comparison step | ❌ Wave 0 |
| CONF-14 | SC#3 | Unregistered key (and a present-but-non-`str` element [4], D-06) raises `ExtensionError` naming the registered keys | unit | new test asserting the message contains the sorted registered keys | ❌ Wave 0 |
| CONF-15 | SC#3 | A definition carrying both `template` and `package` raises | unit | new test | ❌ Wave 0 |
| CONF-16 | SC#3 | A user-defined `"typst"` key raises (literal string only — `"Typst"`/`"TYPST"` pass, D-04) | unit | new test | ❌ Wave 0 |
| CONF-17 | SC#3 | Path arithmetic (D-07/D-09): rejects when the resolved parent **is `srcdir`** or **an ancestor of `srcdir`**; siblings and absolute-outside paths stay legal; independent of file existence | unit | new test, one case per shape | ❌ Wave 0 |
| CONF-18 | SC#4 | The **exactly seven** denylist cases (D-02), each a platform-independent string-shape assertion that passes on Linux; the case-collision case routed through `_collision_key()`'s casefold, not a second folding | unit (parametrized) | new test | ❌ Wave 0 |
| — | SC#3 | Every malformed registry fires **once per build, order-independently** — a multi-master config with a bad entry fails identically regardless of write order | unit | new test with ≥2 masters and one bad entry, asserting a single accumulated raise | ❌ Wave 0 |
| — | SC#5 | Branch on `origin` + completed 3-OS CI run | manual + script | `git ls-remote --heads origin` + `gh run view <id> --json jobs` | ✅ (workflow exists) |

---

## Per-Task Verification Map

*Filled by `/gsd-validate-phase` once PLAN.md task IDs exist. Seeded rows below carry the plan-level
mapping the planner must preserve.*

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD | RED evidence | 1 | TPL-03, TPL-04 (SC#2) | — | N/A | e2e | RESEARCH Q6 procedure, recorded pre-change | ✅ fixtures | ⬜ pending |
| TBD | config registration | 1 | TPL-01 | — | N/A | unit | new registry test | ❌ W0 | ⬜ pending |
| TBD | registry resolver | 1–2 | TPL-01, TPL-05 | — | N/A | unit | new registry test | ❌ W0 | ⬜ pending |
| TBD | key-shape validation | 1–2 | CONF-18 | T-53-01 | key shape rejected **before** any value derived from it reaches a filesystem call | unit | parametrized denylist test | ❌ W0 | ⬜ pending |
| TBD | definition validation | 1–2 | CONF-14, CONF-15, CONF-16, CONF-17 | T-53-02 | CONF-17 rejects `srcdir`-or-ancestor parents before Phase 54's copy site exists | unit | new tests | ❌ W0 | ⬜ pending |
| TBD | `TemplateResolution` widening | 2 | TPL-03 | — | single priority walk preserved (CONF-07/D-06) — no second lookup | unit | additive assertions in `tests/test_template_engine.py::TestTemplateResolutionProvenance` | ✅ additive | ⬜ pending |
| TBD | thread into `render_wrapper()` | 2–3 | TPL-03, TPL-04 | — | N/A | integration | full suite: the 32-file net green unmodified | ✅ | ⬜ pending |
| TBD | push + dispatched CI | 3 | SC#5 | — | N/A | manual | `git ls-remote` + `gh run view` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_template_registry.py` (planner-chosen name) — covers TPL-01, TPL-04, TPL-05,
      CONF-14…CONF-18. No existing test file exercises the resolver, which does not yet exist.
- [ ] `53-RED-EVIDENCE.md` — the one-off SC#2 evidence artifact (RESEARCH Q6). Not a pytest file; a
      markdown artifact recording before/after commit SHAs, per-file SHA-256 of the emitted `.typ`
      files, and PDF page counts across the four existing shapes.
      **Do not name it `53-VERIFICATION.md`** — that name is reserved by `gsd-verifier` and would be
      clobbered (D-12).
- [ ] `tests/test_template_engine.py::TestTemplateResolutionProvenance` — **no new file**; additive
      assertions only, confirming the widened resolution exposes the resolved path at each of the three
      priorities alongside the existing `.source` assertions. Do not restructure the 3 tests that pass.
- Framework install: none — pytest/tox already provisioned via `uv sync --extra dev`.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| SC#2's byte-identity across the four existing shapes | TPL-03, TPL-04 | D-12 forbids a new golden-file pytest gate; a golden generated from post-change code cannot prove pre-change identity, and Phase 54 invalidates the layout one phase later | Run RESEARCH Q6's procedure at the named before/after commits; record SHA-256 per `.typ` and PDF page counts in `53-RED-EVIDENCE.md` |
| Dispatched CI run's per-lane conclusions (Windows / macOS especially) | SC#5 | The run happens on GitHub; the evidence is the recorded run ID + per-lane conclusion | `git push origin gsd/v0.9.0-per-document-templates` → `gh workflow run CI --ref gsd/v0.9.0-per-document-templates` → poll `gh run list --branch …` → `gh run view <id> --json jobs -q '.jobs[] \| {name, conclusion}'`; transcribe run ID and each lane verbatim |
| That `_escapes_outdir()` / `_is_drive_qualified()` were **not** reused, with the reason recorded | CONF-18 (SC#4) | SC#4 requires the artifacts to record *why*, which is a written rationale, not an assertion | Confirm a plan/summary paragraph states their documented contract permits a `/` — the opposite of a single segment's contract |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s for the registry test subset
- [ ] The 32-file `_template.typ` regression net passes **unmodified** — count re-measured by grep, not
      copied from prose (ARCHITECTURE.md §4's summary sentence says 31; its own enumerated list is 32)
- [ ] No evidence artifact named `53-VERIFICATION.md` (reserved by the verifier — D-12)
- [ ] CONF-18's denylist stays at **exactly seven** cases (D-02); no eighth case, no allowlist
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
