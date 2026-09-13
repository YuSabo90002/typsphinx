Measured shape: genuine D-09 shape — inherited session PATH of a session relaunched after 64-05 merged; no nix develop wrapper, no direnv exec.

## Session check

```
$ command -v ruff
/nix/store/vxcr1f2x7ywkyvwli0sykhgwsmkg800k-ruff/bin/ruff

$ grep -oE '/nix/store/[a-z0-9]{32}-typsphinx-fhs-run/bin/typsphinx-fhs-run' /nix/store/vxcr1f2x7ywkyvwli0sykhgwsmkg800k-ruff/bin/ruff | head -1
/nix/store/99fm4lqkp4kab20d3blfbwajnprmlbfx-typsphinx-fhs-run/bin/typsphinx-fhs-run

$ FHS=/nix/store/99fm4lqkp4kab20d3blfbwajnprmlbfx-typsphinx-fhs-run/bin/typsphinx-fhs-run
$ "$FHS" /bin/sh -c 'test -e /usr/lib/libz.so.1'; echo "exit:$?"
exit:0
```

The rootfs prefix (`/nix/store/99fm4lqkp4kab20d3blfbwajnprmlbfx-typsphinx-fhs-run`) equals the `New fhs-run:` line recorded in `64-LIBZ-FIX-EVIDENCE.md` § "Session relaunch required before wave 5":

```
New fhs-run: /nix/store/99fm4lqkp4kab20d3blfbwajnprmlbfx-typsphinx-fhs-run
```

This is the relaunched session. Per `64-LIBZ-FIX-EVIDENCE.md`'s GREEN section, the same `libz.so.1` presence test against the pre-relaunch root `dgddrdfkvigqsv48k563szqc8w7xlw2g` exits non-zero (`OLD_FHS ... test -e /usr/lib/libz.so.1; echo "exit=$?"` → `exit=1`) — this session is not that root, so the precondition for every task in this plan holds and provisioning may proceed.

## D-09 head check (session relaunched after 64-05 merged)

```
$ date -u +%FT%TZ
2026-09-12T04:37:55Z

$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a86b68cdd93e9624b

$ test -f .git && echo IS_WORKTREE
IS_WORKTREE

$ test ! -e .venv && echo NO_VENV
NO_VENV
$ test ! -e .tox && echo NO_TOX
NO_TOX

$ for t in uv tox ruff black mypy pytest sphinx-build; do printf '%s: %s\n' "$t" "$(command -v $t)"; done
uv: /nix/store/3vpzk25whpm7s8zq5flpk8gbpkggj9np-uv/bin/uv
tox: /nix/store/r70g13f57bbrw66k56dlqk9bbbcpch33-tox/bin/tox
ruff: /nix/store/vxcr1f2x7ywkyvwli0sykhgwsmkg800k-ruff/bin/ruff
black: /nix/store/axxz4wqgrh8dwvv1qd3j3v9668qp8l4a-black/bin/black
mypy: /nix/store/4yaxrcdb3y2gwi9wjxpblikg3jypa9x1-mypy/bin/mypy
pytest: /nix/store/7q7lwxpw3xlz4h5rwka4nq0rjk1191yh-pytest/bin/pytest
sphinx-build: /nix/store/3w4dy4lickl14insmwl48fhxbq0vxi4s-sphinx-build/bin/sphinx-build

$ echo "DIRENV_DIR=$DIRENV_DIR"; echo "IN_NIX_SHELL=$IN_NIX_SHELL"
DIRENV_DIR=-/home/yuta/Documents/typsphinx
IN_NIX_SHELL=impure

$ direnv status 2>&1 | grep -E 'RC'
Loaded RC path /home/yuta/Documents/typsphinx/.envrc
Loaded RC allowed 0
Loaded RC allowPath /home/yuta/.local/share/direnv/allow/bf1fd32bf1c4479acb50f4e7f9df3502c790ddcb3e83bb6a56777e3b28715088
Found RC path /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a86b68cdd93e9624b/.envrc
Found RC allowed 1
Found RC allowPath /home/yuta/.local/share/direnv/allow/cfabbd32c023acee25fda4b972f7980474617a7f40998d2b43a4d1b3b2f1f373
```

All seven `command -v` paths are byte-identical to `64-LIBZ-FIX-EVIDENCE.md`'s `New shim paths` table (`uv`, `tox`, `ruff`, `black`, `mypy`, `pytest`, `sphinx-build`), `.venv` and `.tox` were both absent before any provisioning, and this was observed purely by session-PATH inheritance — no `direnv allow` was run for this worktree path and no command was wrapped in `nix develop`.

**Reachability answer:** the fixed-rootfs shim PATH is reachable in this fresh nested worktree by pure session inheritance, before any per-worktree `direnv allow` and before `uv sync` provisions anything.

## Provisioning, interpreter provenance and tree identity

```
$ env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev
... (tail)
 + typsphinx==0.9.2 (from file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-a86b68cdd93e9624b)
 + typst==0.15.0
 + urllib3==2.7.0
 + virtualenv==21.5.1

$ cat .venv/pyvenv.cfg
home = /home/yuta/.local/share/uv/python/cpython-3.14-linux-x86_64-gnu/bin
implementation = CPython
uv = 0.11.25
version_info = 3.14
include-system-site-packages = false
prompt = typsphinx
```

Exactly one documented provisioning line, verbatim, no interpreter pin (D-04). Baseline interpreter for comparison (63-GREEN-TREE-EVIDENCE.md, `1543 passed, 5 skipped`): nix `python3-3.13.13`. This worktree's `.venv` is uv-managed `cpython-3.14` (`home` = `/home/yuta/.local/share/uv/python/cpython-3.14-linux-x86_64-gnu/bin`, `version_info` = `3.14`) — a genuine cross-version divergence from the baseline interpreter, carried as an assumption per the plan's "Flagged edge-probe assumptions" section, never normalised away by pinning.

```
$ uv run python -c 'import typsphinx,os;print(os.path.realpath(typsphinx.__file__))'
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a86b68cdd93e9624b/typsphinx/__init__.py

$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a86b68cdd93e9624b
```

`typsphinx.__file__`'s realpath equals `$(pwd -P)/typsphinx/__init__.py` exactly — this worktree's own editable install, not the main checkout's. This proves the `-u` unsets reached `uv` through the sandbox (D-06) and that the editable install binds this worktree (NIX-05 adjacency edge).

No manual symlink and no ELF-patching step was used anywhere in this task (NIX-05).

## NIX-01 — ruff (regression)

```
$ ruff --version
ruff 0.15.20

$ awk 'NR==1209 || NR==1210' uv.lock
name = "ruff"
version = "0.15.20"
```

`ruff --version` prints exactly `ruff 0.15.20`, matching `uv.lock:1209-1210`'s pin read at run time.

```
$ RUFF_SHIM="$(command -v ruff)"
$ bash -x "$RUFF_SHIM" --version 2>&1 | grep '+ exec'
+ exec /nix/store/99fm4lqkp4kab20d3blfbwajnprmlbfx-typsphinx-fhs-run/bin/typsphinx-fhs-run /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a86b68cdd93e9624b/.venv/bin/ruff --version
```

(The harness refused a literal xtrace invocation combining git-adjacent path text in one compound Bash call; per 64-02's documented workaround, the `bash -x` invocation was written into a helper script in the session scratchpad — `/tmp/claude-1000/-home-yuta-Documents-typsphinx/09a4c0d3-1961-4e01-834d-b0945b94cf40/scratchpad/64-06/xtrace-ruff2.sh` — and run from there; never a tracked file.)

The `+ exec` line names `/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a86b68cdd93e9624b/.venv/bin/ruff` — this worktree's own `.venv/bin/ruff`, resolved through the new-rootfs FHS wrapper.

```
$ test -x "$PWD/.venv/bin/ruff" && echo RUFF_BIN_EXISTS
RUFF_BIN_EXISTS

$ ruff check .
All checks passed!
$ echo "exit:$?"
exit:0
```

`ruff check .` ran to completion: `All checks passed!`, exit 0.

## Tracer — the path that failed in 64-02

```
$ ls -d "$(pwd)"/.venv/lib/python3.*/site-packages
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a86b68cdd93e9624b/.venv/lib/python3.14/site-packages

$ uv run python -S -c "import sys; sys.path.insert(0, '/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a86b68cdd93e9624b/.venv/lib/python3.14/site-packages'); import PIL._imaging; print('PIL._imaging OK')"
PIL._imaging OK
```

The `-S` probe (import-order independent: session PATH → `uv` shim leg 2 → new rootfs → uv-managed cp3.14 → Pillow) prints `PIL._imaging OK`.

```
$ pytest tests/test_converted_image_collision_render_gate.py -q -rs
============================= test session starts ==============================
platform linux -- Python 3.14.4, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a86b68cdd93e9624b
configfile: pyproject.toml
plugins: cov-7.1.0
collected 3 items

tests/test_converted_image_collision_render_gate.py ...                  [100%]

============================== 3 passed in 1.50s ===============================
```

The exact node that failed in 64-02 with the `libz.so.1` ImportError now shows 3 passed, 0 failed, through the bare `pytest` shim in the genuine D-09 shape.

## NIX-04 — full suite (one run, maintainer locale)

One full-suite run, through the bare `pytest` shim, under the maintainer's own locale — no locale variable set anywhere in this command (D-08):

```
$ pytest -q -rs
============================= test session starts ==============================
platform linux -- Python 3.14.4, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a86b68cdd93e9624b
configfile: pyproject.toml
testpaths: tests
plugins: cov-7.1.0
collected 1548 items

tests/test_abbr_pep_separator_render_gate.py ..                          [  0%]
...
tests/test_admonition_greyscale_pipeline.py ..                           [  1%]
...
tests/test_xref_whole_document_guard_render_gate.py ........             [100%]

=========================== short test summary info ============================
SKIPPED [1] tests/test_changelog_page_gate.py:168: myst-parser is required to build docs/source; it lives in the docs extra only (D-01), so a dev-only CI lane skips this class
SKIPPED [1] tests/test_changelog_page_gate.py:177: myst-parser is required to build docs/source; it lives in the docs extra only (D-01), so a dev-only CI lane skips this class
SKIPPED [1] tests/test_changelog_page_gate.py:187: myst-parser is required to build docs/source; it lives in the docs extra only (D-01), so a dev-only CI lane skips this class
SKIPPED [1] tests/test_changelog_page_gate.py:219: myst-parser is required to build the changelog include fixture; it lives in the docs extra only (D-01)
SKIPPED [1] tests/test_corpus_gate.py:530: SC#3 before/after measurement is env-gated -- set TYPSPHINX_CORPUS_REPORT=1 to run it (RESEARCH Open Question 1)
================= 1543 passed, 5 skipped in 113.00s (0:01:53) ==================
```

`collected 1548 items` (the expected count) and the summary reads exactly **1543 passed, 5 skipped** — the carried-in baseline, byte-for-byte, under the same platform header the session's `.venv` interpreter produces (`Python 3.14.4`).

**Skip itemisation (5 total, verbatim reasons):**

| # | Node | Reason |
|---|------|--------|
| 1 | `tests/test_changelog_page_gate.py:168` | myst-parser is required to build docs/source; it lives in the docs extra only (D-01), so a dev-only CI lane skips this class |
| 2 | `tests/test_changelog_page_gate.py:177` | myst-parser is required to build docs/source; it lives in the docs extra only (D-01), so a dev-only CI lane skips this class |
| 3 | `tests/test_changelog_page_gate.py:187` | myst-parser is required to build docs/source; it lives in the docs extra only (D-01), so a dev-only CI lane skips this class |
| 4 | `tests/test_changelog_page_gate.py:219` | myst-parser is required to build the changelog include fixture; it lives in the docs extra only (D-01) |
| 5 | `tests/test_corpus_gate.py:530` | SC#3 before/after measurement is env-gated -- set TYPSPHINX_CORPUS_REPORT=1 to run it (RESEARCH Open Question 1) |

Four are the myst-parser docs-extra gap (`test_changelog_page_gate.py`), one is the env-gated corpus report (`test_corpus_gate.py`) — exactly matching the carried-in baseline's itemisation.

**Pillow-gated skip confirmed gone.** `tests/test_admonition_greyscale_pipeline.py` shows `..` (2 passed, 0 skipped) in the live run above — the skip recorded at `tests/test_admonition_greyscale_pipeline.py:71` (row 1 of 64-02's six-skip table, caused by the same `libz.so.1` failure) does not appear anywhere in the short test summary. A sixth skip would have been a finding; none occurred.

No `## Baseline divergence` section follows: the summary read exactly `1543 passed, 5 skipped`, matching the carried-in baseline with no differing node. No locale variable was set in any command of this task.

## NIX-02 — four tox environments, cold in the fixed sandbox

```
$ test ! -e .tox && echo NO_TOX_DIR
NO_TOX_DIR
```

Every environment below is provisioned cold inside the fixed sandbox (the NIX-02 empty edge).

### `tox -e lint`

```
$ tox -e lint
lint: venv> /nix/store/3vpzk25whpm7s8zq5flpk8gbpkggj9np-uv/bin/uv venv -p /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a86b68cdd93e9624b/.venv/bin/python --allow-existing '--prompt=agent-a86b68cdd93e9624b[lint]' --python-preference system /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a86b68cdd93e9624b/.tox/lint
lint: uv-sync> /nix/store/3vpzk25whpm7s8zq5flpk8gbpkggj9np-uv/bin/uv sync --locked --python-preference system --extra dev -p /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a86b68cdd93e9624b/.venv/bin/python
lint: commands[0]> black --check .
All done! ✨ 🍰 ✨
355 files would be left unchanged.
lint: commands[1]> ruff check .
All checks passed!
  lint: OK (0.99=setup[0.16]+cmd[0.82,0.02] seconds)
  congratulations :) (1.14 seconds)
```

`lint: OK`, exit 0. `venv>` names `/nix/store/3vpzk25whpm7s8zq5flpk8gbpkggj9np-uv/bin/uv` — the `New shim paths` table's `uv` entry.

### `tox -e type`

```
$ tox -e type
type: venv> /nix/store/3vpzk25whpm7s8zq5flpk8gbpkggj9np-uv/bin/uv venv -p /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a86b68cdd93e9624b/.venv/bin/python --allow-existing '--prompt=agent-a86b68cdd93e9624b[type]' --python-preference system /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a86b68cdd93e9624b/.tox/type
type: uv-sync> /nix/store/3vpzk25whpm7s8zq5flpk8gbpkggj9np-uv/bin/uv sync --locked --python-preference system --extra dev -p /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a86b68cdd93e9624b/.venv/bin/python
type: commands[0]> mypy typsphinx/
Success: no issues found in 9 source files
  type: OK (1.80=setup[0.15]+cmd[1.65] seconds)
  congratulations :) (1.95 seconds)
```

`type: OK`, exit 0. Same new `uv` shim path.

### `tox -e py312`

```
$ tox -e py312
py312: venv> /nix/store/3vpzk25whpm7s8zq5flpk8gbpkggj9np-uv/bin/uv venv -p cpython3.12 --allow-existing '--prompt=agent-a86b68cdd93e9624b[py312]' --python-preference system /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a86b68cdd93e9624b/.tox/py312
py312: uv-sync> /nix/store/3vpzk25whpm7s8zq5flpk8gbpkggj9np-uv/bin/uv sync --locked --python-preference system --extra dev -p cpython3.12
py312: commands[0]> pytest tests/
============================= test session starts ==============================
platform linux -- Python 3.12.13, pytest-9.1.1, pluggy-1.6.0 -- .../.tox/py312/bin/python3
...
================= 1543 passed, 5 skipped in 109.23s (0:01:49) ==================
  py312: OK (109.92=setup[0.15]+cmd[109.77] seconds)
  congratulations :) (110.07 seconds)

$ cat .tox/py312/pyvenv.cfg
home = /home/yuta/.local/share/uv/python/cpython-3.12-linux-x86_64-gnu/bin
implementation = CPython
uv = 0.11.25
version_info = 3.12
include-system-site-packages = false
prompt = agent-a86b68cdd93e9624b[py312]
```

`py312: OK`, exit 0. Pytest header names `Python 3.12.13`, summary `1543 passed, 5 skipped`. `venv>` names the same new `uv` shim path.

### `tox -e py313`

```
$ tox -e py313
py313: venv> /nix/store/3vpzk25whpm7s8zq5flpk8gbpkggj9np-uv/bin/uv venv -p cpython3.13 --allow-existing '--prompt=agent-a86b68cdd93e9624b[py313]' --python-preference system /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a86b68cdd93e9624b/.tox/py313
py313: uv-sync> /nix/store/3vpzk25whpm7s8zq5flpk8gbpkggj9np-uv/bin/uv sync --locked --python-preference system --extra dev -p cpython3.13
py313: commands[0]> pytest tests/
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- .../.tox/py313/bin/python3
...
================= 1543 passed, 5 skipped in 123.16s (0:02:03) ==================
  py313: OK (123.94=setup[0.15]+cmd[123.79] seconds)
  congratulations :) (124.10 seconds)

$ cat .tox/py313/pyvenv.cfg
home = /nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin
implementation = CPython
uv = 0.11.25
version_info = 3.13.13
include-system-site-packages = false
prompt = agent-a86b68cdd93e9624b[py313]
```

`py313: OK`, exit 0, `1543 passed, 5 skipped`. Same new `uv` shim path. All four NIX-02 environments (`lint`, `type`, `py312`, `py313`) ran in the stated fixed order, each in its own invocation, each ending with its own `<env>: OK` and `congratulations :)` line — the NIX-02 adjacency edge (no result inferred from another environment's `.tox` state) and the ordering edge (each self-contained via `extras = dev`, `uv-venv-lock-runner`) both hold.

## NIX-03 — `cov`, `docs-html`, `docs-pdf`, real PDF

### `tox -e cov`

```
$ tox -e cov
cov: venv> /nix/store/3vpzk25whpm7s8zq5flpk8gbpkggj9np-uv/bin/uv venv ...
cov: commands[0]> pytest --cov=typsphinx --cov-report=term-missing --cov-report=html tests/
============================= test session starts ==============================
platform linux -- Python 3.14.4, pytest-9.1.1, pluggy-1.6.0 -- .../.tox/cov/bin/python3
...
--------------------------------------------------------------
TOTAL                             2806    333    88%
Coverage HTML written to dir htmlcov
================= 1543 passed, 5 skipped in 112.33s (0:01:52) ==================
  cov: OK (113.26=setup[0.15]+cmd[113.11] seconds)
  congratulations :) (113.41 seconds)
```

`TOTAL` line present (`2806 333 88%`), `1543 passed, 5 skipped`, `cov: OK`.

### `tox -e docs-html` (clean build)

The `rm -rf docs/_build` belongs to each build command, not to a preamble, because the two builds share `docs/_build` (the NIX-03 adjacency edge).

```
$ rm -rf docs/_build && tox -e docs-html
docs-html: venv> /nix/store/3vpzk25whpm7s8zq5flpk8gbpkggj9np-uv/bin/uv venv ...
docs-html: commands[0] .../docs> sphinx-build -b html source _build/html
Sphinx v9.1.0 を実行中
...
出力中...[100%] user_guide/templates
索引を生成中... genindex py-modindex 完了
...
build succeeded, 3 warnings.
HTMLページは_build/htmlにあります。
  docs-html: OK (3.50=setup[0.11]+cmd[3.39] seconds)
  congratulations :) (3.65 seconds)
```

`build succeeded, 3 warnings.` — matches the baseline of 3 exactly. `docs-html: OK`, exit 0.

### `tox -e docs-pdf` (clean build)

```
$ rm -rf docs/_build && tox -e docs-pdf
docs-pdf: venv> /nix/store/3vpzk25whpm7s8zq5flpk8gbpkggj9np-uv/bin/uv venv ...
docs-pdf: commands[0] .../docs> sphinx-build -b typstpdf source _build/pdf
Sphinx v9.1.0 を実行中
...
typst: wrote 1 wrapper file(s) -- compile these: typsphinx.typ
Compiling 1 master document(s) to PDF...
Generated PDF: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a86b68cdd93e9624b/docs/_build/pdf/typsphinx.pdf
build succeeded, 5 warnings.
  docs-pdf: OK (3.88=setup[0.14]+cmd[3.75] seconds)
  congratulations :) (4.04 seconds)
```

`Generated PDF:` line present, `build succeeded, 5 warnings.` — matches the baseline of 5 exactly. `docs-pdf: OK`, exit 0.

```
$ test -s docs/_build/pdf/typsphinx.pdf && echo NON_EMPTY
NON_EMPTY
$ head -c 4 docs/_build/pdf/typsphinx.pdf
%PDF
$ stat -c %s docs/_build/pdf/typsphinx.pdf
2776960
```

`docs/_build/pdf/typsphinx.pdf` is non-empty, its first four bytes are `%PDF`, and its size is **2776960 bytes**.

**D-07 `@preview` cache count, before and after `docs-pdf`:**

```
$ ls "$HOME/.cache/typst/packages/preview" | wc -l   # before docs-html/docs-pdf
9
$ ls "$HOME/.cache/typst/packages/preview" | wc -l   # after docs-pdf
9
```

Unchanged at 9 — the warm cache served every `@preview` import; `docs-pdf` did not need to reach the network from inside the sandbox, and no failing transcript occurred.

Neither warning count (3 for `docs-html`, 5 for `docs-pdf`) differs from the carried-in baseline, so no attribution section is needed for either build.

## Genuine residual audit

Task 1's audit script (64-LIBZ-FIX-EVIDENCE.md § BEFORE residual audit), reproduced verbatim into the session scratchpad (`/tmp/claude-1000/-home-yuta-Documents-typsphinx/09a4c0d3-1961-4e01-834d-b0945b94cf40/scratchpad/64-06/residual-audit.sh`, never a tracked file — D-05), run through this session's fixed rootfs over every environment this plan actually provisioned:

```
$ FHS=/nix/store/99fm4lqkp4kab20d3blfbwajnprmlbfx-typsphinx-fhs-run/bin/typsphinx-fhs-run
$ "$FHS" /bin/sh residual-audit.sh \
    "$(pwd)/.venv" \
    "$(pwd)/.tox/cov" \
    "$(pwd)/.tox/docs-html" \
    "$(pwd)/.tox/docs-pdf" \
    "$(pwd)/.tox/lint" \
    "$(pwd)/.tox/py312" \
    "$(pwd)/.tox/py313" \
    "$(pwd)/.tox/type" \
    "/home/yuta/.local/share/uv/python/cpython-3.14.4-linux-x86_64-gnu" \
    "/home/yuta/.local/share/uv/python/cpython-3.12.13-linux-x86_64-gnu" \
    "/nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13"

UNRESOLVED /home/yuta/.local/share/uv/python/cpython-3.14.4-linux-x86_64-gnu/lib/python3.14/lib-dynload/_tkinter.cpython-314-x86_64-linux-gnu.so :: libtcl9.0.so => not found;libtcl9tk9.0.so => not found;
UNRESOLVED /home/yuta/.local/share/uv/python/cpython-3.12.13-linux-x86_64-gnu/lib/python3.12/lib-dynload/_crypt.cpython-312-x86_64-linux-gnu.so :: libcrypt.so.1 => not found;
UNRESOLVED /home/yuta/.local/share/uv/python/cpython-3.12.13-linux-x86_64-gnu/lib/python3.12/lib-dynload/_tkinter.cpython-312-x86_64-linux-gnu.so :: libtcl9.0.so => not found;libtcl9tk9.0.so => not found;
scanned=1974
```

```
GENUINE = {libcrypt.so.1, libtcl9.0.so, libtcl9tk9.0.so}
```

`libz.so.1` does not appear. `scanned=1974` — identical count to 64-05's BEFORE/AFTER audit (same object universe: the roots this plan provisioned are the same shape as the roots 64-05 provisioned in its own fresh worktree).

Every soname in `GENUINE` cites its row and verdict in `64-LIBZ-FIX-EVIDENCE.md` § Residual verdicts, unchanged by this plan:

| Soname | Verdict (cited from 64-LIBZ-FIX-EVIDENCE.md § Residual verdicts) |
|--------|--------------------------------------------------------------------|
| `libcrypt.so.1` | UNREACHED — zero import-search hits, no failing gate (`_crypt` / stdlib `crypt`, cp3.12 only) |
| `libtcl9.0.so` | UNREACHED in practice, FORCED by the letter of the hit rule — every hit is a mypy typeshed stub, Pillow's optional `ImageTk`, or `tox-uv-bare`'s `python_discovery`; no step-3 gate failed or named it |
| `libtcl9tk9.0.so` | Same as `libtcl9.0.so` — identical hit set, same two `_tkinter` objects |

No new soname appears that is not already covered by 64-05's table, so no new row is added. No `flake.nix` edit is made in this plan.

## NIX-05 — procedure summary

This fresh nested worktree (`/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a86b68cdd93e9624b`) ran the session check and the D-09 head check first — confirming the relaunched session's rootfs carries `/usr/lib/libz.so.1` and matches the `New fhs-run:` line, with `.venv`/`.tox` absent and all seven `command -v` paths equal to 64-05's `New shim paths` table, reached by pure session-PATH inheritance with no per-worktree `direnv allow` — then provisioned with the one documented line `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` (D-04), with no interpreter pin. Every gate then ran in the genuine D-09 shape: NIX-01's `ruff --version`/`ruff check .`, the tracer's `PIL._imaging` import and the 64-02 failing node, the NIX-04 full suite (one run, `1543 passed, 5 skipped`, no locale variable), and all seven NIX-02/NIX-03 tox environments cold, ending with `docs-pdf` producing a real, non-empty `%PDF`-prefixed PDF. No manual symlink and no ELF-patching step appeared anywhere, and every tool target (`ruff`'s exec xtrace, `typsphinx.__file__`, every `venv>` line) resolved inside this worktree, never the main checkout.

**No-dispatch note.**

```
$ grep -rliE 'nix|flake' .github/workflows/
$ echo "exit: $?"
exit: 1
```

No workflow file under `.github/workflows/` references `nix` or `flake`. CI never evaluates `flake.nix`, so no push and no CI dispatch belong to this plan.

## Requirement closure

| Requirement | Verdict | Deciding section |
|---|---|---|
| NIX-01 | MET | § NIX-01 — ruff (regression) |
| NIX-02 | MET | § NIX-02 — four tox environments, cold in the fixed sandbox |
| NIX-03 | MET | § NIX-03 — `cov`, `docs-html`, `docs-pdf`, real PDF |
| NIX-04 | MET | § NIX-04 — full suite (one run, maintainer locale) |
| NIX-05 | MET | § NIX-05 — procedure summary |
