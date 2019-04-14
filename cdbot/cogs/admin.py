import re

from cbot.constants import NICKNAME_PATTERNS, PLACEHOLDER_NICKNAME
from discord.ext.commands import Bot, Cog

def checkName(nick):
    result = False
    for i in NICKNAME_PATTERNS:
        if re.match(i, nick):
            result = True
            break

    return result


class Admin(Cog):
    """
    Admin functionality
    """

    def __init__(self, bot: Bot):
        self.bot = bot

    @Cog.listener()  # triggered on new/removed nickname
    async def on_member_update(memberBefore, memberAfter):
        newNickname = memberAfter.display_name
        if checkName(newNickname):  # bad display name
            if not checkName(memberAfter.name):  # username is okay
                await memberAfter.edit(nick=None)  # reset nickname
            else:
                # assign placeholder nickname
                await memberAfter.edit(nick=PLACEHOLDER_NICKNAME)

    @Cog.listener()  # triggered on username change
    async def on_user_update(memberBefore, memberAfter):
        newUsername = memberAfter.name
        if checkName(newUsername):  # bad username
            # assign placeholder nickname
            await memberAfter.edit(nick=PLACEHOLDER_NICKNAME)

    @Cog.listener()
    async def on_member_join(member):
        username = member.name
        if checkName(username):  # bad username
            # assign placeholder nickname
            await member.edit(nick=PLACEHOLDER_NICKNAME)


def setup(bot):
    bot.add_cog(Admin(bot))
