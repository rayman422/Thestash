from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable, List, Dict, Any

import feedparser
from dateutil import parser as date_parser


@dataclass
class AggregatedItem:
	title: str
	url: str
	summary: str
	published_at: datetime
	source: str


def _parse_datetime(value: Any) -> datetime:
	if isinstance(value, datetime):
		return value.astimezone(timezone.utc)
	try:
		dt = date_parser.parse(str(value))
		if not dt.tzinfo:
			dt = dt.replace(tzinfo=timezone.utc)
		return dt.astimezone(timezone.utc)
	except Exception:
		return datetime.now(tz=timezone.utc)


def fetch_feed(url: str, max_items: int = 5) -> List[AggregatedItem]:
	parsed = feedparser.parse(url)
	items: List[AggregatedItem] = []
	for entry in parsed.entries[:max_items]:
		title = getattr(entry, "title", "Untitled")
		link = getattr(entry, "link", url)
		summary = getattr(entry, "summary", getattr(entry, "description", ""))
		published = getattr(entry, "published", getattr(entry, "updated", datetime.now()))
		items.append(
			AggregatedItem(
				title=title,
				url=link,
				summary=summary,
				published_at=_parse_datetime(published),
				source=url,
			)
		)
	return items


def aggregate_feeds(urls: Iterable[str], max_items_per_feed: int = 5) -> List[AggregatedItem]:
	seen_links: set[str] = set()
	collected: List[AggregatedItem] = []
	for url in urls:
		try:
			items = fetch_feed(url, max_items=max_items_per_feed)
			for item in items:
				if item.url in seen_links:
					continue
				seen_links.add(item.url)
				collected.append(item)
		except Exception:
			# Skip problematic feeds but continue others
			continue
	# Sort by published desc
	collected.sort(key=lambda i: i.published_at, reverse=True)
	return collected


def offline_items() -> List[AggregatedItem]:
	# Deterministic offline items for testing and airgapped environments
	base_time = datetime(2024, 4, 20, 16, 20, tzinfo=timezone.utc)
	return [
		AggregatedItem(
			title=f"Sample cannabis news {i}",
			url=f"https://example.com/news/{i}",
			summary="This is a placeholder summary for offline mode.",
			published_at=base_time,
			source="offline",
		)
		for i in range(1, 6)
	]

