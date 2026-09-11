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

          # Tracer shim: proves one command name travels shim -> FHS
          # passthrough -> this worktree's own .venv/bin/ruff.
          ruffShim = pkgs.writeShellScriptBin "ruff" ''
            set -eu
            ${venvWalk "ruff" (venvShimOnStop "ruff")}
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
              ++ pkgs.lib.optionals pkgs.stdenv.hostPlatform.isLinux [ ruffShim ]
              ++ [ pkgs.uv ];
          };
        }
      );
    };
}
