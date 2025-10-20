# handlers/user/start.py
import logging
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from telegram.constants import ParseMode
from keyboards.reply import main_reply_keyboard

# Import the search functions to be called directly
from .search import search_movie, search_series

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the /start command. It now also processes deep links.
    """
    # --- DEEP LINKING LOGIC ---
    if context.args:
        # A deep link was used, e.g., /start mv_Inception
        payload = context.args[0]
        
        if payload.startswith("mv_"):
            # This is a movie deep link
            movie_name_encoded = payload.replace("mv_", "", 1)
            # Replace underscores back with spaces for the search
            movie_name = movie_name_encoded.replace("_", " ")
            
            # We need to manually set the context.args for the search function
            context.args = movie_name.split()
            await update.effective_message.reply_text(f"🎬 Searching for movie: {movie_name}...")
            await search_movie(update, context)
            return # Stop further execution

        elif payload.startswith("sr_"):
            # This is a series deep link
            series_name_encoded = payload.replace("sr_", "", 1)
            series_name = series_name_encoded.replace("_", " ")

            context.args = series_name.split()
            await update.effective_message.reply_text(f"📺 Searching for series: {series_name}...")
            await search_series(update, context)
            return # Stop further execution

    # --- REGULAR /start LOGIC ---
    # If no deep link was found, or if it was an invalid format, show the normal welcome message.
    await update.effective_message.reply_text(
        "🎉 Welcome to the Cineverse Bot!\n\n"
        "Use the menu below to find movies and series.",
        reply_markup=main_reply_keyboard()
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Displays detailed help information using correctly escaped MarkdownV2."""
    text = r"""
📖 *Cineverse Bot Help*

Here's how to use the bot:

*Navigation*
Use the buttons at the bottom of the screen to browse content\.

*Quick Search Commands*
🔹 `/mv <name>` \- Search for a movie\.
   *Example: `/mv inception`*

🔹 `/sr <name>` \- Search for a series\.
   *Example: `/sr breaking bad`*

Enjoy free access to all movies and series\!
"""
    await update.effective_message.reply_text(
        text,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=main_reply_keyboard()
    )

start_handler = CommandHandler("start", start)
help_handler = CommandHandler("help", help_command)