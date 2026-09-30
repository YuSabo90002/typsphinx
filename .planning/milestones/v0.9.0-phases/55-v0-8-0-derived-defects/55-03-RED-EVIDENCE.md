# Phase 55 Plan 03: RED Evidence — BLD-09 and IMG-03

**Pre-fix commit (this worktree's HEAD before any `typsphinx/` edit):**

```
40b92fc6ee6c3f53a6ec3306778d0c895958a797
```

Captured via `git rev-parse HEAD` before any file under `typsphinx/` was touched. Confirmed with
`git status --porcelain typsphinx/` producing no output at the same point in time.

**Gate location (grepped, not cited from any prior document):**

```
$ grep -n "path.isabs(resolved_uri)" typsphinx/builder.py
1561:        if path.isabs(resolved_uri):
```

Both `.planning/ROADMAP.md` SC#4 and the originating todo cite `builder.py:910`. That number was
already stale before this plan started — the gate is measured here at `:1561` on this worktree's
pre-fix tree. No edit in this plan is anchored on either number; the call site is located by
grepping the literal code above every time it is needed.

---

## BLD-09 — unit level, platform-independent string shape (D-05)

**Command:**

```
uv run pytest tests/test_builder.py -k "driveless_absolute or unc_absolute or relative_uri_is_not" -v
```

**Result: 2 failed, 1 passed, 28 deselected.**

**Verbatim failure tail:**

```
        doc = nodes.document("", reporter=reporter)
        doc.settings = states.Struct()
        doc.settings.env = None
        doc.settings.language_code = "en"
        doc.settings.strict_visitor = False

        img = nodes.image(uri=abs_uri, candidates={"*": abs_uri})
        doc += img

        with caplog.at_level("WARNING"):
            builder.post_process_images(doc)

>       assert img["uri"] != abs_uri
E       AssertionError: assert '\\\\typsphinx_test_55_03_server\\share\\chart.png' != '\\\\typsphinx_test_55_03_server\\share\\chart.png'

tests/test_builder.py:755: AssertionError
=========================== short test summary info ============================
FAILED tests/test_builder.py::test_post_process_images_driveless_absolute_uri_reaches_rehome_branch - AssertionError: assert '\\typsphinx_test_55_03_driveless\\chart.png' != '\\typsphinx_test_55_03_driveless\\chart.png'
FAILED tests/test_builder.py::test_post_process_images_unc_absolute_uri_reaches_rehome_branch - AssertionError: assert '\\\\typsphinx_test_55_03_server\\share\\chart.png' != '\\\\typsphinx_test_55_03_server\\share\\chart.png'
================== 2 failed, 1 passed, 28 deselected in 0.16s ==================
```

Both the driveless-absolute and UNC-shaped literals leave `img["uri"]` completely unrewritten
(`img["uri"] != abs_uri` fails because they ARE still equal — the rehome branch was never
entered). The control test (`relative_uri_is_not_treated_as_absolute`) is the `1 passed` — it must
stay green both before and after the fix.

---

## IMG-03 — unit level (D-05)

**Command:**

```
uv run pytest tests/test_builder.py -k "same_basename or pure_function_of_uri" -v
```

**Result: 1 failed, 1 passed, 29 deselected.**

**Verbatim failure tail:**

```
        img_a = nodes.image(uri=abs_uri_a, candidates={"*": abs_uri_a})
        img_b = nodes.image(uri=abs_uri_b, candidates={"*": abs_uri_b})
        doc += img_a
        doc += img_b

        with caplog.at_level("WARNING"):
            builder.post_process_images(doc)

        key_a, key_b = img_a["uri"], img_b["uri"]

>       assert key_a != key_b
E       AssertionError: assert '_typst_converted/shared.png' != '_typst_converted/shared.png'

tests/test_builder.py:844: AssertionError
------------------------------ Captured log call -------------------------------
WARNING  sphinx.typsphinx.builder:logging.py:138 WARNING: could not rehome image URI '/typsphinx_test_55_03_setA/shared.png' relative to the doctree directory -- relocated to '_typst_converted/shared.png'
WARNING  sphinx.typsphinx.builder:logging.py:138 WARNING: could not rehome image URI '/typsphinx_test_55_03_setB/shared.png' relative to the doctree directory -- relocated to '_typst_converted/shared.png'
=========================== short test summary info ============================
FAILED tests/test_builder.py::test_post_process_images_escape_same_basename_keys_stay_distinct - AssertionError: assert '_typst_converted/shared.png' != '_typst_converted/shared.png'
================== 1 failed, 1 passed, 29 deselected in 0.14s ==================
```

Two absolute URIs in different directories (`/typsphinx_test_55_03_setA/shared.png` and
`/typsphinx_test_55_03_setB/shared.png`), both escaping `doctreedir`, collapse onto the identical
key `_typst_converted/shared.png` — the second document's tracked entry silently overwrites the
first's (`self.images` gains only one entry, confirmed by the two distinct WARNING log lines above
both naming the SAME relocated key). `test_post_process_images_escape_key_is_pure_function_of_uri`
is the `1 passed` — it is not RED by itself (the pre-fix basename-only key is already a
deterministic pure function of `resolved_uri`), only the distinctness test is; this matches the
plan's own note that the purity test's RED-ness is conceptual, not literal, at this stage.

---

## Predicate measurement (input to the Task 2 decision)

Re-measured in THIS worktree (Python 3.13.13, pre-fix tree at the SHA above) via:

```
uv run python /tmp/.../predicate_measure.py
```

using the inline snippet:

```python
import ntpath
import posixpath
from typsphinx.builder import _escapes_outdir, _is_drive_qualified

shapes = {
    "driveless-absolute": "\\typsphinx_test\\chart.png",
    "drive-qualified": "C:\\typsphinx_test\\chart.png",
    "posix-absolute": "/abs/chart.png",
    "unc": "\\\\server\\share\\chart.png",
    "ordinary-relative": "images/chart.png",
}

for name, uri in shapes.items():
    normalized = uri.replace("\\", "/")
    ntabs = ntpath.isabs(uri)
    pxabs = posixpath.isabs(uri)
    dq = _is_drive_qualified(uri)
    sc4 = pxabs or dq
    norm_disj = posixpath.isabs(normalized) or _is_drive_qualified(normalized)
    print(name, ntabs, pxabs, dq, sc4, norm_disj)

print(_escapes_outdir("\\typsphinx_test\\chart.png"))
print(ntpath.join("C:\\build\\out", "\\typsphinx_test\\chart.png"))
```

**Raw output:**

```
shape                | os-native(Win)  | posixpath.isabs   | drive_qualified  | SC4-literal  | backslash-normalized
-------------------------------------------------------------------------------------------------------------------
driveless-absolute   | False           | False             | False            | False        | True
drive-qualified      | True            | False             | True             | True         | True
posix-absolute       | False           | True              | False            | True         | True
unc                  | True            | False             | False            | False        | True
ordinary-relative    | False           | False             | False            | False        | False

_escapes_outdir('\\typsphinx_test\\chart.png') = False

ntpath.join('C:\\build\\out', '\\typsphinx_test\\chart.png') = 'C:\\typsphinx_test\\chart.png'
```

**Reading this table:**

- **SC#4's literal predicate** (`posixpath.isabs(...) or _is_drive_qualified(...)`, applied to the
  raw URI) evaluates **False** for both the driveless-absolute shape and the UNC shape — the exact
  two shapes BLD-09's own requirement text names as needing to reach the rehome branch. It only
  fires for drive-qualified and POSIX-absolute, which are not what BLD-09 describes.
- **The backslash-normalized version of the same idiom** (normalize `\` to `/` first, then apply
  the identical disjunction) evaluates **True** for driveless-absolute, drive-qualified,
  POSIX-absolute, and UNC, and **False** for the ordinary-relative control — matching BLD-09's
  stated behaviour exactly, with the widening bounded by the control case staying False.
- `_escapes_outdir()` — the sibling function whose own inline comment already documents the
  platform-independence idiom — is measured here to ALSO return `False` for the driveless-absolute
  stem, because it splits the stem into segments and checks `posixpath.isabs(stem)` on the RAW
  (not backslash-normalized) input for its own absolute-path branch. This is the sibling latent gap
  Task 3 files as a follow-up todo rather than fixing in this plan.
- `ntpath.join("C:\\build\\out", "\\typsphinx_test\\chart.png")` returns
  `'C:\\typsphinx_test\\chart.png'` — the join **silently discards** `outdir`'s subdirectory
  (`out`) once the second argument is rooted, landing the result at `C:\typsphinx_test\chart.png`
  instead of anywhere under `C:\build\out`. This is the measured mechanism behind the `high`
  severity T-55-05 threat-register entry: if the driveless-absolute gate stays skipped, an
  unrewritten rooted `img["uri"]` reaches `copy_image_files()`'s destination join and the file is
  written at (effectively) the drive root, not under the configured output directory.

This table is what Task 2's blocking checkpoint decision rests on.
