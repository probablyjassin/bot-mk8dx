from discord import Guild, Member


async def get_guild_member(guild: Guild, id: int) -> Member | None:
    member: Member | None = None
    try:
        member = await guild.fetch_member(id)
    except:
        pass
    return member
