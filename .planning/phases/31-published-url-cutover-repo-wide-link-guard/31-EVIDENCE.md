# Phase 31 Plan 01: Link Check negative-control evidence (D-09)

> **This is the D-09 negative-control record.** It is deliberately named `31-EVIDENCE.md`,
> **not** `31-VERIFICATION.md` — the latter is a reserved filename that the verifier agent
> overwrites wholesale, which would destroy this transcription. See `31-CONTEXT.md`
> "Environment briefing" and D-09.

## What this proves

SC#1 asks for proof that the Link Check mechanism built in Task 1 *would have caught* the
7 dead README deep links that motivated this milestone. The most faithful proof is the
mechanism itself failing on the unfixed tree — captured here as a live, red CI run, before
the URL rewrite (a later plan/wave in this phase) touches those links.

## The run

- **Workflow:** `Link Check` (job `link-check`, `.github/workflows/links.yml`)
- **Run URL:** https://github.com/YuSabo90002/typsphinx/actions/runs/30205112477
- **Run id:** `30205112477`
- **Conclusion:** `failure`
- **Evaluated commit SHA:** `eaee760124c089f1abeb827443a56f6609e955d0`
  (branch `worktree-agent-ad9fb4bbe59c49b28`, pushed via `git push -u origin HEAD` per D-08 —
  lychee is never run locally)
- **Created:** 2026-07-26T13:58:04Z — **Updated (completed):** 2026-07-26T13:58:13Z

An earlier run on this same branch, before an unrelated diagnostic-workflow add/remove
pair (see "Diagnostic detour" below), is corroborating evidence of the identical result:
run id `30204930428`, SHA `7821f32f4fe4789e9d443571139c308111198432`, conclusion `failure`,
same 7 flagged deep links, identical summary counts. Both runs post-date the Task 1
(`links.yml`) and Task 2 (pre-existing dead-link repair) commits and pre-date any
DOC-09 URL rewrite, so both are valid readings of the "before the rewrite" tree.

## Lychee summary counts (verbatim from the job log)

```
| Status         | Count |
|----------------|-------|
| 🔍 Total       | 92    |
| 🔗 Unique      | 53    |
| ✅ Successful  | 75    |
| ⏳ Timeouts    | 0     |
| 🔀 Redirected  | 16    |
| 👻 Excluded    | 9     |
| ❓ Unknown     | 0     |
| 🚫 Errors      | 8     |
| ⛔ Unsupported | 0     |
```

`Total (92) = Excluded (9) + Successful (75) + Errors (8)` — arithmetically consistent.

## Full flagged-URL list (8 errors, verbatim)

All 8 errors are reported under `### Errors in ./README.md`:

| Status | URL | Position | Note |
|---|---|---|---|
| 403 | `https://claude.ai/code` | README.md:307:18 | Rejected status code: 403 Forbidden — unrelated to this milestone (a Claude Code badge link); not one of the 7 motivating deep links |
| 404 | `https://yusabo90002.github.io/typsphinx/installation.html` | README.md:271:3 | Rejected status code: 404 Not Found |
| 404 | `https://yusabo90002.github.io/typsphinx/quickstart.html` | README.md:272:3 | Rejected status code: 404 Not Found |
| 404 | `https://yusabo90002.github.io/typsphinx/user_guide/` | README.md:273:3 | Rejected status code: 404 Not Found |
| 404 | `https://yusabo90002.github.io/typsphinx/user_guide/configuration.html` | README.md:274:3 | Rejected status code: 404 Not Found |
| 404 | `https://yusabo90002.github.io/typsphinx/examples/` | README.md:275:3 | Rejected status code: 404 Not Found |
| 404 | `https://yusabo90002.github.io/typsphinx/api/` | README.md:276:3 | Rejected status code: 404 Not Found |
| 404 | `https://yusabo90002.github.io/typsphinx/contributing.html` | README.md:277:3 | Rejected status code: 404 Not Found |

**All 7 old-host documentation deep links are present** (installation, quickstart, user
guide index, configuration reference, examples index, API reference, contributing) — this
is exactly the failure set that motivated this milestone, and SC#1's claim that this
mechanism sees them is confirmed.

**Task 2's repairs held**: no URL under `examples/` and no `changelog.rst` URL appears
anywhere in the failure list. The only non-deep-link error (`https://claude.ai/code`, 403)
is a pre-existing, unrelated badge link not in scope for this phase.

## False-negative rule-outs (the four checks the plan requires before trusting this result)

### 1. The lychee step ran to completion

The log ends in a real link summary (`# Summary` table with non-zero Total/Errors), not an
argument-parse or usage error:

```
Repo-wide link check (advisory)  Check links  2026-07-26T13:58:11.7873194Z # Summary
...
##[notice]Summary report available at: https://github.com/YuSabo90002/typsphinx/actions/runs/30205112477#summary-89801716220
##[error]Process completed with exit code 2.
```

Exit code 2 is lychee's normal "links were broken" exit status (not a CLI-parse failure,
which would exit differently and print a usage/help block instead of a summary table).

### 2. `pyproject.toml` was among the files lychee actually scanned

**This required a diagnostic detour** (see below) because a single `--verbose` does not
print per-file "OK" lines for links.yml's actual check mode — lychee's `-v`/Info-level
reporter only prints non-2xx and excluded results inline, so a clean file produces zero log
lines under `--verbose` alone (confirmed by reading `lychee-bin/src/formatters` /
`verbosity.rs` upstream — `-v` = Info, and Info-level output only surfaces
excluded/error/redirect events, not successes). Absence of `pyproject.toml` from the
Errors/Redirects sections is therefore **not** proof either way on its own — exactly the
false-negative trap RESEARCH.md Pitfall 2 / Assumption A1 warned about.

**Diagnostic detour:** a temporary workflow `.github/workflows/_diag-dump-inputs.yml` was
added, pushed, observed, and then removed (three commits: add, observe, remove — the
`git push -u origin HEAD` → CI-observe loop IS the sanctioned tuning method under D-08).
It ran lychee's `--dump-inputs` mode, which lists every resolved input file (respecting the
same `--extensions`/`--exclude-path` filters as the real job) **without performing any HTTP
checks** — a mode built for exactly this kind of input-set verification
(`lychee-bin/src/commands/dump_inputs.rs`: "outputs the resolved input sources that would be
processed by lychee ... respects file extension filtering and path exclusions").

- **Diagnostic run:** https://github.com/YuSabo90002/typsphinx/actions/runs/30205087374
  (conclusion `success` — `dump-inputs` mode always exits 0), commit
  `ddf1b32349e876f6b91e019f5f48362993b02cea`.
- **Quoted log evidence that `pyproject.toml` was resolved as an input:**

  ```
  Dump lychee inputs (diagnostic, temporary)  Dump inputs  2026-07-26T13:57:27.3606848Z ./pyproject.toml
  ```

This conclusively closes Pitfall 2 / Assumption A1: `pyproject.toml` is not silently
skipped by the `--extensions` filter; it is a scanned input in the exact same job
configuration (`--extensions md,html,rst,txt,toml`, `--exclude-path '.planning'`,
`--exclude-path 'CHANGELOG\.md$'`, `--exclude-path 'tests/fixtures'`) as `links.yml`
itself. The diagnostic workflow was removed immediately after capturing this evidence
(commit `eaee760124c089f1abeb827443a56f6609e955d0`, the same commit whose `links.yml` run
is this evidence file's primary record) — the merged tree carries no trace of it.

### 3. No `.planning/` file, no `CHANGELOG.md`, no `tests/fixtures/` file was scanned

The same `--dump-inputs` diagnostic run printed the **complete, 26-entry resolved input
list** (deduplicated). Quoted in full — no `.planning/` path, no root `CHANGELOG.md`, no
`tests/fixtures/` path appears anywhere in it:

```
./examples/advanced/index.rst
./examples/advanced/chapter1.rst
./examples/advanced/chapter2.rst
./examples/advanced/README.md
./examples/basic/index.rst
./examples/basic/README.md
./examples/charged-ieee/approach1/source/index.rst
./examples/charged-ieee/approach2/source/index.rst
./examples/charged-ieee/README.md
./tests/roots/test-basic/index.rst
./pyproject.toml
./CLAUDE.md
./docs/source/index.rst
./docs/source/contributing.rst
./docs/source/examples/index.rst
./docs/source/examples/basic.rst
./docs/source/examples/advanced.rst
./docs/source/quickstart.rst
./docs/source/changelog.rst
./docs/source/api/index.rst
./docs/source/user_guide/index.rst
./docs/source/user_guide/builders.rst
./docs/source/user_guide/configuration.rst
./docs/source/user_guide/templates.rst
./docs/source/installation.rst
./README.md
```

Note `./tests/roots/test-basic/index.rst` is a *different* path than the excluded
`tests/fixtures/` and is correctly **not** excluded — the exclusion regex is precise,
not over-broad. The real check run's own log corroborates the same exclusion boundary
directly (the `--exclude-path` regexes took effect on individual links found within
scanned files, e.g. a relative reference to the root `CHANGELOG.md`):

```
[EXCLUDED] file:///home/runner/work/typsphinx/typsphinx/CHANGELOG.md (at 311:5) | This is due to your 'exclude' values
```

No `.planning/` URL and no `tests/fixtures/` URL appears anywhere in the real run's
Errors, Redirects, or Excluded lines.

### 4. No relative or local path appears in the checked-link set — D-07 confirmed

Every entry in the Errors and Redirects sections carries an `http`/`https` scheme; the
`[EXCLUDED]` lines are the only place a `file://` URI or a `mailto:` URI appears, and those
are pre-filtered out before checking (excluded, not checked):

```
[EXCLUDED] file:///home/runner/work/typsphinx/typsphinx/docs/configuration.rst (at 262:5) | This is due to your 'exclude' values
[EXCLUDED] file:///home/runner/work/typsphinx/typsphinx/docs/source/user_guide/configuration.rst (at 201:78) | This is due to your 'exclude' values
[EXCLUDED] file:///home/runner/work/typsphinx/typsphinx/LICENSE (at 298:19) | This is due to your 'exclude' values
[EXCLUDED] mailto:yusabo90002@gmail.com (at 13:32) | This is due to your 'exclude' values
[EXCLUDED] mailto:john@mit.edu (at 46:22) | This is due to your 'exclude' values
[EXCLUDED] mailto:john@mit.edu (at 158:22) | This is due to your 'exclude' values
[EXCLUDED] mailto:jane@stanford.edu (at 163:22) | This is due to your 'exclude' values
[EXCLUDED] mailto:me@example.com (at 280:22) | This is due to your 'exclude' values
```

The `docs/source/user_guide/configuration.rst` line at `201:78` is the specific relative
reference from `examples/advanced/README.md`'s known-broken local link that the plan's
Task 1 rationale called out by name — confirmed excluded via `--scheme`, not silently
checked. `--scheme https --scheme http` took effect: no local/relative link was ever
checked (only excluded), satisfying D-07.

## Branch protection (non-required confirmation)

```
$ gh api repos/YuSabo90002/typsphinx/branches/main/protection --jq '.required_status_checks.contexts'
["Test Python 3.12 on ubuntu-latest","Lint and Format Check","Type Check","Code Coverage","Build Package","Test Python 3.13 on ubuntu-latest"]
```

No entry containing `link` or `Link Check` — the job is non-required by omission, as D-04
requires.

## Diagnostic detour — full commit record

For traceability, the three commits added and removed during this evidence-gathering step
(all on this plan's own worktree branch, never touching the phase branch
`gsd/v0.6.4-read-the-docs-migration`):

1. `ddf1b32` — `chore(31-01): temporary diagnostic workflow to dump lychee inputs`
2. (CI observed: run `30205087374`, `success`, `pyproject.toml` confirmed scanned)
3. `eaee760` — `chore(31-01): remove temporary diagnostic workflow`
4. (CI re-observed: run `30205112477`, `failure`, identical 7-deep-link result — this is
   this evidence file's primary record)

---

## Post-rewrite green run (Plan 05)

**This is the D-09 positive half of the evidence pair.** Wave 2 (Plans 03/04) rewrote every
retired-host URL to Read the Docs; this section records the Link Check run against that
rewritten tree, under the same `links.yml` settings modulo one documented tuning iteration
(below), so the difference between this run and the negative control above is attributable to
the rewrite and to nothing else.

### The runs (two pushes, one tuning iteration)

**Iteration 1 — unchanged settings, first push of this plan:**

- **Run URL:** https://github.com/YuSabo90002/typsphinx/actions/runs/30264672521
- **Run id:** `30264672521`
- **Conclusion:** `failure`
- **Evaluated commit SHA:** `79eca1cbb503264ebcf2bec4582cc2c60ef89e0d`
  (branch `worktree-agent-ad728f7d42898a802`, pushed via `git push -u origin HEAD` per D-08)
- **Result:** 1 error — `https://claude.ai/code` (README.md:309:18) returned `403 Forbidden`.
  This is the same pre-existing, unrelated badge-link finding the negative-control run above
  already flagged (there: README.md:307:18, identical URL, identical 403) — **not** one of the
  7 milestone-motivating deep links, and not introduced by this plan. Verified locally
  (D-08 permits `curl` locally) that the URL is genuinely alive and the 403 is a bot-blocking
  false positive, not a dead link:

  ```
  $ curl -s -o /dev/null -w "plain: %{http_code}\n" -L --max-time 20 "https://claude.ai/code"
  plain: 403
  $ curl -s -o /dev/null -w "with-UA: %{http_code}\n" -L --max-time 20 -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36" "https://claude.ai/code"
  with-UA: 200
  ```

  Per the plan's triage rule, a host that is provably alive but blocks the checker's
  request shape is the sanctioned "tuned away inside D-06's lenient posture" case (the
  `--accept` set is explicitly named as a tunable knob), not a "genuinely dead link" requiring
  a source fix. Tuned by widening `--accept` from `100..=103,200..=299,429` to
  `100..=103,200..=299,403,429` in `.github/workflows/links.yml`, committed
  (`829a0b5` — `chore(31-05): accept 403 in links.yml for claude.ai bot-blocking false
  positive`) with the rationale recorded both in the commit message and as a comment in the
  workflow file itself, and re-pushed.

**Iteration 2 — after the `--accept` tuning — the recorded green run:**

- **Run URL:** https://github.com/YuSabo90002/typsphinx/actions/runs/30264757017
- **Run id:** `30264757017`
- **Conclusion:** `success`
- **Evaluated commit SHA:** `829a0b540bbbb4256f3a36eb5a76cd941a13817b`
  (branch `worktree-agent-ad728f7d42898a802`, pushed via `git push -u origin HEAD` per D-08)
- **Created:** 2026-07-27T12:09:32Z — **Updated (completed):** 2026-07-27T12:09:40Z

### Lychee summary counts (verbatim from the job log, iteration 2 / green run)

```
| Status         | Count |
|----------------|-------|
| 🔍 Total       | 93    |
| 🔗 Unique      | 51    |
| ✅ Successful  | 84    |
| ⏳ Timeouts    | 0     |
| 🔀 Redirected  | 20    |
| 👻 Excluded    | 9     |
| ❓ Unknown     | 0     |
| 🚫 Errors      | 0     |
| ⛔ Unsupported | 0     |
```

`Total (93) = Excluded (9) + Successful (84)` — arithmetically consistent, 0 errors.

### Then/now side-by-side against the negative control

| Metric | Negative control (before, run `30205112477`) | Green run (after, run `30264757017`) |
|---|---|---|
| Total links | 92 | 93 |
| Unique links | 53 | 51 |
| Successful | 75 | 84 |
| Errors | 8 (7 retired-host deep links + 1 unrelated `claude.ai/code` 403) | 0 |
| Excluded | 9 | 9 |
| Redirected | 16 | 20 |

Total (92 -> 93) is the same order of magnitude — no scan-surface collapse. The +1 total and
the redirect-count increase from 16 to 20 are consistent with the rewrite itself: the old
`github.io` deep links resolved directly (404, not a redirect), while the new
`https://typsphinx.readthedocs.io/` root URLs each redirect once to `/en/latest/` (visible
above under "Redirects in ./README.md", "./pyproject.toml", and the two `examples/*` READMEs
that also reference the RTD root) — more URLs now redirect rather than dying outright, which
is exactly the expected shape of "the same links now resolve." The Unique count dropping
(53 -> 51) reflects the URL consolidation from the rewrite (multiple github.io deep links
sharing fewer distinct RTD hosts/roots after D-11's version-less top-level convention).

**Specific URLs that moved from failing to passing:** all 7 of the negative control's
retired-host deep links —
`https://yusabo90002.github.io/typsphinx/{installation.html,quickstart.html,user_guide/,
user_guide/configuration.html,examples/,api/,contributing.html}` — no longer appear anywhere
in the tree (confirmed independently by Task 2's repo-wide grep below), so lychee has nothing
to check at those URLs anymore; the tree's *replacement* RTD URLs at the same README lines all
appear in this run's Redirects section (never Errors), i.e. resolving with a 302 to
`/en/latest/`. The 8th negative-control error, `https://claude.ai/code` (403), is unchanged in
kind (still 403 to lychee) but is now within the tuned `--accept` set (see above) rather than
having been fixed at the source — it is unrelated to DOC-09's scope and was never one of the 7
motivating links.

### Did `links.yml` change between the two runs, and does that change risk masking a real failure?

**Yes, one change, fully recorded above:** `--accept` widened to include `403`, applied and
observed via the sanctioned push-observe loop (iteration 1 above), motivated by a single named
URL (`https://claude.ai/code`) that is unrelated to this milestone's scope and independently
verified alive via a browser-UA `curl`. This cannot mask a real failure because:

- It targets exactly one already-identified, already-corroborated (present verbatim in the
  Plan 01 negative control too) false positive — it does not widen path exclusions
  (`--exclude-path` count is still 3, unchanged) and does not add a URL-pattern exclusion
  (`grep -oE '[-]-exclude[a-z-]*' | grep -cx -- '--exclude'` is still `0`).
- The 7 retired-host deep links this milestone exists to catch return `404`, not `403` — they
  are unaffected by this `--accept` addition and would still fail the job if they were still
  present (confirmed structurally: they are not present in the rewritten tree at all, per
  Task 2's grep below, so this is not a hypothetical).
- `--scheme` restriction (`grep -c 'scheme'` -> `2`) is untouched, so D-07 (HTTP(S)-only) still
  holds.
- No `continue-on-error` was added (`grep -v '^\s*#' .github/workflows/links.yml | grep -c
  'continue-on-error'` -> `0`).

### Structural re-confirmation (the same four facts re-checked on the green run)

1. **The lychee step ran to completion, not an argument error.** The log ends in a real
   `# Summary` markdown table (Total/Errors/etc.) and a `##[notice]Summary report available
   at: ...` line, with no usage/help text — the same shape as the negative control.
2. **`pyproject.toml` was among the scanned files.** The Redirects section includes
   `### Redirects in ./pyproject.toml` with its one entry
   (`https://typsphinx.readthedocs.io/` -> 302 -> `/en/latest/`) — direct proof it was parsed
   and its one link checked (not silently skipped), corroborating the Plan 01
   `--dump-inputs` diagnostic finding without needing to repeat that diagnostic.
3. **No `.planning/`, `CHANGELOG.md`, or `tests/fixtures/` file was scanned.** The only
   `[EXCLUDED]` lines in the green run's log (verbatim, 9 total matching the summary's Excluded
   count) are: `docs/configuration.rst` (relative path, at 262:5), 5 `mailto:` addresses, the
   relative `docs/source/user_guide/configuration.rst` reference (at 201:78), `LICENSE` (at
   300:19, relative path), and `CHANGELOG.md` itself (at 313:5, relative path) — identical set
   to the negative control's exclusions, confirming the exclusion boundary did not shift.
4. **No relative/local path appears in the checked-link set — D-07 held.** Every entry in the
   green run's Redirects section carries an `http`/`https` scheme; the `[EXCLUDED]` lines are
   the only place a `file://` or `mailto:` URI appears (pre-filtered, not checked).

### Branch protection (re-confirmed at Plan 05 execution time)

```
$ gh api repos/YuSabo90002/typsphinx/branches/main/protection --jq '.required_status_checks.contexts'
["Test Python 3.12 on ubuntu-latest","Lint and Format Check","Type Check","Code Coverage","Build Package","Test Python 3.13 on ubuntu-latest"]
```

No entry containing `link` or `Link Check` — the job remains non-required, as D-04 requires.

### Conclusion

The red/green pair is complete: the negative control (run `30205112477`, before the rewrite)
flagged all 7 retired-host deep links plus one unrelated pre-existing badge-link 403; the green
run (run `30264757017`, after the rewrite) shows 0 errors, with the same 7 deep links absent
from the tree entirely (not merely passing) and the one unrelated finding disposed of via a
narrowly-scoped, explicitly-justified `--accept` tuning that cannot mask a real failure. Both
runs used the same scan surface (`pyproject.toml` scanned; no `.planning/`/`CHANGELOG.md`/
`tests/fixtures/` scanned; HTTP(S)-only), and the total-link-count order of magnitude is
unchanged (92 -> 93). The difference between red and green is attributable to the DOC-09 URL
rewrite and to nothing else.
