# Frankly

![Frankly profile image](assets/profile.png)

A small Discord bot for candid conversations. It serves **Truth** and **Would You Rather** questions designed with an adult audience in mind, with optional 18+ modes in age-restricted channels.

**Recommended bot name: Frankly.** It is short, friendly, and fits both honest answers and difficult choices. The included 1024×1024 profile image was generated with `openai/gpt-image-1-mini` through OpenRouter and is safe for Discord's circular crop.

## Features

- Global `/truth` and `/would_you_rather` slash commands
- Guild-only installation and command use; commands are unavailable in DMs and user-installed contexts
- Rich question embeds showing the requester's display name and avatar, colored blue for SFW and red for NSFW
- Persistent **Another!** buttons that post each new question as a new message without changing the original post
- **Another NSFW!** buttons included when a message is created in an age-restricted channel, with the current restriction rechecked on every click
- Optional `nsfw` argument on both commands
- NSFW responses restricted to channels that are currently age-restricted
- OpenAI or OpenRouter selection from operator-reviewed question options
- Automatic local random fallback when no AI key is configured, selection fails, or a provider returns anything outside the approved options
- 250 general and 250 NSFW fallback questions for each feature
- No privileged Discord intents
- Global commands work across every guild where the bot is installed

## Discord setup

1. Create an application in the [Discord Developer Portal](https://discord.com/developers/applications).
2. Open **Bot**, use **Reset Token** to generate a bot token, and copy it somewhere secure.
3. If other servers should be able to install it, enable **Public Bot**.
4. Open **Installation** and enable **Guild Install**.
5. Add the `bot` and `applications.commands` scopes.
6. Grant the bot **View Channels**, **Send Messages**, and **Embed Links** permissions. Members who invoke the slash commands must have **Use Application Commands** in the channel.
7. Use the generated install link to add the bot to each guild.

Commands are registered globally and are available in every guild where the bot is installed. Discord applies read-repair when a user invokes a stale global command after an update.

## Run locally

Python 3.11 or newer is required.

```bash
python3 -m venv .venv
.venv/bin/pip install -e .
cp .env.example .env
chmod 600 .env
```

Set `DISCORD_BOT_TOKEN` in `.env`, then optionally set either AI provider key. Load the environment and start the bot:

```bash
set -a
. ./.env
set +a
.venv/bin/discord-question-bot
```

## Run as a service

Complete the local installation first so `.venv` and `.env` exist. The included user service assumes the repository is at `~/discord-question-bot`:

```bash
mkdir -p ~/.config/systemd/user
cp deploy/frankly.service ~/.config/systemd/user/
systemd-analyze --user verify ~/.config/systemd/user/frankly.service
systemctl --user daemon-reload
systemctl --user enable --now frankly.service
```

Check health and follow logs:

```bash
systemctl --user status frankly.service
journalctl --user -u frankly.service -f
```

For startup before login, check whether user lingering is enabled:

```bash
loginctl show-user "$USER" -p Linger
```

If it reports `Linger=no`, enable it once with `sudo loginctl enable-linger "$USER"`.

## Configuration

| Variable | Required | Default |
| --- | --- | --- |
| `DISCORD_BOT_TOKEN` | Yes | — |
| `OPENAI_API_KEY` | No | — |
| `OPENAI_MODEL` | No | `gpt-5.6-luna` |
| `OPENROUTER_API_KEY` | No | — |
| `OPENROUTER_MODEL` | No | `openai/gpt-4o-mini` |

OpenAI takes priority when both keys are present. For each request, a configured provider is shown 12 randomly sampled, operator-reviewed questions and must choose one verbatim. Provider-created or modified text is rejected. With neither key—or if provider selection fails—the bot selects randomly from the same bundled lists. This keeps normal and NSFW channel boundaries enforceable without trusting generated text.

## Commands

| Command | Optional argument |
| --- | --- |
| `/truth` | `nsfw` boolean, default `false` |
| `/would_you_rather` | `nsfw` boolean, default `false` |

Set `nsfw` to `true` for adult-only questions. Discord must mark the current channel as age-restricted; otherwise the bot responds privately with an error. SFW posts show only **Another!** outside age-restricted channels; posts in age-restricted channels show both buttons.

## Development

```bash
.venv/bin/pip install -e '.[dev]'
.venv/bin/python -m pytest
.venv/bin/ruff check src tests
```

## Legal

The hosted Frankly bot is operated by **Ao Collaboration Ltd**. Its use is governed by:

- [Privacy Policy](PRIVACY.md)
- [Terms of Service](TERMS.md)

## License

[MIT](LICENSE) © 2026 Michael Standen
