import discord
from discord import slash_command, ApplicationContext
from discord.utils import get
from discord.ext import commands
from utils.database import db_players, db_archived
from utils.objects import get_register_channel, get_lounge_role

class register(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @slash_command(name="register", description="Register for playing in Lounge")
    async def register(self, ctx: ApplicationContext):
        await ctx.interaction.response.defer()

        existingPlayer = db_players.find_one({"discord_id": ctx.author.id}) | db_archived.find_one({"discord_id": ctx.author.id})
        if existingPlayer:
            return await ctx.respond("You are already registered for Lounge.\nIf your Profile is archived or you're missing the Lounge roles due to rejoining the server, contact a moderator.", ephemeral=True)
        
        username = "".join(
            e for e in ctx.interaction.user.display_name.lower() if e.isalnum()
        )
        if username == "":
            username = ctx.interaction.user.name.lower()

        if self.players.find_one({"name": username}):
            return await ctx.respond(
                "This username is already taken. Try changing your server-nickname or ask a moderator.",
                ephemeral=True,
            )

        role = get(ctx.guild.roles, name="Lounge Player")
        member: discord.Member = ctx.user
        if role in member.roles:
            return await ctx.respond(
                "You already have the Lounge Player role even though you don't have a player role. Please ask a moderator.",
                ephemeral=True,
            )
        try:
            self.players.insert_one(
                {
                    "name": username,
                    "mmr": 2000,
                    "wins": 0,
                    "losses": 0,
                    "discord": str(member.id),
                    "joined": round(time.time()),
                    "history": [],
                },
            )
        except:
            return await ctx.respond(
                "Some error occured creating your player record. Please ask a moderator.",
                ephemeral=True,
            )
        await member.add_roles(get(ctx.guild.roles, name="Lounge Player"))
        await member.add_roles(get(ctx.guild.roles, name="Lounge - Silver"))
        await ctx.respond(
            f"{member.mention} is now registered for Lounge as {username}\n You can view your profile at https://mk8dx-yuzu.github.io/{username}",
            ephemeral=True,
        )


def setup(bot: commands.Bot):
    bot.add_cog(register(bot))
