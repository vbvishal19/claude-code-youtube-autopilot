"""Lesson 1: look before you pay. Tile stills into one grid with ffmpeg.

    python contact_sheet.py stills/ sheet.jpg --cols 4

Every still is scaled to the same tile, labelled with its file name, and
padded so a partial last row still works. Review the sheet, fix bad stills
(free), and only then animate (paid).
"""
import argparse
import math
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from fail_loudly import fail

EXTS = {".jpg", ".jpeg", ".png", ".webp"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("out")
    ap.add_argument("--cols", type=int, default=4)
    ap.add_argument("--tile", default="480x270")
    a = ap.parse_args()

    if not shutil.which("ffmpeg"):
        fail("ffmpeg is not installed or not on PATH.")
    imgs = sorted(p for p in Path(a.folder).iterdir() if p.suffix.lower() in EXTS)
    if not imgs:
        fail(f"No images in {a.folder}.")
    w, h = map(int, a.tile.split("x"))
    rows = math.ceil(len(imgs) / a.cols)

    with tempfile.TemporaryDirectory() as tmp:
        for i, img in enumerate(imgs):
            label = img.stem.replace(":", "\\:").replace("'", "")
            vf = (f"scale={w}:{h}:force_original_aspect_ratio=decrease,"
                  f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color=black,"
                  f"drawtext=text='{label}':x=8:y=8:fontsize=20:fontcolor=white:box=1:boxcolor=black@0.6")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(img), "-vf", vf,
                            f"{tmp}/{i:04d}.png"], check=True)
        for i in range(len(imgs), rows * a.cols):  # blank tiles for the last row
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                            f"color=c=black:s={w}x{h}", "-frames:v", "1", f"{tmp}/{i:04d}.png"], check=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", "1", "-i", f"{tmp}/%04d.png",
                        "-vf", f"tile={a.cols}x{rows}", "-frames:v", "1", a.out], check=True)
    print(f"Contact sheet: {a.out} ({len(imgs)} stills, {a.cols}x{rows})")


if __name__ == "__main__":
    sys.exit(main())
