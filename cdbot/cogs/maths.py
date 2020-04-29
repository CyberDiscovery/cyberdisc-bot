"""
Set of bot commands designed for Maths Challenges.
"""
from io import BytesIO

import aiohttp
import dateutil.parser
import httpx
from discord import Colour, Embed, File
from discord.ext import tasks
from discord.ext.commands import Bot, Cog, Context, command
from html2markdown import convert

from cdbot.constants import Maths as constants


async def get_challenges(
    client: httpx.AsyncClient, page_index: int = 0, page_size: int = 999
):
    """Get challenges, given the relevant parameters."""
    return (
        await client.post(
            constants.Challenges.URL,
            headers=dict(accessToken=constants.Challenges.TOKEN),
            json={
                "pageIndex": page_index,
                "pageSize": page_size,
                "orderBy": [{"desc": "answerDate"}],
                "where": [
                    {"field": "sys.versionStatus", "equalTo": "published"},
                    {"field": "sys.contentTypeId", "in": ["mathsQuiz"]},
                ],
                "fields": ["entryTitle", "category", "sys", "description", "answer"],
            },
        )
    ).json()["items"]


async def get_challenge(number: int) -> dict:
    async with httpx.AsyncClient() as client:
        challenge, *_ = await get_challenges(client, page_index=number - 1, page_size=1)

        question = (
            await client.post(
                constants.Challenges.URL,
                headers=dict(accessToken=constants.Challenges.TOKEN),
                json={
                    "pageIndex": 0,
                    "pageSize": 1,
                    "where": [
                        {"field": "sys.slug", "equalTo": challenge["sys"]["slug"]},
                        {"field": "sys.versionStatus", "equalTo": "published"},
                    ],
                },
            )
        ).json()["items"][0]["question"]

    asset = question[1]["value"]["asset"]["sys"] if len(question) > 1 else None

    return {
        "title": challenge["entryTitle"],
        "published": dateutil.parser.isoparse(
            challenge["sys"]["version"]["created"]
        ).strftime("%d/%m/%Y"),
        "category": challenge["category"][0]["entryTitle"],
        "challenge": convert(question[0]["value"]).replace("&nbsp;", "")[:-1],
        "image": (
            (
                "https://www.kingsmathsschool.com"
                "".join(
                    asset["uri"].rpartition("/")[:2] + (asset["properties"]["filename"],)
                )
            )
            if asset
            else ""
        ),
        "description": challenge["description"],
        "slug": challenge["sys"]["slug"],
    }


class Maths(Cog):
    """Maths-related commands."""

    def __init__(self, bot: Bot):
        self.bot = bot
        self.update_challenge.start()

    @tasks.loop(minutes=1)
    async def update_challenge(self):
        """Check the Kings site for the latest challenges."""
        print("Updating maths challenges...")
        latest_challenge = float("inf")
        latest_challenge = int(
            self.channel.topic.split("Nerds, the lot of you | Challenge ")[1].split(
                " "
            )[0][:-1]
        )
        async with httpx.AsyncClient() as client:
            challenges = await get_challenges(client)
        for number, challenge in enumerate(challenges[::-1], 1):
            title = challenge["entryTitle"]
            if number > latest_challenge:
                await self.challenge(self.channel, len(challenges) - number + 1)
                await self.channel.edit(topic=constants.Challenges.TOPIC.format(title))
        print("Maths challenges successfully updated.")

    @update_challenge.before_loop
    async def wait_until_ready(self):
        """Wait for bot to become ready."""
        await self.bot.wait_until_ready()
        self.channel = self.bot.get_channel(constants.Challenges.CHANNEL)

    @Cog.listener()
    async def on_message(self, message):
        """Check if the message contains inline LaTeX."""
        for expression in constants.LATEX_RE.findall(message.content):
            await self.latex(message.channel, expression)

    @command()
    async def challenge(self, ctx: Context, number: int = 1):
        """Show the provided challenge number."""
        challenge = await get_challenge(number)
        description = challenge["challenge"]
        if len(description) > 2048:
            description = description[:2045] + "..."
        embed = Embed(
            title=challenge["title"],
            colour=Colour(0xE5E242),
            url=f"https://www.kingsmathsschool.com/weekly-maths-challenge/{challenge['slug']}",
            description=description,
        )

        embed.set_image(url=challenge["image"])
        embed.set_thumbnail(
            url="https://pbs.twimg.com/profile_images/502115424121528320/hTQzj_-R.png"
        )
        embed.set_author(name="King's Maths School")
        embed.set_footer(
            text=f"Challenge Released: {challenge['published']} | Category: {challenge['category']}"
        )
        return await ctx.send(embed=embed)

    @command()
    async def latex(self, ctx: Context, expression: str):
        """Render a LaTeX expression"""
        options = {
            "auth": {"user": "guest", "password": "guest"},
            "latex": expression,
            "resolution": 900,
            "color": "969696",
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://latex2png.com/api/convert", json=options
            ) as response:
                result = await response.json()
            if result.get('url'):
                async with session.get("http://latex2png.com" + result["url"]) as response:
                    content = await response.content.read()
            else:
                return await ctx.send(
                    "\N{NO ENTRY SIGN} You provided invalid LaTeX."
                )
        await ctx.send(file=File(BytesIO(content), filename="result.png"))


def setup(bot):
    """
    Required boilerplate for adding functionality of cog to bot.
    """
    bot.add_cog(Maths(bot))
