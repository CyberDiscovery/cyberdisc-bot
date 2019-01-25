from discord import Message
from discord.ext.commands import Bot

from bot.constants import QUOTES_BOT_ID, QUOTES_CHANNEL_ID


class General:
    """
    General Purpose Commands
    """

    def __init__(self, bot: Bot):
        self.bot = bot

    async def on_ready(self):
        print('Logged in as')
        print(self.bot.user.name)
        print(self.bot.user.id)
        print('------')

        self.bot.log.info("CyberDiscovery bot is now logged in.")

        quote_channel = self.bot.get_channel(QUOTES_CHANNEL_ID)

        def is_quote(message: Message):
            return message.author.id == QUOTES_BOT_ID

        async for quote in quote_channel.history(limit=None).filter(is_quote):
            if not quote.embeds:
                continue
            author = quote.embeds[0].author.name
            self.bot.quotes[author].append(quote.id)


def setup(bot):
    bot.add_cog(General(bot))
