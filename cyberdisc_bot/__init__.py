"""Main script to define bot methods, and start the bot."""

from os import environ

from .bot import bot


def main():
    """Entry point for poetry script."""
    bot.run(environ.get("BOT_TOKEN"))
