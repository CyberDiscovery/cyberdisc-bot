import re
from json import load

from aiohttp import ClientSession
from discord import Embed, Message
from discord.ext.commands import Bot, Context, command

from bot.constants import CYBERDISC_ICON_URL, PWNED_ICON_URL


class Cyber:
    """
    Cyber Discovery/Security related commands.
    """

    def __init__(self, bot: Bot):
        self.bot = Bot
        self.game_regex = re.compile(
            "^(?=.*\bgame\b)(?=.*\bwhen\b)(?=.*\b(does|will|did|\?)\b)(?=.*\b(end|finish|close)\b).*$",
            re.IGNORECASE)
        self.essentials_regex = re.compile(
            "^(?=.*\bessentials\b)(?=.*\bwhen\b)(?=.*\b(does|will|did|\?)\b)(?=.*\b(end|finish|close)\b).*$",
            re.IGNORECASE)
        self.elite_qualification_regex = re.compile(
            "^(?=.*\bhow\b)(?=.*\belite\b)(?=.*\bget\b)(?=.*\bto\b).*$",
            re.IGNORECASE)
        self.elite_dates_regex = re.compile(
            "^(?=.*\belite\b)(?=.*\bwhen\b)(?=.*\b(does|will|did|\?)\b)(?=.*\b(start|begin|run|end)\b).*$",
            re.IGNORECASE)
        self.elite_email_regex = re.compile(
            "^(?=.*\belite\b)(?=.*\bemail\b)(?=.*\bhave(?:n(?:[o'])?t)?\b)(?=.*\b(got|received|)\b).*$",
            re.IGNORECASE)

    @command(aliases=["l", "lc"])
    async def level(self, ctx: Context, level_num: int, challenge_num: int):
        """
        Gets information about a specific CyberStart Game level and challenge.
        """

        # Gather HQ data from CyberStart Game.
        with open("headquarters.json") as f:
            game_docs = load(f)

        if level_num not in range(len(game_docs) + 1):
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

    @command()
    async def haveibeenpwned(self, ctx: Context, account: str):
        """
        Searches haveibeenpwned.com for breached accounts.
        """

        url = "https://haveibeenpwned.com/api/v2/breachedaccount/"

        data = {}

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

        url = "https://api.pwnedpasswords.com/pwnedpassword/"

        # If the page doesn't return 200, it will assume there are no breached accounts of that name.
        async with ClientSession() as session:
            async with session.get(url + password) as response:
                if response.status == 200:
                    data = await response.text()
                else:
                    data = ""

        embed = Embed(
            name="have i been pwned?",
            description=f"{ctx.author.mention} | This password has ",
            colour=0x5DBCD2
        )
        embed.set_author(
            name="have i been pwned?",
            icon_url=PWNED_ICON_URL
        )

        if data:
            embed.description += f"been uncovered {data} times."
        else:
            embed.description += f"has never been uncovered."

        await ctx.send(embed=embed)

    async def on_message(self, message: Message):

        # CyberStart Game Dates.
        if self.game_regex.match(message.content):
            await message.channel.send(f"{message.author.mention}  |  Cyberstart Game ended on the 29th May.")

        # CyberStart  Dates.
        elif self.essentials_regex.match(message.content):
            await message.channel.send(f"{message.author.mention}  |  Cyberstart Essentials ends on the 30th June.")

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
