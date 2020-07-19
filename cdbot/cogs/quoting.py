from math import ceil
from typing import Callable, List, Union

from discord import Colour, Embed, HTTPException, Member, Message, NotFound, RawReactionActionEvent, TextChannel, User
from discord.ext import commands
from discord.ext.commands import ArgumentParsingError, Bot, CheckFailure, Cog, UserConverter
from motor.motor_asyncio import AsyncIOMotorClient

from cdbot.constants import (
    CYBERDISC_ICON_URL, LOGGING_CHANNEL_ID, MongoDB, QUOTES_CHANNEL_ID, QUOTES_DELETION_QUOTA, QUOTE_CZAR_ID, SERVER_ID
)

JUMP_URL_FORMAT = "https://discord.com/channels/{0}/{1}/{2}"


def user_can_quote() -> Callable:
    async def predicate(ctx: commands.Context) -> bool:
        czar_role = ctx.guild.get_role(QUOTE_CZAR_ID)
        return czar_role in ctx.author.roles or ctx.author.guild_permissions.administrator
    return commands.check(predicate)


class FormerUser(UserConverter):
    async def convert(self, ctx, argument):
        try:
            return await ctx.bot.fetch_user(argument)
        except (NotFound, HTTPException):
            return await super().convert(ctx, argument)


class QuoteCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        self.guild = self.bot.get_guild(SERVER_ID)
        self.quote_channel = self.bot.get_channel(QUOTES_CHANNEL_ID)
        self.logs_channel = self.bot.get_channel(LOGGING_CHANNEL_ID)
        self.database = AsyncIOMotorClient(
            host=MongoDB.MONGOHOST,
            port=MongoDB.MONGOPORT,
            username=MongoDB.MONGOUSER,
            password=MongoDB.MONGOPASSWORD,
        )[MongoDB.MONGODATABASE]["quotes"]

    @Cog.listener()
    async def on_raw_reaction_add(self, raw_reaction: RawReactionActionEvent):
        thumbs_down = "\N{THUMBS DOWN SIGN}"
        if str(raw_reaction.emoji) == thumbs_down and raw_reaction.channel_id == QUOTES_CHANNEL_ID:
            # Checking for downvote emoji for quote removal.
            message = await self.quote_channel.fetch_message(raw_reaction.message_id)
            reaction = [react for react in message.reactions if str(react.emoji) == thumbs_down][0]
            if reaction.count > QUOTES_DELETION_QUOTA:
                # Check that the count is greater than the required amount.
                await self.database.delete_one({"_id": message.id})  # Delete the quote
                mentions = ", ".join(user.mention async for user in reaction.users())
                for quote_embed in reaction.message.embeds:
                    embed = Embed(
                        color=Colour.blue(),
                        title="Quote Deleted",
                        description=quote_embed.description
                    )
                    embed.add_field(name="Deleted By", value=mentions)
                    embed.set_author(name=quote_embed.author.name, icon_url=quote_embed.author.icon_url)
                await reaction.message.delete()
                await self.logs_channel.send(embed=embed)  # Send an embed to log quote deletion.

    async def get_member_by_id(self, member_id: int) -> Union[Member, User, None]:
        if self.guild.get_member(member_id) is not None:
            return self.guild.get_member(member_id)
        try:
            user = await self.bot.fetch_user(member_id)
            return user
        except NotFound:
            return None

    def quote_dict(self, quoted: Message, message: Message) -> dict:
        quote = dict(
            content_id=quoted.id,
            channel=quoted.channel.id,
            content=quoted.content,
            author=dict(id=quoted.author.id, name=str(quoted.author), avatar=str(quoted.author.avatar_url_as(size=32))),
            quoted_at=message.created_at,
            quoted_by=message.author.id,
        )
        if len(quoted.embeds) > 0:
            quote["embed"] = quoted.embeds[0].to_dict()
        if len(quoted.attachments) > 0:
            quote["image"] = quoted.attachments[0].url
        return quote

    async def quote_embed(self, quote: dict) -> Embed:
        if quote.get("embed", None):
            return Embed.from_dict(quote["embed"])
        channel = self.bot.get_channel(quote["channel"])
        quoted = await self.get_member_by_id(quote["author"]["id"])
        quoter = await self.get_member_by_id(quote["quoted_by"])
        embed = Embed()
        if quoted:
            embed = embed.set_author(name=str(quoted), icon_url=str(quoted.avatar_url_as(size=32)))
        else:
            embed = embed.set_author(name=quote["author"]["name"], icon_url=quote["author"]["avatar"])
        footer_text = "Quoted by "
        if quoter:
            footer_text += str(quoter)
        else:
            footer_text += f"ID: {quote['quoted_by']}"
        footer_text += " in channel "
        if channel:
            footer_text += "#" + str(channel)
        else:
            footer_text += f"ID: {quote['channel']}"
        if quoter:
            embed = embed.set_footer(text=footer_text, icon_url=str(quoter.avatar_url_as(size=32)))
        else:
            embed = embed.set_footer(text=footer_text)
        if "```" in quote["content"]:
            embed.description = quote["content"] + "\n"
        elif len(quote["content"]) > 0:
            embed.description = f"```{quote['content']}```\n"
        else:
            embed.description = ""
        embed.description += f"[Jump to original]({JUMP_URL_FORMAT.format(SERVER_ID, channel.id, quote['content_id'])})"
        embed.timestamp = quote["quoted_at"]
        if quote.get("image", None):
            embed.set_image(url=quote["image"])
        return embed

    async def range_quote(self, channel: TextChannel, after: Message, before: Message) -> List[Message]:
        messages = await channel.history(after=after, before=before).flatten()
        return [after, *messages, before]

    def multi_quote_dict(self, messages: List[Message], message: Message) -> dict:
        multi_quote = dict(
            content_id=messages[0].id,
            channel=messages[0].channel.id,
            quoted_at=message.created_at,
            quoted_by=message.author.id,
            messages=[],
        )
        for line in messages:
            data = dict(original=line.id, content=line.content, author=dict(id=line.author.id, name=str(line.author)))
            if len(line.embeds) > 0:
                data["embed"] = line.embeds[0].to_dict()
            multi_quote["messages"].append(data)
        return multi_quote

    async def multi_quote_embed(self, multi_quote: dict) -> Embed:
        embeds = [message.get("embed", None) for message in multi_quote["messages"]]
        if any(embeds):
            return list(filter(lambda x: x is not None, embeds))
        embed = Embed().set_author(name=str(self.bot.user), icon_url=self.bot.user.avatar_url)
        quoter = await self.get_member_by_id(multi_quote["quoted_by"])
        channel = self.bot.get_channel(multi_quote["channel"])
        jump_to_link = f"[Jump to content]({JUMP_URL_FORMAT.format(SERVER_ID, channel.id, multi_quote['content_id'])})"
        footer_text = "Quoted by "
        if quoter:
            footer_text += str(quoter)
        else:
            footer_text += f"ID: {multi_quote['quoted_by']}"
        footer_text += " in channel "
        if channel:
            footer_text += "#" + str(channel)
        else:
            footer_text += f"ID: {multi_quote['channel']}"
        if quoter:
            embed = embed.set_footer(text=footer_text, icon_url=str(quoter.avatar_url_as(size=32)))
        else:
            embed = embed.set_footer(text=footer_text)
        embed.timestamp = multi_quote["quoted_at"]
        messages = []
        for message in multi_quote["messages"]:
            original = await self.get_member_by_id(message["author"]["id"])
            messages.append(
                dict(content=message["content"], user=str(original) if not None else message["author"]["name"])
            )
        lines = []
        for message in messages:
            line_str = message["user"] + ": "
            if message["content"].startswith("```"):
                line_str += "\n"
            line_str += message["content"]
            if len(line_str) > 200:
                if line_str.endswith("```"):
                    line_str = line_str[:200] + "...```"
                else:
                    line_str = line_str[:200] + "..."
            lines.append(line_str)
        embed.description = "```" + "\n".join(lines) + "```\n" + jump_to_link
        return embed

    async def generate_single_quote(self, quoted: Message, original: Message):
        quote = self.quote_dict(quoted, original)
        embed = await self.quote_embed(quote)
        return embed, quote

    async def generate_multi_quote(
        self, channel: TextChannel, from_message: Message, to_message: Message, message: Message
    ):
        messages = await self.range_quote(channel, from_message, to_message)
        if len("".join(message.content for message in messages)) > 2000:
            raise ArgumentParsingError
        quote = self.multi_quote_dict(messages, message)
        embeds = await self.multi_quote_embed(quote)
        return embeds, quote

    async def save_quote(self, embed: Embed, data: dict):
        quote = await self.quote_channel.send(embed=embed)
        await quote.add_reaction("\N{THUMBS DOWN SIGN}")
        data["_id"] = quote.id
        res = await self.database.insert_one(data)
        print(res)

    @commands.group(invoke_without_command=True)
    async def quote(self, ctx: commands.Context, message: Message):
        """
        Quote a single message.
        """
        if ctx.channel.id == QUOTES_CHANNEL_ID:
            return await ctx.invoke(self.quote_save, message)
        embed, _ = await self.generate_single_quote(message, ctx.message)
        return await ctx.send(embed=embed)

    @quote.group(name="from", invoke_without_command=True)
    async def quote_from(self, ctx: commands.Context, channel: TextChannel, message: int):
        """
        Quote a message from another channel.
        """
        if not channel.permissions_for(ctx.author).read_messages:
            raise CheckFailure()
        message = await channel.fetch_message(message)
        if ctx.channel.id == QUOTES_CHANNEL_ID:
            return await ctx.invoke(self.quote_save, message)
        return await ctx.invoke(self.quote, message)

    @quote.group(name="range", invoke_without_command=True)
    async def quote_range(self, ctx: commands.Context, from_message: Message, to_message: Message):
        """
        Quote a range of messages from the current channel.
        """
        if ctx.channel.id == QUOTES_CHANNEL_ID:
            return ctx.invoke(self.quote_save_range, from_message, to_message)
        embed, _ = await self.generate_multi_quote(ctx.channel, from_message, to_message, ctx.message)
        return await ctx.send(embed=embed)

    @quote_range.command(name="from")
    async def quote_range_from(self, ctx: commands.Context, channel: TextChannel, from_message: int, to_message: int):
        """
        Quote a range of messages from another channel.
        """
        if not channel.permissions_for(ctx.author).read_messages:
            raise CheckFailure()
        if ctx.channel.id == QUOTES_CHANNEL_ID:
            return await ctx.invoke(self.quote_save_range_from, channel, from_message, to_message)
        from_message = await channel.fetch_message(from_message)
        to_message = await channel.fetch_message(to_message)
        embed, _ = await self.generate_multi_quote(channel, from_message, to_message, ctx.message)
        return await ctx.send(embed=embed)

    @quote_from.command(name="range")
    async def quote_from_range(self, ctx: commands.Context, channel: TextChannel, from_message: int, to_message: int):
        return await ctx.invoke(self.quote_range_from, channel, from_message, to_message)

    @quote.group(name="save", invoke_without_command=True)
    @user_can_quote()
    async def quote_save(self, ctx: commands.Context, message: Message):
        embed, data = await self.generate_single_quote(message, ctx.message)
        await ctx.message.delete()
        await self.save_quote(embed, data)
        return await ctx.send(content="Saved quote to database", embed=embed, delete_after=5.0)

    @quote_save.group("from", invoke_without_command=True)
    @user_can_quote()
    async def quote_save_from(self, ctx: commands.Context, channel: TextChannel, message: int):
        if not channel.permissions_for(ctx.author).read_messages:
            raise CheckFailure()
        message = await channel.fetch_message(message)
        embed, data = await self.generate_single_quote(message, ctx.message)
        await ctx.message.delete()
        await self.save_quote(embed, data)
        return await ctx.send(content="Saved quote to database", embed=embed, delete_after=5.0)

    @quote_save.group("range", invoke_without_command=True)
    @user_can_quote()
    async def quote_save_range(self, ctx: commands.Context, from_message: Message, to_message: Message):
        embed, data = await self.generate_multi_quote(ctx.channel, from_message, to_message, ctx.message)
        await ctx.message.delete()
        await self.save_quote(embed, data)
        return await ctx.send(content="Saved quote to database", embed=embed, delete_after=5.0)

    @quote_save_range.command("from")
    @user_can_quote()
    async def quote_save_range_from(
        self, ctx: commands.Context, channel: TextChannel, from_message: int, to_message: int
    ):
        if not channel.permissions_for(ctx.author).read_messages:
            raise CheckFailure()
        from_message = await channel.fetch_message(from_message)
        to_message = await channel.fetch_message(to_message)
        embed, data = await self.generate_multi_quote(channel, from_message, to_message, ctx.message)
        await ctx.message.delete()
        await self.save_quote(embed, data)
        return await ctx.send(content="Saved quote to database", embed=embed, delete_after=5.0)

    @quote_save_from.command("range")
    @user_can_quote()
    async def quote_save_from_range(
        self, ctx: commands.Context, channel: TextChannel, from_message: int, to_message: int
    ):
        return await ctx.invoke(self.quote_save_range_from, channel, from_message, to_message)

    @commands.command()
    async def quotes(self, ctx: commands.Context, member: FormerUser = None):
        """
        Returns a random quotation from the #quotes channel.
        A user can be specified to return a random quotation from that user.
        """
        pipeline = []
        if member:
            pipeline.append(
                {
                    "$match": {
                        "$or": [
                            {
                                "author.id": member.id
                            },
                            {
                                "messages.author.id": member.id
                            }
                        ]
                    }
                }
            )
        pipeline.append({"$sample": {"size": 1}})
        async for doc in self.database.aggregate(pipeline):
            quote = await self.quote_channel.fetch_message(doc["_id"])
            return await ctx.send(embed=quote.embeds[0])
        return await ctx.send("No quotes found.")

    @commands.command()
    async def quotecount(self, ctx: commands.Context, member: FormerUser = None):
        """
        Returns the number of quotes in the #quotes channel.
        A user can be specified to return the number of quotes from that user.
        """
        total_quotes = await self.database.count_documents({"author": {"$exists": True}})
        if not member:
            return await ctx.send(f"There are {total_quotes} quotes in the database")
        user_quotes = await self.database.count_documents({"author.id": member.id})
        return await ctx.send(
            f"There are {user_quotes} quotes from {member} in the database "
            f"({user_quotes / total_quotes:.2%})"
        )

    @commands.command()
    async def quoteboard(self, ctx: commands.Context, page: int = 1):
        """Show a leaderboard of users with the most quotes."""
        page_count = ceil(len(await self.database.distinct("author.id")) / 10)
        if 1 > page > page_count:
            return await ctx.send(":no_entry_sign: Invalid page number")
        users = ""
        start_from = (page - 1) * 10
        current = start_from + 1
        agg = self.database.aggregate(
            [
                {"$match": {"author": {"$ne": None}}},  # Filter multiquotes out.
                {"$sortByCount": "$author.id"},
                {"$limit": 10},
                {"$skip": start_from},
            ]
        )
        async for result in agg:
            author, quotes = result.values()
            users += f"{current}. <@{author}> - {quotes}\n"
            current += 1

        embed = Embed(colour=Colour(0xae444a))
        embed.add_field(name=f"Page {page}/{page_count}", value=users)
        embed.set_author(name="Quotes Leaderboard", icon_url=CYBERDISC_ICON_URL)

        return await ctx.send(embed=embed)


def setup(bot: Bot):
    bot.add_cog(QuoteCog(bot))
