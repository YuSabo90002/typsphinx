# Phase 55 Plan 02: RED Evidence — BLD-07 and BLD-08

**Pre-fix commit (40-character SHA, `git rev-parse HEAD` in this worktree,
before any `typsphinx/` edit):**

```
40b92fc6ee6c3f53a6ec3306778d0c895958a797
```

D-05 sets a DIFFERENT RED evidence level for each defect this plan closes —
this file keeps them in two separately-labelled sections so that difference
is never flattened: BLD-07 is a real `sphinx-build` + `typst.compile()`
transcript (output-visible defect); BLD-08 is a unit-level transcript
(exception-type defect, no output ever reaches the compiled PDF).

---

## BLD-07 — real `sphinx-build` + `typst.compile()` (D-05 real-compile level)

**Command:**

```
uv run pytest tests/test_include_edge_separator_collision_gate.py -v
```

**Result: 2 failed, 2 passed.**

**Verbatim failure tail:**

```
=================================== FAILURES ===================================
_ TestIncludeEdgeSeparatorCollisionGate.test_shared_child_marker_appears_exactly_once _

self = <test_include_edge_separator_collision_gate.TestIncludeEdgeSeparatorCollisionGate object at 0x746fdff6fed0>
collision_build = {'result': CompletedProcess(args=['/home/yuta/Documents/typsphinx/.claude/worktrees/agent-ada68b26c1f4de47a/.venv/bin/...ing.offset + 1)\n  if "a#0>b#0>c" in state("typsphinx:include-edges", ()).get() { include("c.typ") }\n}\n\n\n}\n', ...}

    def test_shared_child_marker_appears_exactly_once(self, collision_build):
        """RED today: the dark edge's guard (``a#0>b`` -> ``c``) collides
        onto the same key as the live edge's guard (``a`` -> ``b#0>c``),
        so it wrongly fires and includes ``c.typ`` a second time -- the
        shared child's marker appears TWICE in the compiled PDF instead of
        once."""
        text = _extract_pdf_text(collision_build["manual_pdf"])
        child_count = text.count("SHAREDCHILDCOLLISIONMARKER")
        fourth_count = text.count("FOURTHDOCUMENTMARKER")
>       assert child_count == 1, (
            "expected the shared child's marker "
            "('SHAREDCHILDCOLLISIONMARKER') to appear exactly once in the "
            f"compiled PDF, got {child_count} occurrences (the fourth "
            f"document's own marker, 'FOURTHDOCUMENTMARKER', appeared "
            f"{fourth_count} times) -- BLD-07: a collided include-edge key "
            f"made a guard that must stay dark fire, duplicating the "
            f"shared child's content"
        )
E       AssertionError: expected the shared child's marker ('SHAREDCHILDCOLLISIONMARKER') to appear exactly once in the compiled PDF, got 2 occurrences (the fourth document's own marker, 'FOURTHDOCUMENTMARKER', appeared 1 times) -- BLD-07: a collided include-edge key made a guard that must stay dark fire, duplicating the shared child's content
E       assert 2 == 1

tests/test_include_edge_separator_collision_gate.py:223: AssertionError
_ TestIncludeEdgeSeparatorCollisionGate.test_published_array_and_two_guards_use_distinct_keys _

self = <test_include_edge_separator_collision_gate.TestIncludeEdgeSeparatorCollisionGate object at 0x746fdff77ce0>
collision_build = {'result': CompletedProcess(args=['/home/yuta/Documents/typsphinx/.claude/worktrees/agent-ada68b26c1f4de47a/.venv/bin/...ing.offset + 1)\n  if "a#0>b#0>c" in state("typsphinx:include-edges", ()).get() { include("c.typ") }\n}\n\n\n}\n', ...}

    def test_published_array_and_two_guards_use_distinct_keys(
        self, collision_build
    ):
        """The emitted ``manual.typ`` publishes an array containing the
        live edge's key and NOT the dark edge's key, and the two content
        files' guard lines test two DIFFERENT keys. Both expected keys are
        derived by calling the product's own single derivation point
        (``make_include_edge_key``), never hardcoded, so this test cannot
        drift from it."""
        from typsphinx.translator import make_include_edge_key
    
        live_key = make_include_edge_key("a", "b#0>c", occurrence=0)
        dark_key = make_include_edge_key("a#0>b", "c", occurrence=0)
    
>       assert live_key != dark_key, (
            "expected the live edge key (parent='a', child='b#0>c') and "
            "the dark edge key (parent='a#0>b', child='c') to differ; "
            f"both derived to {live_key!r}"
        )
E       AssertionError: expected the live edge key (parent='a', child='b#0>c') and the dark edge key (parent='a#0>b', child='c') to differ; both derived to 'a#0>b#0>c'
E       assert 'a#0>b#0>c' != 'a#0>b#0>c'

tests/test_include_edge_separator_collision_gate.py:247: AssertionError
=========================== short test summary info ============================
FAILED tests/test_include_edge_separator_collision_gate.py::TestIncludeEdgeSeparatorCollisionGate::test_shared_child_marker_appears_exactly_once - AssertionError: expected the shared child's marker ('SHAREDCHILDCOLLISIONMARKER') to appear exactly once in the compiled PDF, got 2 occurrences (the fourth document's own marker, 'FOURTHDOCUMENTMARKER', appeared 1 times) -- BLD-07: a collided include-edge key made a guard that must stay dark fire, duplicating the shared child's content
assert 2 == 1
FAILED tests/test_include_edge_separator_collision_gate.py::TestIncludeEdgeSeparatorCollisionGate::test_published_array_and_two_guards_use_distinct_keys - AssertionError: expected the live edge key (parent='a', child='b#0>c') and the dark edge key (parent='a#0>b', child='c') to differ; both derived to 'a#0>b#0>c'
assert 'a#0>b#0>c' != 'a#0>b#0>c'
========================= 2 failed, 2 passed in 0.45s ==========================
```

**Verbatim published state array line, copied out of the pre-fix
`manual.typ`** (re-derived in this worktree by driving
`tests.test_include_edge_separator_collision_gate._build_source_tree()`
against a scratch directory and running `sphinx-build -b typstpdf` directly —
same source tree the pytest gate above builds internally):

```
#state("typsphinx:include-edges", ()).update(("index#0>c", "index#0>a", "a#0>b#0>c", "index#0>a#0>b",))
```

Both content files' guard lines test the SAME key (`"a#0>b#0>c"`), confirming
the collision at the emission layer:

```
a.typ:17:      if "a#0>b#0>c" in state("typsphinx:include-edges", ()).get() { include("b#0>c.typ") }
a#0>b.typ:17:  if "a#0>b#0>c" in state("typsphinx:include-edges", ()).get() { include("c.typ") }
```

The compiled `manual.pdf` has 3 pages; `pypdf`-extracted text contains
`SHAREDCHILDCOLLISIONMARKER` (the shared child `c`'s own body marker)
**2 times** and `FOURTHDOCUMENTMARKER` (the fourth document `b#0>c`'s own
body marker) 1 time — matching this planning session's finding 1 exactly.

---

## BLD-08 — unit level (D-05 unit level)

**Command:**

```
uv run pytest tests/test_include_edge_derivation_unit.py -k DepthBound -v
```

**Result: 4 failed, 29 deselected.**

**Verbatim failure tail:**

```
=================================== FAILURES ===================================
___ TestDeriveMasterEdgeKeysDepthBound.test_chain_one_below_bound_completes ____

self = <test_include_edge_derivation_unit.TestDeriveMasterEdgeKeysDepthBound object at 0x7da2a0a5f9d0>

    def test_chain_one_below_bound_completes(self):
>       from typsphinx.translator import _MAX_INCLUDE_CHAIN_DEPTH
E       ImportError: cannot import name '_MAX_INCLUDE_CHAIN_DEPTH' from 'typsphinx.translator' (/home/yuta/Documents/typsphinx/.claude/worktrees/agent-ada68b26c1f4de47a/typsphinx/translator.py)

tests/test_include_edge_derivation_unit.py:313: ImportError
_ TestDeriveMasterEdgeKeysDepthBound.test_chain_at_exactly_the_bound_completes _

self = <test_include_edge_derivation_unit.TestDeriveMasterEdgeKeysDepthBound object at 0x7da2a0a5fb10>

    def test_chain_at_exactly_the_bound_completes(self):
>       from typsphinx.translator import _MAX_INCLUDE_CHAIN_DEPTH
E       ImportError: cannot import name '_MAX_INCLUDE_CHAIN_DEPTH' from 'typsphinx.translator' (/home/yuta/Documents/typsphinx/.claude/worktrees/agent-ada68b26c1f4de47a/typsphinx/translator.py)

tests/test_include_edge_derivation_unit.py:320: ImportError
_ TestDeriveMasterEdgeKeysDepthBound.test_chain_one_past_the_bound_raises_extension_error _

self = <test_include_edge_derivation_unit.TestDeriveMasterEdgeKeysDepthBound object at 0x7da2a0a63bb0>

    def test_chain_one_past_the_bound_raises_extension_error(self):
        """RED today: this raises a raw ``RecursionError``, not a named
        ``ExtensionError``. The raised message must name the bound, the
        depth reached, the master docname and the deepest docname."""
        from sphinx.errors import ExtensionError
    
>       from typsphinx.translator import _MAX_INCLUDE_CHAIN_DEPTH
E       ImportError: cannot import name '_MAX_INCLUDE_CHAIN_DEPTH' from 'typsphinx.translator' (/home/yuta/Documents/typsphinx/.claude/worktrees/agent-ada68b26c1f4de47a/typsphinx/translator.py)

tests/test_include_edge_derivation_unit.py:332: ImportError
_ TestDeriveMasterEdgeKeysDepthBound.test_bound_is_an_int_with_no_float_arithmetic _

self = <test_include_edge_derivation_unit.TestDeriveMasterEdgeKeysDepthBound object at 0x7da2a0a63ce0>

    def test_bound_is_an_int_with_no_float_arithmetic(self):
        """The precision edge probe (D-05): the bound is a module-level
        ``int`` literal, not a value computed at runtime, and the depth
        path is exact integer arithmetic with no float, rounding or
        truncation anywhere."""
>       from typsphinx.translator import _MAX_INCLUDE_CHAIN_DEPTH
E       ImportError: cannot import name '_MAX_INCLUDE_CHAIN_DEPTH' from 'typsphinx.translator' (/home/yuta/Documents/typsphinx/.claude/worktrees/agent-ada68b26c1f4de47a/typsphinx/translator.py)

tests/test_include_edge_derivation_unit.py:348: ImportError
=========================== short test summary info ============================
FAILED tests/test_include_edge_derivation_unit.py::TestDeriveMasterEdgeKeysDepthBound::test_chain_one_below_bound_completes - ImportError: cannot import name '_MAX_INCLUDE_CHAIN_DEPTH' from 'typsphinx.translator' (/home/yuta/Documents/typsphinx/.claude/worktrees/agent-ada68b26c1f4de47a/typsphinx/translator.py)
FAILED tests/test_include_edge_derivation_unit.py::TestDeriveMasterEdgeKeysDepthBound::test_chain_at_exactly_the_bound_completes - ImportError: cannot import name '_MAX_INCLUDE_CHAIN_DEPTH' from 'typsphinx.translator' (/home/yuta/Documents/typsphinx/.claude/worktrees/agent-ada68b26c1f4de47a/typsphinx/translator.py)
FAILED tests/test_include_edge_derivation_unit.py::TestDeriveMasterEdgeKeysDepthBound::test_chain_one_past_the_bound_raises_extension_error - ImportError: cannot import name '_MAX_INCLUDE_CHAIN_DEPTH' from 'typsphinx.translator' (/home/yuta/Documents/typsphinx/.claude/worktrees/agent-ada68b26c1f4de47a/typsphinx/translator.py)
FAILED tests/test_include_edge_derivation_unit.py::TestDeriveMasterEdgeKeysDepthBound::test_bound_is_an_int_with_no_float_arithmetic - ImportError: cannot import name '_MAX_INCLUDE_CHAIN_DEPTH' from 'typsphinx.translator' (/home/yuta/Documents/typsphinx/.claude/worktrees/agent-ada68b26c1f4de47a/typsphinx/translator.py)
======================= 4 failed, 29 deselected in 0.07s =======================
```

Every failure here is an `ImportError` on `_MAX_INCLUDE_CHAIN_DEPTH` — the
constant does not exist yet, which is itself part of the recorded RED (the
plan's own Task 1 instruction). A direct call confirms the underlying
defect is a raw `RecursionError`, not an `ImportError` or an `ExtensionError`,
once the depth exceeds the interpreter's own limit:

```
$ uv run python -c "
from typsphinx.translator import derive_master_edge_keys
chain = {f'd{i}': [f'd{i+1}'] for i in range(1000)}
derive_master_edge_keys(chain, 'd0')
" 2>&1 | tail -3
RecursionError: maximum recursion depth exceeded
```

### Depth headroom measurement (re-run in this worktree)

Re-measured directly against `derive_master_edge_keys()` in this worktree
(not transcribed from `55-CONTEXT.md`'s prior-session numbers), via a
standalone script driven by `uv run python`:

- **Interpreter's default recursion limit:** `sys.getrecursionlimit()` = **1000**.
- **Longest linear chain that completes from a near-empty stack:** binary-searched
  boundary = **996** (chains of length 990, 993, 994, 995, 996 all complete;
  length 1000 raises `RecursionError`). This worktree's own measurement is one
  frame deeper than `55-CONTEXT.md`'s recorded 995 — both are well inside the
  same order of magnitude and the conclusion (900 is not a safe bound) is
  unaffected either way.
- **A 900-deep chain under extra caller frames:** with 0 or 50 synthetic extra
  Python caller frames stacked above `derive_master_edge_keys()`, a 900-deep
  chain still completes; with 100 or 110 extra caller frames, it raises
  `RecursionError`. This confirms `55-RESEARCH.md`'s proposed constant of 900
  is **not safe** once realistic caller-stack depth (a real `sphinx-build`
  measured at 11 caller frames above this function; a `pytest` + `SphinxTestApp`
  stack is deeper still) is accounted for — it is not used.

This measurement is the justification for the module-level constant Task 3
lands (500 — roughly 495 frames of headroom below the measured 996-deep
near-empty-stack ceiling, two orders of magnitude beyond any real
documentation tree).

---

*Phase: 55-v0-8-0-derived-defects*
*Plan: 02*
*RED recorded: 2026-08-16*
