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

## Raw diffs

### html: _modules/typsphinx/builder.html

~~~diff
--- /tmp/tmp.SH3zNIS9sZ/A/html/_modules/typsphinx/builder.html	2026-09-13 14:41:35.547010155 +0900
+++ /tmp/tmp.SH3zNIS9sZ/C/html/_modules/typsphinx/builder.html	2026-09-13 14:42:21.208483711 +0900
@@ -280 +280 @@
-<span class="kn">from</span><span class="w"> </span><span class="nn">typing</span><span class="w"> </span><span class="kn">import</span> <span class="n">Any</span><span class="p">,</span> <span class="n">Dict</span><span class="p">,</span> <span class="n">List</span><span class="p">,</span> <span class="n">Set</span><span class="p">,</span> <span class="n">Tuple</span>
+<span class="kn">from</span><span class="w"> </span><span class="nn">typing</span><span class="w"> </span><span class="kn">import</span> <span class="n">Any</span>
@@ -1007 +1007 @@
-        <span class="bp">self</span><span class="o">.</span><span class="n">_master_include_edges</span><span class="p">:</span> <span class="n">Dict</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="n">Tuple</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="o">...</span><span class="p">]]</span> <span class="o">=</span> <span class="p">{}</span>
+        <span class="bp">self</span><span class="o">.</span><span class="n">_master_include_edges</span><span class="p">:</span> <span class="nb">dict</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="nb">tuple</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="o">...</span><span class="p">]]</span> <span class="o">=</span> <span class="p">{}</span>
@@ -1017 +1017 @@
-        <span class="bp">self</span><span class="o">.</span><span class="n">_document_template_registry</span><span class="p">:</span> <span class="n">Dict</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="n">TemplateRegistryEntry</span><span class="p">]</span> <span class="o">=</span> <span class="p">{}</span>
+        <span class="bp">self</span><span class="o">.</span><span class="n">_document_template_registry</span><span class="p">:</span> <span class="nb">dict</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="n">TemplateRegistryEntry</span><span class="p">]</span> <span class="o">=</span> <span class="p">{}</span>
@@ -1032 +1032 @@
-    <span class="k">def</span><span class="w"> </span><span class="nf">_build_include_edge_map</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span> <span class="o">-&gt;</span> <span class="n">Dict</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="n">Tuple</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="o">...</span><span class="p">]]:</span>
+    <span class="k">def</span><span class="w"> </span><span class="nf">_build_include_edge_map</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span> <span class="o">-&gt;</span> <span class="nb">dict</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="nb">tuple</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="o">...</span><span class="p">]]:</span>
@@ -1069 +1069 @@
-        <span class="n">edge_map</span><span class="p">:</span> <span class="n">Dict</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="n">Tuple</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="o">...</span><span class="p">]]</span> <span class="o">=</span> <span class="p">{}</span>
+        <span class="n">edge_map</span><span class="p">:</span> <span class="nb">dict</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="nb">tuple</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="o">...</span><span class="p">]]</span> <span class="o">=</span> <span class="p">{}</span>
@@ -1405,2 +1405,2 @@
-        <span class="n">claims</span><span class="p">:</span> <span class="n">Dict</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="nb">str</span><span class="p">]</span> <span class="o">=</span> <span class="p">{}</span>
-        <span class="n">failures</span><span class="p">:</span> <span class="n">List</span><span class="p">[</span><span class="n">Tuple</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="nb">str</span><span class="p">]]</span> <span class="o">=</span> <span class="p">[]</span>
+        <span class="n">claims</span><span class="p">:</span> <span class="nb">dict</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="nb">str</span><span class="p">]</span> <span class="o">=</span> <span class="p">{}</span>
+        <span class="n">failures</span><span class="p">:</span> <span class="nb">list</span><span class="p">[</span><span class="nb">tuple</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="nb">str</span><span class="p">]]</span> <span class="o">=</span> <span class="p">[]</span>
@@ -1730 +1730 @@
-        <span class="n">used_keys</span><span class="p">:</span> <span class="n">Set</span><span class="p">[</span><span class="nb">str</span><span class="p">]</span> <span class="o">=</span> <span class="nb">set</span><span class="p">()</span>
+        <span class="n">used_keys</span><span class="p">:</span> <span class="nb">set</span><span class="p">[</span><span class="nb">str</span><span class="p">]</span> <span class="o">=</span> <span class="nb">set</span><span class="p">()</span>
@@ -1740 +1740 @@
-        <span class="n">templates_path_entries</span><span class="p">:</span> <span class="n">List</span><span class="p">[</span><span class="n">Tuple</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="nb">str</span><span class="p">]]</span> <span class="o">=</span> <span class="p">[]</span>
+        <span class="n">templates_path_entries</span><span class="p">:</span> <span class="nb">list</span><span class="p">[</span><span class="nb">tuple</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="nb">str</span><span class="p">]]</span> <span class="o">=</span> <span class="p">[]</span>
@@ -1748 +1748 @@
-        <span class="n">failures</span><span class="p">:</span> <span class="n">List</span><span class="p">[</span><span class="n">Tuple</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="nb">str</span><span class="p">]]</span> <span class="o">=</span> <span class="p">[]</span>
+        <span class="n">failures</span><span class="p">:</span> <span class="nb">list</span><span class="p">[</span><span class="nb">tuple</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="nb">str</span><span class="p">]]</span> <span class="o">=</span> <span class="p">[]</span>
@@ -1918 +1918 @@
-    <span class="k">def</span><span class="w"> </span><span class="nf">prepare_writing</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span> <span class="n">docnames</span><span class="p">:</span> <span class="n">Set</span><span class="p">[</span><span class="nb">str</span><span class="p">])</span> <span class="o">-&gt;</span> <span class="kc">None</span><span class="p">:</span>
+    <span class="k">def</span><span class="w"> </span><span class="nf">prepare_writing</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span> <span class="n">docnames</span><span class="p">:</span> <span class="nb">set</span><span class="p">[</span><span class="nb">str</span><span class="p">])</span> <span class="o">-&gt;</span> <span class="kc">None</span><span class="p">:</span>
@@ -1939,2 +1939,2 @@
-        <span class="n">build_docnames</span><span class="p">:</span> <span class="n">Set</span><span class="p">[</span><span class="nb">str</span><span class="p">]</span> <span class="o">|</span> <span class="kc">None</span><span class="p">,</span>
-        <span class="n">updated_docnames</span><span class="p">:</span> <span class="n">Set</span><span class="p">[</span><span class="nb">str</span><span class="p">],</span>
+        <span class="n">build_docnames</span><span class="p">:</span> <span class="nb">set</span><span class="p">[</span><span class="nb">str</span><span class="p">]</span> <span class="o">|</span> <span class="kc">None</span><span class="p">,</span>
+        <span class="n">updated_docnames</span><span class="p">:</span> <span class="nb">set</span><span class="p">[</span><span class="nb">str</span><span class="p">],</span>
@@ -2647,3 +2647,3 @@
-        <span class="n">destinations</span><span class="p">:</span> <span class="n">Dict</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="n">Tuple</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="nb">str</span><span class="p">]]</span> <span class="o">=</span> <span class="p">{}</span>
-        <span class="n">failures</span><span class="p">:</span> <span class="n">List</span><span class="p">[</span><span class="n">Tuple</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="nb">str</span><span class="p">]]</span> <span class="o">=</span> <span class="p">[]</span>
-        <span class="n">to_copy</span><span class="p">:</span> <span class="n">List</span><span class="p">[</span><span class="n">Tuple</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="n">Any</span><span class="p">,</span> <span class="nb">str</span><span class="p">,</span> <span class="nb">str</span><span class="p">]]</span> <span class="o">=</span> <span class="p">[]</span>
+        <span class="n">destinations</span><span class="p">:</span> <span class="nb">dict</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="nb">tuple</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="nb">str</span><span class="p">]]</span> <span class="o">=</span> <span class="p">{}</span>
+        <span class="n">failures</span><span class="p">:</span> <span class="nb">list</span><span class="p">[</span><span class="nb">tuple</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="nb">str</span><span class="p">]]</span> <span class="o">=</span> <span class="p">[]</span>
+        <span class="n">to_copy</span><span class="p">:</span> <span class="nb">list</span><span class="p">[</span><span class="nb">tuple</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="n">Any</span><span class="p">,</span> <span class="nb">str</span><span class="p">,</span> <span class="nb">str</span><span class="p">]]</span> <span class="o">=</span> <span class="p">[]</span>
@@ -2853 +2853 @@
-        <span class="n">failures</span><span class="p">:</span> <span class="n">List</span><span class="p">[</span><span class="n">Tuple</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="nb">str</span><span class="p">]]</span> <span class="o">=</span> <span class="p">[]</span>
+        <span class="n">failures</span><span class="p">:</span> <span class="nb">list</span><span class="p">[</span><span class="nb">tuple</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="nb">str</span><span class="p">]]</span> <span class="o">=</span> <span class="p">[]</span>
~~~

### html: _modules/typsphinx/template_engine.html

~~~diff
--- /tmp/tmp.SH3zNIS9sZ/A/html/_modules/typsphinx/template_engine.html	2026-09-13 14:41:35.578420884 +0900
+++ /tmp/tmp.SH3zNIS9sZ/C/html/_modules/typsphinx/template_engine.html	2026-09-13 14:42:21.242210277 +0900
@@ -280 +280 @@
-<span class="kn">from</span><span class="w"> </span><span class="nn">typing</span><span class="w"> </span><span class="kn">import</span> <span class="n">Any</span><span class="p">,</span> <span class="n">Dict</span><span class="p">,</span> <span class="n">List</span>
+<span class="kn">from</span><span class="w"> </span><span class="nn">typing</span><span class="w"> </span><span class="kn">import</span> <span class="n">Any</span>
@@ -383 +383 @@
-<span class="n">ELEMENTS_ALLOWLIST</span><span class="p">:</span> <span class="n">Dict</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="nb">str</span><span class="p">]</span> <span class="o">=</span> <span class="p">{</span>
+<span class="n">ELEMENTS_ALLOWLIST</span><span class="p">:</span> <span class="nb">dict</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="nb">str</span><span class="p">]</span> <span class="o">=</span> <span class="p">{</span>
@@ -546,2 +546,2 @@
-        <span class="n">search_paths</span><span class="p">:</span> <span class="n">List</span><span class="p">[</span><span class="nb">str</span><span class="p">]</span> <span class="o">|</span> <span class="kc">None</span> <span class="o">=</span> <span class="kc">None</span><span class="p">,</span>
-        <span class="n">parameter_mapping</span><span class="p">:</span> <span class="n">Dict</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="nb">str</span><span class="p">]</span> <span class="o">|</span> <span class="kc">None</span> <span class="o">=</span> <span class="kc">None</span><span class="p">,</span>
+        <span class="n">search_paths</span><span class="p">:</span> <span class="nb">list</span><span class="p">[</span><span class="nb">str</span><span class="p">]</span> <span class="o">|</span> <span class="kc">None</span> <span class="o">=</span> <span class="kc">None</span><span class="p">,</span>
+        <span class="n">parameter_mapping</span><span class="p">:</span> <span class="nb">dict</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="nb">str</span><span class="p">]</span> <span class="o">|</span> <span class="kc">None</span> <span class="o">=</span> <span class="kc">None</span><span class="p">,</span>
@@ -550 +550 @@
-        <span class="n">typst_package_imports</span><span class="p">:</span> <span class="n">List</span><span class="p">[</span><span class="nb">str</span><span class="p">]</span> <span class="o">|</span> <span class="kc">None</span> <span class="o">=</span> <span class="kc">None</span><span class="p">,</span>
+        <span class="n">typst_package_imports</span><span class="p">:</span> <span class="nb">list</span><span class="p">[</span><span class="nb">str</span><span class="p">]</span> <span class="o">|</span> <span class="kc">None</span> <span class="o">=</span> <span class="kc">None</span><span class="p">,</span>
@@ -766,3 +766,3 @@
-        <span class="n">sphinx_metadata</span><span class="p">:</span> <span class="n">Dict</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="n">Any</span><span class="p">],</span>
-        <span class="n">typst_elements</span><span class="p">:</span> <span class="n">Dict</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="n">Any</span><span class="p">]</span> <span class="o">|</span> <span class="kc">None</span> <span class="o">=</span> <span class="kc">None</span><span class="p">,</span>
-    <span class="p">)</span> <span class="o">-&gt;</span> <span class="n">Dict</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="n">Any</span><span class="p">]:</span>
+        <span class="n">sphinx_metadata</span><span class="p">:</span> <span class="nb">dict</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="n">Any</span><span class="p">],</span>
+        <span class="n">typst_elements</span><span class="p">:</span> <span class="nb">dict</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="n">Any</span><span class="p">]</span> <span class="o">|</span> <span class="kc">None</span> <span class="o">=</span> <span class="kc">None</span><span class="p">,</span>
+    <span class="p">)</span> <span class="o">-&gt;</span> <span class="nb">dict</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="n">Any</span><span class="p">]:</span>
@@ -803 +803 @@
-        <span class="n">params</span><span class="p">:</span> <span class="n">Dict</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="n">Any</span><span class="p">]</span> <span class="o">=</span> <span class="p">{}</span>
+        <span class="n">params</span><span class="p">:</span> <span class="nb">dict</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="n">Any</span><span class="p">]</span> <span class="o">=</span> <span class="p">{}</span>
@@ -908 +908 @@
-    <span class="k">def</span><span class="w"> </span><span class="nf">extract_toctree_options</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span> <span class="n">doctree</span><span class="p">:</span> <span class="n">Any</span><span class="p">)</span> <span class="o">-&gt;</span> <span class="n">Dict</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="n">Any</span><span class="p">]:</span>
+    <span class="k">def</span><span class="w"> </span><span class="nf">extract_toctree_options</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span> <span class="n">doctree</span><span class="p">:</span> <span class="n">Any</span><span class="p">)</span> <span class="o">-&gt;</span> <span class="nb">dict</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="n">Any</span><span class="p">]:</span>
@@ -975 +975 @@
-        <span class="bp">self</span><span class="p">,</span> <span class="n">params</span><span class="p">:</span> <span class="n">Dict</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="n">Any</span><span class="p">],</span> <span class="n">body</span><span class="p">:</span> <span class="nb">str</span><span class="p">,</span> <span class="n">template_file</span><span class="p">:</span> <span class="nb">str</span> <span class="o">=</span> <span class="kc">None</span>
+        <span class="bp">self</span><span class="p">,</span> <span class="n">params</span><span class="p">:</span> <span class="nb">dict</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="n">Any</span><span class="p">],</span> <span class="n">body</span><span class="p">:</span> <span class="nb">str</span><span class="p">,</span> <span class="n">template_file</span><span class="p">:</span> <span class="nb">str</span> <span class="o">=</span> <span class="kc">None</span>
~~~

### html: _modules/typsphinx/translator.html

~~~diff
--- /tmp/tmp.SH3zNIS9sZ/A/html/_modules/typsphinx/translator.html	2026-09-13 14:41:35.708021341 +0900
+++ /tmp/tmp.SH3zNIS9sZ/C/html/_modules/typsphinx/translator.html	2026-09-13 14:42:21.381222184 +0900
@@ -276 +276 @@
-<span class="kn">from</span><span class="w"> </span><span class="nn">typing</span><span class="w"> </span><span class="kn">import</span> <span class="n">Any</span><span class="p">,</span> <span class="n">Dict</span><span class="p">,</span> <span class="n">List</span><span class="p">,</span> <span class="n">NamedTuple</span><span class="p">,</span> <span class="n">Tuple</span>
+<span class="kn">from</span><span class="w"> </span><span class="nn">typing</span><span class="w"> </span><span class="kn">import</span> <span class="n">Any</span><span class="p">,</span> <span class="n">NamedTuple</span>
@@ -393 +393 @@
-    <span class="n">xref</span><span class="p">:</span> <span class="n">Tuple</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="nb">str</span><span class="p">]</span> <span class="o">|</span> <span class="kc">None</span>
+    <span class="n">xref</span><span class="p">:</span> <span class="nb">tuple</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="nb">str</span><span class="p">]</span> <span class="o">|</span> <span class="kc">None</span>
@@ -619,2 +619,2 @@
-    <span class="n">toctree_includes</span><span class="p">:</span> <span class="n">Dict</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="n">List</span><span class="p">[</span><span class="nb">str</span><span class="p">]],</span> <span class="n">master_docname</span><span class="p">:</span> <span class="nb">str</span>
-<span class="p">)</span> <span class="o">-&gt;</span> <span class="n">Tuple</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="o">...</span><span class="p">]:</span>
+    <span class="n">toctree_includes</span><span class="p">:</span> <span class="nb">dict</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="nb">list</span><span class="p">[</span><span class="nb">str</span><span class="p">]],</span> <span class="n">master_docname</span><span class="p">:</span> <span class="nb">str</span>
+<span class="p">)</span> <span class="o">-&gt;</span> <span class="nb">tuple</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="o">...</span><span class="p">]:</span>
@@ -685,2 +685,2 @@
-    <span class="n">traversed</span><span class="p">:</span> <span class="n">List</span><span class="p">[</span><span class="nb">str</span><span class="p">]</span> <span class="o">=</span> <span class="p">[</span><span class="n">master_docname</span><span class="p">]</span>
-    <span class="n">edge_keys</span><span class="p">:</span> <span class="n">List</span><span class="p">[</span><span class="nb">str</span><span class="p">]</span> <span class="o">=</span> <span class="p">[]</span>
+    <span class="n">traversed</span><span class="p">:</span> <span class="nb">list</span><span class="p">[</span><span class="nb">str</span><span class="p">]</span> <span class="o">=</span> <span class="p">[</span><span class="n">master_docname</span><span class="p">]</span>
+    <span class="n">edge_keys</span><span class="p">:</span> <span class="nb">list</span><span class="p">[</span><span class="nb">str</span><span class="p">]</span> <span class="o">=</span> <span class="p">[]</span>
@@ -688 +688 @@
-    <span class="k">def</span><span class="w"> </span><span class="nf">walk</span><span class="p">(</span><span class="n">parent</span><span class="p">:</span> <span class="nb">str</span><span class="p">,</span> <span class="n">depth</span><span class="p">:</span> <span class="nb">int</span><span class="p">,</span> <span class="n">path</span><span class="p">:</span> <span class="n">Tuple</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="o">...</span><span class="p">])</span> <span class="o">-&gt;</span> <span class="kc">None</span><span class="p">:</span>
+    <span class="k">def</span><span class="w"> </span><span class="nf">walk</span><span class="p">(</span><span class="n">parent</span><span class="p">:</span> <span class="nb">str</span><span class="p">,</span> <span class="n">depth</span><span class="p">:</span> <span class="nb">int</span><span class="p">,</span> <span class="n">path</span><span class="p">:</span> <span class="nb">tuple</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="o">...</span><span class="p">])</span> <span class="o">-&gt;</span> <span class="kc">None</span><span class="p">:</span>
@@ -711 +711 @@
-<span class="k">def</span><span class="w"> </span><span class="nf">render_include_edge_state</span><span class="p">(</span><span class="n">edge_keys</span><span class="p">:</span> <span class="n">Tuple</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="o">...</span><span class="p">])</span> <span class="o">-&gt;</span> <span class="nb">str</span><span class="p">:</span>
+<span class="k">def</span><span class="w"> </span><span class="nf">render_include_edge_state</span><span class="p">(</span><span class="n">edge_keys</span><span class="p">:</span> <span class="nb">tuple</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="o">...</span><span class="p">])</span> <span class="o">-&gt;</span> <span class="nb">str</span><span class="p">:</span>
@@ -818 +818 @@
-        <span class="bp">self</span><span class="o">.</span><span class="n">table_colwidths</span><span class="p">:</span> <span class="n">List</span><span class="p">[</span><span class="n">Any</span><span class="p">]</span> <span class="o">=</span> <span class="p">(</span>
+        <span class="bp">self</span><span class="o">.</span><span class="n">table_colwidths</span><span class="p">:</span> <span class="nb">list</span><span class="p">[</span><span class="n">Any</span><span class="p">]</span> <span class="o">=</span> <span class="p">(</span>
@@ -840 +840 @@
-        <span class="bp">self</span><span class="o">.</span><span class="n">_caption_saved_list_state</span><span class="p">:</span> <span class="n">Tuple</span><span class="p">[</span><span class="nb">bool</span><span class="p">,</span> <span class="nb">bool</span><span class="p">]</span> <span class="o">|</span> <span class="kc">None</span> <span class="o">=</span> <span class="p">(</span>
+        <span class="bp">self</span><span class="o">.</span><span class="n">_caption_saved_list_state</span><span class="p">:</span> <span class="nb">tuple</span><span class="p">[</span><span class="nb">bool</span><span class="p">,</span> <span class="nb">bool</span><span class="p">]</span> <span class="o">|</span> <span class="kc">None</span> <span class="o">=</span> <span class="p">(</span>
@@ -869 +869 @@
-        <span class="bp">self</span><span class="o">.</span><span class="n">_table_state_stack</span><span class="p">:</span> <span class="n">List</span><span class="p">[</span><span class="n">Dict</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="n">Any</span><span class="p">]]</span> <span class="o">=</span> <span class="p">[]</span>
+        <span class="bp">self</span><span class="o">.</span><span class="n">_table_state_stack</span><span class="p">:</span> <span class="nb">list</span><span class="p">[</span><span class="nb">dict</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="n">Any</span><span class="p">]]</span> <span class="o">=</span> <span class="p">[]</span>
@@ -874 +874 @@
-        <span class="bp">self</span><span class="o">.</span><span class="n">_saved_body_for_figure_caption</span><span class="p">:</span> <span class="n">List</span><span class="p">[</span><span class="n">Any</span><span class="p">]</span> <span class="o">|</span> <span class="kc">None</span> <span class="o">=</span> <span class="p">(</span>
+        <span class="bp">self</span><span class="o">.</span><span class="n">_saved_body_for_figure_caption</span><span class="p">:</span> <span class="nb">list</span><span class="p">[</span><span class="n">Any</span><span class="p">]</span> <span class="o">|</span> <span class="kc">None</span> <span class="o">=</span> <span class="p">(</span>
@@ -893 +893 @@
-        <span class="bp">self</span><span class="o">.</span><span class="n">_figure_state_stack</span><span class="p">:</span> <span class="n">List</span><span class="p">[</span><span class="n">Dict</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="n">Any</span><span class="p">]]</span> <span class="o">=</span> <span class="p">[]</span>
+        <span class="bp">self</span><span class="o">.</span><span class="n">_figure_state_stack</span><span class="p">:</span> <span class="nb">list</span><span class="p">[</span><span class="nb">dict</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="n">Any</span><span class="p">]]</span> <span class="o">=</span> <span class="p">[]</span>
@@ -921 +921 @@
-        <span class="bp">self</span><span class="o">.</span><span class="n">_list_item_stack</span><span class="p">:</span> <span class="n">List</span><span class="p">[</span><span class="nb">bool</span><span class="p">]</span> <span class="o">=</span> <span class="p">[]</span>
+        <span class="bp">self</span><span class="o">.</span><span class="n">_list_item_stack</span><span class="p">:</span> <span class="nb">list</span><span class="p">[</span><span class="nb">bool</span><span class="p">]</span> <span class="o">=</span> <span class="p">[]</span>
@@ -938 +938 @@
-        <span class="bp">self</span><span class="o">.</span><span class="n">_legend_list_item_stack</span><span class="p">:</span> <span class="n">List</span><span class="p">[</span><span class="n">Tuple</span><span class="p">[</span><span class="nb">bool</span><span class="p">,</span> <span class="nb">bool</span><span class="p">]]</span> <span class="o">=</span> <span class="p">[]</span>
+        <span class="bp">self</span><span class="o">.</span><span class="n">_legend_list_item_stack</span><span class="p">:</span> <span class="nb">list</span><span class="p">[</span><span class="nb">tuple</span><span class="p">[</span><span class="nb">bool</span><span class="p">,</span> <span class="nb">bool</span><span class="p">]]</span> <span class="o">=</span> <span class="p">[]</span>
@@ -1057,2 +1057,2 @@
-        <span class="bp">self</span><span class="o">.</span><span class="n">current_term_buffer</span><span class="p">:</span> <span class="nb">str</span> <span class="o">|</span> <span class="n">List</span><span class="p">[</span><span class="nb">str</span><span class="p">]</span> <span class="o">|</span> <span class="kc">None</span> <span class="o">=</span> <span class="kc">None</span>
-        <span class="bp">self</span><span class="o">.</span><span class="n">current_definition_buffer</span><span class="p">:</span> <span class="n">List</span><span class="p">[</span><span class="nb">str</span><span class="p">]</span> <span class="o">|</span> <span class="kc">None</span> <span class="o">=</span> <span class="kc">None</span>
+        <span class="bp">self</span><span class="o">.</span><span class="n">current_term_buffer</span><span class="p">:</span> <span class="nb">str</span> <span class="o">|</span> <span class="nb">list</span><span class="p">[</span><span class="nb">str</span><span class="p">]</span> <span class="o">|</span> <span class="kc">None</span> <span class="o">=</span> <span class="kc">None</span>
+        <span class="bp">self</span><span class="o">.</span><span class="n">current_definition_buffer</span><span class="p">:</span> <span class="nb">list</span><span class="p">[</span><span class="nb">str</span><span class="p">]</span> <span class="o">|</span> <span class="kc">None</span> <span class="o">=</span> <span class="kc">None</span>
@@ -1082 +1082 @@
-        <span class="bp">self</span><span class="o">.</span><span class="n">_field_body_stack</span><span class="p">:</span> <span class="n">List</span><span class="p">[</span><span class="n">Tuple</span><span class="p">[</span><span class="nb">bool</span><span class="p">,</span> <span class="nb">bool</span><span class="p">,</span> <span class="nb">bool</span><span class="p">]]</span> <span class="o">=</span> <span class="p">[]</span>
+        <span class="bp">self</span><span class="o">.</span><span class="n">_field_body_stack</span><span class="p">:</span> <span class="nb">list</span><span class="p">[</span><span class="nb">tuple</span><span class="p">[</span><span class="nb">bool</span><span class="p">,</span> <span class="nb">bool</span><span class="p">,</span> <span class="nb">bool</span><span class="p">]]</span> <span class="o">=</span> <span class="p">[]</span>
@@ -1096 +1096 @@
-        <span class="bp">self</span><span class="o">.</span><span class="n">_inline_concat_stack</span><span class="p">:</span> <span class="n">List</span><span class="p">[</span><span class="n">Tuple</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="nb">str</span><span class="p">]</span> <span class="o">|</span> <span class="kc">None</span><span class="p">]</span> <span class="o">=</span> <span class="p">[]</span>
+        <span class="bp">self</span><span class="o">.</span><span class="n">_inline_concat_stack</span><span class="p">:</span> <span class="nb">list</span><span class="p">[</span><span class="nb">tuple</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="nb">str</span><span class="p">]</span> <span class="o">|</span> <span class="kc">None</span><span class="p">]</span> <span class="o">=</span> <span class="p">[]</span>
@@ -1100 +1100 @@
-        <span class="bp">self</span><span class="o">.</span><span class="n">definition_list_items</span><span class="p">:</span> <span class="n">List</span><span class="p">[</span><span class="n">Tuple</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="nb">str</span><span class="p">]]</span> <span class="o">=</span> <span class="p">[]</span>
+        <span class="bp">self</span><span class="o">.</span><span class="n">definition_list_items</span><span class="p">:</span> <span class="nb">list</span><span class="p">[</span><span class="nb">tuple</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="nb">str</span><span class="p">]]</span> <span class="o">=</span> <span class="p">[]</span>
@@ -1111,3 +1111,3 @@
-        <span class="bp">self</span><span class="o">.</span><span class="n">_saved_body_stack</span><span class="p">:</span> <span class="n">List</span><span class="p">[</span><span class="n">List</span><span class="p">[</span><span class="n">Any</span><span class="p">]]</span> <span class="o">=</span> <span class="p">[]</span>
-        <span class="bp">self</span><span class="o">.</span><span class="n">_deflist_items_stack</span><span class="p">:</span> <span class="n">List</span><span class="p">[</span><span class="n">List</span><span class="p">[</span><span class="n">Tuple</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="nb">str</span><span class="p">]]]</span> <span class="o">=</span> <span class="p">[]</span>
-        <span class="bp">self</span><span class="o">.</span><span class="n">_pending_term_stack</span><span class="p">:</span> <span class="n">List</span><span class="p">[</span><span class="nb">str</span> <span class="o">|</span> <span class="kc">None</span><span class="p">]</span> <span class="o">=</span> <span class="p">[]</span>
+        <span class="bp">self</span><span class="o">.</span><span class="n">_saved_body_stack</span><span class="p">:</span> <span class="nb">list</span><span class="p">[</span><span class="nb">list</span><span class="p">[</span><span class="n">Any</span><span class="p">]]</span> <span class="o">=</span> <span class="p">[]</span>
+        <span class="bp">self</span><span class="o">.</span><span class="n">_deflist_items_stack</span><span class="p">:</span> <span class="nb">list</span><span class="p">[</span><span class="nb">list</span><span class="p">[</span><span class="nb">tuple</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="nb">str</span><span class="p">]]]</span> <span class="o">=</span> <span class="p">[]</span>
+        <span class="bp">self</span><span class="o">.</span><span class="n">_pending_term_stack</span><span class="p">:</span> <span class="nb">list</span><span class="p">[</span><span class="nb">str</span> <span class="o">|</span> <span class="kc">None</span><span class="p">]</span> <span class="o">=</span> <span class="p">[]</span>
@@ -1122 +1122 @@
-        <span class="bp">self</span><span class="o">.</span><span class="n">_saved_body_for_admonition_title</span><span class="p">:</span> <span class="n">List</span><span class="p">[</span><span class="n">Any</span><span class="p">]</span> <span class="o">|</span> <span class="kc">None</span> <span class="o">=</span> <span class="p">(</span>
+        <span class="bp">self</span><span class="o">.</span><span class="n">_saved_body_for_admonition_title</span><span class="p">:</span> <span class="nb">list</span><span class="p">[</span><span class="n">Any</span><span class="p">]</span> <span class="o">|</span> <span class="kc">None</span> <span class="o">=</span> <span class="p">(</span>
@@ -1133 +1133 @@
-        <span class="bp">self</span><span class="o">.</span><span class="n">_title_section_ids</span><span class="p">:</span> <span class="n">List</span><span class="p">[</span><span class="nb">str</span><span class="p">]</span> <span class="o">=</span> <span class="p">(</span>
+        <span class="bp">self</span><span class="o">.</span><span class="n">_title_section_ids</span><span class="p">:</span> <span class="nb">list</span><span class="p">[</span><span class="nb">str</span><span class="p">]</span> <span class="o">=</span> <span class="p">(</span>
@@ -1160 +1160 @@
-        <span class="bp">self</span><span class="o">.</span><span class="n">_toctree_entry_occurrences</span><span class="p">:</span> <span class="n">Dict</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="nb">int</span><span class="p">]</span> <span class="o">=</span> <span class="p">{}</span>
+        <span class="bp">self</span><span class="o">.</span><span class="n">_toctree_entry_occurrences</span><span class="p">:</span> <span class="nb">dict</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="nb">int</span><span class="p">]</span> <span class="o">=</span> <span class="p">{}</span>
@@ -1978 +1978 @@
-    <span class="n">_CONCAT_CONTEXTS</span><span class="p">:</span> <span class="n">Tuple</span><span class="p">[</span><span class="n">Tuple</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="nb">str</span><span class="p">],</span> <span class="o">...</span><span class="p">]</span> <span class="o">=</span> <span class="p">(</span>
+    <span class="n">_CONCAT_CONTEXTS</span><span class="p">:</span> <span class="nb">tuple</span><span class="p">[</span><span class="nb">tuple</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="nb">str</span><span class="p">],</span> <span class="o">...</span><span class="p">]</span> <span class="o">=</span> <span class="p">(</span>
@@ -1986 +1986 @@
-    <span class="k">def</span><span class="w"> </span><span class="nf">_inline_concat_context</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span> <span class="o">-&gt;</span> <span class="n">Tuple</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="nb">str</span><span class="p">]</span> <span class="o">|</span> <span class="kc">None</span><span class="p">:</span>
+    <span class="k">def</span><span class="w"> </span><span class="nf">_inline_concat_context</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span> <span class="o">-&gt;</span> <span class="nb">tuple</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="nb">str</span><span class="p">]</span> <span class="o">|</span> <span class="kc">None</span><span class="p">:</span>
@@ -5845 +5845 @@
-    <span class="k">def</span><span class="w"> </span><span class="nf">_resolve_xref_docname</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span> <span class="n">refuri</span><span class="p">:</span> <span class="nb">str</span><span class="p">)</span> <span class="o">-&gt;</span> <span class="n">Tuple</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="nb">str</span><span class="p">]</span> <span class="o">|</span> <span class="kc">None</span><span class="p">:</span>
+    <span class="k">def</span><span class="w"> </span><span class="nf">_resolve_xref_docname</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span> <span class="n">refuri</span><span class="p">:</span> <span class="nb">str</span><span class="p">)</span> <span class="o">-&gt;</span> <span class="nb">tuple</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="nb">str</span><span class="p">]</span> <span class="o">|</span> <span class="kc">None</span><span class="p">:</span>
~~~

### html: _modules/typsphinx/writer.html

~~~diff
--- /tmp/tmp.SH3zNIS9sZ/A/html/_modules/typsphinx/writer.html	2026-09-13 14:41:35.725411397 +0900
+++ /tmp/tmp.SH3zNIS9sZ/C/html/_modules/typsphinx/writer.html	2026-09-13 14:42:21.396188049 +0900
@@ -277 +277 @@
-<span class="kn">from</span><span class="w"> </span><span class="nn">typing</span><span class="w"> </span><span class="kn">import</span> <span class="n">Any</span><span class="p">,</span> <span class="n">Tuple</span>
+<span class="kn">from</span><span class="w"> </span><span class="nn">typing</span><span class="w"> </span><span class="kn">import</span> <span class="n">Any</span>
@@ -564 +564 @@
-        <span class="n">edge_keys</span><span class="p">:</span> <span class="n">Tuple</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="o">...</span><span class="p">]</span> <span class="o">=</span> <span class="p">(),</span>
+        <span class="n">edge_keys</span><span class="p">:</span> <span class="nb">tuple</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="o">...</span><span class="p">]</span> <span class="o">=</span> <span class="p">(),</span>
~~~

### html: api/index.html

~~~diff
--- /tmp/tmp.SH3zNIS9sZ/A/html/api/index.html	2026-09-13 14:41:35.005770694 +0900
+++ /tmp/tmp.SH3zNIS9sZ/C/html/api/index.html	2026-09-13 14:42:20.716285554 +0900
@@ -409 +409 @@
-<dd class="field-odd"><p><strong>docnames</strong> (<span class="sphinx_autodoc_typehints-type"><a class="reference external" href="https://docs.python.org/3/library/typing.html#typing.Set" title="(in Python v3.14)"><code class="xref py py-class docutils literal notranslate"><span class="pre">Set</span></code></a>[<a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#str" title="(in Python v3.14)"><code class="xref py py-class docutils literal notranslate"><span class="pre">str</span></code></a>]</span>) – Set of document names to be written</p>
+<dd class="field-odd"><p><strong>docnames</strong> (<span class="sphinx_autodoc_typehints-type"><a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#set" title="(in Python v3.14)"><code class="xref py py-class docutils literal notranslate"><span class="pre">set</span></code></a>[<a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#str" title="(in Python v3.14)"><code class="xref py py-class docutils literal notranslate"><span class="pre">str</span></code></a>]</span>) – Set of document names to be written</p>
@@ -428,2 +428,2 @@
-<li><p><strong>build_docnames</strong> (<span class="sphinx_autodoc_typehints-type"><a class="reference external" href="https://docs.python.org/3/library/typing.html#typing.Optional" title="(in Python v3.14)"><code class="xref py py-data docutils literal notranslate"><span class="pre">Optional</span></code></a>[<a class="reference external" href="https://docs.python.org/3/library/typing.html#typing.Set" title="(in Python v3.14)"><code class="xref py py-class docutils literal notranslate"><span class="pre">Set</span></code></a>[<a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#str" title="(in Python v3.14)"><code class="xref py py-class docutils literal notranslate"><span class="pre">str</span></code></a>]]</span>) – Document names to build (None = all)</p></li>
-<li><p><strong>updated_docnames</strong> (<span class="sphinx_autodoc_typehints-type"><a class="reference external" href="https://docs.python.org/3/library/typing.html#typing.Set" title="(in Python v3.14)"><code class="xref py py-class docutils literal notranslate"><span class="pre">Set</span></code></a>[<a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#str" title="(in Python v3.14)"><code class="xref py py-class docutils literal notranslate"><span class="pre">str</span></code></a>]</span>) – Document names that were updated</p></li>
+<li><p><strong>build_docnames</strong> (<span class="sphinx_autodoc_typehints-type"><a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#set" title="(in Python v3.14)"><code class="xref py py-class docutils literal notranslate"><span class="pre">set</span></code></a>[<a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#str" title="(in Python v3.14)"><code class="xref py py-class docutils literal notranslate"><span class="pre">str</span></code></a>] | <a class="reference external" href="https://docs.python.org/3/library/constants.html#None" title="(in Python v3.14)"><code class="xref py py-obj docutils literal notranslate"><span class="pre">None</span></code></a></span>) – Document names to build (None = all)</p></li>
+<li><p><strong>updated_docnames</strong> (<span class="sphinx_autodoc_typehints-type"><a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#set" title="(in Python v3.14)"><code class="xref py py-class docutils literal notranslate"><span class="pre">set</span></code></a>[<a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#str" title="(in Python v3.14)"><code class="xref py py-class docutils literal notranslate"><span class="pre">str</span></code></a>]</span>) – Document names that were updated</p></li>
@@ -905 +905 @@
-<li><p><strong>edge_keys</strong> (<span class="sphinx_autodoc_typehints-type"><a class="reference external" href="https://docs.python.org/3/library/typing.html#typing.Tuple" title="(in Python v3.14)"><code class="xref py py-data docutils literal notranslate"><span class="pre">Tuple</span></code></a>[<a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#str" title="(in Python v3.14)"><code class="xref py py-class docutils literal notranslate"><span class="pre">str</span></code></a>, <a class="reference external" href="https://docs.python.org/3/library/constants.html#Ellipsis" title="(in Python v3.14)"><code class="xref py py-data docutils literal notranslate"><span class="pre">...</span></code></a>]</span>) – This master’s own derived edge keys, in discovery
+<li><p><strong>edge_keys</strong> (<span class="sphinx_autodoc_typehints-type"><a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#tuple" title="(in Python v3.14)"><code class="xref py py-class docutils literal notranslate"><span class="pre">tuple</span></code></a>[<a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#str" title="(in Python v3.14)"><code class="xref py py-class docutils literal notranslate"><span class="pre">str</span></code></a>, <a class="reference external" href="https://docs.python.org/3/library/constants.html#Ellipsis" title="(in Python v3.14)"><code class="xref py py-data docutils literal notranslate"><span class="pre">...</span></code></a>]</span>) – This master’s own derived edge keys, in discovery
@@ -1067 +1067 @@
-<li><p><strong>toctree_includes</strong> (<span class="sphinx_autodoc_typehints-type"><a class="reference external" href="https://docs.python.org/3/library/typing.html#typing.Dict" title="(in Python v3.14)"><code class="xref py py-class docutils literal notranslate"><span class="pre">Dict</span></code></a>[<a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#str" title="(in Python v3.14)"><code class="xref py py-class docutils literal notranslate"><span class="pre">str</span></code></a>, <a class="reference external" href="https://docs.python.org/3/library/typing.html#typing.List" title="(in Python v3.14)"><code class="xref py py-class docutils literal notranslate"><span class="pre">List</span></code></a>[<a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#str" title="(in Python v3.14)"><code class="xref py py-class docutils literal notranslate"><span class="pre">str</span></code></a>]]</span>) – A mapping from docname to its ordered
+<li><p><strong>toctree_includes</strong> (<span class="sphinx_autodoc_typehints-type"><a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#dict" title="(in Python v3.14)"><code class="xref py py-class docutils literal notranslate"><span class="pre">dict</span></code></a>[<a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#str" title="(in Python v3.14)"><code class="xref py py-class docutils literal notranslate"><span class="pre">str</span></code></a>, <a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#list" title="(in Python v3.14)"><code class="xref py py-class docutils literal notranslate"><span class="pre">list</span></code></a>[<a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#str" title="(in Python v3.14)"><code class="xref py py-class docutils literal notranslate"><span class="pre">str</span></code></a>]]</span>) – A mapping from docname to its ordered
@@ -1076 +1076 @@
-<dd class="field-even"><p><span class="sphinx_autodoc_typehints-type"><a class="reference external" href="https://docs.python.org/3/library/typing.html#typing.Tuple" title="(in Python v3.14)"><code class="xref py py-data docutils literal notranslate"><span class="pre">Tuple</span></code></a>[<a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#str" title="(in Python v3.14)"><code class="xref py py-class docutils literal notranslate"><span class="pre">str</span></code></a>, <a class="reference external" href="https://docs.python.org/3/library/constants.html#Ellipsis" title="(in Python v3.14)"><code class="xref py py-data docutils literal notranslate"><span class="pre">...</span></code></a>]</span></p>
+<dd class="field-even"><p><span class="sphinx_autodoc_typehints-type"><a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#tuple" title="(in Python v3.14)"><code class="xref py py-class docutils literal notranslate"><span class="pre">tuple</span></code></a>[<a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#str" title="(in Python v3.14)"><code class="xref py py-class docutils literal notranslate"><span class="pre">str</span></code></a>, <a class="reference external" href="https://docs.python.org/3/library/constants.html#Ellipsis" title="(in Python v3.14)"><code class="xref py py-data docutils literal notranslate"><span class="pre">...</span></code></a>]</span></p>
@@ -1109 +1109 @@
-<dd class="field-odd"><p><strong>edge_keys</strong> (<span class="sphinx_autodoc_typehints-type"><a class="reference external" href="https://docs.python.org/3/library/typing.html#typing.Tuple" title="(in Python v3.14)"><code class="xref py py-data docutils literal notranslate"><span class="pre">Tuple</span></code></a>[<a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#str" title="(in Python v3.14)"><code class="xref py py-class docutils literal notranslate"><span class="pre">str</span></code></a>, <a class="reference external" href="https://docs.python.org/3/library/constants.html#Ellipsis" title="(in Python v3.14)"><code class="xref py py-data docutils literal notranslate"><span class="pre">...</span></code></a>]</span>) – The master’s own edge keys, in discovery order (the
+<dd class="field-odd"><p><strong>edge_keys</strong> (<span class="sphinx_autodoc_typehints-type"><a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#tuple" title="(in Python v3.14)"><code class="xref py py-class docutils literal notranslate"><span class="pre">tuple</span></code></a>[<a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#str" title="(in Python v3.14)"><code class="xref py py-class docutils literal notranslate"><span class="pre">str</span></code></a>, <a class="reference external" href="https://docs.python.org/3/library/constants.html#Ellipsis" title="(in Python v3.14)"><code class="xref py py-data docutils literal notranslate"><span class="pre">...</span></code></a>]</span>) – The master’s own edge keys, in discovery order (the
@@ -5228,2 +5228,2 @@
-<li><p><strong>search_paths</strong> (<a class="reference external" href="https://docs.python.org/3/library/typing.html#typing.List" title="(in Python v3.14)"><em>List</em></a><em>[</em><a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#str" title="(in Python v3.14)"><em>str</em></a><em>] </em><em>| </em><em>None</em>)</p></li>
-<li><p><strong>parameter_mapping</strong> (<a class="reference external" href="https://docs.python.org/3/library/typing.html#typing.Dict" title="(in Python v3.14)"><em>Dict</em></a><em>[</em><a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#str" title="(in Python v3.14)"><em>str</em></a><em>, </em><a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#str" title="(in Python v3.14)"><em>str</em></a><em>] </em><em>| </em><em>None</em>)</p></li>
+<li><p><strong>search_paths</strong> (<a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#list" title="(in Python v3.14)"><em>list</em></a><em>[</em><a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#str" title="(in Python v3.14)"><em>str</em></a><em>] </em><em>| </em><em>None</em>)</p></li>
+<li><p><strong>parameter_mapping</strong> (<a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#dict" title="(in Python v3.14)"><em>dict</em></a><em>[</em><a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#str" title="(in Python v3.14)"><em>str</em></a><em>, </em><a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#str" title="(in Python v3.14)"><em>str</em></a><em>] </em><em>| </em><em>None</em>)</p></li>
@@ -5232 +5232 @@
-<li><p><strong>typst_package_imports</strong> (<a class="reference external" href="https://docs.python.org/3/library/typing.html#typing.List" title="(in Python v3.14)"><em>List</em></a><em>[</em><a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#str" title="(in Python v3.14)"><em>str</em></a><em>] </em><em>| </em><em>None</em>)</p></li>
+<li><p><strong>typst_package_imports</strong> (<a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#list" title="(in Python v3.14)"><em>list</em></a><em>[</em><a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#str" title="(in Python v3.14)"><em>str</em></a><em>] </em><em>| </em><em>None</em>)</p></li>
@@ -5371 +5371 @@
-<li><p><strong>sphinx_metadata</strong> (<span class="sphinx_autodoc_typehints-type"><a class="reference external" href="https://docs.python.org/3/library/typing.html#typing.Dict" title="(in Python v3.14)"><code class="xref py py-class docutils literal notranslate"><span class="pre">Dict</span></code></a>[<a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#str" title="(in Python v3.14)"><code class="xref py py-class docutils literal notranslate"><span class="pre">str</span></code></a>, <a class="reference external" href="https://docs.python.org/3/library/typing.html#typing.Any" title="(in Python v3.14)"><code class="xref py py-data docutils literal notranslate"><span class="pre">Any</span></code></a>]</span>) – Dictionary of Sphinx configuration metadata
+<li><p><strong>sphinx_metadata</strong> (<span class="sphinx_autodoc_typehints-type"><a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#dict" title="(in Python v3.14)"><code class="xref py py-class docutils literal notranslate"><span class="pre">dict</span></code></a>[<a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#str" title="(in Python v3.14)"><code class="xref py py-class docutils literal notranslate"><span class="pre">str</span></code></a>, <a class="reference external" href="https://docs.python.org/3/library/typing.html#typing.Any" title="(in Python v3.14)"><code class="xref py py-data docutils literal notranslate"><span class="pre">Any</span></code></a>]</span>) – Dictionary of Sphinx configuration metadata
@@ -5373 +5373 @@
-<li><p><strong>typst_elements</strong> (<span class="sphinx_autodoc_typehints-type"><a class="reference external" href="https://docs.python.org/3/library/typing.html#typing.Optional" title="(in Python v3.14)"><code class="xref py py-data docutils literal notranslate"><span class="pre">Optional</span></code></a>[<a class="reference external" href="https://docs.python.org/3/library/typing.html#typing.Dict" title="(in Python v3.14)"><code class="xref py py-class docutils literal notranslate"><span class="pre">Dict</span></code></a>[<a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#str" title="(in Python v3.14)"><code class="xref py py-class docutils literal notranslate"><span class="pre">str</span></code></a>, <a class="reference external" href="https://docs.python.org/3/library/typing.html#typing.Any" title="(in Python v3.14)"><code class="xref py py-data docutils literal notranslate"><span class="pre">Any</span></code></a>]]</span>) – CONF-04 curated pass-through values (e.g.
+<li><p><strong>typst_elements</strong> (<span class="sphinx_autodoc_typehints-type"><a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#dict" title="(in Python v3.14)"><code class="xref py py-class docutils literal notranslate"><span class="pre">dict</span></code></a>[<a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#str" title="(in Python v3.14)"><code class="xref py py-class docutils literal notranslate"><span class="pre">str</span></code></a>, <a class="reference external" href="https://docs.python.org/3/library/typing.html#typing.Any" title="(in Python v3.14)"><code class="xref py py-data docutils literal notranslate"><span class="pre">Any</span></code></a>] | <a class="reference external" href="https://docs.python.org/3/library/constants.html#None" title="(in Python v3.14)"><code class="xref py py-obj docutils literal notranslate"><span class="pre">None</span></code></a></span>) – CONF-04 curated pass-through values (e.g.
@@ -5384 +5384 @@
-<dd class="field-even"><p><span class="sphinx_autodoc_typehints-type"><a class="reference external" href="https://docs.python.org/3/library/typing.html#typing.Dict" title="(in Python v3.14)"><code class="xref py py-class docutils literal notranslate"><span class="pre">Dict</span></code></a>[<a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#str" title="(in Python v3.14)"><code class="xref py py-class docutils literal notranslate"><span class="pre">str</span></code></a>, <a class="reference external" href="https://docs.python.org/3/library/typing.html#typing.Any" title="(in Python v3.14)"><code class="xref py py-data docutils literal notranslate"><span class="pre">Any</span></code></a>]</span></p>
+<dd class="field-even"><p><span class="sphinx_autodoc_typehints-type"><a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#dict" title="(in Python v3.14)"><code class="xref py py-class docutils literal notranslate"><span class="pre">dict</span></code></a>[<a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#str" title="(in Python v3.14)"><code class="xref py py-class docutils literal notranslate"><span class="pre">str</span></code></a>, <a class="reference external" href="https://docs.python.org/3/library/typing.html#typing.Any" title="(in Python v3.14)"><code class="xref py py-data docutils literal notranslate"><span class="pre">Any</span></code></a>]</span></p>
@@ -5401,2 +5401,2 @@
-<li><p><strong>sphinx_metadata</strong> (<a class="reference external" href="https://docs.python.org/3/library/typing.html#typing.Dict" title="(in Python v3.14)"><em>Dict</em></a><em>[</em><a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#str" title="(in Python v3.14)"><em>str</em></a><em>, </em><a class="reference external" href="https://docs.python.org/3/library/typing.html#typing.Any" title="(in Python v3.14)"><em>Any</em></a><em>]</em>)</p></li>
-<li><p><strong>typst_elements</strong> (<a class="reference external" href="https://docs.python.org/3/library/typing.html#typing.Dict" title="(in Python v3.14)"><em>Dict</em></a><em>[</em><a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#str" title="(in Python v3.14)"><em>str</em></a><em>, </em><a class="reference external" href="https://docs.python.org/3/library/typing.html#typing.Any" title="(in Python v3.14)"><em>Any</em></a><em>] </em><em>| </em><em>None</em>)</p></li>
+<li><p><strong>sphinx_metadata</strong> (<a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#dict" title="(in Python v3.14)"><em>dict</em></a><em>[</em><a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#str" title="(in Python v3.14)"><em>str</em></a><em>, </em><a class="reference external" href="https://docs.python.org/3/library/typing.html#typing.Any" title="(in Python v3.14)"><em>Any</em></a><em>]</em>)</p></li>
+<li><p><strong>typst_elements</strong> (<a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#dict" title="(in Python v3.14)"><em>dict</em></a><em>[</em><a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#str" title="(in Python v3.14)"><em>str</em></a><em>, </em><a class="reference external" href="https://docs.python.org/3/library/typing.html#typing.Any" title="(in Python v3.14)"><em>Any</em></a><em>] </em><em>| </em><em>None</em>)</p></li>
@@ -5406 +5406 @@
-<dd class="field-odd"><p><a class="reference external" href="https://docs.python.org/3/library/typing.html#typing.Dict" title="(in Python v3.14)"><em>Dict</em></a>[<a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#str" title="(in Python v3.14)">str</a>, <a class="reference external" href="https://docs.python.org/3/library/typing.html#typing.Any" title="(in Python v3.14)"><em>Any</em></a>]</p>
+<dd class="field-odd"><p><a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#dict" title="(in Python v3.14)">dict</a>[<a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#str" title="(in Python v3.14)">str</a>, <a class="reference external" href="https://docs.python.org/3/library/typing.html#typing.Any" title="(in Python v3.14)"><em>Any</em></a>]</p>
@@ -5435 +5435 @@
-<dd class="field-even"><p><span class="sphinx_autodoc_typehints-type"><a class="reference external" href="https://docs.python.org/3/library/typing.html#typing.Dict" title="(in Python v3.14)"><code class="xref py py-class docutils literal notranslate"><span class="pre">Dict</span></code></a>[<a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#str" title="(in Python v3.14)"><code class="xref py py-class docutils literal notranslate"><span class="pre">str</span></code></a>, <a class="reference external" href="https://docs.python.org/3/library/typing.html#typing.Any" title="(in Python v3.14)"><code class="xref py py-data docutils literal notranslate"><span class="pre">Any</span></code></a>]</span></p>
+<dd class="field-even"><p><span class="sphinx_autodoc_typehints-type"><a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#dict" title="(in Python v3.14)"><code class="xref py py-class docutils literal notranslate"><span class="pre">dict</span></code></a>[<a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#str" title="(in Python v3.14)"><code class="xref py py-class docutils literal notranslate"><span class="pre">str</span></code></a>, <a class="reference external" href="https://docs.python.org/3/library/typing.html#typing.Any" title="(in Python v3.14)"><code class="xref py py-data docutils literal notranslate"><span class="pre">Any</span></code></a>]</span></p>
@@ -5470 +5470 @@
-<li><p><strong>params</strong> (<span class="sphinx_autodoc_typehints-type"><a class="reference external" href="https://docs.python.org/3/library/typing.html#typing.Dict" title="(in Python v3.14)"><code class="xref py py-class docutils literal notranslate"><span class="pre">Dict</span></code></a>[<a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#str" title="(in Python v3.14)"><code class="xref py py-class docutils literal notranslate"><span class="pre">str</span></code></a>, <a class="reference external" href="https://docs.python.org/3/library/typing.html#typing.Any" title="(in Python v3.14)"><code class="xref py py-data docutils literal notranslate"><span class="pre">Any</span></code></a>]</span>) – Template parameters (title, authors, etc.)</p></li>
+<li><p><strong>params</strong> (<span class="sphinx_autodoc_typehints-type"><a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#dict" title="(in Python v3.14)"><code class="xref py py-class docutils literal notranslate"><span class="pre">dict</span></code></a>[<a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#str" title="(in Python v3.14)"><code class="xref py py-class docutils literal notranslate"><span class="pre">str</span></code></a>, <a class="reference external" href="https://docs.python.org/3/library/typing.html#typing.Any" title="(in Python v3.14)"><code class="xref py py-data docutils literal notranslate"><span class="pre">Any</span></code></a>]</span>) – Template parameters (title, authors, etc.)</p></li>
~~~

### typ: api/index.typ

~~~diff
--- /tmp/tmp.SH3zNIS9sZ/A/pdf/api/index.typ	2026-09-13 14:41:41.019911806 +0900
+++ /tmp/tmp.SH3zNIS9sZ/C/pdf/api/index.typ	2026-09-13 14:42:27.382687536 +0900
@@ -225 +225 @@
-strong(raw("docnames")) + text(" (") + link("https://docs.python.org/3/library/typing.html#typing.Set", raw("Set")) + text("[") + link("https://docs.python.org/3/library/stdtypes.html#str", raw("str")) + text("]") + text(")") + text(" – ") + text("Set of document names to be written")
+strong(raw("docnames")) + text(" (") + link("https://docs.python.org/3/library/stdtypes.html#set", raw("set")) + text("[") + link("https://docs.python.org/3/library/stdtypes.html#str", raw("str")) + text("]") + text(")") + text(" – ") + text("Set of document names to be written")
@@ -248,3 +248 @@
-link("https://docs.python.org/3/library/typing.html#typing.Optional", raw("Optional"))
-text("[")
-link("https://docs.python.org/3/library/typing.html#typing.Set", raw("Set"))
+link("https://docs.python.org/3/library/stdtypes.html#set", raw("set"))
@@ -253 +251,2 @@
-text("]]")
+text("] | ")
+link("https://docs.python.org/3/library/constants.html#None", raw("None"))
@@ -262 +261 @@
-link("https://docs.python.org/3/library/typing.html#typing.Set", raw("Set"))
+link("https://docs.python.org/3/library/stdtypes.html#set", raw("set"))
@@ -981 +980 @@
-link("https://docs.python.org/3/library/typing.html#typing.Tuple", raw("Tuple"))
+link("https://docs.python.org/3/library/stdtypes.html#tuple", raw("tuple"))
@@ -1187 +1186 @@
-link("https://docs.python.org/3/library/typing.html#typing.Dict", raw("Dict"))
+link("https://docs.python.org/3/library/stdtypes.html#dict", raw("dict"))
@@ -1191 +1190 @@
-link("https://docs.python.org/3/library/typing.html#typing.List", raw("List"))
+link("https://docs.python.org/3/library/stdtypes.html#list", raw("list"))
@@ -1213 +1212 @@
-link("https://docs.python.org/3/library/typing.html#typing.Tuple", raw("Tuple")) + text("[") + link("https://docs.python.org/3/library/stdtypes.html#str", raw("str")) + text(", ") + link("https://docs.python.org/3/library/constants.html#Ellipsis", raw("...")) + text("]")
+link("https://docs.python.org/3/library/stdtypes.html#tuple", raw("tuple")) + text("[") + link("https://docs.python.org/3/library/stdtypes.html#str", raw("str")) + text(", ") + link("https://docs.python.org/3/library/constants.html#Ellipsis", raw("...")) + text("]")
@@ -1256 +1255 @@
-strong(raw("edge_keys")) + text(" (") + link("https://docs.python.org/3/library/typing.html#typing.Tuple", raw("Tuple")) + text("[") + link("https://docs.python.org/3/library/stdtypes.html#str", raw("str")) + text(", ") + link("https://docs.python.org/3/library/constants.html#Ellipsis", raw("...")) + text("]") + text(")") + text(" – ") + text("The master’s own edge keys, in discovery order (the return value of ") + raw("derive_master_edge_keys()") + text(").")
+strong(raw("edge_keys")) + text(" (") + link("https://docs.python.org/3/library/stdtypes.html#tuple", raw("tuple")) + text("[") + link("https://docs.python.org/3/library/stdtypes.html#str", raw("str")) + text(", ") + link("https://docs.python.org/3/library/constants.html#Ellipsis", raw("...")) + text("]") + text(")") + text(" – ") + text("The master’s own edge keys, in discovery order (the return value of ") + raw("derive_master_edge_keys()") + text(").")
@@ -5618 +5617 @@
-link("https://docs.python.org/3/library/typing.html#typing.List", emph(raw("List")))
+link("https://docs.python.org/3/library/stdtypes.html#list", emph(raw("list")))
@@ -5630 +5629 @@
-link("https://docs.python.org/3/library/typing.html#typing.Dict", emph(raw("Dict")))
+link("https://docs.python.org/3/library/stdtypes.html#dict", emph(raw("dict")))
@@ -5662 +5661 @@
-link("https://docs.python.org/3/library/typing.html#typing.List", emph(raw("List")))
+link("https://docs.python.org/3/library/stdtypes.html#list", emph(raw("list")))
@@ -5858 +5857 @@
-link("https://docs.python.org/3/library/typing.html#typing.Dict", raw("Dict"))
+link("https://docs.python.org/3/library/stdtypes.html#dict", raw("dict"))
@@ -5872,3 +5871 @@
-link("https://docs.python.org/3/library/typing.html#typing.Optional", raw("Optional"))
-text("[")
-link("https://docs.python.org/3/library/typing.html#typing.Dict", raw("Dict"))
+link("https://docs.python.org/3/library/stdtypes.html#dict", raw("dict"))
@@ -5879 +5876,2 @@
-text("]]")
+text("] | ")
+link("https://docs.python.org/3/library/constants.html#None", raw("None"))
@@ -5899 +5897 @@
-link("https://docs.python.org/3/library/typing.html#typing.Dict", raw("Dict")) + text("[") + link("https://docs.python.org/3/library/stdtypes.html#str", raw("str")) + text(", ") + link("https://docs.python.org/3/library/typing.html#typing.Any", raw("Any")) + text("]")
+link("https://docs.python.org/3/library/stdtypes.html#dict", raw("dict")) + text("[") + link("https://docs.python.org/3/library/stdtypes.html#str", raw("str")) + text(", ") + link("https://docs.python.org/3/library/typing.html#typing.Any", raw("Any")) + text("]")
@@ -5917 +5915 @@
-link("https://docs.python.org/3/library/typing.html#typing.Dict", emph(raw("Dict")))
+link("https://docs.python.org/3/library/stdtypes.html#dict", emph(raw("dict")))
@@ -5929 +5927 @@
-link("https://docs.python.org/3/library/typing.html#typing.Dict", emph(raw("Dict")))
+link("https://docs.python.org/3/library/stdtypes.html#dict", emph(raw("dict")))
@@ -5942 +5940 @@
-link("https://docs.python.org/3/library/typing.html#typing.Dict", emph({text("Dict")})) + text("[") + link("https://docs.python.org/3/library/stdtypes.html#str", text("str")) + text(", ") + link("https://docs.python.org/3/library/typing.html#typing.Any", emph({text("Any")})) + text("]")
+link("https://docs.python.org/3/library/stdtypes.html#dict", text("dict")) + text("[") + link("https://docs.python.org/3/library/stdtypes.html#str", text("str")) + text(", ") + link("https://docs.python.org/3/library/typing.html#typing.Any", emph({text("Any")})) + text("]")
@@ -5972 +5970 @@
-link("https://docs.python.org/3/library/typing.html#typing.Dict", raw("Dict")) + text("[") + link("https://docs.python.org/3/library/stdtypes.html#str", raw("str")) + text(", ") + link("https://docs.python.org/3/library/typing.html#typing.Any", raw("Any")) + text("]")
+link("https://docs.python.org/3/library/stdtypes.html#dict", raw("dict")) + text("[") + link("https://docs.python.org/3/library/stdtypes.html#str", raw("str")) + text(", ") + link("https://docs.python.org/3/library/typing.html#typing.Any", raw("Any")) + text("]")
@@ -6009 +6007 @@
-link("https://docs.python.org/3/library/typing.html#typing.Dict", raw("Dict"))
+link("https://docs.python.org/3/library/stdtypes.html#dict", raw("dict"))
~~~

DOCS_HTML_HUNKS = 62
DOCS_TYP_HUNKS = 21

## D-11 classification

| id | output | file | base lines | before | after | traces to | class |
|----|--------|------|------------|--------|-------|-----------|-------|
| H-001 | html | _modules/typsphinx/builder.html | 280 | from typing import Any, Dict, List, Set, Tuple | from typing import Any | typsphinx/builder.py:13 (import line) | TRACED |
| H-002 | html | _modules/typsphinx/builder.html | 1007 | Dict[str, Tuple[str, ...]] | dict[str, tuple[str, ...]] | typsphinx/builder.py:736 (`_master_include_edges` annotation) | TRACED |
| H-003 | html | _modules/typsphinx/builder.html | 1017 | Dict[str, TemplateRegistryEntry] | dict[str, TemplateRegistryEntry] | typsphinx/builder.py:746 (`_document_template_registry` annotation) | TRACED |
| H-004 | html | _modules/typsphinx/builder.html | 1032 | -> Dict[str, Tuple[str, ...]]: | -> dict[str, tuple[str, ...]]: | typsphinx/builder.py:760 (`_build_include_edge_map` return annotation) | TRACED |
| H-005 | html | _modules/typsphinx/builder.html | 1069 | Dict[str, Tuple[str, ...]] | dict[str, tuple[str, ...]] | typsphinx/builder.py:797 (`edge_map` annotation) | TRACED |
| H-006 | html | _modules/typsphinx/builder.html | 1405,2 | claims: Dict[str, str]; failures: List[Tuple[str, str]] | claims: dict[str, str]; failures: list[tuple[str, str]] | typsphinx/builder.py:1133-1134 (`claims`/`failures` annotations) | TRACED |
| H-007 | html | _modules/typsphinx/builder.html | 1730 | Set[str] | set[str] | typsphinx/builder.py:1458 (`used_keys` annotation) | TRACED |
| H-008 | html | _modules/typsphinx/builder.html | 1740 | List[Tuple[str, str]] | list[tuple[str, str]] | typsphinx/builder.py:1468 (`templates_path_entries` annotation) | TRACED |
| H-009 | html | _modules/typsphinx/builder.html | 1748 | List[Tuple[str, str]] | list[tuple[str, str]] | typsphinx/builder.py:1476 (`failures` annotation) | TRACED |
| H-010 | html | _modules/typsphinx/builder.html | 1918 | docnames: Set[str] | docnames: set[str] | typsphinx/builder.py:1638 (`prepare_writing` param annotation) | TRACED |
| H-011 | html | _modules/typsphinx/builder.html | 1939,2 | build_docnames: Set[str] \| None; updated_docnames: Set[str] | build_docnames: set[str] \| None; updated_docnames: set[str] | typsphinx/builder.py:1656-1657 (`build_docnames`/`updated_docnames` params) | TRACED |
| H-012 | html | _modules/typsphinx/builder.html | 2647,3 | destinations: Dict[...]; failures: List[...]; to_copy: List[...] | destinations: dict[...]; failures: list[...]; to_copy: list[...] | typsphinx/builder.py:2354-2356 (annotations) | TRACED |
| H-013 | html | _modules/typsphinx/builder.html | 2853 | failures: List[Tuple[str, str]] | failures: list[tuple[str, str]] | typsphinx/builder.py:2552 (`failures` annotation) | TRACED |
| H-014 | html | _modules/typsphinx/template_engine.html | 280 | from typing import Any, Dict, List | from typing import Any | typsphinx/template_engine.py:13 (import line) | TRACED |
| H-015 | html | _modules/typsphinx/template_engine.html | 383 | ELEMENTS_ALLOWLIST: Dict[str, str] | ELEMENTS_ALLOWLIST: dict[str, str] | typsphinx/template_engine.py:110 (module constant annotation) | TRACED |
| H-016 | html | _modules/typsphinx/template_engine.html | 546,2 | search_paths: List[str] \| None; parameter_mapping: Dict[str, str] \| None | search_paths: list[str] \| None; parameter_mapping: dict[str, str] \| None | typsphinx/template_engine.py:262-263 (params) | TRACED |
| H-017 | html | _modules/typsphinx/template_engine.html | 550 | typst_package_imports: List[str] \| None | typst_package_imports: list[str] \| None | typsphinx/template_engine.py:266 (param) | TRACED |
| H-018 | html | _modules/typsphinx/template_engine.html | 766,3 | sphinx_metadata: Dict[str, Any]; typst_elements: Dict[str, Any] \| None; -> Dict[str, Any]: | sphinx_metadata: dict[str, Any]; typst_elements: dict[str, Any] \| None; -> dict[str, Any]: | typsphinx/template_engine.py:468-470 (`map_parameters` params/return) | TRACED |
| H-019 | html | _modules/typsphinx/template_engine.html | 803 | params: Dict[str, Any] | params: dict[str, Any] | typsphinx/template_engine.py:505 (`params` annotation) | TRACED |
| H-020 | html | _modules/typsphinx/template_engine.html | 908 | -> Dict[str, Any]: | -> dict[str, Any]: | typsphinx/template_engine.py:604 (`extract_toctree_options` return) | TRACED |
| H-021 | html | _modules/typsphinx/template_engine.html | 975 | params: Dict[str, Any] | params: dict[str, Any] | typsphinx/template_engine.py:665 (`render` param) | TRACED |
| H-022 | html | _modules/typsphinx/translator.html | 276 | from typing import Any, Dict, List, NamedTuple, Tuple | from typing import Any, NamedTuple | typsphinx/translator.py:9 (import line) | TRACED |
| H-023 | html | _modules/typsphinx/translator.html | 393 | xref: Tuple[str, str] \| None | xref: tuple[str, str] \| None | typsphinx/translator.py:126 (`xref` field annotation) | TRACED |
| H-024 | html | _modules/typsphinx/translator.html | 619,2 | toctree_includes: Dict[str, List[str]]; -> Tuple[str, ...]: | toctree_includes: dict[str, list[str]]; -> tuple[str, ...]: | typsphinx/translator.py:344-345 (params/return) | TRACED |
| H-025 | html | _modules/typsphinx/translator.html | 685,2 | traversed: List[str]; edge_keys: List[str] | traversed: list[str]; edge_keys: list[str] | typsphinx/translator.py:410-411 (annotations) | TRACED |
| H-026 | html | _modules/typsphinx/translator.html | 688 | path: Tuple[str, ...] | path: tuple[str, ...] | typsphinx/translator.py:413 (`walk` nested-function param) | TRACED |
| H-027 | html | _modules/typsphinx/translator.html | 711 | edge_keys: Tuple[str, ...] | edge_keys: tuple[str, ...] | typsphinx/translator.py:433 (`render_include_edge_state` param) | TRACED |
| H-028 | html | _modules/typsphinx/translator.html | 818 | table_colwidths: List[Any] | table_colwidths: list[Any] | typsphinx/translator.py:534 (annotation) | TRACED |
| H-029 | html | _modules/typsphinx/translator.html | 840 | _caption_saved_list_state: Tuple[bool, bool] \| None | _caption_saved_list_state: tuple[bool, bool] \| None | typsphinx/translator.py:556 (annotation) | TRACED |
| H-030 | html | _modules/typsphinx/translator.html | 869 | _table_state_stack: List[Dict[str, Any]] | _table_state_stack: list[dict[str, Any]] | typsphinx/translator.py:585 (annotation) | TRACED |
| H-031 | html | _modules/typsphinx/translator.html | 874 | _saved_body_for_figure_caption: List[Any] \| None | _saved_body_for_figure_caption: list[Any] \| None | typsphinx/translator.py:590 (annotation) | TRACED |
| H-032 | html | _modules/typsphinx/translator.html | 893 | _figure_state_stack: List[Dict[str, Any]] | _figure_state_stack: list[dict[str, Any]] | typsphinx/translator.py:609 (annotation) | TRACED |
| H-033 | html | _modules/typsphinx/translator.html | 921 | _list_item_stack: List[bool] | _list_item_stack: list[bool] | typsphinx/translator.py:637 (annotation) | TRACED |
| H-034 | html | _modules/typsphinx/translator.html | 938 | _legend_list_item_stack: List[Tuple[bool, bool]] | _legend_list_item_stack: list[tuple[bool, bool]] | typsphinx/translator.py:654 (annotation) | TRACED |
| H-035 | html | _modules/typsphinx/translator.html | 1057,2 | current_term_buffer: str \| List[str] \| None; current_definition_buffer: List[str] \| None | current_term_buffer: str \| list[str] \| None; current_definition_buffer: list[str] \| None | typsphinx/translator.py:773-774 (annotations) | TRACED |
| H-036 | html | _modules/typsphinx/translator.html | 1082 | _field_body_stack: List[Tuple[bool, bool, bool]] | _field_body_stack: list[tuple[bool, bool, bool]] | typsphinx/translator.py:798 (annotation) | TRACED |
| H-037 | html | _modules/typsphinx/translator.html | 1096 | _inline_concat_stack: List[Tuple[str, str] \| None] | _inline_concat_stack: list[tuple[str, str] \| None] | typsphinx/translator.py:812 (annotation) | TRACED |
| H-038 | html | _modules/typsphinx/translator.html | 1100 | definition_list_items: List[Tuple[str, str]] | definition_list_items: list[tuple[str, str]] | typsphinx/translator.py:816 (annotation) | TRACED |
| H-039 | html | _modules/typsphinx/translator.html | 1111,3 | _saved_body_stack: List[List[Any]]; _deflist_items_stack: List[List[Tuple[str, str]]]; _pending_term_stack: List[str \| None] | _saved_body_stack: list[list[Any]]; _deflist_items_stack: list[list[tuple[str, str]]]; _pending_term_stack: list[str \| None] | typsphinx/translator.py:827-829 (annotations) | TRACED |
| H-040 | html | _modules/typsphinx/translator.html | 1122 | _saved_body_for_admonition_title: List[Any] \| None | _saved_body_for_admonition_title: list[Any] \| None | typsphinx/translator.py:838 (annotation) | TRACED |
| H-041 | html | _modules/typsphinx/translator.html | 1133 | _title_section_ids: List[str] | _title_section_ids: list[str] | typsphinx/translator.py:849 (annotation) | TRACED |
| H-042 | html | _modules/typsphinx/translator.html | 1160 | _toctree_entry_occurrences: Dict[str, int] | _toctree_entry_occurrences: dict[str, int] | typsphinx/translator.py:876 (annotation) | TRACED |
| H-043 | html | _modules/typsphinx/translator.html | 1978 | _CONCAT_CONTEXTS: Tuple[Tuple[str, str], ...] | _CONCAT_CONTEXTS: tuple[tuple[str, str], ...] | typsphinx/translator.py:1631 (class attribute annotation) | TRACED |
| H-044 | html | _modules/typsphinx/translator.html | 1986 | -> Tuple[str, str] \| None: | -> tuple[str, str] \| None: | typsphinx/translator.py:1639 (`_inline_concat_context` return) | TRACED |
| H-045 | html | _modules/typsphinx/translator.html | 5845 | -> Tuple[str, str] \| None: | -> tuple[str, str] \| None: | typsphinx/translator.py:5303 (`_resolve_xref_docname` return) | TRACED |
| H-046 | html | _modules/typsphinx/writer.html | 277 | from typing import Any, Tuple | from typing import Any | typsphinx/writer.py:10 (import line) | TRACED |
| H-047 | html | _modules/typsphinx/writer.html | 564 | edge_keys: Tuple[str, ...] | edge_keys: tuple[str, ...] | typsphinx/writer.py:284 (param annotation) | TRACED |
| H-048 | html | api/index.html | 409 | typing.Set[str] link/text (docnames) | stdtypes.set[str] link/text | typsphinx/builder.py:1638 (`docnames` param); docstring builder.py:1649 | TRACED |
| H-049 | html | api/index.html | 428,2 | typing.Optional[typing.Set[str]] (build_docnames); typing.Set[str] (updated_docnames) | stdtypes.set[str] \| None (build_docnames); stdtypes.set[str] (updated_docnames) | typsphinx/builder.py:1656-1657; docstrings builder.py:1670-1671 (Pitfall 9 shape change on build_docnames: Optional[Set[str]] -> set[str] \| None) | TRACED |
| H-050 | html | api/index.html | 905 | typing.Tuple[str, ...] (edge_keys) | stdtypes.tuple[str, ...] | typsphinx/writer.py:284 (`edge_keys` param); docstring writer.py:312 | TRACED |
| H-051 | html | api/index.html | 1067 | typing.Dict[str, typing.List[str]] (toctree_includes) | stdtypes.dict[str, stdtypes.list[str]] | typsphinx/translator.py:344 (`toctree_includes` param); docstring translator.py:396 | TRACED |
| H-052 | html | api/index.html | 1076 | typing.Tuple[str, ...] (return type) | stdtypes.tuple[str, ...] | typsphinx/translator.py:345 (return annotation, same function as row above) | TRACED |
| H-053 | html | api/index.html | 1109 | typing.Tuple[str, ...] (edge_keys) | stdtypes.tuple[str, ...] | typsphinx/translator.py:433 (`render_include_edge_state` param); docstring translator.py:453 | TRACED |
| H-054 | html | api/index.html | 5228,2 | typing.List[str]\|None (search_paths); typing.Dict[str,str]\|None (parameter_mapping) | stdtypes.list[str]\|None; stdtypes.dict[str,str]\|None | typsphinx/template_engine.py:262-263 (params) | TRACED |
| H-055 | html | api/index.html | 5232 | typing.List[str]\|None (typst_package_imports) | stdtypes.list[str]\|None | typsphinx/template_engine.py:266 (param) | TRACED |
| H-056 | html | api/index.html | 5371 | typing.Dict[str, Any] (sphinx_metadata) | stdtypes.dict[str, Any] | typsphinx/template_engine.py:468 (`map_parameters` param); docstring template_engine.py:475 | TRACED |
| H-057 | html | api/index.html | 5373 | typing.Optional[typing.Dict[str, Any]] (typst_elements) | stdtypes.dict[str, Any] \| None | typsphinx/template_engine.py:469 (`map_parameters` param); docstring template_engine.py:477 (Pitfall 9 shape change: Optional[Dict[str,Any]] -> dict[str,Any] \| None) | TRACED |
| H-058 | html | api/index.html | 5384 | typing.Dict[str, Any] (return type) | stdtypes.dict[str, Any] | typsphinx/template_engine.py:470 (`map_parameters` return, same function as two rows above) | TRACED |
| H-059 | html | api/index.html | 5401,2 | typing.Dict[str, Any] (sphinx_metadata); typing.Dict[str,Any]\|None (typst_elements) [2nd compact rendering] | stdtypes.dict[str, Any]; stdtypes.dict[str,Any]\|None | typsphinx/template_engine.py:468-469 (`map_parameters`, second/compact field-list rendering of the same params) | TRACED |
| H-060 | html | api/index.html | 5406 | typing.Dict[str, Any] (return type) [2nd compact rendering] | stdtypes.dict[str, Any] | typsphinx/template_engine.py:470 (`map_parameters` return, second/compact rendering) | TRACED |
| H-061 | html | api/index.html | 5435 | typing.Dict[str, Any] (return type) | stdtypes.dict[str, Any] | typsphinx/template_engine.py:604 (`extract_toctree_options` return) | TRACED |
| H-062 | html | api/index.html | 5470 | typing.Dict[str, Any] (params) | stdtypes.dict[str, Any] | typsphinx/template_engine.py:665 (`render` param); docstring template_engine.py:671 | TRACED |
| H-063 | typ | api/index.typ | 225 | typing.Set[str] link (docnames) | stdtypes.set[str] link | typsphinx/builder.py:1638 (`docnames` param); docstring builder.py:1649 | TRACED |
| H-064 | typ | api/index.typ | 248,3 | typing.Optional[typing.Set[...] (build_docnames, part 1: opening tokens) | stdtypes.set[...] (build_docnames, opening tokens) | typsphinx/builder.py:1656 (`build_docnames` param) (Pitfall 9 shape change, part 1 of 2 (Optional[Set[ removed)) | TRACED |
| H-065 | typ | api/index.typ | 253 | text("]]") (build_docnames, part 2: closing tokens) | text("] \| ") + link(None) (build_docnames, closing tokens) | typsphinx/builder.py:1656 (`build_docnames` param, continuation of previous row) (Pitfall 9 shape change, part 2 of 2 (]] -> ] \| None)) | TRACED |
| H-066 | typ | api/index.typ | 262 | typing.Set[str] link (updated_docnames) | stdtypes.set[str] link | typsphinx/builder.py:1657 (`updated_docnames` param) | TRACED |
| H-067 | typ | api/index.typ | 981 | typing.Tuple link (edge_keys, writer) | stdtypes.tuple link | typsphinx/writer.py:284 (`edge_keys` param); docstring writer.py:312 | TRACED |
| H-068 | typ | api/index.typ | 1187 | typing.Dict link (toctree_includes, outer) | stdtypes.dict link | typsphinx/translator.py:344 (`toctree_includes` param, outer dict) | TRACED |
| H-069 | typ | api/index.typ | 1191 | typing.List link (toctree_includes, inner) | stdtypes.list link | typsphinx/translator.py:344 (`toctree_includes` param, inner list) | TRACED |
| H-070 | typ | api/index.typ | 1213 | typing.Tuple[str, ...] (return type, render_include_edge_map) | stdtypes.tuple[str, ...] | typsphinx/translator.py:345 (return annotation) | TRACED |
| H-071 | typ | api/index.typ | 1256 | typing.Tuple[str, ...] (edge_keys, render_include_edge_state) | stdtypes.tuple[str, ...] | typsphinx/translator.py:433 (`render_include_edge_state` param); docstring translator.py:453 | TRACED |
| H-072 | typ | api/index.typ | 5618 | typing.List link (search_paths) | stdtypes.list link | typsphinx/template_engine.py:262 (`search_paths` param) | TRACED |
| H-073 | typ | api/index.typ | 5630 | typing.Dict link (parameter_mapping) | stdtypes.dict link | typsphinx/template_engine.py:263 (`parameter_mapping` param) | TRACED |
| H-074 | typ | api/index.typ | 5662 | typing.List link (typst_package_imports) | stdtypes.list link | typsphinx/template_engine.py:266 (`typst_package_imports` param) | TRACED |
| H-075 | typ | api/index.typ | 5858 | typing.Dict link (sphinx_metadata, map_parameters 1st rendering) | stdtypes.dict link | typsphinx/template_engine.py:468 (`map_parameters` param); docstring template_engine.py:475 | TRACED |
| H-076 | typ | api/index.typ | 5872,3 | typing.Optional[typing.Dict[... (typst_elements, part 1) | stdtypes.dict[... (typst_elements, part 1) | typsphinx/template_engine.py:469 (`map_parameters` param) (Pitfall 9 shape change, part 1 of 2) | TRACED |
| H-077 | typ | api/index.typ | 5879 | text("]]") (typst_elements, part 2) | text("] \| ") + link(None) (typst_elements, part 2) | typsphinx/template_engine.py:469 (`map_parameters` param, continuation of previous row) (Pitfall 9 shape change, part 2 of 2) | TRACED |
| H-078 | typ | api/index.typ | 5899 | typing.Dict link (return type, map_parameters 1st rendering) | stdtypes.dict link | typsphinx/template_engine.py:470 (`map_parameters` return) | TRACED |
| H-079 | typ | api/index.typ | 5917 | typing.Dict link (sphinx_metadata, map_parameters 2nd rendering) | stdtypes.dict link | typsphinx/template_engine.py:468 (`map_parameters` param, second/compact rendering) | TRACED |
| H-080 | typ | api/index.typ | 5929 | typing.Dict link (typst_elements, map_parameters 2nd rendering) | stdtypes.dict link | typsphinx/template_engine.py:469 (`map_parameters` param, second/compact rendering) | TRACED |
| H-081 | typ | api/index.typ | 5942 | typing.Dict link (return type, map_parameters 2nd rendering) | stdtypes.dict link | typsphinx/template_engine.py:470 (`map_parameters` return, second/compact rendering) | TRACED |
| H-082 | typ | api/index.typ | 5972 | typing.Dict link (return type, extract_toctree_options) | stdtypes.dict link | typsphinx/template_engine.py:604 (`extract_toctree_options` return) | TRACED |
| H-083 | typ | api/index.typ | 6009 | typing.Dict link (params, render) | stdtypes.dict link | typsphinx/template_engine.py:665 (`render` param) | TRACED |

TRACED_HUNKS = 83
UNTRACED_HUNKS = 0

## Verdict

No untraced hunks. Every one of the 83 hunks (across both HTML and `.typ` outputs) traces to a `Dict`/`List`/`Set`/`Tuple` -> `dict`/`list`/`set`/`tuple` rename, a `typing` import-line change, or (in the API reference) the matching intersphinx link target/title for the renamed type -- including the `Optional[Set[str]]` -> `set[str] | None` and `Optional[Dict[str, Any]]` -> `dict[str, Any] | None` shape changes on `build_docnames` and `typst_elements` (Pitfall 9), each split across two consecutive diff hunks by the unchanged text between them.

DOC23_VERDICT = MET
