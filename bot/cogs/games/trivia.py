import asyncio
import discord
from discord.ext import commands
# FIXED: Remove 'bot.' prefix from all imports
from utils.embeds import (challenge_embed, trivia_embed, trivia_result_embed,
                           error_embed, game_embed, success_embed)
from utils.game_logic import get_trivia_questions
from utils.matchmaking import matchmaking, GameSession
from database.db_utils import get_or_create_player, update_player_stats, log_game


class TriviaAnswerView(discord.ui.View):
    """ABCD answer buttons for trivia."""

    def __init__(self, p1: discord.Member, p2: discord.Member, timeout: float = 30):
        super().__init__(timeout=timeout)
        self.p1 = p1
        self.p2 = p2
        self.answers: dict[int, str] = {}
        self._lock = asyncio.Lock()

    async def _handle(self, interaction: discord.Interaction, choice: str):
        if interaction.user.id not in (self.p1.id, self.p2.id):
            await interaction.response.send_message("You are not in this game!", ephemeral=True)
            return
        async with self._lock:
            if interaction.user.id in self.answers:
                await interaction.response.send_message("You already answered!", ephemeral=True)
                return
            self.answers[interaction.user.id] = choice
            await interaction.response.send_message(f"You answered **{choice}**!", ephemeral=True)
            if len(self.answers) == 2:
                self.stop()

    @discord.ui.button(label="A", style=discord.ButtonStyle.primary, row=0)
    async def btn_a(self, i, _): await self._handle(i, "A")

    @discord.ui.button(label="B", style=discord.ButtonStyle.primary, row=0)
    async def btn_b(self, i, _): await self._handle(i, "B")

    @discord.ui.button(label="C", style=discord.ButtonStyle.primary, row=0)
    async def btn_c(self, i, _): await self._handle(i, "C")

    @discord.ui.button(label="D", style=discord.ButtonStyle.primary, row=0)
    async def btn_d(self, i, _): await self._handle(i, "D")

    async def on_timeout(self):
        self.stop()


class Trivia(commands.Cog, name="Trivia"):
    """Play Trivia against another player."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="trivia")
    @commands.guild_only()
    async def trivia(self, ctx: commands.Context, opponent: discord.Member, rounds: int = 5):
        """Challenge someone to Trivia. Usage: !trivia @user [rounds]"""
        if opponent.bot:
            return await ctx.send(embed=error_embed("Invalid Opponent", "You cannot challenge a bot."))
        if opponent == ctx.author:
            return await ctx.send(embed=error_embed("Invalid Opponent", "You cannot challenge yourself."))
        if not (1 <= rounds <= 10):
            return await ctx.send(embed=error_embed("Invalid Rounds", "Rounds must be between 1 and 10."))
        if matchmaking.is_in_game(ctx.author.id, ctx.guild.id):
            return await ctx.send(embed=error_embed("Already In Game", "You are already in an active game."))
        if matchmaking.is_in_game(opponent.id, ctx.guild.id):
            return await ctx.send(embed=error_embed("Opponent Busy", f"{opponent.display_name} is already in a game."))

        await get_or_create_player(ctx.author.id, ctx.author.display_name)
        await get_or_create_player(opponent.id, opponent.display_name)

        async def on_accept(interaction: discord.Interaction):
            session = GameSession(
                game_type="trivia",
                player1=ctx.author,
                player2=opponent,
                guild_id=ctx.guild.id,
                channel_id=ctx.channel.id,
                data={"rounds": rounds}
            )
            matchmaking.start_session(session)
            await _play_trivia(ctx, session, challenge_msg)

        async def on_decline(interaction: discord.Interaction):
            await challenge_msg.edit(
                embed=error_embed("Challenge Declined", f"{opponent.display_name} declined the challenge."),
                view=None
            )

        matchmaking.add_challenge(ctx.author, opponent, "trivia")

        class AcceptView(discord.ui.View):
            def __init__(self_, ch):
                super().__init__(timeout=60)
                self_.challenged = ch

            async def interaction_check(self_, interaction: discord.Interaction) -> bool:
                if interaction.user.id != self_.challenged.id:
                    await interaction.response.send_message("This isn't for you!", ephemeral=True)
                    return False
                return True

            @discord.ui.button(label="✅ Accept", style=discord.ButtonStyle.success)
            async def acc(self_, i, _):
                self_.stop()
                await i.response.defer()
                await on_accept(i)

            @discord.ui.button(label="❌ Decline", style=discord.ButtonStyle.danger)
            async def dec(self_, i, _):
                self_.stop()
                await i.response.defer()
                await on_decline(i)

        challenge_msg = await ctx.send(
            content=f"{opponent.mention}",
            embed=challenge_embed(ctx.author, opponent, f"Trivia ({rounds} rounds)"),
            view=AcceptView(opponent)
        )

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(embed=error_embed("Missing Argument", "Usage: `!trivia @user [rounds]`"))
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send(embed=error_embed("User Not Found", "Could not find that user."))


async def _play_trivia(ctx: commands.Context, session: GameSession, challenge_msg: discord.Message):
    p1, p2 = session.player1, session.player2
    rounds = session.data.get("rounds", 5)
    questions = get_trivia_questions(rounds)
    scores = {p1.id: 0, p2.id: 0}

    await challenge_msg.edit(
        embed=game_embed(
            "Trivia Starting!",
            f"{p1.mention} vs {p2.mention} — {rounds} questions.\n"
            "Answer quickly! The first to answer correctly each round earns a point."
        ),
        view=None
    )
    await asyncio.sleep(2)

    for i, q in enumerate(questions, 1):
        answer_view = TriviaAnswerView(p1, p2, timeout=30)
        options_text = "\n".join(q["options"])
        embed = trivia_embed(q["question"], q["category"], q["difficulty"], i, rounds)
        embed.add_field(name="Options", value=options_text, inline=False)

        q_msg = await ctx.send(embed=embed, view=answer_view)
        await answer_view.wait()

        correct = q["answer"]
        round_results = []
        for uid, ans in answer_view.answers.items():
            player = p1 if uid == p1.id else p2
            if ans == correct:
                scores[uid] += 1
                round_results.append(f"✅ {player.display_name} — **{ans}** (correct!)")
            else:
                round_results.append(f"❌ {player.display_name} — **{ans}** (wrong)")

        # Players who didn't answer
        for player in [p1, p2]:
            if player.id not in answer_view.answers:
                round_results.append(f"⏱️ {player.display_name} — timed out")

        result_embed = game_embed(
            f"Round {i}/{rounds} — Answer: **{correct}**",
            "\n".join(round_results) + f"\n\n**Score:** {p1.display_name} {scores[p1.id]} — {scores[p2.id]} {p2.display_name}"
        )
        await q_msg.edit(embed=result_embed, view=None)
        await asyncio.sleep(3)

    matchmaking.end_session(p1.id, p2.id, session.guild_id)
    final_embed = trivia_result_embed(p1, p2, scores[p1.id], scores[p2.id], rounds)
    await ctx.send(embed=final_embed)

    p1_score, p2_score = scores[p1.id], scores[p2.id]
    if p1_score > p2_score:
        await update_player_stats(p1.id, "win", "trivia")
        await update_player_stats(p2.id, "loss", "trivia")
        await log_game("trivia", session.guild_id, p1.id, p2.id, "win")
    elif p2_score > p1_score:
        await update_player_stats(p2.id, "win", "trivia")
        await update_player_stats(p1.id, "loss", "trivia")
        await log_game("trivia", session.guild_id, p2.id, p1.id, "win")
    else:
        await update_player_stats(p1.id, "draw", "trivia")
        await update_player_stats(p2.id, "draw", "trivia")
        await log_game("trivia", session.guild_id, None, None, "draw")


async def setup(bot: commands.Bot):
    await bot.add_cog(Trivia(bot))
