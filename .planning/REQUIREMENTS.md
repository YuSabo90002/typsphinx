# Requirements: typsphinx v0.9.1 — Windows path correctness

**Defined:** 2026-08-27
**Core Value:** The `typst`/`typstpdf` builders produce correct, compilable, faithfully-rendered
output — and the documented configuration actually takes effect. A path the extension writes,
emits, or quotes back to the user must be correct on every supported platform, not only on the
one the maintainer develops on.

**Milestone framing.** This is a bug-fix round: no new user-facing capability, no new runtime
dependency, no new `typst_*` config value. Its scope is the Windows path defects Phase 57's
prep-only fence held back, closed together with their whole sibling family.

**Everything below was re-measured at HEAD before being written.** Where a research finding
contradicted the milestone's own initial framing, the finding won and the framing was corrected —
see PATH-01's reachability note and MSG-01's existence.

## v1 Requirements

### PATH — path-shape predicate correctness

- [ ] **PATH-01**: `_escapes_outdir()` (`typsphinx/builder.py:238`) applies its absolute-path and
      drive-qualified checks to the backslash-normalized string, not the raw stem, matching the
      idiom its sibling `_is_absolute_image_uri()` (`builder.py:194`) already uses.

      **Reachability, measured 2026-08-27:** this gap is **not reachable from either real call
      site**. `_resolve_target_stem()` normalizes at `builder.py:662` before calling, and
      `_track_image()` passes a `relpath()` result that always carries a `..` segment, so the
      predicate returns `True` there regardless. Called *directly*, exactly two shapes flip
      classification: driveless-absolute (`\manuals\guide`) and UNC (`\\srv\share\g`), both
      `False → True`. This requirement is therefore **hardening of the function's own contract**,
      not the repair of a live user-facing defect, and it is scoped in deliberately: a future
      third call site that does not pre-normalize would inherit the gap silently.

      **Gate:** the RED-first test must call `_escapes_outdir()` **directly**. An integration test
      routed through either call site is tautologically green before and after the fix and proves
      nothing.

### IMG — image URI safety

- [ ] **IMG-04**: `_track_image()`'s escape branch (`typsphinx/builder.py:1772`) builds its
      relocation key from a forward-slash-normalized basename, so no backslash from the original
      URI survives into the emitted `image()` path value. Today it calls `path.basename()` on the
      RAW URI; on a POSIX build host `path` is `posixpath`, which does not split on `\`, so the
      whole URI comes back and its separators land inside the key.

- [ ] **IMG-05**: `visit_image()` (`typsphinx/translator.py:4746,4749`) routes `adjusted_uri`
      through the existing `escape_typst_string()` (`translator.py:156`) before interpolating it
      into the `image("...")` literal. The escaper wraps the **return value** of
      `_compute_relative_image_path()`, never the raw `uri` before that call — it is a
      syntax-literal transform and must run last.

- [x] **IMG-06**: the relocation key's basename is bounded to 255 UTF-8 bytes, with the
      `{sha1[:8]}-` digest kept whole as the collision anchor (truncating the digest would
      reintroduce the collision IMG-03 closed). Truncation lands on a UTF-8 character boundary and
      never yields an empty basename.

      **Constant, not a probe (owner decision 2026-08-27):** `os.pathconf()` / `os.statvfs()` are
      documented `Availability: Unix` and are unusable on the `windows-latest` lane, so the bound
      is a hardcoded `255` — matching ext4/APFS byte limits and safely under NTFS's 255-UTF-16-unit
      limit. No CI probe is dispatched to measure it.

      **Gate:** this defect has **no compile-visible symptom** — it surfaces as an `ENAMETOOLONG`
      `OSError` at `copy_image_files()` time — so a compile gate will not force it out. It needs
      its own.

- [ ] **IMG-07**: at least one gate in this milestone is a real `typst.compile()` proving a
      Windows-shaped absolute image URI now compiles. **Measured 2026-08-27: Typst refuses a
      backslash in an `image()` path BY VALUE, not by syntax** — escaping the backslash in the
      source (so it decodes to one `\`) still produces `TypstError: path must not contain a
      backslash`. IMG-04 and IMG-05 are therefore **coupled**: neither alone closes the
      compile-time failure. This is also why the defect survived Phase 55's suite, whose tests stop
      at `node["uri"]` and never render.

### MSG — user-facing path quoting

- [x] **MSG-01**: the two existing tests that hard-code `repr()`'s backslash-doubling output as
      their pass criterion are rewritten to assert the *meaning* (the path is named in the message)
      rather than `repr()`'s output format — **before** any message site is rewired. The two are
      `tests/test_out02_escape_target_gate.py:134` (`assert repr(target) in combined_output`, for
      `target = "C:\\escape.typ"`, running unconditionally on every platform) and
      `tests/test_builder.py:598` (`assert repr(abs_uri) in message`, green on POSIX by coincidence
      and breaking only on `windows-latest`). Both must stay green before and after this rewrite.

      **Why this is its own requirement (owner decision 2026-08-27):** it preserves the "zero test
      edits proves POSIX-identical output" discipline 57-11 established. With the `repr()`
      dependency removed first, the requirements that actually change product code can then be
      landed with genuinely zero test edits. The census confirmed the other 18 `repr(...)`
      assertions in the suite are on identifier / list / bytes / int values and correctly stay
      untouched.

- [ ] **MSG-02**: a delimiter-aware path-quoting helper exists in a **new leaf module** with zero
      `typsphinx`-internal imports. It does **not** escape backslashes, and it selects a delimiter
      that cannot appear unescaped inside the value — restoring the half of `repr()` that 57-11's
      hardcoded `'{value}'` dropped, while keeping the half it correctly removed. It accepts
      `str` **and** `os.PathLike`, because `template` values are deliberately allowed to be
      `pathlib.Path` (the module's own design comment and a "Test H" control test say so).

      **Placement is forced, not stylistic:** `builder.py` imports `writer.py` at module scope, and
      `template_registry.py` avoids a cycle with `builder.py` only via a lazy function-scoped
      import. Putting the helper in any of those three files creates an unconditional two-file
      import cycle the moment the other two import it back.

      **Gate:** both halves — the existing no-doubled-separator property
      (`TestWindowsPathEscapingRegressionGuard` in `tests/test_templates_path_collision_gate.py`)
      **and** the sibling case `57-REVIEW.md` IN-01 named as missing: a path containing a literal
      single quote, asserted to be delimited unambiguously.

- [ ] **MSG-03**: every path-valued interpolation in `typsphinx/builder.py` routes through the
      helper — the three sites 57-11 already fixed (`_conf17_violation_message`,
      `_templates_path_collision_message`, `_bundle_destination_collision_message`, ~lines 329-402)
      plus the census groups confirmed live at HEAD: lines 942, 964, 965, 999, 1007, 1008, 1015
      (the v0.8.0-era output-path collision family), 2056, 2066 (bundle-copy I/O), 697 (docname
      target warnings), and 1767 (image-rehome warning). Identifier-valued `!r` — registry keys,
      docnames, config tuples — stays `!r` and is not touched.

- [ ] **MSG-04**: `typsphinx/writer.py`'s wrapper-render debug log (lines 511-513 —
      `wrapper_relative_dir`, `include_path`, `template_file`) routes through the helper.

- [ ] **MSG-05**: `typsphinx/template_registry.py`'s CONF-17 violation (line 422) and existence
      check (line 433) route through the helper. **Line 410 is deliberately excluded**: its
      type-check message interpolates `template` *before* the value is known to be path-shaped —
      it is reached precisely when the value is a `list`, `bytes`, or another non-path type — so
      routing it through a path-quoting helper would be wrong.

### REL — release

- [ ] **REL-09**: v0.9.1 released to PyPI with a curated `## [0.9.1]` CHANGELOG entry, the version
      bumped as the sole literal in `pyproject.toml` with `uv.lock` and `README.md` in lockstep,
      and the GitHub Release body sourced from `scripts/extract_changelog_section.py`.

## v2 Requirements

Deferred to a future milestone. Tracked, not in this roadmap.

### Configuration and rendering

- **CONF-xx**: the `templates_path` collision check resolves against `confdir` rather than
  `srcdir`, so `-c`/confdir projects are covered (54.1-REVIEW WR-02, shipped silent in v0.9.0).

- **DOC-xx**: `numref` numbers diverge per master and vanish entirely for figures reachable only
  from a non-root master (still excluded from every published surface by owner override D-07).

- **CONF-xx**: the "Custom template not found" warning fires three times instead of two for one
  narrow shape (54.1-REVIEW WR-01).

### Toolchain and CI

- **CI-xx**: every dependabot PR dies before running a single test — it bumps `pyproject.toml`
  without regenerating `uv.lock`, and all ten `uv sync --locked` steps refuse the stale lockfile
  (`severity: major`).

- **QUA-06**: `ruff` cannot run on the maintainer's NixOS machine — a freshly-provisioned worktree
  venv pulls a generic-linux wheel whose ELF the loader rejects. Re-measured live 2026-08-22; the
  main tree's stale binary masks it. CI holds lint authority, so nothing is blocked.

- **QUA-07**: split the `dev` extra into PEP 735 `[dependency-groups]` so each tox environment
  installs only what it needs (SEED-003).

- **LNK-01**: add a `sphinx-build -b linkcheck` CI job (`links.yml`'s repo-wide lychee check
  already covers the links each release adds).

- **QUA-xx**: modernize typing imports and drop the `UP006`/`UP035` ruff ignore. Deferred
  *doubly* — `CLAUDE.md` independently instructs not to modernize until that todo lands.

### Structural

- **SEED-004**: `typst-py` upstream maintenance is slowing; typsphinx may need to carry an
  equivalent compile path itself. The largest structural risk on the horizon and never yet scoped
  into any milestone.

### Documentation

- **DOC-xx**: the root `index.rst` toctree lists section indexes AND their children, so the HTML
  sidebar shows Configuration / Builders / Templates twice.

## Out of Scope

Explicitly excluded from v0.9.1, with reasoning.

| Feature | Reason |
|---------|--------|
| General Windows reserved-character sanitization (`<>:"\|?*`, reserved device names) | No demonstrated failure mode in this milestone's evidence. Only backslash and length have measured symptoms; widening to a general sanitizer is speculative scope. |
| A `### Known Limitations` section in the CHANGELOG | Not selected by the owner for this milestone. It has now been declined for a fourth consecutive release; that pattern is worth an explicit decision at a future close rather than a silent default here. |
| A live CI probe to measure the real filesystem `NAME_MAX` on each platform | `os.pathconf()`/`os.statvfs()` are Unix-only, so the probe would have to be a bespoke write-and-measure job. The conservative 255-byte constant is accepted instead (IMG-06). |
| An independent CI requirement for the 3-OS matrix run | Not selected as a requirement. The green matrix remains the milestone's acceptance bar and belongs in the phases' success criteria, not as a REQ-ID of its own. |
| `template_registry.py:410`'s type-check message | Its interpolated value is reached only when it is NOT path-shaped. Routing it through a path-quoting helper would be actively wrong (MSG-05). |
| Any new runtime dependency | Every fix is stdlib-only by construction. Verified against the research: no candidate solution required one. |
| Any new `typst_*` config value | This is a bug-fix round; the configuration surface is unchanged. |

## Traceability

Which phases cover which requirements. Populated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| MSG-01 | Phase 58 | Complete |
| PATH-01 | Phase 59 | Pending |
| IMG-04 | Phase 59 | Pending |
| IMG-05 | Phase 59 | Pending |
| IMG-06 | Phase 59 | Complete |
| IMG-07 | Phase 59 | Pending |
| MSG-02 | Phase 60 | Pending |
| MSG-03 | Phase 60 | Pending |
| MSG-04 | Phase 60 | Pending |
| MSG-05 | Phase 60 | Pending |
| REL-09 | Phase 61 | Pending |

Ordered by phase, not by REQ-ID, because the ordering is itself load-bearing: MSG-01 precedes every
requirement that changes a message string, and IMG-04's value change precedes MSG-03's re-quoting of
the same warning. See ROADMAP.md binding constraints 2 and 4.

**Coverage:**

- v1 requirements: 11 total
- Mapped to phases: 11
- Unmapped: 0 ✓
- Duplicates (a requirement in more than one phase): 0 ✓

**Phase totals:** Phase 58 → 1 (MSG-01) · Phase 59 → 5 (PATH-01, IMG-04, IMG-05, IMG-06, IMG-07) ·
Phase 60 → 4 (MSG-02, MSG-03, MSG-04, MSG-05) · Phase 61 → 1 (REL-09).

**IMG-07 is mapped, not floated.** It reads as a cross-cutting obligation ("at least one gate in this
milestone is a real `typst.compile()`"), but the gate can only be green once IMG-04 and IMG-05 have
both landed — Typst refuses a backslash in an `image()` path by value, not by syntax. Exactly one
phase satisfies that, so IMG-07 is owned by Phase 59, which writes the gate.

## Standing constraints for every phase in this milestone

These are not requirements; they are the conditions any plan in this milestone must satisfy.

1. **RED-first is mandatory, and the bar is not "CI green".** All three defect families are latent:
   no test covers any of them today, and the `windows-latest` lane is green at HEAD and would stay
   green if nothing were fixed. Each gate must FAIL against the unfixed tree before its fix lands.

2. **At least one gate is a real `typst.compile()`** (IMG-GATE). An assertion that stops at
   `node["uri"]` cannot see the property that failed here.

3. **Zero test edits in the product-code requirements.** MSG-01 exists to make this achievable; if
   a later plan finds it must edit a test, that is a signal the census was incomplete, not a
   licence to edit.

4. **Build order respects two measured collision hazards.** PATH-01, IMG-04 and IMG-06 all land in
   the same ~30-line region of `builder.py` — `_escapes_outdir()` is called from inside
   `_track_image()`, and MSG-03's line-1767 site is the exact warning whose `key` value IMG-04
   changes. They must not run as parallel worktree plans against the same file. Separately, a plan
   that changes an emitted message string and a plan that asserts on that string must not share a
   wave — this project has already paid for that once.

5. **Worktree isolation is the standing execution mode.** Every executor provisions its own venv
   (`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev`) and runs everything via
   `uv run`, per `CLAUDE.md`.

6. **Acceptance bar:** the 3-OS CI lane, `windows-latest` included, green over the fix — dispatched
   on the post-fix tip, not inferred from a prior run.

---
*Requirements defined: 2026-08-27*
*Last updated: 2026-08-27 after roadmap creation (Phases 58–61 mapped, 11/11 covered)*
