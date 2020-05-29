import base64
from os import environ


DEPLOY = bool(environ.get('DEPLOY'))


def getenv(name: str, fallback: str = "") -> str:
    """Return an (optionally base64-encoded) env var."""
    variable = environ.get(name)
    if DEPLOY and variable is not None:
        variable = base64.b64decode(variable).decode()
    return variable or fallback


class MongoDB:
    MONGOHOST = getenv("MONGOHOST")
    MONGOPORT = int(getenv("MONGOPORT", 27017))
    MONGOUSER = getenv("MONGOUSER")
    MONGODATABASE = getenv("MONGODATABASE")
    MONGOPASSWORD = getenv("MONGOPASSWORD")


BOT_TOKEN = getenv("BOT_TOKEN")
SENTRY_URL = getenv("SENTRY_URL")

# Fun constants
SERVER_ID = int(environ.get("SERVER_ID", "409851296116375565"))
QUOTES_CHANNEL_ID = int(environ.get("QUOTES_CHANNEL_ID", "463657120441696256"))
QUOTES_BOT_ID = 292953664492929025
QUOTE_CZAR_ID = int(environ.get("QUOTES_CZAR_ID", "471681927439712287"))
LOGGING_CHANNEL_ID = int(environ.get("LOGGING_CHANNEL_ID", "538494690601992212"))
WELCOME_BOT_ID = 155149108183695360

# Misc roles
HUNDRED_PERCENT_ROLE_ID = 640481360766697482
TRUE_HUNDRED_PERCENT_ROLE_ID = 640481628292120576

# Lists for administration
STAFF_ROLE_ID = 450063890362138624
FAKE_ROLE_ID = 533826912712130580
STATIC_NICKNAME_ROLE_ID = 567259415393075210
CD_BOT_ROLE_ID = 543768819844251658
ADMIN_MENTOR_ROLE_ID = 502238208747110411
ROOT_ROLE_ID = int(environ.get("ROOT_MEMBERS_ID", "450113490590629888"))
SUDO_ROLE_ID = int(environ.get("SUDO_MEMBERS_ID", "450113682542952451"))
ADMIN_ROLES = ("Root", "Sudo")
BANNED_DOMAINS = ["discord.gg"]


class Roles:

    class Elite:
        MAIN = int(environ.get("ELITE_MEMBERS_ID", "580387468336037888"))

        class London:
            YOUNGER = int(environ.get("LDN_Y_MEMBERS_ID", "580387877385404428"))
            OLDER = int(environ.get("LDN_O_MEMBERS_ID", "580387897644023811"))

        class Birmingham:
            YOUNGER = int(environ.get("BRM_Y_MEMBERS_ID", "580387895299276830"))
            OLDER = int(environ.get("BRM_O_MEMBERS_ID", "580387899833581572"))

        class Lancaster:
            YOUNGER = int(environ.get("LAN_Y_MEMBERS_ID", "580387892853997578"))
            OLDER = int(environ.get("LAN_O_MEMBERS_ID", "580387898973618176"))

        class VET2019:
            CYBERIST = int(environ.get("2019_CYBERIST_MEMBERS_ID", "610387199300730900"))
            FORENSICATOR = int(environ.get("2019_FORENSICATOR_MEMBERS_ID", "580387897644023811"))

        TALENTDEV = int(environ.get("TALENTDEV_MEMBERS_ID", "669927831031250954"))

    class Exchange:
        SHORTLIST = int(environ.get("EXCH_S_MEMBERS_ID", "582894164597932034"))
        CONFIRMED = int(environ.get("EXCH_C_MEMBERS_ID", "585150522336608256"))


# Cyber Constants
HINTS_LIMIT = 8
CYBERDISC_ICON_URL = "https://pbs.twimg.com/profile_images/921313066515615745/fLEl2Gfa_400x400.jpg"
ELITECOUNT_ENABLED = True

# Readme command constants
README_SEND_ALIASES = ["create", "push", "generate", "send", "make", "build", "upload"]
README_RECV_ALIASES = ["fetch", "get", "pull", "download", "retrieve", "dm", "dl"]

END_README_MESSAGE = (
    "**Can't see any of the above?**\nIf you can't see any of the rich embeds above, try the"
    " following: `Settings -> Text & Images -> Link Preview (Show website preview info from"
    " links pasted into that chat)  -> ON`"
)

BASE_ALIASES = {
    "Headquarters": ["headquarters", "main", "hq", "h"],
    "Moonbase": ["moonbase", "python", "moon", "m"],
    "Forensics": ["forensics", "f"],
    "Volcano": ["volcano", "v", "volc"]
}

# Admin Constants
PLACEHOLDER_NICKNAME = "Valued server member"
NICKNAME_PATTERNS = [
    r'(discord\.gg/)',  # invite links
    r'(nigg|ligma|fag|nazi|hitler|\bpaki\b)',  # banned words
    r'(http(s)?:\/\/.)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)'  # hyperlinks
]

# Emoji Alphabet
EMOJI_LETTERS = [
    "\U0001f1e6\U0001f170\U0001F359",  # A
    "\U0001f1e7\U0001f171",  # B
    "\U0001f1e8\u262a\u00A9",  # C
    "\U0001f1e9\u21a9",  # D
    "\U0001f1ea\U0001f4e7",  # E
    "\U0001f1eb",  # F
    "\U0001f1ec\u26fd",  # G
    "\U0001f1ed\u2653",  # H
    "\U0001f1ee\u2139",  # I
    "\U0001f1ef\u2614",  # J
    "\U0001f1f0",  # K
    "\U0001f1f1\U0001f552\U0001F462",  # L
    "\U0001f1f2\u24c2\u24c2\u264f\u264d\u303d",  # M
    "\U0001f1f3\U0001f4c8\U0001F3B5",  # N
    "\U0001f1f4\U0001f17e\u2b55",  # O
    "\U0001f1f5\U0001f17f",  # P
    "\U0001f1f6",  # Q
    "\U0001f1f7",  # R
    "\U0001f1f8\U0001f4b0\u26a1\U0001F4B2",  # S
    "\U0001f1f9\u271d\U0001F334",  # T
    "\U0001f1fa\u26ce",  # U
    "\U0001f1fb\u2648",  # V
    "\U0001f1fc\u3030",  # W
    "\U0001f1fd\u274e\u274c\u2716",  # X
    "\U0001f1fe\U0001f331\u270C",  # Y
    "\U0001f1ff\U0001f4a4",  # Z
    "\u26ab\U0001f535\U0001f534\u26aa",  # Whitespace alternatives
    "\u2755\u2757\u2763",  # !
    "\u2754\u2753",  # ?
    "\U0001f4b2",  # $
    "\U000021aa",  # (
    "\U000021a9"  # )
]
