from discord import Colour, Embed
from discord.ext import commands


class EmbeddedHelpCommand(commands.HelpCommand):
    def __init__(self):
        super().__init__(command_attrs={'help': 'Gives detailed information about a command.'})

    async def command_callback(self, ctx, *, command=None):
        if command is not None:
            for cog in ctx.bot.cogs:
                if str(command).casefold() == cog.casefold():
                    command = cog
                    break
        return await super().command_callback(ctx, command=command)

    async def send_bot_help(self, mapping):
        ctx = self.context
        embed = Embed(
            color=Colour.blue(),
            description="Type ``:help [command]`` for more info on a command.\n"
                        "You can also type "
                        "``:help [category]`` for more info on a category."
        )
        for cog in mapping.keys():
            if cog is not None:
                if cog.get_commands():
                    embed.add_field(name=cog.qualified_name,
                                    value=f"``:help {cog.qualified_name.lower()}``")

        dm = await ctx.author.send(embed=embed)
        if ctx.guild is not None:
            embed = Embed(
                description=f"[**Jump to DM**]({dm.jump_url})"
            )
            await ctx.send(f"{ctx.author.mention} help info sent to DMs", delete_after=10, embed=embed)
            await ctx.message.delete()

    async def send_cog_help(self, cog):
        ctx = self.context
        embed = Embed(
            color=Colour.blue(),
            title=cog.description,
            description="Type ``:help [command]`` for more info on a command.\n You can also type "
                        "``:help [category]`` for more info on a different category."
        )
        for command in cog.get_commands():
            if command.hidden is not True:
                embed.add_field(name=f"``:{command.name}``", value=command.help)

        dm = await ctx.author.send(embed=embed)
        if ctx.guild is not None:
            embed = Embed(
                description=f"[**Jump to DM**]({dm.jump_url})"
            )
            await ctx.send(f"{ctx.author.mention} help info sent to DMs", delete_after=10, embed=embed)
            await ctx.message.delete()

    async def send_command_help(self, command):
        ctx = self.context
        if command.hidden is not True:
            embed = Embed(
                color=Colour.blue(),
                title=f"``:{command.name}``",
                description=command.help
            )
            embed.add_field(name="Usage",
                            value=f"``:{command.name} {command.signature}``",
                            inline=False)
            if command.aliases:
                embed.add_field(name="Aliases",
                                value=", ".join(f'``:{alias}``' for alias in command.aliases),
                                inline=False)

            await ctx.send(embed=embed)


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot._original_help_command = bot.help_command
        bot.help_command = EmbeddedHelpCommand()
        bot.help_command.cog = self

    def cog_unload(self):
        self.bot.help_command = self.bot._original_help_command


async def setup(bot):
    await bot.add_cog(Help(bot))
