#safe_repo


import math
import os
import random
import time
import re
import logging
from pyrogram import enums
from config import CHANNEL_ID, OWNER_ID 
from safe_repo.core import script
from safe_repo.core.mongo.plans_db import premium_users

# Configure logging
logger = logging.getLogger(__name__)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import cv2
from pyrogram.errors import FloodWait, InviteHashInvalid, InviteHashExpired, UserAlreadyParticipant, UserNotParticipant
from datetime import datetime as dt
import asyncio, subprocess, re, os, time



async def chk_user(message, user_id):
    user = await premium_users()
    # Check if user is in premium list or is owner (lifetime premium)
    if user_id in user:
        return 0
    else:
        await message.reply_text("Purchase premium to do the tasks...")
        return 1



async def gen_link(app,chat_id):
   link = await app.export_chat_invite_link(chat_id)
   return link

async def subscribe(app, message):
   update_channel = CHANNEL_ID
   url = await gen_link(app, update_channel)
   if update_channel:
      try:
         user = await app.get_chat_member(update_channel, message.from_user.id)
         if user.status == "kicked":
            await message.reply_text("You are Banned. Contact -- @safe_repo")
            return 1
      except UserNotParticipant:
         await message.reply_photo(photo="https://graph.org/file/d44f024a08ded19452152.jpg",caption=script.FORCE_MSG.format(message.from_user.mention), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Join Now...", url=f"{url}")]]))
         return 1
      except Exception:
         await message.reply_text("Something Went Wrong. Contact us @safe_repo...")
         return 1



async def get_seconds(time_string):
    def extract_value_and_unit(ts):
        value = ""
        unit = ""

        index = 0
        while index < len(ts) and ts[index].isdigit():
            value += ts[index]
            index += 1

        unit = ts[index:].lstrip()

        if value:
            value = int(value)

        return value, unit

    value, unit = extract_value_and_unit(time_string)

    if unit == 's':
        return value
    elif unit == 'min':
        return value * 60
    elif unit == 'hour':
        return value * 3600
    elif unit == 'day':
        return value * 86400
    elif unit == 'month':
        return value * 86400 * 30
    elif unit == 'year':
        return value * 86400 * 365
    else:
        return 0




PROGRESS_BAR = (
    "╭━━━〔 {status} 〕━━━╮\n"
    "{spinner} **{theme}** `{percent}%`\n"
    "┌─ 📁 **Name:** `{filename}`\n"
    "├─ 📄 **Type:** `{extension}`\n"
    "├─ {link_label} {link}\n"
    "├─ 📊 **Progress:**\n"
    "├─ {bar}\n"
    "├─ 📦 **Size:** `{current}` / `{total}`\n"
    "├─ ⚡ **Speed:** `{speed}/s`\n"
    "├─ ⏳ **ETA:** `{eta}`\n"
    "├─ 🎯 **Done:** `{percent}%`\n"
    "╰━━━━━━━━━━━━━━━━━╯\n\n"
    "💬 **{extra_title}**\n"
    "_“{extra_line1}”_\n"
    "_“{extra_line2}”_\n\n"
    "👤 **By Radhey Kishan Ojha**\n"
    "📞 [t.me/Radheyojha096](https://t.me/Radheyojha096)\n"
    "__Powered by safe_repo__"
)

# Colourful gradient themes: (name, [gradient_filled..., empty])
THEME_STYLES = [
    ("🔵 Neon Blue",   ["🟦", "🟦", "🟦", "⬜"]),
    ("🔴 Fire Red",    ["🟥", "🟧", "🟨", "⬜"]),
    ("🟢 Matrix Green",["🟩", "🟩", "⬜"]),
    ("🟡 Gold Premium",["🟨", "🟧", "⬜"]),
    ("🟣 Purple Cyber",["🟪", "🟪", "⬜"]),
    ("🌈 Rainbow",     ["🟥", "🟧", "🟨", "🟩", "🟦", "🟪", "⬜"]),
    ("💎 Crystal",     ["🩵", "🩵", "⬜"]),
    ("🩷 Pink Pop",    ["🩷", "🩷", "⬜"]),
]

# Animated spinner frames (rotates every update for a live feel)
SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

STATUS_STATES = [
    "📥 Downloading...",
    "📤 Uploading...",
    "🔄 Processing...",
    "🧩 Merging...",
    "🗜 Compressing...",
    "✅ Completed",
]

EXTRA_LINES = [
    # Shayari
    ("💖 Shayari", "Teri yaadon ka safar bhi kamaal hai,", "File download ho ya dil, dono slow hai."),
    ("💖 Shayari", "Aankhon mein sapne aur file mein speed,", "Dono ko ek saath chalaane ka hai need."),
    ("💖 Shayari", "Tera har message ek naya rang deta,", "Aur ye download ek naya dil jeet leta."),
    ("💖 Shayari", "Download ki raahon mein tere khayal,", "Har percent ek naya ehsaas deta hai."),
    ("💖 Shayari", "File ki tarah teri mohabbat bhi,", "Kabhi tez kabhi halki si beh rahi hai."),

    # Jokes
    ("😂 Joke", "Internet itna slow hai,", "Snail bhi aage nikal gaya."),
    ("😂 Joke", "Server ne bola \"kuch der aur\",", "Internet ne bola \"abhi aa raha hoon\"."),
    ("😂 Joke", "Ye download itna slow hai,", "Ki purana phone bhi jealous ho gaya."),
    ("😂 Joke", "Network ne mujhe block kar diya,", "Kaha \"zyada download kar raha hai tu\"."),
    ("😂 Joke", "Progress bar ne mujhse kaha,", "\"Boss, main to complete ho gaya, tu ruk kyun raha hai?\""),

    # Motivation
    ("🔥 Motivation", "Har percent progress success hai,", "Rukna mat, finish tak jao."),
    ("🔥 Motivation", "Har byte ek kadam hai,", "Finish line tumhara intezaar kar rahi hai."),
    ("🔥 Motivation", "Bas thoda aur sabr rakho,", "Jeet finish line ke baad milti hai."),
    ("🔥 Motivation", "Har challenge ek opportunity hai,", "Har download ek new beginning."),
    ("🔥 Motivation", "Speed kam hai par determination high,", "Ye journey success ki taraf le jaayegi."),

    # Funny
    ("😎 Funny", "File aa rahi hai boss,", "Bas network chai pe gaya hai."),
    ("😎 Funny", "Progress bar itna stylish hai,", "Aur upload itna slow hai."),
    ("😎 Funny", "Ye download ki speed dekh kar,", "Turtle ne bhi protest kar diya."),
    ("😎 Funny", "Server ne mujhe friend request bheji,", "Kaha \"download karne ka hai plan\"."),
    ("😎 Funny", "Progress bar ne selfie li,", "Kaha \"main to complete ho gaya, tu kab?\""),
    ("😎 Funny", "Ye upload ki speed dekh kar,", "Cheetah ne bhi training lene ka soch liya."),
    ("😎 Funny", "Network ne kaha \"ab bas kar\",", "Main ne kaha \"ek aur file bas\"."),
    ("😎 Funny", "Download complete hone ka wait,", "Jaise exam ka result ka intezar."),
    ("😎 Funny", "Ye progress bar itna cool hai,", "Ki AC ki zaroorat nahi padti."),
    ("😎 Funny", "File aa rahi hai slowly slowly,", "Jaise ki coffee shop mein line lagi ho."),
]


def choose_progress_style(percentage: float) -> str:
    """Build a smooth gradient progress bar with a bright 'head' segment."""
    style = random.choice(THEME_STYLES)[1]
    segments = 20
    filled = int(round((percentage / 100) * segments))
    # gradient fill colours (everything except the last = empty marker)
    fills = style[:-1]
    empty = style[-1]
    bar = ""
    for i in range(segments):
        if i < filled:
            bar += fills[min(i, len(fills) - 1)]
        else:
            bar += empty
    return bar


def choose_theme() -> str:
    return random.choice(THEME_STYLES)[0]


# Module-level spinner counter for animation between updates
_spinner_index = 0


def choose_spinner() -> str:
    global _spinner_index
    frame = SPINNER_FRAMES[_spinner_index % len(SPINNER_FRAMES)]
    _spinner_index += 1
    return frame


def choose_status(ud_type: str, percentage: float) -> str:
    normalized = ud_type.strip()
    if percentage >= 100:
        return "✅ Completed"
    if normalized:
        return normalized
    return random.choice(STATUS_STATES)


# Track used extra lines to avoid repeats
_used_extra_indices = set()

def choose_extra_text() -> tuple[str, str, str]:
    """Choose a random extra text (joke/shayari/motivation) without repeating."""
    global _used_extra_indices
    
    # If all have been used, reset the set
    if len(_used_extra_indices) >= len(EXTRA_LINES):
        _used_extra_indices.clear()
    
    # Get available indices that haven't been used
    available_indices = [i for i in range(len(EXTRA_LINES)) if i not in _used_extra_indices]
    
    # Pick a random one from available
    chosen_idx = random.choice(available_indices)
    _used_extra_indices.add(chosen_idx)
    
    label, line1, line2 = EXTRA_LINES[chosen_idx]
    return label, line1, line2


def clean_link(link: str) -> str:
    if not link:
        return "N/A"
    return link.strip()


async def progress_bar(current, total, *args):
    try:
        # Extract parameters from args
        # args[0] = ud_type, args[1] = message, args[2] = start, args[3] = file_path, args[4] = source_link
        ud_type = args[0] if len(args) > 0 else "Processing..."
        message = args[1] if len(args) > 1 else None
        start = args[2] if len(args) > 2 else time.time()
        file_path = args[3] if len(args) > 3 else None
        source_link = args[4] if len(args) > 4 else None

        if message is None:
            return

        now = time.time()
        diff = now - start if start else 1
        percentage = 0 if total == 0 else (current * 100) / total
        speed = 0 if diff == 0 else current / diff
        eta_seconds = 0 if speed == 0 else (total - current) / speed

        filename = os.path.basename(file_path) if file_path else "Unknown"
        extension = os.path.splitext(filename)[1][1:] if "." in filename else "unknown"
        status = choose_status(ud_type, percentage)
        theme = choose_theme()
        bar = choose_progress_style(percentage)
        spinner = choose_spinner()
        extra_title, extra_line1, extra_line2 = choose_extra_text()
        link = clean_link(source_link)

        # Determine if this is download or upload based on ud_type
        if "Downloading" in ud_type:
            link_label = "🔗 Source Link:"
        elif "Uploading" in ud_type:
            link_label = "🔗 Destination Link:"
        else:
            link_label = "🔗 Link:"

        # Pick a status emoji for the animated spinner
        if percentage >= 100:
            spinner = "✅"
        elif "Upload" in ud_type:
            spinner = "📤"
        elif "Download" in ud_type:
            spinner = "📥"

        text = PROGRESS_BAR.format(
            status=status,
            spinner=spinner,
            filename=filename,
            extension=extension,
            link_label=link_label,
            link=link,
            bar=bar,
            percent=round(percentage, 1),
            current=humanbytes(current),
            total=humanbytes(total),
            speed=humanbytes(speed),
            eta=convert(int(eta_seconds)),
            theme=theme,
            extra_title=extra_title,
            extra_line1=extra_line1,
            extra_line2=extra_line2,
        )

        if not hasattr(progress_bar, "last_update") or (now - progress_bar.last_update) > 1.0:
            await message.edit(text=text)
            progress_bar.last_update = now
    except Exception as e:
        logger.error(f"Progress bar error: {e}")
        pass


async def show_completion_ui(message, file_path, total_time, file_size):
    """Show completion UI after successful download/upload"""
    try:
        filename = os.path.basename(file_path) if file_path else "Unknown"
        completion_text = f"""
✅ **Download Complete**
📁 **Saved Successfully**

📄 **File:** `{filename}`
📦 **Size:** {humanbytes(file_size)}
⚡ **Total Time:** {convert(int(total_time))}
🎉 **Ready to Open**

By Radhey Kishan Ojha
📞 https://t.me/Radheyojha096

__**Powered by safe_repo**__
"""
        await message.edit(completion_text)
    except Exception as e:
        logger.error(f"Completion UI error: {e}")
        pass

# Initialize last_update attribute
progress_bar.last_update = 0.0

def humanbytes(size):
    if not size:
        return "0 B"
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'B'

def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "d, ") if days else "") + \
        ((str(hours) + "h, ") if hours else "") + \
        ((str(minutes) + "m, ") if minutes else "") + \
        ((str(seconds) + "s, ") if seconds else "") + \
        ((str(milliseconds) + "ms, ") if milliseconds else "")
    return tmp[:-2] 



def convert(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60      
    return "%d:%02d:%02d" % (hour, minutes, seconds)




async def userbot_join(userbot, invite_link):
    try:
        await userbot.join_chat(invite_link)
        return "Successfully joined the Channel"
    except UserAlreadyParticipant:
        return "User is already a participant."
    except (InviteHashInvalid, InviteHashExpired):
        return "Could not join. Maybe your link is expired or Invalid."
    except FloodWait:
        return "Too many requests, try again later."
    except Exception as e:
        print(e)
        return "Could not join, try joining manually."
    


def get_link(string):
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex,string)   
    try:
        link = [x[0] for x in url][0]
        if link:
            return link
        else:
            return False
    except Exception:
        return False


def parse_telegram_link(link: str):
    """Parse any Telegram link into (chat_id, message_id, thread_id, is_story).

    Supports:
      - https://t.me/username/123               (public chat message)
      - https://t.me/c/123456789/123            (private channel message)
      - https://t.me/c/-100123456789/123        (private channel message)
      - https://t.me/c/-100123456789/TOPIC/123  (supergroup topic/thread message)
      - https://t.me/username/TOPIC/123          (public supergroup topic message)
      - https://t.me/username/123?thread=TOPIC  (topic via query param)
      - https://t.me/username/123?comment=456   (comment under a post)
      - https://t.me/b/botname/123              (bot message via t.me/b/)
      - https://t.me/username/s/123             (story)
      - https://t.me/c/123456789/s/123          (private channel story)
    Returns (chat_id, message_id, thread_id, is_story). chat_id/message_id may be
    None when not determinable. thread_id is the topic id (for supergroups).
    """
    if not link:
        return None, None, None, False

    link = link.strip()
    # Strip fragment and trailing query for path parsing
    parsed = link.split("#")[0]
    query = ""
    if "?" in parsed:
        parsed, query = parsed.split("?", 1)

    # Normalise: remove scheme, trailing slash, www
    path = parsed
    for prefix in ("https://", "http://"):
        if path.startswith(prefix):
            path = path[len(prefix):]
    path = path.replace("www.", "")
    # Remove known hosts
    for host in ("t.me/", "telegram.me/", "telesco.pe/"):
        if path.startswith(host[:4]):  # crude: startswith t.me or telegram.me
            pass
    if path.startswith("t.me/"):
        path = path[4:]
    elif path.startswith("telegram.me/"):
        path = path[12:]
    elif path.startswith("telesco.pe/"):
        path = path[11:]

    parts = [p for p in path.split("/") if p]

    # Story link: .../s/ID
    if parts and parts[-2] == "s":
        # chat is everything before /s/
        chat_parts = parts[:-2]
        chat = "/".join(chat_parts) if chat_parts else None
        try:
            story_id = int(parts[-1])
        except ValueError:
            return None, None, None, False
        return chat, story_id, None, True

    # t.me/b/botname/ID
    if parts and parts[0] == "b" and len(parts) >= 3:
        chat = parts[1]
        try:
            msg_id = int(parts[2])
        except ValueError:
            return None, None, None, False
        return chat, msg_id, None, False

    # t.me/c/CHANNEL/...  (private)
    if parts and parts[0] == "c" and len(parts) >= 3:
        raw = parts[1]
        # Convert -100xxxx or xxxx to full -100 form
        if raw.startswith("-100"):
            chat = int(raw)
        elif raw.lstrip("-").isdigit():
            chat = int("-100" + raw.lstrip("-"))
        else:
            chat = raw
        # Remaining parts after channel id: possibly TOPIC then MSG
        rest = parts[2:]
        return _resolve_thread_and_msg(chat, rest, query)

    # Public chat: t.me/username/ID  or  t.me/username/TOPIC/ID
    if len(parts) >= 2:
        chat = parts[0]
        rest = parts[1:]
        return _resolve_thread_and_msg(chat, rest, query)

    return None, None, None, False


def _resolve_thread_and_msg(chat, rest, query):
    """Resolve (chat, message_id, thread_id) from the path parts after the chat."""
    thread_id = None

    # Query param style: ?thread=TOPIC or ?comment=MSG
    if query:
        for kv in query.split("&"):
            if "=" not in kv:
                continue
            k, v = kv.split("=", 1)
            if k == "thread" and v.isdigit():
                thread_id = int(v)
            if k == "comment" and v.isdigit() and len(rest) == 1:
                return chat, int(v), thread_id, False

    if len(rest) == 1:
        try:
            return chat, int(rest[0]), thread_id, False
        except ValueError:
            return chat, None, thread_id, False

    if len(rest) >= 2:
        # rest = [TOPIC, MSG] for supergroup threads
        try:
            topic = int(rest[0])
            msg = int(rest[1])
            return chat, msg, topic, False
        except ValueError:
            try:
                return chat, int(rest[-1]), thread_id, False
            except ValueError:
                return chat, None, thread_id, False

    return chat, None, thread_id, False


def video_metadata(file):
    default_values = {'width': 1, 'height': 1, 'duration': 1}
    try:
        vcap = cv2.VideoCapture(file)
        if not vcap.isOpened():
            return default_values  # Return defaults if video cannot be opened

        width = round(vcap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = round(vcap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = vcap.get(cv2.CAP_PROP_FPS)
        frame_count = vcap.get(cv2.CAP_PROP_FRAME_COUNT)

        if fps <= 0:
            return default_values  # Return defaults if FPS value is zero or negative

        duration = round(frame_count / fps)
        if duration <= 0:
            return default_values  # Return defaults if duration is zero or negative

        vcap.release()
        return {'width': width, 'height': height, 'duration': duration}

    except Exception as e:
        print(f"Error in video_metadata: {e}")
        return default_values
    
def hhmmss(seconds):
    return time.strftime('%H:%M:%S',time.gmtime(seconds))

async def screenshot(video, duration, sender):
    if os.path.exists(f'{sender}.jpg'):
        return f'{sender}.jpg'
    
    # Check if ffmpeg is available
    try:
        ffmpeg_check = await asyncio.create_subprocess_exec(
            "ffmpeg", "-version",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await ffmpeg_check.communicate()
        ffmpeg_available = True
    except FileNotFoundError:
        ffmpeg_available = False
    
    if not ffmpeg_available:
        # If ffmpeg is not available, use a default thumbnail or skip screenshot
        # For now, we'll just return None and handle it in the caller
        logger.warning("ffmpeg not available, skipping screenshot generation")
        return None
    
    # Proceed with ffmpeg if available
    time_stamp = hhmmss(int(duration)/2)
    out = dt.now().isoformat("_", "seconds") + ".jpg"
    cmd = ["ffmpeg",
           "-ss",
           f"{time_stamp}", 
           "-i",
           f"{video}",
           "-frames:v",
           "1", 
           f"{out}",
           "-y"
          ]
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    x = stderr.decode().strip()
    y = stdout.decode().strip()
    if os.path.isfile(out):
        return out
    else:
        None  
