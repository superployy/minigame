import os
import asyncio
import logging
import discord
from discord.ext import commands
from dotenv import load_dotenv
from database.db_utils import init_db, get_or_create_guild

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("MiniGamesBot")

COGS = [
    "cogs.general",
    "cogs.admin",
    "cogs.games.rock_paper_scissors",
    "cogs.games.tic_tac_toe",
    "cogs.games.trivia",
]

DEFAULT_PREFIX = os.getenv("PREFIX", "!")


async def get_prefix(bot: "MiniGamesBot", message: discord.Message) -> str:
    if not message.guild:
        return DEFAULT_PREFIX
    guild_id = message.guild.id
    if guild_id in bot.command_prefix_map:
        return bot.command_prefix_map[guild_id]
    # Fetch from DB
    try:
        guild = await get_or_create_guild(guild_id)
        prefix = guild.prefix or DEFAULT_PREFIX
        bot.command_prefix_map[guild_id] = prefix
        return prefix
    except Exception:
        return DEFAULT_PREFIX


class MiniGamesBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(
            command_prefix=get_prefix,
            intents=intents,
            help_command=None,   # Custom help command in general cog
            description="A Discord Mini-Games PvP Bot",
        )
        self.command_prefix_map: dict[int, str] = {}

    async def setup_hook(self):
        logger.info("Initializing database...")
        await init_db()

        for cog in COGS:
            try:
                await self.load_extension(cog)
                logger.info(f"✅ Loaded cog: {cog}")
            except Exception as e:
                logger.error(f"❌ Failed to load cog {cog}: {e}")

    async def on_ready(self):
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        await self.change_presence(
            activity=discord.Game(name="Mini Games | !help")
        )
        logger.info(f"Serving {len(self.guilds)} guild(s).")

    async def on_guild_join(self, guild: discord.Guild):
        logger.info(f"Joined guild: {guild.name} (ID: {guild.id})")
        await get_or_create_guild(guild.id)

    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.CommandNotFound):
            return
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send("This command can only be used in a server.")
            return
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏳ Slow down! Try again in {error.retry_after:.1f}s.")
            return
        # Log unexpected errors
        logger.error(f"Unhandled command error in {ctx.command}: {error}", exc_info=error)


async def main():
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        logger.critical("DISCORD_TOKEN environment variable is not set. Exiting.")
        return

    bot = MiniGamesBot()
    async with bot:
        await bot.start(token)


if __name__ == "__main__":
    asyncio.run(main())
