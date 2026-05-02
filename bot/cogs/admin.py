import discord
from discord.ext import commands
from bot.utils.embeds import success_embed, error_embed, base_embed
from bot.database.db_utils import get_or_create_guild, update_guild_settings


class Admin(commands.Cog, name="Admin"):
    """Server administration commands (requires Manage Server permission)."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def cog_check(self, ctx: commands.Context) -> bool:
        """All admin commands require Manage Guild permission."""
        return ctx.author.guild_permissions.manage_guild

    @commands.command(name="setprefix")
    @commands.guild_only()
    async def set_prefix(self, ctx: commands.Context, prefix: str):
        """Change the bot's command prefix for this server. Usage: !setprefix <prefix>"""
        if len(prefix) > 5:
            return await ctx.send(embed=error_embed("Invalid Prefix", "Prefix must be 5 characters or fewer."))

        await get_or_create_guild(ctx.guild.id)
        await update_guild_settings(ctx.guild.id, prefix=prefix)

        # Update in-memory prefix for this guild
        self.bot.command_prefix_map[ctx.guild.id] = prefix

        await ctx.send(embed=success_embed("Prefix Updated", f"Command prefix is now `{prefix}`"))

    @commands.command(name="setgamechannel")
    @commands.guild_only()
    async def set_game_channel(self, ctx: commands.Context, channel: discord.TextChannel = None):
        """Set or clear a dedicated game channel. Usage: !setgamechannel [#channel]"""
        await get_or_create_guild(ctx.guild.id)
        if channel:
            await update_guild_settings(ctx.guild.id, game_channel_id=channel.id)
            await ctx.send(embed=success_embed("Game Channel Set", f"Games are now restricted to {channel.mention}."))
        else:
            await update_guild_settings(ctx.guild.id, game_channel_id=None)
            await ctx.send(embed=success_embed("Game Channel Cleared", "Games can now be played in any channel."))

    @commands.command(name="togglegame")
    @commands.guild_only()
    async def toggle_game(self, ctx: commands.Context, game: str):
        """Enable or disable a game. Usage: !togglegame <rps|ttt|trivia>"""
        game = game.lower()
        mapping = {
            "rps": "rps_enabled",
            "ttt": "ttt_enabled",
            "trivia": "trivia_enabled",
        }
        if game not in mapping:
            return await ctx.send(embed=error_embed("Unknown Game", "Valid options: `rps`, `ttt`, `trivia`"))

        guild = await get_or_create_guild(ctx.guild.id)
        field = mapping[game]
        current = getattr(guild, field)
        new_value = not current
        await update_guild_settings(ctx.guild.id, **{field: new_value})

        status = "enabled ✅" if new_value else "disabled ❌"
        await ctx.send(embed=success_embed("Game Toggled", f"**{game.upper()}** is now {status}."))

    @commands.command(name="serversettings", aliases=["settings"])
    @commands.guild_only()
    async def server_settings(self, ctx: commands.Context):
        """View the current server settings."""
        guild = await get_or_create_guild(ctx.guild.id)
        game_ch = (f"<#{guild.game_channel_id}>" if guild.game_channel_id else "Any channel")

        embed = base_embed(f"⚙️ Settings — {ctx.guild.name}", color_key="info")
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        embed.add_field(name="Prefix", value=f"`{guild.prefix}`", inline=True)
        embed.add_field(name="Game Channel", value=game_ch, inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=True)
        embed.add_field(
            name="Games",
            value=(
                f"✂️ RPS: {'✅' if guild.rps_enabled else '❌'}\n"
                f"❌ Tic-Tac-Toe: {'✅' if guild.ttt_enabled else '❌'}\n"
                f"❓ Trivia: {'✅' if guild.trivia_enabled else '❌'}"
            ),
            inline=False
        )
        await ctx.send(embed=embed)

    @commands.command(name="resetstats")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def reset_stats(self, ctx: commands.Context, member: discord.Member):
        """[Admin only] Reset a player's stats. Usage: !resetstats @user"""
        from bot.database.db_utils import AsyncSessionLocal
        from bot.database.models import Player
        from sqlalchemy import select, update as sa_update

        async with AsyncSessionLocal() as session:
            await session.execute(
                sa_update(Player)
                .where(Player.discord_id == member.id)
                .values(wins=0, losses=0, draws=0, rps_wins=0, ttt_wins=0, trivia_wins=0)
            )
            await session.commit()

        await ctx.send(embed=success_embed("Stats Reset", f"{member.display_name}'s stats have been reset."))

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send(embed=error_embed("Permission Denied", "You need **Manage Server** permission."))
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(embed=error_embed("Missing Argument", f"Check `{ctx.prefix}help` for usage."))


async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))
