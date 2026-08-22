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

## Churn scope (measured post-fix)

Re-running `55-RESEARCH.md` § Open Questions item 3's churn measurement against the tree as it now
stands, after Task 1 and Task 2 have both landed.

**Command:**

```
find tests examples docs -type f | grep -E '_u[0-9a-f]+_'
```

**Result:**

```
tests/fixtures/xref_label_collision_guard_gate/a_u2f_b.rst
```

Exactly the single expected path — the only docname in the whole repository whose own file name
literally spells the encoder's `_u<hex>_` token shape. No other document's emitted label moved.

**Command:**

```
grep -rIoh '_u[0-9a-f]\+_' tests/ | sort | uniq -c | sort -rn
```

**Result:**

```
     48 _u2f_
     20 _u40_
     11 _u5f_
      1 _ue9_
      1 _u301_
```

`55-CONTEXT.md` D-02 cited 23 `_u2f_` and 19 `_u40_` occurrences at planning time; this post-fix
measurement shows 48 and 20 respectively. The delta is expected and not reconciled here, per the
plan's own instruction — the load-bearing fact is the PATH set above (unchanged at exactly one
file), not the census total, which naturally grows once Task 1's own product code
(`_LABEL_TOKEN_INTRODUCER_RE`'s docstring and comments), Task 1's inverted test/fixture prose, and
Task 2's new test module (`tests/test_sanitize_label_injectivity_unit.py`, which deliberately
spells `_u2f_`/`_u40_`/`_u5f_` throughout its own byte-identity and counterexample assertions) are
all counted by the same grep. The new `_u5f_` (11 occurrences) and the two encoding-edge tokens
(`_ue9_`, `_u301_`) did not exist in the tree before this plan — they are exactly the new
introducer-escape token (D-02) plus the Unicode edge probes Task 2 adds.

**Command:**

```
uv run pytest -q
```

**Result:**

```
1349 passed, 5 skipped in 118.98s (0:01:58)
```

Unconditional zero failures — no carve-out cited (the `tests/test_state_guard_shapes_gate.py`
carve-out recorded before Phase 54.1 was measured stale on 2026-08-16, per `STATE.md`; that module
passes in full here too, 18/18, folded into the 1349).

**Command:**

```
uv run black --check . && ruff check . && uv run mypy typsphinx/
```

(`ruff` run via the nix-store binary directly, `/nix/store/rxq02ylzcbjpzk7k9s8n4y4xwlznm0zr-ruff-0.15.14/bin/ruff`,
because `uv run ruff` fails to exec on this NixOS sandbox — a pre-existing, unrelated environment
hazard, not a defect this plan introduces.)

**Result:** all three exit 0 — `black --check .` reports "335 files would be left unchanged",
`ruff check .` reports "All checks passed!", `uv run mypy typsphinx/` reports "Success: no issues
found in 8 source files".

**`git diff --stat` against this plan's base commit** (`3d8bdb10eb475c53666abab494d3cbf524eb6ff5`)
confirms `typsphinx/translator.py` is the only production file this plan touched:

```
$ git diff --stat 3d8bdb10eb475c53666abab494d3cbf524eb6ff5 HEAD -- typsphinx/
 typsphinx/translator.py | 42 +++++++++++++++++++++++++++++++++++++++++-
 1 file changed, 41 insertions(+), 1 deletion(-)
```

`uv run pytest tests/test_preview_version_sync.py -q` — `3 passed` — the three-way `@preview`
version-sync surface is untouched by this plan.
