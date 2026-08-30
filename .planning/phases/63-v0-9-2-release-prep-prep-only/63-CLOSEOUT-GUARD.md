# Phase 63 — REL-09 Checkbox-Flip Closeout Guard

This task changes NO requirement state: REL-09 stays an unchecked box (`- [ ]`) and its
Traceability row stays `Pending`. `.planning/REQUIREMENTS.md` is read and quoted here and never
edited.

## Baseline

Recorded at phase head, inside this plan's isolated worktree (`worktree-agent-abc32982f68a82498`),
before this plan creates any file.

```
$ git rev-parse HEAD
c31bb048bf5a92b7550bc2aa68efb114437533fa

$ git log --format='%H %s' -1
c31bb048bf5a92b7550bc2aa68efb114437533fa docs(63): add pattern map

$ git rev-parse --abbrev-ref HEAD
worktree-agent-abc32982f68a82498

$ sha256sum .planning/REQUIREMENTS.md
f0dd4ec377bbc95cd2b8cdb19fe784cfc21bd6d08e2743de6f5b9fc1768f5b33  .planning/REQUIREMENTS.md

$ wc -l .planning/REQUIREMENTS.md
184 .planning/REQUIREMENTS.md

$ date -u +"%Y-%m-%dT%H:%M:%SZ"
2026-08-30T11:15:18Z
```

**PHASE_BASE_SHA:**

```
c31bb048bf5a92b7550bc2aa68efb114437533fa
```

Subject: `docs(63): add pattern map` — a phase-authoring commit that predates this plan's own
execution and carries no `63-NN` (plan-level) commit scope, confirmed by the Task 1 precondition
check (`git log --format=%s -1 | grep -oE '\(63-[0-9]+\)'` returned no match before this file was
created). Plans 63-03 and 63-04 read this value back from this file to scope their `typsphinx/`
diffs.

**Cross-check against the research-time values.** `63-RESEARCH.md` § "Code Examples" §
"The closeout-guard fence (D-16/REL-11)" supplied the values measured at research time (2026-08-30)
as a cross-check, not as this plan's final answer: checksum
`f0dd4ec377bbc95cd2b8cdb19fe784cfc21bd6d08e2743de6f5b9fc1768f5b33`, line count `184`, hits at lines
70/154/175. Both commands were re-run fresh above (not transcribed from the research session), and
both values are byte-identical to the research-time figures. No drift occurred between research and
this plan's own execution; `.planning/REQUIREMENTS.md` has not changed in the interim.

## The lines under guard

Verbatim output of `grep -n 'REL-09' .planning/REQUIREMENTS.md`, run against this worktree's tree at
the timestamp above:

```
$ grep -n 'REL-09' .planning/REQUIREMENTS.md
70:- [ ] **REL-09**: 0.9.2 released to PyPI with a curated `## [0.9.2]` CHANGELOG entry, the version
154:| REL-09 | Phase 63 | Pending |
175:- **Phase 63 — v0.9.2 Release Prep (prep-only)** carries the release half. **REL-09 is cited for
```

Three hits, as expected.

### REL-09's requirement bullet's checkbox line

**Observed at line 70 (byte-for-byte):**

```
- [ ] **REL-09**: 0.9.2 released to PyPI with a curated `## [0.9.2]` CHANGELOG entry, the version
```

(The bullet continues across lines 71-80 with prose describing the version-bump, `uv.lock`
lockstep, and GitHub Release Body requirements — only line 70's leading `- [ ]` is the state-bearing
token.)

### REL-09's Traceability row

**Observed at line 154 (byte-for-byte):**

```
| REL-09 | Phase 63 | Pending |
```

### The phase-mapping-notes paragraph opening line

**Observed at line 175 (byte-for-byte), cited for completeness since the `grep -n` output above
surfaces it, but it carries no checkbox or Pending/Complete state of its own — resolving Pitfall 6
explicitly rather than by copying Phase 61's differently-shaped third hit:**

```
- **Phase 63 — v0.9.2 Release Prep (prep-only)** carries the release half. **REL-09 is cited for
```

**Pitfall 6, resolved against the file's actual current shape.** Phase 61's third `grep -n 'REL-09'`
hit (line 220 of `61-`'s `REQUIREMENTS.md`) was a single terse "phase-totals" summary line —
`Phase 60 → 4 (...) · Phase 61 → 1 (REL-09).` — that stood alone as one line of prose. This phase's
own `.planning/REQUIREMENTS.md` carries a **different structure**: there is no phase-totals
enumeration line at all. Line 175 is instead the **opening line of a six-line prose paragraph**
(the "Phase mapping notes" section's Phase 63 bullet, lines 175-180) describing why REL-09 is cited
for coverage only. Quoting Phase 61's "phase-totals line" shape here would be exactly the defect
Pitfall 6 names: a guard file quoting a line shape the current `.planning/REQUIREMENTS.md` does not
contain.

**Classification:**

- **State-bearing:** line 70 (the requirement bullet's checkbox — `- [ ]` vs `- [x]`) and line 154
  (the Traceability row — `Pending` vs `Complete`). These are the two lines whose content would
  change if the checkbox flipped.
- **Informational-only:** line 175 (the opening line of the multi-line "Phase mapping notes"
  prose paragraph). This line describes REL-09's handling in prose; it carries no
  checkbox/Pending/Complete token of its own and would not change shape merely because line 70 or
  154 flipped.

This classification changes nothing about detection coverage — the whole-file SHA-256 recorded
above covers all three lines (and every other byte in the file) regardless of which are
state-bearing. The classification exists only so the close-time re-verification in
§ "Re-verification protocol (phase close)" below compares the right things line-for-line, and so a
future reader does not mistake line 175's paragraph-opening shape for Phase 61's terse
phase-totals-line shape.

## Why this file exists

`phase.complete`-family tooling has auto-flipped the release requirement's checkbox and
Traceability-row state against an explicit CONTEXT decision at **five consecutive** release-prep
closes (the v0.7.0, v0.7.1, v0.8.0, v0.9.0, and v0.9.1 closes all flipped their respective release
requirement before this project caught and reverted the flip). v0.9.1's Phase 61 was the first to
hold, using this exact procedure (`61-CLOSEOUT-GUARD.md`). The flip is reverted and reported, never
accepted and never committed.

## Re-verification protocol (phase close)

Plan 63-04 (the SC#5 fence-observation-2 owner) runs exactly these commands against the tree as it
stands at its own point in the phase, and reports whether the Baseline still holds:

```bash
sha256sum .planning/REQUIREMENTS.md
# compare the printed digest against this file's Baseline:
# f0dd4ec377bbc95cd2b8cdb19fe784cfc21bd6d08e2743de6f5b9fc1768f5b33

git diff --name-only -- .planning/REQUIREMENTS.md
# expected: no output

grep -n 'REL-09' .planning/REQUIREMENTS.md
# expected: byte-identical to the three quoted lines above (70, 154, 175)
```

## Post-close detection and reversion (after phase.complete runs)

This section is reproduced in `63-HANDOFF.md` so an operator following the handoff reaches it
without opening this file.

After `phase.complete`-family tooling has run for Phase 63 — outside any plan's reach, and precisely
the moment at which the flip has historically landed — run the same three commands again:

```bash
sha256sum .planning/REQUIREMENTS.md
# compare against this file's Baseline: f0dd4ec377bbc95cd2b8cdb19fe784cfc21bd6d08e2743de6f5b9fc1768f5b33

git diff --name-only -- .planning/REQUIREMENTS.md
# expected: no output

grep -n 'REL-09' .planning/REQUIREMENTS.md
# expected: byte-identical to the three quoted lines above (70, 154, 175)
```

If the digest has moved, or `git diff --name-only -- .planning/REQUIREMENTS.md` shows a change
touching line 70's checkbox or line 154's Traceability row, that change is unintended. Revert it by
hand:

```bash
git checkout -- .planning/REQUIREMENTS.md
```

**The flip is reverted and reported, never accepted and never committed.** This is the explicit rule
this project has followed at every prior release-prep close where the flip was caught: revert first,
report second, never ship the flipped state as part of the phase's own close.

## This task's own effect on `.planning/REQUIREMENTS.md`

```
$ git diff --name-only -- .planning/REQUIREMENTS.md
(no output)

$ git status --porcelain .planning/REQUIREMENTS.md
(no output)
```

Byte-unchanged. REL-09 remains `- [ ]` and Pending, exactly as recorded in § "The lines under guard"
above.

## For the operator running phase.complete

This section is reproduced in `63-HANDOFF.md` so an operator following the handoff reaches it
without opening this file separately.

After `phase.complete`-family tooling has run for Phase 63 — outside any plan's reach, and precisely
the moment at which the flip has historically landed at **five consecutive** prior release-prep
closes — run:

```bash
sha256sum .planning/REQUIREMENTS.md
# compare against the Baseline: f0dd4ec377bbc95cd2b8cdb19fe784cfc21bd6d08e2743de6f5b9fc1768f5b33

git diff --name-only -- .planning/REQUIREMENTS.md
# expected: no output

grep -n 'REL-09' .planning/REQUIREMENTS.md
# expected: byte-identical to:
#   70:- [ ] **REL-09**: 0.9.2 released to PyPI with a curated `## [0.9.2]` CHANGELOG entry, the version
#   154:| REL-09 | Phase 63 | Pending |
#   175:- **Phase 63 — v0.9.2 Release Prep (prep-only)** carries the release half. **REL-09 is cited for
```

If any comparison diverges, revert it by hand:

```bash
git checkout -- .planning/REQUIREMENTS.md
```

**The flip is reverted and reported, never accepted and never committed.** Do not proceed with
`/gsd-complete-milestone` or any subsequent step until the reversion is confirmed by re-running the
three commands above and observing MATCH on all three. This third observation is the decisive one
precisely because it runs after the tooling and outside any plan's reach — it is the moment the flip
has landed at five consecutive prior release-prep closes, and the one Phase 61 caught it at for the
first time.

---
*Phase: 63-v0-9-2-release-prep-prep-only*
*Plan: 02*
