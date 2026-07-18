# safe_repo
# Extra module: post cloned media to a public channel and return a
# MX Player / VLC streamable link (t.me/Link09660/MSGID).
# This module does NOT modify any existing upload/download logic.

import logging
from safe_repo import app
from config import STREAM_CHANNEL, STREAM_CHANNEL_USERNAME

logger = logging.getLogger(__name__)


async def post_to_stream_channel(message):
    """Clone the given (already-sent) message to the public stream
    channel and return the streamable links.

    Returns a dict with 'link' (plain) and 'embed' (?embed=1 for VLC/MX Player),
    or None on failure.
    """
    try:
        if message is None:
            return None
        forwarded = await message.copy(STREAM_CHANNEL)
        if forwarded is None:
            return None
        msg_id = getattr(forwarded, "id", None)
        if msg_id is None:
            return None
        base = f"https://t.me/{STREAM_CHANNEL_USERNAME}/{msg_id}"
        return {
            "link": base,
            "embed": base + "?embed=1",
        }
    except Exception as e:
        logger.error(f"Stream channel post failed: {e}")
        return None


async def send_stream_link(sender, message, caption_prefix="🎬 **Stream Link:**"):
    """Post the uploaded message to the public stream channel and send the
    streamable link(s) back to the user as an extra message.
    """
    try:
        result = await post_to_stream_channel(message)
        if not result:
            # Post failed (likely bot is not admin in the public channel).
            await app.send_message(
                chat_id=sender,
                text="⚠️ **Stream link generate nahi ho paya.**\n"
                     f"Bot ko channel @{STREAM_CHANNEL_USERNAME} mein **admin** banaayein "
                     "(post permission ke sath) taaki stream link mile.",
            )
            return
        text = (
            f"{caption_prefix}\n"
            f"🔗 {result['link']}\n\n"
            "📺 **VLC / MX Player mein chalane ke liye:**\n"
            f"`{result['embed']}`\n\n"
            "Is link ko copy karke MX Player / VLC ke 'Network Stream' ya 'URL' box mein paste karein."
        )
        await app.send_message(chat_id=sender, text=text)
    except Exception as e:
        logger.error(f"send_stream_link failed: {e}")
