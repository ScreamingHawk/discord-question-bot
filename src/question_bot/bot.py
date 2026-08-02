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


def question_embed(question: str, user: object, nsfw: bool) -> discord.Embed:
    color = discord.Color.red() if nsfw else discord.Color.blue()
    embed = discord.Embed(description=f"## {question}", color=color)
    name = getattr(user, "display_name", str(user))
    avatar = getattr(getattr(user, "display_avatar", None), "url", None)
    author = {"name": f"Requested by {name}"}
    if avatar:
        author["icon_url"] = str(avatar)
    embed.set_author(**author)
    return embed


class QuestionButton(discord.ui.Button):
    def __init__(self, feature: str, nsfw: bool) -> None:
        super().__init__(
            label="Another NSFW!" if nsfw else "Another!",
            style=discord.ButtonStyle.danger if nsfw else discord.ButtonStyle.primary,
            custom_id=f"frankly:{feature}:another{'_nsfw' if nsfw else ''}",
        )
        self.nsfw = nsfw

    async def callback(self, interaction: discord.Interaction) -> None:
        view = self.view
        if isinstance(view, QuestionView):
            await view.post_question(interaction, self.nsfw)


class QuestionView(discord.ui.View):
    def __init__(self, feature: str, service, show_nsfw: bool) -> None:
        super().__init__(timeout=None)
        self.feature = feature
        self.service = service
        self.add_item(QuestionButton(feature, False))
        if show_nsfw:
            self.add_item(QuestionButton(feature, True))

    async def post_question(self, interaction: discord.Interaction, nsfw: bool) -> None:
        if nsfw and not channel_allows_nsfw(interaction.channel):
            await interaction.response.send_message(NSFW_ONLY, ephemeral=True)
            return
        await interaction.response.defer()
        question = await self.service.question(nsfw)
        view = QuestionView(
            self.feature,
            self.service,
            channel_allows_nsfw(interaction.channel),
        )
        await interaction.followup.send(
            embed=question_embed(question, interaction.user, nsfw),
            view=view,
        )


def build_bot(env: Mapping[str, str] | None = None) -> commands.Bot:
    provider = provider_from_env(os.environ if env is None else env)
    generator = QuestionGenerator(provider)
    truth_service = TruthService(generator)
    wyr_service = WouldYouRatherService(generator)
    bot = commands.Bot(command_prefix=commands.when_mentioned, intents=discord.Intents.none())

    @bot.event
    async def setup_hook() -> None:
        bot.add_view(QuestionView("truth", truth_service, True))
        bot.add_view(QuestionView("would_you_rather", wyr_service, True))
        await bot.tree.sync()

    async def send_question(
        interaction: discord.Interaction,
        feature: str,
        nsfw: bool,
        service,
    ) -> None:
        if nsfw and not channel_allows_nsfw(interaction.channel):
            await interaction.response.send_message(NSFW_ONLY, ephemeral=True)
            return
        await interaction.response.defer()
        question = await service.question(nsfw)
        view = QuestionView(feature, service, channel_allows_nsfw(interaction.channel))
        await interaction.followup.send(
            embed=question_embed(question, interaction.user, nsfw),
            view=view,
        )

    @bot.tree.command(name="truth", description="Get a random truth question")
    @app_commands.describe(nsfw="Allow adult-only questions (NSFW channels only)")
    async def truth(interaction: discord.Interaction, nsfw: bool = False) -> None:
        await send_question(interaction, "truth", nsfw, truth_service)

    @bot.tree.command(name="would_you_rather", description="Get a random Would You Rather question")
    @app_commands.describe(nsfw="Allow adult-only questions (NSFW channels only)")
    async def would_you_rather(interaction: discord.Interaction, nsfw: bool = False) -> None:
        await send_question(interaction, "would_you_rather", nsfw, wyr_service)

    return bot


def main() -> None:
    token = os.environ.get("DISCORD_BOT_TOKEN")
    if not token:
        raise RuntimeError("DISCORD_BOT_TOKEN is required")
    build_bot().run(token)


if __name__ == "__main__":
    main()
