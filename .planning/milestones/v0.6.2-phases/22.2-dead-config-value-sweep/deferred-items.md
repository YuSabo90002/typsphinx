# Deferred Items — Phase 22.2

## From plan 22.2-06

**Item:** `tests/test_examples_basic.py::TestBasicExampleBuild` (3 tests: `test_build_typst_succeeds`,
`test_build_generates_typ_file`, `test_generated_typ_is_valid`) fail in the executor worktree with
`Could not start dynamically linked executable: uv` / NixOS `stub-ld` guidance.

**Root cause:** these tests invoke `subprocess.run(["uv", "run", "sphinx-build", ...])` directly.
Under NixOS, a bare `uv` resolved via a plain subprocess `PATH` lookup (rather than through the
interactive nix-wrapped shell this agent's Bash tool uses) hits the "dynamically linked executable"
sandbox restriction. This matches the already-documented NixOS sandbox limitation
(`uv run <compiled-binary>` fails outside the wrapped shell).

**Scope:** `examples/basic/` and `tests/test_examples_basic.py` — neither file is in this plan's
`files_modified` list (`examples/charged-ieee/approach2/...` only), and both were last touched by an
unrelated prior commit (`b08c67b`, Phase 22). This plan's own two commits touch only the two
`approach2` files listed in frontmatter.

**Action taken:** none — out of scope per the executor scope-boundary rule (pre-existing failure in
unrelated files). Logged here rather than fixed. Not a regression introduced by plan 22.2-06.

**Suggested follow-up:** either invoke `sphinx-build` directly (as this plan's own verification and
the sibling `test_pdf_render_gate.py`/`test_nested_master_render_gate.py` fixtures do via
`sys.executable -m sphinx`) instead of shelling out through `uv run`, or accept this as a fifth
NixOS-worktree-only environmental exclusion alongside the four `test_integration_*` files already
documented in the executor's environment notes.
