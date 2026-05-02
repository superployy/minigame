import asyncio
import discord
from discord.ext import commands
# FIXED: Remove 'bot.' prefix from all imports
from utils.embeds import challenge_embed, rps_result_embed, error_embed, game_embed
from utils.game_logic import RPS_CHOICES, rps_determine_winner
from utils.matchmaking import matchmaking, GameSession
from database.db_utils import get_or_create_player, update_player_stats, log_game


class RpsView(discord.ui.View):
    """View with Rock / Paper / Scissors buttons for the actual game."""

    def __init__(self, session: GameSession, on_choice):
        super().__init__(timeout=30)
        self.session = session
        self.on_choice = on_choice
        self.choices: dict[int, str] = {}

    async def _handle(self, interaction: discord.Interaction, choice: str):
        player = interaction.user
        p1, p2 = self.session.player1, self.session.player2

        if player.id not in (p1.id, p2.id):
            await interaction.response.send_message("You are not in this game!", ephemeral=True)
            return

        if player.id in self.choices:
            await interaction.response.send_message("You already chose!", ephemeral=True)
            return

        self.choices[player.id] = choice
        await interaction.response.send_message(
            f"You chose **{choice}** {'🪨' if choice=='rock' else '📄' if choice=='paper' else '✂️'}!", 
            ephemeral=True
        )

        if len(self.choices) == 2:
            self.stop()
            await self.on_choice(self.choices)

    @discord.ui.button(label="🪨 Rock", style=discord.ButtonStyle.secondary)
    async def rock(self, interaction: discord.Interaction, _):
        await self._handle(interaction, "rock")

    @discord.ui.button(label="📄 Paper", style=discord.ButtonStyle.secondary)
    async def paper(self, interaction: discord.Interaction, _):
        await self._handle(interaction, "paper")

    @discord.ui.button(label="✂️ Scissors", style=discord.ButtonStyle.secondary)
    async def scissors(self, interaction: discord.Interaction, _):
        await self._handle(interaction, "scissors")

    async def on_timeout(self):
        self.stop()


class ChallengeView(discord.ui.View):
    """Accept / decline a challenge."""

    def __init__(self, challenged: discord.Member, on_accept, on_decline):
        super().__init__(timeout=60)
        self.challenged = challenged
        self.on_accept = on_accept
        self.on_decline = on_decline

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.challenged.id:
            await interaction.response.send_message("This challenge isn't for you!", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="✅ Accept", style=discord.ButtonStyle.success)
    async def accept(self, interaction: discord.Interaction, _):
        self.stop()
        await interaction.response.defer()
        await self.on_accept(interaction)

    @discord.ui.button(label="❌ Decline", style=discord.ButtonStyle.danger)
    async def decline(self, interaction: discord.Interaction, _):
        self.stop()
        await interaction.response.defer()
        await self.on_decline(interaction)


class RockPaperScissors(commands.Cog, name="Rock Paper Scissors"):
    """Play Rock Paper Scissors against another player."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="rps", aliases=["rockpaperscissors"])
    @commands.guild_only()
    async def rps(self, ctx: commands.Context, opponent: discord.Member):
        """Challenge someone to Rock Paper Scissors. Usage: !rps @user"""
        if opponent.bot:
            return await ctx.send(embed=error_embed("Invalid Opponent", "You cannot challenge a bot."))
        if opponent == ctx.author:
            return await ctx.send(embed=error_embed("Invalid Opponent", "You cannot challenge yourself."))
        if matchmaking.is_in_game(ctx.author.id, ctx.guild.id):
            return await ctx.send(embed=error_embed("Already In Game", "You are already in an active game."))
        if matchmaking.is_in_game(opponent.id, ctx.guild.id):
            return await ctx.send(embed=error_embed("Opponent Busy", f"{opponent.display_name} is already in a game."))

        await get_or_create_player(ctx.author.id, ctx.author.display_name)
        await get_or_create_player(opponent.id, opponent.display_name)

        async def on_accept(interaction: discord.Interaction):
            session = GameSession(
                game_type="rps",
                player1=ctx.author,
                player2=opponent,
                guild_id=ctx.guild.id,
                channel_id=ctx.channel.id,
            )
            matchmaking.start_session(session)
            await _play_rps(ctx, session, challenge_msg)

        async def on_decline(interaction: discord.Interaction):
            matchmaking.decline_challenge(ctx.author.id, opponent.id, ctx.guild.id)
            await challenge_msg.edit(
                embed=error_embed("Challenge Declined", f"{opponent.display_name} declined the challenge."),
                view=None
            )

        matchmaking.add_challenge(ctx.author, opponent, "rps")
        view = ChallengeView(opponent, on_accept, on_decline)
        challenge_msg = await ctx.send(
            content=f"{opponent.mention}",
            embed=challenge_embed(ctx.author, opponent, "Rock Paper Scissors"),
            view=view
        )

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(embed=error_embed("Missing Argument", "Usage: `!rps @user`"))
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send(embed=error_embed("User Not Found", "Could not find that user."))


async def _play_rps(ctx: commands.Context, session: GameSession, challenge_msg: discord.Message):
    result_holder = {}

    async def on_choice(choices: dict):
        result_holder["choices"] = choices

    view = RpsView(session, on_choice)
    game_msg = await ctx.send(
        embed=game_embed(
            "Rock Paper Scissors — Make your choice!",
            f"{session.player1.mention} vs {session.player2.mention}\n\n"
            "Both players: click your choice below (only you can see your pick)."
        ),
        view=view
    )

    await view.wait()
    matchmaking.end_session(session.player1.id, session.player2.id, session.guild_id)

    choices = result_holder.get("choices", {})
    if len(choices) < 2:
        # Timeout — someone didn't pick
        await game_msg.edit(
            embed=error_embed("Game Timed Out", "One or both players didn't choose in time."),
            view=None
        )
        return

    p1_choice = choices[session.player1.id]
    p2_choice = choices[session.player2.id]
    outcome = rps_determine_winner(p1_choice, p2_choice)

    if outcome == "p1":
        winner, loser = session.player1, session.player2
    elif outcome == "p2":
        winner, loser = session.player2, session.player1
    else:
        winner = loser = None

    embed = rps_result_embed(winner, session.player1, session.player2, p1_choice, p2_choice)
    await game_msg.edit(embed=embed, view=None)

    if winner:
        await update_player_stats(winner.id, "win", "rps")
        await update_player_stats(loser.id, "loss", "rps")
        await log_game("rps", session.guild_id, winner.id, loser.id, "win")
    else:
        await update_player_stats(session.player1.id, "draw", "rps")
        await update_player_stats(session.player2.id, "draw", "rps")
        await log_game("rps", session.guild_id, None, None, "draw")


async def setup(bot: commands.Bot):
    await bot.add_cog(RockPaperScissors(bot))
