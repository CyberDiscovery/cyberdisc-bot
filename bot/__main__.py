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
    return ctx.author.id not in bot.banned_ids


@bot.check
async def block_muted(ctx):
    return ctx.author.id not in bot.muted


# Load cogs
bot.load_extension("bot.cogs.admin")
bot.load_extension("bot.cogs.general")
bot.load_extension("bot.cogs.cyber")
bot.load_extension("bot.cogs.fun")

if __name__ == "__main__":
    bot.run(environ.get("BOT_TOKEN"))
