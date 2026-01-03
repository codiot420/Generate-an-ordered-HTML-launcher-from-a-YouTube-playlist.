#!/usr/bin/env python3
# pre-req :  yt-dlp (`pip install yt-dlp`)

import subprocess
import sys
import re
from pathlib import Path

# html temp

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{page_title}</title>
<meta name="viewport" content="width=device-width, initial-scale=1">

<style>
body {{
  margin: 0;
  font-family: system-ui, sans-serif;
  background: #f4f4f4;
  color: #222;
}}
header {{
  padding: 1rem;
  background: #ffffff;
  border-bottom: 1px solid #ccc;
}}
main {{
  max-width: 1000px;
  margin: auto;
  padding: 1rem;
}}
.controls {{
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}}
button {{
  padding: 0.4rem 0.8rem;
  cursor: pointer;
}}
.playlist div {{
  padding: 0.4rem 0.6rem;
  cursor: pointer;
  border-radius: 4px;
}}
.playlist div:hover {{
  background: #eee;
}}
.playlist .active {{
  background: #dbeafe;
  font-weight: 600;
}}
footer {{
  text-align: center;
  font-size: 0.85rem;
  color: #666;
  padding: 1rem;
}}
</style>
</head>

<body>

<header>
  <h2>{page_title}</h2>
</header>

<main>

<div class="controls">
  <button onclick="prev()">◀ Previous</button>
  <button onclick="next()">Next ▶</button>
</div>

<div class="playlist" id="playlist"></div>

</main>

<footer>
  Videos open on YouTube (external playback).
</footer>

<script>
const lectures = [
{lectures}
];

let current = parseInt(localStorage.getItem("currentLecture")) || 0;
const playlistDiv = document.getElementById("playlist");

function openVideo(i) {{
  if (i < 0 || i >= lectures.length) return;
  current = i;
  localStorage.setItem("currentLecture", current);
  window.open(
    "https://www.youtube.com/watch?v=" + lectures[i].id,
    "_blank"
  );
  render();
}}

function next() {{ openVideo(current + 1); }}
function prev() {{ openVideo(current - 1); }}

function render() {{
  playlistDiv.innerHTML = "";
  lectures.forEach((l, i) => {{
    const div = document.createElement("div");
    div.textContent = `${{i + 1}}. ${{l.title}}`;
    if (i === current) div.classList.add("active");
    div.onclick = () => openVideo(i);
    playlistDiv.appendChild(div);
  }});
}}

render();
</script>

</body>
</html>
"""

def natural_key(s):
    """Natural sort: Lecture 2 < Lecture 10"""
    return [int(x) if x.isdigit() else x.lower()
            for x in re.findall(r"\d+|\D+", s)]

def sanitize_title(title):
    """Safe for JavaScript strings"""
    return title.replace('"', "'").strip()

def extract_entry(line):
    """Split on last |, last field is video ID"""
    title, vid = line.rsplit("|", 1)
    return sanitize_title(title), vid.strip()

def safe_filename_from_title(title):
    """Convert page title to filesystem-safe filename"""
    title = title.strip()
    title = re.sub(r"[^\w]+", "_", title)
    return title.strip("_") + ".html"

def main():
    url = input("Enter YouTube playlist URL: ").strip()
    page_title = input(
        "Page title (default: YouTube Playlist): "
    ).strip() or "YouTube Playlist"

    print("Fetching playlist…")

    cmd = [
        "yt-dlp",
        "--flat-playlist",
        "--print", "%(title)s|%(id)s",
        url
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr)
        sys.exit(1)

    entries = []
    for line in result.stdout.splitlines():
        if "|" not in line:
            continue
        if "[Private video]" in line:
            continue

        title, vid = extract_entry(line)
        if len(vid) != 11:
            continue

        entries.append((title, vid))

    if not entries:
        print("No valid videos found.")
        sys.exit(1)

    entries.sort(key=lambda x: natural_key(x[0]))

    lecture_js = ",\n".join(
        f'  {{ title: "{t}", id: "{vid}" }}'
        for t, vid in entries
    )

    html = HTML_TEMPLATE.format(
        page_title=page_title,
        lectures=lecture_js
    )
    output_file = safe_filename_from_title(page_title)
    Path(output_file).write_text(html, encoding="utf-8")

    print(f"{output_file} generated with {len(entries)} videos.")
    print("Open it by double-clicking or via: python3 -m http.server")

if __name__ == "__main__":
    main()

