from discord import Message
from discord.ext.commands import Bot, BucketType, Context, command, cooldown

from bot.constants import QUOTES_BOT_ID, QUOTES_CHANNEL_ID, SELF_ROLE_NAMES


class General:
    """
    General Purpose Commands
    """

    def __init__(self, bot: Bot):
        self.bot = bot

    @cooldown(rate=1, per=5, type=BucketType.user)
    @command(aliases=["y"])
    async def year(self, ctx: Context, year_group: str):
        """
        Self-assigns a role to the user based on their year group, e.g. :year 11

        Use ":year old" if no longer in secondary education
        Use ":year remove" to remove all self-assignable roles

        Rate limited to one use per five seconds per user
        """
        year_group = year_group.lower()
        roles_to_remove = list(filter(lambda role: role.name in SELF_ROLE_NAMES.values(), ctx.guild.roles))

        if year_group == "remove":
            await ctx.author.remove_roles(*roles_to_remove)
            await ctx.send("All self-assignable roles removed successfully")
            return

        role_name = SELF_ROLE_NAMES.get(year_group, None)

        if role_name is None:
            await ctx.send(f"Not a self-assignable role. Try one of: {', '.join(SELF_ROLE_NAMES.keys())}")
        else:
            roles_to_add = list(filter(lambda role: role.name == role_name, ctx.guild.roles))

            await ctx.author.remove_roles(*roles_to_remove)
            await ctx.author.add_roles(*roles_to_add)

            await ctx.send("Role assigned successfully.")

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
