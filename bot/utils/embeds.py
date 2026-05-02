import discord

# ========== ADD THESE MISSING FUNCTIONS ==========

def base_embed(title, description="", color_key="info"):
    """Create a base embed with standard formatting"""
    colors = {
        "info": discord.Color.blue(),
        "success": discord.Color.green(),
        "error": discord.Color.red(),
        "warning": discord.Color.yellow(),
        "purple": discord.Color.purple()
    }
    color = colors.get(color_key, discord.Color.blue())
    return discord.Embed(title=title, description=description, color=color)

def success_embed(title, description="", color_key="success"):
    """Create a success embed"""
    colors = {
        "success": discord.Color.green(),
    }
    color = colors.get(color_key, discord.Color.green())
    return discord.Embed(title=title, description=description, color=color)

def error_embed(title, description=""):
    """Create an error embed"""
    return discord.Embed(title=f"❌ {title}", description=description, color=discord.Color.red())

def game_embed(title, description, color=discord.Color.purple()):
    """Create a game embed"""
    return discord.Embed(title=title, description=description, color=color)

def challenge_embed( challenger, opponent, game_name):
    """Create a challenge embed"""
    embed = discord.Embed(
        title=f"🎮 {game_name} Challenge!",
        description=f"{challenger.mention} has challenged {opponent.mention} to **{game_name}**!\n\nDo you accept?",
        color=discord.Color.blue()
    )
    embed.set_footer(text="You have 60 seconds to respond.")
    return embed

def leaderboard_embed(players):
    """Create leaderboard embed"""
    embed = discord.Embed(title="🏆 Leaderboard", color=discord.Color.gold())
    if not players:
        embed.description = "No players yet!"
        return embed
    
    description = ""
    for i, player in enumerate(players[:10], 1):
        medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, f"{i}.")
        # Handle both object and dict players
        if hasattr(player, 'name'):
            name = player.name
            wins = player.wins
            win_rate = player.win_rate
        else:
            name = player.get('name', 'Unknown')
            wins = player.get('wins', 0)
            win_rate = player.get('win_rate', 0)
        description += f"{medal} **{name}** — {wins} wins ({win_rate}%)\n"
    
    embed.description = description
    return embed

def rps_result_embed(winner, player1, player2, p1_choice, p2_choice):
    """Create RPS result embed"""
    choice_emojis = {"rock": "🪨", "paper": "📄", "scissors": "✂️"}
    
    embed = discord.Embed(
        title="🎮 Rock Paper Scissors Results",
        color=discord.Color.gold() if winner else discord.Color.blue()
    )
    embed.add_field(name=player1.display_name, value=f"{choice_emojis[p1_choice]} {p1_choice.title()}", inline=True)
    embed.add_field(name="VS", value="⚔️", inline=True)
    embed.add_field(name=player2.display_name, value=f"{choice_emojis[p2_choice]} {p2_choice.title()}", inline=True)
    
    if winner:
        embed.add_field(name="🏆 Winner", value=winner.mention, inline=False)
    else:
        embed.add_field(name="🤝 Result", value="It's a draw!", inline=False)
    
    return embed

# ========== YOUR EXISTING FUNCTIONS BELOW ==========
# (Keep all your existing Tic-Tac-Toe and Trivia functions)

def ttt_game_embed(board: list[list[str]], current_player: discord.Member,
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

def ttt_board_embed(board: list[list[str]], current_player: discord.Member,
                   p1: discord.Member, p2: discord.Member) -> discord.Embed:
    return ttt_game_embed(board, current_player, p1, p2)  # Alias

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
