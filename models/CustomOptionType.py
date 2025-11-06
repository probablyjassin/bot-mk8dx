from typing import Optional

from discord import Option

from models.CustomMogiContext import MogiApplicationContext
from utils.decorators.checks import _is_at_least_role, LoungeRole


class RestrictedOption(Option):
    """Option that requires a minimum role to use."""

    def __init__(self, *args, required_role: Optional[LoungeRole] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_role = required_role

    async def validate(self, ctx: MogiApplicationContext, value):
        if value and self.required_role:
            if not _is_at_least_role(ctx, self.required_role):
                return await ctx.respond(
                    f"You don't have permission to use the `{self.name}` option"
                )
        return await super().validate(ctx, value)
