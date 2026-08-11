# Pitfalls Research: v0.8.0 multi-master composition

**Domain:** Restructuring Sphinx-extension output composition (Sphinx `Builder`/`Writer`/`SphinxTranslator`
layering → Typst `#include()` file graph → `typst-py` compile)
**Researched:** 2026-08-11
**Confidence:** HIGH where a claim cites a `typsphinx` file/line or an upstream source file/line read
directly during this research; MEDIUM/LOW where marked **inferred** (architecturally grounded but not
exercised live).

This file supersedes generic composition-refactor advice with pitfalls specific to *this* change in
*this* codebase: `typsphinx/builder.py`, `typsphinx/writer.py`, `typsphinx/translator.py`, and the Typst
compile semantics `typst-py` enforces. Every pitfall names the exact mechanism it threatens.

---

## Critical Pitfalls

### Pitfall 1: The wrapper's DFS must replicate Sphinx's OWN parent-resolution order, not just its membership

**What goes wrong:**
The design closes the diamond `M → [p, q], p → [c], q → [c]` by moving the include decision into the
wrapper (verified sound — see Pitfall 3). But there is a second, easier-to-miss requirement hiding
inside "mirror `inline_all_toctrees`": **which parent wins is order-dependent, not just
membership-dependent.** Sphinx's real `inline_all_toctrees` (`sphinx/util/nodes.py:485`, read directly)
recurses through a document's own toctree nodes **in the literal order they appear in that document's
source**, threading one mutable `traversed: list[str]` through the recursion. A child already in
`traversed` is skipped when the *next* toctree entry reaches it — so "prefer the deeper path" is really
"whichever parent's subtree the DFS reaches first, by document order, wins." The measured case in
PROJECT.md (`zmid` beating `xmaster` for `shared`) is a specific instance of this, not a standing
"always prefer nested" law — a project where the direct `xmaster → shared` entry is written *before*
`xmaster → zmid` in the rST source would resolve the other way.

The codebase already has a superficially similar traversal that computes the WRONG order for this
purpose: `TypstBuilder._compute_master_included_docnames()` (`builder.py:118-154`) walks
`env.toctree_includes` with `stack.pop()`/`stack.append(child)` — a LIFO stack. Because children are
appended in list order and popped last-in-first-out, this traversal visits a master's children in
**reverse of their source order**, which happens to be harmless today because that method only computes
a *set* (membership, order-irrelevant, feeds the build-time degrade boolean this milestone deletes
anyway). If the new wrapper-DFS-with-heading-offset code is grown by generalizing this existing method
(the obvious, natural refactor path — "we already have toctree-closure code, let's reuse it"), it will
silently reproduce the reversal, and the wrapper will nest a shared document under the wrong parent (or
the parent Sphinx's own relations/prev-next model would not have chosen), giving it the wrong
`set heading(offset: N)` and, per Pitfall 2, the wrong position in that master's figure/table/heading
numbering — with **zero compile error**, since Typst does not know what depth was "correct."

**Why it happens:**
Two pieces of `typsphinx` code look like they solve the same problem (toctree closure) but actually
answer different questions — "is X reachable from master M" (order-irrelevant, existing code) vs. "under
which parent, at what depth, does X appear in M" (order-critical, new code) — and refactoring pressure
pushes toward collapsing them into one.

**How to avoid:**
Write the wrapper-generation DFS as new code with an explicit `traversed: list[str]` (or `set[str]`
checked in *document appearance order*) reinitialized per master, iterating each toctree node's
`entries`/`includefiles` in the order Sphinx recorded them — not by re-deriving membership from
`env.toctree_includes` with a LIFO stack. Do not delete or refactor
`_compute_master_included_docnames` into the new code path; either retire it outright once the
build-time degrade boolean it feeds is deleted (see Pitfall 6), or keep it isolated if anything else
still needs pure membership.

**Warning signs:**
A code review or test that reuses `stack.pop()`/`.append()` order, or that computes the wrapper's
include list from a `set` instead of an ordered structure. A regression fixture with **two** candidate
parents for one shared child, asserting the exact resulting `heading(offset:)` value (not just "compiles
and both headings appear").

**Phase to address:**
The phase implementing wrapper generation / the include-graph DFS. Success criterion: a fixture
reproducing PROJECT.md's own measured `xmaster`/`zmid`/`shared` shape, asserting the wrapper nests
`shared` under the SAME parent Sphinx's `inline_all_toctrees`/relations model would choose, with a
mirror-image fixture (entries reordered) proving the choice tracks source order rather than being a
hardcoded "prefer nested" rule.

---

### Pitfall 2: `:numref:` text is baked in by Sphinx's whole-project numbering, but Typst's figure/table counters are per-compiled-wrapper

**What goes wrong (inferred — verify with a live fixture before treating as settled):**
`TypstBuilder.write()` deliberately calls `env.get_doctree()` + `self.env.apply_post_transforms(doctree, docname)` instead of `env.get_and_resolve_doctree()`, specifically to preserve toctree
nodes (`builder.py:390-397`, docstring: *"For Typst, we need the original toctree nodes... uses
env.get_doctree() instead"*). `apply_post_transforms` still runs Sphinx's full post-transform registry
— confirmed by reading `sphinx/environment/__init__.py:759-776` — which includes `:numref:`/`:ref:`
resolution. That resolution substitutes literal text ("Figure 3", "Table 12") into the `reference` node
**using Sphinx's own project-wide `env.toc_fignumbers`**, computed once during the read phase over
Sphinx's single canonical toctree structure. `typsphinx/translator.py` has **zero** references to
`numfig`/`fignumber`/`secnumber` (grepped, confirmed empty) — it never overrides this text; it just
emits whatever string Sphinx already baked in, inside a `link(...)`.

Typst's own figure/table auto-numbering (`figure()`'s built-in counter) is **global to one compiled
document** and counts strictly in the order figures actually appear in *that compilation's* flattened
content — i.e., in one master's wrapper-DFS order, counting only the figures that master's DFS actually
reaches. Once `typst_documents` declares more than one master with *different* DFS subsets/depths (the
whole point of this milestone), Sphinx's single global fignumber and Typst's own per-wrapper figure
counter can diverge: a figure Sphinx numbers "Figure 12" project-wide may be genuinely "Figure 3" inside
a specific master's independently-compiled PDF (fewer preceding figures were pulled into that master's
DFS). The `:numref:` text would then read "see Figure 12" pointing at a link that lands on a figure
captioned "Figure 3" — a silent, wrong-but-compiling number, not a `label ... does not exist` fatal, so
none of this milestone's compile-based GATE-01 methodology catches it by default.

**Why it happens:**
This is the natural consequence of composing at the FILE layer (Typst's own numbering) while Sphinx's
`:numref:` resolution happens at the PROJECT layer (one env-wide numbering scheme) — the milestone's own
"Key context" already names the file-layer-vs-doctree-layer tension for label duplication; the same
tension applies to any Typst-native auto-numbering feature, and `:numref:` is the one place `typsphinx`
currently depends on Sphinx doing that numbering FOR it rather than deriving it from Typst state.

**How to avoid:**
Before closing this milestone, build a two-master fixture where the SAME `:numref:`-targeted figure
sits in a shared content file included at different DFS positions/depths by two masters, and measure
the printed "Figure N" text against the actual Typst-rendered caption number in each master's PDF via
`pypdf` text extraction. If they diverge (expected per this analysis), either (a) document it as a known
multi-master limitation in the CHANGELOG/README (numref text reflects Sphinx's project-wide numbering,
not the per-master compiled number) — the cheap, in-scope option — or (b) file it as a Future
requirement to replace the baked-in text with a Typst-native `ref()`/counter call that renders
dynamically per compile. Do not silently assume it "just works" because it compiles.

**Warning signs:**
Any success criterion phrased as "`:numref:` resolves correctly" without a concrete before/after number
comparison across two masters with different DFS subsets containing the same referenced figure.

**Phase to address:**
The phase implementing the wrapper-graph DFS (surfaces the divergence) should at minimum measure and
document it; a follow-up phase (or explicit Future item) if (b) is chosen.

---

### Pitfall 3: The diamond IS solved by the wrapper design — but only for shapes where the shared file's identity is unambiguous; self-referential and glob-driven shapes need separate checks

**Verification of the owner's claim:** confirmed sound. Once the include decision (which files, in
which order, at which depth) lives entirely in each master's OWN wrapper — generated once per master
from that master's own DFS closure — two different masters can each embed the same content file at
their own chosen depth with no shared mutable state between them (unlike today, where
`TypstBuilder._included_docnames` is a **build-wide** set shared across every master's `visit_toctree`
call, `builder.py:88-99`, and a global "who wrote this label first" decision leaks between unrelated
masters). This structurally removes the M/M′ diamond, matching the PROJECT.md reasoning.

**Other graph shapes with the same structural property (also solved by the wrapper, verify during
planning):**
- **Any N-master, N-diamond fan-out** — the general case, not just 2 masters × 1 shared child. Each
  wrapper's DFS is independent, so this generalizes for free; a regression fixture with 3+ masters
  sharing 2+ overlapping children is cheap insurance the fix isn't accidentally 2-master-specific.
- **A document appearing under TWO different toctrees of the SAME master** (the actual measured
  `env.toctree_includes` example from Sphinx's own docs: `usage/extensions/index` listed both directly
  and nested under `usage/index`) — already the ordinary within-master dedup case Pitfall 1 covers; the
  wrapper's own `traversed` list (reinitialized per master, per the milestone's stated design) handles
  it identically to the cross-master diamond.

**Shapes that remain problematic even with the wrapper design (must be explicitly decided, not
discovered late):**
- **Cycles in `toctree`** — `a` toctrees `b`, `b` toctrees `a`. Sphinx's own `inline_all_toctrees`
  guards this with the same `traversed` list (a cycle just means `a` is already in `traversed` by the
  time the recursion loops back), so a naive port of that guard is already safe *if Pitfall 1's ordering
  fix is done correctly* — but this is exactly the kind of edge a hand-rolled DFS (as opposed to a
  faithful port) can get wrong in a way that infinite-loops the build instead of degrading gracefully.
  Needs its own fixture, not just inference from the diamond fixture.
- **Self-references** (`a` toctrees itself, directly or via a glob) — same guard, same requirement for
  an explicit fixture; a subtly different failure mode from the 2-node cycle (immediate self-skip on the
  first recursive call rather than a skip one level down).
- **`:orphan:` documents** — correctly EXCLUDED from every `env.toctree_includes` entry (confirmed:
  `builder.py:118-133`'s own docstring states this and it is upstream, structural Sphinx behavior, not
  something typsphinx computes). Not a diamond hazard, but the cross-document reference to an orphan is
  exactly the case Pitfall 6 covers — the wrapper design doesn't change orphan exclusion, only how the
  *reference* to an orphan degrades.
- **Glob toctrees (`:glob:`)** — confirmed (web search of Sphinx toctree docs) that Sphinx expands glob
  patterns into concrete docnames alphabetically **before** populating `env.toctree_includes`, so by the
  time the wrapper's DFS reads it, a glob toctree looks identical to an explicit list — no special
  handling needed in the DFS itself. The alphabetical ordering IS the "document order" for a glob entry,
  which matters for Pitfall 1 (the DFS must still process that alphabetical sequence in order, not
  re-sort it).
- **`.. only::`-pruned entries** — this is a doctree-content-level prune (evaluated per-document during
  read/transform), not a toctree-membership-level one; a document pruned by `.. only::` inside a toctree
  directive's OWN entry list is a different mechanism than the `env.toctree_includes` edges the wrapper
  DFS reads. `40.1`'s own prior work (referenced in `translator.py:3252-3260`, the citation backref
  `ref_node is None` handling) is the closest existing precedent for "a reference to something
  `.. only::` pruned must fail closed, not assume eligibility" — the same discipline applies to any
  wrapper-DFS entry whose target turns out unreadable/pruned. Confirm this is still exercised once
  `visit_toctree` stops emitting includes and the graph-walking logic moves to a new file/method.

**Phase to address:** the phase implementing wrapper generation. Success criteria: one fixture per
listed shape (cycle, self-reference, orphan-reference, glob toctree, `.. only::`-pruned entry), each
with an explicit expected outcome (degrade-to-text, skip, or specific structural assertion) decided
during planning rather than discovered as a test failure during execution.

---

### Pitfall 4: CR-01's `effective != docname` exemption is a landmine once every docname's content file always exists

**What goes wrong:**
`_resolve_output_stem`'s collision guard (`builder.py:264-283`, CR-01) is:

```python
effective = self._directory_preserving_relpath(docname, stem)
found_docs = getattr(self.env, "found_docs", None) or set()
if effective != docname and (
    effective in found_docs or effective == "_template"
):
    logger.warning(...)
    return docname
```

The `effective != docname` clause deliberately **exempts** the case where a master's OWN resolved
target path equals its OWN docname's path — because today that is the single common, legitimate case
(`typst_documents = [('index', 'index.typ', ...)]`, or any target name that resolves to the same stem
as the docname): before this milestone, `index.typ` IS both the content and the template-wrapped master,
written once, by the same `is_master`-gated write path. Under the new split, `write_doc` will
**unconditionally** write a template-less content file at every docname's own path — including the
master's — while the wrapper generator will **separately** want to write a template-carrying file at the
master's resolved target path. When the target resolves to the SAME path as the master's own docname
(exactly the case this guard exempts), the wrapper write and the content write collide on one physical
file. Whichever runs last wins silently: if content-write runs last, the "wrapper" is actually a bare
template-less content file and `TypstPDFBuilder.finish()` compiles it with no template and no includes
(a PDF with no title page, no `#outline()`, and none of its toctree'd children) — a build that reports
success and produces a badly wrong PDF, with no `TypstError` to catch it (defeats GATE-01's classic RED
entirely, since this doesn't even fail to compile).

**Why it happens:** the exemption clause is correct for the CURRENT model and becomes wrong the moment
"master's own docname" stops being a synonym for "the master's whole file."

**How to avoid:** Before or during the wrapper/content split, re-derive CR-01's guard for the two-file
world: decide explicitly whether a `typst_documents` target name is allowed to equal its own master's
docname (if allowed, the wrapper and content paths must be forced to differ some other way — e.g.
suffix, or writing content under a reserved subpath); if disallowed, the `effective != docname`
exemption must be removed and replaced with a clear warning + fallback, following CR-01's own established
convention ("fall back to the docname with a WARNING, never invent a filename the user did not write" —
except here the docname itself is the collision, so the fallback needs its own rule, e.g. a fixed
wrapper suffix). This is exactly the shape of hazard CR-02 (duplicate targets across masters) already
targets — this is CR-02's sibling defect (a target colliding with *itself*, not with another master),
and should be scoped alongside it rather than assumed covered by it.

**Warning signs:** a test asserting `typst_documents = [('index', 'index.typ', ...)]` (or any config
where target name stem == root docname) still produces a title page / `#outline()` / included children
in the compiled PDF — not just "compiles and produces a PDF," since a silently-wrong content-only
"wrapper" also compiles fine.

**Phase to address:** the phase implementing CR-02 (duplicate-target detection) — natural to extend the
same collision-registry work to cover self-collision, since both are instances of "two logical files
want the same physical path."

---

### Pitfall 5: Case-insensitive filesystems can hide a wrapper/content or CR-01/CR-02 collision that Linux CI never sees

**What goes wrong:** every collision guard discussed above (`_resolve_output_stem`'s CR-01 check,
`effective in found_docs`, any future CR-02 duplicate-target registry) does plain Python `==`/`in`
string comparison — case-sensitive. Linux ext4 (the primary dev/CI filesystem) is case-sensitive, so
two paths differing only by case are genuinely different files there and any collision-guard gap goes
unnoticed. macOS's default APFS and Windows' NTFS are both case-insensitive by default. This project's
CI already runs a 3-OS matrix and has twice been bitten by exactly this class of platform-only defect
reaching CI late (the Windows cp1252 encoding defect in v0.7.0's PR #129, the Windows-only
path-separator defect in v0.7.1 — both named directly in the milestone's own question). A wrapper name
that differs from a content docname only by case (e.g. a derived default like `TypstManual.typ`
alongside a real docname `typstmanual/index`, or a user-supplied target name that happens to
case-collide with another docname) would pass every collision guard on Linux CI, then silently overwrite
one of the two files on a macOS or Windows checkout — and this milestone is exactly the moment new
wrapper-vs-content collision surface is being introduced (Pitfall 4).

**How to avoid:** add at least one case-differing collision fixture (e.g. target name `Manual.typ`
colliding with docname `manual`) to the CR-01/CR-02 regression suite, and assert the SAME warning fires
regardless of host OS filesystem case-sensitivity — i.e., make the collision check itself
case-normalized (`.lower()` both sides before comparing) rather than relying on the guard's exact-match
semantics, so behavior doesn't silently vary by platform. This is cheap to do proactively and expensive
to discover only when the 3-OS CI matrix runs on the actual milestone branch.

**Warning signs:** any collision-guard test written using only lowercase docnames/targets, or asserting
collision detection with `assert x == y` rather than including a case-varied negative/positive pair.

**Phase to address:** the same phase implementing CR-01's extension (Pitfall 4) / CR-02, plus a
CI-matrix confirmation once the milestone branch is pushed (see Pitfall 12 on pushing early).

---

### Pitfall 6: Deleting the build-time boolean must not leave a second, now-orphaned degrade mechanism half-alive

**What goes wrong:** `builder.py:100-154`'s `master_included_docnames` machinery
(`_compute_master_included_docnames`, populated once in `write()`, consulted in
`translator.py:3073-3075`) is explicitly the mechanism this milestone replaces with the `context` +
`query` compile-time guard. It has **three** consumers to track down and retire together, not just the
one already named in PROJECT.md: `_reference_anchor_decision` (`translator.py:3070-3076`, the primary
site), and the **two further sites carrying the same label-reference shape** PROJECT.md's own "Key
context" flags for enumeration — citation back-references (`translator.py:3273/3281`) and one more at
`:4291`. Read together, `visit_citation`'s backref loop (`translator.py:3248-3296`) calls
`_reference_anchor_decision` per backref target, so it inherits the new guard automatically THROUGH that
shared predicate — but only if the migration touches `_reference_anchor_decision`'s single derivation
point and does not leave a second, parallel `master_included_docnames` check anywhere else that was
copy-pasted rather than routed through the shared helper. A partial migration — e.g., updating
`_reference_anchor_decision` to the new compile-time guard but leaving `builder.py`'s
`master_included_docnames` computation and `_included_docnames` dedup ledger in place "just in case" —
creates two competing, subtly different degrade decisions that can disagree (build-time set says "not
reachable," runtime `query()` says "exists," or vice versa if the wrapper's DFS diverges from the old
BFS-based closure per Pitfall 1).

**How to avoid:** when this lands, delete `master_included_docnames`,
`_compute_master_included_docnames`, and their call site in `write()` in the SAME change that
introduces the `context`+`query` guard — do not keep both live "for safety." Grep for every read of
`builder.master_included_docnames` (not just the translator's `getattr` site) before considering the
migration complete, and confirm `translator.py:4291`'s site (unread during this research pass — flag for
the executing phase to inspect) uses the same shared predicate rather than a fourth independent
derivation.

**Warning signs:** `master_included_docnames` or `_compute_master_included_docnames` still present in
`builder.py` after the guard lands; any `getattr(self.builder, "master_included_docnames", ...)` call
site outside `_reference_anchor_decision`.

**Phase to address:** the phase implementing the compile-time `context`+`query` guard. Success
criterion: `grep -rn master_included_docnames typsphinx/` returns nothing post-change (or, if a decision
is made to keep it for some OTHER purpose, that purpose is named explicitly rather than left as
leftover surface).

---

### Pitfall 7: Regenerating expected strings from the new emitter, not deriving them independently, launders the GATE-01 gate

**What goes wrong:** this milestone moves output from "one master `.typ` carries body+template" to
"wrapper `.typ` + content `.typ`," so **every** exact-string assertion against a master's file contents
(v0.7.0's comparable change measured 10 files / 61 classes; this milestone's blast radius is likely
comparable or larger since `_is_master_document` disappears entirely, not just specific handlers) needs
new expected strings. The trap: writing the new code, running it, copy-pasting whatever it emits into
the test as the new "expected" string, and calling the test suite green. That process cannot fail — it
mechanically proves the code does what the code does, never that it does what it SHOULD do. It is
specifically dangerous here because the change is BROAD (every master-touching test) and mechanical
(the same wrapper-header + include-list shape repeats across dozens of fixtures), which is exactly the
condition under which a human reviewer's attention fatigues and stops actually reading each generated
string.

**Why it happens:** it is the path of least resistance under time pressure, and — unlike v0.7.0's
node-handler-level GATE-01 fixtures, which each targeted ONE defect with a hand-derivable expected
shape — a structural refactor genuinely has no single external "authority" (no HTML/LaTeX reference
render) for "what should the wrapper file's include list look like" beyond re-deriving it from the
config + toctree graph by hand.

**How to avoid:** for each migrated fixture, derive the expected wrapper structure from FIRST
PRINCIPLES before running the new code — from `typst_documents` config plus the toctree source
literally read from the `.rst` fixture files (not from the translator's output) — write down "wrapper
should include A, B in that order, with offsets 1, 2" as a comment or docstring BEFORE implementing, the
same discipline `test_duplicate_include_label_render_gate.py` / `test_xref_orphan_degrade_render_gate.py`
already apply to labeling/degrade fixtures. For the STRUCTURAL properties (which files are `#include()`d,
in what order, at what offset; which file carries the template imports; that content files carry the
minimal `@preview` import block unconditionally now) prefer regex/structural assertions over full
exact-string diffs, reserving exact-string assertions for the parts that are genuinely
deterministic-by-construction (e.g. the literal `@preview` import lines, which the version-sync test
already pins independently).

**Warning signs:** a test diff where the "expected" value block was clearly pasted from a debug print of
the actual output (identical whitespace/ordering quirks that would be tedious to hand-type); a PR where
every migrated fixture's expected string changed but no PR description explains WHY each one is now
correct as opposed to just "what the code now does."

**Phase to address:** every phase touching the wrapper/content split and its test migration; called out
explicitly as a review gate (not just a coding task) given the size of the blast radius.

---

### Pitfall 8: "Structural, not compile-fatal" defects need the GATE-01 RED redefined per-fixture, same as v0.7.0's own documented exception

**What goes wrong:** the milestone's own "Key context" states all three named defects (B-1, B-2, defect
A) genuinely fail today — either a hard `TypstError` (B-1: `file not found`) or a measurably wrong
structure (B-2: template re-expanded mid-body; defect A: a document silently dropped from one PDF). That
means the classic GATE-01 RED (`TypstCompilationError` before, valid `%PDF` after) is available for
those three — good, this is the EASY case. But v0.7.0's own precedent (documented in its milestone brief,
retained in PROJECT.md) is the warning: not every change in a "structural, not handler-level" milestone
gets to use that classic RED. Several v0.8.0 sub-changes are exactly the class v0.7.0 flagged — CR-02
duplicate-target detection (today: exit 0, no warning, first master's body silently gone — a
non-fatal-but-wrong outcome, same shape as v0.7.0's design defects) and the two PR #131 image-path
defects (one is a WRONG picture rendered with no warning — compiles fine, is simply incorrect content).
For these, "does not compile" is unavailable as the RED state and each needs its own structural/regex/
`pypdf`-text RED assertion defined BEFORE the fix, exactly as v0.7.0's GATE-01 methodology amendment
required — otherwise the "fixture" degrades into Pitfall 7's laundering trap by default, since a
non-fatal defect has no natural RED to distinguish "proves the fix" from "proves the code ran."

**How to avoid:** classify every requirement in this milestone, at planning time, into "genuine compile
fatal today" (classic RED available: B-1, B-2's silent-template-reexpansion is arguably NOT a compile
fatal though — check this explicitly, it may belong in the other bucket too — and defect A) vs.
"compiles fine, produces wrong output today" (CR-02, both image defects) — and for the second bucket,
write the RED-state assertion (e.g., `pypdf` page/text comparison proving the FIRST master's body is
actually missing today, or the WRONG image bytes are embedded today) as an explicit success criterion
before implementation starts, mirroring v0.7.0's own amendment rather than re-discovering the need for
it mid-phase.

**Warning signs:** a phase plan that lists "GATE-01 fixture" as a checkbox without naming, in advance,
what the pre-fix RED assertion actually checks for a non-fatal defect.

**Phase to address:** phase planning for CR-02 and the two image-defect fixes specifically; the
wrapper/content split phases likely get the classic RED for free (B-1/B-2/defect A) but should still
verify B-2 isn't secretly in the non-fatal bucket.

---

### Pitfall 9: `write()` computes per-master graph state up front; `write_doc()` no longer needs the ledger, but `finish()` is now where wrapper files must be written — and `TypstPDFBuilder` overrides both

**What goes wrong:** today, `TypstBuilder.write()` (`builder.py:384-444`, NOT overridden by
`TypstPDFBuilder`) computes `master_included_docnames` up front (before any `write_doc` call) precisely
because a cross-document reference can be emitted before the toctree that includes its target is
processed — order-of-visitation independence was already a hard-won lesson here (`builder.py:422-428`
comments this explicitly). The new wrapper-writing step introduces a genuinely NEW ordering
constraint: a wrapper needs the RESOLVED graph (which content files it includes, at what depth) but does
NOT need each content file's doctree — only the docname graph, which is available from
`env.toctree_includes` alone, without waiting for `write_doc` to run for every content file. Two
plausible-looking but wrong placements:
- Writing wrapper files inside the `write_doc` loop, keyed off `docname` — wrong, because a wrapper is
  a per-MASTER artifact, not a per-DOCNAME one, and the loop iterates `sorted(docnames)`, not masters;
  shoehorning wrapper-emission into that loop (e.g., "when docname is a master, also emit its wrapper")
  works only by accident of docname/master overlap and complicates the CR-01/CR-02 self-collision
  question (Pitfall 4) further by writing wrapper and content on the same iteration.
- Writing wrapper files in `finish()` unconditionally — `TypstBuilder.finish()` (`builder.py:889-897`)
  today only copies images/assets; `TypstPDFBuilder.finish()` (`builder.py:960-1074`) overrides it,
  calls `super().finish()` first, THEN compiles. If wrapper-writing is added to `TypstBuilder.finish()`,
  it runs correctly for `-b typst`; for `-b typstpdf`, `TypstPDFBuilder.finish()`'s `super().finish()`
  call must still trigger it BEFORE the compile loop that follows — a plausible but easy-to-invert
  ordering bug, especially since `TypstPDFBuilder.write_doc()` is its OWN override
  (`builder.py:915-958`) that duplicates `TypstBuilder.write_doc()`'s body almost exactly (both call
  `_resolve_output_stem`/`_directory_preserving_relpath`/`post_process_images`/`self.writer.translate()`)
  — any wrapper-related change made in one override and forgotten in the other silently diverges the two
  builders' output shape.

**How to avoid:** write wrapper generation as a NEW method (e.g. `_write_master_wrappers()`) called once
from a single shared place both builders reach — `write()` (after the `write_doc` loop, since
`TypstBuilder.write()` is NOT overridden by the PDF builder and both builders' actual document-writing
happens through the `write_doc` calls it drives) is the natural single call site, avoiding the
`finish()` override-duplication risk entirely, and keeps the existing "compute graph state up front,
independent of write order" discipline `write()` already established for `master_included_docnames`.
Whatever site is chosen, add an explicit test asserting the SAME wrapper file is produced (byte-for-byte
or structurally) whether the build runs `-b typst` or `-b typstpdf` — the two builders' write_doc
duplication makes silent divergence a standing risk that predates this milestone but this milestone adds
a new artifact (the wrapper) that duplication could newly diverge on.

**Warning signs:** wrapper-writing logic present in `TypstPDFBuilder.write_doc` but absent from
`TypstBuilder.write_doc`, or vice versa; a wrapper produced by `-b typst` that differs from the wrapper
`-b typstpdf` compiles from.

**Phase to address:** the phase implementing wrapper generation, with an explicit success criterion
comparing `-b typst` and `-b typstpdf` wrapper output for the same project.

---

### Pitfall 10: `-j` parallel builds and incremental rebuilds interact with per-build, cross-master mutable state

**What goes wrong:** `TypstBuilder` declares `allow_parallel = True` (`builder.py:61`). The CURRENT
`_included_docnames` ledger is explicitly a **whole-build, cross-master** mutable set
(`builder.py:88-99`, reset once per `write()` call at `builder.py:420`) — this is fine today because
Sphinx's parallel `-j` write phase still funnels through one process's `write()` call for the ledger's
purpose (image tracking / doc writing get parallelized by Sphinx internally via `parallel_available`
paths in `Builder.write`, but this project's OWN `write()` override, per its docstring, replaces the
default `env.get_and_resolve_doctree()`-based loop with its own SERIAL `for docname in sorted(docnames)`
loop — confirmed by reading `builder.py:430-444`: there is no parallel dispatch in this override at all,
so `allow_parallel = True` is declared but the actual write loop is already always serial). This is
good news: it means the existing ledger-mutation pattern is already safe from a `-j`-induced race, and
the new wrapper-DFS state (computed once, up front, from `env.toctree_includes`, independent of
`write_doc` order) inherits that same safety by construction, AS LONG AS the new wrapper-writing code is
also placed in this same serial `write()`/single-process path (Pitfall 9) rather than accidentally
threaded through Sphinx's own parallel image/asset-copy machinery.

The genuine incremental-build risk is different: `get_outdated_docs()` (`builder.py:325-335`) always
yields every docname (full-rebuild-every-time — confirmed, no staleness comparison against `self.env`).
Wrapper files are NOT docnames and are not tracked by this method at all — if a future change makes this
builder incremental-aware (out of scope for THIS milestone, but a natural next request once composition
correctness is fixed), a stale wrapper (written once, never invalidated when its included content
changes) becomes a new staleness class this milestone's design must not make harder to add later. Not
urgent for v0.8.0 itself, but worth a one-line note so wrapper-writing isn't implemented in a way that
assumes "runs exactly once, full rebuild only" so tightly that a later incremental-build feature has to
redesign it.

**How to avoid:** keep wrapper generation in the same up-front, full-graph-computed, serial phase as
`master_included_docnames` was; do not key it off per-document write order or any per-`write_doc` local
state. No code change needed for THIS milestone beyond confirming the placement (Pitfall 9); note the
future-incremental-build consideration in a comment near the new wrapper-writing method so it isn't
"discovered" as a surprise later.

**Warning signs:** wrapper-writing code reading or mutating any state that ALSO gets written inside the
per-docname `write_doc` loop.

**Phase to address:** the phase implementing wrapper generation (placement decision only); no dedicated
phase needed for incremental-build support (explicitly out of scope).

---

### Pitfall 11: The wrapper's relative-include-path math must be based on the RESOLVED wrapper location, not the master's raw docname — this is B-1 itself, and the fix must not reintroduce it one level up

**What goes wrong:** `_compute_relative_include_path(target_docname, current_docname)`
(`translator.py:4305-4414`) computes purely DOCNAME-to-DOCNAME relative paths via `PurePosixPath`,
assuming the file at `current_docname` and the file at `target_docname` sit at their docname-derived
locations. That assumption is exactly what B-1 already violates today for a MASTER whose target name
differs from its docname (`_resolve_output_stem` names the file from the TARGET; `visit_toctree`
computed the include path from the DOCNAME — `builder.py:156-166`'s own docstring literally names this
class of bug: *"the parent includes `guide/index.typ` from the docname while `_resolve_output_stem`
names the file from the target"*). The fix must route the wrapper's own include-path computation through
the SAME resolved-stem + directory-preserving-relpath logic `_resolve_output_stem`/
`_directory_preserving_relpath` already implement for the master's OWN file location — not just for the
master, but for EVERY content file the wrapper includes, since any of them could, in principle, also
have been affected by a differently-shaped future change (today only masters get custom target names,
but the new design's wrapper-generation code is new code, and if it's written by literally reusing
`_compute_relative_include_path(child_docname, master_docname)` unchanged, it silently reintroduces B-1
one level up: it would compute the relative path from the master's DOCNAME's location, not the WRAPPER's
actual resolved output location, which can differ whenever the target name changes the master's
directory-relative position (nested docname + custom target, per `_directory_preserving_relpath`'s own
`D-05` docstring case).

**How to avoid:** the wrapper-generation code must compute its own relative-include-paths using the
WRAPPER's resolved physical location (`_resolve_output_stem(master_docname)` +
`_directory_preserving_relpath(master_docname, stem)`) as the "current" side of the relative-path
calculation, not the raw master docname — while content files, unaffected by target-name resolution
(D-02: non-masters always keep `docname` as their stem), keep using their docname-derived location as
the "target" side unchanged. This is precisely the fix B-1 already names in PROJECT.md's Target features
— call this pitfall out explicitly as the acceptance bar: a fixture with a NESTED master
(`typst_documents = [('guide/index', 'guide-manual.typ', ...)]`, so the wrapper's resolved path differs
in basename from `guide/index.typ` but stays in the SAME directory) must prove the wrapper's `#include()`
paths to its content children resolve correctly, i.e., are computed relative to `guide/guide-manual.typ`,
not `guide/index.typ`.

**Warning signs:** any new wrapper-path helper that calls `_compute_relative_include_path` with the raw
master docname as the "current" argument instead of the resolved wrapper path.

**Phase to address:** the phase implementing wrapper generation — this IS the B-1 fix; treat this
pitfall as B-1's own acceptance-criterion detail rather than a separate task.

---

### Pitfall 12: Process pitfalls this project has already paid for, twice, in the immediately preceding milestones

Drawn directly from `MILESTONES.md`'s own recorded lessons (not inferred):

**12a — the `phase.complete` auto-flip on release-prep phases (three-for-three in this project's
history).** Every one of the last three milestones (v0.6.3, v0.6.4/v0.6.5, v0.7.0, v0.7.1 — all
`override_closeout`) reports `init.manager` auto-flipping every phase to `phase_complete=true` /
`verification_status=passed` with no `MILESTONE-AUDIT.md` run, accepted each time by explicit owner
decision at close rather than by a machine-verified audit. This is not itself a defect, but it means
the RELEASE-PREP phase specifically (the final phase, following this milestone's own stated pattern —
"version bump + curated CHANGELOG entry in the final phase... publish executes at
`/gsd-complete-milestone`") is the one phase whose "complete" status has, four milestones running, never
been independently machine-verified before close. **Warning sign:** treating the final phase's
`phase_complete=true` as equivalent to "the release evidence has been generated," when historically it
has only ever meant "the code changes for that phase landed." **Prevention:** apply REL-04's own lesson
(12b, next) specifically to the release-prep phase — its completion claim must rest on generated
evidence (a real tag push, a real PyPI publish, a real RTD build measurement), not on the workflow files
being correct. **Phase to address:** the final release-prep phase, and `/gsd-complete-milestone` itself.

**12b — reporting a requirement complete on the strength of the code being correct, not on generated
evidence (the REL-04 lesson, paid twice: failed once in v0.7.0, closed correctly in v0.7.1).** v0.7.0's
own retrospective states the exact error: REL-04 was believed fixed because the workflow file was
correct, and the first real tag push then failed at `uv: command not found` — a defect only a REAL
exercise could surface. v0.7.1 explicitly avoided repeating this by measuring the published release
body byte-for-byte against `extract_changelog_section.py`'s output rather than trusting the workflow's
correctness. **For v0.8.0:** this generalizes past REL-04 specifically to EVERY claim in this milestone
that something "now produces a complete PDF for each master, no silently dropped content" — the
acceptance bar must be a REAL `sphinx-build -b typstpdf` run with a REAL multi-master `typst_documents`
config, its output PDFs opened via `pypdf`, and specific text/page assertions proving each master's full
content is present — not "the translator/builder code looks correct" or "one representative fixture
compiles." **Warning sign:** a phase or the milestone close reporting the goal met based on unit-level
fixture passes alone, without a full multi-master `sphinx-build → typst.compile() → pypdf` round trip
exercising the ACTUAL scenario named in the milestone goal (≥2 masters, ≥1 shared child, in one build).
**Phase to address:** every phase claiming a fix to B-1/B-2/defect A/CR-02, and explicitly the milestone
close.

**12c — not pushing the milestone branch until the release PR (milestone invariant #5, which "paid
immediately in v0.7.1").** v0.7.0's own closing note names this as the shared root cause of BOTH defects
that surfaced only at its release PR (the `create-release` `uv` failure and the Windows cp1252 test
failure) — "the milestone branch was never pushed until the release PR, so neither Windows CI nor a real
tag push touched it during any of the eight phases." v0.7.1 explicitly adopted pushing early as a
standing invariant. **For v0.8.0 specifically:** this milestone's own "Key context" already flags a
3-OS-CI-relevant risk class this research surfaces further (Pitfall 5's case-insensitivity hazard,
Pitfall 4's collision-guard gap) — these are exactly the kind of platform-dependent defect that stays
invisible on a Linux-only local dev loop and surfaces only when Windows/macOS CI actually runs. **Warning
sign:** the milestone branch existing only locally or on a fork by the time wrapper/content-split work
is substantially done. **Prevention:** push the milestone branch at (or very near) the first phase,
exactly as CLAUDE.md's own "Worktree-isolated execution" section already mandates worktree isolation as
the STANDING execution mode — the push-early discipline is the release-branch-level analogue of that
same "don't let unverified state accumulate before it's cheap to check" principle. **Phase to address:**
process, not a specific phase — applies from Phase 1 of this milestone onward.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|-----------------|-----------------|
| Reusing `_compute_master_included_docnames`'s LIFO-stack traversal for the new wrapper DFS (Pitfall 1) | Less new code to write | Silently reverses include order, mis-nests shared children with no compile error | Never — write the DFS fresh with an ordered `traversed` list |
| Leaving `master_included_docnames` in place "in case something else needs it" after the compile-time guard lands (Pitfall 6) | Avoids a deletion review pass | Two competing degrade decisions that can silently disagree | Never for this milestone; only if a genuinely new consumer is named explicitly |
| Regenerating GATE-01 expected strings from the new emitter's actual output (Pitfall 7) | Fast, always "passes" | Proves nothing; hides regressions the same test was supposed to catch | Never for structural assertions; only acceptable for the literal `@preview` import lines, which are pinned independently by the version-sync test |
| Treating CR-02 / image-path fixes as classic-RED GATE-01 fixtures without defining the non-fatal RED assertion first (Pitfall 8) | Skips an extra planning step | Fixture measures "code ran," not "defect is fixed" | Never — v0.7.0 already paid for learning this the hard way |
| Deferring the case-insensitive-filesystem collision fixture (Pitfall 5) to "whenever Windows/macOS CI runs" | Saves writing one fixture now | Discovered only on the 3-OS matrix, after the fact, per this project's own history | Acceptable only if a todo is filed AND the milestone branch is pushed immediately (12c) so CI catches it within days, not at the release PR |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|-------------------|
| Sphinx `env.toctree_includes` | Treating it as ordered/authoritative for "which parent owns this child" | It retains EVERY edge (verified: PROJECT.md's own `xmaster -> ['zmid', 'shared']` measurement); parent resolution requires replaying Sphinx's own `inline_all_toctrees`-style DFS order, not just reading the dict |
| Sphinx `apply_post_transforms` vs `get_and_resolve_doctree` | Assuming preserving toctree nodes (`get_doctree()` + manual `apply_post_transforms`) skips numref/xref resolution too | It does NOT skip it (verified by reading `sphinx/environment/__init__.py:759-776`) — `:numref:`/`:ref:` text is still baked in project-wide, creating Pitfall 2 |
| Typst `#include()` + `<label>` | Assuming label collisions only matter "within one file" | Confirmed via Typst's own issue tracker (typst/typst#2368): a label appearing once per file still collides once those files are `#include()`d into one document — exactly this milestone's live hazard |
| Typst `context` + `query(<label>)` | Assuming query() only sees content BEFORE the query call (single-pass mental model) | Confirmed: Typst's introspection (`context`/`query`) operates over the WHOLE compiled document regardless of source position — this is WHY the compile-time guard design works from any DFS position, not a caveat on it |
| `TypstBuilder`/`TypstPDFBuilder` dual `write_doc`/`finish` overrides | Fixing wrapper-generation logic in one builder's override and forgetting the other | Both `write_doc` bodies are near-duplicates today (confirmed, `builder.py:560-603` vs `:915-958`); place wrapper generation in the shared, non-overridden `write()` instead (Pitfall 9) |

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|-----------------|
| Every cross-reference now wrapped in its own `context { query(<label>) }` block (replacing one build-time boolean check with a per-reference compile-time query) | Typst compile time grows with reference count, since `query()`-driven `context` blocks force additional introspection passes (documented Typst behavior, not measured here) | Acceptable for typical doc sizes; if the full Sphinx `doc/` corpus gate (already used by this project's GATE-02 methodology) shows a material compile-time regression, consider batching/memoizing the query rather than assuming it's free | Large corpora with very high cross-reference density — worth a before/after compile-time measurement on the existing corpus gate, not just a correctness check |

## Security Mistakes

Not applicable in the usual sense (no network/auth surface changes in this milestone); the closest
analogue is path-traversal-shaped, already covered by Pitfall 4/11 (a malformed/adversarial
`typst_documents` target name escaping `outdir` — the exact class `_resolve_output_stem`'s existing
D-06/D-07 guards target, and the milestone's own `track-image-rehome-escapes-outdir-for-non-doctreedir-
abs-uri` defect is a second instance of the same escape class, just for images rather than `.typ`
targets).

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-------------------|
| Output-shape change is invisible until a user's existing `typst_documents` config produces a DIFFERENT set of files (wrapper name = old master name; content now under the bare docname) | A user with existing tooling/scripts expecting `manual.typ` to contain the FULL document (title page + body) instead finds it's now a thin wrapper, with the actual content in `index.typ` | Document explicitly in the CHANGELOG, alongside v0.7.1's own rename precedent (already flagged in PROJECT.md's "Key context") — name BOTH the old and new file's role explicitly, not just "output changed" |
| A user who customized `_template.typ` or template-adjacent tooling assuming ONE file per master | Confusion when two files now correspond to what was previously one | Same CHANGELOG treatment; consider a one-time build-time INFO log noting the new wrapper/content split when `typst_documents` is non-default, mirroring the existing warning-on-fallback conventions this codebase already uses pervasively |

## "Looks Done But Isn't" Checklist

- [ ] **Diamond fix**: Often "looks done" once ONE 2-master/1-shared-child fixture compiles — verify with
  a THIRD master and a SECOND shared child, plus a cycle/self-reference fixture (Pitfall 3), before
  calling the diamond class closed.
- [ ] **`master_included_docnames` removal**: Often "looks done" once the primary `translator.py:3073`
  site is migrated — verify with `grep -rn master_included_docnames typsphinx/` returning nothing, and
  the `:4291` site (unread in this pass) explicitly inspected (Pitfall 6).
- [ ] **CR-02 duplicate-target detection**: Often "looks done" once two DIFFERENT masters targeting the
  same name are caught — verify a master targeting ITS OWN docname is also covered (Pitfall 4), and that
  the check is case-normalized (Pitfall 5).
- [ ] **Wrapper relative-include paths**: Often "looks done" once a ROOT-level master (docname == target
  stem, same directory) compiles — verify with a NESTED master whose target name differs from its
  docname (Pitfall 11), the exact B-1 shape.
- [ ] **GATE-01 fixtures for CR-02 / image defects**: Often "looks done" once the fixture compiles green
  post-fix — verify a RED assertion was recorded pre-fix that is NOT just "does not compile" (Pitfall 8),
  since these are non-fatal-but-wrong defects today.
- [ ] **`:numref:` correctness claim**: Often assumed "fine, no code touches it" — verify with an actual
  two-master, divergent-DFS-position fixture and `pypdf` number comparison (Pitfall 2) before claiming
  cross-reference correctness end to end.

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|----------------|------------------|
| Wrapper DFS order wrong (Pitfall 1) | MEDIUM | Isolated to the new wrapper-generation method; rewrite the traversal against a fresh `inline_all_toctrees`-style fixture, no downstream translator changes needed since it only affects offset/include-order, not label namespacing |
| CR-01 self-collision landmine ships (Pitfall 4) | LOW–MEDIUM | Caught by a single fixture once written; fix is localized to `_resolve_output_stem`'s guard clause, no data migration needed since nothing has shipped to PyPI yet mid-milestone |
| `:numref:` divergence discovered late (Pitfall 2) | LOW if documented as a known limitation; MEDIUM if a code fix is chosen | Cheapest recovery is a CHANGELOG/README caveat, not a code fix, given this is a genuinely hard problem (Sphinx's project-wide numbering vs. Typst's per-compile numbering) |
| GATE-01 fixture laundered (Pitfall 7) | HIGH if discovered post-release | Requires re-deriving expected values independently for every affected fixture — exactly the work the shortcut was meant to avoid, now done under pressure instead of during planning |

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|-------------------|----------------|
| 1 — DFS order must replicate Sphinx's resolution | Wrapper-generation phase | Reordered-entries mirror fixture proves order-dependence, not a hardcoded rule |
| 2 — `:numref:` project-wide vs per-master numbering | Wrapper-generation phase (surfaces it) | Two-master fixture with `pypdf` number comparison; documented or fixed explicitly |
| 3 — diamond variants (cycles, self-ref, orphan, glob, `.. only::`) | Wrapper-generation phase | One fixture per shape with an explicit decided outcome |
| 4 — CR-01 self-collision exemption | CR-02 phase | Fixture: `typst_documents` target stem == its own docname |
| 5 — case-insensitive-FS collision gap | CR-02 phase (+ CI confirmation) | Case-varied collision fixture; guard made case-normalized |
| 6 — orphaned `master_included_docnames` | Compile-time guard phase | `grep` returns empty; `:4291` site inspected |
| 7 — laundered GATE-01 via regenerated strings | Every test-migration phase | PR review requires each expected string traced to a written-first rationale |
| 8 — non-fatal defects need a defined RED | CR-02 + image-defect phases | Explicit pre-fix RED assertion recorded, not just "does not compile" |
| 9 — wrapper-write placement across builder overrides | Wrapper-generation phase | `-b typst` vs `-b typstpdf` wrapper-output parity test |
| 10 — parallel/incremental-build state safety | Wrapper-generation phase (placement only) | Confirm wrapper state computed up front, not inside `write_doc` |
| 11 — wrapper include-paths must use resolved location, not raw docname | Wrapper-generation phase (this IS B-1) | Nested-master-with-custom-target fixture |
| 12a/b/c — process lessons (auto-flip, generated evidence, push early) | Release-prep phase + milestone-wide | Real multi-master `sphinx-build → pypdf` evidence; milestone branch pushed from Phase 1 |

## Sources

- `typsphinx/builder.py` (read in full, this session) — `_resolve_output_stem`, `_directory_preserving_
  relpath`, `_compute_master_included_docnames`, `write()`, `write_doc()` (both builders), `finish()`
  (both builders), `_track_image()`.
- `typsphinx/translator.py` — `_namespace_label`, `_resolve_xref_docname`, `visit_toctree`/
  `depart_toctree`, `_compute_relative_include_path`, `_reference_anchor_decision`, `visit_citation`
  backref loop, `visit_footnote`/`visit_footnote_reference`, `visit_index` (read directly, this
  session).
- `typsphinx/writer.py` — `_is_master_document`, `translate()`'s master/included branch (read directly,
  this session).
- `.planning/PROJECT.md` — v0.8.0 "Current Milestone" section (Target features, Key context) and the
  retained v0.7.0/v0.7.1 milestone briefs (read directly, this session; the measured 2026-08-11 premises
  and the "prefer the deeper path... comes from upstream" note are load-bearing for Pitfall 1).
- `.planning/MILESTONES.md` (read in full, this session) — v0.7.0's REL-04/Windows-cp1252 closing
  lesson, v0.7.1's REL-04-closed-on-generated-evidence account, and the `override_closeout` pattern
  across v0.6.2–v0.7.1, all cited directly in Pitfall 12.
- Sphinx source, read directly from the installed venv:
  `.venv/lib/python3.13/site-packages/sphinx/util/nodes.py:485` (`inline_all_toctrees`) and
  `.venv/lib/python3.13/site-packages/sphinx/environment/__init__.py:668-776`
  (`get_and_resolve_doctree`/`apply_post_transforms`).
- [Label `<B>` occurs multiple times in the document when including #outline — Typst Forum](https://forum.typst.app/t/label-b-occurs-multiple-times-in-the-document-when-including-outline/7531)
  and [typst/typst#2368 — "label occurs multiple times" after linking to a label from another file](https://github.com/typst/typst/issues/2368) — confirm the cross-file-include duplicate-label
  hazard is a known, general Typst behavior, not typsphinx-specific.
- [Typst Counter documentation](https://typst.app/docs/reference/introspection/counter/) and
  [i-figured package](https://typst.app/universe/package/i-figured/) — confirm figure/heading counters
  are global to one compiled document and not automatically per-section/per-file, informing Pitfall 2.
- [Typst Context documentation](https://typst.app/docs/reference/context/), [Typst Query
  documentation](https://typst.app/docs/reference/introspection/query/), and [Typst Labels — Examples
  Book](https://sitandr.github.io/typst-examples-book/book/snippets/labels.html) — confirm the
  `context { query(<label>).len() != 0 }` existence-guard idiom is a documented, whole-document
  introspection mechanism (not position-dependent), grounding this milestone's compile-time
  cross-reference degradation design as sound.
- Sphinx toctree documentation (glob expansion, `:orphan:` exclusion) — general web search confirmation
  used only to corroborate `builder.py`'s own docstring claims about `env.toctree_includes`, not as a
  primary source.

---
*Pitfalls research for: typsphinx v0.8.0 multi-master composition*
*Researched: 2026-08-11*
