from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

import requests

from .aggregator import AggregatedItem
from .config import AppConfig


@dataclass
class GeneratedPost:
	title: str
	slug: str
	markdown: str
	created_at: datetime


def _slugify(text: str) -> str:
	text = text.lower()
	text = re.sub(r"[^a-z0-9\s-]", "", text)
	text = re.sub(r"[\s-]+", "-", text).strip("-")
	return text or "post"


def _format_prompt(items: List[AggregatedItem]) -> str:
	bullet_points = "\n".join([f"- {it.title} — {it.url}" for it in items[:8]])
	return (
		"You are a cannabis news blogger. Write a concise, engaging blog post summarizing "
		"today's most interesting cannabis stories. Avoid sensationalism, keep it factual, "
		"and add a short intro and outro. Include links inline in markdown.\n\n"
		f"Source items:\n{bullet_points}\n\n"
		"Output markdown only, no front matter."
	)


def _openai_generate(prompt: str, model: str, api_key: str) -> Optional[str]:
	try:
		from openai import OpenAI
		client = OpenAI(api_key=api_key)
		resp = client.chat.completions.create(
			model=model,
			messages=[
				{"role": "system", "content": "You write high-quality blog posts in Markdown."},
				{"role": "user", "content": prompt},
			],
			temperature=0.7,
			max_tokens=900,
		)
		return resp.choices[0].message.content or None
	except Exception:
		return None


def _ollama_generate(prompt: str, model: str) -> Optional[str]:
	try:
		resp = requests.post(
			"http://localhost:11434/api/generate",
			json={"model": model, "prompt": prompt, "stream": False},
			timeout=60,
		)
		resp.raise_for_status()
		data = resp.json()
		text = data.get("response") or data.get("text")
		return text
	except Exception:
		return None


def _fallback_generate(items: List[AggregatedItem]) -> str:
	lines = ["# Today's Cannabis Roundup", ""]
	lines.append("Highlights:")
	for it in items[:10]:
		lines.append(f"- [{it.title}]({it.url})")
	lines.append("")
	lines.append("Quick take:")
	lines.append(
		"The cannabis landscape continues to evolve. Here's a concise look at what changed "
		"today across policy, products, and culture."
	)
	return "\n".join(lines)


def generate_post(items: List[AggregatedItem], config: AppConfig) -> GeneratedPost:
	created = datetime.now(tz=timezone.utc)
	title_date = created.astimezone().strftime("%b %-d, %Y") if hasattr(created, "astimezone") else created.strftime("%b %d, %Y")
	title = f"The Stash — Cannabis News for {title_date}"
	prompt = _format_prompt(items)

	markdown: Optional[str] = None
	if config.model.provider == "openai" and config.model.openai_api_key:
		markdown = _openai_generate(prompt, config.model.model_name, config.model.openai_api_key)
	elif config.model.provider == "ollama":
		markdown = _ollama_generate(prompt, config.model.model_name)

	if not markdown:
		markdown = _fallback_generate(items)

	slug = _slugify(title)
	return GeneratedPost(title=title, slug=slug, markdown=markdown, created_at=created)

