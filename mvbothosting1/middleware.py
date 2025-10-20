# middleware.py
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.error import TelegramError, BadRequest
from telegram.constants import ParseMode, ChatMemberStatus
from telegram.helpers import escape_markdown
import config

logger = logging.getLogger(__name__)

async def force_join_middleware(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    Middleware that checks channel membership. Returns True if allowed, False if blocked.
    """
    if not update.effective_user:
        return True

    user = update.effective_user

    if user.id in config.ADMIN_IDS:
        return True

    if not config.FORCE_JOIN_CHANNEL:
        return True

    try:
        member = await context.bot.get_chat_member(chat_id=config.FORCE_JOIN_CHANNEL, user_id=user.id)
        if member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER, ChatMemberStatus.RESTRICTED]:
            return True
            
    except BadRequest as e:
        if "user not found" in str(e).lower():
            pass
        else:
            logger.error(f"BOT PERMISSION ERROR in {config.FORCE_JOIN_CHANNEL}: {e}. Bot must be an admin.")
            # Ensure this reply is also MarkdownV2 safe if it contains any special chars
            await update.effective_message.reply_text(
                escape_markdown("Sorry, the bot is experiencing a technical issue. Please notify an admin.", version=2), 
                parse_mode=ParseMode.MARKDOWN_V2
            )
            return True
    except TelegramError as e:
        logger.error(f"TelegramError checking membership for user {user.id}: {e}. Allowing user to pass.")
        return True
    
    # --- If all checks fail, the user is not a member. Block them. ---
    logger.info(f"User {user.id} denied access: Not a member of {config.FORCE_JOIN_CHANNEL}.")
    
    join_url = f"https://t.me/{config.FORCE_JOIN_CHANNEL.lstrip('@')}"
    
    # Construct the raw string, then escape it entirely for MarkdownV2
    raw_text = (
        f"👋 **Access Denied | အသုံးပြုခွင့်မရှိပါ**\n\n"
        f"To use this bot, you must first join our official channel: {config.FORCE_JOIN_CHANNEL}\n"
        f"ဤဘော့တ်ကို အသုံးပြုရန်၊ ကျွန်ုပ်တို့၏တရားဝင်ချန်နယ်ဖြစ်သော {config.FORCE_JOIN_CHANNEL} သို့ ဦးစွာဝင်ရောက်ရပါမည်။"
    )
    # Use escape_markdown for the entire string
    escaped_text = escape_markdown(raw_text, version=2)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("➡️ Join Channel | Channel သို့ Join ပါ", url=join_url)],
        [InlineKeyboardButton("✅ I Have Joined | Join ပြီးပါပြီ", callback_data="check_join_status")]
    ])
    
    if update.callback_query:
        alert_text = (
            f"You have not joined the {config.FORCE_JOIN_CHANNEL} channel yet.\n"
            f"သင် {config.FORCE_JOIN_CHANNEL} သို့ Join ရသေးခြင်းမရှိပါ။\n\n"
            "Please join and then press the button again.\n"
            "ကျေးဇူးပြု၍ Join ပြီးနောက် ခလုတ်ကိုပြန်နှိပ်ပါ။"
        )
        await update.callback_query.answer(alert_text, show_alert=True)
    else:
        # Use the fully escaped text and set parse_mode
        await update.effective_message.reply_text(escaped_text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN_V2)
        
    return False

# ... (rest of middleware.py)