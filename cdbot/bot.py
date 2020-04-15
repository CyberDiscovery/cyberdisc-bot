"""Main script to define bot methods, and start the bot."""

import logging

from cdbot.log import DiscordHandler
from discord import Game
from discord.ext.commands import Bot, when_mentioned_or


logger = logging.getLogger(__name__)

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
bot.log = logger


@bot.check
async def block_banned_ids(ctx):
    """Check for if a user is banned."""
    return ctx.author.id not in bot.banned_ids


@bot.check
async def block_muted(ctx):
    """Check for if a user is muted."""
    return ctx.author.id not in bot.muted


# Load cogs
bot.load_extension("cdbot.cogs.general")
bot.load_extension("cdbot.cogs.cyber")
bot.load_extension("cdbot.cogs.fun")
bot.load_extension("cdbot.cogs.admin")
bot.load_extension("cdbot.cogs.quoting")
