import random
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
    assert "consenting adults" in prompts[0][2].lower()
