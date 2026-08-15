# Phase 54: One Bundle Rule — `_template/<key>/`, Per-Document Selection, Four Deletions - Research

**Researched:** 2026-08-15
**Domain:** Sphinx builder/writer file-output-layout change; stdlib directory-copy mechanics;
Typst absolute-path import resolution; Sphinx `config-inited` deprecation detection
**Confidence:** HIGH — every architectural claim below was verified by reading the CURRENT
`typsphinx/*.py` source this session (post-Phase-53), not from the pre-Phase-53
`research/ARCHITECTURE.md` alone (whose line numbers have drifted). Two external mechanisms
(Typst's `/`-absolute path resolution, `importlib.resources.as_file()` directory support) were
confirmed against official documentation this session.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Bundle copy mechanics**

- **D-01:** An existing destination bundle at `<outdir>/_template/<key>/` is **overwritten in
  place, never deleted first**. Files that exist at the destination but no longer exist in the
  source bundle are left alone. This keeps the standing property that this extension performs no
  deletion under `outdir` — measured: `grep -n "rmtree\|os.remove\|unlink" typsphinx/*.py` returns
  exactly one hit, `pdf.py:204`, which unlinks its own temporary file. The consequence to record
  and test around: SC#3's manifest-diff assertion ("no file I didn't expect is present") is a claim
  about a **clean `outdir`**, so its fixture must build into a fresh directory; on an incremental
  rebuild a stale file from a previous bundle can still be present, and that is accepted behaviour,
  not a defect.
- **D-02:** The copy mechanism is **`os.walk(followlinks=False)` + `shutil.copy2` per file** —
  today's `_copy_template_directory()` body with the `.typ` exclusion removed and the
  source/destination re-pointed at the bundle. Measured against a bundle containing an outward
  file symlink, an outward directory symlink, and a self-referential `loop -> .`: this combination
  copies a file symlink's **content**, does **not** descend into a directory symlink (so its
  contents do not reach the output), and cannot loop. The two rejected alternatives were measured
  in the same run — `shutil.copytree(symlinks=False)` wrote ~40 nested copies of the bundle before
  raising `shutil.Error` on the self-referential link, and `copytree(symlinks=True)` would leave
  the published tree dependent on paths outside `outdir`. — **Reversibility:** reversible — the
  choice is confined to one copy helper with no caller-visible contract.
- **D-03:** **BLD-06's symlink clause and ROADMAP SC#3's "refuses, with a named error, a symlink
  whose resolved path is not a descendant of the bundle" are RETRACTED by the owner.** The intent
  behind "copy the bundle wholesale" was the copy itself, not an inverted prohibition on files
  outside the directory; the guard overshot that intent. This phase amends `REQUIREMENTS.md`'s
  BLD-06 text and `ROADMAP.md`'s Phase 54 SC#3 text to drop the symlink half, keeping the
  metadata-exclusion half. No symlink is refused, no named error exists for one, and no test
  asserts one. D-02 is the whole of the answer to "what happens at a symlink." —
  **Reversibility:** reversible — nothing is published against the retracted clause; it was never
  implemented.
- **D-04:** The exclusion set is **exactly the four kinds SC#3 names and nothing more**: `.git`
  (as a directory name), `.DS_Store`, `Thumbs.db`, and editor backups. `.svn`, `.hg`,
  `__pycache__`, `.idea`, `.vscode` are **not** excluded — do not exceed the roadmap text (the
  same stance Phase 53's D-02 took on the registry-key denylist). The manifest-diff test's
  expected set is therefore exactly these four kinds. The concrete glob list for "editor backups"
  is Claude's discretion, subject to being enumerated in the test rather than implied.
- **D-05:** A copy failure is **fatal for the resolved template file itself and non-fatal for
  everything else in the bundle**. Failing to copy the resolved `.typ` raises `ExtensionError`
  naming the registry key and both paths; failing to copy any other bundle file keeps today's
  `logger.warning(f"Failed to copy template asset …")`-and-continue behaviour. Rationale from
  measurement: today the template body never travelled this code path (it was `.typ`-excluded and
  written separately by `_write_template_file()`), so swallowing a failure could not break the
  import; after this phase the wrapper's `#import` points at a file this copy is solely
  responsible for placing, and swallowing the failure leaves `-b typst` reporting success over an
  output that cannot compile.

**CONF-19 — removed-config detection**

- **D-06:** Detection reads **`app.config._raw_config`** from the `config-inited` handler.
  Measured on the installed Sphinx 9.1: `Config._raw_config` holds the `conf.py` namespace dict
  and is cleared only in `__setstate__` (unpickle), so it is live at `config-inited`. This is the
  only mechanism that handles all three names through one path — `typst_authors` (removed v0.7.1)
  and `typst_toctree_defaults` (removed v0.6.3) are already unregistered, so a sentinel-default
  re-registration cannot see them, and re-registering `typst_template_assets` as an inert sentinel
  would contradict PROJECT.md's "this project does not leave inert config registered." The
  private-attribute dependency is accepted; access must be defensive (`getattr(config,
  "_raw_config", {})`) and a test must fail loudly if the attribute disappears, rather than the
  detection silently going quiet.
- **D-07:** Severity is **`logger.warning`, build continues** — REQUIREMENTS.md's CONF-19 text as
  written ("gets a build warning naming its replacement"). Users running `sphinx-build -W` get a
  hard failure for free. `ExtensionError` was rejected: `typst_toctree_defaults` has been gone
  since v0.6.3 and `typst_authors` since v0.7.1, so raising would turn `conf.py` files that have
  built fine for two milestones into hard failures at v0.9.0, exceeding the requirement text.
- **D-08:** The warning carries **no `type`/`subtype`** and is therefore not individually
  suppressible via `suppress_warnings`. Measured: `grep -n "subtype" typsphinx/*.py` returns
  nothing — every `logger.warning` in this extension is a bare call. Tagging only this one would
  make it the extension's sole suppressible warning and open an unsettled naming question for the
  rest.
- **D-09:** Each of the three values gets **its own bespoke message**, not a shared template with
  a substituted replacement, because the replacement relationship is asymmetric and one value has
  no replacement at all. Required content per value: `typst_template_assets` → the bundle is now
  copied wholesale to `_template/<key>/`, the value is ignored, and **more** files reach the
  output than the explicit list used to select; `typst_authors` → use
  `typst_template_function`'s `params` route, the value is ignored, and author
  department/organization/email do not reach the output; `typst_toctree_defaults` → **there is no
  replacement**, it was registered but never read even when it existed, so deleting it changes no
  output. Exact wording is Claude's discretion subject to SC#5's "names the replacement and states
  the observable consequence."
- **D-10:** Recorded consequence, not an open question: `config-inited` fires for **every**
  builder, so this warning appears in `-b html` builds too — including this repository's own
  `docs/source/conf.py`. `app.builder` does not exist yet at `config-inited`, so the handler
  cannot narrow itself to the typst builders. The handler choice is locked by ROADMAP SC#5; this
  is what follows from it.

**BLD-05 — the bundled `"typst"` bundle's non-`.typ` file**

- **D-11:** The non-`.typ` canary is **`typsphinx/templates/README.md`**. Measured:
  `typsphinx/templates/` currently contains `base.typ` and nothing else, so BLD-05's assertion has
  no subject until a file is added. The README describes what the directory is (the `"typst"`
  key's bundle), that it is copied wholesale to `<outdir>/_template/typst/` on every build, and
  how a user registers their own bundle via `typst_document_templates` — so that a reader who
  finds it in their build output understands why it is there. Rejected: adding a real
  path-relative asset to `base.typ`, because ROADMAP constraint #7's measurement (all three real
  templates have zero path-relative references) is load-bearing and SC#3 separately forbids the
  built-in template from standing as OUT-05 evidence, so breaking that measurement buys nothing.
- **D-12:** `pyproject.toml`'s package-data glob becomes **`templates/**/*`**, not `templates/*`.
  A flat glob would silently drop a future `templates/fonts/x.otf` — exactly the failure shape
  BLD-05 exists to prevent. — **Reversibility:** costly — narrowing it back is precisely what
  D-13's CI check is built to catch, and a narrowing that reaches PyPI ships a wheel with a
  missing bundle file.
- **D-13:** The wheel-content check is a **step added to `ci.yml`'s existing `build` job**, placed
  after `uv build` (`.github/workflows/ci.yml:127-151` already builds `dist/` and runs `twine
  check`). It opens the built `.whl` and asserts `typsphinx/templates/README.md` is inside it.
  Rejected: a pytest test that shells out to a build tool — there is no precedent for that in this
  repository, and it would rebuild a wheel on every OS × Python cell of the matrix.

### Claude's Discretion

- **`tests/fixtures/template_named_dir_master/`'s relocation and what carries its regression
  intent forward.** Not discussed; the owner left it to Claude. Measured, the fixture currently
  carries **three** intents simultaneously and none may be silently dropped:
  1. **G-22.1-4 / CR-01** — a master whose own directory is literally named `_template`. Under
     OUT-06's root-absolute import (SC#1) the string-equality dependence that caused the original
     malformed `"..typ"` / `"../.typ"` import disappears structurally, and under OUT-07 this exact
     docname layout becomes an `ExtensionError`. The natural successor is a **negative** test
     asserting the build stops and names the offending docname.
  2. **BLD-02 / OUT-01** — two `typst_documents` entries against one docname tree with two
     distinct bare targets (`template-dir-master.typ`, `template-dir-sub.typ`), which the
     fixture's own `conf.py` documents as load-bearing, not a rename.
  3. **CONF-09 (Phase 44.2 SC#3)** — per-master author-leak detection, the two entries' authors
     deliberately diverging (`"Test Author"` vs `"Test Author (nested)"`).
     `tests/test_multi_master_metadata_no_leak.py:48` and `tests/test_template_import_path.py:236`
     both reference the fixture directory by path and must be updated together.
  ROADMAP constraint #1 forecloses one option: do not re-open "choose a different reserved
  directory name." Also avoid `_templates/` as the replacement directory name — it is Sphinx's own
  `templates_path` default.
- The exact glob list for D-04's "editor backups."
- Exact wording of D-09's three messages and D-05's `ExtensionError`.
- Where the `config-inited` handler lives (`__init__.py` alongside the config registration,
  versus a module of its own).
- How the write-time used-key accumulator is stored on the builder (ROADMAP constraint #4 names
  `self.images` as the pattern to mirror).
- Test file naming and placement, and the composition of the OUT-05 user-template asset fixture,
  subject to SC#3's requirement that it be a real `sphinx-build → typst.compile()` fixture
  recorded RED against the pre-relocation tree.

### Deferred Ideas (OUT OF SCOPE)

- **Later milestone — VCS/tooling metadata beyond SC#3's four kinds.** D-04 leaves `.svn`, `.hg`,
  `__pycache__`, `.idea`, `.vscode` copied into the output bundle. Cheap to add as further
  exclusion patterns whenever wanted; deliberately not in Phase 54.
- **Later milestone — `suppress_warnings` subtypes for this extension.** D-08 declines to tag
  CONF-19's warning because it would be the only tagged warning here. Tagging the extension's
  warnings as a set is a coherent piece of work; tagging one is not.
- **Later milestone — stale-bundle cleanup on incremental rebuilds.** D-01 accepts that a file
  removed from a source bundle can linger at the destination. Introducing deletion under `outdir`
  is a distinct decision with its own blast radius and belongs on its own.
- **Adjacent cleanup — `writer.py:176-221` `_compute_template_import_path()` is dead code**
  (carried forward from Phase 53's deferred list; line numbers re-measured this session — see
  §Architecture below). Phase 54 removes the depth-counting import path, so this function should
  fall out naturally; if it does not, it is still not this milestone's responsibility to chase.
- Out of scope for THIS phase specifically (per `54-CONTEXT.md`'s `<domain>` block): the five
  v0.8.0-derived defects (Phase 55); the documentation rewrite describing this new layout
  (Phase 56); version bump and CHANGELOG (Phase 57).

</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| TPL-02 | User can select a named template per output document via element [4] of a `typst_documents` entry | Already partially wired by Phase 53: `render_wrapper()` (writer.py:267-486) already accepts a `template_entry: TemplateRegistryEntry \| None` and builds its `TemplateEngine` from it, never from raw `config`. What is still MISSING is that every used key's bundle actually reaches `outdir` (currently only the "typst" key's content is written, via the now-to-be-deleted `_write_template_file()`) — see §Architecture Integration Points 1-3. |
| CONF-19 | A `conf.py` still setting a removed config value gets a build warning naming its replacement | See §Code Examples "config-inited handler" and D-06 through D-10. This is this codebase's first `config-inited` handler — verified: `grep -n "config-inited\|config_inited" typsphinx/*.py` returns nothing today. |
| OUT-04 | Every used key's template bundle is copied wholesale to `<outdir>/_template/<key>/`, `"typst"` under the same rule | See §Architecture Integration Points 2-3 and the NEW Pitfall (srcdir-shadow whole-tree copy) below — the built-in `"typst"` key needs explicit attention because it bypasses Phase 53's CONF-17 parent-directory guard entirely. |
| OUT-05 | A template-relative asset reference resolves because the template sits inside its own copied bundle | Needs a NEW fixture — measured (again) this session that `typsphinx/templates/base.typ` and the two custom templates under `examples/` and `docs/source/_typst/` use font-family references only (`grep` below), so none is evidence for this SC. |
| OUT-06 | A wrapper imports its own template by a path that does not depend on the wrapper's nesting depth | CONFIRMED against Typst's own documentation this session (see §Code Examples "Root-absolute import path"): "An absolute path always resolves relative to the root of the project," and `pdf.py:143`/`builder.py:1660` already compile with `root=self.outdir` for every call. |
| OUT-07 | `_template/` is reserved output space; a source tree that would write there stops the build | `_validate_output_path_collisions()` (builder.py:517-628) currently claims the exact string `"_template.typ"` at line 586 — a prefix-reservation rule is a new predicate, not a widening of `_claim()`'s existing exact-match semantics. See §Architecture. |
| BLD-05 | A non-`.typ` file belonging to the bundled `"typst"` template is present in the built wheel | `pyproject.toml:72-73` currently declares `"typsphinx" = ["templates/*.typ"]` — confirmed this session by direct read. D-11/D-12/D-13 are the fix. |
| BLD-06 | The bundle copy excludes VCS and OS metadata (symlink clause retracted by D-03) | See D-02/D-04 and §Code Examples "Exclusion-aware directory copy." |

</phase_requirements>

## Summary

Phase 53 already did the hard plumbing: `typsphinx/template_registry.py` resolves
`typst_document_templates` into `TemplateRegistryEntry` objects (including a synthesized
`"typst"` entry that mirrors today's four global config values byte-for-byte), and
`render_wrapper()` (writer.py) already builds its `TemplateEngine` from a threaded-in
`template_entry` rather than reading `config` directly. **Nothing in Phase 54 needs to touch the
registry-resolution or per-wrapper-parameter machinery** — that is DONE and independently
re-verified (`53-VERIFICATION.md`, 5/5 truths, re-measured live this session's predecessor).

What Phase 54 actually does is narrower than it first reads: (1) change what `render_wrapper()`
computes as the import-path STRING (root-absolute instead of depth-relative — a one-function
change, `compute_template_import_path_for_dir()`, writer.py:69-106), (2) add a write-time
accumulator of used registry keys (mirroring the already-present `self.images` pattern, one line
in `init()` plus one line in the existing wrapper-writing loop, builder.py:1185-1207), (3) add a
NEW `finish()`-time copy driver that, for each used key with a `template` (not `package`), copies
`TemplateEngine.resolve_template().path.parent` wholesale to `<outdir>/_template/<key>/`
(generalizing the EXISTING `_copy_template_directory()` body, builder.py:1378-1432, whose `.typ`
skip is the only change needed to that function's copy loop itself — its signature also needs to
accept an absolute source directory, since the bundled `"typst"` key's source lives inside the
installed package, not under `srcdir`), and (4) delete four now-dead mechanisms
(`_write_template_file()`, the `.typ` exclusion inside `_copy_template_directory()`,
`copy_template_assets()`'s three early returns, and `typst_template_assets` with its two helper
functions) plus widen the collision reservation from an exact-string claim to a prefix claim
(OUT-07) and add the CONF-19 `config-inited` handler.

**One genuinely new risk surfaced by this session's own code read, not named anywhere in
CONTEXT.md, ROADMAP.md, or the pre-Phase-53 research artifacts:** the synthesized `"typst"`
registry entry is built OUTSIDE the validation loop that applies CONF-17 (`parent directory ==
srcdir` rejection) to every user-DECLARED key. A project with no `typst_template` set but a stray
file literally named `base.typ` sitting at the root of `srcdir` triggers
`TemplateEngine.resolve_template()`'s Priority-2 "search" branch — a real, intentionally-supported
feature (the `<srcdir>/base.typ` "shadow" override, directly tested at
`tests/test_template_engine.py:235-247`) — and its resolved template's PARENT DIRECTORY is
`srcdir` itself. Applying OUT-04's rule naively ("copy the resolved template's parent directory
wholesale") to that case means copying the user's **entire Sphinx source tree** —
`conf.py`, every `.rst` file, `_static/`, everything — into `<outdir>/_template/typst/`. See
§Common Pitfalls, "Pitfall 0" below; this needs an owner decision before or during planning, not a
silent implementation choice.

**Primary recommendation:** treat this as four small, independently-testable edits layered onto
Phase 53's already-shipped plumbing — (a) the import-path string, (b) the accumulator, (c) the
copy driver (generalizing existing code, with the srcdir-shadow guard added), (d) the four
deletions plus the OUT-07 prefix widening and the CONF-19 handler — sequenced so the tree stays
green at each step, mirroring the additive → behaviour-preserving → layout-change → deletion
order Phase 53 itself already modeled successfully.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Registry key → template resolution | Backend (Sphinx builder, Python) | — | `resolve_template_registry()` / `resolve_registry_key()` — pure Python, already shipped (Phase 53), unchanged this phase |
| Bundle directory copy (`_template/<key>/`) | Backend (Sphinx builder, Python/filesystem) | — | New `finish()`-time driver; stdlib `os`/`shutil`/`importlib.resources` only |
| Import-path string computation | Backend (Sphinx writer, Python) | Compile-time (Typst) | Python computes the STRING; Typst's own compiler resolves it against `root=` at compile time — two tiers cooperate, neither alone is sufficient |
| `_template/` prefix collision reservation | Backend (Sphinx builder, Python) | — | Extends `_validate_output_path_collisions()`, a pure pre-write validation pass |
| Deprecated-config detection | Backend (Sphinx extension setup, `config-inited` event) | — | New integration point (this codebase's first), fires for every builder including `-b html` |
| Wheel packaging / CI content check | Build/Packaging (setuptools, GitHub Actions) | — | `pyproject.toml` glob + a CI step; no runtime code |
| Typst project-root resolution for the compiled import | Compile-time (Typst, via `typst-py`) | Backend (`pdf.py`'s `root=` argument) | Already correct — `pdf.py:143` / `builder.py:1660` pass `root=self.outdir` unconditionally today; Phase 54 relies on this, does not need to change it |

Not a frontend UI milestone (confirmed: no template, translator, or output-format change touches
DOM/browser/CDN tiers — everything is Python build-time orchestration plus a markup language
compiled server-side).

## Standard Stack

### Core

**Zero new runtime dependencies.** Every mechanism this phase needs is stdlib, already available
at the project's Python 3.12 floor (`pyproject.toml:10`, `requires-python = ">=3.12"`):

| Module | Purpose | Why Standard |
|--------|---------|--------------|
| `shutil` | `shutil.copy2` per-file copy inside the walk (already used, `builder.py:9`) | Preserves mtime/permissions; already the project's established copy primitive for both images and template assets |
| `os` | `os.walk(followlinks=False)` — the walk itself; `os.path` helpers | Already used throughout `builder.py`; `followlinks=False` is `os.walk`'s own DEFAULT, so D-02 requires no new argument, only removing the `.typ` skip |
| `posixpath` | Comparison-only path normalization via the existing `_collision_key()` (builder.py:438-515) | Already the project's single collision-comparison primitive; the new `_template/` prefix reservation should route through it, not a second one |
| `importlib.resources` | Resolve the `"typst"` key's bundle directory (`typsphinx/templates/`) loader-agnostically | **NEW use in this codebase** (confirmed: `grep -rn "importlib.resources" typsphinx/` returns nothing today) — `importlib.resources.files("typsphinx") / "templates"` plus `importlib.resources.as_file(...)` (directory support added in Python 3.12 — CITED: docs.python.org, "Changed in version 3.12: Added support for _traversable_ representing a directory") is the loader-agnostic replacement for `template_engine.py:284` (`get_default_template_path()`)'s current `Path(__file__).parent / "templates"` |

### Supporting

Nothing new. `Dict`/`List`/`Set`/`Tuple` from `typing` stay in use per CLAUDE.md's explicit
deferral of the `UP006`/`UP035` typing-import modernization — do not "clean up" `builder.py`'s
`from typing import Dict, List, Set, Tuple` (line 12) while touching this file for other reasons.

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `os.walk` + `shutil.copy2` (D-02, kept) | `shutil.copytree()` | REJECTED by owner decision, measured: `symlinks=False` wrote ~40 nested copies of a self-referential-symlink bundle before raising `shutil.Error`; `symlinks=True` would publish an escaping symlink verbatim. `os.walk(followlinks=False)` neither follows nor loops. |
| `importlib.resources.files()`/`as_file()` (new, needed) | `Path(__file__).parent` (today's approach, `template_engine.py:284`) | `Path(__file__).parent` breaks under a non-filesystem loader (zipimport/frozen); `importlib.resources` is the portable stdlib answer and costs one import. Directory support requires Python ≥3.12 — this project's floor already meets that. |
| `config-inited` event handler (new, needed) | A Sphinx `add_config_value()` sentinel re-registration | REJECTED per D-06: `typst_authors`/`typst_toctree_defaults` are ALREADY unregistered from prior milestones, so a sentinel-default re-registration cannot see a `conf.py` that still sets them — only reading `_raw_config` handles all three names through one mechanism. |

**Installation:** none — this phase adds no dependency. No `pip install`/`uv add` command applies.

## Package Legitimacy Audit

**Not applicable — this phase installs zero external packages.** ROADMAP binding constraint #11
states "zero new runtime dependencies (`shutil`, `re`, `importlib.resources` are stdlib and this
project's floor is 3.12)," confirmed directly this session: `importlib.resources` requires no
`pyproject.toml` `dependencies` change, and no new PyPI/npm/crates package name appears anywhere
in this phase's scope. The Package Legitimacy Gate protocol (`gsd-tools query package-legitimacy
check`) has nothing to check against.

## Architecture Patterns

### System Architecture Diagram

```
conf.py: typst_document_templates{}, typst_documents[]
        │
        ▼
write()                                                    [builder.py:755-870, UNCHANGED entry]
  ├─ _validate_output_path_collisions()                    [517-628 — OUT-07 widens _claim("_template.typ")
  │                                                           to a "_template/" PREFIX reservation]
  ├─ self._document_template_registry =
  │     resolve_template_registry(config, srcdir)           [Phase 53, UNCHANGED]
  ├─ _validate_registry_key_references()                    [630-694, Phase 53, UNCHANGED]
  ├─ prepare_writing(docnames)                               [739-753]
  │     └─ DELETE: self._write_template_file() call          [was line 753]
  ├─ self._master_include_edges = _build_include_edge_map()  [Phase 49, UNCHANGED]
  └─ for docname in sorted(docnames):
        write_doc(docname) → _write_typst_files(docname)     [1112-1207]
          ├─ write CONTENT file (docname.typ)                 [UNCHANGED, 1140-1148]
          └─ for each typst_documents entry naming docname:
                template_entry = resolve_registry_key(...)     [1195-1197, Phase 53, UNCHANGED]
                NEW ─▶ self._used_template_keys.add(template_entry.key)
                wrapper = writer.render_wrapper(
                    entry, doctree, wrapper_relative_dir,
                    content_relative_path, edge_keys,
                    template_entry=template_entry)              [writer.py:267-486]
                    │
                    NEW ─▶ template_file = compute_root_absolute_import_path(
                                template_entry.key,
                                <resolved template's own filename>)
                            → "/_template/<key>/<filename>.typ"  (OUT-06)
                write wrapper file
        ▼
finish()                                                    [builder.py:1508-1516]
  ├─ copy_image_files()                                      [UNCHANGED]
  └─ NEW ─▶ _copy_used_template_bundles()
              for key in self._used_template_keys:
                entry = self._document_template_registry[key]
                if entry.template is None: continue            # package-only → nothing to copy
                resolution = TemplateEngine(...).resolve_template()  # Phase 53's .path field
                bundle_src = resolution.path.parent
                  # "typst" key, no override: importlib.resources.files("typsphinx")/"templates"
                  # "typst" key, srcdir/base.typ shadow: bundle_src == srcdir ── SEE PITFALL 0
                  # declared key: already CONF-17-validated ≠ srcdir/ancestor at write() time
                bundle_dst = outdir/_template/<key>/
                copy_bundle(bundle_src, bundle_dst)             # os.walk(followlinks=False)
                                                                  # + shutil.copy2, skip .git/
                                                                  # .DS_Store/Thumbs.db/backups
                     resolved .typ copy fails → ExtensionError (fatal, D-05)
                     any other file copy fails → logger.warning, continue (D-05)
        ▼
TypstPDFBuilder.finish()                                    [builder.py:1519-...]
  └─ super().finish()  (runs the above)
  └─ compile_typst_file_to_pdf(wrapper, root_dir=self.outdir)  [builder.py:1660, pdf.py:110-153]
       typst.compile(typ_path, root=root_dir)                  [pdf.py:143, UNCHANGED]
       → Typst resolves "/_template/<key>/…" against root=outdir regardless of
         the wrapper's own nesting depth (OUT-06) — CONFIRMED against typst.app docs:
         "An absolute path always resolves relative to the root of the project."
```

### Recommended Project Structure

No new files under `typsphinx/` are architecturally required beyond what's already planned
(`typsphinx/templates/README.md`, D-11). New test fixtures land under `tests/fixtures/` following
this project's existing one-fixture-per-scenario convention (e.g.
`tests/fixtures/user_template_relative_asset_gate/` for OUT-05,
`tests/fixtures/template_bundle_manifest_diff_gate/` for BLD-06 — names are Claude's discretion
per CONTEXT.md).

### Component Responsibilities (current file:line, measured this session)

| Component | Location (verified this session) | Current role | Phase 54 change |
|---|---|---|---|
| `_write_template_file()` | `builder.py:1224-1294` | Writes `_template.typ` to outdir root once per build | **DELETE ENTIRELY**, plus its call site at `builder.py:753` inside `prepare_writing()` |
| `copy_template_assets()` | `builder.py:1334-1376` | Three early returns (`typst_template` unset → return; `typst_package` set → return; `typst_template_assets == []` → return) | **DELETE the three early returns**; becomes (or is replaced by) the accumulator-driven driver |
| `_copy_template_directory()` | `builder.py:1378-1432` | `os.walk` + `shutil.copy2`, **skips `.typ` files** (1411-1413), signature takes a SRCDIR-relative `template_path: str` | Remove the `.typ` skip; generalize the signature to accept an ABSOLUTE `src_dir`/`dest_dir` pair (the bundled `"typst"` source is not srcdir-relative) |
| `_copy_explicit_assets()` / `_copy_single_asset()` | `builder.py:1434-1506` | Serve `typst_template_assets`'s explicit-list mode; `_copy_single_asset` uses `shutil.copytree(dirs_exist_ok=True)` (line 1496) | **DELETE BOTH** — no caller remains once `typst_template_assets` is unregistered |
| `finish()` | `builder.py:1508-1516` | `self.copy_image_files(); self.copy_template_assets()` | Point the second line at the new accumulator-driven driver |
| `init()` | `builder.py:222-260` | Initializes `self.images`, `self._master_include_edges`, `self._document_template_registry` (Phase 53) | Add `self._used_template_keys: set[str] = set()` |
| `_write_typst_files()` wrapper loop | `builder.py:1185-1207` | Already resolves `template_entry = resolve_registry_key(...)` (line 1195) and threads it into `render_wrapper()` | Add ONE line: `self._used_template_keys.add(template_entry.key)` |
| `_validate_output_path_collisions()` | `builder.py:517-628` | `_claim("_template.typ", …)` at line 586 — exact-string claim | Replace with a `_template/`-PREFIX reservation predicate (any content/wrapper path whose first `/`-segment is `_template`) — a materially different (prefix- vs exact-match) rule, needs its own function, not a widened `_claim()` call |
| `compute_template_import_path_for_dir()` | `writer.py:69-106` | Computes `"../"*depth + "_template.typ"` — depth-only, assumes ONE global file at outdir root | Replace with a root-absolute computation taking the resolved key + the template's own filename: `f"/_template/{key}/{filename}"` — no depth counting at all under OUT-06 |
| `_compute_template_import_path()` (static method) | `writer.py:176-221` | Already **dead code** — zero non-docstring callers, confirmed this session via `grep -n "_compute_template_import_path" typsphinx/*.py tests/*.py` (only definition + its own docstring reference `writer.py:221`) | Not this phase's responsibility to delete (per Deferred Ideas), but do not mistake it for the function needing generalization — that's `compute_template_import_path_for_dir` |
| `render_wrapper()` | `writer.py:267-486` | Already builds `TemplateEngine` from `resolved_entry` (Phase 53); still computes `template_file` via the OLD depth-only helper at line 480 | Change line 480's call to the new root-absolute computation; everything else in this method is unchanged |
| `TemplateEngine.get_default_template_path()` | `template_engine.py:276-288` | `Path(__file__).parent / "templates" / "base.typ"` (line 284) — plain filesystem path | Route through `importlib.resources.files("typsphinx") / "templates" / "base.typ"` (SC#2 requirement) |
| `TemplateEngine.TemplateResolution.path` | `template_engine.py:37-65` | Already carries the resolved `Path` (Phase 53); NOT yet consumed by any write-path code | This phase is its FIRST consumer — `resolution.path.parent` is the bundle source directory |
| `__init__.py:58` | `app.add_config_value("typst_template_assets", None, "html", [list, type(None)])` | Registers the config value | **DELETE this line**, in the SAME commit as the `config-inited` handler (binding constraint #3) |
| `pdf.py:143` | `typst.compile(typ_path, root=root_dir)` | Already passes `root=` unconditionally | **UNCHANGED** — this is what makes OUT-06's root-absolute import work for free at compile time |
| `builder.py:1660` | `compile_typst_file_to_pdf(typ_file, root_dir=self.outdir)` | Already passes `root_dir=self.outdir` | **UNCHANGED** |
| `pyproject.toml:72-73` | `[tool.setuptools.package-data]` `"typsphinx" = ["templates/*.typ"]` | `.typ`-only glob | Widen to `templates/**/*` (D-12) |
| `.github/workflows/ci.yml:127-154` | `build` job: `uv build` (line 143) → `twine check dist/*` (line 148) | No content-inspection step | Add a step after `uv build` that opens the wheel and asserts `typsphinx/templates/README.md` is present (D-13) |

### Pattern 1: Write-time accumulator, finish-time consumer (already established in this codebase)

**What:** Collect state during the per-docname write loop into a `self.<name>` attribute
initialized in `init()`; consume it, once, in `finish()`.
**When to use:** Any time `finish()` needs to know something that is only fully known after
`write()`'s loop has run over the (possibly incremental) `docnames` set.
**Example (existing precedent, `self.images`):**
```python
# builder.py:231 (init())
self.images: dict[str, str] = {}

# builder.py:1308 (post_process_images/_track_image, during write())
self.images[key] = resolved_uri

# builder.py:1296-1332 (copy_image_files, called from finish())
for imguri, override_src in self.images.items():
    ...
```
The new `self._used_template_keys: set[str] = set()` follows this exact shape — see
Component Responsibilities table above for the three touch points.

### Pattern 2: Root-absolute Typst import path (NEW mechanism this phase introduces)

**What:** Instead of counting `../` by wrapper nesting depth, emit a path beginning with `/`,
which Typst resolves against its own project root (set via `root=` at compile time), not against
the importing file's own directory.
**When to use:** Any future cross-file reference that must be nesting-depth-independent — this
phase's only user is the wrapper's `#import` line, but the mechanism generalizes.
**Verified (CITED: typst.app official docs, fetched this session):**
> "A relative path resolves in relation to the parent directory of the Typst file where the
> function is called." … "An absolute path always resolves relative to the root of the project."
> … "If you wish to use another folder as the root of your project, you can use the CLI's
> `--root` flag."
`typst-py`'s `typst.compile(path, root=root_dir)` is the Python-API equivalent of `--root`, and
this project already calls it with `root=self.outdir` unconditionally (`pdf.py:143`,
`builder.py:1660`) — this phase changes ZERO lines in `pdf.py`.

### Anti-Patterns to Avoid

- **Reusing `_escapes_outdir()`/`_is_drive_qualified()` for the `_template/`-prefix collision
  check:** Phase 53's own `template_registry.py` docstring (lines 9-22) already documents WHY
  these two are the wrong tool for a single-segment question; the SAME reasoning applies here in
  reverse — this is a PREFIX-match question over an already-resolved relative path, not a
  path-segment-shape question, so neither existing helper is the right building block. Route
  through `_collision_key()`'s existing normalize-then-casefold comparison (already the sole
  normalization primitive `_validate_output_path_collisions()` uses).
- **Treating the "typst" key's bundle copy as "the same as every declared key" without
  re-checking the parent-directory shape:** see Pitfall 0 below — the synthesized entry
  structurally skips CONF-17.
- **Widening `_claim("_template.typ", …)` in place instead of adding a genuinely new prefix
  predicate:** the existing function only ever compares one exact string against one exact
  string; a prefix reservation is a different shape of check (needs `startswith` semantics on the
  first `/`-segment, post-normalization) and conflating the two invites a silent regression in
  the non-prefix collision cases `_validate_output_path_collisions()` already correctly handles.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Copy a directory tree while excluding VCS/OS metadata and never following an escaping symlink | A new recursive walker, or `shutil.copytree(ignore=...)` | Extend the EXISTING `_copy_template_directory()` `os.walk(followlinks=False)` + `shutil.copy2` loop with a name-based skip predicate for the four D-04 kinds | `shutil.copytree` was explicitly measured and rejected (D-02) in both symlink modes; `os.walk(followlinks=False)` is already this codebase's proven-correct symlink behaviour and needs no new code for that half |
| Resolve a bundled package data directory across install shapes (editable, wheel, zipapp) | `Path(__file__).parent`-based path math (today's `template_engine.py:284`) | `importlib.resources.files("typsphinx") / "templates"` + `importlib.resources.as_file(...)` | Loader-agnostic stdlib mechanism; directory support since Python 3.12 (this project's own floor); `Path(__file__)` silently breaks under zipimport |
| Detect a removed `conf.py` setting Sphinx no longer registers | A `conf.py` AST/source scan, or re-registering the value as an inert sentinel default | `config-inited` event handler reading `getattr(config, "_raw_config", {})` | Sphinx has no built-in "deprecated config key" mechanism (confirmed: no `add_config_value` variant for this); `_raw_config` is the one place the raw pre-lookup namespace is still visible, and re-registering a sentinel cannot see values ALREADY unregistered from prior milestones (`typst_authors`, `typst_toctree_defaults`) |
| Compute a nesting-depth-independent cross-file reference | A second depth-counting helper parameterized differently, or a symlink-farm trick at the filesystem layer | Typst's own `/`-absolute path resolution against `root=` | This is a compiler-level feature that exists precisely for this use case; the project ALREADY passes `root=self.outdir` to every compile call, so no new plumbing is needed on the Python side at all |

**Key insight:** every mechanism this phase needs is either (a) an existing, already-proven
in-repo pattern generalized slightly, or (b) a stdlib/compiler capability that already exists and
requires zero new abstraction. There is no genuinely novel infrastructure to design here — the
risk in this phase is entirely in getting the DELETIONS and the ORDERING right (see Common
Pitfalls), not in inventing new copy/resolution machinery.

## Common Pitfalls

### Pitfall 0 (NEW — not named in CONTEXT.md, ROADMAP.md, or prior research): The synthesized `"typst"` key can bypass CONF-17 and wholesale-copy the ENTIRE `srcdir`

**What goes wrong:** `resolve_template_registry()` (`template_registry.py:448-467`) synthesizes
the built-in `"typst"` entry OUTSIDE the `for key in sorted(declared.keys(), ...)` validation
loop that applies CONF-17 (`_violates_conf17()`, lines 137-175: rejects a `template` whose parent
directory IS `srcdir` or an ancestor of it) to every user-DECLARED key. If a project has NOT set
`typst_template`, `TemplateEngine(template_path=None, search_paths=[srcdir], ...)` still runs its
normal three-priority walk; Priority 2 checks `Path(srcdir) / "base.typ"` — and if a file
literally named `base.typ` sits at the root of `srcdir` (an intentional, tested, documented
override mechanism — see below), `resolve_template().path` is `srcdir / "base.typ"`, whose
**parent directory is `srcdir` itself**. OUT-04's literal rule ("the resolved template's parent
directory is copied wholesale") applied naively to this case means copying every `.rst` file,
`conf.py`, `_static/`, and anything else under `srcdir` into `<outdir>/_template/typst/`.

**Why it happens:** this `<srcdir>/base.typ` "shadow" resolution is not a hypothetical edge case
— it is directly tested, intentional behaviour: `tests/test_template_engine.py:235-247`
(`test_resolve_template_search_path`) asserts `resolution.path == srcdir / "base.typ"` for exactly
this configuration, and `template_engine.py`'s own docstrings (lines 53-54, 296-297, 375-382)
describe it as "the `<srcdir>/base.typ` shadow of the bundled default." Before Phase 54, this
resolution only ever fed `_write_template_file()`'s `load_template()` call — which reads the
file's CONTENT, never its directory — so the shadow feature was harmless. Phase 54 is the FIRST
code path to ever ask "what is this resolved template's PARENT DIRECTORY," and the synthesized
key was never subject to the guard that would catch this (CONF-17 explicitly measures `parent ==
srcdir` as the exact shape to reject, for every OTHER key).

**How to avoid:** the bundle-copy driver should apply the SAME `_violates_conf17()`-style
parent-directory check (or an equivalent explicit guard) to the RESOLVED path of every key,
including the synthesized `"typst"` entry, before copying — not only to keys that went through
`resolve_template_registry()`'s declared-key loop. The planner must decide the failure mode: (a)
`ExtensionError` (consistent with CONF-17's existing severity for declared keys, but changes
behaviour for existing `conf.py` files using the shadow feature — a genuine breaking change worth
naming explicitly if chosen), (b) `logger.warning` + skip the bundle copy for that key only (the
wrapper's `#import` would then reference a file that was never copied — likely a WORSE outcome, a
Typst compile fatal with no clear cause), or (c) something narrower, e.g. detect specifically
`resolved_parent == srcdir` and degrade to "copy nothing, template stays effectively inlined" —
but this contradicts OUT-04's "no exceptions" framing. **This is an Open Question for the owner,
not a silent implementation choice** — none of the 13 locked CONTEXT.md decisions addresses it,
and it does not fit cleanly under any of them.

**Warning signs:** a test suite that only exercises the `typst_template` (explicit path) and
"nothing set → bundled default" shapes for the `"typst"` key's bundle copy, and never exercises
"nothing set AND a stray `base.typ` exists at `srcdir` root." A code review that assumes
`resolve_template_registry()`'s existing validation already covers the `"typst"` key because it
covers every OTHER key.

**Phase to address:** THIS phase (Phase 54) — it is the first phase where the resolved parent
directory has any consequence at all.

---

### Pitfall 1 (from `research/PITFALLS.md`, still applicable — re-verified this session)

**What goes wrong:** `shutil.copytree()`'s symlink defaults are both wrong for this use case in
different directions — see D-02 for the measured numbers (a ~40-file blowup on
`symlinks=False` against a self-referential link; an escaping symlink published verbatim under
`symlinks=True`).

**How to avoid:** ALREADY DECIDED by D-02 — reuse `_copy_template_directory()`'s existing
`os.walk(followlinks=False)` + `shutil.copy2` body, removing only the `.typ` skip. No new design
work is needed here; this pitfall is fully closed by the locked decision, restated here only so a
planner does not accidentally reintroduce `copytree`.

**Phase to address:** Phase 54 (already resolved by D-02; this entry documents WHY, for anyone
reviewing the resulting diff).

---

### Pitfall 2 (from `research/PITFALLS.md`, still applicable): Deleting `typst_template_assets` from `add_config_value()` is permanently silent without the paired handler

**What goes wrong:** Sphinx has no reverse "this name used to be registered" mechanism — a
`conf.py` still setting `typst_template_assets = [...]` builds successfully with zero diagnostic,
silently doing something different (the whole bundle now copies unconditionally, regardless of
what the old explicit list said).

**How to avoid:** ALREADY DECIDED — D-06 through D-10 lock the `config-inited` + `_raw_config`
mechanism, its severity (warning, not error), its lack of a `subtype`, and its three bespoke
messages. The paired constraint (binding constraint #3): the handler MUST ship in the SAME commit
as the `add_config_value` line's deletion — detection cannot be retrofitted after the fact (there
is no way to tell, post-hoc, whether a historical build silently ignored the setting).

**Phase to address:** Phase 54 (already resolved by D-06..D-10).

---

### Pitfall 3 (from `research/PITFALLS.md`, still applicable, PARTIALLY unresolved by Phase 53): Wheel packaging glob + `Path(__file__).parent`

**What goes wrong:** confirmed AGAIN this session — `pyproject.toml:72-73` still declares
`"typsphinx" = ["templates/*.typ"]`, and `template_engine.py:284`'s
`get_default_template_path()` still uses `Path(__file__).parent / "templates" / "base.typ"`, not
`importlib.resources`. Both are exactly as PITFALLS.md described them before Phase 53 (Phase 53
did not touch either — confirmed: neither file's Phase-53 diff region includes these lines).

**How to avoid:** ALREADY DECIDED — D-11/D-12/D-13 (add `templates/README.md`, widen the glob to
`templates/**/*`, add the CI wheel-content-check step) plus the SC#2 requirement that the
`"typst"` bundle resolve through `importlib.resources`, not `Path(__file__).parent`.

**Phase to address:** Phase 54 (this is the phase; not yet closed as of this research).

---

### Pitfall 4 (from `research/PITFALLS.md`, still applicable): Relocating the template changes Typst's own relative-path resolution for `#image()`/`#bibliography()`/`read()`

**What goes wrong:** any relative asset reference inside a custom template resolves against the
TEMPLATE FILE's own directory, not the compile root — moving the file changes what a relative
reference resolves against. Re-measured this session: `grep -rn "#image(\|#bibliography(\|read(" \
typsphinx/templates/base.typ examples/*/_templates/*.typ docs/source/_typst/*.typ` finds font
references by FAMILY NAME only in all three real templates in this repository (unchanged from the
pre-Phase-53 measurement) — so the known blast radius for THIS repo's own templates is genuinely
zero, but that also means no existing fixture proves the relocation doesn't break a real
path-relative reference.

**How to avoid:** ALREADY DECIDED — OUT-05 requires a NEW real-compile fixture with a
user-supplied template referencing a same-directory asset by relative path, recorded RED against
the pre-relocation tree (SC#3). The built-in template is explicitly disallowed as evidence for
this SC (per ROADMAP SC#3's own text).

**Phase to address:** Phase 54 (this phase; the fixture is new work, not yet built).

---

### Pitfall 5 (measured this session, cross-cutting with the 33-file migration): The exact migration-set size has drifted from the pre-Phase-53 research count

**What goes wrong:** `research/ARCHITECTURE.md` §4 (written before Phase 53) counted 31 files;
ROADMAP.md's binding constraint #2 says "31 test files ... grep-counted"; `54-CONTEXT.md`'s
`<canonical_refs>` section says "The 33 files matching `grep -rln \"_template.typ\" tests/`" and
explicitly instructs "measure at plan time rather than trusting either number." **Measured fresh
this session:** `grep -rl "_template.typ" tests/ | wc -l` → **33** — 6 fixture `conf.py` files
plus 27 test modules (full list below). This is 2 MORE than the pre-Phase-53 count of 31, because
Phase 53 itself added a new file that also asserts `_template.typ`:
`tests/test_registry_prewrite_validation_gate.py`, plus `tests/test_docs_contract_claims_gate.py`
was not present in the old count either.

**How to avoid:** trust this session's fresh count (33), not either older number, when sizing the
migration. Full list, measured this session:

```
tests/fixtures/admonition_greyscale_probe/conf.py
tests/fixtures/bld02_template_clobber_gate/conf.py
tests/fixtures/derived_template_collision_gate/conf.py
tests/fixtures/explicit_template_collision_gate/conf.py
tests/fixtures/package_only_config_gate/conf.py
tests/fixtures/template_named_dir_master/conf.py
tests/test_admonition_greyscale_pipeline.py
tests/test_builder_output_stem.py
tests/test_collision_predicate_completeness_gate.py
tests/test_default_typst_documents_gate.py
tests/test_docs_contract_claims_gate.py
tests/test_empty_typst_documents_optout_gate.py
tests/test_entry_metadata_route_uniformity.py
tests/test_examples_charged_ieee_gate.py
tests/test_external_link_style_render_gate.py
tests/test_heading_depth_render_gate.py
tests/test_integration_advanced.py
tests/test_integration_basic.py
tests/test_nested_master_render_gate.py
tests/test_output_layout_docs_gate.py
tests/test_package_only_config_gate.py
tests/test_package_template_routing.py
tests/test_readthedocs_config.py
tests/test_registry_prewrite_validation_gate.py
tests/test_signature_overflow_render_gate.py
tests/test_signature_page_boundary_render_gate.py
tests/test_target_name_render_gate.py
tests/test_template_assets.py
tests/test_template_engine.py
tests/test_template_import_path.py
tests/test_two_layer_output_gate.py
tests/test_typst_documents_collision_gate.py
tests/test_typst_lang_gate.py
```

**Phase to address:** Phase 54 — plan the migration wave(s) against this 33-file list, not the
30/31/32-number claims in earlier artifacts.

## Code Examples

### Root-absolute import path (replaces `compute_template_import_path_for_dir`)

```python
# writer.py — CURRENT (69-106), depth-only, replace this shape:
def compute_template_import_path_for_dir(wrapper_relative_dir: str) -> str:
    if not wrapper_relative_dir:
        depth = 0
    else:
        depth = len(PurePosixPath(wrapper_relative_dir).parts)
    return "".join(["../"] * depth) + "_template.typ"

# NEEDED shape (illustrative — exact naming/signature is Claude's discretion,
# subject to OUT-06's contract: the returned string must be IDENTICAL for the
# same key regardless of wrapper_relative_dir):
def compute_template_import_path(key: str, template_filename: str) -> str:
    """Root-absolute import path -- resolves via Typst's own `root=`
    handling (pdf.py:143), never by counting the wrapper's own nesting
    depth (OUT-06)."""
    return f"/_template/{key}/{template_filename}"
```

### Exclusion-aware directory copy (generalizes `_copy_template_directory`)

```python
# builder.py — CURRENT (1378-1432) walks src_dir (srcdir-relative) and
# skips ONLY .typ files. Needed: an absolute-path signature (the "typst"
# key's source is not srcdir-relative) and a name-based exclusion set
# for D-04's exactly-four kinds instead of the .typ skip:

_EXCLUDED_BUNDLE_NAMES = {".git", ".DS_Store", "Thumbs.db"}  # + backup glob, Claude's discretion

def _is_excluded_bundle_entry(name: str) -> bool:
    if name in _EXCLUDED_BUNDLE_NAMES:
        return True
    # editor-backup glob list -- e.g. name.endswith("~") or name.endswith(".swp")
    ...
    return False

for root, dirs, files in os.walk(src_dir, followlinks=False):  # unchanged default
    dirs[:] = [d for d in dirs if not _is_excluded_bundle_entry(d)]
    for file in files:
        if _is_excluded_bundle_entry(file):
            continue
        # ... shutil.copy2 as today, with D-05's fatal-vs-warn split for
        # the resolved template file itself vs. every other bundle file
```

### `importlib.resources` for the bundled `"typst"` key (replaces `Path(__file__).parent`)

```python
# template_engine.py — CURRENT (276-288):
def get_default_template_path(self) -> str:
    package_dir = Path(__file__).parent
    template_dir = package_dir / "templates"
    default_template = template_dir / "base.typ"
    return str(default_template)

# NEEDED (CITED: docs.python.org, directory support since Python 3.12):
import importlib.resources

def get_default_template_path(self) -> str:
    resource = importlib.resources.files("typsphinx") / "templates" / "base.typ"
    with importlib.resources.as_file(resource) as real_path:
        return str(real_path)
    # NOTE: as_file()'s context manager may clean up a TEMPORARY extraction
    # on exit for a non-filesystem loader (e.g. zip) -- a caller needing the
    # DIRECTORY to persist for a subsequent os.walk() copy (the bundle-copy
    # driver) must keep the `with importlib.resources.as_file(...)` block
    # open around the ENTIRE copy operation, not just the path lookup.
```

### `config-inited` handler (this codebase's first)

```python
# __init__.py — setup(app) currently has no config-inited connection at all
# (confirmed: grep -n "config-inited\|config_inited\|connect(" typsphinx/*.py
# returns nothing today).

_REMOVED_CONFIG_VALUES = {
    "typst_template_assets": "...D-09's bespoke message...",
    "typst_authors": "...D-09's bespoke message...",
    "typst_toctree_defaults": "...D-09's bespoke message (no replacement)...",
}

def _warn_removed_config_values(app, config) -> None:
    # D-06: defensive getattr -- fail LOUDLY if the private attribute
    # disappears in a future Sphinx, per D-06's own instruction, rather
    # than silently going quiet. (Exact assertion shape is a planning
    # decision -- e.g. a dedicated test importing sphinx.config.Config
    # and asserting hasattr(Config, "_raw_config").)
    raw = getattr(config, "_raw_config", {})
    for name, message in _REMOVED_CONFIG_VALUES.items():
        if name in raw:
            logger.warning(message)  # D-08: no `type=`/`subtype=` kwargs

def setup(app: Sphinx) -> Dict[str, Any]:
    ...
    app.connect("config-inited", _warn_removed_config_values)
    ...
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|---------------|--------|
| One shared `_template.typ` at outdir root, imported via depth-counted `../` | Per-key bundle at `<outdir>/_template/<key>/`, imported via root-absolute `/` path | Phase 54 (this phase) | `typst_documents` element [4] becomes load-bearing (TPL-02); a hand-run `typst compile` needs `--root <outdir>` (documented as a Phase 56 doc obligation, per `54-CONTEXT.md`'s "Specific Ideas") |
| `typst_template_assets` explicit allow-list selects which non-`.typ` files reach output | Whole bundle directory (minus 4 excluded kinds) always reaches output | Phase 54 | Strictly MORE files reach output than before for any project that used the explicit-list mode (D-09's required message text names this) |
| Global `typst_template`/`typst_package` applied to every master uniformly | Per-`typst_documents`-entry selection via registry key | Phase 53 (registry) + Phase 54 (actual selection effect) | An existing untouched `conf.py` is unaffected (byte-identical, TPL-03/TPL-04); a `conf.py` that starts using element [4] gets true per-document templates |

**Deprecated/outdated:**
- `_write_template_file()`, `_copy_explicit_assets()`, `_copy_single_asset()`: deleted this phase.
- `typst_template_assets` config value: deleted this phase (with paired detection).
- `Path(__file__).parent`-based bundle resolution for the `"typst"` key: replaced by
  `importlib.resources` this phase.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Editor-backup exclusion glob list composition is left fully to Claude's discretion (per CONTEXT.md), so this research does not prescribe one | Common Pitfalls / Code Examples | Low — CONTEXT.md explicitly delegates this; any reasonable, enumerated glob (`*~`, `*.swp`, `*.bak`, `*.orig`) satisfies D-04's "exactly the four KINDS" framing as long as it stays within the "editor backups" kind and is tested against the enumerated list, not implied |
| A2 | The `config-inited` handler's exact registration location (`__init__.py` vs. a new module) has no functional bearing, only organizational | Common Pitfalls / Code Examples | Low — CONTEXT.md marks this Claude's discretion explicitly |
| A3 | `TemplateEngine.resolve_template().path` (Phase 53's `.path` field) is sufficient as the sole source for "the resolved template's parent directory" needed by OUT-04's copy driver, with no second lookup mechanism needed | Architecture / Code Examples | Medium — if the bundle-copy driver is implemented as a NEW independent call to `TemplateEngine` rather than reusing the ALREADY-resolved `TemplateResolution` from the write-time lookup, a race is impossible (both reads are pure functions of `config`/`srcdir`, unchanged between write() and finish()) but doing the resolution work TWICE (once implicitly inside `render_wrapper()`, once explicitly in the copy driver) is a minor inefficiency, not a correctness risk — flagged here so the planner considers whether to thread the resolved `Path` through the accumulator instead of re-deriving it in `finish()` |

## Open Questions

1. **How should the bundle-copy driver treat the synthesized `"typst"` key's resolved parent
   directory when it equals `srcdir` (the `<srcdir>/base.typ` shadow case, Pitfall 0)?**
   - What we know: this is a real, tested, intentionally-supported override mechanism
     (`tests/test_template_engine.py:235-247`), and applying OUT-04's rule naively would copy the
     entire source tree into published output — a severe, previously-unnamed risk.
   - What's unclear: whether the owner wants this treated as a NEW CONF-17-shaped build error
     (a genuine, if narrow, breaking change for any project currently relying on the shadow
     feature with no `typst_template` set), a warning-and-skip, or some other narrower guard.
   - Recommendation: surface this explicitly during `/gsd-discuss-phase` or at plan time as a new
     locked decision — do not let a planner or executor silently choose a default. Given the
     owner's established preference (both phases) for guards justified by explicit, measured
     harm, and this harm being both measured and severe (whole-srcdir copy, potential secret/
     content leakage via `conf.py`), an `ExtensionError` mirroring CONF-17's existing text seems
     the most consistent default recommendation, but this is a recommendation, not a decision.

2. **Should the accumulator thread the ALREADY-resolved `TemplateResolution` (from
   `render_wrapper()`'s per-wrapper `TemplateEngine` construction) into `finish()`, or should the
   bundle-copy driver re-derive it independently per key?**
   - What we know: both are pure functions of `(config, srcdir)` given the same registry entry,
     so re-deriving is not a correctness risk — only a minor duplicate-computation cost, once per
     used key per build (not per wrapper).
   - What's unclear: which shape the planner prefers stylistically — `self._used_template_keys:
     set[str]` (simplest, mirrors `self.images`' shape most directly) vs. `self._used_template_
     entries: dict[str, TemplateResolution]` (avoids re-resolving, but is a bigger accumulator
     than the `self.images` precedent this phase is asked to mirror).
   - Recommendation: `set[str]` of keys is simplest and matches ROADMAP constraint #4's explicit
     naming of `self.images` as the pattern to mirror (a `dict[str, str]` of comparable
     simplicity, not a resolution-object cache) — re-deriving via
     `self._document_template_registry[key]` plus a fresh `TemplateEngine(...).resolve_template()`
     call in `finish()` is cheap (file I/O for one small `.typ` file, once per used key) and keeps
     the accumulator itself trivial.

## Environment Availability

No new external tool/service dependency. `uv build` and `twine check` (D-13's CI step context)
are already present and working in `.github/workflows/ci.yml`'s `build` job (lines 127-154,
confirmed this session). The worktree-isolated execution mode (CLAUDE.md, "standing execution
mode") applies unchanged: every command in this phase's plans/executors must run via
`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` then `uv run <command>`.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest ≥8.4 (`pyproject.toml:35`), config at `pyproject.toml:75-84` |
| Config file | `pyproject.toml` (`[tool.pytest.ini_options]`) |
| Quick run command | `uv run pytest tests/test_<module>.py -x` |
| Full suite command | `uv run pytest tests/ -q` (measured baseline this session's predecessor: `1270 passed, 5 skipped in 109.29s`) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| TPL-02 | Two masters naming two different registry keys produce two visibly-different-templates PDFs in one build | integration (real `sphinx-build -b typstpdf`) | `uv run pytest tests/test_two_template_selection_gate.py -x` (name Claude's discretion) | ❌ Wave 0 — new fixture with two registry keys needed |
| CONF-19 | `conf.py` still setting a removed value gets a named `logger.warning` | unit (caplog) | `uv run pytest tests/test_removed_config_deprecation_warning.py -x` (name Claude's discretion) | ❌ Wave 0 |
| OUT-04 | Every used key's bundle lands at `_template/<key>/`; `"typst"` under the same rule; a `package`-only or unused key copies nothing | integration (real `sphinx-build`, filesystem assertions) | `uv run pytest tests/test_bundle_copy_layout_gate.py -x` (name Claude's discretion) | ❌ Wave 0 |
| OUT-05 | A NEW user-template `#image("logo.png")` fixture compiles green via real `typst.compile()`, recorded RED pre-relocation | integration (GATE-01-shaped real compile) | `uv run pytest tests/test_user_template_relative_asset_gate.py -x` (name Claude's discretion) | ❌ Wave 0 — the fixture itself does not exist yet (measured: `grep -rln "image(" examples/*/_templates docs/source/_typst` finds none) |
| OUT-06 | Root master and nested master naming the SAME key emit an identical import string | unit or integration | Extends `tests/test_template_import_path.py` (already in the 33-file migration set) | ✅ file exists, needs new assertions |
| OUT-07 | A source tree writing under `_template/` stops the build, naming the docname | integration (negative) | Extends/replaces `template_named_dir_master`'s successor fixture's own test | ❌ Wave 0 — successor fixture per Claude's Discretion |
| BLD-05 | Built wheel contains a non-`.typ` bundle file | CI-only (not pytest) | `.github/workflows/ci.yml` `build` job, new step per D-13 | ❌ Wave 0 (CI step, not a test file) |
| BLD-06 | Copy excludes exactly the four D-04 kinds; manifest-diff, not presence-only | integration (filesystem fixture with `.git`/`.DS_Store`/`Thumbs.db`/backup files present) | `uv run pytest tests/test_bundle_copy_exclusion_manifest_gate.py -x` (name Claude's discretion) | ❌ Wave 0 |

### Sampling Rate

- **Per task commit:** the specific test file(s) touched, via `uv run pytest tests/test_X.py -x`
- **Per wave merge:** `uv run pytest tests/ -q` plus `uv run black --check .`, `uv run ruff check
  .`, `uv run mypy typsphinx/` (matches CI exactly, per CLAUDE.md's "Commands" section)
- **Phase gate:** full suite green before `/gsd-verify-work`, PLUS `git ls-remote --heads origin
  gsd/v0.9.0-per-document-templates` confirming the milestone branch stays current (standing
  milestone invariant #5, paid every phase since Phase 43)

### Wave 0 Gaps

- [ ] `tests/fixtures/<two-key-selection-fixture>/` + its test module — covers TPL-02
- [ ] `tests/<removed-config-deprecation-warning-test>.py` — covers CONF-19
- [ ] `tests/<bundle-copy-layout-gate>.py` (or extend an existing `*_render_gate.py`) — covers
      OUT-04, including the package-only-copies-nothing and unused-key-copies-nothing cases
- [ ] `tests/fixtures/<user-template-relative-asset-fixture>/` + its test module — covers OUT-05,
      MUST be recorded RED against the pre-relocation tree per SC#3 (a genuine GATE-01-shaped
      fixture, not a synthetic assertion)
- [ ] `tests/fixtures/<template_named_dir_master successor>/` — covers OUT-07's negative case AND
      carries forward the three regression intents enumerated in CONTEXT.md's Claude's Discretion
      section (G-22.1-4/CR-01, BLD-02/OUT-01, CONF-09)
- [ ] `tests/<bundle-copy-exclusion-manifest-gate>.py` — covers BLD-06, manifest-diff shaped (not
      presence-only), fixture containing `.git`, `.DS_Store`, `Thumbs.db`, and at least one
      editor-backup-shaped file
- [ ] `.github/workflows/ci.yml` `build` job step — covers BLD-05 (not a pytest file; a CI step
      per D-13)
- [ ] A test asserting `hasattr(sphinx.config.Config, "_raw_config")` or equivalent, per D-06's
      "must fail loudly if the attribute disappears" instruction
- [ ] Coverage for Pitfall 0 (the `srcdir`-shadow whole-tree-copy risk) — contingent on the Open
      Question #1 resolution; whatever guard is chosen needs its own regression fixture

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-------------------|
| V2 Authentication | No | This extension has no authentication surface — it is a Sphinx build-time extension with no network-facing service |
| V3 Session Management | No | No session concept applies |
| V4 Access Control | No | No multi-user access-control surface |
| V5 Input Validation | Yes | Registry-key shape validation (Phase 53's `_validate_registry_key_shape`, unchanged this phase) PLUS this phase's NEW `_template/`-prefix collision reservation and the bundle-copy exclusion predicate — both are input-validation-shaped controls over user-authored `conf.py` values and user-authored template-bundle directory contents |
| V6 Cryptography | No | No cryptographic operation anywhere in this extension |
| V12 File and Resources (ASVS-adjacent; this project's own established idiom) | Yes | Path-traversal / escape prevention for filesystem copy operations — this project's own established pattern (`_escapes_outdir()`, `_is_drive_qualified()`, `_collision_key()`) already treats every `conf.py`-derived path value as untrusted input requiring validation BEFORE any `path.join()`/`mkdir()`/copy call touches it (per `research/PITFALLS.md`'s own Security Mistakes table, "Validate BEFORE any `path.join()`/`mkdir()` call touches the key") |

### Known Threat Patterns for This Stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|----------------------|
| A malicious or careless template bundle directory contains a symlink pointing outside itself | Information Disclosure | RETRACTED as an explicit guard by owner decision D-03 — mitigated only incidentally by D-02's chosen copy mechanism (`os.walk(followlinks=False)` does not descend into a directory symlink, so its contents never reach the output; a FILE symlink's target CONTENT is copied, which is the accepted, measured behaviour) |
| A template bundle directory contains `.git`, `.DS_Store`, `Thumbs.db`, or editor backup files that leak into published output | Information Disclosure | D-04's four-kind exclusion — **residual risk, owner-accepted, worth naming explicitly**: a `.env` file, an API key file, or any OTHER kind of sensitive file sitting in a user's template bundle directory is NOT excluded by D-04's exactly-four-kinds rule (deliberately, per the same "do not exceed the roadmap text" stance as Phase 53's registry-key denylist) — this is an accepted residual, not an oversight, but should be visible in the shipped documentation (Phase 56) as "the bundle is copied wholesale minus four specific exclusions; keep it clean" |
| The `"typst"` registry key's synthesized entry copies the entire `srcdir` (Pitfall 0) | Information Disclosure / Denial of Service (large/slow copy) | **UNRESOLVED — see Open Question #1.** This is the single highest-severity finding of this research session: a project relying on the intentionally-supported `<srcdir>/base.typ` shadow feature with no explicit `typst_template` set would have its ENTIRE source tree (including `conf.py`, which may contain non-public configuration) copied into published build output |
| A registry key or a `typst_documents` target string is crafted to escape `outdir` via `..`/absolute/drive-qualified shapes | Tampering / Elevation of Privilege (filesystem write outside intended tree) | Already fully covered by Phase 44/47/53's existing `_escapes_outdir()`/`_is_drive_qualified()`/CONF-18 machinery — UNCHANGED by this phase, confirmed no new escape vector is introduced by the `_template/`-prefix reservation (it only WIDENS what counts as a claimed/reserved output path, never narrows an existing escape check) |

## Sources

### Primary (HIGH confidence)

- `typsphinx/builder.py` (full read of lines 1-260, 420-1207, 1550-1610 this session; line numbers
  cited throughout this document are measured against the CURRENT post-Phase-53 file, not the
  pre-Phase-53 research artifacts)
- `typsphinx/writer.py` (full read, 487 lines, this session)
- `typsphinx/template_engine.py` (lines 1-100, 195-350, 595-715, this session)
- `typsphinx/template_registry.py` (full read, 529 lines, this session — Phase 53's shipped module)
- `typsphinx/pdf.py` (full read, 230 lines, this session)
- `typsphinx/__init__.py` (full read, 70 lines, this session)
- `pyproject.toml` (lines 1-90, this session)
- `.github/workflows/ci.yml` (lines 124-156, this session)
- `tests/test_template_engine.py` (lines 225-254, this session — the `srcdir`-shadow test that
  grounds Pitfall 0)
- `tests/fixtures/template_named_dir_master/conf.py` (full read, this session)
- `.planning/phases/53-template-registry-foundation/53-VERIFICATION.md` (full read — confirms
  Phase 53's actual shipped state, not merely its plan)
- `.planning/phases/54-.../54-CONTEXT.md` (full read — 13 locked decisions, treated as binding)
- `.planning/REQUIREMENTS.md`, `.planning/STATE.md`, `.planning/ROADMAP.md` (relevant sections
  read this session)
- Direct grep measurements this session: `grep -rl "_template.typ" tests/` (33 files, listed
  above), `grep -rn "importlib.resources" typsphinx/` (zero hits), `grep -n "config-inited\|
  config_inited" typsphinx/*.py` (zero hits), `grep -n "rmtree\|os.remove\|unlink"
  typsphinx/*.py` (one hit, `pdf.py:204`)

### Secondary (MEDIUM confidence)

- Typst official documentation, `typst.app/docs/reference/foundations/path/` (fetched this
  session via WebFetch) — "An absolute path always resolves relative to the root of the project"
  — grounds OUT-06's entire mechanism
- Python official documentation, `docs.python.org/3/library/importlib.resources.html` (fetched
  this session via WebFetch) — "Changed in version 3.12: Added support for _traversable_
  representing a directory" for `importlib.resources.as_file()`

### Tertiary (LOW confidence, carried forward for context only, not re-verified this session)

- `.planning/research/ARCHITECTURE.md` (pre-Phase-53 — its line numbers have drifted; used only
  for cross-checking the INTEGRATION POINTS list, not for any file:line citation in this document)
- `.planning/research/PITFALLS.md` (pre-Phase-53 — Pitfalls 1-4 above are RESTATEMENTS confirmed
  still applicable this session, not fresh re-derivations; Pitfall 0 is NEW, found this session)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — zero new dependencies, every mechanism confirmed against either the
  current source tree or official documentation this session
- Architecture: HIGH — every file:line citation was read directly this session against the
  CURRENT (post-Phase-53) source, not inherited from stale research
- Pitfalls: HIGH for Pitfalls 1-5 (grounded in direct measurement); HIGH for Pitfall 0 (grounded
  in a direct test-file quote, `tests/test_template_engine.py:247`) but the RESOLUTION for
  Pitfall 0 is an Open Question, not a researched answer — this is honestly represented as unmet,
  not silently assumed

**Research date:** 2026-08-15
**Valid until:** Until Phase 54 code lands (this research is tied to a specific commit's source
tree, `611382b7` per Phase 53's verification — any further commits to `typsphinx/*.py` before
Phase 54 planning begins should trigger a re-grep of the line-number citations above, not a
wholesale re-research)
