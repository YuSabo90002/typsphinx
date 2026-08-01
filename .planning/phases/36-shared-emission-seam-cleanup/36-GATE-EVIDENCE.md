# Phase 36 GATE-01 Evidence: Decoupling Diff + MATH-02 RED -> GREEN Record

This file is Phase 36's single GATE-01 evidence record, appended to by four
plans in sequence: Plan 01 (this plan) writes the pre-decoupling baseline
and the RED capture below; Plan 02 appends the decoupling diff; Plan 03
appends the MATH-02 RED/GREEN pair; Plan 04 appends the regression sweep and
the phase verdict. One file, four appending writers.

This file is deliberately NOT named `36-VERIFICATION.md` -- that filename is
reserved by the verify stage and is overwritten wholesale; a name collision
here would silently destroy this evidence.

Every command below was executed in this plan's own session, in this
worktree. No figure in this file was transcribed or recalled from planning
documents.

## Pre-decoupling baseline (SC#2, D-07)

- **Commit measured:** `b37ea402733c9ed6610c873349dca4c520ae7f22` (this
  plan's Task 2 commit, `test(36-01): capture pre-decoupling golden and ship
  SC#1+SC#2 gate` -- `typsphinx/` is untouched at this commit;
  `git status --porcelain typsphinx/` is empty).
- **Date:** 2026-08-01T00:18:33Z
- **Commands (two independent builds into different scratch directories):**
  ```
  uv run python -m sphinx -b typst -q -E tests/fixtures/desc_rubric_decoupling_render_gate <scratch>/a
  uv run python -m sphinx -b typst -q -E tests/fixtures/desc_rubric_decoupling_render_gate <scratch>/b
  ```
  Both exited `0` with empty stdout/stderr.

### Determinism proof

```
cmp <scratch>/a/index.typ <scratch>/b/index.typ
```
Exit status: `0` -- the two independent builds are byte-identical. No
timestamp, date, or path is embedded in the emitted `.typ`.

Both scratch builds were also compared against the committed golden:
```
cmp <scratch>/a/index.typ tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ
```
Exit status: `0` -- confirms the committed `golden.typ` is exactly what the
untouched translator emits right now, at this commit.

### Golden pointer

`tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ`, quoted
verbatim (90 lines). This exact text must survive Plan 02's decoupling
change byte-for-byte -- that is the whole of SC#2:

```typst
// Essential package imports
#import "@preview/codly:1.3.0": *
#import "@preview/codly-languages:0.1.10": *
#import "@preview/mitex:0.2.7": mi, mitex
#import "@preview/gentle-clues:1.3.1": *

#show: codly-init.with()
#codly(languages: codly-languages)

#import "_template.typ": project

#show: project.with(
  title: "Desc Rubric Decoupling Render Gate",
  authors: ("typsphinx tests",),
  date: "0.0.0",
  lang: "en",
)

#{
[#heading(level: 1, {text("Desc Rubric Decoupling Render Gate")}) <index:desc-rubric-decoupling-render-gate>]

par({text("This fixture combines a single signature, sibling signatures, plain bold markup, an autodoc-style Options rubric, a rubric carrying a propagated target inside a list item, and a rubric at true end-of-document – the constructs Phase 36’s SC#2 names – into one file, so the desc_signature/ rubric decoupling can be proven to produce byte-identical .typ output.")})

par({text("Single signature with an id anchor.")})

strong({text("connect")
text("(") + text("host") + text(", ") + text("port") + text(", ") + text("timeout") + text("=") + text("30") + text(")")})
[#metadata(none) <index:connect>]
par({text("Connect to ")
emph({text("host")})
text(".")})

parbreak()
par({text("Sibling signatures under one directive.")})

strong({text("compile")
text("(") + text("source") + text(")")})
[#metadata(none) <index:compile>]
linebreak()
strong({text("compile")
text("(") + text("source") + text(", ") + text("filename") + text(")")})
linebreak()
strong({text("compile")
text("(") + text("source") + text(", ") + text("filename") + text(", ") + text("symbol") + text(")")})
par({text("Compile source into a code or AST object.")})

parbreak()
par({text("Plain bold markup – the regression control.")})

par({text("This paragraph contains ")
strong({text("bold text")})
text(" that must keep routing through visit_strong unchanged, byte-identical after the decoupling.")})

par({text("The autodoc “Options” rubric shape.")})


strong({text("Options")})
linebreak()
strong({text("--sep")})
[#metadata(none) <index:cmdoption-sep>]
par({text("If specified, separate source and build directories.")})

parbreak()
par({text("A rubric carrying a propagated target, inside a list item.")})

list({
parbreak()

text("First bullet text.")


[#metadata(none) <index:decoupling-rubric-in-list-target>]


strong({text("A Rubric In A List Item")})

linebreak()

parbreak()

text("More text after the rubric.")
})

par({text("A rubric at true end-of-document.")})


strong({text("Trailing Heading")})
linebreak()

}
```

Note the `list({ ... })` block at lines 66-82 (R2's construct): two blank
lines separate `[#metadata(none) <index:decoupling-rubric-in-list-target>]`
(line 72) from `strong({text("A Rubric In A List Item")})` (line 75) -- the
D-03 byte-identity hazard 36-RESEARCH.md measured. This is existing,
pre-decoupling behaviour; the decoupled `visit_rubric` in Plan 02 must
reproduce it exactly, not "fix" it.

## RED — pre-decoupling SC#1 delegation check (SC#1, ADM-06)

- **Command:**
  ```
  uv run pytest tests/test_desc_rubric_decoupling_render_gate.py -q -k "do_not_delegate" --tb=long
  ```

### Verbatim pytest failure output

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-ad75811ce6debe2c2
configfile: pyproject.toml
plugins: cov-7.1.0
collected 3 items / 2 deselected / 1 selected

tests/test_desc_rubric_decoupling_render_gate.py F                       [100%]

=================================== FAILURES ===================================
_ TestDescRubricDecouplingRenderGate.test_desc_signature_and_rubric_do_not_delegate_to_visit_strong _

self = <test_desc_rubric_decoupling_render_gate.TestDescRubricDecouplingRenderGate object at 0x7f7ce350ed50>

    def test_desc_signature_and_rubric_do_not_delegate_to_visit_strong(self):
        """
        The SC#1 assertion. Parses ``typsphinx/translator.py`` with
        ``ast.parse`` and checks, by method name, which handlers still call
        ``self.visit_strong``/``self.depart_strong`` on a dummy node.

        Pre-decoupling (this plan) this assertion FAILS -- all six
        delegation sites still exist, so this is the recorded RED. Runs
        unconditionally: no fixture, no typst-py requirement, and no skip.
        """
        source_text = TRANSLATOR_PATH.read_text(encoding="utf-8")
        tree = ast.parse(source_text, filename=str(TRANSLATOR_PATH))

        functions_by_name: dict[str, ast.AST] = {}
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions_by_name[node.name] = node

        # (a) The four decoupled methods must exist and must NOT delegate.
        for method_name in DECOUPLED_METHODS:
            assert method_name in functions_by_name, (
                f"Expected typsphinx/translator.py to define {method_name!r} "
                "-- the decoupling target is missing entirely."
            )
            delegating_calls = _delegating_calls_in(functions_by_name[method_name])
>           assert delegating_calls == [], (
                f"{method_name} still delegates to {delegating_calls} via a "
                "dummy strong() node -- the ADM-06 decoupling (D-01: copy "
                "visit_strong's body verbatim instead of delegating) has not "
                "been applied yet."
            )
E           AssertionError: visit_desc_signature still delegates to ['visit_strong'] via a dummy strong() node -- the ADM-06 decoupling (D-01: copy visit_strong's body verbatim instead of delegating) has not been applied yet.
E           assert ['visit_strong'] == []
E
E             Left contains one more item: 'visit_strong'
E             Use -v to get more diff

tests/test_desc_rubric_decoupling_render_gate.py:207: AssertionError
=========================== short test summary info ============================
FAILED tests/test_desc_rubric_decoupling_render_gate.py::TestDescRubricDecouplingRenderGate::test_desc_signature_and_rubric_do_not_delegate_to_visit_strong
======================= 1 failed, 2 deselected in 0.04s ========================
```

The failure is on the delegation assertion itself (`assert delegating_calls
== []`, sub-assertion (a) of the SC#1 method) -- not a collection error, an
`ImportError`, a missing fixture, or a skip. RED confirmed against the
unfixed translator.

### Delegation-site census (pre-decoupling)

Command:
```
grep -n "dummy_strong = nodes.strong()" typsphinx/translator.py
```

Verbatim output:
```
4684:        dummy_strong = nodes.strong()
4693:        dummy_strong = nodes.strong()
5047:        dummy_strong = nodes.strong()
5065:        dummy_strong = nodes.strong()
5141:        dummy_strong = nodes.strong()
5147:        dummy_strong = nodes.strong()
```

| Line | Owning method | Disposition |
|------|----------------|-------------|
| 4684 | `visit_desc_signature` | IN SCOPE — must stop delegating in Plan 02 |
| 4693 | `depart_desc_signature` | IN SCOPE — must stop delegating in Plan 02 |
| 5047 | `visit_rubric` | IN SCOPE — must stop delegating in Plan 02 |
| 5065 | `depart_rubric` | IN SCOPE — must stop delegating in Plan 02 |
| 5141 | `visit_literal_strong` | **OUT OF SCOPE** — expected to survive (36-RESEARCH.md Pitfall 1; FLD-03's bold-literal field-list value) |
| 5147 | `depart_literal_strong` | **OUT OF SCOPE** — expected to survive (36-RESEARCH.md Pitfall 1; FLD-03's bold-literal field-list value) |

Expected post-decoupling count: **2, not 0** -- both owned by
`literal_strong`. Confirmed via the census command above: `6` today.

## Pre-change full-suite baseline (SC#4)

- **Command:** `uv run pytest -q --tb=no -rf` (per-worktree provisioning per
  CLAUDE.md: `uv sync --extra dev` + the documented `.venv/bin/uv` and
  `.venv/bin/ruff` symlink fix for the NixOS stub-ld ELF hazard, project
  memory "NixOS sandbox test env").

### Verbatim tail

```
tests/test_typst_elements_pass_through_gate.py ..........                [ 95%]
tests/test_typst_lang_gate.py .....................                     [ 98%]
tests/test_typst_string_escape_gate.py .....                             [ 99%]
tests/test_wide_table_render_gate.py .                                   [ 99%]
tests/test_xref_orphan_degrade_render_gate.py .                          [100%]

=========================== short test summary info ============================
FAILED tests/test_desc_rubric_decoupling_render_gate.py::TestDescRubricDecouplingRenderGate::test_desc_signature_and_rubric_do_not_delegate_to_visit_strong
================== 1 failed, 651 passed, 1 skipped in 57.36s ===================
```

### Sorted set of failing test node IDs

```
tests/test_desc_rubric_decoupling_render_gate.py::TestDescRubricDecouplingRenderGate::test_desc_signature_and_rubric_do_not_delegate_to_visit_strong
```

This single failure is this plan's own intentional SC#1 RED capture (the
section immediately above) -- excluded from the baseline's "other failures"
accounting below, same convention Phase 34's `34-GATE-EVIDENCE.md` used.

**Sorted list of OTHER failing node IDs (the actual pre-change baseline
Plan 04 must compare its post-change failing set against):** none. With the
`.venv/bin/uv`/`.venv/bin/ruff` symlink fix applied, this run shows **zero**
environmentally-failing tests. The 1 skip is inside `tests/test_corpus_gate.py`
(its own documented network-dependent skip), unrelated to this phase.

SC#4's acceptance is `post-change failing set == this set`, never `zero
failures`, because project memory records an environmental failure class in
this sandbox absent the symlink fix. Concretely: Plan 04's expected clean
state is `652 passed, 1 skipped, 0 failed` once Plan 02's decoupling flips
this plan's own RED test to GREEN and Plan 03 lands MATH-02's fix with no
new failure anywhere else -- any additional failure in Plan 04's run beyond
that is a real regression, not environmental noise.

### Lint/type trio baseline

| Command | Exit status | Last output line |
|---------|--------------|-------------------|
| `uv run black --check .` | `0` | "All done! ✨ 🍰 ✨ / 175 files would be left unchanged." |
| `uv run ruff check .` | `0` | "All checks passed!" |
| `uv run mypy typsphinx/` | `0` | "Success: no issues found in 6 source files" |

## Post-decoupling diff (SC#1, SC#2, D-03, D-07)

- **Baseline commit (pre-decoupling, recorded by Plan 01):**
  `b37ea402733c9ed6610c873349dca4c520ae7f22` (`test(36-01): capture
  pre-decoupling golden and ship SC#1+SC#2 gate`).
- **Decoupling commit (this plan, post-decoupling):**
  `8708ab0de6f8b3fe979705c51888de2691982dc4` (`feat(36-02): decouple
  visit_rubric/depart_rubric from visit_strong`, Task 2's commit -- the
  final commit in this plan that touches `typsphinx/translator.py`; Task
  1's commit `12547a2` is its immediate ancestor within the same plan).

### Build commands (two independent worktrees, one per commit)

```
# baseline commit, checked out into a throwaway git worktree with its own
# per-worktree venv (same provisioning steps as CLAUDE.md prescribes)
uv run python -m sphinx -b typst -q -E tests/fixtures/desc_rubric_decoupling_render_gate <scratch>/baseline-build

# decoupling commit, this plan's own worktree
uv run python -m sphinx -b typst -q -E tests/fixtures/desc_rubric_decoupling_render_gate <scratch>/decoupled-build
```

Both exited `0` with empty stdout/stderr.

### SC#2 byte-identity diff (the proof)

```
diff <scratch>/baseline-build/index.typ <scratch>/decoupled-build/index.typ
```

Verbatim output: **(empty)** -- the command printed nothing. Exit status
`0`. The emitted `.typ` is byte-identical across the decoupling change
alone; this is SC#2's discharge.

### `git diff --stat` between the two named commits

A note on measurement first: `git diff --stat` between two commits
reflects the FULL tree difference, including any commits by other
plans/agents that happen to sit between them in history -- it is not
scoped to "this plan's own commits". Measured directly:

```
$ git diff --stat b37ea402733c9ed6610c873349dca4c520ae7f22 8708ab0de6f8b3fe979705c51888de2691982dc4
 .planning/ROADMAP.md                               |  45 ++-
 .planning/STATE.md                                 |  17 +-
 .../36-01-SUMMARY.md                               | 133 +++++++++
 .../36-GATE-EVIDENCE.md                            | 304 +++++++++++++++++++++
 typsphinx/translator.py                            | 188 ++++++++++++-
 5 files changed, 663 insertions(+), 24 deletions(-)
```

The four non-`translator.py` paths are all attributable to work that
landed BETWEEN the baseline commit and this plan's start -- Plan 01's own
Task 3 evidence/summary commits, and the orchestrator's
"docs(phase-36): update tracking after wave 1" commit
(`037504fd224275249c3a303c9c614888a3e9582f`, this plan's actual starting
commit) -- none of it authored by this plan's tasks. Confirmed
`typsphinx/translator.py` is byte-identical between the baseline commit
and this plan's starting commit (`git diff b37ea40 037504fd --
typsphinx/translator.py` produces no output), so re-running the same
`--stat` from the content-identical starting point isolates this plan's
own change cleanly:

```
$ git diff --stat 037504fd224275249c3a303c9c614888a3e9582f 8708ab0de6f8b3fe979705c51888de2691982dc4
 typsphinx/translator.py | 188 ++++++++++++++++++++++++++++++++++++++++++++----
 1 file changed, 175 insertions(+), 13 deletions(-)
```

Exactly one path, `typsphinx/translator.py` -- no test file, no fixture,
no config rides in the decoupling change (D-07).

### D-03 decision taken

Verbatim copy, unreachable branches kept. Both `visit_desc_signature`/
`depart_desc_signature` (Task 1) and `visit_rubric`/`depart_rubric` (Task
2) retain the full body of `visit_strong`/`depart_strong` including the
`_add_paragraph_separator()` call, the markup-mode `#` prefix computation,
and the `_enter_inline_concat_element()`/`_exit_inline_concat_element()`
pair -- all three proven inert when entered from `desc_signature`/`rubric`
by 36-RESEARCH.md. They were kept, not pruned, because the binding
constraint is a zero diff (SC#2) and keeping inert branches costs nothing,
while pruning them would stake byte-identity on three separate
unreachability proofs instead of on a mechanical verbatim copy. The
pre-existing two-blank-line redundancy in `visit_rubric`'s R2 construct
(propagated target inside a list item) was reproduced exactly, not tidied
-- confirmed present, unchanged, in both the baseline and decoupled builds
above (the empty `diff` covers this region too).

## SC#1 delegation census (post-decoupling)

Command:
```
grep -n "dummy_strong = nodes.strong()" typsphinx/translator.py
```

Verbatim output:
```
5303:        dummy_strong = nodes.strong()
5309:        dummy_strong = nodes.strong()
```

Count: **2** (down from the pre-decoupling **6** recorded above).

| Line | Owning method | Disposition |
|------|----------------|-------------|
| 5303 | `visit_literal_strong` | OUT OF SCOPE -- survives by design |
| 5309 | `depart_literal_strong` | OUT OF SCOPE -- survives by design |

`visit_literal_strong`/`depart_literal_strong` are FLD-03's bold-literal
field-list-value node and belong to Phase 38; they were not touched by
this plan (36-RESEARCH.md Pitfall 1).

Verbatim passing output of the SC#1+SC#2+compile-sanity gate module:

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-ae705662415abf531
configfile: pyproject.toml
plugins: cov-7.1.0
collected 3 items

tests/test_desc_rubric_decoupling_render_gate.py ...                     [100%]

============================== 3 passed in 0.57s ===============================
```

All three test methods pass, including the SC#1 delegation assertion,
which flips RED (recorded pre-decoupling above) to GREEN with this plan.

### Regression net

Command (the five pre-existing render gates that already exercise this
seam, plus the new SC#1/SC#2 gate):
```
uv run pytest tests/test_desc_rubric_decoupling_render_gate.py tests/test_desc_signature_concat_render_gate.py tests/test_desc_signature_anchor_render_gate.py tests/test_desc_sig_space_render_gate.py tests/test_rubric_option_concat_render_gate.py tests/test_rubric_propagated_target_render_gate.py -q
```

Verbatim output:
```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-ae705662415abf531
configfile: pyproject.toml
plugins: cov-7.1.0
collected 10 items

tests/test_desc_rubric_decoupling_render_gate.py ...                     [ 30%]
tests/test_desc_signature_concat_render_gate.py ..                       [ 50%]
tests/test_desc_signature_anchor_render_gate.py .                        [ 60%]
tests/test_desc_sig_space_render_gate.py ..                              [ 80%]
tests/test_rubric_option_concat_render_gate.py .                         [ 90%]
tests/test_rubric_propagated_target_render_gate.py .                     [100%]

============================== 10 passed in 2.65s ==============================
```

All ten tests pass. `tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ`
is confirmed unchanged since the baseline commit
(`git diff b37ea40 -- tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ`
produces no output).

## RED — pre-fix run (SC#3, D-04, D-06)

- **Commit measured:** `ea70913` (this plan's Task 1 commit, `test(36-03): add
  Construct H and capture pre-fix PDF-text baselines`) -- `typsphinx/` is
  untouched at this commit; `git status --porcelain typsphinx/` is empty. The
  new SC#3 assertions and the PDF-text invariance guard written in this task
  (Task 2) are run against `typsphinx/translator.py` unchanged since this
  commit, before Task 3's fix is applied.
- **Date:** 2026-08-01
- **Command:**
  ```
  uv run pytest tests/test_inline_math_after_text_render_gate.py -q -k "mitex_path or native_path" --tb=short
  ```

### Verbatim pytest failure output

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a767a2485d4791381
configfile: pyproject.toml
plugins: cov-7.1.0
collected 3 items / 1 deselected / 2 selected

tests/test_inline_math_after_text_render_gate.py FF                      [100%]

=================================== FAILURES ===================================
_ TestInlineMathAfterTextRenderGate.test_typstpdf_separates_inline_math_mitex_path _
tests/test_inline_math_after_text_render_gate.py:301: in test_typstpdf_separates_inline_math_mitex_path
    assert (
E   AssertionError: Construct E (mitex path) did not emit exactly one blank line after the block math call:
E     ... [full emitted .typ elided in this evidence file; the failure below
E     confirms the exact substring under test] ...
E   assert 'text("Text before block math.")\nmitex(`E = m c^2`)\n\nparbreak()' in '// Essential package imports\n#import "@preview/codly:1.3.0": *\n#import "@preview/codly-languages:0.1.10": *\n#impor...ruct's emission must be identical before and after the MATH-02 fix.")})\n\nlist({\nmitex(`H = m g h`)\n\n\n})\n\n\n}\n'
_ TestInlineMathAfterTextRenderGate.test_typstpdf_separates_inline_math_native_path _
tests/test_inline_math_after_text_render_gate.py:457: in test_typstpdf_separates_inline_math_native_path
    assert (
E   AssertionError: Construct E (native path) did not emit exactly one blank line after the block math call:
E     ... [full emitted .typ elided; see above] ...
E   assert 'text("Text before block math.")\n$ E = m c^2 $\n\nparbreak()' in '// Essential package imports\n#import "@preview/codly:1.3.0": *\n#import "@preview/codly-languages:0.1.10": *\n#impor...construct's emission must be identical before and after the MATH-02 fix.")})\n\nlist({\n$ H = m g h $\n\n\n})\n\n\n}\n'
=========================== short test summary info ============================
FAILED tests/test_inline_math_after_text_render_gate.py::TestInlineMathAfterTextRenderGate::test_typstpdf_separates_inline_math_mitex_path
FAILED tests/test_inline_math_after_text_render_gate.py::TestInlineMathAfterTextRenderGate::test_typstpdf_separates_inline_math_native_path
======================= 2 failed, 1 deselected in 0.69s ========================
```

Both failures are on the new Construct E MATH-02 boundary assertion (the GREEN
one-blank-line string), not a collection error, `ImportError`, missing file, or
skip. RED confirmed against the unfixed translator, on both emission paths.

### Pre-fix emitted regions per construct

All four regions below were copied verbatim from a real `sphinx-build -b typst`
build against this commit (unfixed translator), by locating the unique math
body substring (`E = m c^2` for Construct E, `G = m a` for Construct G) in the
emitted `index.typ` and reading the surrounding bytes with a Python one-liner
-- never hand-retyped.

**Construct E, mitex path** (three newlines -- two blank lines -- before
`parbreak()`):
```
text("Text before block math.")\nmitex(`E = m c^2`)\n\n\nparbreak()
```

**Construct G, mitex path** (the labelled equation's payload spans three
source lines because the directive content's own trailing blank lines flow
into `node.astext()`; three newlines before `parbreak()`):
```
[#metadata(none) <index:equation-construct-g-labeled-eq>]\n\nmitex(`G = m a\n\n`)\n\n\nparbreak()
```

**Construct E, native path** (`-D typst_use_mitex=0`):
```
text("Text before block math.")\n$ E = m c^2 $\n\n\nparbreak()
```

**Construct G, native path**:
```
[#metadata(none) <index:equation-construct-g-labeled-eq>]\n\n$ G = m a\n\n $\n\n\nparbreak()
```

**Construct H region, both paths** (the single-element edge -- copied for
reference; this region is asserted UNCHANGED across the fix, not RED):

mitex:
```
list({\nmitex(`H = m g h`)\n\n\n})
```

native:
```
list({\n$ H = m g h $\n\n\n})
```

### GREEN string derivation

Per this plan's `<critical_plan_constraint>` and the milestone's invariant #4,
each GREEN string below was derived BY HAND from the pre-fix string recorded
directly above it, by removing exactly one newline character (the redundant
one, immediately before the following `parbreak()`) -- nothing else was
changed, and no string was taken from a fixed build:

1. **Construct E, mitex.** Pre-fix: `...mitex(\`E = m c^2\`)\n\n\nparbreak()`.
   GREEN: `...mitex(\`E = m c^2\`)\n\nparbreak()` -- the third `\n` removed.
   No string was taken from a fixed build.
2. **Construct G, mitex.** Pre-fix: `...\`)\n\n\nparbreak()` (after the
   labelled payload's closing `` `) ``). GREEN: `...\`)\n\nparbreak()` -- the
   third `\n` removed, the multi-line payload itself untouched.
   No string was taken from a fixed build.
3. **Construct E, native.** Pre-fix: `...$ E = m c^2 $\n\n\nparbreak()`.
   GREEN: `...$ E = m c^2 $\n\nparbreak()` -- the third `\n` removed. No
   string was taken from a fixed build.
4. **Construct G, native.** Pre-fix: `... $\n\n\nparbreak()` (after the
   labelled native span's closing `` $ ``). GREEN: `... $\n\nparbreak()` --
   the third `\n` removed. No string was taken from a fixed build.

Construct H's region (both paths) is asserted UNCHANGED -- not derived -- per
D-06/the plan's measured fact #4: with no following sibling inside the list
item, the trailing flag has no consumer, so pre-fix and post-fix emission are
byte-identical by construction.

The zero-blank-line boundary strings (e.g.
`mitex(\`E = m c^2\`)\nparbreak()`) asserted absent on both sides of the fix
were derived the same way conceptually (one fewer newline than GREEN) but
were never observed in either build; they exist purely as the boundary-check
half of each pair, per the plan's action text.

### PDF-text baseline capture (pre-fix)

Commands (Task 1, same commit `ea70913`):
```
uv run python -m sphinx -b typstpdf -q -E tests/fixtures/inline_math_after_text_render_gate <scratch>/build_mitex_pdf
uv run python -m sphinx -b typstpdf -q -E -D typst_use_mitex=0 tests/fixtures/inline_math_after_text_render_gate <scratch>/build_native_pdf
```
Both exited `0`. Extraction (`pypdf.PdfReader`, pages joined with `\n`,
`extract_text()` per page, matching the existing module idiom):

| Path | Page count | Extracted text length (chars) |
|------|------------|-------------------------------|
| mitex | 3 | 1939 |
| native | 3 | 1939 |

**Measured finding, not assumed:** the two baselines are byte-identical to
each other (`cmp` exit `0`) -- Typst's math typesetting renders both the
mitex-converted LaTeX and the native `$...$` form through the same underlying
Unicode Mathematical Alphanumeric glyph substitution, so the extracted PDF
text carries no visible difference between the two emission paths for this
fixture's math bodies. This is a genuine measurement, recorded transparently
rather than silently reconciled; it does not affect the invariance guard
itself, which compares each path's pre-fix baseline against that SAME path's
post-fix extraction, never baseline-vs-baseline. PDF byte size and PDF byte
equality were never asserted or recorded, per the plan's explicit prohibition
(Typst embeds a `CreationDate`/`ModDate`, so two builds of identical input
differ in bytes).

## GREEN — post-fix run (SC#3, D-04, D-06)

- **Fix commit:** this commit -- Task 3's `typsphinx/translator.py` change
  and this evidence section land together in one atomic commit (the plan's
  own acceptance criteria check `git diff HEAD~1 -- typsphinx/translator.py`
  relative to the RED commit, so the fix must be exactly one commit ahead of
  RED, precluding a separate self-referencing commit for this section). The
  definitive SHA is visible via `git log --oneline -1 -- typsphinx/translator.py`
  once this commit lands; Plan 04 can read it directly from `git log`.
- **RED commit (Task 2):** `21df46a` (`test(36-03): add SC#3 boundary
  assertions and D-04 invariance guard, record RED`).
- **Date:** 2026-08-01

### The fix

Exactly one statement changed in `visit_math_block`'s trailing bookkeeping:
`self.list_item_needs_separator = True` -> `self.list_item_needs_separator =
False`, guarded by the same pre-existing `if self.in_list_item:` -- nothing
else in the method changed. The comment block above the statement was
rewritten to explain the new behaviour (why this handler must CLEAR the
shared flag, unlike every other block-level handler that arms it).

### Verbatim pytest passing output

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a767a2485d4791381
configfile: pyproject.toml
plugins: cov-7.1.0
collected 3 items

tests/test_inline_math_after_text_render_gate.py ...                     [100%]

============================== 3 passed in 1.30s ===============================
```

All three methods green: the two path tests flip RED to GREEN and the
invariance guard stays green.

### Post-fix emitted regions per construct

Copied verbatim from a real `sphinx-build -b typst` build against the fixed
translator, using the same unique-substring lookup as the RED capture --
never hand-retyped, never assumed.

**Construct E, mitex path** (now two newlines -- one blank line -- before
`parbreak()`, matching the hand-derived GREEN string exactly):
```
text("Text before block math.")\nmitex(`E = m c^2`)\n\nparbreak()
```

**Construct G, mitex path**:
```
[#metadata(none) <index:equation-construct-g-labeled-eq>]\n\nmitex(`G = m a\n\n`)\n\nparbreak()
```

**Construct E, native path**:
```
text("Text before block math.")\n$ E = m c^2 $\n\nparbreak()
```

**Construct G, native path**:
```
[#metadata(none) <index:equation-construct-g-labeled-eq>]\n\n$ G = m a\n\n $\n\nparbreak()
```

**Construct H region, both paths** -- confirmed byte-identical to the pre-fix
capture (programmatically compared, `pre_region == post_region` is `True`):

mitex:
```
list({\nmitex(`H = m g h`)\n\n\n})
```

native:
```
list({\n$ H = m g h $\n\n\n})
```

The single-element edge behaved exactly as predicted: with no following
sibling inside the item, the trailing flag has no consumer, so Construct H's
emission is unaffected by the fix on both paths.

### PDF text-invariance result

Both PDFs were rebuilt against the fixed translator and their `pypdf`-
extracted text compared to the Task 1 pre-fix baselines:

| Path | Page count | Extracted text length (chars) | Equals committed baseline |
|------|------------|-------------------------------|----------------------------|
| mitex | 3 | 1939 | `True` |
| native | 3 | 1939 | `True` |

`uv run pytest tests/test_inline_math_after_text_render_gate.py -q -k
"invariant"` passes (1 passed). **PDF bytes were deliberately NOT
compared** -- Typst embeds a `CreationDate`/`ModDate` in every compile, so
two builds of identical input differ in bytes even when their extracted text
and page count are identical (measured earlier in this phase and in
36-CONTEXT.md D-04); only extracted text and page count are asserted.

### RED → GREEN verdict

| Assertion | RED commit | GREEN commit | Transition |
|-----------|------------|---------------|------------|
| Construct E boundary (mitex): GREEN string present | `21df46a` | this commit | FAIL -> PASS |
| Construct E boundary (mitex): two-blank-line form absent | `21df46a` | this commit | (unreached under RED; assert #1 failed first) -> PASS |
| Construct E boundary (mitex): zero-blank-line form absent | `21df46a` | this commit | PASS (always true) -> PASS |
| Construct G boundary (mitex): GREEN string present | `21df46a` | this commit | FAIL -> PASS |
| Construct G boundary (mitex): two-blank-line form absent | `21df46a` | this commit | (unreached under RED) -> PASS |
| Construct G boundary (mitex): zero-blank-line form absent | `21df46a` | this commit | PASS -> PASS |
| Construct H invariance (mitex) | `21df46a` | this commit | PASS -> PASS (byte-identical both sides) |
| Construct E boundary (native): GREEN string present | `21df46a` | this commit | FAIL -> PASS |
| Construct E boundary (native): two-blank-line form absent | `21df46a` | this commit | (unreached under RED) -> PASS |
| Construct E boundary (native): zero-blank-line form absent | `21df46a` | this commit | PASS -> PASS |
| Construct G boundary (native): GREEN string present | `21df46a` | this commit | FAIL -> PASS |
| Construct G boundary (native): two-blank-line form absent | `21df46a` | this commit | (unreached under RED) -> PASS |
| Construct G boundary (native): zero-blank-line form absent | `21df46a` | this commit | PASS -> PASS |
| Construct H invariance (native) | `21df46a` | this commit | PASS -> PASS (byte-identical both sides) |
| PDF-text invariance guard (both paths) | `21df46a` | this commit | PASS -> PASS (trivially green pre-fix, stayed green) |

### Regression net

- `uv run pytest tests/test_inline_math_after_text_render_gate.py -q` --
  3 passed.
- `uv run pytest tests/test_desc_rubric_decoupling_render_gate.py -q` --
  3 passed. The SC#2 golden is untouched by MATH-02 (the decoupling fixture
  contains no math), confirming D-07's commit separation held.
- `uv run pytest -q --tb=no -rf` (full suite): **653 passed, 1 skipped, 0
  failed** -- one more passed than Plan 02's recorded post-decoupling
  baseline (`652 passed, 1 skipped, 0 failed`), exactly accounting for the
  one new test method (`test_block_math_pdf_text_is_invariant_across_the_math02_fix`)
  added in Task 2. Zero regressions anywhere else in the suite.
- `uv run black --check .`, `uv run ruff check .`, `uv run mypy typsphinx/`
  all exit `0`.
- `git status --porcelain typsphinx/` and repo-wide `git status --short`
  confirm only `typsphinx/translator.py` changed by this task's code edit,
  plus this evidence file -- `tests/test_math_mitex.py`,
  `tests/test_math_native.py`, and `tests/test_math_fallback.py` are
  untouched across the whole phase.

## Regression sweep — suite, lint, invariants (SC#4)

- **Commit measured:** `7dde181056d975dc11d99abfa348fda3fe3e9efb` (this
  plan's starting commit, `docs(phase-36): update tracking after wave 3` --
  `typsphinx/` and `tests/` are unchanged by this plan; this plan writes
  only this evidence file and the deferred `par()`-loss todo).
- **Date:** 2026-08-01T01:03:57Z
- **Worktree provisioning:** `uv sync --extra dev --extra docs` (the
  `docs` extra added so a docs dogfooding-style build is available if
  needed; it installs an already-pinned optional extra from the existing
  lockfile and adds no new dependency), followed by the documented NixOS
  stub-ld symlink fix (`.venv/bin/uv` -> the `/nix/store` `uv` binary,
  `.venv/bin/ruff` -> a `/nix/store` `ruff` build, since no `ruff` was on
  `PATH` outside `.venv` in this sandbox). Verified `uv run python -c
  "import typsphinx; print(typsphinx.__file__)"` resolves inside this
  worktree, not the main checkout.

### Step 1 — full suite

**Command:** `uv run pytest -q --tb=no -rf`

Verbatim tail:
```
tests/test_typst_elements_pass_through_gate.py ..........                [ 95%]
tests/test_typst_lang_gate.py .....................                     [ 98%]
tests/test_typst_string_escape_gate.py .....                             [ 99%]
tests/test_wide_table_render_gate.py .                                   [ 99%]
tests/test_xref_orphan_degrade_render_gate.py .                          [100%]

======================= 653 passed, 1 skipped in 59.64s ========================
```

Sorted complete set of failing test node IDs: **empty** -- `grep -c
"^FAILED"` over the captured output returns `0`. No `-rf` failure lines
were printed at all.

### Step 2 — set-difference comparison against Plan 01's pre-change baseline

Plan 01's recorded baseline (re-read verbatim from this file's own "Pre-
change full-suite baseline (SC#4)" section above, not from memory): the
sorted set of OTHER failing node IDs (excluding Plan 01's own intentional
SC#1 RED, which flipped GREEN in Plan 02) is **empty**.

This plan's post-change sorted set of failing node IDs (Step 1, above) is
also **empty**.

| Group | Members |
|-------|---------|
| Failing before AND after (environmental, carried) | none -- empty |
| Failing only after (regressions -- would block the phase) | none -- empty |
| Failing only before (fixed incidentally) | none -- empty |

**Verdict:** all three groups are empty. The post-change failing set is
identical to the pre-change baseline set (both empty), so SC#4's
acceptance ("post-change failing node-ID set == the Plan 01 pre-change
set") is satisfied by direct set equality, not by an absolute-zero
argument -- it happens that both sets are the empty set in this run,
consistent with Plan 01's note that the `.venv/bin/uv`/`.venv/bin/ruff`
symlink fix eliminates the environmental failure class entirely in this
sandbox.

The total-pass-count trend across the phase's four plans: `1 failed, 651
passed, 1 skipped` (Plan 01, pre-decoupling) -> `652 passed, 1 skipped, 0
failed` (Plan 02, post-decoupling) -> `653 passed, 1 skipped, 0 failed`
(Plan 03, post-MATH-02) -> `653 passed, 1 skipped, 0 failed` (this plan,
Plan 04 -- unchanged, since this plan adds no test and touches no code).

### Step 3 — lint/type trio

| Command | Exit status | Last output line |
|---------|--------------|-------------------|
| `uv run black --check .` | `0` | "All done! ✨ 🍰 ✨ / 175 files would be left unchanged." |
| `uv run ruff check .` | `0` | "All checks passed!" |
| `uv run mypy typsphinx/` | `0` | "Success: no issues found in 6 source files" |

### Step 4 — milestone invariants

**Dependency surface unchanged:**
```
$ git diff b37ea402733c9ed6610c873349dca4c520ae7f22 HEAD -- pyproject.toml uv.lock
```
Verbatim output: **(empty)**. Exit status `0`. Neither file changed
anywhere in the phase, from the Plan 01 pre-decoupling baseline commit
through this plan's own HEAD.

**`@preview` lockstep invariant:**
```
$ uv run pytest tests/test_preview_version_sync.py -q
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-af336fd1660ce11ff
configfile: pyproject.toml
plugins: cov-7.1.0
collected 3 items

tests/test_preview_version_sync.py ...                                   [100%]

============================== 3 passed in 0.01s ===============================
```
Exit status `0`.

**Full phase touch-set:**
```
$ git diff b37ea402733c9ed6610c873349dca4c520ae7f22 HEAD --name-only
.planning/REQUIREMENTS.md
.planning/ROADMAP.md
.planning/STATE.md
.planning/phases/36-shared-emission-seam-cleanup/36-01-SUMMARY.md
.planning/phases/36-shared-emission-seam-cleanup/36-02-SUMMARY.md
.planning/phases/36-shared-emission-seam-cleanup/36-03-SUMMARY.md
.planning/phases/36-shared-emission-seam-cleanup/36-GATE-EVIDENCE.md
tests/fixtures/inline_math_after_text_render_gate/index.rst
tests/fixtures/inline_math_pdf_text_mitex.golden.txt
tests/fixtures/inline_math_pdf_text_native.golden.txt
tests/test_inline_math_after_text_render_gate.py
typsphinx/translator.py
```
Every entry is either a test file (`tests/test_inline_math_after_text_render_gate.py`),
a fixture file (the three `tests/fixtures/...` paths), the single source
file `typsphinx/translator.py`, or a planning artifact (`.planning/...`).
This diff is scoped from `b37ea40` (the SHA Plan 02/Plan 03 both name as
"the Plan 01 baseline commit"), which post-dates Plan 01's own Task 1
commit (`73a19db`) that created `tests/fixtures/desc_rubric_decoupling_render_gate/`
and `tests/test_desc_rubric_decoupling_render_gate.py` -- those files are
therefore already present, unchanged, at `b37ea40` and so do not appear
in this particular diff even though they are part of the phase's work.
The Test-migration census below (Task 2) uses the true phase-start commit
(`83114d2`, immediately preceding Plan 01's first commit) so it lists
every test file the whole phase touched, not only the subset visible from
the `b37ea40` baseline.

**No skip/xfail/deselect added:**
```
$ git diff b37ea402733c9ed6610c873349dca4c520ae7f22 HEAD -- tests/ | grep -E '^\+.*(xfail|--deselect)'
```
Verbatim output: **(empty)**. Exit status `1` (grep found no match).

## Regression sweep — corpus gate (SC#4)

**Command:** `uv run pytest tests/test_corpus_gate.py -q -m slow`

Verbatim output:
```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-af336fd1660ce11ff
configfile: pyproject.toml
plugins: cov-7.1.0
collected 5 items / 3 deselected / 2 selected

tests/test_corpus_gate.py .s                                             [100%]

================= 1 passed, 1 skipped, 3 deselected in 13.98s ==================
```

Verbose breakdown (`-v -rs`), to attribute the pass and the skip to named
tests:
```
tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error PASSED [ 50%]
tests/test_corpus_gate.py::test_empty_url_before_after SKIPPED (SC#3
before/after measurement is env-gated -- set TYPSPHINX_CORPUS_REPORT=1
to run it (RESEARCH Open Question 1))                                    [100%]
```

This gate is a **real pass**, not a skip described as a pass: the full-
corpus `-b typstpdf` gate itself
(`TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error`) ran the
real network-cached Sphinx corpus clone and the real `typst.compile()`
pipeline end to end and passed fatal-free. The one skip
(`test_empty_url_before_after`) is a different, unrelated test in the
same module -- its own documented env-gate requiring
`TYPSPHINX_CORPUS_REPORT=1`, not part of this phase's regression surface
(same disposition Phase 34's `34-GATE-EVIDENCE.md` recorded for the
identical skip). The 3 deselected tests are the module's fast non-`slow`
unit tests, already exercised in Step 1's full-suite run above.
