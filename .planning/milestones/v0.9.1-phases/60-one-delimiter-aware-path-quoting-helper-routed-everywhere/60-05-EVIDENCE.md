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

## SC#5 zero test edits (measured)

`PHASE_BASE_SHA` read from `60-01-EVIDENCE.md`'s `## Phase base SHA` section:
`31441d09bd8168f1bcc5170749f6d9646a1d5151`.

### Full `tests/` diff, name-status

Command: `git diff --name-status 31441d09bd8168f1bcc5170749f6d9646a1d5151..HEAD -- tests/`

```
A	tests/test_builder_path_quoting_gate.py
A	tests/test_pathfmt.py
A	tests/test_template_registry_path_quoting_gate.py
M	tests/test_templates_path_collision_gate.py
A	tests/test_writer_path_quoting_gate.py
```

Every line begins with `A` except exactly one `M` line, for
`tests/test_templates_path_collision_gate.py` — exactly as required. No other file appears
with `M` or `D`.

### The one modified file — pure addition

Command: `git diff -U0 31441d09bd8168f1bcc5170749f6d9646a1d5151..HEAD -- tests/test_templates_path_collision_gate.py`

```
diff --git a/tests/test_templates_path_collision_gate.py b/tests/test_templates_path_collision_gate.py
index a9eb85e5..e0b51294 100644
--- a/tests/test_templates_path_collision_gate.py
+++ b/tests/test_templates_path_collision_gate.py
@@ -442,0 +443,4 @@ class TestWindowsPathEscapingRegressionGuard:
+    # MSG-03/D-12: a path-shaped value containing a literal apostrophe --
+    # the single-quote half of the D-01 delimiter-selection rule (the
+    # backslash half is already green here since Phase 57).
+    SINGLE_QUOTE_SHAPED_PATH = "/home/O'Brien's Projects/_templates/nested"
@@ -491,0 +496,46 @@ class TestWindowsPathEscapingRegressionGuard:
+
+    def test_conf17_violation_message_disambiguates_embedded_single_quote(self):
+        """MSG-03/D-12: the SINGLE-QUOTE half of the D-01 delimiter rule,
+        not the backslash half. These three 57-11 message builders
+        stopped doubling backslashes in Phase 57 -- a backslash-doubling
+        assertion here would be tautologically green and prove nothing.
+        The defect this test targets is the one 57-11 introduced by
+        hardcoding an apostrophe delimiter (``'...'``) instead of
+        reproducing ``repr()``'s delimiter SELECTION: a path containing a
+        literal apostrophe can visually close that hardcoded delimiter
+        early. MSG-02's ``quote_path()`` selects double quotes instead
+        whenever the value contains an apostrophe and no double quote, so
+        the double-quote-delimited form of the value must appear intact
+        as a substring of the message.
+        """
+        message = _conf17_violation_message(
+            "mykey", self.SINGLE_QUOTE_SHAPED_PATH, "/srcdir"
+        )
+        assert f'"{self.SINGLE_QUOTE_SHAPED_PATH}"' in message
+
+    def test_templates_path_collision_message_disambiguates_embedded_single_quote(
+        self,
+    ):
+        """MSG-03/D-12: same single-quote-half rationale as
+        ``test_conf17_violation_message_disambiguates_embedded_single_quote``
+        above, for ``_templates_path_collision_message()``'s
+        ``bundle_dir`` argument."""
+        message = _templates_path_collision_message(
+            "mykey",
+            self.SINGLE_QUOTE_SHAPED_PATH,
+            "_templates",
+            "/srcdir/_templates",
+        )
+        assert f'"{self.SINGLE_QUOTE_SHAPED_PATH}"' in message
+
+    def test_bundle_destination_collision_message_disambiguates_embedded_single_quote(
+        self,
+    ):
+        """MSG-03/D-12: same single-quote-half rationale as
+        ``test_conf17_violation_message_disambiguates_embedded_single_quote``
+        above, for ``_bundle_destination_collision_message()``'s
+        ``dest_dir`` argument."""
+        message = _bundle_destination_collision_message(
+            "alpha", "beta", self.SINGLE_QUOTE_SHAPED_PATH
+        )
+        assert f'"{self.SINGLE_QUOTE_SHAPED_PATH}"' in message
```

`git diff -U0 ... | grep -c '^-'` returns `1` — the single unified-diff header line
(`--- a/tests/...`) only. **Zero removed source lines.** The touch to this pre-existing test
file was pure addition: one constant plus three whole new test methods appended after the
pre-existing `test_registry_keys_stay_repr_quoted`.

**`_assert_no_doubled_separator` is byte-identical.** It is defined at line 449 of the current
file (`grep -n "_assert_no_doubled_separator" tests/test_templates_path_collision_gate.py`)
and does not appear anywhere inside the diff hunk above — the diff's two hunks touch only
lines 443 (a new class constant) and 492 onward (three brand-new methods appended after the
last pre-existing method), never the `_assert_no_doubled_separator` static method itself or
any of its sixteen pre-existing call sites. `58-REPR-CENSUS.md`'s third bucket names this
exact predicate as must-not-be-rewritten and must-not-be-re-litigated; it was not touched.

### Cross-check against `58-REPR-CENSUS.md`

`58-REPR-CENSUS.md`'s pass-criterion table enumerates these test modules (excluding the two
MSG-01 already rewrote before this phase began):

| Census module | Modified in this phase's `tests/` diff? |
|---|---|
| `tests/test_registry_container_shape_gate.py` | No |
| `tests/test_registry_prewrite_validation_gate.py` | No |
| `tests/test_template_engine.py` | No |
| `tests/test_template_registry.py` | No |

Confirmed with: `git diff --name-status 31441d09bd8168f1bcc5170749f6d9646a1d5151..HEAD -- tests/test_registry_container_shape_gate.py tests/test_registry_prewrite_validation_gate.py tests/test_template_engine.py tests/test_template_registry.py`

```
(no output)
```

None of the four census-enumerated modules appears as modified — matching the full `tests/`
diff above, which lists only the one already-discussed `M` line for a file the census does
NOT enumerate (`test_templates_path_collision_gate.py` carries the format-asserting "third
bucket" predicate, not a pass-criterion site).

### AST census guard

Command: `uv run pytest tests/test_repr_census_guard.py -q`

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a81cc5ed13e7db22e
configfile: pyproject.toml
plugins: cov-7.1.0
collected 4 items

tests/test_repr_census_guard.py ....                                     [100%]

============================== 4 passed in 0.61s ===============================
```

No entry was appended to `PASS_CRITERION_REPR_ALLOWLIST` — the allowlist stays at its recorded
7 entries.

Command: `git diff 31441d09bd8168f1bcc5170749f6d9646a1d5151..HEAD -- tests/test_repr_census_guard.py`

```
(no output)
```

## Final local gate

Command: `uv run pytest -q`

```
================= 1511 passed, 5 skipped in 121.34s (0:02:01) ==================
```

**Reconciled against each plan's own isolated-worktree count:** wave 1 baseline (`60-01-EVIDENCE.md`)
was `1494 passed, 5 skipped`. Each wave-2 plan ran in its own worktree against that same
baseline plus only its own new tests: `60-02-EVIDENCE.md` (builder.py — 7 new tests in
`tests/test_builder_path_quoting_gate.py` + 3 new methods added to the existing
`TestWindowsPathEscapingRegressionGuard` class = +10) recorded `1504 passed`;
`60-03-EVIDENCE.md` (writer.py — 2 new tests) recorded `1496 passed`; `60-04-EVIDENCE.md`
(template_registry.py — 5 new tests) recorded `1499 passed`. Summed on top of the 1494
baseline once all three wave-2 plans are merged together: `1494 + 10 + 2 + 5 = 1511` — matching
this task's measured full-suite count exactly. No test was added or removed by this task.

Command: `uv run black --check .`

```
All done! ✨ 🍰 ✨
353 files would be left unchanged.
```

Command: `uv run mypy typsphinx/`

```
Success: no issues found in 9 source files
```

### Per-module skip census — the four new gate modules

Command: `uv run pytest tests/test_pathfmt.py tests/test_builder_path_quoting_gate.py tests/test_writer_path_quoting_gate.py tests/test_template_registry_path_quoting_gate.py -v -rs`

```
============================== 41 passed in 0.28s ==============================
```

**0 skipped** across all four new gate modules — `tests/test_pathfmt.py` (MSG-02, 27 tests),
`tests/test_builder_path_quoting_gate.py` (MSG-03, 7 tests), `tests/test_writer_path_quoting_gate.py`
(MSG-04, 2 tests), `tests/test_template_registry_path_quoting_gate.py` (MSG-05, 5 tests) — 41
total, all passed, 0 skipped, 0 deselected in this combined run. A skipped test is never
recorded as a pass: every one of these four modules is a pure string, `caplog`, or
`ExtensionError` assertion needing no Windows host and no compiler, so a skip here can only
mean the worktree venv is wrong. It is not — this worktree was provisioned per `CLAUDE.md`'s
`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` before any command in this
plan ran, confirmed by `tests/test_pathfmt.py`'s own successful import of `typsphinx.pathfmt`
in the very first task of wave 1.

### `ruff check .` — deferred to CI

Command: `uv run ruff check .`

```
Could not start dynamically linked executable: ruff
NixOS cannot run dynamically linked executables intended for generic
linux environments out of the box. For more information, see:
https://nix.dev/permalink/stub-ld
```

This is an environment limitation, not a code defect — a freshly-provisioned worktree venv on
this NixOS-sandboxed development machine pulls a generic-linux `ruff` wheel whose ELF the
loader rejects at exec time (`MEMORY.md`'s "NixOS sandbox test env" note: "ruff は未解消").
CI holds lint authority for this project (`CLAUDE.md`'s own commands section).

## RED-first ledger (phase-wide)

Every one of MSG-02, MSG-03, MSG-04 and MSG-05 has a recorded local RED that preceded its
green. No row below is filled with a green-only reference.

| Requirement | Per-plan evidence file | RED section | GREEN section |
|---|---|---|---|
| MSG-02 | `60-01-EVIDENCE.md` | `## MSG-02 RED` (`ModuleNotFoundError: No module named 'typsphinx.pathfmt'`, exit code 2, before `typsphinx/pathfmt.py` existed) | `## MSG-02 GREEN` (`27 passed`, zero failed, zero skipped) |
| MSG-03 | `60-02-EVIDENCE.md` | `## RED — three 57-11 builders (single-quote half)`, `## RED — _resolve_target_stem`, `## RED — _track_image rehome warning`, `## RED — _validate_output_path_collisions`, `## RED — _copy_bundle_directory` (8 recorded failures across 5 message families, all in commit `f62788de`, before any product edit) | `## GREEN` (`26 passed` for the two gate modules combined; full suite, black, mypy and census guard all green) |
| MSG-04 | `60-03-EVIDENCE.md` | `## RED — wrapper-render debug log` (`1 failed, 1 passed` — `AssertionError: Expected every backslash run to be a single unescaped separator`, before `typsphinx/writer.py` was edited) | `## GREEN` (`2 passed`; full suite 1496 passed, 5 skipped; black/mypy/census guard all green) |
| MSG-05 | `60-04-EVIDENCE.md` | `## RED shape 1 — doubled backslash (str template)` and `## RED shape 2 — leaked class-name wrapper (Path template)` (`3 failed, 2 passed` at that point in the plan, before any product-code edit) | `## GREEN` (`5 passed` across all three classes; `tests/test_template_registry.py` 76 passed with zero edits) |

## SC#5 3-OS CI dispatch

**RESOLVED — dispatched fresh by the orchestrator on the phase's own post-fix tip.**

This section replaces the `PENDING — owner dispatch required` marker 60-05 recorded. The reason
that marker existed is unchanged and worth keeping on the record: 60-05 ran inside an isolated
worktree whose HEAD was a per-agent branch (`worktree-agent-a81cc5ed13e7db22e`) that does not exist
on `origin` and is not the phase tip. Dispatching from there would have cited a tip that is NOT the
phase tip — exactly the stale/wrong-tree citation T-60-13 forbids. The orchestrator performed the
dispatch after merging every wave, on the real tip.

### Dispatch 1 (2026-08-29) — FAILED, and this is the record of why

- Run URL: https://github.com/YuSabo90002/typsphinx/actions/runs/33250839303
- Dispatched head SHA: `516e0b2fafc78909a4621a00625c2e4191ed4a6a`
- Local tip SHA at dispatch: `516e0b2fafc78909a4621a00625c2e4191ed4a6a` (identical)
- Conclusion: **failure** — 3 of 12 jobs red

This dispatch is retained deliberately rather than discarded. ROADMAP constraint 10 says CI is the
final confirmation and never the first discovery; here it *was* first discovery for two defect
classes that no local gate in this environment could reach, and hiding that would misrepresent how
the phase closed.

| job | conclusion |
|---|---|
| Lint and Format Check | **failure** — `ruff F401`: unused module-scope `importlib.util` in `tests/test_pathfmt.py:28` |
| Test Python 3.12 on windows-latest | **failure** — 1 failed, 1505 passed, 10 skipped |
| Test Python 3.13 on windows-latest | **failure** — 1 failed, 1505 passed, 10 skipped |
| Test Python 3.12 on ubuntu-latest | success |
| Test Python 3.13 on ubuntu-latest | success |
| Test Python 3.12 on macos-latest | success |
| Test Python 3.13 on macos-latest | success |
| Type Check | success |
| Code Coverage | success |
| Build Package | success |
| Integration Test - basic | success |
| Integration Test - advanced | success |

**What it caught (both fixed before dispatch 2):**

1. `ruff F401` — unreachable locally: `ruff`'s PyPI generic-linux wheel cannot exec in this dev
   sandbox (QUA-06), so every executor correctly deferred lint to CI, and CI is where it surfaced.
   Fixed in `78c85fe4`.
2. `tests/test_template_registry_path_quoting_gate.py::TestRegistryTemplatePathQuoting::test_conf17_violation_message_has_no_doubled_separator`
   failed on **windows-latest only**, both Python versions. The fixture
   `C:\Users\runner\base.typ` is one plain filename component on POSIX (a backslash is not a
   separator there) so its parent is `srcdir` and the CONF-17 branch fires — the premise the test's
   own docstring stated. On Windows the same string is an ABSOLUTE path, the parent is never
   `srcdir`, and only the existence-check branch fires. Fixed in `130f614e` by asserting the branch
   per platform rather than skipping Windows. **Note the production code was clean on Windows
   throughout**: the observed failure message rendered the template as
   `'C:\Users\runner\base.typ'` with single backslashes, i.e. `quote_path()` was already correct
   there; only the test's branch assumption was not.

A third defect was fixed between the two dispatches from a different source — `60-REVIEW.md` CR-01,
the `quote_path()` both-quotes escape (`e3399825`, D-01 AMENDED). See `60-CONTEXT.md`'s AMENDED
block under D-01/D-01a.

### Dispatch 2 (2026-08-29) — SUCCESS, this is SC#5's acceptance record

- Run URL: https://github.com/YuSabo90002/typsphinx/actions/runs/33252336287
- Dispatched head SHA: `130f614e451cb873684755c4ec1b60531ca90f76`
- Local tip SHA at dispatch: `130f614e451cb873684755c4ec1b60531ca90f76` (**identical** — the run is
  against this phase's own post-fix tip, not inferred from any earlier run)
- Conclusion: **success** — 12 of 12 jobs green
- The dispatched head SHA is newer than every commit this phase produced in waves 1–3, and newer
  than the two fix commits above.

| job | conclusion |
|---|---|
| Test Python 3.12 on ubuntu-latest | success |
| Test Python 3.13 on ubuntu-latest | success |
| Test Python 3.12 on windows-latest | success |
| Test Python 3.13 on windows-latest | success |
| Test Python 3.12 on macos-latest | success |
| Test Python 3.13 on macos-latest | success |
| Lint and Format Check | success |
| Type Check | success |
| Code Coverage | success |
| Build Package | success |
| Integration Test - basic | success |
| Integration Test - advanced | success |

### Orchestrator-side local gates on the same tip

- Full suite: `1517 passed, 1 skipped`
- Full suite under `LC_ALL=C LANG=C`: same result — the locale-dependent CI-only failure class is
  pre-empted, not merely unobserved
- `black --check .`: clean (353 files); `mypy typsphinx/`: clean (9 source files)
- Cross-phase regression gate (Phase 58 + 59 test files, 83 tests): all passed, with
  `tests/test_repr_census_guard.py` and `tests/test_out02_escape_target_gate.py` green and
  **unedited** — the live substance of SC#5's zero-test-edit claim
