# Frankly Privacy Policy

**Effective date: 4 August 2026**

Frankly is a Discord party-question bot operated by **Michael Standen** in New Zealand. This policy explains what information Frankly handles when you use its slash commands or buttons.

## 1. Scope

This policy applies to the hosted Frankly Discord bot. Discord, server administrators, OpenAI, and OpenRouter operate under their own terms and privacy policies.

## 2. Information Frankly handles

When you invoke a Frankly slash command or click one of its buttons, Discord sends the bot an interaction payload. That payload can contain technical and account metadata supplied by Discord, such as:

- your Discord user ID, display name, and avatar URL;
- the server and channel identifiers;
- the command or button used and whether SFW or NSFW mode was requested; and
- whether Discord reports the current channel as age-restricted.

Frankly uses only what it needs to answer the interaction. It uses the command or button and mode to select a question, checks the channel's age-restricted status for NSFW requests, and places the requester's current display name and avatar in the resulting embed.

Using Frankly is optional. If you do not invoke a Frankly command or click its buttons, Frankly does not receive an interaction from that action. If Discord does not provide the interaction metadata needed to identify the request, channel, and requested mode, Frankly cannot provide a response.

The resulting post is visible to people who can access that Discord channel. It remains a Discord message and may continue to display the requester's name and avatar attribution until it is deleted or changed by Discord. Discord and the relevant server administrators control that message's storage, moderation, and deletion.

## 3. Information Frankly does not collect

Frankly does not intentionally collect or maintain:

- message content or message history;
- direct messages unrelated to a Frankly interaction;
- IP addresses or device identifiers from Discord users;
- email addresses, phone numbers, payment information, or Discord credentials;
- advertising identifiers, cookies, analytics, or tracking profiles; or
- a database or file of command usage, user IDs, guild IDs, channel IDs, names, or avatars.

Frankly does not sell personal information or use it for advertising or profiling.

## 4. Permissions and Discord access

Frankly is designed to use only the Discord OAuth scopes `bot` and `applications.commands`, with the bot permissions **View Channels**, **Send Messages**, and **Embed Links**.

The bot runs with `discord.Intents.none()` and does not request privileged gateway intents, including Message Content. It does not request **Read Message History**, **Manage Messages**, **Manage Channels**, or **Administrator**. These limits allow Frankly to receive interactions and post question embeds without monitoring conversations or retrieving channel history.

A Discord server administrator can change a bot role's permissions after installation, but the current Frankly software does not contain code that reads or stores message history even if broader permissions are granted.

## 5. Storage and retention

Frankly has no application database and does not write interaction or user data to local files. Interaction metadata is handled in memory only for the time needed to generate and send a response.

The host keeps routine system service logs, which are rotated according to the host's system journal settings. Frankly's normal logs contain operational events such as startup, shutdown, Discord gateway connectivity, and technical errors. Frankly does not intentionally log command content or user/profile identifiers.

Messages posted by Frankly are stored by Discord under Discord's retention practices and the relevant server's moderation policies. To remove a Frankly post, contact a moderator of the Discord server or use Discord's available message-management tools.

## 6. Optional AI provider processing

Frankly's operator may configure either OpenAI or OpenRouter. When configured, the provider receives:

- the game type (Truth or Would You Rather);
- whether SFW or NSFW mode was requested;
- selection instructions; and
- 12 randomly sampled, audited question options.

The provider is asked to return one option verbatim. Frankly does **not** send the provider Discord user IDs, display names, avatars, Discord user message content, server IDs, channel IDs, or interaction payloads. Provider-created or modified questions are rejected. If provider selection fails, Frankly selects locally from the audited question bank.

OpenAI or OpenRouter may process the API request and associated operator-side technical metadata under their own privacy terms. When OpenRouter is used, it routes the selection request to the model provider chosen in Frankly's configuration. Neither Frankly's prompt nor its approved options contain information identifying the Discord user.

## 7. Disclosure

Frankly does not sell or rent information. Information may be disclosed only:

- through the Discord post requested by the user, as described above;
- to infrastructure or platform providers as technically necessary to operate the service;
- where required by New Zealand law or a valid legal process; or
- where reasonably necessary to protect users, the service, or others from fraud, abuse, or security threats.

Because the bot does not maintain a user-data store, it ordinarily has no retained user record to disclose.

## 8. International processing

Discord and optional AI providers may process data outside New Zealand. Their handling is governed by their own privacy policies and applicable contractual or legal protections.

## 9. Age and adult content

General use is limited to people who meet Discord's minimum age requirement in their country and any higher age required by local law.

NSFW features are only available when Discord reports the current channel as age-restricted. Frankly hides the NSFW button outside those channels and rechecks the channel before every NSFW response. Frankly relies on Discord's access controls and does not independently verify a user's age. NSFW features are intended only for users who are at least 18 and legally permitted to access adult content.

## 10. Your rights

Depending on applicable law, including the New Zealand Privacy Act 2020, you may have rights to ask whether personal information is held and to request access or correction. Frankly does not maintain a user-data database, but you may contact the operator with a privacy question or request.

For information contained in Discord messages or held by Discord, you may also need to contact the relevant server administrator or Discord directly.

If you are not satisfied with the response to a privacy concern, you may contact the [New Zealand Office of the Privacy Commissioner](https://www.privacy.org.nz/).

## 11. Security

Reasonable technical and organisational safeguards are used to limit Frankly's access and avoid unnecessary collection. No online service can guarantee absolute security.

## 12. Changes

This policy may be updated if Frankly's operation or legal obligations change. Material changes will be published in this repository with a revised effective date.

## 13. Contact

Michael Standen is Frankly's privacy contact. For privacy questions or requests, contact:

**Michael Standen**  
Email: [michael@aocollab.tech](mailto:michael@aocollab.tech)
