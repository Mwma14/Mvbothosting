# handlers/admin/admin_panel.py
import logging, uuid
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes, ConversationHandler, CommandHandler,
    CallbackQueryHandler, MessageHandler, filters,
)
from database import db_handler
from keyboards import inline as keyboards
from keyboards.reply import done_uploading_reply_keyboard, main_reply_keyboard # Ensure main_reply_keyboard is imported
from utils import constants as const
from utils.decorators import admin_only
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)

# --- Entry Point ---
@admin_only
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Welcome to the Admin Panel. Choose an action:", reply_markup=keyboards.admin_panel_keyboard())
    return const.SELECTING_ACTION

# --- Add Content Flow ---
async def start_add_content(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    content_type = "Movie" if query.data == const.CALLBACK_ADMIN_ADD_MOVIE else "Series"
    context.user_data['content_type'] = content_type
    context.user_data['videos'] = []
    context.user_data['seasons'] = {}
    await query.edit_message_text(f"🎬 Send the name for the new {content_type}.", reply_markup=keyboards.cancel_keyboard())
    return const.GET_NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['name'] = update.message.text
    await update.message.reply_text(f"🖼️ Great! Now, send the cover photo for '{context.user_data['name']}'.", reply_markup=keyboards.cancel_keyboard())
    return const.GET_PHOTO

async def get_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['cover_photo'] = update.message.photo[-1].file_id
    await update.message.reply_text("🗓️ Got it. Now, please enter the release year (e.g., 2023).", reply_markup=keyboards.cancel_keyboard())
    return const.GET_YEAR

async def get_year(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        context.user_data['year'] = int(update.message.text)
        await update.message.reply_text(
            "📚 Enter the categories for this item, separated by commas.\n"
            "Example: `Action, Comedy, Sci-Fi`",
            parse_mode='Markdown',
            reply_markup=keyboards.cancel_keyboard()
        )
        return const.GET_CATEGORIES
    except ValueError:
        await update.message.reply_text("❌ Invalid year. Please enter a number (e.g., 2023).")
        return const.GET_YEAR

async def get_categories(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores categories and asks for the delete timer."""
    categories_raw = update.message.text
    categories_list = [cat.strip().capitalize() for cat in categories_raw.split(',')]
    context.user_data['categories'] = categories_list
    await update.message.reply_text(
        "⏳ Enter the auto-delete timer in minutes (e.g., 15). Enter 0 for no timer.",
        reply_markup=keyboards.cancel_keyboard()
    )
    return const.GET_TIMER

async def get_timer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        timer = int(update.message.text)
        context.user_data['timer'] = timer
        if context.user_data['content_type'] == "Movie":
            await update.message.reply_text("🎥 Please forward the movie file(s). Click 'Done Uploading' below when finished.", reply_markup=done_uploading_reply_keyboard())
            return const.GET_CONTENT_VIDEOS
        else:
            await update.message.reply_text("🔢 How many seasons does this series have?", reply_markup=keyboards.cancel_keyboard())
            return const.GET_SERIES_SEASON_COUNT
    except ValueError:
        await update.message.reply_text("❌ Invalid timer. Please enter a number (e.g., 15).")
        return const.GET_TIMER

async def get_content_videos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.video:
        context.user_data['videos'].append(update.message.video.file_id)
        await update.message.reply_text(f"✅ Video #{len(context.user_data['videos'])} received. Forward more or click Done.")
    return const.GET_CONTENT_VIDEOS

async def get_season_count(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        count = int(update.message.text)
        if count <= 0: raise ValueError()
        context.user_data['season_total'] = count
        context.user_data['current_season'] = 1
        await update.message.reply_text(f"🎥 Forward all episodes for **Season 1**. Click 'Done Uploading' below when finished.", reply_markup=done_uploading_reply_keyboard(), parse_mode='Markdown')
        return const.GET_SERIES_EPISODES
    except ValueError:
        await update.message.reply_text("❌ Invalid number. Please enter a positive integer.")
        return const.GET_SERIES_SEASON_COUNT

async def get_series_episodes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    season_key = str(context.user_data['current_season'])
    if season_key not in context.user_data['seasons']:
        context.user_data['seasons'][season_key] = []
    if update.message.video:
        context.user_data['seasons'][season_key].append(update.message.video.file_id)
        await update.message.reply_text(f"✅ Season {season_key}, Episode #{len(context.user_data['seasons'][season_key])} received.")
    return const.GET_SERIES_EPISODES

async def done_uploading(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message, content_type = update.message, context.user_data.get('content_type')
    user_id = update.effective_user.id
    if not content_type:
        await message.reply_text("An error occurred. Please /admin again.", reply_markup=main_reply_keyboard(user_id))
        return ConversationHandler.END

    if content_type == "Movie":
        if not context.user_data.get('videos'):
            await message.reply_text("❌ You haven't added any videos!", reply_markup=done_uploading_reply_keyboard())
            return const.GET_CONTENT_VIDEOS
        movie_data = {"id": str(uuid.uuid4()), **context.user_data}
        db_handler.add_movie(movie_data)
        await message.reply_text(f"✅ Movie '{movie_data['name']}' added!", reply_markup=main_reply_keyboard(user_id))
    else:
        current_season, total_seasons = context.user_data.get('current_season', 1), context.user_data.get('season_total', 1)
        if not context.user_data.get('seasons', {}).get(str(current_season)):
            await message.reply_text(f"❌ You haven't added episodes for Season {current_season}!", reply_markup=done_uploading_reply_keyboard())
            return const.GET_SERIES_EPISODES
        if current_season < total_seasons:
            context.user_data['current_season'] += 1
            await message.reply_text(f"🎥 Season {current_season} done. Forward episodes for **Season {context.user_data['current_season']}**.", reply_markup=done_uploading_reply_keyboard(), parse_mode='Markdown')
            return const.GET_SERIES_EPISODES
        else:
            series_data = {"id": str(uuid.uuid4()), **context.user_data}
            db_handler.add_series(series_data)
            await message.reply_text(f"✅ Series '{series_data['name']}' added!", reply_markup=main_reply_keyboard(user_id))

    context.user_data.clear()
    return ConversationHandler.END

async def start_delete_content(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    is_movie = query.data == const.CALLBACK_ADMIN_DELETE_MOVIE
    content_list = db_handler.get_all_movies() if is_movie else db_handler.get_all_series()
    if not content_list:
        await query.edit_message_text(f"No {'movies' if is_movie else 'series'} to delete."); return ConversationHandler.END
    keyboard = [[InlineKeyboardButton(f"❌ {item['name']}", callback_data=f"{(const.CALLBACK_DELETE_MOVIE if is_movie else const.CALLBACK_DELETE_SERIES)}{item['id']}")] for item in content_list]
    keyboard.append([InlineKeyboardButton("🔙 Back to Admin Panel", callback_data=const.CALLBACK_ADMIN_CANCEL)])
    await query.edit_message_text(f"Select the {'movie' if is_movie else 'series'} to delete:", reply_markup=InlineKeyboardMarkup(keyboard))
    return const.CONFIRM_DELETE

async def confirm_delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    is_movie = query.data.startswith(const.CALLBACK_DELETE_MOVIE)
    content_id = query.data.replace(const.CALLBACK_DELETE_MOVIE if is_movie else const.CALLBACK_DELETE_SERIES, "")
    content = (db_handler.find_movie_by_id(content_id) if is_movie else db_handler.find_series_by_id(content_id))
    if content:
        (db_handler.delete_movie_by_id(content_id) if is_movie else db_handler.delete_series_by_id(content_id))
        await query.edit_message_text(f"✅ Successfully deleted '{content['name']}'.")
    else:
        await query.edit_message_text("❌ Content not found or already deleted.")
    await query.message.reply_text("Admin Panel:", reply_markup=keyboards.admin_panel_keyboard())
    return ConversationHandler.END

async def start_rename_content(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    is_movie = query.data == const.CALLBACK_ADMIN_RENAME_MOVIE
    context.user_data['is_movie'] = is_movie
    content_list = db_handler.get_all_movies() if is_movie else db_handler.get_all_series()
    if not content_list:
        await query.edit_message_text(f"No {'movies' if is_movie else 'series'} to rename."); return ConversationHandler.END
    keyboard = [[InlineKeyboardButton(f"✏️ {item['name']}", callback_data=f"{(const.CALLBACK_RENAME_MOVIE if is_movie else const.CALLBACK_RENAME_SERIES)}{item['id']}")] for item in content_list]
    keyboard.append([InlineKeyboardButton("🔙 Back to Admin Panel", callback_data=const.CALLBACK_ADMIN_CANCEL)])
    await query.edit_message_text(f"Select the {'movie' if is_movie else 'series'} to rename:", reply_markup=InlineKeyboardMarkup(keyboard))
    return const.SELECT_RENAME_ITEM

async def get_item_to_rename(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    is_movie = context.user_data['is_movie']
    content_id = query.data.replace(const.CALLBACK_RENAME_MOVIE if is_movie else const.CALLBACK_RENAME_SERIES, "")
    context.user_data['content_id'] = content_id
    content = db_handler.find_movie_by_id(content_id) if is_movie else db_handler.find_series_by_id(content_id)
    if not content:
        await query.edit_message_text("Content not found."); return ConversationHandler.END
    await query.edit_message_text(f"Current name: `{content['name']}`\n\nPlease send the new name.", parse_mode='Markdown', reply_markup=keyboards.cancel_keyboard())
    return const.GET_NEW_NAME

async def get_new_name_and_save(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    new_name, is_movie, content_id = update.message.text, context.user_data['is_movie'], context.user_data['content_id']
    user_id = update.effective_user.id
    all_content = db_handler.get_all_movies() if is_movie else db_handler.get_all_series()
    for item in all_content:
        if item['id'] == content_id:
            item['name'] = new_name; break
    (db_handler.save_data(db_handler.MOVIES_DB_PATH, all_content) if is_movie else db_handler.save_data(db_handler.SERIES_DB_PATH, all_content))
    await update.message.reply_text(f"✅ Successfully renamed to '{new_name}'.", reply_markup=main_reply_keyboard(user_id))
    context.user_data.clear()
    return ConversationHandler.END

# --- NEW: Edit Series Flow ---
async def start_edit_series(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Entry point for editing series."""
    query = update.callback_query
    await query.answer()
    series_list = db_handler.get_all_series()
    if not series_list:
        await query.edit_message_text("No series available to edit.")
        return ConversationHandler.END
    await query.edit_message_text("Select a series to edit:", reply_markup=keyboards.edit_series_list_keyboard(series_list, page=0))
    return const.SELECT_EDIT_SERIES

async def handle_edit_series_pagination(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle pagination of series list."""
    query = update.callback_query
    await query.answer()
    page = int(query.data.replace(const.CALLBACK_EDIT_SERIES_PAGE, ""))
    series_list = db_handler.get_all_series()
    await query.edit_message_text("Select a series to edit:", reply_markup=keyboards.edit_series_list_keyboard(series_list, page=page))
    return const.SELECT_EDIT_SERIES

async def select_series_for_edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """When a series is selected, show its seasons."""
    query = update.callback_query
    await query.answer()
    series_id = query.data.replace(const.CALLBACK_EDIT_SERIES_SELECT, "")
    series = db_handler.find_series_by_id(series_id)
    if not series:
        await query.edit_message_text("Series not found.")
        return ConversationHandler.END
    context.user_data['edit_series_id'] = series_id
    await query.edit_message_text(
        f"Editing: **{series['name']}**\n\nSelect a season to edit:",
        parse_mode='Markdown',
        reply_markup=keyboards.edit_season_selection_keyboard(series)
    )
    return const.SELECT_EDIT_SEASON

async def select_season_for_edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """When a season is selected, show add/remove options."""
    query = update.callback_query
    await query.answer()
    data = query.data.replace(const.CALLBACK_EDIT_SEASON_SELECT, "")
    series_id, season_num = data.split("_")
    series = db_handler.find_series_by_id(series_id)
    if not series or season_num not in series['seasons']:
        await query.edit_message_text("Season not found.")
        return ConversationHandler.END
    context.user_data['edit_season_num'] = season_num
    await query.edit_message_text(
        f"Season {season_num} - {len(series['seasons'][season_num])} episodes\n\nWhat would you like to do?",
        reply_markup=keyboards.edit_action_keyboard()
    )
    return const.SELECT_EDIT_ACTION

async def start_add_episodes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start adding episodes to the selected season."""
    query = update.callback_query
    await query.answer()
    series_id = context.user_data['edit_series_id']
    season_num = context.user_data['edit_season_num']
    series = db_handler.find_series_by_id(series_id)
    if not series or season_num not in series['seasons']:
        await query.edit_message_text("Season not found.")
        return ConversationHandler.END
    existing_count = len(series['seasons'][season_num])
    context.user_data['new_episodes'] = []
    await query.delete_message()
    await query.message.reply_text(
        f"📹 Season {season_num} currently has {existing_count} episodes.\n\n"
        f"Forward the new episode videos. They will be numbered starting from Episode {existing_count + 1}.\n\n"
        f"Click 'Done Uploading' when finished.",
        reply_markup=done_uploading_reply_keyboard()
    )
    return const.ADD_SERIES_EPISODES

async def handle_add_episode_upload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle episode video uploads."""
    if update.message.video:
        context.user_data['new_episodes'].append(update.message.video.file_id)
        series_id = context.user_data['edit_series_id']
        season_num = context.user_data['edit_season_num']
        series = db_handler.find_series_by_id(series_id)
        if series and season_num in series['seasons']:
            existing_count = len(series['seasons'][season_num])
            new_episode_num = existing_count + len(context.user_data['new_episodes'])
            await update.message.reply_text(f"✅ Episode {new_episode_num} received.")
    return const.ADD_SERIES_EPISODES

async def done_adding_episodes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Save the new episodes to the series."""
    series_id = context.user_data['edit_series_id']
    season_num = context.user_data['edit_season_num']
    new_episodes = context.user_data.get('new_episodes', [])
    
    if not new_episodes:
        await update.message.reply_text("❌ You haven't added any episodes!", reply_markup=done_uploading_reply_keyboard())
        return const.ADD_SERIES_EPISODES
    
    user_id = update.effective_user.id
    series = db_handler.find_series_by_id(series_id)
    if not series or season_num not in series['seasons']:
        await update.message.reply_text("❌ Series or season not found!", reply_markup=main_reply_keyboard(user_id))
        context.user_data.clear()
        return ConversationHandler.END
    
    series['seasons'][season_num].extend(new_episodes)
    db_handler.update_series(series_id, series)
    
    await update.message.reply_text(
        f"✅ Successfully added {len(new_episodes)} episode(s) to Season {season_num} of '{series['name']}'!",
        reply_markup=main_reply_keyboard(user_id)
    )
    context.user_data.clear()
    return ConversationHandler.END

async def start_remove_episodes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show episodes that can be removed."""
    query = update.callback_query
    await query.answer()
    series_id = context.user_data['edit_series_id']
    season_num = context.user_data['edit_season_num']
    series = db_handler.find_series_by_id(series_id)
    if not series or season_num not in series['seasons']:
        await query.edit_message_text("Season not found.")
        return ConversationHandler.END
    episodes = series['seasons'][season_num]
    
    if not episodes:
        await query.edit_message_text("No episodes to remove.")
        return ConversationHandler.END
    
    await query.edit_message_text(
        f"Season {season_num} - Select episodes to remove:",
        reply_markup=keyboards.remove_episode_keyboard(series_id, season_num, episodes)
    )
    return const.REMOVE_SERIES_EPISODES

async def handle_remove_episode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Remove a specific episode."""
    query = update.callback_query
    await query.answer()
    data = query.data.replace(const.CALLBACK_REMOVE_EPISODE, "")
    series_id, season_num, episode_index = data.split("_")
    episode_index = int(episode_index)
    
    series = db_handler.find_series_by_id(series_id)
    if not series or season_num not in series['seasons']:
        await query.edit_message_text("Season not found.")
        return ConversationHandler.END
    
    if episode_index < 0 or episode_index >= len(series['seasons'][season_num]):
        await query.answer("Episode not found.", show_alert=True)
        return const.REMOVE_SERIES_EPISODES
    
    removed_episode = series['seasons'][season_num].pop(episode_index)
    db_handler.update_series(series_id, series)
    
    user_id = update.effective_user.id
    episodes = series['seasons'][season_num]
    if not episodes:
        await query.edit_message_text(
            f"✅ Episode {episode_index + 1} removed. No episodes left in Season {season_num}.",
            reply_markup=main_reply_keyboard(user_id)
        )
        context.user_data.clear()
        return ConversationHandler.END
    
    await query.edit_message_text(
        f"✅ Episode {episode_index + 1} removed.\n\nSeason {season_num} now has {len(episodes)} episode(s). Select another to remove or click Done:",
        reply_markup=keyboards.remove_episode_keyboard(series_id, season_num, episodes)
    )
    return const.REMOVE_SERIES_EPISODES

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    user_id = update.effective_user.id
    if update.callback_query:
        await update.callback_query.answer()
        # Edit the message where the inline keyboard was, if possible
        try:
            await update.callback_query.edit_message_text("Operation cancelled.", reply_markup=main_reply_keyboard(user_id))
        except Exception as e:
            logger.warning(f"Could not edit message on cancel via callback: {e}")
            await update.callback_query.message.reply_text("Operation cancelled.", reply_markup=main_reply_keyboard(user_id))
    else:
        await update.message.reply_text("Operation cancelled.", reply_markup=main_reply_keyboard(user_id))
    return ConversationHandler.END

admin_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler("admin", admin_panel)],
    states={
        const.SELECTING_ACTION: [
            CallbackQueryHandler(start_add_content, pattern=f"^{const.CALLBACK_ADMIN_ADD_MOVIE}$|^{const.CALLBACK_ADMIN_ADD_SERIES}$"),
            CallbackQueryHandler(start_delete_content, pattern=f"^{const.CALLBACK_ADMIN_DELETE_MOVIE}$|^{const.CALLBACK_ADMIN_DELETE_SERIES}$"),
            CallbackQueryHandler(start_rename_content, pattern=f"^{const.CALLBACK_ADMIN_RENAME_MOVIE}$|^{const.CALLBACK_ADMIN_RENAME_SERIES}$"),
            CallbackQueryHandler(start_edit_series, pattern=f"^{const.CALLBACK_ADMIN_EDIT_SERIES}$"),
        ],
        const.GET_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
        const.GET_PHOTO: [MessageHandler(filters.PHOTO, get_photo)],
        const.GET_YEAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_year)],
        const.GET_CATEGORIES: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_categories)],
        const.GET_TIMER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_timer)],
        const.GET_CONTENT_VIDEOS: [MessageHandler(filters.VIDEO, get_content_videos), MessageHandler(filters.Regex("^✅ Done Uploading$"), done_uploading)],
        const.GET_SERIES_SEASON_COUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_season_count)],
        const.GET_SERIES_EPISODES: [MessageHandler(filters.VIDEO, get_series_episodes), MessageHandler(filters.Regex("^✅ Done Uploading$"), done_uploading)],
        const.CONFIRM_DELETE: [CallbackQueryHandler(confirm_delete, pattern=f"^{const.CALLBACK_DELETE_MOVIE}|^({const.CALLBACK_DELETE_SERIES})"), CallbackQueryHandler(cancel, pattern=f"^{const.CALLBACK_ADMIN_CANCEL}$")],
        const.SELECT_RENAME_ITEM: [CallbackQueryHandler(get_item_to_rename, pattern=f"^{const.CALLBACK_RENAME_MOVIE}|^({const.CALLBACK_RENAME_SERIES})")],
        const.GET_NEW_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_new_name_and_save)],
        # --- NEW Edit Series States Handlers ---
        const.SELECT_EDIT_SERIES: [
            CallbackQueryHandler(handle_edit_series_pagination, pattern=f"^{const.CALLBACK_EDIT_SERIES_PAGE}"),
            CallbackQueryHandler(select_series_for_edit, pattern=f"^{const.CALLBACK_EDIT_SERIES_SELECT}"),
            CallbackQueryHandler(cancel, pattern=f"^{const.CALLBACK_ADMIN_CANCEL}$"),
        ],
        const.SELECT_EDIT_SEASON: [
            CallbackQueryHandler(select_season_for_edit, pattern=f"^{const.CALLBACK_EDIT_SEASON_SELECT}"),
            CallbackQueryHandler(start_edit_series, pattern=f"^{const.CALLBACK_ADMIN_EDIT_SERIES}$"),
        ],
        const.SELECT_EDIT_ACTION: [
            CallbackQueryHandler(start_add_episodes, pattern=f"^{const.CALLBACK_EDIT_ACTION_ADD}$"),
            CallbackQueryHandler(start_remove_episodes, pattern=f"^{const.CALLBACK_EDIT_ACTION_REMOVE}$"),
            CallbackQueryHandler(start_edit_series, pattern=f"^{const.CALLBACK_ADMIN_EDIT_SERIES}$"),
        ],
        const.ADD_SERIES_EPISODES: [
            MessageHandler(filters.VIDEO, handle_add_episode_upload),
            MessageHandler(filters.Regex("^✅ Done Uploading$"), done_adding_episodes),
        ],
        const.REMOVE_SERIES_EPISODES: [
            CallbackQueryHandler(handle_remove_episode, pattern=f"^{const.CALLBACK_REMOVE_EPISODE}"),
            CallbackQueryHandler(start_edit_series, pattern=f"^{const.CALLBACK_ADMIN_EDIT_SERIES}$"),
        ],
    },
    fallbacks=[CallbackQueryHandler(cancel, pattern=f"^{const.CALLBACK_ADMIN_CANCEL}$"), CommandHandler("cancel", cancel)],
    per_message=False
)