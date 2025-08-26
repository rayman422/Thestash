from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

import markdown2
from jinja2 import Environment, FileSystemLoader, select_autoescape

from .config import AppConfig
from .generator import GeneratedPost


@dataclass
class PostRecord:
	title: str
	slug: str
	created_at_iso: str
	excerpt: str
	markdown_path: str
	html_path: str


def _ensure_dirs(cfg: AppConfig) -> None:
	(cfg.content_dir).mkdir(parents=True, exist_ok=True)
	(cfg.site_dir / "posts").mkdir(parents=True, exist_ok=True)
	(cfg.public_dir / "css").mkdir(parents=True, exist_ok=True)


def _env(cfg: AppConfig) -> Environment:
	return Environment(
		loader=FileSystemLoader(str(cfg.templates_dir)),
		autoescape=select_autoescape(["html", "xml"]),
	)


def _copy_assets(cfg: AppConfig) -> None:
	# Copy public assets (css, images) into site directory
	dst_public = cfg.site_dir / "css"
	dst_public.mkdir(parents=True, exist_ok=True)
	css_src = cfg.public_dir / "css" / "styles.css"
	if css_src.exists():
		shutil.copy2(css_src, dst_public / "styles.css")


def write_post_and_build(cfg: AppConfig, post: GeneratedPost) -> PostRecord:
	_ensure_dirs(cfg)

	# Persist markdown content and a small JSON meta file
	stamp = post.created_at.strftime("%Y%m%d-%H%M%S")
	md_name = f"{stamp}-{post.slug}.md"
	json_name = f"{stamp}-{post.slug}.json"
	md_path = cfg.content_dir / md_name
	meta_path = cfg.content_dir / json_name

	md_path.write_text(post.markdown, encoding="utf-8")

	excerpt = post.markdown.splitlines()[0].lstrip("# ").strip() if post.markdown.strip() else post.title
	meta = {
		"title": post.title,
		"slug": post.slug,
		"created_at": post.created_at.isoformat(),
		"excerpt": excerpt,
		"markdown": str(md_path.relative_to(cfg.project_root)),
	}
	meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

	# Render HTML for post
	env = _env(cfg)
	post_template = env.get_template("post.html")
	html = markdown2.markdown(post.markdown)
	post_html = post_template.render(
		title=post.title,
		content=html,
		created_at=post.created_at,
		base_url=cfg.site.base_url,
		year=datetime.now().year,
	)
	post_out = cfg.site_dir / "posts" / f"{post.slug}.html"
	post_out.write_text(post_html, encoding="utf-8")

	# Rebuild index page
	build_index(cfg)
	_copy_assets(cfg)

	return PostRecord(
		title=post.title,
		slug=post.slug,
		created_at_iso=post.created_at.isoformat(),
		excerpt=excerpt,
		markdown_path=str(md_path),
		html_path=str(post_out),
	)


def _load_all_posts(cfg: AppConfig) -> List[Dict[str, Any]]:
	posts: List[Dict[str, Any]] = []
	if not cfg.content_dir.exists():
		return posts
	for meta_file in sorted(cfg.content_dir.glob("*.json")):
		try:
			data = json.loads(meta_file.read_text(encoding="utf-8"))
			posts.append(data)
		except Exception:
			continue
	# newest first
	posts.sort(key=lambda d: d.get("created_at", ""), reverse=True)
	return posts


def build_index(cfg: AppConfig) -> None:
	env = _env(cfg)
	index_template = env.get_template("index.html")
	posts = _load_all_posts(cfg)
	index_html = index_template.render(
		posts=posts,
		base_url=cfg.site.base_url,
		year=datetime.now().year,
	)
	(cfg.site_dir).mkdir(parents=True, exist_ok=True)
	(cfg.site_dir / "index.html").write_text(index_html, encoding="utf-8")

