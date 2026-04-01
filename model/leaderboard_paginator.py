import discord
from db import DB


class LeaderboardPaginator(discord.ui.View):
    def __init__(self, per_page=10):
        super().__init__(timeout=120)
        self.per_page = per_page
        self.current_page = 0
        self.entries = DB.get_leaderboard(top_n=1000)
        self.max_page = max((len(self.entries) - 1) // self.per_page, 0)
        self.prev_button.disabled = self.max_page <= 0
        self.next_button.disabled = self.max_page <= 0

    def get_page_embed(self):
        start = self.current_page * self.per_page
        end = start + self.per_page
        page_entries = self.entries[start:end]

        embed = discord.Embed(
            title="Reputation Leaderboard",
            color=discord.Color.gold(),
        )
        description_lines = []
        for idx, (user_id, points) in enumerate(page_entries, start=start + 1):
            description_lines.append(f"**{idx}.** <@{user_id}> - {points} pts")
        embed.description = "\n".join(description_lines)
        embed.set_footer(text=f"Page {self.current_page + 1}/{self.max_page + 1}")
        return embed

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.secondary)
    async def prev_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if self.current_page > 0:
            self.current_page -= 1
            await interaction.response.edit_message(
                embed=self.get_page_embed(), view=self
            )

    @discord.ui.button(label="Next", style=discord.ButtonStyle.secondary)
    async def next_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if self.current_page < self.max_page:
            self.current_page += 1
            await interaction.response.edit_message(
                embed=self.get_page_embed(), view=self
            )
