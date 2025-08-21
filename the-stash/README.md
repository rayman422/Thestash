## The Stash — THC Blog with AI Autoposts

The Stash is a minimal static blog that auto-aggregates cannabis news and strain updates, then generates a custom AI blog post at 4:20 AM and 4:20 PM daily.

### Features
- Aggregates news from configurable RSS feeds
- Optional strain update sources
- AI-written posts using OpenAI (with a no-AI fallback)
- Static HTML output with simple styling
- Scheduler: run via cron or built-in APScheduler

### Project Layout
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
  site/                 # build output
  content/              # generated markdown and metadata
  requirements.txt
  run_scheduler.py
  README.md
```

### Prerequisites
- Python 3.10+

### Setup
```bash
cd the-stash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Optionally set your OpenAI API key for higher-quality AI posts:
```bash
export OPENAI_API_KEY=your_key_here
```

### Usage

Fetch news, generate a post, and build the site (one-off):
```bash
PYTHONPATH=src python3 -m stash.main publish
```

Run the continuous scheduler (4:20 AM/PM):
```bash
PYTHONPATH=src python3 run_scheduler.py
```

Or configure cron (preferred for servers):
```bash
crontab -e
# Add two lines (adjust paths):
20 4 * * *  cd /workspace/the-stash && PYTHONPATH=src .venv/bin/python -m stash.main publish >> /workspace/the-stash/cron.log 2>&1
20 16 * * * cd /workspace/the-stash && PYTHONPATH=src .venv/bin/python -m stash.main publish >> /workspace/the-stash/cron.log 2>&1
```

### Configuration
Edit `src/stash/config.py` to adjust:
- Feed URLs
- Number of items to aggregate
- Model name
- Site metadata

### Development
Generate a local test post without OpenAI:
```bash
PYTHONPATH=src python3 -m stash.main publish --no-ai
```

Serve the built site with any static server, e.g.:
```bash
python3 -m http.server --directory site 8080
```

### Notes
- The fallback generator uses extractive summaries if OpenAI is not configured.
- Feeds and external sites can change; adjust sources as needed.

