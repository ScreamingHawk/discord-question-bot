import random

import pytest

from question_bot.generator import Provider, QuestionGenerator, provider_from_env
from question_bot.truth import TruthService, load_truths


def test_truth_fallback_lists_are_large_and_unique():
    for nsfw in (False, True):
        questions = load_truths(nsfw)
        assert len(questions) >= 250
        assert len(questions) == len(set(questions))
        assert all(question.endswith("?") for question in questions)


@pytest.mark.asyncio
async def test_truth_uses_fallback_without_provider():
    service = TruthService(QuestionGenerator(rng=random.Random(4)))

    question = await service.question(nsfw=False)

    assert question in load_truths(False)


def test_openai_is_preferred_when_both_keys_exist():
    provider = provider_from_env(
        {"OPENAI_API_KEY": "openai", "OPENROUTER_API_KEY": "openrouter"}
    )

    assert provider == Provider("openai", "openai", None, "gpt-4o-mini")


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
    assert "consenting adults" in prompts[0][2].lower()


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
