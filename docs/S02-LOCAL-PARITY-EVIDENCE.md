# S02 — Local/RTD parity evidence: `dot` inside the FHS sandbox

Slice M002/S02 closes the local half of **R021**: `sphinx.ext.graphviz` shells out to the
`dot` binary, no Python extra can supply it, and on the maintainer's NixOS machine `dot`
was absent both in the interactive devShell and inside the `typsphinx-fhs-run`
buildFHSEnv sandbox that `tox -e docs-html` execs into. Upstream `render_dot()` catches
`OSError`, logs one warning, returns `(None, None)`, and the page ships the escaped DOT
source as literal text while the build still **exits 0** — the fail-open shape that let
the defect ship.

R021's acceptance for the flake half is explicitly **the built HTML containing the
rendered img**, not `command -v dot` succeeding in an interactive shell.

## Measurement environment

| Field | Value |
|---|---|
| Checkout | `.gsd-worktrees/M002` (git worktree; `.git` is a file) |
| Commit at measurement | `d6bc4889` |
| Interpreter | uv-managed CPython 3.14.4 (`.venv/pyvenv.cfg` `home = ~/.local/share/uv/python/cpython-3.14-linux-x86_64-gnu/bin`) — **not** the main checkout's nixpkgs python3 |
| Sphinx | 9.1.0 |
| Extras provisioned | `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs` → 9 packages added: accessible-pygments 0.0.5, beautifulsoup4 4.15.0, furo 2025.12.19, mdit-py-plugins 0.6.1, myst-parser 5.1.0, soupsieve 2.8.4, sphinx-autodoc-typehints 3.13.7, sphinx-basic-ng 1.0.0b2, sphinx-intl 2.4.0 |
| Host locale | `LANG=ja_JP.UTF-8`, `LC_ALL` unset |
| Build command | `cd docs && uv run --no-sync sphinx-build -b html source _build/html` (the `changedir`/args `tox -e docs-html` uses) |
| Clean build | `rm -rf docs/_build` before **every** build — an incremental rebuild under-reports warnings |

`graphviz_output_format` default read out of the installed extension source:
`'graphviz_output_format', 'png', 'html'` → the GREEN shape is an `<img>`, not an inline
`<svg>` and not an `<object>` (the `<object>` branch is svg-only).

## RED precondition — `dot` absent in BOTH places

Checking only the interactive shell is **not** meaningful evidence; R021 says so outright,
because the docs build runs inside the sandbox, not in the devShell.

| # | Scope | Command | Exit code | Result |
|---|---|---|---|---|
| 1 | interactive / devShell | `command -v dot` | 1 | no output — absent |
| 2 | **inside FHS sandbox** | `uv run --no-sync bash -c 'command -v dot'` | 1 | no output — absent |

`uv` on PATH is confirmed to be the FHS shim: `grep -q typsphinx-fhs-run "$(command -v uv)"`
passes, and the resolved file is a bash wrapper that walks up to this worktree's
`.venv/bin/<tool>` and execs it via `typsphinx-fhs-run`.

## Warning census — recorded under BOTH locales

A bare `WARNING` grep is locale-sensitive: the sandbox passes the host `LANG` through and
Sphinx localises warning **bodies** (only the `WARNING:` severity token stays English).
Matching therefore uses the substring `dot`, not the full sentence.

| Locale | `grep -c '^WARNING:'` | of which match `dot` | Build exit | Emitted summary |
|---|---|---|---|---|
| host (`ja_JP.UTF-8`) | **1** | 1 | 0 | `build succeeded, 1 warning.` |
| `LC_ALL=C LANG=C` | **1** | 1 | 0 | `build succeeded, 1 warning.` |

The one warning, verbatim under each locale:

```
WARNING: dot コマンド 'dot' は実行できません (graphviz 出力のために必要です)。graphviz_dot の設定を確認してください
WARNING: dot command 'dot' cannot be run (needed for graphviz output), check the graphviz_dot setting
```

So the clean-build baseline is **exactly one** warning and it is the `dot` one. A
case-insensitive `grep -ci WARNING` returns 3 on the same log — it also catches the myst
config echo and the `1 warning.` summary line — so the anchored `^WARNING:` count is the
one to compare against.

## RED artifact shape — `docs/_build/html/user_guide/diagrams.html`

Page built, 29261 bytes.

| Assertion | RED (before, this task) |
|---|---|
| literal `digraph dogfood {` present as page text | **yes** (1 match) — the reported symptom |
| `class="graphviz"` present | **no** (0 matches) |
| `<img src="…graphviz-<40-hex-sha1>.png">` referenced | **no** (0 matches for `graphviz-[0-9a-f]{40}\.png`) |
| any `graphviz-*` file emitted under `docs/_build/html` | **no** (0 files) |
| clean-build `^WARNING:` count | **1** (the `dot` warning) |

Degraded markup, `docs/_build/html/user_guide/diagrams.html:277-283` — the DOT source sits
bare inside the `<figure>` with no `graphviz` wrapper div and no image at all:

```html
<figure class="align-default" id="id1">
digraph dogfood {
    &quot;Vorthaneglim&quot; -&gt; &quot;Pellucidrane&quot;;
}<figcaption>
<p><span class="caption-text">Thessomantic dogfood pipeline</span><a class="headerlink" href="#id1" title="Link to this image">¶</a></p>
</figcaption>
</figure>
```

## Controls held

| Control | Measured |
|---|---|
| `git diff --stat -- typsphinx/` | empty (0 lines) — the Typst route is untouched |
| `git diff --stat -- flake.nix` | empty (0 lines) — the flake edit is deliberately **not** in this task, so the baseline is frozen before it |

## T02 — `dot` provisioned in the flake devShell

**The flake change.** One entry, `pkgs.graphviz`, added to the devShell `mkShell`
`packages` list in `flake.nix`, in the **unconditional base list** alongside
`pkgs.nodejs` / `pkgs.pnpm` / `pkgs.git` / `pkgs.python3` — not inside either
`lib.optionals` platform branch, because `dot` is needed on darwin too and is not
platform-gated the way the FHS shims are. Per **D017** it is deliberately NOT added
to `fhsRun`'s `targetPkgs`, and no `dot` shim was added. A comment beside the entry
records why it is there and that the acceptance evidence is the built HTML, not an
interactive `command -v dot`.

### How the shell was reloaded — read this before reading the rows below

`direnv` never loads inside a git worktree (CLAUDE.md § Worktree-isolated
execution), so **`direnv reload` was not the route used here.** The edited
devShell was invoked explicitly instead:

```
nix develop --no-write-lock-file ./.#default --command bash -c '…'
```

Nix reported `Git tree '…/.gsd-worktrees/M002' is dirty` and evaluated the
working-tree `flake.nix`, i.e. the edit under test. It fetched
`graphviz-12.2.1` from `cache.nixos.org` on first entry. Every row labelled
*reloaded* below was measured inside that invocation; nothing was measured in
the stale ambient shell except the pre-reload control, which is labelled as such.

### Pre-reload control — the gap was still open immediately before the edit took effect

| Scope | Command | rc | Result |
|---|---|---|---|
| ambient (unreloaded) interactive | `command -v dot` | **1** | absent |
| ambient (unreloaded) in-sandbox | `uv run --no-sync bash -c 'command -v dot'` | **1** | absent |

So the two scopes below changed *because of the reloaded flake*, not because `dot`
was already lying around on PATH.

### SCOPE A — interactive / devShell (NOT acceptance evidence, per R021)

R021 states outright that `command -v dot` succeeding in the interactive shell is
**not** sufficient evidence. This scope is recorded only for completeness.

| Measurement | Value |
|---|---|
| `command -v dot` | `/nix/store/d5nx177j7n96jmd38x9fpankrpkp5szj-graphviz-12.2.1/bin/dot` (rc=0) |
| `dot -V` | `dot - graphviz version 12.2.1 (0)` |

### SCOPE B — INSIDE the `typsphinx-fhs-run` sandbox (the load-bearing scope)

This is the scope that matters: `tox -e docs-html` runs `sphinx-build` through a
PATH shim that `exec`s into the buildFHSEnv sandbox, so `dot` must be reachable by
the sandboxed **child**. Reached here via `uv run --no-sync`, whose `uv` was
confirmed to be the shim (2 `typsphinx-fhs-run` references in the shim script)
inside the reloaded shell.

| Measurement | Value |
|---|---|
| `command -v dot` | `/nix/store/d5nx177j7n96jmd38x9fpankrpkp5szj-graphviz-12.2.1/bin/dot` (rc=0) |
| `dot -V` | `dot - graphviz version 12.2.1 (0)` |
| real render: `printf 'digraph x { a -> b }' \| dot -Tpng -o /tmp/p02_render.png` | rc=**0** |
| rendered file | `/tmp/p02_render.png`, **3515 bytes**, non-empty |
| `file` output | `PNG image data, 83 x 155, 8-bit/color RGBA, non-interlaced` |

The same store path resolves in both scopes, which is the D017 mechanism
re-confirmed: the sandbox inherits the caller's PATH appended after its own FHS
`/usr/bin`, so an `mkShell` entry is visible inside without a `targetPkgs` entry.
The in-sandbox render is the decisive row — it proves `dot` does not merely resolve
but actually **executes and produces image bytes** under the sandbox's loader.

### T02 invariants — proven unchanged, not merely unmentioned

| Invariant | Method | Result |
|---|---|---|
| `fhsRun`'s `targetPkgs` | `diff` of the `targetPkgs` line vs `git show HEAD:flake.nix` | **unchanged** (`targetPkgs = p: [ p.zlib ];`, line 70) |
| `venvShimNames` roster | `diff` of the whole block vs `HEAD` | **unchanged** (rc=0); still exactly `tox`, `ruff`, `black`, `mypy`, `pytest`, `sphinx-build` |
| no `dot` shim added | `grep -c '"dot"' flake.nix` | **0** — the seven-entrypoint invariant is intact |
| `typsphinx/` untouched | `git diff --stat -- typsphinx/ \| wc -l` | **0** |
| `@preview` versions untouched | `git diff --name-only` over `writer.py`, `template_engine.py`, `templates/base.typ` | **0** files — the three-site sync hazard was not touched |
| whole-worktree diff surface | `git diff --name-only` | `flake.nix` only |
| flake still evaluates everywhere | `nix eval ./.#devShells.<sys>.default.name` | rc=0 for all four declared systems (`x86_64-linux`, `aarch64-linux`, `x86_64-darwin`, `aarch64-darwin`) — the unconditional placement does not break the unbuildable darwin branch |

### What T02 does NOT establish

`dot` being reachable and renderable is a *precondition*, not the slice's
acceptance. T02 does **not** show that `sphinx.ext.graphviz` actually invoked it,
that the diagrams page changed, or that the warning baseline moved off one. Those
are T03's clean-build measurements, in the GREEN column below.

## GREEN column

Pending T03. T02 is **done**: `pkgs.graphviz` is provisioned in the flake devShell
and `dot` is proven to execute and render a real PNG inside the sandbox after a
reload (see the T02 section above). T03 reruns the clean `docs-html` build and
fills the after-column of every RED row above.
