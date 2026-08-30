# Pitfalls Research

**Domain:** Bug-fix milestone on a mature Sphinx→Typst build tool — Windows path-shape correctness
(three related defect families: an un-normalized escape predicate, an un-escaped/un-normalized
image-relocation path, and a codebase-wide `!r`-vs-delimiter message-quoting inconsistency)
**Researched:** 2026-08-27
**Confidence:** HIGH — every pitfall below is anchored to a line number, a docstring, a real grep
result, or a named test in this repository at HEAD, not to generic cross-platform-Python folklore.

## Critical Pitfalls

### Pitfall 1: Two existing tests hard-code the CURRENT (backslash-doubling) `repr()` output as
their pass criterion at two of the ~20 in-scope message sites — the quoting-helper fix breaks
them by design, on POSIX, with no Windows CI required to see it

**What goes wrong:**
`tests/test_out02_escape_target_gate.py::test_escape_shape_refused_with_containment_proof[drive]`
asserts `assert repr(target) in combined_output` for `target = "C:\\escape.typ"` (line 134) — this
targets `builder.py:697`'s `f"name: {target!r} -- using {fallback!r} instead"`, one of the sites
PROJECT.md's group 3 names for the new helper. `tests/test_builder.py`'s
`test_post_process_images_rehome_escape_relocates_with_warning` asserts
`assert repr(abs_uri) in message` (line 598) against `builder.py:1767`'s
`f"could not rehome image URI {resolved_uri!r} relative..."`. Both docstrings/comments explicitly
acknowledge `repr()` doubles a backslash and assert *for* that doubling, not around it:
`test_out02_escape_target_gate.py`'s own comment reads "repr() doubles it for display, so the
warning-text search must match the repr'd form"; `test_builder.py`'s reads "on Windows repr()
doubles every backslash ... Asserting against repr(abs_uri) holds on both." The `[drive]`
parametrization is explicitly marked to run "on every platform (including the drive-qualified
case)" — it is not Windows-only, so it fails on THIS POSIX machine the moment `builder.py:697` is
rewired to the new delimiter-aware helper (which, by design, stops doubling the backslash). The
`test_builder.py` case is subtler: on POSIX its `abs_uri` (`os.path.join(os.sep, ...)`) contains no
backslash, so `repr(abs_uri)` happens to equal the new helper's output too — it stays green
*here*, unedited, but will go red the moment the SAME test runs on the `windows-latest` lane, where
`os.sep == "\\"` makes `abs_uri` backslash-bearing and `repr()`'s doubling and the new helper's
non-doubling diverge.

**Why it happens:**
The two sites were fixed shape-first ("stop doubling backslashes") without auditing every existing
assertion that already depends on the OLD shape. `repr(value) in message` is an attractive,
DRY-looking assertion (it reuses the product's own quoting instead of hardcoding a literal), but
that is exactly what makes it silently track whatever the product currently does, including a
defect.

**How to avoid:**
Before writing the shared quoting helper, run `grep -rn "repr(" tests/*.py` (already run for this
research — 20 hits; the other 18 are all on identifier/list/bytes/int values, never a plain path
string, and correctly stay `!r`/`repr()`) and manually triage every hit for "is the asserted value
path-shaped." Rewrite `test_escape_shape_refused_with_containment_proof[drive]`'s assertion to
expect the new helper's actual (non-doubled, correctly-delimited) output instead of `repr(target)`.
For `test_post_process_images_rehome_escape_relocates_with_warning`, either parametrize it with an
explicitly Windows-shaped `abs_uri` literal (not `os.sep`-derived, so its expectation is the same
on every host) asserting the NEW helper's output, or add a comment recording that the existing
`os.sep`-derived assertion is POSIX-coincidental and will need a matching edit if this test is ever
run against a real Windows-shaped `abs_uri`.

**Warning signs:**
`pytest tests/test_out02_escape_target_gate.py -k drive` or
`pytest tests/test_builder.py -k rehome_escape` goes red immediately after the source edit, on this
machine, with no CI dispatch needed — treat that red as EXPECTED and required, not as a signal to
revert the source fix.

**Phase to address:**
The quoting-helper phase (defect family 3) itself. The two test edits must land in the SAME plan
that touches `builder.py:697` and `builder.py:1767` — never deferred as "tests still pass, ship
now," because for the `[drive]` case they do NOT still pass, and for the rehome case they pass for
the wrong reason (POSIX coincidence) and will silently stop being evidence of anything once a
Windows-shaped value is ever asserted against.

---

### Pitfall 2: The type-check failure at `template_registry.py:410` interpolates `template`
*before* its type is known to be path-shaped — routing it through a string-only quoting helper
built for family 3 will misbehave on the exact non-str values three existing tests deliberately
supply

**What goes wrong:**
`template_registry.py:408-412`:
```python
if template and not isinstance(template, (str, os.PathLike)):
    failures.append(
        f"registry key {key!r}'s template {template!r} must be a path string or os.PathLike, "
        f"not a {type(template).__name__}"
    )
```
This branch is reached PRECISELY when `template` is *not* `str`/`os.PathLike` — by construction,
the value here is never a plain path string. `tests/test_template_registry.py` exercises this with
`template = ["a", "b"]` (asserting `repr(["a", "b"]) in message`, line 832) and
`template = b"base.typ"` (asserting `repr(b"base.typ") in message`, line 847). A quoting helper
built to choose a delimiter based on whether a *string* contains `'`/`"` will either raise
(`AttributeError`/`TypeError` calling `.replace()` on a `list` or `bytes`) or silently produce the
wrong quoting shape if naively applied to this f-string too. This is the SAME family PROJECT.md
groups under "template_registry.py:410,422,433," but 410 is structurally different from its two
siblings.

**Why it happens:**
Grouping "the three `template_registry.py` sites" as one unit (as the source todo and PROJECT.md
both do, reasonably, since they are textually adjacent and share the `{template!r}` shape) hides
that line 410 fires on the FAILURE of the very isinstance check that lines 422/433 rely on having
already passed (`elif template:` — only reached when the outer `if` is False, i.e. `template` IS
`str`/`os.PathLike`).

**How to avoid:**
Treat `template_registry.py:410` as excluded from the new helper, with a one-line comment
explaining why (the value is guaranteed non-path-shaped there); route only lines 422 and 433
(inside the `elif template:` block, where `template` is guaranteed `str`/`os.PathLike`) through it.

**Warning signs:**
`pytest tests/test_template_registry.py -k "list_template_field or bytes_template_field"` raises
an unhandled exception (not the expected `ExtensionError`) or produces a mangled message.

**Phase to address:**
The quoting-helper phase (defect family 3), as an explicit per-site classification step, not an
incidental side effect of a codebase-wide find/replace on `{...!r}` fragments.

---

### Pitfall 3: `os.PathLike` values (e.g. a `pathlib.Path` `template`) reaching the quoting helper
break it unless the helper stringifies first — the codebase already deliberately accepts `Path`
here, and a working shape must not regress

**What goes wrong:**
`template_registry.py`'s own design comment (lines 398-407) documents that `template` accepting
BOTH `str` and `os.PathLike` is deliberate ("a `pathlib.Path` `template` works end to end TODAY,
and blanket-rejecting it would withdraw a working shape rather than close a crash"), and
`tests/test_template_registry.py`'s "Test H (control)" (line 851, `declared_template =
Path("sub/path_tpl.typ")`) exercises exactly this. `Path.__repr__` renders as
`PosixPath('sub/path_tpl.typ')` (or `WindowsPath(...)` on Windows) — not a bare quoted string —
and `Path` has no `.replace(old, new)` string method (it has `.replace()` for filesystem rename,
a completely different signature). A helper written assuming `str` input will either raise
`TypeError` calling a string method on a `Path`, or leak a `PosixPath(...)` wrapper into a
user-facing refusal message if it falls back to bare `f"{value}"`.

**Why it happens:**
Every failing example seen while writing the fix will likely be a plain `str` (that's what a
`conf.py` author normally writes), so a `Path`-valued `template` is easy to never exercise by hand
before shipping — it only surfaces via the one existing control test, or a real user who wrote
`Path("template.typ")` in `conf.py`.

**How to avoid:**
The shared helper's first action should be `value = str(value)` (or every call site does the
`str(...)` conversion before calling it) — never assume the incoming value is already `str`.

**Warning signs:**
A new/changed message for a `Path`-valued `template` shows `PosixPath('...')` or
`WindowsPath('...')` instead of a plain quoted path, or the existing "Test H" control test starts
raising instead of resolving successfully.

**Phase to address:**
The quoting-helper phase (defect family 3) — add a unit test with a `pathlib.Path` `template`
value that *also* violates CONF-17 or is missing (exercising lines 422/433, not just the
already-covered happy-path "Test H"), asserting the emitted message is a plain quoted string.

---

### Pitfall 4: Fixing `translator.py:4746/4749` by ALSO folding `\` to `/` (not just adding
`escape_typst_string()`) would repeat this project's own accepted classification tradeoff at the
wrong layer, turning a loud compile error into a silent wrong-file reference

**What goes wrong:**
`_is_absolute_image_uri()`'s docstring (required reading, `builder.py:160-165`) states the
project's own accepted tradeoff explicitly: normalizing `\`→`/` before classifying a URI as
absolute means "a POSIX filename that literally contains a backslash character is classified as
absolute here, on every platform, even though a bare backslash carries no special meaning in a
POSIX filename." That tradeoff is accepted at the CLASSIFICATION boundary — a false positive there
only causes an unnecessary rehome (a distinct, well-tested, warned-about branch). It would be a
DIFFERENT and strictly worse tradeoff to repeat `.replace("\\", "/")` inside `visit_image()`'s
emission (`translator.py:4746`/`4749`), because by that point the string is CONTENT — the literal
path Typst will open — not a classification input. Silently rewriting a legal POSIX filename's
literal backslash to a slash there changes WHICH FILE Typst looks for: a loud, debuggable
"path must not contain a backslash" compile error becomes a silent "file not found" (or, worse, a
silently-wrong file if the slash-substituted name happens to resolve to something that exists).

**Why it happens:**
The fix sketch for this defect family is naturally read as "make this path safe for Typst," and
`.replace("\\", "/")` is the exact idiom used two call sites away (`_is_absolute_image_uri`,
`_escapes_outdir`) for a *different* purpose (classification) — pattern-matching on the idiom
without re-deriving why it is safe at those two sites (pure classification, no effect on the
written bytes) but not at this third one (the written bytes ARE the classification's own subject)
is an easy, plausible-looking mistake.

**How to avoid:**
The fix at `translator.py:4746`/`4749` is exactly one change: wrap `adjusted_uri` in
`escape_typst_string(adjusted_uri)` (the existing helper, `translator.py:156`, which already
escapes a literal backslash to `\\` — content-preserving, not shape-changing). Land it as its own
diff hunk so a reviewer can confirm no `.replace()` call was added alongside it.

**Warning signs:**
A regression test asserting that an ordinary (non-absolute, non-escaping) relative image URI
containing a literal backslash character in its basename renders with `\\` (escaped) in the
`.typ` output — not with `/` silently substituted.

**Phase to address:**
The `_track_image()`/`visit_image()` slice (defect family 2).

---

### Pitfall 5: A naive length bound on `{digest8}-{basename}` reintroduces the exact collision the
digest was added (IMG-03) to prevent, or produces an unopenable filename — five distinct failure
shapes, all reachable from this project's specific `f"{RESERVED_IMAGE_NAMESPACE}/{digest}-{basename}"`
construction

**What goes wrong, enumerated against the actual construction (`builder.py:1761-1765`):**

1. **Wrong component truncated.** The key is a TWO-segment relative path
   (`_typst_converted/<digest>-<basename>`); POSIX's 255-byte `NAME_MAX` applies PER COMPONENT.
   Truncating the whole `key` string risks eating into `RESERVED_IMAGE_NAMESPACE` or the digest
   itself; the bound belongs on `f"{digest}-{basename}"` alone.
2. **Mid-character UTF-8 split.** `NAME_MAX` is a byte limit; slicing a UTF-8-encoded basename by
   raw byte count (needed to respect that limit) can split a multi-byte character, producing
   invalid UTF-8 that some filesystems refuse to create — trading today's `ENAMETOOLONG` for a
   different, equally opaque `OSError` at the same call site.
3. **Extension lost.** Truncating from the tail with no extension awareness turns
   `long-name.png` into `long-nam` — Typst's `image()` (and this project's own
   `supported_image_types` mimetype-preference logic) can rely on the extension to select an
   embedder, so a working image silently becomes a compile error or a mis-rendered one.
4. **Collision reintroduced.** Two different long basenames sharing the same truncated prefix
   collide again UNLESS the digest (already unique per full `resolved_uri`, not per basename)
   stays untruncated and is what any later collision-avoidance logic anchors on — this is exactly
   what the source todo's fix sketch flags: "the digest must stay the collision anchor when the
   basename is truncated."
5. **Empty-stem edge.** A pathological basename that truncates to nothing (name shorter than the
   fixed digest+separator overhead budgeted for) can yield a leading-dot result (e.g. bare
   `.png`), silently changing POSIX visibility semantics (a hidden file) as a side effect of a
   length fix nobody asked for.

**Why it happens:**
"Add a length cap" sounds like a one-line `[:N]` slice; the digest-collision-anchor requirement,
the per-component (not whole-path) scope of `NAME_MAX`, and the byte-vs-character slicing
distinction are all easy to miss under that framing.

**How to avoid:**
Bound only the `f"{digest}-{basename}"` component; split the extension first (e.g. via
`os.path.splitext`) and preserve it; truncate the STEM portion (never the digest, never the
extension); slice in `str` space (Python `str` indexing is already character-safe — the byte-split
risk appears only if the implementation re-encodes to UTF-8 bytes to check the length and then
slices the BYTES rather than the `str`); size-check against the encoded byte length but slice the
decoded characters.

**Warning signs:**
A test with a >255-character basename should assert THREE things, not just "build succeeds": (a)
no `ENAMETOOLONG`/`OSError`, (b) the resulting file is present with its original extension intact,
and (c) two DIFFERENT long-but-truncation-colliding basenames still produce two DIFFERENT keys
(collision preservation, not merely length compliance) — a test that only checks (a) would pass
even for a fix that reintroduces gap 4.

**Phase to address:**
Defect family 2's length-bound sub-task. Per PROJECT.md's binding constraint #3 this needs its OWN
gate — "no compile-visible symptom... a compile gate will not force it out" — sequenced separately
from the `escape_typst_string()` gate in Pitfall 4.

---

### Pitfall 6: A POSIX-only "no doubled separator" unit test is necessary but was already proven
insufficient once at this exact site family (Phase 57) — the discipline this project has since
adopted for it must be applied to all ~20 sites from the start, not re-derived by trial dispatch

**What goes wrong:**
Phase 57 burned two full CI matrix dispatches (`31956166848`, `31959060298`) on this same
`typst_document_templates`-registry message family before landing 57-11's fix, and even after
57-11 landed, `57-REVIEW.md`'s WR-01 finding shows the fix ITSELF was incomplete (it removed
backslash-doubling but also dropped `repr()`'s quote-disambiguation, so a path containing a literal
`'` now closes the message's quoting early) — meaning even a real green `windows-latest` dispatch
did not, by itself, prove the fix was fully correct. The pattern that DOES work and IS already
proven — `TestWindowsPathEscapingRegressionGuard` in `tests/test_templates_path_collision_gate.py`
calling the message-building functions DIRECTLY with a Windows-shaped string literal, asserting no
doubled separator, entirely on POSIX, no real Windows filesystem needed — exists in this repo
today and is exactly what PROJECT.md's binding constraint #4 requires be extended with the sibling
single-quote case (57-REVIEW's IN-01).

**Why it happens:**
"Push and see what `windows-latest` says" is a faster first step to try than writing a
function-level Windows-shaped-string test, especially when the failure mode (backslash doubling)
seems like it should be visible in a diff review — Phase 57's own history shows it was
misdiagnosed as a path-SEPARATOR problem twice before being correctly diagnosed as an ESCAPING
problem, which is a strong empirical signal that eyeballing the diff is not reliable for this
defect class.

**How to avoid:**
For every one of the ~20 sites plus both `_escapes_outdir()`/`_track_image()` defect families:
write the Windows-shaped-string (and, for family 2, a real `typst.compile()`) RED fixture FIRST,
confirm it fails against the unfixed function via a plain `pytest`/`python -c` invocation on this
POSIX machine, THEN fix, THEN reconfirm green — all before the first CI dispatch. Reserve the
`windows-latest` lane for FINAL confirmation (constraint #6), never for diagnosis.

**Warning signs:**
A plan for this milestone that proposes "dispatch to `windows-latest` and see" as a discovery step,
rather than a POSIX-runnable RED-first fixture, is repeating Phase 57's exact costly pattern.

**Phase to address:**
Cross-cutting — call it out once in the roadmap's shared discipline rather than per-phase; every
phase in this milestone inherits it.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|-----------------|------------------|
| Leaving `template_registry.py:410`'s type-check message on plain `!r` instead of routing it through the new quoting helper | Avoids building type-dispatch logic into the helper (Pitfall 2) | A `list`/`bytes`/`int` `template` value's repr stays possibly-ugly (e.g. `b'base.typ'`) forever, inconsistent in STYLE with its two path-valued siblings two lines below | Always acceptable here — the value is provably never path-shaped at that line, so there is no correctness gap, only a cosmetic asymmetry the source todo itself does not ask to close |
| Not adding a compile-visible OR filesystem-visible regression test for `writer.py:511-513`'s debug log before quoting-fixing it | Faster — this site has zero existing test coverage (confirmed: `grep -rn "Rendering wrapper for docname" tests/` returns nothing) | The fix itself is permanently unverified; a future regression here is invisible to CI forever | Never — add at least one `caplog`-based assertion alongside the fix, mirroring the pattern `test_builder.py:591` already uses for the sibling `logger.warning` site |
| Treating the "3-OS CI green" acceptance bar (constraint #6) as sufficient proof on its own | Simpler mental model — one gate to watch | Constraint #6's own bar was already shown insufficient once for this exact area: 57-11 shipped, CI went green (12/12, run `32557477023`), and WR-01 (single-quote quote-disambiguation) still shipped broken because no test asserted the quote-disambiguation property | Never for this milestone specifically — always pair the 3-OS lane with the function-level RED-first fixtures (Pitfall 6) |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|-----------------|-------------------|
| Worktree-isolated execution (CLAUDE.md, standing mode) | Editing `builder.py`/`translator.py`/`template_registry.py` in a worktree without its own `uv sync --extra dev`, so `pytest` imports the MAIN tree's unchanged editable install and every RED-first fixture in this milestone falsely reports GREEN against the unfixed code | `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` then `uv run pytest ...` for every command in every worktree, per CLAUDE.md's "Worktree-isolated execution" section (mandatory, not conditional, per the project owner's 2026-07-20 decision) |
| `ruff` on this NixOS dev machine | Trusting a local `ruff check .` result inside a freshly-provisioned worktree venv, which pulls a generic-linux wheel whose ELF the loader rejects — silently reporting nothing or erroring out, mistaken for "clean" | Treat CI's `lint` job as sole lint authority for this milestone (per user memory: "ruff は未解消... lint 権威は CI"); do not gate a local commit decision on a worktree `ruff` run |
| The 3-OS CI matrix (`ubuntu-latest`/`windows-latest`/`macos-latest`, confirmed in `.github/workflows/ci.yml`) | Using a real CI dispatch as the FIRST signal for a Windows-shape defect (Phase 57's proven-costly pattern, Pitfall 6) | Front-load every Windows-shape assertion into a POSIX-runnable, function-level fixture (mirroring `TestWindowsPathEscapingRegressionGuard`) and reserve CI for final confirmation only |
| This project's "RED before fix" hard rule (binding constraint #1, all three defects latent, `windows-latest` currently green and would stay green unfixed) | Writing the fix first and the regression test second, then never actually confirming the test fails against the PRE-fix code (since the pre-fix code is gone by the time the test exists) | Commit the failing test against the unfixed tree (or capture its failure output) BEFORE the fix commit, per this project's standing GATE-01 discipline already invoked by both source todos read for this research |

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|-----------------|
| Byte-slicing a UTF-8 basename for the WR-01 length bound without character-boundary awareness (Pitfall 5.2) | An intermittent `UnicodeDecodeError` or filesystem-level rejection, reproducible only with non-ASCII (e.g. this project's own documented Japanese-filename edge cases) basenames long enough to trip the 255-byte cap | Slice in `str`/character space, size-check against the UTF-8-encoded byte length, never slice the encoded bytes directly | Any project with a non-ASCII image filename near or past 255 UTF-8 bytes (roughly 85+ multi-byte CJK characters) |
| `NAME_MAX` differs by filesystem/OS (POSIX ext4/APFS: 255 bytes; Windows without long-path opt-in: `MAX_PATH` 260 total, a different limit shape entirely) | A length-bound fix validated only via a POSIX `ENAMETOOLONG` reproduction may not reproduce — or may fail differently — on the `windows-latest` CI lane | Do not assume the POSIX reproduction generalizes; if the `windows-latest` lane is silent on this specific gate, verify it is silent because the fix works there, not because Windows' different length semantics never triggered the code path at all | Whenever the length-bound gate is asserted only via one platform's error class/errno |

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Treating the quoting helper as a security boundary (escaping a path for LOG-MESSAGE legibility) and conflating it with the SHA-1 relocation digest (a collision-avoidance key, explicitly documented in `builder.py` as non-cryptographic and outside this project's ruff security-rule selection) | None directly — both are correctly non-security-boundary constructs today — but a future contributor "hardening" one in response to a scanner finding could accidentally change the digest's determinism (e.g. adding a random salt), breaking the documented "two builds of the identical project emit the same filename" invariant | Preserve the existing `builder.py` comment explaining the digest is a collision-avoidance key, not a security boundary, when touching the surrounding code for the length-bound fix (Pitfall 5) |

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-------------------|
| A refusal message whose path is delimited with a single quote (`'...'`) when the path itself contains a literal `'` (57-REVIEW's WR-01/IN-01) reads as if it closes early, hiding the rest of the actual path from the reader | A `conf.py` author debugging a template-path collision on a path like `/home/O'Brien's Projects/_templates/nested` sees a message that appears to truncate mid-sentence | Choose `"` as the delimiter when the value contains `'` and not `"`, otherwise `'`, escaping only the chosen delimiter if both appear (exactly the suggested fix already recorded in the source todo) |
| A message that leaks a `PosixPath(...)`/`WindowsPath(...)` repr wrapper (Pitfall 3) instead of a plain path string | Reads as an internal implementation detail leaking into user-facing output, undermining trust that the tool understands its own configuration | Stringify every value before it reaches the quoting helper |

## "Looks Done But Isn't" Checklist

- [ ] **Quoting-helper rollout across all ~20 sites:** Often missing the per-site type/shape audit
  (Pitfalls 1–3) — verify each site's interpolated value is guaranteed `str`/path-shaped before
  routing it through the new helper, not just textually similar to a site that is.
- [ ] **`_track_image()`'s three gaps (basename normalization, escaping, length bound):** Often
  fixed as "gap 1 only" (the smallest useful step the source todo itself calls out) while gaps 2/3
  are silently left latent — verify all three have their OWN RED-first gate, per PROJECT.md's
  explicit "Gap 3 has no compile-visible symptom... needs its own gate."
  Their prevention/verification: a real `typst.compile()` for gap 2 (per binding constraint #2 —
  an assertion stopping at `node["uri"]` cannot see it), and a >255-char basename fixture asserting
  collision-preservation (not just length) for gap 3.
- [ ] **The two existing tests that hard-code `repr()`'s doubling as their pass criterion
  (Pitfall 1):** Often missed because they currently pass (on POSIX, for the non-drive-shaped
  parametrizations) right up until the exact line they target is rewired — verify by running them
  BEFORE claiming the quoting-helper phase complete, expecting and confirming the `[drive]` one
  goes red.
- [ ] **`_escapes_outdir()`'s widened predicate:** Often verified only against the driveless-
  absolute shape the todo measures — verify the existing OUT-01/OUT-02 regression suite (drive-
  qualified and POSIX-absolute branches) still passes unchanged, since those two shapes were
  already correctly classified pre-fix and must not regress.

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|----------------|------------------|
| Pitfall 1 (two tests break on the intended fix) | LOW | Edit the two named tests to assert the new helper's output instead of `repr(...)`; this is expected work, not a regression to revert |
| Pitfall 2/3 (helper misapplied to a non-str or PathLike value) | LOW | Add the type guard/stringify-first step to the shared helper; re-run `tests/test_template_registry.py -k "list_template_field or bytes_template_field or pathlike"` |
| Pitfall 4 (backslash silently folded to slash in emitted content) | MEDIUM | Revert the extra `.replace()` call; re-verify via the regression test that a literal-backslash relative basename round-trips escaped, not substituted |
| Pitfall 5 (length-bound truncation reintroduces a collision or invalid name) | MEDIUM | Add the missing extension-preservation/digest-anchor step; add the two-adversarial-basenames collision test before re-shipping |
| Pitfall 6 (CI dispatch used for diagnosis, burning matrix runs) | HIGH (time cost, not correctness cost) | Stop dispatching; write the POSIX-runnable function-level fixture first, confirm RED against the unfixed function locally, then fix and re-dispatch once |

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|-------------------|----------------|
| 1: hard-coded `repr()` test expectations | Quoting-helper phase (family 3) | `pytest tests/test_out02_escape_target_gate.py -k drive` and `tests/test_builder.py -k rehome_escape` both green, asserting the NEW (non-doubled, delimiter-aware) form, not `repr(...)` |
| 2: `template_registry.py:410` type-check site wrongly routed through the helper | Quoting-helper phase (family 3) | `pytest tests/test_template_registry.py -k "list_template_field or bytes_template_field"` stays green with `ExtensionError` (not an unhandled exception) |
| 3: `os.PathLike` value breaks the helper | Quoting-helper phase (family 3) | New unit test: a `pathlib.Path` `template` that also fails CONF-17/existence emits a plain quoted string |
| 4: backslash silently folded to slash at image emission | `_track_image()`/`visit_image()` phase (family 2) | New regression test: literal-backslash relative basename renders `\\`-escaped in `.typ`, not slash-substituted |
| 5: naive length-bound truncation | `_track_image()`/`visit_image()` phase (family 2), its own gate per binding constraint #3 | Two adversarially-truncation-colliding >255-char basenames produce two distinct keys; extension survives |
| 6: CI-dispatch-as-diagnosis | Cross-cutting, stated once in roadmap shared discipline | Every phase's plan shows a POSIX-runnable RED fixture committed/confirmed BEFORE the corresponding fix commit |

## Sources

- `typsphinx/builder.py` (this repository, HEAD) — `_is_absolute_image_uri()` docstring
  (lines 121-194, especially 160-165's stated tradeoff), `_escapes_outdir()` (197-238),
  `_track_image()` (1637-1792), the message-builder helpers (`_conf17_violation_message`,
  `_templates_path_collision_message`, `_bundle_destination_collision_message`, lines 303-402).
- `typsphinx/translator.py` (this repository, HEAD) — `escape_typst_string()` (156-187),
  `visit_image()` (4718-4766).
- `typsphinx/template_registry.py` (this repository, HEAD) — lines 395-434 (the type-check/
  CONF-17/existence failure trio).
- `.planning/todos/pending/2026-08-16-track-image-escape-branch-basename-not-normalized.md`
- `.planning/todos/pending/2026-08-17-repr-escaped-paths-in-remaining-user-facing-messages.md`
- `.planning/todos/pending/2026-08-16-escapes-outdir-isabs-not-backslash-normalized.md`
- `tests/test_out02_escape_target_gate.py` (lines 79-138, especially the `[drive]` parametrization
  and its `repr(target)` assertion) — grepped and read directly for this research.
- `tests/test_builder.py` (lines 560-599, `test_post_process_images_rehome_escape_relocates_with_warning`)
  — grepped and read directly for this research.
- `tests/test_template_registry.py` (lines 820-1005, the type/bytes/pathlike-value tests) —
  grepped and read directly for this research.
- `tests/test_templates_path_collision_gate.py` (lines 440-491,
  `TestWindowsPathEscapingRegressionGuard`) — the existing proven POSIX-runnable Windows-shape
  test pattern this milestone's binding constraint #4 requires extending.
- `.github/workflows/ci.yml` (lines 12-46) — confirms the 3-OS (`ubuntu-latest`/`windows-latest`/
  `macos-latest`) matrix binding constraint #6 references.
- `.planning/PROJECT.md` — "## Current Milestone: v0.9.1 Windows path correctness" section (goal,
  target features, binding constraints, deferred items).
- `CLAUDE.md` — "Conventions & gotchas" and "Worktree-isolated execution" sections.

---
*Pitfalls research for: typsphinx v0.9.1 "Windows path correctness"*
*Researched: 2026-08-27*
