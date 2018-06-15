from urllib.parse import urlencode

from bot.constants import EVERYONE_REACTIONS

from discord import Message
from discord.ext.commands import (BadArgument, Bot, Context, EmojiConverter,
                                  command)


class Fun:
    """
    Commands for fun!
    """

    def __init__(self, bot: Bot):
        self.bot = bot

    async def on_message(self, message: Message):
        # React if a message contains an @here or @everyone mention.
        if any(ping in message.content for ping in ("@here", "@everyone")):
            for emoji in EVERYONE_REACTIONS:
                await message.add_reaction(emoji)

        # React if message contains dabato.
        if "dabato" in message.content:
            await message.add_reaction("🤔")

    @command()
    async def lmgtfy(self, ctx: Context, search_text: str, *args):
        """
        Lets the bot google that for you.
        """

        # Flag checking.
        delete = False
        ie = False
        if "-d" in args:
            delete = True
        if "-ie" in args:
            ie = True

        # Creates a lmgtfy.com url for the given query.
        request_data = {
            "q": search_text,
            "ie": int(ie)
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
            await ctx.send(f"Unknown emojis: {emoji_string}")


def setup(bot):
    bot.add_cog(Fun(bot))
