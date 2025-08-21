from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List

from jinja2 import Environment, FileSystemLoader, select_autoescape
import markdown2

LOGGER = logging.getLogger(__name__)


def _ensure_dir(path: str | Path) -> None:
	p = Path(path)
	p.mkdir(parents=True, exist_ok=True)


def build_env(templates_dir: str) -> Environment:
	return Environment(
		loader=FileSystemLoader(templates_dir),
		autoescape=select_autoescape(["html", "xml"]),
		trim_blocks=True,
		lstrip_blocks=True,
	)


def write_post(
	output_dir: str,
	public_dir: str,
	templates_dir: str,
	site_name: str,
	site_tagline: str,
	title: str,
	markdown_content: str,
	created_at: datetime,
	sources: list | None = None,
	asset_prefix: str = "",
) -> str:
	"""Render and write a single post page; returns relative URL."""
	env = build_env(templates_dir)
	post_tpl = env.get_template("post.html")
	index_tpl = env.get_template("index.html")
	base_tpl = env.get_template("base.html")

	_ensure_dir(output_dir)
	_ensure_dir(os.path.join(output_dir, "posts"))
	_ensure_dir(public_dir)

	# Copy public assets (simple copy of css only for now)
	css_src = Path(public_dir) / "css" / "styles.css"
	css_dst = Path(output_dir) / "css" / "styles.css"
	css_dst.parent.mkdir(parents=True, exist_ok=True)
	if css_src.exists():
		css_dst.write_text(css_src.read_text(encoding="utf-8"), encoding="utf-8")

	slug_date = created_at.strftime("%Y-%m-%d-%H%M")
	slug_title = "the-stash-roundup"
	file_name = f"{slug_date}-{slug_title}.html"
	output_path = Path(output_dir) / "posts" / file_name

	# Render markdown to HTML before template
	content_html = markdown2.markdown(markdown_content, extras=["fenced-code-blocks", "tables", "strike", "target-blank-links"])

	html = post_tpl.render(
		site_name=site_name,
		site_tagline=site_tagline,
		title=title,
		content_html=content_html,
		created_at=created_at,
		sources=(sources or []),
		asset_prefix=asset_prefix,
	)
	output_path.write_text(html, encoding="utf-8")

	return f"posts/{file_name}"


def build_index(
	output_dir: str,
	templates_dir: str,
	site_name: str,
	site_tagline: str,
	posts: List[dict],
	asset_prefix: str = "",
) -> None:
	env = build_env(templates_dir)
	index_tpl = env.get_template("index.html")

	index_html = index_tpl.render(
		site_name=site_name,
		site_tagline=site_tagline,
		posts=posts,
		asset_prefix=asset_prefix,
	)
	Path(output_dir).mkdir(parents=True, exist_ok=True)
	(Path(output_dir) / "index.html").write_text(index_html, encoding="utf-8")


def build_about(
	output_dir: str,
	templates_dir: str,
	site_name: str,
	site_tagline: str,
	asset_prefix: str = "",
) -> None:
	env = build_env(templates_dir)
	about_tpl = env.get_template("about.html")
	about_html = about_tpl.render(
		site_name=site_name,
		site_tagline=site_tagline,
		title=f"About — {site_name}",
		asset_prefix=asset_prefix,
	)
	Path(output_dir).mkdir(parents=True, exist_ok=True)
	(Path(output_dir) / "about.html").write_text(about_html, encoding="utf-8")

