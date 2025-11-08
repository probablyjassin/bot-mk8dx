import os, io, json
from pathlib import Path
from datetime import datetime, timedelta

from config import ROOMS_CONFIG, LOG_CHANNEL_ID

from discord import SlashCommandGroup, Option, AllowedMentions, File
from discord.ext import commands

from models import MogiApplicationContext, Room

from utils.database.types import archive_type

from utils.data import mogi_manager, state_manager, data_manager
from utils.command_helpers import confirmation
from utils.decorators import (
    is_admin,
    is_moderator,
    is_mogi_manager,
)

ROOMS: list[Room] = [
    Room.from_address(room["address"], room["port"]) for room in ROOMS_CONFIG
]

from utils.command_helpers import fetch_server_passwords


class debug(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    debug = SlashCommandGroup(name="debug", description="Debugging commands")

    @debug.command(
        name="restart",
        description="Places a flag on the system to restart, for a custom watchdog to use.",
    )
    @is_admin()
    async def restart(self, ctx: MogiApplicationContext):
        for mogi in mogi_manager.read_registry().values():
            if mogi.vote:
                return await ctx.respond(
                    "At least one mogi is voting right now. Not restarting to not interrupt it."
                )
        Path("state/restart.flag").touch()
        await ctx.respond(
            "Requested a bot restart. If a watchdog is configured, it will soon recieve the signal..."
        )

    @debug.command(name="db_backup")
    @is_admin()
    async def db_backup(
        self,
        ctx: MogiApplicationContext,
        filename: str = Option(
            str, "The Filename to save as | FILE WON'T GET AUTODELETED", required=False
        ),
    ):
        backup_folder = "backups"
        date_format = "%d-%m-%Y"

        os.makedirs(backup_folder, exist_ok=True)

        # Create the backup file
        backup_filename = filename or os.path.join(
            backup_folder, f"backup_{datetime.now().strftime(date_format)}.json"
        )
        backup_data = {
            "players": data_manager.Players.get_profiles(
                archive=archive_type.INCLUDE, with_id=False, as_json=True
            ),
            "mogis": await data_manager.Mogis.get_all_mogis(
                with_id=False, as_json=True
            ),
        }

        with open(backup_filename, "w") as backup_file:
            json.dump(backup_data, backup_file, indent=4)

        # Remove backups older than 3 days
        for filename in os.listdir(backup_folder):
            file_path = os.path.join(backup_folder, filename)
            if os.path.isfile(file_path):
                file_date_str = filename.split("_")[1].split(".")[0]
                file_date = datetime.strptime(file_date_str, date_format)
                if datetime.now() - file_date > timedelta(days=3):
                    os.remove(file_path)

        try:
            log_channel = await self.bot.fetch_channel(LOG_CHANNEL_ID)
            await log_channel.send(
                f"💾 Database backup saved to `{backup_filename.split('/')[-1]}`"
            )
            await ctx.respond(
                f"💾 Database backup saved to `{backup_filename.split('/')[-1]}`"
            )
        except Exception as e:
            print(f"Error sending database backup log: {e}")
            await ctx.respond(e)

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
                for format, amount in ctx.mogi.vote.votes.items()
                if amount > 0
            ]
        )
        votes_str += f"\n Amount of Random Teams votes: {ctx.mogi.vote.extras['random_teams_votes']}\n"
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

    @debug.command(
        name="set_server", description="chose the yuzu server for the current mogi"
    )
    @is_admin()
    async def set_server(
        self,
        ctx: MogiApplicationContext,
        server=Option(
            str,
            name="server",
            required=True,
            choices=[room["name"] for room in ROOMS_CONFIG],
        ),
    ):
        available_rooms = ROOMS[:]
        for mogi in mogi_manager.read_registry().values():
            if mogi.room and mogi.room in available_rooms:
                available_rooms.remove(mogi.room)
        candidates = [room for room in available_rooms if room.name == server]
        room = candidates[0] if candidates else None
        if not room:
            return await ctx.respond("The room is not available right now")
        ctx.mogi.room = room
        await ctx.respond(f"Set the server to:\n{room.name}")
        await ctx.send(room)

    @debug.command(name="list_servers")
    @is_admin()
    async def list_servers(self, ctx: MogiApplicationContext):
        await ctx.defer()
        rooms: list[Room] = [
            Room.from_address(room["address"], room["port"]) for room in ROOMS_CONFIG
        ]
        msg = ""
        for room in rooms:
            msg += f"{room.name}\n"
        await ctx.respond(msg)

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
        state_manager.load_manual_saved()
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

    @debug.command(
        name="update_passwords",
        description="Refresh the lounge passwords from the provided API endpoint",
    )
    @is_admin()
    async def update_passwords(self, ctx: MogiApplicationContext):
        await fetch_server_passwords(self.bot)
        await ctx.respond(f"Done, check <#{LOG_CHANNEL_ID}>")

    @debug.command(name="locale", description="print ctx.locale")
    async def locale(self, ctx: MogiApplicationContext):
        await ctx.respond(ctx.locale)


def setup(bot: commands.Bot):
    bot.add_cog(debug(bot))
