from __future__ import annotations

import os
from collections.abc import Mapping

import discord
from discord import app_commands
from discord.ext import commands

from .generator import QuestionGenerator, provider_from_env
from .truth import TruthService
from .would_you_rather import WouldYouRatherService

NSFW_ONLY = "NSFW questions can only be used in an age-restricted channel."


def channel_allows_nsfw(channel: object | None) -> bool:
    checker = getattr(channel, "is_nsfw", None)
    return bool(checker()) if callable(checker) else False


def build_bot(env: Mapping[str, str] | None = None) -> commands.Bot:
    provider = provider_from_env(os.environ if env is None else env)
    generator = QuestionGenerator(provider)
    truth_service = TruthService(generator)
    wyr_service = WouldYouRatherService(generator)
    bot = commands.Bot(command_prefix=commands.when_mentioned, intents=discord.Intents.none())

    @bot.event
    async def setup_hook() -> None:
        await bot.tree.sync()

    async def send_question(interaction: discord.Interaction, nsfw: bool, service) -> None:
        if nsfw and not channel_allows_nsfw(interaction.channel):
            await interaction.response.send_message(NSFW_ONLY, ephemeral=True)
            return
        await interaction.response.defer()
        await interaction.followup.send(await service.question(nsfw))

    @bot.tree.command(name="truth", description="Get a random truth question")
    @app_commands.describe(nsfw="Allow adult-only questions (NSFW channels only)")
    async def truth(interaction: discord.Interaction, nsfw: bool = False) -> None:
        await send_question(interaction, nsfw, truth_service)

    @bot.tree.command(name="would_you_rather", description="Get a random Would You Rather question")
    @app_commands.describe(nsfw="Allow adult-only questions (NSFW channels only)")
    async def would_you_rather(interaction: discord.Interaction, nsfw: bool = False) -> None:
        await send_question(interaction, nsfw, wyr_service)

    return bot


def main() -> None:
    token = os.environ.get("DISCORD_BOT_TOKEN")
    if not token:
        raise RuntimeError("DISCORD_BOT_TOKEN is required")
    build_bot().run(token, log_handler=None)


if __name__ == "__main__":
    main()
