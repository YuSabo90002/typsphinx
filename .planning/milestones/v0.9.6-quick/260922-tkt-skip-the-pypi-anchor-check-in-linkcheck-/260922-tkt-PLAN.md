---
phase: quick-260922-tkt
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - docs/source/conf.py
  - .planning/todos/pending/2026-09-20-pypi-history-anchor-unverifiable-under-bot-mitigation-breaks-sphinx-linkcheck.md
  - .planning/todos/completed/2026-09-20-pypi-history-anchor-unverifiable-under-bot-mitigation-breaks-sphinx-linkcheck.md
autonomous: true
requirements: [TODO-2026-09-20-PYPI-ANCHOR]
requirements-completed: []

estimate:
  tokens: 40000
  raw_tokens: 40000
  tasks: 3
  confidence: low

must_haves:
  truths:
    - "A `sphinx-build -b linkcheck` run over `docs/source` no longer records `https://pypi.org/project/typsphinx/#history` (`changelog.rst:474`) as `broken`; it records it as `working`."
    - "The same URL is still fetched and its HTTP status still checked — only the anchor lookup is skipped. It is not in an ignore list and is not `ignored` in the linkcheck output."
    - "The two Class A records — `changelog.rst:8` (`.../compare/v0.9.6...HEAD`) and `changelog.rst:17` (`.../releases/tag/v0.9.6`) — are STILL `broken` after the change, because the `v0.9.6` tag does not exist yet. Their continued failure is the correct outcome, not a regression."
    - "Exactly one record in the whole link set changes `broken` → `working` between the pre-change and post-change runs: the PyPI one. No other suppression is introduced anywhere in the documentation set."
    - "The configured pattern is provably narrow: matched against every URI the linkcheck run discovered, it affects exactly one anchor lookup — the PyPI `#history` one — and no other URL's anchors stop being checked."
    - "`docs/source/conf.py` still parses and still loads under a real Sphinx run (the post-change linkcheck run is itself that proof), and `black --check .` / `ruff check .` stay clean."
    - "A future reader of `docs/source/conf.py` can tell from the file alone WHY the entry exists: the comment names the bot-mitigation mechanism, the 2026-09-22 re-measurement, and the condition under which the entry can simply be deleted."
    - "The tracking todo is no longer pending — it is filed under `.planning/todos/completed/` with its git history preserved."
    - "The REL-15 release fence is intact: `.planning/REQUIREMENTS.md` still hashes to `79b93b81…`, so its checkbox (line 22) and traceability row (line 59) did not move, and no `phase.complete`-family tooling ran."
  artifacts:
    - "docs/source/conf.py — the project's FIRST `linkcheck_*` key, plus its explanatory comment"
    - ".planning/todos/completed/2026-09-20-pypi-history-anchor-unverifiable-under-bot-mitigation-breaks-sphinx-linkcheck.md"
    - "docs/_build/linkcheck-tkt/before.json and after.json — the two linkcheck record sets the differential assertion is taken from (gitignored evidence; quoted in the SUMMARY, not committed)"
  key_links:
    - "The configured regex ↔ Sphinx's own matching semantics. Measured at planning time in `sphinx/builders/linkcheck.py` `HyperlinkAvailabilityCheckWorker._check_uri`: the URI is split on `#` FIRST, and the `linkcheck_anchors_ignore_for_url` patterns are `re.match()`ed against the fragment-STRIPPED URL. A pattern written to match the full `…/#history` string therefore never matches and the fix is a silent no-op that still reads plausibly in review. This is the single most likely way this change fails."
    - "The configured regex ↔ every other URL in the documentation set. `re.match` anchors only at the start, so an unterminated pattern is a prefix match and would silently stop anchor-checking any URL sharing that prefix. Bound by the static scope probe in Task 2 and by the `broken → working` differential in Task 3."
    - "`docs/source/conf.py` ↔ the `typsphinx-doc-translations` (ja) Read the Docs project, which consumes this file byte-for-byte. A `linkcheck_*` key is inert for the `html`/`typstpdf` builders both projects actually run, but it does land in the shared file — the comment has to stand on its own for a reader arriving from the ja side too."
---

<objective>
Stop `tox -e linkcheck` reporting `docs/source/changelog.rst:474`'s
`https://pypi.org/project/typsphinx/#history` anchor as broken, by adding the project's first
`linkcheck_*` key to `docs/source/conf.py`, and file the tracking todo as completed.

Purpose: PyPI serves automated clients a bot-mitigation interstitial — HTTP 200 with a 3038-byte
`Client Challenge` body containing zero anchors — so Sphinx's default-on `linkcheck_anchors` cannot
find `history` in it. The anchor's existence is *unverifiable* from a checker, not disproven. The
todo (filed 2026-09-20 out of Phase 75, which was prep-only) required a re-measurement before
applying, because if PyPI stopped challenging automated clients the todo would close as obsolete
instead. That re-measurement was taken 2026-09-22 and is recorded in `<context>`: the interstitial
is unchanged, byte-for-byte the same size, with and without a desktop User-Agent. The obsolete
branch is ruled out; the config change is the right close. Task 1 nevertheless re-derives that
verdict from the linkcheck run itself and halts if it disagrees — the measurement in `<context>`
is evidence, not authority.

Output: one `linkcheck_anchors_ignore_for_url` entry with its explanatory comment, and a completed
todo. No product code, no test, no CHANGELOG line.

Shape note: this is a single-key configuration change with one real oracle. A leading
`type="tracer"` task would be byte-identical to Task 2, so the tracer-first decomposition collapses
into it. What the three tasks split is not layers but *measurement order*: the oracle here is
differential, so the pre-change run has to be taken before the file is touched and cannot be
reconstructed afterwards.

Execution environment: this plan may run in the main checkout or in an isolated git worktree. Every
command below is written with a `${RUN}` prefix that resolves to `uv run ` in a worktree and to the
empty string in the main checkout, per CLAUDE.md § Worktree-isolated execution. Establish it once,
at the top of each task's verify block:

    if test -f .git; then RUN="uv run "; else RUN=""; fi

In a worktree, provision first with
`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev`. That is enough for the primary
route: `tox -e linkcheck` uses `runner = uv-venv-lock-runner` with `extras = docs`, so tox builds
its own `.tox/linkcheck` environment carrying furo / myst-parser / sphinx-autodoc-typehints without
touching `.venv`. Only the fallback route (calling `sphinx-build` directly) needs the docs extra in
`.venv`, and then it must be named **together with** dev — `uv sync --extra dev --extra docs` —
because an `--extra dev` sync on its own is exact and drops the docs packages.

**Scope fence.** Exactly two product-side paths may change: `docs/source/conf.py` and the todo's
two locations. Do NOT touch `typsphinx/`, `docs/source/changelog.rst`, `CHANGELOG.md`,
`pyproject.toml`, `uv.lock`, `README.md`, `tox.ini`, `.github/`, `.planning/REQUIREMENTS.md`,
`.planning/ROADMAP.md`, or any file under `tests/`. The repository is mid-release-close for
milestone v0.9.6 and `.planning/REQUIREMENTS.md` is under a line-scoped fence for REL-15. Do not run
any `phase.complete`-family tooling. A sibling quick task (`260922-tbe`) already landed in
`typsphinx/translator.py`; leave it alone. Do not edit
`.planning/todos/pending/2026-07-22-add-sphinx-linkcheck-ci-job.md` either — this plan's SUMMARY
notes the interaction, the file itself stays as it is.
</objective>

<execution_context>
@/home/yuta/Documents/typsphinx/.claude/gsd-core/workflows/execute-plan.md
@/home/yuta/Documents/typsphinx/.claude/gsd-core/templates/summary.md
</execution_context>

<context>
@/home/yuta/Documents/typsphinx/CLAUDE.md
@/home/yuta/Documents/typsphinx/.planning/todos/pending/2026-09-20-pypi-history-anchor-unverifiable-under-bot-mitigation-breaks-sphinx-linkcheck.md
@/home/yuta/Documents/typsphinx/docs/source/conf.py

Live observations taken at planning time on branch
`gsd/v0.9.6-doctest-block-rendering-and-release`, HEAD
`9289798cfa31efbd1296cd8572269234f471ef03`, working tree clean. Re-verify anything you rely on; do
not trust these numbers blind.

**The PyPI re-measurement (2026-09-22, the one the todo demanded).** Plain `curl` and `curl` with a
full desktop-browser User-Agent both return HTTP 200, a 3038-byte body, `<title>Client Challenge`,
and zero occurrences of `id="history"` — identical to the 2026-09-20 measurement recorded in the
todo. PyPI has not stopped challenging automated clients, so the todo's "closes as obsolete" branch
does not apply.

**Sphinx's matching semantics, read from the installed source (sphinx 9.1.0).** In
`sphinx/builders/linkcheck.py`, `HyperlinkAvailabilityCheckWorker._check_uri` does:

    req_url, delimiter, anchor = uri.partition('#')
    if delimiter and anchor:
        for rex in self.anchors_ignore:        # matched against the ANCHOR name
            ...
        else:
            for rex in self.anchors_ignore_for_url:
                if rex.match(req_url):         # matched against the FRAGMENT-STRIPPED URL
                    anchor = ''

So for `https://pypi.org/project/typsphinx/#history` the string the pattern is matched against is
`https://pypi.org/project/typsphinx/`, and `re.match` anchors only at the start. Both config keys
exist in this Sphinx version (`linkcheck_anchors_ignore_for_url` and `linkcheck_anchors_ignore`
both resolve), each compiled with `list(map(re.compile, ...))`, so entries are regex strings.

**The file to edit.** `docs/source/conf.py` is 117 lines and contains **zero** `linkcheck` keys
(`grep -n linkcheck docs/source/conf.py` → no output, exit 1). Its seven section headers are all
exactly 78 characters, of the form `# -- <title> ` padded with `-`. Exactly **one** line already
exceeds 88 columns (line 56, 112 chars — the `READTHEDOCS_LANGUAGE` comment); `E501` is ignored in
ruff because black owns wrapping.

**The link set.** `docs/source/changelog.rst:474` is
``- `PyPI Release History <https://pypi.org/project/typsphinx/#history>`_`` — the only anchored URL
written directly in a docs source file. `docs/source/index.rst:28` carries the *bare*
`https://pypi.org/project/typsphinx/` with no fragment, so it is status-checked but never
anchor-checked; it is `working` today and must stay that way. Those are the only two `pypi.org`
URLs under `docs/source`. The two Class A records come from `CHANGELOG.md`, which `changelog.rst`
includes via `myst_parser`: its link definitions at lines 1378 and 1401 are
`https://github.com/YuSabo90002/typsphinx/releases/tag/v0.9.6` and
`https://github.com/YuSabo90002/typsphinx/compare/v0.9.6...HEAD`, reported by linkcheck against
`changelog.rst` lines 17 and 8 (the reference sites). Both are broken because the `v0.9.6` tag does
not exist yet.

**The runner.** `tox.ini`'s `[testenv:linkcheck]` is `changedir = docs`, `extras = docs`,
`runner = uv-venv-lock-runner`, `commands = sphinx-build -b linkcheck source _build/linkcheck`. It
is deliberately outside `env_list`, so plain `tox` never reaches the network. `docs/_build/` is
gitignored (`.gitignore:45`), so evidence written there cannot pollute the commit scope.

**The linkcheck output format, read from the installed builder.** `CheckExternalLinksBuilder.finish`
writes `<outdir>/output.json` as JSON-lines, one object per checked hyperlink, with keys
`filename`, `lineno`, `status`, `code`, `uri`, `info`. `status` is a `StrEnum` and serializes to a
plain string — one of `broken`, `ignored`, `rate-limited`, `redirected`, `timeout`, `unchecked`,
`unknown`, `working`. The builder sets `statuscode = 1` when any link is broken or timed out, so
**both** runs in this plan are expected to exit non-zero while the two Class A records stand. Do
not read that exit code as the run having failed.

**Baselines.** `black --check .` → `358 files would be left unchanged.` `ruff check .` →
`All checks passed!` (must be invoked as the bare `ruff` shim or via `uv run`; calling
`.venv/bin/ruff` directly fails on NixOS with the `stub-ld` message and is not a regression).
`sha256sum .planning/REQUIREMENTS.md` = `79b93b81b5cf6ffdb20f9ddc0c97ff41969ada3547af1b16c4a20cc577d82d67`.
`git branch --list 'gsd/v0.9.6*'` returns exactly one branch (no decoy pair). `jq` is available,
though every check below uses Python so the evidence is independent of it.

**Prior context, not authority.** The last measured linkcheck on this branch read `total = 96`,
`working = 93`, 3 broken (the two Class A plus this Class B). Task 1 takes its own run; if the
counts differ, Task 1's numbers win.

## Decisions taken at planning time

- **D-A: use `linkcheck_anchors_ignore_for_url`, not `linkcheck_anchors_ignore`.** The latter is
  matched against the *anchor name* and applies to every URL in the project, so an entry for
  `history` would stop checking an anchor called `history` on any site. The former is matched
  against the URL. The todo's own Solution wording prefers it, and so does the suppression-scope
  threat in `<threat_model>`.
- **D-B: narrow the todo's suggested `pypi\.org` to the exact project URL, end-anchored.** The todo
  proposes an entry "for `pypi\.org`"; that would be a prefix match covering every PyPI page the
  docs might ever link. The narrowest pattern that still fixes the reported record is
  `r"https://pypi\.org/project/typsphinx/$"`. This is a deliberate narrowing of the source text,
  not a scope reduction: the reported defect is fully closed.
- **D-C (assumption-delta, honest verdict): this is NOT a constant → parameter transition.** The
  `assumption-delta` capability asks whether introducing the project's first `linkcheck_*` key
  turns a hardcoded constant into a parameter. It does not. `linkcheck_anchors` stays at its
  default `True`; nothing that was previously fixed becomes configurable; no new degree of freedom
  is exposed to *users* of typsphinx, because `docs/source/conf.py` is this project's own
  documentation build, not the extension's config surface (which lives in `typsphinx/__init__.py`
  and is `typst_*`-prefixed). What is added is a single-element exception list to a Sphinx builtin.
  Recorded as `chosen: no` rather than left unstated.
</context>

<tasks>

<task type="auto">
  <name>Task 1: Take the pre-change linkcheck baseline and re-derive the "not obsolete" verdict from it</name>
  <files>docs/_build/linkcheck-tkt/before.json (gitignored evidence; no tracked file changes)</files>
  <precondition>The working tree is clean and `docs/source/conf.py` contains zero `linkcheck` keys — this run is the BEFORE half of a differential and is worthless if the file has already been edited. Check with `git status --porcelain` (empty) and `grep -c linkcheck docs/source/conf.py` (no match, exit 1). If either fails, halt and report.</precondition>
  <action>
Run a full, cold linkcheck over `docs/source` and preserve its record set as the differential
baseline. Change no tracked file in this task.

Clear the build directory first so the run is cold: a warm doctree can make a second run measure a
different link set than the first, which would silently corrupt the very comparison this plan
rests on. Then run the project's documented command, from the repository root:

    rm -rf docs/_build/linkcheck
    mkdir -p docs/_build/linkcheck-tkt
    ${RUN}tox -e linkcheck            # expected to exit 1 — see below

The run needs network. Its exit status is **expected to be non-zero** because three records are
broken today; the builder sets `statuscode = 1` whenever any link is broken or timed out. Read the
verdict from `docs/_build/linkcheck/output.json`, never from the exit code. Copy that file to
`docs/_build/linkcheck-tkt/before.json` immediately, before anything else can overwrite it — tox
reuses the same output directory for the second run in Task 3.

If `tox -e linkcheck` cannot provision its environment, fall back to calling Sphinx directly, after
syncing both extras together (`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev
--extra docs` in a worktree):

    ${RUN}sphinx-build -b linkcheck docs/source docs/_build/linkcheck

Record in the SUMMARY which route was used, the wall-clock duration, and the total record count.

One branch this task must honour rather than assume away: the todo requires re-measuring before
applying, because if PyPI had stopped challenging automated clients there would be nothing to fix.
The orchestrator's 2026-09-22 curl measurement says it has not, and the verify block below
re-derives the same verdict from the linkcheck run itself. If the baseline shows the PyPI anchor
record as anything other than `broken`, the verify halts — do NOT proceed to Task 2, do NOT edit
`docs/source/conf.py`; report to the orchestrator that the todo now closes as obsolete and that the
close needs a different shape.
  </action>
  <verify>
    <automated>
if test -f .git; then RUN="uv run "; else RUN=""; fi
set -e
# 0. The baseline file exists and is non-empty JSON-lines.
test -s docs/_build/linkcheck-tkt/before.json
# 1. No tracked file changed while taking the baseline.
test -z "$(git status --porcelain)"
# 2. Parse the record set, print it as evidence, and re-derive the not-obsolete verdict.
${RUN}python - <<'PY'
import collections, json, pathlib, sys

recs = [
    json.loads(line)
    for line in pathlib.Path("docs/_build/linkcheck-tkt/before.json").read_text(
        encoding="utf-8"
    ).splitlines()
    if line.strip()
]
print("BEFORE total records:", len(recs))
print("BEFORE status histogram:", dict(collections.Counter(r["status"] for r in recs)))
for r in sorted(recs, key=lambda r: (r["filename"], r["lineno"])):
    if r["status"] == "broken":
        print("BEFORE broken:", r["filename"], r["lineno"], r["uri"], "|", r["info"][:140])

assert len(recs) > 50, f"only {len(recs)} records — the run did not read the full docs set"

pypi = [r for r in recs if r["uri"].split("#")[0] == "https://pypi.org/project/typsphinx/"]
assert pypi, "no PyPI record in the link set at all — the link text changed; halt and re-plan"
hist = [r for r in pypi if r["uri"].endswith("#history")]
assert len(hist) == 1, f"expected exactly one PyPI #history record, found {len(hist)}"
rec = hist[0]
print("BEFORE pypi-anchor:", rec["filename"], rec["lineno"], rec["uri"], rec["status"])
if rec["status"] != "broken":
    sys.exit(
        "HALT-OBSOLETE: the PyPI anchor record is %r, not broken. PyPI appears to have stopped "
        "challenging automated clients, so per the todo this closes as OBSOLETE and no conf.py "
        "change should be made. Report to the orchestrator; do not run Task 2." % rec["status"]
    )

# The two Class A records must be broken here too — Task 3 asserts they STILL are.
for needle in ("compare/v0.9.6...HEAD", "releases/tag/v0.9.6"):
    m = [r for r in recs if needle in r["uri"]]
    assert len(m) == 1, f"expected exactly one record for {needle}, found {len(m)}"
    print("BEFORE class-A:", needle, m[0]["filename"], m[0]["lineno"], m[0]["status"])
    assert m[0]["status"] == "broken", (
        f"{needle} is {m[0]['status']!r} in the baseline, not broken — the v0.9.6 tag may now "
        "exist; re-read the plan's Class A assumption before continuing"
    )

anchored = [r for r in recs if "#" in r["uri"]]
print("BEFORE anchored-URL count (anchor lookups performed):", len(anchored))
print("BASELINE-OK")
PY
    </automated>
  </verify>
  <done>
`docs/_build/linkcheck-tkt/before.json` holds the complete pre-change record set, printed with its
total, its status histogram, and every broken record named. The PyPI `#history` record is present
exactly once and is `broken`, so the todo's obsolete branch is ruled out from the oracle itself and
not only from the curl measurement. Both Class A records are present exactly once and `broken`. No
tracked file changed and the working tree is clean.
  </done>
</task>

<task type="auto">
  <name>Task 2: Add the URL-scoped anchor-skip to conf.py and prove the suppression is narrow</name>
  <files>docs/source/conf.py</files>
  <precondition>`docs/_build/linkcheck-tkt/before.json` exists and Task 1 printed `BASELINE-OK`. The scope probe in this task reads that file — without it the pattern's breadth can only be reasoned about, not measured.</precondition>
  <action>
Append a new section to the end of `docs/source/conf.py`, after the Autodoc section, introducing
the project's first `linkcheck_*` key.

Header line: follow the file's existing convention exactly — `# -- ` then the title then a space,
padded with `-` to a total length of **78** characters, matching the seven headers already in the
file. Title it for link checking and name the command it governs.

The setting, per D-A and D-B in `<context>`:

    linkcheck_anchors_ignore_for_url = [
        r"https://pypi\.org/project/typsphinx/$",
    ]

Keep the magic trailing comma so black leaves the list exploded. Three properties of that pattern
are load-bearing and must not be "tidied" later: it is a raw string (the `\.` is a regex escape,
not a Python one); it ends at `/` with a `$`, because Sphinx `re.match`es it against the
fragment-stripped URL and an unterminated pattern would be a prefix match over every PyPI page; and
it does NOT contain `#history`, because the fragment is split off before matching — writing the
fragment into the pattern produces a silent no-op that still reads plausibly.

Above it, write a comment block that a future reader can act on without leaving the file. It must
state: that only the ANCHOR lookup is skipped while the page is still fetched and its HTTP status
still checked; that PyPI serves automated clients a bot-mitigation interstitial — HTTP 200, a
3038-byte body titled `Client Challenge`, zero anchors — so the anchor is unverifiable rather than
absent; the re-measurement date `2026-09-22` (unchanged from the 2026-09-20 first measurement); that
the entry can simply be deleted if PyPI stops challenging automated clients; and why the pattern is
end-anchored at the project URL, citing `sphinx/builders/linkcheck.py`'s `_check_uri` as the reason
the fragment is absent from the pattern. Keep every added line at 88 columns or fewer; the file has
exactly one pre-existing over-88 line and must still have exactly one afterwards.

Naming the rejected alternative key in that comment is allowed and is not something any check
greps against — every assertion below reads *parsed values* out of the executed module namespace,
never the file's text, apart from one positive grep for the measurement date.

Change nothing else in the file: not `typst_documents`, not `typst_template`, not the intersphinx
mapping, not the `_resolve_language` helper. Remember this file is consumed byte-for-byte by the
`typsphinx-doc-translations` (ja) Read the Docs project as well.

Then commit just this file with a plain `git add` + `git commit` (not the GSD commit helper —
during a milestone close that helper has a history of resolving a decoy milestone branch). Message:

  docs(linkcheck): skip the PyPI anchor lookup under bot mitigation

ending with the two attribution lines this session requires:

  Co-Authored-By: Claude Opus 5 (1M context) &lt;noreply@anthropic.com&gt;
  Claude-Session: https://claude.ai/code/session_01NDoM8WycFazqm6ooMXAr9r
  </action>
  <verify>
    <automated>
if test -f .git; then RUN="uv run "; else RUN=""; fi
set -e
# 1. Column budget unchanged: still exactly the one pre-existing over-88 line.
test "$(awk 'length > 88' docs/source/conf.py | wc -l)" = 1
# 2. The measurement date is present in the file (positive grep; the only text-level check).
grep -q '2026-09-22' docs/source/conf.py
# 3. Syntax, then real evaluation, then the static scope probe. All three read parsed values.
${RUN}python - <<'PY'
import ast, json, pathlib, re

path = pathlib.Path("docs/source/conf.py").resolve()
source = path.read_text(encoding="utf-8")

# 3a. Syntax: conf.py is imported by every builder, so a parse error breaks everything.
ast.parse(source)
print("AST-PARSE OK")

# 3b. Evaluation: Sphinx exec()s this file, so exec it the same way and read the bound names.
ns = {"__file__": str(path), "__name__": "conf"}
exec(compile(source, str(path), "exec"), ns)  # noqa: S102 - mirrors Sphinx's own loading
pats = ns.get("linkcheck_anchors_ignore_for_url")
assert isinstance(pats, list), f"linkcheck_anchors_ignore_for_url is {pats!r}, expected a list"
assert len(pats) == 1, f"expected exactly one pattern, found {len(pats)}: {pats!r}"
print("CONFIGURED PATTERN:", pats[0])

# The project-wide, anchor-NAME-scoped alternative must not have been set (D-A).
assert "linkcheck_anchors_ignore" not in ns, (
    "the anchor-name-scoped key is bound in conf.py; D-A selects the URL-scoped key instead"
)
# Nothing may be added to an ignore list: the URL must still be fetched and status-checked.
for key in ("linkcheck_ignore", "linkcheck_exclude_documents", "linkcheck_anchors"):
    assert key not in ns, f"{key} was set; this plan adds exactly one linkcheck key"
present = sorted(k for k in ns if k.startswith("linkcheck"))
print("LINKCHECK KEYS BOUND:", present)
assert present == ["linkcheck_anchors_ignore_for_url"]

# 3c. Scope probe, network-free, against the real measured link set from Task 1.
recs = [
    json.loads(line)
    for line in pathlib.Path("docs/_build/linkcheck-tkt/before.json").read_text(
        encoding="utf-8"
    ).splitlines()
    if line.strip()
]
uris = sorted({r["uri"] for r in recs})
rex = re.compile(pats[0])
matched = [u for u in uris if rex.match(u.split("#")[0])]
affected = [u for u in matched if "#" in u]  # only these lose an anchor lookup
print("PATTERN MATCHES:", matched)
print("ANCHOR LOOKUPS SUPPRESSED:", affected)
assert affected == ["https://pypi.org/project/typsphinx/#history"], (
    f"suppression scope is wrong: {affected!r}"
)
assert set(matched) <= {
    "https://pypi.org/project/typsphinx/",
    "https://pypi.org/project/typsphinx/#history",
}, f"pattern reaches beyond the PyPI project URL: {matched!r}"

# Sensitivity control: a deliberately broad pattern must affect strictly more lookups,
# otherwise this probe could not discriminate and the print below says so out loud.
broad = [u for u in uris if re.match(r"https://", u.split("#")[0]) and "#" in u]
print(
    "PROBE SENSITIVITY: anchored URLs in the set =", len(broad),
    "| suppressed by the configured pattern =", len(affected),
)
if len(broad) <= len(affected):
    print(
        "PROBE NOTE: the documentation set contains only one anchored URL, so this control "
        "cannot discriminate; the exact-set assertions above carry the scope claim alone."
    )
print("SCOPE-PROBE OK")
PY
# 4. Format and lint, exactly the commands CLAUDE.md names. Baseline: 358 files unchanged.
${RUN}black --check .
${RUN}ruff check .
# 5. Exactly one file changed in this commit, and it is conf.py.
CHANGED="$(git show --name-only --format= HEAD)"
printf '%s\n' "$CHANGED"
test "$CHANGED" = docs/source/conf.py
test -z "$(git status --porcelain)"
    </automated>
  </verify>
  <done>
`docs/source/conf.py` binds exactly one `linkcheck_*` name — `linkcheck_anchors_ignore_for_url`,
one end-anchored pattern for the PyPI project URL — with no ignore list and no change to
`linkcheck_anchors`. The file parses, executes, and its own bound value, matched against every URI
the Task 1 run discovered, suppresses exactly one anchor lookup and reaches no URL outside the PyPI
project page. The comment carries the bot-mitigation reason and the `2026-09-22` date. The file
still has exactly one over-88 line, `black --check .` and `ruff check .` are clean, and the change
is one file in one commit on `gsd/v0.9.6-doctest-block-rendering-and-release`.
  </done>
</task>

<task type="auto">
  <name>Task 3: Re-run linkcheck, assert the bounded differential, and file the todo as completed</name>
  <files>.planning/todos/pending/2026-09-20-pypi-history-anchor-unverifiable-under-bot-mitigation-breaks-sphinx-linkcheck.md, .planning/todos/completed/2026-09-20-pypi-history-anchor-unverifiable-under-bot-mitigation-breaks-sphinx-linkcheck.md</files>
  <precondition>Task 2's commit is in and `docs/_build/linkcheck-tkt/before.json` still exists. The post-change run below must load the EDITED `docs/source/conf.py`; if the tree has been reverted or stashed, the run proves nothing.</precondition>
  <action>
Take the post-change run the same cold way as Task 1, preserve it as `after.json`, then assert the
differential and file the todo.

    rm -rf docs/_build/linkcheck
    ${RUN}tox -e linkcheck            # still expected to exit 1 — the two Class A records stand
    cp docs/_build/linkcheck/output.json docs/_build/linkcheck-tkt/after.json

Use the same route as Task 1 (tox, or the direct `sphinx-build` fallback); mixing routes between
the two halves would put an unmeasured variable into the comparison.

What the assertion is, and why it is shaped this way. The change can only ever *remove* an anchor
failure — skipping an anchor lookup cannot turn a working link into a broken one. So the complete
surface for a too-broad pattern is the set of records that go `broken` → `working`, and the plan
asserts that set is exactly the one PyPI record. That is deterministic. Demanding raw equality of
every other status instead would make this gate fail on third-party network flakiness — a failure
for the wrong reason — so every other status difference is *printed* as evidence and must be copied
into the SUMMARY rather than silently dropped. If any such difference appears, re-run the post-change
half once (cold, same route) before writing it up, and say in the SUMMARY whether it reproduced.

Then move the todo with `git mv` so its history is preserved:

    git mv .planning/todos/pending/2026-09-20-pypi-history-anchor-unverifiable-under-bot-mitigation-breaks-sphinx-linkcheck.md \
           .planning/todos/completed/2026-09-20-pypi-history-anchor-unverifiable-under-bot-mitigation-breaks-sphinx-linkcheck.md

Do not rewrite the file's body or frontmatter — the destination directory is what records
completion in this repository, and `resolves_phase: null` is correct for a quick task belonging to
no phase. Leave `.planning/todos/pending/2026-07-22-add-sphinx-linkcheck-ci-job.md` untouched; note
in the SUMMARY only that the conf.py key this plan lands is the settling the "Related" section of
the closed todo said that CI-job todo would otherwise have to do first.

Commit the move with `git add -A` restricted to the two todo paths plus `git commit` (again not the
GSD commit helper). Message:

  chore(todos): file the PyPI linkcheck anchor todo as completed

ending with the same two attribution lines used in Task 2. Do not commit anything under
`docs/_build/` — it is gitignored and the clean-tree check below is what proves it stayed out.
  </action>
  <verify>
    <automated>
if test -f .git; then RUN="uv run "; else RUN=""; fi
set -e
test -s docs/_build/linkcheck-tkt/after.json
# 1. The bounded differential.
${RUN}python - <<'PY'
import collections, json, pathlib, sys

def load(name):
    return [
        json.loads(line)
        for line in pathlib.Path(f"docs/_build/linkcheck-tkt/{name}").read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip()
    ]

before, after = load("before.json"), load("after.json")
key = lambda r: (r["filename"], r["lineno"], r["uri"])  # noqa: E731
b = {key(r): r["status"] for r in before}
a = {key(r): r["status"] for r in after}
print("AFTER total records:", len(after))
print("AFTER status histogram:", dict(collections.Counter(r["status"] for r in after)))

# 1a. The same links were discovered both times. Source-derived, so deterministic.
only_before, only_after = sorted(set(b) - set(a)), sorted(set(a) - set(b))
print("RECORDS ONLY IN BEFORE:", only_before)
print("RECORDS ONLY IN AFTER:", only_after)
assert not only_before and not only_after, "the discovered link set changed between runs"

# 1b. Exactly one record goes broken -> working, and it is the PyPI anchor.
fixed = sorted(k for k in b if b[k] == "broken" and a[k] == "working")
for k in fixed:
    print("FIXED broken->working:", k)
assert len(fixed) == 1, f"expected exactly one broken->working record, got {fixed!r}"
assert fixed[0][2] == "https://pypi.org/project/typsphinx/#history", fixed[0]
assert fixed[0][0].endswith("changelog.rst"), fixed[0]

# 1c. It is WORKING, not ignored: the URL is still fetched and status-checked.
rec = next(r for r in after if key(r) == fixed[0])
print("AFTER pypi-anchor record:", rec)
assert rec["status"] == "working", rec
assert rec["status"] != "ignored", rec

# 1d. The two Class A records are STILL broken. Their failure is the correct outcome.
for needle in ("compare/v0.9.6...HEAD", "releases/tag/v0.9.6"):
    m = [r for r in after if needle in r["uri"]]
    assert len(m) == 1, f"expected exactly one record for {needle}, found {len(m)}"
    print("AFTER class-A:", needle, m[0]["filename"], m[0]["lineno"], m[0]["status"])
    assert m[0]["status"] == "broken", (
        f"{needle} is no longer broken — that is NOT this change's doing; investigate before "
        "accepting it"
    )

# 1e. Every other status difference, printed in full as evidence for the SUMMARY.
others = sorted(k for k in b if b[k] != a[k] and k not in set(fixed))
for k in others:
    print(f"OTHER-STATUS-DIFF: {k} {b[k]} -> {a[k]}")
print("OTHER-STATUS-DIFF count:", len(others))
# None of them may be a suppression: broken->working is already exhausted by 1b.
assert all(not (b[k] == "broken" and a[k] == "working") for k in others)
print("DIFFERENTIAL-OK")
PY
# 2. The todo move landed, in both directions, and git recorded a rename.
test ! -e .planning/todos/pending/2026-09-20-pypi-history-anchor-unverifiable-under-bot-mitigation-breaks-sphinx-linkcheck.md
test -f .planning/todos/completed/2026-09-20-pypi-history-anchor-unverifiable-under-bot-mitigation-breaks-sphinx-linkcheck.md
RENAME="$(git log --diff-filter=R --name-status -1 --format= -- .planning/todos)"
printf '%s\n' "$RENAME"
printf '%s\n' "$RENAME" | grep -q '^R'
test -f .planning/todos/pending/2026-07-22-add-sphinx-linkcheck-ci-job.md
# 3. Release-close scope fence: every file no quick task may touch is byte-identical to the base.
git diff --quiet 9289798cfa31efbd1296cd8572269234f471ef03 -- \
  .planning/REQUIREMENTS.md .planning/ROADMAP.md CHANGELOG.md pyproject.toml uv.lock README.md \
  tox.ini .github/ typsphinx/ tests/ docs/source/changelog.rst
# 4. REL-15's fence, stated as its own digest so the evidence is readable.
DIGEST_LINE="$(sha256sum .planning/REQUIREMENTS.md)"
printf '%s\n' "$DIGEST_LINE"
test "${DIGEST_LINE%% *}" = 79b93b81b5cf6ffdb20f9ddc0c97ff41969ada3547af1b16c4a20cc577d82d67
# 5. Exactly two commits, touching exactly three paths, on the milestone branch with no decoy.
CHANGED_RAW="$(git diff --name-only 9289798cfa31efbd1296cd8572269234f471ef03..HEAD)"
CHANGED="$(printf '%s\n' "$CHANGED_RAW" | sort)"
printf '%s\n' "$CHANGED"
test "$CHANGED" = "$(printf '%s\n' \
  '.planning/todos/completed/2026-09-20-pypi-history-anchor-unverifiable-under-bot-mitigation-breaks-sphinx-linkcheck.md' \
  '.planning/todos/pending/2026-09-20-pypi-history-anchor-unverifiable-under-bot-mitigation-breaks-sphinx-linkcheck.md' \
  'docs/source/conf.py' | sort)"
BRANCHES="$(git branch --list 'gsd/v0.9.6*')"
printf '%s\n' "$BRANCHES"
test "$(printf '%s\n' "$BRANCHES" | wc -l)" = 1
test "$(git rev-parse --abbrev-ref HEAD)" = gsd/v0.9.6-doctest-block-rendering-and-release
# 6. Working tree clean — both commits landed and no build evidence was staged.
test -z "$(git status --porcelain)"
    </automated>
  </verify>
  <done>
The post-change linkcheck run discovered the same link set as the pre-change run, and exactly one
record moved `broken` → `working`: `changelog.rst`'s `https://pypi.org/project/typsphinx/#history`,
now `working` rather than `ignored`, so the URL is still fetched and status-checked. Both Class A
records are still `broken`, as they must be until the `v0.9.6` tag exists. Every other status
difference, if any, is printed and carried into the SUMMARY, and none of them is a
`broken` → `working` transition. The todo is under `.planning/todos/completed/` with git recording a
rename, the CI-job todo is untouched, the diff against `9289798c` is exactly three paths,
`.planning/REQUIREMENTS.md` still hashes to `79b93b81…`, one `gsd/v0.9.6*` branch exists, and the
working tree is clean.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| `docs/source/conf.py` → Sphinx's linkcheck builder | A regex in this file decides which published URLs stop having their anchors verified. Everything crossing here is documentation-quality assurance, not user data: no untrusted input is parsed, no credential is read, no network endpoint is newly contacted, and nothing in the shipped `typsphinx` package changes. The one genuine risk is that the boundary is drawn too wide and silently disables checking beyond the single intended URL. |
| `docs/source/conf.py` → the `typsphinx-doc-translations` (ja) RTD project | The same file is consumed byte-for-byte by a second repository's build. A `linkcheck_*` key is inert for the `html`/`typstpdf` builders both projects run, so the blast radius is a comment a ja-side reader must also be able to act on. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-260922-TKT-01 | Tampering | the `linkcheck_anchors_ignore_for_url` pattern — suppression scope | medium | mitigate | Two independent bounds. (a) Task 2's static scope probe compiles the pattern *as conf.py actually binds it* and matches it against every URI the measured link set contains, asserting that exactly one anchor lookup is suppressed and that nothing outside the PyPI project page is reached. (b) Task 3's differential asserts exactly one record moves `broken` → `working` across the change; since skipping an anchor lookup can only remove failures, that transition set is the complete attack surface. D-B additionally end-anchors the pattern with `$`, so it cannot prefix-match other PyPI pages. |
| T-260922-TKT-02 | Tampering | the pattern vs. Sphinx's matching semantics — a silent no-op | medium | mitigate | A pattern containing `#history` never matches, because `_check_uri` splits the fragment off before matching, so the "fix" would look right and do nothing. Bound by Task 3's differential, which fails unless the record actually moves to `working`, and by the `<context>` note recording the read of `sphinx/builders/linkcheck.py`. |
| T-260922-TKT-03 | Repudiation | the conf.py comment — a future reader misreading the entry as a link being suppressed | low | mitigate | The comment states the bot-mitigation mechanism with its measured shape (HTTP 200, 3038-byte `Client Challenge` body, zero anchors), the `2026-09-22` re-measurement date, that only the anchor lookup is skipped, and the condition under which the entry can be deleted. Task 2 asserts the date is present; Task 3 asserts the record is `working`, not `ignored`, so the claim in the comment is measured rather than promised. |
| T-260922-TKT-04 | Tampering | `.planning/REQUIREMENTS.md` REL-15 fence during an open release close | low | mitigate | Task 3 verify steps 3–5 assert byte identity against `9289798c` for every fenced path, the pinned SHA-256 for `.planning/REQUIREMENTS.md`, and that the whole-plan diff is exactly three paths. No `phase.complete`-family tooling is invoked by any task. |
| T-260922-TKT-05 | Denial of service | PyPI's bot mitigation itself | low | accept | The interstitial is a third-party control on a third-party host. This plan deliberately does not work around it — no User-Agent spoofing, no retry loop, no `linkcheck_request_headers` entry. It records that the anchor is unverifiable from an automated client and stops checking that one anchor, which is the honest response. Accepted with no mitigation. |

**Supply chain:** no `npm`/`pip`/`cargo`/`uv add` install task exists in this plan; `pyproject.toml`
and `uv.lock` are inside the scope fence and asserted byte-identical. No dependency is added,
removed, or version-changed, so the `T-{phase}-SC` package-legitimacy row and its blocking human
checkpoint do not apply and no `## Package Legitimacy Audit` table is required.

**ASVS L1 / `block_on: high`** — the highest severity above is `medium`, so nothing crosses the
blocking threshold. The two `medium` rows are both the suppression-scope family the capability
contribution named, and both are mitigated by measurement rather than by reading the regex.
</threat_model>

<verification>
Run from the repository root, after all three tasks:

1. Task 1's baseline script → `BASELINE-OK`, with the total, the status histogram, every broken
   record, and `BEFORE pypi-anchor: … broken` printed.
2. Task 2's config script → `AST-PARSE OK`, `CONFIGURED PATTERN: https://pypi\.org/project/typsphinx/$`,
   `LINKCHECK KEYS BOUND: ['linkcheck_anchors_ignore_for_url']`,
   `ANCHOR LOOKUPS SUPPRESSED: ['https://pypi.org/project/typsphinx/#history']`, `SCOPE-PROBE OK`.
3. `${RUN}black --check .` → `358 files would be left unchanged.`; `${RUN}ruff check .` →
   `All checks passed!`
4. `awk 'length > 88' docs/source/conf.py | wc -l` → `1` (the pre-existing line 56).
5. Task 3's differential script → `FIXED broken->working:` naming the PyPI record only,
   `AFTER class-A: … broken` twice, the `OTHER-STATUS-DIFF` lines (possibly none) and
   `DIFFERENTIAL-OK`.
6. `git diff --name-only 9289798cfa31efbd1296cd8572269234f471ef03..HEAD` → exactly three paths.
7. `sha256sum .planning/REQUIREMENTS.md` → `79b93b81b5cf6ffdb20f9ddc0c97ff41969ada3547af1b16c4a20cc577d82d67`
8. `git status --porcelain` → empty.

Deliberately NOT run here: `tox -e docs-html`, `tox -e docs-pdf`, and the full pytest suite. The
linkcheck run itself loads `docs/source/conf.py` through a real Sphinx build, which is what a
config edit needs proving; a full documentation build would cost minutes and measure nothing these
checks do not. The orchestrator runs the complete local suite separately after this task lands.
</verification>

<success_criteria>
- `docs/source/changelog.rst`'s `https://pypi.org/project/typsphinx/#history` is `working` in the
  post-change linkcheck run, and it got there by the anchor lookup being skipped, not by the URL
  being ignored.
- The two Class A records are still `broken`, and the plan says so as an expected outcome rather
  than asserting an unconditionally clean run.
- Exactly one record in the entire set moves `broken` → `working`; the discovered link set is
  identical across the two runs; every other status difference is printed and carried into the
  SUMMARY.
- The suppression is provably narrow: the pattern, as conf.py binds it, suppresses exactly one
  anchor lookup across every URI the run discovered.
- `docs/source/conf.py` parses, executes, loads under a real Sphinx run, keeps its single
  over-88 line, and stays clean under `black --check .` and `ruff check .`.
- The conf.py comment names the bot-mitigation reason, the `2026-09-22` measurement, and the
  deletion condition.
- The tracking todo is under `.planning/todos/completed/`, moved with `git mv`.
- Exactly two commits touching exactly three paths; the REL-15 fence is intact; no
  `phase.complete`-family tooling ran.
</success_criteria>

<output>
Create
`.planning/quick/260922-tkt-skip-the-pypi-anchor-check-in-linkcheck-/260922-tkt-SUMMARY.md`
when done. Record: which runner route was used and each run's wall-clock duration; the before/after
totals and status histograms; the exact `CONFIGURED PATTERN` line; the `ANCHOR LOOKUPS SUPPRESSED`
and `PROBE SENSITIVITY` lines; the `FIXED broken->working` line; the two `AFTER class-A` lines; every
`OTHER-STATUS-DIFF` line with a note on whether it reproduced on a re-run; the final
`.planning/REQUIREMENTS.md` digest; and one line noting that
`.planning/todos/pending/2026-07-22-add-sphinx-linkcheck-ci-job.md` remains open and that its
prerequisite — settling the PyPI anchor before promoting linkcheck to CI — is now discharged by
this change.
</output>
