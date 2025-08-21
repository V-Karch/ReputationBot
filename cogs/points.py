import discord
from discord.ext import commands
from discord import app_commands


class Points(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(name="hi", description="Check the bot status")
    async def hello_test_command(self, interaction: discord.Interaction):
        await interaction.response.send_message("Hello!")


async def setup(client: commands.Bot):
    await client.add_cog(Points(client))
