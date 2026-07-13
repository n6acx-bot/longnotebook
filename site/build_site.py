"""Build the static site from the gallery manifest and changelog markdown.

Usage: python site/build_site.py
"""
from __future__ import annotations

import json
from pathlib import Path

import markdown as md
from jinja2 import Environment, FileSystemLoader

ROOT = Path(__file__).parent.parent
SITE = ROOT / "site"
PUBLIC = SITE / "public"
CHANGELOG = ROOT / "changelog"


def main() -> None:
    env = Environment(loader=FileSystemLoader(SITE / "templates"))

    manifest_path = PUBLIC / "gallery" / "manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {"date": "n/a", "entries": []}

    index_tpl = env.get_template("index.html")
    (PUBLIC / "index.html").write_text(index_tpl.render(manifest=manifest))

    entries = []
    for path in sorted(CHANGELOG.glob("*.md"), reverse=True):
        entries.append(md.markdown(path.read_text()))

    changelog_tpl = env.get_template("changelog.html")
    (PUBLIC / "changelog.html").write_text(changelog_tpl.render(entries=entries))

    print(f"Built {PUBLIC / 'index.html'} and {PUBLIC / 'changelog.html'}")


if __name__ == "__main__":
    main()
