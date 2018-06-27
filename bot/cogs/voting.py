from discord.ext.commands import Bot, Context, UserInputError, group, command, has_any_role
from discord import Reaction, User
from emoji import UNICODE_EMOJI

from bot.constants import ADMIN_ROLES


class Voting:
    """
    Commands for the voting system.
    """

    def __init__(self, bot: Bot):
        self.bot = bot
        self.polls = []

    async def on_reaction_add(self, reaction: Reaction, user: User):
        poll = self.polls.get(reaction.message.id)

        if poll:
            if poll["anonymous"]:
                await reaction.message.remove_reaction(reaction.emoji, user)
            poll["votes"][user.id] = reaction.emoji

    @group()
    @has_any_role(*ADMIN_ROLES)
    async def poll(self, ctx: Context):
        pass

    @poll.command()
    async def add(self, ctx: Context, message: str, *args: str):
        """
        Command to create a poll.
        """
        poll = {
            "votes": {},
            "emojis": [],
            "anonymous": False,
            "time": 60,  # Time defaults to 1 minute
            "message_id": 0
        }
        skip = False
        for i in range(len(args)):
            if skip:  # Allows to skip checking of the next arg, e.g. if it's a parameter for flag.
                skip = False

            elif args[i] == "-a":  # Flag to enable anonymous voting.
                poll["anonymous"] = True

            elif args[i] == "-e":  # Flag to add an extra emoji to the voting choices.
                try:
                    emoji = args[i+1]
                except IndexError:
                    raise UserInputError("No emoji specified after -e flag.")

                skip = True

                if emoji in UNICODE_EMOJI:
                    pass
                elif emoji in map(str, self.bot.emojis):
                    emoji = emoji
                else:
                    raise UserInputError("Invalid emoji after -e flag.")

                poll["emojis"].append(args[i+1])

            elif args[i] == "-t":  # Flag to specify time left to vote.
                try:
                    time = args[i+1]
                except IndexError:
                    raise UserInputError("No time specified after -t flag.")

                skip = True

                time = reversed(time.split(":"))
                for value in time:
                    if not value.isdigit():
                        raise UserInputError("Invalid time format after -t flag.")
                minutes = time[0]
                hours = 0
                days = 0
                if len(time) > 1:
                    hours = int(time[1])
                if len(time) > 2:
                    days = int(time[2])
                if len(time) > 3:
                    raise UserInputError("Invalid time format after -t flag.")
                total_seconds = minutes*60 + hours*60*60 + days*24*60*60
                poll["time"] = total_seconds

        poll_msg = await ctx.send(message)
        for emoji in poll["emojis"]:
            await poll_msg.add_reaction(emoji)
        poll["message_id"] = message.id
        self.polls.append(poll)


def setup(bot: Bot):
    bot.add_cog(Voting(bot))
