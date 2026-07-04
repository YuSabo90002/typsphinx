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

      # gsd-pi (https://github.com/open-gsd/gsd-pi) is distributed only as an
      # npm package (@opengsd/gsd-pi) that pulls in prebuilt native components
      # (Rust/Python/shell). It cannot be cleanly packaged for Nix, so instead
      # we install it globally into a project-local npm prefix. Inside the FHS
      # sandbox the dynamic loader and standard library paths look like a normal
      # Linux distro, so gsd-pi's prebuilt binaries run without patching.
      gsdPrefixDir = ".gsd-pi";

      # Sourced when entering the shell. Wires up the project-local npm global
      # prefix and installs gsd-pi on first entry (idempotent afterwards).
      gsdSetup = ''
        export GSD_PI_HOME="$PWD/${gsdPrefixDir}"
        export NPM_CONFIG_PREFIX="$GSD_PI_HOME/npm-global"
        export PATH="$NPM_CONFIG_PREFIX/bin:$PATH"
        mkdir -p "$NPM_CONFIG_PREFIX"

        if ! command -v gsd-pi >/dev/null 2>&1; then
          echo "==> Installing @opengsd/gsd-pi into $NPM_CONFIG_PREFIX ..."
          npm install -g @opengsd/gsd-pi@latest || \
            echo "!! gsd-pi install failed (network?). Re-run: npm install -g @opengsd/gsd-pi@latest"
        fi
        echo "gsd-pi devshell ready. Run: gsd-pi --help"
      '';
    in
    {
      devShells = forAllSystems (
        system:
        let
          pkgs = pkgsFor system;

          # The FHS sandbox. targetPkgs are the tools/libs visible on the
          # standard FHS paths (/usr/bin, /usr/lib, ...) inside the sandbox.
          fhs = pkgs.buildFHSEnv {
            name = "typsphinx-gsd-pi";
            targetPkgs = p: [
              # Runtime for gsd-pi.
              p.nodejs
              p.git
              # Python toolchain: uv for fast dependency/venv management.
              p.python3
              p.uv
              p.stdenv.cc.cc.lib
              p.zlib
              p.openssl
              p.curl
            ];
            profile = gsdSetup;
            runScript = "bash";
          };
        in
        {
          # buildFHSEnv is Linux-only. On Linux the default shell IS the FHS
          # sandbox (via `.env`, which execs into the bwrap chroot). On Darwin
          # we fall back to a plain shell without FHS.
          default =
            if pkgs.stdenv.isLinux then
              fhs.env
            else
              pkgs.mkShell {
                packages = [
                  pkgs.nodejs
                  pkgs.git
                  pkgs.python3
                  pkgs.uv
                ];
                shellHook = gsdSetup;
              };
        }
      );
    };
}
