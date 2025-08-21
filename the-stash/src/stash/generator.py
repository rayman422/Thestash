from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import List

from .aggregator import AggregatedItem

LOGGER = logging.getLogger(__name__)


def _compose_prompt(site_name: str, items: List[AggregatedItem], max_words: int) -> str:
	bullet_lines: List[str] = []
	news = [it for it in items if getattr(it, "category", "news") == "news"]
	strains = [it for it in items if getattr(it, "category", "news") == "strain"]
	ordered = news[:8] + strains[:4]
	for it in ordered[:12]:
		date_str = it.published.isoformat() if it.published else "unknown"
		bullet_lines.append(
			f"- {it.title} — {it.source} ({date_str})\n  {it.summary[:320]}\n  {it.url}"
		)
	bullets = "\n".join(bullet_lines)
	return (
		f"You are a cannabis culture editor for a blog called '{site_name}'. "
		f"Write a fun but informative roundup article (max {max_words} words) summarizing key news and new strains. "
		"Keep it light, avoid medical or legal advice. Provide a catchy title, 3-6 short sections with subheadings, and a brief closing. "
		"Include links inline when relevant using Markdown [text](url). Avoid lists of links; weave them into sentences."
		"\n\nItems:\n" + bullets
	)


def generate_with_openai(model: str, prompt: str) -> str:
	from openai import OpenAI

	api_key = os.getenv("OPENAI_API_KEY")
	if not api_key:
		raise RuntimeError("OPENAI_API_KEY not set")
	client = OpenAI(api_key=api_key)
	resp = client.chat.completions.create(
		model=model,
		messages=[
			{"role": "system", "content": "You write engaging, concise cannabis blog posts."},
			{"role": "user", "content": prompt},
		],
		temperature=0.8,
		max_tokens=900,
	)
	return resp.choices[0].message.content.strip()


def generate_with_ollama(model: str, prompt: str, base_url: str = "http://localhost:11434") -> str:
	import requests
	resp = requests.post(
		f"{base_url}/api/generate",
		json={"model": model, "prompt": prompt, "stream": False, "options": {"temperature": 0.8}},
		timeout=120,
	)
	resp.raise_for_status()
	data = resp.json()
	text = data.get("response") or data.get("message") or ""
	return (text or "").strip()


def fallback_generate(items: List[AggregatedItem], max_words: int) -> str:
	sections: List[str] = []
	sections.append("# The Stash Roundup")
	sections.append("A quick mellow tour of what's burning today:")
	for it in items[:6]:
		sections.append(f"## {it.title}\n{it.summary}\n[Read more]({it.url})")
	sections.append("Thanks for stopping by The Stash. Stay lifted and informed.")
	return "\n\n".join(sections)[: max_words * 6]


def generate_post(site_name: str, items: List[AggregatedItem], model: str, max_words: int, use_openai: bool, provider: str = "ollama", ollama_base_url: str = "http://localhost:11434", openai_model: str | None = None) -> str:
	prompt = _compose_prompt(site_name, items, max_words)
	if provider == "openai" or use_openai:
		try:
			return generate_with_openai(openai_model or model, prompt)
		except Exception as exc:
			LOGGER.warning("OpenAI generation failed, falling back: %s", exc)
	elif provider == "ollama":
		try:
			return generate_with_ollama(model, prompt, base_url=ollama_base_url)
		except Exception as exc:
			LOGGER.warning("Ollama generation failed, falling back: %s", exc)
	return fallback_generate(items, max_words)

