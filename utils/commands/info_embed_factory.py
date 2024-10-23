from discord import Embed, Color

def create_embed(
    title: str, 
    description: str, 
    fields: dict, 
    color: Color = Color.blue()
) -> Embed:
    embed = Embed(
        title=title,
        description=description,
        color=color
    )
    for name, value in fields.items():
        embed.add_field(name=name, value=value, inline=False)
    return embed