"""Initialise cdbot as a package for poetry."""

import sentry_sdk

from os import environ

from .bot import bot


def main():
    """Entry point for poetry script."""
    if environ.get("SENTRY_URL") is not None:
        sentry_sdk.init(environ.get("SENTRY_URL"))
    bot.run(environ.get("BOT_TOKEN"))
