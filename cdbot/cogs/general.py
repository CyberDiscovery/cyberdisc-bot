import os

from discord.ext.commands import Bot, Cog
from git import Repo

path = os.path.dirname(os.path.abspath(__file__))
path = '/'.join(path.split('/')[:-2])

repo = Repo(path)
latest = repo.commit()


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
        message, *_ = latest.message.partition('\n')
        link = f'{next(repo.remote().urls)}/commit/{latest}'
        date = latest.authored_datetime.strftime('**%x** at **%X**')
        self.bot.log.info(
            "CyberDiscovery bot is now logged in.\n"
            f"Latest commit: **[{message}]({link})**"
            f"\nAuthor: **{latest.author}** on {date}"
        )

    @Cog.listener()
    async def on_command_error(self, ctx, error):
        self.bot.log.exception(error)


def setup(bot):
    bot.add_cog(General(bot))
