# Deferred Items — Phase 45.1, Plan 01

Out-of-scope discoveries logged per the executor's SCOPE BOUNDARY rule (only
auto-fix issues directly caused by the current task's changes; pre-existing
failures in unrelated files are logged here, not fixed).

## Pre-existing NixOS sandbox failures (45 tests, unrelated to D-B/D-D)

`uv run pytest -q` over the whole suite reports 45 failures, all in five test
files this plan does not touch (confirmed via `git diff --stat HEAD --
tests/test_examples_basic.py tests/test_integration_advanced.py
tests/test_integration_basic.py tests/test_integration_multi_doc.py
tests/test_integration_nested_toctree.py` -- zero diff):

- `tests/test_examples_basic.py` (3 failures)
- `tests/test_integration_advanced.py` (12 failures)
- `tests/test_integration_basic.py` (11 failures)
- `tests/test_integration_multi_doc.py` (8 failures)
- `tests/test_integration_nested_toctree.py` (11 failures)

Root cause: each of these tests invokes `subprocess.run(["uv", "run",
"sphinx-build", ...])` directly (rather than `sys.executable -m sphinx`, the
convention every other subprocess-based gate module in this suite already
follows -- see `tests/test_preview_smoke_gate.py`'s documented rationale).
Under this executor's NixOS sandbox, that specific invocation shape fails at
the OS level before Python even starts:

```
STDERR:
Could not start dynamically linked executable: uv
NixOS cannot run dynamically linked executables intended for generic
linux environments out of the box. For more information, see:
https://nix.dev/permalink/stub-ld
```

This is an environment-level (NixOS stub-ld) limitation of the `uv` binary
itself, not a code defect this plan's D-B/D-D changes introduced or could
fix. All 962 - 45 - 5(skipped) = 912 other tests pass, including every test
this plan's `<files>` list names. Confirmed identical failure signature
across every affected test (all `returncode == 127`, all citing the same
`stub-ld` message).

**Action:** none taken in this plan (out of scope, per SCOPE BOUNDARY). A
future maintenance task should migrate these five files' subprocess
invocations from `["uv", "run", "sphinx-build", ...]` to `[sys.executable,
"-m", "sphinx", ...]`, matching every other subprocess gate in this suite.

- **Status:** acknowledged
- Audit acknowledged at the v0.9.1 milestone close (2026-08-30): carried forward, still open, deliberately not fixed in this milestone.


## `ruff check .` requires `nix-shell -p ruff`, not `uv run ruff`

`uv run ruff check .` and `.venv/bin/ruff check .` both fail identically in
this executor's sandbox:

```
Could not start dynamically linked executable: ruff
NixOS cannot run dynamically linked executables intended for generic
linux environments out of the box.
```

`ruff` ships as a compiled Rust ELF binary (confirmed via `file
.venv/bin/ruff`), unlike `black`/`mypy` (pure-Python, which run fine via
`uv run`), so it needs NixOS's `nix-ld` wrapper, which is not configured for
arbitrary pip-installed binaries in this venv. Worked around for THIS plan's
verification by running `nix-shell -p ruff --run "ruff check ."` instead,
which resolves a nix-store-provided `ruff` with a working dynamic linker.
Result: **all checks passed** (confirmed against this plan's full diff).

**Action:** none taken (environment limitation, not a code defect). Noting
here so a future executor in the same sandbox does not re-diagnose this from
scratch.
