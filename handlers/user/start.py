# handlers/user/start.py
import logging
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from telegram.constants import ParseMode
from telegram.helpers import escape_markdown
from keyboards.reply import main_reply_keyboard
from keyboards.inline import deeplink_retrieval_keyboard, series_season_keyboard
from database import db_handler

# Import the helper functions for sending files
from .browsing import _send_movie_files, _send_series_season_files

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
            
            # Show intermediate message with button
            await update.effective_message.reply_text(
                "⚜️ ဇာတ်ကားရပါပြီ ⚜️\n\n"
                "Copyright ပြဿနာများကိုရှောင်ရှားရန်အတွက်\n"
                "Bot အခွဲများကို အသုံးပြုပါသည်‼️",
                reply_markup=deeplink_retrieval_keyboard('movie', movie_name)
            )
            return # Stop further execution

        elif payload.startswith("sr_"):
            # This is a series deep link
            series_name_encoded = payload.replace("sr_", "", 1)
            series_name = series_name_encoded.replace("_", " ")

            # Show intermediate message with button
            await update.effective_message.reply_text(
                "⚜️ ဇာတ်ကားရပါပြီ ⚜️\n\n"
                "Copyright ပြဿနာများကိုရှောင်ရှားရန်အတွက်\n"
                "Bot အခွဲများကို အသုံးပြုပါသည်‼️",
                reply_markup=deeplink_retrieval_keyboard('series', series_name)
            )
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

async def deeplink_retrieval_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the callback when user clicks the retrieval button from deep link."""
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data
    
    # Determine if it's a movie or series
    if callback_data.startswith("deeplink_movie_"):
        movie_name = callback_data.replace("deeplink_movie_", "")
        
        # Search for the movie by name
        all_movies = db_handler.get_all_movies()
        movie = next((m for m in all_movies if m['name'].lower() == movie_name.lower()), None)
        
        if not movie:
            await query.edit_message_text("❌ Movie not found.")
            return
        
        # Delete the intermediate message
        await query.delete_message()
        
        # Send the movie directly (like movie_select_handler does)
        safe_name = escape_markdown(movie['name'], version=2)
        caption = rf"🎬 *{safe_name}* `({movie['year']})`"
        photo_message = await query.message.reply_photo(
            photo=movie['cover_photo'], 
            caption=caption, 
            parse_mode=ParseMode.MARKDOWN_V2
        )
        await _send_movie_files(context, query.message.chat_id, movie, photo_message.message_id)
        
    elif callback_data.startswith("deeplink_series_"):
        series_name = callback_data.replace("deeplink_series_", "")
        
        # Search for the series by name
        all_series = db_handler.get_all_series()
        series = next((s for s in all_series if s['name'].lower() == series_name.lower()), None)
        
        if not series:
            await query.edit_message_text("❌ Series not found.")
            return
        
        # Delete the intermediate message
        await query.delete_message()
        
        # Send the series cover photo with season selection (like series_select_handler does)
        safe_name = escape_markdown(series['name'], version=2)
        safe_year = escape_markdown(str(series['year']), version=2)
        caption = rf"📺 *{safe_name}* `\({safe_year}\)`\n\nSelect a season:"
        
        photo_message_with_seasons = await query.message.reply_photo(
            photo=series['cover_photo'], 
            caption=caption, 
            parse_mode=ParseMode.MARKDOWN_V2, 
            reply_markup=series_season_keyboard(series)
        )
        context.user_data[f"photo_msg_{series['id']}"] = photo_message_with_seasons.message_id

start_handler = CommandHandler("start", start)
help_handler = CommandHandler("help", help_command)