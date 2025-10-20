# keyboards/reply.py

from telegram import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import config

def main_reply_keyboard(user_id: int = None) -> ReplyKeyboardMarkup:
    """Creates the main persistent reply keyboard. Only shows for admins."""
    # If user is not an admin, return an empty keyboard (hide buttons)
    if user_id is None or user_id not in config.ADMIN_IDS:
        return ReplyKeyboardRemove()
    
    # Admin keyboard with all options
    keyboard = [
        ["🎬 All Movies", "📺 All Series"],
        ["🗓 Browse by Year", "📚 Browse by Category"],
        ["❓ Help & FAQ"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def done_uploading_reply_keyboard() -> ReplyKeyboardMarkup:
    """Creates a temporary reply keyboard with a 'Done' button for the admin."""
    keyboard = [
        [KeyboardButton("✅ Done Uploading")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)