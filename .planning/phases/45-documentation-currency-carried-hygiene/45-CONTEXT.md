# Phase 45: Documentation Currency + Carried Hygiene - Context

**Gathered:** 2026-08-09
**Status:** Ready for planning

<domain>
## Phase Boundary

Make what the project tells a reader match what it now does after Phases 44 / 44.1 / 44.2, and close
the two small carried hygiene items.

Four requirements:

- **DOC-11** — the README Quick Start states what `typst_documents` does, when it must be set, the
  CONF-08 derived default including the `<project>.typ` name shape, that an explicit setting
  overrides the default, and which documents become PDFs.
- **DOC-12** — the published changelog page (`docs/source/changelog.rst`) carries every release from
  0.4.1 through 0.7.0 instead of being frozen at `Version 0.4.0 (Current)`, and both
  `tox -e docs-html` and `tox -e docs-pdf` build it clean.
- **QUA-02** — `derive_typst_lang()` emits its rejection-path warning from exactly one site, with no
  change to the warnings a build produces.
- **QUA-03** — `.planning/PROJECT.md` contains zero unterminated `<!--`, checked by scanning the
  whole file.

Not in this phase:

- **`docs/source/user_guide/templates.rst`.** Its four-parameter custom-template contract is
  **Phase 45.1 / DOC-13**. Do not edit that file here — Phase 45.1's SC#2 must *check* the published
  contract, not inherit an edit this phase made to it.
- **The `## [0.7.1]` CHANGELOG entry.** Phase 46 owns it. This phase's job is to make that a
  zero-extra-edit addition (see D-01).
- **Converting `CHANGELOG.md` away from Markdown.** Measured and rejected during this discussion —
  see D-02.
- **Any `typsphinx/` behaviour change beyond QUA-02's single-site warning refactor** (ROADMAP SC#5).

</domain>

<decisions>
## Implementation Decisions

Every measurement below was taken during this discussion against the current tree unless a different
date is stated.

### DOC-12 — the changelog page mechanism

- **D-01: The page delegates to `CHANGELOG.md` via a myst-parser `include`.** Rather than duplicating
  release history in reStructuredText, `docs/source/changelog.rst` shrinks to its framing sections
  plus an include of the repository's `CHANGELOG.md`, parsed as Markdown
  (`.. include:: ../../CHANGELOG.md` with `:parser:`; MyST's documented `myst_parser.sphinx_` parser
  is the starting candidate — confirm the exact spelling, whether the extension must also be listed
  in `extensions`, and the minimum `myst-parser` version at research time). `myst-parser` is added to
  the **`docs` extra only** — the standing zero-new-**runtime**-dependency invariant is untouched, and
  the `docs` extra already carries `furo`, `sphinx-autodoc-typehints`, and `sphinx-intl`.

  Why this shape: ROADMAP SC#2 requires both that the page *carry every release* and that adding
  `0.7.1` in Phase 46 be "a one-line addition rather than a re-derivation". A hand-maintained
  duplicate satisfies the first and fails the second — and the duplicate drifting silently for 12
  releases is the entire reason this requirement exists. Under D-01, Phase 46 edits `CHANGELOG.md`
  alone and the published page follows with **zero** additional edits.
  — **Reversibility:** reversible — one directive in one file plus one dependency line.

- **D-02: `CHANGELOG.md` stays Markdown.** Converting it to reStructuredText was proposed by the owner
  and withdrawn on measurement. `CHANGELOG.md` is not a docs-only file; it is the supply source for
  the **GitHub Release body (REL-04)**. Measured consumers:

  | Consumer | What it does |
  |---|---|
  | `scripts/extract_changelog_section.py` | parses **Markdown** `## [X.Y.Z]` headings and prints the section body |
  | `.github/workflows/release.yml:72-79` | pre-tag validate gate — aborts the release if the section is missing or empty |
  | `.github/workflows/release.yml:190-197` | pipes the extracted body into `release_notes.md` → the GitHub Release body |
  | `tests/test_changelog_extraction.py` | subprocess-level coverage of the script, in the same call shape production uses |
  | `.github/workflows/links.yml:43` | excludes `CHANGELOG\.md$` from the lychee sweep |

  The decisive fact: **GitHub renders release bodies as Markdown**, so an rST section body pasted
  there degrades to raw text. Compounding it, **REL-04 is the one open requirement carried from
  v0.7.0 and has never run green end to end** (the v0.7.0 tag push died at `uv: command not found`;
  the Release was repaired by hand). Rewriting the extractor in Phase 45 would hand Phase 46 a
  never-exercised path to prove for the first time.
  — **Reversibility:** one-way in practice — undoing it means re-authoring the extractor, its test,
  and two `release.yml` sites, and re-proving REL-04, whose whole remaining obligation is a clean
  end-to-end run of the *existing* mechanism.

- **D-03: The missing `## [0.4.4]` section is reconstructed and added to `CHANGELOG.md`.** It lands
  together with its `[0.4.4]:` link-reference line. Discovered during this discussion: **`v0.4.4` was tagged and
  released, but `CHANGELOG.md` has no section for it** — `grep 0.4.4 CHANGELOG.md docs/source/changelog.rst`
  returns nothing, and the link-reference block jumps `[0.5.0]` → `[0.4.3]`. `git rev-list --count v0.4.3..v0.4.4`
  = **148 commits**. This is why ROADMAP SC#2 counts **12** missing releases (0.4.1 … 0.7.0
  inclusive) while the DOC-12 todo lists 11 — the todo compared the page against `CHANGELOG.md`,
  which itself has the hole.

  Because D-01 delegates, a hole in `CHANGELOG.md` is a hole on the published page. Reconstruct the
  entry from the `v0.4.3..v0.4.4` commit range and the existing GitHub Release for `v0.4.4`.
  Note this phase therefore edits the same file Phase 46 edits — a *historical backfill*, distinct
  from Phase 46's new `## [0.7.1]` section. Nothing about the reconstruction may disturb
  `extract_changelog_section.py`'s parse of any other section (SC-relevant: `tests/test_changelog_extraction.py`
  must stay green).
  — **Reversibility:** reversible — an additive section plus one link-reference line.

- **D-04: The duplicate `## [Unreleased]` is merged into the single one at the top of the file.**
  `CHANGELOG.md` carries `## [Unreleased]` at **line 8** (empty) and again at **line 911**
  ("Planned for Future Releases"). Under D-01 both would surface on the published manual, and Sphinx
  would warn on the duplicate section. Fold line 911's content into the top-of-file `[Unreleased]`
  (or drop it if it is stale) and delete the second heading. Verify while doing so that
  `extract_changelog_section.py` is unaffected — it matches `## [X.Y.Z]` version headings, so
  `[Unreleased]` should be outside its match set, but confirm rather than assume.
  — **Reversibility:** reversible — a content move inside one file.

- **D-05: The 25 `✅` characters are removed from `CHANGELOG.md`.** They sit in the `0.1.0b1`
  section's "Requirement N" lines, where the surrounding prose already states completion. Under D-01
  they reach `tox -e docs-pdf`, and neither typst-py's embedded fonts (Libertinus Serif / New
  Computer Modern) nor RTD's `fonts-noto-cjk` has emoji coverage; Typst's font fallback is silent, so
  the build would report success while rendering tofu. Removing them costs a light rewording of a
  historical release record and keeps both the PDF and GitHub's rendering clean.
  — **Reversibility:** reversible — text-only.

- **D-06: `Development Status` is deleted from the page.** `Migration Guides` and `Release Process` are
  corrected. Measured staleness on `docs/source/changelog.rst`: `Development Status` claims
  "**v0.3.x**: Current stable release / **v0.2.x**: Maintenance mode" — contradicting even the 0.4.0
  heading above it; `Migration Guides` stops at "Migrating from 0.2.x to 0.3.x", so the 0.6.x and
  0.7.0 emitted-`.typ` changes have no migration note anywhere in the manual; `Release Process` lists
  steps that no longer match `release.yml`. `Development Status` is deleted because it is a
  per-release hand-update site — precisely the drift channel D-01 exists to close. The other two are
  corrected in place: add 0.6.x and 0.7.0 migration entries, and restate `Release Process` against
  what `release.yml` actually does today.
  — **Reversibility:** reversible — prose.

### QUA-03 — the defect is already gone

- **D-07: QUA-03 closes on verification alone; no recurrence guard is added.** Measured during this
  discussion: `.planning/PROJECT.md` has **34 `<!--` and 34 `-->`**, and the todo's own depth-check
  script reports `final depth 0 OK`. A per-opener walk pairs every one of the 34. The two
  unterminated footers the todo recorded at commit `279aea5` (its lines 492 and 506) **do not exist
  at HEAD** — later milestone closes rewrote that footer tail and closed them incidentally. ROADMAP
  SC#4 ("zero unterminated `<!--`, checked by scanning the whole file") is therefore already true;
  there is nothing to repair.
  — **Reversibility:** reversible — a guard can be added later if the channel reopens.

- **D-08: Identify and record the commit that closed the two openers.** Bisect the depth check over
  `279aea5..HEAD` and name the commit(s) in the phase's evidence. Rationale the owner selected this
  for: it distinguishes "someone fixed it" from "it closed by accident", which is the evidence that
  justifies D-07's decision not to add a guard. If the closure turns out to be incidental, say so
  plainly in the record rather than reporting the requirement as deliberately repaired.
  — **Reversibility:** reversible — an evidence-file finding.

- **D-09: A naive `<!--` / `-->` count is NOT a valid check.** The scan must exclude prose and code
  spans. Measured across all **867** `.md` files under `.planning/`: a raw count flags 16 files, and
  the notable false positives are the two live planning documents that *describe QUA-03 itself* —
  `.planning/REQUIREMENTS.md:141` and `.planning/ROADMAP.md:731`, each carrying a backticked
  `` `<!--` `` inside prose. `*-RESEARCH.md` files likewise show "`-->` without `<!--`" because of
  ASCII arrows (`A --> B`) in diagrams. This is the same self-reference hazard
  `tests/test_no_stale_github_io_links.py` solved by splitting a literal across two fragments. Any
  script written for D-07/D-08 must walk openers and match each to the next closer, ignoring
  backticked spans and fenced blocks — not compare two counts.
  — **Reversibility:** reversible — a property of the checking script.

### Claude's Discretion

The owner did not select these two areas for discussion. Nothing here is locked by the owner; the
planner should decide on measured grounds. The DOC-11 default below was stated to the owner in the
final discussion turn and accepted along with the instruction to write this file.

- **DOC-11's documentation surface — default: three files, not one.** DOC-11's text names the README
  Quick Start. Measured staleness across the published surface after Phases 44 / 44.2:

  | File | Measured claim | Status after Phase 44 |
  |---|---|---|
  | `README.md` Quick Start (63-126) | no mention of `typst_documents` at all | incomplete |
  | `README.md:203` | "`typst_documents`: … — **required for PDF output**" | **false** |
  | `docs/source/quickstart.rst:60-67` | "Your First PDF" flow with `typst_documents` unset, then "Find your PDF in ``build/pdf/index.pdf``!" | **false** — the derived default writes `<project>.pdf` |
  | `docs/source/user_guide/configuration.rst:23-33` | "Define which documents to build" with no mention that the value is optional or derived | incomplete |

  Default decision: fix all four sites. Leaving `quickstart.rst` telling readers the wrong output
  path while repairing only the README would document *around* the defect, against the phase goal.
  `configuration.rst` gets the derived-default description added only — **do not touch the
  `title`/`author` element text Phase 44.2 wrote there**. `templates.rst` stays untouched
  (Phase 45.1). If the planner concludes the widening is unsafe, the fallback is README-only plus a
  filed todo for the two docs pages — but say so explicitly rather than silently narrowing.

- **QUA-02's refactor shape and how identity is proven.** Measured: `typsphinx/template_engine.py:131-137`
  and `:144-150` hold a **verbatim identical** four-line `logger.warning(...)`. ROADMAP SC#3 requires
  the warning come from exactly one site (verified by a grep over the function's branches) **and**
  that a build over the existing `lang` corpus produce warning-for-warning identical output against a
  pre-refactor baseline. Consequences the planner should carry: the message text must stay
  byte-identical (so the two rejection reasons must **not** be distinguished in the wording — that
  would change output and fail SC#3), and `tests/test_template_engine.py`'s `caplog` assertion pins
  that `repr(value)` appears in the warning, per the source todo. Open: whether the baseline is a
  recorded `45-GATE-EVIDENCE-*.md` artifact or captured inside a test, and whether the single site is
  a nested helper, an early-return guard, or a restructured single tail.

### Folded Todos

All four are already promoted to requirements by the v0.7.1 roadmap; they are listed here as the
source records downstream agents must read.

- `.planning/todos/pending/2026-08-04-docs-changelog-page-stale-at-0-4-0.md` → **DOC-12**
  (`resolves_phase: 45`). Frames the duplicate-vs-delegate question D-01 answers, and names the
  Development Status / Migration Guides staleness D-06 covers.
- `.planning/todos/pending/2026-07-25-derive-typst-lang-duplicated-warning-block.md` → **QUA-02**
  (`resolves_phase: 45`). Written in Japanese. Records Phase 27.1 review IN-01, why it was deferred,
  and the constraint that the `caplog` test pinning `repr(malformed)` must survive.
- `.planning/todos/pending/2026-07-29-project-md-unterminated-html-comments.md` → **QUA-03**
  (`resolves_phase: 45`). Its measured line numbers (492, 506 at `279aea5`) no longer correspond to
  anything at HEAD — see D-07. Its step 3 (a recurrence guard) is explicitly **not** adopted.
- `SEED-001-readme-quickstart-typst-documents-pdf` → **DOC-11** (already promoted; the seed itself is
  recorded in STATE.md's Pending Todos rather than as a file in `todos/pending/`).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements and roadmap
- `.planning/ROADMAP.md` §"Phase 45" — SC#1–SC#5, including SC#2's clause that the mechanism must make
  Phase 46's `0.7.1` entry a one-line addition, and SC#5's fence on `typsphinx/` behaviour change.
- `.planning/ROADMAP.md` §"Phase 45.1" — what is deliberately **not** here: `templates.rst`'s
  custom-template parameter contract (DOC-13).
- `.planning/REQUIREMENTS.md` — DOC-11, DOC-12, QUA-02, QUA-03 (lines 108–145), and the traceability
  rows mapping all four to Phase 45.

### Source todos
- `.planning/todos/pending/2026-08-04-docs-changelog-page-stale-at-0-4-0.md` — DOC-12.
- `.planning/todos/pending/2026-07-25-derive-typst-lang-duplicated-warning-block.md` — QUA-02.
- `.planning/todos/pending/2026-07-29-project-md-unterminated-html-comments.md` — QUA-03.

### Prior-phase decisions that constrain this one
- `.planning/phases/44-typst-documents-default-derivation-builder-input-hardening/44-CONTEXT.md` —
  D-01 (degenerate `project` keeps Sphinx's `'sphinx'` sentinel), D-04 (callable default registered
  exactly as `latex_documents` is), and **D-05**, which measured that the unset-config change is not
  only a rename: the emitted `.typ` gains the full template because the derived entry makes
  `root_doc` a master. DOC-11's README text must not describe it as a rename alone.
- `.planning/phases/44.2-typst-documents-title-and-author-consumption/44.2-CONTEXT.md` — the
  `entry[2]`/`[3]` precedence rules now live in `configuration.rst`; DOC-11 must not contradict or
  rewrite them.
- `.planning/STATE.md` §Blockers/Concerns — the REL-04 carry-over that makes D-02 load-bearing.

### REL-04 surface (read before touching `CHANGELOG.md`)
- `scripts/extract_changelog_section.py` — the Markdown `## [X.Y.Z]` section extractor.
- `.github/workflows/release.yml:72-79` and `:190-197` — the validate gate and the release-body wiring.
- `tests/test_changelog_extraction.py` — subprocess-level coverage; must stay green through D-03/D-04.

### Files under change
- `README.md` — Quick Start (63–126) and the Configuration Options list (203).
- `docs/source/changelog.rst` — the whole page.
- `docs/source/quickstart.rst:60-67, 71-90` — the "Your First PDF" flow and Configuration Options.
- `docs/source/user_guide/configuration.rst:23-33` — the `typst_documents` description.
- `CHANGELOG.md` — the 0.4.4 backfill (D-03), the `[Unreleased]` merge (D-04), the `✅` removal (D-05).
- `pyproject.toml` — the `docs` extra (myst-parser).
- `typsphinx/template_engine.py:131-150` — QUA-02.
- `.planning/PROJECT.md` — QUA-03 (verification only; no edit expected).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `tests/test_no_stale_github_io_links.py` — the established shape for a repo-hygiene pytest module:
  parses raw file text, no network, and deliberately splits a literal to avoid matching itself. It is
  the reference if any checking script is written for D-08/D-09, and it is precedent that this repo
  accepts non-code files being guarded by the shipped suite.
- `scripts/extract_changelog_section.py` + `tests/test_changelog_extraction.py` — the existing,
  hand-verified CHANGELOG parsing surface. D-03 and D-04 must leave both intact.
- `.planning/todos/pending/2026-07-29-project-md-unterminated-html-comments.md` §Solution — carries a
  runnable depth-check one-liner. Note D-09: it is the naive count, and it false-positives on
  `REQUIREMENTS.md` and `ROADMAP.md`.

### Established Patterns
- **Docs build twice.** `tox -e docs-html` (furo) and `tox -e docs-pdf` (`sphinx-build -b typstpdf`,
  dogfooding this extension). Anything added to `docs/source/` must survive typsphinx's own
  translator, not just Sphinx's HTML writer. Neither environment passes `-W`, so warnings do not fail
  the build — SC#2's "build clean" needs an explicit reading.
- **`CHANGELOG.md` structure measured for D-01:** `#` ×1, `##` ×19, `###` ×54, `####` ×7, `---`
  transition ×3, `✅` ×25, 939 lines. `typsphinx/translator.py:5803` has `visit_transition`, so the
  `---` rules have a handler; the deep heading nesting under an `include` still needs a real build to
  confirm.
- **Two-repository i18n.** `docs/source/conf.py` sets `locale_dirs = ["../locale/"]`, and that catalog
  lives in the separate `typsphinx-doc-translations` repository, not here. Every line D-01 newly
  surfaces on the changelog page will render **untranslated on the `ja` site** until that repo's
  catalogs are regenerated. This is a known consequence, not a blocker — but it should be stated in
  the phase record rather than discovered at the milestone close.
- **RTD installs the `docs` extra** (`.readthedocs.yaml` → `uv sync --extras docs`), so adding
  `myst-parser` there is sufficient for the published build; no separate RTD change is needed.

### Integration Points
- `docs/source/index.rst:66` lists `changelog` in the toctree — the page is a toctree child, so under
  the `typstpdf` builder it is an `#include()`d document subject to Phase 44.1's relative heading
  depth. Verify the included Markdown's heading levels land sanely in the PDF outline.
- `README.md:203`'s "required for PDF output" and `docs/source/quickstart.rst`'s
  `build/pdf/index.pdf` are the two places where the published text is now *actively false* rather
  than merely incomplete. They are the sharpest DOC-11 targets.

</code_context>

<specifics>
## Specific Ideas

- The owner opened the DOC-12 discussion by proposing that converting `CHANGELOG.md` to
  reStructuredText would be "more principled" than adding a Markdown parser, then accepted the
  myst-parser include once the REL-04 blast radius was measured. Record this so a later reader does
  not re-propose the rST conversion: the objection is not aesthetic, it is that the GitHub Release
  body is Markdown and REL-04 is unproven.
- The owner consistently chose the option that removes a hand-update site rather than the option that
  refreshes its contents (delegate over duplicate; delete `Development Status` rather than restate
  it). Where a further such choice arises during planning, that is the established preference.
- The owner declined to add a recurrence guard for QUA-03 but asked for the *cause* of the closure to
  be identified — evidence over mechanism, for a channel that has not actually recurred.

</specifics>

<deferred>
## Deferred Ideas

- **A `.planning/` comment-balance guard** (the QUA-03 todo's step 3). Considered and declined at
  D-07. If the drift channel reopens, D-09 records the design constraint the guard would have to
  satisfy.
- **`docs/source/user_guide/templates.rst`'s custom-template parameter contract** — Phase 45.1 /
  DOC-13. Explicitly out of bounds here.
- **The `## [0.7.1]` CHANGELOG entry and its two user-visible callouts** (CONF-08's rename +
  CONF-09's title/author wiring) — Phase 46.
- **Regenerating the `ja` catalogs for the newly-surfaced changelog content** — lives in the
  `typsphinx-doc-translations` repository, outside this repo's phase scope. Flag it at the milestone
  close.

</deferred>

---

*Phase: 45-documentation-currency-carried-hygiene*
*Context gathered: 2026-08-09*
