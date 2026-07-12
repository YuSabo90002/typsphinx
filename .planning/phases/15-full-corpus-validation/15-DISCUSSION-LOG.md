# Phase 15: Full-Corpus Validation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-12
**Phase:** 15-full-corpus-validation
**Areas discussed:** Corpus acquisition & scope, Gate character vs. one-time measurement

---

## Gray-area selection

| Area | Discussed |
|------|-----------|
| Corpus acquisition & scope | ✓ |
| Gate character vs. one-time measurement | ✓ |
| Measurement recording location | defaults (D-06) |
| Empty-URL before/after methodology | defaults (D-07) |

User selected the first two areas to deep-dive; opted to lock the remaining two
(SC#2/#3 mechanics) via recommended defaults rather than interactive discussion.

---

## Corpus acquisition & scope

### Acquisition method
| Option | Description | Selected |
|--------|-------------|----------|
| Shallow `git clone` at pinned tag | Clone the tag matching the installed Sphinx version at run time. Reproducible, net-dependent. | ✓ |
| Vendor a snapshot | Commit a doc/ snapshot into the repo. Net-free but bloats repo, manual Sphinx-update tracking. | |
| Local checkout via env var | Point at a local Sphinx source path. CI/net-free but hard to automate/reproduce. | |

### Scope
| Option | Description | Selected |
|--------|-------------|----------|
| Full `doc/` tree | Faithful to GATE-02 wording and the "full-corpus" name. | ✓ |
| Representative subset | Faster/lighter but diverges from the milestone gate. | |

### conf.py
| Option | Description | Selected |
|--------|-------------|----------|
| Sphinx's real `doc/conf.py` | Real-world fidelity; needs Sphinx-internal + `sphinxext/` extensions loadable. | ✓ |
| Minimal conf.py | Controllable but lower real-world fidelity. | |

**Notes:** The real conf.py may require doc-build-only extensions not in
typsphinx's env — flagged as a researcher risk, with a documented minimal-conf
fallback as the escape hatch.

---

## Gate character vs. one-time measurement

### Gate character
| Option | Description | Selected |
|--------|-------------|----------|
| `slow`-marked standing pytest test (CI-excluded) | Reproducible pytest gate reusing the GATE-01 lineage, kept out of the default/CI fast suite. On-demand. | ✓ |
| One-time milestone validation (report artifact) | Run once via script, capture results in a committed report; no CI, no re-runs. | |
| Dedicated always-on CI job | Corpus validation every run. Strictest but net-dependent, slow, flaky, high-maintenance. | |

### On corpus unavailable (no net / clone failure)
| Option | Description | Selected |
|--------|-------------|----------|
| `pytest.skip` | Skip (don't fail) when the corpus can't be fetched. Standard slow-test hygiene; stays green offline/CI/sandbox. | ✓ |
| Fail | Treat fetch failure as a test failure. Guarantees the gate ran but breaks net-free envs. | |

**Notes:** Reproducibility without CI burden was the deciding factor; the corpus
build's net dependency and slowness make it a poor always-on CI gate.

---

## Claude's Discretion

- Exact clone mechanism, tag-resolution from `sphinx.__version__`, report table
  shape, and warning-capture mechanics — planner/researcher choice, as long as
  the D-01…D-07 decisions hold.

## Deferred Ideas

- Recording measurements as a GitHub issue / `.planning` backlog file (chose an
  in-phase `15-CORPUS-REPORT.md` instead).
- Interactive deep-dive on the measurement mechanics (locked via defaults D-06/D-07).
- XOS-01 (docs-pdf on macOS/Windows) and CFG-01 (configurable `@preview` versions)
  remain v2 out-of-scope.
