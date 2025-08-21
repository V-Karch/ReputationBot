import discord
from db import DB
from discord.ext import commands
from discord import app_commands

OWNER_ID = 923600698967461898


def setup_points_db():
    sql = """
        CREATE TABLE IF NOT EXISTS reputation (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target_user_id INTEGER,
            author_user_id INTEGER,
            point_value INTEGER, -- inferred
            reason TEXT
        )
    """

    db = DB("points.db")
    db.exec_sql(sql)


class Points(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(name="hi", description="Check the bot status")
    async def hello_test_command(self, interaction: discord.Interaction):
        await interaction.response.send_message("Hello!")

    @app_commands.command(
        name="setup", description="Initial setup, this command is not for you"
    )
    async def initial_setup(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        if interaction.user.id != OWNER_ID:
            await interaction.followup.send("This command is not for you.")
            return

        setup_points_db()

        await interaction.followup.send("Attempted initial table setup")


async def setup(client: commands.Bot):
    await client.add_cog(Points(client))
