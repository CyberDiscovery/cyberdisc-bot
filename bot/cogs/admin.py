from discord import Member
from discord.ext.commands import Bot, Context, command, has_any_role

from bot.constants import ADMIN_ROLES, BANNED_DOMAINS


class Admin:
    """
    Administration related commands.
    """

    def __init__(self, bot: Bot):
        self.bot = bot

    async def mute_member(self, member: Member, reason: str="N/A"):
        self.bot.muted.append(member.id)
        print(f"Member {member} ({member.id}) has been muted for reason: {reason}")

    async def unmute_member(self, member: Member, reason: str="N/A"):
        self.bot.muted.remove(member.id)
        print(f"Member {member} ({member.id}) has been unmuted for reason: {reason}")

    @command()
    @has_any_role(*ADMIN_ROLES)
    async def mute(self, ctx: Context, member: Member, reason: str="N/A"):
        """
        Command to mute people.
        """

        # Ignore request to mute admins.
        if any(name in [role.name for role in member.roles] for name in ADMIN_ROLES):
            await ctx.send(f"{ctx.author.mention} | Can't mute an admin!")

        else:
            await self.mute_member(member, reason=reason)
            await ctx.send(f"{ctx.author.mention} | {member.mention} has been muted.")

    @command()
    @has_any_role(*ADMIN_ROLES)
    async def unmute(self, ctx: Context, member: Member, reason: str="N/A"):
        """
        Command to unmute people.
        """

        await self.unmute_member(member, reason=reason)
        await ctx.send(f"{ctx.author.mention} | {member.mention} has been unmuted.")
    
    @command()
    @has_any_role(*ADMIN_ROLES)
    async def purge_from(self, ctx: Context, message: int, limit: int = 1000, reason: str = "N/A"):
        """
        Command to purge all messages since a certain message id.
        """

        # Limit defaults to 1000, can be increased/decreased.
        # Gets message and deletes all after it within the limits
        await ctx.channel.purge(limit=limit, after=await ctx.channel.get_message(message))
        await ctx.send(f"Messages purged since message ID: {message}")

    async def on_message(self, message):
        # Check if author is muted
        if message.author.id in self.bot.muted:
            await message.delete()
            await message.author.send("You are muted!")

        # Check if message contains a banned domain
        elif any(domain in message.content.lower() for domain in BANNED_DOMAINS) and not message.author.bot:
            await message.delete()
            await message.channel.send(f"{message.author.mention} | That domain is banned! You have been muted.")
            await self.mute_member(message.author, "Message contains banned domain")


def setup(bot):
    bot.add_cog(Admin(bot))
