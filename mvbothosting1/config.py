# config.py

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- REQUIRED ---
# Get your bot token from @BotFather on Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN")

# --- REQUIRED ---
# Get your numeric Telegram user ID, e.g., from @userinfobot
# You can add multiple admin IDs, separated by commas
ADMIN_IDS = [6158106622, 1661108890] 

# --- OPTIONAL: FORCE JOIN FEATURE ---
# Add your channel's username (e.g., "@mychannelname"). 
# The bot MUST be an admin in this channel.
# If you don't want this feature, set it to None.
# Example: FORCE_JOIN_CHANNEL = "@your_channel_username"
FORCE_JOIN_CHANNEL = None
