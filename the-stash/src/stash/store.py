from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Iterable, List, Optional


def _ensure_dir(path: Path) -> None:
	path.mkdir(parents=True, exist_ok=True)


def _read_json(path: Path, default):
	if not path.exists():
		return default
	try:
		return json.loads(path.read_text(encoding="utf-8"))
	except Exception:
		return default


def _write_json(path: Path, data) -> None:
	_ensure_dir(path.parent)
	path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def load_seen_urls(state_dir: str = "content") -> set[str]:
	state_path = Path(state_dir) / "seen_urls.json"
	data = _read_json(state_path, [])
	return set(data)


def save_seen_urls(urls: Iterable[str], state_dir: str = "content") -> None:
	state_path = Path(state_dir) / "seen_urls.json"
	_write_json(state_path, list(dict.fromkeys(urls)))


def append_history(entry: dict, state_dir: str = "content") -> None:
	history_path = Path(state_dir) / "history.json"
	hist = _read_json(history_path, [])
	hist.insert(0, entry)
	_write_json(history_path, hist)


def save_post_assets(
	content_dir: str,
	slug: str,
	title: str,
	relative_url: str,
	created_at_iso: str,
	markdown_content: str,
	sources: List[dict],
	used_ai: bool,
	model_name: Optional[str],
) -> None:
	posts_dir = Path(content_dir)
	markdown_path = posts_dir / f"{slug}.md"
	meta_path = posts_dir / f"{slug}.json"
	_ensure_dir(posts_dir)
	markdown_path.write_text(markdown_content, encoding="utf-8")
	meta = {
		"slug": slug,
		"title": title,
		"url": relative_url,
		"created_at": created_at_iso,
		"sources": sources,
		"used_ai": used_ai,
		"model": model_name,
	}
	_write_json(meta_path, meta)

