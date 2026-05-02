import discord
from discord.ext import commands
# FIXED: Remove 'bot.' prefix from all imports
from utils.embeds import (challenge_embed, ttt_board_embed, ttt_result_embed,
                           error_embed, game_embed)
from utils.game_logic import make_board, make_move, check_winner, board_position_to_rc
from utils.matchmaking import matchmaking, GameSession
from database.db_utils import get_or_create_player, update_player_stats, log_game


class TTTView(discord.ui.View):
    """3×3 grid of buttons for Tic-Tac-Toe."""

    LABELS = [
        ["1", "2", "3"],
        ["4", "5", "6"],
        ["7", "8", "9"],
    ]

    def __init__(self, session: GameSession, board: list[list[str]],
                 current_player: discord.Member, symbols: dict,
                 on_move_callback):
        super().__init__(timeout=120)
        self.session = session
        self.board = board
        self.current_player = current_player
        self.symbols = symbols
        self.on_move_callback = on_move_callback
        self._build_buttons()

    def _build_buttons(self):
        self.clear_items()
        for r in range(3):
            for c in range(3):
                cell = self.board[r][c]
                pos = r * 3 + c + 1
                btn = discord.ui.Button(
                    label=self.LABELS[r][c] if cell == " " else ("❌" if cell == "X" else "⭕"),
                    style=(discord.ButtonStyle.secondary if cell == " "
                           else (discord.ButtonStyle.danger if cell == "X"
                                 else discord.ButtonStyle.primary)),
                    disabled=(cell != " "),
                    row=r,
                    custom_id=f"ttt_{pos}",
                )
                btn.callback = self._make_callback(pos)
                self.add_item(btn)

    def _make_callback(self, pos: int):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.current_player.id:
                await interaction.response.send_message(
                    "It's not your turn!", ephemeral=True
                )
                return
            self.stop()
            await interaction.response.defer()
            await self.on_move_callback(pos)
        return callback

    async def on_timeout(self):
        self.stop()


class TicTacToe(commands.Cog, name="Tic Tac Toe"):
    """Play Tic-Tac-Toe against another player."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="ttt", aliases=["tictactoe"])
    @commands.guild_only()
    async def ttt(self, ctx: commands.Context, opponent: discord.Member):
        """Challenge someone to Tic-Tac-Toe. Usage: !ttt @user"""
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
                game_type="ttt",
                player1=ctx.author,
                player2=opponent,
                guild_id=ctx.guild.id,
                channel_id=ctx.channel.id,
            )
            matchmaking.start_session(session)
            await _play_ttt(ctx, session, challenge_msg)

        async def on_decline(interaction: discord.Interaction):
            await challenge_msg.edit(
                embed=error_embed("Challenge Declined", f"{opponent.display_name} declined the challenge."),
                view=None
            )

        matchmaking.add_challenge(ctx.author, opponent, "ttt")

        class AcceptView(discord.ui.View):
            def __init__(self_, ch: discord.Member):
                super().__init__(timeout=60)
                self_.challenged = ch

            async def interaction_check(self_, interaction: discord.Interaction) -> bool:
                if interaction.user.id != self_.challenged.id:
                    await interaction.response.send_message("This isn't for you!", ephemeral=True)
                    return False
                return True

            @discord.ui.button(label="✅ Accept", style=discord.ButtonStyle.success)
            async def accept_btn(self_, interaction: discord.Interaction, _):
                self_.stop()
                await interaction.response.defer()
                await on_accept(interaction)

            @discord.ui.button(label="❌ Decline", style=discord.ButtonStyle.danger)
            async def decline_btn(self_, interaction: discord.Interaction, _):
                self_.stop()
                await interaction.response.defer()
                await on_decline(interaction)

        challenge_msg = await ctx.send(
            content=f"{opponent.mention}",
            embed=challenge_embed(ctx.author, opponent, "Tic-Tac-Toe"),
            view=AcceptView(opponent)
        )

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(embed=error_embed("Missing Argument", "Usage: `!ttt @user`"))
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send(embed=error_embed("User Not Found", "Could not find that user."))


async def _play_ttt(ctx: commands.Context, session: GameSession, challenge_msg: discord.Message):
    board = make_board()
    p1, p2 = session.player1, session.player2
    symbols = {p1.id: "X", p2.id: "O"}
    players = [p1, p2]
    turn = 0
    game_msg = None

    while True:
        current = players[turn % 2]
        board_embed = ttt_board_embed(board, current, p1, p2)

        move_result = {"pos": None}

        async def on_move(pos: int, _move_result=move_result):
            _move_result["pos"] = pos

        view = TTTView(session, board, current, symbols, on_move)

        if game_msg is None:
            game_msg = await ctx.send(embed=board_embed, view=view)
        else:
            await game_msg.edit(embed=board_embed, view=view)

        await view.wait()
        pos = move_result["pos"]

        if pos is None:
            # Timeout
            matchmaking.end_session(p1.id, p2.id, session.guild_id)
            await game_msg.edit(
                embed=error_embed("Game Timed Out", f"{current.display_name} took too long."),
                view=None
            )
            return

        row, col = board_position_to_rc(pos)
        make_move(board, row, col, symbols[current.id])
        winner_sym = check_winner(board)

        if winner_sym:
            matchmaking.end_session(p1.id, p2.id, session.guild_id)
            if winner_sym == "draw":
                result_embed = ttt_result_embed(board, None, p1, p2)
                await game_msg.edit(embed=result_embed, view=None)
                await update_player_stats(p1.id, "draw", "ttt")
                await update_player_stats(p2.id, "draw", "ttt")
                await log_game("ttt", session.guild_id, None, None, "draw")
            else:
                winner = p1 if symbols[p1.id] == winner_sym else p2
                loser = p2 if winner == p1 else p1
                result_embed = ttt_result_embed(board, winner, p1, p2)
                await game_msg.edit(embed=result_embed, view=None)
                await update_player_stats(winner.id, "win", "ttt")
                await update_player_stats(loser.id, "loss", "ttt")
                await log_game("ttt", session.guild_id, winner.id, loser.id, "win")
            return

        turn += 1


async def setup(bot: commands.Bot):
    await bot.add_cog(TicTacToe(bot))
