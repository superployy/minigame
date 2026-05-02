import discord
from discord.ext import commands
from utils.embeds import base_embed, leaderboard_embed, game_embed, error_embed
from database.db_utils import get_or_create_player, get_leaderboard

class General(commands.Cog, name="General"):
    """បញ្ជាទូទៅ៖ ជំនួយ, ស្ថិតិ, តារាងពិន្ទុ (General commands)"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="help", aliases=["h"])
    async def help_cmd(self, ctx: commands.Context):
        """បង្ហាញបញ្ជាទាំងអស់ដែលមាន (Show all commands)"""
        prefix = ctx.prefix or "!"
        
        embed = base_embed(
            "🎮 Mini Games Bot — ជំនួយ",
            "បតហ្គេមខ្នាតតូចសម្រាប់លេងកម្សាន្តជាមួយមិត្តភក្តិ!\n\u200b",
            "info"
        )
        
        embed.add_field(
            name="🎯 ហ្គេមកម្សាន្ត (Games)",
            value=(
                f"**`{prefix}rps @user`** — ប៉ាវសី (កន្ត្រៃ ក្រដាស ថ្ម)\n"
                f"**`{prefix}ttt @user`** — ការ៉ូ (Tic-Tac-Toe)\n"
                f"**`{prefix}trivia @user`** — ឆ្លើយសំណួរចំណេះដឹងទូទៅ"
            ),
            inline=False,
        )
        
        embed.add_field(
            name="📊 ស្ថិតិ និងពិន្ទុ (Stats)",
            value=(
                f"**`{prefix}stats [@user]`** — មើលស្ថិតិ ឈ្នះ/ចាញ់\n"
                f"**`{prefix}leaderboard`** — តារាងអ្នកខ្លាំងបំផុតទាំង ១០\n"
                f"**`{prefix}lb`** — ផ្លូវកាត់មើលតារាងពិន្ទុ"
            ),
            inline=False,
        )
        
        embed.add_field(
            name="⚙️ ការកំណត់ (Admin)",
            value=(
                f"**`{prefix}setprefix`** — ប្តូរសញ្ញាបញ្ជា\n"
                f"**`{prefix}serversettings`** — មើលការកំណត់ក្នុងសឺវើរ"
            ),
            inline=False,
        )
        
        embed.set_footer(text="ប្រើប្រាស់សញ្ញា '!' នៅពីមុខពាក្យបញ្ជា")
        await ctx.send(embed=embed)

    @commands.command(name="stats")
    @commands.guild_only()
    async def stats(self, ctx: commands.Context, member: discord.Member = None):
        """មើលស្ថិតិផ្ទាល់ខ្លួន ឬមិត្តភក្តិ (View stats)"""
        target = member or ctx.author
        player = await get_or_create_player(target.id, target.display_name)

        embed = base_embed(f"📊 ស្ថិតិរបស់ — {target.display_name}", color_key="info")
        embed.set_thumbnail(url=target.display_avatar.url)
        
        # Grid layout for better UX
        embed.add_field(name="🏆 ឈ្នះ", value=f"**{player.wins}**", inline=True)
        embed.add_field(name="💀 ចាញ់", value=f"**{player.losses}**", inline=True)
        embed.add_field(name="🤝 ស្មើ", value=f"**{player.draws}**", inline=True)
        
        embed.add_field(name="🎮 លេងសរុប", value=f"{player.total_games} ដង", inline=True)
        embed.add_field(name="📈 អត្រាឈ្នះ", value=f"**{player.win_rate}%**", inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=True)

        embed.add_field(
            name="🏆 ចំនួនឈ្នះតាមប្រភេទហ្គេម",
            value=(
                f"✂️ ប៉ាវសី: **{player.rps_wins}**\n"
                f"❌ ការ៉ូ: **{player.ttt_wins}**\n"
                f"❓ សំណួរ: **{player.trivia_wins}**"
            ),
            inline=False
        )
        await ctx.send(embed=embed)

    @commands.command(name="leaderboard", aliases=["lb"])
    @commands.guild_only()
    async def leaderboard(self, ctx: commands.Context):
        """មើលតារាងអ្នកដែលមានពិន្ទុខ្ពស់ជាងគេ (Global Leaderboard)"""
        players = await get_leaderboard(10)
        # Assuming leaderboard_embed handles translation, otherwise update it too
        embed = leaderboard_embed(players)
        embed.title = "🏆 តារាងអ្នកខ្លាំងបំផុតទាំង ១០"
        await ctx.send(embed=embed)

    @commands.command(name="ping")
    async def ping(self, ctx: commands.Context):
        """ពិនិត្យមើលល្បឿនបត (Bot latency)"""
        latency = round(self.bot.latency * 1000)
        embed = base_embed("🏓 ផុង!", f"ល្បឿនបញ្ជូនទិន្នន័យ: **{latency}ms**", "success")
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(General(bot))
