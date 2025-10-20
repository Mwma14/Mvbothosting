# utils/decorators.py
import logging
from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
import config

logger = logging.getLogger(__name__)


def admin_only(func):
    @wraps(func)
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in config.ADMIN_IDS:
            logger.warning(f"Unauthorized access attempt for admin command by user {user_id}")
            return
        return await func(update, context, *args, **kwargs)
    return wrapped

def check_channel_membership(func):
    # ... (no changes needed here)
    pass