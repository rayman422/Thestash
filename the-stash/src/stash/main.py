from __future__ import annotations

import argparse
import os
from typing import Optional

from .config import load_config_from_env, AppConfig
from .aggregator import aggregate_feeds, offline_items
from .generator import generate_post
from .builder import write_post_and_build, build_index


def run_publish(cfg: AppConfig, provider: Optional[str], model: Optional[str], no_ai: bool, offline: bool) -> None:
	if provider:
		cfg.model.provider = provider
	if model:
		cfg.model.model_name = model
	if no_ai:
		cfg.model.provider = "none"

	items = offline_items() if offline or os.getenv("STASH_OFFLINE") else aggregate_feeds(
		cfg.site.feeds, max_items_per_feed=cfg.site.max_items_per_feed
	)

	post = generate_post(items, cfg)
	record = write_post_and_build(cfg, post)
	print(f"Published: {record.title} -> {record.html_path}")


def run_build(cfg: AppConfig) -> None:
	build_index(cfg)
	print(f"Built index at {cfg.site_dir / 'index.html'}")


def main(argv: list[str] | None = None) -> None:
	parser = argparse.ArgumentParser(prog="the-stash", description="The Stash — static blog with scheduled AI posts")
	sub = parser.add_subparsers(dest="command")

	pub = sub.add_parser("publish", help="Aggregate feeds, generate a post, and build the site")
	pub.add_argument("--provider", choices=["openai", "ollama", "none"], default=None, help="LLM provider")
	pub.add_argument("--model", default=None, help="Model name for the provider")
	pub.add_argument("--no-ai", action="store_true", help="Disable AI and use fallback text")
	pub.add_argument("--offline", action="store_true", help="Use offline sample items (no network)")

	bld = sub.add_parser("build", help="Rebuild index from existing content")

	args = parser.parse_args(argv)
	cfg = load_config_from_env()

	if args.command == "publish":
		run_publish(cfg, provider=args.provider, model=args.model, no_ai=args.no_ai, offline=args.offline)
	elif args.command == "build":
		run_build(cfg)
	else:
		parser.print_help()


if __name__ == "__main__":
	main()

