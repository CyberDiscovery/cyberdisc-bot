"""Main script to define bot methods, and start the bot."""

import logging
import sys
from collections import defaultdict
from os import environ

from discord import Game
from discord.ext.commands import Bot, when_mentioned_or

from bot.log import DiscordHandler


logger = logging.getLogger(__name__)

muted = []
admins = []

bot = Bot(
    command_prefix=when_mentioned_or(
        "...", ":"
    ),
    activity=Game(
        name=":help"
    )
)

logger.addHandler(DiscordHandler(bot))
logger.setLevel(logging.INFO)

bot.muted = []
bot.banned_ids = []
bot.quotes = defaultdict(list)
bot.log = logger


def handle_exception(exception, instance, traceback):
    """Handle an uncaught exception."""
    logger.exception(
        "**{0}**\n{1}".format(
            exception.__name__, instance
        )
    )


@bot.check
async def block_banned_ids(ctx):
    """Check for if a user is banned."""
    return ctx.author.id not in bot.banned_ids


@bot.check
async def block_muted(ctx):
    """Check for if a user is muted."""
    return ctx.author.id not in bot.muted

# Log all uncaught exceptions
sys.excepthook = handle_exception

# Load cogs
bot.load_extension("bot.cogs.general")
bot.load_extension("bot.cogs.cyber")
bot.load_extension("bot.cogs.fun")

if __name__ == "__main__":
    bot.run(environ.get("BOT_TOKEN"))
