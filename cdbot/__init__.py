"""Initialise cdbot as a package for poetry."""

from os import environ

import base64
import sentry_sdk

from .bot import bot


def main():
    """Entry point for poetry script."""
    if environ.get("SENTRY_URL") is not None:
        sentry_sdk.init(base64.b64decode(environ.get("SENTRY_URL")))
    bot.run(base64.b64decode(environ.get("BOT_TOKEN")))
