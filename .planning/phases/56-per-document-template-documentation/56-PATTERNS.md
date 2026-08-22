# Phase 56: Per-Document Template Documentation - Pattern Map

**Mapped:** 2026-08-16
**Files analyzed:** 14 (2 new test modules, 1 fixture addition, 8 prose files edited, 3 prose-only sweep files)
**Analogs found:** 14 / 14

This phase writes **no production code**. Every "file" below is either an RST/Markdown prose edit
or a pytest doc-gate module/fixture. There is no controller/service/model tier; classification below
uses `docs-page` and `test-gate` as the two roles that matter here.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `tests/test_registry_documentation_gate.py` (name TBD, D-06 two-way catalogue gate) | test-gate | static AST/text scan, no subprocess | `tests/test_docs_contract_claims_gate.py` | exact (same "prose ↔ code predicate, never skips" shape) |
| Removed-values subsection binding (new test method, DOC-17) | test-gate | static text-scan against an importable dict | `tests/test_removed_config_deprecation_gate.py` (binding half) + `typsphinx/removed_config.py` (source dict) | exact |
| `tests/fixtures/user_template_relative_asset_gate/_typst/refs.bib` (new) | fixture (data) | file-I/O, consumed by a real Typst compile | `tests/fixtures/user_template_relative_asset_gate/_typst/branded.typ` + `logo.png` (siblings in the same bundle) | exact |
| New assertion(s) proving `refs.bib` reaches `_template/typst/refs.bib` | test-gate | real `sphinx-build -b typstpdf` → `typst.compile()` | `tests/test_user_template_relative_asset_gate.py::test_asset_reached_the_bundle_destination` | exact |
| Update `test_page_states_the_shared_child_composition` (ten→nine) | test-gate | static text-scan against a real build's measured file count | `tests/test_output_layout_docs_gate.py::TestPublishedOutputLayoutTextMatchesBuild` (whole class) | exact — this is the same file, same class, must be edited not copied |
| `docs/source/user_guide/configuration.rst` (new registry subsection, key-naming subsection, error table, removed-values subsection, element [4] rewrite) | docs-page | request-response (reader-consumed prose) | itself, existing "Template Configuration" subsections (`Template Function`, `Typst Package`, `Template Assets`) | exact (same page, same section family) |
| `docs/source/user_guide/output_layout.rst` (`_template/<key>/` story, file-count fix, `--root` note) | docs-page | request-response | itself, existing "Which File to Compile" section | exact |
| `docs/source/user_guide/templates.rst` (closing note at 114-118) | docs-page | request-response | itself, "Template Assets" subsection (already bundle-correct, written Phase 54) | exact |
| `docs/source/examples/advanced.rst` (refs.bib note + code-block at ~107, 122-131) | docs-page | request-response | `templates.rst`'s Template Assets subsection (sibling worked example) | role-match |
| `docs/source/user_guide/builders.rst:122-130` (file-count only) | docs-page | request-response | `output_layout.rst`'s file-count paragraph (the corrected source of truth) | exact |
| `README.md`, `examples/basic/README.md`, `examples/advanced/README.md`, `docs/source/quickstart.rst`, `docs/source/examples/basic.rst` (sweep surface) | docs-page | request-response | `output_layout.rst`/`configuration.rst` (source of the corrected facts these pages must not contradict) | role-match |
| `CLAUDE.md:49` (D-09, one-line correction) | docs-page (dev-facing, unpoliced) | request-response | itself | n/a — single-line factual fix, no test binds it (deliberately, D-09) |

## Pattern Assignments

### `tests/test_registry_documentation_gate.py` (test-gate, D-06 two-way leading-clause catalogue)

**Analog:** `tests/test_docs_contract_claims_gate.py` (read in full)

**Module docstring shape to copy** (lines 1-43) — explains *why* it never skips, note especially the
"Subject: published prose, not emitted output" framing to adapt for D-06's own two-way check:

```python
"""
...
**Subject: published prose, not emitted output.** Every real-compile
"does the code do what it says" proof already lives in
``tests/test_documented_params_contract_gate.py`` and
``tests/test_typst_lang_gate.py``. This module asks a different question --
does the PROSE agree with the code's own predicate -- and answers it by
reading ``docs/source/**/*.rst`` and calling one Python function
(``typsphinx.template_engine.TemplateEngine.uses_bundled_default_template``).
No ``typst-py`` dependency, no ``sphinx-build`` subprocess: this module
never skips.
"""
```

**Run-time discovery pattern** (lines 151-153) — apply the same shape to scanning
`typsphinx/*.py` for `raise ExtensionError(...)` call sites via `ast`, not a hardcoded file list:

```python
def _iter_rst_pages() -> list:
    """Every ``*.rst`` file under ``docs/source/``, in sorted order."""
    return sorted(DOCS_SOURCE_DIR.rglob("*.rst"))
```

**Exclusion set with inline reason** (lines 142-148) — D-06's scanner must exclude
`builder.py:2377` (the `typstpdf` PDF-compile failure aggregate) this exact way, by explicit
denylist entry with a written reason, not by silently hoping the catalogue matches:

```python
EXCLUDED_CLAIM_PAGES = {
    "docs/source/changelog.rst": (
        "A historical release-note migration guide (documenting the "
        "0.5.x -> 0.6.x typst_elements allowlist change at the time it "
        "shipped), not a live claim about the current build's behaviour."
    ),
}
```

**Two-way closure test pattern** (lines 357-397, `TestContractClaimPageEnumerationIsClosed`) — copy
this three-test shape (non-empty scan / discovered-minus-excluded-equals-reviewed /
no-stale-exclusion) for D-06's own set-equality checks between "clauses the catalogue publishes" and
"clauses `typsphinx/*.py` raises":

```python
def test_discovered_minus_excluded_equals_reviewed(self):
    discovered = _discovered_claim_pages()
    reviewed_or_excluded = discovered - set(EXCLUDED_CLAIM_PAGES)
    assert reviewed_or_excluded == REVIEWED_CLAIM_PAGES, (
        f"Discovered claim pages minus exclusions "
        f"{sorted(reviewed_or_excluded)} != the reviewed set "
        f"{sorted(REVIEWED_CLAIM_PAGES)}. A newly claim-bearing page "
        f"was found that is in neither list -- review its claims..."
    )
```

**"Patterns have teeth" self-test pattern** (lines 439-478, `TestForbiddenClaimDetectorIsFailFirst`)
— feed the classifier a synthetic known-bad string and a synthetic known-good string directly (never
via a page walk), proving both directions of D-06's check actually fire:

```python
def test_pre_fix_claim_is_detected_as_withholding_a_route_the_code_affirms(self):
    _, withheld = _classify_sentence(PRE_FIX_FALSE_CLAIM)
    falsely_withheld = withheld - CODE_WITHHELD_ROUTES
    assert falsely_withheld, (
        "The forbidden-claim detector did not flag the verbatim "
        "pre-fix sentence... this guard would have passed vacuously..."
    )

def test_affirmative_detector_fires_on_a_known_good_sentence(self):
    known_good = "..."
    affirmed, withheld = _classify_sentence(known_good)
    assert affirmed, "The affirmative detector matched nothing."
```

**Real source shapes the AST scanner must parse (all four verified this session):**

```python
# typsphinx/template_registry.py:302-306 -- bare raise, single f-string
if not isinstance(declared, dict):
    raise ExtensionError(
        "typst_document_templates must be a dict mapping registry key to definition,"
        f" got {declared!r}"
    )

# typsphinx/template_registry.py:421-434 -- IMPLICIT adjacent string-literal
# concatenation (two tokens, no `+`) -- a single-line regex will miss this.
failures.append(
    f"registry key {key!r}'s template {template!r} does " "not exist"
)

# typsphinx/template_registry.py:437-441 -- aggregate wrapper
if failures:
    summary = "; ".join(failures)
    raise ExtensionError(
        f"typst_document_templates: {len(failures)} invalid "
        f"definition(s): {summary}"
    )

# typsphinx/template_registry.py:512-517, 522-527 -- two bare raises, CONF-13/CONF-14
raise ExtensionError(
    f"typst_documents entry names registry key {raw_key!r}, "
    "which is not a string -- registered "
    f"typst_document_templates keys: {sorted(registry.keys())!r}"
)
...
raise ExtensionError(
    f"typst_documents entry names registry key {key!r}, which is "
    "not a registered typst_document_templates key -- registered "
    f"keys: {sorted(registry.keys())!r}"
)

# typsphinx/builder.py:950 -- aggregate, output path collisions
raise ExtensionError(
    f"typst: {len(failures)} output path collision(s): {summary}"
)

# typsphinx/builder.py:1310-1313 -- aggregate, pre-write template path failures
raise ExtensionError(
    f"typst: {len(failures)} pre-write template path "
    f"failure(s): {summary}"
)

# typsphinx/builder.py:2151-2153 -- CALL-THROUGH shape: the leading clause is
# NOT an inline f-string at the raise site -- it is the return value of a
# helper function. A naive "grab the f-string literal following
# `raise ExtensionError(`" parser will not see this text at all.
raise ExtensionError(
    _conf17_violation_message(key, str(resolved_path), str(self.srcdir))
)

# typsphinx/builder.py:303-334 -- the helper itself, called from BOTH
# builder.py:1270 (inside the pre-write aggregate, shape #6) AND
# builder.py:2152 (bare, standalone) -- deliberately duplicated, byte-identical
# text either way (see the function's own docstring for why).
def _conf17_violation_message(key: str, resolved_path: str, srcdir: str) -> str:
    return (
        f"typst_document_templates: registry key {key!r}'s "
        f"resolved template {resolved_path!r} has a "
        "parent directory that is srcdir itself, or an "
        f"ancestor of srcdir ({srcdir!r}) -- put "
        "the template in its own subdirectory (CONF-17, A-01)"
    )

# typsphinx/builder.py:1992-1996 -- I/O bare raise, inside try/except
raise ExtensionError(
    f"typst_document_templates: failed to copy the "
    f"resolved template for registry key {key!r} "
    f"from {src_file!r} to {dest_file!r}: {e}"
) from e

# typsphinx/builder.py:2002-2007 -- I/O bare raise
raise ExtensionError(
    f"typst_document_templates: the resolved template for "
    f"registry key {key!r} ({template_filename!r}) was never "
    f"copied from {src_dir!r} to {dest_dir!r} -- a wrapper "
    "naming this key would import a file that does not exist"
)

# typsphinx/builder.py:2174-2177 -- aggregate, bundle destination collisions
raise ExtensionError(
    f"typst_document_templates: {len(failures)} bundle "
    f"destination collision(s): {summary}"
)

# typsphinx/builder.py:2375-2378 -- OUT OF SCOPE for D-06's catalogue: PDF
# compile failure, not a registry/bundle config error. Must be explicitly
# denylisted, not merely absent from the catalogue.
raise ExtensionError(
    f"typstpdf: {len(failures)} master document(s) failed: {summary}"
)
```

---

### DOC-17 removed-values binding (extend `tests/test_removed_config_deprecation_gate.py` or add a
sibling module)

**Analog (binding style):** `tests/test_removed_config_deprecation_gate.py` (read in full — this
module already drives real `sphinx-build` subprocesses per removed name; it does NOT yet bind the
*prose page* to the dict, only the runtime warning). **Recommendation: write DOC-17's prose-binding
as a NEW, separate, no-skip static test (reads `configuration.rst` + imports
`REMOVED_CONFIG_VALUES`), rather than adding a subprocess-based test to this module** — this keeps
the new gate in the "never skips" class alongside D-06, since it needs no `sphinx-build` at all, only
a dict import and a text read (matches `test_docs_contract_claims_gate.py`'s reason for existing).

**Source of truth to import, not transcribe** (`typsphinx/removed_config.py:36-56`):

```python
REMOVED_CONFIG_VALUES: dict[str, str] = {
    "typst_template_assets": (
        "'typst_template_assets' was removed in v0.9.0 and is now ignored. "
        "Every used template's bundle directory (the resolved template "
        "file's parent) is copied wholesale to the output tree, so MORE "
        "files now reach the output than the explicit list used to select "
        "-- no asset list is needed any more."
    ),
    "typst_authors": (
        "'typst_authors' was removed in v0.7.1 and is now ignored. Rich "
        "author structure (department, organization, location, email) is "
        "expressed through 'typst_template_function's 'params' route "
        "instead, so author department, organization, and email do not "
        "reach the output unless supplied that way."
    ),
    "typst_toctree_defaults": (
        "'typst_toctree_defaults' was removed in v0.6.3 and has no "
        "replacement. It was registered but never read even when it "
        "existed, so deleting it changes no build output."
    ),
}
```

**Existing module's own `REQUIRED_PHRASES` dict** (lines 29-39 of
`test_removed_config_deprecation_gate.py`) is the model for what "matching" means — bespoke phrase
sets per name, not one shared template:

```python
REQUIRED_PHRASES = {
    "typst_template_assets": ["typst_template_assets", "copied wholesale", "MORE"],
    "typst_authors": [
        "typst_authors",
        "typst_template_function",
        "department, organization, and email",
    ],
    "typst_toctree_defaults": ["typst_toctree_defaults", "no replacement"],
}
```

**Module-header convention to copy verbatim** (lines 1-19) — cite the phase, the design constraint
(D-06/D-10), and explicitly state the module's no-narrowing-by-builder rule:

```python
"""
Phase 54 plan 06 (CONF-19): the removed-config detection gate.
...
D-10, recorded here rather than left implicit: ``config-inited`` fires for
EVERY builder, not just the Typst ones, ...
"""
```

---

### DOC-16 fixture extension (`tests/fixtures/user_template_relative_asset_gate/_typst/refs.bib`)

**Analogs (full files, already small):**

`tests/fixtures/user_template_relative_asset_gate/_typst/branded.typ` (full text, 57 lines) — the
sibling asset to place `refs.bib` beside. Load-bearing line: `#image("logo.png", width: 24pt)` — the
same bare-relative-filename pattern the new `#bibliography("refs.bib")` call must follow (never
`"_typst/refs.bib"`).

`tests/fixtures/user_template_relative_asset_gate/conf.py` (full text, 42 lines) — no change needed;
already uses the reserved `"typst"` key via a 4-element `typst_documents` entry, so the new bundle
destination is deterministically `_template/typst/refs.bib`.

**What adding the file touches, concretely:**
1. New `tests/fixtures/user_template_relative_asset_gate/_typst/refs.bib` — any valid BibTeX entry.
2. A `#bibliography("refs.bib")` call added inside `_typst/branded.typ`'s body — bare filename.
3. A new assertion, copying this exact shape from
   `tests/test_user_template_relative_asset_gate.py:119-128`
   (`test_asset_reached_the_bundle_destination`):

```python
def test_asset_reached_the_bundle_destination(self, build):
    build_dir = build["build_dir"]
    assert (build_dir / "_template" / "typst" / "logo.png").exists(), (
        "logo.png did not reach the bundle destination "
        "<outdir>/_template/typst/logo.png"
    )
    assert (build_dir / "_template" / "typst" / "branded.typ").exists(), (
        "branded.typ did not reach the bundle destination "
        "<outdir>/_template/typst/branded.typ"
    )
    # New: assert refs.bib the same way.
```

4. No `@preview` import — `bibliography()` is Typst-builtin, does not become a fourth
   version-lockstep site (matches `branded.typ`'s own header comment, lines 7-9, which explicitly
   records this abstention for the same reason).

---

### `_run_sphinx_build` helper (copy per-module, do NOT refactor into a shared fixture)

**Canonical copy** (verbatim, `tests/test_output_layout_docs_gate.py:82-105`):

```python
def _run_sphinx_build(
    source_dir: Path, build_dir: Path, builder: str
) -> subprocess.CompletedProcess:
    """
    Run ``sphinx-build -b <builder>`` as a subprocess and return the
    completed process (stdout/stderr captured as text).

    Invoked as ``sys.executable -m sphinx`` (never ``uv run sphinx-build``,
    never a resolved ``sphinx-build`` binary) so the exact interpreter/venv
    running this test is reused, sidestepping the documented NixOS-sandbox
    PATH-shadowing hazard. Every gate module in this suite carries its own
    copy of this helper rather than importing a sibling module's.
    """
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "sphinx",
            "-b",
            builder,
            str(source_dir),
            str(build_dir),
        ],
        capture_output=True,
        text=True,
    )
```

**Convention-establishing docstring sentence** (`tests/test_removed_config_deprecation_gate.py:5-8`,
quoted for the planner's benefit so no one "helpfully" DRYs this up):

> "This module exercises `typsphinx/removed_config.py`'s `config-inited` handler through real
> `sphinx-build` subprocess builds (the `_run_sphinx_build` helper is copied near-verbatim per this
> repository's own per-module convention, established by `test_typst_lang_gate.py` and
> `test_collision_predicate_completeness_gate.py`)..."

If the new D-16 test only needs to read a fixture's build output already produced elsewhere in the
class (as `test_user_template_relative_asset_gate.py` already does via its class-scoped `build`
fixture), no new copy is needed — reuse that module's existing `build` fixture rather than
duplicating `_run_sphinx_build` a second time inside the same file.

---

### Prose-binding assertion shape — the "ten"/"nine" collision task

**Analog, verbatim (must be EDITED, not copied — same file):**
`tests/test_output_layout_docs_gate.py:461-478`

```python
def test_page_states_the_shared_child_composition(self):
    """docs/source/user_guide/output_layout.rst's shared-child section
    heading is present and the section publishes the literal 'ten'
    file-count claim (D-09, SC#3)."""
    text = OUTPUT_LAYOUT_RST_PATH.read_text(encoding="utf-8")
    assert "Documents Shared by Several Masters" in text, (
        "docs/source/user_guide/output_layout.rst does not contain the "
        "'Documents Shared by Several Masters' section heading."
    )
    # Assert the whole claim clause, not the bare word "ten": "ten" is a
    # substring of "written" and "content", both of which occur many times
    # on this page, so `"ten" in text` was satisfied even when the claim
    # was absent, deleted, or restated with a wrong number.
    assert "writes ten ``.typ`` files" in text, (
        "docs/source/user_guide/output_layout.rst does not publish the "
        "'writes ten ``.typ`` files' count claim for the three-master "
        "example."
    )
```

**Required change:** update the literal string to `"writes nine ``.typ`` files"` (matching
`output_layout.rst:159`'s corrected prose) **in the same task/commit** that edits the `.rst` line, or
the suite goes RED. This is the exact class of same-task test/doc coupling documented in
`tests/test_output_layout_docs_gate.py:351-398`
(`test_three_master_project_emits_ten_typ_files`, already correctly asserting **nine** root-level
`.typ` files against the real build — this is the build-side twin of the prose-side test above; do
not confuse the two, both exist, only the prose-side one still says "ten").

**Whole-class convention worth reusing for D-06's second binding assertion** (if the plan binds any
error-table row's prose to a real build rather than relying solely on the static leading-clause
scan): `TestPublishedOutputLayoutTextMatchesBuild` (lines 401-509) — 5 tests, no skip marker, no
`typst-py` dependency, reads `.rst` text and asserts literal-fragment containment against constants
derived from real code (`REFUSAL_WARNING_FRAGMENT`, `COLLISION_ERROR_FRAGMENT`,
`_WALKTHROUGH_WRAPPER_STEM` computed via `make_filename_from_project()`, never hand-typed).

---

### RST directive conventions (survey of pages being edited)

**Table syntax — use `.. list-table::`.** Already used twice in the corpus and proven under both
`tox -e docs-html` and `tox -e docs-pdf` (`docs/source/user_guide/builders.rst:9-20`,
`docs/source/examples/basic.rst:100`). Verbatim example to follow for D-05's error table and D-07's
key-naming rules table:

```rst
.. list-table::
   :header-rows: 1
   :widths: 20 40 40

   * - Builder
     - Output
     - Use Case
   * - ``typst``
     - ``.typ`` files
     - Edit Typst markup manually, use external Typst CLI
```

`typsphinx/translator.py` implements the full docutils table node chain
(`visit_table`/`depart_table`, `visit_tgroup`, `visit_thead`, `visit_tbody`, `visit_row`,
`visit_entry`/`depart_entry`, including `morecols`/`morerows` → colspan/rowspan at
`translator.py:4573-4598`) — any RST table syntax (`list-table`, simple, grid, `csv-table`) parses to
the same doctree, so `list-table` is a style choice, not a compatibility requirement; chosen purely
for corpus-convention consistency.

**Section heading style** (`configuration.rst:1-13`) — title with `=`, top-level section with `-`,
subsection with `~`:

```rst
Configuration
=============

Basic Configuration
-------------------

Project Information
~~~~~~~~~~~~~~~~~~~
```

The new registry subsection (D-01) is a fifth `~~~~` subsection under the existing `Template
Configuration` `----` section (`configuration.rst:88` onward), alongside `Template Function`,
`Typst Package`, `Template Assets`.

**Cross-reference role — `:doc:`.** Used pervasively (18+ live uses,
e.g. `configuration.rst:58,139,215,235,307,355,387-389`); already proven safe by both green builds.
Example already in the corpus, to copy for D-01's "links to `output_layout` rather than restating":

```rst
See :doc:`templates` for detailed examples.
```

`:ref:` is used only for `genindex`/`modindex`/`search` (`docs/source/index.rst:71-73`) — not a
pattern this phase's new subsections need.

**Config-value naming convention — double-backtick inline literal, NOT `:confval:`.** `:confval:` is
not used anywhere in this repo's docs; every existing mention of a config name uses `` ``typst_template`` ``-style
inline literals (seen throughout `configuration.rst`). D-05/D-07's new content must follow this, not
introduce the unproven `:confval:` role.

**`.. code-block:: python` for conf.py examples**, already the pattern at `configuration.rst:14-19`
and `configuration.rst:100-102` — reuse verbatim for D-04's worked `template`-route example.

## Shared Patterns

### Doc-gate "never skips" design
**Source:** `tests/test_docs_contract_claims_gate.py:16-24`, `tests/test_output_layout_docs_gate.py:21-30`
**Apply to:** D-06's catalogue gate and DOC-17's removed-values binding gate — both must avoid a
`typst-py` import guard AND a subprocess call, since they only read `.rst`/`.py` source text. Only
the DOC-16 fixture-extension test (which needs a real `-b typstpdf` compile) legitimately carries
`@pytest.mark.skipif(not TYPST_AVAILABLE, ...)` — copy the exact guard from
`tests/test_user_template_relative_asset_gate.py:36-41,74-77`.

### `_run_sphinx_build` per-module copy convention
**Source:** `tests/test_output_layout_docs_gate.py:82-105` (also identical, modulo default parameter,
in `test_user_template_relative_asset_gate.py`, `test_quickstart_docs_gate.py`,
`test_removed_config_deprecation_gate.py`)
**Apply to:** any new subprocess-based gate this phase adds. Do not import a shared helper — copy it.

### Exclusion sets are explicit dicts with an inline reason, never a bare list
**Source:** `tests/test_docs_contract_claims_gate.py:142-148` (`EXCLUDED_CLAIM_PAGES`)
**Apply to:** D-06's `builder.py:2377` denylist entry; DOC-17's changelog/CHANGELOG.md history
exclusion if the removed-values sweep test enumerates a page set at all.

### "Patterns have teeth" self-tests
**Source:** `tests/test_docs_template_layout_gate.py::test_patterns_have_teeth` and
`tests/test_docs_contract_claims_gate.py::TestForbiddenClaimDetectorIsFailFirst`
**Apply to:** D-06's gate must prove both directions of its two-way check fire against synthetic
known-bad/known-good strings, not just against the real (already-agreeing, post-fix) doc/code pair.

## No Analog Found

None. Every file this phase touches has a direct or role-matched analog already in the repository.

## Metadata

**Analog search scope:** `tests/test_docs_contract_claims_gate.py`,
`tests/test_output_layout_docs_gate.py`, `tests/test_docs_template_layout_gate.py`,
`tests/test_user_template_relative_asset_gate.py`, `tests/test_removed_config_deprecation_gate.py`,
`tests/fixtures/user_template_relative_asset_gate/**`, `typsphinx/template_registry.py`,
`typsphinx/builder.py`, `typsphinx/removed_config.py`, `docs/source/user_guide/configuration.rst`,
`docs/source/user_guide/output_layout.rst`, `docs/source/user_guide/builders.rst`,
`docs/source/examples/basic.rst`.
**Files scanned:** ~14 read in full or substantial part this session.
**Pattern extraction date:** 2026-08-16
