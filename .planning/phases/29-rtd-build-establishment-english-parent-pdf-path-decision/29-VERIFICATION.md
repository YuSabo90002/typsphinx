# Phase 29 — Live Evidence Record

This file is created by Plan 02 and **appended to** by Plans 03/04/05/06. Every later writer adds a new
`##` section after the existing ones and must never rewrite or reorder what is already here.

## SC#1 — /en/latest/ serves real content

**Command:**

```
curl -sS -o /tmp/p29-en-latest.html -w 'code=%{http_code} url=%{url_effective} size=%{size_download}\n' -L https://typsphinx.readthedocs.io/en/latest/
```

**Fetched:** 2026-07-25T14:00:05Z (UTC)

**Output:**

```
code=200 url=https://typsphinx.readthedocs.io/en/latest/ size=30451
```

**Matched phrase (from the captured body, with surrounding context):**

```
<h2>Key Features<a class="headerlink" href="#key-features" title="Link to this heading">¶</a></h2>
<ul class="simple">
<li><p><strong>Sphinx to Typst Conversion</strong>: Convert reStructuredText/Markdown to Typst format</p></li>
<li><p><strong>Dual Builder Integration</strong>:</p>
<ul>
```

**Proves:** `https://typsphinx.readthedocs.io/en/latest/` returns HTTP 200 and serves typsphinx's own
rendered `docs/source/index.rst` content — the distinctive "Sphinx to Typst Conversion" feature bullet
appears in the response body, not an RTD placeholder or a 404 page (SC#1, serving half).

## SC#4 — documentation root resolves

**Command (full redirect chain, headers + final status):**

```
curl -sS -D - -o /tmp/p29-root-body.html -L https://typsphinx.readthedocs.io/ -w 'FINAL: code=%{http_code} url=%{url_effective} size=%{size_download}\n' | grep -E '^(HTTP/|location:|FINAL)' -i
```

**Fetched:** 2026-07-25T14:00:13Z (UTC)

**Output (redirect chain — status code of each hop plus final effective URL):**

```
HTTP/2 302
location: https://typsphinx.readthedocs.io/en/latest/
HTTP/2 200
FINAL: code=200 url=https://typsphinx.readthedocs.io/en/latest/ size=30451
```

**Body content-match command and output:**

```
grep -q "Sphinx to Typst Conversion" /tmp/p29-root-body.html && echo BODY_MATCH_OK
```
```
BODY_MATCH_OK
```

**Proves:** `https://typsphinx.readthedocs.io/` issues a single HTTP 302 whose `Location` header names
`https://typsphinx.readthedocs.io/en/latest/`, and following that redirect lands on HTTP 200 with the
same distinctive index-page phrase present in the body. The final effective URL contains `latest` — the
documentation root resolves to an existing, content-serving version (RTD Default Version = `latest`),
not to a `stable` version that has no build yet (SC#4, RTD-04).

**Combined plan-prescribed verify command (both fetches, both content assertions, re-run for the record):**

```
curl -sS -o /tmp/p29-en-latest.html -w 'code=%{http_code} url=%{url_effective} size=%{size_download}\n' -L https://typsphinx.readthedocs.io/en/latest/ && curl -sS -o /tmp/p29-root.html -w 'code=%{http_code} url=%{url_effective} size=%{size_download}\n' -L https://typsphinx.readthedocs.io/ && grep -q 'Sphinx to Typst Conversion' /tmp/p29-en-latest.html && grep -q 'Sphinx to Typst Conversion' /tmp/p29-root.html && echo LIVE_FETCH_OK
```
```
code=200 url=https://typsphinx.readthedocs.io/en/latest/ size=30451
code=200 url=https://typsphinx.readthedocs.io/en/latest/ size=30451
LIVE_FETCH_OK
```

## Owner-Manual Steps (human_needed)

The following RTD web-UI actions have **no** `.readthedocs.yaml` representation and no API this phase is
authorized to script. They are recorded here exactly as the owner reported them in Task 1
(`checkpoint:human-action`, gate `blocking-human`) — **owner-reported, NOT machine-verified.** No command
in this repository can assert that these dashboard clicks happened; only their *outcome* (the fetches
above) is machine-verified.

1. **Slug confirmation** — `human_needed`. The owner confirmed on RTD's import screen that the slug
   `typsphinx` was unclaimed (it had been measured unclaimed on 2026-07-25 via a 404 at
   `https://typsphinx.readthedocs.io/`, but RTD's import screen is the authoritative check). The
   `SLUG TAKEN` stop condition did **not** fire.
2. **Project creation + GitHub connection** — `human_needed`. Owner-reported: `slug=typsphinx`, created
   from the GitHub repository `YuSabo90002/typsphinx`, with GitHub connected so pushes trigger builds.
3. **Admin Language = English** — `human_needed`. Owner-reported: `admin_language=English`.
4. **Default Version left at `latest`** — `human_needed`. Owner-reported: `default_version=latest`. Not
   set to `stable` (confirmed independently below by the SC#4 root-fetch, which is machine-verified).

**Fifth owner-manual action, beyond the plan's original four** (recorded per explicit executor
instruction — see reasoning in the next section and in `## Phase 33 Handoff Precondition`):

5. **RTD Default Branch set to the milestone branch** — `human_needed`. The plan assumed the branch
   carrying Plan 01's commits would already be buildable by RTD; it was not, because the milestone
   branch (`gsd/v0.6.4-read-the-docs-migration`) was unpushed at the time and RTD's `latest` version
   tracks the repository's default branch, which was `main`. The orchestrator surfaced this to the
   owner, who chose: push the milestone branch (performed by the orchestrator, commit `2d6ff27`), and
   set **RTD Admin → Advanced settings → Default branch = `gsd/v0.6.4-read-the-docs-migration`** so that
   `latest` tracks the milestone branch for the duration of the milestone (performed by the owner in the
   RTD dashboard — `human_needed`, not machine-verifiable from this repository). This step's reversal is
   recorded as a second, separate precondition in `## Phase 33 Handoff Precondition` below.

**Owner-reported build identity carried forward from Task 1** (used again in the next section):

```
slug=typsphinx
admin_language=English
default_version=latest
build_url=https://app.readthedocs.org/projects/typsphinx/builds/33756675/
build_status=Build succeeded
built_commit=2d6ff27bea2ae205a3f686b1cc53f8d81f9c5ab7
```
