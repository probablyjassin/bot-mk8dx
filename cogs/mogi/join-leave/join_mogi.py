import asyncio
from discord import slash_command, ApplicationContext
from discord.utils import get
from discord.ext import commands
from utils.data.mogi_manager import get_mogi
from models.MogiModel import Mogi
from models.PlayerModel import PlayerProfile
from utils.data.database import db_players, db_archived
from config import GUILD_IDS
from bson.int64 import Int64

class join_mogi(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.join_semaphore = asyncio.Semaphore(1)

    # TODO: Add inmogi role on join

    @slash_command(name="join", description="Join this mogi")
    async def join(self, ctx: ApplicationContext):
        async with self.join_semaphore:
            mogi: Mogi = get_mogi(ctx.channel.id)
            # check if mogi open
            if not mogi:
                return await ctx.respond("There is no mogi open in this channel.")
            # check if player already in mogi
            if [player for player in mogi.players if player.discord_id == ctx.author.id]:
                return await ctx.respond("You're already in this mogi.")
            # check if mogi full
            if len(mogi.players) >= mogi.player_cap:
                return await ctx.respond("This mogi is full.")
            # check if mogi is in progress
            if mogi.isPlaying or mogi.isVoting:
                return await ctx.respond("This mogi has already started.")

            # fetch player record
            player_entry = db_players.find_one({"discord_id": Int64(ctx.author.id)})
            # if not found
            if not player_entry:
                if db_archived.find_one({"discord_id": Int64(ctx.author.id)}):
                    return await ctx.respond("You're in Lounge but archived. Contact a mod to get unarchived.")
                return await ctx.respond("You're not registered for Lounge.")
            
            # assign Player object
            player: PlayerProfile = PlayerProfile(**player_entry)
            
            # if suspended
            if player.suspended:
                return await ctx.respond("You're temporarily inable to join mogis.")
            
            mogi.players.append(player)
            await ctx.user.add_roles(get(ctx.guild.roles, name="InMogi"))
            await ctx.respond(f"{ctx.author.mention} has joined the mogi!\n{len(mogi.players)} players are in!")

def setup(bot: commands.Bot):
    bot.add_cog(join_mogi(bot))
