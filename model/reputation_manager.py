import discord


# ----- Reputation Manager View -----
class ReputationManager(discord.ui.View):
    def __init__(self, db_instance, member, per_page=5):
        super().__init__(timeout=120)
        self.db = db_instance
        self.member = member
        self.per_page = per_page
        self.current_page = 0
        self.entries = []
        self.max_page = 0
        # Load initial entries from DB
        self.refresh_entries_sync()
        self.update_buttons()

    def refresh_entries_sync(self):
        """Synchronous fetch of entries for init."""
        cursor = self.db.get_cursor()
        cursor.execute(
            "SELECT id, point_value, reason, author_user_id FROM reputation "
            "WHERE target_user_id = ? ORDER BY id",
            (self.member.id,),
        )
        self.entries = cursor.fetchall()
        self.max_page = max((len(self.entries) - 1) // self.per_page, 0)
        self.current_page = min(self.current_page, self.max_page)

    async def refresh_entries(self):
        """Async-friendly refresh."""
        cursor = self.db.get_cursor()
        cursor.execute(
            "SELECT id, point_value, reason, author_user_id FROM reputation "
            "WHERE target_user_id = ? ORDER BY id",
            (self.member.id,),
        )
        self.entries = cursor.fetchall()
        self.max_page = max((len(self.entries) - 1) // self.per_page, 0)
        self.current_page = min(self.current_page, self.max_page)
        self.update_buttons()

    def update_buttons(self):
        self.prev_button.disabled = self.current_page == 0
        self.next_button.disabled = self.current_page == self.max_page

    def get_page_embed(self):
        start = self.current_page * self.per_page
        end = start + self.per_page
        page_entries = self.entries[start:end]

        description_lines = [
            f"**Managing Reputation for {self.member.display_name}**\n"
        ]
        for entry_id, points, reason, author_id in page_entries:
            description_lines.append(
                f"ID: {entry_id} | Points: {points:+d} | Author: <@{author_id}> | Reason: {reason}"
            )

        embed = discord.Embed(
            title=f"Reputation Entries (Page {self.current_page + 1}/{self.max_page + 1})",
            description=(
                "\n".join(description_lines) if description_lines else "No entries."
            ),
            color=discord.Color.orange(),
        )
        return embed

    # ----- Navigation Buttons -----
    @discord.ui.button(label="Previous", style=discord.ButtonStyle.secondary)
    async def prev_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        self.current_page = max(self.current_page - 1, 0)
        self.update_buttons()
        await interaction.response.edit_message(embed=self.get_page_embed(), view=self)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.secondary)
    async def next_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        self.current_page = min(self.current_page + 1, self.max_page)
        self.update_buttons()
        await interaction.response.edit_message(embed=self.get_page_embed(), view=self)

    # ----- Delete Entry Button -----
    @discord.ui.button(label="Delete Entry", style=discord.ButtonStyle.danger)
    async def delete_entry(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.send_modal(DeleteEntryModal(self))

    # ----- Add Entry Button -----
    @discord.ui.button(label="Add Entry", style=discord.ButtonStyle.success)
    async def add_entry(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.send_modal(AddEntryModal(self))


# ----- Modal for Deleting Entries -----
class DeleteEntryModal(discord.ui.Modal, title="Delete Reputation Entry"):
    entry_id: discord.ui.TextInput

    def __init__(self, manager_view):
        super().__init__()
        self.manager_view = manager_view

        self.entry_id = discord.ui.TextInput(
            label="Entry ID to Delete",
            placeholder="Enter the ID of the entry to delete",
            required=True,
        )
        self.add_item(self.entry_id)

    async def on_submit(self, interaction: discord.Interaction):
        cursor = self.manager_view.db.get_cursor()
        cursor.execute(
            "DELETE FROM reputation WHERE id = ?", (int(self.entry_id.value),)
        )
        self.manager_view.db.get_connection().commit()
        await self.manager_view.refresh_entries()
        await interaction.response.edit_message(
            embed=self.manager_view.get_page_embed(), view=self.manager_view
        )


# ----- Modal for Adding Entries -----
class AddEntryModal(discord.ui.Modal, title="Add Reputation Entry"):
    point_value: discord.ui.TextInput
    reason: discord.ui.TextInput
    target_user_id: discord.ui.TextInput

    def __init__(self, manager_view):
        super().__init__()
        self.manager_view = manager_view

        # Pre-fill target_user_id with member being managed
        self.target_user_id = discord.ui.TextInput(
            label="Target User ID",
            default=str(manager_view.member.id),
            required=True,
        )
        self.point_value = discord.ui.TextInput(
            label="Point Value (+1 or -1)",
            placeholder="Enter 1 or -1",
            required=True,
        )
        self.reason = discord.ui.TextInput(
            label="Reason",
            placeholder="Reason for reputation change",
            required=True,
        )

        # Add inputs to modal
        self.add_item(self.target_user_id)
        self.add_item(self.point_value)
        self.add_item(self.reason)

    async def on_submit(self, interaction: discord.Interaction):
        cursor = self.manager_view.db.get_cursor()
        cursor.execute(
            "INSERT INTO reputation (target_user_id, author_user_id, point_value, reason) "
            "VALUES (?, ?, ?, ?)",
            (
                int(self.target_user_id.value),
                interaction.user.id,
                int(self.point_value.value),
                self.reason.value,
            ),
        )
        self.manager_view.db.get_connection().commit()
        await self.manager_view.refresh_entries()
        await interaction.response.edit_message(
            embed=self.manager_view.get_page_embed(), view=self.manager_view
        )
