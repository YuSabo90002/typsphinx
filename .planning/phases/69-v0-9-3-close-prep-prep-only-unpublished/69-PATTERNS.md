# Phase 69: v0.9.3 Close Prep (prep-only, unpublished) - Pattern Map

**Mapped:** 2026-09-13
**Files analyzed:** 9 (1 product-tree file, 8 phase-directory evidence/handoff files)
**Analogs found:** 9 / 9

This phase produces no new source code. Every file is either a CHANGELOG edit or a `.planning/`
evidence/handoff document, so "role" below is repurposed to the project's own maintenance-surface
vocabulary (per 69-RESEARCH.md's Architectural Responsibility Map) rather than
controller/service/component. All analogs are git-TRACKED source — every path below was verified
with `git ls-files` before being named; none is a `.gsd/capabilities/` mirror.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `CHANGELOG.md` (edit, `## [Unreleased]` block only) | config/documentation | transform (prose insert, structural invariants preserved) | `.planning/milestones/v0.9.1-phases/61-v0-9-1-release-prep-prep-only/61-CHANGELOG-EVIDENCE.md` (procedure) + `CHANGELOG.md`'s own `## [0.4.4]`/`## [0.5.0]` sections (bullet prose style) | exact |
| `69-CLOSEOUT-GUARD.md` | test/audit (fence) | request-response (read-measure-compare, three observations) | `.planning/milestones/v0.9.2-phases/63-v0-9-2-release-prep-prep-only/63-CLOSEOUT-GUARD.md` (most recent, caught the 7th flip) | exact |
| `69-CHANGELOG-EVIDENCE.md` | test/audit | transform (before/after grep counts) | `61-CHANGELOG-EVIDENCE.md` | exact |
| `69-SC1-INVARIANTS.md` | test/audit | pub-sub / remote-probe (positive-controlled) | `.planning/milestones/v0.9.1-phases/61-v0-9-1-release-prep-prep-only/61-SC4-INVARIANTS.md` | exact |
| `69-GREEN-TREE-EVIDENCE.md` | test/audit | batch (full local suite transcription) | `.planning/milestones/v0.9.1-phases/61-v0-9-1-release-prep-prep-only/61-GREEN-TREE-EVIDENCE.md` | exact |
| `69-CI-EVIDENCE.md` | test/audit | event-driven (push -> dispatch -> wait -> transcribe) | `.planning/phases/65-tox-uv-bare-tox-uv-revert-on-the-uv-path-tox-actually-resolves/65-CI-EVIDENCE.md` | exact |
| D-07 pre-flight evidence file (name at plan discretion, e.g. `69-PREFLIGHT-EVIDENCE.md`) | test/audit | transform (non-committing trial merge + lock check) | 69-RESEARCH.md § "Code Examples" § Pattern 3 (D-07, already executed once this session) — no phase file precedent exists yet since D-07 is new to this phase; closest structural analog is `65-REVERT-EVIDENCE.md`'s "before/after" transcription shape | role-match (mechanism is new to the project, transcription shape is precedented) |
| `69-HANDOFF.md` | documentation (handoff) | request-response (single terminal artifact for a human operator) | `.planning/milestones/v0.9.1-phases/61-v0-9-1-release-prep-prep-only/61-HANDOFF.md` (same polarity: unpublished close, negative-first opening) | exact |
| `COVERAGE.md` | documentation (traceability) | transform (requirement-to-evidence mapping) | Precedent phases' own requirement-closure tables embedded in evidence files (e.g. `65-CI-EVIDENCE.md` § "Requirement closure"); no phase names a standalone `COVERAGE.md` in the 61/63 precedent — check current `.planning/phases/69-*/` directory at plan time for a `COVERAGE.md` template if the GSD tooling generates one automatically | role-match |

## Pattern Assignments

### `CHANGELOG.md` (documentation, transform)

**Analog A — placement procedure:** `61-CHANGELOG-EVIDENCE.md` (full file read).

**Pre-edit measurement pattern** (61-CHANGELOG-EVIDENCE.md lines 5-22):
```
$ git rev-parse HEAD
$ grep -cE '^## \[' CHANGELOG.md
$ grep -cE '^\[[^]]+\]: https' CHANGELOG.md
$ tail -1 CHANGELOG.md
$ awk '/^## \[Unreleased\]/,/^## \[<prior-version>\]/' CHANGELOG.md | grep -cE '^- \*\*'
```
Adapt the `awk` upper bound to the current tree's first versioned heading below `[Unreleased]`
(currently `## [0.9.2]`, per RESEARCH.md's measured `CHANGELOG.md:8-14`) — re-measure, do not copy
`v0.9.0` from the Phase 61 excerpt.

**Bullet shape to copy (bold-lead + trailing requirement-ID parens, house style since Phase 33)**,
verbatim from `61-CHANGELOG-EVIDENCE.md`'s "PATH-01 bullet" section:
```markdown
### Fixed

- **A Windows-shaped `typst_documents` target that reaches outside the output directory is now
  refused on the normalized path, matching its sibling image-URI check (PATH-01).** The
  `typst_documents` escape predicate now applies its absolute-path and drive-qualified checks to
  the same backslash-normalized string its sibling image-URI predicate already used...
```
Phase 69 uses `### Changed` (per D-01), not `### Fixed` — this excerpt is the bold-lead-sentence
+ trailing-parenthetical-ID mechanics to copy, not the heading name.

**Analog B — grouped-heading `### Changed` prose precedent for tooling-only work**, from
`CHANGELOG.md` itself (`## [0.4.4]`, read directly):
```markdown
### Changed

- **CI/Release Durability**
  - Python support floor raised to 3.10-3.13, with the CI and tox test matrices reconciled to match
  - `softprops/action-gh-release` bumped from `v2` to `v3` in the release workflow
```
D-01 calls for the flatter "one bullet per track, bold lead phrase, IDs in trailing parens" shape
(Analog A), not this nested sub-bullet grouping — cite Analog B only as evidence that `### Changed`
is the established heading for tooling-only milestones, per CONTEXT's own precedent citation.

**Placement (D-03):** insert the new `### Changed` block immediately after `## [Unreleased]`
(line 8) and before the existing `### Planned for Future Releases` (line 10) — do not touch the
tail link-reference block (`[Unreleased]: …/compare/v0.9.2...HEAD`, currently around line 1297).

**Post-edit fence pattern** (61-CHANGELOG-EVIDENCE.md "Fence assertions after the bullet landed"):
```
$ grep -cE '^## \[' CHANGELOG.md          # unchanged from pre-edit
$ grep -cE '^\[[^]]+\]: https' CHANGELOG.md # unchanged from pre-edit
$ tail -1 CHANGELOG.md                     # byte-identical
$ awk '/^## \[Unreleased\]/,/^## \[<prior>\]/' CHANGELOG.md | grep -cE '^- \*\*'  # +3 (three bullets)
$ git status --porcelain typsphinx/ tests/  # empty
```

---

### `69-CLOSEOUT-GUARD.md` (test/audit, request-response fence)

**Analog:** `.planning/milestones/v0.9.2-phases/63-v0-9-2-release-prep-prep-only/63-CLOSEOUT-GUARD.md`
(most recent, seventh flip caught) — structurally identical to `61-CLOSEOUT-GUARD.md` (read in full
above); reuse the Phase 61 shape verbatim since Phase 69 has a single requirement (REL-12), matching
Phase 61's single-requirement (REL-09) shape rather than Phase 63's multi-requirement blast-radius
case.

**Baseline section** (61-CLOSEOUT-GUARD.md lines 1-24, copy structure, substitute REL-12):
```markdown
# Phase 69 — REL-12 Checkbox-Flip Closeout Guard

This task changes NO requirement state: REL-12 stays an unchecked box (`- [ ]`) and its
Traceability row stays `Pending`. `.planning/REQUIREMENTS.md` is read and quoted here and never
edited.

## Baseline

$ sha256sum .planning/REQUIREMENTS.md
$ wc -l .planning/REQUIREMENTS.md
$ date -u +"%Y-%m-%dT%H:%M:%SZ"
$ git rev-parse HEAD          # -> PHASE_BASE_SHA

**PHASE_BASE_SHA:** <value>
```

**Lines-under-guard section** — `grep -n 'REL-12' .planning/REQUIREMENTS.md`, expect the checkbox
bullet line, the Traceability row, and (if present) a phase-totals line, quoted byte-for-byte, same
three-line shape as 61-CLOSEOUT-GUARD.md's REL-09 lines 127/206/220.

**Why this file exists section** — copy the running-count framing: 63-CLOSEOUT-GUARD.md's own
count (the flip landed at "seven consecutive" release-prep closes counting through Phase 63);
Phase 69 continues that count.

**Re-verification protocol + post-close detection sections** — copy 61-CLOSEOUT-GUARD.md's exact
three-command block (sha256sum / `git diff --name-only` / `grep -n`) reproduced twice: once for
"phase close" and once for "after phase.complete runs," with the explicit instruction
`git checkout -- .planning/REQUIREMENTS.md` on divergence, never a commit of the flip. Per Pitfall
2 (RESEARCH.md), state explicitly that the guard applies to **every** transition entry point
(`phase.complete` directly, and `/gsd-verify-work`'s inline auto-transition) — 63-CLOSEOUT-GUARD.md
is the file that discovered and documents this second entry point; read its own "why this file
exists"-equivalent section for the exact wording to adapt.

---

### `69-CHANGELOG-EVIDENCE.md` (test/audit, transform)

**Analog:** `61-CHANGELOG-EVIDENCE.md` (full file read above).

Copy its four-part structure:
1. "This plan's base SHA" (`git rev-parse HEAD`)
2. "Pre-edit measurements" (the `grep`/`tail`/`awk` block, § CHANGELOG.md pattern above)
3. The bullet(s) themselves, with an "Accuracy basis" paragraph citing each requirement ID's
   `.planning/REQUIREMENTS.md` traceability note (Phase 69's is TOX-01..04, DEP-01..05,
   NIX-01..08, DOC-19..21 — cite the phases that satisfied them: 64, 65, 66, 67, 68)
4. "Fence assertions after the bullet landed" (post-edit re-run of the same grep/tail/awk block,
   plus `git status --porcelain typsphinx/ tests/` empty)

Also copy the "Docs render" subsection (61-CHANGELOG-EVIDENCE.md, further down the file, not fully
quoted above but present per the Read): a clean-build docs comparison (`rm -rf docs/_build` first,
per Pitfall 6/D-21 precedent) run with `--extra dev --extra docs` synced (Pitfall 5/7).

---

### `69-SC1-INVARIANTS.md` (test/audit, remote-probe)

**Analog:** `.planning/milestones/v0.9.1-phases/61-v0-9-1-release-prep-prep-only/61-SC4-INVARIANTS.md`
(named per that phase's own SC numbering — Phase 69 uses `SC1` since ROADMAP maps the
no-irreversible-action fence to SC#1 here, per RESEARCH.md's Open Question 2 recommendation).

**Positive-control probe pattern**, from RESEARCH.md § Pattern 2 (itself extracted live from this
project's own commands, reusable verbatim):
```bash
$ git ls-remote --tags origin 'v0.9*'
# expect v0.9.0, v0.9.2 present (positive control); v0.9.3 absent (the claim)

$ curl -s -o /dev/null -w "%{http_code}\n" https://pypi.org/pypi/typsphinx/0.9.2/json   # expect 200
$ curl -s -o /dev/null -w "%{http_code}\n" https://pypi.org/pypi/typsphinx/0.9.3/json   # expect 404

$ gh release list --limit 5
# expect v0.9.2 "Latest"; no v0.9.3 row
```
Two separated-in-time observations, each pairing every negative probe with a positive control from
the same fetch (never trust an unreachable endpoint as a clean negative). Also include the
`typsphinx/` diff-emptiness check against `origin/main`'s merge-base, and (per 61-SC4-INVARIANTS.md
precedent) a widened positive control proving the scoped diff mechanism itself is non-vacuous
(e.g., confirm `CHANGELOG.md` DOES show a diff once this phase's edit lands).

---

### `69-GREEN-TREE-EVIDENCE.md` (test/audit, batch)

**Analog:** `.planning/milestones/v0.9.1-phases/61-v0-9-1-release-prep-prep-only/61-GREEN-TREE-EVIDENCE.md`
(cited in 61-HANDOFF.md § SC#3: "full pytest suite (1513 passed, 5 skipped), `black --check`,
`mypy`, and the version-sync guard family").

Copy the shape: "Provisioning and tree identity" section (worktree `uv sync --extra dev` +
`uv run` per CLAUDE.md), then one subsection per tool — `pytest`, `black --check .`, `mypy
typsphinx/` — each with the raw command and its exit code / pass-fail counts, plus an "Executed
versus skipped" accounting (Pitfall 5: report PASSED counts with zero SKIPPED when `--extra docs`
is synced, not the bare exit code). Include both `docs-html` and `docs-pdf` tox environments from a
clean `rm -rf docs/_build` build (Pitfall 6, D-21 precedent).

---

### `69-CI-EVIDENCE.md` (test/audit, event-driven)

**Analog:** `.planning/phases/65-tox-uv-bare-tox-uv-revert-on-the-uv-path-tox-actually-resolves/65-CI-EVIDENCE.md`
(full file read above) — the most complete, most recent push+dispatch+wait+transcribe idiom in
this project, already run against this exact branch.

**Push pattern** (65-CI-EVIDENCE.md § "Push"):
```bash
$ git fetch origin gsd/v0.9.3-toolchain-and-dependency-update-repair
$ git ls-remote --heads origin refs/heads/gsd/v0.9.3-toolchain-and-dependency-update-repair
# -> ORIGIN_BEFORE
$ git merge-base --is-ancestor <ORIGIN_BEFORE> HEAD; echo "exit:$?"   # expect exit:0
$ date -u +%FT%TZ   # -> PUSH_AT
$ git push -u origin gsd/v0.9.3-toolchain-and-dependency-update-repair
# no --force, no tags, no other ref
$ git ls-remote --heads origin refs/heads/gsd/v0.9.3-toolchain-and-dependency-update-repair
# -> remote head now equals PUSHED_SHA
```

**Dispatch pattern** (65-CI-EVIDENCE.md § "Dispatch"):
```bash
$ gh workflow run CI --ref gsd/v0.9.3-toolchain-and-dependency-update-repair
$ gh run list --workflow=ci.yml --branch gsd/v0.9.3-toolchain-and-dependency-update-repair \
    --event workflow_dispatch --limit 5 --json databaseId,headSha,status,createdAt,url
# match the listed row's headSha == PUSHED_SHA, and createdAt > PUSH_AT
```

**Wait pattern:** `gh run watch <id> --interval 30` in the foreground (Bash timeout up to 600000ms,
no `run_in_background`), then:
```bash
$ gh run view <id> --json status,conclusion,workflowName,headSha,url
# status: completed, conclusion: success, headSha == PUSHED_SHA
```

**Job census pattern (all 12 jobs, not just the 6 required ones — Pitfall 11)**:
```bash
$ gh run view <id> --json jobs --jq '.jobs[] | [.name, .conclusion] | @tsv'
```
Transcribe all 12 rows into a table (copy 65-CI-EVIDENCE.md's exact table shape), then separate
tables/call-outs naming both `windows-latest` lanes and both `macos-latest` lanes individually
(D-13's literal text).

**ruff verdict pattern** — read from the `Lint and Format Check` job's `Run lint with tox` step
specifically (Pitfall 10: never `release.yml`'s differently-named lint step), quoting the raw
`black --check .` / `ruff check .` output verbatim, then a comparison table against the local run
recorded in `69-GREEN-TREE-EVIDENCE.md` (same shape as 65-CI-EVIDENCE.md's own comparison table).

**Dispatch-count and no-release-workflow guards** — copy the closing two sections verbatim-in-shape:
`gh run list --workflow=ci.yml ... --json headSha` showing exactly one row with `headSha ==
PUSHED_SHA`; `gh run list --workflow=release.yml --limit 5 --json headSha` showing no row matching
`PUSHED_SHA`.

---

### D-07 pre-flight evidence file (test/audit, transform — new mechanism, precedented transcription)

**Analog:** No prior phase file performs exactly this; the mechanism itself was already executed
once, read-only, in 69-RESEARCH.md § "Code Examples" § "Pattern 3: D-07's non-committing trial-merge
pre-flight" — copy that transcript's command sequence and re-run fresh (Pitfall 1: the tree SHA
moves every session, never copy a prior session's value):
```bash
$ git fetch origin
$ git merge-tree --write-tree HEAD origin/main    # -> tree SHA; rc 0 means no conflict
$ echo "rc=$?"

$ mkdir -p <scratch-dir>
$ git archive <tree-sha> pyproject.toml uv.lock | tar -x -C <scratch-dir>
$ cd <scratch-dir> && uv lock --check
# expect: "Resolved N packages" with exit 0, no drift

$ grep -n '^version' pyproject.toml     # must still read 0.9.2 (D-11)
$ grep -n '^name = "ruff"' -A2 uv.lock  # cite the merged lock's ruff version (0.16.6 at research time)
```
Structural transcription analog for the "before/after, verbatim, reproducible" evidence shape:
`.planning/phases/65-tox-uv-bare-tox-uv-revert-on-the-uv-path-tox-actually-resolves/65-REVERT-EVIDENCE.md`
(same idiom — raw commands, raw output, no paraphrase).

Note per D-07/A2 (RESEARCH.md Assumptions Log): the optional `ruff check .` run on the merged tree
via `typsphinx-fhs-run uvx --from ruff==<merged-version>` is Claude's discretion — include only if
time permits; omitting it fails nothing.

---

### `69-HANDOFF.md` (documentation, request-response)

**Analog:** `.planning/milestones/v0.9.1-phases/61-v0-9-1-release-prep-prep-only/61-HANDOFF.md`
(full file read above) — same polarity as Phase 69 (unpublished close), unlike Phase 63's handoff
which opens with a positive publish checklist.

**Opening (D-09, negative-first — but corrected for D-08's PR step)**, copy 61-HANDOFF.md's exact
opening shape:
```markdown
**This milestone publishes nothing.** ... no tag (local or remote), no PyPI publish, no GitHub
Release, no version bump. [UNLIKE Phase 61: state explicitly that a PR to `main` IS opened and
merged at `/gsd-complete-milestone` — REL-12 — naming precisely which publish actions are absent
while retaining the PR-merge step.]
```
This is the one place Phase 69 must NOT copy 61-HANDOFF.md verbatim — RESEARCH.md's "Code Examples
§ Handoff shape to reproduce" section explicitly flags this correction.

**"What this phase satisfied, and what it did not" section** — copy 61-HANDOFF.md's per-SC
reporting shape (quote each SC verbatim from ROADMAP, mark MET/DROPPED/REWORDED/RETAINED, cite the
deciding evidence file + section for each, never re-derive the verdict inline).

**Branch-update step (D-08)** — new to Phase 69 (Phase 61 had no `main`-absorption step since it
never opened a PR); no direct precedent file section exists, but 61-HANDOFF.md's "What the v0.9.2
milestone inherits" § "1. The second-repository tag" subsection is the closest shape template (an
ordered command sequence with an explicit rationale paragraph before it) — adapt to: merge
`origin/main` into the canonical branch with a merge commit (never rebase) -> push -> open PR ->
wait for 6 named required checks green -> merge with a merge commit (cite `#135`/`#136` as the
"Merge pull request" precedent per D-08).

**Items recorded without acting (D-10, D-11)** — copy 61-HANDOFF.md's "What this phase deliberately
did not do" closing checklist shape (bullet list of explicit non-actions), adapted to name
dependabot PRs #139-#142 by number and state the `0.9.3` version number is unclaimed.

**Fence reproduction section** — copy 61-HANDOFF.md's "Before declaring the milestone closed"
section verbatim-in-shape: reproduce the `69-CLOSEOUT-GUARD.md` three-command block inline so the
operator never needs to open that file separately, and a live final fence observation at the
handoff's own write-time (61-HANDOFF.md § "Fence observation").

**Closing "what this phase deliberately did not do" list** — copy 61-HANDOFF.md's exact bullet
inventory shape (no tag / no release.yml real run / nothing to PyPI / no GitHub Release / no
REQUIREMENTS.md flip / no public disclosure), adding "no `origin/main` merge into the branch inside
this phase" (D-06) as an explicit item since D-08's branch-update step is deferred to
`/gsd-complete-milestone`, not performed here.

---

### `COVERAGE.md` (documentation, transform)

No standalone `COVERAGE.md` file exists in the 61 or 63 precedent directories (verified: `ls` of
both phase directories shows no such file) — this is a naming choice new to Phase 69's own directory
listing in CONTEXT's Claude's-Discretion note. Build it as a requirement-to-evidence traceability
table, the same shape every evidence file's own "Requirement closure" section already uses (e.g.
`65-CI-EVIDENCE.md`'s closing table: `| Requirement | Status | Deciding section |`) — one row per
requirement this phase's evidence touches (REL-12 only, status `FENCED, not closed`, deciding
section `69-CLOSEOUT-GUARD.md`), plus a row per already-satisfied requirement being cited for the
CHANGELOG bullets (TOX-01..04, DEP-01..05, NIX-01..08, DOC-19..21), each pointing at its owning
phase's own evidence.

## Shared Patterns

### The three-command checksum fence (applies to `69-CLOSEOUT-GUARD.md` and `69-HANDOFF.md`)
**Source:** `61-CLOSEOUT-GUARD.md` / `63-CLOSEOUT-GUARD.md`
```bash
sha256sum .planning/REQUIREMENTS.md
git diff --name-only -- .planning/REQUIREMENTS.md   # expect: no output
grep -n 'REL-12' .planning/REQUIREMENTS.md          # expect: byte-identical to baseline
# on divergence:
git checkout -- .planning/REQUIREMENTS.md            # revert, report, never commit
```
Apply this identical block in three places: `69-CLOSEOUT-GUARD.md`'s own baseline-vs-close
comparison, and reproduced verbatim inside `69-HANDOFF.md` for the post-`phase.complete`
observation (Pitfall 2: state it covers every transition entry point, not just a manual
`phase.complete` call).

### Positive-control remote probing (applies to `69-SC1-INVARIANTS.md`)
**Source:** 69-RESEARCH.md § Pattern 2
Every "prove X is absent" probe (`git ls-remote --tags`, `curl` PyPI JSON endpoint, `gh release
list`) is paired with the same call against `v0.9.2` (known to exist) from the same fetch, so an
unreachable remote is never mistaken for a clean negative.

### Push -> dispatch -> wait -> transcribe (applies to `69-CI-EVIDENCE.md`)
**Source:** `65-CI-EVIDENCE.md` (full sequence above)
`git push` (no force/tags) -> `gh workflow run CI --ref <branch>` -> match the listed run's
`headSha` against `PUSHED_SHA` -> `gh run watch <id>` foreground -> `gh run view --json jobs` for
all 12 jobs -> `Lint and Format Check`'s `Run lint with tox` step for ruff's verdict -> a
dispatch-count guard proving exactly one `workflow_dispatch` run carries this tip's SHA -> a
no-`release.yml`-run guard.

### `KEY = value` evidence lines (applies to every evidence file)
**Source:** 65-CI-EVIDENCE.md's own header (`REVERT_SHA = ...`, `PUSHED_SHA = ...`, `RUN_ID =
...`) and RESEARCH.md Pitfall 4
Put the bare value alone on its own line (`PUSHED_SHA = d9c75553...`), with any explanatory prose on
a separate line — never trailing the value — so a verify step's `sed -n "s/^KEY = //p"` extraction
stays exact.

### Worktree provisioning (applies to every plan)
**Source:** `CLAUDE.md` § "Worktree-isolated execution", reproduced in 65-CI-EVIDENCE.md § "Head
check and provisioning"
```bash
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev
# run everything else via: uv run <command>
```
Any plan proving docs content or running `tests/test_changelog_page_gate.py`'s content-coverage
classes must instead sync `--extra dev --extra docs` explicitly (Pitfall 5/7) and report PASSED
counts with zero SKIPPED, not the bare exit code.

## No Analog Found

None — every file this phase produces has at least a role-match analog (the D-07 pre-flight file
and `COVERAGE.md` have no exact same-named prior file, but both have a directly reusable mechanism
or transcription-shape precedent, recorded above).

## Metadata

**Analog search scope:** `.planning/milestones/v0.9.1-phases/61-v0-9-1-release-prep-prep-only/`,
`.planning/milestones/v0.9.2-phases/63-v0-9-2-release-prep-prep-only/`,
`.planning/phases/65-tox-uv-bare-tox-uv-revert-on-the-uv-path-tox-actually-resolves/`,
`.planning/phases/66-github-dependabot-yml-pip-uv-ecosystem/`,
`.planning/phases/67-proof-on-a-real-dependabot-pr-then-disposal-of-123-and-128/`, root
`CHANGELOG.md`.
**Files scanned:** 61-CHANGELOG-EVIDENCE.md, 61-CLOSEOUT-GUARD.md, 61-HANDOFF.md,
63-CLOSEOUT-GUARD.md (partially, via prior research citation), 65-CI-EVIDENCE.md,
65-REVERT-EVIDENCE.md (cited), 66-DEPENDABOT-EVIDENCE.md / 66-MAIN-PR-EVIDENCE.md /
67-*-EVIDENCE.md (enumerated, not opened — same `KEY = value` idiom already confirmed via
65-CI-EVIDENCE.md), `CHANGELOG.md` `## [0.4.4]` / `## [0.5.0]` sections.
**Pattern extraction date:** 2026-09-13
