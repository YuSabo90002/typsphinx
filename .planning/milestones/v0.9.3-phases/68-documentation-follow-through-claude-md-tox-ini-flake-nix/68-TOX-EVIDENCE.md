Measured shape: executor worktree `agent-ae9aed511800dac5e`, direnv-loaded FHS shim inherited from
the session PATH; no `nix develop`, no `direnv exec`, never the main checkout.

## Head check and provisioning

```
$ date -u +%FT%TZ
2026-09-12T15:47:56Z

$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-ae9aed511800dac5e

$ test -f .git; echo "exit:$?"
exit:0

$ command -v uv
/nix/store/3vpzk25whpm7s8zq5flpk8gbpkggj9np-uv/bin/uv

$ grep -c typsphinx-fhs-run "$(command -v uv)"
2

$ env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev
(tail)
 + tox==4.56.1
 + tox-uv==1.36.0
 + tox-uv-bare==1.36.0
 + typsphinx==0.9.2 (from file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-ae9aed511800dac5e)
 + typst==0.15.0
 + uv==0.12.13
```

BASE_68_02 = 0bd33617d3cdf96f0342bdaeb19a0cb031f7c10a

```
$ git merge-base HEAD gsd/v0.9.3-toolchain-and-dependency-update-repair
0bd33617d3cdf96f0342bdaeb19a0cb031f7c10a

$ git rev-parse HEAD
0bd33617d3cdf96f0342bdaeb19a0cb031f7c10a
```

The measured merge-base equals `git rev-parse HEAD` before any commit in this plan: the worktree
forked cleanly from the wave-1 dispatch point.

## Baseline

```
$ sed -n 's/^home = //p;s/^version_info = //p' .venv/pyvenv.cfg
/home/yuta/.local/share/uv/python/cpython-3.14-linux-x86_64-gnu/bin
3.14
```

PYVENV_HOME_68_02 = /home/yuta/.local/share/uv/python/cpython-3.14-linux-x86_64-gnu/bin
PYVENV_VERSION_68_02 = 3.14

```
$ uv run pytest --collect-only -q -p no:cacheprovider
...
======================== 1548 tests collected in 1.23s =========================
```

COLLECT_BEFORE_68_02 = 1548

```
$ uv run pytest tests/test_toolchain_config_gate.py tests/test_pdf_render_gate.py -q -p no:cacheprovider
tests/test_toolchain_config_gate.py ....                                 [ 11%]
tests/test_pdf_render_gate.py ...............................            [100%]

============================== 35 passed in 6.17s ==============================
```

TWO_FILE_RESULT_BEFORE = 35 passed

No `failed` and no `error` in that result — the baseline is green.

```
$ uv run tox config -e py312 --core -k requires
[testenv:py312]

[tox]
requires =
  tox-uv~=1.35
  tox
```

```
$ sed -n '1,11p' tox.ini
[tox]
env_list = py312, py313, lint, type, cov, docs
isolated_build = True
# tox-uv-bare pinned via ~= (not >=1.35,<2): tox's own ini-list loader splits
# single-line `requires` values on "," (only multi-*entry* lists preserve
# newline-splitting), so a literal ">=1.35,<2" is parsed as two bogus
# requirements ("tox-uv-bare>=1.35" and "<2") and tox fails to even start.
# ~=1.35 is the packaging-spec equivalent of >=1.35,<2 (see D-07) with no
# comma, sidestepping the parser bug. Verified equivalent via
# `packaging.specifiers.SpecifierSet` in 04-01-SUMMARY.md.
requires = tox-uv~=1.35
```

## SpecifierSet equivalence

```
$ uv run python -c "
from packaging.specifiers import SpecifierSet
a = SpecifierSet('~=1.35')
b = SpecifierSet('>=1.35,<2')
versions = ['1.34.9','1.35','1.35.0','1.35.1','1.36.0','1.99.99','2.0','2.0.0','2.1','1.35.0rc1','2.0.0a1']
all_agree = True
for v in versions:
    ia = a.contains(v, prereleases=True)
    ib = b.contains(v, prereleases=True)
    if ia != ib:
        all_agree = False
    print(v, ia, ib)
print(all_agree)
"
1.34.9 False False
1.35 True True
1.35.0 True True
1.35.1 True True
1.36.0 True True
1.99.99 True True
2.0 False False
2.0.0 False False
2.1 False False
1.35.0rc1 False False
2.0.0a1 False False
True
```

SPECIFIER_EQUIV = True

Every one of the eleven sampled versions agrees between `~=1.35` and `>=1.35,<2` — the equivalence
the old comment cited in a now-nonexistent SUMMARY file is re-measured here and holds.

## tox.ini rewrite

```
$ sed -n '1,/^requires = /p' tox.ini
[tox]
env_list = py312, py313, lint, type, cov, docs
isolated_build = True
# requires pins `tox-uv~=1.35`. tox's own ini-list loader splits a
# single-line `requires` value on "," (only multi-*entry* lists preserve
# newline-splitting), so a literal ">=1.35,<2" would be parsed as two bogus
# requirements (`tox-uv>=1.35` and `<2`) and tox would fail to even start;
# `~=1.35` admits the same versions as `>=1.35,<2` with no comma,
# sidestepping the parser bug.
# `tox-uv` is safe again: on NixOS, `flake.nix`'s FHS shims run `tox` inside
# a sandbox that provides what its bundled `uv` needs to exec, so that
# bundled `uv` now executes correctly; CI runners were never affected
# either way. The pin was briefly `tox-uv-bare` because outside FHS that
# bundled `uv` could not exec on NixOS.
# See v0.9.3 Phase 65, `65-REVERT-EVIDENCE.md` for the revert, and v0.9.3
# Phase 68, `68-TOX-EVIDENCE.md` for this equivalence, re-measured here.
requires = tox-uv~=1.35
```

```
$ git diff -U0 "$BASE_68_02" -- tox.ini
--- a/tox.ini
+++ b/tox.ini
@@ -4,7 +4,13 @@ isolated_build = True
-# tox-uv-bare pinned via ~= (not >=1.35,<2): tox's own ini-list loader splits
-# single-line `requires` values on "," (only multi-*entry* lists preserve
-# newline-splitting), so a literal ">=1.35,<2" is parsed as two bogus
-# requirements ("tox-uv-bare>=1.35" and "<2") and tox fails to even start.
-# ~=1.35 is the packaging-spec equivalent of >=1.35,<2 (see D-07) with no
-# comma, sidestepping the parser bug. Verified equivalent via
-# `packaging.specifiers.SpecifierSet` in 04-01-SUMMARY.md.
+# requires pins `tox-uv~=1.35`. tox's own ini-list loader splits a
+# single-line `requires` value on "," (only multi-*entry* lists preserve
+# newline-splitting), so a literal ">=1.35,<2" would be parsed as two bogus
+# requirements (`tox-uv>=1.35` and `<2`) and tox would fail to even start;
+# `~=1.35` admits the same versions as `>=1.35,<2` with no comma,
+# sidestepping the parser bug.
+# `tox-uv` is safe again: on NixOS, `flake.nix`'s FHS shims run `tox` inside
+# a sandbox that provides what its bundled `uv` needs to exec, so that
+# bundled `uv` now executes correctly; CI runners were never affected
+# either way. The pin was briefly `tox-uv-bare` because outside FHS that
+# bundled `uv` could not exec on NixOS.
+# See v0.9.3 Phase 65, `65-REVERT-EVIDENCE.md` for the revert, and v0.9.3
+# Phase 68, `68-TOX-EVIDENCE.md` for this equivalence, re-measured here.
```

Removed lines are only old 4-10, and every added line starts with `#`.

```
$ uv run tox config -e py312 --core -k requires
[testenv:py312]

[tox]
requires =
  tox-uv~=1.35
  tox
```

Still prints `tox-uv~=1.35`, no `tox-uv-bare`.

```
$ sed -n '/^requires = /,$p' tox.ini | sha256sum
3a6ca33ed2152dd7fee230eb55a4fb2df256ea200c63c4893d4d6864418eabfc  -

$ git show "$BASE_68_02:tox.ini" | sed -n '/^requires = /,$p' | sha256sum
3a6ca33ed2152dd7fee230eb55a4fb2df256ea200c63c4893d4d6864418eabfc  -
```

Equal — everything from `requires =` onward, including the `package = editable` block, is
byte-identical to base.

```
$ sed -n '1,3p' tox.ini | sha256sum
3f5fd8ebe2be9a54d0e515b163a4b9219c2b4f23ea9aa54e0a66b803b3245167  -

$ git show "$BASE_68_02:tox.ini" | sed -n '1,3p' | sha256sum
3f5fd8ebe2be9a54d0e515b163a4b9219c2b4f23ea9aa54e0a66b803b3245167  -
```

Equal — lines 1-3 unchanged.

## test_toolchain_config_gate.py strings

```
$ git diff -U0 "$BASE_68_02" -- tests/test_toolchain_config_gate.py
--- a/tests/test_toolchain_config_gate.py
+++ b/tests/test_toolchain_config_gate.py
@@ -302,3 +302,4 @@ def test_dev_extra_pins_tox_uv_not_tox_uv_bare():
-    CLAUDE.md's own "Conventions & gotchas" sentence still names `tox-uv-bare` as
-    deliberate — that sentence goes stale as of this revert and is rewritten in
-    Phase 68 (DOC-19/DOC-20), not here (D-06).
+    CLAUDE.md's own "Conventions & gotchas" sentence named `tox-uv-bare` as
+    deliberate when Phase 65's revert landed. Phase 65 left that rewrite for
+    Phase 68; Phase 68 (DOC-19/DOC-20) rewrote it to describe the
+    `tox-uv~=1.35` pin, keeping `tox-uv-bare` only as history.
@@ -367,2 +368,2 @@ def test_dev_extra_pins_tox_uv_not_tox_uv_bare():
-        "(TOX-01, D-04) and CLAUDE.md 'Conventions & gotchas', which still names "
-        "tox-uv-bare as deliberate until Phase 68 (DOC-19/DOC-20) rewrites it."
+        "(TOX-01, D-04). CLAUDE.md 'Conventions & gotchas' was rewritten in "
+        "Phase 68 (DOC-19/DOC-20) to describe the tox-uv pin."
```

Removed lines are only base 302-304 and 367-368 (the assertion-message tail sits two lines
earlier than the plan's approximate 366-368 census, confirmed by direct measurement); base
lines 1-301 are untouched.

```
$ masked AST hash (docstrings + assert messages masked), current tree
ba5710611d00849ec86999bb79862e7cac91c34a209403a5cc799b0a706257d7

$ masked AST hash, git show BASE_68_02:tests/test_toolchain_config_gate.py
ba5710611d00849ec86999bb79862e7cac91c34a209403a5cc799b0a706257d7
```

Equal — no compared name, expression or statement changed.

```
$ whitespace-normalised string constants of test_dev_extra_pins_tox_uv_not_tox_uv_bare
... CLAUDE.md's own "Conventions & gotchas" sentence named `tox-uv-bare` as
deliberate when Phase 65's revert landed. Phase 65 left that rewrite for
Phase 68; Phase 68 (DOC-19/DOC-20) rewrote it to describe the
`tox-uv~=1.35` pin, keeping `tox-uv-bare` only as history. ...
... (TOX-01, D-04). CLAUDE.md 'Conventions & gotchas' was rewritten in
Phase 68 (DOC-19/DOC-20) to describe the tox-uv pin. ...
```

Contains `Phase 68` and `Conventions & gotchas`; contains none of `still names`,
`until Phase 68`, `goes stale`, `###` or `development shell`.

```
$ uv run pytest tests/test_toolchain_config_gate.py tests/test_pdf_render_gate.py -q -p no:cacheprovider
tests/test_toolchain_config_gate.py ....                                 [ 11%]
tests/test_pdf_render_gate.py ...............................            [100%]

============================== 35 passed in 5.56s ==============================
```

Equal to TWO_FILE_RESULT_BEFORE (35 passed).

```
$ uv run black --check tests/test_toolchain_config_gate.py
All done! ✨ 🍰 ✨
1 file would be left unchanged.

$ uv run ruff check tests/test_toolchain_config_gate.py
All checks passed!
```

## test_pdf_render_gate.py sentence

```
$ git diff -U0 "$BASE_68_02" -- tests/test_pdf_render_gate.py
--- a/tests/test_pdf_render_gate.py
+++ b/tests/test_pdf_render_gate.py
@@ -168,4 +168,7 @@ def _run_sphinx_build_typst(
-    the bundled generic-linux `uv` wheel binary). `sys.executable -m sphinx`
-    is kept regardless, because it depends on no PATH resolution at all --
-    a better reason than the hazard ever was, and one that holds no matter
-    what is installed in `.venv/bin`.
+    the bundled generic-linux `uv` wheel binary). The `tox-uv` revert
+    (v0.9.3 Phase 65) put `.venv/bin/uv` back, and on NixOS it now runs
+    through the Phase 64 FHS shims rather than bare, so that hazard does
+    not recur. `sys.executable -m sphinx` is kept regardless, because it
+    depends on no PATH resolution at all -- a better reason than the
+    hazard ever was, and one that holds no matter what is installed in
+    `.venv/bin`.
```

Removed lines are base 168-171, a subset of the plan's approximate 166-171 census; base
lines 1-165 hash identically to base (`06733d0b...`, both sides).

```
$ masked AST hash, tests/test_pdf_render_gate.py — current tree
2a839bd0be69d09fdb70c12688cf7eecce96e6a0bccef0a8ce45b3c8b710e31e

$ masked AST hash, git show BASE_68_02:tests/test_pdf_render_gate.py
2a839bd0be69d09fdb70c12688cf7eecce96e6a0bccef0a8ce45b3c8b710e31e

$ masked AST hash, tests/test_toolchain_config_gate.py — current tree
ba5710611d00849ec86999bb79862e7cac91c34a209403a5cc799b0a706257d7

$ masked AST hash, git show BASE_68_02:tests/test_toolchain_config_gate.py
ba5710611d00849ec86999bb79862e7cac91c34a209403a5cc799b0a706257d7
```

Both files' masked AST hashes equal base — no assertion logic changed anywhere.

```
$ docstring order check (QUA-04 sentence, then the added sentence, then "is kept regardless")
a= 808 z= 1100
m=  The `tox-uv` revert (v0.9.3 Phase 65) put `.venv/bin/uv` back, and on
    NixOS it now runs through the Phase 64 FHS shims rather than bare, so
    that hazard does not recur.
exit:0
```

The inserted text sits strictly between the QUA-04 sentence and the closing "is kept
regardless" sentence, and contains `FHS`, `.venv/bin/uv` and `revert`.

```
$ uv run black --check tests/test_toolchain_config_gate.py tests/test_pdf_render_gate.py
All done! ✨ 🍰 ✨
2 files would be left unchanged.

$ uv run ruff check tests/test_toolchain_config_gate.py tests/test_pdf_render_gate.py
All checks passed!
```

## Gates after the edits

```
$ uv run pytest tests/test_toolchain_config_gate.py tests/test_pdf_render_gate.py -q -p no:cacheprovider
tests/test_toolchain_config_gate.py ....                                 [ 11%]
tests/test_pdf_render_gate.py ...............................            [100%]

============================== 35 passed in 5.74s ==============================
```

TWO_FILE_RESULT_AFTER = 35 passed

Equal to TWO_FILE_RESULT_BEFORE.

```
$ uv run pytest --collect-only -q -p no:cacheprovider
...
======================== 1548 tests collected in 0.26s =========================
```

COLLECT_AFTER_68_02 = 1548

Equal to COLLECT_BEFORE_68_02.

**Note on the Task 3 `<verify><automated>` collect-count extraction:** the literal
`sed -n 's/^\([0-9][0-9]*\) tests\{0,1\} collected.*/\1/p'` pattern anchors at the start
of the line, but this pytest version pads the summary line with `=` to the fallback
80-column terminal width even when stdout is not a tty (`======================== 1548
tests collected in 0.26s =========================`), so the literal pattern never
matches in this worktree. Confirmed the substantive claim directly instead:
`grep -oE '[0-9]+ tests? collected' | grep -oE '^[0-9]+'` and a `sed 's/^=* //;s/
=*$//'` pre-strip both extract `1548` before and after the edit, matching
`COLLECT_BEFORE_68_02`. This is a pre-existing quirk in the plan's own verify text
against this environment's pytest output format, not a defect this plan's edits
introduced.

```
$ git diff --name-only "$BASE_68_02"
.planning/phases/68-documentation-follow-through-claude-md-tox-ini-flake-nix/68-TOX-EVIDENCE.md
tests/test_pdf_render_gate.py
tests/test_toolchain_config_gate.py
tox.ini
```

Only `tox.ini`, the two test files and this evidence file changed (the `68-02-SUMMARY.md`
this plan also produces is written after this gate).

```
$ uv run tox config -e py312 --core -k requires
[testenv:py312]

[tox]
requires =
  tox-uv~=1.35
  tox
```

Still `tox-uv~=1.35`, no `tox-uv-bare`, unchanged from Task 1.
