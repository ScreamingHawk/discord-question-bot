import question_bot.bot as bot_module
from question_bot.bot import NSFW_ONLY, build_bot, channel_allows_nsfw
from question_bot.truth import load_truths
from question_bot.would_you_rather import load_would_you_rathers


class Channel:
    def __init__(self, nsfw):
        self.nsfw = nsfw

    def is_nsfw(self):
        return self.nsfw


class Response:
    def __init__(self):
        self.message = None
        self.ephemeral = False
        self.deferred = False

    async def send_message(self, message, *, ephemeral=False):
        self.message = message
        self.ephemeral = ephemeral

    async def defer(self):
        self.deferred = True


class Followup:
    def __init__(self):
        self.message = None
        self.embed = None
        self.view = None

    async def send(self, message=None, *, embed=None, view=None):
        self.message = message
        self.embed = embed
        self.view = view


class Avatar:
    url = "https://example.com/avatar.png"


class User:
    def __init__(self, name="Michael"):
        self.display_name = name
        self.display_avatar = Avatar()


class Interaction:
    def __init__(self, nsfw, name="Michael"):
        self.channel = Channel(nsfw)
        self.response = Response()
        self.followup = Followup()
        self.user = User(name)
        self.edited_embed = None
        self.edited_view = None

    async def edit_original_response(self, *, embed=None, view=None):
        self.edited_embed = embed
        self.edited_view = view


def test_nsfw_requires_an_nsfw_tagged_channel():
    assert channel_allows_nsfw(Channel(True))
    assert not channel_allows_nsfw(Channel(False))
    assert not channel_allows_nsfw(None)
    assert not channel_allows_nsfw(object())


def test_bot_registers_one_slash_command_per_feature():
    bot = build_bot({})

    commands = bot.tree.get_commands()

    assert {command.name for command in commands} == {"truth", "would_you_rather"}
    assert all(command._guild_ids is None for command in commands)


async def test_truth_rejects_nsfw_mode_outside_nsfw_channels():
    bot = build_bot({})
    interaction = Interaction(False)

    await bot.tree.get_command("truth").callback(interaction, True)

    assert interaction.response.message == NSFW_ONLY
    assert interaction.response.ephemeral
    assert interaction.followup.message is None


async def test_truth_sends_safe_fallback_question_as_attributed_embed():
    bot = build_bot({})
    interaction = Interaction(False)

    await bot.tree.get_command("truth").callback(interaction, False)

    embed = interaction.followup.embed
    assert interaction.response.deferred
    assert embed.description.removeprefix("## ") in load_truths(False)
    assert embed.author.name == "Requested by Michael"
    assert embed.author.icon_url == Avatar.url
    assert [button.label for button in interaction.followup.view.children] == ["Another!"]


async def test_nsfw_channel_shows_both_question_buttons():
    bot = build_bot({})
    interaction = Interaction(True)

    await bot.tree.get_command("truth").callback(interaction, False)

    view = interaction.followup.view
    assert view.timeout is None
    assert [button.label for button in view.children] == ["Another!", "Another NSFW"]
    assert {button.custom_id for button in view.children} == {
        "frankly:truth:another",
        "frankly:truth:another_nsfw",
    }


async def test_nsfw_button_replaces_question_and_attributes_clicker():
    bot = build_bot({})
    initial = Interaction(True)
    await bot.tree.get_command("truth").callback(initial, False)
    button = next(
        button for button in initial.followup.view.children if button.label == "Another NSFW"
    )
    click = Interaction(True, "Agathe")

    await button.callback(click)

    assert click.response.deferred
    assert click.edited_embed.description.removeprefix("## ") in load_truths(True)
    assert click.edited_embed.author.name == "Requested by Agathe"
    assert [button.label for button in click.edited_view.children] == [
        "Another!",
        "Another NSFW",
    ]


async def test_nsfw_button_rechecks_channel_before_generating():
    bot = build_bot({})
    initial = Interaction(True)
    await bot.tree.get_command("truth").callback(initial, False)
    button = next(
        button for button in initial.followup.view.children if button.label == "Another NSFW"
    )
    moved_interaction = Interaction(False)

    await button.callback(moved_interaction)

    assert moved_interaction.response.message == NSFW_ONLY
    assert moved_interaction.response.ephemeral
    assert moved_interaction.edited_embed is None


async def test_another_button_preserves_would_you_rather_game_type():
    bot = build_bot({})
    initial = Interaction(True)
    await bot.tree.get_command("would_you_rather").callback(initial, False)
    button = next(
        button for button in initial.followup.view.children if button.label == "Another!"
    )
    click = Interaction(True, "Agathe")

    await button.callback(click)

    question = click.edited_embed.description.removeprefix("## ")
    assert question in load_would_you_rathers(False)
    assert {button.custom_id for button in click.edited_view.children} == {
        "frankly:would_you_rather:another",
        "frankly:would_you_rather:another_nsfw",
    }


def test_main_keeps_discord_logging_enabled(monkeypatch):
    calls = []

    class Bot:
        def run(self, *args, **kwargs):
            calls.append((args, kwargs))

    monkeypatch.setenv("DISCORD_BOT_TOKEN", "token")
    monkeypatch.setattr(bot_module, "build_bot", Bot)

    bot_module.main()

    assert calls == [(('token',), {})]
