# Phase 70 — After-side Runtime Evidence

BASE_70_11 = 44c43e345f8d5916486e5b7c2790bcb16c58f9d0
SCRATCH_70_11 = /tmp/tmp.0myAv8FjS1

## Precondition checks

Task 1 precondition: `70-FLIP-EVIDENCE.md` exists at HEAD with no HALT heading, and
`pyproject.toml`'s `[tool.ruff.lint]` section names neither UP006 nor UP035.

```
$ test -f .planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-FLIP-EVIDENCE.md; echo "exit:$?"
exit:0
$ grep -c '^## HALT' .planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-FLIP-EVIDENCE.md
0
$ sed -n '/^\[tool\.ruff\.lint\]/,/^\[/p' pyproject.toml
[tool.ruff.lint]
select = ["E", "F", "W", "I", "N", "UP", "B", "A", "C4", "T20"]
ignore = [
    "E501",   # Line too long (handled by black)
    "T201",   # print found (used in tests for debugging)
    "B017",   # asserting blind exception in tests
    "UP028",  # yield from (minor optimization)
    "N802",   # Function naming (docutils visitor pattern uses PascalCase)
    "A001",   # Shadowing builtins (copyright in conf.py is Sphinx convention)
    "F841",   # Unused variable (acceptable in tests and mocks)
]

[tool.mypy]
```
Neither `UP006` nor `UP035` appears in `ignore`. Precondition met — proceeding.

## Provisioning

Ran `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs --python 3.13.13`
in this worktree (`/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a099ef5f3ff5bdb00`). Exit 0.

`.venv/pyvenv.cfg`:
```
home = /nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin
implementation = CPython
uv = 0.11.25
version_info = 3.13.13
include-system-site-packages = false
prompt = typsphinx
```

VENV_HOME = /nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin
VENV_VERSION_INFO = 3.13.13

Both equal 70-02's `70-BASELINE-EVIDENCE.md` keys (`VENV_HOME` and `VENV_VERSION_INFO`) exactly —
confirmed by direct comparison.

## Leg (b) — pytest after

Ran `LC_ALL=C uv run pytest --collect-only -q -p no:cacheprovider 2>/dev/null | grep -oE '[0-9]+ tests? collected' | grep -oE '^[0-9]+'`
(the unanchored form, per 70-02's extraction — the summary line is `=`-decorated):

PYTEST_COLLECTED_AFTER = 1548

Equals `PYTEST_COLLECTED_BEFORE = 1548` from `70-BASELINE-EVIDENCE.md`. Confirmed.

Ran `LC_ALL=C uv run pytest -q -rs -p no:cacheprovider > "$S/pytest-after.out" 2>&1; echo "exit:$?"`:
```
exit:0
```

Summary line (`tail -n 1 "$S/pytest-after.out"`):
```
================= 1547 passed, 1 skipped in 127.63s (0:02:07) ==================
```

PYTEST_RESULT_AFTER = 1547 passed 1 skipped
(from `tail -n 1 "$S/pytest-after.out" | grep -oE '[0-9]+ (passed|failed|skipped|errors?|xfailed|xpassed)' | paste -sd' '`)

Equals `PYTEST_RESULT_BEFORE = 1547 passed 1 skipped`. Confirmed.

PYTEST_WARNINGS_AFTER = 0
(no "warnings summary" section in the output; informational only, matches
`PYTEST_WARNINGS_BEFORE = 0`)

Skip reasons (`-rs` short summary, every `SKIPPED` line):

~~~text pytest-skips-after
SKIPPED [1] tests/test_corpus_gate.py:530: SC#3 before/after measurement is env-gated -- set TYPSPHINX_CORPUS_REPORT=1 to run it (RESEARCH Open Question 1)
~~~

Compared against `pytest-skips-before` after stripping `:<line>:` numbers with
`sed -E 's/:[0-9]+:/:/'` and sorting both under `LC_ALL=C sort`:

```
$ diff skips-before-stripped.txt skips-after-stripped.txt
(empty — no differences)
```

SKIP_REASONS_MATCH = YES

Both `PYTEST_COLLECTED_AFTER` and `PYTEST_RESULT_AFTER` equal their base keys, from a run that
exited 0, and the skip reasons match after stripping line numbers.

LEG_B_VERDICT = MET

## Corpus list at HEAD (D-05)

Precondition: Task 1 committed with `LEG_B_VERDICT = MET` (commit `16ed7dfa`).
`70-CORPUS-DOCS-BASE-EVIDENCE.md` holds `CORPUS_CONTROL = EQUAL`, and its `PHASE_BASE_SHA_SEEN`
(`697a113221a8a267d7e8c6dd1f2b95672f9454d2`) equals 70-02's `PHASE_BASE_SHA`
(`697a113221a8a267d7e8c6dd1f2b95672f9454d2`). Precondition met.

Ran `git ls-tree -r --name-only HEAD -- tests | grep -E '(^|/)conf\.py$' | sed 's#/conf\.py$##' | LC_ALL=C sort > "$S/corpus-list.txt"`:

```
$ wc -l "$S/corpus-list.txt"
167
$ sha256sum "$S/corpus-list.txt"
30857d438df18b5625e96adb99437793eca0d32e34ba4ae155dabea790b50014
```

CORPUS_LIST_SHA256_AFTER = 30857d438df18b5625e96adb99437793eca0d32e34ba4ae155dabea790b50014

Equals `CORPUS_LIST_SHA256 = 30857d438df18b5625e96adb99437793eca0d32e34ba4ae155dabea790b50014` from
`70-CORPUS-DOCS-BASE-EVIDENCE.md`, and the line count (167) equals `CORPUS_PROJECT_COUNT = 167`.
Confirmed.

## D-08 pilot (after side)

Ran 70-03's corpus loop, unchanged, over the first five list entries into `$S/pilot`:

~~~text pilot-manifest-after
tests/fixtures/abbr_pep_separator_render_gate exit=0 typ=3 digest=d384efab0908d5039ea7c0de989e78e7fc49fbf7c3833121f2189069f3ac56ee
tests/fixtures/absolute_image_render_gate exit=0 typ=3 digest=6b48275ea61be0bf204e41f4789ae733c7660624b6ecd4ef59544854253030e7
tests/fixtures/admonition_greyscale_probe exit=0 typ=3 digest=a1eda1cf7e436ab6c2567844dbcdb99dede1d72894c33b337fdd9ae72d639910
tests/fixtures/admonition_locale_title_gate/en exit=0 typ=3 digest=851b4e99dcb08a6856fd855a9d5af71918af89c9f04304c57d0e5157132e310d
tests/fixtures/admonition_locale_title_gate/ja exit=0 typ=3 digest=fd68c78b01367bbfea18bd02aea032519c79eac718bf3fc32f64e8aec327db0d
~~~

Timing file (`$S/pilot-timing.txt`, one `<dir> <seconds>` line per project):

~~~text pilot-timing-after
tests/fixtures/abbr_pep_separator_render_gate 0.24088740348815918
tests/fixtures/absolute_image_render_gate 0.2164297103881836
tests/fixtures/admonition_greyscale_probe 0.21000003814697266
tests/fixtures/admonition_locale_title_gate/en 0.2131803035736084
tests/fixtures/admonition_locale_title_gate/ja 0.2165052890777588
~~~

CORPUS_PILOT_SECONDS_AFTER = 1.0970027446746826
CORPUS_EXTRAPOLATED_SECONDS_AFTER = 37
(sum ÷ 5 × 167, rounded up: 1.0970027446746826 / 5 * 167 = 36.639..., ceil = 37)

37 is well below 1800 — no HALT. The corpus is run in full, unnarrowed.

## Post-flip manifest

Ran the corpus loop over the whole 167-entry list into `$S/after`, with the manifest at
`$S/corpus-after.txt`:

```
$ date +%s.%N   # before
1757... 
$ <loop runs>
$ date +%s.%N   # after
1757...
elapsed: 39.35936427116394
```

CORPUS_FULL_SECONDS_AFTER = 39.35936427116394

```
$ sha256sum "$S/corpus-after.txt"
4c87a31da016b85f260915f6a0690c3fcf1602f17a0e2aa6a21725846d07464d
```

CORPUS_MANIFEST_SHA256_AFTER = 4c87a31da016b85f260915f6a0690c3fcf1602f17a0e2aa6a21725846d07464d

~~~text corpus-manifest-after
tests/fixtures/abbr_pep_separator_render_gate exit=0 typ=3 digest=d384efab0908d5039ea7c0de989e78e7fc49fbf7c3833121f2189069f3ac56ee
tests/fixtures/absolute_image_render_gate exit=0 typ=3 digest=6b48275ea61be0bf204e41f4789ae733c7660624b6ecd4ef59544854253030e7
tests/fixtures/admonition_greyscale_probe exit=0 typ=3 digest=a1eda1cf7e436ab6c2567844dbcdb99dede1d72894c33b337fdd9ae72d639910
tests/fixtures/admonition_locale_title_gate/en exit=0 typ=3 digest=851b4e99dcb08a6856fd855a9d5af71918af89c9f04304c57d0e5157132e310d
tests/fixtures/admonition_locale_title_gate/ja exit=0 typ=3 digest=fd68c78b01367bbfea18bd02aea032519c79eac718bf3fc32f64e8aec327db0d
tests/fixtures/admonition_render_gate exit=0 typ=3 digest=2f2ef1fb628b1e1e7cd82d88f976826f28ec4093d282fd42fc9d4adf13fbf802
tests/fixtures/bld02_duplicate_target_gate exit=2 typ=0 digest=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
tests/fixtures/bld02_path_shape_collision_gate exit=2 typ=0 digest=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
tests/fixtures/bld02_template_clobber_gate exit=2 typ=0 digest=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
tests/fixtures/bld03_ghost_entry_xref_gate exit=0 typ=5 digest=213b195cba6393d6d76d2b67c2fb79dbab3c0123479deacc6543dc74faf01cef
tests/fixtures/bld03_self_collision_gate exit=2 typ=0 digest=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
tests/fixtures/bld03_under_length_entry_gate exit=0 typ=4 digest=abddbb2d98f2322b951673c35a8eed52a493a2bc3f46b8c530bfbd0deda40328
tests/fixtures/bld03_unhashable_docname_gate exit=0 typ=3 digest=05929a1ebb2035182967f3340d456d6831955e75f038bee98821cefab4fcdca3
tests/fixtures/bld04_case_collision_gate exit=2 typ=0 digest=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
tests/fixtures/block_quote_markup_render_gate exit=0 typ=3 digest=f2b85232e912a458bbb60ab35a9b1af6dca1a29fc2fdeeddd0c59d574d3b9946
tests/fixtures/bundle_exclusion_manifest_gate exit=0 typ=3 digest=0152a9e69dbbfc9b48c2d99bba8b382a48b380314da8d607286cd07364c2725b
tests/fixtures/captioned_table_propagated_target_render_gate exit=0 typ=3 digest=9af5289e16612a365b627183498826dcb10423df8ca9b5a825413dcbfee3e37c
tests/fixtures/captioned_table_render_gate exit=0 typ=3 digest=0dab87ab07abe3123f55e5c5948d8b942fe07aed05b68f2634e88885096fb283
tests/fixtures/changelog_include_gate exit=0 typ=4 digest=ffe3776c2617d456fab9f06a48088ff09e8b5a2b97f001193fce95ac63c6bd78
tests/fixtures/citation_caption_dangling_label_gate exit=0 typ=3 digest=ddfcba3813752c26b85d0a3afec9132f6a8ba471aca346585a5033e44fef8140
tests/fixtures/citation_degradation_gate exit=0 typ=3 digest=c4f698f701fea896a845a81b23cd6de9fe387d7a0e7aa8e9b5e089cd01cfb706
tests/fixtures/citation_render_gate exit=0 typ=4 digest=90eb4436be3c393c565b91567108a61e7de67f423a0a9234c854522e6a3a0c90
tests/fixtures/codly_caption_listitem_leak_render_gate exit=0 typ=3 digest=79fa4482112fcadf76faf455c97b6514042be17bd5aa4aa7cd409407dc16a186
tests/fixtures/codly_config_leak_render_gate exit=0 typ=3 digest=8cee7ea9071a92e257577928545c98106b6556078ceebe0ad2258491cda2b945
tests/fixtures/codly_offset_render_gate exit=0 typ=3 digest=12afab0fc925c9c47aa8de6ee3eadb31c5be48928720221627b9b592b9730ad1
tests/fixtures/conf14_prewrite_bad_first_gate exit=2 typ=0 digest=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
tests/fixtures/conf14_prewrite_bad_last_gate exit=2 typ=0 digest=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
tests/fixtures/conf14_prewrite_control_gate exit=0 typ=6 digest=2a7300638a196662625ad0aa1e3c0220ea70e32131ae6a972d47f187710dc33e
tests/fixtures/conf17_prewrite_gate exit=2 typ=0 digest=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
tests/fixtures/confval_field_body_render_gate exit=0 typ=3 digest=121302e98f27ecf3170d53b66e61daf16032d2b93fd9a5205af3b76523921f30
tests/fixtures/confval_field_spacing_render_gate exit=0 typ=3 digest=080b08f9a8e8c0a19a9003d9b11c9a1e702ac4f7c16f14e6da653d3f55c63b3d
tests/fixtures/converted_image_collision_render_gate exit=0 typ=5 digest=a28e0658a01e5d5e5087b1ce2c4fb09e27fbb290d07380bf99f56edb85120a95
tests/fixtures/cross_doc_label_namespace_render_gate exit=0 typ=5 digest=e7d391b949825a01392fd20280e6515aa8fd68562e8c26de95974fde375360df
tests/fixtures/default_typst_documents_gate exit=0 typ=3 digest=98c35efbbc658ac9c6ec9006a6777588385182ee029b811143e86401f89099a2
tests/fixtures/deflist_definition_multiblock_render_gate exit=0 typ=3 digest=7e80bed6b3412e782213a8784fd7f30b6dcd0216d7caff93aa52900283a3362f
tests/fixtures/deflist_nested_definition_render_gate exit=0 typ=3 digest=5c66bc95f4b7c4e687ba584a56c7ec09b8661ae7b65c9e5e9cbaa64feea77ac6
tests/fixtures/deflist_term_concat_render_gate exit=0 typ=3 digest=f1ed277dd457b68daa0e3e54cf7d70c02543620db82dc592b5511346f79fc395
tests/fixtures/deflist_term_in_listitem_render_gate exit=0 typ=3 digest=5502026b09d3ba9ba72367575710a13dd174c6b70b9786ba78fc9c7d6b5d9ef6
tests/fixtures/deflist_term_inline_children_concat exit=0 typ=3 digest=3c624616d5e9b72fe7936e45abafa7eff154245a45ea28956f4409ca399607bd
tests/fixtures/deflist_term_nested_list_render_gate exit=0 typ=3 digest=32b5cce3ef07da6658a6bc8fa5165450319ff2a1efa88b1baca6f2c4ccd815c4
tests/fixtures/derived_docname_collision_gate exit=2 typ=0 digest=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
tests/fixtures/derived_template_collision_gate exit=2 typ=0 digest=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
tests/fixtures/desc_bodyless_concat_render_gate exit=0 typ=3 digest=eb8ccd0e1a79cf7b2e63617dc2a901f1b5891bff1ef39dc664e228bd2c7f17d1
tests/fixtures/desc_break_marker_buffer_swap_gate exit=0 typ=3 digest=2fa60daef52d2c63c1a0c81b49a6259181b648fb92ef2666cb12f184bc278782
tests/fixtures/desc_container_propagated_target_render_gate exit=0 typ=3 digest=cda726b0862b57c19135d33c00218b1333e5e8adeb7bfa8b06d64767b30f4c29
tests/fixtures/desc_content_indent_render_gate exit=0 typ=3 digest=ce56df5e7781fee571e736828b5e472cb9d96d6bcec4cf012116d3a6c05853f0
tests/fixtures/desc_rubric_decoupling_render_gate exit=0 typ=3 digest=629c6b60a26f1f3c5b1f18116b19416c4ae21a1bc7caedb17ff6b860f957ca8a
tests/fixtures/desc_sig_space_render_gate exit=0 typ=3 digest=67efcaeb4b2e3a32e395d7616ac3cff1d3eafebff6fc519de037c449fb97f805
tests/fixtures/desc_signature_anchor_render_gate exit=0 typ=3 digest=05d5e26d98dcb95bbbd6d3b75a183e543f40b50ec4586837194d7feb7c9964bf
tests/fixtures/desc_signature_concat_render_gate exit=0 typ=3 digest=093401cf62917fd9ea4d2d3070c3b43f6b85d58c7331e880233f58d71c5f5691
tests/fixtures/desc_signature_render_gate exit=0 typ=3 digest=b9c1dab5fcf6ad1edfe59531089fbdf831dcd1cfb7caa1a3f559c70808b9d3bf
tests/fixtures/desc_signature_siblings_render_gate exit=0 typ=3 digest=38388b4204792939470054d54937d422f62f5baae1af7aa1ea5f3ade9ff0fe96
tests/fixtures/documented_params_contract_gate exit=0 typ=4 digest=4836ae4f765afaa865cf9754fb5f30b6eecbb078a64ebe628d5168b16e16fdc6
tests/fixtures/duplicate_include_label_render_gate exit=0 typ=5 digest=dc45d6ae7c781d546cdc4532d2a9fdde6f7e1739f232f8a1aa8d85a8e489d1c1
tests/fixtures/empty_typst_documents_optout_gate exit=0 typ=1 digest=ba9539847064f3320e75d95529fa9647e39851d368d1ea958d6a4a75e526930b
tests/fixtures/entry_empty_metadata_render_gate exit=0 typ=3 digest=0f70d712e202985a937e7d0708c178f7452f0d6ddeb46ef330640543d4f7ae65
tests/fixtures/entry_title_author_render_gate exit=0 typ=4 digest=08c6dee61367c3db3a9526f0f9350a282dec87061e0f110645096dd5cff1df6d
tests/fixtures/epigraph_render_gate exit=0 typ=3 digest=feab7c2b98d1f2cbd6d66327d491f2d26f9146e010919cc0cedb6b60f9e8213d
tests/fixtures/explicit_docname_collision_gate exit=2 typ=0 digest=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
tests/fixtures/explicit_template_collision_gate exit=2 typ=0 digest=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
tests/fixtures/explicit_typst_documents_wins_gate exit=0 typ=3 digest=619add691740048babffbc469195b27e2f80f642ca2308e10e4c27668abeaf1e
tests/fixtures/external_link_style_render_gate exit=0 typ=3 digest=28a06fe2f905cb6792ddafacad82a1d7c313684b09faf93c59f463008adfcec9
tests/fixtures/field_body_typography_render_gate exit=0 typ=3 digest=7a13a5a6db37271651d4f04d13a6cbdd5e21be307d24369c76df5ba15bc27b64
tests/fixtures/field_list_in_list_item_render_gate exit=0 typ=3 digest=dfea5a9ab3499919fc2ed1c502a37adda7a4f9d25c9f3b1156f75eb90343ae12
tests/fixtures/figure_length_render_gate exit=0 typ=3 digest=2b8fc54bbb132684c383dd30d47e23a56b856a3f432d187b11aeef8b2574a155
tests/fixtures/figure_propagated_target_render_gate exit=0 typ=3 digest=66b22e1546d2213918ac3777f43ccff0715e416d5e4740f49cf9ae7045012a65
tests/fixtures/figure_target_caption_render_gate exit=0 typ=3 digest=3b735a824e65aba5f5f72b4ada517175a2f3a0a16b84023ba38dc93e150c983d
tests/fixtures/footnote_render_gate exit=0 typ=3 digest=d9322a58a55337e64188f940d4cc821e8f6a20240f9df4d18ce31f6914b51988
tests/fixtures/glob_image_render_gate exit=0 typ=3 digest=d73c6d1259464ff73d4cf36c9694c3926e1d32353edd917073fab6048ebffbf2
tests/fixtures/graphviz_degrade_render_gate exit=0 typ=3 digest=e69c5d8cadda17b79a3af2c92e820c11ca932e667e15ad7ca6f7cd63564057a2
tests/fixtures/inline_image_separator_render_gate exit=0 typ=46 digest=c7d0bb276ba6a4e3b794a7229271e39b841f4a718b2e5c9f0ea8e11be2b2b371
tests/fixtures/inline_literal_overflow_render_gate exit=0 typ=3 digest=1e015fb87f0887ac4ae75296d62e703fc110ec0fd216e20b70992738493945aa
tests/fixtures/inline_math_after_text_render_gate exit=0 typ=3 digest=3031afd2c1c6a48a4f1a7ac71e45ab88bf38d41f8873409e5f918377f8b34246
tests/fixtures/integration_basic exit=0 typ=3 digest=967e45409683cbba4fcdd4499fa3c6da6ddc3165f5da1264acfe1bd2da3207df
tests/fixtures/integration_math_figures exit=0 typ=3 digest=003af80fe0cb9fa6beeb68d24e2c8ae7cea346a2f0c9216ced9db632ec8265f5
tests/fixtures/integration_multi_doc exit=0 typ=5 digest=ebc9c2bb7a269f8b05ef2868fa34ca1b941968261786238e1e3a8621326ce48e
tests/fixtures/integration_multi_level exit=0 typ=7 digest=4872517e929b0d17490b5f0b938d907ebd605ae3de774d4f891472c35bebcf94
tests/fixtures/integration_nested_toctree exit=0 typ=6 digest=bd46a2f37a2980bda049702b8fa30d7443ac972e9b0f7eb38b750a9d346ca2a9
tests/fixtures/integration_sibling exit=0 typ=5 digest=a3ed6cdb40db77a91e482dac78723e3ac803b1ea979beaa584573fec9ca5b948
tests/fixtures/label_at_char_render_gate exit=0 typ=3 digest=a93872d83a7141c2e29c8acd20bf0987e7fce922fab091792f04b8845a5f9f06
tests/fixtures/list_item_nested_block_render_gate exit=0 typ=3 digest=d7cc1722e8854d77999bc641a8ec29533431c04369ffa503a246cc3587b03a34
tests/fixtures/manpage_render_gate exit=0 typ=3 digest=5302f38a87a6fded2839bfb46dbbfa57a3297607f995bd729d80b2e5fe94d02d
tests/fixtures/missing_and_malformed_master_gate exit=0 typ=4 digest=dc078ad4d98bcf266f1f48df69f22cd567abf058b80d59f3d6f16fce1a8922e4
tests/fixtures/mixed_prewrite_failures_a_gate exit=2 typ=0 digest=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
tests/fixtures/mixed_prewrite_failures_b_gate exit=2 typ=0 digest=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
tests/fixtures/nested_dir_multi_master exit=0 typ=5 digest=634fa77f46afc9ec9b5401510f714600d41f60d61338aee5200e22f74630be5a
tests/fixtures/nested_figure_render_gate exit=0 typ=3 digest=fad235f1235ecc23376dc442ce90f5b3c7eb4936027a687737164397977feaa2
tests/fixtures/nested_master_render_gate exit=0 typ=4 digest=ff5b3cfdc88c4c28eaa3e12b31cd8a5dc76956458bedcf87815e2c43ddfab723
tests/fixtures/nested_table_render_gate exit=0 typ=3 digest=ae5c2ad60cf1c4d92e718181b222f548bd5240efb2caebad6d77fb4265cdfaaa
tests/fixtures/non_str_docname_gate exit=0 typ=3 digest=87210f4e3ddecfa6d3a39078e79ecf17790a5d767cd172595f57282396f3c1ef
tests/fixtures/out02_escape_target_gate exit=0 typ=3 digest=78cf71c0aa6b974b53807ee12445432b0eccd13e53f5d4465465c2c96a501991
tests/fixtures/output_layout_bare_target_gate exit=0 typ=3 digest=51fdc6e12a05949cf491c2515af63677faef64c5997cb52c5e3c4da4e1633a56
tests/fixtures/output_layout_explicit_path_gate exit=0 typ=3 digest=735dff2921702a02f7b2ac6773fa9e4e58197389847c08974cf48d607e2b6796
tests/fixtures/output_layout_refused_absolute_gate exit=0 typ=3 digest=b33351e0b0b9e1231fdba29a71157f78afd41e1f59c5c21d35086f9a2c33378f
tests/fixtures/output_layout_refused_drive_gate exit=0 typ=3 digest=f29222a7eac19fa90f85fc2cbad6a7a79975a9c77cdf71f452ba56573b37d4b6
tests/fixtures/output_layout_refused_parent_gate exit=0 typ=3 digest=6201319d192f18bfb55810693ab75aff2ce491116435c6837675e26809995503
tests/fixtures/package_only_config_gate exit=0 typ=2 digest=98442aef76dc496c8a0d75091e09a1b2973e2eb885ba3656fa9d7382787ea938
tests/fixtures/paragraph_concat_render_gate exit=0 typ=3 digest=78f2ed7d5ca79d904c0bb26e58d7d1c29e64746f08bb3abd82bc1e59093fe3dd
tests/fixtures/paragraph_propagated_target_render_gate exit=0 typ=3 digest=8d71b4ad1fc0ef26b0dc5ac63c537dc0db64fac990a2553a1f933aef72207210
tests/fixtures/paragraph_soft_newline_render_gate exit=0 typ=3 digest=4a230d1a438d9f47b3b0473974a05088b8542a1b7ddc4febe77614c3e0710c02
tests/fixtures/params_exclusivity_gate/package_params exit=0 typ=2 digest=8368da7028014e9a89f5f37b4a161fc8130ce6f2d6f6dbb583900aff2447bbf0
tests/fixtures/params_exclusivity_gate/partial_params_template exit=0 typ=4 digest=ac5f4850a3fc70206472f1ae24d515b0567fece4ee105824e72e38e84ed91cac
tests/fixtures/params_exclusivity_gate/zero_params_default exit=0 typ=3 digest=48da88d6bec574897485aa26dbae90ec839c923be94ae30093dd38cdec65e585
tests/fixtures/params_exclusivity_gate/zero_params_template exit=0 typ=4 digest=c030e51b1f22f84cad59b1f4b8563104b7ea15c1c136958eb61df907880ba7c9
tests/fixtures/preview_smoke exit=0 typ=3 digest=2c64d5b460ff5916d7cdaf94b89f7e3395043b7d79899bb99190ecdb8aa0f442
tests/fixtures/quickstart_docs_gate exit=0 typ=3 digest=5abb49cf9eae20fe347e79b7fbbb05aeff8006218a9874bfe67de206f2cfdc17
tests/fixtures/ref_target_nested_list_render_gate exit=0 typ=3 digest=d429dfec54b287a81554818915a8e5a6ce069fb6e3a117f6c994c9d3caf91740
tests/fixtures/registry_container_shape_gate exit=2 typ=0 digest=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
tests/fixtures/reserved_key_case_prewrite_gate exit=2 typ=0 digest=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
tests/fixtures/rubric_indent_invariance_gate exit=0 typ=3 digest=b27a64970e35baafe407f072207ba0b114b560c84168ea7d39608f8de4ab40e8
tests/fixtures/rubric_option_concat_render_gate exit=0 typ=3 digest=6432a402d1814b73cc92c4c3f7e328a6c55f2b60f2be83d0c42696d972a763ed
tests/fixtures/rubric_propagated_target_render_gate exit=0 typ=3 digest=aad857153b8016d9dd1649cbcabf1d47a73168c2b5a8fdd2b3d32c6a8b2cddb9
tests/fixtures/rubric_strong_nesting_render_gate exit=0 typ=3 digest=1caabe88561ef518c4b1ae2c314ed32e45eea269fa14153a6722c7521883e347
tests/fixtures/signature_break_and_arrow_gate exit=0 typ=3 digest=c4a5730aae42350ebecbd283ec0f420c33b5c8782eca5b22d48e4604c22acd41
tests/fixtures/signature_overflow_render_gate exit=0 typ=3 digest=510895113eb7ecaa5bb159196465f1281919053877dcba4f55277e6fd20b5bf3
tests/fixtures/signature_page_boundary_render_gate exit=0 typ=3 digest=6c589ffa62f9bd34c1af4ce984a3a64065695c884dbb0ea1717c87662f46b417
tests/fixtures/signature_typography_gate exit=0 typ=3 digest=b51037dcf23ae7312534ba06ba12757aa732dc7f3c451c87da089d0aa75db1bd
tests/fixtures/state_guard_cycle_gate exit=0 typ=4 digest=fd65667b79901519a0504002462fdfa4b846e1b78d9ddafd77a8af1e6c6c4366
tests/fixtures/state_guard_glob_gate exit=0 typ=6 digest=060f4de1a8ee241cb7abd9eeb1b5c3bdbc58ddd16bb84d0995bbf515d3688c47
tests/fixtures/state_guard_mirror_pair_gate exit=0 typ=9 digest=6218a2a01931fff6bb7cc5a26c22758c3dffddce19446cadbdc1f7528275c3cb
tests/fixtures/state_guard_numref_two_case_gate exit=0 typ=7 digest=b276ab9bf0b207554faf228b9c04da4f09ea4551cbb7873078c831647e48273e
tests/fixtures/state_guard_orphan_ref_gate exit=0 typ=4 digest=d48b35bf009c2fe56a10ae45c440c7e2128c842f79f609ec3ed0ffb7f0e1fca6
tests/fixtures/state_guard_self_and_url_gate exit=0 typ=4 digest=0056779b5ff4c66f36370cdeef9a4f73b7079a97bf09d909c2b8777ce733076c
tests/fixtures/state_guard_selfref_gate exit=0 typ=4 digest=c4debe01ca2399330ea9b140bedf492fc1e468c8b8580ea87b8a943e2a62b7d3
tests/fixtures/state_guard_substring_key_gate exit=0 typ=5 digest=ddffd57bf7be7e898833c810e7973ee0c9e26734ab245d5f248bdd61f49c9a41
tests/fixtures/state_guard_three_master_gate exit=0 typ=10 digest=cb8b78e26546758a0d540bdb108f3ece0efed0d5675f1d4e41e1212eed3e7ea9
tests/fixtures/state_guard_two_master_gate exit=0 typ=9 digest=1f3966ad3c7045369a3a60c7c42d2dd013a2e8b9c81a7f10da1a7e9fa25b1e90
tests/fixtures/static_asset_copy_render_gate exit=0 typ=3 digest=7f8c30b55bdf272e6a881e6b6acbbc81c5eeaa4812cc4eb425c73de50a06f55e
tests/fixtures/substitution_definition_render_gate exit=0 typ=3 digest=d7fffc91dec8740b4a061bf48c8c814bdc2a0df6d5b61271d8cf858cb6338b98
tests/fixtures/table_empty_caption_anchor_render_gate exit=0 typ=3 digest=433332c4b40c2037a876a8aeeccc16bbd8baca10f6e8ea1e6b4b2c850bca6abd
tests/fixtures/table_in_list_item_render_gate exit=0 typ=3 digest=a7892de305d910f203fc13e74d8b6a96697cc593597f52962b0c8cba08a7758d
tests/fixtures/table_width_render_gate exit=0 typ=3 digest=fd2d35d27406080e313c783ec04f2eaee89a984aa59dfa0d0a99a918f378b610
tests/fixtures/target_label_render_gate exit=0 typ=3 digest=e34ea2a045c74d1e77c605d1d30f2a5e7bfda44e25f73b1e5bdefbc3d7bd3b58
tests/fixtures/template_prefix_reservation_gate exit=2 typ=0 digest=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
tests/fixtures/templates_path_absent_control_gate exit=0 typ=3 digest=5676ed98d3f54f7f69bbfab377aa9367ddef66ce1bc8129b20222714555e5687
tests/fixtures/templates_path_adjacent_control_gate exit=0 typ=3 digest=2a688166aa4517d25f353d34273af24d2bc97f8345c5952bf402648ddda5a567
tests/fixtures/templates_path_collision_gate exit=2 typ=0 digest=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
tests/fixtures/templates_path_collision_multi_gate exit=2 typ=0 digest=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
tests/fixtures/templates_path_default_documents_gate exit=2 typ=0 digest=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
tests/fixtures/templates_path_no_typst_template_control_gate exit=0 typ=3 digest=2a675b33187dcad96c229d692205134ecb1c4bb12929292c5b2d99e55449cc6b
tests/fixtures/todo_render_gate exit=0 typ=3 digest=77055211a76bcde8b83ce85074e2330318a8228e515bbc65f42fa96e7a26ea3e
tests/fixtures/topic_line_block_render_gate exit=0 typ=3 digest=cce84b786ecfaecee36dfa2b6512f83d0f0787028df28326f7a3cc355e2beb16
tests/fixtures/trivial_blocks_render_gate exit=0 typ=3 digest=13c68786c0f15ed7a290e6dafa0aec96819ea8f6f5b40aa506f21493d7204f71
tests/fixtures/two_key_selection_gate exit=0 typ=8 digest=f659e45dd265c56056fc048d390dd8538dc0e5a59848a7aec49dd7f02e755e74
tests/fixtures/two_layer_nested_master_gate exit=0 typ=5 digest=642315da969afc08f46e9644e2b4bd64ef1e9ef24d65d18dec30c1e1d48667d3
tests/fixtures/two_layer_root_master_gate exit=0 typ=3 digest=a11dca6c74bebe158f3efc16cfdea89c365dacb553616cc14f216632e8c446ef
tests/fixtures/typst_elements_pass_through_gate/fontsize_positive exit=0 typ=3 digest=bfc63633ba3adba81956a0e67c827f5a5633954ce2184fa55978db1f04b52ad7
tests/fixtures/typst_elements_pass_through_gate/papersize_positive exit=0 typ=3 digest=3eff68a0f3c44cfff10924250f97fd7b3e17f7bfd0822ade88d7d0b1cbbdd51f
tests/fixtures/typst_elements_pass_through_gate/unknown_key_negative exit=2 typ=1 digest=9692f0c3075d334451d5bbcb88ca500c368682659a1919045c8c2c85b5a4a019
tests/fixtures/typst_lang_gate/custom_template_lang exit=0 typ=3 digest=7280cfeabb5450d9177ad919c2b1985028fef81b987a768b560187ee67e437df
tests/fixtures/typst_lang_gate/de_default exit=0 typ=3 digest=e8447a31ebb5210d0f9e1ab586287f5a27f89bbec48ca51a5f82735347c90b71
tests/fixtures/typst_lang_gate/ja_default exit=0 typ=3 digest=88c41d0f4d9fbe58023c19a006a86c8436e1fc0f32c8fd30a54bd2f4acbee598
tests/fixtures/typst_lang_gate/malformed_language exit=0 typ=3 digest=0a85d1684f5e59ce4597ecb381ab5ca55819a839ba7446ea3b83cbc1d79a8cd6
tests/fixtures/typst_lang_gate/null_elements exit=0 typ=3 digest=aca5b363565810ae46148b38675c57e5e4a0a33e7f0459eaf70b743019a6f181
tests/fixtures/typst_lang_gate/package_no_lang exit=0 typ=2 digest=4d89a0f4099d553983da34eb2bd820cf637efbcf3f46382a4c5188bcb4899f0e
tests/fixtures/typst_lang_gate/precedence exit=0 typ=3 digest=d6354958529b8e97146d22abf9425aff7aef914c6a7490df9e5db0437354c796
tests/fixtures/typst_lang_gate/srcdir_shadow_lang exit=0 typ=3 digest=8769ceee6e32aa35ca92880c69f00e9ca100264574901131d9203777e0cb8467
tests/fixtures/user_template_relative_asset_gate exit=0 typ=3 digest=efbb1b68fefa1743b7333216329ac73730b33da7d0fc029cfd5483815eed9bc8
tests/fixtures/version_modified_render_gate exit=0 typ=3 digest=ee1b3bb18f3931b8c57cd3a895b242ad1f5852d28b6c2fa128bb6feabca2417a
tests/fixtures/wide_table_render_gate exit=0 typ=3 digest=eb20bd31b7555810cfabbca66ea52d74204b2f8b5cbc998b3151bf76f59bb2e9
tests/fixtures/windows_shaped_image_uri_gate exit=0 typ=3 digest=5ccde22610f3b75cdaba473f957899c3c7736eb98d094801b8020ef32045db6e
tests/fixtures/xref_label_collision_guard_gate exit=0 typ=5 digest=1dfd9f8c311bb2940c17a1b27337e11eaf3b416dcbc16937a6ab0a3986e45555
tests/fixtures/xref_orphan_degrade_render_gate exit=0 typ=5 digest=28c1234d7c78d1b26b634888e5fbca8d59b8ec67502dc37f5e6083896b9a51cd
tests/fixtures/xref_per_master_guard_gate exit=0 typ=6 digest=c374c943d5bed4f9ffb0df74d2b77ef9257aed2179bf59452bb3bd7c8feddd99
tests/fixtures/xref_refid_render_gate exit=0 typ=3 digest=de36c1f2d7f88abed8c5bdc66f34e5e86d1ad20496e6f751d1c13cfe87f003fc
tests/fixtures/xref_whole_document_guard_gate exit=0 typ=5 digest=061ee5df2673dd3c5a3e0bfca67307aedd6700cf391d0a38bbef53d61865f988
tests/roots/test-basic exit=0 typ=3 digest=8d9e730e0d66a3288d0ee9c30eabf89d50a8b033271cd812176cf64242010b47
~~~

`cmp` of `$S/corpus-after.txt` against the `corpus-manifest` block extracted from
`70-CORPUS-DOCS-BASE-EVIDENCE.md`:

```
$ cmp "$S/corpus-after.txt" base-manifest-extracted.txt; echo "exit:$?"
exit:0
```

The two hashes are equal (`CORPUS_MANIFEST_SHA256_AFTER` = `CORPUS_MANIFEST_SHA256_BEFORE` =
`4c87a31da016b85f260915f6a0690c3fcf1602f17a0e2aa6a21725846d07464d`), and `cmp` exits 0. Every
project, including the 21 failing/zero-output ones (D-06; `CORPUS_NONZERO_EXIT_COUNT = 21` on both
sides), has the same exit code, `.typ` count and `.typ` digest, on the identical 167-entry list in
identical order.

LEG_D_VERDICT = MET
