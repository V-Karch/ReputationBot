import discord

RULES = [
    "1. Be nice to each other. It's fine to disagree, it's not fine to insult or attack other people.",
    "2. Remain mindful and polite when asking or answering questions.",
    "3. This is an English-speaking server, so please speak English to keep communication simple.",
    "4. Be careful in which channel you write.",
    "5. Don't spam. Don't post your question twice unless you fully believe you were not intentionally ignored.",
    "6. No scamming.",
    "7. Don't brigade, raid, or otherwise attack other people or communities. Don't discuss participation in these attacks.",
    '8. Not-safe-for-work content (including gore, and other "shock" content) is prohibited.\nAdditionally hornyposting is heavily discouraged in all the channels. This may warrant an immediate permanent ban. (includes usernames)',
    "9. No advertising. All forms of advertising, whether it's through direct messages or within the server, are subject to prohibition.",
    "10. We only allow trading hacked/genned pokemon if it is made aware to the person receiving the mon, that its hacked/genned. However using them in https://discord.com/channels/1047106748097503322/1060555566847627295 is strictly prohibited!",
    "11. No trading for money, accounts or other valuables outside of pokemon games. Offers for this will get a warning or banned.",
    "12. Using the @.giveaway ping outside of announcing the start of a giveaway in https://discord.com/channels/1047106748097503322/1060555566847627295 will result in a mute.\nExcessive use of it, outside of announcing new giveaways, will result in kick or ban.\nImportant: using hacked/genned mons are strictly prohibited!",
]


def make_rule_embed(rule_number: int) -> discord.Embed:
    message: str = "Invalid Rule Number!"

    if rule_number >= 1 and rule_number <= len(RULES) + 1:
        message = RULES[rule_number - 1]

    embed = discord.Embed(color=discord.Colour.red(), description=message)

    return embed
