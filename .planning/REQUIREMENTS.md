# Requirements: typsphinx — milestone v0.9.3 "Toolchain and dependency-update repair"

**Defined:** 2026-09-02
**Core Value:** The `typst`/`typstpdf` builders produce correct, compilable, faithfully-rendered
output, and the documented configuration actually takes effect. This milestone serves that value
indirectly but concretely: the gates that protect it must be runnable by the maintainer, and the
dependency-update path that keeps the pinned ecosystem current must actually run tests.

**Scope note.** This is a toolchain and CI maintenance milestone. **No product or runtime code
changes**: nothing under `typsphinx/` is modified. No new runtime dependency, no new `typst_*`
config value, no `@preview` bump.

**REQ-ID note.** `NIX-*`, `TOX-*` and `DEP-*` are new categories. `DOC-*` continues from `DOC-18`
and `REL-*` from `REL-11`. **`CI-*` is deliberately not used**: `PROJECT.md`'s carried-forward list
labels the dependabot defect "CI-01", but `CI-01`–`CI-05` were already consumed by v0.5.0-era
requirements. That carried-forward item is **DEP-01** here.

## v1 Requirements

### NixOS execution (NIX)

- [x] **NIX-01**: `ruff check .` runs to completion on the maintainer's NixOS machine and reports
      **0.15.20** — the `uv.lock` version, not nixpkgs' 0.15.14
- [x] **NIX-02**: `tox -e lint`, `tox -e type`, `tox -e py312` and `tox -e py313` each run to
      completion on that machine
- [x] **NIX-03**: `tox -e cov`, `tox -e docs-html` and `tox -e docs-pdf` each run to completion, with
      `docs-pdf` producing a real PDF
- [x] **NIX-04**: the full test suite (1548 tests at milestone start) runs on that machine with no
      environment-caused failures
- [x] **NIX-05**: an executor in a freshly created git worktree can run the documented provisioning
      line and then every gate, with no manual `ln -sf` or `patchelf` step anywhere
- [x] **NIX-06**: `flake.nix` evaluates successfully on all four declared systems, including the two
      darwin ones
- [x] **NIX-07**: each shim resolves its target by absolute path and cannot recurse into itself,
      proven by a check that would catch bare-name resolution
- [x] **NIX-08**: the FHS sandbox's `$HOME`, `/etc` and locale behaviour is measured for this
      project's actual invocation, and its effect on the project's known locale-dependent test class
      is recorded

### tox-uv revert (TOX)

- [x] **TOX-01**: `pyproject.toml` declares `tox-uv` in place of `tox-uv-bare`, with `uv.lock`
      regenerated in lockstep
- [x] **TOX-02**: `tox.ini`'s `requires` names `tox-uv` in the comma-free `~=` form, and `tox` starts
- [x] **TOX-03**: the `uv` binary tox actually resolves is observed from inside a real tox run, with
      an isolated outside-FHS control proving the failure is the uv path rather than something that
      fails earlier
- [x] **TOX-04**: CI is green on the revert across every lane, CI being the authority

### Dependency updates (DEP)

- [x] **DEP-01**: `.github/dependabot.yml` uses `package-ecosystem: "uv"`, and dependabot opens PRs
      updating `pyproject.toml` and `uv.lock` in the same commit
- [x] **DEP-02**: on a real dependabot PR, the `uv sync --locked` step succeeds and the test / lint /
      type jobs actually run — observed, not inferred from a hand-made branch
- [x] **DEP-03**: the `sphinx-typst-stack` grouping, `labels` and `open-pull-requests-limit` are
      confirmed to behave as before under the new ecosystem, or the divergence is recorded
- [x] **DEP-04**: dependabot's supported uv version (`v0.11`) is measured against the uv that CI
      installs (`setup-uv` with `version: "latest"`, currently 0.12.x) and against this repo's lock
      `revision = 3`, and the result recorded
- [x] **DEP-05**: #123 and #128 are disposed of on their merits **after** DEP-02, with the
      grouped-update coverage gap explicitly recorded rather than passed over

### Documentation (DOC — continues from DOC-18)

- [ ] **DOC-19**: `CLAUDE.md`'s NixOS / worktree-provisioning section describes the landed mechanism
      and no longer instructs a manual shim step
- [ ] **DOC-20**: `tox.ini`'s `tox-uv-bare` rationale comment is replaced by one describing the
      current pin, keeping the `~=` ini-parser constraint stated
- [ ] **DOC-21**: `flake.nix` carries notes explaining the FHS wrapper, which commands are shimmed
      and why, and the darwin guard

### Release (REL — continues from REL-11)

- [ ] **REL-12**: the milestone is merged to `main` via a PR, with no tag, no PyPI upload and no
      GitHub Release, and `pyproject.toml` still at `0.9.2`

## Future Requirements

Tracked but not in this roadmap.

### Carried forward from earlier milestones

- **MSG-06**: `translator.py:5047,5152` quote `up_path`/`down_path` with a hardcoded `'...'`
  delimiter — the same MSG-02 shape Phase 60 closed in three other modules
- **NUM-01**: `numref` numbers diverge per master and vanish for figures reachable only from a
  non-root master
- **WR-02**: `templates_path` collision detection resolves against `srcdir` rather than `confdir`
- **WR-03**: the "Custom template not found" warning fires three times instead of two for one narrow
  shape
- **SEED-003**: split the `dev` extra into PEP 735 `[dependency-groups]` so each tox environment
  installs only what it needs
- A `sphinx-build -b linkcheck` CI job
- The `UP006`/`UP035` typing modernization (ruff `ignore` removal)
- The root `index.rst` toctree duplicating section children in the HTML sidebar

### Arising from this milestone

- **`flake.nix` has zero CI coverage while this milestone makes it load-bearing.** No workflow
  references `nix` or `flake`, so a breaking edit is caught only when the maintainer next enters the
  shell. Accepted deliberately as the consequence of leaving CI unchanged (owner decision
  2026-09-02); recorded here so it is a tracked risk rather than an implicit one.

## Out of Scope

Explicitly excluded, with reasons, so they are not re-proposed.

| Feature | Reason |
|---------|--------|
| A `nix` CI job, or migrating CI lanes to the flake | Owner decision 2026-09-02 — Windows cannot run nix and its lanes are load-bearing here (v0.7.0 cp1252, v0.7.1 path separator, all of v0.9.1); and the FHS wrapper is useless on runners that already have a real loader, so CI would not exercise this milestone's mechanism |
| Pinning `setup-uv`'s eleven `version: "latest"` steps | Same decision. Floating also gives early warning of new-uv regressions, which `drift.yml` partly exists to provide |
| Bumping `astral-sh/setup-uv@v7` → `@v10` | Noted during research (moving major tags ended at `v8` when immutable releases began); CI is unchanged this milestone |
| A custom `uv lock` regeneration workflow for dependabot PRs | Superseded by DEP-01 (owner-approved amendment 2026-09-02). Retained only as a fallback if DEP-04 finds the v0.11/v0.12 gap bites. Its own failure modes — forced read-only `GITHUB_TOKEN`, `pull_request_target` exposure, `GITHUB_TOKEN` pushes not retriggering CI, dependabot force-pushing over commits lacking `[dependabot skip]` — are all specific to it |
| System-wide `nix-ld` | Outside this repository's control; already declined by D-03/D-18 |
| `pkgs.ruff` in the devShell | nixpkgs ships 0.15.14 against NIX-01's exact-0.15.20 requirement — local and CI lint would diverge |
| `patchelf` / `autoPatchelfHook` post-sync hooks | Wrong lifecycle: they must re-run after every `uv sync` and every tox provisioning, which is the manual step this milestone exists to retire |
| Trimming `glibcLocales` in the FHS closure | Dropped during scoping — the 0.26 GiB increment is 0.2% of a 136 GiB store, and the override costs an overlay plus loss of binary-cache hits |
| SEED-003 (PEP 735 `[dependency-groups]`) | Stays dormant; tracked under Future Requirements |
| Any change under `typsphinx/` | This is a toolchain milestone by construction |

## Traceability

Which phases cover which requirements. Populated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| NIX-01 | Phase 64 | Complete |
| NIX-02 | Phase 64 | Complete |
| NIX-03 | Phase 64 | Complete |
| NIX-04 | Phase 64 | Complete |
| NIX-05 | Phase 64 | Complete |
| NIX-06 | Phase 64 | Complete |
| NIX-07 | Phase 64 | Complete |
| NIX-08 | Phase 64 | Complete |
| TOX-01 | Phase 65 | Complete |
| TOX-02 | Phase 65 | Complete |
| TOX-03 | Phase 65 | Complete |
| TOX-04 | Phase 65 | Complete |
| DEP-01 | Phase 66 | Complete |
| DEP-02 | Phase 67 | Complete |
| DEP-03 | Phase 66 | Complete |
| DEP-04 | Phase 66 | Complete |
| DEP-05 | Phase 67 | Complete |
| DOC-19 | Phase 68 | Pending |
| DOC-20 | Phase 68 | Pending |
| DOC-21 | Phase 68 | Pending |
| REL-12 | Phase 69 | Pending |

**Coverage:**

- v1 requirements: 21 total
- Mapped to phases: 21 ✓
- Unmapped: 0

**Phase distribution** (every v1 requirement maps to exactly one phase; no orphans, no duplicates):

| Phase | Requirements | Count |
|-------|--------------|-------|
| 64 — FHS Wrapper and Command Shims in `flake.nix` | NIX-01, NIX-02, NIX-03, NIX-04, NIX-05, NIX-06, NIX-07, NIX-08 | 8 |
| 65 — `tox-uv-bare` → `tox-uv` Revert, on the uv Path tox Actually Resolves | TOX-01, TOX-02, TOX-03, TOX-04 | 4 |
| 66 — `.github/dependabot.yml` — `pip` → `uv` Ecosystem | DEP-01, DEP-03, DEP-04 | 3 |
| 67 — Proof on a Real Dependabot PR, Then Disposal of #123 and #128 | DEP-02, DEP-05 | 2 |
| 68 — Documentation Follow-Through — `CLAUDE.md`, `tox.ini`, `flake.nix` | DOC-19, DOC-20, DOC-21 | 3 |
| 69 — v0.9.3 Close Prep (prep-only, unpublished) | REL-12 | 1 |

**REL-12 is mapped to Phase 69 for coverage purposes only.** Like every REL requirement in this
project it closes at `/gsd-complete-milestone`, not inside the phase; its checkbox is held at `[ ]`
through every plan behind the SHA-256 fence described in ROADMAP.md constraint 14.

---
*Requirements defined: 2026-09-02*
*Last updated: 2026-09-02 — traceability populated at roadmap creation (Phases 64–69, 21/21 mapped)*
