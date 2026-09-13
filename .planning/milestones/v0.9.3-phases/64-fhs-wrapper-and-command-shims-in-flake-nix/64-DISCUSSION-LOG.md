# Phase 64: FHS Wrapper and Command Shims in `flake.nix` - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-03
**Phase:** 64-FHS Wrapper and Command Shims in `flake.nix`
**Areas discussed:** Shim roster and the `uv` bootstrap hole, Verification locus, Locale and `$HOME`
policy, Worktree reachability

**Gray-area selection:** all four presented areas were selected.

---

## Shim roster and the `uv` bootstrap hole

### Q1 — Which set of command names gets a shim?

| Option | Description | Selected |
|--------|-------------|----------|
| 7 names: `uv` `tox` `ruff` `black` `mypy` `pytest` `sphinx-build` | Covers every bare command CLAUDE.md documents. `sphinx-build` is documented at `CLAUDE.md:39-40` as a manual verification step and has a `.venv/bin` target (measured: `sphinx-build 9.1.0`). Satisfies the phase goal's "every documented bare command" literally. | ✓ |
| 6 names: research's recommended list | `uv` / `tox` / `ruff` / `black` / `mypy` / `pytest` — `research/ARCHITECTURE.md` Pattern 1's set, matching the names NIX-01's success criterion enumerates. `sphinx-build` would only be reached via `tox -e docs-*`. | |
| 2 names: `uv` and `tox` only | The minimum set under namespace inheritance. Everything else would have to be typed as `uv run <tool>`, forcing a rewrite of CLAUDE.md's bare-command list in Phase 68. | |

**User's choice:** 7 names.

### Q2 — How does the `uv` shim resolve its target?

Measured before asking: `.venv/bin/uv` does not exist today (`tox-uv-bare` ships no `uv` wheel); it
appears only after Phase 65's revert. `command -v uv` currently resolves to
`/nix/store/…-uv-0.11.25/bin/uv`.

| Option | Description | Selected |
|--------|-------------|----------|
| Two-step: `.venv/bin/uv` → nixpkgs `uv`, both through FHS | Works today and on a fresh clone (nix store leg), and switches to the `.venv` binary after Phase 65. Both legs absolute (the store path is fixed at eval time), so NIX-07's no-bare-name rule holds. Routing both through the sandbox is what makes `uv run <tool>` carry FHS into the whole worktree flow, which NIX-05 depends on. | ✓ |
| Wrap nixpkgs `uv` only, never look at `.venv/bin/uv` | No branch, simplest. But after Phase 65 the `uv` tox uses internally (`.venv/bin/uv`) and the one the shim uses (nix store, 0.11.25) would be different versions, complicating TOX-03's "which `uv` did tox resolve" observation. | |
| Do not shim `uv`; leave `pkgs.uv` bare on PATH | `uv` is a nix-built binary and runs natively, so it needs no FHS itself. But `uv run pytest` would then run outside the sandbox, so the mandatory worktree execution path never enters FHS and NIX-05 cannot be satisfied. | |

**User's choice:** Two-step resolution.

**Notes:** The two-step is the single documented exception to the strict no-fallback rule the other
six shims follow; the fallback target is a fixed store path, not a `PATH` lookup.

---

## Verification locus

### Q1 — Where are NIX-01…NIX-04 measured?

Measured before asking: in the main checkout, `.venv/bin/{ruff,black,mypy,pytest,tox,python3,sphinx-build}`
all exit 0 today, with `ruff` reporting exactly 0.15.20 — i.e. SC#1 already passes there with no shim.

| Option | Description | Selected |
|--------|-------------|----------|
| Fresh worktree, after `uv sync`, then every gate | Matches PROJECT.md's Phase 57 lesson ("a main-tree measurement can never detect the hazard"), NIX-05's own "freshly created git worktree" wording, and the project's standing worktree-isolated execution mode. | ✓ |
| Both fresh worktree and main tree | Worktree side detects the hazard; main-tree side would additionally confirm the shims do not break an already-working `.venv`. Roughly doubles gate time (1548 tests ×2, `docs-pdf` ×2). | |
| Delete the main `.venv` and re-sync in place | Reproduces the hazard without creating a worktree, but destroys a currently-working `.venv` and does not literally satisfy NIX-05's "freshly created git worktree". | |

**User's choice:** Fresh worktree only.

### Q2 — What artifact carries the NIX-07 rename test and the NIX-08 measurement?

| Option | Description | Selected |
|--------|-------------|----------|
| Verbatim record in an EVIDENCE markdown only | Uses the project's existing evidence convention; adds no new file surface. Future re-measurement is manual. | ✓ |
| EVIDENCE markdown plus a committed re-runnable script | e.g. `scripts/verify-fhs-shims.sh`. Would let the maintainer re-measure in one command and partially mitigate constraint 8's zero-CI-coverage risk, at the cost of new repository surface. | |
| A pytest test under `tests/` | Rides the suite so it cannot be forgotten, but no CI runner has `nix` (and the Windows/macOS lanes certainly do not), so it would be permanently skipped in CI — an always-skipped test mixed into the 1548. | |

**User's choice:** EVIDENCE markdown only.

---

## Locale and `$HOME` policy

### Q1 — If `docs-pdf` cannot reach its `@preview` packages from inside the sandbox?

Measured before asking: `~/.cache/typst/packages/preview` holds nine packages (`codly`,
`codly-languages`, `mitex`, `gentle-clues`, `fontawesome`, `linguify`, `modern-cv`, `xarrow`,
`charged-ieee`), so a warm cache likely needs nothing beyond `$HOME` passthrough.

| Option | Description | Selected |
|--------|-------------|----------|
| Fix it on the FHS side inside Phase 64 | Confirm `$HOME` bind, add `cacert` to `targetPkgs` if TLS turns out to be needed. SC#2 requires a real PDF (`%PDF` magic bytes, not exit 0) and names `docs-pdf` as the invocation exercising font resolution, subprocess spawning and exit-code propagation — NIX-03 cannot close without it. | ✓ |
| Assume a warm cache; record the cold-cache case | Likely sufficient in practice, but leaves cold-cache behaviour (new machine, CI) unmeasured. | |
| Send cold-cache handling to Future Requirements | Phase 64 would guarantee only warm-cache PDF generation. | |

**User's choice:** Fix it on the FHS side.

### Q2 — If the locale measurement shows in-sandbox behaviour differing from outside?

Measured before asking: `LANG=ja_JP.UTF-8`; the repository has a documented locale-dependent
"local green, CI red" defect class.

| Option | Description | Selected |
|--------|-------------|----------|
| Record it; document the consequence in Phase 68 | NIX-08 asks for measurement and a record, not a behavioural change. If the sandbox *masks* the defect class, that is written up in DOC-19/DOC-21 and the response is a separate decision. | ✓ |
| Pin `LC_ALL` in the shims to erase the difference | Mechanically aligns local with CI, but silently changes the maintainer's working locale and makes ja_JP-specific behaviour harder to observe. | |
| Run the full 1548-test suite under both locales | Would pre-empt one CI-only defect class locally, at roughly double the phase's gate time. | |

**User's choice:** Record only.

---

## Worktree reachability

### Q1 — How is shim reachability in a fresh worktree guaranteed?

Measured before asking, and it changed the premise the research had flagged as an open question:
this session's `PATH` is already the direnv-loaded flake devShell
(`DIRENV_DIR=-/home/yuta/Documents/typsphinx`, `IN_NIX_SHELL=impure`, and `nodejs` / `pnpm` / `git` /
`python3` / `uv` present as store paths — exactly `flake.nix`'s `packages`). The harness's
non-interactive Bash calls never fire direnv's prompt hook, so `PATH` is frozen at session start and
survives `cd` into a worktree.

| Option | Description | Selected |
|--------|-------------|----------|
| Rely on session inheritance; add a `command -v` reachability check at the head of the procedure | No new flake mechanism; NIX-05 closes on observing that the shims were in fact reachable in a worktree. The check guards the one case where inheritance does not hold — a session launched outside the project. | ✓ |
| A `direnv allow` step per worktree | `.envrc` is git-tracked so it lands in each worktree, but `/.direnv/` is machine-local and untrusted there. Relevant only to interactive shells, not to the non-interactive path that actually runs; and it is manual work every time. | |
| Wrap the provisioning line in `nix develop --command` | Fully direnv-independent and the most robust, but changes CLAUDE.md's mandatory line and ripples through every GSD worktree procedure — the opposite of research's "NO other CLAUDE.md wording needs to change" success shape. | |

**User's choice:** Session inheritance plus a reachability check.

---

## Wrap-up

Asked whether the seven captured decisions were sufficient to write CONTEXT.md, offering further
discussion of plan-split granularity, which SHA the SC#5 CI baseline is taken against, and whether to
confirm the shims do not disturb the main tree's existing `.venv`.

**User's choice:** Write CONTEXT.md.

## Claude's Discretion

- `targetPkgs` contents beyond what a failing measurement forces (starting from the minimal shape).
- Dropping `pkgs.uv` from the Linux devShell `packages` so the `uv` shim wins PATH ordering; darwin's
  package list unchanged.
- Exact wording and exit code of the shim's not-found message, and the shape of the upward `.venv`
  walk.
- Keeping the FHS derivation and shims inline in `flake.nix` rather than splitting to `nix/`.
- Plan split granularity, and the name/location of the evidence file(s).
- Which SHA the SC#5 CI baseline is dispatched against.

## Deferred Ideas

- A committed, re-runnable FHS verification script (`scripts/verify-fhs-shims.sh` or similar).
- Running the full test suite under two locales as standing practice.
- Cold-`@preview`-cache behaviour of `docs-pdf` inside the sandbox, if the warm cache masks it.
- Three todos matched by `todo.match-phase` but reviewed and not folded: typing-import modernization
  (forbidden this milestone), the `sphinx-build -b linkcheck` CI job (a workflow addition, excluded by
  ROADMAP constraint 3), and the root-toctree HTML sidebar duplication (unrelated domain).
