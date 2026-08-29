# Milestones: typsphinx

## v0.9.1 Windows path correctness (Completed: 2026-08-30 — **NOT published**)

**Delivered:** three latent Windows path defect families closed on the product side, behind gates
that were RED against the unfixed tree first — and then the release was deliberately cancelled for
an unrelated, pre-existing blocker. This is the first milestone in this project's history that ships
nothing: no tag (local or remote), no PyPI upload and no GitHub Release.
`pyproject.toml` stays at `0.9.0`; the next published release is **0.9.2** (D-02). The work was
merged to `main` after the close via a merge-only PR (see **Git** below) so 0.9.2 can carry it.

**Closeout:** override_closeout — but for the first time in seven closes, on a **real
`v0.9.1-MILESTONE-AUDIT.md`** rather than in the absence of one. The audit reports requirements
10/11, phases 4/4, integration 11/11, flows 1/1, `status: tech_debt`, `fail_gate.triggered: false`.
Known verification overrides: 16 newly acknowledged, 0 carried forward from a prior close (see
STATE.md Deferred Items) — 9 pending todos, 3 dormant seeds, 1 human-needed verification gap from
the archived Phase 22.3, and 3 archived deferred-item entries whose heading-delimited shape the
acknowledge writer refuses, marked by direct file edit instead.
**Phases:** 4 (58–61) · **Plans:** 17 · **Tasks:** 48
**Requirements:** 10/11 v1 requirements complete · **Timeline:** 2026-08-27 → 2026-08-30 (4 days)
**Git:** milestone branch `gsd/v0.9.1-windows-path-correctness` (163 commits) merged to `main` as
`9db2274c` via **PR #135** on 2026-08-29T22:31Z, at owner instruction after the close had already
been taken. The PR was **merge-only** — `61-HANDOFF.md`'s D-12 had ruled out a PR for this
milestone, and the owner overrode that; the no-release half of D-02 was not overridden and still
holds. 15/15 checks green on the PR head, both `windows-latest` lanes and `Lint and Format Check`
included; branch deleted on merge. **Still untagged** — the tag belongs to 0.9.2's release-prep
phase. This is the first v0.x milestone branch to be merged and deleted rather than left standing
alongside v0.7.0–v0.9.0's.
**Code delta (milestone scope, excl. `.planning/`):** 23 files, +3,011 / −72 lines. One new runtime
module (`typsphinx/pathfmt.py`, a zero-import stdlib leaf) and one new test helper
(`tests/_path_naming.py`); everything else is `builder.py`/`translator.py`/`writer.py`/
`template_registry.py` diagnostics and the gate corpus. **Zero runtime dependencies added and no new
`typst_*` config value** — a bug-fix round by construction.

**Key accomplishments:**

- **A message site can move off `!r` without a single test edit** (MSG-01, Phase 58) — the two tests
  that hard-coded `repr()`'s output format as their pass criterion now assert the *meaning* through
  a shared `path_named_in()` predicate, each rewrite proven neither regression nor tautology by a
  real, recorded RED against a temporarily-edited `builder.py`. A self-excluding AST sweep over
  `tests/` brought the whole-tree `repr()`/`!r` pass-criterion census to exactly 7 with **zero
  path-valued sites left** — and `58-REPR-CENSUS.md` then became the instrument Phases 59 and 60
  each used to *measure* their zero-test-edit claims instead of asserting them. Ships no product
  change.

- **A Windows-shaped absolute image URI survives the whole pipeline into a real PDF** (PATH-01,
  IMG-04..IMG-07, Phase 59) — `_escapes_outdir()` decides on the backslash-normalized string,
  proven to change nothing live by a two-tree byte-identity measurement at both production call
  sites; `_build_relocation_key()` normalizes only the basename while still hashing the **raw** URI
  for the collision anchor; `_bound_relocation_component()` bounds the component to 255 UTF-8 bytes
  on character boundaries with the `{sha1[:8]}-` prefix kept whole; and `visit_image()` binds
  `escape_typst_string()` once and interpolates it at **both** emission sites. The acceptance gate
  is a real `typst.compile()` driven through `-b typstpdf`, with an all-lane string-shape sibling
  for `windows-latest`, where the compile gate itself cannot run.

- **One delimiter-aware path-quoting helper, routed everywhere** (MSG-02..MSG-05, Phase 60) —
  `typsphinx/pathfmt.py::quote_path()` reproduces `repr()`'s delimiter-selection rule minus the
  backslash doubling that made a Windows path unmatchable, in a zero-import leaf module gated by a
  27-test RED-first suite. All 23 path-valued interpolations in `builder.py` route through it
  (**including two `target` sites the original enumeration missed**), 3 in `writer.py`, and 2 in
  `template_registry.py` — the latter closing a leaked `PosixPath(...)` wrapper defect as well. The
  adjacent type-check message stays measurably on `repr()` as a deliberate exclusion: its value is
  reached only when it is *not* path-shaped.

- **A locked decision was falsified by measurement and amended rather than read to fit** (Phase 59,
  D-01a) — `59-CONTEXT.md` D-01 and ROADMAP SC#2 both predicted the unfixed tree would be refused
  with `path must not contain a backslash`; it is actually `unclosed delimiter`, because the unfixed
  pipeline emits a raw backslash **and** a raw unescaped `"` at once and the quote ends the string
  before the semantic check runs. D-01's four probe runs had each carried only one defect.
  Re-measured independently, put to the owner, closed with an `AMENDED` block. The substantive claim
  survived intact: only the tree with *both* halves fixed compiles.

- **Two defects were found by gates after every plan in their phase reported complete** — Phase 59's
  own code review found a blocker in `_bound_relocation_component()` (one reserved *byte* empties a
  multi-byte leading character, violating the "never an empty basename" property), fixed in-phase
  with two regression gates proven RED against the pre-fix tree first; and Phase 60's repo-wide
  discovery grep found a **fourth** module carrying the same hardcoded-delimiter shape
  (`translator.py`'s relative-path DEBUG logs) and **filed it as a todo rather than fixing it**,
  outside the requirement scope.

- **The prep-only fence held, and it has slipped at five consecutive prior release-prep closes**
  (Phase 61) — REL-09's checkbox was guarded by a SHA-256 of `.planning/REQUIREMENTS.md` recorded at
  phase head, re-verified at phase close, again inside `61-HANDOFF.md`, and once more by the
  operator at this close: MATCH every time, with `git tag -l 'v0.9.1'` empty at each observation.
  SC#4's proof rests on two observations 38m16s apart spanning two waves and a full 3-OS CI
  dispatch, each network probe carrying a real positive control, with the empty `typsphinx/` diff
  proven non-vacuous by a live widened control.

### Known Gaps

- **REL-09 — v0.9.1 released to PyPI** (Phase 61): **deliberately unmet, and the correct outcome.**
  Owner decisions D-01/D-02/D-08 amended this milestone's definition of done to exclude publication
  entirely. The requirement carries forward to v0.9.2 with its literal wording unchanged, including
  its `v0.9.1` version string — the owner declined both rewriting it and closing it as superseded.
  A checked box would have been the defect. The milestone audit classifies it `deferred`, not
  `unsatisfied`, and `fail_gate` did not trigger.

### Why the release was cancelled

An owner report on 2026-08-29, mid-milestone, surfaced a `severity: blocker` defect: an image node
that is not the first thing in its paragraph is emitted directly adjacent to the preceding code-mode
expression, so Typst refuses the file with `expected semicolon or line break` and `-b typstpdf` does
not degrade — it raises `ExtensionError` and writes **no PDF for any master document in the
project**. Measured **pre-existing, not a regression** (D-06):
`git diff v0.9.0..HEAD -- typsphinx/translator.py` is 25 lines, all IMG-05's
`escape_typst_string()` call, and `visit_image()`'s missing leading separator is byte-identical to
the `v0.9.0` tag. Publishing a release that cannot compile a document containing an inline
substitution image was declined. The blocker was **not fixed here** (D-07 — `translator.py` was
outside both Phase 61's fence and the milestone's requirement set) and **not disclosed on any public
surface** (D-05): no `README.md` Known Limitations entry, no CHANGELOG `### Known Limitations`
section, no GitHub issue — the fourth consecutive cycle at which such a section was declined. It is
tracked as `.planning/todos/pending/2026-08-29-inline-image-in-paragraph-emits-unseparated-expression.md`
and is v0.9.2's first requirement.

**Verification:** all 4 phases `phase_complete=true` / `verification_status=passed` (58: 5/5, 59:
5/5, 60: 5/5, 61: 9/9 must-haves; 0 gaps and 0 human-verification items across all four). Local at
the milestone-final tree: 1513 passed / 5 skipped, `black` and `mypy` clean, version-sync guard
family green. CI acceptance run `33260111745`: **12/12 `success`, both `windows-latest` lanes
included.** `ruff` authority is CI's, not this host's — Phase 59's CI run 1 failed on `ruff` alone
while all six matrix test jobs passed, because `ruff` is unrunnable in the freshly-`uv sync`ed
worktrees every executor runs in.

---

## v0.9.0 per-document templates (Shipped: 2026-08-22)

**Closeout:** override_closeout — no `v0.9.0-MILESTONE-AUDIT.md` was run (owner decision at close:
`init.manager` reported all 6 phases `phase_complete=true` / `verification_status=passed`, and every
v1 requirement except the publish-gated REL-08 was already `Complete` before the close began).
**Sixth consecutive close taken this way** — the pattern has outlived being a default and deserves
an explicit decision about whether the audit step still earns its place here. 13 open artifacts
acknowledged as deferred (see STATE.md Deferred Items) — 10 pending todos, **every one of them
already dispositioned with a reason** in `57-HANDOFF.md` § "Deferrals carried forward", plus 3
dormant seeds never scoped into this milestone.
**Phases:** 6 (53–57, plus 54.1 inserted) · **Plans:** 42 · **Tasks:** 112
**Requirements:** 26/26 v1 requirements complete · **Known gaps:** none
**Timeline:** 2026-08-15 → 2026-08-22 (8 days)
**Git:** milestone branch `gsd/v0.9.0-per-document-templates` (339 commits) merged to `main` via
PR #134 with **all 15 checks green** — a fresh full matrix dispatched on the exact PR head, both
`windows-latest` lanes included, plus the advisory link check which passed this time — and tagged
`v0.9.0` on the merge commit `68b92e24`. Every commit between the phase's last authority CI run
(`32557477023`) and the PR head was measured `.planning/`-only before opening the PR.
**Code delta (milestone scope, excl. `.planning/`):** 166 files, +11,627 / −1,620 lines. The runtime
change is concentrated in two new modules — `typsphinx/template_registry.py` (the resolver and its
whole validation pass) and `typsphinx/removed_config.py` (this codebase's first Sphinx
event-handler connection) — plus `typsphinx/builder.py`, where `_copy_used_template_bundles()` and
the pre-write validators replaced **five deleted methods**; the rest is the test corpus and the
documentation rewrite.
**Released 2026-08-22:** PyPI `typsphinx 0.9.0` (wheel 187,400 B + sdist 809,731 B) published by
release run `32560457509` after owner approval of the `pypi` environment. All jobs `success`,
**`create-release` included** — the job that failed at the v0.7.0 close, and therefore observed
directly rather than assumed, as `57-HANDOFF.md` item 3 required. GitHub Release `v0.9.0` carries
all three assets (`.whl`, `.tar.gz`, and the tag-time `typsphinx.pdf`, 2,754,479 B, attached by
`docs.yml`); its first **123** lines are **byte-identical** to
`scripts/extract_changelog_section.py 0.9.0`'s stdout (`diff` clean), with **0** commit-dump-shaped
lines in that window — the remainder is the `## Installation` block plus GitHub's own auto-generated
"What's Changed". The standing second tag was pushed on `typsphinx-doc-translations`: for the second
consecutive close the pin was advanced by dispatching that repository's own `update-pin.yml`
(run `32566262655`) rather than by a hand-made clone-edit-push, moving its `typsphinx` submodule pin
to the v0.9.0 merge commit `68b92e24` and resyncing the ja catalogs as `f9390d4b`; the annotated tag
`v0.9.0` was then created there on that commit.
**Read the Docs measured live 2026-08-22:** `en` `stable` resolves from the root
(`https://typsphinx.readthedocs.io/` → `/en/stable/`, 302), reports `0.9.0`, and serves its PDF
(2,760,619 B, `application/pdf`); `ja` (slug `typsphinx-ja`) `stable` advanced to `ref: v0.9.0` once
the translations repository's own tag landed, reports `0.9.0`, and serves its PDF (2,963,030 B).
Both projects' Default Versions have been `stable` since the v0.6.4 close and needed no re-flip —
the sixth consecutive close at which none was required.

**REL-08 closed on the publish, not on the prep.** Phase 57 was prep-only by design and held REL-08
at `[ ]` through all **eleven** of its plans, guarding it with a SHA-256 of `REQUIREMENTS.md`
recorded at phase head (`503efc7a…`) and **three separated tag/release probes** (2026-08-16T15:35Z,
2026-08-22T06:51Z, 2026-08-22T07:04Z), all empty. The digest still matched at the close,
immediately before this flip. The `phase.complete` auto-flip fired anyway during Phase 57's own
close-out and was caught and reverted there: **five-for-five on release-prep phases now.**

**Delivered:** every `typst_documents` entry can choose its own template, Typst Universe package,
and template-function arguments through the validated `typst_document_templates` registry, instead
of one globally-configured template being applied to every master. The slot that carries the choice
already existed — `typst_documents` element [4], populated by the builder's own default and set by
this project's own `conf.py`, and documented as "accepted and ignored" — so the milestone is a
promotion of a live placeholder rather than a tuple extension, which is exactly why a `conf.py` that
declares nothing new keeps producing the same PDF.

**Key accomplishments:**

- **The registry, and additivity proven rather than asserted** (TPL-01, TPL-03..05, CONF-14..18) —
  `typsphinx/template_registry.py` resolves the registry once per build; each key carries `template`
  **xor** `package` plus an optional `template_function`; validation is a fixed-order seven-case key
  denylist, the reserved-key check, the xor, a path-arithmetic bundle-escape guard and a per-key
  existence check, all **accumulated into one `ExtensionError`** rather than aborting on the first
  fault, with every raw-exception crash path (cross-drive path, non-`str` key, list-for-dict,
  list/bytes `template`) closed in follow-up plans. The first plan of the milestone captured SHA-256
  hashes and PDF page counts across all four existing configuration shapes from real `-b typstpdf`
  runs **before any code changed**, so "the built-in `"typst"` key produces byte-identical output"
  became a diff against a stored artifact instead of a claim.

- **One bundle rule replaced four mechanisms** (TPL-02, CONF-19, OUT-04..07, BLD-05, BLD-06) — every
  used key's resolved bundle directory is copied **wholesale** to `<outdir>/_template/<key>/`, the
  synthesized built-in key under the same rule with no exception (which closed a previously-unnamed
  whole-source-tree-copy hole), and wrappers import by a root-absolute path independent of their own
  nesting depth, so template-relative asset references resolve for the first time. Five `builder.py`
  methods and an 8-test module were **deleted** rather than extended, and `typst_template_assets`
  was deregistered in the same commit that connected `typsphinx/removed_config.py` — so a `conf.py`
  still setting any of three removed values gets a warning naming the value, its replacement, and
  the observable consequence instead of silently different output.

- **The safety defects that rule created were closed in an inserted phase, not deferred** (WR-01,
  CR-01) — a bundle directory colliding with Sphinx's own `templates_path` now refuses the build
  **before any `.typ` file is written**, closing a hole that would have republished a project's
  Jinja template directory into public build output while the published docs recommended that exact
  layout; and a bundle-escape violation on the built-in key is caught pre-write instead of at
  `finish()`. Two different failure kinds in one build raise once, with a byte-identical,
  declaration-order-independent message.

- **The five v0.8.0-derived defects closed on the product side** (XREF-05, BLD-07..09, IMG-03) —
  each with a RED-recorded reproduction whose ancestry was checked against git history rather than
  taken from prose. `_sanitize_label` was made injective and **proven general by an exhaustive
  decoder round-trip over 66,430 adversarial strings**, not by fixture pass; include-edge keys escape
  their own separators; the chain walk is bounded at 500 frames with a named `ExtensionError`; and
  the image absolute-URI gate moved onto a backslash-normalized predicate with a SHA-1-prefixed
  relocation key.

- **The documentation describes what shipped, bound to code by import and by AST** (DOC-15..17) — a
  two-way AST-pinned error catalogue (AST-based because one raise site uses a shared helper and
  another implicit string concatenation), a seven-case key-naming table bound by import rather than
  transcription, a Removed Configuration Values section, and the stale single-root `_template.typ`
  story rewritten with both published file counts corrected **in the same commit as the test that
  pins them**. The hand-compile `--root` note ships **conditionally** on the target's own path shape,
  both branches proven by a real `typst.compile()` gate — after the CONTEXT-time claim was
  reproduced twice and found false.

- **The release was prepped without taking any irreversible action, and the fence is provable**
  (REL-08 prep half) — version lockstep across `pyproject.toml`/`uv.lock`/`README.md`, a curated
  `## [0.9.0]` section with four `**Breaking` marks and a rolled-over tail link block, a
  `Migrating from 0.8.x to 0.9.0` guide written from a real build at the `v0.8.0` tag in a separately
  provisioned worktree, and green proven across three surfaces (CI 12/12 including both Windows
  lanes; a local 1425-passed suite with `black`/`ruff`/`mypy` clean and a built-wheel content check;
  the multi-template PDF gate at 6 passed / 0 skips, closed against SC#3's "differently typeset"
  wording by a `pypdf` page-geometry read-back showing A4 versus US Letter).

### Known limitations shipped

Three, all deferred by owner decision and recorded **only** in `57-HANDOFF.md` § "Deferrals carried
forward" and `.planning/todos/pending/` — the **third consecutive release** to decline a
`### Known Limitations` CHANGELOG section:

- **WR-02** — `_validate_used_template_paths()` resolves Sphinx's `templates_path` against `srcdir`
  rather than `confdir`, so a project using `-c`/`--confdir` is not covered by the new refusal and
  keeps the republication hole. Shipped **silent** (D-09). This one is weaker than the two
  precedents it cites: the reviewer's own recommended minimum was exactly the CHANGELOG carve-out
  that was declined, and the shipped sentence ("template layout is now validated before anything is
  written") therefore reads as unconditional — an over-broad true-sounding claim rather than a true
  claim with a missing footnote.

- **54.1 WR-01** — the "Custom template not found" warning fires three times instead of two for one
  narrow shape (a synthesized `"typst"` key whose `typst_template` names a nonexistent path).

- **57 WR-01** — the pre-write refusal messages quote path values with a fixed `'...'` delimiter, so
  a path containing a literal single quote closes the quote early. Filed forward into the existing
  `2026-08-17-repr-escaped-paths-in-remaining-user-facing-messages.md` rather than as a new record;
  a single delimiter-aware quoting helper resolves both halves.

### The milestone's carrying story

**A defect diagnosed wrong twice, at a cost of two full CI matrices.** One `windows-latest`
assertion was read as a path **separator** problem in two successive fix attempts. It was an
**escaping** problem: three pre-write refusal messages interpolated PATH values with `!r`, and
`repr()` doubles every backslash, so no `str(Path(...))` assertion could ever match. Plan `57-05`
**halted** rather than claiming its authority gate on a red matrix; `57-11` fixed the product side,
knowingly breaking the prep-only fence once by explicit owner decision recorded as a dated `AMENDED`
block **naming SC#4, plan `57-08` and the phase verifier as its readers** — so the downstream fence
checks read the amended rule instead of reporting a false violation. Fresh authority run
`32557477023` then returned 12/12 including both Windows lanes, and `57-05`'s halt was retired under
a dated ADDENDUM that keeps its contemporaneous failure record verbatim: **retired on new evidence,
not retracted as a mistake.**

**A measurement this milestone made falsified itself within a week.** On 2026-08-16 the project
measured that `ruff` runs on this machine and wrote that into a CONTEXT amendment; on 2026-08-22 the
ELF-exec failure reproduced live in a freshly-provisioned worktree venv. The main checkout's `.venv`
holds an old runnable binary (27,906,360 B) while a venv created today pulls a newer generic-linux
wheel (27,900,480 B) that NixOS cannot exec — so **measuring `ruff` on the main tree can never
detect the hazard**, and the owner's refusal to close that todo on the 2026-08-16 evidence is what
preserved the record.

---

## v0.8.0 multi-master composition (Shipped: 2026-08-15)

**Closeout:** override_closeout — no `v0.8.0-MILESTONE-AUDIT.md` was run (owner decision at close:
`init.manager` reported all 6 phases `phase_complete=true` / `verification_status=passed`, and every
v1 requirement except the publish-gated REL-07 was already `Complete` before the close began).
12 open artifacts acknowledged as deferred (see STATE.md Deferred Items) — 10 pending todos, of
which 5 were already enumerated with reasons in `52-HANDOFF.md` § "Deferred by decision, not
oversight" and 4 more in its § "The remaining reviewed-but-not-folded todos", plus 2 dormant seeds
never scoped into this milestone.
**Phases:** 6 (47–52, no insertions) · **Plans:** 45 · **Tasks:** 121
**Requirements:** 24/24 v1 requirements complete · **Known gaps:** none
**Timeline:** 2026-08-11 → 2026-08-15 (5 days)
**Git:** milestone branch `gsd/v0.8.0-multi-master-composition` (359 commits) merged to `main` via
PR #133 with all 13 real CI checks green; tagged `v0.8.0` on the merge commit `78e01e5`. The only
red check was the advisory repo-wide link check, whose single 404 was `README.md`'s forward link to
the `output_layout` page Phase 51 had just created and which did not exist on RTD until this merge
built it — re-measured 200 on both `/en/latest/` and `/en/stable/` after the close.
**Code delta (milestone scope, excl. `.planning/`):** 344 files, +15,367 / −2,477 lines. The runtime
change is concentrated in `typsphinx/builder.py` (the per-master include-graph computation, the
four-kind pre-write collision validator, target-as-path resolution, and the two image relocation
guards), `typsphinx/writer.py` (the content/wrapper emission split), and `typsphinx/translator.py`
(state-guarded include emission and the shared compile-time label-existence guard); the great
majority of the file count is the test corpus, where **roughly 70 fixture projects and 17 test
modules per migration wave** had to move from the one-file-per-docname shape to the two-layer shape.
**Released 2026-08-15:** PyPI `typsphinx 0.8.0` (wheel 154,895 B + sdist 707,468 B) published by
release run `31861043480` after owner approval of the `pypi` environment. GitHub Release
`Release v0.8.0` carries all three assets (`.whl`, `.tar.gz`, and the tag-time `typsphinx.pdf`,
2,608,537 B); its first 70 lines are **byte-identical** to
`scripts/extract_changelog_section.py 0.8.0`'s stdout (`diff` clean), with **0** commit-dump-shaped
lines — the remainder is GitHub's own auto-generated "What's Changed" PR list. The standing second
tag was pushed on `typsphinx-doc-translations`: rather than advancing the pin by hand, that
repository's own `update-pin.yml` was dispatched (run `31861094950`), advancing its `typsphinx`
submodule pin `a97fe73` → `78e01e5` and resyncing the ja catalogs as `588b96d` — which created
`locale/ja/LC_MESSAGES/user_guide/output_layout.po`, independently confirming Phase 51's new page
reached the translation source; the annotated tag `v0.8.0` was then created there on `588b96d`.
**Read the Docs `stable` measured live 2026-08-15 (both projects):** `en` `stable` identifier
`78e01e53` (the v0.8.0 merge commit), `ja` (slug `typsphinx-ja`) `stable` identifier `588b96da` (the
translations repo's own v0.8.0 tag); both `active`/`built`, both pages report `0.8.0`, both PDFs
served (`en` 2,614,698 B / `ja` 2,816,255 B, `application/pdf`). No owner setting flips needed —
the fifth consecutive close at which none was required.

**REL-07 closed on the publish, not on the prep.** Phase 52 was prep-only by design and held REL-07
at `[ ]` through all nine of its plans, recording a checksum of `REQUIREMENTS.md` in
`52-HANDOFF.md`'s closeout guard so a later diff would have something to compare against. That
checksum (`566859ea…`) still matched at the close, immediately before this flip — the file was
untouched by the entire phase. The `phase.complete` auto-flip fired anyway during Phase 52's own
close-out and was caught and reverted there: **four-for-four on release-prep phases now.**

**Delivered:** a `typst_documents` configuration declaring more than one master now produces a
complete PDF for each of them. The unit of composition moved from "one `.typ` shared by every
master, with the include decision baked in at write time" to "per-master wrapper files that publish
their include edge set as Typst `state`, plus template-less docname-named content files that emit
state-guarded includes at the toctree's own position" — one re-shaping that cut the root all three
known multi-master defects grew from.

**Key accomplishments:**

- **The output split into two layers** (COMP-01..04, OUT-03) — every docname now gets a
  template-less content file and every `typst_documents` entry gets a thin wrapper at the path the
  user actually wrote. This closed **B-1** (a master that is also another master's toctree child
  aborting with `file not found`) and **B-2** (an included master re-expanding its template's title
  page and `#outline()` mid-body) by construction rather than by special-casing. The cost landed in
  the test corpus: five migration waves, each moving ~17 test modules and ~16–19 fixture projects,
  with every self-colliding fixture target de-collided along the way.

- **Each master computes and publishes its own include graph** (COMP-05..12) — mirroring
  `inline_all_toctrees`'s document-order depth-first traversal, published as Typst `state` and read
  by a static per-emission-site guard. A document reached from several masters renders once in each
  master's PDF, at that master's own traversal position, with its heading level varying
  independently per master; the diamond case and two masters requiring conflicting include sets from
  one content file both resolve correctly instead of one silently winning. Verified end to end by a
  real multi-master PDF build and a page-level completeness gate over a three-master fixture.

- **Cross-reference existence moved to compile time** (XREF-03, XREF-04) — a reference whose target
  label is absent from the compiling master degrades to plain text via a shared
  `context { … query(<label>) … }` helper instead of aborting the compile, with the build-time
  all-masters union deleted in the same change and every emission site (including `visit_citation`'s
  back-reference loop and `visit_pending_xref`) routed through one guard. **Deliberately landed
  ahead of the include graph**, which is what makes such a reference reachable-and-absent rather
  than merely absent. Measured effect: the rebuilt documentation PDF's dead-link population dropped
  from 40 URI actions over 20 targets to exactly the 5 pre-declared Sphinx-generated pages.

- **The two PR #131 follow-on image defects closed** (IMG-01, IMG-02) — a converted image rehomed to
  `images/<basename>` no longer collides with a real source image of the same name, and an absolute
  image URI outside `doctreedir` no longer writes outside the output directory; both routed through
  a new `_typst_converted/` reserved namespace, with every assertion byte-unchanged from its
  pre-fix RED version.

- **The published documentation gained an output-layout page** (DOC-14) — which file to compile,
  what a content file compiled standalone does (its own body only, state-guarded children absent,
  no error or warning), what target-as-path means, both `typst_documents` target-failure modes, and
  a "Migrating from 0.7.x to 0.8.0" guide naming the concrete before/after emitted-file set for each
  of the three breaking changes. A sweep-completeness audit run from a later wave than the fixes it
  audits found 2 residual false claims outside the fixing plan's own scope.

- **Milestone invariant #5 paid four times over.** Pushing the branch and dispatching CI mid-phase
  surfaced four real, pre-existing defects local execution structurally could not see; Phase 52's CI
  history is three runs, not one — RED (8 of 12 jobs) → 11/12 → GREEN 12/12. Two are worth carrying:
  a test comparing against **hardcoded Japanese Sphinx warning text** (baselines captured on a
  Japanese-locale machine; reproduces locally in 4 seconds under `LC_ALL=C`, which no one had ever
  run), and an `I001` unsorted import block that survived because **`ruff` has been unrunnable on
  this machine since Phase 45.2**. All four were fixed **test-side**, so the prep-only fence held
  with `typsphinx/` untouched — and the product-side inconsistency the fourth exposed
  (`builder.py:910`'s bare `path.isabs()` against its sibling's deliberate
  `posixpath.isabs(…) or _is_drive_qualified(…)`) was filed as a todo rather than erased by the
  test fix.

**Known limitations shipping in v0.8.0** (D-01/D-03 — internal disclosure only: no
`### Known Limitations` CHANGELOG section, no GitHub issue, no ROADMAP backlog item; the complete
record is `52-HANDOFF.md` plus `.planning/todos/pending/`). All four are `severity: minor` and,
unlike v0.7.1's D-27 pair, all four are **new failure classes created by features this milestone
shipped** — the distinction the owner had on the table when deciding:

- Label-collision false negative in the compile-time xref guard — two docnames sanitizing to the
  same label string (`a/b` and `a_u2f_b`) let a reference to the absent one link to the decoy.

- `make_include_edge_key` does not escape its own `#`/`>` separators, so two edges can collide.
- `_derive_master_edge_keys` recurses unbounded; an include chain deeper than Python's 1000-frame
  limit raises a raw `RecursionError` rather than a named `ExtensionError`.

- The image escape branch keys on basename while the collision branch keys on the full relative
  URI, so two escaping images sharing a basename collide onto one key.

Plus one carried outside that set: `_track_image()` gates on OS-native `path.isabs()`, so a
driveless-absolute image URI is not rehomed under Python 3.13 on Windows.

---

## v0.7.1 bug-fix round (Shipped: 2026-08-11)

**Closeout:** override_closeout — no `v0.7.1-MILESTONE-AUDIT.md` was run (owner decision at close:
`init.manager` reported all 8 phases `phase_complete=true` / `verification_status=passed`, and every
v1 requirement except the two publish-gated REL rows was already `Complete` before the close began).
12 open artifacts acknowledged as deferred (see STATE.md Deferred Items) — all 9 pending todos were
already enumerated in `46-HANDOFF.md` § "Deferred by decision, not oversight", 2 dormant seeds were
never scoped into this milestone, and the 5 "deferred items" carried from Phase 45.1 were
**re-measured at close and found already resolved by Phase 45.2 (QUA-04)**, not deferred.
**Phases:** 8 (43–46, incl. inserted 44.1, 44.2, 45.1, 45.2) · **Plans:** 43 · **Tasks:** 122
**Requirements:** 19/19 v1 requirements complete · **Known gaps:** none
**Timeline:** 2026-08-04 → 2026-08-11 (8 days)
**Git:** milestone branch `gsd/v0.7.1-bug-fix-round` (421 commits) merged to `main` via PR #132 with
all 15 CI checks green; tagged `v0.7.1` on the merge commit `48bf135`
**Code delta (milestone scope, excl. `.planning/`):** 125 files, +10,760 / −935 lines. The runtime
change is concentrated in `typsphinx/translator.py` (the nested-table/figure state stacks, the
`legend` handler, the split caption RENDERING/ANCHORING decision, and relative heading depth),
`typsphinx/builder.py` (the `typst_documents` default derivation and docname hardening), and
`typsphinx/template_engine.py` (the `params` exclusivity rule and the `lang` route widening); the
remainder is the RED-recorded regression gates each change carries — `test_params_exclusivity_gate.py`
(751 lines), `test_authors_pipeline_stage_gate.py` (614), `test_nested_table_render_gate.py` (577),
`test_entry_metadata_precedence.py` (540), `test_docs_contract_claims_gate.py` (477) — plus the
documentation rewrite, the toolchain rename, the version bump, and the CHANGELOG entry.
**Released 2026-08-11:** PyPI `typsphinx 0.7.1` (wheel 135,318 B + sdist 580,288 B) published by
release run `31462027486` after owner approval of the `pypi` environment. GitHub Release
`Release v0.7.1` carries all three assets (`.whl`, `.tar.gz`, and the tag-time `typsphinx.pdf`,
2,436,561 B). The standing second tag was pushed on `typsphinx-doc-translations`: `update-pin.yml`
run `31462409929` advanced its `typsphinx` submodule pin `87f242a` → `48bf135`, then annotated tag
`v0.7.1` was created there on `cf7fa30`.
**Read the Docs `stable` measured live 2026-08-11 (both projects):** `en` `stable` identifier
`48bf1354` (the v0.7.1 merge commit), `ja` (slug `typsphinx-ja`) `stable` identifier `cf7fa308` (the
translations repo's own v0.7.1 tag); both `active`/`built`, both pages report `0.7.1`, both PDFs
served (`en` 2,449,231 B / `ja` 2,642,276 B, `application/pdf`). No owner setting flips needed —
the fourth consecutive close at which none was required.

**REL-04 — closed for the first time, on generated evidence.** The requirement carried from v0.7.0,
where run `30848860064`'s `create-release` job failed at `uv: command not found` (exit 127, the
`astral-sh/setup-uv` step was missing) and the fix landed on `main` afterwards but was never
exercised end to end. This close exercised it: the real `v0.7.1` tag push fired release run
`31462027486`, whose `Create GitHub Release` job completed **success**. The published body was then
measured rather than assumed — its first 77 lines are **byte-identical** to
`scripts/extract_changelog_section.py 0.7.1`'s stdout (`diff` clean), and a `git log --pretty`
commit-dump shape matches **0** lines. Deliberately **not** reported complete on the strength of the
workflow file being correct, which is the precise error v0.7.0 made.

**Delivered:** the documented configuration finally takes effect. This was a maintenance round over
already-diagnosed defects — every requirement closed something already known to be broken, each
carrying a file/line-level todo or a measured basis.

**Key accomplishments:**

- **`typst_documents` gained a LaTeX-shaped default, so following the Quick Start produces a PDF**
  (CONF-08, DOC-11) — previously `sphinx-build -b typstpdf` with `typst_documents` unset exited 0
  with a warning and produced zero output. The default derives from `root_doc`/`project`/`author`
  mirroring `sphinx.builders.latex.default_latex_documents`, measured on real before/after builds
  from throwaway worktrees at named commits. A target name that slugifies onto an existing docname
  now falls back with a WARNING instead of silently destroying content.

- **An explicit entry's title and author now reach the rendered PDF** (CONF-09) — previously
  silently ignored while `config.project`/`config.author` won. Proven end-to-end via a real
  `-b typstpdf` compile read back through `pypdf`, backed by a 27-test precedence matrix including
  the multi-master no-leak property.

- **Nested tables and figures stopped corrupting the enclosing structure** (TBL-04, TBL-05, FIG-01,
  TOC-01) — snapshot save/restore stacks (`_push_table_state`/`_pop_table_state`,
  `_push_figure_state`/`_pop_figure_state`) plus a new `legend` handler; an empty-titled caption
  still anchors its ids via a split RENDERING/ANCHORING decision; and a toctree'd document's
  headings nest one level deeper instead of rendering flat. Each shipped a RED-recorded
  real-`typst.compile()` regression gate.

- **The published custom-template parameter contract and the code agree both ways** (DOC-13,
  CONF-10, CONF-11, CONF-12) — the contract was rewritten onto the nine parameters typsphinx
  actually passes and locked with a RED-proved gate; a declared `typst_template_function` `params`
  dict became the complete parameter set; the auto-derived `lang` now reaches every non-package
  template route; and `typst_authors` was removed outright with no deprecation shim.

- **The published changelog page stopped being two years stale** (DOC-12) —
  `docs/source/changelog.rst` now renders live from repo-root `CHANGELOG.md` via myst-parser's
  `include::` `:parser:` mechanism, closing the drift channel at its source; `CHANGELOG.md` was
  backfilled with the missing v0.4.4 release and deduplicated to one `[Unreleased]` heading.

- **`tox` ran on the maintainer's machine for the first time** (QUA-04) — renaming `tox-uv` to
  `tox-uv-bare` drops the bundled generic-linux `uv` wheel whose ELF NixOS cannot exec. All four tox
  environments now provision with no `TOX_UV_PATH` override, and the full pytest suite under an
  outer `uv run pytest` went from 45 failures to zero. This also retired the five Phase 45.1
  deferred items at their root cause.

- **Absolute image URIs from Sphinx's image converter or downloader no longer abort the compile**
  (Issue #130, PR #131, @christianwehe) — the project's first external contribution, merged into
  the milestone branch during Phase 46.

---

## v0.7.0 — API rendering design overhaul (Shipped: 2026-08-04)

**Closeout:** override_closeout — no `v0.7.0-MILESTONE-AUDIT.md` was run (owner decision at close:
`init.manager` reported all 8 phases `phase_complete=true` / `verification_status=passed`, and every
v1 requirement except the two publish-gated REL rows was already `Complete` before the close began).
6 open artifacts acknowledged as deferred (see STATE.md Deferred Items) — 4 of the 5 pending todos
are Phase 41 D-14's own recorded deferrals to v0.7.1+, one is a planning-docs hygiene record, and
the single dormant seed (SEED-001) was never scoped into this milestone.
**Phases:** 8 (36–42, incl. inserted 40.1) · **Plans:** 57 · **Tasks:** 158
**Requirements:** 32/33 v1 requirements complete · **Known gaps:** 1 (REL-04 — see below)
**Timeline:** 2026-07-29 → 2026-08-04 (7 days)
**Git:** milestone branch `gsd/v0.7.0-api-rendering-design-overhaul` (477 commits) merged to `main`; tagged `v0.7.0` on the merge commit
**Code delta (milestone scope, excl. `.planning/`):** 80 files, +14,619 / −339 lines. The runtime
change is concentrated in `typsphinx/translator.py` (the `desc_*`, `field_list`, admonition/rubric,
and citation handler families); the remainder is the RED-recorded regression gates each node-handler
change carries, the CHANGELOG-section extractor + `release.yml` rework, the version bump, and the
CHANGELOG entry.
**Released 2026-08-04:** PyPI `typsphinx 0.7.0` (wheel 122,514 B + sdist 477,342 B) published by
release run `30848860064` after owner approval of the `pypi` environment (15-minute wait timer).
GitHub Release `Release v0.7.0` carries all three assets (`.whl`, `.tar.gz`, and the tag-time
`typsphinx.pdf` from `docs.yml`) with the curated `## [0.7.0]` CHANGELOG body. Second-repository tag
done: `typsphinx-doc-translations` pin advanced to `75fd8ed` by `update-pin.yml` run `30848873442`
(commit `a2150b1f`) and tagged `v0.7.0` there. PR #129 merged to `main` with 15/15 CI checks green;
`v0.7.0` tagged on merge commit `75fd8ed`.

**Read the Docs `stable` measured live 2026-08-04 (`41-HANDOFF.md` item 5, both projects):** root
`https://typsphinx.readthedocs.io/` → `/en/stable/` (302 → 200); `en` `stable` identifier
`75fd8ed5` (the v0.7.0 merge commit), `ja` `stable` identifier `a2150b1f` (the translations repo's
own v0.7.0 tag); both pages report `0.7.0`; both PDFs served (`en` 1,965,123 B / `ja` 2,152,807 B,
`application/pdf`). Both builds `finished` / `success`. No owner setting flips were needed — both
Default Versions were already `stable` from the v0.6.4 close.

### Known Gaps

**REL-04 — not met; carried to v0.7.1.** The requirement is that the GitHub Release body is the
curated `## [X.Y.Z]` CHANGELOG section rather than a `git log --pretty` commit dump. The workflow
change landed correctly in Phase 41 (plan 41-01), but its **first real tag push failed**: the
`create-release` job runs `uv run python scripts/extract_changelog_section.py` and that job has no
`astral-sh/setup-uv` step — `validate` and `build` both do; `create-release` never needed uv until
REL-04 wired the extractor into it. Run `30848860064` went `validate` ✓ → `build` ✓ →
`publish-pypi` ✓ → `create-release` ✗ (`uv: command not found`, exit 127). `41-HANDOFF.md` item 1
had flagged this tag push as "the first moment that check exercises in anger"; it was, and it broke.

The v0.7.0 release body and the missing wheel/sdist assets were **repaired by hand** at the close, so
the published artifact matches what REL-04 describes. The automation has still never produced it.
`release.yml`'s `create-release` job gained the missing `Install uv` / `Set up Python` steps on
`main` after the release; REL-04 closes only when a real tag push exercises it end to end.

**Two CI-surface defects this milestone's own branch never saw until the release PR.** Alongside
REL-04, the Windows test lanes went RED on PR #129 — three signature render-gate modules added in
Phase 37 read and wrote `.typ` files with a bare `Path.read_text()`/`write_text()`, so Windows'
cp1252 default could not decode UTF-8 output (820 passed / 1 failed; Linux and macOS fully green).
Fixed in `9a544db` before merge. Both defects share a cause: **the milestone branch was never pushed
until the release PR**, so neither Windows CI nor a real tag push ran against it at any point during
the eight phases.

**Delivered:** API reference pages became readable. Autodoc/API output moved from a flat wall of
proportional bold text to a typeset reference document — monospace signatures with hanging-indent
wrapping, description bodies and field lists that indent by nesting depth off one shared constant,
and admonitions re-bucketed onto a taxonomy that survives greyscale. Citations gained full
round-trip support: a document containing one no longer fails the Typst compile outright. Zero new
runtime dependencies; the `@preview` package count stayed at four with no new version-lockstep site;
every node-handler change carries its own recorded-RED GATE-01 fixture.

**Key accomplishments:**

- **Signature typography (SIG-01..SIG-09, Phase 37)** — replaced `desc_signature`'s `strong({...})`
  wrapper with a composed `block(sticky: true, par(hanging-indent: 2.5em, …))`, routed every
  signature text run through `raw(...)` with ZWSP break-opportunity injection, and implemented the
  D-05 discriminator so names/annotations render bold monospace while each parameter renders italic
  and a resolved cross-reference keeps its hyperlink. Long signatures wrap without overflowing the
  margin and never split from the first line of their body across a page break — both proven by
  Typst-probe geometric render gates recorded RED against the untouched translator.

- **Structural indentation + info fields (IND-01..IND-05, FLD-01..FLD-03, Phase 38)** —
  `visit_desc_content` gained a real `pad(left: 2.5em, …)` body (no depth counter), `field_list`
  nests its own `SHARED_INDENT_STEP` pad inside it, and a single-value field body renders inline
  with its label. Field-body parameter names and types carry monospace treatment distinct from the
  plain-bold field label. The translator's last dummy-node delegation sites were replaced by one
  shared leaf-emission helper.

- **Admonition taxonomy + rubric nesting (ADM-01..ADM-06, Phases 36 & 39)** — all ten real
  admonition titles centralized on a single `sphinx.locale.admonitionlabels` lookup, five
  gentle-clues call sites re-routed, and the red family split into three pairwise-distinct functions
  after the owner reversed locked decision D-03 on a post-render greyscale probe. Phase 36 first
  decoupled the shared-emission seam so `desc_signature` and `rubric` could be restyled
  independently — with a recorded empty diff proving byte-identical `.typ` across the change.

- **Citations — full round trip (CIT-01..CIT-06, Phases 40 & 40.1)** — greenfield
  `visit_citation`/`depart_citation`/`visit_label` (run-scoped hanging-indent grid with
  back-reference markers) plus a guarded own-anchor addition to `visit_reference`. Phase 40.1 then
  hardened the degradation paths: `.. only::`-pruned citing sites fail closed instead of emitting a
  dangling `link()` target, ids-less `nodes.target` siblings no longer split one citation run into
  two independently-aligned grids, and the duplicated anchor-eligibility judgement collapsed into
  one shared predicate.

- **Two compile-fatal defects closed (MATH-02, TBL-03)** — `visit_math_block` now clears rather than
  arms the shared list-item separator flag (one blank line, not two, with a PDF-text invariance
  guard proving zero visible change), and `depart_table`'s `_emit_id_anchors` call moved past the
  `in_table` reset so a captioned table preceded by a standalone target emits both labels instead of
  aborting the compile on a dangling one. TBL-03 was promoted out of backlog item 999.2 on
  2026-08-03 *after* Phase 41 had already closed — the first requirement this project has added to
  an already-complete milestone.

- **Release notes sourced from the CHANGELOG (REL-04, Phase 41)** — a stdlib-only, positional
  `## [X.Y.Z]` extractor, pytest-covered and wired into both `release.yml` jobs, replacing the
  ~296-line `git log --pretty` dump. The same phase also converted every shell-context `${{ }}`
  interpolation in `release.yml` to `env:` passing (code-review CR-01), and left a standalone
  seven-item publish handoff checklist with zero irreversible action taken — the tag state was
  probed empty twice, 2m44s apart, to prove the fence held.
  **The extractor itself is correct and hand-verified; what failed at the real tag push is the job
  that calls it — see Known Gaps above.**

---

## v0.6.5 — inline-math separator hotfix (Shipped: 2026-07-29)

**Closeout:** override_closeout — no `v0.6.5-MILESTONE-AUDIT.md` was run (owner decision at close:
a 2-phase, 2-requirement hotfix where `init.manager` reported both phases `phase_complete=true` /
`verification_status=passed` and Phase 35's `35-RELEASE-EVIDENCE.md` had already discharged SC#1–SC#5
against live runs). 8 pending todos acknowledged as deferred (see STATE.md Deferred Items) — the 5
pre-existing ones were already named Out of Scope in the milestone's own REQUIREMENTS.md, and the 3
filed during v0.6.5 are its recorded deliberate deferrals (D-05, D-11) plus one docs-hygiene todo.
**Phases:** 2 (34–35) · **Plans:** 8 · **Tasks:** 27
**Requirements:** 2/2 v1 requirements complete (MATH-01, REL-03) · **Known gaps:** none
**Git:** milestone branch `gsd/v0.6.5-inline-math-separator-hotfix` (72 commits) merged to `main` via PR #125 (13/13 CI checks green before merge); tagged `v0.6.5` on merge commit `839d77f`
**Released 2026-07-28/29:** PyPI `typsphinx 0.6.5` (wheel 94,765 B + sdist 324,824 B, uploaded 21:15:39–21:15:40Z) + GitHub Release `v0.6.5` carrying all three assets (`.whl`, `.tar.gz`, and the tag-time `typsphinx.pdf` from `docs.yml`), via release run 30398631991 — green end-to-end after owner approval of the `pypi` environment. Second-repository tag done: `typsphinx-doc-translations` submodule pin advanced to `839d77f` by `update-pin.yml` run 30398664663 and tagged `v0.6.5` at `1891a09`. RTD `stable` rebuilt green on both tags and measured live: en `stable` identifier `839d77f38ffa`, ja `stable` identifier `1891a0905322`, root → `/en/stable/` (302→200), `/ja/stable/` 200, both pages reporting `0.6.5`, both PDFs served (en 1,705,336 B / ja 1,889,332 B). No owner flips were needed — both Default Versions were already `stable` from the v0.6.4 close.
**Known cosmetic cost (accepted, D-11):** the GitHub Release body is still the `git log` commit dump `release.yml` generates, not the curated `## [0.6.5]` CHANGELOG section — filed as `todos/pending/2026-07-29-release-notes-body-from-changelog-section.md`.
**Code delta (milestone scope, excl. `.planning/`):** 8 files, +560 / −4 lines — the entire runtime
change is +45 lines in `typsphinx/translator.py`; the rest is the GATE-01 regression fixture, the
version bump, and the CHANGELOG entry.

**Delivered:** A document mixing prose and math no longer aborts the Typst compile. Phase 34
root-caused the defect **by measurement** rather than from the backlog's guess, fixed it on both the
mitex and native emission paths, and pinned it with a real-`typst.compile()` fixture recorded RED
pre-fix; Phase 35 was prep-only, with zero irreversible action taken before this close.

**Key accomplishments:**

- Real-`typst.compile()` regression fixture reproducing the inline-math-after-text separator fatal in a list item, a collapsed confval field body, and a definition-list term, on both the mitex and native math paths, recorded RED against the unfixed translator
- Made `visit_math` participate in all three separator protocols (paragraph, code-mode concat, list-item) and `visit_math_block` participate in the list-item protocol, turning the GATE-01 gate GREEN on both the mitex and native `-D typst_use_mitex=0` emission paths
- Post-fix full regression sweep proves zero regression against Plan 01's pre-fix baseline (649 passed/1 skipped/0 failed), clean black/ruff/mypy, a fatal-free full-corpus GATE-02 pass, and a valid 93-page docs PDF — closing all five ROADMAP Phase 34 success criteria with direct evidence
- Added Construct G (labeled display-math inside a list item) to the GATE-01 fixture and four exact-string assertions derived from real `sphinx-build -b typstpdf` builds, closing all three test-side Warnings from the Phase 34 code review with zero `typsphinx/` changes.
- Filed two pending-todo records — WR-01's `visit_math_block` redundant blank line and `release.yml`'s release-notes-body rework — so both deliberate v0.6.5 deferrals (D-05/D-10, D-11) are recorded facts rather than lost ones.
- pyproject.toml/README.md/uv.lock all moved 0.6.4 -> 0.6.5 in lockstep; `uv.lock`'s diff is exactly one line (no transitive dependency re-resolved) and `typsphinx.__version__` confirms the editable-install metadata was regenerated.
- Inserted the curated `## [0.6.5]` CHANGELOG entry (lead paragraph + one-bullet Fixed + three-bullet Verified) and rolled over the tail link block, discharging ROADMAP Phase 35 SC#2 in both halves.
- Proved the post-bump v0.6.5 tree green across seven live runs (including both D-12 docs dogfooding builds), proved the three milestone invariants mechanically over the SHA-anchored full milestone diff (merge-base `eb696bb02d135227d880c679fc909513fe6f7d19`) with a positive control, proved no irreversible action was taken (empty local/remote tag checks plus an optional `gh release view` corroboration), and wrote the standalone six-item `35-HANDOFF.md` checklist `/gsd-complete-milestone` will execute — discharging ROADMAP Phase 35 SC#3, SC#4, and SC#5.

---

## v0.6.4 — Read the Docs migration (Shipped: 2026-07-28)

**Closeout:** verified_closeout — `v0.6.4-MILESTONE-AUDIT.md` passed (13/13 requirements, 6/6 phases
verified, integration checker all-wired, no broken flows); 5 pending todos acknowledged as deferred
(see STATE.md Deferred Items), 2 resolved todos filed to `todos/completed/`.
**Phases:** 6 (29–33, incl. inserted 30.1) · **Plans:** 33 · **Tasks:** 79
**Requirements:** 13/13 v1 requirements complete · **Known gaps:** none
**Git:** milestone branch `gsd/v0.6.4-read-the-docs-migration` (290 commits) merged to `main` via PR #124; tagged `v0.6.4`
**Released:** PyPI `typsphinx 0.6.4` (wheel + sdist) + GitHub Release `v0.6.4` (incl. the tag-time `typsphinx.pdf` asset — Phase 32's deferred live exercise proven), via release run 30309278708 (green end-to-end after owner approval of the `pypi` environment). RTD `stable` built green on the tag for both projects: root → `/en/stable/` 200, `/ja/stable/` 200 at the same release (en identifier `2bf6ef3`, ja at translations tag `v0.6.4`). Owner flips completed 2026-07-28: both Default branches → `main`, both Default Versions → `stable`; `.gitmodules` → `main`; Issue #119 closed; milestone branch deleted.
**Code delta (milestone scope, excl. `.planning/`):** 54 files, +900 / −7,118 lines — a net-negative
milestone: the hand-rolled multilang publishing machinery left the repository.

**Delivered:** Documentation hosting moved from GitHub Pages to Read the Docs end to end — English and
Japanese sites live behind RTD's own flyout, the downloadable PDF is the one `typstpdf` itself produced,
every published URL resolves, the hand-rolled multilang machinery is deleted, and the Pages host is
irreversibly torn down — with every reversible action ordered before the single no-undo one.

**Key accomplishments:**

1. **English RTD site stood up (Phase 29, RTD-01/RTD-04):** `.readthedocs.yaml` + the
   `READTHEDOCS_LANGUAGE` → `SPHINX_LANGUAGE` → `"en"` `_resolve_language()` seam in `conf.py`; the raw
   build log proves typsphinx installed from the checked-out commit (not a stale PyPI wheel); the root
   URL owned at Default Version = `latest` with real-HTTP fetches re-taken by every later phase.

2. **RTD serves typstpdf's own PDF (Phase 29, RTD-02/RTD-03):** `formats: [pdf]` + a
   `build.jobs.build.pdf` override replaces RTD's LaTeX path; the milestone's one open unknown
   (`@preview` egress from RTD's sandbox) resolved to Branch A — the served PDF content-compared
   against the local `tox -e docs-pdf` baseline (93==93 pages, byte-identical text, CJK font present),
   so the `releases/latest/download/` fallback (RTD-03) was satisfied vacuously.

3. **Japanese site from a separate translations repository (Phase 30.1, I18N-01/I18N-03):**
   `typsphinx-doc-translations` created on the `sphinx-doc-translations` model (submodule pin
   auto-advanced by a repaired `update-pin.yml`, observed moving the pin end to end); `/ja/latest/`
   probed against 100%-translated docnames; the Japanese PDF's 10-NUL-byte glyph defect root-caused to
   Typst's font selection and fixed via a custom template's explicit
   `("Libertinus Serif", "Noto Serif CJK JP")` — owner visual UAT confirmed, no English regression.

4. **The deletion round (Phase 30, I18N-02/DOC-08):** `build_multilang.py`, the language switcher,
   its `conf.py` wiring, every task-runner target, the orphan `docs/usage.rst`/`docs/installation.rst`
   pair with 20 collateral tests, and the relocated `docs/locale/` tree — all gone on a green suite
   with the docs build warning-for-warning identical to baseline.

5. **URL cutover behind a proven guard (Phase 31, DOC-09/DOC-10/CI-05):** advisory lychee `links.yml`
   installed first and recorded red on the unfixed tree (negative control); then all 11 retired-host
   URLs in `README.md`/`pyproject.toml` rewritten and locked by a hermetic regression guard; all 35
   published URLs fetched over real HTTP; About → Website set and verified.

6. **Irreversible Pages teardown, gated (Phase 32, CI-04) + release prep (Phase 33, REL-02):** the
   teardown proceeded only behind freshly re-taken evidence that RTD was serving en HTML, ja HTML
   (1038 CJK chars content-verified) and both PDFs; `gh-pages` deleted with `ls-remote`-proven absence
   and the github.io 404 directly observed; version bumped to 0.6.4 with the CHANGELOG curated and the
   publish fence proven held (no tag, no PyPI state) until this close.

**Deferred:** 5 pending todos (sphinx-linkcheck CI job → Future LNK-01; citation-node support;
non-str-docname TypeError hardening; typing-import modernization; `derive_typst_lang()` warning-block
duplication) and 3 quality warnings from 30.1's review (contributing.rst toolchain-install step;
`custom_template.typ` as an unguarded fourth `@preview` lockstep site; no structural tests over the
live translations-repo manifests). Accepted losses (owner decisions 2026-07-25): no browser-language
auto-redirect at the root; old `github.io` URLs 404 with no redirect stubs. Standing cost: every
release now tags **two** repositories (parent + `typsphinx-doc-translations`).

**Archives:** `milestones/v0.6.4-ROADMAP.md`, `milestones/v0.6.4-REQUIREMENTS.md`,
`milestones/v0.6.4-MILESTONE-AUDIT.md`, phase artifacts under `milestones/v0.6.4-phases/`

---

## v0.6.3 config & docs measured fidelity + captioned tables (Shipped: 2026-07-25)

**Phases completed:** 6 phases, 12 plans, 28 tasks

**Key accomplishments:**

- Removed the registered-but-inert `typst_toctree_defaults` Sphinx config value from all seven code/doc/test surfaces (registration line, README, examples, surgically-edited docs/configuration.rst, deleted test file) while leaving the historical CHANGELOG.md entry untouched.
- Captioned `.. table::`/csv-table/list-table now renders as `figure(table(...), caption: {...}, kind: table)` with native "Table N" numbering and a single collision-free `<label>`, fixing both the stray-heading bug and the stale-buffer bug that silently dropped a 2nd table's caption.
- Real `sphinx-build -> typst.compile() -> pypdf` GATE-01 fixture proves the shipped Plan 25-01 translator fix compiles green end-to-end — every captioned-table caption survives exactly once (including the previously stale-buffer-lost 2nd table), `:numref:`/`:ref:` resolve with no duplicate/dangling-label fatal, and a durable fail-pre-fix proof reconstructs both original defect shapes from first principles.
- RawTypst marker + ELEMENTS_ALLOWLIST curated merge in `template_engine.py`, wired from `writer.py` as a separate argument -- `papersize`/`fontsize` now reach `map_parameters()` with correct per-key typing, an unknown key fails loud via `ExtensionError`, and `copyright` is structurally unreachable.
- Four standing real-`typst.compile()`/`sphinx-build` cases (papersize quoted, fontsize unquoted on a separate build, unknown-key abort, copyright non-leak) plus a durable `TestPreFixBasisFailureProof` reconstruction class prove CONF-04's `typst_elements` pass-through actually reaches `project()` -- with a recorded manual red->green confirmation against Plan 01's fix.
- Orphan `docs/configuration.rst` (489 lines, wrong package name `sphinxcontrib.typst`) deleted with its collateral test, the 5 phantom config names purged from `user_guide/configuration.rst` (papersize/fontsize rewritten as working `typst_elements` examples on top of CONF-04), and the redundant drifted config `list-table` removed from `api/index.rst` so config is documented in exactly one canonical place — with a scoped ja gettext regen that also fixed a latent docutils CJK-markup bug it activated.
- `base.typ`'s `project()` gains a `lang` parameter wired into `set text(lang:)`, driven by a new `derive_typst_lang()` conversion helper and a `uses_bundled_default_template()` provenance predicate that gates auto-derivation to the default-template path only, with explicit `typst_elements["lang"]` always winning.
- `lang` documented as the third `typst_elements` key in configuration.rst (derivation, default-template-only scope, explicit-wins precedence, zh_TW limitation) with a scope-limited ja gettext regeneration that keeps all 12 pre-existing obsolete catalog blocks intact.
- A new `tests/test_typst_lang_gate.py` (18 tests, 8 classes) with seven real-compile fixture projects proves CONF-07's `lang` typesetting parameter actually reaches the compiled PDF and changes Typst's generated figure/table supplement labels — via the D-07 split proof (font-independent `ja` source assertion + `de` pypdf-extraction linkage assertion with a new NBSP-tolerant matcher) — while three non-regression fixtures prove no non-default template path ever receives an injected argument it never declared, and a durable pre-fix-basis reconstruction plus a manually recorded red-to-green transition close the loop.
- Atomic version bump across pyproject.toml, uv.lock, and README.md's Status line, with the editable-dist install metadata refreshed so `typsphinx.__version__` reports 0.6.3 and all three version-sync guard tests stay green.
- Live re-ran the SC#3 full-corpus regression gate, full pytest suite, and both docs-build tox environments against the post-version-bump v0.6.3 tree, and recorded verbatim evidence plus SC#4/SC#5 git-diff assertions in a new `28-VERIFICATION.md`.
- Curated `## [0.6.3]` CHANGELOG entry (5 bullets, 6/7 v1 ledger IDs, BREAKING exactly on CONF-04/CONF-05) plus an advanced link-reference block, single source for the eventual GitHub Release body.

**Fixed at the close, before the tag:** the bundled `examples/advanced` sample was unbuildable on two
independent axes — five `typst_elements` keys outside the CONF-04 allowlist Phase 26 had just made
fail-loud, and `_templates/custom.typ` three milestones behind on its `@preview` pins
(`unknown variable: kai`). The template now declares `papersize`/`fontsize`/`lang` in its `project()`,
and `tests/test_preview_version_sync.py` gained a fourth-surface check over `examples/**/*.typ`.

**Closeout type:** `override_closeout`. All 6 phases were `phase_complete` with
`verification_status: passed` and 7/7 v1 requirements checked off, but no `v0.6.3-MILESTONE-AUDIT.md`
was produced (owner accepted at close — Phase 28's live re-run of the full-corpus gate, the full
pytest suite, and both docs-build environments stands in). Known verification overrides: 9 deferred
pending todos (see STATE.md Deferred Items).

**Verified at close:** full suite 657 passed / 1 skipped; `black`/`ruff`/`mypy` clean; full-corpus
regression gate fatal-free with an empty `unknown_visit` catalogue; `sphinx-build -b typstpdf
examples/advanced` builds. Zero new runtime dependencies; no `@preview` version bump.

---

## v0.6.2 rendering fidelity round 2 (Shipped: 2026-07-23)

**Closeout:** override_closeout (pre-close artifact audit surfaced one non-blocking item — Phase 22.3's verification abstained to `human_needed` for a single `verification: backstop` truth: exercising the two GATE-01 fixtures under a real `pytest-xdist` parallel run, which the project does not depend on. All five ROADMAP success criteria for 22.3 were independently verified with direct evidence, including two live revert-and-restore reproductions of the pre-fix defects. Every other phase (19, 20, 21, 22, 22.1, 22.2, 22.4, 23) is `phase_complete` + verification `passed`. Operator acknowledged the backstop item plus 9 pending-todo backlog entries as deferred at close — see STATE.md Deferred Items. **Known verification overrides: 1** (Phase 22.3 pytest-xdist backstop).)
**Phases:** 9 (19, 20, 21, 22, 22.1, 22.2, 22.3, 22.4, 23) · **Plans:** 30 · **Tasks:** 65
**Requirements:** 25/25 v1 requirements complete (FID-02..FID-14, PDF-01, PDF-02, CONF-01..CONF-03, WR-01, WR-02, DOC-01..DOC-05) · **Known gaps:** none milestone-blocking
**Git:** milestone work on `gsd/v0.6.2-rendering-fidelity-round-2` (branching strategy `milestone`); tagged `v0.6.2` at close
**Milestone invariant held:** zero new runtime dependencies, no `@preview` version bump, the 3-way version-sync surface (`writer.py`/`template_engine.py`/`templates/base.typ`) untouched

**Delivered:** Round 2 of rendering fidelity — resolved the 13 medium/low silent mis-render findings the v0.6.1 audit left open as one coherent `translator.py` fix series grouped by root cause (clusters A–F), each pinned by a fail-pre-fix real-`typst.compile()` GATE-01 fixture, plus five inserted builder/config/docs phases: the Issue #117 `typstpdf` target-name PDF fix, nested-master compile-root alignment, a dead-config sweep that also repaired the entirely-broken `typst_package` Typst-Universe path end-to-end, builder-warning hardening (a missing/malformed master now fails loudly instead of a silent successful build), and a full-text README/CLAUDE.md accuracy pass. Closed on the full ~684-page Sphinx `doc/` corpus regression gate (fatal-free, valid `%PDF`, `unknown_visit` catalogue empty).

**Key accomplishments:**

- **Block-separation cluster (Phase 19, FID-02..FID-06):** adjacent block / sibling elements — paragraphs-in-list-items, sibling `desc_signature`s, rubric/option headings, definition-list term↔definition, back-to-back body-less `confval`s — now render with the visible separation the `-b html` authority shows instead of concatenating, via a coherent set of `parbreak()`/`linebreak()`/`terms(separator:)` separator fixes.
- **Signature token spacing + residual fidelity (Phases 20–21, FID-07..FID-14):** intra-signature token spacing restored (`class `/`exception ` prefix, C/C++ inter-token spaces, `:type:`/`:default:` colon-space) by reducing `desc_sig_space` to pass-through; long inline-literal runs wrap at UAX14 boundaries instead of clipping, paragraph soft-newlines collapse to a space, the codly config wrapper stops leaking as prose, external links get `show link:` styling, and PEP 3102/570 separators stop injecting their hover-title text inline.
- **Issue #117 target-name PDF fix + nested-master alignment (Phases 22, 22.1, PDF-01/PDF-02):** a single guarded `TypstBuilder._resolve_output_stem()` now governs all three `.typ`/`.pdf` output-path sites so `typst_documents = [('index', 'manual.typ', …)]` emits `manual.pdf`, not `index.pdf`; `TypstPDFBuilder.finish()` compiles each master's own on-disk `.typ` at its real docname-derived location so nested masters (`api/index`) resolve their `#include()`s and images — the compile basis now matches the translator's emission basis.
- **Dead-config sweep + `typst_package` repair (Phase 22.2, CONF-01..CONF-03):** deleted `typst_output_dir` and `typst_author_params` from every surface, and made the Typst-Universe `typst_package` path — previously unable to compile at all — work end-to-end (BUG-A `_template.typ` never written, BUG-B unconditional param injection, BUG-C dead author wiring, BUG-D wrong docs examples), all locked by a standing config→output regression gate so a registration-only assert can no longer hide a dead feature.
- **Builder-warning hardening + docs accuracy (Phases 22.3, 22.4, WR-01/WR-02, DOC-01..DOC-05):** a missing or malformed master now joins the aggregate `ExtensionError` instead of a silent successful build, the render gate stops asserting on `typst-py`'s uncontracted error wording, and README/CLAUDE.md/pyproject comments were re-derived from measured behavior — unverifiable numeric claims (test count, coverage %) removed rather than re-measured, with a `README`↔`pyproject` version-sync ratchet test added.
- **Release prep + regression-gate close (Phase 23):** bumped `pyproject.toml` → 0.6.2 (sole literal) with `uv.lock` in lockstep, curated the `## [0.6.2]` CHANGELOG entry covering all 25 ledger IDs (Issue #117 presented as a user-visible output-filename change; `### Removed` for the config deletions), and closed on a live full-corpus `-b typstpdf` gate.

---

## v0.6.1 rendering fidelity (Shipped: 2026-07-19)

**Closeout:** override_closeout (pre-close artifact audit clear; Phase 16 & 18 verified `passed`; Phase 17 — a pure audit/documentation phase — has no machine `VERIFICATION.md`, so `init.manager` could not certify `verified_closeout`. Its verification was instead the human confirmation gate 17-03 (D-01a: 14 accepted / 1 rejected of the 15 candidate findings, final severities signed off) plus `17-VALIDATION.md` (five mechanical consistency checks PASS), and its output — FID-01a — was proven downstream by Phase 18's real-compile regression fixture + the closing full-corpus gate. Verification override accepted by operator at close.)
**Phases:** 3 (16–18) · **Plans:** 9 · **Tasks:** 18
**Requirements:** 6/6 v1 requirements complete (TODO-01, MAN-01, LEN-01, AUD-01, FID-01→FID-01a, GATE-03) · **Known gaps:** none (13 medium/low audit findings recorded in `17-AUDIT-CATALOGUE.md` as a Future-Requirements pointer, not milestone-blocking)
**Git:** milestone work on `main` (branching strategy `none`), commits from `dcd03eb` (2026-07-13) through `cc7c64a` (2026-07-19); tagged `v0.6.1`
**Code delta (milestone scope):** ~15 source/test files, +1229 / −13 lines (`typsphinx/translator.py` + `tests/`); zero new runtime dependencies; the 3-way `@preview` version-sync surface untouched

**Delivered:** Moved `typstpdf` output from "compiles fatal-free" (v0.6.0) to "renders faithfully" — implemented the last two silently-dropped nodes (`todo_node`, `manpage`), generalized the CSS-length converter into one shared helper (LEN-01), ran a full 151/151-docname human-assisted visual audit of the Sphinx v9.1.0 `doc/` corpus PDF against its `-b html` baseline (15 findings catalogued, human-confirmed), fixed the sole high-severity finding (F12 wide-table overflow → FID-01a) with a real-compile regression fixture, and closed on the full ~684-page corpus regression gate (fatal-free, `unknown_visit` catalogue empty).

**Key accomplishments:**

- `.. todo::` now renders as a gentle-clues `task()` box with its own dynamic title, gated on `todo_include_todos` via `nodes.SkipNode` exactly like every official Sphinx builder — proven through a real `sphinx-build -> typst.compile() -> pypdf` round trip in both the enabled and disabled configurations.
- `visit_manpage`/`depart_manpage` delegate wholesale to `visit_emphasis`/`depart_emphasis`, rendering `:manpage:` page-reference text (e.g. `ls(1)`) italic in every separator/mode context, proven by a real `typst.compile()` + pypdf GATE-01 fixture spanning a paragraph, a list item, and a figure caption.
- Wired `_convert_length_to_typst` into `visit_figure`/`depart_figure` (`:figwidth:`) and `depart_table` (`:width:`, covering `.. table::`/`.. csv-table::`/`.. list-table::`), closing LEN-01 as the single shared CSS-length -> Typst-length helper used at every length-bearing docutils site.
- Built the rendering-fidelity audit scaffold — three same-corpus baselines (typstpdf/html/text), a corrected exact docname-to-page mapping for all 151 docnames, and the committed `17-AUDIT-CATALOGUE.md` skeleton with fresh provenance, so Plan 17-02's page-by-page visual pass can start immediately.
- Full 151/151-docname visual audit of the sphinx-doc/sphinx v9.1.0 corpus PDF vs. its `-b html` baseline complete, yielding 15 classified systemic findings (1 high / 12 medium / 2 low severity) ready for the Plan 17-03 human confirmation gate.
- Grouped the human-confirmed catalogue's single high-severity finding (F12, wide-table overflow) into `FID-01a`, appended it plus a medium/low pointer to REQUIREMENTS.md, and passed all five mechanical consistency checks against a freshly rebuilt corpus.
- depart_table now emits fr-weighted `columns: (Nfr, ...)` from docutils colwidth, and visit_literal injects U+200B after `.`/`_` in in-table raw() content, closing the audit's sole high-severity wide-table collision bug.
- Re-ran the real ~684-page Sphinx v9.1.0 corpus through `-b typstpdf` post-FID-01a: fatal-free (689-page `index.pdf`, valid `%PDF` magic), `unknown_visit` catalogue empty, and the SC#4 no-new-deps/no-`@preview`-bump invariant confirmed untouched — milestone v0.6.1's regression gate is closed.

---

## v0.6.0 real-world robustness (Shipped: 2026-07-13)

**Closeout:** override_closeout (milestone audit passed — 19/19 requirements, 16/16 integration seams wired, 5/5 E2E flows; pre-close artifact audit found 13 open debug sessions — non-fatal post-GATE-02 rendering-polish, acknowledged and deferred to the next milestone, see STATE.md Deferred Items)
**Phases:** 5 (11–15) · **Plans:** 15 · **Tasks:** 33
**Requirements:** 19/19 v1 requirements complete · **Known gaps:** none (13 non-fatal render-polish items deferred as next-milestone backlog)
**Git:** milestone work (173 commits) delivered via PR #115 (`release/v0.6.0 → main`, closes #114), merge commit `cc26b47`; tagged `v0.6.0` on the merge commit. A Windows-only CI false-negative (the corpus SC#2 `unknown_visit` parser was `^`-anchored and missed CRLF/leading-CR/location-prefixed warning lines) was root-cause-fixed on the PR before merge — the real gate (SC#1 fatal-free compile) passed on all platforms throughout.
**Released:** PyPI `typsphinx 0.6.0` (wheel + sdist) + GitHub Release `v0.6.0`, via `release.yml` (run 29210840198, green end-to-end)
**Code delta (milestone scope):** all work in `typsphinx/translator.py` (+ tests/fixtures); zero new runtime dependencies

**Delivered:** Sphinx's own full `doc/` tree now compiles end-to-end through the `typstpdf` builder with no fatal `TypstCompilationError` (Issue #114 closed) — fixing the two fatal figure/image bugs (px→pt length conversion + `:target:`/caption buffer-swap), adding correct rendering for the highest-frequency previously-dropped nodes (version directives, `refid` cross-references, autodoc `desc_*`, footnotes via a doctree pre-pass, transition/topic/line_block/glossary/tabular_col_spec/abbr), and a graceful-degrade net for out-of-scope graphical nodes — all behind a standing real-`typst.compile()` acceptance gate (GATE-01) and validated against the real corpus (GATE-02). Zero new runtime dependencies; the 3-way `@preview` version-sync surface untouched.

**Key accomplishments:**

- New `_convert_length_to_typst()` regex-based CSS-length-to-Typst converter wired into `visit_image` (fixes Issue #114's fatal `width: 200px` compile abort), plus a shared `_visit_graphical_placeholder()` helper giving `graphviz`/`inheritance_diagram` a visible bordered Typst `rect()` block + one warning + clean `SkipNode` instead of leaking source or aborting
- Figure captions now render through the normal visitor chain via buffer-swap (never `node.astext()`), consumed as a `{...}` code-block `caption:` argument, plus a new `refid` fallback branch in `visit_reference` so internal same-document `:target:` links compile alongside external-URL ones
- Extended `tests/test_pdf_render_gate.py` with three `slow`-marked real-compile test classes proving FIG-01/FIG-02/DEG-01/DEG-02 through `sphinx-build -> typst.compile() -> pypdf` — and, in the process, discovered and fixed a third, previously-hidden fatal Typst-compile bug (labels attached to code-mode statements are invalid Typst syntax) that this gate's own real-compile methodology was the only way to surface
- Unboxed italic version-directive labels (`versionadded`/`versionchanged`/`deprecated`/`versionremoved`) rendered by detecting Sphinx's own classed inline, with a real-compile GATE-01 fixture proving all four kinds plus the content-less case.
- Fixed the fatal dangling-`:term:`-anchor bug by emitting a bracket-wrap Typst `<label>` in `depart_term`, confirmed `visit_reference`'s refid branch was already correct, and proved both fixes with a real-compile `TestXrefRefidRenderGate` gate that would abort without them.
- Landed the four autodoc signature sub-part handlers -- `desc_returns` (return arrow), `desc_signature_line` (genuine `linebreak()`, resolving Open Question 1 empirically), `desc_optional` (recursion-safe nested brackets), and `desc_inline` (transparent pass-through, D-06) -- plus a real-compile GATE-01 fixture proving all four via `pypdf` text-extraction.
- Four small additive translator.py handlers -- transition-to-rule, glossary pass-through, tabularcolumns SkipNode, and stateless abbreviation-expansion -- proven correct through a real sphinx-build -> typst.compile() -> pypdf round-trip.
- Widened the load-bearing `visit_title`/`depart_title` buffer-swap to cover `nodes.topic` parents alongside `nodes.Admonition`, added `visit_topic`/`depart_topic` reusing the `clue` box helper, and fixed a pre-existing multi-child-title compile fatal — all four locked decisions (D-01/D-02/D-05/D-06) plus the Pitfall-1 fix landed as one atomic change per RESEARCH.md's atomicity mandate.
- Added visit_line_block/visit_line to translator.py so line-block content (addresses, epigraph shapes, poetry stanzas) renders with every line break preserved via a real `linebreak()`, and nested line blocks reproduce their structural indentation via a per-depth `h()` spacer — both compile-safe with zero markup-mode involvement.
- New `topic_line_block_render_gate` fixture + `TestTopicLineBlockRenderGate` class prove, via an uncaught real `typst.compile()`, that topic titles and `.. contents::` never leak into Typst's auto-outline (count==1), address/poem `line_block`s produce genuine `linebreak()`s (never source-`\n`-only concatenation), and the pre-existing multi-child admonition-title path (Pitfall 1) still renders correctly.
- Typst-native footnote rendering via a document-order pre-pass index in `visit_document`, with `visit_footnote_reference` emitting the compile-proven `[#footnote({body}) <fn-id>]` / `footnote(<fn-id>)` definition/reuse forms and `visit_footnote` suppressing the definition at its natural docutils location.
- A real `typst.compile()` acceptance fixture (`footnote_render_gate`) and `TestFootnoteRenderGate` class prove the Plan 14-01 footnote handlers compile cleanly end-to-end (SC#1-4), and in doing so caught and fixed a genuine paragraph-state-clobbering bug in `visit_footnote_reference`'s buffer-swap that would have made every realistic footnote citation a fatal compile abort.
- New `tests/test_corpus_gate.py` slow-marked pytest module that shallow-clones Sphinx's own `doc/` tree, wires in typsphinx, builds the full tree through `typstpdf`, and asserts the fatal-free PDF triple plus a frequency-ranked `unknown_visit` catalogue.
- Git-worktree-isolated depart_term XREF-01 revert + env-gated before/after empty-URL warning counter, both builds translate-phase-only (`-b typst`), added to `tests/test_corpus_gate.py`

---

A historical record of shipped versions. Full detail per milestone lives in `.planning/milestones/`.

---

## v0.5.0 — forward-ecosystem

**Shipped:** 2026-07-11
**Closeout:** verified_closeout (pre-close artifact audit clear; all 6 phases verified; milestone audit passed — 14/14 requirements, 5/5 integration seams, E2E release flow ready)
**Phases:** 6 (6–10 + 8.1) · **Plans:** 13 · **Tasks:** 29
**Requirements:** 14/14 v1 requirements complete · **Known gaps:** none
**Git:** milestone work on `release/v0.5.0`, merged to `main` via PR #112; tagged `v0.5.0` (on `main`)
**Released:** PyPI `typsphinx 0.5.0` (wheel + sdist) + GitHub Release, via `release.yml` (green end-to-end)
**Code delta (milestone scope, excl. `.planning/`):** 29 source/config files, +1025 / −467 lines

**Delivered:** Ported typsphinx forward from the v0.4.4 known-good pins to the current ecosystem — Sphinx 9.1, docutils 0.22, typst 0.15, Python 3.12–3.13 — bumping the four bundled `@preview` packages in lockstep to compile cleanly (empirically closing the `unknown variable: kai` break), modernizing the soft-deprecated docutils/Sphinx API surface, fixing a long-latent admonition markup/code-mode render bug (discovered once `docs-pdf` first compiled post-`kai`-fix), adding a `typst compile` smoke gate that guards all four packages, and releasing v0.5.0 to PyPI with the full 3-OS × Python 3.12–3.13 CI matrix observed green. Latest-only, no compatibility range.

**Key accomplishments:**

1. **Raised runtime pins + Python floor (Phase 6):** Re-pinned `sphinx>=9.1,<10` / `docutils>=0.21,<0.23` and raised the Python floor to 3.12–3.13 across all 21 declaration sites (pyproject `requires-python`/classifiers, regenerated `uv.lock`, `tox.ini`, and the four GitHub Actions workflows) as one atomic pin-raise — both builders confirmed registering and a live `-b typst` build passing under Sphinx 9.1.
2. **Bumped `@preview` packages + typst 0.15 — the `kai` fix (Phase 7):** Raised `typst>=0.15.0,<0.16` and bumped mitex `0.2.4`→`0.2.7` (the actual fix, mitex PR #201), gentle-clues `1.2.0`→`1.3.1`, codly-languages `0.1.1`→`0.1.10` (codly `1.3.0` unchanged, registry ceiling), in lockstep across the 3-way version-sync — empirically closing the `unknown variable: kai` compile break via a real `tox -e docs-pdf` run producing a clean 101-page PDF.
3. **API & test compatibility (Phase 8):** Landed `traverse()`→`findall()` and modernized all soft-deprecated docutils/Sphinx call sites (`OptionParser`→`get_default_settings`, `builder.app`→`_app`, `writer_name`→`writer=get_writer_class(...)()`), then installed a permanent pytest `filterwarnings` guard escalating both `DeprecationWarning` and `PendingDeprecationWarning` — full suite green, zero `traverse()` remaining.
4. **Admonition rendering fix (Phase 8.1, inserted):** Rewrote `_visit_admonition`/`_depart_admonition` to emit gentle-clues code-mode content-blocks (`info({...})`) instead of markup-mode brackets (`info[...]`), preserved inline-markup titles via a buffer-swap (also fixing a latent title double-emission bug), added the five previously-unimplemented types (`hint`/`error`/`danger`/`attention`/generic `.. admonition::`), and proved it with a real `sphinx-build → typst.compile() → pypdf` PDF-text-extraction acceptance gate.
5. **Green CI matrix + smoke gate + guardrails (Phase 9):** Observed all 13 CI jobs green for the first time on Sphinx 9.1/docutils 0.22/typst 0.15 across all 3 OS runners (PR #112); added a `typst compile` smoke gate (`tests/test_preview_smoke_gate.py`) exercising all four `@preview` packages via real calls — closing the coverage gap the historical `kai` regression slipped through, proven with a negative control; reconciled stale `main` branch-protection required-checks; confirmed the dependency-ceiling guardrails (`sphinx<10`/`typst<0.16`/`docutils<0.23`).
6. **Version single-source + v0.5.0 release (Phase 10 + milestone close):** `typsphinx.__version__` now derives from `importlib.metadata` (retiring the stale `0.4.3`) with `pyproject.toml` the sole `0.5.0` literal, `uv.lock` regenerated, plus an independent `tomllib` drift-guard test; curated `CHANGELOG.md` `## [0.5.0]` entry as the Release-body source; publish half (merge PR #112 → tag `v0.5.0` → `release.yml` → PyPI + GitHub Release) executed at milestone close, mirroring the v0.4.4 precedent.

**Deferred:** CFG-01 (was FWD-03 — user-configurable `@preview` versions) and XOS-01 (cross-OS docs-PDF CI on macOS/Windows) → v2. Phase 8's multi-`<term>` definition-list hardening deferred as forward-looking (no current docutils 0.22.4 rST syntax emits a multi-`<term>` node).

**Archives:** `milestones/v0.5.0-ROADMAP.md`, `milestones/v0.5.0-REQUIREMENTS.md`, `milestones/v0.5.0-MILESTONE-AUDIT.md`

---

## v0.4.4 — CI-repair + modernize

**Shipped:** 2026-07-05
**Closeout:** verified_closeout (pre-close artifact audit clear; all 5 phases verified)
**Phases:** 5 (1–5) · **Plans:** 15 · **Tasks:** ~35
**Requirements:** 23/23 v1 requirements complete · **Known gaps:** none
**Git:** milestone work merged to `main` via PRs #104 / #105 / #106; close + release-prep via #109; tagged `v0.4.4` (on `main` dae500a)
**Released:** PyPI `typsphinx 0.4.4` (wheel + sdist) + GitHub Release, via release run 28731646924 (green end-to-end)
**Code delta (milestone scope):** ~15 source/config files, +217 / −1202 lines (net, incl. `uv.lock` collapse)

> **Release note:** The first `v0.4.4` tag push failed at the `release.yml` Validate gate — the
> version-verify step imported stdlib-only `tomllib` on the 3.10 floor (a PYVER-02 side effect
> only exercised at tag time). Fixed with a `tomllib`/`tomli` fallback (PR #110), tag re-pointed,
> release re-run green. This also resolved D-11 (`softprops/action-gh-release@v3` ran green).

**Delivered:** Restored a fully green CI pipeline on `main` — lint, the 3-OS × Python 3.10–3.13 test matrix (19 jobs), coverage, and the docs PDF build — by pinning the runtime dependency graph back to a known-good, reproducible combination, then modernized the Python floor and dev tooling and installed durability guardrails so the drift can't silently recur.

**Key accomplishments:**

1. **Root-cause pin (Phase 1):** Pinned `typst>=0.14.1,<0.15` (with precautionary `sphinx<9` / `docutils<0.22` ceilings), regenerated `uv.lock`, mirrored tox ceilings, and removed the dead `sphinx-testing` dep — fixing the `typst.TypstError: unknown variable: kai` break from a bundled `@preview` package under typst 0.15.
2. **Verified green baseline (Phase 2):** Confirmed every previously-red CI job green across the full matrix (incl. the 7 PDF-integration tests and `docs.yml` multi-language PDF-copy), and guarded the 3-way `@preview` version sync with an automated desync test.
3. **Modernized Python floor (Phase 3):** Bumped the supported range to 3.10–3.13 across every config surface (pyproject, tox, CI/docs/release workflows, black/ruff/mypy target-versions) as one atomic, CI-verified batch.
4. **Refreshed dev tooling (Phase 4):** Conservative floor+ceiling bumps for pytest/mypy/black/ruff/tox; artifact actions to node24 ahead of GitHub's 2026-09-16 Node-20 removal; removed the stale `Test Python 3.9` required check.
5. **Durability guardrails (Phase 5):** `uv sync --locked` at all 9 sites (DUR-01), a standalone weekly + dispatch `drift.yml` forward-drift detector with deduplicated issue reporting (DUR-02), a scoped `sphinx-typst-stack` Dependabot group (DUR-03), and a README CI status badge (DUR-04).

**Deferred:** D-11 (`softprops/action-gh-release@v3` tag-gated runtime confirmation) — signed off to the next real release tag (this v0.4.4 release exercises it). v2 forward-ecosystem support (FWD-01/02/03: Sphinx 9, typst 0.15+, configurable `@preview` versions) remains out of scope.

**Archives:** `milestones/v0.4.4-ROADMAP.md`, `milestones/v0.4.4-REQUIREMENTS.md`

---
