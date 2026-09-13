# Architecture Research

**Domain:** Nix/uv/tox toolchain repair for a Python packaging project (typsphinx v0.9.3)
**Researched:** 2026-09-02
**Confidence:** MEDIUM — mechanisms (bwrap namespace inheritance, GitHub Actions token/recursion
rules, buildFHSEnv idiom) are HIGH confidence from documented behavior and a well-known nixpkgs
precedent (`pkgs.steam-run`); the exact env-var/`$HOME`/PATH passthrough of THIS project's specific
`buildFHSEnv` invocation, and whether the shim PATH survives into an executor's freshly created
worktree, are unverified and flagged as experiments below (PROJECT.md itself lists both as open).

This is not a product-architecture document — v0.9.3 changes zero runtime/product code. It is an
integration map for three new/changed toolchain pieces against the existing devShell → tox →
`uv sync --locked` → CI pipeline.

## Standard Architecture

### System Overview — current pipeline and where the three new pieces attach

```
┌─────────────────────────────────────────────────────────────────────┐
│  Local NixOS dev machine (flake.nix, .envrc, direnv installed)      │
│                                                                       │
│   mkShell "default" devShell  ─┐  packages: nodejs, pnpm, git,       │
│                                 │  python3, uv  (+ NEW: FHS shims)   │
│                                 ▼                                    │
│   PATH: [shim: uv] [shim: tox] [shim: ruff] [shim: black]           │
│         [shim: mypy] [shim: pytest]  ← NEW, replaces bare pkgs.uv   │
│                                 │                                    │
│         each shim: exec <fhs-wrapper>/bin/typsphinx-fhs \           │
│                       "$(resolve .venv/bin/<tool> from $PWD)" "$@"  │
│                                 │                                    │
│                                 ▼                                    │
│              buildFHSEnv-produced bwrap sandbox (ONE shared          │
│              derivation, Linux-only, NEW)                            │
│                                 │  (mount-namespace: inherited by    │
│                                 │   every fork/exec child below)     │
│                                 ▼                                    │
│   tox (uv-venv-lock-runner) ──▶ .venv/bin/uv (PyPI-wheel ELF,       │
│         │                        now executable — CHANGED:           │
│         │                        tox-uv-bare → tox-uv)               │
│         ▼                                                            │
│   .tox/py312/bin/{python,ruff,black,mypy,pytest}  (downloaded        │
│   generic-linux-ELF CPython + tools — all inherit the same sandbox) │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  Isolated git worktree (executor)                                    │
│  flake.nix/.envrc present (checked out); direnv trust is PER-PATH   │
│  and NOT inherited from the main tree — open question, see Q3        │
│                                                                       │
│  env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev   │
│  uv run <tool>            ← UNCHANGED by this milestone              │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  GitHub Actions (ubuntu-latest/windows-latest/macos-latest)          │
│  — NOT NixOS, NOT touched by FHS work at all                         │
│                                                                       │
│  dependabot/pip/<bump> branch                                        │
│        │  pyproject.toml bumped, uv.lock stale                       │
│        ▼                                                             │
│  NEW: dependabot-lock.yml  (pull_request, actor==dependabot[bot])   │
│        │  uv lock  →  commit uv.lock back to the PR branch           │
│        ▼                                                             │
│  ci.yml (11× `uv sync --locked` steps) — now installs cleanly        │
│  drift.yml (weekly, separate: `main` @ latest-resolvable, unrelated) │
└─────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | This milestone |
|-----------|----------------|-----------------|
| `flake.nix` `devShells.<system>.default` | Puts `nodejs`/`pnpm`/`git`/`python3`/`uv` and now the FHS shims on PATH via `mkShell` | MODIFIED (Linux branch only; darwin untouched — `buildFHSEnv` is Linux-only) |
| Shared `buildFHSEnv` derivation (new, unnamed here `typsphinx-fhs`) | One bwrap sandbox capable of `exec`-ing an arbitrary absolute-path command inside it (`runScript = "bash -c 'exec \"$@\"'"`, the `pkgs.steam-run` idiom) | NEW |
| Per-command shim scripts (`uv`, `tox`, `ruff`, `black`, `mypy`, `pytest`) | Resolve the project's own `.venv/bin/<tool>` by walking up from `$PWD`, then `exec` it through the shared FHS sandbox | NEW |
| `tox` (`uv-venv-lock-runner`) | Provisions `.tox/<env>/` via `.venv/bin/uv`, downloads pyXXX interpreters, runs `ruff`/`black`/`mypy`/`pytest` inside `.tox/<env>/bin/` | UNCHANGED logic; now runs successfully under FHS because it inherits the shim's sandbox |
| `pyproject.toml` dev extra / `tox.ini` `requires` | Declares which `tox`-driving `uv` plugin is installed | MODIFIED: `tox-uv-bare` → `tox-uv` |
| `ci.yml` / `drift.yml` | GitHub-hosted lanes (Ubuntu/Windows/macOS runners) — generic-linux ELF already executes natively there | UNCHANGED (explicitly out of scope) |
| `.github/dependabot.yml` | `package-ecosystem: "pip"` — bumps `pyproject.toml`, does **not** touch `uv.lock` | UNCHANGED under the scoped design (see Anti-Patterns for the alternative) |
| New `dependabot-lock.yml` workflow | Regenerates and commits `uv.lock` on dependabot PR branches so the 11 `--locked` steps stop refusing them | NEW file |

## Recommended Project Structure

No new source directories. Everything is at the existing repo root:

```
flake.nix                          # MODIFIED — add FHS derivation + shims, system-guarded
tox.ini                            # MODIFIED — s/tox-uv-bare/tox-uv/, requires comment rewritten
pyproject.toml                     # MODIFIED — dev extra: tox-uv-bare → tox-uv pin
CLAUDE.md                          # MODIFIED — NixOS/worktree section rewritten for the new mechanism
.github/workflows/
├── ci.yml                         # UNCHANGED (explicit scope decision)
├── drift.yml                      # UNCHANGED
└── dependabot-lock.yml            # NEW — the uv.lock regeneration workflow
```

Keep the FHS derivation and shims **inside `flake.nix`** rather than splitting into a
`nix/fhs-shims.nix` import: the file is currently 40 lines and single-purpose, and PROJECT.md's own
scope note ("`flake.nix`'s own structure notes" under Documentation follow-through) implies the
maintainer expects to keep reading the whole file in one place. Split out only if the shim list
grows past the five bare-name tools already enumerated (`uv`, `tox`, `ruff`, `black`, `mypy`,
`pytest`).

## Architectural Patterns

### Pattern 1: One shared FHS sandbox derivation, N thin command-name shims

**What:** A single `pkgs.buildFHSEnv` derivation whose `runScript` is `exec "$@"` (the same idiom
nixpkgs' own `pkgs.steam-run` uses to let you prefix arbitrary unpatched binaries: `steam-run
./some-elf-binary args...`). Every tool name that needs to escape the "generic-linux ELF can't
find its loader" problem gets its own tiny `writeShellScriptBin` on the devShell's PATH; each shim
does two things and nothing else: (1) locate the real binary — `.venv/bin/<name>` — by walking up
from `$PWD` (not a hardcoded path, since the caller's cwd is the project root OR any subdirectory,
including inside a worktree at an arbitrary filesystem location, including `docs/` when tox's
`changedir = docs` is active); (2) `exec <fhs>/bin/typsphinx-fhs "$resolved_path" "$@"`.

**When to use:** Any command name the project's own workflow invokes directly by bare name —
cross-referenced against CLAUDE.md's documented command list: `uv`, `pytest`, `black`, `ruff`,
`mypy`, `tox`. Do **not** try to build one `buildFHSEnv` per tool — `buildFHSEnv` evaluation is not
free, and the whole point of the shared-sandbox pattern is that a single sandbox, once entered,
covers the entire descendant process tree for free (Pattern 2).

**Trade-offs:** A thin `exec` wrapper is the only design that doesn't silently break the
`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync` provisioning idiom CLAUDE.md already
mandates for worktrees — if the shim (or `buildFHSEnv`'s wrapper) cleared or reset environment
variables (e.g. via `env -i` or bwrap's `--clearenv`), that `-u` trick's effect would be lost before
`uv` ever saw it. `bwrap` does not clear the calling environment by default and `buildFHSEnv`'s
generated wrapper does not either, so plain `exec "$@"` is safe — but this specific project's
invocation has not been run end-to-end yet; flag as an experiment (see Gaps).

**Example (shape, not literal Nix — verify syntax during planning):**
```nix
# shared sandbox, Linux only
fhs = pkgs.buildFHSEnv {
  name = "typsphinx-fhs";
  targetPkgs = _: [ ];              # only need dynamic-linker/libc compat, not a package set
  runScript = "${pkgs.writeShellScript "fhs-entry" ''exec "$@"''}";
};

# one shim, repeated per tool name in [ "uv" "tox" "ruff" "black" "mypy" "pytest" ]
shim = name: pkgs.writeShellScriptBin name ''
  dir="$PWD"
  while [ "$dir" != "/" ]; do
    if [ -x "$dir/.venv/bin/${name}" ]; then
      exec ${fhs}/bin/typsphinx-fhs "$dir/.venv/bin/${name}" "$@"
    fi
    dir=$(dirname "$dir")
  done
  echo "typsphinx-fhs shim: no .venv/bin/${name} found upward from $PWD" >&2
  exit 127
'';
```

### Pattern 2: Namespace inheritance answers the tox process-tree question directly

**What:** `bwrap` (what `buildFHSEnv` wraps) establishes Linux namespaces (mount namespace, and
others) on the process it execs. Namespaces are a kernel property attached to a process and are
**inherited across `fork()`/`exec()`** by every descendant, exactly like any other process
attribute (cwd, uid, open fds) — a child does not need to "re-enter" the sandbox; it is already
inside it because it was spawned by a process that was.

**When to use — direct answer to "does tox's own subprocess tree need per-tool shims":** No. If the
top-level command the user or CI types is one of the shimmed entrypoints (`tox`, or `uv` when it's
`uv run tox …`), then:

```
shim:tox  (enters FHS sandbox)
  └─ tox (python process, inside sandbox)
      └─ uv-venv-lock-runner → exec .venv/bin/uv sync   (absolute path, ELF, inherits sandbox)
          └─ uv downloads/execs pyXXX interpreter        (ELF, inherits sandbox)
              └─ .tox/py312/bin/{ruff,black,mypy,pytest} (inherits sandbox — no shim needed here)
```

Only the **top-level entrypoints that a human or a workflow step types directly** need a shim:
`uv`, `tox`, and — because CLAUDE.md's documented commands section also lists them as directly
invokable — `ruff`, `black`, `mypy`, `pytest`. Everything `tox` spawns underneath any of those is
covered for free. This also explains, and retires, the manual per-worktree `ln -sf`/`patchelf` step
PROJECT.md says eight phase summaries recorded: that step existed because nothing upstream was
sandboxing the *whole* subprocess tree, so each generic-linux ELF binary (the `.tox/pyXXX`-downloaded
CPython in particular) had to be patched individually, worktree by worktree.

**Trade-offs / what still needs an experiment:** The reasoning above is a correct description of how
Linux namespaces work; what is *not yet measured for this project* is whether `buildFHSEnv`'s
specific generated wrapper preserves `$PWD`, `$HOME`, and the full calling environment when invoked
as a one-shot `exec` from a shim (as opposed to the interactively-entered `nix develop` shell
PROJECT.md's binding measurements were taken from). PROJECT.md explicitly lists "FHS behaviour
inside an executor's isolated worktree" as **unverified, to be closed during planning** — treat that
as the concrete experiment: shim-invoke `tox -e py312` from a fresh worktree and confirm `ruff`,
`mypy`, `pytest`, and the tox-downloaded CPython all execute with zero additional per-tool shims.

### Pattern 3: `mkShell` stays the devShell; FHS is opt-in per-shim, never the shell itself

**What:** PROJECT.md's binding measurements already foreclose two tempting designs: `buildFHSEnv
NAME.env` as the devShell (`/lib64/ld-linux-x86-64.so.2` still resolves to `stub-ld` under both
`nix develop` and direnv), and a `shellHook` that `exec`s into the FHS wrapper (`nix develop` never
runs the hook at all; under direnv the `exec` only replaces nix-direnv's capture subshell, not the
real interactive/command environment). The only design PROJECT.md's own experimentation validated
is per-command shims sitting on a plain `mkShell`'s PATH.

**When to use:** Always, for this project — this is not a stylistic choice, it is the only option
proven to work by the binding measurements already taken.

**Trade-offs:** Requires a `pkgs.stdenv.isLinux` (or `system`-string) guard, since `buildFHSEnv`
does not exist on Darwin. Concretely: `packages = commonPackages ++ (if pkgs.stdenv.isLinux then
linuxShims else [ pkgs.uv ]);` — darwin's `devShells.x86_64-darwin.default` /
`aarch64-darwin.default` keep exactly today's plain `pkgs.uv`, unmodified, because macOS wheels are
Mach-O and never hit the generic-linux-ELF problem this milestone exists to solve.

## Data Flow

### Local dev / CI-matching command flow (post-milestone)

```
developer types `ruff check .`
    ↓
PATH resolves to the NEW shim (not nixpkgs' pkgs.uv — that package is dropped from
`packages` on Linux to avoid a PATH-ordering race with the uv shim)
    ↓
shim walks $PWD upward, finds .venv/bin/ruff (the uv.lock-pinned 0.15.20, not nixpkgs' 0.15.14)
    ↓
shim execs it through the shared FHS sandbox
    ↓
ruff 0.15.20 runs — matches CI's `ruff check .` exactly
```

### Worktree-executor flow (what changes vs. what stays fixed)

```
STAYS FIXED (CLAUDE.md, unchanged by this milestone):
  env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev
  uv run <tool>                       # every subsequent command via `uv run`

CHANGES (only if the direnv-trust question below resolves unfavorably):
  `uv` itself must be the FHS shim for `uv run <tool>` to carry FHS into every downstream
  process — which is exactly the existing "run everything via uv run" rule, so if the `uv`
  shim is reachable on PATH inside the worktree, NO other CLAUDE.md wording needs to change.
  The four other shims (tox/ruff/black/mypy/pytest as bare names) are not load-bearing for
  the worktree flow specifically — they matter for direct-CLI/CI-matching usage, not for
  `uv run`-mediated worktree execution.

OPEN QUESTION (flagged, not settled here):
  direnv trust (`.direnv/allow`) is keyed by path, so a freshly created worktree directory
  is, in the general case, UNTRUSTED even though the exact same flake.nix content was already
  allowed in the main tree. Whether the harness's Bash-tool invocations even run direnv's
  shell hook at all (each call's own tool description says cwd persists but "shell state does
  not" between calls — direnv's hook normally fires on an interactive shell's prompt, which a
  one-shot non-interactive Bash call may never trigger) is unverified. If the shim PATH is not
  present, the worktree flow's `uv run <tool>` silently falls back to whatever `uv`/`tool` was
  already resolvable — this is exactly the class of "45-test false alarm" PROJECT.md cites
  Phase 38-07 for. Resolve during planning with a concrete experiment: cd into a freshly
  created worktree via the Bash tool and check `command -v uv` / `type uv` resolves to the
  shim, not to a bare system/nixpkgs uv.
```

### Dependabot lockfile-regeneration flow

```
dependabot[bot] opens/updates dependabot/pip/<bump>   (pyproject.toml bumped, uv.lock stale)
    ↓
NEW dependabot-lock.yml fires on `pull_request` (opened/synchronize), gated on
  `github.actor == 'dependabot[bot]'` (mirrors the two real stale PRs: #123 ruff, #128 docutils)
    ↓
checks out the PR head, runs `uv lock`, diffs uv.lock
    ↓
if changed: commit + push to the SAME dependabot branch
    ↓
   ⚠ GOTCHA (documented GitHub behavior, not this-repo-specific):
   Dependabot PRs get a READ-ONLY default GITHUB_TOKEN when triggered via `pull_request`
   (a deliberate GitHub security restriction, independent of this repo's own settings) AND,
   separately, ANY push made using a workflow's own GITHUB_TOKEN does not itself trigger a
   new `pull_request`/`push` workflow run (GitHub's anti-recursion rule; workflow_dispatch/
   repository_dispatch are the only triggers exempted). Both mean: a same-token commit either
   cannot push at all, or pushes but never re-triggers ci.yml on the new HEAD SHA — required
   checks stay "pending" forever on that commit and the PR cannot merge. The community pattern
   (browniebroke.com's "Keep uv.lock file up-to-date with Dependabot updates" post) works
   around this with a separate fine-grained PAT/deploy-key secret for the checkout+push step.
   This is a decision the plan needs to make explicitly (new repo secret vs. accept that the
   regen commit needs a manual/`workflow_dispatch` re-run to get ci.yml green).
    ↓
ci.yml's 11× `uv sync --extra dev --locked` steps now install cleanly against the regenerated lock
    ↓
`--locked`'s reproducibility guarantee is preserved everywhere (in scope, unchanged) — this
workflow's job is only to make the LOCKFILE match the PR's already-bumped pyproject.toml, not
to weaken what `--locked` itself enforces
```

`drift.yml` is unrelated traffic on the same graph, not a collision: it runs on a schedule against
`main` (not any dependabot branch), calls `uv lock --upgrade` (resolve to the newest ALLOWED
versions across the board) rather than a plain `uv lock` (resolve within the ALREADY-bumped
constraint one specific dependabot PR proposes), and reports failure via a deduplicated GitHub issue
rather than a commit. The two workflows solve different problems (proactive "does `main` still
resolve at the frontier" vs. reactive "make this one PR's lockfile match its own diff") and never
touch the same branch or file in the same run.

## Anti-Patterns

### Anti-Pattern 1: Landing the `tox-uv-bare` → `tox-uv` revert before the FHS shims are proven

**What people would do:** Flip the pin in `pyproject.toml`/`tox.ini` first, since it's the smaller,
mechanical-looking diff, and land the Nix work afterward as a follow-up.

**Why it's wrong:** `tox-uv-bare` exists *specifically* because plain `tox-uv` depends on the PyPI
`uv` wheel, whose unpatched generic-linux ELF binary lands at `.venv/bin/uv` and cannot execute on
NixOS without FHS — that is the exact QUA-04 defect this milestone dissolves. Reverting the pin
before the FHS sandbox exists and is verified reintroduces that defect for the entire window between
the two commits, breaking `tox -e lint`/`-e type`/`-e py312`/`-e py313` on the maintainer's own
machine — the opposite of this milestone's stated goal.

**Do this instead:** Build order in Pattern 2 / Suggested Build Order below — FHS shims land and are
verified to make `.venv/bin/uv` executable *first* (this can be proven experimentally even before
committing the `tox-uv` pin flip, e.g. by temporarily forcing `tox-uv` in a scratch check), *then*
the pin revert lands.

### Anti-Pattern 2: Assuming the FHS work has any bearing on the dependabot workflow's success

**What people would do:** Sequence the dependabot lockfile-regeneration workflow after the FHS work
"because they're both toolchain fixes in the same milestone."

**Why it's wrong:** `ci.yml` runs exclusively on GitHub-hosted `ubuntu-latest`/`windows-latest`/
`macos-latest` runners, never on NixOS, and is explicitly out of scope for this milestone (no `nix`
job is added). Generic-linux ELF binaries execute natively on GitHub's `ubuntu-latest`. The
dependabot workflow's success or failure is entirely about GitHub Actions token permissions and
`--locked`/lockfile consistency — it has zero technical dependency on `flake.nix` or the `tox-uv`
pin.

**Do this instead:** Treat the FHS/`tox-uv` work and the dependabot-lock workflow as two independent
build tracks that can proceed in parallel; the only shared resource is calendar time in one
milestone, not a code dependency.

### Anti-Pattern 3 (flagged as a genuine open alternative, not a mistake): building a custom regen workflow when Dependabot's own `uv` ecosystem already exists

**What's in scope today:** `.github/dependabot.yml` uses `package-ecosystem: "pip"`, which bumps
`pyproject.toml` version constraints but does not understand or touch `uv.lock` at all — this is the
actual root cause of the two stale PRs (#123, #128) failing at the `uv sync --locked` install step.
Dependabot has shipped native `package-ecosystem: "uv"` support (GA since March 2025) which updates
`uv.lock` directly as part of Dependabot's own PR, using Dependabot's own service credentials (not a
workflow's `GITHUB_TOKEN`), which sidesteps the read-only-token and anti-recursion gotchas in the
Data Flow section above entirely.

**Why this document doesn't just recommend it:** PROJECT.md's Target Features commits explicitly to
"A `uv lock` regeneration workflow for dependabot PRs" as the chosen shape for this milestone — this
is a locked scoping decision, not something this research should override. It is recorded here
because it is directly relevant to the CI-graph risk analysis in Q4 and the roadmap/planning phase
should be aware a simpler native alternative exists, in case the token/permissions friction turns out
to be more expensive than expected during planning.

## Integration Points

### New vs. modified files (explicit)

| File | New/Modified | Mechanism |
|------|---------------|-----------|
| `flake.nix` | Modified | Add one `buildFHSEnv` derivation + up to 6 `writeShellScriptBin` shims (`uv`, `tox`, `ruff`, `black`, `mypy`, `pytest`), guarded by `pkgs.stdenv.isLinux`; darwin systems' package list unchanged; devShell stays `mkShell` |
| `pyproject.toml` | Modified | `dev` extra: `"tox-uv-bare>=1.35,<2"` → `"tox-uv>=1.35,<2"` |
| `tox.ini` | Modified | `requires = tox-uv-bare~=1.35` → `requires = tox-uv~=1.35` (keep the `~=` form — the comma-split parser bug it works around is orthogonal to the package name); rewrite the surrounding rationale comment |
| `CLAUDE.md` | Modified | Rewrite the "Do not simplify it back to tox-uv" bullet (now stale — this milestone does exactly that, safely, because of the FHS layer) and the worktree-provisioning section's NixOS framing |
| `.github/workflows/dependabot-lock.yml` (name TBD in planning) | New | `pull_request` trigger, actor-gated on `dependabot[bot]`, runs `uv lock`, commits back to the PR branch |
| `.github/dependabot.yml` | Unchanged (under the scoped design) | Stays `package-ecosystem: "pip"`; see Anti-Pattern 3 for the alternative that WOULD modify this file |
| `.github/workflows/ci.yml`, `drift.yml` | Unchanged | Explicit scope decision — no `nix` job added, `astral-sh/setup-uv`'s `version: "latest"` stays floating |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| devShell PATH ↔ shared FHS derivation | shim script `exec`s the FHS wrapper with an absolute-path argv | Shim resolves `.venv/bin/<tool>` on the HOST side (before entering the sandbox) by walking up from `$PWD` — sandbox PATH internals are irrelevant to finding the target binary |
| FHS sandbox ↔ tox's own subprocess tree | Linux namespace inheritance across fork/exec | No boundary to cross — this is the load-bearing simplification: one sandboxed entrypoint covers `tox` → `uv-venv-lock-runner` → `.venv/bin/uv` → downloaded CPython → `.tox/<env>/bin/{ruff,mypy,pytest}` for free |
| Worktree provisioning ↔ FHS shims | PATH inheritance / direnv trust | Unresolved — see Data Flow "OPEN QUESTION"; do not assume it works without the flagged experiment |
| dependabot-lock.yml ↔ ci.yml | Git push to the same branch, hoping to re-trigger `pull_request` | Read-only default token + anti-recursion rule for `GITHUB_TOKEN`-authored pushes; needs an explicit PAT/deploy-key decision or an accepted manual re-run step |
| dependabot-lock.yml ↔ drift.yml | None (different branches, different trigger, different `uv lock` mode) | Confirmed non-colliding by design, not by luck |

## Suggested Build Order

1. **FHS wrapper + command-name shims in `flake.nix`.** No dependency on anything else in this
   milestone. Build and verify in isolation first: `ruff --version` reports the `.venv`-pinned
   `0.15.20` (not nixpkgs' `0.15.14`); `tox -e lint`/`-e type`/`-e py312`/`-e py313` all green
   *while temporarily forcing `tox-uv` (not yet the committed pin) to prove `.venv/bin/uv`
   executes under the sandbox*; and — separately — the worktree-executor experiment flagged in
   Data Flow (does the shim PATH reach a freshly created worktree at all).

2. **Revert `tox-uv-bare` → `tox-uv`** in `pyproject.toml` + `tox.ini`. **Depends on (1)** being
   proven, not merely written — landing this first re-opens the exact QUA-04 unpatched-ELF defect
   for the window before (1) lands (Anti-Pattern 1). These two steps can ship in the same phase/
   plan, but the pin flip's own verification gate must run *after* the FHS mechanism, not before.

3. **Documentation follow-through** (`CLAUDE.md`'s NixOS/worktree section, `tox.ini`'s rationale
   comment, `flake.nix`'s structure notes). **Depends on (1)+(2)** being final — it describes the
   new mechanism and removes stale guidance (the "do not revert to tox-uv" instruction, and any
   remaining references to the manual `ln -sf`/`patchelf` workaround this retires).

4. **`uv.lock` regeneration workflow for dependabot PRs.** **Independent of (1)–(3)** — runs on
   GitHub-hosted runners, never touches NixOS/FHS territory (Anti-Pattern 2). Can be built and
   merged in parallel with the flake/tox track. Its own build order: draft the workflow, decide the
   token/permissions approach (default `GITHUB_TOKEN` accepting a manual re-run vs. a new PAT/
   deploy-key secret), then validate.

5. **Prove (4) on a real dependabot PR, then dispose of #123/#128.** **Depends on (4)** existing
   and firing successfully at least once — PROJECT.md is explicit that a hand-made branch with a
   fresh `uv.lock` does not satisfy this; it must be observed on an actual dependabot-authored PR,
   most naturally one of the two already-open stale ones, before either is merged or closed on its
   own merits.

Tracks {1,2,3} and {4,5} have no code dependency on each other and can run as two parallel phases;
only the internal ordering *within* each track is load-bearing.

## Gaps / Experiments Needed During Planning

- **Env-var and `$HOME` passthrough inside the specific `buildFHSEnv` invocation this project ends
  up with** — reasoned as "preserved by default" from `bwrap`/`buildFHSEnv` general behavior, but
  not measured for this repo. Matters for `uv`'s cache/python-install directories under
  `~/.cache/uv`, `~/.local/share/uv/python`.
- **Worktree PATH/direnv-trust reachability** — whether a shim on the main tree's devShell PATH is
  actually resolvable from inside a freshly created, not-yet-`direnv allow`-ed worktree, and whether
  the harness's non-interactive Bash-tool invocations even run direnv's shell hook. Flagged
  explicitly in PROJECT.md as unverified.
- **GitHub Actions token strategy for `dependabot-lock.yml`** — whether to accept the default
  `GITHUB_TOKEN`'s read-only-and-non-retriggering limitations (and rely on a manual/`workflow_dispatch`
  re-run to get `ci.yml` green) or add a new PAT/deploy-key secret. This is a decision, not a
  measurement, but it must be made explicitly rather than discovered as a stuck-PR surprise.

## Sources

- `/home/yuta/Documents/typsphinx/.planning/PROJECT.md` — `## Current Milestone: v0.9.3` section
  (binding measurements, HIGH confidence — curated, owner-verified project record)
- `/home/yuta/Documents/typsphinx/flake.nix`, `tox.ini`, `pyproject.toml`, `CLAUDE.md` (HIGH —
  primary source, current repo state)
- `/home/yuta/Documents/typsphinx/.github/workflows/ci.yml`, `drift.yml`,
  `/home/yuta/Documents/typsphinx/.github/dependabot.yml` (HIGH — primary source)
- NixOS Discourse, "Simple uv usage" — confirms `buildFHSenv` as the standard NixOS answer for
  running unpatched PyPI-wheel binaries, and that `nix-shell`/`nix develop` "drops you into" the FHS
  env rather than the FHS env being usable as a bare devShell attribute (MEDIUM — community source,
  consistent with PROJECT.md's own binding measurement)
- nixpkgs `pkgs.steam-run` idiom — well-known prior art for "one shared `buildFHSEnv` sandbox,
  prefix arbitrary commands with it" (MEDIUM — general nixpkgs knowledge, not independently
  re-verified against this project's nixpkgs pin in this research pass)
- browniebroke.com, "Keep uv.lock file up-to-date with Dependabot updates" (2024-10-02) — documents
  the exact `uv lock` + commit-back pattern and its need for a PAT to work around GitHub's
  default-token restrictions on Dependabot-triggered workflow runs (MEDIUM — third-party blog,
  corroborated by GitHub's own documented token-permission and anti-recursion rules)
- `docs.astral.sh/uv/guides/integration/dependabot` — confirms native `package-ecosystem: "uv"`
  support exists as the alternative noted in Anti-Pattern 3 (HIGH — official Astral docs)
- `tox-dev/tox-uv` GitHub README — `uv` binary discovery order (`TOX_UV_PATH` → bundled `uv` wheel →
  system `uv` on PATH), grounding why `tox-uv-bare` avoids the bundled generic-linux ELF and plain
  `tox-uv` reintroduces it (HIGH — official project README)

---
*Architecture research for: typsphinx v0.9.3 toolchain/CI maintenance milestone*
*Researched: 2026-09-02*
