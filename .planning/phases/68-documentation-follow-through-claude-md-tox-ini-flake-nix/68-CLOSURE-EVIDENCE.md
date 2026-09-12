# Phase 68 Plan 04 — Closure Evidence (merged tree, wave 2)

Measures the merged wave-1 tree (68-01, 68-02, 68-03) in a later wave than every edit it
reports on, per the plan's own framing.

## Head check and provisioning

```
$ date -u +%FT%TZ
2026-09-12T16:07:59Z

$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-af9456d0ad8b8d0e9

$ test -f .git; echo "exit:$?"
exit:0

$ command -v uv
/nix/store/3vpzk25whpm7s8zq5flpk8gbpkggj9np-uv/bin/uv

$ grep -c typsphinx-fhs-run "$(command -v uv)"
2
```

```
$ env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev
(tail)
 + typsphinx==0.9.2 (from file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-af9456d0ad8b8d0e9)
 + typst==0.15.0
 + urllib3==2.7.0
 + uv==0.12.13
 + virtualenv==21.5.1
```

```
$ git merge-base HEAD gsd/v0.9.3-toolchain-and-dependency-update-repair
effc715e47dfe6b7e678b2822b441a7eced23d25
```

BASE_68_04 = effc715e47dfe6b7e678b2822b441a7eced23d25

```
$ git log --oneline -15
effc715e docs(phase-68): update tracking after wave 1, mark wave 2 executing
8d13705c chore: merge executor worktree (worktree-agent-ae9aed511800dac5e)
37de326d chore: merge executor worktree (worktree-agent-a85e86a327c1b7e0e)
7e3daba8 chore: merge executor worktree (worktree-agent-a2eb538334cf0cc75)
88fae6b4 docs(68-02): append self-check to plan summary
4353f5a1 docs(68-02): complete tox.ini and test-file tox-uv-bare rewrite plan
3865e953 test(68-02): add revert/FHS sentence to D-14 docstring, close plan gates
df944a17 docs(68-03): complete flake.nix documentation follow-through plan
b854e969 docs(68-03): add flake.nix header notes and restate per-element comments
ec5506ff test(68-02): rewrite D-13 self-referential prose in test_toolchain_config_gate.py
ff4b8805 docs(68-01): complete CLAUDE.md documentation follow-through plan
322b8a4f docs(68-01): add NixOS development shell subsection and worktree boundary
c8df5e8d docs(68-02): rewrite tox.ini requires comment for the landed tox-uv pin
44dbdb53 docs(68-03): rewrite uvShim comment, derivation-identity gate proven
b6cbeebf docs(68-01): rewrite CLAUDE.md line 11 and tox.ini bullet for tox-uv~=1.35
```

## Wave-1 inputs

```
$ git cat-file -e HEAD:.../68-CLAUDEMD-EVIDENCE.md; echo "exit:$?"
exit:0
$ git cat-file -e HEAD:.../68-TOX-EVIDENCE.md; echo "exit:$?"
exit:0
$ git cat-file -e HEAD:.../68-FLAKE-EVIDENCE.md; echo "exit:$?"
exit:0
$ git cat-file -e HEAD:.../68-01-SUMMARY.md; echo "exit:$?"
exit:0
$ git cat-file -e HEAD:.../68-02-SUMMARY.md; echo "exit:$?"
exit:0
$ git cat-file -e HEAD:.../68-03-SUMMARY.md; echo "exit:$?"
exit:0
```
(all six paths under `.planning/phases/68-documentation-follow-through-claude-md-tox-ini-flake-nix/`)

```
$ grep -c '^## HALT' .../68-CLAUDEMD-EVIDENCE.md
0
$ grep -c '^## HALT' .../68-TOX-EVIDENCE.md
0
$ grep -c '^## HALT' .../68-FLAKE-EVIDENCE.md
0
```

`BASE_68_01`, `BASE_68_02`, `BASE_68_03` read from the three evidence files with the
`KEY = value` reader:

```
$ sed -n 's/^BASE_68_01 = //p' .../68-CLAUDEMD-EVIDENCE.md
0bd33617d3cdf96f0342bdaeb19a0cb031f7c10a
$ sed -n 's/^BASE_68_02 = //p' .../68-TOX-EVIDENCE.md
0bd33617d3cdf96f0342bdaeb19a0cb031f7c10a
$ sed -n 's/^BASE_68_03 = //p' .../68-FLAKE-EVIDENCE.md
0bd33617d3cdf96f0342bdaeb19a0cb031f7c10a
```

```
$ git merge-base --octopus 0bd33617d3cdf96f0342bdaeb19a0cb031f7c10a 0bd33617d3cdf96f0342bdaeb19a0cb031f7c10a 0bd33617d3cdf96f0342bdaeb19a0cb031f7c10a
0bd33617d3cdf96f0342bdaeb19a0cb031f7c10a
```

PHASE_BASE = 0bd33617d3cdf96f0342bdaeb19a0cb031f7c10a

```
$ git merge-base --is-ancestor 0bd33617d3cdf96f0342bdaeb19a0cb031f7c10a HEAD; echo "exit:$?"
exit:0
```

All three wave-1 bases are identical (the three wave-1 worktrees forked from the same
dispatch point, `0bd33617d3cdf96f0342bdaeb19a0cb031f7c10a`), so their octopus merge-base
equals that commit itself, and it is an ancestor of this worktree's HEAD.

## D-15 grep (merged tree)

```
$ git grep -n tox-uv-bare -- ':!.planning' ':!uv.lock'
CLAUDE.md:77:- `tox.ini` pins `tox-uv~=1.35` (not `>=1.35,<2`) — see the comment in that file; tox's ini parser splits a single-line `requires` on commas, so `>=1.35,<2` breaks tox's startup and `~=1.35` is the comma-free equivalent. The pin was earlier `tox-uv-bare` (QUA-04, Phase 45.2) only because the `uv` bundled with `tox-uv` could not exec on NixOS; the NixOS FHS shims now handle that, which is why plain `tox-uv` is correct again.
tests/test_pdf_render_gate.py:167:    cause was removed by QUA-04 (2026-08-10; `tox-uv` -> `tox-uv-bare` drops
tests/test_toolchain_config_gate.py:6:Phase 45.2's migration from tox-uv to tox-uv-bare and the conversion of [testenv]
tests/test_toolchain_config_gate.py:36:MUST name `tox-uv` (by normalized distribution name) and MUST NOT name `tox-uv-bare`
tests/test_toolchain_config_gate.py:41:stub-ld defect QUA-04 fixed by moving to `tox-uv-bare` no longer bites: without
tests/test_toolchain_config_gate.py:46:`.planning/phases/65-tox-uv-bare-tox-uv-revert-on-the-uv-path-tox-actually-resolves/65-REVERT-EVIDENCE.md`
tests/test_toolchain_config_gate.py:51:tox-uv, tox-uv-bare (by normalized distribution name). SC#7 establishes that Phase 45.2's
tests/test_toolchain_config_gate.py:269:    """[project.optional-dependencies].dev MUST name tox-uv, MUST NOT name tox-uv-bare.
tests/test_toolchain_config_gate.py:276:    fixed by moving to `tox-uv-bare` no longer bites. Without `tox-uv`, tox-uv's
tests/test_toolchain_config_gate.py:289:    **The naming trap:** "tox-uv-bare" contains the substring "tox-uv". A naive
tests/test_toolchain_config_gate.py:297:    are covered automatically. Naming `tox-uv` in the dev extra pulls in `tox-uv-bare`
tests/test_toolchain_config_gate.py:300:    `dev` extra naming `tox-uv-bare` directly as a literal entry.
tests/test_toolchain_config_gate.py:302:    CLAUDE.md's own "Conventions & gotchas" sentence named `tox-uv-bare` as
tests/test_toolchain_config_gate.py:305:    `tox-uv~=1.35` pin, keeping `tox-uv-bare` only as history.
tests/test_toolchain_config_gate.py:308:    `.planning/phases/65-tox-uv-bare-tox-uv-revert-on-the-uv-path-tox-actually-resolves/65-REVERT-EVIDENCE.md`
tests/test_toolchain_config_gate.py:359:    # G5 requirement 2 (Phase 65 revert): dev extra MUST NOT name tox-uv-bare directly.
tests/test_toolchain_config_gate.py:360:    assert canonicalize_name("tox-uv-bare") not in dev_names, (
tests/test_toolchain_config_gate.py:361:        "dev extra names 'tox-uv-bare' directly (on normalized distribution name) -- "
tests/test_toolchain_config_gate.py:364:        "motivated it. tox-uv-bare stays present only as tox-uv's own exact-version "
tests/test_toolchain_config_gate.py:366:        "forbids -- it forbids the dev extra naming tox-uv-bare as a literal entry in "
tests/test_toolchain_config_gate.py:374:    """[project].dependencies MUST NOT name any of: uv, tox, tox-uv, tox-uv-bare.
tests/test_toolchain_config_gate.py:396:    are covered automatically. The forbidden list (uv, tox, tox-uv, tox-uv-bare) covers
tests/test_toolchain_config_gate.py:438:    forbidden_packages = {"uv", "tox", "tox-uv", "tox-uv-bare"}
tests/test_toolchain_config_gate.py:445:        "all toolchain packages (tox, tox-uv-bare, pytest, black, ruff, mypy) into [project.optional-dependencies].dev, "
tox.ini:13:# either way. The pin was briefly `tox-uv-bare` because outside FHS that
```

TOXUVBARE_HITS = 25

## D-15 classification

Each hit's surrounding sentence was re-read in the merged tree (not copied from RESEARCH's
pre-edit table) to assign its class.

| # | Location | Class | Why |
|---|----------|-------|-----|
| 1 | `CLAUDE.md:77` | C1 | "The pin was earlier `tox-uv-bare` ... the NixOS FHS shims now handle that, which is why plain `tox-uv` is correct again" — past tense, accurate history of the pin |
| 2 | `tests/test_pdf_render_gate.py:167` | C1 | "cause was removed by QUA-04 (2026-08-10; `tox-uv` -> `tox-uv-bare` drops" — describes the historical QUA-04 move as past |
| 3 | `tests/test_toolchain_config_gate.py:6` | C1 | "Phase 45.2's migration from tox-uv to tox-uv-bare" — accurate history |
| 4 | `tests/test_toolchain_config_gate.py:36` | C2 | "MUST name `tox-uv` ... MUST NOT name `tox-uv-bare`" — states the gate's required/forbidden values |
| 5 | `tests/test_toolchain_config_gate.py:41` | C1 | "stub-ld defect QUA-04 fixed by moving to `tox-uv-bare` no longer bites" — accurate statement that a historical fix no longer applies, not a claim that `tox-uv-bare` is current |
| 6 | `tests/test_toolchain_config_gate.py:46` | C1 | Citation path to `65-REVERT-EVIDENCE.md` — historical reference |
| 7 | `tests/test_toolchain_config_gate.py:51` | C2 | "tox-uv, tox-uv-bare (by normalized distribution name)" — lists the G6 forbidden/compared names |
| 8 | `tests/test_toolchain_config_gate.py:269` | C2 | Docstring: "MUST name tox-uv, MUST NOT name tox-uv-bare" — states the gate's required/forbidden values |
| 9 | `tests/test_toolchain_config_gate.py:276` | C1 | "fixed by moving to `tox-uv-bare` no longer bites. Without `tox-uv`, tox-uv's" — same accurate historical statement as #5, restated in the function docstring |
| 10 | `tests/test_toolchain_config_gate.py:289` | C1 | "The naming trap: 'tox-uv-bare' contains the substring 'tox-uv'" — a durable, time-independent fact about the two strings, not a claim about which is pinned now |
| 11 | `tests/test_toolchain_config_gate.py:297` | C1 | "Naming `tox-uv` in the dev extra pulls in `tox-uv-bare` transitively" — accurate description of the current transitive-dependency shape, not a claim that `tox-uv-bare` is the direct pin |
| 12 | `tests/test_toolchain_config_gate.py:300` | C2 | "it forbids the `dev` extra naming `tox-uv-bare` directly as a literal entry" — states what the gate forbids |
| 13 | `tests/test_toolchain_config_gate.py:302` | C1 | "CLAUDE.md's own ... sentence named `tox-uv-bare` as deliberate when Phase 65's revert landed" — past tense, describes CLAUDE.md's superseded wording as history (rewritten by wave-1's D-13) |
| 14 | `tests/test_toolchain_config_gate.py:305` | C1 | "keeping `tox-uv-bare` only as history" — states the current, accurate disposition of the name |
| 15 | `tests/test_toolchain_config_gate.py:308` | C1 | Citation path to `65-REVERT-EVIDENCE.md` — historical reference |
| 16 | `tests/test_toolchain_config_gate.py:359` | C2 | "G5 requirement 2 (Phase 65 revert): dev extra MUST NOT name tox-uv-bare directly" — comment naming the forbidden value |
| 17 | `tests/test_toolchain_config_gate.py:360` | C2 | `assert canonicalize_name("tox-uv-bare") not in dev_names` — code naming the forbidden value (untouched assertion logic) |
| 18 | `tests/test_toolchain_config_gate.py:361` | C2 | "dev extra names 'tox-uv-bare' directly ..." — assertion failure message naming the forbidden value |
| 19 | `tests/test_toolchain_config_gate.py:364` | C1 | "tox-uv-bare stays present only as tox-uv's own exact-version transitive dependency ... which is expected" — accurate current-state fact about the lock file |
| 20 | `tests/test_toolchain_config_gate.py:366` | C2 | "it forbids the dev extra naming tox-uv-bare as a literal entry" — states what the assertion forbids |
| 21 | `tests/test_toolchain_config_gate.py:374` | C2 | "[project].dependencies MUST NOT name any of: uv, tox, tox-uv, tox-uv-bare" — forbidden-list docstring |
| 22 | `tests/test_toolchain_config_gate.py:396` | C2 | "The forbidden list (uv, tox, tox-uv, tox-uv-bare) covers all possible toolchain packages" — forbidden-list description |
| 23 | `tests/test_toolchain_config_gate.py:438` | C2 | `forbidden_packages = {"uv", "tox", "tox-uv", "tox-uv-bare"}` — code defining the forbidden set |
| 24 | `tests/test_toolchain_config_gate.py:445` | C1 | "Phase 45.2's fix moved all toolchain packages (tox, tox-uv-bare, pytest, black, ruff, mypy) into ... dev" — accurate history of what Phase 45.2 did |
| 25 | `tox.ini:13` | C1 | "The pin was briefly `tox-uv-bare` because outside FHS that bundled `uv` could not exec on NixOS" — past tense, accurate history |

C1_ROWS = 14
C2_ROWS = 11
C3_ROWS = 0

14 + 11 = 25 = TOXUVBARE_HITS. No row is C3.

## SC#2 reading

Negative checks (file-scoped, from the plan's own verify command):

```
$ grep -qF '(with `tox-uv-bare`)' CLAUDE.md; echo "exit:$?"
exit:1
$ grep -qF 'package is also deliberate' CLAUDE.md; echo "exit:$?"
exit:1
$ grep -qF '"simplify"' CLAUDE.md; echo "exit:$?"
exit:1
$ grep -qF 'tox-uv-bare pinned via' tox.ini; echo "exit:$?"
exit:1
$ grep -qF 'tox-uv-bare>=1.35' tox.ini; echo "exit:$?"
exit:1
$ grep -qE 'still names|until Phase 68|goes stale as of this revert' tests/test_toolchain_config_gate.py; echo "exit:$?"
exit:1
```

All six exit 1 (no match) — none of the six stale C3 sentences RESEARCH found before the
wave-1 edits survive in the merged tree.

```
$ uv run tox config -e py312 --core -k requires
[testenv:py312]

[tox]
requires =
  tox-uv~=1.35
  tox
```

`tox config` prints `tox-uv~=1.35`, not `tox-uv-bare`.

SC2_VERDICT = MET (`C3_ROWS = 0` and every negative check and the `tox config` read-back hold)

## Task 1 commit

Committed below (evidence file only, this task's share).
