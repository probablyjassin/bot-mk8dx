import asyncio

from discord import SelectOption
from discord.ui import Select, View


class VerificationSelect(Select):
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.correct_answer = "I read everything"
        self.result = None
        self.answered = asyncio.Event()

        options = [
            SelectOption(label="I Understand", value="I Understand"),
            SelectOption(
                label="I agree with the information",
                value="I agree with the information",
            ),
            SelectOption(label="I read all the rules", value="I read all the rules"),
            SelectOption(label="I read everything", value="I read everything"),
            SelectOption(
                label="I comply with everything", value="I comply with everything"
            ),
        ]

        super().__init__(
            placeholder="Please answer correctly",
            options=options,
            min_values=1,
            max_values=1,
        )

    async def callback(self, interaction):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message(
                "This verification is not for you.", ephemeral=True
            )

        # Set result based on answer
        self.result = self.values[0] == self.correct_answer

        # Acknowledge the interaction without sending a message
        await interaction.response.defer(ephemeral=True)

        # Signal that an answer was given
        self.answered.set()


class VerificationView(View):
    def __init__(self, user_id: int):
        super().__init__(timeout=300)
        self.select = VerificationSelect(user_id)
        self.add_item(self.select)

    async def wait_for_answer(self):
        """Wait for user to answer and return True/False"""
        try:
            await asyncio.wait_for(self.select.answered.wait(), timeout=300)
            return self.select.result
        except asyncio.TimeoutError:
            return False
