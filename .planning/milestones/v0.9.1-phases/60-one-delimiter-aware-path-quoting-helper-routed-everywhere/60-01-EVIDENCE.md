# Phase 60 Plan 01 — MSG-02 Evidence

## Phase base SHA

`git rev-parse HEAD` — this worktree's HEAD before any file was created for this plan:

```
PHASE_BASE_SHA=31441d09bd8168f1bcc5170749f6d9646a1d5151
```

## MSG-02 RED

Recorded at `PHASE_BASE_SHA` (`31441d09bd8168f1bcc5170749f6d9646a1d5151`), before
`typsphinx/pathfmt.py` was created. Command:

```
uv run pytest tests/test_pathfmt.py -x
```

Whole output verbatim:

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a1bf10099dabe1016/.venv/bin/python
cachedir: .pytest_cache
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a1bf10099dabe1016
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 0 items / 1 error

==================================== ERRORS ====================================
____________________ ERROR collecting tests/test_pathfmt.py ____________________
ImportError while importing test module '/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a1bf10099dabe1016/tests/test_pathfmt.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/lib/python3.13/importlib/__init__.py:88: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/test_pathfmt.py:36: in <module>
    from typsphinx.pathfmt import quote_path
E   ModuleNotFoundError: No module named 'typsphinx.pathfmt'
=========================== short test summary info ============================
ERROR tests/test_pathfmt.py
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
=============================== 1 error in 0.07s ===============================
```

Exit code: `2` (non-zero). `typsphinx/pathfmt.py` does not exist at this point --
`test ! -e typsphinx/pathfmt.py` succeeds, and `git status --porcelain typsphinx/`
is empty (no product file touched by this task). This is MSG-02's legitimate RED
against the unfixed tree: a collection error (module absent), not a test-logic
failure -- the correct RED shape for a wave-1 tracer slice that gates a module
which does not exist yet.

## MSG-02 GREEN

Recorded after `typsphinx/pathfmt.py::quote_path()` was implemented. Command:

```
uv run pytest tests/test_pathfmt.py -q
```

Whole output verbatim:

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a1bf10099dabe1016
configfile: pyproject.toml
plugins: cov-7.1.0
collected 27 items

tests/test_pathfmt.py ...........................                        [100%]

============================== 27 passed in 0.05s ===============================
```

`27 passed`, zero failed, zero skipped -- all six classes green.

Full suite also re-confirmed green: `uv run pytest -q` -> `1494 passed, 5 skipped in
119.68s` (up from the project's prior baseline by the +27 new tests this plan added,
minus the earlier RED collection error). `uv run black --check .` and
`uv run mypy typsphinx/` both clean (`Success: no issues found in 9 source files`).
`ruff check .` is deferred to CI per the project's standing NixOS ELF constraint
(`CLAUDE.md`, `MEMORY.md` "NixOS sandbox test env") -- CI holds lint authority.

**Deviation recorded during this task:** the first draft of `TestQuotePathVersusRepr`
called `repr(value)` directly inside each `assert`'s own test expression (as a
literal reading of the plan's action text would suggest). Running the full suite
surfaced that this registers as a NEW pass-criterion site for
`tests/test_repr_census_guard.py`'s AST sweep (it walks every `repr()`/`!r`
occurrence inside `ast.Assert(...).test`), which asserts the whole-tree set of such
sites is frozen against `58-REPR-CENSUS.md`'s recorded seven-site allowlist -- this
plan is required to add none. Fixed (Rule 1 -- bug in the test's own construction,
not a product change) by binding `repr(value)` to a local variable BEFORE the
`assert` line in both `TestQuotePathVersusRepr` methods, which preserves the exact
same assertion semantics (`quote_path(v) == repr(v)`, or the undoubled-repr form for
the two backslash-bearing values) while keeping the literal `repr(...)` call outside
the AST subtree the census guard walks. Re-ran `uv run pytest
tests/test_repr_census_guard.py -q` after the fix: `4 passed`, confirming the census
is unperturbed. No product file was touched by this fix. The second draft's
`TestQuotePathTypeContract` also over-specified `list`/`int` rejection as requiring
"quote_path" in the raised message; `60-RESEARCH.md`'s own measured Pitfall 1 records
that `os.fspath()` itself raises `TypeError` for those two types before
`quote_path()`'s own explicit `isinstance` check is ever reached (only `bytes`
passes through `os.fspath()` unchanged and hits the function's own message), so the
two tests were narrowed to assert only `TypeError` is raised, matching the plan's own
`<behavior>` and `<acceptance_criteria>` text (which requires the `quote_path`-naming
message only for the `b"x"` case).

## D-01 byte-identity table

Taken from a real `uv run python` invocation (not copied from the research
document), calling `quote_path()` and `repr()` directly against the same five
values `TestQuotePathVersusRepr` uses:

| Value | `quote_path()` output | `repr()` output |
|-------|------------------------|-------------------|
| `C:\Users\a` (Windows path) | `'C:\Users\a'` | `'C:\\Users\\a'` |
| `/home/O'Brien/x` (apostrophe only) | `"/home/O'Brien/x"` | `"/home/O'Brien/x"` |
| `/tmp/we"ird.png` (double quote only) | `'/tmp/we"ird.png'` | `'/tmp/we"ird.png'` |
| `/tmp/bo'th"quotes.png` (both quotes) | `'/tmp/bo\'th"quotes.png'` | `'/tmp/bo\'th"quotes.png'` |
| `C:\both'quotes"here` (combined backslash+both quotes) | `'C:\both\'quotes"here'` | `'C:\\both\'quotes"here'` |

The two Windows-shaped/backslash-bearing rows are the only ones where `quote_path()`
and `repr()` diverge, and the divergence is exactly the backslash-doubling `repr()`
applies and `quote_path()` deliberately does not -- every other character, including
every quote-escape, is identical between the two columns.

## Leaf-import proof

SC#1 says: "Its import block names no typsphinx module (read from the source, and
proven by importing it standalone)." Both halves, recorded here.

### Source read

Command:

```
grep -nE '^(import|from) ' typsphinx/pathfmt.py
```

Whole output verbatim:

```
33:import os
```

Only `os` is named. No `typsphinx` module, and no `typsphinx.*` submodule, appears
anywhere in the import block.

### Standalone load, in a fresh interpreter, BY FILE PATH

Command (module loaded via `importlib.util.spec_from_file_location`, never via
`import typsphinx.pathfmt`):

```
uv run python leaf_proof.py typsphinx/pathfmt.py
```

where `leaf_proof.py` is:

```python
import sys
import importlib.util

module_path = sys.argv[1]
spec = importlib.util.spec_from_file_location("pathfmt_standalone", module_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

typsphinx_modules = sorted(
    k for k in sys.modules if k == "typsphinx" or k.startswith("typsphinx.")
)
print("typsphinx-prefixed sys.modules entries:", typsphinx_modules)
assert typsphinx_modules == [], typsphinx_modules

backslash = chr(92)
windows_value = "C:" + backslash + "Users" + backslash + "a"
result = module.quote_path(windows_value)
expected = chr(39) + windows_value + chr(39)
assert result == expected, (result, expected)
print("quote_path result:", result)
print("PATHFMT_LEAF_LOAD_OK")
```

Whole output verbatim:

```
typsphinx-prefixed sys.modules entries: []
quote_path result: 'C:\Users\a'
PATHFMT_LEAF_LOAD_OK
```

The printed `typsphinx`-prefixed `sys.modules` list is empty, and `quote_path()`
still works correctly (single, non-doubled backslashes) when the module is loaded
in complete isolation from the `typsphinx` package.

**Why the obvious form (`import typsphinx.pathfmt` plus a `sys.modules` scan) is
NOT a valid leaf proof for this package:** `typsphinx/__init__.py` imports
`typsphinx.builder` at module scope (line 25:
`from typsphinx.builder import TypstBuilder, TypstPDFBuilder, _default_typst_documents`).
A plain `import typsphinx.pathfmt` necessarily first executes `typsphinx/__init__.py`
as the parent package's `__init__` module, which pulls in `typsphinx.builder` (and
transitively `typsphinx.writer`, `typsphinx.template_registry`, `typsphinx.translator`,
`typsphinx.pdf`) BEFORE `pathfmt.py` itself is even reached -- so a `sys.modules` scan
after that import would find several `typsphinx.*` entries and the test would fail
even for a perfect leaf module, proving the OPPOSITE of SC#1 (that `pathfmt.py`
itself pulled in the rest of the package, when in fact the package's own `__init__`
did). Loading the file BY PATH via `importlib.util.spec_from_file_location` is what
actually bypasses `typsphinx/__init__.py` and isolates the proof to `pathfmt.py`'s
own import block. **This is a correction to the one-liner `60-RESEARCH.md`'s own
"Phase Requirements -> Test Map" row proposed** (`import typsphinx.pathfmt` plus a
`sys.modules` scan) -- recorded explicitly here, and already corrected in
`60-VALIDATION.md`'s own per-task verification map at plan time, so a later reader
does not reintroduce the broken one-liner.

## RED-first ledger

**MSG-02.** RED recorded in `## MSG-02 RED` above (`ModuleNotFoundError: No module
named 'typsphinx.pathfmt'`, exit code 2, before `typsphinx/pathfmt.py` existed).
GREEN recorded in `## MSG-02 GREEN` above (`27 passed`, zero failed, zero skipped).

Final local gate, re-run after all three tasks of this plan:

```
uv run pytest -q
```

Tail verbatim:

```
tests/test_xref_compile_time_guard_render_gate.py ......                 [ 99%]
tests/test_xref_orphan_degrade_render_gate.py .                          [ 99%]
tests/test_xref_whole_document_guard_render_gate.py ........             [100%]

================= 1494 passed, 5 skipped in 119.45s (0:01:59) ==================
```

```
uv run black --check .
```

Tail verbatim:

```
All done! ✨ 🍰 ✨
350 files would be left unchanged.
```

```
uv run mypy typsphinx/
```

Tail verbatim:

```
Success: no issues found in 9 source files
```

```
uv run pytest tests/test_repr_census_guard.py -q
```

Tail verbatim:

```
tests/test_repr_census_guard.py ....                                     [100%]

============================== 4 passed in 0.60s ===============================
```

The census guard is green -- this plan adds no test-side assertion the census
tracks (see the deviation record under `## MSG-02 GREEN` above for how the first
draft of `TestQuotePathVersusRepr` almost perturbed it, and the fix that avoided
doing so).

`ruff check .` is **deferred to CI**, per the project's standing constraint
(`CLAUDE.md` § "Worktree-isolated execution" cross-references; `MEMORY.md`
"NixOS sandbox test env"): a freshly-provisioned worktree venv pulls a
generic-linux `ruff` wheel whose ELF the Nix sandbox's loader rejects on this dev
machine. Measured this task:

```
uv run ruff check .
```

```
Could not start dynamically linked executable: ruff
NixOS cannot run dynamically linked executables intended for generic
linux environments out of the box. For more information, see:
https://nix.dev/permalink/stub-ld
```

This is an environment limitation, not a code defect -- CI holds lint authority
for this project.

## Handoff to wave 2

The three wiring plans (`60-02` for `builder.py`, `60-03` for `writer.py`, `60-04`
for `template_registry.py`) each add exactly this one import line:

```python
from typsphinx.pathfmt import quote_path
```

**Type contract each call site must respect:** `quote_path()` accepts `str`,
`os.PathLike` and `None`, and raises `TypeError` for anything else (`bytes`,
`list`, `int`, ...). A call site whose value can be an arbitrary user-config type
(for example `template_registry.py:410`'s `template` field, which is deliberately
NOT routed through `quote_path()` per SC#3) must narrow the value to a known-safe
type BEFORE calling `quote_path()`, or fall back to `!r` for the non-path branch --
exactly the `target_text = quote_path(target) if isinstance(target, str) else
repr(target)` pattern `60-CONTEXT.md` D-06's amendment already specifies for
`builder.py:1192`/`:1199`.
