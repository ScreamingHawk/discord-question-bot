# Frankly Privacy Policy

**Effective date: 4 August 2026 (New Zealand time)**

Frankly is a Discord party-question bot operated by **Michael Standen** in New Zealand. This policy explains what information Frankly handles when you use its slash commands or buttons.

## 1. Scope

This policy applies to the hosted Frankly Discord bot. Frankly is configured for guild installation, and its commands are limited to channels in Discord servers. Discord, server administrators, OpenAI, OpenRouter, and any downstream model provider operate under their own terms and privacy policies.

## 2. Information Frankly handles

When you invoke a Frankly slash command or click one of its buttons, Discord sends the bot an interaction payload. Depending on the interaction, that payload can contain technical and account metadata supplied by Discord, including:

- your Discord user ID, display name, and avatar URL;
- the server and channel identifiers;
- the command or button used and whether SFW or NSFW mode was requested; and
- whether Discord reports the current channel as age-restricted.

It can also contain an interaction ID and short-lived response token, locale, permissions, application permissions, authorising-install information, and other Discord context needed to process the request. A button interaction includes an in-memory copy of the Frankly message containing that button. This is the bot's own triggering message, not unrelated user messages or general channel history.

Frankly uses only what it needs to answer the interaction. It uses the command or button and mode to select a question, checks the channel's age-restricted status for NSFW requests, and places the requester's current display name and avatar in the resulting embed.

Using Frankly is optional. If you do not invoke a Frankly command or click its buttons, Frankly does not receive an interaction from that action. If Discord does not provide the interaction metadata needed to identify the request, channel, and requested mode, Frankly cannot provide a response.

The resulting post is visible to people who can access that Discord channel. Its attribution is a snapshot of the requester's display name and avatar URL at request time and may remain after later profile changes or account deletion. Discord and the relevant server administrators control that message's storage, rendering, moderation, and deletion.

## 3. Information Frankly does not retain or intentionally request

The Discord metadata described above is processed transiently, but Frankly does not place interaction history or user profiles in an operator-controlled persistent store. Frankly does not intentionally request or retain:

- message content or message history;
- direct messages unrelated to a Frankly interaction;
- IP addresses or device identifiers from Discord users;
- email addresses, phone numbers, payment information, or Discord credentials;
- advertising identifiers, cookies, analytics, or tracking profiles; or
- a database or file of command usage, interaction payloads, user IDs, guild IDs, channel IDs, names, or avatars.

Frankly does not sell personal information or use it for advertising or profiling.

## 4. Permissions and Discord access

Frankly's default installation requests only the Discord OAuth scopes `bot` and `applications.commands`, with **View Channels**, **Send Messages**, and **Embed Links** as the bot permissions.

The bot runs with `discord.Intents.none()` and does not request privileged gateway intents, including Message Content. Its default installation does not request **Read Message History**, **Manage Messages**, **Manage Channels**, or **Administrator**. These limits allow Frankly to receive interactions and post question embeds without monitoring conversations or retrieving channel history.

A bot can also inherit permissions from a server's `@everyone` role, and a server administrator can change its role or channel permissions after installation. Frankly may therefore have an effective permission that its default installation did not request. The current software contains no code that retrieves or stores message history even if **Read Message History** is inherited or granted. Administrators who want the narrowest effective boundary should explicitly deny that permission for Frankly where necessary.

## 5. Storage and retention

Frankly has no application database or interaction-history store and does not write interaction or user data to local files. Individual interaction objects are discarded after handling. The Discord client keeps minimal connection and cache state in memory, including gateway state and identifiers for guilds where the bot is installed, until disconnection or process restart.

Frankly is self-hosted on operator-managed infrastructure; no separate analytics or hosted logging service receives its service logs. Routine logs contain operational events such as startup, shutdown, Discord gateway connectivity, and technical errors. The application does not deliberately log interaction payloads or usage, but dependency-generated diagnostics may include gateway session IDs, request metadata, command names, or other Discord technical identifiers when an error occurs.

Service logs have no fixed retention period. They are kept only for security and troubleshooting and are automatically removed as the size-limited system journal rotates according to available storage and host configuration. Any incidentally logged personal information is deleted or anonymised when it is no longer needed for those purposes.

Messages posted by Frankly are stored by Discord under Discord's retention practices and the relevant server's moderation policies. To remove a Frankly post, contact a moderator of the Discord server or use Discord's available message-management tools.

## 6. Optional AI provider processing

Frankly's operator may configure either OpenAI or OpenRouter. When configured, the provider receives:

- the game type (Truth or Would You Rather);
- whether SFW or NSFW mode was requested;
- selection instructions; and
- 12 randomly sampled, operator-reviewed question options.

The provider is asked to return one option verbatim. Frankly does **not** send the provider Discord user IDs, display names, avatars, Discord user message content, server IDs, channel IDs, or interaction payloads. Provider-created or modified questions are rejected. If provider selection fails, Frankly selects locally from the operator-reviewed question bank.

OpenAI or OpenRouter may process and retain the API request and associated operator-side technical metadata under their own settings and privacy terms. When OpenRouter is used, it routes the request to the selected downstream model provider, which may also process and retain the prompt under its own settings and policies. Neither Frankly's prompt nor its approved options contain information identifying the Discord user.

## 7. Disclosure

Frankly does not sell or rent information. Information may be disclosed only:

- through the Discord post requested by the user, as described above;
- to infrastructure or platform providers as technically necessary to operate the service;
- where required by New Zealand law or a valid legal process; or
- where reasonably necessary to protect users, the service, or others from fraud, abuse, or security threats.

Because the bot does not maintain a user-data store, it ordinarily has no retained user record to disclose.

## 8. International processing

Discord processes interaction data and bot messages and may do so outside New Zealand under its own privacy terms. Frankly does not send personal information identifying the Discord user to an optional AI provider; only the non-identifying selection request described in section 6 is sent. The operator does not represent that a third party's privacy policy alone provides any particular New Zealand international-transfer safeguard.

## 9. Age and adult content

General use is limited to people who meet Discord's minimum age requirement in their country and any higher age required by local law. A parent or guardian's permission is also required where applicable law requires it.

NSFW features are only available when Discord reports the current channel as age-restricted. Frankly hides the NSFW button outside those channels and rechecks the channel before every NSFW response. Frankly relies on Discord's access controls and does not independently verify a user's age. NSFW features are intended only for users who are at least 18 and legally permitted to access adult content.

## 10. Your rights

Depending on applicable law, including the New Zealand Privacy Act 2020, you may have rights to ask whether personal information is held and to request access or correction. Frankly does not maintain a user-data database, but you may contact the operator with a privacy question or request.

For information contained in Discord messages or held by Discord, you may also need to contact the relevant server administrator or Discord directly.

If you are not satisfied with the response to a privacy concern, you may contact the [New Zealand Office of the Privacy Commissioner](https://www.privacy.org.nz/).

## 11. Security

Reasonable technical and organisational safeguards are used to limit Frankly's access and avoid unnecessary collection. No online service can guarantee absolute security.

## 12. Changes

This policy may be updated if Frankly's operation or legal obligations change. Material changes will be published in this repository with a revised effective date and, where practical, announced through Frankly's public service or application information. Material new uses of personal information will apply prospectively or with any additional notice or authority required by law.

## 13. Contact

Michael Standen is Frankly's privacy contact. For privacy questions or requests, contact:

**Michael Standen**  
Email: [michael@aocollab.tech](mailto:michael@aocollab.tech)
