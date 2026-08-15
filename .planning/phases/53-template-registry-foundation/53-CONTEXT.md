# Phase 53: Template Registry Foundation - Context

**Gathered:** 2026-08-15
**Status:** Ready for planning

<domain>
## Phase Boundary

Add the `typst_document_templates` registry as a **validated, resolved-once-per-build data
structure**, and switch `render_wrapper()` from reading `typst_template` / `typst_package` /
`typst_template_function` / `typst_template_mapping` straight off `config` to building its
`TemplateEngine` from a resolved registry definition — while the built-in `"typst"` key synthesizes
exactly those same global values, so **an untouched `conf.py` produces byte-identical output**.

In scope: config registration, the registry resolver, its validation pass (CONF-14…CONF-18),
widening `TemplateEngine`'s resolution so the resolved template PATH is recoverable, threading the
resolved definition into `render_wrapper()`, and pushing `gsd/v0.9.0-milestone` to `origin` with a
completed 3-OS CI run (SC#5).

Out of scope (Phase 54): element [4] actually selecting a different template per document, the
`<outdir>/_template/<key>/` bundle copy, `_write_template_file()`'s deletion, `typst_template_assets`'s
removal, and the `_template/` prefix reservation. Out of scope (Phase 55): the five v0.8.0-derived
defects.

</domain>

<decisions>
## Implementation Decisions

### Registry key shape validation

- **D-01:** Registry-key shape is validated by **denylist enumeration only** — each of ROADMAP SC#4's cases is judged individually and emits its own case-specific error message. No allowlist regex is used, not even as a trailing catch-all. This deliberately rejects STACK.md's `re.fullmatch(r"[A-Za-z0-9_-]+", key)` suggestion in favour of PITFALLS.md's per-case predicate, because SC#3 requires "a message naming the specific reason".
- **D-02:** The denylist is **exactly SC#4's seven cases** and nothing more: empty or whitespace-only, `.`/`..`, containing `/` or `\`, a Windows reserved device name (case-folded, with or without a trailing extension), a trailing dot, a trailing space, and differing from another registered key only by case. Windows-illegal characters (`< > : " | ? *`), control characters (0x00–0x1F), a leading dot, and interior whitespace all stay **accepted** in Phase 53. Do not exceed the roadmap text. — **Reversibility:** costly — tightening this after v0.9.0 ships turns a previously-building `conf.py` into a hard `ExtensionError`, so a later narrowing needs a CHANGELOG breaking-change entry.
- **D-03:** Registry validation reports errors in the **same shape as `_validate_output_path_collisions()`** (builder.py:606-612: accumulate every failure, raise once at the end) but through an **independent** `ExtensionError` of its own. Do not merge registry failures into the collision validator's `failures` list and do not change its `"typst: N output path collision(s): …"` message text.
- **D-04:** Only the **literal** string `"typst"` is reserved (CONF-16). `"Typst"`/`"TYPST"` pass as ordinary user-defined keys, because CONF-18's case-collision check compares **registered** keys against each other and the synthesized built-in is not a member of that set. See Deferred Ideas — the resulting bundle-directory collision is handed to Phase 54.

### Registry validation scope and error surface

- **D-05:** Validation covers **every declared key**, not only keys referenced by element [4]. The FS existence check costs a few `os.path.isfile` calls, which is not worth an exception; PROJECT.md's own v0.9.0 text states "One code path is worth more than the exception". ROADMAP SC#3's order-independence then holds trivially.
- **D-06:** An element [4] that is **present but not a `str`** (`None`, `123`, a tuple, …) raises the **same CONF-14-class `ExtensionError`** as an unregistered key, naming the offending value and the registered keys. It does **not** join `_is_usable_typst_documents_entry()`'s tolerate-and-skip contract (builder.py:115-166) and is **not** silently coerced to `"typst"`. `_is_usable_typst_documents_entry()`'s own docstring instructs that a genuinely different usability question gets a new named predicate rather than an extension of that one. An **absent** element [4] (a four-element tuple) still means `"typst"` per TPL-04.

### Template path resolution

- **D-07:** CONF-17's predicate is framed by the harm it exists to prevent — "copy the parent directory" must never mean "copy the source tree". It rejects when the resolved parent directory **is `srcdir` itself, or is an ancestor of `srcdir`**. srcdir's **siblings** (`../shared/tpl.typ`) and absolute paths outside srcdir stay legal: copying a bounded `shared/` directory is not the harm CONF-17 targets. Measured: `os.path.join(srcdir, "/abs/x.typ")` yields `/abs/x.typ`, so absolute template paths work today and are not being withdrawn. — **Reversibility:** costly — Phase 56 documents this contract; narrowing it later to "must be a strict descendant of srcdir" breaks any config that pointed at a sibling or absolute path.
- **D-08:** A registry `template` pointing at a **file that does not exist** raises `ExtensionError` **for user-defined keys only**. The built-in `"typst"` key keeps today's behaviour unchanged: `resolve_template()` Priority 1 logs `"Custom template not found: … Falling back to default template."` and falls through to Priority 2 (`<srcdir>/base.typ` shadow) then Priority 3 (bundled `base.typ`) — template_engine.py:308-313. Rationale: raising for all keys would flip an existing `conf.py` with a typo'd `typst_template` from warning-and-building to failing, breaking this phase's "changes no output" invariant; keeping warn+fallback for all keys would, in Phase 54, copy `typsphinx/templates/` into `_template/<user-key>/` and let the user believe their own template was used. — **Reversibility:** costly — the per-key divergence is a documented contract from Phase 56 onward.
- **D-09:** CONF-17's predicate is **path arithmetic on the declared value**, independent of whether the file exists, so CONF-17 and D-08's existence check are two separate failures that can both be reported in the same accumulated raise.

### Global-value inheritance for user-defined keys

- **D-10:** A user-defined key that **omits** `template_function` does **not** inherit global `typst_template_function`. Omission means `None`, which `render()` already resolves to the literal `"project"` for both the `#import` line and the `#show:` call (template_engine.py:654, 664). Registry definitions are self-contained; TPL-03's "the built-in key `\"typst\"` resolves to the existing global configuration" is the only inheritance route.
- **D-11:** Global `typst_template_mapping` is passed to the **`"typst"` key's engine only**, not to every key. Measured support: REQUIREMENTS.md's TPL-03 names `typst_template_mapping` as one of the four global values the `"typst"` key resolves to, whereas `typst_package_imports` is absent from that list and PROJECT.md separately locks it as "global, applies to every document" — the requirement text already distinguishes the two, so this is not an inconsistency. A user-defined key therefore gets `DEFAULT_PARAMETER_MAPPING` (`project→title`, `author→authors`, `release→date`), or `{}` when the definition carries a `package` (template_engine.py:230-238, D-05's package rule). Keeping the value scoped to one key also stops Future requirement TPL-06 (retiring `typst_template_mapping`) from gaining new surface. — **Reversibility:** costly — this is the registry's published parameter-naming contract; widening or narrowing it after release changes what every user-defined key emits.

### Evidence for SC#2 (byte-identical output)

- **D-12:** SC#2 is proven by a **one-off evidence artifact only** — `53-RED-EVIDENCE.md` recording the before/after commit SHAs, per-file SHA-256 of the emitted `.typ` files, and PDF page counts across the four existing shapes (`typst_template` set / `typst_package` set / `typst_template_function` set / nothing set). **No new golden-file pytest gate is added.** The standing regression net already exists: the 31 test files asserting the root `_template.typ` must pass **unchanged**, which is exactly what "behaviour-preserving" means for this phase. A golden generated from post-change code cannot prove pre-change identity, and Phase 54 deliberately invalidates that layout one phase later. Note the file name — `53-VERIFICATION.md` is reserved by `gsd-verifier` and must not be used for evidence.

### Claude's Discretion

- Where the registry resolver lives. `.planning/research/ARCHITECTURE.md` §2 recommends a new `typsphinx/template_registry.py`, keeping `template_engine.py` as pure content/parameter logic and `builder.py` as filesystem orchestration.
- The exact widening of `TemplateEngine.resolve_template()` so the resolved `Path` is recoverable — a new field on `TemplateResolution` (template_engine.py:37-56) versus a separate `resolve_template_path()` method. Constraint from the class's own docstring (CONF-07/D-06): it must stay the **single** priority walk, never a second independently-written lookup.
- How the once-per-build resolution result reaches `render_wrapper()` — a builder attribute threaded like `self._master_include_edges` (builder.py:730 → writer.py:268/318) versus a new parameter.
- Exact error message wording, subject to SC#3's "names the specific reason" and CONF-14's "the error names the registered keys".
- Test file naming and placement.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone contract (binding — these carry the locked decisions)

- `.planning/ROADMAP.md` § "🚧 v0.9.0 — per-document templates (ACTIVE)" — the eleven binding
  constraints and Phase 53's five success criteria. Constraints #2 (green at every phase boundary,
  31 test files), #5 (registry keys are single path segments; the existing guards are the wrong
  contract), #6 (standing GATE-01 RED-first bar), #9 (push the milestone branch from the first
  phase), #11 (standing invariants) all bind this phase.
- `.planning/ROADMAP.md` § "Phase 53: Template Registry Foundation" — the goal statement locking
  resolution to `write()` immediately after `_validate_output_path_collisions()` and before
  `prepare_writing()`, and locking `typst_template_mapping` as global-and-untouched.
- `.planning/REQUIREMENTS.md` lines 15-40 — TPL-01, TPL-03, TPL-04, TPL-05, CONF-14…CONF-18 verbatim.
  TPL-03's parenthetical is the measured basis for D-11.
- `.planning/PROJECT.md` § "Current Milestone: v0.9.0 per-document templates" — the
  "Decisions locked at scoping (2026-08-15)" block: registry is function-only, P×A stays broken,
  `params` exclusivity preserved, `package_imports`/`elements` stay global, `"typst"` gets no
  exception in the output layout.

### Research (file:line-grounded; do not re-derive)

- `.planning/research/ARCHITECTURE.md` §2 — NEW vs MODIFIED integration inventory with file:line for
  every touch point.
- `.planning/research/ARCHITECTURE.md` §3 — why resolution belongs once per build in `write()`.
- `.planning/research/ARCHITECTURE.md` §4 — the 31 test files that assert the root `_template.typ`,
  and the additive → behaviour-preserving → layout-change → deletion sequence. Phase 53 is steps 1–2.
- `.planning/research/PITFALLS.md` § "Pitfall 1" — why `_escapes_outdir()`/`_is_drive_qualified()`
  must not be reused for registry keys, and the per-case denylist D-01 adopts.
- `.planning/research/STACK.md` lines 36, 63-65 — the allowlist suggestion **rejected** by D-01, and
  the confirmation that `config-inited` has no precedent in this codebase
  (`grep -n "config-inited" typsphinx/*.py` returns nothing).
- `.planning/research/SUMMARY.md` § "Open Decisions Carried Forward" — both entries are already
  closed by ROADMAP binding constraints #1 and #3; do not re-open them.

### Source of truth in code

- `typsphinx/builder.py:36-112` — `_is_drive_qualified()` / `_escapes_outdir()`. Read the docstrings:
  `_escapes_outdir("manuals/guide")` is `False` by design. This is the contract D-01's new predicate
  must **not** reuse, and the phase's artifacts must record why.
- `typsphinx/builder.py:115-166` — `_is_usable_typst_documents_entry()`, the four-site single source
  of truth for "can this entry produce a wrapper", and its instruction that a different usability
  question gets a new predicate (basis for D-06).
- `typsphinx/builder.py:423-500` — `_collision_key()`: `\`→`/`, `posixpath.normpath`, `casefold`.
  ROADMAP SC#4 requires CONF-18's case-collision check to run through this same comparison.
- `typsphinx/builder.py:502-613` — `_validate_output_path_collisions()`: the accumulate-then-raise-once
  shape D-03 mirrors, and the "runs ONCE at the very top of `write()`" precedent.
- `typsphinx/builder.py:695-730` — `write()`: the exact insertion point (after line 713's collision
  validation, before line 716's `prepare_writing()`), and `self._master_include_edges` at line 730 as
  the "derive once, thread into the per-docname loop" pattern to copy.
- `typsphinx/builder.py:1109-1179` — `_write_template_file()`: the global-config reading and the
  both-`typst_package`-and-`typst_template` warning whose logic moves into the `"typst"` key's
  synthesis. **Not deleted in this phase.**
- `typsphinx/writer.py:322-355` — `render_wrapper()`'s current global-config read and `TemplateEngine`
  construction. This is the call site that switches to the resolved definition.
- `typsphinx/template_engine.py:37-56, 266-336` — `TemplateResolution` and `resolve_template()`'s
  three-priority walk, including the Priority 1 warn-and-fall-back behaviour D-08 preserves for
  `"typst"` and overrides for user-defined keys.
- `typsphinx/template_engine.py:196-265` — `TemplateEngine.__init__`: `DEFAULT_PARAMETER_MAPPING`, the
  `parameter_mapping is None` → `{}`-when-package rule (basis for D-11), and the D-D `params`-presence
  predicate that TPL-01/TPL-05 must leave intact.
- `typsphinx/template_engine.py:640-700` — `render()`'s `self.typst_template_function_name or "project"`
  fallback at both the `#import` and `#show:` sites (basis for D-10).
- `typsphinx/__init__.py:44-58` — the config registration block where `typst_document_templates` is
  added. **`typst_template_assets` at line 58 is NOT removed in this phase** (Phase 54, with CONF-19).

### Project conventions

- `CLAUDE.md` § "The `@preview` version-sync hazard" — the three-site lockstep; this phase must not
  add a fourth site.
- `CLAUDE.md` § "Worktree-isolated execution" — mandatory per-worktree
  `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` plus running everything through
  `uv run`. Worktree isolation is the standing execution mode.
- `CLAUDE.md` § "Conventions & gotchas" — typing-import modernization is forbidden until the filed
  todo lands; `E501` is ruff-ignored because black owns wrapping.
- `.github/workflows/ci.yml:17` — `os: [ubuntu-latest, windows-latest, macos-latest]`. SC#5's
  completed-run evidence must include the `windows-latest` and `macos-latest` lanes.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- **`_validate_output_path_collisions()`'s accumulate-then-raise-once body** (builder.py:502-613) —
  the shape D-03 copies. Its `failures` list plus the `"; ".join(...)` summary is the exact idiom.
- **`_collision_key()`** (builder.py:423-500) — already platform-independent, already casefold-based,
  already documented as comparison-only. CONF-18's case-collision check routes through it rather than
  writing a second folding.
- **`self._master_include_edges = self._build_include_edge_map()`** (builder.py:730) — the "derive
  once in `write()`, thread into the per-docname loop" pattern the registry resolution mirrors.
- **`resolve_package_for_engine()`** (template_engine.py, called from writer.py:341 and
  builder.py:1166) — the single place the package-vs-template routing rule (D-01/D-03/WR-04) lives.
  The `"typst"` key's synthesis must route through it, not re-derive it.
- **`derive_typst_lang()`'s `re.fullmatch()` validate-and-raise idiom** (template_engine.py:133) —
  the in-repo precedent for config-shape validation. D-01 declines its allowlist form but the
  fail-loud structure still applies.
- **`_is_drive_qualified()`'s docstring** (builder.py:36-67) — the written precedent (D-05) for
  validating Windows-shaped input identically on POSIX, which SC#4's platform-independent
  string-shape tests follow.

### Established Patterns

- **Fail loud from inside a `Builder` method, never `config-inited`.** Measured:
  `grep -n "config-inited" typsphinx/*.py` returns nothing. Every config-shape error in this
  extension (`typst_elements` unknown key, output-path collisions at builder.py:611) is raised from a
  `Builder` method. Phase 53 keeps that; the codebase's first `config-inited` handler is CONF-19's,
  in Phase 54.
- **Unusable `typst_documents` entries are tolerated and skipped with a warning, never raised**
  (builder.py:140-146). D-06 deliberately does not extend this contract — a bad registry key is a
  different question and gets its own error.
- **`render()`'s exclusive-parameter rule (D-B/D-D)** — `params`-presence, not truthiness, selects the
  exclusive set. TPL-01/TPL-05 must reach this through the existing attribute, introducing no new
  predicate.
- **Zero new runtime dependencies.** `re`, `posixpath`, `os.path` are already imported in
  `builder.py`; nothing new is needed for this phase's scope.

### Integration Points

1. `typsphinx/__init__.py` — register `typst_document_templates` (default `{}`, rebuild `"html"`,
   types `[dict]`). Nothing is removed here in Phase 53.
2. New registry resolver module — validates all declared keys (D-05), synthesizes the built-in
   `"typst"` key from `typst_template` / `typst_package` / `typst_template_function` /
   `typst_template_mapping`, returns `dict[str, definition]`.
3. `builder.py write()` — call the resolver after line 713, before line 716; store on the builder.
4. `builder.py _write_typst_files()` wrapper loop (1074-1092) — resolve `entry[4]` (absent → `"typst"`)
   against the stored registry and pass the definition into `render_wrapper()`.
5. `writer.py render_wrapper()` (322-355) — construct `TemplateEngine` from the passed definition
   instead of reading `config`. `typst_package_imports` and `typst_elements` continue to come from
   global config; `typst_template_mapping` comes from the definition, which only the `"typst"` key
   carries (D-11).
6. `template_engine.py` — widen the resolution so the resolved `Path` is recoverable, through the
   existing single priority walk. Unused by the write path in this phase; Phase 54's bundle copy is
   its first consumer.
7. Git/CI — push `gsd/v0.9.0-milestone` to `origin` and land a completed 3-OS CI run (SC#5). This is
   phase work, not a code change, and CONF-18's reserved-device-name and case-collision cases are
   structurally invisible to a local Linux-only run.

</code_context>

<specifics>
## Specific Ideas

- The owner **reframed CONF-17 away from its literal roadmap wording** ("a `template` pointing at a
  file directly under `srcdir`") to the harm it exists to prevent: stopping the source tree from
  becoming the copied bundle. D-07 is the result. Plans should describe CONF-17 by that predicate,
  not by the literal wording — and the "declared string contains no separator" formulation is
  explicitly rejected, because `../base.typ` slips through it and would copy the entire project.
- The owner's consistent stance across this discussion: **do not exceed the roadmap text on rejection
  surface** (D-02, D-04), but **do let the goal, not the wording, shape the predicate** (D-07). Both
  at once. Keep new fail-loud behaviour on the new config surface only, never on existing config
  (D-08).

</specifics>

<deferred>
## Deferred Ideas

- **Phase 54 — `"Typst"` vs `"typst"` bundle collision.** D-04 accepts `"Typst"` as an ordinary
  user-defined key and CONF-18's case-collision check compares only registered keys, so a config
  declaring `"Typst"` passes Phase 53 and then, in Phase 54, resolves to the same
  `<outdir>/_template/<key>/` directory as the built-in `"typst"` on the case-insensitive filesystems
  that are macOS's and Windows's defaults. The bundle-destination collision check belongs with the
  layout change that creates those destinations. Route it through `_collision_key()` alongside the
  wrapper/content destinations rather than a second folding.
- **Later phase — Windows-illegal and control characters in registry keys.** D-02 leaves
  `< > : " | ? *` and 0x00–0x1F accepted. A key like `paper:v2` creates a directory fine on Linux and
  fails only on the `windows-latest` CI lane. Cheap to add as a string-shape case whenever it is
  wanted; deliberately not in Phase 53.
- **Adjacent cleanup (not this milestone's responsibility).** `writer.py:170-216`
  `_compute_template_import_path()` is dead code — grep confirms zero non-docstring callers, superseded
  by `compute_template_import_path_for_dir()`. Flagged by `.planning/research/ARCHITECTURE.md` §2 so it
  is not mistaken for the function Phase 54 needs to generalize.

### Reviewed Todos (not folded)

`todo.match-phase 53` returned seven matches, all keyword false positives; none are Phase 53 scope.

- Label-collision false negative in the compile-time xref guard — `resolves_phase: 55`
- `make_include_edge_key` unescaped `#`/`>` separators — `resolves_phase: 55`
- Unbounded recursion in `derive_master_edge_keys` — `resolves_phase: 55`
- `_track_image()`'s escape branch keys relocation on basename alone — `resolves_phase: 55`
- `_track_image()` `isabs` not drive-aware on py3.13 Windows — `resolves_phase: 55`
- REL-04 `create-release` job missing `uv` — `resolves_phase: 46`
- `ruff` generic-linux ELF unrunnable on NixOS — `resolves_phase: null`, toolchain, not phase work
- numref numbers diverge per master — `resolves_phase: null`, translator, not phase work

</deferred>

---

*Phase: 53-Template Registry Foundation*
*Context gathered: 2026-08-15*
