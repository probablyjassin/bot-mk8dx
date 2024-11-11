from pymongo import ReturnDocument

from discord import SlashCommandGroup, Option
from discord.ext import commands

from models.CustomMogiContext import MogiApplicationContext
from models.PlayerModel import PlayerProfile

from utils.data.database import db_players
from utils.command_helpers.find_player import search_player
from utils.command_helpers.checks import is_moderator


class edit(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    edit = SlashCommandGroup(name="edit", description="Suspend or unsuspend players")

    @edit.command(name="add_mmr", description="Add MMR to a player")
    @is_moderator()
    async def add_mmr(
        self,
        ctx: MogiApplicationContext,
        searched_player: str = Option(
            str, name="player", description="username | @ mention | discord_id"
        ),
        delta_mmr: int = Option(int, name="mmr", description="MMR to add"),
        isHistory: bool = Option(
            bool,
            name="history",
            description="Include in history",
            required=False,
            default=False,
        ),
    ):
        player: PlayerProfile = search_player(searched_player)

        if not player:
            await ctx.respond("Couldn't find that player")

        new = db_players.find_one_and_update(
            {"_id": player._id},
            {
                "$inc": {"mmr": delta_mmr},
                "$push": {"history": delta_mmr} if isHistory else {},
            },
            return_document=ReturnDocument.AFTER,
        )

        await ctx.respond(
            f"Changed by {delta_mmr}:\n Updated <@{player.discord_id}> MMR to {new['mmr']}"
        )

    @edit.command(name="username", description="Change a player's username")
    @is_moderator()
    async def username(
        self,
        ctx: MogiApplicationContext,
        searched_player: str = Option(
            str, name="player", description="username | @ mention | discord_id"
        ),
        new_name: str = Option(str, name="newname", description="new username"),
    ):
        player: PlayerProfile = search_player(searched_player)

        if not player:
            await ctx.respond("Couldn't find that player")

        db_players.update_one({"_id": player._id}, ({"$set": {"name": new_name}}))

        await ctx.respond(f"Changed <@{player.discord_id}>'s username to {new_name}")

    @edit.command(name="delete", description="Delete a player's profile")
    @is_moderator()
    async def delete(
        self,
        ctx: MogiApplicationContext,
        searched_player: str = Option(
            str, name="player", description="username | @ mention | discord_id"
        ),
        try_remove_roles: bool = Option(
            bool, name="try_remove_roles", description="Try removing Lounge roles"
        ),
    ):
        player: PlayerProfile = search_player(searched_player)

        if not player:
            await ctx.respond("Couldn't find that player")

        db_players.delete_one({"_id": player._id})

        if try_remove_roles:
            discord_member = await ctx.guild.fetch_member(player.discord_id)
            if not discord_member:
                return await ctx.respond(
                    f"Deleted <@{player.discord_id}>'s profile (couldn't find user to remove roles from)"
                )
            for role in discord_member.roles:
                if "Lounge -" in role.name:
                    await discord_member.remove_roles(role)
                if "InMogi" in role.name:
                    await discord_member.remove_roles(role)

        await ctx.respond(f"Deleted <@{player.discord_id}>'s profile and removed roles")


def setup(bot: commands.Bot):
    bot.add_cog(edit(bot))
