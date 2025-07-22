from discord import SlashCommandGroup, Option, Member
from discord.ext import commands

from models.CustomMogiContext import MogiApplicationContext
from models.PlayerModel import PlayerProfile

from utils.data.data_manager import data_manager
from utils.data.mogi_manager import mogi_manager
from utils.data._database import db_players
from utils.command_helpers.find_player import get_guild_member
from utils.decorators.checks import is_moderator
from utils.decorators.player import other_player


class edit(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    edit = SlashCommandGroup(name="edit", description="Suspend or unsuspend players")

    @edit.command(name="add_mmr", description="Add MMR to a player")
    @is_moderator()
    @other_player(query_varname="searched_player")
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
        # Check if player is in a mogi in another channel
        for mogi in mogi_manager.read_registry().values():
            if ctx.player in mogi.players and mogi.channel_id != ctx.channel.id:
                return await ctx.respond(
                    f"This player is currently in a mogi in <#{mogi.channel_id}>. Use the command there."
                )

        # Use the player profile instance from the mogi the player is in right of (if applicable)
        if ctx.mogi and ctx.player in ctx.mogi.players:
            ctx.player = next(
                (p for p in ctx.mogi.players if p.discord_id == ctx.player.discord_id),
                None,
            )

        new_mmr = ctx.player.mmr + delta_mmr
        ctx.player.mmr = new_mmr

        if isHistory:
            ctx.player.append_history(delta_mmr)

        await ctx.respond(
            f"Changed by {delta_mmr}:\n Updated <@{ctx.player.discord_id}> MMR to {new_mmr}"
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
        player: PlayerProfile = data_manager.find_player(searched_player)

        if not player:
            await ctx.respond("Couldn't find that player")

        # Check if player is in a mogi in another channel
        for mogi in mogi_manager.read_registry().values():
            if player in mogi.players and mogi.channel_id != ctx.channel.id:
                return await ctx.respond(
                    f"This player is currently in a mogi in <#{mogi.channel_id}>. Use the command there."
                )

        # Use the player profile instance from the mogi the player is in right of (if applicable)
        if ctx.mogi and player in ctx.mogi.players:
            player: PlayerProfile = next(
                (p for p in ctx.mogi.players if p.discord_id == player.discord_id),
                None,
            )

        player.name = new_name

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
        player: PlayerProfile = data_manager.find_player(searched_player)

        if not player:
            await ctx.respond("Couldn't find that player")

        db_players.delete_one({"_id": player._id})

        if try_remove_roles:
            discord_member: Member | None = await get_guild_member(
                ctx.guild, player.discord_id
            )
            if not discord_member:
                return await ctx.respond(
                    f"Deleted <@{player.discord_id}>'s profile (couldn't find user to remove roles from)"
                )
            for role in discord_member.roles:
                if "Lounge -" in role.name:
                    await discord_member.remove_roles(role, reason="Deleted profile")
                if "InMogi" in role.name:
                    await discord_member.remove_roles(role, reason="Deleted profile")

        await ctx.respond(f"Deleted <@{player.discord_id}>'s profile and removed roles")


def setup(bot: commands.Bot):
    bot.add_cog(edit(bot))
