# S04 — Published-site evidence: the RTD English diagrams page

This file is the measurement record for M002/S04. The milestone criterion it
serves is the *published* half of **R021**: that the Graphviz fix reaches the
real page a reader loads from readthedocs.org, not merely a local build. S02
proved the local build renders the diagram; S03 proved an artifact gate detects
its absence. Both are builds on the maintainer's machine. Neither has ever
observed readthedocs.org.

**This file is written BEFORE the fix is merged, and that ordering is the
point.** Two things are only possible in this pre-merge window:

1. **The RED baseline is observable now and never again.** Once the merge lands
   and Read the Docs rebuilds, the broken page is gone permanently. A
   post-merge GREEN with no recorded RED is an unattributable "it works now"
   with no proof the page was ever broken.
2. **The assertions are pre-registered.** Writing them down before any
   post-merge data exists is what stops the measurement from being fitted to
   whatever the page happens to show. S02 and S03 both used this pre/post
   discipline; here the external dependency makes a missed baseline
   unrecoverable rather than merely inconvenient.

Accordingly, §2 below is measured and closed, and §3's assertions are a
contract with no results attached. Executing them is **T03**, and its
precondition (a merged fix plus a completed RTD rebuild) does not yet exist.
Nothing in this task merges anything, opens a PR, or measures a post-merge page.

> **Naming note.** This file is deliberately named `…-EVIDENCE.md` and must
> never be renamed to the reserved `-VERIFICATION.md` form. A file matching
> `{phase}-VERIFICATION.md` is overwritten by a later verifier step, which
> would destroy the irreplaceable baseline in §2.

---

## 1. The pinned target URL

```
https://typsphinx.readthedocs.io/en/latest/user_guide/diagrams.html
```

That URL is the single target for every assertion in this file.

### Why `en/stable` is explicitly NOT the target

A task that measured `stable` would record a failure that is really a
version-resolution artifact rather than anything about the fix. Measured from
the RTD v3 API on 2026-10-02:

| Version | `type` | `identifier` | `ref` | What it tracks |
|---|---|---|---|---|
| `latest` | `branch` | `main` | — | the `main` branch — **the target** |
| `stable` | `tag` | `d1df28aeb48556910ac6a2e63ac5455d237d6d79` | `v0.9.7` | the v0.9.7 tag |

The diagrams page **postdates the v0.9.7 tag**, so it does not exist in the
`stable` tree at all. Confirmed by direct request, not inferred:

| Request | HTTP |
|---|---|
| `GET /en/stable/user_guide/diagrams.html` | **404** |
| `GET /en/latest/user_guide/diagrams.html` | **200** |
| `GET /en/latest/` | **200** |

`pyproject.toml` is already at `version = "0.9.8"` (line 7), so `stable` still
resolves to v0.9.7 and will keep 404-ing on this path until a **v0.9.8 tag
ships**. Only after that tag does `stable` become a meaningful second target;
until then, asserting against it tests the tag, not the fix.

---

## 2. The pre-merge RED baseline — MEASURED, this task

Measured fresh in this task. The values below are observations, not
transcriptions of the planning-time expectation; the expectation was 0 / 0 / 1
and is reproduced exactly, so there is no discrepancy to flag.

### The measurement

```bash
curl -sS --max-time 45 -o /tmp/s04_red.html \
  https://typsphinx.readthedocs.io/en/latest/user_guide/diagrams.html
```

| Field | Value |
|---|---|
| Measured at | **2026-10-02T23:34:21Z** (2026-10-03T08:34:21+0900 local) |
| HTTP status | **200** |
| Bytes downloaded | 29607 |
| `sha256` of body | `a1ed058c1f352c8b34a068bd634dba70d5a690b1bacf74911d23f18444de6368` |

### Marker counts on that body

| Marker | Count | Meaning |
|---|---|---|
| `class="graphviz"` | **0** | no rendered-diagram container |
| `graphviz-[0-9a-f]{40}\.png` | **0** | no rendered PNG referenced |
| `<img` (any image tag at all) | **0** | corroborates the above — nothing was rendered |
| `digraph dogfood {` (raw HTML) | **1** | the DOT source shipped as page content |
| `digraph dogfood {` (**tag-stripped visible text**) | **1** | and a reader actually SEES it |

The last row is the strongest statement of the defect, and it is worth
separating from the raw-HTML row: on the published page the marker is in the
visible text, so this is not an `alt`-attribute artifact (see §3) — it is the
user-visible fail-open shape S02 documented. The surrounding visible text as
served:

```
in your documentation appears as a real vector drawing in the
generated PDF.

digraph dogfood {
    "Vorthaneglim" -> "Pellucidrane"
```

### Which RTD build this page corresponds to

From `GET https://readthedocs.org/api/v3/projects/typsphinx/builds/?limit=5`
at measurement time (80 builds total; newest five):

| `id` | `commit` | `version` | `state.code` | `success` | `finished` |
|---|---|---|---|---|---|
| **34900405** | `9c134be03298e73778ea8457a5e3056edc049a6e` | `latest` | `finished` | `true` | 2026-10-02T14:22:26Z |
| 34880066 | `76040d675e49d28d60c1d2248ee317b13164b607` | `latest` | `finished` | `true` | 2026-10-01T15:33:43Z |
| 34879855 | `a78ae3219b25b19d20e07a63f1605a47c8897535` | `latest` | `finished` | `true` | 2026-10-01T15:25:02Z |
| 34879248 | `634833839dfadf91a261036e90b26409aa4cb8ab` | `latest` | `finished` | `true` | 2026-10-01T14:57:24Z |
| 34806829 | `c50dd45d263f14302a8b4819072b84b548360803` | `latest` | `finished` | `true` | 2026-09-28T15:33:03Z |

**The baseline is attributable to an exact commit.** Build `34900405` built
commit `9c134be03298e73778ea8457a5e3056edc049a6e`, and that commit is precisely
the merge-base of this milestone branch with `origin/main`
(`git merge-base origin/main HEAD` → `9c134be032…`). So the RED page above is
the unmodified pre-fix tree, built successfully — not a failed build, not a
partially-deployed state.

### Why the page is RED while the build reports success

Measured, so no reader has to guess which half of the fix is missing:

| Fact | `origin/main` | this branch (`milestone/M002`, HEAD `296d5397`) |
|---|---|---|
| `graphviz::` directives in `docs/source/user_guide/diagrams.rst` | 4 | 4 |
| `graphviz` in `.readthedocs.yaml` `build.apt_packages` | **absent** | **present** (line 26) |
| commits ahead / behind `origin/main` | — | 9 ahead, 0 behind |

The directive is *already* on `main`; the missing piece is the system package.
Upstream `render_dot()` catches the `OSError` from the absent `dot` binary,
returns `(None, None)` without raising, and the build exits 0 — which is why
build 34900405 is `success: true` and the page is still broken. That is the
fail-open shape, confirmed on the published site and not just locally.

---

## 3. The three post-merge assertions (PRE-REGISTERED — no results yet)

Stated as the GREEN contract **before** any post-merge measurement exists. T03
runs these against the §1 URL and must not alter them to match what it finds.

### A1 — the rendered-diagram container is present

`class="graphviz"` appears **at least once** in the served HTML.

Mechanism: upstream emits `<div class="graphviz">` only on the successful render
path (`sphinx/ext/graphviz.py:389` and `:402`), with `'graphviz'` in the node
classes at `:376`. Count 0 is exactly what §2 measured.

### A2 — the referenced PNG is a real, fetchable image

A `graphviz-<40 hex>.png` reference exists (the `graphviz` filename prefix is
upstream's, `sphinx/ext/graphviz.py:280` / `:359`), **and** that reference is
then proven to be an image:

1. resolve its `src` against the page URL,
2. fetch it,
3. require HTTP **200**, PNG magic bytes (`\x89PNG`), and a non-trivial byte
   size.

**S02's rule, recorded explicitly because it is the easiest false GREEN here: a
`src` string alone does not prove a rendered image.** A reference can be present
and the target 404, so the markup must never be the whole claim — the bytes must
be fetched.

### A3 — the raw DOT source is absent from VISIBLE TEXT (primary claim)

`digraph dogfood {` appears **zero** times in the **tag-stripped visible text**
of the served page.

**Why visible text is the primary form, and raw HTML only secondary.** Upstream
defaults an img's `alt` attribute to the DOT source itself:

```python
alt = node.get('alt', self.encode(code).strip())   # sphinx/ext/graphviz.py:384
```

So on a *correctly rendered* page with no explicit `:alt:`, the literal string
`digraph dogfood {` still survives in the raw HTML — as an attribute value the
reader never sees. The raw-HTML form of this claim therefore holds on this tree
**only** because S02 added an explicit `:alt:` to the dogfood directive
(`docs/source/user_guide/diagrams.rst`, 2 `:alt:` options present at HEAD), and
it would silently regress to a false RED if anyone removed that option. The
visible-text form states the actual defect and holds with or without `:alt:`.

Accordingly:

| Claim | Status |
|---|---|
| `digraph dogfood {` absent from tag-stripped visible text | **primary — the assertion** |
| `digraph dogfood {` absent from raw HTML | secondary observation; record it, do not gate on it |

**Use the existing stripper, do not invent another.** The project already has
one: `_visible_text`, defined at `tests/test_graphviz_docs_gate.py:136`. Two of
its properties are load-bearing and a re-derived stripper tends to get them
wrong: each tag becomes a **space** (not the empty string), so two words
separated only by a tag boundary cannot fuse and invent or hide a match; and
entities are unescaped **after** stripping, never before, so entities inside
attribute values are not decoded while still inside a tag and then survive the
strip as apparent text. T03's measurement and that helper must agree.

---

## 4. The RTD readiness gate — precondition for running §3 at all

**Do not run the §3 assertions until this gate passes.** Running them earlier
produces a RED that is about deployment timing, not about the fix.

Poll:

```
https://readthedocs.org/api/v3/projects/typsphinx/builds/?limit=5
```

until some `results[]` entry satisfies **all three** of:

* `commit` equals the **merge commit** (the SHA on `main` after the merge — not
  this branch's HEAD, and not the pre-merge `9c134be032…` of §2);
* `state.code == "finished"`;
* `success == true`.

Each of those three fields is present and populated in the live response — see
the §2 build table, which was read from this endpoint.

**CDN staleness is a false-RED source, not a verdict.** A page fetched before
that build completes — or shortly after it, from an edge cache — may still be
the old body. A fetch whose markers match the §2 RED **after** the gate has
passed must trigger a **re-fetch** (re-poll the builds endpoint, confirm the
build identity again, and request the page again, ideally cache-busted), never a
RED verdict. The §2 `sha256` is recorded precisely so T03 can recognise "I am
being served the byte-identical pre-fix page" and distinguish it from a genuine
post-merge failure.

---

## 5. Documented negative finding — build logs are NOT reachable unauthenticated

Recorded so that no future reader builds a procedure around scraping the build
log and then discovers it cannot work.

`GET https://readthedocs.org/api/v3/projects/typsphinx/builds/34900405/`
returns **HTTP 200** with a detail object whose complete top-level key set is:

```
_links, commit, created, duration, error, finished, id, project, state,
success, urls, version
```

There is **no `commands` array and no `config` object**. The per-command
transcript — the only place the `apt-get install … graphviz` line would appear —
is therefore **not reachable unauthenticated** at that endpoint.

**Consequence for this slice's method: the served page is the evidence.** The
build log is a *contingency diagnostic only*, needing the RTD web UI or an
authenticated token, and is not part of any assertion in §3 or §4. If §3 goes
RED after §4's gate passes, the log is where a human looks next — it is not a
step the procedure depends on.

RTD v3 endpoints confirmed working **without** auth (all HTTP 200, measured):

| Endpoint | Returns |
|---|---|
| `/api/v3/projects/typsphinx/` | project detail |
| `/api/v3/projects/typsphinx/builds/?limit=N` | build list with `commit`, `state.code`, `success` |
| `/api/v3/projects/typsphinx/builds/<id>/` | build detail **minus** `commands`/`config` |
| `/api/v3/projects/typsphinx/versions/latest/` | `type=branch`, `identifier=main` |
| `/api/v3/projects/typsphinx/versions/stable/` | `type=tag`, `ref=v0.9.7` |
| `/api/v3/projects/typsphinx/translations/` | one result: `typsphinx-ja` (`ja`) |

---

## 6. What this evidence does NOT cover

Stated plainly, matching S02's and S03's habit, so nothing here is read as more
than it is.

* **It is not an automated gate.** This is a one-off, human-initiated
  measurement against a live external URL. **No test can assert a live URL** —
  it would make the suite network-dependent and fail offline, in CI sandboxes,
  and on any RTD outage. The regression protection for this defect lives in two
  *offline* gates instead: `tests/test_readthedocs_config.py` (asserts
  `graphviz` is in `.readthedocs.yaml`'s `build.apt_packages`, no build needed)
  and `tests/test_graphviz_docs_gate.py` (asserts a local build renders the
  diagram). This file covers the one thing neither can: that the deployed page
  actually changed.
* **English site only.** Every URL above is under `/en/`. The `ja` translation
  (`typsphinx-ja`, confirmed as the project's single translation in §5) is **not**
  measured here; **R022's disposition is T02's subject**, not this file's.
* **One page.** `user_guide/diagrams.html` only. No claim is made about any
  other published page.
* **A point in time.** §2 is a snapshot of build 34900405; §3 will be a snapshot
  of one post-merge build. Neither prevents a later regression — only the
  offline gates above do that.
* **Not a merge.** This task performed no merge, opened no PR, and measured no
  post-merge page. §3 and §4 are unexecuted by construction.

---

## 7. The `ja` disposition — settled as a tracked deferral (T02)

This section settles R022, the milestone's last external-facing claim. It is
written by **T02** and is about the **Japanese** site; everything above it
(§1–§6) is the English site and is T01/T03's subject.

**The branch was already chosen and this section does not revisit it.** Owner
decision **D015** (2026-10-03) put `ja` **out of scope for M002**: no PR is
opened in `typsphinx-doc-translations`. What this section fixes is the recorded
*reason*. A deferral resting on a wrong premise does not satisfy "settled with
its reason" — it misleads whoever picks it up. Every fact below was re-measured
in this task against the live repository and the live site, not transcribed from
planning notes.

### 7.1 Re-measured facts (all measured 2026-10-02T23:40Z)

Measured against `raw.githubusercontent.com/YuSabo90002/typsphinx-doc-translations/main`
and the GitHub contents API. **Four of the four planning-time facts reproduced
exactly; one planning-time *interpretation* did not — see §7.2.**

| Fact | Measured value | HTTP | Matches planning? |
|---|---|---|---|
| `.gitmodules` → `path` | `typsphinx` | 200 | yes |
| `.gitmodules` → `url` | `https://github.com/YuSabo90002/typsphinx.git` | 200 | yes |
| `.gitmodules` → `branch` | `main` | 200 | yes |
| submodule pin SHA (contents API, `type: submodule`) | `76040d675e49d28d60c1d2248ee317b13164b607` | 200 | yes — **has not advanced** since planning |
| `.readthedocs.yaml` → `build.apt_packages` | `- fonts-noto-cjk` **only** (one entry) | 200 | yes |
| `.readthedocs.yaml` → `graphviz` occurrences | **0** | 200 | yes |
| `.readthedocs.yaml` → `sphinx.configuration` | `typsphinx/docs/source/conf.py` (the submodule's copy) | 200 | yes |
| `.github/workflows/update-pin.yml` | **exists**, 6334 bytes | 200 | yes |
| …its `on:` triggers | `schedule` (`cron: "0 6 * * *"`) **and** `workflow_dispatch: {}` — both present | 200 | yes |

The pin's position relative to this repository, measured locally:

| Measurement | Value |
|---|---|
| `git merge-base --is-ancestor 76040d675e… origin/main` | **true** — the pin is a real `main` commit |
| `git rev-list --count 76040d675e…..origin/main` | **1** — the pin is exactly one commit behind `main`'s tip |
| `origin/main` tip | `9c134be03298e73778ea8457a5e3056edc049a6e` (the same commit §2's RED baseline build 34900405 built) |
| the pin's own subject | `Merge pull request #164 from YuSabo90002/chore/archive-planning-tree` |

### 7.2 Two causes — and a correction to which of them is actually breaking the page

The plan for this task stated that `ja` is broken by two independent causes:
(1) a stale source pin, and (2) a missing `graphviz` in the `ja` repo's own
manifest. **Cause 2 reproduced. Cause 1 did not — as a cause of the missing
diagram it is measurably not one**, and this is recorded as a flagged
difference rather than written as planned.

Measured at the pinned SHA `76040d675e…` versus this branch's HEAD:

| Measurement | at pin `76040d675e…` | at this branch HEAD |
|---|---|---|
| `graphviz::` directives in `docs/source/user_guide/diagrams.rst` | **4** | 4 |
| `:alt:` options in that file | 1 | 2 |
| `graphviz` in **this repo's** `.readthedocs.yaml` | 0 | 2 |

**The four `graphviz::` directives are already present at the pinned commit.**
So the `ja` page is not missing the diagram because its source is stale — the
source that emits the diagram is already there. It is missing the diagram for
one reason only:

> **Cause 2 is the sole cause of the `ja` page's RED state: the `ja`
> repository's own `.readthedocs.yaml` has no `graphviz` in its
> `build.apt_packages`, so `dot` is absent in its build container and upstream
> `render_dot()` fails open exactly as §2 describes for English.**

And the pin advance delivers **nothing** that bears on the render, for a second
measured reason: `ja` does not consume this repository's `.readthedocs.yaml` at
all. Its `sphinx.configuration` is `typsphinx/docs/source/conf.py` — the
submodule's `conf.py`, not the parent's manifest. The `graphviz` line this
milestone added to **this** repo's `.readthedocs.yaml` therefore never reaches
the `ja` build container by any route, pinned or fresh.

What the pin advance *does* deliver is content currency: when this milestone
merges, the daily `update-pin.yml` run advances the pin and the `ja` build picks
up S02's second `:alt:` option (1 → 2). That matters only to the **secondary,
raw-HTML** form of assertion A3 (§3), never to whether a diagram renders.

So the corrected premise, which is what makes the deferral honest:

* **Cause 1 (stale pin) — self-healing, and not load-bearing.** It closes with
  **no `ja`-repo edit at all**, via the daily `schedule` trigger in
  `update-pin.yml`, at most ~24 hours after the fix lands on `main`. It is not
  what is breaking the diagram.
* **Cause 2 (missing `graphviz` in the `ja` manifest) — the whole defect, and
  unfixable from here.** Nothing in this repository can change it. The fix is a
  **one-line `- graphviz` addition to an `apt_packages` block that already
  exists** in the other repo (it currently holds `- fonts-noto-cjk`), i.e. an
  edit to a block, not a new block. Cause 2 is what keeps D015's deferral
  correct — and now it is the *only* thing the deferral needs to rest on.

### 7.3 Correcting the misleading `workflow_dispatch` note

R022's current validation text says:

> "The delivery route must be confirmed in that repository first: update-pin.yml
> does NOT exist in this repo (only ci, docs, drift, links, release), so the
> workflow_dispatch route cannot be assumed from here."

That sentence is **literally true of `typsphinx`** — re-measured here:
`.github/workflows/` in this repository holds exactly `ci.yml`, `docs.yml`,
`drift.yml`, `links.yml`, `release.yml`, and `update-pin.yml` is **absent**.
But it is **misleading**, and a reader takes it as "the route is unavailable."

**The route IS available**, because the workflow exists exactly where it is
needed — in `typsphinx-doc-translations`, carrying **both** triggers
(`schedule` *and* `workflow_dispatch: {}`, measured above). Whoever picks this
up does not need to build a delivery route: they can advance the pin on demand
with a `workflow_dispatch` run in that repository, or simply wait for the daily
`schedule`. The absence of `update-pin.yml` *here* is irrelevant to that.

### 7.4 The live `ja` page — measured

```bash
curl -sS --max-time 45 \
  https://typsphinx.readthedocs.io/ja/latest/user_guide/diagrams.html
```

| Field | Value |
|---|---|
| Measured at | **2026-10-02T23:40:35Z** (2026-10-03T08:40:35+0900 local) |
| HTTP status | **200** |
| Bytes downloaded | 29470 |
| `sha256` of body | `ce500fa27fdc8570e01f0082d5f7b6f1dc4b8db30aa9765b8a9ab929a54bad9e` |

Marker counts, using the **same three markers and the same visible-text
semantics** as §2 and §3 (tag → space, unescape after stripping), so the two
sites' rows are directly comparable:

| Marker | `ja` count | English count (§2) |
|---|---|---|
| `class="graphviz"` | **0** | 0 |
| `graphviz-[0-9a-f]{40}\.png` | **0** | 0 |
| `<img` (any image tag) | **0** | 0 |
| `digraph dogfood {` (raw HTML) | **1** | 1 |
| `digraph dogfood {` (tag-stripped visible text) | **1** | 1 |

**`ja` is RED in exactly the same shape as the pre-fix English page: 0 / 0 / 1.**
A reader of the Japanese site today sees the raw DOT source as page text.

### 7.5 Use this URL — the obvious-looking host 404s

Recorded so a future reader does not curl the host that looks right and wrongly
conclude the site is gone. The `ja` site is served under the **parent's**
domain, because it is an RTD *translation* of `typsphinx` (confirmed in §5: the
project's single translation is `typsphinx-ja`), not a separately-served
project.

| URL | HTTP | Verdict |
|---|---|---|
| `https://typsphinx.readthedocs.io/ja/latest/user_guide/diagrams.html` | **200** | **the correct target — use this** |
| `https://typsphinx.readthedocs.io/ja/latest/` | 200 | correct host, site is live |
| `https://typsphinx-doc-translations.readthedocs.io/` | **404** | repo name ≠ RTD host; **not** evidence the site is gone |
| `https://typsphinx-doc-translations.readthedocs.io/ja/latest/` | **404** | same trap, same non-conclusion |

### 7.6 The settled disposition, stated plainly

> **The `ja` site remains RED when M002 closes, by owner choice (D015).**

M002 does **not** address `ja`. It is not partially fixed, not fixed-pending-
rebuild, and not expected to go GREEN when the English fix merges — because the
daily pin advance (cause 1) does not touch cause 2, and cause 2 lives in a
repository this milestone deliberately does not edit. R022 is therefore an
**accurate tracked deferral**: a known, measured, published defect with a named
one-line fix, a confirmed delivery route, and an explicit owner decision to
leave it for later.

Scope boundary honoured by this task: **no edit was made in any other
repository, and no PR was opened.** D015 scoped that out; it is outward-facing
work in a different repo requiring explicit owner approval. If such a posting is
ever authorised, it must use `gh … --body-file`, never inline command
substitution — the sandbox rejects `$(…)` in `--comment`/`--body` arguments.

---

## 8. Proposed R022 record (applied at slice closeout)

**This task does not mutate the requirement record.** Requirement
terminalization belongs to slice/milestone closeout, and T02 is an ordinary
implementation task with no `gsd_requirement_*` tools on its surface. The exact
replacement strings are drafted here so that closeout's update is accurate and
reviewable rather than re-derived.

**Status:** keep `deferred`. **Class:** keep `operability`. **Primary owning
slice:** keep `deferred (no M002 slice)`. Only `Validation` and `Notes` change.

### Proposed `Validation` string

> Deferred — not validated in M002; the ja site remains RED at milestone close
> by owner decision D015. When picked up: add a one-line `- graphviz` entry to
> the `build.apt_packages` block that already exists in
> `typsphinx-doc-translations`'s own `.readthedocs.yaml` (measured
> 2026-10-02: that block holds `- fonts-noto-cjk` only, and `graphviz` occurs 0
> times in the file), then curl
> `https://typsphinx.readthedocs.io/ja/latest/user_guide/diagrams.html` and
> require `class="graphviz"` ≥ 1, a fetchable `graphviz-<40hex>.png` (HTTP 200 +
> PNG magic bytes, not merely a `src` string), and `digraph dogfood {` absent
> from the tag-stripped visible text. The delivery route is **already
> available** and needs no construction: `.github/workflows/update-pin.yml`
> exists in that repository with both a `schedule` trigger (`cron: "0 6 * * *"`)
> and `workflow_dispatch: {}` (measured 2026-10-02), so the pin can be advanced
> on demand or left to the daily run. Use the parent domain `/ja/` path above —
> `typsphinx-doc-translations.readthedocs.io` 404s (measured), because ja is an
> RTD translation of the `typsphinx` project, not a separately-served project.

### Proposed `Notes` string

> Deferred by owner decision D015, 2026-10-03. Measured premise, corrected in
> S04/T02 (see `docs/S04-PUBLISHED-SITE-EVIDENCE.md` §7): ja consumes this
> repo's `docs/source` as a pinned git submodule (`.gitmodules`:
> `path=typsphinx`, `branch=main`, pinned at `76040d675e…`, one commit behind
> `main`'s tip `9c134be032…`), and its `sphinx.configuration` is the
> submodule's `typsphinx/docs/source/conf.py` — so conf.py is shared, but
> `.readthedocs.yaml` is **not**: ja has its own manifest in the separate
> `typsphinx-doc-translations` repository. The `graphviz` line M002 added to
> this repo's `.readthedocs.yaml` therefore never reaches the ja build
> container by any route. Measured at the pinned commit, the 4 `graphviz::`
> directives are **already present**, so the stale pin is *not* what breaks the
> ja page — the single cause is the missing `graphviz` in ja's own
> `apt_packages`, which no edit or test in this repository can fix or verify.
> The daily `update-pin.yml` advance self-heals pin currency (it will pick up
> S02's second `:alt:`, relevant only to the secondary raw-HTML form of
> assertion A3) but cannot fix the render. Measured live 2026-10-02T23:40:35Z:
> ja is RED in the identical 0 / 0 / 1 shape as the pre-fix English page
> (`class="graphviz"` 0, png 0, `digraph dogfood {` 1 in both raw HTML and
> visible text), HTTP 200, `sha256
> ce500fa27fdc8570e01f0082d5f7b6f1dc4b8db30aa9765b8a9ab929a54bad9e`. Cheap to
> pick up later as its own milestone — the fix is one line in a block that
> already exists, and the `workflow_dispatch` delivery route is already
> available there. **Supersedes** the earlier note's claim that the
> `workflow_dispatch` route "cannot be assumed from here": that was literally
> true of `typsphinx` (which has only ci/docs/drift/links/release) and
> misleading, because `update-pin.yml` exists exactly where it is needed.

---

## Failure Modes

Every dependency here is **external and networked**, which is the whole risk
surface of this slice. Enumerated with its failure path and the handling this
procedure mandates.

| Dependency | Failure mode | Failure path / handling |
|---|---|---|
| `https://typsphinx.readthedocs.io/…/diagrams.html` (the page) | timeout / connection loss | `curl -sS --max-time 45` bounds the wait; `curl` exits non-zero and the measurement is **inconclusive, not RED**. Retry; a network failure is never recorded as an assertion result. |
| same | non-200 (404 / 5xx) | HTTP status is recorded as a first-class field (§2 records `200`). A 404 on `stable` is a *version artifact* (§1), not a defect — this is exactly why the target is pinned to `latest`. A 5xx is an RTD outage: re-fetch. |
| same | **CDN-stale body (the dangerous one)** | Silently returns the pre-fix page and would be read as a genuine RED. §4 mandates: markers matching §2 after the readiness gate passed ⇒ **re-fetch, never a RED verdict**. The recorded `sha256` makes byte-identity with the pre-fix page detectable rather than guessable. |
| `readthedocs.org/api/v3/.../builds/` (readiness gate) | timeout / connection loss | Polling simply has not satisfied the gate yet. The gate is a *precondition*, so failure to reach it **blocks** §3 rather than failing it. |
| same | malformed / unexpected JSON shape | The gate reads three specific fields (`commit`, `state.code`, `success`). A missing or renamed field means the gate is **unproven**, which blocks §3. It must not be treated as satisfied by absence — a `KeyError` or a missing key is a block, not a pass. |
| same | API schema change dropping `commands`/`config` further | Already the measured state (§5) and already designed around: no assertion depends on the build log. |
| the PNG referenced by A2 | reference present but target 404 / non-PNG / truncated | This is the **false-GREEN** path. A2 explicitly requires fetch + HTTP 200 + `\x89PNG` magic + non-trivial size; a `src` string alone is insufficient (S02's rule). |
| `tests/test_graphviz_docs_gate.py:136` `_visible_text` | helper moved/renamed, or T03 re-derives its own stripper | A3 names the helper and its two load-bearing properties (tag→space; unescape after strip) so a drifted or hand-rolled stripper is detectable by disagreement rather than silently producing a different answer. |

Nothing in this task writes to the filesystem outside
`docs/S04-PUBLISHED-SITE-EVIDENCE.md` and `/tmp` scratch, and no subprocess
beyond `curl`/`git`/`python3` is involved.


### T02 addendum — the `ja` disposition's own dependencies (§7)

§7 added three external dependencies beyond §2's. Each is a one-shot read whose
failure makes a *fact unmeasured*, never a fact assumed:

| Dependency | Failure mode | Failure path / handling |
|---|---|---|
| `raw.githubusercontent.com/.../typsphinx-doc-translations/main/*` (`.readthedocs.yaml`, `.gitmodules`, `update-pin.yml`) | timeout / connection loss | `curl -sS --max-time 45`; non-zero exit means the fact is **unmeasured**. §7.1 records the HTTP status per row (all 200) so an unmeasured row is visibly distinct from a measured-absent one. |
| same | **404 read as "the file does not exist"** — the dangerous one | A 404 on `update-pin.yml` would resurrect exactly the wrong premise §7.3 corrects. Handled by recording the status column explicitly and, for `update-pin.yml`, a corroborating byte count (6334) and the parsed `on:` block — a 404 cannot produce either. |
| GitHub contents API (`/contents/typsphinx?ref=main`) | rate limit (unauthenticated, 403/429) or schema change | The pin SHA is read from `.sha` on an object asserted to be `type: submodule`; §7.1 records both fields. A 403 or a missing key leaves the pin **unmeasured** and blocks the §8 draft text, which quotes the SHA. |
| `https://typsphinx.readthedocs.io/ja/latest/user_guide/diagrams.html` | timeout / non-200 / CDN-stale body | Same handling as §2's English page: status is a first-class recorded field (200), with byte count and `sha256` so a later reader can tell whether they were served the identical body. A stale body here is **harmless to the verdict** — unlike §4, this measurement expects RED and makes no post-fix claim. |
| `https://typsphinx-doc-translations.readthedocs.io/` (the 404 trap) | returns 200 in future (RTD project created later) | §7.5's row would become stale. It is recorded as a *measurement with a date*, not an invariant; the conclusion that matters (ja is served under the parent's `/ja/` path) is independently corroborated by §5's translations endpoint. |

Nothing in T02 wrote outside `docs/S04-PUBLISHED-SITE-EVIDENCE.md` and `/tmp`
scratch, made any network **write**, edited any other repository, or mutated any
requirement record. Subprocesses were `curl`, `git`, `python3` only.

## Load Profile

The runtime dimension is small but real: this procedure issues **unauthenticated
polls to a third-party API**, so the resource that saturates first is
**readthedocs.org's anonymous API rate limit**, not anything local.

* **Expected load.** §2 used 1 page fetch + 1 build-list call + 1 build-detail
  call + 2 version calls + 1 translations call + 1 project call. T03 adds a
  readiness poll loop plus 1 page fetch plus 1 PNG fetch.
* **10x breakpoint.** 10x arrives via the §4 **poll loop**, not via page
  fetches: a tight loop against `/builds/` is the only unbounded term. At ~10x a
  sane cadence, anonymous RTD requests risk HTTP 429 / throttling, which would
  masquerade as "gate never satisfied".
* **Protection applied.** The poll is bounded on three axes: `--max-time 45` per
  request; `?limit=5` so each response is small and fixed-size rather than
  paging the full 80-build history; and a **slow cadence matched to reality** —
  RTD builds here take ~45s (build 34900405: created 14:21:40Z, finished
  14:22:26Z), and a merge-triggered build takes minutes to even start, so the
  correct interval is tens of seconds, not sub-second. T03 must also cap total
  poll attempts and report "gate unsatisfied" rather than loop indefinitely.
* **No local load dimension.** The artifact is a single markdown file; there is
  no service, no concurrency, and no data growth.


### T02 addendum

T02 added no runtime load dimension. Its network use is a **fixed, bounded set
of one-shot reads** — 3 raw-file fetches, 1 contents-API call, 4 page/host
fetches, 9 requests total, no loop and no polling — so the §4 poll loop remains
the only unbounded term in this slice and the analysis above is unchanged. At
10x, the first thing to saturate would be the **unauthenticated GitHub API rate
limit** (60 req/hr/IP, far below RTD's), which is why the pin SHA is read with a
single contents call rather than by cloning or walking commits. The artifact
remains one markdown file.

## Negative Tests

This procedure's falsifiability does not rest on tests — no test can assert a
live URL (§6) — so it is established by a measured negative and by named
false-verdict paths that the assertions are explicitly written to exclude.

* **The measured negative case is §2 itself.** The three A1–A3 markers were
  observed at **0 / 0 / 1** on the real published page at a known commit. The
  assertions are therefore known to *discriminate*: they are not vacuous
  predicates that any page would satisfy. This is the same
  "observe it RED before trusting it GREEN" discipline as S03, which forced its
  gate RED before accepting its GREEN.
* **False GREEN — `src` string without bytes.** A2 would pass on markup alone
  while the image 404s. Excluded by requiring fetch + 200 + `\x89PNG` magic +
  non-trivial size.
* **False GREEN — `alt` attribute hiding the regression.** If `:alt:` were
  removed, raw HTML would contain `digraph dogfood {` on a *correctly rendered*
  page (`sphinx/ext/graphviz.py:384`). Excluded by making **visible text** the
  primary claim (A3) and raw HTML only a secondary observation.
* **False RED — CDN-stale page.** Excluded by §4's readiness gate plus the
  mandated re-fetch, with §2's `sha256` as the byte-identity check.
* **False RED — wrong version target.** `GET /en/stable/…/diagrams.html` → **404**,
  measured. Excluded by pinning `latest` and recording *why* (§1), so a future
  reader cannot reintroduce the `stable` 404 as a finding.
* **False RED — build not yet finished.** A page fetched between merge and
  rebuild is legitimately old. Excluded by §4 requiring
  `state.code == "finished"` **and** `success == true` **and** a matching
  `commit` before §3 runs at all.
* **Boundary — `success: true` on a broken page.** Build 34900405 is
  `success: true` *and* serves the defect (§2), because upstream fails open.
  This is why A1–A3 assert on the **served page** and never on build status;
  build success is a precondition, never evidence of the fix.
* **Existing offline coverage, for completeness.** The regression-protecting
  negative tests live in `tests/test_graphviz_docs_gate.py` (S03 drove its
  `TestDogfoodedDiagramHTMLBuild` class RED by removing `dot` from `PATH`) and
  `tests/test_readthedocs_config.py` (asserts the `apt_packages` entry whose
  absence on `main` is the measured root cause in §2).

### T02 addendum — why §7's facts are falsifiable

T02 adds no test, and deliberately so: §6's rule holds — no test may assert a
live URL or a third-party repository's contents. Falsifiability instead comes
from the same discipline used above:

* **Each fact carries its HTTP status and its measurement timestamp**, so an
  unmeasured fact cannot masquerade as a measured one (§7.1).
* **The planning premise was treated as falsifiable and was in fact falsified.**
  §7.2 re-measured the claim that a stale pin is one of two causes and found the
  4 `graphviz::` directives **already present at the pinned commit** — recorded
  as a flagged difference rather than transcribed. This is the negative result
  that makes the rest of §7 credible.
* **The `ja` RED row is a measured negative, not an assumption** (§7.4): 0 / 0 /
  1, computed with the *same* markers and the same `_visible_text` semantics as
  §2, so the two sites are comparable and a marker-set drift would show as
  disagreement.
* **False conclusion — "the ja site is gone."** Excluded by §7.5 measuring the
  404ing host explicitly and pinning the correct URL.
* **False conclusion — "ja will go GREEN when the English fix merges."**
  Excluded by §7.2's measurement that ja never consumes this repo's
  `.readthedocs.yaml`, so the pin advance cannot deliver the fix.
* **Existing offline coverage is unchanged by T02.** No test file was touched;
  `tests/test_readthedocs_config.py` and `tests/test_graphviz_docs_gate.py`
  continue to guard the English/local surface exactly as before.
