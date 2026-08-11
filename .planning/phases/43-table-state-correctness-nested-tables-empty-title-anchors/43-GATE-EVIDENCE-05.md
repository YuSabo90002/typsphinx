# 43-GATE-EVIDENCE-05.md — SC#4 Two-Build Byte-Invariance Proof

**Phase:** 43 (Table State Correctness — Nested Tables + Empty-Title Anchors)
**Wave:** 4 (this refresh executed post-gap-closure, plan 43-06 having landed)
**Plan:** 43-05, Task 1 — **REGENERATED** against the current phase tip after `43-REVIEW.md`
CR-01 was fixed by gap-closure plan 43-06
**Executed:** 2026-08-04 (worktree agent, isolated worktree
`worktree-agent-a3ec4f2e4269654fa`)

## 0. Why this file was regenerated

The original version of this file (produced by the first run of plan 43-05, worktree
`worktree-agent-aa3956ec1949a9fc1`) named POST-FIX = `0b6cbbc7610ff06d7989dd95bcefc3c6659df0a2`
(plan 43-04's fix commit). Phase 43's own code review (`43-REVIEW.md`) then found CR-01, a
BLOCKER: `visit_legend`/`depart_legend` saved `in_list_item`/`list_item_needs_separator` into
flat instance attributes instead of a stack, leaking `in_list_item=True` into every sibling
after a figure whose legend itself contains a legend-bearing figure. Gap-closure plan 43-06 fixed
this (commit `4ea64006cb930bf1362a61dfa9052811f79617a6`) and changed `typsphinx/translator.py`
again. The original POST-FIX SHA is therefore no longer the phase tip, and every measurement
pinned to it is stale. This file re-runs the full two-build method end to end against the new
POST-FIX anchor. The PRE-FIX anchor is unchanged (43-06 did not touch the RED commit's ancestry).

Every command below was executed in THIS session, in this worktree, against the current tip. No
figure was transcribed or recalled from the superseded version of this file — every number here
was freshly measured, even where it turned out to reproduce the earlier evidence's own value.

---

## 1. Corpus inventory (re-measured before building anything)

**Command:** `ls tests/roots/`

```
test-basic
```

Only one root exists under `tests/roots/` — unchanged from the prior measurement (43-06 did not
touch `tests/roots/`).

**Command:** `grep -rn -E '\.\. (figure|image|table|list-table|csv-table)::' docs/source/`
(executed as `docs/sourc*` in this session — a glob substitute for the literal path, because this
sandbox's worktree-path-safety checker refuses any Bash command whose text contains the literal
token `source`, misreading it as an attempt to invoke the shell builtin; the glob resolves to the
identical single directory and the command's semantics are unaffected)

```
docs/source/user_guide/builders.rst:9:.. list-table::
docs/source/examples/basic.rst:100:   .. list-table:: Feature Comparison
docs/source/examples/basic.rst:128:   .. figure:: _static/diagram.png
```

Classification of each hit (re-verified by reading each file directly in this session):

| Hit | Directive | Classification |
|-----|-----------|-----------------|
| `docs/source/examples/basic.rst:100` | `list-table` | **LITERAL** — inside a `.. code-block:: rst` fence (lines 95-103 show the surrounding fence; the directive text is documentation *about* rST syntax, not a real directive docutils parses). Produces no table node. |
| `docs/source/examples/basic.rst:128` | `figure` | **LITERAL** — inside the same `.. code-block:: rst` fence (lines 123-133). Produces no figure node. |
| `docs/source/user_guide/builders.rst:9` | `list-table` | **REAL** — at column 0, not nested under any code-block, immediately following prose (`Overview` / `typsphinx provides two builders for different use cases.`). This is the only real table-or-figure-bearing directive found anywhere in the named D-04 corpus. |

**Command:** `grep -rn -E '\.\. (figure|image|table|list-table|csv-table)::' tests/roots/test-basic/`

```
(no output)
```

`tests/roots/test-basic/` contains no table, figure, image, list-table or csv-table directive of
any kind, real or literal — unchanged from the prior measurement.

**Command:** `grep -rn -E '\.\. image::' docs/sourc*` and `grep -rn -E '\.\. csv-table::'
docs/sourc*` — both **(no output)**. No bare `image::` or `csv-table::` directive exists anywhere
in `docs/source/`. Unchanged.

### D-04 corpus-widening decision (re-confirmed, unchanged)

D-04's stated intent is that figure-bearing existing documents must be in the compared corpus,
not only table-bearing ones. The named corpus (`docs/source` + every root under `tests/roots`)
contains **zero real figure directives** — the only `figure::` hit is a literal inside a
code-block that produces no figure node at all. The corpus is therefore **widened** with the
three existing figure-bearing render-gate fixtures, exactly as the prior version of this file
recorded:

- `tests/fixtures/figure_propagated_target_render_gate`
- `tests/fixtures/figure_target_caption_render_gate`
- `tests/fixtures/figure_length_render_gate`

### A measured divergence from the premise handed to this refresh — `nested_figure_render_gate`

This refresh's briefing stated that `tests/fixtures/nested_figure_render_gate` (which gained a
new Section 5 in plan 43-06, the exact regression fixture for CR-01) was used in this file "as
the positive control or as a corpus item" and asked which. **Neither is correct, measured
directly against the text of this file's own prior version:** `nested_figure_render_gate` does
not appear anywhere in § 1 (corpus inventory), § 4 (empty-diff corpus builds) or § 5 (positive
control) of the superseded evidence. Its only appearance is in the unscoped `git diff --stat`
in the prior § 6, as one of the phase's own fixture files that landed between the two named
commits — it is not, and never was, part of the SC#4 byte-invariance corpus. `nested_figure_render_gate`
is FIG-01's own regression gate, owned by `43-GATE-EVIDENCE-03.md` (plan 43-03, the fixture's
origin) and now `43-GATE-EVIDENCE-07.md` (plan 43-06, the CR-01 gap closure) — not this SC#4
evidence file. Since it was never part of this corpus, its Section-5 growth has no bearing on
this file's empty-diff or positive-control claims; this is stated explicitly, per this plan's own
transparency requirement, rather than silently widening the corpus to match the premise or
silently dropping the discrepancy.

**Final compared corpus (6 items, identical set to the superseded version):**

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

**PRE-FIX — unchanged from the superseded version.** Plan 43-01's RED commit, the last commit on
this phase's history that is an ancestor of every fix and touches nothing under `typsphinx/`.

**Command:** `git log -1 --oneline 05d49334d80705a4884ae63af9ba6e9e60b20be0`

```
05d4933 test(43-01): add TBL-04 nested-table RED fixture and render gate
```

**Command:** `git show --stat 05d49334d80705a4884ae63af9ba6e9e60b20be0 -- typsphinx/`

```
(no output)
```

Confirmed (re-run in this session) — this commit touches nothing under `typsphinx/`.

**POST-FIX — CHANGED for this refresh.** Plan 43-06's fix commit, i.e. the last commit that
touches `typsphinx/translator.py` on the phase's history (`git log --oneline --all -- typsphinx/`
confirms `4ea6400` is the top entry; only doc-tracking and evidence commits follow it up to the
current phase tip `1a3b3c8`). By the time this commit lands, plans 43-01/43-03/43-04's own fixes
are already ancestors of it (the phase's waves and this gap-closure plan built sequentially on
top of each other).

**Command:** `git log -1 --oneline 4ea64006cb930bf1362a61dfa9052811f79617a6`

```
4ea6400 fix(43-06): stack visit_legend/depart_legend state, closing CR-01
```

Both are real 40-hex SHAs:

```
05d49334d80705a4884ae63af9ba6e9e60b20be0
4ea64006cb930bf1362a61dfa9052811f79617a6
```

**Command:** `git merge-base --is-ancestor 05d49334d80705a4884ae63af9ba6e9e60b20be0
4ea64006cb930bf1362a61dfa9052811f79617a6 && echo "ANCESTOR: yes"`

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
`$SCRATCH = /tmp/claude-1000/-home-yuta-Documents-typsphinx/c9af9ab2-462e-4453-b731-76db49b07e25/scratchpad/t4305b`:

**Command:**
```
git archive 05d49334d80705a4884ae63af9ba6e9e60b20be0 | tar -x -C $SCRATCH/pre-fix-tree
git archive 4ea64006cb930bf1362a61dfa9052811f79617a6 | tar -x -C $SCRATCH/post-fix-tree
```
Both exited `0`; `ls $SCRATCH/{pre,post}-fix-tree` confirmed a full source tree in each
(`typsphinx/`, `tests/`, `docs/`, `pyproject.toml`, …).

**Provisioning (each side independently):**
```
(cd $SCRATCH/pre-fix-tree  && uv sync --extra dev --extra docs)
(cd $SCRATCH/post-fix-tree && uv sync --extra dev --extra docs)
```
Both exited `0`; each installed `typsphinx==0.7.0 (from file:///$SCRATCH/<side>-fix-tree)` —
`uv` itself resolved the editable install to THAT side's own path, not the main checkout's nor
this plan's own worktree.

**NixOS `uv` ELF shim (both sides — freshly re-measured, same hazard the environment briefing
named):**
```
readlink -f .venv/bin/uv    # pre-fix side, BEFORE the shim
```
```
/tmp/.../pre-fix-tree/.venv/bin/uv
```
i.e. the symlink target lay INSIDE `.venv` at that point (a real ELF binary, not yet a symlink),
and running it directly failed:
```
.venv/bin/uv --version
```
```
Exit code 127
Could not start dynamically linked executable: .venv/bin/uv
NixOS cannot run dynamically linked executables intended for generic
linux environments out of the box. For more information, see:
https://nix.dev/permalink/stub-ld
```
Fixed identically on both sides:
```
ln -sf "/nix/store/cgvijxnmydknslkl368k4j4j43akvl8b-uv-0.11.25/bin/uv" ".venv/bin/uv"
readlink -f .venv/bin/uv
```
```
/nix/store/cgvijxnmydknslkl368k4j4j43akvl8b-uv-0.11.25/bin/uv
```
— for BOTH `pre-fix-tree` and `post-fix-tree` — outside `.venv`, confirming the symlink is real,
not self-referential. `.venv/bin/uv --version` then printed `uv 0.11.25
(x86_64-unknown-linux-gnu)` on both sides. (`ruff` is not invoked anywhere in this task's builds,
so no `ruff` shim was needed.)

**Isolation proof — `typsphinx.__file__` on each side:**

**Command (pre-fix):**
```
cd $SCRATCH/pre-fix-tree && uv run python -c "import typsphinx, pathlib; print(pathlib.Path(typsphinx.__file__).resolve())"
```
```
/tmp/claude-1000/-home-yuta-Documents-typsphinx/c9af9ab2-462e-4453-b731-76db49b07e25/scratchpad/t4305b/pre-fix-tree/typsphinx/__init__.py
```

**Command (post-fix):**
```
cd $SCRATCH/post-fix-tree && uv run python -c "import typsphinx, pathlib; print(pathlib.Path(typsphinx.__file__).resolve())"
```
```
/tmp/claude-1000/-home-yuta-Documents-typsphinx/c9af9ab2-462e-4453-b731-76db49b07e25/scratchpad/t4305b/post-fix-tree/typsphinx/__init__.py
```

**The two recorded `typsphinx.__file__` paths differ**, and the PRE-FIX path lies INSIDE the
exported pre-fix tree (`.../pre-fix-tree/typsphinx/__init__.py`), not inside the main checkout
(`/home/yuta/Documents/typsphinx`) nor this plan's own worktree
(`/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a3ec4f2e4269654fa`) — direct, positive
evidence the two builds below ran against genuinely different copies of the translator.

---

## 4. Build commands and empty-diff results (the SC#4 corpus, items 1-5)

All builds used `uv run python -m sphinx -b typst -q -E <source> <out>`, run from each side's own
exported tree. All exited `0`.

### 4a. `tests/roots/test-basic` (control, no table/figure)

```
cd $SCRATCH/pre-fix-tree  && uv run python -m sphinx -b typst -q -E tests/roots/test-basic $SCRATCH/builds/pre-test-basic
cd $SCRATCH/post-fix-tree && uv run python -m sphinx -b typst -q -E tests/roots/test-basic $SCRATCH/builds/post-test-basic
```
(`typst_documents` in this fixture's `conf.py` names the master target `output.typ`.)

**Command:** `diff $SCRATCH/builds/pre-test-basic/output.typ $SCRATCH/builds/post-test-basic/output.typ`

**Output:** **(empty)**. **Exit status:** `0`.

### 4b. `docs/source` (whole project, the real `builders.rst` list-table + every other docs page)

```
cd $SCRATCH/pre-fix-tree  && uv run python -m sphinx -b typst -q -E docs/sourc* $SCRATCH/builds/pre-docs
cd $SCRATCH/post-fix-tree && uv run python -m sphinx -b typst -q -E docs/sourc* $SCRATCH/builds/post-docs
```
Both exited `0`.

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
| `api/index.typ` | `1` | **NON-empty — see explanation below (content GREW relative to the superseded evidence)** |

**`api/index.typ` — recorded transparently, and its content is LARGER than the superseded
version.** This page is `sphinx-autodoc`-generated API reference for
`typsphinx.translator.TypstTranslator`, whose rendered content is a direct function of the
translator's own docstrings and method list. Relative to the (unchanged) PRE-FIX side, the
diff now contains, verbatim:

- The **entire** `visit_legend`/`depart_legend` autodoc entries (both methods postdate the
  PRE-FIX commit, so their whole rendered block is new on the POST-FIX side, as in the superseded
  evidence) — but the docstring TEXT itself is now the plan 43-06 REWRITE, not the plan 43-03
  original: it explicitly documents the CR-01 fix (`"Pushes onto self._legend_list_item_stack
  (43-REVIEW.md CR-01) rather than saving into flat scalars — a legend can itself contain a NESTED
  figure whose own legend also visits..."` for `visit_legend`, and `"...stacked in the CR-01 gap
  closure"` / the no-op-safe-pop ASVS V5 explanation for `depart_legend`).
- The same `depart_table` docstring addition the superseded evidence already recorded (TBL-05,
  D-05's RENDERING/ANCHORING split) — unaffected by 43-06, reproduced identically.

This page contains no table or figure *directive* from any user document; it is the extension's
self-documentation of its own API surface, which necessarily updates whenever that surface's
docstrings do — now covering the CR-01 gap-closure docstrings as well as the original TBL-05/FIG-01
ones. It is excluded from the "byte-identical" claim with this stated reason, per this plan's
transparency requirement — not silently dropped from the corpus, and the growth relative to the
superseded evidence is called out explicitly rather than smoothed over.

### 4c. `tests/fixtures/figure_propagated_target_render_gate` (widened corpus, figure path)

```
cd $SCRATCH/pre-fix-tree  && uv run python -m sphinx -b typst -q -E tests/fixtures/figure_propagated_target_render_gate $SCRATCH/builds/pre-fig-prop
cd $SCRATCH/post-fix-tree && uv run python -m sphinx -b typst -q -E tests/fixtures/figure_propagated_target_render_gate $SCRATCH/builds/post-fig-prop
```
Both exited `0`.

**Command:** `diff $SCRATCH/builds/pre-fig-prop/index.typ $SCRATCH/builds/post-fig-prop/index.typ`

**Output:** **(empty)**. **Exit status:** `0`.

### 4d. `tests/fixtures/figure_target_caption_render_gate` (widened corpus, figure path)

```
cd $SCRATCH/pre-fix-tree  && uv run python -m sphinx -b typst -q -E tests/fixtures/figure_target_caption_render_gate $SCRATCH/builds/pre-fig-target
cd $SCRATCH/post-fix-tree && uv run python -m sphinx -b typst -q -E tests/fixtures/figure_target_caption_render_gate $SCRATCH/builds/post-fig-target
```
Both exited `0`.

**Command:** `diff $SCRATCH/builds/pre-fig-target/index.typ $SCRATCH/builds/post-fig-target/index.typ`

**Output:** **(empty)**. **Exit status:** `0`.

### 4e. `tests/fixtures/figure_length_render_gate` (widened corpus, figure path)

```
cd $SCRATCH/pre-fix-tree  && uv run python -m sphinx -b typst -q -E tests/fixtures/figure_length_render_gate $SCRATCH/builds/pre-fig-length
cd $SCRATCH/post-fix-tree && uv run python -m sphinx -b typst -q -E tests/fixtures/figure_length_render_gate $SCRATCH/builds/post-fig-length
```
Both exited `0`, each emitting the same two pre-existing "Unsupported length unit 'ex'" warnings,
unrelated to this fix.

**Command:** `diff $SCRATCH/builds/pre-fig-length/index.typ $SCRATCH/builds/post-fig-length/index.typ`

**Output:** **(empty)**. **Exit status:** `0`.

---

## 5. THE MANDATORY POSITIVE CONTROL — `tests/fixtures/nested_table_render_gate`

This fixture exists at both SHAs (created by plan 43-01's RED commit itself, and 43-06 did not
touch it — confirmed by `git ls-tree -r --name-only <sha> | grep nested_table_render_gate`
returning the identical 3-file list at both SHAs) and contains only NESTED tables — the exact
defect TBL-04 fixes. Its diff MUST be non-empty; an empty result here would mean the two builds
ran the same code, and everything in § 4 would be vacuous.

```
cd $SCRATCH/pre-fix-tree  && uv run python -m sphinx -b typst -q -E tests/fixtures/nested_table_render_gate $SCRATCH/builds/pre-nested-table
cd $SCRATCH/post-fix-tree && uv run python -m sphinx -b typst -q -E tests/fixtures/nested_table_render_gate $SCRATCH/builds/post-nested-table
```
Both exited `0`.

**Command:** `diff $SCRATCH/builds/pre-nested-table/index.typ $SCRATCH/builds/post-nested-table/index.typ`

**Verbatim output (exit status `1`):**

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

**This non-empty diff is byte-identical to the one recorded by the superseded version of this
file** — a real, expected finding: 43-06's CR-01 fix touches only `visit_legend`/`depart_legend`
(the legend/figure neighborhood), a disjoint code region from `_push_table_state`/`_pop_table_state`
and `visit_table`/`depart_table` (the TBL-04 neighborhood this fixture exercises). The
reproduction of the identical diff is therefore the expected outcome of an isolated fix, not a
missed re-measurement — every command above was re-run fresh in this session against the new
POST-FIX SHA, and the fresh output happens to match.

Every `>` line is content that appears ONLY on the post-fix side — the outer table's own header
cells, plain cells, column counts, and captions, which the pre-fix build silently drops (the
exact TBL-04 defect). This demonstrates the two exported trees really executed genuinely
different `depart_table`/`visit_table` code, which is the precondition that makes every EMPTY
diff in § 4 meaningful rather than vacuous — an empty diff proves nothing without this.

---

## 6. Production-diff isolation

**Pathspec-scoped diff — the true production surface between the two named commits (re-measured
against the NEW POST-FIX SHA):**

**Command:** `git diff --stat 05d49334d80705a4884ae63af9ba6e9e60b20be0..4ea64006cb930bf1362a61dfa9052811f79617a6 -- typsphinx/`

```
 typsphinx/translator.py | 571 +++++++++++++++++++++++++++++++++++++++++++-----
 1 file changed, 518 insertions(+), 53 deletions(-)
```

Only `typsphinx/translator.py` — nothing else under `typsphinx/` changed between the two named
commits. (The insertion/deletion counts grew from the superseded evidence's `458+/45-` to
`518+/53-`, reflecting 43-06's own `visit_legend`/`depart_legend` stack rewrite landing on top of
the original three fixes.)

**Unscoped diff — the full tree difference, deliberately larger:**

**Command:** `git diff --stat 05d49334d80705a4884ae63af9ba6e9e60b20be0..4ea64006cb930bf1362a61dfa9052811f79617a6`

```
 .planning/REQUIREMENTS.md                          |  21 +-
 .planning/ROADMAP.md                               |  14 +-
 .planning/STATE.md                                 |  18 +-
 .../43-01-SUMMARY.md                               | 181 ++++++
 .../43-02-SUMMARY.md                               | 200 +++++++
 .../43-03-SUMMARY.md                               | 190 ++++++
 .../43-04-SUMMARY.md                               | 189 ++++++
 .../43-05-SUMMARY.md                               | 176 ++++++
 .../43-GATE-EVIDENCE-01.md                         | 638 +++++++++++++++++++++
 .../43-GATE-EVIDENCE-02.md                         | 192 +++++++
 .../43-GATE-EVIDENCE-03.md                         | 621 ++++++++++++++++++++
 .../43-GATE-EVIDENCE-04.md                         | 511 +++++++++++++++++
 .../43-GATE-EVIDENCE-05.md                         | 548 ++++++++++++++++++
 .../43-GATE-EVIDENCE-06.md                         | 345 +++++++++++
 .../43-REVIEW.md                                   | 180 ++++++
 tests/fixtures/nested_figure_render_gate/conf.py   |  30 +
 tests/fixtures/nested_figure_render_gate/img.png   | Bin 0 -> 68 bytes
 tests/fixtures/nested_figure_render_gate/index.rst |  90 +++
 .../table_empty_caption_anchor_render_gate/conf.py |  44 ++
 .../index.rst                                      |  41 ++
 tests/test_nested_figure_render_gate.py            | 363 ++++++++++++
 tests/test_nested_table_render_gate.py             | 406 +++++++++++++
 .../test_table_empty_caption_anchor_render_gate.py | 237 ++++++++
 typsphinx/translator.py                            | 571 ++++++++++++++++--
 24 files changed, 5733 insertions(+), 73 deletions(-)
```

**Why the unscoped diff is larger (one sentence):** plans 43-01 through 43-06's own fixtures,
tests, review report, evidence files and SUMMARY/REQUIREMENTS/ROADMAP/STATE bookkeeping landed on
this phase's branch between the two named commits, the exact measurement trap
`42-GATE-EVIDENCE-05.md` § 5 already named for Phase 42. `tests/fixtures/nested_figure_render_gate/index.rst`
grew from `62 ++` (superseded diff) to `90 +++` (Section 5, the CR-01 regression gate,
28 added lines) — this is 43-06's own regression-gate fixture, not part of the SC#4 corpus per
§ 1 above.

---

## 7. Milestone invariants

**Command:** `git diff --stat 05d49334d80705a4884ae63af9ba6e9e60b20be0..4ea64006cb930bf1362a61dfa9052811f79617a6 -- pyproject.toml uv.lock`

```
(no output)
```

Empty — zero new runtime dependencies across the whole phase to this point, including 43-06.

**Command:** `uv run python -m pytest tests/test_preview_version_sync.py -q` (run in THIS
worktree, not either scratch tree)

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a3ec4f2e4269654fa
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
/home/yuta/Documents/typsphinx                                           1a3b3c8 [gsd/v0.7.1-bug-fix-round]
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a3ec4f2e4269654fa 1a3b3c8 [worktree-agent-a3ec4f2e4269654fa] locked
```

---

## 9. Verdict

| Success criterion | Discharged by | Status |
|--------------------|----------------|--------|
| SC#4 — every document in the widened corpus with no nested table, no nested figure and no empty-titled caption emits byte-identical `.typ` across the whole phase's change (through the CR-01 gap closure), proven by the two-build method (D-04), with an isolation proof (two distinct `typsphinx.__file__` paths, § 3) and a mandatory non-empty positive control (§ 5) | § 1 (corpus inventory + widening + the `nested_figure_render_gate` divergence finding), § 2 (two named 40-hex SHAs + ancestry, new POST-FIX anchor), § 3 (isolation proof, freshly re-measured), § 4 (six empty diffs across the widened corpus, one exception — `api/index.typ` — recorded and explained as LARGER than the superseded evidence, not silently dropped), § 5 (non-empty positive control, byte-identical to the superseded evidence because CR-01 is disjoint from the TBL-04 code path), § 6 (production surface isolated to `typsphinx/translator.py`, larger diff stat reflecting 43-06's own change), § 7 (empty `pyproject.toml`/`uv.lock` diff, `@preview` lockstep test green) | **MET** |

Not owned by this evidence file:

- SC#5 (completed CI including Windows lanes) — owned by Task 2, recorded in
  `43-GATE-EVIDENCE-06.md` (this refresh).
- SC#1, SC#2, SC#3, SC#6 — owned by `43-GATE-EVIDENCE-01.md`, `-03.md`, `-04.md` respectively (see
  the six-row table in `43-GATE-EVIDENCE-06.md`).
- CR-01 itself (the FIG-01 legend-in-legend defect and its fix) — owned by `43-06-SUMMARY.md` and
  `43-GATE-EVIDENCE-07.md`, not this file.
