"""Initialise cdbot as a package for poetry."""

import sentry_sdk
from git import Repo

from .bot import bot
from .constants import BOT_TOKEN, SENTRY_URL


def main():
    """Entry point for poetry script."""
    sentry_sdk.init(SENTRY_URL, release=Repo().head.object.hexsha)
    bot.run(BOT_TOKEN)
