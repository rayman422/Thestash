from __future__ import annotations

from dataclasses import dataclass, field
import os
from typing import List


@dataclass
class SiteConfig:
	site_name: str = "The Stash"
	site_tagline: str = "A mellow stash of cannabis news and strains"
	base_url: str = os.getenv("BASE_URL", "")  # Optional: e.g., https://user.github.io/the-stash
	output_dir: str = "site"
	content_dir: str = "content/posts"
	templates_dir: str = "templates"
	public_dir: str = "public"
	index_page_size: int = 20


@dataclass
class AggregatorConfig:
	feed_urls: List[str] = field(
		default_factory=lambda: [
			# News and policy
			"https://www.marijuanamoment.net/feed/",
			"https://hightimes.com/feed/",
			"https://cannabisnow.com/feed/",
			# Culture/industry
			"https://www.leafly.com/news/feed",  # May change; aggregator handles failures
					# Community
		"https://www.reddit.com/r/trees/.rss?limit=10",
		]
	)
	items_per_source: int = 5
	max_total_items: int = 30
	request_timeout_seconds: int = 12


@dataclass
class GenerationConfig:
	# Provider can be: 'ollama', 'openai', 'none'
	provider: str = os.getenv("GEN_PROVIDER", "ollama")
	# Default model for provider
	model: str = os.getenv("GEN_MODEL", "llama3.2:3b")
	openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
	ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
	max_words: int = 900


@dataclass
class AppConfig:
	site: SiteConfig = field(default_factory=SiteConfig)
	aggregator: AggregatorConfig = field(default_factory=AggregatorConfig)
	generation: GenerationConfig = field(default_factory=GenerationConfig)


DEFAULT_CONFIG = AppConfig()
