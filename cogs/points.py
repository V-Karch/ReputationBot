import discord
from discord.ext import commands
from discord import app_commands
from db import DB, ExperienceType
from model.history_paginator import HistoryPaginator, ShowHistoryButton
from model.reputation_manager import ReputationManager

OWNER_ID = 923600698967461898


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

        DB.setup_points_db()
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
            return

        DB.add_entry_to_points_db(user.id, interaction.user.id, experience, reason)

        color = (
            discord.Color.green()
            if experience == ExperienceType.positive
            else discord.Color.red()
        )
        emoji = "👍" if experience == ExperienceType.positive else "👎"

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
            await interaction.response.send_message(
                "⚠️ An unexpected error occurred while running this command.",
                ephemeral=True,
            )
            raise error

    @app_commands.command(
        name="check_reputation", description="Check a user's reputation"
    )
    @app_commands.describe(user="The user who's reputation you want to check")
    async def check_reputation(
        self, interaction: discord.Interaction, user: discord.Member
    ):
        await interaction.response.defer()

        db = DB("points.db")
        cursor = db.get_cursor()
        cursor.execute(
            "SELECT point_value, reason, author_user_id FROM reputation WHERE target_user_id = ?",
            (user.id,),
        )
        rows = cursor.fetchall()
        total_points = sum(row[0] for row in rows)

        embed = discord.Embed(
            title=f"{user.display_name}'s Reputation",
            description=f"**Total Reputation:** {total_points}",
            color=discord.Color.blurple(),
        )

        if not rows:
            embed.description += "\nNo reputation history yet."
            await interaction.followup.send(embed=embed)
            return

        view = HistoryPaginator(db, rows, user, total_points)
        await interaction.followup.send(embed=embed, view=ShowHistoryButton(view))

    @app_commands.command(
        name="manage_reputation",
        description="View and manually modify a user's reputation (moderator only)",
    )
    @app_commands.describe(user="The user whose reputation you want to manage")
    async def manage_reputation(
        self, interaction: discord.Interaction, user: discord.Member
    ):
        await interaction.response.defer(ephemeral=True)

        if interaction.user.id != OWNER_ID:
            await interaction.followup.send("You are not allowed to use this command.")
            return

        db = DB("points.db")

        view = ReputationManager(db, user)
        await interaction.followup.send(
            embed=view.get_page_embed(),
            view=view,
        )


async def setup(client: commands.Bot):
    await client.add_cog(Points(client))
