# handlers/user/search.py
import logging
import asyncio
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from database import db_handler
from keyboards.inline import movie_list_keyboard, series_list_keyboard

logger = logging.getLogger(__name__)

async def search_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /mv command to search for movies."""
    query = " ".join(context.args).lower()
    if not query:
        await update.effective_message.reply_text("❌ Please provide a movie name. Example: `/mv inception`")
        return

    all_movies = db_handler.get_all_movies()
    results = [movie for movie in all_movies if query in movie['name'].lower()]

    if not results:
        await update.effective_message.reply_text(f"❌ No movies found matching '{query}'.")
        return

    await update.effective_message.reply_text(
        f"🔎 Found {len(results)} movie(s) matching your search:",
        reply_markup=movie_list_keyboard(results)
    )

async def search_series(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /sr command to search for series."""
    query = " ".join(context.args).lower()
    if not query:
        await update.effective_message.reply_text("❌ Please provide a series name. Example: `/sr game of thrones`")
        return

    all_series = db_handler.get_all_series()
    results = [series for series in all_series if query in series['name'].lower()]

    if not results:
        await update.effective_message.reply_text(f"❌ No series found matching '{query}'.")
        return

    await update.effective_message.reply_text(
        f"🔎 Found {len(results)} series matching your search:",
        reply_markup=series_list_keyboard(results)
    )

async def generic_text_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles generic text messages, attempting to search for movies or series.
    This runs after other specific handlers (like commands or reply keyboard regexes).
    """
    if not update.message or not update.message.text:
        return

    query = update.message.text.strip().lower()

    if not query:
        return

    logger.info(f"User {update.effective_user.id} performing generic search for: '{query}'")

    all_movies = db_handler.get_all_movies()
    movie_results = [movie for movie in all_movies if query in movie['name'].lower()]

    all_series = db_handler.get_all_series()
    series_results = [series for series in all_series if query in series['name'].lower()]

    found_anything = False

    if movie_results:
        await update.effective_message.reply_text(
            f"🔎 Found {len(movie_results)} movie(s) matching '{query}':",
            reply_markup=movie_list_keyboard(movie_results)
        )
        found_anything = True

    if series_results:
        if found_anything:
            await asyncio.sleep(0.5)
        await update.effective_message.reply_text(
            f"🔎 Found {len(series_results)} series matching '{query}':",
            reply_markup=series_list_keyboard(series_results)
        )
        found_anything = True

    if not found_anything:
        await update.effective_message.reply_text(f"❌ No movies or series found matching '{query}'.")

movie_search_handler = CommandHandler("mv", search_movie)
series_search_handler = CommandHandler("sr", search_series)
generic_search_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, generic_text_search)