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

Post-fix commit SHA and both locale runs are appended below once the fix and tests
land (Task 1 / Task 2 completion, in-place edit to this section).

<!-- gsd:write-continue -->
