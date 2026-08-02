import random
import re

import pytest

from question_bot.generator import Provider, QuestionGenerator, provider_from_env
from question_bot.truth import TruthService, load_truths


def test_truth_fallback_lists_are_large_unique_and_varied():
    for nsfw in (False, True):
        questions = load_truths(nsfw)
        openings = {" ".join(question.lower().split()[:4]) for question in questions}
        assert len(questions) >= 250
        assert len(questions) == len(set(questions))
        assert len(openings) >= 50
        assert all(question.endswith("?") for question in questions)
        assert all(len(question) <= 180 for question in questions)


def test_truth_lists_cover_classic_truth_or_dare_topics():
    safe = " ".join(load_truths(False)).lower()
    nsfw = " ".join(load_truths(True)).lower()

    for topic in ("embarrass", "lie", "secret", "regret", "crush", "jealous"):
        assert topic in safe
    for topic in ("sex", "orgasm", "fantasy", "turn-on", "naked", "sext"):
        assert topic in nsfw


def test_truth_nsfw_list_is_explicit_but_excludes_abuse():
    questions = load_truths(True)
    explicit = (
        "fuck",
        "blowjob",
        "oral sex",
        "anal",
        "cum",
        "penetrat",
        "masturbat",
        "orgasm",
        "sex toy",
        "threesome",
        "bondage",
        "dirty talk",
        "porn",
        "sext",
        "nude",
        "naked",
        "sex",
    )
    strong = explicit[:-3]
    forbidden = re.compile(
        r"\b(minor|underage|child|teen|incest|rape|molest|coerc|assault|abuse|"
        r"intoxicated|drunk|blackout|younger|mother|father|sister|brother|sibling|"
        r"animal|bestiality|boss|subordinate|teacher|student|choke|stranger|caught|"
        r"dangerous|life-threatening|feces|electricity|park|elevator|balcony|beach|"
        r"risky|revenge|witnessed|compression|pressure|heat|ice)\b|"
        r"without [^?]{0,40}(consent|permission|knowledge)|non-consens|unprotected sex|"
        r"public sex|in public|public place|household object|boundary [^?]{0,20}crossed|"
        r"incorporated air",
        re.IGNORECASE,
    )

    assert (
        sum(any(term in question.lower() for term in explicit) for question in questions)
        >= 175
    )
    assert (
        sum(any(term in question.lower() for term in strong) for question in questions)
        >= 75
    )
    assert not any(forbidden.search(question) for question in questions)


@pytest.mark.asyncio
async def test_truth_uses_fallback_without_provider():
    service = TruthService(QuestionGenerator(rng=random.Random(4)))

    question = await service.question(nsfw=False)

    assert question in load_truths(False)


def test_openai_is_preferred_when_both_keys_exist():
    provider = provider_from_env(
        {"OPENAI_API_KEY": "openai", "OPENROUTER_API_KEY": "openrouter"}
    )

    assert provider == Provider("openai", "openai", None, "gpt-5.6-luna")


def test_openrouter_is_selected_when_it_is_the_only_key():
    provider = provider_from_env({"OPENROUTER_API_KEY": "openrouter"})

    assert provider == Provider(
        "openrouter",
        "openrouter",
        "https://openrouter.ai/api/v1",
        "openai/gpt-4o-mini",
    )


@pytest.mark.asyncio
async def test_truth_asks_ai_for_an_international_adult_question():
    prompts = []

    async def complete(provider, system, prompt):
        prompts.append((provider, system, prompt))
        return '"What belief have you changed as an adult?"'

    provider = Provider("openai", "key", None, "model")
    service = TruthService(QuestionGenerator(provider, complete=complete))

    question = await service.question(nsfw=True)

    assert question == "What belief have you changed as an adult?"
    assert "30+" in prompts[0][1]
    assert "international" in prompts[0][1].lower()
    assert "truth or dare" in prompts[0][2].lower()
    assert "direct" in prompts[0][2].lower()
    assert "explicit" in prompts[0][2].lower()
    assert "raunchy" in prompts[0][2].lower()
    assert "consenting adults" in prompts[0][2].lower()


@pytest.mark.asyncio
async def test_truth_falls_back_when_ai_returns_an_incomplete_question():
    async def incomplete(*_args):
        return "What is"

    provider = Provider("openai", "key", None, "model")
    service = TruthService(
        QuestionGenerator(provider, complete=incomplete, rng=random.Random(2))
    )

    question = await service.question(nsfw=True)

    assert question in load_truths(True)


@pytest.mark.asyncio
async def test_truth_falls_back_when_ai_fails():
    async def fail(*_args):
        raise RuntimeError("offline")

    provider = Provider("openai", "key", None, "model")
    service = TruthService(
        QuestionGenerator(provider, complete=fail, rng=random.Random(2))
    )

    question = await service.question(nsfw=False)

    assert question in load_truths(False)
