import os

from discord import Colour, Embed
from discord.ext import commands
from discord.ext.commands import Bot, Cog
from git import Repo

from cdbot.constants import WELCOME_CHANNEL_ID, WELCOME_MESSAGE

path = os.path.dirname(os.path.abspath(__file__))
path = "/".join(path.split("/")[:-2])

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
        message, *_ = latest.message.partition("\n")
        link = f"{next(repo.remote().urls)}/commit/{latest}"
        date = latest.authored_datetime.strftime("**%x** at **%X**")
        self.bot.log.info(
            "CyberDiscovery bot is now logged in.\n"
            f"Latest commit: **[{message}]({link})**"
            f"\nAuthor: **{latest.author}** on {date}"
        )

    @Cog.listener()
    async def on_member_join(self, member):
        join_msg_channel = self.bot.get_channel(WELCOME_CHANNEL_ID)
        join_msg = await join_msg_channel.send(f"{member.mention}, {WELCOME_MESSAGE}")
        await join_msg.add_reaction('👋')
        WELCOME_EMBED = Embed(
                        color=Colour.blue(),
                        title="Welcome to the Cyber Discovery Server!",
                        url="https://cyberdiscoverycommunity.uk",
                        description="""Welcome to the Cyber Discovery Community server! Please take a moment to read 
                        the rules in <#409853512185282561> and click the link above to check out our website! Have a 
                        good one! 

                Whilst you do have access to most channels, there are hidden channels for school year groups. To get 
                access, run the corresponding commands in <#409860647170342919>: ```.rank Year 9 .rank Year 10 .rank 
                Year 11 .rank Year 12 .rank Year 13 .rank Technically Adults``` """
        )
        WELCOME_EMBED.set_author(name="Cyber Discovery")
        await member.send("-fsdsdf", embed=WELCOME_EMBED)

    @Cog.listener()
    async def on_member_remove(self, member):
        leave_msg_channel = self.bot.get_channel(WELCOME_CHANNEL_ID)
        await leave_msg_channel.send(f"**{member}** just left **Cyber Discovery**. Bye bye **{member}**...")

    @Cog.listener()
    async def on_member_ban(self, guild, user):
        ban_msg_channel = self.bot.get_channel(WELCOME_CHANNEL_ID)
        await ban_msg_channel.send(f"**{user}** was banned...")

    @Cog.listener()
    async def on_command_error(self, ctx, error):
        # Try provide some user feedback instead of logging all errors.

        if isinstance(error, commands.CommandNotFound):
            return  # No need to log unfound commands anywhere or return feedback

        if isinstance(error, commands.MissingRequiredArgument):
            # Missing arguments are likely human error so do not need logging
            parameter_name = error.param.name
            return await ctx.send(
                f"\N{NO ENTRY SIGN} Required argument {parameter_name} was missing"
            )
        elif isinstance(error, commands.CheckFailure):
            return await ctx.send(
                "\N{NO ENTRY SIGN} You do not have permission to use that command"
            )
        elif isinstance(error, commands.CommandOnCooldown):
            retry_after = round(error.retry_after)
            return await ctx.send(
                f"\N{HOURGLASS} Command is on cooldown, try again after {retry_after} seconds"
            )

        # All errors below this need reporting and so do not return

        if isinstance(error, commands.ArgumentParsingError):
            # Provide feedback & report error
            await ctx.send(
                "\N{NO ENTRY SIGN} An issue occurred while attempting to parse an argument"
            )
        elif isinstance(error, commands.BadArgument):
            await ctx.send("\N{NO ENTRY SIGN} Conversion of an argument failed")
        else:
            await ctx.send(
                "\N{NO ENTRY SIGN} An error occured during execution, the error has been reported."
            )

        extra_context = {
            "discord_info": {
                "Channel": ctx.channel.mention,
                "User": ctx.author.mention,
                "Command": ctx.message.content,
            }
        }

        if ctx.guild is not None:
            # We are NOT in a DM
            extra_context["discord_info"]["Message"] = (
                f"[{ctx.message.id}](https://discordapp.com/channels/"
                f"{ctx.guild.id}/{ctx.channel.id}/{ctx.message.id})"
            )
        else:
            extra_context["discord_info"]["Message"] = f"{ctx.message.id} (DM)"

        self.bot.log.exception(error, extra=extra_context)


def setup(bot):
    bot.add_cog(General(bot))
