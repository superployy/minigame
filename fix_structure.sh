mkdir -p bot
mv main.py bot/
mv cogs bot/ 2>/dev/null || true
mv database bot/ 2>/dev/null || true
mv utils bot/ 2>/dev/null || true
mv models bot/ 2>/dev/null || true
