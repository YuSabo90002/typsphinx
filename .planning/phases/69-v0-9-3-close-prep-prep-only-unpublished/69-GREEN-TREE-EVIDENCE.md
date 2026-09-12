# Phase 69 — Local Green-Tree Evidence (SC#3, local half)

## Head check and provisioning

```
$ date -u +%FT%TZ
2026-09-12T22:47:17Z

$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a69047240a759c44b

$ test -f .git; echo "exit:$?"
exit:0

$ grep -c typsphinx-fhs-run "$(command -v uv)"
2
```

Provisioning:

```
$ env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs
...
 + ruff==0.15.20
 ...
 + tox==4.56.1
 + tox-uv==1.36.0
 + tox-uv-bare==1.36.0
 ...
 + typsphinx==0.9.2 (from file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-a69047240a759c44b)
 + typst==0.15.0
 ...
 + uv==0.12.13
 + virtualenv==21.5.1
```

Both extras synced without error (`myst-parser`, `furo`, `sphinx-autodoc-typehints`, `sphinx-intl` all
present in the resolved set, confirming the docs extra is live).

Before any commit in this plan:

```
$ git rev-parse HEAD
becd70c31bfed573dc10cdc20dcf7a30d57edd57
```

BASE_69_03 = becd70c31bfed573dc10cdc20dcf7a30d57edd57

```
$ git log --oneline -8
becd70c3 docs(phase-69): update tracking after wave 1, mark wave 2 executing
56880eca docs(69-01): move key-line prose off five evidence keys (format only)
435cbbfe chore: merge executor worktree (worktree-agent-ab4c25ec1378d6a2a)
11e8da4d chore: merge executor worktree (worktree-agent-abe1318883a64e327)
ac13a1de docs(69-01): complete CHANGELOG-bullets-and-clean-docs-proof plan
98cbc372 docs(69-02): complete REL-12 fence, SC#1 observation 1 and COVERAGE.md plan
a30fd6f2 feat(69-01): author DEP and NIX changelog bullets, full pure-addition and fence proof
0527f857 docs(69-02): write reasoned no-external-API COVERAGE.md
```

This confirms wave 1 (69-01, 69-02) is merged into this worktree's HEAD before this plan's first
commit.

## Tree identity

```
$ uv run python -c "import typsphinx, sys; print(typsphinx.__version__); print(typsphinx.__file__)"
0.9.2
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a69047240a759c44b/typsphinx/__init__.py
```

TYPSPHINX_FILE = /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a69047240a759c44b/typsphinx/__init__.py

The printed path resolves **inside this worktree**, not the main checkout
(`/home/yuta/Documents/typsphinx/typsphinx`) — this proves the worktree's own editable install is
what every measurement below exercises, not a stale main-checkout copy.

```
$ uv run python -c "import myst_parser; print(myst_parser.__version__)"
5.1.0
```

`myst_parser` imports successfully, proving the docs extra is present in this worktree's venv.

```
$ cat .venv/pyvenv.cfg
home = /home/yuta/.local/share/uv/python/cpython-3.14-linux-x86_64-gnu/bin
implementation = CPython
uv = 0.11.25
version_info = 3.14
include-system-site-packages = false
prompt = typsphinx
```

PYVENV_HOME_69_03 = /home/yuta/.local/share/uv/python/cpython-3.14-linux-x86_64-gnu/bin
PYVENV_VERSION_69_03 = 3.14

```
$ cat /home/yuta/Documents/typsphinx/.venv/pyvenv.cfg   (read-only, main checkout)
home = /nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin
implementation = CPython
uv = 0.11.25
version_info = 3.13.13
include-system-site-packages = false
prompt = typsphinx
```

MAIN_PYVENV_HOME = /nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin
MAIN_PYVENV_VERSION = 3.13.13

**The two interpreters differ**, exactly as CLAUDE.md's "Interpreters may differ" note anticipates:
this worktree's fresh `uv sync` built its `.venv` on uv-managed CPython 3.14, while the main
checkout's `.venv` is on nixpkgs' `python3-3.13.13`. Counts taken in this worktree (below) are
compared only against baselines recorded inside worktrees of this same phase family
(`69-CHANGELOG-EVIDENCE.md`'s own `agent-ab4c25ec1378d6a2a` worktree, also uv-managed CPython 3.14 —
confirmed identical interpreter in that file's own § "Head check and provisioning"), never against
the main checkout's counts, so no comparison in this evidence file crosses an interpreter boundary.

## Product-tree delta and D-06

`PHASE_BASE_SHA` read from `69-CLOSEOUT-GUARD.md`:

```
$ sed -n "s/^PHASE_BASE_SHA = //p" 69-CLOSEOUT-GUARD.md
2db4e803d36d5f7a5db0a92b08cac4988fa88957
```

```
$ git diff --stat 2db4e803d36d5f7a5db0a92b08cac4988fa88957 HEAD -- . ':(exclude).planning'
 CHANGELOG.md | 25 +++++++++++++++++++++++++
 1 file changed, 25 insertions(+)

$ git diff --name-only 2db4e803d36d5f7a5db0a92b08cac4988fa88957 HEAD -- . ':(exclude).planning'
CHANGELOG.md
```

PRODUCT_DELTA = CHANGELOG.md

Exactly one product-tree file changed since the phase base, with 25 insertions and zero deletions —
this is the positive control on the anchor: a non-empty, single-file diff proves `PHASE_BASE_SHA` is
a real ancestor rather than a mistaken pointer at HEAD itself (which would also print an empty diff).
This is the same single file `69-01`'s worktree edited (its own `CHANGELOG.md` diff against the same
base is likewise exactly `CHANGELOG.md`, 25 insertions per `69-CHANGELOG-EVIDENCE.md`'s "Pure-addition
proof" section) — confirming this plan's tree and 69-01's tree carry the identical product-tree
content, so a docs render measured in one worktree applies equally to the other.

```
$ git fetch origin main
From https://github.com/YuSabo90002/typsphinx
 * branch              main       -> FETCH_HEAD

$ git merge-base --is-ancestor origin/main HEAD; echo "exit:$?"
exit:1
```

MAIN_ABSORBED = no

`origin/main` is NOT an ancestor of this worktree's HEAD (exit 1) — D-06's non-absorption
requirement holds: this phase's merged tree has not absorbed `main`, and the SC#3 green measured
below is proven on this phase's own tip, not on a tree that pulled in `main`'s lock or `ruff` 0.16.x.

## Full suite

```
$ uv run pytest --collect-only -q -p no:cacheprovider
...
======================== 1548 tests collected in 1.22s =========================
```

COLLECTED_69_03 = 1548

```
$ uv run pytest -q -rs -p no:cacheprovider
...
=========================== short test summary info ============================
SKIPPED [1] tests/test_corpus_gate.py:530: SC#3 before/after measurement is env-gated -- set TYPSPHINX_CORPUS_REPORT=1 to run it (RESEARCH Open Question 1)
================= 1547 passed, 1 skipped in 116.80s (0:01:56) ==================
```

Run in a single foreground Bash call (well inside the 600000 ms budget; total wall time 116.80s) — no
split was needed.

FULL_SUMMARY = 1547 passed, 1 skipped
FULL_FAILED = 0
FULL_SKIPPED = 1

Every skip accounted for by its printed reason: `tests/test_corpus_gate.py::test_empty_url_before_after`
is deliberately env-gated behind `TYPSPHINX_CORPUS_REPORT=1` (an opt-in before/after measurement,
RESEARCH Open Question 1) — not a failure, not a hidden pass, exactly one skip and it is this one.

`COLLECTED_69_03` (1548) equals `1547 passed + 1 skipped` (1548) from the live run — the collect
count and the executed-plus-skipped count agree.
