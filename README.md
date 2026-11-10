# claude-code-youtube-autopilot

Companion code for **Creative Wonder Tech, episode 1: "I Run 3 YouTube Channels With Claude Code — Here's the Whole System."**

Small, standalone pieces of the pipeline from the video, one per lesson. Each script
runs on its own; Claude Code (or you) calls them and reads their output.

| Lesson | File | What it does |
|---|---|---|
| 1. Look before you pay | `contact_sheet.py` | Tiles free stills into one labelled grid with ffmpeg, so you review before spending credits on animation |
| 2. Verify who you are | `upload_robot/upload.py` | YouTube Data API upload: resumable, thumbnail, playlists, scheduled publish, **channel-identity check before any write** |
| 3. Fail loudly | `fail_loudly.py` | Turns "ran fine, did nothing" into a non-zero exit with a clear message |
| 5. Volume vs judgment | `split_narration.py` | Splits long narration takes into per-scene cues by silence detection |
| 6. Guardrails | `GUARDRAILS.md` | The rules the agent runs under |

## Setup

Python 3.10+ and ffmpeg on your PATH.

```bash
pip install -r requirements.txt
cp .env.example .env          # then fill in your own paths and channel ID
```

For uploads, create an OAuth client (type *Desktop app*) in Google Cloud with the
YouTube Data API v3 enabled, save it as `secrets/youtube-client.json`, then:

```bash
python upload_robot/upload.py --config upload_robot/video.example.json --dry-run
```

The first run opens a browser to sign in. `--dry-run` checks the token's channel
against `channel_id` and stops there. Drop it to upload.

## Examples

```bash
python contact_sheet.py stills/ sheet.jpg --cols 4
python split_narration.py take.m4a cues/ --min-silence 0.6
python fail_loudly.py check-inputs queue.json
```

Secrets never go in this repo: `.gitignore` excludes `.env`, `secrets/` and any token or client JSON.

---

Created by **Vishal S Bhandare** · [LinkedIn](https://www.linkedin.com/in/vishal-bhandare-a3123657/) · MIT licence.
Views are my own.
