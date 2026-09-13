# Phase 70 — DOC-23 Docs Diff

BASE_70_12 = 44c43e345f8d5916486e5b7c2790bcb16c58f9d0
AFTER_SHA = 44c43e345f8d5916486e5b7c2790bcb16c58f9d0
FLIP_COMMIT = 0224b5ea7f565dfcf7db0a9d8b4394a6a815524d

`FLIP_COMMIT` is the only line of `git log --format=%H "$PHASE_BASE_SHA".."$AFTER_SHA" -- pyproject.toml`
run in this worktree, where `PHASE_BASE_SHA = 697a113221a8a267d7e8c6dd1f2b95672f9454d2`
(70-BASELINE-EVIDENCE.md). `AFTER_SHA` equals this worktree's own `HEAD`, since this worktree
forked from the post-flip tip: `git merge-base --is-ancestor FLIP_COMMIT AFTER_SHA` and
`git merge-base --is-ancestor AFTER_SHA HEAD` both hold trivially.

SCRATCH_70_12 = /tmp/tmp.SH3zNIS9sZ

## Worktree W

Created with `git worktree add --detach "$S/docs-wt" "$PHASE_BASE_SHA"` (no branch):

```
$ git worktree add --detach /tmp/tmp.SH3zNIS9sZ/docs-wt 697a113221a8a267d7e8c6dd1f2b95672f9454d2
Preparing worktree (detached HEAD 697a1132)
HEAD is now at 697a1132 docs(70): create phase plan
```

Provisioned inside `W` with
`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs --python 3.13.13`
(exit 0, 90 packages installed, `typsphinx==0.9.2` built from `/tmp/tmp.SH3zNIS9sZ/docs-wt`).

`W/.venv/pyvenv.cfg`:
```
home = /nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin
implementation = CPython
uv = 0.11.25
version_info = 3.13.13
include-system-site-packages = false
prompt = typsphinx
```

W_VENV_HOME = /nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin
W_VENV_VERSION_INFO = 3.13.13

Both equal 70-02's `VENV_HOME` and `VENV_VERSION_INFO` (70-BASELINE-EVIDENCE.md) — confirmed.

## Builds

One build round `R` (in `W/docs`): `rm -rf _build`, then
`LC_ALL=C uv run sphinx-build -b html source _build/html`, then
`LC_ALL=C uv run sphinx-build -b typstpdf source _build/pdf`, then `cp -a _build "$S/R"`.

- Round A at `PHASE_BASE_SHA` (697a1132…) — same commit W was created at, no re-checkout needed.
- Round B, again at `PHASE_BASE_SHA` — no re-checkout, no re-provisioning; same tree as round A.
- `git -C "$S/docs-wt" checkout --detach "$AFTER_SHA"` (44c43e34…), re-provisioned inside `W`
  (uv resolved the same 91 packages, reinstalled `typsphinx==0.9.2` from the new checkout), then
  round C.

```
$ git -C /tmp/tmp.SH3zNIS9sZ/docs-wt checkout --detach 44c43e345f8d5916486e5b7c2790bcb16c58f9d0
Previous HEAD position was 697a1132 docs(70): create phase plan
HEAD is now at 44c43e34 docs(phase-70): update tracking after wave 4, mark wave 5 executing
```

BUILD_EXITS = 0 0 0 0 0 0

Warning counts (`grep -c WARNING` of each raw log; informational only):

| Round | html | pdf |
|-------|------|-----|
| A     | 4    | 6   |
| B     | 4    | 6   |
| C     | 4    | 6   |

## Control (A vs B)

`diff -rq --exclude=.doctrees "$S/A/html" "$S/B/html"` produced no output (empty).

`.typ` manifests for `$S/A/pdf` and `$S/B/pdf` built with 70-03's manifest command
(`find . -type f -name '*.typ' -print0 | LC_ALL=C sort -z | xargs -0 sha256sum`) and compared
with `cmp`:

```
$ cmp /tmp/tmp.SH3zNIS9sZ/A-typ-manifest.txt /tmp/tmp.SH3zNIS9sZ/B-typ-manifest.txt; echo "exit:$?"
exit:0
```

DOCS_HTML_CONTROL = EQUAL
DOCS_TYP_CONTROL = EQUAL

## Base cross-check

A's HTML manifest (excluding `./.doctrees/`) and A's `.typ` manifest, hashed with SHA-256:

```
$ sha256sum /tmp/tmp.SH3zNIS9sZ/A-html-manifest.txt
57090afbe053c28d1175427a718f0037d592fef5e60897273200109d7ac52a26  /tmp/tmp.SH3zNIS9sZ/A-html-manifest.txt
$ sha256sum /tmp/tmp.SH3zNIS9sZ/A-typ-manifest.txt
47ec16d83bea3e3a6dba13228bd770e28c1d6738381ac39ea6e26cae0f24154d  /tmp/tmp.SH3zNIS9sZ/A-typ-manifest.txt
```

Both equal `DOCS_HTML_MANIFEST_SHA256_BEFORE` and `DOCS_TYP_MANIFEST_SHA256_BEFORE` from
70-CORPUS-DOCS-BASE-EVIDENCE.md exactly.

DOCS_BASE_CROSSCHECK = EQUAL

## Differing files (A vs C)

`LC_ALL=C diff -rq --exclude=.doctrees "$S/A/html" "$S/C/html"`:

```
Files /tmp/tmp.SH3zNIS9sZ/A/html/_modules/typsphinx/builder.html and /tmp/tmp.SH3zNIS9sZ/C/html/_modules/typsphinx/builder.html differ
Files /tmp/tmp.SH3zNIS9sZ/A/html/_modules/typsphinx/template_engine.html and /tmp/tmp.SH3zNIS9sZ/C/html/_modules/typsphinx/template_engine.html differ
Files /tmp/tmp.SH3zNIS9sZ/A/html/_modules/typsphinx/translator.html and /tmp/tmp.SH3zNIS9sZ/C/html/_modules/typsphinx/translator.html differ
Files /tmp/tmp.SH3zNIS9sZ/A/html/_modules/typsphinx/writer.html and /tmp/tmp.SH3zNIS9sZ/C/html/_modules/typsphinx/writer.html differ
Files /tmp/tmp.SH3zNIS9sZ/A/html/api/index.html and /tmp/tmp.SH3zNIS9sZ/C/html/api/index.html differ
```

No `Only in` line — no file appeared or vanished (both trees produce 62 HTML files, matching
`DOCS_HTML_FILE_COUNT_BEFORE` from 70-CORPUS-DOCS-BASE-EVIDENCE.md).

DIFF_HTML: _modules/typsphinx/builder.html
DIFF_HTML: _modules/typsphinx/template_engine.html
DIFF_HTML: _modules/typsphinx/translator.html
DIFF_HTML: _modules/typsphinx/writer.html
DIFF_HTML: api/index.html

`.typ` manifests compared the same way (A vs C):

```
$ diff /tmp/tmp.SH3zNIS9sZ/A-typ-manifest.txt /tmp/tmp.SH3zNIS9sZ/C-typ-manifest.txt
2c2
< d5a8d071171917db6ffad78552f7889b4d02daa4fe1c9584b4276930e544f4d9  ./api/index.typ
---
> f3428fbac6fc96492cfa56f373bb751a919460324bc24cf47e95bcef9cdab4bc  ./api/index.typ
```

Both manifests list 16 `.typ` files — no file appeared or vanished.

DIFF_TYP: api/index.typ

DOCS_HTML_DIFF_FILES = 5
DOCS_TYP_DIFF_FILES = 1

Location rule (D-11 as amended): every `DIFF_HTML` path starts with `api/` or
`_modules/typsphinx/`; every `DIFF_TYP` path starts with `api/`. Confirmed for all 6 lines above
— no `## HALT: D-11 location` needed. This exactly matches 70-RESEARCH.md Pitfall 8's measured
shape (four `_modules/typsphinx/{builder,template_engine,translator,writer}.html` pages plus
`api/index.html`).

`W` removed and pruned:

```
$ git worktree remove --force /tmp/tmp.SH3zNIS9sZ/docs-wt
$ git worktree prune
$ git worktree list
/home/yuta/Documents/typsphinx                                           44c43e34 [gsd/v0.9.4-typing-modernization]
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a099ef5f3ff5bdb00 44c43e34 [worktree-agent-a099ef5f3ff5bdb00] locked
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a23300b9d4a0085b6 44c43e34 [worktree-agent-a23300b9d4a0085b6] locked
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-aacdace25a411b095 81084801 [worktree-agent-aacdace25a411b095] locked
```

`/tmp/tmp.SH3zNIS9sZ/docs-wt` does not appear — `W` is absent from `git worktree list`.
