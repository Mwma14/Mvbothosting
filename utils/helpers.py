# utils/helpers.py
import logging
from telegram.ext import ContextTypes
from telegram.error import Forbidden, BadRequest
from keyboards.inline import get_file_again_keyboard
from typing import List, Optional

logger = logging.getLogger(__name__)

async def delete_and_prompt_callback(context: ContextTypes.DEFAULT_TYPE):
    """
    Job callback. Deletes video messages, the photo message, and sends a "Get Again" prompt.
    """
    job = context.job
    chat_id = job.chat_id
    video_message_ids = job.data.get('video_message_ids', [])
    photo_message_id = job.data.get('photo_message_id') # Get the photo ID
    content_type = job.data['content_type']
    content_id = job.data['content_id']
    content_name = job.data['content_name']

    # --- Combine all message IDs to delete ---
    all_message_ids = []
    if photo_message_id:
        all_message_ids.append(photo_message_id)
    all_message_ids.extend(video_message_ids)
    
    deleted_count = 0
    for message_id in all_message_ids:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
            deleted_count += 1
        except BadRequest as e:
            # It's common for a user to have already deleted the message.
            if "message to delete not found" in str(e).lower():
                pass
            else:
                logger.warning(f"Could not delete message {message_id} in chat {chat_id}: {e}")
        except Exception as e:
            logger.warning(f"Unexpected error deleting message {message_id} in chat {chat_id}: {e}")

    logger.info(f"Successfully deleted {deleted_count}/{len(all_message_ids)} messages for content '{content_name}'.")

    # --- Send the "Get File Again" prompt ---
    if deleted_count > 0 or len(all_message_ids) > 0: # Send prompt even if user deleted first
        try:
            prompt_text = (
                f"✅ **'{content_name}'** ၏ ဖိုင်များကို အောင်မြင်စွာဖျက်ပြီးပါပြီ။\n\n"
                "ဖိုင်ကို ပြန်လည်ရယူရန် အောက်ပါခလုတ်ကိုနှိပ်ပါ။\n\n"
                f"✅ The files for **'{content_name}'** have been deleted.\n\n"
                "Click the button below to get them again."
            )
            await context.bot.send_message(
                chat_id=chat_id,
                text=prompt_text,
                reply_markup=get_file_again_keyboard(content_type, content_id),
                parse_mode='Markdown'
            )
        except Forbidden:
             logger.warning(f"Bot blocked by user {chat_id}, cannot send 'Get Again' prompt.")
        except Exception as e:
            logger.error(f"Failed to send 'Get Again' prompt to {chat_id}: {e}")

def schedule_content_deletion(
    context: ContextTypes.DEFAULT_TYPE, 
    chat_id: int, 
    video_message_ids: List[int],
    photo_message_id: Optional[int],
    delay_minutes: int,
    content_type: str,
    content_id: str,
    content_name: str
):
    """
    Schedules a single job to delete a batch of messages (videos + photo) and then send a prompt.
    """
    if delay_minutes > 0 and (video_message_ids or photo_message_id):
        delay_seconds = delay_minutes * 60
        context.job_queue.run_once(
            delete_and_prompt_callback,
            when=delay_seconds,
            data={
                'video_message_ids': video_message_ids,
                'photo_message_id': photo_message_id, # Pass the photo ID to the job
                'content_type': content_type,
                'content_id': content_id,
                'content_name': content_name
            },
            chat_id=chat_id,
            name=f"delete_prompt_{chat_id}_{content_id}"
        )
        total_messages = len(video_message_ids) + (1 if photo_message_id else 0)
        logger.info(f"Scheduled deletion for {total_messages} messages for content '{content_name}' in {delay_minutes} minutes.")