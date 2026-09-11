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

## NIX-01 — black, mypy, pytest, sphinx-build

```
$ black --check .
All done! ✨ 🍰 ✨
355 files would be left unchanged.
$ echo "exit:$?"
exit:0

$ mypy typsphinx/
Success: no issues found in 9 source files
$ echo "exit:$?"
exit:0

$ sphinx-build --version
sphinx-build 9.1.0
$ echo "exit:$?"
exit:0
```

All three exit 0 out of this worktree's `.venv`. The shim internal xtrace for each of the four
remaining D-01 tools (`black`, `mypy`, `pytest`, `sphinx-build`), captured the same way as `ruff`
above:

```
$ bash -x "$(command -v black)" --version 2>&1
+ set -eu
+ start=/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a5539e9d70a2734f2
+ dir=/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a5539e9d70a2734f2
+ :
+ '[' -x /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a5539e9d70a2734f2/.venv/bin/black ']'
+ exec /nix/store/dgddrdfkvigqsv48k563szqc8w7xlw2g-typsphinx-fhs-run/bin/typsphinx-fhs-run /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a5539e9d70a2734f2/.venv/bin/black --version
black, 26.5.1 (compiled: yes)
Python (CPython) 3.14.4

$ bash -x "$(command -v mypy)" --version 2>&1
+ set -eu
+ start=/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a5539e9d70a2734f2
+ dir=/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a5539e9d70a2734f2
+ :
+ '[' -x /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a5539e9d70a2734f2/.venv/bin/mypy ']'
+ exec /nix/store/dgddrdfkvigqsv48k563szqc8w7xlw2g-typsphinx-fhs-run/bin/typsphinx-fhs-run /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a5539e9d70a2734f2/.venv/bin/mypy --version
mypy 2.1.0 (compiled: yes)

$ bash -x "$(command -v pytest)" --version 2>&1
+ set -eu
+ start=/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a5539e9d70a2734f2
+ dir=/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a5539e9d70a2734f2
+ :
+ '[' -x /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a5539e9d70a2734f2/.venv/bin/pytest ']'
+ exec /nix/store/dgddrdfkvigqsv48k563szqc8w7xlw2g-typsphinx-fhs-run/bin/typsphinx-fhs-run /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a5539e9d70a2734f2/.venv/bin/pytest --version
pytest 9.1.1

$ bash -x "$(command -v sphinx-build)" --version 2>&1
+ set -eu
+ start=/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a5539e9d70a2734f2
+ dir=/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a5539e9d70a2734f2
+ :
+ '[' -x /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a5539e9d70a2734f2/.venv/bin/sphinx-build ']'
+ exec /nix/store/dgddrdfkvigqsv48k563szqc8w7xlw2g-typsphinx-fhs-run/bin/typsphinx-fhs-run /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a5539e9d70a2734f2/.venv/bin/sphinx-build --version
sphinx-build 9.1.0
```

Each `+ exec` line names `<this worktree>/.venv/bin/<tool>` — no `.venv/bin/uv` fallback leg
needed for any of these four, since each has its own executable in this worktree's fresh
`.venv/bin/` (D-03's six strict shims).

## NIX-04 — full suite (one run, maintainer locale)

One full-suite run through the bare `pytest` shim, no locale variable set anywhere in this task:

```
$ pytest -q -rs
============================= test session starts ==============================
platform linux -- Python 3.14.4, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a5539e9d70a2734f2
configfile: pyproject.toml
testpaths: tests
plugins: cov-7.1.0
collected 1548 items
...
============ 1 failed, 1541 passed, 6 skipped in 128.95s (0:02:08) =============
```

**This does not match the carried-in baseline (1543 passed, 5 skipped).** 1548 collected still
matches exactly. Recorded honestly, not adjusted to fit.

**Interpreter identity — a second axis of difference from the baseline, recorded plainly, not
resolved:**

```
$ cat .venv/pyvenv.cfg
home = /home/yuta/.local/share/uv/python/cpython-3.14-linux-x86_64-gnu/bin
implementation = CPython
uv = 0.11.25
version_info = 3.14
include-system-site-packages = false
prompt = typsphinx

$ python --version
Python 3.13.13
```

This worktree's own `.venv` (created by this task's `uv sync --extra dev`) carries a
uv-managed, uv-downloaded `cpython-3.14` interpreter — not the devShell's nix-provided
`python3-3.13.13` (which is what `python --version` prints on bare `PATH`, and what the
carried-in 1543/5 baseline in `63-GREEN-TREE-EVIDENCE.md` was measured against, since that
baseline was taken in the main checkout's own `.venv`). `pyproject.toml` requires
`>=3.12` and declares no `.python-version`, so `uv sync` is free to resolve either. This
measurement therefore differs from the baseline on **two** axes at once — sandboxed execution
(this worktree's `.venv` runs entirely inside `typsphinx-fhs-run`) and interpreter version
(3.14 here vs. 3.13.13 for the baseline) — and this evidence file does not disentangle which
axis causes which part of the divergence below; both are stated as open, not resolved.

**Every skip, itemised (six, one more than the five-skip baseline):**

| # | Node / location | Reason |
|---|---|---|
| 1 | `tests/test_admonition_greyscale_pipeline.py:71` | Pillow and typst-py are both required for the greyscale pipeline |
| 2 | `tests/test_changelog_page_gate.py:168` | myst-parser is required to build docs/source; it lives in the docs extra only (D-01), so a dev-only CI lane skips this class |
| 3 | `tests/test_changelog_page_gate.py:177` | myst-parser is required to build docs/source; it lives in the docs extra only (D-01), so a dev-only CI lane skips this class |
| 4 | `tests/test_changelog_page_gate.py:187` | myst-parser is required to build docs/source; it lives in the docs extra only (D-01), so a dev-only CI lane skips this class |
| 5 | `tests/test_changelog_page_gate.py:219` | myst-parser is required to build the changelog include fixture; it lives in the docs extra only (D-01) |
| 6 | `tests/test_corpus_gate.py:530` | SC#3 before/after measurement is env-gated -- set TYPSPHINX_CORPUS_REPORT=1 to run it (RESEARCH Open Question 1) |

Skips 2-6 are the five carried-in baseline skips, unchanged. Skip 1
(`test_admonition_greyscale_pipeline.py:71`) is the sixth, new skip — its own skip condition
gates on Pillow importing successfully, and Pillow's import is exactly what fails for the one
test below. This is very likely the same root cause as the failure, not an independent finding.

**The one failure, its node id, and its first traceback frames** (transcribed from this single
full-suite run's own captured output — not a second, separate re-run of the failing node):

Node id: `tests/test_converted_image_collision_render_gate.py::TestConvertedImageCollisionRenderGate::test_pdf_embeds_both_distinctly_sized_images`

```
self = <test_converted_image_collision_render_gate.TestConvertedImageCollisionRenderGate object at 0x725a781849d0>
...
    reader = pypdf.PdfReader(str(pdf_output))
    extracted_sizes = {
        image_file.image.size
        for page in reader.pages
>       for image_file in page.images
                          ^^^^^^^^^^^
        if image_file.image is not None
    }

tests/test_converted_image_collision_render_gate.py:263:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
.venv/lib/python3.14/site-packages/pypdf/_page.py:500: in __iter__
    yield self[i]
.venv/lib/python3.14/site-packages/pypdf/_page.py:496: in __getitem__
    return self.get_function(lst[index])
.venv/lib/python3.14/site-packages/pypdf/_page.py:714: in _get_image
    from .generic._image_xobject import _xobj_to_image  # noqa: PLC0415
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
.venv/lib/python3.14/site-packages/pypdf/generic/_image_xobject.py:27:
>       from PIL import Image, UnidentifiedImageError
.venv/lib/python3.14/site-packages/pypdf/generic/_image_xobject.py:29: in <module>
    from PIL import Image, UnidentifiedImageError
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
.venv/lib/python3.14/site-packages/PIL/Image.py:95: in <module>
    from . import _imaging as core
>       from . import _imaging as core
E       ImportError: libz.so.1: cannot open shared object file: No such file or directory
```

(then, chained inside `pypdf`'s own except-branch, a second `ImportError` re-raised as
`"pillow is required to do image extraction. It can be installed via 'pip install pypdf[image]'"`
— itself only a symptom of the first `ImportError` above, not a separate cause.)

**Attribution: environment-caused, not product behaviour.** The test asserts real, embedded-image
content of a PDF that `typsphinx`'s own `typstpdf` builder already produced correctly earlier in
the same test (`result.returncode == 0` and `pdf_output.exists()` both passed) — the failure is
entirely inside `pypdf`'s own lazy `PIL` import used only for the test's own assertion tooling,
not inside anything `typsphinx` emits or controls. `PIL/Image.py`'s C extension `_imaging` fails
to `dlopen` `libz.so.1` while running under `typsphinx-fhs-run` (this test's `pytest` process is
one of the six shimmed D-01 tools, entered through the FHS sandbox). `flake.nix`'s `fhsRun`
declares no `targetPkgs` today (Claude's Discretion note in `64-CONTEXT.md`: "start from the
minimal `_: [ ]` shape ... add only what a failing measurement demands"), so `zlib` is not
present inside the sandbox's FHS root — this reads as the same class of gap D-07 anticipated for
`cacert`, just for a different package (`zlib`) discovered by a different gate (NIX-04, not
NIX-03's `docs-pdf`). Whether the interpreter-version difference (3.14 here vs. 3.13.13 for the
baseline) also contributes cannot be isolated from this evidence: this worktree's `.venv/bin/python`
is itself a generic-linux ELF requiring the sandbox to run at all, so there is no way to test
Pillow's import bare, outside the sandbox, without either a manual workaround (forbidden by
NIX-05) or leaving the genuine D-09 shape this plan measures.

**Gate result, stated plainly:** NIX-04 does not close on this measurement. The literal
`1543 passed, 5 skipped` gate does not pass — 1 failure and a sixth skip, both traced to a
`libz.so.1` load failure inside the FHS sandbox. Per the same pattern the plan documents for
D-07's `docs-pdf`/`@preview` gap: `flake.nix` is not edited here (scope fence), the failing
transcript is recorded above instead, and the fix (adding `zlib`, or whichever package actually
provides `libz.so.1`, to `fhsRun`'s `targetPkgs`) belongs to a Phase 64 gap-closure plan
(`/gsd-plan-phase 64 --gaps`), re-measured green in a session relaunched after that plan merges.
The baseline itself is not adjusted to match this run.

**CLAUDE.md's worktree idiom, independent of the above** (routes through `uv run`'s own second
shim leg, not the bare `pytest` shim; unaffected by the failure above since
`tests/test_extension.py` carries no Pillow/pypdf dependency):

```
$ uv run pytest tests/test_extension.py -q
============================= test session starts ==============================
platform linux -- Python 3.14.4, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a5539e9d70a2734f2
configfile: pyproject.toml
plugins: cov-7.1.0
collected 6 items

tests/test_extension.py ......                                           [100%]

============================== 6 passed in 0.10s ===============================
$ echo "exit:$?"
exit:0
```
