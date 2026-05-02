import discord
from discord.ext import commands

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        """Check the bot's latency"""
        await ctx.send(f"🏓 Pong! `{round(self.bot.latency * 1000)}ms`")

    @commands.command()
    async def help(self, ctx):
        """Show bot commands"""
        embed = discord.Embed(
            title="🎮 MOBA GP Mini Games Bot",
            description="Commands for the bot",
            color=discord.Color.green()
        )
        embed.add_field(name="!ping", value="Check bot latency", inline=False)
        embed.add_field(name="More games coming soon!", value="Rock Paper Scissors, Tic Tac Toe, Trivia", inline=False)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(General(bot))
