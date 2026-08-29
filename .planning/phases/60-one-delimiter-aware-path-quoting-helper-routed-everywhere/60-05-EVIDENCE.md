# Phase 60 Plan 05 — Acceptance Evidence

## Phase tip SHA

`git rev-parse HEAD`, taken before this plan's own commits (this plan makes no product
change; the acceptance measurements below are taken against the merged wave-1+wave-2 tip):

```
c8aedc474ed34f9b2943d2e45d7ae35eddc4a799
```

## SC#2 repo-wide discovery grep

Per ROADMAP constraint (Phase 60 SC#2) and this plan's own instructions, each of the four
commands is run **REPO-WIDE over the whole `typsphinx/` package**, not restricted to the three
named modules — the execution-time, repo-wide grep is the discovery authority, not any line
list written before it.

### `grep -rn "\!r" typsphinx/`

```
typsphinx/writer.py:155:            f"{entry[0]!r} is not a str: {value!r} -- "
typsphinx/writer.py:156:            f"falling back to {default!r}"
typsphinx/writer.py:512:            f"Rendering wrapper for docname {docname!r} at "
typsphinx/template_registry.py:115:        return f"registry key {key!r} is empty or whitespace-only"
typsphinx/template_registry.py:117:        return f"registry key {key!r} is '.' or '..', which is not a legal registry key"
typsphinx/template_registry.py:120:            f"registry key {key!r} contains a path separator ('/' or "
typsphinx/template_registry.py:125:            f"registry key {key!r} is a Windows reserved device name "
typsphinx/template_registry.py:129:        return f"registry key {key!r} ends with a trailing dot"
typsphinx/template_registry.py:131:        return f"registry key {key!r} ends with a trailing space"
typsphinx/template_registry.py:134:            f"registry key {key!r} differs from another registered key " "only by case"
typsphinx/template_registry.py:307:            f" got {declared!r}"
typsphinx/template_registry.py:334:            failures.append(f"registry key {key!r} is not a string")
typsphinx/template_registry.py:342:                f"registry key {key!r} is reserved for the built-in "
typsphinx/template_registry.py:343:                f"{RESERVED_REGISTRY_KEY!r} key and cannot be redeclared "
typsphinx/template_registry.py:365:                f"registry key {key!r}'s definition must be a dict, got "
typsphinx/template_registry.py:366:                f"{raw_definition!r}"
typsphinx/template_registry.py:378:                f"registry key {key!r}'s definition sets both 'template' "
typsphinx/template_registry.py:420:                f"registry key {key!r}'s template {template!r} must be a path string or os.PathLike, "
typsphinx/template_registry.py:435:                # `TypeError` at this call site. `key` stays `!r` -- it is
typsphinx/template_registry.py:440:                    f"registry key {key!r}'s template {quote_path(template)} "
typsphinx/template_registry.py:453:                    f"registry key {key!r}'s template {quote_path(template)} "
typsphinx/template_registry.py:535:                f"typst_documents entry names registry key {raw_key!r}, "
typsphinx/template_registry.py:537:                f"typst_document_templates keys: {sorted(registry.keys())!r}"
typsphinx/template_registry.py:545:            f"typst_documents entry names registry key {key!r}, which is "
typsphinx/template_registry.py:547:            f"keys: {sorted(registry.keys())!r}"
typsphinx/template_engine.py:176:        f"'language' = {sphinx_language!r} -- omitting 'lang' (falling "
typsphinx/template_engine.py:568:                    f"typst_elements: unknown key {key!r} -- "
typsphinx/builder.py:528:        f"typst_document_templates: registry key {key!r}'s "
typsphinx/builder.py:545:    back to ``!r`` (57-11-PLAN.md task 2).
typsphinx/builder.py:551:            ``typsphinx.pathfmt.quote_path()`` (MSG-03), never ``!r``,
typsphinx/builder.py:564:        f"registry key {key!r}'s resolved template "
typsphinx/builder.py:594:            never ``!r``).
typsphinx/builder.py:600:        f"registry key {existing_key!r} and registry key "
typsphinx/builder.py:601:        f"{key!r} both resolve to the same bundle "
typsphinx/builder.py:892:                        f"{docname!r} after removing an unsupported path -- "
typsphinx/builder.py:893:                        f"falling back to {docname!r}"
typsphinx/builder.py:914:                    f"{docname!r} -- falling back to {docname!r}"
typsphinx/builder.py:927:                f"{docname!r} -- falling back to {docname!r}"
typsphinx/builder.py:1160:            _claim(content_relpath, f"the content file for docname {docname!r}")
typsphinx/builder.py:1165:                        f"the content file for docname {docname!r} would "
typsphinx/builder.py:1191:                    f"typst_documents entry {index} ({entry!r}) produces "
typsphinx/builder.py:1213:                f"typst_documents entry {index} (docname {docname!r}, "
typsphinx/builder.py:1221:                        f"{docname!r}, target {target_text}) would write "
typsphinx/builder.py:1493:                        f"registry key {declared_key!r} differs from "
typsphinx/builder.py:1494:                        f"the built-in {RESERVED_REGISTRY_KEY!r} "
typsphinx/builder.py:1502:                        f"{declared_key!r} to something that does not "
typsphinx/builder.py:1588:            summary = "; ".join(f"{key!r}: {message}" for key, message in failures)
typsphinx/builder.py:2248:                    logger.debug(f"Copied bundle file for {key!r}: {rel_path}")
typsphinx/builder.py:2255:                            f"resolved template for registry key {key!r} "
typsphinx/builder.py:2266:                f"registry key {key!r} ({quote_path(template_filename)}) "
typsphinx/builder.py:2436:            summary = "; ".join(f"{key!r}: {message}" for key, message in failures)
typsphinx/builder.py:2564:                logger.warning(f"Malformed typst_documents entry: {doc_tuple!r}")
typsphinx/builder.py:2577:                    f"{docname!r} -- expected a str"
typsphinx/builder.py:2592:                    f"typst_documents entry {doc_tuple!r} has no target "
typsphinx/builder.py:2609:                        f"Master document {docname!r} is not a known Sphinx document"
typsphinx/translator.py:417:                f"{master_docname!r} is a very deep toctree nesting -- "
typsphinx/translator.py:420:                f"{path[0]!r} to {path[-1]!r}."
typsphinx/translator.py:5510:                f"(edge_key={edge_key!r})"
```

### `grep -rn "repr(" typsphinx/`

```
typsphinx/template_engine.py:137:    ``logger.warning`` naming the offending value via ``repr()`` and returns
typsphinx/template_registry.py:317:    # `int` beside a `str`). Deliberately NOT `repr(k)` for both partitions:
typsphinx/template_registry.py:318:    # `repr()` switches to double quotes for a string containing an
typsphinx/template_registry.py:325:        key=lambda k: (not isinstance(k, str), k if isinstance(k, str) else repr(k)),
typsphinx/pathfmt.py:19:``''`` is byte-identical to ``repr("")``).
typsphinx/pathfmt.py:21:D-01: the delimiter rule reproduces ``repr()``'s exactly, minus the
typsphinx/pathfmt.py:38:    ``repr()``'s own delimiter-selection rule (D-01) minus the backslash
typsphinx/builder.py:552:            so a Windows backslash is not doubled by ``repr()`` and a
typsphinx/builder.py:1104:        ``repr()`` and stating it produces no wrapper file -- this is the
typsphinx/builder.py:1208:                quote_path(target) if isinstance(target, str) else repr(target)
typsphinx/builder.py:2565:                failures.append((repr(doc_tuple), "malformed typst_documents entry"))
typsphinx/builder.py:2580:                failures.append((repr(docname), message))
```

### `grep -rn "%r" typsphinx/`

```
typsphinx/translator.py:3274:                "Dangling footnote reference: refid=%r not found in document",
```

### `grep -rnoE "'\{[a-zA-Z_.]+\}'" typsphinx/`

```
typsphinx/pathfmt.py:80:'{value_str}'
typsphinx/pathfmt.py:84:'{escaped}'
typsphinx/translator.py:5047:'{up_path}'
typsphinx/translator.py:5047:'{down_path}'
typsphinx/translator.py:5152:'{up_path}'
typsphinx/translator.py:5152:'{down_path}'
typsphinx/translator.py:5372:'{value}'
typsphinx/translator.py:5387:'{unit}'
typsphinx/translator.py:5387:'{value}'
```

### Classification — the three in-scope modules

D-05's role rule: does the reader read this value as a location on a filesystem, or as a name
in a namespace?

| Module | Line | Value | Classification | Disposition |
|---|---|---|---|---|
| writer.py | 155 | `entry[0]` | identifier (docname) | stays `!r` (D-07) |
| writer.py | 155 | `value` | identifier (title/author element) | stays `!r` (D-07) |
| writer.py | 156 | `default` | identifier (`config.project`/`config.author`) | stays `!r` (D-07) |
| writer.py | 512 | `docname` | identifier | stays `!r` (D-07) |
| writer.py | (513, not in grep above — routed) | `wrapper_relative_dir`, `include_path`, `template_file` | path-valued | routed (`quote_path(...)`, confirmed via `grep -c 'quote_path(' typsphinx/writer.py` → 3 below) |
| template_registry.py | 115,117,120,125,129,131,134 | `key` | identifier (registry key) | stays `!r` (D-07) |
| template_registry.py | 307 | `declared` | identifier (raw non-`dict` config value) | stays `!r` (D-07) |
| template_registry.py | 334,342,365,378 | `key` | identifier (registry key) | stays `!r` (D-07) |
| template_registry.py | 343 | `RESERVED_REGISTRY_KEY` | identifier (registry key) | stays `!r` (D-07) |
| template_registry.py | 366 | `raw_definition` | identifier (raw non-`dict` value) | stays `!r` (D-07) |
| template_registry.py | 420 | `key` | identifier (registry key) | stays `!r` (D-07) |
| template_registry.py | 420 | `template` | **deliberate exclusion** (SC#3) — reached only when `template` is NOT `str`/`os.PathLike` | stays `!r` (measured pass criterion, not an oversight) |
| template_registry.py | 440, 453 | `key` | identifier (registry key) | stays `!r` (D-07) |
| template_registry.py | 440, 453 | `template` (via `quote_path(template)`) | path-valued | **routed** |
| template_registry.py | 535, 545 | `raw_key`, `key` | identifier (registry key) | stays `!r` (D-07) |
| template_registry.py | 537, 547 | `sorted(registry.keys())` | identifier list (registry keys) | stays `!r` (D-07) |
| builder.py | 528, 564, 600, 601, 1493, 1494, 1502, 1588, 2248, 2255, 2266, 2436 | `key`/`existing_key`/`declared_key`/`RESERVED_REGISTRY_KEY` | identifier (registry key) | stays `!r` (D-07) |
| builder.py | 892, 893, 914, 927, 1160, 1165, 1213, 1221, 2577, 2609 | `docname` | identifier | stays `!r` (D-07) |
| builder.py | 1191 | `entry` | identifier (whole-tuple config entry) | stays `!r` (D-07) |
| builder.py | 2564, 2592 | `doc_tuple` | identifier (config doc-tuple) | stays `!r` (D-07) |
| builder.py | 1221 | `target_text` (mixed f-string, `docname!r` stays, `target_text` already routed) | path-valued for `target_text` | **routed** upstream (this line only shows the already-routed `target_text` name, not `!r`) |
| builder.py | 2266 | `template_filename` (via `quote_path(template_filename)`) | path-valued | **routed** (shown here as the already-routed call; `key` on the same line stays `!r`) |
| builder.py | 2565 | `repr(doc_tuple)` | identifier (config tuple, `failures.append`) | stays unrouted (D-07) |
| builder.py | 2580 | `repr(docname)` | identifier | stays unrouted (D-07) |
| builder.py | 1208 | `repr(target)` (non-`str` fallback branch of `quote_path(target) if isinstance(target, str) else repr(target)`) | non-path type at this branch by construction | correct fallback, not a defect |

**Conclusion: zero path-valued interpolations remain unrouted in `typsphinx/builder.py`,
`typsphinx/writer.py` or `typsphinx/template_registry.py`.** Every hit in the three in-scope
modules above is either (a) identifier-valued and correctly still `!r`, (b) the single
deliberate exclusion at `template_registry.py:420` (SC#3's own measured pass criterion), or (c)
already routed through `quote_path()`. The negative grep for every named path-valued site
confirms this independently (see `## SC#3 over-reach measurement` below).

### Fourth-module hits — classified, not fixed

Per this plan's own scope rule, any hit in `translator.py`, `template_engine.py`, `pdf.py`,
`removed_config.py` or `__init__.py` is classified but never fixed here.

| Module | Line | Value | Classification | Disposition |
|---|---|---|---|---|
| template_engine.py | 176 | `sphinx_language` | identifier (Sphinx `language` config value, a locale code) | not path-valued — no action |
| template_engine.py | 568 | `key` | identifier (`typst_elements` unknown key name) | not path-valued — no action |
| translator.py | 417 | `master_docname` | identifier (docname) — matches the source todo's own prior classification | not path-valued — no action |
| translator.py | 420 | `path[0]`, `path[-1]` | identifier (docnames from a toctree path list) — matches the source todo's own prior classification | not path-valued — no action |
| translator.py | 5510 | `edge_key` | identifier (cross-reference edge cache key) | not path-valued — no action |
| translator.py | 3274 | `refid` (`%r`) | identifier (footnote reference ID) | not path-valued — no action |
| translator.py | 5372 | `value` | CSS length value string (e.g. a dimension like `"3xyz"`), not a filesystem location | not path-valued — no action |
| translator.py | 5387 | `unit`, `value` | CSS length unit/value strings | not path-valued — no action |
| translator.py | 5047 | `up_path`, `down_path` (hardcoded `'...'` delimiter, `grep4`) | **PATH-VALUED** — relative-path fragments (`"../"` repeats and a `"/"`-joined docname-tree slice) built for a Typst `#include()` path, inside `_compute_relative_include_path()`'s debug log | **genuinely path-valued; filed as a new todo, not fixed** (pdf.py, removed_config.py, `__init__.py`: zero hits from any of the four greps — confirmed separately) |
| translator.py | 5152 | `up_path`, `down_path` (hardcoded `'...'` delimiter, `grep4`) | **PATH-VALUED** — same shape, inside `_compute_relative_image_path()`'s debug log | **genuinely path-valued; filed as a new todo, not fixed** |

**A genuinely path-valued site was found in a fourth module** (`typsphinx/translator.py`,
lines 5047 and 5152 — both `logger.debug()` calls carrying the same hardcoded-single-quote
delimiter defect the three 57-11 message builders had before Phase 60's 60-02 plan routed
them). Per this plan's own prohibition against widening scope mid-phase, this was **not**
fixed. A new todo record was filed instead:

```
.planning/todos/pending/2026-08-29-hardcoded-delimiter-path-fragments-in-translator-relative-path-debug-logs.md
```

`pdf.py`, `removed_config.py` and `__init__.py` were independently checked with all four grep
patterns and produced **zero hits** — confirmed by:

```
$ grep -nE '(\!r|repr\(|%r)' typsphinx/pdf.py typsphinx/removed_config.py typsphinx/__init__.py
(no output)
$ grep -noE "'\{[a-zA-Z_.]+\}'" typsphinx/pdf.py typsphinx/removed_config.py typsphinx/__init__.py
(no output)
```

No product file outside the three in-scope modules was edited by this task
(`git status --porcelain typsphinx/ tests/` is empty, confirmed below).

## SC#3 over-reach measurement

Each surviving identifier-valued class recorded as a command plus its output, not as a prose
claim.

### Registry keys in every form (all shapes: `key`, `existing_key`, `declared_key`,
`RESERVED_REGISTRY_KEY`, `raw_key`)

Command: `grep -cE '\{(key|existing_key|declared_key|RESERVED_REGISTRY_KEY|raw_key)!r\}' typsphinx/builder.py typsphinx/writer.py typsphinx/template_registry.py`

```
typsphinx/builder.py:12
typsphinx/writer.py:0
typsphinx/template_registry.py:17
```

29 surviving registry-key `!r` conversions across the two modules that carry them
(`writer.py` has none — it names no registry key at all).

### Docnames

Command: `grep -cE '\{docname!r\}' typsphinx/builder.py typsphinx/writer.py typsphinx/template_registry.py`

```
typsphinx/builder.py:10
typsphinx/writer.py:1
typsphinx/template_registry.py:0
```

11 surviving docname `!r` conversions.

### Whole-tuple config `entry`

Command: `grep -nE '\{entry!r\}' typsphinx/builder.py`

```
1191:                    f"typst_documents entry {index} ({entry!r}) produces "
```

Exactly 1 surviving site, unchanged.

### Config `doc_tuple`

Command: `grep -nE '\{doc_tuple!r\}' typsphinx/builder.py`

```
2564:                logger.warning(f"Malformed typst_documents entry: {doc_tuple!r}")
2592:                    f"typst_documents entry {doc_tuple!r} has no target "
```

Exactly 2 surviving sites, unchanged.

### Sorted key lists

Command: `grep -nE '\{sorted\(registry\.keys\(\)\)!r\}' typsphinx/template_registry.py`

```
537:                f"typst_document_templates keys: {sorted(registry.keys())!r}"
547:            f"keys: {sorted(registry.keys())!r}"
```

Exactly 2 surviving sites, unchanged.

### `template_registry.py`'s deliberately-excluded type-check message

Command: `grep -cE '\{template!r\}' typsphinx/template_registry.py`

```
1
```

Command: `grep -nE '\{template!r\}' typsphinx/template_registry.py`

```
420:                f"registry key {key!r}'s template {template!r} must be a path string or os.PathLike, "
```

**Line 420 is the sole surviving `template` repr conversion in `typsphinx/template_registry.py`,
measured now.** This is a MEASURED PASS CRITERION, not an oversight: that branch
(`if template and not isinstance(template, (str, os.PathLike)): ...`) is reached precisely
when the value is NOT a path type (a `list`, `bytes`, an `int`), so routing it through
`quote_path()` would misrepresent a list or bytes value as a filesystem location and would
raise `TypeError` on the exact values this branch exists to report — the opposite of correct
diagnostic behavior. The two routed sibling sites (`:440`, `:453`) sit inside the following
`elif template:` branch, which is reachable only when `template` IS `str` or `os.PathLike`
(see 60-04-EVIDENCE.md's `## Edge reachability` for the structural proof that these two
branches are mutually exclusive).

### Falsification gate — the two guarding assertions

Command: `uv run pytest tests/test_template_registry.py -q`

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a81cc5ed13e7db22e
configfile: pyproject.toml
plugins: cov-7.1.0
collected 76 items

tests/test_template_registry.py ........................................ [ 52%]
....................................                                     [100%]

============================== 76 passed in 1.14s ===============================
```

All 76 tests pass, including the two assertions pinning the excluded message's `repr()` output
for a list template (`test_non_path_template_field_raises_extension_error_not_typeerror`'s
`assert repr(["a", "b"]) in message`) and for a bytes template
(`test_bytes_template_field_raises_extension_error_not_typeerror`'s
`assert repr(b"base.typ") in message`) — **both GREEN, UNMODIFIED**. These two assertions are
the phase's falsification gate for accidental over-reach: had this phase's rollout
accidentally routed the type-check message through `quote_path()`, both would fail, since
`quote_path()` raises `TypeError` on a `list` or `bytes` value rather than rendering Python's
own `repr()`.

Command: `git diff --name-status 31441d09bd8168f1bcc5170749f6d9646a1d5151..HEAD -- tests/test_template_registry.py`

```
(no output)
```

`tests/test_template_registry.py` does not appear at all in the phase's `tests/` diff — the
file carrying the two falsification-gate assertions was never touched.

### Clean-tree confirmation for this task

Command: `git status --porcelain typsphinx/ tests/`

```
(no output)
```

This task edited neither `typsphinx/` nor `tests/` — only this evidence file and the one new
todo record under `.planning/todos/pending/`.
