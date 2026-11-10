"""Split a long narration take into cues at the pauses (ffmpeg silencedetect).

    python split_narration.py take.m4a cues/ --min-silence 0.6 --noise -35dB

Writes cue-01.m4a, cue-02.m4a ... plus cues.json with start/end times, so
each cue can be laid under its own scene.
"""
import argparse
import json
import re
import subprocess
from pathlib import Path

from fail_loudly import fail


def silences(path, noise, min_sil):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af",
                        f"silencedetect=noise={noise}:d={min_sil}", "-f", "null", "-"],
                       capture_output=True, text=True)
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r.stderr)]
    dur = re.search(r"Duration: (\d+):(\d+):([\d.]+)", r.stderr)
    if not dur:
        fail(f"Could not read {path}.")
    h, m, s = dur.groups()
    return list(zip(starts, ends)), int(h) * 3600 + int(m) * 60 + float(s)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("take")
    ap.add_argument("outdir")
    ap.add_argument("--noise", default="-35dB")
    ap.add_argument("--min-silence", type=float, default=0.6)
    ap.add_argument("--min-cue", type=float, default=1.0, help="drop cues shorter than this")
    a = ap.parse_args()

    gaps, total = silences(a.take, a.noise, a.min_silence)
    cuts = [0.0] + [(s + e) / 2 for s, e in gaps] + [total]  # cut mid-pause, never mid-word
    out = Path(a.outdir)
    out.mkdir(parents=True, exist_ok=True)
    cues = []
    for start, end in zip(cuts, cuts[1:]):
        if end - start < a.min_cue:
            continue
        name = f"cue-{len(cues) + 1:02d}.m4a"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{start:.3f}", "-to", f"{end:.3f}",
                        "-i", a.take, "-c:a", "aac", "-b:a", "192k", str(out / name)], check=True)
        cues.append({"file": name, "start": round(start, 3), "end": round(end, 3)})
    if not cues:
        fail("No cues found. Try a higher --noise (e.g. -30dB) or a shorter --min-silence.")
    (out / "cues.json").write_text(json.dumps(cues, indent=2))
    print(f"{len(cues)} cues written to {out}")


if __name__ == "__main__":
    main()
