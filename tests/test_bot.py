from question_bot.bot import NSFW_ONLY, build_bot, channel_allows_nsfw
from question_bot.truth import load_truths


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

    async def send(self, message):
        self.message = message


class Interaction:
    def __init__(self, nsfw):
        self.channel = Channel(nsfw)
        self.response = Response()
        self.followup = Followup()


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


async def test_truth_sends_safe_fallback_question():
    bot = build_bot({})
    interaction = Interaction(False)

    await bot.tree.get_command("truth").callback(interaction, False)

    assert interaction.response.deferred
    assert interaction.followup.message in load_truths(False)
