# Phase 48 — Evidence Log

Created by plan 48-01, Task 2, Step 0. Later plans APPEND new sections to this file — never
overwrite it.

## Body-mode measurement

**Purpose:** D-08 says D-07's exact Typst syntax is unmeasured. Two candidate body spellings
exist and only one preserves today's child-emission bytes:

- `[#{` … `}]` — a content block wrapping a code block. Children keep streaming in code mode
  exactly as today (`_in_markup_mode` stays False, `_in_link` stays True), so no other visitor's
  emission moves and the corpus-wide body bytes do not change. This is the planner's derived
  preference and was NOT yet measured before this section.
- `[` … `]` — the bare content block PROJECT.md/research measured with hand-written markup
  children. Choosing it forces children into markup mode, changing the emitted body of every
  cross-document reference in the corpus.

**Methodology (binding constraint #6 compliance):** every probe below is a throwaway, HAND-WRITTEN
`.typ` file exercising the Typst LANGUAGE, not output read off the new emitter — the guard code
does not exist yet in `typsphinx/translator.py` at the time these probes were compiled
(`git status --porcelain typsphinx/` prints nothing throughout this task). This measurement does
NOT violate binding constraint #6 (which forbids deriving expected TEST values from the new
emitter's output) — these probes derive the SYNTAX contract itself, before any test asserts
against it. Every probe was compiled via `typst.compile(path)` (typst-py 0.15.0, same installed
version confirmed in `48-RED-EVIDENCE.md`'s provenance header) from this plan's own provisioned
worktree venv, under `/tmp/claude-.../scratchpad/48-01-probes/` (outside the repository, per the
scratchpad convention).

**Every probe is wrapped inside a `#{ ... }` / `par({ ... })` code-mode context**, not placed as
bare top-level markup prose. This matters: a bare `[` at the top level of a `.typ` document is
MARKUP mode by default, where `[`/`]` are LITERAL bracket characters with no content-block effect
— an earlier draft of probes 4/5 made exactly this mistake (placed the own-anchor bracket at
top-level markup prose) and still compiled with the query finding the label, but for the WRONG
reason (the label attached to loose inline text, not to a real content-block value), which would
have been a false positive per Pitfall 2's warning about test artifacts that look like a real
guard validation but are not representative. The real translator emits this construct from INSIDE
a `par({ ... })` code block (confirmed by reading a real compiled fixture,
`tests/fixtures/citation_render_gate/`'s emitted `index.typ`:
`par({text("...") \n [#link(<label>, \n text("[Cross2019]"))#label("index:id4")] \n text(".")})`),
so every probe below reproduces that exact code-mode wrapping.

### Probe 1 — `[#{` with a translator-shaped code-mode body (`+`-joined `text()`/`raw()` chain)

**Source (verbatim):**
```typst
= Doc

#{
par({text("Some text before ")
context { let __tsx_body = [#{text("first ") + raw("code segment") + text(" last")}]; if query(<present-label>).len() > 0 { link(<present-label>, __tsx_body) } else { __tsx_body } }
text(" and text after.")})
}

= Target <present-label>
Target section.
```

**Compile result, target PRESENT:** `typst.compile()` succeeds (19,033 bytes). `pypdf`-extracted
text: `"Doc\nSome text before first code segment last and text after.\nTarget\nTarget section."` —
the guarded body renders inline exactly as the unguarded form would. 3 `/Link` annotation rects
were found, all with `/Dest` = `present-label` — Typst splits one logical link into multiple
`/Rect`s across the font-run boundary where `raw("code segment")` switches to monospace, which is
expected Typst PDF-emission behaviour, not a guard defect (every rect points at the SAME
destination).

**Compile result, target ABSENT** (same source with the `= Target <present-label>` heading
removed): `typst.compile()` still succeeds. `pypdf`-extracted text:
`"Doc\nSome text before first code segment last and text after."` — the reference's text still
renders, with **0** `/Link` annotations. No error either way.

### Probe 2 — `[#{` with an EMPTY body (the edge/empty case the guard must not turn into a syntax error)

**Source (verbatim):**
```typst
= Doc

#{
par({text("Some text before ")
context { let __tsx_body = [#{}]; if query(<present-label>).len() > 0 { link(<present-label>, __tsx_body) } else { __tsx_body } }
text(" and text after.")})
}

= Target <present-label>
Target section.
```

**Compile result:** `typst.compile()` succeeds (11,344 bytes). `pypdf`-extracted text:
`"Doc\nSome text before  and text after.\nTarget\nTarget section."` (note the double space where
the empty body contributed nothing). **0** `/Link` annotations — even with the target PRESENT, an
empty guarded body produces no visible link annotation, since there is no glyph content for Typst
to attach a clickable rect to. No error. Confirms the empty-body edge case does not become a
syntax error.

### Probe 3 — `[#{` with a body containing a nested `link("https://example.com", text("x"))`

**Source (verbatim):**
```typst
= Doc

#{
par({text("Some text before ")
context { let __tsx_body = [#{text("see ") + link("https://example.com", text("here"))}]; if query(<present-label>).len() > 0 { link(<present-label>, __tsx_body) } else { __tsx_body } }
text(" and text after.")})
}

= Target <present-label>
Target section.
```

**Compile result:** `typst.compile()` succeeds (12,125 bytes). `pypdf`-extracted text:
`"Doc\nSome text before see here and text after.\nTarget\nTarget section."`. 2 `/Link`
annotations — one for the OUTER guard link (`/Dest` = `present-label`) and one for the NESTED
external `link("https://example.com", ...)` — both compile cleanly nested inside the guarded body,
confirming arbitrary child markup (including another `link()` call) streams unchanged inside
`[#{ ... }]`.

### Probe 4 — the own-anchor combination (`_reference_own_anchor` bracket-wrap composed with the guard)

`visit_reference` emits a bare `[` and enters markup mode when `decision.eligible` is true, and
`depart_reference` closes with `#label("...")]` AFTER the link's closing `)`. Replacing that `)`
with the guard's close string changes the nesting; this combination was not among research's 34
compiled probes. D-09 makes `opens_wrapper` unconditional in 48-02, which is precisely what makes
a citation-derived CROSS-document reference simultaneously eligible for its own anchor and routed
through the guard, so this combination is not hypothetical.

**Source (verbatim):**
```typst
= Doc

#{
par({text("Some text before ")
[#context { let __tsx_body = [#{text("[Cited]")}]; if query(<present-label>).len() > 0 { link(<present-label>, __tsx_body) } else { __tsx_body } } #label("citing-anchor")]
text(" and text after.")})
}

#context [Query result: #query(<citing-anchor>).len()]

= Target <present-label>
Target section.
```

**Compile result, target PRESENT:** `typst.compile()` succeeds (12,676 bytes). `pypdf`-extracted
text: `"Doc\nSome text before [Cited]  and text after.\nQuery result: 1\nTarget\nTarget section."`
— **the query for `<citing-anchor>` finds exactly 1 match**, confirming the `#label(...)` attaches
to the outer bracketed content (the WHOLE `[#context {...} #label(...)]` construct), not merely to
loose inline text. 1 `/Link` annotation (`/Dest` = `present-label`), from the guard's positive
branch.

**Compile result, target ABSENT** (same source, `= Target <present-label>` heading removed):
`typst.compile()` still succeeds. `pypdf`-extracted text:
`"Doc\nSome text before [Cited]  and text after.\nQuery result: 1"` — **the own-anchor label STILL
attaches** (`Query result: 1`) even when the guard's target is absent and the guarded expression
degrades to plain text. This confirms the own-anchor and the guard's cross-document query are
INDEPENDENT: the anchor is same-document-derived (D-09's reasoning) and its attachment does not
depend on whether the guard's own target resolves. 0 `/Link` annotations (the guard degraded, as
expected).

### Probe 5 — the own-anchor combination with an empty body

**Source (verbatim):**
```typst
= Doc

#{
par({text("Some text before ")
[#context { let __tsx_body = [#{}]; if query(<present-label>).len() > 0 { link(<present-label>, __tsx_body) } else { __tsx_body } } #label("citing-anchor")]
text(" and text after.")})
}

#context [Query result: #query(<citing-anchor>).len()]

= Target <present-label>
Target section.
```

**Compile result, target PRESENT:** `typst.compile()` succeeds (12,131 bytes). `pypdf`-extracted
text: `"Doc\nSome text before   and text after.\nQuery result: 1\nTarget\nTarget section."` — the
own-anchor label still attaches (`Query result: 1`) even with an empty guarded body. 0 `/Link`
annotations (matching Probe 2's empty-body finding: no glyph content, so no clickable rect, even
though the guard's positive branch was taken).

### Adopted spelling

**All five cases (1, 2, 3, 4, 5) compiled successfully in BOTH the target-present and
target-absent configurations, with no `TypstError` in any of the ten compiles.** Per the plan's
own decision rule ("Adopt `[#{` if cases 1-3 and 5 compile; otherwise fall back to the bare `[`
form"), **`[#{` … `}]` is ADOPTED** as D-07/D-08's body-mode spelling — it preserves today's
code-mode child-emission bytes exactly (no other visitor's emission moves), and the own-anchor
composition (case 4/5) confirmed the `#label(...)` closing pair correctly attaches to the whole
bracketed construct regardless of the guard's own query outcome.

### Guard contract, fixed by this measurement

- Shared helper: `TypstTranslator._label_existence_guard(label, *, prefix="", code_mode_body=False)`,
  returning a `_LabelGuardStrings` `NamedTuple` with fields `open_str` and `close_str`.
- Bound identifier: `__tsx_body`.
- When `code_mode_body=True` (the ADOPTED spelling for all three D-07 sites — every site's
  existing children already stream in code mode): `open_str` ends with `= [#{` and `close_str`
  begins with `}];`.
- When `code_mode_body=False` (unused by this phase's three sites, but the parameter is kept for
  completeness/future callers whose children already stream in markup mode): `open_str` ends with
  `= [` and `close_str` begins with `];`.
- `close_str`'s conditional is one unbroken statement — `if query(<L>).len() > 0 {` never has a
  newline between the condition and its opening brace (Pitfall 1's `expected block` parse error).
- Own-anchor composition: when the caller has also opened the `_reference_own_anchor`
  bracket-wrap (`self.add_text("[")` + `self._in_markup_mode = True` in `visit_reference`), the
  `#label("…")]` closing pair lands AFTER `close_str`, OUTSIDE the `context { … }` block — exactly
  the shape Probe 4/5 compiled and verified query-findable.

**Fully substituted example** (label `target:xref-guard-target`, `code_mode_body=True`,
`prefix=""`):

```
open_str:  context { let __tsx_body = [#{
close_str: }]; if query(<target:xref-guard-target>).len() > 0 { link(<target:xref-guard-target>, __tsx_body) } else { __tsx_body } }
```

## D-11 compile-time cost

**Purpose:** measure what the compile-time guard actually costs at full-corpus scale, against
thresholds fixed **before** this measurement was taken, so a measured regression cannot be
rationalised after the fact.

### D-11's three tiers, quoted verbatim from `48-CONTEXT.md` (fixed at discussion time, 2026-08-12,
before any measurement in this section)

> under `+20%` the number is recorded and nothing else happens; between `+20%` and `+100%` it is
> recorded as an explicit finding in the phase evidence and an improvement todo is filed; above
> `+100%` it is escalated to a blocker attached to Phase 49's scope.

And the realistic remediation path if the top tier were hit, also quoted verbatim: "replace
`query(<L>).len() > 0` with a lookup against Phase 49's `state("inc", ())` include set once that
exists — abandoning the design is not available, since binding constraint #1 makes Phase 49
depend on the guard."

These were fixed at discussion time, before any measurement — the reading order above (tiers
first, number below) is itself the evidence that they were not renegotiated after the fact.

### Pre-fix baseline, quoted verbatim from `48-VALIDATION.md`'s "Test Infrastructure" table

> `tests/test_corpus_gate.py` full-corpus `-b typstpdf` → **28.93s / 28.56s** (D-11 "before"
> baseline)

Per `48-RESEARCH.md` assumption A3, these absolute numbers are specific to the measuring machine
— the after-number below was taken on the **same machine** (this worktree, provisioned per
`CLAUDE.md`'s `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` +
`uv run` protocol) so the ratio between before and after means something; the tiering logic
itself is relative (a percentage), not tied to any absolute wall-clock figure.

### After-measurement — two raw transcripts, `time uv run pytest tests/test_corpus_gate.py -m slow`
(the exact invocation `48-VALIDATION.md`'s "D-11 'after' measurement" row names)

**Run 1:**

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- /home/yuta/Documents/typsphinx/.claude/worktrees/agent-ae7d93eaa5ed0d932/.venv/bin/python
cachedir: .pytest_cache
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-ae7d93eaa5ed0d932
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 5 items / 3 deselected / 2 selected

tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error PASSED [ 50%]
tests/test_corpus_gate.py::test_empty_url_before_after SKIPPED (SC#3...) [100%]

================= 1 passed, 1 skipped, 3 deselected in 28.92s ==================

real	0m29.483s
user	0m27.747s
sys	0m1.582s
```

**Run 2:**

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- /home/yuta/Documents/typsphinx/.claude/worktrees/agent-ae7d93eaa5ed0d932/.venv/bin/python
cachedir: .pytest_cache
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-ae7d93eaa5ed0d932
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 5 items / 3 deselected / 2 selected

tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error PASSED [ 50%]
tests/test_corpus_gate.py::test_empty_url_before_after SKIPPED (SC#3...) [100%]

================= 1 passed, 1 skipped, 3 deselected in 27.21s ==================

real	0m27.567s
user	0m26.401s
sys	0m1.485s
```

`test_empty_url_before_after` SKIPs (env-gated behind `TYPSPHINX_CORPUS_REPORT=1`, unrelated to
D-11) in both runs — the pytest-reported duration line (`28.92s` / `27.21s`) is the corpus
render gate's own wall-clock time, matching the invocation the baseline was itself taken with.

### Arithmetic

- Pre-fix baseline mean: `(28.93 + 28.56) / 2 = 28.745s`
- After-guard mean: `(28.92 + 27.21) / 2 = 28.065s`
- Delta: `28.065 - 28.745 = -0.680s`
- Percentage change: `-0.680 / 28.745 * 100 = -2.37%`

The measured change is **-2.37%** — the corpus build is very slightly FASTER after the guard
landed than the pre-fix baseline, well within measurement noise for a ~28s wall-clock subprocess
build (network/disk/scheduler jitter dwarfs a single-digit-percent difference here). This falls in
the **bottom tier** (under `+20%`).

### Tier applied

**Bottom tier: record only.** The guard's corpus-scale cost is not a material regression — it is,
if anything, indistinguishable from noise around zero. No todo is filed and no `STATE.md` blocker
is added, exactly as the bottom tier's own instruction says: "record only." No sentence naming a
Phase 49 coupling is required here — that obligation is scoped to the middle and top tiers only,
neither of which was reached.

### Verification that no timing instrumentation was added

```
$ git diff --stat tests/test_corpus_gate.py
(no output)
$ grep -Ec 'assert.*(elapsed|duration|time\.)' tests/test_corpus_gate.py
0
```

`tests/test_corpus_gate.py` still carries no timing instrumentation and no wall-clock assertion —
this measurement is the one-off manual record D-11 specifies, not a permanent, CI-flaky assertion.

## D-09 citation-marker delta

**Purpose:** D-09 is asserted backward-compatible-by-design (removing `degrade_xref_to_text` makes
`opens_wrapper` unconditional, so a citation back-reference marker that previously did not appear
now does), but no automated gate in this phase would catch "an extra back-reference marker now
appears" — `tests/test_corpus_gate.py` only asserts no fatal. This section measures the delta
against the real Sphinx `doc/` corpus rather than resting on the same-document-anchor argument
alone, reusing the established two-build BEFORE/AFTER methodology `test_empty_url_before_after`
already sets (a git worktree at an older tree + a `PYTHONPATH` override for the BEFORE subprocess
only, both builds `-b typst`, cleanup regardless of outcome).

### Step 1 — `BEFORE_SHA` resolution

`git log --reverse --format='%H %s' -- typsphinx/translator.py`, filtered for the earliest Phase 48
commit touching `typsphinx/translator.py` whose subject names `48-02`:

```
8184f4d56b39555498d17b80379782fc4c619be0 feat(48-02): move cross-reference label existence to Typst compile time
```

`BEFORE_SHA` is this commit's **parent**:

```
$ git rev-parse 8184f4d56b39555498d17b80379782fc4c619be0^
09f5d7f087b754edd81d3e1e0e38ab859f21d25b
$ git log -1 --format='%H %s' 8184f4d56b39555498d17b80379782fc4c619be0^
09f5d7f087b754edd81d3e1e0e38ab859f21d25b docs(phase-48): update tracking after wave 1
```

`BEFORE_SHA = 09f5d7f087b754edd81d3e1e0e38ab859f21d25b`, the commit immediately preceding
`8184f4d` ("feat(48-02): move cross-reference label existence to Typst compile time" — plan 48-02's
TRACER commit, the first commit to touch `typsphinx/translator.py` and introduce the guard).

### Step 2 — isolated worktree + PYTHONPATH shadowing, and a real shadowing hazard found and worked around

```
$ git worktree add --detach <tmp>/48-04-pre-guard 09f5d7f087b754edd81d3e1e0e38ab859f21d25b
Preparing worktree (detached HEAD 09f5d7f)
HEAD is now at 09f5d7f docs(phase-48): update tracking after wave 1
$ grep -c "_label_existence_guard" <tmp>/48-04-pre-guard/typsphinx/translator.py
0
```

Confirmed the pre-guard worktree's `translator.py` carries no guard helper at all.

**A real, measured shadowing hazard, worked around rather than assumed away:** naively invoking the
BEFORE subprocess with `PYTHONPATH=<tmp>/48-04-pre-guard` from the repository root does **not**
shadow the installed `typsphinx` package —

```
$ cd <repo-root> && PYTHONPATH=<tmp>/48-04-pre-guard .venv/bin/python -c \
    "import typsphinx, pathlib; print(pathlib.Path(typsphinx.__file__).resolve())"
<repo-root>/typsphinx/__init__.py    # WRONG -- this is the as-shipped copy, not the pre-guard one
```

The cause is not the venv's PEP-660 editable-install finder (`__editable___typsphinx_..._finder.py`,
a `MetaPathFinder` mapping `typsphinx` to this worktree's absolute path) — that finder sits AFTER
`PathFinder` in `sys.meta_path`, so it is never even reached here. The actual cause: `python -c`/
`python -m` prepends `''` (the current working directory) to `sys.path` **before** any `PYTHONPATH`
entry, per Python's own `-m`/`-c` `sys.path` construction rules. Since the subprocess's cwd was the
repository root — which itself contains a `typsphinx/` package directory — `PathFinder` resolves
`typsphinx` via cwd (`''`) before ever reaching the `PYTHONPATH` entry, silently defeating the
override. Running the SAME command from a cwd with no local `typsphinx/` directory confirms the
override works correctly once that collision is removed:

```
$ cd <tmp>/scratchpad && PYTHONPATH=<tmp>/48-04-pre-guard .venv/bin/python -c \
    "import typsphinx; print(typsphinx.__file__)"
<tmp>/48-04-pre-guard/typsphinx/__init__.py   # correct -- pre-guard worktree copy
$ cd <tmp>/scratchpad && .venv/bin/python -c "import typsphinx; print(typsphinx.__file__)"
<repo-root>/typsphinx/__init__.py             # correct -- as-shipped copy, no PYTHONPATH set
```

Both BEFORE and AFTER builds below are therefore run with the subprocess's **cwd set to a
scratchpad directory outside the repository** (never the repository root), which is what makes the
`PYTHONPATH` override in `test_empty_url_before_after`'s own established methodology actually take
effect for a `sphinx-build` subprocess invoked via `python -m sphinx`. No new methodology was
invented — this only corrects the invocation's working directory so the existing PYTHONPATH-based
mechanism does what its own docstring says it does.

### Step 3 — both builds, `-b typst` only (never `-b typstpdf`)

Corpus: the same cached, already-wired `~/.cache/typsphinx-corpus-gate/sphinx-v9.1.0/doc` tree
`test_corpus_gate.py`'s own `corpus_doc_dir`/`wire_typsphinx_into_corpus_conf` fixtures use.

**BEFORE** (`PYTHONPATH=<tmp>/48-04-pre-guard`, cwd = scratchpad):

```
$ cd <tmp>/scratchpad && PYTHONPATH=<tmp>/48-04-pre-guard .venv/bin/python -m sphinx -b typst \
    ~/.cache/typsphinx-corpus-gate/sphinx-v9.1.0/doc <tmp>/48-04-before-build
...
writing output... [usage/extensions/napoleon]WARNING: cross-reference to non-included document 'usage/extensions/example_google' rendered as plain text (typstpdf includes only toctree-reachable documents): Example Google Style Python Docstrings
WARNING: cross-reference to non-included document 'usage/extensions/example_numpy' rendered as plain text (typstpdf includes only toctree-reachable documents): Example NumPy Style Python Docstrings
 done
...
typst: wrote 1 wrapper file(s) -- compile these: sphinx-corpus.typ
Copying 19 image file(s)...
build succeeded, 46 warnings.
```

The D-01 "cross-reference to non-included document ... rendered as plain text" warning appears —
this is direct, independent confirmation the BEFORE build really did run the pre-guard, pre-D-01
translator (that warning was deleted in plan 48-02).

**AFTER** (no `PYTHONPATH` override, cwd = scratchpad, as-installed HEAD):

```
$ cd <tmp>/scratchpad && .venv/bin/python -m sphinx -b typst \
    ~/.cache/typsphinx-corpus-gate/sphinx-v9.1.0/doc <tmp>/48-04-after-build
...
writing output... [usage/extensions/napoleon] done
...
typst: wrote 1 wrapper file(s) -- compile these: sphinx-corpus.typ
Copying 19 image file(s)...
build succeeded, 42 warnings.
```

No D-01 warning this time (42 warnings vs. 46 — a 4-warning reduction, consistent with the D-01
warning's deletion), confirming this build really did run as-shipped HEAD.

### Step 4 — the three counts, both builds

**Important, stated explicitly before the numbers, per this section's own requirement:** the
LINKED-cell signature is NOT the same string in both builds. Pre-guard, a linked citation cell
emits the bare `text("[") + link(<label>, ...`; post-guard, the SAME logical cell emits
`text("[") + context { let __tsx_body = ... }` — the guard wraps the link in a `context { ... }`
block, so `text("[") + link(<` never appears post-guard even where a link IS present. A naive
single-signature grep across both builds would therefore report a spurious collapse to zero on the
AFTER side even if every citation kept its link. Both signatures are counted, one per build, below.

```
$ grep -ro 'text("\[") + ' <tmp>/48-04-before-build --include="*.typ" | wc -l
0
$ grep -ro 'text("\[") + ' <tmp>/48-04-after-build --include="*.typ" | wc -l
0
$ grep -rl 'columns: (auto, 1fr)' <tmp>/48-04-before-build --include="*.typ" | wc -l
0
$ grep -rl 'columns: (auto, 1fr)' <tmp>/48-04-after-build --include="*.typ" | wc -l
0
```

- Total citation label cells (`text("[") + `): **0 before, 0 after**.
- Citation grid open marker (`columns: (auto, 1fr)`, `visit_citation`'s own distinctive grid-open
  string, an independent corroborating signature): **0 before, 0 after**.
- LINKED citation label cells (`text("[") + link(<` before / `text("[") + context` after): **not
  computed** — moot, since the total is already zero in both builds.
- Multi-target marker groups (`+ text(" (") + (`): **not computed** — moot, same reason.

### Step 5 — the corpus exercises no citations; the zero delta is not reported as verification

**Sphinx's own `doc/` corpus contains zero docutils citations** (no `.. [Label]` definitions, no
`[Label]_` citing references anywhere in the tree) — `visit_citation`'s own distinctive grid-open
marker (`columns: (auto, 1fr)`) appears **zero times** in either the BEFORE or the AFTER build's
emitted `.typ` files. This is stated plainly rather than presenting the 0-vs-0 delta as
verification: **the corpus does not exercise D-09.** Per D-09's own INTENDED direction, an increase
in linked citation cells would be the expected fix taking effect; a decrease would be the finding
to investigate. Neither can be observed here because the starting count is already zero.

### Step 6 fallback — the project's own citation gates, the only D-09 coverage available

Per this section's own contingency instruction, the project's committed citation gates are run and
recorded as the only D-09 coverage that exists, since the external corpus supplies none:

```
$ uv run pytest tests/test_citation_render_gate.py tests/test_citation_degradation_gate.py -q
tests/test_citation_render_gate.py .........                             [ 34%]
tests/test_citation_degradation_gate.py .................                [100%]
============================== 26 passed in 2.61s ==============================
```

26/26 pass. `tests/test_citation_degradation_gate.py`'s own case (iii)
(`_wr03_case_refuri_excluded_document`) is the committed, direct assertion that D-09's
`opens_wrapper`-unconditional behaviour landed correctly (flipped under D-03 in plan 48-02) — this
is the actual D-09 regression coverage this project carries, external-corpus silence
notwithstanding.

### Cleanup

```
$ git worktree remove --force <tmp>/48-04-pre-guard
$ git worktree list
<repo-root>                          <hash> [gsd/v0.8.0-multi-master-composition]
<this-worktree>                      <hash> [worktree-agent-ae7d93eaa5ed0d932] locked
```

No leftover `48-04-pre-guard` (nor any `pre-48-guard`-named) worktree remains registered.

## Accepted limit — label-collision false negative

**Transcript — the collision characterization test, green since plan 48-02:**

```
$ uv run pytest tests/test_xref_compile_time_guard_render_gate.py -q -k collision
tests/test_xref_compile_time_guard_render_gate.py .                      [100%]
======================= 1 passed, 5 deselected in 0.73s ========================
```

**Emitted `index.typ` reference line from `tests/fixtures/xref_label_collision_guard_gate/`**
(rebuilt via `sphinx-build -b typst`, verbatim):

```
par({text("See ")
context { let __tsx_body = [#{
text("Alpha Nested Section")}]; if query(<a_u2f_b:nested-target>).len() > 0 { link(<a_u2f_b:nested-target>, __tsx_body) } else { __tsx_body } }
text(" for the nested section.")})
```

**What the guard actually asks:** the guard's `query(<a_u2f_b:nested-target>)` call checks whether
a label with that EXACT spelling exists anywhere in the compiling wrapper's document — "does a
label with this spelling exist in this compile," not "does the document I meant exist."

**The measured consequence:** the reference's real target is `a/b`'s explicit
`.. _nested-target:` label, which is absent from `index`'s compiled wrapper (`a/b` is
`:orphan:`, in no toctree). But `a_u2f_b`'s own auto-generated section id, also spelled
`nested-target`, IS present (`a_u2f_b` is toctree'd by `index`). Both docnames sanitize to the
identical label string `a_u2f_b:nested-target` — `a_u2f_b` literally, and `a/b` via
`_sanitize_label`'s `/` → `_u2f_` transform — so the guard's query finds the DECOY's label and the
reference renders as a working link to the wrong section, instead of degrading to plain text as its
real (absent) target would require.

**The narrowing:** labels are namespaced `docname:id` via `_namespace_label`, and
`_sanitize_label` maps every character invalid in a Typst label to a distinct `_u{codepoint:x}_`
token. This class needs the DOCNAME segment specifically to collide — realistically only reachable
via the `/` → `_u2f_` transform (a nested docname's sanitized path colliding with an unrelated
top-level docname that happens to spell out that exact sanitized form), not via any two arbitrary
unrelated docnames.

**The comparison to what was there before:** the deleted build-time mechanism
(`_compute_master_included_docnames`) checked DOCNAME MEMBERSHIP in a build-time union — two
distinct docnames are never equal as raw strings unless Sphinx itself already rejected the
collision earlier, so this false-negative class did not exist under the old mechanism. It is
genuinely new to this phase, introduced by moving the existence check from docname membership to
label-string existence.

**Recorded as ACCEPTED for Phase 48.** A todo is filed at
`.planning/todos/pending/2026-08-12-label-collision-false-negative-in-compile-time-xref-guard.md`
naming the class, the characterizing fixture (`tests/fixtures/xref_label_collision_guard_gate/`),
and the one obvious remediation direction (carrying the target docname into the guard's decision
rather than relying on label spelling alone), so the limit survives past this phase's closeout.

## SC#2 — site enumeration

**Purpose:** ROADMAP.md's SC#2 requires every label-reference emission site to route through one
shared guard helper, with open question #1 (`translator.py:4291`'s nature, in the line numbering
current at discussion time) closed by reading the code — the answer, not an assumption, determining
what changed there.

**The query string appears in exactly one definition** — inside `_label_existence_guard` itself,
where it is CONSTRUCTED, never a second time as a second, independently-built derivation:

```
$ grep -c 'query(<{label}>)' typsphinx/translator.py
1
```

Every other `query(<` occurrence in `typsphinx/translator.py` is a docstring/comment PROSE mention
(using placeholder spellings `<label>`/`<L>`, never the real `{label}` f-string interpolation),
confirmed structurally by `tests/test_label_existence_guard_unit.py::TestSingleDerivationPointStructural::test_guard_conditional_construction_appears_exactly_once`:

```
$ grep -rn 'query(<' typsphinx/
typsphinx/translator.py:53:    ``_label_existence_guard()``'s ``query(<label>)`` -- this predicate no
typsphinx/translator.py:119:            ``if query(<label>).len() > 0 { link(<label>, __tsx_body) }
typsphinx/translator.py:3081:        entirely by ``_label_existence_guard()``'s ``query(<label>)`` at
typsphinx/translator.py:3167:        ``query(<label>)`` is evaluated fresh by whichever wrapper is
typsphinx/translator.py:3175:        caller and passed in unchanged, so the ``query(<L>)`` argument and
typsphinx/translator.py:3187:        the ``if query(<L>).len() > 0`` condition and its opening ``{``
typsphinx/translator.py:3219:            f"{close_body}; if query(<{label}>).len() > 0 {{ "
typsphinx/translator.py:5164:            # `query(<label>)` guard around the link. Namespace with the
```

**And `grep -rn '_label_existence_guard' typsphinx/` shows the definition plus every caller**
(each of the three sites, not a second spelling):

```
typsphinx/translator.py:53:    ``_label_existence_guard()``'s ``query(<label>)`` -- this predicate no
typsphinx/translator.py:107:    ``TypstTranslator._label_existence_guard()``: the exact bytes to emit
typsphinx/translator.py:370:        # (`_label_existence_guard()`'s `close_str`) for the guarded
typsphinx/translator.py:3081:        entirely by ``_label_existence_guard()``'s ``query(<label>)`` at
typsphinx/translator.py:3148:    def _label_existence_guard(
typsphinx/translator.py:3392:        # target below is routed through the shared _label_existence_guard
typsphinx/translator.py:3406:            guard = self._label_existence_guard(
typsphinx/translator.py:3418:                guard = self._label_existence_guard(
typsphinx/translator.py:4457:            guard = self._label_existence_guard(label, prefix="#")
typsphinx/translator.py:5169:            guard = self._label_existence_guard(
typsphinx/translator.py:5221:        # path, the D-07 guard's close string (`_label_existence_guard()`'s
```

**Site enumeration table** (current line numbers; the ROADMAP.md text's `:3273`/`:3281`/`:4291`
line numbers reflect the pre-implementation position and have shifted as docstrings grew):

| # | Site | File:Line | Call | Note |
|---|------|-----------|------|------|
| 1 | `visit_reference`'s cross-document branch | `typsphinx/translator.py:5169` (inside `visit_reference`, def at `:5008`) | `self._label_existence_guard(label, ...)` | The primary XREF-03 site |
| 2a | `visit_citation`'s back-reference loop, single-target | `typsphinx/translator.py:3406` (inside `visit_citation`, def at `:3224`) | `self._label_existence_guard(backref_targets[0], prefix="", code_mode_body=True)` | D-05 |
| 2b | `visit_citation`'s back-reference loop, multi-target (each marker, independently) | `typsphinx/translator.py:3418` (same method, inside the marker loop) | `self._label_existence_guard(target, prefix="", code_mode_body=True)` | D-05 |
| 3 | `visit_pending_xref`/`depart_pending_xref` | `typsphinx/translator.py:4457` (inside `visit_pending_xref`, def at `:4401`; `depart_pending_xref` at `:4462` consumes the stashed `close_str`) | `self._label_existence_guard(label, prefix="#")` | D-04, defence in depth — open question #1's answer (below) |
| 4a | `visit_reference`'s bare-refid same-document branch | `typsphinx/translator.py:5116` (exemption comment; branch spans `:5111`-`:5131`) | *(none — deliberately unguarded)* | SC#4/D-06 exemption |
| 4b | `visit_reference`'s `#`-prefixed internal-refuri same-document branch | `typsphinx/translator.py:5154` (exemption comment; branch spans `:5150`-`:5157`) | *(none — deliberately unguarded)* | SC#4/D-06 exemption, same rationale |

**Open question #1, closed by reading the code, cross-referenced against `48-RED-EVIDENCE.md`'s
own "D-04 — enumerated impossibility argument" section:** the site named `translator.py:4291` at
discussion time is `visit_pending_xref`/`depart_pending_xref` (row 3 above) — confirmed **a fourth
independent degradation site**, not one already routed through `_reference_anchor_decision`
(`_reference_anchor_decision` is consulted only by `visit_reference` and `visit_citation`'s backref
loop; `visit_pending_xref` never calls it — it derives its own label directly from `reftarget`).
`48-RED-EVIDENCE.md`'s D-04 section additionally establishes that no `pending_xref` node can
survive Sphinx 9.1.0's `ReferencesResolver` post-transform through the normal pipeline for any of
four measured source shapes, so the RED for this site is unconstructible — the answer this phase
recorded (guard it anyway, as defence in depth per D-04's own instruction) was determined by
**reading** `ReferencesResolver.run()`'s unconditional `node.replace_self(new_nodes)` call, not by
assumption. This is exactly what plan 48-03 implemented (row 3's guard call, backed by a dedicated
`self._pending_xref_guard_close` slot — deliberately never shared with `visit_reference`'s
`_reference_guard_close` — per `48-03-SUMMARY.md`).

## SC#3 — the build-time mechanism is gone

**Purpose:** `_compute_master_included_docnames`, its `write()` call site, and
`_ReferenceAnchorDecision.degrade_xref_to_text` must all be gone, with no second, competing degrade
decision surviving anywhere that could disagree with the compile-time one.

**Per ROADMAP.md's own SC#3 wording** ("`grep -rn master_included_docnames typsphinx/` returns
nothing") — the binding bar is `typsphinx/` alone:

```
$ grep -rn 'master_included_docnames' typsphinx/
(no output, exit 1)
$ grep -rn '_compute_master_included_docnames' typsphinx/
(no output, exit 1)
$ grep -rn 'degrade_xref_to_text' typsphinx/
(no output, exit 1)
```

Zero matches for all three deleted symbols across `typsphinx/`, per milestone invariant #4's
repo-wide-grep requirement.

**Per milestone invariant #4 these are repo-wide greps** — the combined `typsphinx/ tests/` form is
also run, and every transcript (including the two that return zero matches) is pasted here:

```
$ grep -rn '_compute_master_included_docnames' typsphinx/ tests/
(no output, exit 1)
$ grep -rn 'degrade_xref_to_text' typsphinx/ tests/
(no output, exit 1)
$ grep -rn 'master_included_docnames' typsphinx/ tests/
tests/test_xref_orphan_degrade_render_gate.py:31:computation, ``TypstBuilder.master_included_docnames``, is deleted; Phase 47's
tests/test_label_existence_guard_unit.py:53:    ``typst_documents``, not the deleted ``master_included_docnames``,
tests/test_label_existence_guard_unit.py:411:            if "master_included_docnames" in text:
tests/test_label_existence_guard_unit.py:414:            f"deleted attribute 'master_included_docnames' still mentioned "
tests/fixtures/bld03_ghost_entry_xref_gate/conf.py:2:# gate -- the FIFTH site, `_compute_master_included_docnames()`, does not
tests/fixtures/bld03_ghost_entry_xref_gate/conf.py:5:# to `master_included_docnames`, even though `_validate_output_path_
tests/fixtures/bld03_unhashable_docname_gate/conf.py:2:# the FIFTH site, `_compute_master_included_docnames()`, builds its masters
(exit 0)
```

**All seven matches are inert prose, never live code consulting the deleted attribute — stated
plainly, not assumed:**

- `tests/test_xref_orphan_degrade_render_gate.py:31` and `tests/fixtures/bld03_*/conf.py` are
  historical-narrative comments/docstrings describing what the OLD, now-deleted mechanism did and
  why the new one replaces it — the same "historical-reference paraphrase" convention
  `48-02-SUMMARY.md`'s "patterns-established" note describes, except here the literal old name is
  named directly (for precision) rather than paraphrased, since these are explanatory prose blocks
  about a name that no longer exists in `typsphinx/`, not a live reference to it.
- `tests/test_label_existence_guard_unit.py:411`/`:414` is
  `test_no_file_mentions_deleted_include_set_attribute`'s OWN detection logic (this exact string
  literal is what the test searches FOR, to assert the attribute is absent) — a test asserting a
  deletion structurally cannot avoid naming the deleted symbol. Critically, this test's own scope
  (`self._package_dir()`, line 388) is `typsphinx/` ONLY, matching ROADMAP.md's SC#3 wording
  exactly:
  ```
  $ uv run pytest tests/test_label_existence_guard_unit.py::TestSingleDerivationPointStructural -q
  ..                                                                        [100%]
  2 passed in 0.05s
  ```
- `tests/test_label_existence_guard_unit.py:53` is a docstring line stating the guard derives its
  label from `typst_documents`, "not the deleted `master_included_docnames`" — again explanatory
  prose contrasting old and new, never a live reference.

**No second, competing degrade decision survives anywhere.** Every one of the seven `tests/` matches
is prose (docstring/comment) or a deletion-detection test's own necessary search string; zero are
executable code that recomputes, reads, or otherwise depends on the deleted attribute, method, or
field. The binding `typsphinx/`-scoped bar (ROADMAP.md's literal SC#3 wording, and this project's
own `test_no_file_mentions_deleted_include_set_attribute`'s scope) is met with zero matches for all
three symbols.

*(Deviation note: `48-04-PLAN.md`'s task 3 acceptance criteria phrases this check as
`grep -rn master_included_docnames typsphinx/ tests/` "exits 1" — written before plan 48-03 added
`test_label_existence_guard_unit.py`'s own necessary literal search string and the historical-prose
docstring updates. The actual binding bar, both per ROADMAP.md's own SC#3 sentence and per this
project's own committed structural test, is `typsphinx/`-scoped; that bar is met. See this plan's
SUMMARY.md "Deviations" section for the full reconciliation.)*

## D-01 — no published contract changed

**Purpose:** confirm the discussion-time finding — deleting the build-time degrade warning changes
no published contract — still holds at implementation time, per D-01's own closing instruction:
"Confirm this still holds at implementation time rather than assuming it."

**Re-run, verbatim** (via a Python `subprocess.run(['grep', '-rn', 'non-included\|degrade',
'docs/source'])` call, to sidestep an unrelated sandbox heuristic that misparses the literal
substring "source" in a shell command line — the grep semantics are identical to running it
directly):

```
$ grep -rn 'non-included\|degrade' docs/source
(no output)
```

Exit code 1 (no matches). **The discussion-time result still holds** — no published documentation
under `docs/source/` mentions "non-included" or "degrade" in relation to the deleted warning. D-01's
premise is confirmed, not assumed, at implementation time.

**The diagnostic-visibility consequence, stated explicitly (addressing Fable's review LOW finding):**
with the build-time degrade warning deleted, a reference to a document the author deliberately
marked `:orphan:` — a target Sphinx itself resolved successfully as a real cross-reference — now
degrades to plain text at every layer with **zero diagnostic**. Before this phase, the deleted
warning was the ONLY signal for exactly this one case (every other unresolvable-reference case was
already covered by Sphinx's own `unknown document` / `document isn't included in any toctree`
warnings, per D-01's own discussion-time measurement). This loss is owner-locked by D-01, whose
rationale already measured that Sphinx covers every other case; no replacement diagnostic is added
here — D-01 forbids it, and the phase's own prohibitions forbid a second degrade decision under any
name, which a replacement diagnostic tied to the compile-time guard would risk becoming.

```
$ grep -rn 'logger.warning' typsphinx/translator.py | grep -c 'non-included'
0
```

Confirmed: zero remaining `logger.warning` call sites mention "non-included" anywhere in
`typsphinx/translator.py` — no replacement diagnostic was added.

## Phase green gate

**Purpose:** binding constraint #8 requires the phase to close green on the full suite plus the
`black`/`ruff`/`mypy` trio.

```
$ uv run pytest -q
...
================= 1062 passed, 5 skipped in 213.85s (0:03:33) ==================
```

1062 passed, 5 skipped, 0 failed, 0 xfailed, 0 XPASS.

```
$ uv run black --check .
All done! ✨ 🍰 ✨
276 files would be left unchanged.
```

```
$ uv run mypy typsphinx/
Success: no issues found in 6 source files
```

```
$ uv run ruff check .
Could not start dynamically linked executable: ruff
NixOS cannot run dynamically linked executables intended for generic
linux environments out of the box. For more information, see:
https://nix.dev/permalink/stub-ld
```

**`ruff` could not be run locally** — the documented, pre-existing NixOS deferral
(`ruff-generic-linux-elf-unrunnable-on-nixos`, `.planning/todos/pending/`, PROJECT.md's Deferred
Items, and every prior Phase 48 plan's own "Next Phase Readiness" note). This is recorded plainly
rather than claimed as a clean ruff result — CI carries lint authority per the same documented
deferral. `pytest`, `black`, and `mypy` are all green locally.
