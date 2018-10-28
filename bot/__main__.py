"""Main script to define bot methods, and start the bot."""

from os import environ

from discord import Game
from discord.ext.commands import Bot, when_mentioned_or


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

bot.muted = []

bot.banned_ids = []


@bot.check
async def block_banned_ids(ctx):
    """Check for if a user is banned."""
    return ctx.author.id not in bot.banned_ids


@bot.check
async def block_muted(ctx):
    """Check for if a user is muted."""
    return ctx.author.id not in bot.muted


# Load cogs
bot.load_extension("bot.cogs.admin")
bot.load_extension("bot.cogs.general")
bot.load_extension("bot.cogs.cyber")
bot.load_extension("bot.cogs.fun")
bot.load_extension("bot.cogs.sound")

if __name__ == "__main__":
    bot.run(environ.get("BOT_TOKEN"))
