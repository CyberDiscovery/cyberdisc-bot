import datetime
import random
import re
import string
from asyncio import sleep
from io import StringIO
from json import load

from aiohttp import ClientSession
from cdbot.constants import (
    BASE_ALIASES, CYBERDISC_ICON_URL, END_README_MESSAGE, HINTS_LIMIT, HUNDRED_PERCENT_ROLE_ID, ROOT_ROLE_ID,
    TRUE_HUNDRED_PERCENT_ROLE_ID
)
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from discord import Colour, Embed, File, Message
from discord.ext.commands import Bot, Cog, Context, command, has_role


async def generatebase64(seed: int) -> str:
    random.seed(seed)
    letters = string.ascii_letters + string.digits + "+/="
    return "".join(random.choices(letters, k=20))


class Cyber(Cog):
    """
    Cyber Discovery/Security related commands.
    """

    match_strings = [
        # Assess dates
        (r"^.*\bassess\b.*(start|begin|open)\b.*$", "Cyberstart Assess began on the 6th November 2018."),
        (r"^.*\bassess\b.*(end|finish|close)\b.*$", "Cyberstart Assess ends on the 31st January 2019."),

        # Game dates
        (r"^.*\bgame\b.*(start|begin|open)\b.*$", "Cyberstart Game begins on the 15th January 2019."),
        (r"^.*\bgame\b.*(end|finish|close)\b.*$", "Cyberstart Game ends on the 15th April 2019."),

        # Essentials dates
        (r"^.*\bessentials\b.*(start|begin|open)\b.*$", "Cyberstart Essentials begins on the 5th March 2019."),
        (r"^.*\bessentials\b.*(end|finish|close)\b.*$", "Cyberstart Essentials ends on the 29th April 2019."),

        # Elite questions
        (r"^.*\bhow\b.*\bget\b.*\belite\b.*$", "**Quote from the @CyberDiscUK Twitter: **"
         "Selection for CyberStart Elite will be based on a combination of Game and Essentials results."),

        (r"^.*\belite\b.*\bstart\b.*$", "Cyberstart Elite dates for 2019 are yet to be announced."),

        (r"^.*\bwhat\b.*\belite\b.*\bemail\b.*$", "**Quote from the Cyber Discovery Elite team: **"
         "We’re currently allocating students to their preferred locations so it’s an ongoing process! "
         "We’ll send out details of your location as soon as we can. It shouldn’t be too long!"
         ),

        # Beta date
        (r"^.*\bbeta\b.*(end|finish|close)\b.*$", "Cyberstart Cloud CTF ends on the May 13th 2019 at 12:00pm."),
    ]

    def __init__(self, bot: Bot):
        self.bot = bot

        self.matches = [
            (re.compile(i[0], re.IGNORECASE), i[1]) for i in self.match_strings
        ]

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
    @has_role(ROOT_ROLE_ID)
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
        else:
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
                        # Initialise our message and embed variables each loop.
                        # This is to prevent leftover data from being re-sent.
                        msg_content, current_embed = None, None

                        # The part which handles general messages.
                        if "content" in json_config[section]:
                            msg_content = json_config[section]["content"]

                        # We have an embed. Call in the Seahawks.
                        if "embed" in json_config[section]:
                            current_embed = Embed()
                            msg_embed = json_config[section]["embed"]
                            if "title" in msg_embed:
                                current_embed.title = msg_embed["title"]
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

                        if (msg_content is not None and current_embed is None):
                            await requested_channel.send(content=msg_content)
                        elif (current_embed is not None and msg_content is None):
                            await requested_channel.send(embed=current_embed)
                        else:
                            await requested_channel.send(content=msg_content, embed=current_embed)

                        # User has requested a delay between each message being sent.
                        if (0 < msg_send_interval < 901):
                            await sleep(msg_send_interval)

                    # Send the trailing embed message constant.
                    await requested_channel.send(content=END_README_MESSAGE)

                except(Exception):
                    parse_fail_embed = Embed(
                        colour=0x673ab7,
                        description=":x: **Error parsing JSON file, please ensure its valid!**"
                    )
                    await ctx.message.delete()
                    await ctx.send(embed=parse_fail_embed)

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

    @command()
    async def hundred(self, ctx: Context):
        """
        Gets the number of 100% and true 100% users
        """

        game_r = ctx.guild.get_role(HUNDRED_PERCENT_ROLE_ID)
        true_r = ctx.guild.get_role(TRUE_HUNDRED_PERCENT_ROLE_ID)

        await ctx.send(f"There are {len(game_r.members)} that have completed Cyberstart Game. Out of them, "
                       f"{len(true_r.members)} have also completed Essentials and Assess.")

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

        # Check if the message matches any of the pre-baked regexes
        for regex, response in self.matches:
            if regex.match(message.content):
                await message.channel.send(f"{message.author.mention}  |  {response}")
                break


def setup(bot):
    bot.add_cog(Cyber(bot))
