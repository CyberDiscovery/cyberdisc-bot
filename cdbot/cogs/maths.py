"""
Set of bot commands designed for Maths Challenges.
"""
import asyncio
from io import BytesIO

import aiohttp
from PIL import Image
from discord import Colour, Embed, File, Member, Message, Reaction
from discord.ext.commands import Bot, Cog, Context, command

from cdbot.constants import Maths as constants


class Maths(Cog):
    """Maths-related commands."""

    def __init__(self, bot: Bot):
        self.bot = bot

    @Cog.listener()
    async def on_message(self, message):
        """Check if the message contains inline LaTeX."""
        if constants.LATEX_RE.findall(message.content):
            await self.latex_render(
                message.channel, message.channel.id, message, message.content
            )

    @command()
    async def latex(self, ctx: Context, *, expression: str):
        """
        Render a LaTeX expression with https://quicklatex.com/
        """
        await self.latex_render(ctx, ctx.channel.id, ctx.message, expression)

    async def latex_render(
        self, ctx: Context, channel: int, message: Message, expression: str
    ):

        if channel in constants.BLOCKED_CHANNELS:
            return await ctx.send(
                "\N{NO ENTRY SIGN} You cannot use this command in this channel!",
                delete_after=10,
            )

        # Code and regexes taken from https://quicklatex.com/js/quicklatex.js
        # aiohttp seems to URL-encode things in a way quicklatex doesn't like

        if expression.startswith("...latex") or expression.startswith(":latex"):
            return

        formula = expression.replace("%", "%25").replace("&", "%26")

        preamble = constants.LATEX_PREAMBLE.replace("%", "%25").replace("&", "%26")

        body = "formula=" + formula
        body = body + "$$$$&fsize=50px"
        body = body + "&fcolor=ffffff"
        body = body + "&mode=0"
        body = body + "&out=1"
        body = body + "&errors=1"
        body = body + "&preamble=" + preamble

        border_width = 20

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://www.quicklatex.com/latex3.f", data=body
            ) as response:
                result = await response.text()
            m = constants.LATEX_RESPONSE_RE.match(result)
            if not m:
                return
            status, url, valign, imgw, imgh, errmsg = m.groups()
            if status == "0":
                async with session.get(url) as response:
                    content = await response.content.read()
                img = Image.open(BytesIO(content))
                alpha = img.convert("RGBA").split()[-1]
                image = Image.new(
                    "RGB",
                    (img.size[0] + 2 * border_width, img.size[1] + 2 * border_width),
                    "#36393F",
                )
                image.paste(img, (border_width, border_width), mask=alpha)
                image_bytes = BytesIO()
                image.save(image_bytes, format="PNG")
                image_bytes.seek(0)

                # send the resulting image and add a bin reaction
                rendered_message = await ctx.send(
                    file=File(image_bytes, filename="result.png")
                )
                await rendered_message.add_reaction("\N{WASTEBASKET}")

                # checks if the person who reacted was the original latex author and that they reacted with a bin
                def should_delete(reaction: Reaction, user: Member):
                    return all(
                        (
                            message.author == user,
                            reaction.emoji == "\N{WASTEBASKET}",
                            reaction.message.id == rendered_message.id,
                        )
                    )

                # if the latex author reacts with a bin within 30 secs of sending, delete the rendered image
                # otherwise delete the bin reaction
                try:
                    await self.bot.wait_for(
                        "reaction_add", check=should_delete, timeout=30
                    )
                except asyncio.TimeoutError:
                    await rendered_message.remove_reaction(
                        "\N{WASTEBASKET}", self.bot.user
                    )
                else:
                    await rendered_message.delete()

            else:
                embed = Embed(
                    title="\N{WARNING SIGN} **LaTeX Compile Error** \N{WARNING SIGN}",
                    colour=Colour(0xB33A3A),
                    description=errmsg.replace("@", ""),
                )
                return await ctx.send(embed=embed, delete_after=30)


async def setup(bot):
    """
    Required boilerplate for adding functionality of cog to bot.
    """
    await bot.add_cog(Maths(bot))
