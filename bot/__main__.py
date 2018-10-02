"""Main script to define bot methods, and start the bot."""

from os import environ
from itertools import cycle
from typing import List
from string import ascii_lowercase

from discord import Game

from constants import EMOJI_LETTERS
from discord.ext.commands import Bot, when_mentioned_or


EMOJI_LETTERS = [
    cycle(letters) for letters in EMOJI_LETTERS
]

muted = []
admins = []

ascii_lowercase += ' '


class CustomBot(Bot):
    """Bot class with custom methods."""

    def emojify(self, message: str) -> List[str]:
        """Convert a string to a list of emojis, for use in various cogs."""
        emoji = []
        # Copy the list so iterators are not affected
        emoji_trans = EMOJI_LETTERS.copy()

        # Enumerate characters in the message
        for i, character in enumerate(message):
            index = ascii_lowercase.find(character)
            if not index + 1:
                continue
            # Append the next iteration of the letter
            emoji.append(next(emoji_trans[i]))

        return emoji


bot = CustomBot(
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

if __name__ == "__main__":
    bot.run(environ.get("BOT_TOKEN"))
