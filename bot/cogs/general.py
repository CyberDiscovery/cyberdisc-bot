from discord import Message, utils
from discord.ext.commands import Bot

from bot.constants import LOG_CHANNEL_ID, QUOTES_BOT_ID, QUOTES_CHANNEL_ID


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
        log_channel = self.bot.get_channel(LOG_CHANNEL_ID)

        def is_quote(message: Message):
            return message.author.id == QUOTES_BOT_ID

        async for quote in quote_channel.history(limit=None).filter(is_quote):
            if not quote.embeds:
                continue
            icon_url = quote.embeds[0].author.icon_url.split('/')
            author = int(icon_url[4]) if 'avatars' in icon_url else None
            if not author:
                name = quote.embeds[0].author.name.split('#')
                author = utils.get(quote_channel.guild.members, name=name[0], discriminator=name[1])
                if not author:
                    await log_channel.send("The following quote was unable to be cached: ", embed=quote.embeds[0])
                    continue
            self.bot.quotes[author].append(quote.id)


def setup(bot):
    bot.add_cog(General(bot))
