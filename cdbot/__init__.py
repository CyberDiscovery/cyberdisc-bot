"""Initialise cdbot as a package for poetry."""

import sentry_sdk
from git import Repo
import os

from .bot import bot
from .constants import BOT_TOKEN, SENTRY_URL


def main():
    """Entry point for poetry script."""
    try:
        import googleclouddebugger
        path = os.path.dirname(os.path.abspath(__file__))
        path = '/'.join(path.split('/')[:-2])
        googleclouddebugger.enable(
            module='cdbot',
            version=str(Repo(path).commit())
        )
    except ImportError:
        pass
    sentry_sdk.init(SENTRY_URL)
    bot.run(BOT_TOKEN)
