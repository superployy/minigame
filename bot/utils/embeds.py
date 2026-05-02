import discord

# ========== ADD THESE MISSING FUNCTIONS ==========
def base_embed(title, description, color_key="info"):
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

def game_embed(title, description, color=discord.Color.purple()):
    """Create game embed"""
    return discord.Embed(title=title, description=description, color=color)

def error_embed(error_message):
    """Create error embed"""
    return discord.Embed(title="❌ Error", description=error_message, color=discord.Color.red())

# ========== YOUR EXISTING FUNCTIONS BELOW ==========
# (Keep all the Tic-Tac-Toe and Trivia functions you already have)

def ttt_game_embed(board: list[list[str]], current_player: discord.Member,
                   p1: discord.Member, p2: discord.Member) -> discord.Embed:
    # ... your existing code ...
    pass

# ... rest of your existing functions ...
