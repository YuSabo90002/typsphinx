---
phase: 58
slug: repr-format-decoupling-test-side-only
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: 2026-08-28
---

# Phase 58 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

Register origin: `register_authored_at_plan_time: true` — all three PLAN files
(`58-01`, `58-02`, `58-03`) carried a parseable `<threat_model>` block. Verification
scope is therefore *mitigation existence*, not retroactive STRIDE discovery.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| worktree working tree → milestone branch | The only boundary this phase actively opened. Plans 58-01 and 58-02 each made a transient product edit under `typsphinx/` to record a real RED, then reverted it. A skipped or partial revert would cross a product change into a merged commit. | Product source text (`typsphinx/builder.py`) |
| product log/output text → test assertion | The only "input" `path_named_in()` sees: trusted test-authored literals plus the product's own emitted message text. | Log record text; no external or user-controlled data |
| test-support module → whole test suite | `tests/_path_naming.py` is importable from anywhere `tests/` is on `sys.path`; a name collision would affect unrelated tests. | Python module namespace |
| `tests/**/*.py` source text → census guard verdict | The guard reads and `ast`-parses every file under `tests/`. An unparseable file, or a silently skipped directory, becomes a hole in the enumeration the guard exists to keep honest. | Test source text |
| prior plans' evidence sections → later plans' appends | Three plans wrote one evidence file across three waves. An append that rewrote a prior section would destroy non-re-derivable evidence (the SC#2(a) pre-rewrite baseline in particular). | Recorded run transcripts |
| local repository → `origin` | The milestone branch push — the only outbound action in the phase. | Git refs |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-58-01 | Tampering | `typsphinx/builder.py` — the D-05(b) transient edits (plans 58-01, 58-02) | high | mitigate | Edit/measure/revert confined to each plan's Task 2, then proven clean at phase scope. Re-measured 2026-08-28: `git diff --stat 3b0f2b93..HEAD -- typsphinx/` empty, `git log --oneline 3b0f2b93..HEAD -- typsphinx/` empty, `git status --porcelain typsphinx/` empty. Evidence § SC#4. | closed |
| T-58-02 | Repudiation | the rewritten pass criterion, and the census guard passing vacuously | medium | mitigate | Two independently-required falsification routes, both present. (a) Durable meta-tests: `tests/test_path_naming_predicate.py` — four-shape parametrization (`test_all_escape_shapes_absent_from_falsified_line_are_not_named`) plus the D-03 fallback-trap `False` case. (b) One-time recorded real RED against a live product edit at both sites — evidence §§ "SC#2 (c) … builder.py:697" and "SC#2 (c) … builder.py:1767". Guard non-vacuity: `MINIMUM_FILES_SWEPT = 100` asserted by `test_sweep_is_not_vacuous`, `SyntaxError` routed to `pytest.fail` rather than skip, and the guard itself observed RED once (evidence § D-09, three-step transcript). Re-measured 2026-08-28: 16 passed. | closed |
| T-58-03 | Spoofing | pushing the wrong branch — the decoy-pair hazard | medium | mitigate | Canonical config-slug branch confirmed. Re-measured 2026-08-28: `git branch --list 'gsd/v0.9.1*'` → only `gsd/v0.9.1-windows-path-correctness`; `git ls-remote --heads origin 'gsd/v0.9.1*'` → only `refs/heads/gsd/v0.9.1-windows-path-correctness`. No `gsd/v0.9.1-milestone` decoy local or remote. Upstream read back independently: `git rev-parse --abbrev-ref HEAD@{upstream}` → `origin/gsd/v0.9.1-windows-path-correctness`. | closed |
| T-58-04 | Spoofing | `tests/_path_naming.py` shadowing an existing importable module | low | accept | Accepted risk AR-58-01 below. Re-measured 2026-08-28: `_path_naming` resolves nowhere outside `tests/`; the repo contains exactly one such module. | closed |
| T-58-05 | Tampering | `58-DECOUPLING-EVIDENCE.md` — prior plans' recorded runs | medium | mitigate | Append-only confirmed across all seven commits touching the file (`--numstat`: 131/0, 351/0, 57/1, 105/0, 149/0, 153/0, 180/0). The single deletion is the `<!-- gsd:write-continue -->` sentinel, not evidence content. All ten `##` headings present in wave order, SC#2(a) pre-rewrite baseline first and intact. | closed |
| T-58-06 | Elevation of privilege | an unintended irreversible remote action riding along with the push | high | mitigate | Re-measured 2026-08-28: `git tag -l 'v0.9.1*'` empty and `git ls-remote --tags origin 'v0.9.1*'` empty. The phase's only remote action is a plain branch publish, which is deletable. No tag, no PR, no workflow dispatch. | closed |
| T-58-SC | Tampering | package-manager installs | low | accept | Accepted risk AR-58-02 below. Re-measured 2026-08-28: `git diff --stat 3b0f2b93..HEAD -- pyproject.toml uv.lock` empty — zero dependency change. New modules are stdlib-only (`ast`, `os`, `pathlib`) plus the already-pinned `pytest`. | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-58-01 | T-58-04 | `tests/` holds no bare top-level support module other than `conftest.py`, and the name `_path_naming` appears nowhere else in the suite or on `sys.path`, so the new leaf module cannot shadow an existing import. Recorded rather than gated — severity low, below the `high` block threshold. | plan 58-01 (author), re-measured by secure-phase | 2026-08-28 |
| AR-58-02 | T-58-SC | The phase installs no new package. `uv sync --extra dev` resolves the existing committed `uv.lock` only. `58-RESEARCH.md` § "Package Legitimacy Audit" records the supply-chain gate as not applicable: zero packages proposed, zero `[SUS]`, zero `[SLOP]`. | plan 58-01 (author), re-measured by secure-phase | 2026-08-28 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-08-28 | 7 | 7 | 0 | /gsd-secure-phase (orchestrator, ASVS L1 short-circuit) |

### Security Audit 2026-08-28

| Metric | Count |
|--------|-------|
| Threats found | 7 |
| Closed | 7 |
| Open | 0 |

Short-circuit applied per `secure-phase` Step 3: `threats_open: 0` AND
`register_authored_at_plan_time: true` AND `asvs_level == 1` → L1 grep-depth
verification is sufficient; no auditor subagent spawned. Every closure above was
re-measured live against the working tree on the audit date, not copied from the
plans' own claims.

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-08-28
