# Phase 60: One Delimiter-Aware Path-Quoting Helper, Routed Everywhere - Pattern Map

**Mapped:** 2026-08-29
**Files analyzed:** 8 (2 wave-1, 4 wave-2 new/extended)
**Analogs found:** 8 / 8

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|--------------------|------|-----------|-----------------|----------------|
| `typsphinx/pathfmt.py` (new) | utility (leaf formatter) | transform | `tests/_path_naming.py` (leaf-module discipline mirror) + `typsphinx/builder.py`'s `_conf17_violation_message()` trio (one-function-one-sentence pattern) | exact (structural mirror, cross-tier) |
| `tests/test_pathfmt.py` (new) | test (unit) | transform | `tests/test_path_naming_predicate.py` / `tests/_path_naming.py`'s own assertions | role-match |
| `tests/test_writer_path_quoting_gate.py` (new) | test (unit, log-capture) | event-driven (log emission) | `tests/test_builder.py` / `tests/test_track_image_key_construction.py` (`caplog.at_level(...)`) | role-match |
| `tests/test_template_registry_path_quoting_gate.py` (new) | test (unit, exception-capture) | request-response (validation → raise) | `tests/test_template_registry.py:485-641,830-896` (`pytest.raises(ExtensionError)` + `str(excinfo.value)`) | exact |
| `typsphinx/builder.py` (modified) | service/controller (Sphinx builder) | CRUD + request-response (message construction) | itself — `_conf17_violation_message()` / `_templates_path_collision_message()` / `_bundle_destination_collision_message()` (existing extracted-sentence-builder pattern) | exact (self-analog) |
| `typsphinx/writer.py` (modified) | service (writer) | transform + event-driven (debug log) | `typsphinx/builder.py`'s debug/warning sites for the log-message shape; `writer.py`'s own surrounding lines 490-514 for context | role-match |
| `typsphinx/template_registry.py` (modified) | service (validator) | request-response (validate → raise) | `typsphinx/template_registry.py:405-437` itself (`:410` untouched control site sits two lines above the two routed sites) | exact (self-analog) |
| `tests/test_templates_path_collision_gate.py` (extended, `builder.py` plan only) | test (unit) | request-response | `TestWindowsPathEscapingRegressionGuard` (existing class in same file) | exact |

## Pattern Assignments

### `typsphinx/pathfmt.py` (new leaf module, MSG-02)

**Primary analog:** `tests/_path_naming.py` (read in full, 62 lines) — Phase 58's leaf test-support
module, explicitly written as this module's mirror.

**Module docstring shape to copy** (`tests/_path_naming.py:1-27`):
```python
"""
MSG-01: format-agnostic predicate for asserting that a path value is NAMED
in a message, independent of the quoting convention the message site uses.
...
D-04: this module carries ZERO product-package imports -- it is a leaf
test-support module, mirroring MSG-02's leaf-module discipline on the
product side. It must not be added to ``tests/conftest.py`` (fixtures
only) or duplicated inline in the modules that consume it.
"""

import os
```
`pathfmt.py`'s own docstring should state the MSG-02 leaf-import contract (zero `typsphinx.*`
imports, only stdlib `os`) in the same declarative, decision-ID-citing style, and note it is the
product-side counterpart of this test-side module — including the ONE deliberate disagreement
(D-04: empty string → `''`, not a raised `ValueError`).

**Type-contract idiom to copy verbatim** (`tests/_path_naming.py:33-40`, and Pitfall 1 in
RESEARCH.md — `os.fspath()` alone does NOT reject `bytes`):
```python
def path_named_in(value: str | os.PathLike, text: str) -> bool:
    value_str = os.fspath(value)
    if not isinstance(value_str, str):
        raise TypeError(
            f"path_named_in() requires a value that normalizes to str via "
            f"os.fspath(), got {type(value_str).__name__}"
        )
```
`quote_path()` must use the identical two-step idiom (`os.fspath()` then explicit
`isinstance(result, str)`), per D-03 and RESEARCH.md's measured pitfall
(`os.fspath(b"foo")` returns `b"foo"` unchanged — it does not raise). Adapt the `TypeError` message
to name `quote_path()` instead of `path_named_in()`. Unlike `path_named_in()`, do **not** raise on
empty string (D-04) and **do** special-case `None` before the `os.fspath()` call (D-03: `None`
renders as the bare 4-character string `"None"`).

**Secondary analog — "one function is the ONE place a message sentence/value is built":**
`typsphinx/builder.py:496-595`'s three extracted builders (`_conf17_violation_message()`,
`_templates_path_collision_message()`, `_bundle_destination_collision_message()`, read in full
above). Each has a docstring explaining *why* it is its own function — "so a unit test can call the
real construction code with a Windows-shaped string, never a re-pasted f-string." `quote_path()` is
this same discipline one level down: never let a wiring site inline delimiter-selection logic.

**Reference delimiter algorithm** (RESEARCH.md, verified byte-identical to `repr()` minus backslash
doubling across 7 measured cases including a combined backslash+both-quotes edge case):
```python
def quote_path_ref(value: str) -> str:
    if "'" not in value:
        return f"'{value}'"
    if '"' not in value:
        return f'"{value}"'
    escaped = value.replace("'", "\\'")
    return f"'{escaped}'"
```

### `tests/test_pathfmt.py` (new, MSG-02's own gate, wave 1)

**Analog:** the assertion *style* used across `tests/_path_naming.py`'s consumers and
`tests/test_templates_path_collision_gate.py`'s `_assert_no_doubled_separator` (see below) — direct
function calls, no builder/app fixture needed (pure string-in, string-out). D-11 places this gate
entirely inside the helper's own new module; no existing test file is touched in wave 1.

Also gate the **leaf-import proof** (SC#1) the way RESEARCH.md's Phase Requirements → Test Map
row spells it out:
```bash
uv run python -c "import sys; import typsphinx.pathfmt; assert not any(m.startswith('typsphinx.') and m != 'typsphinx.pathfmt' and m != 'typsphinx' for m in sys.modules)"
```

### `typsphinx/builder.py` wiring plan (MSG-03, wave 2)

**Analog:** itself. The three existing extracted-builder functions at `builder.py:496-595` already
have their quoting rule stated in their own docstrings — those docstrings are explicitly part of the
change surface (they currently say `"quoted with explicit '...' , never !r"` and must be updated to
name `quote_path()`). The remaining 13 sites (D-06's list, D-08a–d, plus the AMENDED-block divergent
`target!r` sites at `:1192`/`:1199`) are ordinary `f"...{value!r}..."` → `f"...{quote_path(value)}..."`
substitutions with no structural change.

**Site list to route (from RESEARCH.md's classified Repo-Wide Discovery Grep table, all independently
re-derived and cross-checked against D-06/D-08):**
- `:524,526` `resolved_path`,`srcdir` (currently hardcoded `'…'`) — `_conf17_violation_message()`
- `:558,560,561` `bundle_dir`,`raw_tp_entry`,`resolved_tp_entry` (hardcoded `'…'`) — `_templates_path_collision_message()`
- `:594` `dest_dir` (hardcoded `'…'`) — `_bundle_destination_collision_message()`
- `:890` `target`,`fallback` — `_resolve_target_stem()` (D-08a)
- `:1135` `relpath` (`_claim()` closure), `:1157` `content_relpath`, `:1158` `TEMPLATE_OUTPUT_DIR` (D-08b)
- `:1192`,`:1199` `target` — **AMENDED, D-06 gap**, same semantic value as `:890`, D-08a reasoning applies
- `:1200` `wrapper_relpath`, `:1201` `TEMPLATE_OUTPUT_DIR` (D-08b), `:1208` `relpath` (failures-list joiner)
- `:1943` `resolved_uri`, `:1944` `key` (relocation path — D-08c, NOT a registry key)
- `:2232` `src_file`,`dest_file`; `:2241` `template_filename` (D-08d, its `key` sibling on the same
  line stays `!r` — a mixed site)
- `:2242` `src_dir`,`dest_dir`

**Sites that stay `!r` (do not touch):** `key`/`existing_key`/`declared_key`/`RESERVED_REGISTRY_KEY`
at `:523,557,592,593,1470,1471,1479,1565,2224,2231,2241`(key half only)`,2410`; `docname` everywhere
including where it shares an f-string with a routed `target` (e.g. `:1199`'s `docname!r` half); `entry`
tuple at `:1181`; `doc_tuple` at `:2538,2566`.

**RED to record (D-12):** for the three 57-11 builders, the single-quote disambiguation defect (see
"RED Reproduction" excerpt below) — the backslash-doubling half is already green there. For every
other site, the doubled-backslash RED via the same `_assert_no_doubled_separator` regex.

**Measured single-quote RED** (RESEARCH.md, calling the real function):
```python
>>> _conf17_violation_message("mykey", "/home/O'Brien/x", "/srcdir")
"typst_document_templates: registry key 'mykey''s resolved template '/home/O'Brien/x' has a "
"parent directory that is srcdir itself..."
```
`'/home/O'Brien/x'` visually closes the quote early — the `57-REVIEW.md` IN-01 defect this phase
fixes.

### `tests/test_templates_path_collision_gate.py` — extended by addition only (D-11, builder.py plan alone)

**Analog:** `TestWindowsPathEscapingRegressionGuard` (this same file, `:412-490`, read in full above).

**Constants to reuse, never redefine:**
```python
WINDOWS_SHAPED_PATH = "C:\\Users\\runner\\project\\_templates\\nested"
WINDOWS_SHAPED_SRCDIR = "C:\\Users\\runner\\project\\source"
```

**Helper to call, never re-derive:**
```python
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

**Docstring rule to follow (governs every new method added here):** call the ACTUAL
message-construction function (e.g. `_conf17_violation_message()`), never a copy of its f-string
pasted into the test — a re-pasted string would keep passing even after a regression. The existing
`test_registry_keys_stay_repr_quoted` control method (`:487-492`) is the pattern for a companion
"identifier stays `!r`" assertion if the new plan wants one for a routed site's sibling identifier.

**What "adding a method" looks like — copy this shape exactly, only changing the function called and
the assertion:**
```python
def test_conf17_violation_message_does_not_double_backslashes(self):
    message = _conf17_violation_message(
        "mykey", self.WINDOWS_SHAPED_PATH, self.WINDOWS_SHAPED_SRCDIR
    )
    self._assert_no_doubled_separator(message)
    assert self.WINDOWS_SHAPED_PATH in message
    assert self.WINDOWS_SHAPED_SRCDIR in message
```
This is a **method addition inside the existing class**, not a new class, not a new file, and not a
rewrite of `_assert_no_doubled_separator` or any existing method. Only `builder.py`'s wiring plan may
touch this file; the other two wave-2 plans must write their own new modules instead.

### `typsphinx/writer.py` wiring plan (MSG-04, wave 2)

**Site (writer.py:510-514, read above):**
```python
logger.debug(
    f"Rendering wrapper for docname {docname!r} at "
    f"wrapper_relative_dir={wrapper_relative_dir!r}, "
    f"include_path={include_path!r}, template_file={template_file!r}"
)
```
Route `wrapper_relative_dir`, `include_path`, `template_file` through `quote_path()`; leave
`docname!r` untouched (identifier-valued, D-07). `template_file` may be `None` on the package-alone
path (`writer.py:502-503`, `if typst_package and not raw_template_path: template_file = None`) — this
is exactly D-03's load-bearing `None → "None"` case; `quote_path(None)` must keep this line
byte-identical.

**Test analog — the `caplog` idiom as actually used in this suite (not a generic pytest doc):**
```python
# tests/test_builder.py-style usage
with caplog.at_level("WARNING"):
    ...
warning_records = [r for r in caplog.records if r.levelname == "WARNING"]
```
For MSG-04's DEBUG-level site, use the same fixture with `"DEBUG"` in place of `"WARNING"`:
```python
with caplog.at_level("DEBUG"):
    ...  # trigger the wrapper render
debug_records = [r for r in caplog.records if r.levelname == "DEBUG"]
```
A second concrete precedent for a `caplog.at_level("WARNING")` call inside a `with` block guarding a
builder call is `tests/test_track_image_key_construction.py:83-96` (also explicitly notes: "Never
asserts on the `logger.warning` message text -- its `!r` quoting is MSG-03's site in Phase 60" — this
phase is that named site).

**RED to record (D-12), measured doubled-backslash shape:**
```python
>>> re.findall(r"\\\\+", message)
['\\\\', '\\\\', '\\\\', '\\\\', '\\\\', '\\\\', '\\\\', '\\\\', '\\\\', '\\\\', '\\\\']  # ELEVEN doubled runs
```

### `typsphinx/template_registry.py` wiring plan (MSG-05, wave 2)

**Sites (template_registry.py:405-437, read in full above):**
```python
elif template:
    template_abs_path = os.path.join(srcdir, template)
    if _violates_conf17(template_abs_path, srcdir):
        failures.append(
            f"registry key {key!r}'s template {template!r} "     # :422 -- route `template`
            "resolves to a parent directory that is srcdir "
            "itself, or an ancestor of srcdir (CONF-17)"
        )
    if not os.path.isfile(template_abs_path):
        failures.append(
            f"registry key {key!r}'s template {template!r} does " "not exist"  # :433 -- route `template`
        )
```
Route `template` at both sites; leave `key` at both sites untouched (identifier, D-07). Do **not**
touch the type-check branch two lines above (`:410`, `f"... template {template!r} must be a path
string ..."`) — deliberately excluded (SC#3 pass criterion), reached only when `template` is NOT a
`str`/`os.PathLike`.

**Test analog — substring-assertion idiom, read verbatim from the two guarding test groups:**

CONF-17 (`tests/test_template_registry.py:480-499`):
```python
with pytest.raises(ExtensionError) as excinfo:
    resolve_template_registry(app.config, str(app.srcdir))
assert "CONF-17" in str(excinfo.value)
```

Existence check (`tests/test_template_registry.py:590-606`):
```python
with pytest.raises(ExtensionError) as excinfo:
    resolve_template_registry(app.config, str(app.srcdir))
assert "does not exist" in str(excinfo.value)
assert "typst_document_templates" in str(excinfo.value)
```

`:410`'s two guarding tests that must stay green **unmodified** (`tests/test_template_registry.py`,
read in full above — this is the falsification gate proving `:410` was NOT accidentally routed):
```python
# list-typed template (Test F region, ~:830)
message = str(excinfo.value)
assert "must be a path string" in message
assert repr(["a", "b"]) in message

# bytes-typed template (Test G, ~:836-847)
app.config.typst_document_templates = {"bad_tpl": {"template": b"base.typ"}}
with pytest.raises(ExtensionError) as excinfo:
    resolve_template_registry(app.config, str(app.srcdir))
message = str(excinfo.value)
assert "must be a path string" in message
assert repr(b"base.typ") in message
```

**RED shapes to record (D-12), two independent shapes, both measured:**
```python
# Shape 1: ordinary str template, Windows-shaped -- doubled backslash
>>> re.findall(r"\\\\+", msg422)
['\\\\', '\\\\', '\\\\', '\\\\']    # FOUR doubled runs

# Shape 2: pathlib.Path template that does not exist -- PosixPath(...) leak
>>> template_path = Path("/some/path/_templates/nested")
>>> f"registry key {key!r}'s template {template_path!r} does not exist"
"registry key 'mykey''s template PosixPath('/some/path/_templates/nested') does not exist"
```
Shape 2 has **no existing test coverage** — Test H (`test_pathlike_template_field_still_resolves`,
read above) proves a `pathlib.Path` template is a supported, working shape, but no test drives it
through the NOT-FOUND branch. This is new coverage the wiring plan must add, not a modification of an
existing assertion. `quote_path()` must call `os.fspath()` on a `Path` BEFORE quote-character
inspection, or the `PosixPath('…')` wrapper leaks through even after routing.

## Shared Patterns

### Import discipline (D-02, forced placement)
**Source:** import blocks of all three product modules, read directly this session.
```python
# builder.py:22-29 (module-scope imports the cycle argument rests on)
from typsphinx.pdf import compile_typst_file_to_pdf
from typsphinx.template_registry import (...)
from typsphinx.translator import derive_master_edge_keys
from typsphinx.writer import TEMPLATE_OUTPUT_DIR, TypstWriter
```
`typsphinx/pathfmt.py` must import **only** `os` — no `typsphinx.*` import of any kind (not even
`typsphinx.template_registry`, which has the least restrictive existing graph). All three wiring
plans add one line: `from typsphinx.pathfmt import quote_path`.

**Apply to:** `typsphinx/pathfmt.py` (must NOT import), `typsphinx/builder.py`,
`typsphinx/writer.py`, `typsphinx/template_registry.py` (must each ADD the one import line).

### "One function is the ONE place a message sentence is built"
**Source:** `typsphinx/builder.py:496-595` (`_conf17_violation_message()` and its two siblings).
**Apply to:** `typsphinx/pathfmt.py`'s `quote_path()` itself — never let any of the three wiring
sites inline delimiter-selection logic; always call `quote_path(value)`.

### `caplog` at a named level, filtered by `levelname`
**Source:** `tests/test_builder.py` (`with caplog.at_level("WARNING"): ...; [r for r in caplog.records
if r.levelname == "WARNING"]`), `tests/test_track_image_key_construction.py:83-96`.
**Apply to:** `tests/test_writer_path_quoting_gate.py` (new), substituting `"DEBUG"`.

### `pytest.raises(ExtensionError)` + `str(excinfo.value)` substring assertion
**Source:** `tests/test_template_registry.py:480-896` (every CONF-17 / existence / type-check test in
that module).
**Apply to:** `tests/test_template_registry_path_quoting_gate.py` (new).

### Windows-shaped literal strings, never `os.name`-gated
**Source:** `TestWindowsPathEscapingRegressionGuard.WINDOWS_SHAPED_PATH` /
`WINDOWS_SHAPED_SRCDIR` (`tests/test_templates_path_collision_gate.py:441-442`).
**Apply to:** every wave-2 test module's RED/green fixtures — hand-built backslash-bearing string
literals, runnable on every CI lane including non-Windows, per RESEARCH.md's Architecture Patterns
note ("nothing needs the `windows-latest` lane to go RED first").

### Live AST guard — the census this phase must not perturb
**Source:** `tests/test_repr_census_guard.py` — re-derives Phase 58's `!r` census at run time.
**What it asserts:** every `!r` occurrence in the tracked modules matches a pre-recorded allowlist
(`58-REPR-CENSUS.md`'s classification of identifier-valued vs. path-valued sites); adding or removing
a test-file assertion, or routing a site the census still expects to see as `!r`, without
re-deriving the census, is what turns it RED.
**What makes it go RED:** editing a **test file's** `!r` usage without updating the census (out of
scope here — zero test edits, per ROADMAP constraint 9), or a wiring plan routing an identifier-valued
site by mistake (e.g. accidentally routing `:410`'s `template!r`, or any `key`/`docname` site).
**Apply to:** all three wave-2 plans as a standing negative check — run
`uv run pytest tests/test_repr_census_guard.py` after wiring, alongside the full suite, before
declaring the plan green. "Zero test edits" (SC#5) is measured against this guard plus
`58-REPR-CENSUS.md`, not self-declared.

## No Analog Found

None — every file in the fixed set has a strong (exact or role-match) analog; no file requires
falling back to RESEARCH.md's synthesized reference implementation alone.

## Metadata

**Analog search scope:** `typsphinx/` (all product modules read directly), `tests/` (leaf
test-support modules, `TestWindowsPathEscapingRegressionGuard`, `test_template_registry.py`,
`test_builder.py`, `test_track_image_key_construction.py` read/grepped directly).
**Files scanned:** 3 product modules read in full at their relevant ranges; 5 test modules read or
grepped; RESEARCH.md's own repo-wide grep output cross-checked against direct reads rather than
re-run redundantly.
**Pattern extraction date:** 2026-08-29
