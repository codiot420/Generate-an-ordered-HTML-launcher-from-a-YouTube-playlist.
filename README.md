# Generate-an-ordered-HTML-launcher-from-a-YouTube-playlist.

## YouTube Playlist → Ordered HTML Launcher

This script generates a clean, ordered HTML page from a YouTube playlist.
Videos open externally on YouTube (no embedded playback).

### Why external-open?
Some environments block embedded YouTube playback (Error 153).
This approach works everywhere.

### Requirements
- Python 3.8+
- yt-dlp (`pip install yt-dlp`)

### Usage

```bash
chmod +x playlist_to_html.py
./playlist_to_html.py
