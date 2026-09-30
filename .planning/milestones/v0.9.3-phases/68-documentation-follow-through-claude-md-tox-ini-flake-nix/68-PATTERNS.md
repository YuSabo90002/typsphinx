# Phase 68: Documentation Follow-Through — Pattern Map

**Mapped:** 2026-09-12
**Files analyzed:** 6 (5 edited in place + 1 new evidence-file family)
**Analogs found:** 6 / 6

This phase is prose-only (Nix `#` comments, Markdown, a tox `.ini` comment block, two pytest
docstrings/messages, plus new phase evidence markdown). There is no application code to pattern-
match against controllers/services/etc. The "analogs" here are: (a) the exact current text at each
edit site — already fully quoted verbatim in RESEARCH.md's "Current Text Inventory" section, which
this file treats as the authoritative excerpt source rather than re-reading the same ranges — and
(b) prior-phase evidence/`AMENDED`-block markdown that establishes this project's conventions for
recording verbatim transcripts and revision history in prose.

## File Classification

| File to Edit | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `CLAUDE.md` (`:11`, `:77`, new subsection, `### Worktree-isolated execution` boundary paragraph) | config/docs (prose, session-loaded instructions) | transform (stale-fact rewrite) | `CLAUDE.md`'s own existing "Worktree-isolated execution" section (`:80-96`) | exact — same file, same section style |
| `tox.ini` (`:4-10` comment block only) | config (comment beside a parsed key) | transform | `tox.ini:19-32` (`package = editable` comment) | exact — same file, same "history + current-state" comment idiom |
| `flake.nix` (`#` comments only: `:26-31`, `:37-42`, `:63-66`, `:74-75`, `:92-97`, plus a new header block above `outputs`) | config/utility (Nix flake, devShell/FHS wrapper) | transform | `flake.nix`'s own existing per-element comments (`:26-31` `fhsRun`, `:37-42` `venvWalk`, `:63-66` strict-shim note) | exact — same file, restate-in-place |
| `tests/test_toolchain_config_gate.py` (`:302-304` docstring, `:366-368` assertion message) | test | transform (text-only) | Same file's own untouched C1/C2 lines (e.g. `:41`, `:276`, `:297`) showing the "accurate historical framing" idiom to convert C3 lines into | exact |
| `tests/test_pdf_render_gate.py` (`:167` docstring, one added sentence) | test | transform (text-only) | Same docstring's own preceding sentence (`:160-167`) — historical-fact-plus-current-reasoning idiom | exact |
| New phase evidence file(s) `68-*-EVIDENCE.md` (D-15 grep classification, derivation-identity gate, green-tree gate) | docs (evidence transcript) | transform / batch (verbatim capture) | `.planning/phases/65-.../65-REVERT-EVIDENCE.md` and `.planning/phases/64-.../64-NIX05-WORKTREE-EVIDENCE.md` | exact |

## Pattern Assignments

### `CLAUDE.md` (docs, D-01..D-08)

**Analog:** `CLAUDE.md`'s own existing sections — no external file needed; this is a same-file
rewrite-in-place plus one new subsection inserted structurally.

**Site 1 — Overview sentence** (`CLAUDE.md:11`, current text, verbatim):
```
Development uses `uv` for env/dependency management and `tox` (with `tox-uv-bare`) as the task runner.
```
D-08 target form: `tox` (with `tox-uv`) — no other wording in this sentence changes.

**Site 2 — Conventions bullet** (`CLAUDE.md:77`, current text, verbatim):
```
- `tox.ini` pins `tox-uv-bare~=1.35` (not `>=1.35,<2`) deliberately — see the comment in that file; tox's ini parser splits a single-line `requires` on commas and breaks otherwise. The `-bare` package is also deliberate (QUA-04, Phase 45.2): the plain `tox-uv` meta package bundles a PyPI `uv` wheel whose generic-linux ELF cannot exec on NixOS, and `uv.find_uv_bin()` searches `.venv/bin` first and reads no environment variable. Do not "simplify" it back to `tox-uv`.
```
D-08 requires: keep the ini-parser explanation (comma-splitting hazard, `~=1.35` as the comma-free
equivalent); replace the `-bare`/QUA-04 rationale with a short note that the earlier `tox-uv-bare`
pin was needed only because the bundled `uv` could not exec on NixOS, which the FHS shims (Phase 64)
now handle; delete the closing "Do not simplify it back to `tox-uv`" sentence — it now points the
wrong way.

**Insertion point pattern — new subsection before `### Worktree-isolated execution`**
(`CLAUDE.md:80-96`, current text, verbatim — this is the section whose recipe D-01/D-03 require
stay byte-identical):
```
### Worktree-isolated execution

**Detection rule:** you are running inside an isolated git worktree when `.git` is a FILE (a `gitdir:` pointer), not a directory — check with `test -f .git`. Sequential main-tree execution has `.git` as a directory and needs none of the steps below.

When operating inside a worktree, provision the worktree's own environment before running anything:

    env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev
    uv run pytest   # run ALL subsequent commands via `uv run`

1. **Provision first.** `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` unsets those two vars so `uv` creates a fresh worktree-local `.venv` instead of syncing into an already-activated main venv and re-pointing it at the worktree.
2. **Run everything via `uv run`.** e.g. `uv run pytest …`. Inside the test fixtures, Sphinx is still invoked as `sys.executable -m sphinx`, which under `uv run` resolves to the worktree venv's python — so `import typsphinx` binds to the worktree's editable copy. This complements the existing NixOS `sys.executable -m sphinx` guidance and does not contradict it.

**Rationale:** the main `.venv` holds a PEP-660 editable finder (`__editable__.typsphinx-*.pth`) that resolves `import typsphinx` to the MAIN checkout's absolute path (`/…/typsphinx/typsphinx`), and `.venv` is gitignored so a fresh worktree starts with no venv of its own. Without the per-worktree `uv sync` + `uv run`, a worktree executor edits files in the worktree but pytest imports the UNCHANGED main-tree package — gates stay RED after a correct fix, and later waves don't see earlier waves' changes. Verified 2026-07-20 that a worktree `uv sync` + `uv run` is isolated (main `.venv` untouched) and works under the NixOS sandbox.

**Applicability — worktree isolation is the STANDING execution mode (project owner's decision, 2026-07-20).** ...
```
The new `###` subsection (D-04, name at discretion) goes between `## Conventions & gotchas`'s last
untouched bullet (line 78) and this heading. **Do not touch the `## Conventions & gotchas` heading
text itself** (line 73) — `tests/test_toolchain_config_gate.py:164` cites it by exact string. This
section's own recipe lines (the `env -u …` line and `uv run pytest` line) must remain
byte-identical; only a new boundary paragraph is added pointing at the new subsection, per D-01.

**Style precedent for a heading + bulleted-facts + bold-lead-in structure:** reuse the pattern
already visible above — `**Bold label.** sentence.` for enumerated facts, a `**Rationale:**`
paragraph for the "why", and a `**<Name> — <qualifier>.**` paragraph for standing-policy statements.
Model the new subsection's internal structure the same way (e.g. `**What the shims are.**`,
`**Prerequisite.**`, `**No manual step.**`, `**Locale.**`, `**Interpreters may differ.**`, then a
pointer sentence to `flake.nix`).

### `tox.ini` (config comment, D-16)

**Analog:** `tox.ini:19-32`'s own `package = editable` comment block — same file, same idiom
("current setting stated explicitly, historical context, why-safe-now, evidence citation").

**Current text to replace** (`tox.ini:1-11`, verbatim; only lines 4-10 are in scope, `requires =`
on line 11 is untouched):
```
[tox]
env_list = py312, py313, lint, type, cov, docs
isolated_build = True
# tox-uv-bare pinned via ~= (not >=1.35,<2): tox's own ini-list loader splits
# single-line `requires` values on "," (only multi-*entry* lists preserve
# newline-splitting), so a literal ">=1.35,<2" is parsed as two bogus
# requirements ("tox-uv-bare>=1.35" and "<2") and tox fails to even start.
# ~=1.35 is the packaging-spec equivalent of >=1.35,<2 (see D-07) with no
# comma, sidestepping the parser bug. Verified equivalent via
# `packaging.specifiers.SpecifierSet` in 04-01-SUMMARY.md.
requires = tox-uv~=1.35
```

**Analog idiom to copy** (`tox.ini:19-32`, verbatim — note the structure: state the current setting
plainly, give historical contrast, state why it's safe/expected now, cite evidence by
archive-stable name):
```
# package = editable (uv-venv-lock-runner's own default, stated explicitly here
# rather than left implicit): a non-editable `package = wheel` build was the
# prior setting here, and 45.2-05's CI dispatch (SC#4) proved it silently
# dropped `typsphinx/templates/base.typ` from the installed package under
# CI's uv (0.12.3), though not under this machine's (0.11.25) -- 23 pytest
# failures across py312/py313/cov, all `FileNotFoundError: Default template
# not found`. ...
# See 45.2-05-SUMMARY.md and
# 45.2-TOOLCHAIN-EVIDENCE.md Step 8 for the transcript.
package = editable
```
D-16's new block must follow this exact shape: keep the comma-splitting-parser explanation in full
(unchanged wording is fine — it is still true), replace the `-bare`/`D-07` citation with a
self-contained explanation ("the pin was briefly `tox-uv-bare` because the bundled `uv` could not
exec on NixOS outside FHS; on NixOS the FHS shims now run `tox`, so its bundled `uv` executes; CI
runners were never affected"), and cite evidence in an archive-stable form (do not reference
`.planning/phases/…` paths that move at milestone-complete; cite by milestone + phase + filename,
e.g. "v0.9.3 Phase 65, `65-REVERT-EVIDENCE.md`").

### `flake.nix` (Nix comments, D-09..D-12)

**Analog:** the file's own existing per-element comments, which already hold correct material to
restate in D-09's style (no `D-NN` IDs, no time-relative phrasing) rather than write fresh:

`flake.nix:26-31` (`fhsRun`, zlib reason — content is correct, keep, restate without any `D-NN`
label if the current text carries one):
```
          fhsRun = pkgs.buildFHSEnv {
            name = "typsphinx-fhs-run";
            # Pillow's `_imaging` extension carries a bare `NEEDED libz.so.1`, and
            # uv-managed CPython links zlib statically, so nothing in the process
            # ever maps it without this entry. See 64-LIBZ-FIX-EVIDENCE.md.
            targetPkgs = p: [ p.zlib ];
```
Citation form must change to archive-stable (D-09): e.g. "v0.9.3 Phase 64, `64-LIBZ-FIX-EVIDENCE.md`".

`flake.nix:37-42` (`venvWalk` description — content correct, keep):
```
          # Bounded upward walk from $PWD looking for .venv/bin/<tool>, stopping
          # at the first ancestor holding a .git entry (a file in a worktree, a
          # directory in the main checkout) or at /. This survives tox's own
          # `changedir = docs` (docs-html/docs-pdf) and never leaves the
          # checkout it started in, so a nested executor worktree can never
          # resolve the main checkout's .venv.
```

`flake.nix:63-66` (strict-shim exit-127 note — carries a `D-03` ID that D-09 says must be removed):
```
          # D-03: the six venv shims have no fallback. A missing
          # .venv/bin/<tool> is a hard, loud failure -- naming the tool and the
          # directory the walk started from, then exiting non-zero (127, the
          # shell's own command-not-found status).
```
Rewrite to drop the `D-03:` prefix; content otherwise correct.

`flake.nix:74-75` (names `D-01`/`D-02` — must be rewritten to prose with no IDs):
```
          # D-01: the full seven-name roster is these six strict venv shims
          # plus `uv` (uvShim below, D-02's sole documented exception).
```

`flake.nix:92-97` (`uvShim`, D-12's primary target — carries the stale "does not exist until Phase
65" phrasing that is now false since Phase 65 landed):
```
          # D-02: `uv` resolves in two legs. Leg 1 is the same bounded upward
          # walk for .venv/bin/uv (it does not exist until Phase 65's tox-uv
          # revert installs it). Leg 2, the on-stop fragment, is the fixed
          # nixpkgs store path -- fixed at flake-evaluation time and therefore
          # un-shadowable. Both legs enter the sandbox, which is what makes
          # `uv run <tool>` carry FHS into every downstream process.
```
Rewrite per D-12: describe both legs by role without version numbers or `D-NN` IDs or
time-relative phrasing; state plainly this is the file's only fallback/deliberate exception.

**New header block above `outputs`** (D-10) has no existing analog in this file (it doesn't exist
yet) — compose from the falsified-alternatives facts in `.planning/PROJECT.md` § "Binding
measurements taken during scoping (2026-09-02)" (cited by RESEARCH.md's canonical_refs) plus the
darwin-guard content in D-11, following the same "prose paragraph, then per-element note beside the
code it documents" layout the file already uses for its other four comments.

### `tests/test_toolchain_config_gate.py` (D-13)

**Analog:** the file's own untouched C1 lines (e.g. `:41`, `:276`, `:297` per RESEARCH.md's D-15
grep classification) — these already model the "accurate historical framing" this phase must
convert the two C3 blocks into.

**Docstring target** (`:302-304`, verbatim, self-referential and about to go stale):
```
    CLAUDE.md's own "Conventions & gotchas" sentence still names `tox-uv-bare` as
    deliberate -- that sentence goes stale as of this revert and is rewritten in
    Phase 68 (DOC-19/DOC-20), not here (D-06).
```

**Assertion message target** (`:358-369`, verbatim; only the final three lines `:366-368` change,
the `assert` on `:359` and message lines `:360-365` stay untouched):
```
    # G5 requirement 2 (Phase 65 revert): dev extra MUST NOT name tox-uv-bare directly.
    assert canonicalize_name("tox-uv-bare") not in dev_names, (
        "dev extra names 'tox-uv-bare' directly (on normalized distribution name) -- "
        "this is the stale Phase 45.2 workaround pin that Phase 65's revert (TOX-01) "
        "removes now that Phase 64's FHS shims dissolve the stub-ld defect (QUA-04) that "
        "motivated it. tox-uv-bare stays present only as tox-uv's own exact-version "
        "transitive dependency in uv.lock, which is expected and not what this assertion "
        "forbids -- it forbids the dev extra naming tox-uv-bare as a literal entry in "
        "pyproject.toml. See 65-REVERT-EVIDENCE.md for the lock regeneration proof "
        "(TOX-01, D-04) and CLAUDE.md 'Conventions & gotchas', which still names "
        "tox-uv-bare as deliberate until Phase 68 (DOC-19/DOC-20) rewrites it."
    )
```
Rewrite both `Phase 68 (DOC-19/DOC-20) rewrites it` self-references to past tense ("rewritten by
Phase 68") — no assertion logic, no compared names change.

### `tests/test_pdf_render_gate.py` (D-14)

**Analog:** the same docstring's own preceding sentences (`:150-166`) already model the
"historical fact, kept, plus current-reasoning" idiom this phase's one added sentence must match.

**Target** (`:150-171`, verbatim; `:167` is the sentence D-14 keeps, a new sentence is inserted
after it, before the unchanged `:168-171` closing reasoning):
```
    Invoked as `sys.executable -m sphinx` (the sphinx-build console entry
    point's module form) rather than shelling out to `uv run sphinx-build`:
    ...
    That cause was removed by QUA-04 (2026-08-10; `tox-uv` -> `tox-uv-bare` drops
    the bundled generic-linux `uv` wheel binary). `sys.executable -m sphinx`
    is kept regardless, because it depends on no PATH resolution at all --
    a better reason than the hazard ever was, and one that holds no matter
    what is installed in `.venv/bin`.
```
Insert one sentence after "bundled generic-linux `uv` wheel binary)." stating: the `tox-uv` revert
(Phase 65) put `.venv/bin/uv` back, and on NixOS it now runs through the Phase 64 FHS shims rather
than bare, so the QUA-04-era hazard no longer applies to a fresh `.venv/bin/uv` — but keep the
closing "`sys.executable -m sphinx` is kept regardless" sentence unchanged.

### New evidence file(s) `68-*-EVIDENCE.md` (D-15 grep, derivation-identity, green-tree gates)

**Analog:** `.planning/phases/65-tox-uv-bare-tox-uv-revert-on-the-uv-path-tox-actually-resolves/65-REVERT-EVIDENCE.md`
and `.planning/phases/64-fhs-wrapper-and-command-shims-in-flake-nix/64-NIX05-WORKTREE-EVIDENCE.md`.

**Structural idiom to copy** (`65-REVERT-EVIDENCE.md:1-28`, verbatim):
```
Measured shape: executor worktree, Phase 64 shims inherited from the session PATH; no nix develop, no direnv exec, never the main checkout.

## Head check

```
$ date -u +%FT%TZ
2026-09-12T07:29:47Z

$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a3ca8472e956ebe27

$ test -f .git; echo "exit:$?"
exit:0
...
```

Precondition met: the pre-revert pin is present and no `uv` lock block exists yet.
```
Pattern: one-line context sentence, then `##`-headed sections each opening with a fenced shell
transcript (command + literal output, no elision beyond `...` where genuinely long), followed by a
one-sentence plain-prose conclusion after each transcript block. Reuse this exact shape for:
- the D-15 grep-classification evidence (re-run `git grep -n tox-uv-bare -- ':!.planning'
  ':!uv.lock'` on the merged wave-1 tree; transcribe every hit; classify per the three buckets),
- the derivation-identity gate (four `nix eval --raw .#devShells.<system>.default.drvPath` calls
  before and after the `flake.nix` comment edit, asserting byte-identical drvPaths),
- the green-tree gate (`pytest --collect-only -q` before/after, `black --check .`, `ruff check .`).

No new script or new test file — Phase 64 D-05's established convention (cited directly by
CONTEXT.md's Claude's Discretion) is verbatim transcripts inside phase evidence markdown only.

## Shared Patterns

### Verbatim-transcript evidence convention
**Source:** `.planning/phases/64-fhs-wrapper-and-command-shims-in-flake-nix/64-NIX05-WORKTREE-EVIDENCE.md`,
`.planning/phases/65-tox-uv-bare-tox-uv-revert-on-the-uv-path-tox-actually-resolves/65-REVERT-EVIDENCE.md`
**Apply to:** every `68-*-EVIDENCE.md` file this phase produces (D-15 grep, derivation-identity,
green-tree gate).
One-line context, `##` section headers, fenced `$ command` / literal-output blocks, one-sentence
conclusion after each block.

### `AMENDED` block convention
**Source:** `.planning/ROADMAP.md` SC#1's existing `AMENDED 2026-09-12` block (already present per
RESEARCH.md, `.planning/ROADMAP.md:646-658` — no further ROADMAP edit needed this phase, only that
`CLAUDE.md`'s new text agree with it).
**Apply to:** none directly edited this phase (ROADMAP itself is out of the edit footprint beyond
what's already landed), but `CLAUDE.md`'s new boundary paragraph (D-01) must restate this block's
substance in its own words, and any phase evidence noting a correction should use the same
"append and keep the original text" idiom rather than deleting the superseded claim.

### Archive-stable citation convention (D-09)
**Source:** none of this phase's own text yet uses it correctly (existing `flake.nix:30`'s
`64-LIBZ-FIX-EVIDENCE.md` citation and `tox.ini:9`'s `04-01-SUMMARY.md` / `D-07` citation are the
stale form being replaced).
**Apply to:** every citation added or restated in `CLAUDE.md`, `tox.ini`, and `flake.nix` this
phase. Form: "v0.9.3 Phase NN, `NN-NAME-EVIDENCE.md`" or a path that does not move
(`.planning/PROJECT.md`) — never a bare `.planning/phases/…` path, because
`/gsd-complete-milestone` moves that directory to `.planning/milestones/v0.9.3-phases/`.

### "Historical fact kept, current-reasoning added" idiom
**Source:** `tests/test_pdf_render_gate.py:150-167` (existing docstring prose), `tox.ini:19-32`
(`package = editable` comment).
**Apply to:** `tox.ini`'s D-16 rewrite, `CLAUDE.md:77`'s D-08 rewrite, and
`tests/test_pdf_render_gate.py:167`'s D-14 addition — state the old fact as history (not deleted),
then state why the current state is correct/safe, without contradicting the historical claim.

## No Analog Found

None. Every edit site in this phase's footprint has a direct, same-file analog (the site's own
existing text, or a neighboring comment/docstring in the identical idiom), and the evidence-file
convention has two directly on-point prior instances (Phase 64, Phase 65).

## Metadata

**Analog search scope:** `CLAUDE.md`, `tox.ini`, `flake.nix`, `tests/test_toolchain_config_gate.py`,
`tests/test_pdf_render_gate.py`, `.planning/phases/64-fhs-wrapper-and-command-shims-in-flake-nix/`,
`.planning/phases/65-tox-uv-bare-tox-uv-revert-on-the-uv-path-tox-actually-resolves/`
**Files scanned:** 5 edit targets + 2 evidence-file analogs (read this session) + `68-CONTEXT.md`,
`68-RESEARCH.md` (required reading, already containing verbatim excerpts for every site)
**Pattern extraction date:** 2026-09-12
</content>
