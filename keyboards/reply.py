# keyboards/reply.py

from telegram import ReplyKeyboardMarkup, KeyboardButton

def main_reply_keyboard() -> ReplyKeyboardMarkup:
    """Creates the main persistent reply keyboard."""
    keyboard = [
        ["🎬 All Movies", "📺 All Series"],
        ["🗓 Browse by Year", "📚 Browse by Category"], # NEW button added
        ["❓ Help & FAQ"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def done_uploading_reply_keyboard() -> ReplyKeyboardMarkup:
    """Creates a temporary reply keyboard with a 'Done' button for the admin."""
    keyboard = [
        [KeyboardButton("✅ Done Uploading")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)