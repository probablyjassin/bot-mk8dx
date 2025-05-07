from discord import Embed, Color


def create_embed(
    title: str,
    description: str,
    thumbnail: str = None,
    fields: dict = None,
    footer: dict = None,
    color: Color = Color.blue(),
    inline: bool = True,
) -> Embed:
    embed = Embed(title=title, description=description, color=color)
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    if fields:
        for name, value in fields.items():
            embed.add_field(name=name, value=value, inline=inline)
    if footer:
        embed.set_footer(text=footer["text"], icon_url=footer["icon_url"])
    return embed
