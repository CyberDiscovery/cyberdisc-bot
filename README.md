# Cyber Discovery Discord Bot [![Build Status](https://dev.azure.com/cyberdiscovery/Cyber%20Discovery%20Discord%20Bot/_apis/build/status/Cyber%20Discovery%20Discord%20Bot?branchName=master)](https://dev.azure.com/cyberdiscovery/Cyber%20Discovery%20Discord%20Bot/_build/latest?definitionId=2&branchName=master) [![Discord](https://discordapp.com/api/guilds/409851296116375565/embed.png)](https://discord.gg/AQPh34Y)
The bot for the Cyber Discovery Community Discord Server!

## Installation
To test the bot, you will need to setup a custom instance of it running locally. First install the dependencies with poetry:
```
pip install --user poetry
poetry install
```
If you don't already have the required Python version (currently 3.7.2) installed, install [pyenv](https://github.com/pyenv/pyenv) before running the above commands.

Whilst they are installing, head over to [the Discord Developer Portal](https://discordapp.com/developers/applications/) and create an application.
It needs a name, then go to the bots tab (on the left) and add a new bot. For testing purposes, it is best to have the bot private, so uncheck that option.
Copy the token (you need to click to reveal it) and set it as an environment variable:
```
export BOT_TOKEN="<insert bot token here>"
```
Or on Windows:
```
set BOT_TOKEN="<insert bot token here>"
```
Go back to the home page of your application on Discord and grab the client ID. Then put it into this url:
```
https://discordapp.com/oauth2/authorize?&client_id=<insert client id here>&scope=bot&
```

Add it to a channel that you will use for testing.

Finally, run the command `poetry run cdbot` in the root of the repository to run the bot on your server. To access admin commands of the bot, add a group called `Root` to the server and add yourself to it.


## Commands
### General Commands:
* **`:help`** - Displays information about the usage and syntax of the commands

### Admin Commands
* **`:migrate_quotes`** - Migrate the existing quotes in the set quotes channel to the PostgreSQL database.
* **`:readme [push | pull] [channel id] [interval]`** - `pull` will DM the user a copy of the JSON used for #readme. `push` will create the readme channel using the set JSON file.

### Cyber Security Commands:
* **`:assess [1-14]`** - Displays information about the corresponding level in CyberStart Assess.
* **`:essentials`** - Displays the remaining time until the start of CyberStart Essentials.
* **`:fieldmanual`** - Returns a link to the CyberStart Game field manual.
* **`:flag [base] [level] [challenge]`** - Generate a very legitimate:tm: flag for CyberStart Game.
* **`:game`** - Displays the remaining time until the start of CyberStart Game.
* **`:hasitbeenpwned password`** - Searches pwnedpasswords.com for breached passwords.
* **`:haveibeenpwned email@exmaple.com`** - Searches haveibeenpwned.com for breached accounts.
* **`:level [base] [level] [challenge]` - Display information about challenges from CyberStart Game

### Fun Commands:
* **`:agentj [text]`** - Creates an image of Agent J with the specified text.
* **`:agentq [text]`** - Creates an image of Agent Q with the specified text.
* **`:angryj [text]`** - Creates an image of Angry Agent J with the specified text.
* **`:jibhat [text]`** - Creates an image of Jibhat with the specified text.
* **`:lmgtfy [-d][-ie] [search]`** - Returns a LMGTFY URL for the given question.  Adding `-d` will delete the message that instigated the command and `-ie` will enable the internet explainer feature on lmgtfy.
* **`:quotes [@mention]`** - Will return a random quote from the #quotes channel. Adding an username/mention will result in a random quote from that user being selected.
* **`:react [emoji `** - Reacts to the previous message with the space seperated emojis in the requesting message.
* **`:xkcd [? | 1810]`** - Fetches xkcd comics. If the argument is left blank the latest comic is shown.  A random comic is shown if the argument is a `?`.  Otherwise, a comic number can be used to fetch a specific comic.

