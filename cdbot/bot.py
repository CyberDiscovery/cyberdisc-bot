"""Main script to define bot methods, and start the bot."""

import logging
from platform import release, system
from os import listdir

from discord import Game, Intents
from discord.ext.commands import Bot, when_mentioned_or
from sentry_sdk import configure_scope

from cdbot.log import DiscordHandler

logger = logging.getLogger(__name__)

intents = Intents.default()
intents.members = True
intents.message_content = True

bot = Bot(command_prefix=when_mentioned_or("...", ":"), activity=Game(name=":help"), intents=intents)

logger.addHandler(DiscordHandler(bot))
logger.setLevel(logging.INFO)

bot.muted = []
bot.banned_ids = []
bot.log = logger


@bot.before_invoke
async def register_metadata(ctx):
    """Attach additional data to sentry events."""
    with configure_scope() as scope:
        scope.user = {"id": ctx.author.id, "username": str(ctx.author)}
        scope.set_context("client_os", {"name": system(), "version": release()})
        scope.set_tag("command", ctx.message.content)
        scope.set_tag("channel", str(ctx.channel))


@bot.check
async def block_banned_ids(ctx):
    """Check for if a user is banned."""
    return ctx.author.id not in bot.banned_ids


@bot.check
async def block_muted(ctx):
    """Check for if a user is muted."""
    return ctx.author.id not in bot.muted


async def load_extensions():
    for filename in listdir("./cdbot/cogs"):
        if filename.endswith(".py"):
            # cut off the .py from the file name
            await bot.load_extension(f"cdbot.cogs.{filename[:-3]}")
