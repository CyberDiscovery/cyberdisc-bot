import re

from discord import AuditLogAction, Colour, Embed, Member
from discord.ext.commands import Bot, Cog, Context, command, has_any_role

from cdbot.constants import (
    ADMIN_MENTOR_ROLE_ID,
    ADMIN_ROLES,
    CD_BOT_ROLE_ID,
    LOGGING_CHANNEL_ID,
    NICKNAME_PATTERNS,
    PLACEHOLDER_NICKNAME,
    ROOT_ROLE_ID,
    STATIC_NICKNAME_ROLE_ID,
    SUDO_ROLE_ID
)


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

    @Cog.listener()  # triggered on new/removed nickname
    async def on_member_update(self, member_before: Member, member_after: Member):
        # get corresponding audit log entry to find who initiated member change
        corresponding_audit_entry = None
        # get all audit log entries for Member Updated
        async for entry in self.bot.guilds[0].audit_logs(
            action=AuditLogAction.member_update
        ):
            # if this entry was to the user in question, and was this specific nickname change
            if entry.target == member_before and entry.after.nick == member_after.nick:
                corresponding_audit_entry = entry
                break

        if (
            corresponding_audit_entry is not None
        ):  # successfully found audit log entry before
            # user changed their own nickname; ignore if admin/bot changed it
            admin_role_check = (
                corresponding_audit_entry.user.top_role.name in ADMIN_ROLES
            )
            bot_role_check = (
                corresponding_audit_entry.user.top_role.id == CD_BOT_ROLE_ID
            )
            mentor_role_check = (
                corresponding_audit_entry.user.top_role.id == ADMIN_MENTOR_ROLE_ID
            )
            if not (admin_role_check or bot_role_check or mentor_role_check):
                for i in member_after.roles:
                    if i.id == STATIC_NICKNAME_ROLE_ID:  # user has Static Name role
                        await member_after.edit(
                            nick=member_before.display_name
                        )  # revert nickname
                        return
                    else:  # check for bad words
                        new_nickname = member_after.display_name
                        if check_bad_name(new_nickname):  # bad display name
                            if not check_bad_name(
                                member_after.name
                            ):  # username is okay
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

    @command()
    @has_any_role(ROOT_ROLE_ID, SUDO_ROLE_ID)
    async def raid(
        self,
        ctx: Context,
        operand: str = ""
    ):
        """
        Allows an admin user to lock down the server in case of a raid.
        This command toggles invite link generation for @everyone and
        revokes all existing invite links.
        """

        everyone = ctx.channel.guild.default_role
        perms = everyone.permissions
        enabled = not perms.create_instant_invite
        logs_channel = self.bot.get_channel(LOGGING_CHANNEL_ID)

        operand = operand.lower()
        boolonoff = ("OFF", "ON")

        action = True
        embed = None

        if not operand:  # status query
            await ctx.send(f"Raid protection currently {boolonoff[enabled]}. Use `:raid [on/off]` to toggle.")
            action = False

        elif operand in ("on", "yes") and not enabled:  # need to turn it on
            enabled = True
            perms.update(create_instant_invite=False)
            embed = Embed(
                color=Colour.blue(),
                title="Raid Protection ON.",
                description=("Raid protection now ON - All invite links were"
                             " deleted and members may not create new ones")
            )
            for invite in await ctx.channel.guild.invites():  # delete links
                await invite.delete()

        elif operand in ("off", "no") and enabled:
            enabled = False
            perms.update(create_instant_invite=True)
            embed = Embed(
                color=Colour.blue(),
                title="Raid Protection OFF.",
                description=("Raid protection now OFF - Members can now create"
                             " new invite links")
            )

        else:  # no changes
            await ctx.send(f"Raid protection {boolonoff[enabled]}, nothing was changed.")
            action = False

        if action:  # if we toggled it
            msg = f"{ctx.author.name} toggled raid protection {boolonoff[enabled]}."
            await everyone.edit(reason=msg, permissions=perms)  # make the perm change
            await ctx.send(msg)  # direct response to invocation

            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            await logs_channel.send(embed=embed)  # log the event


async def setup(bot):
    await bot.add_cog(Admin(bot))
