import datetime
import re
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
from hashlib import sha1
=======

>>>>>>> parent of efe3127... will this fix the build?
=======

>>>>>>> parent of efe3127... will this fix the build?
=======

>>>>>>> parent of efe3127... will this fix the build?
=======

>>>>>>> parent of efe3127... will this fix the build?
=======

>>>>>>> parent of efe3127... will this fix the build?
=======

>>>>>>> parent of efe3127... will this fix the build?
=======

>>>>>>> parent of efe3127... will this fix the build?
from json import load

from aiohttp import ClientSession
from dateutil.relativedelta import relativedelta
from discord import Embed, Message
from discord.ext.commands import Bot, Context, command

from bot.constants import CYBERDISC_ICON_URL, PWNED_ICON_URL


class Cyber:
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

    @command(aliases=["l", "lc"])
    async def level(self, ctx: Context, level_num: int, challenge_num: int):
        """
        Gets information about a specific CyberStart Game level and challenge.
        If the date is before the start date of game (15th January 2019) it will redirect to game() instead
        """

        if datetime.date.today() < datetime.date(2019, 1, 15):
            await self.game.callback(self, ctx)
            return

        # Gather HQ data from CyberStart Game.
        with open("headquarters.json") as f:
            game_docs = load(f)

        if not 0 < level_num <= len(game_docs):
            await ctx.send("Invalid level number!")

        elif challenge_num not in range(len(game_docs[f"L{level_num}"]) + 1):
            await ctx.send("Invalid challenge number!")

        else:
            # Select the needed challenge
            challenge_raw = game_docs[f"L{level_num}"][f"C{challenge_num}"]
            challenge_title = challenge_raw["title"]
            challenge_tip = challenge_raw["tips"]
            challenge_text = challenge_raw["description"]
            embed = Embed(
                title=(f"Level {level_num} Challenge {challenge_num} - {challenge_title}"),
                description=challenge_text,
                colour=0x4262f4
            )
            embed.set_author(
                name="Cyber Discovery",
                icon_url=CYBERDISC_ICON_URL
            )
            embed.set_footer(text="  |  ".join(challenge_tip))

            await ctx.send(embed=embed)

    @command(aliases=["a", "al"])
    async def assess(self, ctx: Context, challenge_num: int):
        """
        Gets information about a specific CyberStart Assess level and challenge.
        """

        # Gather Assess data from JSON file.
        with open("assess.json") as f:
            assess_docs = load(f)

        if not 0 < challenge_num <= len(assess_docs):
            await ctx.send("Invalid challenge number!")

        else:
            # Select the needed challenge
            challenge_raw = assess_docs[challenge_num - 1]
            challenge_title = challenge_raw["title"]
            challenge_difficulty = challenge_raw["difficulty"]
            challenge_text = challenge_raw["description"]
            embed = Embed(
                title=(f"CyberStart Assess Challenge {challenge_num} - {challenge_title}"),
                description=challenge_text,
                colour=0x4262f4
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
        # Get the current date
        today = datetime.date.today()
        game_start_date = datetime.date(2019, 1, 15)
        time_until_game = relativedelta(game_start_date, today)

        # Given a number of items, determine whether it should be pluralised.
        # Then, return the suffix of 's' if it should be, and '' if it shouldn't.
        def suffix_from_number(num):
            return "" if num == 1 else "s"

        month_or_months = "month" + suffix_from_number(time_until_game.months)
        day_or_days = "day" + suffix_from_number(time_until_game.days)

        month_countdown = f"{time_until_game.months} {month_or_months}"
        day_countdown = f"{time_until_game.days} {day_or_days}"

        # Diable the months component of the countdown when there are no months left
        if time_until_game.months:
            month_and_day_countdown = f"{month_countdown} and {day_countdown}"
        else:
            month_and_day_countdown = day_countdown

        if today > game_start_date:
            await ctx.send("Cyberstart Game has begun! Use :level base level to get info"
                           "on specific challenges once we update the bot")
            return
        await ctx.send("Cyberstart Game begins on the 15th January 2019.")
        await ctx.send(f"That's in {month_and_day_countdown}!")

    @command()
    async def essentials(self, ctx: Context):
        # Get the current date
        today = datetime.date.today()
        essentials_start_date = datetime.date(2019, 3, 5)
        time_until_essentials = relativedelta(essentials_start_date, today)

        # Given a number of items, determine whether it should be pluralised.
        # Then, return the suffix of 's' if it should be, and '' if it shouldn't.
        def suffix_from_number(num):
            return "" if num == 1 else "s"

        month_or_months = "month" + suffix_from_number(time_until_essentials.months)
        day_or_days = "day" + suffix_from_number(time_until_essentials.days)

        month_countdown = f"{time_until_essentials.months} {month_or_months}"
        day_countdown = f"{time_until_essentials.days} {day_or_days}"

        # Diable the months component of the countdown when there are no months left
        if time_until_essentials.months:
            month_and_day_countdown = f"{month_countdown} and {day_countdown}"
        else:
            month_and_day_countdown = day_countdown

        if today > essentials_start_date:
            await ctx.send("Cyberstart Essentials has begun!")
            return
        await ctx.send("Cyberstart Essentials begins on the 5th March 2019.")
        await ctx.send(f"That's in {month_and_day_countdown}!")

    async def on_message(self, message: Message):

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
                                       "  Cyberstart Essentials begins on the 5 March 2019.")

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
            text = f"{message.author.mention}  |  Cyberstart Elite dates: London - 4th and 5th August,"
            text += " Bristol - 28th and 29th July, Manchester - 21st and 22nd July"
            await message.channel.send(text)

        # CyberStart Elite email.
        elif self.elite_email_regex.match(message.content):
            text = f"{message.author.mention}  |  **Quote from the Cyber Discovery Elite team: **"
            text += "We’re currently allocating students to their preferred locations so it’s an ongoing process!"
            text += " We’ll send out details of your location as soon as we can. It shouldn’t be too long!"
            await message.channel.send(text)


def setup(bot):
    bot.add_cog(Cyber(bot))
