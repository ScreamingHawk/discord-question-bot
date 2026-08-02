import json
from importlib.resources import files

from .generator import QuestionGenerator


def load_would_you_rathers(nsfw: bool) -> list[str]:
    data = json.loads(files("question_bot.data").joinpath("would_you_rather.json").read_text())
    return data["nsfw" if nsfw else "safe"]


class WouldYouRatherService:
    def __init__(self, generator: QuestionGenerator) -> None:
        self.generator = generator

    async def question(self, nsfw: bool = False) -> str:
        kind = "party game Would You Rather with two distinct, balanced, difficult choices"
        return await self.generator.generate(kind, nsfw, load_would_you_rathers(nsfw))
