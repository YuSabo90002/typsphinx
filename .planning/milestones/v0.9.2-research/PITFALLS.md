# Pitfalls Research — v0.9.2 (Inline Image Blocker Fix + Release)

**Domain:** Sphinx→Typst translator bug-fix + a version-skip PyPI release in this specific repository
**Researched:** 2026-08-30
**Confidence:** HIGH — every claim below is either a direct file:line read at HEAD, a live re-run of
this repository's own commands/API in a scratch directory, or a citation to this project's own
recorded milestone history (RETROSPECTIVE.md, the v0.9.1 audit, archived phase artifacts). No
claim is carried forward from planning prose without independent verification against the current
tree; two places (below) where planning prose could plausibly be assumed were checked and found
correct, and are cited as "confirmed," not "assumed."

---

## Part 1 — Translator-fix pitfalls (mined from this repo's own history)

### Pitfall 1: A gate that asserts on the emitted string cannot see a parser-level defect

**What goes wrong:** A regression test constructs a doctree, runs the translator, and asserts
against `translator.body` (a string) or against `node["uri"]` — never against a real
`typst.compile()`. The emitted string *looks* syntactically plausible even when it is not, so the
test goes green on exactly the defect it exists to catch.

**Measured in THIS repository, three separate times, all in the image/inline-mixed-content
family this milestone touches:**

- `tests/test_translator.py` currently has **nine** image-related unit tests
  (`test_image_conversion`, `test_image_with_attributes`, `test_image_relative_path`,
  `test_image_path_adjustment_root/_nested/_deep_nested/_cross_directory/_same_directory/_subdirectory`,
  lines 1706–3918) — confirmed by grep at HEAD, **none** of them call `typst.compile()` or import
  `TYPST_AVAILABLE`; every other image-adjacent test file that does compile
  (`test_image_literal_escaping_gate.py`, `test_windows_image_uri_render_gate.py`) is a separate,
  newer file. These nine tests almost certainly still pass on the *unfixed* translator, because
  each constructs an image node as the sole/first content of its container — exactly the one shape
  PROJECT.md's binding constraint 2 says is unaffected. **Extending these nine tests is not a
  gate for this milestone's fix; a new real-compile fixture is.**
- v0.6.0's own retrospective lesson, stated in this project's own words: *"A green unit suite ≠
  correct rendered output ... GATE-01's `sphinx-build → typst.compile() → pypdf` methodology
  caught three additional latent fatals that no unit assert would have surfaced."*
  (`.planning/RETROSPECTIVE.md:101`).
- v0.6.5 (the *direct* precedent for this exact defect class — a missing separator before an
  inline code-mode call) was root-caused specifically because `visit_math` "participates" in three
  separator protocols in some containers and not others — the RETROSPECTIVE's own pattern name is
  *"When a bug appears in some containers and not others, suspect protocol participation, not
  ordering"* (`.planning/RETROSPECTIVE.md:326`). `visit_image()` today participates in **none** of
  the three protocols (`_add_paragraph_separator()`, the `list_item_needs_separator` check, and the
  five-site code-mode-concat check) — confirmed by reading `typsphinx/translator.py:4718-4772` and
  cross-referencing the other visitors that do call `list_item_needs_separator`
  (`translator.py:927, 1023, 1777, 1837, 1878, 1921`, etc.). This is the *identical* structural gap
  v0.6.5 fixed for math, now recurring for images.

**Measured directly (this research), not assumed:** a bare missing separator between two adjacent
code-mode calls reproduces the exact error PROJECT.md quotes. Compiled in a scratch directory with
the project's own `typst` package:

```
$ cat unseparated.typ
#{
par({text("Inline substitution ")image("test.png")
})
}
$ uv run python -c "import typst; typst.compile('unseparated.typ')"
FAILED: expected semicolon or line break
```

**How it would manifest in this milestone specifically:** an executor implements the
`visit_image()` fix, runs the existing suite (including the nine string-level tests above), sees
"all green," and reports done — without ever having proven the *new* fixture fails on the unfixed
tree or passes a real Typst parse of the four failing shapes PROJECT.md names (substitution image
mid-sentence, two images in a row, image inside a list item, image preceded by sibling content).

**Prevention:** the phase's acceptance gate MUST include at minimum one test that calls
`sphinx-build -b typstpdf` (or `typst.compile()` directly on the emitted `.typ`) for each of the
four failing shapes and the two passing shapes (image first in paragraph, image inside
`.. figure::`) named in PROJECT.md's Target Features. A test that only inspects `self.body` or
`node["uri"]` does not count as having exercised this defect, however many assertions it contains.

**Phase to address:** the phase implementing the `visit_image()` separator fix. Observable proof:
the new test module's own file explicitly invokes `typst.compile()` (or `sphinx-build -b
typstpdf`) — `grep -c 'typst.compile\|TYPST_AVAILABLE' <new_test_file>` returns > 0.

---

### Pitfall 2: A gate that is never proven RED against the unfixed tree is tautological

**What goes wrong:** A fixture is written *after* the fix already exists in the working tree, so it
is only ever observed passing. It may be vacuously true (e.g., it would also pass against a
correctly-behaving translator with different content), and nobody would notice until the next
regression.

**This project has already built, and repeatedly proved, the antidote — and this milestone should
reuse it verbatim, not reinvent it:**

- Phase 59 (v0.9.1) explicitly names this failure mode in its own success-criteria language:
  *"a call-site-routed gate would be tautologically green before and after the fix and prove
  nothing"* (`59-01-SUMMARY.md:35`), and structured its RED-proof by reconstructing the pre-fix tree
  file-by-file: `git checkout $PHASE_BASE_SHA -- typsphinx/{builder,translator}.py`, running the new
  test, confirming the *exact* Typst error string, then `git status --porcelain` confirming the
  restore was byte-identical (`59-VERIFICATION.md:34`).
- Phase 58 did the same for a test-side-only rewrite: *"proved the rewrite is neither a regression
  nor a tautology via a real, recorded RED against a temporarily-edited `typsphinx/builder.py`"*
  (`58-01-SUMMARY.md:91`).
- PROJECT.md's own binding constraint 1 for the *prior* Windows-path milestone states the general
  rule this milestone inherits: *"the acceptance bar is therefore only meaningful in its RED-first
  form: each gate must FAIL against the unfixed tree before its fix lands."*

**How it would manifest in this milestone specifically:** the new `visit_image()` separator test is
written and passes on the fixed tree, but is never actually run against a `git show
$PHASE_BASE_SHA:typsphinx/translator.py`-restored copy, so nobody can show it would have caught the
*current, live* bug (PROJECT.md's binding constraint 1 gives the exact reproduction: a document
containing `Inline substitution |sub| in a sentence.` emits `par({text("Inline substitution
")image("img.png")` and `typst.compile()` answers `expected semicolon or line break`).

**Prevention:** before closing the phase, restore `typsphinx/translator.py` to the phase's base SHA
(recorded at phase start, exactly as `61-CLOSEOUT-GUARD.md` records `PHASE_BASE_SHA` for
`REQUIREMENTS.md`), re-run the new gate, capture the verbatim `TypstError` string, then restore the
fix and confirm `git status --porcelain` is empty. This is not new process — it is the exact
choreography Phase 59 already executed and recorded in `59-WINDOWS-URI-EVIDENCE.md`.

**Phase to address:** same phase as Pitfall 1. Observable proof: a `*-EVIDENCE.md` (or
`*-VERIFICATION.md`) file quoting the verbatim pre-fix pytest traceback / Typst error string,
followed by a `git status --porcelain` empty-output block proving the restore.

---

### Pitfall 3: Fixing a test instead of proving byte-identical output

**What goes wrong:** When a fix changes emitted output, it is tempting to update whichever
pre-existing test now fails, rather than proving the change is additive (new separators appear only
where the bug lived) and that unaffected shapes are byte-identical to before.

**This is this project's single most-repeated positive pattern, stated explicitly across at least
five milestones — meaning its absence would be conspicuous and should raise suspicion, not be
treated as routine cleanup:**

- v0.6.2: *"the fix is +45 lines with no new helper... non-regression came out clean on a
  set-comparison against the pre-fix baseline (NEW-failures empty)"* — wait, that is v0.6.5's exact
  wording (`.planning/RETROSPECTIVE.md:314`); v0.6.2 independently established *"Prove fixtures have
  teeth by reverting in place"* as a named pattern (`RETROSPECTIVE.md:203`).
  v0.9.1's own product work: *"POSIX output was proven byte-identical the way v0.9.0 proved it — by
  zero pre-existing test edits, measured rather than asserted"* (PROJECT.md, v0.9.1 section).
- v0.9.0: *"the registry is additive... proven against a pre-change SHA-256/page-count baseline
  captured before any code was written"* (`RETROSPECTIVE.md` v0.9.0 entry / `.planning/PROJECT.md`
  Key Lesson 22).

**How it would manifest in this milestone specifically:** if the `visit_image()` fix's separator
logic is slightly too aggressive (fires even when a leading separator already exists — e.g. an
image that is genuinely first in its paragraph), one or more of the nine existing string-level image
tests (Pitfall 1) would start failing because an extra blank line/newline now appears in
`translator.body`. The failure mode to avoid is quietly editing the expected string in those nine
tests to match the new (buggy, over-aggressive) output — because they are string-level tests, they
cannot tell the difference between "this separator was needed" and "this separator is a harmless
but incorrect insertion."

**Prevention:** run the full pre-existing suite against the fix; if any pre-existing test's
*expected string* must change, treat that as a signal requiring justification (is the old expected
output still correct, or did the assertion need to change because the separator now appears where
it did not before, in a spot that changes visible behavior?) — not as routine test maintenance. The
project's own standard is **zero edits to pre-existing tests** for this class of fix (matches
PROJECT.md binding constraint 2: "Exactly one unseparated juxtaposition was found... So this
milestone fixes one emitter; it does not audit a family" — a correctly-scoped fix should not need to
touch tests for footnote/math/download, which already emit a leading `\n`).

**Phase to address:** same phase. Observable proof: `git diff --stat` scoped to `tests/` shows only
*new* test files, or an explicit, reviewed justification for any line changed in a pre-existing test
file.

---

### Pitfall 4: `ruff` is unrunnable in a freshly `uv sync`ed worktree on this machine — lint failures surface only in CI

**What goes wrong:** An executor runs `black --check .` and `mypy typsphinx/` locally, sees them
pass, and reports "lint clean" without ever running `ruff check .` — because it silently fails with
a NixOS stub-loader rejection, not a lint finding, and can be mistaken for "not installed" or
skipped.

**Measured live, in this exact worktree provisioning shape, moments before writing this file:**
`.planning/todos/pending/2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos.md` records the
failure reproducing as recently as 2026-08-22 inside a **freshly `uv sync --extra dev`-provisioned
worktree venv** — the exact provisioning CLAUDE.md mandates for every executor in this project's
standing worktree-isolated execution mode:

```
$ uv run ruff check .
Could not start dynamically linked executable: ruff
NixOS cannot run dynamically linked executables intended for generic
linux environments out of the box.
EXIT CODE: 127
```

The todo explicitly records this is **not a one-time fluke**: it disappeared for one session
(2026-08-16, in a different, not-freshly-provisioned `.venv`) and then reproduced again a week later
in a fresh worktree venv — "the condition flips with the environment... not with any change to this
repository's own tree." CI is unaffected (GitHub's Linux runners have a working `ruff`, confirmed
green at every dispatch).

**Compounding hazard, also measured in this project's history:** the post-merge gate that watches
wave completion in this project's tooling runs `pytest` only — not `black`/`ruff`/`mypy` — so a
wave can merge with a lint-breaking file present as long as pytest is green
(`.claude/…` — recorded as Phase 54.1's real incident in user memory: a new test file broke
`black --check .` and passed pytest-only gates for a full wave before a different executor's
out-of-scope full-repo lint run caught it).

**How it would manifest in this milestone specifically:** the `visit_image()` fix (or the release-
prep phase's CHANGELOG/version edits) introduces an import-order (`I001`) or unused-import
finding that only `ruff` would catch; the executor's local `black --check .` / `mypy` pass green,
`ruff` silently 127s, and the finding is never seen until `release.yml`'s `validate` job runs
`uv run ruff check .` on the real tag push — by which point `build`/`publish-pypi` have not yet run
(ruff is in `validate`, which gates `build`), so the failure is caught before publish, but costs a
failed CI run and a re-tag cycle.

**Prevention:** do not treat local `black`+`mypy` green as "lint clean." Either (a) run
`nix run nixpkgs#ruff -- check .` (confirmed working in this sandbox as of 2026-08-16, per this
project's own recorded workaround) before considering a wave/phase lint-clean, or (b) dispatch
`gh workflow run ci.yml --ref <branch>` explicitly before the release-prep phase closes, and treat
that as the lint authority — CLAUDE.md and this project's memory both already say CI, not the local
machine, is the lint authority here.

**Phase to address:** every phase touching `typsphinx/*.py`, but especially the release-prep phase
(it is the last chance before a real tag push exercises `release.yml`'s `validate` job, which is the
actual lint gate that matters). Observable proof: either a captured `nix run nixpkgs#ruff -- check .`
transcript ending "All checks passed!", or a linked CI run ID with the `Run linters` step green.

---

### Pitfall 5: Locale-dependent test failures that only appear in CI

**What goes wrong:** A test asserts against a Sphinx warning's localized *text* (not its
locale-invariant structural markers), passing on a Japanese-locale dev machine and failing on
CI's English-locale runner.

**Measured, this project, Phase 52 (v0.8.0):** *"`tests/test_state_guard_shapes_gate.py`... was
checking a Japanese-language baseline fragment via partial match; English-locale CI failed 2 cases,
taking down 6 lanes plus Code Coverage."* The fix that stuck was **not** translating the literal
(that just moves the dependency) but anchoring on Sphinx's locale-invariant `file:line: WARNING:`
prefix and `[toc.duplicate_entry]`-style diagnostic tag instead (`_locale_invariant_anchors()`).

**Quick local pre-check, proven cheap (seconds) by this project's own record:**
```bash
LC_ALL=C LANG=C LANGUAGE=C uv run python -m pytest tests/ -q
```

**How it would manifest in this milestone specifically:** if the new gate's assertion inspects any
Sphinx-emitted warning text produced along the way (e.g., a degrade-warning for an unresolvable
image path, or any build-log string), rather than the Typst compile error itself (which is not
Sphinx-localized — it comes from the `typst` Rust binary in English), this class could recur.
Lower risk here than in Phase 52's case because the primary assertion is a `typst.compile()`
success/failure, not a Sphinx warning string — but the release-prep phase's CI dispatch is exactly
where this class has surfaced before (v0.7.0: *"neither Windows CI nor a tag push had touched the
branch once"* across eight phases of green local runs).

**Prevention:** run the `LC_ALL=C` pre-check before any CI dispatch (near-zero cost), and dispatch
`gh workflow run ci.yml --ref <branch>` at least once mid-phase, not only at the release PR — per
this project's own recorded rule (*"push→observe terminal gates"*, v0.4.4; *"the milestone branch
was never pushed until the release PR, and both defects found at the close were invisible until
it was,"* v0.7.1).

**Phase to address:** the `visit_image()` fix phase (mid-phase CI dispatch) and the release-prep
phase (final dispatch before tagging). Observable proof: a linked CI run ID from a
`workflow_dispatch` triggered *before* the release PR, not only the PR's own automatic run.

---

### Pitfall 6: Windows-only failures invisible on a Linux-only local run

**What goes wrong:** A fix that touches path handling or string encoding passes every local test
(this sandbox is Linux/NixOS) but fails only on `windows-latest`, because of a Windows-specific
default (encoding, `ntpath` semantics, path separator).

**Measured, this project, twice, in exactly the path-handling code family v0.9.1/v0.9.2 both touch:**

- v0.7.1: *"three Phase 37 signature render-gate modules read `.typ` with a bare
  `Path.read_text()`, and Windows' cp1252 default cannot decode UTF-8"* — 820 passed / 1 failed on
  Windows only, invisible on Linux/macOS (`RETROSPECTIVE.md:369`).
- v0.9.1 itself (Phase 59): *"CPython 3.13's `ntpath.isabs()` change... the same commit, same OS,
  py3.12 passes and py3.13 fails"* — a version-lane-specific Windows defect, not even reproducible
  on all Windows lanes uniformly.

**This milestone's fix is a pure `translator.py` string-emission change** (not file I/O, not path
parsing), so its direct Windows exposure is lower than v0.9.1's own work — but the release-prep
phase's CHANGELOG/version files, and any test reading `.typ`/`.pdf` output with a bare
`open()`/`Path.read_text()` without an explicit `encoding="utf-8"`, carry the identical hazard
class.

**Prevention:** grep any new test file this phase adds for `Path.read_text()` or `open(` without an
explicit `encoding=` argument; and, per Pitfall 5, dispatch the 3-OS CI matrix
(`windows-latest` included) mid-phase, not only at the release PR — this is the acceptance bar
PROJECT.md's binding constraint 6 already states for the release-prep phase, but this milestone's
own fix phase should not wait that long to find out.

**Phase to address:** the `visit_image()` fix phase (any new test file: grep for missing
`encoding=`) and the release-prep phase (3-OS CI dispatch, both `windows-latest` lanes, before
tagging). Observable proof: linked CI run showing `Test Python 3.12 on windows-latest` and
`Test Python 3.13 on windows-latest` both green.

---

## Part 2 — The `in_figure` trap, measured directly

**Claim to verify:** a separator added to `visit_image()` without branch-awareness would inject a
newline inside a `figure(...)` function-call argument list. Does this break compilation, change
rendered output, or do nothing?

**Measured directly** (scratch directory, this project's own `typst` package, `uv run`):

```
$ cat control.typ
#figure(
  image("test.png",
  width: 40%),
  caption: [A caption]
)

$ cat injected.typ        # one extra blank line injected before "image(", inside figure(...)
#figure(

  image("test.png",
  width: 40%),
  caption: [A caption]
)

$ uv run python -c "
import typst
for name in ['control.typ', 'injected.typ']:
    pdf = typst.compile(name)
    print(name, '-> COMPILED OK, bytes:', len(pdf))
"
control.typ -> COMPILED OK, bytes: 7417
injected.typ -> COMPILED OK, bytes: 7417
```

**Result: neither a syntax error nor a silent layout change — a bare newline inside a
parenthesized Typst function-call argument list is pure insignificant whitespace.** Both files
compiled to byte-identical PDF sizes; Typst's parser treats a line break between tokens inside an
open `(...)` exactly like a space, because the expression is not yet syntactically complete (no
`;`/newline-as-terminator applies until the parenthesis closes). This is the same reason the
*missing*-separator defect (outside any parens, between two complete top-level expressions) fails
while the parenthesized case does not: Typst's "expected semicolon or line break" error fires only
between two syntactically *complete* adjacent expressions at statement level, never inside an
unclosed argument list.

**Cross-check, the actual defect, reproduced for contrast:**

```
$ cat unseparated.typ
#{
par({text("Inline substitution ")image("test.png")
})
}
$ uv run python -c "import typst; typst.compile('unseparated.typ')"
FAILED: expected semicolon or line break
```

**What this means for the fix:** the `in_figure`-branch-unaware failure mode PROJECT.md warns
about is real as a *code-quality* concern (a branch-unaware fix would still be structurally wrong —
it would misplace the two-space indentation convention `visit_image()` otherwise maintains for
readability inside `figure(...)` bodies, and could break the *deliberate* invariant that in-figure
content is exempt from paragraph/list-item separator bookkeeping since figures manage their own
spacing via `depart_figure`) but it is **not** the mechanism by which a naive fix would cause a
compile failure. A naive unconditional `self.add_text("\n")` before every `image(` call would
compile *successfully* in the `in_figure` branch (cosmetic-only) and would very likely be the
*correct* half of the fix in the non-`in_figure` branch (since that is exactly where the real
defect lives). The actual risk of branch-unawareness is not a Typst syntax error inside `figure()`;
it is a maintainability/consistency regression — the "cosmetic" newline could still trip a
*string-level* regression test if one existed asserting the exact figure-body text (none currently
do, per Part 1 Pitfall 1's grep — the nine image tests are all non-figure shapes), or could
interact badly with a *future* whitespace-sensitive Typst construct this project does not currently
use.

**Gate that would catch a genuinely harmful branch-unaware mistake:** the real-`typst.compile()`
gate from Part 1, Pitfall 1 — specifically the "must keep passing" shape PROJECT.md names: *"an
image inside `.. figure::`"*. If a branch-unaware fix somehow did break figure compilation (e.g. by
emitting the separator *before* checking `in_figure` and routing it through a code path that
`add_text()` treats specially — not demonstrated here, but not excluded either), only a real
compile of a figure fixture would show it; a string-level assert on `figure_content` would not,
per Pitfall 1's general argument.

**Phase to address:** the `visit_image()` fix phase. Observable proof: the real-compile gate
includes a figure-fixture case (PROJECT.md already names this as a required "must keep passing"
shape) and it passes; additionally, a byte-count or `pypdf`-extracted-text comparison of the
figure fixture's output before/after the fix, proving zero change (cosmetic whitespace inside
`figure(...)` does not need to be *asserted absent* — it needs to be proven *harmless*, which a
compile-success + unchanged-rendered-output check both establish).

---

## Part 3 — Release pitfalls specific to this repository

### Pitfall 7: The release-requirement checkbox auto-flip (five-for-five, then one hold)

**Evidence, this repository, six consecutive release-prep closes, with citations:**

| Release-prep phase | Flip happened? | Source |
|---|---|---|
| v0.7.0 (Phase 41→42) | Yes — caught in Phase 41, `42-CLOSEOUT-GUARD.md` created as the first checksum baseline | `RETROSPECTIVE.md:361` |
| v0.7.1 (Phase 46) | Yes — REL-06 flipped, REL-04 todo auto-closed; "three-for-three" | `RETROSPECTIVE.md:415` |
| v0.8.0 (Phase 52) | Yes (implied by "four-for-four" at v0.8.0 close) | `RETROSPECTIVE.md:492` |
| v0.9.0 (Phase 57) | Yes — REL-08 flipped, `57-CLOSEOUT-GUARD.md` SHA-256 baseline caught + reverted by hand; "five-for-five" | `RETROSPECTIVE.md:522,544` |
| v0.9.1 (Phase 61) | **No — held for the first time** | `61-CLOSEOUT-GUARD.md`; `.planning/milestones/v0.9.1-MILESTONE-AUDIT.md` Release fence table |

**The exact guard procedure that worked (reusable verbatim), read from `61-CLOSEOUT-GUARD.md`:**

1. **At phase head, before any plan runs:** record `sha256sum .planning/REQUIREMENTS.md`,
   `wc -l .planning/REQUIREMENTS.md`, and `git rev-parse HEAD` (the `PHASE_BASE_SHA`) in a
   dedicated `<phase>-CLOSEOUT-GUARD.md` file. Quote the exact lines under guard verbatim
   (the requirement's checkbox line, its Traceability-table row, and any phase-totals line that
   mentions it) via `grep -n '<REQ-ID>' .planning/REQUIREMENTS.md`.
2. **At phase close, before `phase.complete`-family tooling runs:** re-run the same three commands
   and confirm MATCH against the baseline.
3. **After `phase.complete`-family tooling has run — this is the step that actually catches the
   flip, because it runs OUTSIDE any plan's reach, at precisely the moment the flip has
   historically landed:** re-run `sha256sum`, `git diff --name-only -- .planning/REQUIREMENTS.md`,
   and the `grep -n` again. If the digest moved or the diff shows the checkbox/Traceability-row
   touched, **revert by hand** (`git checkout -- .planning/REQUIREMENTS.md`) and report it —
   *never* accept or commit the flipped state.
4. Reproduce the "for the operator running phase.complete" section verbatim into the phase's
   `HANDOFF.md`, so whoever runs the close step (which may not be the plan author) reaches the
   procedure without having to know this file exists.

**A second, subtler hazard the v0.9.1 audit itself flagged and this milestone inherits:**
`61-VERIFICATION.md`/the milestone audit found that **three of Phase 61's four plans** declared
`requirements-completed: [REL-09]` in their `SUMMARY.md` frontmatter, contradicting the correctly
unmet checkbox — only one plan (`61-02`) got it right, with an inline comment naming the decision.
**A downstream tool that trusts SUMMARY frontmatter rather than `REQUIREMENTS.md` itself would
still flip the wrong thing even with the checksum guard on `REQUIREMENTS.md` holding.** For v0.9.2
this risk is *structurally different but not absent*: the release-prep phase's requirement
(inherited REL-09, or its renumbered ID) is genuinely meant to become `[x]` — but only *after* the
actual PyPI publish/tag at `/gsd-complete-milestone`, not during the prep-only phase itself. Every
plan's `SUMMARY.md` in the prep-only phase must declare `requirements-completed: []` for that
requirement (matching the one correct v0.9.1 example, `61-02-SUMMARY.md`), and the checksum-guard
procedure above must be run once more.

**Phase to address:** the v0.9.2 release-prep phase. Observable proof: a
`<phase>-CLOSEOUT-GUARD.md` file with a baseline SHA-256 recorded at phase head, a re-verification
section recorded at phase close showing `MATCH`, and every plan's `SUMMARY.md` frontmatter in that
phase declaring `requirements-completed: []` for the release requirement (grep confirms no
plan claims it early).

---

### Pitfall 8: `release.yml`'s `uv: command not found` — confirmed fixed, but the workflow has other real exposure

**Read at HEAD (`.github/workflows/release.yml`):** the `create-release` job now has explicit
`Install uv` (`astral-sh/setup-uv@v7`) and `Set up Python` (`uv python install 3.12`) steps before
its `Generate release notes` step, with an inline comment naming the exact prior failure: *"Omitting
these two steps is exactly what failed the first real v0.7.0 tag push (`uv: command not found`, run
30848860064)."* This is **confirmed fixed** — not merely present in the file, but observed running
green at two subsequent real tag pushes: v0.8.0 and v0.9.0, per `RETROSPECTIVE.md`/`PROJECT.md`
(*"the release ran `validate` → `build` → `publish-pypi` → `create-release` all `success`... the
job that failed at the v0.7.0 close"*). No action needed here for v0.9.2 beyond the standing rule
(binding constraint 6): a real tag push still exercises the whole chain, so treat any failure as a
release-prep-phase concern, not a deferred one.

**What else in this workflow could genuinely fail on a real v0.9.2 tag push, read at HEAD:**

1. **The `pypi` environment likely requires manual approval** (GitHub Environment protection
   rule) before `publish-pypi` runs — confirmed by PROJECT.md's own language for v0.9.0: *"published
   by release run `32560457509` after owner approval of the `pypi` environment."* This is an
   expected manual gate, not a failure — but an operator who does not know to expect it may
   mistake a pending run for a stuck/broken one.
2. **`Verify CHANGELOG has a section for this version` (validate job) requires `## [0.9.2]` to
   exist in `CHANGELOG.md` *before* the tag is pushed** — read at HEAD, `CHANGELOG.md`'s only
   version heading below `## [Unreleased]` is `## [0.9.0]`; there is currently no `## [0.9.2]`
   section. This is release-prep's job to create, and `scripts/extract_changelog_section.py`'s
   algorithm is purely positional (matches the literal string after `## [`), so it does not care
   that `0.9.1` is skipped — it will find `## [0.9.2]` correctly as long as that exact heading
   exists, with no dependency on there having been a `## [0.9.1]` heading at any point.
3. **`generate_release_notes: true` stays enabled alongside the curated `body_path`** (by design,
   D-08 from Phase 41 — confirmed unchanged at HEAD) — GitHub's auto-generated "What's Changed"
   section is *appended after* the curated CHANGELOG body, not instead of it. **Live-tested against
   this repository's real GitHub API** (read-only, no release created):
   ```
   $ gh api repos/YuSabo90002/typsphinx/releases/generate-notes \
       -f tag_name=v-scratch-test -f previous_tag_name=v0.9.0 --jq '.body'
   ## What's Changed
   * merge: v0.9.1 — Windows path correctness (Phases 58-61, not released) by @YuSabo90002 in https://github.com/YuSabo90002/typsphinx/pull/135

   **Full Changelog**: https://github.com/YuSabo90002/typsphinx/compare/v0.9.0...v-scratch-test
   ```
   Because v0.9.1's ~155 commits (142 of them `.planning/`-only) were merged as a **single** PR
   (#135), GitHub's auto-notes list **one line per merged PR**, not one line per commit — the
   `.planning/` noise does not leak into this section. The v0.9.2 real release will additionally
   list whatever PR(s) close the inline-image fix and release-prep phases, so this section will be
   2-3 lines instead of the "1 PR line + compare link" shape measured at v0.6.4 — still compact, not
   a commit dump, but worth a human glance before/after publish since the comparison window now
   spans two milestones' worth of history (v0.9.0 → v0.9.2, no v0.9.1 tag to anchor an intermediate
   comparison).
4. **`uv sync --extra dev --locked` in the `validate` and `build` jobs will hard-fail if `uv.lock`
   is not regenerated in the same commit as the `pyproject.toml` version bump** — see Pitfall 10
   below; this is the single highest-probability failure point for the actual v0.9.2 tag push,
   because it is exactly the failure class already live and unresolved for dependabot PRs in this
   repository today.

**Phase to address:** the release-prep phase for items 2–4 (all release-prep's own responsibility);
item 1 needs no phase action, only operator awareness recorded in the phase's handoff notes.
Observable proof: a real `workflow_dispatch` of `release.yml` (or the real tag push itself) with all
five jobs (`validate`, `build`, `publish-pypi`, `create-release`, and the conditional
`publish-testpypi` correctly skipped) showing `success`/`skipped` as appropriate — not "the workflow
file looks correct."

---

### Pitfall 9: The 0.9.0 → 0.9.2 version skip

**Enumerated per the question's named surfaces, each checked at HEAD:**

- **`scripts/extract_changelog_section.py`** — confirmed safe by design. Its docstring explicitly
  documents the algorithm is *purely positional*, matching only the literal requested version
  string with no dependency on adjacency to any other version heading. `## [0.9.1]` never having
  existed is a complete non-issue for this script.
- **The CHANGELOG tail compare-link block** (read at HEAD, `CHANGELOG.md` tail): currently reads
  `[0.9.0]: .../releases/tag/v0.9.0` followed by `[Unreleased]: .../compare/v0.9.0...HEAD` with no
  `[0.9.1]` line ever added (correct — v0.9.1 was never released, so it should never get a link
  line). Release-prep must add `[0.9.2]: .../releases/tag/v0.9.2` and roll the `[Unreleased]:
  compare` line forward to `.../compare/v0.9.2...HEAD` — **skipping 0.9.1 in this chain is
  correct, not a defect**; the risk is only in forgetting the mechanical roll for 0.9.2 itself,
  which is unrelated to the skip. (Per project memory, this link-block edit is release-prep's job,
  same phase as the version bump — not a separate concern.)
- **`README.md`** — read at HEAD: line 347 reads `**Status**: Stable (v0.9.0) - Production ready`.
  A dedicated gate already exists for exactly this drift class:
  `tests/test_readme_version_sync.py::test_readme_status_version_matches_pyproject` parses both
  files independently and asserts equality — **and this gate's own docstring records that README's
  Status line previously drifted stale through two entire releases (v0.6.0 and v0.6.1) before it
  was added.** For v0.9.2, this test will fail loudly (not silently drift) if the version bump
  touches `pyproject.toml` without touching README.md in the same change — this is a real,
  already-armed CI gate, not a new risk to design around, but it is the exact class that has bitten
  this project twice before, so it earns explicit mention in the release-prep checklist.
- **`uv.lock`** — read at HEAD: `uv.lock`'s own `[[package]] name = "typsphinx"` stanza carries a
  literal `version = "0.9.0"` (line 1467), independent of `pyproject.toml`'s `version` field. **This
  is the same defect class already live and blocking dependabot in this repository today**
  (`.planning/todos/pending/2026-08-16-dependabot-prs-die-on-uv-lock-locked-mismatch.md`): every
  `uv sync --extra dev --locked` step (11 occurrences across `ci.yml`, `docs.yml`, `release.yml`)
  refuses a stale lockfile with `error: The lockfile at 'uv.lock' needs to be updated, but
  '--locked' was provided`, and the failure is at the *install* step, before any test/lint/type
  check runs. **The version bump commit must regenerate `uv.lock` (`uv lock` or `uv sync` without
  `--locked`) in the same commit as the `pyproject.toml` edit, or the release-prep phase's own CI
  run — and the real tag push's `validate`/`build` jobs — fail immediately and uninformatively.**
  This is not hypothetical: it is the exact error signature already reproduced twice in this
  repository's dependabot PRs (#123, #128) at the time of the linked todo.
- **`typsphinx-doc-translations` pin/tag procedure** — confirmed via the public GitHub API
  (read-only): the translations repo's tags currently jump `v0.8.0 → v0.9.0` directly (no `v0.9.1`
  tag exists there either), consistent with v0.9.1 never publishing. The established, working
  procedure (used successfully for v0.9.0, "not by a hand-made clone-edit-push, for the second
  consecutive close") is to dispatch that repository's own `update-pin.yml` workflow after the
  v0.9.2 tag lands on `main` — it advances the submodule/pin reference and tags the translations
  repo itself. **This is a manual dispatch step, not automatic on the parent repo's tag push** — it
  must be an explicit item in the release-prep or complete-milestone checklist, not assumed to
  happen as a side effect of `release.yml`.

**Phase to address:** the release-prep phase owns the `pyproject.toml`/`uv.lock`/`README.md`/
`CHANGELOG.md` edits (one atomic commit); `/gsd-complete-milestone` or an explicit release-prep
step owns dispatching `typsphinx-doc-translations`'s `update-pin.yml` after the tag lands.
Observable proof: `git diff` of the version-bump commit touches all four of
`pyproject.toml`/`uv.lock`/`README.md`/`CHANGELOG.md` together (a commit touching only
`pyproject.toml` is the exact shape that currently breaks dependabot); a linked `update-pin.yml`
run ID on the translations repo with a resulting `v0.9.2` tag confirmed via
`gh api repos/YuSabo90002/typsphinx-doc-translations/tags`.

---

### Pitfall 10: `.planning/` commits inside the release PR — measured, and mostly benign

**Measured directly against PR #135 (v0.9.1's merge into `main`):**

```
$ gh pr view 135 --json additions,deletions,changedFiles
"additions": 31797  (dominated by .planning/ phase artifacts — 142 of 155 commits are
                      ".planning/"-only "docs(...)" commits)
```

**This is a code-review-hygiene cost, not a release-body leak.** As shown under Pitfall 8 item 3,
GitHub's auto-generated release notes list one line per *merged PR*, not per commit — since this
project merges each milestone as a single PR, the `.planning/` commit noise inside that PR's diff
does not surface in the GitHub Release body (which is sourced from the curated `CHANGELOG.md`
section, never from `git log`). **The actual cost is at review time**: a reviewer (human or
`code-review`/`gsd-code-review` tooling) working through PR #135's ~31.8k additions has to
distinguish the handful of files that matter (`typsphinx/*.py`, `tests/*.py`,
`.github/workflows/*`) from the much larger `.planning/` volume. This project has a purpose-built
tool for exactly this (`gsd-pr-branch`: "Create a clean PR branch by filtering out `.planning/`
commits — ready for code review") that was **not** used for PR #135 — confirmed by the additions
count above, which is consistent with `.planning/` being included wholesale.

**How it would manifest in this milestone specifically:** the v0.9.2 PR will similarly carry every
`.planning/` commit from phases 62+ (the fix, plus release-prep) mixed with the actual
`translator.py` diff, making a manual or automated code-review pass slower and more error-prone at
finding the one load-bearing hunk (the `visit_image()` separator logic) — a phase where getting the
separator wrong in a subtle way (Part 2) is exactly the kind of thing a rushed review would miss in
a 30k-line diff.

**Prevention:** either invoke `gsd-pr-branch` before requesting review on the v0.9.2 PR (filtering
`.planning/` out of the review-facing diff, matching what this repo already has a skill for but has
not yet used), or explicitly scope any code-review pass with `--files typsphinx/translator.py
tests/<new-gate-file>` rather than reviewing the full PR diff — mirroring the project's own recorded
lesson about `gsd-code-review`'s scope-detection dropping root-level files unless named explicitly
(user memory: `gsd-code-review` extraction only follows paths containing `/`).

**Phase to address:** whichever phase opens the PR for review (likely the fix phase or release-prep).
Observable proof: either a `gsd-pr-branch`-filtered branch/PR exists, or the code-review invocation's
recorded command explicitly lists the product files reviewed (not "reviewed the PR").

---

### Pitfall 11: RTD / translations-repo steps that must follow a publish

**Confirmed sequence from this project's own v0.9.0 close** (`PROJECT.md`, "Prior state, retained
for reference"), reusable verbatim for v0.9.2:

1. Tag push (`v0.9.2`) triggers `release.yml`, publishing to PyPI and creating the GitHub Release.
2. Dispatch `typsphinx-doc-translations`'s own `update-pin.yml` (NOT automatic — a manual/explicit
   dispatch step) — this advances its pin to the new `main` merge commit and tags that repository
   `v0.9.2` itself.
3. Verify Read the Docs `en` `stable` resolves from the new tag and reports `0.9.2` (public API,
   no auth needed — per this project's own recorded fact that RTD's status/build/PDF/flyout APIs
   are curlable without authentication).
4. Verify `ja` `stable` advances only once step 2's translations-repo tag has landed (RTD's
   translation-project resolution follows the *translations repo's own* tags, not the parent's).
5. Confirm no RTD "Default Version" flip is needed on either project — this project's own record
   states this has been unnecessary for six consecutive closes running, so its *absence* is the
   expected, unremarkable outcome, not something requiring action.

**Phase to address:** `/gsd-complete-milestone` (matches the pattern used at every prior publish —
this is explicitly NOT release-prep's job, which stays prep-only per the established
prep/publish split). Observable proof: a linked `update-pin.yml` run ID plus a fresh (same-day)
curl of both RTD project's version-info endpoints showing `0.9.2`.

---

### Pitfall 12: The dependabot `uv.lock --locked` mismatch — does it block this release?

**No — but it is adjacent, not unrelated, and worth a one-line acknowledgment in release-prep.**
The open todo (`.planning/todos/pending/2026-08-16-dependabot-prs-die-on-uv-lock-locked-mismatch.md`)
describes dependabot's own PRs (bumping only `pyproject.toml`'s dependency versions) failing
`uv sync --extra dev --locked` in eleven CI steps. **This todo is explicitly scoped to
dependabot-authored PRs**, not to a maintainer-authored version-bump commit — a human/executor
bumping `pyproject.toml`'s `[project].version` field and remembering to run `uv lock` afterward does
not hit this defect (Pitfall 9 above covers that risk directly). The two are the *same underlying
mechanism* (manifest changed, lockfile not regenerated, `--locked` refuses to proceed) but different
triggers: this todo does not need to be resolved to ship v0.9.2, but its existence is the strongest
available evidence for why Pitfall 9's `uv.lock` regeneration step must not be skipped or assumed
automatic.

**Phase to address:** none required for v0.9.2 to ship (correctly out of scope, confirmed by
PROJECT.md's own "Not scoped into v0.9.2" list, which names this todo explicitly). Observable proof:
not applicable — this is a "confirmed non-blocking" finding, not a pitfall requiring a phase.

---

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification (observable artifact) |
|---|---|---|
| 1. String-only gate can't see parser defect | `visit_image()` fix phase | New test file greps positive for `typst.compile`/`TYPST_AVAILABLE`; the 9 pre-existing string-level image tests are left untouched |
| 2. Gate never proven RED | `visit_image()` fix phase | `*-EVIDENCE.md` quoting verbatim pre-fix Typst error + `git status --porcelain` empty after restore |
| 3. Editing tests instead of proving byte-identical | `visit_image()` fix phase | `git diff --stat -- tests/` shows only new files, or justified edits |
| 4. `ruff` unrunnable in fresh worktree | Every code-touching phase; release-prep especially | `nix run nixpkgs#ruff -- check .` transcript or a linked CI run's `Run linters` step |
| 5. Locale-dependent CI-only failures | `visit_image()` fix phase + release-prep | `LC_ALL=C` local pre-check + a mid-phase `workflow_dispatch` CI run ID |
| 6. Windows-only failures | `visit_image()` fix phase + release-prep | Grep new tests for missing `encoding=`; CI run showing both `windows-latest` lanes green |
| 7. Release-checkbox auto-flip | Release-prep phase | `<phase>-CLOSEOUT-GUARD.md` with SHA-256 baseline + post-close MATCH; every plan's SUMMARY frontmatter shows `requirements-completed: []` |
| 8. `release.yml` exposure beyond the fixed `uv: command not found` | Release-prep phase | Real `workflow_dispatch`/tag-push run with all jobs `success`/`skipped` as expected |
| 9. 0.9.0→0.9.2 version-skip surfaces | Release-prep phase | One commit touching `pyproject.toml` + `uv.lock` + `README.md` + `CHANGELOG.md` together; `test_readme_status_version_matches_pyproject` green |
| 10. `.planning/` noise in the release PR | PR-opening phase | `gsd-pr-branch`-filtered PR, or a review scoped explicitly to product files |
| 11. RTD/translations follow-up | `/gsd-complete-milestone` | `update-pin.yml` run ID + fresh RTD API curl showing `0.9.2` on both `en`/`ja` `stable` |
| 12. Dependabot `--locked` mismatch | None (confirmed non-blocking, carried forward) | N/A — already recorded as out of scope |

---

## "Looks Done But Isn't" Checklist

- [ ] **The `visit_image()` fix "passes all tests":** verify the passing tests include at least one
  real `typst.compile()` invocation per failing shape named in PROJECT.md — a green run of only the
  9 pre-existing string-level tests proves nothing new.
- [ ] **The new gate "is RED-first":** verify the RED observation was captured by actually
  restoring `typsphinx/translator.py` to its pre-fix state and re-running — not by reasoning that it
  "must have failed before."
- [ ] **The release requirement "is checked off":** verify by reading `.planning/REQUIREMENTS.md`
  directly, not by trusting a SUMMARY.md's `requirements-completed` frontmatter field.
- [ ] **"Lint is clean":** verify `ruff check .` actually executed (not 127'd) — a green `black
  --check .` and `mypy` alone do not establish this on this machine.
- [ ] **"CHANGELOG is ready":** verify the version-bump commit also touched `uv.lock` and
  `README.md`'s Status line in the same commit, not just `CHANGELOG.md` and `pyproject.toml`.
- [ ] **"The release is done" after the tag push:** verify `typsphinx-doc-translations`'s
  `update-pin.yml` was dispatched and its resulting tag exists — this does not happen automatically
  from the parent repo's tag push.

---

## Sources

- `.planning/PROJECT.md` (`## Current Milestone: v0.9.2`, v0.9.1/v0.9.0 sections, binding
  constraints) — read at HEAD.
- `.planning/RETROSPECTIVE.md` (v0.4.4 through v0.9.1 entries) — read at HEAD.
- `.planning/milestones/v0.9.1-MILESTONE-AUDIT.md` — read at HEAD.
- `.planning/milestones/v0.9.1-phases/58-*/58-01-SUMMARY.md`, `58-VERIFICATION.md`.
- `.planning/milestones/v0.9.1-phases/59-*/59-01-SUMMARY.md`, `59-VERIFICATION.md`,
  `59-WINDOWS-URI-EVIDENCE.md`.
- `.planning/milestones/v0.9.1-phases/60-*/60-02-EVIDENCE.md`, `60-PATH-QUOTING-EVIDENCE.md`.
- `.planning/milestones/v0.9.1-phases/61-*/61-CLOSEOUT-GUARD.md` — read in full at HEAD.
- `.planning/todos/pending/2026-08-16-dependabot-prs-die-on-uv-lock-locked-mismatch.md`.
- `.planning/todos/pending/2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos.md`.
- `typsphinx/translator.py:4718-4772` (`visit_image`/`depart_image`), and separator-protocol call
  sites at lines 927, 1023, 1777, 1837, 1878, 1914-1935 — read at HEAD.
- `tests/test_translator.py:1706-3918` (image test census) — read at HEAD.
- `.github/workflows/release.yml`, `.github/dependabot.yml` — read at HEAD.
- `scripts/extract_changelog_section.py` — read in full at HEAD.
- `CHANGELOG.md`, `README.md:347`, `pyproject.toml:7`, `uv.lock:1466-1468` — read at HEAD.
- `tests/test_readme_version_sync.py` — read in full at HEAD.
- Live, read-only measurements performed for this research: `typst.compile()` of
  control/injected/naive-injected/unseparated `.typ` fixtures in
  `/tmp/claude-1000/.../scratchpad/typst_probe/`; `gh api
  repos/YuSabo90002/typsphinx/releases/generate-notes` (scratch tag name, no release created);
  `gh api repos/YuSabo90002/typsphinx-doc-translations/tags`; `gh pr view 135 --json
  additions,deletions,changedFiles`; `git log --oneline v0.9.0..HEAD`.

---
*Pitfalls research for: typsphinx v0.9.2 milestone*
*Researched: 2026-08-30*
