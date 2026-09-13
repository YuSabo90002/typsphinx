# Phase 71: v0.9.4 Close Prep (prep-only, unpublished) - Pattern Map

**Mapped:** 2026-09-13
**Files analyzed:** 9 (1 product-tree file + 8 `.planning/phases/71-*/` evidence/handoff files)
**Analogs found:** 9 / 9 (all exact analogs, same phase-shape one milestone earlier)

This phase is release-prep tooling, not application code. There is no controller/service/model
tier here — every "file" is either the one product-tree edit (`CHANGELOG.md`) or a
`.planning/phases/71-*/` evidence/handoff document. Every analog lives in the archived Phase 69
directory `.planning/milestones/v0.9.3-phases/69-v0-9-3-close-prep-prep-only-unpublished/`, which
executed the identical shape for v0.9.3 one milestone earlier, plus `CHANGELOG.md` itself and
Phase 70's masked-AST evidence files.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `CHANGELOG.md` (append one bullet under `## [Unreleased]` → `### Changed`) | config (structured content, not code) | transform (text append, house-register template) | `CHANGELOG.md:12-35` itself (the three existing v0.9.3 bullets) | exact |
| `71-CLOSEOUT-GUARD.md` | utility (measurement/fence script-in-doc) | batch (fixed probe sequence, re-run 3x) | `69-CLOSEOUT-GUARD.md` | exact |
| `71-CHANGELOG-EVIDENCE.md` | test (evidence transcript) | transform (extraction + assertion) | `69-CHANGELOG-EVIDENCE.md` | exact |
| `71-PREFLIGHT-EVIDENCE.md` | utility (non-committing trial-merge probe) | request-response (git/gh/uv read calls, no mutation) | `69-PREFLIGHT-EVIDENCE.md` | exact |
| `71-GREEN-TREE-EVIDENCE.md` | test (local suite/docs proof) | batch (full local test/docs run) | `69-GREEN-TREE-EVIDENCE.md` | exact |
| `71-CI-EVIDENCE.md` | test (CI dispatch + job census) | event-driven (`workflow_dispatch` → poll → job census) | `69-CI-EVIDENCE.md` | exact |
| `71-SC1-INVARIANTS.md` | test (unpublished-shape remote probes) | request-response (read-only external API/CLI probes) | `69-SC1-INVARIANTS.md` | exact |
| `71-HANDOFF.md` | config (standalone instruction doc for a later command) | transform (structured checklist authoring) | `69-HANDOFF.md` | exact |
| `COVERAGE.md` | config (reasoned no-external-API declaration) | transform (fixed declaration template) | `69-.../COVERAGE.md` | exact |

D-11's two new checks (code-freeze diff + masked-AST re-run) have no Phase 69 analog — their
closest analog is Phase 70's own evidence, not Phase 69:

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| D-11 masked-AST re-run (likely folded into `71-CHANGELOG-EVIDENCE.md` or its own section) | utility (AST-hash comparison harness) | transform (parse → mask → hash → compare) | `70-MASK-PILOT-EVIDENCE.md` (harness) + `70-AFTER-STATIC-EVIDENCE.md` (invocation/per-file table) | exact |

## Pattern Assignments

### `CHANGELOG.md` (config, transform)

**Analog:** `CHANGELOG.md:8-36` itself (the existing `## [Unreleased]` → `### Changed` block, three
bullets in place today).

**Section anchors** (read live before editing, do not assume line numbers):
```
## [Unreleased]

### Changed

- **Contributor tooling returns to `tox-uv` from `tox-uv-bare` (TOX-01, TOX-02, TOX-03, TOX-04).**
  ...
- **Dependabot's Python dependency updates now use the `uv` ecosystem instead of `pip` (DEP-01, ...).**
  ...
- **`flake.nix` now provides a NixOS development shell (NIX-01, ..., DOC-19, DOC-20, DOC-21).**
  ...

### Planned for Future Releases
```

**House-register bullet shape to copy** (bold lead with verb + trailing req IDs in parens, one
plain "no effect on installing or using typsphinx" sentence, at most one evidence sentence):
```markdown
- **Contributor tooling returns to `tox-uv` from `tox-uv-bare` (TOX-01, TOX-02, TOX-03, TOX-04).**
  The `dev` extra and `tox.ini`'s `requires` line once again name `tox-uv`, with `uv.lock`
  regenerated in the same change. This has no effect on installing or using typsphinx. A CI run
  dispatched against the branch carrying this change was green across the Linux, Windows and
  macOS test lanes.
```

**Anti-pattern flagged by Phase 69's own code review (`69-REVIEW.md` WR-01):** a bare-noun-phrase
bold lead, e.g. `**A NixOS development shell (...).**` — the fourth bullet must open with a
verb-bearing bold lead per D-01/D-03, following the `tox-uv` bullet's shape (`Contributor tooling
returns to...`) rather than the `flake.nix` bullet's shape (`` `flake.nix` now provides... `` — note
even this one leads with a backtick-quoted subject + verb, which is acceptable; only a pure noun
phrase with no verb is the flagged defect).

**Where to insert:** append as the fourth bullet, directly after the `flake.nix` bullet and before
the blank line that precedes `### Planned for Future Releases`. Everything else in the file
(D-04) — the `Planned for Future Releases` block, every versioned section, and the tail
`[Unreleased]: .../compare/v0.9.2...HEAD` link — is byte-identical; do not touch.

**Numbers to transcribe fresh, never copy from a planning doc:** the test-fixture project count and
the `.typ` byte-identical corpus claim (D-03) come from `70-AFTER-RUNTIME-EVIDENCE.md` /
`70-CORPUS-DOCS-BASE-EVIDENCE.md` at execution time. The concrete `Dict[str, Any]` →
`dict[str, Any]` example is traced to `typsphinx/template_engine.py`'s `map_parameters` function
(`sphinx_metadata: Dict[str, Any]` → `sphinx_metadata: dict[str, Any]` at
`typsphinx/template_engine.py:468-470`, per `70-DOCS-DIFF-EVIDENCE.md:515-518`).

**Forbidden tokens in the new bullet's prose (verify with `grep`):** `v0.9.4`, `0.9.4`, `v0.9.3`,
`0.9.3` (D-01), and `ja`, `Japanese`, `catalog` (D-02).

---

### `71-CLOSEOUT-GUARD.md` (utility, batch)

**Analog:** `.planning/milestones/v0.9.3-phases/69-v0-9-3-close-prep-prep-only-unpublished/69-CLOSEOUT-GUARD.md`
(full file read above).

**Baseline block shape to copy** (§ "Baseline", lines 1-46 of the analog):
```
$ git rev-parse HEAD
<sha>

$ sha256sum .planning/REQUIREMENTS.md
<digest>  .planning/REQUIREMENTS.md

$ wc -l .planning/REQUIREMENTS.md
<n> .planning/REQUIREMENTS.md

$ grep -c 'REL-12' .planning/REQUIREMENTS.md
<count>

$ date -u +"%Y-%m-%dT%H:%M:%SZ"
<timestamp>
```
followed by a `KEY = value` block:
```
PHASE_BASE_SHA = <sha>
REQ_SHA256_BASE = <digest>
REQ_LINES_BASE = <n>
REL12_HITS_BASE = <count>
GUARD_AT = <timestamp>
```
For Phase 71, rename every `REL12_*` key to `REL13_*` and every `REL-12` grep target to `REL-13`
(D-09). Today's live values (2026-09-13, before Phase 71 edits, from `71-RESEARCH.md`'s own
Pattern 2 section — **re-measure fresh at plan-execution time, do not copy**):
```
REQ_SHA256_BASE (current) = 4d98e0287552d2dce8f45b7939dfcb0e729523c6869bfa1cd2d1d041119c5636
REQ_LINES_BASE (current) = 80
REL13_HITS_BASE (current) = 4
```

**§ "The lines under guard" classification pattern to copy** (analog lines 64-91): quote the
verbatim `grep -n 'REL-13' .planning/REQUIREMENTS.md` output, then classify each hit line as
**state-bearing** (the checkbox bullet and the Traceability row) vs. **informational-only** (phase
distribution table, coverage-note prose) — per the RESEARCH.md live census, REL-13's hits are at
lines 24 (checkbox, state-bearing), 33 (AMENDED-block prose, informational), 71 (Traceability row,
state-bearing), 75 (coverage-count line, informational).

**§ "Why the whole-file SHA-256 is the primary probe" rationale to copy verbatim** (analog lines
93-102): line-count neutrality of a `- [ ]` → `- [x]` flip, and the Phase 63 precedent of a
three-requirement simultaneous flip that a scoped grep would have missed.

**§ "Re-verification protocol (phase close)" command block to copy** (analog lines 124-142):
```bash
sha256sum .planning/REQUIREMENTS.md
wc -l .planning/REQUIREMENTS.md
git diff --name-only -- .planning/REQUIREMENTS.md
grep -n 'REL-13' .planning/REQUIREMENTS.md
```

**§ "For the operator running phase.complete" to copy verbatim in structure** (analog lines
144-191): back up `REQUIREMENTS.md`/`ROADMAP.md`/`STATE.md` outside the repo before either
`phase.complete` entry point; re-run the four probes after; `git checkout --` on divergence;
"reverted and reported, never committed"; state that `71-HANDOFF.md` reproduces this section
in full.

**§ "Third observation" pattern to copy** (analog lines 300-365): the orchestrator records
`OBS3_AT`, the pre-call digest, `phase.complete`'s own reported flip (verbatim diff hunk), the
revert command, and post-revert probes with a `REQ_VERDICT_OBS3 = REVERTED` key line. This section
is written by the orchestrator, not a plan, exactly as in the analog.

---

### `71-PREFLIGHT-EVIDENCE.md` (utility, request-response)

**Analog:** `69-PREFLIGHT-EVIDENCE.md`, reused via the exact command sequence already cited in
`71-RESEARCH.md` Pattern 3 (imports/core-pattern equivalent for this file type):
```bash
git fetch origin
git rev-parse origin/main                       # ORIGIN_MAIN_SHA
git merge-tree --write-tree HEAD "$ORIGIN_MAIN_SHA"; echo "exit:$?"   # MERGE_RC, MERGE_TREE
S="$(mktemp -d)"
git archive "$MERGE_TREE" pyproject.toml uv.lock | tar -x -C "$S"
uv --directory "$S" lock --check; echo "exit:$?"                       # LOCK_CHECK_EXIT
git merge-base --is-ancestor "$ORIGIN_MAIN_SHA" HEAD; echo "exit:$?"   # must be 1
gh api repos/YuSabo90002/typsphinx/branches/main/protection --jq '.required_status_checks'
```
Optional lint half (run because Phase 70 touched lint-relevant files):
```bash
S2="$(mktemp -d)"
git archive "$MERGE_TREE" | tar -x -C "$S2"
uv --directory "$S2" sync --locked --extra dev --no-install-project
uv --directory "$S2" run --no-sync ruff check .; echo "exit:$?"
uv --directory "$S2" run --no-sync black --check .; echo "exit:$?"
```
**Error/probe-shaped exit-code convention:** never chain a "may legitimately be non-zero" command
inside `&&` (Pitfall 3 in RESEARCH.md) — always `; echo "exit:$?"` immediately after, exactly as
the analog does.

---

### `71-GREEN-TREE-EVIDENCE.md` (test, batch)

**Analog:** `69-GREEN-TREE-EVIDENCE.md`. Core pattern: full local suite + docs build from a clean
tree, with the `--extra dev --extra docs` provisioning confirmed via
`uv run python -c "import myst_parser; print(myst_parser.__version__)"` before trusting a
"0 skipped" reading on `tests/test_changelog_page_gate.py` (Pitfall 6). Docs warning counts always
come from `rm -rf docs/_build` immediately before each counted build (Pitfall 5).

---

### `71-CI-EVIDENCE.md` (test, event-driven)

**Analog:** `69-CI-EVIDENCE.md` / `70-CI-EVIDENCE.md`. Core pattern (dispatch → poll → per-job
census), copied verbatim from `71-RESEARCH.md` Pattern 4:
```bash
gh workflow run CI --ref gsd/v0.9.4-typing-modernization
gh run list --workflow=ci.yml --branch gsd/v0.9.4-typing-modernization --event workflow_dispatch --limit 5 --json databaseId,headSha,status,createdAt,url
gh run view <RUN_ID> --json status,conclusion,workflowName,headSha,url,createdAt,updatedAt
gh run view <RUN_ID> --json jobs --jq '.jobs[] | [.name, .conclusion] | @tsv'
timeout 590 gh run watch <RUN_ID> --interval 30
gh run view <RUN_ID> --json status,conclusion
```
Expect the same 12 named jobs both prior dispatches recorded (`Code Coverage`,
`Integration Test - basic`, `Integration Test - advanced`, `Lint and Format Check`,
`Test Python {3.12,3.13} on {ubuntu,windows,macos}-latest`, `Build Package`, `Type Check`). Read
`ruff`'s verdict from `Lint and Format Check`'s `Run lint with tox` step log via
`gh run view --job <job_id> --log`, never from `release.yml`.

---

### `71-SC1-INVARIANTS.md` (test, request-response)

**Analog:** `69-SC1-INVARIANTS.md`. Core pattern (each remote probe paired with a positive
control against `v0.9.2`), copied verbatim from `71-RESEARCH.md`'s "Code Examples" section:
```bash
sed -n 7p pyproject.toml
git tag -l 'v0.9*'
git tag -l 'v0.9.3'; git tag -l 'v0.9.4'
git ls-remote --tags origin
git ls-remote --tags origin | grep -c 'refs/tags/v0\.9\.2$'
git ls-remote --tags origin | grep -cE 'refs/tags/v0\.9\.[34]'
curl -sS -o /dev/null -w '%{http_code}' https://pypi.org/pypi/typsphinx/0.9.2/json
curl -sS -o /dev/null -w '%{http_code}' https://pypi.org/pypi/typsphinx/0.9.3/json
curl -sS -o /dev/null -w '%{http_code}' https://pypi.org/pypi/typsphinx/0.9.4/json
gh release list --limit 20 --json tagName,isLatest,publishedAt
gh pr list --head gsd/v0.9.4-typing-modernization --state all --json number,state
```
**Naming note (this project's own hazard, Pitfall 4):** `git ls-remote --tags origin` must run
unfiltered first (silence in a piped grep is indistinguishable from a network failure).

This file also carries D-11 part 1 (the code-freeze diff), reused verbatim from
`71-RESEARCH.md`'s own Code Examples section:
```bash
git log --format='%H %s' -1 -- typsphinx/ tests/
git diff --stat e721ff899a981eafdad696ef1a9c93aaab41ece5..HEAD -- typsphinx/ tests/
# expected: empty
```

---

### D-11 part 2 — masked-AST re-run (utility, transform)

**Analog:** `70-MASK-PILOT-EVIDENCE.md` (the harness itself, byte-checked at
`MASK_HARNESS_SHA256 = 11cdbeb68cae48a890dfc98736ae2ff7fc15c4557cddad6c5f3a06f425db8a65`) and
`70-AFTER-STATIC-EVIDENCE.md` (the invocation pattern and the 10-file table).

**Harness (`ast.NodeTransformer` masking annotations + `typing`/`collections.abc` imports, then
hashing the dumped tree):**
```python
import ast
import hashlib
import sys


class Mask(ast.NodeTransformer):
    def visit_ImportFrom(self, node):
        if node.module in ("typing", "collections.abc"):
            return None
        return node

    def visit_FunctionDef(self, node):
        return self._mask_func(node)

    def visit_AsyncFunctionDef(self, node):
        return self._mask_func(node)

    def _mask_func(self, node):
        self.generic_visit(node)
        node.returns = None
        a = node.args
        for arg in a.posonlyargs + a.args + a.kwonlyargs:
            arg.annotation = None
        if a.vararg:
            a.vararg.annotation = None
        if a.kwarg:
            a.kwarg.annotation = None
        return node

    def visit_AnnAssign(self, node):
        self.generic_visit(node)
        node.annotation = ast.Constant(value=None)
        return node


t = ast.parse(sys.stdin.read())
t = Mask().visit(t)
ast.fix_missing_locations(t)
print(
    hashlib.sha256(
        ast.dump(t, annotate_fields=True, include_attributes=False).encode()
    ).hexdigest()
)
```

**Invocation pattern:**
```bash
H="$(sed -n '/^~~~python mask-harness$/,/^~~~$/p' 70-MASK-PILOT-EVIDENCE.md | sed '1d;$d')"
printf '%s\n' "$H" | sha256sum   # must equal 11cdbeb68cae48a890dfc98736ae2ff7fc15c4557cddad6c5f3a06f425db8a65
sk() { uv run python -c "$H"; }
sk < <(git show 697a113221a8a267d7e8c6dd1f2b95672f9454d2:typsphinx/translator.py)
sk < typsphinx/translator.py
```
Re-run against Phase 70's `PHASE_BASE_SHA` (`697a113221a8a267d7e8c6dd1f2b95672f9454d2`) for the
same ten files (`tests/conftest.py`, `tests/test_bundle_layout_sweep_gate.py`,
`tests/test_include_edge_derivation_unit.py`, `tests/test_include_ledger_removal_gate.py`,
`typsphinx/__init__.py`, `typsphinx/builder.py`, `typsphinx/template_engine.py`,
`typsphinx/template_registry.py`, `typsphinx/translator.py`, `typsphinx/writer.py`). Live-run this
fresh on the close tip; do not copy Phase 70's own recorded hash values as if pre-computed.

---

### `71-HANDOFF.md` (config, transform)

**Analog:** `69-HANDOFF.md`. Structural checklist to copy (per `71-RESEARCH.md` Pattern 5):
1. Opening negative-first paragraph (no tag/PyPI/Release/bump; `update-pin.yml`/RTD `stable` N/A).
2. Numbered "what `/gsd-complete-milestone` does, in order" steps: fence-first backup → re-run
   trial merge → merge `origin/main` if needed (merge commit, never rebase) → `uv lock --check` +
   re-sync → push → open PR → wait on the six named checks → merge (`gh pr merge <number> --merge`)
   → observe the post-merge facts, only then flip REL-13.
3. "What this phase satisfied" — quote REL-13 verbatim, state it stays open, cite every SC verdict.
4. "Recorded without acting" — dependabot census (D-12), unclaimed-version-number statement (D-08).
5. "Before and after phase.complete-family tooling" — reproduce `71-CLOSEOUT-GUARD.md`'s
   § "For the operator running phase.complete" inline, verbatim.
6. "Fence observation" — final live re-check inside this plan's own worktree.
7. "What this phase deliberately did not do" — explicit negative checklist.

---

### `COVERAGE.md` (config, transform)

**Analog:** `.planning/milestones/v0.9.3-phases/69-v0-9-3-close-prep-prep-only-unpublished/COVERAGE.md`.
**Pattern:** open with the literal sentence "No external API integration: ..." then walk through
each detector signal (the phase's own read-only "Trust Boundaries" table row, this file's own
required opening phrase) explaining why each is the detector matching its own required vocabulary,
not a genuine outbound integration (Pitfall 8 in `71-RESEARCH.md`).

## Shared Patterns

### `KEY = value` evidence-line discipline
**Source:** every analog evidence file above (`69-CLOSEOUT-GUARD.md`'s `PHASE_BASE_SHA = ...` /
`REQ_SHA256_BASE = ...` blocks; `69-CHANGELOG-EVIDENCE.md`'s post-hoc fix).
**Apply to:** every `71-*-EVIDENCE.md` file and `71-CLOSEOUT-GUARD.md`.
**Rule:** keep the value bare on the `KEY = value` line; put explanatory prose or parentheticals on
a separate line before/after, never on the same line — `71-RESEARCH.md` Pitfall 2 documents the
exact failure mode this caused mid-Phase-69 (fixed in commit `56880eca`).

### Probe-shaped exit codes never inside `&&`
**Source:** `69-PREFLIGHT-EVIDENCE.md`'s command sequence.
**Apply to:** `71-PREFLIGHT-EVIDENCE.md`, `71-SC1-INVARIANTS.md`, and any diff/grep used as a
boolean probe.
**Rule:** capture with `; echo "exit:$?"` immediately after a command whose "expected" outcome may
be non-zero (e.g. `diff`, `grep -c` with zero matches); never chain such a command inside `&&`
(Pitfall 3).

### Clean-build discipline for docs warning counts
**Source:** `69-GREEN-TREE-EVIDENCE.md`.
**Apply to:** any docs-build comparison in `71-GREEN-TREE-EVIDENCE.md` or `71-CHANGELOG-EVIDENCE.md`.
**Rule:** `rm -rf docs/_build` immediately before every counted build, both baseline and post-edit
(Pitfall 5).

### Requirement-checkbox fence, reused wholesale
**Source:** `69-CLOSEOUT-GUARD.md` in full.
**Apply to:** `71-CLOSEOUT-GUARD.md` and the corresponding section reproduced inside `71-HANDOFF.md`.
**Rule:** whole-file SHA-256 (not scoped grep) as the primary probe; re-verify three times (phase
head, phase close, and after `phase.complete`-family tooling runs); revert with
`git checkout -- .planning/REQUIREMENTS.md`, report but never commit a flip.

## No Analog Found

None — every file in this phase's scope has an exact analog, either in the Phase 69 archive (the
release-prep shape) or in Phase 70's own evidence files (the two D-11 checks unique to this phase).

## Metadata

**Analog search scope:** `.planning/milestones/v0.9.3-phases/69-v0-9-3-close-prep-prep-only-unpublished/`,
`.planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/`, and `CHANGELOG.md`
at the repository root.
**Files scanned:** 9 Phase-69 evidence/handoff files (read in full or via `71-RESEARCH.md`'s
verbatim quotations), 2 Phase-70 evidence files (masked-AST harness + invocation), 1 product-tree
file (`CHANGELOG.md`, read live this session).
**Pattern extraction date:** 2026-09-13.
