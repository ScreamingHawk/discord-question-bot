import json
from importlib.resources import files

from .generator import QuestionGenerator


def load_truths(nsfw: bool) -> list[str]:
    data = json.loads(files("question_bot.data").joinpath("truth.json").read_text())
    return data["nsfw" if nsfw else "safe"]


class TruthService:
    def __init__(self, generator: QuestionGenerator) -> None:
        self.generator = generator

    async def question(self, nsfw: bool = False) -> str:
        kind = (
            "explicit, raunchy classic Truth or Dare truth using direct adult sexual language"
            if nsfw
            else "classic Truth or Dare truth that is direct, revealing, and easy to answer aloud"
        )
        return await self.generator.generate(kind, nsfw, load_truths(nsfw))
