"""Main script to define bot methods, and start the bot."""

import logging
from platform import system, release, python_version
from discord import Game
from discord.ext.commands import Bot, when_mentioned_or
from sentry_sdk import configure_scope

from cdbot.log import DiscordHandler

logger = logging.getLogger(__name__)

bot = Bot(command_prefix=when_mentioned_or("...", ":"), activity=Game(name=":help"))

logger.addHandler(DiscordHandler(bot))
logger.setLevel(logging.INFO)

bot.muted = []
bot.banned_ids = []
bot.log = logger


@bot.before_invoke
async def register_metadata(ctx):
    """Attach additional data to sentry events."""
    with configure_scope() as scope:
        scope.user = {
            'id': ctx.author.id,
            'username': str(ctx.author)
        }
        scope.set_tag('client_os.name', system())
        scope.set_tag('client_os.version', release())
        scope.set_tag('runtime.name', "Python")
        scope.set_tag('runtime.version', python_version())
        scope.set_tag('command', ctx.message.content)
        scope.set_tag('channel', str(ctx.channel))


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
bot.load_extension("cdbot.cogs.maths")
