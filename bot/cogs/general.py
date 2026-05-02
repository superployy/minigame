import discord
from discord.ext import commands
# Fix the imports - remove 'bot.' prefix
from utils.embeds import base_embed, leaderboard_embed, game_embed, error_embed
from database.db_utils import get_or_create_player, get_leaderboard


class General(commands.Cog, name="General"):
    """General commands: help, stats, leaderboard."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="help", aliases=["h"])
    async def help_cmd(self, ctx: commands.Context):
        """Show all available commands."""
        embed = base_embed(
            "🎮 Mini Games Bot — Help",
            "A Discord bot with fun PvP mini-games!\n\u200b",
            "info"
        )
        prefix = ctx.prefix or "!"
        embed.add_field(
            name="🎯 Games",
            value=(
                f"`{prefix}rps @user` — Rock Paper Scissors\n"
                f"`{prefix}ttt @user` — Tic-Tac-Toe\n"
                f"`{prefix}trivia @user [rounds]` — Trivia Quiz (default 5 rounds)"
            ),
            inline=False,
        )
        embed.add_field(
            name="📊 Stats",
            value=(
                f"`{prefix}stats [@user]` — View win/loss stats\n"
                f"`{prefix}leaderboard` — Global leaderboard\n"
                f"`{prefix}lb` — Shortcut for leaderboard"
            ),
            inline=False,
        )
        embed.add_field(
            name="⚙️ Admin",
            value=(
                f"`{prefix}setprefix <prefix>` — Change command prefix\n"
                f"`{prefix}setgamechannel [#channel]` — Restrict games to a channel\n"
                f"`{prefix}togglegame <rps|ttt|trivia>` — Enable/disable games\n"
                f"`{prefix}serversettings` — View current server settings"
            ),
            inline=False,
        )
        embed.add_field(
            name="ℹ️ Info",
            value=(
                f"`{prefix}ping` — Check bot latency\n"
                f"`{prefix}help` — This menu"
            ),
            inline=False,
        )
        await ctx.send(embed=embed)

    @commands.command(name="stats")
    @commands.guild_only()
    async def stats(self, ctx: commands.Context, member: discord.Member = None):
        """View your (or another player's) stats. Usage: !stats [@user]"""
        target = member or ctx.author
        player = await get_or_create_player(target.id, target.display_name)

        embed = base_embed(f"📊 Stats — {target.display_name}", color_key="info")
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.add_field(name="🏆 Wins", value=str(player.wins), inline=True)
        embed.add_field(name="💀 Losses", value=str(player.losses), inline=True)
        embed.add_field(name="🤝 Draws", value=str(player.draws), inline=True)
        embed.add_field(name="🎮 Total Games", value=str(player.total_games), inline=True)
        embed.add_field(name="📈 Win Rate", value=f"{player.win_rate}%", inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=True)
        embed.add_field(
            name="Per-Game Wins",
            value=(
                f"✂️ RPS: **{player.rps_wins}**\n"
                f"❌ Tic-Tac-Toe: **{player.ttt_wins}**\n"
                f"❓ Trivia: **{player.trivia_wins}**"
            ),
            inline=False
        )
        await ctx.send(embed=embed)

    @commands.command(name="leaderboard", aliases=["lb"])
    @commands.guild_only()
    async def leaderboard(self, ctx: commands.Context):
        """View the global top 10 leaderboard."""
        players = await get_leaderboard(10)
        embed = leaderboard_embed(players)
        await ctx.send(embed=embed)

    @commands.command(name="ping")
    async def ping(self, ctx: commands.Context):
        """Check the bot's latency."""
        latency = round(self.bot.latency * 1000)
        embed = base_embed("🏓 Pong!", f"Latency: **{latency}ms**", "success")
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(General(bot))
