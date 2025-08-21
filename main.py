import os
import discord
from discord.ext import commands

OWNER_ID = 923600698967461898

with open("token.txt", "r") as f:
    TOKEN = f.read().strip()

intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix="~", intents=intents)


@client.command(name="sync")
async def _sync(context: commands.Context):
    if context.author.id == OWNER_ID:
        await client.tree.sync()
        await context.reply("Syncing...")
    else:
        await context.reply("This command is not for you...")


@client.event
async def setup_hook():
    for cog in os.listdir("cogs"):
        if not cog.endswith(".py"):
            continue

        await client.load_extension(f"cogs.{cog[:-3]}")
        print(f"Loaded cog `{cog}`")

    print(f"{client.user} is now running.")


client.run(TOKEN)
