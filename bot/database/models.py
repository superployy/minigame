from sqlalchemy import Column, Integer, String, DateTime, BigInteger, Boolean
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime


class Base(DeclarativeBase):
    pass


class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, autoincrement=True)
    discord_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String(100), nullable=False)
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    draws = Column(Integer, default=0)
    rps_wins = Column(Integer, default=0)
    ttt_wins = Column(Integer, default=0)
    trivia_wins = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def total_games(self):
        return self.wins + self.losses + self.draws

    @property
    def win_rate(self):
        if self.total_games == 0:
            return 0.0
        return round((self.wins / self.total_games) * 100, 1)


class GuildSettings(Base):
    __tablename__ = "guild_settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, unique=True, nullable=False)
    prefix = Column(String(10), default="!")
    game_channel_id = Column(BigInteger, nullable=True)
    rps_enabled = Column(Boolean, default=True)
    ttt_enabled = Column(Boolean, default=True)
    trivia_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class GameHistory(Base):
    __tablename__ = "game_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    game_type = Column(String(30), nullable=False)
    guild_id = Column(BigInteger, nullable=False)
    winner_id = Column(BigInteger, nullable=True)
    loser_id = Column(BigInteger, nullable=True)
    result = Column(String(10), nullable=False)  # win/draw
    played_at = Column(DateTime, default=datetime.utcnow)
