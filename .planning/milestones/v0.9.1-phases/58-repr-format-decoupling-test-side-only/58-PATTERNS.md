# Phase 58: `repr()`-Format Decoupling (test-side only) - Pattern Map

**Mapped:** 2026-08-27
**Files analyzed:** 5 (all under `tests/`; `typsphinx/` is out of scope per SC#4)
**Analogs found:** 5 / 5 (one file — `_path_naming.py` — has NO direct analog in the codebase; this is
itself a confirmed finding, not a gap, since D-04's rationale for the module's existence is precisely
that no bare leaf-support module currently exists under `tests/`)

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `tests/_path_naming.py` | utility (test-support, leaf module) | transform (pure predicate fn) | *none* — no bare top-level helper module exists under `tests/` today | no-analog (confirmed by search; see below) |
| `tests/test_path_naming_predicate.py` | test (unit, meta-test) | transform | `tests/test_collision_predicate_completeness_gate.py` / `tests/test_sanitize_label_injectivity_unit.py` (pure-function unit-test style, no Sphinx app) | role-match |
| `tests/test_repr_census_guard.py` | test (static-analysis guard) | batch (whole-tree AST sweep) | `tests/test_no_stale_github_io_links.py` (whole-repo sweep style) + the AST walk technique itself is genuinely novel to this codebase | partial-match |
| `tests/test_out02_escape_target_gate.py` (MODIFIED, line ~134) | test (integration, subprocess) | request-response (real `sphinx-build` subprocess) | itself — the surrounding module already establishes every pattern the edit must preserve (`_run_sphinx_build`, `ESCAPE_WARNING_SUBSTRING`, `_target_for_shape`) | exact (self-analog) |
| `tests/test_builder.py` (MODIFIED, line ~598) | test (integration, in-process) | event-driven (`caplog` capture of a logged warning) | itself — same rationale, plus `TestWindowsPathEscapingRegressionGuard` for the "call the real function, never re-paste the format string" discipline | exact (self-analog) + cross-reference |

## Pattern Assignments

### `tests/_path_naming.py` (utility, transform)

**Analog:** none found by search (`find tests -maxdepth 1 -name '*.py' ! -name 'test_*' ! -name 'conftest.py'`
returns nothing besides itself once created). This absence is itself load-bearing evidence for D-04:
`tests/` has no precedent for a bare top-level support module, only `conftest.py` (fixtures-only,
confirmed below) and `test_*.py` files. The module must therefore be built from CONTEXT.md/RESEARCH.md's
own locked design (D-01/D-03/D-04), not copied from an existing file. RESEARCH.md's Code Example #1 is
the authoritative source text — reproduce it verbatim as the starting point:

```python
# tests/_path_naming.py
"""
Format-agnostic predicate for asserting that a path value is NAMED in a
message, independent of the quoting convention the message site uses.
...
Zero typsphinx imports (mirrors MSG-02's leaf-module discipline).
"""

import os


def path_named_in(value: str | os.PathLike, text: str) -> bool:
    value_str = os.fspath(value)
    return value_str in text or repr(value_str) in text
```

**Import convention confirmed live** (`tests/conftest.py:1-11`):
```python
"""
pytest configuration and fixtures for typsphinx tests.
"""

from pathlib import Path
from typing import Any, Dict

import pytest
from docutils import nodes
from sphinx.testing.util import SphinxTestApp

pytest_plugins = "sphinx.testing.fixtures"
```
`conftest.py` confirmed to hold fixtures only (`rootdir`, `sample_doctree`, and per RESEARCH.md also
`temp_sphinx_app`, `sphinx_config`, `mock_builder`) — no plain helper functions exist there, which is
exactly D-04's rejected alternative. `_path_naming.py` must NOT be added to this file.

**Docstring convention:** every module in `tests/` opens with a triple-quoted module docstring naming
the requirement ID and explaining the design rationale in prose (see `test_out02_escape_target_gate.py`'s
opening docstring below, and `test_templates_path_collision_gate.py`'s). `_path_naming.py` should follow
the same convention even though it is not itself a test module.

---

### `tests/test_path_naming_predicate.py` (test, unit/meta-test)

**Analog:** codebase unit-test style for pure functions with no Sphinx app fixture — e.g.
`test_sanitize_label_injectivity_unit.py`, `test_collision_predicate_completeness_gate.py` (both
`*_unit.py`/`*_gate.py` files that import a function directly and assert on plain input/output pairs,
no `temp_sphinx_app`/`rootdir` fixtures).

**Import pattern** — flat top-level import, matching `tests/` `sys.path` convention (no `tests.`
package prefix anywhere in the suite):
```python
from _path_naming import path_named_in
```

**Core meta-test table shape** (from RESEARCH.md Code Example #2, to be extended, NOT replaced, with
the D-03 fallback-trap negative case — this is the single most important test in the new module per
Common Pitfall #2):
```python
def test_raw_value_present_is_named():
    assert path_named_in("C:\\escape.typ", "target: C:\\escape.typ") is True


def test_repr_quoted_value_is_named():
    message = f"target: {'C:\\escape.typ'!r}"
    assert path_named_in("C:\\escape.typ", message) is True


def test_d03_fallback_trap_is_not_a_false_positive():
    # The value under test ("C:\escape.typ") is ABSENT; only its
    # same-basename sibling ("escape.typ") is quoted. This is the exact
    # shape builder.py:697 produces for the drive-qualified escape shape.
    message = "using 'escape.typ' instead"
    assert path_named_in("C:\\escape.typ", message) is False
```

**No fixtures, no Sphinx app** — plain `def test_*():` functions, matching e.g.
`tests/test_registry_container_shape_gate.py`'s parametrized-but-fixtureless style for logic-only
assertions (as opposed to the app-fixture-heavy integration tests).

---

### `tests/test_repr_census_guard.py` (test, static-analysis / batch)

**Analog:** no exact precedent for AST-based source sweeps in this suite; closest structural analog
is `tests/test_no_stale_github_io_links.py` (a whole-repo-tree textual sweep asserting an absence
condition) for the "walk the tree, assert on the aggregate" shape, but the AST mechanics themselves
are new. RESEARCH.md's Code Example #3 was independently prototyped and verified this session against
the live tree (exactly 9 hits, matching D-08's table) — treat it as the authoritative, already-tested
starting point, not something to re-derive:

```python
import ast
import pathlib

root = pathlib.Path("tests")
hits = []
for f in root.rglob("*.py"):
    if "__pycache__" in f.parts:
        continue
    # D-09: the guard's OWN file must be excluded from the sweep --
    # its allowlist literals contain "repr(" in source form.
    if f.name == "test_repr_census_guard.py":
        continue
    tree = ast.parse(f.read_text(), filename=str(f))
    for node in ast.walk(tree):
        if isinstance(node, ast.Assert):
            # D-09: walk ONLY node.test, never node.msg.
            for sub in ast.walk(node.test):
                if (
                    isinstance(sub, ast.Call)
                    and isinstance(sub.func, ast.Name)
                    and sub.func.id == "repr"
                ):
                    hits.append((str(f), sub.lineno))
                if isinstance(sub, ast.FormattedValue) and sub.conversion == 114:
                    hits.append((str(f), sub.lineno))
```

**Assertion shape:** hit-set (minus the two rewritten path sites, which move OFF the allowlist once
this phase rewrites them) equals a recorded allowlist of exactly 7 non-path sites (the census table in
CONTEXT.md D-08, sites #3-#9). Follow `tests/test_preview_version_sync.py`'s style of asserting a
computed set equals a literal recorded constant, for the general "derive live, compare to recorded
constant" pattern used elsewhere in this suite for drift guards.

**Self-exclusion is mandatory** — the guard's own allowlist literals contain the string `repr(` in
source form, so the file must skip itself during the sweep (shown above).

---

### `tests/test_out02_escape_target_gate.py` (MODIFIED, integration, request-response)

**Self-analog — the surrounding module already defines every pattern the edit reuses.**

**Module docstring / constants** (lines 1-34, already in place, D-02 depends on these — do not
re-derive or re-paste):
```python
FIXTURES_DIR = Path(__file__).parent / "fixtures"
ESCAPE_TARGET_GATE_FIXTURE_DIR = FIXTURES_DIR / "out02_escape_target_gate"

ESCAPE_WARNING_SUBSTRING = "a path is not supported in a typst_documents target name"
```

**Subprocess helper** (`_run_sphinx_build`, lines ~38-56) — invoked as `sys.executable -m sphinx`,
already returns `subprocess.CompletedProcess`; the rewritten test keeps calling this unchanged.

**The exact block to replace** (current, ~line 130-136):
```python
    # The warning formats the target via `!r` (repr) -- for a target
    # carrying a literal backslash (the drive-qualified shape), repr()
    # doubles it for display, so the warning-text search must match the
    # repr'd form the actual log line contains, not the raw target string.
    assert repr(target) in combined_output, (
        f"Expected the warning to name the offending target {target!r}:\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
```

**D-02's replacement shape** (from RESEARCH.md Pattern 2 — line-narrow first, then apply the
predicate; import `path_named_in` at module top alongside the existing imports):
```python
warning_lines = [
    line for line in combined_output.splitlines()
    if ESCAPE_WARNING_SUBSTRING in line
]
assert len(warning_lines) == 1, (
    f"Expected exactly one warning line naming the refused target:\n"
    f"{combined_output}"
)
assert path_named_in(target, warning_lines[0]), (
    f"Expected the warning to name the offending target {target!r} "
    f"(raw or repr()'d):\n{warning_lines[0]}"
)
```

`target = _target_for_shape(shape)` (already computed earlier in the test, lines ~110-111) — the
rewrite must feed this existing value into `path_named_in`, never re-derive or re-paste the shape
string (mirrors `TestWindowsPathEscapingRegressionGuard`'s "call the real value/function" discipline).

---

### `tests/test_builder.py` (MODIFIED, integration, event-driven / caplog)

**Self-analog**, plus cross-reference to `TestWindowsPathEscapingRegressionGuard` for the calling
discipline.

**Surrounding fixture/assertion shape already in place** (`test_post_process_images_rehome_escape_relocates_with_warning`,
lines ~540-598 — do not re-derive `abs_uri`/`expected_key`/`digest` construction, only the final
assertion line changes):
```python
    warning_records = [r for r in caplog.records if r.levelname == "WARNING"]
    assert len(warning_records) == 1
    message = warning_records[0].getMessage()
    assert "could not rehome image URI" in message
    # The product formats the URI with `!r` (deliberate -- it quotes the
    # path), so the emitted message contains repr(abs_uri), not abs_uri
    # itself. On POSIX repr() escapes nothing and the two happen to be
    # equal, masking this on this host; on Windows repr() doubles every
    # backslash (os.sep == "\\"), so the raw path is no longer a substring
    # of the message. Asserting against repr(abs_uri) holds on both.
    assert repr(abs_uri) in message
```

**The exact line to replace** (last line above): `assert repr(abs_uri) in message` becomes
`assert path_named_in(abs_uri, message)` — direct one-line substitution per RESEARCH.md, no
line-narrowing needed here since `message` is already a single `caplog` record's `getMessage()`.

**No `os.name` branch needed in the assertion itself** — the surrounding `abs_root`/`abs_uri`
construction already branches on `os.name` (lines 555-561) to build a platform-appropriate absolute
path; that branch is untouched, only the final assertion changes.

---

### Cross-reference precedent: `TestWindowsPathEscapingRegressionGuard`

**Source:** `tests/test_templates_path_collision_gate.py:411-470`

This is the class CONTEXT.md names as the test-side precedent this phase must match. Its
class-level docstring states the discipline verbatim (lines 412-437):

```python
class TestWindowsPathEscapingRegressionGuard:
    """57-11: closes the blind spot that let CI runs 31956166848 and
    31959060298 both fail on windows-latest for the same reason before
    being twice misdiagnosed as a path-separator problem. ...

    Each test below calls the ACTUAL message-construction function --
    ``_conf17_violation_message()``, ``_templates_path_collision_message()``,
    and ``_bundle_destination_collision_message()`` -- the same three
    functions ``typsphinx/builder.py`` calls at its three pre-write
    refusal sites, never a copy of their f-strings pasted into this test
    module. A re-pasted format string would keep passing even if the
    product regressed back to ``!r``; calling the real function is what
    makes reverting any one site turn its own test RED (recorded in
    57-MESSAGE-FIX-EVIDENCE.md).

    Honest limit: this drives real product code with a Windows-SHAPED
    string (one built by hand, containing backslashes), not a
    Windows-host-resolved ``pathlib.WindowsPath`` -- there is no Windows
    host available to this suite. ...
    """

    WINDOWS_SHAPED_PATH = "C:\\Users\\runner\\project\\_templates\\nested"
    WINDOWS_SHAPED_SRCDIR = "C:\\Users\\runner\\project\\source"

    @staticmethod
    def _assert_no_doubled_separator(message: str) -> None:
        """No run of consecutive backslashes longer than 1 may appear --
        that is what ``repr()`` escaping would produce and what this
        guard exists to catch."""
        doubled = re.findall(r"\\\\+", message)
        assert not doubled, (
            f"Expected every backslash run to be a single unescaped "
            f"separator, found a doubled/escaped run in:\n{message!r}"
        )
```

**Two things to extract and mirror exactly:**
1. **Hand-built Windows-shaped string literals**, never `os.name`-gated, never a real Windows host —
   `WINDOWS_SHAPED_PATH = "C:\\Users\\runner\\project\\_templates\\nested"` is the class-attribute
   convention. `test_out02_escape_target_gate.py`'s `_target_for_shape()` (lines 80-92, already
   existing, reused unmodified) follows the equivalent convention for the `drive` shape
   (`"C:\\escape.typ"` — a hand-built literal, not derived from a real Windows path resolution).
2. **"Call the real function/value, never re-paste the format string."** This class calls the
   product's own message-construction functions directly; Phase 58's two rewritten tests already call
   real product code paths (`sphinx-build` subprocess, `builder.post_process_images()`) — the pattern
   to preserve is that `path_named_in` receives the SAME `target`/`abs_uri` variable the test already
   computed, never a re-typed literal copy of it.

**Explicitly classified, NOT rewritten** (per D-07/D-08's third bucket): this class's own
`_assert_no_doubled_separator` intentionally asserts on `repr()`'s *absence* of doubled backslashes —
the inverse direction of MSG-01's target. It is a dependency of MSG-02's future gate, not decoupled by
this phase.

## Shared Patterns

### Module docstring convention
**Source:** every `tests/*.py` file (e.g. `test_out02_escape_target_gate.py:1-16`,
`test_templates_path_collision_gate.py:1-20`)
**Apply to:** all new files (`_path_naming.py`, `test_path_naming_predicate.py`,
`test_repr_census_guard.py`)
```python
"""
<Requirement-ID prefix>: <one-line summary>.

<prose rationale paragraph(s), often citing the specific defect/CI-run/
prior-phase context that motivates the file's existence>
"""
```

### Flat top-level import (no package prefix)
**Source:** `tests/` has no `__init__.py`; confirmed via D-04's live probe and this session's own
`ls tests/` sweep (no `tests/__init__.py`, no sub-package directories among the `.py` files).
**Apply to:** `test_path_naming_predicate.py`, `test_out02_escape_target_gate.py`,
`test_builder.py` — all import `_path_naming` as a bare top-level module:
```python
from _path_naming import path_named_in
```

### "Call the real product function/value, never re-paste the format string"
**Source:** `TestWindowsPathEscapingRegressionGuard` docstring, `tests/test_templates_path_collision_gate.py:424-431`
**Apply to:** both rewritten assertions in `test_out02_escape_target_gate.py` and `test_builder.py` —
`path_named_in` must be called with the test's own already-computed `target`/`abs_uri` variable, never
a re-typed literal.

### `typst`-availability skip-gate awareness (not a pattern to copy, a hazard to avoid)
**Source:** `tests/test_out02_escape_target_gate.py:25-31` (`TYPST_AVAILABLE` try/except import),
`:96-99` `@pytest.mark.skipif(not TYPST_AVAILABLE, ...)` — RESEARCH.md Pitfall 1.
**Apply to:** evidence-gathering for the D-05/D-06 falsification runs — must record the literal
pytest summary line (`"N passed"` naming the target test), not merely `returncode == 0`, to avoid a
SKIP being misread as a PASS.

## No Analog Found

| File | Role | Data Flow | Reason |
|---|---|---|---|
| `tests/_path_naming.py` | utility (leaf module) | transform | Confirmed by search: `tests/` has zero bare top-level helper modules today, only `conftest.py` (fixtures-only) and `test_*.py` files — this is precisely D-04's stated rationale for why the module doesn't already exist. Build from RESEARCH.md Code Example #1 (already the authoritative locked design), not from a codebase analog. |

## Metadata

**Analog search scope:** `tests/` (all `.py` files, `tests/roots/` and `tests/fixtures/` excluded as
non-Python or fixture-only), plus `tests/conftest.py` read in full for the D-04 fixtures-only claim.
**Files scanned:** `tests/conftest.py`, `tests/test_out02_escape_target_gate.py` (full),
`tests/test_builder.py:540-610`, `tests/test_templates_path_collision_gate.py:1-25,395-470`,
`tests/test_registry_container_shape_gate.py` (imports only), plus a directory listing of all
`tests/*.py` files (excluding `roots/`, `fixtures/`, `__pycache__`) to confirm no bare leaf-module
precedent exists.
**Pattern extraction date:** 2026-08-27
</content>
