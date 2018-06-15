from discord.ext.commands import Bot, when_mentioned_or
from discord import Game

from os import environ


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


bot.load_extension("bot.cogs.admin")
bot.load_extension("bot.cogs.general")
bot.load_extension("bot.cogs.cyber")
bot.load_extension("bot.cogs.fun")


bot.run(environ.get("BOT_TOKEN"))
