# Frankly

![Frankly profile image](assets/profile.png)

A small Discord bot for candid conversations. It generates **Truth** and **Would You Rather** questions for an international audience aged 30+, with optional adult-only modes.

**Recommended bot name: Frankly.** It is short, friendly, and fits both honest answers and difficult choices. The included 1024×1024 profile image was generated with `openai/gpt-image-1-mini` through OpenRouter and is safe for Discord's circular crop.

## Features

- Global `/truth` and `/would_you_rather` slash commands
- Optional `nsfw` argument on both commands
- NSFW requests rejected unless the Discord channel is age-restricted
- OpenAI or OpenRouter question generation
- Automatic local fallback when no AI key is configured or generation fails
- 250 general and 250 NSFW fallback questions for each feature
- No privileged Discord intents
- Global commands support any number of guilds

## Discord setup

1. Create an application in the [Discord Developer Portal](https://discord.com/developers/applications).
2. Open **Bot**, create the bot, and copy its token.
3. If other servers should be able to install it, enable **Public Bot**.
4. Open **Installation** and enable **Guild Install**.
5. Add the `bot` and `applications.commands` scopes.
6. Grant **Send Messages** and **Use Application Commands** permissions.
7. Use the generated install link to add the bot to each guild.

Commands are registered globally. Discord can take up to an hour to show a new global command everywhere.

## Run locally

Python 3.11 or newer is required.

```bash
python3 -m venv .venv
.venv/bin/pip install -e .
cp .env.example .env
```

Set `DISCORD_BOT_TOKEN` in `.env`, then optionally set either AI provider key. Load the environment and start the bot:

```bash
set -a
. ./.env
set +a
.venv/bin/discord-question-bot
```

## Configuration

| Variable | Required | Default |
| --- | --- | --- |
| `DISCORD_BOT_TOKEN` | Yes | — |
| `OPENAI_API_KEY` | No | — |
| `OPENAI_MODEL` | No | `gpt-5.6-luna` |
| `OPENROUTER_API_KEY` | No | — |
| `OPENROUTER_MODEL` | No | `openai/gpt-4o-mini` |

OpenAI is selected when both keys are present. With neither key, questions are selected randomly from the bundled lists. AI errors also fall back locally so commands remain usable.

## Commands

```text
/truth [nsfw:false]
/would_you_rather [nsfw:false]
```

Set `nsfw:true` for adult-only questions. Discord must mark the current channel as age-restricted; otherwise the bot responds privately with an error.

## Development

```bash
.venv/bin/pip install -e '.[dev]'
.venv/bin/python -m pytest
.venv/bin/ruff check src tests scripts
```

Regenerate the checked-in fallback data after editing a source list:

```bash
.venv/bin/python scripts/generate_truths.py
.venv/bin/python scripts/generate_would_you_rathers.py
```

## License

[MIT](LICENSE) © 2026 Michael Standen
