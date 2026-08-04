# Phase 44 Plan 02: Gate Evidence — BLD-01 Non-Str Docname + D-03 Opt-Out Wording

All output below is transcribed verbatim from commands executed in this plan's own
session, against the worktree at
`/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a6a5cf7bb6242bf35`. No figure
is recalled from `44-CONTEXT.md`, `44-PATTERNS.md`, or any other planning document.

## 1. RED — the unchanged code

**Command:**
```
uv run python -m sphinx -b typstpdf -E tests/fixtures/non_str_docname_gate <build>
```

**Exit status:** `2`

**Traceback tail** (from the saved `sphinx-err-*.log`, showing the exception type and
the `posixpath.dirname` frame):
```
Traceback (most recent call last):
  File ".../sphinx/cmd/build.py", line 432, in build_main
    app.build(args.force_all, args.filenames)
  File ".../sphinx/application.py", line 442, in build
    self.builder.build_update()
  File ".../sphinx/builders/__init__.py", line 381, in build_update
    self.build(...)
  File ".../sphinx/builders/__init__.py", line 463, in build
    self.finish()
  File ".../typsphinx/builder.py", line 953, in finish
    relative_path = self._directory_preserving_relpath(docname, stem)
  File ".../typsphinx/builder.py", line 293, in _directory_preserving_relpath
    directory = posixpath.dirname(docname)
  File "<frozen posixpath>", line 178, in dirname
TypeError: expected str, bytes or os.PathLike object, not int
```

**`TypeError` in stderr:** PRESENT (`grep -c "TypeError"` → `1`)

**`master document(s) failed` in stderr:** ABSENT (`grep -c "master document(s) failed"` → `0`)

**Build directory contents before the process died** (`ls -la <build>`):
```
total 24
drwxr-xr-x 1 yuta users    80  8月  4 14:31 .
drwx------ 1 yuta users   212  8月  4 14:31 ..
drwxr-xr-x 1 yuta users    26  8月  4 14:31 .doctrees
-rw-r--r-- 1 yuta users  2438  8月  4 14:31 _template.typ
-rw-r--r-- 1 yuta users 16320  8月  4 14:31 index.pdf
-rw-r--r-- 1 yuta users   520  8月  4 14:31 index.typ
```

The valid master (`index`) is iterated first, so both `index.typ` and `index.pdf` were
already written to disk before the process died attempting the second, malformed entry
— the crash killed the whole `sphinx-build` process (bare `TypeError`, exit `2`)
rather than being reported as a scoped, aggregate failure. No `manual.typ` or
`manual.pdf` was ever produced.

## 2. GREEN — after the guard

**Command:**
```
uv run python -m sphinx -b typstpdf -E tests/fixtures/non_str_docname_gate <build>
```

**Exit status:** `2` (still non-zero — expected, one entry is malformed by design)

**typsphinx-authored stderr fragment (verbatim):**
```
WARNING: typst_documents entry has a non-str docname: 123 -- expected a str

Extension error!
...
sphinx.errors.ExtensionError: typstpdf: 1 master document(s) failed: 123: typst_documents entry has a non-str docname: 123 -- expected a str
```

**`TypeError` in stderr:** ABSENT (`grep -c "TypeError"` → `0`) — **inverted from section 1**

**`master document(s) failed` in stderr:** PRESENT (`grep -c "master document(s) failed"` → `2`) — **inverted from section 1**

**Build directory contents** (`ls -la <build>`):
```
total 24
drwxr-xr-x 1 yuta users    80  8月  4 14:33 .
drwx------ 1 yuta users   390  8月  4 14:33 ..
drwxr-xr-x 1 yuta users    26  8月  4 14:33 .doctrees
-rw-r--r-- 1 yuta users  2438  8月  4 14:33 _template.typ
-rw-r--r-- 1 yuta users 16320  8月  4 14:33 index.pdf
-rw-r--r-- 1 yuta users   520  8月  4 14:33 index.typ
```

`index.typ` and `index.pdf` are both present (the valid master still compiled), and no
`manual.typ` / `manual.pdf` exists for the bad entry's target name.

**Passing pytest output:**
```
$ uv run python -m pytest tests/test_non_str_docname_gate.py tests/test_missing_and_malformed_master_gate.py tests/test_pdf_generation.py -q
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a6a5cf7bb6242bf35
configfile: pyproject.toml
plugins: cov-7.1.0
collected 33 items

tests/test_non_str_docname_gate.py .                                     [  3%]
tests/test_missing_and_malformed_master_gate.py ..                       [  9%]
tests/test_pdf_generation.py ..............................              [100%]

============================== 33 passed in 1.82s ==============================
```
