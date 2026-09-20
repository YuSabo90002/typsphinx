# Phase 75 — Phase 74 Leftovers (D-13, D-14)

## Head check and provisioning

```
$ date -u +%FT%TZ
2026-09-20T08:37:07Z

$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a8562597c86a9f656

$ test -f .git; echo "exit:$?"
exit:0

$ command -v uv
/nix/store/3vpzk25whpm7s8zq5flpk8gbpkggj9np-uv/bin/uv

$ grep -q typsphinx-fhs-run "$(command -v uv)"; echo "exit:$?"
exit:0

$ env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs
... (tail)
 + typsphinx==0.9.2 (from file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-a8562597c86a9f656)
 + typst==0.15.0
 + uv==0.12.13
 + virtualenv==21.5.1
exit:0
```

BASE_75_02 = 526a21d352696cb65c570d07d75ef8c7e3aa96a1

SCRATCH_75_02 = /tmp/p7502_FAHvoy

## Main checkout identity

```
$ test -d /home/yuta/Documents/typsphinx/.git; echo "exit:$?"
exit:0

$ git -C /home/yuta/Documents/typsphinx rev-parse --show-toplevel
/home/yuta/Documents/typsphinx
```

MAIN_CHECKOUT_CONFIRMED = yes

This task acts only on the main checkout's five untracked `probe_*.typ` working-tree files at its
repository root, and touches nothing else there — no tracked file, no ref, no `git` command that
writes in that checkout.

## Probe census before

```
$ git -C /home/yuta/Documents/typsphinx status --porcelain
?? .planning/milestone.lock
?? probe_bogusxyz.typ
?? probe_none.typ
?? probe_pycon.typ
?? probe_python.typ
?? probe_text.typ
```

```
$ find /home/yuta/Documents/typsphinx -maxdepth 1 -name 'probe_*.typ' -printf '%p %s\n'
/home/yuta/Documents/typsphinx/probe_none.typ 154
/home/yuta/Documents/typsphinx/probe_pycon.typ 159
/home/yuta/Documents/typsphinx/probe_python.typ 160
/home/yuta/Documents/typsphinx/probe_text.typ 158
/home/yuta/Documents/typsphinx/probe_bogusxyz.typ 162
```

PROBE_FILES_BEFORE = 5

Tracked-status check, one `git -C <main> ls-files --error-unmatch <path>` per file — every exit must
be non-zero (untracked):

```
$ git -C /home/yuta/Documents/typsphinx ls-files --error-unmatch probe_bogusxyz.typ; echo "exit:$?"
exit:1
$ git -C /home/yuta/Documents/typsphinx ls-files --error-unmatch probe_none.typ; echo "exit:$?"
exit:1
$ git -C /home/yuta/Documents/typsphinx ls-files --error-unmatch probe_pycon.typ; echo "exit:$?"
exit:1
$ git -C /home/yuta/Documents/typsphinx ls-files --error-unmatch probe_python.typ; echo "exit:$?"
exit:1
$ git -C /home/yuta/Documents/typsphinx ls-files --error-unmatch probe_text.typ; echo "exit:$?"
exit:1
```

PROBE_TRACKED_HITS = 0

| File | Size (bytes) | First line |
|------|--------------|------------|
| probe_bogusxyz.typ | 162 | ` ```bogusxyz` |
| probe_none.typ | 154 | ` ``` ` |
| probe_pycon.typ | 159 | ` ```pycon` |
| probe_python.typ | 160 | ` ```python` |
| probe_text.typ | 158 | ` ```text` |

None of the five paths was already absent, so no short-circuit applies and no path matched a tracked
file — the deletion proceeds in step "## Deletion" below.

## Deletion

```
$ rm /home/yuta/Documents/typsphinx/probe_bogusxyz.typ; echo "exit:$?"
exit:0
$ rm /home/yuta/Documents/typsphinx/probe_none.typ; echo "exit:$?"
exit:0
$ rm /home/yuta/Documents/typsphinx/probe_pycon.typ; echo "exit:$?"
exit:0
$ rm /home/yuta/Documents/typsphinx/probe_python.typ; echo "exit:$?"
exit:0
$ rm /home/yuta/Documents/typsphinx/probe_text.typ; echo "exit:$?"
exit:0
```

## Probe census after

```
$ find /home/yuta/Documents/typsphinx -maxdepth 1 -name 'probe_*.typ' -printf '%p %s\n'
(no output)
```

PROBE_FILES_AFTER = 0

```
$ git -C /home/yuta/Documents/typsphinx status --porcelain
?? .planning/milestone.lock
```

The only remaining untracked row in the main checkout is `.planning/milestone.lock`, which is
outside this task's file set and was not touched.

```
$ git -C /home/yuta/Documents/typsphinx diff --name-only -- .gitignore
(empty)
```

GITIGNORE_UNCHANGED = yes

D-13 rejected an ignore rule for these files as a product-tree commit outside the file set REL-15
names; the fix taken here is deletion alone, with `.gitignore` left unchanged in both the main
checkout and this worktree.

## D-14: IN-01 filed, not fixed

TODO_PATH = .planning/todos/pending/2026-09-20-literal-block-docstring-args-still-name-only-the-literal-block-node.md

TODO_PENDING_COUNT = 4

```
$ ls .planning/todos/pending/ | wc -l
4

$ git diff --name-only -- typsphinx
(empty)
```

`74-REVIEW.md`'s unresolved Info finding IN-01 — `visit_literal_block` / `depart_literal_block`
still document `node: The literal block node` although both signatures were widened to
`nodes.literal_block | nodes.doctest_block` — is filed as a pending todo rather than fixed here.
The re-measured line numbers (`translator.py:2444-2445` and `:2594-2595`) match the review's cited
ranges within one line (the review counted from the docstring's leading blank line). No line under
`typsphinx/` was changed or is dirty.

## API coverage declaration

API_COVERAGE_PASSED = true

```
$ node /home/yuta/Documents/typsphinx/.claude/gsd-core/bin/gsd-tools.cjs check api-coverage.verify-pre .planning/phases/75-v0-9-6-release-prep-prep-only
{
  "block": false,
  "passed": true,
  "coverage_present": true,
  "matrix": "COVERAGE.md",
  "counts": {
    "surface": 0,
    "integrate": 0,
    "optout": 0
  },
  "none_declared": true,
  "detected": true,
  "signals": [
    {
      "verb": "integration",
      "noun": "api"
    },
    {
      "verb": "(surface)",
      "noun": "api"
    }
  ],
  "message": "api-coverage: COVERAGE.md declares no external API integration, overriding 2 detected signal(s) — confirm the declaration is accurate"
}
```

The gate's own detector flagged 2 signals from this phase's prose (the words "integration" and
"api"). Each surface a detector could misread as an external API integration, and why it is not
one:

- **`gh api`** — reads this repository's own branch protection settings (a read-only probe of
  `main`'s protection rules for the merge-preflight plan), not a call to any third-party API this
  project builds against.
- **`gh workflow run`** — dispatches this repository's own CI workflow (`ci.yml`) on the milestone
  branch; a single `workflow_dispatch` invocation, not an integration client.
- **PyPI JSON endpoint** — an unauthenticated GET against `https://pypi.org/pypi/typsphinx/<version>/json`
  used purely as a 404-or-200 probe of this project's own package page, to confirm a version is
  or is not yet published. No credential path, no retry policy, no wrapper module.
- **Read the Docs endpoints** — appear only as steps named inside `75-HANDOFF.md`, to be executed
  by a later command after this milestone actually ships; nothing in this phase calls them.

No client, wrapper, credential path or retry policy is built anywhere in this phase; every one of
these is a read-only probe or a single dispatch of infrastructure this project already owns.
