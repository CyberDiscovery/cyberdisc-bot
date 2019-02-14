# Cyber Discovery Discord Bot [![Build Status](https://travis-ci.com/CyberDiscovery/cyberdisc-bot.svg?branch=master)](https://travis-ci.com/CyberDiscovery/cyberdisc-bot) [![Codacy Badge](https://api.codacy.com/project/badge/Grade/c23486f81ee7451eb66405f01591b586)](https://www.codacy.com/app/CyberDiscovery/cyberdisc-bot?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=CyberDiscovery/cyberdisc-bot&amp;utm_campaign=Badge_Grade) [![Discord](https://discordapp.com/api/guilds/409851296116375565/embed.png)](https://discord.gg/AQPh34Y)
The bot for the Cyber Discovery Community Discord Server!

## Installation
To test the bot, you will need to setup a custom instance of it running locally. First install the dependencies with poetry:
```
pip install --user poetry
poetry install
```
If you don't already have the required Python version (currently 3.7.2) installed, install [https://github.com/pyenv/pyenv](pyenv) before running the above commands.

Whilst they are installing, head over to [the Discord Developer Portal](https://discordapp.com/developers/applications/) and create an application.
It needs a name, then go to the bots tab (on the left) and add a new bot. For testing purposes, it is best to have the bot private, so uncheck that option.
Copy the token (you need to click to reveal it) and set it as an environment variable:
```
export BOT_TOKEN="<insert bot token here>"
```
You may want to add this line to your .bashrc or similar to preserve it over terminal windows and sessions.

Go back to the home page of your application on discord and grab the client ID. Then put it into this url:
```
https://discordapp.com/oauth2/authorize?&client_id=<insert client id here>&scope=bot&
```

Add it to a channel that you will use for testing.

Finally, run the command `poetry run cyberdisc-bot` in the root of the repository to run the bot on your server. To access admin commands of the bot, add a group called `Root` to the server and add yourself to it.


## Commands
### General Commands:
* **`:help`** - Displays information about the usage and syntax of the commands

### Admin Commands
* **`:set_quote_channel [#channel]`** - Set the channel to be used as a source by the `:quotes` command. Note: You will have to do this after every restart of the bot.
* **`:mute [@mention]`** - Mute the selected user indefinitely.
* **`:unnmute [@mention]`** - Unmute the selected user.

### Cyber Security Commands:
* **`:level 13 1`** - Gets information about a specific CyberStart Game challenge. If Game has not yet begun, calls `:game` instead.
* **`:haveibeenpwned email@exmaple.com`** - Searches haveibeenpwned.com for breached accounts.
* **`:hasitbeenpwned password`** - Searches pwnedpasswords.com for breached passwords.
* **`:game`** - Displays information about CyberStart Game, including start time.
* **`:assess <level>`** - Displays information about a CyberStart assess level. `<Level>` can be any number from 1-14

### Commands for Fun:
* **`:lmgtfy [-d][-ie] Stupid Question?`** - Returns a LMGTFY URL for the given question.  Adding `-d` will delete the message that instigated the command and `-ie` will enable the internet explainer feature on lmgtfy.
* **`:react ❓`** - Reacts to the previous message with the space seperated emojis in the requesting message.
* **`:xkcd [? | 1810]`** - Fetches xkcd comics. If the argument is left blank the latest comic is shown.  A random comic is shown if the argument is a `?`.  Otherwise, a comic number can be used to fetch a specific comic.
* **`:quotes [@mention]`** - Will return a random quote from the #quotes channel. Adding an username/mention will result in a random quote from that user being selected.
* **`:agentj text`** - Creates an image of Agent J with the specified text.
* **`:jibhat text`** - Creates an image of Jibhat with the specified text.
