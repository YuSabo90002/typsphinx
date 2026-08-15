# Project Research Summary

**Project:** typsphinx v0.9.0 — Per-Document Template Registry
**Domain:** Sphinx extension architecture; multi-output builder integration; template selection and asset bundling
**Researched:** 2026-08-15
**Confidence:** HIGH (all claims grounded in source code reads, primary documentation, and direct precedent from existing shipped features)

## Executive Summary

The per-document template registry feature is a **straightforward architectural addition** to typsphinx's existing Sphinx builder/writer/translator pipeline, with no new runtime dependencies and minimal changes to the public API surface. The recommended approach is to build the feature atop the v0.8.0 wrapper/content infrastructure that already threads per-master-document context through the entire write phase. The design's closest precedent is Sphinx's own `latex_documents` tuple, which has carried a per-entry theme override since v3.0 — this project is replicating a proven pattern that has been shipped and stable for many years.

The key technical decision — moving the bundled `"typst"` template's copy from `prepare_writing()` (today) to `finish()` (this milestone) — is sound because the write phase depends only on a **path string**, never on file contents. Reusing the existing `self.images`-style accumulator pattern keeps incremental builds efficient and integration straightforward. The change delivers the currently-broken promise that template-relative asset references (`#image("logo.png")`) actually work, by copying the resolved template's entire parent directory wholesale rather than serializing a single file.

**Primary risks** are not architectural but procedural: registry-key validation must be stricter than the existing path-segment guard (rejecting empty, `.`/`..`, Windows-reserved names, case collisions, and multi-segment keys), the directory copy must decide symlink and secrets-file policies explicitly (not relying on stdlib defaults), the `"typst"` built-in bundle must resolve through `importlib.resources` to handle zipimport and wheel-vs-editable-install gaps, and the removal of `typst_template_assets` must include an explicit deprecation warning at `config-inited` time (Sphinx's config system cannot auto-detect a stale value). All of these are low-complexity once understood, and the research has identified the exact code patterns to follow.

## Key Findings

### Recommended Stack

**No new dependencies.** Core technologies (`Sphinx >=9.1`, `typst-py >=0.15.0`, Python 3.12+) are already pinned, and every stdlib module needed (`shutil`, `re`, `importlib.resources`) is either already imported elsewhere in typsphinx or available identically across Python versions in the project's floor (3.12).

Implementation patterns to reuse:

- **Directory copy:** `shutil.copytree(src, dst, dirs_exist_ok=True)` — already in use at `builder.py:1381`; generalize to take an absolute source path for the bundled-package case.
- **Registry-key validation:** `re.fullmatch(r"[A-Za-z0-9_-]+", key)` — follows the existing `derive_typst_lang()` precedent, rejects unsafe path-segment shapes.
- **Built-in template resolution:** `importlib.resources.files("typsphinx") / "templates"` wrapped in an `as_file()` context — required for zipimport correctness and wheel-vs-editable-install correctness.
- **Typst import path:** a `/`-prefixed path resolves against the Typst project root, and `pdf.py:143` / `builder.py:1545` already fix that root at `root=self.outdir` for every compile call. Emitting `#import "/_template/<key>/<entry>.typ": <fn>` therefore resolves from any wrapper nesting depth with one fixed string, rather than computing `../`-depth relative paths.

**Sphinx config validation:** `sphinx.config.ENUM` validates a single scalar against a fixed candidate list and does not apply to a dict-of-dicts shape. The `config-inited` event exists but this codebase has zero existing precedent for it; every existing config-shape error (`typst_elements` unknown key, output-path collisions at `builder.py:611`) is raised from inside `Builder` methods. Registry validation should follow that established pattern — with the deliberate exception noted below for the removed `typst_template_assets`, which has no `Builder`-time hook because Sphinx never surfaces unregistered names at all.

### Expected Features

**Table stakes:**

- Reserved `"typst"` key deferring to existing global config (exact precedent: Sphinx's `latex_documents[4]`)
- Fail-loud `ExtensionError` on unregistered/typo'd keys
- Per-entry bundle copies (template's entire parent directory wholesale)
- N documents sharing one named registry key

**Differentiators:**

- Per-entry `template_function` params dict (typsphinx-specific; no peer tool exposes this)
- Single-build per-document template selection without re-invoking the tool

**Anti-features (explicitly avoided):**

- Per-document language override
- Fixed enum of "blessed" keys
- Silent partial-merge on missing keys

**Precedent detail.** `latex_documents` is a six-element tuple `(startdocname, targetname, title, author, theme, toctree_only)`, and `default_latex_documents()` fills the `theme` slot with `config.latex_theme` — the same "reserved slot defers to global" shape proposed here. That slot was itself widened in Sphinx 3.0 from a loosely-typed `documentclass` string into the strict `theme` registry-key system, which is precisely the change being made to typsphinx's element [4]. Typst Universe's own `[template]` package convention (`path` + `entrypoint`, directory copied wholesale into the consumer) independently validates the wholesale-bundle output rule. MkDocs is the strongest negative precedent — it explicitly refused a within-one-config multi-theme registry — but its output unit is "one site", whereas typsphinx's has been "N PDFs from one build" since v0.8.0.

### Architecture Approach

The feature integrates at two points: the **write phase** resolves each entry's registry key and records it into an accumulator; the **finish phase** consumes the accumulated keys and copies each bundle wholesale to `<outdir>/_template/<key>/`.

Ordering was traced through the real call graph: nothing in the write phase reads `_template.typ` bytes — `render_wrapper()` (writer.py:445) only computes an import-path *string*, and Typst itself reads the bytes at compile time in `TypstPDFBuilder.finish()` (builder.py:1541-1545), later than asset copy. The binding constraint is therefore a write-time accumulator of *used* registry keys, mirroring the existing `self.images` pattern.

**Major components:**

1. **Registry resolver** (new module): validates entries, synthesizes the built-in `"typst"` key, fails loud. Resolution belongs once per build in `write()`, mirroring the existing `_master_include_edges` pattern (builder.py:730) — not per-wrapper, because two entries may share a docname with different keys and config-validation errors should be order-independent.
2. **Template path resolution:** `TemplateEngine.resolve_template()` (template_engine.py:280-336) currently discards the resolved file *path*, returning only content plus a source label. The bundle copy needs the parent directory, so `TemplateResolution` must be widened.
3. **Bundle-copy driver** in `builder.py`: iterates used keys, copies directories. Filesystem orchestration belongs here, not in `template_engine.py` (pure content logic).
4. **Registry-key validation:** rejects empty, `.`/`..`, `/`/`\`, Windows-reserved names, trailing dots/spaces, and case collisions.

Deleting `_write_template_file()` breaks **31 test files** (grep-counted).

### Critical Pitfalls

1. **Registry key validation — reusing `_escapes_outdir()` verbatim is unsafe.** That guard was built for whole relative-path target stems and permits `/` and `..` (legal in a path, illegal in one segment). **Mitigation:** a narrower predicate rejecting multi-segment, empty, `.`/`..`, Windows-reserved-name, trailing-dot/space, and case-collision shapes, using platform-independent string logic.

2. **The directory copy's symlink policy is implicit.** `copytree(..., symlinks=False)` dereferences to anywhere (including outside the template); `symlinks=True` preserves links that can escape published output. **Mitigation:** decide the policy explicitly (reject-if-escaping, or dereference-with-check) and add an `ignore=` callable excluding `.git`, `.DS_Store`, editor backups, and secrets. Note `dirs_exist_ok=True` merges and never prunes, so a re-run leaves stale files behind unless that is handled deliberately.

3. **The built-in `"typst"` bundle is not safely copyable via `Path(__file__).parent`.** `pyproject.toml:73` declares `"typsphinx" = ["templates/*.typ"]`, so any non-`.typ` file added to the built-in bundle silently drops out of the built wheel while working fine in the editable/dev installs that are this project's standard loop. **Mitigation:** resolve through `importlib.resources.files()` / `as_file()`, widen the package-data glob, and add a built-wheel content check in CI.

4. **Relocating `_template.typ` changes Typst's relative-path resolution.** `#image()`, `#bibliography()`, and `read()` resolve relative to the `.typ` file's own location, so moving the template one directory deeper changes what path-relative assets mean. PROJECT.md's own measurement found zero path-relative references in this repository's three real templates (fonts are referenced by *family name*), but no fixture yet proves the **user-template** case survives the move — the built-in-template fixture does not stand in for it. **Mitigation:** a real-compile regression fixture whose user template contains an `#image()` reference, plus corrections to `templates.rst` and `advanced.rst`'s stale `"_templates/refs.bib"` guidance.

5. **The removed `typst_template_assets` config becomes permanently silent.** Sphinx does not warn about unregistered `conf.py` names, and detection cannot be retrofitted later. **Mitigation:** an explicit `config-inited` handler warning when the removed key is present, shipped in the same commit as the removal, with the observable behavioural consequence stated in the CHANGELOG.

## Implications for Roadmap

### Suggested Phase Structure

**Phase 1: Registry resolver & API foundation** — additive only; all new code exists but is not yet used. Delivers `typst_document_templates` config registration, the registry module, and the widened `TemplateEngine.TemplateResolution`.

**Phase 2: Wrapper plumbing (behaviour-preserving refactor)** — point `render_wrapper()` at the registry for the `"typst"` key only; output identical to today. Proves the plumbing works before any layout change.

**Phase 3: Bundle-copy mechanism & layout change** — introduce the new output layout (`_template/<key>/…`), keeping `_write_template_file()` in parallel for now. **RESEARCH FLAG:** the `_template/` prefix collision with the `template_named_dir_master` fixture is an unresolved owner decision and blocks scoping of this phase.

**Phase 4: Test migration** — update the 31 test files' path assertions from `outdir/_template.typ` to the new layout. Add the real-compile regression fixture carrying path-relative assets.

**Phase 5: Deletion of the old mechanism** — delete `_write_template_file()` and the old exact-name collision claim.

**Phase 6: Config cleanup** — delete `typst_template_assets`, `_copy_explicit_assets()`, and `_copy_single_asset()`; add the deprecation warning.

**Phase 7: Documentation** — update `configuration.rst`, `templates.rst`, `advanced.rst`, `output_layout.rst`, `builders.rst`.

This structure is a suggestion derived from dependency order, not a commitment; the roadmapper owns the final shape, including where the five v0.8.0-derived defects land.

### Phase Ordering Rationale

- Phases 1–2 are prerequisites: all code exists before tests are modified.
- Phase 3 is where the open decisions bite (symlink policy, collision-reservation narrowness).
- Phases 4–6 are mechanical once 3 is settled.
- Phase 7 follows the code.

### Research Flags

**Needs deeper planning:** the Phase 3 collision question (prefix narrowness / fixture / alternative prefix).

**Standard patterns (skip phase-level research):** Phases 1, 2, and 4–7 follow existing in-repo patterns.

## Open Decisions Carried Forward

These are unresolved and require owner input before the affected phase can be scoped.

1. **`_template/` prefix reservation vs. a real source directory of the same name.** Today's reservation is an exact-name claim on `_template.typ`; a prefix reservation is a new failure class. `tests/fixtures/template_named_dir_master/` is exactly such a project (`_template/index.rst`, `_template/sub/index.rst`) and its own `conf.py` documents that layout as realistic — "an author holding custom Typst partials in a `_template/` directory, mirroring the tool's own reserved naming." Options: choose a different reserved directory name, or make the collision a loud error and require users to rename their source directory.

2. **Whether `typst_template_assets`'s removal ships with a `config-inited` deprecation warning.** Detection cannot be added later, so this must be decided in the same milestone. It would also be this codebase's first use of `config-inited`.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | No new dependencies; stdlib patterns verified against official docs; versions confirmed live against PyPI |
| Features | HIGH | Sphinx precedent primary-sourced from `configuration.rst`; peer-tool surveys cross-checked |
| Architecture | HIGH | All integration points file:line grounded; build order validated against the 31-test impact |
| Pitfalls | MEDIUM-HIGH | All identified with concrete mitigations; some cross-platform hazards are invisible to a *local* Linux run |

**Overall:** HIGH for architecture and stack; MEDIUM-HIGH for pitfalls.

### Gaps to Address

1. **`_template/` prefix collision** — owner design decision required before the layout phase.
2. **Cross-platform pitfall visibility** — Windows reserved-device failures, case collisions, and symlink-privilege gaps are reachable by the existing three-OS test matrix but invisible to a local Linux-only run; detection logic should additionally be covered by platform-independent string-shape assertions, per this project's existing D-05 precedent.
3. **Wheel-packaging correctness** — the editable install masks the `package-data` glob gap; the bundle-copy phase must include a built-wheel content check.

## Sources

**Research files (synthesis input):**

- `.planning/research/STACK.md`, `FEATURES.md`, `ARCHITECTURE.md`, `PITFALLS.md` (all 2026-08-15)

**Orchestrator corrections applied before synthesis:**

- **CONFIRMED** — `pyproject.toml:73` declares `"typsphinx" = ["templates/*.typ"]`; non-`.typ` files added to the built-in bundle silently drop out of the built wheel.
- **CORRECTED** — PITFALLS.md's claim that no Windows/macOS CI lane exists is false. `.github/workflows/ci.yml:17` declares `os: [ubuntu-latest, windows-latest, macos-latest]`; only the separate `docs-pdf` job is ubuntu-only, and cross-OS docs-PDF coverage is tracked as the deferred requirement XOS-01.

---

*Synthesized 2026-08-15. SUMMARY.md was written by the orchestrator after the synthesizer returned the document inline without writing it (issue #222 false refusal); the previous file on disk was v0.8.0's, from commit `eced72fa`.*
