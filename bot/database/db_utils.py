import os
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select, update
from .models import Base, Player, GuildSettings, GameHistory

logger = logging.getLogger(__name__)

engine = None
AsyncSessionLocal = None


async def init_db():
    """Initialize the database connection and create tables."""
    global engine, AsyncSessionLocal

    db_url = os.getenv("DATABASE_URL", "")
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif not db_url:
        raise ValueError("DATABASE_URL environment variable not set.")

    engine = create_async_engine(db_url, echo=False, pool_pre_ping=True)
    AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Database initialized successfully.")


async def get_or_create_player(discord_id: int, username: str) -> Player:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Player).where(Player.discord_id == discord_id))
        player = result.scalar_one_or_none()
        if not player:
            player = Player(discord_id=discord_id, username=username)
            session.add(player)
            await session.commit()
            await session.refresh(player)
        else:
            # Update username if changed
            if player.username != username:
                player.username = username
                await session.commit()
        return player


async def update_player_stats(discord_id: int, result: str, game_type: str):
    """
    result: 'win', 'loss', 'draw'
    game_type: 'rps', 'ttt', 'trivia'
    """
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(Player).where(Player.discord_id == discord_id))
        player = res.scalar_one_or_none()
        if not player:
            return

        if result == "win":
            player.wins += 1
            if game_type == "rps":
                player.rps_wins += 1
            elif game_type == "ttt":
                player.ttt_wins += 1
            elif game_type == "trivia":
                player.trivia_wins += 1
        elif result == "loss":
            player.losses += 1
        elif result == "draw":
            player.draws += 1

        await session.commit()


async def log_game(game_type: str, guild_id: int, winner_id: int | None,
                   loser_id: int | None, result: str):
    async with AsyncSessionLocal() as session:
        game = GameHistory(
            game_type=game_type,
            guild_id=guild_id,
            winner_id=winner_id,
            loser_id=loser_id,
            result=result,
        )
        session.add(game)
        await session.commit()


async def get_leaderboard(limit: int = 10) -> list[Player]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Player).order_by(Player.wins.desc()).limit(limit)
        )
        return result.scalars().all()


async def get_or_create_guild(guild_id: int) -> GuildSettings:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(GuildSettings).where(GuildSettings.guild_id == guild_id)
        )
        guild = result.scalar_one_or_none()
        if not guild:
            guild = GuildSettings(guild_id=guild_id)
            session.add(guild)
            await session.commit()
            await session.refresh(guild)
        return guild


async def update_guild_settings(guild_id: int, **kwargs):
    async with AsyncSessionLocal() as session:
        await session.execute(
            update(GuildSettings).where(GuildSettings.guild_id == guild_id).values(**kwargs)
        )
        await session.commit()
