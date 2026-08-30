---
phase: 63
slug: v0-9-2-release-prep-prep-only
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: 2026-08-30
---

# Phase 63 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

**Register origin:** `register_authored_at_plan_time: true` — all six plans (`63-01` … `63-06`)
carry a parseable `<threat_model>` block. No retroactive-STRIDE reconstruction was needed.

**Verification depth:** ASVS L1 (`workflow.security_asvs_level: 1`), blocking threshold
`workflow.security_block_on: high`. Every mitigation below was re-measured live by the orchestrator
against the phase tip `80fdf64338a65f686ceba2e6132df7d995789fc8` rather than read out of the phase's
own evidence files. Where a probe crosses a network boundary, a positive control derived from the
same fetch is recorded so an unreachable endpoint cannot masquerade as a clean result.

**Phase shape:** prep-only. The phase bumps a version, curates release notes, proves a green tree
and hands off a publish sequence. It performs **no** irreversible release action — the dominant
threat class here is a prep-only phase leaking into a publish, and a release note asserting something
the milestone did not measure.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| `CHANGELOG.md` → `scripts/extract_changelog_section.py` → GitHub Release body | Positional extraction; physical layout decides published content. Body is published verbatim by `release.yml`'s `create-release` job at `/gsd-complete-milestone` | Curated public release prose (4083 bytes) |
| `CHANGELOG.md` → `docs/source/changelog.rst` (MyST include) → Read the Docs (`en` + `ja`) | Same prose crosses into a publicly reachable page on every docs build | Public documentation markup |
| Published release notes → a downstream integrator's security review scope | A blast-radius claim is what a security-conscious consumer uses to decide which files to diff; a falsely narrow claim removes files from that review | Security-relevant scope assertion |
| `pyproject.toml:7` → `uv lock` → `uv.lock` → `uv sync --extra dev --locked` | The version literal crosses into the install precondition of twelve CI lanes and both release-workflow install steps | Build/install integrity |
| `.planning/REQUIREMENTS.md` → `phase.complete`-family tooling → `/gsd-complete-milestone` | Project-state metadata crosses into automated tooling that has mutated it against an explicit decision at five consecutive prior release-prep closes | Release-state truth (REL-09/10/11) |
| this worktree → `origin` + GitHub API (`git ls-remote`, `gh release list`, `gh run list`, `gh pr list`) | Read-only probes whose failure mode is silence — indistinguishable from a clean result without a control | Remote repository state |
| `63-CLOSEOUT-GUARD.md` PHASE_BASE_SHA → plans 63-03/04/06 diff scoping | One recorded anchor decides whether SC#5's central empty-diff claim is a finding or an artifact | Verification anchor |
| `63-HANDOFF.md` → the operator running `/gsd-complete-milestone` | The only carrier of the publish sequence across the phase boundary; an omitted step is a step that does not happen, and a step worded as an instruction could be executed early | Irreversible-action runbook |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-63-01 | Tampering | Scratch (`[Unreleased]`) block leaking into the published Release body — `_SECTION_HEADER_RE` selects by position, never by heading name | high | mitigate | Extractor re-run live: exit 0, 4083 bytes, **0** occurrences of `Unreleased` / `Planned for Future`, **0** stray `## [` version headings in the body | closed |
| T-63-02 | Tampering | Malformed MyST in the new lead paragraph / bullet / `### Verified` subsection publishing broken markup to RTD | medium | mitigate | Clean-build re-measure (`rm -rf docs/_build`) after the final `CHANGELOG.md` commit `2a0bc3be`: `docs-html` 3 warnings, `docs-pdf` 5 warnings — both match the recorded baseline exactly; `test_changelog_page_gate.py` green | closed |
| T-63-03 | Spoofing | Publishing an unresolvable version reference — a heading or tail link for a completed-but-never-published version (`links.yml`'s lychee scan excludes `CHANGELOG.md`, so CI would not catch it) | high | mitigate | `0.9.1` occurs **0** times file-wide; the only `0.9.x` headings are `[0.9.2]` (L17) and `[0.9.0]` (L74); the only `0.9.x` tail links are `[0.9.2]` (L1275) and `[0.9.0]` (L1276); `[Unreleased]` compares from `v0.9.2` | closed |
| T-63-04 | Elevation of Privilege | A partial bump — `pyproject.toml` moved without `uv.lock` regenerated — breaking every `uv sync --extra dev --locked` step before any test runs | high | mitigate | `pyproject.toml:7` = `0.9.2` and `uv.lock:1467` = `0.9.2`; `uv lock --check` resolves 89 packages clean; the bump landed as one commit `10d9d95d` | closed |
| T-63-05 | Repudiation | A `### Verified` bullet asserting a claim this milestone did not measure — the full-corpus `typstpdf` sentence nine prior entries carried | medium | mitigate | The inherited full-corpus sentence occurs **0** times inside the `[0.9.2]` section (it remains visible in `[0.9.0]`'s own section, confirming the grep discriminates); the third bullet is the TEST-05 gate result (16 previously-failing + 9 must-keep-passing shapes, 18/18 masters) | closed |
| T-63-06 | Repudiation | A skipped test recorded as a pass — the release-coverage tuple edit cited as proven by a run in which the asserting classes never executed | medium | mitigate | The proof carries the `docs` extra explicitly and reports both counts: `1547 passed, 1 skipped`; the changelog-content gate reports `17 passed, 0 skipped` | closed |
| T-63-07 | Tampering | REL-09's checkbox silently flipped by `phase.complete`-family tooling, misrepresenting release state to `/gsd-complete-milestone` | high | mitigate | Fence held. The flip **did** land post-`phase.complete` (widened this time to REL-09 **and** REL-10/REL-11), was caught by the whole-file digest, reverted with `git checkout --`, and never committed. Live re-measure: `sha256sum` = `f0dd4ec3…5b33` — matches Baseline; `REL-09` reads `- [ ]` (L70) and `Pending` (L154) | closed |
| T-63-08 | Repudiation | A vacuous fence proof — an unreachable endpoint producing the same empty output as a genuinely clean remote | high | mitigate | Independently re-probed: `v0.9.2` remote tag refs = **0**, positive control `v0.9.0` remote tag refs = **2** from the same fetch, so the probe demonstrably reached its source | closed |
| T-63-09 | Repudiation | A wrong PHASE_BASE_SHA — this plan's own tip recorded instead of the phase's base — making later scoped diffs empty for the wrong reason | medium | mitigate | `git cat-file -e c31bb048…` resolves; subject `docs(63): add pattern map` carries no `(63-NN)` plan scope, i.e. it predates plan execution; widened same-anchor control returns **3** files (non-empty) | closed |
| T-63-10 | Elevation of Privilege | A probe escalating into an action — `gh run list --workflow=release.yml` becoming `gh workflow run release.yml` | high | mitigate | Latest `release.yml` run is `v0.9.0` / `32560457509` from **2026-08-22**, eight days before this phase; no run exists against any Phase 63 commit | closed |
| T-63-11 | Tampering | The guard quoting a line shape the current `.planning/REQUIREMENTS.md` does not contain, so the close-time comparison compares nothing | medium | mitigate | `grep -n 'REL-09'` returns exactly the three hits the guard quotes (L70 state-bearing checkbox, L154 state-bearing Traceability row, L175 informational prose) | closed |
| T-63-12 | Elevation of Privilege | Reaching for the release workflow to find a lint step name, thereby triggering the publish pipeline from a prep-only phase | high | mitigate | The lint verdict is read from `ci.yml`'s own `Lint and Format Check` job; no `release.yml` run exists against this tip (see T-63-10) | closed |
| T-63-13 | Repudiation | A green inherited rather than observed — Phase 62's CI run, or a recalled warning count, cited as this phase's evidence | high | mitigate | Run `33309565005` re-queried live: `workflowName: CI`, `status: completed`, `conclusion: success`, `event: workflow_dispatch`, `createdAt: 2026-08-30T11:41:37Z`, **12/12 jobs success**. Its head SHA `225c6618` differs from the tip, but `git diff --name-only 225c6618..HEAD -- typsphinx/ tests/ pyproject.toml uv.lock` is **empty** — the product tree the green covers is byte-identical to the tree being released | closed |
| T-63-14 | Repudiation | An incremental docs rebuild under-reporting warnings and manufacturing a false baseline match | medium | mitigate | `rm -rf docs/_build` is part of each build command, not a preamble; both re-measured counts (3 / 5) come from clean builds piped live | closed |
| T-63-15 | Repudiation | A green `black` + `mypy` recorded as "lint clean" while `ruff` never ran anywhere (ruff cannot execute on this host) | high | mitigate | CI job `Lint and Format Check` conclusion = `success`, with the step log showing `lint: commands[1]> ruff check .` executing and reporting `All checks passed!`. Authority for the ruff verdict is CI, stated as such in the evidence | closed |
| T-63-16 | Tampering | A partial or stale lockfile failing all twelve lanes at the install step, producing a red run that says nothing about the code | high | mitigate | `uv lock --check` re-run live: resolves clean, no drift; all twelve CI lanes reached and passed their test phases | closed |
| T-63-17 | Tampering | A decoy milestone branch deleted first, orphaning commits carrying the phase's work | medium | mitigate | Branch census re-run: exactly one `0.9.2`-shaped branch exists locally **and** on `origin` — `gsd/v0.9.2-inline-image-blocker-fix-and-release`, the config-derived canonical slug. No `gsd/v0.9-milestone` decoy survives; no orphaned commits | closed |
| T-63-18 | Tampering | REL-09 flipped by tooling *after* the last plan runs (the historical landing point) | high | mitigate | Covered by the same evidence as T-63-07; the decisive third observation was taken **after** `phase.complete` ran and is recorded at `63-CLOSEOUT-GUARD.md` § "Third observation" | closed |
| T-63-19 | Repudiation | A vacuous SC#5 proof — an empty `typsphinx/` diff produced by a wrong or unreachable anchor | high | mitigate | Scoped `git diff --name-only c31bb048..HEAD -- typsphinx/` is **empty**; the same-anchor widened control returns **3** files (`CHANGELOG.md`, `pyproject.toml`, `uv.lock`), so the empty result is a finding, not an artifact of a dead anchor | closed |
| T-63-20 | Elevation of Privilege | A recorded command shape in the handoff executed as an instruction — a tag push, pin dispatch, or release trigger inside the prep-only phase | high | mitigate | `v0.9.2` local tags = **0**, remote tags = **0** (positive control `v0.9.0` = 2); `gh release list` shows `v0.9.0` still `Latest`; no `release.yml` run in this phase | closed |
| T-63-21 | Information Disclosure | An operator misreading a workflow paused on the `pypi` Environment approval as a failed workflow and abandoning or re-running the release mid-flight | medium | mitigate | `63-HANDOFF.md` places the approval-gate warning at L85–93 ("a workflow **paused** on that approval looks exactly like a **failed** workflow"), ahead of the `git tag -a v0.9.2` command at L103 — the operator meets the warning first in reading order | closed |
| T-63-22 | Repudiation | The handoff omitting a close-out step that is not a side effect of anything else — most dangerously the second repository's `update-pin.yml` MANUAL dispatch and its own separate tag | high | mitigate | All five SC#5 steps present and named: tag push (L103), `pypi` approval (L85–93), Release-body byte-identity (L5), `typsphinx-doc-translations` `update-pin.yml` **MANUAL dispatch** with the explicit "not a side effect of this repository's own tag push" statement (L166–172), closeout-guard pointer (L54). REL-04's four items present (L117–139) | closed |
| T-63-23 | Repudiation | Observation 2 recorded by copying observation 1's values, collapsing the two-observation fence into one | medium | mitigate | `63-SC5-INVARIANTS.md` carries three distinct phase-time Zulu timestamps (`2026-08-30T11:17:14Z`, `11:58:23Z`, `13:40:00Z`) and **14** `positive control` occurrences (≥ the 9 required) | closed |
| T-63G-01 | Tampering | The published blast-radius claim — a blanket file-confinement sentence contradicted by the milestone's own diff, narrowing a downstream integrator's review scope | high | mitigate | **This is the defect the gap closure fixed.** Commit `2a0bc3be` deletes the blanket sentence; the surviving intro scopes the claim to the one fix it holds for. Live read of `CHANGELOG.md:19–24` confirms the corrected text is what would publish | closed |
| T-63G-02 | Elevation of Privilege | Irreversible release actions during the gap closure — tag, PyPI upload, GitHub Release, PR, pin dispatch, `release.yml` trigger | high | mitigate | Same live probes as T-63-20; additionally re-probed by plan 63-06 against the post-correction tip rather than inherited | closed |
| T-63G-03 | Tampering | `.planning/REQUIREMENTS.md` REL-09 checkbox and Traceability row mutated during the closure | high | mitigate | No task edits the file; digest unchanged (T-63-07); the file is absent from the `docs(phase-63): complete phase execution` commit `7bafcb96` | closed |
| T-63G-04 | Repudiation | The phase's own evidence trail — erasing the record of what was inspected and what it missed | medium | mitigate | `63-CHANGELOG-EVIDENCE.md` is provably append-only: every commit touching it is `N insertions, 0 deletions` (285/0, 183/0, 96/0, 160/0). The original transcription of the false claim survives (L295, L452) alongside the named contradiction and its resolving commit (L444–461) | closed |
| T-63G-05 | Information Disclosure | The 0.9.0-blocker disclosure and the non-Windows-exclusivity framing deleted along with the false sentence by a careless correction | medium | mitigate | Both survive the correction: "0.9.0 users should upgrade to this release" (L23) and "this is not a Windows-exclusive fix" (L60–61) | closed |
| T-63G-06 | Spoofing | An extracted body that looks correct but is not the bytes that publish — a stale or partially-updated extractor output | medium | mitigate | Extractor re-run by the orchestrator against the corrected file: exit 0, 4083 bytes, content matches the on-disk section; `## [0.6.5]` served as the positive control so an empty `diff` from a broken pipeline could not masquerade as agreement | closed |
| T-63G-07 | Repudiation | A green test run recorded as proof of something it never executed — the changelog content gates skip without the `docs` extra | medium | mitigate | The invocation names `--extra dev --extra docs` explicitly and records both counts (`1547 passed, 1 skipped`), stating that the divergence from the 1543/5 baseline is caused by the differing extras, not by a tree or test change | closed |
| T-63H-01 | Elevation of Privilege | Irreversible release actions during the re-close | high | mitigate | Re-probed against the post-correction tip with positive controls; all absences confirmed independently above (T-63-20 / T-63G-02) | closed |
| T-63H-02 | Tampering | REL-09 flipped after the gap-closure commits move HEAD — the exact condition under which the flip has historically landed | high | mitigate | Re-verified after HEAD moved; the flip landed, was detected by the digest, reverted, and never committed. Current digest matches Baseline | closed |
| T-63H-03 | Repudiation | A phase-close verdict re-asserted rather than re-observed after the tree changed | high | mitigate | Three distinct fresh timestamps and 14 positive-control mentions (see T-63-23); no prior value is reused | closed |
| T-63H-04 | Tampering | A re-pointed anchor or digest in `63-CLOSEOUT-GUARD.md` — extraction is by first match, so file ordering is load-bearing | medium | mitigate | The first 64-hex match sits at L23 inside `## Baseline` (L7–51), above the appended `## Re-verification after gap closure` (L320) and `## Third observation` (L420). All three digest occurrences are the same value | closed |
| T-63H-05 | Spoofing | A stale extractor size in `63-HANDOFF.md` making a correct publish look like a failure, or masking a real body mismatch | medium | mitigate | The handoff records **4083** bytes (L47); the orchestrator's independent re-run of the extractor against the current file returns exactly 4083 bytes | closed |
| T-63H-06 | Information Disclosure | A handoff quietly shortened during the update, dropping a publish step or the approval-gate warning | medium | mitigate | Every element re-confirmed present by name — see T-63-21 and T-63-22 | closed |
| T-63H-07 | Repudiation | A statement in the evidence left standing after the closure invalidated it | medium | mitigate | Commit `83db2f4e` appends an explicit supersession record for the post-dispatch-commit statement, naming the correction commit and cross-referencing the measurement that explains why no re-dispatch follows — the original is superseded, not edited away | closed |
| T-63-SC | Tampering | npm/pip/cargo installs (plans 63-01 … 63-04) | low | accept | See ACC-63-01 | closed |
| T-63G-SC | Tampering | npm/pip/cargo installs (plan 63-05) | low | accept | See ACC-63-01 | closed |
| T-63H-SC | Tampering | npm/pip/cargo installs (plan 63-06) | low | accept | See ACC-63-01 | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| ACC-63-01 | T-63-SC, T-63G-SC, T-63H-SC | Supply-chain package-legitimacy review is not owed by this phase: it installs, adds and upgrades **zero** packages. `63-RESEARCH.md` § "Package Legitimacy Audit" measured this at plan time, and the orchestrator re-measured it — the only `pyproject.toml` / `uv.lock` change across the whole phase is the version literal `0.9.1` → `0.9.2` (the `### Verified` bullet asserting this is itself gated). `uv sync` installs only what the already-committed `uv.lock` resolves. Severity `low`, below the `high` blocking threshold. | yuta (phase owner, via plan-time disposition in all six PLAN.md threat models) | 2026-08-30 |

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-08-30 | 40 | 40 | 0 | orchestrator (`/gsd-secure-phase 63`, ASVS L1 short-circuit — register authored at plan time, threats_open 0) |

**Method.** All 37 `mitigate`-disposition threats were re-measured live against tip
`80fdf64338a65f686ceba2e6132df7d995789fc8` — extractor run, `uv lock --check`, `sha256sum`,
`git diff` with anchor + widened positive control, `git ls-remote` with a `v0.9.0` positive control,
`gh release list`, `gh run list`, `gh run view --json jobs`, and direct file reads — rather than
transcribed from the phase's own evidence files. The 3 `accept`-disposition threats are recorded in
the Accepted Risks Log above.

**Notable finding (mitigation working as designed, not a defect).** The `phase.complete` REL-flip
predicted by T-63-07/T-63-18/T-63G-03/T-63H-02 **did occur** at this close, and with a wider blast
radius than at the five prior closes — REL-09, REL-10 **and** REL-11 all flipped, where previously
only REL-09 had. A guard scoped to REL-09's grep alone would have missed two of the three; the
whole-file SHA-256 caught all three. The flip was reverted with `git checkout --` and never
committed. This is the control firing correctly, and the widened blast radius is worth carrying
forward to the next release-prep phase's guard design.

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-08-30
