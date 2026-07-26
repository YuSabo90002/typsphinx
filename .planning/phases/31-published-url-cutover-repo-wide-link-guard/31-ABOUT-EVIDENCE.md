# Phase 31 Plan 02: About -> Website Evidence

Measured 2026-07-26. This file discharges ROADMAP Phase 31 success criterion 4's second half —
proof over real HTTP that the repository's About -> Website link resolves — and documents which
half of DOC-10 this plan deliberately does not close.

## 1. Before-value of `homepage`

Command:

```
gh api repos/YuSabo90002/typsphinx --jq '.homepage'
```

Output: (empty — field was JSON `null`)

Confirmed via a second, unambiguous read:

```
gh api repos/YuSabo90002/typsphinx | python3 -c "import json,sys; d=json.load(sys.stdin); print(repr(d.get('homepage')))"
```

Output:

```
None
```

This matches the planning-time reading recorded in `31-CONTEXT.md` D-14 (`null` at planning time,
2026-07-26) — the field was genuinely unset at execution time too, which is why GitHub's About
panel fell back to the stale GitHub Pages URL that Issue #119 reported as a 404.

## 2. The PATCH command issued

The local `gh` token carries the `repo` scope and the account holds `admin: true` on this
repository, so the API path was attempted first (per the plan's fallback ordering) and succeeded —
no owner-manual step was required.

Command:

```
gh api repos/YuSabo90002/typsphinx -X PATCH -f homepage='https://typsphinx.readthedocs.io/'
```

Result: HTTP 200, full repository object returned (truncated below to the relevant confirmation;
the call sends only the `homepage` field, so no other repository setting was touched).

Unrelated-fields check, taken both before and after the PATCH, to confirm the PATCH touched
nothing else:

```
gh api repos/YuSabo90002/typsphinx --jq '{description,private,archived,has_issues}'
```

Output (identical before and after):

```
{"archived":false,"description":"Sphinx extension for Typst output format support","has_issues":true,"private":false}
```

## 3. Read-back value

Command:

```
gh api repos/YuSabo90002/typsphinx --jq '.homepage'
```

Output:

```
https://typsphinx.readthedocs.io/
```

Byte-identical to the intended value: bare root, trailing slash, no `/en/` segment, no `/latest/`
segment — the form D-11 requires so Phase 33's Default Version flip (`latest` -> `stable`)
propagates here with zero re-editing.

## 4. Real-HTTP verification

The URL fetched below is not a string typed into this plan — it is the value read back from the
API in step 3, so this evidence proves the link a visitor actually clicks resolves.

### 4a. Following redirects (final status + landing URL)

Command:

```
curl -s -o /dev/null -w "%{http_code}\n" -L --max-time 20 "https://typsphinx.readthedocs.io/"
```

Output:

```
200
```

Command:

```
curl -s -o /dev/null -w "%{url_effective}\n" -L --max-time 20 "https://typsphinx.readthedocs.io/"
```

Output:

```
https://typsphinx.readthedocs.io/en/latest/
```

### 4b. Without following redirects (first-hop status + `Location` header)

Command:

```
curl -s -D - -o /dev/null --max-time 20 "https://typsphinx.readthedocs.io/"
```

Output (headers, truncated to the load-bearing lines):

```
HTTP/2 302
date: Sun, 26 Jul 2026 13:51:08 GMT
content-type: text/html; charset=utf-8
content-length: 0
location: https://typsphinx.readthedocs.io/en/latest/
cf-ray: a213e09a8e528376-KIX
cf-cache-status: EXPIRED
cache-control: max-age=1200
content-language: en
server: cloudflare
x-served: Django-Proxito
strict-transport-security: max-age=31536000; includeSubDomains; preload
vary: Accept-Language, accept-encoding
cdn-cache-control: public, max-age=1200
cross-origin-opener-policy: same-origin
referrer-policy: no-referrer-when-downgrade
x-backend: web-i-0f34ed3c45d688edf
x-content-type-options: nosniff
x-rtd-domain: typsphinx.readthedocs.io
x-rtd-force-addons: true
```

**Chain summary:** the bare root the repository now advertises (`https://typsphinx.readthedocs.io/`)
answers with a first-hop `302` to `https://typsphinx.readthedocs.io/en/latest/` (Read the Docs'
Default Version redirect), which itself answers `200`. A visitor clicking the About panel's
Website link lands on a live English documentation page — the precise action Issue #119 reported
failing with a 404.

### 4c. Japanese documentation root (second independent reading for Plan 05)

Command:

```
curl -s -o /dev/null -w "%{http_code}\n" -L --max-time 20 "https://typsphinx.readthedocs.io/ja/latest/"
```

Output:

```
200
```

Not the Website value itself, but the other half of the two-language site the About link fronts
(Phase 30.1's deliverable) — recorded here for Plan 05's sweep to reuse as a second independent
reading.

## 5. Issue #119 state (unchanged by this plan)

Command:

```
gh issue view 119 --json state --jq .state
```

Output:

```
OPEN
```

Command:

```
gh issue view 119 --json comments --jq '.comments | length'
```

Output:

```
1
```

Neither the issue's state nor its comment count was touched by this plan.

## 6. Measurement timestamp

UTC: `2026-07-26T13:51:18Z`

## What this plan does NOT discharge

Issue #119 remains **open by design** (D-15) — the owner decided the close happens after the
milestone merge, once the README rewrite (Plan 03) is visible on `main`, so that the close-reply
promises are actually fulfilled rather than pre-emptively announced. This plan (Plan 02) delivers
only the "About set + resolving" half of DOC-10; the close-reply draft is **Plan 05's**
deliverable, and the close itself (draft review -> post -> close, D-16) is a handoff to
`/gsd-complete-milestone`, tracked alongside the milestone's other owed post-merge flips
(RTD Default branch x2, `.gitmodules` branch, Default Version flip). This is an intentional
phase-boundary split, not a gap in this plan's verification.
