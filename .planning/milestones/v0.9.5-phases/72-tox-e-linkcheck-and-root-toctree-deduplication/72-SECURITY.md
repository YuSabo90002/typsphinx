---
phase: "72"
slug: "tox-e-linkcheck-and-root-toctree-deduplication"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-09-14"
---

# Phase 72 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.
> Built by `/gsd-secure-phase 72` from the `<threat_model>` blocks of 72-01..72-06-PLAN.md
> (register authored at plan time). No SUMMARY carries a `## Threat Flags` section.
> ASVS L1, `block_on: high` — grep-depth verification against the phase evidence files and a fresh
> re-measurement of git, origin and GitHub Actions state on 2026-09-14; auditor not spawned
> (short-circuit rule: threats_open 0, register authored at plan time, ASVS 1).
> `T-72-SC` appears in 72-01, 72-02 and 72-05 with the same disposition and is listed once.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| `git archive` snapshot → scratch build | the base tree is rebuilt outside the tracked tree; a stale or incremental output could fake a baseline | docs source tree, build logs (non-sensitive) |
| Sphinx / tox console → evidence | localised console text can turn a real count into a false zero | message counts, warning counts |
| linkcheck builder → the internet | outbound HTTP to URLs already committed in docs sources, CHANGELOG.md and docstrings | public URLs, HTTP status |
| `tox.ini` → every tox user and CI's tox-driven jobs | a new section is parsed by every tox invocation | tox configuration |
| docs surfaces / CLAUDE.md → contributors and agent sessions | a listed command is taken as true | command names |
| local refs → origin | a push publishes refs | branch ref, commits |
| gh CLI → GitHub Actions and branch protection | a dispatch starts remote work; reads of protection settings | workflow dispatch, run data, check names |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-72-01 | Repudiation | C-locale grep reading localised output (false zero) | high | mitigate | `LANG=C LC_ALL=C` on every build and grep; `BASE_MULTI_TOCTREE_COUNT = 5` on the base as positive control; English `build succeeded, 3 warnings.` present (72-BASE-EVIDENCE.md, re-grepped by the orchestrator) | closed |
| T-72-02 | Tampering | incremental or wrong-tree base build | medium | mitigate | full-tree `git archive` of `PHASE_BASE_SHA` into a fresh `mktemp -d`; `PHASE_BASE_SHA` tree equals milestone base 098a8ff6 outside `.planning/` (72-BASE-EVIDENCE.md § Base identity) | closed |
| T-72-03 | Tampering | DOC-18 edit touching more than the five entries | medium | mitigate | `git diff --numstat PHASE_BASE_SHA HEAD -- docs/source/index.rst` = `0 5`; section indexes and conf.py absent from the diff (re-measured 2026-09-14) | closed |
| T-72-04 | Information Disclosure | branch-protection settings and run IDs in committed evidence | low | accept | public repository; only check names and run IDs recorded — see AR-01 | closed |
| T-72-05 | Repudiation | linkcheck pass manufactured by an ignore-style key or a link edit | high | mitigate | `grep -c '^linkcheck_' docs/source/conf.py` = 0; no ignore-style key; `LINKCHECK_VERDICT = PASS` on run 1, 95/95 `working` (72-LINKCHECK-EVIDENCE.md) | closed |
| T-72-06 | Repudiation | pass read from a run that did not meet SC#1, or a failure erased | high | mitigate | one run taken, the pass run, exit 0, live recount of `output.json` = 95/95 (re-counted by the orchestrator and the verifier) | closed |
| T-72-07 | Denial of Service | linkcheck entering `env_list` | medium | mitigate | `tox.ini` line 2 still `env_list = py312, py313, lint, type, cov, docs`; `tox.ini` numstat `8 0` (pure append); `tox list` shows linkcheck under additional environments only | closed |
| T-72-08 | Information Disclosure | SSRF / internal-host probing through a committed doc URL | low | accept | local, manual tool over URLs reviewed at commit time — see AR-02 | closed |
| T-72-09 | Tampering | malformed `tox.ini` breaking CI's tox-driven jobs | medium | mitigate | configparser parse in 72-02's verify; CI run 34761445288 `Lint and Format Check` quotes `Run lint with tox` and succeeded (72-CI-EVIDENCE.md) | closed |
| T-72-10 | Repudiation | a surface naming a missing environment, or implying CI runs it | medium | mitigate | 72-03 gated on `[testenv:linkcheck]` at its base; each added line says "needs network; not run by plain tox"; numstat `1 0` per surface (no prose) | closed |
| T-72-11 | Tampering | CLAUDE.md sync-hazard lines disturbed | medium | mitigate | CLAUDE.md numstat `1 0`; `tox  # env_list: …` line present byte-identical (re-grepped) | closed |
| T-72-12 | Repudiation | a listing surface missed by trusting the roadmap's three | low | mitigate | fresh repo-wide and supplementary greps with a disposition row per hit; `DOC24_LINKCHECK_LINES = DOC24_LISTING_SURFACES = 3` (72-DOC24-EVIDENCE.md § Dispositions) | closed |
| T-72-13 | Repudiation | tip zero read from localised or quieted output | high | mitigate | `LANG=C LC_ALL=C`, no `-q`; same-venv base count 5, tip 0, both English summaries present (72-TOCTREE-EVIDENCE.md, re-grepped by the orchestrator) | closed |
| T-72-14 | Repudiation | base and tip built in different environments | medium | mitigate | built back to back in one venv with interpreter recorded; `W1_BASE_MATCH = yes` | closed |
| T-72-15 | Tampering | acting on the parent divergence beyond scope | low | mitigate | `DIVERGENCE_SURVIVES = no`, `DIVERGENCE_TODO = none`; 72-04's diff holds only its evidence and SUMMARY | closed |
| T-72-16 | Tampering | unpickling an untrusted file | low | accept | the pickle is the executor's own build output in its own `mktemp -d` — see AR-03 | closed |
| T-72-17 | Repudiation | false zero from a localised tox docs-html log (tox drops LC_ALL) | high | mitigate | `LANG=C LANGUAGE=C LC_ALL=C uv run tox -e docs-html`; English summary present, `TOX_HTML_MULTI_TOCTREE = 0`, warnings 3 = base (72-GATES-EVIDENCE.md, log re-grepped) | closed |
| T-72-18 | Repudiation | tip linkcheck pass manufactured by an ignore key or link edit | high | mitigate | `TIP_LINKCHECK_VERDICT = PASS`, 95/95 on run 1; conf.py has 0 linkcheck keys | closed |
| T-72-19 | Tampering | scope creep into typsphinx/, workflows, packaging or tests | high | mitigate | `git diff --stat PHASE_BASE_SHA HEAD -- typsphinx/ .github/` empty (re-measured 2026-09-14); product diff = the five named files | closed |
| T-72-20 | Tampering | pushing a decoy, force, another ref, or a tag | high | mitigate | census before push; `gsd/v0.9.5-milestone` absent locally and on origin; `ORIGIN_BEFORE = none`; no v0.9.3/v0.9.4/v0.9.5 tag on origin (re-measured) | closed |
| T-72-21 | Elevation of Privilege | triggering `release.yml` or `update-pin.yml` | high | mitigate | only `gh workflow run CI` issued; `RELEASE_RUNS_AT_PUSHED = 0` (re-measured via `gh run list --workflow=release.yml`) | closed |
| T-72-22 | Repudiation | citing a stale run, or masking red with a second dispatch | high | mitigate | run 34761445288 headSha = `PUSHED_SHA` 0b2595df, event `workflow_dispatch`; `DISPATCH_COUNT = 1`; 12/12 jobs success (re-read live) | closed |
| T-72-23 | Tampering | required status checks changing mid-phase | medium | mitigate | head and close reads equal on strict and sorted contexts; `REQUIRED_CHECKS_UNCHANGED = yes` | closed |
| T-72-24 | Denial of Service | stale `uv.lock` failing every lane | medium | mitigate | `uv sync … --locked` exit 0 before the push (72-CI-EVIDENCE.md); orchestrator `uv lock --check` clean | closed |
| T-72-25 | Information Disclosure | CI log excerpts in evidence | low | accept | public repository and logs; only tool-output lines quoted — see AR-04 | closed |
| T-72-SC | Tampering | package installs during provisioning / tox | low | accept | `uv sync` and `uv-venv-lock-runner` install only what `uv.lock` pins; no new dependency — see AR-05 | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-01 | T-72-04 | The repository is public; recording required-check names and CI run IDs discloses nothing not already visible on GitHub. | plan-time disposition (72-01), confirmed at secure-phase | 2026-09-14 |
| AR-02 | T-72-08 | `tox -e linkcheck` is a local, manually run tool; it fetches only URLs already reviewed when committed to docs, CHANGELOG.md or docstrings, and runs with the invoking developer's own network access. It is not in `env_list` or any CI job. | plan-time disposition (72-02), confirmed at secure-phase | 2026-09-14 |
| AR-03 | T-72-16 | The unpickled `environment.pickle` was produced by the same executor's own Sphinx build, in its own `mktemp -d` directory, moments earlier; no external pickle is loaded. | plan-time disposition (72-04), confirmed at secure-phase | 2026-09-14 |
| AR-04 | T-72-25 | CI logs are public for this repository; only tool-output lines (black, ruff, job conclusions) are quoted. | plan-time disposition (72-06), confirmed at secure-phase | 2026-09-14 |
| AR-05 | T-72-SC | All installs resolve from the committed `uv.lock`; the phase added no dependency (`pyproject.toml` and `uv.lock` absent from the phase diff). | plan-time disposition (72-01, 72-02, 72-05), confirmed at secure-phase | 2026-09-14 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-09-14 | 26 | 26 | 0 | /gsd-secure-phase 72 (orchestrator, ASVS L1 short-circuit; auditor not spawned) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-09-14
