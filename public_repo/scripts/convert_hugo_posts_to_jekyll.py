#!/usr/bin/env python3
"""
Convert Hugo posts (TOML front matter) to Jekyll posts (YAML front matter).

Assumptions:
- Hugo posts live under content/posts/*.md
- Front matter is TOML delimited by +++ markers
- We keep Hugo's <!--more--> markers and configure excerpt_separator accordingly
"""

from __future__ import annotations

import datetime as _dt
import os
from pathlib import Path
import re
import sys
import tomllib


RE_TOML_FM = re.compile(r"^\+\+\+\s*\n(.*?)\n\+\+\+\s*\n(.*)\Z", re.S)


def _yaml_quote(s: str) -> str:
    # Minimal YAML-safe quoting for titles.
    s = s.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{s}"'


def _format_jekyll_date(dt: _dt.datetime) -> str:
    if dt.tzinfo is None:
        # Default to local (+08:00) if missing.
        dt = dt.replace(tzinfo=_dt.timezone(_dt.timedelta(hours=8)))
    # Jekyll accepts ISO-like; keep offset.
    return dt.strftime("%Y-%m-%d %H:%M:%S %z")


def _parse_hugo_post(p: Path) -> tuple[dict, str]:
    raw = p.read_text(encoding="utf-8")
    m = RE_TOML_FM.match(raw)
    if not m:
        raise ValueError(f"Not a Hugo TOML front matter file: {p}")
    fm_toml, body = m.group(1), m.group(2)
    fm = tomllib.loads(fm_toml)
    return fm, body


def _to_slug_and_date(src_path: Path, fm: dict) -> tuple[str, _dt.date]:
    # Prefer front-matter date for correctness.
    dt = fm.get("date")
    if isinstance(dt, _dt.datetime):
        d = dt.date()
    elif isinstance(dt, str):
        d = _dt.datetime.fromisoformat(dt).date()
    else:
        # Fallback: infer from filename prefix.
        name = src_path.stem
        m = re.match(r"^(\d{4})-(\d{2})-(\d{2})-(.+)$", name)
        if m:
            d = _dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            return m.group(4), d
        m = re.match(r"^(\d{4})(\d{2})(\d{2})-(.+)$", name)
        if m:
            d = _dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            return m.group(4), d
        raise ValueError(f"Cannot infer date from {src_path.name} and no front-matter date")

    # Infer slug from filename.
    name = src_path.stem
    m = re.match(r"^\d{4}-\d{2}-\d{2}-(.+)$", name)
    if m:
        slug = m.group(1)
    else:
        m = re.match(r"^\d{8}-(.+)$", name)
        if m:
            slug = m.group(1)
        else:
            slug = name
    return slug, d


def _write_jekyll_post(dst: Path, fm: dict, body: str) -> None:
    title = fm.get("title", "").strip()
    dt = fm.get("date")
    if isinstance(dt, _dt.datetime):
        date_str = _format_jekyll_date(dt)
    elif isinstance(dt, str):
        date_str = _format_jekyll_date(_dt.datetime.fromisoformat(dt))
    else:
        date_str = None

    tags = fm.get("tags") or []
    categories = fm.get("categories") or []

    lines: list[str] = ["---"]
    if title:
        lines.append(f"title: {_yaml_quote(title)}")
    if date_str:
        lines.append(f"date: {date_str}")
    if categories:
        lines.append("categories:")
        for c in categories:
            lines.append(f"  - {_yaml_quote(str(c))}")
    if tags:
        lines.append("tags:")
        for t in tags:
            lines.append(f"  - {_yaml_quote(str(t))}")
    # Keep as a normal post; defaults in _config.yml apply.
    lines.append("---")
    lines.append("")
    # Hugo posts may contain templating snippets like {{ ... }} or {% ... %}.
    # Wrap the whole body in Liquid raw/endraw so Jekyll (Liquid) won't try to parse them.
    lines.append("{% raw %}")
    lines.append(body.rstrip())
    lines.append("{% endraw %}")
    lines.append("")
    dst.write_text("\n".join(lines), encoding="utf-8")


def _clear_md(dir_path: Path) -> None:
    if not dir_path.exists():
        return
    for p in dir_path.glob("*.md"):
        p.unlink()


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    hugo_posts = repo_root / "content" / "posts"
    jekyll_posts = repo_root / "_posts"

    if not hugo_posts.exists():
        print(f"Missing Hugo posts directory: {hugo_posts}", file=sys.stderr)
        return 2

    # Remove template sample content so the preview is clean.
    _clear_md(repo_root / "_posts")
    _clear_md(repo_root / "_publications")
    _clear_md(repo_root / "_talks")
    _clear_md(repo_root / "_teaching")
    _clear_md(repo_root / "_portfolio")

    jekyll_posts.mkdir(parents=True, exist_ok=True)

    converted = 0
    for src in sorted(hugo_posts.glob("*.md")):
        if src.name == "_index.md":
            continue
        fm, body = _parse_hugo_post(src)
        if fm.get("draft") is True:
            continue
        slug, d = _to_slug_and_date(src, fm)
        dst_name = f"{d:%Y-%m-%d}-{slug}.md"
        dst = jekyll_posts / dst_name
        _write_jekyll_post(dst, fm, body)
        converted += 1

    print(f"Converted {converted} posts -> {jekyll_posts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
