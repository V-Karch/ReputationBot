import discord


class HistoryPaginator(discord.ui.View):
    def __init__(self, db_instance, entries, member, total_points, per_page=10):
        super().__init__(timeout=60)
        self.db = db_instance  # store the DB instance
        self.entries = entries
        self.member = member
        self.per_page = per_page
        self.total_points = total_points
        self.current_page = 0
        self.max_page = (len(entries) - 1) // per_page

        self.prev_button.disabled = self.max_page <= 0
        self.next_button.disabled = self.max_page <= 0

    def get_page_embed(self):
        start = self.current_page * self.per_page
        end = start + self.per_page
        page_entries = self.entries[start:end]

        description_lines = [f"**Total Reputation:** {self.total_points}\n"]
        for points, reason, author_id in page_entries:
            description_lines.append(
                f"{points:+d} | By <@{author_id}> | Reason: {reason}"
            )

        page_embed = discord.Embed(
            title=f"{self.member.display_name}'s Reputation History",
            description="\n".join(description_lines),
            color=discord.Color.blurple(),
        )
        page_embed.set_footer(text=f"Page {self.current_page + 1}/{self.max_page + 1}")
        return page_embed

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


class ShowHistoryButton(discord.ui.View):
    def __init__(self, paginator):
        super().__init__(timeout=60)
        self.paginator = paginator

    @discord.ui.button(label="Show History", style=discord.ButtonStyle.primary)
    async def show_history(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.edit_message(
            embed=self.paginator.get_page_embed(), view=self.paginator
        )
