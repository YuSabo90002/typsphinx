# Phase 59: Path-Shape Predicate and Image-URI Correctness - Context

**Gathered:** 2026-08-28
**Status:** Ready for planning

<domain>
## Phase Boundary

A Windows-shaped absolute image URI survives the whole pipeline. Three `builder.py` changes in one
~30-line region plus one `translator.py` change, gated by a real `typst.compile()`:

- **PATH-01** — `_escapes_outdir()` (`typsphinx/builder.py:197-238`) applies its absolute-path and
  drive-qualified checks to the backslash-normalized string, matching the idiom
  `_is_absolute_image_uri()` (`builder.py:194`) already uses. Hardening of the function's own
  contract; **not reachable from either production call site**, so its gate calls it directly.
- **IMG-04** — `_track_image()`'s escape branch (`builder.py:1761-1765`) builds its relocation key
  from a forward-slash-normalized basename, so no backslash from the original URI survives.
- **IMG-06** — that key's final path component is bounded to 255 UTF-8 bytes with the `{sha1[:8]}-`
  collision anchor intact.
- **IMG-05** — `visit_image()` (`translator.py:4742-4749`) routes the *return value* of
  `_compute_relative_image_path()` through `escape_typst_string()` (`translator.py:156`) before
  interpolating it into the `image("...")` literal.
- **IMG-07** — one gate is a real `typst.compile()` proving the above.

**In scope:**

- The four product changes above, plus their RED-first gates.
- One new fixture project for the compile gate, modelled on
  `tests/fixtures/absolute_image_render_gate/`.
- New test files only. `builder.py`, `translator.py` and new test modules are the phase's whole
  write surface.

**Out of scope:**

- **Any edit to an existing test assertion under `tests/`** (ROADMAP constraint 9; measured against
  `58-REPR-CENSUS.md`, not claimed). Adding new test *files* is not a test edit.
- **Any message-string rewiring.** `builder.py:697` and `builder.py:1766-1769` keep `!r` in this
  phase; MSG-03 moves them in Phase 60. IMG-04 changes the *value* `builder.py:1767` interpolates,
  which is exactly why the quoting is a separate phase (ROADMAP constraint 4).
- **The non-escape key branches.** `key = rel_uri` and `key = f"{RESERVED_IMAGE_NAMESPACE}/{rel_uri}"`
  (`builder.py:1778`) are untouched — IMG-04 names the escape branch only. See D-13.
- **Stripping a drive prefix from the key** (D-12 — deferred, with the measurement).
- Any new runtime dependency, any new `typst_*` config value, any typing-import modernization.

</domain>

<decisions>
## Implementation Decisions

The owner selected **"おすすめで進める"** for all four gray areas, so every D-NN below is Claude's
recommendation locked as a decision. Every value marked *measured* was taken **this session
(2026-08-28)** against the live tree at `7d809b83` — including four real `typst.compile()` runs
through the project's own `.venv` typst-py — not from recall.

### IMG-07 — what the compile gate compiles

- **D-01: The gate's image URI is a real file whose basename carries BOTH a backslash and a double quote.**
  Measured four `typst.compile()` runs: `image("dir\logo.png")` → `TypstError: path must not contain
  a backslash`; `image("dir\\logo.png")` (escaped, decodes to one `\`) → the *same* error;
  `image("we"ird.png")` → `TypstError: unclosed delimiter`; `image("we\"ird.png")` → **OK**. A
  backslash-only URI is therefore closed by IMG-04 *alone* (after normalization no backslash can
  survive, so there is nothing left for escaping to do) — which would make SC#2's "neither alone
  would have closed it" false. A URI whose normalized basename is `we"ird.png` and whose raw
  basename is `sub\we"ird.png` makes both halves load-bearing, in all four combinations:

  | tree | emitted `image(...)` literal | Typst |
  |---|---|---|
  | unfixed | `..._typst_converted/{d}-sub\we"ird.png` | `path must not contain a backslash` |
  | IMG-04 only | `..._typst_converted/{d}-we"ird.png` | `unclosed delimiter` |
  | IMG-05 only | `..._typst_converted/{d}-sub\\we\"ird.png` | `path must not contain a backslash` |
  | both | `..._typst_converted/{d}-we\"ird.png` | **compiles** |

  — **Reversibility:** reversible.

- **D-01a: AMENDED — D-01's `unfixed` row is wrong. The measured refusal is `unclosed delimiter`,
  not `path must not contain a backslash`.** Measured by plan 59-05's four-tree reconstruction
  (`git checkout ec6bd3a4 -- typsphinx/{builder,translator}.py`, restored and verified clean after
  every combination) and independently re-measured by the orchestrator against `typst.compile()`
  directly on the four literal shapes. Corrected row:

  | tree | emitted `image(...)` literal | Typst (measured) |
  |---|---|---|
  | unfixed | `..._typst_converted/{d}-sub\we"ird.png` | `unclosed delimiter` |

  Rows `IMG-04 only`, `IMG-05 only` and `both` all measured exactly as D-01 predicted.

  **Why D-01 got it wrong:** its four `typst.compile()` runs each carried exactly ONE defect —
  `image("dir\logo.png")`, `image("dir\\logo.png")`, `image("we"ird.png")`, `image("we\"ird.png")`.
  None carried a raw backslash and a raw unescaped `"` *simultaneously*, which is what the unfixed
  `_track_image()` + `visit_image()` pipeline actually emits. With both present, the unescaped `"`
  terminates the Typst string literal at parse time, so the semantic backslash-in-path check never
  runs. The `\` in the unfixed row is therefore not load-bearing for the refusal at all — the `"`
  alone decides it, which is why the `IMG-04 only` row shows the same `unclosed delimiter`.

  **SC#2 is unaffected.** A, B and C all fail to compile and only D compiles, so "neither alone
  would have closed it" still holds on this fixture — only the *reason* the unfixed tree fails
  changes. **No test is affected either:** `tests/test_windows_image_uri_render_gate.py:259,263`
  assert that *neither* error string appears on the fixed tree, so nothing was bound to the
  falsified prediction.
  — **Reversibility:** reversible. Owner-approved 2026-08-29 after independent re-measurement.

- **D-02: The gate is an end-to-end `sphinx-build -b typstpdf` run, not a hand-written `.typ`.**
  It must exercise `_track_image()`'s key construction *and* `visit_image()`'s interpolation *and*
  `copy_image_files()`'s copy in one pass; a hand-written `.typ` proves only what its author already
  believed. Modelled on `tests/test_absolute_image_render_gate.py` (`-b typstpdf` on purpose — the
  fatal only aborts on `TypstPDFBuilder.finish()`'s compile path), with a fixture `conf.py` that
  registers a small post-transform rewriting `node["uri"]` to the absolute path of a file created
  outside `doctreedir`. Measured: the file must genuinely exist, because
  `copy_image_files()` copies from `self.images[key]` (the raw `resolved_uri`) and skips with
  `Image file not found` otherwise — a green would then be indistinguishable from a missing file.
  — **Reversibility:** reversible.

- **D-03: The compile gate skips on a filesystem that cannot hold the name, probed — never on `os.name`.**
  Measured on this machine (ext4): `open(r'dir\we"ird.png', "wb")` succeeds; both `\` and `"` are
  illegal in a Windows filename, so `windows-latest` cannot construct the fixture. The skip
  condition is an attempted `tmp_path` create wrapped in `except OSError`, with the reason recorded
  in the skip message. `pytest.mark.skipif(os.name == "nt")` is rejected: it asserts a belief about
  the platform where a two-line probe measures the actual constraint.
  — **Reversibility:** reversible.

- **D-04: A POSIX-runnable string-shape gate runs on EVERY lane alongside it, so `windows-latest` is not left uncovered.**
  It asserts on the emitted `.typ` body from a `-b typst` build (no compile, no fixture file needed):
  the `image("...")` literal for a Windows-shaped absolute URI contains **no raw backslash**, and a
  `"` in the path appears in escaped form. This is the proven
  `TestWindowsPathEscapingRegressionGuard` pattern (`tests/test_templates_path_collision_gate.py:411-470`)
  that ROADMAP constraint 10 names, and it is what makes the phase's Windows-lane claim mean
  something despite D-03's skip.
  — **Reversibility:** reversible.

- **D-05: AMENDED — ROADMAP constraint 5's "neither fix alone closes the compile failure" is half true, and the phase satisfies SC#2 by construction rather than by re-litigating it.**
  The measured half: escaping alone does *not* close it (Typst refuses by value, confirmed above).
  The falsified half: IMG-04 alone *does* close a backslash-only URI. No roadmap edit is requested —
  D-01's fixture makes the conjunction genuinely necessary, so SC#2's wording holds literally on this
  phase's gate. This block exists so planning does not re-derive the claim from the constraint text
  and pick a backslash-only fixture that quietly makes SC#2 unprovable.
  — **Reversibility:** reversible.

### IMG-06 — where the 255-byte bound lands and how it is gated

- **D-06: The bound applies to the FINAL PATH COMPONENT as a whole (`{digest}-{basename}`), not to the basename alone.**
  Measured on ext4: a 250-byte basename is creatable; `{sha1[:8]}-` adds 9 bytes; the resulting
  259-byte component fails with `OSError 36 (ENAMETOOLONG)`. Bounding only the basename leaves a
  264-byte component that still fails — i.e. it would ship a gate that passes while the defect
  survives. The budget for the basename is therefore `255 - len(f"{digest}-")` = 246 bytes.
  — **Reversibility:** reversible.

- **D-07: Truncation keeps the digest whole, keeps the extension, truncates the stem from the right, lands on a UTF-8 character boundary, and never yields an empty stem.**
  Precedence when the budget is tight: digest+`-` first (truncating it reintroduces the collision
  IMG-03 closed), then at least one byte of stem, then the extension. If the extension alone would
  consume the whole remaining budget it is truncated too rather than allowed to squeeze the stem to
  nothing. Boundary safety is by encode-then-decode with `errors="ignore"` or an explicit
  continuation-byte walk — never by slicing the `str` and hoping, since the 255 limit is in **bytes**
  and a multi-byte name is exactly the case a naive slice gets wrong.
  — **Reversibility:** reversible.

- **D-08: IMG-06 needs TWO gates, because `copy_image_files()` swallows the `OSError`.**
  Measured: `builder.py:1988-1992` wraps `shutil.copy2` in `except Exception as e` and logs
  `f"Failed to copy image {imguri}: {e}"`, so the `ENAMETOOLONG` `OSError` never propagates and
  `pytest.raises(OSError)` cannot see it. REQUIREMENTS.md's phrase "raised at `copy_image_files()`
  time" describes the origin, not an observable exception. The gates are:
  (a) a **pure-string unit gate**, all lanes, no filesystem: call the key construction directly and
  assert `len(component.encode("utf-8")) <= 255`, digest intact, extension preserved, stem non-empty,
  boundary-safe — this is also where SC#3's collision property is re-proven for two long URIs sharing
  a basename;
  (b) an **integration gate** through a real `sphinx-build` asserting the pre-fix
  `Failed to copy image …: [Errno 36] File name too long` warning **and** the absent destination
  file, both gone after the fix. The RED evidence quotes that warning verbatim.
  — **Reversibility:** reversible.

### PATH-01 — how "byte-identical at both call sites" is proven

- **D-09: Split by what each mechanism can actually observe — a permanent characterization test for the post-fix classification, a recorded two-tree measurement for the "before and after" half.**
  A test in the suite can only ever pin the tree it runs on, so "identical before and after" is
  inherently a two-tree comparison and belongs in the evidence file (the same shape 57-11 and
  58 D-05(b) used). The suite gets: the **direct-call RED gate** for the two shapes that flip
  (`\manuals\guide` and `\\srv\share\g`, both `False → True`, measured in REQUIREMENTS.md), plus a
  **characterization pin** parametrized over the full shape table at both production call sites
  (`_resolve_target_stem()` at `builder.py:662`, `_track_image()` at `builder.py:1727`). The evidence
  file records the same table run against the pre-fix tree and shows the two outputs byte-identical.
  — **Reversibility:** reversible.

- **D-10: The characterization pin goes through the call sites, the RED gate does not.**
  ROADMAP constraint 8 forbids routing PATH-01's *gate* through either call site — both pre-normalize
  or always carry a `..`, so such a test is tautologically green before and after. That prohibition
  is about the gate. The characterization pin has the opposite job: it must run through the call
  sites, because "the hardening changed no live behaviour" is a claim about the call sites and
  nothing else.
  — **Reversibility:** reversible.

### Cross-cutting

- **D-11: Evidence file is `59-WINDOWS-URI-EVIDENCE.md` — NOT `59-VERIFICATION.md`.**
  `{padded_phase}-VERIFICATION.md` is a name `gsd-verifier` reserves and overwrites wholesale.
  Follows 58 D-07 and the `57-MESSAGE-FIX-EVIDENCE.md` precedent.
  — **Reversibility:** reversible.

- **D-12: The drive-colon case is DEFERRED, not folded in — IMG-04 stays at its literal scope.**
  Measured: `posixpath.basename("C:logo.png".replace("\\", "/"))` returns `C:logo.png` — the colon
  survives normalization, and a `_typst_converted/{digest}-C:logo.png` destination is an illegal
  NTFS filename. But this shape arises only for the *drive-relative* form (a drive letter with no
  following separator), which no Sphinx image post-transform produces — the realistic Windows shape
  `C:\Users\…\img.png` normalizes to a clean `img.png`. IMG-04 and SC#3 both say *backslash*;
  widening them here would be scope creep inside the one phase whose discipline is measured claims.
  Recorded in Deferred Ideas with the measurement so it can become its own requirement.
  — **Reversibility:** reversible.

- **D-13: IMG-05's escaping is computed ONCE, immediately after `_compute_relative_image_path()`, and used by both `add_text` sites.**
  `translator.py:4746` (in-figure) and `4749` (standalone) interpolate the same `adjusted_uri`;
  wrapping at each site duplicates the invariant that the escape must run *last*. One
  `escaped_uri = escape_typst_string(adjusted_uri)` on the line after 4742 makes "last" structural.
  Measured consequence for the zero-test-edit claim: `escape_typst_string()` is a no-op for any path
  containing neither `\` nor `"` nor a control character, so every existing expected `image("...")`
  output stays byte-identical.
  — **Reversibility:** reversible.

### Claude's Discretion

The owner delegated all four gray areas, so the planner additionally retains discretion on:
- Plan decomposition within the constraint-3 rule (the three `builder.py` changes are one sequential
  plan; `translator.py` is parallel-safe alongside it; IMG-07's compile gate is the wave after).
- Whether the key-construction logic is extracted into a module-level helper (which would make D-08(a)'s
  pure-string gate a direct call rather than a build) or stays inline in `_track_image()`.
- Fixture and test-module naming, and whether D-04's all-lane string gate lives in a new module or
  joins an existing Windows-shape test class.
- The exact boundary-safe truncation idiom, provided D-07's precedence order holds.

### Folded Todos

`todo.match-phase 59` returned two matches tagged `resolves_phase: 59`; **both folded** — they are
the source records for two of this phase's requirements:

- `2026-08-16-escapes-outdir-isabs-not-backslash-normalized.md` (score 0.90, area: builder) —
  `_escapes_outdir()` normalizes for its traversal split but calls `posixpath.isabs()` on the RAW
  stem. This is PATH-01 verbatim; closing PATH-01 closes the todo.
- `2026-08-16-track-image-escape-branch-basename-not-normalized.md` (score 0.90, area: builder) —
  `_track_image()`'s escape branch builds its key with `path.basename()` on the RAW URI. This is
  IMG-04 verbatim; closing IMG-04 closes the todo.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone-binding documents
- `.planning/ROADMAP.md` § "🚧 v0.9.1 — Windows path correctness (ACTIVE)" — the 14 binding
  constraints. Bearing directly on this phase: **1** (RED-first; "CI green" is evidence of nothing),
  **3** (PATH-01/IMG-04/IMG-06 share one ~30-line region → one sequential plan, never parallel
  worktrees against `builder.py`), **4** (a plan changing an emitted string and a plan asserting on
  it must not share a wave), **5** (read together with **D-05** above), **7** (255 is a hardcoded
  constant, no CI probe), **8** (PATH-01's gate calls the predicate directly), **9** (zero test
  edits), **10** (CI is not first discovery; local RED→green, then a fresh 3-OS dispatch on the
  post-fix tip), **11** (worktree isolation is standing).
- `.planning/ROADMAP.md` § "Phase 59" — the five success criteria this CONTEXT.md is scoped to.
- `.planning/REQUIREMENTS.md` **PATH-01** (lines 21-32, including the measured reachability note),
  **IMG-04** (40-44), **IMG-05** (46-50), **IMG-06** (52-64), **IMG-07** (66-72), and § "Standing
  constraints for every phase in this milestone" (220-243).

### Prior-phase artifacts this phase is bound to
- `.planning/phases/58-repr-format-decoupling-test-side-only/58-REPR-CENSUS.md` — **the enumeration
  the zero-test-edit claim is checked against.** ROADMAP constraint 9: a plan finding it must edit a
  test is a signal the census was incomplete, not a licence to edit.
- `.planning/phases/58-repr-format-decoupling-test-side-only/58-CONTEXT.md` § D-07/D-08/D-09 — the
  census's classification axes and the AST guard that will go RED if a test's `repr()` pass-criterion
  set changes.
- `.planning/phases/58-repr-format-decoupling-test-side-only/58-DECOUPLING-EVIDENCE.md` — the
  evidence-file shape D-11 follows.

### Research (written 2026-08-27)
- `.planning/research/SUMMARY.md` § "Implications for Roadmap" — its **Phase B** (translator
  escaping, parallel-safe) and **Phase C** (builder triple-fix, sequential single plan) are this
  phase's two plan units. Its Key Finding #4 (zero-test-edits cannot hold) is **superseded** by
  MSG-01/Phase 58 and must not be re-litigated.
- `.planning/research/PITFALLS.md` — the measured Typst refusal behaviours.

### Code under change
- `typsphinx/builder.py:194-238` — `_is_absolute_image_uri()` (the normalize-then-decide idiom
  PATH-01 copies), `_escapes_outdir()`, `_is_drive_qualified()`.
- `typsphinx/builder.py:1712-1786` — `_track_image()`'s absolute branch: the `_escapes_outdir()` call
  site at 1727, the digest/key construction at 1761-1765, the `!r` warning at 1766-1769 (read-only
  here), and the two non-escape key branches at 1778/1783.
- `typsphinx/builder.py:1957-1992` — `copy_image_files()`, including the `except Exception` that
  swallows `ENAMETOOLONG` (D-08).
- `typsphinx/translator.py:156` — `escape_typst_string()`, and `:4736-4765` — `visit_image()`.

### Project standing rules
- `CLAUDE.md` § "Worktree-isolated execution" — mandatory per-worktree
  `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` + `uv run` for every executor.
- `pyproject.toml` `[tool.pytest.ini_options]` — `filterwarnings` promotes `DeprecationWarning` /
  `PendingDeprecationWarning` to errors; a new test module must not trip them.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `tests/test_absolute_image_render_gate.py` + `tests/fixtures/absolute_image_render_gate/` — the
  **template for D-01/D-02's gate**: a fixture `conf.py` registering a custom post-transform that
  rewrites `node["uri"]` to an absolute path under `<doctreedir>/images/` without needing an external
  converter binary, plus `_run_sphinx_build_typstpdf()` and a `TYPST_AVAILABLE` import guard. The new
  fixture changes only *which* absolute path the post-transform writes.
- `tests/test_templates_path_collision_gate.py:411-470` — `TestWindowsPathEscapingRegressionGuard`,
  the proven all-lane Windows-shaped-string pattern D-04 follows, including its docstring rule *call
  the real product function, never a re-pasted f-string*.
- `typsphinx/translator.py:156` `escape_typst_string()` — already the single source of truth for
  string-literal escaping; IMG-05 is a routing change, not a new escaper.
- `typsphinx/builder.py` `_is_drive_qualified()` — the one place the drive-letter idiom is written
  (A47-03/A3). Any drive-shape check this phase needs calls it rather than re-deriving.
- `hashlib`, `posixpath`, `ntpath` (stdlib) — everything IMG-04/IMG-06 need. **Zero new dependencies.**

### Established Patterns
- **Normalize, then decide.** `_is_absolute_image_uri()` does `resolved_uri.replace("\\", "/")` and
  then asks `posixpath.isabs(...) or _is_drive_qualified(...)`. PATH-01 makes `_escapes_outdir()`
  match it — the traversal split there already normalizes; only the `isabs`/drive pair reads the raw
  stem.
- **`posixpath`, never the OS-native `path`, for platform-independent shape decisions** — with the
  measured reason recorded inline at `builder.py:233-238` (`ntpath.isabs("/abs/manual")` is `False`).
  The same trap is what makes today's `path.basename()` at 1765 wrong: on a POSIX build host `path`
  is `posixpath`, which does not split on `\`, so the whole URI comes back as the "basename".
- **Windows shapes are hand-built string literals tested on every lane**, never gated on `os.name`.
  D-03's compile gate is the deliberate, probe-guarded exception; D-04 exists so the rule still holds
  for the phase as a whole.

### Integration Points
- `_escapes_outdir()` is called from *inside* `_track_image()` (`builder.py:1727`), thirteen lines
  above the key construction IMG-04/IMG-06 rewrite — ROADMAP constraint 3's whole basis.
- `builder.py:1767`'s warning interpolates `key`, the exact value IMG-04/IMG-06 change, and is one of
  the sites MSG-03 re-quotes in Phase 60 — ROADMAP constraint 4's collision site. Nothing in this
  phase may touch that message string.
- `self.images[key] = resolved_uri` (`builder.py:1783`) → `copy_image_files()` uses the value as the
  override copy source. This is why D-02's fixture file must genuinely exist on disk under its
  backslash-bearing name.
- `_compute_relative_image_path()` (`translator.py:5047`) prepends the `../` depth prefix; IMG-05
  wraps its **return value**, never the raw `uri` before the call.

</code_context>

<specifics>
## Specific Ideas

1. **The four-combination table in D-01 is the concrete design target.** If a plan or executor
   proposes a backslash-only fixture for the compile gate, that is the failure mode to point at: it
   is green with IMG-04 alone, so it cannot prove SC#2's "neither alone would have closed it".

2. **`{digest}-` is 9 bytes and must be counted.** The single most likely IMG-06 mistake is bounding
   `basename` to 255 and shipping a 264-byte component. Measured: 259 bytes already raises
   `OSError 36` on ext4.

3. **A green compile is not evidence unless the source file existed.** `copy_image_files()` skips a
   missing source with a warning and the build continues; the compile then fails for the *wrong*
   reason (file not found), and a future "fix" to that symptom would be chasing the fixture. Assert
   the destination file exists before asserting the compile succeeded.

4. **`typst-py` presence must be confirmed in the worktree venv before claiming a green** — the
   compile gate is `TYPST_AVAILABLE`-guarded and a skip reads as a pass in a summary line. Phase 58
   recorded the same trap (58 specifics #4).

5. **RED evidence must carry Typst's own words.** SC#2 names the `path must not contain a backslash`
   refusal explicitly; the evidence file quotes the `TypstError` text, not a paraphrase.

</specifics>

<deferred>
## Deferred Ideas

- **The drive-relative colon in a relocation key (D-12).** `C:logo.png` normalizes to `C:logo.png`,
  and `_typst_converted/{digest}-C:logo.png` is an illegal NTFS filename. Reaches the escape branch
  via `_is_drive_qualified()`, but no Sphinx image post-transform produces the drive-relative form.
  Sized as its own requirement (~2 lines in the key construction, reusing `_is_drive_qualified()`,
  plus one test case), not folded into IMG-04.

- **The non-escape key branches can still carry a backslash on POSIX.** `key = rel_uri` at
  `builder.py:1783` takes `relpath(...).replace(path.sep, "/")`, and on a POSIX host `path.sep` is
  `/` — so a filename containing a literal backslash survives into the emitted `image()` and Typst
  refuses it by value, which escaping cannot fix either. IMG-04 names the escape branch only.
  Genuinely out of this phase's requirement text; record it rather than widen SC#3.

- **A path containing a literal single quote (`57-REVIEW.md` IN-01).** Belongs to MSG-02's gate in
  Phase 60, which names it. Unrelated to the `"` this phase's D-01 fixture uses (that one is about
  the Typst *string literal*, not about message quoting).

### Reviewed Todos (not folded)

`todo.match-phase 59` returned five further matches, **none folded** — all score 0.60 on generic
keyword overlap and none touches this phase's requirements:

- `2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos.md` — local toolchain; CI remains the lint
  authority.
- `2026-08-14-numref-number-diverges-per-master-and-vanishes-for-non-root-only-figures.md` —
  translator numbering, a separate defect family.
- `2026-08-16-dependabot-prs-die-on-uv-lock-locked-mismatch.md` — CI/tooling.
- `2026-08-16-root-toctree-duplicates-section-children-in-html-sidebar.md` — docs.

</deferred>

---

*Phase: 59-path-shape-predicate-and-image-uri-correctness*
*Context gathered: 2026-08-28*
