import asyncio
from models import MogiApplicationContext


async def confirmation(ctx: MogiApplicationContext, text: str) -> bool:
    """
    Sends a confirmation message and waits for the user to react with a checkmark or X.

    :param ctx: The context of the command.
    :param text: The custom text to display in the confirmation message.
    :return: True if the user confirms, False otherwise.
    """
    message = await ctx.send(text)
    await message.add_reaction("✅")
    await message.add_reaction("❌")

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ["✅", "❌"]

    try:
        reaction, user = await ctx.bot.wait_for(
            "reaction_add", timeout=60.0, check=check
        )
        if str(reaction.emoji) == "✅":
            return True
        else:
            return False
    except asyncio.TimeoutError:
        await ctx.send("Confirmation timed out.")
        return False
