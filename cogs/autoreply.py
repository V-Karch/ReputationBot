import json
import discord
from discord.ext import commands
from discord import app_commands

OWNER_ID = 923600698967461898


class Autoreply(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command(name = "customot", description = "Display CustomOT Tutorial", aliases=["cot"])
    async def custom_ot(self, context: commands.Context, user: discord.Member = None):
        embed = discord.Embed(
            title = "How To Make a Custom OT Pokemon",
            color=0x237feb,
            description="1. To customize the original trainer name or OT, the Pokemon needs to be in Pokemon Go. \n2. You must then change your Pokemon Home name on the mobile app to whatever OT you require. \n\nNote: It is recommended to restart Pokemon Go after this before transferring as Pokemon Home may be slow to register any changes."
        )

        await context.reply(content=user.mention if user else "", embed = embed)

async def setup(client: commands.Bot):
    await client.add_cog(Autoreply(client))
