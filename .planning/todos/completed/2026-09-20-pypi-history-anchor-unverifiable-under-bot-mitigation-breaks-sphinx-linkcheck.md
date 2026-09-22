---
created: 2026-09-20
title: "tox -e linkcheck reports changelog.rst:474's https://pypi.org/project/typsphinx/#history anchor as broken because PyPI now serves a bot-mitigation interstitial to automated clients"
area: docs, ci
resolves_phase: null
source: 75-GREEN-TREE-EVIDENCE.md § "AMENDED 2026-09-20" Class B
severity: minor
files:
  - docs/source/changelog.rst:474  # the PyPI Release History link (re-measured 2026-09-20)
  - docs/source/conf.py            # currently contains zero linkcheck_* keys (re-measured 2026-09-20)
---

## Problem

`tox -e linkcheck` reports `docs/source/changelog.rst:474`,
`https://pypi.org/project/typsphinx/#history`, as a broken anchor. It is not a broken link.

Measured 2026-09-20T11:01:56Z from this machine: the page returns HTTP 200, but the body is a
3038-byte bot-mitigation interstitial whose title is `Client Challenge` and which contains no
anchors at all — `id="history"` occurs 0 times. The same interstitial comes back with a plain
client and with a full browser User-Agent, so it is not a User-Agent filter. Sphinx's
`linkcheck_anchors` is on by default and therefore cannot find `history` in that body.

The anchor's existence is unverifiable from an automated client, not disproven. The adjacent
`https://github.com/YuSabo90002/typsphinx/releases` link on `changelog.rst:473` returns 200 and
passes, so this is specific to PyPI.

Phase 73 (v0.9.5, four days earlier) recorded this same page as part of a 95/95 clean linkcheck
run, so the change is on PyPI's side and recent. The link text itself has not changed since
`691030db feat: add comprehensive documentation site with GitHub Pages`.

## Solution

Add a `linkcheck_anchors_ignore_for_url` (or `linkcheck_anchors_ignore`) entry for `pypi\.org` to
`docs/source/conf.py`, so the URL is still fetched and its status checked while the anchor lookup
is skipped. `docs/source/conf.py` currently contains zero `linkcheck` keys, so this introduces the
first one and should carry a comment naming the bot-mitigation reason and the measurement date —
otherwise a future reader will read it as a link being suppressed.

Re-measure before applying: if PyPI stops challenging automated clients, no config change is
needed and this todo closes as obsolete.

## Why it was deferred

Phase 75 is prep-only (D-14). `docs/source/conf.py` is outside the five files REL-15 names, and
editing it would force SC4's entire green proof to be re-taken on a changed tip — both full pytest
runs, both clean documentation builds, the linkcheck run and the single CI dispatch. The owner's
2026-09-20 decision amended SC4 to read `working` plus the classified exceptions equals `total`
rather than editing any product file; this todo is the deferred half of that decision.

Note this record is **not** carried by the `/gsd-complete-milestone` handoff. The two Class A
records in the same linkcheck run (the `v0.9.6` tag links) are carried there, because creating the
tag is what closes them. This one is independent of the release and closes only by a `conf.py`
change or by PyPI reverting.

## Related

`2026-07-22-add-sphinx-linkcheck-ci-job.md` proposes promoting `sphinx-build -b linkcheck` to a CI
job and already names `docs/source/conf.py` as the place `linkcheck_ignore`-family settings would
live. If that todo is taken up, this one should be resolved inside it rather than separately —
promoting linkcheck to CI without settling the PyPI anchor first would make the new job red on
arrival.
