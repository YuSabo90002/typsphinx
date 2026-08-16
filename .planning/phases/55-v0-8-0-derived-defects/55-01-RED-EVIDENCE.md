# Phase 55 Plan 01 — RED Evidence

Recorded against commit `3d8bdb10eb475c53666abab494d3cbf524eb6ff5` (this worktree's base commit,
before any `typsphinx/` edit). `git status --porcelain typsphinx/` produced no output at the time
these commands were run.

**Fixture:** `tests/fixtures/xref_label_collision_guard_gate/` — two docnames, `a/b` (`:orphan:`,
carries the explicit `.. _nested-target:` label, absent from the compiling master's toctree) and
`a_u2f_b` (the decoy, included in the toctree, whose auto-derived section id is also
`nested-target`). `_sanitize_label` maps `/` to the literal token `_u2f_`, so
`_namespace_label("a/b", "nested-target")` and `_namespace_label("a_u2f_b", "nested-target")` both
sanitize to the identical label `a_u2f_b:nested-target` — the collision this RED evidence records.

## `uv run pytest` summary

**Command:**

```
uv run pytest tests/test_xref_compile_time_guard_render_gate.py -k collision -v
```

**Result:** `1 passed, 5 deselected in 0.91s`

```
tests/test_xref_compile_time_guard_render_gate.py::TestXrefCompileTimeGuardRenderGate::test_label_collision_guard_links_to_decoy PASSED [100%]

======================= 1 passed, 5 deselected in 0.91s ========================
```

`test_label_collision_guard_links_to_decoy` is today's characterization test of the bug (D-04): it
asserts `manual.pdf`'s link destinations DO include `a_u2f_b:nested-target`, resolving the
reference to the decoy's heading. This currently-**passing** assertion IS SC#1's "pre-fix
link-to-decoy behaviour recorded first."

## Real two-master compile — direct `sphinx-build` invocation + destination extraction

**Command (inline, driving the same fixture through `sys.executable -m sphinx -b typstpdf` into a
temporary directory, then printing `sorted(_link_annotation_dests(manual_pdf_bytes))`):**

```python
import subprocess, sys, tempfile
from pathlib import Path
sys.path.insert(0, "tests")
from test_xref_compile_time_guard_render_gate import _link_annotation_dests

FIXTURE = Path("tests/fixtures/xref_label_collision_guard_gate")
with tempfile.TemporaryDirectory() as td:
    build_dir = Path(td)
    result = subprocess.run(
        [sys.executable, "-m", "sphinx", "-b", "typstpdf", str(FIXTURE), str(build_dir)],
        capture_output=True, text=True,
    )
    print("returncode:", result.returncode)
    pdf_bytes = (build_dir / "manual.pdf").read_bytes()
    print("sorted dests:", sorted(_link_annotation_dests(pdf_bytes)))
```

**Result:**

```
returncode: 0
sorted dests: ['a_u2f_b:nested-target', 'a_u2f_b:nested-target', 'index:collision-gate']
```

**This IS SC#1's pre-fix link-to-decoy behaviour, recorded first (binding constraint #6):** the
sorted destination list contains `a_u2f_b:nested-target` — the reference resolves to the decoy's
heading label even though its real intended target (`a/b`, `:orphan:`, absent from the compiling
master) is not present. The build exits 0 (`returncode: 0`) — the collision is invisible at every
layer above the compiled PDF's link-destination table.

## Handover

Task 1 lands the fix (`_LABEL_TOKEN_INTRODUCER_RE` pre-pass inside `_sanitize_label`) and inverts
`test_label_collision_guard_links_to_decoy` into `test_label_collision_no_longer_links_to_decoy`
within this same plan/task — no phase-boundary green gate is needed between recording this RED
evidence and closing it. Task 2 adds the injectivity proof suite; Task 3 measures the churn scope
across the whole tree and appends its own section below.
