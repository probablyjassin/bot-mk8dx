import asyncio
from discord import Reaction, User
from models.CustomMogiContext import MogiApplicationContext


async def confirmation(
    ctx: MogiApplicationContext, text: str, user_id: int | None = None
) -> bool:
    """
    Sends a confirmation message and waits for the user to react with a checkmark or X.

    :param ctx: The context of the command.
    :param text: The custom text to display in the confirmation message.
    :return: True if the user confirms, False otherwise.
    """
    message = await ctx.send(text)
    await message.add_reaction("✅")
    await message.add_reaction("❌")

    def check(reaction: Reaction, user: User):
        return user.id == (user_id if user_id else ctx.author.id) and str(
            reaction.emoji
        ) in ["✅", "❌"]

    try:
        reaction, _ = await ctx.bot.wait_for("reaction_add", timeout=60.0, check=check)
        if str(reaction.emoji) == "✅":
            return True
        else:
            return False
    except asyncio.TimeoutError:
        await ctx.send("Confirmation timed out.")
        return False
