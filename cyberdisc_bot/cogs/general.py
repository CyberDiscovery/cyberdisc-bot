from discord.ext.commands import Bot

<<<<<<< HEAD:cyberdisc_bot/cogs/general.py
from cyberdisc_bot.constants import QUOTES_BOT_ID, QUOTES_CHANNEL_ID

=======
>>>>>>> master:bot/cogs/general.py

class General:
    """
    General Purpose Commands
    """

    def __init__(self, bot: Bot):
        self.bot = bot

    async def on_ready(self):
        print("Logged in as")
        print(self.bot.user.name)
        print(self.bot.user.id)
        print("------")

        self.bot.log.info("CyberDiscovery bot is now logged in.")

    async def on_command_error(self, ctx, error):
        self.bot.log.exception(error)


def setup(bot):
    bot.add_cog(General(bot))
