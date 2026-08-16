---
phase: 55
slug: v0-8-0-derived-defects
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: 2026-08-16
---

# Phase 55 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

Register origin: authored at plan time. All four plans (`55-01`…`55-04`) carried a
parseable `<threat_model>` block; this file consolidates them and records the
verification of each mitigation against the merged implementation.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| maintainer-authored source tree (docnames, section ids, domain ids) → `TypstTranslator._sanitize_label` | Arbitrary author-controlled strings cross into the Typst label alphabet. Trusted in this project's model, but a non-injective encoding turns an authoring accident into silently wrong output. | docnames, section/domain identifiers |
| emitted `.typ` label bytes → `typst.compile()` → PDF link destinations | The compiled artifact a reader downloads. A label collision is invisible at every layer above this one. | label names, link destinations |
| maintainer-authored docnames and toctree shape → `make_include_edge_key` / `derive_master_edge_keys` | Author-controlled strings and graph shape cross into the published Typst `state` array and every content file's guard condition. | docnames, toctree edges |
| published `state` array → per-emission-site `include()` guard at Typst compile time | Decides which document's content lands in which master. A collided key changes that decision with no diagnostic. | include-edge keys |
| `derive_master_edge_keys` → Sphinx's build loop | An uncaught exception here becomes the user's whole build failure; its TYPE decides clean message vs. Python traceback. | control flow / error type |
| third-party Sphinx extension → `node["uri"]` / `node["candidates"]` → `_track_image()` | The one place an absolute or rooted path enters this builder's own path arithmetic. | image URIs (may embed author filesystem layout) |
| `self.images` keys → `copy_image_files()` → `<outdir>` | Every tracked key becomes a destination path under the output directory — unless the platform join discards `outdir` for a rooted key. | file destination paths |
| shipped behaviour → published `CHANGELOG.md` | The only place two of this phase's output changes (a label name, a relocated image filename) are announced. | user-facing release notes |
| measured gate results → `55-04-EVIDENCE.md` → phase completion | What a later reviewer and the milestone audit treat as the record that this phase closed green. | audit evidence |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-55-05 | Tampering | `_track_image()` absolute-URI gate — a rooted driveless URI skipping the gate stays in `self.images`, and the Windows destination join discards `outdir` for a rooted second argument, writing at the drive root | high | mitigate | `_is_absolute_image_uri()` (`typsphinx/builder.py:121`) backslash-normalizes before applying `posixpath.isabs(...) or _is_drive_qualified(...)`; `_track_image()` routed onto it at `builder.py:1653`, so every rooted shape enters the relocate branch and is re-keyed under `RESERVED_IMAGE_NAMESPACE` | closed |
| T-55-01 | Tampering | `TypstTranslator._sanitize_label` — a non-injective label encoding lets a reference resolve to a same-spelled decoy in another document | medium | mitigate | `_LABEL_TOKEN_INTRODUCER_RE` pre-pass (`typsphinx/translator.py:59`, applied at `:5220`) escapes the token's own introducer; proved by decoder round-trip in `tests/test_sanitize_label_injectivity_unit.py` | closed |
| T-55-02 | Tampering | `make_include_edge_key` — two structurally different edges collapsing onto one key make a dark guard fire, duplicating or substituting content | medium | mitigate | `_escape_include_edge_separators()` (`typsphinx/translator.py:210`) applied strictly after `escape_typst_string()` at the single derivation point (`:317`–`:320`); pinned by `tests/test_include_edge_separator_collision_gate.py` (real `typst.compile()`, PDF marker count) | closed |
| T-55-03 | Denial of Service | `derive_master_edge_keys`'s unbounded recursion — a deep toctree exhausts the interpreter stack and crashes the build with a raw traceback | medium | mitigate | `_MAX_INCLUDE_CHAIN_DEPTH = 500` (`translator.py:340`, re-measured in-worktree) with a named `sphinx.errors.ExtensionError` raised at `:414` | closed |
| T-55-04 | Tampering | escape-branch basename-only relocation key — two escaping images sharing a basename collapse onto one key, silently swapping images | medium | mitigate | Key is now a pure function of the whole URI: `hashlib.sha1(resolved_uri...)[:8]` prefix + basename under the reserved namespace (`builder.py:1700`–`:1703`); distinctness + purity tests in `tests/test_builder.py` | closed |
| T-55-09 | Information Disclosure | an unrehomed absolute URI reaching the emitted `.typ` leaks the author's absolute filesystem layout into published output | medium | mitigate | Same fix as T-55-05/T-55-04 — a relocated key carries only the reserved namespace, the digest prefix and the basename; the original directory path never reaches emitted output (the full URI appears only in a build-time warning to the author) | closed |
| T-55-12 | Repudiation | an evidence file whose counts were transcribed from a sibling summary rather than measured after the merge | medium | mitigate | `55-04-EVIDENCE.md` records post-merge, in-worktree command output; transcription forbidden by the plan's prohibition list | closed |
| T-55-13 | Information Disclosure | a user-visible output change shipping unannounced | medium | mitigate | `CHANGELOG.md` `### Fixed` announces all five defects (XREF-05, BLD-07, BLD-08, BLD-09, IMG-03); the two entries with an observable output change (label name; relocated image filename) say so explicitly | closed |
| T-55-07 | Repudiation | a raised message claiming a repeated document was detected when none was measured | low | mitigate | The `ExtensionError` message states only the depth reached, the bound, and the chain endpoints (`translator.py:415`–`:421`) — no repeated-document claim | closed |
| T-55-08 | Tampering | reliance on a Typst behaviour (the escaping character surviving in the string value) that a future release could change, silently returning the collision | low | mitigate | Hand-written Typst language probe compiling real source in `tests/test_include_edge_separator_collision_gate.py:273`–`:295`, so a Typst change fails loudly | closed |
| T-55-06 | Denial of Service | the label pre-pass regex running once per emitted label | low | accept | Bounded lookahead over a fixed character class, no nested quantifier over the same class, compiled once at import — see ACC-55-01 | closed |
| T-55-10 | Spoofing | truncating the relocation digest to 8 hex characters admits a residual collision chance | low | accept | 32 bits over the handful of escaping images in one build — see ACC-55-02 | closed |
| T-55-11 | Cryptography misuse (apparent) | a scanner flagging the SHA-1 call generically | low | accept | Non-cryptographic collision-avoidance key over a build-local path string — see ACC-55-03 | closed |
| T-55-14 | Tampering | the phase-completion step flipping a requirement's checkbox against a recorded decision | low | accept | Deliberately left to a later, readable diff — see ACC-55-04 | closed |
| T-55-SC | Tampering | npm/pip/cargo installs (all four plans) | low | accept | Zero packages installed this phase — see ACC-55-05 | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| ACC-55-01 | T-55-06 | `_LABEL_TOKEN_INTRODUCER_RE` is a bounded lookahead over a fixed character class with no nested quantifier over the same class, compiled once at module import; the measured cost is one extra linear scan per emitted label. No catastrophic-backtracking shape is introduced. | plan 55-01 threat model | 2026-08-16 |
| ACC-55-02 | T-55-10 | The relocation key's digest is truncated to 8 hex characters (32 bits) over the handful of escaping images in a single build, and reaching that branch already requires a third-party extension to place an absolute URI outside the doctree directory. Recorded as a flagged assumption, not measured; widening the truncation is a one-line change if a real collision is ever observed. | plan 55-03 threat model | 2026-08-16 |
| ACC-55-03 | T-55-11 | The `hashlib.sha1` call is a non-cryptographic collision-avoidance key over a build-local path string with no integrity, authentication or secrecy property. Python's built-in `hash()` is unusable (per-process randomization would change emitted filenames between builds). This project's ruff selection does not include the security rule set, and the reason is written at the call site so a future stricter scanner is answered by the code itself. | plan 55-03 threat model | 2026-08-16 |
| ACC-55-04 | T-55-14 | Flipping a requirement checkbox is not plan 55-04's transition to make; leaving `REQUIREMENTS.md` untouched keeps the later diff readable so an unauthorized flip stays visible. | plan 55-04 threat model | 2026-08-16 |
| ACC-55-05 | T-55-SC | Zero packages installed in this phase (binding constraint #11). `55-RESEARCH.md` § Package Legitimacy Audit records the gate as not applicable — every symbol reached for is Python stdlib (`re`, `hashlib`) or part of an already-declared dependency (`sphinx.errors`). `55-04-EVIDENCE.md` records the dependency-array diff. | plans 55-01…55-04 threat models | 2026-08-16 |

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-08-16 | 15 | 15 | 0 | /gsd-secure-phase (orchestrator, ASVS L1 grep-depth short-circuit) |

Verification depth: ASVS level 1, block on `high`. The register was authored at plan
time and `threats_open` evaluated to 0 at classification, so the L1 short-circuit applied
and no separate auditor subagent was spawned. Each `mitigate` disposition was confirmed
by reading the named symbol at its cited location in the merged working tree; each
`accept` disposition is carried into the Accepted Risks Log above.

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-08-16
