# bot.py (main.py)

import logging
from telegram import Update
from telegram.ext import (
    Application, MessageHandler, filters,
    CallbackQueryHandler, PicklePersistence, ContextTypes, CommandHandler,
    TypeHandler, ApplicationHandlerStop, JobQueue
)
from telegram.error import TelegramError
import config

from keyboards.reply import main_reply_keyboard
from handlers.user.start import start, start_handler, help_handler, help_command
from handlers.user.search import movie_search_handler, series_search_handler, generic_search_handler
from handlers.user.browsing import browsing_handlers, show_all_movies, show_all_series, show_browse_by_year, show_browse_by_category # Ensure browsing_handlers is explicitly imported
from handlers.admin.admin_panel import admin_conversation_handler
from middleware import force_join_middleware

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# This function should be in main.py as it needs access to other handlers
async def check_join_status_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("Checking your membership status...", show_alert=False)
    
    # After the middleware confirms membership, this will run.
    await query.message.delete()
    # Call the start handler to show the welcome message
    await start(update, context)

# --- MOVE global_middleware FUNCTION DEFINITION HERE ---
# It must be defined before main() uses it.
async def global_middleware(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_allowed = await force_join_middleware(update, context)
    if not is_allowed:
        raise ApplicationHandlerStop

async def diagnose(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in config.ADMIN_IDS: return
    if not config.FORCE_JOIN_CHANNEL: await update.message.reply_text("Diag: FORCE_JOIN_CHANNEL not set."); return
    await update.message.reply_text(f"Running diagnostic for channel: {config.FORCE_JOIN_CHANNEL}\nChecking user ID: {user_id}")
    try:
        member = await context.bot.get_chat_member(chat_id=config.FORCE_JOIN_CHANNEL, user_id=user_id)
        await update.message.reply_text(f"✅ SUCCESS!\nAPI status: '{member.status}'\nThis means bot permissions are correct.")
    except Exception as e:
        await update.message.reply_text(f"❌ FAILED!\nAPI error: `{e}`\n\nCheck if bot is admin or if channel username is correct.", parse_mode='Markdown')

def main():
    logger.info("Starting bot...")
    persistence = PicklePersistence(filepath="bot_persistence.pickle")
    
    # --- Initialize JobQueue ---
    job_queue = JobQueue()
    
    application = Application.builder().token(config.BOT_TOKEN).persistence(persistence).job_queue(job_queue).build()
    
    # --- MIDDLEWARE SETUP ---
    application.add_handler(TypeHandler(Update, global_middleware), group=-1)

    # --- Other Handlers ---
    application.add_handler(CommandHandler("diag", diagnose))
    application.add_handler(admin_conversation_handler)
    application.add_handler(start_handler)
    application.add_handler(help_handler)
    application.add_handler(movie_search_handler)
    application.add_handler(series_search_handler)
    
    # Correctly add a list of browsing handlers
    application.add_handlers(browsing_handlers) # This is the correct way to add a list of handlers

    application.add_handler(CallbackQueryHandler(check_join_status_callback, pattern="^check_join_status$"))
    
    # Handlers for Reply Keyboard
    application.add_handler(MessageHandler(filters.Regex("^🎬 All Movies$"), show_all_movies))
    application.add_handler(MessageHandler(filters.Regex("^📺 All Series$"), show_all_series))
    application.add_handler(MessageHandler(filters.Regex("^🗓 Browse by Year$"), show_browse_by_year))
    application.add_handler(MessageHandler(filters.Regex("^📚 Browse by Category$"), show_browse_by_category))
    application.add_handler(MessageHandler(filters.Regex("^❓ Help & FAQ$"), help_command))
    
    application.add_handler(generic_search_handler)
    
    logger.info("Bot is running. Press Ctrl-C to stop.")
    application.run_polling()
    
if __name__ == "__main__":
    main()