# Phase 45 Plan 04 — Gate Evidence: QUA-03 Comment-Balance Scan

**Commit SHA scanned:** `d37a3ab84449e89379892cedf4a71419ec206ba4`

Measured against `.planning/PROJECT.md` at the commit above (Task 1's `derive_typst_lang`
refactor commit; `.planning/PROJECT.md` itself is untouched by that commit or any other
commit in this plan).

## Scan script (verbatim)

This is a throwaway diagnostic script — it is not committed to `tests/` or `scripts/` per
D-07, which declines a standing recurrence guard. It is reproduced here in full so the
measurement is reproducible without adding a standing guard.

```python
import pathlib, re, sys

def scan(text):
    """Fence- and backtick-aware opener-stack walk over HTML comment markers.

    Toggles a fenced-block flag on lines whose stripped form starts a fence
    (``` or ~~~), skips lines inside a fence, strips inline backtick spans
    from each remaining line, then scans left to right for <!-- / --> tokens,
    pushing each opener's line number and popping on each closer (LIFO).
    """
    stack, openers, closers, in_fence = [], 0, 0, False
    for idx, line in enumerate(text.split("\n"), start=1):
        s = line.strip()
        if s.startswith("```") or s.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        stripped = re.sub(r"`{1,2}[^`\n]*?`{1,2}", "", line)
        for m in re.finditer(r"<!--|-->", stripped):
            if m.group(0) == "<!--":
                openers += 1
                stack.append(idx)
            else:
                closers += 1
                if stack:
                    stack.pop()
    return openers, closers, stack


if __name__ == "__main__":
    text = pathlib.Path(".planning/PROJECT.md").read_text(encoding="utf-8")
    o, c, stack = scan(text)
    print(f"opener_count={o} closer_count={c} residual_stack={stack}")

    # Self-check (a): same-line pair contributes nothing to residual stack
    sa_o, sa_c, sa_stack = scan("x <" + "!-- inline -" + "-> y")
    print(f"self_check_a: openers={sa_o} closers={sa_c} residual={sa_stack} "
          f"pass={sa_stack == []}")

    # Self-check (b): zero-opener input yields (0, 0), no error
    sb_o, sb_c, sb_stack = scan("no markers here")
    print(f"self_check_b: openers={sb_o} closers={sb_c} residual={sb_stack} "
          f"pass={(sb_o, sb_c) == (0, 0)}")

    # Self-check (c): two openers, one closer -> one residual, ascending order,
    # closer pairs with the most recently unmatched opener (LIFO)
    sc_text = "<" + "!-- a\n<" + "!-- b\n--" + ">\n"
    sc_o, sc_c, sc_stack = scan(sc_text)
    print(f"self_check_c: openers={sc_o} closers={sc_c} residual={sc_stack} "
          f"pass={len(sc_stack) == 1 and sc_stack == sorted(sc_stack)}")
```

## Output on `.planning/PROJECT.md`

```
opener_count=34 closer_count=34 residual_stack=[]
self_check_a: openers=1 closers=1 residual=[] pass=True
self_check_b: openers=0 closers=0 residual=[] pass=True
self_check_c: openers=2 closers=1 residual=[1] pass=True
```

- **Opener count:** 34
- **Closer count:** 34
- **Residual stack:** `[]` (length 0) — zero unterminated openers.

## Self-check results

| Check | Scenario | Result | Pass |
|---|---|---|---|
| (a) same-line pair | A single line carrying both an opener and its closer | residual `[]` | ✅ |
| (b) zero-opener input | A line with no comment markers at all | `(0, 0)`, no error | ✅ |
| (c) LIFO / ascending order | Two openers followed by one closer | one residual opener (line 1), ascending order, most-recent-unmatched-opener pairing | ✅ |

All three self-checks pass, confirming the scan's pairing semantics (LIFO, same-line
neutrality, empty-input safety) before trusting its verdict on the real file.

## D-08 finding

The two unterminated openers the source todo
(`.planning/todos/pending/2026-07-29-project-md-unterminated-html-comments.md`) recorded at
commit `279aea5` (its lines 492 and 506) were closed by commit `43a2a78`:

```
commit 43a2a787a0c5abd5061e0c31f951fd2b6361668f
Author: yuta <yusabo90002@gmail.com>
Date:   Mon Aug 3 20:28:55 2026 +0900

    docs(41-03): terminate PROJECT.md's two unterminated HTML comments (D-13)

    Mechanical scan (regex-count <!-- vs --> markers, checking each opener
    has a closer before the next opener) found exactly two unterminated
    comment-openers in .planning/PROJECT.md, at lines 761 and 775 (moved
    from CONTEXT.md's recorded 492/506, measured at commit 279aea5, since
    the file has grown ~250 lines):

    - Line 761: "<!-- Prior: 2026-07-23 at v0.6.2 milestone close ... Prior
      footer retained below.*" (v0.6.2 close entry)
    - Line 775: "<!-- Prior: 2026-07-11 after Phase 10 (Version-String Fix
      + v0.5.0 Release) complete ... mirroring the v0.4.4 precedent.*"
      (v0.5.0 Phase 10 entry)

    Both are single-line "Prior footer" comments whose content already
    ends with a closing italic marker (*); appended " -->" to close each,
    ...
```

Confirmed directly via `git show 43a2a78` (verbatim above, not copied from a secondary
claim). This is **Phase 41, plan 03, decision "D-13"** — the commit message names its own
decision ID, states the exact pre-fix line numbers (761, 775, moved from the source todo's
492/506 by file growth), the exact content of each comment, and the mechanical scan method
used to find them. The commit is dated 2026-08-03.

**This was a deliberate, self-documented, attributed repair — not an incidental one.**
`45-CONTEXT.md`'s D-07 phrasing ("later milestone closes rewrote that footer tail and closed
them incidentally") is corrected here: the repair itself was intentional, named, and
attributed to a specific decision (D-13) inside a specific plan (41-03). The only sense in
which "incidental" applies is **timing** — the fix landed as a side effect of a
release-prep-adjacent plan's footer-tail rewrite, not inside a dedicated hygiene phase created
to close this specific defect. D-08 exists precisely to distinguish "someone fixed it
deliberately" from "it closed by accident of unrelated editing", and the evidence above shows
the former: the fix was intentional and attributed, even though the *phase* that produced it
was not itself scoped around this defect.

## Disposition

- **SC#4 is satisfied on verification alone.** The whole-file opener-stack scan finds zero
  residual unterminated `<!--` openers in `.planning/PROJECT.md` at the commit named above.
- **No file was edited.** `.planning/PROJECT.md` is unmodified by this plan; QUA-03 closes on
  measurement, per D-07.
- **No recurrence guard was added.** Per D-07, no comment-balance check is added to
  `tests/` or `scripts/` — the scan above is a one-off diagnostic recorded here as evidence,
  not committed as a standing guard.
- **If the drift channel ever reopens**, D-09 records the binding design constraint any
  future guard must satisfy: a naive `<!--`/`-->` token-count comparison is NOT valid,
  because it cannot distinguish real openers from backticked mentions inside prose — two live
  planning documents describing QUA-03 itself (`.planning/REQUIREMENTS.md:141` and
  `.planning/ROADMAP.md:731`) are measured false-positive sites for exactly that reason. Any
  future guard must walk openers/closers with fence and inline-backtick exclusion, as this
  scan does.
