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

## T03 — GREEN column: the clean `docs-html` rebuild

### Route used

`tox -e docs-html` itself — the command the success criteria name — not the direct
`sphinx-build` fallback. It provisioned and ran in this worktree without trouble
(`docs-html: OK`, `runner = uv-venv-lock-runner`, `extras = docs`, `changedir = docs`).
As in T02, the reloaded devShell was entered explicitly, because `direnv` never loads
inside a git worktree:

```
nix develop --no-write-lock-file ./.#default --command bash -c 'tox -e docs-html'
```

`dot` resolved inside that invocation to the same store path T02 measured —
`/nix/store/d5nx177j7n96jmd38x9fpankrpkp5szj-graphviz-12.2.1/bin/dot`,
`dot - graphviz version 12.2.1 (0)`. `rm -rf docs/_build` ran before **every** build
below; no measurement here is an incremental rebuild.

### Before / after

| Assertion | RED (T01) | GREEN (T03) |
|---|---|---|
| literal `digraph dogfood {` in `diagrams.html` | **present** (1 match) — the reported symptom | **absent** (0 matches) |
| `digraph dogfood` as *visible page text* (tags stripped) | present | **0 matches** |
| `class="graphviz"` wrapper | **absent** (0) | **present** (2 — the `div` and the `img` class) |
| `<img src="…graphviz-<40-hex-sha1>.png">` | **absent** (0) | **present** (1) |
| referenced PNG exists on disk, non-empty | **no** (0 `graphviz-*` files emitted) | **yes** — see below |
| diagram emitted as inline `<svg>` or `<object>` | n/a | **no** — 0 `<object>`; `graphviz_output_format` default `png` holds |
| clean-build `^WARNING:` count, host locale | **1** (the `dot` warning) | **0** |
| clean-build `^WARNING:` count, `LC_ALL=C LANG=C` | **1** (the `dot` warning) | **0** |
| strict `-W` clean build | would fail (1 warning) | **exits 0** under both locales |
| `git diff --stat -- typsphinx/` | empty | **empty** — Typst route untouched |
| `diagrams.html` size | 29261 bytes | 29381 bytes |

The rendered PNG, resolved from the page's `src` and `stat`ed on disk rather than trusted
as a string:

| Field | Value |
|---|---|
| `src` on the page | `../_images/graphviz-9d601b680ab94eac1febdc364a0d914f474368d3.png` |
| resolved path | `docs/_build/html/_images/graphviz-9d601b680ab94eac1febdc364a0d914f474368d3.png` |
| size | **11608 bytes** (non-empty) |
| `file` output | `PNG image data, 220 x 155, 8-bit/color RGBA, non-interlaced` |
| sibling emitted | `…png.map`, 41 bytes (the imagemap `dot` also produced) |

The GREEN markup, `docs/_build/html/user_guide/diagrams.html:278` — the `graphviz`
wrapper div and a real `img` now sit where the bare DOT source used to:

```html
<div class="graphviz"><img src="../_images/graphviz-9d601b680ab94eac1febdc364a0d914f474368d3.png" alt="Directed graph with two nodes, Vorthaneglim pointing to Pellucidrane." class="graphviz" /></div>
```

A caution for whoever reads the `<svg` count: `grep -c '<svg' diagrams.html` returns **27**
on the GREEN page, and none of those are the diagram. They are furo's theme chrome (nav and
admonition icons). The diagram's own output format is proven `png` by the `<img>` tag above
and by the file on disk, not by that count.

### Which warning route closed — the strict `-W` one

Per MEM073 the strict route was preferred over grepping a localised log, and it is the one
that closed: a clean `-W` build **exits 0**, which proves zero warnings independent of
message language. The log-grep route is recorded alongside it and agrees.

| Route | Locale | Command | Exit | `^WARNING:` | of which `dot` |
|---|---|---|---|---|---|
| strict | host (`ja_JP.UTF-8`) | `sphinx-build -W -b html source _build/html` | **0** | 0 | 0 |
| strict | `LC_ALL=C LANG=C` | `sphinx-build -W -b html source _build/html` | **0** | 0 | 0 |
| log grep | host (`ja_JP.UTF-8`) | `tox -e docs-html` | 0 | **0** (was 1) | 0 (was 1) |

No unrelated pre-existing warning surfaced under `-W`, so the honest fallback the plan
allows for was not needed. The MEM075 clean-build baseline for this tree therefore moves
from **exactly one** `dot` warning to **zero**, which is what makes a future regression of
this class detectable by a `-W` build instead of requiring someone to notice a missing
image on a published page.

### Deviation: the raw DOT text needed a `:alt:` to actually leave the page

This is the one unplanned change in T03, and it is recorded here rather than folded away,
because the mechanism is not obvious and S03's gate has to be written against it.

The first GREEN build rendered the img correctly **and still matched
`grep 'digraph dogfood {'`**. Measured cause, in the installed extension at
`sphinx/ext/graphviz.py:384`:

```python
alt = node.get('alt', self.encode(code).strip())
```

With no `:alt:` option, upstream uses the **DOT source itself** as the img's `alt`
attribute. So the literal string survived — but only as an attribute. Measured on that
build: `digraph dogfood` matched **1** time in the raw HTML and **0** times in the
tag-stripped visible text. The user-visible defect was already fixed at that point; the
grep marker was not.

The milestone success criteria require that marker to be *independently absent*, so
`docs/source/user_guide/diagrams.rst` now passes an explicit `:alt:` on the dogfood
directive:

```rst
.. graphviz::
   :caption: Thessomantic dogfood pipeline
   :alt: Directed graph with two nodes, Vorthaneglim pointing to Pellucidrane.
```

Three things make this a fix rather than teaching to the test. It is the upstream-supported
option (`option_spec` line 122). The diagrams page's own prose *already* advertises `:alt:`
as supported, and `tests/test_graphviz_docs_gate.py::test_page_documents_the_supported_options`
already asserts that — so the dogfood diagram was the one place not practising what the page
documents. And it is the correct accessibility behaviour: a screen reader previously read
raw DOT syntax aloud. The DOT body in the directive is untouched, so the diagram, its
caption, and its node labels are unchanged — the PNG's sha1
(`9d601b68…`) is **byte-identical before and after** the `:alt:` addition, confirming `alt`
is not an input to the render.

**Note for S03.** The gate has two defensible assertions available, and they are not
equivalent. Asserting `digraph dogfood {` is absent from the raw HTML is what the current
tree satisfies, but it is only true because of the `:alt:` above and would regress if
anyone removed that option. Asserting it is absent from the *tag-stripped visible text* is
the more robust statement of the actual defect and holds with or without `:alt:`. Prefer
the latter, or assert both.

### Controls held in T03

| Control | Method | Result |
|---|---|---|
| `typsphinx/` untouched | `git diff --stat -- typsphinx/ \| wc -l` | **0** |
| no test file added or modified | `git diff --stat -- tests/ \| wc -l` | **0** |
| existing `typstpdf` gate not broken by the rst edit | `pytest tests/test_graphviz_docs_gate.py -q` | **14 passed** |
| `@preview` versions untouched | not in the diff | `writer.py`, `template_engine.py`, `templates/base.typ` all unchanged |
| T03's whole diff surface | `git diff --name-only` | `docs/source/user_guide/diagrams.rst` only |

### What this evidence does NOT cover

Stated plainly so nothing here is read as more than it is:

- **The published RTD page (S04).** Everything above is a *local* build on the maintainer's
  NixOS machine. The `.readthedocs.yaml` `build.apt_packages` half of R021 is a separate
  provisioning route, and the published page only changes after merge plus an RTD rebuild.
  Nothing in T03 touched or observed readthedocs.org.
- **The encoded HTML artifact gate (S03).** T03 asserted the GREEN shape with ad-hoc
  commands recorded in this file. No test encodes it yet, so this measurement is not
  regression-protected; that is S03's deliverable, and the note above tells it which
  assertion to pick.
- **The ja translated site (R022).** Deferred. The build above ran with the host
  `LANG=ja_JP.UTF-8` only to probe warning localisation; it emitted the **English**
  (`code: en`) site. The ja catalogue was never built or inspected.
- **CI.** The flake devShell is a maintainer-machine concern; CI has no shims and does not
  build docs through this route.
