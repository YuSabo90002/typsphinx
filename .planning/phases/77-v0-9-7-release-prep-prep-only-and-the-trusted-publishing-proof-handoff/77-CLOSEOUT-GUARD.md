# Phase 77 — Closeout Guard (ATT-03, ATT-04, ATT-05, REL-17, DOC-25 fence)

This file changes no requirement state: the five guarded requirements — ATT-03, ATT-04, ATT-05,
REL-17 and DOC-25 — stay unchecked `- [ ]` boxes and their Traceability rows stay `Pending`.
`.planning/REQUIREMENTS.md` is read and quoted here, never edited — no plan in Phase 77 writes it.

## Head check and provisioning

- `date -u +%FT%TZ` -> `2026-09-28T13:07:46Z`
- `pwd -P` -> `/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a008a40c849ef1103` (under
  `/home/yuta/Documents/typsphinx/.claude/worktrees/`)
- `test -f .git; echo "exit:$?"` -> `exit:0` (worktree confirmed — `.git` is a file)
- `command -v uv` -> `/nix/store/3vpzk25whpm7s8zq5flpk8gbpkggj9np-uv/bin/uv`
- `grep -c typsphinx-fhs-run "$(command -v uv)"` -> `2`

Provisioning line:

```
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs
```

Exit status: `0`. `typsphinx==0.9.6` installed editable from this worktree's own checkout path,
along with `sphinx==9.1.0`, `myst-parser` (docs extra), `furo`, `tox==4.61.5`, `tox-uv==1.36.0` and
every other `docs`/`dev` extra dependency.

- `sed -n 's/^home = //p;s/^version_info = //p' .venv/pyvenv.cfg` ->
  `PYVENV_HOME` = `/home/yuta/.local/share/uv/python/cpython-3.14-linux-x86_64-gnu/bin`,
  `PYVENV_VERSION_INFO` = `3.14` — a fresh worktree resolves a uv-managed CPython 3.14 rather than
  the main checkout's nix-provided interpreter; both are otherwise compatible with this plan's
  tooling.

Key lines:

```
PYVENV_HOME = /home/yuta/.local/share/uv/python/cpython-3.14-linux-x86_64-gnu/bin
PYVENV_VERSION_INFO = 3.14
```

`mktemp -d /tmp/p7701.XXXXXX` -> `/tmp/p7701.p8Y5y6`.

```
SCRATCH_77_01 = /tmp/p7701.p8Y5y6
```

## Baseline

Recorded at phase head, inside this plan's isolated worktree (`worktree-agent-a008a40c849ef1103`),
before this plan's first commit.

```
$ git rev-parse HEAD
3984b231e30fbb76ba156d2f9b2abe475231bccf

$ git log -1 --format='%H %s'
3984b231e30fbb76ba156d2f9b2abe475231bccf docs(state): start phase 77 execution (wave 1 of 5)
```

Subject `docs(state): start phase 77 execution (wave 1 of 5)` — a phase-tracking commit that
predates this plan's own execution and carries no `(77-0N)` plan-level commit scope. No plan commit
has landed yet.

```
$ git fetch -q origin main && git merge-base HEAD origin/main
9fa1cb894137933f4dbb49d1668fc193e2ef1bc8

$ git rev-parse origin/main
eeba55aa9b62aecb208bf7abecb051b476592b66
```

`MILESTONE_BASE` confirmed by `git merge-base HEAD origin/main` after fetching `origin main`, and
matches the planning-time census exactly (`9fa1cb89…`). `origin/main` itself has moved past the
milestone base to `eeba55aa…` (three Dependabot merges recorded at planning) — this handoff re-reads
`origin/main` live rather than trusting this recorded SHA at any later step.

```
$ sha256sum .planning/REQUIREMENTS.md
35eb6122efd878cad4083a18b84c006f315c3cfe5229f3d443e6c712e6954351  .planning/REQUIREMENTS.md

$ wc -l .planning/REQUIREMENTS.md
189 .planning/REQUIREMENTS.md

$ grep -vE '^- \[.\] \*\*ATT-06\*\*|^\| ATT-06 \|' .planning/REQUIREMENTS.md | sha256sum
fce6cc7d403e4c68b4cf12a6e58bf990f94f9a5f7db2943ce9da2469953d4af5  -
```

The guarded-region digest is the SHA-256 of `.planning/REQUIREMENTS.md` with exactly ATT-06's two
state-bearing lines filtered out (its checkbox bullet and its traceability row), computed with the
verbatim command above so a later reader can re-run it byte-for-byte. This is the digest that
survives ATT-06's legitimate flip and still catches any other change.

```
$ grep -c 'ATT-03' .planning/REQUIREMENTS.md
6
$ grep -c 'ATT-04' .planning/REQUIREMENTS.md
3
$ grep -c 'ATT-05' .planning/REQUIREMENTS.md
5
$ grep -c 'REL-17' .planning/REQUIREMENTS.md
3
$ grep -c 'DOC-25' .planning/REQUIREMENTS.md
3
$ grep -c 'ATT-06' .planning/REQUIREMENTS.md
4
```

All six counts agree digit-for-digit with the `77-01-PLAN.md` frontmatter's own planning-time
census (2026-09-28, HEAD `40c5e7e6`) — no drift occurred between planning and this plan's own
execution.

```
$ grep -c 'attestations input ignored' .planning/REQUIREMENTS.md
1
$ grep -c 'attestations input ignored' .planning/ROADMAP.md
3
```

Discretion A (`77-CONTEXT.md`) keeps both files' ATT-04 annotation-title wording literal and
unedited — this plan does not touch either file's prose, only records these counts. `77-08`
re-counts both at phase close.

```
$ git log -1 --format=%H -- .planning/REQUIREMENTS.md
428c58cfb6accd5c63820f8cc904af9bcf5bb8a0

$ git merge-base --is-ancestor 428c58cfb6accd5c63820f8cc904af9bcf5bb8a0 3984b231e30fbb76ba156d2f9b2abe475231bccf; echo "exit:$?"
exit:0

$ date -u +%FT%TZ
2026-09-28T13:08:09Z
```

`REQ_LAST_COMMIT` is confirmed an ancestor of `PHASE_BASE_SHA`.

Key lines:

```
PHASE_BASE_SHA = 3984b231e30fbb76ba156d2f9b2abe475231bccf
MILESTONE_BASE = 9fa1cb894137933f4dbb49d1668fc193e2ef1bc8
REQ_SHA256_BASE = 35eb6122efd878cad4083a18b84c006f315c3cfe5229f3d443e6c712e6954351
REQ_LINES_BASE = 189
REQ_SHA256_GUARDED_BASE = fce6cc7d403e4c68b4cf12a6e58bf990f94f9a5f7db2943ce9da2469953d4af5
ATT03_HITS_BASE = 6
ATT04_HITS_BASE = 3
ATT05_HITS_BASE = 5
REL17_HITS_BASE = 3
DOC25_HITS_BASE = 3
ATT06_HITS_BASE = 4
ATT04_LITERAL_REQ_HITS_BASE = 1
ATT04_LITERAL_ROADMAP_HITS_BASE = 3
REQ_LAST_COMMIT = 428c58cfb6accd5c63820f8cc904af9bcf5bb8a0
GUARD_AT = 2026-09-28T13:08:09Z
```

## The lines under guard

Verbatim output of `grep -n '<ID>' .planning/REQUIREMENTS.md`, run against this worktree's tree at
the timestamp above, for each of the five guarded IDs.

```
$ grep -n 'ATT-03' .planning/REQUIREMENTS.md
37:- [ ] **ATT-03**: The switch is proven on **PyPI's own served state** for the real 0.9.7 upload, not
51:      so its absence alone does not prove PyPI served provenance. ATT-03 is what proves that.
55:      ATT-03 passes**; until then the token is the rollback path. `TEST_PYPI_API_TOKEN` is left in
162:| ATT-03 | Phase 77 | publish (coverage only) | Pending |
183:→ ATT-03 (PyPI Simple JSON + Integrity APIs) → ATT-05 (both secret scopes + PyPI revocation, and
184:only once ATT-03 has passed) → DOC-25 (written after ATT-05, so it describes a state that is
```

```
$ grep -n 'ATT-04' .planning/REQUIREMENTS.md
47:- [ ] **ATT-04**: The v0.9.7 release run carries **zero** occurrences of the action's
161:| ATT-04 | Phase 77 | publish (coverage only) | Pending |
182:The publish half runs in a fixed order that `77-HANDOFF.md` enforces: tag push → ATT-04 (run log)
```

```
$ grep -n 'ATT-05' .planning/REQUIREMENTS.md
52:- [ ] **ATT-05**: `PYPI_API_TOKEN` is retired from **both** GitHub scopes — the repository-scoped
86:      ATT-01 and ATT-05 land.
163:| ATT-05 | Phase 77 | publish (coverage only) | Pending |
183:→ ATT-03 (PyPI Simple JSON + Integrity APIs) → ATT-05 (both secret scopes + PyPI revocation, and
184:only once ATT-03 has passed) → DOC-25 (written after ATT-05, so it describes a state that is
```

```
$ grep -n 'REL-17' .planning/REQUIREMENTS.md
75:- [ ] **REL-17**: 0.9.7 is published — `pyproject.toml` bumped as the **sole** version literal with
160:| REL-17 | Phase 77 | split — prep in phase, publish at close | Pending |
185:already true). REL-17's publish clauses are checked across the whole of it.
```

```
$ grep -n 'DOC-25' .planning/REQUIREMENTS.md
84:- [ ] **DOC-25**: `.planning/codebase/INTEGRATIONS.md:116-117` no longer describes `PYPI_API_TOKEN`
164:| DOC-25 | Phase 77 | publish (coverage only) | Pending |
184:only once ATT-03 has passed) → DOC-25 (written after ATT-05, so it describes a state that is
```

Six, three, five, three and three hits respectively — as expected from both the baseline probe and
the planning-time census.

**Classification:**

- **State-bearing:** the checkbox bullet line (`- [ ] **<ID>**: …`) and the traceability row
  (`| <ID> | Phase 77 | … | Pending |`) for each of the five IDs — line 37/162 (ATT-03), 47/161
  (ATT-04), 52/163 (ATT-05), 75/160 (REL-17), 84/164 (DOC-25). Only the leading `- [ ]` token of
  each bullet and the trailing `Pending |` of each row are what would change on a flip; the rest of
  each bullet's prose does not change shape merely because the box flips.
- **Informational:** every other hit above — mid-sentence continuation lines referencing an ID in
  prose (ATT-03's lines 51, 55, 183, 184; ATT-04's line 182; ATT-05's lines 86, 183, 184; REL-17's
  line 185; DOC-25's line 184). None of these carries a checkbox or a `Pending`/`Complete` token of
  its own, and none would change shape merely because a checkbox or row flipped elsewhere.

All ten state-bearing lines (two per guarded ID) must be byte-identical at every later observation:
each checkbox still reads `- [ ]` and each row still ends `Pending |`. The wrapped continuation
lines of the five checkbox bullets carry no ID token of their own on those wrapped lines and are
covered by `REQ_SHA256_GUARDED_BASE`, not by these transcripts individually.

## Expected to move: ATT-06

Verbatim output of `grep -n 'ATT-06' .planning/REQUIREMENTS.md`, run at the same timestamp:

```
$ grep -n 'ATT-06' .planning/REQUIREMENTS.md
57:- [ ] **ATT-06**: A rollback procedure is recorded before the tag is pushed, and names: restoring
147:  once the registration is fixed. That is cheaper than ATT-06's re-tag path and should be tried
159:| ATT-06 | Phase 77 | pre-tag | Pending |
179:before. ATT-06 is the one requirement Phase 77 legitimately closes, which is why the fence is
```

Four hits, matching the baseline probe and the planning-time census.

**Classification:** state-bearing — line 57 (the checkbox) and line 159 (the traceability row).
Informational — line 147 (a bullet in § Binding constraints mentioning ATT-06 in passing) and line
179 (the "ATT-06 is the one requirement Phase 77 legitimately closes" sentence in § Traceability).

ATT-06 closes inside this phase (D-04, `77-CONTEXT.md`: the rollback procedure recorded in
`77-HANDOFF.md` before any `v0.9.7` tag exists), so its checkbox and traceability row **may**
legitimately read `[x]` / `Complete` once phase-completion tooling runs. This is exactly why this
fence is line-scoped rather than whole-file: a whole-file digest would fire on ATT-06's own
legitimate completion, indistinguishable from an unwarranted flip of one of the five guarded IDs.
No plan in this phase edits `.planning/REQUIREMENTS.md` itself, so `REQ_SHA256_BASE` is expected to
MATCH at phase close and may change only after phase-completion tooling runs (confined to ATT-06's
two lines). `REQ_SHA256_GUARDED_BASE` is expected to MATCH at all three observations regardless of
whether ATT-06 has flipped.

## Why this file exists

`phase.complete`-family tooling, including `/gsd-verify-work`'s inline transition and
`/gsd-execute-phase`'s tail, has auto-flipped a deferred release checkbox against an explicit
CONTEXT decision at **9 of the 10** prior release-prep closes (`ROADMAP.md` — see the v0.9.6
precedent in `75-CLOSEOUT-GUARD.md`), and at the v0.9.6 close it flipped **both** the coverage-only
REL-15 and the legitimately closing REL-16 in one call — the same tooling call does not distinguish
between a coverage-only requirement and one the phase is actually meant to close. SHA-256 is the
primary probe rather than a scoped grep, because a checkbox flip is line-count-neutral — `- [ ]` and
`- [x]` are the same length, and a `Pending` → `Complete` traceability-row edit does not add or
remove a line, so `wc -l` alone cannot detect it; only a byte-level digest can. The same tooling
rewrote `STATE.md` fields including `current_phase_name` and mangled `ROADMAP.md`'s Status-cell
padding and wrapped list lines at that close — those are not this fence's own guard target, but are
why § "Scratch backups" below also captures `ROADMAP.md` and `STATE.md`.

## Scratch backups

`.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md` and `.planning/STATE.md` copied into
`$SCRATCH_77_01` (`/tmp/p7701.p8Y5y6`), outside the repository, before any later tooling can rewrite
them:

```
$ S=/tmp/p7701.p8Y5y6
$ cp .planning/REQUIREMENTS.md "$S/p7701_REQUIREMENTS.md"
$ cp .planning/ROADMAP.md "$S/p7701_ROADMAP.md"
$ cp .planning/STATE.md "$S/p7701_STATE.md"
$ sha256sum "$S/p7701_REQUIREMENTS.md" "$S/p7701_ROADMAP.md" "$S/p7701_STATE.md"
35eb6122efd878cad4083a18b84c006f315c3cfe5229f3d443e6c712e6954351  /tmp/p7701.p8Y5y6/p7701_REQUIREMENTS.md
99cc38eaa794b6c075b818a6a4cdb49802fd324a74037a1db32eb5539096df93  /tmp/p7701.p8Y5y6/p7701_ROADMAP.md
64ed67bf1bb1cca7ab82c45e13e06e17e9b7943812ca1fc8f95e8e4c12c6a3ff  /tmp/p7701.p8Y5y6/p7701_STATE.md
```

The REQUIREMENTS.md backup's digest matches `REQ_SHA256_BASE`
(`35eb6122efd878cad4083a18b84c006f315c3cfe5229f3d443e6c712e6954351`) exactly.

Key lines:

```
BACKUP_REQUIREMENTS = /tmp/p7701.p8Y5y6/p7701_REQUIREMENTS.md
BACKUP_ROADMAP = /tmp/p7701.p8Y5y6/p7701_ROADMAP.md
BACKUP_STATE = /tmp/p7701.p8Y5y6/p7701_STATE.md
```

The orchestrator's own tracking commits change `ROADMAP.md` and `STATE.md` legitimately during
execution (per-plan progress checkboxes, phase status), so the operator also takes a **fresh**
backup immediately before running `phase.complete`-family tooling — see § "For the operator running
phase.complete" below. These 77-01 backups are the pre-execution reference the operator's own diff
is taken against for anything that is NOT ordinary per-plan progress tracking.

## Re-verification protocol (phase close)

Reproduced inline, so a later reader needs no second file open:

```bash
sha256sum .planning/REQUIREMENTS.md
# compare against REQ_SHA256_BASE: 35eb6122efd878cad4083a18b84c006f315c3cfe5229f3d443e6c712e6954351

wc -l .planning/REQUIREMENTS.md
# compare against REQ_LINES_BASE: 189

git diff --name-only -- .planning/REQUIREMENTS.md
# expected: no output

grep -vE '^- \[.\] \*\*ATT-06\*\*|^\| ATT-06 \|' .planning/REQUIREMENTS.md | sha256sum
# compare against REQ_SHA256_GUARDED_BASE: fce6cc7d403e4c68b4cf12a6e58bf990f94f9a5f7db2943ce9da2469953d4af5

grep -n 'ATT-03' .planning/REQUIREMENTS.md
grep -n 'ATT-04' .planning/REQUIREMENTS.md
grep -n 'ATT-05' .planning/REQUIREMENTS.md
grep -n 'REL-17' .planning/REQUIREMENTS.md
grep -n 'DOC-25' .planning/REQUIREMENTS.md
# each expected byte-identical to § "The lines under guard" above
```

**Three observations are named explicitly, not two:**

1. **Phase head** — this task, recorded above.
2. **Phase close** — `77-08`'s own re-run of these probes.
3. **Once more, after `phase.complete`-family tooling has actually run** — outside any plan's
   reach, run by the orchestrator or the operator. This is the observation that actually catches
   the flip, because it happens after the tooling call that has fired at 9 of 10 prior
   release-prep closes; `/gsd-verify-work`'s inline transition counts as this tooling exactly as
   much as `/gsd-execute-phase`'s own `phase.complete` step does.

## For the operator running phase.complete

This section applies after this phase's plans have finished, at **whichever of the two entry
points runs**: `/gsd-execute-phase`'s `phase.complete` step, or `/gsd-verify-work`'s inline
transition. Both entry points must be treated as equally likely to trigger the flip; neither is
safer to assume clean than the other.

**Before any of the three runs `phase.complete`-family tooling:** `.planning/REQUIREMENTS.md`,
`.planning/ROADMAP.md` and `.planning/STATE.md` are already backed up outside the repository (see
§ "Scratch backups" above, `/tmp/p7701.p8Y5y6`). Take a **fresh** backup of `ROADMAP.md` and
`STATE.md` immediately before running the tooling, since those two files change legitimately
throughout execution — the 77-01 copies are the pre-execution baseline, not the pre-tooling one.

**After it runs**, re-run the probes in § "Re-verification protocol (phase close)" above (the digest
and guarded-region digest are inlined there so the reader needs no other file open).

**Line-scoped reversion recipe:**

- If the guarded-region digest still MATCHes `REQ_SHA256_GUARDED_BASE`, any difference in the full
  digest is ATT-06's own legitimate close — do **not** revert.
- If the guarded-region digest differs from `REQ_SHA256_GUARDED_BASE`: record which lines moved with
  `git diff -- .planning/REQUIREMENTS.md`, then run `git checkout -- .planning/REQUIREMENTS.md`; if
  ATT-06's checkbox and row had also flipped to `[x]` / `Complete`, re-apply only those two lines by
  an in-place edit; re-run the probes until the guarded-region digest MATCHes; report; never commit a
  flipped guarded line (one of ATT-03, ATT-04, ATT-05, REL-17 or DOC-25).
- Diff `.planning/ROADMAP.md` and `.planning/STATE.md` against the fresh pre-tooling backup and
  hand-correct any tooling damage there separately — this is not the same action as reverting a
  guarded-line flip, and `current_phase_name`-style field mangling is a known recurring shape of that
  damage (`75-CLOSEOUT-GUARD.md` § "Third observation").

**The rule: reverted and reported, never committed.** No `/gsd-complete-milestone` step starts
until the five guarded-ID probes above show MATCH.

## Re-verification at phase close

Recorded inside `77-08`'s own worktree (`worktree-agent-a2b6ebe2228d04eb7`), after waves 2, 3 and 4
have all merged — this is observation 2 of the three named in § "Re-verification protocol (phase
close)" above.

```
$ date -u +%FT%TZ
2026-09-28T14:11:10Z

$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a2b6ebe2228d04eb7

$ test -f .git; echo "exit:$?"
exit:0

$ grep -q typsphinx-fhs-run "$(command -v uv)" && echo shim-ok
shim-ok
```

Provisioning: `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs` exited
0 (`typsphinx==0.9.7` installed editable from this worktree's own checkout, plus every `dev`/`docs`
extra dependency).

```
PYVENV_HOME = /home/yuta/.local/share/uv/python/cpython-3.14-linux-x86_64-gnu/bin
PYVENV_VERSION_INFO = 3.14
```

`mktemp -d /tmp/p7708.XXXXXX` -> `/tmp/p7708.Av4OnH`.

```
SCRATCH_77_08 = /tmp/p7708.Av4OnH
```

```
$ git rev-parse HEAD
29323655fcf9a2b447a1a0848921b97e2c4de193

$ git merge-base --is-ancestor 3984b231e30fbb76ba156d2f9b2abe475231bccf HEAD; echo "exit:$?"
exit:0
```

`PHASE_BASE_SHA` is confirmed an ancestor of this worktree's HEAD.

```
$ sha256sum .planning/REQUIREMENTS.md
35eb6122efd878cad4083a18b84c006f315c3cfe5229f3d443e6c712e6954351  .planning/REQUIREMENTS.md

$ wc -l .planning/REQUIREMENTS.md
189 .planning/REQUIREMENTS.md

$ grep -vE '^- \[.\] \*\*ATT-06\*\*|^\| ATT-06 \|' .planning/REQUIREMENTS.md | sha256sum
fce6cc7d403e4c68b4cf12a6e58bf990f94f9a5f7db2943ce9da2469953d4af5  -

$ git diff --name-only -- .planning/REQUIREMENTS.md
(no output)

$ git diff --name-only 3984b231e30fbb76ba156d2f9b2abe475231bccf HEAD -- .planning/REQUIREMENTS.md
(no output)
```

Both digests and the line count are byte-identical to the phase-head baseline; both diffs are
empty — no plan wrote `.planning/REQUIREMENTS.md`.

```
REQ_SHA256_CLOSE = 35eb6122efd878cad4083a18b84c006f315c3cfe5229f3d443e6c712e6954351
REQ_LINES_CLOSE = 189
REQ_SHA256_GUARDED_CLOSE = fce6cc7d403e4c68b4cf12a6e58bf990f94f9a5f7db2943ce9da2469953d4af5
```

The five `grep -n` transcripts, re-run at close:

```
$ grep -n 'ATT-03' .planning/REQUIREMENTS.md
37:- [ ] **ATT-03**: The switch is proven on **PyPI's own served state** for the real 0.9.7 upload, not
51:      so its absence alone does not prove PyPI served provenance. ATT-03 is what proves that.
55:      ATT-03 passes**; until then the token is the rollback path. `TEST_PYPI_API_TOKEN` is left in
162:| ATT-03 | Phase 77 | publish (coverage only) | Pending |
183:→ ATT-03 (PyPI Simple JSON + Integrity APIs) → ATT-05 (both secret scopes + PyPI revocation, and
184:only once ATT-03 has passed) → DOC-25 (written after ATT-05, so it describes a state that is
```

```
$ grep -n 'ATT-04' .planning/REQUIREMENTS.md
47:- [ ] **ATT-04**: The v0.9.7 release run carries **zero** occurrences of the action's
161:| ATT-04 | Phase 77 | publish (coverage only) | Pending |
182:The publish half runs in a fixed order that `77-HANDOFF.md` enforces: tag push → ATT-04 (run log)
```

```
$ grep -n 'ATT-05' .planning/REQUIREMENTS.md
52:- [ ] **ATT-05**: `PYPI_API_TOKEN` is retired from **both** GitHub scopes — the repository-scoped
86:      ATT-01 and ATT-05 land.
163:| ATT-05 | Phase 77 | publish (coverage only) | Pending |
183:→ ATT-03 (PyPI Simple JSON + Integrity APIs) → ATT-05 (both secret scopes + PyPI revocation, and
184:only once ATT-03 has passed) → DOC-25 (written after ATT-05, so it describes a state that is
```

```
$ grep -n 'REL-17' .planning/REQUIREMENTS.md
75:- [ ] **REL-17**: 0.9.7 is published — `pyproject.toml` bumped as the **sole** version literal with
160:| REL-17 | Phase 77 | split — prep in phase, publish at close | Pending |
185:already true). REL-17's publish clauses are checked across the whole of it.
```

```
$ grep -n 'DOC-25' .planning/REQUIREMENTS.md
84:- [ ] **DOC-25**: `.planning/codebase/INTEGRATIONS.md:116-117` no longer describes `PYPI_API_TOKEN`
164:| DOC-25 | Phase 77 | publish (coverage only) | Pending |
184:only once ATT-03 has passed) → DOC-25 (written after ATT-05, so it describes a state that is
```

All five transcripts are byte-identical to § "The lines under guard" above.

```
GUARDED_LINES_MATCH = yes
```

The direct reads SC#5 requires — each of the five checkbox lines and each traceability row, read
directly out of the file at close:

```
$ for id in ATT-03 ATT-04 ATT-05 REL-17 DOC-25; do grep -E "^- \[ \] \*\*$id\*\*" .planning/REQUIREMENTS.md | head -1; done
- [ ] **ATT-03**: The switch is proven on **PyPI's own served state** for the real 0.9.7 upload, not
- [ ] **ATT-04**: The v0.9.7 release run carries **zero** occurrences of the action's
- [ ] **ATT-05**: `PYPI_API_TOKEN` is retired from **both** GitHub scopes — the repository-scoped
- [ ] **REL-17**: 0.9.7 is published — `pyproject.toml` bumped as the **sole** version literal with
- [ ] **DOC-25**: `.planning/codebase/INTEGRATIONS.md:116-117` no longer describes `PYPI_API_TOKEN`

$ for id in ATT-03 ATT-04 ATT-05 REL-17 DOC-25; do grep -E "^\| $id \| Phase 77 \| .* \| Pending \|$" .planning/REQUIREMENTS.md; done
| ATT-03 | Phase 77 | publish (coverage only) | Pending |
| ATT-04 | Phase 77 | publish (coverage only) | Pending |
| ATT-05 | Phase 77 | publish (coverage only) | Pending |
| REL-17 | Phase 77 | split — prep in phase, publish at close | Pending |
| DOC-25 | Phase 77 | publish (coverage only) | Pending |
```

Every checkbox still reads `- [ ]` and every row still ends `Pending |`, read directly out of the
file, never inferred from SUMMARY frontmatter.

```
GUARDED_CHECKBOXES_UNCHECKED = yes
GUARDED_ROWS_PENDING = yes
```

ATT-06's transcript, beside its expected-to-move callout — it has not moved yet, because no plan in
this phase edits `.planning/REQUIREMENTS.md` and phase-completion tooling has not run:

```
$ grep -n 'ATT-06' .planning/REQUIREMENTS.md
57:- [ ] **ATT-06**: A rollback procedure is recorded before the tag is pushed, and names: restoring
147:  once the registration is fixed. That is cheaper than ATT-06's re-tag path and should be tried
159:| ATT-06 | Phase 77 | pre-tag | Pending |
179:before. ATT-06 is the one requirement Phase 77 legitimately closes, which is why the fence is
```

Still `- [ ]` / `Pending` — unchanged from phase head, exactly as expected before phase-completion
tooling runs.

Discretion A's literal counts, re-measured:

```
$ grep -c 'attestations input ignored' .planning/REQUIREMENTS.md
1
$ grep -c 'attestations input ignored' .planning/ROADMAP.md
3
```

Both equal `ATT04_LITERAL_REQ_HITS_BASE` (1) and `ATT04_LITERAL_ROADMAP_HITS_BASE` (3) respectively.

```
ATT04_LITERAL_REQ_HITS_CLOSE = 1
ATT04_LITERAL_ROADMAP_HITS_CLOSE = 3
ATT04_LITERALS_UNCHANGED = yes
```

Fresh close-time backups, copied to `$SCRATCH_77_08` outside the repository:

```
$ S=/tmp/p7708.Av4OnH
$ cp .planning/REQUIREMENTS.md "$S/p7708_REQUIREMENTS.md"
$ cp .planning/ROADMAP.md "$S/p7708_ROADMAP.md"
$ cp .planning/STATE.md "$S/p7708_STATE.md"
$ sha256sum "$S/p7708_REQUIREMENTS.md" "$S/p7708_ROADMAP.md" "$S/p7708_STATE.md"
35eb6122efd878cad4083a18b84c006f315c3cfe5229f3d443e6c712e6954351  /tmp/p7708.Av4OnH/p7708_REQUIREMENTS.md
cc121aad70cba0dcd5b81f7091eeb40c684e0fe067d56c110c127eaf04b703f2  /tmp/p7708.Av4OnH/p7708_ROADMAP.md
ce7dfb5f78197c82aa37572828cac98c3675094b6fca8481ef1410a326115fde  /tmp/p7708.Av4OnH/p7708_STATE.md
```

The REQUIREMENTS.md close-time backup's digest matches the live file exactly (`REQ_SHA256_CLOSE`).

```
CLOSE_BACKUP_REQUIREMENTS = /tmp/p7708.Av4OnH/p7708_REQUIREMENTS.md
CLOSE_BACKUP_ROADMAP = /tmp/p7708.Av4OnH/p7708_ROADMAP.md
CLOSE_BACKUP_STATE = /tmp/p7708.Av4OnH/p7708_STATE.md
```

Diffed against 77-01's phase-head backups (`BACKUP_ROADMAP = /tmp/p7701.p8Y5y6/p7701_ROADMAP.md`,
`BACKUP_STATE = /tmp/p7701.p8Y5y6/p7701_STATE.md`) — both measured, both legitimate orchestrator
tracking changes, not tooling damage:

`ROADMAP.md` diff: the per-plan progress lines for 77-01 through 77-07 flipped `- [ ]` to `- [x]`,
the phase summary row moved from `0/8 | Not started` to `7/8 | In Progress`, and the top-line
`**Plans**:` counter moved from `8 plans (5 waves)` to `7/8 plans executed (5 waves)` — exactly the
per-plan progress tracking the orchestrator updates after every merged wave.

`STATE.md` diff: `last_updated`, `last_activity_desc`, `progress.completed_plans` (3 → 10, cumulative
project count, not phase-scoped), and the `## Current Position` block's `Plan:`/`Status:`/`Last
activity:` lines — all ordinary session-tracking fields the orchestrator updates after each wave,
none of it a checkbox or traceability-row flip inside `.planning/REQUIREMENTS.md`.

`FENCE_CLOSE_VERDICT = MATCH` — every digest, the line count, both empty diffs, the five transcripts
and both direct reads hold.

```
FENCE_CLOSE_VERDICT = MATCH
```

## Handoff to the third observation

Written for the orchestrator who runs `phase.complete`-family tooling after this plan — a new
section, not a second copy of § "For the operator running phase.complete" above.

**Immediately before that tooling runs:** copy `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`
and `.planning/STATE.md` to a fresh `mktemp -d`, outside the repository, exactly as § "For the
operator running phase.complete" and every earlier backup in this file already do.

**Immediately after it runs**, re-run the full probe set from § "Re-verification protocol (phase
close)" above:

```bash
sha256sum .planning/REQUIREMENTS.md
wc -l .planning/REQUIREMENTS.md
git diff --name-only -- .planning/REQUIREMENTS.md
grep -vE '^- \[.\] \*\*ATT-06\*\*|^\| ATT-06 \|' .planning/REQUIREMENTS.md | sha256sum
grep -n 'ATT-03' .planning/REQUIREMENTS.md
grep -n 'ATT-04' .planning/REQUIREMENTS.md
grep -n 'ATT-05' .planning/REQUIREMENTS.md
grep -n 'REL-17' .planning/REQUIREMENTS.md
grep -n 'DOC-25' .planning/REQUIREMENTS.md
```

**Expected:** the guarded-region digest (the same command quoted above, re-run verbatim) still
equals `REQ_SHA256_GUARDED_BASE = fce6cc7d403e4c68b4cf12a6e58bf990f94f9a5f7db2943ce9da2469953d4af5`.
The full digest MAY differ from `REQ_SHA256_BASE`/`REQ_SHA256_CLOSE` only because ATT-06's own
checkbox (line 57) and traceability row (line 159) flipped to `[x]` / `Complete` — that one flip is
legitimate, since ATT-06 is the requirement this phase actually closes.

**Any other difference is a defect, not a legitimate flip.** Revert it:

```bash
git checkout -- .planning/REQUIREMENTS.md
```

then, if ATT-06's checkbox and row had also legitimately flipped before the revert, re-apply only
those two lines by an in-place edit; re-run every probe above until the guarded-region digest
MATCHes `REQ_SHA256_GUARDED_BASE` again; report the event; never commit a flipped guarded line (one
of ATT-03, ATT-04, ATT-05, REL-17 or DOC-25). Record the whole sequence — what moved, the revert,
the re-applied ATT-06 lines if any, and the re-proven MATCH — in a section appended to this file for
that purpose, headed to name the third observation explicitly and naming the orchestrator as the one
who ran it. That write happens outside every plan, at the moment the tooling actually runs; this
plan only documents the protocol.

`.planning/ROADMAP.md` and `.planning/STATE.md` are diffed against the fresh pre-tooling backup
taken above (not against the 77-01 phase-head backup, which predates legitimate per-plan tracking
changes) and any tooling damage — field mangling, wrapped-line corruption — is hand-corrected
separately from the guarded-line reversion.

```
THIRD_OBSERVATION_DOCUMENTED = yes
```

This records that the instructions above exist and are complete, not that the observation has been
taken — the observation itself belongs to whoever runs `phase.complete`-family tooling, after this
plan has finished.

---
*Phase: 77-v0-9-7-release-prep-prep-only-and-the-trusted-publishing-proof-handoff*
*Plan: 01*
