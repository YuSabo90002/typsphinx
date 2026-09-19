# Phase 74 — GATE-01 Evidence (RED, then GREEN)

## Head check and provisioning

`date -u +%FT%TZ`:
```
2026-09-19T22:04:55Z
```

`pwd -P` under `/home/yuta/Documents/typsphinx/.claude/worktrees/`:
```
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-af043e499ab90f999
```

`test -f .git; echo "exit:$?"`:
```
exit:0
```

Shim check `grep -q typsphinx-fhs-run "$(command -v uv)"`:
```
exit:0 (shim present)
```

Provisioning command:
```
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --python 3.13.13
```
Provisioning exit: `0` (uv sync completed, typsphinx==0.9.2 installed editable from this
worktree, full dependency tree resolved).

PYVENV_HOME = /nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin

PYVENV_VERSION_INFO = 3.13.13

RED_START_SHA = 8ea10273265e3966b6e650bad43cf90c9598ed65

SCRATCH_74_02 = /tmp/tmp.GTJV8xZquB

`git diff --name-only 6cc44f22a01f1e9d2080a8220fca2dc2cdcb264b "$RED_START_SHA" -- . ':(exclude).planning'`:
```
(empty — this tree carries no handler)
```

Ruff and black on the new files:
```
$ uv run ruff check tests/test_doctest_block_render_gate.py tests/fixtures/doctest_block_render_gate/conf.py
All checks passed!
$ uv run black --check tests/test_doctest_block_render_gate.py tests/fixtures/doctest_block_render_gate/conf.py
All done!
2 files would be left unchanged.
```

Fixture and module committed as `test(74-02): add context (a) doctest_block render gate (RED)`.

## Tracer RED (context a)

TRACER_RED_SHA = 39a985e0e4fd4e580fa38f0a7a71bf8590f9fea8

Command: `uv run pytest tests/test_doctest_block_render_gate.py -rA -p no:cacheprovider`,
stdout and stderr redirected to `$S/p7402_tracer-pytest.txt`.

Short test summary, verbatim:
```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- /home/yuta/Documents/typsphinx/.claude/worktrees/agent-af043e499ab90f999/.venv/bin/python
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-af043e499ab90f999
configfile: pyproject.toml
plugins: cov-7.1.0

=========================== short test summary info ============================
FAILED tests/test_doctest_block_render_gate.py::TestDoctestBlockRenderGate::test_build_exits_zero_without_compile_failure
FAILED tests/test_doctest_block_render_gate.py::TestDoctestBlockRenderGate::test_build_reports_no_doctest_block_unknown_node
FAILED tests/test_doctest_block_render_gate.py::TestDoctestBlockRenderGate::test_no_unknown_node_warning_for_shape[ctx_a_paragraph]
FAILED tests/test_doctest_block_render_gate.py::TestDoctestBlockRenderGate::test_master_writes_pdf[index]
FAILED tests/test_doctest_block_render_gate.py::TestDoctestBlockRenderGate::test_master_writes_pdf[context_a_paragraph]
FAILED tests/test_doctest_block_render_gate.py::TestDoctestBlockRenderGate::test_context_a_paragraph_line_structure
============================== 6 failed in 0.49s ===============================
```

exit:1

All four required tests are FAILED: `test_context_a_paragraph_line_structure`,
`test_master_writes_pdf[context_a_paragraph]`, `test_no_unknown_node_warning_for_shape[ctx_a_paragraph]`
and `test_build_reports_no_doctest_block_unknown_node`. (Two additional tests also failed —
`test_build_exits_zero_without_compile_failure` and `test_master_writes_pdf[index]` — because the
`index` master's `#include()` re-parses the poisoned `context_a_paragraph` content file, so its own
compile fails too. This is a stronger RED than required, not a gap.)

The gate detects the defect. Proceeding to Task 2.
<!-- gsd:write-continue -->
