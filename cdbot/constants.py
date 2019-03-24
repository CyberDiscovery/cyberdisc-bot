import base64
from os import environ

"""
Setup PostgreSQL
"""


class PostgreSQL:
    PGHOST = base64.b64decode(environ.get("PGHOST"))
    PGPORT = base64.b64decode(environ.get("PGPORT"))
    PGDATABASE = base64.b64decode(environ.get("PGDATABASE"))
    PGUSER = base64.b64decode(environ.get("PGUSER"))
    PGPASSWORD = base64.b64decode(environ.get("PGPASSWORD"))


"""
A list of constants.
"""
# Fun constants
QUOTES_CHANNEL_ID = int(environ("QUOTES_CHANNEL_ID", "463657120441696256"))
QUOTES_BOT_ID = 292953664492929025
LOGGING_CHANNEL_ID = int(environ("LOGGING_CHANNEL_ID", "538494690601992212"))
WELCOME_BOT_ID = 155149108183695360

# Lists for administration
STAFF_ROLE_ID = 450063890362138624
FAKE_ROLE_ID = 533826912712130580
ROOT_ROLE_ID = int(environ("ROOT_MEMBERS_ID", "450113490590629888"))
ADMIN_ROLES = ("Root", "Sudo")
BANNED_DOMAINS = ["discord.gg"]

# Cyber Constants

CYBERDISC_ICON_URL = "https://pbs.twimg.com/profile_images/" "921313066515615745/fLEl2Gfa_400x400.jpg"
PWNED_ICON_URL = "https://upload.wikimedia.org/wikipedia" "/commons/2/23/Have_I_Been_Pwned_logo.png"
END_README_MESSAGE = ("**Can't see any of the above?**\nIf you can't see any of the rich embeds above, try the"
                      " following: `Settings -> Text & Images -> Link Preview (Show website preview info from"
                      " links pasted into that chat)  -> ON`")
# Last level for CyberStart Assess where hints are allowed
HINTS_LIMIT = 8

# Base Aliases
BASE_ALIASES = {
    "Headquarters": ["headquarters", "main", "hq", "h"],
    "Moonbase": ["moonbase", "python", "moon", "m"],
    "Forensics": ["forensics", "f"],
}

# Emoji Alphabet

EMOJI_LETTERS = [  # Feel free to add to this list
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
