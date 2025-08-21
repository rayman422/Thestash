from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import List


def generate_rss(site_name: str, base_url: str, posts: List[dict], output_dir: str) -> None:
	if not base_url:
		base_url = "http://localhost"
	items_xml = []
	for p in posts:
		items_xml.append(
			f"<item><title>{escape_xml(p['title'])}</title><link>{base_url}/{p['url']}</link><guid>{base_url}/{p['url']}</guid><pubDate>{rfc822(p['created_at'])}</pubDate></item>"
		)
	xml = (
		"<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
		f"<rss version=\"2.0\"><channel><title>{escape_xml(site_name)}</title><link>{base_url}/</link><description>{escape_xml(site_name)} feed</description>"
		+ "".join(items_xml)
		+ "</channel></rss>"
	)
	Path(output_dir, "feed.xml").write_text(xml, encoding="utf-8")


def generate_sitemap(base_url: str, posts: List[dict], output_dir: str) -> None:
	if not base_url:
		base_url = "http://localhost"
	urls = [f"<url><loc>{base_url}/</loc></url>"]
	for p in posts:
		urls.append(f"<url><loc>{base_url}/{p['url']}</loc></url>")
	xml = (
		"<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
		"<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">"
		+ "".join(urls)
		+ "</urlset>"
	)
	Path(output_dir, "sitemap.xml").write_text(xml, encoding="utf-8")


def generate_robots(base_url: str, output_dir: str) -> None:
	lines = [
		"User-agent: *",
		"Allow: /",
		f"Sitemap: {base_url or 'http://localhost'}/sitemap.xml",
	]
	Path(output_dir, "robots.txt").write_text("\n".join(lines), encoding="utf-8")


def escape_xml(s: str) -> str:
	return (
		s.replace("&", "&amp;")
		.replace("<", "&lt;")
		.replace(">", "&gt;")
		.replace("\"", "&quot;")
		.replace("'", "&apos;")
	)


def rfc822(iso: str) -> str:
	try:
		dt = datetime.fromisoformat(iso)
	except Exception:
		dt = datetime.utcnow()
	return dt.strftime("%a, %d %b %Y %H:%M:%S GMT")

