import datetime
import random
import re
import string
from asyncio import sleep
from hashlib import sha1
from io import StringIO
from json import load

from aiohttp import ClientSession
from cdbot.constants import (
    BASE_ALIASES, CYBERDISC_ICON_URL, HINTS_LIMIT, PWNED_ICON_URL, ROOT_ROLE_ID
)
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from discord import Colour, Embed, File, Message
from discord.ext.commands import Bot, Cog, Context, command


async def generatebase64(seed: int) -> str:
    random.seed(seed)
    letters = string.ascii_letters + string.digits + "+/="
    return "".join(random.choices(letters, k=20))


class Cyber(Cog):
    """
    Cyber Discovery/Security related commands.
    """

    def __init__(self, bot: Bot):
        self.bot = bot
        self.assess_start_regex = re.compile(
            r"^.*\bassess\b.*(start|begin|open)\b.*$",
            re.IGNORECASE
        )
        self.assess_end_regex = re.compile(
            r"^.*\bassess\b.*(end|finish|close)\b.*$",
            re.IGNORECASE
        )
        self.game_start_regex = re.compile(
            r"^.*\bgame\b.*(start|begin|open)\b.*$",
            re.IGNORECASE
        )
        self.game_end_regex = re.compile(
            r"^.*\bgame\b.*(end|finish|close)\b.*$",
            re.IGNORECASE
        )
        self.essentials_start_regex = re.compile(
            r"^.*\bessentials\b.*(start|begin|open)\b.*$",
            re.IGNORECASE
        )
        self.essentials_end_regex = re.compile(
            r"^.*\bessentials\b.*(end|finish|close)\b.*$",
            re.IGNORECASE
        )
        self.elite_qualification_regex = re.compile(
            r"^.*\bhow\b.*\bget\b.*\belite\b.*$",
            re.IGNORECASE
        )
        self.elite_dates_regex = re.compile(
            r"^.*\belite\b.*\bstart\b.*$",
            re.IGNORECASE
        )
        self.elite_email_regex = re.compile(
            r"^.*\bwhat\b.*\belite\b.*\bemail\b.*$",
            re.IGNORECASE
        )

    @command(aliases=["Manual", "manual", "fm"])
    async def fieldmanual(self, ctx: Context):
        """
        Returns a link to the field manual
        """

        await ctx.send("https://game.joincyberdiscovery.com/manual")

    @command(aliases=["l", "lc"])
    async def level(self, ctx: Context, base: str, level_num: int, challenge_num: int = 0):
        """
        Gets information about a specific CyberStart Game level and challenge.
        If the date is before the start date of game (15th January 2019) it will redirect to game() instead
        """

        if datetime.date.today() < datetime.date(2019, 1, 15):
            await self.game.callback(self, ctx)
            return

        # Gather data from CyberStart Game.
        with open("cdbot/data/game.json") as f:
            game_docs = load(f)
        # Temporary change to allow old usage method
        if base.isnumeric():
            challenge_num = level_num
            level_num = int(base)
            base = "hq"
        elif challenge_num == 0:
            await ctx.send("Invalid challenge number!")
            return
        # Find out which base the user is refering to.
        for area in BASE_ALIASES.keys():
            if base.lower() in BASE_ALIASES[area]:
                base = area
                break
        else:
            await ctx.send("Unknown base.")
            return

        # Check to see if that many levels are present
        if not 0 < level_num <= len(game_docs[base]):
            await ctx.send("Invalid level number!")
        # Then, check to see if the requested challenge is present
        elif challenge_num not in range(len(game_docs[base][level_num - 1]) + 1):
            await ctx.send("Invalid challenge number!")

        else:
            # Select the needed challenge
            challenge_raw = game_docs[base][level_num - 1][challenge_num - 1]
            challenge_title = challenge_raw["title"]
            challenge_tip = challenge_raw["tips"]
            challenge_text = challenge_raw["description"]
            embed = Embed(
                title=(f"{base} - Level {level_num} Challenge {challenge_num} - {challenge_title}"),
                description=challenge_text,
                colour=0x4262f4
            )
            embed.set_author(
                name="Cyber Discovery",
                icon_url=CYBERDISC_ICON_URL
            )
            embed.set_footer(text="  |  ".join(challenge_tip))

            await ctx.send(embed=embed)

    @command()
    async def flag(self, ctx: Context, base: str, level_num: int, challenge_num: int = 0):
        """Generate a flag for the specified base, level and challenge."""
        if challenge_num == 0:
            challenge_num = level_num
            level_num = int(base)
            base = "Headquarters"
        if level_num == 13 and challenge_num == 1:
            content = "13.1 is a No Flag Zone™ 🙅⛔⚔️"
        else:
            # Generates random, but unique and identical per challenge, base 64 "flag"
            content = "The flag is: ||" + (await generatebase64(ord(base[0]) + level_num + challenge_num)) + "||"

        embed = Embed(
            title=(f"{base} - Level {level_num} Challenge {challenge_num}"),
            description=content,
            colour=0x4262f4
        )
        embed.set_author(
            name="Cyber Discovery",
            icon_url=CYBERDISC_ICON_URL
        )

        await ctx.send(embed=embed)

    @command()
    async def readme(self, ctx: Context, operand: str = "", channel_id: int = 0, msg_send_interval: int = 0):
        """
        Allows generating, sending and manipulation of JSON file containing the info needed
        to create and send the embeds for the #readme channel. Only ROOT_ROLE_ID users have
        the permissions need to use this command.
        """

        README_SEND_ALIASES = ["create", "push", "generate", "send", "make", "build", "upload"]
        README_RECV_ALIASES = ["fetch", "get", "pull", "download", "retrieve", "dm", "dl"]

        operand = operand.lower()

        # The supplied operand is incorrect.
        if not (operand in README_SEND_ALIASES + README_RECV_ALIASES):
            incorrect_operand_embed = Embed(
                colour=0x673ab7,
                description=":shrug: **Invalid readme operand supplied.**"
            )
            await ctx.message.delete()
            await ctx.send(embed=incorrect_operand_embed)

        # User missed out the channel_id for certain commands.
        elif (channel_id == 0 and operand in README_SEND_ALIASES):
            misssing_channel_embed = Embed(
                colour=0xff5722,
                description=":facepalm: **Whoops, you missed out the channel ID! Try again.**"
            )
            await ctx.message.delete()
            await ctx.send(embed=misssing_channel_embed)

        # Process the request.
        elif ROOT_ROLE_ID in [msg_author.id for msg_author in ctx.message.author.roles]:
            # Let's create a series of #readme-capable embeds. If something is uploaded,
            # It will attempt to use that file for the readme, if omitted, it will use
            # the default JSONifed readme file and send that into the channel instead.
            if operand in README_SEND_ALIASES:
                try:
                    usr_confirmation_embed = Embed(
                        colour=0x4caf50,
                        description=":white_check_mark: **Creating readme using uploaded config file.**"
                    )

                    # The user has uploaded a config.
                    if ctx.message.attachments != []:
                        json_file_location = [_.url for _ in ctx.message.attachments][0]

                        # GETs the attachment data.
                        async with ClientSession() as session:
                            async with session.get(json_file_location) as response:
                                if response.status == 200:
                                    resp_text = await response.text()

                        json_config = load(StringIO(resp_text))
                        await ctx.send(embed=usr_confirmation_embed)

                    # No config uploaded, just use default config file.
                    else:
                        with open("cdbot/data/readme.json", "rb") as default_json:
                            json_config = load(default_json)

                        usr_confirmation_embed.description = (":ballot_box_with_check: "
                                                              "**Creating readme using default config file.**")
                        await ctx.send(embed=usr_confirmation_embed)

                    await ctx.message.delete()

                    for section in json_config:
                        # Get data from the JSON file sections.
                        if "content" in json_config[section]:
                            msg_content = json_config[section]["content"]

                        # We have an embed. Call in the Seahawks.
                        if "embed" in json_config[section]:
                            current_embed = Embed()
                            msg_embed = json_config[section]["embed"]
                            if "text" in msg_embed:
                                current_embed.description = msg_embed["text"]
                            if "color" in msg_embed:
                                current_embed.colour = Colour(int(msg_embed["color"], 16))

                            # Parse the fields, if there are any.
                            if "fields" in msg_embed:
                                for current_field in msg_embed["fields"]:
                                    # Add the fields to the current embed.
                                    current_embed.add_field(
                                        name=current_field["name"],
                                        value=current_field["value"]
                                    )

                        # Send the message.
                        requested_channel = self.bot.get_channel(channel_id)

                        if ("msg_content" in locals() and "current_embed" not in locals()):
                            await requested_channel.send(content=msg_content)
                        elif ("current_embed" in locals() and "msg_content" not in locals()):
                            await requested_channel.send(embed=current_embed)
                        else:
                            await requested_channel.send(content=msg_content, embed=current_embed)

                        # User has requested a delay between each message being sent.
                        if (0 < msg_send_interval < 901):
                            await sleep(msg_send_interval)

                except(Exception) as e:
                    parse_fail_embed = Embed(
                        colour=0x673ab7,
                        description=":x: **Error parsing JSON file, please ensure its valid!**"
                    )
                    await ctx.message.delete()
                    await ctx.send(embed=parse_fail_embed)
                    await ctx.send(e)  # DEBUG

            # Pull the readme JSON constant files and slide it into the user's DMs.
            elif operand in README_RECV_ALIASES:
                # Get the human-readble readme data.
                with open("cdbot/data/readme_raw.json", "rb") as readme_json:
                    raw_json = readme_json.read()

                    # Slide it to the user's DMs.
                    requesting_user = await self.bot.get_user_info(ctx.message.author.id)
                    await requesting_user.send(
                        content="Hey, here's your readme config file!",
                        file=File(raw_json, 'readme_raw.json')
                    )

                    msg_confirmation = Embed(
                        colour=0x009688,
                        description=":airplane: **Flying in, check your DMs!**"
                    )
                    await ctx.message.delete()
                    await ctx.send(embed=msg_confirmation)

        else:
            # User does not have permissions.
            no_perms_embed = Embed(
                colour=0xf44336,
                description="**Sorry, but you do not have the required permissions to use this command.**"
            )
            await ctx.send(embed=no_perms_embed)

    @command(aliases=["a", "al"])
    async def assess(self, ctx: Context, challenge_num: int):
        """
        Gets information about a specific CyberStart Assess level and challenge.
        """

        NO_HINTS_MSG = f"**:warning: Remember, other people can't give hints after challenge {HINTS_LIMIT}**"

        # Gather Assess data from JSON file.
        with open("cdbot/data/assess.json") as f:
            assess_docs = load(f)

        if not 0 < challenge_num <= len(assess_docs):
            await ctx.send("Invalid challenge number!")

        else:
            # Select the needed challenge
            challenge_raw = assess_docs[challenge_num - 1]
            challenge_title = challenge_raw["title"]
            challenge_difficulty = challenge_raw["difficulty"]
            challenge_text = challenge_raw["description"]

            if challenge_num > HINTS_LIMIT:
                challenge_text = NO_HINTS_MSG + '\n' + challenge_text

            embed = Embed(
                title=f"CyberStart Assess Challenge {challenge_num} - {challenge_title}",
                description=challenge_text,
                colour=0x4262f4,
                url=f"https://assess.joincyberdiscovery.com/challenge-{challenge_num:02d}"
            )
            embed.set_author(
                name="Cyber Discovery",
                icon_url=CYBERDISC_ICON_URL
            )
            embed.set_footer(text=f"Difficulty: {challenge_difficulty}")

            await ctx.send(embed=embed)

    @command()
    async def haveibeenpwned(self, ctx: Context, account: str):
        """
        Searches haveibeenpwned.com for breached accounts.
        """

        url = "https://haveibeenpwned.com/api/v2/breachedaccount/"

        data: dict = {}

        # GETs the data on the breached account.
        async with ClientSession() as session:
            async with session.get(url + account) as response:
                if response.status == 200:
                    data = await response.json()

        # If the page doesn't return 200, it will assume there are no breached accounts of that name.
        if data:
            info_string = "Info from `https://haveibeenpwned.com/`. Showing up to **5** breaches"
            info_string += " (Total: " + str(len(data))
            await ctx.send(f"{ctx.author.mention}  |  {info_string}")
            for i in data[:5]:
                output = "```"
                output += f"Title: {i['Title']}\n"
                output += f"Name: {i['Name']}\n"
                output += f"Breach date: {i['BreachDate']}\n"
                output += f"PwnCount: {i['PwnCount']}\n"

                # An ugly but working method of getting rid of the HTML formatting.
                desc = i["Description"]
                desc = desc.replace("<a href=\"", "")
                desc = desc.replace("\" target=\"_blank\" rel=\"noopener\">", " ")
                desc = desc.replace("</a>", "")
                desc = desc.replace("&quot;", "\"")
                output += f"Description: {desc}\n"

                output += "Lost data: " + "/".join(i['DataClasses']) + "\n"
                output += f"Currently active: {i['IsActive']}\n"
                output += "```"
                await ctx.send(output)

        else:
            await ctx.send(f"{ctx.author.mention}  |  This account has never been breached!")

    @command()
    async def hasitbeenpwned(self, ctx: Context, password: str):
        """
        Searches pwnedpasswords.com for breached passwords.
        """

        url = "https://api.pwnedpasswords.com/range/"
        digest = sha1(password.encode()).hexdigest().upper()  # NOQA
        prefix, digest = digest[:5], digest[5:]

        async with ClientSession() as session:
            async with session.get(url + prefix) as response:
                result = await response.text()

        match = re.search(fr"{digest}:(\d+)", result)
        if match is not None:
            count = int(match.group(1))
        else:
            count = 0

        embed = Embed(
            name="have i been pwned?",
            description=f"{ctx.author.mention} | This password has ",
            colour=0x5DBCD2
        )
        embed.set_author(
            name="have i been pwned?",
            icon_url=PWNED_ICON_URL
        )

        if count:
            embed.description += f"been uncovered {count} times."
        else:
            embed.description += f"has never been uncovered."

        await ctx.send(embed=embed)

    @command()
    async def game(self, ctx: Context):
        """
        Gets the date of, and days and months until, CyberStart Game
        """

        await self.countdown('15th January 2019', 'CyberStart Game', ctx)

    @command()
    async def essentials(self, ctx: Context):
        """
        Gets the date of, and days and months until, CyberStart Essentials
        """

        await self.countdown('5th March 2019', 'CyberStart Essentials', ctx)

    async def countdown(self, countdown_target_str: str, stage_name: str, ctx: Context):
        countdown_target = parse(countdown_target_str).date()

        # Get the current date
        today = datetime.date.today()
        time_until_target = relativedelta(countdown_target, today)

        # Given a number of items, determine whether it should be pluralised.
        # Then, return the suffix of 's' if it should be, and '' if it shouldn't.
        def suffix_from_number(num):
            return "" if num == 1 else "s"

        month_or_months = "month" + suffix_from_number(time_until_target.months)
        day_or_days = "day" + suffix_from_number(time_until_target.days)

        month_countdown = f"{time_until_target.months} {month_or_months}"
        day_countdown = f"{time_until_target.days} {day_or_days}"

        # Diable the months component of the countdown when there are no months left
        if time_until_target.months:
            month_and_day_countdown = f"{month_countdown} and {day_countdown}"
        else:
            month_and_day_countdown = day_countdown

        if today > countdown_target:
            await ctx.send(f"{stage_name} has begun!")
            return
        await ctx.send(f"{stage_name} begins on the {countdown_target_str}.\n"
                       f"That's in {month_and_day_countdown}!")

    @Cog.listener()
    async def on_message(self, message: Message):
        # Check the current command context
        ctx = await self.bot.get_context(message)
        # If message is a command, ignore regex responses.
        if ctx.valid:
            return

        # CyberStart Assess Dates.
        if self.assess_start_regex.match(message.content):
            await message.channel.send(f"{message.author.mention}  |"
                                       "  Cyberstart Assess began on the 6th November 2018.")

        elif self.assess_end_regex.match(message.content):
            await message.channel.send(f"{message.author.mention}  |  Cyberstart Assess ends on the 31st January 2019.")

        # CyberStart Game Dates.
        elif self.game_start_regex.match(message.content):
            await message.channel.send(f"{message.author.mention}  |  Cyberstart Game begins on the 15th January 2019.")

        elif self.game_end_regex.match(message.content):
            await message.channel.send(f"{message.author.mention}  |  Cyberstart Game ends on the 18th March 2019.")

        # CyberStart Essentials Dates.
        elif self.essentials_start_regex.match(message.content):
            await message.channel.send(f"{message.author.mention}  |"
                                       "  Cyberstart Essentials begins on the 5th March 2019.")

        elif self.essentials_end_regex.match(message.content):
            await message.channel.send(f"{message.author.mention}  |"
                                       "  Cyberstart Essentials ends on the 29th April 2019.")

        # CyberStart Elite qualification requirements.
        elif self.elite_qualification_regex.match(message.content):
            text = f"{message.author.mention}  |  **Quote from the @CyberDiscUK Twitter: **"
            text += "Selection for CyberStart Elite will be based on a combination of Game and Essentials results."
            await message.channel.send(text)

        # CyberStart Elite Dates.
        elif self.elite_dates_regex.match(message.content):
            text = f"{message.author.mention}  |  Cyberstart Elite dates for 2019 are yet to be announced."
            await message.channel.send(text)

        # CyberStart Elite email.
        elif self.elite_email_regex.match(message.content):
            text = f"{message.author.mention}  |  **Quote from the Cyber Discovery Elite team: **"
            text += "We’re currently allocating students to their preferred locations so it’s an ongoing process!"
            text += " We’ll send out details of your location as soon as we can. It shouldn’t be too long!"
            await message.channel.send(text)


def setup(bot):
    bot.add_cog(Cyber(bot))
