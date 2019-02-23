from discord.ext.commands import Bot, Cog


class General(Cog):
    """
    General Purpose Commands
    """

    def __init__(self, bot: Bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        print("Logged in as")
        print(self.bot.user.name)
        print(self.bot.user.id)
        print("------")

        self.bot.log.info("CyberDiscovery bot is now logged in.")

    @Cog.listener()
    async def on_command_error(self, ctx, error):
        self.bot.log.exception(error)


def setup(bot):
    bot.add_cog(General(bot))
