# Phase 57 Plan 01 — REL-08 Checkbox-Flip Closeout Guard

Follows the `42-CLOSEOUT-GUARD.md` mechanism this project adopted at the v0.7.0 close, adapted for
Phase 57's single requirement (REL-08). This task changes NO requirement state — REL-08 stays
`[ ]` and Pending; `.planning/REQUIREMENTS.md` is read and quoted here only, never edited.

## Baseline

```
$ sha256sum .planning/REQUIREMENTS.md
503efc7acb10642cee5f7d171bd66e15f4420b8610f7d0a22483424c17567d94  .planning/REQUIREMENTS.md

$ wc -l .planning/REQUIREMENTS.md
227 .planning/REQUIREMENTS.md

$ date -u +"%Y-%m-%dT%H:%M:%SZ"
2026-08-16T15:40:21Z
```

Recorded inside this plan's isolated worktree `worktree-agent-aa884129710c018db`, at the
phase-start SHA `78bd595d344f46c6e1f5a18bce0e24da1f66a9ee` (the tip this worktree branched from,
per `57-BUMP-EVIDENCE.md`'s anchor re-measurement).

## The lines under guard

All lines quoted below were obtained by running `grep -n 'REL-08' .planning/REQUIREMENTS.md`
directly against this worktree's tree at the timestamp above:

```
$ grep -n 'REL-08' .planning/REQUIREMENTS.md
128:- [ ] **REL-08**: v0.9.0 is published — PyPI wheel + sdist, GitHub Release carrying the curated
133:      prep-only final phase (57), which takes zero irreversible action — REL-08 closes at
212:| REL-08 | Phase 57 | Pending |
218:- v1 requirements: 26 total (25 defined 2026-08-15 + REL-08 added at roadmap creation)
```

### REL-08's requirement bullet's checkbox line

**Observed at line 128 (byte-for-byte):**

```
- [ ] **REL-08**: v0.9.0 is published — PyPI wheel + sdist, GitHub Release carrying the curated
```

(The bullet continues across lines 129-136 with prose — the italic note at lines 132-136 explicitly
states REL-08 "stays `[ ]` through every plan of Phase 57" — but only line 128's leading `- [ ]` is
the state-bearing token.)

### REL-08's Traceability row

**Observed at line 212 (byte-for-byte):**

```
| REL-08 | Phase 57 | Pending |
```

Line 218 (the "26 total" coverage-count prose) mentions REL-08 by name but carries no checkbox or
Pending/Complete state of its own — it is not a guarded line, only cited here for completeness
since the `grep -n` output above surfaces it.

## Why this file exists

`phase.complete`-family tooling has auto-flipped the release requirement's checkbox and
Traceability-row state against an explicit CONTEXT decision at **four consecutive release-prep
closes** (the pattern `57-CONTEXT.md` and this plan's own `must_haves.truths` both name). ROADMAP
SC#4 requires this checksum precisely so that flip is caught and reverted rather than shipped as
part of Phase 57's own close — REL-08's own requirement text is explicit that it "closes at
`/gsd-complete-milestone`, on the publish, not on the prep," because the publish (PyPI upload,
GitHub Release, the second-repository tag, Read the Docs `stable`) has not happened yet and this
phase takes zero irreversible action.

## Re-verification protocol

A later plan re-verifying this guard must run exactly these two commands:

```bash
sha256sum .planning/REQUIREMENTS.md
# compare the printed digest against this file's Baseline:
# 503efc7acb10642cee5f7d171bd66e15f4420b8610f7d0a22483424c17567d94

git diff --name-only -- .planning/REQUIREMENTS.md
# expected: no output
```

If the digest no longer matches the Baseline **and** `git diff --name-only -- .planning/
REQUIREMENTS.md` shows a change touching line 128's checkbox or line 212's Traceability row (per
§"The lines under guard" above), that change is unintended — revert by hand
(`git checkout -- .planning/REQUIREMENTS.md`) and report it rather than committing it. A digest
change that touches only some *other* file's line (this file's own checksum is scoped to
`REQUIREMENTS.md` alone) is out of this guard's scope.

**Two later plans own re-verification:** plan **57-08** (the SC#4 sweep) and plan **57-09** (the
handoff), each re-running the two commands above against the tree as it stands at their own point
in the phase and reporting whether the Baseline still holds.

This plan's own effect on `.planning/REQUIREMENTS.md`:

```
$ git status --porcelain .planning/REQUIREMENTS.md
(no output)
```

Byte-unchanged. REL-08 remains `- [ ]` and Pending, exactly as recorded in §"The lines under guard"
above.
