# Phase 46: v0.7.1 Release Prep (prep-only) — Release Evidence

**Filename note:** this file is deliberately **not** named `46-VERIFICATION.md`. That name is
reserved by the `/gsd-verify-work` verifier, which overwrites it wholesale when it runs — writing
this roll-up under that name would mean it gets clobbered the next time the verifier runs (D-15).
This follows the `41-RELEASE-EVIDENCE.md` precedent from the v0.7.0 release-prep phase.

This file rolls up all five ROADMAP success criteria (SC#1-SC#5) for Phase 46. It **cites** the
five sibling evidence files that already discharge SC#1 through SC#4 — quoting their own verdict
language rather than re-deriving it — and takes **fence observation 1 of 2** for SC#5 directly,
because no sibling plan owns SC#5. Observation 2 of 2 is recorded separately, at a later moment, in
`46-HANDOFF.md` § "Proof the fence held".

**Provisioning note:** all commands below were run inside this plan's isolated git worktree
(`worktree-agent-a65e6130833d01fe2`), after `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync
--extra dev`, per this project's `CLAUDE.md` § "Worktree-isolated execution". Every Python
invocation below runs through `uv run`.

**Recorded:** 2026-08-11, at HEAD `26b2e6c6fff77520f36e4ff90c165922ef7026fc` — the same commit
`46-CI-EVIDENCE.md`'s D-23 run 2 pushed and proved green.

---

## SC#1

Quoted verbatim from `.planning/ROADMAP.md` § "Phase 46: v0.7.1 Release Prep (prep-only)":

> 1. `pyproject.toml` is the sole `0.7.1` version literal, with `uv.lock` and `README.md` moved in
>    lockstep and the editable-install metadata regenerated so `typsphinx.__version__` reports
>    `0.7.1`; all three version-sync guard tests stay green.

**Evidence file:** `46-BUMP-EVIDENCE.md` (produced by plan 46-02).

**Verdict, cited verbatim from that file's own "Executed versus skipped" section:**

> **Authority for the full lint/type/py312/py313/docs matrix belongs to CI (D-11), not this plan.**
> This plan's own local scope is exactly the five version-sync guard assertions above, run and
> recorded honestly — nothing was inferred or asserted from memory.

**Figures quoted from that same file, for the record (not re-measured here):** `pyproject.toml`
line 7 moved `0.7.0` → `0.7.1`; `README.md` line 342's Status line moved in lockstep; `uv.lock`'s
`typsphinx` entry reads `version = "0.7.1"`; `uv run python -c "import typsphinx;
print(typsphinx.__version__)"` printed `0.7.1`; `uv lock --check` exited 0; the `[project]
dependencies` array is byte-identical before/after (zero dependency added or removed); and all
three version-sync guard tests (`test_version_matches_pyproject_toml`,
`test_readme_status_version_matches_pyproject`, and the three
`test_preview_version_sync.py` assertions) passed — 5 tests, `failures="0"`, `errors="0"`.

**SC#1 roll-up verdict:** **MET.** All three surfaces (`pyproject.toml`, `README.md`, `uv.lock`)
agree on `0.7.1`; the editable-install metadata was regenerated (`uv sync --extra dev --locked`);
`typsphinx.__version__` reports `0.7.1`; and all three version-sync guard tests pass with zero
failures/errors.

---

## SC#2

Quoted verbatim from `.planning/ROADMAP.md`:

> 2. `CHANGELOG.md` carries a curated `## [0.7.1]` entry covering every v1 requirement this
>    milestone delivered, which **explicitly calls out both user-visible behavioural changes
>    inside a patch release** — CONF-08's output-filename change (using Phase 44's measured
>    before/after filenames) and CONF-09's rendered title/author change (Phase 44.2, which
>    reversed Phase 44's D-02); the tail link block advances (new tag link + `Unreleased` compare);
>    and `docs/source/changelog.rst` gains the matching `0.7.1` entry in the same edit, so DOC-12's
>    page is current at the tag.

**No sibling evidence file owns this criterion** — plan 46-03 delivered the underlying change
(`46-03-SUMMARY.md`), which is cited here rather than re-measured, per this plan's own
`must_haves` instruction to cite sibling verdicts rather than re-derive them.

**Facts, drawn from `46-03-SUMMARY.md`:**

- `CHANGELOG.md` carries a `## [0.7.1] - 2026-08-11` heading (confirmed independently in
  `46-CI-EVIDENCE.md` § "D-23 run 2 — the authority run", `grep -n '^## \[0.7.1\]' CHANGELOG.md` →
  `17:## [0.7.1] - 2026-08-11`).
- The lead paragraph states plainly that "this patch release can break a working configuration"
  (confirmed in `46-REL04-EVIDENCE.md`'s Exercise 1 transcript, which quotes the extracted section
  verbatim).
- D-02's three breakage markings are present: the lead paragraph's plain statement, three
  `**Breaking:**` prefixes on the affected bullets, and a `### Removed` section for `typst_authors`
  (CONF-10).
- D-07's CONF-08 callout carries both measured facts (the before/after filenames from Phase 44's
  own `44-GATE-EVIDENCE-03.md` § 7 measurement) — the derivation change and the concrete filename
  pair it produces.
- The tail link block advances: a `[0.7.1]:` release-tag line is added and `[Unreleased]:` is
  re-pointed to compare `v0.7.1...HEAD`.
- `docs/source/changelog.rst` gains the matching `## [0.7.1]` section in the same edit (D-01's
  lockstep requirement), keeping DOC-12's published changelog page current.

**SC#2 roll-up verdict:** **MET.** The curated `## [0.7.1]` entry exists, is present in the pushed
HEAD proven green by CI (`46-CI-EVIDENCE.md`), covers this milestone's requirements with both
required breaking-change callouts (CONF-08, CONF-09) explicitly marked, the tail link block is
rolled over, and `docs/source/changelog.rst` was edited in lockstep.

---

## SC#3

Quoted verbatim from `.planning/ROADMAP.md`:

> 3. The post-bump tree is proven green **live**, not inherited: full pytest, `black`/`ruff`/
>    `mypy`, the full-corpus `-b typstpdf` gate, and both docs builds (`docs-html`, `docs-pdf`),
>    with the milestone invariants (zero new runtime dependencies; `@preview` count still four
>    with no new lockstep site) asserted mechanically over the SHA-anchored full milestone diff.

This criterion is discharged in two halves, per D-11's authority split, plus the invariant sweep
which is SC#4's own subject (cited separately below, not duplicated here).

### CI authority (D-11, D-23 run 2)

**Evidence file:** `46-CI-EVIDENCE.md` (produced by plan 46-04).

**Verdict quoted verbatim:**

> **All twelve jobs report `success`. No job reports `failure`.** This includes all six
> `{ubuntu, macos, windows} × {3.12, 3.13}` test lanes, `Lint and Format Check`, `Type Check`,
> `Code Coverage`, `Build Package`, and both `Integration Test - basic` / `Integration Test -
> advanced` jobs. `RUN_ID=31458368833` is this task's accepted D-23 run 2 evidence — no retry or
> fix was needed; the run was clean on the first dispatch.

This is D-23 run 2, dispatched against the post-bump, post-CHANGELOG commit
`26b2e6c6fff77520f36e4ff90c165922ef7026fc` (matched by `headSha`), and is the authority for the
full `{ubuntu, macos, windows} × {3.12, 3.13}` test matrix, the lint/format trio, and the type
check.

**D-23 run 1 also lives in `46-CI-EVIDENCE.md`** (run `31456868265`, commit `07b9afd`) and is what
proves D-22's Windows repair — the fix cannot be reproduced locally (backslash path rendering is
Windows `pathlib` behaviour), so a live `windows-latest` run is the only way to demonstrate it.
Both target lanes (`Test Python 3.12 on windows-latest`, `Test Python 3.13 on windows-latest`) flip
from `failure` (baseline run `31445582363`) to `success`.

### Local half

**Evidence file:** `46-GREEN-TREE-EVIDENCE.md` (produced by plan 46-04).

**Verdict quoted verbatim:**

> Per D-11's authority split (see `46-CI-EVIDENCE.md` § "Why this run is the authority"), **this
> file records no claim of authority for pytest, `black`, `ruff`, or `mypy`** — the D-23 run 2 CI
> run is the authority for those, since local never exercises Windows/macOS and
> `.venv/bin/ruff` is a generic-linux ELF the NixOS stub loader rejects (a filed, out-of-scope
> environmental defect). This file covers exactly what CI structurally does not: both docs builds,
> the full-corpus `-b typstpdf` gate, and a single `ja` build.

Figures quoted from that same file: `tox -e docs-html` and `tox -e docs-pdf` both exit 0 (`build
succeeded, 3 warnings` — the 3 warnings are the pre-existing, unrelated `visit_toctree` docstring
diagnostics); `docs/_build/pdf/typsphinx.pdf` produced, 2,452,632 bytes; the full-corpus
`-b typstpdf` gate (`tests/test_corpus_gate.py`) ran **4 passed, 1 skipped** (the one skip is the
opt-in `TYPSPHINX_CORPUS_REPORT=1` measurement, unrelated to the gate's pass/fail criterion), with
`TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error` itself PASSED against Sphinx's own
`doc/` tree; and the `ja` build (D-12) produced `docs/_build/pdf-ja/typsphinx.pdf` (2,520,348
bytes) with `lang: "ja"` confirmed present in the emitted `.typ`.

### SC#3 roll-up verdict

**MET.** Both halves are MET with no gap: the CI authority run (D-23 run 2, `31458368833`) reports
all twelve jobs `success` against the exact post-bump commit; the local half proves both docs
dogfooding builds, the full-corpus gate, and the `ja` build, all green, over the same commit. No
job or command in either evidence file is recorded as `failure` or `NOT MET`.

---

## SC#4

Quoted verbatim from `.planning/ROADMAP.md`:

> 4. REL-04's in-phase share is discharged and its remainder is explicitly owed: `release.yml`'s
>    `create-release` job is verified on `main` to carry the `astral-sh/setup-uv` + `Set up Python`
>    steps ahead of its `uv run python scripts/extract_changelog_section.py` call, and the
>    extractor is run against the new `## [0.7.1]` section producing the intended release-body
>    text. Both facts are recorded as *preconditions*, not as acceptance — the phase's own
>    artifacts state that **REL-04 remains open until a real tag push runs `create-release` to
>    completion**.

**Note on numbering:** ROADMAP's own SC#4 text is REL-04's in-phase precondition check. The
milestone-invariant sweep (zero new runtime dependencies; `@preview` count still four) is folded
into the same plan (46-05) alongside it, and both are cited here under this heading, matching
`41-RELEASE-EVIDENCE.md`'s own precedent of pairing SC#4's invariant sweep with the adjacent
requirement-precondition evidence produced by the same plan.

**Evidence files:** `46-SC4-INVARIANTS.md` (the D-21 invariant sweep) and `46-REL04-EVIDENCE.md`
(REL-04's two preconditions), both produced by plan 46-05.

**Invariant sweep verdict, quoted verbatim from `46-SC4-INVARIANTS.md`'s own roll-up table:**

| Invariant | Status | Evidence |
|---|---|---|
| 1 — zero new runtime dependencies | **PROVEN** | `[project] dependencies` byte-identical `v0.7.0` → HEAD |
| 2 — `@preview` count still four, no new lockstep site | **PROVEN** | `test_preview_version_sync.py` 3/3 passed |
| 3 — the prep-only fence over Phase 46 | **PROVEN** (via corrected reference point) | `git diff c72be91..HEAD -- typsphinx/` is empty |

**REL-04 precondition verdict, quoted verbatim from `46-REL04-EVIDENCE.md`:**

> **REL-04's acceptance evidence is a real tag push whose `create-release` job runs to completion,
> and only `/gsd-complete-milestone` can generate it.** Nothing above is that tag push — Phase 46
> is prep-only by design (no tag, no PyPI, no GitHub Release, no PR), and this plan took no
> irreversible action... **Everything recorded above is a precondition, never acceptance.**

Precondition 1 (the `create-release` job carries `astral-sh/setup-uv` + `Set up Python` ahead of
its `uv run` call, lines 162/167 of `.github/workflows/release.yml`) and Precondition 2 (the
extractor runs against the real `## [0.7.1]` section: exit 0, non-empty body, idempotent across two
invocations, exit 1 with a diagnostic on a missing section, no cross-section leakage, correct
ordering) are both confirmed present and correct.

### SC#4 roll-up verdict

**MET, with REL-04 explicitly stated open.** All three milestone invariants are PROVEN. Both of
REL-04's in-phase preconditions are verified: the workflow fix is present and undisturbed by this
phase (`git diff origin/main..HEAD -- .github/workflows/release.yml` is empty), and the extractor
behaves correctly against the real section. **REL-04 remains open** — its acceptance evidence is a
real tag push whose `create-release` job runs to completion, which only `/gsd-complete-milestone`
can generate. v0.7.0 reported this requirement's mechanism as done on the strength of a correct
workflow file, and the release then failed at exactly that job (run `30848860064`, `uv: command
not found`) — this roll-up does not repeat that error. `.planning/todos/pending/2026-08-04-release-create-job-missing-uv-verify-end-to-end.md`
stays in `todos/pending/`, and `.planning/REQUIREMENTS.md`'s REL-04 row stays `Pending`.

---

## SC#5: no irreversible action taken — the fence, observation 1 of 2

Quoted verbatim from `.planning/ROADMAP.md`:

> 5. No irreversible action was taken: `git tag -l v0.7.1` and `git ls-remote --tags origin
>    v0.7.1` are both empty at phase end, and a standalone handoff checklist exists for
>    `/gsd-complete-milestone` covering merge → tag → `release.yml` (with an explicit item to
>    observe `create-release` succeed, closing REL-04) → PyPI + GitHub Release → the second tag on
>    `typsphinx-doc-translations` → the RTD `stable` measurement on both projects.

This section records **observation 1 of 2**. Observation 2 — a second, independent probe at a
separate moment — is recorded in `46-HANDOFF.md` § "Proof the fence held".

**Timestamp:** 2026-08-11T04:46:40Z (immediately before the two probes below).

Command:
```
$ git tag -l v0.7.1
```
Verbatim output:
```
(empty)
```
Exit code: 0.

Command:
```
$ git ls-remote --tags origin v0.7.1
```
Verbatim output:
```
(empty)
```
Exit code: 0.

Both probes returned genuinely empty output (not an error) — the release workflow
(`.github/workflows/release.yml`) fires only on a `v*` tag push, so an absent tag on both the local
repository and `origin` is what makes "nothing was published" a mechanical claim.

State explicitly, for the record: no pull request has been opened or merged by this phase (D-20's
merge pulled `origin/main` in — the inbound direction — not the reverse), no package has been
uploaded to PyPI, no GitHub Release has been created, and no `git tag` command has been run against
`v0.7.1` (or any tag) anywhere in this phase's execution.

### SC#5 (observation 1) verdict

**Observation 1: EMPTY on both probes, exit 0 on both.** This is one of the two independent
observations SC#5 requires; observation 2 follows in `46-HANDOFF.md` at a separate, later moment.

---

## Phase verdict

| Success Criterion | Status | Evidence |
|---|---|---|
| SC#1 — version-literal lockstep | **PROVEN** | `46-BUMP-EVIDENCE.md` |
| SC#2 — curated `## [0.7.1]` entry, breaking-change callouts, tail link rollover | **PROVEN** | `46-03-SUMMARY.md`, cross-checked against `46-CI-EVIDENCE.md` and `46-REL04-EVIDENCE.md` |
| SC#3 — post-bump tree green, CI authority + local half | **PROVEN** | `46-CI-EVIDENCE.md` + `46-GREEN-TREE-EVIDENCE.md` |
| SC#4 — milestone invariants proven mechanically; REL-04 in-phase share discharged, remainder owed | **PROVEN** (REL-04 explicitly open — not a criterion failure, the criterion's own wording requires this) | `46-SC4-INVARIANTS.md` + `46-REL04-EVIDENCE.md` |
| SC#5 — no irreversible action, fence proven twice | **PROVEN** (observation 1 of 2 here; observation 2 in `46-HANDOFF.md`) | this file, § SC#5, and `46-HANDOFF.md` § "Proof the fence held" |

**No criterion is PARTIAL or NOT PROVEN.** SC#4's own text requires REL-04 to remain open at this
phase's close — that is not a gap in this roll-up's verdict, it is the criterion being satisfied
exactly as written.

---

## Executed versus skipped

A phase-wide list of every command this phase's own evidence files record as **not executed** or
**not authoritative locally**, gathered from each sibling file's own executed-versus-skipped
statement. A skip is not a pass — this list exists so a skip cannot silently disappear at roll-up
time.

| Command / action | Plan | Reason not executed |
|---|---|---|
| `tox -e py312` | 46-02, 46-04 | On this machine `uv venv -p cpython3.12` attempts to download a standalone CPython whose ELF the NixOS stub loader rejects (exit 127) — the environment cannot provision at all, not merely fail. The D-23 run 2 CI run already proves both `py312` and `py313` lanes green on `ubuntu-latest`, `macos-latest`, and `windows-latest`. |
| A bare `tox` (no `-e` selector) | 46-04 | `tox.ini`'s `env_list` includes `lint`, which dies at exit 127 on this machine: `.venv/bin/ruff` is a generic-linux ELF the NixOS stub loader rejects. A filed, out-of-scope environmental defect (`.planning/todos/pending/2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos.md`), not a validation gap — D-11 amendment (b) assigns lint authority to CI, and the D-23 run 2 `Lint and Format Check` job reports `success`. |
| The Windows behaviour of D-22's `.as_posix()` repair | 46-01, 46-04 | Backslash path rendering is Windows `pathlib` behaviour and is not reproducible on this Linux machine — provable only on a real Windows CI runner. D-23 run 1 (`31456868265`) is this repair's acceptance evidence, not the local suite. |
| `.github/workflows/release.yml` itself (a real workflow run) | 46-05 | Cannot run outside a real tag push (`on: push: tags: 'v*'`) or a `workflow_dispatch` invocation; both are forbidden by this phase's prep-only fence. REL-04's in-phase share is discharged instead by a static read of the job's YAML structure plus a direct hand-run of the extractor it calls. |
| Per-hunk assertion tracing of every node-handler change against GATE-01 | every plan | Out of this phase's own scope — Phase 46 is release-prep, not a translator phase; GATE-01 compliance for this milestone's node-handler changes was already discharged by Phases 43/44/44.1/44.2, each carrying its own recorded-RED fixture. |
| `git tag v0.7.1`, any tag push, `release.yml` trigger, PyPI upload, GitHub Release creation, PR open/merge | every plan in this phase | Forbidden by the prep/publish fence (Phase 33/35/41 precedent) that is absolute for this entire phase — these are exactly the actions `46-HANDOFF.md` records as the checklist for `/gsd-complete-milestone` to execute later, never for a release-prep phase to perform itself. |
| Flipping REL-04's / REL-06's checkbox or Traceability row in `.planning/REQUIREMENTS.md` | every plan in this phase | Deliberately deferred to `/gsd-complete-milestone`'s own close-side run, per D-26/D-28 and this plan's own prohibition. `git diff --name-only -- .planning/REQUIREMENTS.md` is empty over this phase's entire history. |

**No skip listed above stands in for a pass anywhere in this phase's evidence.** Every skip is
named with its reason, sourced from the sibling file that actually recorded it.
