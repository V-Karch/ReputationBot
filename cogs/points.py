import discord
from db import DB
from enum import Enum
from discord.ext import commands
from discord import app_commands

OWNER_ID = 923600698967461898


class ExperienceType(Enum):
    positive = "positive"
    negative = "negative"


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


def add_entry_to_points_db(
    target_user_id: int,
    author_user_id: int,
    experience_type: ExperienceType,
    reason: str,
):
    # Determine point value
    if experience_type == ExperienceType.positive:
        point_value = 1
    else:
        point_value = -1

    sql = """
        INSERT INTO reputation (target_user_id, author_user_id, point_value, reason)
        VALUES (?, ?, ?, ?)
    """

    db = DB("points.db")
    db.exec_sql(sql, (target_user_id, author_user_id, point_value, reason))


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

    @app_commands.command(
        name="reputation", description="Add or subtract reputation from a person"
    )
    @app_commands.describe(
        user="The user you want to modify the reputation for",
        experience="The type of experience you had (positive or negative)",
        reason="The reason you are giving this person reputation",
    )
    @app_commands.checks.cooldown(
        1, 300, key=lambda interaction: (interaction.guild_id, interaction.user.id)
    )
    async def reputation(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        experience: ExperienceType,
        reason: str,
    ):
        await interaction.response.defer()

        if interaction.user == user:
            await interaction.followup.send("You can't give reputation to yourself!")

        add_entry_to_points_db(user.id, interaction.user.id, experience, reason)

        if experience == ExperienceType.positive:
            color = discord.Color.green()
            emoji = "👍"
        else:
            color = discord.Color.red()
            emoji = "👎"

        response_embed = discord.Embed(
            title="Reputation Updated!",
            description=f"{interaction.user.mention} gave {emoji} reputation to {user.mention}",
            color=color,
        )
        response_embed.add_field(name="Reason", value=reason, inline=False)

        await interaction.followup.send(embed=response_embed)

    @reputation.error
    async def reputation_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                f"⏳ You’re on cooldown! Try again in {error.retry_after:.1f} seconds.",
                ephemeral=True,
            )
        else:
            # fallback for unexpected errors
            await interaction.response.send_message(
                "⚠️ An unexpected error occurred while running this command.",
                ephemeral=True,
            )
            raise error


async def setup(client: commands.Bot):
    await client.add_cog(Points(client))
