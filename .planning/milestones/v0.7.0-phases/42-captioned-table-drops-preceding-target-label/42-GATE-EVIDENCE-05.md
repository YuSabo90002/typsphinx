# Phase 42, Plan 05 — GATE-05 Evidence (TBL-03, SC#4 caption-less byte invariance)

Discharges ROADMAP SC#4: the caption-less table path is proven byte-for-byte unchanged by the
TBL-03 fix, using the two-build diff method (D-04), the same method Phase 36's SC#2 used
(`36-GATE-EVIDENCE.md` § "Post-decoupling diff"). Every command below was executed in THIS plan's
own worktree session, against two real throwaway git worktrees built with their own per-worktree
venv. No figure was transcribed or recalled from planning documents.

---

## 1. The two named commits

**PRE-FIX** — plan 42-01's RED-recording commit, the natural pre-fix side: it is the last commit
on this phase's history that is an ancestor of the fix and contains no production change
(`42-GATE-EVIDENCE-01.md` § 1 confirms `git status --porcelain typsphinx/` was empty at this
commit).

**Command:** `git log -1 --oneline d28f2c8bcdf8aee49ab82b1d883145a4036acefc`

```
d28f2c8 test(42-01): record classic RED for captioned-table propagated-target drop
```

**POST-FIX** — plan 42-04's fix commit, the only commit in this phase that touches `typsphinx/`
(confirmed below, § 5).

**Command:** `git log -1 --oneline e5575f3ab51144405c44764a5b192b9d5f7526b2`

```
e5575f3 fix(42-04): move captioned-table propagated-anchor call past in-table reset
```

Both are real 40-hex SHAs:

```
d28f2c8bcdf8aee49ab82b1d883145a4036acefc
e5575f3ab51144405c44764a5b192b9d5f7526b2
```

---

## 2. Worktree isolation proof

**Why this section exists (T-42-11):** an unprovisioned worktree resolves `import typsphinx` to
the MAIN checkout via the PEP-660 editable finder baked into the main `.venv`, so both sides would
be built by the SAME (post-fix) code and the pairwise `.typ` diff would be empty for the wrong
reason — proving nothing. This section records, per worktree, that each side really ran its own
copy of `typsphinx`.

### PRE-FIX worktree

**Command:**
```
git worktree add --detach <scratch>/t4205/pre-fix-wt d28f2c8bcdf8aee49ab82b1d883145a4036acefc
```
Output: `Preparing worktree (detached HEAD d28f2c8)` / `HEAD is now at d28f2c8 test(42-01): record
classic RED for captioned-table propagated-target drop`.

**Provisioning:**
```
(cd <scratch>/t4205/pre-fix-wt && unset VIRTUAL_ENV UV_PROJECT_ENVIRONMENT && uv sync --extra dev)
```
Exited `0`; installed `typsphinx==0.7.0 (from file:///<scratch>/t4205/pre-fix-wt)` among the
resolved packages — `uv` itself resolved the editable install to THIS worktree's own path, not
the main checkout's.

**Shim:**
```
ln -sf "/nix/store/cgvijxnmydknslkl368k4j4j43akvl8b-uv-0.11.25/bin/uv" ".venv/bin/uv"
readlink -f .venv/bin/uv
```
```
/nix/store/cgvijxnmydknslkl368k4j4j43akvl8b-uv-0.11.25/bin/uv
```

**Isolation proof:**
```
uv run python -c "import typsphinx, pathlib; print(pathlib.Path(typsphinx.__file__).resolve())"
```
```
/tmp/claude-1000/-home-yuta-Documents-typsphinx/fb0b7b35-ebe9-4a09-9424-6e6eaaf12d12/scratchpad/t4205/pre-fix-wt/typsphinx/__init__.py
```
This path lies INSIDE the pre-fix throwaway worktree, not inside the main checkout
(`/home/yuta/Documents/typsphinx` or this plan's own worktree
`/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a30a8c677768ee97f`).

### POST-FIX worktree

**Command:**
```
git worktree add --detach <scratch>/t4205/post-fix-wt e5575f3ab51144405c44764a5b192b9d5f7526b2
```
Output: `Preparing worktree (detached HEAD e5575f3)` / `HEAD is now at e5575f3 fix(42-04): move
captioned-table propagated-anchor call past in-table reset`.

**Provisioning:**
```
(cd <scratch>/t4205/post-fix-wt && unset VIRTUAL_ENV UV_PROJECT_ENVIRONMENT && uv sync --extra dev)
```
Exited `0`; installed `typsphinx==0.7.0 (from file:///<scratch>/t4205/post-fix-wt)`.

**Shim:**
```
ln -sf "/nix/store/cgvijxnmydknslkl368k4j4j43akvl8b-uv-0.11.25/bin/uv" ".venv/bin/uv"
readlink -f .venv/bin/uv
```
```
/nix/store/cgvijxnmydknslkl368k4j4j43akvl8b-uv-0.11.25/bin/uv
```

**Isolation proof:**
```
uv run python -c "import typsphinx, pathlib; print(pathlib.Path(typsphinx.__file__).resolve())"
```
```
/tmp/claude-1000/-home-yuta-Documents-typsphinx/fb0b7b35-ebe9-4a09-9424-6e6eaaf12d12/scratchpad/t4205/post-fix-wt/typsphinx/__init__.py
```
This path lies INSIDE the post-fix throwaway worktree.

**The two recorded `typsphinx.__file__` paths differ** (`.../pre-fix-wt/typsphinx/__init__.py` vs
`.../post-fix-wt/typsphinx/__init__.py`) — direct, positive evidence the two builds below ran
against genuinely different copies of the translator, not the same code twice.

### `ruff` shim — measured limitation, recorded transparently

`command -v ruff` (with the NixOS store paths on `PATH`) returned nothing in this sandbox, and an
explicit search (`ls /nix/store | grep -i '^[a-z0-9]*-ruff'`) found no `ruff` package present in
the Nix store at all — unlike `uv`, which resolved directly. This matches
`42-GATE-EVIDENCE-04.md` § 5's own note that "this NixOS worktree's Nix-store `ruff` was
unavailable to shim directly." **This plan's task does not invoke `ruff` in either throwaway
worktree** — only `uv run python -m sphinx -b typst` builds are run — so the missing shim does not
weaken the isolation proof above, which rests entirely on the `typsphinx.__file__` paths and the
`uv` shim (both present and recorded). Recorded here rather than silently omitted, per this plan's
own prohibition against silent omission.

---

## 3. Build commands

Both fixtures were built from both worktrees with `uv run python -m sphinx -b typst -q -E`.

### Fixture A — `tests/fixtures/table_in_list_item_render_gate` (pre-existing at both SHAs)

**Command (pre-fix worktree):**
```
uv run python -m sphinx -b typst -q -E tests/fixtures/table_in_list_item_render_gate <scratch>/t4205/pre-fix-build-a
```
**Exit status:** `0`

**Command (post-fix worktree):**
```
uv run python -m sphinx -b typst -q -E tests/fixtures/table_in_list_item_render_gate <scratch>/t4205/post-fix-build-a
```
**Exit status:** `0`

This fixture's entire content (a list-item-nested `list-table` plus a top-level control
`list-table`, both caption-less) exists identically at both named SHAs, confirmed by
`git ls-tree -r --name-only <SHA> | grep table_in_list_item_render_gate` returning the same three
paths (`conf.py`, `index.rst`) at both commits.

### Fixture B — `tests/fixtures/captioned_table_propagated_target_render_gate` (created by plan
42-01; availability confirmed below)

**Availability check** — this fixture must exist at BOTH chosen SHAs, not just the post-fix side,
because it was created by plan 42-01 in the same wave as the RED-recording commit:

**Command:** `git ls-tree -r --name-only d28f2c8bcdf8aee49ab82b1d883145a4036acefc | grep captioned_table_propagated_target_render_gate`
```
tests/fixtures/captioned_table_propagated_target_render_gate/conf.py
tests/fixtures/captioned_table_propagated_target_render_gate/index.rst
tests/test_captioned_table_propagated_target_render_gate.py
```

**Command:** `git ls-tree -r --name-only e5575f3ab51144405c44764a5b192b9d5f7526b2 | grep captioned_table_propagated_target_render_gate`
```
tests/fixtures/captioned_table_propagated_target_render_gate/conf.py
tests/fixtures/captioned_table_propagated_target_render_gate/index.rst
tests/test_captioned_table_propagated_target_render_gate.py
```

Present, identically, at both SHAs — the chosen PRE-FIX SHA (`d28f2c8`, plan 42-01's own
RED-recording commit) is at 42-01, so the fixture is at or after it. No fallback substitution is
needed; both shapes are covered.

**Command (pre-fix worktree):**
```
uv run python -m sphinx -b typst -q -E tests/fixtures/captioned_table_propagated_target_render_gate <scratch>/t4205/pre-fix-build-b
```
**Exit status:** `0`

**Command (post-fix worktree):**
```
uv run python -m sphinx -b typst -q -E tests/fixtures/captioned_table_propagated_target_render_gate <scratch>/t4205/post-fix-build-b
```
**Exit status:** `0`

Fixture B contains BOTH captioned shapes (which the fix changes — that is SC#3's job, discharged
by `42-GATE-EVIDENCE-04.md`, not this file) AND a caption-less control table (which must stay
byte-unchanged — SC#4, this file). Only the caption-less control section's emitted bytes are the
subject of this file's proof; § 4 below isolates that section explicitly rather than diffing the
whole file, because the whole file is EXPECTED to differ (the captioned shapes' propagated anchors
only appear post-fix — that expected difference is verified first, immediately below, as positive
proof the two sides ran different code).

---

## 4. THE PROOF

### 4a. Fixture A — full-file diff (the entire fixture is caption-less)

**Command:**
```
diff <scratch>/t4205/pre-fix-build-a/index.typ <scratch>/t4205/post-fix-build-a/index.typ
```

**Output:** **(empty)**. **Exit status:** `0`.

The list-item-nested table and the top-level control table are both caption-less; the whole
emitted `index.typ` for this fixture is byte-identical across the fix.

### 4b. Fixture B — whole-file diff FIRST (expected to be non-empty — positive proof of
genuine code difference)

**Command:**
```
diff <scratch>/t4205/pre-fix-build-b/index.typ <scratch>/t4205/post-fix-build-b/index.typ
```

**Verbatim output:**
```
42a43,44
> [#metadata(none) <index:tbl-target>]
>
59a62,63
> [#metadata(none) <index:tbl-target-noname>]
>
89a94,96
>
> [#metadata(none) <index:tbl-target-li>]
>
108a116,119
>
> [#metadata(none) <index:tbl-target-b>]
>
> [#metadata(none) <index:tbl-target-a>]
```

**Exit status:** `1` (real, expected difference). Every added line is a propagated-target anchor
that is present only in the post-fix build — exactly the SC#3 fix this phase's plan 42-04 made
(`42-GATE-EVIDENCE-04.md`). **This non-empty diff is deliberately recorded here as the positive
half of the isolation proof**: it demonstrates the two throwaway worktrees really executed
different `depart_table` code, which is the precondition that makes the EMPTY diff below
meaningful rather than vacuous.

### 4c. Fixture B — caption-less control section only (the SC#4 assertion)

The control section's boundaries were located by the surrounding heading anchors, identical in
both builds by name (`<index:caption-less-control-table>` opening,
`<index:references-back-to-the-propagated-targets>` closing), at shifted line numbers (pre-fix
lines 110-124; post-fix lines 121-135 — the 11-line shift is exactly the four propagated-anchor
insertions recorded in § 4b above, confirming no other content moved).

**Commands:**
```
sed -n '110,124p' <scratch>/t4205/pre-fix-build-b/index.typ  > <scratch>/t4205/pre-fix-caption-less-section.typ
sed -n '121,135p' <scratch>/t4205/post-fix-build-b/index.typ > <scratch>/t4205/post-fix-caption-less-section.typ
diff <scratch>/t4205/pre-fix-caption-less-section.typ <scratch>/t4205/post-fix-caption-less-section.typ
```

**Output:** **(empty)**. **Exit status:** `0`.

**Extracted section, verbatim (identical on both sides):**
```typst
[#heading(level: 2, {text("Caption-less control table")}) <index:caption-less-control-table>]

par({text("A table with no caption, no name, and no preceding target must stay byte-unchanged by this fix – it is not figure-wrapped at all.")})

table(
  columns: (8fr, 8fr),
  table.header(
    {par({text("Column A")})},
    {par({text("Column B")})},
  ),
  {par({text("Cell")})},
  {par({text("Cell")})},
)
```

**This is SC#4's discharge.** Both caption-less shapes — the pre-existing top-level control table
in `table_in_list_item_render_gate` (§ 4a, whole-file empty diff) and this phase's own new
caption-less control table in `captioned_table_propagated_target_render_gate` (§ 4c, isolated
section empty diff) — are byte-for-byte unchanged by the TBL-03 fix. Per D-04, the proof is these
two recorded `diff` outputs, not a golden `.typ` file committed to the repository; no golden `.typ`
was added anywhere under `tests/` or the repository tree (confirmed, § 6).

---

## 5. Production-diff isolation

**Pathspec-scoped diff — the fix commit's true production surface:**

**Command:**
```
git diff --stat d28f2c8bcdf8aee49ab82b1d883145a4036acefc..e5575f3ab51144405c44764a5b192b9d5f7526b2 -- typsphinx/
```

```
 typsphinx/translator.py | 34 +++++++++++++++++++++++++++-------
 1 file changed, 27 insertions(+), 7 deletions(-)
```

Only `typsphinx/translator.py` — nothing else under `typsphinx/` changed between the two named
commits.

**Unscoped diff — the full tree difference, deliberately larger:**

**Command:**
```
git diff --stat d28f2c8bcdf8aee49ab82b1d883145a4036acefc..e5575f3ab51144405c44764a5b192b9d5f7526b2
```

```
 .planning/ROADMAP.md                               |  13 +-
 .planning/STATE.md                                 |  16 +-
 .../42-01-SUMMARY.md                               | 138 ++++++
 .../42-02-SUMMARY.md                               | 133 ++++++
 .../42-03-SUMMARY.md                               | 138 ++++++
 .../42-GATE-EVIDENCE-01.md                         | 353 ++++++++++++++++
 .../42-GATE-EVIDENCE-02.md                         | 258 ++++++++++++
 .../42-GATE-EVIDENCE-03.md                         | 463 +++++++++++++++++++++
 ...able-whitespace-only-title-anchor-divergence.md |  98 +++++
 .../figure_propagated_target_render_gate/conf.py   |  40 ++
 .../figure_propagated_target_render_gate/image.png | Bin 0 -> 68 bytes
 .../figure_propagated_target_render_gate/index.rst |  55 +++
 tests/test_figure_propagated_target_render_gate.py | 283 +++++++++++++
 typsphinx/translator.py                            |  34 +-
 14 files changed, 2002 insertions(+), 20 deletions(-)
```

**Why the unscoped diff is larger (one sentence):** unrelated commits from plans 42-02 and 42-03
(the figure-side permanent gate fixture, the misrouting-sweep evidence file, and both plans'
SUMMARY.md/todo artifacts) landed on this phase's branch between the two named commits, exactly
the measurement trap `36-GATE-EVIDENCE.md`'s own "Post-decoupling diff" section named and
explained for Phase 36.

---

## 6. No golden file, no code/fixture change

**Command:** `git status --porcelain typsphinx/ tests/`

```
(no output)
```

Empty — this plan changes no production code and no fixture. No `.typ` golden file was added
anywhere under `tests/` or the repository tree; per D-04, the owner chose the two-build diff
method over a committed golden, and over doing both.

**Command:** `git worktree list` (after cleanup)

```
/home/yuta/Documents/typsphinx                                           a0616f2 [gsd/v0.7.0-api-rendering-design-overhaul]
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a30a8c677768ee97f a0616f2 [worktree-agent-a30a8c677768ee97f] locked
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a487e99b3ae6ae3cd d57f6d1 [worktree-agent-a487e99b3ae6ae3cd] locked
```

No `pre-fix-wt`/`post-fix-wt` scratch worktree remains — both were removed with
`git worktree remove --force <path>` after the builds and diffs above were recorded.

---

## 7. Verdict

| Success criterion | Discharged by | Status |
|--------------------|----------------|--------|
| SC#4 — the caption-less table path is byte-for-byte unchanged by the TBL-03 fix, proven by an empty `diff` between two real `sphinx-build -b typst` runs at named pre-fix and post-fix commits, each built from its own throwaway git worktree with its own venv (D-04) | § 2 (worktree isolation proof, two distinct `typsphinx.__file__` paths), § 3 (both builds exit 0), § 4 (empty diffs: § 4a whole-file for `table_in_list_item_render_gate`, § 4c isolated caption-less section for `captioned_table_propagated_target_render_gate`, with § 4b's non-empty whole-file diff as positive proof the two sides ran genuinely different code), § 5 (production diff isolated to `typsphinx/translator.py` alone) | **MET** |

Not owned by this evidence file:

- SC#3 (a captioned table preceded by a standalone target compiles, both labels resolve) and
  SC#5's GREEN half — owned by plan 42-04, recorded in `42-GATE-EVIDENCE-04.md`.
- The repo-wide misrouting sweep (D-06/D-07) — owned by plan 42-03, recorded in
  `42-GATE-EVIDENCE-03.md`.
- The Phase 41 release-prep reconciliation (SC#6) — owned by plan 42-06.
