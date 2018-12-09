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

        quote_channel = self.bot.get_channel(QUOTES_CHANNEL_ID)

        def is_quote(message: Message):
            return message.author.id == QUOTES_BOT_ID

        async for quote in quote_channel.history(limit=None).filter(is_quote):
            if not quote.embeds:
                continue
            author = quote.embeds[0].author.icon_url
            if 'avatars' not in author:
                print('A quote was unable to be loaded due to author having a default avatar.')
                continue

            author = int(author.split('avatars')[1][1:19])
            self.bot.quotes[author].append(quote.id)
        print(self.bot.quotes)


def setup(bot):
    bot.add_cog(General(bot))
