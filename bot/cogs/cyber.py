from discord.ext.commands import Bot, Context, command
from discord import Embed

from bot.constants import CYBERDISC_ICON_URL

class Cyber:
    """
    Cyber Discovery/Security related commands.
    """

    def __init__(self, bot: Bot):
        self.bot = Bot

    @command(aliases=["l", "lc"])
    async def level(self, ctx: Context, level_num: int, challenge_num: int):
        with open('headquarters.txt','r') as f:
            game_docs = [level.split(":::\n") for level in f.read().split(";;;;;;\n")]
        
        if level_num not in range(len(game_docs)):
            await ctx.send("Invalid level number!")
            
        elif challenge_num not in range(len(game_docs[level_num])):
            await ctx.send("Invalid challenge number!")
            
        else:
            challenge_raw = game_docs[level_num][challenge_num].splitlines()
            challenge_title = challenge_raw.pop(0)
            challenge_tip = challenge_raw.pop(-1)
            challenge_text = "\n".join(challenge_raw)
            embed = Embed(
                title=(f"Level {level_num} Challenge {challenge_num} - {challenge_title}"),
                description=challenge_text,
                colour=0x4262f4
            )
            embed.set_author(
                name="Cyber Discovery",
                icon_url=CYBERDISC_ICON_URL
            )
            embed.set_footer(text=challenge_tip)

            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Cyber(bot))
