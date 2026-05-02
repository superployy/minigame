import asyncio
from dataclasses import dataclass, field
from typing import Optional
import discord


@dataclass
class GameSession:
    game_type: str
    player1: discord.Member
    player2: discord.Member
    guild_id: int
    channel_id: int
    data: dict = field(default_factory=dict)


class MatchmakingManager:
    """
    Manages active challenges and game sessions.
    Challenges expire after 60 seconds if not accepted.
    """

    def __init__(self):
        # challenge_key → {challenger, challenged, game_type, task}
        self._pending: dict[str, dict] = {}
        # session_key → GameSession
        self._sessions: dict[str, GameSession] = {}

    def _challenge_key(self, challenger_id: int, challenged_id: int, guild_id: int) -> str:
        return f"{guild_id}:{challenger_id}:{challenged_id}"

    def _session_key(self, p1_id: int, p2_id: int, guild_id: int) -> str:
        return f"sess:{guild_id}:{min(p1_id, p2_id)}:{max(p1_id, p2_id)}"

    def add_challenge(self, challenger: discord.Member, challenged: discord.Member,
                      game_type: str, expire_callback=None) -> bool:
        """Returns False if a challenge already exists between these users."""
        key = self._challenge_key(challenger.id, challenged.id, challenger.guild.id)
        if key in self._pending:
            return False
        self._pending[key] = {
            "challenger": challenger,
            "challenged": challenged,
            "game_type": game_type,
        }
        if expire_callback:
            task = asyncio.create_task(self._expire(key, expire_callback))
            self._pending[key]["task"] = task
        return True

    async def _expire(self, key: str, callback):
        await asyncio.sleep(60)
        if key in self._pending:
            data = self._pending.pop(key)
            await callback(data)

    def accept_challenge(self, challenger_id: int, challenged_id: int,
                         guild_id: int) -> Optional[dict]:
        key = self._challenge_key(challenger_id, challenged_id, guild_id)
        data = self._pending.pop(key, None)
        if data and "task" in data:
            data["task"].cancel()
        return data

    def decline_challenge(self, challenger_id: int, challenged_id: int, guild_id: int) -> bool:
        key = self._challenge_key(challenger_id, challenged_id, guild_id)
        data = self._pending.pop(key, None)
        if data and "task" in data:
            data["task"].cancel()
        return data is not None

    def start_session(self, session: GameSession):
        key = self._session_key(session.player1.id, session.player2.id, session.guild_id)
        self._sessions[key] = session

    def get_session(self, p1_id: int, p2_id: int, guild_id: int) -> Optional[GameSession]:
        key = self._session_key(p1_id, p2_id, guild_id)
        return self._sessions.get(key)

    def end_session(self, p1_id: int, p2_id: int, guild_id: int):
        key = self._session_key(p1_id, p2_id, guild_id)
        self._sessions.pop(key, None)

    def is_in_game(self, user_id: int, guild_id: int) -> bool:
        for key, sess in self._sessions.items():
            if key.startswith(f"sess:{guild_id}:"):
                if sess.player1.id == user_id or sess.player2.id == user_id:
                    return True
        return False


# Global singleton
matchmaking = MatchmakingManager()
