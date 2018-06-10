from urllib.parse import urlencode

from discord import Message
from discord.ext.commands import Bot, Context, command

from bot.constants import EVERYONE_REACTIONS


class Fun:
    """
    Commands for fun!
    """

    def __init__(self, bot: Bot):
        self.bot = bot

    async def on_message(self, message: Message):
        if any(mention in message.content for mention in ("@here", "@everyone")):
            for emoji in EVERYONE_REACTIONS:
                await message.add_reaction(emoji)

        if "dabato" in message.content:
            await message.add_reaction("🤔")

    @command(aliases=["l"])
    async def lmgtfy(self, ctx: Context, search_text: str, *args):
        """
        Lets the bot google that for you.
        """

        delete = False
        ie = False
        if "-d" in args:
            delete = True
        if "-ie" in args:
            ie = True
        
        request_data = {
            "q": search_text,
            "ie": int(ie)
        }

        url = "https://lmgtfy.com/?" + urlencode(request_data)
        await ctx.send(url)

        if delete:
            await ctx.message.delete()

def setup(bot):
    bot.add_cog(Fun(bot))
