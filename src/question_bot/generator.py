from __future__ import annotations

import logging
import os
import random
from collections.abc import Awaitable, Callable, Mapping, Sequence
from dataclasses import dataclass

from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


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

    async def generate(self, kind: str, nsfw: bool, fallback: Sequence[str]) -> str:
        if self.provider:
            system = (
                "Generate one engaging question for an international audience aged 30+. "
                "Avoid culture-specific assumptions, stereotypes, and references requiring local knowledge. "
                "Return only the question."
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
            try:
                answer = await self.complete(
                    self.provider, system, f"Create a random {kind} question. {mode}"
                )
                answer = answer.strip().strip('"').strip("'")
                if answer.endswith("?") and "\n" not in answer and len(answer) <= 1000:
                    return answer
            except Exception as error:  # noqa: BLE001
                logger.debug("AI generation failed: %s", error)
        return self.rng.choice(fallback)
