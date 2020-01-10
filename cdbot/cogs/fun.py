"""
Set of bot commands designed for general leisure.
"""
import asyncio
import textwrap
from io import BytesIO
from random import randint
from string import ascii_lowercase
from typing import List
from urllib.parse import urlencode

import asyncpg
from PIL import Image, ImageDraw, ImageFont
from aiohttp import ClientSession
from cdbot.constants import (
    EMOJI_LETTERS,
    FAKE_ROLE_ID,
    PostgreSQL,
    QUOTES_BOT_ID,
    QUOTES_CHANNEL_ID,
    ROOT_ROLE_ID,
    STAFF_ROLE_ID,
    SUDO_ROLE_ID,
    WELCOME_BOT_ID,
)
from discord import Embed, File, HTTPException, Message, NotFound, embeds
from discord.ext.commands import (
    Bot, BucketType, Cog,
    Context, UserConverter, command, cooldown
)
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


class FormerUser(UserConverter):
    async def convert(self, ctx, argument):
        try:
            return await ctx.bot.fetch_user(argument)
        except (NotFound, HTTPException):
            return await super().convert(ctx, argument)


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
        self.quote_channel = None
        self.fake_staff_role = None

    async def migrate_quotes(self):
        """Create and initialise the `quotes` table with user quotes."""
        conn = await asyncpg.connect(
            host=PostgreSQL.PGHOST,
            port=PostgreSQL.PGPORT,
            user=PostgreSQL.PGUSER,
            password=PostgreSQL.PGPASSWORD,
            database=PostgreSQL.PGDATABASE,
        )
        await conn.execute(
            "CREATE TABLE IF NOT EXISTS quotes (quote_id bigint PRIMARY KEY, author_id bigint)"
        )
        quote_channel = self.bot.get_channel(QUOTES_CHANNEL_ID)
        async for quote in quote_channel.history(limit=None):
            await self.add_quote_to_db(conn, quote)
        await conn.close()

    @Cog.listener()
    async def on_ready(self):
        guild = self.bot.guilds[0]

        if self.staff_role is None:
            self.staff_role = guild.get_role(STAFF_ROLE_ID)

        if self.fake_staff_role is None:
            self.fake_staff_role = guild.get_role(FAKE_ROLE_ID)

        await self.migrate_quotes()

    @Cog.listener()
    async def on_message(self, message: Message):
        # If a new quote is added, add it to the database.
        if message.channel.id == QUOTES_CHANNEL_ID and (
            message.author.id == QUOTES_BOT_ID or message.mentions is not None
        ):
            conn = await asyncpg.connect(
                host=PostgreSQL.PGHOST,
                port=PostgreSQL.PGPORT,
                user=PostgreSQL.PGUSER,
                password=PostgreSQL.PGPASSWORD,
                database=PostgreSQL.PGDATABASE,
            )

            await self.add_quote_to_db(conn, message)
            await conn.close()
            print(f"Message #{message.id} added to database.")

        if self.fake_staff_role in message.role_mentions and not message.author.bot:
            # A user has requested to ping official staff
            sent = await message.channel.send(embed=self.ping_embed, delete_after=30)
            await sent.add_reaction("\N{THUMBS UP SIGN}")
            await sent.add_reaction("\N{THUMBS DOWN SIGN}")

            def check(reaction, user):
                """Check if the reaction was valid."""
                return all(
                    (user == message.author or user.top_role.id in [ROOT_ROLE_ID, SUDO_ROLE_ID],
                        str(reaction.emoji) in "\N{THUMBS UP SIGN}\N{THUMBS DOWN SIGN}")
                )

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

        # Flag checking.
        delete = False
        ie_flag = False
        if "-d" in args:
            delete = True
        if "-ie" in args:
            ie_flag = True

        # Creates a lmgtfy.com url for the given query.
        request_data = {"q": " ".join(arg for arg in args if not arg.startswith("-")), "ie": int(ie_flag)}
        url = "https://lmgtfy.com/?" + urlencode(request_data)

        await ctx.send(url)

        if delete:
            await ctx.message.delete()

    # Ratelimit to two usages per user every minute and 4 usages per minute per channel
    @command(aliases=["emojify"])
    @cooldown(1, 60, BucketType.user)
    @cooldown(4, 60, BucketType.channel)
    async def react(self, ctx, *, message: str):
        """
        Emojifies a given string, and reacts to a previous message
        with those emojis.
        """
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

    @command()
    async def quotes(self, ctx: Context, member: FormerUser = None):
        """
        Returns a random quotation from the #quotes channel.
        A user can be specified to return a random quotation from that user.
        """
        conn = await asyncpg.connect(
            host=PostgreSQL.PGHOST,
            port=PostgreSQL.PGPORT,
            user=PostgreSQL.PGUSER,
            password=PostgreSQL.PGPASSWORD,
            database=PostgreSQL.PGDATABASE,
        )
        quote_channel = self.bot.get_channel(QUOTES_CHANNEL_ID)

        if member is None:
            message_id = await conn.fetchval(
                "SELECT quote_id FROM quotes ORDER BY random() LIMIT 1;"
            )  # fetchval returns first value by default
        else:
            message_id = await conn.fetchval(
                "SELECT quote_id FROM quotes WHERE author_id=$1 ORDER BY random() LIMIT 1;", member.id
            )
            if message_id is None:
                await ctx.send("No quotes for that user.")
                return

        await conn.close()
        message = await quote_channel.fetch_message(message_id)
        embed = None
        content = message.clean_content
        attachment_urls = [attachment.url for attachment in message.attachments]

        if message.embeds:
            embed = message.embeds[0]
        elif len(attachment_urls) == 1:
            image_url = attachment_urls.pop(0)
            embed = Embed()
            embed.set_image(url=image_url)

        for url in attachment_urls:
            content += "\n" + url

        await ctx.send(content, embed=embed)

    @command()
    async def quotecount(self, ctx: Context, member: FormerUser = None):
        """
        Returns the number of quotes in the #quotes channel.
        A user can be specified to return the number of quotes from that user.
        """
        conn = await asyncpg.connect(
            host=PostgreSQL.PGHOST,
            port=PostgreSQL.PGPORT,
            user=PostgreSQL.PGUSER,
            password=PostgreSQL.PGPASSWORD,
            database=PostgreSQL.PGDATABASE,
        )
        total_quotes = await conn.fetchval('SELECT count(*) FROM quotes;')

        if member is None:
            await ctx.send(f"There are {total_quotes} quotes in the database")
        else:
            user_quotes = await conn.fetchval('SELECT count(*) FROM quotes WHERE author_id=$1;', member.id)
            await ctx.send(f"There are {user_quotes} quotes from {member} in the database \
({round((user_quotes / total_quotes) * 100, 2)}%)")

    @command()
    async def quoteboard(self, ctx: Context, page: int = 1):
        conn = await asyncpg.connect(
            host=PostgreSQL.PGHOST,
            port=PostgreSQL.PGPORT,
            user=PostgreSQL.PGUSER,
            password=PostgreSQL.PGPASSWORD,
            database=PostgreSQL.PGDATABASE,
        )

        page_count = ceil((await conn.fetchval("SELECT count(*) FROM quotes;")) / 10)

        if page > page_count:
            await ctx.send(":no_entry_sign: Invalid page number")
            return

        users = ""
        pos = 0

        for i in await conn.fetchall("SELECT author_id, COUNT(author_id) as quote_count FROM quotes GROUP BY author_id ORDER BY author_id LIMIT 10 OFFSET $1;", (page - 1) * 10):
            users += f"{page + pos}. {Bot.get_all_members(id=str(i["author_id"]).mention()} - {i["quote_count"]}\n"
            pos += 1

        embed = Embed(description="Quotes Leaderboard", colour=Colour(0xae444a))
        .set_footer(text=f"Page {int}/{page_count}")
        .add_field(value=users)
        .set_author(name="Cyber Discovery Community", icon_url=CYBERDISC_ICON_URL)

        await ctx.send(embed=embed)

    async def add_quote_to_db(self, conn: asyncpg.connection.Connection, quote: Message):
        """
        Adds a quote message ID to the database, and attempts to identify the author of the quote.
        """
        author_id = None
        if quote.author.id == QUOTES_BOT_ID:
            if not quote.embeds:
                return
            embed = quote.embeds[0]
            icon_url = embed.author.icon_url
            if type(icon_url) == embeds._EmptyEmbed or 'twimg' in icon_url:
                author_id = QUOTES_BOT_ID
            elif 'avatars' in icon_url:
                try:
                    author_id = int(icon_url.split('/')[-2])
                except ValueError:
                    author_id = 0
            else:
                author_info = embed.author.name.split("#")
                if len(author_info) == 1:
                    author_info.append("0000")
                author = get(
                    quote.guild.members,
                    name=author_info[0],
                    discriminator=author_info[1])
                author_id = author.id if author is not None else None
        else:
            author_id = quote.mentions[0].id if quote.mentions else None
        if author_id is not None:
            await conn.execute(
                "INSERT INTO quotes(quote_id, author_id) VALUES($1, $2) ON CONFLICT DO NOTHING;",
                quote.id,
                author_id,
            )
        else:
            await conn.execute("INSERT INTO quotes(quote_id) VALUES($1) ON CONFLICT DO NOTHING;", quote.id)
        print(f"Quote ID: {quote.id} has been added to the database.")

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
