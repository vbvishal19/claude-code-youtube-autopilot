"""Upload one video to YouTube, safely.

Resumable upload, custom thumbnail, playlist, scheduled publish time,
and a channel-identity check before ANY write.

    python upload_robot/upload.py --config video.json
    python upload_robot/upload.py --config video.json --dry-run

Created by Vishal S Bhandare. MIT licence.
"""
import argparse
import json
import os
import sys
from pathlib import Path

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from fail_loudly import fail  # noqa: E402
from upload_robot.auth import credentials  # noqa: E402

CHUNK = 8 * 1024 * 1024  # 8 MB chunks; each one survives a dropped connection


def verify_channel(yt, expected_id):
    """Lesson 2: ask the API who this token is before writing anything."""
    items = yt.channels().list(part="id,snippet", mine=True).execute().get("items", [])
    if not items:
        fail("This token has no YouTube channel. Re-run auth for the right account.")
    actual = items[0]["id"]
    if actual != expected_id:
        fail(
            f"Channel mismatch: token belongs to '{items[0]['snippet']['title']}' ({actual}), "
            f"config expects {expected_id}. Nothing was uploaded."
        )
    return items[0]["snippet"]["title"]


def body_for(cfg):
    status = {
        "privacyStatus": "private" if cfg.get("publish_at") else cfg.get("privacy", "private"),
        "selfDeclaredMadeForKids": bool(cfg.get("made_for_kids", False)),
        "containsSyntheticMedia": bool(cfg.get("altered_content", True)),
    }
    if cfg.get("publish_at"):
        status["publishAt"] = cfg["publish_at"]  # RFC 3339; YouTube flips it public then
    return {
        "snippet": {
            "title": cfg["title"][:100],
            "description": cfg.get("description", "")[:5000],
            "tags": cfg.get("tags", []),
            "categoryId": str(cfg.get("category_id", 28)),  # 28 = Science & Technology
            "defaultLanguage": cfg.get("language", "en"),
        },
        "status": status,
    }


def upload(yt, cfg):
    video = Path(cfg["video"])
    if not video.is_file():
        fail(f"Video file not found: {video}")
    req = yt.videos().insert(
        part="snippet,status",
        body=body_for(cfg),
        media_body=MediaFileUpload(str(video), chunksize=CHUNK, resumable=True),
    )
    response = None
    while response is None:
        status, response = req.next_chunk(num_retries=5)
        if status:
            print(f"  {int(status.progress() * 100)}%")
    return response["id"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True, help="JSON file describing the video")
    ap.add_argument("--dry-run", action="store_true", help="verify identity and inputs only")
    args = ap.parse_args()

    cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))
    expected = cfg.get("channel_id") or os.environ.get("YT_CHANNEL_ID")
    if not expected:
        fail("No target channel_id in the config or YT_CHANNEL_ID. Refusing to guess.")

    yt = build("youtube", "v3", credentials=credentials())
    title = verify_channel(yt, expected)
    print(f"Token verified for channel: {title}")
    if args.dry_run:
        print("Dry run: identity and config OK, nothing uploaded.")
        return

    try:
        vid = upload(yt, cfg)
        print(f"Uploaded: https://youtu.be/{vid}")
        if cfg.get("thumbnail"):
            yt.thumbnails().set(videoId=vid, media_body=MediaFileUpload(cfg["thumbnail"])).execute()
            print("Thumbnail set.")
        for pl in cfg.get("playlist_ids", []):
            yt.playlistItems().insert(
                part="snippet",
                body={"snippet": {"playlistId": pl, "resourceId": {"kind": "youtube#video", "videoId": vid}}},
            ).execute()
            print(f"Added to playlist {pl}.")
    except HttpError as e:
        fail(f"YouTube API error {e.resp.status}: {e._get_reason()}")


if __name__ == "__main__":
    main()
