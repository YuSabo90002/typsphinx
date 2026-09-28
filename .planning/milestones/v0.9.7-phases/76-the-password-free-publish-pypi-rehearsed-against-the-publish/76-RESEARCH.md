# Phase 76: The `password:`-Free `publish-pypi`, Rehearsed Against the Published v0.9.6 — and MSG-06 - Research

**Researched:** 2026-09-27
**Domain:** GitHub Actions OIDC/Trusted-Publishing workflow mechanics (PyPI) + a leaf-module logging fix
**Confidence:** HIGH (every load-bearing claim below is either a direct measurement taken this
session or a verbatim read of the authoritative source; the one exception — the GH Release
overwrite behavior on an already-tagged release — is `[CITED]`/secondary and is, in any case, moot
per the Contradiction/Risk sections below)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**The rehearsal dispatch — who fires it and how the wait is handled**

- **D-01: The executor fires the dispatch itself.** A plan task runs
  `gh workflow run release.yml --ref <ref> -f tag=v0.9.6`. The owner does not fire it and does not
  hand a run id over.
  - The task reads `gh run list --workflow=release.yml --limit 20 --json databaseId,createdAt,event`
    **immediately before** the dispatch and records that list as the baseline, then reads it again
    after, and asserts the difference is **exactly one** new run. This is not decoration: a
    `gh workflow run` that returns HTTP 5xx has been observed in this repository to create the run
    anyway, so **no retry of `gh workflow run` is permitted until that before/after difference has
    been read**. A silent second run breaks ATT-02's exactly-one reading (ROADMAP constraint 6).
  - **Reversibility:** one-way — a dispatched run cannot be un-dispatched. The run record, the
    deployment-approval event and the audit trail are permanent, and deleting a run does not restore
    ATT-02's "exactly one dispatch" reading.

- **D-02: The same executor waits the run through and then takes the evidence — one plan.**
  No hand-back to the owner mid-plan.
  The wait is two-staged and the executor polls through both stages:
  (1) the `pypi` environment's manual approval, unbounded until the owner presses it, then
  (2) the environment's 15-minute `wait_timer`.
  Because Bash's foreground timeout ceiling is 600 s, the watch must run either as a background
  command or as a bounded polling loop — not as one foreground `gh run watch`.

- **D-03: Approval-pending reaches the owner via GitHub's own notification, not via the executor.**
  No in-repo signalling mechanism is built for it, and the executor is not expected
  to reach the owner: it is a subagent in a worktree and its mid-run output is not visible to the
  owner. The phase therefore accepts that the dispatch may sit unapproved for some time, and bounds
  that with D-04 instead of trying to shorten it.

- **D-04: The wait is bounded at 90 minutes; on exceeding it the executor HALTs, never re-dispatches.**
  The bound is elapsed time from the dispatch to the run's conclusion. On exceeding it the executor
  writes the run id, every job's current status and conclusion, and the exact point reached, into the
  phase evidence file (D-08), and returns. The same run is picked back up later; a second
  `gh workflow run` is never the recovery path for a slow approval.
  - Grounded on a measurement of this exact workflow, not an estimate: v0.9.6's production release
    run `35730551619` took **48 minutes end to end**, of which **42 m 47 s** was the gap between
    `Build Distribution` completing (13:03:54Z) and `Publish to PyPI` starting (13:46:41Z) — the
    `wait_timer` plus the owner's approval latency. 90 minutes is roughly twice that, so it absorbs
    an approval about 40 minutes slower than v0.9.6's without HALTing.

**Owner prerequisite — NOT a plan task**

- **D-05: The PyPI-side Trusted Publisher is NOT yet registered as of 2026-09-27.** The owner will do
  it. No plan task may claim this step, and no agent can perform it.

**Prerequisite checkbox — must be checked before the ATT-02 dispatch task runs:**

- [ ] The Trusted Publisher is registered on PyPI for the **existing** `typsphinx` project, through
      that project's own *Publishing* settings — **not** the account-level "pending publisher" flow
      most tutorials show, because `typsphinx` is already published. The four fields, all measured
      from the repository rather than recalled:
      - repository owner: `YuSabo90002`
      - repository name: `typsphinx`
      - workflow filename: `release.yml` — the **bare** filename, no `.github/workflows/` prefix
      - environment name: `pypi`

      A mismatch on any one of the four produces `invalid-publisher`, and the error is
      indistinguishable across the wrong-filename, wrong-environment and not-registered cases. The
      registration has **no dependency on any code change** — all four values exist in the repository
      unedited today — so it can be done at any time before the dispatch. It cannot be verified by
      any agent: PyPI exposes no API for reading a project's configured publishers, so the rehearsal's
      **duplicate rejection is itself the verification** that all four fields match.

**Claude's Discretion**

- **D-06: The dispatch ref is the milestone branch, so the phase is shaped as two waves.**
  The ref is `gsd/v0.9.7-trusted-publishing-and-release`.
  Wave 1 lands the ATT-01 edit (and MSG-06 in parallel — disjoint
  files); the orchestrator merges wave 1 at cleanup-wave and **pushes the milestone branch to
  `origin`**; wave 2 then takes the pre-dispatch capture, fires the dispatch against that pushed
  milestone branch, watches, and records the evidence.
  - Why not dispatch from the executor's own worktree branch: `workflow_dispatch` runs the
    *dispatched ref's* copy of `release.yml`, so the ref must exist on `origin` and must carry the
    edit. A worktree branch is ephemeral — it is merged and deleted at cleanup-wave — which would
    leave ATT-02's evidence naming a ref that no longer exists.
  - Why this is not blocked: the `pypi` environment's `deployment_branch_policy` is **`null`**
    (measured 2026-09-27 via `gh api repos/YuSabo90002/typsphinx/environments/pypi`), so there is no
    branch restriction and a dispatch from a non-default branch does reach the `pypi` environment.
    `release.yml` already lives on `main` carrying a `workflow_dispatch` trigger, so the "a new
    workflow cannot be dispatched from an unmerged milestone branch" rule that still blocks QUA-08
    does not apply — `release.yml` is not new.
  - The evidence records both the ref **name** and its **commit SHA**, so the run stays reproducible
    after cleanup-wave.
  - **Reversibility:** costly — pushing the milestone branch to `origin` mid-phase is an outward-facing
    action, and the dispatched run permanently names the ref it ran on.

- **D-07: On an `invalid-publisher` rejection, recovery is `gh run rerun` of the SAME run.**
  This covers `invalid-publisher` and `invalid-pending-publisher` alike, and it means the executor
  HALTs rather than firing a second `gh workflow run`. It transcribes the verbatim failing lines and
  returns to the owner, who fixes the PyPI-side registration. Only then is the same run re-run.
  - This keeps ATT-02's "exactly one dispatch" literally true rather than requiring it to be re-read,
    and it is the same "cheapest recovery first" path ROADMAP constraint 14 already establishes for a
    failed production publish: `build`'s artifact is still downloadable within GitHub's 7-day
    retention window, so `publish-pypi` can re-run against it.
  - If the 7-day window has lapsed by the time the registration is fixed, that is an owner decision,
    not an executor one: a second dispatch is permitted **only** on explicit owner approval, and the
    evidence must then record both run ids and state plainly which one ATT-02 is read on.

- **D-08: All ATT-01/ATT-02 evidence goes into one file at the fixed name `76-ATT-EVIDENCE.md`.**
  Full path:
  `.planning/phases/76-the-password-free-publish-pypi-rehearsed-against-the-published-v0-9-6-and-msg-06/76-ATT-EVIDENCE.md`.
  Not `76-VERIFICATION.md`: that name is reserved by `gsd-verifier`, which overwrites it wholesale.
  Phase 77's handoff reads this file by that exact name.
  It must contain, at minimum:
  - the **pre-dispatch** PyPI capture: the Simple JSON API's full file list for `typsphinx` with its
    count and every `upload-time`, and the `provenance` value of 0.9.6's two files (expected `null`);
    plus `gh release view v0.9.6`'s asset list
  - the dispatch command verbatim, with the ref name **and** its commit SHA
  - the `gh run list` baseline and the post-dispatch reading, showing the difference is exactly one
  - the run id, every job's conclusion (`validate`, `build`, `publish-pypi`, `publish-testpypi`,
    `create-release`), and the verbatim failing lines from the `Publish to PyPI` step
  - `grep -c 'attestations input ignored'` and `grep -c 'disabling Trusted Publishing'` over the
    rehearsal run's log → both **0**, each paired with the identical grep over run `35730551619` →
    **non-zero**. A zero without its non-zero control is not a reading.
    **⚠️ See "Contradicts Locked CONTEXT/ROADMAP/REQUIREMENTS" below — this exact grep target was
    measured this session and does not behave as this decision assumes.**
  - the **post-dispatch** PyPI capture, diffed against the pre-dispatch one
  - an explicit sentence, in the evidence's own words, that this is the **rehearsal** run and that
    ATT-04 is a reading on the **v0.9.7 release run** — so this observation must not be transcribed
    forward as ATT-04's evidence
  - the measured line numbers of the deleted lines, rather than a repetition of `:141-144`

**Folded Todos**

- `.planning/todos/pending/2026-09-22-release-yml-uses-a-pypi-api-token-so-trusted-publishing-and.md`
  — This is ATT-01 verbatim; it closes with ATT-01's edit plus ATT-02's rehearsal.
- `.planning/todos/pending/2026-08-29-hardcoded-delimiter-path-fragments-in-translator-relative-path-debug-logs.md`
  — This is MSG-06 verbatim, the fourth module of the MSG-02 family.

### Deferred Ideas (OUT OF SCOPE)

None raised in discussion — the discussion stayed inside the phase boundary. Two todos were
reviewed and stay deferred because REQUIREMENTS.md already carries them under Future Requirements:
`2026-07-22-add-sphinx-linkcheck-ci-job.md` (QUA-08 — blocked on the same "new workflow cannot
dispatch from an unmerged milestone branch" rule that does **not** block `release.yml` here, because
`release.yml` is not new) and `2026-08-14-numref-number-diverges...md` (NUM-01, settled as a Known
Limitations disclosure at v0.9.6).

**Out of scope for this phase** (REQUIREMENTS.md § Out of Scope, restated): migrating
`publish-testpypi` to Trusted Publishing; adding `attestations: true`; adding `skip-existing:`;
pinning the action to a commit SHA; job-level `permissions:` narrowing. None of these may appear in
any plan this research supports.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| ATT-01 | `release.yml`'s `publish-pypi` step publishes with no `password:` key (two-line deletion at the **measured** `:143-144`, confirmed this session). | See "Measured baseline: `release.yml`" and Success-Criteria mapping below. |
| ATT-02 | Exactly one `workflow_dispatch` run against `v0.9.6` reaches `Publish to PyPI` and is rejected with `400`/`File already exists`, not `invalid-publisher`. | See "The rehearsal, end to end" — OIDC exchange order, warehouse duplicate-file logic (measured non-reproducible build proves the content-diff path is reached), `gh` mechanics, pre-dispatch gates. |
| MSG-06 | `translator.py`'s two cross-directory relative-path DEBUG logs (measured at `:5119-5123` and `:5224-5228`) route `up_path`/`down_path` through `quote_path()`. | See "MSG-06 — exact fix and test design" — fixture values, expected pre-fix/post-fix messages computed from `quote_path()`'s own source, existing `TypstTranslator(mock_document, mock_builder)` unit-test precedent. |
</phase_requirements>

## Summary

This phase has two independent, mechanically unrelated halves that happen to share a wave
structure (D-06): a two-line workflow-file deletion proven by a live rehearsal against production
PyPI (ATT-01/ATT-02), and a small, already-patterned logging fix in `translator.py` (MSG-06). There
is no new dependency, no new library, and no new architecture to research in the conventional
sense — the "stack" here is GitHub Actions' OIDC/Trusted-Publishing pipeline
(`pypa/gh-action-pypi-publish@release/v1`) and PyPI's upload endpoint (`warehouse`), both read
directly from their authoritative source this session, and a leaf Python module
(`typsphinx/pathfmt.py::quote_path()`) that already exists and has three working call-site
precedents to copy.

The most load-bearing finding is a **direct measurement that falsifies part of a locked CONTEXT
decision**: the exact grep target `'attestations input ignored'`, which D-08 and ROADMAP SC#4
require to read *non-zero* on the v0.9.6 control run `35730551619`, in fact reads **zero** on that
run — because that literal string only ever appears inside the GitHub Actions annotation's `title=`
attribute, which `gh run view --log` does not print. This makes the grep structurally unable to
produce the non-zero control D-08 and SC#4 require, on any run, ever. See the "Contradicts Locked
CONTEXT/ROADMAP/REQUIREMENTS" section for the fix.

The second most load-bearing finding is a **direct measurement that resolves Q1's central risk in
the rehearsal's favor**: a local rebuild of the current tree (byte-identical to the `v0.9.6` git tag
under `typsphinx/`) does **not** hash-match PyPI's served `v0.9.6` wheel or sdist. The sdist is
non-reproducible on every build (gzip embeds a real timestamp); the wheel is reproducible
build-to-build here but is very unlikely to match the *original* CI build's toolchain versions
(`Generator: setuptools (84.0.0)` locally — an unpinned, drifting value). This means the rehearsal's
upload is *guaranteed* to hit PyPI's "filename exists, content differs" branch — `400 File already
exists` — never the "identical file, 200 OK, write nothing" branch that would let `create-release`
run. This holds even before MSG-06 changes `translator.py`'s bytes; after MSG-06 lands it holds a
second, independent way.

**Primary recommendation:** implement ATT-01 as the plain two-line deletion at `:143-144`
(re-measure before editing — do not trust this document's line numbers either, if the branch has
moved); implement MSG-06 by removing the hardcoded `'...'` delimiters and calling `quote_path()`,
mirroring `writer.py:513-515`'s exact pattern; write MSG-06's RED test as a **direct
`TypstTranslator(mock_document, mock_builder)` unit test** (no Sphinx app needed) following
`tests/test_nested_toctree_paths.py`'s existing precedent, driven by a cross-directory docname pair
carrying a literal apostrophe; and before writing D-08's evidence-grep commands, replace
`'attestations input ignored'` with `'disabling Trusted Publishing'` (confirmed non-zero on the
control) — see the dedicated contradiction section.

## ⚠️ Contradicts Locked CONTEXT/ROADMAP/REQUIREMENTS — the `'attestations input ignored'` grep target

**Measured this session, 2026-09-27**, against the actual v0.9.6 production release run
`35730551619`'s log (`gh run view 35730551619 --log`, 3356 lines, still fully retrievable — log
retention is not an issue):

```
$ LC_ALL=C grep -c 'attestations input ignored' control_run.log
0
$ echo "exit=$?"
exit=1
$ LC_ALL=C grep -c 'the attestations input is ignored' control_run.log
1
$ LC_ALL=C grep -c 'disabling Trusted Publishing' control_run.log
1
```

The verbatim matching log line (`[VERIFIED: gh run view 35730551619 --log]`):

```
Publish to PyPI	UNKNOWN STEP	2026-09-22T13:46:50.5362201Z ##[warning]The workflow was run with the 'attestations: true' input, but an explicit password was also set, disabling Trusted Publishing. As a result, the attestations input is ignored.
```

**Root cause**, confirmed by reading the action's own source at `release/v1`
(resolved commit `dc37677b2e1c63e2034f94d8a5b11f265b73ba33`, `twine-upload.sh`)
`[CITED: raw.githubusercontent.com/pypa/gh-action-pypi-publish/release/v1/twine-upload.sh]`:

```bash
ATTESTATIONS_WITHOUT_TP_WARNING="::warning title=attestations input ignored::\
The workflow was run with the 'attestations: true' input, but an explicit \
password was also set, disabling Trusted Publishing. As a result, the \
attestations input is ignored."
```

The literal phrase `attestations input ignored` exists **only** in the GitHub Actions workflow
command's `title=` attribute. `gh run view --log` (and the raw log stream generally) prints only
the rendered `##[warning]<message body>` line — the message body's own text is "the attestations
input **is** ignored" (note the inserted "is"), never the three-word title phrase. This is not a
quirk of this one run: **the exact string `'attestations input ignored'` cannot appear in
`gh run view --log` output for any run, ever**, because it lives exclusively in metadata the log
stream does not render.

**Impact:**

- **D-08** (`76-CONTEXT.md`) instructs the evidence file to run
  `grep -c 'attestations input ignored'` against both the rehearsal run and the control run
  `35730551619`, expecting `0` and *non-zero* respectively, and states "A zero without its non-zero
  control is not a reading." As measured, **the control itself reads zero** — the intended
  falsifiable control is not achievable with this literal string.
- **ROADMAP.md SC#4** (Phase 76, `:366-371`) and **REQUIREMENTS.md ATT-04** (`:47-51`) repeat the
  same literal string for the *v0.9.7* production run's reading, inheriting the same defect.
- **ROADMAP.md Phase 77 SC#4 / the `77-HANDOFF.md` spec** (`:462`) repeats it a third time as the
  pre-written ATT-04 command.

**Recommendation for the plan** (does not touch CONTEXT.md — that is the orchestrator's call to take
to the owner, per this agent's mandate): use the two greps that were actually measured to
discriminate the control:

```bash
gh run view <run-id> --log | LC_ALL=C grep -c 'disabling Trusted Publishing' || true
```

reads **0** when Trusted Publishing is active (nothing to disable) and **non-zero** (confirmed `1`)
on run `35730551619`, where the token-based path disabled it. This is the literal string the
action's own source actually emits into the log body, and it is the one both D-08's intent and
SC#4's intent are reaching for. If the plan wants to additionally check the attestations-specific
wording, the correct literal is `'the attestations input is ignored'` (with "is") — also confirmed
`1` on the control. **This same fix must be carried into Phase 77's `77-HANDOFF.md`
pre-written ATT-04 command** (out of this phase's own scope to edit, but the same defect is baked
into that spec text and will reproduce there verbatim unless corrected).

Record `grep -c 'attestations input ignored'` returning `0` on **both** the rehearsal and the
control run as an explicit note in `76-ATT-EVIDENCE.md` if the plan still wants to preserve that
literal string for continuity with CONTEXT's wording — but it must not be presented as a
discriminating control, because it discriminates nothing.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| PyPI credential removal (ATT-01) | CI/CD workflow (`.github/workflows/release.yml`) | — | A `with:` key deletion in a GitHub Actions composite-action invocation; no application-tier code involved. |
| OIDC token exchange (ATT-02) | External service boundary (GitHub OIDC provider ↔ PyPI's `/_/oidc/*` endpoints) | CI/CD workflow | Entirely inside `pypa/gh-action-pypi-publish`'s Docker container; the workflow file only supplies `id-token: write` and the `environment: pypi` gate — already present, unedited by this phase. |
| Artifact upload / duplicate-file check (ATT-02) | External service (PyPI `warehouse`, `forklift/legacy.py`) | — | Server-side; the workflow only supplies the built `dist/*` files via `twine upload`, already wired. |
| Attestation signing (Sigstore/Rekor, triggered as a side effect of ATT-02's success path) | External service (Sigstore public infrastructure) | CI/CD workflow | Runs inside the action's container, before the twine upload step, only on the OIDC-success path. Not owned by this repo at all; the repo only opts in via the absence of `password:`. |
| Cross-directory relative-path logging (MSG-06) | Application / Sphinx builder internals (`typsphinx/translator.py`) | Leaf utility module (`typsphinx/pathfmt.py`) | Pure Python string formatting inside a docutils-to-Typst translation method; `quote_path()` is a deliberate zero-dependency leaf the translator imports, per its own module docstring. |

## Standard Stack

**Not applicable in the conventional sense** — this phase introduces no new library, no new
runtime dependency, and no new dev dependency. `typsphinx/pathfmt.py::quote_path()` already exists
(added Phase 60, MSG-02) and is imported unchanged from three sibling modules
(`builder.py:22`, `writer.py:15`, `template_registry.py:33`); MSG-06 adds a fourth import site with
identical shape. `pypa/gh-action-pypi-publish@release/v1` is already pinned in `release.yml:142` and
is explicitly **not** to be re-pinned to a commit SHA (REQUIREMENTS.md § Out of Scope; ROADMAP
constraint 9) — `@release/v1` resolved this session to commit `dc37677b2e1c63e2034f94d8a5b11f265b73ba33`
(2026-07-28) `[VERIFIED: gh api repos/pypa/gh-action-pypi-publish/commits/release/v1]`.

### Installation

None — no `npm install` / `pip install` / `uv add` step belongs to this phase.

## Package Legitimacy Audit

**Not applicable** — no external package is installed, upgraded, or newly imported in this phase.
`quote_path` is an existing first-party module (`typsphinx/pathfmt.py`) already shipped in the
package; nothing from PyPI, npm, or crates.io is added.

## Architecture Patterns

### System Architecture Diagram — ATT-01/ATT-02, the rehearsal's control flow

```
gh workflow run release.yml --ref <milestone-branch> -f tag=v0.9.6
        |
        v
  [validate job]  --- pyproject.toml version == tag input? -----> FAIL (exit before build)
        | success (both read "0.9.6" on the dispatch ref, per constraint 3)
        v
  [build job] ---- uv build -> dist/*.whl, dist/*.tar.gz ---- upload-artifact "dist-packages"
        | success
        v
  [publish-pypi job] --- environment: pypi (manual approval, then 15-min wait_timer) ---
        |                                                        |
        | approved + timer elapsed                               | never approved
        v                                                        v
  download-artifact "dist-packages"                    (D-04: HALT at 90 min, no re-dispatch)
        |
        v
  pypa/gh-action-pypi-publish@release/v1 (inside its own Docker container):
     1. twine check dist/*
     2. TRUSTED_PUBLISHING=true (no password set)
        -> oidc-exchange.py: GET https://pypi.org/_/oidc/audience
                              detect_credential(audience) [GitHub OIDC token, aud=pypi]
                              POST https://pypi.org/_/oidc/mint-token {token}
           |                                                        |
           | mint succeeds (registration matches all 4 fields)      | mint fails
           v                                                        v
     3. attestations.py: Sigstore Fulcio cert + Rekor         die("invalid-publisher"/
        transparency-log entry for EACH dist file                "invalid-pending-publisher")
        (PUBLIC, PERMANENT side effect -- see Common Pitfalls)     -> step FAILS here,
        |                                                             NO Sigstore entry created,
        v                                                             NOTHING reaches PyPI
     4. twine upload --attestations dist/*
        -> PyPI warehouse: _is_duplicate_file(filename, hashes)
           |                                    |
           | hashes match exactly (impossible   | hashes differ (GUARANTEED here --
           | here, measured this session)       | see "Reproducibility" below)
           v                                    v
        200 OK, nothing written           400 Bad Request "File already exists
        (create-release COULD then run    (<filename>, with blake2_256 hash <h>).
         against v0.9.6's existing         See .../help/#file-name-reuse ..."
         GitHub Release -- see below)      -> publish-pypi job FAILS here (desired outcome, SC#2)
        v
  [create-release job] needs: [build, publish-pypi]
     publish-pypi != success -> create-release SKIPPED (SC#3)
```

### Recommended structure — no new files beyond the evidence document

```
.github/workflows/release.yml          # ATT-01: two lines removed (:143-144, re-measure)
typsphinx/translator.py                # MSG-06: two f-strings edited (:5119-5123, :5224-5228)
typsphinx/pathfmt.py                   # unchanged -- quote_path() already exists
tests/test_translator_path_quoting_gate.py   # NEW -- follows the *_path_quoting_gate.py family
                                              # naming convention (writer/builder/template_registry
                                              # siblings), MSG-06's own test module
.planning/phases/76-.../76-ATT-EVIDENCE.md   # D-08's fixed-name evidence file (wave 2 output)
```

### Pattern 1: `quote_path()` call-site substitution (MSG-06)

**What:** Replace a hardcoded `'{value}'` f-string interpolation with `{quote_path(value)}` —
`quote_path()` supplies its own delimiter.
**When to use:** Exactly the two cross-directory DEBUG sites in `translator.py`; nowhere else in
either function (measured — see "MSG-06" section below for the full discovery grep).
**Example, the identical pattern already live in three sibling modules:**
```python
# Source: typsphinx/writer.py:511-515 (MSG-04, Phase 60) -- read this session
logger.debug(
    f"Rendering wrapper for docname {docname!r} at "
    f"wrapper_relative_dir={quote_path(wrapper_relative_dir)}, "
    f"include_path={quote_path(include_path)}, template_file={quote_path(template_file)}"
)
```
MSG-06's fix is structurally identical:
```python
# typsphinx/translator.py -- BEFORE (both sites, :5119-5123 and :5224-5228, identical text)
logger.debug(
    f"Cross-directory path calculation: up_count={up_count}, "
    f"up_path='{up_path}', down_path='{down_path}', "
    f"result: {relative_path}"
)

# AFTER
logger.debug(
    f"Cross-directory path calculation: up_count={up_count}, "
    f"up_path={quote_path(up_path)}, down_path={quote_path(down_path)}, "
    f"result: {relative_path}"
)
```
Plus one new module-level import: `from typsphinx.pathfmt import quote_path`
(`translator.py` currently imports nothing from `typsphinx` at all — confirmed via
`grep -n "^import\|^from" typsphinx/translator.py`, all six imports are `re`, `typing`,
`docutils`, `sphinx.*` — so this is a new import line, not a change to an existing one).

### Pattern 2: Direct-instantiation unit test for a private translator method (MSG-06's test)

**What:** `TypstTranslator` methods that read no Sphinx-build state can be unit-tested by
instantiating the translator directly against a minimal mock document/builder pair — no
`SphinxTestApp` or real build needed.
**When to use:** Any `TypstTranslator._compute_*` helper whose body touches only its own
parameters (confirmed for both MSG-06 sites: neither references `self` anywhere in its body).
**Example, existing precedent for the exact two methods MSG-06 touches:**
```python
# Source: tests/test_nested_toctree_paths.py:17,32-51,107-113 (read this session, EXISTING file,
# not new for this phase -- MSG-06's new test module should follow this same construction)
from typsphinx.translator import TypstTranslator

@pytest.fixture
def mock_document():
    reporter = Reporter("", 2, 4)
    doc = nodes.document("", reporter=reporter)
    doc.settings = states.Struct()
    doc.settings.env = None
    doc.settings.language_code = "en"
    doc.settings.strict_visitor = False
    return doc

@pytest.fixture
def mock_builder():
    class MockConfig:
        typst_use_mitex = True
    class MockDomains:
        pass
    class MockEnv:
        domains = MockDomains()
    class MockBuilder:
        name = "typst"
        current_docname = None
        config = MockConfig()
        env = MockEnv()
    return MockBuilder()

# Existing cross-directory case already exercised (value only, not the DEBUG log):
translator = TypstTranslator(mock_document, mock_builder)
result = translator._compute_relative_include_path(
    target_docname="chapter2/doc2", current_docname="chapter1/doc1"
)
assert result == "../chapter2/doc2"
```
MSG-06's new test reuses this exact construction, adds `caplog.at_level("DEBUG")` around the call
(the `test_writer_path_quoting_gate.py` MSG-04 precedent for *that* half of the pattern — see below),
and swaps the fixture docnames for a pair that (a) is cross-directory and (b) carries a literal `'`
in the component that becomes `down_path`. See "MSG-06 — exact fix and test design" for the concrete
fixture values and both the pre-fix and post-fix expected message strings, computed from
`quote_path()`'s own source read this session.

### Anti-Patterns to Avoid

- **Adding `attestations:` or `skip-existing:` to `release.yml`.** Both are explicitly out of scope
  (REQUIREMENTS.md § Out of Scope, ROADMAP constraint 9). `attestations: true` is already the
  action's default the moment Trusted Publishing activates; writing it restates the exact
  misreading ATT-01 exists to correct. `skip-existing: true` would turn ATT-02's duplicate
  rejection — the signal that proves the registration is correct — into a silent pass.
- **Re-dispatching `release.yml` on any failure.** D-04 and D-07 both forbid this. Only
  `gh run rerun` on the *same* run id is permitted, and only after either the 90-minute wait bound
  or an `invalid-publisher`/`invalid-pending-publisher` rejection, and in the latter case only after
  the owner has fixed the PyPI-side registration.
- **Widening MSG-06's fix beyond the two named DEBUG sites.** The discovery grep (see below) found
  no other `'`-delimited path fragment in either function; `builder.py`, `writer.py` and
  `template_registry.py` must stay byte-identical (SC#5).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Quoting a path-valued string for a diagnostic log | A local `f"'{value}'"` literal, or a fresh helper | `typsphinx.pathfmt.quote_path()` (already exists, three working call sites) | It already implements the exact delimiter-selection and apostrophe-doubling contract this fix needs (`repr()`-like, minus backslash doubling); rebuilding it inline would silently diverge from the sibling modules' behavior and defeat the whole point of the MSG-02 family (one shared helper). |
| Determining whether a PyPI upload was accepted, rejected-as-duplicate, or rejected-as-unauthorized | Parsing HTTP status codes by hand from a custom script | Read the actual log line: `twine`'s printed `HTTPError` (via `warehouse`'s `_is_duplicate_file`/`_exc_with_message`) vs. `oidc-exchange.py`'s `die(_SERVER_REFUSED_TOKEN_EXCHANGE_MESSAGE...)` | The two failure shapes are textually distinct and already well-defined by the two upstream projects; re-deriving a classifier risks missing a third shape (malformed JSON response, `HTTPStatus.FORBIDDEN`/`NOT_FOUND` on the audience call, etc.) that the upstream code already names explicitly. |
| Verifying a hash match before/after the rehearsal | A bespoke diffing script | `sha256sum` on the `gh run download`'d `dist-packages` artifact, compared against the Simple JSON API's `hashes.sha256` field (both already plain JSON/text) | Both are single commands; no library needed. |

**Key insight:** every "don't hand-roll" item here is really "don't re-derive what the upstream
source or this repo's own Phase 60 already defined" — this phase's actual coding surface is
minimal (a two-line deletion and a two-call-site substitution), so the risk is over-engineering
the verification tooling around it, not under-tooling the fix itself.

## Common Pitfalls

### Pitfall 1: Treating the `'attestations input ignored'` grep as a working control
**What goes wrong:** The evidence file (D-08) records "0" for the rehearsal and expects "non-zero"
for the control `35730551619`; both actually read 0, so the recorded "reading" is not falsifiable —
a rehearsal on the OLD, credentialed workflow would produce the identical "0/0" pair.
**Why it happens:** The literal phrase lives only in the GitHub Actions annotation's `title=`
attribute (`::warning title=attestations input ignored::...`), which the rendered log body never
repeats verbatim (the body says "...the attestations input **is** ignored").
**How to avoid:** Use `'disabling Trusted Publishing'` (confirmed non-zero on the control) as the
primary grep; see the dedicated contradiction section above.
**Warning signs:** Any evidence file where both the rehearsal and control readings for this specific
grep are `0` — that is not evidence of the fix working, it is evidence the grep cannot discriminate.

### Pitfall 2: Assuming build reproducibility must be engineered for SC#3 to hold
**What goes wrong:** Over-designing a `SOURCE_DATE_EPOCH`-pinning step or similar "make the rebuild
byte-identical" mitigation that ROADMAP/REQUIREMENTS never asked for and that is explicitly out of
scope (no new build-tooling change is listed anywhere in this phase's requirements).
**Why it happens:** Q1's framing (worry about an accidental 200-OK-identical-file silent success)
sounds like it needs a positive engineering fix.
**How to avoid:** It doesn't. Measured this session: `uv build` from the current, byte-identical-to-
`v0.9.6` tree produces a wheel and sdist whose sha256 **do not match** PyPI's served hashes for
`typsphinx-0.9.6-py3-none-any.whl` / `.tar.gz` (see "Reproducibility" below for the actual hashes).
The rehearsal's upload is guaranteed to hit the "content differs" branch regardless of whether
MSG-06 has landed on the dispatch ref yet. No mitigation needed; only a pre-dispatch confirmation
step (documented below) to *record* this as evidence rather than assume it.
**Warning signs:** A plan task that tries to pin build timestamps or otherwise "fix" reproducibility
— that would be solving a problem that does not exist here and is out of scope.

### Pitfall 3: Instantiating a full `SphinxTestApp` for MSG-06's test
**What goes wrong:** Unnecessary complexity and a slower test; also risks accidentally exercising
code paths (e.g. `writer.py`'s wrapper rendering) that belong to the sibling MSG-04 gate, muddying
"asserts only on strings this module itself emits" (the convention all four `*_path_quoting_gate.py`
siblings state explicitly in their module docstrings).
**Why it happens:** Every other `test_*_path_quoting_gate.py` sibling in this family (`writer`,
`builder`, `template_registry`) drives its target through a `temp_sphinx_app` fixture, so it is easy
to assume this one should too.
**How to avoid:** `_compute_relative_include_path()` and `_compute_relative_image_path()` are
already unit-tested by direct instantiation in `tests/test_nested_toctree_paths.py` — neither method
body touches `self` at all. Follow that file's `TypstTranslator(mock_document, mock_builder)`
pattern instead of the sibling gates' `temp_sphinx_app` pattern.
**Warning signs:** A new test file importing `SphinxTestApp` or using the `temp_sphinx_app` fixture
for MSG-06 when a plain translator instantiation would do.

### Pitfall 4: Believing `ci.yml`'s green run alone proves `validate`'s gate would pass
**What goes wrong:** Dispatching `CI` on the milestone branch and treating a green run as full proof
that `release.yml`'s `validate` job will also pass, then being surprised by a `validate` failure that
consumes the one allowed dispatch (D-01/constraint 6) before ever reaching the OIDC exchange.
**Why it happens:** `ci.yml`'s `lint`/`type-check`/`test` jobs run the *same* underlying commands as
`validate` (`tox -e lint` = `black --check .` + `ruff check .`; `tox -e type` = `mypy typsphinx/`;
`tox -e py312`/`py313` = `pytest tests/`, confirmed this session by reading `tox.ini`), so it is easy
to assume full coverage.
**How to avoid:** `ci.yml` has **no** equivalent of `validate`'s two release-specific steps: the
`pyproject.toml`-version-vs-tag-input check, and
`uv run python scripts/extract_changelog_section.py "$VERSION"`. Both were run locally this session
against the current tree (pyproject.toml reads `0.9.6`, tag input for the rehearsal is `v0.9.6`, and
`extract_changelog_section.py 0.9.6` exits 0 and prints the curated section) — confirming they will
pass, but a CI dispatch alone does not prove it. The plan should dispatch `CI` (workflow name
confirmed via `gh workflow list`: `"CI"`, id `197370967`) **and** run the two local checks, both
pre-dispatch.
**Warning signs:** A plan step that dispatches `CI` and calls it sufficient without also running
the version-match and CHANGELOG-section checks directly.

## Code Examples

### MSG-06 — exact fix and test design

**Discovery grep (SC#5's "zero remaining" claim, pre-fix state):**
```bash
$ grep -n "logger.debug\|up_path='" typsphinx/translator.py
5052: logger.debug(   # "Computing relative include path: target=..."           -- unquoted, identifier
5059: logger.debug(f"No current document, using absolute path: {target_docname}")  -- unquoted
5066: logger.debug(    # "Path components: current_dir=..., target_path=..."    -- unquoted
5072: logger.debug(    # "Current document is in root directory, using absolute path"
5082: logger.debug(    # "Same directory reference: ... result: ..."            -- unquoted
5089: logger.debug(    # "Cross-directory reference detected..."                -- no values
5104: logger.debug(    # "Common parent depth: ..., current_parts=..., target_parts=..."
5119: logger.debug(    # THE SITE -- "Cross-directory path calculation: up_count=...,
5121:     f"up_path='{up_path}', down_path='{down_path}', "                     -- HARDCODED QUOTES
5127: def _compute_relative_image_path(...
5157: logger.debug(    # mirror of :5052
...
5224: logger.debug(    # THE SITE (image variant) -- mirror of :5119
5226:     f"up_path='{up_path}', down_path='{down_path}', "                     -- HARDCODED QUOTES
```
Every other `logger.debug()` call in both functions interpolates without any hardcoded delimiter
(`f"current_dir={current_dir}, ..."` etc. — bare, not `'...'`-wrapped), so the two sites at `:5121`
and `:5226` are the **only** two hardcoded-delimiter path fragments in either function, confirming
SC#5's zero-remaining grep is satisfiable by exactly these two substitutions.

**Exact pre-fix and post-fix message text**, computed by hand-tracing the actual function body (both
functions are structurally identical; shown here for `_compute_relative_include_path`) against a
recommended fixture:

```python
current_docname = "chapter1/doc1"
target_docname = "chapter2/o'brien"
```
Trace: `current_dir = PurePosixPath("chapter1")`; `current_dir != "."` so the root-shortcut does not
fire; `target_path.relative_to(current_dir)` raises `ValueError` (chapter2 vs chapter1) so the
cross-directory branch fires; `current_parts = ("chapter1",)`, `target_parts = ("chapter2", "o'brien")`;
`common_length = 0` (first components differ); `up_count = 1`, `up_path = "../"`;
`down_parts = ("chapter2", "o'brien")`, `down_path = "chapter2/o'brien"`;
`relative_path = "../chapter2/o'brien"`.

- **Pre-fix message** (the hardcoded-delimiter f-string, `:5119-5123` verbatim substituted):
  `"Cross-directory path calculation: up_count=1, up_path='../', down_path='chapter2/o'brien', result: ../chapter2/o'brien"`
  — note the embedded apostrophe in `o'brien` closes the `down_path='...'` delimiter one character
  early; the text `brien',` then reads as unquoted trailing content. This is the defect MSG-06 fixes.
- **Post-fix message** (using `quote_path()`'s own documented rule, read from `pathfmt.py` this
  session: no apostrophe → wrap in `'...'`; apostrophe present, no `"` → wrap in `"..."`):
  `quote_path("../")` → `'../'` (no apostrophe in value). `quote_path("chapter2/o'brien")` → the
  value contains `'` and no `"`, so it wraps in double quotes: `"chapter2/o'brien"` (unescaped,
  per D-01's rule — the value's own characters are never touched in this branch).
  Full message: `"Cross-directory path calculation: up_count=1, up_path='../', down_path=\"chapter2/o'brien\", result: ../chapter2/o'brien"`

An equivalent fixture for `_compute_relative_image_path` (mirrors the include-path case):
`current_docname="chapter1/doc1"`, `image_uri="images/o'brien.png"` →
`up_path="../"`, `down_path="images/o'brien.png"`, same quoting behavior.

**D-04's byte-identity edge case** (documented so the test author does not mistake it for a second
RED shape): when `up_count == 0`, `up_path = ""`, and `quote_path("")` returns `''` — byte-identical
to the pre-fix hardcoded `f"up_path='{up_path}'"` when `up_path` is empty. **A RED assertion must be
driven by the `down_path` carrying the literal `'`, not by testing the empty-`up_path` shape**, which
would stay green (unchanged) both before and after the fix and prove nothing.

**Recorded-RED format to mirror** — Phase 60's MSG-04 sibling (`writer.py`, the same "caplog DEBUG
read" observable shape) recorded its RED like this
(`.planning/milestones/v0.9.1-phases/60-.../60-03-EVIDENCE.md:37-52`, read this session):
```
Command: `uv run pytest tests/test_writer_path_quoting_gate.py -q` (plan base SHA <sha>,
before `typsphinx/writer.py` was edited).
<pytest FAILED output, showing the AssertionError with the actual message vs. expected>
```
MSG-06's own evidence file should follow this exact shape: run the new test module against the
phase-base SHA (before `translator.py` is edited), capture the failure, then the green re-run after.
Phase 60's own consolidated evidence document
(`60-PATH-QUOTING-EVIDENCE.md`, D-10 precedent) is also the format D-08 (this phase) already follows
— a single fixed-name evidence file, not a per-plan `*-VERIFICATION.md`.

### ATT-01 — the exact edit, re-measured this session

```
$ grep -c 'PYPI_API_TOKEN' .github/workflows/release.yml   # 2 (base)
$ grep -c 'attestations' .github/workflows/release.yml     # 0 (base)
$ grep -c 'skip-existing' .github/workflows/release.yml    # 0 (base)
$ git diff origin/main -- .github/workflows/release.yml    # empty (0 lines) -- branch == main here
```
`release.yml:141-144` verbatim (confirmed via `Read`, this session):
```
141:      - name: Publish to PyPI                          <- KEEP
142:        uses: pypa/gh-action-pypi-publish@release/v1    <- KEEP
143:        with:                                           <- DELETE
144:          password: ${{ secrets.PYPI_API_TOKEN }}       <- DELETE
```
After the two-line deletion, `PYPI_API_TOKEN`'s count goes from 2 to 1 (the remaining occurrence is
`:244`'s `TEST_PYPI_API_TOKEN`, which contains the substring — untouched, `publish-testpypi`'s own
credential stays). YAML-parses cleanly both before and after
(`uv run python -c "import yaml; yaml.safe_load(open('.github/workflows/release.yml'))"` → `YAML OK`,
confirmed this session; `pyyaml` is present transitively even though no direct `pip show`/plain
`python -c "import yaml"` sees it outside `uv run`).

### Reproducibility — the measurement that resolves Q1

```
$ git diff v0.9.6 HEAD --stat -- typsphinx/     # empty -- current tree == v0.9.6 tag, byte-for-byte
$ env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv build --out-dir /tmp/build1
$ sha256sum /tmp/build1/*.whl /tmp/build1/*.tar.gz
d344116e...  typsphinx-0.9.6-py3-none-any.whl
f4d69265...  typsphinx-0.9.6.tar.gz
$ env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv build --out-dir /tmp/build2   # second, independent build
$ sha256sum /tmp/build2/*.whl /tmp/build2/*.tar.gz
d344116e...  typsphinx-0.9.6-py3-none-any.whl   # SAME as build1 -- wheel is locally reproducible
b4835d02...  typsphinx-0.9.6.tar.gz             # DIFFERENT from build1 -- sdist is NOT reproducible

PyPI's served hashes for v0.9.6 (Simple JSON API, captured this session):
  wheel: 0289f1adcd361dd773cc0c89d9abe874b8dd6c7ed74ce042bb6bb23e98c5b7c1
  sdist: 74d588b465895f68d041d7376f39fc203f8754aa4ab893a337552f3dc5f07ce8
```
Neither local rebuild's wheel (`d344116e...`) nor either rebuild's sdist (`f4d69265...`/`b4835d02...`)
matches PyPI's served hash. Diagnosis: the wheel's zip entries carry a normalized epoch timestamp
(`1980-01-01`, confirmed by inspecting `zipfile.ZipFile(...).infolist()`), so two *local* builds
match each other — but the wheel's `dist-info/WHEEL` metadata embeds
`Generator: setuptools (84.0.0)` (this session's locally-resolved setuptools version), which almost
certainly differs from whatever `setuptools`/`uv` version the original 2026-09-22 GitHub Actions run
resolved (unpinned beyond `setuptools>=65.0` in `pyproject.toml`'s `[build-system]`). The sdist's
gzip header embeds a **real, non-normalized mtime** (confirmed: two local builds 30 seconds apart
produced different gzip headers, `h\xfa\xb8j` vs. a different byte sequence) — so the sdist is
guaranteed to differ from the original on **every** rebuild, independent of any content change.
`SOURCE_DATE_EPOCH` is not set anywhere in this repo or `release.yml` (confirmed:
`grep -rn "SOURCE_DATE_EPOCH" .` finds nothing).

**Conclusion, stated plainly for the plan:** the rehearsal's rebuild is guaranteed to differ in
content-hash from the originally-published `v0.9.6` wheel and sdist, for reasons that hold
regardless of whether MSG-06's `translator.py` edit has landed on the dispatch ref. This rules out
warehouse's "identical file, 200 OK, silent success" branch (confirmed from warehouse's own source
below) and guarantees the "filename exists, content differs, 400 Bad Request" branch instead — the
outcome SC#2/ATT-02 actually requires. **Recommended pre-dispatch guard for the plan:** build
locally (or `gh run download` the `dist-packages` artifact once `build` completes for the rehearsal
run) and `sha256sum` it against the Simple JSON API's served `hashes.sha256` for `typsphinx-0.9.6-*`
— confirm mismatch — and record both hash sets in `76-ATT-EVIDENCE.md` as the positive proof this
reasoning predicted correctly, rather than asserting the outcome from this research alone.

### PyPI's duplicate-file logic, verbatim from source

`[CITED: raw.githubusercontent.com/pypi/warehouse/main/warehouse/forklift/legacy.py]`, read this
session:
```python
def _is_duplicate_file(db_session, filename, hashes):
    """
    Check to see if file already exists, and if it's content matches.
    A file is considered to exist if its filename *or* blake2 digest are
    present in a file row in the database.

    Returns:
    - True: This file is a duplicate and all further processing should halt.
    - False: This file exists, but it is not a duplicate.
    - None: This file does not exist.
    """
    file_ = (
        db_session.query(File)
        .filter(
            (File.filename == filename)
            | (File.blake2_256_digest == hashes["blake2_256"])
        )
        .first()
    )
    if file_ is not None:
        return (
            file_.filename == filename
            and file_.sha256_digest == hashes["sha256"]
            and file_.blake2_256_digest == hashes["blake2_256"]
        )
    return None
```
And its caller:
```python
is_duplicate = _is_duplicate_file(request.db, filename, file_hashes)
if is_duplicate:
    request.tm.doom()
    return HTTPOk()                              # <-- the branch this phase must NOT reach
if is_duplicate is not None:
    request.metrics.increment("warehouse.upload.failed", tags=["reason:duplicate-file"])
    raise _exc_with_message(
        HTTPBadRequest,
        "File already exists "
        f"({filename!r}, with blake2_256 hash {file_hashes['blake2_256']!r})."
        " See " + request.help_url(_anchor="file-name-reuse") + " for more information.",
    )
```
This confirms: filename-collision + identical hash → `HTTPOk()` (200, nothing written — the risky
branch); filename-collision + different hash → `HTTPBadRequest` with a message containing the
literal substring `File already exists` (SC#2's `400`/`File already exists` reading is grep-able
directly against this text, once `twine` surfaces it — twine renders server error bodies via its
own `HTTPError`/response-print path; the message text itself, including `File already exists`, is
confirmed present verbatim in the response body regardless of twine's own wrapper formatting).

### The OIDC exchange and attestation order, verbatim from source

`[CITED: raw.githubusercontent.com/pypa/gh-action-pypi-publish/release/v1/twine-upload.sh]`,
read this session (full file read; the load-bearing excerpt):
```bash
[[ "${INPUT_USER}" == "__token__" && -z "${INPUT_PASSWORD}" ]] \
    && TRUSTED_PUBLISHING=true || TRUSTED_PUBLISHING=false
...
if "${TRUSTED_PUBLISHING}" ; then
    echo "::debug::Authenticating to ${INPUT_REPOSITORY_URL} via Trusted Publishing"
    INPUT_PASSWORD="$(python /app/oidc-exchange.py)"      # <-- STEP 1: OIDC exchange (PyPI token)
...
fi
...
if [[ ${INPUT_VERIFY_METADATA,,} != "false" ]] ; then
    twine check ${INPUT_PACKAGES_DIR%%/}/*                # <-- STEP 2: local metadata check
fi
...
if [[ ${INPUT_ATTESTATIONS,,} != "false" ]] ; then
    echo "::notice::Generating and uploading digital attestations"
    python /app/attestations.py "${INPUT_PACKAGES_DIR%%/}"  # <-- STEP 3: Sigstore sign (Fulcio+Rekor)
    TWINE_EXTRA_ARGS="--attestations $TWINE_EXTRA_ARGS"
fi
...
exec twine upload ${TWINE_EXTRA_ARGS} ${INPUT_PACKAGES_DIR%%/}/*   # <-- STEP 4: actual upload
```
**Order confirmed: OIDC token exchange (step 1) → `twine check` (step 2) → attestation generation
(Sigstore signing, step 3) → `twine upload` (step 4).** This has two consequences for the plan:

1. **If registration is wrong (`invalid-publisher`), the process dies inside step 1
   (`oidc-exchange.py`'s own `die()` call, which prints the error and `sys.exit(1)`), *before*
   `attestations.py` ever runs.** No Sigstore signing, no Rekor entry, nothing reaches PyPI at all
   in this failure mode — the cheapest possible failure.
2. **If registration is correct (the desired rehearsal outcome, SC#2), step 3 DOES run and DOES
   create a permanent, public Sigstore artifact for both rebuilt `v0.9.6` files — a Fulcio
   short-lived signing certificate (itself logged to a public Certificate Transparency log) and a
   Rekor transparency-log entry — BEFORE the subsequent `twine upload` is even attempted, and
   regardless of whether that upload is later accepted or rejected as a duplicate.** This is an
   outward-facing, permanent side effect that is not "reaching PyPI" (PyPI's own served state is
   unaffected — SC#3) but is also not nothing: a public, permanent, third-party (Sigstore) record
   that this repository's `release.yml` signed a `typsphinx-0.9.6` wheel and sdist on the rehearsal
   date, attributable to the GitHub Actions run's OIDC identity. **The plan should state this
   plainly in `76-ATT-EVIDENCE.md`** rather than let it pass unremarked — it is the actual "cost" of
   getting the SC#2-required duplicate-rejection outcome (as opposed to an `invalid-publisher`
   failure, which has no such cost but also doesn't prove anything).

**`invalid-publisher` error text**, confirmed from `oidc-exchange.py`'s own source
(`_SERVER_REFUSED_TOKEN_EXCHANGE_MESSAGE`, read this session):
```
Token request failed: the server refused the request for the following reasons:

* `invalid-publisher`: <description from PyPI's JSON response>
```
The `code` value (`invalid-publisher` / `invalid-pending-publisher`) is rendered verbatim from
PyPI's JSON `errors[].code` field, so `grep -c 'invalid-publisher'` and
`grep -c 'invalid-pending-publisher'` against `gh run view --log` output are reliable, literal
greps — unlike the `attestations input ignored` case above, these two strings genuinely appear in
the rendered log body when they occur.
`[CITED: raw.githubusercontent.com/pypa/gh-action-pypi-publish/release/v1/oidc-exchange.py]` for the
mechanism; the exact PyPI-side wording of `invalid-publisher` vs. `invalid-pending-publisher`
(a valid token with no matching publisher, vs. a valid token for an already-created project that
only has a *pending* publisher registered) is `[CITED: WebSearch, cross-referencing
github.com/pypi/warehouse issues #20504 and #14389]` — since `typsphinx` is an existing, already-
published project (not a first-time publish via a pending publisher), a registration mismatch here
should surface as `invalid-publisher`, not `invalid-pending-publisher`; CONTEXT's D-07 already
treats both identically for recovery purposes, so this distinction does not change the plan.

### `gh` mechanics measured this session

```
$ gh run view 35730551619 --json jobs --jq '.jobs[] | {name, conclusion, startedAt, completedAt}'
# Exact job names (verbatim, for the plan's evidence-transcription step):
"Validate Release"                  success  12:59:22Z -> 13:03:31Z
"Build Distribution"                success  13:03:35Z -> 13:03:54Z
"Publish to PyPI"                   success  13:46:41Z -> 13:46:57Z
"Publish to TestPyPI (Optional)"    skipped  13:03:55Z -> 13:03:54Z
"Create GitHub Release"             success  13:47:00Z -> 13:47:19Z

$ gh run list --workflow=release.yml --limit 20 --json databaseId,createdAt,event,headBranch,headSha,status,conclusion
# Most recent entry (the baseline the D-01 before/after read compares against):
{"databaseId":35730551619,"createdAt":"2026-09-22T12:59:20Z","event":"push","headBranch":"v0.9.6", ...}
# No entry yet for gsd/v0.9.7-trusted-publishing-and-release -- confirms zero prior dispatches on
# this ref, so the wave-2 D-01 baseline read will show this same most-recent entry until the
# rehearsal fires.

$ gh api repos/YuSabo90002/typsphinx/actions/runs/35730551619/pending_deployments
[]   # empty for a completed run, as expected -- this endpoint is the one to poll mid-run for
     # {"environment":..., "current_user_can_approve":..., "reviewers":[...], "wait_timer":15,
     #  "wait_timer_started_at":...} while status is "waiting" [CITED: GitHub REST API docs shape]

$ gh run rerun --help
# "Rerun an entire run, only failed jobs, or a specific job from a run." Operates on the SAME
# run id / SAME commit SHA -- confirms D-07's premise. Use `gh run view <id> --json jobs
# --jq '.jobs[] | {name, databaseId}'` to get the databaseId needed for `--job` (NOT the URL's
# job number, which 404s).

$ git ls-remote --heads origin | grep -i "v0.9.7\|trusted"
# (empty) -- gsd/v0.9.7-trusted-publishing-and-release has NO upstream yet, confirmed via both
# `git branch -vv` (no `[origin/...]` tracking ref shown) and this direct remote probe.

$ gh api repos/YuSabo90002/typsphinx/rulesets
[]   # no repository rulesets configured -- nothing here blocks the milestone-branch push or the
     # workflow_dispatch beyond the already-known `pypi` environment protection rules.

$ gh api repos/YuSabo90002/typsphinx/environments/pypi
# protection_rules: required_reviewers (YuSabo90002, prevent_self_review:false), wait_timer:15
# deployment_branch_policy: null  -- confirms D-06's premise that a non-default-branch dispatch
# still reaches this environment.

$ gh secret list                 # PYPI_API_TOKEN, TEST_PYPI_API_TOKEN (repo scope)
$ gh secret list --env pypi      # PYPI_API_TOKEN (env scope)
$ gh secret list --env testpypi  # (empty -- TEST_PYPI_API_TOKEN is repo-scope only)
# Confirms ROADMAP constraint 11's "two distinct PYPI_API_TOKEN secrets" and that this phase
# touches neither (ATT-05 is Phase 77/complete-milestone's job).
```

**Polling within Bash's 600s ceiling (D-02):** neither `gh run watch` (blocking, no built-in
sleep/retry escape hatch matching D-02's two-stage wait) nor a single long foreground command is
viable across a wait that can legitimately run past 600s (D-04's 90-minute bound). Recommended
pattern for the plan: either (a) launch `gh run watch <id> --exit-status` via `run_in_background`
and separately poll its completion, or (b) a bounded loop of short `gh run view <id> --json status`
calls (each well under 600s) with a sleep between iterations, checked against elapsed wall-clock
time against the 90-minute D-04 bound on each iteration.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|---------------|--------|
| Password/API-token-based PyPI upload (`password: ${{ secrets.PYPI_API_TOKEN }}`) | OIDC Trusted Publishing (`pypa/gh-action-pypi-publish@release/v1` with no `password:`) | PyPI added Trusted Publishing support in 2023; this repo has carried the token-based path since its first release and switches with this phase | Enables PEP 740 attestations (provenance, ATT-03/ATT-04) automatically; removes the long-lived secret as an attack surface (ATT-05 retires it once ATT-03 passes, in Phase 77). |
| `!r`-conversion (bare `repr()`) for path-valued DEBUG-log interpolations | `quote_path()` (delimiter-aware, no backslash-doubling) | Introduced Phase 60 (MSG-02), routed into `builder.py`/`writer.py`/`template_registry.py`; MSG-06 is the fourth and last module | Prevents both a doubled-backslash misrepresentation on Windows-shaped paths and an early-closing quote on a path containing a literal apostrophe. |

**Deprecated/outdated:**
- Hardcoded `f"key='{value}'"` interpolation for any path-valued log message in this codebase — the
  whole MSG-02 family (Phase 60 + this phase's MSG-06) exists to eliminate the last four instances
  of this pattern.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Twine's rendered output for a 400 duplicate-file response reliably includes the literal substrings `400` and `File already exists` in a form `gh run view --log` captures, matching SC#2's grep target. | "PyPI's duplicate-file logic, verbatim from source" | LOW — warehouse's own `HTTPBadRequest` message contains `File already exists` verbatim (confirmed from source), and twine's generic `HTTPError` printer includes the response status code; the exact surrounding formatting (e.g. whether `400` appears as `400 Client Error` or embedded elsewhere) was not observed on a live failing run this session (no such run exists yet — the rehearsal itself is what will produce it). If twine's wrapper text differs from expectation, the plan's grep should be widened to `grep -i 'File already exists'` alone, which is the more robust, confirmed-verbatim target. |
| A2 | On an `invalid-publisher` rejection, `gh run rerun <id>` (whole run) or `gh run rerun <id> --job <publish-pypi-databaseId>` re-runs against the same commit SHA and reuses the already-uploaded `dist-packages` artifact (within its 7-day retention) rather than requiring `build` to re-run. | "`gh` mechanics measured this session" | LOW/MEDIUM — confirmed via `gh run rerun --help`'s description ("Rerun ... a specific job ID from a run, including dependencies") and standard GitHub Actions job-rerun semantics (a job whose dependency already succeeded is not automatically re-triggered), but not directly observed against a real failed run in this repo this session, since no failure has occurred yet. |
| A3 | `softprops/action-gh-release@v3`, if it ran against an already-existing `v0.9.6` release (the hypothetical the "identical-hash 200 OK" branch would enable), would either update the existing release's body/assets or fail with an `already_exists` validation error — not silently no-op. | Summary / "System Architecture Diagram" annotation | LOW — this branch is now proven unreachable (measured hash mismatch, see "Reproducibility"), so this assumption is moot for the actual rehearsal; it is recorded only because Q1 asked for it and because it is `[CITED: WebSearch, github.com/softprops/action-gh-release issues #45/#403/#445]` rather than a direct read of the pinned `@v3` ref's source this session. |

**If this table is empty:** N/A — see rows above; none of the three risks changes the plan's
recommended actions, since A1's fallback grep is already the stronger recommendation, A2's mechanism
is only invoked in the already-HALT-and-defer-to-owner D-07 path, and A3's branch is proven
unreachable by direct measurement.

## Open Questions

1. **Exact twine-rendered text for the 400 rejection, in this specific run.**
   - What we know: warehouse's server-side message text, verbatim (see Code Examples above).
   - What's unclear: twine's exact wrapper formatting around that server message in `gh run view
     --log` output — cannot be observed until the rehearsal actually runs.
   - Recommendation: the plan's D-08 evidence step should transcribe the **actual** verbatim failing
     lines from the real rehearsal run (as D-08 already requires) rather than pre-committing to an
     exact expected string; use `grep -i 'File already exists'` as the primary discriminator (see A1).

2. **Whether PyPI's warehouse checks duplicate-file status before or after verifying the uploaded
   PEP 740 attestation's own validity.**
   - What we know: the client-side order is OIDC exchange → attestation generation → upload (all
     confirmed from `twine-upload.sh`'s source, read this session).
   - What's unclear: warehouse's server-side internal ordering of attestation validation vs.
     `_is_duplicate_file()` was not read this session (out of scope for `legacy.py`'s excerpt
     fetched).
   - Recommendation: does not matter for this phase — since content-hash mismatch is guaranteed
     (measured), the duplicate-file check will reject the upload regardless of where in warehouse's
     pipeline it sits relative to attestation verification.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `gh` (GitHub CLI) | ATT-02's dispatch, watch, and evidence capture | ✓ | 2.101.0 (nixpkgs) | — |
| `uv` | `uv build` pre-dispatch guard, all `uv run` invocations (worktree isolation, per CLAUDE.md) | ✓ | 0.12.13 | — |
| `curl` | ATT-02's Simple JSON API capture, PyPI served-state baseline | ✓ | (system) | — |
| `python3` / `jq` | JSON extraction from `curl` output | ✓ (both present: `python3` at `/nix/store/.../python3-3.13.13/bin/python3`, `jq` at `/etc/profiles/per-user/yuta/bin/jq`) | — | Prefer `python3 -c "import json; ..."` for parity with the rest of this repo's tooling (no `jq` dependency declared elsewhere) |
| Network access to `pypi.org`, `github.com` API | ATT-02's rehearsal, Simple JSON / release reads | ✓ (confirmed this session — all `curl`/`gh api` calls succeeded) | — | — |
| PyPI-side Trusted Publisher registration | ATT-02's dispatch (prerequisite, D-05) | **✗ as of 2026-09-27** | — | **No fallback — owner action, off-repo, blocks the wave-2 dispatch task until done.** |

**Missing dependencies with no fallback:**
- The PyPI-side Trusted Publisher registration (D-05's owner prerequisite). No plan task may claim
  or work around this.

**Missing dependencies with fallback:**
- None beyond the registration item above.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 9.1.1 (per `pyproject.toml`'s `[tool.pytest.ini_options]`; version observed in a prior session's `60-03-EVIDENCE.md` transcript, this session's own runs were not executed against the worktree's own venv — see note below) |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]` (`:79-96`) |
| Quick run command | `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev && uv run pytest tests/test_translator_path_quoting_gate.py -q` (worktree-isolated, per CLAUDE.md § Worktree-isolated execution — **mandatory**, not optional, per that file's standing-mode language) |
| Full suite command | `uv run pytest tests/ -v` (mirrors `release.yml`'s own `validate` job step, and `tox -e py312`/`py313`) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| ATT-01 | `release.yml` still parses as YAML, credential removed, no replacement key added, `publish-testpypi` byte-identical | static/grep + YAML-parse (not pytest) | `grep -c 'PYPI_API_TOKEN' .github/workflows/release.yml` (expect 1); `grep -c 'attestations'`/`grep -c 'skip-existing'` (expect 0 each); `uv run python -c "import yaml; yaml.safe_load(open('.github/workflows/release.yml'))"` | N/A — no new test file, these are direct shell/YAML checks the plan runs and transcribes |
| ATT-02 | Rehearsal reaches `Publish to PyPI`, rejected as duplicate not unknown-publisher; nothing reached PyPI; disabling-annotation absent (control non-zero) | external/manual-observation (a live `gh` dispatch, cannot be simulated locally) | `gh workflow run release.yml --ref <branch> -f tag=v0.9.6` + the full `gh run view`/`curl`/`gh release view` sequence documented above | N/A — this requirement is proven by a single, irreversible, external run; there is no pytest node for it |
| MSG-06 | A literal `'` in a cross-directory `down_path` no longer closes the log's quote early, for both `_compute_relative_include_path` and `_compute_relative_image_path` | unit (caplog DEBUG read) | `uv run pytest tests/test_translator_path_quoting_gate.py -q` | ❌ — new module, Wave 0/1 gap (this phase's own plan creates it; MSG-06 IS the wave-1 work) |

### Sampling Rate

- **Per task commit:** `uv run pytest tests/test_translator_path_quoting_gate.py -q` (MSG-06's own
  test, fast) and, for the ATT-01 wave-1 task, the grep/YAML-parse triplet above.
- **Per wave merge:** `uv run pytest tests/ -v` (full suite, so MSG-06's new test coexists cleanly
  with the untouched sibling `*_path_quoting_gate.py` modules and with
  `tests/test_nested_toctree_paths.py`'s existing value-only assertions, which must stay green and
  unchanged — MSG-06 only adds a DEBUG-message assertion, it does not change either function's
  return value).
- **Phase gate:** Full suite green before `/gsd-verify-work`; separately, wave 2's `gh`-based
  external observations (ATT-02) are the phase's actual acceptance oracle for that requirement and
  cannot be "sampled" — they are a single, one-shot, irreversible dispatch per D-01.

### Wave 0 Gaps

- [ ] `tests/test_translator_path_quoting_gate.py` — new module, MSG-06's own RED-then-GREEN gate,
      following the naming convention of its three siblings (`test_writer_path_quoting_gate.py`,
      `test_builder_path_quoting_gate.py`, `test_template_registry_path_quoting_gate.py`) and the
      direct-instantiation construction of `tests/test_nested_toctree_paths.py` (no new fixture file
      needed — `mock_document`/`mock_builder` can be locally defined in the new module, mirroring
      the existing sibling gates' own locally-defined fixtures rather than importing shared ones).
- [ ] Framework install: none — pytest/uv/tox are already fully provisioned per `pyproject.toml`'s
      `dev` extra; only the worktree's own `uv sync --extra dev` (CLAUDE.md-mandated) is needed.

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-------------------|
| V2 Authentication | yes (workflow-level, not app-level) | OIDC short-lived token exchange replaces a long-lived static credential — the entire point of ATT-01/ATT-02; PyPI's own `_/oidc/mint-token` endpoint performs the actual authentication decision, out of this repo's control. |
| V3 Session Management | no | Not applicable — this is a one-shot CI/CD token exchange, not a user session. |
| V4 Access Control | yes | The `pypi` GitHub environment's `required_reviewers` + `wait_timer` protection rules are the access-control gate on who can let a run reach the credential-minting step; unchanged by this phase (already configured, `deployment_branch_policy: null` confirmed this session). |
| V5 Input Validation | yes (narrow) | `release.yml`'s own `env:`-not-interpolation invariant (documented in the file's own comments, `:38-44`) — every `${{ }}` value used inside a `run:` block is passed through `env:` first, never interpolated directly into the bash script body, precisely to prevent a malicious tag/branch name from executing as shell code in a job holding `contents: write`/`id-token: write`. Neither this phase's ATT-01 edit nor MSG-06 touches any `run:` block that interpolates a `${{ }}` value, so this invariant is preserved by construction — but the plan's verification step for ATT-01 should explicitly re-confirm (grep for `${{ }}` inside any `run:` block) that the two-line deletion did not accidentally introduce one. |
| V6 Cryptography | yes (delegated) | Sigstore's Fulcio (short-lived X.509 cert issuance) and Rekor (transparency log) — entirely inside `pypa/gh-action-pypi-publish`'s own container, never hand-rolled by this repo; this repo only opts in by removing `password:`. |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|----------------------|
| Long-lived PyPI API token leakage (the exact problem ATT-01 addresses) | Information Disclosure / Elevation of Privilege | Replace with OIDC short-lived token exchange (this phase); until ATT-05 (Phase 77), the token remains as an explicit, deliberate rollback path — not an oversight. |
| Malicious tag/branch name achieving shell injection via `${{ }}`-in-`run:` | Tampering | `release.yml`'s existing `env:`-not-interpolation invariant (unchanged by this phase; re-verify it after the ATT-01 edit as noted above). |
| A second, silent `workflow_dispatch` from an HTTP 5xx retry, breaking the "exactly one dispatch" invariant that ATT-02's evidence depends on | Repudiation (of which run is authoritative) | D-01's mandatory before/after `gh run list` diff, with **no retry permitted** until that diff has been read — already locked in CONTEXT. |
| Accidental identical-hash "silent success" upload creating an unintended, un-audited PyPI/GitHub-Release state | Tampering / Repudiation | Measured this session to be structurally unreachable (see "Reproducibility") — no code-level mitigation needed; the plan's job is to *record* the pre-dispatch hash-mismatch confirmation as positive evidence, not to build a guard against a risk that cannot occur here. |
| Permanent, public Sigstore/Rekor entry created for a *rehearsal* (non-production) build, attributable to this repository | Information Disclosure (of build provenance metadata, not secrets) | Not a vulnerability — Sigstore/Rekor entries are designed to be public by construction — but it is a real, permanent, third-party side effect that the plan must document plainly in `76-ATT-EVIDENCE.md` rather than characterize as "nothing reached PyPI" without qualification (SC#3's "nothing reached PyPI" is about PyPI's *served state*, not about every external system the action touches). |

## Sources

### Primary (HIGH confidence — direct measurement this session, or direct read of authoritative source)
- `gh run view 35730551619 --log` / `--json jobs` — the v0.9.6 production release run, full log and
  job timing, read this session.
- `gh api repos/YuSabo90002/typsphinx/environments/pypi` — the `pypi` environment's protection rules
  and branch policy, read this session.
- `gh api repos/YuSabo90002/typsphinx/rulesets`, `.../branches/main/protection` — repository ruleset
  and branch-protection state, read this session.
- `curl -s https://pypi.org/simple/typsphinx/ -H 'Accept: application/vnd.pypi.simple.v1+json'` —
  full served file list (38 files), captured this session.
- `gh release view v0.9.6 --json assets,name,body,tagName,isDraft,isPrerelease` — captured this
  session (3 assets: wheel, sdist, `typsphinx.pdf`).
- `typsphinx/translator.py`, `typsphinx/pathfmt.py`, `tests/test_nested_toctree_paths.py`,
  `tests/test_writer_path_quoting_gate.py`, `tests/test_builder_path_quoting_gate.py`,
  `tests/test_template_registry_path_quoting_gate.py`, `tests/conftest.py`, `.github/workflows/release.yml`,
  `.github/workflows/ci.yml`, `tox.ini`, `pyproject.toml` — all read directly this session.
- `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv build` (twice, independently) + `sha256sum` — the
  local reproducibility measurement, this session.
- `raw.githubusercontent.com/pypa/gh-action-pypi-publish/release/v1/{twine-upload.sh,oidc-exchange.py,attestations.py}`
  — full file reads via `mcp__tavily__tavily_extract`, this session; `release/v1` resolved to commit
  `dc37677b2e1c63e2034f94d8a5b11f265b73ba33` via `gh api .../commits/release/v1`.
- `raw.githubusercontent.com/pypi/warehouse/main/warehouse/forklift/legacy.py` — `_is_duplicate_file`
  and its caller, read via `WebFetch` this session.
- `.planning/milestones/v0.9.1-phases/60-.../60-PATH-QUOTING-EVIDENCE.md`,
  `60-03-EVIDENCE.md` — Phase 60's own recorded-RED evidence format, read this session as the
  format to mirror.

### Secondary (MEDIUM confidence — WebSearch cross-referencing official/authoritative discussion)
- `github.com/pypi/warehouse` issues #20504, #14389 — `invalid-publisher` vs.
  `invalid-pending-publisher` distinction (existing-project vs. pending-publisher-only cases).

### Tertiary (LOW confidence — WebSearch only, not verified against the pinned action version's own source this session)
- `github.com/softprops/action-gh-release` issues #45, #403, #445 — behavior on an already-existing
  release's tag; moot for this phase per the "Reproducibility" measurement, recorded only because
  the research prompt asked for it.

## Metadata

**Confidence breakdown:**
- ATT-01/ATT-02 mechanics: HIGH — every claim is either a direct `gh`/`curl`/`git`/`uv` measurement
  taken this session or a verbatim read of the action's/warehouse's own source at the currently-pinned
  ref.
- MSG-06 fix and test design: HIGH — the fix mirrors three already-shipped, already-tested sibling
  call sites verbatim; the test construction mirrors an already-existing test file
  (`tests/test_nested_toctree_paths.py`) that already exercises the exact cross-directory branch
  MSG-06 needs, just without a `caplog` assertion yet.
- The CONTEXT-contradiction finding (`'attestations input ignored'`): HIGH — reproduced twice
  (direct grep on the saved log file, with explicit exit-code confirmation) and explained by a
  verbatim read of the action's own source.

**Research date:** 2026-09-27
**Valid until:** This phase's own dispatch is one-shot and imminent — this research is valid through
that single dispatch. If the milestone branch's `typsphinx/` tree changes again before the rehearsal
fires (beyond MSG-06 landing, which this research already accounts for), the "Reproducibility"
section's specific hash values become stale (the reasoning — that sdist builds are never
reproducible and wheel-generator versions drift — does not).
