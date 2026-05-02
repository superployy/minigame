# 🎮 Discord Mini-Games PvP Bot

A fully-featured Discord bot with PvP mini-games: Rock Paper Scissors, Tic-Tac-Toe, and Trivia — deployable to Railway in minutes.

---

## Features

- ✂️ **Rock Paper Scissors** — Button-based, secret choices revealed simultaneously
- ❌ **Tic-Tac-Toe** — Interactive grid with Discord buttons
- ❓ **Trivia** — Multi-round quiz with configurable round count
- 🏆 **Leaderboard** — Global win/loss/draw tracking per player
- ⚙️ **Admin Controls** — Per-server prefix, game channel, enable/disable games
- 🐘 **PostgreSQL** — Persistent stats via SQLAlchemy async

---

## Project Structure

```
├── bot/
│   ├── cogs/
│   │   ├── games/
│   │   │   ├── rock_paper_scissors.py
│   │   │   ├── tic_tac_toe.py
│   │   │   └── trivia.py
│   │   ├── admin.py
│   │   └── general.py
│   ├── database/
│   │   ├── models.py
│   │   └── db_utils.py
│   ├── utils/
│   │   ├── embeds.py
│   │   ├── matchmaking.py
│   │   └── game_logic.py
│   └── main.py
├── requirements.txt
├── Procfile
├── railway.json
└── .env.example
```

---

## 🚀 Deploy to Railway (Step-by-Step)

### 1. Create a Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click **New Application** → give it a name
3. Go to **Bot** tab → click **Add Bot**
4. Under **Privileged Gateway Intents**, enable:
   - ✅ Server Members Intent
   - ✅ Message Content Intent
5. Click **Reset Token** → copy your token (you'll need it)
6. **Invite the bot** to your server:
   ```
   https://discord.com/api/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=277025459200&scope=bot
   ```
   Replace `YOUR_CLIENT_ID` with your bot's Application ID.

### 2. Set Up Railway

1. Go to [railway.app](https://railway.app) and sign in with GitHub
2. Click **New Project** → **Deploy from GitHub repo**
3. Select this repository (fork it first if needed)

### 3. Add a PostgreSQL Database

1. In your Railway project, click **+ New** → **Database** → **PostgreSQL**
2. Railway will automatically set `DATABASE_URL` — copy it for reference

### 4. Set Environment Variables

In Railway → your bot service → **Variables**, add:

| Variable | Value |
|---|---|
| `DISCORD_TOKEN` | Your bot token from step 1 |
| `DATABASE_URL` | Auto-set by Railway PostgreSQL plugin |
| `PREFIX` | `!` (or your preferred prefix) |

### 5. Deploy

Railway auto-deploys when you push to GitHub. Your bot will be online within ~2 minutes.

---

## Commands

### 🎮 Games
| Command | Description |
|---|---|
| `!rps @user` | Challenge to Rock Paper Scissors |
| `!ttt @user` | Challenge to Tic-Tac-Toe |
| `!trivia @user [rounds]` | Challenge to Trivia (1–10 rounds, default 5) |

### 📊 Stats
| Command | Description |
|---|---|
| `!stats [@user]` | View your or another player's stats |
| `!leaderboard` | Top 10 global leaderboard |
| `!ping` | Check bot latency |

### ⚙️ Admin (Manage Server required)
| Command | Description |
|---|---|
| `!setprefix <prefix>` | Change command prefix |
| `!setgamechannel [#channel]` | Restrict games to a channel |
| `!togglegame <rps\|ttt\|trivia>` | Enable/disable a game |
| `!serversettings` | View server configuration |
| `!resetstats @user` | Reset a player's stats (Admin only) |

---

## Local Development

```bash
# Clone
git clone https://github.com/your-username/discord-mini-games-bot
cd discord-mini-games-bot

# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your token and database URL

# Run
python bot/main.py
```

---

## Environment Variables

```env
DISCORD_TOKEN=YOUR_DISCORD_BOT_TOKEN
DATABASE_URL=postgresql://USER:PASSWORD@HOST:PORT/DATABASE
PREFIX=!
```
