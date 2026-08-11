"""
DOC-13's permanent cross-page contract-claim guard (Phase 45.1, plan 07
gap closure).

**What this locks.** ``45.1-VERIFICATION.md`` truth 2b: the published
documentation and typsphinx's shipped behaviour agree in both directions
across the reader-visible doc set, not merely within ``templates.rst``.
Plan 06's own SC#2 two-way agreement proof read ``templates.rst`` alone and
never touched ``configuration.rst`` -- which is exactly how the gap this
plan closes (45.1-REVIEW.md CR-01: ``configuration.rst``'s "Document
Language" section still published the pre-CONF-12 route-scope rule)
escaped that single-page enumeration. This module is the regression lock
against that CLASS of gap recurring: a claim published on a page the
agreement proof never reads.

**Subject: published prose, not emitted output.** Every real-compile
"does the code do what it says" proof already lives in
``tests/test_documented_params_contract_gate.py`` and
``tests/test_typst_lang_gate.py``. This module asks a different question --
does the PROSE agree with the code's own predicate -- and answers it by
reading ``docs/source/**/*.rst`` and calling one Python function
(``typsphinx.template_engine.TemplateEngine.uses_bundled_default_template``).
No ``typst-py`` dependency, no ``sphinx-build`` subprocess: this module
never skips.

**The D-J fence.** D-A/D-J (owner decision, 45.1-CONTEXT.md) declined a
lockstep sync test over the contract's parameter-NAME declaration surfaces
-- ``typsphinx/templates/base.typ``, ``templates.rst``, and
``docs/source/_typst/custom_template.typ`` (the unguarded fourth
lockstep site the v0.6.4 review flagged, still unguarded by design). This
guard checks a different axis entirely: route-SCOPE claim correctness
(which routes the docs say receive or are denied ``lang``) and claim-page
enumeration closure. It contains no parameter-name-list comparison across
those three declaration surfaces and does not read ``custom_template.typ``
at all -- do not extend it across that fence.

**T-45.1-21 / T-45.1-22 (45.1-VERIFICATION.md threat register).** A
single-page proof standing in for a doc-set-wide claim, and a prose guard
that matches nothing and passes vacuously, are both mitigated below:
``TestContractClaimPageEnumerationIsClosed`` closes the page set by
assertion in both directions, and ``TestForbiddenClaimDetectorIsFailFirst``
proves the classifier is not a no-op against the real pre-fix text.
"""

import re
from pathlib import Path

from typsphinx.template_engine import TemplateEngine

REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_SOURCE_DIR = REPO_ROOT / "docs" / "source"

# --------------------------------------------------------------------------
# Route truth, derived from code -- never from prose.
# --------------------------------------------------------------------------

# Five real TemplateEngine constructions covering every route this guard
# cares about. No template file needs to exist on disk: the predicate this
# module asserts against reads only `self.typst_package` (see
# TemplateEngine.uses_bundled_default_template()'s own docstring), so a
# fake path is enough. The two `typst_package` variants are tested
# separately -- the "alone" case is what tests/fixtures/typst_lang_gate/
# package_no_lang/conf.py already covers; the "combined with an explicit
# typst_template" case is deliberately absent from every fixture there
# (see that file's own comment) -- this is the CONF-12 adjacency edge.
ROUTE_CONFIGS = {
    "bundled_default": {},
    "explicit_template": {"template_path": "/nonexistent/custom.typ"},
    "srcdir_shadow": {
        "template_name": "base.typ",
        "search_paths": ["/nonexistent/srcdir"],
    },
    "typst_package_alone": {"typst_package": "@preview/charged-ieee:0.1.4"},
    "typst_package_and_typst_template": {
        "typst_package": "@preview/charged-ieee:0.1.4",
        "template_path": "/nonexistent/custom.typ",
    },
}


def _withheld_routes_from_code() -> frozenset:
    """
    The set of ROUTE_CONFIGS route names for which
    ``uses_bundled_default_template()`` returns ``False`` -- i.e. the
    routes on which the shipped code withholds the auto-derived ``lang``
    argument. Read from a real construction of the code's own class, not
    transcribed.
    """
    return frozenset(
        name
        for name, kwargs in ROUTE_CONFIGS.items()
        if not TemplateEngine(**kwargs).uses_bundled_default_template()
    )


CODE_WITHHELD_ROUTES = _withheld_routes_from_code()
CODE_AFFIRMED_ROUTES = frozenset(ROUTE_CONFIGS) - CODE_WITHHELD_ROUTES

# --------------------------------------------------------------------------
# Claim-page enumeration -- closed in both directions, never open-ended.
# --------------------------------------------------------------------------

PUBLISHED_PARAM_NAMES = (
    "title",
    "authors",
    "date",
    "papersize",
    "fontsize",
    "lang",
    "toctree_maxdepth",
    "toctree_numbered",
    "toctree_caption",
)

# Route/config tokens a page must mention (as an RST inline literal,
# alongside a published parameter name) to count as publishing a contract
# claim at all. Broader than ROUTE_TOKEN_TO_ROUTES below, which is scoped
# specifically to lang route-scope attribution: "``typst_elements``" is
# included here because it is the config surface that carries the
# allowlisted keys across pages, and docs/source/changelog.rst's
# historical release note trips on exactly this broader net (it names
# ``papersize``/``fontsize``/``lang`` as the allowlist inside a
# ``typst_elements`` sentence) -- which is why that page needs a reviewed
# exclusion rather than passing a bare scan silently.
CLAIM_ROUTE_TOKENS = (
    "``typst_template``",
    "``typst_package``",
    "``base.typ``",
    "``typst_elements``",
    "bundled default",
    "default template",
)

REVIEWED_CLAIM_PAGES = frozenset(
    {
        "docs/source/user_guide/configuration.rst",
        "docs/source/user_guide/templates.rst",
        "docs/source/examples/advanced.rst",
    }
)

EXCLUDED_CLAIM_PAGES = {
    "docs/source/changelog.rst": (
        "A historical release-note migration guide (documenting the "
        "0.5.x -> 0.6.x typst_elements allowlist change at the time it "
        "shipped), not a live claim about the current build's behaviour."
    ),
}


def _iter_rst_pages() -> list:
    """Every ``*.rst`` file under ``docs/source/``, in sorted order."""
    return sorted(DOCS_SOURCE_DIR.rglob("*.rst"))


def _page_makes_contract_claim(text: str) -> bool:
    """
    True for a page that mentions at least one published parameter name
    as an RST inline literal AND at least one route/config token --
    the bare scan this module's page-closure test runs before any human
    review, per CLAIM_ROUTE_TOKENS above.
    """
    has_param_name = any(f"``{name}``" in text for name in PUBLISHED_PARAM_NAMES)
    has_route_token = any(token in text for token in CLAIM_ROUTE_TOKENS)
    return has_param_name and has_route_token


def _discovered_claim_pages() -> set:
    return {
        page.relative_to(REPO_ROOT).as_posix()
        for page in _iter_rst_pages()
        if _page_makes_contract_claim(page.read_text(encoding="utf-8"))
    }


# --------------------------------------------------------------------------
# Lang route-scope claim classifier -- purpose-built for this docs corpus,
# not a general natural-language parser.
# --------------------------------------------------------------------------

DERIVATION_TOKENS = ("derive", "derived", "derivation", "auto-derived")

# Negated-applicability wording, exclusive-scope wording, "withheld",
# "never" -- the vocabulary this docs corpus uses to deny a route.
WITHHOLDING_TOKENS = (
    "withheld",
    "never",
    "except",
    "does not apply",
    "do not apply",
    "not apply",
    "only when",
)

# Bare-substring route tokens (no backtick requirement -- a superset of
# the backtick-wrapped CLAIM_ROUTE_TOKENS above) mapped onto the
# ROUTE_CONFIGS name(s) each stands for. A "typst_package" mention maps
# to BOTH package routes: the docs never distinguish "typst_package
# alone" from "typst_package + typst_template" by name, and the D-I rule
# withholds lang identically in either combination, so a doc claim about
# "typst_package" is a claim about their union.
ROUTE_TOKEN_TO_ROUTES = {
    "typst_package": frozenset(
        {"typst_package_alone", "typst_package_and_typst_template"}
    ),
    "typst_template": frozenset({"explicit_template"}),
    "base.typ": frozenset({"srcdir_shadow"}),
    "bundled default": frozenset({"bundled_default"}),
    "default template": frozenset({"bundled_default"}),
}

# The verbatim pre-fix route-scope claim from
# docs/source/user_guide/configuration.rst as it stood at commit
# d952a8f (this plan's own base, before Task 1), quoted by
# 45.1-REVIEW.md CR-01. This is a synthetic known-violation STRING fed
# directly to the classifier below -- not a build against the pre-fix
# tree.
PRE_FIX_FALSE_CLAIM = (
    "Automatic derivation applies **only** when the bundled default "
    "template is what actually gets used. It does **not** apply when "
    "``typst_template`` is configured, when ``typst_package`` is "
    "configured, or when a file named ``base.typ`` sits next to your "
    "``conf.py`` in the source directory (which silently shadows the "
    "bundled template)."
)


def _find_route_tokens(text: str) -> set:
    return {token for token in ROUTE_TOKEN_TO_ROUTES if token in text}


def _classify_sentence(text: str):
    """
    Classify a prose chunk's route-token mentions as affirmed or
    withheld, for the lang-derivation route-scope claim it makes.
    Returns ``(affirmed_routes, withheld_routes)`` as two disjoint
    frozensets of ROUTE_CONFIGS names.

    Purpose-built for this docs corpus's two grammatical shapes, not a
    general natural-language parser:

    - "applies ... except X" / "... withheld ... when X" -- X is
      withheld. Identified by a short window immediately after the
      marker, bounded at the next comma/colon/period so it cannot reach
      past the named route into unrelated later text in the same chunk
      (the post-fix "Scope: every non-package route" shape).
    - "does not apply when A, when B, or when C" -- every route token in
      the REST of the chunk after the marker is withheld, since the
      pre-fix shape enumerates its withheld routes at length after this
      marker rather than immediately beside it.

    Any route token mentioned in the chunk that is not captured as
    withheld by either rule above defaults to affirmed -- a route named
    in a chunk that overall talks about deriving/receiving the argument,
    with no negation attached to that specific mention, is a claim that
    the route receives it.
    """
    lowered = text.lower()
    withheld_tokens: set = set()

    except_match = re.search(r"except\*{0,2}\s+([^,:.]{0,40})", lowered)
    if except_match:
        withheld_tokens |= _find_route_tokens(except_match.group(1))

    not_apply_match = re.search(
        r"(?:does\s+\*{0,2}not\*{0,2}\s+apply|not\s+apply)\b(.*)",
        lowered,
        re.DOTALL,
    )
    if not_apply_match:
        withheld_tokens |= _find_route_tokens(not_apply_match.group(1))

    withheld_word_match = re.search(r"withheld\b(.{0,100})", lowered)
    if withheld_word_match:
        withheld_tokens |= _find_route_tokens(withheld_word_match.group(1))

    all_tokens = _find_route_tokens(lowered)
    affirmed_tokens = all_tokens - withheld_tokens

    def _union(tokens: set) -> frozenset:
        result: set = set()
        for token in tokens:
            result |= ROUTE_TOKEN_TO_ROUTES[token]
        return frozenset(result)

    withheld_routes = _union(withheld_tokens)
    affirmed_routes = _union(affirmed_tokens) - withheld_routes
    return affirmed_routes, withheld_routes


def _claim_sentences(text: str) -> list:
    """
    Split page prose into paragraph-level chunks (blank-line-separated
    RST paragraphs -- the "sentence" unit this module classifies), after
    stripping ``.. code-block::`` directive bodies so Typst/Python
    source lines are never mistaken for prose.

    A chunk qualifies as a lang route-scope claim only when it mentions
    a derivation keyword, a route token, AND the literal ``lang``
    parameter name. The ``lang`` requirement is load-bearing: this docs
    corpus also uses "auto-derived" + route-token language for the
    UNRELATED title/authors/date params-exclusivity rule (CONF-11,
    ``configuration.rst``'s "Precedence" subsection), which must not be
    mistaken for a lang-specific claim -- that subsection never names
    ``lang`` at all.
    """
    no_code_blocks = re.sub(
        r"(?m)^\.\. code-block::[^\n]*\n\n(?:[ \t]+.*\n|\n)*", "", text
    )
    paragraphs = re.split(r"\n\s*\n", no_code_blocks)
    qualifying = []
    for para in paragraphs:
        normalized = " ".join(para.split())
        if not normalized:
            continue
        lowered = normalized.lower()
        has_derivation = any(token in lowered for token in DERIVATION_TOKENS)
        has_route = bool(_find_route_tokens(lowered))
        has_lang = "``lang``" in normalized
        if has_derivation and has_route and has_lang:
            qualifying.append(normalized)
    return qualifying


def _reviewed_pages_text() -> list:
    return [
        (path, (REPO_ROOT / path).read_text(encoding="utf-8"))
        for path in sorted(REVIEWED_CLAIM_PAGES)
    ]


def _withheld_routes_claimed(pages) -> frozenset:
    """Union, across every page, of routes any qualifying sentence claims lang is withheld on."""
    withheld: set = set()
    for _, text in pages:
        for sentence in _claim_sentences(text):
            _, sentence_withheld = _classify_sentence(sentence)
            withheld |= sentence_withheld
    return frozenset(withheld)


def _routes_affirmed(pages) -> frozenset:
    """Union, across every page, of routes any qualifying sentence claims lang is affirmed on."""
    affirmed: set = set()
    for _, text in pages:
        for sentence in _claim_sentences(text):
            sentence_affirmed, _ = _classify_sentence(sentence)
            affirmed |= sentence_affirmed
    return frozenset(affirmed)


# --------------------------------------------------------------------------
# Tests
# --------------------------------------------------------------------------


class TestContractClaimPageEnumerationIsClosed:
    """
    T-45.1-21 mitigation: the claim-page set is closed by assertion in
    both directions, so a new claim-bearing page or a rotted exclusion
    cannot silently escape the two-way agreement check below (this is
    the hole that let CR-01's gap through plan 06's templates.rst-only
    SC#2 enumeration).
    """

    def test_discovered_claim_page_set_is_non_empty(self):
        discovered = _discovered_claim_pages()
        assert discovered, (
            "The claim-page scan discovered zero pages -- a vacuous scan "
            "would let this guard pass without ever checking anything. "
            "If the docs tree genuinely has no contract-claim page left, "
            "this assertion itself must be revisited, not silently "
            "satisfied."
        )

    def test_discovered_minus_excluded_equals_reviewed(self):
        discovered = _discovered_claim_pages()
        reviewed_or_excluded = discovered - set(EXCLUDED_CLAIM_PAGES)
        assert reviewed_or_excluded == REVIEWED_CLAIM_PAGES, (
            f"Discovered claim pages minus exclusions "
            f"{sorted(reviewed_or_excluded)} != the reviewed set "
            f"{sorted(REVIEWED_CLAIM_PAGES)}. A newly claim-bearing page "
            f"was found that is in neither list -- review its claims "
            f"against typsphinx/template_engine.py and add it to "
            f"REVIEWED_CLAIM_PAGES (if it agrees) or EXCLUDED_CLAIM_PAGES "
            f"(with a reason, if it is not a live claim)."
        )

    def test_every_excluded_page_still_makes_a_claim(self):
        discovered = _discovered_claim_pages()
        stale = set(EXCLUDED_CLAIM_PAGES) - discovered
        assert not stale, (
            f"{sorted(stale)} are in EXCLUDED_CLAIM_PAGES but no longer "
            f"make a contract claim under the current scan -- a stale "
            f"exclusion. Remove them from EXCLUDED_CLAIM_PAGES."
        )


class TestLangRouteScopeClaimsMatchShippedPredicate:
    """
    DOC-13 truth 2b: the published documentation and the shipped
    predicate (``TemplateEngine.uses_bundled_default_template()``) agree
    in both directions, proved by set equality across every REVIEWED
    claim page -- not ``templates.rst`` alone.
    """

    def test_code_withheld_routes_is_both_package_combinations(self):
        # CONF-12 / edge: adjacency -- the both-inputs-set case
        # (typst_package AND an explicit typst_template together) is
        # asserted directly, not left implicit; no fixture under
        # tests/fixtures/typst_lang_gate/ covers this combination (see
        # package_no_lang/conf.py's own comment).
        assert CODE_WITHHELD_ROUTES == frozenset(
            {"typst_package_alone", "typst_package_and_typst_template"}
        )

    def test_docs_withheld_routes_equal_code_withheld_routes(self):
        # Direction 1: nothing the docs deny is something the code
        # actually does.
        pages = _reviewed_pages_text()
        claimed_withheld = _withheld_routes_claimed(pages)
        assert claimed_withheld == CODE_WITHHELD_ROUTES, (
            f"Docs claim lang is withheld on {sorted(claimed_withheld)}, "
            f"but the shipped predicate withholds it on "
            f"{sorted(CODE_WITHHELD_ROUTES)}."
        )

    def test_docs_affirmed_routes_equal_code_affirmed_routes(self):
        # Direction 2: nothing the code does goes unpublished.
        pages = _reviewed_pages_text()
        claimed_affirmed = _routes_affirmed(pages)
        assert claimed_affirmed == CODE_AFFIRMED_ROUTES, (
            f"Docs affirm lang derivation on {sorted(claimed_affirmed)}, "
            f"but the shipped predicate affirms it on "
            f"{sorted(CODE_AFFIRMED_ROUTES)}."
        )


class TestForbiddenClaimDetectorIsFailFirst:
    """
    T-45.1-22 mitigation: this guard's own classifier is proved to have
    teeth, RED-proved against PRE_FIX_FALSE_CLAIM -- the verbatim
    pre-fix text 45.1-REVIEW.md CR-01 quotes. Fed directly to the
    classifier (not via a page walk), so a detector that silently
    matches nothing is caught here rather than certifying agreement.
    """

    def test_pre_fix_claim_is_detected_as_withholding_a_route_the_code_affirms(
        self,
    ):
        _, withheld = _classify_sentence(PRE_FIX_FALSE_CLAIM)
        falsely_withheld = withheld - CODE_WITHHELD_ROUTES
        assert falsely_withheld, (
            "The forbidden-claim detector did not flag the verbatim "
            "pre-fix sentence as withholding a route the code actually "
            "affirms -- the detector matched nothing and this guard "
            "would have passed vacuously against the exact text CR-01 "
            "identified as the gap."
        )
        # The pre-fix claim specifically denies lang on the explicit
        # typst_template and <srcdir>/base.typ routes, both of which the
        # code (post-CONF-12) actually affirms -- this is the concrete
        # harm CR-01 recorded.
        assert {"explicit_template", "srcdir_shadow"} <= falsely_withheld

    def test_affirmative_detector_fires_on_a_known_good_sentence(self):
        known_good = (
            "Automatic derivation applies on every route except "
            "``typst_package``: an explicit ``typst_template`` and the "
            "bundled default template both receive the auto-derived "
            "``lang`` argument unconditionally."
        )
        affirmed, withheld = _classify_sentence(known_good)
        assert affirmed, "The affirmative detector matched nothing."
        assert "explicit_template" in affirmed
        assert "bundled_default" in affirmed
        assert "typst_package_alone" in withheld
