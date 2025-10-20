# handlers/user/browsing.py
import logging
import asyncio
from telegram import Update
from telegram.error import BadRequest
from telegram.ext import ContextTypes, CallbackQueryHandler
from telegram.constants import ParseMode
from telegram.helpers import escape_markdown

from database import db_handler
from keyboards import inline as keyboards
from utils import constants as const
from utils.helpers import schedule_content_deletion

logger = logging.getLogger(__name__)

# --- CORE LOGIC: Helper functions for sending files ---

# These helpers are called by the decorated handlers, so they don't need the decorator themselves.
async def _send_movie_files(context: ContextTypes.DEFAULT_TYPE, chat_id: int, movie: dict, photo_message_id: int):
    video_tasks = [
        context.bot.send_video(chat_id=chat_id, video=video_id, caption=f"🎬 {movie['name']}")
        for video_id in movie['videos']
    ]
    video_message_ids = []
    try:
        sent_messages = await asyncio.gather(*video_tasks)
        video_message_ids = [msg.message_id for msg in sent_messages]
    except Exception as e:
        logger.error(f"Failed to send a video for movie {movie['id']}: {e}")
        await context.bot.send_message(chat_id=chat_id, text="⚠️ An error occurred while sending a video file.")

    if video_message_ids or photo_message_id:
        schedule_content_deletion(
            context, chat_id, video_message_ids, photo_message_id, movie['timer'],
            'movie', movie['id'], movie['name']
        )
        if movie['timer'] > 0:
            await asyncio.sleep(1)
            await context.bot.send_message(
                chat_id=chat_id, text=const.DELETION_WARNING_TEXT.format(timer=movie['timer']),
                parse_mode=ParseMode.MARKDOWN
            )
    
    if const.THANK_YOU_STICKER_ID:
        await asyncio.sleep(0.5)
        try:
            await context.bot.send_sticker(chat_id=chat_id, sticker=const.THANK_YOU_STICKER_ID)
        except BadRequest as e:
            logger.error(f"Failed to send sticker. ID might be invalid: {e}")

async def _send_series_season_files(context: ContextTypes.DEFAULT_TYPE, chat_id: int, series: dict, season_num: str, photo_message_id: int):
    episodes = series['seasons'][season_num]
    video_message_ids = []

    for idx, episode_id in enumerate(episodes, 1):
        try:
            caption = f"📺 {series['name']} - S{season_num}E{idx}"
            sent_message = await context.bot.send_video(chat_id=chat_id, video=episode_id, caption=caption)
            video_message_ids.append(sent_message.message_id)
            await asyncio.sleep(0.5)
        except Exception as e:
            logger.error(f"Failed to send episode S{season_num}E{idx} for series {series['id']}: {e}")
            await context.bot.send_message(chat_id=chat_id, text=f"⚠️ An error occurred while sending episode S{season_num}E{idx}.")

    if video_message_ids or photo_message_id:
        schedule_content_deletion(
            context, chat_id, video_message_ids, photo_message_id, series['timer'],
            'series', series['id'], f"{series['name']} S{season_num}"
        )
        if series['timer'] > 0:
            await asyncio.sleep(1)
            await context.bot.send_message(
                chat_id=chat_id, text=const.DELETION_WARNING_TEXT.format(timer=series['timer']),
                parse_mode=ParseMode.MARKDOWN
            )
    
    if const.THANK_YOU_STICKER_ID:
        await asyncio.sleep(0.5)
        try:
            await context.bot.send_sticker(chat_id=chat_id, sticker=const.THANK_YOU_STICKER_ID)
        except BadRequest as e:
            logger.error(f"Failed to send sticker. ID might be invalid: {e}")

# --- HANDLERS (Triggered by Reply Keyboard or Commands) ---

async def show_all_movies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    movies = db_handler.get_all_movies()
    if not movies: await update.message.reply_text("ℹ️ No movies have been added yet."); return
    await update.message.reply_text("Displaying movies (Page 1):", reply_markup=keyboards.movie_list_keyboard(movies, page=0))

async def show_all_series(update: Update, context: ContextTypes.DEFAULT_TYPE):
    series = db_handler.get_all_series()
    if not series: await update.message.reply_text("ℹ️ No series have been added yet."); return
    await update.message.reply_text("Displaying series (Page 1):", reply_markup=keyboards.series_list_keyboard(series, page=0))

async def show_browse_by_year(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Select a year to browse:", reply_markup=keyboards.year_selection_keyboard())

async def show_browse_by_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends the first page of the category selection menu."""
    await update.message.reply_text("Select a category to browse:", reply_markup=keyboards.category_selection_keyboard(page=0))

# --- CALLBACK HANDLERS (Triggered by Inline Buttons) ---

# These handlers are usually for navigation or fetching *lists*, not directly accessing content files.
# So, they don't *strictly* need premium_only, as the content selection handlers below will catch it.
# However, if you want the premium check to happen earlier (before showing lists), you can add it.
# For now, I'll keep it on the actual content-delivery steps.

async def handle_back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try: await query.edit_message_text("✅ Selection cancelled. Use the menu below.")
    except BadRequest as e:
        if "Message is not modified" not in str(e): logger.warning(f"Error handling back button: {e}")

async def back_to_year_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Select a year to browse:", reply_markup=keyboards.year_selection_keyboard())

async def movie_page_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    page = int(query.data.replace(const.CALLBACK_MOVIE_PAGE, ""))
    movies = db_handler.get_all_movies()
    await query.edit_message_text(f"Displaying movies (Page {page+1}):", reply_markup=keyboards.movie_list_keyboard(movies, page=page))

async def series_page_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    page = int(query.data.replace(const.CALLBACK_SERIES_PAGE, ""))
    series = db_handler.get_all_series()
    await query.edit_message_text(f"Displaying series (Page {page+1}):", reply_markup=keyboards.series_list_keyboard(series, page=page))

async def year_page_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    page = int(query.data.split('_')[-1])
    try: await query.edit_message_reply_markup(reply_markup=keyboards.year_selection_keyboard(page=page))
    except BadRequest as e:
        if "Message is not modified" not in str(e): logger.warning(f"Error on year page handler: {e}")

async def year_select_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    year = int(query.data.split('_')[-1])
    try: await query.edit_message_text(f"What would you like to see from {year}?", reply_markup=keyboards.year_content_type_keyboard(year))
    except BadRequest as e:
        if "Message is not modified" not in str(e): logger.warning(f"Error on year select handler: {e}")

async def year_content_type_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    parts = query.data.split('_')
    year, content_type = int(parts[-2]), parts[-1]
    try:
        if content_type == "movies":
            content = [m for m in db_handler.get_all_movies() if m.get('year') == year]
            if not content: await query.edit_message_text(f"No movies found for {year}.", reply_markup=keyboards.year_content_type_keyboard(year)); return
            await query.edit_message_text(f"Movies from {year}:", reply_markup=keyboards.movie_list_keyboard(content))
        else:
            content = [s for s in db_handler.get_all_series() if s.get('year') == year]
            if not content: await query.edit_message_text(f"No series found for {year}.", reply_markup=keyboards.year_content_type_keyboard(year)); return
            await query.edit_message_text(f"Series from {year}:", reply_markup=keyboards.series_list_keyboard(content))
    except BadRequest as e:
        if "Message is not modified" not in str(e): logger.warning(f"Error on year content type handler: {e}")

async def category_page_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    page = int(query.data.replace(const.CALLBACK_CATEGORY_PAGE, ""))
    await query.edit_message_reply_markup(reply_markup=keyboards.category_selection_keyboard(page=page))

async def category_select_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    category = query.data.replace(const.CALLBACK_CATEGORY_SELECT, "")
    await query.edit_message_text(f"What would you like to see from the '{category}' category?", reply_markup=keyboards.category_content_type_keyboard(category))

async def category_content_type_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    parts = query.data.replace(const.CALLBACK_CATEGORY_CONTENT_TYPE, "").split('_')
    category, content_type = parts[0], parts[1]
    
    if content_type == "movies":
        content = [m for m in db_handler.get_all_movies() if category in m.get('categories', [])]
        if not content:
            await query.edit_message_text(f"No movies found in the '{category}' category.", reply_markup=keyboards.category_content_type_keyboard(category)); return
        await query.edit_message_text(f"Movies in '{category}':", reply_markup=keyboards.movie_list_keyboard(content))
    else: # series
        content = [s for s in db_handler.get_all_series() if category in s.get('categories', [])]
        if not content:
            await query.edit_message_text(f"No series found in the '{category}' category.", reply_markup=keyboards.category_content_type_keyboard(category)); return
        await query.edit_message_text(f"Series in '{category}':", reply_markup=keyboards.series_list_keyboard(content))

async def movie_select_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    movie_id = query.data.replace(const.CALLBACK_MOVIE_SELECT, "")
    movie = db_handler.find_movie_by_id(movie_id)
    if not movie: await query.edit_message_text("❌ Movie not found."); return
    await query.delete_message()
    safe_name = escape_markdown(movie['name'], version=2)
    caption = rf"🎬 *{safe_name}* `({movie['year']})`"
    photo_message = await query.message.reply_photo(photo=movie['cover_photo'], caption=caption, parse_mode=ParseMode.MARKDOWN_V2)
    await _send_movie_files(context, query.message.chat_id, movie, photo_message.message_id)

async def series_select_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    series_id = query.data.replace(const.CALLBACK_SERIES_SELECT, "")
    series = db_handler.find_series_by_id(series_id)
    if not series: await query.edit_message_text("❌ Series not found."); return
    await query.delete_message()
    
    # Apply MarkdownV2 escaping for the caption
    safe_name = escape_markdown(series['name'], version=2)
    safe_year = escape_markdown(str(series['year']), version=2)
    caption = rf"📺 *{safe_name}* `\({safe_year}\)`\n\nSelect a season:" # Escaped parentheses for year

    photo_message_with_seasons = await query.message.reply_photo(photo=series['cover_photo'], caption=caption, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=keyboards.series_season_keyboard(series))
    context.user_data[f"photo_msg_{series_id}"] = photo_message_with_seasons.message_id

async def season_select_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data_parts = query.data.replace(const.CALLBACK_SEASON_SELECT, "").split('_')
    series_id, season_num = data_parts[0], data_parts[1]
    series = db_handler.find_series_by_id(series_id)
    if not series or season_num not in series['seasons']: await query.edit_message_text("❌ Season not found."); return
    photo_message_id = context.user_data.get(f"photo_msg_{series_id}")
    await query.edit_message_reply_markup(reply_markup=None)
    
    # Apply MarkdownV2 escaping for the text message
    safe_name = escape_markdown(series['name'], version=2)
    safe_season_num = escape_markdown(season_num, version=2)
    text = rf"Sending all episodes for *{safe_name} \- Season {safe_season_num}*\.\.\." # Escaped period

    await query.message.reply_text(text, parse_mode=ParseMode.MARKDOWN_V2)
    await _send_series_season_files(context, query.message.chat_id, series, season_num, photo_message_id)

async def reget_movie_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    movie_id = query.data.replace(const.CALLBACK_REGET_MOVIE, "")
    movie = db_handler.find_movie_by_id(movie_id)
    if not movie: await query.edit_message_text("❌ This movie seems to have been removed."); return
    safe_name = escape_markdown(movie['name'], version=2)
    text = rf"Re\-sending files for *{safe_name}*\.\.\."
    await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN_V2)
    caption = rf"🎬 *{safe_name}* `({movie['year']})`"
    photo_message = await query.message.reply_photo(photo=movie['cover_photo'], caption=caption, parse_mode=ParseMode.MARKDOWN_V2)
    await _send_movie_files(context, query.message.chat_id, movie, photo_message.message_id)

async def reget_series_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    series_id = query.data.replace(const.CALLBACK_REGET_SERIES, "")
    series = db_handler.find_series_by_id(series_id)
    if not series: await query.edit_message_text("❌ This series seems to have been removed."); return
    
    # Apply MarkdownV2 escaping for the text message
    safe_name = escape_markdown(series['name'], version=2)
    safe_year = escape_markdown(str(series['year']), version=2)
    text = rf"📺 *{safe_name}* `\({safe_year}\)`\n\nWhich season would you like to get again\?" # Escaped parentheses and question mark

    await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=keyboards.series_season_keyboard(series))

browsing_handlers = [
    CallbackQueryHandler(handle_back_to_main, pattern="^back_to_main_menu$"),
    CallbackQueryHandler(back_to_year_selection, pattern="^browse_year_from_callback$"),
    CallbackQueryHandler(show_browse_by_category, pattern="^browse_category_from_callback$"),
    CallbackQueryHandler(movie_page_handler, pattern=f"^{const.CALLBACK_MOVIE_PAGE}"),
    CallbackQueryHandler(series_page_handler, pattern=f"^{const.CALLBACK_SERIES_PAGE}"),
    CallbackQueryHandler(year_page_handler, pattern=f"^{const.CALLBACK_YEAR_PAGE}"),
    CallbackQueryHandler(category_page_handler, pattern=f"^{const.CALLBACK_CATEGORY_PAGE}"),
    CallbackQueryHandler(year_select_handler, pattern=f"^{const.CALLBACK_YEAR_SELECT}"),
    CallbackQueryHandler(category_select_handler, pattern=f"^{const.CALLBACK_CATEGORY_SELECT}"),
    CallbackQueryHandler(year_content_type_handler, pattern=f"^{const.CALLBACK_YEAR_CONTENT_TYPE}"),
    CallbackQueryHandler(category_content_type_handler, pattern=f"^{const.CALLBACK_CATEGORY_CONTENT_TYPE}"),
    CallbackQueryHandler(movie_select_handler, pattern=f"^{const.CALLBACK_MOVIE_SELECT}"),
    CallbackQueryHandler(series_select_handler, pattern=f"^{const.CALLBACK_SERIES_SELECT}"),
    CallbackQueryHandler(season_select_handler, pattern=f"^{const.CALLBACK_SEASON_SELECT}"),
    CallbackQueryHandler(reget_movie_handler, pattern=f"^{const.CALLBACK_REGET_MOVIE}"),
    CallbackQueryHandler(reget_series_handler, pattern=f"^{const.CALLBACK_REGET_SERIES}"),
]