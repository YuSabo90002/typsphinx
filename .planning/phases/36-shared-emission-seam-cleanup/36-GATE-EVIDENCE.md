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
