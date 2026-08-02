import random

import pytest

from question_bot.generator import Provider, QuestionGenerator
from question_bot.would_you_rather import WouldYouRatherService, load_would_you_rathers


def test_would_you_rather_fallback_lists_are_large_and_unique():
    for nsfw in (False, True):
        questions = load_would_you_rathers(nsfw)
        assert len(questions) >= 250
        assert len(questions) == len(set(questions))
        assert all(question.startswith("Would you rather ") for question in questions)
        assert all(question.endswith("?") for question in questions)


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
    assert "two distinct choices" in prompts[0][2].lower()
    assert "consenting adults" in prompts[0][2].lower()
