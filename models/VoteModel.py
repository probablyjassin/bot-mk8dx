from dataclasses import dataclass
from typing import Callable, TYPE_CHECKING
from contextlib import asynccontextmanager

from config import FORMATS

if TYPE_CHECKING:
    from models.MogiModel import Mogi

@dataclass
class Vote:

    is_active: bool = False
    voting_message_id: int | None = None
    voters: set = set()
    votes: dict[str, int] = {format: 0 for format in FORMATS}
    result: str | None = None

    _setup_handlers = []
    _cleanup_handlers = []
        
        
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
    
    async def vote_format(self, mogi: "Mogi", user_id: int, format_choice: str) -> bool:
        """Cast a vote for a specific format"""
        if not self.is_active:
            return False

        # Check if user already voted
        if user_id in self.voters:
            return False
            
        # Check if user is in the mogi
        if user_id not in [player.discord_id for player in mogi.players]:
            return False
            
        # Check if format is valid for current player count
        format_int = self._get_format_int(format_choice)
        if not self._is_valid_format(format_int):
            return False
            
        # Cast the vote
        self.voters.add(user_id)
        self.votes[format_choice.lower()] += 1
        
        # Check if vote should end
        if await self._should_end(mogi):
            winning_format = self._get_winning_format()
            await self.end(winning_format=winning_format)
            return True
            
        return True
    
    async def end(self, winning_format: str = None):
        """End the vote session"""
        if not self.is_active:
            return
            
        self.is_active = False
        self.result = winning_format
        
        # ALWAYS run cleanup handlers, no matter how the vote ends
        for handler in self._cleanup_handlers:
            try:
                await handler()
            except Exception as e:
                print(f"Cleanup handler failed: {e}")
    
    async def _should_end(self, mogi: "Mogi") -> bool:
        """Check if vote should end early"""
        # If everyone has voted
        if len(self.voters) >= len(mogi.players):
            return True
            
        # If one format has more votes than possible remaining votes can overcome
        max_votes = max(self.votes.values())
        remaining_voters = len(mogi.players) - len(self.voters)
        second_highest = sorted(self.votes.values(), reverse=True)[1] if len([v for v in self.votes.values() if v > 0]) > 1 else 0
        
        # If the leading format can't be caught
        return max_votes > (second_highest + remaining_voters)
    
    def _get_winning_format(self) -> str:
        """Get the format with the most votes"""
        if not any(self.votes.values()):
            return "ffa"  # Default if no votes
            
        max_votes = max(self.votes.values())
        winners = [format_name for format_name, votes in self.votes.items() if votes == max_votes]
        
        if len(winners) == 1:
            return winners[0]
        else:
            # Handle tie - could be random or have a priority order
            import random
            return random.choice(winners)
    
    def _get_format_int(self, format_choice: str) -> int:
        """Convert format string to integer"""
        format_lower = format_choice.lower()
        if format_lower == "ffa":
            return 1
        elif format_lower[0].isdigit():
            return int(format_lower[0])
        return 1
    
    def _is_valid_format(self, format_int: int) -> bool:
        """Check if format is valid for current player count"""
        player_count = len(self.mogi.players)
        
        # Must have enough players and player count must be divisible by format
        return player_count >= format_int and player_count % format_int == 0
    
    def get_vote_status(self) -> str:
        """Get current vote status as a string"""
        if not self.is_active:
            return "Vote not active"
            
        status = "Current votes:\n"
        for format_name, vote_count in self.votes.items():
            if vote_count > 0:
                status += f"{format_name.upper()}: {vote_count}\n"
        
        voted_count = len(self.voters)
        total_players = len(self.mogi.players)
        status += f"\nVoted: {voted_count}/{total_players}"
        
        return status
    
    def to_json(self) -> dict:
        """Convert vote to JSON-serializable dictionary"""
        return {
            "voting_message_id": self.voting_message_id,
            "is_active": self.is_active,
            "voters": list(self.voters),  # Convert set to list for JSON serialization
            "votes": self.votes.copy(),   # Copy to avoid modifying original
            "result": self.result
        }
    
    @classmethod
    def from_json(cls, data: dict) -> "Vote":
        """Create Vote instance from JSON data"""
        vote = cls()
        vote.voting_message_id = data.get("voting_message_id")
        vote.is_active = data.get("is_active", False)
        vote.voters = set(data.get("voters", []))  # Convert list back to set
        vote.votes = data.get("votes", {format: 0 for format in FORMATS})
        vote.result = data.get("result")
        return vote

    @asynccontextmanager
    async def session(self):
        """Context manager for automatic cleanup"""
        try:
            await self.start()
            yield self
        finally:
            await self.end()