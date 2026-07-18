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
    channel and return the streamable t.me link.

    Returns the link string, or None on failure.
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
        link = f"https://t.me/{STREAM_CHANNEL_USERNAME}/{msg_id}"
        return link
    except Exception as e:
        logger.error(f"Stream channel post failed: {e}")
        return None


async def send_stream_link(sender, message, caption_prefix="🎬 **Stream Link:**"):
    """Post the uploaded message to the public stream channel and send the
    streamable link back to the user as an extra message.
    """
    try:
        link = await post_to_stream_channel(message)
        if link:
            await app.send_message(
                chat_id=sender,
                text=f"{caption_prefix}\n{link}\n\nVLC / MX Player mein paste karke dekh sakte ho.",
            )
    except Exception as e:
        logger.error(f"send_stream_link failed: {e}")
