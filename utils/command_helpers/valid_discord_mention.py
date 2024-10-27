import re


def is_discord_mention(string):
    return bool(re.compile(r"^<@!?(\d+)>$").match(string))
