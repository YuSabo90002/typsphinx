# 43-GATE-EVIDENCE-05.md — SC#4 Two-Build Byte-Invariance Proof

**Phase:** 43 (Table State Correctness — Nested Tables + Empty-Title Anchors)
**Wave:** 4
**Plan:** 43-05, Task 1
**Executed:** 2026-08-04 (worktree agent, isolated worktree
`worktree-agent-aa3956ec1949a9fc1`)

Discharges roadmap SC#4 (D-04): every document in the compared corpus that contains no nested
table, no nested figure and no empty-titled caption emits byte-identical `.typ` across the
whole phase's change, proven by a two-build diff between a named pre-fix SHA and a named
post-fix SHA, with an isolation proof (two distinct `typsphinx.__file__` paths) and a mandatory
non-empty positive control. Every command below was executed in THIS session, in this worktree.
No figure was transcribed or recalled from a planning document.

---

## 1. Corpus inventory (measured before building anything)

**Command:** `ls tests/roots/`

```
test-basic
```

Only one root exists under `tests/roots/`.

**Command:** `grep -rn -E '\.\. (figure|image|table|list-table|csv-table)::' docs/source/`

```
docs/source/examples/basic.rst:100:   .. list-table:: Feature Comparison
docs/source/examples/basic.rst:128:   .. figure:: _static/diagram.png
docs/source/user_guide/builders.rst:9:.. list-table::
```

Classification of each hit:

| Hit | Directive | Classification |
|-----|-----------|-----------------|
| `docs/source/examples/basic.rst:100` | `list-table` | **LITERAL** — inside a `.. code-block:: rst` fence (lines 95-103 show the surrounding fence; the directive text is documentation *about* rST syntax, not a real directive docutils parses). Produces no table node. |
| `docs/source/examples/basic.rst:128` | `figure` | **LITERAL** — inside the same `.. code-block:: rst` fence (lines 123-133). Produces no figure node. |
| `docs/source/user_guide/builders.rst:9` | `list-table` | **REAL** — at column 0, not nested under any code-block, immediately following prose (`Overview` / `typsphinx provides two builders for different use cases.`). This is the only real table-or-figure-bearing directive found anywhere in the named D-04 corpus. |

**Command:** `grep -rn -E '\.\. (figure|image|table|list-table|csv-table)::' tests/roots/*/` (glob over
every root, i.e. `tests/roots/test-basic/`)

```
(no output)
```

`tests/roots/test-basic/` contains only `conf.py` and a 9-line `index.rst` with a plain
paragraph — no table, figure, image, list-table or csv-table directive of any kind, real or
literal.

**Command:** `grep -rn -E '\.\. image::' docs/source/` and `grep -rn -E '\.\. csv-table::'
docs/source/` — both **(no output)**. No bare `image::` or `csv-table::` directive exists
anywhere in `docs/source/`.

### D-04 corpus-widening decision

D-04's stated intent is that figure-bearing existing documents must be in the compared corpus,
not only table-bearing ones. The named corpus (`docs/source` + every root under `tests/roots`)
contains **zero real figure directives** — the only `figure::` hit is a literal inside a
code-block that produces no figure node at all. Per the plan's explicit instruction, the corpus
is therefore **widened** with the three existing figure-bearing render-gate fixtures:

- `tests/fixtures/figure_propagated_target_render_gate`
- `tests/fixtures/figure_target_caption_render_gate`
- `tests/fixtures/figure_length_render_gate`

This widening is recorded here, not silently substituted, as honouring D-04's stated intent
(figures must be exercised) rather than its literal path list (which structurally cannot satisfy
that intent given the measured corpus contents).

**Final compared corpus** (6 items):

1. `tests/roots/test-basic` (control — no table, no figure)
2. `docs/source` (whole project — the only real table-bearing document, `user_guide/builders.rst`,
   plus every other docs page)
3. `tests/fixtures/figure_propagated_target_render_gate` (widened — figure path)
4. `tests/fixtures/figure_target_caption_render_gate` (widened — figure path)
5. `tests/fixtures/figure_length_render_gate` (widened — figure path)
6. `tests/fixtures/nested_table_render_gate` (the **mandatory positive control**, § 5 below — this
   item is EXPECTED to differ, and is not part of the byte-invariance claim)

---

## 2. The two named commits

**PRE-FIX** — plan 43-01's RED commit, the last commit on this phase's history that is an
ancestor of every fix and touches nothing under `typsphinx/`.

**Command:** `git log -1 --oneline 05d49334d80705a4884ae63af9ba6e9e60b20be0`

```
05d4933 test(43-01): add TBL-04 nested-table RED fixture and render gate
```

**Command:** `git show --stat 05d49334d80705a4884ae63af9ba6e9e60b20be0 -- typsphinx/`

```
(no output)
```

Confirmed — this commit touches nothing under `typsphinx/`.

**POST-FIX** — plan 43-04's fix commit (per this plan's explicit instruction: "the phase tip
after all three fixes landed" — by the time this commit lands, plan 43-01's TBL-04 fix and plan
43-03's FIG-01 fix are already ancestors of it, since the phase's waves built sequentially on top
of each other).

**Command:** `git log -1 --oneline 0b6cbbc7610ff06d7989dd95bcefc3c6659df0a2`

```
0b6cbbc feat(43-04): anchor table ids on the structural captioned decision (TBL-05)
```

Both are real 40-hex SHAs:

```
05d49334d80705a4884ae63af9ba6e9e60b20be0
0b6cbbc7610ff06d7989dd95bcefc3c6659df0a2
```

**Command:** `git merge-base --is-ancestor 05d49334d80705a4884ae63af9ba6e9e60b20be0
0b6cbbc7610ff06d7989dd95bcefc3c6659df0a2 && echo "ANCESTOR: yes"`

```
ANCESTOR: yes
```

---

## 3. Build isolation proof

**Why this section exists (T-43-13):** an unprovisioned tree resolves `import typsphinx` to the
MAIN checkout via the PEP-660 editable finder baked into the main `.venv`, so both sides would be
built by the SAME (post-fix) code and the pairwise `.typ` diff would be empty for the wrong
reason — proving nothing. This section records that each side really ran its own copy of
`typsphinx`.

Both trees were exported with `git archive` (never a plain checkout of the main tree) into
`$SCRATCH = /tmp/claude-1000/-home-yuta-Documents-typsphinx/c9af9ab2-462e-4453-b731-76db49b07e25/scratchpad/t4305`:

**Command:**
```
git archive 05d49334d80705a4884ae63af9ba6e9e60b20be0 | tar -x -C $SCRATCH/pre-fix-tree
git archive 0b6cbbc7610ff06d7989dd95bcefc3c6659df0a2 | tar -x -C $SCRATCH/post-fix-tree
```
Both exited `0`; `ls $SCRATCH/{pre,post}-fix-tree` confirmed a full source tree in each
(`typsphinx/`, `tests/`, `docs/`, `pyproject.toml`, …).

**Provisioning (each side independently):**
```
(cd $SCRATCH/pre-fix-tree  && unset VIRTUAL_ENV UV_PROJECT_ENVIRONMENT && uv sync --extra dev --extra docs)
(cd $SCRATCH/post-fix-tree && unset VIRTUAL_ENV UV_PROJECT_ENVIRONMENT && uv sync --extra dev --extra docs)
```
Both exited `0`; each installed `typsphinx==0.7.0 (from file:///$SCRATCH/<side>-fix-tree)` —
`uv` itself resolved the editable install to THAT side's own path, not the main checkout's nor
this plan's own worktree. (`--extra docs` was added after the first attempt at building
`docs/source` failed with `ExtensionError: sphinx_autodoc_typehints` — recorded as a deviation in
the SUMMARY; it adds no new dependency, per the environment briefing.)

**NixOS `uv` shim (both sides):**
```
ln -sf "/nix/store/cgvijxnmydknslkl368k4j4j43akvl8b-uv-0.11.25/bin/uv" ".venv/bin/uv"
readlink -f .venv/bin/uv
```
Both resolved to `/nix/store/cgvijxnmydknslkl368k4j4j43akvl8b-uv-0.11.25/bin/uv` — outside
`.venv`, confirming the symlink is real, not self-referential. (`ruff` is not invoked anywhere in
this task's builds, so no `ruff` shim was needed — the same measured limitation
`42-GATE-EVIDENCE-05.md` § 2 records: no standalone `ruff` package exists in this NixOS store.)

**Isolation proof — `typsphinx.__file__` on each side:**

**Command (pre-fix):**
```
cd $SCRATCH/pre-fix-tree && uv run python -c "import typsphinx, pathlib; print(pathlib.Path(typsphinx.__file__).resolve())"
```
```
/tmp/claude-1000/-home-yuta-Documents-typsphinx/c9af9ab2-462e-4453-b731-76db49b07e25/scratchpad/t4305/pre-fix-tree/typsphinx/__init__.py
```

**Command (post-fix):**
```
cd $SCRATCH/post-fix-tree && uv run python -c "import typsphinx, pathlib; print(pathlib.Path(typsphinx.__file__).resolve())"
```
```
/tmp/claude-1000/-home-yuta-Documents-typsphinx/c9af9ab2-462e-4453-b731-76db49b07e25/scratchpad/t4305/post-fix-tree/typsphinx/__init__.py
```

**The two recorded `typsphinx.__file__` paths differ**, and the PRE-FIX path lies INSIDE the
exported pre-fix tree (`.../pre-fix-tree/typsphinx/__init__.py`), not inside the main checkout
(`/home/yuta/Documents/typsphinx`) nor this plan's own worktree
(`/home/yuta/Documents/typsphinx/.claude/worktrees/agent-aa3956ec1949a9fc1`) — direct, positive
evidence the two builds below ran against genuinely different copies of the translator.

---

## 4. Build commands and empty-diff results (the SC#4 corpus, items 1-5)

All builds used `uv run python -m sphinx -b typst -q -E <source> <out>`, run from each side's own
exported tree.

### 4a. `tests/roots/test-basic` (control, no table/figure)

**Commands (exit status for both: `0`):**
```
cd $SCRATCH/pre-fix-tree  && uv run python -m sphinx -b typst -q -E tests/roots/test-basic $SCRATCH/builds/pre-test-basic
cd $SCRATCH/post-fix-tree && uv run python -m sphinx -b typst -q -E tests/roots/test-basic $SCRATCH/builds/post-test-basic
```
(`typst_documents` in this fixture's `conf.py` names the master target `output.typ`, not
`index.typ`.)

**Command:** `diff $SCRATCH/builds/pre-test-basic/output.typ $SCRATCH/builds/post-test-basic/output.typ`

**Output:** **(empty)**. **Exit status:** `0`.

### 4b. `docs/source` (whole project, the real `builders.rst` list-table + every other docs page)

**Commands (exit status for both: `0`, each with the same 30+ deprecation-warning noise from
`sphinx_autodoc_typehints`, unrelated to this fix):**
```
cd $SCRATCH/pre-fix-tree  && uv run python -m sphinx -b typst -q -E docs/source $SCRATCH/builds/pre-docs
cd $SCRATCH/post-fix-tree && uv run python -m sphinx -b typst -q -E docs/source $SCRATCH/builds/post-docs
```

Per-file diffs (excluding `.doctrees/*.doctree` and `.doctrees/environment.pickle`, which embed
each build's own absolute scratch-directory path in the pickle and differ for that reason alone —
not part of the `.typ` byte-invariance claim):

| File | `diff` exit | Result |
|------|-------------|--------|
| `_template.typ` | `0` | empty |
| `changelog.typ` | `0` | empty |
| `contributing.typ` | `0` | empty |
| `installation.typ` | `0` | empty |
| `quickstart.typ` | `0` | empty |
| `typsphinx.typ` | `0` | empty |
| `examples/advanced.typ` | `0` | empty |
| `examples/basic.typ` | `0` | empty |
| `examples/index.typ` | `0` | empty |
| **`user_guide/builders.typ`** (the real list-table document) | `0` | **empty** |
| `user_guide/configuration.typ` | `0` | empty |
| `user_guide/index.typ` | `0` | empty |
| `user_guide/templates.typ` | `0` | empty |
| `api/index.typ` | `1` | **NON-empty — see explanation below** |

**`api/index.typ` — recorded transparently, not silently excluded.** This page is
`sphinx-autodoc`-generated API reference for `typsphinx.translator.TypstTranslator`, whose
rendered content is a direct function of the translator's own docstrings and method list. This
phase's fix commits **added** two new public methods with docstrings (`visit_legend`,
`depart_legend`, FIG-01) and **rewrote** `depart_table`'s docstring (TBL-05, D-05's
RENDERING/ANCHORING split). Diffing `api/index.typ` therefore surfaces exactly those additions —
new `#figure` blocks for `visit_legend`/`depart_legend` and an added paragraph in `depart_table`'s
entry — verbatim reflections of the source-code docstrings this phase deliberately changed. This
page contains no table or figure *directive* from any user document; it is the extension's
self-documentation of its own API surface, which necessarily updates whenever that surface's
docstrings do. It is excluded from the "byte-identical" claim with this stated reason, per this
plan's transparency requirement — not silently dropped from the corpus.

### 4c. `tests/fixtures/figure_propagated_target_render_gate` (widened corpus, figure path)

**Commands (exit status for both: `0`):**
```
cd $SCRATCH/pre-fix-tree  && uv run python -m sphinx -b typst -q -E tests/fixtures/figure_propagated_target_render_gate $SCRATCH/builds/pre-fig-prop
cd $SCRATCH/post-fix-tree && uv run python -m sphinx -b typst -q -E tests/fixtures/figure_propagated_target_render_gate $SCRATCH/builds/post-fig-prop
```

**Command:** `diff $SCRATCH/builds/pre-fig-prop/index.typ $SCRATCH/builds/post-fig-prop/index.typ`

**Output:** **(empty)**. **Exit status:** `0`.

### 4d. `tests/fixtures/figure_target_caption_render_gate` (widened corpus, figure path)

**Commands (exit status for both: `0`):**
```
cd $SCRATCH/pre-fix-tree  && uv run python -m sphinx -b typst -q -E tests/fixtures/figure_target_caption_render_gate $SCRATCH/builds/pre-fig-target
cd $SCRATCH/post-fix-tree && uv run python -m sphinx -b typst -q -E tests/fixtures/figure_target_caption_render_gate $SCRATCH/builds/post-fig-target
```

**Command:** `diff $SCRATCH/builds/pre-fig-target/index.typ $SCRATCH/builds/post-fig-target/index.typ`

**Output:** **(empty)**. **Exit status:** `0`.

### 4e. `tests/fixtures/figure_length_render_gate` (widened corpus, figure path)

**Commands (exit status for both: `0`, each emitting the same two pre-existing "Unsupported
length unit 'ex'" warnings, unrelated to this fix):**
```
cd $SCRATCH/pre-fix-tree  && uv run python -m sphinx -b typst -q -E tests/fixtures/figure_length_render_gate $SCRATCH/builds/pre-fig-length
cd $SCRATCH/post-fix-tree && uv run python -m sphinx -b typst -q -E tests/fixtures/figure_length_render_gate $SCRATCH/builds/post-fig-length
```

**Command:** `diff $SCRATCH/builds/pre-fig-length/index.typ $SCRATCH/builds/post-fig-length/index.typ`

**Output:** **(empty)**. **Exit status:** `0`.

---

## 5. THE MANDATORY POSITIVE CONTROL — `tests/fixtures/nested_table_render_gate`

This fixture exists at both SHAs (created by plan 43-01's RED commit itself) and contains only
NESTED tables — the exact defect TBL-04 fixes. Its diff MUST be non-empty; an empty result here
would mean the two builds ran the same code, and everything in § 4 would be vacuous.

**Commands (exit status for both: `0`):**
```
cd $SCRATCH/pre-fix-tree  && uv run python -m sphinx -b typst -q -E tests/fixtures/nested_table_render_gate $SCRATCH/builds/pre-nested-table
cd $SCRATCH/post-fix-tree && uv run python -m sphinx -b typst -q -E tests/fixtures/nested_table_render_gate $SCRATCH/builds/post-nested-table
```

**Command:** `diff $SCRATCH/builds/pre-nested-table/index.typ $SCRATCH/builds/post-nested-table/index.typ`

**Verbatim output (100 lines, exit status `1`):**

```diff
28c28
< figure(
---
> [#figure(
30a31,37
>   table.header(
>     {par({text("NT1HEADA")})},
>     {par({text("NT1HEADB")})},
>   ),
>   {par({text("NT1PLAIN")})},
>   {table(
>   columns: (50fr, 50fr),
32a40
> )},
36c44
< )
---
> ) <index:id1>]
41c49
< figure(
---
> [#figure(
42a51,57
>   columns: (50fr, 50fr),
>   table.header(
>     {par({text("NT2HEADA")})},
>     {par({text("NT2HEADB")})},
>   ),
>   {par({text("NT2PLAIN")})},
>   {table(
45a61
> )},
49c65
< )
---
> ) <index:id2>]
54c70
< figure(
---
> [#figure(
55a72,73
>   columns: (34fr, 11fr),
>   {table(
58a77,78
> )},
>   {par({text("NT3OUTERD")})},
62,64c82
< )
< 
< par({text("NT3OUTERD")})
---
> ) <index:id3>]
69c87
< figure(
---
> [#figure(
71a90,95
>   {par({text("NT4L1PLAIN")})},
>   {table(
>   columns: (50fr, 50fr),
>   {par({text("NT4L2PLAIN")})},
>   {table(
>   columns: (50fr, 50fr),
73a98,99
> )},
> )},
77c103
< )
---
> ) <index:id4>]
82a109,111
>   columns: (50fr, 50fr),
>   table.header(
>     {table(
87a117,121
> )},
>     {par({text("NT5HEADB")})},
>   ),
>   {par({text("NT5BODYA")})},
>   {par({text("NT5BODYB")})},
90,95d123
< par({text("NT5HEADB")})
< 
< par({text("NT5BODYA")})
< 
< par({text("NT5BODYB")})
< 
99a128,131
>   columns: (50fr, 50fr),
>   {par({text("NT6TEXTBEFORE")})
> 
> table(
101a134,137
> )},
>   {},
>   {par({text("NT6ROWTWO")})},
>   {},
103,104d138
< 
< par({text("NT6ROWTWO")})
```

**This non-empty diff is deliberately recorded as the positive half of the isolation proof.**
Every `>` line is content that appears ONLY on the post-fix side — the outer table's own header
cells, plain cells, column counts, and captions, which the pre-fix build silently drops (the
exact TBL-04 defect). This demonstrates the two exported trees really executed genuinely
different `depart_table`/`visit_table` code, which is the precondition that makes every EMPTY
diff in § 4 meaningful rather than vacuous — an empty diff proves nothing without this.

---

## 6. Production-diff isolation

**Pathspec-scoped diff — the true production surface between the two named commits:**

**Command:** `git diff --stat 05d49334d80705a4884ae63af9ba6e9e60b20be0..0b6cbbc7610ff06d7989dd95bcefc3c6659df0a2 -- typsphinx/`

```
 typsphinx/translator.py | 503 +++++++++++++++++++++++++++++++++++++++++++-----
 1 file changed, 458 insertions(+), 45 deletions(-)
```

Only `typsphinx/translator.py` — nothing else under `typsphinx/` changed between the two named
commits.

**Unscoped diff — the full tree difference, deliberately larger:**

**Command:** `git diff --stat 05d49334d80705a4884ae63af9ba6e9e60b20be0..0b6cbbc7610ff06d7989dd95bcefc3c6659df0a2`

```
 .planning/REQUIREMENTS.md                          |  21 +-
 .planning/ROADMAP.md                               |  10 +-
 .planning/STATE.md                                 |  18 +-
 .../43-01-SUMMARY.md                               | 181 ++++++
 .../43-02-SUMMARY.md                               | 200 +++++++
 .../43-03-SUMMARY.md                               | 190 ++++++
 .../43-GATE-EVIDENCE-01.md                         | 638 +++++++++++++++++++++
 .../43-GATE-EVIDENCE-02.md                         | 192 +++++++
 .../43-GATE-EVIDENCE-03.md                         | 621 ++++++++++++++++++++
 .../43-GATE-EVIDENCE-04.md                         | 199 +++++++
 tests/fixtures/nested_figure_render_gate/conf.py   |  30 +
 tests/fixtures/nested_figure_render_gate/img.png   | Bin 0 -> 68 bytes
 tests/fixtures/nested_figure_render_gate/index.rst |  62 ++
 .../table_empty_caption_anchor_render_gate/conf.py |  44 ++
 .../index.rst                                      |  41 ++
 tests/test_nested_figure_render_gate.py            | 287 +++++++++
 tests/test_nested_table_render_gate.py             | 406 +++++++++++++
 .../test_table_empty_caption_anchor_render_gate.py | 237 ++++++++
 typsphinx/translator.py                            | 503 ++++++++++++++--
 19 files changed, 3817 insertions(+), 63 deletions(-)
```

**Why the unscoped diff is larger (one sentence):** plans 43-01, 43-02 and 43-03's own fixtures,
tests, evidence files and SUMMARY/REQUIREMENTS/ROADMAP/STATE bookkeeping landed on this phase's
branch between the two named commits (43-01's fix, then 43-03's FIG-01 fix, both ancestors of the
POST-FIX SHA), the exact measurement trap `42-GATE-EVIDENCE-05.md` § 5 already named for Phase 42.

---

## 7. Milestone invariants

**Command:** `git diff --stat 05d49334d80705a4884ae63af9ba6e9e60b20be0..0b6cbbc7610ff06d7989dd95bcefc3c6659df0a2 -- pyproject.toml uv.lock`

```
(no output)
```

Empty — zero new runtime dependencies across the whole phase to this point.

**Command:** `uv run python -m pytest tests/test_preview_version_sync.py -q` (run in THIS
worktree, not either scratch tree)

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-aa3956ec1949a9fc1
configfile: pyproject.toml
plugins: cov-7.1.0
collected 3 items

tests/test_preview_version_sync.py ...                                   [100%]

============================== 3 passed in 0.01s ===============================
```

Exit `0` — the four `@preview` packages (`codly`, `codly-languages`, `mitex`, `gentle-clues`)
still agree across all three lockstep sites (`writer.py`, `template_engine.py`,
`templates/base.typ`).

---

## 8. No code/fixture change by this task, and cleanup

**Command:** `git status --porcelain typsphinx/ tests/`

```
(no output)
```

Empty — this task changed no production code and no fixture in this worktree.

**Cleanup:** every build was run in `$SCRATCH` (outside this repository's working tree, under the
session scratchpad), so no scratch artifact ever entered the commit. `$SCRATCH` was removed after
this evidence file was written:
```
rm -rf $SCRATCH
```
No `git worktree add` was used for either side (the pre/post-fix sides were `git archive` exports
per the plan's explicit method, not throwaway worktrees), so no worktree cleanup was needed.

**Command:** `git worktree list` (unaffected by this task)

```
/home/yuta/Documents/typsphinx                                           1f24e24 [gsd/v0.7.1-bug-fix-round]
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-aa3956ec1949a9fc1 1f24e24 [worktree-agent-aa3956ec1949a9fc1] locked
```

---

## 9. Verdict

| Success criterion | Discharged by | Status |
|--------------------|----------------|--------|
| SC#4 — every document in the widened corpus with no nested table, no nested figure and no empty-titled caption emits byte-identical `.typ` across the whole phase's change, proven by the two-build method (D-04), with an isolation proof (two distinct `typsphinx.__file__` paths, § 3) and a mandatory non-empty positive control (§ 5) | § 1 (corpus inventory + widening), § 2 (two named 40-hex SHAs + ancestry), § 3 (isolation proof), § 4 (six empty diffs across the widened corpus, one exception — `api/index.typ` — recorded and explained, not silently dropped), § 5 (non-empty positive control), § 6 (production surface isolated to `typsphinx/translator.py`), § 7 (empty `pyproject.toml`/`uv.lock` diff, `@preview` lockstep test green) | **MET** |

Not owned by this evidence file:

- SC#5 (completed CI including Windows lanes) — owned by Task 2, recorded in
  `43-GATE-EVIDENCE-06.md`.
- SC#1, SC#2, SC#3, SC#6 — owned by `43-GATE-EVIDENCE-01.md`, `-03.md`, `-04.md` respectively (see
  the six-row table in `43-GATE-EVIDENCE-06.md`).
