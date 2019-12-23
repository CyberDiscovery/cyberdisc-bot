import os

from discord import Message
from discord.ext import commands
from discord.ext.commands import Bot, Cog
from git import Repo
import re

path = os.path.dirname(os.path.abspath(__file__))
path = '/'.join(path.split('/')[:-2])

repo = Repo(path)
latest = repo.commit()


class General(Cog):
    """
    General Purpose Commands
    """

    # General match strings
    match_strings = [
        # Events
        (r"^.*\bwhat\b.*\b((gci)|(google\b.*\bcode))\b.*$", "Google Code-in is a global, open source competition where students aged 13-17 contribute to open source projects and earn prizes. Find out more at https://codein.withgoogle.com/ or join the Discord server at 651156140796674098")
    ]

    def __init__(self, bot: Bot):
        self.bot = bot

        self.matches = [
            (re.compile(i[0], re.IGNORECASE), i[1]) for i in self.match_strings
        ]


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
        # Try provide some user feedback instead of logging all errors.

        if isinstance(error, commands.CommandNotFound):
            return  # No need to log unfound commands anywhere or return feedback

        if isinstance(error, commands.MissingRequiredArgument):
            # Missing arguments are likely human error so do not need logging
            parameter_name = error.param.name
            return await ctx.send(f"\N{NO ENTRY SIGN} Required argument {parameter_name} was missing")
        elif isinstance(error, commands.CheckFailure):
            return await ctx.send("\N{NO ENTRY SIGN} You do not have permission to use that command")
        elif isinstance(error, commands.CommandOnCooldown):
            retry_after = round(error.retry_after)
            return await ctx.send(f"\N{HOURGLASS} Command is on cooldown, try again after {retry_after} seconds")

        # All errors below this need reporting and so do not return

        if isinstance(error, commands.ArgumentParsingError):
            # Provide feedback & report error
            await ctx.send("\N{NO ENTRY SIGN} An issue occurred while attempting to parse an argument")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("\N{NO ENTRY SIGN} Conversion of an argument failed")
        else:
            await ctx.send("\N{NO ENTRY SIGN} An error occured during execution, the error has been reported.")

        extra_context = {
            "discord_info": {
                "Channel": ctx.channel.mention,
                "User": ctx.author.mention,
                "Command": ctx.message.content
            }
        }

        if ctx.guild is not None:
            # We are NOT in a DM
            extra_context["discord_info"]["Message"] = (
                f'[{ctx.message.id}](https://discordapp.com/channels/'
                f'{ctx.guild.id}/{ctx.channel.id}/{ctx.message.id})'
            )
        else:
            extra_context["discord_info"]["Message"] = f"{ctx.message.id} (DM)"

        self.bot.log.exception(error, extra=extra_context)

    @Cog.listener()
    async def on_message(self, message: Message):
        # Check the current command context
        ctx = await self.bot.get_context(message)
        # If message is a command, ignore regex responses.
        if ctx.valid:
            return

        # Check if the message matches any of the regexes
        for regex, response in self.matches:
            if regex.match(message.content):
                await message.channel.send(f"{message.author.mention}  |  {response}")
                break

def setup(bot):
    bot.add_cog(General(bot))
