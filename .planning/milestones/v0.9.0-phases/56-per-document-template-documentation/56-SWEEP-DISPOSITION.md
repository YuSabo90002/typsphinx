# Phase 56 Plan 05 — Sweep Disposition Record

**Purpose:** SC#4's discovery grep re-run at execution time (D-10), against the merged tree —
every hit is dispositioned in writing here, never silently dropped. The hit set below is what
the grep commands actually returned when run; `56-CONTEXT.md`'s D-09/D-10 hit list is a FLOOR to
compare against, not the search set.

**Run against commit:** `753ea458a9d60f6ddd31b07210cb6423c60b99f8` (the merged base this plan's
worktree forked from — the tip of waves 1 and 2, 56-01 through 56-04).
**Run at:** 2026-08-16T12:01:04Z
**Working directory for every command below:** the repository root, excluding `.git/` and
`.planning/` explicitly.

---

## Discovery commands and complete output

### Command 1 — the former reserved output basename

```
grep -rn '_template\.typ' --include='*' . --exclude-dir=.git --exclude-dir=.planning
```

Complete output (61 lines, one file per line except where a file has multiple hits):

```
CLAUDE.md:49:- **`builder.py`** — `TypstBuilder` (`name="typst"`) drives the write loop, image copying, and template-asset copying. It also writes a shared `_template.typ` file once per build (`_write_template_file`). `TypstPDFBuilder` (`name="typstpdf"`) subclasses it: `write_doc` still emits `.typ`, and `finish()` compiles master documents to PDF via `pdf.py`.
docs/source/conf.py:94:# See docs/source/_typst/custom_template.typ for the font list and its
docs/source/conf.py:96:typst_template = "_typst/custom_template.typ"
CHANGELOG.md:482:  Typst errors (CONF-02, CONF-03)** — fixes a missing `_template.typ` write, unconditional
examples/basic/README.md:38:body that the wrapper includes; and `_template.typ`, the template the
examples/advanced/README.md:65:- `_build/typst/_template.typ` - Template imported by the wrapper (here, your `_typst/custom.typ`)
docs/source/changelog.rst:63:  the reserved ``_template.typ``, every docname's content file, and every entry's wrapper.
docs/source/changelog.rst:197:     // New way -- declare lang with a default, matching the shipped custom_template.typ
examples/charged-ieee/approach2/conf.py:21:# NOTE: typst_package is intentionally NOT set here. _typst/_template.typ
examples/charged-ieee/approach2/conf.py:23:# switch typsphinx to the package-only path, which skips emitting _template.typ
examples/charged-ieee/approach2/conf.py:25:typst_template = "_typst/_template.typ"
scripts/render_admonition_greyscale.py:149:    typ_files = sorted(p for p in build_dir.glob("*.typ") if p.name != "_template.typ")
tests/test_admonition_greyscale_pipeline.py:127:    typ_files = sorted(p for p in build_dir.glob("*.typ") if p.name != "_template.typ")
tests/test_builder_output_stem.py:432:    assert builder._resolve_target_stem("index", "_template.typ") == "_template"
tests/test_builder_output_stem.py:442:    write to a bare ``_template.typ`` file for a target to clobber, since
tests/test_collision_predicate_completeness_gate.py:151:    the exact reserved ``_template.typ`` basename instead; the reservation
tests/test_collision_predicate_completeness_gate.py:314:        assert TypstBuilder._collision_key("./_template.typ") == (
tests/test_collision_predicate_completeness_gate.py:315:            TypstBuilder._collision_key("_template.typ")
tests/test_docs_contract_claims_gate.py:29:``docs/source/_typst/custom_template.typ`` (the unguarded fourth
tests/test_docs_contract_claims_gate.py:34:those three declaration surfaces and does not read ``custom_template.typ``
tests/test_entry_metadata_route_uniformity.py:172:typst_template = '_typst/custom_template.typ'
tests/test_entry_metadata_route_uniformity.py:178:    (template_dir / "custom_template.typ").write_text(
tests/test_entry_metadata_route_uniformity.py:263:typst_template = '_typst/custom_template.typ'
tests/test_entry_metadata_route_uniformity.py:269:    (template_dir / "custom_template.typ").write_text(BUNDLED_BASE_TYP)
tests/test_entry_metadata_route_uniformity.py:284:    assert '#import "/_template/typst/custom_template.typ": project' in content
tests/test_examples_charged_ieee_gate.py:236:        # own basename ("_template.typ", per approach2/conf.py's
tests/test_examples_charged_ieee_gate.py:237:        # typst_template = "_typst/_template.typ") -- not the
tests/test_examples_charged_ieee_gate.py:239:        shared_template_path = build_dir / "_template" / "typst" / "_template.typ"
tests/test_examples_charged_ieee_gate.py:242:            "key's bundle at _template/typst/_template.typ -- its absence "
tests/test_examples_charged_ieee_gate.py:268:        assert '#import "/_template/typst/_template.typ": project' in master_text
tests/test_external_link_style_render_gate.py:146:        # _template.typ (the single-file writer that wrote there is deleted).
tests/test_package_template_routing.py:5:emitted an ``#import`` of the shared ``_template.typ`` file for every master
tests/test_package_template_routing.py:14:  emitted, and no ``_template.typ`` file is written (D-01).
tests/test_package_template_routing.py:98:        assert "_template.typ" not in emitted_text
tests/test_package_template_routing.py:99:        assert not (outdir / "_template.typ").exists()
tests/test_package_only_config_gate.py:6:BUG-A (a package-alone master importing a shared ``_template.typ`` the
tests/test_package_only_config_gate.py:244:        NO reference to the shared ``_template.typ`` file -- which the
tests/test_package_only_config_gate.py:250:        assert "_template.typ" not in text
tests/test_package_only_config_gate.py:251:        assert not (build["build_dir"] / "_template.typ").exists()
tests/test_package_only_config_gate.py:398:        unconditionally imported ``_template.typ``.
tests/test_package_only_config_gate.py:400:        reconstructed = '#import "_template.typ": project\n' + emitted_master_text
tests/test_registry_prewrite_validation_gate.py:170:                # writer that used to put "_template.typ" at the outdir
tests/test_template_engine.py:497:        result = engine.render(params, body, template_file="_template.typ")
tests/test_template_prefix_reservation_gate.py:7:``_template.typ`` infrastructure file (Phase 54 plans 04/05 deleted its
tests/test_user_template_relative_asset_gate.py:8:``docs/source/_typst/custom_template.typ``, and
tests/test_typst_lang_gate.py:65:54: ``_template/<key>/...``, not a root-level ``_template.typ``), not the
tests/test_typst_lang_gate.py:801:        ``_template.typ`` root file) the real build already wrote into this
tests/test_typst_lang_gate.py:886:        ``_template.typ`` root file) to strip its ``lang`` parameter back
tests/test_typst_documents_collision_gate.py:5:``_template.typ`` infrastructure file, now FAILS the build with a single
tests/test_typst_documents_collision_gate.py:95:    docname's own content path, or the reserved _template.typ, now FAILS
tests/test_typst_documents_collision_gate.py:184:        exact-name `_template.typ` claim, which a project-name slug could
tests/test_typst_documents_collision_gate.py:260:        exercises replaced Phase 47's exact-name `_template.typ` claim).
tests/fixtures/admonition_greyscale_probe/conf.py:37:# globbing `*.typ` (excluding a `_template.typ` name, a filter that
tests/fixtures/bld02_template_clobber_gate/conf.py:10:# EXACT reserved basename `_template.typ` (once "./"-normalized); Task 1
tests/fixtures/bld02_template_clobber_gate/conf.py:27:#     `grep -c '^#let project'` proof that the written `_template.typ` no
tests/fixtures/derived_template_collision_gate/conf.py:11:# preserves underscores) to the EXACT reserved basename `_template.typ`.
tests/fixtures/explicit_template_collision_gate/conf.py:10:# preserves underscores) to the EXACT reserved basename `_template.typ`.
tests/fixtures/user_template_relative_asset_gate/conf.py:5:# repository (the bundled default, docs/source/_typst/custom_template.typ,
typsphinx/template_engine.py:38:# `typst_template = "_typst/custom_template.typ"`).
typsphinx/writer.py:190:        single shared ``_template.typ`` file that used to be written at
typsphinx/writer.py:205:            suffix, e.g. ``"_template.typ"`` or ``"../_template.typ"``.
typsphinx/writer.py:209:            '_template.typ'
typsphinx/writer.py:211:            '../_template.typ'
typsphinx/writer.py:213:            '../_template.typ'
typsphinx/writer.py:231:        return "".join(["../"] * depth) + "_template.typ"
```

### Command 2 — the deleted builder method name

```
grep -rn '_write_template_file' --exclude-dir=.git --exclude-dir=.planning .
```

Complete output (1 line):

```
CLAUDE.md:49:- **`builder.py`** — `TypstBuilder` (`name="typst"`) drives the write loop, image copying, and template-asset copying. It also writes a shared `_template.typ` file once per build (`_write_template_file`). `TypstPDFBuilder` (`name="typstpdf"`) subclasses it: `write_doc` still emits `.typ`, and `finish()` compiles master documents to PDF via `pdf.py`.
```

### Command 3 — the retracted element-[4] phrase

```
grep -rn 'accepted and ignored' --exclude-dir=.git --exclude-dir=.planning .
```

Complete output (6 lines, all under `tests/`):

```
tests/test_builder_output_stem.py:123:    """D-09: the fifth tuple element is accepted and ignored -- the
tests/test_entry_metadata_precedence.py:48:  five-element arity (the fifth element is accepted and ignored).
tests/test_entry_metadata_precedence.py:176:    a 4-element entry -- the fifth element is accepted and ignored by this
tests/test_registry_documentation_gate.py:92:# ("Document class ... accepted and ignored") must survive on no
tests/test_registry_documentation_gate.py:94:RETRACTED_ELEMENT_FOUR_PHRASE = "accepted and ignored"
tests/test_registry_documentation_gate.py:616:    """D-02/DOC-15: the retracted "accepted and ignored" definition of
```

### Command 4 — the three removed configuration value names

```
grep -rn 'typst_template_assets\|typst_authors\|typst_toctree_defaults' --exclude-dir=.git --exclude-dir=.planning .
```

Complete output (39 lines) — the full match set is in
`docs/source/user_guide/configuration.rst` (the intended, already-published Removed
Configuration Values section from 56-02), `CHANGELOG.md` / `docs/source/changelog.rst`
(historical), `tests/` (out of policed scope), and `typsphinx/removed_config.py` (source code,
not a documentation page):

```
docs/source/user_guide/configuration.rst:624:   * - ``typst_template_assets``
docs/source/user_guide/configuration.rst:629:   * - ``typst_authors``
docs/source/user_guide/configuration.rst:635:   * - ``typst_toctree_defaults``
CHANGELOG.md:222:- **Breaking:** the `typst_authors` config value is removed (CONF-10) — 0.7.0's documentation
CHANGELOG.md:224:  `typst_authors` is an unregistered `conf.py` variable that Sphinx ignores without any warning, so
CHANGELOG.md:400:- **BREAKING: `typst_toctree_defaults` config value removed (CONF-05)** — it was registered but never
CHANGELOG.md:422:  `docs/source/user_guide/configuration.rst`'s `typst_author` renamed to the real `typst_authors`, the
CHANGELOG.md:484:  `typst_authors`/`typst_author_params` being silently ignored. A new config→output regression
CHANGELOG.md:665:    - Explicit: Specify assets with `typst_template_assets` list (supports glob patterns)
CHANGELOG.md:667:  - New configuration value: `typst_template_assets`
CHANGELOG.md:787:  - New `typst_authors` configuration for detailed author information (department, organization, email)
CHANGELOG.md:1002:- `typst_toctree_defaults`: Default toctree options
docs/source/changelog.rst:97:- **Breaking:** the ``typst_authors`` config value is removed. It was pure sugar over the
docs/source/changelog.rst:102:  dictionary. A leftover ``typst_authors`` is now an unregistered ``conf.py`` variable, which
docs/source/changelog.rst:107:     # Old way -- typst_authors is gone in 0.7.1
docs/source/changelog.rst:108:     typst_authors = {
docs/source/changelog.rst:236:- **Breaking:** the inert ``typst_toctree_defaults`` config value was removed. Delete it from
tests/test_removed_config_deprecation_gate.py:29:REMOVED_NAMES = ["typst_template_assets", "typst_authors", "typst_toctree_defaults"]
tests/test_removed_config_deprecation_gate.py:34:    "typst_template_assets": ["typst_template_assets", "copied wholesale", "MORE"],
tests/test_removed_config_deprecation_gate.py:35:    "typst_authors": [
tests/test_removed_config_deprecation_gate.py:36:        "typst_authors",
tests/test_removed_config_deprecation_gate.py:40:    "typst_toctree_defaults": ["typst_toctree_defaults", "no replacement"],
tests/test_removed_config_deprecation_gate.py:97:    ``typst_toctree_defaults``, an explicit statement that there is none),
tests/test_removed_config_deprecation_gate.py:130:        conf_body = "typst_template_assets = None\n"
tests/test_removed_config_deprecation_gate.py:137:        assert "typst_template_assets" in combined_output, (
tests/test_removed_config_deprecation_gate.py:144:        conf_body = "typst_authors = []\n"
tests/test_removed_config_deprecation_gate.py:151:        assert "typst_authors" in combined_output, (
tests/test_removed_config_deprecation_gate.py:214:    A future accidental re-registration of ``typst_template_assets`` (for
tests/test_removed_config_deprecation_gate.py:220:    def test_typst_template_assets_absent_from_config_registry(self, temp_sphinx_app):
tests/test_removed_config_deprecation_gate.py:221:        assert "typst_template_assets" not in temp_sphinx_app.config.values, (
tests/test_removed_config_deprecation_gate.py:222:            "typst_template_assets must stay genuinely UNREGISTERED -- "
tests/test_registry_documentation_gate.py:86:    "typst_template_assets": "copied wholesale",
tests/test_registry_documentation_gate.py:87:    "typst_authors": "params",
tests/test_registry_documentation_gate.py:88:    "typst_toctree_defaults": "No replacement",
tests/test_registry_documentation_gate.py:803:            name for name in REMOVED_CONFIG_VALUES if name != "typst_authors"
tests/test_registry_documentation_gate.py:808:            f"omitted 'typst_authors' name as missing from a synthetic "
tests/test_registry_documentation_gate.py:810:            f"omitted 'typst_authors' name as missing from a synthetic "
typsphinx/removed_config.py:11:Two of the three names below (``typst_authors``, removed at v0.7.1;
typsphinx/removed_config.py:12:``typst_toctree_defaults``, removed at v0.6.3) have already been
typsphinx/removed_config.py:14:(``app.add_config_value("typst_authors", None, ...)`` purely so Sphinx would
typsphinx/removed_config.py:16:names it currently owns. And re-registering ``typst_template_assets`` as an
typsphinx/removed_config.py:37:    "typst_template_assets": (
typsphinx/removed_config.py:38:        "'typst_template_assets' was removed in v0.9.0 and is now ignored. "
typsphinx/removed_config.py:44:    "typst_authors": (
typsphinx/removed_config.py:45:        "'typst_authors' was removed in v0.7.1 and is now ignored. Rich "
typsphinx/removed_config.py:51:    "typst_toctree_defaults": (
typsphinx/removed_config.py:52:        "'typst_toctree_defaults' was removed in v0.6.3 and has no "
```

### Command 5 — the source-tree-shaped asset reference form

```
grep -rn '_typst/refs\.bib' --exclude-dir=.git --exclude-dir=.planning .
```

Complete output (2 lines, both under `tests/`):

```
tests/test_user_template_relative_asset_gate.py:172:    ``refs.bib`` -> ``_typst/refs.bib``."""
tests/fixtures/user_template_relative_asset_gate/_typst/refs.bib:4:% reference to a subpath form (e.g. `"_typst/refs.bib"`).
```

### Command 6 (this plan's own addition, beyond the plan's minimum list) — stale
### root-level file-count claims not yet caught by the literal-string greps above

```
grep -rn 'ten .typ files\|writes ten\|10 .typ files' --exclude-dir=.git --exclude-dir=.planign .
```

Complete output: **empty** — 56-03 already corrected every root-level-count claim
(`output_layout.rst`, `builders.rst`) in the same commit as the test that pins it.

### Command 7 (this plan's own addition) — every file under the three policed roots that
### mentions `_template` in any form, to catch a stale claim phrased without the literal
### `_template.typ` string

```
grep -rln '_template' --exclude-dir=.git --exclude-dir=.planning docs/ README.md examples/
```

Complete output (18 files). Every file in this list is accounted for below: 13 are
`typst_template = ...` / `typst_template_function` assignments or references naming a real,
unchanged input file or config key (not a hit); `docs/source/user_guide/output_layout.rst`,
`docs/source/user_guide/templates.rst`, `docs/source/user_guide/configuration.rst`, and
`docs/source/examples/advanced.rst` carry the already-corrected bundle-directory prose from
56-01/56-02/56-03/56-04; `examples/basic/README.md`, `examples/advanced/README.md`,
`examples/charged-ieee/approach2/conf.py` are the three files this task fixes below; and
`examples/charged-ieee/approach1/conf.py` is the one hit this grep found BEYOND the floor
(see the "Hits beyond the floor" section).

---

## Comparison against the research floor (56-CONTEXT.md D-09/D-10)

The floor recorded two hits beyond `56-RESEARCH.md`'s original discovery: `CLAUDE.md:49`
(D-09) and `examples/charged-ieee/approach2/conf.py:21-25` (D-10). Both are confirmed present
in this execution-time re-run (Command 1 and Command 2 above).

**This re-run found ONE additional hit the D-09/D-10 floor did not name:**
`examples/charged-ieee/approach1/conf.py:59` names the method
`TypstBuilder.copy_template_assets()`, which does not exist in `typsphinx/builder.py` at this
commit (`grep -n 'copy_template_assets' typsphinx/*.py` returns zero hits). The method was
deleted the same way `_write_template_file()` was — Phase 54's bundle-copy consolidation. This
is the same class of defect D-09 fixes in `CLAUDE.md`, found on a file inside the
already-policed `examples/` set, exactly the failure mode invariants #4/#11 exist to catch: a
written floor (D-09/D-10) missing a hit that a repo-wide re-grep surfaces. **It is not a silent
drop — it is fixed in this task, disposed of below.**

The comment's *behavioral* claim (the package-only route has no asset-copying mechanism) is
still TRUE — verified by reading `typsphinx/builder.py:2123-2126`'s
`_copy_used_template_bundles()`: a used key whose registry entry carries `package` and no
`template` is `continue`d past with nothing copied. Only the METHOD NAME cited is stale.

---

## Per-hit disposition table

| # | File | Line | Matched text | Disposition | Reason |
|---|------|------|--------------|-------------|--------|
| 1 | `CLAUDE.md` | 49 | `_write_template_file` / `_template.typ` | **fixed in this phase** (Task 2) | D-09: the builder method was deleted in Phase 54; the bullet is rewritten to describe the shipped `_copy_used_template_bundles()` bundle-copy path. `CLAUDE.md` is agent-facing instruction, not published user documentation — 54.1's D-12 policed set (`docs/source/` + `README.md` + `examples/`) is NOT widened; no test greps `CLAUDE.md`. |
| 2 | `docs/source/conf.py` | 94, 96 | `custom_template.typ` | **not a hit** | Different filename (`custom_template.typ`) that merely ends in the characters `_template.typ` — the exact false positive the anchored pattern in Task 2's gate exists to exclude. Confirmed: the char immediately before the match is `m` (alphanumeric), so the anchored pattern `(^|[^A-Za-z0-9])_template\.typ` does not fire on it. |
| 3 | `CHANGELOG.md` | 482 | `_template.typ` | **excluded** | Historical release note describing what was true at the version it documents (v0.5.x-era fix entry). Rewriting it would falsify the record. CHANGELOG curation is Phase 57's, not this phase's. |
| 4 | `examples/basic/README.md` | 38 | `_template.typ` | **fixed in this phase** (Task 1) | Named a root-level shared template file as an output artifact. Rewritten to describe two root-level files (`basic-example.typ`, `index.typ`) plus the template bundle one directory down at `_template/typst/`, verified against a real `-b typst` build of the example. |
| 5 | `examples/advanced/README.md` | 65 | `_template.typ` | **fixed in this phase** (Task 1) | Same class as #4: the bulleted output listing's last bullet named a root-level `_template.typ`. Rewritten to `_template/typst/custom.typ`, verified against a real `-b typst` build of the example (four root-level files + the one bundle file at that exact path). |
| 6 | `docs/source/changelog.rst` | 63 | `_template.typ` | **excluded** | Historical release note (the same class as #3) describing the layout at the version it documents. Not rewritten, per D-10's explicit recommendation and this plan's prohibitions. |
| 7 | `docs/source/changelog.rst` | 197 | `custom_template.typ` | **not a hit** | Same class as #2 — a longer basename (`custom_template.typ`) ending in the same characters, not the reserved basename itself. |
| 8 | `examples/charged-ieee/approach2/conf.py` | 21 | `_typst/_template.typ` | **fixed in this phase** (Task 1) | D-10: the original comment named the input file `_typst/_template.typ` directly at the point of an output-artifact claim. Rewritten to refer to "the file `typst_template` names below" instead of repeating the literal path at that sentence, so the corrected sentence carries no stale claim and the anchored gate's exemption stays scoped to the assignment line alone. |
| 9 | `examples/charged-ieee/approach2/conf.py` | 23 | `_template.typ` (in "skips emitting _template.typ") | **fixed in this phase** (Task 1) | D-10: the comment claimed setting `typst_package` would "skip emitting `_template.typ` into the output directory" — an artifact that no longer exists. Rewritten to state the actual consequence: no local bundle would be copied at all, so the template this project relies on would never reach the output directory. |
| 10 | `examples/charged-ieee/approach2/conf.py` | 25 (now 28 post-edit) | `typst_template = "_typst/_template.typ"` | **not a hit — legitimate input path** | The `typst_template` value legitimately NAMES a user template file whose basename coincides with the former reserved output basename. This is an INPUT path, not an output-artifact claim, and is explicitly NOT changed by this task (verified: `grep -c 'typst_template = "_typst/_template.typ"' examples/charged-ieee/approach2/conf.py` is 1, both before and after this task's edit). |
| 11 | `scripts/render_admonition_greyscale.py` | 149 | `_template.typ` | **excluded** | Not under any of the three policed roots (`docs/source/`, `README.md`, `examples/`) — it is a project-internal tooling script. Filters build output by excluding the (now-nonexistent) former basename defensively; harmless, out of scope. |
| 12-53 | `tests/**` (37 distinct hits across 20 files) | various | `_template.typ` / `accepted and ignored` / `typst_template_assets` etc. | **excluded** | Every occurrence under `tests/` is outside the policed set on the measured 54.1 D-12 basis. Read individually, each is either (a) a regression assertion that the reserved-basename artifact is GONE (`test_package_template_routing.py`, `test_package_only_config_gate.py`), (b) a fixture or docstring deliberately exercising the reserved-basename edge case for a collision/reservation gate (`test_collision_predicate_completeness_gate.py`, `test_template_prefix_reservation_gate.py`, `tests/fixtures/*_collision_gate/conf.py`), or (c) the sweep/catalogue gate module's OWN string constant used to detect the retracted phrase's absence (`test_registry_documentation_gate.py`'s `RETRACTED_ELEMENT_FOUR_PHRASE`). None make a documentation claim. |
| 54 | `docs/source/user_guide/configuration.rst` | 624, 629, 635 | `typst_template_assets` / `typst_authors` / `typst_toctree_defaults` | **not a hit — intentional, already-published content** | 56-02's Removed Configuration Values section, which is the correct, intended publication of these three names as removed-value guidance (DOC-17), bound by test to `typsphinx/removed_config.py`. |
| 55 | `typsphinx/removed_config.py`, `typsphinx/writer.py`, `typsphinx/template_engine.py` | various | various | **excluded** | Production source code under `typsphinx/`, not a policed documentation page. This task and this plan modify no file under `typsphinx/` (verified below). |
| 56 | `examples/charged-ieee/approach1/conf.py` | 59 | `TypstBuilder.copy_template_assets()` | **fixed in this phase** (Task 1, beyond the anticipated `files_modified` list) | The method `copy_template_assets()` does not exist in `typsphinx/builder.py` at this commit (`grep -c copy_template_assets typsphinx/*.py` is 0) — deleted alongside `_write_template_file()` in Phase 54's bundle-copy consolidation. Same defect class as D-09, found by this plan's own broadened Command 7 sweep (see "Hits beyond the floor" above), on a file INSIDE the already-policed `examples/` set. The comment's behavioral claim stays true (verified against `_copy_used_template_bundles()`'s package-alone `continue` branch); only the stale method name is corrected, to describe the mechanism without naming an internal symbol. |

---

## Fixes applied (Task 1)

1. `examples/basic/README.md:36-39` — rewritten to name the two root-level files this example
   actually produces (`basic-example.typ`, `index.typ`) plus the template bundle one directory
   down at `_template/typst/`. Verified against a real `-b typst` build into a scratch
   directory: the emitted tree is exactly `basic-example.typ`, `index.typ` at the root, and
   `_template/typst/base.typ` (plus the bundle's own `README.md`) one directory down.

2. `examples/advanced/README.md:65` — the bulleted output listing's last bullet rewritten from
   `_build/typst/_template.typ` to `_build/typst/_template/typst/custom.typ`, keeping the
   parenthetical naming the source (`_typst/custom.typ`). Verified against a real `-b typst`
   build into a scratch directory: the emitted tree is exactly four root-level `.typ` files
   (`advanced-example.typ`, `index.typ`, `chapter1.typ`, `chapter2.typ`) plus
   `_template/typst/custom.typ` one directory down — matching this example's own custom
   template's basename (not `base.typ`, since a custom template's own filename is preserved
   through the bundle copy).

3. `examples/charged-ieee/approach2/conf.py:19-28` — the four-line comment rewritten so it no
   longer claims that setting `typst_package` would "skip emitting `_template.typ`" (an
   artifact that no longer exists). It now states the actual consequence: this approach's own
   template imports the Typst Universe package itself, so setting `typst_package` as well
   would switch typsphinx to the package-only route, no local bundle would be copied, and the
   template this project relies on would never reach the output. The `typst_template` value on
   the following line is unchanged (`grep -c` confirms 1). The comment's other mention of the
   input file's own path was reworded to say "the file `typst_template` names below" rather
   than repeating the literal path at a sentence that used to make a stale output claim,
   keeping the anchored gate's exemption scoped to the assignment line alone (see disposition
   row #10 above and the "Do not fix this filter" note on the plan's own acceptance criterion).

4. `examples/charged-ieee/approach1/conf.py:56-62` — the hit found beyond the floor. Rewritten
   to describe the package-only route's actual lack of an asset-copying mechanism
   (`_copy_used_template_bundles()` skips any key whose entry carries a package and no
   template) instead of naming the deleted `TypstBuilder.copy_template_assets()` method. The
   behavioral claim itself was re-verified true by reading the current bundle-copy code before
   writing the replacement text.

**Verification for Task 1:**
- `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` — succeeded (worktree venv
  provisioned).
- `uv run pytest tests/test_examples_charged_ieee_gate.py -q` — 2 passed.
- `uv run pytest -q` — 1408 passed, 5 skipped, 0 failed.
- `grep -rnE '(^|[^A-Za-z0-9])_template\.typ' docs README.md examples | grep -v 'changelog.rst' | grep -v 'approach2/conf.py:.*typst_template = '` — zero hits.
- `grep -c 'typst_template = "_typst/_template.typ"' examples/charged-ieee/approach2/conf.py` — 1.
- `git diff --stat -- docs/source/changelog.rst CHANGELOG.md typsphinx/ tests/` — empty.

## Fixes applied (Task 2)

5. `CLAUDE.md:49` — D-09: the Architecture section's `builder.py` bullet named
   `_write_template_file`, deleted in Phase 54's bundle-copy consolidation. Rewritten to
   describe `_copy_used_template_bundles()`: the builder accumulates the registry keys used at
   write time and, in `finish()`, copies each used key's whole bundle directory to its own
   directory under the reserved output directory. Scope decision recorded per the plan's
   instruction: `CLAUDE.md` stays agent-facing instruction, not published user documentation,
   so 54.1 D-12's policed set (`docs/source/` + `README.md` + `examples/`) is NOT widened by
   this fix — no test greps `CLAUDE.md`.

6. New `tests/test_bundle_layout_sweep_gate.py` — the machine-enforced, never-skipping,
   run-time, repo-wide presence gate over the three policed roots (`docs/source/`, `README.md`,
   `examples/`), discovered via `rglob()`, never a hardcoded file list. Two patterns:
   `RESERVED_TEMPLATE_BASENAME_RE` (anchored: the character before the match must be
   start-of-line or non-alphanumeric, so a longer basename like `custom_template.typ` cannot
   fire) and `DELETED_WRITE_TEMPLATE_FILE_METHOD_RE` (word-bounded). `EXCLUDED_SWEEP_PATHS`
   carries two reasoned exclusions populated from Task 1's disposition table above: the
   historical `docs/source/changelog.rst` (whole-file) and
   `examples/charged-ieee/approach2/conf.py:28` (line-scoped, the legitimate
   `typst_template` assignment). `TestNoStaleBundleLayoutClaimSurvives` (4 tests: non-empty
   discovery, both patterns clean, exclusion staleness check) and
   `TestSweepPatternsHaveTeeth` (5 tests: both patterns fire on a synthetic bad string and do
   not fire on a synthetic clean string, including the anchor's exact false-positive case) — 9
   tests total, none skipped, no `typst-py` import, no `sphinx-build` subprocess.

**Verification for Task 2:**
- `uv run pytest tests/test_bundle_layout_sweep_gate.py -q` — 9 passed, 0 skipped.
- `uv run pytest -q` — 1417 passed, 5 skipped, 0 failed.
- `grep -c '_write_template_file' CLAUDE.md` — 0.
- `grep -c 'skipif' tests/test_bundle_layout_sweep_gate.py` — 0; `grep -c 'subprocess' tests/test_bundle_layout_sweep_gate.py` — 0.
- `grep -c 'EXCLUDED_SWEEP_PATHS' tests/test_bundle_layout_sweep_gate.py` — 10 (well above 1).
- `uv run black --check .` — clean. `uv run mypy typsphinx/` — clean (8 source files, no issues).
- `cd /home/yuta/Documents/typsphinx && uv run ruff check .claude/worktrees/agent-ad68ec9a3759def94/` — all checks passed (one `B007` unused-loop-variable finding was caught and fixed before this commit: `for key, reason in EXCLUDED_SWEEP_PATHS.items()` → `for key in EXCLUDED_SWEEP_PATHS`, since the staleness test never used `reason`).

**Issue encountered (documented, not fixed — same class as 56-01/56-02/56-04's own "Issues
Encountered" false positives):** the plan's Task 2 acceptance criterion
`grep -rc 'CLAUDE.md' tests/ is 0 — the policed set was not widened` cannot be literally
satisfied: `tests/` already carries 25 PRE-EXISTING citations of `CLAUDE.md` across 22 files
(mostly `// ... (CLAUDE.md).` comments inside `.typ` fixtures citing the `@preview`
version-lockstep hazard, plus a handful of prose citations in
`test_toolchain_config_gate.py`/`test_citation_degradation_gate.py`/
`test_readthedocs_config.py`). None of these are new; none is inside
`tests/test_bundle_layout_sweep_gate.py` (`grep -c 'CLAUDE.md' tests/test_bundle_layout_sweep_gate.py`
is 0); and `git diff HEAD~1 -- tests/` for this commit shows zero added lines containing
`CLAUDE.md`. The intent of the criterion — "this task's own new test does not grep
`CLAUDE.md`'s content" — is genuinely satisfied; the literal repo-wide grep count is not, for
reasons that predate this plan entirely.

---

## Phase-boundary evidence

Recorded against commit `0811ab69` (Task 2's own commit, the tip of this plan's worktree
before Task 3's own commit) — the merged tree carrying all five plans of Phase 56.

### Full pytest suite

Command: `uv run pytest -q`

```
================= 1417 passed, 5 skipped in 118.84s (0:01:58) ==================
```

Compared against the phase's measured starting baseline (`56-VALIDATION.md`: 1366 passed, 5
skipped, 0 failed at HEAD `f07e8cb8`): **+51 passed**, contributed across the phase's five
plans (each plan's own SUMMARY.md records its individual delta: 56-01 +13, 56-02 +15, 56-03
+10, 56-04 +8, 56-05 +9 from `test_bundle_layout_sweep_gate.py`'s own new module — some
plans' growth also extended existing test methods rather than adding new ones, which is why a
per-plan sum does not need to land on exactly +51 to be consistent). **Failed count: zero**,
matching the phase's unconditional-zero-failures standard (`STATE.md` § "The green bar is
UNCONDITIONAL ZERO FAILURES") — no RED is attributed to a pre-existing condition; none
occurred.

### Lint / type trio

Commands: `uv run black --check .` / `uv run ruff check .` (via the documented NixOS
main-checkout workaround) / `uv run mypy typsphinx/`

```
$ uv run black --check .
All done! ✨ 🍰 ✨
339 files would be left unchanged.

$ cd /home/yuta/Documents/typsphinx && uv run ruff check .claude/worktrees/agent-ad68ec9a3759def94/
All checks passed!

$ uv run mypy typsphinx/
Success: no issues found in 8 source files
```

### Documentation builds

Commands: `uv run tox -e docs-html` / `uv run tox -e docs-pdf`

```
$ uv run tox -e docs-html
...
build succeeded, 3 warnings.
  docs-html: OK (3.80=setup[0.12]+cmd[3.68] seconds)
  congratulations :) (3.85 seconds)

$ uv run tox -e docs-pdf
...
WARNING: unknown node type: <doctest_block ...> (compute_content_include_path docstring)
WARNING: unknown node type: <doctest_block ...> (compute_template_import_path docstring)
...
typst: wrote 1 wrapper file(s) -- compile these: typsphinx.typ
Compiling 1 master document(s) to PDF...
Generated PDF: .../docs/_build/pdf/typsphinx.pdf
build succeeded, 5 warnings.
  docs-pdf: OK (4.12=setup[0.12]+cmd[4.00] seconds)
  congratulations :) (4.16 seconds)
```

Both report `build succeeded`. `docs-html`'s 3 warnings and `docs-pdf`'s 5 warnings match the
pre-existing baseline exactly (56-02-SUMMARY.md and 56-04-SUMMARY.md both independently
measured and recorded this same 3/5 split; the unknown-node-type autodoc warnings are the
`writer.py` docstring doctest blocks and are pre-existing and unrelated to any page this phase
edited — confirmed by name: `compute_content_include_path` and `compute_template_import_path`,
neither touched by any of this phase's five plans).

### Production-code diff

Command: `git diff --stat f07e8cb8 -- typsphinx/` (the phase's base commit — `f07e8cb8`,
"docs(state): record phase 56 context session", the commit `56-RESEARCH.md` itself measured
against)

```
(empty)
```

Confirms this phase changed zero lines under `typsphinx/`, across all five plans, matching the
phase's docs-only scope (`56-CONTEXT.md` § "Phase Boundary": "No production code changes").

### Sweep gate and registry documentation gate, independently

Command: `uv run pytest tests/test_bundle_layout_sweep_gate.py tests/test_registry_documentation_gate.py -q`

```
tests/test_bundle_layout_sweep_gate.py .........                         [ 28%]
tests/test_registry_documentation_gate.py .......................        [100%]

============================== 32 passed in 0.27s ==============================
```

---

## Requirement-to-evidence mapping

### DOC-15 — Per-document template registry documentation

- `tests/test_registry_documentation_gate.py::TestErrorCatalogueAgreesWithCode` — the seven
  config-caused `ExtensionError` shapes' error catalogue agrees two-way with
  `typsphinx/template_registry.py` and `typsphinx/builder.py`'s real raise sites.
- `tests/test_registry_documentation_gate.py::TestRetractedElementFourDefinitionIsGone` —
  the retracted "accepted and ignored" phrase is absent repo-wide from the policed set.
- `tests/test_registry_documentation_gate.py::TestKeyNamingRulesMatchTheCode` — the seven
  CONF-18 key-shape rejection cases agree with `_KEY_SHAPE_REJECTION_CASES`.
- `tests/test_docs_template_layout_gate.py::test_every_surviving_jinja_dir_mention_names_templates_path`
  — the D-08 `templates_path` preventive note satisfies the existing same-line exemption rule.
- `tests/test_output_layout_docs_gate.py::TestPublishedOutputLayoutTextMatchesBuild` and
  `tests/test_hand_compile_root_gate.py` — the per-key `_template/<key>/` bundle-directory
  story, the corrected nine-root-level-file count, and the conditional hand-compile `--root`
  rule, all pinned by real builds.
- `tests/test_bundle_layout_sweep_gate.py::TestNoStaleBundleLayoutClaimSurvives` (this plan) —
  the repo-wide, machine-enforced guarantee that no page in the policed set claims the retired
  root-level `_template.typ` artifact or the deleted `_write_template_file` method, going
  forward.

### DOC-16 — Per-document template asset examples

- `tests/test_user_template_relative_asset_gate.py::TestPublishedAssetGuidanceMatchesTheFixture`
  — both `templates.rst`'s no-exceptions bundle rule and `advanced.rst`'s bare-filename
  bibliography reference are bound to the fixture's real, measured bundle destination.
- `tests/test_user_template_relative_asset_gate.py::TestUserTemplateRelativeAssetGate::test_asset_reached_the_bundle_destination`
  — a real `sphinx-build -b typstpdf` proves `refs.bib` reaches
  `_template/typst/refs.bib` alongside `logo.png` and `branded.typ`.
- `tests/test_bundle_layout_sweep_gate.py::TestNoStaleBundleLayoutClaimSurvives::test_no_reserved_template_basename_claim_survives`
  (this plan) — the sweep confirms neither `templates.rst` nor `advanced.rst` (nor any other
  policed page) reintroduces a stale `_template.typ` claim.

### DOC-17 — Removed configuration values migration guidance

- `tests/test_registry_documentation_gate.py::TestRemovedValuesGuidanceMatchesTheWarnings` —
  `configuration.rst`'s Removed Configuration Values section agrees with
  `typsphinx/removed_config.py`'s `REMOVED_CONFIG_VALUES` for all three removed names.
- `tests/test_removed_config_deprecation_gate.py::TestMultipleRemovedValuesEachWarnSeparately::test_all_three_set_together_warn_once_each_in_declaration_order`
  — a real `sphinx-build` with all three removed names set together proves three separate
  warnings fire in declaration order, not aggregated.
- This plan's own Command 4 discovery grep (above) confirms no stale claim about any of the
  three removed names survives outside the intentional, already-published
  `configuration.rst` section and the historical `CHANGELOG.md`/`docs/source/changelog.rst`
  entries.

