from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import feedparser
import requests
from bs4 import BeautifulSoup
from dateutil import parser as date_parser


LOGGER = logging.getLogger(__name__)


USER_AGENT = (
	"TheStashBot/0.1 (+https://example.com; contact: admin@example.com) Python-requests"
)


@dataclass
class AggregatedItem:
	title: str
	url: str
	source: str
	published: Optional[datetime]
	summary: str
	category: Optional[str] = None


def fetch_rss_items(feed_url: str, limit: int, timeout_seconds: int) -> List[AggregatedItem]:
	"""Fetch items from a single RSS/Atom feed and normalize them."""
	LOGGER.info("Fetching feed: %s", feed_url)
	feed = feedparser.parse(feed_url)
	items: List[AggregatedItem] = []
	for entry in feed.entries[:limit]:
		title = getattr(entry, "title", "Untitled") or "Untitled"
		link = getattr(entry, "link", "") or ""
		if not link:
			continue
		source = feed.feed.get("title", feed_url)
		published_dt: Optional[datetime] = None
		if getattr(entry, "published", None):
			try:
				published_dt = date_parser.parse(entry.published)
			except Exception:
				published_dt = None
		summary = strip_html(getattr(entry, "summary", "") or "")
		items.append(
			AggregatedItem(
				title=title,
				url=link,
				source=source,
				published=published_dt,
				summary=summary,
			)
		)
	return items


def strip_html(html_text: str) -> str:
	if not html_text:
		return ""
	# Remove HTML tags
	cleaned = re.sub(re.compile(r"<[^>]+>"), "", html_text)
	# Decode common HTML entities
	import html
	cleaned = html.unescape(cleaned)
	# Clean up Reddit-specific formatting
	cleaned = re.sub(r'\s+submitted by\s+\s+/u/\w+\s+\[link\]\s+\[comments\]', '', cleaned)
	cleaned = re.sub(r'\s+\[link\]\s+\[comments\]', '', cleaned)
	return cleaned.strip()


def enrich_with_og_description(item: AggregatedItem, timeout_seconds: int) -> AggregatedItem:
	"""Fetch page and try to improve summary using Open Graph/Twitter description."""
	try:
		headers = {"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml"}
		resp = requests.get(item.url, headers=headers, timeout=timeout_seconds)
		if resp.status_code != 200 or "text/html" not in resp.headers.get("Content-Type", ""):
			return item
		soup = BeautifulSoup(resp.text, "html.parser")
		meta = (
			soup.find("meta", attrs={"property": "og:description"})
			or soup.find("meta", attrs={"name": "description"})
			or soup.find("meta", attrs={"name": "twitter:description"})
		)
		if meta and meta.get("content"):
			desc = meta["content"].strip()
			if desc and len(desc) > len(item.summary):
				item.summary = desc
	except Exception as exc:
		LOGGER.debug("OG description fetch failed for %s: %s", item.url, exc)
	return item


def aggregate_news(
	feed_urls: List[str],
	items_per_source: int,
	max_total_items: int,
	timeout_seconds: int,
	enrich: bool = True,
) -> List[AggregatedItem]:
	"""Aggregate items across feeds, dedupe, sort by recency, and optionally enrich."""
	all_items: List[AggregatedItem] = []
	for url in feed_urls:
		try:
			items = fetch_rss_items(url, items_per_source, timeout_seconds)
			all_items.extend(items)
		except Exception as exc:
			LOGGER.warning("Failed fetching feed %s: %s", url, exc)

	# Dedupe by URL
	seen: set[str] = set()
	deduped: List[AggregatedItem] = []
	for it in all_items:
		if it.url in seen:
			continue
		seen.add(it.url)
		deduped.append(it)

	# Sort by published desc (fallback to current time)
	def sort_key(it: AggregatedItem) -> float:
		if it.published is None:
			return 0.0
		return it.published.timestamp()

	deduped.sort(key=sort_key, reverse=True)

	# Trim
	trimmed = deduped[:max_total_items]

	# Enrich the top 10 to improve summaries
	if enrich:
		for idx, item in enumerate(trimmed[:10]):
			trimmed[idx] = enrich_with_og_description(item, timeout_seconds)

	return trimmed


def summarize_for_prompt(items: List[AggregatedItem], max_items: int = 12) -> str:
	"""Produce a compact, model-ready summary list."""
	parts: List[str] = []
	for it in items[:max_items]:
		date_str = it.published.isoformat() if it.published else "unknown"
		parts.append(f"- {it.title} (source: {it.source}, date: {date_str})\n  {it.summary[:280]}\n  Link: {it.url}")
	return "\n".join(parts)


def categorize_items(items: List[AggregatedItem]) -> List[AggregatedItem]:
	"""Tag items as 'strain' or 'news' using simple keyword heuristics."""
	strain_keywords = [
		"strain", "strains", "indica", "sativa", "hybrid", "cultivar", "terpene",
		"seed", "seeds", "flower", "buds", "kush", "haze", "skunk", "og ", "gelato",
		"sherb", "cookie", "cake", "rcb", "resin", "hash",
	]
	for it in items:
		text = f"{it.title} {it.summary}".lower()
		it.category = "strain" if any(k in text for k in strain_keywords) else "news"
	return items

