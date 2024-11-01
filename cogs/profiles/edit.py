from pymongo import ReturnDocument

from discord import SlashCommandGroup, ApplicationContext, Option
from discord.ext import commands

from models.PlayerModel import PlayerProfile
from utils.data.database import db_players
from utils.command_helpers.find_player import search_player
from utils.command_helpers.checks import is_moderator


class edit(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    edit = SlashCommandGroup(name="edit", description="Suspend or unsuspend players")

    @edit.command(name="mmr", description="Add MMR to a player")
    @is_moderator()
    async def mmr(
        self,
        ctx: ApplicationContext,
        searched_player: str = Option(
            str, name="player", description="username | @ mention | discord_id"
        ),
        delta_mmr: int = Option(int, name="mmr", description="MMR to add"),
        isHistory: bool = Option(
            bool,
            name="history",
            description="Include in history",
            required=False,
            default="False",
            choices=["True", "False"],
        ),
    ):
        player: PlayerProfile = search_player(searched_player)

        if not player:
            await ctx.respond("Couldn't find that player")

        new = db_players.find_one_and_update(
            {"_id": player._id},
            {
                "$inc": {"mmr": delta_mmr},
                "$push": {"history": delta_mmr} if isHistory == "True" else {},
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
        ctx: ApplicationContext,
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


def setup(bot: commands.Bot):
    bot.add_cog(edit(bot))
