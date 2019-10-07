import re

from cdbot.constants import (
    ADMIN_MENTOR_ROLE_ID, ADMIN_ROLES, CD_BOT_ROLE_ID, NICKNAME_PATTERNS, PLACEHOLDER_NICKNAME,
    ROOT_ROLE_ID, STATIC_NICKNAME_ROLE_ID, SUDO_ROLE_ID
)
from discord import AuditLogAction, Member
from discord.ext.commands import Bot, Cog, command, has_role


def check_bad_name(nick):
    for i in NICKNAME_PATTERNS:
        if re.match(i, nick, re.IGNORECASE):
            return True
    return False


class Admin(Cog):
    """
    Admin functionality
    """

    def __init__(self, bot: Bot):
        self.bot = bot
        self.modules = {
            "mod_fallback": False,
            "purge_fallback": False
        }

    @Cog.listener()  # triggered on new/removed nickname
    async def on_member_update(self, member_before: Member, member_after: Member):
        # get corresponding audit log entry to find who initiated member change
        corresponding_audit_entry = None
        # get all audit log entries for Member Updated
        async for entry in self.bot.guilds[0].audit_logs(action=AuditLogAction.member_update):
            # if this entry was to the user in question, and was this specific nickname change
            if (entry.target == member_before and entry.after.nick == member_after.nick):
                corresponding_audit_entry = entry
                print(entry.user)
                print(entry.user.roles)
                break

        if corresponding_audit_entry is not None:  # successfully found audit log entry before
            # user changed their own nickname; ignore if admin/bot changed it
            admin_role_check = (corresponding_audit_entry.user.top_role.name in ADMIN_ROLES)
            bot_role_check = (corresponding_audit_entry.user.top_role.id == CD_BOT_ROLE_ID)
            mentor_role_check = (corresponding_audit_entry.user.top_role.id == ADMIN_MENTOR_ROLE_ID)
            if not(admin_role_check or bot_role_check or mentor_role_check):
                for i in member_after.roles:
                    print(i.id)
                    if i.id == STATIC_NICKNAME_ROLE_ID:  # user has Static Name role
                        await member_after.edit(nick=member_before.display_name)  # revert nickname
                        return
                    else:  # check for bad words
                        new_nickname = member_after.display_name
                        if check_bad_name(new_nickname):  # bad display name
                            if not check_bad_name(member_after.name):  # username is okay
                                await member_after.edit(nick=None)  # reset nickname
                            else:
                                # assign placeholder nickname
                                await member_after.edit(nick=PLACEHOLDER_NICKNAME)

    @Cog.listener()  # triggered on username change
    async def on_user_update(self, member_before: Member, member_after: Member):
        new_username = member_after.name
        if check_bad_name(new_username):  # bad username
            # assign placeholder nickname
            await member_after.edit(nick=PLACEHOLDER_NICKNAME)

    @Cog.listener()
    async def on_member_join(self, member: Member):
        username = member.name
        if check_bad_name(username):  # bad username
            # assign placeholder nickname
            await member.edit(nick=PLACEHOLDER_NICKNAME)

    def check_function_enabled(self, mod_name: str):
        pass

    @command()
    @has_role(ROOT_ROLE_ID)
    async def mute(self, member: Member):
        """
        Fallback mute command when Dyno suffers an outage.
        Same basic functionality though most other features will be lacking.
        """
        pass

    @command()
    @has_role(ROOT_ROLE_ID)
    async def unmute(self, member: Member):
        """
        Fallback unmute command when Dyno suffers an outage.
        """
        pass

    @command()
    @has_role(ROOT_ROLE_ID)
    async def warn(self, member: Member):
        """
        Fallback warn command when Dyno suffers an outage.
        """
        pass

    @command()
    @has_role(ROOT_ROLE_ID)
    async def purge(self, member: Member):
        """
        Fallback purge command when Dyno suffers an outage.
        This is dangerous, so a purge specific module has
        to be enable with :modprobe purge_fallback
        """
        pass

    @command()
    @has_role(ROOT_ROLE_ID)
    async def modprobe(self, *mod_args):
        """
        Hotplug the fallback moderation features in an extended outage scenario.
        These commands are disabled by default to avoid accidental clashes.
        """
        pass

        """
        Things to sort:
            -> Mute/Unmute/Warn/Purge
            -> Timed Mutes
            -> Modlogs
            -> Hotplug modules
            -> Can't mute Sudo's/Root's/Already muted
            -> Muted embed to DM?
            -> Sort out *args
        """


def setup(bot):
    bot.add_cog(Admin(bot))
