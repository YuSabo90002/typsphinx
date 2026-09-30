# Phase 60 Plan 04 — MSG-05 Evidence

## Plan base SHA

```
1118199a577533f598a799b51d08b7bc3e9bcc49
```

## Discovery grep

Command: `grep -n '\!r' typsphinx/template_registry.py`

```
113:        return f"registry key {key!r} is empty or whitespace-only"
115:        return f"registry key {key!r} is '.' or '..', which is not a legal registry key"
118:            f"registry key {key!r} contains a path separator ('/' or "
123:            f"registry key {key!r} is a Windows reserved device name "
127:        return f"registry key {key!r} ends with a trailing dot"
129:        return f"registry key {key!r} ends with a trailing space"
132:            f"registry key {key!r} differs from another registered key " "only by case"
305:            f" got {declared!r}"
332:            failures.append(f"registry key {key!r} is not a string")
340:                f"registry key {key!r} is reserved for the built-in "
341:                f"{RESERVED_REGISTRY_KEY!r} key and cannot be redeclared "
363:                f"registry key {key!r}'s definition must be a dict, got "
364:                f"{raw_definition!r}"
376:                f"registry key {key!r}'s definition sets both 'template' "
410:                f"registry key {key!r}'s template {template!r} must be a path string or os.PathLike, "
422:                    f"registry key {key!r}'s template {template!r} "
433:                    f"registry key {key!r}'s template {template!r} does " "not exist"
514:                f"typst_documents entry names registry key {raw_key!r}, "
516:                f"typst_document_templates keys: {sorted(registry.keys())!r}"
524:            f"typst_documents entry names registry key {key!r}, which is "
526:            f"keys: {sorted(registry.keys())!r}"
```

Classification per D-05's role rule (does the reader read this as a location on a filesystem, or
as a name in a namespace?):

- `:113` — `key` — registry key, identifier-valued. **Stays unrouted.**
- `:115` — `key` — registry key, identifier-valued. **Stays unrouted.**
- `:118` — `key` — registry key, identifier-valued. **Stays unrouted.**
- `:123` — `key` — registry key, identifier-valued. **Stays unrouted.**
- `:127` — `key` — registry key, identifier-valued. **Stays unrouted.**
- `:129` — `key` — registry key, identifier-valued. **Stays unrouted.**
- `:132` — `key` — registry key, identifier-valued. **Stays unrouted.**
- `:305` — `declared` — the raw, non-`dict` `typst_document_templates` config value itself (whatever
  the user declared the whole config option as); not a path in any sense. **Stays unrouted.**
- `:332` — `key` — registry key, identifier-valued. **Stays unrouted.**
- `:340`/`:341` — `key` and `RESERVED_REGISTRY_KEY` — both registry keys, identifier-valued.
  **Stay unrouted.**
- `:363`/`:364` — `key` (registry key) and `raw_definition` (the raw, non-`dict` definition value —
  not a path). **Stay unrouted.**
- `:376` — `key` — registry key, identifier-valued. **Stays unrouted.**
- `:410` — `key` (registry key, unrouted) and `template` — the deliberate exclusion (MSG-05/D-12
  shape 3 / SC#3): reached only when `template` is NOT `str` and NOT `os.PathLike`, so it is never
  path-shaped here. **Both interpolations on this line stay unrouted.**
- `:422` — `key` (registry key, unrouted) and `template` — this IS a path-valued interpolation
  (the CONF-17 violation message). **`template` routes through `quote_path()`; `key` stays
  unrouted.**
- `:433` — `key` (registry key, unrouted) and `template` — this IS a path-valued interpolation
  (the existence-check message). **`template` routes through `quote_path()`; `key` stays
  unrouted.**
- `:514`/`:516` — `raw_key` (registry key, identifier-valued) and
  `sorted(registry.keys())` — a SORTED LIST OF REGISTRY KEYS rendered as a diagnostic summary; the
  `repr()` call here is a summary-list rendering, not a single path-valued message interpolation,
  and every element of the list is itself an identifier-valued registry key. **Both stay
  unrouted.**
- `:524`/`:526` — same shape as `:514`/`:516`: `key` (registry key) and
  `sorted(registry.keys())` (key list). **Both stay unrouted.**

Note (per task instructions): this module's `repr()` call inside its key SORT (e.g. any
`sorted(..., key=repr)`-style usage, if present) would be a sort key, not a message interpolation,
and out of SC#2's scope entirely. No such sort-key usage was found in this module's discovery grep
output above — every hit above is a message-interpolation `!r`, not a sort key. Recorded per the
task instruction for completeness.

**Result: exactly two `template` interpolations route (`:422`, `:433`); the type-check branch's
`template` at `:410` stays unrouted (the deliberate exclusion); every registry-key interpolation in
every form stays unrouted; the non-`dict` declared-value and raw-definition interpolations stay
unrouted; the sorted key lists stay unrouted.** This matches D-05/D-06/D-07's classification
exactly.

## RED shape 1 — doubled backslash (str template)

Command: `uv run pytest tests/test_template_registry_path_quoting_gate.py -q`
(plan base SHA `1118199a577533f598a799b51d08b7bc3e9bcc49`, pre-fix tree)

Both `TestRegistryTemplatePathQuoting` methods fail because the pre-fix module still
renders `template` with `!r`, which doubles every backslash in a Windows-shaped `str`
template:

```
_ TestRegistryTemplatePathQuoting.test_conf17_violation_message_has_no_doubled_separator _

message = "typst_document_templates: 2 invalid definition(s): registry key 'mykey''s template 'C:\\\\Users\\\\runner\\\\base.typ' resolves to a parent directory that is srcdir itself, or an ancestor of srcdir (CONF-17); registry key 'mykey''s template 'C:\\\\Users\\\\runner\\\\base.typ' does not exist"

    def _assert_no_doubled_separator(message: str) -> None:
        doubled = re.findall(r"\\\\+", message)
>       assert not doubled, (
            f"Expected every backslash run to be a single unescaped "
            f"separator, found a doubled/escaped run in:\n{message!r}"
        )
E       AssertionError: Expected every backslash run to be a single unescaped separator, found a doubled/escaped run in:
E         "typst_document_templates: 2 invalid definition(s): registry key 'mykey''s template 'C:\\\\Users\\\\runner\\\\base.typ' resolves to a parent directory that is srcdir itself, or an ancestor of srcdir (CONF-17); registry key 'mykey''s template 'C:\\\\Users\\\\runner\\\\base.typ' does not exist"
E       assert not ['\\\\', '\\\\', '\\\\', '\\\\', '\\\\', '\\\\']

_ TestRegistryTemplatePathQuoting.test_existence_check_message_has_no_doubled_separator _

message = "typst_document_templates: 1 invalid definition(s): registry key 'mykey''s template '_typst/nested/C:\\\\Users\\\\runner\\\\base.typ' does not exist"

    def _assert_no_doubled_separator(message: str) -> None:
        doubled = re.findall(r"\\\\+", message)
>       assert not doubled, (
            f"Expected every backslash run to be a single unescaped "
            f"separator, found a doubled/escaped run in:\n{message!r}"
        )
E       AssertionError: Expected every backslash run to be a single unescaped separator, found a doubled/escaped run in:
E         "typst_document_templates: 1 invalid definition(s): registry key 'mykey''s template '_typst/nested/C:\\\\Users\\\\runner\\\\base.typ' does not exist"
E       assert not ['\\\\', '\\\\', '\\\\']
```

Both shapes reach their intended branch exactly as designed: shape (a) — a bare
`"C:\Users\runner\base.typ"` component — fires BOTH the CONF-17 branch (its resolved
parent equals `srcdir` itself, since a backslash is not a POSIX path separator) and the
existence check (accumulated in the same raise, per D-09); shape (b) — the
`"_typst/nested/..."`-prefixed variant — moves the resolved parent below `srcdir`, so
only the existence check fires and `"CONF-17"` is absent from the message, as asserted.
No substitution was needed; the constructed shapes reached their intended branches on
the first attempt.

## RED shape 2 — leaked class-name wrapper (Path template)

Command: `uv run pytest tests/test_template_registry_path_quoting_gate.py -q`
(plan base SHA `1118199a577533f598a799b51d08b7bc3e9bcc49`, pre-fix tree)

```
_ TestRegistryPathLikeTemplateNoClassWrapper.test_pathlike_template_existence_message_leaks_no_class_wrapper _

message = "typst_docum...es not exist"
    assert "does not exist" in message
    assert str(template) in message
>   assert "PosixPath" not in message
E   AssertionError: assert 'PosixPath' not in 'typst_docum...es not exist'
E
E   'PosixPath' is contained here:
E      template PosixPath('/some/path/_templates/nested/base.typ') does not exist
E   ?           +++++++++
```

This shape has NO existing coverage anywhere in the suite before this module — it is a
genuinely new gate, not a re-derivation of an existing test. An absolute,
outside-`srcdir` `pathlib.Path("/some/path/_templates/nested/base.typ")` makes
`os.path.join(srcdir, template)` return the `Path` verbatim (an absolute component
discards `srcdir`), so its resolved parent is outside `srcdir` and only the existence
check fires — the pre-fix `{template!r}` conversion renders it as
`PosixPath('/some/path/_templates/nested/base.typ')`, leaking Python's internal class
name into a user-facing `conf.py` error.

Full transcript (all 5 collected tests, 3 failed / 2 passed at this point in the plan):

```
collected 5 items

tests/test_template_registry_path_quoting_gate.py FFF..                  [100%]

3 failed, 2 passed in 0.17s
```

## Exclusion control (two-tree)

**Pre-fix half** (plan base SHA `1118199a577533f598a799b51d08b7bc3e9bcc49`):

Command: `uv run pytest tests/test_template_registry_path_quoting_gate.py -q -k type_check_message_stays_repr_quoted`

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
collected 5 items / 3 deselected / 2 selected

tests/test_template_registry_path_quoting_gate.py ..                     [100%]

======================= 2 passed, 3 deselected in 0.12s ========================
```

`TestRegistryTypeCheckMessageStaysReprQuoted`'s two methods (list-typed and bytes-typed
`template`) are already GREEN before any product-code change — the type-check branch
(`template_registry.py:410`) is untouched by this task and stays on Python's own
`repr()` conversion. This is the pre-fix half of the two-tree pin; task 2 restores the
pre-fix module temporarily to re-run this identical selector and confirm the excluded
site's behaviour is byte-identical after the fix lands, then completes the post-fix
half below.

**Post-fix half** (after task 2's `feat(60-04)` commit `623d023f` and its follow-up
`fix(60-04)` commit `7b1c4e3c` — a comment-only reword that corrected an accidental
`grep`-count inflation with no change to any interpolation or message text — restored
via `git checkout HEAD -- typsphinx/template_registry.py`):

Procedure: `git checkout 1118199a577533f598a799b51d08b7bc3e9bcc49 -- typsphinx/template_registry.py`
(restoring the PRE-FIX module while keeping the new test module unchanged), run the
selector, then `git checkout HEAD -- typsphinx/template_registry.py` (restoring the
committed POST-FIX module) and run the identical selector again. This measurement was
re-run once against the final `HEAD` (after the `fix(60-04)` follow-up commit) to keep
the evidence anchored to the commit the plan actually ships.

PRE-FIX run (`grep -c 'quote_path(' typsphinx/template_registry.py` → `0` at this
point):

```
============================= test session starts ==============================
collected 5 items / 3 deselected / 2 selected

tests/test_template_registry_path_quoting_gate.py ..                     [100%]

======================= 2 passed, 3 deselected in 0.12s ========================
```

POST-FIX run (`grep -c 'quote_path(' typsphinx/template_registry.py` → `2` at this
point, confirming the correct commit was restored):

```
============================= test session starts ==============================
collected 5 items / 3 deselected / 2 selected

tests/test_template_registry_path_quoting_gate.py ..                     [100%]

======================= 2 passed, 3 deselected in 0.20s ========================
```

**The two transcripts are identical (`2 passed, 3 deselected`) — the excluded
type-check branch's behaviour is UNCHANGED by MSG-05's fix.** `git status --porcelain
typsphinx/` was empty after the final `git checkout HEAD` restore, confirming the
temporary checkout left no residue.

## GREEN

Command: `uv run pytest tests/test_template_registry_path_quoting_gate.py -q`
(post-fix, HEAD commit `7b1c4e3c`, following the comment-only `fix(60-04)` after
`623d023f`)

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-abd9ae6b18abb7125
configfile: pyproject.toml
plugins: cov-7.1.0
collected 5 items

tests/test_template_registry_path_quoting_gate.py .....                  [100%]

============================== 5 passed in 0.15s ===============================
```

All 5 tests across the three classes are GREEN: both RED-shape-1 tests (doubled
backslash), the RED-shape-2 test (leaked `PosixPath(...)` wrapper), and both exclusion-
control tests (which stayed green throughout, per the two-tree measurement above).

Command: `uv run pytest tests/test_template_registry.py -q` (zero edits to this file)

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-abd9ae6b18abb7125
configfile: pyproject.toml
plugins: cov-7.1.0
collected 76 items

tests/test_template_registry.py ........................................ [ 52%]
....................................                                     [100%]

============================== 76 passed in 0.70s ==============================
```

Full-suite, black, mypy and the AST census guard were also re-run green after task 2's
fix (verbatim tails recorded in task 3's `## Zero test edits (measured)` section):
`uv run pytest -q` (1499 passed, 5 skipped); `uv run black --check .` (351 files
unchanged); `uv run mypy typsphinx/` (no issues found in 9 source files);
`uv run pytest tests/test_repr_census_guard.py -q` (4 passed).

No mypy narrowing was needed at either routed call site — the surrounding
`isinstance(template, (str, os.PathLike))` guard (the `if` the `elif` branch follows)
already establishes the narrowed type before either `quote_path(template)` call, so
`quote_path()`'s own signature needed no widening.

## Known gate gaps

Every routed interpolation in this module has a behavioural gate, named below:

- `typsphinx/template_registry.py:440` (the CONF-17 violation message's `template`) —
  gated by `TestRegistryTemplatePathQuoting::test_conf17_violation_message_has_no_doubled_separator`.
- `typsphinx/template_registry.py:453` (the existence-check message's `template`) —
  gated by `TestRegistryTemplatePathQuoting::test_existence_check_message_has_no_doubled_separator`
  (backslash-doubling half) and by
  `TestRegistryPathLikeTemplateNoClassWrapper::test_pathlike_template_existence_message_leaks_no_class_wrapper`
  (`PosixPath(...)` class-name-wrapper half — the same source line, exercised through
  the `Path`-typed branch instead of the `str`-typed branch).

No routed interpolation in this module is ungated. The deliberately-EXCLUDED
type-check message at `typsphinx/template_registry.py:420` is not a routed
interpolation, so it needs no routing gate — its own SC#3 exclusion control is
`TestRegistryTypeCheckMessageStaysReprQuoted` (both methods), which is covered above.

## RED-first ledger

MSG-05 closes with two independent RED shapes recorded FAILING against the unfixed
tree BEFORE any product-code edit, per D-12:

| RED shape | Site | Command | Result recorded in |
|---|---|---|---|
| 1. Doubled backslash (`str` template) | CONF-17 violation message (`:440` post-fix) and existence-check message (`:453` post-fix) | `uv run pytest tests/test_template_registry_path_quoting_gate.py -q` | `## RED shape 1 — doubled backslash (str template)` above — both `TestRegistryTemplatePathQuoting` methods failed with `assert not doubled` AssertionErrors showing 3 and 6 doubled-backslash runs respectively |
| 2. Leaked `pathlib` class-name wrapper (`Path` template) | existence-check message (`:453` post-fix) | `uv run pytest tests/test_template_registry_path_quoting_gate.py -q` | `## RED shape 2 — leaked class-name wrapper (Path template)` above — `TestRegistryPathLikeTemplateNoClassWrapper`'s single method failed with `'PosixPath' is contained here` |

Both RED transcripts are pasted verbatim in their own sections above, each with its
exact command and the plan base SHA (`1118199a577533f598a799b51d08b7bc3e9bcc49`) at
which they were recorded. GREEN is recorded in `## GREEN` above, after task 2's fix
(`feat(60-04)` commit `623d023f`, followed by the comment-only `fix(60-04)` commit
`7b1c4e3c`): all 5 tests across the three classes pass.

## Edge reachability

**Claim 1 — the empty-value edge is structurally unreachable at both routed sites.**
Source (`typsphinx/template_registry.py`, the `elif template:` guard immediately
following the type-check `if`):

```python
if template and not isinstance(template, (str, os.PathLike)):
    failures.append(...)
elif template:
    ...  # both routed sites live inside this branch
```

`elif template:` is gated on TRUTHINESS (the module's own established convention,
documented in the comment block immediately above the `if`: "`template: None` / `""` /
`0` / `[]` resolving exactly as they do today, unchanged"). An empty string, `None`,
`0`, or `[]` is falsy, so neither the `if` nor the `elif` branch executes for it at
all — the whole validation block is skipped, and `quote_path()` is never called with
an empty (or any other falsy) value from this module. This is proven by an EXISTING,
unmodified control test: `tests/test_template_registry.py`'s
`test_falsy_template_field_still_resolves_verbatim` (parametrized over
`[None, "", 0, []]`) asserts the registry resolves without raising for every one of
those values — which is only possible if the `elif` branch (where both routed
`quote_path()` calls live) never runs for them.

**Claim 2 — the wrong-type edge is structurally unreachable at both routed sites.**
Source (the `if`/`elif` pair above, restated): the `if` branch's condition is
`template and not isinstance(template, (str, os.PathLike))` — i.e. "truthy AND NOT
(`str` or `os.PathLike`)". The `elif` branch (where both routed sites live) therefore
executes ONLY when that condition is false while `template` is still truthy, which
by De Morgan's law means: `not template` (excluded by Claim 1) OR
`isinstance(template, (str, os.PathLike))`. Since the `elif`'s own guard `elif
template:` additionally requires truthiness, the ONLY way to reach the `elif` body is
`template` truthy AND `isinstance(template, (str, os.PathLike))` true. A `bytes`,
`list`, or `int` value can therefore never reach either routed `quote_path()` call
from this module — it is caught by the `if` branch's type check first (and reported
via the deliberately-excluded `!r` message at `:420`), never falling through to the
`elif`. This is proven by the existing, unmodified control tests
`test_non_path_template_field_raises_extension_error_not_typeerror` and
`test_bytes_template_field_raises_extension_error_not_typeerror` in
`tests/test_template_registry.py`, plus this plan's own
`TestRegistryTypeCheckMessageStaysReprQuoted` (both methods) — all of which observe
the `if` branch firing for exactly these types, never the `elif`.

**Claim 3 — the CONF-17 and existence checks are structurally independent.** Source
(`typsphinx/template_registry.py`, inside the `elif template:` body):

```python
if _violates_conf17(template_abs_path, srcdir):
    failures.append(...)  # CONF-17
if not os.path.isfile(template_abs_path):
    failures.append(...)  # existence
```

These are two separate `if` statements, not an `if`/`elif` pair — neither is
conditioned on the other's outcome, so a `template` value that both violates CONF-17
AND names a nonexistent file appends BOTH failure strings to the same accumulated
`failures` list, which is then joined with `"; "` and raised in one `ExtensionError`
(D-09). This is proven both by an existing, unmodified test
(`test_conf17_and_not_found_both_reported_in_one_raise`, which asserts both `"CONF-17"`
and `"does not exist"` appear in the same raised message) and by this plan's own
`TestRegistryTemplatePathQuoting::test_conf17_violation_message_has_no_doubled_separator`,
whose constructed shape (a bare Windows-shaped filename component) deliberately fires
BOTH checks at once and asserts on the resulting `"2 invalid definition(s)"` combined
message (visible in the RED-shape-1 transcript above).

## Zero test edits (measured)

Command: `git diff --name-status 1118199a577533f598a799b51d08b7bc3e9bcc49..HEAD -- tests/`

```
A	tests/test_template_registry_path_quoting_gate.py
```

Every line begins with `A` (added) — this plan added exactly one new test file and
modified zero existing test files.

Command: `uv run pytest tests/test_template_registry.py -q` (green tail, zero edits to
this file):

```
collected 76 items

tests/test_template_registry.py ........................................ [ 52%]
....................................                                     [100%]

============================== 76 passed in 0.70s ==============================
```

The two assertions this plan's SC#3 falsification gate depends on —
`test_non_path_template_field_raises_extension_error_not_typeerror`'s
`assert repr(["a", "b"]) in message` (line 832, per `tests/test_repr_census_guard.py`'s
own recorded allowlist) and
`test_bytes_template_field_raises_extension_error_not_typeerror`'s
`assert repr(b"base.typ") in message` (line 847, same allowlist) — are GREEN
UNMODIFIED. They are the phase's falsification gate for accidental over-reach: if this
plan had accidentally routed the type-check message through `quote_path()`, both of
these pre-existing assertions would fail, since `quote_path()` raises `TypeError` on a
`list` or `bytes` value rather than rendering Python's own `repr()`.

Command: `uv run pytest tests/test_repr_census_guard.py -q` (green tail):

```
collected 4 items

tests/test_repr_census_guard.py ....                                     [100%]

============================== 4 passed in 0.61s ===============================
```

No entry was appended to `PASS_CRITERION_REPR_ALLOWLIST` — the census guard's
allowlist is unchanged from Phase 58's own recorded seven-site enumeration, confirming
this plan added no new `repr()`/`!r` pass-criterion site inside an `assert` test
expression anywhere under `tests/`.

`uv run pytest -q` was also re-run green after every product-code edit in this plan
(1499 passed, 5 skipped, matching the count recorded at the end of wave 1 in
`60-01-EVIDENCE.md`), and `uv run black --check .` / `uv run mypy typsphinx/` both
stayed clean throughout.

## Wave-3 handoff

Grep command scoped to this module: `grep -n '\!r' typsphinx/template_registry.py`
(the same discovery-authority command SC#2 requires wave 3 to re-run repo-wide).

- `grep -c 'quote_path(' typsphinx/template_registry.py` → **2** (`:440`, `:453` —
  both inside the `elif template:` body, the CONF-17 violation message and the
  existence-check message respectively).
- `grep -cE '\{template\!r\}' typsphinx/template_registry.py` → **1**, at
  **`typsphinx/template_registry.py:420`** — the deliberately-excluded type-check
  message's `template` interpolation. This is the sole surviving `template` repr
  conversion in this module; it must remain `!r` after the phase, per SC#3.
- Identifier-valued names in this module that must still render through Python's
  `repr()` conversion (`!r`) after the phase (all currently `!r`, all unrouted by this
  plan, all confirmed still present via
  `grep -cE '\{key\!r\}' typsphinx/template_registry.py` → 15):
  - `key` (the primary registry-key variable, used throughout `resolve_template_registry()`
    and its helpers — every `f"registry key {key!r}..."` site).
  - `raw_key` (`:535`, the raw `typst_documents` entry's target-registry-key lookup).
  - `RESERVED_REGISTRY_KEY` (`:343`, the synthesized built-in `"typst"` key).
  - `declared` (`:307`, the raw non-`dict` `typst_document_templates` config value).
  - `raw_definition` (`:366`, the raw non-`dict` per-key definition value).
  - `sorted(registry.keys())` (`:537`, `:547` — the sorted list of registry keys
    rendered as a diagnostic summary; every element is itself an identifier-valued
    registry key, never a filesystem path).

## Ruff (deferred to CI)

`ruff check .` was NOT run as part of this plan's local verification. Reason: a
freshly-provisioned worktree venv (`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv
sync --extra dev`) pulls a generic-linux `ruff` wheel whose ELF the loader rejects on
this development sandbox (a known, previously-recorded NixOS-sandbox limitation — see
this project's own MEMORY.md note "NixOS sandbox test env": "uv は解消済み。ruff は未解消").
CI holds lint authority for this project (`CLAUDE.md`'s own commands section: `ruff
check .` runs there); this is an environment limitation, not a code defect, and no
code was "fixed" to work around it.
