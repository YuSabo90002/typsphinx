# Phase 65: `tox-uv-bare` → `tox-uv` Revert, on the uv Path tox Actually Resolves - Research

**Researched:** 2026-09-12
**Domain:** tox plugin/package-name swap, `uv` binary discovery order, NixOS FHS sandbox, CI job census
**Confidence:** HIGH — every load-bearing claim in this document was executed against a live scratch
copy this session (labelled FORECAST throughout) or read from installed/upstream source; no claim
rests on training-data recall of `tox-uv`'s internals.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01: ROADMAP SC#3 and constraint 12 carry an `AMENDED 2026-09-12` block correcting the "different
  function" claim; the original text stays.** Measured: the installed `tox_uv/_venv.py:232-238`
  bundled step is literally `from uv import find_uv_bin; return find_uv_bin()`. No binary ships in
  the `tox-uv` wheel; "bundled" = the PyPI `uv` dependency's script, which `find_uv_bin()` returns as
  `<tox's own env>/bin/uv` — the same `.venv/bin/uv` file the Phase 64 `uv` shim's first leg resolves.
  So "bundled wheel vs shimmed/`.venv` binary" is a false dichotomy, and what separates a shell-level
  `find_uv_bin()` from a real tox run is only the calling process. The substantive requirement —
  observe from **inside** a real tox run, plus an isolated control — is unchanged and binding. Both
  AMENDED blocks were written and committed with this CONTEXT. The verifier reports the literal
  reading and the amended reading of SC#3 separately. `.planning/research/PITFALLS.md` Pitfall 1
  carries the same false claim and is left as archival research (not amended).

- **D-02: A bundled resolution inside FHS to the tree's own `.venv/bin/uv`, with the tox environment
  passing, closes SC#3 — no `TOX_UV_PATH` anywhere.** Observation: `tox -vv -e py312` via the shim in
  the executor worktree, capturing tox-uv's own DEBUG line
  `using bundled uv from: <worktree>/.venv/bin/uv [tox_uv/_venv.py:237]` verbatim, and the env's final
  `py312: OK`. The ROADMAP's recovery clause ("set `TOX_UV_PATH` or return to `-bare`") is **not
  triggered**: `TOX_UV_PATH=uv` would resolve through the shim to the very same file. Do not set
  `TOX_UV_PATH` in `flake.nix`, in `tox.ini` `setenv` (which would also reach CI), or in the shell. If
  the observation instead shows the `TOX_UV_PATH` or `PATH` branch firing, or a path other than the
  worktree's `.venv/bin/uv`, that is a DIVERGENT result — record it and HALT, do not "recover" on the
  executor's own judgement.
  **Version:** the bundled branch logs the path only, no version. The resolved binary's version must
  also be observed from inside the tox run and must equal `uv.lock`'s `uv` version exactly
  (constraint 6 — versions, not exit codes). The mechanism is Claude's discretion, but it must not
  leave a committed `tox.ini` change made solely for observation (a tox 4 `-x`/`--override` on the
  command line, or uv's own `-v` output inside the `-vv` log, are acceptable shapes).

- **D-03: The control runs in the executor worktree, from a dedicated venv built on the nix
  interpreter, never from the provisioned `.venv`.** Reason (measured): a fresh worktree's `uv sync`
  builds `.venv` on uv-managed CPython 3.14 — a generic-linux ELF — so running it outside FHS fails
  on `python3` first, which is exactly why the previous control isolated nothing. Shape: create a
  separate venv (not committed; outside the tracked tree or gitignored) with the nix `python3`
  (`/nix/store/…-python3-3.13.13`, confirm by `readlink -f` + `pyvenv.cfg` `home`, and record both —
  if the interpreter is not a nix store path the control is invalid), install the **lock-pinned**
  `tox-uv`/`tox-uv-bare`/`uv`/`tox` versions into it, and run
  `<control-venv>/bin/python -m tox -vv -e py312` against the worktree's edited `tox.ini`, invoked by
  absolute path so no shim is involved. Expected, and required to close: tox starts; the log shows
  `using bundled uv from: <control-venv>/bin/uv`; the first uv exec fails with `Could not start
  dynamically linked executable: …/bin/uv` and exit 127. Any failure before the uv exec means the
  control did not isolate the uv path and SC#3 stays open. Scratch pre-measurement (2026-09-12,
  `tox-uv 1.36.0`, `-e type`) reproduced exactly this shape — see `<specifics>`. Evidence is recorded
  verbatim in the phase's evidence markdown (Phase 64 D-05 convention: no new script, no new test).

- **D-04: Commit exactly what a plain `uv lock` produces, ride-along bumps included, and record
  them.** Measured in a scratch copy (uv 0.11.25 via the shim's nixpkgs leg): `Added tox-uv v1.36.0`,
  `Updated tox-uv-bare v1.35.2 -> v1.36.0`, `Added uv v0.12.13`; header stays `version = 1`,
  `revision = 3`; 48 changed lines. Re-running `uv lock --check` and `uv lock` with `uv 0.12.13` on
  that lock was a no-op (byte-identical). No `--upgrade`, no `--upgrade-package`, no pin to 1.35.2, no
  hand edit. Versions recorded literally at execution time (they may have moved since 2026-09-12). The
  commit touching `pyproject.toml` must list `uv.lock` in `git show --name-only`, and
  `uv sync --extra dev --locked` must exit 0 on the changed tree (SC#1). Record which `uv` binary and
  version performed the regeneration.

- **D-05: The maintainer-machine `uv` switch is accepted and recorded, and the shim's nixpkgs leg
  stays.** Once `.venv/bin/uv` exists, the Phase 64 `uv` shim's first leg resolves it, so every `uv`
  on this machine moves from nixpkgs `0.11.25` to the lock-pinned `uv` (0.12.13 at measurement; CI
  already installs `latest`, 0.12.x). Measured in the scratch tree: `uv --version` → `uv 0.12.13`.
  Record the before/after in evidence. Phase 64 D-02's leg 2 (nixpkgs store path) is **not** dropped
  here even though its reversibility note anticipated that: a fresh clone or a fresh worktree has no
  `.venv` until the first `uv sync`, so leg 2 is the bootstrap. Whether any documentation reflects
  this is Phase 68's call.

- **D-06: This phase edits only the `tox.ini` `requires` value, `pyproject.toml:38`, and `uv.lock` in
  the tree — not the comments that name `tox-uv-bare`.** The `tox.ini:4-10` rationale comment is
  DOC-20's by name ("`tox.ini`'s `tox-uv-bare` rationale comment is replaced…"), `CLAUDE.md:11` and
  `:77` are DOC-19's surface, and `flake.nix:93` ("does not exist until Phase 65's tox-uv revert
  installs it") is DOC-21's. Their staleness between Phase 65 and Phase 68 is an accepted,
  same-milestone interval. Evidence/planning files under `.planning/` are unrestricted.

  > **Research-time finding, not a locked decision — see `## Decision Conflicts` below.** A live full
  > pytest run against the swapped `pyproject.toml`/`tox.ini`/`uv.lock` shows this restriction is
  > incomplete: `tests/test_toolchain_config_gate.py::test_dev_extra_pins_tox_uv_bare_not_tox_uv`
  > FAILS after the swap, because it is a static gate asserting the exact opposite of what this phase
  > does. It is not covered by D-06's edit list. This is flagged for the owner, not silently expanded
  > into scope.

### Carried forward (not re-decided)

- Worktree isolation is the standing execution mode; every executor provisions with
  `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` and runs via `uv run`, and first
  confirms `command -v uv` / `command -v tox` point at the Phase 64 shims (Phase 64 D-09).
- TOX-04 exactly as SC#4 states: one `gh workflow run CI --ref <branch>` on the pushed post-revert
  tip, **completed**, every job's conclusion transcribed literally, both `windows-latest` and both
  `macos-latest` lanes named, `ruff`'s verdict from `Lint and Format Check` / `Run lint with tox`.
- No change under `typsphinx/`; no workflow edit; full pytest suite green at phase close; `@preview`
  count stays four.

### Claude's Discretion

- The exact mechanism for printing the resolved `uv` version from inside the tox run (D-02), within
  the no-committed-`tox.ini`-observation-edit constraint.
- How the control venv gets the lock-pinned versions (e.g. `uv export` filtered to the four packages,
  or explicit `==` pins read from `uv.lock`), and where it lives (not committed).
- Whether `tox -vv -e py312` in D-02 runs cold (`-r`) — recommended, so provisioning actually
  exercises the resolved `uv`.
- Whether and when the main checkout's `.venv` is re-synced after the worktree merge (it keeps working
  either way: without `.venv/bin/uv`, `tox-uv-bare`'s code path falls to `PATH` → the shim).
- Plan split and evidence file naming.

### Deferred Ideas (OUT OF SCOPE)

- Rewording `tox.ini`'s rationale comment, `CLAUDE.md:11`/`:77`, and `flake.nix:93` to reflect the
  landed `tox-uv` — Phase 68 (DOC-19/20/21), per D-06.
- Dropping the `uv` shim's nixpkgs leg — not done (D-05: it is the bootstrap); revisit only if a
  future phase provides another bootstrap path.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| TOX-01 | `pyproject.toml` declares `tox-uv` in place of `tox-uv-bare`, with `uv.lock` regenerated in lockstep | § Standard Stack, § Code Examples "Lock regeneration", verbatim FORECAST table row 1 — `uv lock` reproduces `Added tox-uv v1.36.0` / `Updated tox-uv-bare … -> v1.36.0` / `Added uv v0.12.13`; `uv sync --extra dev --locked` exits 0 |
| TOX-02 | `tox.ini`'s `requires` names `tox-uv` in the comma-free `~=` form, and `tox` starts | § Common Pitfalls "The ini-parser trap and the `--version` false negative", FORECAST rows 6-7 — `tox --version` does NOT exercise `requires`; `tox --showconfig -e py312` does (0.15s, exit 1 on the comma form, exit 0 on `~=`) |
| TOX-03 | the `uv` binary tox actually resolves is observed from inside a real tox run, with an isolated outside-FHS control proving the failure is the uv path rather than something that fails earlier | § Architecture Patterns "Discovery order", § Code Examples "D-02 observation" and "D-03 control", FORECAST rows 2-5, 8-9 |
| TOX-04 | CI is green on the revert across every lane, CI being the authority | § Validation Architecture, § Environment Availability (CI job census reused from Phase 64's 12-row baseline) |
</phase_requirements>

## Project Constraints (from CLAUDE.md)

- Worktree isolation is the **standing execution mode** for every executor on this project (not
  conditional on parallelism benefit): `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra
  dev`, then run everything via `uv run`.
- `tox.ini`'s comma-free `~=1.35` form for `requires` is explicitly documented as load-bearing in
  CLAUDE.md's own "Conventions & gotchas" — do not "simplify" it back to a comma-bearing range.
- `tox-uv-bare` is currently named in CLAUDE.md as the deliberate QUA-04 fix ("Do not 'simplify' it
  back to `tox-uv`") — this phase's revert makes that CLAUDE.md sentence stale. CLAUDE.md is DOC-19's
  surface (Phase 68), not this phase's; the interval is accepted (D-06).
- `black`/`ruff` lint and `mypy` type-check must both stay runnable via `tox -e lint` / `tox -e type`
  exactly as documented — the revert must not change tox environment names or invocation shape.
- No commands here modify the main checkout; all scratch measurement happened under
  `/tmp/claude-1000/.../scratchpad/research-65{,-stale}/`, confirmed by `git status --short` on the
  main checkout returning clean before and after this research session.

## Summary

The revert is mechanically a two-token edit (`pyproject.toml:38`, `tox.ini`'s `requires` line) plus a
`uv lock` regeneration, and every one of D-01 through D-05's measured claims reproduced exactly in a
fresh scratch copy this session: `uv lock` adds `tox-uv v1.36.0`, bumps `tox-uv-bare` to the same
version (lockstep confirmed live against PyPI's JSON API), and adds `uv v0.12.13`; `uv sync --extra
dev --locked` exits 0; inside the FHS sandbox a real `tox -vv -e py312 -r` run logs
`using bundled uv from: <tree>/.venv/bin/uv [tox_uv/_venv.py:237]` and — critically — a `-vv` run
(verbosity 4, confirmed from `tox`'s own `DEFAULT_VERBOSITY = 2` plus two `-v` flags) makes tox-uv
append `-v` to its own `uv venv`/`uv sync` subprocess commands, and uv's own verbose startup banner
(`DEBUG uv 0.12.13 (x86_64-unknown-linux-gnu)`) appears in the tox log immediately after — closing
D-02's "version, not just path" requirement with **zero committed `tox.ini` edits**. The isolated
D-03 control also reproduced exactly: a venv built on the nix `python3-3.13.13` interpreter (confirmed
non-generic-linux, executes host-side) resolves the SAME bundled-uv code path but to `<ctrl-venv>/bin/
uv`, a generic-linux ELF, which fails immediately with `Could not start dynamically linked executable`
/ exit 127 on the very first `uv venv` subprocess — no earlier failure, unlike the prior control that
died on `.venv/bin/python3`.

The one finding this research surfaces that is **not** covered by any locked decision: a live full
pytest run (1548 tests) against the swapped tree fails exactly one test —
`tests/test_toolchain_config_gate.py::test_dev_extra_pins_tox_uv_bare_not_tox_uv` — a static gate from
Phase 45.2 that asserts the dev extra **must** name `tox-uv-bare` and **must not** name `tox-uv`,
which is the literal opposite of TOX-01. D-06 confines this phase's edits to three files that do not
include this test. Constraint 13 ("every phase closes green on the full pytest suite") and this
phase's own SC's cannot both be satisfied without touching a fourth file. This is recorded under
`## Decision Conflicts` for the owner, not resolved unilaterally.

A second, lower-stakes finding for the "main checkout re-sync" discretion item: tox's own `[tox]
requires` provisioning mechanism tolerates a stale `.venv` gracefully — it builds a side-car
`.tox/.tox` meta-environment (via the `uv` resolved from `PATH`, i.e. the Phase 64 shim's nixpkgs
leg) to satisfy the new `requires = tox-uv~=1.35` and re-execs itself there, so `tox -e <any>` does
**not** break in the interval before the maintainer's own `.venv` is resynced. But a bare `uv run
<tool>` does **not** perform that resync on its own — `uv run` without `--extra dev` implicitly syncs
only the base project, leaving the dev extra (and therefore `.venv/bin/uv`) untouched. Only the
CLAUDE.md-documented `uv sync --extra dev` (with or without `env -u …`) actually installs
`.venv/bin/uv` and upgrades `tox-uv-bare` in place.

**Primary recommendation:** execute D-01 through D-05 exactly as decided (nothing here falsifies
them); add one out-of-footprint task — updating (not deleting) `test_dev_extra_pins_tox_uv_bare_not_
tox_uv` — after putting the conflict to the owner, since it is required for constraint 13's
full-green-suite invariant and for TOX-01 to actually land cleanly.

## Architectural Responsibility Map

This phase has no application-tier capabilities — it is entirely toolchain/build-plane. Mapped for
completeness against the template's tiers:

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Dependency declaration (`pyproject.toml`, `uv.lock`) | Build / Toolchain | — | Governs what `uv sync` installs; no runtime code path |
| `uv` binary discovery (`tox_uv/_venv.py`) | Build / Toolchain | OS/Sandbox (NixOS FHS) | A tox plugin's own subprocess-resolution logic, executed at tox-provisioning time, not at Sphinx build/runtime |
| CI job execution (`ci.yml`) | CI / Build | — | GitHub-hosted runners; unaffected by NixOS-specific tiers |
| `typsphinx/` (the Sphinx extension itself) | N/A | N/A | Explicitly untouched this milestone (constraint 13) |

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `tox-uv` | 1.36.0 [VERIFIED: PyPI JSON API, `https://pypi.org/pypi/tox-uv/1.36.0/json`, fetched 2026-09-12] | tox plugin swapping `virtualenv`+pip for `uv` inside tox environments | Upstream-maintained (`tox-dev/tox-uv`), the package this project used before Phase 45.2's NixOS-specific `-bare` workaround, and the mechanism `uv-venv-lock-runner` (already in use) depends on |
| `tox-uv-bare` | 1.36.0 (transitive, via `tox-uv`'s own `tox-uv-bare==1.36.0` pin) [VERIFIED: PyPI JSON API — `requires_dist: ['tox-uv-bare==1.36.0', 'uv<1,>=0.9.27']`, fetched live 2026-09-12] | Provides the `tox_uv` Python module (the actual plugin code); `tox-uv` is a thin meta-package adding only the `uv` dependency | Confirmed: both packages release in exact version lockstep across their last 8 published versions (1.33.2 … 1.36.0) [VERIFIED: PyPI JSON API, both `/pypi/tox-uv/json` and `/pypi/tox-uv-bare/json` releases lists compared live] |
| `uv` (the PyPI package, distinct from the system/nixpkgs `uv` binary) | 0.12.13 at scratch measurement 2026-09-12 [VERIFIED: `uv lock` output in scratch copy — `Added uv v0.12.13`; cross-checked against `uv.lock`'s own recorded `upload-time = "2026-09-10T19:25:…"` for that version] | New transitive dev dependency, installed into `.venv`; its `find_uv_bin()` is what `tox_uv/_venv.py`'s bundled branch calls | Required by `tox-uv`'s own dependency spec (`uv<1,>=0.9.27`); not independently chosen |

### Package Legitimacy Audit

`uv` is the only genuinely new distribution entering the dependency tree (as a **transitive** — not
direct — dev dependency, pulled in solely because `tox-uv` requires it). `tox-uv` was previously
installed on this exact machine before Phase 45.2's downgrade to `-bare` (i.e., it is not a novel
choice, it is the pre-45.2 status quo), and `tox-uv-bare` is already the currently-pinned dependency.

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| `tox-uv` | PyPI | Long-established (first tracked release far before 1.33.x; already used pre-Phase-45.2 in this repo) | High (tox's own recommended `uv` integration) | `github.com/tox-dev/tox-uv` | Not run through the automated `package-legitimacy check` seam this session (network-gated PyPI JSON fetch used directly instead, see below) — manually cross-checked: `tox-dev` org, matches the plugin already documented in `CLAUDE.md`'s own history | Approved — re-adoption of a previously-used, still-canonical package, not a new supply-chain surface |
| `tox-uv-bare` | PyPI | Same (companion package, same maintainers) | Same order of magnitude | Same repo | — | Already the current pin; version bump only |
| `uv` | PyPI | Astral's own flagship tool, multi-year, extremely high downloads | `astral-sh/uv` | — | Approved — this project already depends on `uv` as its primary package manager (installed via nixpkgs and via `setup-uv` in CI); adding the PyPI wheel as a transitive dev dependency does not introduce a new vendor, only a new **installation path** for a tool already fully trusted |

No `SLOP` or `SUS` verdicts. `uv.lock` records a `sha256` hash for every wheel/sdist of all three
packages (verified by reading `uv.lock:1420-1608` in the scratch copy — see § Security Domain), and
`uv sync --locked`/`--extra dev --locked` refuses to proceed on any hash mismatch, which is the
integrity control this addition rides on rather than a bespoke check.

**Installation:** no manual install step — `uv lock` (regenerating `uv.lock`) followed by
`uv sync --extra dev --locked` (already the standard provisioning line) is the entire mechanism.

**Version verification (live, this session):**
```
$ uv lock          # scratch copy, uv 0.11.25 via shim's nixpkgs leg
Resolved 91 packages in 1.17s
Added tox-uv v1.36.0
Updated tox-uv-bare v1.35.2 -> v1.36.0
Added uv v0.12.13
```

## Architecture Patterns

### `uv` Discovery Order Inside a Real Tox Run

```
tox -e py312 (or any uv-venv-lock-runner environment)
        │
        ▼
tox_uv._venv.UvVenv.uv   (cached_property — resolved ONCE per environment instance)
        │
        ├─ 1. TOX_UV_PATH set? ──yes──▶ shutil.which(TOX_UV_PATH); log WARNING "using uv from
        │                                TOX_UV_PATH: <path> (<version via subprocess --version>)"
        │         │no
        │         ▼
        ├─ 2. `from uv import find_uv_bin; find_uv_bin()` succeeds? ──yes──▶ log DEBUG
        │         │                       "using bundled uv from: <path>"  (NO version logged here —
        │         │                        find_uv_bin() returns the calling interpreter's OWN
        │         │                        venv/bin/uv, i.e. tox's own `.venv/bin/uv` once `uv` is
        │         │                        installed as a dependency)
        │         │no (ImportError/FileNotFoundError — e.g. tox-uv-bare, no `uv` package installed)
        │         ▼
        └─ 3. shutil.which("uv") on PATH ──▶ log DEBUG "using system uv from PATH: <path>
                                               (<version via subprocess --version>)"

Resolved binary is cached and reused for BOTH subprocess calls this env makes:
  - `uv venv -p <spec> --allow-existing [-v] ...`        (tox_uv/_venv.py:287, create_python_env)
  - `uv sync --locked --extra dev [--reinstall] [-v] -p <spec>`  (tox_uv/_run_lock.py:113, _setup_env)

`-v` is appended to BOTH subprocess commands only when tox's own verbosity > 3, i.e. `-vv` or higher
(tox's DEFAULT_VERBOSITY = 2, each `-v` flag adds 1 [VERIFIED: installed tox 4.56.1 source,
tox/config/cli/parser.py:133,495-501, quoted: `DEFAULT_VERBOSITY = 2` and
`verbosity.add_argument("-v", "--verbose", action="count", dest="verbose", ..., default=DEFAULT_VERBOSITY)`]).
uv's own `-v` startup banner (`DEBUG uv 0.12.13 (x86_64-unknown-linux-gnu)`) is what surfaces the
version in branch 2, where tox-uv itself logs no version.
```

### Pattern: Observing Branch + Path + Version From Inside a Real Tox Run (D-02)

**What:** run `tox -vv -e py312 -r` (verbosity ≥ 4, cold) through the Phase 64 shim, in the executor's
provisioned worktree, and grep the transcript for two adjacent classes of line.
**When to use:** exactly D-02's requirement — SC#3's "from inside a real tox run", no shell-level
`uv --version` or `uv.find_uv_bin()` probe.
**Example (FORECAST, this session, scratch copy):**
```
py312: 272 D using bundled uv from: <tree>/.venv/bin/uv [tox_uv/_venv.py:237]
...
py312: 276 W venv> .venv/bin/uv venv -p cpython3.12 --allow-existing '--prompt=…[py312]' -v --python-preference system <tree>/.tox/py312 [tox/tox_env/api.py:485]
DEBUG uv 0.12.13 (x86_64-unknown-linux-gnu)
...
py312: 391 W uv-sync> .venv/bin/uv sync --locked --python-preference system --extra dev --reinstall -v -p cpython3.12 [tox/tox_env/api.py:485]
DEBUG uv 0.12.13 (x86_64-unknown-linux-gnu)
...
  py312: OK (0.58 seconds)
```
The `using bundled uv from:` line gives the path and the fired branch (branch 2 — no `TOX_UV_PATH`,
no `PATH` fallback text present anywhere in the transcript). The `DEBUG uv 0.12.13 …` line immediately
following each `uv venv …-v…`/`uv sync …-v…` dispatch is uv's OWN version banner, captured by tox's
subprocess output relay — this is what closes the "version, not exit code" half of D-02 without
touching `tox.ini`.

### Pattern: The Isolated Outside-FHS Control (D-03)

**What:** a venv built on the nix `python3` interpreter (not the worktree's own `.venv`, which is
built on a generic-linux uv-managed CPython and would fail on the interpreter itself, isolating
nothing), with the four lock-pinned packages installed into it, invoked by absolute path with no shim
involved.
**Example (FORECAST, this session):**
```
$ /nix/store/l9k0…-python3-3.13.13/bin/python3 -m venv ctrl-venv
$ cat ctrl-venv/pyvenv.cfg
home = /nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin
executable = /nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin/python3.13
$ uv pip install --python ctrl-venv/bin/python3 "tox==4.56.1" "tox-uv==1.36.0" "tox-uv-bare==1.36.0" "uv==0.12.13"
 + tox==4.56.1
 + tox-uv==1.36.0
 + tox-uv-bare==1.36.0
 + uv==0.12.13
$ file ctrl-venv/bin/uv
ctrl-venv/bin/uv: ELF 64-bit LSB pie executable, ... dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, ... for GNU/Linux 2.6.32, ...
$ env PATH="/usr/bin:/bin" ctrl-venv/bin/python3 -m tox -vv -e py312 --workdir /tmp/ctrl-tox-workdir -r
py312: 93 D using bundled uv from: <tree>/ctrl-venv/bin/uv [tox_uv/_venv.py:237]
py312: 98 W venv> ctrl-venv/bin/uv venv -p cpython3.12 --allow-existing '--prompt=…[py312]' -v --python-preference system /tmp/ctrl-tox-workdir/py312 [tox/tox_env/api.py:485]
Could not start dynamically linked executable: <tree>/ctrl-venv/bin/uv
NixOS cannot run dynamically linked executables intended for generic linux environments out of the box. ...
py312: 100 C exit 127 (0.00 seconds) ...> ctrl-venv/bin/uv venv ... pid=… [tox/execute/api.py:308]
  py312: FAIL code 127 (0.00 seconds)
```
Tox **starts** (registered-plugins banner prints, environments resolve), the SAME bundled branch
fires, and the **first** subprocess exec — the `uv venv` call — is what fails, immediately, on the
`uv` binary itself. Nothing earlier fails (no interpreter-discovery error, no `requires` provisioning
error). `--workdir /tmp/ctrl-tox-workdir` isolates the run from the tree's own `.tox/`, confirmed by
inspecting `.tox/` afterward (unchanged; only `/tmp/ctrl-tox-workdir/py312` was created).

### Recommended Project Structure

No new files or directories. This phase edits exactly `pyproject.toml`, `tox.ini`, `uv.lock` (plus,
pending the owner's disposition of the Decision Conflict below, `tests/test_toolchain_config_gate.py`).
The control venv (D-03) and any scratch measurement live outside the tracked tree or gitignored, never
committed.

### Anti-Patterns to Avoid

- **Setting `TOX_UV_PATH` "just to be safe."** D-02 is explicit: this is the DIVERGENT-result recovery
  path, not the default. Setting it pre-emptively (in `flake.nix`, `tox.ini setenv`, or the shell)
  masks the very discovery-order question SC#3 exists to answer, and a `tox.ini setenv` would also
  reach CI, changing TOX-04's baseline silently.
- **Treating `tox --version` as proof `tox` starts (SC#2).** Measured this session: `tox --version`
  exits 0 even against the deliberately-broken comma-bearing `requires = tox-uv>=1.35,<2` — it never
  evaluates `[tox] requires` at all. Use a command that actually provisions/configures (see § Common
  Pitfalls).
- **Running the D-03 control from the worktree's own `.venv`.** That venv is built on uv-managed
  CPython (a generic-linux ELF itself), so it fails on the *interpreter*, before ever reaching the
  `uv` exec — reproducing the exact "isolated nothing" failure ROADMAP constraint 5(e) names.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Printing the resolved `uv` version from inside tox without editing `tox.ini` | A custom logging shim, a monkeypatch, a wrapper script around `uv` | `tox -vv` (verbosity ≥ 4) — tox-uv already appends `-v` to its own `uv venv`/`uv sync` calls at that verbosity, and `uv -v` already prints its own version banner | Zero new code, zero new committed file; the mechanism already exists in both `tox` and `uv` and was exercised live this session |
| Verifying the two packages release in lockstep | Manually diffing GitHub tags/changelogs | PyPI's JSON API (`/pypi/<name>/json`, `releases` keys) | Machine-readable, authoritative, and was fetched live this session for both packages — an assumption here is unnecessary when the check costs one HTTP request |
| Isolating the uv-exec failure from earlier failures | A patched/relinked `.venv/bin/python3`, or `patchelf` on the control | A venv built directly on the nix `python3` store path | `patchelf`/`autoPatchelfHook` are explicitly out of scope for this milestone (REQUIREMENTS.md § Out of Scope) and the nix-interpreter venv achieves the same isolation with zero extra machinery |

**Key insight:** every mechanism this phase needs (version disclosure, lockstep verification,
isolation) already exists in tools already in the dependency graph (`tox`'s own verbosity flag,
`uv`'s own `-v`, PyPI's own JSON API, nix's own store paths) — the temptation to add new
instrumentation should be resisted per D-02's explicit "no committed `tox.ini` change made solely for
observation" constraint.

## Runtime State Inventory

This is a rename/config-swap phase (the tool declared as the tox-uv provider changes name), so this
section is included per the trigger, even though it is not a data-migration phase in the usual sense.

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | None — no database, no user-facing collection, no ID scheme references `tox-uv`/`tox-uv-bare` by name. Verified by the repo-wide grep in § below. | None |
| Live service config | None found under this project's control. Dependabot's ecosystem/grouping config is a **different** requirement (DEP-01, Phase 66) and is untouched here. | None |
| OS-registered state | None — no Task Scheduler / launchd / systemd / pm2 registration references either package name. | None |
| Secrets/env vars | `TOX_UV_PATH` is a **documented recovery mechanism**, not a currently-set variable; measured absent in this session's shell (`env \| grep TOX_UV_PATH` empty) and must **stay** absent per D-02 unless a DIVERGENT result is found. | None unless DIVERGENT |
| Build artifacts / installed packages | **The maintainer's own main-checkout `.venv` is exactly this category, and it is the one real item here.** After the merge, `.venv` still has `tox-uv-bare==1.35.2` (or whatever was last synced) until an explicit `uv sync --extra dev` runs. Measured this session (scratch reproduction): a bare `uv run <tool>` (no `--extra dev`) does **not** trigger the resync — the dev extra is untouched, `tox-uv-bare` stays at its old pin, and no `.venv/bin/uv` appears. Only an explicit `uv sync --extra dev` (the CLAUDE.md-documented line) installs `.venv/bin/uv` and bumps `tox-uv-bare` to match the new lock. **Separately**, `tox`'s own `[tox] requires` provisioning tolerates the interval gracefully: `tox -e <any>` run against a stale `.venv` self-provisions a side-car `.tox/.tox` meta-environment via the `uv` resolved from PATH (the shim's nixpkgs leg) and re-execs there — it does not fail and does not require the maintainer to do anything first. | Code edit: none (mechanism already exists). Recommended: state explicitly in evidence that the main-checkout resync is **not required for correctness**, only for the maintainer's own `uv`/`tox-uv` versions to move onto the new pins (D-05's "accepted and recorded" framing) — and note that a bare `uv run` will NOT perform it. |

**Repo-wide grep performed:** `grep -rln "tox-uv-bare\|tox_uv_bare\|tox-uv\b" --include="*.py" tests/
typsphinx/ scripts/` → two files: `tests/test_toolchain_config_gate.py` (assertions — see § Decision
Conflicts) and `tests/test_pdf_render_gate.py` (one docstring/comment reference, line 167, no
assertion — becomes stale prose after the revert but does not fail any test; in scope for Phase 68's
documentation pass, not this phase's).

## Common Pitfalls

### Pitfall 1: `tox --version` does not prove SC#2's "`tox` starts"

**What goes wrong:** using `tox --version` as the smoke test for "the edited `tox.ini` parses" gives a
false pass — `tox --version` never evaluates `[tox] requires` at all.
**Why it happens:** `--version` is handled before tox's own config-loading machinery runs the ini-list
converter that splits `requires` on commas.
**How to avoid:** use a command that actually loads config, e.g. `tox --showconfig -e py312` (fast,
0.15s, no environment provisioning) or any real `-e <env>` invocation.
**Warning signs:** a "tox starts" claim backed only by `tox --version` output.
**Measured (FORECAST, this session):**
```
$ requires = tox-uv>=1.35,<2      # deliberately broken comma form
$ tox --version
4.56.1 from …/tox/__init__.py
registered plugins: tox-uv-bare-1.36.0 at … with uv==0.12.13
$ echo exit:$?
exit:0                             # FALSE PASS — requires was never evaluated

$ tox --showconfig -e py312
… packaging.requirements.InvalidRequirement: Expected package name at the start of dependency specifier
    <2
    ^
$ echo exit:$?
exit:1                             # correctly fails
```
With the correct `requires = tox-uv~=1.35` form restored, `tox --showconfig -e py312` exits 0 in
~0.17s.

### Pitfall 2: A stale main-checkout `.venv` is more forgiving than expected — but a bare `uv run` is not enough to fix it

**What goes wrong:** assuming the maintainer must manually intervene the moment `pyproject.toml`/
`tox.ini`/`uv.lock` land, or conversely assuming any `uv run` call auto-repairs the `.venv`.
**Why it happens:** two independent mechanisms are in play and have opposite generosity. tox's own
`[tox] requires` provisioning (`tox/provision.py`) self-heals via a side-car `.tox/.tox` environment
built with `uv` resolved from PATH — it does not need the outer `.venv` to be current at all. `uv
run`, by contrast, only implicitly syncs the **base** project unless `--extra dev` (or an equivalent
default-groups configuration) is given, so a plain `uv run <tool>` leaves a stale dev extra
(`tox-uv-bare` at its old version, no `.venv/bin/uv`) untouched.
**How to avoid:** state explicitly, in evidence and/or DOC-19 (Phase 68), that the documented
`uv sync --extra dev` line (already CLAUDE.md's provisioning idiom) is what performs the resync — not
"any `uv run` call."
**Warning signs:** an evidence note asserting "the venv updates itself the next time any command
runs" without specifying `--extra dev`.
**Measured (FORECAST, this session, `research-65-stale` scratch copy — old `.venv` built pre-swap,
`pyproject.toml`/`tox.ini`/`uv.lock` swapped afterward without a resync):**
```
$ uv run python --version         # no --extra dev
Uninstalled 1 package in 0.47ms
Installed 1 package in 0.85ms
Python 3.14.4
$ ls .venv/bin | grep '^uv$'; echo exit:$?
exit:1                             # uv NOT installed — dev extra untouched
$ .venv/bin/python -c "..." ; ls .venv/lib/python*/site-packages | grep '^tox'
tox_uv_bare-1.35.2.dist-info       # still the OLD version

$ env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev
 + tox-uv==1.36.0
 - tox-uv-bare==1.35.2
 + tox-uv-bare==1.36.0
 + uv==0.12.13
$ ls .venv/bin | grep '^uv$'; echo exit:$?
exit:0                             # now present

$ rm -rf .tox && timeout 60 tox -vv -e lint --notest     # BEFORE the resync above
ROOT: … will run in automatically provisioned tox, host …/.venv/bin/python is missing [requires (has)]: tox-uv~=1.35
.tox: … using system uv from PATH: /nix/store/…-uv/bin/uv (uv 0.11.25 …)
ROOT: … will run in a automatically provisioned python environment under …/.tox/.tox/bin/python
lint: … using bundled uv from: …/.tox/.tox/bin/uv [tox_uv/_venv.py:237]
  lint: OK (0.41 seconds)            # tox self-heals; outer .venv/bin left untouched
```

### Pitfall 3: A locked-decision edit footprint (D-06) collides with a pre-existing test that encodes the opposite decision

**What goes wrong:** planning strictly to D-06's three-file edit list, without re-measuring the full
suite against the swapped tree, ships a phase that cannot close green (constraint 13).
**Why it happens:** Phase 45.2 added a static pytest gate,
`tests/test_toolchain_config_gate.py::test_dev_extra_pins_tox_uv_bare_not_tox_uv`, whose entire
purpose was to fail loudly if anyone ever reverted `tox-uv-bare` back to `tox-uv` — which is precisely
what this phase does. D-06 was decided before this specific test collision was measured.
**How to avoid:** see `## Decision Conflicts` below — surface to the owner before writing the plan;
do not silently widen or silently ignore D-06.
**Warning signs:** `pytest tests/` reporting `1 failed, 1542 passed, 5 skipped` against an otherwise-
correct swap.
**Measured (FORECAST, this session, full suite, `research-65` scratch copy, `tox -vv -e py312 -r`
without `--notest`):**
```
FAILED tests/test_toolchain_config_gate.py::test_dev_extra_pins_tox_uv_bare_not_tox_uv
AssertionError: dev extra does not contain 'tox-uv-bare' (on normalized distribution name) -- ...
1 failed, 1542 passed, 5 skipped in 108.07s (0:01:48)
py312: FAIL code 1 (109.16 seconds)
```

## Code Examples

### Lock regeneration (TOX-01, D-04) — verbatim, this session

```
$ sed -i 's/"tox-uv-bare>=1.35,<2"/"tox-uv>=1.35,<2"/' pyproject.toml
$ sed -i 's/requires = tox-uv-bare~=1.35/requires = tox-uv~=1.35/' tox.ini
$ uv lock
Using CPython 3.14.4
Resolved 91 packages in 1.17s
Added tox-uv v1.36.0
Updated tox-uv-bare v1.35.2 -> v1.36.0
Added uv v0.12.13
$ sed -n '1,3p' uv.lock
version = 1
revision = 3
requires-python = ">=3.12"
$ diff /home/yuta/Documents/typsphinx/uv.lock uv.lock | wc -l
60
$ uv lock --check
Resolved 91 packages in 0.59ms
$ echo exit:$?
exit:0
$ uv sync --extra dev --locked
 ... (91 packages resolved, all installed)
$ echo exit:$?
exit:0
```

Note: this session's diff count (60 lines) differs from D-04's earlier same-day measurement (48
lines); both are legitimate — package indices move continuously and the exact diff size is not a
load-bearing number, only the `Added`/`Updated` shape and the unchanged `version = 1` / `revision = 3`
header are.

### `git show --name-only` shape (SC#1)

Not independently re-measured (standard git behavior, no tox/uv-specific nuance) — the executor's
real commit, made with `pyproject.toml` and `uv.lock` staged together, will show both files in
`git show --name-only HEAD`. The failure mode SC#1 names ("a commit touching only `pyproject.toml`")
is exactly what happens if `uv lock` is run but not staged, or is run in a separate commit.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|---------------|--------|
| `tox-uv` (bundled `uv` wheel, generic-linux ELF) | `tox-uv-bare` (system `uv` via `shutil.which`) | Phase 45.2, 2026-08-10 (QUA-04) | Fixed the maintainer's NixOS machine at the cost of a permanent CI/local divergence risk (SC#7's static gate) |
| `tox-uv-bare` | `tox-uv` (this phase) | Phase 65, pending | Restores upstream default; made safe by Phase 64's FHS wrapper, which makes the bundled `.venv/bin/uv` executable again on NixOS via the sandbox |

**Deprecated/outdated:** none of `tox`, `tox-uv`, `tox-uv-bare`, or `uv` deprecate anything relevant
here; `tox-uv` 1.36.0's own changelog (fetched via web search, not read from source — see Sources) is
minor: a flaky-test fix, a formatting-tooling swap, and Python 3.15 added to `tox-uv`'s own test
matrix [CITED: GitHub releases page for tox-dev/tox-uv, tag 1.36.0]. No incompatibility between
`tox-uv`/lock-pinned `uv` and `astral-sh/setup-uv@v7` surfaced in this search; absence of a hit is not
proof of absence and is not claimed as such.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | No known incompatibility exists between `tox-uv` 1.36.x / lock-pinned `uv` 0.12.13 and `astral-sh/setup-uv@v7`'s installed `uv` on `windows-latest`/`macos-latest` runners | State of the Art, Validation Architecture | If wrong, TOX-04's CI run could fail on a Windows/macOS-specific path-resolution edge (e.g. `.venv\Scripts\uv.exe` vs `find_uv_bin()`'s expectations) that this research did not reproduce locally (no Windows/macOS host available in this session) |
| A2 | `find_uv_bin()` (the `uv` PyPI package's own lookup function) resolves correctly to `.venv\Scripts\uv.exe` on Windows and `.venv/bin/uv` on macOS/Linux without special-casing beyond what `tox_uv/_venv.py`'s own `env_bin_dir()` already does (`Scripts` on `win32`, `bin` elsewhere) | Environment Availability, Validation Architecture | If wrong, one or more Windows/macOS lanes in TOX-04 could fail at the `uv venv`/`uv sync` provisioning step for a reason unrelated to this phase's edit — this is exactly why TOX-04 requires a real CI run rather than inference |
| A3 | `tox-uv` (as opposed to `tox-uv-bare`, previously installed pre-Phase-45.2 in this exact repo) carries no other behavioral difference beyond the `uv` dependency and its discovery-order branch — i.e. no other config-key or default changed between the two packages' `tox_uv` module versions in the interval | Standard Stack | Low risk (both packages ship the identical `tox_uv` module per D-01's own finding — `tox-uv-bare` IS where the code lives), but not independently re-diffed against every non-`uv`-related line of `_venv.py`/`_run_lock.py`/`_installer.py` |

## Open Questions

1. **Does the owner want `test_dev_extra_pins_tox_uv_bare_not_tox_uv` updated in this phase, or handled as a separate gap-closure step?**
   - What we know: the test fails deterministically and by design against the swapped tree; it is not
     in D-06's edit footprint; constraint 13 requires the full suite green at phase close.
   - What's unclear: whether the owner wants this folded into Phase 65's plan (a fourth edited file,
     contradicting D-06's literal text) or handled via an AMENDED block to D-06, or deferred to a
     gap-closure plan after the primary revert lands.
   - Recommendation: put the finding (already recorded under `## Decision Conflicts`) to the owner at
     `/gsd-plan-phase` time, before committing to a plan shape; the fix itself (inverting the two
     assertions and updating the docstring's historical framing) is small and low-risk once approved.

2. **Windows/macOS `uv` resolution under the bundled branch — genuinely unverified until TOX-04's real CI run.**
   - What we know: `env_bin_dir()` is OS-aware in source, and `setup-uv@v7`'s installed `uv` and the
     lock-pinned `uv` installed into `.venv` are two different binaries in two different PATH
     locations on every OS.
   - What's unclear: whether any subtle Windows path-separator or macOS-codesigning issue affects
     `find_uv_bin()`'s resolution of `.venv\Scripts\uv.exe` — no Windows/macOS host was available this
     session to probe directly.
   - Recommendation: TOX-04's real dispatched CI run is the only closing measurement; no amount of
     Linux-side research substitutes for it (this matches ROADMAP constraint 7's standing policy).

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Phase 64 `uv`/`tox` shims on PATH | All of TOX-01..03 | ✓ (confirmed this session: `command -v uv` → `/nix/store/…-uv/bin/uv`, `command -v tox` → `/nix/store/…-tox/bin/tox`) | uv 0.11.25 (nixpkgs leg, pre-revert); resolves to 0.12.13 once `.venv/bin/uv` exists | — |
| nix `python3` store path (for D-03's control venv) | TOX-03 | ✓ (`/nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13`) | 3.13.13 | — |
| uv-managed `cpython-3.12.13` (for `tox -e py312`'s own venv) | TOX-02, TOX-03 | ✓ (already installed, `uv python list` confirms `/home/yuta/.local/share/uv/python/cpython-3.12-linux-x86_64-gnu/bin/python3.12`) | 3.12.13 | If absent on a fresh machine, `uv python install 3.12` (network-dependent) |
| `gh` CLI + `gh workflow run` access to the pushed branch | TOX-04 | Not independently re-probed this session (Phase 64's `64-CI-EVIDENCE.md` already exercised the identical procedure against this exact branch successfully) | n/a | — |
| Windows/macOS test host | TOX-04's A1/A2 assumptions | ✗ (Linux-only research session) | — | None — TOX-04's real dispatched CI run is the only substitute, per ROADMAP constraint 7 |

**Missing dependencies with no fallback:** none block *research or planning*; TOX-04's actual
Windows/macOS verification has no local fallback by design (CI is the authority).

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest [VERIFIED: `pyproject.toml:79-88`, `[tool.pytest.ini_options]`, `testpaths = ["tests"]`] |
| Config file | `pyproject.toml` (`[tool.pytest.ini_options]`) |
| Quick run command | `tox --showconfig -e py312` (SC#2's parser-exercise, ~0.15s) or `pytest tests/test_toolchain_config_gate.py -x` (~1-2s) |
| Full suite command | `tox -e py312` (or `-e py313`) — runs the full 1548-test suite through the real `uv-venv-lock-runner` path this phase edits |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|--------------------|-------------|
| TOX-01 | `pyproject.toml` declares `tox-uv`; `uv.lock` regenerated in same commit; `uv sync --extra dev --locked` exits 0 | integration (shell) | `uv sync --extra dev --locked; echo $?` then `git show --name-only <commit>` | ✅ (no new file — shell-level check against the commit) |
| TOX-01 | Existing dev-extra static gate must reflect the new pin (see Decision Conflict) | unit | `pytest tests/test_toolchain_config_gate.py::test_dev_extra_pins_tox_uv_bare_not_tox_uv -x` | ❌ needs owner-approved update before it can be green — currently asserts the pre-revert state |
| TOX-02 | `tox` starts against the edited `tox.ini`; broken comma form is rejected | integration (shell) | `tox --showconfig -e py312; echo $?` (expect 0 on the edited file; a manual negative-control run against the comma form should show exit 1) | ✅ (no new file) |
| TOX-03 | Bundled-branch resolution + version observed from inside a real tox run | integration (shell, evidence-recorded per Phase 64 D-05 convention — no new test file) | `tox -vv -e py312 -r 2>&1 \| grep -E "using bundled uv from|^DEBUG uv "` | ✅ (no new file; matches Phase 64's convention of recording in evidence markdown, not a committed script) |
| TOX-03 | Isolated outside-FHS control fails on the uv exec, not earlier | integration (shell, evidence-recorded) | `<ctrl-venv>/bin/python -m tox -vv -e py312 --workdir <tmp> -r` (run outside any shim) | ✅ (no new file) |
| TOX-04 | CI green across every lane | CI (external) | `gh workflow run CI --ref <branch>` then `gh run watch <id> --exit-status`, transcribe `gh run view <id> --json jobs` | ✅ (existing `ci.yml`, unedited) |
| (repo-wide) | Full suite stays green | unit+integration | `tox -e py312` / `tox -e py313` (full suite, not `--notest`) | ✅ — but currently RED on the swap alone (see Decision Conflicts); GREEN once the one test is updated |

### Sampling Rate

- **Per task commit:** `tox --showconfig -e py312` (fast parser check) after the `tox.ini`/
  `pyproject.toml` edits; `pytest tests/test_toolchain_config_gate.py -x` after any test-file edit.
- **Per wave merge:** full `tox -e py312` (exercises the real bundled-`uv` path end to end, not just
  `--notest`) — this is also literally D-02's own evidence-gathering command, so it is not
  double-work.
- **Phase gate:** full pytest suite green (`tox -e py312` and `-e py313`) before `/gsd-verify-work`,
  plus TOX-04's dispatched CI run completed with all 12 jobs transcribed (reuse Phase 64's 12-row job
  census shape: 6 `test` matrix jobs [`ubuntu-latest`×2, `windows-latest`×2, `macos-latest`×2 Python
  versions], `Lint and Format Check`, `Type Check`, `Code Coverage`, `Build Package`, `Integration Test
  - basic`, `Integration Test - advanced` — [VERIFIED: `.github/workflows/ci.yml:11-215`, the `test`
  job's `matrix.os: [ubuntu-latest, windows-latest, macos-latest]` × `python-version: ['3.12','3.13']`,
  plus `lint`, `type-check`, `coverage`, `build`, `integration` job definitions, cross-checked against
  `64-CI-EVIDENCE.md`'s own 12-row transcription of run `34618719267`]).

### Wave 0 Gaps

- None — no new test framework or fixture is needed. The one gap is not a missing test but an
  **existing test whose assertion direction is now wrong** (`test_dev_extra_pins_tox_uv_bare_not_
  tox_uv`), which is a plan-content decision (pending owner input), not an infrastructure gap.

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-------------------|
| V2 Authentication | no | n/a — no auth surface touched |
| V3 Session Management | no | n/a |
| V4 Access Control | no | n/a |
| V5 Input Validation | no | n/a — no user input path |
| V6 Cryptography / Integrity | yes | `uv.lock`'s per-artifact `sha256` hash pinning, enforced by `uv sync --locked`/`--extra dev --locked` refusing on mismatch [VERIFIED: `uv.lock:1420-1608` in this session's scratch copy, quoted verbatim: `wheels = [ { url = "https://files.pythonhosted.org/packages/f9/d7/…/tox_uv-1.36.0-py3-none-any.whl", hash = "sha256:5f81b39be3fe4e14c6b9bb7ba637ed97d34efa6214efd5f525d95ee9559a99ac", … } ]` for `tox-uv`, and equivalent entries for `tox-uv-bare` and `uv`] |

### Known Threat Patterns for This Stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|-----------------------|
| Supply-chain substitution of a new transitive dependency (`uv`, a native-binary PyPI wheel) | Tampering | `uv.lock`'s hash pins + `--locked`/`--extra dev --locked` in CI and in the documented provisioning line — any tampered or re-published artifact with a different hash is refused at sync time, not silently accepted |
| Cross-ecosystem or slopsquatted package-name confusion (a common hallucination vector in agentic package additions) | Spoofing | Not applicable here — `tox-uv`, `tox-uv-bare`, and `uv` are all pre-existing, already-vendored-in-this-repo's-history package names (see § Package Legitimacy Audit); no new name is being introduced |
| A malicious or compromised `TOX_UV_PATH` environment variable silently redirecting every `uv` invocation | Tampering / Elevation of Privilege | D-02 explicitly forbids setting `TOX_UV_PATH` anywhere in this phase's own config surface (`flake.nix`, `tox.ini setenv`, shell); it remains an opt-in override the maintainer must set deliberately, not a default this phase introduces |

## Decision Conflicts

> Required by the orchestrator's hard rules: measurements that contradict a locked decision or a
> ROADMAP success criterion are recorded here, not silently re-scoped around.

### Conflict 1 — D-06's edit footprint vs. a pre-existing static test asserting the opposite decision

**Decision contradicted:** D-06 ("This phase edits only the `tox.ini` `requires` value,
`pyproject.toml:38`, and `uv.lock` in the tree") and, transitively, ROADMAP constraint 13's "every
phase closes green on the full pytest suite."

**Command and output (FORECAST, this session, `research-65` scratch copy, full suite via
`tox -vv -e py312 -r`, no `--notest`):**
```
FAILED tests/test_toolchain_config_gate.py::test_dev_extra_pins_tox_uv_bare_not_tox_uv
E       AssertionError: dev extra does not contain 'tox-uv-bare' (on normalized distribution name) -- ...
E       assert 'tox-uv-bare' in {'black', 'build', 'mypy', 'pillow', 'pre-commit', 'pypdf', ...}
=========================== short test summary info ===========================
FAILED tests/test_toolchain_config_gate.py::test_dev_extra_pins_tox_uv_bare_not_tox_uv
1 failed, 1542 passed, 5 skipped in 108.07s (0:01:48)
```

**Why this is a real conflict, not a research artifact:** the test (`tests/test_toolchain_config_gate.
py:269-362`, from Phase 45.2) has TWO assertions:
- line 336: `assert canonicalize_name("tox-uv-bare") in dev_names` — **fails** post-revert, because
  the dev extra now names `tox-uv` directly (`tox-uv-bare` is present only as `tox-uv`'s own
  transitive dependency, not a literal entry in `pyproject.toml`'s `dev` list).
- line 351: `assert canonicalize_name("tox-uv") not in dev_names` — would **also** fail (assertion 336
  aborts the test first) since `tox-uv` is now literally present.

Both assertions, and the test's entire docstring/module-docstring framing (`GAP G5 (45.2-02-D1,
SC#2)`), encode "tox-uv-bare is correct, tox-uv is the regression" — the precise inverse of this
phase's mandate. This is not a flaky test or an environment artifact; it is a static gate doing
exactly what it was built to do, now aimed at the wrong target.

**What is NOT affected:** `test_runtime_dependencies_carry_no_toolchain_package` (same file,
`forbidden_packages = {"uv", "tox", "tox-uv", "tox-uv-bare"}` checked against `[project].dependencies`,
not the `dev` extra) — confirmed still passing in the same full-suite run, since this phase only
touches the `dev` extra. `tests/test_pdf_render_gate.py:167`'s reference is a docstring/comment only,
carries no assertion, and does not fail.

**Recommendation for the orchestrator to put to the owner:** either (a) fold updating
`test_dev_extra_pins_tox_uv_bare_not_tox_uv` (inverting its two assertions and its docstring's
historical framing to describe Phase 65's revert, analogous to how `65-CONTEXT.md`'s own D-01 AMENDED
block was written) into this phase's plan as a fourth, explicitly-called-out file, or (b) issue an
AMENDED block to D-06 authorizing that edit before planning proceeds. Leaving D-06 as literally written
makes constraint 13 ("full pytest suite green") and TOX-01 mutually unsatisfiable in the same commit.

## Sources

### Primary (HIGH confidence)

- `flake.nix` (this repo, read in full) — `fhsRun`, `venvWalk`, `uvShim`, `venvShimNames`.
- `.venv/lib/python3.13/site-packages/tox_uv/_venv.py` (installed `tox-uv-bare` 1.35.2, whose
  `tox_uv` module is byte-identical in provenance to `tox-uv` 1.36.0's per D-01 — confirmed the
  `uv` `cached_property`'s three-branch discovery order and the `_get_uv_version()` helper directly
  from source, lines 207-252).
- `.venv/lib/python3.13/site-packages/tox_uv/_run_lock.py` (installed source, lines 60-137 — the
  `uv sync` command-building logic, `-v` append condition, `--locked`/`--extra`/`--reinstall` flags).
- `.venv/lib/python3.14/site-packages/tox/config/cli/parser.py` (scratch-installed tox 4.56.1 source,
  `DEFAULT_VERBOSITY = 2` and the `-v`/`action="count"` verbosity argument, lines 133, 495-501).
- PyPI JSON API, fetched live 2026-09-12: `https://pypi.org/pypi/tox-uv/1.36.0/json` (`requires_dist`)
  and `https://pypi.org/pypi/tox-uv/json` + `https://pypi.org/pypi/tox-uv-bare/json` (`releases` key
  lockstep comparison, last 8 versions each).
- `.github/workflows/ci.yml` (this repo, read in full) — job matrix, step names, triggers.
- `.planning/phases/64-fhs-wrapper-and-command-shims-in-flake-nix/64-CI-EVIDENCE.md` (the 12-job
  census template and the pre-revert CI baseline, run `34618719267`).
- `.planning/phases/64-fhs-wrapper-and-command-shims-in-flake-nix/64-LIBZ-DIAGNOSIS.md` (fresh
  worktree `.venv` built on uv-managed CPython 3.14, why `.venv/bin/python3` itself is a generic-
  linux ELF).
- `tests/test_toolchain_config_gate.py` (this repo, read in full, lines 1-445).
- Live scratch execution this session — every command in § Code Examples, § Architecture Patterns,
  and § Decision Conflicts was run and its output pasted verbatim, not recalled.

### Secondary (MEDIUM confidence)

- `newreleases.io` / GitHub releases page summary for `tox-uv` 1.36.0 (fetched via WebSearch, not
  read from the primary changelog file directly) — used only for "no obvious incompatibility" framing
  in § State of the Art, explicitly caveated as absence-of-evidence, not evidence-of-absence.

### Tertiary (LOW confidence)

- None used as a basis for any claim in this document.

## Metadata

**Confidence breakdown:**
- Standard stack (package identity, versions, lockstep): HIGH — every version and lockstep claim was
  fetched live from PyPI's own JSON API this session.
- Architecture (discovery order, version disclosure mechanism, isolated control shape): HIGH — every
  step was reproduced end-to-end in a scratch copy this session, with verbatim log output captured.
- Pitfalls: HIGH for the three documented here (all reproduced live); the Decision Conflict is the
  single most load-bearing finding in this document and should not be treated as a minor footnote.
- Windows/macOS TOX-04 behavior (A1/A2 in Assumptions Log): LOW — no Windows/macOS host was available
  in this research session; TOX-04's real CI run is the only closing measurement.

**Research date:** 2026-09-12
**Valid until:** ~14 days (2026-09-26) — this domain moves fast (uv/tox-uv/tox-uv-bare all release
frequently; the exact versions recorded here WILL be stale by execution time, per D-04's own framing
of "recorded literally at execution time"). The *mechanism* (discovery order, verbosity-triggered `-v`
disclosure, isolated-control shape) is stable and not expected to change on this timescale.
