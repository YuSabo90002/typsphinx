# Pitfalls Research

**Domain:** Python package CI repair after long dependency drift (Sphinx extension wrapping typst-py + Typst Universe `@preview` packages, managed with uv/tox)
**Researched:** 2026-07-04
**Confidence:** HIGH for repo-specific findings (read directly from `pyproject.toml`, `tox.ini`, `.github/workflows/*.yml`, `typsphinx/writer.py`, `typsphinx/template_engine.py`, `typsphinx/templates/base.typ`, `typsphinx/pdf.py`); MEDIUM for the typst-py↔typst-compiler version-correspondence claim (no official doc states it explicitly, but it is the observed pattern and the basis for the empirical-verification method below).

## Critical Pitfalls

### Pitfall 1: Under-pinning — fixing typst but leaving sphinx/docutils to rot again

**What goes wrong:**
The team pins `typst` to a known-good 0.14.x and stops there, leaving `sphinx>=5.0` and `docutils>=0.18` open-ended in `pyproject.toml` (their current state). The next `uv lock --upgrade` or a contributor's fresh clone resolves `sphinx==9.x` / `docutils==0.22.x` again — the exact combination the 2026-07-04 CI failure evidence shows breaking lint (`black --check` reformatting 3 files) and cascading through the matrix. A second, sneakier variant: the pins are edited correctly in `pyproject.toml`, but `uv.lock` (already committed in this repo) is never regenerated with `uv lock`, so CI installs whatever the stale lock still contains — which may not even reflect the new pins at all, or (if CI ever adopts `uv sync --locked`) fails outright with "lockfile out of date."

**Why it happens:**
The instinct after finding one broken package (typst) is to pin only that package and declare victory, because the reproduction case (`unknown variable: kai`) is 100% attributable to typst 0.15. Sphinx/docutils look "not currently broken" once typst is pinned, so they're deprioritized. Lockfile regeneration is a separate, easy-to-forget step because `uv sync` (no `--locked`/`--frozen` flag) — which is what every job in `ci.yml`, `docs.yml`, and `release.yml` currently runs — will silently re-resolve and rewrite `uv.lock` if it's stale rather than erroring. That silent auto-repair hides the drift instead of surfacing it.

**How to avoid:**
- Add explicit upper bounds for every runtime dependency in `pyproject.toml`, not just `typst`: e.g. `sphinx>=5.0,<9`, `docutils>=0.18,<0.21` (pick the actual ceiling verified against the known-good combination), `typst>=0.14.1,<0.15`.
- After editing `pyproject.toml`, always run `uv lock` locally and commit the resulting `uv.lock` diff in the same commit as the pin change — never edit one without the other.
- Consider switching CI's `uv sync --extra dev` invocations to `uv sync --extra dev --locked` (see Pitfall 6) so a forgotten lock regeneration fails loudly in CI instead of silently drifting.

**Warning signs:**
- `git diff` shows `pyproject.toml` changed but `uv.lock` unchanged (or vice versa) in the same commit.
- `uv lock --check` (or `uv sync --locked` if adopted) reports the lock is out of date.
- Any dependency in `pyproject.toml` still has no upper bound after this milestone claims "pinned to known-good."

**Phase to address:**
The pin-and-lock phase (first phase of the milestone) — this is the phase whose entire job is to produce the known-good pin set. It must own the *whole* dependency graph (sphinx, docutils, typst, plus the dev/docs extras), not just the one package with the reproducible failure, and it must end with a regenerated, committed `uv.lock`.

---

### Pitfall 2: The 3-way `@preview` version desync

**What goes wrong:**
The bundled Typst Universe package versions (`codly:1.3.0`, `codly-languages:0.1.1`, `mitex:0.2.4`, `gentle-clues:1.2.0`) are hardcoded as duplicated string literals in **three independent places**:
1. `typsphinx/writer.py` lines 94-97 (import block emitted for *included* documents)
2. `typsphinx/template_engine.py` lines 313-316 (import block emitted for *master* documents using the file-based template path)
3. `typsphinx/templates/base.typ` lines 8, 14, 19 (the inline default template)

When fixing the `kai` break, it is very easy to bump the version in one or two of these and miss the third — e.g. editing `writer.py` and `template_engine.py` (the Python-visible ones a grep for "codly" surfaces first) but forgetting `templates/base.typ` because it's a non-Python asset file that doesn't show up in a `.py`-scoped search, or vice versa. The result: master documents render with one package version, included documents (or documents using the inline default template vs. the file-based template path) render with another. This is invisible in most tests because the visible symptom is subtle (a package changelog behavior difference, not necessarily a hard error) — it will not reliably reproduce as a CI failure, making it a silent inconsistency rather than a loud break.

**Why it happens:**
This is a known, already-documented tech-debt item (see `CONCERNS.md` "Hardcoded Typst Package Versions") — there is no single source of truth for these four version strings, so any edit requires manual, exhaustive grep-and-replace across non-uniform file types (`.py` and `.typ`).

**How to avoid:**
- Before editing, run `grep -rn '@preview/' typsphinx/` to enumerate every occurrence (there are exactly 3 files, 4 packages each = up to 12 literal strings) and edit all of them in the same commit.
- Add a single regression test that parses all three emission paths (`writer.py`'s included-document branch, `template_engine.py`'s master-document branch, and the literal contents of `templates/base.typ`) and asserts the four package version strings are identical across all three — this converts "must remember to check" into "CI fails if you forget."
- Do NOT use this milestone to build the full configurable-version system (`typst_package_versions` config value) proposed in `CONCERNS.md` — that's explicitly out of scope per `PROJECT.md`. The fix here is: pin all three locations consistently, and add the cross-file consistency test, nothing more.

**Warning signs:**
- `grep -rn "codly\|mitex\|gentle-clues" typsphinx/` returns version strings that don't all match after an edit.
- Integration tests pass but a manual diff of a master-document `.typ` output vs. an included-document `.typ` output shows different `#import` version pins.
- No test currently exists to catch this (confirmed via `TESTING.md` — the existing test suite covers rendering behavior, not cross-file version-string consistency).

**Phase to address:**
Same phase as Pitfall 1 (the pin phase) — it must include a checklist step "update all 3 `@preview` locations" and the new consistency test, and that test must run in the same phase before moving on, not be deferred.

---

### Pitfall 3: Guessing the typst pin instead of empirically confirming it

**What goes wrong:**
The team picks a typst version by pattern-matching on the error (e.g. "it broke going to 0.15, so let's just pin `<0.15`" and grab whatever the latest 0.14.x happens to be, such as `0.14.1` because it's the current `pyproject.toml` floor). This can still fail, because:
- typst-py's PyPI version numbers track the underlying Typst compiler version it bundles (typst-py `0.14.1` ships compiler `0.14.1`, `0.15.0` ships compiler `0.15.0`, etc. — MEDIUM confidence, no single authoritative doc states this but it is the consistent observed pattern across typst-py releases). That means *any* 0.14.x release could behave slightly differently from another, and the four bundled `@preview` packages each declare their own `compiler` compatibility floor in their own `typst.toml` on Typst Universe — there is no guarantee that codly 1.3.0, codly-languages 0.1.1, mitex 0.2.4, and gentle-clues 1.2.0 all name the *same* compatible compiler range. It is entirely possible that no single typst-py version satisfies all four simultaneously (e.g. one package requires compiler ≥0.14.0 and another was published *after* 0.14.1 and silently expects ≥0.14.1 behavior, or one has an upper-bound gap).
- The reproduction environment described in `PROJECT.md` ("loose pins resolved sphinx==9.0.4, docutils==0.22.4, typst==0.15.0") is the *known-bad* combination; nothing in the repo currently proves which specific 0.14.x is known-good beyond "it worked before the rot set in," which is not written down anywhere durable.

**How to avoid — the empirical method (do this, don't guess):**
1. Enumerate candidate typst-py versions in the 0.14.x line from PyPI (`pip index versions typst` or the PyPI JSON API).
2. For each candidate, in an isolated venv/uv environment, run the actual compile path the extension uses: build the `docs/` PDF target (`tox -e docs-pdf`, which exercises exactly the `codly` + `codly-languages` + `mitex` + `gentle-clues` import block from `templates/base.typ`) against that one pinned typst version, with everything else held constant.
3. Record pass/fail per candidate version in a small matrix (a scratch script or a temporary CI matrix job is fine — doesn't need to be permanent). The first version (scanning from newest 0.14.x down, or oldest up — either direction, just be systematic) where the PDF build succeeds with **no** `unknown variable` / `unknown import` error is the empirically confirmed pin.
4. Cross-check by also compiling a minimal per-package smoke test (a `.typ` file that only imports and invokes one of the four packages at a time) — this isolates *which* package would be the first to break if you're ever forced to consider a typst upgrade later, which materially helps the deferred sphinx-9/typst-0.15 port scoped out of this milestone.
5. If step 2 finds **no** 0.14.x version that satisfies all four packages, that is a real risk this milestone must surface rather than paper over: the fallback is to pin one of the `@preview` packages to an *older* published version instead of moving the typst pin (Typst Universe keeps prior package versions installable), and re-run the same empirical check with that substitution.

**Warning signs:**
- The chosen typst version was picked because it's "the current floor in pyproject.toml" or "the newest 0.14.x on PyPI" without an actual compile-and-pass check against the bundled `@preview` set.
- `tox -e docs-pdf` (or the PDF-integration tests) is treated as passing based on `black`/`ruff`/unit-test success alone, without actually invoking the PDF build locally with the candidate pin.
- No record exists (commit message, `PROJECT.md` Key Decisions row, or code comment) of *which* typst versions were tried and rejected — meaning the next person to touch this repeats the guesswork from scratch.

**Phase to address:**
This empirical verification is the core deliverable of the pin phase — it should be the first concrete action taken (before touching Python/black/ruff), since every other CI bucket (lint reformatting aside) cascades from this one compiler↔package compatibility question. Record the confirmed version and the rejected candidates in `PROJECT.md`'s Key Decisions table so it's durable.

---

### Pitfall 4: Cross-platform pins that pass on ubuntu but fail on windows/macos

**What goes wrong:**
The evidence already shows this happening: "matrix jobs exit 254/1 cascading from the same compile error" across `ubuntu-latest`, `windows-latest`, `macos-latest`. Beyond the `kai` compile error itself (which is compiler/package logic and should be OS-independent once the pin is right), typst-py ships as a compiled binary wheel per platform — a version that has a manylinux wheel on PyPI is not guaranteed to have simultaneously-published, working wheels for Windows and macOS (arm64 vs x86_64) at the exact same release. Additional platform-specific traps for this stack:
- Path handling: `typsphinx/builder.py` and `translator.py` do manual path string manipulation (per `CONCERNS.md`, not `pathlib.Path.relative_to()`) for nested image paths — this is a classic Windows backslash-vs-forward-slash trap that a green ubuntu run will never expose.
- Line endings: `black --check` and `ruff check` can behave differently if `core.autocrlf` / `.gitattributes` normalize line endings differently across OS checkouts, causing "already formatted on ubuntu, reformats on windows" churn.
- The `typst.compile()` call in `pdf.py` writes a `tempfile.NamedTemporaryFile` and passes its path to the compiler — on Windows, an open file handle held by the Python process can block the compiler subprocess/library from reading the same path (classic Windows file-locking difference vs. POSIX), a failure mode that will never surface in the ubuntu/macos legs.

**How to avoid:**
- Once the typst/`@preview` pin is empirically confirmed (Pitfall 3), verify wheel availability for that exact typst-py version across all three OS runners *before* declaring the pin final — e.g. check the PyPI project's "Download files" page for the version, or simply let one full matrix CI run (all 12 python×os combinations) complete against the candidate pin and treat any platform-specific install failure as a signal to pick a different patch version in the same minor line, not to abandon the empirical method.
- Don't declare the milestone done from a green ubuntu run alone — the matrix (`fail-fast: false`, 3 OS × 4 Python versions = 12 jobs) must be watched to completion at least once after the pin lands.
- If the Windows temp-file/handle issue is suspected, confirm `tempfile.NamedTemporaryFile(..., delete=False, ...)` (already used in `pdf.py`) is closed before typst reads it — the `with` block does close the handle before `typst.compile()` is called, so this is likely already safe, but re-verify after any pin change since typst-py's internal file access pattern could differ between compiler versions.

**Warning signs:**
- CI is declared green based on the `lint`/`type-check`/`coverage`/`build` jobs (all `ubuntu-latest` only) plus a subset of the `test` matrix, without watching all 3 OS legs of `test` to completion.
- A matrix job fails with a different exit code (e.g. 254 vs 1) than its sibling OS legs for what should be "the same" underlying error — this is itself evidence of an OS-level difference (segfault/panic vs. clean Python exception) worth root-causing rather than dismissing as noise.

**Phase to address:**
A dedicated cross-platform verification checkpoint at the end of the pin phase (or as its own short phase gate) — run the full 12-job matrix to completion against the newly confirmed pins and treat any single-OS failure as blocking, not a "flaky, ignore it."

---

### Pitfall 5: Python 3.10 floor bump hazards

**What goes wrong:**
Several distinct hazards bundle under "modernize to 3.10–3.13," and they don't all fail the same way:
- **Black target-version drift**: `pyproject.toml`'s `[tool.black] target-version = ["py39","py310","py311","py312"]` is a *set* black uses to pick the lowest common feature subset. Removing `py39` and adding `py313` changes what black considers "safe" syntax to emit (e.g. parenthesized context managers, `except*`), which reformats files that were stable before — this is exactly the class of churn the failure evidence already shows ("Python 3.11 cannot parse code formatted for Python 3.12" — a real black error class when the *installed* black/Python parsing the file is older than the target-version black was told to format for). Bumping the floor without also bumping the CI runner's own Python (the `lint` job pins `uv python install 3.11` in `ci.yml`) can reproduce this exact class of failure again, just shifted up a version.
- **ruff target-version staleness**: `[tool.ruff] target-version = "py39"` is a separate setting from black's and is easy to forget — leaving it at `py39` after bumping `requires-python` means ruff won't apply the newer up-to-date (`UP0xx`) rules relevant to 3.10+ (e.g. it won't suggest `X | Y` unions consistently or PEP 604 patterns), producing an internally inconsistent lint config.
- **mypy `python_version = "3.9"`**: same staleness risk — mypy type-checks against a Python semantics floor that no longer matches `requires-python`.
- **Dropped 3.9-only accommodations**: `ruff.lint.ignore` already carries `UP035`/`UP006` explicitly commented "Python 3.9+ support" — once the floor moves to 3.10, these ignores become stale opt-outs that should be reconsidered (re-enabling them may trigger a second wave of reformatting/lint churn beyond the black target-version bump).
- **3.13 wheel/availability gaps**: not every dev dependency is guaranteed to have 3.13 wheels or 3.13 compatibility yet. `sphinx-testing>=1.0` (a dev dependency distinct from Sphinx's own built-in `sphinx.testing.fixtures` already used in `conftest.py`) is a good candidate to scrutinize — it is a low-maintenance, low-activity package (MEDIUM confidence: exact last-release date not directly confirmed here, but it is a long-dormant package in this ecosystem) and is plausible to either lack 3.13 support or be entirely redundant now that the test suite already uses Sphinx's own `sphinx.testing.fixtures` directly.

**Why it happens:**
Python floor/target-version settings are scattered across four independent tool configs (`black`, `ruff`, `mypy`, `requires-python`/classifiers) plus the CI matrix and per-job `uv python install` pins — there's no single flag that bumps all of them together, so a partial bump (e.g. `requires-python` updated but `mypy.python_version` left at 3.9) is the default outcome unless done as an explicit checklist.

**How to avoid:**
- Treat "bump the Python floor" as a checklist touching all of: `requires-python`, `classifiers` (drop `Programming Language :: Python :: 3.9`, add `3.13`), `[tool.black] target-version`, `[tool.ruff] target-version`, `[tool.mypy] python_version`, `tox.ini`'s `env_list` and the `ci.yml` matrix's `python-version` list, and every job's individual `uv python install` pin (`lint`, `type-check`, `coverage`, `build`, `integration`, `docs.yml`, `release.yml` all currently hardcode `3.11` — decide whether these single-Python jobs should move to the new floor, ceiling, or stay at a middle version, and do it deliberately rather than leaving some at 3.11 and others bumped).
- Run `black --check .` and `ruff check .` locally under the *lowest* newly-supported Python (3.10) after the config bump, not just under whatever Python happens to be on the developer's machine — this catches the "formatted for a newer target than the interpreter running the check" class of failure before CI does.
- Before removing the `UP035`/`UP006` ruff ignores, run `ruff check .` once with them removed to size the blast radius as a separate, reviewable diff — don't fold silent behavior-changing reformatting into the same commit as the version-pin changes from Pitfalls 1-3.
- Audit `dev`/`docs` optional-dependency groups for 3.13 wheel availability before committing to 3.13 in the matrix — `pip install --python 3.13 <pkg>` in a scratch venv for each dependency is a fast empirical check, same philosophy as Pitfall 3's "verify, don't guess."

**Warning signs:**
- `black --check .` passes locally but fails in CI (or vice versa) — a target-version/interpreter-version mismatch between local and CI Python.
- Four different "Python version" settings (`requires-python`, black, ruff, mypy) don't all point at the same floor after the change.
- A `uv sync` under Python 3.13 reports "no wheels available" or falls back to a source build that fails to compile for any dev/docs dependency.
- `sphinx-testing` (or any similarly dormant dependency) is still listed in `dev` after the bump without having been checked for 3.13 support.

**Phase to address:**
A distinct "Python floor modernization" phase, sequenced *after* the dependency-pin phase (Pitfalls 1-4) is green — bumping Python and reformatting should not be mixed into the same commits as the typst/sphinx/docutils pin fix, both so `git blame`/bisect stays useful and so a reformatting-churn regression doesn't get confused with a real compatibility regression.

---

### Pitfall 6: Green-but-frozen — CI passes today but rots again silently

**What goes wrong:**
The milestone succeeds at making every job green, but does so in a way indistinguishable from the state that caused the original rot: loose upper bounds re-introduced by habit, no scheduled check that would catch the *next* time Typst Universe or Sphinx ships a breaking release, and no lockfile-enforcement discipline in CI. Six months later, someone bumps an unrelated dependency, `uv sync` silently re-resolves past the ceiling (if the ceiling was set too loosely, e.g. `<10` instead of a tighter tested range), and the exact same class of failure recurs — except now there's no fresh "PROJECT.md failure evidence" writeup to reconstruct what broke.

**Why it happens:**
"Green CI" is a point-in-time state; nothing about a passing test run today proves the pins will still resolve to the same thing next month unless the lockfile is both committed *and* enforced. Scheduled drift-detection (a periodic CI run against unpinned/latest versions) is exactly the kind of "nice to have, do it later" item that gets cut under time pressure once the main jobs are green — and it's easy to conflate "add a drift-detection job" with "go fix the drift it finds," which would scope-creep into the explicitly-deferred sphinx-9/typst-0.15 port.

**How to avoid (without scope-creeping into the deferred port):**
- Enforce lockfile discipline in the jobs that matter most for reproducibility: switch `ci.yml`'s `uv sync --extra dev` to `uv sync --extra dev --locked` (or at minimum add a fast, separate CI step — `uv lock --check` — that fails if `uv.lock` drifts from `pyproject.toml`). This makes "forgot to regenerate the lock" (Pitfall 1) a loud CI failure instead of a silent one, permanently, not just during this milestone.
- Set upper bounds deliberately tight around the *empirically confirmed* known-good versions from Pitfall 3, not just "less than the next major" — e.g. if 0.14.1 through 0.14.9 are all empirically confirmed safe but 0.14.10 hasn't been checked, a bound of `<0.15` still risks drifting to an unverified 0.14.x patch; consider `~=0.14.1` (compatible-release) semantics if the project wants tight reproducibility, or explicitly re-run the Pitfall-3 empirical check whenever the ceiling is loosened.
- Add a **separate, non-blocking** scheduled workflow (e.g. weekly `on: schedule`) that runs `uv sync -U` (or `uv lock --upgrade` in a throwaway branch) against the *unpinned* upper edge and reports (not fails the main pipeline) whether newer sphinx/docutils/typst/`@preview` combinations still work. This is detection, not remediation — it explicitly does NOT trigger any code changes to support sphinx 9/typst 0.15; it just gives early warning so the *next* milestone has fresh failure evidence instead of starting from another multi-year drift.
- Do not resurrect the `typst_package_versions` configurability tech-debt item as part of "durability" — that's explicitly deferred per `PROJECT.md`; durability here means lockfile + bounds + a detection job, not a redesign.

**Warning signs:**
- `ci.yml`/`docs.yml`/`release.yml` still call plain `uv sync` (no `--locked`/`--frozen`) after this milestone — meaning the very drift mechanism that caused this milestone is still live.
- No scheduled workflow exists to proactively surface the next drift before it silently accumulates for another multi-year gap.
- Upper bounds were chosen as "whatever's one major version above current" rather than "the specific range verified in Pitfall 3."

**Phase to address:**
A short "durability guardrail" phase (or the final phase before milestone close) — deliberately scoped to lockfile enforcement + a detection-only scheduled job, explicitly *not* touching sphinx-9/typst-0.15 support code. Verification for this phase: confirm `uv sync --locked` (or `uv lock --check`) is present in `ci.yml`, and confirm the scheduled drift job exists and is separate from the required-status-check jobs so it can't block merges.

---

### Pitfall 7: Release workflow / lockfile drift breaking `release.yml` or the build

**What goes wrong:**
`release.yml`'s `validate` job re-implements its own dependency install and quality gates independently of `tox.ini` (`uv run pytest tests/ -v`, `uv run black --check .`, `uv run ruff check .`, `uv run mypy typsphinx/` — run directly, not via `tox -e lint`/`tox -e type`/`tox -e cov` as `ci.yml` does). This means:
- A pin/config change made only in `tox.ini` or only reasoned about via `ci.yml` can leave `release.yml` out of sync — e.g. if the Python floor bump changes which Python version `tox` environments use but `release.yml`'s `uv python install 3.11` step is left untouched, a release could be *cut* on a Python version this milestone is trying to retire, or validated with a stale lint/type config path that diverges subtly from what `ci.yml` actually enforces on `main`.
- `release.yml`'s `build` job runs `uv sync --extra dev` *after* `uv build`, purely to get `twine` for `twine check dist/*` — if the lockfile is out of date (Pitfall 1) this resolves independently of the `validate` job's earlier install, meaning the two jobs in the same workflow run could theoretically install different dependency sets if the lock is unstable/drifting mid-migration.
- The release workflow only triggers on `v*` tags — meaning a lockfile/pin mistake introduced during this milestone may not be caught by `release.yml` at all until someone actually cuts the next tagged release, potentially long after the CI-repair milestone is considered "done" and merged.

**Why it happens:**
`release.yml` was written to be self-contained (not depend on `tox.ini` environments) for release-safety reasons, but that means it's a second, independent place where the same pin/Python-floor changes must be mirrored, and nothing forces the two workflows to be edited together.

**How to avoid:**
- After any pin or Python-floor change, diff `release.yml`'s `validate` job commands against the equivalent `tox.ini` environments (`lint`, `type`, `cov`) and update `release.yml`'s hardcoded Python version and command set to match, or better, have `release.yml` call `uv run tox -e lint`/`-e type` etc. directly instead of duplicating the raw commands — reduces future drift surface between the two workflows to zero.
- Before considering the milestone complete, do a dry-run exercise of the release workflow's `validate` job logic locally (not necessarily cutting a real tag) against the new pins: `uv sync --extra dev --locked && uv run pytest tests/ -v && uv run black --check . && uv run ruff check . && uv run mypy typsphinx/` — if this doesn't pass cleanly, `release.yml` will fail the next time someone actually tags a release, likely long after this milestone's context is gone.
- Confirm `uv build` + `twine check dist/*` still succeeds with the new `requires-python` floor/ceiling and dropped/added classifiers (a version-mismatch here surfaces as a `twine check` metadata warning, not a hard error, so it's easy to miss).

**Warning signs:**
- `release.yml` and `ci.yml`/`tox.ini` specify different Python versions, different lint/type-check invocations, or different dependency install flags after this milestone's changes.
- No dry-run of `release.yml`'s validate logic was performed against the new pins before the milestone was marked complete.
- `requires-python` classifiers in `pyproject.toml` don't match the actual matrix tested in `ci.yml` (e.g. classifiers list 3.9 while `ci.yml`'s matrix no longer includes it, or vice versa) — `twine check` may flag this as inconsistent metadata.

**Phase to address:**
The final phase of the milestone (after pins, `@preview` sync, and Python floor are all settled) — explicitly include a "release workflow parity check" step as part of the exit criteria, not an afterthought triggered only when someone next tags a release.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|-----------------|------------------|
| Pin only `typst`, leave `sphinx`/`docutils` unbounded | Fastest path to green on the reproduced failure | Repeats the exact rot this milestone exists to fix | Never — this milestone's whole point is bounding the full dependency graph |
| Fix the 3-way `@preview` version string in only the files a grep happens to surface first | Saves a few minutes of triple-checking | Silent output inconsistency between master and included documents, undetectable by most tests | Never — always grep all 3 locations and add the consistency test |
| Skip the empirical typst-pin verification and reuse "whatever version was in `pyproject.toml` before" | Fast, no extra CI runs needed | May still be broken (no proof it was ever the version actually used in production) or may not satisfy all 4 `@preview` packages | Never for the final pin — acceptable only as a first *candidate* to test, not as the final answer |
| Leave `release.yml` duplicating raw commands instead of delegating to `tox` environments | No risk of touching a release-critical workflow during a CI-repair milestone | Every future pin/config change must remember to update two places | Acceptable to defer *consolidating* release.yml onto tox, but not acceptable to skip *verifying* release.yml parity this milestone |
| Skip the scheduled drift-detection job to save milestone time | Smaller, faster-to-review milestone | Guarantees another silent multi-year drift cycle like the one this milestone is fixing | Only acceptable if explicitly logged as a deferred follow-up in `PROJECT.md`, not silently dropped |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|-----------------|-------------------|
| typst-py (PyPI `typst` package) | Assuming any 0.14.x satisfies the bundled `@preview` set because "0.14 < 0.15" | Empirically compile the actual `docs-pdf` target against each 0.14.x candidate (Pitfall 3) before finalizing the pin |
| Typst Universe `@preview` packages | Editing the version string in only 1-2 of the 3 hardcoded locations | Grep all of `writer.py`, `template_engine.py`, `templates/base.typ` together; add a cross-file consistency test |
| `uv sync` (no `--locked`) in CI | Treating a green `uv sync` as proof the lockfile is current | Add `--locked` (or a separate `uv lock --check` step) so drift fails loudly instead of silently re-resolving |
| GitHub Actions matrix (`fail-fast: false`, 3 OS × 4 Python) | Declaring the milestone done from a partial/ubuntu-only view of the matrix | Watch the full 12-job matrix to completion at least once after the pin change lands |
| Codecov upload (`fail_ci_if_error: false`) | Assuming coverage job success implies coverage was actually uploaded/processed | Treat Codecov step failures as informational only — don't rely on it as a pin-correctness signal |
| PyPI trusted publishing (`release.yml`) | Assuming `release.yml` will "just work" because `ci.yml` is green | Dry-run `release.yml`'s `validate` job commands locally against the new pins before considering the milestone complete |

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|-----------------|
| `fail-fast: false` across all 12 test-matrix jobs while iterating on a still-broken pin | Every debugging iteration burns all 12 jobs' worth of CI minutes to reconfirm the same known error | While actively iterating on the typst/`@preview` pin, test locally (Pitfall 3's empirical method) or use `workflow_dispatch` with a narrowed matrix before pushing to the full matrix | Becomes costly as soon as more than a couple of guess-and-check pin iterations are pushed to CI instead of verified locally first |

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Loosening upper bounds "just to be safe for the future" after this milestone | Silently reintroduces exposure to the next breaking major release, defeating the durability goal | Keep bounds tied to the empirically-verified range (Pitfall 3/6); use a separate scheduled job (Pitfall 6) to surface newer versions for review rather than widening bounds pre-emptively |
| Pinning dependencies so tightly that known security patches in sphinx/docutils/typst are missed | Stale, vulnerable transitive dependencies persist indefinitely | Pair the tight pin with the scheduled drift-detection job (Pitfall 6) so security-relevant upgrades are surfaced on a cadence, even though they're not auto-applied |

## "Looks Done But Isn't" Checklist

- [ ] **Dependency pins:** `pyproject.toml` shows bounds on `typst` but check `sphinx` and `docutils` also have explicit upper bounds — not just the one package from the reproduced failure.
- [ ] **Lockfile:** `uv.lock` was regenerated (`uv lock`) and committed in the same change as any `pyproject.toml` dependency edit — diff both files together, not just one.
- [ ] **`@preview` versions:** all three locations (`writer.py`, `template_engine.py`, `templates/base.typ`) show identical version strings for `codly`, `codly-languages`, `mitex`, `gentle-clues` — verified by grep, not memory.
- [ ] **Typst pin verification:** the chosen typst version has a recorded, reproducible empirical check (which candidates were tried, which passed the `docs-pdf` build) — not just "it's the newest 0.14.x."
- [ ] **Cross-platform:** the full 12-job matrix (3 OS × 4 Python) was watched to green completion at least once after the pin landed, not inferred from the ubuntu-only jobs (`lint`, `type-check`, `coverage`, `build`).
- [ ] **Python floor:** `requires-python`, classifiers, `[tool.black] target-version`, `[tool.ruff] target-version`, `[tool.mypy] python_version`, `tox.ini`'s `env_list`, and every hardcoded `uv python install` line across `ci.yml`/`docs.yml`/`release.yml` all agree on the same floor/ceiling — not just one of them.
- [ ] **3.13 wheel check:** every `dev`/`docs` optional dependency (especially long-dormant ones like `sphinx-testing`) was checked for 3.13 installability, not assumed compatible.
- [ ] **Durability guardrail:** CI enforces lockfile currency (`--locked` or `uv lock --check`) and a scheduled drift-detection job exists — "green today" is not the same as "won't silently rot again."
- [ ] **Release workflow parity:** `release.yml`'s hardcoded Python version and duplicated lint/type/test commands were checked against the new pins and the updated `tox.ini` environments, with a local dry-run performed.

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|-----------------|------------------|
| Under-pinning (Pitfall 1) discovered after merge | LOW | Add the missing upper bounds, regenerate `uv.lock`, open a follow-up PR — no code changes needed, purely metadata |
| 3-way `@preview` desync (Pitfall 2) shipped | MEDIUM | Grep all 3 locations, correct the mismatched one, add the missing consistency test, re-run the full docs-pdf + integration suite to confirm output parity |
| Wrong typst pin chosen without empirical check (Pitfall 3), later found to still break one `@preview` package in some code path | MEDIUM-HIGH | Re-run the empirical per-package matrix (Pitfall 3 steps), narrow to the version that satisfies all four, and if none exists, downgrade the offending single `@preview` package instead of the whole typst pin |
| Cross-platform pin failure surfaces after merge (Pitfall 4) | MEDIUM | Re-run the full matrix, isolate the failing OS leg, check for a platform-specific wheel gap or path-handling bug, patch narrowly (patch-version bump or path-handling fix) rather than re-opening the whole pin decision |
| Python floor bump caused unexpected reformatting churn (Pitfall 5) | LOW-MEDIUM | Isolate the reformatting diff into its own commit/PR separate from the pin fix, review it standalone, and align black/ruff/mypy target versions explicitly rather than iterating blindly |
| CI green but drift guardrail missing (Pitfall 6) noticed post-milestone | LOW | Add `--locked` to the `uv sync` CI steps and the scheduled drift-detection workflow as a fast, self-contained follow-up — no runtime code changes required |
| `release.yml` breaks on the next real tag (Pitfall 7) | HIGH (blocks an actual release) | Fix `release.yml` in a hotfix branch, dry-run its `validate` job logic locally against current `main`, and re-tag once confirmed — costly mainly because it's discovered under release-time pressure rather than during the milestone |

## Sources

- Direct repository inspection (HIGH confidence): `.planning/PROJECT.md`, `.planning/codebase/CONCERNS.md`, `.planning/codebase/TESTING.md`, `.github/workflows/ci.yml`, `.github/workflows/docs.yml`, `.github/workflows/release.yml`, `pyproject.toml`, `tox.ini`, `typsphinx/writer.py`, `typsphinx/template_engine.py`, `typsphinx/templates/base.typ`, `typsphinx/pdf.py`
- [uv docs — Locking and syncing](https://docs.astral.sh/uv/concepts/projects/sync/) (HIGH confidence — official docs; confirms `uv sync` silently re-resolves a stale lock while `--locked` errors and `--frozen` skips validation entirely)
- [astral-sh/uv issue #12372 — "Have `uv sync` default to `--locked`"](https://github.com/astral-sh/uv/issues/12372) (MEDIUM confidence — community discussion corroborating the default-sync drift risk)
- [typst 0.15.0 changelog](https://typst.app/docs/changelog/0.15.0/) and [Typst 0.15 blog post](https://typst.app/blog/2026/typst-0.15/) (HIGH confidence — official Typst sources describing the 0.15 release the project must avoid for now)
- [typst/typst issue #4379 — package `compiler` field compatibility](https://github.com/typst/typst/issues/4379) (MEDIUM confidence — confirms each Universe package declares its own compiler-compatibility floor in `typst.toml`, the basis for "no single typst version may satisfy all four packages")
- [messense/typst-py GitHub repo](https://github.com/messense/typst-py) (MEDIUM confidence — the typst-py binding source; version-correspondence to the bundled compiler is an inferred pattern, not an explicitly documented guarantee, hence the recommendation to verify empirically rather than assume)

---
*Pitfalls research for: typsphinx CI-repair / dependency-modernization maintenance milestone*
*Researched: 2026-07-04*
</content>
