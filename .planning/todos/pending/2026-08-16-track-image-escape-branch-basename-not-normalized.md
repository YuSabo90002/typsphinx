---
created: 2026-08-16
title: "`_track_image()`'s escape branch builds its relocation key with `path.basename()` on the RAW URI, so a backslash-shaped absolute image URI emits an `image(\"...\")` path Typst refuses to compile"
area: builder
resolves_phase: unassigned
severity: major
source: Phase 55 code review CR-01 + WR-01
  (.planning/phases/55-v0-8-0-derived-defects/55-REVIEW.md, including the
  orchestrator addendum that re-measured CR-01 against the pre-fix tree);
  owner decided 2026-08-16 to file rather than fix inside Phase 55, because the
  defect is pre-existing and falsifies neither SC#4 nor SC#5
files:
  - typsphinx/builder.py  # _track_image() escape branch -- path.basename(resolved_uri) on the raw URI
  - typsphinx/builder.py  # _track_image() escape branch -- {digest}-{basename} key has no length bound
  - typsphinx/translator.py  # visit_image() -- image("{adjusted_uri}") emitted with no escape_typst_string()
---

## Problem

Three related gaps in one path, all on the same URI as it travels from
`TypstBuilder._track_image()` to `TypstTranslator.visit_image()`.

### 1. Non-normalized basename (CR-01)

`_track_image()`'s escape branch builds its relocation key as:

```python
digest = hashlib.sha1(resolved_uri.encode("utf-8")).hexdigest()[:8]
key = f"{RESERVED_IMAGE_NAMESPACE}/{digest}-{path.basename(resolved_uri)}"
```

On a POSIX build host `path.basename` is `posixpath.basename`, which splits only on `/`. A
backslash-shaped absolute URI therefore has **no** basename to take — the whole URI comes
back — and the raw backslashes end up inside the key.

This is the same shape of gap BLD-09 closed one call earlier in the same method: the gate now
normalizes (`_is_absolute_image_uri()`), the key construction two lines later still does not.

**Measured on the merged Phase 55 tree** (doctreedir `/build/doctrees`):

| shape | `_is_absolute_image_uri` | escape branch | key contains `\` |
|---|---|---|---|
| unc `\\server\share\chart.png` | True | True | **yes** |
| driveless-absolute `\typsphinx_test\chart.png` | True | True | **yes** |
| drive-qualified `C:\typsphinx_test\chart.png` | True | True | **yes** |
| posix-absolute `/tmp/typsphinx_test/chart.png` | True | True | no |
| ordinary-relative `images/chart.png` | False | — | — |

### 2. The emitted path is never escaped

That key becomes `node["uri"]`, and `visit_image()` emits it directly:

```python
adjusted_uri = self._compute_relative_image_path(uri, current_docname)
self.add_text(f'image("{adjusted_uri}"')
```

with no `escape_typst_string()` call — unlike every other user-controlled string this area
routes through an escaping transform. Typst rejects the result outright:

```
$ printf '#image("_typst_converted/70c5653b-\\\\typsphinx_test_55_03_server\\share\\chart.png")\n' > probe.typ
$ python -c "import typst; typst.compile('probe.typ', output='probe.pdf')"
COMPILE ERROR: TypstError path must not contain a backslash
```

### 3. No length bound on the key (WR-01)

The relocated filename is `{digest8}-{basename}` — a fixed 9-byte prefix plus an uncapped
basename. ext4 / APFS / NTFS all cap a path component at 255. A basename already near that
limit now exceeds it; and per gap 1 the "basename" can be an entire absolute URI. That
surfaces later and less legibly than gap 1 — an `ENAMETOOLONG` `OSError` at
`copy_image_files()` time rather than a compile error.

## Not a Phase 55 regression

Re-measured at Phase 55 close by running the pre-fix `builder.py` (commit `40b92fc6`) and the
merged one side by side against the same UNC URI:

```
PRE-FIX  node['uri'] = '\\typsphinx_test_55_03_server\share\chart.png'
POST-FIX node['uri'] = '_typst_converted/70c5653b-\\typsphinx_test_55_03_server\share\chart.png'
```

The backslashes reached `image(...)` — and Typst refused the compile — **before** Phase 55 too;
pre-fix the URI simply was not classified as absolute on POSIX and fell through to
`self.images[resolved_uri] = ""` with `node["uri"]` untouched. The unnormalized
`path.basename()` call is itself pre-existing
(`40b92fc6:typsphinx/builder.py:1589`). IMG-03 added the digest prefix ahead of it and did not
change its normalization.

What Phase 55 changed for this input class: the emitted path now carries the reserved namespace
and a digest, and a `could not rehome image URI` warning is logged where there was previously
silence. The compile still fails, identically.

Independently reproduced twice at phase close — by the code reviewer and, separately, by the
phase verifier (`55-VERIFICATION.md` § "CR-01 independent reproduction").

## Fix sketch

Gap 1 is one line, and the smallest useful step:

```python
safe_basename = path.basename(resolved_uri.replace("\\", "/"))
key = f"{RESERVED_IMAGE_NAMESPACE}/{digest}-{safe_basename}"
```

But that alone does not make the emitted path safe — it only removes backslashes this one
branch introduces. Whoever takes this should decide whether gaps 2 and 3 belong in the same
slice: escaping at the `image("...")` emission site is the general guard, and the length bound
must keep the digest as the collision anchor (truncating the basename alone would reintroduce
the collision IMG-03 just closed).

Whatever lands must carry a real `typst.compile()` gate. Neither of BLD-09's new tests renders
or compiles its result, which is why this survived Phase 55's own suite — the property is
invisible to an assertion that stops at `node["uri"]`.

## Owner decision (2026-08-16)

**Timing — AMENDED 2026-08-16, same day, before anything was created.** The final decision is:
**defer to the NEXT milestone. Nothing is inserted into v0.9.0.**

~~**Timing: close inside v0.9.0 via an INSERTED phase (56.1), not after the release.**~~
SUPERSEDED. The earlier reading of this decision is retained above struck-through so a future reader
does not re-derive the abandoned branch from a half-memory. No `56.1` was ever created — the ROADMAP,
`STATE.md`, and `.planning/phases/` carry no trace of it, so the amendment costs nothing but this
paragraph.

What survives from the superseded reading, because it was measured rather than assumed: Phase 57's
SC#4 requires that `git diff` over the release-prep phase show **no unintended `typsphinx/` change**.
That is why this cannot be fixed inline on the current branch under any timing — it is an argument
against inline editing, not an argument for insertion, and it still holds.

**Scope: "CI の Windows ビルドが通ればまあ一旦良い。残滓は todo へ."** The acceptance bar is the
3-OS CI lane — `windows-latest` included — green over the fix, not exhaustive closure of all three
gaps. Whatever is not needed to reach that bar is filed forward as a new todo rather than folded in.

**Recorded caveat, for whoever plans this at the next milestone** — the bar as literally stated is not self-sufficient and
must not be read as "run CI, observe green, done": all three gaps are **latent**, covered by no test
today, so the `windows-latest` lane is already green at HEAD and would stay green if nothing were
fixed. The bar only becomes meaningful in its RED-first form: new gates that **fail** against the
unfixed tree first, then pass on `windows-latest`. Per this todo's own §"Fix sketch", at least one
of those gates must be a real `typst.compile()` — an assertion that stops at `node["uri"]` cannot
see the property that failed here, which is exactly why this survived Phase 55's suite.

Expected residue → todo: gap 3 (WR-01, the unbounded `{digest}-{basename}` key length) has no
compile-visible symptom and will not be forced out by a compile gate, so it is the likeliest item to
file forward. Gap 2 (`escape_typst_string()` at the `image("...")` emission site) is the general
guard; whether it is needed to reach the bar depends on what the RED gate is written against.

## Related

- `.planning/todos/pending/2026-08-16-escapes-outdir-isabs-not-backslash-normalized.md` — the
  sibling non-normalized predicate in `_escapes_outdir()`, filed by plan `55-03` while closing
  BLD-09. Same family; consider closing both together.
