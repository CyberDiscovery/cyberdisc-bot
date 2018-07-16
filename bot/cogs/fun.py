"""
Set of bot commands designed for general leisure.
"""
from random import choice, randint
from urllib.parse import urlencode

from aiohttp import ClientSession
from discord import Embed, Member, Message
from discord.ext.commands import (BadArgument, Bot, Context, EmojiConverter,
                                  command)

from bot.constants import EVERYONE_REACTIONS, QUOTE_CHANNEL_ID


class Fun:
    """
    Commands for fun!
    """

    def __init__(self, bot: Bot):
        self.bot = bot

    async def on_message(self, message: Message):
        """
        React based on the contents of a message.
        """
        # React if a message contains an @here or @everyone mention.
        if any(mention in message.content
                for mention in ("@here", "@everyone")):
            for emoji in EVERYONE_REACTIONS:
                await message.add_reaction(emoji)

        # React if message contains dabato.
        if "dabato" in message.content:
            await message.add_reaction("🤔")

    @command()
    async def lmgtfy(self, ctx: Context, *args: str):
        """
        Returns a LMGTFY URL for a given user argument.
        """

        # Flag checking.
        delete = False
        ie_flag = False
        if "-d" in args:
            delete = True
        if "-ie" in args:
            ie_flag = True

        # Creates a lmgtfy.com url for the given query.
        request_data = {
            "q": " ".join(arg for arg in args if not arg.startswith("-")),
            "ie": int(ie_flag)
        }
        url = "https://lmgtfy.com/?" + urlencode(request_data)

        await ctx.send(url)

        if delete:
            await ctx.message.delete()

    @command()
    async def react(self, ctx: Context, *reactions: str):
        """
        Reacts to the previous message with the given space-separated emojis.
        """
        # Added mutability
        reactions = list(reactions)

        # Detect if message number is present in the invocation arguments.
        msg_num = 1
        if reactions[0].isdigit():
            msg_num += int(reactions.pop(0))
        else:
            msg_num += 1

        # Getting the message to react to.
        message = await ctx.channel.history(limit=msg_num, reverse=True).next()
        await ctx.message.delete()

        unknown_emojis = []

        # Reacts to the message.
        for reaction in reactions:
            if len(reaction) > 1:
                try:
                    reaction = await EmojiConverter().convert(ctx, reaction)
                except BadArgument:
                    unknown_emojis.append(reaction)
                    continue
            await message.add_reaction(reaction)

        # Informs the user of unknown emojis.
        if unknown_emojis:
            emoji_string = ", ".join(unknown_emojis)
            # Inserts an invisible character to render mass mentions ineffective.
            emoji_string = emoji_string.replace("@here", "@\xadhere").replace("@everyone", "@\xadeveryone")
            await ctx.send(f"Unknown emojis: {emoji_string}")

    @command()
    async def xkcd(self, ctx: Context, number: str=None):
        """
        Fetches xkcd comics.
        If number is left blank, automatically fetches the latest comic.
        If number is set to '?', a random comic is fetched.
        """

        # Creates endpoint URI
        if number is None or number == "?":
            endpoint = "https://xkcd.com/info.0.json"
        else:
            endpoint = f"https://xkcd.com/{number}/info.0.json"

        # Fetches JSON data from endpoint
        async with ClientSession() as session:
            async with session.get(endpoint) as response:
                data = await response.json()

        # Updates comic number
        if number == "?":
            number = randint(1, int(data["num"]))  # noqa: B311
            endpoint = f"https://xkcd.com/{number}/info.0.json"
            async with ClientSession() as session:
                async with session.get(endpoint) as response:
                    data = await response.json()
        else:
            number = data["num"]

        # Creates date object (Sorry, but I'm too tired to use datetime.)
        date = f"{data['day']}/{data['month']}/{data['year']}"

        # Creates Rich Embed, populates it with JSON data and sends it.
        comic = Embed()
        comic.title = data["safe_title"]
        comic.set_footer(text=data["alt"])
        comic.set_image(url=data["img"])
        comic.url = f"https://xkcd.com/{number}"
        comic.set_author(
            name="xkcd",
            url="https://xkcd.com/",
            icon_url="https://xkcd.com/s/0b7742.png")
        comic.add_field(name="Number:", value=number)
        comic.add_field(name="Date:", value=date)
        comic.add_field(
            name="Explanation:",
            value=f"https://explainxkcd.com/{number}")

        await ctx.send(embed=comic)

    @command()
    async def quotes(self, ctx: Context, member: Member=None):
        """
        Returns a random quotation from the #quotes channel.
        A user can be specified to return a random quotation from that user.
        A channel ID must be specified in QUOTE_CHANNEL_ID for the bot to retrieve the quotations successfully.
        """
        quotation_channel = self.bot.get_channel(QUOTE_CHANNEL_ID)
        if member is not None:
            all_quotations = await quotation_channel.history(limit=None).flatten()
            quotations = []
            for quotation in all_quotations:
                embed = quotation.embeds[0]
                author_name = embed.author.name
                author = ctx.message.guild.get_member_named(author_name)
                if author == member:
                    quotations.append(quotation)
        else:
            quotations = await quotation_channel.history(limit=None).flatten()
        quotation = choice(quotations)
        embed_quotation = quotation.embeds[0]
        await ctx.send(embed=embed_quotation)


def setup(bot):
    """
    Required boilerplate for adding functionality of cog to bot.
    """
    bot.add_cog(Fun(bot))
