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

## Re-verification at phase close

Run by plan 63-04, inside its own isolated worktree (`worktree-agent-a4d2b14ab7009647a`), at a fresh
UTC timestamp distinct from the Baseline's:

```
$ date -u +"%Y-%m-%dT%H:%M:%SZ"
2026-08-30T12:03:06Z
```

The protocol's own triad, re-run and compared side by side against the Baseline recorded above:

**SHA-256 digest**

| | Value |
|---|---|
| Baseline (recorded at phase head) | `f0dd4ec377bbc95cd2b8cdb19fe784cfc21bd6d08e2743de6f5b9fc1768f5b33` |
| Live (this re-verification) | `f0dd4ec377bbc95cd2b8cdb19fe784cfc21bd6d08e2743de6f5b9fc1768f5b33` |

```
$ sha256sum .planning/REQUIREMENTS.md
f0dd4ec377bbc95cd2b8cdb19fe784cfc21bd6d08e2743de6f5b9fc1768f5b33  .planning/REQUIREMENTS.md
```

**Line count**

| | Value |
|---|---|
| Baseline (recorded at phase head) | `184` |
| Live (this re-verification) | `184` |

```
$ wc -l .planning/REQUIREMENTS.md
184 .planning/REQUIREMENTS.md
```

**Name-only diff, scoped to `.planning/REQUIREMENTS.md`**

```
$ git diff --name-only -- .planning/REQUIREMENTS.md
(no output)
```

Expected no output; observed no output.

**The `REL-09` grep, compared line-for-line against the Baseline's quoted hits**

| Line | Baseline (§ "The lines under guard") | Live |
|---|---|---|
| 70 | `- [ ] **REL-09**: 0.9.2 released to PyPI with a curated `\`## [0.9.2]\`` CHANGELOG entry, the version` | identical |
| 154 | `\| REL-09 \| Phase 63 \| Pending \|` | identical |
| 175 (informational-only) | `- **Phase 63 — v0.9.2 Release Prep (prep-only)** carries the release half. **REL-09 is cited for` | identical |

```
$ grep -n 'REL-09' .planning/REQUIREMENTS.md
70:- [ ] **REL-09**: 0.9.2 released to PyPI with a curated `## [0.9.2]` CHANGELOG entry, the version
154:| REL-09 | Phase 63 | Pending |
175:- **Phase 63 — v0.9.2 Release Prep (prep-only)** carries the release half. **REL-09 is cited for
```

Byte-identical to the Baseline's § "The lines under guard" on all three lines, both line numbers and
byte content of the two state-bearing lines (70's checkbox and 154's Traceability row), and the
presence of the informational-only third hit (175).

**Verdict: MATCH.** All four comparisons above — the SHA-256 digest, the line count, the empty
name-only diff, and the byte-identical `REL-09` grep hits — hold at phase close exactly as they held
at phase head. No divergence occurred, so the reversion procedure below was **not** exercised this
time; it is recorded for completeness in case a future re-run of this section finds one.

**If a comparison had diverged** (most likely REL-09's checkbox flipped to checked against this
phase's explicit decision), the response would be: do not accept it, do not commit it. Run
`git checkout -- .planning/REQUIREMENTS.md`, re-run the full triad above, and record the before
state, the reversion command, and the after state in this same section, then report the divergence
in this plan's SUMMARY. The flip has landed at five consecutive prior release-prep closes and
Phase 61 was the first to hold; the only thing that made the difference was recording, comparing and
reverting rather than assuming — the same discipline this MATCH verdict confirms held again here.

**The decisive observation is still owed, and it is not this plan's to take.** It runs after
`phase.complete`-family tooling, outside any plan's reach, and its protocol is already written into
this file's § "For the operator running phase.complete" section above, confirmed present at this
re-verification. `63-HANDOFF.md` points at that section by name so an operator following the handoff
reaches it without opening this file separately.

**REL-09's state, read directly out of `.planning/REQUIREMENTS.md` at this close** — never inferred
from any plan's frontmatter:

Checkbox line (70): `- [ ] **REL-09**: 0.9.2 released to PyPI with a curated `\`## [0.9.2]\`` CHANGELOG entry, the version`
— unchecked.

Traceability row (154): `| REL-09 | Phase 63 | Pending |` — Pending.

## Re-verification after gap closure

**Why this section exists.** Plan 63-05's gap-closure correction commit (`2a0bc3be`) and this
plan's own commits move HEAD forward from the "Re-verification at phase close" observation above.
Moving HEAD is precisely the condition under which the historical checkbox flip has landed at
**five consecutive** prior release-prep closes. A fence verified before those commits says nothing
about the tree after them — this section re-runs the same triad against the tree as it now stands.

Run inside this plan's own isolated worktree (`worktree-agent-ae5c12953cb4748a0`), at a fresh UTC
timestamp distinct from both the Baseline's and the phase-close re-verification's:

```
$ date -u +"%Y-%m-%dT%H:%M:%SZ"
2026-08-30T13:43:18Z
```

The protocol's own triad, re-run and compared side by side against the Baseline recorded above:

**SHA-256 digest**

| | Value |
|---|---|
| Baseline (recorded at phase head) | `f0dd4ec377bbc95cd2b8cdb19fe784cfc21bd6d08e2743de6f5b9fc1768f5b33` |
| Live (this re-verification, post-gap-closure) | `f0dd4ec377bbc95cd2b8cdb19fe784cfc21bd6d08e2743de6f5b9fc1768f5b33` |

```
$ sha256sum .planning/REQUIREMENTS.md
f0dd4ec377bbc95cd2b8cdb19fe784cfc21bd6d08e2743de6f5b9fc1768f5b33  .planning/REQUIREMENTS.md
```

**Line count**

| | Value |
|---|---|
| Baseline (recorded at phase head) | `184` |
| Live (this re-verification, post-gap-closure) | `184` |

```
$ wc -l .planning/REQUIREMENTS.md
184 .planning/REQUIREMENTS.md
```

**Name-only diff and porcelain status, scoped to `.planning/REQUIREMENTS.md`**

```
$ git diff --name-only -- .planning/REQUIREMENTS.md
(no output)

$ git status --porcelain .planning/REQUIREMENTS.md
(no output)
```

Both expected no output; both observed no output.

**The `REL-09` grep, compared line-for-line against the Baseline's quoted hits**

| Line | Baseline (§ "The lines under guard") | Live (post-gap-closure) |
|---|---|---|
| 70 | `- [ ] **REL-09**: 0.9.2 released to PyPI with a curated `\`## [0.9.2]\`` CHANGELOG entry, the version` | identical |
| 154 | `\| REL-09 \| Phase 63 \| Pending \|` | identical |
| 175 (informational-only) | `- **Phase 63 — v0.9.2 Release Prep (prep-only)** carries the release half. **REL-09 is cited for` | identical |

```
$ grep -n 'REL-09' .planning/REQUIREMENTS.md
70:- [ ] **REL-09**: 0.9.2 released to PyPI with a curated `## [0.9.2]` CHANGELOG entry, the version
154:| REL-09 | Phase 63 | Pending |
175:- **Phase 63 — v0.9.2 Release Prep (prep-only)** carries the release half. **REL-09 is cited for
```

Byte-identical to the Baseline's § "The lines under guard" on all three lines, both line numbers
and byte content of the two state-bearing lines (70's checkbox and 154's Traceability row), and the
presence of the informational-only third hit (175).

**Verdict: MATCH.** All four comparisons above — the SHA-256 digest, the line count, the empty
name-only diff / porcelain status, and the byte-identical `REL-09` grep hits — hold after the
gap-closure commits (`2a0bc3be`, `41eb46be`, `c9f929b2`, and this plan's own Task 1 commit) exactly
as they held at phase head and at phase close. No divergence occurred, so the reversion procedure
was **not** exercised this time.

**If a comparison had diverged** (most likely REL-09's checkbox flipped to checked against this
phase's explicit decision), the response would have been: do not accept it, do not commit it. Run
`git checkout -- .planning/REQUIREMENTS.md`, re-run the full triad above, and record the before
state, the literal reversion command, and the after state in this same section, then report the
divergence in this plan's SUMMARY. No such divergence occurred here.

**REL-09's state, read directly out of `.planning/REQUIREMENTS.md` at this re-verification** — never
inferred from any plan's frontmatter:

Checkbox line (70): `- [ ] **REL-09**: 0.9.2 released to PyPI with a curated `\`## [0.9.2]\`` CHANGELOG entry, the version`
— unchecked.

Traceability row (154): `| REL-09 | Phase 63 | Pending |` — Pending. Both `63-05-PLAN.md` and
`63-06-PLAN.md` (this plan) declare `requirements-completed: []` for REL-09.

**The decisive observation is still owed, and it is still not a plan's to take.** It runs after
`phase.complete`-family tooling, outside any plan's reach, and its protocol is already written into
this file's § "For the operator running phase.complete" section above — confirmed still present and
unedited by this re-verification. `63-HANDOFF.md` continues to point at that section by name so an
operator following the handoff reaches it without opening this file separately.

---
*Phase: 63-v0-9-2-release-prep-prep-only*
*Plan: 02, 04, 06*
