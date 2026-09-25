import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
DB_PATH = DATA_DIR / "database.db"
SETTINGS_PATH = DATA_DIR / "settings.json"


def _now():
    return datetime.now(timezone.utc).isoformat()


class Database:
    def __init__(self, path=DB_PATH):
        DATA_DIR.mkdir(exist_ok=True)
        self.path = str(path)
        self._init()

    def _connect(self):
        con = sqlite3.connect(self.path)
        con.row_factory = sqlite3.Row
        return con

    def _init(self):
        with self._connect() as c:
            c.executescript("""
            CREATE TABLE IF NOT EXISTS history (video_id TEXT PRIMARY KEY, title TEXT, artist TEXT, album TEXT, thumbnail TEXT, played_at TEXT);
            CREATE TABLE IF NOT EXISTS liked (video_id TEXT PRIMARY KEY, title TEXT, artist TEXT, album TEXT, thumbnail TEXT, added_at TEXT);
            CREATE TABLE IF NOT EXISTS playlists (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE NOT NULL);
            CREATE TABLE IF NOT EXISTS playlist_songs (playlist_id INTEGER, video_id TEXT, title TEXT, artist TEXT, album TEXT, thumbnail TEXT, added_at TEXT, PRIMARY KEY(playlist_id, video_id));
            """)

    @staticmethod
    def song_dict(song):
        return {k: song.get(k, "") for k in ("video_id", "title", "artist", "album", "thumbnail")}

    def add_history(self, song):
        s = self.song_dict(song)
        with self._connect() as c:
            c.execute("INSERT OR REPLACE INTO history VALUES(?,?,?,?,?,?)", (*s.values(), _now()))

    def history(self):
        with self._connect() as c: return [dict(r) for r in c.execute("SELECT * FROM history ORDER BY played_at DESC LIMIT 100")]
    def clear_history(self):
        with self._connect() as c: c.execute("DELETE FROM history")
    def is_liked(self, vid):
        with self._connect() as c: return c.execute("SELECT 1 FROM liked WHERE video_id=?", (vid,)).fetchone() is not None
    def liked(self):
        with self._connect() as c: return [dict(r) for r in c.execute("SELECT * FROM liked ORDER BY added_at DESC")]
    def toggle_like(self, song):
        s = self.song_dict(song)
        with self._connect() as c:
            if c.execute("SELECT 1 FROM liked WHERE video_id=?", (s["video_id"],)).fetchone():
                c.execute("DELETE FROM liked WHERE video_id=?", (s["video_id"],)); return False
            c.execute("INSERT INTO liked VALUES(?,?,?,?,?,?)", (*s.values(), _now())); return True
    def playlists(self):
        with self._connect() as c: return [dict(r) for r in c.execute("SELECT * FROM playlists ORDER BY name")]
    def create_playlist(self, name):
        with self._connect() as c: c.execute("INSERT OR IGNORE INTO playlists(name) VALUES(?)", (name.strip(),))
    def rename_playlist(self, pid, name):
        with self._connect() as c: c.execute("UPDATE playlists SET name=? WHERE id=?", (name.strip(), pid))
    def delete_playlist(self, pid):
        with self._connect() as c: c.execute("DELETE FROM playlist_songs WHERE playlist_id=?; DELETE FROM playlists WHERE id=?", (pid, pid))
    def playlist_songs(self, pid):
        with self._connect() as c: return [dict(r) for r in c.execute("SELECT * FROM playlist_songs WHERE playlist_id=? ORDER BY added_at", (pid,))]
    def add_to_playlist(self, pid, song):
        s = self.song_dict(song)
        with self._connect() as c: c.execute("INSERT OR IGNORE INTO playlist_songs VALUES(?,?,?,?,?,?,?)", (pid, *s.values(), _now()))
    def remove_from_playlist(self, pid, vid):
        with self._connect() as c: c.execute("DELETE FROM playlist_songs WHERE playlist_id=? AND video_id=?", (pid, vid))


def load_settings():
    DATA_DIR.mkdir(exist_ok=True)
    try: return json.loads(SETTINGS_PATH.read_text(encoding="utf8"))
    except (OSError, ValueError): return {"download_location": str(Path.home() / "Downloads"), "volume": 0.7, "theme": "dark"}


def save_settings(settings):
    DATA_DIR.mkdir(exist_ok=True); SETTINGS_PATH.write_text(json.dumps(settings, indent=2), encoding="utf8")
