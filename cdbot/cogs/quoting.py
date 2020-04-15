from typing import Any, Callable, List, Union

from discord import utils, Embed, Message, Member, NotFound, TextChannel, User
from discord.ext import commands
from discord.ext.commands import Bot, Cog

from cdbot.constants import SERVER_ID, QUOTES_CHANNEL_ID, QUOTE_CZAR_ID


def is_quote_czar() -> Callable:
    async def predicate(ctx: commands.Context) -> bool:
        czar_role = utils.get(ctx.guild.roles, id=QUOTE_CZAR_ID)
        return czar_role in ctx.author.roles or ctx.author.guild_permissions.administrator
    return commands.check(predicate)


class QuoteCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        # maybe need do stuff here
        pass

    @Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        # temporary for test
        await ctx.send(f"{type(error)}: {error}")

    async def get_member_by_id(self, member_id: int) -> Union[Member, User, None]:
        if (member := utils.get(self.bot.get_all_members(), id=member_id)) is not None:  # noqa: E203, E231
            return member
        try:
            user = await self.bot.fetch_user(member_id)
            return user
        except NotFound:
            return None

    def quote_dict(self, quoted: Message, message: Message) -> dict:
        quote = dict(
            content_id=quoted.id,
            content_link=quoted.jump_url,
            channel=quoted.channel.id,
            content=quoted.content,
            author=dict(id=quoted.author.id, name=str(quoted.author), avatar=str(quoted.author.avatar_url_as(size=32))),
            quoted_at=message.created_at,
            quoted_by=message.author.id,
        )
        if len(quoted.embeds) > 0:
            quote["embed"] = quoted.embeds[0].to_dict()
        return quote

    async def quote_embed(self, quote: dict) -> Embed:
        if quote.get("embed", None):
            return Embed.from_dict(quote["embed"])
        channel = utils.get(self.bot.get_all_channels(), guild__id=SERVER_ID, id=quote["channel"])
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
            embed.description = quote["content"]
        else:
            embed.description = f"```{quote['content']}```"
        embed.description += f"\n[Jump to orignal]({quote['content_link']})"
        embed.timestamp = quote["quoted_at"]
        return embed

    async def range_quote(self, channel: TextChannel, after: Message, before: Message) -> List[Message]:
        messages = await channel.history(after=after, before=before).flatten()
        return [after, *messages, before]

    def multi_quote_dict(self, messages: List[Message], message: Message) -> dict:
        multi_quote = dict(
            content_id=messages[0].id,
            content_link=messages[0].jump_url,
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

    def paginate_lines(self, lines: List[str]) -> List[str]:
        paginator = commands.Paginator()
        for line in lines:
            try:
                paginator.add_line(line)
            except RuntimeError:
                paginator.close_page()
                paginator.add_line(line)
        return paginator.pages

    async def multi_quote_embed(self, multi_quote: dict) -> Union[Embed, List[Embed]]:
        embeds = [message.get("embed", None) for message in multi_quote["messages"]]
        if any(embeds):
            return list(filter(lambda x: x is not None, embeds))
        embed = Embed().set_author(name=str(self.bot.user), icon_url=self.bot.user.avatar_url)
        quoter = await self.get_member_by_id(multi_quote["quoted_by"])
        channel = utils.get(self.bot.get_all_channels(), guild__id=SERVER_ID, id=multi_quote["channel"])
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
            if "```" in message["content"]:
                line_str += "\n"
            line_str += message["content"][:1950]
            lines.append(line_str)
        pages = self.paginate_lines(lines)
        if len(pages) < 2:
            embed.description = pages[0] + f"\n[Jump to content]({multi_quote['content_link']})"
            return embed
        else:
            embeds = []
            for page in pages:
                embed = embed.copy()
                embed.description = page
                embeds.append(embed)
            embeds[-1].description = page[-1] + f"\n[Jump to content]({multi_quote['content_link']})"
            return embeds

    async def generate_single_quote(self, quoted: Message, original: Message):
        quote = self.quote_dict(quoted, original)
        embed = await self.quote_embed(quote)
        return embed, quote

    async def generate_multi_quote(
        self, channel: TextChannel, from_message: Message, to_message: Message, message: Message
    ):
        messages = await self.range_quote(channel, from_message, to_message)
        quote = self.multi_quote_dict(messages, message)
        embeds = await self.multi_quote_embed(quote)
        return embeds, quote

    async def save_single_quote(self, data: dict):
        # do something.
        pass

    async def save_multi_quote(self, data: dict):
        # do something.
        pass

    @commands.group(invoke_without_command=True)
    async def quote(self, ctx: commands.Context, message: Message):
        """
        Quote a single message.
        """
        embed, _ = await self.generate_single_quote(message, ctx.message)
        return await ctx.send(embed=embed)

    @quote.group(name="from", invoke_without_command=True)
    async def quote_from(self, ctx: commands.Context, channel: TextChannel, message: int):
        """
        Quote a message from another channel.
        """
        message = await channel.fetch_message(message)
        await ctx.invoke(self.quote, message)

    @quote.group(name="range", invoke_without_command=True)
    async def quote_range(self, ctx: commands.Context, from_message: Message, to_message: Message):
        """
        Quote a range of messages from the current channel.
        """
        embeds, _ = await self.generate_multi_quote(ctx.channel, from_message, to_message, ctx.message)
        if isinstance(embeds, list):
            for embed in embeds:
                await ctx.send(embed=embed)
            return
        return await ctx.send(embed=embeds)

    @quote_range.command(name="from")
    async def quote_range_from(self, ctx: commands.Context, channel: TextChannel, from_message: int, to_message: int):
        """
        Quote a range of messages from another channel.
        """
        from_message = await channel.fetch_message(from_message)
        to_message = await channel.fetch_message(to_message)
        embeds, _ = await self.generate_multi_quote(ctx.channel, from_message, to_message, ctx.message)
        if isinstance(embeds, list):
            for embed in embeds:
                await ctx.send(embed=embed)
            return
        return await ctx.send(embed=embeds)

    @quote_from.command(name="range")
    async def quote_from_range(self, ctx: commands.Context, channel: TextChannel, from_message: int, to_message: int):
        await ctx.invoke(self.quote_range_from, channel, from_message, to_message)

    @quote.group(name="save", invoke_without_command=True)
    @is_quote_czar()
    async def quote_save(self, ctx: commands.Context, message: Message):
        embed, data = await self.generate_single_quote(message, ctx.message)
        await self.save_single_quote(data)
        quote_channel = utils.get(self.bot.get_all_channels(), guild__id=SERVER_ID, id=QUOTES_CHANNEL_ID)
        await quote_channel.send(embed=embed)
        return await ctx.send(content="Saved quote to database", embed=embed)

    @quote_save.group("from", invoke_without_command=True)
    @is_quote_czar()
    async def quote_save_from(self, ctx: commands.Context, channel: TextChannel, message: int):
        message = await channel.fetch_message(message)
        embed, data = await self.generate_single_quote(message, ctx.message)
        await self.save_single_quote(data)
        quote_channel = utils.get(self.bot.get_all_channels(), guild__id=SERVER_ID, id=QUOTES_CHANNEL_ID)
        await quote_channel.send(embed=embed)
        return await ctx.send(content="Saved quote to database", embed=embed)

    @quote_save.group("range", invoke_without_command=True)
    @is_quote_czar()
    async def quote_save_range(self, ctx: commands.Context, from_message: Message, to_message: Message):
        embeds, data = await self.generate_multi_quote(ctx.channel, from_message, to_message, ctx.message)
        await self.save_multi_quote(data)
        if isinstance(embeds, list):  # silently doesnt send long multiquotes to # quotes
            for embed in embeds:
                await ctx.send(embed=embed)
                return
        quote_channel = utils.get(self.bot.get_all_channels(), guild__id=SERVER_ID, id=QUOTES_CHANNEL_ID)
        await quote_channel.send(embed=embeds)
        return await ctx.send(content="Saved quote to database", embed=embeds)

    @quote_save_range.command("from")
    @is_quote_czar()
    async def quote_save_range_from(
        self, ctx: commands.Context, channel: TextChannel, from_message: int, to_message: int
    ):
        from_message = await channel.fetch_message(from_message)
        to_message = await channel.fetch_message(to_message)
        embeds, data = await self.generate_multi_quote(ctx.channel, from_message, to_message, ctx.message)
        await self.save_multi_quote(data)
        if isinstance(embeds, list):  # silently doesnt send long multiquotes to # quotes
            for embed in embeds:
                await ctx.send(embed=embed)
                return
        quote_channel = utils.get(self.bot.get_all_channels(), guild__id=SERVER_ID, id=QUOTES_CHANNEL_ID)
        await quote_channel.send(embed=embeds)
        return await ctx.send(content="Saved quote to database", embed=embeds)

    @quote_save_from.command("range")
    @is_quote_czar()
    async def quote_save_from_range(
        self, ctx: commands.Context, channel: TextChannel, from_message: int, to_message: int
    ):
        await ctx.invoke(self.quote_save_range_from, channel, from_message, to_message)


def setup(bot: Bot):
    bot.add_cog(QuoteCog(bot))
