# Phase 71: v0.9.4 Close Prep (prep-only, unpublished) - Context

**Gathered:** 2026-09-13
**Status:** Ready for planning

<domain>
## Phase Boundary

Package the v0.9.4 typing-modernization milestone for a merge to `main` and nothing else. That
means four things. Add one CHANGELOG bullet under the existing `## [Unreleased]`. Prove the tree is
unpublished-shaped and green on runs executed in this phase. Hold REL-13's checkbox at `[ ]` behind
the SHA-256 fence. Write a standalone `71-HANDOFF.md` for `/gsd-complete-milestone`.

**ROADMAP SC#1..SC#4 govern this phase.** One clause of SC#2 is amended (D-02). The other decisions
below settle only what the criteria leave open, and most of them carry forward from v0.9.3's
Phase 69, the same close-prep shape one milestone earlier.

**Zero irreversible action.** This phase makes no version bump, creates no tag (local or remote),
uploads nothing to PyPI, creates no GitHub Release, opens no PR, merges nothing, dispatches no
`update-pin.yml` and comments on no PR. It takes two outward actions, both standing prep-phase
precedent (Phases 57, 61, 63, 69): pushing the canonical milestone branch, and dispatching `ci.yml`
through `workflow_dispatch`.

**Measured state at discussion time (2026-09-13, HEAD `bcc109a0`):**
- **Version:** `pyproject.toml:7` reads `version = "0.9.2"`.
- **Branches:** local `gsd/v0.9.4-typing-modernization` is `main` + 96 commits and 13 ahead of its
  `origin` counterpart (all 13 are `.planning/` commits after Phase 70's push). `git branch -a --list
  '*v0.9.4*'` shows only the canonical branch and its remote-tracking ref, so there is no
  `gsd/v0.9.4-milestone` decoy.
- **`main`:** `origin/main` = `main` = `d14ca458` = the merge-base, so the milestone branch lacks
  **zero** `main` commits. `main`'s protection is `strict: true` with six required checks: `Test
  Python 3.12 on ubuntu-latest`, `Test Python 3.13 on ubuntu-latest`, `Lint and Format Check`, `Type
  Check`, `Code Coverage`, `Build Package`. The last milestone PR, #143, merged as `58d578f2`.
- **Open PRs:** none (`gh pr list --state open` → `[]`).
- **CHANGELOG:**
  - `CHANGELOG.md:8` is `## [Unreleased]`, `:10` is `### Changed`, holding v0.9.3's three bullets
    (tox-uv, Dependabot `uv`, `flake.nix`).
  - `:37` is `### Planned for Future Releases`.
  - `:1324` is `[Unreleased]: …/compare/v0.9.2...HEAD`.
  - `:1302` is `[0.9.2]: …/releases/tag/v0.9.2`.
- **Phase 70's base and numbers:** `PHASE_BASE_SHA = 697a1132…`
  (`70-BASELINE-EVIDENCE.md:4`). The after-side numbers are in `70-AFTER-RUNTIME-EVIDENCE.md`:
  `PYTEST_RESULT_AFTER = 1547 passed 1 skipped`, `LEG_D_VERDICT = MET`. The docs diff is in
  `70-DOCS-DIFF-EVIDENCE.md`: 5 HTML files and 1 `.typ`, 83 hunks, all traced.
- **`ja` site mechanism** (drives D-02):
  - `typsphinx-doc-translations`' `update-pin.yml` runs on `schedule: cron "0 6 * * *"` plus
    `workflow_dispatch`. Each run fetches `main`'s tip, runs `git submodule update --remote`,
    regenerates the `.pot`, runs `sphinx-intl update`, and commits if anything changed. Nothing in
    it depends on a release.
  - The daily runs succeeded through 2026-09-12T10:22Z. The pin `6181768f` has not moved only
    because `main` did not move between 2026-08-31 and #137 at 2026-09-12T10:38Z.
  - Positive control: `en/latest/changelog.html` shows v0.9.3's `tox-uv` bullet (3 hits), and
    `ja/latest` does not yet (0 hits; last ja build 2026-08-31 on `51862fdd`).
  - `locale/ja/LC_MESSAGES/api/index.po` has 668 msgids and **0** translated. Two msgids carry
    `~typing.Dict` / `~typing.Tuple` autodoc type roles.

</domain>

<decisions>
## Implementation Decisions

### The one `## [Unreleased]` CHANGELOG bullet

- **D-01: One bullet, appended as the fourth under the existing `### Changed`, after the `flake.nix` bullet.** It follows the house register of the three above it: a bold lead phrase ending with the requirement IDs in trailing parentheses (`QUA-09, QUA-11, QUA-12, DOC-22, DOC-23`), then prose written for a reader of the published changelog page (`docs/source/changelog.rst` includes `CHANGELOG.md`, so this text reaches Read the Docs `latest` once REL-13 merges). It names the API-reference type-text change with the concrete example `Dict[str, Any]` → `dict[str, Any]`, and it states plainly that the change has no effect on installing or using typsphinx. It does not name `v0.9.4`, `0.9.4`, `v0.9.3` or `0.9.3` anywhere in the prose, because no release carries those numbers.

- **D-02: The bullet says nothing about the Japanese site or its translation catalogs. REL-13 and ROADMAP SC#2 carry an AMENDED block recording this.** The owner chose to drop the sentence, not correct it. The literal clause ("the ja translation catalogs pick it up at the next published release") was falsified by measurement (see the domain section). The ja `latest` site follows `main` within about a day through the daily `update-pin.yml` schedule, not at a release. The ja API reference is untranslated (0/668), so it shows the same English type text the en bullet already describes. The AMENDED blocks were appended in the same commit as this CONTEXT, before the phase's fence baseline. **No Phase 71 plan writes `.planning/REQUIREMENTS.md`.** `grep` for `ja`, `Japanese` or `catalog` inside the new bullet must come back empty.

- **D-03: The bullet carries exactly one evidence sentence, saying that emitted Typst output and runtime behaviour are unchanged.** It cites the byte-identical `.typ` output over the test-fixture corpus, the leg (d) result. Any number in it (the project count, for instance) is transcribed from `70-AFTER-RUNTIME-EVIDENCE.md` / `70-CORPUS-DOCS-BASE-EVIDENCE.md` at execution time, never from this file. It does not enumerate the five QUA-12 legs, and it does not cite pytest or mypy figures. This matches v0.9.3's one-sentence evidence register ("A CI run … was green across the Linux, Windows and macOS test lanes").

- **D-04: Everything else in `CHANGELOG.md` is byte-identical.** That covers the three v0.9.3 bullets, the `### Planned for Future Releases` block, every versioned section and the tail link block. The `[Unreleased]` compare base stays `v0.9.2`. There is no `### Verified` subsection and no lead paragraph under `## [Unreleased]` (Phase 69 D-04: the next release-prep phase authors those when it promotes the bullets). `scripts/extract_changelog_section.py` is not run for a new section.

### Bringing `main` in, and the PR at close

- **D-05: The milestone branch does not absorb `main` inside this phase. Today there is nothing to absorb.** `origin/main` equals the merge-base (`d14ca458`), measured. SC#3's non-committing trial merge is still run at execution time and transcribed verbatim: `git fetch origin`, then `git merge-tree --write-tree HEAD origin/main` (exit code and tree SHA), `uv lock --check` on that tree's `pyproject.toml` + `uv.lock` extracted to scratch, and `ruff check .` on the merged tree at the merged lock's `ruff` version. It catches the case constraint 4 names, a `main` that moved (a dependabot `ruff` bump, say) between now and execution. Nothing from it is committed.

- **D-06 — `71-HANDOFF.md`'s branch-update step is conditional, because `main` is `strict: true`.** If `origin/main` has moved past the merge-base when `/gsd-complete-milestone` runs, merge it into the canonical milestone branch with a merge commit (never a rebase), push, and re-check. Otherwise the step is a recorded no-op. Then:
  1. Open the PR from `gsd/v0.9.4-typing-modernization` to `main`.
  2. Wait for the six required checks, named literally as in the domain section, to be green on the head.
  3. Merge with a merge commit, the method #135, #136 and #143 used.

- **D-07: `71-HANDOFF.md` opens by stating the negative.** It publishes nothing: no tag, no PyPI upload, no GitHub Release, no version bump. The `update-pin.yml` dispatch and the Read the Docs `stable` check are not applicable. The handoff also records, as a fact and not a step, that the daily `update-pin.yml` schedule will move ja `latest` onto the merged `main` without any action. ja `stable` is unchanged, because it follows the translations repository's tags. It lists the observations REL-13 is checked on after the merge (SC#4): the merge commit on `origin/main`, `pyproject.toml` still `0.9.2`, no `v0.9.4` tag, PyPI 404 for `0.9.4`, and no `v0.9.4` Release.

- **D-08: The `0.9.3` and `0.9.4` version numbers are both recorded as unclaimed, not decided.** After this phase `## [Unreleased]` holds two unpublished milestones' bullets (three from v0.9.3 plus this one). The handoff states that the next release-prep phase promotes all four into its versioned section, the Phase 61 → 63 mechanism. Whether the next published release is `0.9.3`, `0.9.4` or something else belongs to that milestone's scoping.

### Mechanics that bind every plan

- **D-09: The fence is `71-CLOSEOUT-GUARD.md`, reusing the `69-CLOSEOUT-GUARD.md` procedure.** At phase head it records `sha256sum`, `wc -l`, `git rev-parse HEAD` as this phase's own `PHASE_BASE_SHA`, and `grep -n 'REL-13' .planning/REQUIREMENTS.md`. The phase head is after D-02's AMENDED commit. The same commands re-run and MATCH at phase close, and once more after `phase.complete`-family tooling has run, including `/gsd-verify-work`'s inline transition. A flip is reverted with `git checkout -- .planning/REQUIREMENTS.md` and reported, never committed. Every plan's `SUMMARY.md` declares `requirements-completed: []`. SHA-256 is the primary probe, because a flip leaves `wc -l` unchanged.

- **D-10: One CI dispatch on the phase's final tip, after the branch is pushed.** First re-check for a decoy per constraint 9 (none exists today). If a decoy appears, advance the canonical pointer before deleting it. Push only the canonical branch. Then run `gh workflow run CI --ref gsd/v0.9.4-typing-modernization` and wait for it to finish. Transcribe every job conclusion literally, name both `windows-latest` and both `macos-latest` lanes, and read `ruff`'s verdict from `Lint and Format Check` (step `Run lint with tox`). No plan triggers `release.yml`. A second dispatch is justified only if a later plan lands a code-affecting change.

- **D-11: SC#1's "no code change slipped in" has two parts.**
  1. `git diff --stat <Phase 70's final code commit>..HEAD -- typsphinx/ tests/` is empty on the close tip.
  2. Phase 70's masked-AST harness re-runs on the close tip against Phase 70's `PHASE_BASE_SHA` (`697a1132…`) for the converted files, and the hashes equal.

  The remote probes (tags `v0.9.3` / `v0.9.4`, PyPI, GitHub Release) each carry a positive control against the existing `v0.9.2`.

- **D-12: Dependabot PRs.** None is open today. If one opens during the phase, it is named in `71-HANDOFF.md` and left untouched (Phase 69 D-10). A `ruff` bump merged to `main` meanwhile is caught by D-05's trial merge, and its count is authoritative (constraint 4).

### Claude's Discretion

- The exact prose of the bullet, within D-01..D-03.
- Plan decomposition, waves, and evidence-file naming, following the Phase 69 set: `71-CLOSEOUT-GUARD.md`, `71-CHANGELOG-EVIDENCE.md`, `71-PREFLIGHT-EVIDENCE.md`, `71-GREEN-TREE-EVIDENCE.md`, `71-CI-EVIDENCE.md`, `71-HANDOFF.md`, plus an SC#1 invariants file. `71-VERIFICATION.md` is reserved for the verifier and must not be plan-authored.
- How D-11's masked-AST re-run is invoked, as long as it is the Phase 70 mask (annotation subtrees plus `typing` / `collections.abc` `ImportFrom`) and non-vacuous.
- The docs warning baselines for SC#3, provided both come from a clean build (`rm -rf docs/_build` first).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase contract
- `.planning/ROADMAP.md` § "Phase 71: v0.9.4 Close Prep (prep-only, unpublished)": the goal, SC#1..SC#4, and SC#2's AMENDED block.
- `.planning/ROADMAP.md` § "🚧 v0.9.4 — Typing Modernization (ACTIVE)": constraints 4 (dependabot `ruff` bump / trial merge), 8 (CI lint authority), 9 (branch census and decoy), 10 (checksum fence), 11 (worktree isolation; the CHANGELOG page gate's zero-skip reading needs the `docs` extra), 12 (standing invariants).
- `.planning/REQUIREMENTS.md`: REL-13 verbatim with its AMENDED block, and the Traceability note that REL-13 maps here for coverage only.

### Precedent (v0.9.3's close prep, the same shape)
- `.planning/milestones/v0.9.3-phases/69-v0-9-3-close-prep-prep-only-unpublished/69-CONTEXT.md`: D-01..D-14, the carried-forward decisions.
- `.planning/milestones/v0.9.3-phases/69-v0-9-3-close-prep-prep-only-unpublished/69-CLOSEOUT-GUARD.md`: the fence procedure to reuse.
- `.planning/milestones/v0.9.3-phases/69-v0-9-3-close-prep-prep-only-unpublished/69-HANDOFF.md`: the handoff structure (negative-first, strict-protection update step, merge commit).
- `.planning/milestones/v0.9.3-phases/69-v0-9-3-close-prep-prep-only-unpublished/69-PREFLIGHT-EVIDENCE.md`: the `merge-tree` + `git archive` + `uv lock --check` pre-flight transcript shape.
- `.planning/milestones/v0.9.3-phases/69-v0-9-3-close-prep-prep-only-unpublished/69-CHANGELOG-EVIDENCE.md`, `69-GREEN-TREE-EVIDENCE.md`, `69-CI-EVIDENCE.md`, `69-SC1-INVARIANTS.md`: evidence shapes.

### What the bullet describes (Phase 70 evidence)
- `.planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-AFTER-RUNTIME-EVIDENCE.md`: legs (b) and (d); the source of any number D-03 cites.
- `.planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-CORPUS-DOCS-BASE-EVIDENCE.md`: the leg (d) corpus as enumerated at the base.
- `.planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-DOCS-DIFF-EVIDENCE.md`: DOC-23, the API-reference type-text change the bullet names.
- `.planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-BASELINE-EVIDENCE.md`: `PHASE_BASE_SHA` for D-11.
- `.planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-MASK-PILOT-EVIDENCE.md` and `70-AFTER-STATIC-EVIDENCE.md`: the masked-AST harness D-11 re-runs.
- `.planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-CI-EVIDENCE.md`: Phase 70's CI run, the comparison point for this phase's run.

### Files this phase edits or reads
- `CHANGELOG.md:8-36` (`## [Unreleased]` → `### Changed`, append after the third bullet), `:37` (Planned block, untouched), `:1324` (`[Unreleased]` tail link, untouched).
- `pyproject.toml:7`: must still read `0.9.2` (read only).
- `docs/source/changelog.rst`: includes `CHANGELOG.md`, which makes the bullet published text.
- `tests/test_changelog_page_gate.py`: needs `myst_parser` (the `docs` extra) and skips in a `--extra dev` worktree venv.
- `.github/workflows/ci.yml`: the `workflow_dispatch` route, the 3-OS matrix and `Lint and Format Check`. `release.yml` is never triggered.
- `CLAUDE.md` § "Worktree-isolated execution": mandatory per-worktree `uv sync` + `uv run`.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- The 61/63/69 `CLOSEOUT-GUARD.md` procedure, the only measure that has caught the release-requirement flip.
- `git merge-tree --write-tree` + `git archive <tree> pyproject.toml uv.lock` into scratch + `uv lock --check`, which measures the merge result without touching the branch (Phase 69 D-07).
- Phase 70's masked-AST `sk()`-shaped harness with the annotation + `typing`/`collections.abc` import mask.

### Established Patterns
- Bold-lead bullets with trailing requirement IDs under `### Changed`, one plain "no effect on installing or using typsphinx" sentence, and at most one evidence sentence (the three v0.9.3 bullets at `CHANGELOG.md:12-35`).
- Evidence is transcribed verbatim in `71-{TOPIC}-EVIDENCE.md`, using bare `KEY = value` lines with no trailing prose wherever a verify step extracts them.
- Remote probes (tag, PyPI, GitHub Release) each carry a positive control against `v0.9.2`.

### Integration Points
- `CHANGELOG.md` is the only product-tree file this phase authors. Everything else lands under `.planning/phases/71-*/`.
- `docs-html` and `docs-pdf` consume `CHANGELOG.md`, so a malformed MyST bullet shows up as a new docs warning against the clean-build baseline.
- The main checkout's `uv sync --extra dev` drops the `docs` extra. Restore it with `--extra dev --extra docs` before the docs tox environments and the zero-skip changelog gate run there.

</code_context>

<specifics>
## Specific Ideas

- **Draft bullet shape** (wording at discretion): "**Type annotations in typsphinx's source now use builtin generics (QUA-09, QUA-11, QUA-12, DOC-22, DOC-23).** … the API reference now shows `dict[str, Any]` where it showed `Dict[str, Any]` … The Typst output typsphinx generates is unchanged: … byte-identical … This has no effect on installing or using typsphinx."
- `phase.complete` has flipped the release requirement at eight release-prep closes, and `/gsd-verify-work` reaches it through its inline transition. Back up REQUIREMENTS / ROADMAP / STATE to scratch before either runs.

</specifics>

<deferred>
## Deferred Ideas

- Choosing the next published version number (`0.9.3` / `0.9.4` / other) belongs to the next milestone's scoping (D-08).
- The REQUIREMENTS Out of Scope row "ja translation catalog resync — happens at the next published release" carries the same timing error D-02 measured. It is noted in REL-13's AMENDED block and left for the milestone-close archive, not edited separately.

### Reviewed Todos (not folded)
- `2026-08-16-root-toctree-duplicates-section-children-in-html-sidebar.md`: DOC-18, a Future Requirement; docs structure, unrelated to close prep.
- `2026-07-22-add-sphinx-linkcheck-ci-job.md`: QUA-08; a workflow edit, forbidden by constraint 12.
- `2026-08-14-numref-number-diverges-per-master-and-vanishes-for-non-root-only-figures.md`: NUM-01; a `typsphinx/` change, which SC#1 forbids here.
- `2026-08-29-hardcoded-delimiter-path-fragments-in-translator-relative-path-debug-logs.md`: MSG-06; a `typsphinx/` change, constraint 12.
- `2026-09-13-doctest-block-unhandled-collapses-examples-to-one-line.md`: TRN-01; a `typsphinx/` change.

</deferred>

---

*Phase: 71-v0-9-4-close-prep-prep-only-unpublished*
*Context gathered: 2026-09-13*
