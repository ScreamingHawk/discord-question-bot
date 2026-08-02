import random
import re
from collections import Counter

import pytest

from question_bot.generator import Provider, QuestionGenerator
from question_bot.would_you_rather import WouldYouRatherService, load_would_you_rathers


def test_would_you_rather_fallback_lists_are_large_unique_and_varied():
    for nsfw in (False, True):
        questions = load_would_you_rathers(nsfw)
        choices = [
            question.removeprefix("Would you rather ").removesuffix("?").split(", or ")
            for question in questions
        ]
        left_counts = Counter(choice[0] for choice in choices)
        right_counts = Counter(choice[1] for choice in choices)

        assert len(questions) >= 250
        assert len(questions) == len(set(questions))
        assert all(len(choice) == 2 for choice in choices)
        assert max(left_counts.values()) <= 3
        assert max(right_counts.values()) <= 3
        assert all(question.startswith("Would you rather ") for question in questions)
        assert all(question.endswith("?") for question in questions)
        assert all(len(question) <= 180 for question in questions)


def test_would_you_rather_lists_cover_classic_party_topics():
    safe = " ".join(load_would_you_rathers(False)).lower()
    nsfw = " ".join(load_would_you_rathers(True)).lower()

    for topic in ("money", "travel", "career", "friend", "embarrass", "phone"):
        assert topic in safe
    for topic in ("sex", "kiss", "naked", "fantasy", "orgasm", "sext"):
        assert topic in nsfw


def test_would_you_rather_nsfw_list_is_explicit_but_excludes_abuse():
    questions = load_would_you_rathers(True)
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
    prefixes = Counter(
        " ".join(
            question.removeprefix("Would you rather ").lower().split()[:5]
        )
        for question in questions
    )

    assert (
        sum(any(term in question.lower() for term in explicit) for question in questions)
        >= 175
    )
    assert (
        sum(any(term in question.lower() for term in strong) for question in questions)
        >= 75
    )
    assert max(prefixes.values()) <= 8
    assert not any(forbidden.search(question) for question in questions)


@pytest.mark.asyncio
async def test_would_you_rather_uses_fallback_without_provider():
    service = WouldYouRatherService(QuestionGenerator(rng=random.Random(8)))

    question = await service.question(nsfw=False)

    assert question in load_would_you_rathers(False)


@pytest.mark.asyncio
async def test_would_you_rather_asks_ai_for_two_adult_options():
    prompts = []

    async def complete(provider, system, prompt):
        prompts.append((provider, system, prompt))
        return "Would you rather kiss slowly or be kissed passionately?"

    provider = Provider("openrouter", "key", "https://openrouter.ai/api/v1", "model")
    service = WouldYouRatherService(QuestionGenerator(provider, complete=complete))

    question = await service.question(nsfw=True)

    assert question.startswith("Would you rather ")
    assert "party game" in prompts[0][2].lower()
    assert "two distinct" in prompts[0][2].lower()
    assert "balanced" in prompts[0][2].lower()
    assert "difficult" in prompts[0][2].lower()
    assert "explicit" in prompts[0][2].lower()
    assert "raunchy" in prompts[0][2].lower()
    assert "consenting adults" in prompts[0][2].lower()
