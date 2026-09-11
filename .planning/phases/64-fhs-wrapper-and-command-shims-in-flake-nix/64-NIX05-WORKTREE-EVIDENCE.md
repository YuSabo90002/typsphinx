# Phase 64 Plan 02 — NIX-01..NIX-05 Worktree Procedure Evidence

Measured shape: genuine D-09 shape — inherited session PATH, no nix develop wrapper, no direnv exec (orchestrator note 3).

This is a Claude Code executor session launched **after** plan 64-01's `flake.nix` edit merged
into the main checkout, from a shell where direnv had already loaded the new devShell (STATE.md:
"session relaunched from a direnv-loaded main-checkout shell"). Every command below runs through
this session's own inherited `PATH` — never `nix develop --command`, never `direnv exec` — inside
this one, freshly created, nested worktree.

## D-09 head check (session launched after 64-01 merged)

```
$ date -u +%FT%TZ
2026-09-11T15:16:52Z

$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a5539e9d70a2734f2

$ test -f .git; echo "exit:$?"
exit:0

$ test ! -e .venv; echo "exit:$?"
exit:0

$ test ! -e .tox; echo "exit:$?"
exit:0

$ command -v ruff
/nix/store/vp86ji36v1nyp4q8d85i49hpyz43zszq-ruff/bin/ruff

$ command -v uv
/nix/store/f1y7m4b5vxrbwszkrni3yc2lv0x22zcj-uv/bin/uv

$ grep -c typsphinx-fhs-run "$(command -v ruff)"
1

$ grep -c typsphinx-fhs-run "$(command -v uv)"
2

$ echo "DIRENV_DIR=$DIRENV_DIR"
DIRENV_DIR=-/home/yuta/Documents/typsphinx

$ echo "IN_NIX_SHELL=$IN_NIX_SHELL"
IN_NIX_SHELL=impure

$ direnv status 2>&1 | grep -E 'RC'
Loaded RC path /home/yuta/Documents/typsphinx/.envrc
Loaded RC allowed 0
Loaded RC allowPath /home/yuta/.local/share/direnv/allow/bf1fd32bf1c4479acb50f4e7f9df3502c790ddcb3e83bb6a56777e3b28715088
Found RC path /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a5539e9d70a2734f2/.envrc
Found RC allowed 1
Found RC allowPath /home/yuta/.local/share/direnv/allow/e39d4713779ee742d476d1b95472eac95348f8e79f48d431ac1bbac4557a9341
```

`.venv` and `.tox` are both absent at the head check — nothing is provisioned yet. Both `ruff` and
`uv` resolve to `/nix/store/…` shim paths, and both shim files contain the `typsphinx-fhs-run`
marker (`uv`'s shim references it twice — once directly for the sandbox-entered venv-walk leg,
once again inside the fixed nixpkgs-`uv` fallback leg, D-02). `direnv status`'s `Loaded RC` block
is the main checkout's `.envrc` — `allowed 0` (allowed), which is what this session's frozen `PATH`
actually came from. `direnv status`'s `Found RC` block is *this worktree's own* `.envrc`, found by
walking up from `pwd` — `allowed 1` (**not** allowed): this worktree's `.envrc` has never been
individually `direnv allow`-ed.

**NIX-05's open question, answered by this observation in one sentence:** the shim `PATH` is
reachable in this worktree purely by inheritance from the launching session — never via a
`direnv allow` for this worktree's own path, since `Found RC allowed 1` shows that path was never
allowed at all.

## Provisioning and tree identity

The one documented provisioning line, transcribed exactly as CLAUDE.md specifies it, with the
tail of its output:

```
$ env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev
...
 + pytest-cov==7.1.0
 + python-discovery==1.4.3
 + pytokens==0.4.1
 + pyyaml==6.0.3
 + readme-renderer==45.0
 + requests==2.34.2
 + requests-toolbelt==1.0.0
 + rfc3986==2.0.0
 + rich==15.0.0
 + roman-numerals==4.1.0
 + ruff==0.15.20
 + secretstorage==3.5.0
 + snowballstemmer==3.1.1
 + sphinx==9.1.0
 + sphinxcontrib-applehelp==2.0.0
 + sphinxcontrib-devhelp==2.0.0
 + sphinxcontrib-htmlhelp==2.1.0
 + sphinxcontrib-jsmath==1.0.1
 + sphinxcontrib-qthelp==2.0.0
 + sphinxcontrib-serializinghtml==2.0.0
 + tomli-w==1.2.0
 + tox==4.56.1
 + tox-uv-bare==1.35.2
 + twine==6.2.0
 + types-docutils==0.22.3.20260518
 + typing-extensions==4.16.0
 + typsphinx==0.9.2 (from file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-a5539e9d70a2734f2)
 + typst==0.15.0
 + urllib3==2.7.0
 + virtualenv==21.5.1
```

No manual symlink and no ELF-patching step ran anywhere in this procedure.

The `uv` shim's internal xtrace, captured by running `bash -x <shim-path> --version` directly
against the shim's own store path (not routed through a wrapper subprocess, so every internal
command the shim script itself runs is visible):

```
$ bash -x "$(command -v uv)" --version 2>&1 | grep -v '^uv '
+ set -eu
+ start=/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a5539e9d70a2734f2
+ dir=/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a5539e9d70a2734f2
+ :
+ '[' -x /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a5539e9d70a2734f2/.venv/bin/uv ']'
+ '[' -e /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a5539e9d70a2734f2/.git ']'
+ break
+ exec /nix/store/dgddrdfkvigqsv48k563szqc8w7xlw2g-typsphinx-fhs-run/bin/typsphinx-fhs-run /nix/store/cgvijxnmydknslkl368k4j4j43akvl8b-uv-0.11.25/bin/uv --version
```

`.venv/bin/uv` does not exist yet (D-02 — that path only appears after Phase 65's `tox-uv-bare` →
`tox-uv` revert), so the bounded upward walk breaks at the first `.git` ancestor (this worktree's
own `.git` file) and falls through to leg 2: the fixed nixpkgs `uv` store path,
`/nix/store/cgvijxnmydknslkl368k4j4j43akvl8b-uv-0.11.25/bin/uv`, entered through
`typsphinx-fhs-run`. The `+ exec` line names that `/nix/store/…-uv-…/bin/uv` path exactly, proving
D-02's two-leg resolution and that this session's `-u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT`
unsets reached `uv` through the sandbox (D-06) — an inherited `VIRTUAL_ENV` never redirected the
sync, since the sync wrote this worktree's own fresh `.venv` (confirmed by the tree-identity check
below).

Tree identity — proving the editable install binds this worktree, not the main checkout:

```
$ uv run python -c 'import typsphinx,os;print(os.path.realpath(typsphinx.__file__))'
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a5539e9d70a2734f2/typsphinx/__init__.py

$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a5539e9d70a2734f2
```

`typsphinx.__file__` resolves to `<pwd -P>/typsphinx/__init__.py` exactly — the editable install
this worktree's `uv sync` created binds `import typsphinx` to this worktree's own source tree, not
the main checkout's.

## NIX-01 — ruff

```
$ ruff --version
ruff 0.15.20
```

Compared against `uv.lock:1209-1210` (read at run time, this task's `read_first`):

```
[[package]]
name = "ruff"
version = "0.15.20"
```

Exact match. The shim's internal xtrace, captured the same way as `uv` above:

```
$ bash -x "$(command -v ruff)" --version 2>&1
+ set -eu
+ start=/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a5539e9d70a2734f2
+ dir=/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a5539e9d70a2734f2
+ :
+ '[' -x /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a5539e9d70a2734f2/.venv/bin/ruff ']'
+ exec /nix/store/dgddrdfkvigqsv48k563szqc8w7xlw2g-typsphinx-fhs-run/bin/typsphinx-fhs-run /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a5539e9d70a2734f2/.venv/bin/ruff --version
ruff 0.15.20
```

Unlike `uv`, `ruff`'s venv walk finds `.venv/bin/ruff` immediately (D-01/D-03's six strict shims —
this worktree's own fresh `uv sync` just created it), so the `+ exec` line names
`<this worktree>/.venv/bin/ruff` directly — not a nixpkgs store path. This distinguishes the
worktree's own binary from the main checkout's identically-versioned `.venv/bin/ruff`: the version
string alone (`ruff 0.15.20`) cannot tell the two apart, since the main checkout's older `.venv`
also reports 0.15.20 — only this xtrace path, rooted at `/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a5539e9d70a2734f2/.venv/bin/ruff`, proves which tree actually ran.

```
$ ruff check .
All checks passed!
$ echo "exit:$?"
exit:0
```

`ruff check .` runs to completion with exit 0 and no findings — a genuine ruff verdict on this
worktree's source tree, not an environment failure.

Outside-sandbox control — the same worktree, the same unmodified `.venv/bin/ruff` file, invoked
bare (no shim in front of it):

```
$ .venv/bin/ruff --version
Could not start dynamically linked executable: .venv/bin/ruff
NixOS cannot run dynamically linked executables intended for generic
linux environments out of the box. For more information, see:
https://nix.dev/permalink/stub-ld
$ echo "exit:$?"
exit:127
```

Still rejected at rc 127 with the stub-ld message, in this same worktree, on this same binary —
confirming the shim (not some change to the file itself) is what makes `ruff` run.
