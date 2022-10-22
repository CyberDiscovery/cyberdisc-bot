"""Entry point for the 'python -m cdbot' command."""

from asyncio import run

import cdbot

if __name__ == "__main__":
    run(cdbot.main())
