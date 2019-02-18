"""Initialise cdbot as a package for poetry."""

from os import environ

from .bot import bot

import sentry_sdk


def main():
    """Entry point for poetry script."""
    if environ.get("SENTRY_URL") is not None:
        sentry_sdk.init(environ.get("SENTRY_URL"))
    bot.run(environ.get("BOT_TOKEN"))
