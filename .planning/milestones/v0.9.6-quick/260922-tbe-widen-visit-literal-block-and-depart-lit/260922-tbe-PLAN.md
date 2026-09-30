---
phase: quick-260922-tbe
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - typsphinx/translator.py
  - .planning/todos/pending/2026-09-20-literal-block-docstring-args-still-name-only-the-literal-block-node.md
  - .planning/todos/completed/2026-09-20-literal-block-docstring-args-still-name-only-the-literal-block-node.md
autonomous: true
requirements: [IN-01]
requirements-completed: []

estimate:
  tokens: 18000
  raw_tokens: 18000
  tasks: 2
  confidence: low

must_haves:
  truths:
    - "A reader who consults only `visit_literal_block`'s `Args:` entry learns the method is also the doctest-block entry point, without having to read the widened signature or `visit_doctest_block`'s docstring."
    - "The same is true of `depart_literal_block`'s `Args:` entry."
    - "The package's executable behaviour is unchanged: the docstring-stripped AST of `typsphinx/translator.py` is byte-identical to the same file at the pinned base commit `b367f576`."
    - "`tests/test_docstring_rest_census_guard.py` still reports zero forbidden docutils message classes across every typsphinx docstring, so the widened text introduced no reST defect."
    - "The tracking todo is no longer pending — it is filed under `.planning/todos/completed/` with its git history preserved."
    - "The REL-15 release fence is intact: `.planning/REQUIREMENTS.md` is byte-identical to `b367f576`, so REL-15's checkbox (line 22) and traceability row (line 59) did not move."
  artifacts:
    - "typsphinx/translator.py — both `Args:` entries widened, nothing else changed"
    - ".planning/todos/completed/2026-09-20-literal-block-docstring-args-still-name-only-the-literal-block-node.md"
  key_links:
    - "The widened `Args:` text ↔ the already-widened `self, node: nodes.literal_block | nodes.doctest_block` annotation on both signatures — the prose and the annotation must name the same set of node kinds. This is the whole point of the change; if the prose is widened on only one of the two methods, the link is half-made."
    - "The docstring text ↔ `tests/test_docstring_rest_census_guard.py`, which parses every `typsphinx/*.py` docstring through napoleon + docutils. This guard is the one test that actually reads these two docstrings, so it is the real oracle for a docstring edit."
---

<objective>
Widen the `Args:` docstring entries of `visit_literal_block` and `depart_literal_block` in
`typsphinx/translator.py` so they name the doctest block as well as the literal block, and file the
tracking todo as completed.

Purpose: Phase 74 widened both signatures to `nodes.literal_block | nodes.doctest_block` and updated
the surrounding prose, but left the two `Args:` lines behind. A reader consulting only the `Args:`
entry does not learn that `visit_literal_block` is also the doctest-block entry point. The todo
(`74-REVIEW.md` § "Info" IN-01) was deferred out of Phase 75 by D-14 because that phase was
prep-only; the prep-only fence is now spent, so the one-line fix can land.

Output: two widened docstring lines and a completed-todo file. No behaviour change, no new test.

Shape note: this is a single-layer, single-file documentation edit. A leading `type="tracer"` task
would be byte-identical to Task 1, so the tracer-first decomposition collapses into it rather than
being split out artificially.

Execution environment: this plan may run in the main checkout or in an isolated git worktree. Every
command below is written with a `${RUN}` prefix that resolves to `uv run ` in a worktree and to the
empty string in the main checkout, per CLAUDE.md § Worktree-isolated execution. Establish it once,
at the top of each task's verify block:

    if test -f .git; then RUN="uv run "; else RUN=""; fi
</objective>

<execution_context>
@/home/yuta/Documents/typsphinx/.claude/gsd-core/workflows/execute-plan.md
@/home/yuta/Documents/typsphinx/.claude/gsd-core/templates/summary.md
</execution_context>

<context>
@/home/yuta/Documents/typsphinx/CLAUDE.md
@/home/yuta/Documents/typsphinx/.planning/todos/pending/2026-09-20-literal-block-docstring-args-still-name-only-the-literal-block-node.md

Live observations taken at planning time on branch
`gsd/v0.9.6-doctest-block-rendering-and-release`, HEAD `b367f57609fa3c060986acf89d35d330cfd4724c`.
Re-verify before editing; do not trust these numbers blind:

- `typsphinx/translator.py:2431` — `def visit_literal_block(`, signature already reads
  `self, node: nodes.literal_block | nodes.doctest_block`. Its `Args:` label sits at line 2444 and
  the parameter line at 2445.
- `typsphinx/translator.py:2586` — `def depart_literal_block(`, same widened signature. `Args:` at
  line 2594, parameter line at 2595.
- `grep -n "The literal block node" typsphinx/translator.py` returns **exactly two** hits, 2445 and
  2595. There is no third site and no test or doc source asserting the text — the only other
  occurrences in the tree are inside the gitignored `docs/_build/` output.
- Both parameter lines are indented with 12 spaces.
- `awk 'length > 88' typsphinx/translator.py | wc -l` = **9** (pre-existing long lines; `E501` is
  ignored in ruff because black owns wrapping, and black does not reflow docstring prose).
- Baseline is green: `ruff check .` → `All checks passed!`; `black --check .` → `358 files would be
  left unchanged.`
- `pytest tests/test_docstring_rest_census_guard.py tests/test_doctest_block_render_gate.py -q` →
  **18 passed** in ~1s.
- `sha256sum .planning/REQUIREMENTS.md` = `79b93b81b5cf6ffdb20f9ddc0c97ff41969ada3547af1b16c4a20cc577d82d67`
- `git branch --list 'gsd/v0.9.6*'` returns exactly one branch (no decoy pair).
</context>

<tasks>

<!-- planner-discipline-allow: node: The literal block node -->

<task type="auto">
  <name>Task 1: Widen both `Args:` parameter lines to name the doctest block</name>
  <files>typsphinx/translator.py</files>
  <precondition>`grep -c "The literal block node" typsphinx/translator.py` returns exactly 2, and both `visit_literal_block` and `depart_literal_block` already carry the `nodes.literal_block | nodes.doctest_block` annotation. If either is false, the tree is not the one this plan measured — halt and report.</precondition>
  <action>
In `typsphinx/translator.py`, replace BOTH occurrences of the 12-space-indented docstring parameter
line that currently ends after the words "literal block node" — one inside `visit_literal_block`
(around line 2445), one inside `depart_literal_block` (around line 2595) — with the widened text the
todo's Solution section proposes verbatim:

12 spaces, then `node: The literal block node, or a doctest block delegated here`

That is 75 columns, well inside the 88-column budget, so no wrapping is needed and black will not
reflow it. Change nothing else: not the `Args:` labels, not the surrounding docstring prose, not the
signatures (already widened by Phase 74), not a single line of code. Locate the sites by grepping
the file rather than by trusting the line numbers quoted in `<context>` — they were measured at
planning time and may have shifted.

Do not touch `docs/source/conf.py` (a separate quick task owns it), `CHANGELOG.md`,
`pyproject.toml`, `uv.lock`, `README.md`, `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`, or
any file under `tests/`. The repository is mid-release-close for milestone v0.9.6 and
`.planning/REQUIREMENTS.md` is under a line-scoped fence for REL-15. Do not run any
`phase.complete`-family tooling.

Commit the single file with a plain `git add` + `git commit` (not the GSD commit helper — during a
milestone close that helper has a history of resolving a decoy milestone branch). Message:

  docs(translator): widen literal-block Args docstrings to name the doctest block

ending with the two attribution lines this session requires:

  Co-Authored-By: Claude Opus 5 (1M context) &lt;noreply@anthropic.com&gt;
  Claude-Session: https://claude.ai/code/session_01NDoM8WycFazqm6ooMXAr9r
  </action>
  <verify>
    <automated>
if test -f .git; then RUN="uv run "; else RUN=""; fi
set -e
# 1. Exactly two widened lines, zero un-widened ones left. `grep -n` + `wc -l` rather than
#    `grep -c`, and the `-n` output doubles as readable evidence of which lines moved.
WIDENED="$(grep -n '^            node: The literal block node, or a doctest block delegated here$' typsphinx/translator.py)"
printf '%s\n' "$WIDENED"
test "$(printf '%s\n' "$WIDENED" | wc -l)" = 2
! grep -q '^            node: The literal block node$' typsphinx/translator.py
# 2. Column budget unchanged: still the 9 pre-existing long lines, no tenth.
test "$(awk 'length > 88' typsphinx/translator.py | wc -l)" = 9
# 3. Behaviour identity: docstring-stripped AST identical to the pinned base blob.
#    Proven non-vacuous at planning time -- this oracle reports SAME for a docstring-only
#    edit and DIFFERS for a one-token code edit.
${RUN}python - <<'PY'
import ast, subprocess
def strip(src):
    tree = ast.parse(src)
    for n in ast.walk(tree):
        if isinstance(n, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            b = n.body
            if b and isinstance(b[0], ast.Expr) and isinstance(b[0].value, ast.Constant) \
                    and isinstance(b[0].value.value, str):
                n.body = b[1:] or [ast.Pass()]
    return ast.dump(tree)
base = subprocess.run(
    ["git", "show", "b367f57609fa3c060986acf89d35d330cfd4724c:typsphinx/translator.py"],
    capture_output=True, text=True, check=True).stdout
now = open("typsphinx/translator.py", encoding="utf-8").read()
assert strip(base) == strip(now), "docstring-stripped AST DIFFERS -- executable code changed"
print("AST-EQUIV OK")
PY
# 4. Lint / format / types, exactly the commands CLAUDE.md names.
${RUN}ruff check .
${RUN}black --check .
${RUN}mypy typsphinx/
# 5. The real docstring oracle plus the doctest-block render gate. Baseline: 18 passed.
${RUN}pytest tests/test_docstring_rest_census_guard.py tests/test_doctest_block_render_gate.py -q
    </automated>
  </verify>
  <done>
Both `Args:` parameter lines read `node: The literal block node, or a doctest block delegated here`
(count 2, zero un-widened remainders). The file has no tenth over-88 line. The docstring-stripped
AST matches `b367f576`'s, so no executable code changed. `ruff check .`, `black --check .` and
`mypy typsphinx/` are clean, and the two targeted test files report 18 passed. The change is
committed as one file in one commit on `gsd/v0.9.6-doctest-block-rendering-and-release`.
  </done>
</task>

<task type="auto">
  <name>Task 2: File the tracking todo as completed and re-assert the release-close scope fence</name>
  <files>.planning/todos/pending/2026-09-20-literal-block-docstring-args-still-name-only-the-literal-block-node.md, .planning/todos/completed/2026-09-20-literal-block-docstring-args-still-name-only-the-literal-block-node.md</files>
  <action>
Move the todo with `git mv` so its history is preserved:

  git mv .planning/todos/pending/2026-09-20-literal-block-docstring-args-still-name-only-the-literal-block-node.md \
         .planning/todos/completed/2026-09-20-literal-block-docstring-args-still-name-only-the-literal-block-node.md

Do not rewrite the file's body or frontmatter — the destination directory is what records
completion in this repository, and `resolves_phase: null` is correct for a quick task that belongs
to no phase. Do not run any `phase.complete`-family tooling; nothing in `.planning/REQUIREMENTS.md`
or `.planning/ROADMAP.md` flips for this work, and this plan's `requirements-completed` is empty by
design.

Commit the move with plain `git add -A` restricted to the two todo paths plus `git commit` (again
not the GSD commit helper). Message:

  chore(todos): file the literal-block Args docstring todo as completed

ending with the same two attribution lines used in Task 1.
  </action>
  <verify>
    <automated>
set -e
# 1. The move landed, in both directions.
test ! -e .planning/todos/pending/2026-09-20-literal-block-docstring-args-still-name-only-the-literal-block-node.md
test -f .planning/todos/completed/2026-09-20-literal-block-docstring-args-still-name-only-the-literal-block-node.md
# 2. Git recorded it as a rename, not a delete plus an unrelated add. Capture git's status
#    first so a broken `git` cannot be swallowed by the pipeline's last stage.
RENAME="$(git log --diff-filter=R --name-status -1 --format= -- .planning/todos)"
printf '%s\n' "$RENAME"
printf '%s\n' "$RENAME" | grep -q '^R'
# 3. Release-close scope fence: files no quick task may touch are byte-identical to the base.
#    docs/source/conf.py is deliberately absent -- the sibling quick task owns it.
git diff --quiet b367f57609fa3c060986acf89d35d330cfd4724c -- \
  .planning/REQUIREMENTS.md .planning/ROADMAP.md CHANGELOG.md pyproject.toml uv.lock README.md tests/
# 4. REL-15's fence, stated as its own digest so the evidence is readable.
DIGEST_LINE="$(sha256sum .planning/REQUIREMENTS.md)"
printf '%s\n' "$DIGEST_LINE"
test "${DIGEST_LINE%% *}" = 79b93b81b5cf6ffdb20f9ddc0c97ff41969ada3547af1b16c4a20cc577d82d67
# 5. No decoy milestone branch was created by the two commits. Capture first, count second.
BRANCHES="$(git branch --list 'gsd/v0.9.6*')"
printf '%s\n' "$BRANCHES"
test "$(printf '%s\n' "$BRANCHES" | wc -l)" = 1
test "$(git rev-parse --abbrev-ref HEAD)" = gsd/v0.9.6-doctest-block-rendering-and-release
# 6. Working tree clean -- both commits actually landed.
test -z "$(git status --porcelain)"
    </automated>
  </verify>
  <done>
The todo lives under `.planning/todos/completed/` with git recording a rename. `.planning/REQUIREMENTS.md`
still hashes to `79b93b81…` and, together with `.planning/ROADMAP.md`, `CHANGELOG.md`,
`pyproject.toml`, `uv.lock`, `README.md` and `tests/`, is byte-identical to `b367f576`. Exactly one
`gsd/v0.9.6*` branch exists, HEAD is still the milestone branch, and the working tree is clean.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| (none crossed) | This change edits prose inside two Python docstring literals. No input parsing, no network, no filesystem write path, no credential, no user-supplied data, and no executable statement is added, removed, or reordered. Task 1's docstring-stripped AST equivalence check against `b367f576` is the structural proof of that claim, not an assertion. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-260922-TBE-01 | Tampering | `typsphinx/translator.py` — an edit inside a source file could smuggle a behaviour change alongside the documentation change | low | mitigate | Task 1 verify step 3 compares the docstring-stripped AST of the edited file against the blob at `b367f576` and fails on any executable difference. The oracle was proven non-vacuous at planning time: SAME for a docstring-only edit, DIFFERS for a one-token code edit. |
| T-260922-TBE-02 | Information disclosure | the rendered API reference, which publishes these docstrings | low | accept | The added clause names `doctest_block`, a public docutils node type already visible in both method signatures and described at length in `visit_doctest_block`'s own docstring. No path, secret, internal identifier, or previously unpublished fact is introduced. |
| T-260922-TBE-03 | Tampering | `.planning/REQUIREMENTS.md` REL-15 fence during an open release close | low | mitigate | Task 2 verify steps 3 and 4 assert whole-file byte identity against `b367f576` plus the pinned SHA-256, covering REL-15's line-22 checkbox and line-59 traceability row. No `phase.complete`-family tooling is invoked by either task. |

**Supply chain:** no `npm`/`pip`/`cargo`/`uv add` install task exists in this plan — no dependency is
added, removed, or version-changed. The `T-{phase}-SC` package-legitimacy row and its blocking human
checkpoint therefore do not apply, and no `## Package Legitimacy Audit` table is required.

**ASVS L1 / block_on: high** — every threat above is `low`, so nothing here crosses the blocking
threshold. This is the honest verdict for a docstring-text change, not an invented register.
</threat_model>

<verification>
Run from the repository root, after both tasks:

1. `grep -n '^            node: The literal block node, or a doctest block delegated here$' typsphinx/translator.py | wc -l` → `2`
2. `grep -q '^            node: The literal block node$' typsphinx/translator.py` → no match (exit 1)
3. Task 1's AST-equivalence heredoc → `AST-EQUIV OK`
4. `${RUN}ruff check .` → `All checks passed!`; `${RUN}black --check .` → `358 files would be left unchanged.`; `${RUN}mypy typsphinx/` clean
5. `${RUN}pytest tests/test_docstring_rest_census_guard.py tests/test_doctest_block_render_gate.py -q` → `18 passed`
6. `git diff --quiet b367f57609fa3c060986acf89d35d330cfd4724c -- .planning/REQUIREMENTS.md .planning/ROADMAP.md CHANGELOG.md pyproject.toml uv.lock README.md tests/` → exit 0
7. `git status --porcelain` → empty

Deliberately NOT run here: `tox -e docs-html`, `tox -e docs-pdf`, `tox -e linkcheck`, and the full
pytest suite. The orchestrator runs the full local suite once after both quick tasks land; running a
docs build for a docstring edit would cost minutes and measure nothing this plan's checks do not.
</verification>

<success_criteria>
- Both `Args:` parameter lines in `typsphinx/translator.py` name the doctest block, and no
  un-widened remainder survives anywhere in the file.
- The change is provably behaviour-neutral: docstring-stripped AST identical to `b367f576`.
- Lint, format, types and the two targeted test files are green, with the targeted run at 18 passed.
- The tracking todo is under `.planning/todos/completed/`, moved with `git mv`.
- Exactly two commits, touching exactly three paths (the translator plus the todo's two locations).
- The REL-15 release fence is intact and no `phase.complete`-family tooling ran.
</success_criteria>

<output>
Create `.planning/quick/260922-tbe-widen-visit-literal-block-and-depart-lit/260922-tbe-SUMMARY.md`
when done. Record: the two edited line numbers as actually found, the `AST-EQUIV OK` line, the
observed pytest count, the post-edit over-88 line count, and the `.planning/REQUIREMENTS.md` digest
as re-measured at the end.
</output>
