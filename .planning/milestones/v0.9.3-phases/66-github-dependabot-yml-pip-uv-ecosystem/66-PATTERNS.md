# Phase 66: `.github/dependabot.yml` — `pip` → `uv` Ecosystem - Pattern Map

**Mapped:** 2026-09-12
**Files analyzed:** 2 (1 tracked-source edit, 1 phase-evidence artifact class)
**Analogs found:** 2 / 2

This phase has no application-code surface (config.md itself says "no unit/integration test
exercises it"). The two things to be created/modified are a one-line config edit and an
observation-recording evidence file. Both have close, recent, tracked analogs in Phase 65.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|--------------------|------|-----------|-----------------|---------------|
| `.github/dependabot.yml` | config | request-response (GitHub-platform config read, no runtime code path) | `.github/dependabot.yml` (self — in-place edit of the existing tracked file) | exact |
| `.planning/phases/66-.../66-*-EVIDENCE.md` (D-02 snapshots, D-04 acceptance read, D-05 leg-2 uv-version observation) | test (manual-observation evidence, not a pytest file) | event-driven (external SaaS reacting to a config push; recorded, not asserted in-repo) | `.planning/phases/65-.../65-CI-EVIDENCE.md` and `65-REVERT-EVIDENCE.md` | exact |
| `65-0N-PLAN.md`-style verify commands (`sed -n 's/^KEY = //p'`, `grep -c '^## '`) that a later plan/wave reads back | utility (verification script embedded in PLAN.md, not a source file) | transform (evidence text → gate boolean) | `65-01-PLAN.md` / `65-02-PLAN.md` wave-gate blocks (see excerpt below, same directory) | role-match |

## Pattern Assignments

### `.github/dependabot.yml` (config, request-response)

**Analog:** the file itself, current tracked content (read this session, byte-identical to
`origin/main`'s copy per `65-REVERT-EVIDENCE.md`-style byte-identity checks — see D-01's
`git diff origin/main <milestone-branch> -- .github/dependabot.yml` convention).

**Current full content** (verbatim, all 30 lines — the entire file, since the edit is a single
enum-value swap and every other line stays byte-identical):
```yaml
version: 2
updates:
  # Python dependencies (pyproject.toml)
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "00:00"
    open-pull-requests-limit: 5
    labels:
      - "dependencies"
      - "automated"
    groups:
      sphinx-typst-stack:
        patterns:
          - "sphinx*"
          - "docutils*"
          - "typst*"
        exclude-patterns:
          - "sphinx-autodoc-typehints"
          - "sphinx-intl"

  # GitHub Actions
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "monthly"
    open-pull-requests-limit: 3
    labels:
      - "ci"
      - "automated"
```

**The exact diff to apply** (RESEARCH.md "Code Examples" — already verified against the live
file this session):
```diff
--- a/.github/dependabot.yml
+++ b/.github/dependabot.yml
@@ -1,7 +1,7 @@
 version: 2
 updates:
   # Python dependencies (pyproject.toml)
-  - package-ecosystem: "pip"
+  - package-ecosystem: "uv"
     directory: "/"
     schedule:
       interval: "weekly"
```

**Core pattern — what must NOT change:** every key below `directory:` in the Python `updates[0]`
entry (schedule block, `open-pull-requests-limit: 5`, both `labels`, the whole
`groups.sphinx-typst-stack` block including both `patterns` and `exclude-patterns`), and the
entire second `updates[1]` (`github-actions`) entry, byte-for-byte. D-06 explicitly forbids adding
`versioning-strategy` or any other new key.

**Error handling:** N/A — this is a declarative YAML enum value with no in-repo validation path
(RESEARCH.md Security Domain: "closed enum GitHub itself validates on config parse"). Do not add a
schema check or test for this file; DEP-01/DEP-03/DEP-04 are all closed by external observation
(`gh pr view`), not by a local assertion.

**Validation:** the only "validation" this file's plan needs is the D-01 byte-identity check
between the `main`-bound PR branch and the milestone branch, run as plain `git diff`:
```bash
git diff origin/main origin/gsd/v0.9.3-toolchain-and-dependency-update-repair -- .github/dependabot.yml
# expect: empty (after both carry the same "uv" edit)
```

---

### Evidence files (`66-*-EVIDENCE.md`) (test/manual-observation, event-driven)

**Analog:** `.planning/phases/65-.../65-CI-EVIDENCE.md` and `65-REVERT-EVIDENCE.md` (both read in
full this session).

**Structural pattern to copy:**
1. Open with one prose line stating the measured shape/environment context (worktree vs. main
   checkout, what's inherited from prior phases), e.g.:
   ```
   Measured shape: executor worktree, Phase 64 shims inherited from the session PATH; no nix
   develop, no direnv exec, never the main checkout.
   ```
2. Declare `KEY = value` lines immediately under a fact once it's measured (e.g.
   `REVERT_SHA = d32eb5d…`, `PUSHED_SHA = d9c7555…`, `RUN_ID = 34681968010`), so a later plan's
   verify command can grep them back with `sed -n 's/^KEY = //p'`.
3. Use `## Section Heading` per measurement topic (`## Head check`, `## Dispatch`, `## Run`,
   `## Job census`, `## Requirement closure`), each followed by a fenced `$ command` / literal
   output block, quoted verbatim — never paraphrased.
4. Close with a `## Requirement closure` table:
   ```markdown
   | Requirement | Status | Deciding section |
   |---|---|---|
   | TOX-04 | MET | `## Run`, `## Job census`, ... |
   ```
5. When later evidence needs to reference earlier evidence in the same phase without re-deciding
   it, restate the row and cite the earlier file/section by name rather than re-running the
   observation:
   ```
   TOX-01, TOX-02 and TOX-03 are restated from `65-REVERT-EVIDENCE.md` § Requirement closure
   (not re-decided here): all three read MET, deciding sections ...
   ```
6. An orchestrator-side follow-up step (e.g. main-checkout re-sync) is appended as
   `## Addendum: <description> (orchestrator, D-0N)` rather than a new top-level file — see
   `65-REVERT-EVIDENCE.md`'s "Addendum: main-checkout re-sync" section for the exact shape.

**Applied to Phase 66:** name candidates consistent with this convention —
`66-MAIN-PR-EVIDENCE.md` (D-01 PR open/merge, byte-identity, 6-check green),
`66-DEPENDABOT-EVIDENCE.md` (D-02 pre/post #123/#128 snapshots, D-03 "Check for updates"
checkpoint outcome, D-04 real-`uv`-PR "same commit" proof, D-06 grouping/labels/limit
observation), and `66-UV-VERSION-EVIDENCE.md` or a `## D-05 leg 2` section inside one of the above
(the D-05 uv-version-compatibility observation on the real PR's head, mirroring
`65-REVERT-EVIDENCE.md`'s own `## D-05 uv before and after` section naming). Evidence-file naming
is explicitly Claude's Discretion per CONTEXT.md — these are suggestions consistent with Phase 65's
convention, not a locked requirement.

---

### Wave-gate verify commands (utility/transform, embedded in PLAN.md)

**Analog:** `65-REVERT-EVIDENCE.md`'s own "## Wave-1 gate" section, which is itself a copy of what
a consuming `65-0N-PLAN.md` verify block runs against the prior wave's evidence file:

```bash
$ sed -n 's/^REVERT_SHA = //p' 65-REVERT-EVIDENCE.md | head -n 1
d32eb5db6219bf4917ab820a44562ba479e5fe71

$ git merge-base --is-ancestor d32eb5db6219bf4917ab820a44562ba479e5fe71 HEAD; echo "exit:$?"
exit:0

$ grep -c '^## DIVERGENT' 65-REVERT-EVIDENCE.md
0
```

**Applied to Phase 66:** any plan wave that depends on an earlier wave's recorded PR number, SHA,
or run ID should read it back the same way — `sed -n 's/^KEY = //p' <evidence-file>` — rather than
re-deriving it, and should grep for a `## DIVERGENT` / `## HALT` marker heading (if the plan defines
one, per D-05's "record it and HALT for the owner" failure branch) before treating a prior wave as
clean.

---

## Shared Patterns

### `checkpoint:decision` / `checkpoint:human-action` placement

**Source:** No prior phase in this repository's tracked plans currently uses either checkpoint
type (`grep -rl "checkpoint:decision\|checkpoint:human-action" .planning/phases/` matches only
this phase's own CONTEXT.md/RESEARCH.md). There is no in-repo analog to copy the exact plan-syntax
from; the planner must follow the GSD plan-schema convention for these checkpoint types directly.
**Apply to:** D-01 requires a `checkpoint:decision` (owner go-ahead) immediately before the
`main`-bound PR is merged (one-way/irreversible per D-01's own text). D-03 requires a
`checkpoint:human-action` for the "Check for updates" UI click, since RESEARCH.md's Pitfall 1 and
Environment Availability table confirm no `gh api` surface exists for either the manual trigger or
reading "config accepted" — both are UI-only (Insights → Dependency graph → Dependabot tab).

### External-observation-only verification (no pytest/tox file)

**Source:** RESEARCH.md's own Validation Architecture section states plainly that this phase's
three requirements (DEP-01, DEP-03, DEP-04) are "manual-only (external-service observation)" with
`gh pr view <n> --json ...` / `git show --name-only <sha>` / `uv lock --check` on a checked-out PR
head as the only verification commands — mirroring the git-tracked, no-pytest verification style
`65-CI-EVIDENCE.md` and `65-REVERT-EVIDENCE.md` already use for their own CI-run and revert
observations (`gh run view`, `gh run list --json ...`, quoted verbatim, never asserted via a test
file).
**Apply to:** every plan/wave in this phase. Do not create a `tests/test_dependabot_*.py` file —
there is no schema this project's own suite validates for `.github/dependabot.yml` (confirmed:
"has no schema the project's own test suite validates").

### Byte-identity cross-branch check (D-01)

**Source:** `65-REVERT-EVIDENCE.md`'s fence item (b) pattern:
```bash
$ git diff --name-only d32eb5db6219bf4917ab820a44562ba479e5fe71 HEAD -- pyproject.toml tox.ini uv.lock tests/test_toolchain_config_gate.py typsphinx .github/workflows flake.nix flake.lock CLAUDE.md
(empty)
```
**Apply to:** D-01's own explicit verification instruction — `git diff` the file between the
`main`-bound PR branch and the milestone branch, expect empty, before merging either.

## No Analog Found

None — every artifact this phase creates or modifies has a Phase 65 tracked analog (config file
self-edit; evidence-file structure; wave-gate verify-command idiom). RESEARCH.md itself confirms
there is no application-code, pytest, or tox-file surface for this phase to map against, so no
"role x data-flow" combination here needed to fall back to a stack-only (RESEARCH.md Code
Examples) pattern.

## Metadata

**Analog search scope:** `.github/dependabot.yml` (the file itself);
`.planning/phases/65-tox-uv-bare-tox-uv-revert-on-the-uv-path-tox-actually-resolves/` (all
`65-*.md` evidence and plan files, all git-tracked per `git ls-files`); repo-wide grep for
`checkpoint:decision`/`checkpoint:human-action` usage (none found outside this phase's own
CONTEXT/RESEARCH).
**Files scanned:** `.github/dependabot.yml`, `65-CI-EVIDENCE.md`, `65-REVERT-EVIDENCE.md`
(both read in full), directory listing of `65-*` phase artifacts.
**Pattern extraction date:** 2026-09-12
**Tracked-source gate:** all paths cited above verified via `git ls-files` to be tracked source,
none a `.gsd/capabilities/` or other gitignored mirror.
