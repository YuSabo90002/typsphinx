# 53-08 RED Evidence — WR-01 (container shape) and WR-02 (`template` field shape)

Deliberately NOT named `53-VERIFICATION.md`, which `gsd-verifier` reserves and would
clobber (D-12).

## Base commit

Pre-fix commit SHA (unfixed `typsphinx/template_registry.py`, both WR-01 and WR-02
reproduced against it), measured with `git rev-parse HEAD`:

```
74eb4440ba8bc0dda6bed63e24b9aab6bb26d146
```

## WR-01 — truthy non-`dict` `typst_document_templates` container

### Pre-fix unit reproduction

Command:

```python
from typsphinx.template_registry import resolve_template_registry


class C:
    pass


c = C()
c.typst_document_templates = ["a", "b"]
resolve_template_registry(c, "/tmp/x")
```

Verbatim traceback (raw `AttributeError`, not this module's `ExtensionError`):

```
Traceback (most recent call last):
  File "<repro>", line 12, in <module>
    resolve_template_registry(c, "/tmp/x")
    ~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^
  File "typsphinx/template_registry.py", line 262, in resolve_template_registry
    all_keys = {key for key in declared.keys() if isinstance(key, str)}
                               ^^^^^^^^^^^^^
AttributeError: 'list' object has no attribute 'keys'
```

### Pre-fix falsy control

Command:

```python
from typsphinx.template_registry import resolve_template_registry


class C:
    pass


c = C()
c.typst_document_templates = []
r = resolve_template_registry(c, "/tmp/x")
print(sorted(r.keys()))
```

Output (resolves silently, no raise — the crash surface is exactly the truthy
non-`dict` case, per the `or {}` normalization on the preceding line):

```
['typst']
```

## WR-02 — truthy unusable `template` field

### Pre-fix unit reproduction

Command:

```python
from typsphinx.template_registry import resolve_template_registry


class C:
    pass


c = C()
c.typst_document_templates = {"key": {"template": ["a", "b"]}}
resolve_template_registry(c, "/tmp/x")
```

Verbatim traceback (raw `TypeError`, not this module's `ExtensionError`):

```
Traceback (most recent call last):
  File "<repro>", line 12, in <module>
    resolve_template_registry(c, "/tmp/x")
  File "typsphinx/template_registry.py", line 340, in resolve_template_registry
    template_abs_path = os.path.join(srcdir, template)
                         ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^
TypeError: join() argument must be str, bytes, or os.PathLike object, not 'list'
```

### Pre-fix falsy/`Path` controls

Command (falsy `template` — `[]` — resolves and stores verbatim):

```python
from typsphinx.template_registry import resolve_template_registry


class C:
    pass


c = C()
c.typst_document_templates = {"key": {"template": []}}
e = resolve_template_registry(c, "/tmp/x")["key"]
print(e.template)
```

Output:

```
[]
```

Command (a `pathlib.Path` `template` resolves end-to-end today, control for D-07's
"do not newly reject a working shape"):

```python
import pathlib
from typsphinx.template_registry import resolve_template_registry


class C:
    pass


c = C()
srcdir_path = pathlib.Path("/tmp/wr02_control_srcdir")
srcdir_path.mkdir(exist_ok=True)
(srcdir_path / "sub").mkdir(exist_ok=True)
tpl = srcdir_path / "sub" / "tpl.typ"
tpl.write_text("")
c.typst_document_templates = {"key": {"template": pathlib.Path("sub/tpl.typ")}}
e = resolve_template_registry(c, str(srcdir_path))["key"]
print(type(e.template), e.template)
```

Output:

```
<class 'pathlib.PosixPath'> sub/tpl.typ
```

This is measured — not transcribed from `53-REVIEW.md`, which is a starting point,
not a measurement.

## Post-fix section

Both guards land in `typsphinx/template_registry.py`:

- WR-01: `isinstance(declared, dict)` checked immediately after
  `declared = getattr(config, "typst_document_templates", None) or {}` and BEFORE the
  `all_keys` comprehension, raising this module's own `ExtensionError` naming
  `typst_document_templates` and `repr(declared)` — pre-accumulation, since the
  accumulate loop's own precondition (`declared` is iterable as a mapping) does not
  hold when the container itself is the wrong shape.
- WR-02: `isinstance(template, (str, os.PathLike))` checked inside the existing
  truthy `template` branch of the accumulate loop, joining the same `failures` list
  as every other definition-level check (D-09) — accumulated, not pre-accumulation.

### Post-fix reproduction re-runs (both now raise this module's own `ExtensionError`)

WR-01 repro, re-run against the fixed code:

```
ExtensionError: typst_document_templates must be a dict mapping registry key to definition, got ['a', 'b']
```

WR-02 repro, re-run against the fixed code:

```
ExtensionError: typst_document_templates: 1 invalid definition(s): registry key 'key''s template ['a', 'b'] must be a path string or os.PathLike, not a list
```

### Two-locale proof

`uv run pytest tests/test_registry_container_shape_gate.py tests/test_template_registry.py -q`
(ambient locale, ja_JP): `85 passed`.

`LC_ALL=C uv run pytest tests/test_registry_container_shape_gate.py tests/test_template_registry.py -q`:
`85 passed` — identical count, confirming no assertion depends on the ambient locale.

### Post-fix commit SHAs

- WR-01 (Task 1): `6846a190` — `feat(53-08): close WR-01 -- typo'd typst_document_templates
  container fails cleanly`.
- WR-02 (Task 2): recorded in a small follow-up docs commit immediately after the Task 2
  feat commit lands, naming that commit's own SHA (both are, by construction, distinct
  from the pre-fix base `74eb4440ba8bc0dda6bed63e24b9aab6bb26d146`).

### Full-suite and toolchain checks (Task 2 acceptance criteria)

- `uv run pytest tests/ -q` → `1270 passed, 5 skipped`.
- `uv run pytest tests/test_preview_version_sync.py -q` → `3 passed`.
- `grep -rl "_template\.typ" tests/ | wc -l` → **33**, not the plan's documented "32,
  the phase-start count". Re-measured directly against the pre-fix base commit
  (`git grep -l "_template\.typ" 74eb4440ba8bc0dda6bed63e24b9aab6bb26d146 -- tests/ | wc -l`
  also returns 33) — the count was already 33 before this plan's Task 1 or Task 2 touched
  anything, because `tests/test_registry_prewrite_validation_gate.py` (added by plan 53-06)
  already matches the pattern. Neither this plan's new files
  (`tests/test_registry_container_shape_gate.py`, the `registry_container_shape_gate`
  fixture) nor its edits to `tests/test_template_registry.py` reference `_template.typ` at
  all. The "32" figure in `53-08-PLAN.md`'s acceptance criteria is stale documentation
  from before plan 53-06 landed, not a regression introduced here.
- `uv run black --check .` → `310 files would be left unchanged` (clean, after
  reformatting the new `tests/test_registry_container_shape_gate.py` to match).
- `uv run mypy typsphinx/` → `Success: no issues found in 7 source files`.
- `uv run ruff check .` → `Could not start dynamically linked executable: ruff` (the
  recorded NixOS generic-linux ELF hazard; CLAUDE.md's own guidance is to record this
  verbatim rather than claim a lint pass — plan 53-10's dispatched CI run is this phase's
  authoritative lint evidence).
