import os
import shutil
from pathlib import Path

import pytest

from stash.config import load_config_from_env
from stash.main import run_publish


def setup_module(module):
	# Ensure clean site and content directories for test isolation
	root = Path(__file__).resolve().parents[1]
	for sub in ["site", "content/posts"]:
		p = root / sub
		if p.exists():
			shutil.rmtree(p)


def test_offline_publish(tmp_path, monkeypatch):
	monkeypatch.setenv("STASH_OFFLINE", "1")
	cfg = load_config_from_env()
	run_publish(cfg, provider="none", model=None, no_ai=True, offline=True)

	site_dir = Path(__file__).resolve().parents[1] / "site"
	index_html = site_dir / "index.html"
	assert index_html.exists()

	posts_dir = site_dir / "posts"
	assert any(p.suffix == ".html" for p in posts_dir.glob("*.html"))