from __future__ import annotations

import argparse
import json
import logging
from datetime import datetime
from pathlib import Path

from .aggregator import aggregate_news, categorize_items
from .builder import build_index, write_post, build_about
from .config import DEFAULT_CONFIG
from .generator import generate_post
from .store import load_seen_urls, save_seen_urls, append_history, save_post_assets
from .feeds import generate_rss, generate_sitemap, generate_robots


logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s %(name)s: %(message)s")
LOGGER = logging.getLogger(__name__)


def publish_once(no_ai: bool = False) -> None:
	config = DEFAULT_CONFIG
	LOGGER.info("Aggregating news and strains...")
	items = aggregate_news(
		feed_urls=config.aggregator.feed_urls,
		items_per_source=config.aggregator.items_per_source,
		max_total_items=config.aggregator.max_total_items,
		timeout_seconds=config.aggregator.request_timeout_seconds,
	)
	LOGGER.info("Fetched %d items", len(items))

	# Global dedupe against seen URL cache
	seen_urls = load_seen_urls()
	items = [it for it in items if it.url not in seen_urls]
	LOGGER.info("After seen-url filter: %d items", len(items))
	items = categorize_items(items)

	LOGGER.info("Generating post content...")
	markdown = generate_post(
		site_name=config.site.site_name,
		items=items,
		model=config.generation.model,
		max_words=config.generation.max_words,
		use_openai=False,
		provider=config.generation.provider,
		ollama_base_url=config.generation.ollama_base_url,
		openai_model=config.generation.openai_model,
	)

	created_at = datetime.now()
	title = f"The Stash Roundup — {created_at.strftime('%b %d, %Y %I:%M %p')}"
	LOGGER.info("Writing post page...")
	# Collect source meta for display and archival
	source_meta = [
		{"title": it.title, "url": it.url, "source": it.source, "category": it.category}
		for it in items[:12]
	]

	# Determine asset prefix for GH Pages deployments (base_url path)
	asset_prefix = ""
	if config.site.base_url:
		try:
			from urllib.parse import urlparse
			p = urlparse(config.site.base_url)
			asset_prefix = (p.path or "").rstrip("/")
		except Exception:
			asset_prefix = ""

	rel_path = write_post(
		output_dir=config.site.output_dir,
		public_dir=config.site.public_dir,
		templates_dir=config.site.templates_dir,
		site_name=config.site.site_name,
		site_tagline=config.site.site_tagline,
		title=title,
		markdown_content=markdown,
		created_at=created_at,
		sources=source_meta,
		asset_prefix=asset_prefix,
	)

	LOGGER.info("Updating index page...")
	index_json_path = Path(config.site.output_dir) / "posts.json"
	posts_meta = []
	if index_json_path.exists():
		try:
			posts_meta = json.loads(index_json_path.read_text(encoding="utf-8"))
		except Exception:
			posts_meta = []
	posts_meta.insert(0, {
		"title": title,
		"url": rel_path,
		"created_at": created_at.isoformat(),
	})
	posts_meta = posts_meta[: config.site.index_page_size]
	index_json_path.parent.mkdir(parents=True, exist_ok=True)
	index_json_path.write_text(json.dumps(posts_meta, indent=2), encoding="utf-8")

	build_index(
		output_dir=config.site.output_dir,
		templates_dir=config.site.templates_dir,
		site_name=config.site.site_name,
		site_tagline=config.site.site_tagline,
		posts=posts_meta,
		asset_prefix=asset_prefix,
	)
	build_about(
		output_dir=config.site.output_dir,
		templates_dir=config.site.templates_dir,
		site_name=config.site.site_name,
		site_tagline=config.site.site_tagline,
		asset_prefix=asset_prefix,
	)

	# Save assets and history
	slug = rel_path.split("/")[-1].replace(".html", "")
	used_ai_flag = (config.generation.provider in ("ollama", "openai") and not no_ai)
	save_post_assets(
		content_dir=config.site.content_dir,
		slug=slug,
		title=title,
		relative_url=rel_path,
		created_at_iso=created_at.isoformat(),
		markdown_content=markdown,
		sources=source_meta,
		used_ai=used_ai_flag,
		model_name=(config.generation.model if used_ai_flag else None),
	)
	append_history({"slug": slug, "title": title, "url": rel_path, "created_at": created_at.isoformat(), "num_sources": len(source_meta)})

	# Update seen URLs
	seen_urls.update([it.url for it in items])
	save_seen_urls(seen_urls)

	# Feeds
	generate_rss(config.site.site_name, config.site.base_url, posts_meta, config.site.output_dir)
	generate_sitemap(config.site.base_url, posts_meta, config.site.output_dir)
	generate_robots(config.site.base_url, config.site.output_dir)

	LOGGER.info("Publish complete: %s", rel_path)


def main() -> None:
	parser = argparse.ArgumentParser(description="The Stash CLI")
	sub = parser.add_subparsers(dest="cmd", required=True)

	publish = sub.add_parser("publish", help="Fetch, generate, and build one post")
	publish.add_argument("--provider", choices=["ollama","openai","none"], default=None, help="Generation provider")
	publish.add_argument("--model", default=None, help="Model name (provider-specific)")
	publish.add_argument("--no-ai", action="store_true", help="Disable AI and use fallback")

	args = parser.parse_args()
	if args.cmd == "publish":
		from .config import DEFAULT_CONFIG as C
		if args.provider:
			C.generation.provider = args.provider
		if args.model:
			C.generation.model = args.model
		publish_once(no_ai=(args.no_ai or C.generation.provider == "none"))


if __name__ == "__main__":
	main()

