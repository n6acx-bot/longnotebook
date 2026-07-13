"""Proof-of-concept run: sweep elementary CA rules, render the top few as
stills, render one Game of Life soup as an animation, write a manifest for
the site generator and a first changelog entry.

Usage: run as the `longnotebook` user, from the project root, with the venv
active:
    python sweep/run_sweep.py
"""
from __future__ import annotations

import datetime
import json
import sys
from pathlib import Path

import imageio.v3 as iio
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
import elementary_ca
import game_of_life

ROOT = Path(__file__).parent.parent
GALLERY = ROOT / "site" / "public" / "gallery"
CHANGELOG = ROOT / "changelog"


def render_elementary(grid: np.ndarray, path: Path) -> None:
    img = Image.fromarray((1 - grid) * 255).convert("L")
    img = img.resize((img.width * 3, img.height * 3), Image.NEAREST)
    img.save(path)


def render_life_gif(frames: list[np.ndarray], path: Path) -> None:
    imgs = [((1 - f) * 255).astype(np.uint8) for f in frames]
    iio.imwrite(path, imgs, duration=60, loop=0)


def main() -> None:
    GALLERY.mkdir(parents=True, exist_ok=True)
    CHANGELOG.mkdir(parents=True, exist_ok=True)

    today = datetime.date.today().isoformat()
    manifest = {"date": today, "entries": []}

    print("Sweeping 256 elementary CA rules...")
    top = elementary_ca.sweep(top_n=6)
    for entry in top:
        rule = entry["rule"]
        fname = f"rule{rule}.png"
        render_elementary(entry["grid"], GALLERY / fname)
        manifest["entries"].append(
            {
                "kind": "elementary",
                "title": f"Rule {rule}",
                "score": round(entry["score"], 4),
                "image": f"gallery/{fname}",
            }
        )
        print(f"  rule {rule}: score {entry['score']:.4f} -> {fname}")

    print("Rendering one Game of Life soup...")
    frames = game_of_life.simulate(seed=0, size=80, frames=150)
    render_life_gif(frames, GALLERY / "life_soup_0.gif")
    manifest["entries"].append(
        {
            "kind": "life",
            "title": "Random soup, seed 0",
            "image": "gallery/life_soup_0.gif",
        }
    )

    with open(GALLERY / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)

    changelog_path = CHANGELOG / f"{today}-setup.md"
    if not changelog_path.exists():
        best = top[0]
        changelog_path.write_text(
            f"""# {today} — First run

Environment stood up today on `penguin.home.n6acx.net`, running as a
dedicated unprivileged account (`longnotebook`) rather than root, with no
access to fleet credentials.

First sweep: all 256 elementary CA rules scored by a rough
variation/non-periodicity heuristic. Top result was **rule
{best['rule']}** (score {best['score']:.4f}) — see the gallery. Also
rendered one Game of Life random-soup run as a first animated piece.

This is a proof that the pipeline works end to end (sweep -> score ->
render -> publish), not a real research finding yet — the scoring
heuristic is intentionally simple and will need real iteration before
anything here counts as "interesting" in a way worth writing up.
"""
        )

    print(f"Done. Manifest: {GALLERY / 'manifest.json'}")
    print(f"Changelog: {changelog_path}")


if __name__ == "__main__":
    main()
