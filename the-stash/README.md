## The Stash — THC Blog with AI Autoposts (Rewritten)

This is a clean rewrite of The Stash: a minimal static blog that aggregates cannabis news and optionally uses an LLM to generate a short post. It can run entirely offline with a deterministic fallback.

### Features
- Aggregates news from configurable RSS feeds
- Optional AI post generation via OpenAI or Ollama
- Offline deterministic fallback (no network, no API keys)
- Static HTML site generation via Jinja2 templates
- Scheduler to auto-publish at 4:20 AM and 4:20 PM

### Layout
```
 the-stash/
   src/stash/
     __init__.py
     config.py
     aggregator.py
     generator.py
     builder.py
     scheduler.py
     main.py
   templates/
     base.html
     post.html
     index.html
   public/
     css/styles.css
   site/                # build output
   content/             # generated markdown + metadata
   requirements.txt
   run_scheduler.py
   README.md
```

### Requirements
- Python 3.10+

### Setup
Option A: Install dependencies to user site-packages (no venv):
```bash
python3 -m pip install --user --break-system-packages -r the-stash/requirements.txt
```

Option B: Use a venv (if system has python3-venv installed):
```bash
cd the-stash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Optional: Enable OpenAI
```bash
export OPENAI_API_KEY=your_key
export STASH_PROVIDER=openai
export STASH_MODEL=gpt-4o-mini
```

Optional: Use Ollama
```bash
# Install Ollama from https://ollama.com and pull a model
ollama pull llama3.2:3b
export STASH_PROVIDER=ollama
export STASH_MODEL=llama3.2:3b
```

Base URL (for GitHub Pages or subpath hosting):
```bash
export BASE_URL="/your-subpath"
```

### One-off publish (offline, no AI)
```bash
PYTHONPATH=the-stash/src python3 -m stash.main publish --offline --no-ai
```
Output will be in `the-stash/site/`.

### Scheduler
Run a blocking scheduler to publish at 4:20 AM/PM in your timezone:
```bash
export STASH_TIMEZONE="America/Los_Angeles"  # optional, defaults to UTC
PYTHONPATH=the-stash/src python3 the-stash/run_scheduler.py
```

### Development
- Rebuild index from existing content: `PYTHONPATH=the-stash/src python3 -m stash.main build`
- Run tests: `cd the-stash && PYTHONPATH=src python3 -m pytest -q`

### Notes
- If no provider is configured, the generator uses the offline fallback.
- Feeds are set in `src/stash/config.py` or via `STASH_FEEDS` env var.


