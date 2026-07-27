# Phase 33: v0.6.4 Release Prep — Release Evidence

This file records SC#3 and SC#4 of ROADMAP Phase 33, with verbatim command output backing every
claim. Every command below was re-run during this plan's execution (2026-07-28); no figure is
carried forward from `33-CONTEXT.md`, `33-RESEARCH.md`, or `33-PATTERNS.md` as evidence — those
documents are inputs to be re-verified, not evidence themselves.

**Filename note:** this file is deliberately not named `33-VERIFICATION.md` — that name is
reserved by the `/gsd-verify-work` verifier, which overwrites it wholesale.

---

## SC#3: `Documentation` metadata URL — real HTTP re-verification

**Claim:** `pyproject.toml`'s `[project.urls] Documentation` value resolves over real HTTP to a
2xx terminal status on the prepared tree.

### Step 1 — parse the URL from `pyproject.toml` (not assumed, not quoted from a planning doc)

Command:
```
$ uv run python -c "import tomllib;print(tomllib.load(open('pyproject.toml','rb'))['project']['urls']['Documentation'])"
```

Verbatim output:
```
https://typsphinx.readthedocs.io/
```

This confirms the value in the prepared tree's `pyproject.toml` is the one fetched below. Phase 31
already set this value to the Read the Docs root; this plan makes no edit to it (confirmed by the
SC#4 `git diff main..HEAD -- pyproject.toml` section below, which shows only the version-bump
hunk — no `[project.urls]` change from this phase).

### Step 2 — un-followed fetch (records the redirect status and `Location`)

Command:
```
$ curl -s -o /dev/null -w "HTTP_CODE:%{http_code}\nLOCATION_HEADER_FOLLOWS\n" -D - "https://typsphinx.readthedocs.io/"
```

Verbatim output (headers, truncated to the load-bearing lines — full response included
cookies/CDN headers omitted here for brevity, none of which affect the verdict):
```
HTTP/2 302
date: Mon, 27 Jul 2026 21:15:25 GMT
content-type: text/html; charset=utf-8
content-length: 0
location: https://typsphinx.readthedocs.io/en/latest/
x-rtd-project: typsphinx
x-rtd-project-method: public_domain
x-rtd-redirect: system
x-rtd-version-method: path
server: cloudflare

HTTP_CODE:302
```

### Step 3 — followed fetch (records the terminal status code and effective URL)

Command:
```
$ curl -s -L -o /dev/null -w "TERMINAL_HTTP_CODE:%{http_code}\nEFFECTIVE_URL:%{url_effective}\nREDIRECT_COUNT:%{num_redirects}\n" "https://typsphinx.readthedocs.io/"
```

Verbatim output:
```
TERMINAL_HTTP_CODE:200
EFFECTIVE_URL:https://typsphinx.readthedocs.io/en/latest/
REDIRECT_COUNT:1
```

### Verdict

**SC#3: MET.** The `Documentation` URL parsed live from the prepared tree's `pyproject.toml`
(`https://typsphinx.readthedocs.io/`) redirects once (302 → `location:
https://typsphinx.readthedocs.io/en/latest/`, `x-rtd-project: typsphinx` confirming this is the
correct RTD project) and terminates at HTTP 200 on `https://typsphinx.readthedocs.io/en/latest/`.
This is a 2xx terminal status, so SC#3 is met with an honest, freshly-taken verdict.

### Observation timestamp

**2026-07-27T21:15:32Z** (ISO-8601, UTC). This is a point-in-time observation of a live external
service (Read the Docs), not a fact this repository holds any re-verification mechanism for.

### Deliberately excluded from CHANGELOG.md

Per D-03 (`33-CONTEXT.md`), this live-serving observation is **not** recorded in `CHANGELOG.md`.
The project's `### Verified` CHANGELOG convention (plan 33-02) is restricted to invariants a `git
diff` can mechanically re-prove at any future point; a point-in-time HTTP fetch against an external
service has no standing re-verification mechanism and would go stale the moment RTD's content or
routing changes. It is recorded here, in this dated evidence file, instead.
