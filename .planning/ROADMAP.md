# Roadmap: typsphinx

## Milestones

- ✅ **v0.4.4 — CI-repair + modernize** — Phases 1–5 (shipped 2026-07-05) → [archive](milestones/v0.4.4-ROADMAP.md)
- ✅ **v0.5.0 — forward-ecosystem** — Phases 6–10 + 8.1 (shipped 2026-07-11) → [archive](milestones/v0.5.0-ROADMAP.md)
- ✅ **v0.6.0 — real-world robustness** — Phases 11–15 (shipped 2026-07-13) → [archive](milestones/v0.6.0-ROADMAP.md)
- ✅ **v0.6.1 — rendering fidelity** — Phases 16–18 (shipped 2026-07-19) → [archive](milestones/v0.6.1-ROADMAP.md)
- ✅ **v0.6.2 — rendering fidelity round 2** — Phases 19–23 (+22.1–22.4) (shipped 2026-07-23) → [archive](milestones/v0.6.2-ROADMAP.md)
- ✅ **v0.6.3 — config & docs measured fidelity + captioned tables** — Phases 24–28 (+27.1) (shipped 2026-07-25) → [archive](milestones/v0.6.3-ROADMAP.md)
- ✅ **v0.6.4 — Read the Docs migration** — Phases 29–33 (+30.1) (shipped 2026-07-28) → [archive](milestones/v0.6.4-ROADMAP.md)
- ✅ **v0.6.5 — inline-math separator hotfix** — Phases 34–35 (shipped 2026-07-29) → [archive](milestones/v0.6.5-ROADMAP.md)
- ✅ **v0.7.0 — API rendering design overhaul** — Phases 36–42 (+40.1) (shipped 2026-08-04) → [archive](milestones/v0.7.0-ROADMAP.md)
- ✅ **v0.7.1 — bug-fix round** — Phases 43–46 (+44.1, 44.2, 45.1, 45.2) (shipped 2026-08-11) → [archive](milestones/v0.7.1-ROADMAP.md)
- ✅ **v0.8.0 — multi-master composition** — Phases 47–52 (shipped 2026-08-15) → [archive](milestones/v0.8.0-ROADMAP.md)
- ✅ **v0.9.0 — per-document templates** — Phases 53–57 (+54.1) (shipped 2026-08-22) → [archive](milestones/v0.9.0-ROADMAP.md)
- ✅ **v0.9.1 — Windows path correctness** — Phases 58–61 (completed 2026-08-30, **never published**) → [archive](milestones/v0.9.1-ROADMAP.md)
- ✅ **v0.9.2 — Inline image blocker fix and release** — Phases 62–63 (shipped 2026-08-31) → [archive](milestones/v0.9.2-ROADMAP.md)
- 🚧 **v0.9.3 — Toolchain and dependency-update repair** — Phases 64–69 (active, started 2026-09-02)

**Active milestone: v0.9.3 — Toolchain and dependency-update repair.** Six phases (64–69), and two
independent aims: make every lint / type / test lane actually run on the maintainer's NixOS machine,
and return the dependency-update path to a state where dependabot PRs are tested rather than dying at
the install step. **No product or runtime code changes** — nothing under `typsphinx/` is modified,
no new runtime dependency, no new `typst_*` config value, no `@preview` bump.

**This milestone is not published.** No tag, no PyPI upload, no GitHub Release; `pyproject.toml`
stays at **`0.9.2`** and this milestone's CHANGELOG bullets sit under `## [Unreleased]`, following
the v0.9.1 precedent. A PR to `main` **is** opened and merged — decided up front, as v0.9.1's was
not. That is **REL-12**, and it closes at `/gsd-complete-milestone`.

Phase numbering is **continuous across milestones** — v0.9.2 ran Phases 62–63, so v0.9.3 starts at
**Phase 64**.

## Phases

**Phase Numbering:**

- Integer phases (64, 65, …): Planned milestone work
- Decimal phases (64.1, 64.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order. Numbering is
**continuous across milestones** — each milestone continues from the prior one's last phase
(never resets to 1). v0.9.2 ran Phases 62–63, so this milestone starts at **Phase 64**.

<details>
<summary>✅ v0.9.2 Inline image blocker fix and release (Phases 62–63) — SHIPPED 2026-08-31</summary>

- [x] Phase 62: The `visit_image()` Separator Fix and Its Real-Compile Gate (4/4 plans) — completed 2026-08-30
- [x] Phase 63: v0.9.2 Release Prep (prep-only) (6/6 plans) — completed 2026-08-30

7/7 v1 requirements complete; `verified_closeout`. Full phase detail, the 14 binding constraints,
success criteria and decisions: [milestones/v0.9.2-ROADMAP.md](milestones/v0.9.2-ROADMAP.md)

</details>

<details>
<summary>✅ v0.9.1 Windows path correctness (Phases 58–61) — COMPLETED 2026-08-30, NOT PUBLISHED</summary>

- [x] Phase 58: `repr()`-Format Decoupling (test-side only) (3/3 plans) — completed 2026-08-28
- [x] Phase 59: Path-Shape Predicate and Image-URI Correctness (5/5 plans) — completed 2026-08-29
- [x] Phase 60: One Delimiter-Aware Path-Quoting Helper, Routed Everywhere (5/5 plans) — completed 2026-08-29
- [x] Phase 61: v0.9.1 Release Prep (prep-only) (4/4 plans) — completed 2026-08-30

10/11 v1 requirements complete. REL-09 (publish to PyPI) deliberately unmet — the release was
cancelled, not missed. It carried forward into v0.9.2 and closed there. Full phase detail:
[milestones/v0.9.1-ROADMAP.md](milestones/v0.9.1-ROADMAP.md)

</details>

<details>
<summary>✅ v0.4.4 – v0.9.0 (Phases 1–57) — SHIPPED 2026-07-05 → 2026-08-22</summary>

Each milestone's phase detail lives in its own archive, linked from the **Milestones** list above.

</details>

## 🚧 v0.9.3 — Toolchain and dependency-update repair (ACTIVE)

**Milestone Goal:** the gates that protect this project's core value must be runnable by the
maintainer, and the dependency-update path that keeps the pinned ecosystem current must actually run
tests. Neither is true today: `ruff`, `tox -e py312`, `.venv/bin/uv` and the CPython tox downloads
all die on NixOS' stub loader, and every dependabot PR dies at `uv sync --locked` before a single
test runs. This milestone serves the core value **indirectly but concretely** — it changes no
product behaviour and ships nothing to users.

**Binding constraints this roadmap is built on** (settled decisions and measured facts, not open
questions):

1. **Two tracks, hard ordering inside each, no dependency across them.** Track A is
   `{FHS wrapper + shims} → {tox-uv revert}` and the order is a real dependency, not a convention:
   reverting the pin before the FHS wrapper is proven **reintroduces exactly the defect
   `tox-uv-bare` was chosen to avoid** (QUA-04, v0.7.1 Phase 45.2). Track B is
   `{dependabot ecosystem switch} → {prove on a real dependabot PR, then dispose of #123/#128}` and
   is fully independent of Track A: CI runs on GitHub-hosted runners and never touches NixOS, and
   the two tracks share no file and no mechanism. **Documentation is last on both tracks** so it
   describes what landed rather than what was planned.

2. **This milestone is not published, and that was decided up front.** No tag (local or remote), no
   PyPI upload, no GitHub Release. `pyproject.toml` stays at `0.9.2`; the CHANGELOG bullets go under
   `## [Unreleased]` and **no `## [0.9.3]` heading and no `[0.9.3]` tail link are ever created**. A
   PR to `main` **is** opened and merged — that is REL-12, and like every REL requirement in this
   project it closes at `/gsd-complete-milestone`, not inside a phase.

   > **AMENDED 2026-09-12 (Phase 66 discuss, owner-approved).** "One PR to `main`" does not survive
   > contact with how dependabot reads its configuration: GitHub's own docs
   > (`about-the-dependabot-yml-file.md:46`) state the file must live "in the default branch
   > (typically `main`)", and `origin/main`'s `.github/dependabot.yml` still reads `pip`. With the
   > milestone reaching `main` only at REL-12, no `uv`-ecosystem PR could open before the milestone
   > closed, so Phase 66 SC#1's real-PR observation and all of Phase 67 (DEP-02, DEP-05) would be
   > unreachable. Phase 66 therefore opens and merges **one additional PR to `main` carrying only
   > `.github/dependabot.yml`**, with byte-identical content committed on the milestone branch so
   > REL-12's merge stays conflict-free. REL-12 is otherwise unchanged: still the milestone's PR,
   > still closed at `/gsd-complete-milestone`; nothing is tagged, uploaded or released. Consequence
   > for constraint 4: removing the `pip` entry on `main` may itself change #123/#128's state (docs
   > are silent; unmeasured), so Phase 66 snapshots both PRs immediately before and after the merge
   > and Phase 67 SC#2 reads that record — any close caused by it is a **mechanical** close, never
   > DEP-05's disposal on the merits. See `66-CONTEXT.md` D-01..D-02.

3. **CI is deliberately unchanged.** No `nix` job is added; `astral-sh/setup-uv`'s **eleven**
   `version: "latest"` steps are **not** pinned; `astral-sh/setup-uv@v7` is **not** bumped to `@v10`.
   The only `.github/` file this milestone edits is `.github/dependabot.yml`, which is not a
   workflow. Any phase proposing a workflow edit is out of scope by construction — see
   REQUIREMENTS.md's Out of Scope table, which is binding.

4. **DEP-02 requires a real dependabot PR, and the ordering around #123/#128 is not obvious.** A
   hand-made branch carrying a fresh `uv.lock` does **not** satisfy it — the source todo rejects that
   shortcut explicitly. #123 (`ruff <0.17`, open since 2026-07-27) and #128 (`docutils <0.24`, open
   since 2026-08-03) were opened under the `pip` ecosystem, and `@dependabot recreate` re-runs under
   the ecosystem the PR was *opened* with, so neither can be converted in place; fresh PRs must open
   under `uv`, and it is **those** that constitute the proof. **DEP-05 is sequenced strictly after
   DEP-02** (Pitfall 8): closing the old PRs before the proof removes the only real dependabot PRs
   to test against. The tension between "they must close so fresh ones open" and "do not close them
   before the proof" is resolved by a distinction the executing phase must hold: a **mechanical
   close to unblock** a fresh `uv`-ecosystem PR is not DEP-05's **disposal on the merits**, and
   whether such a close is even required is itself unmeasured. Phase 67 measures whether a `uv`-
   ecosystem PR can open for a dependency that already has an open `pip`-ecosystem PR before it
   closes anything, and records the merit judgement on whichever PR — original or successor —
   carries each bump.

5. **Five items are genuinely unverified and are closed by measurement inside a phase, never
   assumed.** (a) `buildFHSEnv`'s `$HOME` / `TMPDIR` / `/etc` / locale passthrough **for this
   project's actual invocation** — no source measures it in the command-shim-from-an-outer-`mkShell`
   shape used here, and it bears directly on this repo's known **locale-dependent CI-only defect
   class** (NIX-08, Phase 64). (b) Whether the shim PATH is reachable in a freshly created git
   worktree before `direnv allow` has run there, and whether the harness's non-interactive Bash
   calls trigger direnv's hook at all (NIX-05, Phase 64). (c) The uv **v0.11-vs-0.12** lock-revision
   question — dependabot states v0.11 support, `ci.yml` installs `latest` (0.12.x today), this
   repo's lock is `version = 1, revision = 3` (DEP-04, Phase 66). (d) Grouped-update behaviour under
   the new ecosystem (DEP-03, Phase 66). (e) An **isolated outside-FHS control** for the tox `uv`
   discovery path — the earlier control did not isolate it, having failed earlier on
   `.venv/bin/python3` (TOX-03, Phase 65).

6. **Verification asserts exact versions, not exit codes.** NIX-01 requires `ruff` to report
   **0.15.20** — the `uv.lock` version, confirmed at `uv.lock:1209-1210` — not merely to succeed,
   and not nixpkgs' 0.15.14. A shim that degrades gracefully to *some* other binary when
   `.venv/bin/<tool>` is missing replaces "doesn't run" with "runs but lies" (Pitfall 10); shims
   fail loudly instead. The same standard applies everywhere in this milestone: `tox -e docs-pdf`
   must produce a real PDF, not exit 0.

7. **CI holds lint authority, and only CI reaches Windows and macOS.** Those lanes have caught real
   defects at three consecutive closes (v0.7.0 cp1252, v0.7.1 path separator, all of v0.9.1). A
   green maintainer machine is not a green project: **TOX-04's green must come from a real CI run**,
   dispatched with `gh workflow run CI --ref <branch>` (`ci.yml`'s push/PR triggers are scoped to
   `main`/`develop`, so a push alone runs no CI), with `ruff`'s verdict taken from that run's
   **`Lint and Format Check`** job — whose one step, **`Run lint with tox`** (`ci.yml:69`), runs
   `uv run tox -e lint` = `black --check .` + `ruff check .`. `ci.yml` carries no step named
   `Run linters`; that name exists only at `release.yml:84`.

8. **`flake.nix` becomes load-bearing this milestone while keeping ZERO CI coverage — named here so
   it is a tracked risk rather than an implicit one.** No workflow references `nix` or `flake`, so a
   breaking edit is caught only when the maintainer next enters the shell, and the darwin branch of
   the per-system guard cannot be exercised at all from a Linux machine. This is the accepted
   consequence of constraint 3 (owner decision 2026-09-02), **not** an oversight. The mitigation is
   bounded and required: `nix eval` / `nix flake show` must succeed for **all four** declared
   systems — `x86_64-linux`, `aarch64-linux`, `x86_64-darwin`, `aarch64-darwin` (`flake.nix:11-15`)
   — on the Linux evaluator, which catches a missing or misplaced guard at eval time without darwin
   hardware, and DOC-21 must state that darwin is unverified by construction so a darwin contributor
   reports breakage rather than assuming CI would have caught it. It is filed under REQUIREMENTS.md
   § Future Requirements → "Arising from this milestone".

9. **The `gsd/v0.9.3-*` decoy branch pair is live and must be corrected before anything is pushed.**
   Measured at roadmap time (2026-09-02): the canonical, config-derived branch
   `gsd/v0.9.3-toolchain-and-dependency-update-repair` is at **`efffd892`** (`main` + 1), while
   `gsd/v0.9.3-milestone` is at **`7d1f4a70`** (canonical + 3: the AMENDED block, the research
   commit and the requirements commit) and is where **HEAD** currently sits. This is the same
   inverted shape v0.9.2 measured, and repeating v0.9.1's correction here **would orphan three
   commits**. `git merge-base --is-ancestor` confirms the two are strictly linear, so the safe
   sequence is: fast-forward the canonical ref to `7d1f4a70`, re-point HEAD with
   `git symbolic-ref` (no checkout, so uncommitted files survive), **and only then** delete the
   decoy. Nothing matching `0.9.3` exists on `origin`. Expect the decoy to be re-created by the next
   `gsd-tools query commit` — it is a per-milestone recurrence, not a one-off.

10. **Milestone invariant #5: the milestone branch reaches `origin` in the FIRST phase**, evidenced
    by a **completed** CI run including the `windows-latest` and `macos-latest` lanes. Adopted
    v0.7.1; its absence cost v0.7.0 two defects found only at the release PR. It applies here even
    though Phase 64's own deliverable (`flake.nix`) is invisible to CI, because Phase 65's TOX-04
    and Phase 69's PR both depend on the branch already being on `origin` with a known-green
    baseline. Constraint 9's correction happens before this push.

11. **Worktree isolation is the standing execution mode** (owner decision, `CLAUDE.md`), and this
    milestone must not repurpose the FHS wrapper as a substitute for it (Pitfall 3). Every executor
    still provisions with `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` and
    runs everything via `uv run`. A worktree is a directory direnv has never seen, so `.envrc`'s
    `use flake` does not auto-load there and the shims may not exist at all — which is precisely
    NIX-05's measurement. An executor that skips provisioning because "the shims are on PATH now"
    reproduces the Phase 38-07 incident (45 test failures misdiagnosed as a code regression) via a
    new and less familiar mechanism. DOC-19 must state this boundary explicitly.

12. **`tox-uv`'s discovery order is a different code path from the one the scoping measurement
    printed** (Pitfall 1, the highest-risk item in Track A). `tox-uv`-the-tox-plugin resolves
    `TOX_UV_PATH` → **its own bundled `uv` wheel** → `PATH`; `tox-uv-bare` skips the middle step.
    The recorded measurement showed `uv.find_uv_bin()` — `uv`-the-Python-package's own lookup, used
    by its build backend — which is not the same function. The real `tox -e type` / `-e lint` /
    `-e py312` / `-e py313` runs did pass inside FHS, so the mechanism is exercised; what is missing
    is the isolated control. TOX-03 is Phase 65's primary verification target for this reason, and
    the recovery if the bundled binary wins is low-cost and known: set `TOX_UV_PATH`, or revert to
    `tox-uv-bare`.

    > **AMENDED 2026-09-12 (Phase 65 discuss, owner-approved).** Measured against the installed
    > source and a scratch probe, "which is not the same function" is false. `tox-uv`'s middle step
    > *is* `uv.find_uv_bin()` — `from uv import find_uv_bin; return find_uv_bin()`
    > (`tox_uv/_venv.py:232-238`; the `tox_uv` module ships in `tox-uv-bare`, and `tox-uv` adds only
    > the `uv` dependency). No binary ships inside the `tox-uv` wheel: "bundled" means the PyPI `uv`
    > package's script, which `find_uv_bin()` returns as `<tox's own env>/bin/uv` — the outer
    > `.venv/bin/uv`, the same file the Phase 64 `uv` shim's first leg resolves. What separates the
    > scoping measurement from a real tox run is the calling process, not the function. Probe
    > (`tox-uv 1.36.0` in a nix `python3-3.13.13` venv): inside FHS, `tox -vv -e type` logs
    > `using bundled uv from: …/.venv/bin/uv [tox_uv/_venv.py:237]` and passes; outside FHS the same
    > run starts, resolves the same path and fails exec'ing it (`Could not start dynamically linked
    > executable`, exit 127). The recovery above therefore does not apply: inside FHS the bundled
    > binary *is* the intended `.venv/bin/uv`, and it executes. See `65-CONTEXT.md` D-01..D-03.

13. **Standing invariants carried forward:** **no change under `typsphinx/`** — this is a toolchain
    milestone by construction, and any diff there is an over-reach signal, not routine work; zero
    new runtime dependencies and no new third-party GitHub Action (`tox-uv` and `tox-uv-bare` release
    in exact version lockstep, verified against the PyPI JSON API, and `tox-uv == tox-uv-bare + uv`,
    so the revert is a drop-in package-name swap keeping the existing `>=1.35,<2` range in
    `pyproject.toml:38` and the comma-free `~=1.35` form in `tox.ini`); no new `typst_*` config
    value; the `@preview` package count stays at **four** with no version change; typing-import
    modernization is forbidden (`CLAUDE.md` independently instructs it); SEED-003 (PEP 735
    `[dependency-groups]`) stays dormant; and every phase closes green on the full pytest suite.
    **`uv.lock` is regenerated with `uv lock`, never hand-edited**, and lands in the same commit as
    any `pyproject.toml` change — omitting that reproduces the exact `--locked` refusal this
    milestone exists to repair.

14. **The release-requirement flip hazard is now seven-for-eight and must be fenced.**
    `phase.complete` has auto-flipped the release requirement to `[x]` against an explicit CONTEXT
    decision at seven consecutive release-prep closes (Phases 41, 46, 52, 57, 61 held it, 63 flipped
    and was reverted — see `282bce71`). Phase 69 reuses the procedure that has worked: SHA-256 +
    `wc -l` + `git rev-parse HEAD` of `.planning/REQUIREMENTS.md` recorded at phase head, re-verified
    at phase close, **and re-verified once more after `phase.complete`-family tooling runs** — that
    third observation is the one that actually catches the flip, because it runs outside any plan's
    reach. Every plan in Phase 69 declares `requirements-completed: []` for REL-12. **This is also
    why DOC-19/DOC-20/DOC-21 are a separate phase from REL-12**: a whole-file checksum fence only
    works in a phase where no other requirement checkbox is meant to move.

15. **Not a frontend UI milestone** (standing project note). `ui.plan-gate` false-positives on
    words this milestone cannot avoid — "page", "render", "PDF", "docs-html". Each phase detail
    therefore carries an explicit `**UI hint**: no` line, the authoritative override
    `ui-safety-gate.cjs` reads, rather than relying on a per-run `--skip-ui`.

**`research/SUMMARY.md`'s suggested A1 / A2 / B1 / B2 / C structure is adopted as five phases plus a
close phase, not five.** Its A1 is Phase 64 unchanged, A2 is Phase 65, B1 is Phase 66, B2 is Phase
67 and C is Phase 68 — the research's own ordering rationale is constraint 1 above, and none of its
boundaries was moved. The sixth phase (69) is this project's standing prep-only final phase, the
convention held for **nine consecutive milestones** under `branching_strategy: milestone`: the phase
takes zero irreversible action and the merge executes at `/gsd-complete-milestone`. REL-12 is
therefore mapped to Phase 69 for coverage purposes only.

- [x] **Phase 64: FHS Wrapper and Command Shims in `flake.nix`** - Every documented bare command and every tox environment runs to completion on the maintainer's NixOS machine through Linux-guarded `buildFHSEnv` shims that resolve the project's own `.venv` binaries by absolute path, with the sandbox's environment behaviour measured rather than assumed (completed 2026-09-12)
- [x] **Phase 65: `tox-uv-bare` → `tox-uv` Revert, on the uv Path tox Actually Resolves** - The upstream `tox-uv` package returns to `pyproject.toml` and `tox.ini` with `uv.lock` regenerated in lockstep, gated on observing which `uv` binary a real tox run resolves and on a CI run that is green across every lane (completed 2026-09-12)
- [x] **Phase 66: `.github/dependabot.yml` — `pip` → `uv` Ecosystem** - Dependabot maintains `uv.lock` alongside `pyproject.toml` in one commit, with the v0.11/v0.12 lock-revision question and the `sphinx-typst-stack` grouping measured against live sources rather than inferred (completed 2026-09-12)
- [x] **Phase 67: Proof on a Real Dependabot PR, Then Disposal of #123 and #128** - The install step is observed succeeding and the test / lint / type jobs observed running on a real dependabot PR, after which each stale bump is judged on its merits and the grouped-update coverage gap is recorded rather than passed over (completed 2026-09-12)
- [x] **Phase 68: Documentation Follow-Through — `CLAUDE.md`, `tox.ini`, `flake.nix`** - The three documentation surfaces describe the mechanism that actually landed, retire the manual shim instruction, and state both boundaries that would otherwise be inferred wrongly: worktree executors are unassisted by `flake.nix`, and darwin is unverified by construction (completed 2026-09-13)
- [ ] **Phase 69: v0.9.3 Close Prep (prep-only, unpublished)** - The milestone's CHANGELOG bullets land under `## [Unreleased]` with `pyproject.toml` still at `0.9.2`, the tree is proven green on runs executed in this phase, and the PR to `main` is prepared behind a checksum fence with zero irreversible action taken

## Phase Details

### Phase 64: FHS Wrapper and Command Shims in `flake.nix`

**Goal**: the maintainer types `ruff check .`, `pytest`, or `tox -e py313` on the NixOS machine and
it runs — not one binary at a time behind a manual `ln -sf` or `patchelf`, but the whole
generic-linux-ELF class at once, because a Linux-namespace sandbox is inherited across `fork`/`exec`
and therefore only the top-level entrypoints a human types need shimming. Everything `tox` spawns
beneath them — the `uv-venv-lock-runner`, `.venv/bin/uv`, the CPython tox downloads, each
`.tox/<env>/bin/*` — inherits the sandbox for free.

Nothing else in Track A is safe until this is proven (constraint 1). Two designs were already
falsified by measurement during scoping and must not be re-derived: `buildFHSEnv`'s `.env` used as
the devShell does **not** put you inside FHS under either `nix develop` or `direnv`, and a
`shellHook` that `exec`s into the wrapper does not work either — `nix develop` never runs the hook,
and under direnv the `exec` only replaces nix-direnv's environment-capture subshell. The devShell
stays `mkShell` and the FHS is exposed as PATH command shims from it. `buildFHSEnv` is a plain alias
for `buildFHSEnvBubblewrap` and is the name to write; `buildFHSEnvChroot` was removed from
nixos-unstable and referencing it hard-fails flake evaluation.

This is the first phase of the milestone, so it carries constraint 9's decoy-branch correction and
constraint 10's branch-to-`origin` invariant.

**Depends on**: Nothing (first phase of the milestone)
**Requirements**: NIX-01, NIX-02, NIX-03, NIX-04, NIX-05, NIX-06, NIX-07, NIX-08
**Success Criteria** (what must be TRUE):

  1. **`ruff check .` runs to completion and reports the version `uv.lock` pins, not the one nixpkgs
     ships.** `ruff --version` through the shim prints exactly **0.15.20** (`uv.lock:1209-1210`),
     never nixpkgs' 0.15.14, and `ruff check .` completes over the repository. The same standard
     applies to the other documented bare commands (`pytest`, `black --check .`, `mypy typsphinx/`):
     each runs to completion and resolves out of the project's own `.venv`. An exit code alone does
     not satisfy this criterion — a shim that silently falls back to any other source replaces
     "doesn't run" with "runs but disagrees with CI" (NIX-01).

  2. **Every tox environment runs to completion, and the full suite is clean of environment-caused
     failures.** `tox -e lint`, `-e type`, `-e py312` and `-e py313` each run to completion
     (NIX-02); `tox -e cov`, `-e docs-html` and `-e docs-pdf` each run to completion, with
     `docs-pdf` producing a **real PDF** — a non-empty file beginning with the `%PDF` magic bytes,
     not merely exit 0 (NIX-03); and the full test suite (**1548** tests at milestone start) runs
     with **no environment-caused failures**, each remaining failure, if any, attributed to a cause
     that is not the toolchain (NIX-04). A single smoke command is explicitly not sufficient here:
     `tox -e docs-pdf` is the invocation that exercises font resolution, subprocess spawning and
     exit-code propagation through the sandbox.

  3. **The flake evaluates everywhere it declares, and no shim can re-enter itself.** `nix eval` /
     `nix flake show` succeeds for **all four** systems declared at `flake.nix:11-15` — including
     both darwin ones, whose `buildFHSEnv` call must never be evaluated because it is Linux-only —
     on the Linux evaluator (NIX-06). Each shim resolves its target by an **absolute, un-shadowable
     path** and cannot recurse into itself, proven by a check that **would catch bare-name
     resolution**: rename or remove the `.venv/bin/<tool>` target and the shim fails with a clear
     "not found" rather than hanging, fork-bombing, or falling through to another binary. A one-off
     `--version` smoke test does not satisfy this (NIX-07).

  4. **The sandbox's environment behaviour is measured for this project's actual invocation, not
     assumed.** `$HOME`, `TMPDIR`, `/etc` and locale passthrough are measured for the exact
     command-shim-from-an-outer-`mkShell` shape used here — no published source measures it in this
     shape — and the **effect on this repository's known locale-dependent CI-only defect class** is
     recorded, including whether the sandbox reproduces or *masks* it (NIX-08). Separately, an
     executor in a **freshly created git worktree** runs the documented provisioning line
     (`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev`) and then every gate, with
     **no manual `ln -sf` and no `patchelf` step anywhere** — and whether the shim PATH is reachable
     there before `direnv allow` has been run for that worktree path is answered by observation,
     either way, rather than asserted (NIX-05).

  5. **The milestone branch is on `origin` with a completed 3-OS CI run.** Constraint 9's
     decoy-pair correction is **already done** — see the resolved note below — so this criterion
     reduces to pushing the canonical branch with tracking and observing a real CI run. A run
     dispatched with `gh workflow run CI --ref <branch>` has **completed**, with the
     `windows-latest` and `macos-latest` lanes named individually and green. This run is the
     pre-revert baseline Phase 65's TOX-04 is compared against.

     > **Constraint 9 — RESOLVED 2026-09-02 by the operator at roadmap approval, before Phase 64
     > planning began.** The roadmapper deferred the correction into this criterion; it was executed
     > immediately instead, because leaving it deferred would have stacked every Phase 64 commit onto
     > the decoy as well. The measured state it corrected differs from the roadmapper's recorded
     > values, because a `commit` helper call made *after* the roadmapper's measurement re-created the
     > decoy and moved HEAD onto it a second time — this session had already renamed it once, at
     > `efffd892`, and the rename did not hold. Measured before: decoy `gsd/v0.9.3-milestone` at
     > `d494b4a9`, `main`+5, **carrying HEAD and every commit of this milestone**; canonical
     > `gsd/v0.9.3-toolchain-and-dependency-update-repair` stranded at `efffd892`, `main`+1.
     > Sequence executed: `git branch -f <canonical> d494b4a9` → `git symbolic-ref HEAD
     > refs/heads/<canonical>` (chosen over `checkout` so the working tree was never touched) →
     > `git branch -d gsd/v0.9.3-milestone` (accepted as fully merged). Measured after: canonical at
     > `d494b4a9`, `main`+5, sole `gsd/v0.9.3-*` ref; **zero commits orphaned.** A Phase 64 executor
     > must re-measure rather than trust this note, and must expect the decoy to be re-created by any
     > later `commit` helper invocation — it has now fired twice within this one milestone.

**Plans**: 6/6 plans executed (5 waves; a Claude Code session relaunch is required between wave 1 and wave 2, and again between wave 4 and wave 5)

Plans:
**Wave 1**

- [x] 64-01-PLAN.md — flake.nix: one Linux-guarded buildFHSEnv passthrough plus the seven D-01 shims; ruff RED→GREEN tracer, tox shakeout (nested entry, D-07), NIX-06 on all four systems with darwin byte-identical

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 64-02-PLAN.md — NIX-05 in the genuine D-09 shape: fresh nested worktree, head check, the one provisioning line, then NIX-01 bare commands, NIX-04 full suite and NIX-02/NIX-03 tox environments with a real PDF
- [x] 64-03-PLAN.md — NIX-07 rename proof from a nested worktree with an escape positive control, and NIX-08 environment and locale measurement against terms committed before measuring

**Wave 3** *(blocked on Wave 2 completion)*

- [x] 64-04-PLAN.md — SC#5: re-measured branch census, canonical branch pushed with tracking, one CI dispatch observed to completion with all lanes transcribed

**Wave 4** *(gap closure; blocked on Wave 3 completion)*

- [x] 64-05-PLAN.md — flake.nix: zlib in fhsRun's targetPkgs (CR-01), gated by a DT_NEEDED residual audit before and after, an import-order-independent RED→GREEN on three interpreter builds, a DIAGNOSTIC second-gap sweep, and NIX-06/07/08 re-bound on the final flake

**Wave 5** *(gap closure; blocked on Wave 4 completion and a Claude Code session relaunch)*

- [x] 64-06-PLAN.md — genuine D-09 re-measurement after the fix in a fresh nested worktree: NIX-01 regression, the path that failed, NIX-04 full suite, all seven tox environments (NIX-02/NIX-03) with a real PDF, and the residual audit over what it provisions

**UI hint**: no

### Phase 65: `tox-uv-bare` → `tox-uv` Revert, on the uv Path tox Actually Resolves

**Goal**: the QUA-04 constraint that forced `-bare` — the bundled `uv` wheel cannot exec on NixOS —
is dissolved by Phase 64's wrapper, so the repository returns to the upstream `tox-uv` package. The
change itself is mechanical: `tox-uv` and `tox-uv-bare` release in exact version lockstep (verified
against the PyPI JSON API) and `tox-uv == tox-uv-bare + uv`, so this is a drop-in package-name swap.
What is **not** mechanical is the proof, and that is what this phase is really for.

The revert reinstates `tox-uv`'s bundled-wheel discovery step, which is the single highest-risk item
in Track A (constraint 12). The primary verification target is therefore not "tox is green" — it is
**which `uv` binary a real tox run resolved**, plus an isolated outside-FHS control that fails on the
uv path rather than earlier. This phase is sequenced strictly after Phase 64 because reverting the
pin before the sandbox is proven reintroduces exactly the defect `-bare` was chosen to avoid.

**Depends on**: Phase 64
**Requirements**: TOX-01, TOX-02, TOX-03, TOX-04
**Success Criteria** (what must be TRUE):

  1. **The declared dependency is `tox-uv`, with `uv.lock` regenerated in the same commit.**
     `pyproject.toml:38` declares `tox-uv` in place of `tox-uv-bare`, keeping the existing
     `>=1.35,<2` range, and `git show --name-only` on that commit lists `pyproject.toml` **and**
     `uv.lock` together — `uv.lock` regenerated with `uv lock`, never hand-edited. `uv sync --extra
     dev --locked` exits 0 against the changed tree; a commit touching only `pyproject.toml` is the
     exact shape currently killing every dependabot PR (TOX-01).

  2. **`tox` starts, and the ini-parser constraint survives the edit.** `tox.ini`'s `requires` names
     `tox-uv` in the **comma-free `~=` form** (`tox-uv~=1.35`), because tox's own ini-list loader
     splits a single-line `requires` value on `,` and a literal `>=1.35,<2` is parsed as two bogus
     requirements so tox fails to even start. `tox --version` (or any environment) starts
     successfully against the edited file (TOX-02).

  3. **The `uv` binary tox actually resolved is observed from inside a real tox run, against an
     isolated control.** The resolved path and version are printed from **inside** a real
     `tox -e py312` run — not from `uv --version` at the shell, and not from `uv.find_uv_bin()`,
     which is a different function on a different code path — and the result shows whether
     `tox-uv`'s bundled wheel or the shimmed/`.venv` binary won. An **isolated outside-FHS control**
     accompanies it and demonstrates that the failure it produces is the **uv path** rather than
     something that fails earlier: the previous control failed on `.venv/bin/python3` and therefore
     isolated nothing. If the bundled binary wins, the recorded recovery is `TOX_UV_PATH` or a
     return to `tox-uv-bare` — either outcome closes this criterion, an unmeasured "it passed" does
     not (TOX-03).

     > **AMENDED 2026-09-12 (Phase 65 discuss, owner-approved).** Two phrases above are falsified
     > by measurement; the substantive requirement stands. (a) "not from `uv.find_uv_bin()`, which
     > is a different function on a different code path": `tox-uv`'s bundled step *calls*
     > `uv.find_uv_bin()` (`tox_uv/_venv.py:234-236`); the binding distinction is that the path is
     > observed from inside the tox process, not from a shell. (b) "whether `tox-uv`'s bundled wheel
     > or the shimmed/`.venv` binary won": these are the same file, `<env>/bin/uv`, so the
     > observation records which of `_venv.py`'s three branches fired (`TOX_UV_PATH` / bundled /
     > `PATH`) plus the resolved path and version. A bundled resolution, inside FHS, to the tree's own
     > `.venv/bin/uv` with the environment passing **closes** this criterion without `TOX_UV_PATH`
     > (`65-CONTEXT.md` D-02); the isolated control runs from a nix-interpreter venv so that the only
     > thing left to fail is the uv exec (D-03). The verifier reports the literal and the amended
     > reading separately.

  4. **CI is green on the revert across every lane, and CI is the authority.** One run dispatched
     with `gh workflow run CI --ref <branch>` on the post-revert tip has **completed**, with every
     job's conclusion transcribed literally, both `windows-latest` and both `macos-latest` lanes
     named individually, and `ruff`'s verdict taken from that run's `Lint and Format Check` job
     (step `Run lint with tox`) rather than from this machine. A green maintainer machine does not
     satisfy this criterion — only CI reaches the Windows and macOS lanes, which have caught real
     defects at three consecutive closes (TOX-04).

**Plans**: 2/2 plans executed (2 waves; wave 2 pushes the post-revert tip and dispatches CI only after wave 1's SC#3 evidence reads MET)

Plans:
**Wave 1**

- [x] 65-01-PLAN.md — the four-file revert commit (pyproject, tox.ini, uv.lock, the Phase 45.2 gate inverted RED→GREEN) with a tox-uv tracer, then the D-02 observation inside FHS (cold tox -vv -e py312 -r, full suite) and the D-03 nix-interpreter control outside FHS

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 65-02-PLAN.md — TOX-04: wave-1 gate, branch census, constraint-13 fence, fast-forward push, one CI dispatch observed in the foreground to completion, twelve-job census with per-lane uv resolution against the Phase 64 baseline

**UI hint**: no

### Phase 66: `.github/dependabot.yml` — `pip` → `uv` Ecosystem

**Goal**: dependabot updates `pyproject.toml` and `uv.lock` **together, in the same commit**, so the
eleven `uv sync --locked` steps stop refusing a stale lockfile and dependabot PRs reach the tests
they exist to run. `--locked` and its reproducibility guarantee stay everywhere; nothing is loosened
to make the PRs pass.

This is a configuration change, not a new workflow — and that is the whole point of the amendment
recorded in PROJECT.md. The milestone was scoped with a custom Actions workflow that would run
`uv lock` on dependabot PRs and push the result back; two of the four researchers independently
surfaced that dependabot has supported `package-ecosystem: "uv"` natively since GA on 2025-03-13,
the orchestrator re-verified it against GitHub's own supported-ecosystems table and Astral's own
`docs/guides/integration/dependabot.md` rather than accepting the researchers' prose, and the owner
approved the replacement on 2026-09-02. Every failure mode Pitfalls research found for the custom
workflow — the forced read-only `GITHUB_TOKEN`, the `pull_request_target` exposure, pushes that do
not retrigger CI, dependabot force-pushing over commits lacking `[dependabot skip]` — is **specific
to that workflow** and disappears with the switch. The custom workflow survives only as a fallback,
to be reached for **only if** this phase's DEP-04 measurement finds the v0.11/v0.12 gap bites.

This phase is independent of Track A (constraint 1) and can be planned and executed in parallel
with Phases 64–65.

**Depends on**: Nothing (independent of Track A)
**Requirements**: DEP-01, DEP-03, DEP-04
**Success Criteria** (what must be TRUE):

  1. **`.github/dependabot.yml` uses the `uv` ecosystem, and dependabot's own output proves it took
     effect.** The Python `updates` entry reads `package-ecosystem: "uv"`, dependabot accepts the
     configuration (no config-error annotation on the repository's Dependabot tab), and the PRs it
     opens update **`pyproject.toml` and `uv.lock` in the same commit** — read from a real PR's own
     commit contents, not inferred from the YAML being correct. The `github-actions` entry is left
     untouched (DEP-01).

  2. **The uv version question is measured against live sources and recorded either way.**
     Dependabot's stated supported uv version (**v0.11**) is measured against the uv that CI
     installs (`astral-sh/setup-uv` with `version: "latest"`, currently 0.12.x across eleven steps)
     and against this repository's lock (`version = 1, revision = 3`, local uv 0.11.25), and the
     result is **recorded** — including, if a 0.12-written lock revision turns out to be one a
     0.11 dependabot cannot handle, the explicit finding that the fallback custom workflow is now
     in play. Measured, not assumed; this is the one question that can invalidate the whole
     approach (DEP-04).

  3. **The grouping, labels and PR limit are confirmed to behave as before, or the divergence is
     recorded.** The `sphinx-typst-stack` group (`sphinx*` / `docutils*` / `typst*`, excluding
     `sphinx-autodoc-typehints` and `sphinx-intl`), the `dependencies` / `automated` labels, and
     `open-pull-requests-limit: 5` are carried across unchanged and confirmed to behave as they did
     under `pip` — or the divergence is written down. "Confirmed" means observed against
     dependabot's own behaviour or its documented ecosystem support, not assumed from the YAML being
     syntactically identical (DEP-03).

**Plans**: 4/4 plans executed (4 sequential waves; 66-02 carries the D-01 owner merge checkpoint, 66-03 the D-03 owner action on the Dependabot tab)

Plans:
**Wave 1**

- [x] 66-01-PLAN.md — the one-token `pip` → `uv` switch committed on the milestone branch and, byte-identical, on a `main`-bound PR branch built from `origin/main`; PR opened and its 6 required checks observed green

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 66-02-PLAN.md — pre-merge gate and simulated REL-12 merge, owner go-ahead (D-01, one-way), D-02 pre-merge snapshot of #123/#128, two-parent merge into `main`

**Wave 3** *(blocked on Wave 2 completion)*

- [x] 66-03-PLAN.md — the post-merge `uv` update job read from the Actions API (`Dependabot Updates`), owner Dependabot-tab read and conditional "Check for updates" (D-03/D-04), D-02 post-merge snapshot, `dependabot/uv/` PR census

**Wave 4** *(blocked on Wave 3 completion)*

- [x] 66-04-PLAN.md — SC#1 from a real `uv` PR's head commit, D-05 legs 1 and 2 (HALT on leg-2 failure), D-06 observations, DEP-01/DEP-03/DEP-04 closure table

**UI hint**: no

### Phase 67: Proof on a Real Dependabot PR, Then Disposal of #123 and #128

**Goal**: the fix is proven where it has to be proven — on a **real dependabot PR**, with the
`uv sync --locked` step observed succeeding and the test / lint / type jobs observed actually
running — and only then are the two long-stale bumps judged on their merits rather than merged
because CI finally went green.

The ordering inside this phase is the whole reason it is a phase (constraint 4, Pitfall 8). #123 and
#128 were opened under the `pip` ecosystem and cannot be converted in place, so fresh PRs must open
under `uv`; but closing the old ones first removes the only real dependabot PRs to test against and
forces the hand-made-branch shortcut the milestone's own acceptance bar rejects. **Measure before
closing anything.**

**Depends on**: Phase 66
**Requirements**: DEP-02, DEP-05
**Success Criteria** (what must be TRUE):

  1. **On a real dependabot PR, the install step succeeds and the jobs actually run — observed.**
     A PR opened by `dependabot[bot]` under the `uv` ecosystem has a completed check history in
     which the `uv sync --locked` step **succeeds** and the test, lint and type jobs **run to a
     conclusion** rather than dying before the first test. The evidence is the PR's own check runs
     and step logs. A hand-made branch carrying a fresh `uv.lock` does **not** satisfy this
     criterion, however green it is (DEP-02).

  2. **Whether the stale PRs had to close first is measured, and any pre-proof close is recorded as
     mechanical rather than as disposal.** Before #123 or #128 is touched, it is observed whether a
     `uv`-ecosystem PR can open for a dependency that already has an open `pip`-ecosystem PR. If it
     can, both stay open until criterion 1 is satisfied. If it cannot, the close is taken as a
     **mechanical unblock**, recorded as such with that measurement attached, and the merit judgement
     is still taken afterwards on the successor PR. Either way, the proof in criterion 1 precedes
     every merit decision (DEP-05, constraint 4).

  3. **Each bump is disposed of on its merits, with the judgement written down.** #123
     (`ruff <0.17`) and #128 (`docutils <0.24`) — or the `uv`-ecosystem PRs that supersede them —
     each reach a recorded decision: merged, or closed with the reason. "CI is finally green" is not
     a merit; the ruff bound in particular interacts with NIX-01's exact-0.15.20 requirement and
     with `pyproject.toml`'s `>=0.15,<0.16` specifier, and that interaction is part of the judgement
     (DEP-05).

  4. **The grouped-update coverage gap is recorded explicitly rather than passed over.** Neither
     #123 (ruff) nor #128 (docutils) is a grouped bump, so **neither exercises the
     `sphinx-typst-stack` path** — a grouped multi-package update can hit a genuinely unresolvable
     dependency graph, a different failure from the stale-lockfile mismatch this milestone repairs.
     The phase states in writing that this milestone's proof does not cover that path, so a future
     grouped PR failing at resolution is recognized as an uncovered case rather than misread as a
     regression of this fix (DEP-05, Pitfall 7).

     > **AMENDED 2026-09-12 (Phase 67 discuss, owner-approved).** The premise "neither #123 nor #128
     > is a grouped bump" is falsified by measurement: #128 **is** a `sphinx-typst-stack` group PR
     > (branch `dependabot/pip/sphinx-typst-stack-12b5b89b5a`, title "…in the sphinx-typst-stack
     > group across 1 directory"). The conclusion is unchanged: under `uv` no group PR opened,
     > because the group's `docutils` member failed with `dependency_file_not_resolvable` (Sphinx
     > 9.1.0 caps `docutils<0.23`; `66-DEPENDABOT-EVIDENCE.md` § uv update job conclusion) — itself
     > a live instance of the "genuinely unresolvable dependency graph" named above — and the PR
     > carrying this milestone's proof (#138, `ruff`) is not grouped. So the proof still does not
     > cover a grouped `uv` update, and the phase still states that gap in writing.
     > `REQUIREMENTS.md` DEP-05 is unchanged (its text is correct). See `67-CONTEXT.md` D-06. The
     > verifier reports the literal and the amended reading separately.

**Plans**: 5/5 plans executed (4 waves; 67-02 and 67-03 run in parallel in wave 2; 67-02, 67-03 and 67-04 each carry one owner checkpoint:decision immediately before a one-way GitHub action)

Plans:
**Wave 1**

- [x] 67-01-PLAN.md — D-01/D-02: DEP-02 read from #138's own CI run `34689041575` (job census, check runs, per-step reads of every Lint/Type/Test job), Phase 66 snapshots cited, #123/#128 re-snapshotted read-only after the proof

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 67-02-PLAN.md — D-03/D-04: #138 pre-merge gate and SC#3 merits (dev-extra scope, FHS `ruff check .` of the milestone tip, REL-12 simulation with a lock check, NIX-01 interaction), owner go-ahead, two-parent merge into `main`; the milestone branch does not absorb `main`
- [x] 67-03-PLAN.md — D-05: Sphinx's `docutils` cap re-measured on PyPI (HALT if relaxed), #128 merits and whole-thread read, owner-approved comment, cap re-checked immediately before closing #128

**Wave 3** *(blocked on Wave 2 completion)*

- [x] 67-04-PLAN.md — D-03: #123 closed as superseded by the merged #138, after its thread is read and the owner approves the exact comment

**Wave 4** *(blocked on Wave 3 completion)*

- [x] 67-05-PLAN.md — D-06: SC#4 grouped-update coverage gap in its literal and amended readings, ordering proof, deferred-PR and todo checks, DEP-02/DEP-05 closure table

**UI hint**: no

### Phase 68: Documentation Follow-Through — `CLAUDE.md`, `tox.ini`, `flake.nix`

**Goal**: the three documentation surfaces describe the mechanism that **actually landed**, not the
one that was planned — which is why this phase is last on both tracks. Two of the three carry a
boundary that will otherwise be inferred wrongly, and both inferences have already cost this project
real time.

No Nix-ecosystem convention exists for making a shim self-announcing — a runtime banner would
corrupt tool output that CI and pytest parse — so documentation is the only mechanism available
here.

**Depends on**: Phase 65 and Phase 67 (documents what both tracks landed)
**Requirements**: DOC-19, DOC-20, DOC-21
**Success Criteria** (what must be TRUE):

  1. **`CLAUDE.md`'s NixOS / worktree-provisioning section describes the landed mechanism and
     instructs no manual shim step.** The manual `ln -sf` / `patchelf` guidance is gone — retired,
     not made conditional — and in its place the section describes what Phase 64 actually landed
     (DOC-19). It also states the boundary explicitly, in its own words rather than by implication:
     **the FHS wrapper is for the maintainer's interactive NixOS shell; automated worktree executors
     keep using `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` + `uv run`,
     unaffected and unassisted by `flake.nix`**, and a worktree is a directory direnv has never seen.
     Phase 64's NIX-05 measurement is what this text reports; if that measurement found the shims
     *are* reachable in a fresh worktree, the section says so and still keeps the provisioning
     recipe mandatory (constraint 11, Pitfall 3).

     > **AMENDED 2026-09-12 (Phase 68 discuss, owner-approved).** "Unaffected and unassisted by
     > `flake.nix`" is false on the maintainer's NixOS machine, measured by Phase 64's NIX-05
     > (`64-NIX05-WORKTREE-EVIDENCE.md`, `64-GAP-REMEASURE-EVIDENCE.md`). A fresh worktree's
     > `uv sync` builds `.venv` on uv-managed CPython, a generic-linux ELF NixOS refuses outside FHS
     > (rc 127), so `uv run …` in a worktree works only because the `uv` shim enters the FHS sandbox.
     > The shims reach the worktree solely through `PATH` inherited from a session launched in the
     > direnv-loaded main checkout (the worktree's own `.envrc` is never allowed). What stays
     > binding: the provisioning recipe is unchanged and mandatory, `flake.nix` does not substitute
     > for it, and `CLAUDE.md` states that boundary explicitly — now as "the recipe itself runs
     > through the shims, which arrive by inheritance, not by direnv". Separately, the manual
     > `ln -sf` / `patchelf` guidance was never in `CLAUDE.md` (`git log -S` finds zero commits for
     > either term), so its retirement is satisfied vacuously and is evidenced, not edited. The
     > verifier reports the literal and amended readings separately. See `68-CONTEXT.md` D-01..D-03.

  2. **`tox.ini`'s rationale comment describes the pin that is actually there.** The `tox-uv-bare`
     rationale block — the one explaining that the bundled `uv` wheel's generic-linux ELF cannot
     exec on NixOS — is replaced by one describing the current `tox-uv` pin and why the revert is now
     safe, **keeping the `~=` ini-parser constraint stated** in full: tox's ini-list loader splits a
     single-line `requires` on commas, so `>=1.35,<2` breaks tox's startup and `~=1.35` is the
     comma-free equivalent. A repository-wide grep finds no surviving `tox-uv-bare` rationale
     presented as current (DOC-20).

  3. **`flake.nix` carries notes explaining its own structure, including what cannot be verified.**
     The file explains the FHS wrapper (why `mkShell` stays the devShell and why the two obvious
     alternatives were falsified), **which commands are shimmed and why** those and not others — the
     namespace-inheritance finding that only top-level entrypoints need shims — and the darwin
     per-system guard. The darwin note states plainly that **darwin is unverified by construction**:
     `buildFHSEnv` is Linux-only, no maintainer machine can exercise the guard's darwin branch, and
     **no CI lane covers `flake.nix` at all**, so a darwin contributor should report breakage
     directly rather than assume CI would have caught it (DOC-21, constraint 8).

**Plans**: 4 plans (2 waves; 68-01, 68-02 and 68-03 edit disjoint files in parallel in wave 1; 68-04 measures the merged tree in wave 2; no checkpoints)

Plans:
**Wave 1**

- [x] 68-01-PLAN.md — D-01..D-08: CLAUDE.md line 11 and the Conventions bullet name the landed `tox-uv~=1.35` pin; a new `### NixOS development shell` subsection (shims, launch prerequisite and shim check, no manual step, locale, interpreters); a boundary paragraph above the byte-identical provisioning recipe; D-02 vacuity evidenced at base
- [x] 68-02-PLAN.md — D-13/D-14/D-16: `tox.ini`'s `requires` comment rewritten (pin, ini-parser constraint in full, why `tox-uv` is safe, one-line history, equivalence re-measured) and the two test files' stale prose moved to the post-Phase-68 state, text only (masked AST hash unchanged)
- [x] 68-03-PLAN.md — D-09..D-12: `flake.nix` header notes (FHS wrapper and the two falsified alternatives, shimmed commands and namespace inheritance, darwin unverified by construction, archive-stable sources) and per-element notes, comments only (four drvPaths byte-identical)

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 68-04-PLAN.md — D-15: repository-wide `tox-uv-bare` grep on the merged tree with every hit classified, SC#1 literal and amended readings, SC#3 with merged-tree drvPaths, cross-file consistency, full suite plus black and ruff, DOC-19..DOC-21 closure

**UI hint**: no

### Phase 69: v0.9.3 Close Prep (prep-only, unpublished)

**Goal**: the milestone is packaged for a merge to `main` and nothing else. This is a **toolchain**
milestone that ships nothing to users: no version bump, no tag, no PyPI upload, no GitHub Release.
The CHANGELOG bullets go under `## [Unreleased]` and stay there — the same shape v0.9.1 used, but
decided up front rather than after the close.

The one irreversible action this milestone does take — opening and merging the PR to `main` — is
**REL-12**, and per this project's convention held for nine consecutive milestones it executes at
`/gsd-complete-milestone`, not inside this phase. REL-12 is cited here for coverage only, its
checkbox stays `[ ]` through every plan, and constraint 14's checksum fence is what keeps it there.

**Depends on**: Phase 68
**Requirements**: REL-12
**Success Criteria** (what must be TRUE):

  1. **The tree is proven unpublished-shaped, probed with positive controls.** `pyproject.toml`
     still reads `0.9.2` and no commit in this milestone bumps it; `git tag -l 'v0.9.3'` and a
     remote tag probe both come back **empty**, each remote probe carrying a positive control so an
     empty result is distinguishable from a broken probe; no PyPI upload and no GitHub Release exist
     for `0.9.3`. `git diff` over the milestone shows **no change under `typsphinx/`** — the
     constraint-13 fence, measured rather than asserted.

  2. **The CHANGELOG carries this milestone's work under `## [Unreleased]` and creates no release
     section.** The toolchain and dependency-update work is described under the existing
     `## [Unreleased]` heading; `grep` confirms **no `## [0.9.3]` heading and no `[0.9.3]` tail
     link** exist anywhere in `CHANGELOG.md`, and the `[Unreleased]` compare base is left at
     `v0.9.2` because nothing was released. `scripts/extract_changelog_section.py` is **not** run
     for a `0.9.3` section, because no such section is created.

  3. **The tree is proven green on runs executed in this phase, not on a prior phase's word.** Full
     pytest suite, `black --check .`, `mypy typsphinx/`, and both docs tox environments against a
     warning baseline taken from a **clean** build (`rm -rf docs/_build` first — an incremental
     rebuild under-reports warnings and manufactures a false "baseline match"), plus one fresh 3-OS
     CI run dispatched on this phase's own tip with every job conclusion transcribed literally, both
     `windows-latest` lanes named, and `ruff` green in that run's `Lint and Format Check` job.

  4. **The REL-12 checkbox is proven held by a recorded SHA-256, and the handoff is standalone.** A
     `69-CLOSEOUT-GUARD.md` records `sha256sum .planning/REQUIREMENTS.md`, `wc -l`, the
     `PHASE_BASE_SHA` and the verbatim guarded lines (`grep -n 'REL-12'`) at phase head; the same
     commands re-run MATCH at phase close **and once more after `phase.complete`-family tooling has
     run** — the third observation being the one that actually catches the flip (constraint 14).
     Every plan's `SUMMARY.md` frontmatter declares `requirements-completed: []` for REL-12, and the
     checkbox is read directly out of `.planning/REQUIREMENTS.md` as `[ ]` at close, never inferred
     from frontmatter. A `69-HANDOFF.md` enumerates every step `/gsd-complete-milestone` must
     execute: opening the PR from the canonical milestone branch to `main`, the CI checks that must
     be green before merge, the merge itself, and the explicit statement that **no tag is pushed, no
     PyPI upload is made and no GitHub Release is created** — with `typsphinx-doc-translations`'
     `update-pin.yml` dispatch and the Read the Docs `stable` verification both **not applicable**,
     because nothing is released.

**Plans**: 6 plans (3 waves; 69-01 and 69-02 run in parallel in wave 1; 69-03, 69-04 and 69-05 run in parallel in wave 2, 69-04 being the phase's only push and CI dispatch; 69-06 closes the fence and writes the handoff in wave 3; no checkpoints)

Plans:
**Wave 1**

- [x] 69-01-PLAN.md — D-01..D-05: three `### Changed` bullets (TOX, DEP, NIX) under the existing `## [Unreleased]`, pure addition, both docs environments built clean before and after the edit
- [x] 69-02-PLAN.md — D-12: phase-head REQUIREMENTS.md checksum guard naming both transition entry points; SC#1 observation 1 with a positive control on every remote probe; the no-external-API COVERAGE.md

**Wave 2** *(blocked on Wave 1 completion)*

- [ ] 69-03-PLAN.md — D-06: full suite twice (once under LC_ALL=C), black, mypy, ruff, the version-sync family, the changelog page gate with 0 skipped, both docs environments clean against the baseline
- [ ] 69-04-PLAN.md — D-13/D-14: decoy re-check, fast-forward push of the canonical branch, one CI dispatch, 12-job census with both windows-latest and macos-latest lanes, ruff from Lint and Format Check
- [ ] 69-05-PLAN.md — D-07/D-08/D-10: non-committing trial merge of origin/main, merged lock and merged-tree lint, main protection and merge-method census, dependabot PR census

**Wave 3** *(blocked on Wave 2 completion)*

- [ ] 69-06-PLAN.md — D-08..D-13: SC#1 observation 2, phase-scoped typsphinx/ diff, close-time fence re-verification, and the negative-first standalone 69-HANDOFF.md

**Cross-cutting constraints:**

- REL-12 is cited for coverage only; SUMMARY requirements-completed: [].

**UI hint**: no

## Progress

**Execution Order:** phases execute in numeric order within a milestone (decimal insertions between
their surrounding integers), with the prep-only close phase last. Two of the arrows are real
dependencies rather than convention: **64 → 65**, because reverting the `tox-uv` pin before the FHS
wrapper is proven reintroduces exactly the defect `tox-uv-bare` was chosen to avoid; and
**66 → 67**, because the proof requires dependabot PRs that only exist once the ecosystem switch is
live. **Phase 66 has no dependency on Track A at all** — CI runs on GitHub-hosted runners and never
touches NixOS, and the two tracks share no file and no mechanism — so 66 and 67 may be planned and
executed in parallel with 64 and 65. Phase 68 is last on both tracks so the documentation describes
the landed shape, and Phase 69 follows it.

Phases 1–63 shipped or completed across v0.4.4 → v0.9.2; their per-phase plan counts, statuses and
completion dates are preserved in each milestone's archived roadmap under `milestones/`. The table
below tracks the active milestone only.

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 64. FHS Wrapper and Command Shims in `flake.nix` | v0.9.3 | 6/6 | Complete    | 2026-09-12 |
| 65. `tox-uv-bare` → `tox-uv` Revert, on the uv Path tox Actually Resolves | v0.9.3 | 2/2 | Complete    | 2026-09-12 |
| 66. `.github/dependabot.yml` — `pip` → `uv` Ecosystem | v0.9.3 | 4/4 | Complete    | 2026-09-12 |
| 67. Proof on a Real Dependabot PR, Then Disposal of #123 and #128 | v0.9.3 | 5/5 | Complete    | 2026-09-12 |
| 68. Documentation Follow-Through — `CLAUDE.md`, `tox.ini`, `flake.nix` | v0.9.3 | 4/4 | Complete    | 2026-09-13 |
| 69. v0.9.3 Close Prep (prep-only, unpublished) | v0.9.3 | 2/6 | In Progress | - |

## Roadmap Evolution

Per-milestone evolution notes are archived with their milestone. v0.9.2's — the four decisions baked
into the 62–63 split, the inverted `gsd/v0.9.2-milestone` decoy-branch correction, and the two
PROJECT.md target-feature claims research falsified before the roadmap was written — live in
[milestones/v0.9.2-ROADMAP.md](milestones/v0.9.2-ROADMAP.md).

- **2026-09-02** — v0.9.3 roadmap created: **Phases 64–69**, 21/21 v1 requirements mapped, zero
  orphans, zero duplicates, continuing numbering from v0.9.2's Phase 63. Six phases at
  `granularity: standard`, which nominally suggests 4–6 — at the top of the range, because this
  milestone contains **two independent tracks** rather than one, and compressing across the track
  boundary would couple work that shares no file and no mechanism. Four decisions are baked into
  the structure and should not be re-derived during planning:

  - **`research/SUMMARY.md`'s A1 / A2 / B1 / B2 / C structure is adopted whole**, as Phases 64, 65,
    66, 67 and 68. No boundary was moved. Its two hard orderings (A1 → A2, B1 → B2) and its
    statement that the tracks share nothing are constraint 1.

  - **All eight NIX requirements are one phase, not two.** NIX-02/03/04 (every tox environment,
    every documented command, the full suite) are the *acceptance criteria* of the mechanism NIX-01
    and NIX-05..08 deliver; splitting them out would manufacture a phase that is pure verification
    of another phase's work, which is the anti-pattern the granularity guidance names. The research
    reached the same conclusion independently.

  - **DEP-03 and DEP-04 are mapped to Phase 66, not 67**, following the research's own assignment:
    both are questions about whether the *configuration* behaves as intended, and DEP-04's answer
    can invalidate the approach before any PR is judged. DEP-05 carries the grouped-update
    **coverage-gap record** (Pitfall 7) so nothing is duplicated between the two.

  - **DOC-19..21 and REL-12 are separate phases (68 and 69), not one.** The house convention is a
    prep-only final phase, held for nine consecutive milestones; more concretely, constraint 14's
    whole-file SHA-256 fence on `.planning/REQUIREMENTS.md` only works in a phase where no other
    requirement checkbox is meant to move, and DOC-19/20/21 legitimately move three.

- **2026-09-02** — **The `gsd/v0.9.3-*` decoy pair is live and inverted, exactly as v0.9.2's was.**
  Measured at roadmap time: the canonical config-derived branch
  `gsd/v0.9.3-toolchain-and-dependency-update-repair` is at `efffd892` (`main` + 1), while
  `gsd/v0.9.3-milestone` is at `7d1f4a70` (canonical + 3) and is where HEAD sits;
  `git merge-base --is-ancestor` confirms the canonical branch is an ancestor of the decoy, so
  nothing has diverged. Deleting the decoy first — the correction v0.9.1 ran — **would orphan three
  commits**: the AMENDED block, the research commit and the requirements commit. The canonical
  pointer must be fast-forwarded to `7d1f4a70` before `gsd/v0.9.3-milestone` is deleted. Nothing
  matching `0.9.3` exists on `origin`. Phase 64 carries both the correction and the push as SC#5.
  **The roadmapper did not perform the correction** — it is recorded here for the first executing
  phase, and confirmed live at the time of writing.

- **2026-09-02** — Two structural facts inherited from PROJECT.md's `AMENDED 2026-09-02` block are
  load-bearing here and must not be re-litigated during planning. **(1) The dependabot fix is a
  native ecosystem switch, not a custom workflow.** The milestone was scoped with an Actions
  workflow that would run `uv lock` on dependabot PRs and push the result; research falsified that
  as the right mechanism and the owner approved the replacement. Every failure mode Pitfalls
  research documented — the forced read-only `GITHUB_TOKEN`, `pull_request_target` exposure,
  `GITHUB_TOKEN` pushes not retriggering CI, dependabot force-pushing over commits lacking
  `[dependabot skip]` — belongs to the superseded workflow and **does not apply to Phases 66–67**.
  The workflow survives as a fallback reachable only if DEP-04 finds the v0.11/v0.12 gap bites; its
  pitfalls are recorded in `research/PITFALLS.md` §§ 4–6 against that contingency. **(2) The FHS
  design space is already narrowed by measurement**: `buildFHSEnv`'s `.env` as a devShell and a
  `shellHook` that `exec`s into the wrapper were both falsified during scoping, so the devShell
  stays `mkShell` and the FHS is exposed as PATH command shims.

- **2026-09-02** — **The 3-OS CI matrix run was deliberately given no REQ-ID**, matching v0.9.1's
  and v0.9.2's decision. It remains the milestone's acceptance bar and is carried in the success
  criteria of the phases that need it (64 SC#5 as the pre-revert baseline, 65 SC#4 as TOX-04's own
  authority, 69 SC#3 on the close tip), dispatched fresh on each phase's own tip and never inferred
  from a prior run. The same applies to milestone invariant #5 (branch to `origin` in the first
  phase), which is constraint 10 rather than a requirement.

## Backlog

Candidate work not yet scoped into a milestone. Promote items with `/gsd-review-backlog`, or
pull a whole cluster into the next milestone via `/gsd-new-milestone`.
Numbered 999.x so milestone reorganization never renumbers or drops them.

New items land here as `999.x` entries. **No item is open** — the backlog has been empty since
2026-08-04. Item **999.1** (inline math after text: missing separator before `#mi()` causes a Typst
error) was promoted into v0.6.5 as Phase 34 / requirement MATH-01 and shipped 2026-07-29. Item
**999.2** (a captioned table drops the id of an immediately preceding standalone target) was promoted
into v0.7.0 as **Phase 42 / requirement TBL-03** and shipped in v0.7.0. Numbering does not reuse
retired numbers, so the next item filed here is **999.3**.

**Todos promoted into v0.9.3** (2026-09-02) — the two long-standing toolchain records this milestone
exists to close, each now carrying REQ-IDs and a phase:

- `2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos` → **Phase 64** (NIX-01 through NIX-08).
  Open since 2026-08-11 and raised at four consecutive closes; tracked as Future requirement QUA-06.
  Its live 2026-08-22 recurrence is the reason the fix must be measured in a **freshly provisioned**
  worktree venv (NIX-05) rather than on the main tree, whose stale binary masks it. The record's
  scope is `ruff` alone; this milestone deliberately widens it to the whole generic-linux-ELF class,
  because the namespace-inheritance finding makes one wrapper cover `ruff`, `tox`, `.venv/bin/uv`
  and the CPython tox downloads at once.

- `2026-08-16-dependabot-prs-die-on-uv-lock-locked-mismatch` → **Phase 66** (DEP-01, DEP-03, DEP-04)
  and **Phase 67** (DEP-02, DEP-05). `severity: major`; its `--locked` census — ten steps across
  four workflows, eleven at HEAD — is what made v0.9.0's D-13 sequencing constraint concrete, and
  every dependabot PR still dies before a single test runs. Note that this record was written
  against the *custom workflow* framing; PROJECT.md's `AMENDED 2026-09-02` block supersedes its
  proposed mechanism with the native `package-ecosystem: "uv"` switch. Its **acceptance criterion is
  unchanged** and is the one that matters: prove it on a real dependabot PR.

  **Requirement-ID note:** PROJECT.md's carried-forward list labels this defect "CI-01", but
  `CI-01`–`CI-05` were consumed by v0.5.0-era requirements. It is **DEP-01** here; `CI-*` is
  deliberately not reused.

Each todo record stays **pending** until its phase executes; the todo is the detail record, the phase
entry above is the sequencing record.

**Still open and deferred, not in v0.9.3 scope** (5 of the 7 pending todos):

- `2026-08-14-numref-number-diverges-per-master-and-vanishes-for-non-root-only-figures` (NUM-01,
  `severity: major`) — still excluded from every published surface by owner override D-07.

- `2026-08-29-hardcoded-delimiter-path-fragments-in-translator-relative-path-debug-logs` (MSG-06,
  `severity: minor`) — `translator.py:5047,5152` carry the same hardcoded-`'...'` delimiter shape
  Phase 60 closed in three other modules; the one-line fix is `quote_path()`, which now exists.
  **Explicitly out of reach this milestone**: it is a change under `typsphinx/`, which constraint 13
  forbids.

- `2026-08-16-root-toctree-duplicates-section-children-in-html-sidebar` — an HTML sidebar defect in
  this project's own docs `index.rst`.

- `2026-07-22-add-sphinx-linkcheck-ci-job` (Future LNK-01) — deferred again; a CI job, which
  constraint 3 puts out of scope by construction. Seventh consecutive close at which it is raised.

- `2026-07-22-modernize-typing-imports-drop-up006-up035-ignore` — deferred *doubly deliberately*:
  `CLAUDE.md` independently instructs "don't modernize typing imports until that todo lands", and it
  is a change under `typsphinx/`.

**Dormant seeds:** `SEED-001-readme-quickstart-typst-documents-pdf` (substantially discharged by
v0.7.1's CONF-08 + DOC-11 and v0.8.0's DOC-14), **`SEED-003-tox-dependency-groups-per-env`** (Future
QUA-07 — splitting the `dev` extra into PEP 735 `[dependency-groups]`; **adjacent to this milestone's
`tox.ini` work and explicitly kept dormant by PROJECT.md's scope statement**, so a phase touching
`tox.ini` must not absorb it opportunistically), and **`SEED-004-typst-py-maintenance-risk-vendored-compile-path`**
— `typst-py` upstream maintenance is slowing and typsphinx may eventually need to carry an equivalent
compile path. Still the single largest structural risk on the horizon, and still never scoped into
any milestone across four consecutive closes.

**Known limitations still shipped with no published surface** after v0.9.2, carried unchanged into
this milestone because it touches no product code: WR-02's `confdir` gap, the tripled "Custom
template not found" warning, and NUM-01's `numref` per-master divergence. That is the **fifth
consecutive** cycle at which a `### Known Limitations` section was declined; the decision remains
open for the next release cycle, and v0.9.3 does not force it, because v0.9.3 publishes nothing.

**New standing risk arising from this milestone:** `flake.nix` becomes load-bearing while keeping
**zero CI coverage** — no workflow references `nix` or `flake`, so a breaking edit is caught only
when the maintainer next enters the shell, and the darwin branch of the per-system guard cannot be
exercised from a Linux machine at all. Accepted deliberately as the consequence of leaving CI
unchanged (owner decision 2026-09-02). Recorded in REQUIREMENTS.md § Future Requirements → "Arising
from this milestone", carried as constraint 8 above, and documented on the surface itself by DOC-21.

---
*Roadmap created: 2026-07-04 · Reorganized at each milestone close: v0.4.4 (2026-07-05), v0.5.0 (2026-07-11), v0.6.0 (2026-07-13), v0.6.1 (2026-07-19), v0.6.2 (2026-07-23), v0.6.3 (2026-07-25), v0.6.4 (2026-07-28), v0.6.5 (2026-07-29), v0.7.0 (2026-08-04), v0.7.1 (2026-08-11), v0.8.0 (2026-08-15), v0.9.0 (2026-08-22), v0.9.1 (2026-08-30 — completed, not published), v0.9.2 (2026-08-31). Per-milestone phase detail, success criteria, and decisions for completed milestones live in `milestones/vX.Y-ROADMAP.md`. Active milestone: v0.9.3 (Phases 64–69), roadmap created 2026-09-02.*
