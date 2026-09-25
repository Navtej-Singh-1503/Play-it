# PLAY-IT

A lightweight Python/PySide6 desktop music player. It searches YouTube Music, resolves a playable stream only when playback starts, and stores library data locally in SQLite.

## Windows

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

If PowerShell script execution is restricted, use Command Prompt:

```bat
py -3 -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -r requirements.txt
python main.py
```

yt-dlp's MP3 post-processing may require an ffmpeg executable only for the explicit Download action; normal streaming playback does not download files. Use only content you are permitted to save.

The UI and network work are separated: YouTube Music, yt-dlp, and downloads run in `QThreadPool` workers. SQLite is local and the application does not require Node, npm, a server, or a build step.
