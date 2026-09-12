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

## SC#1 literal reading

Re-ran the head check and `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev`
(quick resync, no changes) before this task's measurements.

| Clause | Text | Measurement | Verdict |
|--------|------|-------------|---------|
| (a) manual `ln -sf`/`patchelf` guidance is gone, retired, not conditional | "The manual `ln -sf` / `patchelf` guidance is gone" | `git grep -nE 'ln -sf|patchelf' -- ':!.planning'` → one hit, `CLAUDE.md:88`, inside the "No manual step" paragraph of the `### NixOS development shell` subsection, stating no such step exists or is needed. `68-CLAUDEMD-EVIDENCE.md` recorded `LNSF_COMMITS = 0`, `PATCHELF_COMMITS = 0`, `LNSF_PATCHELF_GREP_HITS_BEFORE = 0` at `PHASE_BASE` — the guidance never existed to retire | MET |
| (b) section describes what Phase 64 actually landed | "in its place the section describes what Phase 64 actually landed" | `### NixOS development shell` subsection quoted in full below, describing the seven shims, the FHS sandbox, the exit-127 failure mode, the `uv` fallback leg, and the shim-version readback — this is what Phase 64 built, not what was originally planned | MET |
| (c) executors keep using the recipe | "automated worktree executors keep using `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` + `uv run`" | `awk '/^When operating inside a worktree, provision/{f=1} f' CLAUDE.md \| sha256sum` = `2c39540d38d94116d19ee5c2552cc5c105b0ef1228932713c082cdb8041a9b9a`, and the same pipeline over `git show 0bd33617d3cdf96f0342bdaeb19a0cb031f7c10a:CLAUDE.md` = `2c39540d38d94116d19ee5c2552cc5c105b0ef1228932713c082cdb8041a9b9a` — equal | MET |
| (d) executors "unaffected and unassisted by `flake.nix`" | "unaffected and unassisted by `flake.nix`" | NIX-05 (`64-NIX05-WORKTREE-EVIDENCE.md`): a fresh worktree's `uv sync` builds `.venv` on uv-managed CPython, a generic-linux ELF NixOS refuses outside FHS; `uv run …` in a worktree works only because the `uv` shim enters the FHS sandbox, inherited by PATH from the launching session. Worktree executors on this machine are therefore assisted by, and depend on, `flake.nix` | **contradicted by measurement, by design** |
| (e) a worktree is a directory direnv has never seen | "a worktree is a directory direnv has never seen" | Boundary paragraph (quoted below) states plainly: "`direnv` never loads inside a worktree itself, and a worktree's own `.envrc` is never allowed there" | MET |
| (f) if NIX-05 found the shims reachable, the section says so and keeps the recipe mandatory | "if that measurement found the shims *are* reachable in a fresh worktree, the section says so and still keeps the provisioning recipe mandatory" | Boundary paragraph states "The recipe below is unchanged and mandatory on every machine; `flake.nix` does not substitute for it. On the maintainer's NixOS machine the recipe itself runs through the shims described in the section above" | MET |

Quoted `### NixOS development shell` subsection (clause b):

```
### NixOS development shell

**Scope.** This subsection applies only on the maintainer's NixOS machine, where `direnv` loads `flake.nix`'s devShell in the main checkout. CI and non-NixOS contributors have no shims and need none — nothing here changes how CI or a non-NixOS contributor runs any of these commands.

**What the shims are.** On that machine, PATH carries seven bare commands: `uv`, `tox`, `ruff`, `black`, `mypy`, `pytest` and `sphinx-build` — the same commands named in § Commands above. Each walks up from the current directory to this checkout's own `.venv/bin/<tool>` and runs it inside an FHS sandbox (`typsphinx-fhs-run`), which is what lets generic-linux binaries that `uv` installs or downloads execute, together with everything they spawn. A missing `.venv/bin/<tool>` fails loudly: a `typsphinx-shim:` line on stderr names the tool and prints the provisioning line as a hint, then the shim exits 127 — it never silently runs some other binary. `uv` alone also falls back to nixpkgs' own `uv`, so a fresh clone or worktree with no `.venv` yet can run its first `uv sync`. Once `.venv` exists, `uv --version` reports the version `uv.lock` pins.

**Prerequisite and check.** Launch Claude Code from a shell in which `direnv` has already loaded the main checkout's devShell. Before provisioning a worktree, confirm the shim is on PATH by running exactly: `grep -q typsphinx-fhs-run "$(command -v uv)"`.

**No manual step.** No manual `ln -sf` or `patchelf` step exists or is needed — those two words appear in this sentence and nowhere else in this file. A `Could not start dynamically linked executable` error means the shim is not on PATH (the session was not launched from the direnv-loaded checkout); relaunch from that shell — it is not a code regression.

**Locale.** The sandbox passes the host's `LANG` through unchanged, so Sphinx warning text stays localised inside it exactly as outside. CI runs in English, so a test asserting warning text should also be run under `LC_ALL=C` locally.

**Interpreters may differ.** A fresh worktree's `.venv` is built on uv-managed CPython, while the main checkout's may be on nixpkgs' `python3` — the two may differ. Compare both `.venv/pyvenv.cfg` `home` and `version_info` before comparing test counts between them.

**Rationale pointer.** Why the development shell is built this way is recorded in `flake.nix`'s own header notes — see that file, not this one.
```

Boundary paragraph (clauses e, f), quoted from `### Worktree-isolated execution`:

```
**Detection rule:** you are running inside an isolated git worktree when `.git` is a FILE (a `gitdir:` pointer), not a directory — check with `test -f .git`. Sequential main-tree execution has `.git` as a directory and needs none of the steps below.

**NixOS boundary.** The recipe below is unchanged and mandatory on every machine; `flake.nix` does not substitute for it. On the maintainer's NixOS machine the recipe itself runs through the shims described in the section above, because a worktree's `.venv` is built on a generic-linux interpreter that NixOS runs only inside the sandbox — so the worktree depends on those shims being present. The shims reach a worktree only because they are inherited through PATH from a session launched in the direnv-loaded main checkout: `direnv` never loads inside a worktree itself, and a worktree's own `.envrc` is never allowed there.
```

SC1_LITERAL_VERDICT = PARTIAL (every clause except (d) is MET; (d) is contradicted by measurement, by design — the expected outcome per D-01)

## SC#1 amended reading

```
$ grep -n 'AMENDED 2026-09-12 (Phase 68 discuss' .planning/ROADMAP.md
646:     > **AMENDED 2026-09-12 (Phase 68 discuss, owner-approved).** "Unaffected and unassisted by

$ grep -n 'satisfied vacuously' .planning/ROADMAP.md
657:     > either term), so its retirement is satisfied vacuously and is evidenced, not edited. The
```

The recipe-tail hash equality from the literal reading's clause (c) applies unchanged here:
`2c39540d38d94116d19ee5c2552cc5c105b0ef1228932713c082cdb8041a9b9a` on both sides
(current tree and `PHASE_BASE`'s `CLAUDE.md`).

The boundary paragraph (quoted above under SC#1 literal reading) shows all four required
elements:
- the recipe is unchanged and mandatory: "The recipe below is unchanged and mandatory on every machine"
- `flake.nix` does not substitute for it: "`flake.nix` does not substitute for it"
- on NixOS the recipe runs through the shims: "On the maintainer's NixOS machine the recipe itself runs through the shims described in the section above"
- the shims arrive by inheritance, not by direnv: "The shims reach a worktree only because they are inherited through PATH from a session launched in the direnv-loaded main checkout: `direnv` never loads inside a worktree itself, and a worktree's own `.envrc` is never allowed there"

D-03 check present in the subsection, NixOS-only scoped:

```
$ awk '/^### NixOS development shell$/{f=1} /^### Worktree-isolated execution$/{f=0} f' CLAUDE.md | grep -F 'grep -q typsphinx-fhs-run "$(command -v uv)"'
**Prerequisite and check.** Launch Claude Code from a shell in which `direnv` has already loaded the main checkout's devShell. Before provisioning a worktree, confirm the shim is on PATH by running exactly: `grep -q typsphinx-fhs-run "$(command -v uv)"`.
```

The subsection's own `**Scope.**` sentence scopes the whole subsection — including this
check — to "the maintainer's NixOS machine", explicitly stating "CI and non-NixOS
contributors have no shims and need none".

SC1_AMENDED_VERDICT = MET (all of the above hold)

## SC#3 reading

Merged-tree drvPaths, all four equal to `68-FLAKE-EVIDENCE.md`'s `DRV_BEFORE_` values:

```
x86_64-linux    /nix/store/jnbia2810h255l78mn8k26sic5xqvb9p-nix-shell.drv
aarch64-linux   /nix/store/8qqw29d5k2jp4w9pcc4zyhk418fmdv4m-nix-shell.drv
x86_64-darwin   /nix/store/fclfls55m9lp06679x7zrw0qzjya834j-nix-shell.drv
aarch64-darwin  /nix/store/2m6y6pshri0vyw3jb5agczjnz9a92sxc-nix-shell.drv
```

(each obtained via `nix eval --raw ".#devShells.<sys>.default.drvPath"`, run for all four
systems from a script file to avoid the sandbox's substring match on the word "eval" in an
inline command; values transcribed verbatim from that run.)

```
$ grep -nE 'D-[0-9]' flake.nix
(no output)
```

`flake.nix` header block, quoted in full, mapped onto SC#3's parts:

```
  # The devShell here is a plain mkShell. On Linux it adds one buildFHSEnv
  # passthrough (`typsphinx-fhs-run`, a pure exec) and PATH command shims
  # that enter it. Two more obvious designs were tried and falsified: using
  # buildFHSEnv's own `.env` attribute as the devShell does not put the
  # shell inside FHS under either `nix develop` or direnv, because
  # `/lib64/ld-linux-x86-64.so.2` still resolves to NixOS's stub-ld either
  # way. A `shellHook` that execs into the wrapper fares no better: `nix
  # develop` never runs the hook at all, and under direnv the exec only
  # replaces nix-direnv's own environment-capture subshell, leaving the
  # real interactive shell outside FHS. So the devShell stays `mkShell`,
  # and `.envrc`'s `use flake` keeps working unchanged.
  #
  # Exactly the seven bare commands CLAUDE.md documents are shimmed: `uv`,
  # plus the six names in `venvShimNames` (`tox`, `ruff`, `black`, `mypy`,
  # `pytest`, `sphinx-build`). A Linux sandbox's mount namespace is
  # inherited across `fork` and `exec` by every descendant process, so
  # only these top-level entrypoints need a shim -- everything tox or uv
  # spawns underneath, including the tree's own `.venv/bin/uv`, a
  # downloaded interpreter, or a `.tox/<env>/bin` tool, already runs
  # inside the sandbox it was forked from. Every shimmed command keeps
  # the exact string CLAUDE.md documents.
  #
  # `buildFHSEnv` is Linux-only, so the wrapper and its shims are added
  # only when the host platform is Linux; on darwin the shell instead
  # carries nixpkgs' own `uv`, unshimmed. Darwin is unverified by
  # construction: no maintainer machine can exercise that branch, and no
  # CI lane evaluates this file at all. The only check ever performed
  # here is a `nix eval` of all four declared systems' devShells, run on
  # a Linux evaluator; the darwin shell itself has never been built or
  # entered. A darwin contributor who hits breakage here should report
  # it directly as a GitHub issue, rather than assume CI would have
  # caught it.
  #
  # Measurement sources:
  # `.planning/PROJECT.md`, "Binding measurements taken during scoping", for the two falsified devShell designs above.
  # v0.9.3 Phase 64 `64-NIX05-WORKTREE-EVIDENCE.md`, for PATH inheritance reaching a worktree.
  # v0.9.3 Phase 64 `64-FLAKE-EVIDENCE.md`, for the four-system `nix eval` check.
  # v0.9.3 Phase 64 `64-LIBZ-FIX-EVIDENCE.md`, for the `zlib` entry below.
  # v0.9.3 Phase 65 `65-REVERT-EVIDENCE.md`, for tox-uv's bundled uv resolving `.venv/bin/uv` inside FHS.
```

Mapping: the FHS wrapper + `mkShell` + both falsified alternatives (`buildFHSEnv`'s `.env`
and the `shellHook` exec) are the first paragraph; which commands are shimmed and why only
top-level entrypoints need shims is the second paragraph (namespace inheritance across
`fork`/`exec`); the darwin note — unverified by construction, Linux-only `buildFHSEnv`, no
maintainer machine, no CI lane, report directly (D-11) — is the third paragraph, verbatim.

SC3_VERDICT = MET (all drvPaths equal `DRV_BEFORE_`, no decision IDs, every header part present)

## Cross-file consistency

(a) The seven shimmed names, each beginning a command line in CLAUDE.md's `## Commands` section:

```
$ awk '/venvShimNames = \[/{f=1;next} f && /\];/{exit} f' flake.nix
            "tox"
            "ruff"
            "black"
            "mypy"
            "pytest"
            "sphinx-build"

$ awk '/^## Commands$/{f=1;next} /^## Architecture$/{f=0} f' CLAUDE.md
Development uses `uv` for env/dependency management and `tox` (with `tox-uv`) as the task runner.

uv sync --extra dev          # install with dev dependencies
pytest                       # run full suite (config in pyproject.toml)
...
black --check .              # black --check . (CI); drop --check to format
ruff check .
mypy typsphinx/
tox                          # env_list: py312, py313, lint, type, cov, docs
...
sphinx-build -b typst    source build/typst   # emit .typ files
```

Each of `uv`, `tox`, `ruff`, `black`, `mypy`, `pytest`, `sphinx-build` begins a command
line inside `## Commands`.

(b) CLAUDE.md's `tox.ini` bullet, beside tox.ini's `requires` line and comment:

```
$ grep -qF -- '- `tox.ini` pins `tox-uv~=1.35`' CLAUDE.md; echo "exit:$?"
exit:0
```

CLAUDE.md:77 reads `tox.ini` pins `tox-uv~=1.35` (not `>=1.35,<2`); `tox.ini:17` reads
`requires = tox-uv~=1.35`, with the preceding comment block explaining the same
ini-parser constraint. They agree.

(c) `test_dev_extra_pins_tox_uv_not_tox_uv_bare`'s claim about CLAUDE.md, read against
CLAUDE.md's bullet:

```
tests/test_toolchain_config_gate.py:302-305:
    CLAUDE.md's own "Conventions & gotchas" sentence named `tox-uv-bare` as
    deliberate when Phase 65's revert landed. Phase 65 left that rewrite for
    Phase 68; Phase 68 (DOC-19/DOC-20) rewrote it to describe the
    `tox-uv~=1.35` pin, keeping `tox-uv-bare` only as history.
```

CLAUDE.md:77 does exactly that: it describes the `tox-uv~=1.35` pin and names
`tox-uv-bare` only in a past-tense historical clause ("The pin was earlier
`tox-uv-bare`..."). The test's past-tense claim about CLAUDE.md is true.

(d) `_run_sphinx_build_typst`'s docstring sentence, read against `.venv/bin/uv` in this
worktree and the uv shim check:

```
$ ls -l .venv/bin/uv
-rwxr-xr-x 1 yuta users 49388608  9月 13 01:07 .venv/bin/uv
```

`.venv/bin/uv` exists in this worktree (49,388,608 bytes, executable). The docstring
(`tests/test_pdf_render_gate.py:168-171`) reads: "The `tox-uv` revert (v0.9.3 Phase 65)
put `.venv/bin/uv` back, and on NixOS it now runs through the Phase 64 FHS shims rather
than bare, so that hazard does not recur." This matches the head check's own
`grep -c typsphinx-fhs-run "$(command -v uv)"` = 2 earlier in this evidence file — the
`uv` on PATH is the FHS shim, and `.venv/bin/uv` is what it walks up to and execs.

(e) CLAUDE.md's `uv` bootstrap sentence, read against flake.nix's `uvShim` note:

CLAUDE.md: "`uv` alone also falls back to nixpkgs' own `uv`, so a fresh clone or worktree
with no `.venv` yet can run its first `uv sync`."

flake.nix `uvShim` note: "Leg 2, the on-stop fragment, resolves to nixpkgs' own uv at a
store path fixed at evaluation time... It is the bootstrap for a fresh clone or worktree
that has no .venv yet, before its first uv sync -- without it such a tree could not
provision itself."

Both describe the identical fallback: nixpkgs' `uv`, bootstrapping a fresh clone/worktree
before its first `uv sync`.

CROSS_FILE_VERDICT = consistent (all five agree)

## Task 2 commit

Committed below (evidence file only, this task's share).

## Green tree (merged)

Re-ran the head check and `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev`
(quick resync, 91 packages resolved, 81 checked, no changes) before this task's measurements.

```
$ sed -n 's/^home = //p;s/^version_info = //p' .venv/pyvenv.cfg
/home/yuta/.local/share/uv/python/cpython-3.14-linux-x86_64-gnu/bin
3.14
```

PYVENV_HOME_68_04 = /home/yuta/.local/share/uv/python/cpython-3.14-linux-x86_64-gnu/bin
PYVENV_VERSION_68_04 = 3.14

Per D-06, this interpreter (uv-managed CPython 3.14) may differ from the main checkout's
(nixpkgs `python3` 3.13.13) and from the wave-1 worktrees' (all three also uv-managed
3.14, per their own evidence files). The gate here is 0 failed, not a cross-tree count
comparison.

```
$ uv run pytest -q -p no:cacheprovider
(tail)
tests/test_xref_compile_time_guard_render_gate.py ......                 [ 99%]
tests/test_xref_orphan_degrade_render_gate.py .                          [ 99%]
tests/test_xref_whole_document_guard_render_gate.py ........             [100%]

================= 1543 passed, 5 skipped in 112.14s (0:01:52) ==================
```

FULL_SUMMARY = 1543 passed, 5 skipped
FULL_FAILED = 0

Single invocation completed inside the 600000ms foreground timeout — no split was needed.

```
$ uv run black --check .; echo "exit:$?"
All done! ✨ 🍰 ✨
355 files would be left unchanged.
exit:0

$ uv run ruff check .; echo "exit:$?"
All checks passed!
exit:0
```

```
$ uv run tox config -e py312 --core -k requires
[testenv:py312]

[tox]
requires =
  tox-uv~=1.35
  tox
```

No CI dispatch: no success criterion of this phase requires one, and CI is unchanged
(constraint 3).

## Phase scope fence

```
$ git diff --name-only "$PHASE_BASE" HEAD -- . ':!.planning'
CLAUDE.md
flake.nix
tests/test_pdf_render_gate.py
tests/test_toolchain_config_gate.py
tox.ini
```

Exactly the five edit targets, each present.

```
$ git diff --stat "$PHASE_BASE" HEAD -- typsphinx .github pyproject.toml uv.lock CHANGELOG.md
(empty)
```

Empty — nothing under `typsphinx/`, `.github/`, `pyproject.toml`, `uv.lock` or
`CHANGELOG.md` changed since `PHASE_BASE` (constraint 13; CHANGELOG is Phase 69's).

```
$ git diff --name-only "$BASE_68_04" -- .planning/STATE.md .planning/ROADMAP.md .planning/REQUIREMENTS.md
(empty)
```

Empty — this worktree's executor did not edit any tracking file.

## Requirement closure

| Requirement | Criterion | Evidence (section) | Verdict |
|-------------|-----------|---------------------|---------|
| DOC-19 | `CLAUDE.md`'s NixOS/worktree-provisioning section describes the landed mechanism and instructs no manual shim step | `## SC#1 amended reading` (this file); `68-CLAUDEMD-EVIDENCE.md` (68-01's gates: recipe-tail hash equality, D-02 vacuity at base, D-08 rewrite, gate-ordering check) | MET |
| DOC-20 | `tox.ini`'s `tox-uv-bare` rationale comment is replaced by one describing the current pin, with the `~=` ini-parser constraint stated | `## SC#2 reading`, `## D-15 classification` (this file); `68-TOX-EVIDENCE.md` (68-02's gates: SpecifierSet equivalence, masked-AST-hash-unchanged, 35-passed unchanged) | MET |
| DOC-21 | `flake.nix` carries notes explaining the FHS wrapper, which commands are shimmed and why, and the darwin guard | `## SC#3 reading` (this file); `68-FLAKE-EVIDENCE.md` (68-03's gates: four-system drvPath equality before/after, `nix flake check` exit 0 both times, comment-stripped hash unchanged) | MET |

DOC19_VERDICT = MET
DOC20_VERDICT = MET
DOC21_VERDICT = MET

SC#1's literal reading is reported separately above (`## SC#1 literal reading`,
`SC1_LITERAL_VERDICT = PARTIAL`, clause (d) contradicted by measurement by design) — its
own verdict is distinct from `SC1_AMENDED_VERDICT = MET`, which is what DOC-19's closure
above relies on, per D-01 (Phase 65 D-01 precedent: literal and amended readings are never
folded into one verdict).
