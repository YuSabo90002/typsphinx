# 57-11: Message-Fix Evidence

Evidence for plan `57-11` — fixing the Windows-only `repr()`-escaping defect at the three
pre-write template-path refusal sites in `typsphinx/builder.py`, after two full CI matrix
dispatches (`31956166848`, then `31959060298`) both failed the same assertion on both
`windows-latest` lanes for the same underlying reason.

**This plan has not observed a green Windows lane.** Everything below is local, POSIX-host
evidence: the census, the before/after reproduction of the escaping behaviour using a
hand-built Windows-shaped string, the byte-identical-on-POSIX argument, and the task-2
RED/GREEN demonstration. No CI has been dispatched from this plan. Windows-lane confirmation is
recorded as still pending in `.planning/WINDOWS.md` entries 9 and 10, which this plan updates
but deliberately does not close.

## 1. The `!r` census

Every `!r` interpolation under `typsphinx/`, enumerated by `grep -n '!r' typsphinx/*.py` and
classified by inspecting the surrounding code (not by variable name alone — e.g.
`translator.py`'s `path[0]!r`/`path[-1]!r` are docnames despite the variable being named
`path`).

**Classification rule:** *path-valued* — the interpolated value is a filesystem path or path
fragment (can contain `os.sep`, so `repr()` escapes it on Windows). *identifier-valued* — a
registry key, docname, config tuple, or similar, where `!r`'s quoting is correct and intended
and there is nothing for `repr()` to escape (registry keys are barred from containing a path
separator by `template_registry.py`'s own validation).

| File | Line(s) (pre-57-11) | Interpolated value(s) | Classification | In the three named refusal sites? | Disposition |
|---|---|---|---|---|---|
| `builder.py` | 330 | `key` | identifier | — | kept `!r` |
| `builder.py` | 331 | `resolved_path` | **path** | srcdir-ancestor refusal | **FIXED** (task 1) |
| `builder.py` | 333 | `srcdir` | **path** | srcdir-ancestor refusal | **FIXED** (task 1) |
| `builder.py` | 624-625 | `docname` (×2) | identifier | — | kept `!r` (warning log) |
| `builder.py` | 630 | `target`, `fallback` | path | — | out of scope (warning log; filed as todo) |
| `builder.py` | 645, 658 | `docname` (×2 each) | identifier | — | kept `!r` (warning log) |
| `builder.py` | 875 | `relpath` | path | — | out of scope (v0.8.0-era output-path collision family; filed as todo) |
| `builder.py` | 891 | `docname` | identifier | — | kept `!r` |
| `builder.py` | 896-898 | `docname`, `content_relpath`, `TEMPLATE_OUTPUT_DIR` | path (content_relpath, TEMPLATE_OUTPUT_DIR); identifier (docname) | — | out of scope (v0.8.0-era family; filed as todo) |
| `builder.py` | 921 | `entry` | identifier (config tuple) | — | kept `!r` |
| `builder.py` | 931-932 | `docname`, `target` | identifier (docname); path (target) | — | out of scope (v0.8.0-era family; filed as todo) |
| `builder.py` | 939-941 | `docname`, `target`, `wrapper_relpath`, `TEMPLATE_OUTPUT_DIR` | mixed, path values present | — | out of scope (v0.8.0-era family; filed as todo) |
| `builder.py` | 948 | `relpath` | path | — | out of scope (v0.8.0-era family; filed as todo) |
| `builder.py` | 1210-1211 | `declared_key`, `RESERVED_REGISTRY_KEY` | identifier | — | kept `!r` |
| `builder.py` | 1219 | `declared_key` | identifier | — | kept `!r` |
| `builder.py` | 1295 | `key` | identifier | templates_path collision refusal | kept `!r` |
| `builder.py` | 1296 | `bundle_dir` | **path** | templates_path collision refusal | **FIXED** (task 1) |
| `builder.py` | 1298 | `raw_tp_entry` | **path** | templates_path collision refusal | **FIXED** (task 1) |
| `builder.py` | 1299 | `resolved_tp_entry` | **path** | templates_path collision refusal | **FIXED** (task 1) |
| `builder.py` | 1311 | `key` | identifier | — | kept `!r` (aggregate summary) |
| `builder.py` | 1706 | `resolved_uri` | path | — | out of scope (warning log; filed as todo) |
| `builder.py` | 1707 | `key` (synthesized namespace key, basename-only, no separator) | identifier-ish | — | kept `!r` (warning log) |
| `builder.py` | 1987 | `key` | identifier | — | kept `!r` (debug log) |
| `builder.py` | 1994-1995 | `key`, `src_file`, `dest_file` | identifier (key); path (src_file, dest_file) | — | out of scope (bundle-copy I/O failure; filed as todo) |
| `builder.py` | 2004-2005 | `key`, `template_filename`, `src_dir`, `dest_dir` | identifier (key); path (rest) | — | out of scope (bundle-copy I/O failure; filed as todo) |
| `builder.py` | 2163 | `existing[0]` | identifier | bundle-destination collision refusal | kept `!r` |
| `builder.py` | 2164 | `key` | identifier | bundle-destination collision refusal | kept `!r` |
| `builder.py` | 2165 | `dest_dir` | **path** | bundle-destination collision refusal | **FIXED** (task 1) |
| `builder.py` | 2173 | `key` | identifier | — | kept `!r` (aggregate summary) |
| `builder.py` | 2301 | `doc_tuple` | identifier (config tuple) | — | kept `!r` (warning log) |
| `builder.py` | 2314 | `docname` | identifier | — | kept `!r` |
| `builder.py` | 2329 | `doc_tuple` | identifier | — | kept `!r` |
| `builder.py` | 2346 | `docname` | identifier | — | kept `!r` |
| `writer.py` | 154-155 | `entry[0]` (docname), `value`, `default` (title/author string, not a path) | identifier | — | kept `!r` |
| `writer.py` | 511-513 | `docname`, `wrapper_relative_dir`, `include_path`, `template_file` | identifier (docname); path (rest) | — | out of scope (debug log; filed as todo) |
| `template_registry.py` | 113, 115, 118, 123, 127, 129, 132 | `key` | identifier | — | kept `!r` (registry-key validation) |
| `template_registry.py` | 305 | `declared` | identifier (declared count/shape) | — | kept `!r` |
| `template_registry.py` | 332, 340-341, 363-364, 376 | `key`, `raw_definition` | identifier | — | kept `!r` |
| `template_registry.py` | 410, 422, 433 | `key` (identifier), `template` (**path**) | mixed | — | out of scope (declared-template validation; filed as todo — same defect SHAPE, different file/validation path) |
| `template_registry.py` | 514, 516, 524, 526 | `raw_key`, `key` | identifier | — | kept `!r` |
| `template_engine.py` | 176 | `sphinx_language` | identifier (language code, not a path) | — | kept `!r` |
| `template_engine.py` | 568 | `key` (`typst_elements` key) | identifier | — | kept `!r` |
| `translator.py` | 417, 420 | `master_docname`, `path[0]`, `path[-1]` | identifier (all three are docnames — `path` here is a `Tuple[str, ...]` of docnames, not a filesystem path, despite the variable name) | — | kept `!r` |
| `translator.py` | 5504 | `edge_key` | identifier | — | kept `!r` |

**Result:** 4 path-valued sites fixed (task 1: 3 in the named refusal family, one of which
(`bundle_dir`) also required its two siblings `raw_tp_entry`/`resolved_tp_entry` at the same
call site — that is the "3 named refusal sites" from the plan, expanding to the interpolations
listed above). All other path-valued `!r` sites are filed in the deferred todo
(`.planning/todos/pending/2026-08-17-repr-escaped-paths-in-remaining-user-facing-messages.md`).
Every identifier-valued `!r` is untouched.

## 2. Local Windows-shape reproduction — before and after

`repr()` escapes each backslash; a `'{value}'` f-string does not. Reproduced directly against
`_conf17_violation_message()` (the shared helper used at the srcdir-ancestor site and reused
inside both `_validate_used_template_paths()` and `_copy_used_template_bundles()` for their own
CONF-17 checks).

**Before the fix** (reconstructed with the pre-57-11 `!r` form, for comparison — not committed):

```
$ uv run python -c "
win_bundle = 'C:\\\\Users\\\\runner\\\\project\\\\_templates\\\\nested'
srcdir = 'C:\\\\Users\\\\runner\\\\project\\\\source'
old_msg = (
    f\"typst_document_templates: registry key {'mykey'!r}'s \"
    f\"resolved template {win_bundle!r} has a \"
    'parent directory that is srcdir itself, or an '
    f\"ancestor of srcdir ({srcdir!r}) -- put \"
    'the template in its own subdirectory (CONF-17, A-01)'
)
print(old_msg)
import re
print('backslash run lengths:', [len(r) for r in re.findall(r'\\\\+', old_msg)])
"
typst_document_templates: registry key 'mykey''s resolved template 'C:\\Users\\runner\\project\\_templates\\nested' has a parent directory that is srcdir itself, or an ancestor of srcdir ('C:\\Users\\runner\\project\\source') -- put the template in its own subdirectory (CONF-17, A-01)
backslash run lengths: [2, 2, 2, 2, 2, 2, 2, 2, 2]
```

Every backslash run is length 2 — the doubled-escaping defect, reproduced.

**After the fix** (the actual, committed `_conf17_violation_message()`):

```
$ uv run python -c "
from typsphinx.builder import _conf17_violation_message
win_bundle = 'C:\\\\Users\\\\runner\\\\project\\\\_templates\\\\nested'
srcdir = 'C:\\\\Users\\\\runner\\\\project\\\\source'
msg = _conf17_violation_message('mykey', win_bundle, srcdir)
print(msg)
import re
print('backslash run lengths:', [len(r) for r in re.findall(r'\\\\+', msg)])
"
typst_document_templates: registry key 'mykey''s resolved template 'C:\Users\runner\project\_templates\nested' has a parent directory that is srcdir itself, or an ancestor of srcdir ('C:\Users\runner\project\source') -- put the template in its own subdirectory (CONF-17, A-01)
backslash run lengths: [1, 1, 1, 1, 1, 1, 1, 1, 1]
```

Every backslash run is now length 1 — the platform separator, unescaped. This is the fix.

## 3. Byte-identical-on-POSIX argument

`repr('_templates')` and `"'{}'".format('_templates')` both yield `'_templates'` — there is
nothing for `repr()` to escape when the string contains no backslash, which is always true on
POSIX (`os.sep == '/'`). The full local suite (see §4) passes with **zero test file edits** in
task 1's commit, which is the actual proof: if POSIX output had changed, at least one existing
assertion in `tests/test_templates_path_collision_gate.py`,
`tests/test_typst_documents_collision_gate.py`, or `tests/test_template_registry.py` would have
had to change to keep passing, and none did.

## 4. Full local suite — task 1 (message fix only, zero test edits)

```
$ uv run python -m pytest -q
================= 1417 passed, 5 skipped in 122.70s (0:02:02) ==================
$ git diff --name-only -- tests/
(empty)
$ uv run ruff check .        # via nix-shell -p ruff --run "ruff check ." (see NixOS note below)
All checks passed!
$ uv run black --check .
All done! ✨ 🍰 ✨
339 files would be left unchanged.
$ uv run mypy typsphinx/
Success: no issues found in 8 source files
```

**NixOS note:** this environment's freshly-synced worktree `.venv/bin/ruff` is a generic-linux
ELF the NixOS stub loader rejects (`Could not start dynamically linked executable: ruff`) — a
known, previously-documented environmental hazard for this repo, unrelated to this plan's
change. Ran `ruff check .` via `nix-shell -p ruff --run "ruff check ."` instead (ruff 0.15.14
from nixpkgs), which produced the clean result above. `black` and `mypy` ran fine through
`uv run` directly.

## 5. 57-10's assertion now matches — confirmed, not reverted

`tests/test_templates_path_collision_gate.py`'s
`test_multi_relation_each_key_names_own_bundle_dir_and_own_entry` (plan 57-10's fix) asserts:

```python
beta_bundle_tail = str(Path("_templates") / "nested")
assert beta_bundle_tail in message, ...
```

On Windows, `str(Path("_templates") / "nested")` renders as `_templates\nested` — ONE
backslash. Before 57-11, the message embedded `{bundle_dir!r}`, whose `repr()` would have
doubled that separator to `_templates\\nested`, so 57-10's one-backslash assertion could NOT
have matched a live Windows run — it was correct in shape but blocked by the un-fixed defect
underneath it (exactly what `.planning/WINDOWS.md` entry 10 recorded). After 57-11, the message
embeds `'{bundle_dir}'` with no escaping, so the emitted backslash count now matches
`str(Path(...))`'s one-backslash form exactly. **This assertion was NOT reverted or re-edited by
57-11** — `git diff --name-only -- tests/` for task 1's commit is empty, and task 2's commit
only ADDS a new test class to this file, touching no existing assertion.

## 6. Task 2 — RED/GREEN demonstration (real product code, not a re-pasted format string)

Task 2 extracted the two inline refusal f-strings into their own functions
(`_templates_path_collision_message()`, `_bundle_destination_collision_message()`), mirroring
the pre-existing `_conf17_violation_message()` extraction, and wired them at their original call
sites (pure refactor — byte-identical message text, confirmed by the same zero-test-edit full
suite run in §4 after the refactor). `TestWindowsPathEscapingRegressionGuard` in
`tests/test_templates_path_collision_gate.py` calls all three real functions directly with a
hand-built Windows-shaped path string and asserts no backslash run longer than 1 survives.

**RED (temporarily reverted `_conf17_violation_message()` back to `!r`):**

```
$ uv run python -m pytest tests/test_templates_path_collision_gate.py -q -k "test_conf17_violation_message_does_not_double_backslashes" -v
FAILED tests/test_templates_path_collision_gate.py::TestWindowsPathEscapingRegressionGuard::test_conf17_violation_message_does_not_double_backslashes
E       AssertionError: Expected every backslash run to be a single unescaped separator, found a doubled/escaped run in:
E         "typst_document_templates: registry key 'mykey''s resolved template 'C:\\\\Users\\\\runner\\\\project\\\\_templates\\\\nested' has a parent directory that is srcdir itself, or an ancestor of srcdir ('C:\\\\Users\\\\runner\\\\project\\\\source') -- put the template in its own subdirectory (CONF-17, A-01)"
E       assert not ['\\\\', '\\\\', '\\\\', '\\\\', '\\\\', '\\\\', ...]
======================= 1 failed, 15 deselected in 0.05s =======================
```

**GREEN (restored the fix):**

```
$ uv run python -m pytest tests/test_templates_path_collision_gate.py -q -k "WindowsPathEscapingRegressionGuard"
tests/test_templates_path_collision_gate.py ....                         [100%]
======================= 4 passed, 12 deselected in 0.03s =======================
```

This demonstrates the guard fails when `!r` is reintroduced at a fixed site and passes once
restored — exercising the actual product function, not a duplicated format string (a duplicated
string would have kept passing through the revert, which is precisely the failure mode task 2
guards against).

**Honest limit** (also stated in the test module's docstring): these three functions never call
`os.path`/`ntpath` themselves — they only format a string they are handed. The test drives them
with a hand-built Windows-*shaped* string (literal backslashes), not a real `ntpath`-resolved
`pathlib.WindowsPath`, because there is no Windows host available to this suite. This is the
closest honest approximation available locally; it covers exactly the surface the `!r`-escaping
defect lives on (string formatting), and does not cover whether `ntpath.dirname()` /
`ntpath.join()` themselves would produce a different path shape on a real Windows host — that
remains covered only by an actual Windows CI run, which this plan has not observed.
