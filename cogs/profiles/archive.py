from discord import SlashCommandGroup, Option
from discord.ext import commands

from models.CustomMogiContext import MogiApplicationContext
from models.PlayerModel import PlayerProfile

from utils.data.database import db_players, db_archived
from utils.command_helpers.find_player import search_player
from utils.command_helpers.checks import is_moderator


class archive(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    archive = SlashCommandGroup(
        name="archive", description="Archive or unarchive players"
    )

    @archive.command(name="add", description="Archive a player")
    @is_moderator()
    async def archive_add(
        self,
        ctx: MogiApplicationContext,
        searched_player: str = Option(
            str, name="player", description="username | @ mention | discord_id"
        ),
    ):
        player: PlayerProfile = search_player(searched_player)

        if not player:
            return await ctx.respond("Couldn't find that player")

        db_archived.insert_one(player.to_mongo())
        db_players.delete_one({"_id": player._id})

        await ctx.respond(f"Archived <@{player.discord_id}>")

    @archive.command(name="retrieve", description="Unarchive a player")
    @is_moderator()
    async def archive_retrieve(
        self,
        ctx: MogiApplicationContext,
        searched_player: str = Option(
            str, name="player", description="username | @ mention | discord_id"
        ),
    ):
        player: PlayerProfile = search_player(searched_player, from_archive=True)

        if not player:
            return await ctx.respond("Couldn't find that player")

        print(player.__dict__)

        db_players.insert_one(player.to_mongo())
        db_archived.delete_one({"_id": player._id})

        await ctx.respond(f"Retrieved <@{player.discord_id}>")


def setup(bot: commands.Bot):
    bot.add_cog(archive(bot))
