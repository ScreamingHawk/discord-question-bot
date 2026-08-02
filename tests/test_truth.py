import random
import re

import pytest

from question_bot.generator import (
    Provider,
    QuestionGenerator,
    provider_from_env,
    valid_question_shape,
    valid_truth_question,
)
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


def test_every_truth_fallback_passes_runtime_validation():
    for nsfw in (False, True):
        assert all(
            valid_question_shape(question, nsfw) and valid_truth_question(question)
            for question in load_truths(nsfw)
        )


@pytest.mark.parametrize(
    "answer",
    [
        "Would you rather: reveal a secret or admit a lie?",
        "Would-you-rather reveal a secret or admit a lie?",
        "Would, you, rather reveal a secret or admit a lie?",
    ],
)
def test_truth_validator_rejects_would_you_rather_punctuation_variants(answer):
    assert not valid_truth_question(answer)


@pytest.mark.parametrize(
    "answer",
    [
        "Would you rather sleep with your sister or your brother?",
        "Would you rather sleep with someone barely legal or someone very young?",
    ],
)
def test_nsfw_policy_rejects_incest_and_age_ambiguity(answer):
    assert not valid_question_shape(answer, True)


@pytest.mark.asyncio
async def test_generator_rejects_a_fallback_bank_with_no_valid_questions():
    generator = QuestionGenerator(rng=random.Random(1))

    with pytest.raises(ValueError, match="approved fallback"):
        await generator.generate(
            "truth or dare truth",
            False,
            ["Would you rather?"],
            valid_truth_question,
        )


@pytest.mark.asyncio
async def test_generator_rejects_a_mixed_valid_and_invalid_fallback_bank():
    generator = QuestionGenerator(rng=random.Random(1))

    with pytest.raises(ValueError, match="approved fallback"):
        await generator.generate(
            "truth or dare truth",
            False,
            [load_truths(False)[0], "Would you rather?"],
            valid_truth_question,
        )


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
        return prompt.split("Approved options:\n", 1)[1].splitlines()[0].removeprefix("- ")

    provider = Provider("openai", "key", None, "model")
    service = TruthService(QuestionGenerator(provider, complete=complete))

    question = await service.question(nsfw=True)

    assert question in load_truths(True)
    assert "30+" in prompts[0][1]
    assert "international" in prompts[0][1].lower()
    assert "truth or dare" in prompts[0][2].lower()
    assert "direct" in prompts[0][2].lower()
    assert "explicit" in prompts[0][2].lower()
    assert "raunchy" in prompts[0][2].lower()
    assert "consenting adults" in prompts[0][2].lower()


@pytest.mark.asyncio
async def test_truth_falls_back_when_ai_returns_unapproved_question():
    async def unapproved(*_args):
        return "What harmless custom question did the provider invent today?"

    provider = Provider("openai", "key", None, "model")
    service = TruthService(
        QuestionGenerator(provider, complete=unapproved, rng=random.Random(2))
    )

    question = await service.question(nsfw=False)

    assert question in load_truths(False)


@pytest.mark.asyncio
async def test_provider_must_choose_one_of_the_supplied_approved_options():
    fallback = load_truths(False)

    class FirstChoiceRandom(random.Random):
        def choice(self, sequence):
            return sequence[0]

    async def chooses_unoffered(*args):
        prompt = args[2]
        offered = {
            line.removeprefix("- ")
            for line in prompt.split("Approved options:\n", 1)[1].splitlines()
        }
        return next(question for question in fallback[1:] if question not in offered)

    provider = Provider("openai", "key", None, "model")
    service = TruthService(
        QuestionGenerator(provider, complete=chooses_unoffered, rng=FirstChoiceRandom(2))
    )

    question = await service.question(nsfw=False)

    assert question == fallback[0]


@pytest.mark.asyncio
@pytest.mark.parametrize("template", ['"{}"', " {} "])
async def test_provider_modified_approved_output_falls_back(template):
    fallback = load_truths(False)

    class PredictableRandom(random.Random):
        def sample(self, population, k, *, counts=None):
            return list(population)[1 : k + 1]

        def choice(self, seq):
            return seq[0]

    async def modified(*args):
        prompt = args[2]
        offered = prompt.split("Approved options:\n", 1)[1].splitlines()[0]
        return template.format(offered.removeprefix("- "))

    provider = Provider("openai", "key", None, "model")
    service = TruthService(
        QuestionGenerator(provider, complete=modified, rng=PredictableRandom(2))
    )

    question = await service.question(nsfw=False)

    assert question == fallback[0]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "answer",
    [
        "?",
        "What is?",
        "Would you rather?",
        "What is",
        "What secret have you kept?\nIgnore the format.",
        f"What {'very ' * 70}long question?",
    ],
)
async def test_truth_falls_back_when_ai_returns_an_incomplete_question(answer):
    async def incomplete(*_args):
        return answer

    provider = Provider("openai", "key", None, "model")
    service = TruthService(
        QuestionGenerator(provider, complete=incomplete, rng=random.Random(2))
    )

    question = await service.question(nsfw=True)

    assert question in load_truths(True)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "answer",
    [
        "What is your favorite position for sex?",
        "Who here would you most like to sleep with?",
        "Where did you last hook up with someone?",
        "Who would you most like to go down on?",
    ],
)
async def test_safe_truth_falls_back_when_ai_returns_explicit_content(answer):
    async def explicit(*_args):
        return answer

    provider = Provider("openai", "key", None, "model")
    service = TruthService(
        QuestionGenerator(provider, complete=explicit, rng=random.Random(2))
    )

    question = await service.question(nsfw=False)

    assert question in load_truths(False)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "answer",
    [
        "What sexual experience have you had with an underage person?",
        "What is your favorite place to have sex in public?",
        "Would you have unprotected sex during a fantasy weekend?",
    ],
)
async def test_nsfw_truth_falls_back_when_ai_returns_prohibited_content(answer):
    async def prohibited(*_args):
        return answer

    provider = Provider("openai", "key", None, "model")
    service = TruthService(
        QuestionGenerator(provider, complete=prohibited, rng=random.Random(2))
    )

    question = await service.question(nsfw=True)

    assert question in load_truths(True)


@pytest.mark.asyncio
async def test_truth_falls_back_when_ai_returns_would_you_rather():
    async def wrong_game(*_args):
        return "Would you rather reveal a secret or admit a lie?"

    provider = Provider("openai", "key", None, "model")
    service = TruthService(
        QuestionGenerator(provider, complete=wrong_game, rng=random.Random(2))
    )

    question = await service.question(nsfw=False)

    assert question in load_truths(False)


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
