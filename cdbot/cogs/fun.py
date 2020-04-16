"""
Set of bot commands designed for general leisure.
"""
import asyncio
import textwrap
from io import BytesIO
from math import ceil
from random import randint
from string import ascii_lowercase
from typing import List
from urllib.parse import urlencode

from PIL import Image, ImageDraw, ImageFont
from aiohttp import ClientSession
from cdbot.constants import (
    CYBERDISC_ICON_URL,
    EMOJI_LETTERS,
    FAKE_ROLE_ID,
    QUOTES_CHANNEL_ID,
    ROOT_ROLE_ID,
    SERVER_ID,
    STAFF_ROLE_ID,
    SUDO_ROLE_ID,
    WELCOME_BOT_ID,
)
from discord import Embed, File, Message
from discord.ext.commands import Bot, BucketType, Cog, Context, command, cooldown
from discord.utils import get

ascii_lowercase += " !?$()"

REACT_TRIGGERS = {
    "kali": "\N{ONCOMING POLICE CAR}",
    "duck": "\N{DUCK}"
}


def convert_emoji(message: str) -> List[str]:
    """Convert a string to a list of emojis."""
    emoji_trans = list(map(iter, EMOJI_LETTERS))
    # Enumerate characters in the message

    emojified = []

    for character in message:
        index = ascii_lowercase.find(character)
        if index == -1:
            continue
        # Yield the next iteration of the letter
        try:
            emojified.append(next(emoji_trans[index]))
        except StopIteration:
            continue

    return emojified


async def emojify(message: Message, string: str):
    """Convert a string to emojis, and add those emojis to a message."""
    for emoji in convert_emoji(string.lower()):
        if emoji is not None:
            await message.add_reaction(emoji)


class Fun(Cog):
    """
    Commands for fun!
    """

    # Embed sent when users try to ping staff
    ping_embed = (
        Embed(
            colour=0xFF0000, description="⚠ **Please make sure you have taken the following into account:** "
        )
        .set_footer(
            text="To continue with the ping, react \N{THUMBS UP SIGN}, To delete this message and move on,"
            " react \N{THUMBS DOWN SIGN}"
        )
        .add_field(
            name="Cyber Discovery staff will not provide help for challenges.",
            value="If you're looking for help, feel free to ask questions in one of our topical channels.",
        )
        .add_field(
            name="Make sure you have emailed support before pinging here.",
            value="`support@joincyberdiscovery.com` are available to answer any and all questions!",
        )
    )

    def __init__(self, bot: Bot):
        self.bot = bot
        self.staff_role = None
        self.fake_staff_role = None


    @Cog.listener()
    async def on_ready(self):
        guild = get(self.bot.guilds, id=SERVER_ID)

        if self.staff_role is None:
            self.staff_role = guild.get_role(STAFF_ROLE_ID)

        if self.fake_staff_role is None:
            self.fake_staff_role = guild.get_role(FAKE_ROLE_ID)

    @cooldown(1, 60, BucketType.user)
    @cooldown(4, 60, BucketType.channel)
    @cooldown(6, 3600, BucketType.guild)
    @Cog.listener()
    async def on_message(self, message: Message):
        if self.fake_staff_role in message.role_mentions and not message.author.bot:
            # A user has requested to ping official staff
            sent = await message.channel.send(embed=self.ping_embed, delete_after=30)
            await sent.add_reaction("\N{THUMBS UP SIGN}")
            await sent.add_reaction("\N{THUMBS DOWN SIGN}")

            def check(reaction, user):
                """Check if the reaction was valid."""
                return all((
                    user == message.author or user.top_role.id in [ROOT_ROLE_ID, SUDO_ROLE_ID],
                    str(reaction.emoji) in "\N{THUMBS UP SIGN}\N{THUMBS DOWN SIGN}"
                ))

            try:
                # Get the user's reaction
                reaction, _ = await self.bot.wait_for("reaction_add", timeout=30, check=check)

            except asyncio.TimeoutError:
                pass

            else:
                if str(reaction) == "\N{THUMBS UP SIGN}":
                    # The user wants to continue with the ping
                    await self.staff_role.edit(mentionable=True)
                    staff_ping = Embed(
                        title="This user has requested an official staff ping!",
                        colour=0xFF0000,
                        description=message.content,
                    ).set_author(
                        name=f"{message.author.name}#{message.author.discriminator}",
                        icon_url=message.author.avatar_url,
                    )
                    # Send the embed with the user's content
                    await message.channel.send(self.staff_role.mention, embed=staff_ping)
                    await self.staff_role.edit(mentionable=False)
                    # Delete the original message
                    await message.delete()

            finally:
                await sent.delete()

        ctx = await self.bot.get_context(message)

        if ctx.valid:
            # Don't react to valid commands
            return

        for word in message.content.lower().split():
            # Check if the message contains a trigger
            if word in REACT_TRIGGERS:
                to_react = REACT_TRIGGERS[word]

                if len(to_react) > 1:  # We have a string to react with
                    await emojify(message, to_react)
                else:
                    await message.add_reaction(to_react)

                return  # Only one auto-reaction per message

        # Adds waving emoji when a new user joins.
        if "Welcome to the Cyber Discovery" in message.content and message.author.id == WELCOME_BOT_ID:
            await message.add_reaction("\N{WAVING HAND SIGN}")

    @command()
    async def lmgtfy(self, ctx: Context, *args: str):
        """
        Returns a LMGTFY URL for a given user argument.
        """
        # Creates a lmgtfy.com url for the given query.
        request_data = {
            "q": " ".join(arg for arg in args if not arg.startswith("-")),
            "ie": int("-ie" in args)
        }
        url = "https://lmgtfy.com/?" + urlencode(request_data)

        await ctx.send(url)

        if "-d" in args:
            await ctx.message.delete()

    # Ratelimit to one use per user every minute and 4 usages per minute per channel
    @command(aliases=["emojify"])
    @cooldown(1, 60, BucketType.user)
    @cooldown(4, 60, BucketType.channel)
    async def react(self, ctx, *, message: str):
        """
        Emojifies a given string, and reacts to a previous message
        with those emojis.
        """
        if ctx.channel.id == QUOTES_CHANNEL_ID:
            await ctx.send("This command is disabled in this channel!", delete_after=10)
            return
        limit, _, output = message.partition(" ")
        if limit.isdigit():
            limit = int(limit)
        else:
            output = message
            limit = 2
        async for target in ctx.channel.history(limit=limit):
            pass
        await emojify(target, output)

    @command()
    async def xkcd(self, ctx: Context, number: str = None):
        """
        Fetches xkcd comics.
        If number is left blank, automatically fetches the latest comic.
        If number is set to '?', a random comic is fetched.
        """

        # Creates endpoint URI
        if number is None or number == "?":
            endpoint = "https://xkcd.com/info.0.json"
        else:
            endpoint = f"https://xkcd.com/{number}/info.0.json"

        # Fetches JSON data from endpoint
        async with ClientSession() as session:
            async with session.get(endpoint) as response:
                data = await response.json()

        # Updates comic number
        if number == "?":
            number = randint(1, int(data["num"]))  # noqa: B311
            endpoint = f"https://xkcd.com/{number}/info.0.json"
            async with ClientSession() as session:
                async with session.get(endpoint) as response:
                    data = await response.json()
        else:
            number = data["num"]

        # Creates date object (Sorry, but I'm too tired to use datetime.)
        date = f"{data['day']}/{data['month']}/{data['year']}"

        # Creates Rich Embed, populates it with JSON data and sends it.
        comic = Embed()
        comic.title = data["safe_title"]
        comic.set_footer(text=data["alt"])
        comic.set_image(url=data["img"])
        comic.url = f"https://xkcd.com/{number}"
        comic.set_author(name="xkcd", url="https://xkcd.com/", icon_url="https://xkcd.com/s/0b7742.png")
        comic.add_field(name="Number:", value=number)
        comic.add_field(name="Date:", value=date)
        comic.add_field(name="Explanation:", value=f"https://explainxkcd.com/{number}")

        await ctx.send(embed=comic)

    async def create_text_image(self, ctx: Context, person: str, text: str):
        """
        Creates an image of a given person with the specified text.
        """
        if len(text) > 100:
            return await ctx.send(":no_entry_sign: Your text must be shorter than 100 characters.")
        drawing_text = textwrap.fill(text, 20)
        font = ImageFont.truetype("cdbot/resources/Dosis-SemiBold.ttf", 150)

        text_layer = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
        text_layer_drawing = ImageDraw.Draw(text_layer)
        text_layer_drawing.text((0, 0), drawing_text, fill=(0, 0, 0), align="center", font=font)

        cropped_text_layer = text_layer.crop(text_layer.getbbox())
        cropped_text_layer.thumbnail((170, 110))

        image = Image.open(f"cdbot/resources/{person}SaysBlank.png")

        x = int((image.width / 5 + 20) - (cropped_text_layer.width / 2))
        y = int((image.height / 5 + 50 / 2) - (cropped_text_layer.height / 2))

        image.paste(cropped_text_layer, (x, y), cropped_text_layer)
        image_bytes = BytesIO()
        image.save(image_bytes, format="PNG")
        image_bytes.seek(0)
        await ctx.send(file=File(image_bytes, filename=f"{person}.png"))

    @command()
    async def agentj(self, ctx: Context, *, text: str):
        """
        Creates an image of Agent J with the specified text.
        """
        await self.create_text_image(ctx, "AgentJ", text)

    @command()
    async def jibhat(self, ctx: Context, *, text: str):
        """
        Creates an image of Jibhat with the specified text.
        """
        await self.create_text_image(ctx, "Jibhat", text)

    @command()
    async def agentq(self, ctx: Context, *, text: str):
        """
        Creates an image of Agent Q with the specified text.
        """
        await self.create_text_image(ctx, "AgentQ", text)

    @command()
    async def angryj(self, ctx: Context, *, text: str):
        """
        Creates an image of Angry Agent J with the specified text.
        """
        await self.create_text_image(ctx, "AngryJ", text)

    @command()
    async def angrylyne(self, ctx: Context, *, text: str):
        """
        Creates an image of Angry James Lyne with the specified text.
        """
        await self.create_text_image(ctx, "AngryLyne", text)


def setup(bot):
    """
    Required boilerplate for adding functionality of cog to bot.
    """
    bot.add_cog(Fun(bot))
