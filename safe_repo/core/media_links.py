import os
import shutil
import uuid
from pathlib import Path
from typing import Optional, Dict

_STREAM_CACHE_DIR = None


def _get_cache_dir(cache_dir=None):
    global _STREAM_CACHE_DIR

    if cache_dir:
        _STREAM_CACHE_DIR = str(Path(cache_dir).expanduser())
        return _STREAM_CACHE_DIR

    if _STREAM_CACHE_DIR:
        return _STREAM_CACHE_DIR

    env_dir = os.environ.get("STREAM_CACHE_DIR")
    if env_dir:
        _STREAM_CACHE_DIR = str(Path(env_dir).expanduser())
        return _STREAM_CACHE_DIR

    base_dir = Path(__file__).resolve().parent / "stream_cache"
    base_dir.mkdir(parents=True, exist_ok=True)
    _STREAM_CACHE_DIR = str(base_dir)
    return _STREAM_CACHE_DIR


def _get_base_url(base_url=None):
    if base_url:
        return base_url.rstrip("/")

    env_url = (
        os.environ.get("PUBLIC_BASE_URL")
        or os.environ.get("APP_URL")
        or os.environ.get("RENDER_EXTERNAL_URL")
        or os.environ.get("BASE_URL")
        or "http://127.0.0.1:5000"
    )
    return env_url.rstrip("/")


def save_stream_file(source_path, base_url=None, cache_dir=None) -> Optional[Dict[str, str]]:
    """Copy a local media file into a public cache directory and return stream URLs."""
    if not source_path or not os.path.exists(source_path):
        return None

    cache_path = Path(_get_cache_dir(cache_dir))
    cache_path.mkdir(parents=True, exist_ok=True)

    token = uuid.uuid4().hex
    safe_name = os.path.basename(source_path).replace(" ", "_")
    target_path = cache_path / f"{token}_{safe_name}"
    shutil.copy2(source_path, target_path)

    base_url = _get_base_url(base_url)
    return {
        "token": token,
        "file_path": str(target_path),
        "stream_url": f"{base_url}/stream/{token}",
        "player_url": f"{base_url}/player/{token}",
    }


def get_stream_file(token):
    """Fetch a previously stored stream file by token."""
    if not token:
        return None

    cache_dir = Path(_get_cache_dir())
    cache_dir.mkdir(parents=True, exist_ok=True)

    for path in cache_dir.glob(f"{token}_*"):
        if path.is_file():
            return {"token": token, "file_path": str(path)}

    return None
