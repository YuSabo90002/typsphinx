---
created: 2026-09-20
title: "visit_literal_block and depart_literal_block docstrings still read `Args: node: The literal block node`, although both signatures were widened to nodes.literal_block | nodes.doctest_block"
area: translator, docs
resolves_phase: null
source: 74-REVIEW.md § "Info" IN-01
severity: minor
files:
  - typsphinx/translator.py:2444-2445  # visit_literal_block's Args: line (re-measured 2026-09-20)
  - typsphinx/translator.py:2594-2595  # depart_literal_block's Args: line (re-measured 2026-09-20)
---

## Problem

Phase 74 widened both `visit_literal_block` and `depart_literal_block`'s node-parameter type to
`nodes.literal_block | nodes.doctest_block`, and updated the surrounding prose in several places
(for example the `language` fallback comment inside `visit_literal_block`) to describe the new
doctest-block behavior. The `Args:` sections of both docstrings were not updated to match, and
still read, verbatim:

`visit_literal_block` (`typsphinx/translator.py:2444-2445`):

```
        Args:
            node: The literal block node
```

`depart_literal_block` (`typsphinx/translator.py:2594-2595`):

```
        Args:
            node: The literal block node
```

A reader who consults only the `Args:` line — not the full docstring body, the widened type
annotation, or `visit_doctest_block`'s own docstring — does not learn that `visit_literal_block`
is also the doctest-block entry point.

## Solution

Widen each `Args:` entry's one line to name both node kinds, e.g.:

```
        Args:
            node: The literal block node, or a doctest block delegated here
```

This is documentation text only inside a docstring, changes no behaviour, and needs no test.

## Why it was deferred

D-14: Phase 75 is prep-only. Touching `typsphinx/` here would force SC4's entire green proof to
be re-taken on a changed tip — both full pytest runs, the clean `docs-html` and `docs-pdf` builds,
the `linkcheck` run, and the single CI dispatch. Precedent: v0.7.1's Phase 46 D-03 declined a
`typst_authors` shim and D-27 declined a `builder.py` fix in the same phase for the same
prep-only-fence reasoning. MSG-06
(`.planning/todos/pending/2026-08-29-hardcoded-delimiter-path-fragments-in-translator-relative-path-debug-logs.md`)
stays pending for the identical reason.
