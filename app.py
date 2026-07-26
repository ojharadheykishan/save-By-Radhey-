import os
import time
import threading
import requests
from flask import Flask, send_file, abort, request, render_template_string
from safe_repo.core.media_links import get_stream_file, read_stream_entries, get_stream_entry

app = Flask(__name__)

# Auto-ping settings
AUTO_PING_ENABLED = True
AUTO_PING_INTERVAL = 300  # 5 minutes in seconds
APP_URL = None


def auto_ping():
    """Background task to keep the app awake by pinging itself periodically"""
    while AUTO_PING_ENABLED and APP_URL:
        try:
            response = requests.get(APP_URL)
            print(f"Auto-ping successful: {response.status_code}")
        except Exception as e:
            print(f"Auto-ping failed: {str(e)}")
        time.sleep(AUTO_PING_INTERVAL)


@app.route('/')
def home():
    return """
    <center>
        <!-- Safe_repo -->
    </center>
    <style>
        body {
            background: antiquewhite;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            height: 100vh;
            margin: 0;
        }
        footer {
            text-align: center;
            padding: 10px;
            background: antiquewhite;
            font-size: 1.2em;
        }
    </style>
    <footer>
        Made with 💕 by t.me/Safe_repo
    </footer>
    """


@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    return "OK", 200


@app.route('/catalog')
def catalog_page():
    """Show a browseable catalog of generated stream links."""
    subject_filter = (request.args.get('subject') or '').strip()
    date_filter = (request.args.get('date') or '').strip()
    entries = read_stream_entries()

    filtered = []
    for entry in entries:
        if subject_filter and str(entry.get('subject', '')).lower() != subject_filter.lower():
            continue
        if date_filter and str(entry.get('date', '')) != date_filter:
            continue
        filtered.append(entry)
    filtered.sort(key=lambda item: item.get('timestamp', ''), reverse=True)

    subjects = sorted({str(entry.get('subject', 'General')) for entry in entries})
    dates = sorted({str(entry.get('date', '')) for entry in entries if entry.get('date')})

    return render_template_string("""
    <html>
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>LinkByRK Catalog</title>
        <style>
          body { font-family: Arial, sans-serif; margin: 0; background: #0f172a; color: #f8fafc; }
          .wrap { max-width: 1100px; margin: 0 auto; padding: 24px; }
          .filters { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 16px; }
          select, button { padding: 8px 10px; border-radius: 6px; border: 1px solid #334155; background: #111827; color: #f8fafc; }
          .card { background: #111827; border: 1px solid #334155; border-radius: 12px; padding: 16px; margin-bottom: 14px; }
          .topline { display: flex; justify-content: space-between; gap: 10px; flex-wrap: wrap; margin-bottom: 8px; }
          .pill { display: inline-block; background: #2563eb; color: white; padding: 4px 8px; border-radius: 999px; font-size: 0.8rem; }
          .actions a, .actions button { display: inline-block; margin-right: 8px; margin-top: 8px; color: #93c5fd; text-decoration: none; }
          .muted { color: #94a3b8; font-size: 0.95rem; }
          .desc { margin: 8px 0; color: #e2e8f0; }
        </style>
      </head>
      <body>
        <div class="wrap">
          <h1>LinkByRK Catalog</h1>
          <p class="muted">Browse links by subject, date, and description.</p>
          <form class="filters" method="get" action="/catalog">
            <select name="subject">
              <option value="">All subjects</option>
              {% for subject in subjects %}
              <option value="{{ subject }}" {% if subject_filter == subject %}selected{% endif %}>{{ subject }}</option>
              {% endfor %}
            </select>
            <select name="date">
              <option value="">All dates</option>
              {% for date in dates %}
              <option value="{{ date }}" {% if date_filter == date %}selected{% endif %}>{{ date }}</option>
              {% endfor %}
            </select>
            <button type="submit">Filter</button>
            <a href="/catalog" style="color:#93c5fd; padding: 8px 0;">Clear</a>
          </form>
          {% if filtered %}
            {% for entry in filtered %}
            <div class="card">
              <div class="topline">
                <div>
                  <strong>{{ entry.title or entry.subject or 'Untitled' }}</strong>
                  <div class="muted">{{ entry.date }} · {{ entry.timestamp }}</div>
                </div>
                <div><span class="pill">{{ entry.subject or 'General' }}</span></div>
              </div>
              {% if entry.description %}<div class="desc">{{ entry.description }}</div>{% endif %}
              <div class="actions">
                <a href="{{ entry.player_url }}" target="_blank">Open Player</a>
                <a href="{{ entry.stream_url }}" target="_blank">Open Direct Link</a>
                <button onclick="navigator.clipboard.writeText('{{ entry.stream_url }}')">Copy Stream Link</button>
                <button onclick="navigator.clipboard.writeText('{{ entry.player_url }}')">Copy Player Link</button>
              </div>
            </div>
            {% endfor %}
          {% else %}
            <div class="card">No links yet.</div>
          {% endif %}
        </div>
      </body>
    </html>
    """, subjects=subjects, dates=dates, filtered=filtered, subject_filter=subject_filter, date_filter=date_filter)


@app.route('/stream/<token>')
def stream_media(token):
    """Serve a cached media file as a direct HTTP stream."""
    entry = get_stream_file(token)
    if not entry:
        abort(404)

    path = entry["file_path"]
    if not os.path.exists(path):
        abort(404)

    as_attachment = request.args.get("download") == "1"
    return send_file(path, as_attachment=as_attachment)


@app.route('/player/<token>')
def player_page(token):
    """Return a simple HTML page that opens the stream in a player-friendly way."""
    entry = get_stream_file(token)
    if not entry:
        abort(404)

    stream_url = f"{request.url_root.rstrip('/')}/stream/{token}"
    entry_meta = get_stream_entry(token)
    title = entry_meta.get('title') if entry_meta else 'Media Player'
    description = entry_meta.get('description') if entry_meta else ''
    subject = entry_meta.get('subject') if entry_meta else 'General'
    return f"""
    <html>
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>{title}</title>
        <style>
          body {{ margin:0; background:#000; color:#fff; font-family:Arial,sans-serif; }}
          .wrap {{ min-height:100vh; display:flex; flex-direction:column; justify-content:center; align-items:center; padding:16px; box-sizing:border-box; }}
          .box {{ width:100%; max-width:900px; background:#111; border-radius:12px; overflow:hidden; box-shadow:0 10px 30px rgba(0,0,0,0.4); }}
          .top {{ padding:12px 16px; background:#1a1a1a; display:flex; justify-content:space-between; align-items:center; gap:12px; flex-wrap:wrap; }}
          .controls {{ display:flex; gap:8px; flex-wrap:wrap; align-items:center; }}
          select, button {{ border:none; border-radius:6px; padding:6px 10px; background:#222; color:#fff; }}
          video {{ width:100%; height:auto; background:#000; display:block; }}
          a {{ color:#4da3ff; text-decoration:none; }}
          .small {{ font-size:0.85rem; color:#aaa; }}
          .meta {{ padding: 12px 16px; background:#0f172a; color:#e2e8f0; }}
        </style>
      </head>
      <body>
        <div class="wrap">
          <div class="box">
            <div class="top">
              <div>
                <div>🎬 {title}</div>
                <div class="small">Subject: {subject}</div>
              </div>
              <div class="controls">
                <select id="speed">
                  <option value="1">1x</option>
                  <option value="1.25">1.25x</option>
                  <option value="1.5">1.5x</option>
                  <option value="2">2x</option>
                  <option value="4">4x</option>
                </select>
                <a href="{stream_url}" target="_blank">Open Direct Link</a>
                <a href="javascript:void(0);" onclick="window.open('{stream_url}', 'streamPopup', 'width=900,height=600');">Popup Player</a>
                <a href="{stream_url}?download=1" target="_blank">Download</a>
                <button onclick="navigator.clipboard.writeText('{stream_url}')">Copy Stream</button>
              </div>
            </div>
            <div class="meta">
              <div><strong>Description:</strong> {description}</div>
            </div>
            <video id="player" controls autoplay playsinline>
              <source src="{stream_url}" />
            </video>
          </div>
        </div>
        <script>
          const player = document.getElementById('player');
          const speedSelect = document.getElementById('speed');
          speedSelect.addEventListener('change', () => {{ player.playbackRate = parseFloat(speedSelect.value); }});
        </script>
      </body>
    </html>
    """, 200, {{"Content-Type": "text/html; charset=utf-8"}}


def start_bot_process():
    """Start the safe_repo bot.

    Guard against double-start: if another instance of the bot is already
    running (e.g. a separate Render worker using the same BOT_TOKEN), two
    Pyrogram clients would log in to the same bot and Telegram returns a
    409 Conflict, making the bot stop responding.

    NOTE: we use a lock file instead of `pgrep` because minimal Docker images
    (e.g. Render's python:3.10-slim) do not ship `pgrep`, which previously
    crashed this launcher with FileNotFoundError.
    """
    import subprocess
    import time
    import os
    import signal

    lock_file = "/tmp/safe_repo_bot.lock"

    # If a bot process is already running (lock file with a live PID), do not
    # spawn a second one.
    if os.path.exists(lock_file):
        try:
            with open(lock_file) as f:
                old_pid = int(f.read().strip())
            # Check if that PID is still alive (works without pgrep)
            os.kill(old_pid, 0)
            print(f"safe_repo bot already running (pid {old_pid}); "
                  "not starting a duplicate.")
            return
        except (ValueError, ProcessLookupError, PermissionError):
            # Stale lock file - remove it and continue
            try:
                os.remove(lock_file)
            except Exception:
                pass
        except Exception:
            try:
                os.remove(lock_file)
            except Exception:
                pass

    try:
        # Write our PID to the lock file
        with open(lock_file, "w") as f:
            f.write(str(os.getpid()))

        print("Starting safe_repo bot process...")
        bot_proc = subprocess.Popen(["python3", "-m", "safe_repo"])
        bot_proc.wait()
        print(f"safe_repo exited with code {bot_proc.returncode}")
    except Exception as e:
        print(f"safe_repo launcher error: {e}")
    finally:
        # Clean up lock file on exit
        try:
            if os.path.exists(lock_file):
                os.remove(lock_file)
        except Exception:
            pass


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    # Start bot process in background for all environments
    # This ensures both Flask app (health check) and bot are running
    bot_thread = threading.Thread(target=start_bot_process, daemon=True)
    bot_thread.start()

    # Determine the app URL for auto-ping
    # For Render, the URL will be provided in the RENDER_EXTERNAL_URL environment variable
    if 'RENDER_EXTERNAL_URL' in os.environ:
        APP_URL = os.environ['RENDER_EXTERNAL_URL']
        print(f"App URL: {APP_URL}")

        # Start auto-ping background task
        if AUTO_PING_ENABLED:
            ping_thread = threading.Thread(target=auto_ping, daemon=True)
            ping_thread.start()
            print(f"Auto-ping service started (interval: {AUTO_PING_INTERVAL} seconds)")

    # Always start Flask app to provide health check endpoint
    print(f"Starting Flask app on port {port}")
    app.run(host='0.0.0.0', port=port)
