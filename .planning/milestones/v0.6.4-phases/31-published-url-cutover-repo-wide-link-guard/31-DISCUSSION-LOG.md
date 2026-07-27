# Phase 31: Published-URL Cutover + Repo-Wide Link Guard - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-26
**Phase:** 31-published-url-cutover-repo-wide-link-guard
**Areas discussed:** Link checker tooling, RTD URL shapes to burn in, #119 close and About sequencing, INTEGRATIONS.md rewrite depth

---

## Link checker tooling (CI-05)

### Tool selection

| Option | Description | Selected |
|--------|-------------|----------|
| lychee (recommended) | Rust tool + official lychee-action v2. Scans md/HTML/rst/plain text; TOML digestible as text. `.lycheeignore` (regex) URL excludes | ✓ |
| Custom Python script | Zero external-action dependency, but retries/false-positive hardening become self-maintained | |
| Other prebuilt Action | markdown-link-check etc. are mostly markdown-only — poor fit for pyproject.toml | |

### Trigger

| Option | Description | Selected |
|--------|-------------|----------|
| Weekly + PR both (recommended) | Covers both time-based rot and new introductions | |
| Weekly only (drift.yml shape) | One workflow, zero PR noise; detection lags up to a week | |
| PR/push only | Catches commit-borne breakage; external rot with no commits in flight goes undetected | ✓ |

**Notes:** Owner accepted the undetected-rot-between-pushes limitation. Future extension is a one-block `schedule:` addition (recorded in deferred).

### Scan scope

| Option | Description | Selected |
|--------|-------------|----------|
| Whole repo minus excludes (recommended) | Full scan; path excludes: .planning/, CHANGELOG.md, etc. | ✓ |
| Enumerate target files | Predictable, but new files outside the list are permanently unseen (reproduces this milestone's failure structure) | |
| Whole repo, minimal excludes | Keeping CHANGELOG.md scanned goes permanently red after Phase 32 | |

### Failure presentation

| Option | Description | Selected |
|--------|-------------|----------|
| Red non-required check (recommended) | Fails normally, never registered as Required. Simple, hard to miss | ✓ |
| continue-on-error always green | Invisible without opening logs — contradicts CI-05's purpose | |
| Red ✕ + summary comment | Most visible, but needs extra permissions and implementation | |

### Negative-control evidence form (SC#1)

| Option | Description | Selected |
|--------|-------------|----------|
| CI run + transcription (recommended) | Commit links.yml first, let CI go red on the pre-rewrite tree, transcribe run URL + flagged URLs into VERIFICATION.md | ✓ |
| Local run paste | Phase 29 D-15 form. Faster, but indirect as proof that CI detects it | |
| Both | Strongest, most work | |

### Workflow location

| Option | Description | Selected |
|--------|-------------|----------|
| New links.yml (recommended) | Standalone, same shape as drift.yml; non-Required is structurally self-evident | ✓ |
| Job in ci.yml | ci.yml is where Required checks live — "this one job is non-required" gets confusing | |
| Job in docs.yml | Entangles with a file Phase 32 will heavily cut | |

### False-positive posture

| Option | Description | Selected |
|--------|-------------|----------|
| Lenient settings (recommended) | Retries + accept 429 + timeout. Exact values Claude's discretion | ✓ |
| Strict defaults | More misses become failures; erodes trust in an advisory job | |

### Relative-link checking

| Option | Description | Selected |
|--------|-------------|----------|
| Check them (recommended) | Local file-link breakage caught by the same job | |
| HTTP(S) only | Scope pinned to CI-05's wording | ✓ |

**Notes (user-initiated constraint):** "It's Rust, so I don't want to run it locally" — all
lychee execution is CI-only; tuning via branch push → CI observation. `curl` is fine locally.
Saved to memory.

---

## RTD URL shapes to burn in (DOC-09)

### Deep-link version segment

| Option | Description | Selected |
|--------|-------------|----------|
| /en/latest/ everywhere (recommended) | Resolves now, satisfies SC#2; tracks main; no Phase 33 rewrite needed | ✓ |
| latest now → stable in Phase 33 | Two-step churn plus a second verification pass in Phase 33 | |

### Top-level link URL

| Option | Description | Selected |
|--------|-------------|----------|
| Bare root (recommended) | Auto-follows the Default Version flip; no re-editing | ✓ |
| /en/latest/ uniform | One redirect faster but pinned to latest forever | |

### Badge

| Option | Description | Selected |
|--------|-------------|----------|
| RTD official badge (recommended) | passing/failing reflects the real build — the badge itself becomes monitoring | ✓ |
| Keep shields.io static badge | Always blue; reflects nothing | |

### ja link addition

| Option | Description | Selected |
|--------|-------------|----------|
| Add it (recommended) | One line to /ja/latest/; discoverability for Phase 30.1's deliverable; +1 URL to verify | ✓ |
| Don't add | Leave ja discovery to RTD's flyout | |

---

## #119 close and About sequencing (DOC-10)

### Timing

| Option | Description | Selected |
|--------|-------------|----------|
| About immediate + close within Phase 31 (recommended) | Satisfies SC#4 inside the phase | |
| About immediate + close after merge | Symptom resolved instantly; close once everything is on main. SC#4's close half becomes a handoff | ✓ |
| Both after merge | put101's 404 lingers that much longer | |

**Notes:** Owner accepted that SC#4's close half moves from Phase 31 verification to the
milestone-close handoff list (recorded as CONTEXT.md D-15).

### Reply posting flow

| Option | Description | Selected |
|--------|-------------|----------|
| Draft → owner review → post (recommended) | Same flow as the PR#98 precedent | ✓ |
| Fix the draft during Phase 31 | Mechanical posting later, but state changes at close time force a re-review anyway | |
| Claude posts directly | Outward-facing text with no review | |

### Reply content scope

| Option | Description | Selected |
|--------|-------------|----------|
| Fulfillment report only (recommended) | New URL + the fixes delivered, kept short | ✓ |
| + migration background | Announcement value, longer reply | |

---

## INTEGRATIONS.md rewrite depth

### Depth

| Option | Description | Selected |
|--------|-------------|----------|
| ROADMAP-minimum + new-integration additions (recommended) | Hosting/CI/env-var paragraphs + RTD/translations/links.yml sections; full refresh left to /gsd-map-codebase | |
| Full refresh | Re-analyze the whole file, update Analysis Date; partial re-staling by Phase 32 accepted | ✓ |
| URL swap only | Falls short of ROADMAP Notes' "paragraph-level rewrite" finding | |

### Exclusion carve-out for links.yml

| Option | Description | Selected |
|--------|-------------|----------|
| Keep as is (recommended) | .planning/ excluded wholesale; INTEGRATIONS.md URLs verified once by execution-time curl | ✓ |
| Un-exclude .planning/codebase/ only | Puts the 7 maps under ongoing watch, but widens the false-positive surface | |

---

## Claude's Discretion

- Exact lychee parameter values (retries, timeout, accepted statuses, caching)
- Exclusion mechanics (`--exclude-path` vs `.lycheeignore`) and whether tests/fixtures fake URLs need excluding
- Placement and wording of the one-line ja link in README
- Deep-link target-path existence checks on RTD and shape adjustments
- Section structure of the INTEGRATIONS.md full refresh
- #119 close-reply draft wording (owner reviews before posting)

## Deferred Ideas

- Weekly scheduled run for external-link rot (one-block `schedule:` addition to links.yml)
- Repo-internal relative file-link checking
- Ongoing link watch over `.planning/codebase/`
- Revisiting the CHANGELOG.md github.io keep-as-history decision
