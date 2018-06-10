from discord.ext.commands import Bot

from bot.constants import BANNED_DOMAINS


class Admin:
    """
    Administration related commands.
    """

    def __init__(self, bot: Bot):
        self.bot = bot

    async def mute_member(self, member, reason="N/A"):
        self.bot.muted.append(member.id)
        print(f"Member {member} ({member.id}) has been muted for reason: {reason}")

    async def on_message(self, message):
        if message.author.id in self.bot.muted:
            await message.delete()
            await message.author.send("You are muted!")
        
        elif any(domain in message.content.lower() for domain in BANNED_DOMAINS):
            await message.delete()
            await message.channel.send(f"{message.author.mention} | That domain is banned! You have been muted.")
            await self.mute_member(message.author, "Message contains banned domain")

def setup(bot):
    bot.add_cog(Admin(bot))
