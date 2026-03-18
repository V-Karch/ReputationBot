import discord
from discord.ext import commands

OWNER_ID = 923600698967461898


class Autoreply(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command(
        name="customot", description="Display CustomOT Tutorial", aliases=["cot"]
    )
    async def custom_ot(self, context: commands.Context, user: discord.Member = None):
        embed = discord.Embed(
            title="How To Make a Custom OT Pokemon",
            color=0x237FEB,
            description="1. To customize the original trainer name or OT, the Pokemon needs to be in Pokemon Go. \n2. You must then change your Pokemon Home name on the mobile app to whatever OT you require. \n\nNote: It is recommended to restart Pokemon Go after this before transferring as Pokemon Home may be slow to register any changes.",
        )

        await context.reply(content=user.mention if user else "", embed=embed)

    @commands.command(
        name="stamp",
        description="Display Difference Between Pokemon Go Stamp and Pokemon Go Origin Marker",
    )
    async def stamp(self, context: commands.Context, user: discord.Member = None):
        embed = discord.Embed(
            title="The Pokemon Go Stamp and Pokemon Go Origin Marker are NOT the same.",
            color=0x237FEB,
            description="The stamp shows the game that the pokemon was last in before being transferred to home.\nThis is important because pokemon cannot obtain the stamp once lost, but hacked pokemon **may** have the origin marker.",
        )
        embed.set_image(url="https://i.imgur.com/PZKnD5p.jpg")

        await context.reply(content=user.mention if user else "", embed=embed)

    @commands.command(
        name="crosspost", description="Warns users not to crosspost", aliases=["crossp"]
    )
    async def crosspost(self, context: commands.Context, user: discord.Member = None):
        embed = discord.Embed(
            title="❗️Do not post your request in more than one channel",
            color=0x237FEB,
            description="Please give it some time before requesting again depending on the length of your demand.\n\n*Refrain from crossposting again. Thank you for understanding.*",
        )

        await context.reply(content=user.mention if user else "", embed=embed)

    @commands.command(
        name="tradechannels",
        description="Tells users where the trade channels are",
        aliases=["tc"],
    )
    async def tradechannels(
        self, context: commands.Context, user: discord.Member = None
    ):
        embed = discord.Embed(
            title="❗️ This is not a trade channel",
            color=0x237FEB,
            description="Click below and please repost your request in one of the following locations:\n",
        )

        embed.description += "\nTrade Hub 1: <#1341162683734425631>\n"
        embed.description += "Trade Hub 2: <#1341162764701536398>\n"
        embed.description += "Shiny Trade: <#1047110840735768636>\n\n"
        embed.description += (
            "Alternatively, For different games, we have the following:"
        )
        embed.description += "\n\nLegends ZA: <#1428946618392252416>\n"
        embed.description += "Legends Arceus: <#1070473675289133116>\n"
        embed.description += "Brilliant Diamond/Shining Pearl: <#1070473596302012507>\n"
        embed.description += "Sword and Shield: <#1070427983367651348>\n"
        embed.description += "Pokemon Let's Go: <#1070473752695021598>"

        # Consolidation
        print(embed.description)

        await context.reply(content=user.mention if user else "", embed=embed)


async def setup(client: commands.Bot):
    await client.add_cog(Autoreply(client))
