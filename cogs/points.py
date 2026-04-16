import discord
from discord.ext import commands
from discord import app_commands
from db import DB, ExperienceType
from model.leaderboard_paginator import LeaderboardPaginator
from model.history_paginator import HistoryPaginator, ShowHistoryButton
from model.reputation_manager import ReputationManager

OWNER_ID = 923600698967461898

TRADER_RANKS = [
    {"name": "Potential Trader", "required": 5, "role_id": 1484354856352219327},
    {"name": "Trusted Trader", "required": 15, "role_id": 1058092559773216858},
    {"name": "Trade Leader", "required": 30, "role_id": 1484356325960978442},
    {"name": "Elite Trader", "required": 45, "role_id": 1058867257868030012},
    {"name": "Champion Trader", "required": 100, "role_id": 1484356944822140960},
]


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
            "SELECT point_value, reason, author_user_id FROM reputation WHERE target_user_id = ? ORDER BY id DESC",
            (user.id,),
        )
        rows = cursor.fetchall()
        total_points = sum(row[0] for row in rows)
        unique_users = len(set(row[2] for row in rows if row[0] > 0))

        embed = discord.Embed(
            title=f"{user.display_name}'s Reputation",
            description=f"**Total Reputation:** {total_points}\n"
            + f"**Unique Traders**: {unique_users}",
            color=discord.Color.blurple(),
        )

        if not rows:
            embed.description += "\nNo reputation history yet."
            await interaction.followup.send(embed=embed)
            return

        view = HistoryPaginator(db, rows, user, total_points, unique_users)
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

        if (
            interaction.user.id != OWNER_ID
        ):  # TODO: Change this to be available for anyone Mod+
            await interaction.followup.send("You are not allowed to use this command.")
            return

        db = DB("points.db")

        view = ReputationManager(db, user)
        await interaction.followup.send(
            embed=view.get_page_embed(),
            view=view,
        )

    @app_commands.command(
        name="repboard", description="Display top users by reputation points"
    )
    async def repboard(self, interaction: discord.Interaction):
        await interaction.response.defer()
        paginator = LeaderboardPaginator(per_page=10)
        if not paginator.entries:
            await interaction.followup.send("No reputation data yet.")
            return
        await interaction.followup.send(
            embed=paginator.get_page_embed(), view=paginator
        )

    @app_commands.command(
        name="reprank", description="Display your ranking in the reputation leaderboard"
    )
    async def reprank(self, interaction: discord.Interaction):
        await interaction.response.defer()
        rank = DB.get_user_rank(interaction.user.id)
        if rank == 0:
            await interaction.followup.send("You have no reputation points yet.")
            return
        await interaction.followup.send(
            f"You are currently ranked #{rank} on the leaderboard."
        )

    @app_commands.command(
        name="traderank",
        description="Check your trading rank based on unique traders",
    )
    @app_commands.describe(user="User to check (optional)")
    async def traderank(
        self,
        interaction: discord.Interaction,
        user: discord.Member | None = None,
    ):
        await interaction.response.defer()

        # Determine target
        member = user or interaction.user
        member = interaction.guild.get_member(member.id)

        unique_users = DB.get_unique_traders_count(member.id)

        current_rank = None
        next_rank = None

        for rank in TRADER_RANKS:
            if unique_users >= rank["required"]:
                current_rank = rank
            elif unique_users < rank["required"] and next_rank is None:
                next_rank = rank

        if current_rank is None:
            current_rank = {
                "name": "Unranked",
                "required": 0,
                "role_id": None,
            }

        # Only sync roles if checking self
        is_self = member.id == interaction.user.id

        ranked_up = False

        if is_self:
            eligible_roles = {
                rank["role_id"]
                for rank in TRADER_RANKS
                if unique_users >= rank["required"]
            }

            all_rank_roles = {rank["role_id"] for rank in TRADER_RANKS}
            user_role_ids = {role.id for role in member.roles}

            roles_to_add_ids = eligible_roles - user_role_ids
            roles_to_remove_ids = (user_role_ids & all_rank_roles) - eligible_roles

            ranked_up = (
                current_rank["role_id"] is not None
                and current_rank["role_id"] not in user_role_ids
            )

            roles_to_add = [
                interaction.guild.get_role(rid)
                for rid in roles_to_add_ids
                if interaction.guild.get_role(rid)
            ]

            roles_to_remove = [
                interaction.guild.get_role(rid)
                for rid in roles_to_remove_ids
                if interaction.guild.get_role(rid)
            ]

            if roles_to_add:
                await member.add_roles(*roles_to_add, reason="Trader rank sync (add)")
            if roles_to_remove:
                await member.remove_roles(
                    *roles_to_remove, reason="Trader rank sync (remove)"
                )

        # Progress text
        if next_rank:
            remaining = next_rank["required"] - unique_users
            progress_text = (
                f"{remaining} more unique traders needed for <@&{next_rank['role_id']}>"
            )
        else:
            progress_text = "Maximum rank achieved"

        # Tier list
        tier_lines = [
            f"<@&{rank['role_id']}> — {rank['required']} traders"
            for rank in TRADER_RANKS
        ]

        subject = "Your" if is_self else f"{member.mention}'s"

        embed = discord.Embed(
            title="Trading Rank",
            color=discord.Color.blurple(),
            description=(
                f"**{subject} Unique Traders:** {unique_users}\n\n"
                f"**Current Rank:** "
                + (
                    f"<@&{current_rank['role_id']}>"
                    if current_rank["role_id"]
                    else "Unranked"
                )
                + f"\n\n**Next Rank Progress:** {progress_text}"
            ),
        )

        embed.add_field(
            name="Rank Tiers",
            value="\n".join(tier_lines),
            inline=False,
        )

        content = None
        if is_self and ranked_up and current_rank["role_id"]:
            content = member.mention
            embed.add_field(
                name="",
                value=f"Congratulations! You have ranked up to <@&{current_rank['role_id']}>",
                inline=False,
            )

        await interaction.followup.send(content=content, embed=embed)


async def setup(client: commands.Bot):
    await client.add_cog(Points(client))
