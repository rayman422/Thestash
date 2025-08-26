from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


DEFAULT_FEEDS: List[str] = [
	"https://www.leafly.com/news/feed",
	"https://www.marijuanamoment.net/feed/",
	"https://www.reddit.com/r/trees/.rss",
]


def get_project_root() -> Path:
	"""Return the project root directory (folder that contains templates/, public/)."""
	# This file lives at the-stash/src/stash/config.py
	# parent of parent of parent => the-stash
	return Path(__file__).resolve().parents[2]


@dataclass
class ModelConfig:
	provider: str = "none"  # one of: openai, ollama, none
	model_name: str = "gpt-4o-mini"
	openai_api_key: str | None = None


@dataclass
class SiteConfig:
	timezone: str = "UTC"
	max_items_per_feed: int = 5
	feeds: List[str] = field(default_factory=lambda: list(DEFAULT_FEEDS))
	base_url: str | None = None


@dataclass
class AppConfig:
	site: SiteConfig = field(default_factory=SiteConfig)
	model: ModelConfig = field(default_factory=ModelConfig)
	project_root: Path = field(default_factory=get_project_root)
	content_dir: Path = field(init=False)
	site_dir: Path = field(init=False)
	templates_dir: Path = field(init=False)
	public_dir: Path = field(init=False)

	def __post_init__(self) -> None:
		self.content_dir = self.project_root / "content" / "posts"
		self.site_dir = self.project_root / "site"
		self.templates_dir = self.project_root / "templates"
		self.public_dir = self.project_root / "public"


def load_config_from_env() -> AppConfig:
	"""
	Construct AppConfig from environment variables with sensible defaults.
	
	Environment variables:
	- OPENAI_API_KEY
	- STASH_PROVIDER (openai|ollama|none)
	- STASH_MODEL (model name)
	- STASH_TIMEZONE (IANA TZ name)
	- STASH_FEEDS (comma-separated list)
	- BASE_URL (used for absolute links)
	"""
	app = AppConfig()

	openai_api_key = os.getenv("OPENAI_API_KEY")
	provider = os.getenv("STASH_PROVIDER", app.model.provider).strip().lower()
	model_name = os.getenv("STASH_MODEL", app.model.model_name)
	timezone = os.getenv("STASH_TIMEZONE", app.site.timezone)
	feeds_env = os.getenv("STASH_FEEDS")
	base_url = os.getenv("BASE_URL")

	app.model.openai_api_key = openai_api_key
	app.model.provider = provider
	app.model.model_name = model_name
	app.site.timezone = timezone
	if feeds_env:
		feeds = [u.strip() for u in feeds_env.split(",") if u.strip()]
		if feeds:
			app.site.feeds = feeds
	app.site.base_url = base_url

	return app
