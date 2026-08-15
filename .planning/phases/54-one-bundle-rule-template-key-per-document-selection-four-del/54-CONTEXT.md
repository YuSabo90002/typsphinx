# Phase 54: One Bundle Rule — `_template/<key>/`, Per-Document Selection, Four Deletions - Context

**Gathered:** 2026-08-15
**Status:** Ready for planning

<domain>
## Phase Boundary

The output layout becomes one rule with no exceptions — **every used registry key's template
bundle (the resolved template's parent directory) is copied wholesale to
`<outdir>/_template/<key>/`** — and `typst_documents` element [4] therefore actually selects which
template typesets which document. Because the bundle copy carries the template verbatim
(`resolve_template()` reads the file with no substitution), four mechanisms are **deleted rather
than extended**: `_write_template_file()` entirely, `_copy_template_directory()`'s `.typ`
exclusion, `copy_template_assets()`'s three early returns, and `typst_template_assets` with
`_copy_explicit_assets()` / `_copy_single_asset()`.

In scope: TPL-02, CONF-19, OUT-04, OUT-05, OUT-06, OUT-07, BLD-05, BLD-06. The write-time
accumulator of used keys feeding a `finish()`-time copy; the root-absolute template import path;
the `_template/` prefix reservation; migration of the 32 test files asserting the root
`_template.typ`; relocation of `tests/fixtures/template_named_dir_master/`; the new user-template
asset fixture for OUT-05; the wheel-content check for BLD-05; the `config-inited` handler for
CONF-19; and the two requirement-text amendments recorded in D-03 below.

Out of scope (Phase 55): the five v0.8.0-derived defects. Out of scope (Phase 56): the
documentation rewrite that describes this layout. Out of scope (Phase 57): version bump and
CHANGELOG.

</domain>

<decisions>
## Implementation Decisions

### Bundle copy mechanics

- **D-01:** An existing destination bundle at `<outdir>/_template/<key>/` is **overwritten in place, never deleted first**. Files that exist at the destination but no longer exist in the source bundle are left alone. This keeps the standing property that this extension performs no deletion under `outdir` — measured: `grep -n "rmtree\|os.remove\|unlink" typsphinx/*.py` returns exactly one hit, `pdf.py:204`, which unlinks its own temporary file. The consequence to record and test around: SC#3's manifest-diff assertion ("no file I didn't expect is present") is a claim about a **clean `outdir`**, so its fixture must build into a fresh directory; on an incremental rebuild a stale file from a previous bundle can still be present, and that is accepted behaviour, not a defect.
- **D-02:** The copy mechanism is **`os.walk(followlinks=False)` + `shutil.copy2` per file** — today's `_copy_template_directory()` body with the `.typ` exclusion removed and the source/destination re-pointed at the bundle. Measured against a bundle containing an outward file symlink, an outward directory symlink, and a self-referential `loop -> .`: this combination copies a file symlink's **content**, does **not** descend into a directory symlink (so its contents do not reach the output), and cannot loop. The two rejected alternatives were measured in the same run — `shutil.copytree(symlinks=False)` wrote ~40 nested copies of the bundle before raising `shutil.Error` on the self-referential link, and `copytree(symlinks=True)` would leave the published tree dependent on paths outside `outdir`. — **Reversibility:** reversible — the choice is confined to one copy helper with no caller-visible contract.
- **D-03:** **BLD-06's symlink clause and ROADMAP SC#3's "refuses, with a named error, a symlink whose resolved path is not a descendant of the bundle" are RETRACTED by the owner.** The intent behind "copy the bundle wholesale" was the copy itself, not an inverted prohibition on files outside the directory; the guard overshot that intent. This phase amends `REQUIREMENTS.md`'s BLD-06 text and `ROADMAP.md`'s Phase 54 SC#3 text to drop the symlink half, keeping the metadata-exclusion half. No symlink is refused, no named error exists for one, and no test asserts one. D-02 is the whole of the answer to "what happens at a symlink". — **Reversibility:** reversible — nothing is published against the retracted clause; it was never implemented.
- **D-04:** The exclusion set is **exactly the four kinds SC#3 names and nothing more**: `.git` (as a directory name), `.DS_Store`, `Thumbs.db`, and editor backups. `.svn`, `.hg`, `__pycache__`, `.idea`, `.vscode` are **not** excluded — do not exceed the roadmap text (the same stance Phase 53's D-02 took on the registry-key denylist). The manifest-diff test's expected set is therefore exactly these four kinds. The concrete glob list for "editor backups" is Claude's discretion, subject to being enumerated in the test rather than implied.
- **D-05:** A copy failure is **fatal for the resolved template file itself and non-fatal for everything else in the bundle**. Failing to copy the resolved `.typ` raises `ExtensionError` naming the registry key and both paths; failing to copy any other bundle file keeps today's `logger.warning(f"Failed to copy template asset …")`-and-continue behaviour. Rationale from measurement: today the template body never travelled this code path (it was `.typ`-excluded and written separately by `_write_template_file()`), so swallowing a failure could not break the import; after this phase the wrapper's `#import` points at a file this copy is solely responsible for placing, and swallowing the failure leaves `-b typst` reporting success over an output that cannot compile.

### CONF-19 — removed-config detection

- **D-06:** Detection reads **`app.config._raw_config`** from the `config-inited` handler. Measured on the installed Sphinx 9.1: `Config._raw_config` holds the `conf.py` namespace dict and is cleared only in `__setstate__` (unpickle), so it is live at `config-inited`. This is the only mechanism that handles all three names through one path — `typst_authors` (removed v0.7.1) and `typst_toctree_defaults` (removed v0.6.3) are already unregistered, so a sentinel-default re-registration cannot see them, and re-registering `typst_template_assets` as an inert sentinel would contradict PROJECT.md's "this project does not leave inert config registered". The private-attribute dependency is accepted; access must be defensive (`getattr(config, "_raw_config", {})`) and a test must fail loudly if the attribute disappears, rather than the detection silently going quiet.
- **D-07:** Severity is **`logger.warning`, build continues** — REQUIREMENTS.md's CONF-19 text as written ("gets a build warning naming its replacement"). Users running `sphinx-build -W` get a hard failure for free. `ExtensionError` was rejected: `typst_toctree_defaults` has been gone since v0.6.3 and `typst_authors` since v0.7.1, so raising would turn `conf.py` files that have built fine for two milestones into hard failures at v0.9.0, exceeding the requirement text.
- **D-08:** The warning carries **no `type`/`subtype`** and is therefore not individually suppressible via `suppress_warnings`. Measured: `grep -n "subtype" typsphinx/*.py` returns nothing — every `logger.warning` in this extension is a bare call. Tagging only this one would make it the extension's sole suppressible warning and open an unsettled naming question for the rest.
- **D-09:** Each of the three values gets **its own bespoke message**, not a shared template with a substituted replacement, because the replacement relationship is asymmetric and one value has no replacement at all. Required content per value: `typst_template_assets` → the bundle is now copied wholesale to `_template/<key>/`, the value is ignored, and **more** files reach the output than the explicit list used to select; `typst_authors` → use `typst_template_function`'s `params` route, the value is ignored, and author department/organization/email do not reach the output; `typst_toctree_defaults` → **there is no replacement**, it was registered but never read even when it existed, so deleting it changes no output. Exact wording is Claude's discretion subject to SC#5's "names the replacement and states the observable consequence".
- **D-10:** Recorded consequence, not an open question: `config-inited` fires for **every** builder, so this warning appears in `-b html` builds too — including this repository's own `docs/source/conf.py`. `app.builder` does not exist yet at `config-inited`, so the handler cannot narrow itself to the typst builders. The handler choice is locked by ROADMAP SC#5; this is what follows from it.

### BLD-05 — the bundled `"typst"` bundle's non-`.typ` file

- **D-11:** The non-`.typ` canary is **`typsphinx/templates/README.md`**. Measured: `typsphinx/templates/` currently contains `base.typ` and nothing else, so BLD-05's assertion has no subject until a file is added. The README describes what the directory is (the `"typst"` key's bundle), that it is copied wholesale to `<outdir>/_template/typst/` on every build, and how a user registers their own bundle via `typst_document_templates` — so that a reader who finds it in their build output understands why it is there. Rejected: adding a real path-relative asset to `base.typ`, because ROADMAP constraint #7's measurement (all three real templates have zero path-relative references) is load-bearing and SC#3 separately forbids the built-in template from standing as OUT-05 evidence, so breaking that measurement buys nothing.
- **D-12:** `pyproject.toml`'s package-data glob becomes **`templates/**/*`**, not `templates/*`. A flat glob would silently drop a future `templates/fonts/x.otf` — exactly the failure shape BLD-05 exists to prevent. — **Reversibility:** costly — narrowing it back is precisely what D-13's CI check is built to catch, and a narrowing that reaches PyPI ships a wheel with a missing bundle file.
- **D-13:** The wheel-content check is a **step added to `ci.yml`'s existing `build` job**, placed after `uv build` (`.github/workflows/ci.yml:127-151` already builds `dist/` and runs `twine check`). It opens the built `.whl` and asserts `typsphinx/templates/README.md` is inside it. Rejected: a pytest test that shells out to a build tool — there is no precedent for that in this repository, and it would rebuild a wheel on every OS × Python cell of the matrix.

### Shadow-template location (owner decision taken at plan-phase, after 54-RESEARCH.md's Open Question #1)

- **D-14:** The `<srcdir>/base.typ` shadow route **moves into a directory: its source-side location becomes `<srcdir>/_typst/base.typ`**, so that the resolved template's parent is a genuine bundle directory and OUT-04's one rule applies to the synthesized `"typst"` key with **zero exceptions**. The problem this closes, measured: `writer.py:382` and `builder.py:1279` pass `search_paths=[srcdir]`, `template_engine.py:329-331` resolves `<srcdir>/base.typ` as Priority 2, and Phase 53's CONF-17 guard `_violates_conf17()` runs only inside `template_registry.py:419-424`'s declared-entry loop while the synthesized `"typst"` entry is appended after it at `:458` — so a shadow project's **entire source tree** would be the bundle and would be copied wholesale into `<outdir>/_template/typst/`. `tests/fixtures/typst_lang_gate/srcdir_shadow_lang/` (`base.typ` + `conf.py` + `index.rst`) is a real, currently-green `-b typstpdf` real-compile fixture that hits exactly this. `search_paths` therefore becomes `[<srcdir>/_typst]` and `srcdir` itself is **removed** from it — leaving `srcdir` in as a fallback would preserve the hole verbatim. The directory name `_typst/` is this repository's own precedent and not a new invention: `docs/source/conf.py:96` already sets `typst_template = "_typst/custom_template.typ"`, and `docs/source/_typst/` is the only such directory in the tree; `_templates/` stays excluded for the reason already recorded below (Sphinx's own `templates_path` default). Rejected alternatives, both measured: copying the single resolved file instead of its parent when the parent is `srcdir` (adds exactly one recorded exception to a phase whose SC#2 says `"typst"` is under the same rule), and extending CONF-17's `ExtensionError` to the synthesized key (turns `tests/test_typst_lang_gate.py:624,632` RED and deletes a route documented at `docs/source/user_guide/templates.rst:213` and `configuration.rst:325`). — **Reversibility:** costly — the shadow route's path is a published, documented contract; undoing it after v0.9.0 ships is a second breaking change for every user who moved their file. The owner took this decision explicitly; it does not earn a second `checkpoint:decision`.
**Retracted at plan time — D-15 (runtime warning for the relocated shadow route).** A companion decision was drafted here that would have had D-06's `config-inited` handler also warn when `<srcdir>/base.typ` exists while `<srcdir>/_typst/base.typ` does not. **The owner removed it.** The relocation's announcement is therefore documentation-only: the pages and the v0.9.0 breaking-change changelog entry that `54-03` writes. The accepted consequence, recorded rather than left implicit: a shadow project that upgrades to v0.9.0 without reading the changelog gets a PDF typeset by the bundled default instead of its own template, with **no build-time diagnostic**. `54-06`'s threat row T-54-24 carries this as `accept`, not `mitigate`. Do not re-introduce the warning as an "obvious improvement" during execution.

**Consequences of D-14 the plans must carry (each measured, none optional):** `tests/fixtures/typst_lang_gate/srcdir_shadow_lang/base.typ` → `.../srcdir_shadow_lang/_typst/base.typ` (the two tests at `tests/test_typst_lang_gate.py:624,632` stay green by relocation, not by rewrite); `tests/test_template_engine.py:235-247` (`test_resolve_template_search_path`) updates the directory it plants `base.typ` in; `docs/source/user_guide/templates.rst:213` and `docs/source/user_guide/configuration.rst:325` change `<srcdir>/base.typ` → `<srcdir>/_typst/base.typ`; the changelog gains a v0.9.0 breaking-change entry for the moved route.

### Claude's Discretion

- **`tests/fixtures/template_named_dir_master/`'s relocation and what carries its regression intent forward.** Not discussed; the owner left it to Claude. Measured, the fixture currently carries **three** intents simultaneously and none may be silently dropped:
  1. **G-22.1-4 / CR-01** — a master whose own directory is literally named `_template`. Under OUT-06's root-absolute import (SC#1) the string-equality dependence that caused the original malformed `"..typ"` / `"../.typ"` import disappears structurally, and under OUT-07 this exact docname layout becomes an `ExtensionError`. The natural successor is a **negative** test asserting the build stops and names the offending docname.
  2. **BLD-02 / OUT-01** — two `typst_documents` entries against one docname tree with two distinct bare targets (`template-dir-master.typ`, `template-dir-sub.typ`), which the fixture's own `conf.py` documents as load-bearing, not a rename.
  3. **CONF-09 (Phase 44.2 SC#3)** — per-master author-leak detection, the two entries' authors deliberately diverging (`"Test Author"` vs `"Test Author (nested)"`). `tests/test_multi_master_metadata_no_leak.py:48` and `tests/test_template_import_path.py:236` both reference the fixture directory by path and must be updated together.
  ROADMAP constraint #1 forecloses one option: do not re-open "choose a different reserved directory name". Also avoid `_templates/` as the replacement directory name — it is Sphinx's own `templates_path` default.
- The exact glob list for D-04's "editor backups".
- Exact wording of D-09's three messages and D-05's `ExtensionError`.
- Where the `config-inited` handler lives (`__init__.py` alongside the config registration, versus a module of its own).
- How the write-time used-key accumulator is stored on the builder (ROADMAP constraint #4 names `self.images` as the pattern to mirror).
- Test file naming and placement, and the composition of the OUT-05 user-template asset fixture, subject to SC#3's requirement that it be a real `sphinx-build → typst.compile()` fixture recorded RED against the pre-relocation tree.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone contract (binding — these carry the locked decisions)

- `.planning/ROADMAP.md` § "🚧 v0.9.0 — per-document templates (ACTIVE)" — the eleven binding
  constraints. Constraints #1 (`_template/` reserved wholesale; the fixture moves; do not re-open
  the directory-name choice), #2 (green at every phase boundary), #3 (the removal ships with its
  detection in the same commit; first `config-inited` in this codebase), #4 (copy runs in
  `finish()` fed by a write-time accumulator; `resolve_template()` must yield the resolved path),
  #6 (standing GATE-01 RED-first bar), #7 (all three real templates measured to have zero
  path-relative references, so OUT-05 needs a NEW user-template fixture), #8 (`pyproject.toml:73`
  glob + built-wheel check), #9 (milestone branch stays pushed), #11 (standing invariants) all
  bind this phase.
- `.planning/ROADMAP.md` § "Phase 54: One Bundle Rule …" — the five success criteria. **SC#3's
  symlink sentence is amended by D-03 above**; the rest stands as written.
- `.planning/REQUIREMENTS.md` lines 18, 45, 50-68 — TPL-02, CONF-19, OUT-04…OUT-07, BLD-05,
  BLD-06 verbatim. **BLD-06's symlink clause is amended by D-03 above.**
- `.planning/PROJECT.md` § "Current Milestone: v0.9.0 per-document templates" — the "one output
  rule, no exceptions" statement, the four-deletions list with the reason each one collapses, and
  the "Decisions locked at scoping (2026-08-15)" block.

### Prior phase (do not re-litigate)

- `.planning/phases/53-template-registry-foundation/53-CONTEXT.md` — D-01…D-12. D-04 (only the
  literal `"typst"` is reserved) and D-07/D-08 (CONF-17's predicate; per-key existence-check
  divergence) directly shape what this phase's bundle copy will encounter. Its **Deferred Ideas**
  section hands this phase the `"Typst"`-vs-`"typst"` bundle-destination collision, with the route
  already chosen: through `_collision_key()` alongside the wrapper/content destinations, not a
  second case-folding.
- `.planning/phases/53-template-registry-foundation/53-VERIFICATION.md` and `53-SUMMARY` files —
  what the registry actually shipped, versus what was planned.
- `.planning/phases/53-template-registry-foundation/deferred-items.md` — the pre-existing
  `tests/test_state_guard_shapes_gate.py` failure (7 tests reading an archived
  `.planning/` path). It predates Phase 53 and is still open; it will surface in this phase's
  "full suite green" gate and must not be mistaken for a regression this phase caused.

### Research (file:line-grounded; do not re-derive)

- `.planning/research/ARCHITECTURE.md` §2 — NEW vs MODIFIED integration inventory. It also flags
  `writer.py:170-216` `_compute_template_import_path()` as **dead code** (zero non-docstring
  callers, superseded by `compute_template_import_path_for_dir()`) so it is not mistaken for the
  function OUT-06 generalizes.
- `.planning/research/ARCHITECTURE.md` §4 — the test files that assert the root `_template.typ`
  and the additive → behaviour-preserving → layout-change → deletion sequence. Phase 54 is
  steps 3–4.
- `.planning/research/PITFALLS.md` — Pitfall 5 (detection cannot be retrofitted after an
  unregistration) is the basis for CONF-19 shipping in the same commit.

### Source of truth in code

- `typsphinx/builder.py:1334-1376` — `copy_template_assets()` and its three early returns
  (unset `typst_template`, `typst_package` set, empty `typst_template_assets` list). All three
  are deleted; "has no bundle" becomes a per-key property.
- `typsphinx/builder.py:1378-1432` — `_copy_template_directory()`: the `os.walk` + `copy2` body
  D-02 keeps, the `.typ` exclusion D-02 removes, and the per-file
  `except Exception → logger.warning` D-05 keeps for non-template files.
- `typsphinx/builder.py:1434-1506` — `_copy_explicit_assets()` / `_copy_single_asset()`. Both
  deleted with `typst_template_assets`. Note `_copy_single_asset()`'s
  `shutil.copytree(dirs_exist_ok=True)` — the inherited default D-01 replaces with an explicit
  recorded policy.
- `typsphinx/builder.py:1508-1516` — `TypstBuilder.finish()`, where the accumulator-driven bundle
  copy runs (ROADMAP constraint #4).
- `typsphinx/builder.py:1224-1332` — `_write_template_file()`, deleted entirely. Its
  `path.join(self.outdir, "_template.typ")` at line 1290 is the write no output tree may contain
  after this phase.
- `typsphinx/builder.py:502-613` — `_validate_output_path_collisions()`, and specifically
  `_claim("_template.typ", …)` at line 586: the exact-name claim that becomes a `_template/`
  prefix reservation (OUT-07). `_collision_key()` at 423-500 is the case-folding the
  `"Typst"`/`"typst"` destination check routes through.
- `typsphinx/writer.py:60-106` and `170-221` — the two `_template.typ` import-path helpers.
  `170-216` is dead code; the live one is `compute_template_import_path_for_dir()`. Both encode
  the depth-counting OUT-06 replaces with a root-absolute path.
- `typsphinx/template_engine.py:37-56` — `TemplateResolution`, already carrying `path` (added in
  Phase 53). Its parent directory is the bundle. `get_default_template_path()` at 276-288 still
  uses `Path(__file__).parent`; SC#2 requires the `"typst"` bundle to resolve through
  `importlib.resources` instead.
- `typsphinx/__init__.py:58` — `app.add_config_value("typst_template_assets", …)`, the line
  removed in the same commit as CONF-19's handler.
- `typsphinx/pdf.py:143` — `typst.compile(typ_path, root=root_dir)`, the fixed Typst project root
  that makes OUT-06's root-absolute import resolve regardless of wrapper nesting depth.

### Tests and fixtures this phase touches

- The 33 files matching `grep -rln "_template.typ" tests/` — the migration set for the layout
  change (ROADMAP constraint #2 counts 31–32; measure at plan time rather than trusting either
  number).
- `tests/fixtures/template_named_dir_master/` (`conf.py`, `_template/index.rst`,
  `_template/sub/index.rst`) — read `conf.py`'s comment block in full before moving it; it
  documents all three regression intents enumerated under Claude's Discretion.
- `tests/test_multi_master_metadata_no_leak.py:48` and `tests/test_template_import_path.py:236` —
  the two path references into that fixture.
- `.github/workflows/ci.yml:127-151` — the `build` job D-13 extends.

### Project conventions

- `CLAUDE.md` § "Worktree-isolated execution" — mandatory per-worktree
  `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` plus running everything
  through `uv run`. Worktree isolation is the standing execution mode.
- `CLAUDE.md` § "The `@preview` version-sync hazard" — three sites in lockstep; this phase must
  not add a fourth.
- `CLAUDE.md` § "Conventions & gotchas" — typing-import modernization forbidden until the filed
  todo lands.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- **`_copy_template_directory()`'s `os.walk` + `copy2` loop** (builder.py:1378-1432) — D-02 keeps
  this body verbatim minus the `.typ` exclusion. It is already the measured-correct symlink
  behaviour; nothing new needs writing for that half.
- **`_collision_key()`** (builder.py:423-500) — `\`→`/`, `posixpath.normpath`, `casefold`.
  Already the single folding for destination comparison; the `"Typst"`/`"typst"` bundle-destination
  check and the `_template/` prefix reservation both route through it.
- **`_validate_output_path_collisions()`'s accumulate-then-raise-once shape** (builder.py:502-613)
  — the idiom OUT-07's reservation error follows, and where the existing `_claim("_template.typ")`
  lives.
- **`self.images` accumulator + `copy_image_files()` in `finish()`** — named by ROADMAP
  constraint #4 as the pattern the used-key accumulator mirrors.
- **`TemplateResolution.path`** (template_engine.py:37-56) — already present from Phase 53, unused
  by the write path so far. This phase is its first consumer; `path.parent` is the bundle.
- **`ci.yml`'s `build` job** (127-151) — already runs `uv build` and produces `dist/`; D-13 adds
  one step rather than a job.

### Established Patterns

- **No deletion under `outdir`.** Measured: the only `unlink`/`rmtree` in `typsphinx/` is
  `pdf.py:204` on its own temp file. D-01 preserves this.
- **Config-shape errors raise from inside a `Builder` method; warnings are bare `logger.warning`
  with no subtype.** D-08 preserves the second half. CONF-19's `config-inited` handler is the
  deliberate, roadmap-locked exception to the first half.
- **Asset-copy failures warn and continue** (builder.py:1425-1430, 1500-1506). D-05 keeps this for
  every bundle file except the resolved template itself.
- **Fixture `conf.py` files carry long comment blocks explaining what is load-bearing.** The
  relocated `template_named_dir_master` successor must carry the same for all three intents.
- **Zero new runtime dependencies.** `shutil`, `os`, `posixpath`, `importlib.resources` are all
  stdlib and the floor is 3.12.

### Integration Points

1. `typsphinx/__init__.py` — remove `typst_template_assets` registration (line 58); connect the
   `config-inited` handler in the same commit (ROADMAP constraint #3).
2. `typsphinx/builder.py write()` / `_write_typst_files()` — accumulate used registry keys as
   wrappers are emitted (only entries whose docname is in the write set produce one).
3. `typsphinx/builder.py finish()` — replace `copy_template_assets()` with the accumulator-driven
   bundle copy; `TypstPDFBuilder.finish()` inherits it before compiling.
4. `typsphinx/builder.py _validate_output_path_collisions()` — the `_template.typ` exact-name
   claim becomes a `_template/` prefix reservation (OUT-07), plus the bundle-destination
   case-collision check.
5. `typsphinx/writer.py render_wrapper()` — emit the root-absolute template import
   (`/_template/<key>/<file>.typ`) instead of a depth-counted relative path; the two depth-counting
   helpers go away, one of which is already dead code.
6. `typsphinx/template_engine.py get_default_template_path()` — resolve the bundled default
   through `importlib.resources` rather than `Path(__file__).parent` (SC#2).
7. `pyproject.toml:73` — widen package-data to `templates/**/*` (D-12).
8. `typsphinx/templates/README.md` — new file (D-11).
9. `.github/workflows/ci.yml` `build` job — wheel-content assertion step (D-13).
10. `.planning/REQUIREMENTS.md` (BLD-06) and `.planning/ROADMAP.md` (Phase 54 SC#3) — the D-03
    amendment.

</code_context>

<specifics>
## Specific Ideas

- The owner **rejected the framing of BLD-06's symlink guard outright**, in their own words: the
  intent was simply "the template directory gets copied wholesale, that's a good implementation" —
  there was no intent to construct the inverse rule that files outside the directory are
  forbidden. D-03 records the retraction. The general stance this establishes for planning: a
  guard is justified by the harm it prevents, and a guard nobody asked for is scope, not safety.
  This is consistent with, not contrary to, Phase 53's D-07 (let the goal shape the predicate) —
  there the goal *was* to stop the source tree becoming the bundle; here there is no equivalent
  goal behind the symlink clause.
- The owner's consistent stance across both phases: **do not exceed the roadmap text on rejection
  surface.** D-04 (exactly SC#3's four exclusion kinds) and D-07 (warning, not error) are the same
  call Phase 53's D-02 made.
- **The `-b typst` builder's output is no longer self-contained for a hand-run compile.** A
  root-absolute `#import "/_template/<key>/…"` resolves only when Typst's project root is the
  outdir. `pdf.py:143` already passes `root=outdir` for every compile this project performs, so
  `typstpdf` is unaffected — but a user who runs `typst compile build/typst/index.typ` by hand now
  needs `--root build/typst`. This is a Phase 56 documentation obligation, recorded here so it is
  not discovered late.

</specifics>

<deferred>
## Deferred Ideas

- **Later milestone — VCS/tooling metadata beyond SC#3's four kinds.** D-04 leaves `.svn`, `.hg`,
  `__pycache__`, `.idea`, `.vscode` copied into the output bundle. Cheap to add as further
  exclusion patterns whenever wanted; deliberately not in Phase 54.
- **Later milestone — `suppress_warnings` subtypes for this extension.** D-08 declines to tag
  CONF-19's warning because it would be the only tagged warning here. Tagging the extension's
  warnings as a set is a coherent piece of work; tagging one is not.
- **Later milestone — stale-bundle cleanup on incremental rebuilds.** D-01 accepts that a file
  removed from a source bundle can linger at the destination. Introducing deletion under `outdir`
  is a distinct decision with its own blast radius and belongs on its own.
- **Adjacent cleanup — `writer.py:170-216` `_compute_template_import_path()` is dead code**
  (carried forward from Phase 53's deferred list). Phase 54 removes the depth-counting import
  path, so this function should fall out naturally; if it does not, it is still not this
  milestone's responsibility to chase.

### Reviewed Todos (not folded)

`todo.match-phase 54` returned ten matches, all keyword false positives; none are Phase 54 scope.

- `_track_image()` escape-branch basename-only relocation key — `resolves_phase: 55`
- `_track_image()` `isabs` not drive-aware on py3.13 Windows — `resolves_phase: 55`
- Label-collision false negative in the compile-time xref guard — `resolves_phase: 55`
- `make_include_edge_key` unescaped `#`/`>` separators — `resolves_phase: 55`
- Unbounded recursion in `derive_master_edge_keys` — `resolves_phase: 55`
- typing-import modernization (`UP006`/`UP035`) — forbidden by `CLAUDE.md` until its own todo lands
- REL-04 `create-release` job missing `uv` — `resolves_phase: 46`
- `ruff` generic-linux ELF unrunnable on NixOS — toolchain, not phase work
- numref numbers diverge per master — translator, not phase work
- `sphinx-build -b linkcheck` CI job — unrelated

</deferred>

---

*Phase: 54-One Bundle Rule — `_template/<key>/`, Per-Document Selection, Four Deletions*
*Context gathered: 2026-08-15*
