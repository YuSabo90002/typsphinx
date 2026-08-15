# Phase 53: Template Registry Foundation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-15
**Phase:** 53-Template Registry Foundation
**Areas discussed:** Registry key shape validation, Template path resolution failure, Global-value inheritance for user-defined keys, Byte-identity evidence (SC#2)

**Gray areas offered but not selected:** Validation scope (all declared keys vs. keys referenced by
element [4]) — this one surfaced anyway inside the template-path-resolution area and was decided
there (CONTEXT.md D-05).

---

## Registry key shape validation

### Q1 — Which validation style?

| Option | Description | Selected |
|--------|-------------|----------|
| Denylist enumeration only | Judge each of ROADMAP SC#4's 7 cases individually, case-specific error message (PITFALLS.md recommendation) | ✓ |
| Denylist + allowlist catch-all | Per-case messages first, then `re.fullmatch(r"[A-Za-z0-9_-]+", key)` as a backstop; no gap from an incomplete enumeration, but rejects non-ASCII keys and `my.template` | |
| Allowlist only | `re.fullmatch(r"[A-Za-z0-9_-]+", key)` alone (STACK.md recommendation, following `derive_typst_lang()`'s `re.fullmatch(r"[a-z]{2,3}")`) | |

**User's choice:** Denylist enumeration only.
**Notes:** The two research documents disagreed — STACK.md line 36 and lines 63-65 recommend the
allowlist; PITFALLS.md "Pitfall 1" and ROADMAP SC#4 enumerate the denylist. The divergence was
surfaced as measured fact before the question was asked.

### Q2 — Which shapes beyond SC#4's 7 cases?

| Option | Description | Selected |
|--------|-------------|----------|
| Windows-illegal + control characters | `< > : " | ? *` and 0x00–0x1F. `paper:v2` creates a directory on Linux and fails only on the windows-latest lane; `_is_drive_qualified()` only matches a leading `X:` so it lets `paper:v2` through | |
| Leading dot (`.hidden`) | Produces a dotfile bundle directory; STACK.md explicitly suggests rejecting a leading `.` | |
| Interior whitespace (`paper v2`) | Legal on every filesystem; Typst's `#import "…"` is a quoted string so it works as a path too | |
| Add nothing | SC#4's 7 cases exactly; do not exceed the roadmap text | ✓ |

**User's choice:** Add nothing.
**Notes:** The Windows-illegal-character gap was recorded as a deferred idea rather than dropped.

### Q3 — Error reporting shape?

| Option | Description | Selected |
|--------|-------------|----------|
| Same shape, independent raise | Accumulate all failures and raise once, mirroring `_validate_output_path_collisions()` (builder.py:606-612), but as its own `ExtensionError` | ✓ |
| Merge into the collision validator's `failures` list | One `ExtensionError` per build covering both classes, at the cost of changing an existing method's responsibility and message text | |
| Raise immediately on the first failure | Minimal implementation; departs from the repository's accumulate precedent and forces repeated builds to fix several bad entries | |

**User's choice:** Same shape, independent raise.
**Notes:** `_validate_output_path_collisions()` was read directly before the options were written —
it builds a `failures` list and raises `f"typst: {len(failures)} output path collision(s): {summary}"`.

### Q4 — Case handling of the reserved `"typst"` key?

| Option | Description | Selected |
|--------|-------------|----------|
| Judge CONF-16 by casefold | `"Typst"`/`"TYPST"` also rejected as reserved-key violations, catching the Phase 54 bundle collision here | |
| Include the built-in key in the case-collision comparison set | Same rejection, reported as a CONF-18 case collision instead of a CONF-16 reserved-key error | |
| Reserve literal `"typst"` only | `"Typst"` passes as an ordinary user-defined key; CONF-18 compares registered keys only and the synthesized built-in is not one | ✓ |

**User's choice:** Reserve literal `"typst"` only.
**Notes:** The consequence was stated back before moving on — on case-insensitive filesystems
(macOS/Windows defaults) `_template/Typst/` and `_template/typst/` are the same directory, so this
slips past Phase 53. Recorded as a deferred item routed to Phase 54.

---

## Template path resolution failure

### Q1 — What predicate implements CONF-17?

The first framing of this question (declared-string separator check / normalized-parent-equals-srcdir /
resolved-file's-parent) was **rejected by the user**: *"本質的には template でソースファイルが選ばれるのを
防ぐのが目的だが、そういう目線で選択肢がないか？"* — the options had been derived from the roadmap's
wording rather than from the harm the requirement exists to prevent. The question was rebuilt around
the goal, with a measured divergence table showing where the candidate predicates actually differ.

| Option | Description | Selected |
|--------|-------------|----------|
| Bundle must be a strict descendant of srcdir | One predicate catches srcdir itself, `./base.typ`, `../base.typ`, srcdir's siblings and absolute paths; matches PROJECT.md's "srcdir-relative local .typ" definition but withdraws absolute paths that work today | |
| Reject only srcdir itself and its ancestors | Catches every case where the source tree becomes the bundle; `../shared/tpl.typ` and absolute paths stay legal because copying a bounded `shared/` is not the harm | ✓ |
| Reject when the bundle contains `source_suffix` files | Most literal reading of "prevent source files being selected", but needs an FS walk, cannot be a string-shape test, and lets a srcdir with no top-level `.rst` through | |

**User's choice:** Reject only srcdir itself and its ancestors.
**Notes:** The "declared string has no separator" formulation was dropped before the second round —
`../base.typ` slips through it and would copy the whole project, which is strictly worse than the
case CONF-17 names. Measured while building the table: `os.path.join(srcdir, "/abs/x.typ")` returns
`/abs/x.typ`, so absolute template paths are functional today.

### Q2 — A registry `template` that does not exist?

| Option | Description | Selected |
|--------|-------------|----------|
| ExtensionError for user-defined keys only | Fail loud on the new config surface; `"typst"` keeps today's warn-and-fall-back | ✓ (Claude's recommendation, requested by the user) |
| Keep warn+fallback for all keys | No requirement covers this case, so the roadmap text is not exceeded; but a typo'd key silently renders with `base.typ` | |
| ExtensionError for all keys | One rule, but flips an existing `conf.py` with a typo'd `typst_template` from building to failing | |

**User's choice:** "おすすめ" — deferred to Claude's recommendation, which was option 1.
**Notes:** Rationale given before proceeding: option 3 breaks Phase 53's defining "changes no output"
invariant and would need a CHANGELOG entry; option 2 gets worse in Phase 54, where the fallback would
copy `typsphinx/templates/` into `_template/<user-key>/` and let the user believe their own template
was used. `"typst"` is *defined* as deferring to today's global configuration, which includes today's
warn+fallback semantics.

### Q3 — Which keys does validation cover?

| Option | Description | Selected |
|--------|-------------|----------|
| Shape/xor/reserved on all keys, FS existence check on used keys only | Restricts the I/O to what is needed | |
| Validate every declared key | Order-independence trivial; fixtures need not touch `typst_documents`; a broken unused definition stops the build | ✓ (Claude's recommendation, requested by the user) |
| Validate only keys referenced by element [4] | Lets users park spare definitions; a broken one is found only when element [4] is edited | |

**User's choice:** "おすすめ" — deferred to Claude's recommendation, which was option 2.
**Notes:** Rationale: the existence check is a few `os.path.isfile` calls, and PROJECT.md's own v0.9.0
text states "One code path is worth more than the exception".

### Q4 — element [4] present but not a `str`?

| Option | Description | Selected |
|--------|-------------|----------|
| Same CONF-14-class ExtensionError | Reported as "this entry names something that is not a registered key", with the value and the registered keys named | ✓ |
| Join the existing warning + skip contract | Extend `_is_usable_typst_documents_entry()`; the entry is dropped with a warning and produces no wrapper | |
| Treat as unspecified (`"typst"`) | Widest reading of TPL-04; a typo would silently render with the default template | |

**User's choice:** Same CONF-14-class ExtensionError.
**Notes:** Measured first — `_is_usable_typst_documents_entry()` (builder.py:115-166) checks only
truthiness, `len >= 2`, and `isinstance(entry[0], str)`; element [4] is type-checked nowhere. Its
docstring states that a genuinely different usability question must get its own named predicate.

---

## Byte-identity evidence (SC#2)

| Option | Description | Selected |
|--------|-------------|----------|
| One-off evidence artifact only | `53-RED-EVIDENCE.md` with before/after commit SHAs, per-file SHA-256, PDF page counts | ✓ (Claude's recommendation, requested by the user) |
| Evidence artifact plus a permanent golden gate | Adds committed golden `.typ` fixtures for the four shapes; Phase 54 would churn every one of them | |
| Permanent golden gate only | Runs in CI forever, but a golden generated from post-change code cannot prove pre-change identity | |

**User's choice:** "おすすめ" — deferred to Claude's recommendation, which was option 1.
**Notes:** Both precedents were measured before the question: seven `*-RED-EVIDENCE.md` artifacts
under `.planning/milestones/v0.8.0-phases/`, and eight test files using `hashlib`/snapshot assertions.
Decisive argument: the standing regression net already exists — the 31 test files asserting the root
`_template.typ` must pass unchanged, which is what "behaviour-preserving" means here.

---

## Global-value inheritance for user-defined keys

The first framing of these two questions was **rejected by the user** (*"質問の意味がよくわからん"*).
They were re-asked with concrete `conf.py` examples and a table of the exact Typst lines each choice
emits, after measuring `TemplateEngine.__init__` and `render()`.

### Q1 — Does a user-defined key omitting `template_function` inherit the global value?

| Option | Description | Selected |
|--------|-------------|----------|
| `project` (no inheritance) | Registry definitions are self-contained; omission means `None`, and `render()` already falls back to the literal `"project"` at both the `#import` and `#show:` sites | ✓ |
| `ieee` (inherit the global) | Global `typst_template_function` becomes every key's default, overridable per definition; less repetition but the definition alone no longer tells you which function is called | |

**User's choice:** `project` — no inheritance.
**Notes:** Measured before asking — template_engine.py:654 and :664 both use
`self.typst_template_function_name or "project"`, so "omitted" already has a defined meaning.

### Q2 — Which keys receive global `typst_template_mapping`?

| Option | Description | Selected |
|--------|-------------|----------|
| `title:` — pass it to the `"typst"` key only | Treated as one of the four global values TPL-03 says `"typst"` resolves to; user-defined keys get `DEFAULT_PARAMETER_MAPPING`, and Future requirement TPL-06 gains no new surface | ✓ |
| `doc_title:` — pass it to all keys | Keeps writer.py:348's current unconditional shape; smallest code change, but a project with a global mapping cannot give a user-defined key the default naming | |

**User's choice:** `title:` — `"typst"` only.
**Notes:** Confirmed afterwards against the requirement text: REQUIREMENTS.md's TPL-03 names
`typst_template_mapping` among the four globals `"typst"` resolves to, while `typst_package_imports`
is absent from that list and PROJECT.md locks it separately as global-for-every-document. The two
values are distinguished by the requirements themselves, so this decision is not inconsistent with
"`package_imports` and `elements` stay global".

---

## Claude's Discretion

- Registry resolver module placement (research recommends a new `typsphinx/template_registry.py`).
- The exact widening of `TemplateEngine.resolve_template()` so the resolved `Path` is recoverable —
  a `TemplateResolution` field versus a separate method — subject to keeping the single priority walk.
- How the once-per-build resolution result reaches `render_wrapper()` (builder attribute vs. parameter).
- Exact error message wording.
- Test file naming and placement.

## Deferred Ideas

- **Phase 54:** `"Typst"` and the built-in `"typst"` resolve to the same `_template/<key>/` directory
  on case-insensitive filesystems. Consequence of the Q4 choice in the key-validation area.
- **Later phase:** reject Windows-illegal characters (`< > : " | ? *`) and control characters in
  registry keys.
- **Adjacent cleanup:** `writer.py:170-216` `_compute_template_import_path()` is dead code (flagged by
  `.planning/research/ARCHITECTURE.md` §2); not this milestone's responsibility.
