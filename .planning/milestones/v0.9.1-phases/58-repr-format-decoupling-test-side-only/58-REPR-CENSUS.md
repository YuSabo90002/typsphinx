# Phase 58: `repr()`/`!r` Census — `tests/`

This document records the enumeration Phases 59 and 60 check their zero-test-edit claim against,
per milestone binding constraint 9. It is a planning artifact, not a test — nothing here decides a
GREEN or RED verdict. The enumeration it records is backed at run time by
`tests/test_repr_census_guard.py` (D-09), which asserts the same seven-site allowlist via a live
AST sweep.

## How this census was derived

This census comes from a **whole-tree sweep of `tests/**/*.py`**, never from the two sites MSG-01
names (`tests/test_out02_escape_target_gate.py:134` and `tests/test_builder.py:598`). Deriving the
enumeration set from those two known sites would inherit the very blind spot the census exists to
close — a framing error this project has already paid for once (D-08).

The figures below were produced by `tests/test_repr_census_guard.py`'s own
`_collect_pass_criterion_repr_sites()` helper, run standalone on 2026-08-28 against this plan's
worktree:

```
uv run python -c "
import ast, pathlib
root = pathlib.Path('tests')
hits = []
for f in root.rglob('*.py'):
    if '__pycache__' in f.parts or f.name == 'test_repr_census_guard.py':
        continue
    tree = ast.parse(f.read_text(encoding='utf-8'), filename=str(f))
    for node in ast.walk(tree):
        if isinstance(node, ast.Assert):
            for sub in ast.walk(node.test):
                if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Name) and sub.func.id == 'repr':
                    hits.append((f.relative_to(root).as_posix(), sub.lineno))
                if isinstance(sub, ast.FormattedValue) and sub.conversion == 114:
                    hits.append((f.relative_to(root).as_posix(), sub.lineno))
for h in sorted(hits):
    print(h)
"
```

produces exactly the seven sites in the pass-criterion table below, byte-for-byte matching
`tests/test_repr_census_guard.py`'s recorded `PASS_CRITERION_REPR_ALLOWLIST`.

## Axis 1 — role

- **Pass-criterion**: the `repr(...)`/`!r` construct sits inside an `assert` statement's *test*
  expression and therefore decides GREEN or RED for that assertion.
- **Diagnostic-only**: the construct sits inside a failure-message f-string, a `pytest.fail`
  argument, a `parametrize(ids=...)` value, a comment, or a docstring — it cannot decide the
  verdict of any assertion.

The overwhelming majority of `repr(`/`!r` occurrences in this suite are diagnostic-only, and that
is entirely legitimate: quoting a value in a failure message so a human reading pytest output can
see exactly what was compared is good practice, and nothing in this milestone changes it. Only the
pass-criterion role is in this phase's scope.

## Axis 2 — value type

path / identifier / list / bytes / int / other.

## The pass-criterion census

All nine sites that were pass-criterion at the phase base — the two this phase rewrote (MSG-01)
plus the seven that remain untouched:

| Site | Value | Value type | Disposition |
|---|---|---|---|
| `tests/test_out02_escape_target_gate.py:134` | `target` (`"C:\escape.typ"` etc.) | **path** | rewritten under MSG-01 (plan 58-01) |
| `tests/test_builder.py:598` | `abs_uri` | **path** | rewritten under MSG-01 (plan 58-02) |
| `tests/test_registry_container_shape_gate.py:142` | `["a", "b"]` | list | untouched |
| `tests/test_registry_prewrite_validation_gate.py:278` | `"first-bad"` | identifier | untouched |
| `tests/test_registry_prewrite_validation_gate.py:279` | `"second-bad"` (negative case — asserted absent) | identifier | untouched |
| `tests/test_template_engine.py:1317` | `malformed` (a language code) | identifier | untouched |
| `tests/test_template_registry.py:832` | `["a", "b"]` | list | untouched |
| `tests/test_template_registry.py:847` | `b"base.typ"` | bytes | untouched |
| `tests/test_template_registry.py:1001` | `bad_value` (parametrized over `None`, `123`, `("a", "b")`) | other | untouched |

**Post-phase state:** seven pass-criterion sites remain, all seven non-path. The path-valued
pass-criterion count is **zero**.

## Third bucket — path-valued but format-asserting by design

`TestWindowsPathEscapingRegressionGuard._assert_no_doubled_separator` in
`tests/test_templates_path_collision_gate.py:445-455` is deliberately excluded from the
pass-criterion table above, even though it is path-valued. It asserts the **absence** of `repr()`'s
doubled-backslash rendering (`re.findall(r"\\\\+", message)` must be empty) — the **inverse**
direction of MSG-01's target, which asserts a path's *meaning* is preserved regardless of quoting
form. `TestWindowsPathEscapingRegressionGuard` asserts the opposite: that a specific quoting defect
(`!r`'s backslash-doubling leaking into a user-facing message) does NOT recur. MSG-02's own gate in
Phase 60 depends on this class continuing to catch that regression.

**It must NOT be rewritten, and Phase 60 must not re-litigate it.** This bucket exists in this
document precisely so a later phase reading only the pass-criterion table above does not conclude
the site was overlooked — it was seen, classified, and deliberately left alone.

It is not in the pass-criterion table above because its check is a regular-expression search for
consecutive backslashes in a message string (`re.findall(r"\\\\+", message)`), not a `repr()` call
or an `!r` conversion the AST sweep matches — the AST guard (`tests/test_repr_census_guard.py`)
correctly does not and should not flag it.

## Total occurrences — a descriptive, methodology-dependent figure

A fresh textual count over `tests/**/*.py`, run on 2026-08-28 in this worktree:

```
uv run python -c "
import pathlib, re
total = 0
pat = re.compile(r'repr\(|!r\b')
for f in pathlib.Path('tests').rglob('*.py'):
    if '__pycache__' in f.parts:
        continue
    total += len(pat.findall(f.read_text(encoding='utf-8')))
print(total)
"
```

produced **368** in this worktree.

Two earlier figures exist: **341** from `58-CONTEXT.md` D-08's session and **352** from
`58-RESEARCH.md`'s independent regex recount, both taken over a tree with no diff between them
(`git diff --stat 72896623 HEAD -- typsphinx/ tests/ pyproject.toml` was empty at the time each was
measured). The divergence among all three figures — 341, 352, and this document's own 368 — is
therefore a **counting-methodology difference**, not tree drift: what counts as one occurrence in
an f-string carrying two conversions, whether fixture/root directories are included, and (for this
document's count) the addition of `tests/_path_naming.py`, `tests/test_path_naming_predicate.py`,
and `tests/test_repr_census_guard.py` themselves in plans 58-01 through 58-03, each of which adds
diagnostic-only `repr(`/`!r` text of their own (docstrings explaining the predicate's design,
`ast.Call(func=Name('repr'))` literals in the guard's own source, etc.).

**No total is a test target, and here is why:** it is fragile to any future test file adding a
diagnostic-only `repr()`/`!r` occurrence (as this very phase's own new modules just demonstrated),
and it is not the safety-critical number. The safety-critical number is the **seven-site
allowlist**, which `tests/test_repr_census_guard.py` re-derives at run time on every test run,
never from a snapshot.

## The guard

`tests/test_repr_census_guard.py` is the AST-backed guard that keeps this census honest. It
re-derives the whole-tree pass-criterion set at run time (excluding itself by resolved-path
identity) and asserts it equals `PASS_CRITERION_REPR_ALLOWLIST`, the same seven sites recorded in
the table above. It also asserts the sweep is non-vacuous (parses at least 100 files), that zero
path-valued pass-criterion sites remain, and that every allowlist entry still points at a real
line in a real file.

**What its going RED means:** per milestone binding constraint 9, a plan in Phase 59 or 60 finding
this guard RED after touching a test file is a signal that the census was **incomplete**, not a
licence to edit the guard. The correct response is to **re-derive the census** — re-run the sweep,
understand why a new site appeared or a recorded one vanished, and update this document and the
guard's allowlist together — never to quietly append an allowlist entry to make the guard pass
again without understanding why the set changed.

## What this document is used for downstream

Phase 59 (PATH-01, IMG-04, IMG-05, IMG-06, IMG-07) and Phase 60 (MSG-02, MSG-03, MSG-04, MSG-05)
both claim **zero test edits** to the sites this document enumerates. This file, together with
`tests/test_repr_census_guard.py`, is the enumeration those claims are checked against — a
concrete, re-derivable list — rather than a belief.
