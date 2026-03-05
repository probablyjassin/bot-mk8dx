from dataclasses import dataclass, field
from typing import Callable, TYPE_CHECKING
import asyncio

from config import FORMATS

if TYPE_CHECKING:
    from models import Mogi


@dataclass
class Vote:

    is_active: bool = False
    voting_message_id: int | None = None
    voters: set = field(default_factory=lambda: set())
    votes: dict[str, int] = field(
        default_factory=lambda: {"mini": 0, **{format: 0 for format in FORMATS}}
    )
    user_votes: dict = field(default_factory=dict)  # user_id -> voted format key

    result: str | None = None
    _vote_lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    _setup_handlers: list[Callable] = field(default_factory=lambda: [])
    _cleanup_handlers: list[Callable] = field(default_factory=lambda: [])

    def add_setup_handler(self, handler: Callable):
        """Add a handler to run when vote starts"""
        self._setup_handlers.append(handler)

    def add_cleanup_handler(self, handler: Callable):
        """Add a handler to run when vote ends (regardless of how it ends)"""
        self._cleanup_handlers.append(handler)

    async def start(self):
        """Start the vote session"""
        if self.is_active:
            return False

        self.is_active = True

        # Run setup handlers
        for handler in self._setup_handlers:
            try:
                await handler()
            except Exception as e:
                print(f"Setup handler failed: {e}")

        return True

    async def cast_vote_format(self, mogi: "Mogi", user_id: int, choice: str) -> bool:
        """Cast or change a vote for a specific format"""
        async with self._vote_lock:
            if not self.is_active:
                return False

            # Check if user is in the mogi
            if user_id not in [player.discord_id for player in mogi.players]:
                return False

            # Check if format is valid for current player count
            format_int = self._get_format_int(choice)
            if not self._is_valid_format(mogi, format_int):
                return False

            prev_choice = self.user_votes.get(user_id)

            # Same vote — no-op
            if prev_choice == choice:
                return False

            # Undo previous vote if the user had one
            if user_id in self.voters and prev_choice and prev_choice in self.votes:
                self.votes[prev_choice] -= 1
            elif user_id not in self.voters:
                self.voters.add(user_id)

            # Cast the new vote
            self.votes[choice] += 1
            self.user_votes[user_id] = choice

            # Check if vote should end
            if await self._should_end(mogi):
                winning_format, tied_formats = self._get_winning_format()
                await self.end(
                    mogi, winning_format=winning_format, tied_formats=tied_formats
                )
                return True

            return True

    async def cast_vote_extra(self, mogi: "Mogi", user_id: int, choice: str) -> bool:
        async with self._vote_lock:  # Lock this too
            if not self.is_active:
                return False

            # Check if user is in the mogi
            if user_id not in [player.discord_id for player in mogi.players]:
                return False

            # Handle Mini Mogi vote
            if choice == "Mini":
                prev_choice = self.user_votes.get(user_id)

                # Same vote — no-op
                if prev_choice == "mini":
                    return False

                # Undo previous format vote if any
                if user_id in self.voters and prev_choice and prev_choice in self.votes:
                    self.votes[prev_choice] -= 1
                elif user_id not in self.voters:
                    self.voters.add(user_id)

                self.votes["mini"] += 1
                self.user_votes[user_id] = "mini"

                if await self._should_end(mogi):
                    winning_format, tied_formats = self._get_winning_format()
                    await self.end(
                        mogi, winning_format=winning_format, tied_formats=tied_formats
                    )
                return True

    async def end(
        self, mogi: "Mogi", winning_format: str = None, tied_formats: list[str] = None
    ):
        """End the vote session"""
        if not self.is_active:
            return

        self.is_active = False
        self.result = winning_format

        if winning_format == "mini":
            mogi.is_mini = True

        # ALWAYS run cleanup handlers, no matter how the vote ends
        for handler in self._cleanup_handlers:
            try:
                await handler(winning_format, tied_formats)
            except Exception as e:
                print(f"Cleanup handler failed: {e}")

        # VoteModel instance deletes itself
        mogi.vote = None

    async def _should_end(self, mogi: "Mogi") -> bool:
        """Check if vote should end early"""
        # If everyone has voted
        if len(self.voters) >= len(mogi.players):
            return True

        # If one format has more votes than possible remaining votes can overcome
        max_votes = max(self.votes.values())
        remaining_voters = len(mogi.players) - len(self.voters)
        second_highest = (
            sorted(self.votes.values(), reverse=True)[1]
            if len([v for v in self.votes.values() if v > 0]) > 1
            else 0
        )

        # If the leading format can't be caught
        return max_votes > (second_highest + remaining_voters)

    def _get_winning_format(self) -> tuple[str, list[str] | None]:
        """Get the format with the most votes. Returns (winning_format, tied_formats or None)"""
        if not any(self.votes.values()):
            return "ffa", None  # Default if no votes

        max_votes = max(self.votes.values())
        winners = [
            format_name
            for format_name, votes in self.votes.items()
            if votes == max_votes
        ]

        if len(winners) == 1:
            return winners[0], None
        else:
            # Handle tie - random selection
            import random

            return random.choice(winners), winners

    def _get_format_int(self, format_choice: str) -> int:
        """Convert format string to integer"""
        format_lower = format_choice.lower()
        if format_lower in ["ffa", "mini"]:
            return 1
        elif format_lower[0].isdigit():
            return int(format_lower[0])
        return 1

    def _is_valid_format(self, mogi: "Mogi", format_int: int) -> bool:
        """Check if format is valid for current player count"""
        player_count = len(mogi.players)

        # Must have enough players and player count must be divisible by format
        return player_count >= format_int and player_count % format_int == 0

    def get_vote_status(self, mogi: "Mogi") -> str:
        """Get current vote status as a string"""
        if not self.is_active:
            return "Vote not active"

        status = "Current votes:\n"
        for format_name, vote_count in self.votes.items():
            if vote_count > 0:
                status += f"{format_name.upper()}: {vote_count}\n"

        voted_count = len(self.voters)
        total_players = len(mogi.players)
        status += f"\nVoted: {voted_count}/{total_players}"

        return status

    def to_json(self) -> dict:
        """Convert vote to JSON-serializable dictionary"""
        return {
            "voting_message_id": self.voting_message_id,
            "is_active": self.is_active,
            "voters": list(self.voters),
            "votes": self.votes.copy(),
            "user_votes": {str(k): v for k, v in self.user_votes.items()},
            "result": self.result,
        }

    @classmethod
    def from_json(cls, data: dict | None) -> "Vote":
        """Create Vote instance from JSON data"""
        if not data:
            return None
        vote = cls()
        vote.voting_message_id = data.get("voting_message_id", None)
        vote.is_active = data.get("is_active", False)
        vote.voters = set(data.get("voters", []))
        vote.votes = data.get("votes", {format: 0 for format in FORMATS})
        vote.user_votes = {int(k): v for k, v in data.get("user_votes", {}).items()}
        vote.result = data.get("result", None)
        return vote
