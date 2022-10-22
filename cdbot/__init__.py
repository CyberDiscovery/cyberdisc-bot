"""Initialise cdbot as a package for poetry."""

import sentry_sdk
from git import Repo
from sentry_sdk.integrations.aiohttp import AioHttpIntegration

from .bot import bot, load_extensions
from .constants import BOT_TOKEN, SENTRY_URL


async def main():
    """Entry point for poetry script."""
    sentry_sdk.init(
        SENTRY_URL,
        release=Repo().head.object.hexsha,
        integrations=[AioHttpIntegration()],
    )
    await load_extensions()
    await bot.start(BOT_TOKEN)

    #bot.run(BOT_TOKEN)
