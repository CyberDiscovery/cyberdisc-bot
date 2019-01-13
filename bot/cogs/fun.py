"""
Set of bot commands designed for general leisure.
"""
import textwrap
from itertools import cycle
from random import choice, randint
from string import ascii_lowercase
from typing import AsyncGenerator
from urllib.parse import urlencode

from aiohttp import ClientSession
from discord import Embed, File, Member, Message
from discord.ext.commands import (
    Bot, Context, TextChannelConverter, command, has_any_role
)
from wand.drawing import Drawing
from wand.image import Image

from bot.constants import ADMIN_ROLES, EMOJI_LETTERS, FAKE_STAFF_ROLE_ID, QUOTES_BOT_ID, QUOTES_CHANNEL_ID,\
    SERVER_ID, STAFF_ROLE_ID


EMOJI_LETTERS = [
    cycle(letters) for letters in EMOJI_LETTERS
]

ascii_lowercase += ' '


async def _convert_emoji(message: str) -> AsyncGenerator[str, None]:
    """Convert a string to a list of emojis."""
    emoji_trans = list(map(iter, EMOJI_LETTERS))
    # Enumerate characters in the message
    for character in message:
        index = ascii_lowercase.find(character)
        if not index + 1:
            continue
        # Yield the next iteration of the letter
        try:
            emoji = next(emoji_trans[index])
        except StopIteration:
            yield None
        yield emoji


async def emojify(message: Message, string: str):
    """Convert a string to emojis, and add those emojis to a message."""
    async for emoji in _convert_emoji(string.lower()):
        if emoji is not None:
            await message.add_reaction(emoji)


class Fun:
    """
    Commands for fun!
    """

    def __init__(self, bot: Bot):
        self.bot = bot
        self.quote_channel = None
        self.staff_role = None

    async def on_message(self, message: Message):

        if message.channel.id == QUOTES_CHANNEL_ID and message.author.id == QUOTES_BOT_ID:
            author = message.embeds[0].title
            self.bot.quotes[author].append(message.id)

        """
        React based on the contents of a message.
        """
        # React if a message contains an @here or @everyone mention.
        if any(mention in message.content for mention in ("@here", "@everyone")):
            await message.add_reaction("🙁")
            await emojify(message, "who pinged")

        # React if message contains dabato.
        if "dabato" in message.content:
            await message.add_reaction("🤔")

        # React FBI OPEN UP if message contains trigger words.
        triggers = ["child", "fbi", "loli", "hentai", "illegal", "maltego"]
        if any(trigger in message.content.lower() for trigger in triggers):
            await emojify(message, "fbi open up")

        # React if message contains Kali.
        if "kali" in message.content.lower():
            await message.add_reaction("🚔")

        # React if message contains Duck.
        if "duck" in message.content.lower():
            await message.add_reaction("🦆")

        # React "NO" if message contains revive.
        if "revive" in message.content.lower():
            await emojify(message, "nou")

        # Ask if user has contacted support before letting them ping staff
        if self.staff_role is None:
            for y in self.bot.get_server(SERVER_ID).roles:
                if y.id == STAFF_ROLE_ID:
                    self.staff_role = y
                break

        if FAKE_STAFF_ROLE_ID in message.raw_role_mentions and message.author.id != self.bot.user.id:
            msg = await self.bot.send_message(message.channel,
                                              'Please try emailing support@joincyberdiscovery.com before'
                                              ' pinging staff! Continue with the ping anyway?')
            await self.bot.add_reaction(msg, '👍')
            await self.bot.add_reaction(msg, '👎')
            res = await self.bot.wait_for_reaction(['👍', '👎'], message=msg, user=message.author, timeout=100)
            if res is None:
                await self.bot.edit_message(msg, "You didn't react in time. Please try again.")
                await self.bot.remove_reaction(msg, '👍')
                await self.bot.remove_reaction(msg, '👎')
            elif res.reaction.emoji == '👍':
                await self.bot.edit_role(self.staff_role.server, self.staff_role, mentionable=True)
                await self.bot.send_message(message.channel,
                                            '<@&' + STAFF_ROLE_ID + '> mentioned by ' + message.author.mention)
                await self.bot.edit_role(self.staff_role.server, self.staff_role, mentionable=False)
            else:
                await self.bot.edit_message(msg, "Email support@joincyberdiscovery.com for support!")

    @command()
    async def lmgtfy(self, ctx: Context, *args: str):
        """
        Returns a LMGTFY URL for a given user argument.
        """

        # Flag checking.
        delete = False
        ie_flag = False
        if "-d" in args:
            delete = True
        if "-ie" in args:
            ie_flag = True

        # Creates a lmgtfy.com url for the given query.
        request_data = {
            "q": " ".join(arg for arg in args if not arg.startswith("-")),
            "ie": int(ie_flag)
        }
        url = "https://lmgtfy.com/?" + urlencode(request_data)

        await ctx.send(url)

        if delete:
            await ctx.message.delete()

    @command(aliases=['emojify'])
    async def react(self, ctx, *, message: str):
        """
        Emojifies a given string, and reacts to a previous message
        with those emojis.
        """
        print(repr(message))
        limit, _, output = message.partition(' ')
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
        comic.set_author(
            name="xkcd",
            url="https://xkcd.com/",
            icon_url="https://xkcd.com/s/0b7742.png")
        comic.add_field(name="Number:", value=number)
        comic.add_field(name="Date:", value=date)
        comic.add_field(
            name="Explanation:",
            value=f"https://explainxkcd.com/{number}")

        await ctx.send(embed=comic)

    @command()
    async def quotes(self, ctx: Context, member: Member = None):
        """
        Returns a random quotation from the #quotes channel.
        A user can be specified to return a random quotation from that user.
        """
        quote_channel = self.bot.get_channel(QUOTES_CHANNEL_ID)
        quotes = self.bot.quotes

        if member is None:
            message_id = choice(quotes[choice(list(quotes.keys()))])
        else:
            user_quotes = quotes[f'{member.name}#{member.discriminator}']
            if not user_quotes:
                await ctx.send("No quotes from that user.")
                return
            message_id = choice(user_quotes)

        message = await quote_channel.get_message(message_id)
        await ctx.send(embed=message.embeds[0])

    @command()
    @has_any_role(*ADMIN_ROLES)
    async def set_quote_channel(self, ctx: Context, channel: TextChannelConverter):
        """
        Sets the quotes channel.
        """
        self.quote_channel = channel
        await ctx.send("Quotes channel successfully set.")

    async def create_text_image(self, ctx: Context, person: str, text: str):
        """
        Creates an image of a given person with the specified text.
        """
        lines = textwrap.wrap(text, 15)
        draw = Drawing()
        image = Image(filename=f"bot/resources/{person}SaysBlank.png")
        draw.font = "bot/resources/Dosis-SemiBold.ttf"
        draw.text_alignment = "center"
        draw.font_size = 34
        offset = 45 - 10 * len(lines)
        for line in lines:
            draw.text(image.width // 5 + 20, image.height // 5 + offset, line)
            offset += 35
        draw(image)
        image.save(filename=f"bot/resources/{person}Says.png")
        await ctx.send(file=File(f"bot/resources/{person}Says.png"))

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


def setup(bot):
    """
    Required boilerplate for adding functionality of cog to bot.
    """
    bot.add_cog(Fun(bot))
