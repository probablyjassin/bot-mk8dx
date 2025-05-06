import io, json

from config import ROOMS

from discord import SlashCommandGroup, Option, AllowedMentions, File
from discord.ext import commands

from models.CustomMogiContext import MogiApplicationContext
from models.RoomModel import Room

from utils.data.mogi_manager import mogi_manager
from utils.data.state import state_manager
from utils.command_helpers.confirm import confirmation
from utils.command_helpers.checks import (
    is_admin,
    is_moderator,
    is_mogi_manager,
)


class debugging(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    debug = SlashCommandGroup(name="debug", description="Debugging commands")

    @debug.command(name="current_mogi", description="print the mogi for this channel")
    @is_admin()
    async def current_mogi(self, ctx: MogiApplicationContext):
        mogi_data = ctx.mogi.to_json()
        await ctx.respond(
            file=File(
                fp=io.StringIO(json.dumps(mogi_data, indent=2)),
                filename="mogi_data.json",
            )
        )

    @debug.command(name="destroy_mogi")
    @is_admin()
    async def destroy_mogi(self, ctx: MogiApplicationContext):
        await ctx.response.defer()

        if not mogi_manager.get_mogi(ctx.channel.id):
            return await ctx.respond("No mogi exists for this channel")

        if await confirmation(
            ctx,
            f"Are you sure you want to wipe the entire state of the mogi in <#{ctx.channel.id}>",
        ):
            mogi_manager.destroy_mogi(ctx.channel.id)
            return await ctx.respond("# This mogi has been closed.")

        await ctx.respond("Canceled")

    @debug.command(name="votes", description="check the votes for the current mogi")
    @is_moderator()
    async def votes(self, ctx: MogiApplicationContext):
        votes_str = "\n".join(
            [
                f"{format}: {amount}"
                for format, amount in ctx.mogi.votes.items()
                if amount > 0
            ]
        )
        await ctx.respond(f"Votes: \n{votes_str}", ephemeral=True)

    @debug.command(name="list_mogis", description="print the mogi registry")
    @is_admin()
    async def all_mogis(self, ctx: MogiApplicationContext):
        await ctx.respond(
            f"There are currently {len(mogi_manager.read_registry())} mogis:\n"
            + "\n".join(
                f"<#{mogi.channel_id}>: {len(mogi.players)} | {mogi.format}"
                for mogi in mogi_manager.read_registry().values()
            )
        )

    @debug.command(name="set_server", description="chose the yuzu server for the current mogi")
    @is_admin()
    async def set_server(self, ctx: MogiApplicationContext, server = Option(
        str,
        name="server",
        required=True,
        choices=[room['name'] for room in ROOMS],
        ),
    ):
        server = [room for room in ROOMS if room['name'] == server][0]
        room_obj = Room.from_address(server['address'], server['port'])
        ctx.mogi.room = room_obj
        await ctx.respond(f"Set the server to:\n{server}")
        await ctx.send(room_obj)

    """ @debug.command(name="test_player", description="add a dummy player to the mogi")
    @is_mogi_not_in_progress()
    @is_admin()
    async def test_player(self, ctx: MogiApplicationContext):

        dummy_names = ["spamton", "jordan", "mrboost", "bruv"]
        dummy: PlayerProfile = PlayerProfile(
            _id=ObjectId("0123456789ab0123456789ab"),
            name=f"{random.choice(dummy_names)}{str(random.randint(10, 99))}",
            mmr=random.randint(1000, 6000),
            discord_id=000000000000000000,
            history=[],
        )
        ctx.mogi.players.append(dummy)
        await ctx.respond(f"Added {dummy.name} to the mogi") """

    @debug.command(name="load_state", description="Load state")
    @is_admin()
    async def load_state(self, ctx: MogiApplicationContext):
        state_manager.load_saved()
        await ctx.respond("State loaded")

    @debug.command(name="inmogi")
    async def inmogi(self, ctx: MogiApplicationContext):
        await ctx.respond(
            f"<@&{ctx.inmogi_role.id}>", allowed_mentions=AllowedMentions(roles=True)
        )

    @debug.command(name="perms", description="perms test")
    @is_admin()
    async def perms(self, ctx: MogiApplicationContext):
        await ctx.respond(
            f"Your perms: {ctx.author.guild_permissions.value}"
            f"Admin role: {ctx.get_lounge_role('Admin').permissions.value}"
            f"Moderator role: {ctx.get_lounge_role('Moderator').permissions.value}"
            f"Mogi Manager role: {ctx.get_lounge_role('Mogi Manager').permissions.value}"
        )

    @debug.command(name="player_cap", description="change the player cap")
    @is_mogi_manager()
    async def player_cap(
        self, ctx: MogiApplicationContext, cap: int = Option(int, "The new player cap")
    ):
        ctx.mogi.player_cap = cap
        await ctx.respond(
            f"Updated the player cap for this mogi to {ctx.mogi.player_cap}"
        )


def setup(bot: commands.Bot):
    bot.add_cog(debugging(bot))
