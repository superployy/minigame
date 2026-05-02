import discord
from datetime import datetime


COLORS = {
    "success": 0x2ECC71,
    "error": 0xE74C3C,
    "info": 0x3498DB,
    "warning": 0xF39C12,
    "gold": 0xF1C40F,
    "purple": 0x9B59B6,
    "game": 0x1ABC9C,
}


def base_embed(title: str, description: str = "", color_key: str = "info") -> discord.Embed:
    embed = discord.Embed(
        title=title,
        description=description,
        color=COLORS.get(color_key, COLORS["info"]),
        timestamp=datetime.utcnow(),
    )
    embed.set_footer(text="Mini Games Bot")
    return embed


def success_embed(title: str, description: str = "") -> discord.Embed:
    return base_embed(f"✅ {title}", description, "success")


def error_embed(title: str, description: str = "") -> discord.Embed:
    return base_embed(f"❌ {title}", description, "error")


def game_embed(title: str, description: str = "") -> discord.Embed:
    return base_embed(f"🎮 {title}", description, "game")


def challenge_embed(challenger: discord.Member, challenged: discord.Member, game: str) -> discord.Embed:
    embed = base_embed(
        f"⚔️ {game} Challenge!",
        f"{challenger.mention} has challenged {challenged.mention} to a game of **{game}**!\n\n"
        f"{challenged.mention}, do you accept?",
        "purple"
    )
    embed.add_field(name="How to respond", value="✅ Accept  |  ❌ Decline", inline=False)
    return embed


def leaderboard_embed(players: list, title: str = "🏆 Global Leaderboard") -> discord.Embed:
    embed = base_embed(title, color_key="gold")
    medals = ["🥇", "🥈", "🥉"]
    if not players:
        embed.description = "No players on the leaderboard yet. Play some games!"
        return embed

    rows = []
    for i, p in enumerate(players):
        medal = medals[i] if i < 3 else f"`#{i+1}`"
        rows.append(
            f"{medal} **{p.username}** — {p.wins}W / {p.losses}L / {p.draws}D  ({p.win_rate}%)"
        )
    embed.description = "\n".join(rows)
    return embed


def rps_result_embed(winner: discord.Member | None, p1: discord.Member, p2: discord.Member,
                     p1_choice: str, p2_choice: str) -> discord.Embed:
    emojis = {"rock": "🪨", "paper": "📄", "scissors": "✂️"}
    e1, e2 = emojis[p1_choice], emojis[p2_choice]
    if winner:
        title = f"{winner.display_name} wins!"
        desc = (f"{p1.mention} chose {e1} **{p1_choice}**\n"
                f"{p2.mention} chose {e2} **{p2_choice}**")
        color = "success"
    else:
        title = "It's a draw!"
        desc = (f"Both players chose {e1} **{p1_choice}**")
        color = "warning"
    embed = base_embed(f"✂️ Rock Paper Scissors — {title}", desc, color)
    return embed


def ttt_board_embed(board: list[list[str]], current_player: discord.Member,
                    p1: discord.Member, p2: discord.Member) -> discord.Embed:
    symbols = {" ": "⬜", "X": "❌", "O": "⭕"}
    rows = []
    for row in board:
        rows.append("".join(symbols[c] for c in row))
    board_str = "\n".join(rows)
    embed = game_embed(
        "Tic-Tac-Toe",
        f"{p1.mention} ❌  vs  {p2.mention} ⭕\n\n{board_str}\n\n"
        f"**{current_player.display_name}'s turn**"
    )
    return embed


def ttt_result_embed(board: list[list[str]], winner: discord.Member | None,
                     p1: discord.Member, p2: discord.Member) -> discord.Embed:
    symbols = {" ": "⬜", "X": "❌", "O": "⭕"}
    rows = []
    for row in board:
        rows.append("".join(symbols[c] for c in row))
    board_str = "\n".join(rows)

    if winner:
        title = f"🎉 {winner.display_name} wins Tic-Tac-Toe!"
        color = "success"
    else:
        title = "🤝 Tic-Tac-Toe — Draw!"
        color = "warning"
    embed = base_embed(title, f"{board_str}", color)
    return embed


def trivia_embed(question: str, category: str, difficulty: str, index: int, total: int) -> discord.Embed:
    embed = base_embed(
        f"❓ Trivia  [{index}/{total}]",
        f"**Category:** {category}  |  **Difficulty:** {difficulty.title()}\n\n{question}",
        "purple"
    )
    embed.add_field(name="⏱️ Time limit", value="30 seconds per question", inline=False)
    return embed


def trivia_result_embed(p1: discord.Member, p2: discord.Member,
                        p1_score: int, p2_score: int, total: int) -> discord.Embed:
    if p1_score > p2_score:
        winner, loser = p1, p2
        ws, ls = p1_score, p2_score
    elif p2_score > p1_score:
        winner, loser = p2, p1
        ws, ls = p2_score, p1_score
    else:
        embed = base_embed(
            "🤝 Trivia — Draw!",
            f"Both players scored **{p1_score}/{total}**!",
            "warning"
        )
        return embed

    embed = base_embed(
        f"🏆 Trivia — {winner.display_name} wins!",
        f"🥇 {winner.mention}: **{ws}/{total}**\n🥈 {loser.mention}: **{ls}/{total}**",
        "success"
    )
    return embed
