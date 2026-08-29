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

## GREEN

(filled by task 2)

## Known gate gaps

(filled by task 3)
