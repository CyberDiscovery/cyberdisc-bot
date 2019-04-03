from discord.ext.commands import Bot, Cog
from git import Repo


commit = Repo().commit()


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
        date = commit.authored_datetime.strftime('**%x** at **%X**')
        self.bot.log.info(
            "CyberDiscovery bot is now logged in.\n"
            f"Latest commit: **[{commit}](https://github.com/CyberDiscovery/cyberdisc-bot/commit/{commit})**"
            f"\nAuthor: **{commit.author}** on {date}"
        )

    @Cog.listener()
    async def on_command_error(self, ctx, error):
        self.bot.log.exception(error)


def setup(bot):
    bot.add_cog(General(bot))
