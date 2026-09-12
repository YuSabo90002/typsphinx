{
  description = "typsphinx development shell";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

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
            # uv-managed CPython links zlib statically, so nothing in the process
            # ever maps it without this entry. See 64-LIBZ-FIX-EVIDENCE.md.
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

          # D-03: the six venv shims have no fallback. A missing
          # .venv/bin/<tool> is a hard, loud failure -- naming the tool and the
          # directory the walk started from, then exiting non-zero (127, the
          # shell's own command-not-found status).
          venvShimOnStop =
            tool:
            ''
              echo "typsphinx-shim: ${tool}: no executable .venv/bin/${tool} found walking up from $start (stopped at $dir); provision with: env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev" >&2
              exit 127
            '';

          # D-01: the full seven-name roster is these six strict venv shims
          # plus `uv` (uvShim below, D-02's sole documented exception).
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

          # D-02: `uv` resolves in two legs. Leg 1 is the same bounded upward
          # walk for .venv/bin/uv (it does not exist until Phase 65's tox-uv
          # revert installs it). Leg 2, the on-stop fragment, is the fixed
          # nixpkgs store path -- fixed at flake-evaluation time and therefore
          # un-shadowable. Both legs enter the sandbox, which is what makes
          # `uv run <tool>` carry FHS into every downstream process.
          uvShim = pkgs.writeShellScriptBin "uv" ''
            set -eu
            ${venvWalk "uv" ''exec "${fhsRun}/bin/typsphinx-fhs-run" "${pkgs.uv}/bin/uv" "$@"''}
          '';
        in
        {
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
