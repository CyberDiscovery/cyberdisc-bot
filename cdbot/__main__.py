"""Entry point for the 'python -m cdbot' command."""

import cdbot
from asyncio import run

if __name__ == "__main__":
    run(cdbot.main())
