"""Reacts with the "No U" emote to any message that mentions the bot"""

from discord.utils import find


class NoU:
    def __init__(self, bot):
        self.bot = bot

    async def on_message(self, msg):
        if msg.guild:
            me = msg.guild.me
            if me in msg.mentions:
                emoji = find(lambda e: e.name.lower() == "nou", msg.guild.emojis)
                await msg.add_reaction(emoji)


def setup(bot):
    bot.add_cog(NoU(bot))
