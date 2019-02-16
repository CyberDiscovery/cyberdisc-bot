"""Initialise cdbot as a package for poetry."""

from os import environ

from .bot import bot


def main():
    """Entry point for poetry script."""
    bot.run(environ.get("BOT_TOKEN"))
