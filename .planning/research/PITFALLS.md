# Pitfalls Research

**Domain:** Toolchain/CI maintenance on a mature, PyPI-published Python package — adding a `buildFHSEnv` + command-name-shim layer to an existing `mkShell`/direnv `flake.nix`, reverting `tox-uv-bare` → `tox-uv`, adding a dependabot lockfile-regeneration workflow, and disposing of two stale dependabot PRs. No product/runtime code changes.
**Researched:** 2026-09-02
**Confidence:** MEDIUM overall (cross-checked against GitHub's own docs and `tox-uv`'s own README/PyPI page for the token-retrigger and uv-discovery-order claims; the buildFHSEnv sandbox-internals claims are LOW confidence / flagged unverified — this repo has no prior FHS experience to check against, and the milestone's own scoping already found several of the "obvious" designs (FHS-as-devShell, `shellHook exec`) don't work, which is itself a warning that this surface is undertested)

## Critical Pitfalls

### Pitfall 1: `tox-uv`'s own bundled-`uv` discovery silently reinstates the exact ELF the milestone is retiring

**What goes wrong:**
`tox-uv` (the full meta package) resolves its `uv` binary in this order: `TOX_UV_PATH` env var → **bundled `uv` wheel shipped inside the `tox-uv` package itself** → system `PATH`. `tox-uv-bare` skips the middle step and goes straight to `PATH`. Reverting `tox-uv-bare` → `tox-uv` reintroduces step 2. If `TOX_UV_PATH` is not set, `tox -e py312`/`-e lint`/`-e type` will happily find and execute `tox-uv`'s **own bundled generic-linux `uv` wheel** — the same class of ELF `/lib64/ld-linux-x86-64.so.2` stub-loader rejection this milestone exists to fix — completely bypassing whatever `uv` the FHS wrapper puts on `PATH`.

**Why it happens:**
The milestone's own binding measurement ("`tox-uv` works under FHS: `uv.find_uv_bin()` returns `.venv/bin/uv`") tests **`uv`-the-Python-package's own `find_uv_bin()`** — the function `uv`'s build backend uses to locate its own CLI, which does look at `.venv/bin` and `PATH`. This is a **different code path** from `tox-uv`-the-tox-plugin's discovery order documented above. Conflating the two functions because they share a name pattern is an easy mistake, and it means the milestone's headline verification claim may not actually cover the risk it looks like it covers.

**Consequences:**
`tox -e py312` (or any `uv-venv-lock-runner` env) fails locally with the identical `Could not start dynamically linked executable` stub-loader error the milestone is meant to eliminate — but now *silently reintroduced by the revert itself*, not by anything the FHS wrapper failed to do. Worse, it could pass intermittently depending on which of `tox-uv`'s internal call sites get hit first, producing a flaky-looking failure that's actually deterministic once understood.

**Prevention:**
Before completing the revert, explicitly test `tox -e py312` (not just `ruff --version` or `uv --version`) under the FHS wrapper and confirm — by printing the resolved `uv` path/version from inside a tox run (`uv --version` invoked as the very first `commands =` line, or `TOX_UV_VERBOSE`-style tracing) — which binary actually ran. If the bundled one wins, set `TOX_UV_PATH` in the FHS wrapper's environment to force PATH-resolution of the shimmed/venv `uv`, or fall back to keeping `tox-uv-bare`.

**Detection:**
`tox -e py312 -- -v` (or equivalent) failing with the stub-loader message *after* the revert, on a machine where `ruff --version` and bare `uv --version` (run directly, not through tox) both succeed under the shim.

**Phase to address:**
tox-uv revert phase — this is the single highest-risk item for that phase and should be its primary verification target, not `uv --version` alone.

---

### Pitfall 2: A command shim that resolves back to itself inside the FHS sandbox (self-recursion)

**What goes wrong:**
A shim script's job is "put `ruff` on `PATH`, and running it execs into the FHS wrapper, which then runs the real `ruff`." If the FHS sandbox's own internal `PATH` is inherited from (or overlaps with) the outer shell's `PATH` — which is exactly what a `mkShell`-based devShell naturally does — and the shim invokes the wrapped command *by bare name* (`exec ruff "$@"`) rather than by an explicit, un-shadowable path (`.venv/bin/ruff`, or the FHS wrapper's dedicated named binary), the command resolves back to the same shim inside the sandbox, calling itself again.

**Why it happens:**
`buildFHSEnv`'s generated wrapper binaries are themselves just names placed on `PATH`; nothing about the mechanism prevents the sandbox's internal `PATH` from containing the same shim directory the outer shell used to reach the wrapper in the first place, unless the wrapper's own `runScript`/environment setup deliberately excludes it.

**Consequences:**
Infinite recursion — either a stack/fork-bomb-shaped resource exhaustion, or (if bwrap has depth/PID limits) a confusing crash with no clear message pointing at the cause. This is the kind of failure a one-off smoke test (`ruff --version` run once, interactively) is unlikely to reproduce reliably, because the recursion depends on exactly how the shim resolves `ruff` inside vs. outside the sandbox — a detail easy to get right by accident on the first try and wrong after an unrelated refactor.

**Prevention:**
Every shim must invoke the wrapped tool through a path that cannot re-resolve to the shim itself: either the tool's absolute `.venv/bin/<tool>` path, or the FHS wrapper's own dedicated entry-point name (distinct from the shimmed command name), with the sandbox's internal `PATH` explicitly scoped to exclude the outer shim directory. Verify with a canary: temporarily `rm` (or rename) the `.venv/bin/<tool>` target and confirm the shim fails with a clear "not found" rather than hanging.

**Detection:**
A shimmed command that never returns, or returns only after visibly climbing memory/CPU, especially after any change to how `PATH` is constructed in either the outer `mkShell` or the FHS wrapper's `runScript`.

**Phase to address:**
FHS wrapper + shims phase — include an explicit non-recursion check as part of that phase's success criteria, not just "the shim runs the tool once and prints the right version."

---

### Pitfall 3: Worktree executors skip provisioning because "the shim is on PATH now," reproducing the exact 45-test false alarm via a new mechanism

**What goes wrong:**
This repo's standing execution mode runs plan executors in isolated git worktrees, each requiring `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` before anything else, and `uv run` for every subsequent command (CLAUDE.md, "Worktree-isolated execution"). That recipe deliberately does **not** go through `flake.nix`/direnv/the FHS wrapper at all — it is a plain-shell, Nix-agnostic path chosen specifically because it already avoids the stub-ld problem. Once this milestone lands, a plan or executor could reasonably (and wrongly) assume the new FHS shims mean provisioning is no longer necessary, or write a verification step that calls a bare `ruff`/`tox` command expecting the shim to "just work."

**Why it happens:**
Worktrees are new directories outside the original checkout's already-`direnv allow`ed path. `.envrc`'s `use flake` does not auto-load for a directory direnv has never seen — a worktree needs its own `direnv allow` before the FHS shims exist there at all. An executor unaware of this distinction, seeing the milestone's "no more manual `ln -sf`/`patchelf` step" framing, is exactly the kind of person likely to skip the `uv sync --extra dev` step on the theory that the new Nix machinery has superseded it.

**Consequences:**
Same failure signature as the documented Phase 38-07 incident: 45 test failures, misdiagnosed as a code regression, when the actual cause is a missing local-provisioning step — except this time the false trail leads toward "the new FHS wrapper is broken" instead of toward "forgot to symlink," costing more investigation time because the new mechanism is less familiar.

**Prevention:**
Do not repurpose the FHS wrapper as a substitute for the worktree provisioning recipe. Documentation follow-through should state explicitly: the FHS wrapper is for the maintainer's interactive NixOS shell; automated worktree executors keep using plain `uv sync --extra dev` + `uv run`, unaffected and unassisted by `flake.nix`. Any plan step that invokes a shimmed command inside a worktree context should first confirm (`direnv status`, or simply checking whether the shim resolves) rather than assuming.

**Detection:**
A worktree-executed step failing with the stub-loader message, or with "command not found" for a tool the maintainer's shell resolves fine — check whether `direnv allow` was ever run for that worktree path before assuming a regression.

**Phase to address:**
FHS wrapper + shims phase (the CLAUDE.md documentation-follow-through work should state this boundary explicitly); flagged again for whichever phase updates the worktree-provisioning section.

---

### Pitfall 4: `GITHUB_TOKEN`-authored lockfile push leaves the PR's checks stuck on the old, failing run

**What goes wrong:**
GitHub's documented behavior: workflow runs that push commits using the default `GITHUB_TOKEN` do **not** trigger new workflow runs (except `workflow_dispatch`/`repository_dispatch`) — a deliberate anti-recursion guard. If the new lockfile-regeneration workflow pushes the regenerated `uv.lock` using the default token, the eleven `--locked` CI steps never re-run against the fix. The PR still shows red (or stale) checks even though the actual defect is resolved.

**Why it happens:**
It is the obvious first implementation — `permissions: contents: write` plus the default token is the path of least resistance, and it "looks like it worked" (the commit lands, `git log` shows it) while the thing that actually matters (a fresh, passing CI run) silently never happens.

**Consequences:**
The milestone's own required proof — "observe the install step succeed" on a real dependabot PR — cannot be obtained without either (a) noticing the checks never refreshed and manually re-running them, or (b) switching to a token that *does* retrigger CI (a PAT or GitHub App token), which raises Pitfall 5 below.

**Prevention:**
Decide up front whether the workflow needs to retrigger CI automatically. If yes, use a fine-scoped PAT or a GitHub App installation token (least privilege: `contents: write` on this repo only), not the default `GITHUB_TOKEN`. If the team accepts a manual "re-run checks" step after the lockfile push, document that explicitly so it isn't mistaken for a bug during verification.

**Detection:**
Compare the timestamp of the lockfile-regen workflow's push commit against the timestamp of the PR's most recent check run — if the check run predates the push, it did not see the fix.

**Phase to address:**
Dependabot lockfile-regeneration workflow phase.

---

### Pitfall 5: Elevating the token to fix Pitfall 4 opens the documented `recreate` + write-token exploit chain

**What goes wrong:**
The known "pwn request" pattern (publicly documented, Boost Security Labs) chains: a workflow with write access that reacts to a bot's PR → the bot's branch gets force-pushed (via `@dependabot recreate` or its own scheduled rebase) → the write-privileged workflow re-runs against attacker-influenced content. Any workflow that (a) checks out a dependabot branch, (b) runs arbitrary resolution (`uv lock`, which executes package build backends/metadata resolution — not fully inert), and (c) holds a token capable of pushing back with elevated permissions, has the shape this pattern targets.

**Why it happens:**
Solving Pitfall 4 (retriggering CI) pushes naturally toward "just use a more powerful token" without re-examining what that token can now do in combination with dependabot's own recreate/force-push behavior, which is itself attacker-triggerable via a PR comment on a public repository.

**Consequences:**
Worst case, a workflow scoped too broadly (e.g., a PAT with org-wide `contents: write`, or `pull_request_target` pointed at the PR head) becomes a supply-chain injection point. This repo's dependabot PRs are same-repository (not fork-originated), which removes the specific fork-identity-spoofing step of the published exploit, but the core risk — a write-capable workflow re-running attacker-influenced content after a force-push — is not eliminated by that alone if the workflow ever checks out and executes PR-branch content with a powerful token.

**Prevention:**
Scope the token to the minimum needed (repo-only `contents: write`, ideally a bot/machine account or GitHub App installation restricted to this repository, not a personal PAT with broad scope). Gate the workflow explicitly on `github.actor == 'dependabot[bot]'` and, if using `pull_request_target` at all, do **not** repoint `actions/checkout` at the PR head — prefer `pull_request` (same-repo dependabot branches don't need `pull_request_target`'s fork-secret-access rationale in the first place). Treat `uv lock` as executing semi-trusted content (it does resolve and may execute setup code for arbitrary declared packages) even though the *manifest* diff itself is dependabot's own proposal.

**Detection:**
Code review question for this phase: "what token does this workflow hold, and what could a comment-triggered `@dependabot recreate` force-push into the branch this workflow re-runs against with that token?"

**Phase to address:**
Dependabot lockfile-regeneration workflow phase — a security-review pass before merge, not an afterthought.

---

### Pitfall 6: Dependabot's own rebase/force-push silently discards the pushed lockfile fix

**What goes wrong:**
GitHub's documented dependabot behavior: it rebases and force-pushes over extra commits added to its own branches unless the commit message contains `[dependabot skip]` (or one of its variant spellings). A lockfile-regeneration commit pushed without that trailer can be wiped out the next time dependabot rebases the same PR (scheduled, or via `@dependabot rebase`/`recreate`), silently reverting the branch to its original stale-lockfile state.

**Why it happens:**
The magic trailer string is easy to miss because nothing about a successful first run signals its absence — the fix works, checks (eventually) go green, and the omission only surfaces on the *next* dependabot rebase cycle, which may be days later and look like an unrelated regression.

**Consequences:**
A fix that was "proven" once during this milestone's verification silently stops working on the next weekly dependabot cycle, reopening the exact defect this milestone closes, with no obvious trigger connecting the two events.

**Prevention:**
Include `[dependabot skip]` (or the project's chosen variant) in every commit the lockfile-regen workflow makes. Verify by triggering a dependabot rebase (comment `@dependabot rebase`) after the lockfile-regen workflow has run once, and confirming the pushed commit survives.

**Detection:**
`uv.lock` reverting to a state that predates a lockfile-regen commit, with no human-authored commit explaining the change — check `git log --oneline uv.lock` for a dependabot-authored commit landing after the regen workflow's commit.

**Phase to address:**
Dependabot lockfile-regeneration workflow phase.

---

### Pitfall 7: The grouped `sphinx-typst-stack` update is a harder resolution problem than either currently-open PR can prove

**What goes wrong:**
`dependabot.yml` groups `sphinx*`, `docutils*`, `typst*` (excluding `sphinx-autodoc-typehints`, `sphinx-intl`) into one PR that bumps multiple packages together. `#123` (`ruff`) and `#128` (`docutils`) are both single-package bumps. A grouped multi-package bump can hit a genuinely **unresolvable** dependency graph (not just a stale-lockfile mismatch) — e.g., a new Sphinx version's own floor conflicting with something else still pinned in `pyproject.toml`. The lockfile-regen workflow's `uv lock` step would then fail for a *different* reason than the one this milestone is fixing, and neither of the two named PRs can exercise that path because neither is a grouped bump.

**Why it happens:**
It's tempting to treat "prove the fix on a real dependabot PR" as satisfied by either #123 or #128 alone, since both are readily available and already stale. The grouped-update code path is untested by either.

**Consequences:**
A grouped `sphinx-typst-stack` PR arrives after this milestone ships, dies at `uv lock` with a real resolution conflict, and the workflow (correctly) does nothing to fix it — but if this failure mode wasn't anticipated, it can look like the milestone's fix regressed rather than encountering a case it was never scoped to solve.

**Prevention:**
Treat resolution-failure (not just `--locked` mismatch) as a distinct, expected outcome the workflow should handle gracefully (e.g., leave a comment or fail visibly rather than silently), and note in phase planning that proof-of-fix on #123/#128 alone does not cover the grouped-bump path — flag it as a known gap rather than letting it surface as a surprise.

**Detection:**
Watch for the next scheduled dependabot run to see whether it opens a `sphinx-typst-stack` grouped PR, and if so, treat its `uv lock` outcome as a second, independent data point beyond #123/#128.

**Phase to address:**
Dispose-stale-PRs / prove-fix phase — call this out explicitly as an accepted gap in that phase's closing notes, matching the milestone's own pattern of stating unverified items rather than asserting full coverage.

---

### Pitfall 8: Disposing of the stale PRs before proving the fix removes the only real dependabot PRs to test against

**What goes wrong:**
The milestone lists both "prove the fix on a real dependabot PR" and "dispose of the two stale dependabot PRs" as target features, without an explicit ordering. If the stale PRs (#123, #128) are closed first, there is no open, real dependabot PR left to observe the install step succeeding on — forcing whoever verifies the fix into exactly the hand-made-branch shortcut the source todo explicitly says "does not count."

**Why it happens:**
"Dispose of the stale PRs" reads like cleanup work suited to happen early or in parallel; it's not obviously sequenced after "prove the fix" unless someone notices the dependency.

**Consequences:**
Verification either stalls (waiting for a fresh dependabot run, which is weekly per `dependabot.yml`'s schedule) or gets faked with a hand-rolled branch, which the milestone's own acceptance bar explicitly rejects.

**Prevention:**
Sequence phases so at least one of #123/#128 stays open until the lockfile-regen workflow has been observed fixing its install step, *then* judge and close it on its merits (as intended) — or explicitly force a fresh dependabot run (re-triggering it, or waiting for the weekly schedule) before closing both, if closing early is preferred for other reasons.

**Detection:**
Phase plan review: does the plan sequence "prove fix" strictly before "close #123/#128," or leave the order ambiguous?

**Phase to address:**
Cross-cutting — should be pinned as an explicit phase-ordering decision during roadmap creation, not left to an executor's judgment mid-phase.

---

### Pitfall 9: `flake.nix` becomes load-bearing with zero CI coverage, and Darwin's per-system guard is untestable by the maintainer

**What goes wrong:**
This milestone explicitly makes `flake.nix` load-bearing (the FHS wrapper is no longer a "nice to have," it's the retirement mechanism for a documented recurring failure) while also explicitly leaving it out of CI (`nix` job is out of scope). `buildFHSEnv` is Linux-only, and `flake.nix` declares `x86_64-darwin`/`aarch64-darwin` systems, requiring a per-system guard so the FHS additions don't break `nix develop` on macOS. The maintainer's machine is NixOS (Linux) — there is **no way to locally verify the Darwin branch of the guard actually works**, and no CI lane checks it either.

**Why it happens:**
It's a natural consequence of the milestone's explicit scoping decision (no `nix` CI job), not a design mistake — but it's worth stating plainly because it creates a standing blind spot the milestone itself calls out as a "new standing risk."

**Consequences:**
A guard that's syntactically present but logically wrong (e.g., guards the wrong attribute, or still evaluates `buildFHSEnv` unconditionally for darwin systems inside a `let` binding that isn't actually skipped) would only be discovered by an actual Darwin contributor running `nix develop`/`direnv allow` and hitting a failure — with no automated signal pointing back at this milestone as the cause, potentially long after it merges.

**Prevention:**
At minimum, verify with `nix eval` / `nix flake show` for each declared system (including the darwin ones) that evaluation succeeds without attempting to actually build anything — this catches "guard is missing/wrong" eval-time errors without needing a macOS machine. Document in the flake's own structure notes (already planned as documentation follow-through) that Darwin is unverified-by-construction and any Darwin contributor should report breakage directly rather than assuming CI would have caught it.

**Detection:**
`nix flake check` (or `nix eval .#devShells.aarch64-darwin.default` etc.) failing or throwing on a Linux machine — this is checkable without Darwin hardware and should be part of this phase's verification even though it doesn't prove the shell actually *works* there.

**Phase to address:**
FHS wrapper + shims phase, with an explicit note carried into documentation follow-through.

---

### Pitfall 10: Version-skew shim — the shimmed tool doesn't match the pinned `uv.lock` version, silently diverging from CI

**What goes wrong:**
The milestone's own binding measurement states the bar precisely: `ruff --version` must report **0.15.20** (the `uv.lock`-pinned version), not nixpkgs' `0.15.14`. Any shim design that resolves the wrapped tool from a source other than the project's own `.venv` (e.g., falling back to a nixpkgs-provided binary when the venv one is momentarily missing, or resolving via a cached/global location instead of the current worktree's `.venv`) reintroduces exactly the divergence CI vs. local lint results this milestone is meant to eliminate — just moved from "doesn't run at all" to "runs, but disagrees with CI."

**Why it happens:**
A shim that degrades gracefully (falls back to *something* rather than failing loudly when `.venv` is missing/stale) is tempting to write for robustness, but robustness here directly conflicts with correctness — a silent fallback is worse than a loud failure, because it produces a plausible-looking but wrong lint pass.

**Consequences:**
A maintainer sees `ruff check .` pass locally via the shim, pushes, and CI fails on a rule difference between ruff versions — or the reverse, silently passing locally on a stricter/looser ruleset than CI enforces, undermining the "make lanes actually run" goal by replacing "doesn't run" with "runs but lies."

**Prevention:**
Shim scripts should fail loudly (non-zero exit, clear message) if the expected `.venv/bin/<tool>` doesn't exist, rather than falling back to any other source. Verification for this phase should assert the exact pinned version string, not just "the command exits 0."

**Detection:**
`ruff --version` (through the shim) not matching `uv.lock`'s pinned `ruff` version, checkable with a one-line grep/diff.

**Phase to address:**
FHS wrapper + shims phase.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|--------------------|-----------------|------------------|
| Skip the `TOX_UV_PATH` override and hope `tox-uv`'s bundled binary happens to work | Simpler `tox.ini`, one less env var to document | Reintroduces Pitfall 1's silent ELF failure on any environment where the bundled binary is discovered first | Never — verify discovery order explicitly instead |
| Use the default `GITHUB_TOKEN` for the lockfile-regen push and accept "checks don't auto-refresh" | No PAT/App-token setup, smallest permission footprint | PR appears red/stale even after the fix lands; humans must manually re-run checks every time | Acceptable only if explicitly documented and the team is fine re-running checks by hand each cycle |
| Prove the dependabot fix on a hand-made branch with a fresh `uv.lock` instead of waiting for a real PR | Fast to set up, doesn't depend on dependabot's schedule | Does not actually prove dependabot's own output installs cleanly — explicitly rejected by the source todo | Never, per this milestone's own acceptance bar |
| Treat `ruff --version` (or any single smoke command) as proof the FHS wrapper works | Fast verification, easy to script | Misses cwd/HOME/TMPDIR/locale/font-resolution/exit-code differences that only surface under a full `tox -e docs-pdf`-style real invocation | Acceptable only as a first smoke check, never as the sole verification gate |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|-----------------|-------------------|
| `tox-uv` ↔ `buildFHSEnv`/PATH shims | Assuming `uv.find_uv_bin()` (the `uv` package's own lookup, used by its build backend) and `tox-uv`'s internal uv-discovery order are the same mechanism | Test `tox -e py312` itself, not just `uv --version`, to see which binary `tox-uv` actually resolved (Pitfall 1) |
| GitHub Actions push ↔ dependabot's own rebase automation | Pushing a fix commit without `[dependabot skip]` in the message, assuming a one-time push is durable | Always include the skip trailer; verify survival across a manual `@dependabot rebase` (Pitfall 6) |
| `GITHUB_TOKEN` ↔ downstream workflow triggers | Assuming a workflow-pushed commit re-triggers CI the same way a human's push does | Use a scoped PAT/App token if re-triggering is required, and document the tradeoff explicitly (Pitfall 4, 5) |
| Worktree-isolated executors ↔ `flake.nix`/direnv | Assuming the FHS shims are available inside a freshly created worktree without `direnv allow` having been run there | Keep worktree executors on the existing `uv sync --extra dev` + `uv run` recipe, untouched by this milestone (Pitfall 3) |
| Dependabot grouped updates ↔ single-package proof PRs | Treating a pass on `#123`/`#128` as proof the lockfile-regen workflow handles the grouped `sphinx-typst-stack` case | Explicitly flag the grouped-update path as unverified by those two PRs alone (Pitfall 7) |

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|-----------------|
| Every shimmed command pays a fresh `bwrap` sandbox-entry cost | Editor-on-save `ruff`/`mypy` invocations feel noticeably slower than the un-shimmed `.venv/bin` equivalent | Measure interactive-latency overhead during the FHS phase; if unacceptable, consider caching or a persistent FHS session rather than a per-invocation wrapper | Immediately noticeable for tools invoked many times per minute (linters-on-save), not for one-off `tox` runs |
| Lockfile-regen workflow re-running `uv lock` (full resolution) on every dependabot push | CI minutes creep up on every grouped or rapid-succession dependabot update | Guard with a diff-check so the workflow no-ops (and doesn't even attempt a push) when the lockfile is already current | Noticeable once dependabot's weekly cadence overlaps with grouped multi-package PRs needing several rebase cycles |

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Granting the lockfile-regen workflow a broadly-scoped PAT or `pull_request_target` with a PR-head checkout | Documented "pwn request" chain: force-push (via `@dependabot recreate`) + write-privileged re-run of PR-branch content | Scope to repo-only `contents: write`; prefer `pull_request` over `pull_request_target` since dependabot PRs here are same-repo; gate on `github.actor == 'dependabot[bot]'` (Pitfall 5) |
| Treating `uv lock`'s manifest resolution as fully inert content | `uv lock` resolves and may touch package metadata/build-backend code for whatever versions dependabot proposes — not zero-trust-safe by default | Run resolution in a workflow with the minimum token/secret exposure needed, independent of whether the *push-back* step needs a more powerful token |
| Skipping least-privilege review because "it's just a lockfile bump" | Understates the actual permission surface (`contents: write` + secrets exposure) a seemingly small automation workflow ends up needing | Explicit security-review pass on this one workflow before merge, same rigor as any other `permissions:` grant in this repo's other workflows (see `release.yml`'s own `${{ }}`-in-`run:` injection-avoidance comment for the house standard) |

## "Looks Done But Isn't" Checklist

- [ ] **FHS shim passes a version check**: `ruff --version`/`uv --version` succeeding via the shim does not prove `tox -e py312`, `tox -e docs-pdf` (real font/subprocess resolution), or signal/exit-code propagation work — verify with a full `tox` run, not a smoke command.
- [ ] **`tox-uv` revert "works" locally**: confirm which `uv` binary `tox-uv` actually resolved (bundled vs. PATH/shimmed) — a passing `tox -e py312` doesn't tell you which path it took, and the wrong path is a latent regression (Pitfall 1).
- [ ] **Lockfile-regen workflow's push "succeeds"**: a green workflow run that pushed a commit does not mean the PR's CI checks reflect that commit — check the check-run timestamp against the push timestamp (Pitfall 4).
- [ ] **`flake.nix` evaluates cleanly**: `nix flake check` passing does not mean the Darwin devShell branch actually works — it only proves the guard doesn't throw at eval time on a Linux evaluator (Pitfall 9).
- [ ] **Dependabot PR disposal**: closing `#123`/`#128` "because CI is finally set up to handle them" is not the same as having *observed* the install step succeed on one of them before closing (Pitfall 8).
- [ ] **Grouped dependency-update coverage**: proving the fix on `#123` (ruff) or `#128` (docutils) alone does not cover the `sphinx-typst-stack` grouped-bump resolution path (Pitfall 7).

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|-----------------|------------------|
| `tox-uv`'s bundled binary wins over the shim (Pitfall 1) | LOW | Set `TOX_UV_PATH` to the shimmed/venv `uv` path, or revert `tox.ini`/`pyproject.toml` back to `tox-uv-bare` — a previously-proven-working one-line change |
| Shim self-recursion (Pitfall 2) | MEDIUM | Fix the shim to invoke by absolute path / distinct entry-point name; add the non-recursion canary test before re-enabling |
| Lockfile-regen workflow enters a push loop (Pitfall 19-class issue under Pitfall 4/6 discussion) | MEDIUM | Disable the workflow trigger, force-reset the branch with `git push --force-with-lease` to the last good commit, add a diff-guard, re-enable |
| Dependabot clobbers the pushed lockfile fix (Pitfall 6) | LOW | Re-push with `[dependabot skip]` in the commit message — this cannot be fixed retroactively on the already-clobbered commit, only forward |
| Darwin devShell silently broken (Pitfall 9) | MEDIUM (needs a Darwin reporter) | Fix the per-system guard once a concrete failure is reported; there is no way to proactively catch this without Darwin hardware or a future `nix` CI job |

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|-------------------|---------------|
| Bundled-`uv` discovery reinstates the ELF failure (P1) | tox-uv revert | `tox -e py312` (full run) resolves the intended `uv` binary, not just `uv --version` |
| Shim self-recursion (P2) | FHS wrapper + shims | Canary test: rename the target venv binary, confirm the shim fails cleanly rather than looping |
| Worktree executors skip provisioning (P3) | FHS wrapper + shims (+ documentation follow-through) | Explicit statement that worktree executors are unaffected/unassisted by `flake.nix`; a worktree run still requires `uv sync --extra dev` |
| `GITHUB_TOKEN` push doesn't retrigger CI (P4) | Dependabot lockfile-regeneration workflow | Check-run timestamp postdates the lockfile-regen push |
| Elevated token opens the recreate-exploit chain (P5) | Dependabot lockfile-regeneration workflow | Security-review pass: token scope, actor gate, `pull_request` vs. `pull_request_target` choice recorded |
| Dependabot clobbers the pushed fix (P6) | Dependabot lockfile-regeneration workflow | `[dependabot skip]` present in every regen commit; survives a manual `@dependabot rebase` |
| Grouped `sphinx-typst-stack` untested by #123/#128 (P7) | Dispose-stale-PRs / prove-fix | Explicitly documented as an accepted gap, or a grouped PR's resolution is separately observed |
| Disposal-before-proof ordering hazard (P8) | Cross-cutting (roadmap phase ordering) | Roadmap sequences "prove fix" strictly before "close #123/#128" |
| `flake.nix` load-bearing with zero CI/Darwin coverage (P9) | FHS wrapper + shims | `nix flake check`/`nix eval` succeeds for all four declared systems on the Linux evaluator; Darwin gap documented, not silently accepted |
| Shim version-skew from CI (P10) | FHS wrapper + shims | Exact `ruff --version` string asserted against `uv.lock`'s pinned version, not just exit-code 0 |

## Sources

- `.planning/PROJECT.md` — `## Current Milestone: v0.9.3` section (binding measurements, scope, explicit unverified items) — curated/repo, HIGH confidence (primary source, not web research)
- `.planning/todos/pending/2026-08-16-dependabot-prs-die-on-uv-lock-locked-mismatch.md` — repo, HIGH confidence
- `.planning/todos/pending/2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos.md` — repo, HIGH confidence
- `tox.ini`, `pyproject.toml`, `flake.nix`, `.envrc`, `.github/workflows/ci.yml`, `.github/workflows/drift.yml`, `.github/workflows/release.yml`, `.github/dependabot.yml` — repo, HIGH confidence (read directly)
- GitHub Docs, "Managing pull requests for dependency updates" (rebase-strategy, `[dependabot skip]`) — web, MEDIUM confidence (official docs, cross-checked)
- GitHub Docs, "Securely using pull_request_target" — web, MEDIUM confidence (official docs)
- GitHub Community Discussions #62346, #65321, #55906 — "`GITHUB_TOKEN`-authored pushes don't retrigger workflows" — web, MEDIUM confidence (multiple independent threads, consistent with official docs' recursive-run-prevention rationale)
- Boost Security Labs, "Weaponizing Dependabot: Pwn Request at its Finest" — web, MEDIUM confidence (single source, but consistent with GitHub's own `pull_request_target` security docs)
- `tox-uv` README / PyPI page (`tox-dev/tox-uv`) — uv discovery order, `tox-uv` vs. `tox-uv-bare` distinction — web, MEDIUM confidence (project's own documentation)
- NixOS/nixpkgs#31104, "chrootenv: buildFHSUserEnv doesn't work inside sandbox" — web, LOW confidence (single GitHub issue, describes nested-Nix-sandbox case specifically, not the `nix develop`/direnv interactive-shell case this milestone actually uses — flagged as unverified analogy, not a direct hit)
- General `buildFHSEnv`/Nix sandbox environment-variable behavior (`HOME`, `TMPDIR`, `/etc`, locale) — web, LOW confidence — no source found that directly measures `buildFHSEnv`'s runtime environment differences in the specific shape this milestone uses (command-name shims exec'd from an outer `mkShell`); flagged throughout as needing empirical verification during the FHS wrapper phase rather than asserted from these sources

---
*Pitfalls research for: typsphinx v0.9.3 toolchain/dependency-update repair milestone*
*Researched: 2026-09-02*
