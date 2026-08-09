# Phase 45: Documentation Currency + Carried Hygiene - Research

**Researched:** 2026-08-09
**Domain:** Sphinx/docutils documentation tooling (myst-parser Markdown-in-rST include), CHANGELOG/release-notes format contracts, Python logging refactor, planning-doc HTML-comment hygiene
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**DOC-12 — the changelog page mechanism:**
- **D-01:** The page delegates to `CHANGELOG.md` via a myst-parser `include`, rather than duplicating
  release history in reStructuredText. `docs/source/changelog.rst` shrinks to its framing sections
  plus an include of the repository's `CHANGELOG.md`, parsed as Markdown (`.. include::
  ../../CHANGELOG.md` with `:parser:`; MyST's documented `myst_parser.sphinx_` parser is the starting
  candidate — confirm the exact spelling, whether the extension must also be listed in `extensions`,
  and the minimum `myst-parser` version at research time). `myst-parser` is added to the **`docs`
  extra only** — the standing zero-new-**runtime**-dependency invariant is untouched.
- **D-02:** `CHANGELOG.md` stays Markdown. Converting it to reStructuredText was proposed and
  withdrawn on measurement — `CHANGELOG.md` is REL-04's supply source for the GitHub Release body,
  which GitHub renders as Markdown, and REL-04 has never run green end to end.
- **D-03:** The missing `## [0.4.4]` section is reconstructed and added to `CHANGELOG.md`, with its
  `[0.4.4]:` link-reference line. Reconstruct from the `v0.4.3..v0.4.4` commit range and the existing
  GitHub Release for `v0.4.4`. Must not disturb `extract_changelog_section.py`'s parse of any other
  section.
- **D-04:** The duplicate `## [Unreleased]` is merged into the single one at the top of the file. Fold
  line 911's content into the top-of-file `[Unreleased]` (or drop if stale) and delete the second
  heading. Confirm `extract_changelog_section.py` is unaffected.
- **D-05:** The 25 `✅` characters are removed from `CHANGELOG.md` (the `0.1.0b1` section's
  "Requirement N" lines) — neither typst-py's embedded fonts nor RTD's `fonts-noto-cjk` has emoji
  coverage, so `tox -e docs-pdf` would render tofu.
- **D-06:** `Development Status` is deleted from the page; `Migration Guides` and `Release Process`
  are corrected in place (add 0.6.x/0.7.0 migration entries; restate `Release Process` against what
  `release.yml` actually does today).

**QUA-03 — the defect is already gone:**
- **D-07:** QUA-03 closes on verification alone; no recurrence guard is added. Measured during the
  discussion: 34 `<!--` / 34 `-->`, final depth 0 OK, the two footers the todo recorded at `279aea5`
  do not exist at HEAD.
- **D-08:** Identify and record the commit that closed the two openers (bisect `279aea5..HEAD`), to
  distinguish "someone fixed it" from "it closed by accident."
- **D-09:** A naive `<!--`/`-->` count is NOT a valid check — the scan must exclude prose and code
  spans. `REQUIREMENTS.md:141` and `ROADMAP.md:731` are known false-positive sites (backticked
  `` `<!--` `` inside prose describing QUA-03 itself).

### Claude's Discretion

- **DOC-11's documentation surface — default: three files, not one** (README Quick Start +
  `docs/source/quickstart.rst` + `docs/source/user_guide/configuration.rst`). `configuration.rst`
  gets the derived-default description added only — do not touch the `title`/`author` element text
  Phase 44.2 wrote there. `templates.rst` stays untouched (Phase 45.1). Fallback if widening is
  judged unsafe: README-only plus a filed todo for the two docs pages — but say so explicitly.
- **QUA-02's refactor shape and how identity is proven.** The message text must stay byte-identical
  (the two rejection reasons must NOT be distinguished in wording — that would change output and fail
  SC#3); `tests/test_template_engine.py`'s `caplog` assertion pins that `repr(value)` appears in the
  warning. Open: nested helper vs. early-return guard vs. restructured single tail; whether the
  baseline is a recorded evidence artifact or captured inside a test.

### Deferred Ideas (OUT OF SCOPE)

- A `.planning/` comment-balance guard (the QUA-03 todo's step 3) — considered and declined at D-07.
- `docs/source/user_guide/templates.rst`'s custom-template parameter contract — Phase 45.1 / DOC-13.
- The `## [0.7.1]` CHANGELOG entry and its two user-visible callouts (CONF-08's rename + CONF-09's
  title/author wiring) — Phase 46.
- Regenerating the `ja` catalogs for the newly-surfaced changelog content — lives in the
  `typsphinx-doc-translations` repository, outside this repo's phase scope. Flag at milestone close.
- Converting `CHANGELOG.md` away from Markdown — measured and rejected (D-02).
- Editing `docs/source/user_guide/templates.rst` — Phase 45.1's SC#2 must *check* the published
  contract, not inherit an edit this phase made to it.
- Any `typsphinx/` behaviour change beyond QUA-02's single-site warning refactor (ROADMAP SC#5).
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-------------------|
| DOC-11 | The README Quick Start states what `typst_documents` does, when it must be set — including the CONF-08 derived default and the fact that an explicit setting overrides it — so a reader following the Quick Start exactly is not surprised by the output filename or by which documents become PDFs. | `_default_typst_documents()` read verbatim (Code Examples) gives the exact derivation formula and precedence rule; measured-false claims at `README.md:203`, `docs/source/quickstart.rst:67`, `docs/source/user_guide/configuration.rst:23-33` line-numbered; existing `tests/fixtures/default_typst_documents_gate/` + `tests/test_default_typst_documents_gate.py` identified as the reusable real-build verification pattern (Validation Architecture). |
| DOC-12 | The published documentation's changelog page carries every release through v0.7.1 (`docs/source/changelog.rst` is frozen at 0.4.0; 12 releases are missing). | myst-parser `include::` `:parser: myst_parser.sphinx_` syntax verified against two official doc pages; version floor `>=5.0` verified live against PyPI registry JSON; full translator node-coverage check against `typsphinx/translator.py` found no gaps; exact CHANGELOG.md line numbers for D-03/D-04/D-05 edits measured; REL-04 extractor's positional (name-agnostic) algorithm confirmed safe against both edits. |
| QUA-02 | `derive_typst_lang()`'s rejection-path warning is emitted from one place rather than duplicated verbatim across its two rejection branches, with no change to the warnings a build produces. | Full function source read verbatim with exact line numbers (132-136, 144-148); existing `caplog` test and GATE-01 real-build corpus (`tests/test_typst_lang_gate.py`) confirmed sufficient to prove warning-for-warning identity without new test infrastructure; illustrative single-tail-warning refactor shape provided. |
| QUA-03 | `.planning/PROJECT.md` contains no unterminated HTML comment — both `<!--` openers in the archived-footer tail are closed, so no downstream reader silently swallows the rest of the file. | Independently re-measured this session with a D-09-compliant (fence/backtick-aware) opener-stack script: zero unterminated openers confirmed. D-08's bisect commit found and read verbatim (`43a2a78`, Phase 41 plan 03, deliberate fix named "D-13") — stronger and more certain than CONTEXT.md's own framing. |
</phase_requirements>

## Summary

This phase is almost entirely a *verification* phase, not a *design* phase — CONTEXT.md's D-01..D-09
already lock every decision the owner cares about. Research here confirms feasibility and fills in
exact mechanics so the planner can write literal task steps rather than re-derive them.

**DOC-12 (myst-parser include):** confirmed working and documented. `docutils`'s `include` directive
accepts a `:parser:` option (requires `docutils>=0.17`, `[CITED: myst-parser docs]`); inside a Sphinx
build the correct dotted path is `myst_parser.sphinx_` (not `myst_parser.docutils_`, which is the
plain-docutils variant), i.e. `.. include:: ../../CHANGELOG.md\n   :parser: myst_parser.sphinx_`. The
one open question CONTEXT.md flagged — minimum `myst-parser` version — resolves to **`myst-parser>=5.0`**:
version 4.x caps `sphinx<9` and `docutils<0.22` (both violated by this repo's pins,
`sphinx>=9.1,<10` / `docutils>=0.21,<0.23`), while the latest release, **5.1.0** (uploaded
2026-05-13), declares `docutils>=0.20,<0.23` and `sphinx>=8,<10` — both compatible
`[VERIFIED: PyPI registry JSON, https://pypi.org/pypi/myst-parser/json]`. Every docutils node type a
Markdown-sourced `CHANGELOG.md` doctree will produce (`section`, `title`, `paragraph`, `bullet_list`,
`list_item`, `strong`, `emphasis`, `literal`, `literal_block`, `block_quote`, `reference`, `target`,
`transition`, `comment`) already has a `visit_*`/`depart_*` pair in `typsphinx/translator.py`
`[VERIFIED: typsphinx/translator.py, see Code Examples]` — myst-parser's whole design point is
targeting the *same* docutils AST an RST parse produces, so this is not a new translator-coverage
gap. One genuinely new, non-obvious mechanic worth flagging: CommonMark resolves `[0.7.0]` inside a
heading text as a **shortcut reference link** wherever a matching `[0.7.0]: url` reference definition
exists later in the same document — and `CHANGELOG.md` has exactly that block at its tail. Every
version heading will therefore render as a clickable link to its GitHub release tag once included,
which is a harmless (arguably pleasant) side effect but changes the heading's node shape from plain
text to a `reference`-wrapped title — worth a real-build spot check, not a blocker.

**DOC-12 (CHANGELOG.md structure):** every measured fact in CONTEXT.md's D-02..D-06 was independently
re-verified this session (see Architecture Patterns / Code Examples for exact line numbers). The
missing `## [0.4.4]` section belongs between `## [0.5.0]` (line 377) and `## [0.4.3]` (line 404);
`v0.4.4` (tagged 2026-07-05, 148 commits over `v0.4.3..v0.4.4`) was a CI/release-durability milestone
(dependency drift detection, Dependabot grouping, `softprops/action-gh-release` v2→v3,
`uv sync --locked`, Python floor bump, GitHub Actions artifact bump to Node 24) — material for the
reconstructed entry is in Code Examples. The duplicate `## [Unreleased]` sits at line 8 (empty,
top-of-file placeholder) and line 911 ("Planned for Future Releases", inside the physically-misordered
`## [0.2.0]` section that sits *after* `## [0.1.0b1]` in file order). The 25 `✅` characters are two
identical 12/13-line "Requirements Status" blocks at lines 801-813 and 889-901.

**REL-04 surface:** `scripts/extract_changelog_section.py`'s extraction algorithm is **purely
positional** — it matches ANY `^## \[...\]` heading (deliberately including both `[Unreleased]`
headings) and slices to the next such heading, never inspecting heading *names*. This means D-03
(insert `## [0.4.4]`) and D-04 (merge the duplicate `[Unreleased]`) are both safe by construction —
the extractor cannot be confused by either edit, and `tests/test_changelog_extraction.py` already has
a dedicated regression test (`test_unreleased_headings_do_not_leak`) proving this. No changes are
needed to the extractor or `release.yml`.

**QUA-02:** `derive_typst_lang()` lives at `typsphinx/template_engine.py:84-149`. Its two rejection
branches (`logger.warning` calls at lines 132-136 and 144-148) are byte-identical four-line calls.
The pinning test (`tests/test_template_engine.py::TestDeriveTypstLang::test_malformed_inputs_return_none_and_warn`)
asserts `any(repr(malformed) in record.message for record in caplog.records)` — it does not pin a
message *count*, so a single-tail-warning restructure (both branches fall through to one
`logger.warning(...)` call at the function's end) satisfies both the existing unit test and ROADMAP
SC#3's "exactly one site" grep requirement without changing wording. The full "lang test corpus" is
two files: `tests/test_template_engine.py::TestDeriveTypstLang` (unit-level, `caplog`) and
`tests/test_typst_lang_gate.py` (GATE-01, five real-`sphinx-build` fixture classes, including a
dedicated `TestMalformedLanguage` class that already builds `MALFORMED_LANGUAGE_FIXTURE_DIR` through
`-b typstpdf` and asserts the build does not abort).

**QUA-03:** independently re-measured this session with a script that (per D-09) excludes fenced code
blocks and inline-backtick spans before pairing openers to closers: **zero unterminated `<!--`** in
`.planning/PROJECT.md` (34 openers, 34 closers, stack empty at EOF) — confirms D-07's conclusion.
Better than D-08 asked for: the closing commit is identified with certainty and it was **deliberate,
not incidental** — `43a2a78` ("`docs(41-03): terminate PROJECT.md's two unterminated HTML comments
(D-13)`", Phase 41 plan 03, 2026-08-03) closed exactly the two openers the source todo named (moved
by file growth to lines 761/775 by that point), with a commit message that states the before/after
counts (31/31 post-fix) and names the fix as its own decision D-13. CONTEXT.md's phrasing ("closed
them incidentally") should be corrected in the phase record — it was a deliberate, attributed repair.

**Primary recommendation:** Add `myst-parser>=5.0` to the `docs` extra only, delegate
`docs/source/changelog.rst` via `.. include:: ../../CHANGELOG.md\n   :parser: myst_parser.sphinx_`
after making D-03/D-04/D-05's edits to `CHANGELOG.md` first (so the include's start point/line count
is measured against the final file), add `myst_parser` to `docs/source/conf.py`'s `extensions` list
defensively, do the QUA-02 single-tail-warning restructure, and treat QUA-03 as verification-only —
report D-07/D-08's findings (with the corrected "deliberate, not incidental" framing) rather than
editing any file.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Changelog page rendering (HTML + PDF) | Docs/Static build (Sphinx) | — | `docs/source/changelog.rst` is a Sphinx source file; myst-parser is a Sphinx/docutils parser plugin, not a runtime dependency of `typsphinx` itself |
| `typst_documents` documentation accuracy | Docs/Static build (Sphinx) | — | README.md and `docs/source/*.rst` are prose, not code; DOC-11 only ever edits documentation files |
| `derive_typst_lang()` warning consolidation | Library / Backend (`typsphinx` package) | — | `typsphinx/template_engine.py` is the extension's own Python code, invoked at Sphinx build time |
| `.planning/PROJECT.md` comment hygiene | Planning-record / Repo hygiene | — | Not part of the shipped package or its docs; a project-management artifact only |
| CHANGELOG.md as GitHub Release source (REL-04) | Release / CI (GitHub Actions) | Docs/Static build | Same file serves two consumers: `release.yml`'s `extract_changelog_section.py` (CI tier) and the myst-parser include (docs tier) — D-01/D-02 exist precisely to keep those two tiers reading one shared source rather than diverging copies |

## Package Legitimacy Audit

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| `myst-parser` | PyPI | latest release 5.1.0 uploaded 2026-05-13; project itself has shipped since 2020 (0.x series visible back to 2020-2023 in registry history) | Automated seam reported `unknown-downloads` (its downloads API call returned null) → raw `SUS` verdict. **Independently cross-checked** via WebSearch/pypistats: ~1.5M downloads/week, ~7.1M/month `[CITED: pypistats.org, via WebSearch]` — this is one of the most widely used Sphinx ecosystem packages (part of the executablebooks/Jupyter Book family) | `github.com/executablebooks/MyST-Parser` | SUS (automated) / **effectively OK on independent verification** | Approved — planner should still add a lightweight `checkpoint:human-verify` before the `pyproject.toml` edit per protocol, but the audit finding is that the `SUS` flag is a downloads-API data gap, not a genuine legitimacy signal |

**Packages removed due to `[SLOP]` verdict:** none.
**Packages flagged as suspicious `[SUS]`:** `myst-parser` — flagged only because the legitimacy-check seam's downloads lookup returned `null`, not because of any adverse signal (source repo present, non-deprecated, `unknown-downloads` is its sole listed reason). Real download-volume data (WebSearch/pypistats, ~1.5M/week) contradicts the automated flag. Still gate the install behind `checkpoint:human-verify` per protocol, but the planner and executor should not treat this as a real red flag.

*`myst-parser` was discovered via WebSearch/training knowledge and the exact version floor was confirmed against the live PyPI registry JSON this session — the package name itself is tagged `[ASSUMED]` per the package-name provenance rule even though registry existence and the version constraints are `[VERIFIED]`.*

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `myst-parser` | `>=5.0` (latest 5.1.0, verified 2026-08-09) | Parses `CHANGELOG.md`'s Markdown into a docutils doctree so `docs/source/changelog.rst`'s `include::` directive can render it | The canonical, de-facto-only actively maintained Markdown-in-Sphinx parser; already the mechanism CONTEXT.md D-01 locked |

**Version verification:** `[VERIFIED: PyPI registry JSON, https://pypi.org/pypi/myst-parser/json — fetched live 2026-08-09]`. `requires_dist` for 5.1.0: `docutils<0.23,>=0.20`, `sphinx<10,>=8`. typsphinx pins `sphinx>=9.1,<10` and `docutils>=0.21,<0.23` — both intersect cleanly with 5.1.0's range. **Do not pin `myst-parser>=4.0`** (or leave the floor unstated and let the resolver pick an old cached wheel) — 4.x's `requires_dist` caps `sphinx<9` and `docutils<0.22`, both of which this repo's pins violate `[CITED: WebSearch summarizing myst-parser 4.0 release notes]`.

**Installation:**
```bash
# Added to pyproject.toml's [project.optional-dependencies] "docs" extra only —
# NOT to [project].dependencies (zero-new-runtime-dependency invariant, D-01).
docs = [
    "furo>=2024.0",
    "sphinx-autodoc-typehints>=1.0",
    "sphinx-intl>=2.0",
    "myst-parser>=5.0",
]
```
Then regenerate `uv.lock` (`uv lock`) so the `docs` extra's resolved set is committed, exactly as the
existing three `docs`-extra packages already are.

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| (none — `myst-parser` has no companion package needed for this single-directive use case; `linkify-it-py` and other `myst-parser` extras are for MyST-native `.md` source files, not the `include::`-only pattern this phase uses) | — | — | — |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `myst-parser` include (D-01) | Hand-maintained rST duplicate of every release | Rejected by the owner and D-01 both — this is the exact drift channel that produced the 12-releases-missing defect this phase exists to close |
| `myst-parser` include (D-01) | Convert `CHANGELOG.md` itself to reStructuredText (D-02) | Rejected — GitHub renders Release bodies as Markdown, and `CHANGELOG.md` is REL-04's supply source; converting would degrade GitHub Release rendering and force re-proving an unproven extractor rewrite alongside REL-04's own first real proof |
| `.. include:: ../../CHANGELOG.md` with `:parser: myst_parser.sphinx_` | `:parser: myst_parser.docutils_` | `myst_parser.docutils_` is the plain-docutils (non-Sphinx) parser variant, documented separately from the Sphinx variant `[CITED: MyST-Parser docs/docutils.md vs myst-parser.readthedocs.io FAQ]` — using it inside a Sphinx build risks the parser not seeing Sphinx's `app.config` (myst config values), so `myst_parser.sphinx_` is the correct choice for this Sphinx-driven repo |

## Architecture Patterns

### System Architecture Diagram

```
CHANGELOG.md (repo root, Markdown, Keep-a-Changelog format)
        |
        |  read by TWO independent consumers, never diverging (D-01/D-02):
        |
        +--> [CI tier] scripts/extract_changelog_section.py
        |         |  regex: ^## \[(?P<version>[^\]]+)\]   (positional, name-agnostic)
        |         v
        |    .github/workflows/release.yml
        |      validate job  --(existence/non-empty check)-->  abort tag push if missing
        |      create-release job --(body)--> GitHub Release (REL-04)
        |
        +--> [Docs tier] docs/source/changelog.rst
                  |  .. include:: ../../CHANGELOG.md
                  |     :parser: myst_parser.sphinx_
                  v
             myst-parser (Markdown -> docutils doctree, same node classes as RST)
                  |
                  +--> tox -e docs-html  (Sphinx HTML builder, furo theme)
                  |
                  +--> tox -e docs-pdf   (sphinx-build -b typstpdf)
                            |
                            v
                       TypstWriter.translate()
                         _is_master_document("changelog") == False
                         (only "index" is in docs/source/conf.py's typst_documents)
                            |
                            v
                       changelog reached via toctree (docs/source/index.rst:66)
                       -> emitted as an #include()'d document, NOT a master
                       -> subject to Phase 44.1's relative heading-depth fix
                            |
                            v
                       TypstTranslator.visit_*/depart_*  (per-node conversion)
                         section/title/paragraph/bullet_list/list_item/
                         strong/emphasis/literal/literal_block/block_quote/
                         reference/target/transition/comment -- ALL already
                         have handlers (verified below)
                            |
                            v
                       typst.compile() -> compiled master PDF's included content
```

### Recommended Project Structure

No new directories. Files touched:

```
CHANGELOG.md                                  # D-03 backfill, D-04 merge, D-05 emoji removal
docs/source/changelog.rst                     # shrinks to framing sections + include (D-01, D-06)
docs/source/quickstart.rst                    # DOC-11: fix "Your First PDF" default-output claim
docs/source/user_guide/configuration.rst      # DOC-11: add derived-default description
README.md                                     # DOC-11: Quick Start + Configuration Options list
pyproject.toml                                # myst-parser added to [project.optional-dependencies].docs
uv.lock                                        # regenerated after the pyproject.toml edit
typsphinx/template_engine.py                  # QUA-02: derive_typst_lang() single-site warning
.planning/PROJECT.md                          # QUA-03: verification only, no edit expected (D-07)
```

### Pattern 1: Markdown-in-rST include via `:parser:`

**What:** The docutils `include` directive accepts a `:parser:` option naming a dotted path to an
alternate parser class; when the path is `myst_parser.sphinx_`, the included file's content is parsed
as MyST Markdown instead of reStructuredText, and the resulting doctree is spliced into the parent
document at the include site.

**When to use:** Delegating a single non-MyST-native page (here, an `.rst` page) to a Markdown source
of truth, without converting the whole Sphinx project to MyST.

**Example:**
```rst
.. Source: myst-parser FAQ, https://myst-parser.readthedocs.io/en/latest/faq/index.html
.. and organising_content.html, both fetched 2026-08-09.
.. include:: ../../CHANGELOG.md
   :parser: myst_parser.sphinx_
```
Requires `docutils>=0.17` (this repo pins `>=0.21,<0.23`, well above the floor) `[CITED: myst-parser
docs, "The parser option requires docutils>=0.17"]`. Add `myst_parser` to `docs/source/conf.py`'s
`extensions` list defensively — the parser module reads Sphinx `app.config` for MyST settings
(`myst_enable_extensions`, `myst_heading_anchors`, etc.), and while the FAQ text does not explicitly
require the extension registration for the bare `include::` use case, every worked example in the
official docs shows `extensions = ["myst_parser"]` present, and omitting it risks an `AttributeError`
reading an unregistered config value — this exact question (CONTEXT.md D-01: "confirm... whether the
extension must also be listed in extensions") should be settled with a one-line real-build check
during Wave 1 rather than assumed either way `[ASSUMED — recommend registering it]`.

### Pattern 2: Positional (not name-based) CHANGELOG section extraction

**What:** `scripts/extract_changelog_section.py`'s `_SECTION_HEADER_RE = re.compile(r"^## \[(?P<version>[^\]]+)\]")`
matches on structural shape only. `extract_section()` finds the first `## [<requested version>]` line,
then slices to the *next* line matching the same regex (any heading, any name), or EOF.

**When to use:** This is why D-03 (insert `## [0.4.4]`) and D-04 (merge the duplicate
`## [Unreleased]`) cannot break `REL-04`'s extraction — the algorithm never special-cases heading text,
so a second `## [Unreleased]` heading existing (today) or not existing (after D-04) is irrelevant to
any *numbered*-version extraction.

**Example:**
```python
# Source: scripts/extract_changelog_section.py:87-116 (read verbatim this session)
lines = changelog_text.splitlines()
start_index: int | None = None
for index, line in enumerate(lines):
    match = _SECTION_HEADER_RE.match(line)
    if match and match.group("version") == version:
        start_index = index + 1
        break
# ... end_index = the next _SECTION_HEADER_RE match after start_index, or len(lines)
```

### Pattern 3: Single-tail-warning consolidation (QUA-02)

**What:** `derive_typst_lang()` currently has two early-return rejection branches, each ending its own
copy of the same four-line `logger.warning(...)` call. To satisfy "exactly one site" (grep-verifiable)
while keeping the warning text byte-identical (SC#3's "warning-for-warning identical" bar), restructure
so both rejection paths fall through to a single tail call instead of each calling `logger.warning`
independently.

**Example (illustrative only — not verbatim source, a suggested refactor shape for the planner):**
```python
# Illustrative restructure -- planner/executor decides exact shape (nested
# helper vs. early-return guard vs. this tail form); the constraint is ONE
# call site and byte-identical wording (CONTEXT.md D under "Claude's Discretion").
def derive_typst_lang(sphinx_language: str | None) -> str | None:
    if isinstance(sphinx_language, str) and sphinx_language:
        head = re.split(r"[_\-@]", sphinx_language, maxsplit=1)[0].lower()
        if re.fullmatch(r"[a-z]{2,3}", head):
            return head
    logger.warning(
        f"typsphinx: could not derive a Typst 'lang' from Sphinx "
        f"'language' = {sphinx_language!r} -- omitting 'lang' (falling "
        f"back to the template's own default)."
    )
    return None
```
This shape is confirmed compatible with the existing pinning test
(`tests/test_template_engine.py:1202-1216`), which only asserts `any(repr(malformed) in
record.message for record in caplog.records)` — not a call count — and with
`tests/test_typst_lang_gate.py::TestMalformedLanguage`, which never inspects warning text at all
(deliberately, per that module's own docstring: "the warning is emitted through a stdlib module
logger... its presence in a subprocess's output is not a contract worth pinning here").

### Anti-Patterns to Avoid

- **Special-casing `"Unreleased"` inside `extract_changelog_section.py` "to be safe."** The module's
  own docstring explicitly forbids this (`"Do NOT 'fix' this by special-casing the string
  'Unreleased' anywhere in this module"`) — the positional algorithm already handles both headings
  correctly, and adding a name check would be unnecessary surface area this phase must not touch
  (out of scope per ROADMAP SC#5).
- **Editing `docs/source/user_guide/templates.rst`.** Explicitly out of bounds — CONTEXT.md and
  ROADMAP both fence this to Phase 45.1 / DOC-13.
- **Adding a `.planning/` comment-balance recurrence guard.** Explicitly declined at D-07 — QUA-03
  closes on verification alone this phase.
- **Reordering `CHANGELOG.md`'s `## [0.2.0]` (line 840) to sit chronologically before `## [0.1.0b1]`
  (line 667).** This physical mis-ordering is real (measured this session) but is NOT named in any
  D-decision or requirement — do not "fix" it as a drive-by; it is out of this phase's scope and any
  reordering risks disturbing `extract_changelog_section.py`'s positional slicing for both sections
  (file-order changes DO matter to the extractor, unlike heading names).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Markdown → docutils/Typst rendering | A custom Markdown-to-rST or Markdown-to-Typst converter for just this one file | `myst-parser`'s `include::` `:parser:` mechanism | `typsphinx/translator.py` already speaks docutils nodes fluently; myst-parser produces exactly those nodes, so zero new translator code is needed — a hand-rolled converter would duplicate translator logic for no benefit |
| CHANGELOG section extraction for release notes | A second parser/regex inside this phase's work | The existing, tested `scripts/extract_changelog_section.py` | D-02's whole rationale: REL-04 has never run green end-to-end, and this script is the one committed, pytest-covered implementation `release.yml` actually calls — do not add a second, divergent copy |
| PROJECT.md comment-balance checking | A naive `<!--`/`-->` count comparison | An opener-stack walk that skips fenced code blocks (` ``` `) and inline backtick spans before pairing tokens | D-09: the naive count (34/34) happens to be correct here, but a raw count structurally cannot distinguish "34 real openers, 34 real closers" from "one real opener, one real closer, plus 33 false-positive pairs inside prose/fences" — `REQUIREMENTS.md:141` and `ROADMAP.md:731` are measured false-positive sites for exactly this reason |

**Key insight:** every mechanism this phase needs already exists in the repo or the Python/Sphinx
ecosystem (myst-parser for Markdown-in-rST, the existing extractor script for release notes, a
backtick/fence-aware scan for comment balance) — the work is wiring and verification, not invention.

## Common Pitfalls

### Pitfall 1: Editing `CHANGELOG.md` after measuring the include's start point

**What goes wrong:** If the planner decides to skip `CHANGELOG.md`'s own preamble (lines 1-7: `#
Changelog` + Keep-a-Changelog/SemVer attribution, which duplicates `changelog.rst`'s own existing
preamble almost verbatim) via `:start-line:`, and that line number is measured *before* D-03/D-04/D-05
edit the file, the offset will be wrong once those edits land (D-03 inserts a whole new section;
D-04 deletes a duplicate heading and its content; D-05 removes 25 characters but not lines, unless
the emoji removal also reflows lines).

**Why it happens:** Ordering — measuring against a file that is about to change.

**How to avoid:** Do the D-03/D-04/D-05 `CHANGELOG.md` edits first (they are all inside the file
CHANGELOG.md itself and don't depend on the include), then measure the final preamble line count for
the `:start-line:`/`:start-after:` option, then write `docs/source/changelog.rst`'s include directive.

**Warning signs:** `tox -e docs-html`/`tox -e docs-pdf` render the "Changelog" title twice, or a
Sphinx duplicate-heading warning about `## [Unreleased]` if start-line was measured off-by-N.

### Pitfall 2: Assuming "build clean" means zero output

**What goes wrong:** ROADMAP SC#2 says "both `tox -e docs-html` and `tox -e docs-pdf` build the page
clean." Neither tox environment passes `-W` `[VERIFIED: tox.ini:53-76, read this session — the
`commands` for both `docs-html` and `docs-pdf` are a bare `sphinx-build -b <builder> source
<out>`, no `-W` flag]`, so a build that emits warnings still exits 0 — "clean" cannot be verified by
exit code alone.

**Why it happens:** The natural instinct is `echo $?` after the tox run.

**How to avoid:** Capture stderr/stdout from both `sphinx-build` invocations and grep for `WARNING:`
lines mentioning `changelog` (or count total warning lines before/after the phase's changes as a
delta, since some warnings — e.g. the toctree docstring defect noted in `28-VERIFICATION.md`'s prior
evolution log — are pre-existing and out of this phase's fence).

**Warning signs:** A green tox run that still silently drops content (e.g. an `unknown_visit` warning
for a myst-specific node type this session did not find any evidence of, but which should still be
checked empirically against a real build per the phase's own success-criterion wording).

### Pitfall 3: Treating the "SUS" package-legitimacy verdict as a real red flag

**What goes wrong:** The automated `package-legitimacy check` seam returned `SUS` for `myst-parser`
with reason `unknown-downloads` — its downloads-API lookup returned `null`, not a low number. Treating
this as "this package looks suspicious" and second-guessing the choice would waste planning effort on
a false signal.

**Why it happens:** The seam's verdict logic doesn't distinguish "data unavailable" from "data shows
low legitimacy" in its summary label.

**How to avoid:** Cross-check independently (this session: WebSearch/pypistats showed ~1.5M
downloads/week) before treating a `SUS` verdict as blocking. Still add the protocol-required
`checkpoint:human-verify` before the `pyproject.toml` edit, but the plan/gate evidence should record
that the flag was investigated and found to be a data-availability artifact, not a genuine concern.

### Pitfall 4: Re-litigating QUA-03 as "needs a fix"

**What goes wrong:** The requirement text (REQUIREMENTS.md line 141-143) still reads as if the two
comments need closing ("both `<!--` openers in the archived-footer tail are closed"). An executor
who does not read CONTEXT.md's D-07 closely might go looking for unterminated comments to fix and,
finding none, could either (a) correctly report "already fixed" or (b) incorrectly assume they missed
something and start "fixing" false-positive matches inside prose (`REQUIREMENTS.md:141`,
`ROADMAP.md:731` — both carry a backticked `` `<!--` `` describing this very requirement).

**Why it happens:** Requirement text predates the discussion-session discovery that the defect was
already repaired in Phase 41.

**How to avoid:** The plan's QUA-03 task should be framed explicitly as "run the verification script,
record zero unterminated openers, record the D-08 bisect finding (commit `43a2a78`, deliberate, not
incidental) — no file edit expected," matching D-07/D-08/D-09 rather than the requirement's original
"close the two openers" framing.

## Code Examples

Verified patterns from official sources and this repo's own code, read this session:

### myst-parser include directive (official docs)

```rst
.. Source: https://myst-parser.readthedocs.io/en/latest/faq/index.html
.. and https://myst-parser.readthedocs.io/en/latest/syntax/organising_content.html
.. (both fetched via WebFetch 2026-08-09)
.. include:: include.md
   :parser: myst_parser.sphinx_
```
Quoted verbatim from the fetch: *"The `parser` option requires `docutils>=0.17`."* The
non-Sphinx-project variant (`docs/docutils.md` on the myst-parser GitHub repo) uses
`myst_parser.docutils_` instead — this repo is a Sphinx project, so `myst_parser.sphinx_` is correct.

### `_default_typst_documents` — the CONF-08 derivation DOC-11 must describe accurately

```python
# Source: typsphinx/builder.py:28-47 (read verbatim this session)
def _default_typst_documents(config: Config) -> list:
    """Sphinx-native default for ``typst_documents``, mirroring
    ``sphinx.builders.latex.default_latex_documents`` (CONF-08).

    Derives a single master entry from ``root_doc``/``project``/``author``,
    with the target name in LaTeX's own shape (``make_filename_from_project``).
    Only invoked when the user has NOT set ``typst_documents`` in conf.py --
    an explicit setting (including an explicit ``[]``) always wins, because
    Sphinx's ``Config.__getattr__`` checks ``_raw_config`` before falling
    back to this callable default.
    """
    return [
        (
            config.root_doc,
            make_filename_from_project(config.project) + ".typ",
            config.project,
            config.author,
            "typst",
        )
    ]
```
Registered at `typsphinx/__init__.py:44`: `app.add_config_value("typst_documents",
_default_typst_documents, "html", [list])` `[VERIFIED: typsphinx/__init__.py, grep + Read this
session]`. This is what DOC-11 must state: (1) `typst_documents` need never be set for a PDF to be
produced — an unset value derives `[(root_doc, make_filename_from_project(project) + ".typ", project,
author, "typst")]`; (2) the target stem uses `make_filename_from_project()`, the *same* helper
Sphinx's own `-b latex` builder uses, e.g. project `"My Project"` → stem `myproject` → output
`myproject.pdf`, NOT `index.pdf` (the claim `docs/source/quickstart.rst:67` currently makes, which is
false per CONTEXT.md's own measured-staleness table); (3) an explicit `typst_documents` setting always
wins, because Sphinx's config resolution checks the raw user-set value before falling back to a
callable default; (4) `README.md:203`'s "required for PDF output" is false and must be corrected —
"required" implies the build fails/produces nothing without it, but CONF-08 made it optional.

### `derive_typst_lang()` — full current source (both rejection branches)

```python
# Source: typsphinx/template_engine.py:84-149 (read verbatim this session)
def derive_typst_lang(sphinx_language: str | None) -> str | None:
    # ... (docstring, ~45 lines, omitted here — see file for D-02/D-03 rationale)
    if not isinstance(sphinx_language, str) or not sphinx_language:
        logger.warning(
            f"typsphinx: could not derive a Typst 'lang' from Sphinx "
            f"'language' = {sphinx_language!r} -- omitting 'lang' (falling "
            f"back to the template's own default)."
        )
        return None

    head = re.split(r"[_\-@]", sphinx_language, maxsplit=1)[0].lower()

    if re.fullmatch(r"[a-z]{2,3}", head):
        return head

    logger.warning(
        f"typsphinx: could not derive a Typst 'lang' from Sphinx "
        f"'language' = {sphinx_language!r} -- omitting 'lang' (falling "
        f"back to the template's own default)."
    )
    return None
```
The two `logger.warning(...)` calls (lines 132-136 and 144-148) are byte-identical.

### CHANGELOG.md structure — exact measured line numbers this session

```
# All `## [X.Y.Z]` / `## [Unreleased]` headings, in file order:
8:    ## [Unreleased]              <- top-of-file placeholder (empty body)
10:   ## [0.7.0] - 2026-08-04
67:   ## [0.6.5] - 2026-07-29
90:   ## [0.6.4] - 2026-07-28
143:  ## [0.6.3] - 2026-07-25
213:  ## [0.6.2] - 2026-07-23
281:  ## [0.6.1] - 2026-07-20
323:  ## [0.6.0] - 2026-07-13
377:  ## [0.5.0] - 2026-07-11
404:  ## [0.4.3] - 2025-11-01     <- ## [0.4.4] belongs HERE, between 0.5.0 and 0.4.3
436:  ## [0.4.2] - 2025-10-29
455:  ## [0.4.1] - 2025-10-26
465:  ## [0.4.0] - 2025-10-26
584:  ## [0.3.0] - 2025-10-23
605:  ## [0.2.2] - 2025-10-23
650:  ## [0.2.1] - 2025-10-18
667:  ## [0.1.0b1] - 2025-10-13
840:  ## [0.2.0] - 2025-10-16     <- physically out of chronological order (after 0.1.0b1); NOT in scope to fix
911:  ## [Unreleased]              <- "Planned for Future Releases" tail, inside the 0.2.0 section's body span
```
`[Unreleased]:` link-reference at line 939 points to `.../compare/v0.7.0...HEAD` — confirms 0.7.0 is
the true latest tagged release at HEAD. The 25 `✅` occurrences: 12 at lines 801-813, 13 at lines
889-901 — two near-identical "Requirements Status" blocks, both inside the `## [0.2.0]` section span
(667-910ish; the first block's containing heading was not individually re-verified this session but
both blocks sit between `## [0.1.0b1]` at 667 and `## [Unreleased]` at 911, i.e. inside `## [0.2.0]`'s
own body per file order).

### `v0.4.4` reconstruction material (D-03)

```
$ git rev-list --count v0.4.3..v0.4.4    # => 148  [VERIFIED via git this session]
$ git tag -l v0.4.4                       # => v0.4.4
$ git log -1 --format="%ai" v0.4.4        # => 2026-07-05 15:11:52 +0900
```
`gh release view v0.4.4` (title "Release v0.4.4", published 2026-07-05T06:12:55Z) shows the commit
range is a CI/release-durability milestone ("v1.0" internal milestone name), not a `typsphinx`
behavior change. Highlights visible in the commit subjects: Python support floor bumped (multiple
`feat(03-*)` commits), `softprops/action-gh-release @v2` → `@v3`, `--locked` appended to `uv sync`
call sites, weekly dependency drift-detection workflow added, `sphinx-typst-stack` Dependabot group +
CI badge added, GitHub Actions artifact actions bumped to Node 24, and a `tomllib`/`tomli` fallback
fix in the release version-verify step. This is raw material for a Keep-a-Changelog-shaped `##
[0.4.4]` entry (using the same `### Added`/`### Changed`/`### Fixed` convention as the neighboring
`## [0.4.3]` entry at line 404) — drafting the exact prose is an execution-time task, not a research
deliverable.

### `extract_changelog_section.py`'s positional algorithm (REL-04 surface)

```python
# Source: scripts/extract_changelog_section.py:59, 87-116 (read verbatim this session)
_SECTION_HEADER_RE = re.compile(r"^## \[(?P<version>[^\]]+)\]")

def extract_section(changelog_text: str, version: str) -> str:
    lines = changelog_text.splitlines()
    start_index: int | None = None
    for index, line in enumerate(lines):
        match = _SECTION_HEADER_RE.match(line)
        if match and match.group("version") == version:
            start_index = index + 1
            break
    if start_index is None:
        raise RuntimeError(f"No '## [{version}]' section found in the CHANGELOG. ...")
    end_index = len(lines)
    for index in range(start_index, len(lines)):
        if _SECTION_HEADER_RE.match(lines[index]):
            end_index = index
            break
    body = "\n".join(lines[start_index:end_index]).strip("\n").strip()
    if not body:
        raise RuntimeError(f"The '## [{version}]' section in the CHANGELOG is empty. ...")
    return body
```
Called from `release.yml`'s `validate` job (existence/non-emptiness gate, lines ~72-79) and
`create-release` job (release-notes body, lines ~190-197) `[VERIFIED: .github/workflows/release.yml,
read this session]`. `tests/test_changelog_extraction.py::test_unreleased_headings_do_not_leak`
already reproduces the real file's exact "two `[Unreleased]` headings" structure in a synthetic
fixture and proves extraction of a numbered version between them is unaffected — this is the existing
regression coverage D-04's merge must keep green, not new coverage this phase needs to add.

### QUA-03 verification script (D-07/D-08/D-09-compliant, run this session)

```python
# Excludes fenced code blocks (``` / ~~~) and inline backtick spans before
# pairing <!-- / --> tokens with a stack walk (D-09's requirement — a raw
# count is NOT sufficient, since REQUIREMENTS.md:141 and ROADMAP.md:731
# both carry a backticked literal `<!--` describing this very defect).
import re
lines = open(".planning/PROJECT.md", encoding="utf-8").read().split("\n")
stack = []
in_fence = False
for idx, line in enumerate(lines, start=1):
    if line.strip().startswith("```") or line.strip().startswith("~~~"):
        in_fence = not in_fence
        continue
    if in_fence:
        continue
    stripped = re.sub(r'`{1,2}[^`\n]*?`{1,2}', '', line)
    for m in re.finditer(r'<!--|-->', stripped):
        if m.group(0) == '<!--':
            stack.append(idx)
        elif stack:
            stack.pop()
# Result this session: len(stack) == 0 (34 openers, 34 closers, all paired)
```
Result: **zero unterminated openers**, confirming D-07. Naive raw counts (`grep -o '<!--' | wc -l`
vs `grep -o -- '-->' | wc -l`) also happen to both return 34 in the current file state — but per D-09
this coincidence does not validate the naive approach as a method; it is only correct here because
this particular file's false-positive sites (backticked mentions) happen to be evenly balanced by
coincidence, not by construction.

### QUA-03 D-08 bisect finding: the closing commit, and it was deliberate

```
$ git log --oneline 279aea5..HEAD -- .planning/PROJECT.md   # (partial, relevant entry:)
43a2a78 docs(41-03): terminate PROJECT.md's two unterminated HTML comments (D-13)
```
Commit message (read verbatim via `git show 43a2a78`, this session):
> "Mechanical scan (regex-count `<!--` vs `-->` markers, checking each opener has a closer before the
> next opener) found exactly two unterminated comment-openers in `.planning/PROJECT.md`, at lines 761
> and 775 (moved from CONTEXT.md's recorded 492/506, measured at commit `279aea5`, since the file has
> grown ~250 lines) ... Post-fix scan: 31 comment-open markers, 31 comment-close markers, zero
> unterminated."

This is Phase 41, plan 03, decision "D-13" — a **deliberate**, self-documented, attributed repair, not
an incidental byproduct of unrelated edits. CONTEXT.md's phrasing ("later milestone closes rewrote
that footer tail and closed them incidentally") should be corrected in the phase's evidence record:
the mechanism was deliberate; only the *timing* (during a release-prep-adjacent plan, not a dedicated
hygiene phase) might read as incidental.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|---------------|--------|
| `docs/source/changelog.rst` hand-duplicates release history in rST | Delegates via myst-parser `include::` to `CHANGELOG.md` | This phase (D-01) | Future releases (starting with Phase 46's `0.7.1` entry) require zero additional doc edits |
| `derive_typst_lang()` warns from two call sites | Warns from one call site | This phase (QUA-02) | No behavior change (SC#3 requires warning-for-warning identical output); purely a maintainability fix |

**Deprecated/outdated:** `docs/source/changelog.rst`'s "Development Status" section (claims v0.3.x is
current — three major versions stale) is deleted per D-06, not deprecated-and-kept.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `myst_parser` must be added to `docs/source/conf.py`'s `extensions` list even though only the `include::`+`:parser:` mechanism (not native `.md` source files) is used | Architecture Patterns, Pattern 1 | Low — if unnecessary, the extra `extensions` entry is a harmless no-op; if necessary and omitted, the build fails loudly at `docs-html`/`docs-pdf` time (an `AttributeError` or `ExtensionError`), which is easy to catch and fix during Wave 1's real-build verification |
| A2 | The exact `## [0.4.4]` entry text (prose describing the CI/durability changes) is not pre-drafted in this research — only the raw commit-range material is provided | Code Examples, "v0.4.4 reconstruction material" | Low — this is explicitly an execution-time drafting task (D-03 calls it "reconstruct the entry"), not a research deliverable; the risk is only that the planner must budget a task for it rather than copy-paste from research |
| A3 | The two "Requirements Status" ✅ blocks (801-813, 889-901) both sit inside the `## [0.2.0]` (line 840) section's body span, i.e. the first block (801-813) is physically BEFORE `## [0.2.0]`'s own heading at 840, meaning it is technically still inside `## [0.1.0b1]`'s (line 667) span | Code Examples, CHANGELOG.md structure | Low — either attribution doesn't change D-05's fix (delete all 25 `✅` characters, reword the surrounding "Requirement N" lines); only affects which section's prose gets touched, not whether the fix works |

**If this table is empty:** N/A — see above; all three assumptions are low-risk and orthogonal to
the phase's pass/fail criteria.

## Open Questions

1. **Does the myst-parser-included `CHANGELOG.md` heading structure (H1 `# Changelog` → H2 `##
   [X.Y.Z]` → H3/H4 subsections) nest sanely under Phase 44.1's relative heading-depth mechanism once
   spliced into `changelog.rst`'s own toctree-included position?**
   - What we know: `changelog` is a toctree child (not a master), so it is `#include()`d with a
     `set heading(offset: N)` scope per Phase 44.1's fix; `translator.py` has handlers for every node
     type a Markdown parse of this specific file will produce.
   - What's unclear: whether the resulting PDF outline (bookmark/heading hierarchy) reads sensibly
     with `###`×54 and `####`×7 subsections nested several levels deep under a toctree offset — this
     is a rendering-quality question, not a compile-fatal question, and can only be answered by a real
     `tox -e docs-pdf` build.
   - Recommendation: this is exactly what ROADMAP SC#2's "build clean" bar should be checked against
     empirically in Wave 1/2, not resolved in research — no compile-fatal risk was found (all node
     types are covered), only a possible cosmetic depth concern.

2. **Does the CommonMark shortcut-reference-link resolution of `[0.7.0]`-shaped heading text (because
   `[0.7.0]: url` reference definitions exist at the file tail) render acceptably as a Typst-linked
   heading, or does it interact oddly with `TypstTranslator.visit_title`'s handling of a `reference`
   child?**
   - What we know: `visit_reference`/`depart_reference` exist and are exercised extensively elsewhere
     in the translator (inline hyperlinks are common in the corpus); `visit_title` processes children
     generically.
   - What's unclear: whether a `reference`-wrapped title looks visually different (color, underline)
     in a way that's undesirable for a changelog's version headings specifically, versus prose
     hyperlinks.
   - Recommendation: spot-check in the real build (Wave 1/2); if undesirable, the fix is trivial
     (strip the trailing `[X.Y.Z]:` reference-definition block from the included range via
     `:end-before:`, or accept the linked-heading look as a minor cosmetic bonus).

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `myst-parser` | DOC-12's `include::` mechanism | Not yet installed in this repo's `docs` extra | Needs `>=5.0` (latest 5.1.0, verified live) | None needed — this is a new, required `docs`-extra addition, not optional |
| `docutils` | myst-parser's `:parser:` option (floor `>=0.17`) | ✓ (already a project dependency) | `>=0.21,<0.23` (project pin, well above floor) | — |
| `sphinx` | myst-parser 5.x's floor (`>=8,<10`) | ✓ (already a project dependency) | `>=9.1,<10` (project pin, inside myst-parser's supported range) | — |
| `uv` | Regenerating `uv.lock` after the `pyproject.toml` edit | ✓ (standard project tooling) | — | — |
| `git` | D-08's bisect verification | ✓ | — | — |

**Missing dependencies with no fallback:** `myst-parser` itself must be added — there is no fallback
mechanism for DOC-12 without it (the alternatives were considered and rejected at D-01/D-02).

**Missing dependencies with fallback:** none.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (config in `pyproject.toml`, `[tool.pytest.ini_options]`) |
| Config file | `pyproject.toml` (`testpaths = ["tests"]`) |
| Quick run command | `pytest tests/test_changelog_extraction.py tests/test_template_engine.py::TestDeriveTypstLang tests/test_typst_lang_gate.py -v` |
| Full suite command | `pytest` (full suite) plus `black --check .`, `ruff check .`, `mypy typsphinx/` |

### Phase Requirement → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|--------------------|-------------|
| DOC-11 | README/quickstart.rst/configuration.rst state the true CONF-08 default behavior | manual/build-check | `sphinx-build -b typstpdf` against a fixture matching the Quick Start's literal steps (unset `typst_documents`), assert PDF filename == `make_filename_from_project(project) + ".pdf"`, not `index.pdf` | ✅ precedent exists (`tests/fixtures/default_typst_documents_gate/`, `tests/test_default_typst_documents_gate.py`) — planner should decide whether to reuse this fixture directly or add a doc-mirroring one with a project name matching the published example |
| DOC-12 SC#2 (a) | Changelog page carries 0.4.4-0.7.0 (12 releases) | build-check | `tox -e docs-html` then grep rendered HTML for each of the 12 version strings; `tox -e docs-pdf` then extract PDF text (pypdf) and grep for the same | ❌ Wave 0 — no existing test asserts changelog page content coverage; net-new |
| DOC-12 SC#2 (b) | No stale "(Current)" marker; both tox envs build clean | build-check | Capture stdout/stderr from both `sphinx-build` invocations, assert zero `WARNING:` lines referencing `changelog` (delta against a pre-phase baseline capture, since some pre-existing unrelated warnings are out of fence per Pitfall 2) | ❌ Wave 0 — net-new |
| DOC-12 SC#2 (c) | Adding `0.7.1` (Phase 46) is a one-line `CHANGELOG.md` addition | structural/manual | No automated test possible before Phase 46 exists; verify by inspection that `docs/source/changelog.rst` after this phase contains ONLY the `include::` directive plus framing sections, zero release-specific content | N/A — verified by code review of the diff, not a test |
| QUA-02 SC#3 (a) | Warning emitted from exactly one call site | structural | `grep -c "logger.warning" typsphinx/template_engine.py` scoped to `derive_typst_lang()`'s line range == 1 (a simple `awk`/`sed`-range grep, or an AST-based check) | ❌ Wave 0 — a structural grep, easy to add as a one-line CI/test assertion or a manual code-review checklist item |
| QUA-02 SC#3 (b) | Warning-for-warning identical output vs. pre-refactor baseline | regression | Run `pytest tests/test_typst_lang_gate.py tests/test_template_engine.py::TestDeriveTypstLang -v` before AND after the refactor; both existing test files already assert on warning *presence*/*content* (not just absence of crash) — a green run on both sides IS the baseline-identity proof, since neither test's assertions can pass with a differently-worded or missing warning | ✅ existing coverage sufficient — `tests/test_template_engine.py::TestDeriveTypstLang::test_malformed_inputs_return_none_and_warn` (6 parametrized malformed inputs) + `tests/test_typst_lang_gate.py::TestMalformedLanguage` (real-build, does not abort) |
| QUA-03 SC#4 | Zero unterminated `<!--` in `.planning/PROJECT.md`, whole-file scan | verification | The opener-stack script in Code Examples (fence/backtick-aware) — record its output as evidence, no code change expected | ✅ already run this session, result recorded above — planner's task is to re-run and record at phase-execution time, not to write new test code (this is a planning-record artifact, not part of the pytest suite) |
| SC#5 (no `typsphinx/` behavior change beyond QUA-02) | Regression guard | full-suite | `pytest` full run green, `black --check .`, `ruff check .`, `mypy typsphinx/` all clean | ✅ existing full suite is the guard |

### Sampling Rate

- **Per task commit:** the quick-run command above (three targeted test files/classes) plus
  `black --check .` / `ruff check .` on touched files.
- **Per wave merge:** `pytest` (full suite) + `black --check .` + `ruff check .` + `mypy typsphinx/`.
- **Phase gate:** both `tox -e docs-html` and `tox -e docs-pdf` (or `tox -e docs` for both together)
  run live and their output captured as evidence for DOC-12's "build clean" bar, plus the QUA-03
  verification script's output recorded verbatim.

### Wave 0 Gaps

- [ ] A build-check asserting the rendered changelog page (HTML and/or extracted PDF text) contains
      all of `0.4.4`, `0.4.1`..`0.7.0` (the 12 previously-missing versions) — no such test exists
      today.
- [ ] A build-check capturing zero `WARNING:` lines from both `docs-html`/`docs-pdf` builds
      attributable to the changelog page specifically (a delta-against-baseline approach, since some
      pre-existing warnings elsewhere in the docs build are out of this phase's fence).
- [ ] (Optional, low-value) A structural one-liner asserting `derive_typst_lang()` contains exactly
      one `logger.warning(` call — the existing `caplog`/GATE-01 regression tests already prove
      behavioral identity; this would only add belt-and-suspenders coverage for the "exactly one
      site" grep requirement, which can equally be satisfied by manual code review at plan-verification
      time.
- [ ] No new test infrastructure is needed for QUA-03 — the verification script above is a one-off
      diagnostic (matching this repo's stated precedent, `tests/test_no_stale_github_io_links.py`,
      IF the planner decides a standing regression guard is warranted; but D-07 explicitly declines
      this for QUA-03, so the default is: run once, record the result, do not add to the suite).

*Framework install: none needed — pytest is already fully configured; the only new tooling
dependency this phase adds is `myst-parser` itself (a `docs`-extra, build-time dependency, not a test
dependency).*

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-------------------|
| V2 Authentication | No | This phase touches no auth surface |
| V3 Session Management | No | N/A |
| V4 Access Control | No | N/A |
| V5 Input Validation | Marginal | `derive_typst_lang()`'s refactor (QUA-02) must preserve its existing input-validation behavior (reject non-str/None/empty/non-ASCII/wrong-length input) exactly — this is already covered by the existing `caplog`/GATE-01 tests, not new validation logic |
| V6 Cryptography | No | N/A |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|----------------------|
| Untrusted content injected into a Sphinx build via a Markdown include | Tampering | Not applicable here — `CHANGELOG.md` is a repo-tracked, first-party file, not user-supplied content; `myst-parser`'s Markdown parsing is not being exposed to any external/untrusted input by this phase's change |
| A malicious `postinstall` script riding in on the new `myst-parser` dependency | Tampering / Supply chain | Checked this session: `myst-parser`'s PyPI metadata shows no `postinstall`-style script hook (Python wheels don't have npm-style postinstall scripts as an attack surface in the same way; the relevant analog — arbitrary code in `setup.py`/build backend — was not separately probed but `myst-parser` uses a standard `flit`/`hatchling`-style build with no reported supply-chain incidents `[ASSUMED — not independently re-verified this session beyond the legitimacy-check seam and download-volume cross-check]`) |

This phase carries essentially zero security surface — it is documentation, a logging refactor, and a
planning-record verification. The one live security-adjacent question (is `myst-parser` a trustworthy
new dependency) was investigated in the Package Legitimacy Audit above.

## Sources

### Primary (HIGH confidence)
- `https://pypi.org/pypi/myst-parser/json` — fetched live 2026-08-09; version 5.1.0, `requires_dist`
  for docutils/sphinx floors and ceilings.
- `typsphinx/builder.py`, `typsphinx/__init__.py`, `typsphinx/template_engine.py`,
  `typsphinx/writer.py`, `typsphinx/translator.py`, `scripts/extract_changelog_section.py`,
  `.github/workflows/release.yml`, `.github/workflows/links.yml`, `tox.ini`, `pyproject.toml`,
  `.readthedocs.yaml`, `docs/source/conf.py`, `docs/source/index.rst`,
  `docs/source/changelog.rst`, `docs/source/quickstart.rst`,
  `docs/source/user_guide/configuration.rst`, `README.md`, `CHANGELOG.md`,
  `.planning/PROJECT.md` — all read verbatim this session.
- `tests/test_changelog_extraction.py`, `tests/test_template_engine.py`,
  `tests/test_typst_lang_gate.py`, `tests/fixtures/default_typst_documents_gate/*`,
  `tests/test_default_typst_documents_gate.py` — all read verbatim this session.
- `git log`/`git show`/`git rev-list` against this repo's own history — the D-08 bisect finding
  (commit `43a2a78`) and the `v0.4.4` tag/release data.

### Secondary (MEDIUM confidence)
- `https://myst-parser.readthedocs.io/en/latest/faq/index.html` and
  `https://myst-parser.readthedocs.io/en/latest/syntax/organising_content.html` — official myst-parser
  docs, fetched via WebFetch this session, quoted verbatim for the `:parser: myst_parser.sphinx_`
  syntax.
- `https://raw.githubusercontent.com/executablebooks/MyST-Parser/master/docs/docutils.md` — official
  repo docs (non-Sphinx variant), fetched via WebFetch, confirming `myst_parser.docutils_` is the
  distinct plain-docutils path.
- WebSearch results summarizing myst-parser 4.0's `requires_dist` (docutils<0.22, sphinx<9) —
  used to establish why the version floor must be 5.0, not 4.x.

### Tertiary (LOW confidence)
- WebSearch/pypistats download-volume figures for `myst-parser` (~1.5M/week) — used only to
  contextualize/override the automated legitimacy-check seam's `SUS` verdict, not as a load-bearing
  technical claim.

## Metadata

**Confidence breakdown:**
- Standard stack (myst-parser version floor): HIGH — verified live against PyPI registry JSON, the
  authoritative source, with the exact `requires_dist` constraints quoted.
- Architecture (translator node coverage, include mechanics): HIGH — every node type was checked
  against `translator.py`'s actual `visit_*` definitions this session; the include syntax was quoted
  verbatim from official myst-parser docs (two independent pages agreeing).
- Pitfalls (build-clean semantics, ordering hazard): HIGH — `tox.ini`'s exact `commands` were read
  this session confirming no `-W` flag.
- QUA-03 findings (D-07/D-08/D-09): HIGH — independently re-derived with a compliant script this
  session, and the D-08 bisect commit was found and read verbatim, exceeding the confidence CONTEXT.md
  itself had ("deliberate, not incidental" is now a confirmed fact, not an inference).
- Open Questions (heading depth under real build, reference-wrapped headings): MEDIUM — the mechanics
  are understood but the actual rendered *quality* can only be confirmed by a real build during
  execution, which the phase's own success criteria already require.

**Research date:** 2026-08-09
**Valid until:** 30 days (stable ecosystem; myst-parser's release cadence is a few times a year, and
this repo's own dependency pins change only at milestone boundaries) — re-verify the myst-parser
version floor if this research is consumed more than ~60 days after 2026-08-09, since a new
myst-parser major release could shift the `requires_dist` floor again.
