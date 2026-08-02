from __future__ import annotations

import logging
import os
import random
import re
from collections.abc import Awaitable, Callable, Mapping, Sequence
from dataclasses import dataclass

from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

SAFE_MODE_SEXUAL = re.compile(
    r"\b(?:sex(?:ual|ually|iest|y)?|fuck(?:ed|ing)?|blowjob|oral sex|anal sex|"
    r"orgasm|masturbat\w*|nude|naked|porn|sext\w*|penis|vagina|cock|dick|cum|"
    r"threesome|bondage|kink\w*|fetish\w*|horny|erotic\w*|genitals?|intercourse|"
    r"foreplay|penetrat\w*|arous\w*|lingerie|dildo|vibrator|handjob|rimjob|"
    r"finger(?:ed|ing)|spank\w*|striptease|one-night stand|hook(?:ed|ing)? up|"
    r"hookups?|(?:sleep|sleeping|slept) with|make love|(?:get|getting|got) laid|"
    r"(?:go|going|went) down on|turn(?:ed|ing|s)? (?:you |me |them )?on)\b",
    re.IGNORECASE,
)
NSFW_UNSAFE = re.compile(
    r"\b(?:minor|underage|child|teen|boy|girl|guy|young(?:er)?|barely legal|"
    r"mother|father|sister|brother|sibling|relative|cousin|aunt|uncle|incest|"
    r"rape|molest\w*|"
    r"coerc\w*|assault|intoxicated|drunk|blackout|unconscious|asleep|bestiality|"
    r"animal|chok\w*|stranger|teacher|student|boss|employee|subordinate|"
    r"unprotected|bareback|scat|feces|watersports?|risky|dangerous)\b|"
    r"without [^?]{0,40}(?:consent|permission|knowledge)|non-consens|"
    r"(?:public sex|sex in public|in a public place|go bare|go dry|without lube|"
    r"household object|power tools?|wrong person)",
    re.IGNORECASE,
)
WORD = re.compile(r"[\w'-]+")


def valid_question_shape(answer: str, nsfw: bool) -> bool:
    if not 15 <= len(answer) <= 300 or "\n" in answer or answer.count("?") != 1:
        return False
    if not answer.endswith("?") or len(WORD.findall(answer)) < 5:
        return False
    if nsfw:
        return NSFW_UNSAFE.search(answer) is None
    return SAFE_MODE_SEXUAL.search(answer) is None


def valid_truth_question(answer: str) -> bool:
    return re.match(r"^would[\W_]+you[\W_]+rather\b", answer, re.IGNORECASE) is None


def valid_would_you_rather_question(answer: str) -> bool:
    prefix = "would you rather "
    if not answer.casefold().startswith(prefix):
        return False
    body = answer[len(prefix) : -1]
    choices = re.split(r",?\s+or\s+", body, maxsplit=1, flags=re.IGNORECASE)
    normalized = [WORD.findall(choice.casefold()) for choice in choices]
    trivial = {"yes", "no", "maybe", "either", "neither", "this", "that"}
    return (
        len(normalized) == 2
        and all(normalized)
        and normalized[0] != normalized[1]
        and not any(len(choice) == 1 and choice[0] in trivial for choice in normalized)
    )


@dataclass(frozen=True)
class Provider:
    name: str
    api_key: str
    base_url: str | None
    model: str


def provider_from_env(env: Mapping[str, str] = os.environ) -> Provider | None:
    if key := env.get("OPENAI_API_KEY"):
        return Provider("openai", key, None, env.get("OPENAI_MODEL", "gpt-5.6-luna"))
    if key := env.get("OPENROUTER_API_KEY"):
        return Provider(
            "openrouter",
            key,
            "https://openrouter.ai/api/v1",
            env.get("OPENROUTER_MODEL", "openai/gpt-4o-mini"),
        )
    return None


async def _complete(provider: Provider, system: str, prompt: str) -> str:
    client = AsyncOpenAI(api_key=provider.api_key, base_url=provider.base_url)
    response = await client.chat.completions.create(
        model=provider.model,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": prompt}],
        temperature=1.2,
        max_tokens=400,
    )
    return response.choices[0].message.content or ""


class QuestionGenerator:
    def __init__(
        self,
        provider: Provider | None = None,
        *,
        complete: Callable[[Provider, str, str], Awaitable[str]] = _complete,
        rng: random.Random | None = None,
    ) -> None:
        self.provider = provider
        self.complete = complete
        self.rng = rng or random.Random()

    async def generate(
        self,
        kind: str,
        nsfw: bool,
        fallback: Sequence[str],
        validator: Callable[[str], bool],
    ) -> str:
        approved = [
            question
            for question in fallback
            if valid_question_shape(question, nsfw) and validator(question)
        ]
        if len(approved) != len(fallback) or not approved:
            raise ValueError("Question bank contains a question outside the approved fallback policy")

        if self.provider:
            system = (
                "Choose exactly one question from the approved options supplied by the user for an "
                "international audience aged 30+. Return that question verbatim and nothing else."
            )
            mode = (
                "Use direct, unambiguous adult sexual vocabulary rather than mild euphemisms. "
                "Keep it to one short party-game question, not erotic narrative. It must involve "
                "only consenting adults and must not include minors, age ambiguity, incest, "
                "coercion, exploitation, sexual violence, intoxicated consent, public exposure, "
                "or unsafe sexual acts."
                if nsfw
                else "Keep the question suitable for a general adult channel and non-sexual."
            )
            options = self.rng.sample(approved, min(12, len(approved)))
            option_text = "\n".join(f"- {question}" for question in options)
            try:
                answer = await self.complete(
                    self.provider,
                    system,
                    f"Select one {kind} question verbatim. {mode}\nApproved options:\n{option_text}",
                )
                if answer in options:
                    return answer
            except Exception as error:  # noqa: BLE001
                logger.debug("Provider question selection failed: %s", error)
        return self.rng.choice(approved)
