# Cyber Discovery Discord Bot

[![Build Docker Container](https://github.com/CyberDiscovery/cyberdisc-bot/actions/workflows/build.yml/badge.svg)](https://github.com/CyberDiscovery/cyberdisc-bot/actions/workflows/build.yml) [![Discord](https://img.shields.io/discord/409851296116375565)](https://discord.cyberdiscoverycommunity.uk) [![Lint](https://github.com/CyberDiscovery/cyberdisc-bot/actions/workflows/lint.yml/badge.svg)](https://github.com/CyberDiscovery/cyberdisc-bot/actions/workflows/lint.yml) [![GitHub](https://img.shields.io/github/license/cyberdiscovery/cyberdisc-bot)](https://github.com/CyberDiscovery/cyberdisc-bot/blob/master/LICENSE) ![Python 3.8.x](https://img.shields.io/badge/python-3.9.x-yellow.svg)

The bot for the Cyber Discovery [Community Discord Server](https://discord.cyberdiscoverycommunity.uk)!

## Installation

### Creating a Bot Token

First, head over to [the Discord Developer Portal](https://discordapp.com/developers/applications/) and create an application.
Set a name, then go to the bots tab (on the left) and add a new bot. For testing purposes, it is best to have the bot private, so untick the `Public Bot` option.

You should then get the client ID of your bot and put it into this URL to join it to your Discord server:

```text
https://discordapp.com/oauth2/authorize?&client_id=<insert client id here>&scope=bot&
```

### Docker Compose

You can run Cyber Discovery Bot most easily with Docker Compose. Just set the following environment variables and run `docker-compose up -d`.

* `BOT_TOKEN`
* `QUOTES_BOT_ID`
* `QUOTES_CHANNEL_ID`
* `LOGGING_CHANNEL_ID`

### Bare Metal

You can also locally install the bot on your system. First install the dependencies with [Poetry](https://python-poetry.org/):

```bash
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
poetry install
```

Or on Windows:

```powershell
(Invoke-WebRequest -Uri https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py -UseBasicParsing).Content | python
poetry install
```

If you don't already have the required Python version (currently 3.8+) installed, install [pyenv](https://github.com/pyenv/pyenv) before running the above commands.

You will then need to set the bot token as an environment variable:

```bash
export BOT_TOKEN="<insert bot token here>"
```

Or on Windows:

```powershell
set BOT_TOKEN="<insert bot token here>"
```

Finally, run the command `poetry run cdbot` in the root of the repository to run the bot on your machine. To access admin commands of the bot, set the environment variable `ROOT_MEMBERS_ID` to the ID of your administrators group.

## Commands

### General Commands

* **`:help`** - Displays information about the usage and syntax of all commands.

### Admin Commands

* **`:readme [push | pull] [channel id] [interval]`** - `pull` will DM the user a copy of the JSON used for #readme. `push` will create the readme channel using the set JSON file.

### Cyber Discovery Commands

* **`:assess [1-14]`** - Displays information about the corresponding level in CyberStart Assess.
* **`:essentials`** - Displays the remaining time until the start of CyberStart Essentials.
* **`:fieldmanual`** - Returns a link to the CyberStart Game field manual.
* **`:flag [base] [level] [challenge]`** - Generate a very legitimate:tm: flag for CyberStart Game.
* **`:game`** - Displays the remaining time until the start of CyberStart Game.
* **`:level [base] [level] [challenge]`** - Display information about challenges from CyberStart Game.

### Fun Commands

* **`:agentj [text]`** - Creates an image of Agent J with the specified text.
* **`:agentq [text]`** - Creates an image of Agent Q with the specified text.
* **`:angryj [text]`** - Creates an image of Angry Agent J with the specified text.
* **`:angrylyne [text]`** - Creates an image of Angry James Lyne with the specified text.
* **`:baldj [text]`** - Creates an image of Bald James Lyne with the specified text.
* **`:jibhat [text]`** - Creates an image of Jibhat with the specified text.
* **`:lmgtfy [-d][-ie] [search]`** - Returns a LMGTFY URL for the given question.  Adding `-d` will delete the message that instigated the command and `-ie` will enable the internet explainer feature on lmgtfy.
* **`:hundred`** - Returns the number of people who have completed all of CyberStart Game.
* **`:quotes [@mention]`** - Will return a random quote from the #quotes channel. Adding an username/mention will result in a random quote from that user being selected.
* **`:quoteboard [1]`** - Return a leaderboard of the number of entries in #quotes sorted by user.
* **`:quotecount [@mention]`** - Returns the number of quotes in the DB. Adding a username/mention will return the number of quotes from that user.
* **`:react [emoji]`** - Reacts to the previous message with the space seperated emojis in the requesting message.
* **`:xkcd [? | 1810]`** - Fetches xkcd comics. If the argument is left blank the latest comic is shown.  A random comic is shown if the argument is a `?`.  Otherwise, a comic number can be used to fetch a specific comic.

### Maths Commands

* **`:challenge [number]`** - Get a KCL maths challenge. If no number is specified, the most recent will be used, else the number will be how many after the most recent should be retrieved.
* **`:latex [latex]`** - Renders LaTeX. Can also be invoked by wrapping a string in `$` or `$$`.
