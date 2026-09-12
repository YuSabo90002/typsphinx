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
<!-- gsd:write-continue -->
