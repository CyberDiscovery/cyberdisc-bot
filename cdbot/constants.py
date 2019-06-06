import base64
from os import environ


DEPLOY = bool(environ.get('DEPLOY'))


def getenv(name: str, fallback: str = "") -> str:
    """Return an (optionally base64-encoded) env var."""
    variable = environ.get(name)
    if DEPLOY and variable is not None:
        variable = base64.b64decode(variable).decode()
    return variable or fallback


class PostgreSQL:
    PGHOST = getenv("PGHOST")
    PGPORT = getenv("PGPORT")
    PGUSER = getenv("PGUSER")
    PGDATABASE = getenv("PGDATABASE")
    PGPASSWORD = getenv("PGPASSWORD")


BOT_TOKEN = getenv("BOT_TOKEN")
SENTRY_URL = getenv("SENTRY_URL")

# Fun constants
QUOTES_CHANNEL_ID = int(environ.get("QUOTES_CHANNEL_ID", "463657120441696256"))
QUOTES_BOT_ID = 292953664492929025
LOGGING_CHANNEL_ID = int(environ.get("LOGGING_CHANNEL_ID", "538494690601992212"))
WELCOME_BOT_ID = 155149108183695360

# Misc roles
HUNDRED_PERCENT_ROLE_ID = 532654673270669313
TRUE_HUNDRED_PERCENT_ROLE_ID = 552536443948367903

# Lists for administration
STAFF_ROLE_ID = 450063890362138624
FAKE_ROLE_ID = 533826912712130580
STATIC_NICKNAME_ROLE_ID = 567259415393075210
CD_BOT_ROLE_ID = 543768819844251658
ADMIN_MENTOR_ROLE_ID = 502238208747110411
ROOT_ROLE_ID = int(environ.get("ROOT_MEMBERS_ID", "450113490590629888"))
ADMIN_ROLES = ("Root", "Sudo")
BANNED_DOMAINS = ["discord.gg"]
ELITE_ROLES = {
    "Elite": {
        "London": {"Younger": "580387877385404428", "Older": "580387897644023811"},
        "Birmingham": {"Younger": "580387895299276830", "Older": "580387899833581572"},
        "Lancaster": {"Younger": "580387898973618176", "Older": "580387892853997578"},
    },
    "Exchange": {"Shortlist": "582894164597932034", "Confirmed": "585150522336608256"},
}

# Cyber Constants
HINTS_LIMIT = 8
CYBERDISC_ICON_URL = "https://pbs.twimg.com/profile_images/921313066515615745/fLEl2Gfa_400x400.jpg"

END_README_MESSAGE = (
    "**Can't see any of the above?**\nIf you can't see any of the rich embeds above, try the"
    " following: `Settings -> Text & Images -> Link Preview (Show website preview info from"
    " links pasted into that chat)  -> ON`"
)

BASE_ALIASES = {
    "Headquarters": ["headquarters", "main", "hq", "h"],
    "Moonbase": ["moonbase", "python", "moon", "m"],
    "Forensics": ["forensics", "f"],
}

# Admin Constants
PLACEHOLDER_NICKNAME = "Valued server member"
NICKNAME_PATTERNS = [
    r'(discord\.gg/)',  # invite links
    r'(nigg|cunt|ligma|fag|nazi|hitler|\bpaki\b)',  # banned words
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
    "\U0001f4b2"  # $
]
