import os
import time
import threading
import requests
from flask import Flask

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
