# Stack Research

**Domain:** Nix toolchain (FHS compatibility shims) + GitHub Actions (dependabot lockfile regeneration) for a mature, PyPI-published Python package
**Researched:** 2026-09-02
**Confidence:** HIGH (nix APIs verified directly against `NixOS/nixpkgs` master source and `pkgs/top-level/aliases.nix`; PyPI version facts verified via live `pypi.org` JSON API; GitHub Actions facts verified via GitHub's own docs and `api.github.com` release lookups. The Dependabot-native-lockfile-regeneration gap is MEDIUM — Astral's own docs cite an open upstream issue rather than a fixed behavior.)

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| `pkgs.buildFHSEnv` | nixpkgs `nixos-unstable` (this flake's existing pin) | Wraps a bubblewrap sandbox so generic-linux-ELF binaries (uv-downloaded CPython, `uv pip install`ed wheels like `ruff`) can exec on NixOS | Verified in `pkgs/top-level/all-packages.nix` (line 318-319, fetched 2026-09-02): `buildFHSEnv = buildFHSEnvBubblewrap;` — it is a **plain alias**, not a separate implementation. This is the name to write in `flake.nix`; `buildFHSEnvBubblewrap` also works but is the less idiomatic spelling. Matches the already-measured fact that `buildFHSEnv` wrapping works for `ruff`/`tox`/`uv`/downloaded CPython. |
| `tox-uv` | `>=1.35,<2` (unpinned exact — same range the repo already uses for `tox-uv-bare`) | tox runner plugin that provisions each `tox` env from `uv.lock` via `uv sync` | Confirmed via live PyPI JSON: `tox-uv` and `tox-uv-bare` are released in **exact version lockstep** (both list `1.33.0 … 1.36.0` as their most recent 10 releases, identical set). The existing `>=1.35,<2` constraint on `-bare` is directly portable to plain `tox-uv` with no re-derivation needed. `tox-uv==1.36.0`'s own `requires_dist` is `tox-uv-bare==1.36.0` + `uv>=0.9.27,<1` — i.e. `tox-uv` is literally `tox-uv-bare` plus a bundled `uv` wheel dependency. That bundled wheel is the one whose generic-linux ELF QUA-04 found unrunnable outside FHS; the already-measured facts show it now works *inside* the flake's FHS wrapper (`uv.find_uv_bin()` resolves `.venv/bin/uv`, and `tox -e type/lint/py312/py313` are all green). |
| `astral-sh/setup-uv` | Keep existing `@v7` pin (repo's own convention) | Installs `uv` in each GitHub Actions job | **Not to be changed by this milestone** — explicitly out of scope. For accuracy: live GitHub API lookup (2026-09-02) shows the actual latest release is `v10.0.1`, and `v7` moving tags are gone (immutable-release-only since `v8`). Do not silently "fix" this while implementing (b)/(c) — it would violate the milestone's own out-of-scope line, and dependabot's own `github-actions` ecosystem entry in `.github/dependabot.yml` is the intended channel for that bump. For the *new* dependabot-lock-regen workflow, match the existing `@v7` convention for consistency rather than introducing a second pin scheme in the same repo. |
| `pull_request_target` (GitHub Actions event) | n/a (built-in) | Trigger that gives the lock-regen workflow a **writable** `GITHUB_TOKEN` when the PR is opened by `dependabot[bot]` | Verified against GitHub's own troubleshooting docs (`docs.github.com/.../dependabot-on-actions`, fetched 2026-09-02): workflows triggered by the plain `pull_request` event **from Dependabot are forced to a read-only `GITHUB_TOKEN`** regardless of the workflow's `permissions:` block — this is a hard-coded GitHub security behavior, not a bug to work around with YAML. The documented fix is exactly "a two-step process that includes `pull_request_target`". Because Dependabot PRs in this repo are always same-repo branches (never forks — Dependabot never opens forked PRs for a repo it has write access to), `pull_request_target` here carries none of the "pwn request" risk that applies to fork PRs; the risk is out of scope. |

### Supporting Libraries / Actions

| Library / Action | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `pkgs.writeShellScriptBin` | nixpkgs builtin | Builds one cheap, non-sandboxed wrapper derivation per shimmed command name (`ruff`, `tox`, `black`, `mypy`, `pytest`, …) | Use this — not N separate `buildFHSEnv` calls — to expose multiple command-name shims without re-materializing the FHS rootfs N times (see idiom below). |
| `pkgs.writeShellScript` | nixpkgs builtin | Builds the single passthrough `runScript` (`exec "$@"`) that turns one `buildFHSEnv` derivation into a generic "run anything inside this sandbox" entry point | This is what makes one rootfs serve every shimmed command. |
| `stefanzweifel/git-auto-commit-action` | `@v7` (live lookup 2026-09-02: latest tag `v7.2.0`) | Commits + pushes the regenerated `uv.lock` back onto the Dependabot PR's branch | Simpler than hand-rolling `git config` / `git commit` / `git push` steps; widely used for exactly this "regenerate a lockfile and push it back" pattern (confirmed via a working example workflow at browniebroke.com, fetched 2026-09-02, using the same `uv lock` + commit-back shape this repo needs — that example itself used an older `@v5` pin from 2024; verify current `@v7` before adopting). Alternative: `peter-evans/create-pull-request` if a *separate* PR is preferred over pushing directly onto the dependabot branch — not recommended here since it multiplies PRs instead of fixing the existing one. |
| `actions/checkout` | `@v7` (already used everywhere in this repo's workflows) | Checks out the Dependabot PR's head branch for the lock-regen job | Under `pull_request_target`, `github.ref` defaults to the **base** branch, not the PR branch — the checkout step must explicitly set `ref: ${{ github.event.pull_request.head.ref }}` (or `.head.sha`) or it will silently lock-regen the wrong tree. This is a common `pull_request_target` foot-gun, not specific to uv. |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| `bubblewrap` (`bwrap`) | The actual sandbox backend `buildFHSEnv` shells out to | Pulled in transitively by `buildFHSEnv`; do not add `pkgs.bubblewrap` to `mkShell.packages` separately, it is not meant to be invoked directly. |
| `nix flake show` / `nix eval .#devShells.<system>.default` | Sanity-check that darwin systems still evaluate after the FHS guard is added | Run this for at least one darwin system entry (`x86_64-darwin` or `aarch64-darwin`) before merging — the milestone's own "Unverified" list does not include a darwin evaluation check, and `flake.nix` gets zero CI coverage, so this must be done by hand during planning/execution. |

## Installation / Integration

### (a) FHS wrapper + command-name shims — `flake.nix`

Canonical idiom, building the sandbox rootfs **once** and deriving cheap per-command wrappers from it via `map` (answers "how to expose several command-name wrappers without duplicating the rootfs derivation"):

```nix
devShells = forAllSystems (
  system:
  let
    pkgs = pkgsFor system;

    # One passthrough runScript turns the FHS sandbox into a generic
    # "run anything inside this mount namespace" entry point, instead of
    # baking one command per buildFHSEnv derivation (which would rebuild
    # the whole rootfs closure once per command).
    fhsRun = pkgs.buildFHSEnv {
      name = "typsphinx-fhs-run";
      runScript = "${pkgs.writeShellScript "fhs-passthrough" ''exec "$@"''}";
      # targetPkgs/multiPkgs stay empty: the real tools already live in
      # .venv (installed by uv/tox-uv), the sandbox only needs to supply
      # a working dynamic linker + baseTargetPaths (glibc, coreutils, …),
      # which buildFHSEnv already provides unconditionally.
    };

    # Command names that resolve inside the project's own .venv.
    # chdirToPwd defaults to true and the cwd is auto-bind-mounted, so
    # "$PWD/.venv/bin/<name>" inside the sandbox is the same path the
    # caller already has outside it.
    venvShimNames = [ "ruff" "black" "mypy" "pytest" "tox" "sphinx-build" ];
    venvShims = map (
      cmd:
      pkgs.writeShellScriptBin cmd ''
        exec ${fhsRun}/bin/typsphinx-fhs-run "$PWD/.venv/bin/${cmd}" "$@"
      ''
    ) venvShimNames;

    # uv itself is not installed inside .venv (it creates .venv), so its
    # shim resolves to nixpkgs' own uv rather than a venv-relative path.
    uvShim = pkgs.writeShellScriptBin "uv" ''
      exec ${fhsRun}/bin/typsphinx-fhs-run ${pkgs.uv}/bin/uv "$@"
    '';
  in
  {
    default = pkgs.mkShell {
      packages = [
        pkgs.nodejs
        pkgs.pnpm
        pkgs.git
        pkgs.python3
        pkgs.uv
      ] ++ pkgs.lib.optionals pkgs.stdenv.hostPlatform.isLinux (venvShims ++ [ uvShim ]);
    };
  }
);
```

Notes:
- `mkShell` is unchanged as the devShell type — matches the binding measurement that `.env`/`shellHook` entry into `buildFHSEnv` does not work under either `nix develop` or `direnv`. The shim derivations are ordinary (non-sandboxed) executables that internally exec into the sandbox; putting them on `mkShell.packages` works exactly like any other package, because from `mkShell`'s point of view they *are* ordinary packages.
- The exact set of `venvShimNames` (which commands get shimmed) is a requirements-phase decision, not a research fact — the milestone context names `ruff`, `tox -e py312`, `uv`, and "the CPython that tox downloads" as the four proven-broken classes; the CPython case does not need its own shim because it is `tox`'s child process and inherits the mount namespace once `tox` itself runs inside it.
- `buildFHSEnv` requires either `name` or `pname`+`version`; using `name` directly (as above) avoids forcing the `pname ? throw …` / `version ? throw …` defaults in the underlying `pkgs/build-support/build-fhsenv-bubblewrap/default.nix`.

### (b) `tox-uv` revert — `pyproject.toml` and `tox.ini`

`pyproject.toml`:
```diff
- "tox-uv-bare>=1.35,<2",
+ "tox-uv>=1.35,<2",
```
(Range carries over unchanged — verified identical release cadence above.)

`tox.ini` — the parser-bug workaround this repo already documents for `-bare` (comma-in-single-line-`requires` splits into two bogus requirements) applies identically to plain `tox-uv`, since it is the same `requires = <pkg>~=<ver>` line shape:
```diff
- requires = tox-uv-bare~=1.35
+ requires = tox-uv~=1.35
```
Keep the existing explanatory comment above this line — its parser-bug rationale (§ `~=` vs `>=1.35,<2`) is unrelated to which of the two packages is named and remains correct verbatim.

### (c) Dependabot `uv.lock` regeneration workflow — new `.github/workflows/*.yml`

```yaml
name: Dependabot Lockfile Sync

on:
  pull_request_target:
    branches: [ main, develop ]
    paths:
      - "pyproject.toml"

permissions:
  contents: write

jobs:
  relock:
    if: github.actor == 'dependabot[bot]'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
        with:
          ref: ${{ github.event.pull_request.head.ref }}

      - name: Install uv
        uses: astral-sh/setup-uv@v7
        with:
          version: "latest"

      - name: Set up Python
        run: uv python install 3.12

      - name: Regenerate lockfile against the bumped pyproject.toml
        run: uv lock

      - uses: stefanzweifel/git-auto-commit-action@v7
        with:
          commit_message: "chore: regenerate uv.lock for dependabot bump"
          file_pattern: uv.lock
```

Open design point for requirements/roadmap (not resolved here — it is a policy tradeoff, not a research fact):
- A push made with the default `GITHUB_TOKEN` **does not trigger new workflow runs** on that branch (GitHub's documented anti-loop behavior), so the repo's normal `ci.yml` `pull_request: [synchronize]` will **not** automatically re-run after this job pushes the fixed lockfile. Options: (1) accept it and re-trigger CI manually (`workflow_dispatch`, or close/reopen the PR) each time — zero new secrets, matches "no `nix` job is added" spirit of keeping CI untouched; (2) store a fine-grained PAT as a repo secret and use it in the `checkout`/push step instead of `GITHUB_TOKEN`, which *does* retrigger `synchronize` — adds a credential to maintain. Given the milestone's own acceptance test is "prove the fix on a real dependabot PR, observing the install step succeed" (not "observing full green CI on the first push"), option (1) is sufficient to satisfy the stated scope; flag option (2) only if the roadmap wants zero-manual-step closure.

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|--------------------------|
| `pkgs.buildFHSEnv` | `buildFHSEnvChroot` | Never for new code — verified via live nixpkgs `aliases.nix` fetch (2026-09-02): `buildFHSEnvChroot = throw "'buildFHSEnvChroot' is deprecated, please use 'buildFHSEnv'";` (added 2026-05-21), and `doc/release-notes/rl-2611.section.md` confirms `buildFHSEnvChroot has been removed after deprecation in 23.05.` Any reference to it in this flake would hard-fail evaluation on the `nixos-unstable` pin this repo already uses. |
| `pkgs.buildFHSEnv` | `buildFHSEnvBubblewrap` | Functionally identical (`buildFHSEnv` is a plain alias of it per `all-packages.nix`) — only use the longer name if you specifically want to signal "this is bubblewrap-backed" in code review; otherwise it is pure noise. |
| One `buildFHSEnv` + N `writeShellScriptBin` shims | N separate `buildFHSEnv { runScript = "<real-tool>"; }` derivations | Never here — each `buildFHSEnv` call materializes its own rootfs closure (measured cost: +0.26 GiB store closure for *one* such env in this session's prior testing); N of them multiplies that. The single-passthrough-plus-thin-shims pattern gets the same effect from one rootfs. |
| `pull_request_target` for the lock-regen job | Skip Dependabot entirely with `if: github.actor != 'dependabot[bot]'` | This is the opposite of the milestone's goal (it silences the exact PRs that need fixing) — mentioned only because GitHub's own docs list it as their first-listed "workaround"; it is not applicable here. |
| `pull_request_target` for the lock-regen job | Elevate `permissions:` on a plain `pull_request` trigger | Verified not to work for Dependabot-authored PRs specifically — GitHub forces read-only regardless of the `permissions:` block on that event when the actor is Dependabot. This is the one alternative that looks plausible but is confirmed non-functional by GitHub's own docs. |
| `stefanzweifel/git-auto-commit-action@v7` | Hand-rolled `git config`/`commit`/`push` steps | Only if the maintainer wants zero third-party actions in this workflow; functionally equivalent, more YAML to maintain. |
| `stefanzweifel/git-auto-commit-action@v7` | `peter-evans/create-pull-request` | Only if the desired outcome is a *second* PR carrying the lockfile fix rather than amending the existing Dependabot PR in place — not recommended here since the milestone's goal is "dependabot PRs are tested," i.e. fixing the PR that already exists. |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|--------------|
| `buildFHSEnvChroot` | Hard-removed on the `nixos-unstable` pin this flake already uses (throws at eval time, not a soft deprecation warning) | `buildFHSEnv` |
| A `shellHook` that `exec`s into the FHS wrapper from `mkShell` | Already measured this session to be non-functional under both `nix develop` (hook body never runs) and `direnv` (the `exec` only replaces nix-direnv's env-capture subshell, not the real interactive shell) | Command-name shim derivations added to `mkShell.packages`, as above |
| Switching the devShell itself to `pkgs.buildFHSEnv.env` | Already measured non-functional under both `nix develop` and `direnv` (`/lib64/ld-linux-x86-64.so.2` still resolves to `stub-ld` in both) | Keep `mkShell`; add shims |
| Bumping `astral-sh/setup-uv` past `@v7` in this milestone, anywhere in `.github/workflows/` | Explicitly out of scope per the milestone's own scoping note; doing it opportunistically while touching (c) would silently expand scope and duplicate what dependabot's `github-actions` ecosystem entry already exists to do | Leave the existing `@v7`/`version: "latest"` pins untouched; use the same convention in the *new* workflow for consistency |
| Plain `pull_request` (not `pull_request_target`) for the lock-regen workflow | Confirmed by GitHub's own docs to receive a forced-read-only `GITHUB_TOKEN` for Dependabot-authored PRs, independent of any `permissions:` block written in the workflow | `pull_request_target` with an explicit head-ref checkout |
| Leaving `dependabot.yml`'s `package-ecosystem: "pip"` unquestioned | See flagged finding below — Astral's own integration docs state plainly that a uv project's `dependabot.yml` "should... use `package-ecosystem: 'uv'` (not pip or pip-compile)"; this repo's current `.github/dependabot.yml` uses `"pip"`. This is very likely a *contributing root cause* of the stale-`uv.lock` symptom this milestone is built to fix, not just an unrelated observation. | Flag for the requirements/roadmap phase as a candidate change alongside (c) — see below |

**Flagged finding requiring a decision, not a research recommendation to silently apply:** this repo's `.github/dependabot.yml` currently reads `package-ecosystem: "pip"` for the `pyproject.toml`/`uv.lock` directory. GitHub added a **dedicated `"uv"` ecosystem** (general availability announced March 2025 per GitHub's changelog), and Astral's integration guide is explicit that a uv project should use it, not `"pip"`. Whether `"pip"` on this repo already silently falls back to uv-aware parsing (some evidence Dependabot's `pip` ecosystem detection reportedly picked up `uv.lock` automatically in some repos) or genuinely misparses the lockfile could not be fully disambiguated from documentation alone — Astral's own page hedges ("there are some use cases that are not yet working," citing `astral-sh/uv#2512`, an open issue). Given the milestone's explicit target is exactly "dependabot PRs are tested rather than dying at the install step," changing `dependabot.yml`'s ecosystem line to `"uv"` is a one-line change with a plausible causal link to the observed failure and should be evaluated by requirements alongside the (c) workflow — not dismissed as out of scope by default, since it may make the (c) workflow's job unnecessary in the common case (dependabot itself keeping `uv.lock` in sync) while (c) remains as a safety net for the cases Astral's own docs say are not yet working.

## Stack Patterns by Variant

**If evaluating `flake.nix` on `x86_64-linux` / `aarch64-linux`:**
- `pkgs.stdenv.hostPlatform.isLinux` is `true`, so `lib.optionals … (venvShims ++ [ uvShim ])` evaluates the `buildFHSEnv` branch and the shims land on `mkShell.packages`.

**If evaluating `flake.nix` on `x86_64-darwin` / `aarch64-darwin`:**
- `pkgs.stdenv.hostPlatform.isLinux` is `false`. Because Nix `let`-bindings are lazy and `lib.optionals false x` never forces `x`, the `fhsRun`/`venvShims`/`uvShim` thunks — which call `pkgs.buildFHSEnv`, a Linux-only construct — are **never evaluated** on darwin. This is the same idiom nixpkgs' own top-level `flake.nix` uses (`lib.optionalAttrs (...) { ... }` guarded by `stdenv.hostPlatform.isLinux`, verified live 2026-09-02). No `system == "x86_64-linux" || …` string-matching is needed; gate on the platform predicate, not the system string.

**If the lock-regen workflow needs to also run for a hand-authored branch (not Dependabot):**
- Add a second, ordinary `pull_request` (not `_target`) job, or drop the `if: github.actor == 'dependabot[bot]'` guard and accept the read-only-token limitation does not apply to non-Dependabot actors. Out of scope for this milestone, noted only so the workflow isn't accidentally written in a way that *requires* the actor check to function (it currently gates unnecessary permission use, not correctness).

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| `tox-uv==1.36.0` | `uv>=0.9.27,<1` | From `tox-uv`'s own PyPI `requires_dist` (live lookup 2026-09-02). Currently-published `uv` is `0.12.9`, well inside range — no conflict with this repo's `tox-uv-bare>=1.35,<2` → `tox-uv>=1.35,<2` revert. |
| `tox-uv` / `tox-uv-bare` | Each other, version-for-version | Confirmed identical release-version sets on PyPI (`1.32.0` through `1.36.0` for `-bare`; `1.33.0` through `1.36.0` visible in the last-10 window for both) — the revert is a drop-in package-name swap, no version research needed beyond what QUA-04 already did for `-bare`. |
| `tox-uv-bare==1.36.0`'s own deps | `tox<5,>=4.52.1` | Compatible with this repo's existing `tox>=4.56,<5` pin — unaffected by the (b) revert. |
| `pkgs.buildFHSEnv` | nixpkgs `nixos-unstable` as of 2026-09-02 | The `finalAttrs`-pattern support and `buildFHSEnvChroot` removal are both landing on this branch per `doc/release-notes/rl-2611.section.md` (in-progress release notes for the *upcoming* 26.11, already merged to `nixos-unstable`) — this flake's existing `nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable"` pin already tracks this; no input change needed. |
| Dependabot `package-ecosystem: "uv"` | GA since March 2025 (GitHub changelog) | Available on any GitHub Enterprise Cloud/github.com repo today; no version gate. See flagged finding above. |

## Sources

- `github.com/NixOS/nixpkgs` `pkgs/top-level/all-packages.nix` (raw fetch, master, 2026-09-02) — `buildFHSEnv = buildFHSEnvBubblewrap;` alias, confirmed directly from source. HIGH confidence.
- `github.com/NixOS/nixpkgs` `pkgs/top-level/aliases.nix` (raw fetch, master, 2026-09-02) — `buildFHSEnvChroot` throw-alias, added 2026-05-21. HIGH confidence.
- `github.com/NixOS/nixpkgs` `doc/release-notes/rl-2611.section.md` (raw fetch, master, 2026-09-02) — `buildFHSEnvChroot has been removed after deprecation in 23.05.` and `buildFHSEnv` `finalAttrs` support. HIGH confidence.
- `github.com/NixOS/nixpkgs` `pkgs/build-support/build-fhsenv-bubblewrap/default.nix` and `buildFHSEnv.nix` (raw fetch, master, 2026-09-02) — full argument surface (`targetPkgs`, `multiPkgs`, `profile`, `runScript`, `executableName`, `unshareUser`/`unshareIpc`/`unsharePid`/`unshareNet`/`unshareUts`/`unshareCgroup`, `privateTmp`, `chdirToPwd`, `dieWithParent`, `extraPreBwrapCmds`, `extraBwrapArgs`, `extraInstallCommands`, `extraOutputsToInstall`, `extraBuildCommands(Multi)`, `nativeBuildInputs`, `multiArch`, `includeClosures`). HIGH confidence — read directly, not summarized secondhand.
- `github.com/NixOS/nixpkgs` `flake.nix` (raw fetch, master, 2026-09-02) — the `lib.optionalAttrs (...isLinux) {...}` per-system darwin-guard idiom used by nixpkgs on its own flake. HIGH confidence.
- `pypi.org/pypi/tox-uv/json` and `pypi.org/pypi/tox-uv-bare/json` (live API, 2026-09-02) — version lockstep and `requires_dist` facts. HIGH confidence (primary source, not a summarizer).
- `pypi.org` / `api.github.com/repos/astral-sh/setup-uv/releases/latest` (live API, 2026-09-02) — `v10.0.1` is current; `@v7` moving tags are gone since immutable releases began at `v8`. HIGH confidence.
- `api.github.com/repos/stefanzweifel/git-auto-commit-action/releases/latest` (live API, 2026-09-02) — `v7.2.0`. HIGH confidence.
- `docs.github.com/en/code-security/reference/supply-chain-security/troubleshoot-dependabot/dependabot-on-actions` (fetched 2026-09-02) — forced read-only `GITHUB_TOKEN` for Dependabot-triggered `pull_request` events, and the documented `pull_request_target` two-step workaround. HIGH confidence (official GitHub docs).
- `docs.astral.sh/uv/guides/integration/dependabot/` (fetched 2026-09-02) — recommends `package-ecosystem: "uv"` over `"pip"`; cites open upstream gap `astral-sh/uv#2512`. MEDIUM confidence on the "not yet working" claim specifically (Astral hedges it themselves and links to an issue tracker rather than stating a resolved behavior) — HIGH confidence on the ecosystem-name recommendation itself.
- `browniebroke.com/blog/2024-10-02-keep-uv-lock-file-up-to-date-with-dependabot-updates` (fetched 2026-09-02) — worked example workflow shape (`uv lock` + `git-auto-commit-action` + PAT-for-retrigger caveat); dated 2024, action version in the example (`@v3`/`@v5`) is stale and was cross-checked against live release lookups above rather than reused verbatim. LOW-MEDIUM confidence on exact versions shown in that post, HIGH confidence on the overall workflow shape it demonstrates.

---
*Stack research for: Nix/CI toolchain maintenance, typsphinx v0.9.3*
*Researched: 2026-09-02*
