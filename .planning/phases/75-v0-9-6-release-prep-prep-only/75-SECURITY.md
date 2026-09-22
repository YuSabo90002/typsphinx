---
phase: "75"
slug: "v0-9-6-release-prep-prep-only"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-09-22"
---

# Phase 75 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

State B run: no SECURITY.md existed. All seven plans carried a `<threat_model>` block authored at
plan time, so `register_authored_at_plan_time` is `true` and this audit **verified that the
registered mitigations exist** rather than scanning for new threats.

Every row below was measured by the auditor against the live repository, git history, the GitHub
API and PyPI — not read from the phase's own evidence claims.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| `.planning/REQUIREMENTS.md` → phase-completion tooling | automation writes to a file this phase must hold unchanged, with no human in the loop at write time | release-readiness state (REL-15 checkbox) |
| local measurement → published claim | a zero count measured here becomes the basis for a claim in the release notes and the handoff | warning counts, message-class censuses |
| repository state → remote publish surfaces | tag, PyPI and GitHub Release probes are the only evidence that nothing irreversible has happened | publish state |
| worktree → main checkout working tree | 75-02's first task is the only one in the phase that writes outside its own worktree | untracked scratch files |
| `CHANGELOG.md` → published documentation and the GitHub Release body | `docs/source/changelog.rst` includes the file; `release.yml` reads the `## [0.9.6]` section through the extractor at tag time | public release prose |
| `pyproject.toml` → `uv.lock` → installed distribution | a hand-edited lock would be underivable and could diverge from what CI resolves | dependency resolution |
| documentation → external network | `linkcheck` is the only gate whose verdict depends on hosts outside this project | third-party availability |
| milestone branch → `origin/main` | the merge is the irreversible step this phase must prove safe without performing | repository history |
| local branch → `origin`, and dispatch → GitHub Actions | the only writes this phase makes to a remote | branch tip, one workflow dispatch |
| phase evidence → `/gsd-complete-milestone` | a different command, in a later session, executes the release from this handoff alone | release procedure |
| `gh` command construction → GitHub API | a command body assembled from unvetted text is the injection surface | API write authority |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-75-01 | Tampering | REQUIREMENTS REL-15 checkbox flipped by tooling | high | mitigate | SHA-256 + line-count + verbatim grep fence at head, close and after tooling; revert-and-report. Fired at `phase.complete`, caught, REL-15 reverted pre-commit (`75-CLOSEOUT-GUARD.md` § Third observation) | closed |
| T-75-02 | Repudiation | unfalsifiable zero warning/message-class counts | high | mitigate | synthetic control yields 1/2/2 hits; Phase 74's pre-fix real-build control at `6cc44f22` | closed |
| T-75-03 | Repudiation | empty probe that is empty because the command is wrong | medium | mitigate | every emptiness probe carries a live `v0.9.2` positive control | closed |
| T-75-04 | Info Disclosure | credential in transcribed command output | medium | mitigate | 12-pattern credential grep over every phase artifact returns zero hits | closed |
| T-75-05 | DoS | incremental documentation build under-reporting warnings | medium | mitigate | `rm -rf docs/_build` before every counted build, each under `LANG`/`LANGUAGE`/`LC_ALL`=C | closed |
| T-75-06 | Tampering | deletion in the main checkout reaching a tracked file | high | mitigate | toplevel confirmed, 5× `ls-files --error-unmatch` each non-zero, depth-1 glob, one `rm` per path; `.gitignore` unchanged | closed |
| T-75-07 | Repudiation | IN-01 dropped silently under the prep-only fence | medium | mitigate | tracked pending todo naming both functions, the stale text, the review ID and the deferral reason | closed |
| T-75-08 | Spoofing | fabricated coverage-matrix row | low | **accept** | reasoned one-line declaration written instead of a matrix; gate returns `passed: true`. See Accepted Risks Log | closed |
| T-75-09 | Repudiation | release-notes claim untrue of this milestone's diff | high | mitigate | D-04's corrected wording used; the blanket dependency sentence negative-checked to 0 inside `## [0.9.6]`. See advisory 4 | closed |
| T-75-10 | Tampering | carried bullet silently re-worded during promotion | high | mitigate | per-subsection SHA-256 digests recomputed base vs `## [0.9.6]`; carried `### Fixed` bullet a byte-identical tail | closed |
| T-75-11 | Repudiation | already-fixed defect published as a current limitation | high | mitigate | `### Known Limitations` negative-checked for all four excluded defects (0 hits each); exactly 1 bold-lead entry, NUM-01 | closed |
| T-75-12 | Tampering | hand-edited `uv.lock` | medium | mitigate | `uv lock --check` exit 0; the lock's diff in the bump commit is the single `typsphinx` version line | closed |
| T-75-13 | Info Disclosure | scratch block leaking into the public release body | medium | mitigate | extractor re-executed: 7104 bytes, digest matches, zero `Planned for Future Releases`, zero `## [` lines | closed |
| T-75-14 | DoS | version bump landing alone, stalling dependency PRs | high | mitigate | `git show --name-only` on the bump commit lists exactly the five-file union | closed |
| T-75-15 | Repudiation | a gate turned green by editing a test, config key or source file | high | mitigate | 75-04 touches only `.planning/`; the red linkcheck gate was recorded verbatim as NOT-MET and escalated, then amended by owner decision, never edited green | closed |
| T-75-16 | DoS | locale-dependent failure appearing only in CI | medium | mitigate | full suite run twice, second under `LC_ALL=C`, both 1569 passed; re-taken identically on the fix tip. See advisory 5 | closed |
| T-75-17 | Repudiation | false baseline from an incremental rebuild | high | mitigate | `rm -rf docs/_build` before every counted build; integers re-parsed from the saved logs at verify time | closed |
| T-75-18 | Tampering | linkcheck pass bought with an ignore key | medium | mitigate | `docs/source/conf.py` carries **zero** `linkcheck` keys, verified live; unchanged since Phase 45.1 | closed |
| T-75-19 | Repudiation | zero-skip claim in an environment that could only skip | high | mitigate | `--extra docs` provisioned everywhere, `-rs` mandatory; live re-run gives 6 passed with `myst_parser` importable | closed |
| T-75-20 | Tampering | trial merge creating a real commit or moving a ref | high | mitigate | `git merge-tree --write-tree` only; no merge- or trial-named branch exists; no merge commit has an `origin/main`-side parent | closed |
| T-75-21 | Spoofing | assuming `main`'s required checks from memory | medium | mitigate | fetched live at preflight and at CI close, compared char-for-char against Phase 74's reading | closed |
| T-75-22 | Repudiation | zero open-PR count produced by a wrong query | medium | mitigate | all-state control returns rows before any zero is believed; reproduced live | closed |
| T-75-23 | EoP | `gh` body built by shell command substitution | medium | mitigate | every `gh` call in the phase is a GET; zero write verbs anywhere in the artifacts | closed |
| T-75-24 | DoS | lint version skew between the merged tree and CI | medium | mitigate | merged tree's own resolved ruff recorded and lint run inside it. See advisory 2 — `main` has since moved to ruff 0.16.8, re-measured clean | closed |
| T-75-25 | Tampering | force-push, or decoy branch mishandled | high | mitigate | `ORIGIN_BEFORE` re-measured immediately before each push and proven an ancestor; no force flag; `DECOY_ACTION = none-present` | closed |
| T-75-26 | Repudiation | two CI runs making the dispatch reading unverifiable | high | mitigate | three dispatch runs on the branch, each on a **distinct** `headSha`; no tip carries two. `DISPATCH_COUNT_PHASE_TOTAL = 2` recorded with dispatch 1's original reading preserved | closed |
| T-75-27 | Tampering | an irreversible action slipping in beside the push | **critical** | mitigate | fence probed live: no `v0.9.6` tag local or remote, no GitHub Release, PyPI 404 against a 200 control, 0 open PRs, 0 `release.yml` runs at either pushed SHA | closed |
| T-75-28 | Repudiation | green read from run status while a job failed | high | mitigate | per-job read of run `35714217450`: 12/12 `success`, four cross-platform lanes asserted individually, job-name set byte-identical to run 1 and to Phase 74's reference | closed |
| T-75-29 | Info Disclosure | wholesale job log carrying a token | medium | mitigate | only the named lint step's two command lines and its result line are quoted | closed |
| T-75-30 | Tampering | REL-15 flipped by tooling after the last plan finishes | high | mitigate | third observation's commands, expected values and reversion recipe present in both the guard and the handoff; the flip then fired and was caught | closed |
| T-75-31 | Repudiation | a handoff depending on files the operator does not open | high | mitigate | all six required contexts, every SHA, run id and digest inlined; no step requires another file | closed |
| T-75-32 | EoP | release body assembled by command substitution | medium | mitigate | `75-HANDOFF.md` carries zero `$(` and zero `--body`; the release body comes from the extractor inside `release.yml` | closed |
| T-75-33 | Repudiation | scope fence passing because its pathspec matches nothing | high | mitigate | both fences reproduced live with non-vacuous controls | closed |
| T-75-34 | Tampering | ROADMAP/STATE mangled unnoticed | medium | mitigate | both backed up to scratch at phase head and diffed at close; both were mangled by `phase.complete` and repaired, each repair enumerated in `1a777938` | closed |
| T-75-35 | Spoofing | Dependabot ordering rule keyed on a stale count | medium | mitigate | handoff quotes the census with its timestamp, adds a live re-read, states the rule conditionally, and rejects both figures as operative. See advisory 3 | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-75-01 | T-75-08 | A coverage matrix row would have to describe an integration this phase does not build. Phase 75 names `gh api`, PyPI, Read the Docs and a `workflow_dispatch` often enough that the seal-time api-coverage detector has a live false-positive history in this repository, but every one of those is a read-only probe or a CI dispatch, not an external API integration. A reasoned one-line declaration in `COVERAGE.md` is the documented accepted form, and the gate returns `passed: true` against it. Fabricating a matrix row would itself be the spoofing this threat names. Severity low; below the `high` block threshold either way. | Phase 75 plan author (75-02 `<threat_model>`, disposition `accept`), confirmed by this audit | 2026-09-22 |

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-09-22 | 35 | 35 | 0 | gsd-security-auditor (opus), State B, ASVS L1, block_on high |

---

## Advisories

Informational findings from the audit. None is a missing mitigation; none blocks.

1. **T-75-08's accepted risk now has a persistent home** — this file's Accepted Risks Log, above.
   Before this file existed the acceptance lived only in the plan's register row and `COVERAGE.md`.

2. **`origin/main` has moved since the trial merge, and the movement includes ruff.** The preflight
   recorded `main` at `6cc44f22` with `MAIN_MOVED = no`. It is now `3f084add`: four Dependabot PRs
   (#152 pypdf, #153 tox, #154 ruff 0.16.7 → 0.16.8, #155 types-docutils) merged 2026-09-21/22.
   The recorded `MERGE_TREE = 96d8ca9e` is therefore stale — the live trial merge now yields
   `2fc4368a`. Because `main` is `strict: true`, the branch must be updated and CI re-run before the
   release PR can merge. `75-HANDOFF.md` already carries that instruction conditionally; the
   condition is now actually true.

   **T-75-24's risk was re-measured rather than left open.** The merged tree will carry ruff
   `0.16.8` while this phase's CI ran `0.16.7`. `ruff==0.16.8` was run against this tree:
   `All checks passed!`, exit 0. The skew exists but does not materialise.

3. **The Dependabot census is stale in the same way.** `DEPENDABOT_OPEN_PRS = 0` and the handoff's
   live re-read `HANDOFF_OPEN_PRS_LIVE = 0` are both still true right now, but four PRs opened and
   merged after the census was taken. T-75-35's mitigation anticipated exactly this and instructs a
   re-read at release time.

4. **T-75-09 advisory: the `### Verified` prose is narrower than D-04's own measurement.** The
   published bullet says the `dev` extra's only change is the `tox-uv` return. The measured
   `v0.9.2..HEAD` diff of `pyproject.toml` also carries `ruff>=0.15,<0.16` → `ruff>=0.15,<0.17` and
   two removed `ruff` ignores (`UP035`, `UP006`). D-04 (`75-CONTEXT.md:92-99`) documented the ruff
   cap move *and then prescribed the narrower wording*, so the implementation matches the decision
   exactly — but the decision's own prose omits a dependency-constraint change it had measured.
   Worth the owner's eyes before the tag; not a gate, and not a defect in the mitigation.

5. **`tox -e linkcheck` was the one command not locale-pinned.** Its `output.json` `info` field
   carries a localized Japanese string. Linkcheck is not a warning-counted build, so this falls
   outside T-75-05/T-75-16's declared scope, but CI runs in English and this project has been bitten
   by locale-dependent readings before. Relevant to the post-tag linkcheck re-run the handoff
   requires.

6. **No `## Threat Flags` section exists in any SUMMARY.** There is no executor-side surface
   declaration to cross-check the register against. The register's own completeness carried the
   audit instead.

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-09-22
