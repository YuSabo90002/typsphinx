{
  description = "typsphinx development shell";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

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
  outputs =
    { self, nixpkgs }:
    let
      systems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];
      forAllSystems = nixpkgs.lib.genAttrs systems;
      pkgsFor = system: nixpkgs.legacyPackages.${system};
    in
    {
      devShells = forAllSystems (
        system:
        let
          pkgs = pkgsFor system;

          fhsRun = pkgs.buildFHSEnv {
            name = "typsphinx-fhs-run";
            # Pillow's `_imaging` extension carries a bare `NEEDED libz.so.1`, and
            # uv-managed CPython links zlib statically, so nothing in the sandboxed
            # process ever maps it without this entry. See v0.9.3 Phase 64 `64-LIBZ-FIX-EVIDENCE.md`.
            targetPkgs = p: [ p.zlib ];
            runScript = "${pkgs.writeShellScript "typsphinx-fhs-passthrough" ''
              exec "$@"
            ''}";
          };

          # Bounded upward walk from $PWD looking for .venv/bin/<tool>, stopping
          # at the first ancestor holding a .git entry (a file in a worktree, a
          # directory in the main checkout) or at /. This survives tox's own
          # `changedir = docs` (docs-html/docs-pdf) and never leaves the
          # checkout it started in, so a nested executor worktree can never
          # resolve the main checkout's .venv.
          venvWalk =
            tool: onStop:
            ''
              start="$PWD"
              dir="$PWD"
              while :; do
                if [ -x "$dir/.venv/bin/${tool}" ]; then
                  exec "${fhsRun}/bin/typsphinx-fhs-run" "$dir/.venv/bin/${tool}" "$@"
                fi
                if [ -e "$dir/.git" ]; then
                  break
                fi
                if [ "$dir" = / ]; then
                  break
                fi
                dir="$(dirname "$dir")"
              done
              ${onStop}
            '';

          # The six venv shims have no fallback. A missing .venv/bin/<tool>
          # is a hard, loud failure -- naming the tool and the directory the
          # walk started from, then exiting non-zero (127, the shell's own
          # command-not-found status). A shim that quietly ran some other
          # binary instead would turn "does not run" into "runs but lies",
          # which is exactly what this fallback-free design avoids.
          venvShimOnStop =
            tool:
            ''
              echo "typsphinx-shim: ${tool}: no executable .venv/bin/${tool} found walking up from $start (stopped at $dir); provision with: env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev" >&2
              exit 127
            '';

          # The full seven-name roster is these six strict venv shims plus
          # `uv` (`uvShim` below, the one exception).
          venvShimNames = [
            "tox"
            "ruff"
            "black"
            "mypy"
            "pytest"
            "sphinx-build"
          ];
          venvShims = map (
            cmd:
            pkgs.writeShellScriptBin cmd ''
              set -eu
              ${venvWalk cmd (venvShimOnStop cmd)}
            ''
          ) venvShimNames;

          # `uv` resolves in two legs, described here by role rather than by
          # version. Leg 1 is the same bounded upward walk used by the strict
          # shims above, ending at the tree's own .venv/bin/uv -- the uv that
          # uv.lock pins, present once `uv sync` has provisioned the tree.
          # Leg 2, the on-stop fragment, resolves to nixpkgs' own uv at a
          # store path fixed at evaluation time, which is why it cannot be
          # shadowed. It is the bootstrap for a fresh clone or worktree that
          # has no .venv yet, before its first uv sync -- without it such a
          # tree could not provision itself, so it must not be removed as
          # cleanup. Both legs enter the sandbox, which is what makes
          # `uv run <tool>` carry FHS into every downstream process. This is
          # the only fallback in this file, deliberately: the six strict
          # shims above must never gain one.
          uvShim = pkgs.writeShellScriptBin "uv" ''
            set -eu
            ${venvWalk "uv" ''exec "${fhsRun}/bin/typsphinx-fhs-run" "${pkgs.uv}/bin/uv" "$@"''}
          '';
        in
        {
          # See the header note above `outputs` for the darwin guard this branch implements.
          default = pkgs.mkShell {
            packages =
              [
                pkgs.nodejs
                pkgs.pnpm
                pkgs.git
                # Python toolchain: uv for fast dependency/venv management.
                pkgs.python3
              ]
              ++ pkgs.lib.optionals pkgs.stdenv.hostPlatform.isLinux ([ uvShim ] ++ venvShims)
              ++ pkgs.lib.optionals (!pkgs.stdenv.hostPlatform.isLinux) [ pkgs.uv ];
          };
        }
      );
    };
}
