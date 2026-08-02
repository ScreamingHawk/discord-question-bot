from question_bot.bot import build_bot, channel_allows_nsfw


class Channel:
    def __init__(self, nsfw):
        self.nsfw = nsfw

    def is_nsfw(self):
        return self.nsfw


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
